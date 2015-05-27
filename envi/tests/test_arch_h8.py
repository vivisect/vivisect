
import envi
import envi.memory as e_mem
import envi.memcanvas as e_memcanvas
import envi.memcanvas.renderers as e_rend
import envi.archs.h8 as e_h8
import vivisect
import platform
import unittest

instrs = [
        ( "8342", 0x4560, 'add.b #42, r3h'),
        ( "7c6075f0", 0x4560, 'bixor #7, @er6'),
        ( "7d707170", 0x4560, 'bnot #7, @er7'),
        ( "0832", 0x4560, 'add.b r3h, r2h'),
        ( "791d4745", 0x4560, 'add.w #4745, e5'),
        ( "0932", 0x4560, 'add.w r3, r2'),
        ( "7a1d00047145", 0x4560, 'add.l #47145, er5'),
        ( "01406930", 0x4560, 'ldc @er3, ccr'),
        ( "014069b0", 0x4560, 'stc ccr, @er3'),
        ( "01c05023", 0x4560, 'mulxs.b r2h, r3'),
        ( "01c05223", 0x4560, 'mulxs.w r2, er3'),
        ( "01d05123", 0x4560, 'divxs.b r2h, r3'),
        ( "01d05323", 0x4560, 'divxs.w r2, er3'),
        ( "01f06423", 0x4560, 'or.l er2, er3'),
        ( "01f06523", 0x4560, 'xor.l er2, er3'),
        ( "01f06623", 0x4560, 'and.l er2, er3'),
        ( "0a03", 0x4560, 'inc.b r3h'),
        ( "0a83", 0x4560, 'add.l er0, er3'),
        ( "0b83", 0x4560, 'adds #2, er3'),
        ( "0b93", 0x4560, 'adds #4, er3'),
        ( "0b53", 0x4560, 'inc.w #1, r3'),
        ( "0bf3", 0x4560, 'inc.l #2, er3'),
        ( "0f00", 0x4560, 'daa r0h'),
        ( "0f93", 0x4560, 'mov.l er1, er3'),

        ]

class H8InstrTest(unittest.TestCase):
    def test_envi_h8_assorted_instrs(self):
       global instrs

       archmod = envi.getArchModule("h8")

       for bytez, va, reprOp in instrs:
           op = archmod.archParseOpcode(bytez.decode('hex'), 0, va)
           if repr(op).replace(' ','') != reprOp.replace(' ',''):
               raise Exception("FAILED to decode instr:  %.8x %s - should be: %s  - is: %s" % \
                       ( va, bytez, reprOp, repr(op) ) )

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

