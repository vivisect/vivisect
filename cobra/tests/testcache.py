import os
import unittest

import cobra.cache as c_cache

class CobraCacheTest(unittest.TestCase):

    #def setUp(self):
        #pass

    #def tearDown(self):
        #pass

    def test_cobra_cache_basic(self):
        cache = c_cache.FixedDepthCache( 5 )
        for i in range(10):
            cache.put(i, 'I: %d' % i)

        self.assertEqual( cache.get(0), None)
        self.assertEqual( cache.get(9), 'I: 9')

    def test_cobra_cache_misscb(self):

        def misscb(x):
            return 'X: %d' % x

        cache = c_cache.FixedDepthCache( 5, misscb=misscb )
        self.assertEqual( cache.get(33), 'X: 33')

    def test_cobra_cache_size(self):

        cache = c_cache.FixedDepthCache( 5 )
        for i in range(10):
            cache.put(i, 'I: %d' % i)

        self.assertEqual( len(cache), 5 )

    def test_cobra_cache_cachefunc(self):

        d = {'hits':0}
        @c_cache.cachefunc(10)
        def cacheme():
            d['hits'] += 1

        cacheme()
        cacheme()

        self.assertEqual( d['hits'], 1 )

