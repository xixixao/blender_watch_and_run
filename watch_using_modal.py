# import bpy

# import asyncio
# from watchfiles import awatch

import bpy
import asyncio

# import watchfiles
import threading

# Used for synchronizing with the background thread which does the watching
stop_event = asyncio.Event()


def register():
    bpy.utils.register_class(ExternalLiveEditOperator)
    bpy.types.TOPBAR_MT_file_external_data.append(add_external_live_edit_operator)


def unregister():
    stop_watching()
    bpy.utils.register_class(ExternalLiveEditOperator)


def add_external_live_edit_operator(self, _context):
    self.layout.separator()
    self.layout.operator(ExternalLiveEditOperator.bl_idname)


class ExternalLiveEditOperator(bpy.types.Operator):
    """Execute a script file whenever it changes"""

    bl_idname = "object.external_live_edit"
    bl_label = "External Live Edit"
    # bl_options = {"REGISTER", "UNDO"}

    # START: The Operator paramaters shown in the popup

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    watch_path: bpy.props.StringProperty(
        name="Folder to Watch",
        description="Path to the folder containing the files to import",
        default="",
        subtype="DIR_PATH",
    )

    run_path: bpy.props.StringProperty(
        name="Script to Run",
        description="Path to the folder containing the files to import",
        default="",
        subtype="FILE_PATH",
    )

    should_watch: bpy.props.BoolProperty(
        name="Watch",
        description="Path to the folder containing the files to import",
    )

    # END: The Operator paramaters shown in the popup

    def invoke(self, context, event):
        # context.window_manager.invoke_props_modal(self, width=500)
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, _context):
        print(self.filepath)
        if self.should_watch:
            start_watching(self)
        else:
            stop_watching()
        return {"FINISHED"}

    # def paths(self):
    #     return {"watch_path": self.watch_path, "run_path": self.run_path}


def start_watching(*args):
    stop_event.clear()
    thread = threading.Thread(target=watcher, args=args)
    thread.start()


def stop_watching():
    stop_event.set()


def watcher(*args):
    asyncio.run(watcher_main(*args))


async def watcher_main(operator):
    # paths = operator.paths()
    print("Starting watching", operator.watch_path)
    async for _ in watchfiles.awatch(paths.watch_path, stop_event=stop_event):
        print("Now I would rerun the script")
    print("Stopped watching", operator.watch_path)


register()

# #bpy.types.Scene.externalLiveEditWatchPath = bpy.props.StringProperty(
# #    name = "Folder to Watch",
# #    description = "Path to the folder containing the files to import",
# #    default = "",
# #    subtype = 'DIR_PATH'
# #);


# #bpy.types.Scene.externalLiveEditScriptPath = bpy.props.StringProperty(
# #    name = "Script to Run",
# #    description = "Path to the folder containing the files to import",
# #    default = "",
# #    subtype = 'FILE_PATH'
# #);


# #bpy.types.Scene.externalLiveEditIsWatching = bpy.props.BoolProperty(
# #    name = "Watch",
# #    description = "Path to the folder containing the files to import",
# #);


# #bpy.utils.unregister_class(ObjectCursorArray)
# #bpy.utils.unregister_class(OBJECT_PT_property_example)
# bpy.utils.register_class(ObjectCursorArray)
# bpy.utils.register_class(OBJECT_PT_property_example)
# bpy.utils.register_class(ExternalLiveEditOperator)


# #bpy.types.TEXT_MT_text.append(activate_external_live_edit)
# #bpy.types.VIEW3D_MT_object.append(menu_func)


# from typing import Dict, ClassVar, get_type_hints
# import asyncio
# from watchfiles import awatch

# # async def main():
# #     async for changes in awatch('./test'):
# #         print(changes)

# # asyncio.run(main())

# class Foo:
#   a: 3
#   a = 4

# print(Foo())
# print(get_type_hints(Foo))


