import vstruct

from vstruct.primitives import *
from vstruct.defs.macho.const import *

vm_prot_t = v_uint32
cpu_type_t = v_uint32
cpu_subtype_t = v_uint32
lc_str = v_uint32

class mach_header(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.magic      = v_uint32() # mach magic number identifier
        self.cputype    = cpu_type_t() # cpu specifier
        self.cpusubtype = cpu_subtype_t() # machine specifier
        self.filetype   = v_uint32() # type of file
        self.ncmds      = v_uint32() # number of load commands
        self.sizeofcmds = v_uint32() # the size of all the load commands
        self.flags      = v_uint32() # flags

    def vsParse(self, bytes, offset=0):
        # Over-ride this so we can do the parse, and make sure we
        # had the right endianness.
        ret = vstruct.VStruct.vsParse(self, bytes, offset=offset)
        if self.magic == MH_CIGAM:
            self._vs_fmtbase = '>'
            ret = vstruct.VStruct.vsParse(self, bytes, offset=offset)
        return ret

class mach_header_64(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.magic      = v_uint32() # mach magic number identifier
        self.cputype    = cpu_type_t() # cpu specifier
        self.cpusubtype = cpu_subtype_t() # machine specifier
        self.filetype   = v_uint32() # type of file
        self.ncmds      = v_uint32() # number of load commands
        self.sizeofcmds = v_uint32() # the size of all the load commands
        self.flags      = v_uint32() # flags
        self.reserved   = v_uint32() # reserved


# FIXME all commands should subclass this one!
class load_command(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.cmd     = v_uint32() # type of load command
        self.cmdsize = v_uint32() # total size of command in bytes

class segment_command(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.cmd         = v_uint32() # LC_SEGMENT
        self.cmdsize     = v_uint32() # includes sizeof section structs
        self.segname     = v_str(size=16) # segment name
        self.vmaddr      = v_uint32() # memory address of this segment
        self.vmsize      = v_uint32() # memory size of this segment
        self.fileoff     = v_uint32() # file offset of this segment
        self.filesize    = v_uint32() # amount to map from the file
        self.maxprot     = vm_prot_t() # maximum VM protection
        self.initprot    = vm_prot_t() # initial VM protection
        self.nsects      = v_uint32() # number of sections in segment
        self.flags       = v_uint32() # flags

class segment_command_64(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.cmd         = v_uint32() # LC_SEGMENT_64
        self.cmdsize     = v_uint32() # includes sizeof section_64 structs
        self.segname[16] = v_uint8() # segment name
        self.vmaddr      = v_uint64() # memory address of this segment
        self.vmsize      = v_uint64() # memory size of this segment
        self.fileoff     = v_uint64() # file offset of this segment
        self.filesize    = v_uint64() # amount to map from the file
        self.maxprot     = vm_prot_t() # maximum VM protection
        self.initprot    = vm_prot_t() # initial VM protection
        self.nsects      = v_uint32() # number of sections in segment
        self.flags       = v_uint32() # flags


class section(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.sectname     = v_str(size=16) # name of this section
        self.segname      = v_str(size=16) # segment this section goes in
        self.addr         = v_uint32() # memory address of this section
        self.size         = v_uint32() # size in bytes of this section
        self.offset       = v_uint32() # file offset of this section
        self.align        = v_uint32() # section alignment (power of 2)
        self.reloff       = v_uint32() # file offset of relocation entries
        self.nreloc       = v_uint32() # number of relocation entries
        self.flags        = v_uint32() # flags (section type and attributes)
        self.reserved1    = v_uint32() # reserved (for offset or index)
        self.reserved2    = v_uint32() # reserved (for count or sizeof)


class section_64(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.sectname     = v_str(size=16) # name of this section
        self.segname      = v_str(size=16) # segment this section goes in
        self.addr         = v_uint64() # memory address of this section
        self.size         = v_uint64() # size in bytes of this section
        self.offset       = v_uint32() # file offset of this section
        self.align        = v_uint32() # section alignment (power of 2)
        self.reloff       = v_uint32() # file offset of relocation entries
        self.nreloc       = v_uint32() # number of relocation entries
        self.flags        = v_uint32() # flags (section type and attributes)
        self.reserved1    = v_uint32() # reserved (for offset or index)
        self.reserved2    = v_uint32() # reserved (for count or sizeof)
        self.reserved3    = v_uint32() # reserved

class fvmlib_command(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.cmd     = v_uint32() # LC_IDFVMLIB or LC_LOADFVMLIB
        self.cmdsize = v_uint32() # includes pathname string
        self.name          = lc_str() # library's target pathname
        self.minor_version = v_uint32() # library's minor version number
        self.header_addr   = v_uint32() # library's header address

class dylib_command(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.cmd     = v_uint32() # LC_ID_DYLIB, LC_LOAD_{,WEAK_}DYLIB, LC_REEXPORT_DYLIB
        self.cmdsize = v_uint32() # includes pathname string
        self.name                  = lc_str() # library's path name
        self.timestamp             = v_uint32() # library's build time stamp
        self.current_version       = v_uint32() # library's current version number
        self.compatibility_version = v_uint32() # library's compatibility vers number
        self.namedata              = v_bytes(size=0)

    def vsParse(self, bytes, offset=0):
        # So we can grab the name data
        retoff = vstruct.VStruct.vsParse(self, bytes, offset=offset)
        # Grab the name from the inline data...
        name = bytes[ offset + self.name : offset + self.cmdsize ]
        name = name.split('\x00', 1)[0]
        self.vsGetField('namedata').vsSetLength(len(name))
        self.namedata = name
        return retoff

class sub_framework_command(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.cmd      = v_uint32() # LC_SUB_FRAMEWORK
        self.cmdsize  = v_uint32() # includes umbrella string
        self.umbrella = lc_str() # the umbrella framework name


class sub_client_command(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.cmd     = v_uint32() # LC_SUB_CLIENT
        self.cmdsize = v_uint32() # includes client string
        self.client  = lc_str() # the client name


class sub_umbrella_command(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.cmd          = v_uint32() # LC_SUB_UMBRELLA
        self.cmdsize      = v_uint32() # includes sub_umbrella string
        self.sub_umbrella = lc_str() # the sub_umbrella framework name


class sub_library_command(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.cmd         = v_uint32() # LC_SUB_LIBRARY
        self.cmdsize     = v_uint32() # includes sub_library string
        self.sub_library = lc_str() # the sub_library name


class prebound_dylib_command(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.cmd            = v_uint32() # LC_PREBOUND_DYLIB
        self.cmdsize        = v_uint32() # includes strings
        self.name           = lc_str() # library's path name
        self.nmodules       = v_uint32() # number of modules in library
        self.linked_modules = lc_str() # bit vector of linked modules


class dylinker_command(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.cmd     = v_uint32() # LC_ID_DYLINKER or LC_LOAD_DYLINKER
        self.cmdsize = v_uint32() # includes pathname string
        self.name    = lc_str() # dynamic linker's path name


class thread_command(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.cmd     = v_uint32() # LC_THREAD or LC_UNIXTHREAD
        self.cmdsize = v_uint32() # total size of this command


class routines_command(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.cmd          = v_uint32() # LC_ROUTINES
        self.cmdsize      = v_uint32() # total size of this command
        self.init_address = v_uint32() # address of initialization routine
        self.init_module  = v_uint32() # index into the module table that
        self.reserved1    = v_uint32()
        self.reserved2    = v_uint32()
        self.reserved3    = v_uint32()
        self.reserved4    = v_uint32()
        self.reserved5    = v_uint32()
        self.reserved6    = v_uint32()


class routines_command_64(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.cmd          = v_uint32() # LC_ROUTINES_64
        self.cmdsize      = v_uint32() # total size of this command
        self.init_address = v_uint64() # address of initialization routine
        self.init_module  = v_uint64() # index into the module table that
        self.reserved1    = v_uint64()
        self.reserved2    = v_uint64()
        self.reserved3    = v_uint64()
        self.reserved4    = v_uint64()
        self.reserved5    = v_uint64()
        self.reserved6    = v_uint64()


class symtab_command(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.cmd     = v_uint32() # LC_SYMTAB
        self.cmdsize = v_uint32() # sizeof(struct symtab_command)
        self.symoff  = v_uint32() # symbol table offset
        self.nsyms   = v_uint32() # number of symbol table entries
        self.stroff  = v_uint32() # string table offset
        self.strsize = v_uint32() # string table size in bytes

class dysymtab_command(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.cmd            = v_uint32() # LC_DYSYMTAB
        self.cmdsize        = v_uint32() # sizeof(struct dysymtab_command)
        self.ilocalsym      = v_uint32() # index to local symbols
        self.nlocalsym      = v_uint32() # number of local symbols
        self.iextdefsym     = v_uint32() # index to externally defined symbols
        self.nextdefsym     = v_uint32() # number of externally defined symbols
        self.iundefsym      = v_uint32() # index to undefined symbols
        self.nundefsym      = v_uint32() # number of undefined symbols
        self.tocoff         = v_uint32() # file offset to table of contents
        self.ntoc           = v_uint32() # number of entries in table of contents
        self.modtaboff      = v_uint32() # file offset to module table
        self.nmodtab        = v_uint32() # number of module table entries
        self.extrefsymoff   = v_uint32() # offset to referenced symbol table
        self.nextrefsyms    = v_uint32() # number of referenced symbol table entries
        self.indirectsymoff = v_uint32() # file offset to the indirect symbol table
        self.nindirectsyms  = v_uint32() # number of indirect symbol table entries
        self.extreloff      = v_uint32() # offset to external relocation entries
        self.nextrel        = v_uint32() # number of external relocation entries
        self.locreloff      = v_uint32() # offset to local relocation entries
        self.nlocrel        = v_uint32() # number of local relocation entries


class dylib_table_of_contents(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.symbol_index = v_uint32() # the defined external symbol (index into the symbol table)
        self.module_index = v_uint32() # index into the module table this symbol is defined in


class dylib_module(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.module_name           = v_uint32() # the module name (index into string table)
        self.iextdefsym            = v_uint32() # index into externally defined symbols
        self.nextdefsym            = v_uint32() # number of externally defined symbols
        self.irefsym               = v_uint32() # index into reference symbol table
        self.nrefsym               = v_uint32() # number of reference symbol table entries
        self.ilocalsym             = v_uint32() # index into symbols for local symbols
        self.nlocalsym             = v_uint32() # number of local symbols
        self.iextrel               = v_uint32() # index into external relocation entries
        self.nextrel               = v_uint32() # number of external relocation entries
        self.iinit_iterm           = v_uint32() # low 16 bits are the index into the init section, high 16 bits are the index into the term section
        self.ninit_nterm           = v_uint32() # low 16 bits are the number of init section entries, high 16 bits are the number of term section entries
        self.objc_module_info_addr = v_uint32() # the (__OBJC,__module_info) section
        self.objc_module_info_size = v_uint32() # the (__OBJC,__module_info) section


class dylib_module_64(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.module_name           = v_uint32() # the module name (index into string table)
        self.iextdefsym            = v_uint32() # index into externally defined symbols
        self.nextdefsym            = v_uint32() # number of externally defined symbols
        self.irefsym               = v_uint32() # index into reference symbol table
        self.nrefsym               = v_uint32() # number of reference symbol table entries
        self.ilocalsym             = v_uint32() # index into symbols for local symbols
        self.nlocalsym             = v_uint32() # number of local symbols
        self.iextrel               = v_uint32() # index into external relocation entries
        self.nextrel               = v_uint32() # number of external relocation entries
        self.iinit_iterm           = v_uint32() # low 16 bits are the index into the init section, high 16 bits are the index into the term section
        self.ninit_nterm           = v_uint32() # low 16 bits are the number of init section entries, high 16 bits are the number of term section entries
        self.objc_module_info_size = v_uint32() # the (__OBJC,__module_info) section
        self.objc_module_info_addr = v_uint64() # the (__OBJC,__module_info) section


class dylib_reference(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.flags = v_uint32() # flags to indicate the type of reference


class twolevel_hints_command(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.cmd     = v_uint32() # LC_TWOLEVEL_HINTS
        self.cmdsize = v_uint32() # sizeof(struct twolevel_hints_command)
        self.offset  = v_uint32() # offset to the hint table
        self.nhints  = v_uint32() # number of hints in the hint table


class twolevel_hint(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.itoc = v_uint32() # index into the table of contents

class prebind_cksum_command(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.cmd     = v_uint32() # LC_PREBIND_CKSUM
        self.cmdsize = v_uint32() # sizeof(struct prebind_cksum_command)
        self.cksum   = v_uint32() # the check sum or zero


class uuid_command(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.cmd      = v_uint32() # LC_UUID
        self.cmdsize  = v_uint32() # sizeof(struct uuid_command)
        self.uuid[16] = v_uint8() # the 128-bit uuid


class rpath_command(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.cmd     = v_uint32() # LC_RPATH
        self.cmdsize = v_uint32() # includes string
        self.path    = lc_str() # path to add to run path


class linkedit_data_command(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.cmd      = v_uint32() # LC_CODE_SIGNATURE or LC_SEGMENT_SPLIT_INFO
        self.cmdsize  = v_uint32() # sizeof(struct linkedit_data_command)
        self.dataoff  = v_uint32() # file offset of data in __LINKEDIT segment
        self.datasize = v_uint32() # file size of data in __LINKEDIT segment


class encryption_info_command(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.cmd       = v_uint32() # LC_ENCRYPTION_INFO
        self.cmdsize   = v_uint32() # sizeof(struct encryption_info_command)
        self.cryptoff  = v_uint32() # file offset of encrypted range
        self.cryptsize = v_uint32() # file size of encrypted range
        self.cryptid   = v_uint32() # which enryption system, 0 means not-encrypted yet


class symseg_command(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.cmd     = v_uint32() # LC_SYMSEG
        self.cmdsize = v_uint32() # sizeof(struct symseg_command)
        self.offset  = v_uint32() # symbol segment offset
        self.size    = v_uint32() # symbol segment size in bytes


class ident_command(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.cmd     = v_uint32() # LC_IDENT
        self.cmdsize = v_uint32() # strings that follow this command

class fvmfile_command(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.cmd         = v_uint32() # LC_FVMFILE
        self.cmdsize     = v_uint32() # includes pathname string
        self.name        = lc_str() # files pathname
        self.header_addr = v_uint32() # files virtual address

command_classes = {
    LC_SEGMENT:     segment_command,
    LC_SYMTAB:      symtab_command,
    LC_LOAD_DYLIB:  dylib_command,
}

def getCommandClass(cmdtype):
    cls = command_classes.get(cmdtype)
    if cls is not None:
        return cls
    return load_command

