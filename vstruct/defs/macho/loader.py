import vstruct

from vstruct.primitives import *
from vstruct.defs.macho.const import *

vm_prot_t = v_uint32
cpu_type_t = v_uint32
cpu_subtype_t = v_uint32
lc_str = v_uint32

class mach_header(vstruct.VStruct):

    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self, bigend=bigend)
        self.magic      = v_uint32(bigend=bigend) # mach magic number identifier
        self.cputype    = cpu_type_t(bigend=bigend) # cpu specifier
        self.cpusubtype = cpu_subtype_t(bigend=bigend) # machine specifier
        self.filetype   = v_uint32(bigend=bigend) # type of file
        self.ncmds      = v_uint32(bigend=bigend) # number of load commands
        self.sizeofcmds = v_uint32(bigend=bigend) # the size of all the load commands
        self.flags      = v_uint32(bigend=bigend) # flags

    def pcb_magic(self):
        if self.magic == MH_CIGAM:
            self.vsSetEndian(True)

class mach_header_64(vstruct.VStruct):

    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self, bigend=bigend)
        self.magic      = v_uint32(bigend=bigend) # mach magic number identifier
        self.cputype    = cpu_type_t(bigend=bigend) # cpu specifier
        self.cpusubtype = cpu_subtype_t(bigend=bigend) # machine specifier
        self.filetype   = v_uint32(bigend=bigend) # type of file
        self.ncmds      = v_uint32(bigend=bigend) # number of load commands
        self.sizeofcmds = v_uint32(bigend=bigend) # the size of all the load commands
        self.flags      = v_uint32(bigend=bigend) # flags
        self.reserved   = v_uint32() # reserved

    def pcb_magic(self):
        if self.magic == MH_CIGAM_64:
            self.vsSetEndian(True)

class load_command(vstruct.VStruct):

    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self, bigend=bigend)
        self.cmd     = v_uint32(bigend=bigend) # type of load command
        self.cmdsize = v_uint32(bigend=bigend) # total size of command in bytes

class segment_command(load_command):

    def __init__(self, bigend=False):
        # LC_SEGMENT
        load_command.__init__(self, bigend=bigend)
        self.segname  = v_str(size=16) # segment name
        self.vmaddr   = v_uint32(bigend=bigend) # memory address of this segment
        self.vmsize   = v_uint32(bigend=bigend) # memory size of this segment
        self.fileoff  = v_uint32(bigend=bigend) # file offset of this segment
        self.filesize = v_uint32(bigend=bigend) # amount to map from the file
        self.maxprot  = vm_prot_t(bigend=bigend) # maximum VM protection
        self.initprot = vm_prot_t(bigend=bigend) # initial VM protection
        self.nsects   = v_uint32(bigend=bigend) # number of sections in segment
        self.flags    = v_uint32(bigend=bigend) # flags

        self.sections = vstruct.VArray()

    def vsParse(self, bytes, offset=0):
        # parse the structure
        bigend = self.vsGetEndian()
        retoff = vstruct.VStruct.vsParse(self, bytes, offset=offset)

        # now that we have the parsed structure, we can parse the section info for this
        # segment, which follows directly after the segment info structure
        step = len(self)
        for i in range(self.nsects):
            sect = section(bigend=self.vsGetEndian())
            step += sect.vsParse(bytes[offset+step:])
            self.sections.vsAddElement(sect)

        return len(self) + offset

class segment_command_64(load_command):

    def __init__(self, bigend=False):
        # LC_SEGMENT_64

        load_command.__init__(self, bigend=bigend)
        self.segname  = v_str(size=16) # segment name
        self.vmaddr   = v_uint64(bigend=bigend) # memory address of this segment
        self.vmsize   = v_uint64(bigend=bigend) # memory size of this segment
        self.fileoff  = v_uint64(bigend=bigend) # file offset of this segment
        self.filesize = v_uint64(bigend=bigend) # amount to map from the file
        self.maxprot  = vm_prot_t(bigend=bigend) # maximum VM protection
        self.initprot = vm_prot_t(bigend=bigend) # initial VM protection
        self.nsects   = v_uint32(bigend=bigend) # number of sections in segment
        self.flags    = v_uint32(bigend=bigend) # flags

        self.sections = vstruct.VArray()

    def vsParse(self, bytes, offset=0):
        # parse the structure
        retoff = vstruct.VStruct.vsParse(self, bytes, offset=offset)

        # now that we have the parsed structure, we can parse the section info for this
        # segment, which follows directly after the segment info structure
        step = len(self)
        for i in range(self.nsects):
            sect = section_64(self.vsGetEndian())
            step += sect.vsParse(bytes[offset+step:])
            self.sections.vsAddElement(sect)

        # as with all vsParse methods, we return the new offset,
        # which is the old + len(seg header) + len(all associated sections we just parsed)
        return len(self) + offset


