import sys
import copy
import struct

import envi
import envi.bits as e_bits
import envi.memory as e_mem

from envi.archs.msp430.regs import *

########################################################
# Process special opcodes that come from double opcodes
#
# These could use the dpbase parse from arm.py
#

def dpbase(workData):
    """
    Parse and return dcode_val, dsreg, ds_addr_mode, 
    destreg, dest_addr_mode, op_bw, dsopsize, destopsize
    for a standard data processing instruction.
    """
    dcode_val = ((workData & DOUBLE_OPCODE) >> 12) - 4
    dsreg = (workData & DSOURCE_REG) >> 8
    ds_addr_mode = (workData & SOURCE_ADDR_MODE) >> 4
    destreg = workData & DEST_REG
    dest_addr_mode = (workData & DEST_ADDR_MODE) >> 7
    op_bw = (workData & BYTE_WORD) << 2     # IF_BYTE
    if op_bw:
        dsopsize = 1
        destopsize = 1
    else:
        dsopsize = 2
        destopsize = 2

    # FIXME: wtf is this logic?  where should op_bw play here?
    #if (ds_addr_mode == REG_INDEX) or (ds_addr_mode == REG_IND_AUTOINC):
    #    dsopsize = 1
    #if (dest_addr_mode == REG_INDEX):
    #    destopsize = 1
    return dcode_val, dsreg, ds_addr_mode, destreg, dest_addr_mode, op_bw, dsopsize, destopsize

def decode0(workData, opData, va):
    # Parse out because of special operations
    # MOV
    dcode_val, dsreg, ds_addr_mode, destreg, dest_addr_mode, op_bw, dsopsize, destopsize = dpbase(workData)

    # NOP
    if ((dsreg > 3) and (dsreg == destreg)) and not ds_addr_mode and not dest_addr_mode:
        mnem, flags = dspcode[0]
        return Msp430Opcode( va, SP_OPCODE_TYPE, mnem, [], 0, opData.lenData())
    # RET
    # moved before POP to process properly
    if ((dsreg == 1) and (ds_addr_mode == REG_IND_AUTOINC) and (destreg == 0)):
        mnem, flags = dspcode[3]
        return Msp430Opcode( va, SP_OPCODE_TYPE, mnem, [ ], IF_NOFALL, opData.lenData())
    # POP
    if ((dsreg == 1) and (ds_addr_mode == REG_IND_AUTOINC)):
        mnem, flags = dspcode[1]
        return Msp430Opcode( va, SINGLE_OPCODE_TYPE, mnem, [ Msp430Operands[dest_addr_mode](destreg, opData, destopsize, va) ], op_bw, opData.lenData())
    # BRANCH
    if (destreg == 0) and not dest_addr_mode:
        mnem, flags = dspcode[2]
        op = Msp430Opcode( va, SINGLE_OPCODE_TYPE, mnem, [ Msp430Operands[ds_addr_mode](dsreg, opData, dsopsize, va) ], IF_BRANCH|IF_NOFALL, opData.lenData())
        return op
    '''
    # CLR
    if ((dsreg == 3) and (ds_addr_mode == REG_DIRECT)):
    mnem, flags = dspcode[4]
        return Msp430Opcode( va, SINGLE_OPCODE_TYPE, mnem, [ Msp430Operands[dest_addr_mode](destreg, opData, destopsize) ], op_bw)
    '''
    # Nothing Special
    return Msp430Opcode(
            va,
            DOUBLE_OPCODE_TYPE,
            dcode[dcode_val],
            [ Msp430Operands[ds_addr_mode](dsreg, opData, dsopsize, va), Msp430Operands[dest_addr_mode](destreg, opData, destopsize, va) ],
            op_bw, 
            opData.lenData()
            )

