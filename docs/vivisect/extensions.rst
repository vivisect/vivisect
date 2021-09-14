Extending Vivisect / Vdb
########################

Vivisect allows you to extend it's functionality through the use of Vivisect Extensions.  Extensions are loaded with the GUI, and they give nearly complete access to the entire Vivisect Workspace and GUI.

Extensions are Python modules loaded from directories contained in the `VIV_EXT_PATH` environment variable.  Like DOS or Unix paths, this is a set of directories separated by the OS-specific separator (Windows=';', Unix=':').

Like all Python modules, they can be either a `<modulename>.py` file or a directory with a `__init__.py` file inside it.  Each module will be loaded into the namespace and the `vivExtension(vw, vwgui)` function executed (for Vdb, the `vdbExtension(vdb, vdbgui)` function will be executed).  It is up to the module to make any modifications (adding menu entries or toolbars, hooking the context menu, etc) within this function.  Submodules may be included in the directory- version of the extensions, and may be accessed with `from . import <blah>`.

In addition to your private zero-day finding extensions, outside plugins may be wrapped into Vivisect by simply copying/symlinking them into one of your extension directories (listed in the `VIV_EXT_PATH`).

If no `VIV_EXT_PATH` environment variable has been defined, Vivisect will look for extensions in `$HOME/.viv/plugins/` if it exists.  If `VIV_EXT_PATH` is defined, you much choose to add `$HOME/.viv/plugins/` to it or not.  It will not be checked unless it is explicitly listed in `VIV_EXT_PATH`.

For examples of using this powerful capability, look at the example file at: `vivisect/extensions/example_gui_extension.py`
