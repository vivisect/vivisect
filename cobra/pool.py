import time
import logging
import collections

import cobra

logger = logging.getLogger(__name__)


class PoolMethod(cobra.CobraMethod):
    def __init__(self, pool, methname):
        cobra.CobraMethod.__init__(self, None, methname)
        self._cobra_pool = pool

    def __call__(self, *args, **kwargs):
        proxy = self._cobra_pool.cobraPoolGetProxy(rotate=self._cobra_pool.loadbalance)
        while True:
            try:
                return getattr(proxy, self.methname)(*args, **kwargs)
            except cobra.CobraException as e:
                logger.warning('CobraPool Method Failure: %s %s', proxy._cobra_uri, e)
                proxy = self._cobra_pool.cobraPoolGetProxy(rotate=True)


class CobraPool:
    '''
    A transparent "pool" of cobra proxies with failure,
    load balancing, and data agregation capabilties.

    NOTE: by default, all CobraExceptions are "failures".
          ( this means auth fail etc may be masked! )
    '''
    def __init__(self, uris, loadbalance=False):
        self.uris = collections.deque([str(u) for u in uris])
        self.faildelay = 1
        self.proxycache = {}
        self.loadbalance = loadbalance

    def __getattr__(self, name):
        proxy = self.cobraPoolGetProxy()
        if proxy._cobra_methods.get(name, False):
            poolmeth = PoolMethod(self, name)
            setattr(self, name, poolmeth)
            return poolmeth
        raise AttributeError('no such method: %s' % name)

    def cobraPoolAddUri(self, uri):
        '''
        Add a URI to this CobraPool.
        '''
        self.uris.append(uri)

    def cobraPoolGetProxy(self, rotate=False):
        if rotate:
            self.uris.rotate(1)

        while True:
            try:

                uri = self.uris[0]
                proxy = self.proxycache.get(uri)
                if proxy is None:
                    proxy = cobra.CobraProxy(uri)
                    self.proxycache[uri] = proxy
                return proxy
            except Exception as e:
                self.uris.rotate(1)
                logger.warning('CobraPool Proxy Failure: %s %s', uri, e)
                time.sleep(self.faildelay)  # FIXME track per?
