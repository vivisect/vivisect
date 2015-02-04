import unittest
import threading

import synapse.lib.threads as s_threads

class TestThreads(unittest.TestCase):

    def test_firethread(self):

        testdata = {}
        def workthread(x,foo=None):
            testdata['x'] = x
            testdata['foo'] = foo

        thr = s_threads.fireWorkThread(workthread,10,foo='woot')
        thr.join()

        self.assertEqual( testdata.get('x'), 10 )
        self.assertEqual( testdata.get('foo'), 'woot' )

    def test_rwlock_basic(self):

        testdata = {'order':[]}

        def writethread():
            testdata['order'].append('write')

        def readthread():
            testdata['order'].append('read')

        lock = s_threads.RWLock()

        threads = []
        with lock.reader():
            threads.append( s_threads.fireWorkThread(readthread) )
            threads.append( s_threads.fireWorkThread(readthread) )

            threads.append( s_threads.fireWorkThread(writethread) )
            threads.append( s_threads.fireWorkThread(writethread) )

        [ t.join() for t in threads ]
        self.assertEqual(testdata['order'],['read','read','write','write'])

    def test_rwlock_multiread(self):

        e = threading.Event()
        lock = s_threads.RWLock()

        def reader2():
            with lock.reader():
                e.set()

        with lock.reader():
            thr = s_threads.fireWorkThread(reader2)
            self.assertTrue( e.wait(3) )
            thr.join()
