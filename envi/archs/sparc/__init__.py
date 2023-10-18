"""
The envi architecture module for the 32 bit SPARCv8 platform.
"""

#
# Reference used: https://sparc.org/wp-content/uploads/2014/01/v8.pdf.gz
# 

import struct
import envi

from envi.archs.sparc.disasm import *

class SparcModule(envi.ArchitectureModule):
    def __init__(self, name="sparc", endian=envi.ENDIAN_MSB):
        self._arch_dis = SparcDisasm()

        envi.ArchitectureModule.__init__(self, name, endian)

    def getPointerSize(self):
        return 4

    def pointerString(self, va):
        return "0x%.08x" % (va)


    def archParseOpcode(self, bytecode, offset=0, va=0, extra=None):

        return self._arch_dis.disasm(bytecode, offset, va)
