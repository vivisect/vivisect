"""
Darwin Platform Module
"""
# Copyright (C) 2007 Invisigoth - See LICENSE file for details
import os
import ctypes
import signal
import logging
import ctypes.util as c_util

import envi.const as e_const

import vtrace
import vtrace.archs.i386 as v_i386
import vtrace.archs.amd64 as v_amd64
import vtrace.platforms.base as v_base
import vtrace.platforms.posix as v_posix


logger = logging.getLogger(__name__)
addrof = ctypes.pointer

# The OSX ptrace defines...
PT_TRACE_ME     = 0    # child declares it's being traced
PT_READ_I       = 1    # read word in child's I space
PT_READ_D       = 2    # read word in child's D space
PT_READ_U       = 3    # read word in child's user structure
PT_WRITE_I      = 4    # write word in child's I space
PT_WRITE_D      = 5    # write word in child's D space
PT_WRITE_U      = 6    # write word in child's user structure
PT_CONTINUE     = 7    # continue the child
PT_KILL         = 8    # kill the child process
PT_STEP         = 9    # single step the child
PT_ATTACH       = 10   # trace some running process
PT_DETACH       = 11   # stop tracing a process
PT_SIGEXC       = 12   # signals as exceptions for current_proc
PT_THUPDATE     = 13   # signal for thread#
PT_ATTACHEXC    = 14   # attach to running process with signal exception
PT_FORCEQUOTA   = 30   # Enforce quota for root
PT_DENY_ATTACH  = 31

# Top-level identifiers
CTL_UNSPEC  = 0        # unused
CTL_KERN    = 1        # "high kernel": proc, limits
CTL_VM      = 2        # virtual memory
CTL_VFS     = 3        # file system, mount type is next
CTL_NET     = 4        # network, see socket.h
CTL_DEBUG   = 5        # debugging parameters
CTL_HW      = 6        # generic cpu/io
CTL_MACHDEP = 7        # machine dependent
CTL_USER    = 8        # user-level
CTL_MAXID   = 9        # number of valid top-level ids

KERN_OSTYPE          = 1    # string: system version
KERN_OSRELEASE       = 2    # string: system release
KERN_OSREV           = 3    # int: system revision
KERN_VERSION         = 4    # string: compile time info
KERN_MAXVNODES       = 5    # int: max vnodes
KERN_MAXPROC         = 6    # int: max processes
KERN_MAXFILES        = 7    # int: max open files
KERN_ARGMAX          = 8    # int: max arguments to exec
KERN_SECURELVL       = 9    # int: system security level
KERN_HOSTNAME        = 10    # string: hostname
KERN_HOSTID          = 11    # int: host identifier
KERN_CLOCKRATE       = 12    # struct: struct clockrate
KERN_VNODE           = 13    # struct: vnode structures
KERN_PROC            = 14    # struct: process entries
KERN_FILE            = 15    # struct: file entries
KERN_PROF            = 16    # node: kernel profiling info
KERN_POSIX1          = 17    # int: POSIX.1 version
KERN_NGROUPS         = 18    # int: # of supplemental group ids
KERN_JOB_CONTROL     = 19    # int: is job control available
KERN_SAVED_IDS       = 20    # int: saved set-user/group-ID
KERN_BOOTTIME        = 21    # struct: time kernel was booted
KERN_NISDOMAINNAME   = 22    # string: YP domain name
KERN_DOMAINNAME      = KERN_NISDOMAINNAME
KERN_MAXPARTITIONS   = 23    # int: number of partitions/disk
KERN_KDEBUG          = 24    # int: kernel trace points
KERN_UPDATEINTERVAL  = 25    # int: update process sleep time
KERN_OSRELDATE       = 26    # int: OS release date
KERN_NTP_PLL         = 27    # node: NTP PLL control
KERN_BOOTFILE        = 28    # string: name of booted kernel
KERN_MAXFILESPERPROC = 29    # int: max open files per proc
KERN_MAXPROCPERUID   = 30    # int: max processes per uid
KERN_DUMPDEV         = 31    # dev_t: device to dump on
KERN_IPC             = 32    # node: anything related to IPC
KERN_DUMMY           = 33    # unused
KERN_PS_STRINGS      = 34    # int: address of PS_STRINGS
KERN_USRSTACK32      = 35    # int: address of USRSTACK
KERN_LOGSIGEXIT      = 36    # int: do we log sigexit procs?
KERN_SYMFILE         = 37    # string: kernel symbol filename
KERN_PROCARGS        = 38
#/* 39 was KERN_PCSAMPLES... now deprecated
KERN_NETBOOT         = 40    # int: are we netbooted? 1=yes,0=no
KERN_PANICINFO       = 41    # node: panic UI information
KERN_SYSV            = 42    # node: System V IPC information
KERN_AFFINITY        = 43    # xxx
KERN_TRANSLATE       = 44    # xxx
KERN_CLASSIC         = KERN_TRANSLATE    # XXX backwards compat
KERN_EXEC            = 45    # xxx
KERN_CLASSICHANDLER  = KERN_EXEC # XXX backwards compatibility
KERN_AIOMAX          = 46    # int: max aio requests
KERN_AIOPROCMAX      = 47    # int: max aio requests per process
KERN_AIOTHREADS      = 48    # int: max aio worker threads
KERN_PROCARGS2       = 49
KERN_COREFILE        = 50    # string: corefile format string
KERN_COREDUMP        = 51    # int: whether to coredump at all
KERN_SUGID_COREDUMP  = 52    # int: whether to dump SUGID cores
KERN_PROCDELAYTERM   = 53    # int: set/reset current proc for delayed termination during shutdown
KERN_SHREG_PRIVATIZABLE = 54    # int: can shared regions be privatized ?
KERN_PROC_LOW_PRI_IO = 55    # int: set/reset current proc for low priority I/O
KERN_LOW_PRI_WINDOW  = 56    # int: set/reset throttle window - milliseconds
KERN_LOW_PRI_DELAY   = 57    # int: set/reset throttle delay - milliseconds
KERN_POSIX           = 58    # node: posix tunables
KERN_USRSTACK64      = 59    # LP64 user stack query
KERN_NX_PROTECTION   = 60    # int: whether no-execute protection is enabled
KERN_TFP             = 61    # Task for pid settings
KERN_PROCNAME        = 62    # setup process program  name(2*MAXCOMLEN)
KERN_THALTSTACK      = 63    # for compat with older x86 and does nothing
KERN_SPECULATIVE_READS  = 64    # int: whether speculative reads are disabled
KERN_OSVERSION       = 65    # for build number i.e. 9A127
KERN_SAFEBOOT        = 66    # are we booted safe?
KERN_LCTX            = 67    # node: login context
KERN_RAGEVNODE       = 68
KERN_TTY             = 69    # node: tty settings
KERN_CHECKOPENEVT    = 70      # spi: check the VOPENEVT flag on vnodes at open time
KERN_MAXID           = 71    # number of valid kern ids
# # KERN_RAGEVNODE types
KERN_RAGE_PROC       = 1
KERN_RAGE_THREAD     = 2
KERN_UNRAGE_PROC     = 3
KERN_UNRAGE_THREAD   = 4

