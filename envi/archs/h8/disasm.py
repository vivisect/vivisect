import sys
import struct
import traceback

import envi
import envi.bits as e_bits

from envi.bits import binary

'''
mov b/w/l
movfpe b
movtpe b
pop  w/l
push w/l
--
add/sub b/w/l   add.b, add.w, add.l
addx/subx b
inc/dec b/w/l
adds/subs l
daa/das b
mulxs b/w
mulxu b/w
divxs b/w
divxu b/w
cmp b/w/l
neg b/w/l
exts w/l
extu w/l
and b/w/l
or  b/w/l
xor b/w/l
not b/w/l
--
shal/shar b/w/l
shll/shlr b/w/l
rotl/rotr b/w/l
rotxl/rotxr b/w/l
bset b
bclr b
bnot b
btst b
bad b
biand b
--
bor b
bior b
bxor b
bixor b
bld b
bild b
bst b
bist b
--
bcc bra/bt brn/bf bhi bls bhs bcs/blo bne beq bvc bvs bpl bmi bge blt bgt ble
jmp
bsr
jsr
rts
--
trapa
rte
sleep
ldc b/w
stc b/w
andc b
orc b
xorc b
nop
--
eepmov.b
eepmov.w


'''


class H8Opcode(envi.Opcode):

    def __hash__(self):
        return int(hash(self.mnem) ^ (self.size << 4))

    def __len__(self):
        return int(self.size)

    def getBranches(self, emu=None):
        """
        Return a list of tuples.  Each tuple contains the target VA of the
        branch, and a possible set of flags showing what type of branch it is.

        See the BR_FOO types for all the supported envi branch flags....
        Example: for bva,bflags in op.getBranches():
        """
        ret = []

        if not self.iflags & envi.IF_NOFALL:
            ret.append((self.va + self.size, envi.BR_FALL | self._def_arch))

        return ret

    def render(self, mcanv):
        """
        Render this opcode to the specified memory canvas
        """
        mnem = self.mnem + cond_codes.get(self.prefixes)
        daib_flags = self.iflags & IF_DAIB_MASK
        if self.iflags & IF_L:
            mnem += 'l'
        elif self.iflags & IF_PSR_S:
            mnem += 's'
        elif daib_flags > 0:
            idx = ((daib_flags)>>(IF_DAIB_SHFT)) 
            mnem += daib[idx]
        else:
            if self.iflags & IF_S:
                mnem += 's'
            if self.iflags & IF_D:
                mnem += 'd'
            if self.iflags & IF_B:
                mnem += 'b'
            if self.iflags & IF_H:
                mnem += 'h'
            elif self.iflags & IF_T:
                mnem += 't'
        #FIXME: Advanced SIMD modifiers (IF_V*)
        if self.iflags & IF_THUMB32:
            mnem += ".w"

        mcanv.addNameText(mnem, typename="mnemonic")
        mcanv.addText(" ")

        # Allow each of our operands to render
        imax = len(self.opers)
        lasti = imax - 1
        for i in xrange(imax):
            oper = self.opers[i]
            oper.render(mcanv, self, i)
            if i != lasti:
                mcanv.addText(",")
        #if self.iflags & IF_W:     # handled in operand.  still keeping flag to indicate this instruction writes back
        #    mcanc.addText(" !")

    def __repr__(self):
        mnem = self.mnem + cond_codes.get(self.prefixes)
        daib_flags = self.iflags & IF_DAIB_MASK
        if self.iflags & IF_L:
            mnem += 'l'
        elif self.iflags & IF_PSR_S:
            mnem += 's'
        elif daib_flags > 0:
            idx = ((daib_flags)>>(IF_DAIB_SHFT)) 
            mnem += daib[idx]
        else:
            if self.iflags & IF_S:
                mnem += 's'
            if self.iflags & IF_D:
                mnem += 'd'
            if self.iflags & IF_B:
                mnem += 'b'
            if self.iflags & IF_H:
                mnem += 'h'
            elif self.iflags & IF_T:
                mnem += 't'
        if self.iflags & IF_THUMB32:
            mnem += ".w"
        
        x = []
        
        for o in self.opers:
            x.append(o.repr(self))
        #if self.iflags & IF_W:     # handled in operand.  still keeping flag to indicate this instruction writes back
        #    x[-1] += " !"      
        return mnem + " " + ", ".join(x)



