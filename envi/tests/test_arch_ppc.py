import sys
import unittest
import vivisect
import envi.archs.ppc
import envi.exc as e_exc
import envi.archs.ppc.vle as eapvd
import vivisect.symboliks.analysis as vs_anal

import logging
from binascii import unhexlify
from envi.archs.ppc.regs import *
from envi.archs.ppc.const import *

logger = logging.getLogger(__name__)

MARGIN_OF_ERROR = 200

def getVivEnv(arch='ppc'):
    vw = vivisect.VivWorkspace()
    vw.setMeta("Architecture", arch)
    vw.addMemoryMap(0, 7, 'firmware', '\xff' * 16384)
    vw.addMemoryMap(0xbfbff000, 7, 'firmware', '\xfe' * 0x1000)

    emu = vw.getEmulator()
    emu.setMeta('forrealz', True)
    emu.logread = emu.logwrite = True

    sctx = vs_anal.getSymbolikAnalysisContext(vw)
    return vw, emu, sctx

class PpcInstructionSet(unittest.TestCase):
    def validateEmulation(self, emu, opbytes, setters, tests, tidx=0):
        '''
        Run emulation tests.  On successful test, returns True
        '''
        # first set any environment stuff necessary
        ## defaults
        emu.setRegister(3, 0x414141)
        emu.setRegister(4, 0x444444)
        emu.setRegister(5, 0x10)
        emu.setRegister(6, 0x464646)
        emu.setRegister(7, 0x474747)
        emu.setStackCounter(0x450000)

        # setup flags and registers
        #settersrepr = '( %r )' % (', '.join(["%s=%s" % (s, hex(v)) for s,v in setters]))
        testsrepr = '( %r )' % (', '.join(["%s==%s" % (s, hex(v)) for s,v in tests]))

        va = 0x40004560
        for tgt, val in setters:
            try:
                # try register first
                emu.setRegisterByName(tgt, val)
                if tgt == 'PC':
                    va = val

            except e_exc.InvalidRegisterName:
                # it's not a register
                if type(tgt) == str and tgt.startswith("PSR_"):
                    # it's a flag
                    emu.setFlag(eval(tgt), val)

                #elif type(tgt) in (long, int): Keeping this line incase I break things
                elif isinstance(tgt, int):
                    # it's an address
                    #emu.writeMemValue(tgt, val, 1) # limited to 1-byte writes currently.  Commenting this out so I don't mess up what was there already.
                    emu.writeMemory(tgt, val)

                else:
                    op = emu.archParseOpcode(unhexlify(opbytes), 0, va=va)
                    raise Exception( "Funkt up Setting: (%r: %r test#%d)  %s = 0x%x" % (opbytes, op, tidx, tgt, val) )

        op = emu.archParseOpcode(unhexlify(opbytes), 0, va=va)
        print("0x%x:  %r" % (op.va, op))

        emu.executeOpcode(op)

        if not len(tests):
            success = True
        else:
            # start out as failing...
            success = False

        for tgt, val in tests:
            try:
                # try register first
                testval = emu.getRegisterByName(tgt)
                if testval == val:
                    success = True
                else:  # should be an else
                    raise Exception("FAILED(reg): (%r test#%d)  %s  !=  0x%x (observed: 0x%x) \n\t(setters: %r)\n\t(test: %r)" % (op, tidx, tgt, val, testval, settersrepr, testsrepr))

            except e_exc.InvalidRegisterName:
                # it's not a register
                if type(tgt) == str and tgt.startswith("PSR_"):
                    # it's a flag
                    testval = emu.getFlag(eval(tgt))
                    if testval == val:
                        success = True
                    else:
                        raise Exception("FAILED(flag): (%r test#%d)  %s  !=  0x%x (observed: 0x%x) \n\t(setters: %r)\n\t(test: %r)" % (op, tidx, tgt, val, testval, settersrepr, testsrepr))

                elif type(tgt) in (long, int):
                    # it's an address
                    testval = emu.readMemValue(tgt, 1)
                    if testval == val:
                        success = True
                    raise Exception("FAILED(mem): (%r test#%d)  0x%x  !=  0x%x (observed: 0x%x) \n\t(setters: %r)\n\t(test: %r)" % (op, tidx, tgt, val, testval, settersrepr, testsrepr))

                else:
                    raise Exception( "Funkt up test (%r test#%d) : %s == %s" % (op, tidx, tgt, val) )

        return success

    def do_emutsts(self, emu, opbytes, emutests):
        '''
        Setup and Perform Emulation Tests per architecture variant
        '''
        bademu = 0
        goodemu = 0
        # if we have a special test lets run it
        for tidx, sCase in enumerate(emutests):
            #allows us to just have a result to check if no setup needed
            if 'tests' in sCase:
                setters = ()
                if 'setup' in sCase:
                    setters = sCase['setup']

                tests = sCase['tests']
                if self.validateEmulation(emu, opbytes, (setters), (tests), tidx):
                    goodemu += 1
                else:
                    bademu += 1
                    op = emu.archParseOpcode(unhexlify(opbytes), 0, va=0x40004560)
                    raise Exception( "FAILED emulation (special case): %.8x %s - %s" % (op.va, opbytes, op) )

            else:
                bademu += 1
                op = emu.archParseOpcode(unhexlify(opbytes), 0, va=0x40004560)
                raise Exception( "FAILED special case test format bad:  Instruction test does not have a 'tests' field: %.8x %s - %s" % (op.va, opbytes, op))

        return goodemu, bademu

    def test_envi_ppcvle_disasm(self):
        from . import ppc_vle_instructions
        self.do_envi_disasm('vle', ppc_vle_instructions)

    def test_envi_ppc_server_disasm(self):
        from . import ppc_server_instructions
        self.do_envi_disasm('ppc-server', ppc_server_instructions)

    def test_envi_ppcvle_emu(self):
        from . import ppc_vle_emutests
        self.do_envi_emu('vle', ppc_vle_emutests)

    def test_envi_ppc_server_emu(self):
        from . import ppc_server_emutests
        self.do_envi_emu('ppc-server', ppc_server_emutests)

    def do_envi_disasm(self, archname, test_module):
        bademu = 0
        goodemu = 0
        test_pass = 0

        vw, emu, sctx = getVivEnv(archname)

        for test_bytes, result_instr in test_module.instructions:
            try:
                # test decoding of the instructions
                op = vw.arch.archParseOpcode(unhexlify(test_bytes), 0, va=0x40004560)
                op_str = repr(op).strip()
                if op_str == result_instr:
                    test_pass += 1
                if result_instr != op_str:
                    logging.error('{}: ours: {} != {}'.format(test_bytes, repr(op_str), repr(result_instr)))

            except Exception as  e:
                logging.exception('ERROR: {}: {}'.format(test_bytes, result_instr))

        logger.info("%s: %d of %d successes", archname, test_pass, len(test_module.instructions))
        self.assertAlmostEqual(test_pass, len(test_module.instructions), delta=MARGIN_OF_ERROR)

    def do_envi_emu(self, archname, emu_module):
        bademu = 0
        goodemu = 0
        test_pass = 0

        vw, emu, sctx = getVivEnv(archname)

        print()
        for test_bytes, emutests in emu_module.emutests.items():
            try:
                # do emulator tests for this byte combination
                if emutests is not None:
                    ngoodemu, nbademu = self.do_emutsts(emu, test_bytes, emutests)
                    goodemu += ngoodemu
                    bademu += nbademu

            except Exception as  e:

                logging.exception('ERROR: {}:'.format(test_bytes,))

        logger.info("%s: Total of %d tests completed.", archname, (goodemu + bademu))
        self.assertEqual(goodemu, emu_module.GOOD_EMU_TESTS)

    def test_MASK_and_ROTL(self):
        import envi.archs.ppc.emu as eape
        import vivisect.symboliks.archs.ppc as vsap

        for x in range(64):
            for y in range(64):
                #mask =
                emumask = eape.MASK(x, y)

                symmask = vsap.MASK(vsap.Const(x, 8), vsap.Const(y, 8))
                #print(hex(emumask), repr(symmask), symmask)


                self.assertEqual(emumask, symmask.solve(), 'MASK({}, {}): {} != {}'.format(x, y, emumask, symmask.solve()))

        for y in range(32):
            emurot32 = eape.ROTL32(0x31337040, y)
            symrot32 = vsap.ROTL32(vsap.Const(0x31337040, 8), vsap.Const(y, 8))
            self.assertEqual(emurot32, symrot32.solve(), 'ROTL32(0x31337040, {}): {} != {}   {}'.format(y, hex(emurot32), hex(symrot32.solve()), symrot32))

        for y in range(64):
            emurot64 = eape.ROTL64(0x31337040, y)
            symrot64 = vsap.ROTL64(vsap.Const(0x31337040, 8), vsap.Const(y, 8))
            self.assertEqual(emurot64, symrot64.solve(), 'ROTL64(0x31337040, {}): {} != {}   {}'.format(y, hex(emurot64), hex(symrot64.solve()), symrot64))

    def test_CR_and_XER(self):
        vw, emu, sctx = getVivEnv(arch='ppc-server')

        # now compare the register and bitmap stuff to be the same
        emu.setRegister(REG_CR0, 0)
        emu.setRegister(REG_CR0_LT, 1)
        cr = emu.getRegister(REG_CR)
        self.assertEqual(("CR: ", hex(cr)), ("CR: ", hex(0x80000000)))
        cr0 = emu.getRegister(REG_CR0)
        self.assertEqual(("CR0: ", hex(cr0)), ("CR0: ", hex(8)))
        self.assertEqual((cr0) , FLAGS_LT)

        emu.setRegister(REG_CR0, 0)
        emu.setRegister(REG_CR0_GT, 1)
        cr = emu.getRegister(REG_CR)
        self.assertEqual(("CR: ", hex(cr)), ("CR: ", hex(0x40000000)))
        cr0 = emu.getRegister(REG_CR0)
        self.assertEqual(("CR0: ", hex(cr0)), ("CR0: ", hex(4)))
        self.assertEqual((cr0) , FLAGS_GT)

        emu.setRegister(REG_CR0, 0)
        emu.setRegister(REG_CR0_EQ, 1)
        cr = emu.getRegister(REG_CR)
        self.assertEqual(("CR: ", hex(cr)), ("CR: ", hex(0x20000000)))
        cr0 = emu.getRegister(REG_CR0)
        self.assertEqual(("CR0: ", hex(cr0)), ("CR0: ", hex(2)))
        self.assertEqual((cr0) , FLAGS_EQ)

        emu.setRegister(REG_CR0, 0)
        emu.setRegister(REG_CR0_SO, 1)
        cr = emu.getRegister(REG_CR)
        self.assertEqual(("CR: ", hex(cr)), ("CR: ", hex(0x10000000)))
        cr0 = emu.getRegister(REG_CR0)
        self.assertEqual(("CR0: ", hex(cr0)), ("CR0: ", hex(1)))
        self.assertEqual((cr0) , FLAGS_SO)

        emu.setRegister(REG_CR0, 0)
        emu.setRegister(REG_XER, 0)
        emu.setRegister(REG_CA, 1)
        xer = emu.getRegister(REG_XER)
        self.assertEqual(xer , XERFLAGS_CA)
        self.assertEqual(xer>>XERFLAGS_shift, FLAGS_XER_CA)

        emu.setRegister(REG_CR0, 0)
        emu.setRegister(REG_XER, 0)
        emu.setRegister(REG_OV, 1)
        xer = emu.getRegister(REG_XER)
        self.assertEqual(xer , XERFLAGS_OV)
        self.assertEqual(xer>>XERFLAGS_shift, FLAGS_XER_OV)

        emu.setRegister(REG_CR0, 0)
        emu.setRegister(REG_XER, 0)
        emu.setRegister(REG_SO, 1)
        xer = emu.getRegister(REG_XER)
        self.assertEqual(xer , XERFLAGS_SO)
        self.assertEqual(xer>>XERFLAGS_shift, FLAGS_XER_SO)



    def test_emu_CR_and_XER(self):
        addco_tests = (
            {'cmd': 'addco.', 'inr1': 0x1, 'inr2': 0x2, 'inr3': 0x0, 'incr': 0x0, 'inxer': 0x0,     'expr3': 0x3,   'expcr': 0x40000000,    'expxer': 0x0,},
            {'cmd': 'addco.', 'inr1': 0x3fffffffffffffff, 'inr2': 0x3fffffffffffffff, 'inr3': 0x0, 'incr': 0x0, 'inxer': 0x0,       'expr3': 0x7ffffffffffffffe,    'expcr': 0x40000000,    'expxer': 0x0,},
            {'cmd': 'addco.', 'inr1': 0x4000000000000000, 'inr2': 0x4000000000000000, 'inr3': 0x0, 'incr': 0x0, 'inxer': 0xc0000000,        'expr3': 0x8000000000000000,    'expcr': 0x90000000,    'expxer': 0xc0000000,},
            {'cmd': 'addco.', 'inr1': 0x4000000000000000, 'inr2': 0x4000000000000000, 'inr3': 0x0, 'incr': 0x0, 'inxer': 0xc0000000,        'expr3': 0x8000000000000000,    'expcr': 0x90000000,    'expxer': 0xc0000000,},
            {'cmd': 'addco.', 'inr1': 0x7fffffffffffffff, 'inr2': 0x7fffffffffffffff, 'inr3': 0x0, 'incr': 0x0, 'inxer': 0xc0000000,        'expr3': 0xfffffffffffffffe,    'expcr': 0x90000000,    'expxer': 0xc0000000,},
            {'cmd': 'addco.', 'inr1': 0x8000000000000000, 'inr2': 0x8000000000000000, 'inr3': 0x0, 'incr': 0x0, 'inxer': 0xc0000000,        'expr3': 0x0,   'expcr': 0x30000000,    'expxer': 0xe0000000,},
            {'cmd': 'addco.', 'inr1': 0xffffffffffffffff, 'inr2': 0xffffffffffffffff, 'inr3': 0x0, 'incr': 0x0, 'inxer': 0xa0000000,        'expr3': 0xfffffffffffffffe,    'expcr': 0x90000000,    'expxer': 0xa0000000,},
            {'cmd': 'addco.', 'inr1': 0x1, 'inr2': 0x2, 'inr3': 0x0, 'incr': 0x0, 'inxer': 0xa0000000,      'expr3': 0x3,   'expcr': 0x50000000,    'expxer': 0x80000000,},
            {'cmd': 'addco.', 'inr1': 0x8000000000000000, 'inr2': 0x7fffffffffffffff, 'inr3': 0x0, 'incr': 0x0, 'inxer': 0x0,       'expr3': 0xffffffffffffffff,    'expcr': 0x80000000,    'expxer': 0x0,},
            {'cmd': 'addco.', 'inr1': 0x8000000000000000, 'inr2': 0x7fffffffffffffff, 'inr3': 0x0, 'incr': 0x0, 'inxer': 0x0,       'expr3': 0xffffffffffffffff,    'expcr': 0x80000000,    'expxer': 0x0,},
            {'cmd': 'addco.', 'inr1': 0x8000000000000000, 'inr2': 0x8000000000000000, 'inr3': 0x0, 'incr': 0x0, 'inxer': 0x0,       'expr3': 0x0,   'expcr': 0x30000000,    'expxer': 0xe0000000,},
            {'cmd': 'addco.', 'inr1': 0x7fffffffffffffff, 'inr2': 0x8000000000000000, 'inr3': 0x0, 'incr': 0x0, 'inxer': 0x0,       'expr3': 0xffffffffffffffff,    'expcr': 0x80000000,    'expxer': 0x0,},
            {'cmd': 'addco.', 'inr1': 0xcfffffffffffffff, 'inr2': 0x8000000000000000, 'inr3': 0x0, 'incr': 0x0, 'inxer': 0x0,       'expr3': 0x4fffffffffffffff,    'expcr': 0x50000000,    'expxer': 0xe0000000,},
        )

        cmpd_tests = (
            {'cmd': 'cmpd.', 'inr0': 0x1, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1, 'inr1': 0x4, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1, 'inr1': 0x8, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1, 'inr1': 0x10, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1, 'inr1': 0x20, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1, 'inr1': 0x40, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1, 'inr1': 0x80, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1, 'inr1': 0x100, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1, 'inr1': 0x200, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1, 'inr1': 0x400, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1, 'inr1': 0x800, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1, 'inr1': 0x1000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1, 'inr1': 0x2000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1, 'inr1': 0xffffffff00080000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1, 'inr1': 0xffffffff00100000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1, 'inr1': 0xffffffff00200000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1, 'inr1': 0xffffffff00400000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1, 'inr1': 0xffffffff00800000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1, 'inr1': 0xffffffff01000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1, 'inr1': 0xffffffff02000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1, 'inr1': 0xffffffff04000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1, 'inr1': 0xffffffff08000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1, 'inr1': 0xffffffff10000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1, 'inr1': 0xffffffff20000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2, 'inr1': 0x4, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2, 'inr1': 0x8, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2, 'inr1': 0x10, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2, 'inr1': 0x20, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2, 'inr1': 0x40, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2, 'inr1': 0x80, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2, 'inr1': 0x100, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2, 'inr1': 0x200, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2, 'inr1': 0x400, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2, 'inr1': 0x800, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2, 'inr1': 0x1000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2, 'inr1': 0x2000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2, 'inr1': 0xffffffff00080000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2, 'inr1': 0xffffffff00100000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2, 'inr1': 0xffffffff00200000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2, 'inr1': 0xffffffff00400000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2, 'inr1': 0xffffffff00800000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2, 'inr1': 0xffffffff01000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2, 'inr1': 0xffffffff02000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2, 'inr1': 0xffffffff04000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2, 'inr1': 0xffffffff08000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2, 'inr1': 0xffffffff10000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2, 'inr1': 0xffffffff20000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4, 'inr1': 0x4, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4, 'inr1': 0x8, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4, 'inr1': 0x10, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4, 'inr1': 0x20, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4, 'inr1': 0x40, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4, 'inr1': 0x80, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4, 'inr1': 0x100, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4, 'inr1': 0x200, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4, 'inr1': 0x400, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4, 'inr1': 0x800, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4, 'inr1': 0x1000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4, 'inr1': 0x2000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4, 'inr1': 0xffffffff00080000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4, 'inr1': 0xffffffff00100000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4, 'inr1': 0xffffffff00200000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4, 'inr1': 0xffffffff00400000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4, 'inr1': 0xffffffff00800000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4, 'inr1': 0xffffffff01000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4, 'inr1': 0xffffffff02000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4, 'inr1': 0xffffffff04000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4, 'inr1': 0xffffffff08000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4, 'inr1': 0xffffffff10000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4, 'inr1': 0xffffffff20000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8, 'inr1': 0x4, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8, 'inr1': 0x8, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8, 'inr1': 0x10, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8, 'inr1': 0x20, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8, 'inr1': 0x40, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8, 'inr1': 0x80, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8, 'inr1': 0x100, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8, 'inr1': 0x200, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8, 'inr1': 0x400, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8, 'inr1': 0x800, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8, 'inr1': 0x1000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8, 'inr1': 0x2000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8, 'inr1': 0xffffffff00080000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8, 'inr1': 0xffffffff00100000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8, 'inr1': 0xffffffff00200000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8, 'inr1': 0xffffffff00400000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8, 'inr1': 0xffffffff00800000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8, 'inr1': 0xffffffff01000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8, 'inr1': 0xffffffff02000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8, 'inr1': 0xffffffff04000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8, 'inr1': 0xffffffff08000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8, 'inr1': 0xffffffff10000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8, 'inr1': 0xffffffff20000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x10, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x10, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x10, 'inr1': 0x4, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x10, 'inr1': 0x8, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x10, 'inr1': 0x10, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x10, 'inr1': 0x20, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x10, 'inr1': 0x40, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x10, 'inr1': 0x80, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x10, 'inr1': 0x100, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x10, 'inr1': 0x200, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x10, 'inr1': 0x400, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x10, 'inr1': 0x800, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x10, 'inr1': 0x1000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x10, 'inr1': 0x2000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x10, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x10, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x10, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x10, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x10, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x10, 'inr1': 0xffffffff00080000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x10, 'inr1': 0xffffffff00100000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x10, 'inr1': 0xffffffff00200000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x10, 'inr1': 0xffffffff00400000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x10, 'inr1': 0xffffffff00800000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x10, 'inr1': 0xffffffff01000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x10, 'inr1': 0xffffffff02000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x10, 'inr1': 0xffffffff04000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x10, 'inr1': 0xffffffff08000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x10, 'inr1': 0xffffffff10000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x10, 'inr1': 0xffffffff20000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x10, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x10, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x20, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x20, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x20, 'inr1': 0x4, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x20, 'inr1': 0x8, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x20, 'inr1': 0x10, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x20, 'inr1': 0x20, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x20, 'inr1': 0x40, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x20, 'inr1': 0x80, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x20, 'inr1': 0x100, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x20, 'inr1': 0x200, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x20, 'inr1': 0x400, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x20, 'inr1': 0x800, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x20, 'inr1': 0x1000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x20, 'inr1': 0x2000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x20, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x20, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x20, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x20, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x20, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x20, 'inr1': 0xffffffff00080000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x20, 'inr1': 0xffffffff00100000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x20, 'inr1': 0xffffffff00200000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x20, 'inr1': 0xffffffff00400000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x20, 'inr1': 0xffffffff00800000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x20, 'inr1': 0xffffffff01000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x20, 'inr1': 0xffffffff02000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x20, 'inr1': 0xffffffff04000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x20, 'inr1': 0xffffffff08000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x20, 'inr1': 0xffffffff10000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x20, 'inr1': 0xffffffff20000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x20, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x20, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x40, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x40, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x40, 'inr1': 0x4, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x40, 'inr1': 0x8, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x40, 'inr1': 0x10, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x40, 'inr1': 0x20, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x40, 'inr1': 0x40, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x40, 'inr1': 0x80, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x40, 'inr1': 0x100, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x40, 'inr1': 0x200, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x40, 'inr1': 0x400, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x40, 'inr1': 0x800, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x40, 'inr1': 0x1000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x40, 'inr1': 0x2000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x40, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x40, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x40, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x40, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x40, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x40, 'inr1': 0xffffffff00080000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x40, 'inr1': 0xffffffff00100000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x40, 'inr1': 0xffffffff00200000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x40, 'inr1': 0xffffffff00400000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x40, 'inr1': 0xffffffff00800000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x40, 'inr1': 0xffffffff01000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x40, 'inr1': 0xffffffff02000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x40, 'inr1': 0xffffffff04000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x40, 'inr1': 0xffffffff08000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x40, 'inr1': 0xffffffff10000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x40, 'inr1': 0xffffffff20000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x40, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x40, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x80, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x80, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x80, 'inr1': 0x4, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x80, 'inr1': 0x8, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x80, 'inr1': 0x10, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x80, 'inr1': 0x20, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x80, 'inr1': 0x40, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x80, 'inr1': 0x80, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x80, 'inr1': 0x100, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x80, 'inr1': 0x200, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x80, 'inr1': 0x400, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x80, 'inr1': 0x800, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x80, 'inr1': 0x1000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x80, 'inr1': 0x2000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x80, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x80, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x80, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x80, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x80, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x80, 'inr1': 0xffffffff00080000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x80, 'inr1': 0xffffffff00100000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x80, 'inr1': 0xffffffff00200000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x80, 'inr1': 0xffffffff00400000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x80, 'inr1': 0xffffffff00800000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x80, 'inr1': 0xffffffff01000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x80, 'inr1': 0xffffffff02000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x80, 'inr1': 0xffffffff04000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x80, 'inr1': 0xffffffff08000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x80, 'inr1': 0xffffffff10000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x80, 'inr1': 0xffffffff20000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x80, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x80, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x100, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x100, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x100, 'inr1': 0x4, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x100, 'inr1': 0x8, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x100, 'inr1': 0x10, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x100, 'inr1': 0x20, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x100, 'inr1': 0x40, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x100, 'inr1': 0x80, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x100, 'inr1': 0x100, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x100, 'inr1': 0x200, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x100, 'inr1': 0x400, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x100, 'inr1': 0x800, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x100, 'inr1': 0x1000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,      'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x100, 'inr1': 0x2000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,      'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x100, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,      'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x100, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,      'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x100, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x100, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x100, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x100, 'inr1': 0xffffffff00080000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x100, 'inr1': 0xffffffff00100000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x100, 'inr1': 0xffffffff00200000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x100, 'inr1': 0xffffffff00400000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x100, 'inr1': 0xffffffff00800000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x100, 'inr1': 0xffffffff01000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x100, 'inr1': 0xffffffff02000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x100, 'inr1': 0xffffffff04000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x100, 'inr1': 0xffffffff08000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x100, 'inr1': 0xffffffff10000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x100, 'inr1': 0xffffffff20000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x100, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x100, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x200, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x200, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x200, 'inr1': 0x4, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x200, 'inr1': 0x8, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x200, 'inr1': 0x10, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x200, 'inr1': 0x20, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x200, 'inr1': 0x40, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x200, 'inr1': 0x80, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x200, 'inr1': 0x100, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x200, 'inr1': 0x200, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x200, 'inr1': 0x400, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x200, 'inr1': 0x800, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x200, 'inr1': 0x1000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,      'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x200, 'inr1': 0x2000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,      'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x200, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,      'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x200, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,      'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x200, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x200, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x200, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x200, 'inr1': 0xffffffff00080000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x200, 'inr1': 0xffffffff00100000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x200, 'inr1': 0xffffffff00200000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x200, 'inr1': 0xffffffff00400000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x200, 'inr1': 0xffffffff00800000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x200, 'inr1': 0xffffffff01000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x200, 'inr1': 0xffffffff02000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x200, 'inr1': 0xffffffff04000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x200, 'inr1': 0xffffffff08000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x200, 'inr1': 0xffffffff10000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x200, 'inr1': 0xffffffff20000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x200, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x200, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x400, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x400, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x400, 'inr1': 0x4, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x400, 'inr1': 0x8, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x400, 'inr1': 0x10, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x400, 'inr1': 0x20, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x400, 'inr1': 0x40, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x400, 'inr1': 0x80, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x400, 'inr1': 0x100, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x400, 'inr1': 0x200, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x400, 'inr1': 0x400, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x400, 'inr1': 0x800, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x400, 'inr1': 0x1000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,      'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x400, 'inr1': 0x2000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,      'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x400, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,      'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x400, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,      'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x400, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x400, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x400, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x400, 'inr1': 0xffffffff00080000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x400, 'inr1': 0xffffffff00100000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x400, 'inr1': 0xffffffff00200000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x400, 'inr1': 0xffffffff00400000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x400, 'inr1': 0xffffffff00800000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x400, 'inr1': 0xffffffff01000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x400, 'inr1': 0xffffffff02000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x400, 'inr1': 0xffffffff04000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x400, 'inr1': 0xffffffff08000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x400, 'inr1': 0xffffffff10000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x400, 'inr1': 0xffffffff20000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x400, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x400, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x800, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x800, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x800, 'inr1': 0x4, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x800, 'inr1': 0x8, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x800, 'inr1': 0x10, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x800, 'inr1': 0x20, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x800, 'inr1': 0x40, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x800, 'inr1': 0x80, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x800, 'inr1': 0x100, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x800, 'inr1': 0x200, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x800, 'inr1': 0x400, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x800, 'inr1': 0x800, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x800, 'inr1': 0x1000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,      'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x800, 'inr1': 0x2000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,      'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x800, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,      'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x800, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,      'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x800, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x800, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x800, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x800, 'inr1': 0xffffffff00080000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x800, 'inr1': 0xffffffff00100000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x800, 'inr1': 0xffffffff00200000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x800, 'inr1': 0xffffffff00400000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x800, 'inr1': 0xffffffff00800000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x800, 'inr1': 0xffffffff01000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x800, 'inr1': 0xffffffff02000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x800, 'inr1': 0xffffffff04000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x800, 'inr1': 0xffffffff08000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x800, 'inr1': 0xffffffff10000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x800, 'inr1': 0xffffffff20000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x800, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x800, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1000, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1000, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1000, 'inr1': 0x4, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1000, 'inr1': 0x8, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1000, 'inr1': 0x10, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1000, 'inr1': 0x20, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1000, 'inr1': 0x40, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1000, 'inr1': 0x80, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1000, 'inr1': 0x100, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,      'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1000, 'inr1': 0x200, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,      'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1000, 'inr1': 0x400, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,      'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1000, 'inr1': 0x800, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,      'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1000, 'inr1': 0x1000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1000, 'inr1': 0x2000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1000, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1000, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1000, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1000, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1000, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1000, 'inr1': 0xffffffff00080000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1000, 'inr1': 0xffffffff00100000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1000, 'inr1': 0xffffffff00200000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1000, 'inr1': 0xffffffff00400000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1000, 'inr1': 0xffffffff00800000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1000, 'inr1': 0xffffffff01000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1000, 'inr1': 0xffffffff02000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1000, 'inr1': 0xffffffff04000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1000, 'inr1': 0xffffffff08000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1000, 'inr1': 0xffffffff10000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1000, 'inr1': 0xffffffff20000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1000, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x1000, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2000, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2000, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2000, 'inr1': 0x4, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2000, 'inr1': 0x8, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2000, 'inr1': 0x10, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2000, 'inr1': 0x20, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2000, 'inr1': 0x40, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2000, 'inr1': 0x80, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2000, 'inr1': 0x100, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,      'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2000, 'inr1': 0x200, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,      'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2000, 'inr1': 0x400, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,      'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2000, 'inr1': 0x800, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,      'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2000, 'inr1': 0x1000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2000, 'inr1': 0x2000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2000, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2000, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2000, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2000, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2000, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2000, 'inr1': 0xffffffff00080000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2000, 'inr1': 0xffffffff00100000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2000, 'inr1': 0xffffffff00200000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2000, 'inr1': 0xffffffff00400000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2000, 'inr1': 0xffffffff00800000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2000, 'inr1': 0xffffffff01000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2000, 'inr1': 0xffffffff02000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2000, 'inr1': 0xffffffff04000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2000, 'inr1': 0xffffffff08000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2000, 'inr1': 0xffffffff10000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2000, 'inr1': 0xffffffff20000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2000, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x2000, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4000, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4000, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4000, 'inr1': 0x4, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4000, 'inr1': 0x8, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4000, 'inr1': 0x10, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4000, 'inr1': 0x20, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4000, 'inr1': 0x40, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4000, 'inr1': 0x80, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4000, 'inr1': 0x100, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,      'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4000, 'inr1': 0x200, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,      'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4000, 'inr1': 0x400, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,      'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4000, 'inr1': 0x800, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,      'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4000, 'inr1': 0x1000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4000, 'inr1': 0x2000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4000, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4000, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4000, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4000, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4000, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4000, 'inr1': 0xffffffff00080000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4000, 'inr1': 0xffffffff00100000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4000, 'inr1': 0xffffffff00200000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4000, 'inr1': 0xffffffff00400000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4000, 'inr1': 0xffffffff00800000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4000, 'inr1': 0xffffffff01000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4000, 'inr1': 0xffffffff02000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4000, 'inr1': 0xffffffff04000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4000, 'inr1': 0xffffffff08000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4000, 'inr1': 0xffffffff10000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4000, 'inr1': 0xffffffff20000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4000, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x4000, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8000, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8000, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8000, 'inr1': 0x4, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8000, 'inr1': 0x8, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8000, 'inr1': 0x10, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8000, 'inr1': 0x20, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8000, 'inr1': 0x40, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8000, 'inr1': 0x80, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8000, 'inr1': 0x100, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,      'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8000, 'inr1': 0x200, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,      'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8000, 'inr1': 0x400, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,      'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8000, 'inr1': 0x800, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,      'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8000, 'inr1': 0x1000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8000, 'inr1': 0x2000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8000, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8000, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8000, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8000, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8000, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8000, 'inr1': 0xffffffff00080000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8000, 'inr1': 0xffffffff00100000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8000, 'inr1': 0xffffffff00200000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8000, 'inr1': 0xffffffff00400000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8000, 'inr1': 0xffffffff00800000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8000, 'inr1': 0xffffffff01000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8000, 'inr1': 0xffffffff02000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8000, 'inr1': 0xffffffff04000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8000, 'inr1': 0xffffffff08000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8000, 'inr1': 0xffffffff10000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8000, 'inr1': 0xffffffff20000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8000, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0x8000, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00010000, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00010000, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00010000, 'inr1': 0x4, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00010000, 'inr1': 0x8, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00010000, 'inr1': 0x10, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00010000, 'inr1': 0x20, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00010000, 'inr1': 0x40, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00010000, 'inr1': 0x80, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00010000, 'inr1': 0x100, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00010000, 'inr1': 0x200, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00010000, 'inr1': 0x400, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00010000, 'inr1': 0x800, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00010000, 'inr1': 0x1000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00010000, 'inr1': 0x2000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00010000, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00010000, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00010000, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00010000, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00010000, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00010000, 'inr1': 0xffffffff00080000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00010000, 'inr1': 0xffffffff00100000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00010000, 'inr1': 0xffffffff00200000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00010000, 'inr1': 0xffffffff00400000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00010000, 'inr1': 0xffffffff00800000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00010000, 'inr1': 0xffffffff01000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00010000, 'inr1': 0xffffffff02000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00010000, 'inr1': 0xffffffff04000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00010000, 'inr1': 0xffffffff08000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00010000, 'inr1': 0xffffffff10000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00010000, 'inr1': 0xffffffff20000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00010000, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00010000, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00020000, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00020000, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00020000, 'inr1': 0x4, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00020000, 'inr1': 0x8, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00020000, 'inr1': 0x10, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00020000, 'inr1': 0x20, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00020000, 'inr1': 0x40, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00020000, 'inr1': 0x80, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00020000, 'inr1': 0x100, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00020000, 'inr1': 0x200, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00020000, 'inr1': 0x400, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00020000, 'inr1': 0x800, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00020000, 'inr1': 0x1000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00020000, 'inr1': 0x2000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00020000, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00020000, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00020000, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00020000, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00020000, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00020000, 'inr1': 0xffffffff00080000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00020000, 'inr1': 0xffffffff00100000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00020000, 'inr1': 0xffffffff00200000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00020000, 'inr1': 0xffffffff00400000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00020000, 'inr1': 0xffffffff00800000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00020000, 'inr1': 0xffffffff01000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00020000, 'inr1': 0xffffffff02000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00020000, 'inr1': 0xffffffff04000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00020000, 'inr1': 0xffffffff08000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00020000, 'inr1': 0xffffffff10000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00020000, 'inr1': 0xffffffff20000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00020000, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00020000, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00040000, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00040000, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00040000, 'inr1': 0x4, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00040000, 'inr1': 0x8, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00040000, 'inr1': 0x10, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00040000, 'inr1': 0x20, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00040000, 'inr1': 0x40, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00040000, 'inr1': 0x80, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00040000, 'inr1': 0x100, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00040000, 'inr1': 0x200, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00040000, 'inr1': 0x400, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00040000, 'inr1': 0x800, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00040000, 'inr1': 0x1000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00040000, 'inr1': 0x2000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00040000, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00040000, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00040000, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00040000, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00040000, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00040000, 'inr1': 0xffffffff00080000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00040000, 'inr1': 0xffffffff00100000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00040000, 'inr1': 0xffffffff00200000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00040000, 'inr1': 0xffffffff00400000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00040000, 'inr1': 0xffffffff00800000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00040000, 'inr1': 0xffffffff01000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00040000, 'inr1': 0xffffffff02000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00040000, 'inr1': 0xffffffff04000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00040000, 'inr1': 0xffffffff08000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00040000, 'inr1': 0xffffffff10000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00040000, 'inr1': 0xffffffff20000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00040000, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00040000, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00080000, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00080000, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00080000, 'inr1': 0x4, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00080000, 'inr1': 0x8, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00080000, 'inr1': 0x10, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00080000, 'inr1': 0x20, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00080000, 'inr1': 0x40, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00080000, 'inr1': 0x80, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00080000, 'inr1': 0x100, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00080000, 'inr1': 0x200, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00080000, 'inr1': 0x400, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00080000, 'inr1': 0x800, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00080000, 'inr1': 0x1000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00080000, 'inr1': 0x2000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00080000, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00080000, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00080000, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00080000, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00080000, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00080000, 'inr1': 0xffffffff00080000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00080000, 'inr1': 0xffffffff00100000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00080000, 'inr1': 0xffffffff00200000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00080000, 'inr1': 0xffffffff00400000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00080000, 'inr1': 0xffffffff00800000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00080000, 'inr1': 0xffffffff01000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00080000, 'inr1': 0xffffffff02000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00080000, 'inr1': 0xffffffff04000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00080000, 'inr1': 0xffffffff08000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00080000, 'inr1': 0xffffffff10000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00080000, 'inr1': 0xffffffff20000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00080000, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00080000, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00100000, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00100000, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00100000, 'inr1': 0x4, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00100000, 'inr1': 0x8, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00100000, 'inr1': 0x10, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00100000, 'inr1': 0x20, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00100000, 'inr1': 0x40, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00100000, 'inr1': 0x80, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00100000, 'inr1': 0x100, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00100000, 'inr1': 0x200, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00100000, 'inr1': 0x400, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00100000, 'inr1': 0x800, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00100000, 'inr1': 0x1000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00100000, 'inr1': 0x2000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00100000, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00100000, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00100000, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00100000, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00100000, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00100000, 'inr1': 0xffffffff00080000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00100000, 'inr1': 0xffffffff00100000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00100000, 'inr1': 0xffffffff00200000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00100000, 'inr1': 0xffffffff00400000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00100000, 'inr1': 0xffffffff00800000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00100000, 'inr1': 0xffffffff01000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00100000, 'inr1': 0xffffffff02000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00100000, 'inr1': 0xffffffff04000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00100000, 'inr1': 0xffffffff08000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00100000, 'inr1': 0xffffffff10000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00100000, 'inr1': 0xffffffff20000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00100000, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00100000, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00200000, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00200000, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00200000, 'inr1': 0x4, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00200000, 'inr1': 0x8, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00200000, 'inr1': 0x10, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00200000, 'inr1': 0x20, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00200000, 'inr1': 0x40, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00200000, 'inr1': 0x80, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00200000, 'inr1': 0x100, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00200000, 'inr1': 0x200, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00200000, 'inr1': 0x400, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00200000, 'inr1': 0x800, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00200000, 'inr1': 0x1000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00200000, 'inr1': 0x2000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00200000, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00200000, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00200000, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00200000, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00200000, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00200000, 'inr1': 0xffffffff00080000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00200000, 'inr1': 0xffffffff00100000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00200000, 'inr1': 0xffffffff00200000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00200000, 'inr1': 0xffffffff00400000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00200000, 'inr1': 0xffffffff00800000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00200000, 'inr1': 0xffffffff01000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00200000, 'inr1': 0xffffffff02000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00200000, 'inr1': 0xffffffff04000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00200000, 'inr1': 0xffffffff08000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00200000, 'inr1': 0xffffffff10000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00200000, 'inr1': 0xffffffff20000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00200000, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00200000, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00400000, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00400000, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00400000, 'inr1': 0x4, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00400000, 'inr1': 0x8, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00400000, 'inr1': 0x10, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00400000, 'inr1': 0x20, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00400000, 'inr1': 0x40, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00400000, 'inr1': 0x80, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00400000, 'inr1': 0x100, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00400000, 'inr1': 0x200, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00400000, 'inr1': 0x400, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00400000, 'inr1': 0x800, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00400000, 'inr1': 0x1000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00400000, 'inr1': 0x2000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00400000, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00400000, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00400000, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00400000, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00400000, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00400000, 'inr1': 0xffffffff00080000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00400000, 'inr1': 0xffffffff00100000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00400000, 'inr1': 0xffffffff00200000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00400000, 'inr1': 0xffffffff00400000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00400000, 'inr1': 0xffffffff00800000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00400000, 'inr1': 0xffffffff01000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00400000, 'inr1': 0xffffffff02000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00400000, 'inr1': 0xffffffff04000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00400000, 'inr1': 0xffffffff08000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00400000, 'inr1': 0xffffffff10000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00400000, 'inr1': 0xffffffff20000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00400000, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00400000, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00800000, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00800000, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00800000, 'inr1': 0x4, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00800000, 'inr1': 0x8, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00800000, 'inr1': 0x10, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00800000, 'inr1': 0x20, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00800000, 'inr1': 0x40, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00800000, 'inr1': 0x80, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00800000, 'inr1': 0x100, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00800000, 'inr1': 0x200, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00800000, 'inr1': 0x400, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00800000, 'inr1': 0x800, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00800000, 'inr1': 0x1000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00800000, 'inr1': 0x2000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00800000, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00800000, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00800000, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00800000, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00800000, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00800000, 'inr1': 0xffffffff00080000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00800000, 'inr1': 0xffffffff00100000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00800000, 'inr1': 0xffffffff00200000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00800000, 'inr1': 0xffffffff00400000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00800000, 'inr1': 0xffffffff00800000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00800000, 'inr1': 0xffffffff01000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00800000, 'inr1': 0xffffffff02000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00800000, 'inr1': 0xffffffff04000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00800000, 'inr1': 0xffffffff08000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00800000, 'inr1': 0xffffffff10000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00800000, 'inr1': 0xffffffff20000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00800000, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff00800000, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff01000000, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff01000000, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff01000000, 'inr1': 0x4, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff01000000, 'inr1': 0x8, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff01000000, 'inr1': 0x10, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff01000000, 'inr1': 0x20, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff01000000, 'inr1': 0x40, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff01000000, 'inr1': 0x80, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff01000000, 'inr1': 0x100, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff01000000, 'inr1': 0x200, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff01000000, 'inr1': 0x400, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff01000000, 'inr1': 0x800, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff01000000, 'inr1': 0x1000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff01000000, 'inr1': 0x2000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff01000000, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff01000000, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff01000000, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff01000000, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff01000000, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff01000000, 'inr1': 0xffffffff00080000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff01000000, 'inr1': 0xffffffff00100000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff01000000, 'inr1': 0xffffffff00200000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff01000000, 'inr1': 0xffffffff00400000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff01000000, 'inr1': 0xffffffff00800000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff01000000, 'inr1': 0xffffffff01000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff01000000, 'inr1': 0xffffffff02000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff01000000, 'inr1': 0xffffffff04000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff01000000, 'inr1': 0xffffffff08000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff01000000, 'inr1': 0xffffffff10000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff01000000, 'inr1': 0xffffffff20000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff01000000, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff01000000, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff02000000, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff02000000, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff02000000, 'inr1': 0x4, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff02000000, 'inr1': 0x8, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff02000000, 'inr1': 0x10, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff02000000, 'inr1': 0x20, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff02000000, 'inr1': 0x40, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff02000000, 'inr1': 0x80, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff02000000, 'inr1': 0x100, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff02000000, 'inr1': 0x200, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff02000000, 'inr1': 0x400, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff02000000, 'inr1': 0x800, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff02000000, 'inr1': 0x1000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff02000000, 'inr1': 0x2000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff02000000, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff02000000, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff02000000, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff02000000, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff02000000, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff02000000, 'inr1': 0xffffffff00080000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff02000000, 'inr1': 0xffffffff00100000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff02000000, 'inr1': 0xffffffff00200000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff02000000, 'inr1': 0xffffffff00400000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff02000000, 'inr1': 0xffffffff00800000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff02000000, 'inr1': 0xffffffff01000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff02000000, 'inr1': 0xffffffff02000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff02000000, 'inr1': 0xffffffff04000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff02000000, 'inr1': 0xffffffff08000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff02000000, 'inr1': 0xffffffff10000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff02000000, 'inr1': 0xffffffff20000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff02000000, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff02000000, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff04000000, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff04000000, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff04000000, 'inr1': 0x4, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff04000000, 'inr1': 0x8, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff04000000, 'inr1': 0x10, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff04000000, 'inr1': 0x20, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff04000000, 'inr1': 0x40, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff04000000, 'inr1': 0x80, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff04000000, 'inr1': 0x100, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff04000000, 'inr1': 0x200, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff04000000, 'inr1': 0x400, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff04000000, 'inr1': 0x800, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff04000000, 'inr1': 0x1000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff04000000, 'inr1': 0x2000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff04000000, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff04000000, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff04000000, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff04000000, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff04000000, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff04000000, 'inr1': 0xffffffff00080000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff04000000, 'inr1': 0xffffffff00100000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff04000000, 'inr1': 0xffffffff00200000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff04000000, 'inr1': 0xffffffff00400000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff04000000, 'inr1': 0xffffffff00800000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff04000000, 'inr1': 0xffffffff01000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff04000000, 'inr1': 0xffffffff02000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff04000000, 'inr1': 0xffffffff04000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff04000000, 'inr1': 0xffffffff08000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff04000000, 'inr1': 0xffffffff10000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff04000000, 'inr1': 0xffffffff20000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff04000000, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff04000000, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff08000000, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff08000000, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff08000000, 'inr1': 0x4, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff08000000, 'inr1': 0x8, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff08000000, 'inr1': 0x10, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff08000000, 'inr1': 0x20, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff08000000, 'inr1': 0x40, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff08000000, 'inr1': 0x80, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff08000000, 'inr1': 0x100, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff08000000, 'inr1': 0x200, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff08000000, 'inr1': 0x400, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff08000000, 'inr1': 0x800, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff08000000, 'inr1': 0x1000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff08000000, 'inr1': 0x2000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff08000000, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff08000000, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff08000000, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff08000000, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff08000000, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff08000000, 'inr1': 0xffffffff00080000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff08000000, 'inr1': 0xffffffff00100000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff08000000, 'inr1': 0xffffffff00200000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff08000000, 'inr1': 0xffffffff00400000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff08000000, 'inr1': 0xffffffff00800000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff08000000, 'inr1': 0xffffffff01000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff08000000, 'inr1': 0xffffffff02000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff08000000, 'inr1': 0xffffffff04000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff08000000, 'inr1': 0xffffffff08000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff08000000, 'inr1': 0xffffffff10000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff08000000, 'inr1': 0xffffffff20000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff08000000, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff08000000, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff10000000, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff10000000, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff10000000, 'inr1': 0x4, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff10000000, 'inr1': 0x8, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff10000000, 'inr1': 0x10, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff10000000, 'inr1': 0x20, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff10000000, 'inr1': 0x40, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff10000000, 'inr1': 0x80, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff10000000, 'inr1': 0x100, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff10000000, 'inr1': 0x200, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff10000000, 'inr1': 0x400, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff10000000, 'inr1': 0x800, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff10000000, 'inr1': 0x1000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff10000000, 'inr1': 0x2000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff10000000, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff10000000, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff10000000, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff10000000, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff10000000, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff10000000, 'inr1': 0xffffffff00080000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff10000000, 'inr1': 0xffffffff00100000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff10000000, 'inr1': 0xffffffff00200000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff10000000, 'inr1': 0xffffffff00400000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff10000000, 'inr1': 0xffffffff00800000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff10000000, 'inr1': 0xffffffff01000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff10000000, 'inr1': 0xffffffff02000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff10000000, 'inr1': 0xffffffff04000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff10000000, 'inr1': 0xffffffff08000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff10000000, 'inr1': 0xffffffff10000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff10000000, 'inr1': 0xffffffff20000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff10000000, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff10000000, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff20000000, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff20000000, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff20000000, 'inr1': 0x4, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff20000000, 'inr1': 0x8, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff20000000, 'inr1': 0x10, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff20000000, 'inr1': 0x20, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff20000000, 'inr1': 0x40, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff20000000, 'inr1': 0x80, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff20000000, 'inr1': 0x100, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff20000000, 'inr1': 0x200, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff20000000, 'inr1': 0x400, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff20000000, 'inr1': 0x800, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff20000000, 'inr1': 0x1000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff20000000, 'inr1': 0x2000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff20000000, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff20000000, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff20000000, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff20000000, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff20000000, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff20000000, 'inr1': 0xffffffff00080000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff20000000, 'inr1': 0xffffffff00100000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff20000000, 'inr1': 0xffffffff00200000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff20000000, 'inr1': 0xffffffff00400000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff20000000, 'inr1': 0xffffffff00800000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff20000000, 'inr1': 0xffffffff01000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff20000000, 'inr1': 0xffffffff02000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff20000000, 'inr1': 0xffffffff04000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff20000000, 'inr1': 0xffffffff08000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff20000000, 'inr1': 0xffffffff10000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff20000000, 'inr1': 0xffffffff20000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff20000000, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff20000000, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff40000000, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff40000000, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff40000000, 'inr1': 0x4, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff40000000, 'inr1': 0x8, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff40000000, 'inr1': 0x10, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff40000000, 'inr1': 0x20, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff40000000, 'inr1': 0x40, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff40000000, 'inr1': 0x80, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff40000000, 'inr1': 0x100, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff40000000, 'inr1': 0x200, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff40000000, 'inr1': 0x400, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff40000000, 'inr1': 0x800, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff40000000, 'inr1': 0x1000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff40000000, 'inr1': 0x2000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff40000000, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff40000000, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff40000000, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff40000000, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff40000000, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff40000000, 'inr1': 0xffffffff00080000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff40000000, 'inr1': 0xffffffff00100000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff40000000, 'inr1': 0xffffffff00200000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff40000000, 'inr1': 0xffffffff00400000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff40000000, 'inr1': 0xffffffff00800000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff40000000, 'inr1': 0xffffffff01000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff40000000, 'inr1': 0xffffffff02000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff40000000, 'inr1': 0xffffffff04000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff40000000, 'inr1': 0xffffffff08000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff40000000, 'inr1': 0xffffffff10000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff40000000, 'inr1': 0xffffffff20000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff40000000, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff40000000, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff80000000, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff80000000, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff80000000, 'inr1': 0x4, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff80000000, 'inr1': 0x8, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff80000000, 'inr1': 0x10, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff80000000, 'inr1': 0x20, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff80000000, 'inr1': 0x40, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff80000000, 'inr1': 0x80, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff80000000, 'inr1': 0x100, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff80000000, 'inr1': 0x200, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff80000000, 'inr1': 0x400, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff80000000, 'inr1': 0x800, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff80000000, 'inr1': 0x1000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff80000000, 'inr1': 0x2000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff80000000, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff80000000, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0, 'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff80000000, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff80000000, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff80000000, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff80000000, 'inr1': 0xffffffff00080000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff80000000, 'inr1': 0xffffffff00100000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff80000000, 'inr1': 0xffffffff00200000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff80000000, 'inr1': 0xffffffff00400000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff80000000, 'inr1': 0xffffffff00800000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff80000000, 'inr1': 0xffffffff01000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff80000000, 'inr1': 0xffffffff02000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff80000000, 'inr1': 0xffffffff04000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff80000000, 'inr1': 0xffffffff08000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff80000000, 'inr1': 0xffffffff10000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff80000000, 'inr1': 0xffffffff20000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff80000000, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmpd.', 'inr0': 0xffffffff80000000, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,     'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
        )

        cmplw_tests = (
            {'cmd': 'cmplw.', 'inr0': 0x1, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x1, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x1, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x1, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x1, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x1, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x1, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x1, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x1, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x2, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x2, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,  'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x2, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x2, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x2, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x2, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x2, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x2, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x2, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x4000, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x4000, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x4000, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x4000, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x4000, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x4000, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x4000, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x4000, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x4000, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x8000, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x8000, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,       'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x8000, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x8000, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x8000, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x8000, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x8000, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x8000, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0x8000, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff00010000, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff00010000, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff00010000, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff00010000, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff00010000, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff00010000, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff00010000, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff00010000, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff00010000, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff00020000, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff00020000, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff00020000, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff00020000, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff00020000, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff00020000, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff00020000, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff00020000, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff00020000, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff00040000, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff00040000, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff00040000, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff00040000, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff00040000, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff00040000, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff00040000, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff00040000, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff00040000, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff40000000, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff40000000, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff40000000, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff40000000, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff40000000, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff40000000, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff40000000, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff40000000, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff40000000, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x80000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff80000000, 'inr1': 0x1, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff80000000, 'inr1': 0x2, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,   'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff80000000, 'inr1': 0x4000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff80000000, 'inr1': 0x8000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,        'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff80000000, 'inr1': 0xffffffff00010000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff80000000, 'inr1': 0xffffffff00020000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff80000000, 'inr1': 0xffffffff00040000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff80000000, 'inr1': 0xffffffff40000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x40000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff80000000, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
            {'cmd': 'cmplw.', 'inr0': 0xffffffff80000000, 'inr1': 0xffffffff80000000, 'incr': 0x0, 'inxer': 0x0, 'infpscr': 0x0,    'expcr': 0x20000000,    'expxer': 0x0,  'expfpscr': 0x0},
        )

        subfco_tests = (
            {'cmd': 'subfco.', 'inr1': 0x1, 'inr2': 0x2, 'inr3': 0x0, 'incr': 0x0, 'inxer': 0x0,    'expr3': 0xffffffffffffffff,    'expcr': 0x80000000,    'expxer': 0x0,},
            {'cmd': 'subfco.', 'inr1': 0x1, 'inr2': 0x2, 'inr3': 0x0, 'incr': 0x0, 'inxer': 0xa0000000,     'expr3': 0xffffffffffffffff,    'expcr': 0x90000000,    'expxer': 0x80000000,},
            {'cmd': 'subfco.', 'inr1': 0x3fffffffffffffff, 'inr2': 0x3fffffffffffffff, 'inr3': 0x0, 'incr': 0x0, 'inxer': 0x0,      'expr3': 0x0,   'expcr': 0x20000000,    'expxer': 0x20000000,},
            {'cmd': 'subfco.', 'inr1': 0x4000000000000000, 'inr2': 0x4000000000000000, 'inr3': 0x0, 'incr': 0x0, 'inxer': 0x0,      'expr3': 0x0,   'expcr': 0x20000000,    'expxer': 0x20000000,},
            {'cmd': 'subfco.', 'inr1': 0x4000000000000000, 'inr2': 0x4000000000000000, 'inr3': 0x0, 'incr': 0x0, 'inxer': 0xc0000000,       'expr3': 0x0,   'expcr': 0x30000000,    'expxer': 0xa0000000,},
            {'cmd': 'subfco.', 'inr1': 0x7fffffffffffffff, 'inr2': 0x7fffffffffffffff, 'inr3': 0x0, 'incr': 0x0, 'inxer': 0x0,      'expr3': 0x0,   'expcr': 0x20000000,    'expxer': 0x20000000,},
            {'cmd': 'subfco.', 'inr1': 0x7fffffffffffffff, 'inr2': 0x7fffffffffffffff, 'inr3': 0x0, 'incr': 0x0, 'inxer': 0xc0000000,       'expr3': 0x0,   'expcr': 0x30000000,    'expxer': 0xa0000000,},
            {'cmd': 'subfco.', 'inr1': 0x8000000000000000, 'inr2': 0x8000000000000000, 'inr3': 0x0, 'incr': 0x0, 'inxer': 0x0,      'expr3': 0x0,   'expcr': 0x20000000,    'expxer': 0x20000000,},
            {'cmd': 'subfco.', 'inr1': 0x8000000000000000, 'inr2': 0x8000000000000000, 'inr3': 0x0, 'incr': 0x0, 'inxer': 0xc0000000,       'expr3': 0x0,   'expcr': 0x30000000,    'expxer': 0xa0000000,},
            {'cmd': 'subfco.', 'inr1': 0xffffffffffffffff, 'inr2': 0xffffffffffffffff, 'inr3': 0x0, 'incr': 0x0, 'inxer': 0x0,      'expr3': 0x0,   'expcr': 0x20000000,    'expxer': 0x20000000,},
            {'cmd': 'subfco.', 'inr1': 0xffffffffffffffff, 'inr2': 0xffffffffffffffff, 'inr3': 0x0, 'incr': 0x0, 'inxer': 0xa0000000,       'expr3': 0x0,   'expcr': 0x30000000,    'expxer': 0xa0000000,},
        )
        OPCODE_ADDCO = unhexlify('7C620C15')
        OPCODE_CMPD =  unhexlify('7C200800')
        OPCODE_CMPLW = unhexlify('7C000840')
        OPCODE_SUBFCO= unhexlify('7C620C11')

        vw, emu, sctx = getVivEnv(arch='ppc-server')
        ppcarch = vw.imem_archs[0]
        op = ppcarch.archParseOpcode(OPCODE_ADDCO)
        for test in addco_tests:
            self._do_addco_CR_XER(op, emu, test['inr1'],  test['inr2'], test['inr3'], test['incr'], test['inxer'], test['expr3'], test['expcr'], test['expxer'])

        op = ppcarch.archParseOpcode(OPCODE_CMPD)
        for test in cmpd_tests:
            self._do_cmpd_CR_XER(op, emu, test['inr0'],  test['inr1'], test['incr'], test['inxer'], test['infpscr'], test['expcr'], test['expxer'], test['expfpscr'])

        op = ppcarch.archParseOpcode(OPCODE_CMPLW)
        for test in cmplw_tests:
            self._do_cmpd_CR_XER(op, emu, test['inr0'],  test['inr1'], test['incr'], test['inxer'], test['infpscr'], test['expcr'], test['expxer'], test['expfpscr'])

        op = ppcarch.archParseOpcode(OPCODE_SUBFCO)
        for test in subfco_tests:
            self._do_addco_CR_XER(op, emu, test['inr1'],  test['inr2'], test['inr3'], test['incr'], test['inxer'], test['expr3'], test['expcr'], test['expxer'])


    def _do_addco_CR_XER(self, op, emu, r1, r2, r3, cr, xer, expr3, expcr, expxer):
        emu.setRegisterByName('r1', r1)
        emu.setRegisterByName('r2', r2)
        emu.setRegisterByName('r3', r3)
        emu.setRegisterByName('CR', cr)
        emu.setRegisterByName('XER', xer)

        emu.executeOpcode(op)

        newcr = emu.getRegisterByName('CR')
        newxer = emu.getRegisterByName('XER')
        newr3 = emu.getRegisterByName('r3')

        tmpl = "%r:  r1:%x r2:%x r3:%x cr:%x xer:%x   nr3:%x ncr:%x nxer:%x   er3:%x ecr:%x exer:%x"
        self.assertEqual((newr3, newcr, newxer), (expr3, expcr, expxer), \
                msg=tmpl % (op, r1, r2, r3, cr, xer, newr3, newcr, newxer, expr3, expcr, expxer) )


    def _do_cmpd_CR_XER(self, op, emu, r0, r1, cr, xer, fpscr, expcr, expxer, expfpscr):
        emu.setRegisterByName('r0', r0)
        emu.setRegisterByName('r1', r1)
        emu.setRegisterByName('CR', cr)
        emu.setRegisterByName('XER', xer)
        emu.setRegisterByName('FPSCR', fpscr)

        emu.executeOpcode(op)

        newcr = int(emu.getRegisterByName('CR'))
        newxer = int(emu.getRegisterByName('XER'))
        newfpscr = int(emu.getRegisterByName('FPSCR'))

        tmpl = "%r:  r0:%x r1:%x cr:%x xer:%x   ncr:%x nxer:%x nfpscr:%x   ecr:%x exer:%x efpscr:%x"
        self.assertEqual((newcr, newxer, newfpscr), (expcr, expxer, expfpscr), \
                msg=tmpl % (op, r0, r1, cr, xer, newcr, newxer, fpscr, expcr, expxer, expfpscr))


