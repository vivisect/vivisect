"""
Win32 Platform Module
"""
# Copyright (C) 2007 Invisigoth - See LICENSE file for details
import os
import sys
import math
import struct
import logging
import traceback
import platform

import PE

import vstruct.builder as vs_builder
import vstruct.defs.win32 as vs_win32
import vstruct.defs.windows as vs_windows

import vtrace
import vtrace.archs.i386 as v_i386
import vtrace.archs.amd64 as v_amd64
import vtrace.platforms.base as v_base

import envi
import envi.bits as e_bits
import envi.const as e_const
import envi.archs.i386 as e_i386
import envi.archs.amd64 as e_amd64
import envi.symstore.resolver as e_resolv
import envi.symstore.symcache as e_symcache

import ctypes
from ctypes import *

logger = logging.getLogger(__name__)
platdir = os.path.dirname(__file__)

kernel32 = None
dbghelp = None
psapi = None
ntdll = None
advapi32 = None

IsWow64Process = None

# Setup some ctypes helpers:
# NOTE: we don't use LPVOID because it can return None.
#       c_size_t is the designated platform word width int.
LPVOID  = c_size_t
HANDLE  = LPVOID
SIZE_T  = LPVOID
QWORD   = c_ulonglong
DWORD   = c_ulong
WORD    = c_ushort
BOOL    = c_ulong
BYTE    = c_ubyte
NULL    = 0
LPCWSTR = LPWSTR = c_wchar_p
LPDWORD = PDWORD = ctypes.POINTER(DWORD)

INFINITE = 0xffffffff
EXCEPTION_MAXIMUM_PARAMETERS = 15

# Debug Event Types
EXCEPTION_DEBUG_EVENT       = 1
CREATE_THREAD_DEBUG_EVENT   = 2
CREATE_PROCESS_DEBUG_EVENT  = 3
EXIT_THREAD_DEBUG_EVENT     = 4
EXIT_PROCESS_DEBUG_EVENT    = 5
LOAD_DLL_DEBUG_EVENT        = 6
UNLOAD_DLL_DEBUG_EVENT      = 7
OUTPUT_DEBUG_STRING_EVENT   = 8
RIP_EVENT                   = 9

# Symbol Flags
SYMFLAG_VALUEPRESENT     = 0x00000001
SYMFLAG_REGISTER         = 0x00000008
SYMFLAG_REGREL           = 0x00000010
SYMFLAG_FRAMEREL         = 0x00000020
SYMFLAG_PARAMETER        = 0x00000040
SYMFLAG_LOCAL            = 0x00000080
SYMFLAG_CONSTANT         = 0x00000100
SYMFLAG_EXPORT           = 0x00000200
SYMFLAG_FORWARDER        = 0x00000400
SYMFLAG_FUNCTION         = 0x00000800
SYMFLAG_VIRTUAL          = 0x00001000
SYMFLAG_THUNK            = 0x00002000
SYMFLAG_TLSREL           = 0x00004000

# Symbol Resolution Options
SYMOPT_CASE_INSENSITIVE         = 0x00000001
SYMOPT_UNDNAME                  = 0x00000002
SYMOPT_DEFERRED_LOADS           = 0x00000004
SYMOPT_NO_CPP                   = 0x00000008
SYMOPT_LOAD_LINES               = 0x00000010
SYMOPT_OMAP_FIND_NEAREST        = 0x00000020
SYMOPT_LOAD_ANYTHING            = 0x00000040
SYMOPT_IGNORE_CVREC             = 0x00000080
SYMOPT_NO_UNQUALIFIED_LOADS     = 0x00000100
SYMOPT_FAIL_CRITICAL_ERRORS     = 0x00000200
SYMOPT_EXACT_SYMBOLS            = 0x00000400
SYMOPT_ALLOW_ABSOLUTE_SYMBOLS   = 0x00000800
SYMOPT_IGNORE_NT_SYMPATH        = 0x00001000
SYMOPT_INCLUDE_32BIT_MODULES    = 0x00002000
SYMOPT_PUBLICS_ONLY             = 0x00004000
SYMOPT_NO_PUBLICS               = 0x00008000
SYMOPT_AUTO_PUBLICS             = 0x00010000
SYMOPT_NO_IMAGE_SEARCH          = 0x00020000
SYMOPT_SECURE                   = 0x00040000
SYMOPT_NO_PROMPTS               = 0x00080000
SYMOPT_OVERWRITE                = 0x00100000
SYMOPT_DEBUG                    = 0x80000000

# Exception Types
EXCEPTION_WAIT_0                   = 0x00000000
EXCEPTION_ABANDONED_WAIT_0         = 0x00000080
EXCEPTION_USER_APC                 = 0x000000C0
EXCEPTION_TIMEOUT                  = 0x00000102
EXCEPTION_PENDING                  = 0x00000103
DBG_EXCEPTION_HANDLED              = 0x00010001
DBG_CONTINUE                       = 0x00010002
EXCEPTION_SEGMENT_NOTIFICATION     = 0x40000005
DBG_TERMINATE_THREAD               = 0x40010003
DBG_TERMINATE_PROCESS              = 0x40010004
DBG_CONTROL_C                      = 0x40010005
DBG_CONTROL_BREAK                  = 0x40010008
DBG_COMMAND_EXCEPTION              = 0x40010009
EXCEPTION_GUARD_PAGE_VIOLATION     = 0x80000001
EXCEPTION_DATATYPE_MISALIGNMENT    = 0x80000002
EXCEPTION_BREAKPOINT               = 0x80000003
STATUS_WX86_BREAKPOINT             = 0x4000001f
EXCEPTION_SINGLE_STEP              = 0x80000004
STATUS_WX86_SINGLE_STEP            = 0x4000001e
DBG_EXCEPTION_NOT_HANDLED          = 0x80010001
STATUS_BUFFER_OVERFLOW             = 0x80000005
STATUS_SUCCESS                     = 0x00000000
STATUS_INFO_LENGTH_MISMATCH        = 0xC0000004
EXCEPTION_ACCESS_VIOLATION         = 0xC0000005
EXCEPTION_IN_PAGE_ERROR            = 0xC0000006
EXCEPTION_INVALID_HANDLE           = 0xC0000008
EXCEPTION_NO_MEMORY                = 0xC0000017
EXCEPTION_ILLEGAL_INSTRUCTION      = 0xC000001D
EXCEPTION_NONCONTINUABLE_EXCEPTION = 0xC0000025
EXCEPTION_INVALID_DISPOSITION      = 0xC0000026
EXCEPTION_ARRAY_BOUNDS_EXCEEDED    = 0xC000008C
EXCEPTION_FLOAT_DENORMAL_OPERAND   = 0xC000008D
EXCEPTION_FLOAT_DIVIDE_BY_ZERO     = 0xC000008E
EXCEPTION_FLOAT_INEXACT_RESULT     = 0xC000008F
EXCEPTION_FLOAT_INVALID_OPERATION  = 0xC0000090
EXCEPTION_FLOAT_OVERFLOW           = 0xC0000091
EXCEPTION_FLOAT_STACK_CHECK        = 0xC0000092
EXCEPTION_FLOAT_UNDERFLOW          = 0xC0000093
EXCEPTION_INTEGER_DIVIDE_BY_ZERO   = 0xC0000094
EXCEPTION_INTEGER_OVERFLOW         = 0xC0000095
EXCEPTION_PRIVILEGED_INSTRUCTION   = 0xC0000096
EXCEPTION_STACK_OVERFLOW           = 0xC00000FD
EXCEPTION_CONTROL_C_EXIT           = 0xC000013A
EXCEPTION_FLOAT_MULTIPLE_FAULTS    = 0xC00002B4
EXCEPTION_FLOAT_MULTIPLE_TRAPS     = 0xC00002B5
EXCEPTION_REG_NAT_CONSUMPTION      = 0xC00002C9

# Context Info
CONTEXT_i386    = 0x00010000    # this assumes that i386 and
CONTEXT_i486    = 0x00010000    # i486 have identical context records
CONTEXT_AMD64   = 0x00100000    # For amd x64...

CONTEXT_CONTROL         = 0x00000001  # SS:SP, CS:IP, FLAGS, BP
CONTEXT_INTEGER         = 0x00000002  # AX, BX, CX, DX, SI, DI
CONTEXT_SEGMENTS        = 0x00000004  # DS, ES, FS, GS
CONTEXT_FLOATING_POINT  = 0x00000008  # 387 state
CONTEXT_DEBUG_REGISTERS = 0x00000010  # DB 0-3,6,7
CONTEXT_EXTENDED_REGISTERS  = 0x00000020  # cpu specific extensions
CONTEXT_FULL = (CONTEXT_CONTROL | CONTEXT_INTEGER | CONTEXT_SEGMENTS)
CONTEXT_ALL = (CONTEXT_CONTROL | CONTEXT_INTEGER | CONTEXT_SEGMENTS | CONTEXT_FLOATING_POINT | CONTEXT_DEBUG_REGISTERS | CONTEXT_EXTENDED_REGISTERS)


# Thread Permissions
THREAD_ALL_ACCESS = 0x001f03ff
PROCESS_ALL_ACCESS = 0x001f0fff

# Memory Permissions
PAGE_NOACCESS = 0x01
PAGE_READONLY = 0x02
PAGE_READWRITE = 0x04
PAGE_WRITECOPY = 0x08
PAGE_EXECUTE = 0x10
PAGE_EXECUTE_READ = 0x20
PAGE_EXECUTE_READWRITE = 0x40
PAGE_EXECUTE_WRITECOPY = 0x80
PAGE_GUARD = 0x100
PAGE_NOCACHE = 0x200
PAGE_WRITECOMBINE = 0x400

# Map win32 permissions to envi permissions
perm_lookup = {
    PAGE_NOACCESS:0,
    PAGE_READONLY:e_const.MM_READ,
    PAGE_READWRITE: e_const.MM_READ | e_const.MM_WRITE,
    PAGE_WRITECOPY: e_const.MM_READ | e_const.MM_WRITE,
    PAGE_EXECUTE: e_const.MM_EXEC,
    PAGE_EXECUTE_READ: e_const.MM_EXEC | e_const.MM_READ,
    PAGE_EXECUTE_READWRITE: e_const.MM_EXEC | e_const.MM_READ | e_const.MM_WRITE,
    PAGE_EXECUTE_WRITECOPY: e_const.MM_EXEC | e_const.MM_READ | e_const.MM_WRITE,
}

# To get win32 permssions from envi permissions
perm_rev_lookup = {
    0:PAGE_NOACCESS,
    e_const.MM_READ:PAGE_READONLY,
    e_const.MM_READ|e_const.MM_WRITE:PAGE_READWRITE,
    e_const.MM_EXEC:PAGE_EXECUTE,
    e_const.MM_EXEC|e_const.MM_READ:PAGE_EXECUTE_READ,
    e_const.MM_EXEC|e_const.MM_READ|e_const.MM_WRITE:PAGE_EXECUTE_READWRITE,
}

# Memory States
MEM_COMMIT = 0x1000
MEM_FREE = 0x10000
MEM_RESERVE = 0x2000

