"""
Posix Signaling Module
"""
# Copyright (C) 2007 Invisigoth - See LICENSE file for details
import os
import sys
import struct
import signal
import logging


import vtrace
import vtrace.platforms.base as v_base

import Elf
from ctypes import *
import ctypes.util as cutil

import envi.cli as e_cli
import envi.symstore.resolver as e_resolv

logger = logging.getLogger(__name__)
libc = None

class PosixMixin:

    """
    A mixin for systems which use POSIX signals and
    things like wait()
    """

    def __init__(self):
        """
        Setup for the fact that we support signal driven
        debugging on posix platforms
        """
        self.stepping = False # Set this on stepi to diff the TRAP
        self.execing  = False # Set this on exec to diff the TRAP
        self.pthreads = [] # Some platforms make a pthread list

        self.fireTracerThread()

    def platformKill(self):
        self.sendSignal(signal.SIGKILL)

    def sendSignal(self, signo):
        self.requireAttached()
        os.kill(self.pid, signo)

    def platformSendBreak(self):
        self.sendSignal(signal.SIGTRAP)  # FIXME maybe change to SIGSTOP

    def platformWait(self):
        return os.waitpid(self.pid, 0)

    def handleAttach(self):
        self.fireNotifiers(vtrace.NOTIFY_ATTACH)
        self._findLibraryMaps(b'\x7fELF', always=True)
        self._simpleCreateThreads()
        # We'll emulate windows here and send an additional
        # break after our library load events to make things easy
        self.runAgain(False)  # Clear this, if they want BREAK to run, it will
        self.fireNotifiers(vtrace.NOTIFY_BREAK)

    def platformProcessEvent(self, event):
        pid, status = event
        if os.WIFEXITED(status):
            tid = self.getMeta("ThreadId", -1)
            exitcode = os.WEXITSTATUS(status)
            if tid != self.getPid():
                # Set the selected thread ID to the pid cause
                # the old one's invalid
                if tid in self.pthreads:
                    self.pthreads.remove(tid)
                self.setMeta("ThreadId", self.getPid())
                self._fireExitThread(tid, exitcode)

            else:
                self._fireExit(exitcode)

        elif os.WIFSIGNALED(status):
            self._fireExit(os.WTERMSIG(status))

        elif os.WIFSTOPPED(status):
            sig = os.WSTOPSIG(status)
            self.handlePosixSignal(sig)

        else:
            logger.error("Unhandled posix status code: %d", status)

    def handlePosixSignal(self, sig):
        """
        Handle a basic posix signal for this trace.  This was seperated from
        platformProcessEvent so extenders could skim events and still use this logic.
        """
        if sig == signal.SIGTRAP:

            # Traps on posix systems are a little complicated
            if self.stepping:
                # FIXME try out was single step thing for intel
                self.stepping = False
                self._fireStep()

            elif self.checkWatchpoints():
                return

            elif self.checkBreakpoints():
                # It was either a known BP or a sendBreak()
                return

            elif self.execing:
                self.execing = False
                self.handleAttach()

            else:
                self._fireSignal(sig)

        elif sig == signal.SIGSTOP:
            # FIXME only on attaching..
            self.handleAttach()

        else:
            self._fireSignal(sig)


