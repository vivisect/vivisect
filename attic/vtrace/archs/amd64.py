"""
Amd64 Support Module
"""
# Copyright (C) 2007 Invisigoth - See LICENSE file for details
import struct

import envi.archs.amd64 as e_amd64
import vtrace.archs.i386 as vt_i386

class Amd64Mixin(
        e_amd64.Amd64Module,
        e_amd64.Amd64RegisterContext,
        vt_i386.i386WatchMixin):
    """
    Do what we need to for the lucious amd64
    """
    def __init__(self):
        e_amd64.Amd64Module.__init__(self)
        e_amd64.Amd64RegisterContext.__init__(self)
        vt_i386.i386WatchMixin.__init__(self)

        self.setMeta('Architecture','amd64')

    def archGetStackTrace(self):
        self.requireAttached()
        current = 0
        sanity = 1000
        frames = []
        rbp = self.getRegisterByName("rbp")
        rip = self.getRegisterByName("rip")
        frames.append((rip,rbp))

        while rbp != 0 and current < sanity:
            try:
                rbp,rip = self.readMemoryFormat(rbp, "<QQ")
            except:
                break
            frames.append((rip,rbp))
            current += 1

        return frames

