import sys
import copy
import struct
import logging

import envi
import envi.exc as e_exc
import envi.bits as e_bits
import envi.memory as e_mem

from . import regs, rxtables
from .const import *

logger = logging.getLogger(__name__)


class RxOpcode(envi.Opcode):

    def __init__(self, va, opcode, mnem, operands, iflags=0, size=0):
        self.iflags = iflags | envi.ARCH_RX
        envi.Opcode.__init__(self, va, opcode, mnem, 0, size, operands, iflags)

    def __len__(self):
        return self.size


    def __repr__(self):
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
        elif self.iflags & IF_UWORD:
            mnem += '.uw'
        elif self.iflags & IF_24BIT:
            mnem += '.a'
        elif self.iflags & IF_SMALL:
            mnem += '.s'


        return mnem + " " + ",".join([o.repr(self) for o in self.opers])

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
        elif self.iflags & IF_UWORD:
            mnem += '.uw'

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
        return regs.rctx.getRegisterWidth(self.reg) // 8

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

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if not self.reg == oper.reg:
            return False
        if not self.oflags == oper.oflags:
            return False
        return True



class RxDisasm:
    def __init__(self):
        self._dis_regctx = regs.RxRegisterContext()
        self._dis_oparch = envi.ARCH_RX

        self.HANDLERS = [None for x in range(len(formconsts))]
        self.HANDLERS[FORM_AD] = self.form_AD
        self.HANDLERS[FORM_IMM1] = self.form_IMM1
        self.HANDLERS[FORM_RTSD] = self.form_RTSD
        self.HANDLERS[FORM_MVFA] = self.form_MVFA
        self.HANDLERS[FORM_MOVLI] = self.form_MOVLI
        self.HANDLERS[FORM_PCDSP] = self.form_PCDSP
        self.HANDLERS[FORM_RD_LI] = self.form_RD_LI
        self.HANDLERS[FORM_RS2_LI] = self.form_RS2_LI
        self.HANDLERS[FORM_RD_IMM] = self.form_RD_IMM
        self.HANDLERS[FORM_RD_LD_RS] = self.form_RD_LD_RS
        self.HANDLERS[FORM_RD_LD_RS_L] = self.form_RD_LD_RS_L
        self.HANDLERS[FORM_RD_LD_RS_B] = self.form_RD_LD_RS_B
        self.HANDLERS[FORM_A_RS2_RS] = self.form_A_RS2_RS
        self.HANDLERS[FORM_LD_RS2_RS_L] = self.form_LD_RS2_RS_L
        self.HANDLERS[FORM_LD_RS2_RS_UB] = self.form_LD_RS2_RS_UB
        self.HANDLERS[FORM_RD_LD_MI_RS] = self.form_RD_LD_MI_RS
        self.HANDLERS[FORM_MOV_RD_SZ_LD_LI] = self.form_MOV_RD_SZ_LD_LI
        self.HANDLERS[FORM_SCCND] = self.form_SCCND
        self.HANDLERS[FORM_BMCND] = self.form_BMCND
        self.HANDLERS[FORM_GOOGOL] = self.form_GOOGOL
        self.HANDLERS[FORM_MOV_RI_RB] = self.form_MOV_RI_RB

    def disasm(self, bytez, off=0, va=0):
        curtable = rxtables.tblmain
        opvals = [None for x in range(10)]

        # bite off the first byte
        bval, = struct.unpack_from('B', bytez, off)
        val = bval
        opsize = 1
        opvals[opsize] = val

        #print("val: 0x%x  bval: 0x%x" % (val, bval))
        tbldefs = curtable[bval]
        if tbldefs is None:
            raise e_exc.InvalidInstruction(bytez=bytez[off:off+10], va=va)

        nextbl, handler, mask, endval, opcode, mnem, operdefs, opsz, iflags = tbldefs
        found = True
        
        #print("  tabline: %r" % (repr(curtable[bval])))
        if nextbl is not None:
            found = False
            # skip to the next table
            curtable = nextbl

            # search through the list looking for the right one...
            for nextbl, handler, mask, endval, opcode, mnem, operdefs, opsz, iflags in curtable:
                try:
                    while opsize < opsz:
                        # grab the next byte
                        bval, = struct.unpack_from('B', bytez, off+opsize)
                        # update the running value we'll use to parse
                        val <<= 8
                        val |= bval

                        # update the opsize and store the byte
                        opsize += 1
                        opvals[opsize] = val
                        #print(" ++ %x  0x%x  %r" % (bval, val, opvals))


                    # find a match:
                    if opvals[opsz] & mask != endval:
                        #masked = opvals[opsz] & mask
                        #print("-cmp- 0x%x & 0x%x (0x%x) != 0x%x" % (opvals[opsz], mask, masked, endval))
                        continue

                    found = True
                    break

                except Exception as e:
                    # if we don't have enough bytes to grow to a certain size, that possible decoding is invalid
                    #print("%r (%r)" % (e, type(e)))
                    continue

        else:   # true up the length for maintable entries
            while opsize < opsz:
                # grab the next byte
                bval, = struct.unpack_from('B', bytez, off+opsize)
                # update the running value we'll use to parse
                val <<= 8
                val |= bval
                # update the opsize and store the byte
                opsize += 1
                opvals[opsize] = val


        if not found:
            raise e_exc.InvalidInstruction(bytez[off:off+opsize], "Couldn't find a opcode match in the table")

        logger.debug("PARSE MATCH FOUND: val: %x\n\t%x %x %x %r %r  %r  %x", val, mask, endval, opcode, mnem, operdefs, opsz, iflags)


        # we've found a match, parse it!
        off += opsz
        val = opvals[opsz]

        # let's parse out the things
        fields = {}
        for fkey, fparts in operdefs:
            fdata = 0
            fullmask = 0

            for shval, fmask in fparts:
                fullmask |= fmask
                fdata |= ((val >> shval) & fmask)

            if fullmask > 0xff:
                # this is a >8 bit, we need to reverse byte order
                isize = 0
                newdata = 0
                while fullmask:
                    isize += 1
                    newdata <<= 8
                    newdata |= fdata & 0xff
                    fdata >>= 8
                    fullmask >>= 8

                if fkey != O_UIMM and 1 < isize < 4:
                    fdata = e_bits.sign_extend(newdata, isize, 4)
                    #print("0x%x: signed: %d, %d, 0x%x -> 0x%x" % (va, isize, 4, newdata, fdata))
                else:
                    #print("fkey: %r: %r" % (fkey, nms[fkey]))
                    fdata = newdata
                    #print("0x%x: NOT signed: %d, %d, 0x%x -> 0x%x" % (va, isize, 4, newdata, fdata))

            elif fullmask == 0xff:
                if fkey != O_UIMM:
                    fdata = e_bits.sign_extend(fdata, 1, 4)
            
            fields[fkey] = fdata

        if handler is not None:
            # if we have a handler, just let it do everything
            hndlFunc = self.HANDLERS[handler]
            #logger.debug("Handler: %r" % hndlFunc)
            return hndlFunc(va, opcode, mnem, fields, opsz, iflags, bytez, off)



        # first things first... parse out the O_SZ field and apply it to iflags and tsize
        operkeys = fields.keys()
        if O_SZ in operkeys:
            osz = fields.pop(O_SZ)
            flag, tsize = SZ[osz]
            iflags |= flag
            operkeys = fields.keys()
            oflags = 0

        elif O_MI in operkeys:
            mi = fields.pop(O_MI)
            operkeys = fields.keys()
            oflags, tsize = MI_FLAGS[mi]

        else:
            tsize = 1
            oflags = OF_B

        # deciding key fields and build operand tuple
        opercnt = len(fields)
        if opercnt == 0:
            opers = ()

        else:
            opers = []
            if opercnt == 1:
                logger.debug("Parser: 1-oper")
                for key, val in fields.items():
                    #logger.debug("  %d ---> %r" % (key, nms[key]))
                    opercls = OPERS.get(key)
                    opers = (
                            opercls(val, va),
                    )
                
            elif opercnt == 2:
                logger.debug("Parser: 2-oper")
                #'li' gives a size for an extra IMM:#
                li = fields.get(O_LI)
                if li is not None:
                    if li == 0:
                        li = 4
                        imm = e_bits.parsebytes(bytez, off, li, sign=False)
                    else:
                        imm = e_bits.parsebytes(bytez, off, li, sign=False)
                        imm = e_bits.sign_extend(imm, li, 4) 
                    #logger.debug("  li: %x   imm: 0x%x" % (li, imm))
                    off += li
                    opsz += li

                    opers.append(RxImmOper(imm, va=va))

                # check all the registers (and not quite)
                #logger.debug([nms[x] for x,y in fields.items()])
                for regconst in O_UIMM, O_IMM, O_RS, O_RS2, O_CR, O_A, O_RD, O_RD2:
                    val = fields.get(regconst)
                    logger.debug("  loop: %r = %r" % (nms[regconst], val))
                    if val is not None:
                        if regconst in (O_IMM, O_UIMM):
                            opers.append(RxImmOper(val, va=va))

                        elif regconst == O_A:
                            opers.append(RxRegOper(regs.REG_ACC0 + val, va))

                        elif regconst == O_CR:
                            opers.append(RxCRRegOper(val, va=va))

                        elif regconst == O_RS:
                            if O_LDS in operkeys:
                                lds = fields.get(O_LDS)
                                dsp = e_bits.parsebytes(bytez, off, lds, sign=False)
                                opers.append(RxDspOper(val, dsp, tsize=tsize, oflags=oflags, va=va))
                                off += lds
                                opsz += lds

                            elif O_DSPS in operkeys:
                                dsp = fields.get(O_DSPS)
                                opers.append(RxDspOper(val, dsp, tsize=tsize, va=va))

                            else:
                                opers.append(RxRegOper(val, va=va))

                        else:
                            opers.append(RxRegOper(val, va=va))

            else:   # 3 and 4 operand-parts
                logger.debug("Parser: 3/4/5-oper")
                #'li' gives a size for an extra IMM:#
                li = fields.get(O_LI)
                lds = fields.get(O_LDS)
                lds2 = fields.get(O_LDS2)
                ldd = fields.get(O_LDD)
                #logger.debug("ldd: %r   lds: %r" % (ldd, lds))

                if li is not None:
                    if li == 0:
                        li = 4
                        imm = e_bits.parsebytes(bytez, off, li, sign=False)
                    else:
                        imm = e_bits.parsebytes(bytez, off, li, sign=False)
                        imm = e_bits.sign_extend(imm, li, 4) 
                    #logger.debug("  li: %x   imm: 0x%x" % (li, imm))
                    off += li
                    opsz += li

                    opers.append(RxImmOper(imm, va=va))

                elif O_IMM in operkeys:
                    imm = fields.get(O_IMM)
                    #print("   imm: %x" % imm)
                    opers.append(RxImmOper(imm, va))

                elif O_UIMM in operkeys:
                    imm = fields.get(O_UIMM)
                    #print("   imm: %x" % imm)
                    opers.append(RxUImmOper(imm, va))

                # check all the registers (and not quite)
                for regconst in O_RS, O_RS2, O_CR, O_A, O_RD, O_RD2:
                    reg = fields.get(regconst)
                    logger.debug("  loop: %r = %r" % (nms[regconst], reg))
                    if reg is not None:
                        if regconst == O_CR:
                            opers.append(RxCRRegOper(reg, va=va))

                        elif regconst == O_A:
                            opers.append(RxRegOper(regs.REG_ACC0 + reg, va))

                        elif regconst == O_RD:
                            if ldd in (1,2):
                                #print(mnem, [nms[key] for key in operkeys])
                                dsp = e_bits.parsebytes(bytez, off, ldd, sign=False)
                                opers.append(RxDspOper(reg, dsp, tsize=tsize, oflags=oflags, va=va))
                                off += ldd
                                opsz += ldd

                            elif O_DSPD in operkeys:
                                dsp = fields.get(O_DSPD)
                                opers.append(RxDspOper(reg, dsp, tsize=tsize, va=va))

                            else:
                                opers.append(RxRegOper(reg, va=va))

                        elif regconst == O_RS:
                            if lds is not None and lds < 3:
                                dsp = e_bits.parsebytes(bytez, off, lds, sign=False)
                                opers.append(RxDspOper(reg, dsp, tsize=tsize, oflags=oflags, va=va))
                                off += lds
                                opsz += lds

                            elif O_DSPS in operkeys:
                                dsp = fields.get(O_DSPS)
                                opers.append(RxDspOper(reg, dsp, tsize=tsize, va=va))

                            else:
                                opers.append(RxRegOper(reg, va=va))

                        elif regconst == O_RS2:
                            if lds2 is not None and lds2 < 3:
                                dsp = e_bits.parsebytes(bytez, off, lds2, sign=False)
                                opers.append(RxDspOper(reg, dsp, tsize=tsize, oflags=oflags, va=va))
                                off += lds2
                                opsz += lds2

                            else:
                                opers.append(RxRegOper(reg, va=va))

                        else:
                            opers.append(RxRegOper(reg, va=va))


        #import envi.interactive as ei; ei.dbg_interact(locals(), globals())
        return RxOpcode(va, opcode, mnem, opers, iflags, opsz)


    def form_RTSD(self, va, opcode, mnem, fields, opsz, iflags, bytez, off):
        uimm = fields[O_UIMM]
        uimm <<= 2  # rtsd keeps the stack 32-bit aligned

        rd = fields.get(O_RD)

        if rd is not None:
            rd2 = fields.get(O_RD2)
            opers = (
                    RxImmOper(uimm, va),
                    RxRegOper(rd, va),
                    RxRegOper(rd2, va),
                    )

        else:
            opers = (
                    RxImmOper(uimm, va),
                    )

        return RxOpcode(va, opcode, mnem, opers, iflags, opsz) 

    def form_PCDSP(self, va, opcode, mnem, fields, opsz, iflags, bytez, off):
        pcdsp = fields[O_PCDSP]

        # if we're the short-stuff...
        if opsz == 1 and pcdsp < 3:
            pcdsp += 8

        opers = (
                RxPcdspOper(pcdsp, va, relative=True),
                )

        return RxOpcode(va, opcode, mnem, opers, iflags, opsz) 

    def form_RD_LD_MI_RS(self, va, opcode, mnem, fields, opsz, iflags, bytez, off):
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
            if lds == 0:
                dsp = 0
            else:
                fmt = e_bits.getFormat(lds, big_endian=False, signed=False)
                dsp, = struct.unpack_from(fmt, bytez, off)
                opsz += lds
                off += lds

            oflags, tsize = MI_FLAGS[mi]

            opers = (
                    RxDspOper(rs, dsp, tsize, oflags, va), 
                    RxRegOper(rd, va), 
                    )

        return RxOpcode(va, opcode, mnem, opers, iflags, opsz) 

    def form_BMCND(self, va, opcode, mnem, fields, opsz, iflags, bytez, off):
        mnem = BMCND[fields.get(O_CD)]
        # rd, imm, cd, (ld)

        iflags |= IF_COND

        imm = fields.get(O_IMM)
        rd = fields.get(O_RD)
        ld = fields.get(O_LDD)

        if ld is None or ld == 3:
            ### NEXT PART: Documentation is incorrect, per email from Renesas, and their tooling
            #raise e_exc.InvalidInstruction(bytez[off-opsz:off], 
            #        'BMCND: ld cannot be 3')
            opers = (
                    RxImmOper(imm, va),
                    RxRegOper(rd, va),
                    )

        else:
            if ld is not None:
                # dsp operand with 0 or some 1- or 2-byte displacement
                badd = ld
                dsp = e_bits.parsebytes(bytez, off, badd, sign=False)
                opsz += badd

            else:
                # if dsp is 0, it's a simple deref
                dsp = 0

            opers = (
                    RxImmOper(imm, va),
                    RxDspOper(rd, dsp, tsize=1, oflags=OF_B, va=va),
                    )

        return RxOpcode(va, opcode, mnem, opers, iflags, opsz) 

    def form_SCCND(self, va, opcode, mnem, fields, opsz, iflags, bytez, off):
        #import envi.interactive as ei; ei.dbg_interact(locals(), globals())
        mnem = SCCND[fields.get(O_CD)]

        szflags, tsize = SZ[fields.get(O_SZ)]
        iflags |= IF_COND | szflags

        rd = fields.get(O_RD)
        ld = fields.get(O_LDD)
        if ld == 3: # treated as just a register operand
            opers = (RxRegOper(rd, va), )

        else:   # dsp operand with 0 or some 1- or 2-byte displacement
            badd = ld
            dsp = e_bits.parsebytes(bytez, off, badd, sign=False)
            opsz += badd

            opers = (RxDspOper(rd, dsp, tsize=tsize, va=va), )

        return RxOpcode(va, opcode, mnem, opers, iflags, opsz) 


    def form_LD_RS2_RS_L(self, va, opcode, mnem, fields, opsz, iflags, bytez, off):
        rs = fields.get(O_RS)
        rs2 = fields.get(O_RS2)
        lds = fields.get(O_LDS)
        tsize = 4
        oflags = OF_L

        if lds == 3:
            opers = (
                    RxRegOper(rs, va),
                    RxRegOper(rs2, va),
                    )
        else:
            dsps = 0
            if lds in (1,2):
                dsps = e_bits.parsebytes(bytez, off, lds, sign=False)
                opsz += lds
            
            opers = (
                    RxDspOper(rs, dsps, tsize=tsize, oflags=oflags, va=va), 
                    RxRegOper(rs2, va), 
                    )

        return RxOpcode(va, opcode, mnem, opers, iflags, opsz) 

    def form_LD_RS2_RS_UB(self, va, opcode, mnem, fields, opsz, iflags, bytez, off):
        rs = fields.get(O_RS)
        rs2 = fields.get(O_RS2)
        lds = fields.get(O_LDS)
        tsize = 1
        oflags = OF_UB

        if lds == 3:
            opers = (
                    RxRegOper(rs, va),
                    RxRegOper(rs2, va),
                    )
        else:
            dsps = 0
            if lds in (1,2):
                dsps = e_bits.parsebytes(bytez, off, lds, sign=False)
                opsz += lds
            
            opers = (
                    RxDspOper(rs, dsps, tsize=tsize, oflags=oflags, va=va), 
                    RxRegOper(rs2, va), 
                    )

        return RxOpcode(va, opcode, mnem, opers, iflags, opsz) 

    def form_MOV_RD_SZ_LD_LI(self, va, opcode, mnem, fields, opsz, iflags, bytez, off):
        li = fields.get(O_LI)
        rd = fields.get(O_RD)
        ldd = fields.get(O_LDD)
        osz = fields.get(O_SZ)
        oflag, tsize = SZ[osz]
        iflags |= IF_LONG

        if ldd == 3:
            oper1 = RxRegOper(rd, va)
        else:
            dspd = 0
            if ldd in (1,2):
                dspd = e_bits.parsebytes(bytez, off, ldd, sign=False)
                opsz += ldd
                off+= ldd
            
            oper1 = RxDspOper(rd, dspd, tsize=tsize, va=va)

        # li as 0 translates to 32-bit
        if li == 0:
            li = 4
        imm = e_bits.sign_extend(e_bits.parsebytes(bytez, off, li, sign=False), li, 4)
        opsz += li
        off+= li

        opers = (
                RxImmOper(imm, va),
                oper1,
                )

        return RxOpcode(va, opcode, mnem, opers, iflags, opsz) 

    def form_MOVLI(self, va, opcode, mnem, fields, opsz, iflags, bytez, off, tsize=1, oflags=OF_UB):
        rs = fields.get(O_RS)
        rd = fields.get(O_RD)
        opers = (
                RxDspOper(rs, 0, tsize=4, va=va),
                RxRegOper(rd, va),
                )

        return RxOpcode(va, opcode, mnem, opers, iflags, opsz) 

    def form_RD_LD_RS_B(self, va, opcode, mnem, fields, opsz, iflags, bytez, off):
        return self.form_RD_LD_RS(va, opcode, mnem, fields, opsz, iflags, bytez, off, tsize=1, oflags=OF_B)

    def form_RD_LD_RS_L(self, va, opcode, mnem, fields, opsz, iflags, bytez, off):
        return self.form_RD_LD_RS(va, opcode, mnem, fields, opsz, iflags, bytez, off, tsize=4, oflags=OF_L)

    def form_RD_LD_RS(self, va, opcode, mnem, fields, opsz, iflags, bytez, off, tsize=1, oflags=OF_UB):
        rs = fields.get(O_RS)
        rd = fields.get(O_RD)
        lds = fields.get(O_LDS)

        #print("RD_LD_RS: %r" % mnem)
        if lds is None:
            ldd = fields.get(O_LDD)

            if ldd == 3:
                opers = (
                        RxRegOper(rs, va),
                        RxRegOper(rd, va),
                        )
            else:
                if ldd in (1,2):
                    dspd = e_bits.parsebytes(bytez, off, ldd, sign=False)
                    opsz += ldd
                elif ldd == 0:
                    dspd = 0
                
                opers = (
                        RxRegOper(rs, va), 
                        RxDspOper(rd, dspd, tsize=tsize, oflags=oflags, va=va), 
                        )

        else:
            if lds == 3:
                opers = (
                        RxRegOper(rs, va),
                        RxRegOper(rd, va),
                        )
            else:
                dsps = 0
                if lds in (1,2):
                    dsps = e_bits.parsebytes(bytez, off, lds, sign=False)
                    opsz += lds
                
                opers = (
                        RxDspOper(rs, dsps, tsize=tsize, oflags=oflags, va=va), 
                        RxRegOper(rd, va), 
                        )

        return RxOpcode(va, opcode, mnem, opers, iflags, opsz) 

    def form_RD_IMM(self, va, opcode, mnem, fields, opsz, iflags, bytez, off):
        opers = (
                RxImmOper(fields.get(O_IMM), va),
                RxRegOper(fields.get(O_RD), va),
                )

        return RxOpcode(va, opcode, mnem, opers, iflags, opsz) 

    def form_MVFA(self, va, opcode, mnem, fields, opsz, iflags, bytez, off):
        imm = fields.get(O_IMM) ^ 2 # odd wtf moment in RX-land
        acc = fields.get(O_A)
        rd = fields.get(O_RD)
        opers = (
                RxImmOper(imm, va),
                RxRegOper(regs.REG_ACC0 + acc, va), 
                RxRegOper(rd, va),
                )

        return RxOpcode(va, opcode, mnem, opers, iflags, opsz) 

    def form_RD_LI(self, va, opcode, mnem, fields, opsz, iflags, bytez, off):
        #import envi.interactive as ei; ei.dbg_interact(locals(), globals())
        rd = fields.get(O_RD)
        li = fields.get(O_LI)
        badd = (li, 4)[li==0]
        imm = e_bits.parsebytes(bytez, off, badd, sign=False)
        imm = e_bits.sign_extend(imm, badd, 4)
        opsz += badd

        opers = (
                RxImmOper(imm, va),
                RxRegOper(rd, va), 
                )

        return RxOpcode(va, opcode, mnem, opers, iflags, opsz) 

    def form_RS2_LI(self, va, opcode, mnem, fields, opsz, iflags, bytez, off):
        #import envi.interactive as ei; ei.dbg_interact(locals(), globals())
        rs2 = fields.get(O_RS2)
        li = fields.get(O_LI)
        badd = (li, 4)[li==0]
        imm = e_bits.parsebytes(bytez, off, badd, sign=False)
        imm = e_bits.sign_extend(imm, badd, 4)
        opsz += badd

        opers = (
                RxImmOper(imm, va),
                RxRegOper(rs2, va), 
                )

        return RxOpcode(va, opcode, mnem, opers, iflags, opsz) 

    def form_A_RS2_RS(self, va, opcode, mnem, fields, opsz, iflags, bytez, off):
        #import envi.interactive as ei; ei.dbg_interact(locals(), globals())
        rs = fields.get(O_RS)
        rs2 = fields.get(O_RS2)
        acc = fields.get(O_A)
        opers = (
                RxRegOper(rs, va), 
                RxRegOper(rs2, va), 
                RxRegOper(regs.REG_ACC0 + acc, va), 
                )

        return RxOpcode(va, opcode, mnem, opers, iflags, opsz) 

    def form_GOOGOL(self, va, opcode, mnem, fields, opsz, iflags, bytez, off):
        rs = fields.get(O_RS)
        rd = fields.get(O_RD)
        sz = fields.get(O_SZ)
        lds = fields.get(O_LDS)
        ldd = fields.get(O_LDD)

        niflags, tsize = SZ[sz]
        iflags |= niflags

        if lds > 2 or ldd > 2:
            raise InvalidInstruction()

        dsps = e_bits.parsebytes(bytez, off, lds, sign=False)
        off += lds
        opsz += lds

        dspd = e_bits.parsebytes(bytez, off, ldd, sign=False)
        opsz += ldd
        off += ldd

        opers = (
                RxDspOper(rs, dsps, tsize=tsize, va=va),
                RxDspOper(rd, dspd, tsize=tsize, va=va),
                )

        return RxOpcode(va, opcode, mnem, opers, iflags, opsz) 

    def form_MOV_RI_RB(self, va, opcode, mnem, fields, opsz, iflags, bytez, off):
        sz = fields.get(O_SZ)
        ri = fields.get(O_RI)
        rb = fields.get(O_RB)
        rd = fields.get(O_RD)
        rs = fields.get(O_RS)

        iflags, tsize = SZ[sz]

        if rs is None:
            opers = (
                    RxRegIdxOper(ri, rb, tsize=tsize, va=va),
                    RxRegOper(rd, va),
                    )
        else:
            opers = (
                    RxRegOper(rs, va),
                    RxRegIdxOper(ri, rb, tsize=tsize, va=va),
                    )

        return RxOpcode(va, opcode, mnem, opers, iflags, opsz) 

    def form_AD(self, va, opcode, mnem, fields, opsz, iflags, bytez, off):
        add = fields.get(O_ADD)
        ads = fields.get(O_ADS)
        
        rd = fields.get(O_RD)
        rs = fields.get(O_RS)

        osz = fields.get(O_SZ, 1)
        flag, tsize = SZ[osz]
        iflags |= flag

        if add is None:
            opers = (
                RxRegIncOper(rs, ads, tsize, va),
                RxRegOper(rd, va),
                )
        else:
            opers = (
                RxRegOper(rs, va),
                RxRegIncOper(rd, add, tsize, va),
                )

        return RxOpcode(va, opcode, mnem, opers, iflags, opsz) 

    def form_IMM1(self, va, opcode, mnem, fields, opsz, iflags, bytez, off):
        imm = fields.get(O_IMM)
        acc = fields.get(O_A)

        opers = (
            RxImmOper(imm + 1, va),     # special encoding.  for imm:1, add 1
            RxRegOper(regs.REG_ACC0 + acc, va),
            )

        return RxOpcode(va, opcode, mnem, opers, iflags, opsz) 


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
            if self.reg == regs.REG_PC:
                return op.va
            return
        return emu.getRegister(self.reg)

    def setOperValue(self, op, emu, val):
        emu.setRegister(self.reg, val)

    def getOperAddr(self, op, emu=None):
        pass

    def getWidth(self):
        return regs.rctx.getRegisterWidth(self.reg) // 8

    def repr(self, op):
        return regs.rctx.getRegisterName(self.reg)

    def render(self, mcanv, op, idx):
        rname = regs.rctx.getRegisterName(self.reg)
        hint = mcanv.syms.getSymHint(op.va, idx)
        if hint is not None:
            mcanv.addNameText(hint)

        else:
            mcanv.addNameText(rname, typename='registers')

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if not self.reg == oper.reg:
            return False
        return True

