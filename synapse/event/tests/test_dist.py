import unittest
import synapse.event.dist as s_eventdist

class EventDistTest(unittest.TestCase):

    def test_event_dist_basic(self):
        d = s_eventdist.EventDist()
        self._run_eventdist(d)

    def test_event_dist_queue(self):
        d = s_eventdist.EventQueue()
        self._run_eventdist(d)

    def _run_eventdist(self, d):
        testdata = {}
        def ondone(event):
            testdata['ondone'] = True
            testdata['doneinfo'] = event[1].get('woot')

        def makeerr(event):
            testdata['makeerr'] = True
            raise Exception('makeerr')

        def onerr(event):
            testdata['onerr'] = True

        def onall(event):
            testdata['onall'] = True

        def onshut(event):
            testdata['onshut'] = True

        d.on('!',onerr)
        d.on('*',onall)
        d.on('$',onshut)
        d.on('ondone',ondone)
        d.on('makeerr',makeerr)

        d.fire('ondone', woot='woot')
        d.fire('makeerr', woot='woot')

        d.fini()

        self.assertTrue(testdata['ondone'])
        self.assertEqual(testdata['doneinfo'],'woot')
        self.assertTrue(testdata['onall'])

        self.assertTrue(testdata['onerr'])
        self.assertTrue(testdata['makeerr'])

        self.assertTrue(testdata['onshut'])