def unittest_parsers(buf = 'ABCDEFGHIJKLMNOP', off=3, va=0x2544):
    val, = struct.unpack('>H', buf[off:off+2])

    for tsize in (1,2,4):
        p_i3_Rd(va, val, buf, off, tsize)
        p_i3_aERd(va, val, buf, off, tsize) 
        p_i3_aAA8(va, val, buf, off, tsize) 
        p_i8_CCR(va, val, buf, off, tsize) 
        p_i8_Rd(va, val, buf, off, tsize) 
        p_i16_Rd(va, val, buf, off, tsize) 
        p_i32_ERd(va, val, buf, off, tsize) 
        p_Rd(va, val, buf, off, tsize) 
        p_Rs_Rd(va, val, buf, off, tsize)  
        p_Rs_Rd_4b(va, val, buf, off, tsize)  
        p_Rs_ERd(va, val, buf, off, tsize)  
        p_Rs_ERd_4b(va, val, buf, off, tsize)  
        p_ERd(va, val, buf, off, tsize)  
        p_ERs_ERd(va, val, buf, off, tsize)  
        p_Rn_Rd(va, val, buf, off, tsize)  
        p_Rn_aERd(va, val, buf, off, tsize)  
        p_Rn_aAA8(va, val, buf, off, tsize)  
        p_aERn(va, val, buf, off, tsize)  
        p_aAA24(va, val, buf, off, tsize)  
        p_aaAA8(va, val, buf, off, tsize)  
        p_1_Rd(va, val, buf, off, tsize)  
        p_2_Rd(va, val, buf, off, tsize)  
        p_4_Rd(va, val, buf, off, tsize)  
        p_1_ERd(va, val, buf, off, tsize)  
        p_2_ERd(va, val, buf, off, tsize)  
        p_4_ERd(va, val, buf, off, tsize)  
        p_disp8(va, val, buf, off, tsize)  
        p_dis16(va, val, buf, off, tsize)  
        p_nooperands(va, val, buf, off, tsize) 

class H8Operand(envi.Operand):
    tsize = 2
    def involvesPC(self):
        return False

class H8RegDirOper(H8Operand):
    ''' register operand. '''

    def __init__(self, reg, va=0, oflags=0):
        self.va = va
        self.reg = reg
        self.oflags = oflags

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.reg != oper.reg:
            return False
        if self.oflags != oper.oflags:
            return False
        return True
    
    def involvesPC(self):
        return self.reg == REG_PC

    def isDeref(self):
        return False

    def getOperValue(self, op, emu=None):
        if self.reg == REG_PC:
            return self.va  # FIXME: is this modified?  or do we need to att # to this?

        if emu == None:
            return None
        return emu.getRegister(self.reg)

    def setOperValue(self, op, emu=None, val=None):
        if emu == None:
            return None
        emu.setRegister(self.reg, val)

    def render(self, mcanv, op, idx):
        name = self._dis_regctx.getRegisterName(self.reg)
        rname = self._dis_regctx.getRegisterName(self.reg&RMETA_NMASK)
        mcanv.addNameText(name, name=rname, typename="registers")

    def repr(self, op):
        name = self._dis_regctx.getRegisterName(self.reg)
        rname = self._dis_regctx.getRegisterName(self.reg&RMETA_NMASK)
        return rname

