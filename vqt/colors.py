
qt_matrix = '''

QWidget {
    background-color: #000000;
    color: #00ff00;
    font: Courier;
}

QTextEdit {
    border: 2px solid #00802b;
}

QDockWidget::title {
    background: #000000;
    text-align: center;
}

QDockWidget::close-button, QDockWidget::float-button {
    border: 1px solid transparent;
    background: #00802b;
    padding: 0px;
}

QDockWidget::close-button:hover, QDockWidget::float-button:hover {
    background: #00ff00;
}

QTabBar::tab {
    /*
     background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                 stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                 stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
    */
    background: #000000;
    border: 2px solid #00802b;
    /* border-bottom-color: #C2C7CB; */
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    min-width: 8ex;
    padding: 2px;
}

QTabBar::tab:selected {
    border: 3px solid #00ff00;
    /* border-bottom-color: #00ff00; */
}

QTreeView::item:selected {
     /* border: 1px solid #567dbc; */
    color: #000000;
    background: #00802b;
}

QMainWindow::seperator {
    width: 4px;
    height: 4px;
    background: #00802b;
}

QMainWindow::seperator:hover {
    width: 4px;
    height: 4px;
    background: #00ff00;
}

QMenu {
    color: #00ff00;
    background-color: #000000;

    border: 2px solid #00802b;

    selection-color: #000000;
    selection-background-color: #00ff00;
}

QLineEdit {
    border: 2px solid #00802b;
    border-radius: 4px;
    /* padding: 0 8px; */
    /* font: Courier; */
    /* color: #00ff00; */
    /* background: #000000; */
    selection-background-color: darkgray;
}

QTreeView {
    border: 2px solid #00802b;
    alternate-background-color: #0f0f0f;
}

QHeaderView::section {
     color: #00ff00;
     padding-left: 4px;
     background-color: #000000;
     border: 1px solid #00802b;
}

QPushButton {
     border-width: 2px;
     border-radius: 4px;
     border-style: outset;
     border-color: #00802b;
     padding: 1px;
}

QComboBox {
    padding: 1px;
    color: #00ff00;
    background: #000000;
    border-radius: 4px;
    border: 2px solid #00802b;
    selection-color: #000000;
    selection-background-color: #00ff00;
}

QMenuBar {
    color: #00ff00;
    background-color: #000000;
    selection-color: #000000;
    selection-background-color: #00ff00;
    border: 2px solid #00802b;
}

QMenuBar::item {
    color: #00ff00;
    background-color: #000000;
}

QMenuBar::item:selected {
    color: #00ff00;
    background-color: #000000;
}

QMainWindow::separator {
     width: 4px;
     height: 4px;
     background: #00802b;
}

QMainWindow::separator:hover {
     background: #00ff00;
}

QSplitter::handle {
     width: 6px;
     height: 6px;
     background: #000000;
}

QSplitter::handle:hover {
     background: #00ff00;
}

QToolButton:disabled {
    color: #606060;
}

QToolButton { /* all types of tool button */
    border: 2px solid #8f8f91;
    border-radius: 6px;
}

QToolBar {
    background: #101010;
    border: 2px solid #00802b;
    spacing: 3px; /* spacing between items in toolbar */
}
'''

defcolors = qt_matrix

def getDefaultColors():
    return qt_matrix

