"""
PPC Support Module (not done)
"""
# Copyright (C) 2007 Invisigoth - See LICENSE file for details
class PpcMixin:
    def archAddWatchpoint(self, address):
        pass

    def archRemWatchpoint(self, address):
        pass

    def archCheckWatchpoint(self, address):
        pass

    def getStackTrace(self):
        self.requireAttached()
        return []

    def getBreakInstruction(self):
        # twi 0x14, r0, 0 
        # trap if r0 is (>=:unsigned) 0
        return "\x0e\x80\x00\x00"

    def archGetPcName(self):
        return "r0"

    def archGetSpName(self):
        return "r1"

    def platformCall(self, address, args, convention=None):
        pass
