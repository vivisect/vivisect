from PyQt5 import QtCore, QtGui, QtWidgets

from vqt.basics import *

example_src = '''
// A comment (not /* yet... */ )
// "pure" c types only for now...
struct example {
    char x; // This is ok too...
    unsigned int y[20];
};

'''

class UserStructEditor(QtWidgets.QWidget):

    def __init__(self, vw, name=None, parent=None):
        '''
        Open a view to edit/create user structure defs.
        If "name" is none, we assume they are creating one.
        '''
        QtWidgets.QWidget.__init__(self, parent=parent)
        self._v_vw = vw
        self._v_sname = name
        self._v_changed = True

        ssrc = example_src
        if name:
            ssrc = vw.getUserStructSource( name )
            self._v_changed = False

        self.srcedit = QtWidgets.QTextEdit(parent=self)
        self.srcedit.setText( ssrc )
        self.srcedit.textChanged.connect( self._text_changed )

        buttons = QtWidgets.QDialogButtonBox( QtWidgets.QDialogButtonBox.Save, parent=self)
        buttons.accepted.connect( self._save_event )

        self._set_title()
        self.setLayout( VBox( self.srcedit, buttons ) )

    def _set_title(self):

        name = self._v_sname
        if name == None:
            name = '(new)'

        status = ''
        if self._v_changed:
            status = '(unsaved!)'

        self.setWindowTitle('Struct Edit: %s %s' % (name, status))

    def _save_event(self):

        ssrc = str(self.srcedit.toPlainText())

        try:
            self._v_sname = self._v_vw.setUserStructSource( ssrc )
            self._v_changed = False
            self._set_title()
        except Exception, e:
            QtWidgets.QMessageBox.warning(self, 'Syntax Error', str(e), QtWidgets.QMessageBox.Ok )


    def _text_changed(self):
        self._v_changed = True        
        self._set_title()

