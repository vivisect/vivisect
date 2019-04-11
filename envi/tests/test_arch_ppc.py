
import envi
import envi.memory as e_mem
import envi.registers as e_reg
import envi.memcanvas as e_memcanvas
import envi.memcanvas.renderers as e_rend
import envi.archs.arm as arm
import vivisect

import struct
import platform
import unittest

import arm_bit_test_adds
import arm_bit_test_cmn
import arm_bit_test_cmp
import arm_bit_test_subs

# testing PSR stuff - not actually working unittesting...
from envi import IF_RET, IF_NOFALL, IF_BRANCH, IF_CALL, IF_COND

from envi.archs.ppc.regs import *
from envi.archs.ppc.const import *
from envi.archs.ppc.disasm import *

instrs = [
        (REV_ALL_ARM, '08309fe5', 0xbfb00000, 'ldr r3, [#0xbfb00010]', 0, ()),
        (REV_ALL_ARM, '08309fe5', 0xbfb00000, 'ldr r3, [#0xbfb00010]', 0, (
            {'setup':(('r0',0xaa),('PSR_C',0),('r3',0x1a)),
                'tests':(('r3',0xfefefefe),('PSR_Q',0),('PSR_N',0),('PSR_Z',0),('PSR_V',0),('PSR_C',0)) },
            {'setup':(('r0',0xaa),('PSR_C',0),('r3',0x1a)),
                'tests':(('r3',0xfefefefe),('PSR_Q',0),('PSR_N',0),('PSR_Z',0),('PSR_V',0),('PSR_C',0)) }
        )),
        ]
