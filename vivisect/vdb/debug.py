
class DebugApi:

    def __init__(self, targ, **info):
        self._dbg_targ = targ
        self._dbg_info = info
        #self.ext object with proxy caller

    def getProcList(self):
        '''
        Retrieve a list of (pid,info) tuples for processes.

        Example:

            for pid,info in dbg.getProcList():
                print('pid: %d' % (pid,))

        '''
        return self._dbg_targ.getProcList()

    def getProcTrace(self, proc, attach=True):
        '''
        Retrieve a Trace instance for the given proc tuple.

        Caller may optionally specify attach=False to manually
        call attach.
        '''
        trace = self._proc_trace(proc)
        if attach:
            trace.attach()
        return trace

    def callExtApi(self, api, *args, **kwargs):
        '''
        Call an extended API on the DebugTarget.

        Example:

            dbg.callExtApi('woot',10,foo='blah')

        '''
        return self._dbg_targ.callExtApi(api,*args,**kwargs)

dbgctors = {
}

def addDebugApi(targ,ctor):
    '''
    Add a DebugApi ctor for a target name.

    Example:

        class MyDebugApi(DebugApi):
            ...

        addDebugApi('mything',MyDebugApi)

    '''
    dbgctors[targ] = ctor

def getDebugApi(targ='this',**info):
    '''
    Construct a new DebugApi object for the given target.

    Example:

        dbg = getDebugApi('vmware',port=8832)

    '''
    ctor = dbgctors.get(targ)
    if ctor == None:
        return ctor

    return ctor(**info)