# # KERN_OPENEVT types
KERN_OPENEVT_PROC    = 1
KERN_UNOPENEVT_PROC  = 2

# # KERN_TFP types
KERN_TFP_POLICY      = 1

# # KERN_TFP_POLICY values . All policies allow task port for self
KERN_TFP_POLICY_DENY    = 0     # Deny Mode: None allowed except privileged
KERN_TFP_POLICY_DEFAULT = 2    # Default  Mode: related ones allowed and upcall authentication

# # KERN_KDEBUG types
KERN_KDEFLAGS        = 1
KERN_KDDFLAGS        = 2
KERN_KDENABLE        = 3
KERN_KDSETBUF        = 4
KERN_KDGETBUF        = 5
KERN_KDSETUP         = 6
KERN_KDREMOVE        = 7
KERN_KDSETREG        = 8
KERN_KDGETREG        = 9
KERN_KDREADTR        = 10
KERN_KDPIDTR         = 11
KERN_KDTHRMAP        = 12
# # Don't use 13 as it is overloaded with KERN_VNODE
KERN_KDPIDEX         = 14
KERN_KDSETRTCDEC     = 15
KERN_KDGETENTROPY    = 16

# # KERN_PANICINFO types
KERN_PANICINFO_MAXSIZE  = 1    # quad: panic UI image size limit
KERN_PANICINFO_IMAGE    = 2    # panic UI in 8-bit kraw format

# * KERN_PROC subtypes
KERN_PROC_ALL        = 0    # everything
KERN_PROC_PID        = 1    # by process id
KERN_PROC_PGRP       = 2    # by process group id
KERN_PROC_SESSION    = 3    # by session of pid
KERN_PROC_TTY        = 4    # by controlling tty
KERN_PROC_UID        = 5    # by effective uid
KERN_PROC_RUID       = 6    # by real uid
KERN_PROC_LCID       = 7    # by login context id

# Stupid backwards perms defs...
VM_PROT_READ	= 1
VM_PROT_WRITE	= 2
VM_PROT_EXECUTE	= 4

# Thread status types...
x86_THREAD_STATE32    = 1
x86_FLOAT_STATE32     = 2
x86_EXCEPTION_STATE32 = 3
x86_THREAD_STATE64    = 4
x86_FLOAT_STATE64     = 5
x86_EXCEPTION_STATE64 = 6
x86_THREAD_STATE      = 7
x86_FLOAT_STATE       = 8
x86_EXCEPTION_STATE   = 9
x86_DEBUG_STATE32     = 10
x86_DEBUG_STATE64     = 11
x86_DEBUG_STATE       = 12
THREAD_STATE_NONE     = 13

class X86_STATE_HDR(ctypes.Structure):
    _fields_ = [
        ('flavor', ctypes.c_uint32),
        ('count',  ctypes.c_uint32),
    ]

class STRUCT_X86_THREAD_STATE32(ctypes.Structure):
    _fields_ = [
        #('tsh', X86_STATE_HDR),
        ('eax', ctypes.c_uint32),
        ('ebx', ctypes.c_uint32),
        ('ecx', ctypes.c_uint32),
        ('edx', ctypes.c_uint32),
        ('edi', ctypes.c_uint32),
        ('esi', ctypes.c_uint32),
        ('ebp', ctypes.c_uint32),
        ('esp', ctypes.c_uint32),
        ('ss',  ctypes.c_uint32),
        ('eflags', ctypes.c_uint32),
        ('eip', ctypes.c_uint32),
        ('cs',  ctypes.c_uint32),
        ('ds',  ctypes.c_uint32),
        ('es',  ctypes.c_uint32),
        ('fs',  ctypes.c_uint32),
        ('gs',  ctypes.c_uint32),
    ]

