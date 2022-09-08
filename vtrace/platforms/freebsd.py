"""
FreeBSD support...
"""

import os
import ctypes
import ctypes.util as cutil
import logging

import envi.cli as e_cli
import envi.const as e_const

import vtrace
import vtrace.archs.i386 as v_i386
import vtrace.archs.amd64 as v_amd64
import vtrace.platforms.base as v_base
import vtrace.platforms.posix as v_posix
import vtrace.util as v_util

logger = logging.getLogger(__name__)

libc = ctypes.CDLL(cutil.find_library("c"))
libkvm = ctypes.CDLL(cutil.find_library("kvm"))

# kvm_getprocs cmds
KERN_PROC_ALL           = 0       # everything
KERN_PROC_PID           = 1       # by process id
KERN_PROC_PGRP          = 2       # by process group id
KERN_PROC_SESSION       = 3       # by session of pid
KERN_PROC_TTY           = 4       # by controlling tty
KERN_PROC_UID           = 5       # by effective uid
KERN_PROC_RUID          = 6       # by real uid
KERN_PROC_ARGS          = 7       # get/set arguments/proctitle
KERN_PROC_PROC          = 8       # only return procs
KERN_PROC_SV_NAME       = 9       # get syscall vector name
KERN_PROC_RGID          = 10      # by real group id
KERN_PROC_GID           = 11      # by effective group id
KERN_PROC_PATHNAME      = 12      # path to executable
KERN_PROC_INC_THREAD    = 0x10    # Include threads in filtered results

pid_t = ctypes.c_int32
lwpid_t = ctypes.c_int32
void_p = ctypes.c_void_p
dev_t = ctypes.c_uint32
sigset_t = ctypes.c_uint32*4
uid_t = ctypes.c_uint32
gid_t = ctypes.c_uint32
fixpt_t = ctypes.c_uint32
caddr_t = ctypes.c_void_p
vm_size_t = ctypes.c_ulong
segsz_t = ctypes.c_ulong

# Could go crazy and grep headers for this stuff ;)
KI_NGROUPS = 16
OCOMMLEN = 16
WMESGLEN = 8
LOGNAMELEN = 17
LOCKNAMELEN = 8
COMMLEN = 19
KI_EMULNAMELEN = 16
KI_NSPARE_INT = 10
KI_NSPARE_PTR = 7
KI_NSPARE_LONG = 12


def c_buf(size):
    return ctypes.c_char * size

class PRIORITY(ctypes.Structure):
    _fields_ = (
        ("pri_class", ctypes.c_ubyte),
        ("pri_level", ctypes.c_ubyte),
        ("pri_native", ctypes.c_ubyte),
        ("pri_user", ctypes.c_ubyte)
    )

class TIMEVAL(ctypes.Structure):
    _fields_ = (
        ("tv_sec", ctypes.c_long),
        ("tv_usec", ctypes.c_long)
    )

class RUSAGE(ctypes.Structure):
    _fields_ = (
        ("ru_utime", TIMEVAL),          # user time used
        ("ru_stime", TIMEVAL),          # system time used
        ("ru_maxrss", ctypes.c_long),   #
        ("ru_ixrss", ctypes.c_long),    # (j) integral shared memory size
        ("ru_idrss", ctypes.c_long),    # (j) integral unshared data
        ("ru_isrss", ctypes.c_long),    # (j) integral unshared stack
        ("ru_minflt", ctypes.c_long),   # (c) page reclaims
        ("ru_majflt", ctypes.c_long),   # (c) page faults
        ("ru_nswap", ctypes.c_long),    # (c + j) swaps
        ("ru_inblock", ctypes.c_long),  # (n) block input operations
        ("ru_oublock", ctypes.c_long),  # (n) block output operations
        ("ru_msgsnd", ctypes.c_long),   # (n) messages sent
        ("ru_msgrcv", ctypes.c_long),   # (n) messages received
        ("ru_nsignals", ctypes.c_long), # (c) signals received
        ("ru_nvcsw", ctypes.c_long),    # (j) voluntary context switches
        ("ru_nivcsw", ctypes.c_long),   # (j) involuntary
    )