def decode1(workData, opData, va):
    # Parse out because of special operations
    # ADD
    dcode_val, dsreg, ds_addr_mode, destreg, dest_addr_mode, op_bw, dsopsize, destopsize = dpbase(workData)
    
    # RLA
    if (dsreg == destreg) and not ds_addr_mode and not dest_addr_mode:
        mnem, flags = dspcode[5]
        return Msp430Opcode( va, SINGLE_OPCODE_TYPE, mnem, [ Msp430Operands[dest_addr_mode](destreg, opData, destopsize, va) ], op_bw, opData.lenData())
    # INC
    if ((dsreg == 3) and (ds_addr_mode == REG_INDEX)):
        mnem, flags = dspcode[6]
        return Msp430Opcode( va, SINGLE_OPCODE_TYPE, mnem, [ Msp430Operands[dest_addr_mode](destreg, opData, destopsize, va) ], op_bw, opData.lenData())
    # INCD
    if ((dsreg == 3) and (ds_addr_mode == REG_INDIRECT)):
        mnem, flags = dspcode[7]
        return Msp430Opcode( va, SINGLE_OPCODE_TYPE, mnem, [ Msp430Operands[dest_addr_mode](destreg, opData, destopsize, va) ], op_bw, opData.lenData())
    # Nothing Special
    return Msp430Opcode(
            va,
            DOUBLE_OPCODE_TYPE,
            dcode[dcode_val],
            [ Msp430Operands[ds_addr_mode](dsreg, opData, dsopsize, va), Msp430Operands[dest_addr_mode](destreg, opData, destopsize, va) ],
            op_bw,
            opData.lenData())

def decode2(workData, opData, va):
    # Parse out because of special operations
    # ADDC
    dcode_val, dsreg, ds_addr_mode, destreg, dest_addr_mode, op_bw, dsopsize, destopsize = dpbase(workData)
    
    # RLC
    if (dsreg == destreg) and not ds_addr_mode and not dest_addr_mode:
        mnem, flags = dspcode[8]
        return Msp430Opcode( va, SINGLE_OPCODE_TYPE, mnem, [ Msp430Operands[dest_addr_mode](destreg, opData, destopsize, va) ], op_bw, opData.lenData())
    # ADC
    if ((dsreg == 3) and (ds_addr_mode == REG_DIRECT)):
        mnem, flags = dspcode[9]
        return Msp430Opcode( va, SINGLE_OPCODE_TYPE, mnem, [ Msp430Operands[dest_addr_mode](destreg, opData, destopsize, va) ], op_bw, opData.lenData())
    # Nothing Special
    return Msp430Opcode(
            va,
            DOUBLE_OPCODE_TYPE,
            dcode[dcode_val],
            [ Msp430Operands[ds_addr_mode](dsreg, opData, dsopsize, va), Msp430Operands[dest_addr_mode](destreg, opData, destopsize, va) ],
            op_bw,
            opData.lenData())

def decode3(workData, opData, va):
    # Parse out because of special operations
    # SUBC
    dcode_val, dsreg, ds_addr_mode, destreg, dest_addr_mode, op_bw, dsopsize, destopsize = dpbase(workData)
    
    # SBC
    if ((dsreg == 3) and (ds_addr_mode == REG_DIRECT)):
        mnem, flags = dspcode[10]
        return Msp430Opcode( va, SINGLE_OPCODE_TYPE, mnem, [ Msp430Operands[dest_addr_mode](destreg, opData, destopsize, va) ], op_bw, opData.lenData())
    # Nothing Special
    return Msp430Opcode(
            va,
            DOUBLE_OPCODE_TYPE,
            dcode[dcode_val],
            [ Msp430Operands[ds_addr_mode](dsreg, opData, dsopsize, va), Msp430Operands[dest_addr_mode](destreg, opData, destopsize, va) ],
            op_bw,
            opData.lenData())