# # bl_info = {
# #     "name": "2Blender",
# #     "author": "xixixao",
# #     "version": (1, 0),
# #     "blender": (3, 3, 0),
# #     "location": "World > Watch",
# #     "description": "Watch files for code changes to reload.",
# #     "warning": "",
# #     "wiki_url": "",
# #     "category": "Tools",
# # }

# # import bpy
# # import socket as socket
# # import sys
# # import os

# # import threading
# # import time

# # import addon_utils
# # import imp


# # class ToBlender(object):
# #     """ Threading example class

# #     The run() method will be started and it will run in the background
# #     until the application exits.
# #     """

# #     def __init__(self, interval=1):
# #         """ Constructor

# #         :type interval: int
# #         :param interval: Check interval, in seconds
# #         """
# #         self.interval = interval
# #         self.running = True
# #         self.thread = threading.Thread(target=self.run, args=())
# #         self.thread.daemon = True                            # Daemonize thread
# #         self.thread.start()                                  # Start the execution

# #     def processRemoteCommand(self, cmd):
# #         exists = os.path.isfile(cmd)
# #         if exists:
# #             dir = os.path.dirname(cmd)
# #             if dir not in sys.path:
# #                 sys.path.append(dir)
# #             module = os.path.basename(os.path.splitext(cmd)[0])
# #             sys.modules.pop(module, None)
# #             __import__(module).main()
# #             # print ('try execute "' + cmd + '"')
# #             #exec(compile(open(cmd).read(), cmd, 'exec'))
# #             return True
# #         else:
# #             addonName = cmd
# #             print ('try restart "' + addonName + '"')
# #             addon_utils.disable(addonName)
# #             addon_utils.enable(addonName)
# #             return True

# #         print ('no command given')
# #         return False

# #     def run(self):
# #         """ Method that runs forever """
# #         # Create a TCP/IP socket
# #         self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# #         self.server_address = ('localhost', 3001)
# #         self.socket.settimeout(1)
# #         print ('starting up on %s port %s' % self.server_address)
# #         self.socket.bind(self.server_address)

# #         # Listen for incoming connections
# #         self.socket.listen(1)

# #         print ('waiting for a connection that informs about code changes...')
# #         while self.running:
# #             try:
# #                 connection, client_address = self.socket.accept()
# #             except socket.timeout:
# #                 if (self.running):
# #                     continue
# #                 else:
# #                     break

# #             print (client_address)
# #             try:
# #                 print ('client connected:', client_address)
# #                 while self.running:
# #                     try:
# #                         data = connection.recv(4096)
# #                         dataString = data.decode("utf-8")
# #                         if(dataString != None and dataString != ""):
# #                             print ('received command "%s"' % data)
# #                             self.processRemoteCommand(dataString)
# #                         connection.sendall(("processed \"" + dataString  + "\"").encode())
# #                     except Exception as e:
# #                         try:
# #                             connection.sendall(str(e).encode())
# #                             print(e)
# #                         except:
# #                             pass
# #                         break
# #             finally:
# #                 connection.close()
# #                 time.sleep(self.interval)
# #         print ('server stopped')

# #     def stop(self):
# #         self.running = False

# #     def __del__(self):
# #         self.stop()

# # server = None

# # def register():
# #     global server
# #     server = ToBlender()

# # def unregister():
# #     global server
# #     print('stopping server...')
# #     server.stop()
# #     del server

# # if __name__ == "__main__":
# #    register()


# async def main():
#     stop_event = asyncio.Event()

#     async def stop_soon():
#         await asyncio.sleep(3)
#         stop_event.set()

#     stop_soon_task = asyncio.create_task(stop_soon())

#     async for changes in awatch('./test', stop_event=stop_event):
#         print(changes)

#     # cleanup by awaiting the (now complete) stop_soon_task
#     await stop_soon_task

# asyncio.run(main())


# def main():
#   asyncio.run(scenario())

# async def scenario():
#   start_watching('./test')
#   await asyncio.sleep(3)
#   stop_watching()
#   await asyncio.sleep(2)
#   start_watching('./test')
#   await asyncio.sleep(3)
#   stop_watching()
