import vivisect.hal.memory as v_mem
import vivisect.debug.trace as v_trace

import vivisect.archs.i386.cpu as v_i386_cpu
import vivisect.archs.amd64.cpu as v_amd64_cpu

from vertex.lib.common import tufo
from vivisect.platforms.windows.winnt import *

badmem_perms = {
    0:v_mem.MM_READ,
    1:v_mem.MM_WRITE,
    8:v_mem.MM_EXEC,
}

class WinTrace(v_trace.Trace):

    def _initTraceLocals(self):
        self.on('target:win:exception', self._onWinException)

    def _onWinException(self, event):
        code = event[1].get('code')
        addr = event[1].get('addr')
        params = event[1].get('params')

        if code in (EXCEPTION_BREAKPOINT, STATUS_WX86_BREAKPOINT):

            if self.proc[1].get('firststop') == None:
                self.proc[1]['firststop'] = True
                self.fire('proc:ready')
                return

            # check for addr is at breakpoint!
            # check for watch points

        signorm = None
        exinfo = {'code':code,'addr':addr,'params':params}

        if code == EXCEPTION_ACCESS_VIOLATION:
            memaddr = params[1]
            memperm = badmem_perms.get( params[0], 0 )
            signorm = tufo('badmem', addr=memaddr, perm=memperm)

        elif code == EXCEPTION_ILLEGAL_INSTRUCTION:
            signorm = tufo('badinst')

        self.fire('proc:signal', signo=code, signorm=signorm, exinfo=exinfo)

class I386WinTrace(WinTrace,v_i386_cpu.I386Cpu):

    def _initTraceMixins(self):
        v_i386_cpu.I386Cpu.__init__(self,threads=0)

class Amd64WinTrace(WinTrace,v_amd64_cpu.Amd64Cpu):

    def _initTraceMixins(self):
        v_amd64_cpu.Amd64Cpu.__init__(self,threads=0)