class H8RegIndirOper(H8Operand):
    '''
    Register Indirect
    register specifies 32bit ERn reg, lower 24bits being an address

    FIXME: some instructions use "@ERd" but seem to mean "ERd"??  check docs.
    '''

    def __init__(self, reg, va, tsize, disp=0, oflags=0):
        self.va = va
        self.reg = reg
        self.disp = disp
        self.tsize = tsize
        self.oflags = oflags

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.reg != oper.reg:
            return False
        if self.disp != oper.disp:
            return False
        if self.oflags != oper.oflags:
            return False
        return True

    def involvesPC(self):
        return self.reg == REG_PC

    def isDeref(self):
        return True

    def getOperAddr(self, op, emu=None, mod=False):
        '''
        if mod==True, actually update the register for PostInc/PreDec
        '''
        addr = self.disp
        if self.oflags & OF_PREDEC:
            addr -= self.tsize

        if self.reg == REG_PC:
            addr += self.va
            return addr

        if emu == None:
            return None

        addr += emu.getRegister(self.reg)

        if mod:
            if self.oflags & OF_PREDEC:
                emu.setRegister(emu.getRegister(self.reg) - self.tsize)
            elif self.oflags & OF_POSTINC:
                emu.setRegister(emu.getRegister(self.reg) + self.tsize)

        return addr

    def getOperValue(self, op, emu=None, mod=False):
        if emu == None:
            return None
        addr = self.getOperAddr( op, emu, mod )
        return emu.readMemValue(self.reg, self.tsize)

    def render(self, mcanv, op, idx):
        name = self._dis_regctx.getRegisterName(self.reg)
        rname = self._dis_regctx.getRegisterName(self.reg&RMETA_NMASK)
        mcanv.addText('@')
        if self.disp:
            mcanv.addText('(%d, ' % self.disp)
        if self.oflags & OF_PREDEC:
            mcanv.addText('-')
        mcanv.addNameText(name, name=rname, typename="registers")
        if self.oflags & OF_POSTINC:
            mcanv.addText('+')
        if self.disp:
            mcanv.addText(')')

    def repr(self, op):
        ''' unfixed '''
        out = ['@']
        name = self._dis_regctx.getRegisterName(self.reg)
        rname = self._dis_regctx.getRegisterName(self.reg&RMETA_NMASK)
        if self.disp:
            out.append('(%d, ' % self.disp)

        if self.oflags & OF_PREDEC:
            out.append('-')

        out.append(rname)

        if self.oflags & OF_POSTINC:
            out.append('+')

        if self.disp:
            out.append(')')
        return ''.join(out)

class H8AbsAddrOper(H8Operand):
    '''
    Absolute Address
    '''
    def __init__(self, aa):
        self.aa = aa

    def __eq__(self, oper):
        ''' unfixed '''
        if not isinstance(oper, self.__class__):
            return False
        if self.aa != oper.aa:
            return False
        return True

    def involvesPC(self):
        return False

    def isDeref(self):
        return False

    def getOperValue(self, op, emu=None):
        return self.aa

    def render(self, mcanv, op, idx):
        mcanv.addText('@')
        mcanv.addNameText('%x'%self.aa, name=self.aa, typename='address')

    def repr(self, op):
        return '@%x' % self.aa

class H8ImmOper(H8Operand):
    '''
    Immediate Operand
    '''
    def __init__(self, val):
        self.val = val

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.val != oper.val:
            return False
        return True

    def involvesPC(self):
        return False

    def isDeref(self):
        return False

    def getOperValue(self, op, emu=None):
        return self.val

    def render(self, mcanv, op, idx):
        mcanv.addText('#')
        mcanv.addNameText('%x' % self.val, typename='immediate')

    def repr(self, op):
        return "#%x" % self.val

class H8MemIndirOper(H8Operand):
    '''
    Memory Indirect
    '''
    def __init__(self, aa):
        self.aa = aa

    def __eq__(self, oper):
        ''' unfixed '''
        if not isinstance(oper, self.__class__):
            return False
        if self.aa != oper.aa:
            return False
        return True

    def involvesPC(self):
        return False

    def isDeref(self):
        return True

    def getOperValue(self, op, emu=None):
        # can't survive without an emulator
        if emu == None:
            return None

        addr = self.getOperAddr(op, emu)
        ret = emu.readMemoryValue(addr, self.tsize)
        return ret

    def getOperAddr(self, op, emu=None):
        return self.aa

    def render(self, mcanv, op, idx):
        mcanv.addText('@@')
        mcanv.addNameText('%x'%self.aa, name=self.aa, typename='address')

    def repr(self, op):
        return '@@%x' % self.aa

class H8PcOffsetOper(H8Operand):
    '''
    PC Relative Address

    H8ImmOper but for Branches, not a dereference.  perhaps we can have H8ImmOper do all the things... but for now we have this.
    '''
    def __init__(self, val, va):
        self.va = va
        self.val = val

    def __eq__(self, oper):
        ''' unfixed '''
        if not isinstance(oper, self.__class__):
            return False
        if self.val != oper.val:
            return False
        if self.va != oper.va:
            return False
        return True

    def involvesPC(self):
        return True

    def isDeref(self):
        return False

    def isDiscrete(self):
        return False

    def getOperValue(self, op, emu=None):
        return self.va + self.val

    def render(self, mcanv, op, idx):
        value = self.getOperValue(op)
        if mcanv.mem.isValidPointer(value):
            name = addrToName(mcanv, value)
            mcanv.addVaText(name, value)
        else:
            mcanv.addVaText('%.4x' % value, value)

    def repr(self, op):
        targ = self.getOperValue(op)
        tname = "#%.4x" % targ
        return tname


