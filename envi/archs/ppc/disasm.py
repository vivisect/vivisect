import envi
import envi.bits as e_bits

import struct

from .ppc_tables import *
from .regs import *
from .const import *
from .disasm_classes import *

class PpcDisasm:
    __ARCH__ = None # abstract class.  subclasses should define this
    def __init__(self, endian=ENDIAN_MSB, options=CAT_PPC_EMBEDDED, psize=8):
        self.psize = psize

        ### TODO: options gets lost in Vivisect.  it must be part of the event stream to get saved.
        ###   this is only worthwhile for canned options which are otherwise persistent or for
        ###   incidental hacking use.  perhaps we need arch config entries in the config file which
        ###   are passed into the different architectures.
        ### currently we rely on 5 specific option groupings, each of which are their own "architecture": see bottom

        # any speedy stuff here
        self._instr_dict = None
        self._dis_regctx = Ppc64RegisterContext()
        self.setEndian(endian)
        self.setCategories(options)

    def setCategories(self, options):
        if options == 0:
            options = CAT_NONE
        self.options = options

        # The lookup for decoding instructions
        self._instr_dict = {}

        # populate and trim unnecessary instructions (based on categories)
        for key, group in instr_dict.items():
            mygroup = []
            for ocode in group:
                mask, value, data = ocode
                if not (data[3] & self.options):
                    continue

                mygroup.append(ocode)

            mygroup = tuple(mygroup)    # for speed
            self._instr_dict[key] = mygroup

    def setEndian(self, endian):
        self.endian = endian
        self.fmt = ('<I', '>I')[endian]

    def disasm(self, bytez, offset, va):
        """
        Parse a sequence of bytes out into an envi.Opcode instance.
        This is the BOOK E PPC Disassembly routine.  Look in vle module for VLE instruction decoding
        """
        # Stuff we'll be putting in the opcode object
        optype = None # This gets set if we successfully decode below
        mnem = None
        operands = []
        prefixes = 0
        iflags = 0

        ival, = struct.unpack_from(self.fmt, bytez, offset)
        #print(hex(ival))

        key = ival >> 26
        #print(hex(key))

        #print(group)
        group = self._instr_dict.get(key)
        if not group:
            raise envi.InvalidInstruction(bytez[offset:offset+4], 'No Instruction Group Found: %x' % key, va)

        try:
            data = next(d for m, v, d in group if ival & m == v)
        except:
            raise envi.InvalidInstruction(bytez[offset:offset+4], 'No Instruction Matched in Group: %x' % key, va)

        mnem, opcode, form, cat, operands, iflags = data

        decoder = decoders.get(form, form_DFLT)

        nopcode, opers, iflags = decoder(self, va, ival, opcode, operands, iflags)
        if nopcode != None:
            opcode = nopcode

        mnem, opcode, opers, iflags = self.simplifiedMnems(ival, mnem, opcode, opers, iflags)
        iflags |= self.__ARCH__

        return PpcOpcode(va, opcode, mnem, size=4, operands=opers, iflags=iflags)

    def simplifiedMnems(self, ival, mnem, opcode, opers, iflags):
        if opcode in SIMPLIFIEDS.keys():
            return SIMPLIFIEDS[opcode](ival, mnem, opcode, opers, iflags)

        return mnem, opcode, opers, iflags

# TODO simpleMnems:
# rlwinm -> clrlwi

cmp_mnems = ('cmpw','cmpd')
cmp_opcodes = (INS_CMPW, INS_CMPD)
def simpleCMP(ival, mnem, opcode, opers, iflags):
    # The 'L' operand (second operand) indicates if this is a word or
    # double-word comparison
    mnem = cmp_mnems[opers[1].val]
    opcode = cmp_opcodes[opers[1].val]

    # if using CR0, it can be omitted
    if opers[0].field == 0:
        # drop the first two operands
        opers = opers[2:]
    else:
        # drop the second operand
        opers.pop(1)

    return mnem, opcode, opers, iflags

