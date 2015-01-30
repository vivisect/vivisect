import unittest

import synapse.lib.queue as s_queue

class QueueTest(unittest.TestCase):

    def test_queue_basic(self):
        q = s_queue.Queue()
        q.put('woot')

        self.assertEqual(q.get(),'woot')
        self.assertFalse(q.abandoned(10))

    def test_queue_prepend(self):
        q = s_queue.Queue()
        q.put('foo')
        q.prepend('bar')

        self.assertEqual(q.get(),'bar')
        self.assertEqual(q.get(),'foo')

    def test_queue_extend(self):
        q = s_queue.Queue()
        q.extend(['foo','bar'])

        self.assertEqual(q.get(),'foo')
        self.assertEqual(q.get(),'bar')

# FIXME lots more tests to write here...
