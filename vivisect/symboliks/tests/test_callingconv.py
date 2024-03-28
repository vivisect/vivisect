import unittest

import vivisect
import vivisect.symboliks.archs.amd64 as sym_amd64

from vstruct.primitives import *
from vivisect.symboliks.common import *


class CallingConvTest(unittest.TestCase):
    def test_getSymbolikArgs(self):
        '''
        tests generating the symbolic definitions from the envi calling
        conventions.
        '''
        cc = sym_amd64.MSx64CallSym()

        argc = 5
        sargs = cc.getSymbolikArgs(None, 'a'*argc, update=False)
        assert(len(sargs) == argc)

        argc = 15
        sargs = cc.getSymbolikArgs(None, 'b'*argc, update=False)
        assert(len(sargs) == argc)

    def NEWPtest_setSymbolikArgs(self):
        '''
        tests setting and then getting the args for a function.  we manually
        smash in the function args for now *and* hardcode the test to a func
        in 64-bit pre-run win32k.sys.viv workspace.
        '''
        vw = vivisect.VivWorkspace()
        vw.loadWorkspace('win32k.sys.viv')
        fva = 0xfffff97fff1706a0
        args = [(v_uint64, None), ] * 6
        vw.setFunctionArgs(fva, args)

        ctx = sym_amd64.Amd64SymbolikAnalysisContext(vw)
        emu = ctx.getFunctionEmulator(fva)
        cc = sym_amd64.MSx64CallSym()

        argc = len(args)
        argv = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06]
        cc.setSymbolikArgs(emu, argv)
        sargs = cc.getSymbolikArgs(emu, argv, update=False)
        for idx, arg in enumerate(sargs):

            val = arg.update(emu)
            if isinstance(arg, Mem):
                val = emu.readSymMemory(arg, 8)
                arg = arg.update(emu)
                arg = arg.reduce(emu)

        assert(len(sargs) == argc)
