import unittest

REV_ALL_ARM = 0 #FIXME change once we know what this is/does

class ArmInstructionSet(unittest.TestCase):
    def test_msr(self):
        # test the MSR instruction
        import envi.archs.arm as e_arm;reload(e_arm)
        am=e_arm.ArmModule()
        op = am.archParseOpcode('d3f021e3'.decode('hex'))
        self.assertEqual('msr CPSR_c, #0xd3', repr(op))

instrs = [
    #FIXME rev_all_arm

#Data processing immediate

    # PC-release addressing
    (REV_ALL_ARM, '50abcd03', 'adr x3, [#0x1479a2]', 0, ()), #adr
    (REV_ALL_ARM, 'd0abcd03', 'adrp x3, [#0x1479a2000]', 0, ()), #adrp
    
    # Add/sub (immediate)
    (REV_ALL_ARM, '113c15e3', 'add w3, w14, [#0xf05{, LSL #0}]', 0, ()), #add (shift=0b00, sf=0b0)
    (REV_ALL_ARM, '117c15e3', 'add w3, w14, [#0xf05{, LSL #12}]', 0, ()), #add (shift=0b01, sf=0b0)
    (REV_ALL_ARM, '913c15e3', 'add x3, x14, [#0xf05{, LSL #0}]', 0, ()), #add (shift=0b00, sf=0b1)
    (REV_ALL_ARM, '917c15e3', 'add x3, x14, [#0xf05{, LSL #12}]', 0, ()), #add (shift=0b01, sf=0b1)
    (REV_ALL_ARM, '313c15e3', 'adds w3, w14, [#0xf05{, LSL #0}]', 0, ()), #adds (shift=0b00, sf=0b0)
    (REV_ALL_ARM, '317c15e3', 'adds w3, w14, [#0xf05{, LSL #12}]', 0, ()), #adds (shift=0b01, sf=0b0)
    (REV_ALL_ARM, 'b13c15e3', 'adds x3, x14, [#0xf05{, LSL #0}]', 0, ()), #adds (shift=0b00, sf=0b1)
    (REV_ALL_ARM, 'b17c15e3', 'adds x3, x14, [#0xf05{, LSL #12}]', 0, ()), #adds (shift=0b01, sf=0b1)
    (REV_ALL_ARM, '513c15e3', 'sub w3, w14, [#0xf05{, LSL #0}]', 0, ()), #add (shift=0b00, sf=0b0)
    (REV_ALL_ARM, '517c15e3', 'sub w3, w14, [#0xf05{, LSL #12}]', 0, ()), #add (shift=0b01, sf=0b0)
    (REV_ALL_ARM, 'd13c15e3', 'sub x3, x14, [#0xf05{, LSL #0}]', 0, ()), #add (shift=0b00, sf=0b1)
    (REV_ALL_ARM, 'd17c15e3', 'sub x3, x14, [#0xf05{, LSL #12}]', 0, ()), #add (shift=0b01, sf=0b1)
    (REV_ALL_ARM, '713c15e3', 'subs w3, w14, [#0xf05{, LSL #0}]', 0, ()), #adds (shift=0b00, sf=0b0)
    (REV_ALL_ARM, '717c15e3', 'subs w3, w14, [#0xf05{, LSL #12}]', 0, ()), #adds (shift=0b01, sf=0b0)
    (REV_ALL_ARM, 'f13c15e3', 'subs x3, x14, [#0xf05{, LSL #0}]', 0, ()), #adds (shift=0b00, sf=0b1)
    (REV_ALL_ARM, 'f17c15e3', 'subs x3, x14, [#0xf05{, LSL #12}]', 0, ()), #adds (shift=0b01, sf=0b1)
    
    # Logical (immediate)
    
    (REV_ALL_ARM, '123bf5e3', 'and w3, w14, [#f7b]', 0, ()),    #and (32-bit variant)
    (REV_ALL_ARM, '323bf5e3', 'orr w3, w14, [#f7b]', 0, ()),    #orr (32-bit variant)
    (REV_ALL_ARM, '523bf5e3', 'eor w3, w14, [#f7b]', 0, ()),    #eor (32-bit variant)
    (REV_ALL_ARM, '723bf5e3', 'ands w3, w14, [#f7b]', 0, ()),   #ands (32-bit variant)
    (REV_ALL_ARM, '923bf5e3', 'and x3, x14, [#f7b]', 0, ()),    #and (64-bit variant)
    (REV_ALL_ARM, 'b23bf5e3', 'orr x3, x14, [#f7b]', 0, ()),    #orr (64-bit variant)
    (REV_ALL_ARM, 'd27bf5e3', 'eor x3, x14, [#1f7b]', 0, ()),   #eor (64-bit variant)
    (REV_ALL_ARM, 'f27bf5e3', 'ands x3, x14, [#1f7b]', 0, ()),  #ands (64-bit variant)
    
    # Move wide (immediate)
    
    (REV_ALL_ARM, '12a8b7e3', 'movn w3, #45bf{, LSL #10}', 0, ()), #movn (32-bit variant)
    (REV_ALL_ARM, '52a8b7e3', 'movz w3, #45bf{, LSL #10}', 0, ()), #movz (32-bit variant)
    (REV_ALL_ARM, '72a8b7e3', 'movk w3, #45bf{, LSL #10}', 0, ()), #movk (32-bit variant)
    (REV_ALL_ARM, '92a8b7e3', 'movn x3, #45bf{, LSL #10}', 0, ()), #movn (64-bit variant)
    (REV_ALL_ARM, 'd2a8b7e3', 'movz x3, #45bf{, LSL #10}', 0, ()), #movz (64-bit variant)
    (REV_ALL_ARM, 'f2a8b7e3', 'movk w3, #45bf{, LSL #10}', 0, ()), #movk (64-bit variant)
    
    # Bitfield
    
    (REV_ALL_ARM, '1338b5e3', 'sbfm w3, w14, #38, #2d', 0, ()), #sbfm (32-bit variant)
    (REV_ALL_ARM, '5338b5e3', 'bfm w3, w14, #38, #2d', 0, ()),  #bfm (32-bit variant)
    (REV_ALL_ARM, '7338b5e3', 'ubfm w3, w14, #38, #2d', 0, ()), #ubfm (32-bit variant)
    (REV_ALL_ARM, '9378b5e3', 'sbfm x3, x14, #38, #2d', 0, ()), #sbfm (64-bit variant)
    (REV_ALL_ARM, 'd378b5e3', 'bfm x3, x14, #38, #2d', 0, ()),  #bfm (64-bit variant)
    (REV_ALL_ARM, 'f378b5e3', 'ubfm w3, x14, #38, #2d', 0, ()), #ubfm (64-bit variant)
    
    # Extract
    
    (REV_ALL_ARM, '138a75e3', 'extr w3, w14, w10, #1d', 0, ()), #extr (32-bit variant)
    (REV_ALL_ARM, '93ca75e3', 'extr w3, w14, w10, #1d', 0, ()), #extr (64-bit variant)

#Branch, exception generation and system instructions

    
    # Unconditional branch (immediate)
    
    (REV_ALL_ARM, '15bf86a3', 'b 6fe1a8c', 0, ()), #b
    (REV_ALL_ARM, '95bf86a3', 'bl 6fe1a8c', 0, ()), #bl
    
    # Compare and branch (immediate)
    
    (REV_ALL_ARM, '34f8b5e3', 'cbz w3, 1f16bc', 0, ()), #cbz (32-bit variant)
    (REV_ALL_ARM, '35f8b5e3', 'cbnz w3, 1f16bc', 0, ()),#cbnz (32-bit variant)
    (REV_ALL_ARM, 'b4f8b5e3', 'cbz x3, 1f16bc', 0, ()), #cbz (64-bit variant)
    (REV_ALL_ARM, 'b5f8b5e3', 'cbnz x3, 1f16bc', 0, ()),#cbnz (64-bit variant)
    
    # Test & branch (immediate)
    
    (REV_ALL_ARM, '368f42e3', 'tbz w3, #11, e85c', 0, ()),  #tbz (b5 = 0, width spec = w)
    (REV_ALL_ARM, 'b68f42e3', 'tbz x3, #31, e85c', 0, ()),  #tbz (b5 = 1, width spec = x)
    (REV_ALL_ARM, '378f42e3', 'tbnz w3, #11, e85c', 0, ()), #tbnz (b5 = 0, width spec = w)
    (REV_ALL_ARM, 'b78f42e3', 'tbnz x3, #31, e85c', 0, ()), #tbnz (b5 = 1, width spec = x)
    
    # Conditional branch (immediate)
    
    #FIXME cond encoded in the standard way
    (REV_ALL_ARM, '54abcdef', 'b.cond 1579bc', 0, ()), #b.cond
    
    # Exception generation
    
    (REV_ALL_ARM, 'd41bade1', 'svc #dd6f', 0, ()),
    (REV_ALL_ARM, 'd41bade2', 'hvc #dd6f', 0, ()),
    (REV_ALL_ARM, 'd41bade3', 'smc #dd6f', 0, ()),
    (REV_ALL_ARM, 'd43bade0', 'brk #dd6f', 0, ()),
    (REV_ALL_ARM, 'd45bade0', 'hlt #dd6f', 0, ()),
    (REV_ALL_ARM, 'd4bbade1', 'dcps1 {#dd6f}', 0, ()),
    (REV_ALL_ARM, 'd4bbade2', 'dcps2 {#dd6f}', 0, ()),
    (REV_ALL_ARM, 'd4bbade3', 'dcps3 {#dd6f}', 0, ()),
    
    # System
    
    (REV_ALL_ARM, 'd5004abf', 'msr SPSel, #a', 0, ()),  #msr (op1 = 000, op2 = 101)
    (REV_ALL_ARM, 'd5034adf', 'msr DAIFSet, #a', 0, ()),#msr (op1 = 011, op2 = 110)
    (REV_ALL_ARM, 'd5034aff', 'msr DAIFClr, #a', 0, ()),#msr (op1 = 011, op2 = 111)
    (REV_ALL_ARM, 'd5032a1f', 'hint #50', 0, ()),       #hint
    (REV_ALL_ARM, 'd5033a5f', 'clrex #a', 0, ()),       #clrex
    (REV_ALL_ARM, 'd503319f', 'dsb OSHLD|#1', 0, ()),   #dsb (crm = 0001)
    (REV_ALL_ARM, 'd503329f', 'dsb OSHST|#2', 0, ()),   #dsb (crm = 0010)
    (REV_ALL_ARM, 'd503339f', 'dsb OSH|#3', 0, ()),     #dsb (crm = 0011)
    (REV_ALL_ARM, 'd503359f', 'dsb NSHLD|#5', 0, ()),   #dsb (crm = 0101)
    (REV_ALL_ARM, 'd503369f', 'dsb NSHST|#6', 0, ()),   #dsb (crm = 0110)
    (REV_ALL_ARM, 'd503379f', 'dsb NSH|#7', 0, ()),     #dsb (crm = 0111)
    (REV_ALL_ARM, 'd503399f', 'dsb ISHLD|#9', 0, ()),   #dsb (crm = 1001)
    (REV_ALL_ARM, 'd5033a9f', 'dsb ISHST|#a', 0, ()),   #dsb (crm = 1010)
    (REV_ALL_ARM, 'd5033b9f', 'dsb ISH|#b', 0, ()),     #dsb (crm = 1011)
    (REV_ALL_ARM, 'd5033d9f', 'dsb LD|#d', 0, ()),      #dsb (crm = 1101)
    (REV_ALL_ARM, 'd5033e9f', 'dsb ST|#e', 0, ()),      #dsb (crm = 1110)
    (REV_ALL_ARM, 'd5033f9f', 'dsb SY|#f', 0, ()),      #dsb (crm = 1111)
    (REV_ALL_ARM, 'd50331bf', 'dmb OSHLD|#1', 0, ()),   #dmb (crm = 0001)
    (REV_ALL_ARM, 'd50332bf', 'dmb OSHST|#2', 0, ()),   #dmb (crm = 0010)
    (REV_ALL_ARM, 'd50333bf', 'dmb OSH|#3', 0, ()),     #dmb (crm = 0011)
    (REV_ALL_ARM, 'd50335bf', 'dmb NSHLD|#5', 0, ()),   #dmb (crm = 0101)
    (REV_ALL_ARM, 'd50336bf', 'dmb NSHST|#6', 0, ()),   #dmb (crm = 0110)
    (REV_ALL_ARM, 'd50337bf', 'dmb NSH|#7', 0, ()),     #dmb (crm = 0111)
    (REV_ALL_ARM, 'd50339bf', 'dmb ISHLD|#9', 0, ()),   #dmb (crm = 1001)
    (REV_ALL_ARM, 'd5033abf', 'dmb ISHST|#a', 0, ()),   #dmb (crm = 1010)
    (REV_ALL_ARM, 'd5033bbf', 'dmb ISH|#b', 0, ()),     #dmb (crm = 1011)
    (REV_ALL_ARM, 'd5033dbf', 'dmb LD|#d', 0, ()),      #dmb (crm = 1101)
    (REV_ALL_ARM, 'd5033ebf', 'dmb ST|#e', 0, ()),      #dmb (crm = 1110)
    (REV_ALL_ARM, 'd5033fbf', 'dmb SY|#f', 0, ()),      #dmb (crm = 1111)
    (REV_ALL_ARM, 'd5033fdf', 'isb SY|#f', 0, ()),      #isb (SY, crm = 1111)
    (REV_ALL_ARM, 'd50f1a63', 'sys #7, c1, ca, #3, x3', 0, ()), #sys FIXME name
    (REV_ALL_ARM, 'd5171ae3', 'msr r14551, x3', 0, ()), #msr (register) FIXME system register
    (REV_ALL_ARM, 'd52f1a63', 'sysl x3, #7, c1, ca, #3', 0, ()), #sysl FIXME name
    (REV_ALL_ARM, 'd5371ae3', 'mrs x3, r14551', 0, ()), #mrs FIXME system register
    
    # Unconditional branch (register)
    
    (REV_ALL_ARM, 'd61f0060', 'br x3', 0, ()),
    (REV_ALL_ARM, 'd63f0060', 'blr x3', 0, ()),
    (REV_ALL_ARM, 'd65f0060', 'ret {x3}', 0, ()),
    (REV_ALL_ARM, 'd69f03e0', 'eret', 0, ()),
    (REV_ALL_ARM, 'd6bf03e0', 'drps', 0, ()),
#Loads and stores

#Data processing (register)
    
    # Logical (shifted register)
    
    #every set of 4 tests has the same instruction 4x with a different shift value
    #this results in each result looking identical aside from LSL, LSR, ASR, ROR,
    #(which correspond to shift values of 00, 01, 10, and 11) and mnemonic/opcode
    #32-bit variants
    (REV_ALL_ARM, '0a0b3dc3', 'and w3, w14, w11{, LSL #f}', 0, ()),
    (REV_ALL_ARM, '0a4b3dc3', 'and w3, w14, w11{, LSR #f}', 0, ()),
    (REV_ALL_ARM, '0a8b3dc3', 'and w3, w14, w11{, ASR #f}', 0, ()),
    (REV_ALL_ARM, '0acb3dc3', 'and w3, w14, w11{, ROR #f}', 0, ()),
    (REV_ALL_ARM, '0a2b3dc3', 'bic w3, w14, w11{, LSL #f}', 0, ()),
    (REV_ALL_ARM, '0a6b3dc3', 'bic w3, w14, w11{, LSR #f}', 0, ()),
    (REV_ALL_ARM, '0aab3dc3', 'bic w3, w14, w11{, ASR #f}', 0, ()),
    (REV_ALL_ARM, '0aeb3dc3', 'bic w3, w14, w11{, ROR #f}', 0, ()),
    (REV_ALL_ARM, '2a0b3dc3', 'orr w3, w14, w11{, LSL #f}', 0, ()),
    (REV_ALL_ARM, '2a4b3dc3', 'orr w3, w14, w11{, LSR #f}', 0, ()),
    (REV_ALL_ARM, '2a8b3dc3', 'orr w3, w14, w11{, ASR #f}', 0, ()),
    (REV_ALL_ARM, '2acb3dc3', 'orr w3, w14, w11{, ROR #f}', 0, ()),
    (REV_ALL_ARM, '2a2b3dc3', 'orn w3, w14, w11{, LSL #f}', 0, ()),
    (REV_ALL_ARM, '2a6b3dc3', 'orn w3, w14, w11{, LSR #f}', 0, ()),
    (REV_ALL_ARM, '2aab3dc3', 'orn w3, w14, w11{, ASR #f}', 0, ()),
    (REV_ALL_ARM, '2aeb3dc3', 'orn w3, w14, w11{, ROR #f}', 0, ()),
    (REV_ALL_ARM, '4a0b3dc3', 'eor w3, w14, w11{, LSL #f}', 0, ()),
    (REV_ALL_ARM, '4a4b3dc3', 'eor w3, w14, w11{, LSR #f}', 0, ()),
    (REV_ALL_ARM, '4a8b3dc3', 'eor w3, w14, w11{, ASR #f}', 0, ()),
    (REV_ALL_ARM, '4acb3dc3', 'eor w3, w14, w11{, ROR #f}', 0, ()),
    (REV_ALL_ARM, '4a2b3dc3', 'eon w3, w14, w11{, LSL #f}', 0, ()),
    (REV_ALL_ARM, '4a6b3dc3', 'eon w3, w14, w11{, LSR #f}', 0, ()),
    (REV_ALL_ARM, '4aab3dc3', 'eon w3, w14, w11{, ASR #f}', 0, ()),
    (REV_ALL_ARM, '4aeb3dc3', 'eon w3, w14, w11{, ROR #f}', 0, ()),
    (REV_ALL_ARM, '6a0b3dc3', 'ands w3, w14, w11{, LSL #f}', 0, ()),
    (REV_ALL_ARM, '6a4b3dc3', 'ands w3, w14, w11{, LSR #f}', 0, ()),
    (REV_ALL_ARM, '6a8b3dc3', 'ands w3, w14, w11{, ASR #f}', 0, ()),
    (REV_ALL_ARM, '6acb3dc3', 'ands w3, w14, w11{, ROR #f}', 0, ()),
    (REV_ALL_ARM, '6a2b3dc3', 'bics w3, w14, w11{, LSL #f}', 0, ()),
    (REV_ALL_ARM, '6a6b3dc3', 'bics w3, w14, w11{, LSR #f}', 0, ()),
    (REV_ALL_ARM, '6aab3dc3', 'bics w3, w14, w11{, ASR #f}', 0, ()),
    (REV_ALL_ARM, '6aeb3dc3', 'bics w3, w14, w11{, ROR #f}', 0, ()),
    #64-bit variants of the same instructions
    (REV_ALL_ARM, '8a0b3dc3', 'and x3, x14, x11{, LSL #f}', 0, ()),
    (REV_ALL_ARM, '8a4b3dc3', 'and x3, x14, x11{, LSR #f}', 0, ()),
    (REV_ALL_ARM, '8a8b3dc3', 'and x3, x14, x11{, ASR #f}', 0, ()),
    (REV_ALL_ARM, '8acb3dc3', 'and x3, x14, x11{, ROR #f}', 0, ()),
    (REV_ALL_ARM, '8a2b3dc3', 'bic x3, x14, x11{, LSL #f}', 0, ()),
    (REV_ALL_ARM, '8a6b3dc3', 'bic x3, x14, x11{, LSR #f}', 0, ()),
    (REV_ALL_ARM, '8aab3dc3', 'bic x3, x14, x11{, ASR #f}', 0, ()),
    (REV_ALL_ARM, '8aeb3dc3', 'bic x3, x14, x11{, ROR #f}', 0, ()),
    (REV_ALL_ARM, 'aa0b3dc3', 'orr x3, x14, x11{, LSL #f}', 0, ()),
    (REV_ALL_ARM, 'aa4b3dc3', 'orr x3, x14, x11{, LSR #f}', 0, ()),
    (REV_ALL_ARM, 'aa8b3dc3', 'orr x3, x14, x11{, ASR #f}', 0, ()),
    (REV_ALL_ARM, 'aacb3dc3', 'orr x3, x14, x11{, ROR #f}', 0, ()),
    (REV_ALL_ARM, 'aa2b3dc3', 'orn x3, x14, x11{, LSL #f}', 0, ()),
    (REV_ALL_ARM, 'aa6b3dc3', 'orn x3, x14, x11{, LSR #f}', 0, ()),
    (REV_ALL_ARM, 'aaab3dc3', 'orn x3, x14, x11{, ASR #f}', 0, ()),
    (REV_ALL_ARM, 'aaeb3dc3', 'orn x3, x14, x11{, ROR #f}', 0, ()),
    (REV_ALL_ARM, 'ca0b3dc3', 'eor x3, x14, x11{, LSL #f}', 0, ()),
    (REV_ALL_ARM, 'ca4b3dc3', 'eor x3, x14, x11{, LSR #f}', 0, ()),
    (REV_ALL_ARM, 'ca8b3dc3', 'eor x3, x14, x11{, ASR #f}', 0, ()),
    (REV_ALL_ARM, 'cacb3dc3', 'eor x3, x14, x11{, ROR #f}', 0, ()),
    (REV_ALL_ARM, 'ca2b3dc3', 'eon x3, x14, x11{, LSL #f}', 0, ()),
    (REV_ALL_ARM, 'ca6b3dc3', 'eon x3, x14, x11{, LSR #f}', 0, ()),
    (REV_ALL_ARM, 'caab3dc3', 'eon x3, x14, x11{, ASR #f}', 0, ()),
    (REV_ALL_ARM, 'caeb3dc3', 'eon x3, x14, x11{, ROR #f}', 0, ()),
    (REV_ALL_ARM, 'ea0b3dc3', 'ands x3, x14, x11{, LSL #f}', 0, ()),
    (REV_ALL_ARM, 'ea4b3dc3', 'ands x3, x14, x11{, LSR #f}', 0, ()),
    (REV_ALL_ARM, 'ea8b3dc3', 'ands x3, x14, x11{, ASR #f}', 0, ()),
    (REV_ALL_ARM, 'eacb3dc3', 'ands x3, x14, x11{, ROR #f}', 0, ()),
    (REV_ALL_ARM, 'ea2b3dc3', 'bics x3, x14, x11{, LSL #f}', 0, ()),
    (REV_ALL_ARM, 'ea6b3dc3', 'bics x3, x14, x11{, LSR #f}', 0, ()),
    (REV_ALL_ARM, 'eaab3dc3', 'bics x3, x14, x11{, ASR #f}', 0, ()),
    (REV_ALL_ARM, 'eaeb3dc3', 'bics x3, x14, x11{, ROR #f}', 0, ()),
    
    # Add/sub (shifted register)
    
    #similar to logical (shifted register), these are sets of three tests for the
    #same instruction, where the only different thing is the shift value.
    #the main difference is that logical (shifted register) didn't have shift = 11 as reserved
    (REV_ALL_ARM, '0b0b3dc3', 'add w3, w14, w11{, LSL #f}', 0, ()),
    (REV_ALL_ARM, '0b4b3dc3', 'add w3, w14, w11{, LSR #f}', 0, ()),
    (REV_ALL_ARM, '0b8b3dc3', 'add w3, w14, w11{, ASR #f}', 0, ()),
    (REV_ALL_ARM, '2b0b3dc3', 'adds w3, w14, w11{, LSL #f}', 0, ()),
    (REV_ALL_ARM, '2b4b3dc3', 'adds w3, w14, w11{, LSR #f}', 0, ()),
    (REV_ALL_ARM, '2b8b3dc3', 'adds w3, w14, w11{, ASR #f}', 0, ()),
    (REV_ALL_ARM, '4b0b3dc3', 'sub w3, w14, w11{, LSL #f}', 0, ()),
    (REV_ALL_ARM, '4b4b3dc3', 'sub w3, w14, w11{, LSR #f}', 0, ()),
    (REV_ALL_ARM, '4b8b3dc3', 'sub w3, w14, w11{, ASR #f}', 0, ()),
    (REV_ALL_ARM, '6b0b3dc3', 'subs w3, w14, w11{, LSL #f}', 0, ()),
    (REV_ALL_ARM, '6b4b3dc3', 'subs w3, w14, w11{, LSR #f}', 0, ()),
    (REV_ALL_ARM, '6b8b3dc3', 'subs w3, w14, w11{, ASR #f}', 0, ()),
    #64-bit variants of the same instructions
    (REV_ALL_ARM, '8b0b3dc3', 'add x3, x14, x11{, LSL #f}', 0, ()),
    (REV_ALL_ARM, '8b4b3dc3', 'add x3, x14, x11{, LSR #f}', 0, ()),
    (REV_ALL_ARM, '8b8b3dc3', 'add x3, x14, x11{, ASR #f}', 0, ()),
    (REV_ALL_ARM, 'ab0b3dc3', 'adds x3, x14, x11{, LSL #f}', 0, ()),
    (REV_ALL_ARM, 'ab4b3dc3', 'adds x3, x14, x11{, LSR #f}', 0, ()),
    (REV_ALL_ARM, 'ab8b3dc3', 'adds x3, x14, x11{, ASR #f}', 0, ()),
    (REV_ALL_ARM, 'cb0b3dc3', 'sub x3, x14, x11{, LSL #f}', 0, ()),
    (REV_ALL_ARM, 'cb4b3dc3', 'sub x3, x14, x11{, LSR #f}', 0, ()),
    (REV_ALL_ARM, 'cb8b3dc3', 'sub x3, x14, x11{, ASR #f}', 0, ()),
    (REV_ALL_ARM, 'eb0b3dc3', 'subs x3, x14, x11{, LSL #f}', 0, ()),
    (REV_ALL_ARM, 'eb4b3dc3', 'subs x3, x14, x11{, LSR #f}', 0, ()),
    (REV_ALL_ARM, 'eb8b3dc3', 'subs x3, x14, x11{, ASR #f}', 0, ()),
    
    # Add/subtract (extended register)
    
    #this time, there are 8 tests per instruction, each having a different extend
    #64-bit variants sometimes have the 11 register as a w. only x when option = x11
    (REV_ALL_ARM, '0b2b0dc3', 'add w3, w14, w11{, UXTB {#3}}', 0, ()),
    (REV_ALL_ARM, '0b2b2dc3', 'add w3, w14, w11{, UXTH {#3}}', 0, ()),
    (REV_ALL_ARM, '0b2b4dc3', 'add w3, w14, w11{, LSL|USTW {#3}}', 0, ()),
    (REV_ALL_ARM, '0b2b6dc3', 'add w3, w14, w11{, UXTX {#3}}', 0, ()),
    (REV_ALL_ARM, '0b2b8dc3', 'add w3, w14, w11{, SXTB {#3}}', 0, ()),
    (REV_ALL_ARM, '0b2badc3', 'add w3, w14, w11{, SXTH {#3}}', 0, ()),
    (REV_ALL_ARM, '0b2bcdc3', 'add w3, w14, w11{, SXTW {#3}}', 0, ()),
    (REV_ALL_ARM, '0b2bedc3', 'add w3, w14, w11{, SXTX {#3}}', 0, ()),
    (REV_ALL_ARM, '2b2b0dc3', 'adds w3, w14, w11{, UXTB {#3}}', 0, ()),
    (REV_ALL_ARM, '2b2b2dc3', 'adds w3, w14, w11{, UXTH {#3}}', 0, ()),
    (REV_ALL_ARM, '2b2b4dc3', 'adds w3, w14, w11{, LSL|USTW {#3}}', 0, ()),
    (REV_ALL_ARM, '2b2b6dc3', 'adds w3, w14, w11{, UXTX {#3}}', 0, ()),
    (REV_ALL_ARM, '2b2b8dc3', 'adds w3, w14, w11{, SXTB {#3}}', 0, ()),
    (REV_ALL_ARM, '2b2badc3', 'adds w3, w14, w11{, SXTH {#3}}', 0, ()),
    (REV_ALL_ARM, '2b2bcdc3', 'adds w3, w14, w11{, SXTW {#3}}', 0, ()),
    (REV_ALL_ARM, '2b2bedc3', 'adds w3, w14, w11{, SXTX {#3}}', 0, ()),
    (REV_ALL_ARM, '4b2b0dc3', 'sub w3, w14, w11{, UXTB {#3}}', 0, ()),
    (REV_ALL_ARM, '4b2b2dc3', 'sub w3, w14, w11{, UXTH {#3}}', 0, ()),
    (REV_ALL_ARM, '4b2b4dc3', 'sub w3, w14, w11{, LSL|USTW {#3}}', 0, ()),
    (REV_ALL_ARM, '4b2b6dc3', 'sub w3, w14, w11{, UXTX {#3}}', 0, ()),
    (REV_ALL_ARM, '4b2b8dc3', 'sub w3, w14, w11{, SXTB {#3}}', 0, ()),
    (REV_ALL_ARM, '4b2badc3', 'sub w3, w14, w11{, SXTH {#3}}', 0, ()),
    (REV_ALL_ARM, '4b2bcdc3', 'sub w3, w14, w11{, SXTW {#3}}', 0, ()),
    (REV_ALL_ARM, '4b2bedc3', 'sub w3, w14, w11{, SXTX {#3}}', 0, ()),
    (REV_ALL_ARM, '6b2b0dc3', 'subs w3, w14, w11{, UXTB {#3}}', 0, ()),
    (REV_ALL_ARM, '6b2b2dc3', 'subs w3, w14, w11{, UXTH {#3}}', 0, ()),
    (REV_ALL_ARM, '6b2b4dc3', 'subs w3, w14, w11{, LSL|USTW {#3}}', 0, ()),
    (REV_ALL_ARM, '6b2b6dc3', 'subs w3, w14, w11{, UXTX {#3}}', 0, ()),
    (REV_ALL_ARM, '6b2b8dc3', 'subs w3, w14, w11{, SXTB {#3}}', 0, ()),
    (REV_ALL_ARM, '6b2badc3', 'subs w3, w14, w11{, SXTH {#3}}', 0, ()),
    (REV_ALL_ARM, '6b2bcdc3', 'subs w3, w14, w11{, SXTW {#3}}', 0, ()),
    (REV_ALL_ARM, '6b2bedc3', 'subs w3, w14, w11{, SXTX {#3}}', 0, ()),
    #64-bit variants of the same instructions
    (REV_ALL_ARM, '8b2b0dc3', 'add x3, x14, w11{, UXTB {#3}}', 0, ()),
    (REV_ALL_ARM, '8b2b2dc3', 'add x3, x14, w11{, UXTH {#3}}', 0, ()),
    (REV_ALL_ARM, '8b2b4dc3', 'add x3, x14, w11{, LSL|USTW {#3}}', 0, ()),
    (REV_ALL_ARM, '8b2b6dc3', 'add x3, x14, x11{, UXTX {#3}}', 0, ()),
    (REV_ALL_ARM, '8b2b8dc3', 'add x3, x14, w11{, SXTB {#3}}', 0, ()),
    (REV_ALL_ARM, '8b2badc3', 'add x3, x14, w11{, SXTH {#3}}', 0, ()),
    (REV_ALL_ARM, '8b2bcdc3', 'add x3, x14, w11{, SXTW {#3}}', 0, ()),
    (REV_ALL_ARM, '8b2bedc3', 'add x3, x14, x11{, SXTX {#3}}', 0, ()),
    (REV_ALL_ARM, 'ab2b0dc3', 'adds x3, x14, w11{, UXTB {#3}}', 0, ()),
    (REV_ALL_ARM, 'ab2b2dc3', 'adds x3, x14, w11{, UXTH {#3}}', 0, ()),
    (REV_ALL_ARM, 'ab2b4dc3', 'adds x3, x14, w11{, LSL|USTW {#3}}', 0, ()),
    (REV_ALL_ARM, 'ab2b6dc3', 'adds x3, x14, x11{, UXTX {#3}}', 0, ()),
    (REV_ALL_ARM, 'ab2b8dc3', 'adds x3, x14, w11{, SXTB {#3}}', 0, ()),
    (REV_ALL_ARM, 'ab2badc3', 'adds x3, x14, w11{, SXTH {#3}}', 0, ()),
    (REV_ALL_ARM, 'ab2bcdc3', 'adds x3, x14, w11{, SXTW {#3}}', 0, ()),
    (REV_ALL_ARM, 'ab2bedc3', 'adds x3, x14, x11{, SXTX {#3}}', 0, ()),
    (REV_ALL_ARM, 'cb2b0dc3', 'sub x3, x14, w11{, UXTB {#3}}', 0, ()),
    (REV_ALL_ARM, 'cb2b2dc3', 'sub x3, x14, w11{, UXTH {#3}}', 0, ()),
    (REV_ALL_ARM, 'cb2b4dc3', 'sub x3, x14, w11{, LSL|USTW {#3}}', 0, ()),
    (REV_ALL_ARM, 'cb2b6dc3', 'sub x3, x14, x11{, UXTX {#3}}', 0, ()),
    (REV_ALL_ARM, 'cb2b8dc3', 'sub x3, x14, w11{, SXTB {#3}}', 0, ()),
    (REV_ALL_ARM, 'cb2badc3', 'sub x3, x14, w11{, SXTH {#3}}', 0, ()),
    (REV_ALL_ARM, 'cb2bcdc3', 'sub x3, x14, w11{, SXTW {#3}}', 0, ()),
    (REV_ALL_ARM, 'cb2bedc3', 'sub x3, x14, x11{, SXTX {#3}}', 0, ()),
    (REV_ALL_ARM, 'eb2b0dc3', 'subs x3, x14, w11{, UXTB {#3}}', 0, ()),
    (REV_ALL_ARM, 'eb2b2dc3', 'subs x3, x14, w11{, UXTH {#3}}', 0, ()),
    (REV_ALL_ARM, 'eb2b4dc3', 'subs x3, x14, w11{, LSL|USTW {#3}}', 0, ()),
    (REV_ALL_ARM, 'eb2b6dc3', 'subs x3, x14, x11{, UXTX {#3}}', 0, ()),
    (REV_ALL_ARM, 'eb2b8dc3', 'subs x3, x14, w11{, SXTB {#3}}', 0, ()),
    (REV_ALL_ARM, 'eb2badc3', 'subs x3, x14, w11{, SXTH {#3}}', 0, ()),
    (REV_ALL_ARM, 'eb2bcdc3', 'subs x3, x14, w11{, SXTW {#3}}', 0, ()),
    (REV_ALL_ARM, 'eb2bedc3', 'subs x3, x14, x11{, SXTX {#3}}', 0, ()),
    
    # Add/subtract (with carry)
    
    (REV_ALL_ARM, '1a0b01c3', 'adc w3, w14, w11', 0, ()),
    (REV_ALL_ARM, '3a0b01c3', 'adcs w3, w14, w11', 0, ()),
    (REV_ALL_ARM, '5a0b01c3', 'sbc w3, w14, w11', 0, ()),
    (REV_ALL_ARM, '7a0b01c3', 'sbcs w3, w14, w11', 0, ()),
    (REV_ALL_ARM, '9a0b01c3', 'adc x3, x14, x11', 0, ()),
    (REV_ALL_ARM, 'ba0b01c3', 'adcs x3, x14, x11', 0, ()),
    (REV_ALL_ARM, 'da0b01c3', 'sbc x3, x14, x11', 0, ()),
    (REV_ALL_ARM, 'fa0b01c3', 'sbcs x3, x14, x11', 0, ()),
    
    # Conditional compare (register)
    
    #FIXME X = cond, Y = nzcv, olist to match
    (REV_ALL_ARM, '3a4bX1cY', 'ccmn w14, w11, #nzcv, cond', 0, ()),
    (REV_ALL_ARM, '7a4bX1cY', 'ccmp w14, w11, #nzcv, cond', 0, ()),
    (REV_ALL_ARM, 'ba4bX1cY', 'ccmn x14, x11, #nzcv, cond', 0, ()),
    (REV_ALL_ARM, 'fa4bX1cY', 'ccmp x14, x11, #nzcv, cond', 0, ()),
    
    # Conditional compare (immediate)
    
    #FIXME X = cond, Y = nzcv, olist to match
    (REV_ALL_ARM, '3a4bX9cY', 'ccmn w14, #11, #nzcv, cond', 0, ()),
    (REV_ALL_ARM, '7a4bX9cY', 'ccmp w14, #11, #nzcv, cond', 0, ()),
    (REV_ALL_ARM, 'ba4bX9cY', 'ccmn x14, #11, #nzcv, cond', 0, ()),
    (REV_ALL_ARM, 'fa4bX9cY', 'ccmp x14, #11, #nzcv, cond', 0, ()),
    
    # Conditional select
    
    #FIXME X = cond, olist to match
    (REV_ALL_ARM, '1a8bX1c3', 'csel w3, w14, w11, cond', 0, ()),
    (REV_ALL_ARM, '1a8bX5c3', 'csinc w3, w14, w11, cond', 0, ()),
    (REV_ALL_ARM, '5a8bX1c3', 'csinv w3, w14, w11, cond', 0, ()),
    (REV_ALL_ARM, '5a8bX5c3', 'csneg w3, w14, w11, cond', 0, ()),
    (REV_ALL_ARM, '9a8bX1c3', 'csel x3, x14, x11, cond', 0, ()),
    (REV_ALL_ARM, '9a8bX5c3', 'csinc x3, x14, x11, cond', 0, ()),
    (REV_ALL_ARM, 'da8bX1c3', 'csinv x3, x14, x11, cond', 0, ()),
    (REV_ALL_ARM, 'da8bX5c3', 'csneg x3, x14, x11, cond', 0, ()),
    
    # Data processing (3 source)
    
    (REV_ALL_ARM, '1b0b25c3', 'madd w3, w14, w11, w9', 0, ()),
    (REV_ALL_ARM, '1b0ba5c3', 'msub w3, w14, w11, w9', 0, ()),
    (REV_ALL_ARM, '9b0b25c3', 'madd x3, x14, x11, x9', 0, ()),
    (REV_ALL_ARM, '9b0ba5c3', 'msub x3, x14, x11, x9', 0, ()),
    (REV_ALL_ARM, '9b2b25c3', 'smaddl x3, w14, w11, x9', 0, ()),
    (REV_ALL_ARM, '9b2ba5c3', 'smsubl x3, w14, w11, x9', 0, ()),
    (REV_ALL_ARM, '9b4b25c3', 'smulh x3, x14, x11', 0, ()),
    (REV_ALL_ARM, '9bab25c3', 'umaddl x3, w14, w11, x9', 0, ()),
    (REV_ALL_ARM, '9baba5c3', 'umsubl x3, w14, w11, x9', 0, ()),
    (REV_ALL_ARM, '9bdb25c3', 'umulh x3, x14, x11', 0, ()),
    
    # Data processing (2 source)
    
    (REV_ALL_ARM, '1acb09c3', 'udiv w3, w14, w11', 0, ()),
    (REV_ALL_ARM, '1acb0dc3', 'sdiv w3, w14, w11', 0, ()),
    (REV_ALL_ARM, '1acb21c3', 'lslv w3, w14, w11', 0, ()),
    (REV_ALL_ARM, '1acb25c3', 'lsrv w3, w14, w11', 0, ()),
    (REV_ALL_ARM, '1acb29c3', 'asrv w3, w14, w11', 0, ()),
    (REV_ALL_ARM, '1acb2dc3', 'rorv w3, w14, w11', 0, ()),
    (REV_ALL_ARM, '1acb41c3', 'crc32b w3, w14, w11', 0, ()),
    (REV_ALL_ARM, '1acb45c3', 'crc32h w3, w14, w11', 0, ()),
    (REV_ALL_ARM, '1acb49c3', 'crc32w w3, w14, w11', 0, ()),
    (REV_ALL_ARM, '1acb51c3', 'crc32cb w3, w14, w11', 0, ()),
    (REV_ALL_ARM, '1acb55c3', 'crc32ch w3, w14, w11', 0, ()),
    (REV_ALL_ARM, '1acb59c3', 'crc32cw w3, w14, w11', 0, ()),
    (REV_ALL_ARM, '9acb09c3', 'udiv x3, x14, x11', 0, ()),
    (REV_ALL_ARM, '9acb0dc3', 'sdiv x3, x14, x11', 0, ()),
    (REV_ALL_ARM, '9acb21c3', 'lslv x3, x14, x11', 0, ()),
    (REV_ALL_ARM, '9acb25c3', 'lsrv x3, x14, x11', 0, ()),
    (REV_ALL_ARM, '9acb29c3', 'asrv x3, x14, x11', 0, ()),
    (REV_ALL_ARM, '9acb2dc3', 'rorv x3, x14, x11', 0, ()),
    (REV_ALL_ARM, '9acb4dc3', 'crc32x w3, w14, w11', 0, ()),
    (REV_ALL_ARM, '9acb5dc3', 'crc32cx w3, w14, w11', 0, ()),
    
    # Data processing (1 source)
    
    (REV_ALL_ARM, '5ac001c3', 'rbit w3, w14', 0, ()),
    (REV_ALL_ARM, '5ac005c3', 'rev16 w3, w14', 0, ()),
    (REV_ALL_ARM, '5ac009c3', 'rev w3, w14', 0, ()),
    (REV_ALL_ARM, '5ac011c3', 'clz w3, w14', 0, ()),
    (REV_ALL_ARM, '5ac015c3', 'cls w3, w14', 0, ()),
    (REV_ALL_ARM, 'dac001c3', 'rbit x3, x14', 0, ()),
    (REV_ALL_ARM, 'dac005c3', 'rev16 x3, x14', 0, ()),
    (REV_ALL_ARM, 'dac009c3', 'rev32 x3, x14', 0, ()),
    (REV_ALL_ARM, 'dac00dc3', 'rev x3, x14', 0, ()),
    (REV_ALL_ARM, 'dac011c3', 'clz x3, x14', 0, ()),
    (REV_ALL_ARM, 'dac015c3', 'cls x3, x14', 0, ()),

     
#Data processing (SIMD and floating point)
]
