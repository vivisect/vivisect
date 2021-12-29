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
        for key in instr_dict:
            self._instr_dict[key] = {}
            for i in range(len(instr_dict[key])):
                cat = instr_dict[key][i][2][3]
                if cat & self.options == 0:
                    continue

                mask = instr_dict[key][i][0]
                val = instr_dict[key][i][1]

                if mask not in self._instr_dict[key]:
                    self._instr_dict[key][mask] = {}

                if val in self._instr_dict[key][mask]:
                    entry = self._instr_dict[key][mask][val]
                    errmsg = 'Duplicate instruction decoding %#x, %#x: prev = %s, new = %s' % (mask, val, entry[0], data[0])
                    raise Exception(errmsg)
                else:
                    self._instr_dict[key][mask][val] = instr_dict[key][i][2]

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

        # Ensure that the target address is 4-byte aligned
        if offset & 0x3:
            raise envi.InvalidAddress(offset)

        ival, = struct.unpack_from(self.fmt, bytez, offset)
        #print(hex(ival))

        key = ival >> 26
        #print(hex(key))

        group = self._instr_dict.get(key)
        if not group:
            raise envi.InvalidInstruction(bytez[offset:offset+4], 'No Instruction Group Found: %x' % key, va)

        for mask in group:
            masked_ival = ival & mask
            try:
                data = group[mask][masked_ival]
                break
            except KeyError:
                pass
        else:
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

def getTrapOpcode(mnem):
    try:
        return globals()['INS_%s' % mnem.upper()]
    except KeyError:
        # INS_TWU doesn't exist but will get replaced another way
        return None

td_mnems  = {k : ('td%s' % v,  getTrapOpcode('td%s' % v))  for k,v in trap_conds.items()}
tdi_mnems = {k : ('td%si' % v, getTrapOpcode('td%si' % v)) for k,v in trap_conds.items()}
tw_mnems  = {k : ('tw%s' % v,  getTrapOpcode('tw%s' % v))  for k,v in trap_conds.items()}
tw_mnems[0x1f] = ('trap', INS_TRAP)
twi_mnems = {k : ('tw%si' % v, getTrapOpcode('tw%si' % v)) for k,v in trap_conds.items()}

def simpleTD(ival, mnem, opcode, opers, iflags):
    cond = opers[0].val
    opinfo = td_mnems.get(cond)
    if opinfo:
        nmnem, nopcode = opinfo
        if nopcode == INS_TRAP:
            # No operands for a 'trap' instruction
            return nmnem, nopcode, (), iflags
        else:
            # remove the condition (first) operand
            return nmnem, nopcode, opers[1:], iflags

    return mnem, opcode, opers, iflags

def simpleTDI(ival, mnem, opcode, opers, iflags):
    cond = opers[0].val
    opinfo = tdi_mnems.get(cond)
    if opinfo:
        nmnem, nopcode = opinfo
        if nopcode == INS_TRAP:
            # No operands for a 'trap' instruction
            return nmnem, nopcode, (), iflags
        else:
            # remove the condition (first) operand
            return nmnem, nopcode, opers[1:], iflags

    return mnem, opcode, opers, iflags

def simpleTW(ival, mnem, opcode, opers, iflags):
    cond = opers[0].val
    opinfo = tw_mnems.get(cond)
    if opinfo:
        nmnem, nopcode = opinfo
        if nopcode == INS_TRAP:
            # No operands for a 'trap' instruction
            return nmnem, nopcode, (), iflags
        else:
            # remove the condition (first) operand
            return nmnem, nopcode, opers[1:], iflags

    return mnem, opcode, opers, iflags

def simpleTWI(ival, mnem, opcode, opers, iflags):
    cond = opers[0].val
    opinfo = twi_mnems.get(cond)
    if opinfo:
        nmnem, nopcode = opinfo
        if nopcode == INS_TRAP:
            # No operands for a 'trap' instruction
            return nmnem, nopcode, (), iflags
        else:
            # remove the condition (first) operand
            return nmnem, nopcode, opers[1:], iflags

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

    for onm, otype, oshr, omask, oflags in operands:
        val = (ival >> oshr) & omask
        oper = OPERCLASSES[otype](val, va)
        opers.append(oper)

    return opcode, opers, iflags

