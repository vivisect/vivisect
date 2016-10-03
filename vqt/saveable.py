import json
import traceback


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
        if qstate is None:
            return

        try:
            state = json.loads(str(qstate))
            self.vqSetSaveState(state)
        except Exception as e:
            traceback.print_exc()
            print(('failed to restore %s: %s' % (name, e)))

    def vqGetSaveState(self):
        return None

    def vqSetSaveState(self, state):
        return None
