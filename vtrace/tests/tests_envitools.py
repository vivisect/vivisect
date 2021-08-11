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
            if mfname in ('[vvar]', '[vsyscall]') or mperms == 0:
                continue

            # test that the file mappings exist for each (which means segments have to be correct)
            filename = vw.getFileByVa(mva)
            self.assertTrue(filename in mfname)

    def test_workspaceFromTraceWithCollapse_Strict(self):
        vw = vtrace.util.vwFromTrace(self.trace, collapse=True, strict=True)
        vwmaps = list(vw.getMemoryMaps())

        for mva, msize, mperms, mfname in self.trace.getMemoryMaps():
            if mfname in ('[vvar]', '[vsyscall]') or mperms == 0:
                continue

            # test that the file mappings exist for each (which means segments have to be correct)
            filename = vw.getFileByVa(mva)
            self.assertTrue(filename in mfname)
            self.assertEqual(len(vwmaps), 53)

    def test_workspaceFromTraceWithCollapse_Nonstrict(self):
        vw = vtrace.util.vwFromTrace(self.trace, collapse=True, strict=False)
        vwmaps = list(vw.getMemoryMaps())

        for mva, msize, mperms, mfname in self.trace.getMemoryMaps():
            if mfname in ('[vvar]', '[vsyscall]') or mperms == 0:
                continue

            # test that the file mappings exist for each (which means segments have to be correct)
            filename = vw.getFileByVa(mva)
            self.assertTrue(filename in mfname)
            self.assertEqual(len(vwmaps), 26)