# Memory Types
MEM_IMAGE = 0x1000000
MEM_MAPPED = 0x40000
MEM_PRIVATE = 0x20000

# Process Creation Flags
DEBUG_ONLY_THIS_PROCESS = 0x02

MAX_PATH=260


# System Status Codes from https://docs.microsoft.com/en-us/windows/win32/debug/system-error-codes--0-499-
ERROR_SUCCESS = 0
ERROR_INVALID_FUNCTION = 1
ERROR_FILE_NOT_FOUND = 2
ERROR_NO_MORE_FILES = 18

class MSR(Structure):
    _fields_ = [
        ('msr', DWORD),
        ('value', QWORD),
    ]

# The enum of NtSystemDebugControl operations
SysDbgQueryModuleInformation = 0
SysDbgQueryTraceInformation = 1
SysDbgSetTracepoint = 2
SysDbgSetSpecialCall = 3
SysDbgClearSpecialCalls = 4
SysDbgQuerySpecialCalls = 5
SysDbgBreakPoint = 6
SysDbgQueryVersion = 7
SysDbgReadVirtual = 8
SysDbgWriteVirtual = 9
SysDbgReadPhysical = 10
SysDbgWritePhysical = 11
SysDbgReadControlSpace = 12
SysDbgWriteControlSpace = 13
SysDbgReadIoSpace = 14
SysDbgWriteIoSpace = 15
SysDbgReadMsr = 16
SysDbgWriteMsr = 17
SysDbgReadBusData = 18
SysDbgWriteBusData = 19
SysDbgCheckLowMemory = 20
SysDbgEnableKernelDebugger = 21
SysDbgDisableKernelDebugger = 22
SysDbgGetAutoKdEnable = 23
SysDbgSetAutoKdEnable = 24
SysDbgGetPrintBufferSize = 25
SysDbgSetPrintBufferSize = 26
SysDbgGetKdUmExceptionEnable = 27
SysDbgSetKdUmExceptionEnable = 28
SysDbgGetTriageDump = 29
SysDbgGetKdBlockEnable = 30
SysDbgSetKdBlockEnable = 31
SysDbgRegisterForUmBreakInfo = 32
SysDbgGetUmBreakPid = 33
SysDbgClearUmBreakPid = 34
SysDbgGetUmAttachPid = 35
SysDbgClearUmAttachPid = 36

def wrmsr(msrid, value):
    m = MSR()
    m.msr = msrid
    m.value = value
    mptr = addressof(m)
    x = ntdll.NtSystemDebugControl(SysDbgWriteMsr, mptr, sizeof(m), 0, 0, 0)
    if x != 0:
        raise vtrace.PlatformException('NtSystemDebugControl Failed: 0x%.8x' % kernel32.GetLastError())
    return 0

def rdmsr(msrid):
    m = MSR()
    m.msr = msrid
    m.value = 0

    mptr = addressof(m)
    msize = sizeof(m)

    x = ntdll.NtSystemDebugControl(SysDbgReadMsr, mptr, msize, mptr, msize, 0)
    if x != 0:
        raise vtrace.PlatformException('NtSystemDebugControl Failed: 0x%.8x' % kernel32.GetLastError())
    return m.value

SC_MANAGER_ALL_ACCESS           = 0xF003F
SC_MANAGER_CREATE_SERVICE       = 0x0002
SC_MANAGER_CONNECT              = 0x0001
SC_MANAGER_ENUMERATE_SERVICE    = 0x0004
SC_MANAGER_LOCK                 = 0x0008
SC_MANAGER_MODIFY_BOOT_CONFIG   = 0x0020
SC_MANAGER_QUERY_LOCK_STATUS    = 0x0010

SC_ENUM_PROCESS_INFO = 0

SERVICE_WIN32       = 0x30

SERVICE_ACTIVE      = 0x01
SERVICE_INNACTIVE   = 0x02
SERVICE_STATE_ALL   = 0x03

class SERVICE_STATUS_PROCESS(Structure):
    _fields_ = [
            ('dwServiceType', DWORD),
            ('dwCurrentState', DWORD),
            ('dwControlsAccepted', DWORD),
            ('dwWin32ExitCode', DWORD),
            ('dwServiceSpecificExitCode',DWORD),
            ('dwCheckPoint', DWORD),
            ('dwWaitHint', DWORD),
            ('dwProcessId', DWORD),
            ('dwServiceFlags', DWORD)
    ]

class ENUM_SERVICE_STATUS_PROCESS(Structure):
    _fields_ = [
            ('lpServiceName', c_wchar_p),
            ('lpDisplayName', c_wchar_p),
            ('ServiceStatusProcess', SERVICE_STATUS_PROCESS),
    ]

class EXCEPTION_RECORD(Structure):
    _fields_ = [
            ("ExceptionCode", DWORD),
            ("ExceptionFlags", DWORD),
            ("ExceptionRecord", LPVOID),
            ("ExceptionAddress", LPVOID),
            ("NumberParameters", c_ulong),
            ("ExceptionInformation", LPVOID * EXCEPTION_MAXIMUM_PARAMETERS)
            ]

class EXCEPTION_DEBUG_INFO(Structure):
    _fields_ = [
            ("ExceptionRecord", EXCEPTION_RECORD),
            ("FirstChance", c_ulong)
            ]

class CREATE_THREAD_DEBUG_INFO(Structure):
    _fields_ = [
            ("Thread", HANDLE),
            ("ThreadLocalBase", LPVOID),
            ("StartAddress", LPVOID)
            ]

class CREATE_PROCESS_DEBUG_INFO(Structure):
    _fields_ = [
            ("File", HANDLE),
            ("Process", HANDLE),
            ("Thread", HANDLE),
            ("BaseOfImage", LPVOID),
            ("DebugInfoFileOffset", c_ulong),
            ("DebugInfoSize", c_ulong),
            ("ThreadLocalBase", LPVOID),
            ("StartAddress", LPVOID),
            ("ImageName", LPVOID),
            ("Unicode", c_short),
            ]

class EXIT_THREAD_DEBUG_INFO(Structure):
    _fields_ = [("ExitCode", c_ulong),]

class EXIT_PROCESS_DEBUG_INFO(Structure):
    _fields_ = [("ExitCode", c_ulong),]

class LOAD_DLL_DEBUG_INFO(Structure):
    _fields_ = [
            ("File", HANDLE),
            ("BaseOfDll", LPVOID),
            ("DebugInfoFileOffset", c_ulong),
            ("DebugInfoSize", c_ulong),
            ("ImageName", LPVOID),
            ("Unicode", c_ushort),
            ]
class UNLOAD_DLL_DEBUG_INFO(Structure):
    _fields_ = [
            ("BaseOfDll", LPVOID),
            ]
class OUTPUT_DEBUG_STRING_INFO(Structure):
    _fields_ = [
            ("DebugStringData", LPVOID),
            ("Unicode", c_ushort),
            ("DebugStringLength", c_ushort),
            ]
class RIP_INFO(Structure):
    _fields_ = [
            ("Error", c_ulong),
            ("Type", c_ulong),
            ]

class DBG_EVENT_UNION(Union):
    _fields_ = [ ("Exception",EXCEPTION_DEBUG_INFO),
                 ("CreateThread", CREATE_THREAD_DEBUG_INFO),
                 ("CreateProcessInfo", CREATE_PROCESS_DEBUG_INFO),
                 ("ExitThread", EXIT_THREAD_DEBUG_INFO),
                 ("ExitProcess", EXIT_PROCESS_DEBUG_INFO),
                 ("LoadDll", LOAD_DLL_DEBUG_INFO),
                 ("UnloadDll", UNLOAD_DLL_DEBUG_INFO),
                 ("DebugString", OUTPUT_DEBUG_STRING_INFO),
                 ("RipInfo", RIP_INFO)]

class DEBUG_EVENT(Structure):
    _fields_ = [
            ("DebugEventCode", c_ulong),
            ("ProcessId", c_ulong),
            ("ThreadId", c_ulong),
            ("u", DBG_EVENT_UNION),
            ]

class FloatSavex86(Structure):
    _fields_ = [("ControlWord", c_ulong),
                  ("StatusWord", c_ulong),
                  ("TagWord", c_ulong),
                  ("ErrorOffset", c_ulong),
                  ("ErrorSelector", c_ulong),
                  ("DataOffset", c_ulong),
                  ("DataSelector", c_ulong),
                  ("RegisterSave", c_byte*80),
                  ("Cr0NpxState", c_ulong),
                  ]

class CONTEXTx64(Structure):
    _fields_ = [

        ("P1Home",c_ulonglong),
        ("P2Home",c_ulonglong),
        ("P3Home",c_ulonglong),
        ("P4Home",c_ulonglong),
        ("P5Home",c_ulonglong),
        ("P6Home",c_ulonglong),

        ("ContextFlags", DWORD),
        ("MxCsr",DWORD),

        ("cs",WORD),
        ("ds",WORD),
        ("es",WORD),
        ("fs", WORD),
        ("gs",WORD),
        ("ss",WORD),
        ("eflags",DWORD),

        ("debug0",c_ulonglong),
        ("debug1",c_ulonglong),
        ("debug2",c_ulonglong),
        ("debug3",c_ulonglong),
        ("debug6",c_ulonglong),
        ("debug7",c_ulonglong),

        ("rax",c_ulonglong),
        ("rcx",c_ulonglong),
        ("rdx",c_ulonglong),
        ("rbx",c_ulonglong),
        ("rsp",c_ulonglong),
        ("rbp",c_ulonglong),
        ("rsi",c_ulonglong),
        ("rdi",c_ulonglong),
        ("r8",c_ulonglong),
        ("r9",c_ulonglong),
        ("r10",c_ulonglong),
        ("r11",c_ulonglong),
        ("r12",c_ulonglong),
        ("r13",c_ulonglong),
        ("r14",c_ulonglong),
        ("r15",c_ulonglong),
        ("rip",c_ulonglong),

        ("foo",c_ulonglong*200),

        #union {
            #XMM_SAVE_AREA32 FltSave,
            #struct {
                #M128A Header[2],
                #M128A Legacy[8],
                #M128A Xmm0,
                #M128A Xmm1,
                #M128A Xmm2,
                #M128A Xmm3,
                #M128A Xmm4,
                #M128A Xmm5,
                #M128A Xmm6,
                #M128A Xmm7,
                #M128A Xmm8,
                #M128A Xmm9,
                #M128A Xmm10,
                #M128A Xmm11,
                #M128A Xmm12,
                #M128A Xmm13,
                #M128A Xmm14,
                #M128A Xmm15,
            #},
        #},

        #M128A VectorRegister[26],
        #(VectorControl,c_ulonglong),

        #(DebugControl,c_ulonglong),
        #(LastBranchToRip,c_ulonglong),
        #(LastBranchFromRip,c_ulonglong),
        #(LastExceptionToRip,c_ulonglong),
        #(LastExceptionFromRip,c_ulonglong),
    ]

    def regPostProcess(self):
        pass

# Used for xmm registers
class M128A(Structure):
    _fields_ = [
            ('Low', c_ulonglong),
            ('High', c_ulonglong),
    ]

