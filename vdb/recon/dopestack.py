'''
A quick set of tools for doing stack doping.
'''
import vtrace

def dopeThreadStack(trace, threadid):
    curthread = trace.getCurrentThread()
    try:
        trace.selectThread(threadid)
        sp = trace.getStackCounter()
        mmap = trace.getMemoryMap(sp)
        if mmap == None:
            raise Exception('Thread %d has invalid stack pointer 0x%.8x' % (threadid, sp))

        mapva, mapsize, mperms, mfname = mmap

        dopesize = sp - mapva
        trace.writeMemory(mapva, 'V' * dopesize)

    except Exception, e:
        print 'dopeThreadStack Failed On %d' % threadid
        trace.selectThread(curthread)

def dopeAllThreadStacks(trace):
    '''
    Apply stack doping to all thread stacks.
    '''
    for threadid in trace.getThreads().keys():
        dopeThreadStack(trace, threadid)

class ThreadDopeNotifier(vtrace.Notifier):

    def notify(self, event, trace):
        dopeAllThreadStacks(trace)

dopenotif = ThreadDopeNotifier()

def enableEventDoping(trace):
    trace.registerNotifier(vtrace.NOTIFY_CONTINUE, dopenotif)

def disableEventDoping(trace):
    trace.deregisterNotifier(vtrace.NOTIFY_CONTINUE, dopenotif)

