# Blender "Watch And Run" Add-on

File watcher addon for Blender. Edit files in an external editor, save the files and see results instantly inside Blender.

## Installation

1. Install Python module `watchfiles`

   - on MacOS: `/Applications/Blender.app/Contents/Resources/3.3/python/bin/python3.10 -m pip install watchfiles`
   - _TODO: instructions for other OSs_
   - _TODO: include the pip install inside the addon itself_

2. Download `external_live_edit.py`
3. Add it as addon in Blender

## Usage

1. Execute "Watch And Run" operator

   - in the `Scripting` workspace -> in the `Text` menu -> click on `Watch and Run` menu item
   - via Search (`F3` shortcut), type `Watch and Run`

2. A file path selector will appear
3. Choose the file with the Python module you want to run. If it has a `main` function it will be called after the module is loaded.

The module will then be reloaded and reexecuted every time any file changes in the file's parent folder (or any of its subfolders).

To disable the watching run the `Stop Watching` operator, which you will find in the `Text` menu or via Search.

### Working with multiple files

You can use a folder with multiple modules to split your script.

Folder structure:

```
/script/
  ├── foo.py
  └── another.py
```

Choose `/script/foo.py` which contains:

```py
import another
```

---

If you want nested folders for more structure, or if you want to avoid shadowing builtin modules, you can use a package.

```
/script/
  ├── __init__.py
  ├── foo.py
  └── another/
        ├── __init__.py
        └── bar.py
```

And in `/script/foo.py`:

```py
import script.another.bar
# Or using relative paths
from .another import bar
```

### Gotchas

1. Only modules declared in files inside the the parent folder of the chosen file will be reloaded. Any other modules will not be reloaded. You will have to restart Blender to update them.

## Contributions

Contributions are welcome for any issue or to implement the `TODO`s called out above.

### Under the Hood

There are a few tricks to get this functionality working correctly and efficiently:

1. `watchfiles` is used in a background thread to watch for file changes
2. The `Watch and Run` operator is a modal operator which gets run every 50ms and checks an `asyncio.Event` for whether the chosen module should be run
3. Running the module entails making sure its directory is in `sys.path` and removing all the modules from the directory so that they get rerun correctly
4. The chosen path is written to a Blender `Text` so that it is saved in the `.blend` file and watch can be automatically restarted when you open the `.blend` file
5. The background thread must be killed before exiting Blender otherwise Blender never quits
