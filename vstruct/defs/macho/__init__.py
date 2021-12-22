'''
Structure definitions for the OSX MachO binary format.
'''
import struct
import logging
import binascii

import vstruct
from vstruct.defs.macho.fat import *
from vstruct.defs.macho.const import *
from vstruct.defs.macho.stabs import *
from vstruct.defs.macho.loader import *

logger = logging.getLogger(__name__)

class mach_o(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self._raw_bytes = b''
        self._symbols = None

        self.mach_header = mach_header()
        self.load_commands = vstruct.VStruct()

    def getSymbols(self):
        if self._symbols is not None:
            return self._symbols

        self._symbols = []
        for fname,vs in self.load_commands:
            if vs.cmd != LC_SYMTAB:
                continue
            strbytes = self._raw_bytes[vs.stroff:vs.stroff+vs.strsize]
            strtab = strbytes.split('\x00')
            offset = vs.symoff
            for i in range(vs.nsyms):
                n = nlist() # FIXME 64!
                offset = n.vsParse(self._raw_bytes, offset)
                #symstr = strtab[n.n_strx]
                # FIXME this is slow!
                symstr = strbytes[n.n_strx:].split('\x00', 1)[0]

    def getLibDeps(self):
        '''
        Return a list of the library files this Mach-O is dependant on
        '''
        ret = []
        for fname, vs in self.load_commands:
            if vs.cmd != LC_LOAD_DYLIB:
                continue
            ret.append(vs.namedata)
        return ret

    def getSegments(self):
        '''
        Return a list of (segname, rva, perms, bytes) tuples for the memory
        segments defined by the loader commands
        '''
        ret = []
        for fname, vs in self.load_commands:
            if vs.cmd not in (LC_SEGMENT, LC_SEGMENT_64):
                continue
            # Slice the segment bytes from raw bytes
            fbytes = self._raw_bytes[ vs.fileoff: vs.fileoff + vs.filesize ]
            # Pad out to virtual size
            try:
                fbytes = fbytes.ljust(vs.vmsize, b'\x00')
            except:
                logger.warning('Segment allocation failure')
                continue

            ret.append((vs.segname, vs.vmaddr, vs.initprot, fbytes))
        return ret

    def vsParse(self, bytes, offset=0):
        magic = struct.unpack('<I', bytes[:4])[0]
        if magic in (MH_MAGIC_64, MH_CIGAM_64):
            self.mach_header = mach_header_64()

        self._raw_bytes = bytes[offset:]
        offset = self.mach_header.vsParse(bytes, offset=offset)
        for i in range(self.mach_header.ncmds):
            # should we use endian from header?
            cmdtype, cmdlen = struct.unpack('<II', bytes[offset:offset+8])
            cmdclass = getCommandClass(cmdtype)
            cmdobj = cmdclass()
            cmdobj.vsParse(bytes, offset=offset)
            self.load_commands.vsAddField('cmd%d' % i, cmdobj)
            offset += cmdobj.cmdsize
