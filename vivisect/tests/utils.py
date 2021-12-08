import unittest
import contextlib

import vivisect.cli as v_cli

class VivTest(unittest.TestCase):
    '''
    Base class for vivisect unit tests so that we have a common place to throw certain common
    utilities.
    '''

    def eq(self, x, y):
        '''
        Assert x is equal to y
        '''
        self.assertEqual(x, y)

    def len(self, x, y):
        '''
        Assert that length of x is equal to y
        '''
        self.assertEqual(len(x), y)

    def none(self, x):
        '''
        Assert x is none
        '''
        self.assertIsNone(x)

    def nn(self, x):
        '''
        Assert x is not none
        '''
        self.assertIsNotNone(x)

    @contextlib.contextmanager
    def snap(self, vw):
        '''
        Checkpoint a workspace. Yields a new workspace that can be editted
        as the test needs, and once the context handler ends, all changes will
        tossed

        To be used with some caution, as it does create a duplicate workspace.
        '''
        safe = v_cli.VivCli()
        events = list(vw.exportWorkspace())
        safe.importWorkspace(events)
        yield safe