def decode4(workData, opData, va):
    # Parse out because of special operations
    # SUB
    dcode_val, dsreg, ds_addr_mode, destreg, dest_addr_mode, op_bw, dsopsize, destopsize = dpbase(workData)
    
    # DEC
    if ((dsreg == 3) and (ds_addr_mode == REG_INDEX)):
        mnem, flags = dspcode[11]
        return Msp430Opcode( va, SINGLE_OPCODE_TYPE, mnem, [ Msp430Operands[dest_addr_mode](destreg, opData, destopsize, va) ], op_bw, opData.lenData())
    # DECD
    if ((dsreg == 3) and (ds_addr_mode == REG_INDIRECT)):
        mnem, flags = dspcode[12]
        return Msp430Opcode( va, SINGLE_OPCODE_TYPE, mnem, [ Msp430Operands[dest_addr_mode](destreg, opData, destopsize, va) ], op_bw, opData.lenData())
    # Nothing Special
    return Msp430Opcode(
            va,
            DOUBLE_OPCODE_TYPE,
            dcode[dcode_val],
            [ Msp430Operands[ds_addr_mode](dsreg, opData, dsopsize, va), Msp430Operands[dest_addr_mode](destreg, opData, destopsize, va) ],
            op_bw,
            opData.lenData())

def decode5(workData, opData, va):
    # Parse out because of special operations
    # CMP
    dcode_val, dsreg, ds_addr_mode, destreg, dest_addr_mode, op_bw, dsopsize, destopsize = dpbase(workData)
    
    # TST
    if ((dsreg == 3) and (ds_addr_mode == REG_DIRECT)):
        mnem, flags = dspcode[13]
        return Msp430Opcode( va, SINGLE_OPCODE_TYPE, mnem, [ Msp430Operands[dest_addr_mode](destreg, opData, destopsize, va) ], op_bw, opData.lenData())
    # Nothing Special
    return Msp430Opcode(
            va,
            DOUBLE_OPCODE_TYPE,
            dcode[dcode_val],
            [ Msp430Operands[ds_addr_mode](dsreg, opData, dsopsize, va), Msp430Operands[dest_addr_mode](destreg, opData, destopsize, va) ],
            op_bw,
            opData.lenData())

def decode6(workData, opData, va):
    # Parse out because of special operations
    # DADD
    dcode_val, dsreg, ds_addr_mode, destreg, dest_addr_mode, op_bw, dsopsize, destopsize = dpbase(workData)
    
    # DADC
    if ((dsreg == 3) and (ds_addr_mode == REG_DIRECT)):
        mnem, flags = dspcode[14]
        return Msp430Opcode( va, SINGLE_OPCODE_TYPE, mnem, [ Msp430Operands[dest_addr_mode](destreg, opData, destopsize, va) ], op_bw, opData.lenData())
    # Nothing Special
    return Msp430Opcode(
            va,
            DOUBLE_OPCODE_TYPE,
            dcode[dcode_val],
            [ Msp430Operands[ds_addr_mode](dsreg, opData, dsopsize, va), Msp430Operands[dest_addr_mode](destreg, opData, destopsize, va) ],
            op_bw,
            opData.lenData())

def decode7(workData, opData, va):
    # Parse out because of special operations
    # Nothing Special, move along now
    dcode_val, dsreg, ds_addr_mode, destreg, dest_addr_mode, op_bw, dsopsize, destopsize = dpbase(workData)
    return Msp430Opcode(
            va,
            DOUBLE_OPCODE_TYPE,
            dcode[dcode_val],
            [ Msp430Operands[ds_addr_mode](dsreg, opData, dsopsize, va), Msp430Operands[dest_addr_mode](destreg, opData, destopsize, va) ],
            op_bw,
            opData.lenData())

def decode8(workData, opData, va):
    # Parse out because of special operations
    # BIC
    dcode_val, dsreg, ds_addr_mode, destreg, dest_addr_mode, op_bw, dsopsize, destopsize = dpbase(workData)
    
    # CLRC
    if ((destreg == 2) and (dsreg == 3) and (ds_addr_mode == REG_INDEX)):
        mnem, flags = dspcode[15]
        return Msp430Opcode( va, SP_OPCODE_TYPE, mnem, [ ], 0, opData.lenData())
    # CLRZ
    if ((destreg == 2) and (dsreg == 3) and (ds_addr_mode == REG_INDIRECT)):
        mnem, flags = dspcode[17]
        return Msp430Opcode( va, SP_OPCODE_TYPE, mnem, [ ], 0, opData.lenData())
    # CLRN
    if ((destreg == 2) and (dsreg == 2) and (ds_addr_mode == REG_INDIRECT)):
        mnem, flags = dspcode[19]
        return Msp430Opcode( va, SP_OPCODE_TYPE, mnem, [ ], 0, opData.lenData())
    # DINT
    if ((destreg == 2) and (dsreg == 2) and (ds_addr_mode == REG_IND_AUTOINC)):
        mnem, flags = dspcode[21]
        return Msp430Opcode( va, SP_OPCODE_TYPE, mnem, [ ], 0, opData.lenData())
    # Nothing Special
    return Msp430Opcode(
            va,
            DOUBLE_OPCODE_TYPE,
            dcode[dcode_val],
            [ Msp430Operands[ds_addr_mode](dsreg, opData, dsopsize, va), Msp430Operands[dest_addr_mode](destreg, opData, destopsize, va) ],
            op_bw,
            opData.lenData()
            )

