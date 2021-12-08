import struct

import envi
import envi.bits as e_bits
import envi.archs.i386 as e_i386
from . import opcode64 as opcode86

from envi.const import RMETA_NMASK

from envi.archs.i386.disasm import iflag_lookup, operand_range, priv_lookup, \
        i386Opcode, i386ImmOper, i386RegOper, i386ImmMemOper, i386RegMemOper, \
        i386SibOper, PREFIX_REPNZ, PREFIX_REPZ, PREFIX_REP, PREFIX_REP_SIMD, \
        PREFIX_OP_SIZE, PREFIX_ADDR_SIZE, MANDATORY_PREFIXES, PREFIX_REP_MASK,\
        RMETA_LOW8, RMETA_LOW16

from .regs import *
from envi.archs.i386.opconst import OP_EXTRA_MEMSIZES, OP_MEM_B, OP_MEM_W, OP_MEM_D, \
                                    OP_MEM_Q, OP_MEM_DQ, OP_MEM_QQ, OP_MEMMASK, \
                                    INS_VEXREQ, OP_NOVEXL, INS_VEXNOPREF, OP_NOREX, \
                                    PREFIX_REX, PREFIX_REX_B, PREFIX_REX_X, PREFIX_REX_W, \
                                    PREFIX_REX_MASK, PREFIX_REX_RXB, PREFIX_REX_R
all_tables = opcode86.tables86

# Pre generate these for fast lookup. Because our REX prefixes have the same relative
# bit relationship to eachother, we can cheat a little...
amd64_prefixes = list(e_i386.i386_prefixes)
amd64_prefixes[0x40] = (0x10 << 16)
amd64_prefixes[0x41] = (0x11 << 16)
amd64_prefixes[0x42] = (0x12 << 16)
amd64_prefixes[0x43] = (0x13 << 16)
amd64_prefixes[0x44] = (0x14 << 16)
amd64_prefixes[0x45] = (0x15 << 16)
amd64_prefixes[0x46] = (0x16 << 16)
amd64_prefixes[0x47] = (0x17 << 16)
amd64_prefixes[0x48] = (0x18 << 16)
amd64_prefixes[0x49] = (0x19 << 16)
amd64_prefixes[0x4a] = (0x1a << 16)
amd64_prefixes[0x4b] = (0x1b << 16)
amd64_prefixes[0x4c] = (0x1c << 16)
amd64_prefixes[0x4d] = (0x1d << 16)
amd64_prefixes[0x4e] = (0x1e << 16)
amd64_prefixes[0x4f] = (0x1f << 16)
amd64_prefixes[0xc5] = (0x20 << 16)  # VEX 2byte
amd64_prefixes[0xc4] = (0x40 << 16)  # VEX 3byte


REX_HIGH_DROP = ~(e_i386.RMETA_HIGH8 ^ e_i386.RMETA_LOW8)  # FIXME: this is ugly

PREFIX_VEX2  = 0x200000  # 2 byte VEX (data stored in opcode)
PREFIX_VEX3  = 0x400000  # 3 byte VEX (data stored in opcode)
PREFIX_VEX_L = 0x800000  # L bit set
PREFIX_VEX   = PREFIX_VEX2 | PREFIX_VEX3

PREFIX_SIZE_BOTH = (PREFIX_REX_W | PREFIX_VEX_L)

IMM_REQOFFS = (opcode86.ADDRMETH_I, opcode86.ADDRMETH_J, opcode86.ADDRMETH_L)

VEX_V_SHIFT  = 59

REX_BUMP = 8
MODE_16 = 0
MODE_32 = 1
MODE_64 = 2

RMETA_LOW32 = 0x200000

META_SIZES = [0 for i in range(9)]
META_SIZES[1] = RMETA_LOW8
META_SIZES[2] = RMETA_LOW16
META_SIZES[4] = RMETA_LOW32