class KINFO_PROC(ctypes.Structure):
    _fields_ = (
        ("ki_structsize", ctypes.c_int),# size of this structure
        ("ki_layout", ctypes.c_int),    # reserved: layout identifier
        ("ki_args", void_p),            # address of command arguments (struct pargs*)
        ("ki_paddr", void_p),           # address of proc (struct proc*)
        ("ki_addr", void_p),            # kernel virtual addr of u-area (struct user*)
        ("ki_tracep", void_p),          # pointer to trace file (struct vnode *)
        ("ki_textvp", void_p),          # pointer to executable file (struct vnode *)
        ("ki_fd", void_p),              # pointer to open file info (struct filedesc  *)
        ("ki_vmspace", void_p),         # pointer to kernel vmspace struct (struct vmspace *)
        ("ki_wchan", void_p),           # sleep address (void*)
        ("ki_pid", pid_t),              # Process identifier
        ("ki_ppid", pid_t),             # parent process id
        ("ki_pgid", pid_t),             # process group id
        ("ki_tpgid", pid_t),            # tty process group id
        ("ki_sid", pid_t),              # Process session ID
        ("ki_tsid", pid_t),             # Terminal session ID
        ("ki_jobc", ctypes.c_short),    # job control counter
        ("ki_spare_short1", ctypes.c_short), #
        ("ki_tdev", dev_t),             # controlling tty dev
        ("ki_siglist", sigset_t),       # Signals arrived but not delivered
        ("ki_sigmask", sigset_t),       # Current signal mask
        ("ki_sigignore", sigset_t),     # Signals being ignored
        ("ki_sigcatch", sigset_t),      # Signals being caught by user
        ("ki_uid", uid_t),              # effective user id
        ("ki_ruid", uid_t),             # Real user id
        ("ki_svuid", uid_t),            # Saved effective user id
        ("ki_rgid", gid_t),             # Real group id
        ("ki_svgid", gid_t),            # Saved effective group id
        ("ki_ngroups", ctypes.c_short), # number of groups
        ("ki_spare_short2", ctypes.c_short),
        ("ki_groups", gid_t * KI_NGROUPS), # groups
        ("ki_size", vm_size_t),         # virtual size
        ("ki_rssize", segsz_t),         # current resident set size in pages
        ("ki_swrss", segsz_t),          # resident set size before last swap
        ("ki_tsize", segsz_t),          # text size (pages) XXX
        ("ki_dsize", segsz_t),          # data size (pages) XXX
        ("ki_ssize", segsz_t),          # stack size (pages)
        ("ki_xstat", ctypes.c_ushort),  # Exit status for wait and stop signal
        ("ki_acflag", ctypes.c_ushort), # Accounting flags
        ("ki_pctcpu", fixpt_t),         # %cpu for process during ki_swtime
        ("ki_estcpu", ctypes.c_uint),   # Time averaged value of ki_cpticks
        ("ki_slptime", ctypes.c_uint),  # Time since last blocked
        ("ki_swtime", ctypes.c_uint),   # Time swapped in or out
        ("ki_spareint1", ctypes.c_int), # unused (just here for alignment)
        ("ki_runtime", ctypes.c_uint64),# Real time in microsec
        ("ki_start", TIMEVAL),          # starting time
        ("ki_childtime", TIMEVAL),      # time used by process children
        ("ki_flag", ctypes.c_long),     # P_* flags
        ("ki_kiflag", ctypes.c_long),   # KI_* flags
        ("ki_traceflag", ctypes.c_int), # kernel trace points
        ("ki_stat", ctypes.c_char),     # S* process status
        ("ki_nice", ctypes.c_ubyte),    # Process "nice" value
        ("ki_lock", ctypes.c_char),     # Process lock (prevent swap) count
        ("ki_rqindex", ctypes.c_char),  # Run queue index
        ("ki_oncpu", ctypes.c_char),    # Which cpu we are on
        ("ki_lastcpu", ctypes.c_char),  # Last cpu we were on
        ("ki_ocomm", c_buf(OCOMMLEN+1)),      # command name
        ("ki_wmesg", c_buf(WMESGLEN+1)),      # wchan message
        ("ki_login", c_buf(LOGNAMELEN+1)),    # setlogin name
        ("ki_lockname", c_buf(LOCKNAMELEN+1)),# lock name
        ("ki_comm", c_buf(COMMLEN+1)),        # command name
        ("ki_emul", c_buf(KI_EMULNAMELEN+1)), # emulation name
        ("ki_sparestrings",c_buf(68)),   # spare string space
        ("ki_spareints", ctypes.c_int*KI_NSPARE_INT),
        ("ki_jid", ctypes.c_int),       # Process jail ID
        ("ki_numthreads", ctypes.c_int),# KSE number of total threads
        ("ki_tid", lwpid_t),            # thread id
        ("ki_pri", PRIORITY),           # process priority
        ("ki_rusage", RUSAGE),          # process rusage statistics
        # XXX - most fields in ki_rusage_ch are not (yet) filled in
        ("ki_rusage_ch", RUSAGE),       # rusage of children processes
        ("ki_pcb", void_p),             # kernel virtual addr of pcb
        ("ki_kstack", void_p),          # kernel virtual addr of stack
        ("ki_udata", void_p),           # User convenience pointer
        ("ki_spareptrs", void_p*KI_NSPARE_PTR),
        ("ki_sparelongs", ctypes.c_long*KI_NSPARE_LONG),
        ("ki_sflag", ctypes.c_long),    # PS_* flags
        ("ki_tdflags", ctypes.c_long),  # KSE kthread flag
    )

