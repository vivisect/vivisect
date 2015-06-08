import synapse.event.dist as s_evtdist
import vivisect.debug.cmdline as v_cmdline
import vivisect.debug.process as v_process

from vivisect.debug.common import *

class Debugger(s_evtdist.EventDist):

    def __init__(self, targ, **info):
        s_evtdist.EventDist.__init__(self)
        self._dbg_targ = targ
        self._dbg_info = targ.getDebugInfo()
        self._dbg_info.update( info )

    def getDebugCli(self):
        '''
        Construct and return a new VdbCmdLine object for this debugger.

        Example:

            cli = dbg.getDebugCli()

            cli.cmdloop()

        '''
        return self._dbg_getDebugCli()

    def getDebugInfo(self, prop, default=None):
        '''
        Retrieve an info property from the Debugger.

        Example:

            woot = dbg.getDebugInfo('woot')

        '''
        return self._dbg_info.get(prop,default)

    def getProcessList(self):
        '''
        Retrieve a list of Process objects for the debug target.

        Example:

            import vivisect.debug.debugger as v_debugger
            dbg = v_debugger.getDebugger()

            for p in dbg.getProcessList():
                print( p.getProcInfo('name') )

        '''
        return self._getProcessList()

    def attach(self, pid):
        '''
        Attach and return a Trace for a process by pid.

        Example:

            import vivisect.debug.debugger as v_debugger
            dbg = v_debugger.getDebugger()

            trace = dbg.attach(pid)

        '''
        trace = self.getTraceForPid(pid)
        trace.attach(wait=True)
        return trace

    def getProcessByPid(self, pid):
        '''
        Retrieve a Process object for the given pid.

        Example:

            proc = dbg.getProcessByPid(pid)
            
        '''
        proc = self._reqProcByPid(pid)
        return self._initProcess(proc)

    def _reqProcByPid(self, pid):
        proc = self._dbg_targ.getProcByPid(pid)
        if proc == None:
            raise NoSuchProcess('pid: %s' % (pid,))
        return proc

    def getTraceForPid(self, pid):
        '''
        Retrieve a trace object for the given process.

        Example:

            trace = dbg.getTraceForPid(pid)

            # ...add event hooks

            trace.attach(pid)


        Notes:

            * trace is *not* attached upon return.
              ( allows event hooks to be added before attach )

        '''
        proc = self._reqProcByPid(pid)
        trace = self._initTrace(proc)
        return trace

    def exec(self, cmdline):
        proc,events = self._dbg_targ.traceExec(cmdline)
        proc[1]['cmdline'] = cmdline
        trace = self._initTrace(proc)
        trace._runExecEvents(events)
        return trace

    def getDebugTarget(self):
        '''
        Returns a reference to the underlying DebutTarget instance.

        Example:

            tgt = dbg.getDebugTarget()

        Notes:

            * be *sure* you know what you're doing. this is dangerous.

        '''
        return self._dbg_targ

    def _initTrace(self, proc):
        raise ImplementMe()

    def _initProcess(self, proc):
        '''
        Construct and return a vivisect.debug.Process for the
        given (pid,info) proc tufo returned by the target object.
        '''
        return v_process.Process(proc, self)

    def _getProcessList(self):
        '''
        Return a list of vivisect.debug.Process objects for the target.
        '''
        ret = []
        for proc in self._dbg_targ.getProcList():
            ret.append( self._initProcess( proc ) )
        return ret

    def _dbg_getDebugCli(self):
        return v_cmdline.VdbCmdLine(self)

dbgctors = {
}

def addDebugCtor(targ,ctor):
    '''
    Add a Debugger ctor for a target name.

    Example:

        class MyDebugger(Debugger):
            ...

        addaddDebugCtor('mything',MyDebugger)

    '''
    dbgctors[targ] = ctor

def getDebugger(targ='this',**info):
    '''
    Construct a new Debugger object for the given target.

    Example:

        dbg = getDebugger('vmware',port=8832)

    '''
    ctor = dbgctors.get(targ)
    if ctor == None:
        return ctor

    return ctor(**info)

