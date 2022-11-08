# Blender External Live Edit

File watcher addon for Blender. Edit files in an external editor, save and see results instantly inside Blender.

## Installation

1. Install Python module `watchfiles`

   - on MacOS: `/Applications/Blender.app/Contents/Resources/3.3/python/bin/python3.10 -m pip install watchfiles`
   - _TODO: instructions for other OSs_
   - _TODO: include the pip install inside the addon itself_

2. Download `external_live_edit.py`
3. Add it as addon in Blender

## Usage

1. Execute External Live Edit

   - via `File` -> `External Data` -> `External Live Edit` menu item
   - via Search (`F3` shortcut), type `External Live Edit`

2. A popup will appear
3. Choose the `Folder to Watch`. Any file change in this folder will trigger the execution of the script.
4. Choose the `Script to Run`. This should be a Python module which is an entry point for your script. If it has a `main` function this will be run.
5. Toggle `Watch` to checked.

The script will be run for the first time after you click outside the popup to close it. The script will then be run every time any file changes in the selected folder (or any subfolder).

To disable the watching run the `External Live Edit` operator again and uncheck the `Watch` checkbox.

### Working with multiple files

You can use a folder with multiple modules to split your script.

`Folder to Watch`: `'/script/'`
`Script to Run`: `'/script/foo.py'`

Folder structure:

```
/script/
  ├── foo.py
  └── another.py
```

And in `/script/foo.py`:

```py
import another
```

If you want nested folders for more structure, or if you want to avoid shadowing builtin modules, you can use a package.

`Folder to Watch`: `'/script/'`
`Script to Run`: `'/script/__main__.py'`

```
/script/
  ├── __init__.py
  ├── __main__.py
  └── another/
        ├── __init__.py
        └── foo.py
```

And in `/script/__main__.py`:

```py
import script.another
import script.another.foo
# Or using relative paths
from .another import foo
```

_TODO: Support running other modules from a package?_

### Gotchas

1. Only modules declared in files inside the `Folder to Watch` or the parent folder of the `Script to Run` will be reloaded. Any other modules will not be reloaded. You will have to restart Blender to update them.

## Contributions

Contributions are welcome for any issue or to implement the `TODO`s called out above.
