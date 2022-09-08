import unittest
import vivisect.tests.helpers as helpers

class HelperTest(unittest.TestCase):

    def test_helper_pathjoin(self):
        # retrieve a known vivtestfiles path ( or skip )
        helpers.getTestPath('windows','i386','helloworld.exe')

