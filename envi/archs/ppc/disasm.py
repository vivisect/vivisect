import envi
import envi.bits as e_bits

import copy
import struct

#from envi.archs.ppc.disasm import *
from envi.archs.ppc.ppc_tables import *
from envi.archs.ppc.regs import *
from const import *
from disasm_classes import *

class PpcDisasm:
    __ARCH__ = None # abstract class.  subclasses should define this
    def __init__(self, endian=ENDIAN_MSB, options=CAT_PPC_EMBEDDED):
        ### FIXME: options gets lost in Vivisect.  it must be part of the event stream to get saved.  this is only worthwhile for canned options which are otherwise persistent or for incidental hacking use.
        ### perhaps we need arch config entries in the config file which are passed into the different architectures.
        # any speedy stuff here
        if options == 0:
            options = CAT_NONE
        self._dis_regctx = Ppc64RegisterContext()
        self.setEndian(endian)
        self.options = options

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

        fmt = ('<I', '>I')[self.endian]
        ival, = struct.unpack_from(fmt, bytez, offset)
        #print hex(ival)

        key = ival >> 26
        #print hex(key)
        
        group = instr_dict.get(key)
        #print group
        if group == None:
            raise envi.InvalidInstruction(bytez[offset:offset+4], 'No Instruction Group Found: %x' % key, va)

        data = None
        match = False
        for ocode in group:
            mask, value, data = ocode
            #print hex(ival), hex(mask), hex(value)
            if ival & mask != value:
                continue
            if not (data[3] & self.options):
                #print "0x%x & 0x%x == 0 :(" % (data[3], self.options)
                continue

            #print "0x%x & 0x%x != 0 :)" % (data[3], self.options)
            #print "match:  %x & %x == %x" % (ival, mask, value)
            match = True
            break

        if not match:
            raise envi.InvalidInstruction(bytez[offset:offset+4], 'No Instruction Matched in Group: %x' % key, va)

        mnem, opcode, form, cat, operands, iflags = data

        decoder = decoders.get(form, form_DFLT)
        if decoder == None:
            raise envi.InvalidInstruction(bytez[offset:offset+4], 'No Decoder Found for Form %s' % form_names.get(form), va)

        nopcode, opers, iflags = decoder(self, va, ival, operands, iflags)
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

def simpleCMP(ival, mnem, opcode, opers, iflags):
    #print vars(opers[0])
    l = opers[1].val
    opers.pop(1)

    # if using CR0, it can be omitted
    if opers[0].field == 0:
        opers.pop(0)
    
    if l == 0:
        return 'cmpw', INS_CMPWI, opers, iflags
    return 'cmpd', INS_CMPDI, opers, iflags

def simpleCMPI(ival, mnem, opcode, opers, iflags):
    l = opers[1].val
    opers.pop(1)

    # if using CR0, it can be omitted
    if opers[0].field == 0:
        opers.pop(0)
    
    if l == 0:
        return 'cmpwi', INS_CMPWI, opers, iflags
    return 'cmpdi', INS_CMPDI, opers, iflags

def simpleCMPLI(ival, mnem, opcode, opers, iflags):
    l = opers[1].val
    opers.pop(1)

    # if using CR0, it can be omitted
    if opers[0].field == 0:
        opers.pop(0)
   
    if l == 0:
        return 'cmplwi', INS_CMPWI, opers, iflags
    return 'cmpldi', INS_CMPDI, opers, iflags

def simpleCMPL(ival, mnem, opcode, opers, iflags):
    l = opers[1].val
    opers.pop(1)

    # if using CR0, it can be omitted
    if opers[0].field == 0:
        opers.pop(0)
    
    if l == 0:
        return 'cmplw', INS_CMPWI, opers, iflags
    return 'cmpld', INS_CMPDI, opers, iflags

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
            return 'msync', opcode, (), iflags

        if oper0 == 1:
            return 'lwsync', opcode, (), iflags

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
        0x05 : 'lge',
        0x06 : 'lle', 

        0x04 : 'eq',

        0x08 : 'gt',
        0x0a : 'ge',
        0x10 : 'lt',
        0x14 : 'le',
        0x18 : 'ne',
        0x1f : '',
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


from regs import sprnames
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
for k, v in globals().items():
    if k.startswith('simple'):
        capmnem = k[6:]
        SIMPLIFIEDS[eval('INS_' + capmnem)] = v


# FORM parsers
def form_DFLT(disasm, va, ival, operands, iflags):
    opers = []
    opcode = None

    for onm, otype, oshr, omask in operands:
        val = (ival >> oshr) & omask
        oper = OPERCLASSES[otype](val, va)
        opers.append(oper)

    return opcode, opers, iflags
    
def form_A(disasm, va, ival, operands, iflags):
    opcode = None
    # fallback for all non-memory-accessing FORM_X opcodes
    opers = []
    for onm, otype, oshr, omask in operands:
        val = (ival >> oshr) & omask
        oper = OPERCLASSES[otype](val, va)
        opers.append(oper)

    if iflags & IF_MEM_EA:
        opvals = [((ival >> oshr) & omask) for onm, otype, oshr, omask in operands]
        # FORM_X opcodes that access memory (EA calculation) with rA==0 use the number 0
        if opvals[1] == 0:
            opers[1] = PpcImmOper(0, va)

    return opcode, opers, iflags