libkvm.kvm_getprocs.argtypes = [caddr_t, ctypes.c_int, ctypes.c_int, caddr_t]
libkvm.kvm_getprocs.restype = ctypes.POINTER(KINFO_PROC)

libkvm.kvm_open.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p]
libkvm.kvm_open.restype = caddr_t

# All the FreeBSD ptrace defines
PT_TRACE_ME     = 0       #/* child declares it's being traced */
PT_READ_I       = 1       #/* read word in child's I space */
PT_READ_D       = 2       #/* read word in child's D space */
PT_WRITE_I      = 4       #/* write word in child's I space */
PT_WRITE_D      = 5       #/* write word in child's D space */
PT_CONTINUE     = 7       #/* continue the child */
PT_KILL         = 8       #/* kill the child process */
PT_STEP         = 9       #/* single step the child */
PT_ATTACH       = 10      #/* trace some running process */
PT_DETACH       = 11      #/* stop tracing a process */
PT_IO           = 12      #/* do I/O to/from stopped process. */
PT_LWPINFO      = 13      #/* Info about the LWP that stopped. */
PT_GETNUMLWPS   = 14      #/* get total number of threads */
PT_GETLWPLIST   = 15      #/* get thread list */
PT_CLEARSTEP    = 16      #/* turn off single step */
PT_SETSTEP      = 17      #/* turn on single step */
PT_SUSPEND      = 18      #/* suspend a thread */
PT_RESUME       = 19      #/* resume a thread */
PT_TO_SCE       = 20      # Stop on syscall entry
PT_TO_SCX       = 21      # Stop on syscall exit
PT_SYSCALL      = 22      # Stop on syscall entry and exit
PT_GETREGS      = 33      #/* get general-purpose registers */
PT_SETREGS      = 34      #/* set general-purpose registers */
PT_GETFPREGS    = 35      #/* get floating-point registers */
PT_SETFPREGS    = 36      #/* set floating-point registers */
PT_GETDBREGS    = 37      #/* get debugging registers */
PT_SETDBREGS    = 38      #/* set debugging registers */
#PT_FIRSTMACH    = 64      #/* for machine-specific requests */

