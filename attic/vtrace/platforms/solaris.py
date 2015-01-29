"""
Solaris Platform Module (Incomplete)
"""
# Copyright (C) 2007 Invisigoth - See LICENSE file for details
import os
import struct
import array

# Control codes (long values) for messages written to ctl and lwpctl files.
PCNULL   = 0L# null request, advance to next message */
PCSTOP   = 1L# direct process or lwp to stop and wait for stop */
PCDSTOP  = 2L# direct process or lwp to stop */
PCWSTOP  = 3L# wait for process or lwp to stop, no timeout */
PCTWSTOP = 4L# wait for stop, with long millisecond timeout arg */
PCRUN    = 5L# make process/lwp runnable, w/ long flags argument */
PCCSIG   = 6L# clear current signal from lwp */
PCCFAULT = 7L# clear current fault from lwp */
PCSSIG   = 8L# set current signal from siginfo_t argument */
PCKILL   = 9L# post a signal to process/lwp, long argument */
PCUNKILL = 10L# delete a pending signal from process/lwp, long arg */
PCSHOLD  = 11L# set lwp signal mask from sigset_t argument */
PCSTRACE = 12L# set traced signal set from sigset_t argument */
PCSFAULT = 13L# set traced fault set from fltset_t argument */
PCSENTRY = 14L# set traced syscall entry set from sysset_t arg */
PCSEXIT  = 15L# set traced syscall exit set from sysset_t arg */
PCSET    = 16L# set modes from long argument */
PCUNSET  = 17L# unset modes from long argument */
PCSREG   = 18L# set lwp general registers from prgregset_t arg */
PCSFPREG = 19L# set lwp floating-point registers from prfpregset_t */
PCSXREG  = 20L# set lwp extra registers from prxregset_t arg */
PCNICE   = 21L# set nice priority from long argument */
PCSVADDR = 22L# set %pc virtual address from long argument */
PCWATCH  = 23L# set/unset watched memory area from prwatch_t arg */
PCAGENT  = 24L# create agent lwp with regs from prgregset_t arg */
PCREAD   = 25L# read from the address space via priovec_t arg */
PCWRITE  = 26L# write to the address space via priovec_t arg */
PCSCRED  = 27L# set process credentials from prcred_t argument */
PCSASRS  = 28L# set ancillary state registers from asrset_t arg */
PCSPRIV  = 29L# set process privileges from prpriv_t argument */
PCSZONE  = 30L# set zoneid from zoneid_t argument */
PCSCREDX = 31L# as PCSCRED but with supplemental groups */

# PCRUN long operand flags.
PRCSIG   = 0x01# clear current signal, if any */
PRCFAULT = 0x02# clear current fault, if any */
PRSTEP   = 0x04# direct the lwp to single-step */
PRSABORT = 0x08# abort syscall, if in syscall */
PRSTOP   = 0x10# set directed stop request */

# Status flags
PR_STOPPED  = 0x00000001# lwp is stopped */
PR_ISTOP    = 0x00000002# lwp is stopped on an event of interest */
PR_DSTOP    = 0x00000004# lwp has a stop directive in effect */
PR_STEP     = 0x00000008# lwp has a single-step directive in effect */
PR_ASLEEP   = 0x00000010# lwp is sleeping in a system call */
PR_PCINVAL  = 0x00000020# contents of pr_instr undefined */
PR_ASLWP    = 0x00000040# obsolete flag; never set */
PR_AGENT    = 0x00000080# this lwp is the /proc agent lwp */
PR_DETACH   = 0x00000100# this is a detached lwp */
PR_DAEMON   = 0x00000200# this is a daemon lwp */
# The following flags apply to the process, not to an individual lwp */
PR_ISSYS    = 0x00001000# this is a system process */
PR_VFORKP   = 0x00002000# process is the parent of a vfork()d child */
PR_ORPHAN   = 0x00004000# process's process group is orphaned */
# The following process flags are modes settable by PCSET/PCUNSET */
PR_FORK     = 0x00100000# inherit-on-fork is in effect */
PR_RLC      = 0x00200000# run-on-last-close is in effect */
PR_KLC      = 0x00400000# kill-on-last-close is in effect */
PR_ASYNC    = 0x00800000# asynchronous-stop is in effect */
PR_MSACCT   = 0x01000000# micro-state usage accounting is in effect */
PR_BPTADJ   = 0x02000000# breakpoint trap pc adjustment is in effect */
PR_PTRACE   = 0x04000000# ptrace-compatibility mode is in effect */
PR_MSFORK   = 0x08000000# micro-state accounting inherited on fork */
PR_IDLE     = 0x10000000# lwp is a cpu's idle thread */


# Permissions...
MA_READ    = 0x04# readable by the traced process */
MA_WRITE   = 0x02# writable by the traced process */
MA_EXEC    = 0x01# executable by the traced process */
MA_SHARED  = 0x08# changes are shared by mapped object */
MA_ANON    = 0x40# anonymous memory (e.g. /dev/zero) */
MA_ISM     = 0x80# intimate shared mem (shared MMU resources) */
MA_NORESERVE = 0x100# mapped with MAP_NORESERVE */
MA_SHM     = 0x200# System V shared memory */
MA_RESERVED1 = 0x400# reserved for future use */

class SolarisMixin:

    def initMixin(self):
        #import sunprocfs
        self.ctl = None

    def platformGetRegs(self):
        pid = self.getPid()

    #def platformGetThreads(self):
        #ret = []
        #for name in os.listdir("/proc/%d/lwp" % self.pid):
            #ret.append(int(name))
        #return ret

    def platformAttach(self, pid):
        self.ctl = file("/proc/%d/ctl" % pid, "ab")
        self.ctl.write(struct.pack("<L", PRSTOP))

    def platformContinue(self):
        """
        Tell the process to continue running
        """
        self.writeCtl(struct.pack("<LL", PCRUN, 0))

    def platformWait(self):
        """
        wait for the process to do someting "interesting"
        """
        self.writeCtl(struct.pack("<L", PCWSTOP))
        bytes = file("/proc/%d/psinfo" % self.pid, "rb").read()
        return bytes

    def writeCtl(self, bytes):
        os.write(self.ctl.fileno(), bytes)

    def platformDetach(self):
        print "SOLARIS DETACH"
        self.ctl.close()
        self.ctl = None

class SolarisIntelMixin:
    """
    Handle register formats for the intel solaris stuff
    """
    def getRegisterFormat(self):
        return ""

    def getRegisterNames(self):
        return []

    def platformReadMemory(self, addr, size):
        a = array.array('c',"\x00" * size)
        baddr, blen = a.buffer_info()
        priovec = struct.pack("<4L",PCREAD, baddr, blen, addr)
        print repr(priovec)
        self.writeCtl(priovec)
        return a.tostring()

    def platformWriteMemory(self, addr, bytes):
        a = array.array('c',bytes)
        baddr,blen = a.buffer_info()
        priovec = struct.pack("<LLLL", PCWRITE, baddr, blen, addr)
        self.writeCtl(priovec)

    def platformGetMaps(self):
        ret = []
        pid = self.getPid()
        mapdata = file("/proc/%d/map" % pid, "rb").read()
        while mapdata:
            addr,size = struct.unpack("<LL", mapdata[:8])
            perms, = struct.unpack("<L", mapdata[80:84])
            perms = perms & 0x7
            ret.append((addr,size, perms, ""))
            mapdata = mapdata[96:]
        return ret