class section(vstruct.VStruct):

    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self, bigend=bigend)
        self.sectname  = v_str(size=16) # name of this section
        self.segname   = v_str(size=16) # segment this section goes in
        self.addr      = v_uint32(bigend=bigend) # memory address of this section
        self.size      = v_uint32(bigend=bigend) # size in bytes of this section
        self.offset    = v_uint32(bigend=bigend) # file offset of this section
        self.align     = v_uint32(bigend=bigend) # section alignment (power of 2)
        self.reloff    = v_uint32(bigend=bigend) # file offset of relocation entries
        self.nreloc    = v_uint32(bigend=bigend) # number of relocation entries
        self.flags     = v_uint32(bigend=bigend) # flags (section type and attributes)
        self.reserved1 = v_uint32(bigend=bigend) # reserved (for offset or index)
        self.reserved2 = v_uint32(bigend=bigend) # reserved (for count or sizeof)


class section_64(vstruct.VStruct):

    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self, bigend=bigend)
        self.sectname     = v_str(size=16) # name of this section
        self.segname      = v_str(size=16) # segment this section goes in
        self.addr         = v_uint64(bigend=bigend) # memory address of this section
        self.size         = v_uint64(bigend=bigend) # size in bytes of this section
        self.offset       = v_uint32(bigend=bigend) # file offset of this section
        self.align        = v_uint32(bigend=bigend) # section alignment (power of 2)
        self.reloff       = v_uint32(bigend=bigend) # file offset of relocation entries
        self.nreloc       = v_uint32(bigend=bigend) # number of relocation entries
        self.flags        = v_uint32(bigend=bigend) # flags (section type and attributes)
        self.reserved1    = v_uint32(bigend=bigend) # reserved (for offset or index)
        self.reserved2    = v_uint32(bigend=bigend) # reserved (for count or sizeof)
        self.reserved3    = v_uint32(bigend=bigend) # reserved

class fvmlib_command(load_command):

    def __init__(self, bigend=False):
        # LC_IDFVMLIB or LC_LOADFVMLIB
        # includes pathname string
        load_command.__init__(self, bigend=bigend)
        self.name          = lc_str() # library's target pathname
        self.minor_version = v_uint32(bigend=bigend) # library's minor version number
        self.header_addr   = v_uint32(bigend=bigend) # library's header address

    def pcb_name(self):
        pass

class dylib_command(load_command):

    def __init__(self, bigend=False):
        # LC_ID_DYLIB, LC_LOAD_{,WEAK_}DYLIB, LC_REEXPORT_DYLIB
        # includes pathname string
        load_command.__init__(self, bigend=bigend)
        self.name                  = lc_str() # library's path name
        self.timestamp             = v_uint32(bigend=bigend) # library's build time stamp
        self.current_version       = v_uint32(bigend=bigend) # library's current version number
        self.compatibility_version = v_uint32(bigend=bigend) # library's compatibility vers number
        self.namedata              = ''

    def vsParse(self, bytes, offset=0):
        # So we can grab the name data
        retoff = vstruct.VStruct.vsParse(self, bytes, offset=offset)
        # Grab the name from the inline data...
        name = bytes[ offset + self.name : offset + self.cmdsize ]
        name = name.split(b'\x00', 1)[0].decode('utf-8')
        self.namedata = name
        return retoff

class sub_framework_command(load_command):

    def __init__(self, bigend=False):
        # LC_SUB_FRAMEWORK
        load_command.__init__(self, bigend=bigend)
        self.umbrella = lc_str() # the umbrella framework name


class sub_client_command(load_command):

    def __init__(self, bigend=False):
        # LC_SUB_CLIENT
        load_command.__init__(self, bigend=bigend)
        self.client  = lc_str() # the client name