cmpi_mnems = ('cmpwi','cmpdi')
cmpi_opcodes = (INS_CMPWI, INS_CMPDI)
def simpleCMPI(ival, mnem, opcode, opers, iflags):
    # The 'L' operand (second operand) indicates if this is a word or
    # double-word comparison
    mnem = cmpi_mnems[opers[1].val]
    opcode = cmpi_opcodes[opers[1].val]

    # if using CR0, it can be omitted
    if opers[0].field == 0:
        # drop the first two operands
        opers = opers[2:]
    else:
        # drop the second operand
        opers.pop(1)

    return mnem, opcode, opers, iflags

cmpli_mnems = ('cmplwi','cmpldi')
cmpli_opcodes = (INS_CMPLWI, INS_CMPLDI)
def simpleCMPLI(ival, mnem, opcode, opers, iflags):
    # The 'L' operand (second operand) indicates if this is a word or
    # double-word comparison
    mnem = cmpli_mnems[opers[1].val]
    opcode = cmpli_opcodes[opers[1].val]

    # if using CR0, it can be omitted
    if opers[0].field == 0:
        # drop the first two operands
        opers = opers[2:]
    else:
        # drop the second operand
        opers.pop(1)

    return mnem, opcode, opers, iflags

cmpl_mnems = ('cmplw','cmpld')
cmpl_opcodes = (INS_CMPLW, INS_CMPLD)
def simpleCMPL(ival, mnem, opcode, opers, iflags):
    # The 'L' operand (second operand) indicates if this is a word or
    # double-word comparison
    mnem = cmpl_mnems[opers[1].val]
    opcode = cmpl_opcodes[opers[1].val]

    # if using CR0, it can be omitted
    if opers[0].field == 0:
        # drop the first two operands
        opers = opers[2:]
    else:
        # drop the second operand
        opers.pop(1)

    return mnem, opcode, opers, iflags

mr_mnems = ('mr', 'mr.')
def simpleOR(ival, mnem, opcode, opers, iflags):
    if opers[1] == opers[2]:
        mnem = mr_mnems[bool(iflags & IF_RC)]
        return mnem, INS_MR, (opers[0], opers[2]), iflags
    return mnem, opcode, opers, iflags

def simpleORI(ival, mnem, opcode, opers, iflags):
    if ival == 0x60000000:
        return 'nop', INS_NOP, tuple(), iflags

    if opers[2].val == 0:
        mnem = mr_mnems[bool(iflags & IF_RC)]
        return mnem, INS_MR, opers[:2], iflags

    return mnem, opcode, opers, iflags

def simpleADDI(ival, mnem, opcode, opers, iflags):
    if ival & 0xfc1f0000 == 0x38000000:
        return 'li', INS_LI, (opers[0], opers[2]), iflags

    return mnem, opcode, opers, iflags

def simpleADDIS(ival, mnem, opcode, opers, iflags):
    if ival & 0xfc1f0000 == 0x3c000000:
        return 'lis', INS_LIS, (opers[0], opers[2]), iflags

    return mnem, opcode, opers, iflags

def simpleNOR(ival, mnem, opcode, opers, iflags):
    if opers[1] == opers[2]:
        return 'not', INS_NOT, (opers[0], opers[2]), iflags
    return mnem, opcode, opers, iflags

def simpleMTCRF(ival, mnem, opcode, opers, iflags):
    #if opers[0].val == 0xff:
    #    return 'mtcr', INS_MTCR, (opers[1],), iflags
    return mnem, opcode, opers, iflags

def simpleSYNC(ival, mnem, opcode, opers, iflags):
    if opers[1].val == 0:
        oper0 = opers[0].val
        if oper0 == 0:
            # This could also be represented as `sync` with no parameters, the
            # EREF suggests this form is allowed to maintain compatibility with
            # the PowerISA.
            return 'msync', INS_MSYNC, (), iflags

        if oper0 == 1:
            return 'lwsync', INS_LWSYNC, (), iflags

    return mnem, opcode, opers, iflags