class STRUCT_X86_EXCEPTION_STATE32(ctypes.Structure):
    _fields_ = [
        ('trapno',     ctypes.c_uint32),
        ('err',        ctypes.c_uint32),
        ('faultvaddr', ctypes.c_uint32),
    ]

class STRUCT_X86_DEBUG_STATE32(ctypes.Structure):
    _fields_ = [ ('debug%d', ctypes.c_uint32) for i in range(8) ]

class STRUCT_X86_THREAD_STATE64(ctypes.Structure):
    _fields_ = [
        #('tsh', X86_STATE_HDR),
        ('rax', ctypes.c_uint64),
        ('rbx', ctypes.c_uint64),
        ('rcx', ctypes.c_uint64),
        ('rdx', ctypes.c_uint64),
        ('rdi', ctypes.c_uint64),
        ('rsi', ctypes.c_uint64),
        ('rbp', ctypes.c_uint64),
        ('rsp', ctypes.c_uint64),
        ('r8',  ctypes.c_uint64),
        ('r9',  ctypes.c_uint64),
        ('r10', ctypes.c_uint64),
        ('r11', ctypes.c_uint64),
        ('r12', ctypes.c_uint64),
        ('r13', ctypes.c_uint64),
        ('r14', ctypes.c_uint64),
        ('r15', ctypes.c_uint64),
        ('rip', ctypes.c_uint64),
        ('rflags', ctypes.c_uint64),
        ('cs',  ctypes.c_uint64),
        ('fs',  ctypes.c_uint64),
        ('gs',  ctypes.c_uint64),
    ]


class STRUCT_X86_EXCEPTION_STATE64(ctypes.Structure):
    _fields_ = [
        ('trapno',     ctypes.c_uint32),
        ('err',        ctypes.c_uint32),
        ('faultvaddr', ctypes.c_uint64),
    ]

class STRUCT_X86_DEBUG_STATE64(ctypes.Structure):
    _fields_ = [ ('debug%d', ctypes.c_uint64) for i in range(8) ]

###########################################################################
#
# mach port enumerations
#
MACH_PORT_NULL              = 0

#MACH_PORT_RIGHT_* definitions are used as arguments
MACH_PORT_RIGHT_SEND        = 0
MACH_PORT_RIGHT_RECEIVE     = 1
MACH_PORT_RIGHT_SEND_ONCE   = 2
MACH_PORT_RIGHT_PORT_SET    = 3
MACH_PORT_RIGHT_DEAD_NAME   = 4
MACH_PORT_RIGHT_LABELH      = 5
MACH_PORT_RIGHT_NUMBER      = 6

def MACH_PORT_TYPE(right):
    return 1 << (right + 16)

MACH_PORT_TYPE_SEND         = MACH_PORT_TYPE(MACH_PORT_RIGHT_SEND)
MACH_PORT_TYPE_RECEIVE      = MACH_PORT_TYPE(MACH_PORT_RIGHT_RECEIVE)
MACH_PORT_TYPE_SEND_ONCE    = MACH_PORT_TYPE(MACH_PORT_RIGHT_SEND_ONCE)
MACH_PORT_TYPE_PORT_SET     = MACH_PORT_TYPE(MACH_PORT_RIGHT_PORT_SET)
MACH_PORT_TYPE_DEAD_NAME    = MACH_PORT_TYPE(MACH_PORT_RIGHT_DEAD_NAME)
MACH_PORT_TYPE_LABELH       = MACH_PORT_TYPE(MACH_PORT_RIGHT_LABELH)

###########################################################################
#
# mach message types and structures
#
MACH_MSG_TIMEOUT_NONE = 0
MACH_MSG_OPTION_NONE  = 0

MACH_SEND_MSG       = 0x00000001
MACH_RCV_MSG        = 0x00000002
MACH_RCV_LARGE      = 0x00000004

MACH_SEND_TIMEOUT   = 0x00000010
MACH_SEND_INTERRUPT = 0x00000040  # libmach implements
MACH_SEND_CANCEL    = 0x00000080
MACH_SEND_ALWAYS    = 0x00010000  # internal use only
MACH_SEND_TRAILER   = 0x00020000  

MACH_RCV_TIMEOUT    = 0x00000100
MACH_RCV_NOTIFY     = 0x00000200
MACH_RCV_INTERRUPT  = 0x00000400  # libmach implements
MACH_RCV_OVERWRITE  = 0x00001000

# Return codes from mach_msg...
MACH_RCV_TIMED_OUT  = 0x10004003

MACH_MSG_TYPE_MOVE_RECEIVE   = 16    # Must hold receive rights
MACH_MSG_TYPE_MOVE_SEND      = 17    # Must hold send rights
MACH_MSG_TYPE_MOVE_SEND_ONCE = 18    # Must hold sendonce rights
MACH_MSG_TYPE_COPY_SEND      = 19    # Must hold send rights
MACH_MSG_TYPE_MAKE_SEND      = 20    # Must hold receive rights
MACH_MSG_TYPE_MAKE_SEND_ONCE = 21    # Must hold receive rights
MACH_MSG_TYPE_COPY_RECEIVE   = 22    # Must hold receive rights

size_t            = ctypes.c_ulong