def p_i3_Rd(va, val, buf, off, tsize):
    # band, bclr, biand, bild, bior, bist, bixor, bld, bnot, bor, bset, bst, btst, bxor
    iflags = 0
    op = val >> 7
    i3 = (val >> 4) & 0x7
    Rd = val & 0xf

    opers = (
            H8ImmOper(i3),
            H8RegDirOper(Rd, va, 0),
            )
    return (op, None, opers, iflags, 2)

def p_i3_aERd(va, val, buf, off, tsize): 
    # band, bclr, biand, bild, bior, bist, bixor, bld, bnot, bor, bset, bst, btst, bxor
    val2, = struct.unpack('>H', buf[off+2: off+4])

    iflags = 0
    op = ((((val >> 3)&0xfff0) | (val&0xf))<<13) | ((val2>>3)&0xfff0) | (val&0xf)
    i3 = (val2 >> 4) & 0x7
    ERd = (val >> 4) & 0x7

    opers = (
            H8ImmOper(i3),
            H8RegIndirOper(ERd, va, tsize, 0),
            )
    return (op, None, opers, iflags, 4)

def p_i3_aAA8(va, val, buf, off, tsize): 
    # band, bclr, biand, bild, bior, bist, bixor, bld, bnot, bor, bset, bst, btst, bxor
    val2, = struct.unpack('>H', buf[off+2: off+4])

    iflags = 0
    op = (val >> 16) | (val&0xf) | (val2>>15) | (val&0xf)
    i3 = (val2 >> 4) & 0x7
    aa = val & 0xff

    opers = (
            H8ImmOper(i3),
            H8AbsAddrOper(aa),
            )
    return (op, None, opers, iflags, 4)

def p_i8_CCR(va, val, buf, off, tsize): 
    # andc
    iflags = 0
    op = val >> 8
    i8 = val & 0xff

    opers = (
            H8ImmOper(i8),
            )
    return (op, None, opers, iflags, 2)

def p_i8_Rd(va, val, buf, off, tsize): 
    # add.b, addx, and.b, cmp.b
    iflags = 0
    op = val >> 4
    i8 = val & 0xff
    Rd = (val >> 8) & 0xf

    opers = (
            H8ImmOper(i8),
            H8RegDirOper(Rd, va, 0),
            )
    return (op, None, opers, iflags, 2)

def p_i16_Rd(va, val, buf, off, tsize): 
    # add.w, and.w, cmp.w
    val2, = struct.unpack('>H', buf[off+2: off+4])

    iflags = 0
    op = val >> 4
    i16 = val2
    Rd = val & 0xf

    opers = (
            H8ImmOper(i16),
            H8RegDirOper(Rd, va, 0),
            )
    return (op, None, opers, iflags, 4)

def p_i32_ERd(va, val, buf, off, tsize): 
    # add.l, and.l, cmp.l
    val2, = struct.unpack('>I', buf[off+2: off+6])

    iflags = 0
    op = val >> 3
    i32 = val2
    ERd = val & 0x7

    opers = (
            H8ImmOper(i32),
            H8RegIndirOper(ERd, va, tsize, 0),
            )
    return (op, None, opers, iflags, 6)

def p_Rd(va, val, buf, off, tsize): 
    # daa, das, dec.b, exts.w, extu.w, inc.b
    iflags = 0
    op = val >> 4
    Rd = val & 0xf

    opers = (
            H8RegDirOper(Rd, va, 0),
            )
    return (op, None, opers, iflags, 2)

def p_Rs_Rd(va, val, buf, off, tsize):  
    # add.b, add.w, addx, and.b, and.w, cmp.b, cmp.w, divxu.b
    iflags = 0
    op = val >> 16
    Rs = (val >> 4) & 0xf
    Rd = val & 0xf

    opers = (
            H8RegDirOper(Rs, va, 0),
            H8RegDirOper(Rd, va, 0),
            )
    return (op, None, opers, iflags, 2)

