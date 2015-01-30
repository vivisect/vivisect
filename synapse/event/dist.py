'''
Classes which implement local multi-consumer event distribution.
'''
import traceback
import collections

import synapse.lib.queue as s_queue
import synapse.lib.threads as s_threads

class EventDist:
    '''
    Local event distributor.

    Special Event Names:

    *   - called on all event fires
    !   - called on event callback error
    $   - called on event dist shutdown
    '''
    def __init__(self):
        self._syn_verbose = False
        self._syn_handlers = collections.defaultdict(list)

    def _synFireCallbacks(self, cblist, evt, evtinfo):
        for cb in cblist:
            try:
                cb(evt,evtinfo)
            except Exception as e:
                if self._syn_verbose:
                    traceback.print_exc()
                evtinfo = {'evt':evt,'evtinfo':evtinfo,'exc':e}
                for errcb in self._syn_handlers.get('!',[]):
                    try:
                        errcb('!',evtinfo)
                    except Exception as e:
                        traceback.print_exc()

    def synShutDown(self):
        '''
        Call this API when you are done with the event dist.

        Example:
            d.synShutDown()
        '''
        cblist = self._syn_handlers.get('$')
        if cblist != None:
            self._synFireCallbacks(cblist,'$',{})

        self._syn_handlers.clear()

    def synFireEvent(self, evt, evtinfo):
        '''
        Fire a single event through the callbacks.

        NOTE: the calling thread's context *is* used
              to execute 
        '''
        cblist = self._syn_handlers.get(evt)
        if cblist != None:
            self._synFireCallbacks(cblist,evt,evtinfo)

        cblist = self._syn_handlers.get('*')
        if cblist != None:
            self._synFireCallbacks(cblist,evt,evtinfo)

    def synAddHandler(self, name, callback):
        '''
        Add an event handler callback.

        Example:
            def my_handler(evt,evtinfo):
                dostuff()

            s.synAddHandler('woot',my_handler)
        '''
        self._syn_handlers[name].append(callback)

    #def synDelHandler

    def synPopHandlers(self, name):
        '''
        Remove all handlers for a given event name.

        Example:
            s.synPopHandlers('woot')
        '''
        return self._syn_handlers.pop(name,None)

class EventQueue(EventDist):
    '''
    EventQueue extends EventDist using a callback thread.

    An EventQueue allows synFireEvent to queue events to an
    internal consumer thread in order to avoid using the calling
    thread to execute callbacks.
    '''
    def __init__(self,pool=1):
        EventDist.__init__(self)
        self.que = s_queue.Queue()
        self.pool = pool
        self.threads = []
        for i in range(pool):
            thr = s_threads.fireWorkThread(self._runEventLoop)
            self.threads.append(thr)

    def synFireEvent(self, evt, evtinfo):
        self.que.put( (evt,evtinfo) )

    def synShutDown(self):
        for i in range(self.pool):
            self.que.append(None)
        for thr in self.threads:
            thr.join()
        return EventDist.synShutDown(self)

    def _runEventLoop(self):
        for e in self.que:
            if e == None:
                self.que.shutdown()
                return
            EventDist.synFireEvent(self, *e)
