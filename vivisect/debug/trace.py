import vivisect.debug.bases as v_bases
from vivisect.debug.lib.until import forever

class Trace(v_bases.TraceBase):
    '''
    The Trace class implements the API for debugging a process.

    Example:

        import vivisect.debug.api as v_dbgapi

        dbg = v_dbgapi.getDebugApi()
        for proc in dbg.ps():
            if proc[1].get('name') == 'calc.exe':

                trace = dbg.getTraceForProc(proc)
                # do stuff...

    '''
    def attach(self):
        if self.once:
            raise Exception('Trace object may not be re-used')

        self.once = True
        pid = self.proc[0]

        # FIXME this belongs in the run loop
        events = self.target.attach(pid)
        [ self.targbus.dist(e) for e in events ]
        self._fireStopEvent()

    def run(self, until=None, wait=False):
        '''
        Continue execution for the trace process.

        The optional callback "until" will be used to continue
        the process execution loop until the callback returns
        True.  Specify wait=True to block until execution has
        ceased.

        Example:

            def until(trace):
                return trace.getLibByName('woot') != None

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
            trace = event[1].get('trace')
            if not thingiwantisready(trace):
                trace.cont()

        trace.addBreakByAddr(addr, onhit=onhit)
        trace.run(wait=True)

        '''
        self.runinfo['cont'] = True

    def stop(self, wait=True):
        self._req_state(running=True)
        self.target.stop( self.proc[0] )
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

    def print(self, msg, **info):
        '''
        Fire a trace:print event to display msg on interactive debuggers.

        Example:

            def onhit(event):
                trace = event[1].get('trace')
                trace.print('my break was hit')

            trace.addBreakByAddr(addr, onhit=onhit)
        '''
        self.fire('trace:print', msg=msg, **info)

    def error(self, msg, **info):
        '''
        Fire a trace:error event to notify debuggers we have a problem.

        Example:

            try:
                dostuff( trace )
            except Exception as e:
                trace.error(e)

        '''
        self.fire('trace:error', msg=msg, **info)

    def setAutoCont(self, evtname, cont=True):
        '''
        Set an events "auto continue" status by name.

        Example:

            # do not stop on library load events
            trace.setAutoCont('trace:lib:load')

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
        return self.autocont

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
        self.target.kill( self.proc[0] )
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
    def addBreakByExpr(self, expr, onhit=None, **info):
        '''
        Add a breakpoint by expression.

        If the expression does not currently evalutate to an address
        the breakpoint will be deferred and evaluation will re-attempted.
        '''

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

    #def getLibs(self):
    #def getLibByName(
    #def getLibByAddr(

    def isInState(self, **kwargs):
        '''
        '''
        for k,v in kwargs.items():
            s = self.states.get(k)
            if s != v:
                return False
        return True

    #def detach(self):
    #def getLibBex(self, 