def decode9(workData, opData, va):
    # Parse out because of special operations
    # BIS
    dcode_val, dsreg, ds_addr_mode, destreg, dest_addr_mode, op_bw, dsopsize, destopsize = dpbase(workData)
    
    # SETC
    if ((destreg == 2) and (dsreg == 3) and (ds_addr_mode == REG_INDEX)):
        mnem, flags = dspcode[16]
        return Msp430Opcode( va, SP_OPCODE_TYPE, mnem, [ ], 0, opData.lenData())
    # SETZ
    if ((destreg == 2) and (dsreg == 3) and (ds_addr_mode == REG_INDIRECT)):
        mnem, flags = dspcode[18]
        return Msp430Opcode( va, SP_OPCODE_TYPE, mnem, [ ], 0, opData.lenData())
    # SETN
    if ((destreg == 2) and (dsreg == 2) and (ds_addr_mode == REG_INDIRECT)):
        mnem, flags = dspcode[20]
        return Msp430Opcode( va, SP_OPCODE_TYPE, mnem, [ ], 0, opData.lenData())
    # DINT
    if ((destreg == 2) and (dsreg == 2) and (ds_addr_mode == REG_IND_AUTOINC)):
        mnem, flags = dspcode[22]
        return Msp430Opcode( va, SP_OPCODE_TYPE, mnem, [ ], 0, opData.lenData())
    # Nothing Special
    return Msp430Opcode(
            va, 
            DOUBLE_OPCODE_TYPE,
            dcode[dcode_val],
            [ Msp430Operands[ds_addr_mode](dsreg, opData, dsopsize, va), Msp430Operands[dest_addr_mode](destreg, opData, destopsize, va) ],
            op_bw,
            opData.lenData()
            )

def decode10(workData, opData, va):
    # Parse out because of special operations
    # XOR
    dcode_val, dsreg, ds_addr_mode, destreg, dest_addr_mode, op_bw, dsopsize, destopsize = dpbase(workData)
    
    # INV
    if ((dsreg == 3) and (ds_addr_mode == REG_IND_AUTOINC)):
        mnem, flags = dspcode[23]
        return Msp430Opcode( va, SINGLE_OPCODE_TYPE, mnem, [ Msp430Operands[dest_addr_mode](destreg, opData, destopsize, va) ], op_bw, opData.lenData())
    # Nothing Special
    return Msp430Opcode(
            va, 
            DOUBLE_OPCODE_TYPE,
            dcode[dcode_val],
            [ Msp430Operands[ds_addr_mode](dsreg, opData, dsopsize, va), Msp430Operands[dest_addr_mode](destreg, opData, destopsize, va) ],
            op_bw,
            opData.lenData()
            )

def decode11(workData, opData, va):
    # Parse out because of special operations
    # Nothing Special, move along now
    dcode_val, dsreg, ds_addr_mode, destreg, dest_addr_mode, op_bw, dsopsize, destopsize = dpbase(workData)
    
    return Msp430Opcode(
            va, 
            DOUBLE_OPCODE_TYPE,
            dcode[dcode_val],
            [ Msp430Operands[ds_addr_mode](dsreg, opData, dsopsize, va), Msp430Operands[dest_addr_mode](destreg, opData, destopsize, va) ],
            op_bw,
            opData.lenData()
            )