class Amd64Opcode(i386Opcode):
    def __init__(self, va, opcode, mnem, prefixes, size, operands, iflags=0):
        '''
        Overriding this from envi/__init__.py in order to set the mnem for VEX instructions
        Technically this should be on the i386 one as well, but we don't yet support VEX for that.
        So oh well
        '''
        envi.Opcode.__init__(self, va, opcode, mnem, prefixes, size, operands, iflags)
        if prefixes & PREFIX_VEX and not opcode & INS_VEXNOPREF:
            mnem = 'v' + mnem
        self.mnem = mnem

    def __repr__(self):
        """
        Over-ride this if you want to make arch specific repr.
        """
        pfx = self.getPrefixName()
        if pfx:
            pfx = '%s: ' % pfx

        return pfx + self.mnem + " " + ",".join([o.repr(self) for o in self.opers])

    def render(self, mcanv):
        """
        Render this opcode to the specified memory canvas
        """
        if self.prefixes:
            pfx = self.getPrefixName()
            if pfx:
                mcanv.addNameText("%s: " % pfx, pfx)

        mcanv.addNameText(self.mnem, typename="mnemonic")
        mcanv.addText(" ")

        # Allow each of our operands to render
        imax = len(self.opers)
        lasti = imax - 1
        for i in range(imax):
            oper = self.opers[i]
            oper.render(mcanv, self, i)
            if i != lasti:
                mcanv.addText(",")

class Amd64RipRelOper(envi.DerefOper):
    def __init__(self, imm, tsize):
        self.imm = imm
        self.tsize = tsize
        self._is_deref = True

    def getOperValue(self, op, emu=None):
        if not self._is_deref:  # Special lea behavior
            return self.getOperAddr(op)
        if emu is None:
            return None
        return emu.readMemValue(self.getOperAddr(op, emu), self.tsize)

    def setOperValue(self, op, emu, val):
        emu.writeMemValue(self.getOperAddr(op, emu), val, self.tsize)

    def getOperAddr(self, op, emu=None):
        return op.va + op.size + self.imm

    def isDeref(self):
        # The disassembler may reach in and set this (if lea...)
        return self._is_deref

    def isDiscrete(self):
        return True

    def render(self, mcanv, op, idx):
        destva = op.va + op.size + self.imm
        sym = mcanv.syms.getSymByAddr(destva)

        mcanv.addNameText(e_i386.sizenames[self.tsize])
        mcanv.addText(" [")
        mcanv.addNameText("rip", typename="registers")

        if self.imm > 0:
            mcanv.addText(" + ")
            if sym is not None:
                mcanv.addVaText("$%s" % repr(sym), destva)
            else:
                mcanv.addNameText(str(self.imm))
        elif self.imm < 0:
            mcanv.addText(" - ")
            if sym is not None:
                mcanv.addVaText("$%s" % repr(sym), destva)
            else:
                mcanv.addNameText(str(abs(self.imm)))
        mcanv.addText("]")

    def repr(self, op):
        return "%s [rip + %d]" % (e_i386.sizenames[self.tsize], self.imm)


operands_index = 2
vex_pp_table = ( (0xf,), (0x66,), (0xf3,), (0xf2,) )
vex3_mmmm_table = ( (None,), (None,), (0x38,), (0x3A,), None, None, None, None )   # None is invalid.  (None,) adds no table depths


