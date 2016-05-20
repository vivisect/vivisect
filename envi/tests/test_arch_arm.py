import struct

import envi
import envi.memory as e_mem
import envi.registers as e_reg
import envi.memcanvas as e_memcanvas
import envi.memcanvas.renderers as e_rend
import envi.archs.h8 as e_h8
import vivisect
import platform
import unittest
from envi import IF_RET, IF_NOFALL, IF_BRANCH, IF_CALL, IF_COND
from envi.archs.h8.regs import *
from envi.archs.h8.const import *
from envi.archs.h8.parsers import *


# OPHEX, VA, repr, flags, emutests
instrs = [
        ('08309fe5', 0xbfb00000, 'ldr r3, [#0xbfb00010]', 0, ()),
        ('0830bbe5', 0xbfb00000, 'ldr r3, [r11, #0x8]!', 0, ()),
        ('08309be4', 0xbfb00000, 'ldr r3, [r11], #0x8', 0, ()),
        ('08301be4', 0xbfb00000, 'ldr r3, [r11], #-0x8', 0, ()),
        ('02209ae7', 0xbfb00000, 'ldr r2, [r10, r2]', 0, ()),
        ('02209ae6', 0xbfb00000, 'ldr r2, [r10], r2', 0, ()),
        ('02203ae7', 0xbfb00000, 'ldr r2, [r10, -r2]!', 0, ()),
        ('0220bae7', 0xbfb00000, 'ldr r2, [r10, r2]!', 0, ()),
        ('22209ae7', 0xbfb00000, 'ldr r2, [r10, r2 lsr #32]', 0, ()),
        ('08309fe5', 0xbfb00000, 'ldr r3, [#0xbfb00010]', 0, ()),
        ('08309fe5', 0xbfb00000, 'ldr r3, [#0xbfb00010]', 0, ()),
        ]
# FIXME: create list of this from IDA flow below - THIS CURRENT DATA IS FOR H8!  NOT ARM/THUMB
'''
        ( '8342', 0x4560, 'add.b #42, r3h', IF_B, () ),
        ( '7c6075f0', 0x4560, 'bixor #7, @er6', 0, () ),
        ( '7d507170', 0x4560, 'bnot #7, @er5', 0, () ),
        ( '0832', 0x4560, 'add.b r3h, r2h', IF_B, () ),
        ( '791d4745', 0x4560, 'add.w #4745, e5', IF_W, () ),
        ( '0932', 0x4560, 'add.w r3, r2', IF_W, () ),
        ( '7a1d00047145', 0x4560, 'add.l #47145, er5', IF_L, () ),
        ( '01406930', 0x4560, 'ldc.w @er3, ccr', IF_W, () ),
        ( '014069b0', 0x4560, 'stc.w ccr, @er3', IF_W, () ),
        ( '01c05023', 0x4560, 'mulxs.b r2h, r3', IF_B, () ),
        ( '01c05223', 0x4560, 'mulxs.w r2, er3', IF_W, () ),
        ( '01d05123', 0x4560, 'divxs.b r2h, r3', IF_B, () ),
        ( '01d05323', 0x4560, 'divxs.w r2, er3', IF_W, () ),
        ( '01f06423', 0x4560, 'or.l er2, er3', IF_L, () ),
        ( '01f06523', 0x4560, 'xor.l er2, er3', IF_L, () ),
        ( '01f06623', 0x4560, 'and.l er2, er3', IF_L, () ),
        ( '0a03', 0x4560, 'inc.b r3h', IF_B, () ),
        ( '0a83', 0x4560, 'add.l er0, er3', IF_L, () ),
        ( '0b83', 0x4560, 'adds #2, er3', 0, () ),
        ( '0b93', 0x4560, 'adds #4, er3', 0, () ),
        ( '0b53', 0x4560, 'inc.w #1, r3', IF_W, () ),
        ( '0bf3', 0x4560, 'inc.l #2, er3', IF_L, () ),
        ( '0f00', 0x4560, 'daa r0h', 0, () ),
        ( '0f93', 0x4560, 'mov.l er1, er3', IF_L, () ),
        ( '1a03', 0x4560, 'dec.b r3h', IF_B, () ),
        ( '1a83', 0x4560, 'sub.l er0, er3', IF_L, (
            {'setup':(('er0',0xaa),('CCR_C',0),('er3',0x1a)), 
                'tests':(('er3',0x90),('CCR_H',0),('CCR_N',0),('CCR_Z',0),('CCR_V',0),('CCR_C',0)) },
            {'setup':(('er0',0xab),('CCR_C',0),('er3',0xb0)), 
                'tests':(('er3',0xfffffffb),('CCR_H',1),('CCR_N',1),('CCR_Z',0),('CCR_V',0),('CCR_C',1)) },
            ) ),
        ( '1b83', 0x4560, 'subs #2, er3', 0, () ),
        ( '1b93', 0x4560, 'subs #4, er3', 0, () ),
        ( '1b53', 0x4560, 'dec.w #1, r3', IF_W, () ),
        ( '1bf3', 0x4560, 'dec.l #2, er3', IF_L, () ),
        '''

# temp scratch: generated these while testing
['0de803c0','8de903c0','ade903c0','2de803c0','1de803c0','3de803c0','9de903c0','bde903c0',]
['srsdb.w sp, svc',
         'srsia.w sp, svc',
          'srsia.w sp!, svc',
           'srsdb.w sp!, svc',
            'rfedb.w sp',
             'rfedb.w sp!',
              'rfeia.w sp',
               'rfeia.w sp!']

import struct
def getThumbStr(val, val2):
    return struct.pack('<HH', val, val2)

def getThumbOps(vw, numtups):
    return [vw.arch.archParseOpcode(getThumbStr(val,val2), 1, 0x8000001) for val,val2 in numtups]

# more scratch
#ops = getThumbOps(vw, [(0x0df7,0x03b0),(0x00f7,0xaa8a),(0xf7fe,0xbdbc),(0xf385,0x8424)]) ;op=ops[0];ops
#ops = getThumbOps(vw, [(0xf386,0x8424),(0xf385,0x8400)]) ;op=ops[0];ops
#Out[1]: [msr.w APSR_s, r5]

# testing PSR stuff - not actually working unittesting...
import envi.memcanvas as ememc
import envi.archs.thumb16.disasm as eatd
oper = eatd.ArmPgmStatRegOper(1,15)
#smc = ememc.StringMemoryCanvas(vw)
#oper.render(smc, None, 0)
#smc.strval == 'SPSR_fcxs'
###############################################33