######################################################
# Table of the parser functions for special opcodes

decode_function = (
    decode0,
    decode1,
    decode2,
    decode3,
    decode4,
    decode5,
    decode6,
    decode7,
    decode8,
    decode9,
    decode10,
    decode11
)

class Msp430Opcode(envi.Opcode):

    def __init__(self, va, opcode, mnem, opers, iflags=0, size=0):
        self.va = va
        self.opcode = opcode
        self.mnem = mnem
        self.opers = opers
        self.iflags = iflags | envi.ARCH_MSP430
        self.size = size

    def __len__(self):
        return self.size

    def isByte(self):
        return self.iflags

    def render(self, mcanv):
        """
        Render this opcode to the specified memory canvas
        """
        mnem = self.mnem
        if self.iflags & IF_BYTE:
            mnem += '.b'

        mcanv.addNameText(mnem, typename="mnemonic")
        mcanv.addText(" ")

        # Allow each of our operands to render
        imax = len(self.opers)
        lasti = imax - 1
        for i in range(imax):
            oper = self.opers[i]
            oper.render(mcanv, self, i)
            if i != lasti:
                mcanv.addText(", ")

    def __repr__(self):
        if self.iflags & IF_BYTE:
            # Let everybody know that we only need a byte instead of a word
            mnem = self.mnem + '.b'
        else:
            mnem = self.mnem

        x = [mnem]
        # Test for Special Opcode Type and 'reti'
        if  self.opcode == SP_OPCODE_TYPE: 
            return " ".join(x)
        if self.opcode == DOUBLE_OPCODE_TYPE:
            x.append(repr(self.opers[0]) + ",")
            x.append(repr(self.opers[1]))
        else:
            # Single opcode or jumps
            x.append(repr(self.opers[0]))
        return " ".join(x)

    def getBranches(self, emu=None):
        ret = []

        # To start with we have no flags ( except our arch )
        flags = self.iflags & envi.ARCH_MASK
        addb = False

        # If we are a conditional branch, even our fallthrough
        # case is conditional...
        if (self.iflags & IF_BRANCH):
            addb = True
            if not (self.iflags & IF_NOFALL):
                flags |= envi.BR_COND

        # If we can fall through, reflect that...
        if not self.iflags & envi.IF_NOFALL:
            ret.append((self.va + self.size, flags|envi.BR_FALL))

        # if we have no operands, it has no further branches...
        if len(self.opers) == 0:
            return ret

        # Check for a call...
        if self.iflags & IF_CALL:
            flags |= envi.BR_PROC
            addb = True

        if addb:
            oper0 = self.opers[0]
            if oper0.isDeref():
                flags |= envi.BR_DEREF
                tova = oper0.getOperAddr(self, emu=emu)
            else:
                tova = oper0.getOperValue(self, emu=emu)

            ret.append((tova, flags))

        return ret

#FIXME: This should just be wrapped into envi
def addrToName(mcanv, va):
    sym = mcanv.syms.getSymByAddr(va)
    if sym is not None:
        return repr(sym)
    return "0x%.4x" % va

def renderPossibleLocation(mcanv, op, idx, value):
    hint = mcanv.syms.getSymHint(op.va, idx)
    if hint is not None:
        if mcanv.mem.isValidPointer(value):
            mcanv.addVaText(hint, value)
        else:
            mcanv.addNameText(hint)
    elif mcanv.mem.isValidPointer(value):
        name = addrToName(mcanv, value)
        mcanv.addVaText(name, value)
    else:
        value &= 0xffff
        mcanv.addNameText('0x%x' % value)

class Msp430Operand(envi.Operand):

    def __init__(self, val, inData, tsize=2, va=0):
        self.val = val
        self.tsize = tsize
        self.va = va

    def render(self, mcanv, op, idx):
        mcanv.addText(" " + self.__repr__())

    def renderReg(self, mcanv, op, idx, reg):
        hint = mcanv.syms.getSymHint(op.va, idx)
        if hint is not None:
            mcanv.addNameText(hint, typename="registers")
        else:
            name = self._dis_regctx.getRegisterName(reg)
            rname = self._dis_regctx.getRegisterName(reg&RMETA_NMASK)
            mcanv.addNameText(name, name=rname, typename="registers")

