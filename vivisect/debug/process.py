
class Process:
    '''
    A running processes on the debug target.

    Each Process instance supports methods which are available
    through the DebugApi *without* attaching to the process.

    Example:

    import vivisect.debug.api as v_dbgapi

    dbg = v_dbgapi.getDebugApi()

    for p in dbg.ps():
        if p.info('name') == 'sshd':
            p.kill()
    '''
    def __init__(self, proc, dbgapi):
        self.pid = proc[0]
        self.proc = proc
        self.dbgapi = dbgapi
        self.dbgtgt = dbgapi.getDebugTarget()

    def __str__(self):
        pid = self.proc[0]
        name = self.info('name')
        return '%6d %s' % (pid,name)

    def __repr__(self):
        return str(self)

    def info(self, prop):
        '''
        Retrieve a property from the process info dictionary.

        Example:

            exepath = p.info('path')

        '''
        return self.proc[1].get(prop)

    def kill(self):
        '''
        Kill the target process ( forced termination ).

        Example:

            for proc in dbgapi.ps():
                if proc.info('name') == 'kavtray.exe':
                    proc.kill()

        '''
        self.dbgtgt._pid_kill( self.pid )

    def attach(self):
        '''
        Attach to the target process and return a Trace object.

        Example:

            import vivisect.debug.api as v_dbgapi

            dbg = v_dbgapi.getDebugApi()

            for p in dbg.ps():
                if p.info('name') == 'lsass.exe':
                    trace = p.attach()

        '''
        trace = self.dbgapi._proc_trace(self.proc)
        trace.attach()
        return trace
