bl_info = {
    "name": "Watch and Run",
    "author": "xixixao",
    "version": (0, 1),
    "blender": (3, 3, 0),
    "location": "Scripting -> Text -> Watch and Run",
    "description": (
        "File watcher addon. Edit files in an external editor,"
        " save the files and see results instantly inside Blender."
    ),
    "doc_url": "https://github.com/xixixao/blender_watch_and_run",
    "tracker_url": "https://github.com/xixixao/blender_watch_and_run/issues",
    "category": "Text",
}

import sys
import os
import importlib
import asyncio
import threading
import atexit
import traceback
import bpy
import watchfiles

# Events are used for synchronizing with the background thread
# which does the watching
stop_event = asyncio.Event()
run_event = asyncio.Event()

# The name of the `Text` which the watched path gets written to for peristence
text_name = "__watch_and_run__"


def register():
    bpy.utils.register_class(WatchAndRunOperator)
    bpy.utils.register_class(StopWatchingOperator)
    add_to_text_menu(operator_menu_items)
    register_file_load_handler(watch_and_run_on_load)
    register_blender_exit_handler(stop_watching)


def unregister():
    stop_watching()
    remove_from_text_menu(operator_menu_items)
    bpy.utils.unregister_class(StopWatchingOperator)
    bpy.utils.unregister_class(WatchAndRunOperator)


def add_to_text_menu(menu_items):
    bpy.types.TEXT_MT_text.append(menu_items)


def remove_from_text_menu(menu_items):
    bpy.types.TEXT_MT_text.remove(menu_items)


def operator_menu_items(self, _context):
    self.layout.separator()
    self.layout.operator(WatchAndRunOperator.bl_idname)
    self.layout.operator(StopWatchingOperator.bl_idname)


def register_file_load_handler(handler):
    bpy.app.handlers.load_post.append(handler)


def register_blender_exit_handler(handler):
    atexit.register(handler)


class WatchAndRunOperator(bpy.types.Operator):
    """Execute a module file whenever it changes"""

    bl_idname = "text.watch_and_run"
    bl_label = "Watch and Run"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    _timer = None

    def invoke(self, context, _event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        stop_watching()
        save_watched_path(self.filepath)
        start_watching()
        run_event.set()
        self.start_timer(context)
        return {"RUNNING_MODAL"}

    def start_timer(self, context):
        window_manager = context.window_manager
        self._timer = window_manager.event_timer_add(
            0.05, window=context.window
        )
        window_manager.modal_handler_add(self)

    def modal(self, context, event):
        if stop_event.is_set():
            self.cancel(context)
            return {"CANCELLED"}

        if event.type == "TIMER":
            if run_event.is_set():
                run_watched_module()
                run_event.clear()

        return {"PASS_THROUGH"}

    def cancel(self, context):
        context.window_manager.event_timer_remove(self._timer)


class StopWatchingOperator(bpy.types.Operator):
    """Stop watching and executing the previously selected module"""

    bl_idname = "text.stop_watching"
    bl_label = "Stop Watching"

    def execute(self, _context):
        stop_watching()
        delete_watched_path()
        return {"FINISHED"}


def run_watched_module():
    try:
        path = read_watched_path()
        run_from_path(path)
    except BaseException as error:
        log("Error while running chosen module")
        traceback.print_exception(error)


@bpy.app.handlers.persistent
def watch_and_run_on_load(_):
    path = maybe_read_watched_path()
    if path is None:
        return
    log("Starting watching on Blend file load")
    bpy.ops.text.watch_and_run(filepath=path)


def save_watched_path(path):
    if text_name not in bpy.data.texts.keys():
        bpy.data.texts.new(text_name)
    bpy.data.texts[text_name].from_string(path)


def read_watched_path():
    string = maybe_read_watched_path()
    assert string is not None, "Expected path to be stored in a Text object"
    return string


def maybe_read_watched_path():
    text = bpy.data.texts.get(text_name)
    if text is None:
        return None
    return text.as_string()


def delete_watched_path():
    text = bpy.data.texts[text_name]
    if text is not None:
        bpy.data.texts.remove(text)


def start_watching():
    stop_event.clear()
    thread = threading.Thread(target=watcher)
    thread.start()


def stop_watching():
    stop_event.set()


def watcher():
    path = read_watched_path()
    directory_path = os.path.dirname(path)
    log("Started watching", directory_path)
    for _ in watchfiles.watch(
        directory_path, watch_filter=WatchFilter(), stop_event=stop_event
    ):
        run_event.set()
    log("Stopped watching", directory_path)


def run_from_path(run_path):
    ## Determine which paths we're working with
    directory_path = os.path.dirname(run_path)
    is_package = os.path.isfile(os.path.join(directory_path, "__init__.py"))
    leaf_module_name = os.path.basename(os.path.splitext(run_path)[0])
    if not is_package:
        module_directory_path = directory_path
        module_name = leaf_module_name
    else:
        module_directory_path = os.path.dirname(directory_path)
        package_name = os.path.basename(directory_path)
        module_name = package_name + "." + leaf_module_name

    if module_directory_path not in sys.path:
        sys.path.append(module_directory_path)
        log("Registered", module_directory_path)

    ## Remove the previously loaded modules
    previously_loaded_modules = []
    for module in sys.modules.values():
        if hasattr(module, "__file__"):
            source_path = module.__file__
            if type(source_path) == str and is_in_directory(
                directory_path, source_path
            ):
                previously_loaded_modules.append(module.__name__)
    for loaded_module_name in previously_loaded_modules:
        sys.modules.pop(loaded_module_name, None)
    log("Reset", previously_loaded_modules)

    ## Load the given module
    log("Loading", module_name)
    module = importlib.import_module(module_name)

    ## Run `main()` if present
    if hasattr(module, "main") and callable(module.main):
        log("Running `main` of", module_name)
        module.main()


def is_in_directory(directory_path, path):
    return path.startswith(directory_path + os.sep)


class WatchFilter(watchfiles.DefaultFilter):
    def __init__(self):
        super().__init__(
            ignore_entity_patterns=watchfiles.DefaultFilter.ignore_entity_patterns
            + (".tmp$",)
        )


def log(*args):
    print("WATCH AND RUN:", *args)


if __name__ == "__main__":
    register()