class Msp430RegDirectOper(Msp430Operand):
    def __repr__(self):
        # Register direct
        if self.val == REG_CG:
            # Special Case
            return "#0"
        else:
            # return Rn
            regname = registers[self.val]
            return "%s" % regname

    def render(self, mcanv, op, idx):
        if self.val == REG_CG:
            mcanv.addText("#0x0")
            return

        self.renderReg(mcanv, op, idx, self.val)


    def getOperValue(self, op, emu=None):
        if self.val == REG_PC:
            return op.va + op.size
        if self.val == REG_CG:
            return 0

        if emu==None: 
            return

        return emu.getRegister(self.val)

    def setOperValue(self, op, emu, val):
        if self.val == REG_CG:
            return 0

        return emu.setRegister(self.val, val)

class Msp430RegIndexOper(Msp430Operand):
    def __init__(self, val, inData, tsize=0, va=0):
        Msp430Operand.__init__(self, val, inData, tsize, va)
        if val != REG_CG:
            new_val = inData.nextData()

            # this is signed
            if new_val > 32768:
                new_val = ((new_val & 32767) - 32768)

            self.new_val = new_val

    def __repr__(self):
        # Register indexed
        if self.val == REG_SR:
            # Special Case
            return "&0x%0.4x" % self.new_val
        if self.val == REG_CG:
            # Special Case
            return "#1"
        new_val = self.new_val
        # If r0 then return hex value
        if not self.val:
            return "0x%0.4x" % new_val

        regname = registers[self.val]
        return "0x%x(%s)" % (new_val,regname)

    def render(self, mcanv, op, idx):
        if self.val == REG_SR:
            mcanv.addText('&')
            renderPossibleLocation(mcanv, op, idx, self.new_val)

        elif self.val == REG_CG:
            mcanv.addText('#0x1')

        elif self.val == REG_PC:
            mcanv.addText('#')
            renderPossibleLocation(mcanv, op, idx, self.new_val)

        else:
            if self.new_val < 0:
                preface = '-0x%x(' % abs(self.new_val)
            else:
                preface = '0x%x(' % self.new_val
            mcanv.addText(preface)
            self.renderReg(mcanv, op, idx, self.val)
            mcanv.addText(')')

    def setOperValue(self, op, emu, val):
        if self.val == REG_CG:
            return 1

        addr = self.getOperAddr(op, emu)
        emu.writeMemValue(addr, val, self.tsize)

    def getOperValue(self, op, emu=None):
        if self.val == REG_CG:
            return 1

        if emu==None:
            return None

        addr = self.getOperAddr(op, emu)
        val = emu.readMemValue(addr, self.tsize)
        return val


    def getOperAddr(self, op, emu=None):
        if self.val == REG_SR:
            return self.new_val
        if self.val == REG_PC:
            return op.va + op.size + self.new_val

        if emu==None:
            return None

        addr = emu.getRegister(self.val)
        return addr + self.new_val

    def isDeref(self):
        if self.val == REG_CG:
            return False
        return True

class Msp430RegIndirOper(Msp430Operand):
    def __repr__(self):
        # Register indirect
        if self.val == REG_SR:
            # Special Case
            return "#0x4"
        if self.val == REG_CG:
            # Special Case
            return "#0x2"
        regname = registers[self.val]
        return "@%s" % regname

    def render(self, mcanv, op, idx):
        # Register indirect
        if self.val == REG_SR:
            # Special Case
            mcanv.addText("#")
            mcanv.addNameText("0x4")
            return

        if self.val == REG_CG:
            # Special Case
            mcanv.addText("#")
            mcanv.addNameText("0x2")
            return

        mcanv.addText("@")
        self.renderReg(mcanv, op, idx, self.val)

    def setOperValue(self, op, emu, val):
        if self.val in (REG_SR, REG_CG):
            return

        addr = self.getOperAddr(op, emu)
        emu.writeMemValue(addr, val, self.tsize)

    def getOperValue(self, op, emu=None):
        if self.val in (REG_SR, REG_CG):
            return (None, None, 4, 2)[self.val]

        if emu is None:
            return None

        addr = self.getOperAddr(op, emu)
        val = emu.readMemValue(addr, self.tsize)
        return val

    def getOperAddr(self, op, emu=None):
        if self.val == REG_PC:
            return op.va + op.size

        if emu is None:
            return None

        return emu.getRegister(self.val)

    def isDeref(self):
        if self.val in (REG_SR, REG_CG):
            return False
        return True

