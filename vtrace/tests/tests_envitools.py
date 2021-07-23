import vtrace
import vtrace.util


class EnvitoolsTests(vtrace.tests.VtraceProcessTest):
    def test_emulatorFromTrace(self):
        emu = vtrace.util.emuFromTrace(self.trace)

        ctx = self.trace.getRegisterContext()
        for rname, idx in ctx.getRegisterNameIndexes():
            self.assertEqual(self.trace.getRegister(idx), emu.getRegister(idx))

        emu.stepi()
