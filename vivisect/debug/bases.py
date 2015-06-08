import itertools
import threading
import traceback
import collections

import synapse.lib.queue as s_queue
import synapse.event.dist as s_evtdist
import synapse.lib.threads as s_threads

import vivisect.hal.cpu as v_cpu
import vivisect.hal.memory as v_memory

'''
Internal guts of a few of the debug classes.
'''

class TraceMem(v_memory.Memory):
    '''
    Implement the *super* thin API needed by the CacheMemory.
    '''
    def __init__(self, trace):
        self.pid = trace.proc[0]
        self.cache = {}
        self.trace = trace
        self.target = trace.getDebugTarget()

    def _getMemoryMaps(self):
        mmaps = self.cache.get('mmaps')
        if mmaps == None:
            mmaps = self.target.traceGetMemoryMaps(self.pid)
            self.cache['mmaps'] = mmaps
        return mmaps

    def _getMemoryMap(self, addr):
        for mmap in self.mmaps():
            if addr < mmap[0]:
                continue
            if addr > mmap[0] + mmap[1].get('size'):
                continue
            return mmap

    def _readMemory(self, addr, size):
        return self.target.traceReadMemory(self.pid,addr,size)

    def _writeMemory(self, addr, byts):
        return self.target.traceWriteMemory(self.pid,addr,byts)