class Msp430RegIndirAutoincOper(Msp430Operand):
    def __init__(self, val, inData, tsize, va=0):
        Msp430Operand.__init__(self, val, inData, tsize, va)
        if val == REG_PC:
            new_val = inData.nextData()
            if new_val > 32768:
                new_val = ((new_val & 32767) - 32768)

            self.new_val = new_val

    def __repr__(self):
        # Register indirect autoincrement
        if self.val == REG_PC:
            # Return @PC+x where x is the next word in the instruction stream
            return "#0x%x" % (self.new_val)

        if self.val == REG_SR:
            # Special Case
            return "#0x8"
        if self.val == REG_CG:
            # Special Case
            return "#-0x1"

        regname = registers[self.val]
        return "@%s+" % regname

    def render(self, mcanv, op, idx):
        # Register indirect autoincrement
        if self.val == REG_PC:
            # Return @PC+x where x is the next word in the instruction stream
            mcanv.addText("#")
            renderPossibleLocation(mcanv, op, idx, self.new_val)
            return

        if self.val == REG_SR:
            mcanv.addText("#")
            mcanv.addNameText("0x8")
            return

        if self.val == REG_CG:
            mcanv.addText("#")
            mcanv.addNameText("-0x1")
            return

        self.renderReg(mcanv, op, idx, self.val)

    def setOperValue(self, op, emu, val):
        if self.val in (REG_PC, REG_SR, REG_CG):
            return 

        addr = self.getOperAddr(op, emu)
        emu.readMemValue(addr, va, self.tsize)

    def getOperValue(self, op, emu=None):
        if self.val == REG_PC:
            return self.new_val
        elif self.val == REG_SR:
            return 8
        elif self.val == REG_CG:
            return -1

        if emu is None:
            return None
        addr = self.getOperAddr(op, emu)
        val = emu.readMemValue(addr, self.tsize)
        return val

    def getOperAddr(self, op, emu=None):
        if emu is None:
            return None

        addr = emu.getRegister(self.val)
        emu.setRegister(self.val, addr + self.tsize)
        return addr

    def isDeref(self):
        if self.val in (REG_PC, REG_SR, REG_CG):
            return False
        return True

class Msp430JmpOper(Msp430Operand):
    def __init__(self, val, inData, tsize, va=0):
        if (val > 0xff):
            jmp_val = va + (2 * ((val & 511) - 512)) + 2
        else:
            jmp_val = va + (2 * val) + 2

        Msp430Operand.__init__(self, jmp_val, inData, tsize, va)

    def __repr__(self):
            # Process and sign jump offsets
            # PC = PC + 2 * offset
            if self.va:
                return "#0x%x" % self.val
            return "$0x%x" % self.val

    def render(self, mcanv, op, idx):
        if self.va:
            mcanv.addText("#")
        else:
            mcanv.addText("$")

        renderPossibleLocation(mcanv, op, idx, self.val)

    def setOperValue(self, op, emu, val):
        return

    def getOperValue(self, op, emu=None):
        return self.val