class ExtendedXmmx86(Structure):
    _fields_ = [
            ('Header', M128A * 2),
            ('Legacy', M128A * 8),
            ('_xmm0',   M128A),
            ('_xmm1',   M128A),
            ('_xmm2',   M128A),
            ('_xmm3',   M128A),
            ('_xmm4',   M128A),
            ('_xmm5',   M128A),
            ('_xmm6',   M128A),
            ('_xmm7',   M128A),
            ("Pad", c_byte * 224),
    ]

class CONTEXTx86(Structure):
    _fields_ = [   ("ContextFlags", c_ulong),
                   ("debug0", c_ulong),
                   ("debug1", c_ulong),
                   ("debug2", c_ulong),
                   ("debug3", c_ulong),
                   ("debug6", c_ulong),
                   ("debug7", c_ulong),
                   ("FloatSave", FloatSavex86),
                   ("gs", c_ulong),
                   ("fs", c_ulong),
                   ("es", c_ulong),
                   ("ds", c_ulong),
                   ("edi", c_ulong),
                   ("esi", c_ulong),
                   ("ebx", c_ulong),
                   ("edx", c_ulong),
                   ("ecx", c_ulong),
                   ("eax", c_ulong),
                   ("ebp", c_ulong),
                   ("eip", c_ulong),
                   ("cs", c_ulong),
                   ("eflags", c_ulong),
                   ("esp", c_ulong),
                   ("ss", c_ulong),

                   #("Extension", c_byte * 512),
                   ('Extension', ExtendedXmmx86),

                    #M128A Header[2],
                    #M128A Legacy[8],
                    #M128A Xmm0,
                    #M128A Xmm1,
                    #M128A Xmm2,
                    #M128A Xmm3,
                    #M128A Xmm4,
                    #M128A Xmm5,
                    #M128A Xmm6,
                    #M128A Xmm7,
                   ]

    def regPostProcess(self):
        self.xmm0 = (self.Extension._xmm0.High << 8) + self.Extension._xmm0.Low
        self.xmm1 = (self.Extension._xmm1.High << 8) + self.Extension._xmm1.Low
        self.xmm2 = (self.Extension._xmm2.High << 8) + self.Extension._xmm2.Low
        self.xmm3 = (self.Extension._xmm3.High << 8) + self.Extension._xmm3.Low
        self.xmm4 = (self.Extension._xmm4.High << 8) + self.Extension._xmm4.Low
        self.xmm5 = (self.Extension._xmm5.High << 8) + self.Extension._xmm5.Low
        self.xmm6 = (self.Extension._xmm6.High << 8) + self.Extension._xmm6.Low
        self.xmm7 = (self.Extension._xmm7.High << 8) + self.Extension._xmm7.Low

class MEMORY_BASIC_INFORMATION(Structure):
    _fields_ = [
        ("BaseAddress", SIZE_T),
        ("AllocationBase", SIZE_T),
        ("AllocationProtect", DWORD),
        ("RegionSize", SIZE_T),
        ("State", DWORD),
        ("Protect", DWORD),
        ("Type", DWORD),
        ]

class STARTUPINFO(Structure):
    """
    Passed into CreateProcess
    """
    _fields_ = [
            ("db", c_ulong),
            ("Reserved", c_char_p),
            ("Desktop", c_char_p),
            ("Title", c_char_p),
            ("X", c_ulong),
            ("Y", c_ulong),
            ("XSize", c_ulong),
            ("YSize", c_ulong),
            ("XCountChars", c_ulong),
            ("YCountChars", c_ulong),
            ("FillAttribute", c_ulong),
            ("Flags", c_ulong),
            ("ShowWindow", c_ushort),
            ("Reserved2", c_ushort),
            ("Reserved3", LPVOID),
            ("StdInput", c_ulong),
            ("StdOutput", c_ulong),
            ("StdError", c_ulong),
            ]

class PROCESS_INFORMATION(Structure):
    _fields_ = [
            ("Process", HANDLE),
            ("Thread", HANDLE),
            ("ProcessId", c_ulong),
            ("ThreadId", c_ulong),
            ]

class SYMBOL_INFO(Structure):
    _fields_ = [
                ("SizeOfStruct", c_ulong),
                ("TypeIndex", c_ulong),
                ("Reserved1", c_ulonglong),
                ("Reserved2", c_ulonglong),
                ("Index", c_ulong),
                ("Size", c_ulong),
                ("ModBase", c_ulonglong),
                ("Flags", c_ulong),
                ("Value", c_ulonglong),
                ("Address", c_ulonglong),
                ("Register", c_ulong),
                ("Scope", c_ulong),
                ("Tag", c_ulong),
                ("NameLen", c_ulong),
                ("MaxNameLen", c_ulong),
                ("Name", c_char * 2000), # MAX_SYM_NAME
                ]

class IMAGEHLP_MODULE64(Structure):
    _fields_ = [
            ("SizeOfStruct", c_ulong),
            ("BaseOfImage", c_ulonglong),
            ("ImageSize", c_ulong),
            ("TimeDateStamp", c_ulong),
            ("CheckSum", c_ulong),
            ("NumSyms", c_ulong),
            ("SymType", c_ulong),
            ("ModuleName", c_char*32),
            ("ImageName", c_char*256),
            ("LoadedImageName", c_char*256),
            ("LoadedPdbName", c_char*256),
            ("CvSig", c_ulong),
            ("CvData", c_char*(MAX_PATH*3)),
            ("PdbSig", c_ulong),
            ("PdbSig70", c_char * 16), #GUID
            ("PdbAge", c_ulong),
            ("PdbUnmatched", c_ulong),
            ("DbgUnmatched", c_ulong),
            ("LineNumbers", c_ulong),
            ("GlobalSymbols", c_ulong),
            ("TypeInfo", c_ulong),
            ]

class IMAGEHLP_STACK_FRAME(Structure):
    _fields_ = [
        ('InstructionOffset',     QWORD),
        ('ReturnOffset',          QWORD),
        ('FrameOffset',           QWORD),
        ('StackOffset',           QWORD),
        ('BackingStoreOffset',    QWORD),
        ('FuncTableEntry',        QWORD),
        ('Params',                QWORD*4),
        ('Reserved',              QWORD*5),
        ('Virtual',               BOOL),
        ('Reserved2',             DWORD),
    ]

IMAGE_DIRECTORY_ENTRY_EXPORT          =0   # Export Directory
IMAGE_DIRECTORY_ENTRY_IMPORT          =1   # Import Directory
IMAGE_DIRECTORY_ENTRY_RESOURCE        =2   # Resource Directory
IMAGE_DIRECTORY_ENTRY_EXCEPTION       =3   # Exception Directory
IMAGE_DIRECTORY_ENTRY_SECURITY        =4   # Security Directory
IMAGE_DIRECTORY_ENTRY_BASERELOC       =5   # Base Relocation Table
IMAGE_DIRECTORY_ENTRY_DEBUG           =6   # Debug Directory
IMAGE_DIRECTORY_ENTRY_COPYRIGHT       =7   # (X86 usage)
IMAGE_DIRECTORY_ENTRY_ARCHITECTURE    =7   # Architecture Specific Data
IMAGE_DIRECTORY_ENTRY_GLOBALPTR       =8   # RVA of GP
IMAGE_DIRECTORY_ENTRY_TLS             =9   # TLS Directory
IMAGE_DIRECTORY_ENTRY_LOAD_CONFIG    =10   # Load Configuration Directory
IMAGE_DIRECTORY_ENTRY_BOUND_IMPORT   =11   # Bound Import Directory in headers
IMAGE_DIRECTORY_ENTRY_IAT            =12   # Import Address Table
IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT   =13   # Delay Load Import Descriptors
IMAGE_DIRECTORY_ENTRY_COM_DESCRIPTOR =14   # COM Runtime descriptor

IMAGE_DEBUG_TYPE_UNKNOWN          =0
IMAGE_DEBUG_TYPE_COFF             =1
IMAGE_DEBUG_TYPE_CODEVIEW         =2
IMAGE_DEBUG_TYPE_FPO              =3
IMAGE_DEBUG_TYPE_MISC             =4
IMAGE_DEBUG_TYPE_EXCEPTION        =5
IMAGE_DEBUG_TYPE_FIXUP            =6
IMAGE_DEBUG_TYPE_OMAP_TO_SRC      =7
IMAGE_DEBUG_TYPE_OMAP_FROM_SRC    =8
IMAGE_DEBUG_TYPE_BORLAND          =9
IMAGE_DEBUG_TYPE_RESERVED10       =10
IMAGE_DEBUG_TYPE_CLSID            =11

SSRVOPT_CALLBACK            = 0x0001
SSRVOPT_DWORD               = 0x0002
SSRVOPT_DWORDPTR            = 0x0004
SSRVOPT_GUIDPTR             = 0x0008
SSRVOPT_OLDGUIDPTR          = 0x0010
SSRVOPT_UNATTENDED          = 0x0020
SSRVOPT_NOCOPY              = 0x0040
SSRVOPT_PARENTWIN           = 0x0080
SSRVOPT_PARAMTYPE           = 0x0100
SSRVOPT_SECURE              = 0x0200
SSRVOPT_TRACE               = 0x0400
SSRVOPT_SETCONTEXT          = 0x0800
SSRVOPT_PROXY               = 0x1000
SSRVOPT_DOWNSTREAM_STORE    = 0x2000

TI_GET_SYMTAG                   = 0
TI_GET_SYMNAME                  = 1
TI_GET_LENGTH                   = 2
TI_GET_TYPE                     = 3
TI_GET_TYPEID                   = 4
TI_GET_BASETYPE                 = 5
TI_GET_ARRAYINDEXTYPEID         = 6
TI_FINDCHILDREN                 = 7
TI_GET_DATAKIND                 = 8
TI_GET_ADDRESSOFFSET            = 9
TI_GET_OFFSET                   = 10
TI_GET_VALUE                    = 11
TI_GET_COUNT                    = 12
TI_GET_CHILDRENCOUNT            = 13
TI_GET_BITPOSITION              = 14
TI_GET_VIRTUALBASECLASS         = 15
TI_GET_VIRTUALTABLESHAPEID      = 16
TI_GET_VIRTUALBASEPOINTEROFFSET = 17
TI_GET_CLASSPARENTID            = 18
TI_GET_NESTED                   = 19
TI_GET_SYMINDEX                 = 20
TI_GET_LEXICALPARENT            = 21
TI_GET_ADDRESS                  = 22
TI_GET_THISADJUST               = 23
TI_GET_UDTKIND                  = 24
TI_IS_EQUIV_TO                  = 25
TI_GET_CALLING_CONVENTION       = 26

SymTagNull              = 0
SymTagExe               = 1
SymTagCompiland         = 2
SymTagCompilandDetails  = 3
SymTagCompilandEnv      = 4
SymTagFunction          = 5
SymTagBlock             = 6
SymTagData              = 7
SymTagAnnotation        = 8
SymTagLabel             = 9
SymTagPublicSymbol      = 10
SymTagUDT               = 11
SymTagEnum              = 12
SymTagFunctionType      = 13
SymTagPointerType       = 14
SymTagArrayType         = 15
SymTagBaseType          = 16
SymTagTypedef           = 17
SymTagBaseClass         = 18
SymTagFriend            = 19
SymTagFunctionArgType   = 20
SymTagFuncDebugStart    = 21
SymTagFuncDebugEnd      = 22
SymTagUsingNamespace    = 23
SymTagVTableShape       = 24
SymTagVTable            = 25
SymTagCustom            = 26
SymTagThunk             = 27
SymTagCustomType        = 28
SymTagManagedType       = 29
SymTagDimension         = 30
SymTagMax               = 31

