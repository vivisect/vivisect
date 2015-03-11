
class DebugTarget:

    def __init__(self, **info):
        self._tgt_info = info
        self._tgt_procs = {}
        self._tgt_extapis = {}

    def initProcEvent(self, evt, **evtinfo):
        return (evt,evtinfo)

    def reqProcByPid(self, pid):
        proc = self._tgt_procs.get(pid)
        if proc == None:
            raise Exception('pid is not attached: %s' % (pid,))
        return proc

    def procAttach(self, pid):
        proc = self._tgt_procs.get(pid)
        if proc != None:
            raise Exception('pid already attached: %s' % (pid,))

        proc = (pid,{})
        self._tgt_procs[pid] = proc

        return self._proc_attach(proc)

    def procRun(self, pid):
        '''
        Run the process until the next debug event.
        '''
        proc = self.reqProcByPid(pid)
        return self._proc_run(proc,addr,size)

    def procDetach(self, pid):
        proc = self.reqProcByPid(pid)
        return self._proc_detach(proc,addr,size)

    def procMemRead(self, pid, addr, size):
        proc = self.reqProcByPid(pid)
        return self._proc_memread(proc,addr,size)

    def procMemWrite(self, pid, addr, mem):
        proc = self.reqProcByPid(pid)
        return self._proc_memwrite(proc,addr,mem)

    def procMemMaps(self, pid):
        proc = self.reqProcByPid(pid)
        return self._proc_memmaps(proc,addr,mem)

    def addExtApi(self, api, func):
        self._tgt_extapis[api] = func

    def callExtApi(self, api, *args, **kwargs):
        meth = self._tgt_extapis.get(api)
        if meth == None:
            raise Exception('Unknown Ext Api: %s' % (api,))

    def getProcList(self):
        print('WOOT')
        return [(0,{'name':'woot'})]

