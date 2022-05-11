"""
A place for all vivisect contstants so everybody can import them.
"""

# Vivisect workspace events
# NOTE: All events in a vivisect workspace are notified async!
# Also, an event *must* carry with it all the needed information to
# reconstruct the changes to the workspace for the event.
VWE_ADDLOCATION     = 1 # (va,size,ltype,tinfo)
VWE_DELLOCATION     = 2 # (va,size,ltype,tinfo)

VWE_ADDSEGMENT      = 3 # (va, size, name, filename)
VWE_DELSEGMENT      = 4 # FIXME IMPLEMENT

VWE_ADDRELOC        = 5 # (va,rtype)
VWE_DELRELOC        = 6 # # FIXME IMPLEMENT

VWE_ADDMODULE       = 7 # DEPRECATED
VWE_DELMODULE       = 8 # DEPRECATED

VWE_ADDFMODULE      = 9  # DEPRECATED
VWE_DELFMODULE      = 10 # DEPRECATED

VWE_ADDFUNCTION     = 11 # (va, meta)
VWE_DELFUNCTION     = 12 # va

VWE_SETFUNCARGS     = 13 # (fva, arglist)
VWE_SETFUNCMETA     = 14 # (funcva, key, value)

VWE_ADDCODEBLOCK    = 15 # (va, size, funcva)
VWE_DELCODEBLOCK    = 16 # FIXME IMPLEMENT

VWE_ADDXREF         = 17 # (fromva, tova, reftype)
VWE_DELXREF         = 18 # (fromva, tova, reftype)

VWE_SETNAME         = 19 # (va, name)

VWE_ADDMMAP         = 20 # (va, perms, bytes) #OMG MAYBE BIG
VWE_DELMMAP         = 21 # FIXME IMPLEMENT

VWE_ADDEXPORT       = 22 # export object (not for long)
VWE_DELEXPORT       = 23 # export object (not for long)

VWE_SETMETA         = 24 # (key, val)

VWE_COMMENT         = 25 # (va, comment)

VWE_ADDFILE         = 26 # (normname, baseaddr, md5sum)
VWE_DELFILE         = 27  # FIXME IMPLEMENT

VWE_SETFILEMETA     = 28 # (fname, key, value)

VWE_ADDCOLOR        = 29 # (mapname, colordict)
VWE_DELCOLOR        = 30 # mapname

VWE_ADDVASET        = 31 # (name, setdict)
VWE_DELVASET        = 32 # setname

VWE_ADDFREF         = 33 # (va, operidx, value)
VWE_DELFREF         = 34 # FIXME IMPLEMENT

VWE_SETVASETROW     = 35 # (name, rowtup)
VWE_DELVASETROW     = 36 # (name, va)

VWE_ADDFSIG         = 37 # (sigbytes, sigmask)
VWE_DELFSIG         = 38 # FIXME IMPLEMENT

VWE_FOLLOWME        = 39 # LEGACY - not in use.
VWE_CHAT            = 40 # (username, message)

VWE_SYMHINT         = 41 # (va, idx, hint)
VWE_AUTOANALFIN     = 42 # (starttime, endtime)

VWE_MAX             = 43

# Constants for vivisect "transient" events which flow through
# the event subsystem but are not recorded to the workspace.
VTE_MASK            = 0x80000000
VTE_IAMLEADER       = 1 # (user,followname)
VTE_FOLLOWME        = 2 # (user,followname,expr)
VTE_MAX             = 3

# API fields
API_RET_TYPE    = 0
API_RET_NAME    = 1
API_CCONV       = 2
API_FUNC_NAME   = 3
API_ARG_START   = 4

# Reference Types
# NOTE: All XREFs may have type specific flags
REF_CODE   = 1 # A branch/call
REF_DATA   = 2 # A memory dereference
REF_PTR    = 3 # A pointer immediate (may be in operand *or* part of LOC_PTR)

ref_type_names = {
    REF_CODE: "Code",
    REF_DATA: "Data",
    REF_PTR: "Pointer",
}

#NOTE: The flag values for REF_CODE are the envi.BR_FOO flags
#      which describe opcode branches.

#NOTE: All locations ltypes may not change (backward compat)
LOC_UNDEF   = 0  # An undefined "non-location"
LOC_NUMBER  = 1  # A numerical value (non-pointer)
LOC_STRING  = 2  # A null terminated string
LOC_UNI     = 3  # A null terminated unicode string
LOC_POINTER = 4  # A type to hold a known-derefable pointer that is of appropriate length for arch
LOC_OP      = 5  # An opcode
LOC_STRUCT  = 6  # A custom structure (struct name is in tinfo)
LOC_CLSID   = 7  # A clsid
LOC_VFTABLE = 8  # A c++ vftable
LOC_IMPORT  = 9  # An import dword ptr
LOC_PAD     = 10  # A sequence of bytes which is a pad (string nulls, MS hotpatch... (char is tinfo)
LOC_MAX     = 11

