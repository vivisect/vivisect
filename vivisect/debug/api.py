
import vivisect.debug.process as v_process

class DebugApi:

    def __init__(self, targ, **info):
        self._dbg_targ = targ
        self._dbg_info = info
        #self.ext object with proxy caller

    def getDebugTarget(self):
        return self._dbg_targ

    def ps(self):
        '''
        Retrieve a list of Process objects for the debug target.

        Example:

            import vivisect.debug.api as v_dbgapi
            dbg = v_dbgapi.getDebugApi()

            for p in dbg.ps():
                print( p.info('name') )

        '''
        ret = []
        for proc in self._dbg_targ.ps():
            ret.append( self._init_process( proc ) )
        return ret

    def attach(self, pid):
        '''
        Attach and return a Trace for a process by pid.

        Example:

            import vivisect.debug.api as v_dbgapi
            dbg = v_dbgapi.getDebugApi()

            trace = dbg.attach(pid)

        '''
        proc = self._dbg_targ.proc(pid)
        if proc == None:
            raise Exception('no such process: %s' % (pid,))

        trace = self._proc_trace(proc)
        trace.attach()

        return trace

    def _init_process(self, proc):
        return v_process.Process(proc, self)

    def exec(self, cmdline):
        proc,events = self._dbg_targ._trace_exec(cmdline)
        trace = self._proc_trace(proc)
        trace._run_exec_events(events)
        return trace

    def callExtApi(self, api, *args, **kwargs):
        '''
        Call an extended API on the DebugTarget.

        Example:

            dbg.callExtApi('woot',10,foo='blah')

        '''
        return self._dbg_targ.callExtApi(api,*args,**kwargs)

dbgctors = {
}

def addDebugApi(targ,ctor):
    '''
    Add a DebugApi ctor for a target name.

    Example:

        class MyDebugApi(DebugApi):
            ...

        addDebugApi('mything',MyDebugApi)

    '''
    dbgctors[targ] = ctor

def getDebugApi(targ='this',**info):
    '''
    Construct a new DebugApi object for the given target.

    Example:

        dbg = getDebugApi('vmware',port=8832)

    '''
    ctor = dbgctors.get(targ)
    if ctor == None:
        return ctor

    return ctor(**info)
