import sys
import os
import importlib
import bpy


def log(*args):
    first_arg = args[0]
    if type(first_arg).__base__ == bpy.types.Operator:
        first_arg.report({"INFO"}, *args[1:])
    else:
        print("LIVE EDIT:", *args)


def main():
    run_path = "/Users/srb/Work/Blender/Scripting/src/test.py"
    watch_path = "/Users/srb/Work/Blender/Scripting/src/"

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
            if type(source_path) == str and (
                (is_in_directory(watch_path, source_path))
                or (is_in_directory(directory_path, source_path))
            ):
                previously_loaded_modules.append(module.__name__)
    for module_name in previously_loaded_modules:
        sys.modules.pop(module_name, None)
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


main()
