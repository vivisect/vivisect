import unittest

import vtrace
import vtrace.envitools
from vtrace.tests import VtraceProcessTest


class EnvitoolsTests(VtraceProcessTest):
    def test_emulatorFromTrace(self):
        emu = vtrace.envitools.emuFromTrace(self.trace)

        ctx = self.trace.getRegisterContext()
        for rname, idx in ctx.getRegisterNameIndexes():
            self.assertEqual(self.trace.getRegister(idx), emu.getRegister(idx))

        emu.stepi()
