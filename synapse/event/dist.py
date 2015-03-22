'''
Classes which implement local multi-consumer event distribution.
'''
import traceback
import collections

import synapse.lib.queue as s_queue
import synapse.lib.threads as s_threads

from vertex.lib.common import tufo

class EventDist:
    '''
    Local event distributor.

    Special Event Names:

    *   - called on all event fires
    !   - called on event callback error
    $   - called on event dist shutdown
    '''
    def __init__(self):
        self._syn_asplode = False   # should we explode on cb exception?
        self._syn_verbose = False   # should we traceback on cb exception?
        self._syn_handlers = collections.defaultdict(list)

    def _synFireCallbacks(self, cblist, event):
        for cb in cblist:

            try:
                cb(event)

            except Exception as e:

                if self._syn_asplode:
                    raise e

                if self._syn_verbose:
                    traceback.print_exc()

                errevent = tufo('!', event=event, exc=e)
                for errcb in self._syn_handlers.get('!',()):
                    try:
                        errcb(errevent)
                    except Exception as e:
                        traceback.print_exc()

    def fini(self):
        '''
        Call this API when you are done with the event dist.

        Example:

            d.fini()

        '''
        cblist = self._syn_handlers.get('$')
        if cblist != None:
            self._synFireCallbacks(cblist,tufo('$'))

        self._syn_handlers.clear()

    def fire(self, evt, **evtinfo):
        '''
        Fire a single event on the EventDist.

        Example:

            bus.fire('woot', foo='bar')

        '''
        event = (evt,evtinfo)
        return self.dist(event)

    def dist(self, event):
        '''
        Re-distribute an existing event tufo.

        Example:

            d1 = EventDist()
            d2 = EventDist()

            d1.on('*', d2.dist)

            # all events in d1 will also be seen in d2

        '''
        cblist = self._syn_handlers.get(event[0])
        if cblist != None:
            self._synFireCallbacks(cblist,event)

        cblist = self._syn_handlers.get('*')
        if cblist != None:
            self._synFireCallbacks(cblist,event)

    def distall(self, events):
        '''
        Re-distribute all events from the given iterable.


        Example:

            events = getFooEvents()

            bus.distall(events)

        '''
        [ self.dist(e) for e in events ]

    def on(self, name, callback):
        '''
        Add an event handler callback by name.

        Example:
            def my_handler(event):
                dostuff()

            bus.on('woot',my_handler)
        '''
        self._syn_handlers[name].append(callback)

    def link(self, bus):
        '''
        Link this EventDist to another ( one way ).

        Example:

            d1 = EventDist()
            d2 = EventDist()

            d1.link( d2 )

            # all d1 events propigate to d2
            # but not the other way ( loop! )

        '''
        self.on('*', bus.dist)

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

    An EventQueue allows fire() to queue events to an
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

    def fire(self, evt, **evtinfo):
        self.que.put( (evt,evtinfo) )

    def fini(self):
        [ self.que.append(None) for t in self.threads ]
        [ t.join() for t in self.threads ]
        self.que.shutdown()
        return EventDist.fini(self)

    def _runEventLoop(self):
        for event in self.que:
            if event == None:
                break

            evt,evtinfo = event
            EventDist.fire(self, evt, **evtinfo)