# On PT_IO addr is a pointer to a struct

class PTRACE_IO_DESC(ctypes.Structure):
    _fields_ = [
        ("piod_op", ctypes.c_int),      # I/O operation
        ("piod_offs", ctypes.c_void_p), # Child offset
        ("piod_addr", ctypes.c_void_p), # Parent Offset
        ("piod_len", ctypes.c_uint)     # Size
    ]

# Operations in piod_op.
PIOD_READ_D     = 1       # Read from D space
PIOD_WRITE_D    = 2       # Write to D space
PIOD_READ_I     = 3       # Read from I space
PIOD_WRITE_I    = 4       # Write to I space

class PTRACE_LWPINFO(ctypes.Structure):
    _fields_ = (
        ("pl_lwpid", lwpid_t),
        ("pl_event", ctypes.c_int),
        ("pl_flags", ctypes.c_int),
        ("pl_sigmask", sigset_t),
        ("pl_siglist", sigset_t),
    )

PL_EVENT_NONE   = 0
PL_EVENT_SIGNAL = 1

PL_FLAGS_SA    = 0
PL_FLAGS_BOUND = 1

class FreeBSDMixin:

    def __init__(self):
        self.initMode("Syscall", False, "Break on Syscalls")
        self.kvmh = libkvm.kvm_open(None, None, None, 0, "vtrace")
        if not os.path.exists('/proc/curproc/file'):
            raise Exception("VDB needs /proc! (use: mount -t procfs procfs /proc)")

    def finiMixin(self):
        if self.kvmh is not None:
            libkvm.kvm_close(self.kvmh)

    def platformReadMemory(self, address, size):
        #FIXME optimize for speed!
        iod = PTRACE_IO_DESC()
        buf = ctypes.create_string_buffer(size)

        iod.piod_op = PIOD_READ_D
        iod.piod_addr = ctypes.addressof(buf)
        iod.piod_offs = address
        iod.piod_len = size

        if v_posix.ptrace(PT_IO, self.pid, ctypes.addressof(iod), 0) != 0:
            raise Exception("ptrace PT_IO failed to read 0x%.8x" % address)

        return buf.raw

    def platformWriteMemory(self, address, buf):
        #FIXME optimize for speed!
        iod = PTRACE_IO_DESC()

        cbuf = ctypes.create_string_buffer(buf)

        iod.piod_op = PIOD_WRITE_D
        iod.piod_addr = ctypes.addressof(cbuf)
        iod.piod_offs = address
        iod.piod_len = len(buf)

        if v_posix.ptrace(PT_IO, self.pid, ctypes.addressof(iod), 0) != 0:
            raise Exception("ptrace PT_IO failed to write 0x%.8x" % address)

    @v_base.threadwrap
    def platformAttach(self, pid):
        if v_posix.ptrace(PT_ATTACH, pid, 0, 0) != 0:
            raise Exception("Ptrace Attach Failed")

    def _getExeName(self, pid):
        return os.readlink('/proc/%d/file' % pid)

    #@v_base.threadwrap
    def platformExec(self, cmdline):
        # Basically just like the one in the Ptrace mixin...
        self.execing = True
        cmdlist = e_cli.splitargs(cmdline)
        os.stat(cmdlist[0])
        pid = os.fork()
        if pid == 0:
            v_posix.ptrace(PT_TRACE_ME, 0, 0, 0)
            os.execv(cmdlist[0], cmdlist)
            sys.exit(-1)
        return pid

    def handleAttach(self):
        self.setMeta('ExeName', self._getExeName(self.pid))
        return v_posix.PosixMixin.handleAttach(self)

    @v_base.threadwrap
    def platformWait(self):

        pid,status = v_posix.PosixMixin.platformWait(self)

        # Get the thread id from the ptrace interface
        info = PTRACE_LWPINFO()
        size = ctypes.sizeof(info)
        if v_posix.ptrace(PT_LWPINFO, self.pid, ctypes.addressof(info), size) == 0:
            self.setMeta('ThreadId', info.pl_lwpid)

        return pid,status

    @v_base.threadwrap
    def platformProcessEvent(self, event):

        pid,status = event

        if os.WIFEXITED(status):

            exitcode = os.WEXITSTATUS(status)

            tid = self.getMeta("ThreadId", None)
            if tid is None or len(self.getThreads()) == 0:
                self._fireExit( exitcode )
                return

            self._fireExitThread(tid, exitcode)

            # set thread to pid ( the thread exited... so... )
            self.setMeta('ThreadId', pid)
            self._fireExit( exitcode )

        elif os.WIFSIGNALED(status):
            self._fireExit( os.WTERMSIG( status ) )

        elif os.WIFSTOPPED(status):
            sig = os.WSTOPSIG(status)
            self.handlePosixSignal(sig)

        else:
            logger.warning('Received unknown event: %s', event)


    @v_base.threadwrap
    def platformStepi(self):
        self.stepping = True
        if v_posix.ptrace(PT_STEP, self.pid, 1, 0) != 0:
            raise Exception("ptrace PT_STEP failed!")

    @v_base.threadwrap
    def platformContinue(self):
        cmd = PT_CONTINUE
        if self.getMode("Syscall"):
            cmd = PT_SYSCALL

        sig = self.getCurrentSignal()
        if sig is None:
            sig = 0

        # In freebsd address is the place to continue from
        # but 1 means use existing EIP
        if v_posix.ptrace(cmd, self.pid, 1, sig) != 0:
            raise Exception("ptrace PT_CONTINUE/PT_SYSCALL failed")

    @v_base.threadwrap
    def platformDetach(self):
        if v_posix.ptrace(PT_DETACH, self.pid, 1, 0) != 0:
            raise Exception("Ptrace Detach Failed")

    @v_base.threadwrap
    def platformGetThreads(self):
        ret = {}
        cnt = self._getThreadCount()
        if cnt & 0xffffffff == 0xffffffff:
            return ret
        buf = (ctypes.c_int * cnt)()
        if v_posix.ptrace(PT_GETLWPLIST, self.pid, ctypes.addressof(buf), cnt) != cnt:
            raise Exception("ptrace PW_GETLWPLIST failed")
        for x in buf:
            ret[x] = x
        return ret

    @v_base.threadwrap
    def platformSuspendThread(self, tid):
        if v_posix.ptrace(PT_SUSPEND, tid, 0, 0) != 0:
            raise Exception("ptrace PT_SUSPEND failed!")

    @v_base.threadwrap
    def platformResumeThread(self, tid):
        if v_posix.ptrace(PT_RESUME, tid, 0, 0) != 0:
            raise Exception("ptrace PT_RESUME failed!")

    def _getThreadCount(self):
        return v_posix.ptrace(PT_GETNUMLWPS, self.pid, 0, 0)

    def platformGetFds(self):
        return []

    def platformGetMaps(self):
        # FIXME make this not need proc
        ret = []
        mpath = "/proc/%d/map" % self.pid

        with open(mpath, 'rb') as mapfile:
            for line in mapfile:
                perms = 0
                fname = ""
                maptup = line.split(None)
                base = int(maptup[0], 16)
                max  = int(maptup[1], 16)
                permstr = maptup[5]

                if maptup[11] == "vnode":
                    fname = maptup[12].strip()

                if permstr[0] == 'r':
                    perms |= e_const.MM_READ

                if permstr[1] == 'w':
                    perms |= e_const.MM_WRITE

                if permstr[2] == 'x':
                    perms |= e_const.MM_EXEC

                ret.append((base, max-base, perms, fname))

        return ret

    def platformPs(self):
        ret = []
        cnt = ctypes.c_uint(0)

        p = libkvm.kvm_getprocs(self.kvmh, KERN_PROC_PROC, 0, ctypes.addressof(cnt))
        for i in range(cnt.value):
            kinfo = p[i]
            if kinfo.ki_structsize != ctypes.sizeof(KINFO_PROC):
                logger.warning("WARNING: KINFO_PROC CHANGED SIZE, Trying to account for it... good luck")
            ret.append((kinfo.ki_pid, kinfo.ki_comm))

        ret.reverse()
        return ret