class sub_umbrella_command(load_command):

    def __init__(self, bigend=False):
        # LC_SUB_UMBRELLA
        # includes sub_umbrella string
        load_command.__init__(self, bigend=bigend)
        self.sub_umbrella = lc_str() # the sub_umbrella framework name


class sub_library_command(load_command):

    def __init__(self, bigend=False):
        # LC_SUB_LIBRARY
        # includes sub_umbrella string
        load_command.__init__(self, bigend=bigend)
        self.sub_library = lc_str() # the sub_library name


class prebound_dylib_command(load_command):

    def __init__(self, bigend=False):
        # LC_PREBOUND_DYLIB
        load_command.__init__(self, bigend=bigend)
        self.name           = lc_str() # library's path name
        self.nmodules       = v_uint32(bigend=bigend) # number of modules in library
        self.linked_modules = lc_str() # bit vector of linked modules


class dylinker_command(load_command):

    def __init__(self, bigend=False):
        # LC_ID_DYLINKER or LC_LOAD_DYLINKER
        load_command.__init__(self, bigend=bigend)
        self.name    = lc_str() # dynamic linker's path name

# Thread commands contain machine-specific data structures suitable for
# use in the thread state primitives.  The machine specific data structures
# follow the struct thread_command as follows.
# Each flavor of machine specific data structure is preceded by an unsigned
# long constant for the flavor of that data structure, an uint32_t
# that is the count of longs of the size of the state data structure and then
# the state data structure follows.  This triple may be repeated for many
# flavors.  The constants for the flavors, counts and state data structure
# definitions are expected to be in the header file <machine/thread_status.h>.
# These machine specific data structures sizes must be multiples of
# 4 bytes  The cmdsize reflects the total size of the thread_command
# and all of the sizes of the constants for the flavors, counts and state
# data structures.
#
# For executable objects that are unix processes there will be one
# thread_command (cmd == LC_UNIXTHREAD) created for it by the link-editor.
# This is the same as a LC_THREAD, except that a stack is automatically
# created (based on the shell's limit for the stack size).  Command arguments
# and environment variables are copied onto that stack.
class thread_command(load_command):

    def __init__(self, bigend=False):
        # LC_THREAD or LC_UNIXTHREAD
        load_command.__init__(self, bigend=bigend)
        self.flavor  = v_uint32(bigend=bigend) # flavor of thread state
        self.count   = v_uint32(bigend=bigend) # count of longs in thread state


class routines_command(load_command):

    def __init__(self, bigend=False):
        # LC_ROUTINES
        load_command.__init__(self, bigend=bigend)
        self.init_address = v_uint32(bigend=bigend) # address of initialization routine
        self.init_module  = v_uint32(bigend=bigend) # index into the module table that
        self.reserved1    = v_uint32(bigend=bigend)
        self.reserved2    = v_uint32(bigend=bigend)
        self.reserved3    = v_uint32(bigend=bigend)
        self.reserved4    = v_uint32(bigend=bigend)
        self.reserved5    = v_uint32(bigend=bigend)
        self.reserved6    = v_uint32(bigend=bigend)


class routines_command_64(load_command):

    def __init__(self, bigend=False):
        # LC_ROUTINES_64
        load_command.__init__(self, bigend=bigend)
        self.init_address = v_uint64(bigend=bigend) # address of initialization routine
        self.init_module  = v_uint64(bigend=bigend) # index into the module table that
        self.reserved1    = v_uint64(bigend=bigend)
        self.reserved2    = v_uint64(bigend=bigend)
        self.reserved3    = v_uint64(bigend=bigend)
        self.reserved4    = v_uint64(bigend=bigend)
        self.reserved5    = v_uint64(bigend=bigend)
        self.reserved6    = v_uint64(bigend=bigend)


class symtab_command(load_command):

    def __init__(self, bigend=False):
        # LC_SYMTAB
        load_command.__init__(self, bigend=bigend)
        self.symoff  = v_uint32(bigend=bigend) # symbol table offset
        self.nsyms   = v_uint32(bigend=bigend) # number of symbol table entries
        self.stroff  = v_uint32(bigend=bigend) # string table offset
        self.strsize = v_uint32(bigend=bigend) # string table size in bytes

