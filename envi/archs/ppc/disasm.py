import envi
import envi.bits as e_bits

import copy
import struct


from envi.archs.ppc.disasm import *
from envi.archs.ppc.regs import *
from const import *


def p_rDrArB(sdef, off, flags=0):
    pass

def p_rDrAUimm(sdef, off, flags=0):
    pass

def p_rDrA(sdef, off, flags=0):
    pass

def p_rDrArBcrfS(sdef, off, flags=0):   # evsel
    pass

def p_rDSIMM(sdef, off, flags=0):
    pass

def p_rSrArB(sdef, off, flags=0):
    pass

def p_rSrAUimm(sdef, off, flags=0):
    pass

def p_rDUimmRb(sdef, off, flags=0):
    pass

def p_rSrA(sdef, off, flags=0):
    pass

def p_frD__frB(sdef, off, flags=0):
    pass

def p_crD_frAfrB(sdef, off, flags=0):       # fcmpo, fcmpu
    pass

def p_frDfrAfrBfrC(sdef, off, flags=0):
    pass

def p_frDfrAfrB(sdef, off, flags=0):
    pass

def p_CTrArB(sdef, off, flags=0):
    pass

def p_rDrArBcrb(sdef, off, flags=0):
    pass

def p_rDrAD(sdef, off, flags=0):
    pass

def p_rDrADS(sdef, off, flags=0):
    pass

def p_frDrAD(sdef, off, flags=0):
    pass

def p_frDrArB(sdef, off, flags=0):
    pass

def p_vDrArB(sdef, off, flags=0):
    pass

def p_MO(sdef, off, flags=0):
    pass

def p_crD_crfS(sdef, off, flags=0):
    pass

def p_crD(sdef, off, flags=0):
    pass

def p_rD(sdef, off, flags=0):
    pass

def p_rDDCRN(sdef, off, flags=0):
    pass

def p_frD(sdef, off, flags=0):
    pass

def p_rD_CRM(sdef, off, flags=0):    # can combine these with a flag??
    pass

def p_rDPMRN(sdef, off, flags=0):
    pass

def p_rDSPRN(sdef, off, flags=0):
    pass

def p_rDTBRN(sdef, off, flags=0):
    pass

def p_rDTMRN(sdef, off, flags=0):
    pass

def p_vD(sdef, off, flags=0):
    pass

def p_rB(sdef, off, flags=0):
    pass

def p_rD_CRM(sdef, off, flags=0):
    pass

def p_rS_DCRN(sdef, off, flags=0):
    pass

def p_crbD(sdef, off, flags=0):
    pass

def p_LFMWfrB(sdef, off, flags=0):
    pass

def p_crD_WIMM(sdef, off, flags=0):
    pass

def p_rS(sdef, off, flags=0):
    pass

def p_rS_CRM(sdef, off, flags=0):
    pass

def p_rDrASimm(sdef, off, flags=0):
    pass

def p_rSrArBmb(sdef, off, flags=0):
    pass

def p_rSrArBmb(sdef, off, flags=0):
    pass

def p_rSrAshme(sdef, off, flags=0):
    pass


class PpcDisasm:
    def __init__(self):
        # any speedy stuff here
        self._dis_regctx = PpcRegisterContext()
        self.endian = ENDIAN_MSB

    def setEndian(self, endian):
        self.endian = endian
        self.fmt = ('<I', '>I')[endian]


    def disasm(self, bytez, offset, va):
        """
        Parse a sequence of bytes out into an envi.Opcode instance.
        """
        # Stuff we'll be putting in the opcode object
        optype = None # This gets set if we successfully decode below
        startoff = offset # Use startoff as a size knob if needed
        mnem = None 
        operands = []
        prefixes = 0
        iflags = 0

        bytezlen = len(bytez)

        if offset + 4 < bytezlen:
            fmt = ('<I', '>I')[self.endian]
            ival = struct.unpack_from(fmt, bytez, offset)
            
            op = find_ppc(bytez, offset)
            
            if op == None:
                op = find_e(bytez, offset)

        if op == None and offset+2 < bytezlen:
            fmt = ('<H', '>H')[self.endian]
            ival = struct.unpack_from(fmt, bytez, offset)

            op = find_se(bytez, offset)



        key = ival >> 26    # how will VLE work?
        
        decoder = decoders[key]
        if decoder == None:
            raise InvalidInstruction(bytez[offset:offset+4], 'No Decoder Found: %x' % key, va)

        foostuff = decoder(ival, va)

        print foostuff

        #now make Opcode...