def simpleISEL(ival, mnem, opcode, opers, iflags):
    if opers[-1].bit == 0:
        return 'isellt', INS_ISELLT, (opers[0], opers[1], opers[2]), iflags
    if opers[-1].bit == 1:
        return 'iselgt', INS_ISELGT, (opers[0], opers[1], opers[2]), iflags
    if opers[-1].bit == 2:
        return 'iseleq', INS_ISELEQ, (opers[0], opers[1], opers[2]), iflags
    return mnem, opcode, opers, iflags

def simpleVOR(ival, mnem, opcode, opers, iflags):
    if opers[1] == opers[2]:
        opers.pop()
        return 'vmr', INS_VMR, opers, iflags
    return mnem, opcode, opers, iflags

trap_conds = {
        0x01 : 'lgt',
        0x02 : 'llt',
        0x03 : 'lne',
        0x05 : 'lge',  # also 'lnl'
        0x06 : 'lle',  # also 'lng'

        0x04 : 'eq',

        0x08 : 'gt',
        0x0c : 'ge',   # also 'nl'
        0x10 : 'lt',
        0x14 : 'le',   # also 'ng'
        0x18 : 'ne',
        0x1f : 'u',    # in PowerISA but not in NXP EREF
    }

td_mnems = { k : 'td%s' % v for k,v in trap_conds.items() }
tdi_mnems = { k : 'td%si' % v for k,v in trap_conds.items() }
tw_mnems = { k : 'tw%s' % v for k,v in trap_conds.items() }
twi_mnems = { k : 'tw%si' % v for k,v in trap_conds.items() }
tw_mnems[0x1f] = 'trap'

def simpleTD(ival, mnem, opcode, opers, iflags):
    cond = opers[0].val
    nmnem = td_mnems.get(cond)
    if nmnem is not None:
        if opers[1] == opers[2]:
            return 'trap', opcode, (), iflags
        opers = opers[1:3]
        return nmnem, opcode, opers, iflags

    return mnem, opcode, opers, iflags

def simpleTDI(ival, mnem, opcode, opers, iflags):
    cond = opers[0].val
    nmnem = tdi_mnems.get(cond)
    if nmnem is not None:
        if opers[1] == opers[2]:
            return 'trap', opcode, (), iflags
        opers = opers[1:3]
        return nmnem, opcode, opers, iflags

    return mnem, opcode, opers, iflags

def simpleTW(ival, mnem, opcode, opers, iflags):
    cond = opers[0].val
    nmnem = tw_mnems.get(cond)
    if nmnem is not None:
        if opers[1] == opers[2]:
            return 'trap', opcode, (), iflags
        opers = opers[1:3]
        return nmnem, opcode, opers, iflags

    return mnem, opcode, opers, iflags

def simpleTWI(ival, mnem, opcode, opers, iflags):
    cond = opers[0].val
    nmnem = twi_mnems.get(cond)
    if nmnem is not None:
        if opers[1] == opers[2]:
            return 'trap', opcode, (), iflags
        opers = opers[1:3]
        return nmnem, opcode, opers, iflags

    return mnem, opcode, opers, iflags

def simpleCREQV(ival, mnem, opcode, opers, iflags):
    if opers[0] == opers[1] == opers[2]:
        opers = (opers[0],)
        return 'crset', opcode, opers, iflags
    return mnem, opcode, opers, iflags

def simpleCRXOR(ival, mnem, opcode, opers, iflags):
    if opers[0] == opers[1] == opers[2]:
        opers = (opers[0],)
        return 'crclr', opcode, opers, iflags
    return mnem, opcode, opers, iflags

