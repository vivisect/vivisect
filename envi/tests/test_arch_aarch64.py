#this probably needs to be looked over once more to make sure all
#assembler symbols are correctly represented

GOOD_TESTS = 495588
GOOD_EMU_TESTS = 412972

import sys
import envi
import struct
import unittest
import vivisect
import envi.memcanvas as e_memcanv

from binascii import unhexlify
from envi.archs.aarch64.regs import *
from envi.tests.aarch64_data import instrs


instrs_bigend = [
    #Data processing immediate

    # PC-release addressing
    ('50abcd03', 'adr x3, #0x000579a2', 0, ()), #adr
    ('d0abcd03', 'adrp x3, [#0x1479a2000]', 0, ()), #adrp
    
    # Add/sub (immediate)
    ('113c15e3', 'add w3, w14, [#0xf05{, LSL #0}]', 0, ()), #add (shift=0b00, sf=0b0)
    ('117c15e3', 'add w3, w14, [#0xf05{, LSL #12}]', 0, ()), #add (shift=0b01, sf=0b0)
    ('913c15e3', 'add x3, x14, [#0xf05{, LSL #0}]', 0, ()), #add (shift=0b00, sf=0b1)
    ('917c15e3', 'add x3, x14, [#0xf05{, LSL #12}]', 0, ()), #add (shift=0b01, sf=0b1)
    ('313c15e3', 'adds w3, w14, [#0xf05{, LSL #0}]', 0, ()), #adds (shift=0b00, sf=0b0)
    ('317c15e3', 'adds w3, w14, [#0xf05{, LSL #12}]', 0, ()), #adds (shift=0b01, sf=0b0)
    ('b13c15e3', 'adds x3, x14, [#0xf05{, LSL #0}]', 0, ()), #adds (shift=0b00, sf=0b1)
    ('b17c15e3', 'adds x3, x14, [#0xf05{, LSL #12}]', 0, ()), #adds (shift=0b01, sf=0b1)
    ('513c15e3', 'sub w3, w14, [#0xf05{, LSL #0}]', 0, ()), #add (shift=0b00, sf=0b0)
    ('517c15e3', 'sub w3, w14, [#0xf05{, LSL #12}]', 0, ()), #add (shift=0b01, sf=0b0)
    ('d13c15e3', 'sub x3, x14, [#0xf05{, LSL #0}]', 0, ()), #add (shift=0b00, sf=0b1)
    ('d17c15e3', 'sub x3, x14, [#0xf05{, LSL #12}]', 0, ()), #add (shift=0b01, sf=0b1)
    ('713c15e3', 'subs w3, w14, [#0xf05{, LSL #0}]', 0, ()), #adds (shift=0b00, sf=0b0)
    ('717c15e3', 'subs w3, w14, [#0xf05{, LSL #12}]', 0, ()), #adds (shift=0b01, sf=0b0)
    ('f13c15e3', 'subs x3, x14, [#0xf05{, LSL #0}]', 0, ()), #adds (shift=0b00, sf=0b1)
    ('f17c15e3', 'subs x3, x14, [#0xf05{, LSL #12}]', 0, ()), #adds (shift=0b01, sf=0b1)
    
    # Logical (immediate)
    
    ('123bf5e3', 'and w3, w14, [#f7b]', 0, ()),    #and (32-bit variant)
    ('323bf5e3', 'orr w3, w14, [#f7b]', 0, ()),    #orr (32-bit variant)
    ('523bf5e3', 'eor w3, w14, [#f7b]', 0, ()),    #eor (32-bit variant)
    ('723bf5e3', 'ands w3, w14, [#f7b]', 0, ()),   #ands (32-bit variant)
    ('923bf5e3', 'and x3, x14, [#f7b]', 0, ()),    #and (64-bit variant)
    ('b23bf5e3', 'orr x3, x14, [#f7b]', 0, ()),    #orr (64-bit variant)
    ('d27bf5e3', 'eor x3, x14, [#1f7b]', 0, ()),   #eor (64-bit variant)
    ('f27bf5e3', 'ands x3, x14, [#1f7b]', 0, ()),  #ands (64-bit variant)
    
    # Move wide (immediate)
    
    ('12a8b7e3', 'movn w3, #45bf{, LSL #10}', 0, ()), #movn (32-bit variant)
    ('52a8b7e3', 'movz w3, #45bf{, LSL #10}', 0, ()), #movz (32-bit variant)
    ('72a8b7e3', 'movk w3, #45bf{, LSL #10}', 0, ()), #movk (32-bit variant)
    ('92a8b7e3', 'movn x3, #45bf{, LSL #10}', 0, ()), #movn (64-bit variant)
    ('d2a8b7e3', 'movz x3, #45bf{, LSL #10}', 0, ()), #movz (64-bit variant)
    ('f2a8b7e3', 'movk w3, #45bf{, LSL #10}', 0, ()), #movk (64-bit variant)
    
    # Bitfield
    
    ('1338b5e3', 'sbfm w3, w14, #38, #2d', 0, ()), #sbfm (32-bit variant)
    ('5338b5e3', 'bfm w3, w14, #38, #2d', 0, ()),  #bfm (32-bit variant)
    ('7338b5e3', 'ubfm w3, w14, #38, #2d', 0, ()), #ubfm (32-bit variant)
    ('9378b5e3', 'sbfm x3, x14, #38, #2d', 0, ()), #sbfm (64-bit variant)
    ('d378b5e3', 'bfm x3, x14, #38, #2d', 0, ()),  #bfm (64-bit variant)
    ('f378b5e3', 'ubfm w3, x14, #38, #2d', 0, ()), #ubfm (64-bit variant)
    
    # Extract
    
    ('138a75e3', 'extr w3, w14, w10, #1d', 0, ()), #extr (32-bit variant)
    ('93ca75e3', 'extr w3, w14, w10, #1d', 0, ()), #extr (64-bit variant)

#Branch, exception generation and system instructions

    
    # Unconditional branch (immediate)
    
    ('15bf86a3', 'b 6fe1a8c', 0, ()), #b
    ('95bf86a3', 'bl 6fe1a8c', 0, ()), #bl
    
    # Compare and branch (immediate)
    
    ('34f8b5e3', 'cbz w3, 1f16bc', 0, ()), #cbz (32-bit variant)
    ('35f8b5e3', 'cbnz w3, 1f16bc', 0, ()),#cbnz (32-bit variant)
    ('b4f8b5e3', 'cbz x3, 1f16bc', 0, ()), #cbz (64-bit variant)
    ('b5f8b5e3', 'cbnz x3, 1f16bc', 0, ()),#cbnz (64-bit variant)
    
    # Test & branch (immediate)
    
    ('368f42e3', 'tbz w3, #11, e85c', 0, ()),  #tbz (b5 = 0, width spec = w)
    ('b68f42e3', 'tbz x3, #31, e85c', 0, ()),  #tbz (b5 = 1, width spec = x)
    ('378f42e3', 'tbnz w3, #11, e85c', 0, ()), #tbnz (b5 = 0, width spec = w)
    ('b78f42e3', 'tbnz x3, #31, e85c', 0, ()), #tbnz (b5 = 1, width spec = x)
    
    # Conditional branch (immediate)
    
    ('54abcde0', 'b.EQ 1579bc', 0, ()), #b.cond
    ('54abcde1', 'b.NE 1579bc', 0, ()), #b.cond
    ('54abcde2', 'b.CS 1579bc', 0, ()), #b.cond
    ('54abcde3', 'b.CC 1579bc', 0, ()), #b.cond
    ('54abcde4', 'b.MI 1579bc', 0, ()), #b.cond
    ('54abcde5', 'b.PL 1579bc', 0, ()), #b.cond
    ('54abcde6', 'b.VS 1579bc', 0, ()), #b.cond
    ('54abcde7', 'b.VC 1579bc', 0, ()), #b.cond
    ('54abcde8', 'b.HI 1579bc', 0, ()), #b.cond
    ('54abcde9', 'b.LS 1579bc', 0, ()), #b.cond
    ('54abcdea', 'b.GE 1579bc', 0, ()), #b.cond
    ('54abcdeb', 'b.LT 1579bc', 0, ()), #b.cond
    ('54abcdec', 'b.GT 1579bc', 0, ()), #b.cond
    ('54abcded', 'b.LE 1579bc', 0, ()), #b.cond
    ('54abcdee', 'b.AL 1579bc', 0, ()), #b.cond
    
    # Exception generation
    
    ('d41bade1', 'svc #dd6f', 0, ()),
    ('d41bade2', 'hvc #dd6f', 0, ()),
    ('d41bade3', 'smc #dd6f', 0, ()),
    ('d43bade0', 'brk #dd6f', 0, ()),
    ('d45bade0', 'hlt #dd6f', 0, ()),
    ('d4bbade1', 'dcps1 {#dd6f}', 0, ()),
    ('d4bbade2', 'dcps2 {#dd6f}', 0, ()),
    ('d4bbade3', 'dcps3 {#dd6f}', 0, ()),
    
    # System
    
    ('d5004abf', 'msr SPSel, #a', 0, ()),  #msr (op1 = 000, op2 = 101)
    ('d5034adf', 'msr DAIFSet, #a', 0, ()),#msr (op1 = 011, op2 = 110)
    ('d5034aff', 'msr DAIFClr, #a', 0, ()),#msr (op1 = 011, op2 = 111)
    ('d5032a1f', 'hint #50', 0, ()),       #hint
    ('d5033a5f', 'clrex #a', 0, ()),       #clrex
    ('d503319f', 'dsb OSHLD|#1', 0, ()),   #dsb (crm = 0001)
    ('d503329f', 'dsb OSHST|#2', 0, ()),   #dsb (crm = 0010)
    ('d503339f', 'dsb OSH|#3', 0, ()),     #dsb (crm = 0011)
    ('d503359f', 'dsb NSHLD|#5', 0, ()),   #dsb (crm = 0101)
    ('d503369f', 'dsb NSHST|#6', 0, ()),   #dsb (crm = 0110)
    ('d503379f', 'dsb NSH|#7', 0, ()),     #dsb (crm = 0111)
    ('d503399f', 'dsb ISHLD|#9', 0, ()),   #dsb (crm = 1001)
    ('d5033a9f', 'dsb ISHST|#a', 0, ()),   #dsb (crm = 1010)
    ('d5033b9f', 'dsb ISH|#b', 0, ()),     #dsb (crm = 1011)
    ('d5033d9f', 'dsb LD|#d', 0, ()),      #dsb (crm = 1101)
    ('d5033e9f', 'dsb ST|#e', 0, ()),      #dsb (crm = 1110)
    ('d5033f9f', 'dsb SY|#f', 0, ()),      #dsb (crm = 1111)
    ('d50331bf', 'dmb OSHLD|#1', 0, ()),   #dmb (crm = 0001)
    ('d50332bf', 'dmb OSHST|#2', 0, ()),   #dmb (crm = 0010)
    ('d50333bf', 'dmb OSH|#3', 0, ()),     #dmb (crm = 0011)
    ('d50335bf', 'dmb NSHLD|#5', 0, ()),   #dmb (crm = 0101)
    ('d50336bf', 'dmb NSHST|#6', 0, ()),   #dmb (crm = 0110)
    ('d50337bf', 'dmb NSH|#7', 0, ()),     #dmb (crm = 0111)
    ('d50339bf', 'dmb ISHLD|#9', 0, ()),   #dmb (crm = 1001)
    ('d5033abf', 'dmb ISHST|#a', 0, ()),   #dmb (crm = 1010)
    ('d5033bbf', 'dmb ISH|#b', 0, ()),     #dmb (crm = 1011)
    ('d5033dbf', 'dmb LD|#d', 0, ()),      #dmb (crm = 1101)
    ('d5033ebf', 'dmb ST|#e', 0, ()),      #dmb (crm = 1110)
    ('d5033fbf', 'dmb SY|#f', 0, ()),      #dmb (crm = 1111)
    ('d5033fdf', 'isb SY|#f', 0, ()),      #isb (SY, crm = 1111)
    ('d50f1a63', 'sys #7, c1, ca, #3, x3', 0, ()), #sys FIXME name
    ('d5171ae3', 'msr r14551, x3', 0, ()), #msr (register) FIXME system register
    ('d52f1a63', 'sysl x3, #7, c1, ca, #3', 0, ()), #sysl FIXME name
    ('d5371ae3', 'mrs x3, r14551', 0, ()), #mrs FIXME system register
    
    # Unconditional branch (register)
    
    ('d61f0060', 'br x3', 0, ()),
    ('d63f0060', 'blr x3', 0, ()),
    ('d65f0060', 'ret {x3}', 0, ()),
    ('d69f03e0', 'eret', 0, ()),
    ('d6bf03e0', 'drps', 0, ()),
#Loads and stores
    
    # Load/store exclusive
    
    ('080b25c3', 'stxrb w11, w3, [x14{, #0}]', 0, ()),
    ('080ba5c3', 'stlxrb w11, w3, [x14{, #0}]', 0, ()),
    ('084b25c3', 'ldxrb w3, [x14{, #0}]', 0, ()),
    ('084ba5c3', 'ldaxrb w3, [x14{, #0}]', 0, ()),
    ('088ba5c3', 'stlrb w3, [x14{, #0}]', 0, ()),
    ('08cba5c3', 'ldarb w3, [x14{, #0}]', 0, ()),
    ('480b25c3', 'stxrh w11, w3, [x14{, #0}]', 0, ()),
    ('480ba5c3', 'stlxrh w11, w3, [x14{, #0}]', 0, ()),
    ('484b25c3', 'ldxrh w3, [x14{, #0}]', 0, ()),
    ('484ba5c3', 'ldaxrh w3, [x14{, #0}]', 0, ()),
    ('488ba5c3', 'stlrh w3, [x14{, #0}]', 0, ()),
    ('48cba5c3', 'ldarh w3, [x14{, #0}]', 0, ()),
    ('880b25c3', 'stxr w11, w3, [x14{, #0}]', 0, ()),
    ('880ba5c3', 'stlxr w11, w3, [x14{, #0}]', 0, ()),
    ('882b25c3', 'stxp w11, w3, w9, [x14{, #0}]', 0, ()),
    ('882ba5c3', 'stlxp w11, w3, w9, [x14{, #0}]', 0, ()),
    ('884b25c3', 'ldxr w3, [x14{, #0}]', 0, ()),
    ('884ba5c3', 'ldaxr w3, [x14{, #0}]', 0, ()),
    ('886b25c3', 'ldxp w3, w9, [x14{, #0}]', 0, ()),
    ('886ba5c3', 'ldaxp w3, w9, [x14{, #0}]', 0, ()),
    ('888ba5c3', 'stlr w3, [x14{, #0}]', 0, ()),
    ('88cba5c3', 'ldar w3, [x14{, #0}]', 0, ()),
    ('c80b25c3', 'stxr w11, x3, [x14{, #0}]', 0, ()),
    ('c80ba5c3', 'stlxr w11, x3, [x14{, #0}]', 0, ()),
    ('c82b25c3', 'stxp w11, x3, x9, [x14{, #0}]', 0, ()),
    ('c82ba5c3', 'stlxp w11, x3, x9, [x14{, #0}]', 0, ()),
    ('c84b25c3', 'ldxr x3, [x14{, #0}]', 0, ()),
    ('c84ba5c3', 'ldaxr x3, [x14{, #0}]', 0, ()),
    ('c86b25c3', 'ldxp x3, x9, [x14{, #0}]', 0, ()),
    ('c86ba5c3', 'ldaxp x3, x9, [x14{, #0}]', 0, ()),
    ('c88ba5c3', 'stlr x3, [x14{, #0}]', 0, ()),
    ('c8cba5c3', 'ldar x3, [x14{, #0}]', 0, ()),
    
    # Load register (literal)
    
    ('18abcde3', 'ldr w3 1579bc', 0, ()),
    ('1cabcde3', 'ldr s3 1579bc', 0, ()),
    ('58abcde3', 'ldr x3 1579bc', 0, ()),
    ('5cabcde3', 'ldr d3 1579bc', 0, ()),
    ('98abcde3', 'ldrsw x3 1579bc', 0, ()),
    ('9cabcde3', 'ldr q3 1579bc', 0, ()),
    ('d8abcde0', 'prfm PLDL1KEEP, 1579bc', 0, ()),
    ('d8abcde1', 'prfm PLDL1STRM, 1579bc', 0, ()),
    ('d8abcde2', 'prfm PLDL2KEEP, 1579bc', 0, ()),
    ('d8abcde3', 'prfm PLDL2STRM, 1579bc', 0, ()),
    ('d8abcde4', 'prfm PLDL3KEEP, 1579bc', 0, ()),
    ('d8abcde5', 'prfm PLDL3STRM, 1579bc', 0, ()),
    ('d8abcde6', 'prfm #6, 1579bc', 0, ()),
    ('d8abcde7', 'prfm #7, 1579bc', 0, ()),
    ('d8abcde8', 'prfm PLIL1KEEP, 1579bc', 0, ()),
    ('d8abcde9', 'prfm PLIL1STRM, 1579bc', 0, ()),
    ('d8abcdea', 'prfm PLIL2KEEP, 1579bc', 0, ()),
    ('d8abcdeb', 'prfm PLIL2STRM, 1579bc', 0, ()),
    ('d8abcdec', 'prfm PLIL3KEEP, 1579bc', 0, ()),
    ('d8abcded', 'prfm PLIL3STRM, 1579bc', 0, ()),
    ('d8abcdee', 'prfm #14, 1579bc', 0, ()),
    ('d8abcdef', 'prfm #15, 1579bc', 0, ()),
    ('d8abcdf0', 'prfm PSTL1KEEP, 1579bc', 0, ()),
    ('d8abcdf1', 'prfm PSTL1STRM, 1579bc', 0, ()),
    ('d8abcdf2', 'prfm PSTL2KEEP, 1579bc', 0, ()),
    ('d8abcdf3', 'prfm PSTL2STRM, 1579bc', 0, ()),
    ('d8abcdf4', 'prfm PSTL3KEEP, 1579bc', 0, ()),
    ('d8abcdf5', 'prfm PSTL3STRM, 1579bc', 0, ()),
    ('d8abcdf6', 'prfm #22, 1579bc', 0, ()),
    ('d8abcdf7', 'prfm #23, 1579bc', 0, ()),
    ('d8abcdf8', 'prfm #24, 1579bc', 0, ()),
    ('d8abcdf9', 'prfm #25, 1579bc', 0, ()),
    ('d8abcdfa', 'prfm #26, 1579bc', 0, ()),
    ('d8abcdfb', 'prfm #27, 1579bc', 0, ()),
    ('d8abcdfc', 'prfm #28, 1579bc', 0, ()),
    ('d8abcdfd', 'prfm #29, 1579bc', 0, ()),
    ('d8abcdfe', 'prfm #30, 1579bc', 0, ()),
    ('d8abcdff', 'prfm #31, 1579bc', 0, ()),
    
    # Load/store no-allocate pair (offset)

    ('2831a5c3', 'stnp w3, w9, [x14{, #18c}]', 0, ()),
    ('2871a5c3', 'ldnp w3, w9, [x14{, #18c}]', 0, ()),
    ('2c31a5c3', 'stnp s3, s9, [x14{, #18c}]', 0, ()),
    ('2c71a5c3', 'ldnp s3, s9, [x14{, #18c}]', 0, ()),
    ('6c31a5c3', 'stnp d3, d9, [x14{, #318}]', 0, ()),
    ('6c71a5c3', 'ldnp d3, d9, [x14{, #318}]', 0, ()),
    ('a831a5c3', 'stnp x3, x9, [x14{, #318}]', 0, ()),
    ('a871a5c3', 'ldnp x3, x9, [x14{, #318}]', 0, ()),
    ('ac31a5c3', 'stnp q3, q9, [x14{, #630}]', 0, ()),
    ('ac71a5c3', 'ldnp q3, q9, [x14{, #630}]', 0, ()),
    
    # Load/store register pair (post-indexed)
    
    ('28b1a5c3', 'stp w3, w9, [x14], #18c', 0, (
            {'setup':(('x14',0x41414000),(0x4141418c,0x40), (0x4141418e,0x41),(0x41414190,0x42),(0x41414192,0x43), ),
                'tests':(('x3',0x410040),('x9',0x440042),) },
        )),
    ('28f1a5c3', 'ldp w3, w9, [x14], #18c', 0, ()),
    ('2cb1a5c3', 'stp s3, s9, [x14], #18c', 0, ()),
    ('2cf1a5c3', 'ldp s3, s9, [x14], #18c', 0, ()),
    ('68f1a5c3', 'ldpsw x3, x9, [x14], #18c', 0, ()),
    ('6cb1a5c3', 'stp d3, d9, [x14], #318', 0, ()),
    ('6cf1a5c3', 'ldp d3, d9, [x14], #318', 0, ()),
    ('a8b1a5c3', 'stp x3, x9, [x14], #318', 0, ()),
    ('a8f1a5c3', 'ldp x3, x9, [x14], #318', 0, ()),
    ('acb1a5c3', 'stp q3, q9, [x14], #630', 0, ()),
    ('acf1a5c3', 'ldp q3, q9, [x14], #630', 0, ()),

    # Load/store register pair (offset)
    
    ('2931a5c3', 'stp w3, w9, [x14{, #18c}]', 0, ()),
    ('2971a5c3', 'ldp w3, w9, [x14{, #18c}]', 0, ()),
    ('2d31a5c3', 'stp s3, s9, [x14{, #18c}]', 0, ()),
    ('2d71a5c3', 'ldp s3, s9, [x14{, #18c}]', 0, ()),
    ('6971a5c3', 'ldpsw x3, x9, [x14{, #18c}]', 0, ()),
    ('6d31a5c3', 'stp d3, d9, [x14{, #318}]', 0, ()),
    ('6d71a5c3', 'ldp d3, d9, [x14{, #318}]', 0, ()),
    ('a931a5c3', 'stp x3, x9, [x14{, #318}]', 0, ()),
    ('a971a5c3', 'ldp x3, x9, [x14{, #318}]', 0, ()),
    ('ad31a5c3', 'stp q3, q9, [x14{, #630}]', 0, ()),
    ('ad71a5c3', 'ldp q3, q9, [x14{, #630}]', 0, ()),
    
    # Load/store register pair (pre-indexed)
    
    ('29b1a5c3', 'stp w3, w9, [x14, #18c]!', 0, ()),
    ('29f1a5c3', 'ldp w3, w9, [x14, #18c]!', 0, ()),
    ('2db1a5c3', 'stp s3, s9, [x14, #18c]!', 0, ()),
    ('2df1a5c3', 'ldp s3, s9, [x14, #18c]!', 0, ()),
    ('69f1a5c3', 'ldpsw x3, x9, [x14, #18c]!', 0, ()),
    ('6db1a5c3', 'stp d3, d9, [x14, #318]!', 0, ()),
    ('6df1a5c3', 'ldp d3, d9, [x14, #318]!', 0, ()),
    ('a9b1a5c3', 'stp x3, x9, [x14, #318]!', 0, ()),
    ('a9f1a5c3', 'ldp x3, x9, [x14, #318]!', 0, ()),
    ('adb1a5c3', 'stp q3, q9, [x14, #630]!', 0, ()),
    ('adf1a5c3', 'ldp q3, q9, [x14, #630]!', 0, ()),
    
    # Load/store register (unscaled immediate)
    
    ('3810f1c3', 'sturb w3, [x14{, #10f}]', 0, ()),
    ('3850f1c3', 'ldurb w3, [x14{, #10f}]', 0, ()),
    ('3890f1c3', 'ldursb x3, [x14{, #10f}]', 0, ()),
    ('38d0f1c3', 'ldursb w3, [x14{, #10f}]', 0, ()),
    ('3c10f1c3', 'stur b3, [x14{, #10f}]', 0, ()),
    ('3c50f1c3', 'ldur b3, [x14{, #10f}]', 0, ()),
    ('3c90f1c3', 'stur q3, [x14{, #10f}]', 0, ()),
    ('3cd0f1c3', 'ldur q3, [x14{, #10f}]', 0, ()),
    ('7810f1c3', 'sturh w3, [x14{, #10f}]', 0, ()),
    ('7850f1c3', 'ldurh w3, [x14{, #10f}]', 0, ()),
    ('7890f1c3', 'ldursh x3, [x14{, #10f}]', 0, ()),
    ('78d0f1c3', 'ldursh w3, [x14{, #10f}]', 0, ()),
    ('7c10f1c3', 'stur h3, [x14{, #10f}]', 0, ()),
    ('7c50f1c3', 'ldur h3, [x14{, #10f}]', 0, ()),
    ('b810f1c3', 'stur w3, [x14{, #10f}]', 0, ()),
    ('b850f1c3', 'ldur w3, [x14{, #10f}]', 0, ()),
    ('b890f1c3', 'ldursw x3, [x14{, #10f}]', 0, ()),
    ('bc10f1c3', 'stur s3, [x14{, #10f}]', 0, ()),
    ('bc50f1c3', 'ldur s3, [x14{, #10f}]', 0, ()),
    ('f810f1c3', 'stur x3, [x14{, #10f}]', 0, ()),
    ('f850f1c3', 'ldur x3, [x14{, #10f}]', 0, ()),
    ('f890f1c0', 'prfum PLDL1KEEP, [x14{, #10f}]', 0, ()),
    ('f890f1c1', 'prfum PLDL1STRM, [x14{, #10f}]', 0, ()),
    ('f890f1c2', 'prfum PLDL2KEEP, [x14{, #10f}]', 0, ()),
    ('f890f1c3', 'prfum PLDL2STRM, [x14{, #10f}]', 0, ()),
    ('f890f1c4', 'prfum PLDL3KEEP, [x14{, #10f}]', 0, ()),
    ('f890f1c5', 'prfum PLDL3STRM, [x14{, #10f}]', 0, ()),
    ('f890f1c8', 'prfum PLIL1KEEP, [x14{, #10f}]', 0, ()),
    ('f890f1c9', 'prfum PLIL1STRM, [x14{, #10f}]', 0, ()),
    ('f890f1ca', 'prfum PLIL2KEEP, [x14{, #10f}]', 0, ()),
    ('f890f1cb', 'prfum PLIL2STRM, [x14{, #10f}]', 0, ()),
    ('f890f1cc', 'prfum PLIL3KEEP, [x14{, #10f}]', 0, ()),
    ('f890f1cd', 'prfum PLIL3STRM, [x14{, #10f}]', 0, ()),
    ('f890f1d0', 'prfum PSTL1KEEP, [x14{, #10f}]', 0, ()),
    ('f890f1d1', 'prfum PSTL1STRM, [x14{, #10f}]', 0, ()),
    ('f890f1d2', 'prfum PSTL2KEEP, [x14{, #10f}]', 0, ()),
    ('f890f1d3', 'prfum PSTL2STRM, [x14{, #10f}]', 0, ()),
    ('f890f1d4', 'prfum PSTL3KEEP, [x14{, #10f}]', 0, ()),
    ('f890f1d5', 'prfum PSTL3STRM, [x14{, #10f}]', 0, ()),
    ('fc10f1c3', 'stur d3, [x14{, #10f}]', 0, ()),
    ('fc50f1c3', 'ldur d3, [x14{, #10f}]', 0, ()),
    
    # Load/store register (immediate post-indexed)
    
    ('3810f5c3', 'strb w3, [x14], #10f', 0, ()),
    ('3850f5c3', 'ldrb w3, [x14], #10f', 0, ()),
    ('3890f5c3', 'ldrsb x3, [x14], #10f', 0, ()),
    ('38d0f5c3', 'ldrsb w3, [x14], #10f', 0, ()),
    ('3c10f5c3', 'str b3, [x14], #10f', 0, ()),
    ('3c50f5c3', 'ldr b3, [x14], #10f', 0, ()),
    ('3c90f5c3', 'str q3, [x14], #10f', 0, ()),
    ('3cd0f5c3', 'ldr q3, [x14], #10f', 0, ()),
    ('7810f5c3', 'strh w3, [x14], #10f', 0, ()),
    ('7850f5c3', 'ldrh w3, [x14], #10f', 0, ()),
    ('7890f5c3', 'ldrsh x3, [x14], #10f', 0, ()),
    ('78d0f5c3', 'ldrsh w3, [x14], #10f', 0, ()),
    ('7c10f5c3', 'str h3, [x14], #10f', 0, ()),
    ('7c50f5c3', 'ldr h3, [x14], #10f', 0, ()),
    ('b810f5c3', 'str w3, [x14], #10f', 0, ()),
    ('b850f5c3', 'ldr w3, [x14], #10f', 0, ()),
    ('b890f5c3', 'ldrsw x3, [x14], #10f', 0, ()),
    ('bc10f5c3', 'str s3, [x14], #10f', 0, ()),
    ('bc50f5c3', 'ldr s3, [x14], #10f', 0, ()),
    ('f810f5c3', 'str x3, [x14], #10f', 0, ()),
    ('f850f5c3', 'ldr x3, [x14], #10f', 0, ()),
    ('fc10f5c3', 'str d3, [x14], #10f', 0, ()),
    ('fc50f5c3', 'ldr d3, [x14], #10f', 0, ()),
    
    # Load/store register (unprivileged)
    
    ('3810f9c3', 'sttrb w3, [x14{, #10f}]', 0, ()),
    ('3850f9c3', 'ldtrb w3, [x14{, #10f}]', 0, ()),
    ('3890f9c3', 'ldtrsb x3, [x14{, #10f}]', 0, ()),
    ('38d0f9c3', 'ldtrsb w3, [x14{, #10f}]', 0, ()),
    ('7810f9c3', 'sttrh w3, [x14{, #10f}]', 0, ()),
    ('7850f9c3', 'ldtrh w3, [x14{, #10f}]', 0, ()),
    ('7890f9c3', 'ldtrsh x3, [x14{, #10f}]', 0, ()),
    ('78d0f9c3', 'ldtrsh w3, [x14{, #10f}]', 0, ()),
    ('b810f9c3', 'sttr w3, [x14{, #10f}]', 0, ()),
    ('b850f9c3', 'ldtr w3, [x14{, #10f}]', 0, ()),
    ('b890f9c3', 'ldtrsw x3, [x14{, #10f}]', 0, ()),
    ('f810f9c3', 'sttr x3, [x14{, #10f}]', 0, ()),
    ('f850f9c3', 'ldtr x3, [x14{, #10f}]', 0, ()),
    
    # Load/store register (immediate pre-indexed)
    
    ('3810fdc3', 'strb w3, [x14, #10f]!', 0, ()),
    ('3850fdc3', 'ldrb w3, [x14, #10f]!', 0, ()),
    ('3890fdc3', 'ldrsb x3, [x14, #10f]!', 0, ()),
    ('38d0fdc3', 'ldrsb w3, [x14, #10f]!', 0, ()),
    ('3c10fdc3', 'str b3, [x14, #10f]!', 0, ()),
    ('3c50fdc3', 'ldr b3, [x14, #10f]!', 0, ()),
    ('3c90fdc3', 'str q3, [x14, #10f]!', 0, ()),
    ('3cd0fdc3', 'ldr q3, [x14, #10f]!', 0, ()),
    ('7810fdc3', 'strh w3, [x14, #10f]!', 0, ()),
    ('7850fdc3', 'ldrh w3, [x14, #10f]!', 0, ()),
    ('7890fdc3', 'ldrsh x3, [x14, #10f]!', 0, ()),
    ('78d0fdc3', 'ldrsh w3, [x14, #10f]!', 0, ()),
    ('7c10fdc3', 'str h3, [x14, #10f]!', 0, ()),
    ('7c50fdc3', 'ldr h3, [x14, #10f]!', 0, ()),
    ('b810fdc3', 'str w3, [x14, #10f]!', 0, ()),
    ('b850fdc3', 'ldr w3, [x14, #10f]!', 0, ()),
    ('b890fdc3', 'ldrsw x3, [x14, #10f]!', 0, ()),
    ('bc10fdc3', 'str s3, [x14, #10f]!', 0, ()),
    ('bc50fdc3', 'ldr s3, [x14, #10f]!', 0, ()),
    ('f810fdc3', 'str x3, [x14, #10f]!', 0, ()),
    ('f850fdc3', 'ldr x3, [x14, #10f]!', 0, ()),
    ('fc10fdc3', 'str d3, [x14, #10f]!', 0, ()),
    ('fc50fdc3', 'ldr d3, [x14, #10f]!', 0, ()),
    
    # Load/store register (register offset)

    #every 5 tests is for the same instruction, just with altered <extend> values
    #LSL gets 2 tests, because <amount> doesn't default to zero when <extend> is LSL
    #prfm is an exception, so there are 5 sets of 18 tests each. Each set has the same
    #value for <extend> on all 18 tests. What changes between tests is the value of <prfop>
    ('382b59c3', 'strb w3, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('382bd9c3', 'strb w3, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('382b69c3', 'strb w3, [x14, x11{, LSL{}}]', 0, ()),
    ('382b79c3', 'strb w3, [x14, x11{, LSL{#0}}]', 0, ()),
    ('382bf9c3', 'strb w3, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('386b59c3', 'ldrb w3, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('386bd9c3', 'ldrb w3, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('386b69c3', 'ldrb w3, [x14, x11{, LSL{}}]', 0, ()),
    ('386b79c3', 'ldrb w3, [x14, x11{, LSL{#0}}]', 0, ()),
    ('386bf9c3', 'ldrb w3, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('38ab59c3', 'ldrsb x3, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('38abd9c3', 'ldrsb x3, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('38ab69c3', 'ldrsb x3, [x14, x11{, LSL{}}]', 0, ()),
    ('38ab79c3', 'ldrsb x3, [x14, x11{, LSL{#0}}]', 0, ()),
    ('38abf9c3', 'ldrsb x3, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('38eb59c3', 'ldrsb w3, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('38ebd9c3', 'ldrsb w3, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('38eb69c3', 'ldrsb w3, [x14, x11{, LSL{}}]', 0, ()),
    ('38eb79c3', 'ldrsb w3, [x14, x11{, LSL{#0}}]', 0, ()),
    ('38ebf9c3', 'ldrsb w3, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('3c2b59c3', 'str b3, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('3c2bd9c3', 'str b3, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('3c2b69c3', 'str b3, [x14, x11{, LSL{}}]', 0, ()),
    ('3c2b79c3', 'str b3, [x14, x11{, LSL{#0}}]', 0, ()),
    ('3c2bf9c3', 'str b3, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('3c6b59c3', 'ldr b3, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('3c6bd9c3', 'ldr b3, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('3c6b69c3', 'ldr b3, [x14, x11{, LSL{}}]', 0, ()),
    ('3c6b79c3', 'ldr b3, [x14, x11{, LSL{#0}}]', 0, ()),
    ('3c6bf9c3', 'ldr b3, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('3cab59c3', 'str q3, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('3cabd9c3', 'str q3, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('3cab69c3', 'str q3, [x14, x11{, LSL{#0}}]', 0, ()),
    ('3cab79c3', 'str q3, [x14, x11{, LSL{#4}}]', 0, ()),
    ('3cabf9c3', 'str q3, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('3ceb59c3', 'ldr q3, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('3cebd9c3', 'ldr q3, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('3ceb69c3', 'ldr q3, [x14, x11{, LSL{#0}}]', 0, ()),
    ('3ceb79c3', 'ldr q3, [x14, x11{, LSL{#4}}]', 0, ()),
    ('3cebf9c3', 'ldr q3, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('782b59c3', 'strh w3, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('782bd9c3', 'strh w3, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('782b69c3', 'strh w3, [x14, x11{, LSL{#0}}]', 0, ()),
    ('782b79c3', 'strh w3, [x14, x11{, LSL{#1}}]', 0, ()),
    ('782bf9c3', 'strh w3, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('786bf9c3', 'ldrh w3, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('786bf9c3', 'ldrh w3, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('786bf9c3', 'ldrh w3, [x14, x11{, LSL{#0}}]', 0, ()),
    ('786bf9c3', 'ldrh w3, [x14, x11{, LSL{#1}}]', 0, ()),
    ('786bf9c3', 'ldrh w3, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('78ab59c3', 'ldrsh x3, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('78abd9c3', 'ldrsh x3, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('78ab69c3', 'ldrsh x3, [x14, x11{, LSL{#0}}]', 0, ()),
    ('78ab79c3', 'ldrsh x3, [x14, x11{, LSL{#1}}]', 0, ()),
    ('78abf9c3', 'ldrsh x3, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('78eb59c3', 'ldrsh w3, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('78ebd9c3', 'ldrsh w3, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('78eb69c3', 'ldrsh w3, [x14, x11{, LSL{#0}}]', 0, ()),
    ('78eb79c3', 'ldrsh w3, [x14, x11{, LSL{#1}}]', 0, ()),
    ('78ebf9c3', 'ldrsh w3, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('7c2b59c3', 'str h3, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('7c2bd9c3', 'str h3, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('7c2b69c3', 'str h3, [x14, x11{, LSL{#0}}]', 0, ()),
    ('7c2b79c3', 'str h3, [x14, x11{, LSL{#1}}]', 0, ()),
    ('7c2bf9c3', 'str h3, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('7c6b59c3', 'ldr h3, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('7c6bd9c3', 'ldr h3, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('7c6b69c3', 'ldr h3, [x14, x11{, LSL{#0}}]', 0, ()),
    ('7c6b79c3', 'ldr h3, [x14, x11{, LSL{#1}}]', 0, ()),
    ('7c6bf9c3', 'ldr h3, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('b82b59c3', 'str w3, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('b82bd9c3', 'str w3, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('b82b69c3', 'str w3, [x14, x11{, LSL{#0}}]', 0, ()),
    ('b82b79c3', 'str w3, [x14, x11{, LSL{#2}}]', 0, ()),
    ('b82bf9c3', 'str w3, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('b86b59c3', 'ldr w3, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('b86bd9c3', 'ldr w3, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('b86b69c3', 'ldr w3, [x14, x11{, LSL{#0}}]', 0, ()),
    ('b86b79c3', 'ldr w3, [x14, x11{, LSL{#2}}]', 0, ()),
    ('b86bf9c3', 'ldr w3, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('b8ab59c3', 'ldrsw x3, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('b8abd9c3', 'ldrsw x3, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('b8ab69c3', 'ldrsw x3, [x14, x11{, LSL{#0}}]', 0, ()),
    ('b8ab79c3', 'ldrsw x3, [x14, x11{, LSL{#2}}]', 0, ()),
    ('b8abf9c3', 'ldrsw x3, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('bc2b59c3', 'str s3, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('bc2bd9c3', 'str s3, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('bc2b69c3', 'str s3, [x14, x11{, LSL{#0}}]', 0, ()),
    ('bc2b79c3', 'str s3, [x14, x11{, LSL{#2}}]', 0, ()),
    ('bc2bf9c3', 'str s3, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('bc6b59c3', 'ldr s3, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('bc6bd9c3', 'ldr s3, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('bc6b69c3', 'ldr s3, [x14, x11{, LSL{#0}}]', 0, ()),
    ('bc6b79c3', 'ldr s3, [x14, x11{, LSL{#2}}]', 0, ()),
    ('bc6bf9c3', 'ldr s3, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('f82b59c3', 'str x3, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('f82bd9c3', 'str x3, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('f82b69c3', 'str x3, [x14, x11{, LSL{#0}}]', 0, ()),
    ('f82b79c3', 'str x3, [x14, x11{, LSL{#3}}]', 0, ()),
    ('f82bf9c3', 'str x3, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('f86b59c3', 'ldr x3, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('f86bd9c3', 'ldr x3, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('f86b69c3', 'ldr x3, [x14, x11{, LSL{#0}}]', 0, ()),
    ('f86b79c3', 'ldr x3, [x14, x11{, LSL{#3}}]', 0, ()),
    ('f86bf9c3', 'ldr x3, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('f8ab59c0', 'prfm PLDL1KEEP, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('f8ab59c1', 'prfm PLDL1STRM, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('f8ab59c2', 'prfm PLDL2KEEP, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('f8ab59c3', 'prfm PLDL2STRM, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('f8ab59c4', 'prfm PLDL3KEEP, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('f8ab59c5', 'prfm PLDL3STRM, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('f8ab59c8', 'prfm PLIL1KEEP, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('f8ab59c9', 'prfm PLIL1STRM, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('f8ab59ca', 'prfm PLIL2KEEP, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('f8ab59cb', 'prfm PLIL2STRM, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('f8ab59cc', 'prfm PLIL3KEEP, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('f8ab59cd', 'prfm PLIL3STRM, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('f8ab59d0', 'prfm PSTL1KEEP, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('f8ab59d1', 'prfm PSTL1STRM, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('f8ab59d2', 'prfm PSTL2KEEP, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('f8ab59d3', 'prfm PSTL2STRM, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('f8ab59d4', 'prfm PSTL3KEEP, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('f8ab59d5', 'prfm PSTL3STRM, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('f8abd9c0', 'prfm PLDL1KEEP, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('f8abd9c1', 'prfm PLDL1STRM, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('f8abd9c2', 'prfm PLDL2KEEP, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('f8abd9c3', 'prfm PLDL2STRM, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('f8abd9c4', 'prfm PLDL3KEEP, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('f8abd9c5', 'prfm PLDL3STRM, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('f8abd9c8', 'prfm PLIL1KEEP, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('f8abd9c9', 'prfm PLIL1STRM, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('f8abd9ca', 'prfm PLIL2KEEP, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('f8abd9cb', 'prfm PLIL2STRM, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('f8abd9cc', 'prfm PLIL3KEEP, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('f8abd9cd', 'prfm PLIL3STRM, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('f8abd9d0', 'prfm PSTL1KEEP, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('f8abd9d1', 'prfm PSTL1STRM, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('f8abd9d2', 'prfm PSTL2KEEP, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('f8abd9d3', 'prfm PSTL2STRM, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('f8abd9d4', 'prfm PSTL3KEEP, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('f8abd9d5', 'prfm PSTL3STRM, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('f8ab69c0', 'prfm PLDL1KEEP, [x14, x11{, LSL{#0}}]', 0, ()),
    ('f8ab69c1', 'prfm PLDL1STRM, [x14, x11{, LSL{#0}}]', 0, ()),
    ('f8ab69c2', 'prfm PLDL2KEEP, [x14, x11{, LSL{#0}}]', 0, ()),
    ('f8ab69c3', 'prfm PLDL2STRM, [x14, x11{, LSL{#0}}]', 0, ()),
    ('f8ab69c4', 'prfm PLDL3KEEP, [x14, x11{, LSL{#0}}]', 0, ()),
    ('f8ab69c5', 'prfm PLDL3STRM, [x14, x11{, LSL{#0}}]', 0, ()),
    ('f8ab69c8', 'prfm PLIL1KEEP, [x14, x11{, LSL{#0}}]', 0, ()),
    ('f8ab69c9', 'prfm PLIL1STRM, [x14, x11{, LSL{#0}}]', 0, ()),
    ('f8ab69ca', 'prfm PLIL2KEEP, [x14, x11{, LSL{#0}}]', 0, ()),
    ('f8ab69cb', 'prfm PLIL2STRM, [x14, x11{, LSL{#0}}]', 0, ()),
    ('f8ab69cc', 'prfm PLIL3KEEP, [x14, x11{, LSL{#0}}]', 0, ()),
    ('f8ab69cd', 'prfm PLIL3STRM, [x14, x11{, LSL{#0}}]', 0, ()),
    ('f8ab69d0', 'prfm PSTL1KEEP, [x14, x11{, LSL{#0}}]', 0, ()),
    ('f8ab69d1', 'prfm PSTL1STRM, [x14, x11{, LSL{#0}}]', 0, ()),
    ('f8ab69d2', 'prfm PSTL2KEEP, [x14, x11{, LSL{#0}}]', 0, ()),
    ('f8ab69d3', 'prfm PSTL2STRM, [x14, x11{, LSL{#0}}]', 0, ()),
    ('f8ab69d4', 'prfm PSTL3KEEP, [x14, x11{, LSL{#0}}]', 0, ()),
    ('f8ab69d5', 'prfm PSTL3STRM, [x14, x11{, LSL{#0}}]', 0, ()),
    ('f8ab79c0', 'prfm PLDL1KEEP, [x14, x11{, LSL{#3}}]', 0, ()),
    ('f8ab79c1', 'prfm PLDL1STRM, [x14, x11{, LSL{#3}}]', 0, ()),
    ('f8ab79c2', 'prfm PLDL2KEEP, [x14, x11{, LSL{#3}}]', 0, ()),
    ('f8ab79c3', 'prfm PLDL2STRM, [x14, x11{, LSL{#3}}]', 0, ()),
    ('f8ab79c4', 'prfm PLDL3KEEP, [x14, x11{, LSL{#3}}]', 0, ()),
    ('f8ab79c5', 'prfm PLDL3STRM, [x14, x11{, LSL{#3}}]', 0, ()),
    ('f8ab79c8', 'prfm PLIL1KEEP, [x14, x11{, LSL{#3}}]', 0, ()),
    ('f8ab79c9', 'prfm PLIL1STRM, [x14, x11{, LSL{#3}}]', 0, ()),
    ('f8ab79ca', 'prfm PLIL2KEEP, [x14, x11{, LSL{#3}}]', 0, ()),
    ('f8ab79cb', 'prfm PLIL2STRM, [x14, x11{, LSL{#3}}]', 0, ()),
    ('f8ab79cc', 'prfm PLIL3KEEP, [x14, x11{, LSL{#3}}]', 0, ()),
    ('f8ab79cd', 'prfm PLIL3STRM, [x14, x11{, LSL{#3}}]', 0, ()),
    ('f8ab79d0', 'prfm PSTL1KEEP, [x14, x11{, LSL{#3}}]', 0, ()),
    ('f8ab79d1', 'prfm PSTL1STRM, [x14, x11{, LSL{#3}}]', 0, ()),
    ('f8ab79d2', 'prfm PSTL2KEEP, [x14, x11{, LSL{#3}}]', 0, ()),
    ('f8ab79d3', 'prfm PSTL2STRM, [x14, x11{, LSL{#3}}]', 0, ()),
    ('f8ab79d4', 'prfm PSTL3KEEP, [x14, x11{, LSL{#3}}]', 0, ()),
    ('f8ab79d5', 'prfm PSTL3STRM, [x14, x11{, LSL{#3}}]', 0, ()),
    ('f8abf9c0', 'prfm PLDL1KEEP, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('f8abf9c1', 'prfm PLDL1STRM, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('f8abf9c2', 'prfm PLDL2KEEP, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('f8abf9c3', 'prfm PLDL2STRM, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('f8abf9c4', 'prfm PLDL3KEEP, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('f8abf9c5', 'prfm PLDL3STRM, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('f8abf9c8', 'prfm PLIL1KEEP, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('f8abf9c9', 'prfm PLIL1STRM, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('f8abf9ca', 'prfm PLIL2KEEP, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('f8abf9cb', 'prfm PLIL2STRM, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('f8abf9cc', 'prfm PLIL3KEEP, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('f8abf9cd', 'prfm PLIL3STRM, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('f8abf9d0', 'prfm PSTL1KEEP, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('f8abf9d1', 'prfm PSTL1STRM, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('f8abf9d2', 'prfm PSTL2KEEP, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('f8abf9d3', 'prfm PSTL2STRM, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('f8abf9d4', 'prfm PSTL3KEEP, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('f8abf9d5', 'prfm PSTL3STRM, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('fc2b59c3', 'str d3, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('fc2bd9c3', 'str d3, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('fc2b69c3', 'str d3, [x14, x11{, LSL{#0}}]', 0, ()),
    ('fc2b79c3', 'str d3, [x14, x11{, LSL{#3}}]', 0, ()),
    ('fc2bf9c3', 'str d3, [x14, x11{, SXTX{#0}}]', 0, ()),
    ('fc6b59c3', 'ldr d3, [x14, w11{, UXTW{#0}}]', 0, ()),
    ('fc6bd9c3', 'ldr d3, [x14, w11{, SXTW{#0}}]', 0, ()),
    ('fc6b69c3', 'ldr d3, [x14, x11{, LSL{#0}}]', 0, ()),
    ('fc6b79c3', 'ldr d3, [x14, x11{, LSL{#3}}]', 0, ()),
    ('fc6bf9c3', 'ldr d3, [x14, x11{, SXTX{#0}}]', 0, ()),
    
    #Load/store register (unsigned immediate)
    
    ('3910f1c3', 'strb w3, [x14{, #43c}]', 0, ()),
    ('3950f1c3', 'ldrb w3, [x14{, #43c}]', 0, ()),
    ('3990f1c3', 'ldrsb x3, [x14{, #43c}]', 0, ()),
    ('39d0f1c3', 'ldrsb w3, [x14{, #43c}]', 0, ()),
    ('3d10f1c3', 'str b3, [x14{, #43c}]', 0, ()),
    ('3d50f1c3', 'ldr b3, [x14{, #43c}]', 0, ()),
    ('3d90f1c3', 'str q3, [x14{, #43c0}]', 0, ()),
    ('3dd0f1c3', 'ldr q3, [x14{, #43c0}]', 0, ()),
    ('7910f1c3', 'strh w3, [x14{, #878}]', 0, ()),
    ('7950f1c3', 'ldrh w3, [x14{, #878}]', 0, ()),
    ('7990f1c3', 'ldrsh x3, [x14{, #878}]', 0, ()),
    ('79d0f1c3', 'ldrsh w3, [x14{, #878}]', 0, ()),
    ('7d10f1c3', 'str h3, [x14{, #878}]', 0, ()),
    ('7d50f1c3', 'ldr h3, [x14{, #878}]', 0, ()),
    ('b910f1c3', 'str w3, [x14{, #10f0}]', 0, ()),
    ('b950f1c3', 'ldr w3, [x14{, #10f0}]', 0, ()),
    ('b990f1c3', 'ldrsw x3, [x14{, #10f0}]', 0, ()),
    ('bd10f1c3', 'str s3, [x14{, #10f0}]', 0, ()),
    ('bd50f1c3', 'ldr s3, [x14{, #10f0}]', 0, ()),
    ('f910f1c3', 'str x3, [x14{, #21e0}]', 0, ()),
    ('f950f1c3', 'ldr x3, [x14{, #21e0}]', 0, ()),
    ('f990f1c0', 'prfm PLDL1KEEP, [x14{, #21e0}]', 0, ()),
    ('f990f1c1', 'prfm PLDL1STRM, [x14{, #21e0}]', 0, ()),
    ('f990f1c2', 'prfm PLDL2KEEP, [x14{, #21e0}]', 0, ()),
    ('f990f1c3', 'prfm PLDL2STRM, [x14{, #21e0}]', 0, ()),
    ('f990f1c4', 'prfm PLDL3KEEP, [x14{, #21e0}]', 0, ()),
    ('f990f1c5', 'prfm PLDL3STRM, [x14{, #21e0}]', 0, ()),
    ('f990f1c8', 'prfm PLIL1KEEP, [x14{, #21e0}]', 0, ()),
    ('f990f1c9', 'prfm PLIL1STRM, [x14{, #21e0}]', 0, ()),
    ('f990f1ca', 'prfm PLIL2KEEP, [x14{, #21e0}]', 0, ()),
    ('f990f1cb', 'prfm PLIL2STRM, [x14{, #21e0}]', 0, ()),
    ('f990f1cc', 'prfm PLIL3KEEP, [x14{, #21e0}]', 0, ()),
    ('f990f1cd', 'prfm PLIL3STRM, [x14{, #21e0}]', 0, ()),
    ('f990f1d0', 'prfm PSTL1KEEP, [x14{, #21e0}]', 0, ()),
    ('f990f1d1', 'prfm PSTL1STRM, [x14{, #21e0}]', 0, ()),
    ('f990f1d2', 'prfm PSTL2KEEP, [x14{, #21e0}]', 0, ()),
    ('f990f1d3', 'prfm PSTL2STRM, [x14{, #21e0}]', 0, ()),
    ('f990f1d4', 'prfm PSTL3KEEP, [x14{, #21e0}]', 0, ()),
    ('f990f1d5', 'prfm PSTL3STRM, [x14{, #21e0}]', 0, ()),
    ('fd10f1c3', 'str d3, [x14{, #21e0}]', 0, ()),
    ('fd50f1c3', 'ldr d3, [x14{, #21e0}]', 0, ()),
    
    #AdvSIMD load/store multiple structures
    
    #each set of 7 tests has a different mnemonic (disregarding shared st1/ld1 variants)
    #each set tests for all 7 possible values of <T>
    #all tests are for the no offset variants
    #st4
    ('0c0001c3', 'st4 { v3.8b, v4.8b, v5.8b, v6.8b }, [x14]', 0, ()),
    ('4c0001c3', 'st4 { v3.16b, v4.16b, v5.16b, v6.16b }, [x14]', 0, ()),
    ('0c0005c3', 'st4 { v3.4h, v4.4h, v5.4h, v6.4h }, [x14]', 0, ()),
    ('4c0005c3', 'st4 { v3.8h, v4.8h, v5.8h, v6.8h }, [x14]', 0, ()),
    ('0c0009c3', 'st4 { v3.2s, v4.2s, v5.2s, v6.2s }, [x14]', 0, ()),
    ('4c0009c3', 'st4 { v3.4s, v4.4s, v5.4s, v6.4s }, [x14]', 0, ()),
    ('4c000dc3', 'st4 { v3.2d, v4.2d, v5.2d, v6.2d }, [x14]', 0, ()),
    #st1(4)
    ('0c0021c3', 'st1 { v3.8b, v4.8b, v5.8b, v6.8b }, [x14]', 0, ()),
    ('4c0021c3', 'st1 { v3.16b, v4.16b, v5.16b, v6.16b }, [x14]', 0, ()),
    ('0c0025c3', 'st1 { v3.4h, v4.4h, v5.4h, v6.4h }, [x14]', 0, ()),
    ('4c0025c3', 'st1 { v3.8h, v4.8h, v5.8h, v6.8h }, [x14]', 0, ()),
    ('0c0029c3', 'st1 { v3.2s, v4.2s, v5.2s, v6.2s }, [x14]', 0, ()),
    ('4c0029c3', 'st1 { v3.4s, v4.4s, v5.4s, v6.4s }, [x14]', 0, ()),
    ('4c002dc3', 'st1 { v3.2d, v4.2d, v5.2d, v6.2d }, [x14]', 0, ()),
    #st3
    ('0c0041c3', 'st3 { v3.8b, v4.8b, v5.8b }, [x14]', 0, ()),
    ('4c0041c3', 'st3 { v3.16b, v4.16b, v5.16b }, [x14]', 0, ()),
    ('0c0045c3', 'st3 { v3.4h, v4.4h, v5.4h }, [x14]', 0, ()),
    ('4c0045c3', 'st3 { v3.8h, v4.8h, v5.8h }, [x14]', 0, ()),
    ('0c0049c3', 'st3 { v3.2s, v4.2s, v5.2s }, [x14]', 0, ()),
    ('4c0049c3', 'st3 { v3.4s, v4.4s, v5.4s }, [x14]', 0, ()),
    ('4c004dc3', 'st3 { v3.2d, v4.2d, v5.2d }, [x14]', 0, ()),
    #st1(3)
    ('0c0061c3', 'st1 { v3.8b, v4.8b, v5.8b }, [x14]', 0, ()),
    ('4c0061c3', 'st1 { v3.16b, v4.16b, v5.16b }, [x14]', 0, ()),
    ('0c0065c3', 'st1 { v3.4h, v4.4h, v5.4h }, [x14]', 0, ()),
    ('4c0065c3', 'st1 { v3.8h, v4.8h, v5.8h }, [x14]', 0, ()),
    ('0c0069c3', 'st1 { v3.2s, v4.2s, v5.2s }, [x14]', 0, ()),
    ('4c0069c3', 'st1 { v3.4s, v4.4s, v5.4s }, [x14]', 0, ()),
    ('4c006dc3', 'st1 { v3.2d, v4.2d, v5.2d }, [x14]', 0, ()),
    #st1(1)
    ('0c0071c3', 'st1 { v3.8b }, [x14]', 0, ()),
    ('4c0071c3', 'st1 { v3.16b }, [x14]', 0, ()),
    ('0c0075c3', 'st1 { v3.4h }, [x14]', 0, ()),
    ('4c0075c3', 'st1 { v3.8h }, [x14]', 0, ()),
    ('0c0079c3', 'st1 { v3.2s }, [x14]', 0, ()),
    ('4c0079c3', 'st1 { v3.4s }, [x14]', 0, ()),
    ('4c007dc3', 'st1 { v3.2d }, [x14]', 0, ()),
    #st2
    ('0c0081c3', 'st2 { v3.8b, v4.8b }, [x14]', 0, ()),
    ('4c0081c3', 'st2 { v3.16b, v4.16b }, [x14]', 0, ()),
    ('0c0085c3', 'st2 { v3.4h, v4.4h }, [x14]', 0, ()),
    ('4c0085c3', 'st2 { v3.8h, v4.8h }, [x14]', 0, ()),
    ('0c0089c3', 'st2 { v3.2s, v4.2s }, [x14]', 0, ()),
    ('4c0089c3', 'st2 { v3.4s, v4.4s }, [x14]', 0, ()),
    ('4c008dc3', 'st2 { v3.2d, v4.2d }, [x14]', 0, ()),
    #st1(2)
    ('0c00a1c3', 'st1 { v3.8b, v4.8b }, [x14]', 0, ()),
    ('4c00a1c3', 'st1 { v3.16b, v4.16b }, [x14]', 0, ()),
    ('0c00a5c3', 'st1 { v3.4h, v4.4h }, [x14]', 0, ()),
    ('4c00a5c3', 'st1 { v3.8h, v4.8h }, [x14]', 0, ()),
    ('0c00a9c3', 'st1 { v3.2s, v4.2s }, [x14]', 0, ()),
    ('4c00a9c3', 'st1 { v3.4s, v4.4s }, [x14]', 0, ()),
    ('4c00adc3', 'st1 { v3.2d, v4.2d }, [x14]', 0, ()),
    #ld4
    ('0c4001c3', 'ld4 { v3.8b, v4.8b, v5.8b, v6.8b }, [x14]', 0, ()),
    ('4c4001c3', 'ld4 { v3.16b, v4.16b, v5.16b, v6.16b }, [x14]', 0, ()),
    ('0c4005c3', 'ld4 { v3.4h, v4.4h, v5.4h, v6.4h }, [x14]', 0, ()),
    ('4c4005c3', 'ld4 { v3.8h, v4.8h, v5.8h, v6.8h }, [x14]', 0, ()),
    ('0c4009c3', 'ld4 { v3.2s, v4.2s, v5.2s, v6.2s }, [x14]', 0, ()),
    ('4c4009c3', 'ld4 { v3.4s, v4.4s, v5.4s, v6.4s }, [x14]', 0, ()),
    ('4c400dc3', 'ld4 { v3.2d, v4.2d, v5.2d, v6.2d }, [x14]', 0, ()),
    #ld1(4)
    ('0c4021c3', 'ld1 { v3.8b, v4.8b, v5.8b, v6.8b }, [x14]', 0, ()),
    ('4c4021c3', 'ld1 { v3.16b, v4.16b, v5.16b, v6.16b }, [x14]', 0, ()),
    ('0c4025c3', 'ld1 { v3.4h, v4.4h, v5.4h, v6.4h }, [x14]', 0, ()),
    ('4c4025c3', 'ld1 { v3.8h, v4.8h, v5.8h, v6.8h }, [x14]', 0, ()),
    ('0c4029c3', 'ld1 { v3.2s, v4.2s, v5.2s, v6.2s }, [x14]', 0, ()),
    ('4c4029c3', 'ld1 { v3.4s, v4.4s, v5.4s, v6.4s }, [x14]', 0, ()),
    ('4c402dc3', 'ld1 { v3.2d, v4.2d, v5.2d, v6.2d }, [x14]', 0, ()),
    #ld3
    ('0c4041c3', 'ld3 { v3.8b, v4.8b, v5.8b }, [x14]', 0, ()),
    ('4c4041c3', 'ld3 { v3.16b, v4.16b, v5.16b }, [x14]', 0, ()),
    ('0c4045c3', 'ld3 { v3.4h, v4.4h, v5.4h }, [x14]', 0, ()),
    ('4c4045c3', 'ld3 { v3.8h, v4.8h, v5.8h }, [x14]', 0, ()),
    ('0c4049c3', 'ld3 { v3.2s, v4.2s, v5.2s }, [x14]', 0, ()),
    ('4c4049c3', 'ld3 { v3.4s, v4.4s, v5.4s }, [x14]', 0, ()),
    ('4c404dc3', 'ld3 { v3.2d, v4.2d, v5.2d }, [x14]', 0, ()),
    #ld1(3)
    ('0c4061c3', 'ld1 { v3.8b, v4.8b, v5.8b }, [x14]', 0, ()),
    ('4c4061c3', 'ld1 { v3.16b, v4.16b, v5.16b }, [x14]', 0, ()),
    ('0c4065c3', 'ld1 { v3.4h, v4.4h, v5.4h }, [x14]', 0, ()),
    ('4c4065c3', 'ld1 { v3.8h, v4.8h, v5.8h }, [x14]', 0, ()),
    ('0c4069c3', 'ld1 { v3.2s, v4.2s, v5.2s }, [x14]', 0, ()),
    ('4c4069c3', 'ld1 { v3.4s, v4.4s, v5.4s }, [x14]', 0, ()),
    ('4c406dc3', 'ld1 { v3.2d, v4.2d, v5.2d }, [x14]', 0, ()),
    #ld1(1)
    ('0c4071c3', 'ld1 { v3.8b }, [x14]', 0, ()),
    ('4c4071c3', 'ld1 { v3.16b }, [x14]', 0, ()),
    ('0c4075c3', 'ld1 { v3.4h }, [x14]', 0, ()),
    ('4c4075c3', 'ld1 { v3.8h }, [x14]', 0, ()),
    ('0c4079c3', 'ld1 { v3.2s }, [x14]', 0, ()),
    ('4c4079c3', 'ld1 { v3.4s }, [x14]', 0, ()),
    ('4c407dc3', 'ld1 { v3.2d }, [x14]', 0, ()),
    #ld2
    ('0c4081c3', 'ld2 { v3.8b, v4.8b }, [x14]', 0, ()),
    ('4c4081c3', 'ld2 { v3.16b, v4.16b }, [x14]', 0, ()),
    ('0c4085c3', 'ld2 { v3.4h, v4.4h }, [x14]', 0, ()),
    ('4c4085c3', 'ld2 { v3.8h, v4.8h }, [x14]', 0, ()),
    ('0c4089c3', 'ld2 { v3.2s, v4.2s }, [x14]', 0, ()),
    ('4c4089c3', 'ld2 { v3.4s, v4.4s }, [x14]', 0, ()),
    ('4c408dc3', 'ld2 { v3.2d, v4.2d }, [x14]', 0, ()),
    #ld1(2)
    ('0c40a1c3', 'ld1 { v3.8b, v4.8b }, [x14]', 0, ()),
    ('4c40a1c3', 'ld1 { v3.16b, v4.16b }, [x14]', 0, ()),
    ('0c40a5c3', 'ld1 { v3.4h, v4.4h }, [x14]', 0, ()),
    ('4c40a5c3', 'ld1 { v3.8h, v4.8h }, [x14]', 0, ()),
    ('0c40a9c3', 'ld1 { v3.2s, v4.2s }, [x14]', 0, ()),
    ('4c40a9c3', 'ld1 { v3.4s, v4.4s }, [x14]', 0, ()),
    ('4c40adc3', 'ld1 { v3.2d, v4.2d }, [x14]', 0, ()),
    
    #AdvSIMD Load/store multiple structures (post-indexed)

    #each set of 7 tests has a different mnemonic (disregarding shared st1/ld1 variants)
    #each set tests for all 7 possible values of <T>
    #st4 (register offset)
    ('0c8b01c3', 'st4 { v3.8b, v4.8b, v5.8b, v6.8b }, [x14], x11', 0, ()),
    ('4c8b01c3', 'st4 { v3.16b, v4.16b, v5.16b, v6.16b }, [x14], x11', 0, ()),
    ('0c8b05c3', 'st4 { v3.4h, v4.4h, v5.4h, v6.4h }, [x14], x11', 0, ()),
    ('4c8b05c3', 'st4 { v3.8h, v4.8h, v5.8h, v6.8h }, [x14], x11', 0, ()),
    ('0c8b09c3', 'st4 { v3.2s, v4.2s, v5.2s, v6.2s }, [x14], x11', 0, ()),
    ('4c8b09c3', 'st4 { v3.4s, v4.4s, v5.4s, v6.4s }, [x14], x11', 0, ()),
    ('4c8b0dc3', 'st4 { v3.2d, v4.2d, v5.2d, v6.2d }, [x14], x11', 0, ()),
    #st1(4) (register offset)
    ('0c8b21c3', 'st1 { v3.8b, v4.8b, v5.8b, v6.8b }, [x14], x11', 0, ()),
    ('4c8b21c3', 'st1 { v3.16b, v4.16b, v5.16b, v6.16b }, [x14], x11', 0, ()),
    ('0c8b25c3', 'st1 { v3.4h, v4.4h, v5.4h, v6.4h }, [x14], x11', 0, ()),
    ('4c8b25c3', 'st1 { v3.8h, v4.8h, v5.8h, v6.8h }, [x14], x11', 0, ()),
    ('0c8b29c3', 'st1 { v3.2s, v4.2s, v5.2s, v6.2s }, [x14], x11', 0, ()),
    ('4c8b29c3', 'st1 { v3.4s, v4.4s, v5.4s, v6.4s }, [x14], x11', 0, ()),
    ('4c8b2dc3', 'st1 { v3.2d, v4.2d, v5.2d, v6.2d }, [x14], x11', 0, ()),
    #st3 (register offset)
    ('0c8b41c3', 'st3 { v3.8b, v4.8b, v5.8b }, [x14], x11', 0, ()),
    ('4c8b41c3', 'st3 { v3.16b, v4.16b, v5.16b }, [x14], x11', 0, ()),
    ('0c8b45c3', 'st3 { v3.4h, v4.4h, v5.4h }, [x14], x11', 0, ()),
    ('4c8b45c3', 'st3 { v3.8h, v4.8h, v5.8h }, [x14], x11', 0, ()),
    ('0c8b49c3', 'st3 { v3.2s, v4.2s, v5.2s }, [x14], x11', 0, ()),
    ('4c8b49c3', 'st3 { v3.4s, v4.4s, v5.4s }, [x14], x11', 0, ()),
    ('4c8b4dc3', 'st3 { v3.2d, v4.2d, v5.2d }, [x14], x11', 0, ()),
    #st1(3) (register offset)
    ('0c8b61c3', 'st1 { v3.8b, v4.8b, v5.8b }, [x14], x11', 0, ()),
    ('4c8b61c3', 'st1 { v3.16b, v4.16b, v5.16b }, [x14], x11', 0, ()),
    ('0c8b65c3', 'st1 { v3.4h, v4.4h, v5.4h }, [x14], x11', 0, ()),
    ('4c8b65c3', 'st1 { v3.8h, v4.8h, v5.8h }, [x14], x11', 0, ()),
    ('0c8b69c3', 'st1 { v3.2s, v4.2s, v5.2s }, [x14], x11', 0, ()),
    ('4c8b69c3', 'st1 { v3.4s, v4.4s, v5.4s }, [x14], x11', 0, ()),
    ('4c8b6dc3', 'st1 { v3.2d, v4.2d, v5.2d }, [x14], x11', 0, ()),
    #st1(1) (register offset)
    ('0c8b71c3', 'st1 { v3.8b }, [x14], x11', 0, ()),
    ('4c8b71c3', 'st1 { v3.16b }, [x14], x11', 0, ()),
    ('0c8b75c3', 'st1 { v3.4h }, [x14], x11', 0, ()),
    ('4c8b75c3', 'st1 { v3.8h }, [x14], x11', 0, ()),
    ('0c8b79c3', 'st1 { v3.2s }, [x14], x11', 0, ()),
    ('4c8b79c3', 'st1 { v3.4s }, [x14], x11', 0, ()),
    ('4c8b7dc3', 'st1 { v3.2d }, [x14], x11', 0, ()),
    #st2 (register offset)
    ('0c8b81c3', 'st2 { v3.8b, v4.8b }, [x14], x11', 0, ()),
    ('4c8b81c3', 'st2 { v3.16b, v4.16b }, [x14], x11', 0, ()),
    ('0c8b85c3', 'st2 { v3.4h, v4.4h }, [x14], x11', 0, ()),
    ('4c8b85c3', 'st2 { v3.8h, v4.8h }, [x14], x11', 0, ()),
    ('0c8b89c3', 'st2 { v3.2s, v4.2s }, [x14], x11', 0, ()),
    ('4c8b89c3', 'st2 { v3.4s, v4.4s }, [x14], x11', 0, ()),
    ('4c8b8dc3', 'st2 { v3.2d, v4.2d }, [x14], x11', 0, ()),
    #st1(2) (register offset)
    ('0c8ba1c3', 'st1 { v3.8b, v4.8b }, [x14], x11', 0, ()),
    ('4c8ba1c3', 'st1 { v3.16b, v4.16b }, [x14], x11', 0, ()),
    ('0c8ba5c3', 'st1 { v3.4h, v4.4h }, [x14], x11', 0, ()),
    ('4c8ba5c3', 'st1 { v3.8h, v4.8h }, [x14], x11', 0, ()),
    ('0c8ba9c3', 'st1 { v3.2s, v4.2s }, [x14], x11', 0, ()),
    ('4c8ba9c3', 'st1 { v3.4s, v4.4s }, [x14], x11', 0, ()),
    ('4c8badc3', 'st1 { v3.2d, v4.2d }, [x14], x11', 0, ()),
    #st4 (immediate offset)
    ('0c9f01c3', 'st4 { v3.8b, v4.8b, v5.8b, v6.8b }, [x14], #32', 0, ()),
    ('4c9f01c3', 'st4 { v3.16b, v4.16b, v5.16b, v6.16b }, [x14], #64', 0, ()),
    ('0c9f05c3', 'st4 { v3.4h, v4.4h, v5.4h, v6.4h }, [x14], #32', 0, ()),
    ('4c9f05c3', 'st4 { v3.8h, v4.8h, v5.8h, v6.8h }, [x14], #64', 0, ()),
    ('0c9f09c3', 'st4 { v3.2s, v4.2s, v5.2s, v6.2s }, [x14], #32', 0, ()),
    ('4c9f09c3', 'st4 { v3.4s, v4.4s, v5.4s, v6.4s }, [x14], #64', 0, ()),
    ('4c9f0dc3', 'st4 { v3.2d, v4.2d, v5.2d, v6.2d }, [x14], #64', 0, ()),
    #st1(4) (immediate offset)
    ('0c9f21c3', 'st1 { v3.8b, v4.8b, v5.8b, v6.8b }, [x14], #32', 0, ()),
    ('4c9f21c3', 'st1 { v3.16b, v4.16b, v5.16b, v6.16b }, [x14], #64', 0, ()),
    ('0c9f25c3', 'st1 { v3.4h, v4.4h, v5.4h, v6.4h }, [x14], #32', 0, ()),
    ('4c9f25c3', 'st1 { v3.8h, v4.8h, v5.8h, v6.8h }, [x14], #64', 0, ()),
    ('0c9f29c3', 'st1 { v3.2s, v4.2s, v5.2s, v6.2s }, [x14], #32', 0, ()),
    ('4c9f29c3', 'st1 { v3.4s, v4.4s, v5.4s, v6.4s }, [x14], #64', 0, ()),
    ('4c9f2dc3', 'st1 { v3.2d, v4.2d, v5.2d, v6.2d }, [x14], #64', 0, ()),
    #st3 (immediate offset)
    ('0c9f41c3', 'st3 { v3.8b, v4.8b, v5.8b }, [x14], #32', 0, ()),
    ('4c9f41c3', 'st3 { v3.16b, v4.16b, v5.16b }, [x14], #64', 0, ()),
    ('0c9f45c3', 'st3 { v3.4h, v4.4h, v5.4h }, [x14], #32', 0, ()),
    ('4c9f45c3', 'st3 { v3.8h, v4.8h, v5.8h }, [x14], #64', 0, ()),
    ('0c9f49c3', 'st3 { v3.2s, v4.2s, v5.2s }, [x14], #32', 0, ()),
    ('4c9f49c3', 'st3 { v3.4s, v4.4s, v5.4s }, [x14], #64', 0, ()),
    ('4c9f4dc3', 'st3 { v3.2d, v4.2d, v5.2d }, [x14], #64', 0, ()),
    #st1(3) (immediate offset)
    ('0c9f61c3', 'st1 { v3.8b, v4.8b, v5.8b }, [x14], #32', 0, ()),
    ('4c9f61c3', 'st1 { v3.16b, v4.16b, v5.16b }, [x14], #64', 0, ()),
    ('0c9f65c3', 'st1 { v3.4h, v4.4h, v5.4h }, [x14], #32', 0, ()),
    ('4c9f65c3', 'st1 { v3.8h, v4.8h, v5.8h }, [x14], #64', 0, ()),
    ('0c9f69c3', 'st1 { v3.2s, v4.2s, v5.2s }, [x14], #32', 0, ()),
    ('4c9f69c3', 'st1 { v3.4s, v4.4s, v5.4s }, [x14], #64', 0, ()),
    ('4c9f6dc3', 'st1 { v3.2d, v4.2d, v5.2d }, [x14], #64', 0, ()),
    #st1(1) (immediate offset)
    ('0c9f71c3', 'st1 { v3.8b }, [x14], #32', 0, ()),
    ('4c9f71c3', 'st1 { v3.16b }, [x14], #64', 0, ()),
    ('0c9f75c3', 'st1 { v3.4h }, [x14], #32', 0, ()),
    ('4c9f75c3', 'st1 { v3.8h }, [x14], #64', 0, ()),
    ('0c9f79c3', 'st1 { v3.2s }, [x14], #32', 0, ()),
    ('4c9f79c3', 'st1 { v3.4s }, [x14], #64', 0, ()),
    ('4c9f7dc3', 'st1 { v3.2d }, [x14], #64', 0, ()),
    #st2 (immediate offset)
    ('0c9f81c3', 'st2 { v3.8b, v4.8b }, [x14], #32', 0, ()),
    ('4c9f81c3', 'st2 { v3.16b, v4.16b }, [x14], #64', 0, ()),
    ('0c9f85c3', 'st2 { v3.4h, v4.4h }, [x14], #32', 0, ()),
    ('4c9f85c3', 'st2 { v3.8h, v4.8h }, [x14], #64', 0, ()),
    ('0c9f89c3', 'st2 { v3.2s, v4.2s }, [x14], #32', 0, ()),
    ('4c9f89c3', 'st2 { v3.4s, v4.4s }, [x14], #64', 0, ()),
    ('4c9f8dc3', 'st2 { v3.2d, v4.2d }, [x14], #64', 0, ()),
    #st1(2) (immediate offset)
    ('0c9fa1c3', 'st1 { v3.8b, v4.8b }, [x14], #32', 0, ()),
    ('4c9fa1c3', 'st1 { v3.16b, v4.16b }, [x14], #64', 0, ()),
    ('0c9fa5c3', 'st1 { v3.4h, v4.4h }, [x14], #32', 0, ()),
    ('4c9fa5c3', 'st1 { v3.8h, v4.8h }, [x14], #64', 0, ()),
    ('0c9fa9c3', 'st1 { v3.2s, v4.2s }, [x14], #32', 0, ()),
    ('4c9fa9c3', 'st1 { v3.4s, v4.4s }, [x14], #64', 0, ()),
    ('4c9fadc3', 'st1 { v3.2d, v4.2d }, [x14], #64', 0, ()),
    #ld4 (register offset)
    ('0ccb01c3', 'ld4 { v3.8b, v4.8b, v5.8b, v6.8b }, [x14], x11', 0, ()),
    ('4ccb01c3', 'ld4 { v3.16b, v4.16b, v5.16b, v6.16b }, [x14], x11', 0, ()),
    ('0ccb05c3', 'ld4 { v3.4h, v4.4h, v5.4h, v6.4h }, [x14], x11', 0, ()),
    ('4ccb05c3', 'ld4 { v3.8h, v4.8h, v5.8h, v6.8h }, [x14], x11', 0, ()),
    ('0ccb09c3', 'ld4 { v3.2s, v4.2s, v5.2s, v6.2s }, [x14], x11', 0, ()),
    ('4ccb09c3', 'ld4 { v3.4s, v4.4s, v5.4s, v6.4s }, [x14], x11', 0, ()),
    ('4ccb0dc3', 'ld4 { v3.2d, v4.2d, v5.2d, v6.2d }, [x14], x11', 0, ()),
    #ld1(4) (register offset)
    ('0ccb21c3', 'ld1 { v3.8b, v4.8b, v5.8b, v6.8b }, [x14], x11', 0, ()),
    ('4ccb21c3', 'ld1 { v3.16b, v4.16b, v5.16b, v6.16b }, [x14], x11', 0, ()),
    ('0ccb25c3', 'ld1 { v3.4h, v4.4h, v5.4h, v6.4h }, [x14], x11', 0, ()),
    ('4ccb25c3', 'ld1 { v3.8h, v4.8h, v5.8h, v6.8h }, [x14], x11', 0, ()),
    ('0ccb29c3', 'ld1 { v3.2s, v4.2s, v5.2s, v6.2s }, [x14], x11', 0, ()),
    ('4ccb29c3', 'ld1 { v3.4s, v4.4s, v5.4s, v6.4s }, [x14], x11', 0, ()),
    ('4ccb2dc3', 'ld1 { v3.2d, v4.2d, v5.2d, v6.2d }, [x14], x11', 0, ()),
    #ld3 (register offset)
    ('0ccb41c3', 'ld3 { v3.8b, v4.8b, v5.8b }, [x14], x11', 0, ()),
    ('4ccb41c3', 'ld3 { v3.16b, v4.16b, v5.16b }, [x14], x11', 0, ()),
    ('0ccb45c3', 'ld3 { v3.4h, v4.4h, v5.4h }, [x14], x11', 0, ()),
    ('4ccb45c3', 'ld3 { v3.8h, v4.8h, v5.8h }, [x14], x11', 0, ()),
    ('0ccb49c3', 'ld3 { v3.2s, v4.2s, v5.2s }, [x14], x11', 0, ()),
    ('4ccb49c3', 'ld3 { v3.4s, v4.4s, v5.4s }, [x14], x11', 0, ()),
    ('4ccb4dc3', 'ld3 { v3.2d, v4.2d, v5.2d }, [x14], x11', 0, ()),
    #ld1(3) (register offset)
    ('0ccb61c3', 'ld1 { v3.8b, v4.8b, v5.8b }, [x14], x11', 0, ()),
    ('4ccb61c3', 'ld1 { v3.16b, v4.16b, v5.16b }, [x14], x11', 0, ()),
    ('0ccb65c3', 'ld1 { v3.4h, v4.4h, v5.4h }, [x14], x11', 0, ()),
    ('4ccb65c3', 'ld1 { v3.8h, v4.8h, v5.8h }, [x14], x11', 0, ()),
    ('0ccb69c3', 'ld1 { v3.2s, v4.2s, v5.2s }, [x14], x11', 0, ()),
    ('4ccb69c3', 'ld1 { v3.4s, v4.4s, v5.4s }, [x14], x11', 0, ()),
    ('4ccb6dc3', 'ld1 { v3.2d, v4.2d, v5.2d }, [x14], x11', 0, ()),
    #ld1(1) (register offset)
    ('0ccb71c3', 'ld1 { v3.8b }, [x14], x11', 0, ()),
    ('4ccb71c3', 'ld1 { v3.16b }, [x14], x11', 0, ()),
    ('0ccb75c3', 'ld1 { v3.4h }, [x14], x11', 0, ()),
    ('4ccb75c3', 'ld1 { v3.8h }, [x14], x11', 0, ()),
    ('0ccb79c3', 'ld1 { v3.2s }, [x14], x11', 0, ()),
    ('4ccb79c3', 'ld1 { v3.4s }, [x14], x11', 0, ()),
    ('4ccb7dc3', 'ld1 { v3.2d }, [x14], x11', 0, ()),
    #ld2 (register offset)
    ('0ccb81c3', 'ld2 { v3.8b, v4.8b }, [x14], x11', 0, ()),
    ('4ccb81c3', 'ld2 { v3.16b, v4.16b }, [x14], x11', 0, ()),
    ('0ccb85c3', 'ld2 { v3.4h, v4.4h }, [x14], x11', 0, ()),
    ('4ccb85c3', 'ld2 { v3.8h, v4.8h }, [x14], x11', 0, ()),
    ('0ccb89c3', 'ld2 { v3.2s, v4.2s }, [x14], x11', 0, ()),
    ('4ccb89c3', 'ld2 { v3.4s, v4.4s }, [x14], x11', 0, ()),
    ('4ccb8dc3', 'ld2 { v3.2d, v4.2d }, [x14], x11', 0, ()),
    #ld1(2) (register offset)
    ('0ccba1c3', 'ld1 { v3.8b, v4.8b }, [x14], x11', 0, ()),
    ('4ccba1c3', 'ld1 { v3.16b, v4.16b }, [x14], x11', 0, ()),
    ('0ccba5c3', 'ld1 { v3.4h, v4.4h }, [x14], x11', 0, ()),
    ('4ccba5c3', 'ld1 { v3.8h, v4.8h }, [x14], x11', 0, ()),
    ('0ccba9c3', 'ld1 { v3.2s, v4.2s }, [x14], x11', 0, ()),
    ('4ccba9c3', 'ld1 { v3.4s, v4.4s }, [x14], x11', 0, ()),
    ('4ccbadc3', 'ld1 { v3.2d, v4.2d }, [x14], x11', 0, ()),
    #ld4 (immediate offset)
    ('0cdf01c3', 'ld4 { v3.8b, v4.8b, v5.8b, v6.8b }, [x14], #32', 0, ()),
    ('4cdf01c3', 'ld4 { v3.16b, v4.16b, v5.16b, v6.16b }, [x14], #64', 0, ()),
    ('0cdf05c3', 'ld4 { v3.4h, v4.4h, v5.4h, v6.4h }, [x14], #32', 0, ()),
    ('4cdf05c3', 'ld4 { v3.8h, v4.8h, v5.8h, v6.8h }, [x14], #64', 0, ()),
    ('0cdf09c3', 'ld4 { v3.2s, v4.2s, v5.2s, v6.2s }, [x14], #32', 0, ()),
    ('4cdf09c3', 'ld4 { v3.4s, v4.4s, v5.4s, v6.4s }, [x14], #64', 0, ()),
    ('4cdf0dc3', 'ld4 { v3.2d, v4.2d, v5.2d, v6.2d }, [x14], #64', 0, ()),
    #ld1(4) (immediate offset)
    ('0cdf21c3', 'ld1 { v3.8b, v4.8b, v5.8b, v6.8b }, [x14], #32', 0, ()),
    ('4cdf21c3', 'ld1 { v3.16b, v4.16b, v5.16b, v6.16b }, [x14], #64', 0, ()),
    ('0cdf25c3', 'ld1 { v3.4h, v4.4h, v5.4h, v6.4h }, [x14], #32', 0, ()),
    ('4cdf25c3', 'ld1 { v3.8h, v4.8h, v5.8h, v6.8h }, [x14], #64', 0, ()),
    ('0cdf29c3', 'ld1 { v3.2s, v4.2s, v5.2s, v6.2s }, [x14], #32', 0, ()),
    ('4cdf29c3', 'ld1 { v3.4s, v4.4s, v5.4s, v6.4s }, [x14], #64', 0, ()),
    ('4cdf2dc3', 'ld1 { v3.2d, v4.2d, v5.2d, v6.2d }, [x14], #64', 0, ()),
    #ld3 (immediate offset)
    ('0cdf41c3', 'ld3 { v3.8b, v4.8b, v5.8b }, [x14], #32', 0, ()),
    ('4cdf41c3', 'ld3 { v3.16b, v4.16b, v5.16b }, [x14], #64', 0, ()),
    ('0cdf45c3', 'ld3 { v3.4h, v4.4h, v5.4h }, [x14], #32', 0, ()),
    ('4cdf45c3', 'ld3 { v3.8h, v4.8h, v5.8h }, [x14], #64', 0, ()),
    ('0cdf49c3', 'ld3 { v3.2s, v4.2s, v5.2s }, [x14], #32', 0, ()),
    ('4cdf49c3', 'ld3 { v3.4s, v4.4s, v5.4s }, [x14], #64', 0, ()),
    ('4cdf4dc3', 'ld3 { v3.2d, v4.2d, v5.2d }, [x14], #64', 0, ()),
    #ld1(3) (immediate offset)
    ('0cdf61c3', 'ld1 { v3.8b, v4.8b, v5.8b }, [x14], #32', 0, ()),
    ('4cdf61c3', 'ld1 { v3.16b, v4.16b, v5.16b }, [x14], #64', 0, ()),
    ('0cdf65c3', 'ld1 { v3.4h, v4.4h, v5.4h }, [x14], #32', 0, ()),
    ('4cdf65c3', 'ld1 { v3.8h, v4.8h, v5.8h }, [x14], #64', 0, ()),
    ('0cdf69c3', 'ld1 { v3.2s, v4.2s, v5.2s }, [x14], #32', 0, ()),
    ('4cdf69c3', 'ld1 { v3.4s, v4.4s, v5.4s }, [x14], #64', 0, ()),
    ('4cdf6dc3', 'ld1 { v3.2d, v4.2d, v5.2d }, [x14], #64', 0, ()),
    #ld1(1) (immediate offset)
    ('0cdf71c3', 'ld1 { v3.8b }, [x14], #32', 0, ()),
    ('4cdf71c3', 'ld1 { v3.16b }, [x14], #64', 0, ()),
    ('0cdf75c3', 'ld1 { v3.4h }, [x14], #32', 0, ()),
    ('4cdf75c3', 'ld1 { v3.8h }, [x14], #64', 0, ()),
    ('0cdf79c3', 'ld1 { v3.2s }, [x14], #32', 0, ()),
    ('4cdf79c3', 'ld1 { v3.4s }, [x14], #64', 0, ()),
    ('4cdf7dc3', 'ld1 { v3.2d }, [x14], #64', 0, ()),
    #ld2 (immediate offset)
    ('0cdf81c3', 'ld2 { v3.8b, v4.8b }, [x14], #32', 0, ()),
    ('4cdf81c3', 'ld2 { v3.16b, v4.16b }, [x14], #64', 0, ()),
    ('0cdf85c3', 'ld2 { v3.4h, v4.4h }, [x14], #32', 0, ()),
    ('4cdf85c3', 'ld2 { v3.8h, v4.8h }, [x14], #64', 0, ()),
    ('0cdf89c3', 'ld2 { v3.2s, v4.2s }, [x14], #32', 0, ()),
    ('4cdf89c3', 'ld2 { v3.4s, v4.4s }, [x14], #64', 0, ()),
    ('4cdf8dc3', 'ld2 { v3.2d, v4.2d }, [x14], #64', 0, ()),
    #ld1(2) (immediate offset)
    ('0cdfa1c3', 'ld1 { v3.8b, v4.8b }, [x14], #32', 0, ()),
    ('4cdfa1c3', 'ld1 { v3.16b, v4.16b }, [x14], #64', 0, ()),
    ('0cdfa5c3', 'ld1 { v3.4h, v4.4h }, [x14], #32', 0, ()),
    ('4cdfa5c3', 'ld1 { v3.8h, v4.8h }, [x14], #64', 0, ()),
    ('0cdfa9c3', 'ld1 { v3.2s, v4.2s }, [x14], #32', 0, ()),
    ('4cdfa9c3', 'ld1 { v3.4s, v4.4s }, [x14], #64', 0, ()),
    ('4cdfadc3', 'ld1 { v3.2d, v4.2d }, [x14], #64', 0, ()),

    #AdvSIMD Load/store single structure
    
    #all tests are for the no offset variants
    #st1 and st3
    ('4d0019c3', 'st1 { v3.b }[#e], x14', 0, ()),
    ('4d0039c3', 'st3 { v3.b, v4.b, v5.b }[#e], x14', 0, ()),
    ('4d0059c3', 'st1 { v3.h }[#6], x14', 0, ()),
    ('4d0079c3', 'st3 { v3.h, v4.h, v5.h }[#6], x14', 0, ()),
    ('4d0091c3', 'st1 { v3.s }[#3], x14', 0, ()),
    ('4d0085c3', 'st1 { v3.d }[#1], x14', 0, ()),
    ('4d00b1c3', 'st3 { v3.s, v4.s, v5.s }[#3], x14', 0, ()),
    ('4d00a5c3', 'st3 { v3.d, v4.d, v5.d }[#1], x14', 0, ()),
    #st2 and st4
    ('4d2019c3', 'st2 { v3.b, v4.b }[#e], x14', 0, ()),
    ('4d2039c3', 'st4 { v3.b, v4.b, v5.b, v6.b }[#e], x14', 0, ()),
    ('4d2059c3', 'st2 { v3.h, v4.h }[#6], x14', 0, ()),
    ('4d2079c3', 'st4 { v3.h, v4.h, v5.h, v6.h }[#6], x14', 0, ()),
    ('4d2091c3', 'st2 { v3.s, v4.s }[#3], x14', 0, ()),
    ('4d2085c3', 'st2 { v3.d, v4.d }[#1], x14', 0, ()),
    ('4d20b1c3', 'st4 { v3.s, v4.s, v5.s, v6.s }[#3], x14', 0, ()),
    ('4d20a5c3', 'st4 { v3.d, v4.d, v5.d, v6.d }[#1], x14', 0, ()),
    #ld1 and ld3 
    ('4d4019c3', 'ld1 { v3.b }[#e], x14', 0, ()),
    ('4d4039c3', 'ld3 { v3.b, v4.b, v5.b }[#e], x14', 0, ()),
    ('4d4059c3', 'ld1 { v3.h }[#6], x14', 0, ()),
    ('4d4079c3', 'ld3 { v3.h, v4.h, v5.h }[#6], x14', 0, ()),
    ('4d4091c3', 'ld1 { v3.s }[#3], x14', 0, ()),
    ('4d4085c3', 'ld1 { v3.d }[#1], x14', 0, ()),
    ('4d40b1c3', 'ld3 { v3.s, v4.s, v5.s }[#3], x14', 0, ()),
    ('4d40a5c3', 'ld3 { v3.d, v4.d, v5.d }[#1], x14', 0, ()),
    #ld1r
    ('0d40c1c3', 'ld1r { v3.8b }, x14', 0, ()),
    ('4d40c1c3', 'ld1r { v3.16b }, x14', 0, ()),
    ('0d40c5c3', 'ld1r { v3.4h }, x14', 0, ()),
    ('4d40c5c3', 'ld1r { v3.8h }, x14', 0, ()),
    ('0d40c9c3', 'ld1r { v3.2s }, x14', 0, ()),
    ('4d40c9c3', 'ld1r { v3.4s }, x14', 0, ()),
    ('0d40cdc3', 'ld1r { v3.1d }, x14', 0, ()),
    ('4d40cdc3', 'ld1r { v3.2d }, x14', 0, ()),
    #ld3r 
    ('0d40e1c3', 'ld3r { v3.8b, v4.8b, v5.8b }, x14', 0, ()),
    ('4d40e1c3', 'ld3r { v3.16b, v4.16b, v5.16b }, x14', 0, ()),
    ('0d40e5c3', 'ld3r { v3.4h, v4.4h, v5.4h }, x14', 0, ()),
    ('4d40e5c3', 'ld3r { v3.8h, v4.8h, v5.8h }, x14', 0, ()),
    ('0d40e9c3', 'ld3r { v3.2s, v4.2s, v5.2s }, x14', 0, ()),
    ('4d40e9c3', 'ld3r { v3.4s, v4.4s, v5.4s }, x14', 0, ()),
    ('0d40edc3', 'ld3r { v3.1d, v4.1d, v5.1d }, x14', 0, ()),
    ('4d40edc3', 'ld3r { v3.2d, v4.2d, v5.2d }, x14', 0, ()),
    #ld2 and ld4 
    ('4d6019c3', 'ld2 { v3.b, v4.b }[#e], x14', 0, ()),
    ('4d6039c3', 'ld4 { v3.b, v4.b, v5.b, v6.b }[#e], x14', 0, ()),
    ('4d6059c3', 'ld2 { v3.h, v4.h }[#6], x14', 0, ()),
    ('4d6079c3', 'ld4 { v3.h, v4.h, v5.h, v6.h }[#6], x14', 0, ()),
    ('4d6091c3', 'ld2 { v3.s, v4.s }[#3], x14', 0, ()),
    ('4d6085c3', 'ld2 { v3.d, v4.d }[#1], x14', 0, ()),
    ('4d60b1c3', 'ld4 { v3.s, v4.s, v5.s, v6.s }[#3], x14', 0, ()),
    ('4d60a5c3', 'ld4 { v3.d, v4.d, v5.d, v6.d }[#1], x14', 0, ()),
    #ld2r
    ('0d60c1c3', 'ld2r { v3.8b, v4.8b }, x14', 0, ()),
    ('4d60c1c3', 'ld2r { v3.16b, v4.16b }, x14', 0, ()),
    ('0d60c5c3', 'ld2r { v3.4h, v4.4h }, x14', 0, ()),
    ('4d60c5c3', 'ld2r { v3.8h, v4.8h }, x14', 0, ()),
    ('0d60c9c3', 'ld2r { v3.2s, v4.2s }, x14', 0, ()),
    ('4d60c9c3', 'ld2r { v3.4s, v4.4s }, x14', 0, ()),
    ('0d60cdc3', 'ld2r { v3.1d, v4.1d }, x14', 0, ()),
    ('4d60cdc3', 'ld2r { v3.2d, v4.2d }, x14', 0, ()),
    #ld4r 
    ('0d60e1c3', 'ld4r { v3.8b, v4.8b, v5.8b, v6.8b }, x14', 0, ()),
    ('4d60e1c3', 'ld4r { v3.16b, v4.16b, v5.16b, v6.16b }, x14', 0, ()),
    ('0d60e5c3', 'ld4r { v3.4h, v4.4h, v5.4h, v6.4h }, x14', 0, ()),
    ('4d60e5c3', 'ld4r { v3.8h, v4.8h, v5.8h, v6.8h }, x14', 0, ()),
    ('0d60e9c3', 'ld4r { v3.2s, v4.2s, v5.2s, v6.2s }, x14', 0, ()),
    ('4d60e9c3', 'ld4r { v3.4s, v4.4s, v5.4s, v6.4s }, x14', 0, ()),
    ('0d60edc3', 'ld4r { v3.1d, v4.1d, v5.1d, v6.1d }, x14', 0, ()),
    ('4d60edc3', 'ld4r { v3.2d, v4.2d, v5.2d, v6.2d }, x14', 0, ()),
    
    #AdvSIMD Load/store single structure (post-indexed)
    
    #st1 and st3 (register offset)
    ('4e8b19c3', 'st1 { v3.b }[#e], x14, x11', 0, ()),
    ('4e8b39c3', 'st3 { v3.b, v4.b, v5.b }[#e], x14, x11', 0, ()),
    ('4e8b59c3', 'st1 { v3.h }[#6], x14, x11', 0, ()),
    ('4e8b79c3', 'st3 { v3.h, v4.h, v5.h }[#6], x14, x11', 0, ()),
    ('4e8b91c3', 'st1 { v3.s }[#3], x14, x11', 0, ()),
    ('4e8b85c3', 'st1 { v3.d }[#1], x14, x11', 0, ()),
    ('4e8bb1c3', 'st3 { v3.s, v4.s, v5.s }[#3], x14, x11', 0, ()),
    ('4e8ba5c3', 'st3 { v3.d, v4.d, v5.d }[#1], x14, x11', 0, ()),
    #st1 and st3 (immediate offset)
    ('4e9f19c3', 'st1 { v3.b }[#e], x14, #1', 0, ()),
    ('4e9f39c3', 'st3 { v3.b, v4.b, v5.b }[#e], x14, #3', 0, ()),
    ('4e9f59c3', 'st1 { v3.h }[#6], x14, #2', 0, ()),
    ('4e9f79c3', 'st3 { v3.h, v4.h, v5.h }[#6], x14, #6', 0, ()),
    ('4e9f91c3', 'st1 { v3.s }[#3], x14, #4', 0, ()),
    ('4e9f85c3', 'st1 { v3.d }[#1], x14, #8', 0, ()),
    ('4e9fb1c3', 'st3 { v3.s, v4.s, v5.s }[#3], x14, #12', 0, ()),
    ('4e9fa5c3', 'st3 { v3.d, v4.d, v5.d }[#1], x14, #24', 0, ()),
    #st2 and st4 (register offset)
    ('4eab19c3', 'st2 { v3.b, v4.b }[#e], x14, x11', 0, ()),
    ('4eab39c3', 'st4 { v3.b, v4.b, v5.b, v6.b }[#e], x14, x11', 0, ()),
    ('4eab59c3', 'st2 { v3.h, v4.h }[#6], x14, x11', 0, ()),
    ('4eab79c3', 'st4 { v3.h, v4.h, v5.h, v6.h }[#6], x14, x11', 0, ()),
    ('4eab91c3', 'st2 { v3.s, v4.s }[#3], x14, x11', 0, ()),
    ('4eab85c3', 'st2 { v3.d, v4.d }[#1], x14, x11', 0, ()),
    ('4eabb1c3', 'st4 { v3.s, v4.s, v5.s, v6.s }[#3], x14, x11', 0, ()),
    ('4eaba5c3', 'st4 { v3.d, v4.d, v5.d, v6.d }[#1], x14, x11', 0, ()),
    #st2 and st4 (immediate offset)
    ('4ebf19c3', 'st2 { v3.b, v4.b }[#e], x14, #2', 0, ()),
    ('4ebf39c3', 'st4 { v3.b, v4.b, v5.b, v6.b }[#e], x14, #4', 0, ()),
    ('4ebf59c3', 'st2 { v3.h, v4.h }[#6], x14, #4', 0, ()),
    ('4ebf79c3', 'st4 { v3.h, v4.h, v5.h, v6.h }[#6], x14, #8', 0, ()),
    ('4ebf91c3', 'st2 { v3.s, v4.s }[#3], x14, #8', 0, ()),
    ('4ebf85c3', 'st2 { v3.d, v4.d }[#1], x14, #16', 0, ()),
    ('4ebfb1c3', 'st4 { v3.s, v4.s, v5.s, v6.s }[#3], x14, #16', 0, ()),
    ('4ebfa5c3', 'st4 { v3.d, v4.d, v5.d, v6.d }[#1], x14, #32', 0, ()),
    #ld1 and ld3 (register offset)
    ('4ecb19c3', 'ld1 { v3.b }[#e], x14, x11', 0, ()),
    ('4ecb39c3', 'ld3 { v3.b, v4.b, v5.b }[#e], x14, x11', 0, ()),
    ('4ecb59c3', 'ld1 { v3.h }[#6], x14, x11', 0, ()),
    ('4ecb79c3', 'ld3 { v3.h, v4.h, v5.h }[#6], x14, x11', 0, ()),
    ('4ecb91c3', 'ld1 { v3.s }[#3], x14, x11', 0, ()),
    ('4ecb85c3', 'ld1 { v3.d }[#1], x14, x11', 0, ()),
    ('4ecbb1c3', 'ld3 { v3.s, v4.s, v5.s }[#3], x14, x11', 0, ()),
    ('4ecba5c3', 'ld3 { v3.d, v4.d, v5.d }[#1], x14, x11', 0, ()),
    #ld1r (register offset)
    ('0ecbc1c3', 'ld1r { v3.8b }, x14, x11', 0, ()),
    ('4ecbc1c3', 'ld1r { v3.16b }, x14, x11', 0, ()),
    ('0ecbc5c3', 'ld1r { v3.4h }, x14, x11', 0, ()),
    ('4ecbc5c3', 'ld1r { v3.8h }, x14, x11', 0, ()),
    ('0ecbc9c3', 'ld1r { v3.2s }, x14, x11', 0, ()),
    ('4ecbc9c3', 'ld1r { v3.4s }, x14, x11', 0, ()),
    ('0ecbcdc3', 'ld1r { v3.1d }, x14, x11', 0, ()),
    ('4ecbcdc3', 'ld1r { v3.2d }, x14, x11', 0, ()),
    #ld3r (register offset)
    ('0ecbe1c3', 'ld3r { v3.8b, v4.8b, v5.8b }, x14, x11', 0, ()),
    ('4ecbe1c3', 'ld3r { v3.16b, v4.16b, v5.16b }, x14, x11', 0, ()),
    ('0ecbe5c3', 'ld3r { v3.4h, v4.4h, v5.4h }, x14, x11', 0, ()),
    ('4ecbe5c3', 'ld3r { v3.8h, v4.8h, v5.8h }, x14, x11', 0, ()),
    ('0ecbe9c3', 'ld3r { v3.2s, v4.2s, v5.2s }, x14, x11', 0, ()),
    ('4ecbe9c3', 'ld3r { v3.4s, v4.4s, v5.4s }, x14, x11', 0, ()),
    ('0ecbedc3', 'ld3r { v3.1d, v4.1d, v5.1d }, x14, x11', 0, ()),
    ('4ecbedc3', 'ld3r { v3.2d, v4.2d, v5.2d }, x14, x11', 0, ()),
    #ld1 and ld3 (immediate offset)
    ('4ecb19c3', 'ld1 { v3.b }[#e], x14, #1', 0, ()),
    ('4ecb39c3', 'ld3 { v3.b, v4.b, v5.b }[#e], x14, #3', 0, ()),
    ('4ecb59c3', 'ld1 { v3.h }[#6], x14, #2', 0, ()),
    ('4ecb79c3', 'ld3 { v3.h, v4.h, v5.h }[#6], x14, #6', 0, ()),
    ('4ecb91c3', 'ld1 { v3.s }[#3], x14, #4', 0, ()),
    ('4ecb85c3', 'ld1 { v3.d }[#1], x14, #8', 0, ()),
    ('4ecbb1c3', 'ld3 { v3.s, v4.s, v5.s }[#3], x14, #12', 0, ()),
    ('4ecba5c3', 'ld3 { v3.d, v4.d, v5.d }[#1], x14, #24', 0, ()),
    #ld1r (immediate offset)
    ('0edfc1c3', 'ld1r { v3.8b }, x14, #1', 0, ()),
    ('4edfc1c3', 'ld1r { v3.16b }, x14, #1', 0, ()),
    ('0edfc5c3', 'ld1r { v3.4h }, x14, #2', 0, ()),
    ('4edfc5c3', 'ld1r { v3.8h }, x14, #2', 0, ()),
    ('0edfc9c3', 'ld1r { v3.2s }, x14, #4', 0, ()),
    ('4edfc9c3', 'ld1r { v3.4s }, x14, #4', 0, ()),
    ('0edfcdc3', 'ld1r { v3.1d }, x14, #8', 0, ()),
    ('4edfcdc3', 'ld1r { v3.2d }, x14, #8', 0, ()),
    #ld3r (immediate offset)
    ('0edfe1c3', 'ld3r { v3.8b, v4.8b, v5.8b }, x14, #3', 0, ()),
    ('4edfe1c3', 'ld3r { v3.16b, v4.16b, v5.16b }, x14, #3', 0, ()),
    ('0edfe5c3', 'ld3r { v3.4h, v4.4h, v5.4h }, x14, #6', 0, ()),
    ('4edfe5c3', 'ld3r { v3.8h, v4.8h, v5.8h }, x14, #6', 0, ()),
    ('0edfe9c3', 'ld3r { v3.2s, v4.2s, v5.2s }, x14, #12', 0, ()),
    ('4edfe9c3', 'ld3r { v3.4s, v4.4s, v5.4s }, x14, #12', 0, ()),
    ('0edfedc3', 'ld3r { v3.1d, v4.1d, v5.1d }, x14, #24', 0, ()),
    ('4edfedc3', 'ld3r { v3.2d, v4.2d, v5.2d }, x14, #24', 0, ()),
    #ld2 and ld4 (register offset)
    ('4eeb19c3', 'ld2 { v3.b, v4.b }[#e], x14, x11', 0, ()),
    ('4eeb39c3', 'ld4 { v3.b, v4.b, v5.b, v6.b }[#e], x14, x11', 0, ()),
    ('4eeb59c3', 'ld2 { v3.h, v4.h }[#6], x14, x11', 0, ()),
    ('4eeb79c3', 'ld4 { v3.h, v4.h, v5.h, v6.h }[#6], x14, x11', 0, ()),
    ('4eeb91c3', 'ld2 { v3.s, v4.s }[#3], x14, x11', 0, ()),
    ('4eeb85c3', 'ld2 { v3.d, v4.d }[#1], x14, x11', 0, ()),
    ('4eebb1c3', 'ld4 { v3.s, v4.s, v5.s, v6.s }[#3], x14, x11', 0, ()),
    ('4eeba5c3', 'ld4 { v3.d, v4.d, v5.d, v6.d }[#1], x14, x11', 0, ()),
    #ld2r (register offset)
    ('0eebc1c3', 'ld2r { v3.8b, v4.8b }, x14, x11', 0, ()),
    ('4eebc1c3', 'ld2r { v3.16b, v4.16b }, x14, x11', 0, ()),
    ('0eebc5c3', 'ld2r { v3.4h, v4.4h }, x14, x11', 0, ()),
    ('4eebc5c3', 'ld2r { v3.8h, v4.8h }, x14, x11', 0, ()),
    ('0eebc9c3', 'ld2r { v3.2s, v4.2s }, x14, x11', 0, ()),
    ('4eebc9c3', 'ld2r { v3.4s, v4.4s }, x14, x11', 0, ()),
    ('0eebcdc3', 'ld2r { v3.1d, v4.1d }, x14, x11', 0, ()),
    ('4eebcdc3', 'ld2r { v3.2d, v4.2d }, x14, x11', 0, ()),
    #ld4r (register offset)
    ('0eebe1c3', 'ld4r { v3.8b, v4.8b, v5.8b, v6.8b }, x14, x11', 0, ()),
    ('4eebe1c3', 'ld4r { v3.16b, v4.16b, v5.16b, v6.16b }, x14, x11', 0, ()),
    ('0eebe5c3', 'ld4r { v3.4h, v4.4h, v5.4h, v6.4h }, x14, x11', 0, ()),
    ('4eebe5c3', 'ld4r { v3.8h, v4.8h, v5.8h, v6.8h }, x14, x11', 0, ()),
    ('0eebe9c3', 'ld4r { v3.2s, v4.2s, v5.2s, v6.2s }, x14, x11', 0, ()),
    ('4eebe9c3', 'ld4r { v3.4s, v4.4s, v5.4s, v6.4s }, x14, x11', 0, ()),
    ('0eebedc3', 'ld4r { v3.1d, v4.1d, v5.1d, v6.1d }, x14, x11', 0, ()),
    ('4eebedc3', 'ld4r { v3.2d, v4.2d, v5.2d, v6.2d }, x14, x11', 0, ()),
    #ld2 and ld4 (immediate offset)
    ('4eeb19c3', 'ld2 { v3.b, v4.b }[#e], x14, #2', 0, ()),
    ('4eeb39c3', 'ld4 { v3.b, v4.b, v5.b, v6.b }[#e], x14, #4', 0, ()),
    ('4eeb59c3', 'ld2 { v3.h, v4.h }[#6], x14, #4', 0, ()),
    ('4eeb79c3', 'ld4 { v3.h, v4.h, v5.h, v6.h }[#6], x14, #8', 0, ()),
    ('4eeb91c3', 'ld2 { v3.s, v4.s }[#3], x14, #8', 0, ()),
    ('4eeb85c3', 'ld2 { v3.d, v4.d }[#1], x14, #16', 0, ()),
    ('4eebb1c3', 'ld4 { v3.s, v4.s, v5.s, v6.s }[#3], x14, #16', 0, ()),
    ('4eeba5c3', 'ld4 { v3.d, v4.d, v5.d, v6.d }[#1], x14, #32', 0, ()),
    #ld2r (immediate offset)
    ('0effc1c3', 'ld2r { v3.8b, v4.8b }, x14, #2', 0, ()),
    ('4effc1c3', 'ld2r { v3.16b, v4.16b }, x14, #2', 0, ()),
    ('0effc5c3', 'ld2r { v3.4h, v4.4h }, x14, #4', 0, ()),
    ('4effc5c3', 'ld2r { v3.8h, v4.8h }, x14, #4', 0, ()),
    ('0effc9c3', 'ld2r { v3.2s, v4.2s }, x14, #8', 0, ()),
    ('4effc9c3', 'ld2r { v3.4s, v4.4s }, x14, #8', 0, ()),
    ('0effcdc3', 'ld2r { v3.1d, v4.1d }, x14, #16', 0, ()),
    ('4effcdc3', 'ld2r { v3.2d, v4.2d }, x14, #16', 0, ()),
    #ld4r (immediate offset)
    ('0effe1c3', 'ld4r { v3.8b, v4.8b, v5.8b, v6.8b }, x14, #4', 0, ()),
    ('4effe1c3', 'ld4r { v3.16b, v4.16b, v5.16b, v6.16b }, x14, #4', 0, ()),
    ('0effe5c3', 'ld4r { v3.4h, v4.4h, v5.4h, v6.4h }, x14, #8', 0, ()),
    ('4effe5c3', 'ld4r { v3.8h, v4.8h, v5.8h, v6.8h }, x14, #8', 0, ()),
    ('0effe9c3', 'ld4r { v3.2s, v4.2s, v5.2s, v6.2s }, x14, #16', 0, ()),
    ('4effe9c3', 'ld4r { v3.4s, v4.4s, v5.4s, v6.4s }, x14, #16', 0, ()),
    ('0effedc3', 'ld4r { v3.1d, v4.1d, v5.1d, v6.1d }, x14, #32', 0, ()),
    ('4effedc3', 'ld4r { v3.2d, v4.2d, v5.2d, v6.2d }, x14, #32', 0, ()),
#Data processing (register)
    
    #Logical (shifted register)
    
    #every set of 4 tests has the same instruction 4x with a different shift value
    #this results in each result looking identical aside from LSL, LSR, ASR, ROR,
    #(which correspond to shift values of 00, 01, 10, and 11) and mnemonic/opcode
    #32-bit variants
    ('0a0b3dc3', 'and w3, w14, w11{, LSL #f}', 0, ()),
    ('0a4b3dc3', 'and w3, w14, w11{, LSR #f}', 0, ()),
    ('0a8b3dc3', 'and w3, w14, w11{, ASR #f}', 0, ()),
    ('0acb3dc3', 'and w3, w14, w11{, ROR #f}', 0, ()),
    ('0a2b3dc3', 'bic w3, w14, w11{, LSL #f}', 0, ()),
    ('0a6b3dc3', 'bic w3, w14, w11{, LSR #f}', 0, ()),
    ('0aab3dc3', 'bic w3, w14, w11{, ASR #f}', 0, ()),
    ('0aeb3dc3', 'bic w3, w14, w11{, ROR #f}', 0, ()),
    ('2a0b3dc3', 'orr w3, w14, w11{, LSL #f}', 0, ()),
    ('2a4b3dc3', 'orr w3, w14, w11{, LSR #f}', 0, ()),
    ('2a8b3dc3', 'orr w3, w14, w11{, ASR #f}', 0, ()),
    ('2acb3dc3', 'orr w3, w14, w11{, ROR #f}', 0, ()),
    ('2a2b3dc3', 'orn w3, w14, w11{, LSL #f}', 0, ()),
    ('2a6b3dc3', 'orn w3, w14, w11{, LSR #f}', 0, ()),
    ('2aab3dc3', 'orn w3, w14, w11{, ASR #f}', 0, ()),
    ('2aeb3dc3', 'orn w3, w14, w11{, ROR #f}', 0, ()),
    ('4a0b3dc3', 'eor w3, w14, w11{, LSL #f}', 0, ()),
    ('4a4b3dc3', 'eor w3, w14, w11{, LSR #f}', 0, ()),
    ('4a8b3dc3', 'eor w3, w14, w11{, ASR #f}', 0, ()),
    ('4acb3dc3', 'eor w3, w14, w11{, ROR #f}', 0, ()),
    ('4a2b3dc3', 'eon w3, w14, w11{, LSL #f}', 0, ()),
    ('4a6b3dc3', 'eon w3, w14, w11{, LSR #f}', 0, ()),
    ('4aab3dc3', 'eon w3, w14, w11{, ASR #f}', 0, ()),
    ('4aeb3dc3', 'eon w3, w14, w11{, ROR #f}', 0, ()),
    ('6a0b3dc3', 'ands w3, w14, w11{, LSL #f}', 0, ()),
    ('6a4b3dc3', 'ands w3, w14, w11{, LSR #f}', 0, ()),
    ('6a8b3dc3', 'ands w3, w14, w11{, ASR #f}', 0, ()),
    ('6acb3dc3', 'ands w3, w14, w11{, ROR #f}', 0, ()),
    ('6a2b3dc3', 'bics w3, w14, w11{, LSL #f}', 0, ()),
    ('6a6b3dc3', 'bics w3, w14, w11{, LSR #f}', 0, ()),
    ('6aab3dc3', 'bics w3, w14, w11{, ASR #f}', 0, ()),
    ('6aeb3dc3', 'bics w3, w14, w11{, ROR #f}', 0, ()),
    #64-bit variants of the same instructions
    ('8a0b3dc3', 'and x3, x14, x11{, LSL #f}', 0, ()),
    ('8a4b3dc3', 'and x3, x14, x11{, LSR #f}', 0, ()),
    ('8a8b3dc3', 'and x3, x14, x11{, ASR #f}', 0, ()),
    ('8acb3dc3', 'and x3, x14, x11{, ROR #f}', 0, ()),
    ('8a2b3dc3', 'bic x3, x14, x11{, LSL #f}', 0, ()),
    ('8a6b3dc3', 'bic x3, x14, x11{, LSR #f}', 0, ()),
    ('8aab3dc3', 'bic x3, x14, x11{, ASR #f}', 0, ()),
    ('8aeb3dc3', 'bic x3, x14, x11{, ROR #f}', 0, ()),
    ('aa0b3dc3', 'orr x3, x14, x11{, LSL #f}', 0, ()),
    ('aa4b3dc3', 'orr x3, x14, x11{, LSR #f}', 0, ()),
    ('aa8b3dc3', 'orr x3, x14, x11{, ASR #f}', 0, ()),
    ('aacb3dc3', 'orr x3, x14, x11{, ROR #f}', 0, ()),
    ('aa2b3dc3', 'orn x3, x14, x11{, LSL #f}', 0, ()),
    ('aa6b3dc3', 'orn x3, x14, x11{, LSR #f}', 0, ()),
    ('aaab3dc3', 'orn x3, x14, x11{, ASR #f}', 0, ()),
    ('aaeb3dc3', 'orn x3, x14, x11{, ROR #f}', 0, ()),
    ('ca0b3dc3', 'eor x3, x14, x11{, LSL #f}', 0, ()),
    ('ca4b3dc3', 'eor x3, x14, x11{, LSR #f}', 0, ()),
    ('ca8b3dc3', 'eor x3, x14, x11{, ASR #f}', 0, ()),
    ('cacb3dc3', 'eor x3, x14, x11{, ROR #f}', 0, ()),
    ('ca2b3dc3', 'eon x3, x14, x11{, LSL #f}', 0, ()),
    ('ca6b3dc3', 'eon x3, x14, x11{, LSR #f}', 0, ()),
    ('caab3dc3', 'eon x3, x14, x11{, ASR #f}', 0, ()),
    ('caeb3dc3', 'eon x3, x14, x11{, ROR #f}', 0, ()),
    ('ea0b3dc3', 'ands x3, x14, x11{, LSL #f}', 0, ()),
    ('ea4b3dc3', 'ands x3, x14, x11{, LSR #f}', 0, ()),
    ('ea8b3dc3', 'ands x3, x14, x11{, ASR #f}', 0, ()),
    ('eacb3dc3', 'ands x3, x14, x11{, ROR #f}', 0, ()),
    ('ea2b3dc3', 'bics x3, x14, x11{, LSL #f}', 0, ()),
    ('ea6b3dc3', 'bics x3, x14, x11{, LSR #f}', 0, ()),
    ('eaab3dc3', 'bics x3, x14, x11{, ASR #f}', 0, ()),
    ('eaeb3dc3', 'bics x3, x14, x11{, ROR #f}', 0, ()),
    
    #Add/sub (shifted register)
    
    #similar to logical (shifted register), these are sets of three tests for the
    #same instruction, where the only different thing is the shift value.
    #the main difference is that logical (shifted register) didn't have shift = 11 as reserved
    ('0b0b3dc3', 'add w3, w14, w11{, LSL #f}', 0, ()),
    ('0b4b3dc3', 'add w3, w14, w11{, LSR #f}', 0, ()),
    ('0b8b3dc3', 'add w3, w14, w11{, ASR #f}', 0, ()),
    ('2b0b3dc3', 'adds w3, w14, w11{, LSL #f}', 0, ()),
    ('2b4b3dc3', 'adds w3, w14, w11{, LSR #f}', 0, ()),
    ('2b8b3dc3', 'adds w3, w14, w11{, ASR #f}', 0, ()),
    ('4b0b3dc3', 'sub w3, w14, w11{, LSL #f}', 0, ()),
    ('4b4b3dc3', 'sub w3, w14, w11{, LSR #f}', 0, ()),
    ('4b8b3dc3', 'sub w3, w14, w11{, ASR #f}', 0, ()),
    ('6b0b3dc3', 'subs w3, w14, w11{, LSL #f}', 0, ()),
    ('6b4b3dc3', 'subs w3, w14, w11{, LSR #f}', 0, ()),
    ('6b8b3dc3', 'subs w3, w14, w11{, ASR #f}', 0, ()),
    #64-bit variants of the same instructions
    ('8b0b3dc3', 'add x3, x14, x11{, LSL #f}', 0, ()),
    ('8b4b3dc3', 'add x3, x14, x11{, LSR #f}', 0, ()),
    ('8b8b3dc3', 'add x3, x14, x11{, ASR #f}', 0, ()),
    ('ab0b3dc3', 'adds x3, x14, x11{, LSL #f}', 0, ()),
    ('ab4b3dc3', 'adds x3, x14, x11{, LSR #f}', 0, ()),
    ('ab8b3dc3', 'adds x3, x14, x11{, ASR #f}', 0, ()),
    ('cb0b3dc3', 'sub x3, x14, x11{, LSL #f}', 0, ()),
    ('cb4b3dc3', 'sub x3, x14, x11{, LSR #f}', 0, ()),
    ('cb8b3dc3', 'sub x3, x14, x11{, ASR #f}', 0, ()),
    ('eb0b3dc3', 'subs x3, x14, x11{, LSL #f}', 0, ()),
    ('eb4b3dc3', 'subs x3, x14, x11{, LSR #f}', 0, ()),
    ('eb8b3dc3', 'subs x3, x14, x11{, ASR #f}', 0, ()),
    
    #Add/subtract (extended register)
    
    #this time, there are 8 tests per instruction, each having a different extend
    #64-bit variants sometimes have the 11 register as a w. only x when option = x11
    ('0b2b0dc3', 'add w3, w14, w11{, UXTB {#3}}', 0, ()),
    ('0b2b2dc3', 'add w3, w14, w11{, UXTH {#3}}', 0, ()),
    ('0b2b4dc3', 'add w3, w14, w11{, LSL|USTW {#3}}', 0, ()),
    ('0b2b6dc3', 'add w3, w14, w11{, UXTX {#3}}', 0, ()),
    ('0b2b8dc3', 'add w3, w14, w11{, SXTB {#3}}', 0, ()),
    ('0b2badc3', 'add w3, w14, w11{, SXTH {#3}}', 0, ()),
    ('0b2bcdc3', 'add w3, w14, w11{, SXTW {#3}}', 0, ()),
    ('0b2bedc3', 'add w3, w14, w11{, SXTX {#3}}', 0, ()),
    ('2b2b0dc3', 'adds w3, w14, w11{, UXTB {#3}}', 0, ()),
    ('2b2b2dc3', 'adds w3, w14, w11{, UXTH {#3}}', 0, ()),
    ('2b2b4dc3', 'adds w3, w14, w11{, LSL|USTW {#3}}', 0, ()),
    ('2b2b6dc3', 'adds w3, w14, w11{, UXTX {#3}}', 0, ()),
    ('2b2b8dc3', 'adds w3, w14, w11{, SXTB {#3}}', 0, ()),
    ('2b2badc3', 'adds w3, w14, w11{, SXTH {#3}}', 0, ()),
    ('2b2bcdc3', 'adds w3, w14, w11{, SXTW {#3}}', 0, ()),
    ('2b2bedc3', 'adds w3, w14, w11{, SXTX {#3}}', 0, ()),
    ('4b2b0dc3', 'sub w3, w14, w11{, UXTB {#3}}', 0, ()),
    ('4b2b2dc3', 'sub w3, w14, w11{, UXTH {#3}}', 0, ()),
    ('4b2b4dc3', 'sub w3, w14, w11{, LSL|USTW {#3}}', 0, ()),
    ('4b2b6dc3', 'sub w3, w14, w11{, UXTX {#3}}', 0, ()),
    ('4b2b8dc3', 'sub w3, w14, w11{, SXTB {#3}}', 0, ()),
    ('4b2badc3', 'sub w3, w14, w11{, SXTH {#3}}', 0, ()),
    ('4b2bcdc3', 'sub w3, w14, w11{, SXTW {#3}}', 0, ()),
    ('4b2bedc3', 'sub w3, w14, w11{, SXTX {#3}}', 0, ()),
    ('6b2b0dc3', 'subs w3, w14, w11{, UXTB {#3}}', 0, ()),
    ('6b2b2dc3', 'subs w3, w14, w11{, UXTH {#3}}', 0, ()),
    ('6b2b4dc3', 'subs w3, w14, w11{, LSL|USTW {#3}}', 0, ()),
    ('6b2b6dc3', 'subs w3, w14, w11{, UXTX {#3}}', 0, ()),
    ('6b2b8dc3', 'subs w3, w14, w11{, SXTB {#3}}', 0, ()),
    ('6b2badc3', 'subs w3, w14, w11{, SXTH {#3}}', 0, ()),
    ('6b2bcdc3', 'subs w3, w14, w11{, SXTW {#3}}', 0, ()),
    ('6b2bedc3', 'subs w3, w14, w11{, SXTX {#3}}', 0, ()),
    #64-bit variants of the same instructions
    ('8b2b0dc3', 'add x3, x14, w11{, UXTB {#3}}', 0, ()),
    ('8b2b2dc3', 'add x3, x14, w11{, UXTH {#3}}', 0, ()),
    ('8b2b4dc3', 'add x3, x14, w11{, LSL|USTW {#3}}', 0, ()),
    ('8b2b6dc3', 'add x3, x14, x11{, UXTX {#3}}', 0, ()),
    ('8b2b8dc3', 'add x3, x14, w11{, SXTB {#3}}', 0, ()),
    ('8b2badc3', 'add x3, x14, w11{, SXTH {#3}}', 0, ()),
    ('8b2bcdc3', 'add x3, x14, w11{, SXTW {#3}}', 0, ()),
    ('8b2bedc3', 'add x3, x14, x11{, SXTX {#3}}', 0, ()),
    ('ab2b0dc3', 'adds x3, x14, w11{, UXTB {#3}}', 0, ()),
    ('ab2b2dc3', 'adds x3, x14, w11{, UXTH {#3}}', 0, ()),
    ('ab2b4dc3', 'adds x3, x14, w11{, LSL|USTW {#3}}', 0, ()),
    ('ab2b6dc3', 'adds x3, x14, x11{, UXTX {#3}}', 0, ()),
    ('ab2b8dc3', 'adds x3, x14, w11{, SXTB {#3}}', 0, ()),
    ('ab2badc3', 'adds x3, x14, w11{, SXTH {#3}}', 0, ()),
    ('ab2bcdc3', 'adds x3, x14, w11{, SXTW {#3}}', 0, ()),
    ('ab2bedc3', 'adds x3, x14, x11{, SXTX {#3}}', 0, ()),
    ('cb2b0dc3', 'sub x3, x14, w11{, UXTB {#3}}', 0, ()),
    ('cb2b2dc3', 'sub x3, x14, w11{, UXTH {#3}}', 0, ()),
    ('cb2b4dc3', 'sub x3, x14, w11{, LSL|USTW {#3}}', 0, ()),
    ('cb2b6dc3', 'sub x3, x14, x11{, UXTX {#3}}', 0, ()),
    ('cb2b8dc3', 'sub x3, x14, w11{, SXTB {#3}}', 0, ()),
    ('cb2badc3', 'sub x3, x14, w11{, SXTH {#3}}', 0, ()),
    ('cb2bcdc3', 'sub x3, x14, w11{, SXTW {#3}}', 0, ()),
    ('cb2bedc3', 'sub x3, x14, x11{, SXTX {#3}}', 0, ()),
    ('eb2b0dc3', 'subs x3, x14, w11{, UXTB {#3}}', 0, ()),
    ('eb2b2dc3', 'subs x3, x14, w11{, UXTH {#3}}', 0, ()),
    ('eb2b4dc3', 'subs x3, x14, w11{, LSL|USTW {#3}}', 0, ()),
    ('eb2b6dc3', 'subs x3, x14, x11{, UXTX {#3}}', 0, ()),
    ('eb2b8dc3', 'subs x3, x14, w11{, SXTB {#3}}', 0, ()),
    ('eb2badc3', 'subs x3, x14, w11{, SXTH {#3}}', 0, ()),
    ('eb2bcdc3', 'subs x3, x14, w11{, SXTW {#3}}', 0, ()),
    ('eb2bedc3', 'subs x3, x14, x11{, SXTX {#3}}', 0, ()),
    
    #Add/subtract (with carry)
    
    ('1a0b01c3', 'adc w3, w14, w11', 0, ()),
    ('3a0b01c3', 'adcs w3, w14, w11', 0, ()),
    ('5a0b01c3', 'sbc w3, w14, w11', 0, ()),
    ('7a0b01c3', 'sbcs w3, w14, w11', 0, ()),
    ('9a0b01c3', 'adc x3, x14, x11', 0, ()),
    ('ba0b01c3', 'adcs x3, x14, x11', 0, ()),
    ('da0b01c3', 'sbc x3, x14, x11', 0, ()),
    ('fa0b01c3', 'sbcs x3, x14, x11', 0, ()),
    
    #Conditional compare (register)
    
    ('3a4b01cf', 'ccmn w14, w11, #f, EQ', 0, ()),
    ('7a4b11ce', 'ccmp w14, w11, #e, NE', 0, ()),
    ('ba4b21cd', 'ccmn x14, x11, #d, CS', 0, ()),
    ('fa4b31cc', 'ccmp x14, x11, #c, CC', 0, ()),
    ('3a4b41cb', 'ccmn w14, w11, #b, MI', 0, ()),
    ('7a4b51ca', 'ccmp w14, w11, #a, PL', 0, ()),
    ('ba4b61c9', 'ccmn x14, x11, #9, VS', 0, ()),
    ('fa4b71c8', 'ccmp x14, x11, #8, VC', 0, ()),
    ('3a4b81c7', 'ccmn w14, w11, #7, HI', 0, ()),
    ('7a4b91c6', 'ccmp w14, w11, #6, LS', 0, ()),
    ('ba4ba1c5', 'ccmn x14, x11, #5, GE', 0, ()),
    ('fa4bb1c4', 'ccmp x14, x11, #4, LT', 0, ()),
    ('3a4bc1c3', 'ccmn w14, w11, #3, GT', 0, ()),
    ('7a4bd1c2', 'ccmp w14, w11, #2, LE', 0, ()),
    ('ba4be1c1', 'ccmn x14, x11, #1, AL', 0, ()),
    
    #Conditional compare (immediate)
    
    ('3a4b09cb', 'ccmn w14, #11, #b, EQ', 0, ()),
    ('7a4b19ca', 'ccmp w14, #11, #a, NE', 0, ()),
    ('ba4b29c9', 'ccmn x14, #11, #9, CS', 0, ()),
    ('fa4b39c8', 'ccmp x14, #11, #8, CC', 0, ()),
    ('3a4b49cb', 'ccmn w14, #11, #b, MI', 0, ()),
    ('7a4b59ca', 'ccmp w14, #11, #a, PL', 0, ()),
    ('ba4b69c9', 'ccmn x14, #11, #9, VS', 0, ()),
    ('fa4b79c8', 'ccmp x14, #11, #8, VC', 0, ()),
    ('3a4b89cb', 'ccmn w14, #11, #b, HI', 0, ()),
    ('7a4b99ca', 'ccmp w14, #11, #a, LS', 0, ()),
    ('ba4ba9c9', 'ccmn x14, #11, #9, GE', 0, ()),
    ('fa4bb9c8', 'ccmp x14, #11, #8, LT', 0, ()),
    ('3a4bc9cb', 'ccmn w14, #11, #b, GT', 0, ()),
    ('7a4bd9ca', 'ccmp w14, #11, #a, LE', 0, ()),
    ('ba4be9c9', 'ccmn x14, #11, #9, AL', 0, ()),
    
    #Conditional select
    
    ('1a8b01c3', 'csel w3, w14, w11, EQ', 0, ()),
    ('1a8b15c3', 'csinc w3, w14, w11, NE', 0, ()),
    ('5a8b21c3', 'csinv w3, w14, w11, CS', 0, ()),
    ('5a8b35c3', 'csneg w3, w14, w11, CC', 0, ()),
    ('9a8b41c3', 'csel x3, x14, x11, MI', 0, ()),
    ('9a8b55c3', 'csinc x3, x14, x11, PL', 0, ()),
    ('da8b61c3', 'csinv x3, x14, x11, VS', 0, ()),
    ('da8b75c3', 'csneg x3, x14, x11, VC', 0, ()),
    ('1a8b81c3', 'csel w3, w14, w11, HI', 0, ()),
    ('1a8b95c3', 'csinc w3, w14, w11, LS', 0, ()),
    ('5a8ba1c3', 'csinv w3, w14, w11, GE', 0, ()),
    ('5a8bb5c3', 'csneg w3, w14, w11, LT', 0, ()),
    ('9a8bc1c3', 'csel x3, x14, x11, GT', 0, ()),
    ('9a8bd5c3', 'csinc x3, x14, x11, LE', 0, ()),
    ('da8be1c3', 'csinv x3, x14, x11, AL', 0, ()),
    ('da8b05c3', 'csneg x3, x14, x11, EQ', 0, ()),
    
    #Data processing (3 source)
    
    ('1b0b25c3', 'madd w3, w14, w11, w9', 0, ()),
    ('1b0ba5c3', 'msub w3, w14, w11, w9', 0, ()),
    ('9b0b25c3', 'madd x3, x14, x11, x9', 0, ()),
    ('9b0ba5c3', 'msub x3, x14, x11, x9', 0, ()),
    ('9b2b25c3', 'smaddl x3, w14, w11, x9', 0, ()),
    ('9b2ba5c3', 'smsubl x3, w14, w11, x9', 0, ()),
    ('9b4b25c3', 'smulh x3, x14, x11', 0, ()),
    ('9bab25c3', 'umaddl x3, w14, w11, x9', 0, ()),
    ('9baba5c3', 'umsubl x3, w14, w11, x9', 0, ()),
    ('9bdb25c3', 'umulh x3, x14, x11', 0, ()),
    
    #Data processing (2 source)
    
    ('1acb09c3', 'udiv w3, w14, w11', 0, ()),
    ('1acb0dc3', 'sdiv w3, w14, w11', 0, ()),
    ('1acb21c3', 'lslv w3, w14, w11', 0, ()),
    ('1acb25c3', 'lsrv w3, w14, w11', 0, ()),
    ('1acb29c3', 'asrv w3, w14, w11', 0, ()),
    ('1acb2dc3', 'rorv w3, w14, w11', 0, ()),
    ('1acb41c3', 'crc32b w3, w14, w11', 0, ()),
    ('1acb45c3', 'crc32h w3, w14, w11', 0, ()),
    ('1acb49c3', 'crc32w w3, w14, w11', 0, ()),
    ('1acb51c3', 'crc32cb w3, w14, w11', 0, ()),
    ('1acb55c3', 'crc32ch w3, w14, w11', 0, ()),
    ('1acb59c3', 'crc32cw w3, w14, w11', 0, ()),
    ('9acb09c3', 'udiv x3, x14, x11', 0, ()),
    ('9acb0dc3', 'sdiv x3, x14, x11', 0, ()),
    ('9acb21c3', 'lslv x3, x14, x11', 0, ()),
    ('9acb25c3', 'lsrv x3, x14, x11', 0, ()),
    ('9acb29c3', 'asrv x3, x14, x11', 0, ()),
    ('9acb2dc3', 'rorv x3, x14, x11', 0, ()),
    ('9acb4dc3', 'crc32x w3, w14, w11', 0, ()),
    ('9acb5dc3', 'crc32cx w3, w14, w11', 0, ()),

    #Data processing (1 source)

    ('5ac001c3', 'rbit w3, w14', 0, ()),
    ('5ac005c3', 'rev16 w3, w14', 0, ()),
    ('5ac009c3', 'rev w3, w14', 0, ()),
    ('5ac011c3', 'clz w3, w14', 0, ()),
    ('5ac015c3', 'cls w3, w14', 0, ()),
    ('dac001c3', 'rbit x3, x14', 0, ()),
    ('dac005c3', 'rev16 x3, x14', 0, ()),
    ('dac009c3', 'rev32 x3, x14', 0, ()),
    ('dac00dc3', 'rev x3, x14', 0, ()),
    ('dac011c3', 'clz x3, x14', 0, ()),
    ('dac015c3', 'cls x3, x14', 0, ()),

     
#Data processing (SIMD and floating point)

    #Floating-point<->fixed-point conversions

    ('1e02a9c3', 'scvtf s3, w14, #22', 0, ()),
    ('1e03a9c3', 'ucvtf s3, w14, #22', 0, ()),
    ('1e18a9c3', 'fcvtzs w14, s3, #22', 0, ()),
    ('1e19a9c3', 'fcvtzu w14, s3, #22', 0, ()),
    ('1e42a9c3', 'scvtf d3, w14, #22', 0, ()),
    ('1e43a9c3', 'ucvtf d3, w14, #22', 0, ()),
    ('1e58a9c3', 'fcvtzs w14, d3, #22', 0, ()),
    ('1e59a9c3', 'fcvtzu w14, d3, #22', 0, ()),
    ('9e02a9c3', 'scvtf s3, x14, #22', 0, ()),
    ('9e03a9c3', 'ucvtf s3, x14, #22', 0, ()),
    ('9e18a9c3', 'fcvtzs x14, s3, #22', 0, ()),
    ('9e19a9c3', 'fcvtzu x14, s3, #22', 0, ()),
    ('9e42a9c3', 'scvtf d3, x14, #22', 0, ()),
    ('9e43a9c3', 'ucvtf d3, x14, #22', 0, ()),
    ('9e58a9c3', 'fcvtzs x14, d3, #22', 0, ()),
    ('9e59a9c3', 'fcvtzu x14, d3, #22', 0, ()),

    #Floating-point conditional compare

    ('1e2b05cf', 'fccmp s14, s11, #f, EQ', 0, ()),
    ('1e2b15de', 'fccmpe s14, s11, #e, NE', 0, ()),
    ('1e6b25cd', 'fccmp d14, d11, #d, CS', 0, ()),
    ('1e6b35dc', 'fccmpe d14, d11, #c, CC', 0, ()),
    ('1e2b45cf', 'fccmp s14, s11, #f, MI', 0, ()),
    ('1e2b55de', 'fccmpe s14, s11, #e, PL', 0, ()),
    ('1e6b65cd', 'fccmp d14, d11, #d, VS', 0, ()),
    ('1e6b75dc', 'fccmpe d14, d11, #c, VC', 0, ()),
    ('1e2b85cf', 'fccmp s14, s11, #f, HI', 0, ()),
    ('1e2b95de', 'fccmpe s14, s11, #e, LS', 0, ()),
    ('1e6ba5cd', 'fccmp d14, d11, #d, GE', 0, ()),
    ('1e6bb5dc', 'fccmpe d14, d11, #c, LT', 0, ()),
    ('1e2bc5cf', 'fccmp s14, s11, #f, GT', 0, ()),
    ('1e2bd5de', 'fccmpe s14, s11, #e, LE', 0, ()),
    ('1e6be5cd', 'fccmp d14, d11, #d, AL', 0, ()),

    #Floating-point data-processing (2 source)

    ('1e2b09c3', 'fmul s3, s14, s11', 0, ()),
    ('1e2b19c3', 'fdiv s3, s14, s11', 0, ()),
    ('1e2b29c3', 'fadd s3, s14, s11', 0, ()),
    ('1e2b39c3', 'fsub s3, s14, s11', 0, ()),
    ('1e2b49c3', 'fmax s3, s14, s11', 0, ()),
    ('1e2b59c3', 'fmin s3, s14, s11', 0, ()),
    ('1e2b69c3', 'fmaxnm s3, s14, s11', 0, ()),
    ('1e2b79c3', 'fminnm s3, s14, s11', 0, ()),
    ('1e2b89c3', 'fnmul s3, s14, s11', 0, ()),
    ('1e6b09c3', 'fmul d3, d14, d11', 0, ()),
    ('1e6b19c3', 'fdiv d3, d14, d11', 0, ()),
    ('1e6b29c3', 'fadd d3, d14, d11', 0, ()),
    ('1e6b39c3', 'fsub d3, d14, d11', 0, ()),
    ('1e6b49c3', 'fmax d3, d14, d11', 0, ()),
    ('1e6b59c3', 'fmin d3, d14, d11', 0, ()),
    ('1e6b69c3', 'fmaxnm d3, d14, d11', 0, ()),
    ('1e6b79c3', 'fminnm d3, d14, d11', 0, ()),
    ('1e6b89c3', 'fnmul d3, d14, d11', 0, ()),

    #Floating-point conditional select

    ('1e2b0dc3', 'fcsel s3, s14, s11, EQ', 0, ()),
    ('1e6b1dc3', 'fcsel d3, d14, d11, NE', 0, ()),
    ('1e2b2dc3', 'fcsel s3, s14, s11, CS', 0, ()),
    ('1e6b3dc3', 'fcsel d3, d14, d11, CC', 0, ()),
    ('1e2b4dc3', 'fcsel s3, s14, s11, MI', 0, ()),
    ('1e6b5dc3', 'fcsel d3, d14, d11, PL', 0, ()),
    ('1e2b6dc3', 'fcsel s3, s14, s11, VS', 0, ()),
    ('1e6b7dc3', 'fcsel d3, d14, d11, VC', 0, ()),
    ('1e2b8dc3', 'fcsel s3, s14, s11, HI', 0, ()),
    ('1e6b9dc3', 'fcsel d3, d14, d11, LS', 0, ()),
    ('1e2badc3', 'fcsel s3, s14, s11, GE', 0, ()),
    ('1e6bbdc3', 'fcsel d3, d14, d11, LT', 0, ()),
    ('1e2bcdc3', 'fcsel s3, s14, s11, GT', 0, ()),
    ('1e6bddc3', 'fcsel d3, d14, d11, LE', 0, ()),
    ('1e2bedc3', 'fcsel s3, s14, s11, AL', 0, ()),

    #Floating-point immediate

    ('1e267003', 'fmov s3, #33', 0, ()),
    ('1e667003', 'fmov d3, #33', 0, ()),

    #Floating-point compare

    ('1e2b21c0', 'fcmp s14, s11', 0, ()),
    ('1e2b21c8', 'fcmp s14, #0.0', 0, ()),
    ('1e2b21d0', 'fcmpe s14, s11', 0, ()),
    ('1e2b21d8', 'fcmpe s14, #0.0', 0, ()),
    ('1e6b21c0', 'fcmp d14, d11', 0, ()),
    ('1e6b21c8', 'fcmp d14, #0.0', 0, ()),
    ('1e6b21d0', 'fcmpe d14, d11', 0, ()),
    ('1e6b21d8', 'fcmpe d14, #0.0', 0, ()),

    #Floating-point data-processing (1 source)

    ('1e2041c3', 'fmov s3, s14', 0, ()),
    ('1e20c1c3', 'fabs s3, s14', 0, ()),
    ('1e2141c3', 'fneg s3, s14', 0, ()),
    ('1e21c1c3', 'fsqrt s3, s14', 0, ()),
    ('1e22c1c3', 'fcvt d3, s14', 0, ()),
    ('1e23c1c3', 'fcvt h3, s14', 0, ()),
    ('1e2441c3', 'frintn s3, s14', 0, ()),
    ('1e24c1c3', 'frintp s3, s14', 0, ()),
    ('1e2541c3', 'frintm s3, s14', 0, ()),
    ('1e25c1c3', 'frintz s3, s14', 0, ()),
    ('1e2641c3', 'frinta s3, s14', 0, ()),
    ('1e2741c3', 'frintx s3, s14', 0, ()),
    ('1e27c1c3', 'frinti s3, s14', 0, ()),
    ('1e6041c3', 'fmov d3, d14', 0, ()),
    ('1e60c1c3', 'fabs d3, d14', 0, ()),
    ('1e6141c3', 'fneg d3, d14', 0, ()),
    ('1e61c1c3', 'fsqrt d3, d14', 0, ()),
    ('1e62c1c3', 'fcvt s3, d14', 0, ()),
    ('1e63c1c3', 'fcvt h3, d14', 0, ()),
    ('1e6441c3', 'frintn d3, d14', 0, ()),
    ('1e64c1c3', 'frintp d3, d14', 0, ()),
    ('1e6541c3', 'frintm d3, d14', 0, ()),
    ('1e65c1c3', 'frintz d3, d14', 0, ()),
    ('1e6641c3', 'frinta d3, d14', 0, ()),
    ('1e6741c3', 'frintx d3, d14', 0, ()),
    ('1e67c1c3', 'frinti d3, d14', 0, ()),
    ('1ee241c3', 'fcvt s3, h14', 0, ()),
    ('1ee2c1c3', 'fcvt d3, h14', 0, ()),

    #Floating-point<->integer conversions

    ('1e2001c3', 'fcvtns w3, s14', 0, ()),
    ('1e2101c3', 'fcvtnu w3, s14', 0, ()),
    ('1e2201c3', 'scvtf s3, w14', 0, ()),
    ('1e2301c3', 'ucvtf s3, w14', 0, ()),
    
    ('1e2401c3', 'fcvtas w3, s14', 0, ()),
    ('1e2501c3', 'fcvtau w3, s14', 0, ()),
    ('1e2601c3', 'fmov w3, s14', 0, ()),
    ('1e2701c3', 'fmov s3, w14', 0, ()),
    ('1e2801c3', 'fcvtps w3, s14', 0, ()),
    ('1e2901c3', 'fcvtpu w3, s14', 0, ()),
     
    ('1e3001c3', 'fcvtms w3, s14', 0, ()),
    ('1e3101c3', 'fcvtmu w3, s14', 0, ()),
    ('1e3801c3', 'fcvtzs w3, s14', 0, ()),
    ('1e3901c3', 'fcvtzu w3, s14', 0, ()),
     
    ('1e6001c3', 'fcvtns w3, d14', 0, ()),
    ('1e6101c3', 'fcvtnu w3, d14', 0, ()),
    ('1e6201c3', 'scvtf d3, w14', 0, ()),
    ('1e6301c3', 'ucvtf d3, w14', 0, ()),
    ('1e6401c3', 'fcvtas w3, d14', 0, ()),
    ('1e6501c3', 'fcvtau w3, d14', 0, ()),
    ('1e6801c3', 'fcvtps w3, d14', 0, ()),
    ('1e6901c3', 'fcvtpu w3, d14', 0, ()),
     
    ('1e7001c3', 'fcvtms w3, d14', 0, ()),
    ('1e7101c3', 'fcvtmu w3, d14', 0, ()),
    ('1e7801c3', 'fcvtzs w3, d14', 0, ()),
    ('1e7901c3', 'fcvtzu w3, d14', 0, ()),
     
    ('9e2001c3', 'fcvtns x3, s14', 0, ()),
    ('9e2101c3', 'fcvtnu x3, s14', 0, ()),
    ('9e2201c3', 'scvtf s3, x14', 0, ()),
    ('9e2301c3', 'ucvtf s3, x14', 0, ()),
    ('9e2401c3', 'fcvtas x3, s14', 0, ()),
    ('9e2501c3', 'fcvtau x3, s14', 0, ()),
    ('9e2801c3', 'fcvtps x3, s14', 0, ()),
    ('9e2901c3', 'fcvtpu x3, s14', 0, ()),
     
    ('9e3001c3', 'fcvtms x3, s14', 0, ()),
    ('9e3101c3', 'fcvtmu x3, s14', 0, ()),
    ('9e3801c3', 'fcvtzs x3, s14', 0, ()),
    ('9e3901c3', 'fcvtzu x3, s14', 0, ()),
     
    ('9e6001c3', 'fcvtns x3, d14', 0, ()),
    ('9e6101c3', 'fcvtnu x3, d14', 0, ()),
    ('9e6201c3', 'scvtf d3, x14', 0, ()),
    ('9e6301c3', 'ucvtf d3, x14', 0, ()),
    ('9e6401c3', 'fcvtas x3, d14', 0, ()),
    ('9e6501c3', 'fcvtau x3, d14', 0, ()),
    ('9e6601c3', 'fmov x3, d14', 0, ()),
    ('9e6701c3', 'fmov d3, x14', 0, ()),
    ('9e6801c3', 'fcvtps x3, d14', 0, ()),
    ('9e6901c3', 'fcvtpu x3, d14', 0, ()),

    ('9e7001c3', 'fcvtms x3, d14', 0, ()),
    ('9e7101c3', 'fcvtmu x3, d14', 0, ()),
    ('9e7801c3', 'fcvtzs x3, d14', 0, ()),
    ('9e7901c3', 'fcvtzu x3, d14', 0, ()),

    ('9eae01c3', 'fmov x3, v14.d[1]', 0, ()),
    ('9eaf01c3', 'fmov v3.d[1], x14', 0, ()),

    #Floating-point data-processing (3 source)

    ('1f0b25c3', 'fmadd s3, s14, s11, s9', 0, ()),
    ('1f0ba5c3', 'fmsub s3, s14, s11, s9', 0, ()),
    ('1f2b25c3', 'fnmadd s3, s14, s11, s9', 0, ()),
    ('1f2ba5c3', 'fnmsub s3, s14, s11, s9', 0, ()),
    ('1f4b25c3', 'fmadd d3, d14, d11, d9', 0, ()),
    ('1f4ba5c3', 'fmsub d3, d14, d11, d9', 0, ()),
    ('1f6b25c3', 'fnmadd d3, d14, d11, d9', 0, ()),
    ('1f6ba5c3', 'fnmsub d3, d14, d11, d9', 0, ()),

    #AdvSIMD three same

    #shadd
    ('0e2b05c3', 'shadd v3.8b, v14.8b, v11.8b', 0, ()),
    ('4e2b05c3', 'shadd v3.16b, v14.16b, v11.16b', 0, ()),
    ('0e6b05c3', 'shadd v3.4h, v14.4h, v11.4h', 0, ()),
    ('4e6b05c3', 'shadd v3.8h, v14.8h, v11.8h', 0, ()),
    ('0eab05c3', 'shadd v3.2s, v14.2s, v11.2s', 0, ()),
    ('4eab05c3', 'shadd v3.4s, v14.4s, v11.4s', 0, ()),
    #sqadd
    ('0e2b0dc3', 'sqadd v3.8b, v14.8b, v11.8b', 0, ()),
    ('4e2b0dc3', 'sqadd v3.16b, v14.16b, v11.16b', 0, ()),
    ('0e6b0dc3', 'sqadd v3.4h, v14.4h, v11.4h', 0, ()),
    ('4e6b0dc3', 'sqadd v3.8h, v14.8h, v11.8h', 0, ()),
    ('0eab0dc3', 'sqadd v3.2s, v14.2s, v11.2s', 0, ()),
    ('4eab0dc3', 'sqadd v3.4s, v14.4s, v11.4s', 0, ()),
    ('4eeb0dc3', 'sqadd v3.2d, v14.2d, v11.2d', 0, ()),
    #srhadd
    ('0e2b15c3', 'srhadd v3.8b, v14.8b, v11.8b', 0, ()),
    ('4e2b15c3', 'srhadd v3.16b, v14.16b, v11.16b', 0, ()),
    ('0e6b15c3', 'srhadd v3.4h, v14.4h, v11.4h', 0, ()),
    ('4e6b15c3', 'srhadd v3.8h, v14.8h, v11.8h', 0, ()),
    ('0eab15c3', 'srhadd v3.2s, v14.2s, v11.2s', 0, ()),
    ('4eab15c3', 'srhadd v3.4s, v14.4s, v11.4s', 0, ()),
    #shsub
    ('0e2b25c3', 'shsub v3.8b, v14.8b, v11.8b', 0, ()),
    ('4e2b25c3', 'shsub v3.16b, v14.16b, v11.16b', 0, ()),
    ('0e6b25c3', 'shsub v3.4h, v14.4h, v11.4h', 0, ()),
    ('4e6b25c3', 'shsub v3.8h, v14.8h, v11.8h', 0, ()),
    ('0eab25c3', 'shsub v3.2s, v14.2s, v11.2s', 0, ()),
    ('4eab25c3', 'shsub v3.4s, v14.4s, v11.4s', 0, ()),
    #sqsub
    ('0e2b2dc3', 'sqsub v3.8b, v14.8b, v11.8b', 0, ()),
    ('4e2b2dc3', 'sqsub v3.16b, v14.16b, v11.16b', 0, ()),
    ('0e6b2dc3', 'sqsub v3.4h, v14.4h, v11.4h', 0, ()),
    ('4e6b2dc3', 'sqsub v3.8h, v14.8h, v11.8h', 0, ()),
    ('0eab2dc3', 'sqsub v3.2s, v14.2s, v11.2s', 0, ()),
    ('4eab2dc3', 'sqsub v3.4s, v14.4s, v11.4s', 0, ()),
    ('4eeb2dc3', 'sqsub v3.2d, v14.2d, v11.2d', 0, ()),
    #cmgt (register)
    ('0e2b35c3', 'cmgt v3.8b, v14.8b, v11.8b', 0, ()),
    ('4e2b35c3', 'cmgt v3.16b, v14.16b, v11.16b', 0, ()),
    ('0e6b35c3', 'cmgt v3.4h, v14.4h, v11.4h', 0, ()),
    ('4e6b35c3', 'cmgt v3.8h, v14.8h, v11.8h', 0, ()),
    ('0eab35c3', 'cmgt v3.2s, v14.2s, v11.2s', 0, ()),
    ('4eab35c3', 'cmgt v3.4s, v14.4s, v11.4s', 0, ()),
    ('4eeb35c3', 'cmgt v3.2d, v14.2d, v11.2d', 0, ()),
    #cmge (register)
    ('0e2b3dc3', 'cmge v3.8b, v14.8b, v11.8b', 0, ()),
    ('4e2b3dc3', 'cmge v3.16b, v14.16b, v11.16b', 0, ()),
    ('0e6b3dc3', 'cmge v3.4h, v14.4h, v11.4h', 0, ()),
    ('4e6b3dc3', 'cmge v3.8h, v14.8h, v11.8h', 0, ()),
    ('0eab3dc3', 'cmge v3.2s, v14.2s, v11.2s', 0, ()),
    ('4eab3dc3', 'cmge v3.4s, v14.4s, v11.4s', 0, ()),
    ('4eeb3dc3', 'cmge v3.2d, v14.2d, v11.2d', 0, ()),
    #sshl
    ('0e2b45c3', 'sshl v3.8b, v14.8b, v11.8b', 0, ()),
    ('4e2b45c3', 'sshl v3.16b, v14.16b, v11.16b', 0, ()),
    ('0e6b45c3', 'sshl v3.4h, v14.4h, v11.4h', 0, ()),
    ('4e6b45c3', 'sshl v3.8h, v14.8h, v11.8h', 0, ()),
    ('0eab45c3', 'sshl v3.2s, v14.2s, v11.2s', 0, ()),
    ('4eab45c3', 'sshl v3.4s, v14.4s, v11.4s', 0, ()),
    ('4eeb45c3', 'sshl v3.2d, v14.2d, v11.2d', 0, ()),
    #sqshl (register)
    ('0e2b4dc3', 'sqshl v3.8b, v14.8b, v11.8b', 0, ()),
    ('4e2b4dc3', 'sqshl v3.16b, v14.16b, v11.16b', 0, ()),
    ('0e6b4dc3', 'sqshl v3.4h, v14.4h, v11.4h', 0, ()),
    ('4e6b4dc3', 'sqshl v3.8h, v14.8h, v11.8h', 0, ()),
    ('0eab4dc3', 'sqshl v3.2s, v14.2s, v11.2s', 0, ()),
    ('4eab4dc3', 'sqshl v3.4s, v14.4s, v11.4s', 0, ()),
    ('4eeb4dc3', 'sqshl v3.2d, v14.2d, v11.2d', 0, ()),
    #srshl
    ('0e2b55c3', 'srshl v3.8b, v14.8b, v11.8b', 0, ()),
    ('4e2b55c3', 'srshl v3.16b, v14.16b, v11.16b', 0, ()),
    ('0e6b55c3', 'srshl v3.4h, v14.4h, v11.4h', 0, ()),
    ('4e6b55c3', 'srshl v3.8h, v14.8h, v11.8h', 0, ()),
    ('0eab55c3', 'srshl v3.2s, v14.2s, v11.2s', 0, ()),
    ('4eab55c3', 'srshl v3.4s, v14.4s, v11.4s', 0, ()),
    ('4eeb55c3', 'srshl v3.2d, v14.2d, v11.2d', 0, ()),
    #sqrshl
    ('0e2b5dc3', 'sqrshl v3.8b, v14.8b, v11.8b', 0, ()),
    ('4e2b5dc3', 'sqrshl v3.16b, v14.16b, v11.16b', 0, ()),
    ('0e6b5dc3', 'sqrshl v3.4h, v14.4h, v11.4h', 0, ()),
    ('4e6b5dc3', 'sqrshl v3.8h, v14.8h, v11.8h', 0, ()),
    ('0eab5dc3', 'sqrshl v3.2s, v14.2s, v11.2s', 0, ()),
    ('4eab5dc3', 'sqrshl v3.4s, v14.4s, v11.4s', 0, ()),
    ('4eeb5dc3', 'sqrshl v3.2d, v14.2d, v11.2d', 0, ()),
    #smax
    ('0e2b65c3', 'smax v3.8b, v14.8b, v11.8b', 0, ()),
    ('4e2b65c3', 'smax v3.16b, v14.16b, v11.16b', 0, ()),
    ('0e6b65c3', 'smax v3.4h, v14.4h, v11.4h', 0, ()),
    ('4e6b65c3', 'smax v3.8h, v14.8h, v11.8h', 0, ()),
    ('0eab65c3', 'smax v3.2s, v14.2s, v11.2s', 0, ()),
    ('4eab65c3', 'smax v3.4s, v14.4s, v11.4s', 0, ()),
    #smin
    ('0e2b6dc3', 'smin v3.8b, v14.8b, v11.8b', 0, ()),
    ('4e2b6dc3', 'smin v3.16b, v14.16b, v11.16b', 0, ()),
    ('0e6b6dc3', 'smin v3.4h, v14.4h, v11.4h', 0, ()),
    ('4e6b6dc3', 'smin v3.8h, v14.8h, v11.8h', 0, ()),
    ('0eab6dc3', 'smin v3.2s, v14.2s, v11.2s', 0, ()),
    ('4eab6dc3', 'smin v3.4s, v14.4s, v11.4s', 0, ()),
    #sabd
    ('0e2b75c3', 'sabd v3.8b, v14.8b, v11.8b', 0, ()),
    ('4e2b75c3', 'sabd v3.16b, v14.16b, v11.16b', 0, ()),
    ('0e6b75c3', 'sabd v3.4h, v14.4h, v11.4h', 0, ()),
    ('4e6b75c3', 'sabd v3.8h, v14.8h, v11.8h', 0, ()),
    ('0eab75c3', 'sabd v3.2s, v14.2s, v11.2s', 0, ()),
    ('4eab75c3', 'sabd v3.4s, v14.4s, v11.4s', 0, ()),
    #saba
    ('0e2b7dc3', 'saba v3.8b, v14.8b, v11.8b', 0, ()),
    ('4e2b7dc3', 'saba v3.16b, v14.16b, v11.16b', 0, ()),
    ('0e6b7dc3', 'saba v3.4h, v14.4h, v11.4h', 0, ()),
    ('4e6b7dc3', 'saba v3.8h, v14.8h, v11.8h', 0, ()),
    ('0eab7dc3', 'saba v3.2s, v14.2s, v11.2s', 0, ()),
    ('4eab7dc3', 'saba v3.4s, v14.4s, v11.4s', 0, ()),
    #add (vector)
    ('0e2b85c3', 'add v3.8b, v14.8b, v11.8b', 0, ()),
    ('4e2b85c3', 'add v3.16b, v14.16b, v11.16b', 0, ()),
    ('0e6b85c3', 'add v3.4h, v14.4h, v11.4h', 0, ()),
    ('4e6b85c3', 'add v3.8h, v14.8h, v11.8h', 0, ()),
    ('0eab85c3', 'add v3.2s, v14.2s, v11.2s', 0, ()),
    ('4eab85c3', 'add v3.4s, v14.4s, v11.4s', 0, ()),
    ('4eeb85c3', 'add v3.2d, v14.2d, v11.2d', 0, ()),
    #cmtst
    ('0e2b8dc3', 'cmtst v3.8b, v14.8b, v11.8b', 0, ()),
    ('4e2b8dc3', 'cmtst v3.16b, v14.16b, v11.16b', 0, ()),
    ('0e6b8dc3', 'cmtst v3.4h, v14.4h, v11.4h', 0, ()),
    ('4e6b8dc3', 'cmtst v3.8h, v14.8h, v11.8h', 0, ()),
    ('0eab8dc3', 'cmtst v3.2s, v14.2s, v11.2s', 0, ()),
    ('4eab8dc3', 'cmtst v3.4s, v14.4s, v11.4s', 0, ()),
    ('4eeb8dc3', 'cmtst v3.2d, v14.2d, v11.2d', 0, ()),
    #mla (vector)
    ('0e2b95c3', 'mla v3.8b, v14.8b, v11.8b', 0, ()),
    ('4e2b95c3', 'mla v3.16b, v14.16b, v11.16b', 0, ()),
    ('0e6b95c3', 'mla v3.4h, v14.4h, v11.4h', 0, ()),
    ('4e6b95c3', 'mla v3.8h, v14.8h, v11.8h', 0, ()),
    ('0eab95c3', 'mla v3.2s, v14.2s, v11.2s', 0, ()),
    ('4eab95c3', 'mla v3.4s, v14.4s, v11.4s', 0, ()),
    #mul (vector)
    ('0e2b9dc3', 'mul v3.8b, v14.8b, v11.8b', 0, ()),
    ('4e2b9dc3', 'mul v3.16b, v14.16b, v11.16b', 0, ()),
    ('0e6b9dc3', 'mul v3.4h, v14.4h, v11.4h', 0, ()),
    ('4e6b9dc3', 'mul v3.8h, v14.8h, v11.8h', 0, ()),
    ('0eab9dc3', 'mul v3.2s, v14.2s, v11.2s', 0, ()),
    ('4eab9dc3', 'mul v3.4s, v14.4s, v11.4s', 0, ()),
    #smaxp
    ('0e2ba5c3', 'smaxp v3.8b, v14.8b, v11.8b', 0, ()),
    ('4e2ba5c3', 'smaxp v3.16b, v14.16b, v11.16b', 0, ()),
    ('0e6ba5c3', 'smaxp v3.4h, v14.4h, v11.4h', 0, ()),
    ('4e6ba5c3', 'smaxp v3.8h, v14.8h, v11.8h', 0, ()),
    ('0eaba5c3', 'smaxp v3.2s, v14.2s, v11.2s', 0, ()),
    ('4eaba5c3', 'smaxp v3.4s, v14.4s, v11.4s', 0, ()),
    #sminp
    ('0e2badc3', 'sminp v3.8b, v14.8b, v11.8b', 0, ()),
    ('4e2badc3', 'sminp v3.16b, v14.16b, v11.16b', 0, ()),
    ('0e6badc3', 'sminp v3.4h, v14.4h, v11.4h', 0, ()),
    ('4e6badc3', 'sminp v3.8h, v14.8h, v11.8h', 0, ()),
    ('0eabadc3', 'sminp v3.2s, v14.2s, v11.2s', 0, ()),
    ('4eabadc3', 'sminp v3.4s, v14.4s, v11.4s', 0, ()),
    #sqdmulh (vector)
    ('0e6bb5c3', 'sqdmulh v3.4h, v14.4h, v11.4h', 0, ()),
    ('4e6bb5c3', 'sqdmulh v3.8h, v14.8h, v11.8h', 0, ()),
    ('0eabb5c3', 'sqdmulh v3.2s, v14.2s, v11.2s', 0, ()),
    ('4eabb5c3', 'sqdmulh v3.4s, v14.4s, v11.4s', 0, ()),
    #addp (vector)
    ('0e2bbdc3', 'addp v3.8b, v14.8b, v11.8b', 0, ()),
    ('4e2bbdc3', 'addp v3.16b, v14.16b, v11.16b', 0, ()),
    ('0e6bbdc3', 'addp v3.4h, v14.4h, v11.4h', 0, ()),
    ('4e6bbdc3', 'addp v3.8h, v14.8h, v11.8h', 0, ()),
    ('0eabbdc3', 'addp v3.2s, v14.2s, v11.2s', 0, ()),
    ('4eabbdc3', 'addp v3.4s, v14.4s, v11.4s', 0, ()),
    ('4eebbdc3', 'addp v3.2d, v14.2d, v11.2d', 0, ()),
    #fmaxnm (vector)
    ('0e2bc5c3', 'fmaxnm v3.2s, v14.2s, v11.2s', 0, ()),
    ('4e2bc5c3', 'fmaxnm v3.4s, v14.4s, v11.4s', 0, ()),
    ('4e6bc5c3', 'fmaxnm v3.2d, v14.2d, v11.2d', 0, ()),
    #fmla (vector)
    ('0e2bcdc3', 'fmla v3.2s, v14.2s, v11.2s', 0, ()),
    ('4e2bcdc3', 'fmla v3.4s, v14.4s, v11.4s', 0, ()),
    ('4e6bcdc3', 'fmla v3.2d, v14.2d, v11.2d', 0, ()),
    #fadd (vector)
    ('0e2bd5c3', 'fadd v3.2s, v14.2s, v11.2s', 0, ()),
    ('4e2bd5c3', 'fadd v3.4s, v14.4s, v11.4s', 0, ()),
    ('4e6bd5c3', 'fadd v3.2d, v14.2d, v11.2d', 0, ()),
    #fmulx
    ('0e2bddc3', 'fmulx v3.2s, v14.2s, v11.2s', 0, ()),
    ('4e2bddc3', 'fmulx v3.4s, v14.4s, v11.4s', 0, ()),
    ('4e6bddc3', 'fmulx v3.2d, v14.2d, v11.2d', 0, ()),
    #fcmeq (register)
    ('0e2be5c3', 'fcmeq v3.2s, v14.2s, v11.2s', 0, ()),
    ('4e2be5c3', 'fcmeq v3.4s, v14.4s, v11.4s', 0, ()),
    ('4e6be5c3', 'fcmeq v3.2d, v14.2d, v11.2d', 0, ()),
    #fmax (vector)
    ('0e2bf5c3', 'fmax v3.2s, v14.2s, v11.2s', 0, ()),
    ('4e2bf5c3', 'fmax v3.4s, v14.4s, v11.4s', 0, ()),
    ('4e6bf5c3', 'fmax v3.2d, v14.2d, v11.2d', 0, ()),
    #frecps
    ('0e2bfdc3', 'frecps v3.2s, v14.2s, v11.2s', 0, ()),
    ('4e2bfdc3', 'frecps v3.4s, v14.4s, v11.4s', 0, ()),
    ('4e6bfdc3', 'frecps v3.2d, v14.2d, v11.2d', 0, ()),
    #and (vector)
    ('0e2b1dc3', 'and v3.8b, v14.8b, v11.8b', 0, ()),
    ('4e2b1dc3', 'and v3.16b, v14.16b, v11.16b', 0, ()),
    #bic (vector, register)
    ('0e6b1dc3', 'bic v3.8b, v14.8b, v11.8b', 0, ()),
    ('4e6b1dc3', 'bic v3.16b, v14.16b, v11.16b', 0, ()),
    #fminnm (vector)
    ('0eabc5c3', 'fminnm v3.2s, v14.2s, v11.2s', 0, ()),
    ('4eabc5c3', 'fminnm v3.4s, v14.4s, v11.4s', 0, ()),
    ('4eebc5c3', 'fminnm v3.2d, v14.2d, v11.2d', 0, ()),
    #fmls (vector)
    ('0eabcdc3', 'fmls v3.2s, v14.2s, v11.2s', 0, ()),
    ('4eabcdc3', 'fmls v3.4s, v14.4s, v11.4s', 0, ()),
    ('4eebcdc3', 'fmls v3.2d, v14.2d, v11.2d', 0, ()),
    #fsub (vector)
    ('0eabd5c3', 'fsub v3.2s, v14.2s, v11.2s', 0, ()),
    ('4eabd5c3', 'fsub v3.4s, v14.4s, v11.4s', 0, ()),
    ('4eebd5c3', 'fsub v3.2d, v14.2d, v11.2d', 0, ()),
    #fmin (vector)
    ('0eabf5c3', 'fmin v3.2s, v14.2s, v11.2s', 0, ()),
    ('4eabf5c3', 'fmin v3.4s, v14.4s, v11.4s', 0, ()),
    ('4eebf5c3', 'fmin v3.2d, v14.2d, v11.2d', 0, ()),
    #fsqrts
    ('0eabfdc3', 'fsqrts v3.2s, v14.2s, v11.2s', 0, ()),
    ('4eabfdc3', 'fsqrts v3.4s, v14.4s, v11.4s', 0, ()),
    ('4eebfdc3', 'fsqrts v3.2d, v14.2d, v11.2d', 0, ()),
    #orr (vector, register)
    ('0eab1dc3', 'orr v3.8b, v14.8b, v11.8b', 0, ()),
    ('4eab1dc3', 'orr v3.16b, v14.16b, v11.16b', 0, ()),
    #orn (vector)
    ('0eeb1dc3', 'orn v3.8b, v14.8b, v11.8b', 0, ()),
    ('4eeb1dc3', 'orn v3.16b, v14.16b, v11.16b', 0, ()),
    #uhadd
    ('2e2b05c3', 'uhadd v3.8b, v14.8b, v11.8b', 0, ()),
    ('6e2b05c3', 'shadd v3.16b, v14.16b, v11.16b', 0, ()),
    ('2e6b05c3', 'shadd v3.4h, v14.4h, v11.4h', 0, ()),
    ('6e6b05c3', 'shadd v3.8h, v14.8h, v11.8h', 0, ()),
    ('2eab05c3', 'shadd v3.2s, v14.2s, v11.2s', 0, ()),
    ('6eab05c3', 'shadd v3.4s, v14.4s, v11.4s', 0, ()),
    #uqadd
    ('2e2b0dc3', 'uqadd v3.8b, v14.8b, v11.8b', 0, ()),
    ('6e2b0dc3', 'uqadd v3.16b, v14.16b, v11.16b', 0, ()),
    ('2e6b0dc3', 'uqadd v3.4h, v14.4h, v11.4h', 0, ()),
    ('6e6b0dc3', 'uqadd v3.8h, v14.8h, v11.8h', 0, ()),
    ('2eab0dc3', 'uqadd v3.2s, v14.2s, v11.2s', 0, ()),
    ('6eab0dc3', 'uqadd v3.4s, v14.4s, v11.4s', 0, ()),
    ('6eeb0dc3', 'uqadd v3.2d, v14.2d, v11.2d', 0, ()),
    #urhadd
    ('2e2b15c3', 'urhadd v3.8b, v14.8b, v11.8b', 0, ()),
    ('6e2b15c3', 'urhadd v3.16b, v14.16b, v11.16b', 0, ()),
    ('2e6b15c3', 'urhadd v3.4h, v14.4h, v11.4h', 0, ()),
    ('6e6b15c3', 'urhadd v3.8h, v14.8h, v11.8h', 0, ()),
    ('2eab15c3', 'urhadd v3.2s, v14.2s, v11.2s', 0, ()),
    ('6eab15c3', 'urhadd v3.4s, v14.4s, v11.4s', 0, ()),
    #uhsub
    ('2e2b25c3', 'uhsub v3.8b, v14.8b, v11.8b', 0, ()),
    ('6e2b25c3', 'uhsub v3.16b, v14.16b, v11.16b', 0, ()),
    ('2e6b25c3', 'uhsub v3.4h, v14.4h, v11.4h', 0, ()),
    ('6e6b25c3', 'uhsub v3.8h, v14.8h, v11.8h', 0, ()),
    ('2eab25c3', 'uhsub v3.2s, v14.2s, v11.2s', 0, ()),
    ('6eab25c3', 'uhsub v3.4s, v14.4s, v11.4s', 0, ()),
    #uqsub
    ('2e2b2dc3', 'uqsub v3.8b, v14.8b, v11.8b', 0, ()),
    ('6e2b2dc3', 'uqsub v3.16b, v14.16b, v11.16b', 0, ()),
    ('2e6b2dc3', 'uqsub v3.4h, v14.4h, v11.4h', 0, ()),
    ('6e6b2dc3', 'uqsub v3.8h, v14.8h, v11.8h', 0, ()),
    ('2eab2dc3', 'uqsub v3.2s, v14.2s, v11.2s', 0, ()),
    ('6eab2dc3', 'uqsub v3.4s, v14.4s, v11.4s', 0, ()),
    ('6eeb2dc3', 'uqsub v3.2d, v14.2d, v11.2d', 0, ()),
    #cmhi (register)
    ('2e2b35c3', 'cmhi v3.8b, v14.8b, v11.8b', 0, ()),
    ('6e2b35c3', 'cmhi v3.16b, v14.16b, v11.16b', 0, ()),
    ('2e6b35c3', 'cmhi v3.4h, v14.4h, v11.4h', 0, ()),
    ('6e6b35c3', 'cmhi v3.8h, v14.8h, v11.8h', 0, ()),
    ('2eab35c3', 'cmhi v3.2s, v14.2s, v11.2s', 0, ()),
    ('6eab35c3', 'cmhi v3.4s, v14.4s, v11.4s', 0, ()),
    ('6eeb35c3', 'cmhi v3.2d, v14.2d, v11.2d', 0, ()),
    #cmhs (register)
    ('2e2b3dc3', 'cmhs v3.8b, v14.8b, v11.8b', 0, ()),
    ('6e2b3dc3', 'cmhs v3.16b, v14.16b, v11.16b', 0, ()),
    ('2e6b3dc3', 'cmhs v3.4h, v14.4h, v11.4h', 0, ()),
    ('6e6b3dc3', 'cmhs v3.8h, v14.8h, v11.8h', 0, ()),
    ('2eab3dc3', 'cmhs v3.2s, v14.2s, v11.2s', 0, ()),
    ('6eab3dc3', 'cmhs v3.4s, v14.4s, v11.4s', 0, ()),
    ('6eeb3dc3', 'cmhs v3.2d, v14.2d, v11.2d', 0, ()),
    #ushl
    ('2e2b45c3', 'ushl v3.8b, v14.8b, v11.8b', 0, ()),
    ('6e2b45c3', 'ushl v3.16b, v14.16b, v11.16b', 0, ()),
    ('2e6b45c3', 'ushl v3.4h, v14.4h, v11.4h', 0, ()),
    ('6e6b45c3', 'ushl v3.8h, v14.8h, v11.8h', 0, ()),
    ('2eab45c3', 'ushl v3.2s, v14.2s, v11.2s', 0, ()),
    ('6eab45c3', 'ushl v3.4s, v14.4s, v11.4s', 0, ()),
    ('6eeb45c3', 'ushl v3.2d, v14.2d, v11.2d', 0, ()),
    #uqshl (register)
    ('2e2b4dc3', 'uqshl v3.8b, v14.8b, v11.8b', 0, ()),
    ('6e2b4dc3', 'uqshl v3.16b, v14.16b, v11.16b', 0, ()),
    ('2e6b4dc3', 'uqshl v3.4h, v14.4h, v11.4h', 0, ()),
    ('6e6b4dc3', 'uqshl v3.8h, v14.8h, v11.8h', 0, ()),
    ('2eab4dc3', 'uqshl v3.2s, v14.2s, v11.2s', 0, ()),
    ('6eab4dc3', 'uqshl v3.4s, v14.4s, v11.4s', 0, ()),
    ('6eeb4dc3', 'uqshl v3.2d, v14.2d, v11.2d', 0, ()),
    #urshl
    ('2e2b55c3', 'urshl v3.8b, v14.8b, v11.8b', 0, ()),
    ('6e2b55c3', 'urshl v3.16b, v14.16b, v11.16b', 0, ()),
    ('2e6b55c3', 'urshl v3.4h, v14.4h, v11.4h', 0, ()),
    ('6e6b55c3', 'urshl v3.8h, v14.8h, v11.8h', 0, ()),
    ('2eab55c3', 'urshl v3.2s, v14.2s, v11.2s', 0, ()),
    ('6eab55c3', 'urshl v3.4s, v14.4s, v11.4s', 0, ()),
    ('6eeb55c3', 'urshl v3.2d, v14.2d, v11.2d', 0, ()),
    #uqrshl
    ('2e2b5dc3', 'uqrshl v3.8b, v14.8b, v11.8b', 0, ()),
    ('6e2b5dc3', 'uqrshl v3.16b, v14.16b, v11.16b', 0, ()),
    ('2e6b5dc3', 'uqrshl v3.4h, v14.4h, v11.4h', 0, ()),
    ('6e6b5dc3', 'uqrshl v3.8h, v14.8h, v11.8h', 0, ()),
    ('2eab5dc3', 'uqrshl v3.2s, v14.2s, v11.2s', 0, ()),
    ('6eab5dc3', 'uqrshl v3.4s, v14.4s, v11.4s', 0, ()),
    ('6eeb5dc3', 'uqrshl v3.2d, v14.2d, v11.2d', 0, ()),
    #smax
    ('2e2b65c3', 'umax v3.8b, v14.8b, v11.8b', 0, ()),
    ('6e2b65c3', 'umax v3.16b, v14.16b, v11.16b', 0, ()),
    ('2e6b65c3', 'umax v3.4h, v14.4h, v11.4h', 0, ()),
    ('6e6b65c3', 'umax v3.8h, v14.8h, v11.8h', 0, ()),
    ('2eab65c3', 'umax v3.2s, v14.2s, v11.2s', 0, ()),
    ('6eab65c3', 'umax v3.4s, v14.4s, v11.4s', 0, ()),
    #umin
    ('2e2b6dc3', 'umin v3.8b, v14.8b, v11.8b', 0, ()),
    ('6e2b6dc3', 'umin v3.16b, v14.16b, v11.16b', 0, ()),
    ('2e6b6dc3', 'umin v3.4h, v14.4h, v11.4h', 0, ()),
    ('6e6b6dc3', 'umin v3.8h, v14.8h, v11.8h', 0, ()),
    ('2eab6dc3', 'umin v3.2s, v14.2s, v11.2s', 0, ()),
    ('6eab6dc3', 'umin v3.4s, v14.4s, v11.4s', 0, ()),
    #uabd
    ('2e2b75c3', 'uabd v3.8b, v14.8b, v11.8b', 0, ()),
    ('6e2b75c3', 'uabd v3.16b, v14.16b, v11.16b', 0, ()),
    ('2e6b75c3', 'uabd v3.4h, v14.4h, v11.4h', 0, ()),
    ('6e6b75c3', 'uabd v3.8h, v14.8h, v11.8h', 0, ()),
    ('2eab75c3', 'uabd v3.2s, v14.2s, v11.2s', 0, ()),
    ('6eab75c3', 'uabd v3.4s, v14.4s, v11.4s', 0, ()),
    #uaba
    ('2e2b7dc3', 'uaba v3.8b, v14.8b, v11.8b', 0, ()),
    ('6e2b7dc3', 'uaba v3.16b, v14.16b, v11.16b', 0, ()),
    ('2e6b7dc3', 'uaba v3.4h, v14.4h, v11.4h', 0, ()),
    ('6e6b7dc3', 'uaba v3.8h, v14.8h, v11.8h', 0, ()),
    ('2eab7dc3', 'uaba v3.2s, v14.2s, v11.2s', 0, ()),
    ('6eab7dc3', 'uaba v3.4s, v14.4s, v11.4s', 0, ()),
    #sub (vector)
    ('2e2b85c3', 'sub v3.8b, v14.8b, v11.8b', 0, ()),
    ('6e2b85c3', 'sub v3.16b, v14.16b, v11.16b', 0, ()),
    ('2e6b85c3', 'sub v3.4h, v14.4h, v11.4h', 0, ()),
    ('6e6b85c3', 'sub v3.8h, v14.8h, v11.8h', 0, ()),
    ('2eab85c3', 'sub v3.2s, v14.2s, v11.2s', 0, ()),
    ('6eab85c3', 'sub v3.4s, v14.4s, v11.4s', 0, ()),
    ('6eeb85c3', 'sub v3.2d, v14.2d, v11.2d', 0, ()),
    #cmeq
    ('2e2b8dc3', 'cmeq v3.8b, v14.8b, v11.8b', 0, ()),
    ('6e2b8dc3', 'cmeq v3.16b, v14.16b, v11.16b', 0, ()),
    ('2e6b8dc3', 'cmeq v3.4h, v14.4h, v11.4h', 0, ()),
    ('6e6b8dc3', 'cmeq v3.8h, v14.8h, v11.8h', 0, ()),
    ('2eab8dc3', 'cmeq v3.2s, v14.2s, v11.2s', 0, ()),
    ('6eab8dc3', 'cmeq v3.4s, v14.4s, v11.4s', 0, ()),
    ('6eeb8dc3', 'cmeq v3.2d, v14.2d, v11.2d', 0, ()),
    #mls (vector)
    ('0e2b95c3', 'mls v3.8b, v14.8b, v11.8b', 0, ()),
    ('4e2b95c3', 'mls v3.16b, v14.16b, v11.16b', 0, ()),
    ('0e6b95c3', 'mls v3.4h, v14.4h, v11.4h', 0, ()),
    ('4e6b95c3', 'mls v3.8h, v14.8h, v11.8h', 0, ()),
    ('0eab95c3', 'mls v3.2s, v14.2s, v11.2s', 0, ()),
    ('4eab95c3', 'mls v3.4s, v14.4s, v11.4s', 0, ()),
    #pmul (vector)
    ('2e2b9dc3', 'pmul v3.8b, v14.8b, v11.8b', 0, ()),
    ('6e2b9dc3', 'pmul v3.16b, v14.16b, v11.16b', 0, ()),
    #umaxp
    ('2e2ba5c3', 'umaxp v3.8b, v14.8b, v11.8b', 0, ()),
    ('6e2ba5c3', 'umaxp v3.16b, v14.16b, v11.16b', 0, ()),
    ('2e6ba5c3', 'umaxp v3.4h, v14.4h, v11.4h', 0, ()),
    ('6e6ba5c3', 'umaxp v3.8h, v14.8h, v11.8h', 0, ()),
    ('2eaba5c3', 'umaxp v3.2s, v14.2s, v11.2s', 0, ()),
    ('6eaba5c3', 'umaxp v3.4s, v14.4s, v11.4s', 0, ()),
    #uminp
    ('2e2badc3', 'uminp v3.8b, v14.8b, v11.8b', 0, ()),
    ('6e2badc3', 'uminp v3.16b, v14.16b, v11.16b', 0, ()),
    ('2e6badc3', 'uminp v3.4h, v14.4h, v11.4h', 0, ()),
    ('6e6badc3', 'uminp v3.8h, v14.8h, v11.8h', 0, ()),
    ('2eabadc3', 'uminp v3.2s, v14.2s, v11.2s', 0, ()),
    ('6eabadc3', 'uminp v3.4s, v14.4s, v11.4s', 0, ()),
    #sqrdmulh (vector)
    ('2e6bb5c3', 'sqrdmulh v3.4h, v14.4h, v11.4h', 0, ()),
    ('6e6bb5c3', 'sqrdmulh v3.8h, v14.8h, v11.8h', 0, ()),
    ('2eabb5c3', 'sqrdmulh v3.2s, v14.2s, v11.2s', 0, ()),
    ('6eabb5c3', 'sqrdmulh v3.4s, v14.4s, v11.4s', 0, ()),
    #fmaxnmp (vector)
    ('2e2bc5c3', 'fmaxnmp v3.2s, v14.2s, v11.2s', 0, ()),
    ('6e2bc5c3', 'fmaxnmp v3.4s, v14.4s, v11.4s', 0, ()),
    ('6e6bc5c3', 'fmaxnmp v3.2d, v14.2d, v11.2d', 0, ()),
    #faddp (vector)
    ('2e2bd5c3', 'faddp v3.2s, v14.2s, v11.2s', 0, ()),
    ('6e2bd5c3', 'faddp v3.4s, v14.4s, v11.4s', 0, ()),
    ('6e6bd5c3', 'faddp v3.2d, v14.2d, v11.2d', 0, ()),
    #fmul
    ('2e2bddc3', 'fmul v3.2s, v14.2s, v11.2s', 0, ()),
    ('6e2bddc3', 'fmul v3.4s, v14.4s, v11.4s', 0, ()),
    ('6e6bddc3', 'fmul v3.2d, v14.2d, v11.2d', 0, ()),
    #fcmge (register)
    ('2e2be5c3', 'fcmge v3.2s, v14.2s, v11.2s', 0, ()),
    ('6e2be5c3', 'fcmge v3.4s, v14.4s, v11.4s', 0, ()),
    ('6e6be5c3', 'fcmge v3.2d, v14.2d, v11.2d', 0, ()),
    #facge (vector)
    ('2e2bedc3', 'facge v3.2s, v14.2s, v11.2s', 0, ()),
    ('6e2bedc3', 'facge v3.4s, v14.4s, v11.4s', 0, ()),
    ('6e6bedc3', 'facge v3.2d, v14.2d, v11.2d', 0, ()),
    #fmaxp (vector)
    ('2e2bf5c3', 'fmaxp v3.2s, v14.2s, v11.2s', 0, ()),
    ('6e2bf5c3', 'fmaxp v3.4s, v14.4s, v11.4s', 0, ()),
    ('6e6bf5c3', 'fmaxp v3.2d, v14.2d, v11.2d', 0, ()),
    #fdiv
    ('2e2bfdc3', 'fdiv v3.2s, v14.2s, v11.2s', 0, ()),
    ('6e2bfdc3', 'fdiv v3.4s, v14.4s, v11.4s', 0, ()),
    ('6e6bfdc3', 'fdiv v3.2d, v14.2d, v11.2d', 0, ()),
    #eor (vector)
    ('2e2b1dc3', 'eor v3.8b, v14.8b, v11.8b', 0, ()),
    ('6e2b1dc3', 'eor v3.16b, v14.16b, v11.16b', 0, ()),
    #bsl
    ('2e6b1dc3', 'bsl v3.8b, v14.8b, v11.8b', 0, ()),
    ('6e6b1dc3', 'bsl v3.16b, v14.16b, v11.16b', 0, ()),
    #fminnmp (vector)
    ('2eabc5c3', 'fminnmp v3.2s, v14.2s, v11.2s', 0, ()),
    ('6eabc5c3', 'fminnmp v3.4s, v14.4s, v11.4s', 0, ()),
    ('6eebc5c3', 'fminnmp v3.2d, v14.2d, v11.2d', 0, ()),
    #fabd (vector)
    ('2eabd5c3', 'fabd v3.2s, v14.2s, v11.2s', 0, ()),
    ('6eabd5c3', 'fabd v3.4s, v14.4s, v11.4s', 0, ()),
    ('6eebd5c3', 'fabd v3.2d, v14.2d, v11.2d', 0, ()),
    #fcmgt
    ('2eabe5c3', 'fcmgt v3.2s, v14.2s, v11.2s', 0, ()),
    ('6eabe5c3', 'fcmgt v3.4s, v14.4s, v11.4s', 0, ()),
    ('6eebe5c3', 'fcmgt v3.2d, v14.2d, v11.2d', 0, ()),
    #facgt
    ('2eabedc3', 'facgt v3.2s, v14.2s, v11.2s', 0, ()),
    ('6eabedc3', 'facgt v3.4s, v14.4s, v11.4s', 0, ()),
    ('6eebedc3', 'facgt v3.2d, v14.2d, v11.2d', 0, ()),
    #fminp (vector)
    ('2eabf5c3', 'fminp v3.2s, v14.2s, v11.2s', 0, ()),
    ('6eabf5c3', 'fminp v3.4s, v14.4s, v11.4s', 0, ()),
    ('6eebf5c3', 'fminp v3.2d, v14.2d, v11.2d', 0, ()),
    #bit
    ('2eab1dc3', 'bit v3.8b, v14.8b, v11.8b', 0, ()),
    ('6eab1dc3', 'bit v3.16b, v14.16b, v11.16b', 0, ()),
    #bif
    ('2eeb1dc3', 'bif v3.8b, v14.8b, v11.8b', 0, ()),
    ('6eeb1dc3', 'bif v3.16b, v14.16b, v11.16b', 0, ()),

    #AdvSIMD three different

    #saddl
    ('0e2b01c3', 'saddl{} v3.8h, v14.8b, v11.8b', 0, ()),
    ('4e2b01c3', 'saddl{2} v3.8h, v14.16b, v11.16b', 0, ()),
    ('0e6b01c3', 'saddl{} v3.4s, v14.4h, v11.4h', 0, ()),
    ('4e6b01c3', 'saddl{2} v3.4s, v14.8h, v11.8h', 0, ()),
    ('0eab01c3', 'saddl{} v3.2d, v14.2s, v11.2s', 0, ()),
    ('4eab01c3', 'saddl{2} v3.2d, v14.4s, v11.4s', 0, ()),
    #saddw
    ('0e2b11c3', 'saddw{} v3.8h, v14.8h, v11.8b', 0, ()),
    ('4e2b11c3', 'saddw{2} v3.8h, v14.8h, v11.16b', 0, ()),
    ('0e6b11c3', 'saddw{} v3.4s, v14.4s, v11.4h', 0, ()),
    ('4e6b11c3', 'saddw{2} v3.4s, v14.4s, v11.8h', 0, ()),
    ('0eab11c3', 'saddw{} v3.2d, v14.2d, v11.2s', 0, ()),
    ('4eab11c3', 'saddw{2} v3.2d, v14.2d, v11.4s', 0, ()),
    #ssubl
    ('0e2b21c3', 'ssubl{} v3.8h, v14.8b, v11.8b', 0, ()),
    ('4e2b21c3', 'ssubl{2} v3.8h, v14.16b, v11.16b', 0, ()),
    ('0e6b21c3', 'ssubl{} v3.4s, v14.4h, v11.4h', 0, ()),
    ('4e6b21c3', 'ssubl{2} v3.4s, v14.8h, v11.8h', 0, ()),
    ('0eab21c3', 'ssubl{} v3.2d, v14.2s, v11.2s', 0, ()),
    ('4eab21c3', 'ssubl{2} v3.2d, v14.4s, v11.4s', 0, ()),
    #ssubw
    ('0e2b31c3', 'ssubw{} v3.8h, v14.8h, v11.8b', 0, ()),
    ('4e2b31c3', 'ssubw{2} v3.8h, v14.8h, v11.16b', 0, ()),
    ('0e6b31c3', 'ssubw{} v3.4s, v14.4s, v11.4h', 0, ()),
    ('4e6b31c3', 'ssubw{2} v3.4s, v14.4s, v11.8h', 0, ()),
    ('0eab31c3', 'ssubw{} v3.2d, v14.2d, v11.2s', 0, ()),
    ('4eab31c3', 'ssubw{2} v3.2d, v14.2d, v11.4s', 0, ()),
    #addhn
    ('0e2b41c3', 'addhn{} v3.8b, v14.8h, v11.8h', 0, ()),
    ('4e2b41c3', 'addhn{2} v3.16b, v14.8h, v11.8h', 0, ()),
    ('0e6b41c3', 'addhn{} v3.4h, v14.4s, v11.4s', 0, ()),
    ('4e6b41c3', 'addhn{2} v3.8h, v14.4s, v11.4s', 0, ()),
    ('0eab41c3', 'addhn{} v3.2s, v14.2d, v11.2d', 0, ()),
    ('4eab41c3', 'addhn{2} v3.4s, v14.2d, v11.2d', 0, ()),
    #sabal
    ('0e2b51c3', 'sabal{} v3.8h, v14.8b, v11.8b', 0, ()),
    ('4e2b51c3', 'sabal{2} v3.8h, v14.16b, v11.16b', 0, ()),
    ('0e6b51c3', 'sabal{} v3.4s, v14.4h, v11.4h', 0, ()),
    ('4e6b51c3', 'sabal{2} v3.4s, v14.8h, v11.8h', 0, ()),
    ('0eab51c3', 'sabal{} v3.2d, v14.2s, v11.2s', 0, ()),
    ('4eab51c3', 'sabal{2} v3.2d, v14.4s, v11.4s', 0, ()),
    #subhn
    ('0e2b61c3', 'subhn{} v3.8b, v14.8h, v11.8h', 0, ()),
    ('4e2b61c3', 'subhn{2} v3.16b, v14.8h, v11.8h', 0, ()),
    ('0e6b61c3', 'subhn{} v3.4h, v14.4s, v11.4s', 0, ()),
    ('4e6b61c3', 'subhn{2} v3.8h, v14.4s, v11.4s', 0, ()),
    ('0eab61c3', 'subhn{} v3.2s, v14.2d, v11.2d', 0, ()),
    ('4eab61c3', 'subhn{2} v3.4s, v14.2d, v11.2d', 0, ()),
    #sabdl
    ('0e2b71c3', 'sabdl{} v3.8h, v14.8b, v11.8b', 0, ()),
    ('4e2b71c3', 'sabdl{2} v3.8h, v14.16b, v11.16b', 0, ()),
    ('0e6b71c3', 'sabdl{} v3.4s, v14.4h, v11.4h', 0, ()),
    ('4e6b71c3', 'sabdl{2} v3.4s, v14.8h, v11.8h', 0, ()),
    ('0eab71c3', 'sabdl{} v3.2d, v14.2s, v11.2s', 0, ()),
    ('4eab71c3', 'sabdl{2} v3.2d, v14.4s, v11.4s', 0, ()),
    #smlal
    ('0e2b81c3', 'smlal{} v3.8h, v14.8b, v11.8b', 0, ()),
    ('4e2b81c3', 'smlal{2} v3.8h, v14.16b, v11.16b', 0, ()),
    ('0e6b81c3', 'smlal{} v3.4s, v14.4h, v11.4h', 0, ()),
    ('4e6b81c3', 'smlal{2} v3.4s, v14.8h, v11.8h', 0, ()),
    ('0eab81c3', 'smlal{} v3.2d, v14.2s, v11.2s', 0, ()),
    ('4eab81c3', 'smlal{2} v3.2d, v14.4s, v11.4s', 0, ()),
    #sqdmlal
    ('0e6b91c3', 'sqdmlal{} v3.4s, v14.4h, v11.4h', 0, ()),
    ('4e6b91c3', 'sqdmlal{2} v3.4s, v14.8h, v11.8h', 0, ()),
    ('0eab91c3', 'sqdmlal{} v3.2d, v14.2s, v11.2s', 0, ()),
    ('4eab91c3', 'sqdmlal{2} v3.2d, v14.4s, v11.4s', 0, ()),
    #smlsl
    ('0e2ba1c3', 'smlsl{} v3.8h, v14.8b, v11.8b', 0, ()),
    ('4e2ba1c3', 'smlsl{2} v3.8h, v14.16b, v11.16b', 0, ()),
    ('0e6ba1c3', 'smlsl{} v3.4s, v14.4h, v11.4h', 0, ()),
    ('4e6ba1c3', 'smlsl{2} v3.4s, v14.8h, v11.8h', 0, ()),
    ('0eaba1c3', 'smlsl{} v3.2d, v14.2s, v11.2s', 0, ()),
    ('4eaba1c3', 'smlsl{2} v3.2d, v14.4s, v11.4s', 0, ()),
    #sqdmlsl
    ('0e6bb1c3', 'sqdmlsl{} v3.4s, v14.4h, v11.4h', 0, ()),
    ('4e6bb1c3', 'sqdmlsl{2} v3.4s, v14.8h, v11.8h', 0, ()),
    ('0eabb1c3', 'sqdmlsl{} v3.2d, v14.2s, v11.2s', 0, ()),
    ('4eabb1c3', 'sqdmlsl{2} v3.2d, v14.4s, v11.4s', 0, ()),
    #smull
    ('0e2bc1c3', 'smull{} v3.8h, v14.8b, v11.8b', 0, ()),
    ('4e2bc1c3', 'smull{2} v3.8h, v14.16b, v11.16b', 0, ()),
    ('0e6bc1c3', 'smull{} v3.4s, v14.4h, v11.4h', 0, ()),
    ('4e6bc1c3', 'smull{2} v3.4s, v14.8h, v11.8h', 0, ()),
    ('0eabc1c3', 'smull{} v3.2d, v14.2s, v11.2s', 0, ()),
    ('4eabc1c3', 'smull{2} v3.2d, v14.4s, v11.4s', 0, ()),
    #sqdmull
    ('0e6bd1c3', 'sqdmull{} v3.4s, v14.4h, v11.4h', 0, ()),
    ('4e6bd1c3', 'sqdmull{2} v3.4s, v14.8h, v11.8h', 0, ()),
    ('0eabd1c3', 'sqdmull{} v3.2d, v14.2s, v11.2s', 0, ()),
    ('4eabd1c3', 'sqdmull{2} v3.2d, v14.4s, v11.4s', 0, ()),
    #pmull
    ('0e2be1c3', 'pmull{} v3.8h, v14.8b, v11.8b', 0, ()),
    ('4e2be1c3', 'pmull{2} v3.8h, v14.16b, v11.16b', 0, ()),
    ('0eebe1c3', 'pmull{} v3.1q, v14.1d, v11.1d', 0, ()),
    ('4eebe1c3', 'pmull{2} v3.1q, v14.2d, v11.2d', 0, ()),

    #uaddl
    ('2e2b01c3', 'uaddl{} v3.8h, v14.8b, v11.8b', 0, ()),
    ('6e2b01c3', 'uaddl{2} v3.8h, v14.16b, v11.16b', 0, ()),
    ('2e6b01c3', 'uaddl{} v3.4s, v14.4h, v11.4h', 0, ()),
    ('6e6b01c3', 'uaddl{2} v3.4s, v14.8h, v11.8h', 0, ()),
    ('2eab01c3', 'uaddl{} v3.2d, v14.2s, v11.2s', 0, ()),
    ('6eab01c3', 'uaddl{2} v3.2d, v14.4s, v11.4s', 0, ()),
    #uaddw
    ('2e2b11c3', 'uaddw{} v3.8h, v14.8h, v11.8b', 0, ()),
    ('6e2b11c3', 'uaddw{2} v3.8h, v14.8h, v11.16b', 0, ()),
    ('2e6b11c3', 'uaddw{} v3.4s, v14.4s, v11.4h', 0, ()),
    ('6e6b11c3', 'uaddw{2} v3.4s, v14.4s, v11.8h', 0, ()),
    ('2eab11c3', 'uaddw{} v3.2d, v14.2d, v11.2s', 0, ()),
    ('6eab11c3', 'uaddw{2} v3.2d, v14.2d, v11.4s', 0, ()),
    #usubl
    ('2e2b21c3', 'usubl{} v3.8h, v14.8b, v11.8b', 0, ()),
    ('6e2b21c3', 'usubl{2} v3.8h, v14.16b, v11.16b', 0, ()),
    ('2e6b21c3', 'usubl{} v3.4s, v14.4h, v11.4h', 0, ()),
    ('6e6b21c3', 'usubl{2} v3.4s, v14.8h, v11.8h', 0, ()),
    ('2eab21c3', 'usubl{} v3.2d, v14.2s, v11.2s', 0, ()),
    ('6eab21c3', 'usubl{2} v3.2d, v14.4s, v11.4s', 0, ()),
    #usubw
    ('2e2b31c3', 'usubw{} v3.8h, v14.8h, v11.8b', 0, ()),
    ('6e2b31c3', 'usubw{2} v3.8h, v14.8h, v11.16b', 0, ()),
    ('2e6b31c3', 'usubw{} v3.4s, v14.4s, v11.4h', 0, ()),
    ('6e6b31c3', 'usubw{2} v3.4s, v14.4s, v11.8h', 0, ()),
    ('2eab31c3', 'usubw{} v3.2d, v14.2d, v11.2s', 0, ()),
    ('6eab31c3', 'usubw{2} v3.2d, v14.2d, v11.4s', 0, ()),
    #raddhn
    ('2e2b41c3', 'raddhn{} v3.8b, v14.8h, v11.8h', 0, ()),
    ('6e2b41c3', 'raddhn{2} v3.16b, v14.8h, v11.8h', 0, ()),
    ('2e6b41c3', 'raddhn{} v3.4h, v14.4s, v11.4s', 0, ()),
    ('6e6b41c3', 'raddhn{2} v3.8h, v14.4s, v11.4s', 0, ()),
    ('2eab41c3', 'raddhn{} v3.2s, v14.2d, v11.2d', 0, ()),
    ('6eab41c3', 'raddhn{2} v3.4s, v14.2d, v11.2d', 0, ()),
    #uabal
    ('2e2b51c3', 'uabal{} v3.8h, v14.8b, v11.8b', 0, ()),
    ('6e2b51c3', 'uabal{2} v3.8h, v14.16b, v11.16b', 0, ()),
    ('2e6b51c3', 'uabal{} v3.4s, v14.4h, v11.4h', 0, ()),
    ('6e6b51c3', 'uabal{2} v3.4s, v14.8h, v11.8h', 0, ()),
    ('2eab51c3', 'uabal{} v3.2d, v14.2s, v11.2s', 0, ()),
    ('6eab51c3', 'uabal{2} v3.2d, v14.4s, v11.4s', 0, ()),
    #rsubhn
    ('2e2b61c3', 'rsubhn{} v3.8b, v14.8h, v11.8h', 0, ()),
    ('6e2b61c3', 'rsubhn{2} v3.16b, v14.8h, v11.8h', 0, ()),
    ('2e6b61c3', 'rsubhn{} v3.4h, v14.4s, v11.4s', 0, ()),
    ('6e6b61c3', 'rsubhn{2} v3.8h, v14.4s, v11.4s', 0, ()),
    ('2eab61c3', 'rsubhn{} v3.2s, v14.2d, v11.2d', 0, ()),
    ('6eab61c3', 'rsubhn{2} v3.4s, v14.2d, v11.2d', 0, ()),
    #uabdl
    ('2e2b71c3', 'uabdl{} v3.8h, v14.8b, v11.8b', 0, ()),
    ('6e2b71c3', 'uabdl{2} v3.8h, v14.16b, v11.16b', 0, ()),
    ('2e6b71c3', 'uabdl{} v3.4s, v14.4h, v11.4h', 0, ()),
    ('6e6b71c3', 'uabdl{2} v3.4s, v14.8h, v11.8h', 0, ()),
    ('2eab71c3', 'uabdl{} v3.2d, v14.2s, v11.2s', 0, ()),
    ('6eab71c3', 'uabdl{2} v3.2d, v14.4s, v11.4s', 0, ()),
    #umlal
    ('2e2b81c3', 'umlal{} v3.8h, v14.8b, v11.8b', 0, ()),
    ('6e2b81c3', 'umlal{2} v3.8h, v14.16b, v11.16b', 0, ()),
    ('2e6b81c3', 'umlal{} v3.4s, v14.4h, v11.4h', 0, ()),
    ('6e6b81c3', 'umlal{2} v3.4s, v14.8h, v11.8h', 0, ()),
    ('2eab81c3', 'umlal{} v3.2d, v14.2s, v11.2s', 0, ()),
    ('6eab81c3', 'umlal{2} v3.2d, v14.4s, v11.4s', 0, ()),
    #umlsl
    ('2e2ba1c3', 'umlsl{} v3.8h, v14.8b, v11.8b', 0, ()),
    ('6e2ba1c3', 'umlsl{2} v3.8h, v14.16b, v11.16b', 0, ()),
    ('2e6ba1c3', 'umlsl{} v3.4s, v14.4h, v11.4h', 0, ()),
    ('6e6ba1c3', 'umlsl{2} v3.4s, v14.8h, v11.8h', 0, ()),
    ('2eaba1c3', 'umlsl{} v3.2d, v14.2s, v11.2s', 0, ()),
    ('6eaba1c3', 'umlsl{2} v3.2d, v14.4s, v11.4s', 0, ()),
    #umull
    ('2e2bc1c3', 'umull{} v3.8h, v14.8b, v11.8b', 0, ()),
    ('6e2bc1c3', 'umull{2} v3.8h, v14.16b, v11.16b', 0, ()),
    ('2e6bc1c3', 'umull{} v3.4s, v14.4h, v11.4h', 0, ()),
    ('6e6bc1c3', 'umull{2} v3.4s, v14.8h, v11.8h', 0, ()),
    ('2eabc1c3', 'umull{} v3.2d, v14.2s, v11.2s', 0, ()),
    ('6eabc1c3', 'umull{2} v3.2d, v14.4s, v11.4s', 0, ()),

    #AdvSIMD two-reg misc

    #instructions with u == 0
    #instructions with size == xx
    #rev64
    ('0e2009c3', 'rev64 v3.8b, v14.8b', 0, ()),
    ('4e2009c3', 'rev64 v3.16b, v14.16b', 0, ()),
    ('0e6009c3', 'rev64 v3.4h, v14.4h', 0, ()),
    ('4e6009c3', 'rev64 v3.8h, v14.8h', 0, ()),
    ('0ea009c3', 'rev64 v3.2s, v14.2s', 0, ()),
    ('4ea009c3', 'rev64 v3.4s, v14.4s', 0, ()),
    #rev16 (vector)
    ('0e2019c3', 'rev16 v3.8b, v14.8b', 0, ()),
    ('4e2019c3', 'rev16 v3.16b, v14.16b', 0, ()),
    #saddlp
    ('0e2029c3', 'saddlp v3.4h, v14.8b', 0, ()),
    ('4e2029c3', 'saddlp v3.8h, v14.16b', 0, ()),
    ('0e6029c3', 'saddlp v3.2s, v14.4h', 0, ()),
    ('4e6029c3', 'saddlp v3.4s, v14.8h', 0, ()),
    ('0ea029c3', 'saddlp v3.1d, v14.2s', 0, ()),
    ('4ea029c3', 'saddlp v3.2d, v14.4s', 0, ()),
    #suqadd
    ('0e2039c3', 'suqadd v3.8b, v14.8b', 0, ()),
    ('4e2039c3', 'suqadd v3.16b, v14.16b', 0, ()),
    ('0e6039c3', 'suqadd v3.4h, v14.4h', 0, ()),
    ('4e6039c3', 'suqadd v3.8h, v14.8h', 0, ()),
    ('0ea039c3', 'suqadd v3.2s, v14.2s', 0, ()),
    ('4ea039c3', 'suqadd v3.4s, v14.4s', 0, ()),
    ('4ee039c3', 'suqadd v3.2d, v14.2d', 0, ()),
    #cls (vector)
    ('0e2049c3', 'cls v3.8b, v14.8b', 0, ()),
    ('4e2049c3', 'cls v3.16b, v14.16b', 0, ()),
    ('0e6049c3', 'cls v3.4h, v14.4h', 0, ()),
    ('4e6049c3', 'cls v3.8h, v14.8h', 0, ()),
    ('0ea049c3', 'cls v3.2s, v14.2s', 0, ()),
    ('4ea049c3', 'cls v3.4s, v14.4s', 0, ()),
    #cnt
    ('0e2059c3', 'cnt v3.8b, v14.8b', 0, ()),
    ('4e2059c3', 'cnt v3.16b, v14.16b', 0, ()),
    #sadalp
    ('0e2069c3', 'sadalp v3.4h, v14.8b', 0, ()),
    ('4e2069c3', 'sadalp v3.8h, v14.16b', 0, ()),
    ('0e6069c3', 'sadalp v3.2s, v14.4h', 0, ()),
    ('4e6069c3', 'sadalp v3.4s, v14.8h', 0, ()),
    ('0ea069c3', 'sadalp v3.1d, v14.2s', 0, ()),
    ('4ea069c3', 'sadalp v3.2d, v14.4s', 0, ()),
    #sqabs
    ('0e2079c3', 'sqabs v3.8b, v14.8b', 0, ()),
    ('4e2079c3', 'sqabs v3.16b, v14.16b', 0, ()),
    ('0e6079c3', 'sqabs v3.4h, v14.4h', 0, ()),
    ('4e6079c3', 'sqabs v3.8h, v14.8h', 0, ()),
    ('0ea079c3', 'sqabs v3.2s, v14.2s', 0, ()),
    ('4ea079c3', 'sqabs v3.4s, v14.4s', 0, ()),
    ('4ee079c3', 'sqabs v3.2d, v14.2d', 0, ()),
    #cmgt (zero)
    ('0e2089c3', 'cmgt v3.8b, v14.8b, #0', 0, ()),
    ('4e2089c3', 'cmgt v3.16b, v14.16b, #0', 0, ()),
    ('0e6089c3', 'cmgt v3.4h, v14.4h, #0', 0, ()),
    ('4e6089c3', 'cmgt v3.8h, v14.8h, #0', 0, ()),
    ('0ea089c3', 'cmgt v3.2s, v14.2s, #0', 0, ()),
    ('4ea089c3', 'cmgt v3.4s, v14.4s, #0', 0, ()),
    ('4ee089c3', 'cmgt v3.2d, v14.2d, #0', 0, ()),
    #cmeq (zero)
    ('0e2099c3', 'cmeq v3.8b, v14.8b, #0', 0, ()),
    ('4e2099c3', 'cmeq v3.16b, v14.16b, #0', 0, ()),
    ('0e6099c3', 'cmeq v3.4h, v14.4h, #0', 0, ()),
    ('4e6099c3', 'cmeq v3.8h, v14.8h, #0', 0, ()),
    ('0ea099c3', 'cmeq v3.2s, v14.2s, #0', 0, ()),
    ('4ea099c3', 'cmeq v3.4s, v14.4s, #0', 0, ()),
    ('4ee099c3', 'cmeq v3.2d, v14.2d, #0', 0, ()),
    #cmlt (zero)
    ('0e20a9c3', 'cmlt v3.8b, v14.8b, #0', 0, ()),
    ('4e20a9c3', 'cmlt v3.16b, v14.16b, #0', 0, ()),
    ('0e60a9c3', 'cmlt v3.4h, v14.4h, #0', 0, ()),
    ('4e60a9c3', 'cmlt v3.8h, v14.8h, #0', 0, ()),
    ('0ea0a9c3', 'cmlt v3.2s, v14.2s, #0', 0, ()),
    ('4ea0a9c3', 'cmlt v3.4s, v14.4s, #0', 0, ()),
    ('4ee0a9c3', 'cmlt v3.2d, v14.2d, #0', 0, ()),
    #abs
    ('0e20b9c3', 'abs v3.8b, v14.8b', 0, ()),
    ('4e20b9c3', 'abs v3.16b, v14.16b', 0, ()),
    ('0e60b9c3', 'abs v3.4h, v14.4h', 0, ()),
    ('4e60b9c3', 'abs v3.8h, v14.8h', 0, ()),
    ('0ea0b9c3', 'abs v3.2s, v14.2s', 0, ()),
    ('4ea0b9c3', 'abs v3.4s, v14.4s', 0, ()),
    ('4ee0b9c3', 'abs v3.2d, v14.2d', 0, ()),
    #xtn
    ('0e2129c3', 'xtn{} v3.8b, v14.8h', 0, ()),
    ('4e2129c3', 'xtn{2} v3.16b, v14.8h', 0, ()),
    ('0e6129c3', 'xtn{} v3.4h, v14.4s', 0, ()),
    ('4e6129c3', 'xtn{2} v3.8h, v14.4s', 0, ()),
    ('0ea129c3', 'xtn{} v3.2s, v14.2d', 0, ()),
    ('4ea129c3', 'xtn{2} v3.4s, v14.2d', 0, ()),
    #sqxtn
    ('0e2149c3', 'sqxtn{} v3.8b, v14.8h', 0, ()),
    ('4e2149c3', 'sqxtn{2} v3.16b, v14.8h', 0, ()),
    ('0e6149c3', 'sqxtn{} v3.4h, v14.4s', 0, ()),
    ('4e6149c3', 'sqxtn{2} v3.8h, v14.4s', 0, ()),
    ('0ea149c3', 'sqxtn{} v3.2s, v14.2d', 0, ()),
    ('4ea149c3', 'sqxtn{2} v3.4s, v14.2d', 0, ()),
    #instructions with size == 0x
    #fcvtn
    ('0e2169c3', 'fcvtn{} v3.4h, v14.4s', 0, ()),
    ('4e2169c3', 'fcvtn{2} v3.8h, v14.4s', 0, ()),
    ('0e6169c3', 'fcvtn{} v3.2s, v14.2d', 0, ()),
    ('4e6169c3', 'fcvtn{2} v3.4s, v14.2d', 0, ()),
    #fcvtl
    ('0e2179c3', 'fcvtl{} v3.4h, v14.4s', 0, ()),
    ('4e2179c3', 'fcvtl{2} v3.8h, v14.4s', 0, ()),
    ('0e6179c3', 'fcvtl{} v3.2s, v14.2d', 0, ()),
    ('4e6179c3', 'fcvtl{2} v3.4s, v14.2d', 0, ()),
    #frintn
    ('0e2189c3', 'frintn v3.2s, v14.2s', 0, ()),
    ('4e2189c3', 'frintn v3.4s, v14.4s', 0, ()),
    ('4e6189c3', 'frintn v3.2d, v14.2d', 0, ()),
    #frintm
    ('0e2199c3', 'frintm v3.2s, v14.2s', 0, ()),
    ('4e2199c3', 'frintm v3.4s, v14.4s', 0, ()),
    ('4e6199c3', 'frintm v3.2d, v14.2d', 0, ()),
    #fcvtns
    ('0e21a9c3', 'fcvtns v3.2s, v14.2s', 0, ()),
    ('4e21a9c3', 'fcvtns v3.4s, v14.4s', 0, ()),
    ('4e61a9c3', 'fcvtns v3.2d, v14.2d', 0, ()),
    #fcvtms
    ('0e21b9c3', 'fcvtms v3.2s, v14.2s', 0, ()),
    ('4e21b9c3', 'fcvtms v3.4s, v14.4s', 0, ()),
    ('4e61b9c3', 'fcvtms v3.2d, v14.2d', 0, ()),
    #fcvtas
    ('0e21c9c3', 'fcvtas v3.2s, v14.2s', 0, ()),
    ('4e21c9c3', 'fcvtas v3.4s, v14.4s', 0, ()),
    ('4e61c9c3', 'fcvtas v3.2d, v14.2d', 0, ()),
    #scvtf
    ('0e21d9c3', 'scvtf v3.2s, v14.2s', 0, ()),
    ('4e21d9c3', 'scvtf v3.4s, v14.4s', 0, ()),
    ('4e61d9c3', 'scvtf v3.2d, v14.2d', 0, ()),
    #instructions with size == 1x
    #fcmgt (zero)
    ('0ea0c9c3', 'fcmgt v3.2s, v14.2s, #0', 0, ()),
    ('4ea0c9c3', 'fcmgt v3.4s, v14.4s, #0', 0, ()),
    ('4ee0c9c3', 'fcmgt v3.2d, v14.2d, #0', 0, ()),
    #fcmeq (zero)
    ('0ea0d9c3', 'fcmeq v3.2s, v14.2s, #0', 0, ()),
    ('4ea0d9c3', 'fcmeq v3.4s, v14.4s, #0', 0, ()),
    ('4ee0d9c3', 'fcmeq v3.2d, v14.2d, #0', 0, ()),
    #fcmlt (zero)
    ('0ea0e9c3', 'fcmlt v3.2s, v14.2s, #0', 0, ()),
    ('4ea0e9c3', 'fcmlt v3.4s, v14.4s, #0', 0, ()),
    ('4ee0e9c3', 'fcmlt v3.2d, v14.2d, #0', 0, ()),
    #fabs (vector)
    ('0ea0f9c3', 'fabs v3.2s, v14.2s', 0, ()),
    ('4ea0f9c3', 'fabs v3.4s, v14.4s', 0, ()),
    ('4ee0f9c3', 'fabs v3.2d, v14.2d', 0, ()),
    #frintp (vector)
    ('0ea189c3', 'frintp v3.2s, v14.2s', 0, ()),
    ('4ea189c3', 'frintp v3.4s, v14.4s', 0, ()),
    ('4ee189c3', 'frintp v3.2d, v14.2d', 0, ()),
    #frintz (vector)
    ('0ea199c3', 'frintz v3.2s, v14.2s', 0, ()),
    ('4ea199c3', 'frintz v3.4s, v14.4s', 0, ()),
    ('4ee199c3', 'frintz v3.2d, v14.2d', 0, ()),
    #fcvtps (vector)
    ('0ea1a9c3', 'fcvtps v3.2s, v14.2s', 0, ()),
    ('4ea1a9c3', 'fcvtps v3.4s, v14.4s', 0, ()),
    ('4ee1a9c3', 'fcvtps v3.2d, v14.2d', 0, ()),
    #fcvtzs (vector, integer)
    ('0ea1b9c3', 'fcvtzs v3.2s, v14.2s', 0, ()),
    ('4ea1b9c3', 'fcvtzs v3.4s, v14.4s', 0, ()),
    ('4ee1b9c3', 'fcvtzs v3.2d, v14.2d', 0, ()),
    #urecpe
    ('0ea1c9c3', 'urecpe v3.2s, v14.2s', 0, ()),
    ('4ea1c9c3', 'urecpe v3.4s, v14.4s', 0, ()),
    #frecpe
    ('0ea1d9c3', 'frecpe v3.2s, v14.2s', 0, ()),
    ('4ea1d9c3', 'frecpe v3.4s, v14.4s', 0, ()),
    ('4ee1d9c3', 'frecpe v3.2d, v14.2d', 0, ()),
    #instructions with u == 1
    #instructions with size == xx
    #rev32 (vector)
    ('2e2009c3', 'rev32 v3.8b, v14.8b', 0, ()),
    ('6e2009c3', 'rev32 v3.16b, v14.16b', 0, ()),
    ('2e6009c3', 'rev32 v3.4h, v14.4h', 0, ()),
    ('6e6009c3', 'rev32 v3.8h, v14.8h', 0, ()),
    #uaddlp
    ('2e2029c3', 'uaddlp v3.4h, v14.8b', 0, ()),
    ('6e2029c3', 'uaddlp v3.8h, v14.16b', 0, ()),
    ('2e6029c3', 'uaddlp v3.2s, v14.4h', 0, ()),
    ('6e6029c3', 'uaddlp v3.4s, v14.8h', 0, ()),
    ('2ea029c3', 'uaddlp v3.1d, v14.2s', 0, ()),
    ('6ea029c3', 'uaddlp v3.2d, v14.4s', 0, ()),
    #usqadd
    ('2e2039c3', 'usqadd v3.8b, v14.8b', 0, ()),
    ('6e2039c3', 'usqadd v3.16b, v14.16b', 0, ()),
    ('2e6039c3', 'usqadd v3.4h, v14.4h', 0, ()),
    ('6e6039c3', 'usqadd v3.8h, v14.8h', 0, ()),
    ('2ea039c3', 'usqadd v3.2s, v14.2s', 0, ()),
    ('6ea039c3', 'usqadd v3.4s, v14.4s', 0, ()),
    ('6ee039c3', 'usqadd v3.2d, v14.2d', 0, ()),
    #clz (vector)
    ('2e2049c3', 'clz v3.8b, v14.8b', 0, ()),
    ('6e2049c3', 'clz v3.16b, v14.16b', 0, ()),
    ('2e6049c3', 'clz v3.4h, v14.4h', 0, ()),
    ('6e6049c3', 'clz v3.8h, v14.8h', 0, ()),
    ('2ea049c3', 'clz v3.2s, v14.2s', 0, ()),
    ('6ea049c3', 'clz v3.4s, v14.4s', 0, ()),
    #uadalp
    ('2e2069c3', 'uadalp v3.4h, v14.8b', 0, ()),
    ('6e2069c3', 'uadalp v3.8h, v14.16b', 0, ()),
    ('2e6069c3', 'uadalp v3.2s, v14.4h', 0, ()),
    ('6e6069c3', 'uadalp v3.4s, v14.8h', 0, ()),
    ('2ea069c3', 'uadalp v3.1d, v14.2s', 0, ()),
    ('6ea069c3', 'uadalp v3.2d, v14.4s', 0, ()),
    #sqneg
    ('2e2079c3', 'sqneg v3.8b, v14.8b', 0, ()),
    ('6e2079c3', 'sqneg v3.16b, v14.16b', 0, ()),
    ('2e6079c3', 'sqneg v3.4h, v14.4h', 0, ()),
    ('6e6079c3', 'sqneg v3.8h, v14.8h', 0, ()),
    ('2ea079c3', 'sqneg v3.2s, v14.2s', 0, ()),
    ('6ea079c3', 'sqneg v3.4s, v14.4s', 0, ()),
    ('6ee079c3', 'sqneg v3.2d, v14.2d', 0, ()),
    #cmge (zero)
    ('2e2089c3', 'cmge v3.8b, v14.8b, #0', 0, ()),
    ('6e2089c3', 'cmge v3.16b, v14.16b, #0', 0, ()),
    ('2e6089c3', 'cmge v3.4h, v14.4h, #0', 0, ()),
    ('6e6089c3', 'cmge v3.8h, v14.8h, #0', 0, ()),
    ('2ea089c3', 'cmge v3.2s, v14.2s, #0', 0, ()),
    ('6ea089c3', 'cmge v3.4s, v14.4s, #0', 0, ()),
    ('6ee089c3', 'cmge v3.2d, v14.2d, #0', 0, ()),
    #cmle (zero)
    ('2e2099c3', 'cmle v3.8b, v14.8b, #0', 0, ()),
    ('6e2099c3', 'cmle v3.16b, v14.16b, #0', 0, ()),
    ('2e6099c3', 'cmle v3.4h, v14.4h, #0', 0, ()),
    ('6e6099c3', 'cmle v3.8h, v14.8h, #0', 0, ()),
    ('2ea099c3', 'cmle v3.2s, v14.2s, #0', 0, ()),
    ('6ea099c3', 'cmle v3.4s, v14.4s, #0', 0, ()),
    ('6ee099c3', 'cmle v3.2d, v14.2d, #0', 0, ()),
    #neg (vector)
    ('2e20b9c3', 'neg v3.8b, v14.8b', 0, ()),
    ('6e20b9c3', 'neg v3.16b, v14.16b', 0, ()),
    ('2e60b9c3', 'neg v3.4h, v14.4h', 0, ()),
    ('6e60b9c3', 'neg v3.8h, v14.8h', 0, ()),
    ('2ea0b9c3', 'neg v3.2s, v14.2s', 0, ()),
    ('6ea0b9c3', 'neg v3.4s, v14.4s', 0, ()),
    ('6ee0b9c3', 'neg v3.2d, v14.2d', 0, ()),
    #sqxtun
    ('2e2129c3', 'sqxtun{} v3.8b, v14.8h', 0, ()),
    ('6e2129c3', 'sqxtun{2} v3.16b, v14.8h', 0, ()),
    ('2e6129c3', 'sqxtun{} v3.4h, v14.4s', 0, ()),
    ('6e6129c3', 'sqxtun{2} v3.8h, v14.4s', 0, ()),
    ('2ea129c3', 'sqxtun{} v3.2s, v14.2d', 0, ()),
    ('6ea129c3', 'sqxtun{2} v3.4s, v14.2d', 0, ()),
    #shll
    ('2e2139c3', 'shll{} v3.8h, v14.8b, #8', 0, ()),
    ('6e2139c3', 'shll{2} v3.8h, v14.16b, #8', 0, ()),
    ('2e6139c3', 'shll{} v3.4s, v14.4h, #16', 0, ()),
    ('6e6139c3', 'shll{2} v3.4s, v14.8h, #16', 0, ()),
    ('2ea139c3', 'shll{} v3.2d, v14.2s, #32', 0, ()),
    ('6ea139c3', 'shll{2} v3.2d, v14.4s, #32', 0, ()),    
    #uqxtn
    ('2e2149c3', 'uqxtn{} v3.8b, v14.8h', 0, ()),
    ('6e2149c3', 'uqxtn{2} v3.16b, v14.8h', 0, ()),
    ('2e6149c3', 'uqxtn{} v3.4h, v14.4s', 0, ()),
    ('6e6149c3', 'uqxtn{2} v3.8h, v14.4s', 0, ()),
    ('2ea149c3', 'uqxtn{} v3.2s, v14.2d', 0, ()),
    ('6ea149c3', 'uqxtn{2} v3.4s, v14.2d', 0, ()),
    #instructions with size == 0x
    #fcvtxn
    ('2e6169c3', 'fcvtxn{} v3.2s, v14.2d', 0, ()),
    ('6e6169c3', 'fcvtxn{2} v3.4s, v14.2d', 0, ()),
    #frinta
    ('2e2189c3', 'frinta v3.2s, v14.2s', 0, ()),
    ('6e2189c3', 'frinta v3.4s, v14.4s', 0, ()),
    ('6e6189c3', 'frinta v3.2d, v14.2d', 0, ()),
    #frintx
    ('2e2199c3', 'frintx v3.2s, v14.2s', 0, ()),
    ('6e2199c3', 'frintx v3.4s, v14.4s', 0, ()),
    ('6e6199c3', 'frintx v3.2d, v14.2d', 0, ()),
    #fcvtnu
    ('2e21a9c3', 'fcvtnu v3.2s, v14.2s', 0, ()),
    ('6e21a9c3', 'fcvtnu v3.4s, v14.4s', 0, ()),
    ('6e61a9c3', 'fcvtnu v3.2d, v14.2d', 0, ()),
    #fcvtmu
    ('2e21b9c3', 'fcvtmu v3.2s, v14.2s', 0, ()),
    ('6e21b9c3', 'fcvtmu v3.4s, v14.4s', 0, ()),
    ('6e61b9c3', 'fcvtmu v3.2d, v14.2d', 0, ()),
    #fcvtau
    ('2e21c9c3', 'fcvtau v3.2s, v14.2s', 0, ()),
    ('6e21c9c3', 'fcvtau v3.4s, v14.4s', 0, ()),
    ('6e61c9c3', 'fcvtau v3.2d, v14.2d', 0, ()),
    #ucvtf
    ('2e21d9c3', 'ucvtf v3.2s, v14.2s', 0, ()),
    ('6e21d9c3', 'ucvtf v3.4s, v14.4s', 0, ()),
    ('6e61d9c3', 'ucvtf v3.2d, v14.2d', 0, ()),
    #not (size == 00)
    ('2e2059c3', 'not v3.8b, v14.8b', 0, ()),
    ('6e2059c3', 'not v3.16b, v14.16b', 0, ()),
    #rbit (vector) (size == 01)
    ('2e6059c3', 'rbit v3.8b, v14.8b', 0, ()),
    ('6e6059c3', 'rbit v3.16b, v14.16b', 0, ()),    
    #instructions with size == 1x
    #fcmge (zero)
    ('2ea0c9c3', 'fcmge v3.2s, v14.2s, #0', 0, ()),
    ('6ea0c9c3', 'fcmge v3.4s, v14.4s, #0', 0, ()),
    ('6ee0c9c3', 'fcmge v3.2d, v14.2d, #0', 0, ()),
    #fcmle (zero)
    ('2ea0d9c3', 'fcmle v3.2s, v14.2s, #0', 0, ()),
    ('6ea0d9c3', 'fcmle v3.4s, v14.4s, #0', 0, ()),
    ('6ee0d9c3', 'fcmle v3.2d, v14.2d, #0', 0, ()),
    #fneg (vector)
    ('2ea0f9c3', 'fneg v3.2s, v14.2s', 0, ()),
    ('6ea0f9c3', 'fneg v3.4s, v14.4s', 0, ()),
    ('6ee0f9c3', 'fneg v3.2d, v14.2d', 0, ()),
    #frinti (vector)
    ('2ea199c3', 'frinti v3.2s, v14.2s', 0, ()),
    ('6ea199c3', 'frinti v3.4s, v14.4s', 0, ()),
    ('6ee199c3', 'frinti v3.2d, v14.2d', 0, ()),
    #fcvtpu (vector)
    ('2ea1a9c3', 'fcvtpu v3.2s, v14.2s', 0, ()),
    ('6ea1a9c3', 'fcvtpu v3.4s, v14.4s', 0, ()),
    ('6ee1a9c3', 'fcvtpu v3.2d, v14.2d', 0, ()),
    #fcvtzu (vector, integer)
    ('2ea1b9c3', 'fcvtzu v3.2s, v14.2s', 0, ()),
    ('6ea1b9c3', 'fcvtzu v3.4s, v14.4s', 0, ()),
    ('6ee1b9c3', 'fcvtzu v3.2d, v14.2d', 0, ()),
    #ursqrte
    ('2ea1c9c3', 'ursqrte v3.2s, v14.2s', 0, ()),
    ('6ea1c9c3', 'ursqrte v3.4s, v14.4s', 0, ()),
    #frsqrte
    ('2ea1d9c3', 'frsqrte v3.2s, v14.2s', 0, ()),
    ('6ea1d9c3', 'frsqrte v3.4s, v14.4s', 0, ()),
    ('6ee1d9c3', 'frsqrte v3.2d, v14.2d', 0, ()),
    #fsqrt (vector)
    ('2ea1f9c3', 'frsqrt v3.2s, v14.2s', 0, ()),
    ('6ea1f9c3', 'frsqrt v3.4s, v14.4s', 0, ()),
    ('6ee1f9c3', 'frsqrt v3.2d, v14.2d', 0, ()),
    
    #AdvSIMD across lanes

    #saddlv
    ('0e3039c3', 'saddlv h3, v14.8b', 0, ()),
    ('4e3039c3', 'saddlv h3, v14.16b', 0, ()),
    ('0e7039c3', 'saddlv s3, v14.4h', 0, ()),
    ('4e7039c3', 'saddlv s3, v14.8h', 0, ()),
    ('4eb039c3', 'saddlv d3, v14.4s', 0, ()),
    #smaxv
    ('0e30a9c3', 'smaxv b3, v14.8b', 0, ()),
    ('4e30a9c3', 'smaxv b3, v14.16b', 0, ()),
    ('0e70a9c3', 'smaxv h3, v14.4h', 0, ()),
    ('4e70a9c3', 'smaxv h3, v14.8h', 0, ()),
    ('4eb0a9c3', 'smaxv s3, v14.4s', 0, ()),
    #sminv
    ('0e31a9c3', 'sminv b3, v14.8b', 0, ()),
    ('4e31a9c3', 'sminv b3, v14.16b', 0, ()),
    ('0e71a9c3', 'sminv h3, v14.4h', 0, ()),
    ('4e71a9c3', 'sminv h3, v14.8h', 0, ()),
    ('4eb1a9c3', 'sminv s3, v14.4s', 0, ()),
    #addv
    ('0e31b9c3', 'addv b3, v14.8b', 0, ()),
    ('4e31b9c3', 'addv b3, v14.16b', 0, ()),
    ('0e71b9c3', 'addv h3, v14.4h', 0, ()),
    ('4e71b9c3', 'addv h3, v14.8h', 0, ()),
    ('4eb1b9c3', 'addv s3, v14.4s', 0, ()),
    #uaddlv
    ('2e3039c3', 'uaddlv h3, v14.8b', 0, ()),
    ('6e3039c3', 'uaddlv h3, v14.16b', 0, ()),
    ('2e7039c3', 'uaddlv s3, v14.4h', 0, ()),
    ('6e7039c3', 'uaddlv s3, v14.8h', 0, ()),
    ('6eb039c3', 'uaddlv d3, v14.4s', 0, ()),
    #umaxv
    ('2e30a9c3', 'umaxv b3, v14.8b', 0, ()),
    ('6e30a9c3', 'umaxv b3, v14.16b', 0, ()),
    ('2e70a9c3', 'umaxv h3, v14.4h', 0, ()),
    ('6e70a9c3', 'umaxv h3, v14.8h', 0, ()),
    ('6eb0a9c3', 'umaxv s3, v14.4s', 0, ()),
    #uminv
    ('2e31a9c3', 'uminv b3, v14.8b', 0, ()),
    ('6e31a9c3', 'uminv b3, v14.16b', 0, ()),
    ('2e71a9c3', 'uminv h3, v14.4h', 0, ()),
    ('6e71a9c3', 'uminv h3, v14.8h', 0, ()),
    ('6eb1a9c3', 'uminv s3, v14.4s', 0, ()),
    #fmaxnmv
    ('6e30c9c3', 'fmaxnmv s3, v14.4s', 0, ()),
    #fmaxv
    ('6e30f9c3', 'fmaxv s3, v14.4s', 0, ()),
    #fminnmv
    ('6eb0c9c3', 'fminnmv s3, v14.4s', 0, ()),
    #fminv
    ('6eb0f9c3', 'fminv s3, v14.4s', 0, ()),

    #

    #dup (element)
    ('0e0105c3', 'dup v3.8b, v14.b[0]', 0, ()),
    ('0e0205c3', 'dup v3.4h, v14.h[0]', 0, ()),
    ('0e0305c3', 'dup v3.8b, v14.b[1]', 0, ()),
    ('0e0405c3', 'dup v3.2s, v14.s[0]', 0, ()),
    ('0e0505c3', 'dup v3.8b, v14.b[2]', 0, ()),
    ('0e0605c3', 'dup v3.4h, v14.h[1]', 0, ()),
    ('0e0705c3', 'dup v3.8b, v14.b[3]', 0, ()),
    ('0e0905c3', 'dup v3.8b, v14.b[4]', 0, ()),
    ('0e0a05c3', 'dup v3.4h, v14.h[2]', 0, ()),
    ('0e0b05c3', 'dup v3.8b, v14.b[5]', 0, ()),
    ('0e0c05c3', 'dup v3.2s, v14.s[1]', 0, ()),
    ('0e0d05c3', 'dup v3.8b, v14.b[6]', 0, ()),
    ('0e0e05c3', 'dup v3.4h, v14.h[3]', 0, ()),
    ('0e0f05c3', 'dup v3.8b, v14.b[7]', 0, ()),
    ('0e1105c3', 'dup v3.8b, v14.b[8]', 0, ()),
    ('0e1205c3', 'dup v3.4h, v14.h[4]', 0, ()),
    ('0e1305c3', 'dup v3.8b, v14.b[9]', 0, ()),
    ('0e1405c3', 'dup v3.2s, v14.s[2]', 0, ()),
    ('0e1505c3', 'dup v3.8b, v14.b[10]', 0, ()),
    ('0e1605c3', 'dup v3.4h, v14.h[5]', 0, ()),
    ('0e1705c3', 'dup v3.8b, v14.b[11]', 0, ()),
    ('0e1905c3', 'dup v3.8b, v14.b[12]', 0, ()),
    ('0e1a05c3', 'dup v3.4h, v14.h[6]', 0, ()),
    ('0e1b05c3', 'dup v3.8b, v14.b[13]', 0, ()),
    ('0e1c05c3', 'dup v3.2s, v14.s[3]', 0, ()),
    ('0e1d05c3', 'dup v3.8b, v14.b[14]', 0, ()),
    ('0e1e05c3', 'dup v3.4h, v14.h[7]', 0, ()),
    ('0e1f05c3', 'dup v3.8b, v14.b[15]', 0, ()),
    ('4e0105c3', 'dup v3.16b, v14.b[0]', 0, ()),
    ('4e0205c3', 'dup v3.8h, v14.h[0]', 0, ()),
    ('4e0305c3', 'dup v3.16b, v14.b[1]', 0, ()),
    ('4e0405c3', 'dup v3.4s, v14.s[0]', 0, ()),
    ('4e0505c3', 'dup v3.16b, v14.b[2]', 0, ()),
    ('4e0605c3', 'dup v3.8h, v14.h[1]', 0, ()),
    ('4e0705c3', 'dup v3.16b, v14.b[3]', 0, ()),
    ('4e0805c3', 'dup v3.2d, v14.d[0]', 0, ()),
    ('4e0905c3', 'dup v3.16b, v14.b[4]', 0, ()),
    ('4e0a05c3', 'dup v3.8h, v14.h[2]', 0, ()),
    ('4e0b05c3', 'dup v3.16b, v14.b[5]', 0, ()),
    ('4e0c05c3', 'dup v3.4s, v14.s[1]', 0, ()),
    ('4e0d05c3', 'dup v3.16b, v14.b[6]', 0, ()),
    ('4e0e05c3', 'dup v3.8h, v14.h[3]', 0, ()),
    ('4e0f05c3', 'dup v3.16b, v14.b[7]', 0, ()),
    ('4e1105c3', 'dup v3.16b, v14.b[8]', 0, ()),
    ('4e1205c3', 'dup v3.8h, v14.h[4]', 0, ()),
    ('4e1305c3', 'dup v3.16b, v14.b[9]', 0, ()),
    ('4e1405c3', 'dup v3.4s, v14.s[2]', 0, ()),
    ('4e1505c3', 'dup v3.16b, v14.b[10]', 0, ()),
    ('4e1605c3', 'dup v3.8h, v14.h[5]', 0, ()),
    ('4e1705c3', 'dup v3.16b, v14.b[11]', 0, ()),
    ('4e1805c3', 'dup v3.2d, v14.d[1]', 0, ()),
    ('4e1905c3', 'dup v3.16b, v14.b[12]', 0, ()),
    ('4e1a05c3', 'dup v3.8h, v14.h[6]', 0, ()),
    ('4e1b05c3', 'dup v3.16b, v14.b[13]', 0, ()),
    ('4e1c05c3', 'dup v3.4s, v14.s[3]', 0, ()),
    ('4e1d05c3', 'dup v3.16b, v14.b[14]', 0, ()),
    ('4e1e05c3', 'dup v3.8h, v14.h[7]', 0, ()),
    ('4e1f05c3', 'dup v3.16b, v14.b[15]', 0, ()),
    #dup (general)
    ('0e010dc3', 'dup v3.8b, w14', 0, ()),
    ('0e020dc3', 'dup v3.4h, w14', 0, ()),
    ('0e030dc3', 'dup v3.8b, w14', 0, ()),
    ('0e040dc3', 'dup v3.2s, w14', 0, ()),
    ('0e050dc3', 'dup v3.8b, w14', 0, ()),
    ('0e060dc3', 'dup v3.4h, w14', 0, ()),
    ('0e070dc3', 'dup v3.8b, w14', 0, ()),
    ('0e090dc3', 'dup v3.8b, w14', 0, ()),
    ('0e0a0dc3', 'dup v3.4h, w14', 0, ()),
    ('0e0b0dc3', 'dup v3.8b, w14', 0, ()),
    ('0e0c0dc3', 'dup v3.2s, w14', 0, ()),
    ('0e0d0dc3', 'dup v3.8b, w14', 0, ()),
    ('0e0e0dc3', 'dup v3.4h, w14', 0, ()),
    ('0e0f0dc3', 'dup v3.8b, w14', 0, ()),
    ('0e110dc3', 'dup v3.8b, w14', 0, ()),
    ('0e120dc3', 'dup v3.4h, w14', 0, ()),
    ('0e130dc3', 'dup v3.8b, w14', 0, ()),
    ('0e140dc3', 'dup v3.2s, w14', 0, ()),
    ('0e150dc3', 'dup v3.8b, w14', 0, ()),
    ('0e160dc3', 'dup v3.4h, w14', 0, ()),
    ('0e170dc3', 'dup v3.8b, w14', 0, ()),
    ('0e190dc3', 'dup v3.8b, w14', 0, ()),
    ('0e1a0dc3', 'dup v3.4h, w14', 0, ()),
    ('0e1b0dc3', 'dup v3.8b, w14', 0, ()),
    ('0e1c0dc3', 'dup v3.2s, w14', 0, ()),
    ('0e1d0dc3', 'dup v3.8b, w14', 0, ()),
    ('0e1e0dc3', 'dup v3.4h, w14', 0, ()),
    ('0e1f0dc3', 'dup v3.8b, w14', 0, ()),
    ('4e010dc3', 'dup v3.16b, w14', 0, ()),
    ('4e020dc3', 'dup v3.8h, w14', 0, ()),
    ('4e030dc3', 'dup v3.16b, w14', 0, ()),
    ('4e040dc3', 'dup v3.4s, w14', 0, ()),
    ('4e050dc3', 'dup v3.16b, w14', 0, ()),
    ('4e060dc3', 'dup v3.8h, w14', 0, ()),
    ('4e070dc3', 'dup v3.16b, w14', 0, ()),
    ('4e080dc3', 'dup v3.2d, x14', 0, ()),
    ('4e090dc3', 'dup v3.16b, w14', 0, ()),
    ('4e0a0dc3', 'dup v3.8h, w14', 0, ()),
    ('4e0b0dc3', 'dup v3.16b, w14', 0, ()),
    ('4e0c0dc3', 'dup v3.4s, w14', 0, ()),
    ('4e0d0dc3', 'dup v3.16b, w14', 0, ()),
    ('4e0e0dc3', 'dup v3.8h, w14', 0, ()),
    ('4e0f0dc3', 'dup v3.16b, w14', 0, ()),
    ('4e110dc3', 'dup v3.16b, w14', 0, ()),
    ('4e120dc3', 'dup v3.8h, w14', 0, ()),
    ('4e130dc3', 'dup v3.16b, w14', 0, ()),
    ('4e140dc3', 'dup v3.4s, w14', 0, ()),
    ('4e150dc3', 'dup v3.16b, w14', 0, ()),
    ('4e160dc3', 'dup v3.8h, w14', 0, ()),
    ('4e170dc3', 'dup v3.16b, w14', 0, ()),
    ('4e180dc3', 'dup v3.2d, x14', 0, ()),
    ('4e190dc3', 'dup v3.16b, w14', 0, ()),
    ('4e1a0dc3', 'dup v3.8h, w14', 0, ()),
    ('4e1b0dc3', 'dup v3.16b, w14', 0, ()),
    ('4e1c0dc3', 'dup v3.4s, w14', 0, ()),
    ('4e1d0dc3', 'dup v3.16b, w14', 0, ()),
    ('4e1e0dc3', 'dup v3.8h, w14', 0, ()),
    ('4e1f0dc3', 'dup v3.16b, w14', 0, ()),
    #smov (32-bit)
    ('0e012dc3', 'smov w3, v14.b[0]', 0, ()),
    ('0e022dc3', 'smov w3, v14.h[0]', 0, ()),
    ('0e032dc3', 'smov w3, v14.b[1]', 0, ()),
    ('0e052dc3', 'smov w3, v14.b[2]', 0, ()),
    ('0e062dc3', 'smov w3, v14.h[1]', 0, ()),
    ('0e072dc3', 'smov w3, v14.b[3]', 0, ()),
    ('0e092dc3', 'smov w3, v14.b[4]', 0, ()),
    ('0e0a2dc3', 'smov w3, v14.h[2]', 0, ()),
    ('0e0b2dc3', 'smov w3, v14.b[5]', 0, ()),
    ('0e0d2dc3', 'smov w3, v14.b[6]', 0, ()),
    ('0e0e2dc3', 'smov w3, v14.h[3]', 0, ()),
    ('0e0f2dc3', 'smov w3, v14.b[7]', 0, ()),
    ('0e112dc3', 'smov w3, v14.b[8]', 0, ()),
    ('0e122dc3', 'smov w3, v14.h[4]', 0, ()),
    ('0e132dc3', 'smov w3, v14.b[9]', 0, ()),
    ('0e152dc3', 'smov w3, v14.b[10]', 0, ()),
    ('0e162dc3', 'smov w3, v14.h[5]', 0, ()),
    ('0e172dc3', 'smov w3, v14.b[11]', 0, ()),
    ('0e192dc3', 'smov w3, v14.b[12]', 0, ()),
    ('0e1a2dc3', 'smov w3, v14.h[6]', 0, ()),
    ('0e1b2dc3', 'smov w3, v14.b[13]', 0, ()),
    ('0e1d2dc3', 'smov w3, v14.b[14]', 0, ()),
    ('0e1e2dc3', 'smov w3, v14.h[7]', 0, ()),
    ('0e1f2dc3', 'smov w3, v14.b[15]', 0, ()),
    #umov (32-bit)
    ('0e013dc3', 'umov w3, v14.b[0]', 0, ()),
    ('0e023dc3', 'umov w3, v14.h[0]', 0, ()),
    ('0e033dc3', 'umov w3, v14.b[1]', 0, ()),
    ('0e043dc3', 'umov w3, v14.s[0]', 0, ()),
    ('0e053dc3', 'umov w3, v14.b[2]', 0, ()),
    ('0e063dc3', 'umov w3, v14.h[1]', 0, ()),
    ('0e073dc3', 'umov w3, v14.b[3]', 0, ()),
    ('0e093dc3', 'umov w3, v14.b[4]', 0, ()),
    ('0e0a3dc3', 'umov w3, v14.h[2]', 0, ()),
    ('0e0b3dc3', 'umov w3, v14.b[5]', 0, ()),
    ('0e0c3dc3', 'umov w3, v14.s[1]', 0, ()),
    ('0e0d3dc3', 'umov w3, v14.b[6]', 0, ()),
    ('0e0e3dc3', 'umov w3, v14.h[3]', 0, ()),
    ('0e0f3dc3', 'umov w3, v14.b[7]', 0, ()),
    ('0e113dc3', 'umov w3, v14.b[8]', 0, ()),
    ('0e123dc3', 'umov w3, v14.h[4]', 0, ()),
    ('0e133dc3', 'umov w3, v14.b[9]', 0, ()),
    ('0e143dc3', 'umov w3, v14.s[2]', 0, ()),
    ('0e153dc3', 'umov w3, v14.b[10]', 0, ()),
    ('0e163dc3', 'umov w3, v14.h[5]', 0, ()),
    ('0e173dc3', 'umov w3, v14.b[11]', 0, ()),
    ('0e193dc3', 'umov w3, v14.b[12]', 0, ()),
    ('0e1a3dc3', 'umov w3, v14.h[6]', 0, ()),
    ('0e1b3dc3', 'umov w3, v14.b[13]', 0, ()),
    ('0e1c3dc3', 'umov w3, v14.s[3]', 0, ()),
    ('0e1d3dc3', 'umov w3, v14.b[14]', 0, ()),
    ('0e1e3dc3', 'umov w3, v14.h[7]', 0, ()),
    ('0e1f3dc3', 'umov w3, v14.b[15]', 0, ()),
    #ins (general)
    ('4e011dc3', 'ins v3.b[0], w14', 0, ()),
    ('4e021dc3', 'ins v3.h[0], w14', 0, ()),
    ('4e031dc3', 'ins v3.b[1], w14', 0, ()),
    ('4e041dc3', 'ins v3.s[0], w14', 0, ()),
    ('4e051dc3', 'ins v3.b[2], w14', 0, ()),
    ('4e061dc3', 'ins v3.h[1], w14', 0, ()),
    ('4e071dc3', 'ins v3.b[3], w14', 0, ()),
    ('4e081dc3', 'ins v3.d[0], x14', 0, ()),
    ('4e091dc3', 'ins v3.b[4], w14', 0, ()),
    ('4e0a1dc3', 'ins v3.h[2], w14', 0, ()),
    ('4e0b1dc3', 'ins v3.b[5], w14', 0, ()),
    ('4e0c1dc3', 'ins v3.s[1], w14', 0, ()),
    ('4e0d1dc3', 'ins v3.b[6], w14', 0, ()),
    ('4e0e1dc3', 'ins v3.h[3], w14', 0, ()),
    ('4e0f1dc3', 'ins v3.b[7], w14', 0, ()),
    ('4e111dc3', 'ins v3.b[8], w14', 0, ()),
    ('4e121dc3', 'ins v3.h[4], w14', 0, ()),
    ('4e131dc3', 'ins v3.b[9], w14', 0, ()),
    ('4e141dc3', 'ins v3.s[2], w14', 0, ()),
    ('4e151dc3', 'ins v3.b[10], w14', 0, ()),
    ('4e161dc3', 'ins v3.h[5], w14', 0, ()),
    ('4e171dc3', 'ins v3.b[11], w14', 0, ()),
    ('4e181dc3', 'ins v3.d[1], x14', 0, ()),
    ('4e191dc3', 'ins v3.b[12], w14', 0, ()),
    ('4e1a1dc3', 'ins v3.h[6], w14', 0, ()),
    ('4e1b1dc3', 'ins v3.b[13], w14', 0, ()),
    ('4e1c1dc3', 'ins v3.s[3], w14', 0, ()),
    ('4e1d1dc3', 'ins v3.b[14], w14', 0, ()),
    ('4e1e1dc3', 'ins v3.h[7], w14', 0, ()),
    ('4e1f1dc3', 'ins v3.b[15], w14', 0, ()),
    #smov (64-bit)
    ('4e012dc3', 'smov x3, v14.b[0]', 0, ()),
    ('4e022dc3', 'smov x3, v14.h[0]', 0, ()),
    ('4e032dc3', 'smov x3, v14.b[1]', 0, ()),
    ('4e042dc3', 'smov x3, v14.s[0]', 0, ()),
    ('4e052dc3', 'smov x3, v14.b[2]', 0, ()),
    ('4e062dc3', 'smov x3, v14.h[1]', 0, ()),
    ('4e072dc3', 'smov x3, v14.b[3]', 0, ()),
    ('4e092dc3', 'smov x3, v14.b[4]', 0, ()),
    ('4e0a2dc3', 'smov x3, v14.h[2]', 0, ()),
    ('4e0b2dc3', 'smov x3, v14.b[5]', 0, ()),
    ('4e0c2dc3', 'smov x3, v14.s[1]', 0, ()),
    ('4e0d2dc3', 'smov x3, v14.b[6]', 0, ()),
    ('4e0e2dc3', 'smov x3, v14.h[3]', 0, ()),
    ('4e0f2dc3', 'smov x3, v14.b[7]', 0, ()),
    ('4e112dc3', 'smov x3, v14.b[8]', 0, ()),
    ('4e122dc3', 'smov x3, v14.h[4]', 0, ()),
    ('4e132dc3', 'smov x3, v14.b[9]', 0, ()),
    ('4e142dc3', 'smov x3, v14.s[2]', 0, ()),
    ('4e152dc3', 'smov x3, v14.b[10]', 0, ()),
    ('4e162dc3', 'smov x3, v14.h[5]', 0, ()),
    ('4e172dc3', 'smov x3, v14.b[11]', 0, ()),
    ('4e192dc3', 'smov x3, v14.b[12]', 0, ()),
    ('4e1a2dc3', 'smov x3, v14.h[6]', 0, ()),
    ('4e1b2dc3', 'smov x3, v14.b[13]', 0, ()),
    ('4e1c2dc3', 'smov x3, v14.s[3]', 0, ()),
    ('4e1d2dc3', 'smov x3, v14.b[14]', 0, ()),
    ('4e1e2dc3', 'smov x3, v14.h[7]', 0, ()),
    ('4e1f2dc3', 'smov x3, v14.b[15]', 0, ()),
    #umov (64-bit)
    ('4e083dc3', 'umov x3, v14.d[0]', 0, ()),
    ('4e183dc3', 'umov x3, v14.d[1]', 0, ()),
    #ins (element)
    ('6e011dc3', 'ins v3.b[0], v14.b[1]', 0, ()),
    ('6e021dc3', 'ins v3.h[0], v14.h[1]', 0, ()),
    ('6e031dc3', 'ins v3.b[1], v14.b[3]', 0, ()),
    ('6e041dc3', 'ins v3.s[0], v14.s[1]', 0, ()),
    ('6e051dc3', 'ins v3.b[2], v14.b[5]', 0, ()),
    ('6e061dc3', 'ins v3.h[1], v14.h[3]', 0, ()),
    ('6e071dc3', 'ins v3.b[3], v14.b[7]', 0, ()),
    ('6e081dc3', 'ins v3.d[0], v14.d[1]', 0, ()),
    ('6e091dc3', 'ins v3.b[4], v14.b[9]', 0, ()),
    ('6e0a1dc3', 'ins v3.h[2], v14.h[5]', 0, ()),
    ('6e0b1dc3', 'ins v3.b[5], v14.b[b]', 0, ()),
    ('6e0c1dc3', 'ins v3.s[1], v14.s[3]', 0, ()),
    ('6e0d1dc3', 'ins v3.b[6], v14.b[d]', 0, ()),
    ('6e0e1dc3', 'ins v3.h[3], v14.h[7]', 0, ()),
    ('6e0f1dc3', 'ins v3.b[7], v14.b[f]', 0, ()),
    ('6e111dc3', 'ins v3.b[8], v14.b[1]', 0, ()),
    ('6e121dc3', 'ins v3.h[4], v14.h[1]', 0, ()),
    ('6e131dc3', 'ins v3.b[9], v14.b[3]', 0, ()),
    ('6e141dc3', 'ins v3.s[2], v14.s[1]', 0, ()),
    ('6e151dc3', 'ins v3.b[10], v14.b[5]', 0, ()),
    ('6e161dc3', 'ins v3.h[5], v14.h[3]', 0, ()),
    ('6e171dc3', 'ins v3.b[11], v14.b[7]', 0, ()),
    ('6e181dc3', 'ins v3.d[1], v14.d[1]', 0, ()),
    ('6e191dc3', 'ins v3.b[12], v14.b[9]', 0, ()),
    ('6e1a1dc3', 'ins v3.h[6], v14.h[5]', 0, ()),
    ('6e1b1dc3', 'ins v3.b[13], v14.b[13]', 0, ()),
    ('6e1c1dc3', 'ins v3.s[3], v14.s[3]', 0, ()),
    ('6e1d1dc3', 'ins v3.b[14], v14.b[14]', 0, ()),
    ('6e1e1dc3', 'ins v3.h[7], v14.h[7]', 0, ()),
    ('6e1f1dc3', 'ins v3.b[15], v14.b[15]', 0, ()),

    #AdvSIMD vector x indexed element

    #smlal
    ('0f6b29c3', 'smlal{} v3.4s, v14.4h, v11.h[6]', 0, ()),
    ('4f7b29c3', 'smlal{2} v3.4s, v14.8h, v11.h[7]', 0, ()),
    ('0fab29c3', 'smlal{} v3.2d, v14.2s, v11.s[3]', 0, ()),
    ('4fbb29c3', 'smlal{2} v3.2d, v14.4s, v27.s[3]', 0, ()),
    #sqdmlal
    ('0f6b39c3', 'sqdmlal{} v3.4s, v14.4h, v11.h[6]', 0, ()),
    ('4f7b39c3', 'sqdmlal{2} v3.4s, v14.8h, v11.h[7]', 0, ()),
    ('0fab39c3', 'sqdmlal{} v3.2d, v14.2s, v11.s[3]', 0, ()),
    ('4fbb39c3', 'sqdmlal{2} v3.2d, v14.4s, v27.s[3]', 0, ()),
    #smlsl
    ('0f6b69c3', 'smlsl{} v3.4s, v14.4h, v11.h[6]', 0, ()),
    ('4f7b69c3', 'smlsl{2} v3.4s, v14.8h, v11.h[7]', 0, ()),
    ('0fab69c3', 'smlsl{} v3.2d, v14.2s, v11.s[3]', 0, ()),
    ('4fbb69c3', 'smlsl{2} v3.2d, v14.4s, v27.s[3]', 0, ()),
    #sqdmlsl
    ('0f6b79c3', 'sqdmlsl{} v3.4s, v14.4h, v11.h[6]', 0, ()),
    ('4f7b79c3', 'sqdmlsl{2} v3.4s, v14.8h, v11.h[7]', 0, ()),
    ('0fab79c3', 'sqdmlsl{} v3.2d, v14.2s, v11.s[3]', 0, ()),
    ('4fbb79c3', 'sqdmlsl{2} v3.2d, v14.4s, v27.s[3]', 0, ()),
    #mul (by element)
    ('0f6b89c3', 'mul v3.4h, v14.4h, v11.h[6]', 0, ()),
    ('4f7b89c3', 'mul v3.8h, v14.8h, v11.h[7]', 0, ()),
    ('0fab89c3', 'mul v3.2s, v14.2s, v11.s[3]', 0, ()),
    ('4fbb89c3', 'mul v3.4s, v14.4s, v27.s[3]', 0, ()),
    #smull
    ('0f6ba9c3', 'smull{} v3.4s, v14.4h, v11.h[6]', 0, ()),
    ('4f7ba9c3', 'smull{2} v3.4s, v14.8h, v11.h[7]', 0, ()),
    ('0faba9c3', 'smull{} v3.2d, v14.2s, v11.s[3]', 0, ()),
    ('4fbba9c3', 'smull{2} v3.2d, v14.4s, v27.s[3]', 0, ()),
    #sqdmull
    ('0f6bb9c3', 'sqdmull{} v3.4s, v14.4h, v11.h[6]', 0, ()),
    ('4f7bb9c3', 'sqdmull{2} v3.4s, v14.8h, v11.h[7]', 0, ()),
    ('0fabb9c3', 'sqdmull{} v3.2d, v14.2s, v11.s[3]', 0, ()),
    ('4fbbb9c3', 'sqdmull{2} v3.2d, v14.4s, v27.s[3]', 0, ()),
    #sqdmulh
    ('0f6bc9c3', 'sqdmulh v3.4h, v14.4h, v11.h[6]', 0, ()),
    ('4f7bc9c3', 'sqdmulh v3.8h, v14.8h, v11.h[7]', 0, ()),
    ('0fabc9c3', 'sqdmulh v3.2s, v14.2s, v11.s[3]', 0, ()),
    ('4fbbc9c3', 'sqdmulh v3.4s, v14.4s, v27.s[3]', 0, ()),
    #sqrdmulh
    ('0f6bd9c3', 'sqrdmulh v3.4h, v14.4h, v11.h[6]', 0, ()),
    ('4f7bd9c3', 'sqrdmulh v3.8h, v14.8h, v11.h[7]', 0, ()),
    ('0fabd9c3', 'sqrdmulh v3.2s, v14.2s, v11.s[3]', 0, ()),
    ('4fbbd9c3', 'sqrdmulh v3.4s, v14.4s, v27.s[3]', 0, ()),
    #fmla
    ('0f8b19c3', 'fmla v3.2s, v14.2s, v11.s[2]', 0, ()),
    ('4fbb19c3', 'fmla v3.4s, v14.4s, v27.s[3]', 0, ()),
    ('4fcb19c3', 'fmla v3.2d, v14.2d, v11.d[1]', 0, ()),
    #fmls
    ('0f8b59c3', 'fmls v3.2s, v14.2s, v11.s[2]', 0, ()),
    ('4fbb59c3', 'fmls v3.4s, v14.4s, v27.s[3]', 0, ()),
    ('4fcb59c3', 'fmls v3.2d, v14.2d, v11.d[1]', 0, ()),
    #fmul
    ('0f8b99c3', 'fmul v3.2s, v14.2s, v11.s[2]', 0, ()),
    ('4fbb99c3', 'fmul v3.4s, v14.4s, v27.s[3]', 0, ()),
    ('4fcb99c3', 'fmul v3.2d, v14.2d, v11.d[1]', 0, ()),
    #mla (by element)
    ('2f6b09c3', 'mla v3.4h, v14.4h, v11.h[6]', 0, ()),
    ('6f7b09c3', 'mla v3.8h, v14.8h, v11.h[7]', 0, ()),
    ('2fab09c3', 'mla v3.2s, v14.2s, v11.s[3]', 0, ()),
    ('6fbb09c3', 'mla v3.4s, v14.4s, v27.s[3]', 0, ()),
    #umlal
    ('2f6b29c3', 'umlal{} v3.4s, v14.4h, v11.h[6]', 0, ()),
    ('6f7b29c3', 'umlal{2} v3.4s, v14.8h, v11.h[7]', 0, ()),
    ('2fab29c3', 'umlal{} v3.2d, v14.2s, v11.s[3]', 0, ()),
    ('6fbb29c3', 'umlal{2} v3.2d, v14.4s, v27.s[3]', 0, ()),
    #mls (by element)
    ('2f6b49c3', 'mls v3.4h, v14.4h, v11.h[6]', 0, ()),
    ('6f7b49c3', 'mls v3.8h, v14.8h, v11.h[7]', 0, ()),
    ('2fab49c3', 'mls v3.2s, v14.2s, v11.s[3]', 0, ()),
    ('6fbb49c3', 'mls v3.4s, v14.4s, v27.s[3]', 0, ()),
    #umlsl
    ('2f6b69c3', 'umlsl{} v3.4s, v14.4h, v11.h[6]', 0, ()),
    ('6f7b69c3', 'umlsl{2} v3.4s, v14.8h, v11.h[7]', 0, ()),
    ('2fab69c3', 'umlsl{} v3.2d, v14.2s, v11.s[3]', 0, ()),
    ('6fbb69c3', 'umlsl{2} v3.2d, v14.4s, v27.s[3]', 0, ()),
    #umull
    ('2f6ba9c3', 'umull{} v3.4s, v14.4h, v11.h[6]', 0, ()),
    ('6f7ba9c3', 'umull{2} v3.4s, v14.8h, v11.h[7]', 0, ()),
    ('2faba9c3', 'umull{} v3.2d, v14.2s, v11.s[3]', 0, ()),
    ('6fbba9c3', 'umull{2} v3.2d, v14.4s, v27.s[3]', 0, ()),
    #fmulx
    ('2f8b99c3', 'fmulx v3.2s, v14.2s, v11.s[2]', 0, ()),
    ('6fbb99c3', 'fmulx v3.4s, v14.4s, v27.s[3]', 0, ()),
    ('6fcb99c3', 'fmulx v3.2d, v14.2d, v11.d[1]', 0, ()),

    #AdvSIMD modified immediate

    #movi (32-bit shifted immediate)
    ('0f050723', 'movi v3.2s, #b9{, LSL #0}', 0, ()),
    ('4f050723', 'movi v3.4s, #b9{, LSL #0}', 0, ()),
    ('0f052723', 'movi v3.2s, #b9{, LSL #8}', 0, ()),
    ('4f052723', 'movi v3.4s, #b9{, LSL #8}', 0, ()),
    ('0f054723', 'movi v3.2s, #b9{, LSL #16}', 0, ()),
    ('4f054723', 'movi v3.4s, #b9{, LSL #16}', 0, ()),
    ('0f056723', 'movi v3.2s, #b9{, LSL #24}', 0, ()),
    ('4f056723', 'movi v3.4s, #b9{, LSL #0}', 0, ()),
    #orr(vector, immediate) (32-bit)
    ('0f051723', 'orr v3.2s, #b9{, LSL#0}', 0, ()),
    ('4f051723', 'orr v3.4s, #b9{, LSL#0}', 0, ()),
    ('0f053723', 'orr v3.2s, #b9{, LSL#8}', 0, ()),
    ('4f053723', 'orr v3.4s, #b9{, LSL#8}', 0, ()),
    ('0f055723', 'orr v3.2s, #b9{, LSL#16}', 0, ()),
    ('4f055723', 'orr v3.4s, #b9{, LSL#16}', 0, ()),
    ('0f057723', 'orr v3.2s, #b9{, LSL#24}', 0, ()),
    ('4f057723', 'orr v3.4s, #b9{, LSL#24}', 0, ()),
    #movi (16-bit shifted immediate)
    ('0f058723', 'movi v3.4h, #b9{, LSL #0}', 0, ()),
    ('4f058723', 'movi v3.8h, #b9{, LSL #0}', 0, ()),
    ('0f05a723', 'movi v3.4h, #b9{, LSL #8}', 0, ()),
    ('4f05a723', 'movi v3.8h, #b9{, LSL #8}', 0, ()),
    #orr (vector, immediate) (16-bit)
    ('0f059723', 'orr v3.4h, #b9{, LSL #0}', 0, ()),
    ('4f059723', 'orr v3.8h, #b9{, LSL #0}', 0, ()),
    ('0f05b723', 'orr v3.4h, #b9{, LSL #8}', 0, ()),
    ('4f05b723', 'orr v3.8h, #b9{, LSL #8}', 0, ()),
    #movi (32-bit shifting ones)
    ('0f05c723', 'movi v3.2s, #b9, MSL #8', 0, ()),
    ('4f05c723', 'movi v3.4s, #b9, MSL #8', 0, ()),
    ('0f05d723', 'movi v3.2s, #b9, MSL #16', 0, ()),
    ('4f05d723', 'movi v3.4s, #b9, MSL #16', 0, ()),
    #movi (8-bit)
    ('0f05e723', 'movi v3.8b, #b9{, LSL #0}', 0, ()),
    ('4f05e723', 'movi v3.16b, #b9{, LSL #0}', 0, ()),
    #fmov (vector, immediate) (single-precision)
    ('0f05f723', 'fmov v3.2s, #b9', 0, ()),
    ('4f05f723', 'fmov v3.4s, #b9', 0, ()),
    #mvni (32-bit shifted immediate)
    ('2f050723', 'mvni v3.2s, #b9{, LSL #0}', 0, ()),
    ('6f050723', 'mvni v3.4s, #b9{, LSL #0}', 0, ()),
    ('2f052723', 'mvni v3.2s, #b9{, LSL #8}', 0, ()),
    ('6f052723', 'mvni v3.4s, #b9{, LSL #8}', 0, ()),
    ('2f054723', 'mvni v3.2s, #b9{, LSL #16}', 0, ()),
    ('6f054723', 'mvni v3.4s, #b9{, LSL #16}', 0, ()),
    ('2f056723', 'mvni v3.2s, #b9{, LSL #24}', 0, ()),
    ('6f056723', 'mvni v3.4s, #b9{, LSL #0}', 0, ()),
    #bic (vector, immediate) (32-bit)
    ('2f051723', 'bic v3.2s, #b9{, LSL#0}', 0, ()),
    ('6f051723', 'bic v3.4s, #b9{, LSL#0}', 0, ()),
    ('2f053723', 'bic v3.2s, #b9{, LSL#8}', 0, ()),
    ('6f053723', 'bic v3.4s, #b9{, LSL#8}', 0, ()),
    ('2f055723', 'bic v3.2s, #b9{, LSL#16}', 0, ()),
    ('6f055723', 'bic v3.4s, #b9{, LSL#16}', 0, ()),
    ('2f057723', 'bic v3.2s, #b9{, LSL#24}', 0, ()),
    ('6f057723', 'bic v3.4s, #b9{, LSL#24}', 0, ()),
    #mvni (16-bit shifted immediate)
    ('2f058723', 'mvni v3.4h, #b9{, LSL #0}', 0, ()),
    ('6f058723', 'mvni v3.8h, #b9{, LSL #0}', 0, ()),
    ('2f05a723', 'mvni v3.4h, #b9{, LSL #8}', 0, ()),
    ('6f05a723', 'mvni v3.8h, #b9{, LSL #8}', 0, ()),
    #bic (vector, immediate) (16-bit)
    ('2f059723', 'bic v3.4h, #b9{, LSL #0}', 0, ()),
    ('6f059723', 'bic v3.8h, #b9{, LSL #0}', 0, ()),
    ('2f05b723', 'bic v3.4h, #b9{, LSL #8}', 0, ()),
    ('6f05b723', 'bic v3.8h, #b9{, LSL #8}', 0, ()),
    #mvni (32-bit shifting ones)
    ('2f05c723', 'mvni v3.2s, #b9, MSL #8', 0, ()),
    ('6f05c723', 'mvni v3.4s, #b9, MSL #8', 0, ()),
    ('2f05d723', 'mvni v3.2s, #b9, MSL #16', 0, ()),
    ('6f05d723', 'mvni v3.4s, #b9, MSL #16', 0, ()),
    #movi (64-bit scalar)
    ('2f05e723', 'movi d3, #b9', 0, ()),
    #movi (64-bit vector)
    ('6f05e723', 'movi v3.2d, #b9', 0, ()),
    #fmov (vector, immediate) (double precision)
    ('6f05f723', 'fmov v3.2d, #b9', 0, ()),

    #AdvSIMD shift by immediate

    #sshr
    ('0f0a05c3', 'sshr v3.8b, v14.8b, #6', 0, ()),
    ('4f0a05c3', 'sshr v3.16b, v14.16b, #6', 0, ()),
    ('0f1205c3', 'sshr v3.4h, v14.4h, #14', 0, ()),
    ('0f1a05c3', 'sshr v3.4h, v14.4h, #6', 0, ()),
    ('4f1205c3', 'sshr v3.8h, v14.8h, #14', 0, ()),
    ('4f1a05c3', 'sshr v3.8h, v14.8h, #6', 0, ()),
    ('0f2205c3', 'sshr v3.2s, v14.2s, #30', 0, ()),
    ('0f2a05c3', 'sshr v3.2s, v14.2s, #22', 0, ()),
    ('0f3205c3', 'sshr v3.2s, v14.2s, #14', 0, ()),
    ('0f3a05c3', 'sshr v3.2s, v14.2s, #6', 0, ()),
    ('4f2205c3', 'sshr v3.4s, v14.4s, #30', 0, ()),
    ('4f2a05c3', 'sshr v3.4s, v14.4s, #22', 0, ()),
    ('4f3205c3', 'sshr v3.4s, v14.4s, #14', 0, ()),
    ('4f3a05c3', 'sshr v3.4s, v14.4s, #6', 0, ()),
    ('4f4205c3', 'sshr v3.2d, v14.2d, #62', 0, ()),
    ('4f4a05c3', 'sshr v3.2d, v14.2d, #54', 0, ()),
    ('4f5205c3', 'sshr v3.2d, v14.2d, #46', 0, ()),
    ('4f5a05c3', 'sshr v3.2d, v14.2d, #38', 0, ()),
    ('4f6205c3', 'sshr v3.2d, v14.2d, #30', 0, ()),
    ('4f6a05c3', 'sshr v3.2d, v14.2d, #22', 0, ()),
    ('4f7205c3', 'sshr v3.2d, v14.2d, #14', 0, ()),
    ('4f7a05c3', 'sshr v3.2d, v14.2d, #6', 0, ()),
    #ssra
    ('0f0a15c3', 'ssra v3.8b, v14.8b, #6', 0, ()),
    ('4f0a15c3', 'ssra v3.16b, v14.16b, #6', 0, ()),
    ('0f1215c3', 'ssra v3.4h, v14.4h, #14', 0, ()),
    ('0f1a15c3', 'ssra v3.4h, v14.4h, #6', 0, ()),
    ('4f1215c3', 'ssra v3.8h, v14.8h, #14', 0, ()),
    ('4f1a15c3', 'ssra v3.8h, v14.8h, #6', 0, ()),
    ('0f2215c3', 'ssra v3.2s, v14.2s, #30', 0, ()),
    ('0f2a15c3', 'ssra v3.2s, v14.2s, #22', 0, ()),
    ('0f3215c3', 'ssra v3.2s, v14.2s, #14', 0, ()),
    ('0f3a15c3', 'ssra v3.2s, v14.2s, #6', 0, ()),
    ('4f2215c3', 'ssra v3.4s, v14.4s, #30', 0, ()),
    ('4f2a15c3', 'ssra v3.4s, v14.4s, #22', 0, ()),
    ('4f3215c3', 'ssra v3.4s, v14.4s, #14', 0, ()),
    ('4f3a15c3', 'ssra v3.4s, v14.4s, #6', 0, ()),
    ('4f4215c3', 'ssra v3.2d, v14.2d, #62', 0, ()),
    ('4f4a15c3', 'ssra v3.2d, v14.2d, #54', 0, ()),
    ('4f5215c3', 'ssra v3.2d, v14.2d, #46', 0, ()),
    ('4f5a15c3', 'ssra v3.2d, v14.2d, #38', 0, ()),
    ('4f6215c3', 'ssra v3.2d, v14.2d, #30', 0, ()),
    ('4f6a15c3', 'ssra v3.2d, v14.2d, #22', 0, ()),
    ('4f7215c3', 'ssra v3.2d, v14.2d, #14', 0, ()),
    ('4f7a15c3', 'ssra v3.2d, v14.2d, #6', 0, ()),
    #srshr
    ('0f0a25c3', 'srshr v3.8b, v14.8b, #6', 0, ()),
    ('4f0a25c3', 'srshr v3.16b, v14.16b, #6', 0, ()),
    ('0f1225c3', 'srshr v3.4h, v14.4h, #14', 0, ()),
    ('0f1a25c3', 'srshr v3.4h, v14.4h, #6', 0, ()),
    ('4f1225c3', 'srshr v3.8h, v14.8h, #14', 0, ()),
    ('4f1a25c3', 'srshr v3.8h, v14.8h, #6', 0, ()),
    ('0f2225c3', 'srshr v3.2s, v14.2s, #30', 0, ()),
    ('0f2a25c3', 'srshr v3.2s, v14.2s, #22', 0, ()),
    ('0f3225c3', 'srshr v3.2s, v14.2s, #14', 0, ()),
    ('0f3a25c3', 'srshr v3.2s, v14.2s, #6', 0, ()),
    ('4f2225c3', 'srshr v3.4s, v14.4s, #30', 0, ()),
    ('4f2a25c3', 'srshr v3.4s, v14.4s, #22', 0, ()),
    ('4f3225c3', 'srshr v3.4s, v14.4s, #14', 0, ()),
    ('4f3a25c3', 'srshr v3.4s, v14.4s, #6', 0, ()),
    ('4f4225c3', 'srshr v3.2d, v14.2d, #62', 0, ()),
    ('4f4a25c3', 'srshr v3.2d, v14.2d, #54', 0, ()),
    ('4f5225c3', 'srshr v3.2d, v14.2d, #46', 0, ()),
    ('4f5a25c3', 'srshr v3.2d, v14.2d, #38', 0, ()),
    ('4f6225c3', 'srshr v3.2d, v14.2d, #30', 0, ()),
    ('4f6a25c3', 'srshr v3.2d, v14.2d, #22', 0, ()),
    ('4f7225c3', 'srshr v3.2d, v14.2d, #14', 0, ()),
    ('4f7a25c3', 'srshr v3.2d, v14.2d, #6', 0, ()),
    #srsra
    ('0f0a35c3', 'srsra v3.8b, v14.8b, #6', 0, ()),
    ('4f0a35c3', 'srsra v3.16b, v14.16b, #6', 0, ()),
    ('0f1235c3', 'srsra v3.4h, v14.4h, #14', 0, ()),
    ('0f1a35c3', 'srsra v3.4h, v14.4h, #6', 0, ()),
    ('4f1235c3', 'srsra v3.8h, v14.8h, #14', 0, ()),
    ('4f1a35c3', 'srsra v3.8h, v14.8h, #6', 0, ()),
    ('0f2235c3', 'srsra v3.2s, v14.2s, #30', 0, ()),
    ('0f2a35c3', 'srsra v3.2s, v14.2s, #22', 0, ()),
    ('0f3235c3', 'srsra v3.2s, v14.2s, #14', 0, ()),
    ('0f3a35c3', 'srsra v3.2s, v14.2s, #6', 0, ()),
    ('4f2235c3', 'srsra v3.4s, v14.4s, #30', 0, ()),
    ('4f2a35c3', 'srsra v3.4s, v14.4s, #22', 0, ()),
    ('4f3235c3', 'srsra v3.4s, v14.4s, #14', 0, ()),
    ('4f3a35c3', 'srsra v3.4s, v14.4s, #6', 0, ()),
    ('4f4235c3', 'srsra v3.2d, v14.2d, #62', 0, ()),
    ('4f4a35c3', 'srsra v3.2d, v14.2d, #54', 0, ()),
    ('4f5235c3', 'srsra v3.2d, v14.2d, #46', 0, ()),
    ('4f5a35c3', 'srsra v3.2d, v14.2d, #38', 0, ()),
    ('4f6235c3', 'srsra v3.2d, v14.2d, #30', 0, ()),
    ('4f6a35c3', 'srsra v3.2d, v14.2d, #22', 0, ()),
    ('4f7235c3', 'srsra v3.2d, v14.2d, #14', 0, ()),
    ('4f7a35c3', 'srsra v3.2d, v14.2d, #6', 0, ()),
    #shl
    ('0f0a55c3', 'shl v3.8b, v14.8b, #2', 0, ()),
    ('4f0a55c3', 'shl v3.16b, v14.16b, #2', 0, ()),
    ('0f1255c3', 'shl v3.4h, v14.4h, #2', 0, ()),
    ('0f1a55c3', 'shl v3.4h, v14.4h, #10', 0, ()),
    ('4f1255c3', 'shl v3.8h, v14.8h, #2', 0, ()),
    ('4f1a55c3', 'shl v3.8h, v14.8h, #10', 0, ()),
    ('0f2255c3', 'shl v3.2s, v14.2s, #2', 0, ()),
    ('0f2a55c3', 'shl v3.2s, v14.2s, #10', 0, ()),
    ('0f3255c3', 'shl v3.2s, v14.2s, #18', 0, ()),
    ('0f3a55c3', 'shl v3.2s, v14.2s, #26', 0, ()),
    ('4f2255c3', 'shl v3.4s, v14.4s, #2', 0, ()),
    ('4f2a55c3', 'shl v3.4s, v14.4s, #10', 0, ()),
    ('4f3255c3', 'shl v3.4s, v14.4s, #18', 0, ()),
    ('4f3a55c3', 'shl v3.4s, v14.4s, #26', 0, ()),
    ('4f4255c3', 'shl v3.2d, v14.2d, #2', 0, ()),
    ('4f4a55c3', 'shl v3.2d, v14.2d, #10', 0, ()),
    ('4f5255c3', 'shl v3.2d, v14.2d, #18', 0, ()),
    ('4f5a55c3', 'shl v3.2d, v14.2d, #26', 0, ()),
    ('4f6255c3', 'shl v3.2d, v14.2d, #34', 0, ()),
    ('4f6a55c3', 'shl v3.2d, v14.2d, #42', 0, ()),
    ('4f7255c3', 'shl v3.2d, v14.2d, #50', 0, ()),
    ('4f7a55c3', 'shl v3.2d, v14.2d, #58', 0, ()),
    #sqshl
    ('0f0a75c3', 'sqshl v3.8b, v14.8b, #2', 0, ()),
    ('4f0a75c3', 'sqshl v3.16b, v14.16b, #2', 0, ()),
    ('0f1275c3', 'sqshl v3.4h, v14.4h, #2', 0, ()),
    ('0f1a75c3', 'sqshl v3.4h, v14.4h, #10', 0, ()),
    ('4f1275c3', 'sqshl v3.8h, v14.8h, #2', 0, ()),
    ('4f1a75c3', 'sqshl v3.8h, v14.8h, #10', 0, ()),
    ('0f2275c3', 'sqshl v3.2s, v14.2s, #2', 0, ()),
    ('0f2a75c3', 'sqshl v3.2s, v14.2s, #10', 0, ()),
    ('0f3275c3', 'sqshl v3.2s, v14.2s, #18', 0, ()),
    ('0f3a75c3', 'sqshl v3.2s, v14.2s, #26', 0, ()),
    ('4f2275c3', 'sqshl v3.4s, v14.4s, #2', 0, ()),
    ('4f2a75c3', 'sqshl v3.4s, v14.4s, #10', 0, ()),
    ('4f3275c3', 'sqshl v3.4s, v14.4s, #18', 0, ()),
    ('4f3a75c3', 'sqshl v3.4s, v14.4s, #26', 0, ()),
    ('4f4275c3', 'sqshl v3.2d, v14.2d, #2', 0, ()),
    ('4f4a75c3', 'sqshl v3.2d, v14.2d, #10', 0, ()),
    ('4f5275c3', 'sqshl v3.2d, v14.2d, #18', 0, ()),
    ('4f5a75c3', 'sqshl v3.2d, v14.2d, #26', 0, ()),
    ('4f6275c3', 'sqshl v3.2d, v14.2d, #34', 0, ()),
    ('4f6a75c3', 'sqshl v3.2d, v14.2d, #42', 0, ()),
    ('4f7275c3', 'sqshl v3.2d, v14.2d, #50', 0, ()),
    ('4f7a75c3', 'sqshl v3.2d, v14.2d, #58', 0, ()),
    #shrn
    ('0f0a85c3', 'shrn{} v3.8b, v14.8h, #6', 0, ()),
    ('4f0a85c3', 'shrn{2} v3.16b, v14.8h, #6', 0, ()),
    ('0f1285c3', 'shrn{} v3.4h, v14.4s, #14', 0, ()),
    ('0f1a85c3', 'shrn{} v3.4h, v14.4s, #6', 0, ()),
    ('4f1285c3', 'shrn{2} v3.8h, v14.4s, #14', 0, ()),
    ('4f1a85c3', 'shrn{2} v3.8h, v14.4s, #6', 0, ()),
    ('0f2285c3', 'shrn{} v3.2s, v14.2d, #30', 0, ()),
    ('0f2a85c3', 'shrn{} v3.2s, v14.2d, #22', 0, ()),
    ('0f3285c3', 'shrn{} v3.2s, v14.2d, #14', 0, ()),
    ('0f3a85c3', 'shrn{} v3.2s, v14.2d, #6', 0, ()),
    ('4f2285c3', 'shrn{2} v3.4s, v14.2d, #30', 0, ()),
    ('4f2a85c3', 'shrn{2} v3.4s, v14.2d, #22', 0, ()),
    ('4f3285c3', 'shrn{2} v3.4s, v14.2d, #14', 0, ()),
    ('4f3a85c3', 'shrn{2} v3.4s, v14.2d, #6', 0, ()),
    #rshrn
    ('0f0a8dc3', 'rshrn{} v3.8b, v14.8h, #6', 0, ()),
    ('4f0a8dc3', 'rshrn{2} v3.16b, v14.8h, #6', 0, ()),
    ('0f128dc3', 'rshrn{} v3.4h, v14.4s, #14', 0, ()),
    ('0f1a8dc3', 'rshrn{} v3.4h, v14.4s, #6', 0, ()),
    ('4f128dc3', 'rshrn{2} v3.8h, v14.4s, #14', 0, ()),
    ('4f1a8dc3', 'rshrn{2} v3.8h, v14.4s, #6', 0, ()),
    ('0f228dc3', 'rshrn{} v3.2s, v14.2d, #30', 0, ()),
    ('0f2a8dc3', 'rshrn{} v3.2s, v14.2d, #22', 0, ()),
    ('0f328dc3', 'rshrn{} v3.2s, v14.2d, #14', 0, ()),
    ('0f3a8dc3', 'rshrn{} v3.2s, v14.2d, #6', 0, ()),
    ('4f228dc3', 'rshrn{2} v3.4s, v14.2d, #30', 0, ()),
    ('4f2a8dc3', 'rshrn{2} v3.4s, v14.2d, #22', 0, ()),
    ('4f328dc3', 'rshrn{2} v3.4s, v14.2d, #14', 0, ()),
    ('4f3a8dc3', 'rshrn{2} v3.4s, v14.2d, #6', 0, ()),
    #sqshrn
    ('0f0a95c3', 'sqshrn{} v3.8b, v14.8h, #6', 0, ()),
    ('4f0a95c3', 'sqshrn{2} v3.16b, v14.8h, #6', 0, ()),
    ('0f1295c3', 'sqshrn{} v3.4h, v14.4s, #14', 0, ()),
    ('0f1a95c3', 'sqshrn{} v3.4h, v14.4s, #6', 0, ()),
    ('4f1295c3', 'sqshrn{2} v3.8h, v14.4s, #14', 0, ()),
    ('4f1a95c3', 'sqshrn{2} v3.8h, v14.4s, #6', 0, ()),
    ('0f2295c3', 'sqshrn{} v3.2s, v14.2d, #30', 0, ()),
    ('0f2a95c3', 'sqshrn{} v3.2s, v14.2d, #22', 0, ()),
    ('0f3295c3', 'sqshrn{} v3.2s, v14.2d, #14', 0, ()),
    ('0f3a95c3', 'sqshrn{} v3.2s, v14.2d, #6', 0, ()),
    ('4f2295c3', 'sqshrn{2} v3.4s, v14.2d, #30', 0, ()),
    ('4f2a95c3', 'sqshrn{2} v3.4s, v14.2d, #22', 0, ()),
    ('4f3295c3', 'sqshrn{2} v3.4s, v14.2d, #14', 0, ()),
    ('4f3a95c3', 'sqshrn{2} v3.4s, v14.2d, #6', 0, ()),
    #sqrshrn
    ('0f0a9dc3', 'sqrshrn{} v3.8b, v14.8h, #6', 0, ()),
    ('4f0a9dc3', 'sqrshrn{2} v3.16b, v14.8h, #6', 0, ()),
    ('0f129dc3', 'sqrshrn{} v3.4h, v14.4s, #14', 0, ()),
    ('0f1a9dc3', 'sqrshrn{} v3.4h, v14.4s, #6', 0, ()),
    ('4f129dc3', 'sqrshrn{2} v3.8h, v14.4s, #14', 0, ()),
    ('4f1a9dc3', 'sqrshrn{2} v3.8h, v14.4s, #6', 0, ()),
    ('0f229dc3', 'sqrshrn{} v3.2s, v14.2d, #30', 0, ()),
    ('0f2a9dc3', 'sqrshrn{} v3.2s, v14.2d, #22', 0, ()),
    ('0f329dc3', 'sqrshrn{} v3.2s, v14.2d, #14', 0, ()),
    ('0f3a9dc3', 'sqrshrn{} v3.2s, v14.2d, #6', 0, ()),
    ('4f229dc3', 'sqrshrn{2} v3.4s, v14.2d, #30', 0, ()),
    ('4f2a9dc3', 'sqrshrn{2} v3.4s, v14.2d, #22', 0, ()),
    ('4f329dc3', 'sqrshrn{2} v3.4s, v14.2d, #14', 0, ()),
    ('4f3a9dc3', 'sqrshrn{2} v3.4s, v14.2d, #6', 0, ()),
    #sshll
    ('0f0aa5c3', 'sshll{} v3.8h, v14.8b, #2', 0, ()),
    ('4f0aa5c3', 'sshll{2} v3.8h, v14.16b, #2', 0, ()),
    ('0f12a5c3', 'sshll{} v3.4s, v14.4h, #2', 0, ()),
    ('0f1aa5c3', 'sshll{} v3.4s, v14.4h, #10', 0, ()),
    ('4f12a5c3', 'sshll{2} v3.4s, v14.8h, #2', 0, ()),
    ('4f1aa5c3', 'sshll{2} v3.4s, v14.8h, #10', 0, ()),
    ('0f22a5c3', 'sshll{} v3.2d, v14.2s, #2', 0, ()),
    ('0f2aa5c3', 'sshll{} v3.2d, v14.2s, #10', 0, ()),
    ('0f32a5c3', 'sshll{} v3.2d, v14.2s, #18', 0, ()),
    ('0f3aa5c3', 'sshll{} v3.2d, v14.2s, #26', 0, ()),
    ('4f22a5c3', 'sshll{2} v3.2d, v14.4s, #2', 0, ()),
    ('4f2aa5c3', 'sshll{2} v3.2d, v14.4s, #10', 0, ()),
    ('4f32a5c3', 'sshll{2} v3.2d, v14.4s, #18', 0, ()),
    ('4f3aa5c3', 'sshll{2} v3.2d, v14.4s, #26', 0, ()),
    #scvtf
    ('0f22e5c3', 'scvtf v3.2s, v14.2s, #30', 0, ()),
    ('0f2ae5c3', 'scvtf v3.2s, v14.2s, #22', 0, ()),
    ('0f32e5c3', 'scvtf v3.2s, v14.2s, #14', 0, ()),
    ('0f3ae5c3', 'scvtf v3.2s, v14.2s, #6', 0, ()),
    ('4f22e5c3', 'scvtf v3.4s, v14.4s, #30', 0, ()),
    ('4f2ae5c3', 'scvtf v3.4s, v14.4s, #22', 0, ()),
    ('4f32e5c3', 'scvtf v3.4s, v14.4s, #14', 0, ()),
    ('4f3ae5c3', 'scvtf v3.4s, v14.4s, #6', 0, ()),
    ('4f42e5c3', 'scvtf v3.2d, v14.2d, #62', 0, ()),
    ('4f4ae5c3', 'scvtf v3.2d, v14.2d, #54', 0, ()),
    ('4f52e5c3', 'scvtf v3.2d, v14.2d, #46', 0, ()),
    ('4f5ae5c3', 'scvtf v3.2d, v14.2d, #38', 0, ()),
    ('4f62e5c3', 'scvtf v3.2d, v14.2d, #30', 0, ()),
    ('4f6ae5c3', 'scvtf v3.2d, v14.2d, #22', 0, ()),
    ('4f72e5c3', 'scvtf v3.2d, v14.2d, #14', 0, ()),
    ('4f7ae5c3', 'scvtf v3.2d, v14.2d, #6', 0, ()),
    #fcvtzs
    ('0f22fdc3', 'fcvtzs v3.2s, v14.2s, #30', 0, ()),
    ('0f2afdc3', 'fcvtzs v3.2s, v14.2s, #22', 0, ()),
    ('0f32fdc3', 'fcvtzs v3.2s, v14.2s, #14', 0, ()),
    ('0f3afdc3', 'fcvtzs v3.2s, v14.2s, #6', 0, ()),
    ('4f22fdc3', 'fcvtzs v3.4s, v14.4s, #30', 0, ()),
    ('4f2afdc3', 'fcvtzs v3.4s, v14.4s, #22', 0, ()),
    ('4f32fdc3', 'fcvtzs v3.4s, v14.4s, #14', 0, ()),
    ('4f3afdc3', 'fcvtzs v3.4s, v14.4s, #6', 0, ()),
    ('4f42fdc3', 'fcvtzs v3.2d, v14.2d, #62', 0, ()),
    ('4f4afdc3', 'fcvtzs v3.2d, v14.2d, #54', 0, ()),
    ('4f52fdc3', 'fcvtzs v3.2d, v14.2d, #46', 0, ()),
    ('4f5afdc3', 'fcvtzs v3.2d, v14.2d, #38', 0, ()),
    ('4f62fdc3', 'fcvtzs v3.2d, v14.2d, #30', 0, ()),
    ('4f6afdc3', 'fcvtzs v3.2d, v14.2d, #22', 0, ()),
    ('4f72fdc3', 'fcvtzs v3.2d, v14.2d, #14', 0, ()),
    ('4f7afdc3', 'fcvtzs v3.2d, v14.2d, #6', 0, ()),
    #ushr
    ('2f0a05c3', 'ushr v3.8b, v14.8b, #6', 0, ()),
    ('6f0a05c3', 'ushr v3.16b, v14.16b, #6', 0, ()),
    ('2f1205c3', 'ushr v3.4h, v14.4h, #14', 0, ()),
    ('2f1a05c3', 'ushr v3.4h, v14.4h, #6', 0, ()),
    ('6f1205c3', 'ushr v3.8h, v14.8h, #14', 0, ()),
    ('6f1a05c3', 'ushr v3.8h, v14.8h, #6', 0, ()),
    ('2f2205c3', 'ushr v3.2s, v14.2s, #30', 0, ()),
    ('2f2a05c3', 'ushr v3.2s, v14.2s, #22', 0, ()),
    ('2f3205c3', 'ushr v3.2s, v14.2s, #14', 0, ()),
    ('2f3a05c3', 'ushr v3.2s, v14.2s, #6', 0, ()),
    ('6f2205c3', 'ushr v3.4s, v14.4s, #30', 0, ()),
    ('6f2a05c3', 'ushr v3.4s, v14.4s, #22', 0, ()),
    ('6f3205c3', 'ushr v3.4s, v14.4s, #14', 0, ()),
    ('6f3a05c3', 'ushr v3.4s, v14.4s, #6', 0, ()),
    ('6f4205c3', 'ushr v3.2d, v14.2d, #62', 0, ()),
    ('6f4a05c3', 'ushr v3.2d, v14.2d, #54', 0, ()),
    ('6f5205c3', 'ushr v3.2d, v14.2d, #46', 0, ()),
    ('6f5a05c3', 'ushr v3.2d, v14.2d, #38', 0, ()),
    ('6f6205c3', 'ushr v3.2d, v14.2d, #30', 0, ()),
    ('6f6a05c3', 'ushr v3.2d, v14.2d, #22', 0, ()),
    ('6f7205c3', 'ushr v3.2d, v14.2d, #14', 0, ()),
    ('6f7a05c3', 'ushr v3.2d, v14.2d, #6', 0, ()),
    #usra
    ('2f0a15c3', 'usra v3.8b, v14.8b, #6', 0, ()),
    ('6f0a15c3', 'usra v3.16b, v14.16b, #6', 0, ()),
    ('2f1215c3', 'usra v3.4h, v14.4h, #14', 0, ()),
    ('2f1a15c3', 'usra v3.4h, v14.4h, #6', 0, ()),
    ('6f1215c3', 'usra v3.8h, v14.8h, #14', 0, ()),
    ('6f1a15c3', 'usra v3.8h, v14.8h, #6', 0, ()),
    ('2f2215c3', 'usra v3.2s, v14.2s, #30', 0, ()),
    ('2f2a15c3', 'usra v3.2s, v14.2s, #22', 0, ()),
    ('2f3215c3', 'usra v3.2s, v14.2s, #14', 0, ()),
    ('2f3a15c3', 'usra v3.2s, v14.2s, #6', 0, ()),
    ('6f2215c3', 'usra v3.4s, v14.4s, #30', 0, ()),
    ('6f2a15c3', 'usra v3.4s, v14.4s, #22', 0, ()),
    ('6f3215c3', 'usra v3.4s, v14.4s, #14', 0, ()),
    ('6f3a15c3', 'usra v3.4s, v14.4s, #6', 0, ()),
    ('6f4215c3', 'usra v3.2d, v14.2d, #62', 0, ()),
    ('6f4a15c3', 'usra v3.2d, v14.2d, #54', 0, ()),
    ('6f5215c3', 'usra v3.2d, v14.2d, #46', 0, ()),
    ('6f5a15c3', 'usra v3.2d, v14.2d, #38', 0, ()),
    ('6f6215c3', 'usra v3.2d, v14.2d, #30', 0, ()),
    ('6f6a15c3', 'usra v3.2d, v14.2d, #22', 0, ()),
    ('6f7215c3', 'usra v3.2d, v14.2d, #14', 0, ()),
    ('6f7a15c3', 'usra v3.2d, v14.2d, #6', 0, ()),
    #urshr
    ('2f0a25c3', 'urshr v3.8b, v14.8b, #6', 0, ()),
    ('6f0a25c3', 'urshr v3.16b, v14.16b, #6', 0, ()),
    ('2f1225c3', 'urshr v3.4h, v14.4h, #14', 0, ()),
    ('2f1a25c3', 'urshr v3.4h, v14.4h, #6', 0, ()),
    ('6f1225c3', 'urshr v3.8h, v14.8h, #14', 0, ()),
    ('6f1a25c3', 'urshr v3.8h, v14.8h, #6', 0, ()),
    ('2f2225c3', 'urshr v3.2s, v14.2s, #30', 0, ()),
    ('2f2a25c3', 'urshr v3.2s, v14.2s, #22', 0, ()),
    ('2f3225c3', 'urshr v3.2s, v14.2s, #14', 0, ()),
    ('2f3a25c3', 'urshr v3.2s, v14.2s, #6', 0, ()),
    ('6f2225c3', 'urshr v3.4s, v14.4s, #30', 0, ()),
    ('6f2a25c3', 'urshr v3.4s, v14.4s, #22', 0, ()),
    ('6f3225c3', 'urshr v3.4s, v14.4s, #14', 0, ()),
    ('6f3a25c3', 'urshr v3.4s, v14.4s, #6', 0, ()),
    ('6f4225c3', 'urshr v3.2d, v14.2d, #62', 0, ()),
    ('6f4a25c3', 'urshr v3.2d, v14.2d, #54', 0, ()),
    ('6f5225c3', 'urshr v3.2d, v14.2d, #46', 0, ()),
    ('6f5a25c3', 'urshr v3.2d, v14.2d, #38', 0, ()),
    ('6f6225c3', 'urshr v3.2d, v14.2d, #30', 0, ()),
    ('6f6a25c3', 'urshr v3.2d, v14.2d, #22', 0, ()),
    ('6f7225c3', 'urshr v3.2d, v14.2d, #14', 0, ()),
    ('6f7a25c3', 'urshr v3.2d, v14.2d, #6', 0, ()),
    #ursra
    ('2f0a35c3', 'ursra v3.8b, v14.8b, #6', 0, ()),
    ('6f0a35c3', 'ursra v3.16b, v14.16b, #6', 0, ()),
    ('2f1235c3', 'ursra v3.4h, v14.4h, #14', 0, ()),
    ('2f1a35c3', 'ursra v3.4h, v14.4h, #6', 0, ()),
    ('6f1235c3', 'ursra v3.8h, v14.8h, #14', 0, ()),
    ('6f1a35c3', 'ursra v3.8h, v14.8h, #6', 0, ()),
    ('2f2235c3', 'ursra v3.2s, v14.2s, #30', 0, ()),
    ('2f2a35c3', 'ursra v3.2s, v14.2s, #22', 0, ()),
    ('2f3235c3', 'ursra v3.2s, v14.2s, #14', 0, ()),
    ('2f3a35c3', 'ursra v3.2s, v14.2s, #6', 0, ()),
    ('6f2235c3', 'ursra v3.4s, v14.4s, #30', 0, ()),
    ('6f2a35c3', 'ursra v3.4s, v14.4s, #22', 0, ()),
    ('6f3235c3', 'ursra v3.4s, v14.4s, #14', 0, ()),
    ('6f3a35c3', 'ursra v3.4s, v14.4s, #6', 0, ()),
    ('6f4235c3', 'ursra v3.2d, v14.2d, #62', 0, ()),
    ('6f4a35c3', 'ursra v3.2d, v14.2d, #54', 0, ()),
    ('6f5235c3', 'ursra v3.2d, v14.2d, #46', 0, ()),
    ('6f5a35c3', 'ursra v3.2d, v14.2d, #38', 0, ()),
    ('6f6235c3', 'ursra v3.2d, v14.2d, #30', 0, ()),
    ('6f6a35c3', 'ursra v3.2d, v14.2d, #22', 0, ()),
    ('6f7235c3', 'ursra v3.2d, v14.2d, #14', 0, ()),
    ('6f7a35c3', 'ursra v3.2d, v14.2d, #6', 0, ()),
    #sri
    ('2f0a45c3', 'sri v3.8b, v14.8b, #6', 0, ()),
    ('6f0a45c3', 'sri v3.16b, v14.16b, #6', 0, ()),
    ('2f1245c3', 'sri v3.4h, v14.4h, #14', 0, ()),
    ('2f1a45c3', 'sri v3.4h, v14.4h, #6', 0, ()),
    ('6f1245c3', 'sri v3.8h, v14.8h, #14', 0, ()),
    ('6f1a45c3', 'sri v3.8h, v14.8h, #6', 0, ()),
    ('2f2245c3', 'sri v3.2s, v14.2s, #30', 0, ()),
    ('2f2a45c3', 'sri v3.2s, v14.2s, #22', 0, ()),
    ('2f3245c3', 'sri v3.2s, v14.2s, #14', 0, ()),
    ('2f3a45c3', 'sri v3.2s, v14.2s, #6', 0, ()),
    ('6f2245c3', 'sri v3.4s, v14.4s, #30', 0, ()),
    ('6f2a45c3', 'sri v3.4s, v14.4s, #22', 0, ()),
    ('6f3245c3', 'sri v3.4s, v14.4s, #14', 0, ()),
    ('6f3a45c3', 'sri v3.4s, v14.4s, #6', 0, ()),
    ('6f4245c3', 'sri v3.2d, v14.2d, #62', 0, ()),
    ('6f4a45c3', 'sri v3.2d, v14.2d, #54', 0, ()),
    ('6f5245c3', 'sri v3.2d, v14.2d, #46', 0, ()),
    ('6f5a45c3', 'sri v3.2d, v14.2d, #38', 0, ()),
    ('6f6245c3', 'sri v3.2d, v14.2d, #30', 0, ()),
    ('6f6a45c3', 'sri v3.2d, v14.2d, #22', 0, ()),
    ('6f7245c3', 'sri v3.2d, v14.2d, #14', 0, ()),
    ('6f7a45c3', 'sri v3.2d, v14.2d, #6', 0, ()),    
    #sli
    ('2f0a55c3', 'sli v3.8b, v14.8b, #2', 0, ()),
    ('6f0a55c3', 'sli v3.16b, v14.16b, #2', 0, ()),
    ('2f1255c3', 'sli v3.4h, v14.4h, #2', 0, ()),
    ('2f1a55c3', 'sli v3.4h, v14.4h, #10', 0, ()),
    ('6f1255c3', 'sli v3.8h, v14.8h, #2', 0, ()),
    ('6f1a55c3', 'sli v3.8h, v14.8h, #10', 0, ()),
    ('2f2255c3', 'sli v3.2s, v14.2s, #2', 0, ()),
    ('2f2a55c3', 'sli v3.2s, v14.2s, #10', 0, ()),
    ('2f3255c3', 'sli v3.2s, v14.2s, #18', 0, ()),
    ('2f3a55c3', 'sli v3.2s, v14.2s, #26', 0, ()),
    ('6f2255c3', 'sli v3.4s, v14.4s, #2', 0, ()),
    ('6f2a55c3', 'sli v3.4s, v14.4s, #10', 0, ()),
    ('6f3255c3', 'sli v3.4s, v14.4s, #18', 0, ()),
    ('6f3a55c3', 'sli v3.4s, v14.4s, #26', 0, ()),
    ('6f4255c3', 'sli v3.2d, v14.2d, #2', 0, ()),
    ('6f4a55c3', 'sli v3.2d, v14.2d, #10', 0, ()),
    ('6f5255c3', 'sli v3.2d, v14.2d, #18', 0, ()),
    ('6f5a55c3', 'sli v3.2d, v14.2d, #26', 0, ()),
    ('6f6255c3', 'sli v3.2d, v14.2d, #34', 0, ()),
    ('6f6a55c3', 'sli v3.2d, v14.2d, #42', 0, ()),
    ('6f7255c3', 'sli v3.2d, v14.2d, #50', 0, ()),
    ('6f7a55c3', 'sli v3.2d, v14.2d, #58', 0, ()),
    #sqshlu
    ('2f0a65c3', 'sqshlu v3.8b, v14.8b, #2', 0, ()),
    ('6f0a65c3', 'sqshlu v3.16b, v14.16b, #2', 0, ()),
    ('2f1265c3', 'sqshlu v3.4h, v14.4h, #2', 0, ()),
    ('2f1a65c3', 'sqshlu v3.4h, v14.4h, #10', 0, ()),
    ('6f1265c3', 'sqshlu v3.8h, v14.8h, #2', 0, ()),
    ('6f1a65c3', 'sqshlu v3.8h, v14.8h, #10', 0, ()),
    ('2f2265c3', 'sqshlu v3.2s, v14.2s, #2', 0, ()),
    ('2f2a65c3', 'sqshlu v3.2s, v14.2s, #10', 0, ()),
    ('2f3265c3', 'sqshlu v3.2s, v14.2s, #18', 0, ()),
    ('2f3a65c3', 'sqshlu v3.2s, v14.2s, #26', 0, ()),
    ('6f2265c3', 'sqshlu v3.4s, v14.4s, #2', 0, ()),
    ('6f2a65c3', 'sqshlu v3.4s, v14.4s, #10', 0, ()),
    ('6f3265c3', 'sqshlu v3.4s, v14.4s, #18', 0, ()),
    ('6f3a65c3', 'sqshlu v3.4s, v14.4s, #26', 0, ()),
    ('6f4265c3', 'sqshlu v3.2d, v14.2d, #2', 0, ()),
    ('6f4a65c3', 'sqshlu v3.2d, v14.2d, #10', 0, ()),
    ('6f5265c3', 'sqshlu v3.2d, v14.2d, #18', 0, ()),
    ('6f5a65c3', 'sqshlu v3.2d, v14.2d, #26', 0, ()),
    ('6f6265c3', 'sqshlu v3.2d, v14.2d, #34', 0, ()),
    ('6f6a65c3', 'sqshlu v3.2d, v14.2d, #42', 0, ()),
    ('6f7265c3', 'sqshlu v3.2d, v14.2d, #50', 0, ()),
    ('6f7a65c3', 'sqshlu v3.2d, v14.2d, #58', 0, ()),
    #uqshl
    ('2f0a75c3', 'uqshl v3.8b, v14.8b, #2', 0, ()),
    ('6f0a75c3', 'uqshl v3.16b, v14.16b, #2', 0, ()),
    ('2f1275c3', 'uqshl v3.4h, v14.4h, #2', 0, ()),
    ('2f1a75c3', 'uqshl v3.4h, v14.4h, #10', 0, ()),
    ('6f1275c3', 'uqshl v3.8h, v14.8h, #2', 0, ()),
    ('6f1a75c3', 'uqshl v3.8h, v14.8h, #10', 0, ()),
    ('2f2275c3', 'uqshl v3.2s, v14.2s, #2', 0, ()),
    ('2f2a75c3', 'uqshl v3.2s, v14.2s, #10', 0, ()),
    ('2f3275c3', 'uqshl v3.2s, v14.2s, #18', 0, ()),
    ('2f3a75c3', 'uqshl v3.2s, v14.2s, #26', 0, ()),
    ('6f2275c3', 'uqshl v3.4s, v14.4s, #2', 0, ()),
    ('6f2a75c3', 'uqshl v3.4s, v14.4s, #10', 0, ()),
    ('6f3275c3', 'uqshl v3.4s, v14.4s, #18', 0, ()),
    ('6f3a75c3', 'uqshl v3.4s, v14.4s, #26', 0, ()),
    ('6f4275c3', 'uqshl v3.2d, v14.2d, #2', 0, ()),
    ('6f4a75c3', 'uqshl v3.2d, v14.2d, #10', 0, ()),
    ('6f5275c3', 'uqshl v3.2d, v14.2d, #18', 0, ()),
    ('6f5a75c3', 'uqshl v3.2d, v14.2d, #26', 0, ()),
    ('6f6275c3', 'uqshl v3.2d, v14.2d, #34', 0, ()),
    ('6f6a75c3', 'uqshl v3.2d, v14.2d, #42', 0, ()),
    ('6f7275c3', 'uqshl v3.2d, v14.2d, #50', 0, ()),
    ('6f7a75c3', 'uqshl v3.2d, v14.2d, #58', 0, ()),
    #sqshrun
    ('2f0a85c3', 'sqshrun{} v3.8b, v14.8h, #6', 0, ()),
    ('6f0a85c3', 'sqshrun{2} v3.16b, v14.8h, #6', 0, ()),
    ('2f1285c3', 'sqshrun{} v3.4h, v14.4s, #14', 0, ()),
    ('2f1a85c3', 'sqshrun{} v3.4h, v14.4s, #6', 0, ()),
    ('6f1285c3', 'sqshrun{2} v3.8h, v14.4s, #14', 0, ()),
    ('6f1a85c3', 'sqshrun{2} v3.8h, v14.4s, #6', 0, ()),
    ('2f2285c3', 'sqshrun{} v3.2s, v14.2d, #30', 0, ()),
    ('2f2a85c3', 'sqshrun{} v3.2s, v14.2d, #22', 0, ()),
    ('2f3285c3', 'sqshrun{} v3.2s, v14.2d, #14', 0, ()),
    ('2f3a85c3', 'sqshrun{} v3.2s, v14.2d, #6', 0, ()),
    ('6f2285c3', 'sqshrun{2} v3.4s, v14.2d, #30', 0, ()),
    ('6f2a85c3', 'sqshrun{2} v3.4s, v14.2d, #22', 0, ()),
    ('6f3285c3', 'sqshrun{2} v3.4s, v14.2d, #14', 0, ()),
    ('6f3a85c3', 'sqshrun{2} v3.4s, v14.2d, #6', 0, ()),
    #sqrshrun
    ('2f0a8dc3', 'sqrshrun{} v3.8b, v14.8h, #6', 0, ()),
    ('6f0a8dc3', 'sqrshrun{2} v3.16b, v14.8h, #6', 0, ()),
    ('2f128dc3', 'sqrshrun{} v3.4h, v14.4s, #14', 0, ()),
    ('2f1a8dc3', 'sqrshrun{} v3.4h, v14.4s, #6', 0, ()),
    ('6f128dc3', 'sqrshrun{2} v3.8h, v14.4s, #14', 0, ()),
    ('6f1a8dc3', 'sqrshrun{2} v3.8h, v14.4s, #6', 0, ()),
    ('2f228dc3', 'sqrshrun{} v3.2s, v14.2d, #30', 0, ()),
    ('2f2a8dc3', 'sqrshrun{} v3.2s, v14.2d, #22', 0, ()),
    ('2f328dc3', 'sqrshrun{} v3.2s, v14.2d, #14', 0, ()),
    ('2f3a8dc3', 'sqrshrun{} v3.2s, v14.2d, #6', 0, ()),
    ('6f228dc3', 'sqrshrun{2} v3.4s, v14.2d, #30', 0, ()),
    ('6f2a8dc3', 'sqrshrun{2} v3.4s, v14.2d, #22', 0, ()),
    ('6f328dc3', 'sqrshrun{2} v3.4s, v14.2d, #14', 0, ()),
    ('6f3a8dc3', 'sqrshrun{2} v3.4s, v14.2d, #6', 0, ()),
    #uqshrn
    ('2f0a95c3', 'uqshrn{} v3.8b, v14.8h, #6', 0, ()),
    ('6f0a95c3', 'uqshrn{2} v3.16b, v14.8h, #6', 0, ()),
    ('2f1295c3', 'uqshrn{} v3.4h, v14.4s, #14', 0, ()),
    ('2f1a95c3', 'uqshrn{} v3.4h, v14.4s, #6', 0, ()),
    ('6f1295c3', 'uqshrn{2} v3.8h, v14.4s, #14', 0, ()),
    ('6f1a95c3', 'uqshrn{2} v3.8h, v14.4s, #6', 0, ()),
    ('2f2295c3', 'uqshrn{} v3.2s, v14.2d, #30', 0, ()),
    ('2f2a95c3', 'uqshrn{} v3.2s, v14.2d, #22', 0, ()),
    ('2f3295c3', 'uqshrn{} v3.2s, v14.2d, #14', 0, ()),
    ('2f3a95c3', 'uqshrn{} v3.2s, v14.2d, #6', 0, ()),
    ('6f2295c3', 'uqshrn{2} v3.4s, v14.2d, #30', 0, ()),
    ('6f2a95c3', 'uqshrn{2} v3.4s, v14.2d, #22', 0, ()),
    ('6f3295c3', 'uqshrn{2} v3.4s, v14.2d, #14', 0, ()),
    ('6f3a95c3', 'uqshrn{2} v3.4s, v14.2d, #6', 0, ()),
    #uqrshrn
    ('2f0a9dc3', 'uqrshrn{} v3.8b, v14.8h, #6', 0, ()),
    ('6f0a9dc3', 'uqrshrn{2} v3.16b, v14.8h, #6', 0, ()),
    ('2f129dc3', 'uqrshrn{} v3.4h, v14.4s, #14', 0, ()),
    ('2f1a9dc3', 'uqrshrn{} v3.4h, v14.4s, #6', 0, ()),
    ('6f129dc3', 'uqrshrn{2} v3.8h, v14.4s, #14', 0, ()),
    ('6f1a9dc3', 'uqrshrn{2} v3.8h, v14.4s, #6', 0, ()),
    ('2f229dc3', 'uqrshrn{} v3.2s, v14.2d, #30', 0, ()),
    ('2f2a9dc3', 'uqrshrn{} v3.2s, v14.2d, #22', 0, ()),
    ('2f329dc3', 'uqrshrn{} v3.2s, v14.2d, #14', 0, ()),
    ('2f3a9dc3', 'uqrshrn{} v3.2s, v14.2d, #6', 0, ()),
    ('6f229dc3', 'uqrshrn{2} v3.4s, v14.2d, #30', 0, ()),
    ('6f2a9dc3', 'uqrshrn{2} v3.4s, v14.2d, #22', 0, ()),
    ('6f329dc3', 'uqrshrn{2} v3.4s, v14.2d, #14', 0, ()),
    ('6f3a9dc3', 'uqrshrn{2} v3.4s, v14.2d, #6', 0, ()),
    #ushll
    ('2f0aa5c3', 'ushll{} v3.8h, v14.8b, #2', 0, ()),
    ('6f0aa5c3', 'ushll{2} v3.8h, v14.16b, #2', 0, ()),
    ('2f12a5c3', 'ushll{} v3.4s, v14.4h, #2', 0, ()),
    ('2f1aa5c3', 'ushll{} v3.4s, v14.4h, #10', 0, ()),
    ('6f12a5c3', 'ushll{2} v3.4s, v14.8h, #2', 0, ()),
    ('6f1aa5c3', 'ushll{2} v3.4s, v14.8h, #10', 0, ()),
    ('2f22a5c3', 'ushll{} v3.2d, v14.2s, #2', 0, ()),
    ('2f2aa5c3', 'ushll{} v3.2d, v14.2s, #10', 0, ()),
    ('2f32a5c3', 'ushll{} v3.2d, v14.2s, #18', 0, ()),
    ('2f3aa5c3', 'ushll{} v3.2d, v14.2s, #26', 0, ()),
    ('6f22a5c3', 'ushll{2} v3.2d, v14.4s, #2', 0, ()),
    ('6f2aa5c3', 'ushll{2} v3.2d, v14.4s, #10', 0, ()),
    ('6f32a5c3', 'ushll{2} v3.2d, v14.4s, #18', 0, ()),
    ('6f3aa5c3', 'ushll{2} v3.2d, v14.4s, #26', 0, ()),
    #ucvtf
    ('2f22e5c3', 'ucvtf v3.2s, v14.2s, #30', 0, ()),
    ('2f2ae5c3', 'ucvtf v3.2s, v14.2s, #22', 0, ()),
    ('2f32e5c3', 'ucvtf v3.2s, v14.2s, #14', 0, ()),
    ('2f3ae5c3', 'ucvtf v3.2s, v14.2s, #6', 0, ()),
    ('6f22e5c3', 'ucvtf v3.4s, v14.4s, #30', 0, ()),
    ('6f2ae5c3', 'ucvtf v3.4s, v14.4s, #22', 0, ()),
    ('6f32e5c3', 'ucvtf v3.4s, v14.4s, #14', 0, ()),
    ('6f3ae5c3', 'ucvtf v3.4s, v14.4s, #6', 0, ()),
    ('6f42e5c3', 'ucvtf v3.2d, v14.2d, #62', 0, ()),
    ('6f4ae5c3', 'ucvtf v3.2d, v14.2d, #54', 0, ()),
    ('6f52e5c3', 'ucvtf v3.2d, v14.2d, #46', 0, ()),
    ('6f5ae5c3', 'ucvtf v3.2d, v14.2d, #38', 0, ()),
    ('6f62e5c3', 'ucvtf v3.2d, v14.2d, #30', 0, ()),
    ('6f6ae5c3', 'ucvtf v3.2d, v14.2d, #22', 0, ()),
    ('6f72e5c3', 'ucvtf v3.2d, v14.2d, #14', 0, ()),
    ('6f7ae5c3', 'ucvtf v3.2d, v14.2d, #6', 0, ()),
    #fcvtzu
    ('2f22fdc3', 'fcvtzu v3.2s, v14.2s, #30', 0, ()),
    ('2f2afdc3', 'fcvtzu v3.2s, v14.2s, #22', 0, ()),
    ('2f32fdc3', 'fcvtzu v3.2s, v14.2s, #14', 0, ()),
    ('2f3afdc3', 'fcvtzu v3.2s, v14.2s, #6', 0, ()),
    ('6f22fdc3', 'fcvtzu v3.4s, v14.4s, #30', 0, ()),
    ('6f2afdc3', 'fcvtzu v3.4s, v14.4s, #22', 0, ()),
    ('6f32fdc3', 'fcvtzu v3.4s, v14.4s, #14', 0, ()),
    ('6f3afdc3', 'fcvtzu v3.4s, v14.4s, #6', 0, ()),
    ('6f42fdc3', 'fcvtzu v3.2d, v14.2d, #62', 0, ()),
    ('6f4afdc3', 'fcvtzu v3.2d, v14.2d, #54', 0, ()),
    ('6f52fdc3', 'fcvtzu v3.2d, v14.2d, #46', 0, ()),
    ('6f5afdc3', 'fcvtzu v3.2d, v14.2d, #38', 0, ()),
    ('6f62fdc3', 'fcvtzu v3.2d, v14.2d, #30', 0, ()),
    ('6f6afdc3', 'fcvtzu v3.2d, v14.2d, #22', 0, ()),
    ('6f72fdc3', 'fcvtzu v3.2d, v14.2d, #14', 0, ()),
    ('6f7afdc3', 'fcvtzu v3.2d, v14.2d, #6', 0, ()),

    #AdvSIMD TBL/TBX

    ('0e0b01c3', 'tbl v3.8b, { v14.16b }, v11.8b', 0, ()),
    ('4e0b01c3', 'tbl v3.16b, { v14.16b }, v11.16b', 0, ()),
    ('0e0b11c3', 'tbx v3.8b, { v14.16b }, v11.8b', 0, ()),
    ('4e0b11c3', 'tbx v3.16b, { v14.16b }, v11.16b', 0, ()),
    ('0e0b21c3', 'tbl v3.8b, { v14.16b, v15.16b }, v11.8b', 0, ()),
    ('4e0b21c3', 'tbl v3.16b, { v14.16b, v15.16b }, v11.16b', 0, ()),
    ('0e0b31c3', 'tbx v3.8b, { v14.16b, v15.16b }, v11.8b', 0, ()),
    ('4e0b31c3', 'tbx v3.16b, { v14.16b, v15.16b }, v11.16b', 0, ()),
    ('0e0b41c3', 'tbl v3.8b, { v14.16b, v15.16b, v16.16b }, v11.8b', 0, ()),
    ('4e0b41c3', 'tbl v3.16b, { v14.16b, v15.16b, v16.16b }, v11.16b', 0, ()),
    ('0e0b51c3', 'tbx v3.8b, { v14.16b, v15.16b, v16.16b }, v11.8b', 0, ()),
    ('4e0b51c3', 'tbx v3.16b, { v14.16b, v15.16b, v16.16b }, v11.16b', 0, ()),
    ('0e0b61c3', 'tbl v3.8b, { v14.16b, v15.16b, v16.16b, v17.16b }, v11.8b', 0, ()),
    ('4e0b61c3', 'tbl v3.16b, { v14.16b, v15.16b, v16.16b, v17.16b }, v11.16b', 0, ()),
    ('0e0b71c3', 'tbx v3.8b, { v14.16b, v15.16b, v16.16b, v17.16b }, v11.8b', 0, ()),
    ('4e0b71c3', 'tbx v3.16b, { v14.16b, v15.16b, v16.16b, v17.16b }, v11.16b', 0, ()),

    #AdvSIMD ZIP/UZP/TRN

    ('0e0b19c3', 'uzp1 v3.8b, v14.8b, v11.8b', 0, ()),
    ('4e0b19c3', 'uzp1 v3.16b, v14.16b, v11.16b', 0, ()),
    ('0e4b19c3', 'uzp1 v3.4h, v14.4h, v11.4h', 0, ()),
    ('4e4b19c3', 'uzp1 v3.8h, v14.8h, v11.8h', 0, ()),
    ('0e8b19c3', 'uzp1 v3.2s, v14.2s, v11.2s', 0, ()),
    ('4e8b19c3', 'uzp1 v3.4s, v14.4s, v11.4s', 0, ()),
    ('4ecb19c3', 'uzp1 v3.2d, v14.2d, v11.2d', 0, ()),

    ('0e0b29c3', 'trn1 v3.8b, v14.8b, v11.8b', 0, ()),
    ('4e0b29c3', 'trn1 v3.16b, v14.16b, v11.16b', 0, ()),
    ('0e4b29c3', 'trn1 v3.4h, v14.4h, v11.4h', 0, ()),
    ('4e4b29c3', 'trn1 v3.8h, v14.8h, v11.8h', 0, ()),
    ('0e8b29c3', 'trn1 v3.2s, v14.2s, v11.2s', 0, ()),
    ('4e8b29c3', 'trn1 v3.4s, v14.4s, v11.4s', 0, ()),
    ('4ecb29c3', 'trn1 v3.2d, v14.2d, v11.2d', 0, ()),

    ('0e0b39c3', 'zip1 v3.8b, v14.8b, v11.8b', 0, ()),
    ('4e0b39c3', 'zip1 v3.16b, v14.16b, v11.16b', 0, ()),
    ('0e4b39c3', 'zip1 v3.4h, v14.4h, v11.4h', 0, ()),
    ('4e4b39c3', 'zip1 v3.8h, v14.8h, v11.8h', 0, ()),
    ('0e8b39c3', 'zip1 v3.2s, v14.2s, v11.2s', 0, ()),
    ('4e8b39c3', 'zip1 v3.4s, v14.4s, v11.4s', 0, ()),
    ('4ecb39c3', 'zip1 v3.2d, v14.2d, v11.2d', 0, ()),

    ('0e0b59c3', 'uzp2 v3.8b, v14.8b, v11.8b', 0, ()),
    ('4e0b59c3', 'uzp2 v3.16b, v14.16b, v11.16b', 0, ()),
    ('0e4b59c3', 'uzp2 v3.4h, v14.4h, v11.4h', 0, ()),
    ('4e4b59c3', 'uzp2 v3.8h, v14.8h, v11.8h', 0, ()),
    ('0e8b59c3', 'uzp2 v3.2s, v14.2s, v11.2s', 0, ()),
    ('4e8b59c3', 'uzp2 v3.4s, v14.4s, v11.4s', 0, ()),
    ('4ecb59c3', 'uzp2 v3.2d, v14.2d, v11.2d', 0, ()),

    ('0e0b69c3', 'trn2 v3.8b, v14.8b, v11.8b', 0, ()),
    ('4e0b69c3', 'trn2 v3.16b, v14.16b, v11.16b', 0, ()),
    ('0e4b69c3', 'trn2 v3.4h, v14.4h, v11.4h', 0, ()),
    ('4e4b69c3', 'trn2 v3.8h, v14.8h, v11.8h', 0, ()),
    ('0e8b69c3', 'trn2 v3.2s, v14.2s, v11.2s', 0, ()),
    ('4e8b69c3', 'trn2 v3.4s, v14.4s, v11.4s', 0, ()),
    ('4ecb69c3', 'trn2 v3.2d, v14.2d, v11.2d', 0, ()),

    ('0e0b79c3', 'zip2 v3.8b, v14.8b, v11.8b', 0, ()),
    ('4e0b79c3', 'zip2 v3.16b, v14.16b, v11.16b', 0, ()),
    ('0e4b79c3', 'zip2 v3.4h, v14.4h, v11.4h', 0, ()),
    ('4e4b79c3', 'zip2 v3.8h, v14.8h, v11.8h', 0, ()),
    ('0e8b79c3', 'zip2 v3.2s, v14.2s, v11.2s', 0, ()),
    ('4e8b79c3', 'zip2 v3.4s, v14.4s, v11.4s', 0, ()),
    ('4ecb79c3', 'zip2 v3.2d, v14.2d, v11.2d', 0, ()),

    #AdvSIMD EXT

    ('2e0b61c3', 'ext v3.8b, v14.8b, v11.8b, #5', 0, ()),
    ('6e0b69c3', 'ext v3.16b, v14.16b, v11.16b, #11', 0, ()),

    #AdvSIMD scalar three same

    #sqadd
    ('5e2b0dc3', 'sqadd b3, b14, b11', 0, ()),
    ('5e6b0dc3', 'sqadd h3, h14, h11', 0, ()),
    ('5eab0dc3', 'sqadd s3, s14, s11', 0, ()),
    ('5eeb0dc3', 'sqadd d3, d14, d11', 0, ()),
    #sqsub
    ('5e2b2dc3', 'sqsub b3, b14, b11', 0, ()),
    ('5e6b2dc3', 'sqsub h3, h14, h11', 0, ()),
    ('5eab2dc3', 'sqsub s3, s14, s11', 0, ()),
    ('5eeb2dc3', 'sqsub d3, d14, d11', 0, ()),
    #cmgt (register)
    ('5eeb35c3', 'cmgt d3, d14, d11', 0, ()),
    #cmge (register)
    ('5eeb3dc3', 'cmge d3, d14, d11', 0, ()),
    #sshl
    ('5eeb45c3', 'sshl d3, d14, d11', 0, ()),
    #sqshl
    ('5e2b4dc3', 'sqshl b3, b14, b11', 0, ()),
    ('5e6b4dc3', 'sqshl h3, h14, h11', 0, ()),
    ('5eab4dc3', 'sqshl s3, s14, s11', 0, ()),
    ('5eeb4dc3', 'sqshl d3, d14, d11', 0, ()),
    #srshl
    ('5eeb55c3', 'srshl d3, d14, d11', 0, ()),
    #sqrshl
    ('5e2b5dc3', 'sqrshl b3, b14, b11', 0, ()),
    ('5e6b5dc3', 'sqrshl h3, h14, h11', 0, ()),
    ('5eab5dc3', 'sqrshl s3, s14, s11', 0, ()),
    ('5eeb5dc3', 'sqrshl d3, d14, d11', 0, ()),
    #add (vector)
    ('5eeb85c3', 'add d3, d14, d11', 0, ()),
    #cmtst
    ('5eeb8dc3', 'cmtst d3, d14, d11', 0, ()),
    #sqdmulh
    ('5e6bb5c3', 'sqdmulh h3, h14, h11', 0, ()),
    ('5eabb5c3', 'sqdmulh s3, s14, s11', 0, ()),
    #fmulx
    ('5e2bddc3', 'fmulx s3, s14, s11', 0, ()),
    ('5e6bddc3', 'fmulx d3, d14, d11', 0, ()),
    #fcmeq
    ('5e2be5c3', 'fcmeq s3, s14, s11', 0, ()),
    ('5e6be5c3', 'fcmeq d3, d14, d11', 0, ()),
    #frecps
    ('5e2bfdc3', 'frecps s3, s14, s11', 0, ()),
    ('5e6bfdc3', 'frecps d3, d14, d11', 0, ()),
    #frsqrts
    ('5eabfdc3', 'frsqrts s3, s14, s11', 0, ()),
    ('5eebfdc3', 'frsqrts d3, d14, d11', 0, ()),
    #uqadd
    ('7e2b0dc3', 'uqadd b3, b14, b11', 0, ()),
    ('7e6b0dc3', 'uqadd h3, h14, h11', 0, ()),
    ('7eab0dc3', 'uqadd s3, s14, s11', 0, ()),
    ('7eeb0dc3', 'uqadd d3, d14, d11', 0, ()),
    #uqsub
    ('7e2b2dc3', 'uqsub b3, b14, b11', 0, ()),
    ('7e6b2dc3', 'uqsub h3, h14, h11', 0, ()),
    ('7eab2dc3', 'uqsub s3, s14, s11', 0, ()),
    ('7eeb2dc3', 'uqsub d3, d14, d11', 0, ()),
    #cmhi (register)
    ('7eeb35c3', 'cmhi d3, d14, d11', 0, ()),
    #cmhs (register)
    ('7eeb3dc3', 'cmhs d3, d14, d11', 0, ()),
    #ushl
    ('7eeb45c3', 'ushl d3, d14, d11', 0, ()),
    #uqshl
    ('7e2b4dc3', 'uqshl b3, b14, b11', 0, ()),
    ('7e6b4dc3', 'uqshl h3, h14, h11', 0, ()),
    ('7eab4dc3', 'uqshl s3, s14, s11', 0, ()),
    ('7eeb4dc3', 'uqshl d3, d14, d11', 0, ()),
    #urshl
    ('7eeb55c3', 'urshl d3, d14, d11', 0, ()),
    #uqrshl
    ('7e2b5dc3', 'uqrshl b3, b14, b11', 0, ()),
    ('7e6b5dc3', 'uqrshl h3, h14, h11', 0, ()),
    ('7eab5dc3', 'uqrshl s3, s14, s11', 0, ()),
    ('7eeb5dc3', 'uqrshl d3, d14, d11', 0, ()),
    #sub (vector)
    ('7eeb85c3', 'sub d3, d14, d11', 0, ()),
    #cmeq
    ('7eeb8dc3', 'cmeq d3, d14, d11', 0, ()),
    #sqrdmulh
    ('7e6bb5c3', 'sqrdmulh h3, h14, h11', 0, ()),
    ('7eabb5c3', 'sqrdmulh s3, s14, s11', 0, ()),
    #fcmge
    ('7e2be5c3', 'fcmge s3, s14, s11', 0, ()),
    ('7e6be5c3', 'fcmge d3, d14, d11', 0, ()),
    #facge
    ('7e2bedc3', 'facge s3, s14, s11', 0, ()),
    ('7e6bedc3', 'facge d3, d14, d11', 0, ()),
    #fabd
    ('7eabd5c3', 'fabd s3, s14, s11', 0, ()),
    ('7eebd5c3', 'fabd d3, d14, d11', 0, ()),
    #fcmgt (register)
    ('7eabe5c3', 'fcmgt s3, s14, s11', 0, ()),
    ('7eebe5c3', 'fcmgt d3, d14, d11', 0, ()),
    #facgt
    ('7eabedc3', 'facgt s3, s14, s11', 0, ()),
    ('7eebedc3', 'facgt d3, d14, d11', 0, ()),

    #AdvSIMD scalar three different

    #sqdmlal
    ('5e6b91c3', 'sqdmlal s3, h14, h11', 0, ()),
    ('5eab91c3', 'sqdmlal d3, s14, s11', 0, ()),
    #sqdmlsl
    ('5e6bb1c3', 'sqdmlsl s3, h14, h11', 0, ()),
    ('5eabb1c3', 'sqdmlsl d3, s14, s11', 0, ()),
    #sqdmull
    ('5e6bd1c3', 'sqdmull s3, h14, h11', 0, ()),
    ('5eabd1c3', 'sqdmull d3, s14, s11', 0, ()),

    #AdvSIMD scalar two-reg misc

    #suqadd
    ('5e2039c3', 'suqadd b3, b14', 0, ()),
    ('5e6039c3', 'suqadd h3, h14', 0, ()),
    ('5ea039c3', 'suqadd s3, s14', 0, ()),
    ('5ee039c3', 'suqadd d3, d14', 0, ()),
    #sqabs
    ('5e2079c3', 'sqabs b3, b14', 0, ()),
    ('5e6079c3', 'sqabs h3, h14', 0, ()),
    ('5ea079c3', 'sqabs s3, s14', 0, ()),
    ('5ee079c3', 'sqabs d3, d14', 0, ()),
    #cmgt (zero)
    ('5ee089c3', 'cmgt d3, d14, #0', 0, ()),
    #cmeq (zero)
    ('5ee099c3', 'cmeq d3, d14, #0', 0, ()),
    #cmlt (zero)
    ('5ee0a9c3', 'cmlt d3, d14, #0', 0, ()),
    #abs
    ('5ee0b9c3', 'abs d3, d14', 0, ()),
    #sqxtn
    ('5e2149c3', 'sqxtn b3, h14', 0, ()),
    ('5e6149c3', 'sqxtn h3, s14', 0, ()),
    ('5ea149c3', 'sqxtn s3, d14', 0, ()),
    #fcvtns (vector)
    ('5e21a9c3', 'fcvtns s3, s14', 0, ()),
    ('5e61a9c3', 'fcvtns d3, d14', 0, ()),
    #fcvtms (vector)
    ('5e21b9c3', 'fcvtms s3, s14', 0, ()),
    ('5e61b9c3', 'fcvtms d3, d14', 0, ()),
    #fcvtas (vector)
    ('5e21c9c3', 'fcvtas s3, s14', 0, ()),
    ('5e61c9c3', 'fcvtas d3, d14', 0, ()),
    #scvtf (vector, integer)
    ('5e21d9c3', 'scvtf s3, s14', 0, ()),
    ('5e61d9c3', 'scvtf d3, d14', 0, ()),
    #fcmgt (zero)
    ('5ea0c9c3', 'fcmgt s3, s14, #0', 0, ()),
    ('5ee0c9c3', 'fcmgt d3, d14, #0', 0, ()),
    #fcmeq (zero)
    ('5ea0d9c3', 'fcmeq s3, s14, #0', 0, ()),
    ('5ee0d9c3', 'fcmeq d3, d14, #0', 0, ()),
    #fcmlt (zero)
    ('5ea0e9c3', 'fcmlt s3, s14', 0, ()),
    ('5ee0e9c3', 'fcmlt d3, d14, #0', 0, ()),
    #fcvtps (zero)
    ('5ea1a9c3', 'fcvtps s3, s14', 0, ()),
    ('5ee1a9c3', 'fcvtps d3, d14', 0, ()),
    #fcvtzs (zero)
    ('5ea1b9c3', 'fcvtzs s3, s14', 0, ()),
    ('5ee1b9c3', 'fcvtzs d3, d14', 0, ()),
    #frecpe (zero)
    ('5ea1d9c3', 'frecpe s3, s14', 0, ()),
    ('5ee1d9c3', 'frecpe d3, d14', 0, ()),
    #frecpx (zero)
    ('5ea1f9c3', 'frecpx s3, s14', 0, ()),
    ('5ee1f9c3', 'frecpx d3, d14', 0, ()),
    #usqadd
    ('7e2039c3', 'usqadd b3, b14', 0, ()),
    ('7e6039c3', 'usqadd h3, h14', 0, ()),
    ('7ea039c3', 'usqadd s3, s14', 0, ()),
    ('7ee039c3', 'usqadd d3, d14', 0, ()),
    #sqneg
    ('7e2079c3', 'sqneg b3, b14', 0, ()),
    ('7e6079c3', 'sqneg h3, h14', 0, ()),
    ('7ea079c3', 'sqneg s3, s14', 0, ()),
    ('7ee079c3', 'sqneg d3, d14', 0, ()),
    #cmge (zero)
    ('7ee089c3', 'cmge d3, d14, #0', 0, ()),
    #cmle (zero)
    ('7ee099c3', 'cmle d3, d14, #0', 0, ()),
    #neg (vector)
    ('7ee0b9c3', 'neg d3, d14', 0, ()),
    #sqxtun
    ('7e2129c3', 'sqxtun b3, h14', 0, ()),
    ('7e6129c3', 'sqxtun h3, s14', 0, ()),
    ('7ea129c3', 'sqxtun s3, d14', 0, ()),
    #uqxtn
    ('7e2149c3', 'uqxtn b3, h14', 0, ()),
    ('7e6149c3', 'uqxtn h3, s14', 0, ()),
    ('7ea149c3', 'uqxtn s3, d14', 0, ()),
    #fcvtxn
    ('7e6169c3', 'fcvtxn s3, d14', 0, ()),
    #fcvtnu (vector)
    ('7e21a9c3', 'fcvtnu s3, s14', 0, ()),
    ('7e61a9c3', 'fcvtnu d3, d14', 0, ()),
    #fcvtmu (vector)
    ('7e21b9c3', 'fcvtmu s3, s14', 0, ()),
    ('7e61b9c3', 'fcvtmu d3, d14', 0, ()),
    #fcvtau (vector)
    ('7e21c9c3', 'fcvtau s3, s14', 0, ()),
    ('7e61c9c3', 'fcvtau d3, d14', 0, ()),
    #ucvtf (vector, integer)
    ('7e21d9c3', 'ucvtf s3, s14', 0, ()),
    ('7e61d9c3', 'ucvtf d3, d14', 0, ()),
    #fcmge (zero)
    ('7ea0c9c3', 'fcmge s3, s14, #0', 0, ()),
    ('7ee0c9c3', 'fcmge d3, d14, #0', 0, ()),
    #fcmle (zero)
    ('7ea0d9c3', 'fcmle s3, s14, #0', 0, ()),
    ('7ee0d9c3', 'fcmle d3, d14, #0', 0, ()),
    #fcvtpu (zero)
    ('7ea1a9c3', 'fcvtpu s3, s14', 0, ()),
    ('7ee1a9c3', 'fcvtpu d3, d14', 0, ()),
    #fcvtzu (zero)
    ('7ea1b9c3', 'fcvtzu s3, s14', 0, ()),
    ('7ee1b9c3', 'fcvtzu d3, d14', 0, ()),
    #frsqrte (zero)
    ('7ea1d9c3', 'frsqrte s3, s14', 0, ()),
    ('7ee1d9c3', 'frsqrte d3, d14', 0, ()),

    #AdvSIMD scalar pairwise

    #addp (scalar)
    ('5ef1b9c3', 'addp d3, v14.2d', 0, ()),
    #fmaxnmp (scalar)
    ('7e30c9c3', 'fmaxnmp s3, v3.2s', 0, ()),
    ('7e70c9c3', 'fmaxnmp d3, v3.2d', 0, ()),
    #faddp (scalar)
    ('7e30d9c3', 'faddp s3, v3.2s', 0, ()),
    ('7e70d9c3', 'faddp d3, v3.2d', 0, ()),
    #fmaxp (scalar)
    ('7e30f9c3', 'fmaxp s3, v3.2s', 0, ()),
    ('7e70f9c3', 'fmaxp d3, v3.2d', 0, ()),
    #fminnmp (scalar)
    ('7eb0c9c3', 'fminnmp s3, v3.2s', 0, ()),
    ('7ef0c9c3', 'fminnmp d3, v3.2d', 0, ()),
    #fminp (scalar)
    ('7eb0f9c3', 'fminp s3, v3.2s', 0, ()),
    ('7ef0f9c3', 'fminp d3, v3.2d', 0, ()),

    #AdvSIMD scalar copy

    ('5e0105c3', 'dup b3, v14.b[0]', 0, ()),
    ('5e0205c3', 'dup h3, v14.h[0]', 0, ()),
    ('5e0305c3', 'dup b3, v14.b[1]', 0, ()),
    ('5e0405c3', 'dup s3, v14.s[0]', 0, ()),
    ('5e0505c3', 'dup b3, v14.b[2]', 0, ()),
    ('5e0605c3', 'dup h3, v14.h[1]', 0, ()),
    ('5e0705c3', 'dup b3, v14.b[3]', 0, ()),
    ('5e0805c3', 'dup d3, v14.d[0]', 0, ()),
    ('5e0905c3', 'dup b3, v14.b[4]', 0, ()),
    ('5e0a05c3', 'dup h3, v14.h[2]', 0, ()),
    ('5e0b05c3', 'dup b3, v14.b[5]', 0, ()),
    ('5e0c05c3', 'dup s3, v14.s[1]', 0, ()),
    ('5e0d05c3', 'dup b3, v14.b[6]', 0, ()),
    ('5e0e05c3', 'dup h3, v14.h[3]', 0, ()),
    ('5e0f05c3', 'dup b3, v14.b[7]', 0, ()),
    ('5e1105c3', 'dup b3, v14.b[8]', 0, ()),
    ('5e1205c3', 'dup h3, v14.h[4]', 0, ()),
    ('5e1305c3', 'dup b3, v14.b[9]', 0, ()),
    ('5e1405c3', 'dup s3, v14.s[2]', 0, ()),
    ('5e1505c3', 'dup b3, v14.b[10]', 0, ()),
    ('5e1605c3', 'dup h3, v14.h[5]', 0, ()),
    ('5e1705c3', 'dup b3, v14.b[11]', 0, ()),
    ('5e1805c3', 'dup d3, v14.d[1]', 0, ()),
    ('5e1905c3', 'dup b3, v14.b[12]', 0, ()),
    ('5e1a05c3', 'dup h3, v14.h[6]', 0, ()),
    ('5e1b05c3', 'dup b3, v14.b[13]', 0, ()),
    ('5e1c05c3', 'dup s3, v14.s[3]', 0, ()),
    ('5e1d05c3', 'dup b3, v14.b[14]', 0, ()),
    ('5e1e05c3', 'dup h3, v14.h[7]', 0, ()),
    ('5e1f05c3', 'dup b3, v14.b[15]', 0, ()),

    #AdvSIMD scalar x indexed element

    #sqdmlal (by element)
    ('5f6b39c3', 'sqdmlal s3, h14, v11.h[#6]', 0, ()),
    ('5f7b39c3', 'sqdmlal s3, h14, v11.h[#7]', 0, ()),
    ('5fab39c3', 'sqdmlal d3, s14, v11.s[#3]', 0, ()),
    ('5fbb39c3', 'sqdmlal d3, s14, v27.s[#3]', 0, ()),
    #sqdmlsl (by element)
    ('5f6b79c3', 'sqdmlsl s3, h14, v11.h[#6]', 0, ()),
    ('5f7b79c3', 'sqdmlsl s3, h14, v11.h[#7]', 0, ()),
    ('5fab79c3', 'sqdmlsl d3, s14, v11.s[#3]', 0, ()),
    ('5fbb79c3', 'sqdmlsl d3, s14, v27.s[#3]', 0, ()),
    #sqdmull (by element)
    ('5f6bb9c3', 'sqdmull s3, h14, v11.h[#6]', 0, ()),
    ('5f7bb9c3', 'sqdmull s3, h14, v11.h[#7]', 0, ()),
    ('5fabb9c3', 'sqdmull d3, s14, v11.s[#3]', 0, ()),
    ('5fbbb9c3', 'sqdmull d3, s14, v27.s[#3]', 0, ()),
    #sqdmulh (by element)
    ('5f6bc9c3', 'sqdmulh h3, h14, v11.h[#6]', 0, ()),
    ('5f7bc9c3', 'sqdmulh h3, h14, v11.h[#7]', 0, ()),
    ('5fabc9c3', 'sqdmulh s3, s14, v11.s[#3]', 0, ()),
    ('5fbbc9c3', 'sqdmulh s3, s14, v27.s[#3]', 0, ()),
    #sqrdmulh (by element)
    ('5f6bd9c3', 'sqrdmulh h3, h14, v11.h[#6]', 0, ()),
    ('5f7bd9c3', 'sqrdmulh h3, h14, v11.h[#7]', 0, ()),
    ('5fabd9c3', 'sqrdmulh s3, s14, v11.s[#3]', 0, ()),
    ('5fbbd9c3', 'sqrdmulh s3, s14, v27.s[#3]', 0, ()),
    #fmla (by element)
    ('5f8bX9c3', 'fmla s3, s14, v11.s[2]', 0, ()),
    ('5fabX9c3', 'fmla s3, s14, v11.s[3]', 0, ()),
    ('5fcbX9c3', 'fmla d3, d14, v11.s[1]', 0, ()),
    #fmls (by element)
    ('5f8bX9c3', 'fmls s3, s14, v11.s[2]', 0, ()),
    ('5fabX9c3', 'fmls s3, s14, v11.s[3]', 0, ()),
    ('5fcbX9c3', 'fmls d3, d14, v11.s[1]', 0, ()),
    #fmul (by element)
    ('5f8bX9c3', 'fmul s3, s14, v11.s[2]', 0, ()),
    ('5fabX9c3', 'fmul s3, s14, v11.s[3]', 0, ()),
    ('5fcbX9c3', 'fmul d3, d14, v11.s[1]', 0, ()),
    #fmulx (by element)
    ('7f8bX9c3', 'fmulx s3, s14, v11.s[2]', 0, ()),
    ('7fabX9c3', 'fmulx s3, s14, v11.s[3]', 0, ()),
    ('7fcbX9c3', 'fmulx d3, d14, v11.s[1]', 0, ()),

    #AdvSIMD scalar shift by immediate

    #sshr
    ('5f4305c3', 'sshr d3, d14, #61', 0, ()),
    ('5f4b05c3', 'sshr d3, d14, #53', 0, ()),
    ('5f5305c3', 'sshr d3, d14, #45', 0, ()),
    ('5f5b05c3', 'sshr d3, d14, #37', 0, ()),
    ('5f6305c3', 'sshr d3, d14, #29', 0, ()),
    ('5f6b05c3', 'sshr d3, d14, #21', 0, ()),
    ('5f7305c3', 'sshr d3, d14, #13', 0, ()),
    ('5f7b05c3', 'sshr d3, d14, #5', 0, ()),
    #ssra
    ('5f4315c3', 'ssra d3, d14, #61', 0, ()),
    ('5f4b15c3', 'ssra d3, d14, #53', 0, ()),
    ('5f5315c3', 'ssra d3, d14, #45', 0, ()),
    ('5f5b15c3', 'ssra d3, d14, #37', 0, ()),
    ('5f6315c3', 'ssra d3, d14, #29', 0, ()),
    ('5f6b15c3', 'ssra d3, d14, #21', 0, ()),
    ('5f7315c3', 'ssra d3, d14, #13', 0, ()),
    ('5f7b15c3', 'ssra d3, d14, #5', 0, ()),
    #srshr
    ('5f4325c3', 'srshr d3, d14, #61', 0, ()),
    ('5f4b25c3', 'srshr d3, d14, #53', 0, ()),
    ('5f5325c3', 'srshr d3, d14, #45', 0, ()),
    ('5f5b25c3', 'srshr d3, d14, #37', 0, ()),
    ('5f6325c3', 'srshr d3, d14, #29', 0, ()),
    ('5f6b25c3', 'srshr d3, d14, #21', 0, ()),
    ('5f7325c3', 'srshr d3, d14, #13', 0, ()),
    ('5f7b25c3', 'srshr d3, d14, #5', 0, ()),
    #srsra
    ('5f4335c3', 'srsra d3, d14, #61', 0, ()),
    ('5f4b35c3', 'srsra d3, d14, #53', 0, ()),
    ('5f5335c3', 'srsra d3, d14, #45', 0, ()),
    ('5f5b35c3', 'srsra d3, d14, #37', 0, ()),
    ('5f6335c3', 'srsra d3, d14, #29', 0, ()),
    ('5f6b35c3', 'srsra d3, d14, #21', 0, ()),
    ('5f7335c3', 'srsra d3, d14, #13', 0, ()),
    ('5f7b35c3', 'srsra d3, d14, #5', 0, ()),
    #shl
    ('5f4355c3', 'shl d3, d14, #3', 0, ()),
    ('5f4b55c3', 'shl d3, d14, #11', 0, ()),
    ('5f5355c3', 'shl d3, d14, #19', 0, ()),
    ('5f5b55c3', 'shl d3, d14, #27', 0, ()),
    ('5f6355c3', 'shl d3, d14, #35', 0, ()),
    ('5f6b55c3', 'shl d3, d14, #43', 0, ()),
    ('5f7355c3', 'shl d3, d14, #51', 0, ()),
    ('5f7b55c3', 'shl d3, d14, #59', 0, ()),
    #sqshl
    ('5f0b75c3', 'sqshl b3, b14, #3', 0, ()),
    ('5f1375c3', 'sqshl h3, h14, #3', 0, ()),
    ('5f1b75c3', 'sqshl h3, h14, #11', 0, ()),
    ('5f2375c3', 'sqshl s3, s14, #3', 0, ()),
    ('5f2b75c3', 'sqshl s3, s14, #11', 0, ()),
    ('5f3375c3', 'sqshl s3, s14, #19', 0, ()),
    ('5f3b75c3', 'sqshl s3, s14, #27', 0, ()),
    ('5f4375c3', 'sqshl d3, d14, #3', 0, ()),
    ('5f4b75c3', 'sqshl d3, d14, #11', 0, ()),
    ('5f5375c3', 'sqshl d3, d14, #19', 0, ()),
    ('5f5b75c3', 'sqshl d3, d14, #27', 0, ()),
    ('5f6375c3', 'sqshl d3, d14, #35', 0, ()),
    ('5f6b75c3', 'sqshl d3, d14, #43', 0, ()),
    ('5f7375c3', 'sqshl d3, d14, #51', 0, ()),
    ('5f7b75c3', 'sqshl d3, d14, #59', 0, ()),
    #sqshrn
    ('5f0b95c3', 'sqshrn b3, h14, #5', 0, ()),
    ('5f1395c3', 'sqshrn h3, s14, #13', 0, ()),
    ('5f1b95c3', 'sqshrn h3, s14, #5', 0, ()),
    ('5f2395c3', 'sqshrn s3, d14, #29', 0, ()),
    ('5f2b95c3', 'sqshrn s3, d14, #21', 0, ()),
    ('5f3395c3', 'sqshrn s3, d14, #13', 0, ()),
    ('5f3b95c3', 'sqshrn s3, d14, #5', 0, ()),
    #sqrshrn
    ('5f0b9dc3', 'sqrshrn b3, h14, #5', 0, ()),
    ('5f139dc3', 'sqrshrn h3, s14, #13', 0, ()),
    ('5f1b9dc3', 'sqrshrn h3, s14, #5', 0, ()),
    ('5f239dc3', 'sqrshrn s3, d14, #29', 0, ()),
    ('5f2b9dc3', 'sqrshrn s3, d14, #21', 0, ()),
    ('5f339dc3', 'sqrshrn s3, d14, #13', 0, ()),
    ('5f3b9dc3', 'sqrshrn s3, d14, #5', 0, ()),
    #scvtf
    ('5f23e5c3', 'scvtf s3, s14, #29', 0, ()),
    ('5f2be5c3', 'scvtf s3, s14, #21', 0, ()),
    ('5f33e5c3', 'scvtf s3, s14, #13', 0, ()),
    ('5f3be5c3', 'scvtf s3, s14, #5', 0, ()),
    ('5f43e5c3', 'scvtf d3, d14, #61', 0, ()),
    ('5f4be5c3', 'scvtf d3, d14, #53', 0, ()),
    ('5f53e5c3', 'scvtf d3, d14, #45', 0, ()),
    ('5f5be5c3', 'scvtf d3, d14, #37', 0, ()),
    ('5f63e5c3', 'scvtf d3, d14, #29', 0, ()),
    ('5f6be5c3', 'scvtf d3, d14, #21', 0, ()),
    ('5f73e5c3', 'scvtf d3, d14, #13', 0, ()),
    ('5f7be5c3', 'scvtf d3, d14, #5', 0, ()),
    #fcvtzs
    ('5f23fdc3', 'fcvtzs s3, s14, #29', 0, ()),
    ('5f2bfdc3', 'fcvtzs s3, s14, #21', 0, ()),
    ('5f33fdc3', 'fcvtzs s3, s14, #13', 0, ()),
    ('5f3bfdc3', 'fcvtzs s3, s14, #5', 0, ()),
    ('5f43fdc3', 'fcvtzs d3, d14, #61', 0, ()),
    ('5f4bfdc3', 'fcvtzs d3, d14, #53', 0, ()),
    ('5f53fdc3', 'fcvtzs d3, d14, #45', 0, ()),
    ('5f5bfdc3', 'fcvtzs d3, d14, #37', 0, ()),
    ('5f63fdc3', 'fcvtzs d3, d14, #29', 0, ()),
    ('5f6bfdc3', 'fcvtzs d3, d14, #21', 0, ()),
    ('5f73fdc3', 'fcvtzs d3, d14, #13', 0, ()),
    ('5f7bfdc3', 'fcvtzs d3, d14, #5', 0, ()),
    #ushr
    ('7f4305c3', 'ushr d3, d14, #61', 0, ()),
    ('7f4b05c3', 'ushr d3, d14, #53', 0, ()),
    ('7f5305c3', 'ushr d3, d14, #45', 0, ()),
    ('7f5b05c3', 'ushr d3, d14, #37', 0, ()),
    ('7f6305c3', 'ushr d3, d14, #29', 0, ()),
    ('7f6b05c3', 'ushr d3, d14, #21', 0, ()),
    ('7f7305c3', 'ushr d3, d14, #13', 0, ()),
    ('7f7b05c3', 'ushr d3, d14, #5', 0, ()),
    #usra
    ('7f4315c3', 'usra d3, d14, #61', 0, ()),
    ('7f4b15c3', 'usra d3, d14, #53', 0, ()),
    ('7f5315c3', 'usra d3, d14, #45', 0, ()),
    ('7f5b15c3', 'usra d3, d14, #37', 0, ()),
    ('7f6315c3', 'usra d3, d14, #29', 0, ()),
    ('7f6b15c3', 'usra d3, d14, #21', 0, ()),
    ('7f7315c3', 'usra d3, d14, #13', 0, ()),
    ('7f7b15c3', 'usra d3, d14, #5', 0, ()),
    #urshr
    ('7f4325c3', 'urshr d3, d14, #61', 0, ()),
    ('7f4b25c3', 'urshr d3, d14, #53', 0, ()),
    ('7f5325c3', 'urshr d3, d14, #45', 0, ()),
    ('7f5b25c3', 'urshr d3, d14, #37', 0, ()),
    ('7f6325c3', 'urshr d3, d14, #29', 0, ()),
    ('7f6b25c3', 'urshr d3, d14, #21', 0, ()),
    ('7f7325c3', 'urshr d3, d14, #13', 0, ()),
    ('7f7b25c3', 'urshr d3, d14, #5', 0, ()),
    #ursra
    ('7f4335c3', 'ursra d3, d14, #61', 0, ()),
    ('7f4b35c3', 'ursra d3, d14, #53', 0, ()),
    ('7f5335c3', 'ursra d3, d14, #45', 0, ()),
    ('7f5b35c3', 'ursra d3, d14, #37', 0, ()),
    ('7f6335c3', 'ursra d3, d14, #29', 0, ()),
    ('7f6b35c3', 'ursra d3, d14, #21', 0, ()),
    ('7f7335c3', 'ursra d3, d14, #13', 0, ()),
    ('7f7b35c3', 'ursra d3, d14, #5', 0, ()),
    #sri
    ('7f4345c3', 'sri d3, d14, #61', 0, ()),
    ('7f4b45c3', 'sri d3, d14, #53', 0, ()),
    ('7f5345c3', 'sri d3, d14, #45', 0, ()),
    ('7f5b45c3', 'sri d3, d14, #37', 0, ()),
    ('7f6345c3', 'sri d3, d14, #29', 0, ()),
    ('7f6b45c3', 'sri d3, d14, #21', 0, ()),
    ('7f7345c3', 'sri d3, d14, #13', 0, ()),
    ('7f7b45c3', 'sri d3, d14, #5', 0, ()), 
    #sli
    ('7f4355c3', 'sli d3, d14, #3', 0, ()),
    ('7f4b55c3', 'sli d3, d14, #11', 0, ()),
    ('7f5355c3', 'sli d3, d14, #19', 0, ()),
    ('7f5b55c3', 'sli d3, d14, #27', 0, ()),
    ('7f6355c3', 'sli d3, d14, #35', 0, ()),
    ('7f6b55c3', 'sli d3, d14, #43', 0, ()),
    ('7f7355c3', 'sli d3, d14, #51', 0, ()),
    ('7f7b55c3', 'sli d3, d14, #59', 0, ()),
    #sqshlu
    ('7f0b65c3', 'sqshlu b3, b14, #3', 0, ()),
    ('7f1365c3', 'sqshlu h3, h14, #3', 0, ()),
    ('7f1b65c3', 'sqshlu h3, h14, #11', 0, ()),
    ('7f2365c3', 'sqshlu s3, s14, #3', 0, ()),
    ('7f2b65c3', 'sqshlu s3, s14, #11', 0, ()),
    ('7f3365c3', 'sqshlu s3, s14, #19', 0, ()),
    ('7f3b65c3', 'sqshlu s3, s14, #27', 0, ()),
    ('7f4365c3', 'sqshlu d3, d14, #3', 0, ()),
    ('7f4b65c3', 'sqshlu d3, d14, #11', 0, ()),
    ('7f5365c3', 'sqshlu d3, d14, #19', 0, ()),
    ('7f5b65c3', 'sqshlu d3, d14, #27', 0, ()),
    ('7f6365c3', 'sqshlu d3, d14, #35', 0, ()),
    ('7f6b65c3', 'sqshlu d3, d14, #43', 0, ()),
    ('7f7365c3', 'sqshlu d3, d14, #51', 0, ()),
    ('7f7b65c3', 'sqshlu d3, d14, #59', 0, ()),
    #uqshl
    ('7f0b75c3', 'uqshl b3, b14, #3', 0, ()),
    ('7f1375c3', 'uqshl h3, h14, #3', 0, ()),
    ('7f1b75c3', 'uqshl h3, h14, #11', 0, ()),
    ('7f2375c3', 'uqshl s3, s14, #3', 0, ()),
    ('7f2b75c3', 'uqshl s3, s14, #11', 0, ()),
    ('7f3375c3', 'uqshl s3, s14, #19', 0, ()),
    ('7f3b75c3', 'uqshl s3, s14, #27', 0, ()),
    ('7f4375c3', 'uqshl d3, d14, #3', 0, ()),
    ('7f4b75c3', 'uqshl d3, d14, #11', 0, ()),
    ('7f5375c3', 'uqshl d3, d14, #19', 0, ()),
    ('7f5b75c3', 'uqshl d3, d14, #27', 0, ()),
    ('7f6375c3', 'uqshl d3, d14, #35', 0, ()),
    ('7f6b75c3', 'uqshl d3, d14, #43', 0, ()),
    ('7f7375c3', 'uqshl d3, d14, #51', 0, ()),
    ('7f7b75c3', 'uqshl d3, d14, #59', 0, ()),
    #sqshrun
    ('7f0b85c3', 'sqshrun b3, h14, #5', 0, ()),
    ('7f1385c3', 'sqshrun h3, s14, #13', 0, ()),
    ('7f1b85c3', 'sqshrun h3, s14, #5', 0, ()),
    ('7f2385c3', 'sqshrun s3, d14, #29', 0, ()),
    ('7f2b85c3', 'sqshrun s3, d14, #21', 0, ()),
    ('7f3385c3', 'sqshrun s3, d14, #13', 0, ()),
    ('7f3b85c3', 'sqshrun s3, d14, #5', 0, ()),
    #sqrshrun
    ('7f0b8dc3', 'sqrshrun b3, h14, #5', 0, ()),
    ('7f138dc3', 'sqrshrun h3, s14, #13', 0, ()),
    ('7f1b8dc3', 'sqrshrun h3, s14, #5', 0, ()),
    ('7f238dc3', 'sqrshrun s3, d14, #29', 0, ()),
    ('7f2b8dc3', 'sqrshrun s3, d14, #21', 0, ()),
    ('7f338dc3', 'sqrshrun s3, d14, #13', 0, ()),
    ('7f3b8dc3', 'sqrshrun s3, d14, #5', 0, ()),
    #uqshrn
    ('7f0b95c3', 'uqshrn b3, h14, #5', 0, ()),
    ('7f1395c3', 'uqshrn h3, s14, #13', 0, ()),
    ('7f1b95c3', 'uqshrn h3, s14, #5', 0, ()),
    ('7f2395c3', 'uqshrn s3, d14, #29', 0, ()),
    ('7f2b95c3', 'uqshrn s3, d14, #21', 0, ()),
    ('7f3395c3', 'uqshrn s3, d14, #13', 0, ()),
    ('7f3b95c3', 'uqshrn s3, d14, #5', 0, ()),
    #uqrshrn
    ('7f0b9dc3', 'uqrshrn b3, h14, #5', 0, ()),
    ('7f139dc3', 'uqrshrn h3, s14, #13', 0, ()),
    ('7f1b9dc3', 'uqrshrn h3, s14, #5', 0, ()),
    ('7f239dc3', 'uqrshrn s3, d14, #29', 0, ()),
    ('7f2b9dc3', 'uqrshrn s3, d14, #21', 0, ()),
    ('7f339dc3', 'uqrshrn s3, d14, #13', 0, ()),
    ('7f3b9dc3', 'uqrshrn s3, d14, #5', 0, ()),
    #ucvtf
    ('7f23e5c3', 'ucvtf s3, s14, #29', 0, ()),
    ('7f2be5c3', 'ucvtf s3, s14, #21', 0, ()),
    ('7f33e5c3', 'ucvtf s3, s14, #13', 0, ()),
    ('7f3be5c3', 'ucvtf s3, s14, #5', 0, ()),
    ('7f43e5c3', 'ucvtf d3, d14, #61', 0, ()),
    ('7f4be5c3', 'ucvtf d3, d14, #53', 0, ()),
    ('7f53e5c3', 'ucvtf d3, d14, #45', 0, ()),
    ('7f5be5c3', 'ucvtf d3, d14, #37', 0, ()),
    ('7f63e5c3', 'ucvtf d3, d14, #29', 0, ()),
    ('7f6be5c3', 'ucvtf d3, d14, #21', 0, ()),
    ('7f73e5c3', 'ucvtf d3, d14, #13', 0, ()),
    ('7f7be5c3', 'ucvtf d3, d14, #5', 0, ()),
    #fcvtzu
    ('7f23fdc3', 'fcvtzu s3, s14, #29', 0, ()),
    ('7f2bfdc3', 'fcvtzu s3, s14, #21', 0, ()),
    ('7f33fdc3', 'fcvtzu s3, s14, #13', 0, ()),
    ('7f3bfdc3', 'fcvtzu s3, s14, #5', 0, ()),
    ('7f43fdc3', 'fcvtzu d3, d14, #61', 0, ()),
    ('7f4bfdc3', 'fcvtzu d3, d14, #53', 0, ()),
    ('7f53fdc3', 'fcvtzu d3, d14, #45', 0, ()),
    ('7f5bfdc3', 'fcvtzu d3, d14, #37', 0, ()),
    ('7f63fdc3', 'fcvtzu d3, d14, #29', 0, ()),
    ('7f6bfdc3', 'fcvtzu d3, d14, #21', 0, ()),
    ('7f73fdc3', 'fcvtzu d3, d14, #13', 0, ()),
    ('7f7bfdc3', 'fcvtzu d3, d14, #5', 0, ()),

    #Crypto AES

    ('4e2849c3', 'aese v3.16b, v14.16b', 0, ()),
    ('4e2859c3', 'aesd v3.16b, v14.16b', 0, ()),
    ('4e2869c3', 'aesmc v3.16b, v14.16b', 0, ()),
    ('4e2879c3', 'aesimc v3.16b, v14.16b', 0, ()),

    #Crypto three-reg SHA

    ('5e0b01c3', 'sha1c q3, s14, v11.4s', 0, ()),
    ('5e0b11c3', 'sha1p q3, s14, v11.4s', 0, ()),
    ('5e0b21c3', 'sha1m q3, s14, v11.4s', 0, ()),
    ('5e0b31c3', 'sha1su0 v3.4s, v14.4s, v11.4s', 0, ()),
    ('5e0b41c3', 'sha256h q3, q14, v11.4s', 0, ()),
    ('5e0b51c3', 'sha256h2 q3, q14, v11.4s', 0, ()),
    ('5e0b61c3', 'sha256su1 v3.4s, v14.4s, v11.4s', 0, ()),

    #Crypto two-reg SHA

    ('5e2809c3', 'sha1h s3, s14', 0, ()),
    ('5e2819c3', 'sha1su1 v3.4s, v14.4s', 0, ()),
    ('5e2829c3', 'sha256su0 v3.4s, v14.4s', 0, ()),
]


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

        '''
        for bytez, reprOp, iflags, emutests in instrs_bigend:
            va = 0
            try:
                self._do_test(emu, va, bytez, reprOp, iflags, emutests, stats)
            except Exception as e:
                stats['badcount'] += 1
                
                print("Exception: %r" % e)
                import traceback
                traceback.print_exc()
        '''
        line = 1

        for va, bytez, reprOp, iflags, emutests in instrs:
            try:
                self._do_test(emu, va, bytez, reprOp, iflags, emutests, stats, line)
            except Exception as e:
                stats['badcount'] += 1
                
                print("Exception while parsing %s (%s): %r" % (bytez, reprOp, e))
                import traceback
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

def doBinjaGrab(filename='output_linux_arm_vuln.elf'):
    import binaryninja
    bv = binaryninja.open_view(filename)
    bv.save(filename+'.bndb')

    testdata = []
    for f in bv.functions:
        #print (f)
        for instr, va in f.instructions:
            testdata.append((va, bv.read(va, 4), instr))

    done = []
    outlines = []
    for va, bytez, oparry in testdata:
        if bytez in done:
            print("skipping existing instruction...")
            continue
        done.append(bytez)
        outlines.append("    (0x%x, '%s', %r, 0, ())," % (va, bytez.hex(), ''.join([str(x) for x in oparry])))

    return outlines


