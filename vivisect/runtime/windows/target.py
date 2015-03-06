import vivisect.vdb.debug as v_debug
import vivisect.vdb.trace as v_trace
import vivisect.vdb.target as v_target
import vivisect.lib.thishost as v_thishost

class WindowsTarget(v_target.DebugTarget):

    def __init__(self, **info):
        v_target.DebugTarget.__init__(self, **info)

class WinTargetI386(WindowsTarget): pass
class WinTargetAmd64(WindowsTarget): pass

def winDebugCtor(**info):

    if v_thishost.check(arch='i386'):
        return WinTargetI386(**info)

    if v_thishost.check(arch='amd64'):
        return WinTargetAmd64(**info)

    print('winDebugCtor')

v_debug.addDebugCtor('this',winDebugCtor)
