import logging

logger = logging.getLogger(__name__)


class CobraDispatchMethod:
    '''
    implements use of async cobra calls
    '''
    def __init__(self, dispatcher, methname):
        self.dispatcher = dispatcher
        self.methname = methname

    def __call__(self, *args, **kwargs):
        logger.debug("Calling: %s (%s, %s)", self.methname, repr(args)[:20], repr(kwargs)[:20])
        waiters = []

        try:
            for proxy in self.dispatcher.getCobraProxies():
                waiters.append(getattr(proxy, self.methname)(*args, _cobra_async=True, **kwargs))
            return [waiter.wait() for waiter in waiters]
        except Exception:
            for waiter in waiters:
                if waiter.csock:
                    waiter.csock.trashed = True
            raise
        finally:
            for waiter in waiters:
                if waiter.csock and waiter.csock.pool is not None:
                    waiter.csock.pool.put(waiter.csock)


class CobraDispatcher:
    '''
    class implements logic around making async calls
    to multiple cobra proxies. specifically enforces requeuing
    of socket objects when proxy uses sockpool. list of proxies
    can be a mix of proxies with different settings.
    '''
    def __init__(self, proxies):
        self._cobra_proxies = proxies

    def addCobraProxy(self, proxy):
        self._cobra_proxies.append(proxy)

    def delCobraProxy(self, proxy):
        self._cobra_proxies.remove(proxy)

    def getCobraProxies(self):
        return self._cobra_proxies

    def __getattr__(self, name):
        logger.debug("getattr %s", name)

        if name == "__getinitargs__":
            raise AttributeError()

        self._cobra_methods = self._cobra_proxies[0]._cobra_methods
        self._cobra_name = self._cobra_proxies[0]._cobra_name
        # Handle methods
        if self._cobra_methods.get(name, False):
            meth = CobraDispatchMethod(self, name)
            setattr(self, name, meth)
            return meth
