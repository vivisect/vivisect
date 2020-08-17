'''
A couple useful thread related toys...
'''
import time
import logging
import threading
import functools
import collections

import envi.exc as e_exc

logger = logging.getLogger(__name__)

def firethread(func):
    '''
    A decorator which fires a thread to do the given call.

    NOTE: This means these methods may not return anything
    and callers may not expect sync behavior!
    '''
    def dothread(*args, **kwargs):
        thr = threading.Thread(target=func, args=args, kwargs=kwargs)
        thr.setDaemon(True)
        thr.start()
        return thr
    functools.update_wrapper(dothread, func)
    return dothread


def maintthread(stime):
    '''
    A decorator which will act as a maintenance loop by calling
    back the wrapped function ( in a thread fired for this purpose )
    every "stime" seconds.
    '''
    def maintwrap(func):

        def maintloop(*args, **kwargs):
            while True:
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    logger.warning('MaintThread (%s) Error: %s', args[0], e)
                time.sleep(stime)

        def dothread(*args, **kwargs):
            thr = threading.Thread(target=maintloop, args=args, kwargs=kwargs)
            thr.setDaemon(True)
            thr.start()

        functools.update_wrapper(dothread, func)
        return dothread

    return maintwrap


class ChunkQueue:
    '''
    This is a Queue like object which returns *all* pending items
    when requested to minimize round tripping.  It's also keeps track
    of client checkins to help identify "abandonment" behaviors.
    '''
    def __init__(self, items=None):
        self.shut = False
        self.last = time.time()
        self.lock = threading.Lock()
        self.event = threading.Event()
        if items is None:
            items = []
        self.items = items

    def shutdown(self):
        self.shut = True
        self.event.set()

    def abandoned(self, dtime):
        now = time.time()
        return now > (self.last + dtime)

    def append(self, x):
        if self.shut:
            raise e_exc.QueueShutdown()
        with self.lock:
            self.items.append(x)
            self.event.set()

    def prepend(self, x):
        # NOTE: this is heavy, use judiciously
        if self.shut:
            raise e_exc.QueueShutdown()
        with self.lock:
            self.items.insert(0,x)
            self.event.set()

    def extend(self, x):
        if self.shut:
            raise e_exc.QueueShutdown()
        with self.lock:
            self.items.extend(x)
            self.event.set()

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        try:
            while True:
                for i in self.get(timeout=1):
                    yield i
        except e_exc.QueueShutdown as e:
            pass

    def put(self, item):
        if self.shut:
            raise e_exc.QueueShutdown()
        self.append( item )

    def get(self, timeout=None):
        self.last = time.time()
        with self.lock:
            if self.items:
                return self._get_items()

            if self.shut:
                raise e_exc.QueueShutdown()

            # Clear the event so we can wait...
            self.event.clear()

        self.event.wait(timeout=timeout)
        if self.shut:
            raise e_exc.QueueShutdown()
        with self.lock:
            self.last = time.time()
            if not self.items and self.shut:
                raise e_exc.QueueShutdown()
            return self._get_items()

    def peek(self):
        return list(self.items)

    def _get_items(self):
        ret = self.items
        self.items = []
        return ret

class EnviQueue:
    '''
    A deterministic Queue that doesn't suck.
    '''
    def __init__(self, items=None):
        self.shut = False
        self.last = time.time()
        self.lock = threading.Lock()
        self.event = threading.Event()
        if items is None:
            items = []
        self.items = collections.deque(items)

    def abandoned(self, dtime):
        now = time.time()
        return now > (self.last + dtime)

    def shutdown(self):
        self.shut = True
        self.event.set()

    def append(self, x):
        if self.shut:
            raise e_exc.QueueShutdown()
        with self.lock:
            self.items.append(x)
            self.event.set()

    def prepend(self, x):
        if self.shut:
            raise e_exc.QueueShutdown()
        with self.lock:
            self.items.appendleft(x)
            self.event.set()

    def extend(self, x):
        if self.shut:
            raise e_exc.QueueShutdown()
        with self.lock:
            self.items.extend(x)
            self.event.set()

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        if self.shut:
            raise e_exc.QueueShutdown()
        try:
            while True:
                ret = self.get()
                yield ret
        except e_exc.QueueShutdown as e:
            pass

    def put(self, x):
        self.append(x)

    def get(self, timeout=None):
        start = time.time()
        self.last = start

        while True:
            if self.shut:
                raise e_exc.QueueShutdown()

            with self.lock:
                if self.items:
                    return self.items.popleft()

                # Clear the event so we can wait...
                self.event.clear()

            deltat = None
            if timeout:
                deltat = max(0, timeout - (time.time() - start))

            if not self.event.wait(timeout=deltat):
                return None
