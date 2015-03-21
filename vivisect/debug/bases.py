import threading
import traceback

import synapse.lib.queue as s_queue
import synapse.event.dist as s_evtdist
import synapse.lib.threads as s_threads

import vivisect.hal.cpu as v_cpu
import vivisect.hal.memory as v_memory

'''
Internal guts of a few of the debug classes.
'''

class TraceMem:
    '''
    Implement the *super* thin API needed by the CacheMemory.
    '''
    def __init__(self, trace):
        self.pid = trace.proc[0]
        self.target = trace.getDebugApi().getDebugTarget()

    def getMemoryMaps(self):
        return self.target.memmaps(self.pid)

    def readMemory(self, addr, size):
        return self.target.memread(self.pid, addr, size)

    def writeMemory(self, addr, mem):
        return self.target.memwrite(self.pid, addr, mem)

class TraceBase:

    def __init__(self, proc, dbgapi):

        self.once = False
        self.proc = proc
        self.dbgapi = dbgapi
        self.target = dbgapi.getDebugTarget()

        self.autocont = {}      # auto-continue event status
        self.sigignore = {}     # auto-continue signal code status
        self.traceinfo = {}     # backing for setTraceInfo/getTraceInfo

        # allow each Trace subclass to call his own cpu ctor
        self._init_trace_cpu()

        self._syn_verbose = True
        self.traceinfo.update( self._init_trace_info() )

        # one thread per-trace to facilitate "non-blocking" run()
        self.runq = s_queue.Queue()
        self.runthr = s_threads.fireWorkThread(self._runThreadLoop)
        self.runinfo = {}   # run loop info ( such as cont=True and lastevent )
        self.stopevt = threading.Event()

        self.libs = {}
        self.states = {'attached':False,'running':False,'exited':False}

        self.targbus = s_evtdist.EventDist()    # events from target
        self.tracebus = s_evtdist.EventDist()   # "published" tracer events

        #self.targbus.on('*',self._slot_print)
        #self.tracebus.on('*',self._slot_print)
        self.tracebus.on('*', self._slot_trace_events )

        # "target" event handlers translate to "trace" events
        self.targbus.on('target:attach', self._slot_target_attach)
        self.targbus.on('target:thread:init', self._slot_target_thread_init)
        self.targbus.on('target:thread:exit', self._slot_target_thread_exit)
        self.targbus.on('target:lib:load', self._slot_target_lib_load)
        self.targbus.on('target:lib:unload', self._slot_target_lib_unload)
        self.targbus.on('target:signal', self._slot_target_signal)
        self.targbus.on('target:exit', self._slot_target_exit)

        # setup auto-continue event defaults
        self.setAutoCont('trace:attach')
        self.setAutoCont('trace:lib:load')
        self.setAutoCont('trace:lib:unload')
        self.setAutoCont('trace:thread:init')
        self.setAutoCont('trace:thread:exit')

        # allow each Trace subclass to init his own handlers
        self._init_trace_handlers()

    def _slot_trace_events(self, event):
        # gets called for each and every event on the trace bus
        self.runinfo['cont'] = self.autocont.get( event[0], False )
        self.runinfo['lastevent'] = event

    def _init_trace_handlers(self):
        pass

    def _init_trace_info(self):
        return {}

    def _slot_print(self, event):
        print('EVENT: %s %r' % event)

    def getDebugApi(self):
        '''
        Returns the DebugApi instance used to create the trace.

        Example:

            dbg = trace.getDebugApi()
            dbg.doOtherStuff()

        '''
        return self.dbgapi

    def _init_cpu_mem(self):
        self._trace_mem = TraceMem(self)
        self._trace_mem_cache = v_memory.MemoryCache( self._trace_mem )
        return self._trace_mem_cache

    def _req_state(self, **kwargs):
        for k,v in kwargs.items():
            s = self.states.get(k)
            if s != v:
                raise Exception('invalid state: %s=%s (requires %s)' % (k,s,v))

    def _runThreadLoop(self):
        for runinfo in self.runq:
            self.tracebus.fire('trace:run')
            try:
                while True:

                    signo = self.runinfo.get('signo')
                    self.runinfo.clear()

                    events = self.target.run(self.proc[0], signo=signo)

                    cont = self._run_targ_events( events )

                    # if we're no longer attached, break out
                    if not self.isInState(attached=True):
                        break

                    # run until callbacks take total precidence
                    until = runinfo.get('until')
                    if until != None:
                        try:
                            if not until(self):
                                continue

                        except Exception as e:
                            traceback.print_exc()
                            msg = 'run until callback error: %s' % (e,)
                            self.tracebus.fire('trace:error', msg=msg)

                        # we're either @until or error
                        break

                    if not cont:
                        break

                self._fireStopEvent()

            except Exception as e:
                traceback.print_exc()
                self._fireStopEvent()

    def _run_exec_events(self, events):
        cont = self._run_targ_events(events)
        if not cont:
            self._fireStopEvent()
            return

        self.run(wait=True)

    def _run_targ_events(self, events):
        # fire the given events through the targbus
        # Returns True if we should continue
        for event in events:
            self.targbus.dist(event)

        if self.runinfo.get('cont'):
            return True

    def _target_common(self, event):
        # consume generic elements of target events
        # such as current thread id and registers
        tid = event[1].get('tid')

        # did they select a thread?
        if tid != None:
            thread = self.setThread(tid)

            # did they prep us with regs?
            regdict = event[1].get('regdict')
            if regdict != None:
                thread[1]['regs'].load( regdict )

    def _slot_target_attach(self, event):
        self.states['attached'] = True
        proc = event[1].get('proc')
        self.proc[1].update( proc[1] )
        self.tracebus.fire('trace:attach', trace=self)

    #def _slot_target_detach(self, evt, evtinfo):
        #self.states['attached'] = False
        #self.tracebus.fire('trace:detach', proc=self.proc)

    def _slot_target_signal(self, event):
        evtinfo = event[1]
        signo = evtinfo.get('signo')
        exinfo = evtinfo.get('exinfo')
        signorm = evtinfo.get('signorm')

        self.runinfo['signo'] = signo
        self.runinfo['exinfo'] = exinfo
        self.runinfo['signorm'] = signorm

        self.tracebus.fire('trace:signal', trace=self, signo=signo, exinfo=exinfo, signorm=signorm)

    def _slot_target_exit(self, event):
        exitcode = event[1].get('exitcode')
        self.states['attached'] = False
        self.runinfo['exitcode'] = exitcode
        self.tracebus.fire('trace:exit', trace=self, exitcode=exitcode)

    def _slot_target_lib_load(self, event):
        self._target_common(event)
        lib = event[1].get('lib')
        self.libs[ lib[0] ] = lib
        self.tracebus.fire('trace:lib:load', trace=self, lib=lib)

    def _slot_target_lib_unload(self, event):
        self._target_common(event)
        addr = event[1].get('addr')
        lib = self.libs.pop(addr,None)
        self.tracebus.fire('trace:lib:unload', trace=self, lib=lib)

    def _slot_target_thread_init(self, event):
        thread = event[1].get('thread')
        self._init_thread(thread)

        pid = self.proc[0]
        tid = thread[0]

        def cacheregs():
            return self.target.getregs( pid, tid )

        thread[1]['regs'].oncache( cacheregs )
        self.tracebus.fire('trace:thread:init', trace=self, thread=thread)

    def _slot_target_thread_exit(self, event):
        tid = event[1].get('tid')
        exitcode = event[1].get('exitcode')

        thread = self.getThread(tid=tid)
        self._fini_thread(thread)
        self.tracebus.fire('trace:thread:exit', trace=self, thread=thread, exitcode=exitcode)

    def _fireStopEvent(self):
        self.tracebus.fire('trace:stop')
        self.stopevt.set()