class TraceBase:

    def __init__(self, proc, dbg):

        self.dbg = dbg
        self.once = False
        self.proc = proc
        self.target = dbg.getDebugTarget()

        self.bpidgen = itertools.count(0)

        self.autocont = {}      # auto-continue event status
        self.sigignore = {}     # auto-continue signal code status

        self._t_breaks = {}         # id:tufo

        def membrk():
            return {'breaks':{}, 'active':False, 'saved':None, 'refs':0 }

        self._t_membreaks = collections.defaultdict( membrk )# saved memory break info

        # hook for trace mixin ctors
        self._initTraceMixins()

        # one thread per-trace to facilitate "non-blocking" run()
        self.runq = s_queue.Queue()
        self.runthr = s_threads.fireWorkThread(self._runThreadLoop)
        self.runinfo = {}   # run loop info ( such as cont=True and lastevent )
        self.stopevt = threading.Event()

        self.states = {'attached':False,'running':False,'exited':False}

        # "target" event handlers translate to "trace" events
        self.on('proc:exit', self._onProcExit)
        self.on('proc:attach', self._onProcAttach)

        self.on('proc:signal', self._onProcSignal)

        self.on('thread:init', self._onThreadInit)
        self.on('thread:exit', self._onThreadExit)

        self.on('lib:load', self._onLibLoad)
        self.on('lib:free', self._onLibFree)

        # fire the general handler for all trace events
        self.on('proc:attach', self._onTraceEvent)
        self.on('proc:detach', self._onTraceEvent)

        self.on('thread:init', self._onTraceEvent)
        self.on('thread:exit', self._onTraceEvent)

        self.on('lib:load', self._onTraceEvent)
        self.on('lib:free', self._onTraceEvent)

        self.on('proc:signal', self._onTraceEvent)
        self.on('proc:exit', self._onTraceEvent)

        # setup auto-continue event defaults
        self.setAutoCont('proc:attach')

        self.setAutoCont('lib:load')
        self.setAutoCont('lib:free')

        self.setAutoCont('thread:init')
        self.setAutoCont('thread:exit')

        # allow each Trace subclass to init his own stuff
        self._initTraceLocals()

    def _bp_set_enabled(self, bp, en):
        if bp[1].get('enabled') == en:
            return

        self.fire('bp:enabled', bp=bp, en=en)

        addr = bp[1].get('addr')
        if addr == None:
            return

        if en:
            self._inc_membreak(addr, bp)
        else:
            self._dec_membreak(addr, bp)

    def _mb_clear(self):
        # deactivate all memory breaks
        for addr,mbinfo in self._t_membreaks.items():
            if not mbinfo.get('active'):
                continue

            self._mb_deactivate(addr,mbinfo)

    def _mb_activate(self, addr, mbinfo):
        #activate a memory break address
        brk = self._cpu_info.get('brk')

        if brk == None:
            self.error('cpu info has no brk!')
            return

        mbinfo['saved'] = self.readMemory(addr, len(brk))

        self.writeMemory(addr, brk)
        mbinfo['active'] = True

    def _mb_deactivate(self, addr, mbinfo):
        # deactivate a memory break address
        sav = mbinfo.get('saved')
        self.writeMemory(addr, sav)
        mbinfo['active'] = False

    def _bp_sync(self):
        # resolve/activate/clear breakpoints

        #FIXME handle deferred breaks here

        for addr,mbinfo in self._t_membreaks.items():
            refs = mbinfo.get('refs')
            activ = mbinfo.get('active')

            if refs == 0 and activ:
                self._mb_deactivate(addr,mbinfo)
                # FIXME check for not breaks and pop
                continue

            if refs != 0 and not activ:
                self._mb_activate(addr,mbinfo)

    def _inc_membreak(self, addr, bp):
        mbinfo = self._t_membreaks[addr]
        mbinfo['breaks'][ bp[0] ] = bp
        mbinfo['refs'] += 1

    def _dec_membreak(self, addr, bp):
        mbinfo = self._t_membreaks[addr]
        mbinfo['breaks'].pop( bp[0], None)
        mbinfo['refs'] -= 1

    def _bp_init(self, **info):
        # initialize a bp tufo
        info['active'] = False
        info['enabled'] = True

        bp = (next(self.bpidgen), info)

        self._t_breaks[ bp[0] ] = bp
        self.fire('bp:add', bp=bp)

        if bp[1].get('enabled'):
            self._bp_set_enabled(bp, True)

        return

    def _bp_fini(self, bp):

        self.fire('bp:del', bp=bp)

        # disable to handle dec membreak
        self._bp_set_enabled(bp, False)
        self._t_breaks.pop( bp[0], None )

        # do we have an addr?
        addr = bp[1].get('addr')
        if addr == None:
            return

        # does the addr have mem break info yet?
        mbinfo = self._t_membreaks.get(addr)
        if mbinfo == None:
            return

        # pop the mbinfo if there are no other breaks
        if not mbinfo.get('breaks'):
            self._t_membreaks.pop(addr,None)

    def _onTraceEvent(self, event):
        # gets called for each and every event on the trace bus
        self.runinfo['cont'] = self.autocont.get( event[0], False )
        self.runinfo['lastevent'] = event

    def _initTraceLocals(self):
        pass

    def getDebugger(self):
        '''
        Returns the Debugger instance used to create the trace.

        Example:

            dbg = trace.getDebugger()
            dbg.doOtherStuff()

        '''
        return self.dbg

    def getDebugTarget(self):
        '''
        Return a reference to the DebugTarget object.

        Example:

            tgt = trace.getDebugTarget()
        '''
        return self.target

    def _initCpuMemory(self):
        return TraceMem(self)

    def _req_state(self, **kwargs):
        for k,v in kwargs.items():
            s = self.states.get(k)
            if s != v:
                raise Exception('invalid state: %s=%s (requires %s)' % (k,s,v))

    def _run_attach(self):
        pid = self.proc[0]
        events = self.target.traceAttach(pid)
        self.distall( events )
        self._traceFullStop()

    def _runThreadLoop(self):
        for runinfo in self.runq:

            try:

                if runinfo.get('attach'):
                    self._run_attach()
                    continue

                self.fire('cpu:run')
                while True:

                    signo = self.runinfo.get('signo')

                    self._traceToRun()

                    events = self.target.traceRun(self.proc[0], signo=signo)

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
                            self.error('run until callback error: %s' % (e,))

                        # we're either @until or error
                        break

                    if not cont:
                        break

                self._traceFullStop()

            except Exception as e:
                traceback.print_exc()
                self._traceFullStop()

    def _runExecEvents(self, events):
        cont = self._run_targ_events(events)
        if not cont:
            self._traceFullStop()
            return

        self.run(wait=True)

    def _traceToRun(self):
        # called pre-run in the loop
        self._bp_sync()
        self.stopevt.clear()
        self.runinfo.clear()

    def _run_targ_events(self, events):
        # fire the given events through the targbus
        # Returns True if we should continue
        for event in events:
            self._target_common(event)
            self.dist( event )
        #self.distall(events)
        return self.runinfo.get('cont',False)

    def _target_common(self, event):
        # consume generic elements of target events
        # such as current thread id and registers
        tid = event[1].get('tid')

        # did they select a thread?
        if tid != None:
            thread = self.thread(tid)

            # did they prep us with regs?
            regdict = event[1].get('regdict')
            if regdict != None:
                thread[1]['regs'].load( regdict )

    def _onProcAttach(self, event):
        self.states['attached'] = True
        proc = event[1].get('proc')
        self.proc[1].update( proc[1] )

    def _onProcSignal(self, event):
        evtinfo = event[1]

        signo = evtinfo.get('signo')
        exinfo = evtinfo.get('exinfo')
        signorm = evtinfo.get('signorm')

        self.runinfo['signo'] = signo
        self.runinfo['exinfo'] = exinfo
        self.runinfo['signorm'] = signorm

    def _onProcExit(self, event):
        exitcode = event[1].get('exitcode')
        self.states['attached'] = False
        self.runinfo['exitcode'] = exitcode

    def _onLibLoad(self, event):
        lib = event[1].get('lib')
        v_cpu.Cpu._initLib(self, lib)

    def _onLibFree(self, event):
        addr = event[1].get('addr')
        lib = self._cpu_libs.get(addr,None)
        v_cpu.Cpu._finLib(lib)

        # put the lib into the event for everyone else
        event[1]['lib'] = lib

    def _onThreadInit(self, event):
        thread = event[1].get('thread')
        self._initCpuThread(thread)

        pid = self.proc[0]
        tid = thread[0]

        def cacheregs():
            return self.target.traceGetRegs( pid, tid )

        thread[1]['regs'].oncache( cacheregs )

    def _onThreadExit(self, event):
        tid = event[1].get('tid')
        exitcode = event[1].get('exitcode')

        thread = self.thread(tid)
        self._fini_thread(thread)

        # put the thread tuple into the event for everybody else
        event[1]['thread'] = thread

    def _traceFullStop(self):
        '''
        Called by event processing when we know the trace is stopped.
        ( and not going to immediately go again )
        '''
        self._mb_clear()
        self.states['running'] = False
        self.stopevt.set()
        self.fire('cpu:stop')