def simpleCROR(ival, mnem, opcode, opers, iflags):
    if opers[1] == opers[2]:
        return 'crmove', opcode, opers[:2], iflags
    return mnem, opcode, opers, iflags

def simpleCRNOR(ival, mnem, opcode, opers, iflags):
    if opers[1] == opers[2]:
        return 'crnot', opcode, opers[:2], iflags
    return mnem, opcode, opers, iflags


from .regs import sprnames
def _no_simpleMTSPR(ival, mnem, opcode, opers, iflags):
    spridx = opers[0].val
    spr = sprnames.get(spridx)
    return 'mt' + spr, opcode, opers[1:], iflags

def _no_simpleMFSPR(ival, mnem, opcode, opers, iflags):
    spridx = opers[1].val
    spr = sprnames.get(spridx)
    return 'mf' + spr, opcode, opers[:-1], iflags

# this generates the handler table for any function starting with simple*
SIMPLIFIEDS = {}
for k, v in list(globals().items()):
    if k.startswith('simple'):
        capmnem = k[6:]
        SIMPLIFIEDS[eval('INS_' + capmnem)] = v


# FORM parsers
def form_DFLT(disasm, va, ival, opcode, operands, iflags):
    opers = []
    opcode = None

    for onm, otype, oshr, omask in operands:
        val = (ival >> oshr) & omask
        oper = OPERCLASSES[otype](val, va)
        opers.append(oper)

    return opcode, opers, iflags

def form_A(disasm, va, ival, opcode, operands, iflags):
    opcode = None
    # fallback for all non-memory-accessing FORM_X opcodes
    opers = []
    for onm, otype, oshr, omask in operands:
        val = (ival >> oshr) & omask
        opers.append(OPERCLASSES[otype](val, va))

    if iflags & IF_MEM_EA:
        opvals = [((ival >> oshr) & omask) for onm, otype, oshr, omask in operands]
        # FORM_X opcodes that access memory (EA calculation) with rA==0 use the number 0
        if opvals[1] == 0:
            opers[1] = PpcImmOper(0, va)

    return opcode, opers, iflags

def form_X(disasm, va, ival, opcode, operands, iflags):
    opcode = None
    # fallback for all non-memory-accessing FORM_X opcodes
    opers = []
    rAidx = None
    for idx, (onm, otype, oshr, omask) in enumerate(operands):
        val = (ival >> oshr) & omask
        oper = OPERCLASSES[otype](val, va)
        opers.append(oper)
        if otype == FIELD_rA:
            rAidx = idx

    if iflags & IF_MEM_EA and rAidx is not None:
        opvals = [((ival >> oshr) & omask) for onm, otype, oshr, omask in operands]
        # FORM_X opcodes that access memory (EA calculation) with rA==0 use the number 0
        if opvals[rAidx] == 0:
            opers[rAidx] = PpcImmOper(0, va)

    return opcode, opers, iflags


def form_XL(disasm, va, ival, opcode, operands, iflags):
    opers = []
    opcode = None

    for onm, otype, oshr, omask in operands:
        val = (ival >> oshr) & omask
        if otype == FIELD_crBI:
            # Only add this operand if it has a non-zero value
            if val != 0:
                opers.append(OPERCLASSES[otype](val, va))
        else:
            opers.append(OPERCLASSES[otype](val, va))

    return opcode, opers, iflags

def form_EVX(disasm, va, ival, opcode, operands, iflags):
    opers = []
    opcode = None

    # if the last operand is UIMM[123], it's a memory deref.
    if len(operands) == 3 and operands[2][1] in (FIELD_UIMM1, FIELD_UIMM2, FIELD_UIMM3):
        opvals = [((ival >> oshr) & omask) for onm, otype, oshr, omask in operands]
        oper0 = OPERCLASSES[operands[0][1]](opvals[0], va)
        opers.append(oper0)

        oper1 = PpcMemOper(opvals[1], opvals[2], va)
        opers.append(oper1)
        return opcode, opers, iflags

    for onm, otype, oshr, omask in operands:
        val = (ival >> oshr) & omask
        oper = OPERCLASSES[otype](val, va)
        # FIXME: FORM_X seems to use Signed IMM's
        opers.append(oper)

    return opcode, opers, iflags