def form_X(disasm, va, ival, operands, iflags):
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

    
def form_XL(disasm, va, ival, operands, iflags):
    opers = []
    opcode = None

    for onm, otype, oshr, omask in operands:
        val = (ival >> oshr) & omask
        if otype == FIELD_BH:
            iflags |= BHFLAGS[val]
            continue # FIXME: this may want to change...
        oper = OPERCLASSES[otype](val, va)
        opers.append(oper)

    return opcode, opers, iflags
    
def form_EVX(disasm, va, ival, operands, iflags):
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
    
def form_D(disasm, va, ival, operands, iflags):
    opers = []
    opcode = None

    opvals = [((ival >> oshr) & omask) for onm, otype, oshr, omask in operands]
    # if the last operand is FIELD_D, it's a memory deref.
    if len(operands) == 3 and operands[2][1] == FIELD_D:
        oper0 = OPERCLASSES[operands[0][1]](opvals[0], va)
        opers.append(oper0)

        if opvals[1] == 0:
            oper1 = PpcImmOper(0, va)
            oper2 = OPERCLASSES[operands[2][1]](opvals[2], va)
            opers = (oper0, oper1, oper2)
            return opcode, opers, iflags

        oper1 = PpcMemOper(opvals[1], opvals[2], va)
        opers.append(oper1)
        return opcode, opers, iflags

    # check for rA being 0... and convert it to Immediate 0     TESTME: does this correctly slice the instruction set?
    elif iflags & IF_MEM_EA and len(operands) == 3 and operands[1][1] == FIELD_rA and opvals[1] == 0:
        print "form_D: secondary IF_MEM_EA...", hex(ival), operands, iflags
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
    
def form_B(disasm, va, ival, operands, iflags):
    opers = []
    opcode = None

    opvals = [((ival >> oshr) & omask) for onm, otype, oshr, omask in operands]

    # contingency for decoding BC opcodes with BO left in tact (basically, BC, BCL, BCA, BCLA)
    if len(opvals) == 3:
        opers.append(PpcImmOper(opvals.pop(0), va))

    if len(opvals) == 2:
        opers.append(PpcCBRegOper(opvals[0], va))
        tgt = opvals[1] << 2
    
    if len(opvals) == 1:    # eg. bdnz doesn't have a BI operand
        tgt = opvals[0] << 2

    if iflags & IF_ABS:
        opers.append(PpcUImmOper(tgt, va))
    else:
        val = e_bits.signed(tgt, 2) + va
        opers.append(PpcUImmOper(val, va))

    return opcode, opers, iflags

def form_I(disasm, va, ival, operands, iflags):
    opers = []
    opcode = None

    opvals = [((ival >> oshr) & omask) for onm, otype, oshr, omask in operands]

    tgt = opvals[0] << 2
    if iflags & IF_ABS:
        opers.append(PpcUImmOper(tgt, va))
    else:
        val = e_bits.bsigned(tgt, 26) + va
        opers.append(PpcUImmOper(val, va))

    return opcode, opers, iflags

def form_DS(disasm, va, ival, operands, iflags):
    opcode = None

    opvals = [((ival >> oshr) & omask) for onm, otype, oshr, omask in operands]
    oper0 = OPERCLASSES[operands[0][1]](opvals[0], va)
    oper1 = PpcMemOper(opvals[1], opvals[2] * 4, va)
    opers = (oper0, oper1)
    return opcode, opers, iflags
    
def form_MDS(disasm, va, ival, operands, iflags):
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
    
def form_MD(disasm, va, ival, operands, iflags):
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
    
def form_XS(disasm, va, ival, operands, iflags):
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

def form_XFX(disasm, va, ival, operands, iflags):
    opers = []
    opcode = None

    if len(operands) == 3 and operands[2][1] in (FIELD_DCRN0_4, FIELD_PMRN0_4, FIELD_SPRN0_4, FIELD_TMRN0_4, FIELD_TBRN0_4,):
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

class Ppc64EmbeddedDisasm(PpcDisasm):
    __ARCH__ = envi.ARCH_PPC_E64
    def __init__(self, endian=ENDIAN_MSB, options=CAT_PPC_EMBEDDED):
        PpcDisasm.__init__(self, endian, options)

class Ppc32EmbeddedDisasm(PpcDisasm):
    __ARCH__ = envi.ARCH_PPC_E32
    def __init__(self, endian=ENDIAN_MSB, options=CAT_PPC_EMBEDDED):
        PpcDisasm.__init__(self, endian, options)

class Ppc64ServerDisasm(PpcDisasm):
    __ARCH__ = envi.ARCH_PPC_S64
    def __init__(self, endian=ENDIAN_MSB, options=CAT_PPC_SERVER):
        PpcDisasm.__init__(self, endian, options)

class Ppc32ServerDisasm(PpcDisasm):
    __ARCH__ = envi.ARCH_PPC_S32
    def __init__(self, endian=ENDIAN_MSB, options=CAT_PPC_SERVER):
        PpcDisasm.__init__(self, endian, options)

