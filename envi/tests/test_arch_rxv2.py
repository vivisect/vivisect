import struct
import binascii

import envi
import envi.exc as e_exc
import envi.memory as e_mem
import envi.memcanvas as e_memcanvas
import envi.memcanvas.renderers as e_rend
import vivisect

import logging
import platform
import unittest

from envi import IF_RET, IF_NOFALL, IF_BRANCH, IF_CALL, IF_COND


logger = logging.getLogger(__name__)


GOOD_TESTS = 94
GOOD_EMU_TESTS = 0


instrs = [
        ('06e202f44141', 0x4560, 'adc 0x4141[r15].uw,r4', 0, ()),   # FORM_RD_LD_MI_RS
        ('06e302f4', 0x4560, 'adc r15,r4', 0, ()),              # FORM_RD_LD_MI_RS
        ('06e102f441', 0x4560, 'adc 0x41[r15].uw,r4', 0, ()),     # FORM_RD_LD_MI_RS
        ('06a102f441', 0x4560, 'adc 0x41[r15].l,r4', 0, ()),      # FORM_RD_LD_MI_RS
        ('fd7c24414243', 0x4560, 'adc 0x414243,r4', 0, ()),         # FORM_RD_LI
        ('fda432f44141', 0x4560, 'shar 0x4,r3,r2', 0, ()),          # DFLT-3/4
        ('7f14', 0x4560, 'jsr r4', envi.IF_CALL, ()),               # DFLT-1
        ('7e24', 0x4560, 'abs r4', 0, ()),                          # DFLT-1
        ('fc0f42', 0x4560, 'abs r4,r2', 0, ()),                     # DFLT-2
        ('623b', 0x4560, 'add 0x3,r11', 0, ()),                     # FORM_RD_IMM
        ('4a234142', 0x4560, 'add 0x4142[r2].ub,r3', 0, ()),        # FORM_RD_LD_RS
        ('06ca454142', 0x4560, 'add 0x4142[r4].uw,r5', 0, ()),    # FORM_RD_LD_MI_RS
        ('6423', 0x4560, 'and 0x2,r3', 0, ()),                      # FORM_RD_IMM
        ('742341424344', 0x4560, 'and 0x41424344,r3', 0, ()),       # FORM_RD_LI
        ('53234243', 0x4560, 'and r2,r3', 0, ()),                   # FORM_RD_LD_RS
        ('52234243', 0x4560, 'and 0x4243[r2].ub,r3', 0, ()),        # FORM_RD_LD_RS
        ('2423', 0x4560, 'bgtu 0x4583', 0, ()),                     # FORM_PCDSP
        ('1f', 0x4560, 'bnz 0x4567', 0, ()),                        # FORM_PCDSP
        ('18', 0x4560, 'bnz 0x4568', 0, ()),                        # FORM_PCDSP
        ('2240', 0x4560, 'bgeu 0x45a0', 0, ()),                     # FORM_PCDSP
        ('3b4715', 0x4560, 'bnz 0x8c75', 0, ()),                    # FORM_PCDSP
        ('fced3468', 0x4560, 'bmgtu 0x3,0x68[r3]', 0, ()),          # FORM_BMCND
        ('fde734', 0x4560, 'bmltu 0x7,[r4]', 0, ()),             # FORM_BMCND
        ('fcf23f4546', 0x4560, 'bnot 0x4,0x4546[r3].b', 0, ()),             # FORM_BMCND
        ('fc6e3f4568', 0x4560, 'bnot r3,0x4568[r15].ub', 0, ()),             # FORM_BMCND
        ('fde6f4', 0x4560, 'bnot 0x6,r4', 0, ()),                    # FORM_PCDSP
        ('fc6f36', 0x4560, 'bnot r6,r3', 0, ()),             # FORM_BMCND
        ('08', 0x4560, 'bra 0x4568', 0, ()),             # FORM_BMCND
        ('2e05', 0x4560, 'bra 0x4565', 0, ()),             # FORM_BMCND
        ('384715', 0x4560, 'bra 0x8c75', 0, ()),             # FORM_BMCND
        ('7f45', 0x4560, 'bra r5', 0, ()),             # FORM_BMCND
        ('00', 0x4560, 'brk', 0, ()),             # FORM_BMCND
        ('f2334568', 0x4560, 'bset 0x3,0x4568[r3].b', 0, ()),             # FORM_BMCND
        ('fc62344568', 0x4560, 'bset r3,0x4568[r4].ub', 0, ()),             # FORM_BMCND
        ('7834', 0x4560, 'bset 0x3,r4', 0, ()),             # FORM_BMCND
        ('7934', 0x4560, 'bset 0x13,r4', 0, ()),             # FORM_BMCND
        ('fc6334', 0x4560, 'bset r4,r3', 0, ()),             # FORM_BMCND
        ('394568', 0x4560, 'bsr 0x8ac8', 0, ()),             # FORM_BMCND
        ('05456800', 0x4560, 'bsr 0x45ad60', 0, ()),             # FORM_BMCND
        ('7f53', 0x4560, 'bsr r3', 0, ()),             # FORM_BMCND
        ('f6334568', 0x4560, 'btst 0x3,0x4568[r3].b', 0, ()),             # FORM_BMCND
        ('fc6aab4568', 0x4560, 'btst 0x4568[r11].b,r10', 0, ()),             # FORM_BMCND
        ('7d44', 0x4560, 'btst 0x14,r4', 0, ()),             # FORM_BMCND
        ('fc6bab', 0x4560, 'btst r11,r10', 0, ()),             # FORM_BMCND
        ('7fb3', 0x4560, 'clrpsw O', 0, ()),             # FORM_BMCND
        ('6134', 0x4560, 'cmp 0x3,r4', 0, ()),             # FORM_BMCND
        ('75547f', 0x4560, 'cmp 0x7f,r4', 0, ()),             # FORM_BMCND
        ('76041720', 0x4560, 'cmp 0x1720,r4', 0, ()),             # FORM_BMCND
        ('46341780', 0x4560, 'cmp 0x1780[r3].ub,r4', 0, ()),             # FORM_BMCND
        ('0686341780', 0x4560, 'cmp 0x1780[r3].l,r4', 0, ()),             # FORM_BMCND
        ('fd78841780', 0x4560, 'div 0x1780,r4', 0, ()),             # FORM_BMCND
        ('fc22341780', 0x4560, 'div 0x1780[r3].ub,r4', 0, ()),             # FORM_BMCND
        ('06a208341780', 0x4560, 'div 0x1780[r3].l,r4', 0, ()),             # FORM_BMCND
        ('fd78931780', 0x4560, 'divu 0x1780,r3', 0, ()),             # FORM_BMCND
        ('fc26341780', 0x4560, 'divu 0x1780[r3].ub,r4', 0, ()),             # FORM_BMCND
        ('06a209341780', 0x4560, 'divu 0x1780[r3].l,r4', 0, ()),             # FORM_BMCND
        ('fd0f34', 0x4560, 'emaca r3,r4,acc1', 0, ()),             # FORM_BMCND
        ('fd4f34', 0x4560, 'emsba r3,r4,acc1', 0, ()),             # FORM_BMCND
        ('fd78641780', 0x4560, 'emul 0x1780,r4', 0, ()),             # FORM_BMCND
        ('06a206341780', 0x4560, 'emul 0x1780[r3].l,r4', 0, ()),             # FORM_BMCND
        ('fd0b34', 0x4560, 'emula r3,r4,acc1', 0, ()),             # FORM_BMCND
        ('fd78741780', 0x4560, 'emulu 0x1780,r4', 0, ()),             # FORM_BMCND
        ('fc1e341780', 0x4560, 'emulu 0x1780[r3].ub,r4', 0, ()),             # FORM_BMCND
        ('06a207341780', 0x4560, 'emulu 0x1780[r3].l,r4', 0, ()),             # FORM_BMCND
        ('fd722400047145', 0x4560, 'fadd 0x47145,r4', 0, ()),             # FORM_BMCND
        ('fc8a341780', 0x4560, 'fadd 0x1780[r3].ub,r4', 0, ()),             # FORM_BMCND
        ('ffa345', 0x4560, 'fadd r4,r5,r3', 0, ()),             # FORM_BMCND
        ('fd721400047145', 0x4560, 'fcmp 0x47145,r4', 0, ()),             # FORM_BMCND
        ('fc86341780', 0x4560, 'fcmp 0x1780[r3].b,r4', 0, ()),             # FORM_BMCND
        ('fd724400047145', 0x4560, 'fdiv 0x47145,r4', 0, ()),             # FORM_BMCND
        ('fc92341780', 0x4560, 'fdiv 0x1780[r3].ub,r4', 0, ()),             # FORM_BMCND
        ('fd723400047145', 0x4560, 'fmul 0x47145,r4', 0, ()),             # FORM_BMCND
        ('fc8e341780', 0x4560, 'fmul 0x1780[r3].ub,r4', 0, ()),             # FORM_BMCND
        ('ffb345', 0x4560, 'fmul r4,r5,r3', 0, ()),             # FORM_BMCND
        ('fca2341780', 0x4560, 'fsqrt 0x1780[r3].ub,r4', 0, ()),             # FORM_BMCND
        ('fd720400047145', 0x4560, 'fsub 0x47145,r4', 0, ()),             # FORM_BMCND
        ('fc82341780', 0x4560, 'fsub 0x1780[r3].ub,r4', 0, ()),             # FORM_BMCND
        ('ff8345', 0x4560, 'fsub r4,r5,r3', 0, ()),             # FORM_BMCND
        ('fc96341780', 0x4560, 'ftoi 0x1780[r3].ub,r4', 0, ()),             # FORM_BMCND
        ('fca6341780', 0x4560, 'ftou 0x1780[r3].ub,r4', 0, ()),             # FORM_BMCND
        ('756045', 0x4560, 'int 0x45', 0, ()),             # FORM_BMCND
        ('fc46341780', 0x4560, 'itof 0x1780[r3].ub,r4', 0, ()),             # FORM_BMCND
        ('06a211341780', 0x4560, 'itof 0x1780[r3].l,r4', 0, ()),             # FORM_BMCND
        ('7f04', 0x4560, 'jmp r4', 0, ()),             # FORM_BMCND
        ('7f14', 0x4560, 'jsr r4', 0, ()),             # FORM_BMCND
        ('fd0c34', 0x4560, 'machi r3,r4,acc1', 0, ()),             # FORM_BMCND
        ('fd0e34', 0x4560, 'maclh r3,r4,acc1', 0, ()),             # FORM_BMCND
        ('fd0d34', 0x4560, 'maclo r3,r4,acc1', 0, ()),             # FORM_BMCND
        ('fd78441780', 0x4560, 'max 0x1780,r4', 0, ()),             # FORM_BMCND
        ('fc12341780', 0x4560, 'max 0x1780[r3].ub,r4', 0, ()),             # FORM_BMCND
        ('06a204341780', 0x4560, 'max 0x1780[r3].l,r4', 0, ()),             # FORM_BMCND
        ('fd745417', 0x4560, 'min 0x17,r4', 0, ()),             # FORM_BMCND
        ('fc153417', 0x4560, 'min 0x17[r3].ub,r4', 0, ()),             # FORM_BMCND
        ('0661043417', 0x4560, 'max 0x17[r3].w,r4', 0, ()),             # FORM_BMCND
        ('97cb', 0x4560, 'mov.w r3,0x1f[r4]', 0, ()),             # FORM_BMCND
        ('9fcb', 0x4560, 'mov.w 0x1f[r4],r3', 0, ()),             # FORM_BMCND
        ('66f4', 0x4560, 'mov 0xf,r4', 0, ()),             # FORM_BMCND # wrong, but doesn't really need a size?
        ('3ecc17', 0x4560, 'mov.l 0x17,0x1c[r4]', 0, ()),             # FORM_BMCND
        ('754321', 0x4560, 'mov 0x21,r3', 0, ()),             # FORM_BMCND # doesn't really need a size?
        ('fb3a1780', 0x4560, 'mov 0x1780,r3', 0, ()),             # FORM_BMCND # doesn't really need a size?
        ('fb3200047145', 0x4560, 'mov 0x47145,r3', 0, ()),             # FORM_BMCND # doesn't really need a size?
        ### FIXME: go back through and make sense of all the SIMM/IMM/UIMM parsing.  should these be operand flags?
        ('ef34', 0x4560, 'mov.l r3,r4', 0, ()),             # FORM_
        ('fa3a17804715', 0x4560, 'mov.l 0x1780,0x4715[r3]', 0, ()),             # FORM_
        ('fe6234', 0x4560, 'mov.l [r3, r2],r4', 0, ()),             # FORM_
        ('eb341780', 0x4560, 'mov.l r4,0x1780[r3]', 0, ()),             # FORM_
        ('fe2234', 0x4560, 'mov.l r4,[r3, r2]', 0, ()),             # FORM_
        ('e934401780', 0x4560, 'mov.l 0x40[r3],0x1780[r4]', 0, ()),             # FORM_
        ('fd2234', 0x4560, 'mov.l r4,[r3+]', 0, ()),             # FORM_
        ('fd2634', 0x4560, 'mov.l r4,[-r3]', 0, ()),             # FORM_
        ('fd2a34', 0x4560, 'mov.l [r3+],r4', 0, ()),             # FORM_
        ('fd2e34', 0x4560, 'mov.l [-r3],r4', 0, ()),             # FORM_
        ('fd2c34', 0x4560, 'mov.b [-r3],r4', 0, ()),             # FORM_

]

