
import vstruct
from vstruct.primitives import *
import vstruct.primitives as vs_prim

class fat_header(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.magic = v_uint32(bigend=True)
        self.nfat_arch = v_uint32(bigend=True)

class fat_arch(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.cputype    = v_uint32(bigend=True)  # cpu specifier (int) */
        self.cpusubtype = v_uint32(bigend=True)  # machine specifier (int) */
        self.offset     = v_uint32(bigend=True)  # file offset to this object file */
        self.size       = v_uint32(bigend=True)  # size of this object file */
        self.align      = v_uint32(bigend=True)  # alignment as a power of 2 */