tsizes_formD = {
        INS_LWZ: 4,
        INS_LWZU: 4,
        INS_LBZ: 1,
        INS_LBZU: 1,
        INS_STW: 4,
        INS_STWU: 4,
        INS_STB: 1,
        INS_STBU: 1,
        INS_LHZ: 2,
        INS_LHZU: 2,
        INS_LHA: 2,
        INS_LHAU: 2,
        INS_STH: 2,
        INS_STHU: 2,
        INS_LMW: 4,
        INS_STMW: 4,
        INS_LFS: 4,
        INS_LFSU: 4,
        INS_LFD: 8,
        INS_LFDU: 8,
        INS_STFS: 4,
        INS_STFSU: 4,
        INS_STFD: 8,
        INS_STFDU: 8,
}

def form_D(disasm, va, ival, opcode, operands, iflags):
    opers = []

    opvals = [((ival >> oshr) & omask) for onm, otype, oshr, omask in operands]
    # if the last operand is FIELD_D, it's a memory deref. (load/store instructions)
    if len(operands) == 3 and operands[2][1] == FIELD_D:
        # let's figure out what *memory size* the operand uses
        tsize = tsizes_formD.get(opcode)
        #print("DBG: 0x%x:   FORM_D: opcode: 0x%x    tsize=%r" % (va, opcode, tsize))
        oper0 = OPERCLASSES[operands[0][1]](opvals[0], va)

        if opvals[1] == 0:
            oper1 = PpcImmOper(0, va)
            oper2 = OPERCLASSES[operands[2][1]](opvals[2], va, tsize=tsize)
            opers = (oper0, oper1, oper2)
            return opcode, opers, iflags

        oper1 = PpcMemOper(opvals[1], opvals[2], va, tsize=tsize)
        opers =(oper0, oper1)
        return opcode, opers, iflags

    # check for rA being 0... and convert it to Immediate 0     TESTME: does this correctly slice the instruction set?
    elif iflags & IF_MEM_EA and len(operands) == 3 and operands[1][1] == FIELD_rA and opvals[1] == 0:
        print("form_D: secondary IF_MEM_EA...", hex(ival), operands, iflags)
        oper0 = OPERCLASSES[operands[0][1]](opvals[0], va)
        oper1 = PpcImmOper(0, va)
        oper2 = OPERCLASSES[operands[2][1]](opvals[2], va)
        opers = (oper0, oper1, oper2)
        return opcode, opers, iflags

    oidx = 0
    for onm, otype, oshr, omask in operands:
        val = opvals[oidx]
        oper = OPERCLASSES[otype](val, va)
        opers.append(oper)
        oidx += 1

    return opcode, opers, iflags

def form_B(disasm, va, ival, opcode, operands, iflags):
    opers = []
    opcode = None

    # FORM_B instructions (branch and branch conditional variants) can
    # have 2 or 3 operands, the last operand is 'BD' (the target address), the
    # second to last value is the 'BI' or 'crBI' operand.  'BI' operands must be
    # left alone but if 'crBI' operands are 0 then the "cr0" value can be
    # removed from the operand list because "cr0" is the default condition
    # register and the PPC simplified mnemonics leave cr0 off.

    for onm, otype, oshr, omask in operands:
        opval = (ival >> oshr) & omask
        if otype == FIELD_BD:
            offset = e_bits.bsigned(opval << 2, 16)
            if iflags & IF_ABS:
                addr = e_bits.unsigned(offset, disasm.psize)
                tgtoper = PpcJmpAbsOper(addr)
            else:
                tgtoper = PpcJmpRelOper(offset, va)
            opers.append(tgtoper)
        elif otype == FIELD_crBI:
            # Only add this operand if it has a non-zero value
            if opval != 0:
                opers.append(OPERCLASSES[otype](opval, va))
        else:
            opers.append(OPERCLASSES[otype](opval, va))

    return opcode, opers, iflags

