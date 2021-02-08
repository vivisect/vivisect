import unittest

import cobra.devent as c_devent

class CobraEventTest(unittest.TestCase):

    #def setUp(self):
        #pass

    #def tearDown(self):
        #pass

    def test_cobra_devent(self):

        eventcore = c_devent.CobraEventCore()
        chan = eventcore.initEventChannel()
        eventcore.fireEvent('blah',(1,2,3))
        etup = eventcore.getNextEventsForChan(chan)[0]
        self.assertEqual(etup[0], 'blah')

    def test_cobra_devent_timeout(self):
        eventcore = c_devent.CobraEventCore()
        chan = eventcore.initEventChannel()
        self.assertFalse( eventcore.getNextEventsForChan( chan, timeout=0.01 ) )