class IMAGE_DEBUG_DIRECTORY(Structure):
    _fields_ = [
            ("Characteristics", c_ulong),
            ("TimeDateStamp", c_ulong),
            ("MajorVersion", c_ushort),
            ("MinorVersion", c_ushort),
            ("Type", c_ulong),
            ("SizeOfData", c_ulong),
            ("AddressOfRawData", c_ulong),
            ("PointerToRawData", c_ulong),
            ]

NT_LIST_HANDLES = 16

ACCESS_MASK = DWORD
class SYSTEM_HANDLE(Structure):
    _fields_ = [
    ('ProcessID'        , c_ulong),
    ('HandleType'       , c_byte),
    ('Flags'            , c_byte),
    ('HandleNumber' , c_ushort),
    ('KernelAddress'    , LPVOID),
    ('GrantedAccess'    , ACCESS_MASK),
    ]
PSYSTEM_HANDLE = POINTER(SYSTEM_HANDLE)

# OBJECT_INFORMATION_CLASS
ObjectBasicInformation      = 0
ObjectNameInformation       = 1
ObjectTypeInformation       = 2
ObjectAllTypesInformation   = 3
ObjectHandleInformation     = 4

# ProcessInformationClass
ProcessBasicInformation = 0  # Get pointer to PEB
ProcessDebugPort        = 7  # Get DWORD_PTR to debug port number
ProcessWow64Information = 26 # Get WOW64 status
# FIXME may be more reliable to use this! \|/
ProcessImageFileName    = 27 # Get a UNICODE_STRING of the filename
ProcessExecuteFlags     = 34 # Get DWORD of execute status (including DEP) (bug: your process only)

class UNICODE_STRING(Structure):
    _fields_ = (
        ("Length",c_ushort),
        ("MaximumLength", c_ushort),
        ("Buffer", c_wchar_p)
    )
PUNICODE_STRING = POINTER(UNICODE_STRING)

class OBJECT_TYPE_INFORMATION(Structure):
    _fields_ = (
        ("String",UNICODE_STRING),
        ("reserved", c_uint * 22)
    )

object_type_map = {
    "File":vtrace.FD_FILE,
    "Directory":vtrace.FD_FILE,
    "Event":vtrace.FD_EVENT,
    "KeyedEvent":vtrace.FD_EVENT,
    "Mutant":vtrace.FD_LOCK,
    "Semaphore":vtrace.FD_LOCK,
    "Key":vtrace.FD_REGKEY,
    "Port":vtrace.FD_UNKNOWN,
    "Section":vtrace.FD_UNKNOWN,
    "IoCompletion":vtrace.FD_UNKNOWN,
    "Desktop":vtrace.FD_UNKNOWN,
    "WindowStation":vtrace.FD_UNKNOWN,
}

class LUID(Structure):
    _fields_ = (
        ("LowPart", c_ulong),
        ("HighPart", c_ulong)
    )

class TOKEN_PRIVILEGES(Structure):
    # This isn't really universal, more just for one priv use
    _fields_ = (
        ("PrivilegeCount", c_ulong), # Always one
        ("Privilege", LUID),
        ("PrivilegeAttribute", c_ulong)
    )

def loadlib(path):
    # returns None rather than exceptioning
    try:
        return windll.LoadLibrary(path)
    except Exception as e:
        logger.warning('LoadLibrary %s: %s', path, e)

# All platforms must be able to import this module (for exceptions etc..)
# (do this stuff *after* we define some types...)
if sys.platform == "win32":

    kernel32 = windll.kernel32
    # We need to inform some of the APIs about their args
    kernel32.GetLastError.argtypes = []
    kernel32.GetLastError.restype = DWORD
    kernel32.OpenProcess.argtypes = [DWORD, BOOL, DWORD]
    kernel32.OpenProcess.restype = HANDLE
    kernel32.CreateProcessA.argtypes = [LPVOID, c_char_p, LPVOID, LPVOID, c_uint, DWORD, LPVOID, LPVOID, LPVOID, LPVOID]
    kernel32.ReadProcessMemory.argtypes = [HANDLE, LPVOID, LPVOID, SIZE_T, LPVOID]
    kernel32.ReadProcessMemory.restype = BOOL
    kernel32.WriteProcessMemory.argtypes = [HANDLE, LPVOID, c_char_p, SIZE_T, LPVOID]
    kernel32.WriteProcessMemory.restype = BOOL
    kernel32.GetThreadContext.argtypes = [HANDLE, LPVOID]
    kernel32.SetThreadContext.argtypes = [HANDLE, LPVOID]
    kernel32.CreateRemoteThread.argtypes = [HANDLE, LPVOID, SIZE_T, LPVOID, LPVOID, DWORD, LPVOID]
    kernel32.SuspendThread.argtypes = [HANDLE,]
    kernel32.ResumeThread.argtypes = [HANDLE,]
    kernel32.ResumeThread.restype = DWORD
    kernel32.ContinueDebugEvent.argtypes = [DWORD, DWORD, DWORD]
    kernel32.ContinueDebugEvent.restype = BOOL
    kernel32.VirtualQueryEx.argtypes = [HANDLE, LPVOID, LPVOID, SIZE_T]
    kernel32.DebugBreakProcess.argtypes = [HANDLE,]
    kernel32.CloseHandle.argtypes = [HANDLE,]
    kernel32.GetLogicalDriveStringsA.argtypes = [DWORD, LPVOID]
    kernel32.TerminateProcess.argtypes = [HANDLE, DWORD]
    kernel32.VirtualProtectEx.argtypes = [HANDLE, LPVOID, SIZE_T, DWORD, LPVOID]
    kernel32.VirtualAllocEx.argtypes = [HANDLE, LPVOID, SIZE_T, DWORD, DWORD]
    kernel32.VirtualAllocEx.restype = c_void_p
    kernel32.VirtualFreeEx.argtypes = [HANDLE, LPVOID, SIZE_T, DWORD]
    kernel32.DuplicateHandle.argtypes = [HANDLE, HANDLE, HANDLE, LPVOID, DWORD, DWORD, DWORD]
    kernel32.SetEvent.argtypes = [HANDLE, ]
    kernel32.FormatMessageW.argtypes = [DWORD, LPVOID, DWORD, DWORD, LPVOID, DWORD, LPVOID]
    kernel32.WaitForDebugEvent.argtypes = [LPVOID, DWORD]

    kernel32.QueryDosDeviceW.argtypes = [LPCWSTR, LPWSTR, DWORD]
    kernel32.FindFirstVolumeW.argtypes = [LPWSTR, DWORD]
    kernel32.FindFirstVolumeW.restype = HANDLE
    kernel32.FindNextVolumeW.argtypes = [HANDLE, LPWSTR, DWORD]
    kernel32.FindNextVolumeW.restype  = BOOL
    kernel32.FindVolumeClose.argtypes = [HANDLE]
    kernel32.FindVolumeClose.restype = BOOL
    kernel32.GetVolumePathNamesForVolumeNameW.argtypes = [LPWSTR, LPWSTR, DWORD, PDWORD]
    kernel32.GetVolumePathNamesForVolumeNameW.restype = BOOL

    IsWow64Process = getattr(kernel32, 'IsWow64Process', None)
    if IsWow64Process is not None:
        IsWow64Process.argtypes = [HANDLE, LPVOID]

    psapi = windll.psapi
    psapi.GetModuleFileNameExW.argtypes = [HANDLE, HANDLE, LPVOID, DWORD]
    psapi.GetMappedFileNameW.argtypes = [HANDLE, LPVOID, LPVOID, DWORD]
    psapi.GetModuleBaseNameW.argtypes = [HANDLE, HANDLE, c_wchar_p, DWORD]
    psapi.EnumProcesses.argtypes = [LPVOID, DWORD, LPVOID]
    psapi.EnumProcessModules.argtypes = [HANDLE, HANDLE, DWORD, LPVOID]

    ntdll = windll.ntdll
    ntdll.NtQuerySystemInformation.argtypes = [DWORD, LPVOID, DWORD, LPVOID]
    ntdll.NtQueryObject.argtypes = [HANDLE, DWORD, c_void_p, DWORD, LPVOID]
    ntdll.NtQueryObject.restype = c_ulong
    ntdll.NtQueryInformationProcess.argtypes = [HANDLE, DWORD, c_void_p, DWORD, LPVOID]
    ntdll.NtSystemDebugControl.restype = SIZE_T

    arch = envi.getCurrentArch()

    SYMCALLBACK = WINFUNCTYPE(BOOL, POINTER(SYMBOL_INFO), c_ulong, LPVOID)
    PDBCALLBACK = WINFUNCTYPE(BOOL, c_char_p, LPVOID)

    symsrv = loadlib( os.path.join(platdir,'windll', arch, 'symsrv.dll') )
    dbghelp = loadlib( os.path.join(platdir,'windll', arch, 'dbghelp.dll') )

    if dbghelp is not None:
        dbghelp.SymInitialize.argtypes = [HANDLE, c_char_p, BOOL]
        dbghelp.SymInitialize.restype = BOOL
        dbghelp.SymSetOptions.argtypes = [DWORD]
        dbghelp.SymSetOptions.restype = DWORD
        dbghelp.SymCleanup.argtypes = [HANDLE]
        dbghelp.SymCleanup.restype = BOOL
        dbghelp.SymLoadModule64.argtypes = [HANDLE, HANDLE, c_char_p, c_char_p, QWORD, DWORD]
        dbghelp.SymLoadModule64.restype = QWORD
        dbghelp.SymGetModuleInfo64.argtypes = [HANDLE, QWORD, POINTER(IMAGEHLP_MODULE64)]
        dbghelp.SymSetContext.restype = BOOL
        dbghelp.SymSetContext.argtypes = [ HANDLE, POINTER(IMAGEHLP_STACK_FRAME), LPVOID ]
        dbghelp.SymGetModuleInfo64.restype = BOOL
        dbghelp.SymEnumSymbols.argtypes = [HANDLE, QWORD, c_char_p, SYMCALLBACK, LPVOID]
        dbghelp.SymEnumSymbols.restype = BOOL
        dbghelp.SymEnumTypes.argtypes = [HANDLE, QWORD, SYMCALLBACK, LPVOID]
        dbghelp.SymEnumTypes.restype = BOOL
        dbghelp.SymGetTypeInfo.argtypes = [HANDLE, QWORD, DWORD, DWORD, c_void_p]
        dbghelp.SymGetTypeInfo.restype = BOOL
        dbghelp.SymFromAddr.argtypes = [HANDLE, QWORD, POINTER(QWORD), POINTER(SYMBOL_INFO) ]

    advapi32 = windll.advapi32
    advapi32.LookupPrivilegeValueA.argtypes = [LPVOID, c_char_p, LPVOID]
    advapi32.OpenProcessToken.argtypes = [HANDLE, DWORD, HANDLE]
    advapi32.AdjustTokenPrivileges.argtypes = [HANDLE, DWORD, LPVOID, DWORD, LPVOID, LPVOID]
    advapi32.OpenSCManagerA.argtypes = [ LPVOID, LPVOID, DWORD ]
    advapi32.OpenSCManagerA.restype = HANDLE
    advapi32.EnumServicesStatusExW.argtypes = [ HANDLE,
                                                LPVOID,
                                                DWORD,
                                                DWORD,
                                                LPVOID,
                                                DWORD,
                                                LPVOID,
                                                LPVOID,
                                                LPVOID,
                                                LPVOID ]
    advapi32.EnumServicesStatusExW.restype = BOOL
    advapi32.CloseServiceHandle.argtypes = [ HANDLE, ]
    advapi32.CloseServiceHandle.restype = BOOL
    advapi32.GetTokenInformation.argtypes = [HANDLE, DWORD, LPVOID, DWORD, LPVOID]
    advapi32.GetTokenInformation.restype = BOOL

