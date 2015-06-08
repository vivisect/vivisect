
class Process:
    '''
    A running processes on the debug target.

    Each Process instance supports methods which are available
    through the Debugger *without* attaching to the process.

    Example:

    import vivisect.debug.debugger as v_debugger

    dbg = v_debugger.getDebugger()

    for p in dbg.getProcessList():
        if p.getProcInfo('name') == 'sshd':
            p.kill()
    '''
    def __init__(self, proc, dbg):
        self.dbg = dbg
        self.pid = proc[0]
        self.proc = proc
        self.dbgtgt = dbg.getDebugTarget()

    def __str__(self):
        pid = self.proc[0]
        name = self.getProcInfo('name')
        return '%6d %s' % (pid,name)

    def __repr__(self):
        return str(self)

    def getProcInfo(self, prop):
        '''
        Retrieve a property from the process info dictionary.

        Example:

            exepath = p.getProcInfo('path')

        '''
        return self.proc[1].get(prop)

    def kill(self):
        '''
        Kill the target process ( forced termination ).

        Example:

            for proc in dbg.getProcessList():
                if proc.getProcInfo('name') == 'kavtray.exe':
                    proc.kill()

        '''
        self.dbgtgt._pid_kill( self.pid )

    def getTrace(self, attach=False):
        '''
        Return an (optionally already attached) Trace for the Process.

        Example:

            import vivisect.debug.debugger as v_debugger

            dbg = v_debugger.getDebugger()

            for p in dbg.getProcessList():
                if p.getProcInfo('name') == 'lsass.exe':
                    trace = p.getTrace()
                    trace.on('lib:load', dostuff)
                    trace.attach()

        '''
        trace = self.dbg._initTrace(self.proc)
        if attach:
            trace.attach()
        return trace
