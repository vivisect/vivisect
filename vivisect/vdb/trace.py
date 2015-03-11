import synapse.event.dist as s_evtdist

class Trace(s_evtdist.EventDist):
    '''
    The Trace class implements the API for debugging a process.

    Example:

        import vivisect.vdb.debug as v_debug

        dbg = v_debug.getDebugApi()
        for proc in dbg.getProcList():
            if proc[1].get('name') == 'calc.exe':

                trace = dbg.getTraceForProc(proc)
                # do stuff...

    '''
    def __init__(self, proc, dbgapi):
        s_evtdist.EventDist.__init__(self)

        self.proc = proc
        self.dbgapi = dbgapi
        self.target = dbgapi.getDebugTarget()

        self.libs = {}
        self.threads = {}

    def attach(self, pid):
        events = self.target.procAttach()

    #def detach(self):

