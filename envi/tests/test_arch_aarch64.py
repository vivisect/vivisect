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
    
    #Load/store exclusive
    
    (REV_ALL_ARM, '080b25c3', 'stxrb w11, w3, [x14{, #0}]', 0, ()),
    (REV_ALL_ARM, '080ba5c3', 'stlxrb w11, w3, [x14{, #0}]', 0, ()),
    (REV_ALL_ARM, '084b25c3', 'ldxrb w3, [x14{, #0}]', 0, ()),
    (REV_ALL_ARM, '084ba5c3', 'ldaxrb w3, [x14{, #0}]', 0, ()),
    (REV_ALL_ARM, '088ba5c3', 'stlrb w3, [x14{, #0}]', 0, ()),
    (REV_ALL_ARM, '08cba5c3', 'ldarb w3, [x14{, #0}]', 0, ()),
    (REV_ALL_ARM, '480b25c3', 'stxrh w11, w3, [x14{, #0}]', 0, ()),
    (REV_ALL_ARM, '480ba5c3', 'stlxrh w11, w3, [x14{, #0}]', 0, ()),
    (REV_ALL_ARM, '484b25c3', 'ldxrh w3, [x14{, #0}]', 0, ()),
    (REV_ALL_ARM, '484ba5c3', 'ldaxrh w3, [x14{, #0}]', 0, ()),
    (REV_ALL_ARM, '488ba5c3', 'stlrh w3, [x14{, #0}]', 0, ()),
    (REV_ALL_ARM, '48cba5c3', 'ldarh w3, [x14{, #0}]', 0, ()),
    (REV_ALL_ARM, '880b25c3', 'stxr w11, w3, [x14{, #0}]', 0, ()),
    (REV_ALL_ARM, '880ba5c3', 'stlxr w11, w3, [x14{, #0}]', 0, ()),
    (REV_ALL_ARM, '882b25c3', 'stxp w11, w3, w9, [x14{, #0}]', 0, ()),
    (REV_ALL_ARM, '882ba5c3', 'stlxp w11, w3, w9, [x14{, #0}]', 0, ()),
    (REV_ALL_ARM, '884b25c3', 'ldxr w3, [x14{, #0}]', 0, ()),
    (REV_ALL_ARM, '884ba5c3', 'ldaxr w3, [x14{, #0}]', 0, ()),
    (REV_ALL_ARM, '886b25c3', 'ldxp w3, w9, [x14{, #0}]', 0, ()),
    (REV_ALL_ARM, '886ba5c3', 'ldaxp w3, w9, [x14{, #0}]', 0, ()),
    (REV_ALL_ARM, '888ba5c3', 'stlr w3, [x14{, #0}]', 0, ()),
    (REV_ALL_ARM, '88cba5c3', 'ldar w3, [x14{, #0}]', 0, ()),
    (REV_ALL_ARM, 'c80b25c3', 'stxr w11, x3, [x14{, #0}]', 0, ()),
    (REV_ALL_ARM, 'c80ba5c3', 'stlxr w11, x3, [x14{, #0}]', 0, ()),
    (REV_ALL_ARM, 'c82b25c3', 'stxp w11, x3, x9, [x14{, #0}]', 0, ()),
    (REV_ALL_ARM, 'c82ba5c3', 'stlxp w11, x3, x9, [x14{, #0}]', 0, ()),
    (REV_ALL_ARM, 'c84b25c3', 'ldxr x3, [x14{, #0}]', 0, ()),
    (REV_ALL_ARM, 'c84ba5c3', 'ldaxr x3, [x14{, #0}]', 0, ()),
    (REV_ALL_ARM, 'c86b25c3', 'ldxp x3, x9, [x14{, #0}]', 0, ()),
    (REV_ALL_ARM, 'c86ba5c3', 'ldaxp x3, x9, [x14{, #0}]', 0, ()),
    (REV_ALL_ARM, 'c88ba5c3', 'stlr x3, [x14{, #0}]', 0, ()),
    (REV_ALL_ARM, 'c8cba5c3', 'ldar x3, [x14{, #0}]', 0, ()),
    
    #Load register (literal)
    
    #FIXME prfm #uimm5
    (REV_ALL_ARM, '18abcde3', 'ldr w3 1579bc', 0, ()),
    (REV_ALL_ARM, '1cabcde3', 'ldr s3 1579bc', 0, ()),
    (REV_ALL_ARM, '58abcde3', 'ldr x3 1579bc', 0, ()),
    (REV_ALL_ARM, '5cabcde3', 'ldr d3 1579bc', 0, ()),
    (REV_ALL_ARM, '98abcde3', 'ldrsw x3 1579bc', 0, ()),
    (REV_ALL_ARM, '9cabcde3', 'ldr q3 1579bc', 0, ()),
    (REV_ALL_ARM, 'd8abcde0', 'prfm PLDL1KEEP 1579bc', 0, ()),
    (REV_ALL_ARM, 'd8abcde1', 'prfm PLDL1STRM 1579bc', 0, ()),
    (REV_ALL_ARM, 'd8abcde2', 'prfm PLDL2KEEP 1579bc', 0, ()),
    (REV_ALL_ARM, 'd8abcde3', 'prfm PLDL2STRM 1579bc', 0, ()),
    (REV_ALL_ARM, 'd8abcde4', 'prfm PLDL3KEEP 1579bc', 0, ()),
    (REV_ALL_ARM, 'd8abcde5', 'prfm PLDL3STRM 1579bc', 0, ()),
    (REV_ALL_ARM, 'd8abcde8', 'prfm PLIL1KEEP 1579bc', 0, ()),
    (REV_ALL_ARM, 'd8abcde9', 'prfm PLIL1STRM 1579bc', 0, ()),
    (REV_ALL_ARM, 'd8abcdea', 'prfm PLIL2KEEP 1579bc', 0, ()),
    (REV_ALL_ARM, 'd8abcdeb', 'prfm PLIL2STRM 1579bc', 0, ()),
    (REV_ALL_ARM, 'd8abcdec', 'prfm PLIL3KEEP 1579bc', 0, ()),
    (REV_ALL_ARM, 'd8abcded', 'prfm PLIL3STRM 1579bc', 0, ()),
    (REV_ALL_ARM, 'd8abcdf0', 'prfm PSTL1KEEP 1579bc', 0, ()),
    (REV_ALL_ARM, 'd8abcdf1', 'prfm PSTL1STRM 1579bc', 0, ()),
    (REV_ALL_ARM, 'd8abcdf2', 'prfm PSTL2KEEP 1579bc', 0, ()),
    (REV_ALL_ARM, 'd8abcdf3', 'prfm PSTL2STRM 1579bc', 0, ()),
    (REV_ALL_ARM, 'd8abcdf4', 'prfm PSTL3KEEP 1579bc', 0, ()),
    (REV_ALL_ARM, 'd8abcdf5', 'prfm PSTL3STRM 1579bc', 0, ()),
    
    #Load/store no-allocate pair (offset)

    (REV_ALL_ARM, '2831a5c3', 'stnp w3, w9, [x14{, #18c}]', 0, ()),
    (REV_ALL_ARM, '2871a5c3', 'ldnp w3, w9, [x14{, #18c}]', 0, ()),
    (REV_ALL_ARM, '2c31a5c3', 'stnp s3, s9, [x14{, #18c}]', 0, ()),
    (REV_ALL_ARM, '2c71a5c3', 'ldnp s3, s9, [x14{, #18c}]', 0, ()),
    (REV_ALL_ARM, '6c31a5c3', 'stnp d3, d9, [x14{, #318}]', 0, ()),
    (REV_ALL_ARM, '6c71a5c3', 'ldnp d3, d9, [x14{, #318}]', 0, ()),
    (REV_ALL_ARM, 'a831a5c3', 'stnp x3, x9, [x14{, #318}]', 0, ()),
    (REV_ALL_ARM, 'a871a5c3', 'ldnp x3, x9, [x14{, #318}]', 0, ()),
    (REV_ALL_ARM, 'ac31a5c3', 'stnp q3, q9, [x14{, #630}]', 0, ()),
    (REV_ALL_ARM, 'ac71a5c3', 'ldnp q3, q9, [x14{, #630}]', 0, ()),
    
    #Load/store register pair (post-indexed)
    
    (REV_ALL_ARM, '28b1a5c3', 'stp w3, w9, [x14], #18c', 0, ()),
    (REV_ALL_ARM, '28f1a5c3', 'ldp w3, w9, [x14], #18c', 0, ()),
    (REV_ALL_ARM, '2cb1a5c3', 'stp s3, s9, [x14], #18c', 0, ()),
    (REV_ALL_ARM, '2cf1a5c3', 'ldp s3, s9, [x14], #18c', 0, ()),
    (REV_ALL_ARM, '68f1a5c3', 'ldpsw x3, x9, [x14], #18c', 0, ()),
    (REV_ALL_ARM, '6cb1a5c3', 'stp d3, d9, [x14], #318', 0, ()),
    (REV_ALL_ARM, '6cf1a5c3', 'ldp d3, d9, [x14], #318', 0, ()),
    (REV_ALL_ARM, 'a8b1a5c3', 'stp x3, x9, [x14], #318', 0, ()),
    (REV_ALL_ARM, 'a8f1a5c3', 'ldp x3, x9, [x14], #318', 0, ()),
    (REV_ALL_ARM, 'acb1a5c3', 'stp q3, q9, [x14], #630', 0, ()),
    (REV_ALL_ARM, 'acf1a5c3', 'ldp q3, q9, [x14], #630', 0, ()),

    #Load/store register pair (offset)
    
    (REV_ALL_ARM, '2931a5c3', 'stp w3, w9, [x14{, #18c}]', 0, ()),
    (REV_ALL_ARM, '2971a5c3', 'ldp w3, w9, [x14{, #18c}]', 0, ()),
    (REV_ALL_ARM, '2d31a5c3', 'stp s3, s9, [x14{, #18c}]', 0, ()),
    (REV_ALL_ARM, '2d71a5c3', 'ldp s3, s9, [x14{, #18c}]', 0, ()),
    (REV_ALL_ARM, '6971a5c3', 'ldpsw x3, x9, [x14{, #18c}]', 0, ()),
    (REV_ALL_ARM, '6d31a5c3', 'stp d3, d9, [x14{, #318}]', 0, ()),
    (REV_ALL_ARM, '6d71a5c3', 'ldp d3, d9, [x14{, #318}]', 0, ()),
    (REV_ALL_ARM, 'a931a5c3', 'stp x3, x9, [x14{, #318}]', 0, ()),
    (REV_ALL_ARM, 'a971a5c3', 'ldp x3, x9, [x14{, #318}]', 0, ()),
    (REV_ALL_ARM, 'ad31a5c3', 'stp q3, q9, [x14{, #630}]', 0, ()),
    (REV_ALL_ARM, 'ad71a5c3', 'ldp q3, q9, [x14{, #630}]', 0, ()),
    
    #Load/store register pair (pre-indexed)
    
    (REV_ALL_ARM, '29b1a5c3', 'stp w3, w9, [x14, #18c]!', 0, ()),
    (REV_ALL_ARM, '29f1a5c3', 'ldp w3, w9, [x14, #18c]!', 0, ()),
    (REV_ALL_ARM, '2db1a5c3', 'stp s3, s9, [x14, #18c]!', 0, ()),
    (REV_ALL_ARM, '2df1a5c3', 'ldp s3, s9, [x14, #18c]!', 0, ()),
    (REV_ALL_ARM, '69f1a5c3', 'ldpsw x3, x9, [x14, #18c]!', 0, ()),
    (REV_ALL_ARM, '6db1a5c3', 'stp d3, d9, [x14, #318]!', 0, ()),
    (REV_ALL_ARM, '6df1a5c3', 'ldp d3, d9, [x14, #318]!', 0, ()),
    (REV_ALL_ARM, 'a9b1a5c3', 'stp x3, x9, [x14, #318]!', 0, ()),
    (REV_ALL_ARM, 'a9f1a5c3', 'ldp x3, x9, [x14, #318]!', 0, ()),
    (REV_ALL_ARM, 'adb1a5c3', 'stp q3, q9, [x14, #630]!', 0, ()),
    (REV_ALL_ARM, 'adf1a5c3', 'ldp q3, q9, [x14, #630]!', 0, ()),
    
    #Load/store register (unscaled immediate)
    
    (REV_ALL_ARM, '3810f1c3', 'sturb w3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, '3850f1c3', 'ldurb w3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, '3890f1c3', 'ldursb x3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, '38d0f1c3', 'ldursb w3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, '3c10f1c3', 'stur b3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, '3c50f1c3', 'ldur b3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, '3c90f1c3', 'stur q3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, '3cd0f1c3', 'ldur q3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, '7810f1c3', 'sturh w3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, '7850f1c3', 'ldurh w3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, '7890f1c3', 'ldursh x3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, '78d0f1c3', 'ldursh w3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, '7c10f1c3', 'stur h3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, '7c50f1c3', 'ldur h3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, 'b810f1c3', 'stur w3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, 'b850f1c3', 'ldur w3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, 'b890f1c3', 'ldursw x3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, 'bc10f1c3', 'stur s3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, 'bc50f1c3', 'ldur s3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, 'f810f1c3', 'stur x3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, 'f850f1c3', 'ldur x3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, 'f890f1c0', 'prfum PLDL1KEEP, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, 'f890f1c1', 'prfum PLDL1STRM, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, 'f890f1c2', 'prfum PLDL2KEEP, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, 'f890f1c3', 'prfum PLDL2STRM, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, 'f890f1c4', 'prfum PLDL3KEEP, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, 'f890f1c5', 'prfum PLDL3STRM, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, 'f890f1c8', 'prfum PLIL1KEEP, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, 'f890f1c9', 'prfum PLIL1STRM, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, 'f890f1ca', 'prfum PLIL2KEEP, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, 'f890f1cb', 'prfum PLIL2STRM, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, 'f890f1cc', 'prfum PLIL3KEEP, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, 'f890f1cd', 'prfum PLIL3STRM, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, 'f890f1d0', 'prfum PSTL1KEEP, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, 'f890f1d1', 'prfum PSTL1STRM, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, 'f890f1d2', 'prfum PSTL2KEEP, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, 'f890f1d3', 'prfum PSTL2STRM, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, 'f890f1d4', 'prfum PSTL3KEEP, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, 'f890f1d5', 'prfum PSTL3STRM, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, 'fc10f1c3', 'stur d3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, 'fc50f1c3', 'ldur d3, [x14{, #10f}]', 0, ()),
    
    #Load/store register (immediate post-indexed)
    
    (REV_ALL_ARM, '3810f5c3', 'strb w3, [x14], #10f', 0, ()),
    (REV_ALL_ARM, '3850f5c3', 'ldrb w3, [x14], #10f', 0, ()),
    (REV_ALL_ARM, '3890f5c3', 'ldrsb x3, [x14], #10f', 0, ()),
    (REV_ALL_ARM, '38d0f5c3', 'ldrsb w3, [x14], #10f', 0, ()),
    (REV_ALL_ARM, '3c10f5c3', 'str b3, [x14], #10f', 0, ()),
    (REV_ALL_ARM, '3c50f5c3', 'ldr b3, [x14], #10f', 0, ()),
    (REV_ALL_ARM, '3c90f5c3', 'str q3, [x14], #10f', 0, ()),
    (REV_ALL_ARM, '3cd0f5c3', 'ldr q3, [x14], #10f', 0, ()),
    (REV_ALL_ARM, '7810f5c3', 'strh w3, [x14], #10f', 0, ()),
    (REV_ALL_ARM, '7850f5c3', 'ldrh w3, [x14], #10f', 0, ()),
    (REV_ALL_ARM, '7890f5c3', 'ldrsh x3, [x14], #10f', 0, ()),
    (REV_ALL_ARM, '78d0f5c3', 'ldrsh w3, [x14], #10f', 0, ()),
    (REV_ALL_ARM, '7c10f5c3', 'str h3, [x14], #10f', 0, ()),
    (REV_ALL_ARM, '7c50f5c3', 'ldr h3, [x14], #10f', 0, ()),
    (REV_ALL_ARM, 'b810f5c3', 'str w3, [x14], #10f', 0, ()),
    (REV_ALL_ARM, 'b850f5c3', 'ldr w3, [x14], #10f', 0, ()),
    (REV_ALL_ARM, 'b890f5c3', 'ldrsw x3, [x14], #10f', 0, ()),
    (REV_ALL_ARM, 'bc10f5c3', 'str s3, [x14], #10f', 0, ()),
    (REV_ALL_ARM, 'bc50f5c3', 'ldr s3, [x14], #10f', 0, ()),
    (REV_ALL_ARM, 'f810f5c3', 'str x3, [x14], #10f', 0, ()),
    (REV_ALL_ARM, 'f850f5c3', 'ldr x3, [x14], #10f', 0, ()),
    (REV_ALL_ARM, 'fc10f5c3', 'str d3, [x14], #10f', 0, ()),
    (REV_ALL_ARM, 'fc50f5c3', 'ldr d3, [x14], #10f', 0, ()),
    
    #Load/store register (unprivileged)
    
    (REV_ALL_ARM, '3810f9c3', 'sttrb w3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, '3850f9c3', 'ldtrb w3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, '3890f9c3', 'ldtrsb x3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, '38d0f9c3', 'ldtrsb w3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, '7810f9c3', 'sttrh w3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, '7850f9c3', 'ldtrh w3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, '7890f9c3', 'ldtrsh x3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, '78d0f9c3', 'ldtrsh w3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, 'b810f9c3', 'sttr w3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, 'b850f9c3', 'ldtr w3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, 'b890f9c3', 'ldtrsw x3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, 'f810f9c3', 'sttr x3, [x14{, #10f}]', 0, ()),
    (REV_ALL_ARM, 'f850f9c3', 'ldtr x3, [x14{, #10f}]', 0, ()),
    
    #Load/store register (immediate pre-indexed)
    
    (REV_ALL_ARM, '3810fdc3', 'strb w3, [x14, #10f]!', 0, ()),
    (REV_ALL_ARM, '3850fdc3', 'ldrb w3, [x14, #10f]!', 0, ()),
    (REV_ALL_ARM, '3890fdc3', 'ldrsb x3, [x14, #10f]!', 0, ()),
    (REV_ALL_ARM, '38d0fdc3', 'ldrsb w3, [x14, #10f]!', 0, ()),
    (REV_ALL_ARM, '3c10fdc3', 'str b3, [x14, #10f]!', 0, ()),
    (REV_ALL_ARM, '3c50fdc3', 'ldr b3, [x14, #10f]!', 0, ()),
    (REV_ALL_ARM, '3c90fdc3', 'str q3, [x14, #10f]!', 0, ()),
    (REV_ALL_ARM, '3cd0fdc3', 'ldr q3, [x14, #10f]!', 0, ()),
    (REV_ALL_ARM, '7810fdc3', 'strh w3, [x14, #10f]!', 0, ()),
    (REV_ALL_ARM, '7850fdc3', 'ldrh w3, [x14, #10f]!', 0, ()),
    (REV_ALL_ARM, '7890fdc3', 'ldrsh x3, [x14, #10f]!', 0, ()),
    (REV_ALL_ARM, '78d0fdc3', 'ldrsh w3, [x14, #10f]!', 0, ()),
    (REV_ALL_ARM, '7c10fdc3', 'str h3, [x14, #10f]!', 0, ()),
    (REV_ALL_ARM, '7c50fdc3', 'ldr h3, [x14, #10f]!', 0, ()),
    (REV_ALL_ARM, 'b810fdc3', 'str w3, [x14, #10f]!', 0, ()),
    (REV_ALL_ARM, 'b850fdc3', 'ldr w3, [x14, #10f]!', 0, ()),
    (REV_ALL_ARM, 'b890fdc3', 'ldrsw x3, [x14, #10f]!', 0, ()),
    (REV_ALL_ARM, 'bc10fdc3', 'str s3, [x14, #10f]!', 0, ()),
    (REV_ALL_ARM, 'bc50fdc3', 'ldr s3, [x14, #10f]!', 0, ()),
    (REV_ALL_ARM, 'f810fdc3', 'str x3, [x14, #10f]!', 0, ()),
    (REV_ALL_ARM, 'f850fdc3', 'ldr x3, [x14, #10f]!', 0, ()),
    (REV_ALL_ARM, 'fc10fdc3', 'str d3, [x14, #10f]!', 0, ()),
    (REV_ALL_ARM, 'fc50fdc3', 'ldr d3, [x14, #10f]!', 0, ()),
    
    Load/store register (register offset)

    #every 5 tests is for the same instruction, just with altered <extend> values
    #LSL gets 2 tests, because <amount> doesn't default to zero when <extend> is LSL
    #prfm is an exception, so there are 5 sets of 18 tests each. Each set has the same
    #value for <extend> on all 18 tests. What changes between tests is the value of <prfop>
    (REV_ALL_ARM, '382b59c3', 'strb w3, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, '382bd9c3', 'strb w3, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, '382b69c3', 'strb w3, [x14, x11{, LSL{}}]', 0, ()),
    (REV_ALL_ARM, '382b79c3', 'strb w3, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, '382bf9c3', 'strb w3, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, '386b59c3', 'ldrb w3, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, '386bd9c3', 'ldrb w3, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, '386b69c3', 'ldrb w3, [x14, x11{, LSL{}}]', 0, ()),
    (REV_ALL_ARM, '386b79c3', 'ldrb w3, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, '386bf9c3', 'ldrb w3, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, '38ab59c3', 'ldrsb x3, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, '38abd9c3', 'ldrsb x3, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, '38ab69c3', 'ldrsb x3, [x14, x11{, LSL{}}]', 0, ()),
    (REV_ALL_ARM, '38ab79c3', 'ldrsb x3, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, '38abf9c3', 'ldrsb x3, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, '38eb59c3', 'ldrsb w3, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, '38ebd9c3', 'ldrsb w3, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, '38eb69c3', 'ldrsb w3, [x14, x11{, LSL{}}]', 0, ()),
    (REV_ALL_ARM, '38eb79c3', 'ldrsb w3, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, '38ebf9c3', 'ldrsb w3, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, '3c2b59c3', 'str b3, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, '3c2bd9c3', 'str b3, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, '3c2b69c3', 'str b3, [x14, x11{, LSL{}}]', 0, ()),
    (REV_ALL_ARM, '3c2b79c3', 'str b3, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, '3c2bf9c3', 'str b3, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, '3c6b59c3', 'ldr b3, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, '3c6bd9c3', 'ldr b3, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, '3c6b69c3', 'ldr b3, [x14, x11{, LSL{}}]', 0, ()),
    (REV_ALL_ARM, '3c6b79c3', 'ldr b3, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, '3c6bf9c3', 'ldr b3, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, '3cab59c3', 'str q3, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, '3cabd9c3', 'str q3, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, '3cab69c3', 'str q3, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, '3cab79c3', 'str q3, [x14, x11{, LSL{#4}}]', 0, ()),
    (REV_ALL_ARM, '3cabf9c3', 'str q3, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, '3ceb59c3', 'ldr q3, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, '3cebd9c3', 'ldr q3, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, '3ceb69c3', 'ldr q3, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, '3ceb79c3', 'ldr q3, [x14, x11{, LSL{#4}}]', 0, ()),
    (REV_ALL_ARM, '3cebf9c3', 'ldr q3, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, '782b59c3', 'strh w3, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, '782bd9c3', 'strh w3, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, '782b69c3', 'strh w3, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, '782b79c3', 'strh w3, [x14, x11{, LSL{#1}}]', 0, ()),
    (REV_ALL_ARM, '782bf9c3', 'strh w3, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, '786bf9c3', 'ldrh w3, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, '786bf9c3', 'ldrh w3, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, '786bf9c3', 'ldrh w3, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, '786bf9c3', 'ldrh w3, [x14, x11{, LSL{#1}}]', 0, ()),
    (REV_ALL_ARM, '786bf9c3', 'ldrh w3, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, '78ab59c3', 'ldrsh x3, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, '78abd9c3', 'ldrsh x3, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, '78ab69c3', 'ldrsh x3, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, '78ab79c3', 'ldrsh x3, [x14, x11{, LSL{#1}}]', 0, ()),
    (REV_ALL_ARM, '78abf9c3', 'ldrsh x3, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, '78eb59c3', 'ldrsh w3, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, '78ebd9c3', 'ldrsh w3, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, '78eb69c3', 'ldrsh w3, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, '78eb79c3', 'ldrsh w3, [x14, x11{, LSL{#1}}]', 0, ()),
    (REV_ALL_ARM, '78ebf9c3', 'ldrsh w3, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, '7c2b59c3', 'str h3, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, '7c2bd9c3', 'str h3, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, '7c2b69c3', 'str h3, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, '7c2b79c3', 'str h3, [x14, x11{, LSL{#1}}]', 0, ()),
    (REV_ALL_ARM, '7c2bf9c3', 'str h3, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, '7c6b59c3', 'ldr h3, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, '7c6bd9c3', 'ldr h3, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, '7c6b69c3', 'ldr h3, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, '7c6b79c3', 'ldr h3, [x14, x11{, LSL{#1}}]', 0, ()),
    (REV_ALL_ARM, '7c6bf9c3', 'ldr h3, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, 'b82b59c3', 'str w3, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'b82bd9c3', 'str w3, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'b82b69c3', 'str w3, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, 'b82b79c3', 'str w3, [x14, x11{, LSL{#2}}]', 0, ()),
    (REV_ALL_ARM, 'b82bf9c3', 'str w3, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, 'b86b59c3', 'ldr w3, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'b86bd9c3', 'ldr w3, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'b86b69c3', 'ldr w3, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, 'b86b79c3', 'ldr w3, [x14, x11{, LSL{#2}}]', 0, ()),
    (REV_ALL_ARM, 'b86bf9c3', 'ldr w3, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, 'b8ab59c3', 'ldrsw x3, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'b8abd9c3', 'ldrsw x3, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'b8ab69c3', 'ldrsw x3, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, 'b8ab79c3', 'ldrsw x3, [x14, x11{, LSL{#2}}]', 0, ()),
    (REV_ALL_ARM, 'b8abf9c3', 'ldrsw x3, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, 'bc2b59c3', 'str s3, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'bc2bd9c3', 'str s3, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'bc2b69c3', 'str s3, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, 'bc2b79c3', 'str s3, [x14, x11{, LSL{#2}}]', 0, ()),
    (REV_ALL_ARM, 'bc2bf9c3', 'str s3, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, 'bc6b59c3', 'ldr s3, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'bc6bd9c3', 'ldr s3, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'bc6b69c3', 'ldr s3, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, 'bc6b79c3', 'ldr s3, [x14, x11{, LSL{#2}}]', 0, ()),
    (REV_ALL_ARM, 'bc6bf9c3', 'ldr s3, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f82b59c3', 'str x3, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f82bd9c3', 'str x3, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f82b69c3', 'str x3, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f82b79c3', 'str x3, [x14, x11{, LSL{#3}}]', 0, ()),
    (REV_ALL_ARM, 'f82bf9c3', 'str x3, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f86b59c3', 'ldr x3, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f86bd9c3', 'ldr x3, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f86b69c3', 'ldr x3, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f86b79c3', 'ldr x3, [x14, x11{, LSL{#3}}]', 0, ()),
    (REV_ALL_ARM, 'f86bf9c3', 'ldr x3, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab59c0', 'prfm PLDL1KEEP, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab59c1', 'prfm PLDL1STRM, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab59c2', 'prfm PLDL2KEEP, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab59c3', 'prfm PLDL2STRM, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab59c4', 'prfm PLDL3KEEP, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab59c5', 'prfm PLDL3STRM, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab59c8', 'prfm PLIL1KEEP, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab59c9', 'prfm PLIL1STRM, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab59ca', 'prfm PLIL2KEEP, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab59cb', 'prfm PLIL2STRM, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab59cc', 'prfm PLIL3KEEP, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab59cd', 'prfm PLIL3STRM, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab59d0', 'prfm PSTL1KEEP, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab59d1', 'prfm PSTL1STRM, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab59d2', 'prfm PSTL2KEEP, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab59d3', 'prfm PSTL2STRM, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab59d4', 'prfm PSTL3KEEP, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab59d5', 'prfm PSTL3STRM, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abd9c0', 'prfm PLDL1KEEP, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abd9c1', 'prfm PLDL1STRM, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abd9c2', 'prfm PLDL2KEEP, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abd9c3', 'prfm PLDL2STRM, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abd9c4', 'prfm PLDL3KEEP, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abd9c5', 'prfm PLDL3STRM, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abd9c8', 'prfm PLIL1KEEP, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abd9c9', 'prfm PLIL1STRM, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abd9ca', 'prfm PLIL2KEEP, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abd9cb', 'prfm PLIL2STRM, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abd9cc', 'prfm PLIL3KEEP, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abd9cd', 'prfm PLIL3STRM, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abd9d0', 'prfm PSTL1KEEP, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abd9d1', 'prfm PSTL1STRM, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abd9d2', 'prfm PSTL2KEEP, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abd9d3', 'prfm PSTL2STRM, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abd9d4', 'prfm PSTL3KEEP, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abd9d5', 'prfm PSTL3STRM, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab69c0', 'prfm PLDL1KEEP, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab69c1', 'prfm PLDL1STRM, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab69c2', 'prfm PLDL2KEEP, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab69c3', 'prfm PLDL2STRM, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab69c4', 'prfm PLDL3KEEP, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab69c5', 'prfm PLDL3STRM, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab69c8', 'prfm PLIL1KEEP, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab69c9', 'prfm PLIL1STRM, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab69ca', 'prfm PLIL2KEEP, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab69cb', 'prfm PLIL2STRM, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab69cc', 'prfm PLIL3KEEP, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab69cd', 'prfm PLIL3STRM, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab69d0', 'prfm PSTL1KEEP, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab69d1', 'prfm PSTL1STRM, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab69d2', 'prfm PSTL2KEEP, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab69d3', 'prfm PSTL2STRM, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab69d4', 'prfm PSTL3KEEP, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab69d5', 'prfm PSTL3STRM, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab79c0', 'prfm PLDL1KEEP, [x14, x11{, LSL{#3}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab79c1', 'prfm PLDL1STRM, [x14, x11{, LSL{#3}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab79c2', 'prfm PLDL2KEEP, [x14, x11{, LSL{#3}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab79c3', 'prfm PLDL2STRM, [x14, x11{, LSL{#3}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab79c4', 'prfm PLDL3KEEP, [x14, x11{, LSL{#3}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab79c5', 'prfm PLDL3STRM, [x14, x11{, LSL{#3}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab79c8', 'prfm PLIL1KEEP, [x14, x11{, LSL{#3}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab79c9', 'prfm PLIL1STRM, [x14, x11{, LSL{#3}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab79ca', 'prfm PLIL2KEEP, [x14, x11{, LSL{#3}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab79cb', 'prfm PLIL2STRM, [x14, x11{, LSL{#3}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab79cc', 'prfm PLIL3KEEP, [x14, x11{, LSL{#3}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab79cd', 'prfm PLIL3STRM, [x14, x11{, LSL{#3}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab79d0', 'prfm PSTL1KEEP, [x14, x11{, LSL{#3}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab79d1', 'prfm PSTL1STRM, [x14, x11{, LSL{#3}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab79d2', 'prfm PSTL2KEEP, [x14, x11{, LSL{#3}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab79d3', 'prfm PSTL2STRM, [x14, x11{, LSL{#3}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab79d4', 'prfm PSTL3KEEP, [x14, x11{, LSL{#3}}]', 0, ()),
    (REV_ALL_ARM, 'f8ab79d5', 'prfm PSTL3STRM, [x14, x11{, LSL{#3}}]', 0, ()),
    (REV_ALL_ARM, 'f8abf9c0', 'prfm PLDL1KEEP, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abf9c1', 'prfm PLDL1STRM, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abf9c2', 'prfm PLDL2KEEP, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abf9c3', 'prfm PLDL2STRM, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abf9c4', 'prfm PLDL3KEEP, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abf9c5', 'prfm PLDL3STRM, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abf9c8', 'prfm PLIL1KEEP, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abf9c9', 'prfm PLIL1STRM, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abf9ca', 'prfm PLIL2KEEP, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abf9cb', 'prfm PLIL2STRM, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abf9cc', 'prfm PLIL3KEEP, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abf9cd', 'prfm PLIL3STRM, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abf9d0', 'prfm PSTL1KEEP, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abf9d1', 'prfm PSTL1STRM, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abf9d2', 'prfm PSTL2KEEP, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abf9d3', 'prfm PSTL2STRM, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abf9d4', 'prfm PSTL3KEEP, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, 'f8abf9d5', 'prfm PSTL3STRM, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, 'fc2b59c3', 'str d3, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'fc2bd9c3', 'str d3, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'fc2b69c3', 'str d3, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, 'fc2b79c3', 'str d3, [x14, x11{, LSL{#3}}]', 0, ()),
    (REV_ALL_ARM, 'fc2bf9c3', 'str d3, [x14, x11{, SXTX{#0}}]', 0, ()),
    (REV_ALL_ARM, 'fc6b59c3', 'ldr d3, [x14, w11{, UXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'fc6bd9c3', 'ldr d3, [x14, w11{, SXTW{#0}}]', 0, ()),
    (REV_ALL_ARM, 'fc6b69c3', 'ldr d3, [x14, x11{, LSL{#0}}]', 0, ()),
    (REV_ALL_ARM, 'fc6b79c3', 'ldr d3, [x14, x11{, LSL{#3}}]', 0, ()),
    (REV_ALL_ARM, 'fc6bf9c3', 'ldr d3, [x14, x11{, SXTX{#0}}]', 0, ()),
    
    #Load/store register (unsigned immediate)
    
    (REV_ALL_ARM, '3910f1c3', 'strb w3, [x14{, #43c}]', 0, ()),
    (REV_ALL_ARM, '3950f1c3', 'ldrb w3, [x14{, #43c}]', 0, ()),
    (REV_ALL_ARM, '3990f1c3', 'ldrsb x3, [x14{, #43c}]', 0, ()),
    (REV_ALL_ARM, '39d0f1c3', 'ldrsb w3, [x14{, #43c}]', 0, ()),
    (REV_ALL_ARM, '3d10f1c3', 'str b3, [x14{, #43c}]', 0, ()),
    (REV_ALL_ARM, '3d50f1c3', 'ldr b3, [x14{, #43c}]', 0, ()),
    (REV_ALL_ARM, '3d90f1c3', 'str q3, [x14{, #43c0}]', 0, ()),
    (REV_ALL_ARM, '3dd0f1c3', 'ldr q3, [x14{, #43c0}]', 0, ()),
    (REV_ALL_ARM, '7910f1c3', 'strh w3, [x14{, #878}]', 0, ()),
    (REV_ALL_ARM, '7950f1c3', 'ldrh w3, [x14{, #878}]', 0, ()),
    (REV_ALL_ARM, '7990f1c3', 'ldrsh x3, [x14{, #878}]', 0, ()),
    (REV_ALL_ARM, '79d0f1c3', 'ldrsh w3, [x14{, #878}]', 0, ()),
    (REV_ALL_ARM, '7d10f1c3', 'str h3, [x14{, #878}]', 0, ()),
    (REV_ALL_ARM, '7d50f1c3', 'ldr h3, [x14{, #878}]', 0, ()),
    (REV_ALL_ARM, 'b910f1c3', 'str w3, [x14{, #10f0}]', 0, ()),
    (REV_ALL_ARM, 'b950f1c3', 'ldr w3, [x14{, #10f0}]', 0, ()),
    (REV_ALL_ARM, 'b990f1c3', 'ldrsw x3, [x14{, #10f0}]', 0, ()),
    (REV_ALL_ARM, 'bd10f1c3', 'str s3, [x14{, #10f0}]', 0, ()),
    (REV_ALL_ARM, 'bd50f1c3', 'ldr s3, [x14{, #10f0}]', 0, ()),
    (REV_ALL_ARM, 'f910f1c3', 'str x3, [x14{, #21e0}]', 0, ()),
    (REV_ALL_ARM, 'f950f1c3', 'ldr x3, [x14{, #21e0}]', 0, ()),
    (REV_ALL_ARM, 'f990f1c0', 'prfm PLDL1KEEP, [x14{, #21e0}]', 0, ()),
    (REV_ALL_ARM, 'f990f1c1', 'prfm PLDL1STRM, [x14{, #21e0}]', 0, ()),
    (REV_ALL_ARM, 'f990f1c2', 'prfm PLDL2KEEP, [x14{, #21e0}]', 0, ()),
    (REV_ALL_ARM, 'f990f1c3', 'prfm PLDL2STRM, [x14{, #21e0}]', 0, ()),
    (REV_ALL_ARM, 'f990f1c4', 'prfm PLDL3KEEP, [x14{, #21e0}]', 0, ()),
    (REV_ALL_ARM, 'f990f1c5', 'prfm PLDL3STRM, [x14{, #21e0}]', 0, ()),
    (REV_ALL_ARM, 'f990f1c8', 'prfm PLIL1KEEP, [x14{, #21e0}]', 0, ()),
    (REV_ALL_ARM, 'f990f1c9', 'prfm PLIL1STRM, [x14{, #21e0}]', 0, ()),
    (REV_ALL_ARM, 'f990f1ca', 'prfm PLIL2KEEP, [x14{, #21e0}]', 0, ()),
    (REV_ALL_ARM, 'f990f1cb', 'prfm PLIL2STRM, [x14{, #21e0}]', 0, ()),
    (REV_ALL_ARM, 'f990f1cc', 'prfm PLIL3KEEP, [x14{, #21e0}]', 0, ()),
    (REV_ALL_ARM, 'f990f1cd', 'prfm PLIL3STRM, [x14{, #21e0}]', 0, ()),
    (REV_ALL_ARM, 'f990f1d0', 'prfm PSTL1KEEP, [x14{, #21e0}]', 0, ()),
    (REV_ALL_ARM, 'f990f1d1', 'prfm PSTL1STRM, [x14{, #21e0}]', 0, ()),
    (REV_ALL_ARM, 'f990f1d2', 'prfm PSTL2KEEP, [x14{, #21e0}]', 0, ()),
    (REV_ALL_ARM, 'f990f1d3', 'prfm PSTL2STRM, [x14{, #21e0}]', 0, ()),
    (REV_ALL_ARM, 'f990f1d4', 'prfm PSTL3KEEP, [x14{, #21e0}]', 0, ()),
    (REV_ALL_ARM, 'f990f1d5', 'prfm PSTL3STRM, [x14{, #21e0}]', 0, ()),
    (REV_ALL_ARM, 'fd10f1c3', 'str d3, [x14{, #21e0}]', 0, ()),
    (REV_ALL_ARM, 'fd50f1c3', 'ldr d3, [x14{, #21e0}]', 0, ()),
    
    #AdvSIMD load/store multiple structures
    
    #each set of 7 tests has a different mnemonic (disregarding shared st1/ld1 variants)
    #each set tests for all 7 possible values of <T>
    #all tests are for the no offset variants
    #st4
    (REV_ALL_ARM, '0c0001c3', 'st4 { v3.8b, v4.8b, v5.8b, v6.8b }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c0001c3', 'st4 { v3.16b, v4.16b, v5.16b, v6.16b }, [x14]', 0, ()),
    (REV_ALL_ARM, '0c0005c3', 'st4 { v3.4h, v4.4h, v5.4h, v6.4h }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c0005c3', 'st4 { v3.8h, v4.8h, v5.8h, v6.8h }, [x14]', 0, ()),
    (REV_ALL_ARM, '0c0009c3', 'st4 { v3.2s, v4.2s, v5.2s, v6.2s }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c0009c3', 'st4 { v3.4s, v4.4s, v5.4s, v6.4s }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c000dc3', 'st4 { v3.2d, v4.2d, v5.2d, v6.2d }, [x14]', 0, ()),
    #st1(4)
    (REV_ALL_ARM, '0c0021c3', 'st1 { v3.8b, v4.8b, v5.8b, v6.8b }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c0021c3', 'st1 { v3.16b, v4.16b, v5.16b, v6.16b }, [x14]', 0, ()),
    (REV_ALL_ARM, '0c0025c3', 'st1 { v3.4h, v4.4h, v5.4h, v6.4h }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c0025c3', 'st1 { v3.8h, v4.8h, v5.8h, v6.8h }, [x14]', 0, ()),
    (REV_ALL_ARM, '0c0029c3', 'st1 { v3.2s, v4.2s, v5.2s, v6.2s }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c0029c3', 'st1 { v3.4s, v4.4s, v5.4s, v6.4s }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c002dc3', 'st1 { v3.2d, v4.2d, v5.2d, v6.2d }, [x14]', 0, ()),
    #st3
    (REV_ALL_ARM, '0c0041c3', 'st3 { v3.8b, v4.8b, v5.8b }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c0041c3', 'st3 { v3.16b, v4.16b, v5.16b }, [x14]', 0, ()),
    (REV_ALL_ARM, '0c0045c3', 'st3 { v3.4h, v4.4h, v5.4h }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c0045c3', 'st3 { v3.8h, v4.8h, v5.8h }, [x14]', 0, ()),
    (REV_ALL_ARM, '0c0049c3', 'st3 { v3.2s, v4.2s, v5.2s }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c0049c3', 'st3 { v3.4s, v4.4s, v5.4s }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c004dc3', 'st3 { v3.2d, v4.2d, v5.2d }, [x14]', 0, ()),
    #st1(3)
    (REV_ALL_ARM, '0c0061c3', 'st1 { v3.8b, v4.8b, v5.8b }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c0061c3', 'st1 { v3.16b, v4.16b, v5.16b }, [x14]', 0, ()),
    (REV_ALL_ARM, '0c0065c3', 'st1 { v3.4h, v4.4h, v5.4h }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c0065c3', 'st1 { v3.8h, v4.8h, v5.8h }, [x14]', 0, ()),
    (REV_ALL_ARM, '0c0069c3', 'st1 { v3.2s, v4.2s, v5.2s }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c0069c3', 'st1 { v3.4s, v4.4s, v5.4s }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c006dc3', 'st1 { v3.2d, v4.2d, v5.2d }, [x14]', 0, ()),
    #st1(1)
    (REV_ALL_ARM, '0c0071c3', 'st1 { v3.8b }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c0071c3', 'st1 { v3.16b }, [x14]', 0, ()),
    (REV_ALL_ARM, '0c0075c3', 'st1 { v3.4h }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c0075c3', 'st1 { v3.8h }, [x14]', 0, ()),
    (REV_ALL_ARM, '0c0079c3', 'st1 { v3.2s }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c0079c3', 'st1 { v3.4s }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c007dc3', 'st1 { v3.2d }, [x14]', 0, ()),
    #st2
    (REV_ALL_ARM, '0c0081c3', 'st2 { v3.8b, v4.8b }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c0081c3', 'st2 { v3.16b, v4.16b }, [x14]', 0, ()),
    (REV_ALL_ARM, '0c0085c3', 'st2 { v3.4h, v4.4h }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c0085c3', 'st2 { v3.8h, v4.8h }, [x14]', 0, ()),
    (REV_ALL_ARM, '0c0089c3', 'st2 { v3.2s, v4.2s }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c0089c3', 'st2 { v3.4s, v4.4s }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c008dc3', 'st2 { v3.2d, v4.2d }, [x14]', 0, ()),
    #st1(2)
    (REV_ALL_ARM, '0c00a1c3', 'st1 { v3.8b, v4.8b }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c00a1c3', 'st1 { v3.16b, v4.16b }, [x14]', 0, ()),
    (REV_ALL_ARM, '0c00a5c3', 'st1 { v3.4h, v4.4h }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c00a5c3', 'st1 { v3.8h, v4.8h }, [x14]', 0, ()),
    (REV_ALL_ARM, '0c00a9c3', 'st1 { v3.2s, v4.2s }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c00a9c3', 'st1 { v3.4s, v4.4s }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c00adc3', 'st1 { v3.2d, v4.2d }, [x14]', 0, ()),
    #ld4
    (REV_ALL_ARM, '0c4001c3', 'ld4 { v3.8b, v4.8b, v5.8b, v6.8b }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c4001c3', 'ld4 { v3.16b, v4.16b, v5.16b, v6.16b }, [x14]', 0, ()),
    (REV_ALL_ARM, '0c4005c3', 'ld4 { v3.4h, v4.4h, v5.4h, v6.4h }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c4005c3', 'ld4 { v3.8h, v4.8h, v5.8h, v6.8h }, [x14]', 0, ()),
    (REV_ALL_ARM, '0c4009c3', 'ld4 { v3.2s, v4.2s, v5.2s, v6.2s }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c4009c3', 'ld4 { v3.4s, v4.4s, v5.4s, v6.4s }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c400dc3', 'ld4 { v3.2d, v4.2d, v5.2d, v6.2d }, [x14]', 0, ()),
    #ld1(4)
    (REV_ALL_ARM, '0c4021c3', 'ld1 { v3.8b, v4.8b, v5.8b, v6.8b }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c4021c3', 'ld1 { v3.16b, v4.16b, v5.16b, v6.16b }, [x14]', 0, ()),
    (REV_ALL_ARM, '0c4025c3', 'ld1 { v3.4h, v4.4h, v5.4h, v6.4h }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c4025c3', 'ld1 { v3.8h, v4.8h, v5.8h, v6.8h }, [x14]', 0, ()),
    (REV_ALL_ARM, '0c4029c3', 'ld1 { v3.2s, v4.2s, v5.2s, v6.2s }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c4029c3', 'ld1 { v3.4s, v4.4s, v5.4s, v6.4s }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c402dc3', 'ld1 { v3.2d, v4.2d, v5.2d, v6.2d }, [x14]', 0, ()),
    #ld3
    (REV_ALL_ARM, '0c4041c3', 'ld3 { v3.8b, v4.8b, v5.8b }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c4041c3', 'ld3 { v3.16b, v4.16b, v5.16b }, [x14]', 0, ()),
    (REV_ALL_ARM, '0c4045c3', 'ld3 { v3.4h, v4.4h, v5.4h }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c4045c3', 'ld3 { v3.8h, v4.8h, v5.8h }, [x14]', 0, ()),
    (REV_ALL_ARM, '0c4049c3', 'ld3 { v3.2s, v4.2s, v5.2s }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c4049c3', 'ld3 { v3.4s, v4.4s, v5.4s }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c404dc3', 'ld3 { v3.2d, v4.2d, v5.2d }, [x14]', 0, ()),
    #ld1(3)
    (REV_ALL_ARM, '0c4061c3', 'ld1 { v3.8b, v4.8b, v5.8b }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c4061c3', 'ld1 { v3.16b, v4.16b, v5.16b }, [x14]', 0, ()),
    (REV_ALL_ARM, '0c4065c3', 'ld1 { v3.4h, v4.4h, v5.4h }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c4065c3', 'ld1 { v3.8h, v4.8h, v5.8h }, [x14]', 0, ()),
    (REV_ALL_ARM, '0c4069c3', 'ld1 { v3.2s, v4.2s, v5.2s }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c4069c3', 'ld1 { v3.4s, v4.4s, v5.4s }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c406dc3', 'ld1 { v3.2d, v4.2d, v5.2d }, [x14]', 0, ()),
    #ld1(1)
    (REV_ALL_ARM, '0c4071c3', 'ld1 { v3.8b }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c4071c3', 'ld1 { v3.16b }, [x14]', 0, ()),
    (REV_ALL_ARM, '0c4075c3', 'ld1 { v3.4h }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c4075c3', 'ld1 { v3.8h }, [x14]', 0, ()),
    (REV_ALL_ARM, '0c4079c3', 'ld1 { v3.2s }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c4079c3', 'ld1 { v3.4s }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c407dc3', 'ld1 { v3.2d }, [x14]', 0, ()),
    #ld2
    (REV_ALL_ARM, '0c4081c3', 'ld2 { v3.8b, v4.8b }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c4081c3', 'ld2 { v3.16b, v4.16b }, [x14]', 0, ()),
    (REV_ALL_ARM, '0c4085c3', 'ld2 { v3.4h, v4.4h }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c4085c3', 'ld2 { v3.8h, v4.8h }, [x14]', 0, ()),
    (REV_ALL_ARM, '0c4089c3', 'ld2 { v3.2s, v4.2s }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c4089c3', 'ld2 { v3.4s, v4.4s }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c408dc3', 'ld2 { v3.2d, v4.2d }, [x14]', 0, ()),
    #ld1(2)
    (REV_ALL_ARM, '0c40a1c3', 'ld1 { v3.8b, v4.8b }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c40a1c3', 'ld1 { v3.16b, v4.16b }, [x14]', 0, ()),
    (REV_ALL_ARM, '0c40a5c3', 'ld1 { v3.4h, v4.4h }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c40a5c3', 'ld1 { v3.8h, v4.8h }, [x14]', 0, ()),
    (REV_ALL_ARM, '0c40a9c3', 'ld1 { v3.2s, v4.2s }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c40a9c3', 'ld1 { v3.4s, v4.4s }, [x14]', 0, ()),
    (REV_ALL_ARM, '4c40adc3', 'ld1 { v3.2d, v4.2d }, [x14]', 0, ()),
    
    #AdvSIMD Load/store multiple structures (post-indexed)

    #each set of 7 tests has a different mnemonic (disregarding shared st1/ld1 variants)
    #each set tests for all 7 possible values of <T>
    #st4 (register offset)
    (REV_ALL_ARM, '0c8b01c3', 'st4 { v3.8b, v4.8b, v5.8b, v6.8b }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4c8b01c3', 'st4 { v3.16b, v4.16b, v5.16b, v6.16b }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '0c8b05c3', 'st4 { v3.4h, v4.4h, v5.4h, v6.4h }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4c8b05c3', 'st4 { v3.8h, v4.8h, v5.8h, v6.8h }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '0c8b09c3', 'st4 { v3.2s, v4.2s, v5.2s, v6.2s }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4c8b09c3', 'st4 { v3.4s, v4.4s, v5.4s, v6.4s }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4c8b0dc3', 'st4 { v3.2d, v4.2d, v5.2d, v6.2d }, [x14], x11', 0, ()),
    #st1(4) (register offset)
    (REV_ALL_ARM, '0c8b21c3', 'st1 { v3.8b, v4.8b, v5.8b, v6.8b }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4c8b21c3', 'st1 { v3.16b, v4.16b, v5.16b, v6.16b }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '0c8b25c3', 'st1 { v3.4h, v4.4h, v5.4h, v6.4h }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4c8b25c3', 'st1 { v3.8h, v4.8h, v5.8h, v6.8h }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '0c8b29c3', 'st1 { v3.2s, v4.2s, v5.2s, v6.2s }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4c8b29c3', 'st1 { v3.4s, v4.4s, v5.4s, v6.4s }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4c8b2dc3', 'st1 { v3.2d, v4.2d, v5.2d, v6.2d }, [x14], x11', 0, ()),
    #st3 (register offset)
    (REV_ALL_ARM, '0c8b41c3', 'st3 { v3.8b, v4.8b, v5.8b }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4c8b41c3', 'st3 { v3.16b, v4.16b, v5.16b }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '0c8b45c3', 'st3 { v3.4h, v4.4h, v5.4h }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4c8b45c3', 'st3 { v3.8h, v4.8h, v5.8h }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '0c8b49c3', 'st3 { v3.2s, v4.2s, v5.2s }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4c8b49c3', 'st3 { v3.4s, v4.4s, v5.4s }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4c8b4dc3', 'st3 { v3.2d, v4.2d, v5.2d }, [x14], x11', 0, ()),
    #st1(3) (register offset)
    (REV_ALL_ARM, '0c8b61c3', 'st1 { v3.8b, v4.8b, v5.8b }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4c8b61c3', 'st1 { v3.16b, v4.16b, v5.16b }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '0c8b65c3', 'st1 { v3.4h, v4.4h, v5.4h }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4c8b65c3', 'st1 { v3.8h, v4.8h, v5.8h }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '0c8b69c3', 'st1 { v3.2s, v4.2s, v5.2s }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4c8b69c3', 'st1 { v3.4s, v4.4s, v5.4s }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4c8b6dc3', 'st1 { v3.2d, v4.2d, v5.2d }, [x14], x11', 0, ()),
    #st1(1) (register offset)
    (REV_ALL_ARM, '0c8b71c3', 'st1 { v3.8b }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4c8b71c3', 'st1 { v3.16b }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '0c8b75c3', 'st1 { v3.4h }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4c8b75c3', 'st1 { v3.8h }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '0c8b79c3', 'st1 { v3.2s }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4c8b79c3', 'st1 { v3.4s }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4c8b7dc3', 'st1 { v3.2d }, [x14], x11', 0, ()),
    #st2 (register offset)
    (REV_ALL_ARM, '0c8b81c3', 'st2 { v3.8b, v4.8b }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4c8b81c3', 'st2 { v3.16b, v4.16b }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '0c8b85c3', 'st2 { v3.4h, v4.4h }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4c8b85c3', 'st2 { v3.8h, v4.8h }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '0c8b89c3', 'st2 { v3.2s, v4.2s }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4c8b89c3', 'st2 { v3.4s, v4.4s }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4c8b8dc3', 'st2 { v3.2d, v4.2d }, [x14], x11', 0, ()),
    #st1(2) (register offset)
    (REV_ALL_ARM, '0c8ba1c3', 'st1 { v3.8b, v4.8b }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4c8ba1c3', 'st1 { v3.16b, v4.16b }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '0c8ba5c3', 'st1 { v3.4h, v4.4h }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4c8ba5c3', 'st1 { v3.8h, v4.8h }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '0c8ba9c3', 'st1 { v3.2s, v4.2s }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4c8ba9c3', 'st1 { v3.4s, v4.4s }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4c8badc3', 'st1 { v3.2d, v4.2d }, [x14], x11', 0, ()),
    #st4 (immediate offset)
    (REV_ALL_ARM, '0c9f01c3', 'st4 { v3.8b, v4.8b, v5.8b, v6.8b }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4c9f01c3', 'st4 { v3.16b, v4.16b, v5.16b, v6.16b }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '0c9f05c3', 'st4 { v3.4h, v4.4h, v5.4h, v6.4h }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4c9f05c3', 'st4 { v3.8h, v4.8h, v5.8h, v6.8h }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '0c9f09c3', 'st4 { v3.2s, v4.2s, v5.2s, v6.2s }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4c9f09c3', 'st4 { v3.4s, v4.4s, v5.4s, v6.4s }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '4c9f0dc3', 'st4 { v3.2d, v4.2d, v5.2d, v6.2d }, [x14], #64', 0, ()),
    #st1(4) (immediate offset)
    (REV_ALL_ARM, '0c9f21c3', 'st1 { v3.8b, v4.8b, v5.8b, v6.8b }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4c9f21c3', 'st1 { v3.16b, v4.16b, v5.16b, v6.16b }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '0c9f25c3', 'st1 { v3.4h, v4.4h, v5.4h, v6.4h }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4c9f25c3', 'st1 { v3.8h, v4.8h, v5.8h, v6.8h }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '0c9f29c3', 'st1 { v3.2s, v4.2s, v5.2s, v6.2s }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4c9f29c3', 'st1 { v3.4s, v4.4s, v5.4s, v6.4s }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '4c9f2dc3', 'st1 { v3.2d, v4.2d, v5.2d, v6.2d }, [x14], #64', 0, ()),
    #st3 (immediate offset)
    (REV_ALL_ARM, '0c9f41c3', 'st3 { v3.8b, v4.8b, v5.8b }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4c9f41c3', 'st3 { v3.16b, v4.16b, v5.16b }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '0c9f45c3', 'st3 { v3.4h, v4.4h, v5.4h }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4c9f45c3', 'st3 { v3.8h, v4.8h, v5.8h }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '0c9f49c3', 'st3 { v3.2s, v4.2s, v5.2s }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4c9f49c3', 'st3 { v3.4s, v4.4s, v5.4s }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '4c9f4dc3', 'st3 { v3.2d, v4.2d, v5.2d }, [x14], #64', 0, ()),
    #st1(3) (immediate offset)
    (REV_ALL_ARM, '0c9f61c3', 'st1 { v3.8b, v4.8b, v5.8b }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4c9f61c3', 'st1 { v3.16b, v4.16b, v5.16b }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '0c9f65c3', 'st1 { v3.4h, v4.4h, v5.4h }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4c9f65c3', 'st1 { v3.8h, v4.8h, v5.8h }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '0c9f69c3', 'st1 { v3.2s, v4.2s, v5.2s }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4c9f69c3', 'st1 { v3.4s, v4.4s, v5.4s }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '4c9f6dc3', 'st1 { v3.2d, v4.2d, v5.2d }, [x14], #64', 0, ()),
    #st1(1) (immediate offset)
    (REV_ALL_ARM, '0c9f71c3', 'st1 { v3.8b }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4c9f71c3', 'st1 { v3.16b }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '0c9f75c3', 'st1 { v3.4h }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4c9f75c3', 'st1 { v3.8h }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '0c9f79c3', 'st1 { v3.2s }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4c9f79c3', 'st1 { v3.4s }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '4c9f7dc3', 'st1 { v3.2d }, [x14], #64', 0, ()),
    #st2 (immediate offset)
    (REV_ALL_ARM, '0c9f81c3', 'st2 { v3.8b, v4.8b }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4c9f81c3', 'st2 { v3.16b, v4.16b }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '0c9f85c3', 'st2 { v3.4h, v4.4h }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4c9f85c3', 'st2 { v3.8h, v4.8h }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '0c9f89c3', 'st2 { v3.2s, v4.2s }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4c9f89c3', 'st2 { v3.4s, v4.4s }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '4c9f8dc3', 'st2 { v3.2d, v4.2d }, [x14], #64', 0, ()),
    #st1(2) (immediate offset)
    (REV_ALL_ARM, '0c9fa1c3', 'st1 { v3.8b, v4.8b }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4c9fa1c3', 'st1 { v3.16b, v4.16b }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '0c9fa5c3', 'st1 { v3.4h, v4.4h }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4c9fa5c3', 'st1 { v3.8h, v4.8h }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '0c9fa9c3', 'st1 { v3.2s, v4.2s }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4c9fa9c3', 'st1 { v3.4s, v4.4s }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '4c9fadc3', 'st1 { v3.2d, v4.2d }, [x14], #64', 0, ()),
    #ld4 (register offset)
    (REV_ALL_ARM, '0ccb01c3', 'ld4 { v3.8b, v4.8b, v5.8b, v6.8b }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4ccb01c3', 'ld4 { v3.16b, v4.16b, v5.16b, v6.16b }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '0ccb05c3', 'ld4 { v3.4h, v4.4h, v5.4h, v6.4h }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4ccb05c3', 'ld4 { v3.8h, v4.8h, v5.8h, v6.8h }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '0ccb09c3', 'ld4 { v3.2s, v4.2s, v5.2s, v6.2s }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4ccb09c3', 'ld4 { v3.4s, v4.4s, v5.4s, v6.4s }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4ccb0dc3', 'ld4 { v3.2d, v4.2d, v5.2d, v6.2d }, [x14], x11', 0, ()),
    #ld1(4) (register offset)
    (REV_ALL_ARM, '0ccb21c3', 'ld1 { v3.8b, v4.8b, v5.8b, v6.8b }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4ccb21c3', 'ld1 { v3.16b, v4.16b, v5.16b, v6.16b }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '0ccb25c3', 'ld1 { v3.4h, v4.4h, v5.4h, v6.4h }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4ccb25c3', 'ld1 { v3.8h, v4.8h, v5.8h, v6.8h }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '0ccb29c3', 'ld1 { v3.2s, v4.2s, v5.2s, v6.2s }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4ccb29c3', 'ld1 { v3.4s, v4.4s, v5.4s, v6.4s }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4ccb2dc3', 'ld1 { v3.2d, v4.2d, v5.2d, v6.2d }, [x14], x11', 0, ()),
    #ld3 (register offset)
    (REV_ALL_ARM, '0ccb41c3', 'ld3 { v3.8b, v4.8b, v5.8b }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4ccb41c3', 'ld3 { v3.16b, v4.16b, v5.16b }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '0ccb45c3', 'ld3 { v3.4h, v4.4h, v5.4h }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4ccb45c3', 'ld3 { v3.8h, v4.8h, v5.8h }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '0ccb49c3', 'ld3 { v3.2s, v4.2s, v5.2s }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4ccb49c3', 'ld3 { v3.4s, v4.4s, v5.4s }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4ccb4dc3', 'ld3 { v3.2d, v4.2d, v5.2d }, [x14], x11', 0, ()),
    #ld1(3) (register offset)
    (REV_ALL_ARM, '0ccb61c3', 'ld1 { v3.8b, v4.8b, v5.8b }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4ccb61c3', 'ld1 { v3.16b, v4.16b, v5.16b }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '0ccb65c3', 'ld1 { v3.4h, v4.4h, v5.4h }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4ccb65c3', 'ld1 { v3.8h, v4.8h, v5.8h }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '0ccb69c3', 'ld1 { v3.2s, v4.2s, v5.2s }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4ccb69c3', 'ld1 { v3.4s, v4.4s, v5.4s }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4ccb6dc3', 'ld1 { v3.2d, v4.2d, v5.2d }, [x14], x11', 0, ()),
    #ld1(1) (register offset)
    (REV_ALL_ARM, '0ccb71c3', 'ld1 { v3.8b }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4ccb71c3', 'ld1 { v3.16b }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '0ccb75c3', 'ld1 { v3.4h }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4ccb75c3', 'ld1 { v3.8h }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '0ccb79c3', 'ld1 { v3.2s }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4ccb79c3', 'ld1 { v3.4s }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4ccb7dc3', 'ld1 { v3.2d }, [x14], x11', 0, ()),
    #ld2 (register offset)
    (REV_ALL_ARM, '0ccb81c3', 'ld2 { v3.8b, v4.8b }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4ccb81c3', 'ld2 { v3.16b, v4.16b }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '0ccb85c3', 'ld2 { v3.4h, v4.4h }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4ccb85c3', 'ld2 { v3.8h, v4.8h }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '0ccb89c3', 'ld2 { v3.2s, v4.2s }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4ccb89c3', 'ld2 { v3.4s, v4.4s }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4ccb8dc3', 'ld2 { v3.2d, v4.2d }, [x14], x11', 0, ()),
    #ld1(2) (register offset)
    (REV_ALL_ARM, '0ccba1c3', 'ld1 { v3.8b, v4.8b }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4ccba1c3', 'ld1 { v3.16b, v4.16b }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '0ccba5c3', 'ld1 { v3.4h, v4.4h }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4ccba5c3', 'ld1 { v3.8h, v4.8h }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '0ccba9c3', 'ld1 { v3.2s, v4.2s }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4ccba9c3', 'ld1 { v3.4s, v4.4s }, [x14], x11', 0, ()),
    (REV_ALL_ARM, '4ccbadc3', 'ld1 { v3.2d, v4.2d }, [x14], x11', 0, ()),
    #ld4 (immediate offset)
    (REV_ALL_ARM, '0cdf01c3', 'ld4 { v3.8b, v4.8b, v5.8b, v6.8b }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4cdf01c3', 'ld4 { v3.16b, v4.16b, v5.16b, v6.16b }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '0cdf05c3', 'ld4 { v3.4h, v4.4h, v5.4h, v6.4h }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4cdf05c3', 'ld4 { v3.8h, v4.8h, v5.8h, v6.8h }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '0cdf09c3', 'ld4 { v3.2s, v4.2s, v5.2s, v6.2s }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4cdf09c3', 'ld4 { v3.4s, v4.4s, v5.4s, v6.4s }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '4cdf0dc3', 'ld4 { v3.2d, v4.2d, v5.2d, v6.2d }, [x14], #64', 0, ()),
    #ld1(4) (immediate offset)
    (REV_ALL_ARM, '0cdf21c3', 'ld1 { v3.8b, v4.8b, v5.8b, v6.8b }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4cdf21c3', 'ld1 { v3.16b, v4.16b, v5.16b, v6.16b }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '0cdf25c3', 'ld1 { v3.4h, v4.4h, v5.4h, v6.4h }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4cdf25c3', 'ld1 { v3.8h, v4.8h, v5.8h, v6.8h }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '0cdf29c3', 'ld1 { v3.2s, v4.2s, v5.2s, v6.2s }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4cdf29c3', 'ld1 { v3.4s, v4.4s, v5.4s, v6.4s }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '4cdf2dc3', 'ld1 { v3.2d, v4.2d, v5.2d, v6.2d }, [x14], #64', 0, ()),
    #ld3 (immediate offset)
    (REV_ALL_ARM, '0cdf41c3', 'ld3 { v3.8b, v4.8b, v5.8b }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4cdf41c3', 'ld3 { v3.16b, v4.16b, v5.16b }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '0cdf45c3', 'ld3 { v3.4h, v4.4h, v5.4h }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4cdf45c3', 'ld3 { v3.8h, v4.8h, v5.8h }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '0cdf49c3', 'ld3 { v3.2s, v4.2s, v5.2s }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4cdf49c3', 'ld3 { v3.4s, v4.4s, v5.4s }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '4cdf4dc3', 'ld3 { v3.2d, v4.2d, v5.2d }, [x14], #64', 0, ()),
    #ld1(3) (immediate offset)
    (REV_ALL_ARM, '0cdf61c3', 'ld1 { v3.8b, v4.8b, v5.8b }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4cdf61c3', 'ld1 { v3.16b, v4.16b, v5.16b }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '0cdf65c3', 'ld1 { v3.4h, v4.4h, v5.4h }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4cdf65c3', 'ld1 { v3.8h, v4.8h, v5.8h }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '0cdf69c3', 'ld1 { v3.2s, v4.2s, v5.2s }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4cdf69c3', 'ld1 { v3.4s, v4.4s, v5.4s }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '4cdf6dc3', 'ld1 { v3.2d, v4.2d, v5.2d }, [x14], #64', 0, ()),
    #ld1(1) (immediate offset)
    (REV_ALL_ARM, '0cdf71c3', 'ld1 { v3.8b }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4cdf71c3', 'ld1 { v3.16b }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '0cdf75c3', 'ld1 { v3.4h }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4cdf75c3', 'ld1 { v3.8h }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '0cdf79c3', 'ld1 { v3.2s }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4cdf79c3', 'ld1 { v3.4s }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '4cdf7dc3', 'ld1 { v3.2d }, [x14], #64', 0, ()),
    #ld2 (immediate offset)
    (REV_ALL_ARM, '0cdf81c3', 'ld2 { v3.8b, v4.8b }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4cdf81c3', 'ld2 { v3.16b, v4.16b }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '0cdf85c3', 'ld2 { v3.4h, v4.4h }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4cdf85c3', 'ld2 { v3.8h, v4.8h }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '0cdf89c3', 'ld2 { v3.2s, v4.2s }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4cdf89c3', 'ld2 { v3.4s, v4.4s }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '4cdf8dc3', 'ld2 { v3.2d, v4.2d }, [x14], #64', 0, ()),
    #ld1(2) (immediate offset)
    (REV_ALL_ARM, '0cdfa1c3', 'ld1 { v3.8b, v4.8b }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4cdfa1c3', 'ld1 { v3.16b, v4.16b }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '0cdfa5c3', 'ld1 { v3.4h, v4.4h }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4cdfa5c3', 'ld1 { v3.8h, v4.8h }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '0cdfa9c3', 'ld1 { v3.2s, v4.2s }, [x14], #32', 0, ()),
    (REV_ALL_ARM, '4cdfa9c3', 'ld1 { v3.4s, v4.4s }, [x14], #64', 0, ()),
    (REV_ALL_ARM, '4cdfadc3', 'ld1 { v3.2d, v4.2d }, [x14], #64', 0, ()),

    #AdvSIMD Load/store single structure
    
    #FIXME bitwise concatenation
    #all tests are for the no offset variants
    #st1 and st3
    (REV_ALL_ARM, '4d0019c3', 'st1 { v3.b }[#e], x14', 0, ()),
    (REV_ALL_ARM, '4d0039c3', 'st3 { v3.b, v4.b, v5.b }[#e], x14', 0, ()),
    (REV_ALL_ARM, '4d0059c3', 'st1 { v3.h }[#6], x14', 0, ()),
    (REV_ALL_ARM, '4d0079c3', 'st3 { v3.h, v4.h, v5.h }[#6], x14', 0, ()),
    (REV_ALL_ARM, '4d0091c3', 'st1 { v3.s }[#3], x14', 0, ()),
    (REV_ALL_ARM, '4d0085c3', 'st1 { v3.d }[#1], x14', 0, ()),
    (REV_ALL_ARM, '4d00b1c3', 'st3 { v3.s, v4.s, v5.s }[#3], x14', 0, ()),
    (REV_ALL_ARM, '4d00a5c3', 'st3 { v3.d, v4.d, v5.d }[#1], x14', 0, ()),
    #st2 and st4
    (REV_ALL_ARM, '4d2019c3', 'st2 { v3.b, v4.b }[#e], x14', 0, ()),
    (REV_ALL_ARM, '4d2039c3', 'st4 { v3.b, v4.b, v5.b, v6.b }[#e], x14', 0, ()),
    (REV_ALL_ARM, '4d2059c3', 'st2 { v3.h, v4.h }[#6], x14', 0, ()),
    (REV_ALL_ARM, '4d2079c3', 'st4 { v3.h, v4.h, v5.h, v6.h }[#6], x14', 0, ()),
    (REV_ALL_ARM, '4d2091c3', 'st2 { v3.s, v4.s }[#3], x14', 0, ()),
    (REV_ALL_ARM, '4d2085c3', 'st2 { v3.d, v4.d }[#1], x14', 0, ()),
    (REV_ALL_ARM, '4d20b1c3', 'st4 { v3.s, v4.s, v5.s, v6.s }[#3], x14', 0, ()),
    (REV_ALL_ARM, '4d20a5c3', 'st4 { v3.d, v4.d, v5.d, v6.d }[#1], x14', 0, ()),
    #ld1 and ld3 
    (REV_ALL_ARM, '4d4019c3', 'ld1 { v3.b }[#e], x14', 0, ()),
    (REV_ALL_ARM, '4d4039c3', 'ld3 { v3.b, v4.b, v5.b }[#e], x14', 0, ()),
    (REV_ALL_ARM, '4d4059c3', 'ld1 { v3.h }[#6], x14', 0, ()),
    (REV_ALL_ARM, '4d4079c3', 'ld3 { v3.h, v4.h, v5.h }[#6], x14', 0, ()),
    (REV_ALL_ARM, '4d4091c3', 'ld1 { v3.s }[#3], x14', 0, ()),
    (REV_ALL_ARM, '4d4085c3', 'ld1 { v3.d }[#1], x14', 0, ()),
    (REV_ALL_ARM, '4d40b1c3', 'ld3 { v3.s, v4.s, v5.s }[#3], x14', 0, ()),
    (REV_ALL_ARM, '4d40a5c3', 'ld3 { v3.d, v4.d, v5.d }[#1], x14', 0, ()),
    #ld1r
    (REV_ALL_ARM, '0d40c1c3', 'ld1r { v3.8b }, x14', 0, ()),
    (REV_ALL_ARM, '4d40c1c3', 'ld1r { v3.16b }, x14', 0, ()),
    (REV_ALL_ARM, '0d40c5c3', 'ld1r { v3.4h }, x14', 0, ()),
    (REV_ALL_ARM, '4d40c5c3', 'ld1r { v3.8h }, x14', 0, ()),
    (REV_ALL_ARM, '0d40c9c3', 'ld1r { v3.2s }, x14', 0, ()),
    (REV_ALL_ARM, '4d40c9c3', 'ld1r { v3.4s }, x14', 0, ()),
    (REV_ALL_ARM, '0d40cdc3', 'ld1r { v3.1d }, x14', 0, ()),
    (REV_ALL_ARM, '4d40cdc3', 'ld1r { v3.2d }, x14', 0, ()),
    #ld3r 
    (REV_ALL_ARM, '0d40e1c3', 'ld3r { v3.8b, v4.8b, v5.8b }, x14', 0, ()),
    (REV_ALL_ARM, '4d40e1c3', 'ld3r { v3.16b, v4.16b, v5.16b }, x14', 0, ()),
    (REV_ALL_ARM, '0d40e5c3', 'ld3r { v3.4h, v4.4h, v5.4h }, x14', 0, ()),
    (REV_ALL_ARM, '4d40e5c3', 'ld3r { v3.8h, v4.8h, v5.8h }, x14', 0, ()),
    (REV_ALL_ARM, '0d40e9c3', 'ld3r { v3.2s, v4.2s, v5.2s }, x14', 0, ()),
    (REV_ALL_ARM, '4d40e9c3', 'ld3r { v3.4s, v4.4s, v5.4s }, x14', 0, ()),
    (REV_ALL_ARM, '0d40edc3', 'ld3r { v3.1d, v4.1d, v5.1d }, x14', 0, ()),
    (REV_ALL_ARM, '4d40edc3', 'ld3r { v3.2d, v4.2d, v5.2d }, x14', 0, ()),
    #ld2 and ld4 
    (REV_ALL_ARM, '4d6019c3', 'ld2 { v3.b, v4.b }[#e], x14', 0, ()),
    (REV_ALL_ARM, '4d6039c3', 'ld4 { v3.b, v4.b, v5.b, v6.b }[#e], x14', 0, ()),
    (REV_ALL_ARM, '4d6059c3', 'ld2 { v3.h, v4.h }[#6], x14', 0, ()),
    (REV_ALL_ARM, '4d6079c3', 'ld4 { v3.h, v4.h, v5.h, v6.h }[#6], x14', 0, ()),
    (REV_ALL_ARM, '4d6091c3', 'ld2 { v3.s, v4.s }[#3], x14', 0, ()),
    (REV_ALL_ARM, '4d6085c3', 'ld2 { v3.d, v4.d }[#1], x14', 0, ()),
    (REV_ALL_ARM, '4d60b1c3', 'ld4 { v3.s, v4.s, v5.s, v6.s }[#3], x14', 0, ()),
    (REV_ALL_ARM, '4d60a5c3', 'ld4 { v3.d, v4.d, v5.d, v6.d }[#1], x14', 0, ()),
    #ld2r
    (REV_ALL_ARM, '0d60c1c3', 'ld2r { v3.8b, v4.8b }, x14', 0, ()),
    (REV_ALL_ARM, '4d60c1c3', 'ld2r { v3.16b, v4.16b }, x14', 0, ()),
    (REV_ALL_ARM, '0d60c5c3', 'ld2r { v3.4h, v4.4h }, x14', 0, ()),
    (REV_ALL_ARM, '4d60c5c3', 'ld2r { v3.8h, v4.8h }, x14', 0, ()),
    (REV_ALL_ARM, '0d60c9c3', 'ld2r { v3.2s, v4.2s }, x14', 0, ()),
    (REV_ALL_ARM, '4d60c9c3', 'ld2r { v3.4s, v4.4s }, x14', 0, ()),
    (REV_ALL_ARM, '0d60cdc3', 'ld2r { v3.1d, v4.1d }, x14', 0, ()),
    (REV_ALL_ARM, '4d60cdc3', 'ld2r { v3.2d, v4.2d }, x14', 0, ()),
    #ld4r 
    (REV_ALL_ARM, '0d60e1c3', 'ld4r { v3.8b, v4.8b, v5.8b, v6.8b }, x14', 0, ()),
    (REV_ALL_ARM, '4d60e1c3', 'ld4r { v3.16b, v4.16b, v5.16b, v6.16b }, x14', 0, ()),
    (REV_ALL_ARM, '0d60e5c3', 'ld4r { v3.4h, v4.4h, v5.4h, v6.4h }, x14', 0, ()),
    (REV_ALL_ARM, '4d60e5c3', 'ld4r { v3.8h, v4.8h, v5.8h, v6.8h }, x14', 0, ()),
    (REV_ALL_ARM, '0d60e9c3', 'ld4r { v3.2s, v4.2s, v5.2s, v6.2s }, x14', 0, ()),
    (REV_ALL_ARM, '4d60e9c3', 'ld4r { v3.4s, v4.4s, v5.4s, v6.4s }, x14', 0, ()),
    (REV_ALL_ARM, '0d60edc3', 'ld4r { v3.1d, v4.1d, v5.1d, v6.1d }, x14', 0, ()),
    (REV_ALL_ARM, '4d60edc3', 'ld4r { v3.2d, v4.2d, v5.2d, v6.2d }, x14', 0, ()),
    
    #AdvSIMD Load/store single structure (post-indexed)
    
    #st1 and st3 (register offset)
    (REV_ALL_ARM, '4e8b19c3', 'st1 { v3.b }[#e], x14, x11', 0, ()),
    (REV_ALL_ARM, '4e8b39c3', 'st3 { v3.b, v4.b, v5.b }[#e], x14, x11', 0, ()),
    (REV_ALL_ARM, '4e8b59c3', 'st1 { v3.h }[#6], x14, x11', 0, ()),
    (REV_ALL_ARM, '4e8b79c3', 'st3 { v3.h, v4.h, v5.h }[#6], x14, x11', 0, ()),
    (REV_ALL_ARM, '4e8b91c3', 'st1 { v3.s }[#3], x14, x11', 0, ()),
    (REV_ALL_ARM, '4e8b85c3', 'st1 { v3.d }[#1], x14, x11', 0, ()),
    (REV_ALL_ARM, '4e8bb1c3', 'st3 { v3.s, v4.s, v5.s }[#3], x14, x11', 0, ()),
    (REV_ALL_ARM, '4e8ba5c3', 'st3 { v3.d, v4.d, v5.d }[#1], x14, x11', 0, ()),
    #st1 and st3 (immediate offset)
    (REV_ALL_ARM, '4e9f19c3', 'st1 { v3.b }[#e], x14, #1', 0, ()),
    (REV_ALL_ARM, '4e9f39c3', 'st3 { v3.b, v4.b, v5.b }[#e], x14, #3', 0, ()),
    (REV_ALL_ARM, '4e9f59c3', 'st1 { v3.h }[#6], x14, #2', 0, ()),
    (REV_ALL_ARM, '4e9f79c3', 'st3 { v3.h, v4.h, v5.h }[#6], x14, #6', 0, ()),
    (REV_ALL_ARM, '4e9f91c3', 'st1 { v3.s }[#3], x14, #4', 0, ()),
    (REV_ALL_ARM, '4e9f85c3', 'st1 { v3.d }[#1], x14, #8', 0, ()),
    (REV_ALL_ARM, '4e9fb1c3', 'st3 { v3.s, v4.s, v5.s }[#3], x14, #12', 0, ()),
    (REV_ALL_ARM, '4e9fa5c3', 'st3 { v3.d, v4.d, v5.d }[#1], x14, #24', 0, ()),
    #st2 and st4 (register offset)
    (REV_ALL_ARM, '4eab19c3', 'st2 { v3.b, v4.b }[#e], x14, x11', 0, ()),
    (REV_ALL_ARM, '4eab39c3', 'st4 { v3.b, v4.b, v5.b, v6.b }[#e], x14, x11', 0, ()),
    (REV_ALL_ARM, '4eab59c3', 'st2 { v3.h, v4.h }[#6], x14, x11', 0, ()),
    (REV_ALL_ARM, '4eab79c3', 'st4 { v3.h, v4.h, v5.h, v6.h }[#6], x14, x11', 0, ()),
    (REV_ALL_ARM, '4eab91c3', 'st2 { v3.s, v4.s }[#3], x14, x11', 0, ()),
    (REV_ALL_ARM, '4eab85c3', 'st2 { v3.d, v4.d }[#1], x14, x11', 0, ()),
    (REV_ALL_ARM, '4eabb1c3', 'st4 { v3.s, v4.s, v5.s, v6.s }[#3], x14, x11', 0, ()),
    (REV_ALL_ARM, '4eaba5c3', 'st4 { v3.d, v4.d, v5.d, v6.d }[#1], x14, x11', 0, ()),
    #st2 and st4 (immediate offset)
    (REV_ALL_ARM, '4ebf19c3', 'st2 { v3.b, v4.b }[#e], x14, #2', 0, ()),
    (REV_ALL_ARM, '4ebf39c3', 'st4 { v3.b, v4.b, v5.b, v6.b }[#e], x14, #4', 0, ()),
    (REV_ALL_ARM, '4ebf59c3', 'st2 { v3.h, v4.h }[#6], x14, #4', 0, ()),
    (REV_ALL_ARM, '4ebf79c3', 'st4 { v3.h, v4.h, v5.h, v6.h }[#6], x14, #8', 0, ()),
    (REV_ALL_ARM, '4ebf91c3', 'st2 { v3.s, v4.s }[#3], x14, #8', 0, ()),
    (REV_ALL_ARM, '4ebf85c3', 'st2 { v3.d, v4.d }[#1], x14, #16', 0, ()),
    (REV_ALL_ARM, '4ebfb1c3', 'st4 { v3.s, v4.s, v5.s, v6.s }[#3], x14, #16', 0, ()),
    (REV_ALL_ARM, '4ebfa5c3', 'st4 { v3.d, v4.d, v5.d, v6.d }[#1], x14, #32', 0, ()),
    #ld1 and ld3 (register offset)
    (REV_ALL_ARM, '4ecb19c3', 'ld1 { v3.b }[#e], x14, x11', 0, ()),
    (REV_ALL_ARM, '4ecb39c3', 'ld3 { v3.b, v4.b, v5.b }[#e], x14, x11', 0, ()),
    (REV_ALL_ARM, '4ecb59c3', 'ld1 { v3.h }[#6], x14, x11', 0, ()),
    (REV_ALL_ARM, '4ecb79c3', 'ld3 { v3.h, v4.h, v5.h }[#6], x14, x11', 0, ()),
    (REV_ALL_ARM, '4ecb91c3', 'ld1 { v3.s }[#3], x14, x11', 0, ()),
    (REV_ALL_ARM, '4ecb85c3', 'ld1 { v3.d }[#1], x14, x11', 0, ()),
    (REV_ALL_ARM, '4ecbb1c3', 'ld3 { v3.s, v4.s, v5.s }[#3], x14, x11', 0, ()),
    (REV_ALL_ARM, '4ecba5c3', 'ld3 { v3.d, v4.d, v5.d }[#1], x14, x11', 0, ()),
    #ld1r (register offset)
    (REV_ALL_ARM, '0ecbc1c3', 'ld1r { v3.8b }, x14, x11', 0, ()),
    (REV_ALL_ARM, '4ecbc1c3', 'ld1r { v3.16b }, x14, x11', 0, ()),
    (REV_ALL_ARM, '0ecbc5c3', 'ld1r { v3.4h }, x14, x11', 0, ()),
    (REV_ALL_ARM, '4ecbc5c3', 'ld1r { v3.8h }, x14, x11', 0, ()),
    (REV_ALL_ARM, '0ecbc9c3', 'ld1r { v3.2s }, x14, x11', 0, ()),
    (REV_ALL_ARM, '4ecbc9c3', 'ld1r { v3.4s }, x14, x11', 0, ()),
    (REV_ALL_ARM, '0ecbcdc3', 'ld1r { v3.1d }, x14, x11', 0, ()),
    (REV_ALL_ARM, '4ecbcdc3', 'ld1r { v3.2d }, x14, x11', 0, ()),
    #ld3r (register offset)
    (REV_ALL_ARM, '0ecbe1c3', 'ld3r { v3.8b, v4.8b, v5.8b }, x14, x11', 0, ()),
    (REV_ALL_ARM, '4ecbe1c3', 'ld3r { v3.16b, v4.16b, v5.16b }, x14, x11', 0, ()),
    (REV_ALL_ARM, '0ecbe5c3', 'ld3r { v3.4h, v4.4h, v5.4h }, x14, x11', 0, ()),
    (REV_ALL_ARM, '4ecbe5c3', 'ld3r { v3.8h, v4.8h, v5.8h }, x14, x11', 0, ()),
    (REV_ALL_ARM, '0ecbe9c3', 'ld3r { v3.2s, v4.2s, v5.2s }, x14, x11', 0, ()),
    (REV_ALL_ARM, '4ecbe9c3', 'ld3r { v3.4s, v4.4s, v5.4s }, x14, x11', 0, ()),
    (REV_ALL_ARM, '0ecbedc3', 'ld3r { v3.1d, v4.1d, v5.1d }, x14, x11', 0, ()),
    (REV_ALL_ARM, '4ecbedc3', 'ld3r { v3.2d, v4.2d, v5.2d }, x14, x11', 0, ()),
    #ld1 and ld3 (immediate offset)
    (REV_ALL_ARM, '4ecb19c3', 'ld1 { v3.b }[#e], x14, #1', 0, ()),
    (REV_ALL_ARM, '4ecb39c3', 'ld3 { v3.b, v4.b, v5.b }[#e], x14, #3', 0, ()),
    (REV_ALL_ARM, '4ecb59c3', 'ld1 { v3.h }[#6], x14, #2', 0, ()),
    (REV_ALL_ARM, '4ecb79c3', 'ld3 { v3.h, v4.h, v5.h }[#6], x14, #6', 0, ()),
    (REV_ALL_ARM, '4ecb91c3', 'ld1 { v3.s }[#3], x14, #4', 0, ()),
    (REV_ALL_ARM, '4ecb85c3', 'ld1 { v3.d }[#1], x14, #8', 0, ()),
    (REV_ALL_ARM, '4ecbb1c3', 'ld3 { v3.s, v4.s, v5.s }[#3], x14, #12', 0, ()),
    (REV_ALL_ARM, '4ecba5c3', 'ld3 { v3.d, v4.d, v5.d }[#1], x14, #24', 0, ()),
    #ld1r (immediate offset)
    (REV_ALL_ARM, '0edfc1c3', 'ld1r { v3.8b }, x14, #1', 0, ()),
    (REV_ALL_ARM, '4edfc1c3', 'ld1r { v3.16b }, x14, #1', 0, ()),
    (REV_ALL_ARM, '0edfc5c3', 'ld1r { v3.4h }, x14, #2', 0, ()),
    (REV_ALL_ARM, '4edfc5c3', 'ld1r { v3.8h }, x14, #2', 0, ()),
    (REV_ALL_ARM, '0edfc9c3', 'ld1r { v3.2s }, x14, #4', 0, ()),
    (REV_ALL_ARM, '4edfc9c3', 'ld1r { v3.4s }, x14, #4', 0, ()),
    (REV_ALL_ARM, '0edfcdc3', 'ld1r { v3.1d }, x14, #8', 0, ()),
    (REV_ALL_ARM, '4edfcdc3', 'ld1r { v3.2d }, x14, #8', 0, ()),
    #ld3r (immediate offset)
    (REV_ALL_ARM, '0edfe1c3', 'ld3r { v3.8b, v4.8b, v5.8b }, x14, #3', 0, ()),
    (REV_ALL_ARM, '4edfe1c3', 'ld3r { v3.16b, v4.16b, v5.16b }, x14, #3', 0, ()),
    (REV_ALL_ARM, '0edfe5c3', 'ld3r { v3.4h, v4.4h, v5.4h }, x14, #6', 0, ()),
    (REV_ALL_ARM, '4edfe5c3', 'ld3r { v3.8h, v4.8h, v5.8h }, x14, #6', 0, ()),
    (REV_ALL_ARM, '0edfe9c3', 'ld3r { v3.2s, v4.2s, v5.2s }, x14, #12', 0, ()),
    (REV_ALL_ARM, '4edfe9c3', 'ld3r { v3.4s, v4.4s, v5.4s }, x14, #12', 0, ()),
    (REV_ALL_ARM, '0edfedc3', 'ld3r { v3.1d, v4.1d, v5.1d }, x14, #24', 0, ()),
    (REV_ALL_ARM, '4edfedc3', 'ld3r { v3.2d, v4.2d, v5.2d }, x14, #24', 0, ()),
    #ld2 and ld4 (register offset)
    (REV_ALL_ARM, '4eeb19c3', 'ld2 { v3.b, v4.b }[#e], x14, x11', 0, ()),
    (REV_ALL_ARM, '4eeb39c3', 'ld4 { v3.b, v4.b, v5.b, v6.b }[#e], x14, x11', 0, ()),
    (REV_ALL_ARM, '4eeb59c3', 'ld2 { v3.h, v4.h }[#6], x14, x11', 0, ()),
    (REV_ALL_ARM, '4eeb79c3', 'ld4 { v3.h, v4.h, v5.h, v6.h }[#6], x14, x11', 0, ()),
    (REV_ALL_ARM, '4eeb91c3', 'ld2 { v3.s, v4.s }[#3], x14, x11', 0, ()),
    (REV_ALL_ARM, '4eeb85c3', 'ld2 { v3.d, v4.d }[#1], x14, x11', 0, ()),
    (REV_ALL_ARM, '4eebb1c3', 'ld4 { v3.s, v4.s, v5.s, v6.s }[#3], x14, x11', 0, ()),
    (REV_ALL_ARM, '4eeba5c3', 'ld4 { v3.d, v4.d, v5.d, v6.d }[#1], x14, x11', 0, ()),
    #ld2r (register offset)
    (REV_ALL_ARM, '0eebc1c3', 'ld2r { v3.8b, v4.8b }, x14, x11', 0, ()),
    (REV_ALL_ARM, '4eebc1c3', 'ld2r { v3.16b, v4.16b }, x14, x11', 0, ()),
    (REV_ALL_ARM, '0eebc5c3', 'ld2r { v3.4h, v4.4h }, x14, x11', 0, ()),
    (REV_ALL_ARM, '4eebc5c3', 'ld2r { v3.8h, v4.8h }, x14, x11', 0, ()),
    (REV_ALL_ARM, '0eebc9c3', 'ld2r { v3.2s, v4.2s }, x14, x11', 0, ()),
    (REV_ALL_ARM, '4eebc9c3', 'ld2r { v3.4s, v4.4s }, x14, x11', 0, ()),
    (REV_ALL_ARM, '0eebcdc3', 'ld2r { v3.1d, v4.1d }, x14, x11', 0, ()),
    (REV_ALL_ARM, '4eebcdc3', 'ld2r { v3.2d, v4.2d }, x14, x11', 0, ()),
    #ld4r (register offset)
    (REV_ALL_ARM, '0eebe1c3', 'ld4r { v3.8b, v4.8b, v5.8b, v6.8b }, x14, x11', 0, ()),
    (REV_ALL_ARM, '4eebe1c3', 'ld4r { v3.16b, v4.16b, v5.16b, v6.16b }, x14, x11', 0, ()),
    (REV_ALL_ARM, '0eebe5c3', 'ld4r { v3.4h, v4.4h, v5.4h, v6.4h }, x14, x11', 0, ()),
    (REV_ALL_ARM, '4eebe5c3', 'ld4r { v3.8h, v4.8h, v5.8h, v6.8h }, x14, x11', 0, ()),
    (REV_ALL_ARM, '0eebe9c3', 'ld4r { v3.2s, v4.2s, v5.2s, v6.2s }, x14, x11', 0, ()),
    (REV_ALL_ARM, '4eebe9c3', 'ld4r { v3.4s, v4.4s, v5.4s, v6.4s }, x14, x11', 0, ()),
    (REV_ALL_ARM, '0eebedc3', 'ld4r { v3.1d, v4.1d, v5.1d, v6.1d }, x14, x11', 0, ()),
    (REV_ALL_ARM, '4eebedc3', 'ld4r { v3.2d, v4.2d, v5.2d, v6.2d }, x14, x11', 0, ()),
    #ld2 and ld4 (immediate offset)
    (REV_ALL_ARM, '4eeb19c3', 'ld2 { v3.b, v4.b }[#e], x14, #2', 0, ()),
    (REV_ALL_ARM, '4eeb39c3', 'ld4 { v3.b, v4.b, v5.b, v6.b }[#e], x14, #4', 0, ()),
    (REV_ALL_ARM, '4eeb59c3', 'ld2 { v3.h, v4.h }[#6], x14, #4', 0, ()),
    (REV_ALL_ARM, '4eeb79c3', 'ld4 { v3.h, v4.h, v5.h, v6.h }[#6], x14, #8', 0, ()),
    (REV_ALL_ARM, '4eeb91c3', 'ld2 { v3.s, v4.s }[#3], x14, #8', 0, ()),
    (REV_ALL_ARM, '4eeb85c3', 'ld2 { v3.d, v4.d }[#1], x14, #16', 0, ()),
    (REV_ALL_ARM, '4eebb1c3', 'ld4 { v3.s, v4.s, v5.s, v6.s }[#3], x14, #16', 0, ()),
    (REV_ALL_ARM, '4eeba5c3', 'ld4 { v3.d, v4.d, v5.d, v6.d }[#1], x14, #32', 0, ()),
    #ld2r (immediate offset)
    (REV_ALL_ARM, '0effc1c3', 'ld2r { v3.8b, v4.8b }, x14, #2', 0, ()),
    (REV_ALL_ARM, '4effc1c3', 'ld2r { v3.16b, v4.16b }, x14, #2', 0, ()),
    (REV_ALL_ARM, '0effc5c3', 'ld2r { v3.4h, v4.4h }, x14, #4', 0, ()),
    (REV_ALL_ARM, '4effc5c3', 'ld2r { v3.8h, v4.8h }, x14, #4', 0, ()),
    (REV_ALL_ARM, '0effc9c3', 'ld2r { v3.2s, v4.2s }, x14, #8', 0, ()),
    (REV_ALL_ARM, '4effc9c3', 'ld2r { v3.4s, v4.4s }, x14, #8', 0, ()),
    (REV_ALL_ARM, '0effcdc3', 'ld2r { v3.1d, v4.1d }, x14, #16', 0, ()),
    (REV_ALL_ARM, '4effcdc3', 'ld2r { v3.2d, v4.2d }, x14, #16', 0, ()),
    #ld4r (immediate offset)
    (REV_ALL_ARM, '0effe1c3', 'ld4r { v3.8b, v4.8b, v5.8b, v6.8b }, x14, #4', 0, ()),
    (REV_ALL_ARM, '4effe1c3', 'ld4r { v3.16b, v4.16b, v5.16b, v6.16b }, x14, #4', 0, ()),
    (REV_ALL_ARM, '0effe5c3', 'ld4r { v3.4h, v4.4h, v5.4h, v6.4h }, x14, #8', 0, ()),
    (REV_ALL_ARM, '4effe5c3', 'ld4r { v3.8h, v4.8h, v5.8h, v6.8h }, x14, #8', 0, ()),
    (REV_ALL_ARM, '0effe9c3', 'ld4r { v3.2s, v4.2s, v5.2s, v6.2s }, x14, #16', 0, ()),
    (REV_ALL_ARM, '4effe9c3', 'ld4r { v3.4s, v4.4s, v5.4s, v6.4s }, x14, #16', 0, ()),
    (REV_ALL_ARM, '0effedc3', 'ld4r { v3.1d, v4.1d, v5.1d, v6.1d }, x14, #32', 0, ()),
    (REV_ALL_ARM, '4effedc3', 'ld4r { v3.2d, v4.2d, v5.2d, v6.2d }, x14, #32', 0, ()),
#Data processing (register)
    
    #Logical (shifted register)
    
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
    
    #Add/sub (shifted register)
    
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
    
    #Add/subtract (extended register)
    
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
    
    #Add/subtract (with carry)
    
    (REV_ALL_ARM, '1a0b01c3', 'adc w3, w14, w11', 0, ()),
    (REV_ALL_ARM, '3a0b01c3', 'adcs w3, w14, w11', 0, ()),
    (REV_ALL_ARM, '5a0b01c3', 'sbc w3, w14, w11', 0, ()),
    (REV_ALL_ARM, '7a0b01c3', 'sbcs w3, w14, w11', 0, ()),
    (REV_ALL_ARM, '9a0b01c3', 'adc x3, x14, x11', 0, ()),
    (REV_ALL_ARM, 'ba0b01c3', 'adcs x3, x14, x11', 0, ()),
    (REV_ALL_ARM, 'da0b01c3', 'sbc x3, x14, x11', 0, ()),
    (REV_ALL_ARM, 'fa0b01c3', 'sbcs x3, x14, x11', 0, ()),
    
    #Conditional compare (register)
    
    #FIXME X = cond, olist to match
    (REV_ALL_ARM, '3a4bX1cf', 'ccmn w14, w11, #f, cond', 0, ()),
    (REV_ALL_ARM, '7a4bX1ce', 'ccmp w14, w11, #e, cond', 0, ()),
    (REV_ALL_ARM, 'ba4bX1cd', 'ccmn x14, x11, #d, cond', 0, ()),
    (REV_ALL_ARM, 'fa4bX1cc', 'ccmp x14, x11, #c, cond', 0, ()),
    
    #Conditional compare (immediate)
    
    #FIXME X = cond, olist to match
    (REV_ALL_ARM, '3a4bX9cb', 'ccmn w14, #11, #b, cond', 0, ()),
    (REV_ALL_ARM, '7a4bX9ca', 'ccmp w14, #11, #a, cond', 0, ()),
    (REV_ALL_ARM, 'ba4bX9c9', 'ccmn x14, #11, #9, cond', 0, ()),
    (REV_ALL_ARM, 'fa4bX9c8', 'ccmp x14, #11, #8, cond', 0, ()),
    
    #Conditional select
    
    #FIXME X = cond, olist to match
    (REV_ALL_ARM, '1a8bX1c3', 'csel w3, w14, w11, cond', 0, ()),
    (REV_ALL_ARM, '1a8bX5c3', 'csinc w3, w14, w11, cond', 0, ()),
    (REV_ALL_ARM, '5a8bX1c3', 'csinv w3, w14, w11, cond', 0, ()),
    (REV_ALL_ARM, '5a8bX5c3', 'csneg w3, w14, w11, cond', 0, ()),
    (REV_ALL_ARM, '9a8bX1c3', 'csel x3, x14, x11, cond', 0, ()),
    (REV_ALL_ARM, '9a8bX5c3', 'csinc x3, x14, x11, cond', 0, ()),
    (REV_ALL_ARM, 'da8bX1c3', 'csinv x3, x14, x11, cond', 0, ()),
    (REV_ALL_ARM, 'da8bX5c3', 'csneg x3, x14, x11, cond', 0, ()),
    '''
    Data processing (3 source)
    '''
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
    
    #Data processing (2 source)
    
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

    #Data processing (1 source)

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