mach_port_t       = ctypes.c_uint32
mach_port_name_t  = ctypes.c_uint32
mach_port_right_t = ctypes.c_uint32
mach_msg_size_t   = ctypes.c_uint32
mach_msg_bits_t   = ctypes.c_uint32
mach_msg_id_t     = ctypes.c_uint32

ipc_space_t       = ctypes.c_uint32

kern_return_t     = ctypes.c_uint32

class mach_msg_header_t(ctypes.Structure):
    _fields_ = [
      ('msgh_bits',        mach_msg_bits_t),
      ('msgh_size',        mach_msg_size_t),
      ('msgh_remote_port', mach_port_t),
      ('msgh_local_port',  mach_port_t),
      ('msgh_reserved',    mach_msg_size_t),
      ('msgh_id',          mach_msg_id_t),
    ]

class mach_msg_body_t(ctypes.Structure):
    _fields_ = [
        ('msgh_descriptor_count', ctypes.c_uint32),
    ]

class mach_msg_port_descriptor_t(ctypes.Structure):
    _fields_ = [
        ('name',        mach_port_t),
        ('pad1',        mach_msg_size_t),
        ('pad2',        ctypes.c_uint32),
    ]

class NDR_record_t(ctypes.Structure):
    _fields_ = [
        ('mig_vers',     ctypes.c_uint8),
        ('if_vers',      ctypes.c_uint8),
        ('reserved',     ctypes.c_uint8),
        ('mig_encoding', ctypes.c_uint8),
        ('int_rep',      ctypes.c_uint8),
        ('char_rep',     ctypes.c_uint8),
        ('float_rep',    ctypes.c_uint8),
        ('reserved2',    ctypes.c_uint8),
    ]

exception_type_t        = ctypes.c_uint32
mach_msg_type_number_t  = ctypes.c_uint32
exception_data_t        = ctypes.POINTER(ctypes.c_uint32)

# the message type we receive from the kernel for exceptions
class exc_msg(ctypes.Structure):
    _fields_ = [
        ('Head',    mach_msg_header_t),
        #('data',    ctypes.c_uint8 * 1024),

        ('body',    mach_msg_body_t),
        ('thread',  mach_msg_port_descriptor_t),
        ('task',    mach_msg_port_descriptor_t),
        ('NDR',     NDR_record_t),
        ('exception', exception_type_t),
        ('codeCnt',   mach_msg_type_number_t),
        ('codes',     ctypes.c_uint32 * 128),


        ##('codes',     exception_data_t),
        ##('pad',       ctypes.c_uint8 * 512)

    ]

# The response message we send back
class exc_rep_msg(ctypes.Structure):
    _fields_ = [
        ('Head',    mach_msg_header_t),
        ('data',    ctypes.c_uint8 * 1024),
        #('NDR',     NDR_record_t),
        #('RetCode', ctypes.c_uint32)
    ]

##########################################################################
# mach generic exception codes
#
EXC_BAD_ACCESS            = 1
EXC_BAD_INSTRUCTION       = 2
EXC_ARITHMETIC            = 3
EXC_EMULATION             = 4
EXC_SOFTWARE              = 5
EXC_BREAKPOINT            = 6
EXC_SYSCALL               = 7
EXC_MACH_SYSCALL          = 8
EXC_RPC_ALERT             = 9
EXC_CRASH                 = 10

# EXC_SOFTWARE will have code[0] == EXC_SOFT_SIGNAL for posix sigs
EXC_SOFT_BREAK            = 0x00001 # LLDB: (exc_type == EXC_BREAKPOINT || ((exc_type == EXC_SOFTWARE) && exc_data[0] == 1))
EXC_SOFT_SIGNAL           = 0x10003 # Unix signal exceptions

EXC_MASK_MACHINE            = 0
EXC_MASK_BAD_ACCESS         = 1 << EXC_BAD_ACCESS
EXC_MASK_BAD_INSTRUCTION    = 1 << EXC_BAD_INSTRUCTION
EXC_MASK_ARITHMETIC         = 1 << EXC_ARITHMETIC
EXC_MASK_EMULATION          = 1 << EXC_EMULATION
EXC_MASK_SOFTWARE           = 1 << EXC_SOFTWARE
EXC_MASK_BREAKPOINT         = 1 << EXC_BREAKPOINT
EXC_MASK_SYSCALL            = 1 << EXC_SYSCALL
EXC_MASK_MACH_SYSCALL       = 1 << EXC_MACH_SYSCALL
EXC_MASK_RPC_ALERT          = 1 << EXC_RPC_ALERT
EXC_MASK_CRASH              = 1 << EXC_CRASH

EXC_MASK_ALL = (EXC_MASK_BAD_ACCESS |
                EXC_MASK_BAD_INSTRUCTION |
                EXC_MASK_ARITHMETIC |
                EXC_MASK_EMULATION |
                EXC_MASK_SOFTWARE |
                EXC_MASK_BREAKPOINT |
                EXC_MASK_SYSCALL |
                EXC_MASK_MACH_SYSCALL |
                EXC_MASK_RPC_ALERT |
                EXC_MASK_CRASH |
                EXC_MASK_MACHINE)

EXCEPTION_DEFAULT        = 1 # Send a catch_exception_raise message including the identity.
EXCEPTION_STATE          = 2 # Send a catch_exception_raise_state message including the thread state.
EXCEPTION_STATE_IDENTITY = 3 # Send a catch_exception_raise_state_identity message including the thread identity and state.
MACH_EXCEPTION_CODES     = 0x80000000 # Send 64-bit code and subcode in the exception header