elemsizes = {
    OF_VEC_8: 1,
    OF_VEC_16: 2,
    OF_VEC_32: 4,
    OF_VEC_64: 8,
    OF_VEC_128: 16,
    OF_VEC_FLT: 4,
}
OF_VEC_MASK = (OF_VEC_8 | OF_VEC_16 | OF_VEC_32 | OF_VEC_64 | OF_VEC_128 | OF_VEC_FLT)

def oflags_elemsize(oflags):
    return elemsizes.get(oflags & OF_VEC_MASK, 1)   # use default to avoid dev failures

def form_VX(disasm, va, ival, opcode, operands, iflags):
    opers = []
    opcode = None

    # Default with special-casing for passing in size and signedness flags
    for onm, otype, oshr, omask, oflags in operands:
        val = (ival >> oshr) & omask
        if OPERCLASSES[otype] == PpcVRegOper:
            elemsize = oflags_elemsize(oflags)
            signed = oflags & OF_SIGNED
            floating = oflags & OF_VEC_FLT
            oper = OPERCLASSES[otype](val, va, elemsize=elemsize, signed=signed, floating=floating)
        else:
            oper = OPERCLASSES[otype](val, va)
        opers.append(oper)

    return opcode, opers, iflags

def form_A(disasm, va, ival, opcode, operands, iflags):
    # fallback for all non-memory-accessing FORM_X opcodes
    opers = []
    for onm, otype, oshr, omask, oflags in operands:
        val = (ival >> oshr) & omask

        # In addition to instructions that calculate an EA, the isel instruction
        # is FORM_A but if the second (rA) operand is 0 then a 0 constant should
        # be used instead of a register.
        if otype == FIELD_rA and val== 0 and \
                ((iflags & IF_MEM_EA) != 0 or opcode == INS_ISEL):
            opers.append(PpcImmOper(0, va))
        else:
            opers.append(OPERCLASSES[otype](val, va))

    return opcode, opers, iflags

tsizes_formX = {
    INS_LBZX: 1,
    INS_LHZX: 2,
    INS_LWZX: 4,
    INS_LDX: 8,
    INS_LHAX: 2,
    INS_LWAX: 4,
    INS_TLBIVAX: 8,
    INS_TLBSX: 8,
    INS_LHAUX: 2,
    INS_LWAUX: 4,
    INS_LBZUX: 1,
    INS_LHZUX: 2,
    INS_LWZUX: 4,
    INS_LDUX: 8,
    INS_STBX: 1,
    INS_STHX: 2,
    INS_STWX: 4,
    INS_STDX: 8,
    INS_STBUX: 1,
    INS_STHUX: 2,
    INS_STWUX: 4,
    INS_STDUX: 8,
    INS_LFSUX: 4,
    INS_LFSX: 4,
    INS_STFDX: 8,
    INS_STFIWX: 4,
    INS_STFDEPX: 8,
    INS_STFDUX: 8,
    INS_LVEBX: 1,
    INS_LVEHX: 2,
    INS_LVEPX: 16,
    INS_LVEPXL: 16,
    INS_LVEWX: 4,
    INS_LVEXBX: 1,
    INS_LVEXHX: 2,
    INS_LVEXWX: 4,
    INS_LVX: 16,
    INS_LVXL: 16,
    INS_LVSL: 1,    # irrelevant, never deref'd
    INS_LVSM: 1,    # irrelevant, never deref'd
    INS_LVSR: 1,    # irrelevant, never deref'd
    INS_LVSWX: 1,   # irrelevant, never deref'd
    INS_LVSWXL: 1,  # irrelevant, never deref'd
    INS_LVTLX: 1,   # irrelevant, never deref'd
    INS_LVTLXL: 1,  # irrelevant, never deref'd
    INS_LVTRX: 1,   # irrelevant, never deref'd
    INS_LVTRXL: 1,  # irrelevant, never deref'd
    INS_STVEBX: 1,
    INS_STVEHX: 2,
    INS_STVEWX: 4,
    INS_STVEXBX: 1,
    INS_STVEXHX: 2,
    INS_STVEXWX: 4,
    INS_STVFLX: 1,
    INS_STVFLXL: 1,
    INS_STVFRX: 1,
    INS_STVFRXL: 1,
    INS_STVX: 16,
    INS_STVXL: 16,
    INS_STVEPX: 16,
    INS_STVEPXL: 16,
    INS_EVLDDEPX: 8,
    INS_EVSTDDEPX: 8,
}

