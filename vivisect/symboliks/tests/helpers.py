import vivisect.symboliks.emulator as vsym_emu


class MockEmulator(vsym_emu.SymbolikEmulator):
    __width__ = 4

    def __init__(self, vw):
        # super(TestEmulator, self).__init__(vw)
        vsym_emu.SymbolikEmulator.__init__(self, vw)
