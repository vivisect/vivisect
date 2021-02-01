import sys
import copy
import struct
import logging

import envi
import envi.exc as e_exc
import envi.bits as e_bits
import envi.memory as e_mem

from . import regs, rxtables
from const import *

logger = logging.getLogger(__name__)


class RxOpcode(envi.Opcode):

    def __init__(self, va, opcode, mnem, opers, iflags=0, size=0):
        self.va = va
        self.opcode = opcode
        self.mnem = mnem
        self.opers = opers
        self.iflags = iflags | envi.ARCH_RXV2
        self.size = size

    def __len__(self):
        return self.size

    def render(self, mcanv):
        """
        Render this opcode to the specified memory canvas
        """
        mnem = self.mnem
        if self.iflags & IF_BYTE:
            mnem += '.b'
        elif self.iflags & IF_WORD:
            mnem += '.w'
        elif self.iflags & IF_LONG:
            mnem += '.l'

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

class RxRegDirectOper(envi.RegisterOper):
    '''
    register operand
    '''

    def __init__(self, reg, va=0, oflags=0):
        if reg is None:
            raise envi.InvalidInstruction(mesg="None Reg Type!",
                    bytez='f00!', va=va)
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
        return self.reg == regs.REG_PC

    def getWidth(self):
        return regs.rctx.getRegisterWidth(self.reg) / 8

    def getOperValue(self, op, emu=None, codeflow=False):
        if self.reg == regs.REG_PC and not codeflow:
            return self.va

        if emu is None:
            return None
        return emu.getRegister(self.reg)

    def setOperValue(self, op, emu=None, val=None):
        if emu is None:
            return None
        emu.setRegister(self.reg, val)