class dysymtab_command(load_command):

    def __init__(self, bigend=False):
        # LC_DYSYMTAB
        load_command.__init__(self, bigend=bigend)
        self.ilocalsym      = v_uint32(bigend=bigend) # index to local symbols
        self.nlocalsym      = v_uint32(bigend=bigend) # number of local symbols
        self.iextdefsym     = v_uint32(bigend=bigend) # index to externally defined symbols
        self.nextdefsym     = v_uint32(bigend=bigend) # number of externally defined symbols
        self.iundefsym      = v_uint32(bigend=bigend) # index to undefined symbols
        self.nundefsym      = v_uint32(bigend=bigend) # number of undefined symbols
        self.tocoff         = v_uint32(bigend=bigend) # file offset to table of contents
        self.ntoc           = v_uint32(bigend=bigend) # number of entries in table of contents
        self.modtaboff      = v_uint32(bigend=bigend) # file offset to module table
        self.nmodtab        = v_uint32(bigend=bigend) # number of module table entries
        self.extrefsymoff   = v_uint32(bigend=bigend) # offset to referenced symbol table
        self.nextrefsyms    = v_uint32(bigend=bigend) # number of referenced symbol table entries
        self.indirectsymoff = v_uint32(bigend=bigend) # file offset to the indirect symbol table
        self.nindirectsyms  = v_uint32(bigend=bigend) # number of indirect symbol table entries
        self.extreloff      = v_uint32(bigend=bigend) # offset to external relocation entries
        self.nextrel        = v_uint32(bigend=bigend) # number of external relocation entries
        self.locreloff      = v_uint32(bigend=bigend) # offset to local relocation entries
        self.nlocrel        = v_uint32(bigend=bigend) # number of local relocation entries


class dylib_table_of_contents(vstruct.VStruct):

    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self, bigend=bigend)
        self.symbol_index = v_uint32(bigend=bigend) # the defined external symbol (index into the symbol table)
        self.module_index = v_uint32(bigend=bigend) # index into the module table this symbol is defined in


class dylib_module(vstruct.VStruct):

    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self, bigend=bigend)
        self.module_name           = v_uint32(bigend=bigend) # the module name (index into string table)
        self.iextdefsym            = v_uint32(bigend=bigend) # index into externally defined symbols
        self.nextdefsym            = v_uint32(bigend=bigend) # number of externally defined symbols
        self.irefsym               = v_uint32(bigend=bigend) # index into reference symbol table
        self.nrefsym               = v_uint32(bigend=bigend) # number of reference symbol table entries
        self.ilocalsym             = v_uint32(bigend=bigend) # index into symbols for local symbols
        self.nlocalsym             = v_uint32(bigend=bigend) # number of local symbols
        self.iextrel               = v_uint32(bigend=bigend) # index into external relocation entries
        self.nextrel               = v_uint32(bigend=bigend) # number of external relocation entries
        self.iinit_iterm           = v_uint32(bigend=bigend) # low 16 bits are the index into the init section, high 16 bits are the index into the term section
        self.ninit_nterm           = v_uint32(bigend=bigend) # low 16 bits are the number of init section entries, high 16 bits are the number of term section entries
        self.objc_module_info_addr = v_uint32(bigend=bigend) # the (__OBJC,__module_info) section
        self.objc_module_info_size = v_uint32(bigend=bigend) # the (__OBJC,__module_info) section


class dylib_module_64(vstruct.VStruct):

    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self, bigend=bigend)
        self.module_name           = v_uint32(bigend=bigend) # the module name (index into string table)
        self.iextdefsym            = v_uint32(bigend=bigend) # index into externally defined symbols
        self.nextdefsym            = v_uint32(bigend=bigend) # number of externally defined symbols
        self.irefsym               = v_uint32(bigend=bigend) # index into reference symbol table
        self.nrefsym               = v_uint32(bigend=bigend) # number of reference symbol table entries
        self.ilocalsym             = v_uint32(bigend=bigend) # index into symbols for local symbols
        self.nlocalsym             = v_uint32(bigend=bigend) # number of local symbols
        self.iextrel               = v_uint32(bigend=bigend) # index into external relocation entries
        self.nextrel               = v_uint32(bigend=bigend) # number of external relocation entries
        self.iinit_iterm           = v_uint32(bigend=bigend) # low 16 bits are the index into the init section, high 16 bits are the index into the term section
        self.ninit_nterm           = v_uint32(bigend=bigend) # low 16 bits are the number of init section entries, high 16 bits are the number of term section entries
        self.objc_module_info_size = v_uint32(bigend=bigend) # the (__OBJC,__module_info) section
        self.objc_module_info_addr = v_uint64(bigend=bigend) # the (__OBJC,__module_info) section