class bsd_regs_i386(ctypes.Structure):
    _fields_ = (
        ("fs",  ctypes.c_ulong),
        ("es",  ctypes.c_ulong),
        ("ds",  ctypes.c_ulong),
        ("edi",  ctypes.c_ulong),
        ("esi",  ctypes.c_ulong),
        ("ebp",  ctypes.c_ulong),
        ("isp",  ctypes.c_ulong),
        ("ebx",  ctypes.c_ulong),
        ("edx",  ctypes.c_ulong),
        ("ecx",  ctypes.c_ulong),
        ("eax",  ctypes.c_ulong),
        ("trapno",  ctypes.c_ulong),
        ("err",  ctypes.c_ulong),
        ("eip",  ctypes.c_ulong),
        ("cs",  ctypes.c_ulong),
        ("eflags",  ctypes.c_ulong),
        ("esp",  ctypes.c_ulong),
        ("ss",  ctypes.c_ulong),
        ("gs",  ctypes.c_ulong),
        ("debug0",  ctypes.c_ulong),
        ("debug1",  ctypes.c_ulong),
        ("debug2",  ctypes.c_ulong),
        ("debug3",  ctypes.c_ulong),
        ("debug4",  ctypes.c_ulong),
        ("debug5",  ctypes.c_ulong),
        ("debug6",  ctypes.c_ulong),
        ("debug7",  ctypes.c_ulong),
    )

