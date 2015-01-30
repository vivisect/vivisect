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
        def ondone(evt,evtinfo):
            testdata['ondone'] = True
            testdata['doneinfo'] = evtinfo.get('woot')

        def makeerr(evt,evtinfo):
            testdata['makeerr'] = True
            raise Exception('makeerr')

        def onerr(evt,evtinfo):
            testdata['onerr'] = True

        def onall(evt,evtinfo):
            testdata['onall'] = True

        def onshut(evt,evtinfo):
            testdata['onshut'] = True

        d.synAddHandler('!',onerr)
        d.synAddHandler('*',onall)
        d.synAddHandler('$',onshut)
        d.synAddHandler('ondone',ondone)
        d.synAddHandler('makeerr',makeerr)
        d.synFireEvent('ondone',{'woot':'woot'})
        d.synFireEvent('makeerr',{'woot':'woot'})

        d.synShutDown()

        self.assertTrue(testdata['ondone'])
        self.assertEqual(testdata['doneinfo'],'woot')
        self.assertTrue(testdata['onall'])

        self.assertTrue(testdata['onerr'])
        self.assertTrue(testdata['makeerr'])

        self.assertTrue(testdata['onshut'])
