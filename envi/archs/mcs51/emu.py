import sys

import envi
import envi.bits as e_bits
import envi.memory as e_mem

import copy
import struct

import opcode8051 as optable
from envi.archs.mcs51.disasm import *
from envi.archs.mcs51.regs import *
from envi.archs.mcs51 import *

import atlasutils.smartprint as sp

"""
32k internal program memory bank 0x0000-0x7fff ("bank 0") - always available so never needs to be switched into a bank
FL_BANK (SFR 0xb6) controls which external bank is available as 0x8000-0xffff
The 75m6531 has 4 banks including bank 0 available.
Reset sets the bank bits to 1 (making banks 0 and 1 available)

ports p0,p1,p2 are bit-tied to the registers P0, P1, P2.  Direction (Input versus Output) is controlled for each through Dir0, Dir1, Dir2 respectively.
"""
#FIXME: Handle banked access to 0x8000-0xffff
#FIXME: Do something smart with the ports, possibly implement interrupts and sequential state tracking (not just current state)

MCU_START       = 0x0000
IV_EXT0         = 0x0003
IV_TIMER0       = 0x000b
IV_EXT1         = 0x0013
IV_TIMER1       = 0x001b
INTVECTOR_4     = 0x0023

class StdCall(envi.CallingConvention):

    def getCallArgs(self, emu, count):
        esp = emu.getRegister(REG_ESP)
        esp += 1 # For the saved eip
        return struct.unpack("<%dB" % count, emu.readMemory(esp, count))

class Cdecl(envi.CallingConvention):

    def getCallArgs(self, emu, count):
        esp = emu.getRegister(REG_ESP)
        esp += 1 # For the saved eip
        return struct.unpack("<%dB" % count, emu.readMemory(esp, count))

    def setReturnValue(self, emu, value, ccinfo):
        esp = emu.getRegister(REG_ESP)
        eip = struct.unpack("B", emu.readMemory(esp, 1))[0]
        esp += 1 # For the saved eip

        emu.setRegister(REG_ESP, esp)
        emu.setRegister(REG_EAX, value)
        emu.setProgramCounter(eip)

class ThisCall(envi.CallingConvention):

    #FIXME do something about emulated argc vs our arg count...
    def getCallArgs(self, emu, count):
        #ret = [emu.getRegister(REG_ECX),]
        esp = emu.getRegister(REG_ESP)
        esp += 1 # For the saved eip
        return struct.unpack("<%dB" % count, emu.readMemory(esp, count))

    def setReturnValue(self, emu, value, ccinfo):
        """
        """
        if ccinfo == None:
            ccinfo = 0
        # Our first arg (if any) is in a reg
        esp = emu.getRegister(REG_ESP)
        eip = struct.unpack("<B", emu.readMemory(esp, 1))[0]
        esp += 1 # For the saved eip
        esp += ccinfo # Cleanup saved args
        emu.setRegister(REG_ESP, esp)
        emu.setRegister(REG_EAX, value)
        emu.setProgramCounter(eip)

# Pre-make these and use the same instances for speed
stdcall = StdCall()
thiscall = ThisCall()
cdecl = Cdecl()

OPER_SRC = 1
OPER_DST = 0


