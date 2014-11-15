import unittest

import vtrace.breakpoints

# TODO: move testmods.hookbptest tests in here as well.

class MockTrace(object):
    def getCurrentThread(self):
        return 0

class HookBpPostTests(unittest.TestCase):
    def test_PostHitNoCallinfo(self):
        '''
        tests condition where:
        1. thread 1 hits hookbp and sets up postbp
        2. thread 2 hits postbp (there's nothing in callinfo for thread 2)
        '''
        hbp = vtrace.breakpoints.HookBreakpoint('0xdeadbeef')
        phbp = vtrace.breakpoints.PostHookBreakpoint('0xcafebabe', hbp)

        phbp.notify(None, MockTrace())