def p_Rs_Rd_4b(va, val, buf, off, tsize):  
    # divxs.b
    val2, = struct.unpack('>H', buf[off+2: off+4])
    iflags = 0
    op = (val << 8) | (val2 >> 8)
    Rs = (val2 >> 4) & 0xf
    Rd = val2 & 0xf

    opers = (
            H8RegDirOper(Rs, va, 0),
            H8RegDirOper(Rd, va, 0),
            )
    return (op, None, opers, iflags, 4)

def p_Rs_ERd(va, val, buf, off, tsize):  
    # mulxu.w, divxu.w
    iflags = 0
    op = ((val >> 8) << 1) | ((val >> 3) & 1)
    Rs = (val >> 4) & 0xf
    ERd = val & 0x7

    # FIXME: make sure ER# and R# have correct metaregister values
    opers = (
            H8RegDirOper(Rs, va, 0),
            H8RegDirOper(ERd, va, 0),
            )
    return (op, None, opers, iflags, 2)


def p_ERs_ERd(va, val, buf, off, tsize):  
    # add.l, cmp.l
    iflags = 0
    op = ((val >> 7)&0xfffe) | (val&1)
    ERs = (val >> 4) & 0x7
    ERd = val & 0x7

    opers = (
            H8RegDirOper(Rs, va, 0),
            H8RegDirOper(ERd, va, 0),
            )
    return (op, None, opers, iflags, 2)

def p_Rs_ERd_4b(va, val, buf, off, tsize):  
    # divxs.w
    val2, = struct.unpack('>H', buf[off+2: off+4])
    iflags = 0
    op = (val << 8) | (val2 >> 8)
    Rs = (val2 >> 4) & 0xf
    ERd = val2 & 0x7

    opers = (
            H8RegDirOper(Rs, va, 0),
            H8RegDirOper(ERd, va, 0),
            )
    return (op, None, opers, iflags, 4)


def p_ERd(va, val, buf, off, tsize):  
    # exts.l, extu.l
    iflags = 0
    op = val >> 4
    ERd = val & 0x7

    opers = (
            H8RegDirOper(ERd, va, 0),
            )
    return (op, None, opers, iflags, 2)

