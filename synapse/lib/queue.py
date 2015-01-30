'''
Utilitized queue objects that suck less than python's
'''
import time
import threading
import collections

class QueueShutdown(Exception): pass

class Queue:
    '''
    A Queue with a few bells and whistles
    '''
    def __init__(self, items=None):
        self.shut = False
        self.last = time.time()
        self.lock = threading.Lock()
        self.event = threading.Event()
        if items == None:
            items = []
        self.items = collections.deque(items)

    def abandoned(self, dtime):
        now = time.time()
        return now > (self.last + dtime)

    def shutdown(self):
        self.shut = True
        self.event.set()

    def append(self, x):
        if self.shut: raise QueueShutdown()
        with self.lock:
            self.items.append(x)
            self.event.set()

    def prepend(self, x):
        if self.shut: raise QueueShutdown()
        with self.lock:
            self.items.appendleft(x)
            self.event.set()

    def extend(self, x):
        if self.shut: raise QueueShutdown()
        with self.lock:
            self.items.extend(x)
            self.event.set()

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        if self.shut: raise QueueShutdown()
        try:
            while True:
                ret = self.get()
                yield ret
        except QueueShutdown as e:
            pass

    def put(self, x):
        self.append(x)

    def get(self, timeout=None):
        start = time.time()
        self.last = start

        while True:
            if self.shut: raise QueueShutdown()

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
        if items == None:
            items = []
        self.items = items

    def shutdown(self):
        self.shut = True
        self.event.set()

    def abandoned(self, dtime):
        now = time.time()
        return now > (self.last + dtime)

    def append(self, x):
        if self.shut: raise QueueShutdown()
        with self.lock:
            self.items.append(x)
            self.event.set()

    def prepend(self, x):
        # NOTE: this is heavy, use judiciously
        if self.shut: raise QueueShutdown()
        with self.lock:
            self.items.insert(0,x)
            self.event.set()

    def extend(self, x):
        if self.shut: raise QueueShutdown()
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
        except QueueShutdown as e:
            pass

    def put(self, item):
        if self.shut: raise QueueShutdown()
        self.append( item )

    def get(self, timeout=None):
        self.last = time.time()
        with self.lock:
            if self.items:
                return self._get_items()

            if self.shut: raise QueueShutdown()

            # Clear the event so we can wait...
            self.event.clear()

        self.event.wait(timeout=timeout)
        if self.shut: raise QueueShutdown()
        with self.lock:
            self.last = time.time()
            if not self.items and self.shut:
                raise QueueShutdown()
            return self._get_items()

    def peek(self):
        return list(self.items)

    def _get_items(self):
        ret = self.items
        self.items = []
        return ret

