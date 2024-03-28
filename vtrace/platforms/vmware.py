'''
Underlying platform implementation for kernel debugging
with vmware gdbserver.

Msv1_0SubAuthenticationRoutine

VMWare config options...
debugStub.listen.guest64 = "TRUE" # ends up on port 8864 (or next avail)


# 32 bit target.... ( defaults to port 8832 )
debugStub.listen.guest32 = "TRUE"
debugStub.listen.guest32.remote = "TRUE" # bind to 0.0.0.0 rather than 127.0.0.1
debugStub.hideBreakpoints = "TRUE" # Enable breakpoints

# 64 bit target.... ( defaults to port 8864 )
debugStub.listen.guest64 = "TRUE"
debugStub.listen.guest64.remote = "TRUE" # bind to 0.0.0.0 rather than 127.0.0.1
debugStub.hideBreakpoints = "TRUE" # Enable breakpoints

'''
import logging

import PE
import vtrace

import envi.bits as e_bits
import envi.symstore.resolver as e_resolv
import envi.symstore.symcache as e_symcache

import vtrace.archs.i386 as vt_i386
import vtrace.platforms.base as vt_base
import vtrace.platforms.win32 as vt_win32
import vtrace.platforms.winkern as vt_winkern
import vtrace.platforms.gdbstub as vt_gdbstub

logger = logging.getLogger(__name__)

class VMWareMixin(vt_gdbstub.GdbStubMixin):

    def __init__(self, host=None, port=None):
        vt_gdbstub.GdbStubMixin.__init__(self, host=host, port=port)
        self.bigmask = e_bits.u_maxes[ self.getPointerSize() ]

class VMWare32WindowsTrace(
            vtrace.Trace,
            VMWareMixin,
            vt_i386.i386Mixin,
            vt_base.TracerBase,
            ):

    def __init__(self, host=None, port=None):

        vtrace.Trace.__init__(self, archname='i386')
        vt_base.TracerBase.__init__(self)
        vt_i386.i386Mixin.__init__(self)
        VMWareMixin.__init__(self, host=host, port=port)

        self.setMeta('Format','pe')
        self.setMeta('Platform','winkern')

        self._break_after_bp = False  # we stop directly on the bp addr

    def _getVmwareReg(self, rname):
        '''
        Use VMWare's monitor extension to get a register we wouldn't
        normally have...
        '''
        #fs 0x30 base 0xffdff000 limit 0x00001fff type 0x3 s 1 dpl 0 p 1 db 1
        fsstr = self._monitorCommand('r %s' % rname)
        fsparts = fsstr.split()
        return int(fsparts[3], 16)

    def _gdbJustAttached(self):
        # Implement the callback from the GdbStubMixin parent...

        fsbase = self._getVmwareReg('fs')

        fs_fields = self.readMemoryFormat(fsbase, '<8I')
        # Windows has a self reference in the KPCR...
        if fs_fields[7] != fsbase:
            logger.warning(str([ hex(x) for x in fs_fields ]))
            raise Exception('poi(fsbase+(ptr*7)) != fsbase! ( not actually windows? )')

        vt_winkern.initWinkernTrace(self, fsbase)
        return

    def normFileName(self, libname):
        basename = libname.split('\\')[-1]
        return basename.split(".")[0].split("-")[0].lower()

    def platformParseBinary(self, filename, baseaddr, normname):
        try:
            pe = PE.peFromMemoryObject(self, baseaddr)
            vhash = e_symcache.symCacheHashFromPe(pe)

            symcache = self.symcache.getCacheSyms(vhash)
            if symcache is None:
                # Symbol type 0 for now...
                symcache = [(rva, 0, name, e_resolv.SYMSTOR_SYM_SYMBOL) for rva, ord, name in pe.getExports()]
                self.symcache.setCacheSyms(vhash, symcache)

            self.impSymCache(symcache, symfname=normname, baseaddr=baseaddr)

        except Exception as e:
            logger.error('Error Parsing Binary (%s): %s', normname, e)

    def buildNewTrace(self):
        return VMWare32WindowsTrace(host=self._gdb_host, port=self._gdb_port)

    # FIXME move these to gdbstub

    def isValidPointer(self, addr):
        # Fake this out by attempting to read... ( slow/lame )
        cmd = 'm%x,%x' % (addr, 1)
        pkt = self._cmdTransact(cmd)
        return not pkt.startswith('E')

    def archActivBreakpoint(self, addr):
        self._gdbAddMemBreak(addr, 1)

    def archClearBreakpoint(self, addr):
        self._gdbDelMemBreak(addr, 1)

