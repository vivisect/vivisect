import os
import unittest
import vivisect
import envi.archs.ppc
import envi.exc as e_exc
import envi.const as e_const
import envi.common as e_common
import envi.expression as e_exp
import envi.archs.ppc.vle as eapvd
import envi.archs.ppc.emu as eape
import envi.archs.ppc.const as eapc
import vivisect.symboliks.analysis as vs_anal

import logging
from binascii import unhexlify
from envi.archs.ppc.regs import *
from envi.archs.ppc.const import *

logging.basicConfig()
logger = logging.getLogger(__name__)
_log_level = os.environ.get('LOG_LEVEL', 'INFO')
if hasattr(logging, _log_level):
    e_common.initLogging(logger, level=getattr(logging, _log_level))
else:
    e_common.initLogging(logger, level=int(_log_level))

MARGIN_OF_ERROR = 200

def getVivEnv(arch='ppc', endian=e_const.ENDIAN_MSB):
    vw = vivisect.VivWorkspace()
    vw.setMeta("Architecture", arch)
    vw.setMeta('bigend', endian)
    vw.addMemoryMap(0, 7, 'firmware', b'\xff' * 16384)
    vw.addMemoryMap(0xbfbff000, 7, 'firmware', b'\xfe' * 0x1000)

    # A few more memory regions to match what PPC64 Linux usually allocates
    vw.addMemoryMap(0x10000000, 7, 'ram', b'\xfd' * 0x1000)
    vw.addMemoryMap(0x10010000, 7, 'ram', b'\xfc' * 0x1000)

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

        # XER has at least some sticky bits, which can cause issues. It would
        # arguably be detrimental to have to set this for all instructions where
        # it is necessary, since it can be hard to tell where it's relevant.
        emu.setRegisterByName('xer', 0)

        ## defaults
        emu.setRegister(3, 0x414141)
        emu.setRegister(4, 0x444444)
        emu.setRegister(5, 0x10)
        emu.setRegister(6, 0x464646)
        emu.setRegister(7, 0x474747)
        emu.setStackCounter(0x450000)

        # setup flags and registers
        def _strify(val):
            if isinstance(val, int):
                return hex(val)
            elif isinstance(val, bytes):
                return val.hex()
            else:
                return str(val)
        settersrepr = '( %r )' % (', '.join(["%s=%s" % (_strify(s), _strify(v)) for s,v in setters]))
        testsrepr = '( %r )' % (', '.join(["%s==%s" % (_strify(s), _strify(v)) for s,v in tests]))

        va = 0x40004560
        for tgt, val in setters:
            try:
                # try register first
                emu.setRegisterByName(tgt, val)
                if tgt == 'PC':
                    va = val

            except e_exc.InvalidRegisterName:
                # it's not a register
                if type(tgt) == str:
                    if tgt.startswith("REG_"):
                        # it's a REGISTER constant (able to manipulate individual bits
                        reg = eval(tgt)
                        emu.setRegister(reg, val)

                    elif tgt.startswith('[') and ']' in tgt:
                        tgtaddrstr = tgt[1:tgt.find(']')]
                        if ':' in tgtaddrstr:
                            tgtaddrstr, tgtsz = tgtaddrstr.split(':')

                        tgtaddr = e_exp.evaluate(tgtaddrstr, emu.getRegisters())
                        emu.writeMemory(tgtaddr, val)

                elif isinstance(tgt, int):
                    # it's an address
                    emu.writeMemory(tgt, val)

                else:
                    op = emu.archParseOpcode(unhexlify(opbytes), 0, va=va)
                    raise Exception( "Funkt up Setting: (%r: %r test#%d)  %s = 0x%x" % (opbytes, op, tidx, tgt, val) )

        op = emu.archParseOpcode(unhexlify(opbytes), 0, va=va)
        logger.debug("0x%x:  %r",op.va, op)

        emu.executeOpcode(op)

        if not len(tests):
            success = True
        else:
            # start out as failing...
            success = False

        failure_msg = []
        for tgt, val in tests:
            try:
                # try register first
                testval = emu.getRegisterByName(tgt)
                if testval == val:
                    success = True
                else:  # should be an else
                    failure_msg.append('%s  !=  %s (observed: %s) (reg)' % (_strify(tgt), _strify(val), _strify(testval)))

            except e_exc.InvalidRegisterName:
                # it's not a register

                if type(tgt) == str:
                    if tgt.startswith("REG_"):
                        # it's a REGISTER constant (able to manipulate individual bits
                        reg = eval(tgt)
                        testval = emu.getRegister(reg)
                        if testval == val:
                            success = True
                        else:  # should be an else
                            failure_msg.append('%s  !=  %s (observed: %s) (reg)' % (_strify(tgt), _strify(val), _strify(testval)))

                    elif tgt.startswith('[') and ']' in tgt:
                        tgtaddrstr = tgt[1:tgt.find(']')]
                        if ':' in tgtaddrstr:
                            tgtaddrstr, tgtsz = tgtaddrstr.split(':')
                        else:
                            tgtsz = len(val)

                        tgtaddr = e_exp.evaluate(tgtaddrstr, emu.getRegisters())
                        testval = emu.readMemory(tgtaddr, tgtsz)
                        if testval == val:
                            success = True
                        else:
                            failure_msg.append('%s  !=  %s (observed: %s) (mem)' % (_strify(tgt), _strify(val), _strify(testval)))

                elif isinstance(tgt, int):
                    # it's an address, determine how many bytes to read
                    testval_size = len(val)
                    testval = emu.readMemory(tgt, testval_size)
                    if testval == val:
                        success = True

                    else:
                        failure_msg.append('%s  !=  %s (observed: %s) (mem)' % (_strify(tgt), _strify(val), _strify(testval)))
                else:
                    raise Exception( "Funkt up test (%r test#%d) : %s == %s" % (op, tidx, tgt, val) )

        if failure_msg:
            msg = '\n\t'.join(failure_msg)
            raise Exception("FAILED: (%r test#%d)\n\t%s\n\t(setters: %r)\n\t(test: %r)" % (op, tidx, msg, settersrepr, testsrepr))

        return success, op

    def do_emutsts(self, emu, opbytes, emutests):
        '''
        Setup and Perform Emulation Tests per architecture variant
        '''
        bademu = 0
        goodemu = 0

        # Keep track of which instructions have been tested
        tested_instrs = set()

        # if we have a special test lets run it
        for tidx, sCase in enumerate(emutests):
            #allows us to just have a result to check if no setup needed
            if 'tests' in sCase:
                setters = ()
                if 'setup' in sCase:
                    setters = sCase['setup']

                tests = sCase['tests']

                test_result, op = self.validateEmulation(emu, opbytes, (setters), (tests), tidx)
                tested_instrs.add(op.opcode)

                if test_result:
                    goodemu += 1
                else:
                    bademu += 1
                    raise Exception( "FAILED emulation (special case): %.8x %s - %s" % (op.va, opbytes, op) )

            else:
                bademu += 1
                raise Exception( "FAILED special case test format bad:  Instruction test does not have a 'tests' field: %.8x %s - %s" % (op.va, opbytes, op))

        return goodemu, bademu, tested_instrs

    def test_envi_ppcvle_disasm(self):
        from . import ppc_vle_instructions
        self.do_envi_disasm('vle', ppc_vle_instructions)

    def test_envi_ppc_embedded_disasm(self):
        from . import ppc_embedded_instructions
        self.do_envi_disasm('ppc-embedded', ppc_embedded_instructions)

    def test_envi_ppc_server_disasm(self):
        from . import ppc_server_instructions
        self.do_envi_disasm('ppc-server', ppc_server_instructions)

    def test_envi_ppcvle_emu(self):
        from . import ppc_vle_emutests
        self.do_envi_emu('vle', ppc_vle_emutests)

    def test_envi_ppc_embedded_emu(self):
        from . import ppc_embedded_emutests
        self.do_envi_emu('ppc-embedded', ppc_embedded_emutests)

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
        #self.assertEqual(test_pass, len(test_module.instructions))

    def run_one_test(self, archname, test_bytes, test):
        vw, emu, sctx = getVivEnv(archname)
        ngoodemu, nbademu, _ = self.do_emutsts(emu, test_bytes, test)
        logger.debug('good: %d', ngoodemu)
        logger.debug('bad: %d', nbademu)

    def do_envi_emu(self, archname, emu_module):
        bademu = 0
        goodemu = 0
        tested_instrs = set()

        vw, emu, sctx = getVivEnv(archname)

        total_tests = sum(len(t) for t in emu_module.emutests.values())
        for test_bytes, emutests in emu_module.emutests.items():
            try:
                # do emulator tests for this byte combination
                if emutests is not None:
                    ngoodemu, nbademu, opcodes = self.do_emutsts(emu, test_bytes, emutests)
                    goodemu += ngoodemu
                    bademu += nbademu
                    tested_instrs |= opcodes

            except Exception as  e:
                # Save the tests that were attempted to be run for this byte
                # pattern as "bad"
                bademu += len(emutests)

                logging.exception('ERROR: {}:'.format(test_bytes,))

        logger.info("%s: %d of %d successes", archname, goodemu, total_tests)
        self.assertAlmostEqual(goodemu, total_tests, delta=MARGIN_OF_ERROR)

        logger.info("%s: Total of %d tests completed.", archname, (goodemu + bademu))
        self.assertEqual(goodemu, emu_module.GOOD_EMU_TESTS)

        # sanity check: the number of good and bad tests should equal the total
        # tests
        self.assertEqual(goodemu+bademu, total_tests)

        # For informational/debugging purposes, print out which instructions
        # have not been tested
        all_instrs = dict((n, getattr(eapc, n)) for n in dir(eapc) if n.startswith('INS_'))
        untested_instrs = dict((k, v) for k, v in all_instrs.items() if v not in tested_instrs)

        if untested_instrs:
            logger.warning('%s %d out of %d instructions tested', archname, len(tested_instrs), len(all_instrs))
            msgs = ['%s (%d)' % (k, v) for k, v in untested_instrs.items()]
            logger.debug('\n'.join(msgs))

    def test_MASK_and_ROTL(self):
        import vivisect.symboliks.archs.ppc as vsap

        for x in range(64):
            for y in range(64):
                #mask =
                emumask = eape.MASK(x, y)

                symmask = vsap.MASK(vsap.Const(x, 8), vsap.Const(y, 8))
                logger.debug('%#x, %r, %s', emumask, symmask, symmask)


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
        emu.setRegisterByName('cr', cr)
        emu.setRegisterByName('xer', xer)

        emu.executeOpcode(op)

        newcr = emu.getRegisterByName('cr')
        newxer = emu.getRegisterByName('xer')
        newr3 = emu.getRegisterByName('r3')

        tmpl = "%r:  r1:%x r2:%x r3:%x cr:%x xer:%x   nr3:%x ncr:%x nxer:%x   er3:%x ecr:%x exer:%x"
        self.assertEqual((newr3, newcr, newxer), (expr3, expcr, expxer), \
                msg=tmpl % (op, r1, r2, r3, cr, xer, newr3, newcr, newxer, expr3, expcr, expxer) )


    def _do_cmpd_CR_XER(self, op, emu, r0, r1, cr, xer, fpscr, expcr, expxer, expfpscr):
        emu.setRegisterByName('r0', r0)
        emu.setRegisterByName('r1', r1)
        emu.setRegisterByName('cr', cr)
        emu.setRegisterByName('xer', xer)
        emu.setRegisterByName('fpscr', fpscr)

        emu.executeOpcode(op)

        newcr = int(emu.getRegisterByName('cr'))
        newxer = int(emu.getRegisterByName('xer'))
        newfpscr = int(emu.getRegisterByName('fpscr'))

        tmpl = "%r:  r0:%x r1:%x cr:%x xer:%x   ncr:%x nxer:%x nfpscr:%x   ecr:%x exer:%x efpscr:%x"
        self.assertEqual((newcr, newxer, newfpscr), (expcr, expxer, expfpscr), \
                msg=tmpl % (op, r0, r1, cr, xer, newcr, newxer, fpscr, expcr, expxer, expfpscr))

    def test_ppc_const_dups(self):
        # Check if there are any duplicates in the data used to generate the PPC
        # constants

        # Check on the SPR names
        import envi.archs.ppc.spr as eaps
        spr_name_lookup = {}
        for sprnum, (rname, _, _bitsz) in eaps.sprs.items():
            sprname = rname.upper()

            # If this SPR's name is already there print a helpful message
            if sprname in spr_name_lookup:
                dupnum = spr_name_lookup[sprname]
                dupname = eaps.sprnames[dupnum].upper()
                logger.debug('SPR[%d]: %s ([%d]: %s)', sprnum, sprname, dupnum, dupname)

            self.assertTrue(sprname not in spr_name_lookup)

            spr_name_lookup[rname] = sprnum

    def test_ppc_invalid_emufuncs(self):
        emufuncs = [n[2:].lower() for n in dir(eape.PpcAbstractEmulator) if n.startswith('i_')]
        instrs = [n[4:].lower() for n in dir(eapc) if n.startswith('INS_')]

        # Find any i_??? functions which do not match a valid instruction
        invalid_instr_funcs = [n for n in emufuncs if n not in instrs]

        if invalid_instr_funcs:
            logger.warning('%d invalid PPC Emulation functions', len(invalid_instr_funcs))
            msgs = ['i_%s has no matching INS_%s instruction' % (n, n.upper()) for n in invalid_instr_funcs]
            logger.debug('\n'.join(msgs))

    def test_ppc_missing_emufuncs(self):
        emufuncs = [n[2:].lower() for n in dir(eape.PpcAbstractEmulator) if n.startswith('i_')]
        instrs = [n[4:].lower() for n in dir(eapc) if n.startswith('INS_')]

        # Find any INS_??? instructions that don't have emulation functions
        missing_emu_instrs = [n for n in instrs if n not in emufuncs]

        if missing_emu_instrs:
            logger.warning('Missing %d PPC Emulation functions', len(missing_emu_instrs))
            msgs = ['INS_%s has no matching i_%s emulation instruction' % (n.upper(), n) for n in missing_emu_instrs]
            logger.debug('\n'.join(msgs))
