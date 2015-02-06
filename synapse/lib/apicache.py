import time
import functools
import collections

'''
A utility module for caching API call results.

Example:

    import synapse.lib.apicache as s_apicache

    class woot(s_apicache.ApiCache):

        def __init__(self):
            s_apicache.ApiCache.__init__(self)

        @s_apicache.cacheapi
        def calcHeavyThing(self, x, y):
            return x + y # haha... "heavy" ;)

    w = woot()
    a = w.calcHeavyThing(30,40)

    # ... later

    x = w.calcHeavyThing(30,40) # this hit the cache!

Notes:
    The ApiCache object supports assigning "maxsize" for each
    API cache as well as a "timeout" which will clear cache
    elements which were requested "timeout" seconds ago or more.

'''

def cacheapi(f):
    '''
    A decorator which triggers API caching behavior.
    '''
    apiname = f.__name__

    def cachemeth(*args,**kwargs):

        callkey = (args[1:],tuple(kwargs.items()))
        cacheinfo = args[0]._cache_info.get(apiname)

        if cacheinfo == None:
            cacheinfo = cachedict()
            args[0]._cache_info[apiname] = cacheinfo

        fifo = cacheinfo['fifo']
        cache = cacheinfo['cache']

        cachehit = cache.get(callkey)

        now = time.time()

        # get possible config updates from cache info
        timeout = cacheinfo.get('timeout')

        # if we get a single timed out result, cull them all
        if timeout != None and cachehit != None and cachehit[0] + timeout < now:
            while fifo and fifo[0][0] + timeout > now:
                remhit = fifo.popleft()
                cache.pop(remhit[1],None)

            cachehit = None

        # if we dont have a hit here, lets go get one!
        if cachehit == None:
            retval = f(*args,**kwargs)

            cachehit = (time.time(),callkey,retval)

            fifo.append( cachehit )
            cache[callkey] = cachehit

            # on adding to the cache, we check if it's too big
            maxsize = cacheinfo.get('maxsize')
            if maxsize != None and len(fifo) > maxsize:
                while len(fifo) > maxsize:
                    remhit = fifo.popleft()
                    cache.pop(remhit[1],None) # pop the callkey tuple

        return cachehit[2] # retval

    functools.wraps(cachemeth,f)
    return cachemeth

class ApiCache:
    '''
    A base class for objects which implement API caching.

    Extending from this object allows classes to use the
    @cacheapi decorator to cache results from API calls.

    NOTE: use of the cacheapi decorator incurs a small
          overhead.  Only use where caching would be faster.
    '''

    def __init__(self):
        self._cache_info = {}

    def apiCacheList(self):
        '''
        Retrieve a list of apiname:cacheinfo tuples.
        '''
        return self._cache_info.items()

    def apiCacheClear(self,apiname=None):
        '''
        Flush cached results from the ApiCache.

        Caller may optionally specify an API name to flush
        a specific cache rather than all cached elements.
        '''
        if apiname == None:
            for cachename,cacheinfo in self._cache_info.items():
                cacheinfo['fifo'].clear()
                cacheinfo['cache'].clear()
            return
        
        cacheinfo = self._cache_info.get(apiname)
        if cacheinfo != None:
            cacheinfo['fifo'].clear()
            cacheinfo['cache'].clear()

        return

    def apiCacheSetInfo(self, apiname, name, valu):
        '''
        Set an element in the cacheinfo dict for a given API.

        This may be used to modify the maxsize and/or timeout for
        elements in an ApiCache.

        Example:

            x = CachedThing()
            x.apiCacheSetInfo('getThingByStuff','timeout',30)

            x.getThingByStuff() # never returns cache hits older than 30 seconds.

        '''
        cacheinfo = self._cache_info.get(apiname)
        if cacheinfo == None:
            cacheinfo = cachedict()
            self._cache_info[apiname] = cacheinfo
        cacheinfo[name] = valu

    def apiCacheGetInfo(self, apiname, name):
        '''
        Retrieve info from the cacheinfo dict for a given API.
        '''
        cacheinfo = self._cache_info.get(apiname)
        if cacheinfo == None:
            return None
        return cacheinfo.get(name)

def cachedict():
    return {'fifo':collections.deque(),'cache':{}}