def form_I(disasm, va, ival, opcode, operands, iflags):
    opers = []
    opcode = None

    opvals = [((ival >> oshr) & omask) for onm, otype, oshr, omask in operands]

    offset = e_bits.bsigned(opvals[0] << 2, 26)
    if iflags & IF_ABS:
        addr = e_bits.unsigned(offset, disasm.psize)
        tgtoper = PpcJmpAbsOper(addr)
    else:
        tgtoper = PpcJmpRelOper(offset, va)
    opers.append(tgtoper)

    return opcode, opers, iflags

def form_DS(disasm, va, ival, opcode, operands, iflags):
    opcode = None

    opvals = [((ival >> oshr) & omask) for onm, otype, oshr, omask in operands]
    oper0 = OPERCLASSES[operands[0][1]](opvals[0], va)
    oper1 = PpcMemOper(opvals[1], opvals[2] * 4, va)
    opers = (oper0, oper1)
    return opcode, opers, iflags

def form_MDS(disasm, va, ival, opcode, operands, iflags):
    opers = []
    opcode = None

    opvals = [((ival >> oshr) & omask) for onm, otype, oshr, omask in operands]
    oper0 = OPERCLASSES[operands[0][1]](opvals[0], va)
    oper1 = OPERCLASSES[operands[1][1]](opvals[1], va)
    oper2 = OPERCLASSES[operands[2][1]](opvals[2], va)

    val = (opvals[4] << 5) | opvals[3]
    oper3 = PpcImmOper(val, va)

    opers = (oper0, oper1, oper2, oper3)
    return opcode, opers, iflags

def form_MD(disasm, va, ival, opcode, operands, iflags):
    opers = []
    opcode = None

    opvals = [((ival >> oshr) & omask) for onm, otype, oshr, omask in operands]
    oper0 = OPERCLASSES[operands[0][1]](opvals[0], va)
    oper1 = OPERCLASSES[operands[1][1]](opvals[1], va)

    val = (opvals[5] << 5) | opvals[2]
    oper2 = PpcImmOper(val, va)
    val = (opvals[4] << 5) | opvals[3]
    oper3 = PpcImmOper(val, va)

    opers = (oper0, oper1, oper2, oper3)
    return opcode, opers, iflags

def form_XS(disasm, va, ival, opcode, operands, iflags):
    opers = []
    opcode = None

    opvals = [((ival >> oshr) & omask) for onm, otype, oshr, omask in operands]
    oper0 = OPERCLASSES[operands[0][1]](opvals[0], va)
    oper1 = OPERCLASSES[operands[1][1]](opvals[1], va)
    val = (opvals[3] << 5) | opvals[2]
    oper2 = PpcImmOper(val, va)

    opers = (oper0, oper1, oper2)
    return opcode, opers, iflags


REG_OFFS = {
        FIELD_DCRN0_4 : REG_OFFSET_DCR,
        FIELD_PMRN0_4 : REG_OFFSET_PMR,
        FIELD_SPRN0_4 : REG_OFFSET_SPR,
        FIELD_TMRN0_4 : REG_OFFSET_TMR,
        FIELD_TBRN0_4 : REG_OFFSET_TBR,
        }

