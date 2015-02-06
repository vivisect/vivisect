import time
import unittest

import synapse.lib.apicache as s_apicache

class ApiCacheTest(unittest.TestCase):

    def test_apicache_basic(self):

        testdata = {'foo':0,'bar':0}
        class woot(s_apicache.ApiCache):

            @s_apicache.cacheapi
            def foo(self, x, y):
                testdata['foo'] += 1
                return x + y

            @s_apicache.cacheapi
            def bar(self, x, y=10):
                testdata['bar'] += 1
                return x + y

        w = woot()

        self.assertEqual( w.foo(30,40), 70 )
        self.assertEqual( testdata['foo'], 1 )

        self.assertEqual( w.foo(30,40), 70 )
        self.assertEqual( testdata['foo'], 1 )

        self.assertEqual( w.foo(40,40), 80 )
        self.assertEqual( testdata['foo'], 2 )

        self.assertEqual( testdata['bar'], 0 )

        self.assertEqual( w.bar(30,y=40), 70 )
        self.assertEqual( testdata['bar'], 1 )

        self.assertEqual( w.bar(30,y=40), 70 )
        self.assertEqual( testdata['bar'], 1 )

    def test_apicache_timeout(self):
        '''
        Confirm that items are bumped from the cache if they are too old
        '''
        testdata = {'foo':0}

        class woot(s_apicache.ApiCache):

            @s_apicache.cacheapi
            def foo(self, x, y):
                testdata['foo'] += 1
                return x + y

        w = woot()
        w.apiCacheSetInfo('foo','timeout',0.1)

        w.foo(20,30)
        w.foo(20,30)

        self.assertEqual(testdata['foo'], 1)

        time.sleep(0.2)

        w.foo(20,30)
        self.assertEqual(testdata['foo'], 2)

    def test_apicache_maxsize(self):
        '''
        Confirm that items are bumped from the cache if it's too big
        '''
        testdata = {'foo':0}

        class woot(s_apicache.ApiCache):
            @s_apicache.cacheapi
            def foo(self, x, y):
                testdata['foo'] += 1
                return x + y

        w = woot()
        w.apiCacheSetInfo('foo','maxsize',2)

        w.foo(10,20)
        w.foo(20,30)

        self.assertEqual(testdata['foo'], 2)

        w.foo(10,20)
        w.foo(20,30)

        self.assertEqual(testdata['foo'], 2)

        w.foo(30,40)
        self.assertEqual(testdata['foo'], 3)

        w.foo(20,30)
        self.assertEqual(testdata['foo'], 3)

        w.foo(10,20)
        self.assertEqual(testdata['foo'], 4)

    def test_apicache_clear(self):
        '''
        Confirm that items are bumped from the cache if it's too big
        '''
        testdata = {'foo':0}

        class woot(s_apicache.ApiCache):
            @s_apicache.cacheapi
            def foo(self, x, y):
                testdata['foo'] += 1
                return x + y

        w = woot()

        w.foo(10,20)
        self.assertEqual(testdata['foo'], 1)

        w.apiCacheClear('foo')

        w.foo(10,20)
        self.assertEqual(testdata['foo'], 2)

        w.apiCacheClear()

        w.foo(10,20)
        self.assertEqual(testdata['foo'], 3)
