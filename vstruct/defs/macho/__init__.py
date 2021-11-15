'''
Structure definitions for the OSX MachO binary format.
'''
import struct
import vstruct

from vstruct.defs.macho.fat import *
from vstruct.defs.macho.const import *
from vstruct.defs.macho.stabs import *
from vstruct.defs.macho.loader import *

class mach_o(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self._raw_bytes = ''
        self._symbols = None

        self.mach_header = mach_header()
        self.load_commands = vstruct.VStruct()

    def getEndian(self):
        return self.mach_header.vsGetMeta('endian')

    def getPointerSize(self):
        return self.mach_header.vsGetMeta('psize')

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
            if vs.segname == '__PAGEZERO':
                continue

            # Slice the segment bytes from raw bytes
            fbytes = self._raw_bytes[ vs.fileoff: vs.fileoff + vs.filesize ]
            # Pad out to virtual size
            fbytes = fbytes.ljust(vs.vmsize, b'\x00')

            ret.append((vs.segname, vs.vmaddr, vs.initprot, fbytes))
        return ret

    def getStructureInfo(self):
        '''
        Returns Structure information usable by the loader to tag file structures
        '''
        structs = []
        for fname, vs in self.load_commands:
            if vs.cmd not in (LC_SEGMENT, LC_SEGMENT_64):
                continue
            if vs.segname == '__PAGEZERO':
                continue

            if vs.fileoff == 0:
                offset = 0
                va = None
                if self.mach_header.vsGetMeta('psize') == 8:
                    va = vs.vmaddr
                    structs.append(('macho.mach_header_64', va))
                    offset += len(mach_header_64())

                else:
                    va = vs.vmaddr
                    structs.append(('macho.mach_header', va))
                    offset += len(mach_header())

                for cmd, vs in self.load_commands:
                    structs.append(('macho.' + vs.vsGetTypeName(), va + offset))
                    offset += vs.cmdsize

        return structs

    def vsParse(self, bytes, offset=0):
        self._raw_bytes = bytes[offset:]
        offset = self.mach_header.vsParse(bytes, offset=offset)
        for i in range(self.mach_header.ncmds):
            # should we use endian from header?
            fmt = ('<II','>II')[self.getEndian()]
            cmdtype, cmdlen = struct.unpack(fmt, bytes[offset:offset+8])
            cmdclass = getCommandClass(cmdtype)
            cmdobj = cmdclass()
            cmdobj.vsParse(bytes, offset=offset)
            self.load_commands.vsAddField('cmd%d' % i, cmdobj)
            offset += cmdobj.cmdsize