class RXv2InstructionSet(unittest.TestCase):
    ''' main unit test with all tests to run '''
    def test_envi_rxv2_assorted_instrs(self):
        #setup initial work space for test
        vw = vivisect.VivWorkspace()
        vw.setMeta("Architecture", "rxv2")
        vw.addMemoryMap(0, 7, 'firmware', '\xff' * 16384*1024)
        vw.addMemoryMap(0x400000, 7, 'firmware', '\xff' * 16384*1024)
        #emu = vw.getEmulator()
        #emu.setMeta('forrealz', True)
        #emu._forrealz = True
        #emu.logread = emu.logwrite = True
        badcount = 0
        goodcount = 0
        goodemu = 0
        bademu = 0

        for bytez, va, reprOp, iflags, emutests in instrs:
            print("Test: %r" % bytez)
            op = vw.arch.archParseOpcode(binascii.unhexlify(bytez), 0, va)
            redoprepr = repr(op).replace(' ','').lower()
            redgoodop = reprOp.replace(' ','').lower()
            if redoprepr != redgoodop:
                badcount += 1
                raise Exception("%d FAILED to decode instr:  %.8x %s - should be: %s  - is: %s" % \
                        (goodcount, va, bytez, reprOp, repr(op) ) )
                self.assertEqual((goodcount, bytez, redoprepr), (goodcount, bytez, redgoodop))

            else:
                goodcount += 1


            # NO EMUTESTS YET
            continue

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
        #self.assertEqual(goodemu, GOOD_EMU_TESTS)

