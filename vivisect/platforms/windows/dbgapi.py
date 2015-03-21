
import vivisect.debug.api as v_dbgapi
import vivisect.platforms.windows.trace as v_win_trace

class WinDebugApi(v_dbgapi.DebugApi):

    def _proc_trace(self, proc):
        arch = proc[1].get('arch')

        if arch == 'i386':
            return v_win_trace.I386WinTrace(proc,self)

        if arch == 'amd64':
            return v_win_trace.Amd64WinTrace(proc,self)

        raise Exception('No Trace Class: %s' % (arch,))