class dylib_reference(vstruct.VStruct):

    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self, bigend=bigend)
        self.flags = v_uint32(bigend=bigend) # flags to indicate the type of reference


class twolevel_hints_command(load_command):

    def __init__(self, bigend=False):
        # LC_TWOLEVEL_HINTS
        load_command.__init__(self, bigend=bigend)
        self.offset  = v_uint32(bigend=bigend) # offset to the hint table
        self.nhints  = v_uint32(bigend=bigend) # number of hints in the hint table


class twolevel_hint(load_command):

    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self, bigend=bigend)
        self.itoc = v_uint32(bigend=bigend) # index into the table of contents

class prebind_cksum_command(load_command):

    def __init__(self, bigend=False):
        # LC_PREBIND_CKSUM
        load_command.__init__(self, bigend=bigend)
        self.cksum   = v_uint32(bigend=bigend) # the check sum or zero


class uuid_command(load_command):

    def __init__(self, bigend=False):
        # LC_UUID
        load_command.__init__(self, bigend=bigend)
        self.uuid = v_bytes(size=16)


class rpath_command(load_command):

    def __init__(self, bigend=False):
        # LC_RPATH
        load_command.__init__(self, bigend=bigend)
        self.path    = lc_str() # path to add to run path


class linkedit_data_command(load_command):

    def __init__(self, bigend=False):
        # LC_CODE_SIGNATURE or LC_SEGMENT_SPLIT_INFO
        load_command.__init__(self, bigend=bigend)
        self.dataoff  = v_uint32(bigend=bigend) # file offset of data in __LINKEDIT segment
        self.datasize = v_uint32(bigend=bigend) # file size of data in __LINKEDIT segment


class encryption_info_command(load_command):

    def __init__(self, bigend=False):
        # LC_ENCRYPTION_INFO
        load_command.__init__(self, bigend=bigend)
        self.cryptoff  = v_uint32(bigend=bigend) # file offset of encrypted range
        self.cryptsize = v_uint32(bigend=bigend) # file size of encrypted range
        self.cryptid   = v_uint32(bigend=bigend) # which enryption system, 0 means not-encrypted yet


class symseg_command(load_command):

    def __init__(self, bigend=False):
        # LC_SYMSEG
        load_command.__init__(self, bigend=bigend)
        self.offset  = v_uint32(bigend=bigend) # symbol segment offset
        self.size    = v_uint32(bigend=bigend) # symbol segment size in bytes


class ident_command(load_command):

    def __init__(self, bigend=False):
        # LC_IDENT
        load_command.__init__(self, bigend=bigend)


class fvmfile_command(load_command):

    def __init__(self, bigend=False):
        # LC_FVMFILE
        load_command.__init__(self, bigend=bigend)
        self.name        = lc_str() # files pathname
        self.header_addr = v_uint32(bigend=bigend) # files virtual address


class dyld_info_command(load_command):

    def __init__(self, bigend=False):
        load_command.__init__(self, bigend=bigend)
        self.rebase_off = v_uint32(bigend=bigend)
        self.rebase_size = v_uint32(bigend=bigend)
        self.bind_off = v_uint32(bigend=bigend)
        self.bind_size = v_uint32(bigend=bigend)
        self.weak_bind_off = v_uint32(bigend=bigend)
        self.weak_bind_size = v_uint32(bigend=bigend)
        self.lazy_bind_off = v_uint32(bigend=bigend)
        self.lazy_bind_size = v_uint32(bigend=bigend)
        self.export_off = v_uint32(bigend=bigend)
        self.export_size = v_uint32(bigend=bigend)


class version_min_command(load_command):

    def __init__(self, bigend=False):
        load_command.__init__(self, bigend=bigend)
        self.version = v_uint32(bigend=bigend)
        self.sdk = v_uint32(bigend=bigend)


