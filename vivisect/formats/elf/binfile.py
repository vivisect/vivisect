import vivisect.lib.bits as v_bits
#import vivisect.lib.binfile as v_binfile
import vivisect.lib.binfile as v_binfile

from vertex.lib.common import tufo
from vivisect.hal.memory import MM_READ, MM_WRITE, MM_EXEC
from vivisect.vstruct.types import *

from synapse.lib.apicache import cacheapi
from vivisect.formats.elf.const import *

###############################################

class Elf32(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.e_ident       = vbytes(EI_NIDENT)
        self.e_class       = uint8()
        self.e_data        = uint8()
        self.e_fileversion = uint8()
        self.e_osabi       = uint8()
        self.e_abiversion  = uint8()
        self.e_pad         = vbytes(EI_PADLEN)
        self.e_type        = uint16()
        self.e_machine     = uint16()
        self.e_version     = uint32()
        self.e_entry       = uint32()
        self.e_phoff       = uint32()
        self.e_shoff       = uint32()
        self.e_flags       = uint32()
        self.e_ehsize      = uint16()
        self.e_phentsize   = uint16()
        self.e_phnum       = uint16()
        self.e_shentsize   = uint16()
        self.e_shnum       = uint16()
        self.e_shstrndx    = uint16()

class Elf32Section(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.sh_name      = uint32()
        self.sh_type      = uint32()
        self.sh_flags     = uint32()
        self.sh_addr      = uint32()
        self.sh_offset    = uint32()
        self.sh_size      = uint32()
        self.sh_link      = uint32()
        self.sh_info      = uint32()
        self.sh_addralign = uint32()
        self.sh_entsize = uint32()

class Elf32Pheader(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.p_type   = uint32()
        self.p_offset = uint32()
        self.p_vaddr  = uint32()
        self.p_paddr  = uint32()
        self.p_filesz = uint32()
        self.p_memsz  = uint32()
        self.p_flags  = uint32()
        self.p_align  = uint32()

class Elf32Reloc(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.r_offset = ptr32()
        self.r_info   = uint32()

class Elf32Reloca(Elf32Reloc):
    def __init__(self):
        Elf32Reloc.__init__(self)
        self.r_addend = uint32()

class Elf32Symbol(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.st_name  = uint32()
        self.st_value = uint32()
        self.st_size  = uint32()
        self.st_info  = uint8()
        self.st_other = uint8()
        self.st_shndx = uint16()

class Elf32Dynamic(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.d_tag   = uint32()
        self.d_value = uint32()
        self._dyn_name = None

    def getDynName(self):
        return self._dyn_name

    def setDynName(self, name):
        self._dyn_name = name

class Elf64(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.e_ident       = vbytes(EI_NIDENT)
        self.e_class       = uint8()
        self.e_data        = uint8()
        self.e_fileversion = uint8()
        self.e_osabi       = uint8()
        self.e_abiversio   = uint8()
        self.e_pad         = vbytes(EI_PADLEN)
        self.e_type        = uint16()
        self.e_machine     = uint16()
        self.e_version     = uint32()
        self.e_entry       = uint64()
        self.e_phoff       = uint64()
        self.e_shoff       = uint64()
        self.e_flags       = uint32()
        self.e_ehsize      = uint16()
        self.e_phentsize   = uint16()
        self.e_phnum       = uint16()
        self.e_shentsize   = uint16()
        self.e_shnum       = uint16()
        self.e_shstrndx    = uint16()

class Elf64Section(Elf32Section):
    def __init__(self):
        VStruct.__init__(self)
        self.sh_name      = uint32()
        self.sh_type      = uint32()
        self.sh_flags     = uint64()
        self.sh_addr      = uint64()
        self.sh_offset    = uint64()
        self.sh_size      = uint64()
        self.sh_link      = uint32()
        self.sh_info      = uint32()
        self.sh_addralign = uint64()
        self.sh_entsize   = uint64()

class Elf64Pheader(Elf32Pheader):
    def __init__(self):
        VStruct.__init__(self)
        self.p_type   = uint32()
        self.p_flags  = uint32()
        self.p_offset = uint64()
        self.p_vaddr  = uint64()
        self.p_paddr  = uint64()
        self.p_filesz = uint64()
        self.p_memsz  = uint64()
        self.p_align  = uint64()


class Elf64Reloc(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.r_offset = ptr64()
        self.r_info   = uint64()

class Elf64Reloca(Elf64Reloc):
    def __init__(self):
        #Elf64Reloc.__init__(self)
        VStruct.__init__(self)
        self.r_offset = uint64()
        self.r_info   = uint64()
        self.r_addend = uint64()

class Elf64Symbol(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.st_name  = uint32()
        self.st_info  = uint8()
        self.st_other = uint8()
        self.st_shndx = uint16()
        self.st_value = uint64()
        self.st_size  = uint64()

class Elf64Dynamic(Elf32Dynamic):
    def __init__(self):
        VStruct.__init__(self)
        self.d_tag   = uint64()
        self.d_value = uint64()

class ElfNote(VStruct):

    def __init__(self, endian='little'):
        VStruct.__init__(self)
        self['namesz'] = uint32(endian=endian).vsOnset( self._on_namesz )
        self['descsz'] = uint32(endian=endian).vsOnset( self._on_descsz )
        self['ntype']  = uint32(endian=endian)
        self['name']   = zstr()
        self['desc']   = vbytes() #VArray()

    def _on_namesz(self):
        self['name'].vsResize( self.namesz )

    def _on_descsz(self):
        self['desc'].vsResize( self.descsz )

class ElfAbiNote(ElfNote):
    def __init__(self, endian='little'):
        ElfNote.__init__(self, endian=endian)
        self['descsz'] = uint32(endian=endian)
        self['desc'] = varray(4, uint32, endian=endian)()

    #def pcb_namesz(self):
        #self['name'].vsSetLength( self.namesz )

    #def pcb_descsz(self):
        #elems = [ uint32() for i in xrange(self.descsz / 4) ]
        #self.desc = VArray(elems=elems)

class ElfBinFile(v_binfile.BinFile):

    def __init__(self, fd, **info):
        info.setdefault('zeromap',4096)
        v_binfile.BinFile.__init__(self, fd, **info)

        self.info.addKeyCtor('elf:header', self._getElfHeader )
        self.info.addKeyCtor('elf:prelink', self._getElfPrelink )
        self.info.addKeyCtor('elf:dynsyms', self._getElfDynSyms )
        self.info.addKeyCtor('elf:dynamics', self._getElfDynamics )
        self.info.addKeyCtor('elf:pheaders', self._getElfPheaders )

        self.info.addKeyCtor('elf:gnu:abi', self._elfGnuAbi )
        self.info.addKeyCtor('elf:gnu:buildid', self._elfGnuBuildId )

    def _elfGnuAbi(self):
        sec = self.getSectionByName('.note.ABI-tag')
        if sec == None:
            return None

        note = self.getStruct( self.ra2off(sec[0]) , ElfAbiNote)
        if note == None:
            return None

        if note.name != 'GNU':
            return None

        osid = int(note.desc[0])
        plat = gnu_osabi.get(osid)
        if plat == None:
            self.addAnomaly('new gnu os abi: %d' % (osid,), ra=sec[0], osid=osid)
            return None

        platver = ( int(note.desc[1]), int(note.desc[2]), int(note.desc[3]) )
        return plat,platver

    def _elfGnuBuildId(self):
        sec = self.getSectionByName('.note.gnu.build-id')
        if sec == None:
            return None

        note = self.getStruct( self.ra2off(sec[0]), ElfNote)
        if note == None:
            return None

        if note.name != 'GNU':
            return None

        return v_bits.b2h(note.desc)

    def _getArch(self):
        elf = self.getInfo('elf:header')
        return e_machine_arch.get(elf.e_machine)

    def _getFormat(self):
        return 'elf'

    def _getPlatform(self):
        elf = self.getInfo('elf:header')
        if elf.e_osabi != 0:
            return e_osabi.get( elf.e_osabi )

        abi = self.getInfo('elf:gnu:abi')
        if abi == None:
            return None

        return abi[0]

    def _getByteOrder(self):
        elf = self.getInfo('elf:header')
        return e_machine_order.get(elf.e_machine)

    def _getBinType(self):
        elf = self.getInfo('elf:header')
        if elf.e_type == ET_DYN:
            return 'dyn'
        if elf.e_type == ET_EXEC:
            return 'exe'
        return 'unk'

    def _getBaseAddr(self):

        addr = None
        for off,pgm in self.getInfo('elf:pheaders'):
            if not pgm.p_vaddr:
                continue

            if addr == None:
                addr = pgm.p_vaddr
                continue

            addr = min(addr,pgm.p_vaddr)

        # if we didn't get one, make one up
        if addr == None:
            addr = 0x20000000

        return addr

    def _getSections(self):
        # return (ra,size,name) tuples
        elf = self.getInfo('elf:header')
        if not elf.e_shoff:
            return ()


        strbase = elf.e_shstrndx

        cls = Elf32Section
        if self.getPtrSize() == 8:
            cls = Elf64Section

        off = elf.e_shoff
        size = elf.e_shentsize * elf.e_shnum
        headers = list( self.getStructs(off,size,cls) )

        strsec = headers[ elf.e_shstrndx ][1]
        stroff = strsec.sh_offset

        ret =  []
        for hra,hdr in headers:

            name = self.ascii( stroff + hdr.sh_name, 256 )
            sec = tufo(hdr.sh_addr, size=hdr.sh_size, name=name, header=hdr)

            ret.append( (hdr.sh_addr, hdr.sh_size, name, {'header':hdr}) )

        return ret

    def _getElfPrelink(self):
        for off,dyn in self.getInfo('elf:dynamics'):
            if dyn.d_tag == DT_GNU_PRELINKED:
                return True
            if dyn.d_tag == DT_GNU_CONFLICTSZ:
                return True
        return False

    def _getElfDynSyms(self):

        sec = self.getSectionByName('.dynsym')
        if sec == None:
            return ()

        hdr = sec[1].get('header')
        if not hdr.sh_off:
            return()

        raise Exception('.dynsym!')

    def _getElfDynamics(self):
        cls = Elf32Dynamic
        if self.getPtrSize() == 8:
            cls = Elf64Dynamic

        sec = self.getSectionByName('.dynamic')
        if not sec:
            return ()

        saddr,ssize,sname,sinfo = sec
        hdr = sinfo.get('header')

        dyns = []
        for off,dyn in self.getStructs(hdr.sh_offset,hdr.sh_size,cls):

            if dyn.d_tag == DT_NULL:
                break

            if dyn.d_tag in (DT_NEEDED,DT_SONAME):
                name = self._elf_strtab(dyn.d_value,'.dynstr')
                dyn.setDynName(name)

            dyns.append( (off,dyn) )

        return dyns

    def _elf_strtab(self, off, sec):
        sec = self.getSectionByName(sec)
        if sec == None:
            return None

        hdr = sec[3].get('header')
        return self.ascii( hdr.sh_offset + off, hdr.sh_size )

    def _getMemoryMaps(self):
        ret = []
        for off,pgm in self.getInfo('elf:pheaders'):

            if pgm.p_type != PT_LOAD:
                continue

            init = self.readAtOff(pgm.p_offset, pgm.p_filesz)
            init = init.rjust(pgm.p_memsz,b'\x00')

            perm = pgm.p_flags & 0x7

            info = {
                'init':init,
                'fileoff':pgm.p_offset,
                'filesize':pgm.p_filesz,
            }
            mmap = ( pgm.p_vaddr, pgm.p_memsz, perm, info )
            ret.append( mmap )

        return ret

    def _getElfPheaders(self):
        pcls = Elf32Pheader
        if self.getPtrSize() == 8:
            pcls = Elf64Pheader

        elf = self.getInfo('elf:header')

        off = elf.e_phoff
        size = elf.e_phnum * elf.e_phentsize
        return list( self.getStructs(off, size, pcls, off=True) )

    def _getElfHeader(self):
        elf = self.getStruct(0,Elf32)
        if elf.e_machine in e_machine_64:
            elf = self.getStruct(0,Elf64)
        return elf

    @staticmethod
    def isMyFormat(byts):
        return byts[0:4] == b'\x7fELF'

v_binfile.addBinFormat('elf',ElfBinFile)
