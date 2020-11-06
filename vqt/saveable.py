import json
import logging

logger = logging.getLogger(__name__)

def compat_isNone(state):
    # WTF! (QByteArray is None) is True!
    if state is None:
        return True

    return not len(state)

class SaveableWidget(object):
    '''
    Inherited by widgets that want to save and restore settings.

    Implement vqGetSaveState/vqSetSaveState.
    '''
    def vqSaveState(self, settings, name, stub=''):
        state = self.vqGetSaveState()
        settings.setValue(stub+name, json.dumps(state))

    def vqRestoreState(self, settings, name, stub=''):
        qstate = settings.value(stub+name)
        if qstate is None:
            return

        try:
            state = json.loads(str(qstate))
            self.vqSetSaveState(state)
        except Exception as e:
            logger.warning('failed to restore %s: %s', name, e)

    def vqGetSaveState(self):
        return None

    def vqSetSaveState(self, state):
        return None