def d_4(ival, va):
    pass

dec_4 = {
        0 : None
        }
    
decoders = {
        2 : None,
        3 : None,
        4 : d_4,
        }

        
def genTests(abytez):
    import subprocess
    from subprocess import PIPE

    file('/tmp/ppcbytez', 'wb').write(''.join(abytez))
    proc = subprocess.Popen(['/usr/bin/powerpc-linux-gnu-objdump', '-D','/tmp/ppcbytez', '-b', 'binary', '-m', 'powerpc:e5500'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    data = proc.stdout.readlines()
    data = [x.strip() for x in data]
    data = [x.split('\t') for x in data]
    
    for parts in data:
        if len(parts) < 4:
            print parts
            continue
        ova, bytez, op, opers = parts[:4]
        ova = ova[:-1]
        bytez = bytez[6:8] + bytez[4:6] + bytez[2:4] + bytez[:2]
        yield ("        ('%s', 0x%s, '%s %s', 0, ())," % (bytez, ova, op, opers))

'''
###################################3
fmts = ['B', '>H', None, '>I']

import envi.archs.cc8051.optable8051 as optable
nofall_types = [
    optable.INS_AJMP,
    optable.INS_LJMP,
    optable.INS_RET,
    optable.INS_RETI,
    optable.INS_JMP,
]
branch_types = [
    optable.INS_NOP,
    optable.INS_AJMP,
    optable.INS_LJMP,
    optable.INS_JBC,
    optable.INS_ACALL,
    optable.INS_LCALL,
    optable.INS_JB,
    optable.INS_RET,
    optable.INS_JNB,
    optable.INS_RETI,
    optable.INS_JC,
    optable.INS_JNC,
    optable.INS_JZ,
    optable.INS_JNZ,
    optable.INS_JMP,
    optable.INS_SJMP,
    optable.INS_CJNE,
    optable.INS_DJNZ,
]
call_types = [
    optable.INS_ACALL,
    optable.INS_LCALL,
]

sizenames = (None, "BYTE ","WORD ",None,"DWORD ")

OPTYPE_REG = 0x0
OPTYPE_IMM = 0x1
OPTYPE_INDEXED = 0x2
OPTYPE_INDIRECT = 0x3
OPTYPE_DIRECT = 0x4
OPTYPE_ADDR = 0x5
OPTYPE_PCREL = 0x6
OPTYPE_BIT = 0x7

def addrToName(mcanv, va):
    sym = mcanv.syms.getSymByAddr(va)
    if sym != None:
        return repr(sym)
    return "0x%.8x" % va

###########################################################################
#
# Operand objects for the Teridian 80515 architecture
#


class CC8051DirectOper(envi.Operand):
    """
    An operand which represents the dereference (memory read/write) of
    a memory location associated with an immediate.
    <0x80 - IRAM
    >0x7f - SFR
    """
    def __init__(self, imm):
        self.imm = imm
        self.type = OPTYPE_DIRECT
        self.tsize = 1

    def repr(self, op):
        name = reg_hash.get(self.imm, None)
        if name == None:
            return "%xh" % (self.imm)
        else:
            print "CHECKME:"
            return name[0]

    def getOperValue(self, op, emu=None):
        if emu == None: return None # This operand type requires an emulator
        return emu.readMemValue(self.getOperAddr(op, emu), 1)

    def setOperValue(self, op, emu, val):
        emu.writeMemValue(self.getOperAddr(op, emu), val, 1)

    def getOperAddr(self, op, emu=None):
        ret = self.imm
        if emu != None:
            base, size, offset, name = emu._emu_segments[SEG_IRAM]
            ret += offset
        return ret

    def isDeref(self):
        return True

    def render(self, mcanv, op, idx):
        value = reg_hash.get(self.imm, None)
        if value == None:
            value = self.imm
        mcanv.addText(" @")

        hint = mcanv.syms.getSymHint(op.va, idx)
        if hint != None:
            mcanv.addVaText(hint, value)
        else:
            name = addrToName(mcanv, value)
            mcanv.addVaText(name, value)

        #mcanv.addText("]")

    def __eq__(self, other):
        if not isinstance(other, CC8051DirectOper):
            return False
        if other.imm != self.imm:
            return False
        return True

class CC8051IndirectOper(envi.Operand):
    """
    An operand which represents the result of reading/writting memory from the
    dereference (with possible displacement) from a given register.
    0-0xff - IRAM
    """
    def __init__(self, reg):
        self.reg = reg
        self.type = OPTYPE_INDIRECT
        self.tsize = 1

    def repr(self, op):
        r = self._dis_regctx.getRegisterName(self.reg)
        return "@%s" % (r)

    def getOperValue(self, op, emu=None):
        if emu == None: return None # This operand type requires an emulator
        return emu.readMemValue(self.getOperAddr(op, emu), 1)

    def setOperValue(self, op, emu, val):
        emu.writeMemValue(self.getOperAddr(op, emu), val, 1)

    def getOperAddr(self, op, emu):
        if emu == None: return None # This operand type requires an emulator
        #base, size, offset, name = emu._emu_segments[SEG_IRAM]  #CHECKME: Is this correct?
        base, size, offset, name = emu.getSegmentInfo(op)  #CHECKME: Is this correct?
        rval = emu.getRegister(self.reg)
        return base + rval + offset

    def isDeref(self):
        return True

    def render(self, mcanv, op, idx):
        mcanv.addText(" @")
        mcanv.addNameText(self._dis_regctx.getRegisterName(self.reg), typename="registers")
        hint = mcanv.syms.getSymHint(op.va, idx)
        if hint != None:
            mcanv.addText(" + ")
            mcanv.addNameText(hint)

        #else:
            #if self.disp > 0:
                #mcanv.addText(" + ")
                #mcanv.addNameText(str(self.disp))
            #elif self.disp < 0:
                #mcanv.addText(" - ")
                #mcanv.addNameText(str(abs(self.disp)))
        #mcanv.addText("]")

    def __eq__(self, other):
        if not isinstance(other, CC8051IndirectOper):
            return False
        if other.reg != self.reg:
            return False
        #if other.disp != self.disp:
            #return False
        return True

class CC8051RegOper(envi.Operand):

    def __init__(self, reg):
        self.reg = reg
        self.type = OPTYPE_REG
        self.tsize = reg_table[reg][4]

    def repr(self, op):
        return self._dis_regctx.getRegisterName(self.reg)

    def getOperValue(self, op, emu=None):
        if emu == None: return None # This operand type requires an emulator
        return emu.getRegister(self.reg)

    def setOperValue(self, op, emu, value):
        emu.setRegister(self.reg, value)

    def render(self, mcanv, op, idx):
        hint = mcanv.syms.getSymHint(op.va, idx)
        if hint != None:
            mcanv.addNameText(name, typename="registers")
        else:
            name = self._dis_regctx.getRegisterName(self.reg)
            mcanv.addNameText(name, typename="registers")

    def __eq__(self, other):
        if not isinstance(other, CC8051RegOper):
            return False
        if other.reg != self.reg:
            return False
        return True

# For opcodes which need their immediate extended on print
sextend = []

class CC8051ImmOper(envi.Operand):
    """
    An operand representing an immediate.
    """
    def __init__(self, imm):
        self.imm = imm
        self.type = OPTYPE_IMM
        self.tsize = 1

    def repr(self, op):
        return "#0%xh" % self.imm

    def getOperValue(self, op, emu=None):
        return self.imm

    def render(self, mcanv, op, idx):
        value = self.imm
        hint = mcanv.syms.getSymHint(op.va, idx)
        if hint != None:
            mcanv.addVaText(hint)
        elif mcanv.mem.isValidPointer(value):
            name = addrToName(mcanv, value)
            mcanv.addVaText(name, value)
        else:
            mcanv.addNameText(str(value))

    def __eq__(self, other):
        if not isinstance(other, CC8051ImmOper):
            return False
        if other.imm != self.imm:
            return False
        return True

class CC8051AddrOper(envi.Operand):
    """
    An operand representing an Absolute FLASH address
    Only ever will be used for "movc" instruction
    """
    def __init__(self, addr):
        self.imm = addr
        self.type = OPTYPE_ADDR
        self.tsize = 1

    def repr(self, op):
        #FIXME: Symbol Resolver here.
        return "%.4xh" % (self.imm&0xffff)

    def getOperValue(self, op, emu=None):
        return self.imm

    def render(self, mcanv, op, idx):
        value = self.imm
        hint = mcanv.syms.getSymHint(op.va, idx)
        if hint != None:
            mcanv.addVaText(hint)
        elif mcanv.mem.isValidPointer(value):
            name = addrToName(mcanv, value)
            mcanv.addVaText(name, value)
        else:
            mcanv.addNameText(str(value))

    def __eq__(self, other):
        if not isinstance(other, CC8051AddrOper):
            return False
        if other.imm != self.imm:
            return False
        return True


class CC8051IndexedOper(envi.Operand):
    """
    This is the operand used for BASE-relative offsets
    for Code- in opcode "movc" and "jmp" opcodes
    """
    def __init__(self, basereg):
        self.basereg = basereg
        self.type = OPTYPE_INDEXED
        self.tsize = 1

    def repr(self, op):
        #return "\t; %.2xh" % (op.va + op.size + self.imm)
        return "@A+"+reg_table[self.basereg][0]

    def getOperValue(self, op, emu=None):
        if emu == None: return None
        retval = emu.getRegister(REG_A) + emu.getRegister(self.basereg)
        return retval

    def render(self, mcanv, op, idx):
        hint = mcanv.syms.getSymHint(op.va, idx)
        if hint != None:
            mcanv.addVaText(hint, value)
        else:
            mcanv.addNameText("@A", "registers" )
            mcanv.addText("+")
            mcanv.addNameText(reg_table[self.basereg][0], "registers")

    def __eq__(self, other):
        if not isinstance(other, CC8051IndexedOper):
            return False
        if other.imm != self.imm:
            return False
        return True

class CC8051PcRelOper(envi.Operand):
    """
    An operand representing a PC-relative address...  (+ or - the program counter)
    """
    def __init__(self, rel):
        self.imm = rel
        self.type = OPTYPE_PCREL
        self.tsize = 1

    def repr(self, op):
        return "%.4xh" % ((self.imm + op.va + len(op)) & 0xffff)

    def getOperValue(self, op, emu=None):
        return self.imm + op.va + len(op)

    def render(self, mcanv, op, idx):
        value = self.imm + op.va + len(op)
        hint = mcanv.syms.getSymHint(op.va, idx)
        if hint != None:
            mcanv.addVaText(hint)
        elif mcanv.mem.isValidPointer(value):
            name = addrToName(mcanv, value)
            mcanv.addVaText(name, value)
        else:
            mcanv.addNameText(str(value))

    def __eq__(self, other):
        if not isinstance(other, CC8051PcRelOper):
            return False
        if other.imm != self.imm:
            return False
        return True

class CC8051BitOper(envi.Operand):
    def __init__(self, bit, base=None, comp=False):
        self.bit = bit
        self.base = base
        self.comp = comp
        self.type = OPTYPE_BIT
        self.tsize = 1

    def __eq__(self, other):
        if not isinstance(other, CC8051BitOper):
            return False
        if other.bit != self.bit:
            return False == 1
        if other.base != self.base:
            return False == 1
        if other.comp != self.comp:
            return False
        return True

    def repr(self, op):
        if self.base == None:
            #print vars(self)
            s=[optable.FLAGS[self.bit]]#PSW name...
        else:
            #breg = self._dis_regctx.getRegisterName(self.base)
            s = ["#0%xh"%self.base, ".%x"%(self.bit)]
        if (self.comp):
            s.insert(0, "not ")
        return "".join(s)

    def getOperValue(self, op, emu=None):
        if emu == None: return None # This operand type requires an emulator
        byte = emu.readMemValue(self.getOperAddr(op, emu), 1)
        bit = (byte >> self.bit) & 1
        return bit

    def setOperValue(self, op, emu, val):
        byte = emu.readMemValue(self.getOperAddr(op, emu), 1)
        if val == 1:
            byte |= (1 << self.bit)
        elif val == 0:
            mask = (0xff ^ (1<<self.bit))
            byte &= mask
        if self.base == None:
            emu.calculateParity()
        return emu.writeMemValue(self.getOperAddr(op, emu), byte , 1)
    
    def getOperAddr(self, op, emu):
        base, size, offset, name = emu.getSegmentInfo(op)
        if self.base == None:
            return reg_table[REG_PSW][1]
        else:
            return self.base + offset

    def render(self, mcanv, op, idx):
        if (self.comp):
            mcanv.addText("not ")
        if self.base == None:
            mcanv.addNameText(optable.FLAGS[self.bit])#PSW name...
        else:
            breg = self._dis_regctx.getRegisterName(self.base)
            mcanv.addNameText(breg)
            mcanv.addNameText(".%x"%(self.bit))


class CC8051Opcode(envi.Opcode):

    def isCall(self):
        if self.opcode in call_types:
            return True
        return False

    def isBranch(self):
        return self.opcode in branch_types

    def isReturn(self):
        if self.opcode == optable.INS_RET or self.opcode == optable.INS_RETI:
            return True
        return False

    #FIXME: Implement this..
    #def getBranches(self, emu=None):
        #ret = []

        ## To start with we have no flags.
        #flags = 0
        #addb = False

        ## If we are a conditional branch, even our fallthrough
        ## case is conditional...
        #if self.opcode == opcode86.INS_BRANCHCC:
            #flags |= envi.BR_COND
            #addb = True

        ## If we can fall through, reflect that...
        #if not self.iflags & envi.IF_NOFALL:
            #ret.append((self.va + self.size, flags|envi.BR_FALL))

        ## In intel, if we have no operands, it has no
        ## further branches...
        #if len(self.opers) == 0:
            #return ret

        ## Check for a call...
        #if self.opcode == opcode86.INS_CALL:
            #flags |= envi.BR_PROC
            #addb = True

        ## A conditional call?  really?  what compiler did you use? ;)
        #elif self.opcode == opcode86.INS_CALLCC:
            #flags |= (envi.BR_PROC | envi.BR_COND)
            #addb = True

        #elif self.opcode == opcode86.INS_BRANCH:
            #oper0 = self.opers[0]
            #if isinstance(oper0, CC8051SibOper) and oper0.scale == 4:
                ## In the case with no emulator, note that our deref is
                ## from the base of a table. If we have one, parse out all the
                ## valid pointers from our base
                #base = oper0._getOperBase(emu)
                #if emu == None:
                    #ret.append((base, flags | envi.BR_DEREF | envi.BR_TABLE))

                #else:
                    ## Since we're parsing this out, lets just resolve the derefs
                    ## for our caller...
                    #dest = emu.readMemValue(base, oper0.tsize)
                    #while emu.isValidPointer(dest):
                        #ret.append((dest, envi.BR_COND))
                        #base += oper0.tsize
                        #dest = emu.readMemValue(base, oper0.tsize)
            #else:
                #addb = True

        #if addb:
            #oper0 = self.opers[0]
            #if oper0.isDeref():
                #flags |= envi.BR_DEREF
                #tova = oper0.getOperAddr(self, emu=emu)
            #else:
                #tova = oper0.getOperValue(self, emu=emu)

            ## FIXME check for SIB decodes and if we have an emulator,
            ## FIXME lets do switch case decoding here!

            #ret.append((tova, flags))

        #return ret

    def render(self, mcanv):
        """
        Render this opcode to the specified memory canvas
        """
        if self.prefixes:
            pfx = self._getPrefixName(self.prefixes)
            if pfx:
                mcanv.addNameText("%s: " % pfx, pfx)

        mcanv.addNameText(self.mnem, typename="mnemonic")
        mcanv.addText(" ")

        # Allow each of our operands to render
        imax = len(self.opers)
        lasti = imax - 1
        for i in xrange(imax):
            oper = self.opers[i]
            oper.render(mcanv, self, i)
            if i != lasti:
                mcanv.addText(",")

    def _getPrefixName(self, prefix):
        """
        """
        ret = []
        for byte,name in prefix_names:
            if prefix & byte:
                ret.append(name)
        return "".join(ret)

class CC8051Disasm:
    def __init__(self):
        # any speedy stuff here
        self._dis_regctx = CC8051RegisterContext()


    def disasm(self, bytes, offset, va):
        """
        Parse a sequence of bytes out into an envi.Opcode instance.
        """
        # Stuff we'll be putting in the opcode object
        optype = None # This gets set if we successfully decode below
        startoff = offset # Use startoff as a size knob if needed
        mnem = None 
        operands = []
        prefixes = 0
        iflags = 0
        
        obyte = ord(bytes[offset])
        #print "OBYTE",hex(obyte)
        opdesc = optable.table_main[obyte]

        #print repr(opdesc)
        mnem = opdesc[1]
        optype = opdesc[0]
        if optype == None:
            #print tabidx
            #print opdesc
            #print "OPTTYPE 0"
            raise envi.InvalidInstruction()

        operoffset = 1
        opers = opdesc[6]
        # Begin parsing operands based off address method
        #print "%d opers"%len(opers)
        for i in xrange(len(opers)):         # operands tuple
            if (opers[i] == optable.OP_None):
                #print "WTF, None operand??"
                continue
            oper = None # Set this if we end up with an operand
            osize = 0

            # Pull out the operand description from the table
            operflags = opers[i]
            opertype = operflags & optable.OPERANDTYPEMASK
            operdesc = optable.OPERANDS_BY_OP[opertype]
            
            tsize = operdesc[4]

            #FIXME:  FUGLY!
            # tsize: size of the target data...
            # osize: number of instruction bytes used for the operand
            if opertype == optable.OP_REGISTER:
                osize = 0
                reg = (operflags&optable.OPERANDREGMASK)>>optable.OPERANDREGLOC
                oper = CC8051RegOper(reg)
                
            elif opertype == optable.OP_IMMEDIATE:
                osize = (operflags&optable.OPERANDFLAGMASK)>>optable.OPERANDFLAGLOC
                loc = offset+operoffset
                oper = CC8051ImmOper(imm=struct.unpack(fmts[osize-1],bytes[loc:loc+osize])[0])
                
            elif opertype == optable.OP_A:
                osize = 0
                reg = REG_A
                oper = CC8051RegOper(reg)

            elif opertype == optable.OP_ACC_DPTR_INDIRECT:
                osize = 0
                basereg = REG_DPTR
                oper = CC8051IndexedOper(basereg)
                
            elif opertype == optable.OP_ACC_PC_INDIRECT:
                #FIXME: DPTR relative addressing with SEGMENTS (accesses code and RAM both....)
                osize = 0
                #reg = REG_A
                basereg = REG_PC
                oper = CC8051IndexedOper(basereg)
                
            elif opertype == optable.OP_ADDR11:
                osize = 1
                loc = offset+operoffset
                addr11 = struct.unpack("B",bytes[loc-1] )[0] >> 5
                addr11 += struct.unpack("B",bytes[loc])[0]
                oper = CC8051AddrOper(addr11)
                
            elif opertype == optable.OP_ADDR16:
                osize = 2
                loc = offset+operoffset
                addr16, = struct.unpack(">H",bytes[loc:loc+2])
                oper = CC8051AddrOper(addr16)
                
            elif opertype == optable.OP_B:
                osize = 0
                reg = REG_B
                oper = CC8051RegOper(reg)
                
            elif opertype == optable.OP_C:
                osize = 0
                oper = CC8051BitOper(PSW_C)
                
            elif opertype == optable.OP_DPTR:
                osize = 0
                reg = REG_DPTR
                oper = CC8051RegOper(reg)
                
            elif opertype == optable.OP_DPTR_INDIRECT:
                osize = 0
                reg = REG_DPTR
                oper = CC8051IndirectOper(reg)
                
            elif opertype == optable.OP_DIRECT:
                osize = 1
                loc = offset+operoffset
                oper = CC8051DirectOper(imm=struct.unpack(fmts[osize-1],bytes[loc:loc+osize])[0])

            elif opertype == optable.OP_REG_INDIRECT:
                osize = 0
                reg = (operflags&optable.OPERANDREGMASK)>>optable.OPERANDREGLOC
                oper = CC8051IndirectOper(reg)

            elif opertype == optable.OP_REL:
                osize = 1
                loc = offset+operoffset
                #print "=%s="%repr(bytes[loc:loc+osize])
                oper = CC8051PcRelOper(struct.unpack("b",bytes[loc:loc+osize])[0])
                
            elif opertype == optable.OP_bit:
                osize = 1
                loc = offset+operoffset
                bitnum = struct.unpack("B",bytes[loc])[0]
                base = bitnum & 0xf8
                bit = bitnum & 7
                oper = CC8051BitOper(bit, base=base)  #FIXME: NOT SURE HOW TO RECODE UPPER 5 bits!
                
                #raise "How do I encode a OP_bit?"
            elif opertype == optable.OP_comp_bit:
                osize = 1
                loc = offset+operoffset
                bitnum = struct.unpack(fmts[osize-1],bytes[loc:loc+osize])[0]
                base = bitnum >> 3
                bit = bitnum & 7
                oper = CC8051BitOper(bit, base=base, comp=True)  # repr will need to split imm into upper 5 and lower 3 bits...  scale = 1 if "not" bit
                #raise "How do I encode a OM_comp_bit?"
            else:
                #osize = 0
                #operand = optable.OPERANDS_BY_OP[opertype]
                #oper = envi.Operand(, tsize, reg=optable.A)
                raise "WTF?  No clue what kind of OPERAND that is... %s"%opertype


            if oper != None:
                #print "operand: %s"%repr(oper)
                oper._dis_regctx = self._dis_regctx    # ugly hack from visi's code... :)
                operands.append(oper)
            else:
                raise "WTF, None operand??"
            operoffset += osize

        # Make global note of instructions who
        # do *not* fall through...
        if optype in nofall_types:
            iflags |= envi.IF_NOFALL

        #if priv_lookup.get(mnem, False):
            #iflags |= envi.IF_PRIV
        #sp.dumpTree(operands)

        ret = envi.Opcode(va, optype, mnem, prefixes, (offset-startoff)+opdesc[4], operands, iflags)

        return ret

    def getEmulator(self):
        return TeridianEmulator()

    def getRegisterCount(self):
        return len(reg_table)

    def getProgramCounterIndex(self):
        return REG_PC

    def getStackCounterIndex(self):
        return REG_SP

    def getFrameCounterIndex(self):
        return REG_BP

    def getRegisterName(self, regidx):
        return reg_table[reg_table]

    def getBranches(self, op, va, emu=None):
        """
        Return the discernable branches for the instruction.
        (with the assumption that it is located at va).
        If an optional emulator object is passed in, use the
        emulator (getOperValue()) to attempt to detect the
        target location for the branch in the emulation env.

        NOTE: This does *not* return a "branch" to the next
              instruction. Users should check IF_NOFALL.
        """
        ret = []

        if op.opcode in branch_types:

            if op.opers[-1].type == OPTYPE_IMM:
                ret.append(va + op.size + op.opers[-1].imm)

            elif emu != None:
                # If we have an emulator, lets see if it can figgure
                # it out...
                ret.append(emu.getOperValue(op, -1))

        return ret

    '''