class Amd64Disasm(e_i386.i386Disasm):

    def __init__(self, mode=MODE_64):
        e_i386.i386Disasm.__init__(self, mode=mode)
        self._dis_oparch = envi.ARCH_AMD64
        self._dis_prefixes = amd64_prefixes
        self._dis_regctx = Amd64RegisterContext()
        self.ptrsize = 8

        # 64-bit only
        self._dis_amethods[opcode86.ADDRMETH_B >> 16] = self.ameth_b
        self._dis_amethods[opcode86.ADDRMETH_H >> 16] = self.ameth_h
        self._dis_amethods[opcode86.ADDRMETH_E >> 16] = self.ameth_e
        self._dis_amethods[opcode86.ADDRMETH_L >> 16] = self.ameth_l
        self._dis_amethods[opcode86.ADDRMETH_VEXH >> 16] = self.ameth_vexh

        # Over-ride these which are in use by the i386 version of the ASM
        self.ROFFSETSIMD  = e_i386.getRegOffset(amd64regs, "ymm0")
        self.ROFFSETDEBUG = e_i386.getRegOffset(amd64regs, "debug0")
        self.ROFFSETCTRL  = e_i386.getRegOffset(amd64regs, "ctrl0")
        self.ROFFSETTEST  = e_i386.getRegOffset(amd64regs, "test0")
        self.ROFFSETSEG   = e_i386.getRegOffset(amd64regs, "es")
        self.ROFFSETFPU   = e_i386.getRegOffset(amd64regs, "st0")
        # Note: getRegOffset doesn't work on meta registers and mm* are aliases of the
        # st registers, so we use getRegisterIndex instead
        self.ROFFSETMMX   = self._dis_regctx.getRegisterIndex("mm0")

    # NOTE: Technically, the REX must be the *last* prefix specified
    # NOTE: Technically, the VEX must be the *last* prefix specified (REX be damned)

    def _dis_calc_tsize(self, opertype, prefixes, operflags):
        """
        Use the oper type and prefixes to decide on the tsize for
        the operand.
        """
        mode = MODE_32

        sizelist = opcode86.OPERSIZE.get(opertype, None)
        if sizelist is None:
            raise Exception("OPERSIZE FAIL")

        if operflags & opcode86.OP_64AUTO:
            mode = MODE_64

        # NOTE: REX takes precedence over 66
        # (see section 2.2.1.2 in Intel 2a)
        if prefixes & PREFIX_SIZE_BOTH:

            mode = MODE_64

        elif prefixes & e_i386.PREFIX_OP_SIZE:

            mode = MODE_16

        return sizelist[mode]

    def disasm(self, bytez, offset, va):
        '''
        The main amd64 decoder function. The inital steps it takes are determining what
        potential prefixes are attached to the instruction. By "potential", we mean that at
        this stage we don't know if thigs like 66, F2, F3 are being used as normal prefixes
        (representing things like a rep prefix) or if they're being used as mandatory prefixes
        that completely change with instruction we're decoding. All potential prefixes are stored
        in the pho_prefixes variable.

        To that end, there's some tap dancing we need to do to deal with what the intel manual
        refers to as "mandatory prefixes". If we hit a main opcode byte of 0F and we know we have a
        potentially mandatory prefix (and we're not in VEX land), we treat the byte right before the 0F
        as the only potential mandatory prefix (as laid out in the intel manual). Then we basically brute
        force the decoding since we really only have two paths to try. One where the mandatory prefix is
        merely a normal prefix (and doesn't affect which set of tables we traverse down) and one where
        the mandatory prefix does affect what tables we rachet through (and thus directly changes which
        instruction we're looking at). For each case, we append all the relevant output to a list (should
        the decoding produce a meaningful output).

        If we end up producing no instruction definitions from our brute force loop, we've hit an invalid
        sequence of instruction bytes and we throw an exception.

        If only one path produce output, then that's our results and we proceed on to use the instruction
        definition to determine what addressing methods and size types to use when determining operands.

        If both paths produce a valid instruction definition, then the path that uses the mandatory prefix
        to directly change the instruction takes precedence over the path where it's just a normal prefix.

        In both the one and two results case, outside of our instruction decoding loop, we've kept a list of
        the possible decodings we could have hit, and just merely pop off the end of the list (so order
        matters when building the ppref variable).
        '''
        # FIXME: for newer instructions, the VEX.W bit needs to be able to change the opcode. ugh.
        # FIXME: And also REX.W

        # Stuff for opcode parsing
        tabdesc = all_tables[opcode86.TBL_Main]  # A tuple (optable, shiftbits, mask byte, sub, max)
        startoff = offset  # Use startoff as a size knob if needed
        isvex = False
        vexw = None
        last_pref = 0
        ppref = [(None, None)]

        # Stuff we'll be putting in the opcode object
        optype = None  # This gets set if we successfully decode below
        mnem = None
        operands = []

        prefixes = 0
        pho_prefixes = 0  # faux prefixes...don't immediately apply them, they may not be the prefixes we're looking for

        while True:

            obyte = bytez[offset]

            # This line changes in 64 bit mode
            p = self._dis_prefixes[obyte]
            if p is None:
                break

            if MANDATORY_PREFIXES[obyte]:
                pho_prefixes |= p
                last_pref = obyte
            else:
                prefixes |= p

            if p & PREFIX_VEX:
                isvex = True
                if p == PREFIX_VEX2:
                    offset += 1
                    imm1 = bytez[offset]
                    # shouldn't in 64-bit mode, but in 32-bit, this keeps LES from colliding
                    # TODO: So we're always in 64 bit here. This will need to be here once we unify 32/64 decoding
                    #if imm1 & 0xc0 != 0xc0:
                        #break
                    inv1 = imm1 ^ 0xff

                    vex_l = (0, PREFIX_VEX_L)[(imm1 & 4) >> 2]
                    vvvv = ((inv1 >> 3) & 0xf)
                    pp = imm1 & 3

                    prefixes |= (inv1 << 11) & PREFIX_REX_R     # R is inverted
                    prefixes |= vex_l
                    prefixes |= (vvvv << VEX_V_SHIFT)
                    combined_mand_prefixes = vex_pp_table[pp]

                elif p == PREFIX_VEX3:
                    imm1 = bytez[offset+1]
                    offset += 2
                    # TODO: So we're always in 64 bit here. This will need to be here once we unify 32/64 decoding
                    #if imm1 & 0xc0 != 0xc0:
                        #break
                    imm2 = bytez[offset]
                    inv1 = imm1 ^ 0xff
                    inv2 = imm2 ^ 0xff

                    vex_l = (0, PREFIX_VEX_L)[(imm2 & 4) >> 2]
                    vvvv = ((inv2 >> 3) & 0xf)
                    pp = imm2 & 3
                    m_mmmm = imm1 & 0x1f
                    prefixes |= ((inv1 << 11) & PREFIX_REX_RXB)     # RXB are inverted
                    vexw = ((imm2 << 12) & PREFIX_REX_W)            # W is not inverted
                    prefixes |= vexw
                    prefixes |= vex_l
                    prefixes |= (vvvv << VEX_V_SHIFT)               # vvvv

                    combined_mand_prefixes = vex_pp_table[ pp ] + vex3_mmmm_table[m_mmmm]

                # VEX prefixes default to 0F table, possibly F20F, F30F or 660F
                # VEX3 prefixes may also specify depths into 38 and 3A tables
                for tabidx in combined_mand_prefixes:
                    if tabidx is None:
                        continue
                    opdesc = tabdesc[0][tabidx]
                    tabdesc = all_tables[opdesc[0]]
                # So VEX and mandatory prefixes don't really intermingle
                offset += 1
                break

            offset += 1
            continue

        if obyte != 0x0f:
            prefixes |= pho_prefixes

        # intel manual says VEX and legacy prefixes don't intermingle
        if obyte == 0x0f and MANDATORY_PREFIXES[last_pref] and not isvex:
            obyte = last_pref
            ppref.append((last_pref, amd64_prefixes[last_pref]))

        decodings = []
        mainbyte = offset
        all_prefixes = prefixes

        ogtabdesc = tabdesc
        # onehot in this case refers to the their prefixes that are defined in i386/disasm.py where only
        # on bit of the entire integer is set. We use that to quickly pop things in and out of the prefixes
        # list
        for pref, onehot in ppref:
            tabdesc = ogtabdesc
            offset = mainbyte
            if pref is not None:
                # our mandatory prefix is not none, which means that we have to jump through the tables
                # using the mandatory prefix byte as our "main byte"
                # As a bit of a hack, the 66/F2/F3 entries in the main table
                # directly point to the 660F/F20F/F30F tables since we're carefully tap dancing around
                # what our opcode byte really is
                obyte = pref
                # since we're treating this prefix as mandatory and not as REPNZ/REPZ/etc, we need to rip
                # it out of the pho_prefixes before we combine pho_prefixes with the main prefixes container
                all_prefixes = prefixes | (pho_prefixes & (~onehot))
            else:
                # treat nothing as a mandatory prefix (or we defaulted into here if we got no mandatory
                # prefixes). For most instructions this will be the normal case.
                obyte = bytez[offset]
                all_prefixes = prefixes | pho_prefixes

            while True:
                if (obyte > tabdesc[5]):
                    tabdesc = all_tables[tabdesc[6]]

                tabidx = ((obyte - tabdesc[4]) >> tabdesc[2]) & tabdesc[3]
                opdesc = tabdesc[0][tabidx]

                # Hunt down multi-byte opcodes
                nexttable = opdesc[0]
                if nexttable != 0:  # If we have a sub-table specified, use it.
                    tabdesc = all_tables[nexttable]

                    # Account for the table jump we made
                    offset += 1
                    obyte = bytez[offset]
                    continue

                # We are now on the final table...
                tbl_opercnt = tabdesc[1]
                mnem = opdesc[3 + tbl_opercnt]
                optype = opdesc[1]
                if tabdesc[3] == 0xff:
                    offset += 1  # For our final opcode byte
                break

            if optype & INS_VEXREQ and not isvex:
                continue

            if optype != 0:
                decodings.append((tabdesc, opdesc, offset, all_prefixes))

        if not len(decodings):
            raise envi.InvalidInstruction(bytez=bytez[startoff:startoff+16], va=va)

        tabdesc, opdesc, offset, prefixes = decodings.pop()
        optype = opdesc[1]
        tbl_opercnt = tabdesc[1]
        mnem = opdesc[3 + tbl_opercnt]

        if optype == 0:
            raise envi.InvalidInstruction(bytez=bytez[startoff:startoff+16], va=va)

        operoffset = 0
        # Begin parsing operands based off address method
        for i in range(operands_index, operands_index + tbl_opercnt):

            oper = None  # Set this if we end up with an operand
            osize = 0

            # Pull out the operand description from the table
            operflags = opdesc[i]
            opertype = operflags & opcode86.OPTYPE_MASK
            addrmeth = operflags & opcode86.ADDRMETH_MASK

            # If there are no more operands, break out of the loop!
            if operflags == 0:
                break

            # handles tsize calculations including new REX prefixes
            tsize = self._dis_calc_tsize(opertype, prefixes, operflags)
            # If addrmeth is zero, we have operands embedded in the opcode
            if addrmeth == 0:
                osize = 0
                oper = self.ameth_0(operflags, opdesc[2+tbl_opercnt+i], tsize, prefixes)

            else:
                # So the 0x7f is here to help us deal with an issue between VEX and non-VEX
                # A super common patter in vex is to add an operand somewhere in the middle of the
                # existing operands. So if we have like cmpps xmm2, 17 in non-VEX, the vex version
                # will look like vsprlw xmm3, xmm4, 17.
                # The fun bit of this is that the vex only portions aren't exclusive to the VEX-only
                # addressing methods, so we can have ADDRMETH_V be skipped outside of VEX mode too, and not
                # just things like ADDRMETH_H. Hence, we need a new flag that I stash in the upper bits of
                # instruction operand definition so we can know when to skip operands
                ameth = self._dis_amethods[(addrmeth >> 16) & 0x7F]
                vex_skip = addrmeth & opcode86.ADDRMETH_VEXSKIP
                if not isvex and vex_skip:
                    continue

                if ameth is None:
                    raise Exception("Implement Addressing Method 0x%.8x" % addrmeth)

                # NOTE: Depending on your addrmethod you may get beginning of operands, or offset
                try:
                    if addrmeth in IMM_REQOFFS:
                        osize, oper = ameth(bytez, offset+operoffset, tsize, prefixes, operflags)

                        # If we are a sign extended immediate and not the same as the other operand,
                        # do the sign extension during disassembly so nothing else has to worry about it..
                        if operflags & opcode86.OP_SIGNED:
                            if len(operands) and tsize != operands[-1].tsize:
                                otsize = operands[-1].tsize
                                oper.imm = e_bits.sign_extend(oper.imm, oper.tsize, otsize)
                                oper.tsize = otsize
                            elif not len(operands):
                                oper.imm = e_bits.sign_extend(oper.imm, oper.tsize, self._dis_default_size)
                                oper.tsize = self._dis_default_size

                    else:
                        # see same code section in i386 for this rationale
                        osize, oper = ameth(bytez, offset, tsize, prefixes, operflags)
                        if oper and oper.isDeref():
                            memsz = OP_EXTRA_MEMSIZES[(operflags & OP_MEMMASK) >> 4]
                            if memsz is not None:
                                oper.tsize = memsz
                            if prefixes & PREFIX_ADDR_SIZE:
                                if getattr(oper, 'reg', None) is not None:
                                    oper.reg |= RMETA_LOW32
                                elif getattr(oper, 'index', None) is not None:
                                    oper.index |= RMETA_LOW32

                except struct.error:
                    # Catch struct unpack errors due to insufficient data length
                    raise envi.InvalidInstruction(bytez=bytez[startoff:startoff+16])

            if oper is not None:
                # This is a filty hack for now...
                oper._dis_regctx = self._dis_regctx
                operands.append(oper)

            operoffset += osize

        typemask = optype & 0xFFFF
        # Pull in the envi generic instruction flags
        iflags = iflag_lookup.get(typemask, 0) | self._dis_oparch

        if prefixes & PREFIX_REP_MASK:
            iflags |= envi.IF_REPEAT

        if priv_lookup.get(mnem, False):
            iflags |= envi.IF_PRIV

        # Lea will have a reg-mem/sib operand with _is_deref True, but should be false
        if typemask == opcode86.INS_LEA:
            operands[1]._is_deref = False

        ret = Amd64Opcode(va, optype, mnem, prefixes, (offset-startoff)+operoffset, operands, iflags)
        return ret

    def parse_modrm(self, byte, prefixes=0):
        # Pass in a string with an offset for speed rather than a new string
        mod = (byte >> 6) & 0x3
        reg = (byte >> 3) & 0x7
        rm = byte & 0x7

        if prefixes & PREFIX_REX_R:
            reg |= 0b1000

        if prefixes & PREFIX_REX_B:
            if not (mod != 3 and rm == 4):  # if not SIB
                rm |= 0b1000

        return (mod,reg,rm)

    def byteRegOffset(self, val, prefixes=0):
        # NOTE: Override this because there is no AH etc in 64 bit mode
        if (prefixes & PREFIX_REX):     # the parse_modrm function deals with register index adds
            val |= e_i386.RMETA_LOW8

        else:  # not using REX, revert to old split-registers (low/high)
            if val < 4:
                val |= e_i386.RMETA_LOW8
            else:
                val |= e_i386.RMETA_HIGH8
                val -= 4

        return val

    def extended_parse_modrm(self, bytes, offset, opersize, regbase=0, prefixes=0):
        """
        Return a tuple of (size, Operand)
        """
        size = 1
        # FIXME this would be best to not parse_modrm twice.  tweak it.
        mod,reg,rm = self.parse_modrm(bytes[offset], prefixes)
        if mod == 0 and rm == 5:
            imm = e_bits.parsebytes(bytes, offset + size, 4, sign=True)
            size += 4
            return(size, Amd64RipRelOper(imm, opersize))

        return e_i386.i386Disasm.extended_parse_modrm(self, bytes, offset, opersize, regbase, prefixes)

    # NOTE: Override a bunch of the address modes to account for REX
    def ameth_0(self, operflags, operval, tsize, prefixes):
        # o = e_i386.i386Disasm.ameth_0(self, operflags, operval, tsize, prefixes)
        if operflags & opcode86.OP_REG:
            # for handling meta registers embedded in opcodes
            if prefixes & PREFIX_OP_SIZE:
                if self._dis_regctx.isMetaRegister(operval):
                    operval = (operval & RMETA_NMASK) | META_SIZES[tsize]
                else:
                    operval |= META_SIZES[tsize]
            width = self._dis_regctx.getRegisterWidth(operval) >> 3
            o = i386RegOper(operval, width)
        elif operflags & opcode86.OP_IMM:
            o = i386ImmOper(operval, tsize)
        else:
            raise Exception("Unknown ameth_0! operflags: 0x%.8x" % operflags)

        if not (operflags & OP_NOREX) and prefixes & PREFIX_REX_W and getattr(o, 'reg', None):
            o.reg &= 0xffff

        if prefixes & PREFIX_REX_B and isinstance(o, e_i386.i386RegOper):
            # the optable entries for AH with REX_B is terribly unhelpful.
            if o.reg & e_i386.RMETA_HIGH8 == e_i386.RMETA_HIGH8:
                o.reg &= REX_HIGH_DROP
                o.reg += 4
            if not (operflags & OP_NOREX):
                o.reg += REX_BUMP
        return o

    def ameth_vexh(self, bytes, offset, tsize, prefixes, operflags):
        '''
        So this is here because instructions like movss and movsd are ambiguous in their
        2/3 operand state without first jumping ahead to the modrm byte. If modrm refers to
        memory, we skip this state and just go on to the next addressing method. If it refers
        to a register, pass through to self.ameth_h
        '''
        mod, reg, rm = self.parse_modrm(bytes[offset], prefixes)
        if mod == 3:
            return self.ameth_h(bytes, offset, tsize, prefixes, operflags)
        else:
            return (0, None)

    def ameth_l(self, bytez, offset, tsize, prefixes, operflags):
        reg = self.ROFFSETSIMD
        imm = e_bits.parsebytes(bytez, offset, 1, sign=False)
        idx = (imm & 0xF0) >> 4
        if not (prefixes & PREFIX_VEX_L) or operflags & OP_NOVEXL:
            reg += e_i386.RMETA_LOW128
        return (1, i386RegOper(reg + idx, tsize))

    def ameth_g(self, bytes, offset, tsize, prefixes, operflags):
        osize, oper = e_i386.i386Disasm.ameth_g(self, bytes, offset, tsize, prefixes, operflags)
        # TODO: Disallowing reg_rip is probably wrong
        # TODO: the addr override operates off the default of the instruction, so we need to grab that
        if oper.tsize == 4:
            oper.reg |= RMETA_LOW32
        if prefixes & PREFIX_REX_R:
            oper.reg += REX_BUMP
        return osize, oper

    def ameth_b(self, bytez, offset, tsize, prefixes, operflags):
        osize = 0
        oper = 0
        vvvv = (prefixes >> VEX_V_SHIFT) & 0xf
        oper = i386RegOper(vvvv, tsize)
        # TODO: Disallowing reg_rip is probably wrong
        if oper.tsize == 4:
            oper.reg |= RMETA_LOW32
        return osize, oper

    def ameth_h(self, bytez, offset, tsize, prefixes, operflags):
        osize = 0
        vvvv = (prefixes >> VEX_V_SHIFT) & 0xf
        offset = self.ROFFSETSIMD
        if not (prefixes & PREFIX_VEX_L) or operflags & OP_NOVEXL:
            vvvv |= e_i386.RMETA_LOW128

        oper = i386RegOper(offset + vvvv, tsize)
        return osize, oper

    def ameth_c(self, bytes, offset, tsize, prefixes, operflags):
        osize, oper = e_i386.i386Disasm.ameth_c(self, bytes, offset, tsize, prefixes, operflags)
        if prefixes & PREFIX_REX_R:
            oper.reg += REX_BUMP
        return osize, oper

    def ameth_d(self, bytes, offset, tsize, prefixes, operflags):
        osize, oper = e_i386.i386Disasm.ameth_d(self, bytes, offset, tsize, prefixes, operflags)
        if prefixes & PREFIX_REX_R:
            oper.reg += REX_BUMP
        return osize, oper

    def ameth_v(self, bytes, offset, tsize, prefixes, operflags):
        osize, oper = e_i386.i386Disasm.ameth_v(self, bytes, offset, tsize, prefixes, operflags)

        # FIXME: YMM->XMM (this may move into i386 version when VEX is made available there)
        if not (prefixes & PREFIX_VEX_L) or operflags & OP_NOVEXL:
            oper.reg += e_i386.RMETA_LOW128

        if prefixes & PREFIX_REX_R:
            oper.reg += REX_BUMP
        return osize, oper

    def ameth_u(self, bytes, offset, tsize, prefixes, operflags):
        osize, oper = e_i386.i386Disasm.ameth_u(self, bytes, offset, tsize, prefixes, operflags)

        if not (prefixes & PREFIX_VEX_L) or operflags & OP_NOVEXL:
            oper.reg += e_i386.RMETA_LOW128

        if prefixes & PREFIX_REX_B:
            oper.reg += REX_BUMP

        return osize, oper

    # NOTE: The ones below are the only ones to which REX.X or REX.B can apply (besides ameth_0)
    # FIXME: we need to adhere to the ADDR_SIZE/OPER_SIZE rules better...  the REX_BUMP is an afterthought...
    # however, all the rules are based on ADDR_SIZE/OPER_SIZE and can be coalesced elegantly into amd64/i386
    # and even make 16-bit mode play nicely.
    # FIXME: processing of REX into actual operand size/indexes should be done *pre* operand-parsing
    # if for no other reason, because that's how the manuals discuss it.
    # NO REALLY ! FIXME!
    def _dis_rex_exmodrm(self, oper, prefixes, operflags):
        # REMEMBER: all extended mod RM reg fields come from the r/m part.  If it
        #           were actually just the reg part, it'd be in one of the above
        #           addressing modes...

        if hasattr(oper, "index"):
            # Adjust the size if needed
            if prefixes & PREFIX_REX_X:
                # fix up index in case it was set to None by sib_parse (index==4 without REX)
                if oper.index is None:
                    oper.index = 4
                oper.index += REX_BUMP

        # oper.reg will be r/m or SIB base
        if getattr(oper, "reg", None) is not None:
            # Adjust the size if needed
            if prefixes & PREFIX_REX_B:
                oper.reg += REX_BUMP

        if isinstance(oper, e_i386.i386RegOper):
            if oper.tsize == 4:
                oper.reg |= RMETA_LOW32

    def ameth_e(self, bytes, offset, tsize, prefixes, operflags):
        regbase = 0
        # TODO: Does this impact memory as well?
        osize, oper = self.extended_parse_modrm(bytes, offset, tsize, prefixes=prefixes, regbase=regbase)
        self._dis_rex_exmodrm(oper, prefixes, operflags)
        return osize, oper

    def ameth_w(self, bytez, offset, tsize, prefixes, operflags):
        mod, reg, rm = self.parse_modrm(bytez[offset])
        if mod == 3:
            vvvv = self.ROFFSETSIMD
            if not (prefixes & PREFIX_VEX_L) or operflags & OP_NOVEXL:
                vvvv |= e_i386.RMETA_LOW128
                tsize = 16

            osize, oper = (1, i386RegOper(rm + vvvv, tsize))
        else:
            osize, oper = self.extended_parse_modrm(bytez, offset, tsize, prefixes=prefixes)
            if (oper.tsize == 32 and not (prefixes & PREFIX_VEX_L)) or operflags & OP_NOVEXL:
                oper.tsize = 16

        self._dis_rex_exmodrm(oper, prefixes, operflags)
        return osize, oper


if __name__ == '__main__':
    import envi.archs
    envi.archs.dismain(Amd64Disasm())
