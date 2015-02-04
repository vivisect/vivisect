import os
import threading
import collections

def getThreadLocal(name,ctor,*args,**kwargs):
    '''
    Retrieve or construct a thread local variable.
    ( useful "ctor" mechanism which threading.local is missing )
    '''
    thr = threading.currentThread()
    synlocs = getattr(thr,'_syn_locals',None)
    if synlocs == None:
        synlocs = {}
        thr._syn_locals = synlocs

    ret = synlocs.get(name)
    if ret == None:
        ret = ctor(*args,**kwargs)
        synlocs[name] = ret

    return ret

def fireWorkThread(func,*args,**kwargs):
    thr = threading.Thread(target=func,args=args,kwargs=kwargs)
    thr.setDaemon(True)
    thr.start()
    return thr

class RWLock:
    '''
    A multi-reader/exclusive-writer lock.
    '''
    def __init__(self):
        self.lock = threading.Lock()
        self.ident = os.urandom(16)

        self.rw_holder = None
        self.ro_holders = set()

        self.ro_waiters = collections.deque()
        self.rw_waiters = collections.deque()

    def reader(self):
        # use thread locals with our GUID for holder ident
        holder = getThreadLocal(self.ident,RWWith,self)

        holder.event.clear()
        holder.writer = False

        with self.lock:

            # if there's no rw holder, off we go!
            if not self.rw_holder and not self.rw_waiters:
                self.ro_holders.add( holder )
                return holder

            self.ro_waiters.append(holder)

        holder.event.wait() # FIXME timeout
        return holder

    def writer(self):
        '''
        Acquire an exclusive write lock on the given RWLock.
        '''
        holder = getThreadLocal(self.ident,RWWith,self)

        holder.event.clear()
        holder.writer = True

        with self.lock:

            if not self.rw_holder and not self.ro_holders:
                self.rw_holder = holder
                return holder

            self.rw_waiters.append( holder )

        holder.event.wait() # FIXME timeout
        return holder

    def release(self, holder):

        with self.lock:

            if holder.writer:
                self.rw_holder = None

                # a write lock release should free readers first...
                if self.ro_waiters:
                    while self.ro_waiters:
                        nexthold = self.ro_waiters.popleft()
                        self.ro_holders.add( nexthold )
                        hexthold.event.set()
                    return

                if self.rw_waiters:
                    nexthold = self.rw_waiters.popleft()
                    self.rw_holder = nexthold
                    nexthold.event.set()
                    return

                return

            # releasing a read hold from here down...
            self.ro_holders.remove( holder )
            if self.ro_holders:
                return

            # the last reader should release a writer first
            if self.rw_waiters:
                nexthold = self.rw_waiters.popleft()
                self.rw_holder = nexthold
                nexthold.event.set()
                return

            # there should be no waiting readers here...
            return

class RWWith:

    def __init__(self, rwlock):
        self.event = threading.Event()
        self.writer = False
        self.rwlock = rwlock

    def __enter__(self):
        return self

    def __exit__(self, exclass, exc, tb):
        self.rwlock.release(self)