class RxCBRegOper(RxRegOper):
    def __init__(self, flag, va):
        self.reg = regs.REG_C + (flag << 24)
        self.flag = flag
        self.va = va

    def getWidth(self):
        return 1    # FIXME: bit-fields are always wrong... should we return bits, not bytes?

    def repr(self, op):
        return regs.rctx.getRegisterName(self.reg)

    def render(self, mcanv, op, idx):
        hint = mcanv.syms.getSymHint(op.va, idx)
        if hint is not None:
            mcanv.addNameText(name, typename="registers")
        else:
            name = regs.rctx.getRegisterName(self.reg)
            rname = regs.rctx.getRegisterName(self.reg&RMETA_NMASK)
            mcanv.addNameText(name, name=rname, typename="registers")

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if not self.reg == oper.reg:
            return False
        if not self.flag == oper.flag:
            return False
        return True


class RxCRRegOper(RxRegOper):
    def __init__(self, reg, va):
        self.reg = regs.REG_PSW + reg
        self.va = va


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
        return "#" + hex(self.val)

    def render(self, mcanv, op, idx):
        value = self.getOperValue(op)
        mcanv.addText('#')

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

            if value >= 4096:
                mcanv.addNameText('0x%.8x' % value)
            else:
                mcanv.addNameText(str(value))

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if not self.val == oper.val:
            return False
        return True

