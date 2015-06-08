import os
import socket
import getpass

import synapse.lib.queue as s_queue
import synapse.lib.threads as s_threads
import vivisect.lib.thishost as v_thishost

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
        self._tgt_traces = {}
        self._tgt_extapis = {}

        self._tgt_pidq = {}
        self._tgt_pidt = {}

    def getDebugInfo(self):
        '''
        Retrieve the initial info for the Debugger info dict.

        By Convention:

        pid     - the pid of the DebugTarget
        user    - the user the debugger is running as
        host    - the host name of the DebugTarget
        path    - the current dir of the DebugTarget
        '''
        info = {
            'pid':os.getpid(),
            'user':getpass.getuser(),
            'host':socket.gethostname(),
            'path':os.path.abspath( os.curdir ),

            'arch':v_thishost.get('arch'),
            'format':v_thishost.get('format'),
            'platform':v_thishost.get('platform'),
        }
        return info

    def getTargInfo(self, prop, default=None):
        '''
        Retrieve a value from the target info dict.
        '''
        return self._tgt_info.get(prop,default)

    def setTargInfo(self, prop, valu):
        '''
        Set a value in the DebugTarget info dict.
        '''
        self._tgt_info[prop] = valu

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

        Example:

            def woot(x):
                dostuff(x)
                return 'hi'

            retval = tgt.callPidThread(pid, woot, 10)
            # retval == 'hi' but was executed in pid thread

        '''
        retq = s_threads.getThreadLocal('_pid_retq',s_queue.Queue)
        pidq = self._tgt_pidq.get(pid)

        pidq.put( (retq,func,args,kwargs) )

        ret = retq.get()
        if isinstance(ret,Exception):
            raise ret

        return ret

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

    def putFileBytes(self, path, byts):
        with open(path,'wb') as fd:
            fd.write( byts )

    def reqTraceProc(self, pid):
        info = self._tgt_traces.get(pid)
        if info == None:
            raise Exception('pid is not attached: %s' % (pid,))
        return info

    def _initProcThread(self, proc, tid, **info):
        '''
        Initialize a thread tufo for the specified proc.
        ( used only target side )
        '''
        thread = (tid,info)
        proc[1]['threads'][tid] = thread
        return thread

    def _finiProcThread(self, proc, tid):
        '''
        Tear down a thread tufo by tid from the specified proc.
        '''
        return proc[1]['threads'].pop(tid,None)

    def reqThreadByTid(self, proc, tid):
        thread = proc[1]['threads'].get(tid)
        if thread == None:
            raise Exception('tid %d is not valid for pid %d' % (proc[0],tid))
        return thread

    def getProcByPid(self, pid):
        '''
        Return a proc tuple (pid,info) for the given pid.

        Example:

            proc = tgt.getProcByPid(pid)

        '''
        return self._getProcByPid(pid)

    def getProcList(self):
        return self._getProcList()

    def traceAttach(self, pid):
        proc = self._tgt_traces.get(pid)
        if proc != None:
            raise Exception('pid already attached: %s' % (pid,))

        proc = self._initTraceProc(pid)
        return self._traceAttach(proc)

    def traceExec(self, cmdline, **opts):
        return self._traceExec(cmdline, **opts)

    def traceKill(self, pid):
        proc = self.reqTraceProc(pid)
        return self._traceKill(proc)

    def _initTraceProc(self, pid, **info):
        info['threads'] = {}
        proc = tufo(pid,**info)
        self._tgt_traces[pid] = proc
        return proc

    def traceRun(self, pid, signo=None):
        '''
        Run the process until the next debug event.
        '''
        proc = self.reqTraceProc(pid)
        return self._traceRun(proc,signo=signo)

    def traceStop(self, pid):
        proc = self.reqTraceProc(pid)
        return self._traceStop(proc)

    def traceDetach(self, pid):
        proc = self.reqTraceProc(pid)
        return self._traceDetach(proc,addr,size)

    def traceReadMemory(self, pid, addr, size):
        proc = self.reqTraceProc(pid)
        return self._traceReadMemory(proc,addr,size)

    def traceWriteMemory(self, pid, addr, byts):
        proc = self.reqTraceProc(pid)
        return self._traceWriteMemory(proc,addr,byts)

    def traceGetMemoryMaps(self, pid):
        proc = self.reqTraceProc(pid)
        return self._traceGetMemoryMaps(proc)

    def traceGetRegs(self, pid, tid):
        proc = self.reqTraceProc(pid)
        thread = self.reqThreadByTid(proc,tid)
        return self._traceGetRegs(proc, thread)

    def traceSetRegs(self, pid, tid, regs):
        trac = self.reqTraceProc(pid)
        thread = self.reqThreadByTid(proc,tid)
        self._traceSetRegs(proc,thread,regs)

    # methods for a platform to implement...

    def _getProcByPid(self, pid):
        raise ImplementMe()

    def _traceKill(self, proc):
        raise ImplementMe()

    def _traceRun(self, proc, signo=None):
        raise ImplementMe()

    def _traceGetRegs(self, proc, tid):
        raise ImplementMe()

    def _traceSetRegs(self, proc, thread, regs):
        raise ImplementMe()

    def _traceGetMemoryMaps(self, proc):
        raise ImplementMe()

    def _traceReadMemory(self, proc, addr, size):
        raise ImplementMe()

    def _traceWriteMemory(self, proc, addr, mem):
        raise ImplementMe()

    def _traceStop(self, proc):
        raise ImplementMe()