class ArmInstructionSet(unittest.TestCase):
    def test_msr(self):
        # test the MSR instruction
        import envi.archs.arm as e_arm;reload(e_arm)
        am=e_arm.ArmModule()
        op = am.archParseOpcode('d3f021e3'.decode('hex'))
        self.assertEqual('msr CPSR_c, #0xd3', repr(op))

    def test_envi_arm_operands(self):
        vw = vivisect.VivWorkspace()
        vw.setMeta("Architecture", "arm")
        vw.addMemoryMap(0, 7, 'firmware', '\xff' * 16384*1024)
        #vw.addMemoryMap(0x400000, 7, 'firmware', '\xff' * 16384*1024)
        vw.addMemoryMap(0xbfb00000, 7, 'firmware', '\xfe' * 16384*1024)


        # testing the ArmImmOffsetOper

        # ldr r3, [#0xbfb00010]
        emu = vw.getEmulator()
        emu.writeMemory(0xbfb00010, "abcdef98".decode('hex'))
        op = vw.arch.archParseOpcode('\x080\x9f\xe5', va=0xbfb00000)
        print repr(op)
        print hex(op.getOperValue(1, emu))

        self.assertEqual(hex(0x98efcdab), hex(op.getOperValue(1, emu)))



        # ldr r3, [r11, #0x8]!
        emu.writeMemory(0xbfb00018, "FFEEDDCC".decode('hex'))
        emu.setRegister(11, 0xbfb00010)
        op = vw.arch.archParseOpcode('\x08\x30\xbb\xe5', va=0xbfb00000)
        value = op.getOperValue(1, emu, update=True)
        print repr(op)
        print hex(value)
        print hex(emu.getRegister(11))

        self.assertEqual(hex(0xccddeeff), hex(value))


        
        # ldr r3, [r11], #0x8
        emu.writeMemory(0xbfb00010, "ABCDEF10".decode('hex'))
        emu.setRegister(11, 0xbfb00010)
        op = vw.arch.archParseOpcode('\x08\x30\x9b\xe4', va=0xbfb00000)
        value = op.getOperValue(1, emu, update=True)
        print repr(op)
        print hex(value)
        print hex(emu.getRegister(11))

        self.assertEqual(hex(0xbfb00018), hex(emu.getRegister(11)))
        self.assertEqual(hex(0x10efcdab), hex(value))


        # ldr r3, [r11], #-0x8
        emu.writeMemory(0xbfb00010, "ABCDEF10".decode('hex'))
        emu.setRegister(11, 0xbfb00010)
        op = vw.arch.archParseOpcode('\x08\x30\x1b\xe4', va=0xbfb00000)
        value = op.getOperValue(1, emu, update=True)
        print repr(op)
        print hex(value)
        print hex(emu.getRegister(11))

        self.assertEqual(hex(0xbfb00008), hex(emu.getRegister(11)))
        self.assertEqual(hex(0x10efcdab), hex(value))


        # testing the ArmScaledOffsetOper
        
        # ldr r2, [r10, r2 ]
        emu = vw.getEmulator()
        op = vw.arch.archParseOpcode('02209ae7'.decode('hex'), va=0xbfb00000)
        emu.setRegister(10, 0xbfb00008)
        emu.setRegister(2,  8)
        emu.writeMemory(0xbfb00010, "abcdef98".decode('hex'))
        print repr(op)
        print hex(op.getOperValue(1, emu))

        self.assertEqual(hex(0x98efcdab), hex(op.getOperValue(1, emu)))
        self.assertEqual(hex(0xbfb00008), hex(emu.getRegister(10)))
        self.assertEqual(hex(8), hex(emu.getRegister(2)))



        # ldr r2, [r10], r2 
        emu.setRegister(10, 0xbfb00008)
        emu.setRegister(2,  8)
        emu.writeMemory(0xbfb00008, "ABCDEF10".decode('hex'))
        op = vw.arch.archParseOpcode('02209ae6'.decode('hex'), va=0xbfb00000)
        value = op.getOperValue(1, emu, update=True)
        print repr(op)
        print hex(value)
        print hex(emu.getRegister(10))

        self.assertEqual(hex(0xbfb00010), hex(emu.getRegister(10)))
        self.assertEqual(hex(0x10efcdab), hex(value))

        
        
        # ldr r2, [r10, -r2 ]!
        emu.writeMemory(0xbfb00018, "FFEEDDCC".decode('hex'))
        emu.writeMemory(0xbfb00010, "55555555".decode('hex'))
        emu.writeMemory(0xbfb00008, "f000f000".decode('hex'))
        emu.setRegister(10, 0xbfb00010)
        emu.setRegister(2,  8)
        op = vw.arch.archParseOpcode('02203ae7'.decode('hex'), va=0xbfb00000)
        value = op.getOperValue(1, emu, update=True)
        print repr(op)
        print hex(value)
        print hex(emu.getRegister(10))

        self.assertEqual(hex(0x00f000f0), hex(value))
        self.assertEqual(hex(0xbfb00008), hex(emu.getRegister(10)))


        
        # ldr r2, [r10, r2 ]!
        emu.writeMemory(0xbfb00018, "FFEEDDCC".decode('hex'))
        emu.writeMemory(0xbfb00010, "55555555".decode('hex'))
        emu.setRegister(10, 0xbfb00010)
        emu.setRegister(2,  8)
        op = vw.arch.archParseOpcode('0220bae7'.decode('hex'), va=0xbfb00000)
        value = op.getOperValue(1, emu, update=True)
        print repr(op)
        print hex(value)
        print hex(emu.getRegister(10))

        self.assertEqual(hex(0xccddeeff), hex(value))
        self.assertEqual(hex(0xbfb00018), hex(emu.getRegister(10)))

        # Scaled with shifts/roll
        # ldr r2, [r10, r2 lsr #32]
        emu = vw.getEmulator()
        op = vw.arch.archParseOpcode('22209ae7'.decode('hex'), va=0xbfb00000)
        emu.setRegister(10, 0xbfb00008)
        emu.setRegister(2,  8)
        emu.writeMemory(0xbfb00010, "abcdef98".decode('hex'))
        print repr(op)
        print hex(op.getOperValue(1, emu))

        self.assertEqual(hex(0xbfb00008), hex(emu.getRegister(10)))
        self.assertEqual(hex(0x98efcdab), hex(op.getOperValue(1, emu)))
        self.assertEqual(hex(8), hex(emu.getRegister(2)))



        # ldr r2, [r10], r2 
        emu.setRegister(10, 0xbfb00008)
        emu.setRegister(2,  8)
        emu.writeMemory(0xbfb00008, "ABCDEF10".decode('hex'))
        op = vw.arch.archParseOpcode('22219ae6'.decode('hex'), va=0xbfb00000)
        value = op.getOperValue(1, emu, update=True)
        print repr(op)
        print hex(value)
        print hex(emu.getRegister(10))

        self.assertEqual(hex(0xbfb00010), hex(emu.getRegister(10)))
        self.assertEqual(hex(0x98efcdab), hex(op.getOperValue(1, emu)))
        self.assertEqual(hex(8), hex(emu.getRegister(2)))
        self.assertEqual(hex(0x10efcdab), hex(value))

        
        


        
    def test_envi_arm_assorted_instrs(self):

        #archmod = envi.getArchModule("h8")
        vw = vivisect.VivWorkspace()
        vw.setMeta("Architecture", "arm")
        vw.addMemoryMap(0, 7, 'firmware', '\xff' * 16384*1024)
        vw.addMemoryMap(0x400000, 7, 'firmware', '\xff' * 16384*1024)
        emu = vw.getEmulator()
        emu.logread = emu.logwrite = True

        badcount = 0
        goodcount = 0

        #emu = archmod.getEmulator()
        #emu.addMemoryMap(0, 7, 'firmware', '\xff' * 16384*1024)
        #emu.addMemoryMap(0x400000, 7, 'firmware', '\xff' * 16384*1024)

        for bytez, va, reprOp, iflags, emutests in instrs:
            op = vw.arch.archParseOpcode(bytez.decode('hex'), 0, va)
            redoprepr = repr(op).replace(' ','').lower()
            redgoodop = reprOp.replace(' ','').lower()
            if redoprepr != redgoodop:
                raise Exception("FAILED to decode instr:  %.8x %s - should be: %s  - is: %s" % \
                         ( va, bytez, reprOp, repr(op) ) )
                badcount += 1
                raise Exception("FAILED to decode instr:  %.8x %s - should be: %s  - is: %s" % \
                         ( va, bytez, reprOp, repr(op) ) )
            self.assertEqual((bytez, redoprepr, op.iflags), (bytez, redgoodop, iflags))

            # test some things
            if not len(emutests):
                # if we don't have tests, let's just run it in the emulator anyway and see if things break
                if not self.validateEmulation(emu, op, (), ()):
                    goodcount += 1
                else:
                    raise Exception( "FAILED emulation:  %s" % op )
                    badcount += 1

            else:
                for tdata in emutests:  # dict with 'setup' and 'tests' as keys
                    setup = tdata.get('setup', ())
                    tests = tdata.get('tests', ())
                    if not self.validateEmulation(emu, op, setup, tests):
                        goodcount += 1
                    else:
                        raise Exception( "FAILED emulation:  %s" % op )
                        badcount += 1

        #op = vw.arch.archParseOpcode('12c3'.decode('hex'))
        ##rotl.b #2, r3h
        ##print( op, hex(0x7a) )
        #emu.setRegisterByName('r3h', 0x7a)
        #emu.executeOpcode(op)
        ##print( hex(emu.getRegisterByName('r3h')), emu.getFlag(CCR_C) )
        ##0xef False

    def test_envi_arm_thumb_switches(self):
        pass

    def validateEmulation(self, emu, op, setters, tests):
        # first set any environment stuff necessary
        ## defaults
        emu.setRegister(REG_ER3, 0x414141)
        emu.setRegister(REG_ER4, 0x444444)
        emu.setRegister(REG_ER5, 0x454545)
        emu.setRegister(REG_ER6, 0x464646)
        emu.setRegister(REG_SP, 0x450000)

        ## special cases
        for tgt, val in setters:
            try:
                # try register first
                emu.setRegisterByName(tgt, val)
            except e_reg.InvalidRegisterName, e:
                # it's not a register
                if type(tgt) == str and tgt.startswith("CCR_"):
                    # it's a flag
                    emu.setFlag(eval(tgt), val)
                elif type(tgt) in (long, int):
                    # it's an address
                    emu.writeMemValue(tgt, val, 1) # limited to 1-byte writes currently
                else:
                    raise Exception( "Funkt up Setting:  %s = 0x%x" % (tgt, val) )

        emu.executeOpcode(op)

        # do tests
        success = 1
        for tgt, val in tests:
            try:
                # try register first
                testval = emu.getRegisterByName(tgt)
                if testval == val:
                    #print("SUCCESS: %s  ==  0x%x" % (tgt, val))
                    continue
                success = 0
                raise Exception("FAILED(reg): %s  !=  0x%x (observed: 0x%x)" % (tgt, val, testval))

            except e_reg.InvalidRegisterName, e:
                # it's not a register
                if type(tgt) == str and tgt.startswith("CCR_"):
                    # it's a flag
                    testval = emu.getFlag(eval(tgt)) 
                    if testval == val:
                        #print("SUCCESS: %s  ==  0x%x" % (tgt, val))
                        continue
                    success = 0
                    raise Exception("FAILED(flag): %s  !=  0x%x (observed: 0x%x)" % (tgt, val, testval))

                elif type(tgt) in (long, int):
                    # it's an address
                    testval = emu.readMemValue(tgt, 1)
                    if testval == val:
                        #print("SUCCESS: 0x%x  ==  0x%x" % (tgt, val))
                        continue
                    success = 0
                    raise Exception("FAILED(mem): 0x%x  !=  0x%x (observed: 0x%x)" % (tgt, val, testval))

                else:
                    raise Exception( "Funkt up test: %s == %s" % (tgt, val) )

        # do some read/write tracking/testing
        #print emu.curpath
        if len(emu.curpath[2]['readlog']):
            outstr = emu.curpath[2]['readlog']
            if len(outstr) > 10000: outstr = outstr[:10000]
            #print( repr(op) + '\t\tRead: ' + repr(outstr) )
        if len(emu.curpath[2]['writelog']):
            outstr = emu.curpath[2]['writelog']
            if len(outstr) > 10000: outstr = outstr[:10000]
            #print( repr(op) + '\t\tWrite: '+ repr(outstr) )
        emu.curpath[2]['readlog'] = []
        emu.curpath[2]['writelog'] = []

        return not success
