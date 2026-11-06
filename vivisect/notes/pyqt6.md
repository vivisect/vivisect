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