def getFormatMessage(err, isNtStatusCode):
    '''
    Given an error code look up via win32 FormatMessage API.
    '''
    if isNtStatusCode:
        dwFlags = 0x1800
        dwSource = windll.ntdll._handle
    else:
        dwFlags = 0x1000
        dwSource = NULL

    dwMessageId = err
    dwLanguageId = 0
    dwSize = 512
    lpBuffer = create_unicode_buffer(dwSize)
    vaList = NULL
    ret = kernel32.FormatMessageW(dwFlags,
                                  dwSource,
                                  dwMessageId,
                                  dwLanguageId,
                                  addressof(lpBuffer),
                                  dwSize,
                                  vaList)
    if not ret:
        return None

    return lpBuffer.value

def getServicesList():
    '''
    Get a list of (pid, servicename, displayname) tuples for the
    currently running services.
    '''

    ret = []
    scmh = advapi32.OpenSCManagerA(NULL, NULL, SC_MANAGER_ENUMERATE_SERVICE)

    try:
        dwSvcSize  = DWORD(0)
        dwSvcCount = DWORD(0)

        advapi32.EnumServicesStatusExW( scmh,
                                        SC_ENUM_PROCESS_INFO,
                                        SERVICE_WIN32,
                                        SERVICE_ACTIVE,
                                        NULL,
                                        0,
                                        addressof(dwSvcSize),
                                        addressof(dwSvcCount),
                                        NULL,
                                        NULL)

        buf = create_string_buffer(dwSvcSize.value)

        advapi32.EnumServicesStatusExW( scmh,
                                        SC_ENUM_PROCESS_INFO,
                                        SERVICE_WIN32,
                                        SERVICE_ACTIVE,
                                        addressof(buf),
                                        dwSvcSize.value,
                                        addressof(dwSvcSize),
                                        addressof(dwSvcCount),
                                        NULL,
                                        NULL)

        #p = POINTER(ENUM_SERVICE_STATUS_PROCESS)(addressof(buf))
        p = cast(buf, POINTER(ENUM_SERVICE_STATUS_PROCESS))

        for i in range(dwSvcCount.value):
            pid = p[i].ServiceStatusProcess.dwProcessId
            name = p[i].lpServiceName
            descr = p[i].lpDisplayName
            ret.append((pid, name, descr))

    finally:
        advapi32.CloseServiceHandle(scmh)

    return ret

x = '''
BOOL WINAPI EnumServicesStatusEx(
  __in         SC_HANDLE hSCManager,
  __in         SC_ENUM_TYPE InfoLevel,
  __in         DWORD dwServiceType,
  __in         DWORD dwServiceState,
  __out_opt    LPBYTE lpServices,
  __in         DWORD cbBufSize,
  __out        LPDWORD pcbBytesNeeded,
  __out        LPDWORD lpServicesReturned,
  __inout_opt  LPDWORD lpResumeHandle,
  __in_opt     LPCTSTR pszGroupName
);
'''

SE_PRIVILEGE_ENABLED    = 0x00000002
TOKEN_ADJUST_PRIVILEGES = 0x00000020
TOKEN_QUERY             = 0x00000008
dbgprivdone = False

# TOKEN_INFORMATION_CLASS
TokenUser                   = 1
TokenGroups                 = 2
TokenPrivileges             = 3
TokenOwner                  = 4
TokenPrimaryGroup           = 5
TokenDefaultDacl            = 6
TokenSource                 = 7
TokenType                   = 8
TokenImpersonationLevel     = 9
TokenStatistics             = 10
TokenRestrictedSids         = 11
TokenSessionId              = 12
TokenGroupsAndPrivileges    = 13
TokenSessionReference       = 14
TokenSandBoxInert           = 15
TokenAuditPolicy            = 16
TokenOrigin                 = 17
TokenElevationType          = 18
TokenLinkedToken            = 19
TokenElevation              = 20
TokenHasRestrictions        = 21
TokenAccessInformation      = 22
TokenVirtualizationAllowed  = 23
TokenVirtualizationEnabled  = 24
TokenIntegrityLevel         = 25
TokenUIAccess               = 26
TokenMandatoryPolicy        = 27
TokenLogonSid               = 28
MaxTokenInfoClass           = 29

# TOKEN_ELEVATION_TYPE
TokenElevationTypeDefault   = 1
TokenElevationTypeFull      = 2
TokenElevationTypeLimited   = 3

def getTokenElevationType(handle=-1):

    token = HANDLE(0)
    etype = DWORD(0)
    outsize = DWORD(0)
    if not advapi32.OpenProcessToken(handle, TOKEN_QUERY, addressof(token)):
        raise Exception('Invalid Process Handle: %d' % handle)

    advapi32.GetTokenInformation(token, TokenElevationType, addressof(etype), 4, addressof(outsize))

    return etype.value

def getDebugPrivileges():
    tokprivs = TOKEN_PRIVILEGES()
    dbgluid = LUID()
    token = HANDLE(0)

    if not advapi32.LookupPrivilegeValueA(0, b"seDebugPrivilege", addressof(dbgluid)):
        logger.warning("LookupPrivilegeValue Failed: %d", kernel32.GetLastError())
        return False

    if not advapi32.OpenProcessToken(-1, TOKEN_ADJUST_PRIVILEGES, addressof(token)):
        logger.warning("kernel32.OpenProcessToken Failed: %d", kernel32.GetLastError())
        return False

    tokprivs.PrivilegeCount = 1
    tokprivs.Privilege = dbgluid
    tokprivs.PrivilegeAttribute = SE_PRIVILEGE_ENABLED

    if not advapi32.AdjustTokenPrivileges(token, 0, addressof(tokprivs), 0, 0, 0):
        kernel32.CloseHandle(token)
        logger.warning("AdjustTokenPrivileges Failed: %d", kernel32.GetLastError())
        return False

    kernel32.CloseHandle(token)

def buildSystemHandleInformation(count):
    """
    Dynamically build the structure definition for the
    handle info list.
    """
    class SYSTEM_HANDLE_INFORMATION(Structure):
        _fields_ = [ ('Count', c_ulong), ('Handles', SYSTEM_HANDLE * count), ]
    return SYSTEM_HANDLE_INFORMATION()

def buildFindChildrenParams(count):
    class TI_FINDCHILDREN_PARAMS(Structure):
        _fields_ = [ ('Count', c_ulong), ('Start', c_ulong), ("Children",c_ulong * count),]
    tif = TI_FINDCHILDREN_PARAMS()
    tif.Count = count
    return tif

def raiseWin32Error(name):
    mesg = "Win32 Error %s failed: %s" % (name, kernel32.GetLastError())
    logger.warning(mesg)
    raise vtrace.PlatformException("Win32 Error %s failed: %s" % (name,kernel32.GetLastError()))

def GetModuleFileNameEx(phandle, mhandle):

    buf = create_unicode_buffer(1024)
    psapi.GetModuleFileNameExW(phandle, mhandle, addressof(buf), 1024)
    return buf.value

av_einfo_perms = [e_const.MM_READ, e_const.MM_WRITE, None, None, None, None, None, None, e_const.MM_EXEC]