class RxUImmOper(RxImmOper):
    def getOperValue(self, op, emu=None):
        return self.val

class RxPcdspOper(envi.ImmedOper):
    def __init__(self, val, va, relative=True):
        self.val = val
        self.va = va
        self.rel = relative

    def getOperValue(self, op, emu=None):
        val = self.val
        if self.rel:
            val = (val + self.va) & 0xffffffff
        return val

    def setOperValue(self, op, emu, val):
        return None

    def getOperAddr(self, op, emu=None):
        return None

    def repr(self, op):
        return "0x%x" % self.getOperValue(op)

    def render(self, mcanv, op, idx):
        value = self.getOperValue(op)

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
            mcanv.addNameText('0x%.8x' % value)

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if not self.val == oper.val:
            return False
        if not self.rel == oper.rel:
            return False
        return True

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

        # dsp is multiplied by the tsize (per spec)
        dsp = self.dsp * self.tsize
        return emu.getRegister(reg) + dsp

    def getWidth(self):
        return self.tsize

    def repr(self, op):
        szl = SIZE_BYTES[self.oflags]
        rname = regs.rctx.getRegisterName(self.reg)
        dsp = self.dsp * self.tsize

        if szl is None:
            if self.dsp == 0:
                return "[%s]" % (rname)
            return "0x%x[%s]" % (dsp, rname)

        if self.dsp == 0:
            return "[%s].%s" % (rname, szl)
        return "0x%x[%s].%s" % (dsp, rname, szl)

    def render(self, mcanv, op, idx):
        szl = SIZE_BYTES[self.oflags]
        rname = regs.rctx.getRegisterName(self.reg)
        dsp = self.dsp * self.tsize

        if dsp != 0:
            mcanv.addNameText(hex(dsp), typename='offset')

        mcanv.addText('[')
        mcanv.addNameText(rname, typename='registers')
        if szl is None:
            mcanv.addText(']')
        else:
            mcanv.addText('].%s' % szl)

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if not self.oflags == oper.oflags:
            return False
        if not self.reg == oper.reg:
            return False
        if not self.tsize == oper.tsize:
            return False
        if not self.dsp == oper.dsp:
            return False
        return True