# The entry_point_command is a replacement for thread_command.
# It is used for main executables to specify the location (file offset)
# of main().  If -stack_size was used at link time, the stacksize
# field will contain the stack size need for the main thread.
class entry_point_command(load_command):

    def __init__(self, bigend=False):
        load_command.__init__(self, bigend=bigend)
        self.entryoff  = v_uint64(bigend=bigend)  # file (__TEXT) offset of main()
        self.stacksize = v_uint64(bigend=bigend)  # if not zero, initial stack size


class source_version_command(load_command):
    def __init__(self, bigend=False):
        load_command.__init__(self, bigend=bigend)
        self.version = v_uint64(bigend=bigend)  # A.B.C.D.E packed as a24.b10.c10.d10.e10

    def getVersion(self):
        verinfo = []
        version = self.version
        for i in range(4):
            valu = version & 0x3FF
            verinfo.insert(0, str(valu))
            version >>= 10
        last = version & 0xFFFFFF
        verinfo.insert(0, str(last))
        return '.'.join(verinfo)

class data_in_code_entry(vstruct.VStruct):
    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self, bigend=bigend)
        self.offset = v_uint32(bigend=bigend)  # from mach_header to start of the range
        self.length = v_uint16(bigend=bigend)
        self.kind = v_uint16(bigend=bigend)  # a DICE_KIND_* value


command_classes = {
    LC_SEGMENT:     segment_command,
    LC_SYMTAB:      symtab_command,
    LC_LOAD_DYLIB:  dylib_command,

    LC_SEGMENT: segment_command,
    LC_SYMTAB: symtab_command,
    LC_SYMSEG: symseg_command,
    LC_THREAD: thread_command,
    LC_UNIXTHREAD: thread_command,
    LC_LOADFVMLIB: fvmlib_command,
    LC_IDFVMLIB: fvmlib_command,
    LC_IDENT: ident_command,
    LC_FVMFILE: fvmfile_command,
    # LC_PREPAGE: ,
    LC_DYSYMTAB: dysymtab_command,
    LC_LOAD_DYLIB: dylib_command,
    LC_ID_DYLIB: dylib_command,
    LC_LOAD_DYLINKER: dylinker_command,
    LC_ID_DYLINKER: dylib_command,
    LC_PREBOUND_DYLIB: prebound_dylib_command,
    LC_ROUTINES: routines_command,
    LC_SUB_FRAMEWORK: sub_framework_command,
    LC_SUB_UMBRELLA: sub_umbrella_command,
    LC_SUB_CLIENT: sub_client_command,
    LC_SUB_LIBRARY: sub_library_command,
    LC_TWOLEVEL_HINTS: twolevel_hints_command,
    LC_PREBIND_CKSUM: prebind_cksum_command,
    LC_LOAD_WEAK_DYLIB: dylib_command,
    LC_SEGMENT_64: segment_command_64,
    LC_ROUTINES_64: routines_command_64,
    LC_UUID: uuid_command,
    LC_RPATH: rpath_command,
    LC_CODE_SIGNATURE: linkedit_data_command,
    LC_SEGMENT_SPLIT_INFO: linkedit_data_command,
    LC_REEXPORT_DYLIB: dylib_command,
    LC_LAZY_LOAD_DYLIB: dylib_command,
    LC_ENCRYPTION_INFO: encryption_info_command,
    LC_DYLD_INFO: dyld_info_command,
    LC_DYLD_INFO_ONLY: dyld_info_command,
    # LC_LOAD_UPWARD_DYLIB: ,  # TODO: I can't find any refs on what this should be
    LC_VERSION_MIN_MACOSX: version_min_command,
    LC_VERSION_MIN_IPHONEOS: version_min_command,
    LC_FUNCTION_STARTS: linkedit_data_command,
    LC_DYLD_ENVIRONMENT: dylinker_command,
    LC_MAIN: entry_point_command,
    LC_DATA_IN_CODE: linkedit_data_command,
    LC_SOURCE_VERSION: source_version_command,
    LC_DYLIB_CODE_SIGN_DRS: linkedit_data_command,
}

def getCommandClass(cmdtype):
    cls = command_classes.get(cmdtype)
    if cls is not None:
        return cls
    return load_command

