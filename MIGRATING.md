# Migrating to Python3

So vivisect recently went from python2 to python3. Luckily, most APIs have stayed
relatively the same. There are a couple APIs (such as read/write memory) where the
inputs/outputs have changed, but for the most part, the APIs have very similar
structure to what they had before. Beyond that though, perhaps the biggest hurdle
for upgrading from python2 to python3 are any pre-existing workspaces.

# Migrating from PyQt5 to PyQt6

The GUI has been updated from PyQt5 to PyQt6. This section documents the changes
for extension authors and downstream users.

## Dependency Changes

- `pyqt5==5.15.7` → `pyqt6>=6.5.0`
- `pyqtwebengine==5.15.6` → `pyqt6-webengine>=6.5.0`

## Key API Changes

### Import Changes

- All `from PyQt5` imports are now `from PyQt6`
- `QAction` and `QShortcut` moved from `QtWidgets` to `QtGui`:
  ```python
  # Old
  from PyQt5.QtWidgets import QAction, QShortcut
  # New
  from PyQt6.QtGui import QAction, QShortcut
  ```
- `QWebEnginePage` moved from `QtWebEngineWidgets` to `QtWebEngineCore`:
  ```python
  # Old
  from PyQt5.QtWebEngineWidgets import QWebEnginePage
  # New
  from PyQt6.QtWebEngineCore import QWebEnginePage
  ```
- `QRegExpValidator` → `QRegularExpressionValidator` (from `QtGui`)
- `QtCore.QRegExp` → `QtCore.QRegularExpression`

### Scoped Enums (Major Change)

PyQt6 requires fully-qualified enum values. Examples:

| PyQt5 | PyQt6 |
|-------|-------|
| `Qt.Horizontal` | `Qt.Orientation.Horizontal` |
| `Qt.DisplayRole` | `Qt.ItemDataRole.DisplayRole` |
| `Qt.ItemIsEditable` | `Qt.ItemFlag.ItemIsEditable` |
| `Qt.AlignLeft` | `Qt.AlignmentFlag.AlignLeft` |
| `Qt.TopDockWidgetArea` | `Qt.DockWidgetArea.TopDockWidgetArea` |
| `Qt.AscendingOrder` | `Qt.SortOrder.AscendingOrder` |
| `Qt.ShiftModifier` | `Qt.KeyboardModifier.ShiftModifier` |
| `Qt.LeftButton` | `Qt.MouseButton.LeftButton` |
| `QMessageBox.Ok` | `QMessageBox.StandardButton.Ok` |
| `QFont.Normal` | `QFont.Weight.Normal` |

### Method Changes

- `exec_()` → `exec()` (on QDialog, QMenu, QApplication, QMessageBox)
- `event.globalPos()` → `event.globalPosition().toPoint()`
- `event.globalX()`/`globalY()` → `int(event.globalPosition().x())`/`y()`
- `QShortcut` context integer → `Qt.ShortcutContext` enum

### Signal Changes

- `currentIndexChanged['QString']` → `currentTextChanged` (for string-valued signals)

## Existing workspaces

Workspaces saved via the basicfile format won't migrate cleanly. Basicfile is backed
by python's pickle, so having it work across python2 and python3 is...tricky. Not
impossible, but in order to maintain backwards compatibility, while still providing
an upgrade path, there's another storage module (vivisect.storage.mpfile) that is 
msgpack based which, and works across python versions. To further help with migration,
there's the `vivisect.storage.tools.convert` module that can convert from one storage
format to the other. The conversion module exists in both the latest python2 release
(0.2.1) as well as the upcoming 1.0.1 release, in case another major need of it arises.

But to convert a single workspace from basicfile to mpfile:
```
python2 -m vivisect.storage.tools.convert <basicfile_workspace>
```
Which will then produce a `<workspace>.mpviv` file that should be loadable in python2 and python3.

The opposite also works, so you can run:
```
python2 -m vivisect.storage.tools.convert <mpfile_workspace>
```
To produce a basicfile-based workspace.

Please note that since we don't want to accidentally overwrite any files, the `.viv`
or `.mpviv` extensions that the conversion tool do not replace any other extensions,
so if you run the conversion tool on `foo.viv`, you'll end up with `foo.viv.mpviv`.
If this is not the behavior you want, you can supply the `--name` parameter to the tool
to specify the name for the new workspace like so:
```
python2 -m vivisect.storage.tools.convert <workspace> --name <my_new_worksapce_name>
```