"""
def generateTestInfo(ophexbytez='6e'):
    '''
    Helper function to help generate test cases that can easily be copy-pasta
    '''
    h8 = e_h8.H8Module()
    opbytez = ophexbytez
    op = h8.archParseOpcode(opbytez.decode('hex'), 0, 0x4000)
    print( "opbytez = '%s'\noprepr = '%s'"%(opbytez,repr(op)) )
    opvars=vars(op)
    opers = opvars.pop('opers')
    print( "opcheck = ",repr(opvars) )

    opersvars = []
    for x in range(len(opers)):
        opervars = vars(opers[x])
        opervars.pop('_dis_regctx')
        opersvars.append(opervars)

    print( "opercheck = %s" % (repr(opersvars)) )



raw_instrs = [
    ]


def genDPArm():
    out = []
    for z in range(16):
        for x in range(32):
            y = 0xe0034567 + (x<<20) + (z<<4)
            try:
                bytez = struct.pack("<I", y)
                out.append(bytez)
                op = vw.arch.archParseOpcode(bytez)
                print "%x %s" % (y, op)

            except:
                print "%x error" % y

    file('dpArmTest','w').write(''.join(out))

'''
674503E0                    AND             R4, R3, R7,ROR#10
674513E0                    ANDS            R4, R3, R7,ROR#10
674523E0                    EOR             R4, R3, R7,ROR#10
674533E0                    EORS            R4, R3, R7,ROR#10
674543E0                    SUB             R4, R3, R7,ROR#10
674553E0                    SUBS            R4, R3, R7,ROR#10
674563E0                    RSB             R4, R3, R7,ROR#10
674573E0                    RSBS            R4, R3, R7,ROR#10
674583E0                    ADD             R4, R3, R7,ROR#10
674593E0                    ADDS            R4, R3, R7,ROR#10
6745A3E0                    ADC             R4, R3, R7,ROR#10
6745B3E0                    ADCS            R4, R3, R7,ROR#10
6745C3E0                    SBC             R4, R3, R7,ROR#10
6745D3E0                    SBCS            R4, R3, R7,ROR#10
6745E3E0                    RSC             R4, R3, R7,ROR#10
6745F3E0                    RSCS            R4, R3, R7,ROR#10
674513E1                    TST             R3, R7,ROR#10
674533E1                    TEQ             R3, R7,ROR#10
674553E1                    CMP             R3, R7,ROR#10
674573E1                    CMN             R3, R7,ROR#10
674583E1                    ORR             R4, R3, R7,ROR#10
674593E1                    ORRS            R4, R3, R7,ROR#10
6745A3E1                    MOV             R4, R7,ROR#10
6745B3E1                    MOVS            R4, R7,ROR#10
6745C3E1                    BIC             R4, R3, R7,ROR#10
6745D3E1                    BICS            R4, R3, R7,ROR#10
6745E3E1                    MVN             R4, R7,ROR#10
6745F3E1                    MVNS            R4, R7,ROR#10
774503E0                    AND             R4, R3, R7,ROR R5
774513E0                    ANDS            R4, R3, R7,ROR R5
774523E0                    EOR             R4, R3, R7,ROR R5
774533E0                    EORS            R4, R3, R7,ROR R5
774543E0                    SUB             R4, R3, R7,ROR R5
774553E0                    SUBS            R4, R3, R7,ROR R5
774563E0                    RSB             R4, R3, R7,ROR R5
774573E0                    RSBS            R4, R3, R7,ROR R5
774583E0                    ADD             R4, R3, R7,ROR R5
774593E0                    ADDS            R4, R3, R7,ROR R5
7745A3E0                    ADC             R4, R3, R7,ROR R5
7745B3E0                    ADCS            R4, R3, R7,ROR R5
7745C3E0                    SBC             R4, R3, R7,ROR R5
7745D3E0                    SBCS            R4, R3, R7,ROR R5
7745E3E0                    RSC             R4, R3, R7,ROR R5
7745F3E0                    RSCS            R4, R3, R7,ROR R5
774513E1                    TST             R3, R7,ROR R5
774523E1                    BKPT            0x3457
774533E1                    TEQ             R3, R7,ROR R5
774543E1                    HVC             #0x3457
774553E1                    CMP             R3, R7,ROR R5
774563E1                    SMC             #0x3457
774573E1                    CMN             R3, R7,ROR R5
774583E1                    ORR             R4, R3, R7,ROR R5
774593E1                    ORRS            R4, R3, R7,ROR R5
7745A3E1                    MOV             R4, R7,ROR R5
7745B3E1                    MOVS            R4, R7,ROR R5
7745C3E1                    BIC             R4, R3, R7,ROR R5
7745D3E1                    BICS            R4, R3, R7,ROR R5
7745E3E1                    MVN             R4, R7,ROR R5
7745F3E1                    MVNS            R4, R7,ROR R5
874503E0                    AND             R4, R3, R7,LSL#11
874513E0                    ANDS            R4, R3, R7,LSL#11
874523E0                    EOR             R4, R3, R7,LSL#11
874533E0                    EORS            R4, R3, R7,LSL#11
874543E0                    SUB             R4, R3, R7,LSL#11
874553E0                    SUBS            R4, R3, R7,LSL#11
874563E0                    RSB             R4, R3, R7,LSL#11
874573E0                    RSBS            R4, R3, R7,LSL#11
874583E0                    ADD             R4, R3, R7,LSL#11
874593E0                    ADDS            R4, R3, R7,LSL#11
8745A3E0                    ADC             R4, R3, R7,LSL#11
8745B3E0                    ADCS            R4, R3, R7,LSL#11
8745C3E0                    SBC             R4, R3, R7,LSL#11
8745D3E0                    SBCS            R4, R3, R7,LSL#11
8745E3E0                    RSC             R4, R3, R7,LSL#11
8745F3E0                    RSCS            R4, R3, R7,LSL#11
874503E1                    SMLABB          R3, R7, R5, R4
874513E1                    TST             R3, R7,LSL#11
874523E1                    SMLAWB          R3, R7, R5, R4
874533E1                    TEQ             R3, R7,LSL#11
874543E1                    SMLALBB         R4, R3, R7, R5
874553E1                    CMP             R3, R7,LSL#11
874563E1                    SMULBB          R3, R7, R5
874573E1                    CMN             R3, R7,LSL#11
874583E1                    ORR             R4, R3, R7,LSL#11
874593E1                    ORRS            R4, R3, R7,LSL#11
8745A3E1                    MOV             R4, R7,LSL#11
8745B3E1                    MOVS            R4, R7,LSL#11
8745C3E1                    BIC             R4, R3, R7,LSL#11
8745D3E1                    BICS            R4, R3, R7,LSL#11
8745E3E1                    MVN             R4, R7,LSL#11
8745F3E1                    MVNS            R4, R7,LSL#11
974523E0                    MLA             R3, R7, R5, R4
974533E0                    MLAS            R3, R7, R5, R4
974543E0                    UMAAL           R4, R3, R7, R5
974553E0                    UMAALS          R4, R3, R7, R5
974563E0                    MLS             R3, R7, R5, R4
974573E0                    MLSS            R3, R7, R5, R4
974583E0                    UMULL           R4, R3, R7, R5
974593E0                    UMULLS          R4, R3, R7, R5
9745A3E0                    UMLAL           R4, R3, R7, R5
9745B3E0                    UMLALS          R4, R3, R7, R5
9745C3E0                    SMULL           R4, R3, R7, R5
9745D3E0                    SMULLS          R4, R3, R7, R5
9745E3E0                    SMLAL           R4, R3, R7, R5
9745F3E0                    SMLALS          R4, R3, R7, R5
974503E1                    TST             R3, R7,LSL R5
974513E1                    TST             R3, R7,LSL R5
974523E1                    TEQ             R3, R7,LSL R5
974533E1                    TEQ             R3, R7,LSL R5
974543E1                    CMP             R3, R7,LSL R5
974553E1                    CMP             R3, R7,LSL R5
974563E1                    CMN             R3, R7,LSL R5
974573E1                    CMN             R3, R7,LSL R5
974583E1                    ORR             R4, R3, R7,LSL R5
974593E1                    ORRS            R4, R3, R7,LSL R5
9745A3E1                    MOV             R4, R7,LSL R5
9745B3E1                    MOVS            R4, R7,LSL R5
9745C3E1                    BIC             R4, R3, R7,LSL R5
9745D3E1                    BICS            R4, R3, R7,LSL R5
9745E3E1                    MVN             R4, R7,LSL R5
9745F3E1                    MVNS            R4, R7,LSL R5
A74503E0                    AND             R4, R3, R7,LSR#11
A74513E0                    ANDS            R4, R3, R7,LSR#11
A74523E0                    EOR             R4, R3, R7,LSR#11
A74533E0                    EORS            R4, R3, R7,LSR#11
A74543E0                    SUB             R4, R3, R7,LSR#11
A74553E0                    SUBS            R4, R3, R7,LSR#11
A74563E0                    RSB             R4, R3, R7,LSR#11
A74573E0                    RSBS            R4, R3, R7,LSR#11
A74583E0                    ADD             R4, R3, R7,LSR#11
A74593E0                    ADDS            R4, R3, R7,LSR#11
A745A3E0                    ADC             R4, R3, R7,LSR#11
A745B3E0                    ADCS            R4, R3, R7,LSR#11
A745C3E0                    SBC             R4, R3, R7,LSR#11
A745D3E0                    SBCS            R4, R3, R7,LSR#11
A745E3E0                    RSC             R4, R3, R7,LSR#11
A745F3E0                    RSCS            R4, R3, R7,LSR#11
A74503E1                    SMLATB          R3, R7, R5, R4
A74513E1                    TST             R3, R7,LSR#11
A74523E1                    SMULWB          R3, R7, R5
A74533E1                    TEQ             R3, R7,LSR#11
A74543E1                    SMLALTB         R4, R3, R7, R5
A74553E1                    CMP             R3, R7,LSR#11
A74563E1                    SMULTB          R3, R7, R5
A74573E1                    CMN             R3, R7,LSR#11
A74583E1                    ORR             R4, R3, R7,LSR#11
A74593E1                    ORRS            R4, R3, R7,LSR#11
A745A3E1                    MOV             R4, R7,LSR#11
A745B3E1                    MOVS            R4, R7,LSR#11
A745C3E1                    BIC             R4, R3, R7,LSR#11
A745D3E1                    BICS            R4, R3, R7,LSR#11
A745E3E1                    MVN             R4, R7,LSR#11
A745F3E1                    MVNS            R4, R7,LSR#11
B74503E0                    STRH            R4, [R3],-R7
B74513E0                    LDRH            R4, [R3],-R7
B74523E0                    STRHT           R4, [R3],-R7
B74533E0                    LDRHT           R4, [R3],-R7
B74543E0                    STRH            R4, [R3],#-0x57
B74553E0                    LDRH            R4, [R3],#-0x57
B74563E0                    STRHT           R4, [R3],#-0x57
B74573E0                    LDRHT           R4, [R3],#-0x57
B74583E0                    STRH            R4, [R3],R7
B74593E0                    LDRH            R4, [R3],R7
B745A3E0                    STRHT           R4, [R3],R7
B745B3E0                    LDRHT           R4, [R3],R7
B745C3E0                    STRH            R4, [R3],#0x57
B745D3E0                    LDRH            R4, [R3],#0x57
B745E3E0                    STRHT           R4, [R3],#0x57
B745F3E0                    LDRHT           R4, [R3],#0x57
B74503E1                    STRH            R4, [R3,-R7]
B74513E1                    LDRH            R4, [R3,-R7]
B74523E1                    STRH            R4, [R3,-R7]!
B74533E1                    LDRH            R4, [R3,-R7]!
B74543E1                    STRH            R4, [R3,#-0x57]
B74553E1                    LDRH            R4, [R3,#-0x57]
B74563E1                    STRH            R4, [R3,#-0x57]!
B74573E1                    LDRH            R4, [R3,#-0x57]!
B74583E1                    STRH            R4, [R3,R7]
B74593E1                    LDRH            R4, [R3,R7]
B745A3E1                    STRH            R4, [R3,R7]!
B745B3E1                    LDRH            R4, [R3,R7]!
B745C3E1                    STRH            R4, [R3,#0x57]
B745D3E1                    LDRH            R4, [R3,#0x57]
B745E3E1                    STRH            R4, [R3,#0x57]!
B745F3E1                    LDRH            R4, [R3,#0x57]!
C74503E0                    AND             R4, R3, R7,ASR#11
C74513E0                    ANDS            R4, R3, R7,ASR#11
C74523E0                    EOR             R4, R3, R7,ASR#11
C74533E0                    EORS            R4, R3, R7,ASR#11
C74543E0                    SUB             R4, R3, R7,ASR#11
C74553E0                    SUBS            R4, R3, R7,ASR#11
C74563E0                    RSB             R4, R3, R7,ASR#11
C74573E0                    RSBS            R4, R3, R7,ASR#11
C74583E0                    ADD             R4, R3, R7,ASR#11
C74593E0                    ADDS            R4, R3, R7,ASR#11
C745A3E0                    ADC             R4, R3, R7,ASR#11
C745B3E0                    ADCS            R4, R3, R7,ASR#11
C745C3E0                    SBC             R4, R3, R7,ASR#11
C745D3E0                    SBCS            R4, R3, R7,ASR#11
C745E3E0                    RSC             R4, R3, R7,ASR#11
C745F3E0                    RSCS            R4, R3, R7,ASR#11
C74503E1                    SMLABT          R3, R7, R5, R4
C74513E1                    TST             R3, R7,ASR#11
C74523E1                    SMLAWT          R3, R7, R5, R4
C74533E1                    TEQ             R3, R7,ASR#11
C74543E1                    SMLALBT         R4, R3, R7, R5
C74553E1                    CMP             R3, R7,ASR#11
C74563E1                    SMULBT          R3, R7, R5
C74573E1                    CMN             R3, R7,ASR#11
C74583E1                    ORR             R4, R3, R7,ASR#11
C74593E1                    ORRS            R4, R3, R7,ASR#11
C745A3E1                    MOV             R4, R7,ASR#11
C745B3E1                    MOVS            R4, R7,ASR#11
C745C3E1                    BIC             R4, R3, R7,ASR#11
C745D3E1                    BICS            R4, R3, R7,ASR#11
C745E3E1                    MVN             R4, R7,ASR#11
C745F3E1                    MVNS            R4, R7,ASR#11
D74503E0                    LDRD            R4, [R3],-R7
D74513E0                    LDRSB           R4, [R3],-R7
D74523E0                    LDRTD           R4, [R3],-R7
D74533E0                    LDRSBT          R4, [R3],-R7
D74543E0                    LDRD            R4, [R3],#-0x57
D74553E0                    LDRSB           R4, [R3],#-0x57
D74563E0                    LDRTD           R4, [R3],#-0x57
D74573E0                    LDRSBT          R4, [R3],#-0x57
D74583E0                    LDRD            R4, [R3],R7
D74593E0                    LDRSB           R4, [R3],R7
D745A3E0                    LDRTD           R4, [R3],R7
D745B3E0                    LDRSBT          R4, [R3],R7
D745C3E0                    LDRD            R4, [R3],#0x57
D745D3E0                    LDRSB           R4, [R3],#0x57
D745E3E0                    LDRTD           R4, [R3],#0x57
D745F3E0                    LDRSBT          R4, [R3],#0x57
D74503E1                    LDRD            R4, [R3,-R7]
D74513E1                    LDRSB           R4, [R3,-R7]
D74523E1                    LDRD            R4, [R3,-R7]!
D74533E1                    LDRSB           R4, [R3,-R7]!
D74543E1                    LDRD            R4, [R3,#-0x57]
D74553E1                    LDRSB           R4, [R3,#-0x57]
D74563E1                    LDRD            R4, [R3,#-0x57]!
D74573E1                    LDRSB           R4, [R3,#-0x57]!
D74583E1                    LDRD            R4, [R3,R7]
D74593E1                    LDRSB           R4, [R3,R7]
D745A3E1                    LDRD            R4, [R3,R7]!
D745B3E1                    LDRSB           R4, [R3,R7]!
D745C3E1                    LDRD            R4, [R3,#0x57]
D745D3E1                    LDRSB           R4, [R3,#0x57]
D745E3E1                    LDRD            R4, [R3,#0x57]!
D745F3E1                    LDRSB           R4, [R3,#0x57]!
E74503E0                    AND             R4, R3, R7,ROR#11
E74513E0                    ANDS            R4, R3, R7,ROR#11
E74523E0                    EOR             R4, R3, R7,ROR#11
E74533E0                    EORS            R4, R3, R7,ROR#11
E74543E0                    SUB             R4, R3, R7,ROR#11
E74553E0                    SUBS            R4, R3, R7,ROR#11
E74563E0                    RSB             R4, R3, R7,ROR#11
E74573E0                    RSBS            R4, R3, R7,ROR#11
E74583E0                    ADD             R4, R3, R7,ROR#11
E74593E0                    ADDS            R4, R3, R7,ROR#11
E745A3E0                    ADC             R4, R3, R7,ROR#11
E745B3E0                    ADCS            R4, R3, R7,ROR#11
E745C3E0                    SBC             R4, R3, R7,ROR#11
E745D3E0                    SBCS            R4, R3, R7,ROR#11
E745E3E0                    RSC             R4, R3, R7,ROR#11
E745F3E0                    RSCS            R4, R3, R7,ROR#11
E74503E1                    SMLATT          R3, R7, R5, R4
E74513E1                    TST             R3, R7,ROR#11
E74523E1                    SMULWT          R3, R7, R5
E74533E1                    TEQ             R3, R7,ROR#11
E74543E1                    SMLALTT         R4, R3, R7, R5
E74553E1                    CMP             R3, R7,ROR#11
E74563E1                    SMULTT          R3, R7, R5
E74573E1                    CMN             R3, R7,ROR#11
E74583E1                    ORR             R4, R3, R7,ROR#11
E74593E1                    ORRS            R4, R3, R7,ROR#11
E745A3E1                    MOV             R4, R7,ROR#11
E745B3E1                    MOVS            R4, R7,ROR#11
E745C3E1                    BIC             R4, R3, R7,ROR#11
E745D3E1                    BICS            R4, R3, R7,ROR#11
E745E3E1                    MVN             R4, R7,ROR#11
E745F3E1                    MVNS            R4, R7,ROR#11
F74503E0                    STRD            R4, [R3],-R7
F74513E0                    LDRSH           R4, [R3],-R7
F74523E0                    STRTD           R4, [R3],-R7
F74533E0                    LDRSHT          R4, [R3],-R7
F74543E0                    STRD            R4, [R3],#-0x57
F74553E0                    LDRSH           R4, [R3],#-0x57
F74563E0                    STRTD           R4, [R3],#-0x57
F74573E0                    LDRSHT          R4, [R3],#-0x57
F74583E0                    STRD            R4, [R3],R7
F74593E0                    LDRSH           R4, [R3],R7
F745A3E0                    STRTD           R4, [R3],R7
F745B3E0                    LDRSHT          R4, [R3],R7
F745C3E0                    STRD            R4, [R3],#0x57
F745D3E0                    LDRSH           R4, [R3],#0x57
F745E3E0                    STRTD           R4, [R3],#0x57
F745F3E0                    LDRSHT          R4, [R3],#0x57
F74503E1                    STRD            R4, [R3,-R7]
F74513E1                    LDRSH           R4, [R3,-R7]
F74523E1                    STRD            R4, [R3,-R7]!
F74533E1                    LDRSH           R4, [R3,-R7]!
F74543E1                    STRD            R4, [R3,#-0x57]
F74553E1                    LDRSH           R4, [R3,#-0x57]
F74563E1                    STRD            R4, [R3,#-0x57]!
F74573E1                    LDRSH           R4, [R3,#-0x57]!
F74583E1                    STRD            R4, [R3,R7]
F74593E1                    LDRSH           R4, [R3,R7]
F745A3E1                    STRD            R4, [R3,R7]!
F745B3E1                    LDRSH           R4, [R3,R7]!
F745C3E1                    STRD            R4, [R3,#0x57]
F745D3E1                    LDRSH           R4, [R3,#0x57]
F745E3E1                    STRD            R4, [R3,#0x57]!
F745F3E1                    LDRSH           R4, [R3,#0x57]!
074603E0                    AND             R4, R3, R7,LSL#12
074613E0                    ANDS            R4, R3, R7,LSL#12
074623E0                    EOR             R4, R3, R7,LSL#12
074633E0                    EORS            R4, R3, R7,LSL#12
074643E0                    SUB             R4, R3, R7,LSL#12
074653E0                    SUBS            R4, R3, R7,LSL#12
074663E0                    RSB             R4, R3, R7,LSL#12
074673E0                    RSBS            R4, R3, R7,LSL#12
074683E0                    ADD             R4, R3, R7,LSL#12
074693E0                    ADDS            R4, R3, R7,LSL#12
0746A3E0                    ADC             R4, R3, R7,LSL#12
0746B3E0                    ADCS            R4, R3, R7,LSL#12
0746C3E0                    SBC             R4, R3, R7,LSL#12
0746D3E0                    SBCS            R4, R3, R7,LSL#12
0746E3E0                    RSC             R4, R3, R7,LSL#12
0746F3E0                    RSCS            R4, R3, R7,LSL#12
074603E1                    TST             R3, R7,LSL#12
074613E1                    TST             R3, R7,LSL#12
074623E1                    TEQ             R3, R7,LSL#12
074633E1                    TEQ             R3, R7,LSL#12
074643E1                    CMP             R3, R7,LSL#12
074653E1                    CMP             R3, R7,LSL#12
074663E1                    CMN             R3, R7,LSL#12
074673E1                    CMN             R3, R7,LSL#12
074683E1                    ORR             R4, R3, R7,LSL#12
074693E1                    ORRS            R4, R3, R7,LSL#12
0746A3E1                    MOV             R4, R7,LSL#12
0746B3E1                    MOVS            R4, R7,LSL#12
0746C3E1                    BIC             R4, R3, R7,LSL#12
0746D3E1                    BICS            R4, R3, R7,LSL#12
0746E3E1                    MVN             R4, R7,LSL#12
0746F3E1                    MVNS            R4, R7,LSL#12
174603E0                    AND             R4, R3, R7,LSL R6
174613E0                    ANDS            R4, R3, R7,LSL R6
174623E0                    EOR             R4, R3, R7,LSL R6
174633E0                    EORS            R4, R3, R7,LSL R6
174643E0                    SUB             R4, R3, R7,LSL R6
174653E0                    SUBS            R4, R3, R7,LSL R6
174663E0                    RSB             R4, R3, R7,LSL R6
174673E0                    RSBS            R4, R3, R7,LSL R6
174683E0                    ADD             R4, R3, R7,LSL R6
174693E0                    ADDS            R4, R3, R7,LSL R6
1746A3E0                    ADC             R4, R3, R7,LSL R6
1746B3E0                    ADCS            R4, R3, R7,LSL R6
1746C3E0                    SBC             R4, R3, R7,LSL R6
1746D3E0                    SBCS            R4, R3, R7,LSL R6
1746E3E0                    RSC             R4, R3, R7,LSL R6
1746F3E0                    RSCS            R4, R3, R7,LSL R6
174603E1                    TST             R3, R7,LSL R6
174613E1                    TST             R3, R7,LSL R6
174623E1                    BX              R7
174643E1                    CMP             R3, R7,LSL R6
174653E1                    CMP             R3, R7,LSL R6
174663E1                    CLZ             R4, R7
174673E1                    CMN             R3, R7,LSL R6
174683E1                    ORR             R4, R3, R7,LSL R6
174693E1                    ORRS            R4, R3, R7,LSL R6
1746A3E1                    MOV             R4, R7,LSL R6
1746B3E1                    MOVS            R4, R7,LSL R6
1746C3E1                    BIC             R4, R3, R7,LSL R6
1746D3E1                    BICS            R4, R3, R7,LSL R6
1746E3E1                    MVN             R4, R7,LSL R6
1746F3E1                    MVNS            R4, R7,LSL R6
274603E0                    AND             R4, R3, R7,LSR#12
274613E0                    ANDS            R4, R3, R7,LSR#12
274623E0                    EOR             R4, R3, R7,LSR#12
274633E0                    EORS            R4, R3, R7,LSR#12
274643E0                    SUB             R4, R3, R7,LSR#12
274653E0                    SUBS            R4, R3, R7,LSR#12
274663E0                    RSB             R4, R3, R7,LSR#12
274673E0                    RSBS            R4, R3, R7,LSR#12
274683E0                    ADD             R4, R3, R7,LSR#12
274693E0                    ADDS            R4, R3, R7,LSR#12
2746A3E0                    ADC             R4, R3, R7,LSR#12
2746B3E0                    ADCS            R4, R3, R7,LSR#12
2746C3E0                    SBC             R4, R3, R7,LSR#12
2746D3E0                    SBCS            R4, R3, R7,LSR#12
2746E3E0                    RSC             R4, R3, R7,LSR#12
2746F3E0                    RSCS            R4, R3, R7,LSR#12
274603E1                    TST             R3, R7,LSR#12
274613E1                    TST             R3, R7,LSR#12
274623E1                    BXJ             R7
274643E1                    CMP             R3, R7,LSR#12
274653E1                    CMP             R3, R7,LSR#12
274663E1                    CMN             R3, R7,LSR#12
274673E1                    CMN             R3, R7,LSR#12
274683E1                    ORR             R4, R3, R7,LSR#12
274693E1                    ORRS            R4, R3, R7,LSR#12
2746A3E1                    MOV             R4, R7,LSR#12
2746B3E1                    MOVS            R4, R7,LSR#12
2746C3E1                    BIC             R4, R3, R7,LSR#12
2746D3E1                    BICS            R4, R3, R7,LSR#12
2746E3E1                    MVN             R4, R7,LSR#12
2746F3E1                    MVNS            R4, R7,LSR#12
374603E0                    AND             R4, R3, R7,LSR R6
374613E0                    ANDS            R4, R3, R7,LSR R6
374623E0                    EOR             R4, R3, R7,LSR R6
374633E0                    EORS            R4, R3, R7,LSR R6
374643E0                    SUB             R4, R3, R7,LSR R6
374653E0                    SUBS            R4, R3, R7,LSR R6
374663E0                    RSB             R4, R3, R7,LSR R6
374673E0                    RSBS            R4, R3, R7,LSR R6
374683E0                    ADD             R4, R3, R7,LSR R6
374693E0                    ADDS            R4, R3, R7,LSR R6
3746A3E0                    ADC             R4, R3, R7,LSR R6
3746B3E0                    ADCS            R4, R3, R7,LSR R6
3746C3E0                    SBC             R4, R3, R7,LSR R6
3746D3E0                    SBCS            R4, R3, R7,LSR R6
3746E3E0                    RSC             R4, R3, R7,LSR R6
3746F3E0                    RSCS            R4, R3, R7,LSR R6
374603E1                    TST             R3, R7,LSR R6
374613E1                    TST             R3, R7,LSR R6
374623E1                    BLX             R7
374633E1                    TEQ             R3, R7,LSR R6
374643E1                    CMP             R3, R7,LSR R6
374653E1                    CMP             R3, R7,LSR R6
374663E1                    CMN             R3, R7,LSR R6
374673E1                    CMN             R3, R7,LSR R6
374683E1                    ORR             R4, R3, R7,LSR R6
374693E1                    ORRS            R4, R3, R7,LSR R6
3746A3E1                    MOV             R4, R7,LSR R6
3746B3E1                    MOVS            R4, R7,LSR R6
3746C3E1                    BIC             R4, R3, R7,LSR R6
3746D3E1                    BICS            R4, R3, R7,LSR R6
3746E3E1                    MVN             R4, R7,LSR R6
3746F3E1                    MVNS            R4, R7,LSR R6
474603E0                    AND             R4, R3, R7,ASR#12
474613E0                    ANDS            R4, R3, R7,ASR#12
474623E0                    EOR             R4, R3, R7,ASR#12
474633E0                    EORS            R4, R3, R7,ASR#12
474643E0                    SUB             R4, R3, R7,ASR#12
474653E0                    SUBS            R4, R3, R7,ASR#12
474663E0                    RSB             R4, R3, R7,ASR#12
474673E0                    RSBS            R4, R3, R7,ASR#12
474683E0                    ADD             R4, R3, R7,ASR#12
474693E0                    ADDS            R4, R3, R7,ASR#12
4746A3E0                    ADC             R4, R3, R7,ASR#12
4746B3E0                    ADCS            R4, R3, R7,ASR#12
4746C3E0                    SBC             R4, R3, R7,ASR#12
4746D3E0                    SBCS            R4, R3, R7,ASR#12
4746E3E0                    RSC             R4, R3, R7,ASR#12
4746F3E0                    RSCS            R4, R3, R7,ASR#12
474603E1                    TST             R3, R7,ASR#12
474613E1                    TST             R3, R7,ASR#12
474623E1                    TEQ             R3, R7,ASR#12
474633E1                    TEQ             R3, R7,ASR#12
474643E1                    CMP             R3, R7,ASR#12
474653E1                    CMP             R3, R7,ASR#12
474663E1                    CMN             R3, R7,ASR#12
474673E1                    CMN             R3, R7,ASR#12
474683E1                    ORR             R4, R3, R7,ASR#12
474693E1                    ORRS            R4, R3, R7,ASR#12
4746A3E1                    MOV             R4, R7,ASR#12
4746B3E1                    MOVS            R4, R7,ASR#12
4746C3E1                    BIC             R4, R3, R7,ASR#12
4746D3E1                    BICS            R4, R3, R7,ASR#12
4746E3E1                    MVN             R4, R7,ASR#12
4746F3E1                    MVNS            R4, R7,ASR#12
574603E0                    AND             R4, R3, R7,ASR R6
574613E0                    ANDS            R4, R3, R7,ASR R6
574623E0                    EOR             R4, R3, R7,ASR R6
574633E0                    EORS            R4, R3, R7,ASR R6
574643E0                    SUB             R4, R3, R7,ASR R6
574653E0                    SUBS            R4, R3, R7,ASR R6
574663E0                    RSB             R4, R3, R7,ASR R6
574673E0                    RSBS            R4, R3, R7,ASR R6
574683E0                    ADD             R4, R3, R7,ASR R6
574693E0                    ADDS            R4, R3, R7,ASR R6
5746A3E0                    ADC             R4, R3, R7,ASR R6
5746B3E0                    ADCS            R4, R3, R7,ASR R6
5746C3E0                    SBC             R4, R3, R7,ASR R6
5746D3E0                    SBCS            R4, R3, R7,ASR R6
5746E3E0                    RSC             R4, R3, R7,ASR R6
5746F3E0                    RSCS            R4, R3, R7,ASR R6
574603E1                    TST             R3, R7,ASR R6
574613E1                    TST             R3, R7,ASR R6
574623E1                    TEQ             R3, R7,ASR R6
574633E1                    TEQ             R3, R7,ASR R6
574643E1                    CMP             R3, R7,ASR R6
574653E1                    CMP             R3, R7,ASR R6
574663E1                    CMN             R3, R7,ASR R6
574673E1                    CMN             R3, R7,ASR R6
574683E1                    ORR             R4, R3, R7,ASR R6
574693E1                    ORRS            R4, R3, R7,ASR R6
5746A3E1                    MOV             R4, R7,ASR R6
5746B3E1                    MOVS            R4, R7,ASR R6
5746C3E1                    BIC             R4, R3, R7,ASR R6
5746D3E1                    BICS            R4, R3, R7,ASR R6
5746E3E1                    MVN             R4, R7,ASR R6
5746F3E1                    MVNS            R4, R7,ASR R6


# Load/store word and unsigned bytes
674503E6                    STR             R4, [R3],-R7,ROR#10
674523E6                    STRT            R4, [R3],-R7,ROR#10
674543E6                    STRB            R4, [R3],-R7,ROR#10
674563E6                    STRBT           R4, [R3],-R7,ROR#10
674583E6                    STR             R4, [R3],R7,ROR#10
6745A3E6                    STRT            R4, [R3],R7,ROR#10
6745C3E6                    STRB            R4, [R3],R7,ROR#10
6745E3E6                    STRBT           R4, [R3],R7,ROR#10
674503E7                    STR             R4, [R3,-R7,ROR#10]
674523E7                    STR             R4, [R3,-R7,ROR#10]!
674543E7                    STRB            R4, [R3,-R7,ROR#10]
674563E7                    STRB            R4, [R3,-R7,ROR#10]!
674583E7                    STR             R4, [R3,R7,ROR#10]
6745A3E7                    STR             R4, [R3,R7,ROR#10]!
6745C3E7                    STRB            R4, [R3,R7,ROR#10]
6745E3E7                    STRB            R4, [R3,R7,ROR#10]!

674503E0                    AND             R4, R3, R7,ROR#10
674513E0                    ANDS            R4, R3, R7,ROR#10
674523E0                    EOR             R4, R3, R7,ROR#10
674533E0                    EORS            R4, R3, R7,ROR#10
674543E0                    SUB             R4, R3, R7,ROR#10
674553E0                    SUBS            R4, R3, R7,ROR#10
674563E0                    RSB             R4, R3, R7,ROR#10
674573E0                    RSBS            R4, R3, R7,ROR#10
674583E0                    ADD             R4, R3, R7,ROR#10
674593E0                    ADDS            R4, R3, R7,ROR#10
6745A3E0                    ADC             R4, R3, R7,ROR#10
6745B3E0                    ADCS            R4, R3, R7,ROR#10
6745C3E0                    SBC             R4, R3, R7,ROR#10
6745D3E0                    SBCS            R4, R3, R7,ROR#10
6745E3E0                    RSC             R4, R3, R7,ROR#10
6745F3E0                    RSCS            R4, R3, R7,ROR#10
"""


