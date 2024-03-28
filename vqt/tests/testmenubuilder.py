import logging
import unittest
import vqt.menubuilder as vmb

logger = logging.getLogger(__name__)


class MenuTest(unittest.TestCase):

    def test_actioncall_success(self):
        ac = vmb.ActionCall(acsucceed, 4, 8)
        out = ac()
        self.assertEqual(out, 32)

    def test_actioncall_fail(self):
        ac = vmb.ActionCall(acfail, 4, 8)
        ac()


def acsucceed(x, y):
    return x * y


def acfail(x, y):
    return y / 0
