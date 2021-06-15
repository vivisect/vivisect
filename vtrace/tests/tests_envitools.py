import vtrace
import vtrace.envitools
import vtrace.util


class EnvitoolsTests(vtrace.tests.VtraceProcessTest):
    def test_emulatorFromTrace(self):
        emu = vtrace.util.emuFromTrace(self.trace)

        ctx = self.trace.getRegisterContext()
        for rname, idx in ctx.getRegisterNameIndexes():
            self.assertEqual(self.trace.getRegister(idx), emu.getRegister(idx))

        emu.stepi()

    def test_workspaceFromTrace(self):
        vw = vtrace.util.vwFromTrace(self.trace, collapse=False)
        vwmaps = list(vw.getMemoryMaps())

        for mva, msize, mperms, mfname in self.trace.getMemoryMaps():

            # test that the file mappings exist for each (which means segments have to be correct)
            filename = vw.getFileByVa(mva)
            self.assertIn(filename, mfname)
