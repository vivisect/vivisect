import envi


class dotnetModule(envi.ArchitectureModule):
    def __init__(self):
        envi.ArchitectureModule(self, 'dotnet')
        self._arch_dis = DotNetDisasm()

    def archGetRegCtx(self):
        return dotnetRegisterContext()

    def archGetBreakInstr(self):
        pass

    def archGetNopInstr(self):
        pass

    def archGetRegisterGroups(self):
        pass

    def getPointerSize(self):
        pass

    def pointerString(self, va):
        pass

    def archParseOpcode(self, bytes, offset=0, va=0):
        pass

    def getEmulator(self):
        return DotNetEmulator()