def genMediaInstructionBytes():
    # Media Instructions
    out = []
    for x in range(32):
        for z in range(8):
            y = 0xe6034f17 + (x<<20) + (z<<5)
            try:
                bytez = struct.pack("<I", y)
                out.append(bytez)
                op = vw.arch.archParseOpcode(bytez)
                print "%x %s" % (y, op)

            except:
                print "%x error" % y

    file('mediaArmTest','w').write(''.join(out))

def genAdvSIMD():
    # thumb
    outthumb = []
    outarm = []
    base = 0xe0043002 # generic Adv SIMD with Vn=8, Vd=6, Vm=4 (or 4,3,2, depending)
    # thumb dp, arm dp (with both 0/1 for U)
    for option in (0xf000000, 0x2000000, 0x3000000, 0x1f000000):
        for A in range(16): # three registers of same length
            for B in range(16): # three registers of same length
                for C in range(16):
                    val = base + (A<<19) + (B<<8) + (C<<4)
                    bytez = struct.pack("<I", val)
                    outarm.append(bytez)
                    bytez = struct.pack("<HH", val>>16, val&0xffff)
                    outthumb.append(bytez)

                    #op = vw.arch.archParseOpcode(bytez)
                    #print "%x %s" % (val, op)

    out = outarm
    out.extend(outthumb)
    file('advSIMD', 'wb').write(''.join(out))




# thumb 16bit IT, CNBZ, CBZ