class i8051Emulator(Mcs51Module, Mcs51RegisterContext, envi.Emulator):

    def __init__(self, segs=None, regarray=None):
        self.segments = segs
        self.reg_table = reg_table
        # segments: flash-prog-mem, external-RAM, config-RAM, 8051-RAM
        # seglist syntax:  (base_va, size, offset_in_real_memory, name)
        # if not handed in, rega1rray is initialized to the standard init values for each register
        Mcs51Module.__init__(self)
        Mcs51RegisterContext.__init__(self)
        if regarray == None:
            regarray = []
            for rname,rloc,rmask,rfmt,rsz,rinit,intW,intR in self.reg_table:
                regarray.append(rinit)
                
        self.setupInternalMemMaps()
        self.initRegisters()
        self.fp_exceptions = []
        #self.addCallingConvention("stdcall", stdcall)
        #self.addCallingConvention("thiscall", thiscall)
        #self.addCallingConvention("cdecl", cdecl)

    
    def setupInternalMemMaps(self):
        for mmap in xrange(0,len(self.segments)):
            bva,size,offset,name = self.segments[mmap]
            try:
                self.memobj.addMemoryMap(bva+offset,0777,name, "\x00"*(size))
            except:
                sys.excepthook(*sys.exc_info())

    def initRegisters(self):
        for num in xrange(len(self.reg_table)):
            rname, rloc, rmask, rfmt, rsz, rinit, intW,intR = self.reg_table[num]
            self.setRegister(num, rinit)


    def stepi(self):
        pc = self.getProgramCounter()
        #bytes = self.readMemory(pc, 32)
        op = self.makeOpcode(pc)
        self.executeOpcode(op)

    def getRegister(self, index):
        rname, rloc, rmask, rfmt, rsz, rinit, intW, intR = self.reg_table[index]
        # PSW determines which bank of registers to use
        if index < 8:
            index += (self.getRegister(REG_PSW) & 0x18)
        if intR != None:
            return intR(index, self)
        else:
            return self.readMemValue(rloc, rsz)

    def setRegister(self, index, val):
        rname, rloc, rmask, rfmt, rsz, rinit, intW, intR = self.reg_table[index]
        if index < 8:
            index += (self.getRegister(REG_PSW) & 0x18)
        if intW != None:
            return intW(index, self, val)
        else:
            bytes = struct.pack(rfmt, val & rmask)
            return self.writeMemory(rloc, bytes)

    def undefFlags(self):
        """
        Used in PDE.
        A flag setting operation has resulted in un-defined value.  Set
        the flags to un-defined as well.
        """
        self.setRegister(REG_FLAGS, None)

    def setFlag(self, which, state):
        flags = self.getRegister(REG_FLAGS)
        # On PDE, assume we're setting enough flags...
        if flags ==  None:
            flags = 0

        if state:
            flags |= (1<<which)
        else:
            flags &= ~(1<<which)
        self.setRegister(REG_FLAGS, flags)

    def getFlag(self, which):
        flags = self.getRegister(REG_FLAGS)
        if flags == None:
            raise envi.PDEUndefinedFlag(self)
        return bool(flags & (1<<which))

    def readMemValue(self, addr, size):
        bytes = self.readMemory(addr, size)
        if bytes == None:
            return None
        #FIXME change this (and all uses of it) to passing in format...
        if len(bytes) != size:
            raise Exception("Read Gave Wrong Length  %x: %d:%d"%(addr,len(bytes),size))
        if size == 1:
            return struct.unpack("B", bytes)[0]
        elif size == 2:
            return struct.unpack(">H", bytes)[0]
        elif size == 4:
            return struct.unpack(">L", bytes)[0]
        elif size == 8:
            return struct.unpack(">Q", bytes)[0]

    def writeMemValue(self, addr, value, size):
        #FIXME change this (and all uses of it) to passing in format...
        if size == 1:
            bytes = struct.pack("B",value & 0xff)
        elif size == 2:
            bytes = struct.pack(">H",value & 0xffff)
        elif size == 4:
            bytes = struct.pack(">L", value & 0xffffffff)
        elif size == 8:
            bytes = struct.pack(">Q", value & 0xffffffffffffffff)
        self.writeMemory(addr, bytes)

    def readMemSignedValue(self, addr, size):
        bytes = self.readMemory(addr, size)
        if bytes == None:
            return None
        if size == 1:
            return struct.unpack("b", bytes)[0]
        elif size == 2:
            return struct.unpack("<h", bytes)[0]
        elif size == 4:
            return struct.unpack("<l", bytes)[0]

    def makeOpcode(self, pc):
        map = self.memobj._mem_bytelookup.get(pc & self.memobj._mem_mask)
        if map == None:
            raise envi.SegmentationViolation(pc)
        mapva, mperm, mapbytes = map
        if not mperm & e_mem.MM_READ:
            raise envi.SegmentationViolation(pc)
        offset = pc - mapva
        return self._arch_dis.disasm(mapbytes, offset, pc)

    def executeOpcode(self, op):
        # NOTE: If an opcode method returns
        #       other than None, that is the new eip
        meth = self.op_methods.get(op.mnem, None)
        if meth == None:
            raise envi.UnsupportedInstruction(self, op)
        x = meth(op)
        if x != None:
            self.setProgramCounter(x)
        else:
            pc = self.getProgramCounter()
            pc += op.size
            self.setProgramCounter(pc)

    def doPush(self, val):
        esp = self.getRegister(REG_SP)
        esp += 1
        self.writeMemValue(esp, val, 1)
        self.setRegister(REG_SP, esp)

    def doPop(self):
        esp = self.getRegister(REG_SP)
        val = self.readMemValue(esp, 1)
        self.setRegister(REG_SP, esp-1)
        return val

    def integerSubtraction(self, op):
        """
        Do the core of integer subtraction but only *return* the
        resulting value rather than assigning it.
        (allows cmp and sub to use the same code)
        """
        # Src op gets sign extended to dst
        #FIXME account for same operand with zero result for PDE
        dst = op.opers[OPER_DST].getOperValue(op, self)
        src = op.opers[OPER_SRC].getOperValue(op, self)

        if src == None or dst == None:
            self.undefFlags()
            return None

        # So we can either do a BUNCH of crazyness with xor and shifting to
        # get the necissary flags here, *or* we can just do both a signed and
        # unsigned sub and use the results.
        dsize = op.opers[OPER_DST].tsize
        ssize = op.opers[OPER_SRC].tsize
        # Sign extend immediates where the sizes don't match
        if dsize != ssize:
            src = e_bits.sign_extend(src, ssize, dsize)
            ssize = dsize
        return self.intSubBase(src, dst, ssize, dsize)

    def intSubBase(self, src, dst, ssize, dsize):

        usrc = e_bits.unsigned(src, ssize)
        udst = e_bits.unsigned(dst, dsize)

        ssrc = e_bits.signed(src, ssize)
        sdst = e_bits.signed(dst, dsize)

        ures = udst - usrc
        sres = sdst - ssrc

        #print "dsize/ssize: %d %d" % (dsize, ssize)
        #print "unsigned: %d %d %d" % (usrc, udst, ures)
        #print "signed: %d %d %d" % (ssrc, sdst, sres)

        self.setFlag(PSW_OV, e_bits.is_signed_overflow(sres, dsize))
        self.setFlag(PSW_AC, e_bits.is_aux_carry(usrc, udst))
        self.setFlag(PSW_C, e_bits.is_unsigned_carry(ures, dsize))
        self.setFlag(PSW_P, e_bits.is_parity_byte(ures))

        return ures

    def logicalAnd(self, op):
        dst = op.opers[OPER_DST].getOperValue(op, self)
        src = op.opers[OPER_SRC].getOperValue(op, self)

        # PDE
        if dst == None or src == None:
            self.undefFlags()
            op.opers[OPER_DST].setOperValue(op, self, None)
            return

        dsize = op.opers[OPER_DST].tsize
        ssize = op.opers[OPER_SRC].tsize

        # sign-extend an immediate if needed
        if dsize != ssize:
            src = e_bits.sign_extend(src, ssize, dsize)
            ssize = dsize

        # Make sure everybody's on the same bit page.
        dst = e_bits.unsigned(dst, dsize)
        src = e_bits.unsigned(src, ssize)

        res = src & dst

        self.setFlag(EFLAGS_AF, 0) # AF is undefined, but it seems like it is zeroed
        self.setFlag(EFLAGS_OF, 0)
        self.setFlag(EFLAGS_CF, 0)
        self.setFlag(EFLAGS_SF, e_bits.is_signed(res, dsize))
        self.setFlag(EFLAGS_ZF, not res)
        self.setFlag(EFLAGS_PF, e_bits.is_parity_byte(res))
        return res

    def addCallingConvention(self, name, obj):
        self.call_convs[name] = obj

    def hasCallingConvention(self, name):
        if self.call_convs.get(name) != None:
            return True
        return False

    def getCallArgs(self, count, cc):
        """
        Emulator implementors can implement this method to allow
        analysis modules a platform/architecture independant way
        to get stack/reg/whatever args.

        Usage: getCallArgs(3, "stdcall") -> (0, 32, 0xf00)
        """
        c = self.call_convs.get(cc, None)
        if c == None:
            raise UnknownCallingConvention(cc)

        return c.getCallArgs(self, count)

    def setReturnValue(self, value, cc, argc=0):
        """
        Emulator implementors can implement this method to allow
        analysis modules a platform/architecture independant way
        to set a function return value. (this should also take
        care of any argument cleanup or other return time tasks
        for the calling convention)
        """
        c = self.call_convs.get(cc, None)
        if c == None:
            raise UnknownCallingConvention(cc)

        return c.setReturnValue(self, value, argc)

    def getOperValue(self, op, idx):
        """
        Return the value for the operand at index idx for
        the given opcode reading memory and register states if necissary.

        In partially-defined emulation, this may return None
        """
        oper = op.opers[idx]
        return oper.getOperValue(op, self)

    def getOperAddress(self, op, idx):
        """
        Return the address that an operand which deref's memory
        would read from on getOperValue().
        """
        oper = op.opers[idx]
        return oper.getOperAddr(op, self)
        
    def setOperValue(self, op, idx, value):
        """
        Set the value of the target operand at index idx from
        opcode op.
        """
        oper = op.opers[idx]
        value = e_bits.unsigned(value, oper.tsize)
        return oper.setOperValue(op, self, value)

    def calculateParity(self):
        """
        recalculate EVEN parity on the PSW
        """
        pswtmp = self.getRegister(REG_PSW) >> 1
        parity = 0
        for x in xrange(7):
            parity += pswtmp & 1
            pswtmp >>= 1
        parity = parity % 2
        self.setFlag(PSW_P, parity)

    def getSegmentIndex(self, op):
        #FIXME: THIS IS FORNICATED
        # direct opers >0x80
        # opcodes movx and movc
        if op.opcode == optable.INS_MOVX:
            return SEG_XRAM
        if op.opcode == optable.INS_MOVC:
            return SEG_FLASH
        if (op.opers[0].type == OPTYPE_DIRECT and op.opers[0].getOperValue(op,self) >= 0x80) or (len(op.opers) > 1 and op.opers[1].type == OPTYPE_DIRECT and op.opers[1].getOperValue(op,self) >= 0x80):
            return SEG_SFR
        return SEG_IRAM


    # Beginning of Instruction methods
    def i_nop(self, op):
        pass

    def i_ajmp(self, op):
        #0x01   ajmp addr11
        val = op.opers[OPER_DST].getOperValue(op, self)
        return val

    i_ljmp = i_ajmp  # only difference is masked by ENVI: "ljmp addr16"
    i_sjmp = i_ajmp  # CHECKME: sjmp is relative.  make sure this is handled in Operand
    i_jmp = i_ajmp
    
    def i_jb(self, op):     #jmp if bit is set
        dst = op.opers[OPER_DST].getOperValue(op, self)
        if dst:
            val = op.opers[OPER_SRC].getOperValue(op, self)
            return val
        
    def i_jbc(self, op):    #jmp is bit is set, and clear the bit
        bit = op.opers[OPER_DST].getOperValue(op, self)
        if bit:
            val = op.opers[OPER_SRC].getOperValue(op, self)
            op.opers[OPER_DST].setOperValue(op, self, 0)
            return val

    def i_jnb(self, op):
        bit = op.opers[OPER_DST].getOperValue(op, self)
        if not bit:
            val = op.opers[OPER_SRC].getOperValue(op, self)
            return val
        

    def i_jc(self, op):    #jmp if Carry bit is set
        val = op.opers[OPER_DST].getOperValue(op, self)
        C = self.getFlag(PSW_C)
        if C:
            return val
    
    def i_jz(self, op):    #jmp if accumulator is zero
        val = op.opers[OPER_DST].getOperValue(op, self)
        A = self.getRegister(REG_A)
        if A == 0:
            return val
    
    def i_jnz(self, op):
        val = op.opers[OPER_DST].getOperValue(op, self)
        A = self.getRegister(REG_A)
        if A != 0:
            return val
    
    def i_djnz(self, op):
        dst = op.opers[OPER_DST].getOperValue(op, self)
        dst -= 1
        op.opers[OPER_DST].setOperValue(op, self, dst & 0xff)
        if dst:
            val = op.opers[OPER_SRC].getOperValue(op, self)
            return val
        
    def i_cjne(self, op):
        dst = op.opers[OPER_DST].getOperValue(op, self)
        src = op.opers[OPER_SRC].getOperValue(op, self)
        if dst == src:
            val = op.opers[OPER_DST].getOperValue(op, self)
            self.setFlag(PSW_C, 0)
            return val
            
        elif dst < src:
            self.setFlag(PSW_C, 1)
        else:
            self.setFlag(PSW_C, 0)

    
    def i_acall(self, op):
        # push PC on to the stack
        pc = self.getRegister(REG_PC) + len(op)
        self.doPush(pc&0xff)
        self.doPush(pc>>8)
        
        # now jmp to new location
        self.setRegister(REG_PC, op.opers[OPER_DST].getOperValue(op, self))

    i_lcall = i_acall  # only difference is masked by ENVI: "lcall addr16"

    def i_pop(self, op):
        val = self.doPop()
        op.opers[OPER_DST].setOperValue(op, self, val)

    def i_push(self, op):
        val = op.opers[OPER_DST].getOperValue(op, self)
        if op.opers[0].type == OPTYPE_IMM:
            val = e_bits.sign_extend(val, op.opers[0].tsize, 4) #FIXME 64bit
        self.doPush(val)

    def i_rr(self, op):
        A = self.getRegister(REG_A)
        val = (A>>1 + ((A<<7) & 0xff))
        self.setRegister(REG_A, val)
        
    def i_rrc(self, op):
        C = self.getFlag(PSW_C)
        A = self.getRegister(REG_A)
        val = (C<<7) + (A >> 1) + ((A << 6) & 0x7f) 
        C = A & 1
        self.setFlag(PSW_C, C)
        self.setRegister(REG_A, val)
        
    def i_rl(self, op):
        A = self.getRegister(REG_A)
        val = (A>>7 + ((A<<1) & 0xff))
        self.setRegister(REG_A, val)
        
    def i_rlc(self, op):
        C = self.getFlag(PSW_C)
        A = self.getRegister(REG_A)
        val = C + (A >> 6) + ((A << 1) & 0xfe) 
        C = A >> 7
        self.setFlag(PSW_C, C)
        self.setRegister(REG_A, val)
        
    def i_inc(self, op):
        val = op.opers[OPER_DST].getOperValue(op, self)
        width = op.opers[OPER_DST].tsize
        mask = e_bits.u_maxes[width]
        val += 1
        op.opers[OPER_DST].setOperValue(op, self, val&mask)
        
    def i_dec(self, op):
        val = op.opers[OPER_DST].getOperValue(op, self)
        width = op.opers[OPER_DST].tsize
        mask = e_bits.u_maxes[width]
        val -= 1
        op.opers[OPER_DST].setOperValue(op, self, val&0xff)
    
    def i_ret(self, op):
        pc = self.doPop() << 8
        pc += self.doPop()
        return pc
        #self.setRegister(REG_PC, pc)
    
    def i_reti(self, op):
        pc = self.doPop() << 8
        pc += self.doPop()
        return pc
        #self.setRegister(REG_PC, pc)
        # tell Interrupt Control System the interrupt handling is complete...
        # FIXME: Interrupt Control System flags update????
        
    def i_orl(self, op):#FIXME: FLAGS
        dst = op.opers[OPER_DST].getOperValue(op, self)
        src = op.opers[OPER_SRC].getOperValue(op, self)
        # PDE
        if dst == None or src == None:
            self.undefFlags()
            op.opers[OPER_DST].setOperValue(op, self, None)
            return

        op.opers[OPER_DST].setOperValue(op, self, (dst | src))
        self.calculateParity()  # if oper is the Carry bit (could be), recalc the PSW parity. #FIXME: Put in Bit operand?
        
    def i_anl(self, op):
        dst = op.opers[OPER_DST].getOperValue(op, self)
        src = op.opers[OPER_SRC].getOperValue(op, self)
        # PDE
        if dst == None or src == None:
            self.undefFlags()
            op.opers[OPER_DST].setOperValue(op, self, None)
            return

        val = (dst & src)
        op.opers[OPER_DST].setOperValue(op, self, val)
        self.calculateParity()  # if oper is the Carry bit (could be), recalc the PSW parity. #FIXME: Put in Bit operand?
        
    def i_xrl(self, op):
        dst = op.opers[OPER_DST].getOperValue(op, self)
        src = op.opers[OPER_SRC].getOperValue(op, self)
        # PDE
        if dst == None or src == None:
            self.undefFlags()
            op.opers[OPER_DST].setOperValue(op, self, None)
            return

        val = (dst ^ src)
        op.opers[OPER_DST].setOperValue(op, self, val)
        ### commented out... Carry bit not used for XRL?
        #self.calculateParity()  # if oper is the Carry bit (could be), recalc the PSW parity. #FIXME: Put in Bit operand?


    def i_mov(self, op):
        if isinstance(op.opers[0], Mcs51ImmOper) and isinstance(op.opers[1], Mcs51ImmOper):
            val = op.opers[OPER_DST].getOperValue(op, self)
            op.opers[OPER_SRC].setOperValue(op, self, val)
        else:
            val = op.opers[OPER_SRC].getOperValue(op, self)
            op.opers[OPER_DST].setOperValue(op, self, val)
        
    def i_movc(self, op):
        base, size, offset, name = self.segments[SEG_FLASH]
        addr = op.opers[OPER_SRC].getOperValue(op, self) + offset
        A = self.readMemValue(addr,1)
        self.setRegister(REG_A, A)

    def i_movx(self, op):
        base, size, offset, name = self.segments[SEG_XRAM]
        if op.opers[0].type == OPTYPE_REG:
            srcaddr = op.opers[OPER_SRC].getOperAddr(op, self) #+ offset
            #val = self.readMemValue(self.getOperAddr(op, emu), 1)
            val = self.readMemValue(srcaddr, 1)
            op.opers[OPER_DST].setOperValue(op, self, val)
        else:
            val = op.opers[OPER_SRC].getOperValue(op, self)
            dstaddr = op.opers[OPER_DST].getOperAddr(op, self)# + offset
            self.writeMemValue(dstaddr, val, 1)

    def i_setb(self, op):
        global fixop, emu
        #FIXME: this is borked.  wtf?
        fixop = op
        emu = self
        raise ("FIXME NOW!: i_setb")
        dst = op.opers[OPER_DST].getOperValue(op, self)
        src = op.opers[OPER_SRC].getOperValue(op, self)

    def i_da(self, op):
        C = self.getFlag(PSW_C)
        A = op.opers[0].getOperValue(op, self)

        nib1 = A & 0xf
        if C or (nib1 > 9):
            A += 6

        nib2 = A & 0xf0
        if (nib2 > 0x90):
            A += 0x60

        op.opers[0].setOperValue(op, self, A)


        if (A > 0x99):
            self.setFlag(PSW_C, 1)


    def i_xchd(self, op):
        dst = op.opers[OPER_DST].getOperValue(op, self)
        src = op.opers[OPER_SRC].getOperValue(op, self)

        dst = (dst & 0xf0) + (src & 0xf)
        src = (src & 0xf0) + (src & 0xf)

        op.opers[OPER_DST].setOperValue(op, self, dst)
        op.opers[OPER_SRC].setOperValue(op, self, src)


    def i_add(self, op):#CHECKME: FLAGS (completed but scary)
        dst = op.opers[OPER_DST].getOperValue(op, self)
        src = op.opers[OPER_SRC].getOperValue(op, self)
        
        dsize = op.opers[OPER_DST].tsize
        ssize = op.opers[OPER_SRC].tsize

        #FIXME PDE and flags
        if dst == None or src == None:
            self.undefFlags()
            self.setOperValue(op, 0, None)
            return

        if dsize > ssize:
            src = e_bits.sign_extend(src, ssize, dsize)
            ssize = dsize

        cf = 0
        if self.getFlag(PSW_C):
            cf = 1

        udst = e_bits.unsigned(dst, dsize)
        usrc = e_bits.unsigned(src, ssize)
        sdst = e_bits.signed(dst, dsize)
        ssrc = e_bits.signed(src, ssize)

        ures = udst + usrc
        sres = sdst + ssrc

        self.setFlag(PSW_C, e_bits.is_unsigned_carry(ures, dsize))
        self.setFlag(PSW_AC, e_bits.is_aux_carry(src,dst))
        self.setFlag(PSW_OV, e_bits.is_signed_overflow(sres, dsize))
        
        op.opers[OPER_DST].setOperValue(op, self, ures & 0xff)
        self.calculateParity()
        
    def i_addc(self, op):
        dst = op.opers[OPER_DST].getOperValue(op, self)
        src = op.opers[OPER_SRC].getOperValue(op, self)
        
        dsize = op.opers[OPER_DST].tsize
        ssize = op.opers[OPER_SRC].tsize

        #FIXME PDE and flags
        if dst == None or src == None:
            self.undefFlags()
            self.setOperValue(op, 0, None)
            return

        if dsize > ssize:
            src = e_bits.sign_extend(src, ssize, dsize)
            ssize = dsize

        cf = 0
        if self.getFlag(PSW_C):
            cf = 1

        udst = e_bits.unsigned(dst, dsize)
        usrc = e_bits.unsigned(src, ssize)
        sdst = e_bits.signed(dst, dsize)
        ssrc = e_bits.signed(src, ssize)

        ures = udst + usrc + cf
        sres = sdst + ssrc + cf

        self.setFlag(PSW_C, e_bits.is_unsigned_carry(ures, dsize))
        self.setFlag(PSW_AC, e_bits.is_aux_carry(src,dst))
        self.setFlag(PSW_OV, e_bits.is_signed_overflow(sres, dsize))
        
        op.opers[OPER_DST].setOperValue(op, self, ures & 0xff)
        self.calculateParity()
        
    def i_subb(self, op):#CHECKME: FLAGS (completed but scary)
        dst = op.opers[OPER_DST].getOperValue(op, self)
        src = op.opers[OPER_SRC].getOperValue(op, self)
        # PDE
        if dst == None or src == None:
            self.undefFlags()
            op.opers[OPER_DST].setOperValue(op, self, None)
            return
        
        val = dst - src
        op.opers[OPER_DST].setOperValue(op, self, val & 0xff)
        
        self.setFlag(PSW_OV, e_bits.is_signed_overflow(sres, dsize))
        self.setFlag(PSW_AC, e_bits.is_aux_carry(usrc, udst))
        self.setFlag(PSW_C, e_bits.is_unsigned_carry(ures, dsize))
        
        # Delete the following when confirmed correct bit settings for SUBB
        ###FIXME: USE e_bits like add and addc
        ### The Carry Bit (C) is set if a borrow was required for bit 7, otherwise it is cleared. In other words, if the unsigned value being subtracted is greater than the Accumulator the Carry Flag is set. (8052.com)
        ##if src > dst:
            ##self.setFlag(PSW_C, 1)
        ##else:
            ##self.setFlag(PSW_C, 0)
        
        ### The Auxillary Carry (AC) bit is set if a borrow was required for bit 3, otherwise it is cleared. In other words, the bit is set if the low nibble of the value being subtracted was greater than the low nibble of the Accumulator.(8052.com)
        ##if (src&0xf) > (dst&0xf):   #lower nibble needs to borrow
            ##self.setFlag(PSW_AC, 1)
        ##else:
            ##self.setFlag(PSW_AC, 0)

        ### The Overflow (OV) bit is set if a borrow was required for bit 6 or for bit 7, but not both. In other words, the subtraction of two signed bytes resulted in a value outside the range of a signed byte (-128 to 127). Otherwise it is cleared.(8052.com)
        ##if val & 0x80:  # FIXME: HACK, bit 6 or bit 7 borrow, but not both
            ##self.setFlag(PSW_OV, 1)
        ##else:
            ##self.setFlag(PSW_OV, 0)


        self.calculateParity()

    def i_subb(self, op):
        dst = op.opers[OPER_DST].getOperValue(op, self)
        src = op.opers[OPER_SRC].getOperValue(op, self)

        # Much like "integer subtraction" but we need
        # too add in the carry flag
        if src == None or dst == None:
            self.undefFlags()
            return None

        dsize = op.opers[OPER_DST].tsize
        ssize = op.opers[OPER_SRC].tsize
        # Sign extend immediates where the sizes don't match
        if dsize != ssize:
            src = e_bits.sign_extend(src, ssize, dsize)
            ssize = dsize
        src += self.getFlag(PSW_C)
        res = self.intSubBase(src, dst, ssize, dsize)
        self.setOperValue(op, 0, res)
        self.calculateParity()


    def i_mul(self, op):
        dst = op.opers[OPER_DST].getOperValue(op, self)
        src = op.opers[OPER_SRC].getOperValue(op, self)
        # PDE
        if dst == None or src == None:
            self.undefFlags()
            op.opers[OPER_DST].setOperValue(op, self, None)
            return
        
        val = dst * src
        op.opers[OPER_DST].setOperValue(op, self, (val & 0xff))

        self.setFlag(PSW_OV, (val >> 8))
        self.setFlag(PSW_C, 0)
        self.calculateParity()

    def i_div(self, op):
        dst = op.opers[OPER_DST].getOperValue(op, self)
        src = op.opers[OPER_SRC].getOperValue(op, self)
        # PDE
        if dst == None or src == None:
            self.undefFlags()
            op.opers[OPER_DST].setOperValue(op, self, None)
            return

        if src == 0: # division by zero
            self.setFlag(PSW_OV, 1)
        else:
            val = dst / src
            rem = dst % src
            op.opers[OPER_DST].setOperValue(op, self, val)
            op.opers[OPER_SRC].setOperValue(op, self, rem)
            self.setFlag(PSW_OV, 0)

        self.setFlag(PSW_C, 0)
        self.calculateParity()

    def i_cpl(self, op):
        val = op.opers[OPER_DST].getOperValue(op, self)
        val ^= 0xff
        op.opers[OPER_DST].setOperValue(op, self, val)

    def i_clr(self, op):
        op.opers[OPER_DST].setOperValue(op, self, 0)

    def i_swap(self, op):
        val = self.getRegister(REG_A)
        self.setRegister(REG_A, e_bits.byteswap(val, 1))

    def i_xch(self, op):
        dst = op.opers[OPER_DST].getOperValue(op, self)
        src = op.opers[OPER_SRC].getOperValue(op, self)
        # PDE
        if dst == None or src == None:
            self.undefFlags()
            op.opers[OPER_DST].setOperValue(op, self, None)
            return

        op.opers[OPER_DST].setOperValue(op, self, src)
        op.opers[OPER_SRC].setOperValue(op, self, dst)


######################### Architecture Specific Extensions ############################

class Mcs51Emulator(i8051Emulator):
    reg_table = reg_table
    def __init__(self, regarray=None):
        i8051Emulator.__init__(self, seglist_8051, regarray)

class CC1110Emulator(i8051Emulator):
    reg_table = reg_table
    def __init__(self, regarray=None):
        i8051Emulator.__init__(self, seglist_1110, regarray)

class CC2430Emulator(i8051Emulator):
    reg_table = reg_table
    def __init__(self, regarray=None):
        i8051Emulator.__init__(self, seglist_2430, regarray)


"""
import envi.archs.mcs51 as mcs51
import envi.memory as e_m

t_arch=mcs51.Mcs51Module()
e=t_arch.getEmulator()
m=e_m.MemoryObject()
e.setMemoryObject(m)
m.addMemoryMap(0x0000,0777,"memmap1", "\xff"*1024)

"""