def form_X(disasm, va, ival, opcode, operands, iflags):
    # If this is an IF_MEM_EA instruction with rA and rB, those combine and we use
    # a PpcIndexedMemOper. rB is ALWAYS after rA if it's present, and part of the
    # definition of IF_INDEXED is that rA and rB are both present.
    opers = []
    operands_iterator = iter([(o[1], (ival >> o[2]) & o[3], o[4]) for o in operands])
    for otype, val, oflags in operands_iterator:
        if otype in [FIELD_rA, FIELD_sA] and iflags & IF_INDEXED:
            _, rB_val, _ = next(operands_iterator) # get rB and skip over it in next iteration
            opers.append(PpcIndexedMemOper(val, rB_val, va, tsize=tsizes_formX.get(opcode)))
        elif otype == FIELD_rA and val == 0 and (iflags & IF_MEM_EA) != 0:
            # Some FORM_X rA == 0 instructions are not load/store instructions
            opers.append(PpcImmOper(0, va))
        elif OPERCLASSES[otype] == PpcVRegOper:
            elemsize = oflags_elemsize(oflags)
            signed = oflags & OF_SIGNED
            opers.append(OPERCLASSES[otype](val, va, elemsize=elemsize, signed=signed))
        else:
            opers.append(OPERCLASSES[otype](val, va))

    return opcode, opers, iflags

def form_XL(disasm, va, ival, opcode, operands, iflags):
    opers = []
    opcode = None

    for onm, otype, oshr, omask, oflags in operands:
        val = (ival >> oshr) & omask
        if otype == FIELD_crBI:
            # Only add this operand if it has a non-zero value
            if val != 0:
                opers.append(OPERCLASSES[otype](val, va))
        else:
            opers.append(OPERCLASSES[otype](val, va))

    return opcode, opers, iflags

uimm_multipliers_formEVX = {
    FIELD_UIMM1: 8,
    FIELD_UIMM2: 2,
    FIELD_UIMM3: 4,
}

tsizes_formEVX = {
    INS_EVLDD: 8,
    INS_EVLDDX: 8,
    INS_EVLDH: 8,
    INS_EVLDHX: 8,
    INS_EVLDW: 8,
    INS_EVLDWX: 8,
    INS_EVLHHESPLAT: 2,
    INS_EVLHHESPLATX: 2,
    INS_EVLHHOSSPLAT: 2,
    INS_EVLHHOSSPLATX: 2,
    INS_EVLHHOUSPLAT: 2,
    INS_EVLHHOUSPLATX: 2,
    INS_EVLWHE: 4,
    INS_EVLWHEX: 4,
    INS_EVLWHOS: 4,
    INS_EVLWHOSX: 4,
    INS_EVLWHOU: 4,
    INS_EVLWHOUX: 4,
    INS_EVLWHSPLAT: 4,
    INS_EVLWHSPLATX: 4,
    INS_EVLWWSPLAT: 4,
    INS_EVLWWSPLATX: 4,
    INS_EVSTDD: 8,
    INS_EVSTDDX: 8,
    INS_EVSTDH: 8,
    INS_EVSTDHX: 8,
    INS_EVSTDW: 8,
    INS_EVSTDWX: 8,
    INS_EVSTWHE: 2,
    INS_EVSTWHO: 2,
    INS_EVSTWHEX: 2,
    INS_EVSTWHOX: 2,
    INS_EVSTWWE: 4,
    INS_EVSTWWO: 4,
    INS_EVSTWWEX: 4,
    INS_EVSTWWOX: 4,
}