def p_ERs_ERd_4b(va, val, buf, off, tsize):  
    # and.l, or.l
    val2, = struct.unpack('>H', buf[off+2: off+4])

    iflags = 0
    op = (val << 2) | ((val2 >> 6)&2) | ((val2 >> 3)&1)
    ERs = (val2 >> 4) & 0x7
    ERd = val2 & 0x7

    opers = (
            H8RegDirOper(ERs, va, 0),
            H8RegDirOper(ERd, va, 0),

    return (op, None, opers, iflags, 4)

def p_Rn_Rd(va, val, buf, off, tsize):  
    # bclr, bset, btst
    iflags = 0
    op = val >> 8
    Rn = (val >> 4) & 0xf
    Rd = val & 0xf

    opers = (
            H8RegDirOper(Rn, va, 0),
            H8RegDirOper(Rd, va, 0),
            )
    return (op, None, opers, iflags, 2)

def p_Rn_aERd(va, val, buf, off, tsize):  
    # bclr, bset, btst
    val2, = struct.unpack('>H', buf[off+2: off+4])

    iflags = 0
    op = ((val >> 12)&0xfff0) | (val&0xf) | ((val2>>4)&0xfff0) | (val2&0xf)
    aERd = (val >> 4) & 0x7
    Rn = (val >> 4) & 0xf

    opers = (
            H8RegDirOper(Rn, va, 0),
            H8RegIndirOper(aERd, va, tsize, disp=0, oflags=0),
            )
    return (op, None, opers, iflags, 4)

def p_Rn_aAA8(va, val, buf, off, tsize):  
    # bclr, bset, btst
    val2, = struct.unpack('>H', buf[off+2: off+4])

    iflags = 0
    op = (val & 0xff00) | ((val2 >> 4)&0xff0) | (val2&0xf)
    Rn = (val2 >> 4) & 0xf
    aAA8 = val & 0xff

    opers = (
            H8RegDirOper(Rn, va, 0),
            H8AbsAddrOper(aAA8),
            )
    return (op, None, opers, iflags, 4)

def p_aERn(va, val, buf, off, tsize):  
    # jmp, jsr
    iflags = 0
    op = ((val >> 3)&0xfff0) | (val&0xf)
    aERn = (val >> 4) & 0x7

    opers = (
            H8RegIndirOper(aERn, va, 0),
            )
    return (op, None, opers, iflags, 2)

def p_aAA24(va, val, buf, off, tsize):  
    # jmp, jsr
    val2, = struct.unpack('>H', buf[off+2: off+4])

    iflags = 0
    op = val >> 8
    aAA24 = ((val&0xf) << 16) | val2

    opers = (
            H8AbsAddrOper(aAA24),
            )
    return (op, None, opers, iflags, 2)

def p_aaAA8(va, val, buf, off, tsize):  
    # jmp, jsr
    iflags = 0
    op = val >> 8
    aaAA8 = val & 0xff

    opers = (
            H8MemIndirOper(aaAA8),
            )
    return (op, None, opers, iflags, 2)

def p_1_Rd(va, val, buf, off, tsize):  
    # dec.w, inc.w
    iflags = 0
    op = val >> 4
    Rd = val & 0xf

    opers = (
            H8ImmOper(1)
            H8RegDirOper(Rd, va, 0),
            )
    return (op, None, opers, iflags, 2)

def p_2_Rd(va, val, buf, off, tsize):  
    # dec.w, inc.w
    iflags = 0
    op = val >> 4
    Rd = val & 0xf

    opers = (
            H8ImmOper(2)
            H8RegDirOper(Rd, va, 0),
            )
    return (op, None, opers, iflags, 2)

def p_4_Rd(va, val, buf, off, tsize):  
    # dec.w
    iflags = 0
    op = val >> 4
    Rd = val & 0xf

    opers = (
            H8ImmOper(4)
            H8RegDirOper(Rd, va, 0),
            )
    return (op, None, opers, iflags, 2)

def p_1_ERd(va, val, buf, off, tsize):  
    # adds, dec.l, inc.l
    iflags = 0
    op = val >> 3
    ERd = val & 0x7

    opers = (
            H8ImmOper(1),
            H8RegDirOper(ERd, va, 0),
            )
    return (op, None, opers, iflags, 2)

def p_2_ERd(va, val, buf, off, tsize):  
    # adds, dec.l, inc.l
    iflags = 0
    op = val >> 3
    ERd = val & 0x7

    opers = (
            H8ImmOper(1),
            H8RegDirOper(ERd, va, 0),
            )
    return (op, None, opers, iflags, 2)

def p_4_ERd(va, val, buf, off, tsize):  
    # adds, dec.l
    iflags = 0
    op = val >> 3
    ERd = val & 0x7

    opers = (
            H8ImmOper(1),
            H8RegDirOper(ERd, va, 0),
            )
    return (op, None, opers, iflags, 2)

def p_disp8(va, val, buf, off, tsize):  
    # bcc, bsr
    iflags = 0
    op = val >> 8
    disp8 = val & 0xff

    opers = (
            H8PcOffsetOper(disp8, va),
            )
    return (op, None, opers, iflags, 2)

def p_disp16(va, val, buf, off, tsize):  
    # bcc, bsr
    val2, = struct.unpack('>H', buf[off+2: off+4])

    iflags = 0
    op = val
    disp16 = val2

    opers = (
            H8PcOffsetOper(disp16, va),
            )
    return (op, None, opers, iflags, 4)

_
def p_Rs_aAA16(va, val, buf, off, tsize):
    val2, = struct.unpack('>H', buf[off+2: off+4])

    iflags = 0
    op = val >> 4
    Rs = val & 0xf
    aAA16 = val2

    opers = (
            H8RegDirOper(Rs),
            H8AbsAddrOper(aAA16),
            )
    return (op, None, opers, iflags, 4)

def p_Rs_aAA24(va, val, buf, off, tsize):
    val2, = struct.unpack('>I', buf[off+2: off+6])

    iflags = 0
    op = val >> 4
    Rs = val & 0xf
    aAA24 = val2 & 0xffffff

    opers = (
            H8RegDirOper(Rs),
            H8AbsAddrOper(aAA24),
            )
    return (op, None, opers, iflags, 6)

def p_aAA16_Rd(va, val, buf, off, tsize):  
    val2, = struct.unpack('>H', buf[off+2: off+4])

    iflags = 0
    op = val >> 4
    Rd = val & 0xf
    aAA16 = val2

    opers = (
            H8AbsAddrOper(aAA16),
            H8RegDirOper(Rd),
            )
    return (op, None, opers, iflags, 4)

def p_aAA24_Rd(va, val, buf, off, tsize):  
    val2, = struct.unpack('>I', buf[off+2: off+6])

    iflags = 0
    op = val >> 4
    Rd = val & 0xf
    aAA16 = val2 & 0xffffff

    opers = (
            H8AbsAddrOper(aAA16),
            H8RegDirOper(Rd),
            )
    return (op, None, opers, iflags, 6)

def p_nooperands(va, val, buf, off, tsize):  
    # eepmov.b, eepmov.w, 
    iflags = 0
    op = val

    opers = ()
    return (op, None, opers, iflags, 2)


bit_dbles = [
        ('error', 0),
        ('error', 0),
        ('error', 0),
        ('error', 0),
        ('error', 0),
        ('error', 0),
        ('bst', 0),
        ('bist', 0),
        ('bor', 0),
        ('bior', 0),
        ('bxor', 0),
        ('bixor', 0),
        ('band', 0),
        ('biand', 0),
        ('bld', 0),
        ('bild', 0),
        ]

def getBitDbl_OpMnem(val):
    op = val >> 6
    mnem = bit_dbles[(op & 0xf)]
    return op, mnem

def p_Bit_Doubles(va, val, buf, off, tsize):
    iflags = 0
    op, mnem = getBitDbl_OpMnem(val)
    
    i3 = (val>>4) & 0x7
    Rd = val & 0xf

    opers = (
            H8ImmOper(i3),
            H8RegDirOper(Rd, va, 0),
            )
    return (op, mnem, opers, iflags, 2)

def p_Mov_6A(va, val, buf, off, tsize):
    op = val >> 4
    if op & 0x8:
        # Rs, @aa:16/24
        if op & 0x2:
            return p_Rs_aAA24(va, val, buf, off, tsize)
        return p_Rs_aAA16(va, val, buf, off, tsize)

    else:
        # @aa:16/24, Rd
            return p_aAA24_Rd(va, val, buf, off, tsize)
        return p_aAA16_Rd(va, val, buf, off, tsize)

def p_Mov_6C(va, val, buf, off, tsize):
    op = val >> 7
    if op & 0x1:
        # @ERs+, Rd
        return p_Rs_aAA16(va, val, buf, off, tsize)

    else:
        # @aa:16/24, Rd
        return p_aAA16_Rd(va, val, buf, off, tsize)

def p_Mov_78(va, val, buf, off, tsize):
    val2, val3_4 = struct.unpack(">HI", buf[off+2:off+8])

    op = (val3_4 >> 24) | ((val2&0xfff0)<<4) | ((val&0xff80)<<(20+1)) | ((val&0xf)<<20)
    #FIXME: complex and ugly.  do we even need these in this impl?

    mnem = None
    disp = val3_4 & 0xffffff

    if (val2 & 8):
        ers = (val>>4) & 0x7
        rd  = val2 & 0xf
        opers = (
                H8RegIndirOper(ers, va, tsize=tsize, disp=disp, oflags=0),
                H8RegOper(rd),
                )
    else:
        erd = (val>>4) & 0x7
        rs  = val2 & 0xf
        opers = (
                H8RegOper(rs),
                H8RegIndirOper(erd, va, tsize=tsize, disp=disp, oflags=0),
                )

    return (op, mnem, opers, iflags, 2)

mnem_79a = (
        'mov',
        'add',
        'cmp',
        'sub',
        'or',
        'xor',
        'and',
        )

def p_79(va, val, buf, off, tsize):
    op, m, opers, iflags, osz = p_i16_Rd(va, val, buf, off, tsize)
    mnem = mnem_79a[(val>>4)&0xf]
    return op, mnem, opers, iflags, osz

def p_7a(va, val, buf, off, tsize):
    op, m, opers, iflags, osz = p_i32_ERd(va, val, buf, off, tsize)
    mnem = mnem_79a[(val>>4)&0xf]
    return op, mnem, opers, iflags, osz

def p_eepmov(va, val, buf, off, tsize):
    val2, = struct.unpack('>H', buf[off+2: off+4])
    op = (val<<8) | val2
    tsize = (1,2)[ (val>>7)&1]
    return op, None, (), 0, 4)

