'''
A widget for editing EnviConfig options.
'''
from PyQt4 import QtCore, QtGui

class EnviConfigOption:

    def __init__(self, config, name, value):
        self.econfig = config
        self.ename = name
        self.evalue = value

    def setEnviValue(self, evalue):
        self.evalue = evalue
        self.econfig[self.ename] = evalue

class EnviConfigBool(EnviConfigOption,QtGui.QCheckBox):

    def __init__(self, config, name, value, parent=None):
        QtGui.QCheckBox.__init__(self, parent=parent)
        EnviConfigOption.__init__(self, config, name, value)
        self.toggled.connect( self.setEnviValue )
        self.setChecked(value)

    def parseEnviValue(self):
        self.setEnviValue( self.isChecked() )

class EnviConfigInt(EnviConfigOption,QtGui.QLineEdit):

    def __init__(self, config, name, value, parent=None):
        QtGui.QLineEdit.__init__(self, parent=parent)
        EnviConfigOption.__init__(self, config, name, value)
        self.editingFinished.connect( self.parseEnviValue )

        valstr = str(value)
        if value > 1024:
            valstr = '0x%.8x' % value
        self.setText(valstr)

    def parseEnviValue(self):
        self.setEnviValue(int(str(self.text()),0))

class EnviConfigString(EnviConfigOption,QtGui.QLineEdit):
    def __init__(self, config, name, value, parent=None):
        QtGui.QLineEdit.__init__(self, parent=parent)
        EnviConfigOption.__init__(self, config, name, value)
        self.editingFinished.connect( self.parseEnviValue )
        self.setText(value)

    def parseEnviValue(self):
        self.setEnviValue(str(self.text()))

cfgtypes = {
    int:EnviConfigInt,
    long:EnviConfigInt,
    str:EnviConfigString,
    unicode:EnviConfigString,
    bool:EnviConfigBool,
}

class EnviConfigEditor(QtGui.QWidget):

    def __init__(self, config, parent=None):
        QtGui.QWidget.__init__(self, parent=parent)
        self.enviconfig = config

        lyt = QtGui.QFormLayout()

        optnames = config.keys()
        optnames.sort()

        for optname in optnames:
            optval = config.get(optname)
            cls = cfgtypes.get(type(optval))
            if cls == None:
                #print('no class: %r' % val)
                continue

            label = QtGui.QLabel(optname)
            clsobj = cls(config, optname, optval, parent=self)
            doc = config.getOptionDoc(optname)
            if doc != None:
                label.setToolTip(doc)
            lyt.addRow(label, clsobj)

        self.setLayout(lyt)

class EnviConfigTabs(QtGui.QTabWidget):
    '''
    A widget for a multi-tab multi-config
    editor view. Specify a list of (name,config)
    tuples.
    '''

    def __init__(self, configs, parent=None):
        QtGui.QTabWidget.__init__(self, parent=parent)

        for name,config in configs:
            editor = EnviConfigEditor(config, parent=self)
            self.addTab(editor, name)

if __name__ == '__main__':

    import vqt.main as vq_main
    import envi.config as e_config

    defaults = {
        'woot':10,
        'baz':'faz',
        'foo':True,
    }

    docs = {
        'woot':'The number of woots!',
        'baz':'Where to look for a baz',
        'foo':'Should we do foo?',
    }

    config = e_config.EnviConfig(filename='test.json', defaults=defaults, docs=docs)

    vq_main.startup()
    widget = EnviConfigEditor( config )
    widget.show()
    vq_main.main()