i386_DBG_OFF = (19*4)

class bsd_regs_amd64(ctypes.Structure):
    _fields_ = (
        ("r15", ctypes.c_ulonglong),
        ("r14", ctypes.c_ulonglong),
        ("r13", ctypes.c_ulonglong),
        ("r12", ctypes.c_ulonglong),
        ("r11", ctypes.c_ulonglong),
        ("r10", ctypes.c_ulonglong),
        ("r9", ctypes.c_ulonglong),
        ("r8", ctypes.c_ulonglong),
        ("rdi", ctypes.c_ulonglong),
        ("rsi", ctypes.c_ulonglong),
        ("rbp", ctypes.c_ulonglong),
        ("rbx", ctypes.c_ulonglong),
        ("rdx", ctypes.c_ulonglong),
        ("rcx", ctypes.c_ulonglong),
        ("rax", ctypes.c_ulonglong),
        ("trapno", ctypes.c_ulonglong),
        ("err", ctypes.c_ulonglong),
        ("rip", ctypes.c_ulonglong),
        ("cs", ctypes.c_ulonglong),
        ("rflags", ctypes.c_ulonglong),
        ("rsp", ctypes.c_ulonglong),
        ("ss", ctypes.c_ulonglong),
        ("debug0", ctypes.c_ulonglong),
        ("debug1", ctypes.c_ulonglong),
        ("debug2", ctypes.c_ulonglong),
        ("debug3", ctypes.c_ulonglong),
        ("debug4", ctypes.c_ulonglong),
        ("debug5", ctypes.c_ulonglong),
        ("debug6", ctypes.c_ulonglong),
        ("debug7", ctypes.c_ulonglong),
        ("debug8", ctypes.c_ulonglong),
        ("debug9", ctypes.c_ulonglong),
        ("debug10", ctypes.c_ulonglong),
        ("debug11", ctypes.c_ulonglong),
        ("debug12", ctypes.c_ulonglong),
        ("debug13", ctypes.c_ulonglong),
        ("debug14", ctypes.c_ulonglong),
        ("debug15", ctypes.c_ulonglong),
    )