boolean_t = ctypes.c_uint32
pid_t     = ctypes.c_uint32
#u_int     = ctypes.c_uint32
#pvoid     = ctypes.c_void_p
#fixpt_t   = ctypes.c_uint32
#u_quad_t  = ctypes.c_ulonglong
#sigset_t  = ctypes.c_uint32
thread_t  = ctypes.c_uint32


####################################################################
#
# mach VM related stuff....
#
vm_prot_t    = ctypes.c_uint32
vm_inherit_t = ctypes.c_uint32
vm_behavior_t = ctypes.c_uint32
memory_object_offset_t = ctypes.c_ulonglong

VM_REGION_BASIC_INFO_64    = 9

class vm_region_basic_info_64(ctypes.Structure):
    _fields_ = [
        ('protection',      vm_prot_t),
        ('max_protection',  vm_prot_t),
        ('inheritance',     vm_inherit_t),
        ('shared',          boolean_t),
        ('reserved',        boolean_t),
        ('offset',          memory_object_offset_t),
        ('behavior',        vm_behavior_t),
        ('user_wired_count',ctypes.c_ushort),
    ]

VM_REGION_BASIC_INFO_COUNT_64 = ctypes.sizeof(vm_region_basic_info_64) / 4

#mach_helper = ctypes.CDLL('./darwin_mach.dylib')

#
# These are used by the machhelper library code
#
class DarwinDebugCtx(ctypes.Structure):
    _fields_ = [
        ('dbgtask', mach_port_t),
        ('task',    mach_port_t),
        ('portset', mach_port_name_t),
        ('excport', mach_port_name_t),
        ('msgin',   ctypes.c_void_p),
        ('msgout',  ctypes.c_void_p),
    ]

class ProcessListEntry(ctypes.Structure):
    _fields_ = [
        ('pid', ctypes.c_uint),
        ('name', ctypes.c_char * 17),
    ]

darwindir = os.path.dirname(__file__)

####################################################################
    