def p_7c(va, val, buf, off, tsize):
    # btst, bor, bior, bxor, bixor, band, biand, bid, bild (erd)
    val2, = struct.unpack('>H', buf[off+2: off+4])
    iflags = 0
    op, mnem = getBitDbl_OpMnem(val2)
    op |= ((val & 0xff80)<<9)

    telltale = (val2>>8) 
    
    # FIXME: is any of this redundant with previous encodings?
    if telltale == 0x63:
        # btst (0x####63##
        mnem = 'btst'
        erd = (val>>4) & 0x7
        rn = (val2>>4) & 0xf
        opers = (
                H8RegIndirOper(rn, tsize=tsize)
                H8RegIndirOper(erd, tsize=tsize)
                }

    elif telltale == 0x73:
        # btst (0x####73##
        mnem = 'btst'
        erd = (val>>4) & 0x7
        imm = (val2>>4) & 0x7
        opers = (
                H8ImmOper(imm),
                H8RegIndirOper(erd, tsize=tsize)
                }

    elif 0x78 > telltale > 0x73:
        # other bit-halves:
        i3 = (val2>>4) & 0x7
        erd = val2 & 0xf

        opers = (
                H8ImmOper(i3),
                H8RegDirOper(erd, va, 0),
                )
    
    return op, mnem, opers, iflags, 4