class RxDisasm:
    def __init__(self):
        self._dis_regctx = regs.RXv2RegisterContext()
        self._dis_oparch = envi.ARCH_MSP430

        self.HANDLERS = [None for x in range(len(formconsts))]
        self.HANDLERS[FORM_PCDSP] = self.form_PCDSP
        self.HANDLERS[FORM_RD_LI] = self.form_RD_LI
        self.HANDLERS[FORM_RD_IMM] = self.form_RD_IMM
        self.HANDLERS[FORM_RD_LD_RS] = self.form_RD_LD_RS
        self.HANDLERS[FORM_A_RS2_RS] = self.form_A_RS2_RS
        self.HANDLERS[FORM_RD_LD_MI_RS] = self.form_RD_LD_MI_RS

    def disasm(self, bytez, offset=0, va=0):
        curtable = rxtables.tblmain

        # bite off the first byte
        bval, = struct.unpack_from('B', bytez, offset)
        val = bval
        opsize = 1

        #print "val: 0x%x  bval: 0x%x" % (val, bval)
        nextbl, handler, mask, endval, opcode, mnem, operdefs, sz, iflags = curtable[bval]
        found = True
        
        #print "  tabline: %r" % (repr(curtable[bval]))
        if nextbl is not None:
            found = False
            # skip to the next table
            curtable = nextbl

            # search through the list looking for the right one...
            for nextbl, handler, mask, endval, opcode, mnem, operdefs, sz, iflags in curtable:
                ### IMPORTANT: the lists MUST BE in order from smallest to largest encoding!
                while sz > opsize:
                    # grab the next byte
                    bval, = struct.unpack_from('B', bytez, offset+opsize)
                    # update the running value we'll use to parse
                    val <<= 8
                    val |= bval
                    # update the opsize
                    opsize += 1

                # find a match:
                if val & mask != endval:
                    continue

                found = True
                break

        if not found:
            raise e_exc.InvalidInstruction(bytez[offset:offset+opsize], "Couldn't find a opcode match in the table")

        # we've found a match, parse it!
        logger.warning("PARSE MATCH FOUND: val: %x\n\t%x %x %x %r %r  %r  %x", val, mask, endval, opcode, mnem, operdefs, sz, iflags)
        print("PARSE MATCH FOUND: val: %x\n\t%x %x %x %r %r  %r  %x" % (val, mask, endval, opcode, mnem, operdefs, sz, iflags))

        # let's parse out the things
        fields = {}
        for fkey, fparts in operdefs:
            fdata = 0
            for shval, fmask in fparts:
                fdata |= ((val >> shval) & fmask)
            
            fields[fkey] = fdata

        if handler is not None:
            # if we have a handler, just let it do everything
            hndlFunc = self.HANDLERS[handler]
            return hndlFunc(va, opcode, mnem, fields, sz, iflags, bytez, offset+opsize)


        # deciding key fields and build operand tuple
        opercnt = len(fields)

        operkeys = fields.keys()
        if opercnt == 0:
            opers = ()

        else:
            opers = []
            if opercnt == 1:
                if 'rs' in operkeys:
                    if 'lds' in operkeys:
                        # we have a dsp(Rs) operand
                        raise Exception('Slow Parsing LDS operand...')
                    else:
                        opers.append(RxRegOper(reg, va))
                elif 'imm' in operkeys:
                    # immediates must be sources, can't write to the opcode!
                    pass

                
            elif opercnt == 2:
                #'li' gives a size for an extra IMM:#
                li = fields.get(O_LI)
                if li is not None:
                    if li == 3:
                        imm = e_bits.slowparsebytes(bytez, off, 3, signed=True, bigend=True)
                    else:
                        if li == 0:
                            li = 4

                        fmt = e_bits.getFormat(li, big_endian=True, signed=True)
                        imm, = struct.unpack_from(fmt, bytez, off)

                    opers.append(RxImmOper(imm, va=va))

                # check all the registers (and not quite)
                for regconst in O_RS, O_RS2, O_CR, O_A, O_RD, O_RD2:
                    reg = fields.get(regconst)
                    if reg is not None:
                        if regconst == O_CR:
                            opers.append(RxCRRegOper(reg, va=va))

                        else:
                            opers.append(RxRegOper(reg, va=va))

                    elif fields.get(O_RS2):
                        opers.append(RxRegOper(


            elif opercnt == 3:
                #'li' gives a size for an extra IMM:#
                li = fields.get(O_LI)
                if li is not None:
                    if li == 3:
                        imm = e_bits.slowparsebytes(bytez, off, 3, signed=True, bigend=True)
                    else:
                        if li == 0:
                            li = 4

                        fmt = e_bits.getFormat(li, big_endian=True, signed=True)
                        imm, = struct.unpack_from(fmt, bytez, off)

                    opers.append(RxImmOper(imm, va=va))

                # check all the registers (and not quite)
                for regconst in O_RS, O_RS2, O_CR, O_A, O_RD, O_RD2:
                    reg = fields.get(regconst)
                    if reg is not None:
                        if regconst == O_CR:
                            opers.append(RxCRRegOper(reg, va=va))

                        else:
                            opers.append(RxRegOper(reg, va=va))

                    elif fields.get(O_RS2):
                        opers.append(RxRegOper(

            elif opercnt == 4:
                        pass
        import envi.interactive as ei; ei.dbg_interact(locals(), globals())


        return RxOpcode(va, opcode, mnem, opers, iflags, size) 

    def form_PCDSP(self, va, opcode, mnem, fields, sz, iflags, bytez, off):
        import envi.interactive as ei; ei.dbg_interact(locals(), globals())
        opers = (RxPcdspOper(fields[O_PCDSP]), va)

        return RxOpcode(va, opcode, mnem, opers, iflags, size) 

    def form_RD_LD_MI_RS(self, va, opcode, mnem, fields, size, iflags, bytez, off):
        rd = fields.get(O_RD)
        lds = fields.get(O_LDS)
        mi = fields.get(O_MI)
        rs = fields.get(O_RS)

        # read dsp bytes:
        if lds == 3:
            # plain reg
            opers = (
                    RxRegOper(rs, va), 
                    RxRegOper(rd, va), 
                    )

        else:
            fmt = e_bits.getFormat(lds, big_endian=True, signed=True)
            dsp, = struct.unpack_from(fmt, bytez, off)

            oflags, tsize = MI_FLAGS[mi]

            opers = (
                    RxDspOper(rs, dsp, tsize, oflags, va), 
                    RxRegOper(rd, va), 
                    )

        return RxOpcode(va, opcode, mnem, opers, iflags, size) 

    def form_RD_LD_RS(self, va, opcode, mnem, fields, sz, iflags, bytez, off):
        import envi.interactive as ei; ei.dbg_interact(locals(), globals())
        opers = (RxPcdspOper(fdata, va), )

        return RxOpcode(va, opcode, mnem, opers, iflags, size) 

    def form_RD_IMM(self, va, opcode, mnem, fields, sz, iflags, bytez, off):
        import envi.interactive as ei; ei.dbg_interact(locals(), globals())
        opers = (RxPcdspOper(fdata, va), )

        return RxOpcode(va, opcode, mnem, opers, iflags, size) 

    def form_RD_LI(self, va, opcode, mnem, fields, sz, iflags, bytez, off):
        import envi.interactive as ei; ei.dbg_interact(locals(), globals())
        opers = (RxPcdspOper(fdata, va), )

        return RxOpcode(va, opcode, mnem, opers, iflags, size) 

    def form_A_RS2_RS(self, va, opcode, mnem, fields, sz, iflags, bytez, off):
        import envi.interactive as ei; ei.dbg_interact(locals(), globals())
        opers = (RxPcdspOper(fdata, va), )

        return RxOpcode(va, opcode, mnem, opers, iflags, size) 



    def getPointerSize(self):
        return 4

    def getProgramCounterIndex(self):
        return regs.REG_PC

    def getStackCounterIndex(self):
        return regs.REG_SP

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


class RxRegOper(envi.RegisterOper):
    def __init__(self, reg, va):
        self.reg = reg
        self.va = va

    def getOperValue(self, op, emu=None):
        if emu is None:
            return
        return emu.getRegister(self.reg)

    def setOperValue(self, op, emu, val):
        logger.warning("%s needs to implement setOperAddr!" % self.__class__.__name__)

    def getOperAddr(self, op, emu=None):
        pass

    def getWidth(self):
        return regs.rctx.getRegisterWidth(self.reg) / 8

    def repr(self, op):
        return regs.rctx.getRegisterName(self.reg)

    def render(self, mcanv, op, idx):
        rname = regs.rctx.getRegisterName(self.reg)
        mcanv.addNameText(rname, typename='registers')

class RxImmOper(envi.ImmedOper):
    def __init__(self, val, va):
        self.val = val
        self.va = va

    def getOperValue(self, op, emu=None):
        return self.val

    def setOperValue(self, op, emu, val):
        logger.warning("%s needs to implement setOperAddr!" % self.__class__.__name__)

    def getOperAddr(self, op, emu=None):
        logger.warning("%s needs to implement getOperAddr!" % self.__class__.__name__)

    def repr(self, op):
        return self.val

    def render(self, mcanv, op, idx):
        val = self.getOperValue(op)
        mcanv.addText('#')
        mcanv.addNameText('0x%.2x' % (val))

class RxPcdspOper(envi.ImmedOper):
    def __init__(self, val, va):
        self.val = val
        self.va = va

    def getOperValue(self, op, emu=None):
        return self.val

    def setOperValue(self, op, emu, val):
        logger.warning("%s needs to implement setOperAddr!" % self.__class__.__name__)

    def getOperAddr(self, op, emu=None):
        logger.warning("%s needs to implement getOperAddr!" % self.__class__.__name__)

    def repr(self, op):
        return self.val

    def render(self, mcanv, op, idx):
        val = self.getOperValue(op)
        mcanv.addText('#')
        mcanv.addNameText('0x%.2x' % (val))

class RxDspOper(envi.RegisterOper):
    def __init__(self, reg, dsp, tsize=1, oflags=0, va=None):
        self.oflags = oflags
        self.tsize = tsize
        self.reg = reg
        self.dsp = dsp
        self.va = va

    def getOperValue(self, op, emu=None):
        if emu is None:
            return

        taddr = self.getOperAddr(op, emu)
        return emu.readMemValue(taddr, self.tsize)

    def setOperValue(self, op, emu, val):
        if emu is not None:
            return None

        taddr = self.getOperAddr(op, emu)
        emu.writeMemValue(taddr, val, self.tsize)

    def getOperAddr(self, op, emu=None):
        if emu is None:
            return None
        return emu.getRegister(reg) + self.dsp

    def getWidth(self):
        return self.tsize

    def repr(self, op):
        szl = SIZE_BYTES[self.tsize]
        rname = regs.rctx.getRegisterName(self.reg)
        return "0x%x(%s).%s" % (self.dsp, rname, szl)

    def render(self, mcanv, op, idx):
        szl = SIZE_BYTES[self.oflags]
        rname = regs.rctx.getRegisterName(self.reg)
        mcanv.addNameText(szl, typename='offset')
        mcanv.addText('(')
        mcanv.addNameText(rname, typename='registers')
        mcanv.addText(').%s' % szl)







