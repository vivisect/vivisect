import struct
import binascii

import envi
import envi.exc as e_exc
import envi.memory as e_mem
import envi.memcanvas as e_memcanvas
import envi.memcanvas.renderers as e_rend
import envi.archs.arm as arm
import vivisect

import logging
import platform
import unittest

import arm_bit_test_adds
import arm_bit_test_cmn
import arm_bit_test_cmp
import arm_bit_test_subs

from envi import IF_RET, IF_NOFALL, IF_BRANCH, IF_CALL, IF_COND
from envi.archs.arm.regs import *
from envi.archs.arm.const import *
from envi.archs.arm.disasm import *

from envi.tests.armthumb_tests import advsimdtests

logger = logging.getLogger(__name__)


GOOD_TESTS = 5953
GOOD_EMU_TESTS = 1175


instrs = [
        ('06e202f44141', 0x4560, 'adc 0x4141(r15).w,r4', 0, ()),    # FORM_RD_LD_MI_RS
        ('06e302f44141', 0x4560, 'adc r15,r4', 0, ()),              # FORM_RD_LD_MI_RS
        ('06e102f44141', 0x4560, 'adc 0x41(r15).w,r4', 0, ()),      # FORM_RD_LD_MI_RS
        ('06a102f44141', 0x4560, 'adc 0x41(r15).l,r4', 0, ()),      # FORM_RD_LD_MI_RS
        ('fd7c24414243', 0x4560, 'adc 0x414243,r4', 0, ()),         # FORM_RD_LI
        ('fda432f44141', 0x4560, 'shar 0x4,r3,r2', 0, ()),          # DFLT-3/4


]

class ArmInstructionSet(unittest.TestCase):
    ''' main unit test with all tests to run '''
    def test_envi_arm_assorted_instrs(self):
        #setup initial work space for test
        vw = vivisect.VivWorkspace()
        vw.setMeta("Architecture", "rxv2")
        vw.addMemoryMap(0, 7, 'firmware', '\xff' * 16384*1024)
        vw.addMemoryMap(0x400000, 7, 'firmware', '\xff' * 16384*1024)
        emu = vw.getEmulator()
        emu.setMeta('forrealz', True)
        emu._forrealz = True
        emu.logread = emu.logwrite = True
        badcount = 0
        goodcount = 0
        goodemu = 0
        bademu = 0

        for bytez, va, reprOp, iflags, emutests in instrs:
            op = vw.arch.archParseOpcode(binascii.unhexlify(bytez), 0, va)
            redoprepr = repr(op).replace(' ','').lower()
            redgoodop = reprOp.replace(' ','').lower()
            if redoprepr != redgoodop:
                num, = struct.unpack("<I", binascii.unhexlify(bytez))
                bs = bin(num)[2:].zfill(32)
                badcount += 1
                raise Exception("%d FAILED to decode instr:  %.8x %s - should be: %s  - is: %s" % \
                        (goodcount, va, bytez, reprOp, repr(op) ) )
                self.assertEqual((goodcount, bytez, redoprepr), (goodcount, bytez, redgoodop))

            else:
                goodcount += 1

            if not len(emutests):
                try:
                    # if we don't have special tests, let's just run it in the emulator anyway and see if things break
                    if not self.validateEmulation(emu, op, (), ()):
                        goodemu += 1
                    else:
                        bademu += 1
                except envi.UnsupportedInstruction:
                    bademu += 1
                except Exception as exp:
                    logger.exception("Exception in Emulator for command - %r  %r  %r\n  %r", repr(op), bytez, reprOp, exp)
                    bademu += 1
            else:
                # if we have a special test lets run it
                for tidx, sCase in enumerate(emutests):
                    #allows us to just have a result to check if no setup needed
                    if 'tests' in sCase:
                        setters = ()
                        if 'setup' in sCase:
                            setters = sCase['setup']
                        tests = sCase['tests']
                        if not self.validateEmulation(emu, op, (setters), (tests), tidx):
                            goodcount += 1
                            goodemu += 1
                        else:
                            bademu += 1
                            raise Exception( "FAILED emulation (special case): %.8x %s - %s" % (va, bytez, op) )

                    else:
                        bademu += 1
                        raise Exception( "FAILED special case test format bad:  Instruction test does not have a 'tests' field: %.8x %s - %s" % (va, bytez, op))

        logger.info("Done with assorted instructions test.  DISASM: %s tests passed.  %s tests failed.  EMU: %s tests passed.  %s tests failed" % \
                (goodcount, badcount, goodemu, bademu))
        logger.info("Total of ", str(goodcount + badcount) + " tests completed.")
        self.assertEqual(goodcount, GOOD_TESTS)
        self.assertEqual(goodemu, GOOD_EMU_TESTS)

