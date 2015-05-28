
import envi
import envi.memory as e_mem
import envi.memcanvas as e_memcanvas
import envi.memcanvas.renderers as e_rend
import envi.archs.h8 as e_h8
import vivisect
import platform
import unittest
from envi import IF_RET, IF_NOFALL, IF_BRANCH, IF_CALL, IF_COND
from envi.archs.h8.const import *

instrs = [
        ( "8342", 0x4560, 'add.b #42, r3h', IF_B),
        ( "7c6075f0", 0x4560, 'bixor #7, @er6', 0),
        ( "7d707170", 0x4560, 'bnot #7, @er7', 0),
        ( "0832", 0x4560, 'add.b r3h, r2h', IF_B),
        ( "791d4745", 0x4560, 'add.w #4745, e5', IF_W),
        ( "0932", 0x4560, 'add.w r3, r2', IF_W),
        ( "7a1d00047145", 0x4560, 'add.l #47145, er5', IF_L),
        ( "01406930", 0x4560, 'ldc @er3, ccr', 0),
        ( "014069b0", 0x4560, 'stc ccr, @er3', 0),
        ( "01c05023", 0x4560, 'mulxs.b r2h, r3', IF_B),
        ( "01c05223", 0x4560, 'mulxs.w r2, er3', IF_W),
        ( "01d05123", 0x4560, 'divxs.b r2h, r3', IF_B),
        ( "01d05323", 0x4560, 'divxs.w r2, er3', IF_W),
        ( "01f06423", 0x4560, 'or.l er2, er3', IF_L),
        ( "01f06523", 0x4560, 'xor.l er2, er3', IF_L),
        ( "01f06623", 0x4560, 'and.l er2, er3', IF_L),
        ( "0a03", 0x4560, 'inc.b r3h', IF_B),
        ( "0a83", 0x4560, 'add.l er0, er3', IF_L),
        ( "0b83", 0x4560, 'adds #2, er3', 0),
        ( "0b93", 0x4560, 'adds #4, er3', 0),
        ( "0b53", 0x4560, 'inc.w #1, r3', IF_W),
        ( "0bf3", 0x4560, 'inc.l #2, er3', IF_L),
        ( "0f00", 0x4560, 'daa r0h', 0),
        ( "0f93", 0x4560, 'mov.l er1, er3', IF_L),
        ( "1a03", 0x4560, 'dec.b r3h', IF_B),
        ( "1a83", 0x4560, 'sub.l er0, er3', IF_L),
        ( "1b83", 0x4560, 'subs #2, er3', 0),
        ( "1b93", 0x4560, 'subs #4, er3', 0),
        ( "1b53", 0x4560, 'dec.w #1, r3', IF_W),
        ( "1bf3", 0x4560, 'dec.l #2, er3', IF_L),
        ( "1f00", 0x4560, 'das r0h', 0),
        ( "5470", 0x4560, 'rts', IF_RET | IF_NOFALL),
        ( "4670", 0x4560, 'bne #45d2', IF_BRANCH | IF_COND),
        ( "4e90", 0x4560, 'bgt #44f2', IF_BRANCH | IF_COND),
        ( "58500070", 0x4560, 'blo #45d4', IF_BRANCH | IF_COND),
        ( "58b0f070", 0x4560, 'bmi #35d4', IF_BRANCH | IF_COND),

        ]

class H8InstrTest(unittest.TestCase):
    def test_envi_h8_assorted_instrs(self):
       global instrs

       archmod = envi.getArchModule("h8")

       for bytez, va, reprOp, iflags in instrs:
            op = archmod.archParseOpcode(bytez.decode('hex'), 0, va)
            if repr(op).replace(' ','') != reprOp.replace(' ',''):
                raise Exception("FAILED to decode instr:  %.8x %s - should be: %s  - is: %s" % \
                        ( va, bytez, reprOp, repr(op) ) )
            self.assertEqual(op.iflags, iflags)

    #FIXME: test emuluation as well.


def generateTestInfo(ophexbytez='6e'):
    h8 = e_h8.H8Module()
    opbytez = ophexbytez
    op = h8.archParseOpcode(opbytez.decode('hex'), 0, 0x4000)
    print "opbytez = '%s'\noprepr = '%s'"%(opbytez,repr(op))
    opvars=vars(op)
    opers = opvars.pop('opers')
    print "opcheck = ",repr(opvars)

    opersvars = []
    for x in range(len(opers)):
        opervars = vars(opers[x])
        opervars.pop('_dis_regctx')
        opersvars.append(opervars)

    print "opercheck = %s" % (repr(opersvars))

