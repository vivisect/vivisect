import os
import sys
import struct
import unittest
import traceback

import msgpack

import envi
import vivisect
import envi.memcanvas as e_memcanv

from binascii import unhexlify
from envi.archs.aarch64.regs import *

#this probably needs to be looked over once more to make sure all
#assembler symbols are correctly represented
GOOD_TESTS = 495588
GOOD_EMU_TESTS = 412972


class A64InstructionSet(unittest.TestCase):
    ''' main unit test with all tests to run '''
    
    def test_msr(self):     #FIXME: revamp for Aarch64
        return
        # test the MSR instruction
        am = aarch64.A64Module()
        op = am.archParseOpcode(unhexlify('d3f021e3'))
        self.assertEqual('msr CPSR_c, #0xd3', repr(op))

    def test_BigEndian(self):       #FIXME: revamp for Aarch64
        return
        am = aarch64.A64Module()
        am.setEndian(envi.ENDIAN_MSB)
        op = am.archParseOpcode(unhexlify('e321f0d3'))
        self.assertEqual('msr CPSR_c, #0xd3', repr(op))

    def test_regs(self):        #FIXME: revamp for Aarch64
        return
        self.assertEqual(rctx.getRealRegisterNameByIdx(REG_D3), 'q1')
        self.assertEqual(rctx.getRealRegisterNameByIdx(REG_S0), 'q0')
        self.assertEqual(rctx.getRealRegisterNameByIdx(REG_S1), 'q0')
        self.assertEqual(rctx.getRealRegisterNameByIdx(REG_S2), 'q0')
        self.assertEqual(rctx.getRealRegisterNameByIdx(REG_S3), 'q0')
        self.assertEqual(rctx.getRealRegisterNameByIdx(REG_S4), 'q1')

    def test_envi_aarch64_operands(self):       #FIXME: revamp for Aarch64
        return
        vw = vivisect.VivWorkspace()
        vw.setMeta("Architecture", "a64")
        vw.addMemoryMap(0, 7, 'firmware', '\xff' * 16384*1024)
        vw.addMemoryMap(0xbfb00000, 7, 'firmware', '\xfe' * 16384*1024)


        # testing the ArmImmOffsetOper

        # ldr r3, [#0xbfb00010]
        emu = vw.getEmulator()
        emu.setMeta('forrealz', True)
        emu._forrealz = True    # cause base_reg updates on certain Operands.

        emu.writeMemory(0xbfb00010, unhexlify("abcdef98"))

        opstr = struct.pack('<I', 0xe59f3008)
        op = vw.arch.archParseOpcode(opstr, va=0xbfb00000)
        #print(repr(op))
        #print(hex(op.getOperValue(1, emu)))

        self.assertEqual(hex(0x98efcdab), hex(op.getOperValue(1, emu)))

        # ldr r3, [r11, #0x8]!
        emu.writeMemory(0xbfb00018, unhexlify("FFEEDDCC"))
        emu.setRegister(11, 0xbfb00010)

        opstr = struct.pack('<I', 0xe5bb3008)
        op = vw.arch.archParseOpcode(opstr, va=0xbfb00000)

        value = op.getOperValue(1, emu)
        #print(repr(op))
        #print(hex(value))
        #print(hex(emu.getRegister(11)))

        self.assertEqual(hex(0xccddeeff), hex(value))

        # ldr r3, [r11], #0x8
        emu.writeMemory(0xbfb00010, unhexlify("ABCDEF10"))
        emu.setRegister(11, 0xbfb00010)
        
        opstr = struct.pack('<I', 0xe4bb3008)
        op = vw.arch.archParseOpcode(opstr, va=0xbfb00000)
        
        value = op.getOperValue(1, emu)
        #print(repr(op))
        #print(hex(value))
        #print(hex(emu.getRegister(11)))

        self.assertEqual(hex(0xbfb00018), hex(emu.getRegister(11)))
        self.assertEqual(hex(0x10efcdab), hex(value))


        # ldr r3, [r11], #-0x8
        emu.writeMemory(0xbfb00010, unhexlify("ABCDEF10"))
        emu.setRegister(11, 0xbfb00010)
        
        opstr = struct.pack('<I', 0xe43b3008)
        op = vw.arch.archParseOpcode(opstr, va=0xbfb00000)
        
        value = op.getOperValue(1, emu)
        #print(repr(op))
        #print(hex(value))
        #print(hex(emu.getRegister(11)))

        self.assertEqual(hex(0xbfb00008), hex(emu.getRegister(11)))
        self.assertEqual(hex(0x10efcdab), hex(value))


        # testing the ArmScaledOffsetOper
        
        # ldr r2, [r10, r2 ]
        emu = vw.getEmulator()
        emu.setMeta('forrealz', True)
        emu._forrealz = True
        
        opstr = struct.pack('<I', 0xe79a2002)
        op = vw.arch.archParseOpcode(opstr, va=0xbfb00000)
        
        emu.setRegister(10, 0xbfb00008)
        emu.setRegister(2,  8)
        emu.writeMemory(0xbfb00010, unhexlify("abcdef98"))
        #print(repr(op))
        #print(hex(op.getOperValue(1, emu)))

        self.assertEqual(hex(0x98efcdab), hex(op.getOperValue(1, emu)))
        self.assertEqual(hex(0xbfb00008), hex(emu.getRegister(10)))
        self.assertEqual(hex(8), hex(emu.getRegister(2)))



        # ldrt r2, [r10], r2 
        emu.setRegister(10, 0xbfb00008)
        emu.setRegister(2,  8)
        emu.writeMemory(0xbfb00008, unhexlify("ABCDEF10"))
        
        opstr = struct.pack('<I', 0xe6ba2002)
        op = vw.arch.archParseOpcode(opstr, va=0xbfb00000)
        
        value = op.getOperValue(1, emu)
        #print(repr(op))
        #print(hex(value))
        #print(hex(emu.getRegister(10)))

        self.assertEqual(hex(0xbfb00010), hex(emu.getRegister(10)))
        self.assertEqual(hex(0x10efcdab), hex(value))

        
        
        # ldr r2, [r10, -r2 ]!
        emu.writeMemory(0xbfb00018, unhexlify("FFEEDDCC"))
        emu.writeMemory(0xbfb00010, unhexlify("55555555"))
        emu.writeMemory(0xbfb00008, unhexlify("f000f000"))
        emu.setRegister(10, 0xbfb00010)
        emu.setRegister(2,  8)
        
        opstr = struct.pack('<I', 0xe73a2002)
        op = vw.arch.archParseOpcode(opstr, va=0xbfb00000)
        
        value = op.getOperValue(1, emu)
        #print(repr(op))
        #print(hex(value))
        #print(hex(emu.getRegister(10)))

        self.assertEqual(hex(0x00f000f0), hex(value))
        self.assertEqual(hex(0xbfb00008), hex(emu.getRegister(10)))


        
        # ldr r2, [r10, r2 ]!
        emu.writeMemory(0xbfb00018, unhexlify("FFEEDDCC"))
        emu.writeMemory(0xbfb00010, unhexlify("55555555"))
        emu.setRegister(10, 0xbfb00010)
        emu.setRegister(2,  8)
        
        opstr = struct.pack('<I', 0xe7ba2002)
        op = vw.arch.archParseOpcode(opstr, va=0xbfb00000)
        
        value = op.getOperValue(1, emu)
        #print(repr(op))
        #print(hex(value))
        #print(hex(emu.getRegister(10)))

        self.assertEqual(hex(0xccddeeff), hex(value))
        self.assertEqual(hex(0xbfb00018), hex(emu.getRegister(10)))



        # Scaled with shifts/roll
        # ldr r3, [r10, r2 lsr #2]
        emu = vw.getEmulator()
        emu.setMeta('forrealz', True)
        emu._forrealz = True
        
        opstr = struct.pack('<I', 0xe79a3122)
        op = vw.arch.archParseOpcode(opstr, va=0xbfb00000)
        
        emu.setRegister(10, 0xbfb00008)
        emu.setRegister(2,  2)
        emu.writeMemory(0xbfb00008, unhexlify("abcdef98"))
        #print(repr(op))
        #print(hex(op.getOperValue(1, emu)))

        self.assertEqual(hex(0xbfb00008), hex(emu.getRegister(10)))
        self.assertEqual(hex(0x98efcdab), hex(op.getOperValue(1, emu)))
        self.assertEqual(hex(2), hex(emu.getRegister(2)))

        emu.executeOpcode(op)

        self.assertEqual(hex(0xbfb00008), hex(emu.getRegister(10)))
        self.assertEqual(hex(0x98efcdab), hex(op.getOperValue(1, emu)))
        self.assertEqual(hex(2), hex(emu.getRegister(2)))



        # ldr r2, [r10], r2 , lsr 2
        emu.setRegister(10, 0xbfb00008)
        emu.setRegister(2,  2)
        emu.writeMemory(0xbfb00008, unhexlify("ABCDEF10"))

        opstr = struct.pack('<I', 0xe69a3122)
        op = vw.arch.archParseOpcode(opstr, va=0xbfb00000)
        
        value = op.getOperValue(1, emu)
        #print(repr(op))
        #print(hex(value))
        #print(hex(emu.getRegister(10)))

        self.assertEqual(hex(0xbfb00008), hex(emu.getRegister(10)))
        #self.assertEqual(hex(0x98efcdab), hex(op.getOperValue(1, emu)))
        self.assertEqual(hex(2), hex(emu.getRegister(2)))
        self.assertEqual(hex(0x10efcdab), hex(value))



        # testing the ArmRegOffsetOper

        # (131071, 'b2451ae1', 17760, 'ldrh r4, [r10, -r2] ', 0, ())
        # (131071, 'b2459ae1', 17760, 'ldrh r4, [r10, r2] ', 0, ())

        # ldrh r3, [r10], -r2 
        #b2451ae0 
        emu = vw.getEmulator()
        emu.setMeta('forrealz', True)
        emu._forrealz = True

        opstr = struct.pack('<I', 0xe03a30b2)
        op = vw.arch.archParseOpcode(opstr, va=0xbfb00000)

        emu.setRegister(10, 0xbfb00008)
        emu.setRegister(2,  8)
        emu.writeMemory(0xbfb00000, unhexlify("abcdef98"))
        emu.writeMemory(0xbfb00008, unhexlify("12345678"))
        #print(repr(op))
        val = op.getOperValue(1, emu)
        #print(hex(val))

        self.assertEqual(hex(0x3412), hex(val))
        self.assertEqual(hex(0xbfb00000), hex(emu.getRegister(10)))
        self.assertEqual(hex(8), hex(emu.getRegister(2)))



        # ldr r3, [r10], r2 
        # (131071, 'b2359ae0', 17760, 'ldrh r4, [r10], r2 ', 0, ())
        emu.setRegister(10, 0xbfb00008)
        emu.setRegister(2,  8)
        emu.writeMemory(0xbfb00008, unhexlify("ABCDEF10"))

        opstr = struct.pack('<I', 0xe0ba35b2)
        op = vw.arch.archParseOpcode(opstr, va=0xbfb00000)
        
        value = op.getOperValue(1, emu)
        #print(repr(op))
        #print(hex(value))
        #print(hex(emu.getRegister(10)))

        self.assertEqual(hex(0xbfb00010), hex(emu.getRegister(10)))
        self.assertEqual(hex(0xcdab), hex(value))

        
        
        # ldr r2, [r10, -r2 ]!
        # (131071, 'b2453ae1', 17760, 'ldrh r4, [r10, -r2]! ', 0, ())
        emu.writeMemory(0xbfb00018, unhexlify("FFEEDDCC"))
        emu.writeMemory(0xbfb00010, unhexlify("55555555"))
        emu.writeMemValue(0xbfb00008, 0xf030e040, 4)
        emu.setRegister(10, 0xbfb00010)
        emu.setRegister(2,  8)
        
        opstr = struct.pack('<I', 0xe13a45b2)
        op = vw.arch.archParseOpcode(opstr, va=0xbfb00000)
        
        value = op.getOperValue(1, emu)
        #print(repr(op))
        #print(hex(value))
        #print(hex(emu.getRegister(10)))

        self.assertEqual(hex(0xe040), hex(value))
        self.assertEqual(hex(0xbfb00008), hex(emu.getRegister(10)))


        
        # ldr r2, [r10, r2 ]!
        # (131071, 'b245bae1', 17760, 'ldrh r4, [r10, r2]! ', 0, ())
        emu.writeMemory(0xbfb00018, unhexlify("FFEEDDCC"))
        emu.writeMemory(0xbfb00010, unhexlify("55555555"))
        emu.setRegister(10, 0xbfb00010)
        emu.setRegister(2,  8)
        
        opstr = struct.pack('<I', 0xe1ba45b2)
        op = vw.arch.archParseOpcode(opstr, va=0xbfb00000)
        
        value = op.getOperValue(1, emu)
        #print(repr(op))
        #print(hex(value))
        #print(hex(emu.getRegister(10)))

        self.assertEqual(hex(0xeeff), hex(value))
        self.assertEqual(hex(0xbfb00018), hex(emu.getRegister(10)))

        


        
    def test_envi_aarch64_assorted_instrs(self):
        # setup initial work space for test
        vw = vivisect.VivWorkspace()
        vw.setMeta("Architecture", "a64")
        vw.setEndian(envi.ENDIAN_LSB)
        vw.addMemoryMap(0, 7, 'firmware', b'\xff' * 16384*1024)
        vw.addMemoryMap(0x400000, 7, 'firmware', b'\xff' * 16384*1024)
        emu = vw.getEmulator()
        emu.setMeta('forrealz', True)
        emu._forrealz = True
        emu.logread = emu.logwrite = True

        stats = {
                'badcount': 0,
                'goodcount': 0,
                'goodemu': 0,
                'bademu': 0,
        }

        line = 1
        dirn = os.path.dirname(__file__)
        instpath = os.path.join(dirn, 'aarch64.littleend.mpk')
        # TODO: also test the bigendian stuff
        with open(instpath, mode='rb') as fd:
            unpk = msgpack.Unpacker(fd)
            for va, bytez, reprOp, iflags, emutests in unpk:
                try:
                    self._do_test(emu, va, bytez, reprOp, iflags, emutests, stats, line)
                except Exception as e:
                    stats['badcount'] += 1

                    print("Exception while parsing %s (%s): %r" % (bytez, reprOp, e))
                    traceback.print_exc()
                line += 1

        print("Done with assorted instructions test.  DISASM: %s tests passed.  %s tests failed.  EMU: %s tests passed.  %s tests failed" % (stats['goodcount'], stats['badcount'], stats['goodemu'], stats['bademu']))

        print("Total of ", str(stats['goodcount'] + stats['badcount']) + " tests completed.")
        self.assertEqual(stats['goodcount'], GOOD_TESTS)
        self.assertEqual(stats['goodemu'], GOOD_EMU_TESTS)

    def _do_test(self, emu, va, bytez, reprOp, iflags, emutests, stats, line = 0):
            vw = emu.vw
            strcanv = e_memcanv.StringMemoryCanvas(vw)
            op = vw.arch.archParseOpcode(unhexlify(bytez), 0, va)

            # clean up and normalize generated repr and control repr
            op.render(strcanv)
            redoprepr = repr(op).replace(' ','').lower()
            redoprender = strcanv.strval.replace(' ','').lower()
            redgoodop = reprOp.replace(' ','').lower()

            while '0x0' in redoprepr:
                redoprepr = redoprepr.replace('0x0','0x')
            redoprepr = redoprepr.replace('0x','')

            while '0x0' in redgoodop:
                redgoodop = redgoodop.replace('0x0','0x')
            redgoodop = redgoodop.replace('0x','')

            while '0x0' in redoprender:
                redoprender = redoprender.replace('0x0','0x')
            redoprender = redoprender.replace('0x','')

            # do the comparison
            if redoprepr != redgoodop or redoprender != redgoodop:
                num, = struct.unpack("<I", unhexlify(bytez))
                #print(hex(num))
                #bs = bin(num)[2:].zfill(32)
                #print(bs)
                
                stats['badcount'] += 1
                
                print("%d FAILED to decode instr:  %.8x %s - should be: %s  - is: %s" % \
                        (line, va, bytez, reprOp, repr(op) ) )

                # Printing out the actual comparison for debugging
                print("Failed comparison at %.8x : \'%s\' was not equal to \'%s\' or \'%s\'" % \
                    (va, redgoodop, redoprepr, redoprender))

                print("test: %r\ngood: %r" % (redoprepr, redgoodop))

            else:
                stats['goodcount'] += 1

            # emutests:
            if not len(emutests):
                try:
                    # if we don't have special tests, let's just run it in the emulator anyway and see if things break
                    if not self.validateEmulation(emu, op, (), ()):
                        stats['goodemu'] += 1
                    else:
                        stats['bademu'] += 1
                except envi.UnsupportedInstruction:
                    #print("Instruction not in Emulator - ", repr(op))
                    stats['bademu'] += 1
                except Exception as exp:
                    print("Exception in Emulator for command - ",repr(op), bytez, reprOp)
                    print("  ",exp )
                    sys.excepthook(*sys.exc_info())
                    stats['bademu'] += 1

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
                            stats['goodcount'] += 1
                            stats['goodemu'] += 1
                        else:
                            stats['bademu'] += 1
                            raise Exception( "FAILED emulation (special case): %.8x %s - %s" % (va, bytez, op) )

                    else:
                        stats['bademu'] += 1
                        raise Exception( "FAILED special case test format bad:  Instruction test does not have a 'tests' field: %.8x %s - %s" % (va, bytez, op))

        
    def validateEmulation(self, emu, op, setters, tests, tidx=0):


        # first set any environment stuff necessary
        ## defaults
        emu.setRegister(REG_X3, 0x414141)
        emu.setRegister(REG_X4, 0x444444)
        emu.setRegister(REG_X5, 0x10)
        emu.setRegister(REG_X6, 0x464646)
        emu.setRegister(REG_X7, 0x474747)
        emu.setRegister(REG_SP, 0x450000)
        ## special cases
        # setup flags and registers
        settersrepr = '( %r )' % (', '.join(["%s=%s" % (s, hex(v)) for s,v in setters]))
        testsrepr = '( %r )' % (', '.join(["%s==%s" % (s, hex(v)) for s,v in tests]))
        for tgt, val in setters:
            try:
                # try register first
                emu.setRegisterByName(tgt, val)
            except e_reg.InvalidRegisterName as e:
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
            except e_reg.InvalidRegisterName as e:
                # it's not a register
                if type(tgt) == str and tgt.startswith("PSR_"):
                    # it's a flag
                    testval = emu.getFlag(eval(tgt))
                    if testval == val:
                        #print("SUCCESS(flag): %s  ==  0x%x" % (tgt, val))
                        success = 0
                    else:
                        raise Exception("FAILED(flag): (%r test#%d)  %s  !=  0x%x (observed: 0x%x) \n\t(setters: %r)\n\t(test: %r)" % (op, tidx, tgt, val, testval, settersrepr, testsrepr))
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
        #print(emu.curpath)
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