class RxRegIdxOper(envi.RegisterOper):
    def __init__(self, reg, idx, tsize=1, oflags=0, va=None):
        self.oflags = oflags
        self.tsize = tsize
        self.reg = reg
        self.idx = idx
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
        return emu.getRegister(reg) + emu.getRegister(self.idx)

    def getWidth(self):
        return self.tsize

    def repr(self, op):
        szl = SIZE_BYTES[self.oflags]
        rname = regs.rctx.getRegisterName(self.reg)
        iname = regs.rctx.getRegisterName(self.idx)
        if szl is None:
            return "[%s, %s]" % (rname, iname)

        return "[%s, %s].%s" % (rname, iname, szl)

    def render(self, mcanv, op, idx):
        szl = SIZE_BYTES[self.oflags]
        rname = regs.rctx.getRegisterName(self.reg)
        iname = regs.rctx.getRegisterName(self.idx)

        mcanv.addText('[')
        mcanv.addNameText(rname, typename='registers')
        mcanv.addText(', ')
        mcanv.addNameText(iname, typename='registers')
        if szl is None:
            mcanv.addText(']')
        else:
            mcanv.addText('].%s' % szl)

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if not self.oflags == oper.oflags:
            return False
        if not self.reg == oper.reg:
            return False
        if not self.tsize == oper.tsize:
            return False
        if not self.idx == oper.idx:
            return False
        return True