def form_XFX(disasm, va, ival, opcode, operands, iflags):
    opers = []
    opcode = None

    operlen = len(operands)
    if operlen == 3 and operands[2][1] in (FIELD_DCRN0_4, FIELD_PMRN0_4, FIELD_SPRN0_4, FIELD_TMRN0_4, FIELD_TBRN0_4,):
        opvals = [((ival >> oshr) & omask) for onm, otype, oshr, omask in operands]

        if operands[1][1] in (FIELD_DCRN5_9, FIELD_PMRN5_9, FIELD_SPRN5_9, FIELD_TMRN5_9, FIELD_TBRN5_9,):
            val = (opvals[2] << 5) | opvals[1]
            oper0 = OPERCLASSES[operands[0][1]](opvals[0], va)
            regoff = REG_OFFS.get(operands[2][1])
            oper1 = PpcRegOper(regoff + val, va)

        else:
            val = (opvals[2] << 5) | opvals[0]
            regoff = REG_OFFS.get(operands[2][1])
            oper0 = PpcRegOper(regoff + val, va)    # FIXME: do we want specific DCRN, PMRN, SPRN, TMRN, TBRN operand types?
            oper1 = OPERCLASSES[operands[1][1]](opvals[1], va)

        opers = (oper0, oper1)
        return opcode, opers, iflags

    elif operlen == 4 and operands[0][1] == FIELD_L:
        # mtfsf special case ordering
        operands = (operands[1], operands[3], operands[0], operands[2])

    for onm, otype, oshr, omask in operands:
        val = (ival >> oshr) & omask
        oper = OPERCLASSES[otype](val, va)
        opers.append(oper)

    return opcode, opers, iflags

decoders = { eval(x) : form_DFLT for x in globals().keys() if x.startswith('FORM_') }
decoders[FORM_A] = form_A
decoders[FORM_X] = form_X
decoders[FORM_EVX] = form_EVX
decoders[FORM_D] = form_D
decoders[FORM_B] = form_B
decoders[FORM_I] = form_I
decoders[FORM_DS] = form_DS
decoders[FORM_XFX] = form_XFX
decoders[FORM_MDS] = form_MDS
decoders[FORM_MD] = form_MD
decoders[FORM_XS] = form_XS
decoders[FORM_XL] = form_XL


def genTests(abytez):
    import subprocess
    from subprocess import PIPE

    open('/tmp/ppcbytez', 'wb').write(''.join(abytez))
    proc = subprocess.Popen(['/usr/bin/powerpc-linux-gnu-objdump', '-D','/tmp/ppcbytez', '-b', 'binary', '-m', 'powerpc:e5500'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    data = proc.stdout.readlines()
    data = [x.strip() for x in data]
    data = [x.split('\t') for x in data]

    for parts in data:
        if len(parts) < 4:
            print(parts)
            continue
        ova, bytez, op, opers = parts[:4]
        ova = ova[:-1]
        bytez = bytez[6:8] + bytez[4:6] + bytez[2:4] + bytez[:2]
        yield ("        ('%s', 0x%s, '%s %s', 0, ())," % (bytez, ova, op, opers))

class Ppc64EmbeddedDisasm(PpcDisasm):
    __ARCH__ = envi.ARCH_PPC_E64
    def __init__(self, endian=ENDIAN_MSB, options=CAT_PPC_EMBEDDED, psize=8):
        PpcDisasm.__init__(self, endian, options, psize=psize)

class Ppc32EmbeddedDisasm(PpcDisasm):
    __ARCH__ = envi.ARCH_PPC_E32
    def __init__(self, endian=ENDIAN_MSB, options=CAT_PPC_EMBEDDED, psize=4):
        PpcDisasm.__init__(self, endian, options, psize=psize)

class Ppc64ServerDisasm(PpcDisasm):
    __ARCH__ = envi.ARCH_PPC_S64
    def __init__(self, endian=ENDIAN_MSB, options=CAT_PPC_SERVER, psize=8):
        PpcDisasm.__init__(self, endian, options, psize=psize)

class Ppc32ServerDisasm(PpcDisasm):
    __ARCH__ = envi.ARCH_PPC_S32
    def __init__(self, endian=ENDIAN_MSB, options=CAT_PPC_SERVER, psize=4):
        PpcDisasm.__init__(self, endian, options, psize=psize)