loc_lookups = {v:k for k,v in globals().items() if k.startswith('LOC_')}

loc_type_names = {
        LOC_UNDEF: 'Undefined',
        LOC_NUMBER: 'Num/Int',
        LOC_STRING: 'String',
        LOC_UNI: 'Unicode',
        LOC_POINTER: 'Pointer',
        LOC_OP: 'Opcode',
        LOC_STRUCT: 'Structure',
        LOC_CLSID: 'Clsid',
        LOC_VFTABLE: 'VFTable',
        LOC_IMPORT: 'Import Entry',
        LOC_PAD: 'Pad'
}

# Location tuples contain the following fields indexes.  Many types of
# tuples are used in vivisect for performance.  *most* try to implement
# va and size as the first 2 elements and are then called "Area Compatable"
L_VA    = 0
L_SIZE  = 1
L_LTYPE = 2
L_TINFO = 3

# Code-block tuples are Area Compatable code block descriptions that
# tie code blocks to functions.
CB_VA     = 0
CB_SIZE   = 1
CB_FUNCVA = 2

# Memory Map tuples are Area Compatable tuples that
# describe a loaded memory map
MAP_VA    = 0
MAP_SIZE  = 1
MAP_PERMS = 2
MAP_FNAME = 3

# Segment tuples are Area Compatable tuples that describe
# a "section" or "segment" inside a memory map.
SEG_VA    = 0
SEG_SIZE  = 1
SEG_NAME  = 2 # The name of the segment ".text" ".plt"
SEG_FNAME = 3 # The *normalized* name of the file

# XREF tuples *not* area compatable tuples
XR_FROM  = 0
XR_TO    = 1
XR_RTYPE = 2
XR_RFLAG = 3

# Export Types
EXP_UNTYPED  = 0xffffffff
EXP_FUNCTION = 0
EXP_DATA     = 1

# Relocation types
RTYPE_BASERELOC = 0 # VA contains a pointer to a va (and is assumed fixed up by parser)
RTYPE_BASEOFF   = 1 # Add Base and Offset to a pointer at a memory location
RTYPE_BASEPTR   = 2 # Like BASEOFF, but treated as a Pointer, not part of an instruction/etc.

REBASE_TYPES = (RTYPE_BASEOFF, RTYPE_BASEPTR)

# Function Local Symbol Types
LSYM_NAME   = 0 # syminfo is a (typestr,name) tuple
LSYM_FARG   = 1 # syminfo is an argument index


# vaset "type" constants
VASET_ADDRESS   = 0
VASET_INTEGER   = 1
VASET_STRING    = 2
VASET_HEXTUP    = 3
VASET_COMPLEX   = 4

# Symboliks effect types
EFFTYPE_DEBUG        = 0
EFFTYPE_SETVAR       = 1
EFFTYPE_READMEM      = 2
EFFTYPE_WRITEMEM     = 3
EFFTYPE_CALLFUNC     = 4
EFFTYPE_CONSTRAIN    = 5

# symboliks object types
SYMT_VAR            = 0
SYMT_ARG            = 1
SYMT_CALL           = 2
SYMT_MEM            = 3
SYMT_SEXT           = 4
SYMT_CONST          = 5
SYMT_LOOKUP         = 6
SYMT_NOT            = 7

SYMT_OPER           = 0x00010000
SYMT_OPER_ADD       = SYMT_OPER | 1
SYMT_OPER_SUB       = SYMT_OPER | 2
SYMT_OPER_MUL       = SYMT_OPER | 3
SYMT_OPER_DIV       = SYMT_OPER | 4
SYMT_OPER_AND       = SYMT_OPER | 5
SYMT_OPER_OR        = SYMT_OPER | 6
SYMT_OPER_XOR       = SYMT_OPER | 7
SYMT_OPER_MOD       = SYMT_OPER | 8
SYMT_OPER_LSHIFT    = SYMT_OPER | 9
SYMT_OPER_RSHIFT    = SYMT_OPER | 10
SYMT_OPER_POW       = SYMT_OPER | 11

SYMT_CON            = 0x00020000
SYMT_CON_EQ         = SYMT_CON | 1
SYMT_CON_NE         = SYMT_CON | 2
SYMT_CON_GT         = SYMT_CON | 3
SYMT_CON_GE         = SYMT_CON | 4
SYMT_CON_LT         = SYMT_CON | 5
SYMT_CON_LE         = SYMT_CON | 6
SYMT_CON_UNK        = SYMT_CON | 7
SYMT_CON_NOTUNK     = SYMT_CON | 8
