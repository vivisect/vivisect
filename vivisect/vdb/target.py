
class DebugTarget:

    def __init__(self, **info):
        self._tgt_info = info

    def getProcList(self):
        return [(0,{'name':'woot'})]