class DarwinMixin(v_posix.PosixMixin, v_posix.PtraceMixin):

    def __init__(self):
        v_posix.PosixMixin.__init__(self)
        v_posix.PtraceMixin.__init__(self)

        self.libc = ctypes.CDLL(c_util.find_library('c'))
        self.myport = self.libc.mach_task_self()

        self.libc.mach_port_allocate.argtypes = [ipc_space_t, mach_port_right_t, ctypes.POINTER(mach_port_name_t)]
        self.libc.mach_port_allocate.restype = kern_return_t

        self.libc.mach_vm_read.argtypes = [ mach_port_t, size_t, size_t, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_uint32)]
        self.libc.mach_vm_read.restype = kern_return_t

        self.libc.ptrace.restype = ctypes.c_int
        self.libc.ptrace.argtypes = [ctypes.c_int, ctypes.c_uint32, ctypes.c_size_t, ctypes.c_int]

        machhelp_path = os.path.join(darwindir, 'machhelper.dylib')
        self.machhelper = ctypes.CDLL(machhelp_path)
        self.machhelper.platformPs.restype = ctypes.POINTER(ProcessListEntry)

        self.useptrace = False

        self.portset = self.newMachPort(MACH_PORT_RIGHT_PORT_SET)
        self.excport = self.newMachRWPort()
        self.addPortToSet(self.excport)

    def platformPs(self):

        ret = []
        y = self.machhelper.platformPs()
        i = 0
        while y[i].pid != 0xffffffff:
            ret.append((y[i].pid, y[i].name))
            i += 1

        # FIXME free!
        ret.reverse()
        return ret

    def platformParseBinary(self, filename, baseaddr, normname):
        pass

    def platformGetFds(self):
        logger.warning('platformGetFds() needs implementing on darwin')
        return []

    def platformExec(self, cmdline):
        pid = v_posix.PtraceMixin.platformExec(self, cmdline)
        self.task = self.taskForPid(pid)
        self.setExceptionPort()
        return pid

    def _getThreadPorts(self):
        count = ctypes.c_uint32()
        tlist = ctypes.POINTER(thread_t)()
        assert( self.libc.task_threads(self.task, addrof(tlist), addrof(count)) == 0 )
        ret = [ tlist[i] for i in range(count.value)]
        self.libc.vm_deallocate(self.task, tlist)
        return ret

    def platformSuspendThread(self, tid):
        self.libc.thread_suspend(tid)

    def platformResumeThread(self, tid):
        self.libc.thread_resume(tid)

    def platformGetThreads(self):
        ret = {}
        for tid in self._getThreadPorts():
            ret[tid] = tid
        return ret

    def platformGetMaps(self):
        maps = []
        address = ctypes.c_ulong(0)
        mapsize = ctypes.c_ulong(0)
        name    = ctypes.c_uint32(0)
        count   = ctypes.c_uint32(VM_REGION_BASIC_INFO_COUNT_64)
        info    = vm_region_basic_info_64()

        while True:

            r = self.libc.mach_vm_region(self.task, addrof(address),
                                   addrof(mapsize), VM_REGION_BASIC_INFO_64,
                                   addrof(info), addrof(count),
                                   addrof(name))

            # If we get told "invalid address", we have crossed into kernel land...
            if r == 1:
                break

            if r != 0:
                self.libc.mach_error("mach_vm_region", r)
                raise Exception('vm_region Failed for 0x%.8x: 0x%.8x' % (address.value,r))

            perms = 0
            p = info.protection
            if p & VM_PROT_READ:
                perms |= e_const.MM_READ
            if p & VM_PROT_WRITE:
                perms |= e_const.MM_WRITE
            if p & VM_PROT_EXECUTE:
                perms |= e_const.MM_EXEC
            if info.shared:
                perms |= e_const.MM_SHARED
            # If we got any perms, report the map
            if perms:
                maps.append((address.value, mapsize.value, perms, ''))

            address.value += mapsize.value

        return maps

    def handlePosixSignal(self, sig):

        if sig == signal.SIGTRAP:
            # FIXME I think we can catch these!
            # Traps on posix systems are a little complicated
            if self.stepping:
                self.stepping = False
                self.fireNotifiers(vtrace.NOTIFY_STEP)

            # FIXME and these too...
            elif self.checkBreakpoints():
                # It was either a known BP or a sendBreak()
                return

            elif self.execing:
                self.execing = False
                self.handleAttach()

            else:
                self._fireSignal(sig)

        elif sig == signal.SIGSTOP:
            # We get a regular POSIX stop signal on attach
            #self.attaching = False
            self.handleAttach()

        else:
            self._fireSignal(sig)
                                   
    def platformProcessEvent(self, event):
        """
        Handle a mach exception message
        """
        #if self.attaching:
            #self.useptrace = True
            #return self.handlePosixSignal(event)

        #self.useptrace = False

        # Some event states that need to be reset
        self.softexc = False

        threadid, excode, codes = event

        # Set the thread that signaled.
        self.setMeta('ThreadId', threadid)
        self.setMeta('StoppedThreadId', threadid)
        self.setMeta('MachException', event)

        if excode == EXC_SOFTWARE:

            self.softexc = True

            assert(len(codes) == 2)
            assert(codes[0] == EXC_SOFT_SIGNAL)

            sig = codes[1]
            self.handlePosixSignal(sig)

        elif excode == EXC_BAD_ACCESS:
            logger.warning('exc_bad_access %s', str([hex(x) for x in codes]))
            signo = signal.SIGSEGV
            #if codes[0] == KERN_INVALID_ADDRESS:
                #signo = signal.SIGBUS

            self._fireSignal(signo)

        elif excode == EXC_BAD_INSTRUCTION:
            logger.warning('exc_bad_instruction %s', str([hex(x) for x in codes]))
            self._fireSignal(signal.SIGILL)

        elif excode == EXC_CRASH:
            logger.warning('Crash: %s', str([hex(x) for x in codes]))
            self._fireExit(0xffffffff)

        elif excode == EXC_BREAKPOINT:
            logger.warning('exc_breakpoint: %s', str(codes))
            self.handlePosixSignal(signal.SIGTRAP)

        else:
            logger.warning('Unprocessed Exception Type: %d', excode)
            self.fireNotifiers(vtrace.NOTIFY_SIGNAL)

        return

    def platformAttach(self, pid):
        #print 'CLASSIC',self.machhelper.is_pid_classic(pid)
        #self.attaching = True
        self.task = self.taskForPid(pid)
        self.setExceptionPort()
        assert( self.libc.ptrace(PT_ATTACHEXC, pid, 0, 0) == 0 )

    def taskForPid(self, pid):
        task = ctypes.c_uint32()
        ret = self.libc.task_for_pid(self.myport, pid, addrof(task))
        if ret != 0:
            raise Exception('task_for_pid failed: 0x%.8x\n' % ret)
        return task.value

    def newMachPort(self, right):
        port = mach_port_name_t()
        assert( self.libc.mach_port_allocate(self.myport, right, addrof(port)) == 0)
        return port.value

    def newMachRWPort(self):
        port = self.newMachPort(MACH_PORT_RIGHT_RECEIVE)
        assert( self.libc.mach_port_insert_right(self.myport, port, port, MACH_MSG_TYPE_MAKE_SEND) == 0 )
        return port

    def addPortToSet(self, port):
        assert( self.libc.mach_port_move_member(self.myport, port, self.portset) == 0 )

    def setExceptionPort(self):
        # Set the target task's exception port to our excport
        #r = self.libc.task_set_exception_ports(self.task, EXC_MASK_SOFTWARE, self.excport,
        r = self.libc.task_set_exception_ports( self.task,
                                                EXC_MASK_ALL,
                                                self.excport,
                                                EXCEPTION_DEFAULT,
                                                THREAD_STATE_NONE)
        if r != 0:
            raise Exception('task_set_exception_ports failed: 0x%.8x' % r)

    def _getNextExc(self, timeout=None):

        exc = exc_msg()

        flags = MACH_RCV_MSG | MACH_RCV_LARGE
        if timeout is not None:
            flags |= MACH_RCV_TIMEOUT
            
        r = self.libc.mach_msg(addrof(exc),
                           flags,
                           0,                   # Send size...
                           ctypes.sizeof(exc),  # Recv msg size
                           self.excport,
                           timeout,
                           MACH_PORT_NULL)

        if r == MACH_RCV_TIMED_OUT:
            return None

        if r != 0:
            raise Exception('mach_msg (RECV) failed: 0x%.8x' % r)

        return exc

    def platformWait(self):
        # Wait for a mach message on the exception port

        #exc = None
        #while exc is None:
            #exc = self._getNextExc()

        #self.setMeta('ThreadId', exc.thread.name)
        #self.setMeta('StoppedThreadId', exc.thread.name)

        #e2 = self._getNextExc(timeout=0)
        #if e2 is not None:
        #print "ALSO GOT",e2


        # Sometimes there are still posix signals anyway...
        #while os.waitpid(-1, os.WNOHANG) != (0,0):
            #pass

        #if self.attaching:
            #pid,status = os.waitpid(self.pid, 0)
            #return os.WSTOPSIG(status)

        #pid,status = os.waitpid(self.pid, 0)
        exc = self._getNextExc()

        # Suspend the task so reading etc is safe...
        self.libc.task_suspend(self.task)

        # NOTE We must extract *all* needed info from the event here!
        codes = [exc.codes[i] for i in range(exc.codeCnt)]
        ret = (exc.thread.name, exc.exception, codes)

        self.setMeta('MachExcMsg', exc)
        #self.sendExcResp(exc)

        return ret

    def sendExcResp(self, exc, maskexc=False):

        res = self.buildExcResp(exc, maskexc=maskexc)
        x = self.libc.mach_msg( addrof(res),
                                MACH_SEND_MSG,
                                res.Head.msgh_size,
                                0, 
                                res.Head.msgh_remote_port,
                                MACH_MSG_TIMEOUT_NONE,
                                MACH_PORT_NULL)

        if x != 0:
            raise Exception('mach_msg MACH_SEND_MSG failed: 0x%.8x' % (x,))

    def buildExcResp(self, exc, maskexc=False):
        res = exc_rep_msg()
        self.machhelper.vtrace_exc_server(ctypes.pointer(exc.Head), ctypes.pointer(res.Head), maskexc)
        return res

    def platformStepi(self):
        self.stepping = True

        exc = self.getMeta('MachExcMsg')
        if exc is not None:
            self.setMeta('MachExcMsg', None)
            maskexc = ( self.getCurrentSignal() is None )
            self.sendExcResp(exc, maskexc=maskexc)

        assert( self.libc.task_resume(self.task) == 0 )
        assert( self.libc.ptrace(PT_STEP, self.pid, 1, 0) == 0 )

    def platformContinue(self):

        sig = self.getCurrentSignal()
        if sig is None:
            sig = 0

        #threadid = self.getMeta('StoppedThreadId', 0)
        #if self.softexc:
            #assert( self.macptrace(PT_THUPDATE, self.pid, threadid, sig) == 0 )

        # If we have a mach message to respond to, lets do that....
        exc = self.getMeta('MachExcMsg')
        if exc is not None:
            self.setMeta('MachExcMsg', None)
            maskexc = ( self.getCurrentSignal() is None )
            self.sendExcResp(exc, maskexc=maskexc)

        #if self.useptrace:
            #assert( self.libc.ptrace(PT_THUPDATE, self.pid, threadid, sig) == 0 )
            #assert( self.libc.ptrace(PT_CONTINUE, self.pid, 1, sig) == 0 )
            #return

        if self.softexc:
            assert( self.macptrace(PT_CONTINUE, self.pid, 1, sig) == 0 )

        assert( self.libc.task_resume(self.task) == 0 )

    def macptrace(self, request, pid, addr, data, zok=True):
        ret = self.libc.ptrace(request, pid, addr, data)
        if ret != 0 and zok:
            self.libc.perror('macptrace: ')
        return ret

    def platformDetach(self):
        assert( self.libc.task_resume(self.task) == 0 )
        assert( self.macptrace(PT_DETACH, self.pid, 0, 0) == 0 )

        #for threadport in self._getThreadPorts():
            #print 'threadport', self.libc.mach_port_deallocate(self.myport, threadport)

        logger.debug('darwin detach:')
        logger.debug(self.libc.mach_port_deallocate(self.myport, self.task))
        logger.debug(self.libc.mach_port_deallocate(self.myport, self.excport))
        logger.debug(self.libc.mach_port_deallocate(self.myport, self.portset))

    def platformReadMemory(self, address, size):
        pval = ctypes.c_void_p(0)
        sval = ctypes.c_uint32(0)
        assert( self.libc.mach_vm_read(self.task, address, size, addrof(pval), addrof(sval)) == 0 )
        buf = ctypes.string_at(pval.value, sval.value)
        assert( self.libc.vm_deallocate(self.myport, pval, sval) == 0 )
        return buf

    def platformWriteMemory(self, address, data):
        assert( self.libc.vm_write(self.task, address, data, len(data)) == 0 )

    # FIXME use vm_allocate for allocate memory
    # FIXME use vm_protect