amd64_DBG_OFF = (22*ctypes.sizeof(ctypes.c_uint64))

class FreeBSDi386Trace(
    vtrace.Trace,
    FreeBSDMixin,
    v_i386.i386Mixin,
    v_posix.ElfMixin,
    v_posix.PosixMixin,
    v_base.TracerBase):

    def __init__(self):
        vtrace.Trace.__init__(self)
        v_base.TracerBase.__init__(self)
        v_posix.ElfMixin.__init__(self)
        v_posix.PosixMixin.__init__(self)
        v_i386.i386Mixin.__init__(self)
        FreeBSDMixin.__init__(self)

    @v_base.threadwrap
    def platformGetRegCtx(self, tid):
        ctx = self.archGetRegCtx()
        u = bsd_regs_i386()

        addr = ctypes.addressof(u)
        if v_posix.ptrace(PT_GETREGS, tid, addr, 0) != 0:
            raise Exception("ptrace PT_GETREGS failed!")

        if v_posix.ptrace(PT_GETDBREGS, tid, addr+i386_DBG_OFF, 0) != 0:
            raise Exception("ptrace PT_GETDBREGS failed!")

        ctx._rctx_Import(u)

        return ctx

    @v_base.threadwrap
    def platformSetRegCtx(self, tid, ctx):
        u = bsd_regs_i386()
        ctx._rctx_Export(u)
        addr = ctypes.addressof(u)
        if v_posix.ptrace(PT_SETREGS, self.pid, addr, 0) != 0:
            raise Exception("ptrace PT_SETREGS failed!")
        if v_posix.ptrace(PT_SETDBREGS, self.pid, addr+i386_DBG_OFF, 0) != 0:
            raise Exception("ptrace PT_SETDBREGS failed!")


class FreeBSDAmd64Trace(
    vtrace.Trace,
    FreeBSDMixin,
    v_amd64.Amd64Mixin,
    v_posix.ElfMixin,
    v_posix.PosixMixin,
    v_base.TracerBase):

    def __init__(self):
        vtrace.Trace.__init__(self)
        v_base.TracerBase.__init__(self)
        v_posix.ElfMixin.__init__(self)
        v_posix.PosixMixin.__init__(self)
        v_amd64.Amd64Mixin.__init__(self)
        FreeBSDMixin.__init__(self)

    def _getAmdRegsStruct(self, tid):
        '''
        Get (and populate) a register structure
        (even set regs needs to get it first...)
        '''
        u = bsd_regs_amd64()
        addr = ctypes.addressof(u)
        if v_posix.ptrace(PT_GETREGS, tid, addr, 0) != 0:
            raise Exception("ptrace PT_GETREGS failed!")
        if v_posix.ptrace(PT_GETDBREGS, tid, addr+amd64_DBG_OFF, 0) != 0:
            raise Exception("ptrace PT_GETDBREGS failed!")
        return u

    @v_base.threadwrap
    def platformGetRegCtx(self, tid):
        ctx = self.archGetRegCtx()
        u = self._getAmdRegsStruct(tid)
        ctx._rctx_Import(u)
        return ctx

    @v_base.threadwrap
    def platformSetRegCtx(self, tid, ctx):
        u = self._getAmdRegsStruct(tid)
        ctx._rctx_Export(u)
        addr = ctypes.addressof(u)
        if v_posix.ptrace(PT_SETREGS, tid, addr, 0) != 0:
            raise Exception("ptrace PT_SETREGS failed!")
        if v_posix.ptrace(PT_SETDBREGS, tid, addr+amd64_DBG_OFF, 0) != 0:
            raise Exception("ptrace PT_SETDBREGS failed!")


