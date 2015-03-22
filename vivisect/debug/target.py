import synapse.lib.queue as s_queue
import synapse.lib.threads as s_threads

from vertex.lib.common import tufo

class DebugTarget:
    '''
    The DebugTarget class implements the lowest level of the DebugApi.

    The DebugTarget is also the object which may be "remote" in the case
    of remote debugging.  This means all arguments/return values for *all*
    remotely accessed methods *must* be msgpack serializable.

    DebugApi --calls--> DebugTarget
    Trace    --calls--> DebugTarget

    For most platforms, the DebugTarget object should live in the runtime
    package.

    vivisect/runtime/<platform>/target.py
    '''

    def __init__(self, **info):
        self._tgt_info = info
        self._tgt_procs = {}
        self._tgt_extapis = {}

        self._tgt_pidq = {}
        self._tgt_pidt = {}

    def initPidThread(self, pid):
        '''
        Initialize a thread to handle some requests for the pid.
        '''
        pidq = s_queue.Queue()
        pidt = s_threads.fireWorkThread( self.mainPidThread, pidq )

        self._tgt_pidq[pid] = pidq
        self._tgt_pidt[pid] = pidt

    def finiPidThread(self, pid):
        '''
        Free resources associated with a previous initPidThread call.
        '''
        pidq = self._tgt_pidq.pop(pid)
        pidt = self._tgt_pidt.pop(pid)

        pidq.shutdown()
        pidt.join()

    def callPidThread(self, pid, func, *args, **kwargs):
        '''
        Helper utility for platforms which require only a single thread
        to call particular debug APIs.
        '''
        retq = s_threads.getThreadLocal('_pid_retq',s_queue.Queue)
        pidq = self._tgt_pidq.get(pid)

        pidq.put( (retq,func,args,kwargs) )

        ret = retq.get()
        if not isinstance(ret,Exception):
            return ret

        raise ret

    def execPidThread(self, func, *args, **kwargs):
        '''
        Attempt to atomically initialize a pid thread and call the func.

        ( if the func fails, clean up the new pid thread )
        '''
        retq = s_threads.getThreadLocal('_pid_retq',s_queue.Queue)

        pidq = s_queue.Queue()
        pidt = s_threads.fireWorkThread( self.mainPidThread, pidq )

        pidq.put( (retq,func,args,kwargs) )

        proc = retq.get()

        if isinstance(proc, Exception):
            pidq.shutdown()
            pidt.join()
            raise proc

        pid = proc[0]
        self._tgt_pidq[pid] = pidq
        self._tgt_pidt[pid] = pidt
        return proc

    def mainPidThread(self, pidq):
        for retq,meth,args,kwargs in pidq:
            try:
                retq.put( meth(*args,**kwargs) )
            except Exception as e:
                retq.put( e )

    def getFileBytes(self, path):
        return open(path,'rb').read()

    def putFileBytes(self, path, buf):
        fd = open(path,'wb')
        fd.write(buf)
        fd.close()

    def reqProcByPid(self, pid):
        proc = self._tgt_procs.get(pid)
        if proc == None:
            raise Exception('pid is not attached: %s' % (pid,))
        return proc

    def _init_thread(self, proc, tid, **info):
        '''
        Initialize a thread tufo for the specified proc.
        ( used only target side )
        '''
        thread = (tid,info)
        proc[1]['threads'][tid] = thread
        return thread

    def _fini_thread(self, proc, tid):
        '''
        Tear down a thread tufo by tid from the specified proc.
        '''
        return proc[1]['threads'].pop(tid,None)

    def reqThreadByTid(self, proc, tid):
        thread = proc[1]['threads'].get(tid)
        if thread == None:
            raise Exception('tid %d is not valid for pid %d' % (proc[0],tid))
        return thread

    def proc(self, pid):
        '''
        Return a proc tufo for a pid *without* attaching.
        '''
        return self._proc_forpid(pid)

    def attach(self, pid):
        proc = self._tgt_procs.get(pid)
        if proc != None:
            raise Exception('pid already attached: %s' % (pid,))

        proc = self._init_proc(pid)
        return self._proc_attach(proc)

    def kill(self, pid):
        proc = self.reqProcByPid(pid)
        return self._proc_kill(proc)

    def _init_proc(self, pid, **info):
        info['threads'] = {}
        proc = tufo(pid,**info)
        self._tgt_procs[pid] = proc
        return proc

    def run(self, pid, signo=None):
        '''
        Run the process until the next debug event.
        '''
        proc = self.reqProcByPid(pid)
        return self._proc_run(proc,signo=signo)

    def stop(self, pid):
        proc = self.reqProcByPid(pid)
        return self._proc_stop(proc)

    def detach(self, pid):
        proc = self.reqProcByPid(pid)
        return self._proc_detach(proc,addr,size)

    def peek(self, pid, addr, size):
        proc = self.reqProcByPid(pid)
        return self._proc_peek(proc,addr,size)

    def poke(self, pid, addr, mem):
        proc = self.reqProcByPid(pid)
        return self._proc_poke(proc,addr,mem)

    def mmaps(self, pid):
        proc = self.reqProcByPid(pid)
        return self._proc_mmaps(proc)

    def getregs(self, pid, tid):
        proc = self.reqProcByPid(pid)
        thread = self.reqThreadByTid(proc,tid)
        return self._proc_getregs(proc, thread)

    def setregs(self, pid, tid, regdict):
        proc = self.reqProcByPid(pid)
        thread = self.reqThreadByTid(proc,tid)
        self._proc_setregs(proc,thread,regdict)

    # methods for a platform to implement...

    def _proc_forpid(self, pid):
        raise ImplementMe()

    def _proc_kill(self, proc):
        raise ImplementMe()

    def _proc_run(self, proc, signo=None):
        raise ImplementMe()

    def _proc_getregs(self, proc, tid):
        raise ImplementMe()

    def _proc_setregs(self, proc, thread):
        raise ImplementMe()

    def _proc_mmaps(self, proc):
        raise ImplementMe()

    def _proc_peek(self, proc, addr, size):
        raise ImplementMe()

    def _proc_poke(self, proc, addr, mem):
        raise ImplementMe()

    def _proc_run(self, proc):
        raise ImplementMe()

    def _proc_stop(self, proc):
        raise ImplementMe()
