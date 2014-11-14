from PyQt4 import QtCore, QtGui

from vqt.basics import *

example_src = '''
// A comment (not /* yet... */ )
// "pure" c types only for now...
struct example {
    char x; // This is ok too...
    unsigned int y[20];
};

'''

class UserStructEditor(QtGui.QWidget):

    def __init__(self, vw, name=None, parent=None):
        '''
        Open a view to edit/create user structure defs.
        If "name" is none, we assume they are creating one.
        '''
        QtGui.QWidget.__init__(self, parent=parent)
        self._v_vw = vw
        self._v_sname = name
        self._v_changed = True

        ssrc = example_src
        if name:
            ssrc = vw.getUserStructSource( name )
            self._v_changed = False

        self.srcedit = QtGui.QTextEdit(parent=self)
        self.srcedit.setText( ssrc )
        self.srcedit.textChanged.connect( self._text_changed )

        buttons = QtGui.QDialogButtonBox( QtGui.QDialogButtonBox.Save, parent=self)
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
            QtGui.QMessageBox.warning(self, 'Syntax Error', str(e), QtGui.QMessageBox.Ok )


    def _text_changed(self):
        self._v_changed = True        
        self._set_title()