class RxRegIncOper(envi.RegisterOper):
    '''
    Incrementing/Decrementing Reg-deref
    ad determins which:
        (ad == 0)  means post-inc   [Rx+]
        (ad == 1)  means pre-dec    [-Rx]
    '''
    def __init__(self, reg, ad, tsize=1, va=None):
        self.tsize = tsize
        self.reg = reg
        self.ad = ad
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

        addr = emu.getRegister(reg)
        if self.ad == 1: # 0== post-inc, 1== pre-dec
            newreg = addr - 1
            addr = newreg
        else:
            newreg = addr + 1

        if emu.getMeta("forrealz"):
            emu.setRegister(self.reg, newreg)
        return addr

    def getWidth(self):
        return self.tsize

    def repr(self, op):
        rname = regs.rctx.getRegisterName(self.reg)
        if self.ad == 1:
            return "[-%s]" % (rname)
        return "[%s+]" % (rname)

    def render(self, mcanv, op, idx):
        rname = regs.rctx.getRegisterName(self.reg)
        mcanv.addText('[')
        if self.ad == 1:
            mcanv.addText('-')
            mcanv.addNameText(rname, typename='registers')
        else:
            mcanv.addNameText(rname, typename='registers')
            mcanv.addText('+')
        mcanv.addText(']')

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if not self.reg == oper.reg:
            return False
        if not self.tsize == oper.tsize:
            return False
        if not self.ad == oper.ad:
            return False
        return True



OPERS = {}
OPERS[O_CB] = RxCBRegOper
OPERS[O_CR] = RxCRRegOper
OPERS[O_PCDSP] = RxPcdspOper
OPERS[O_IMM] = RxImmOper
OPERS[O_UIMM] = RxUImmOper
OPERS[O_RD] = RxRegOper
OPERS[O_RD2] = RxRegOper
OPERS[O_RS] = RxRegOper
OPERS[O_RS2] = RxRegOper

