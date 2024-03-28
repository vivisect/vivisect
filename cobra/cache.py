'''
An API implementing a few caching utilities.
( use carefully! caches are dangerous ;) )
'''
from functools import wraps
from collections import deque

class FixedDepthCache:
    '''
    A fixed depth cache.
    '''
    def __init__(self, depth, misscb=None, finicb=None):
        self.cache = {}
        self.depth = depth
        self.cdeque = deque()

        self.misscb = misscb
        self.finicb = finicb

    def clear(self):
        '''
        Clear all the elements of the cache.
        '''
        self.cache.clear()
        self.cdeque.clear()

    def get(self, key, default=None):
        '''
        Retrieve the given key's value in the cache.
        '''
        if key not in self.cache and self.misscb:
            val = self.misscb(key)
            self.put(key, val)
            return val

        return self.cache.get(key, default)

    def put(self, key, value):
        '''
        Insert the given key/value pair into the cache.
        '''
        self.cache[key] = value
        self.cdeque.append(key)
        while len(self.cdeque) > self.depth:
            popkey = self.cdeque.popleft()
            popval = self.cache.pop(popkey, None)
            if self.finicb:
                self.finicb(popkey, popval)

    def pop(self):
        key = self.cdeque.popleft()
        val = self.cache.pop(key)
        return (key, val)

    def has(self, key):
        return key in self.cache

    def __len__(self):
        return len(self.cdeque)

def cachefunc(depth):
    cache = FixedDepthCache(depth)

    def wrapdef(f):

        @wraps(f)
        def funcdef(*args):
            if not cache.has( args ):
                ret = f(*args)
                cache.put(args,ret)
                return ret
            return cache.get(args)

        return funcdef

    return wrapdef