bit_dble7d = [
        ('bset', 0),
        ('bset', 0),
        ('bnot', 0),
        ('bnot', 0),
        ('bclr', 0),
        ('bclr', 0),
        None, 
        None, 
        None, 
        None,
        None, 
        None, 
        None, 
        None,
        ('bst', 0),
        ('bist', 0),
        ]

def p_7d(va, val, buf, off, tsize):
    # bset, bnor, bclr
    val2, = struct.unpack('>H', buf[off+2: off+4])
    iflags = 0
    op, mnem = getBitDbl_OpMnem(val2)
    op |= ((val & 0xff80)<<9)

    telltale = (val2>>8) 
    
    # FIXME: is any of this redundant with previous encodings?
    if telltale == 0x63:
        # btst (0x####63##
        mnem = 'btst'
        erd = (val>>4) & 0x7
        rn = (val2>>4) & 0xf
        opers = (
                H8RegIndirOper(rn, tsize=tsize)
                H8RegIndirOper(erd, tsize=tsize)
                }

    elif telltale == 0x73:
        # btst (0x####73##
        mnem = 'btst'
        erd = (val>>4) & 0x7
        imm = (val2>>4) & 0x7
        opers = (
                H8ImmOper(imm),
                H8RegIndirOper(erd, tsize=tsize)
                }

    elif 0x78 > telltale > 0x73:
        # other bit-halves:
        i3 = (val2>>4) & 0x7
        erd = val2 & 0xf

        opers = (
                H8ImmOper(i3),
                H8RegDirOper(erd, va, 0),
                )
    
    return op, mnem, opers, iflags, osz

class H8Disasm:
    fmt = None
    def __init__(self):
        pass

    def disasm(self, bytez, offset, va):
        ''' unfixed '''
        """
        Parse a sequence of bytes out into an envi.Opcode instance.
        """
        opbytes = bytez[offset:offset+2]
        opval, = struct.unpack(">H", opbytes)
        
        
        # If we don't know the encoding by here, we never will ;)
        if enc == None:
            raise envi.InvalidInstruction(mesg="No encoding found!",
                    bytez=bytez[offset:offset+4], va=va)

        opcode, mnem, olist, flags = ienc_parsers[enc](opval, va)

        ############# this is all in need of redoing....
        # Ok...  if we're a non-conditional branch, *or* we manipulate PC unconditionally,
        # lets call ourself envi.IF_NOFALL
        if cond == COND_AL:                             # FIXME: this could backfire if COND_EXTENDED...
            if opcode in (INS_B, INS_BX):
                flags |= envi.IF_NOFALL

            elif (  len(olist) and 
                    isinstance(olist[0], H8RegOper) and
                    olist[0].involvesPC() and 
                    (opcode & 0xffff) not in no_update_Rd ):       # FIXME: only want IF_NOFALL if it *writes* to PC!
                
                showop = True
                flags |= envi.IF_NOFALL

        else:
            flags |= envi.IF_COND

        #####################################################


        # FIXME conditionals are currently plumbed as "prefixes".  Perhaps normalize to that...
        op = H8Opcode(va, opcode, mnem, cond, 4, olist, flags)
        op.encoder = enc    #FIXME: DEBUG CODE

        return op

if __name__ == '__main__':
    import envi.archs
    envi.archs.dismain( H8Disasm() )
