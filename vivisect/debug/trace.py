import vivisect.debug.bases as v_bases
from vivisect.debug.common import forever

class Trace(v_bases.TraceBase):
    '''
    The Trace class implements the API for debugging a process.

    Traces can operate synchronously or asynchronously to allow both
    simple scripting as well as non-blocking debugger behavior.

    Trace Events:

            * proc:attach       - the trace has newly attached
            * proc:ready        - initial attach/loads complete

            * proc:exit         - the trace process has exited
            * proc:detach       - the trace has detached from process


            * trace:break       - the trace hit a break/watch
            * proc:signal       - the trace detected a signal/exception

            * lib:load          - the trace detected a library load
            * lib:free          - the trace detected a library free

            * thread:init       - the trace detected a new thread
            * thread:exit       - the trace detected a thread exit

            * cpu:run           - the trace is about to continue execution
            * cpu:stop          - the trace is stopping execution


    Example:

        import vivisect.debug.debugger as v_debugger

        dbg = v_dbgapi.getDebugger()

        for p in dbg.getProcessList():
            if p.getProcInfo('name') == 'calc.exe':
                t = p.getTrace(attach=True)

                trace = dbg.getTraceForProc(proc)
                # do stuff...


    '''
    def attach(self, wait=True):
        '''
        Attach the trace to the target process and optionally block.

        Example:

            trace = dbgapi.traceForPid(pid)
            trace.on('lib:load', dostuff)
            trace.attach()

            # we are now attached and stopped
            # ( with initial libs loaded )

        '''
        if self.once:
            raise Exception('Trace object may not be re-used')

        self.once = True
        self.stopevt.clear()
        self.runq.put( {'attach':True} )

        if wait:
            self.wait()

    def run(self, until=None, wait=True):
        '''
        Continue execution for the trace process.

        The optional callback "until" will be used to continue
        the process execution loop until the callback returns
        True.  Specify wait=False to enable async/non-blocking.

        Example:

            def until(trace):
                return trace.lib('woot') != None

            trace.run(until=until,wait=True)

        '''
        self._req_state(attached=True, running=False)

        runinfo = {'until':until}

        self.stopevt.clear()
        self.runq.put( runinfo )

        if wait:
            self.wait()

    def cont(self):
        '''
        Continue exeuction ( async ) once event processing is complete.

        This method is the correct way to cause the trace to run again
        once current run or event callbacks are complete.

        def mybreak(event):
            if not thingiwantisready(trace):
                trace.cont()

        trace.addBreakByAddr(addr, onhit=onhit)
        trace.run(wait=True)

        '''
        self.runinfo['cont'] = True

    def stop(self, wait=True):
        '''
        Stop (break) the target process and optionally wait for it to fully stop.

        Example:

            trace.stop(wait=True)

            # traced process has stopped executing

        '''
        self._req_state(running=True)
        self.target.traceStop( self.proc[0] )
        if wait:
            self.wait()

    def wait(self, timeout=None):
        '''
        Wait for the trace to stop running.

        Returns True if the trace is stopped, False on timeout.

        Example:

            if trace.wait(timeout=60):
                print('trace is stopped')

        '''
        return self.stopevt.wait(timeout=timeout)

    def setAutoCont(self, evtname, cont=True):
        '''
        Set an events "auto continue" status by name.

        Example:

            # do not stop on library load events
            trace.setAutoCont('lib:load')

        '''
        self.autocont[evtname] = cont

    def getAutoCont(self):
        '''
        Returns a dict of <name>:<bool> pairs for event auto-continue status.

        Example:

            auto = trace.getAutoCont()

            if auto.get('trace:woot'):
                print('trace will auto-continue the trace:woot event')

        NOTE: the returned dict is *not* a copy, modifications *will*
              effect trace behavior.

        '''
        return dict(self.autocont)

    def setSigIgnore(self, code, ignore=True):
        '''
        Set a signal code to be "ignored" ( triggers automatic continue ).

        Example:

            # ignore signal/exception code 0xd0af00c3
            trace.setSigIgnore( 0xd0af00c3 )

        '''
        self.sigignore[code] = ignore

    def getSigIgnore(self):
        '''
        Returns the current ignored signals dict.

        Example:

            ign = trace.getSigIgnore()
            if ign.get( 0xc000001d ):
                print('trace is purposely fun exception...')

        NOTE: the returned dict is *not* a copy, modifications *will*
              effect trace behavior.

        '''
        return self.sigignore

    def kill(self):
        '''
        Send the traced process a kill signal and wait for it to exit.
        '''
        self.target.traceKill( self.proc[0] )
        self.run(until=forever, wait=True)

    def addBreakByAddr(self, addr, onhit=None, **info):
        '''
        Add a breakpoint by address.

        The onhit callback may be specified to be notified when the
        breakpoint is hit.

        Example:

            # bp is the (bpid,info) tufo
            def onhit(trace, bp):
                print( bp[1].get('woot') )
                dostuff()

            trace.addBreakByAddr( addr, onhit, woot=10)
            trace.run()

        '''
        info['addr'] = addr
        info['onhit'] = onhit

        bp = self._bp_init(**info)

        return bp

    def addBreakByExpr(self, expr, onhit=None, **info):
        '''
        Add a breakpoint by expression.

        If the expression does not currently evalutate to an address
        the breakpoint will be deferred and evaluation will re-attempted.
        '''

        info['expr'] = expr
        info['onhit'] = onhit

        bp = self._bp_init(**info)
        ## if expression is not currently resolved, delay
        #self.bpdelay[ bp[0] ] = bp

        #self.fire('trace:bp:add', trace=self, bp=bp)
        return bp

    #def setBreakEnabled(self, bp, enabled=True):

    def delBreakPoint(self, bp):
        '''
        Delete a breakpoint by id.

        Example:

            trace.delBreakById( bpid )


        '''
        self._t_breaks.pop( bp[0], None)
        self.fire('trace:bp:del', trace=self, bp=bp)
        return bp

    def setTraceInfo(self, prop, valu):
        '''
        Set a property in the trace "info" dictionary.

        Example:

            trace.setTraceInfo('thing_i_want_later', Thing())

        '''
        self.traceinfo[prop] = valu
        self.fire('trace:info:set', trace=self, prop=prop, valu=valu)
        self.fire('trace:info:set:%s' % prop, trace=self, valu=valu)

    def getTraceInfo(self, prop):
        '''
        Retrieve a property from the "trace info" dictionary.

        Example:

            foo = trace.getTraceInfo('foo')

        '''
        return self.traceinfo.get(prop)

    def fini(self):
        self._req_state(attached=False)
        self.runq.shutdown()
        self.runthr.wait()

    def isInState(self, **kwargs):
        '''
        Checks that the trace matches the given states specified in kwargs.

        Example:

            if trace.isInState(attached=True, running=False):
                dostuff(trace)

        '''
        for k,v in kwargs.items():
            s = self.states.get(k)
            if s != v:
                return False
        return True

