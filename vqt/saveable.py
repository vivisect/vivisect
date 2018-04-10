import json

try:
    from PyQt5.QtCore import PYQT_VERSION_STR
except:
    from PyQt4.QtCore import PYQT_VERSION_STR

def compat_isNone(state):
    if PYQT_VERSION_STR.startswith('4'):
        return state.isNull()
    return state == None or not len(state)

def compat_toStr(qstate):
    if PYQT_VERSION_STR.startswith('4'):
        return str(qstate.toString())
    return str(qstate)

def compat_toByteArray(strobj):
    if PYQT_VERSION_STR.startswith('4'):
        return strobj.toByteArray()
    return strobj

class SaveableWidget(object):
    '''
    Inherited by widgets that want to save and restore settings.

    Implement vqGetSaveState/vqSetSaveState.
    '''
    def vqSaveState(self, settings, name):
        state = self.vqGetSaveState()
        settings.setValue(name, json.dumps(state))

    def vqRestoreState(self, settings, name):
        qstate = settings.value(name)
        if qstate == None:
            return

        try:
            state = json.loads(compat_toStr(qstate))
            self.vqSetSaveState(state)
        except Exception, e:
            print('failed to restore %s: %s' % (name,e))

    def vqGetSaveState(self):
        return None

    def vqSetSaveState(self, state):
        return None