import envi.memcanvas as ememc
class PpcInstructionSet(unittest.TestCase):
    def test_msr(self):
        pass


    # defaults for settings - not fully implimented and won't be so until after ARMv8 is completed.
    armTestVersion = REV_ARMv7A
    armTestOnce = True

    def test_msr(self):
        # test the MSR instruction
        am = arm.ArmModule()
        op = am.archParseOpcode('d3f021e3'.decode('hex'))
        self.assertEqual('msr CPSR_c, #0xd3', repr(op))

    def test_BigEndian(self):
        am = arm.ArmModule()
        am.setEndian(envi.ENDIAN_MSB)
        op = am.archParseOpcode('e321f0d3'.decode('hex'))
        self.assertEqual('msr CPSR_c, #0xd3', repr(op))

    def test_regs(self):
        self.assertEqual(rctx.getRealRegisterNameByIdx(REG_D3), 'q1')
        self.assertEqual(rctx.getRealRegisterNameByIdx(REG_S0), 'q0')
        self.assertEqual(rctx.getRealRegisterNameByIdx(REG_S1), 'q0')
        self.assertEqual(rctx.getRealRegisterNameByIdx(REG_S2), 'q0')
        self.assertEqual(rctx.getRealRegisterNameByIdx(REG_S3), 'q0')
        self.assertEqual(rctx.getRealRegisterNameByIdx(REG_S4), 'q1')

    def test_envi_arm_operands(self):
        vw = vivisect.VivWorkspace()
        vw.setMeta("Architecture", "arm")
        vw.addMemoryMap(0, 7, 'firmware', '\xff' * 16384*1024)
        vw.addMemoryMap(0xbfb00000, 7, 'firmware', '\xfe' * 16384*1024)


        # testing the ArmImmOffsetOper

        # ldr r3, [#0xbfb00010]
        emu = vw.getEmulator()
        emu.setMeta('forrealz', True)
        emu._forrealz = True    # cause base_reg updates on certain Operands.

        emu.writeMemory(0xbfb00010, "abcdef98".decode('hex'))

        opstr = struct.pack('<I', 0xe59f3008)
        op = vw.arch.archParseOpcode(opstr, va=0xbfb00000)
        #print repr(op)
        #print hex(op.getOperValue(1, emu))

        self.assertEqual(hex(0x98efcdab), hex(op.getOperValue(1, emu)))

    def test_envi_arm_assorted_instrs(self):
        #setup initial work space for test
        vw = vivisect.VivWorkspace()
        vw.setMeta("Architecture", "arm")
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
        
        for archz, bytez, va, reprOp, iflags, emutests in instrs:
            ranAlready = False  # support for run once only
            #itterate through architectures 
            for key in ARCH_REVS: 
                test_arch = ARCH_REVS[key]
                if ((not ranAlready) or (not self.armTestOnce)) and ((archz & test_arch & self.armTestVersion) != 0): 
                    ranAlready = True
                    #num, = struct.unpack("<I", bytez.decode('hex'))
                    #bs = bin(num)[2:].zfill(32)
                    #print bytez, bs
                    #print reprOp
                    op = vw.arch.archParseOpcode(bytez.decode('hex'), 0, va)
                    #print repr(op)
                    redoprepr = repr(op).replace(' ','').lower()
                    redgoodop = reprOp.replace(' ','').lower()
                    if redoprepr != redgoodop:
                        print  bytez,redgoodop
                        print  bytez,redoprepr
                        print
                        #print out binary representation of opcode for checking
                        num, = struct.unpack("<I", bytez.decode('hex'))
                        print hex(num)
                        bs = bin(num)[2:].zfill(32)
                        print bs
                        
                        badcount += 1
                        
                        raise Exception("%d FAILED to decode instr:  %.8x %s - should be: %s  - is: %s" % \
                                (goodcount, va, bytez, reprOp, repr(op) ) )
                        self.assertEqual((goodcount, bytez, redoprepr), (goodcount, bytez, redgoodop))

                    else:
                        goodcount += 1

                    #print bytez, op
                    if not len(emutests):
                        try:
                            # if we don't have special tests, let's just run it in the emulator anyway and see if things break
                            if not self.validateEmulation(emu, op, (), ()):
                                goodemu += 1
                            else:
                                bademu += 1
                        except envi.UnsupportedInstruction:
                            #print "Instruction not in Emulator - ", repr(op)
                            bademu += 1
                        except Exception as exp:
                            print "Exception in Emulator for command - ",repr(op), bytez, reprOp
                            print "  ",exp 
                            sys.excepthook(*sys.exc_info())
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

        
        print "Done with assorted instructions test.  DISASM: %s tests passed.  %s tests failed.  EMU: %s tests passed.  %s tests failed" % \
                (goodcount, badcount, goodemu, bademu)
        print "Total of ", str(goodcount + badcount) + " tests completed."
        self.assertEqual(goodcount, GOOD_TESTS)
        self.assertEqual(goodemu, GOOD_EMU_TESTS)

    def validateEmulation(self, emu, op, setters, tests, tidx=0):
        # first set any environment stuff necessary
        ## defaults
        emu.setRegister(REG_R3, 0x414141)
        emu.setRegister(REG_R4, 0x444444)
        emu.setRegister(REG_R5, 0x10)
        emu.setRegister(REG_R6, 0x464646)
        emu.setRegister(REG_R7, 0x474747)
        emu.setRegister(REG_SP, 0x450000)
        ## special cases
        # setup flags and registers
        settersrepr = '( %r )' % (', '.join(["%s=%s" % (s, hex(v)) for s,v in setters]))
        testsrepr = '( %r )' % (', '.join(["%s==%s" % (s, hex(v)) for s,v in tests]))
        for tgt, val in setters:
            try:
                # try register first
                emu.setRegisterByName(tgt, val)
            except e_reg.InvalidRegisterName, e:
                # it's not a register
                if type(tgt) == str and tgt.startswith("PSR_"):
                    # it's a flag
                    emu.setFlag(eval(tgt), val)
                elif type(tgt) in (long, int):
                    # it's an address
                    #For this couldn't we set a temp value equal to endian and write that? Assuming byte order is issue with this one
                    emu.writeMemValue(tgt, val, 1) # limited to 1-byte writes currently
                else:
                    raise Exception( "Funkt up Setting: (%r test#%d)  %s = 0x%x" % (op, tidx, tgt, val) )
        emu.executeOpcode(op)
        if not len(tests):
            success = 0
        else:
            success = 1
        for tgt, val in tests:
            try:
                # try register first
                testval = emu.getRegisterByName(tgt)
                if testval == val:
                    #print("SUCCESS(reg): %s  ==  0x%x" % (tgt, val))
                    success = 0
                else:  # should be an else
                    raise Exception("FAILED(reg): (%r test#%d)  %s  !=  0x%x (observed: 0x%x) \n\t(setters: %r)\n\t(test: %r)" % (op, tidx, tgt, val, testval, settersrepr, testsrepr))
            except e_reg.InvalidRegisterName, e:
                # it's not a register
                if type(tgt) == str and tgt.startswith("PSR_"):
                    # it's a flag
                    testval = emu.getFlag(eval(tgt))
                    if testval == val:
                        #print("SUCCESS(flag): %s  ==  0x%x" % (tgt, val))
                        success = 0
                    else:
                        raise Exception("FAILED(flag): (%r test#%d)  %s  !=  0x%x (observed: 0x%x) \n\t(setters: %r)\n\t(test: %r)" % (op, tidx, tgt, val, testval, settersrepr, testsrepr))
                        #raise Exception("FAILED(flag): (%r test#%d)  %s  !=  0x%x (observed: 0x%x)" % (op, tidx, tgt, val, testval))
                elif type(tgt) in (long, int):
                    # it's an address
                    testval = emu.readMemValue(tgt, 1)
                    if testval == val:
                        #print("SUCCESS(addr): 0x%x  ==  0x%x" % (tgt, val))
                        success = 0
                    raise Exception("FAILED(mem): (%r test#%d)  0x%x  !=  0x%x (observed: 0x%x) \n\t(setters: %r)\n\t(test: %r)" % (op, tidx, tgt, val, testval, settersrepr, testsrepr))

                else:
                    raise Exception( "Funkt up test (%r test#%d) : %s == %s" % (op, tidx, tgt, val) )
        
        # NOTE: Not sure how to test this to see if working
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
        
        return success