def form_EVX(disasm, va, ival, opcode, operands, iflags):
    opers = []

    # if the last operand is UIMM[123], it's a memory deref.
    if len(operands) == 3 and operands[2][1] in (FIELD_UIMM1, FIELD_UIMM2, FIELD_UIMM3):
        opvals = [((ival >> oshr) & omask) for onm, otype, oshr, omask, oflags in operands]

        if OPERCLASSES[operands[0][1]] == PpcSPEVRegOper:
            elemsize = oflags_elemsize(operands[0][4])
            signed = operands[0][4] & OF_SIGNED
            floating = operands[0][4] & OF_VEC_FLT
            oper0 = OPERCLASSES[operands[0][1]](opvals[0], va, elemsize=elemsize, signed=signed, floating=floating)
        else:
            oper0 = OPERCLASSES[operands[0][1]](opvals[0], va)

        opers.append(oper0)
        oper1 = PpcMemOper(opvals[1], opvals[2] * uimm_multipliers_formEVX[operands[2][1]], va, tsize=tsizes_formEVX.get(opcode))
        opers.append(oper1)
        return opcode, opers, iflags

    # If this is an IF_MEM_EA instruction with rA and rB, those combine and we use
    # a PpcIndexedMemOper. rB is ALWAYS after rA if it's present, and part of the
    # definition of IF_INDEXED is that rA and rB are both present.
    operands_iterator = iter([(o[1], (ival >> o[2]) & o[3], o[4]) for o in operands])
    for otype, val, oflags in operands_iterator:
        if otype == FIELD_sA and iflags & IF_INDEXED:
            _, rB_val, _ = next(operands_iterator) # get rB and skip over it in next iteration
            opers.append(PpcIndexedMemOper(val, rB_val, va, tsize=tsizes_formEVX.get(opcode)))
            continue
        elif OPERCLASSES[otype] == PpcSPEVRegOper:
            elemsize = oflags_elemsize(oflags)
            signed = oflags & OF_SIGNED
            floating = oflags & OF_VEC_FLT
            oper = OPERCLASSES[otype](val, va, elemsize=elemsize, signed=signed, floating=floating)
        else:
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

    opvals = [((ival >> oshr) & omask) for onm, otype, oshr, omask, oflags in operands]
    # if the last operand is FIELD_D, it's a memory deref. (load/store instructions)
    if len(operands) == 3 and operands[2][1] == FIELD_D:
        # let's figure out what *memory size* the operand uses
        tsize = tsizes_formD.get(opcode)
        #print("DBG: 0x%x:   FORM_D: opcode: 0x%x    tsize=%r" % (va, opcode, tsize))
        oper0 = OPERCLASSES[operands[0][1]](opvals[0], va)
        oper1 = PpcMemOper(opvals[1], opvals[2], va, tsize=tsize)
        opers =(oper0, oper1)
        return opcode, opers, iflags

    oidx = 0
    for onm, otype, oshr, omask, oflags in operands:
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

    for onm, otype, oshr, omask, oflags in operands:
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

    opvals = [((ival >> oshr) & omask) for onm, otype, oshr, omask, oflags in operands]

    offset = e_bits.bsigned(opvals[0] << 2, 26)
    if iflags & IF_ABS:
        addr = e_bits.unsigned(offset, disasm.psize)
        tgtoper = PpcJmpAbsOper(addr)
    else:
        tgtoper = PpcJmpRelOper(offset, va)
    opers.append(tgtoper)

    return opcode, opers, iflags

tsizes_formDS = {
    INS_LD: 8,
    INS_LDU: 8,
    INS_LWA: 4,
    INS_STD: 8,
    INS_STDU: 8,
}

def form_DS(disasm, va, ival, opcode, operands, iflags):
    tsize = tsizes_formDS.get(opcode)
    opvals = [((ival >> oshr) & omask) for onm, otype, oshr, omask, oflags in operands]
    oper0 = OPERCLASSES[operands[0][1]](opvals[0], va)
    oper1 = PpcMemOper(opvals[1], opvals[2] * 4, va, tsize=tsize)
    opers = (oper0, oper1)
    return opcode, opers, iflags

def form_MDS(disasm, va, ival, opcode, operands, iflags):
    opers = []
    opcode = None

    opvals = [((ival >> oshr) & omask) for onm, otype, oshr, omask, oflags in operands]
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

    opvals = [((ival >> oshr) & omask) for onm, otype, oshr, omask, oflags in operands]
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

    opvals = [((ival >> oshr) & omask) for onm, otype, oshr, omask, oflags in operands]
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
        opvals = [((ival >> oshr) & omask) for onm, otype, oshr, omask, oflags in operands]

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

    for onm, otype, oshr, omask, oflags in operands:
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
decoders[FORM_VX] = form_VX
decoders[FORM_VC] = form_VX
decoders[FORM_VA] = form_VX


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