class ElfMixin:
    """
    A platform mixin to parse Elf binaries
    """
    def __init__(self):
        self.setMeta('Format', 'elf')

    def platformParseBinary(self, filename, baseaddr, normname):
        typemap = {
            Elf.STT_FUNC: e_resolv.FunctionSymbol,
            Elf.STT_SECTION: e_resolv.SectionSymbol,
        }

        try:
            fd = self.platformOpenFile(filename)
            elf = Elf.Elf(fd)
        except IOError:
            try:
                # it's possible we hit vdso or something similar
                elf = Elf.elfFromMemoryObject(self, baseaddr)
            except:
                raise
        # elf = Elf.Elf(fd)
        addbase = 0
        if not elf.isPreLinked() and elf.isSharedObject():
            addbase = baseaddr

        for sec in elf.sections:
            sym = e_resolv.SectionSymbol(sec.name, sec.sh_addr+addbase, sec.sh_size, normname)
            self.addSymbol(sym)

        for sym in elf.symbols:
            symclass = typemap.get((sym.st_info & 0xf), e_resolv.Symbol)
            sym = symclass(sym.name, sym.st_value+addbase, sym.st_size, normname)
            self.addSymbol(sym)

        for sym in elf.dynamic_symbols:
            symclass = typemap.get((sym.st_info & 0xf), e_resolv.Symbol)
            sym = symclass(sym.name, sym.st_value+addbase, sym.st_size, normname)
            self.addSymbol(sym)

        if elf.isExecutable():
            sym = e_resolv.Symbol('__entry', elf.e_entry, 0, normname)
            self.addSymbol(sym)

# As much as I would *love* if all the ptrace defines were the same all the time,
# there seem to be small platform differences...
# These are the ones upon which most agree
PT_TRACE_ME     = 0   # child declares it's being traced */
PT_READ_I       = 1   # read word in child's I space */
PT_READ_D       = 2   # read word in child's D space */
PT_READ_U       = 3   # read word in child's user structure */
PT_WRITE_I      = 4   # write word in child's I space */
PT_WRITE_D      = 5   # write word in child's D space */
PT_WRITE_U      = 6   # write word in child's user structure */
PT_CONTINUE     = 7   # continue the child */
PT_KILL         = 8   # kill the child process */
PT_STEP         = 9   # single step the child */

def ptrace(code, pid, addr, data):
    """
    The contents of this call are basically cleanly
    passed to the libc implementation of ptrace.
    """
    global libc
    if not libc:
        if os.getenv('ANDROID_ROOT'):
            cloc = '/system/lib/libc.so'

        else:
            cloc = cutil.find_library("c")
            if not cloc:
                raise Exception("ERROR: can't find C library on posix system!")

        libc = CDLL(cloc)
        libc.ptrace.restype = c_size_t
        libc.ptrace.argtypes = [c_int, c_uint32, c_size_t, c_size_t]
    return libc.ptrace(code, pid, c_size_t(addr), c_size_t(data))

class PtraceMixin:
    """
    A platform mixin for using the ptrace functions
    to attach/detach/continue/stepi etc. Many *nix systems
    will probably use this...

    NOTE: if you get a PT_FOO undefined, it *probably* means that
    the PT_FOO macro isn't defined for that platform (which means
    it need to be done another way like PT_GETREGS on darwin doesn't
    exist... but the darwin mixin over-rides platformGetRegs)
    """

    def __init__(self):
        """
        Setup supported modes
        """

        self.conthack = 0
        if sys.platform == "darwin":
            self.conthack = 1

        self.fireTracerThread()

    @v_base.threadwrap
    def platformExec(self, cmdline):
        self.execing = True
        cmdlist = e_cli.splitargs(cmdline)
        os.stat(cmdlist[0])
        pid = os.fork()
        if pid == 0:
            ptrace(PT_TRACE_ME, 0, 0, 0)
            os.execv(cmdlist[0], cmdlist)
            sys.exit(-1)
        return pid

    @v_base.threadwrap
    def platformWriteMemory(self, address, bytes):
        wordsize = len(struct.pack("P",0))
        remainder = len(bytes) % wordsize

        if remainder:
            pad = self.readMemory(address+(len(bytes)-remainder), wordsize)
            bytes += pad[remainder:]

        for i in range(int(len(bytes)/wordsize)):
            offset = wordsize * i
            dword = struct.unpack("L",bytes[offset:offset+wordsize])[0]
            if ptrace(PT_WRITE_D, self.pid, int(address+offset), int(dword)) != 0:
                raise Exception("ERROR ptrace PT_WRITE_D failed!")