class WindowsMixin:

    """
    A mixin to handle all non-arch specific win32 stuff.
    """

    def __init__(self):

        self.casesens = False

        self.phandle = None
        self.thandles = {}
        self.win32threads = {}
        self.dosdevs = []
        self.flushcache = False
        self.faultaddr = None
        global dbgprivdone
        if not dbgprivdone:
            dbgprivdone = getDebugPrivileges()

        self._is_wow64 = False  # 64 bit trace uses this...
        self._step_suspends = set() # Threads we have suspended for single stepping

        # Skip the attach event and plow through to the first
        # injected breakpoint (cause libs are loaded by then)
        self.enableAutoContinue(vtrace.NOTIFY_ATTACH)

        self.setupDosDeviceMaps()

        # Setup our binary format meta
        self.setMeta('Format','pe')

        # Setup some win32_ver info in metadata
        rel,ver,csd,ptype = platform.win32_ver()
        self.setMeta("WindowsRelease",rel)
        self.setMeta("WindowsVersion", ver)
        self.setMeta("WindowsCsd", csd)
        self.setMeta("WindowsProcessorType", ptype)

        # Setup modes which only apply to windows systems
        self.initMode('BlockStep', False, 'Single step to branch entry points')

        # If possible, get a default set of struct definitions
        # for ntdll...
        nt = vs_windows.getCurrentDef('ntdll')
        if nt is not None:
            self.vsbuilder.addVStructNamespace('ntdll', nt)

        # Either way, add the fallback "win32" namespace
        self.vsbuilder.addVStructNamespace('win32', vs_win32)

        # We need thread proxying for a few calls...
        self.fireTracerThread()

    def platformGetFds(self):
        ret = []
        hinfo = self.getHandles()
        for x in range(hinfo.Count):
            if hinfo.Handles[x].ProcessID != self.pid:
                continue

            hand = hinfo.Handles[x].HandleNumber
            myhand = self.dupHandle(hand)
            typestr = self.getHandleInfo(myhand, ObjectTypeInformation)
            htype = object_type_map.get(typestr, vtrace.FD_UNKNOWN)

            # prevent hanging when accessing special named pipes
            if hinfo.Handles[x].GrantedAccess == 0x0012019f:
                namestr = 'unknown, special named pipe with access mask 0x0012019f'
                ret.append( (hand, htype, "%s: %s" % (typestr, namestr)) )
                return ret

            wait = False
            if typestr == "File":
                wait = True
            namestr = self.getHandleInfo(myhand, ObjectNameInformation, wait=wait)
            kernel32.CloseHandle(myhand)
            ret.append( (hand, htype, "%s: %s" % (typestr, namestr)) )
        return ret

    def _winJitEvent(self, handle):
        kernel32.SetEvent(handle)

    def dupHandle(self, handle):
        """
        Duplicate the handle (who's id is in the currently attached
        target process) and return our own copy.
        """
        hret = c_uint(0)
        kernel32.DuplicateHandle(self.phandle,
                                 handle,
                                 kernel32.GetCurrentProcess(),
                                 addressof(hret),
                                 0,
                                 False,
                                 2) # DUPLICATE_SAME_ACCESS
        return hret.value

    def getHandleInfo(self, handle, itype=ObjectTypeInformation, wait=False):
        returnLength = c_ulong(0)
        objInfo = create_string_buffer(100)

        retval = ntdll.NtQueryObject(handle,
                                     itype,
                                     objInfo,
                                     sizeof(objInfo),
                                     addressof(returnLength))

        if (retval == STATUS_INFO_LENGTH_MISMATCH or
            retval == STATUS_BUFFER_OVERFLOW):

            objInfo = create_string_buffer(returnLength.value)
            retval = ntdll.NtQueryObject(handle,
                                         itype,
                                         objInfo,
                                         sizeof(objInfo),
                                         addressof(returnLength))

        if retval != 0:
            return 'Error 0x%.8x' % (e_bits.unsigned(retval, self.psize))

        uString = cast(objInfo, PUNICODE_STRING).contents

        return uString.Buffer

    def getHandles(self):

        hinfo = buildSystemHandleInformation(1)
        hsize = c_ulong(sizeof(hinfo))

        ntdll.NtQuerySystemInformation(NT_LIST_HANDLES, addressof(hinfo), hsize, addressof(hsize))

        count = math.ceil((hsize.value-4) // sizeof(SYSTEM_HANDLE))
        hinfo = buildSystemHandleInformation(count)
        hsize = c_ulong(sizeof(hinfo))

        ntdll.NtQuerySystemInformation(NT_LIST_HANDLES, addressof(hinfo), hsize, 0)

        return hinfo

    def setupDosDeviceMaps(self):
        '''
        Deal with the fun of mapping device names to drives
        '''
        self.dosdevs = []
        # redux
        devicename = create_unicode_buffer(1024)
        buffer = create_unicode_buffer(1024)

        hndl = kernel32.FindFirstVolumeW(buffer, 1024)
        while True:
            if hndl == -1:
                break
            namevalu = buffer.value[4:].rstrip('\\')
            size = kernel32.QueryDosDeviceW(namevalu, devicename, 1024)

            drivenames = create_unicode_buffer(1024)
            valulen = DWORD()

            stat = kernel32.GetVolumePathNamesForVolumeNameW(buffer.value, drivenames, 1024, pointer(valulen))
            if drivenames.value:
                self.dosdevs.append((drivenames.value, devicename.value))

            nextvolu = kernel32.FindNextVolumeW(hndl, buffer, DWORD(1024))
            if not nextvolu:
                err = kernel32.GetLastError()
                if err == ERROR_NO_MORE_FILES:
                    # Clean break. No more volumes to find.
                    break
                else:
                    logger.warning('Invalid exit code for FindVolumes of %d', err)
                    break
        kernel32.FindVolumeClose(hndl)

    def platformKill(self):
        kernel32.TerminateProcess(self.phandle, 0)

    @v_base.threadwrap
    def platformExec(self, cmdline):
        sinfo = STARTUPINFO()
        pinfo = PROCESS_INFORMATION()
        if not kernel32.CreateProcessA(0, cmdline.encode('utf-8'), 0, 0, 0,
                DEBUG_ONLY_THIS_PROCESS, 0, 0, addressof(sinfo), addressof(pinfo)):
            raiseWin32Error("CreateProcess (platformExec)")

        # When launching an app, we're guaranteed to get a breakpoint
        # Unless we want to fail checkBreakpoints, we'll need to set ShouldBreak
        self.setMeta('ShouldBreak', True)

        kernel32.CloseHandle(pinfo.Process)
        kernel32.CloseHandle(pinfo.Thread)

        return pinfo.ProcessId

    def platformInjectSo(self, filename):
        tid = c_uint32()
        x = self.parseExpression('kernel32.LoadLibraryA')
        memaddr = self.allocateMemory(4096)
        self.writeMemory(memaddr, b'%s\x00' % filename)
        t =  kernel32.CreateRemoteThread(self.phandle, 0, 0, x, memaddr, 0, addressof(tid))
        self.joinThread(tid.value)
        kernel32.CloseHandle(t)
        kernel32.VirtualFreeEx(self.phandle, memaddr, 0, 0x8000) # MEM_RELEASE 0x8000  MEM_DECOMMIT 0x4000

    @v_base.threadwrap
    def platformAttach(self, pid):
        if not kernel32.DebugActiveProcess(pid):
            raiseWin32Error("DebugActiveProcess")

    @v_base.threadwrap
    def platformDetach(self):
        # Do the crazy "can't suppress exceptions from detach" dance.
        if ((not self.exited) and
            self.getCurrentBreakpoint() is not None):
            self._clearBreakpoints()
            self.platformSendBreak()
            self.platformContinue()
            self.platformWait()

        try:
            if not kernel32.DebugActiveProcessStop(self.pid):
                raiseWin32Error("DebugActiveProcessStop")
        finally:
            phandle = self.phandle
            self.phandle = None
            kernel32.CloseHandle(phandle)


    def platformProtectMemory(self, va, size, perms):
        pret = c_uint(0)
        pval = perm_rev_lookup.get(perms, PAGE_EXECUTE_READWRITE)
        ret = kernel32.VirtualProtectEx(self.phandle, va, size, pval, addressof(pret))
        if ret == 0:
            raiseWin32Error("kernel32.VirtualProtectEx")

    def platformAllocateMemory(self, size, perms=e_const.MM_RWX, suggestaddr=0):
        pval = perm_rev_lookup.get(perms, PAGE_EXECUTE_READWRITE)
        ret = kernel32.VirtualAllocEx(self.phandle,
                suggestaddr, size, MEM_COMMIT, pval)
        if ret == 0:
            raiseWin32Error("kernel32.VirtualAllocEx")
        return ret

    def platformReadMemory(self, address, size):
        btype = c_char * size
        buf = btype()
        ret = c_ulong(0)
        if not kernel32.ReadProcessMemory(self.phandle, address, addressof(buf), size, addressof(ret)):
            raiseWin32Error("kernel32.ReadProcessMemory %s" % hex(address))
        return buf.raw

    @v_base.threadwrap
    def platformContinue(self):

        # If there is anything in _step_suspends, un-suspend them
        for thrid in self._step_suspends:
            retn = kernel32.ResumeThread(thrid)

        self._step_suspends.clear()

        self._continueDebugEvent()

    def _continueDebugEvent(self):

        magic = DBG_CONTINUE

        if self.getCurrentSignal() is not None:
            magic = DBG_EXCEPTION_NOT_HANDLED

        if self.flushcache:
            self.flushcache = False
            kernel32.FlushInstructionCache(self.phandle, 0, 0)

        if not kernel32.ContinueDebugEvent(self.pid, self.getMeta("StoppedThreadId"), magic):
            raiseWin32Error("ContinueDebugEvent")

    @v_base.threadwrap
    def platformStepi(self):
        # We have some flag fields broken out as meta regs
        self.setRegisterByName("TF", 1)
        if self.getMode('BlockStep'):
            wrmsr(e_i386.MSR_DEBUGCTL, e_i386.MSR_DEBUGCTL_BTF)

        self._syncRegs()

        # For single step, suspend all the threads except the current
        for thrid in self.getThreads().keys():

            # If this thread is the "current thread" don't suspend it
            if thrid == self.getCurrentThread():
                # If it was suspended because of stepping another thread
                # resume it.
                if thrid in self._step_suspends:
                    kernel32.ResumeThread(thrid)
                continue

            # Check for "already suspended"
            if self.sus_threads.get( thrid ):
                continue

            # Check if we're returning in a step loop
            if thrid in self._step_suspends:
                continue

            # Call suspend thread directly for speed
            kernel32.SuspendThread(thrid)
            self._step_suspends.add( thrid )

        self._continueDebugEvent()

    def platformWriteMemory(self, address, buf):
        ret = c_ulong(0)
        if not kernel32.WriteProcessMemory(self.phandle, address, buf, len(buf), addressof(ret)):
            raiseWin32Error("kernel32.WriteProcessMemory")
        # If we wrote memory, flush the instruction cache...
        self.flushcache = True
        return ret.value

    def platformSendBreak(self):
        #FIXME make this support windows 2000
        if not kernel32.DebugBreakProcess(self.phandle):
            raiseWin32Error("kernel32.DebugBreakProcess")

    def platformPs(self):
        ret = []
        pcount = 1024
        pids = (c_int * pcount)()
        needed = c_int(0)
        hmodule = HANDLE()

        psapi.EnumProcesses(addressof(pids), 4*pcount, addressof(needed))
        if needed.value > pcount:
            # If the array was too small, lets up the size to needed + 128
            pcount = needed.value + 128
            pids = (c_int * pcount)()
            psapi.EnumProcesses(addressof(pids), 4*pcount, addressof(needed))

        for i in range(needed.value//4):
            fname = (c_wchar * 512)()
            phandle = kernel32.OpenProcess(PROCESS_ALL_ACCESS, 0, pids[i])
            if not phandle: # If we get 0, we failed to open it (perms)
                continue
            psapi.EnumProcessModules(phandle, addressof(hmodule), 4, addressof(needed))
            psapi.GetModuleBaseNameW(phandle, hmodule, fname, 512)
            ret.append( (pids[i], fname.value))
            kernel32.CloseHandle(phandle)
            kernel32.CloseHandle(hmodule)
        return ret

    @v_base.threadwrap
    def platformWait(self):
        event = DEBUG_EVENT()
        if not kernel32.WaitForDebugEvent(addressof(event), INFINITE):
            raiseWin32Error("WaitForDebugEvent")
        return event

    def platformGetMemFault(self):
        return self.faultaddr,self.faultperm

    def platformProcessEvent(self, event):

        self.faultaddr = None
        self.faultperm = None

        if event.ProcessId != self.pid:
            raise Exception("event.ProcessId != self.pid (%d != %d)" %
                             (event.ProcessId,self.pid))

        ThreadId = event.ThreadId
        eventdict = {} # Each handler fills this in
        self.setMeta("Win32Event", eventdict)
        self.setMeta("StoppedThreadId", ThreadId)
        self.setMeta("ThreadId", ThreadId)

        if event.DebugEventCode == CREATE_PROCESS_DEBUG_EVENT:
            self.phandle = event.u.CreateProcessInfo.Process
            baseaddr = event.u.CreateProcessInfo.BaseOfImage
            ImageName = GetModuleFileNameEx(self.phandle, 0)
            if not ImageName:
                # If it fails, fall back on getMappedFileName
                ImageName = self.getMappedFileName(baseaddr)
            self.setMeta("ExeName", ImageName)

            teb = event.u.CreateProcessInfo.ThreadLocalBase
            self.win32threads[ThreadId] = teb
            self.thandles[ThreadId] = event.u.CreateProcessInfo.Thread

            tobj = self.getStruct("ntdll.TEB", teb)
            if tobj is not None:
                peb = tobj.ProcessEnvironmentBlock
                self.setMeta("PEB", peb)
                self.setVariable("peb", peb)

            eventdict["ImageName"] = ImageName
            eventdict["StartAddress"] = event.u.CreateProcessInfo.StartAddress
            eventdict["ThreadLocalBase"] = teb

            self._is_wow64 = False
            if IsWow64Process is not None:
                b = BOOL()
                IsWow64Process(self.phandle, addressof(b))
                if b.value:
                    self._is_wow64 = True

            self.setMeta('IsWow64', self._is_wow64)

            self.fireNotifiers(vtrace.NOTIFY_ATTACH)
            self.addLibraryBase(ImageName, baseaddr)

        elif event.DebugEventCode == CREATE_THREAD_DEBUG_EVENT:
            self.thandles[ThreadId] = event.u.CreateThread.Thread
            teb = event.u.CreateThread.ThreadLocalBase
            startaddr = event.u.CreateThread.StartAddress
            # Setup the event dictionary for notifiers
            eventdict["ThreadLocalBase"] = teb
            eventdict["StartAddress"] = startaddr
            self.win32threads[ThreadId] = teb
            self.fireNotifiers(vtrace.NOTIFY_CREATE_THREAD)

        elif event.DebugEventCode == EXCEPTION_DEBUG_EVENT:
            excode = event.u.Exception.ExceptionRecord.ExceptionCode
            exflags = event.u.Exception.ExceptionRecord.ExceptionFlags
            exaddr = event.u.Exception.ExceptionRecord.ExceptionAddress
            exparam = event.u.Exception.ExceptionRecord.NumberParameters
            firstChance = event.u.Exception.FirstChance

            plist = []
            for i in range(exparam):
                plist.append(int(event.u.Exception.ExceptionRecord.ExceptionInformation[i]))

            eventdict["ExceptionCode"] = excode
            eventdict["ExceptionFlags"] = exflags
            eventdict["ExceptionAddress"] = exaddr
            eventdict["NumberParameters"] = exparam
            eventdict["FirstChance"] = bool(firstChance)
            eventdict["ExceptionInformation"] = plist

            if firstChance:

                if excode in (EXCEPTION_BREAKPOINT, STATUS_WX86_BREAKPOINT):

                    if not self.checkBreakpoints():
                        # On first attach, all the library load
                        # events occur, then we hit a CC.  So,
                        # if we don't find a breakpoint, notify
                        # break anyay....
                        self.fireNotifiers(vtrace.NOTIFY_BREAK)

                elif excode in (EXCEPTION_SINGLE_STEP, STATUS_WX86_SINGLE_STEP):

                    if not self.checkWatchpoints():
                        self._fireStep()

                else:
                    if excode == 0xc0000005:
                        self.faultaddr = plist[1]
                        self.faultperm = av_einfo_perms[plist[0]]

                    # First we check for PageWatchpoint faults
                    if not self.checkPageWatchpoints():
                        self._fireSignal(excode, siginfo=plist)

            else:
                self._fireSignal(excode, siginfo=plist)

        elif event.DebugEventCode == EXIT_PROCESS_DEBUG_EVENT:
            ecode = event.u.ExitProcess.ExitCode
            eventdict["ExitCode"] = ecode
            self._fireExit(ecode)
            self.platformDetach()

        elif event.DebugEventCode == EXIT_THREAD_DEBUG_EVENT:
            self.win32threads.pop(ThreadId, None)
            ecode = event.u.ExitThread.ExitCode
            eventdict["ExitCode"] = ecode
            self._fireExitThread(ThreadId, ecode)

        elif event.DebugEventCode == LOAD_DLL_DEBUG_EVENT:
            baseaddr = event.u.LoadDll.BaseOfDll
            ImageName = GetModuleFileNameEx(self.phandle, event.u.LoadDll.File)
            if not ImageName:
                # If it fails, fall back on getMappedFileName
                ImageName = self.getMappedFileName(baseaddr)
            self.addLibraryBase(ImageName, baseaddr)
            kernel32.CloseHandle(event.u.LoadDll.File)

        elif event.DebugEventCode == UNLOAD_DLL_DEBUG_EVENT:
            baseaddr = event.u.UnloadDll.BaseOfDll
            eventdict["BaseOfDll"] = baseaddr
            self.delLibraryBase(baseaddr)

        elif event.DebugEventCode == OUTPUT_DEBUG_STRING_EVENT:
            # Gotta have a way to continue these...
            d = event.u.DebugString
            sdata = d.DebugStringData
            ssize = d.DebugStringLength

            # FIXME possibly make a gofast option that
            # doesn't get the string
            mem = self.readMemory(sdata, ssize)
            if d.Unicode:
                mem = mem.decode("utf-16-le")
            eventdict["DebugString"] = mem
            self.fireNotifiers(vtrace.NOTIFY_DEBUG_PRINT)

        else:
            logger.warning("Currently unhandled event %d", event.DebugEventCode)

        # NOTE: Not everbody falls through to here


    def getMappedFileName(self, address):
        self.requireAttached()
        fname = (c_wchar * 512)()
        x = psapi.GetMappedFileNameW(self.phandle, address, addressof(fname), 512)
        if not x:
            return ""
        name = fname.value
        for dosname, devname in self.dosdevs:
            if name.startswith(devname):
                return name.replace(devname, dosname)
        return name

    def platformGetMaps(self):
        stack = []
        ret = []
        base = 0

        for thrid, tebaddr in self.win32threads.items():
            teb = self.getStruct("ntdll.TEB", tebaddr)
            stack.append((teb.NtTib.StackBase, teb.NtTib.StackLimit))

        pebva = self.getMeta("PEB")

        mbi = MEMORY_BASIC_INFORMATION()
        while kernel32.VirtualQueryEx(self.phandle, base, addressof(mbi), sizeof(mbi)) > 0:
            if mbi.State == MEM_COMMIT:
                prot = mbi.Protect & 0xff
                perm = perm_lookup.get(prot, 0)
                base = mbi.BaseAddress
                mname = self.getMappedFileName(base)
                if not mname:
                    if pebva == base:
                        mname = '[PEB]'
                    else:
                        # see if we're in stack town
                        for stackbase, limit in stack:
                            print(f"Comparing {hex(base)} to {hex(stackbase)}-{hex(limit)}")
                            if stackbase >= base >= limit:
                                mname = '[Stack]'
                ret.append( (base, mbi.RegionSize, perm, mname) )

            base += mbi.RegionSize

        return ret

    def platformGetThreads(self):
        return self.win32threads

    def platformSuspendThread(self, thrid):
        thandle = self.thandles.get(thrid)
        if thandle is None:
            raise Exception('Suspending Unknown Thread: %d' % (thrid,))

        if kernel32.SuspendThread(thandle) == 0xffffffff:
            raiseWin32Error()

    def platformResumeThread(self, thrid):
        thandle = self.thandles.get(thrid)
        if thandle is None:
            raise Exception('Resuming Unknown Thread: %d' % (thrid,))

        if kernel32.ResumeThread(thandle) == 0xffffffff:
            raiseWin32Error()

    def platformParseBinary(self, filename, baseaddr, normname):
        pe = PE.peFromMemoryObject(self, baseaddr)
        ep = pe.IMAGE_NT_HEADERS.OptionalHeader.AddressOfEntryPoint
        self.addSymbol(e_resolv.Symbol('__entry', baseaddr+ep, 0, normname))
        symhash = e_symcache.symCacheHashFromPe(pe)

        if self.symcache:
            symcache = self.symcache.getCacheSyms(symhash)
            if symcache is not None:
                self.impSymCache(symcache, symfname=normname, baseaddr=baseaddr)
                return

        symcache = None
        # Check if we can use the real lib to parse...
        if dbghelp is not None and os.path.isfile(filename):
            symcache = self.parseWithDbgHelp(filename, baseaddr, normname)

        # If it's *still* none, fall back on PE
        if symcache is None:
            symcache = [ (rva, 0, name, 0) for (rva, ord, name) in pe.getExports() ]

        self.impSymCache( symcache, symfname=normname, baseaddr=baseaddr)

        if self.symcache:
            self.symcache.setCacheSyms(symhash, symcache)

    def parseWithDbgHelp(self, filename, baseaddr, normname):
        funcflags = (SYMFLAG_FUNCTION | SYMFLAG_EXPORT)

        sympath = self.getMeta('NtSymbolPath')
        parser = Win32SymbolParser(self.phandle, filename, baseaddr, sympath=sympath)
        parser.parse()
        parser.loadStructsIntoTrace(self, normname)
        return parser.getCacheSyms()

    @v_base.threadwrap
    def platformGetRegCtx(self, threadid):
        ctx = self.archGetRegCtx()
        c = self._winGetRegStruct()

        thandle = self.thandles.get(threadid, None)
        if not thandle:
            raise Exception("Getting registers for unknown thread")

        if not kernel32.GetThreadContext(thandle, addressof(c)):
            raiseWin32Error("kernel32.GetThreadContext")

        c.regPostProcess()

        ctx._rctx_Import(c)
        return ctx

    @v_base.threadwrap
    def platformSetRegCtx(self, threadid, ctx):

        c = self._winGetRegStruct()

        thandle = self.thandles.get(threadid, None)
        if not thandle:
            raise Exception("Getting registers for unknown thread: %d" % threadid)

        if not kernel32.GetThreadContext(thandle, addressof(c)):
            raiseWin32Error("kernel32.GetThreadContext (tid: %d)" % threadid)

        ctx._rctx_Export(c)

        if not kernel32.SetThreadContext(thandle, addressof(c)):
            raiseWin32Error("kernel32.SetThreadContext (tid: %d)" % threadid)

    def _getSvcList(self):
        '''
        Expose the getServicesList via the trace for remote...
        '''
        return getServicesList()

    def _getFormatMessage(self, err, isNtStatusCode):
        '''
        Expose the getFormatMessage via the trace for remote...
        '''
        return getFormatMessage(err, isNtStatusCode)

    def _getUacStatus(self):
        return getTokenElevationType(self.phandle)

# NOTE: The order of the constructors vs inheritance is very important...

class Windowsi386Trace(vtrace.Trace,
                       WindowsMixin,
                       v_i386.i386Mixin,
                       v_base.TracerBase):

    def __init__(self):
        vtrace.Trace.__init__(self)
        v_base.TracerBase.__init__(self)
        v_i386.i386Mixin.__init__(self)
        WindowsMixin.__init__(self)

    def _winGetRegStruct(self):
        c = CONTEXTx86()
        c.ContextFlags = (CONTEXT_i386 |
                          CONTEXT_FULL |
                          CONTEXT_DEBUG_REGISTERS |
                          CONTEXT_EXTENDED_REGISTERS)
        return c

class WindowsAmd64Trace(vtrace.Trace,
                        WindowsMixin,
                        v_amd64.Amd64Mixin,
                        v_base.TracerBase):

    def __init__(self):
        vtrace.Trace.__init__(self)
        v_base.TracerBase.__init__(self)
        WindowsMixin.__init__(self)
        v_amd64.Amd64Mixin.__init__(self)

    def _winGetRegStruct(self):
        c = CONTEXTx64()
        c.ContextFlags = (CONTEXT_AMD64 | CONTEXT_FULL | CONTEXT_DEBUG_REGISTERS)
        return c

reserved = {
    'None': True,
    'True': True,
    'False': True,
}

VT_EMPTY    = 0
VT_NULL     = 1
VT_I2       = 2
VT_I4       = 3
VT_R4       = 4
VT_R8       = 5
VT_CY       = 6
VT_DATE     = 7
VT_BSTR     = 8
VT_DISPATCH = 9
VT_ERROR    = 10
VT_BOOL     = 11
VT_VARIANT  = 12
VT_UNKNOWN  = 13
VT_I1       = 16
VT_UI1      = 17
VT_UI2      = 18
VT_UI4      = 19
VT_INT      = 20
VT_UINT     = 21

class VARIANT_guts(Union):
    _fields_ = [
        ('ui1', c_uint8),
        ('ui2', c_uint16),
        ('ui4', c_uint32),
        ('i1', c_int8),
        ('i2', c_int16),
        ('i4', c_int32),
        ('pad', BYTE*32),
    ]

class VARIANT(Structure):
    _fields_ = [
        ('vt', WORD),
        ('res1', WORD),
        ('res2', WORD),
        ('res3', WORD),
        ('u', VARIANT_guts),
    ]

class Win32SymbolParser:

    def __init__(self, phandle, filename, loadbase, sympath=None):
        self.phandle = phandle
        self.filename = filename
        self.loadbase = loadbase
        self.sympath = sympath
        self.symbols = []
        self.symopts = (SYMOPT_UNDNAME | SYMOPT_NO_PROMPTS | SYMOPT_NO_CPP)
        self._sym_types = {}
        self._sym_enums = {}
        self._sym_locals = {}

    def printSymbolInfo(self, info):
        # Just a helper function for "reversing" how dbghelp works
        for n,t in info.__class__._fields_:
            print(n,repr(getattr(info, n)))

    def symGetTypeInfo(self, tindex, tinfo, tparam):
        x = dbghelp.SymGetTypeInfo(self.phandle, self.loadbase,
                                   tindex, tinfo, tparam)
        if x == 0:
            return False
        return True

    def symGetTypeName(self, typeid):
        n = c_wchar_p()
        self.symGetTypeInfo(typeid, TI_GET_SYMNAME, pointer(n))
        val = n.value
        # Strip leading / trailing _'s
        if val is not None:
            val = val.strip('_')
        if val == '<unnamed-tag>' or val == 'unnamed':
            val = '_unnamed_%d' % typeid
        return val

    def symGetUdtKind(self, typeid):
        offset = c_ulong(0)
        self.symGetTypeInfo(typeid, TI_GET_UDTKIND, pointer(offset))
        return offset.value

    def symGetTypeOffset(self, typeid):
        offset = c_ulong(0)
        self.symGetTypeInfo(typeid, TI_GET_OFFSET, pointer(offset))
        return offset.value

    def symGetTypeLength(self, typeid):
        size = c_ulonglong(0)
        self.symGetTypeInfo(typeid, TI_GET_LENGTH, pointer(size))
        return size.value

    def symGetArrayIndexType(self, typeid):
        offset = c_ulong(0)
        self.symGetTypeInfo(typeid, TI_GET_ARRAYINDEXTYPEID, pointer(offset))
        return offset.value

    def symGetTypeValue(self, typeid):
        #size = c_ulonglong(0)
        v = VARIANT()
        self.symGetTypeInfo(typeid, TI_GET_VALUE, pointer(v))

        vt = v.vt

        # Messy, but gotta do it...
        if vt == VT_I1: return v.u.i1
        if vt == VT_I2: return v.u.i2
        if vt == VT_I4: return v.u.i4
        if vt == VT_UI1: return v.u.ui1
        if vt == VT_UI2: return v.u.ui2
        if vt == VT_UI4: return v.u.ui4

        raise Exception('Unhandled Variant Type: %d' % v.vt)

    def symGetTypeBase(self, typeid):
        btype = c_ulong(typeid)
        # Resolve the deepest base type
        while self.symGetTypeTag(btype.value) == SymTagTypedef:
            self.symGetTypeInfo(btype.value, TI_GET_BASETYPE, pointer(btype))
        return btype.value

    def symGetTypeType(self, child):
        ktype = c_ulong(0)
        self.symGetTypeInfo(child, TI_GET_TYPE, pointer(ktype))
        return ktype.value

    def symGetTypeTag(self, typeid):
        btype = c_ulong(0)
        self.symGetTypeInfo(typeid, TI_GET_SYMTAG, pointer(btype))
        return btype.value

    def _fixKidName(self, kidname):

        if kidname and kidname[0].isdigit():
            kidname = '_%s' % kidname

        if reserved.get(kidname):
            kidname = '_%s' % kidname

        return kidname

    def _symTypeEnum(self, name, tidx):
        size = self.symGetTypeLength(tidx)
        kids = []
        for child in self._symGetChildren(tidx):
            kidname = self.symGetTypeName(child)
            kidval = self.symGetTypeValue(child)
            kidname = self._fixKidName(kidname)
            kids.append((kidname, kidval))

        self._sym_enums[name] = (name, size, kids)

    def _symTypeUserDefined(self, name, tidx):
        size = self.symGetTypeLength(tidx)
        kids = []
        for child in self._symGetChildren(tidx):
            kidname = self.symGetTypeName(child)
            kidoff = self.symGetTypeOffset(child)
            ktype = self.symGetTypeType(child)
            ksize = self.symGetTypeLength(ktype)
            ktag = self.symGetTypeTag(ktype)

            kidname = self._fixKidName(kidname)
            kflags = 0
            ktypename = None
            kcount = None

            if ktag == SymTagPointerType:
                kflags |= vs_builder.VSFF_POINTER
                ptype = self.symGetTypeType(ktype)
                ktypename = self.symGetTypeName(ptype)

            elif ktag == SymTagArrayType:
                atype = self.symGetTypeType(ktype)
                asize = self.symGetTypeLength(atype)
                if asize == 0:
                    continue # on 0 length array, skip it
                kcount = ksize // asize

                # Now, we setup our *child* to be the type
                ktypename = self.symGetTypeName(atype)
                ksize = asize

                if self.symGetTypeTag(atype) == SymTagPointerType:
                    kflags |= vs_builder.VSFF_POINTER

            elif ktag == SymTagEnum:
                #ktypename = self.symGetTypeName(ktype)
                pass

            elif ktag == SymTagUDT:
                ktypename = self.symGetTypeName(ktype)

            elif ktag == SymTagBaseType:
                pass

            elif ktag == SymTagFunctionType:
                # Function pointer types...
                pass

            elif ktag == SymTagNull:
                pass

            else:
                logger.warning('%s:%s Unknown Type Tag: %d', name, kidname, ktag)

            kids.append((kidname, kidoff, ksize, ktypename, kflags, kcount))

        self._sym_types[name] = (name, size, kids)

    def _symGetChildren(self, typeIndex):

        s = c_ulong(0)
        self.symGetTypeInfo(typeIndex, TI_GET_CHILDRENCOUNT, pointer(s))
        tif = buildFindChildrenParams(s.value)
        self.symGetTypeInfo(typeIndex, TI_FINDCHILDREN, pointer(tif))
        for i in range(s.value):
            child = tif.Children[i]
            yield child

    def typeEnumCallback(self, psym, size, ctx):
        sym = psym.contents

        myname = self.symGetTypeName(sym.TypeIndex)
        mytag = self.symGetTypeTag(sym.TypeIndex)

        if mytag == SymTagUDT:
            self._symTypeUserDefined(myname, sym.TypeIndex)
            return True

        if mytag == SymTagEnum:
            self._symTypeEnum(myname, sym.TypeIndex)
            return True

        return True

    def symEnumCallback(self, psym, size, ctx):
        sym = psym.contents

        if sym.Tag == SymTagFunction:
            sym.Flags |= SYMFLAG_FUNCTION
        
        name = sym.Name
        if name:
            name = name.decode('utf-8')
        self.symbols.append((name, int(sym.Address), int(sym.Size), sym.Flags))
        return True

    def symFromAddr(self, address):
        si = SYMBOL_INFO()
        si.SizeOfStruct = sizeof(si) - 2000
        si.MaxNameLen = 2000
        disp = QWORD()
        dbghelp.SymFromAddr(self.phandle, address, pointer(disp), pointer(si))
        return si

    def symInit(self):
        dbghelp.SymInitialize(self.phandle, self.sympath, False)
        dbghelp.SymSetOptions(self.symopts)

        x = dbghelp.SymLoadModule64(self.phandle,
                                    0,
                                    self.filename.encode('utf-8'),
                                    None,
                                    self.loadbase,
                                    os.path.getsize(self.filename))


        # This is for debugging which pdb got loaded
        #imghlp = IMAGEHLP_MODULE64()
        #imghlp.SizeOfStruct = sizeof(imghlp)
        #dbghelp.SymGetModuleInfo64(self.phandle, x, pointer(imghlp))
        #print "PDB",repr(imghlp.LoadedPdbName)

    def symCleanup(self):
        dbghelp.SymCleanup(self.phandle)

    def symLocalCallback(self, psym, size, ctx):
        sym = psym.contents
        address = c_int32(sym.Address).value
        self._cur_locs.append( (sym.Name, address, sym.Size, sym.Flags) )

        return True

    def parseArgs(self):

        for name, addr, size, flags in self.symbols:

            si = self.symFromAddr(addr)
            if si.Tag != SymTagFunction:
                continue

            self._cur_locs = []

            sframe = IMAGEHLP_STACK_FRAME()
            sframe.InstructionOffset = addr
            dbghelp.SymSetContext(self.phandle, pointer(sframe), 0)
            dbghelp.SymEnumSymbols(self.phandle,
                        0,
                        None,
                        SYMCALLBACK(self.symLocalCallback),
                        0)

            if len(self._cur_locs):
                self._sym_locals[addr] = self._cur_locs

    def parse(self):
        try:

            self.symInit()

            dbghelp.SymEnumSymbols(self.phandle,
                        self.loadbase,
                        None,
                        SYMCALLBACK(self.symEnumCallback),
                        NULL)

            self.parseTypes()
            #self.parseArgs()

            self.symCleanup()

        except Exception:
            logger.error(traceback.format_exc())
            raise

    def parseTypes(self):
        #self.symInit()
        # This is how you enumerate type information
        dbghelp.SymEnumTypes(self.phandle,
                    self.loadbase,
                    SYMCALLBACK(self.typeEnumCallback),
                    NULL)

        #self.symCleanup()

    def loadStructsIntoTrace(self, trace, normname):
        t = self._sym_types.values()
        e = self._sym_enums.values()

        # Only add the namespace if we have values...
        if len(t):
            builder = vs_builder.VStructBuilder(defs=t, enums=e)
            trace.vsbuilder.addVStructNamespace(normname, builder)

    def getCacheSyms(self):
        '''
        Get the parsed symbols as a list of envi SymbolCache tuples.
        '''
        ret = []
        funcflags = (SYMFLAG_FUNCTION | SYMFLAG_EXPORT)
        for name, addr, size, flags in self.symbols:
            stype = e_resolv.SYMSTOR_SYM_SYMBOL
            if flags & funcflags:
                stype = e_resolv.SYMSTOR_SYM_FUNCTION
            ret.append( (addr-self.loadbase, size, name, stype) )
        return ret