class Msp430Disasm:
    def __init__(self):
        self._dis_regctx = Msp430RegisterContext()
        self._dis_oparch = envi.ARCH_MSP430

    # FIXME: Msp430Data is kinda kludgy and should be wrapped into the disasm logic
    class Msp430Data:
        """
            Msp430Data processes the incoming data.
            Optimally this will be 6 words coming in
            but, it could be more.
        """
        def __init__ (self, inData, inPos):
            self.data = inData
            self.offset = self.start = inPos
            self.next = inPos + 2
    
        def getData(self):
            return struct.unpack("<H", self.data[self.offset:self.next])[0]
    
        def nextData(self):
            self.incData()
            return struct.unpack("<H", self.data[self.offset:self.next])[0]

        def incData(self):
            self.offset += 2
            self.next += 2
            return

        def lenData(self):
            return (self.next - self.start)

    def disasm(self, bytes, offset=0, va=0):
        opData = self.Msp430Data(bytes, offset)
        while not opData.lenData() == 0:
            workData = opData.getData()
            if (workData >> 13):
                if ((workData >> 13) > 1):
                    # Parse out because of special operations
                    # This doesn't see to allow returning the function
                    # Have to set a variable
                    result =  decode_function[(((workData & DOUBLE_OPCODE) >> 12) - 4)](workData, opData, va)
                    # FILTHY HACK
                    for oper in result.opers:
                        oper._dis_regctx = self._dis_regctx
                    return result
                else:
                    # It is a Jump Opcode
                    mnem, flags = jcode[(workData & JUMP_OPCODE) >> 10]
                    op = Msp430Opcode(
                            va,
                            JUMP_OPCODE_TYPE,
                            mnem, 
                            [ Msp430JmpOper((workData & JUMP_OFFSET), opData, 0, va) ],
                            flags,
                            opData.lenData()
                            )
                    # FILTHY HACK
                    for oper in op.opers:
                        oper._dis_regctx = self._dis_regctx
                    return op
            else:
                # Test to see of primary input is not opcode
                if not (workData >> 12):
                    # Okay, something went wrong, so return the dirty word
                    raise Exception("Decode Error 0")

                ds_addr_mode = (workData & SOURCE_ADDR_MODE) >> 4
                dsreg = workData & DEST_REG
                op_bw = (workData & BYTE_WORD) >> 6
                dsopsize = 0
                # Test op_dw here to ensure it is used correctly
                if (((workData & SINGLE_OPCODE) >> 7) in [1,3,5,6]) and op_bw:
                    # Okay, something went wrong, so return the dirty word
                    raise Exception("Decode Error 1")
                if (ds_addr_mode == REG_INDEX) or (ds_addr_mode == REG_IND_AUTOINC):
                    dsopsize = 1
                # It is a Single Opcode
                # Process reti so don't have to do a 
                # string compare on mnem during repr
                if (((workData & SINGLE_OPCODE) >> 7) == 6):
                    if (workData & RETI_MASK):
                        mnem, flags = scode[6]
                        return Msp430Opcode( va, SP_OPCODE_TYPE, mnem, [], flags, opData.lenData())
                    else:
                        # Okay, something went wrong, so return the dirty word
                        raise Exception('Decode Error 2')
                else:
                    mnem, flags = scode[(workData & SINGLE_OPCODE) >> 7]
                    flags |= (op_bw << 8)
                    op = Msp430Opcode(
                            va,
                            SINGLE_OPCODE_TYPE,
                            mnem,
                            [ Msp430Operands[ds_addr_mode](dsreg, opData, dsopsize, va) ],
                            flags,
                            opData.lenData()
                            )
                    # FILTHY HACK
                    for oper in op.opers:
                        oper._dis_regctx = self._dis_regctx
                    return op
        # Primary Functional registers index values
        #REG_PC = 0  # reg0 is the Program Counter
        #REG_SP = 1  # reg1 is the Stack Pointer
        #REG_SR = 2  # reg2 is the Status Register
        #REG_CG = 3  # reg3 is the Constant Generator

    def getPointerSize(self):
        return 2

    def getProgramCounterIndex(self):
        return REG_PC

    def getStackCounterIndex(self):
        return REG_SP

    def getFrameCounterIndex(self):
        return None
            
    def getRegisterCount(self):
        """
        Return the number of registers
        """
        return len(registers)

    def clearRegisters(self, regcount):
        array = []
        for i in range(regcount):
            array.append(0)
        return array


Msp430Operands = [
        Msp430RegDirectOper,
        Msp430RegIndexOper,
        Msp430RegIndirOper,
        Msp430RegIndirAutoincOper,
        Msp430JmpOper,
]