class Darwini386Trace(
            vtrace.Trace,
            DarwinMixin,
            v_i386.i386Mixin,
            v_base.TracerBase):

    def __init__(self):
        vtrace.Trace.__init__(self)
        v_base.TracerBase.__init__(self)
        v_i386.i386Mixin.__init__(self)
        DarwinMixin.__init__(self)

    def getThreadException(self, tid):
        # Each arch trace must implement this...
        state = STRUCT_X86_EXCEPTION_STATE32()
        scount = ctypes.c_uint32(ctypes.sizeof(state) / 4)
        ret = self.libc.thread_get_state(tid, x86_EXCEPTION_STATE32, addrof(state), addrof(scount));
        if ret != 0:
            raise Exception('thread_get_state failed: 0x%.8x' % ret)
        return state.trapno, state.err, state.faultvaddr

    def platformGetRegCtx(self, tid):
        ctx = self.archGetRegCtx()
        # NOTE: the tid *is* the port...

        state = STRUCT_X86_THREAD_STATE32()
        scount = ctypes.c_uint32(ctypes.sizeof(state) / 4)
        ret = self.libc.thread_get_state(tid, x86_THREAD_STATE32, addrof(state), addrof(scount));
        if ret != 0:
            raise Exception('thread_get_state (THREAD_STATE32) failed: 0x%.8x' % ret)
        ctx._rctx_Import(state)

        state = STRUCT_X86_DEBUG_STATE32()
        scount = ctypes.c_uint32(ctypes.sizeof(state) / 4)
        ret = self.libc.thread_get_state(tid, x86_DEBUG_STATE32, addrof(state), addrof(scount));
        if ret != 0:
            raise Exception('thread_get_state (DEBUG_STATE32) failed: 0x%.8x' % ret)
        ctx._rctx_Import(state)

        return ctx

    def platformSetRegCtx(self, tid, ctx):
        state = STRUCT_X86_THREAD_STATE32()

        # Sync up a struct first...
        scount = ctypes.c_uint32(ctypes.sizeof(state) / 4)
        ret = self.libc.thread_get_state(tid, x86_THREAD_STATE32, addrof(state), addrof(scount));
        if ret != 0:
            raise Exception('thread_get_state (THREAD_STATE32) failed: 0x%.8x' % ret)

        # Export our shit into it...
        ctx._rctx_Export(state)

        scount = ctypes.sizeof(state) / 4
        r = self.libc.thread_set_state(tid, x86_THREAD_STATE32, addrof(state), scount)
        if r != 0:
            raise Exception('thread_set_state (THREAD_STATE32) failed: 0x%.8x' % r)

        state = STRUCT_X86_DEBUG_STATE32()
        ctx._rctx_Export(state)
        scount = ctypes.sizeof(state) / 4
        r = self.libc.thread_set_state(tid, x86_DEBUG_STATE32, addrof(state), scount)
        if r != 0:
            raise Exception('thread_set_state (DEBUG_STATE32) failed: 0x%.8x' % r)

class DarwinAmd64Trace(
            vtrace.Trace,
            DarwinMixin,
            v_amd64.Amd64Mixin,
            v_base.TracerBase):

    def __init__(self):
        vtrace.Trace.__init__(self)
        v_base.TracerBase.__init__(self)
        v_amd64.Amd64Mixin.__init__(self)
        DarwinMixin.__init__(self)

    def getThreadException(self, tid):
        # Each arch trace must implement this...
        state = STRUCT_X86_EXCEPTION_STATE64()
        scount = ctypes.c_uint32(ctypes.sizeof(state) / 8)
        ret = self.libc.thread_get_state(tid, x86_EXCEPTION_STATE64, addrof(state), addrof(scount));
        if ret != 0:
            raise Exception('thread_get_state failed: 0x%.8x' % ret)
        return state.trapno, state.err, state.faultvaddr

    def platformGetRegCtx(self, tid):
        ctx = self.archGetRegCtx()
        # NOTE: the tid *is* the port...

        state = STRUCT_X86_THREAD_STATE64()
        scount = ctypes.c_uint32(ctypes.sizeof(state) / 4)
        ret = self.libc.thread_get_state(tid, x86_THREAD_STATE64, addrof(state), addrof(scount));
        if ret != 0:
            self.libc.mach_error("thread_get_state x86_THREAD_STATE64 failed:", ret)
            raise Exception('thread_get_state (THREAD_STATE64) failed: 0x%.8x' % ret)
        ctx._rctx_Import(state)

        state = STRUCT_X86_DEBUG_STATE64()
        scount = ctypes.c_uint32(ctypes.sizeof(state) / 4)
        ret = self.libc.thread_get_state(tid, x86_DEBUG_STATE64, addrof(state), addrof(scount));
        if ret != 0:
            self.libc.mach_error("thread_get_state x86_DEBUG_STATE64 failed:", ret)
            raise Exception('thread_get_state (DEBUG_STATE64) failed: 0x%.8x' % ret)
        ctx._rctx_Import(state)

        return ctx

    def platformSetRegCtx(self, tid, ctx):

        state = STRUCT_X86_THREAD_STATE64()

        # Sync up a struct first...
        scount = ctypes.c_uint32(ctypes.sizeof(state) / 8)
        ret = self.libc.thread_get_state(tid, x86_THREAD_STATE64, addrof(state), addrof(scount));
        if ret != 0:
            raise Exception('thread_get_state (THREAD_STATE64) failed: 0x%.8x' % ret)

        # Export our shit into it...
        ctx._rctx_Export(state)

        scount = ctypes.sizeof(state) / 8
        r = self.libc.thread_set_state(tid, x86_THREAD_STATE64, addrof(state), scount)
        if r != 0:
            raise Exception('thread_set_state (THREAD_STATE64) failed: 0x%.8x' % r)

        state = STRUCT_X86_DEBUG_STATE64()
        ctx._rctx_Export(state)
        scount = ctypes.sizeof(state) / 8
        r = self.libc.thread_set_state(tid, x86_DEBUG_STATE64, addrof(state), scount)
        if r != 0:
            raise Exception('thread_set_state (DEBUG_STATE64) failed: 0x%.8x' % r)
