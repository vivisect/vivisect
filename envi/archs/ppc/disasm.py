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
    def __init__(self, endian=ENDIAN_MSB, options=CAT_NONE|CAT_SP):  # FIXME: options needs to be paired down into a few common bitmasks, like CAT_ALTIVEC, etc...  right now this causes collisions, so first in list wins...
        # any speedy stuff here
        if options == 0:
            options = CAT_NONE
        self._dis_regctx = PpcRegisterContext()
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
        startoff = offset # Use startoff as a size knob if needed
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

        nopcode, opers, iflags = decoder(va, ival, operands, iflags)
        if nopcode != None:
            opcode = nopcode

        mnem, opcode, opers, iflags = self.simplifiedMnems(ival, mnem, opcode, opers, iflags)

        return PpcOpcode(va, opcode, mnem, size=4, operands=opers, iflags=iflags)

    def simplifiedMnems(self, ival, mnem, opcode, opers, iflags):
        if opcode in SIMPLIFIEDS.keys(): 
            return SIMPLIFIEDS[opcode](ival, mnem, opcode, opers, iflags)

        return mnem, opcode, opers, iflags


def simpleORI(ival, mnem, opcode, opers, iflags):
    if ival == 0x60000000:
        return 'nop', INS_NOP, tuple(), iflags
    return mnem, opcode, opers, iflags

def simpleADDI(ival, mnem, opcode, opers, iflags):
    if ival == 0x38000000:
        return 'li', INS_LI, (opers[0], opers[2]), iflags
    if ival == 0x3c000000:
        return 'lis', INS_LIS, (opers[0], opers[2]), iflags

    #  not sure how to do LA well just yet.
    return mnem, opcode, opers, iflags

def simpleOR(ival, mnem, opcode, opers, iflags):
    if opers[1] == opers[2]:
        return 'mr', INS_MR, (opers[0], opers[2]), iflags
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
    #if opers 
    return mnem, opcode, opers, iflags
def simpleISEL(ival, mnem, opcode, opers, iflags):
    if opers[-1].bit == 0:
        return 'isellt', INS_ISELLT, (opers[0], opers[1], opers[2]), iflags
    if opers[-1].bit == 1:
        return 'iselgt', INS_ISELGT, (opers[0], opers[1], opers[2]), iflags
    if opers[-1].bit == 2:
        return 'iseleq', INS_ISELEQ, (opers[0], opers[1], opers[2]), iflags
    return mnem, opcode, opers, iflags

SIMPLIFIEDS = {
        INS_ORI     : simpleORI,
        INS_ADDI    : simpleADDI,
        INS_OR      : simpleOR,
        INS_NOR     : simpleNOR,
        INS_MTCRF   : simpleMTCRF,
        INS_SYNC    : simpleSYNC,
        INS_ISEL    : simpleISEL,
}

def form_DFLT(va, ival, operands, iflags):
    opers = []
    opcode = None

    for onm, otype, oshr, omask in operands:
        val = (ival >> oshr) & omask
        oper = OPERCLASSES[otype](val, va)
        opers.append(oper)

    return opcode, opers, iflags
    
def form_EVX(va, ival, operands, iflags):
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
        opers.append(oper)

    return opcode, opers, iflags
    
def form_D(va, ival, operands, iflags):
    opers = []
    opcode = None

    # if the last operand is FIELD_D, it's a memory deref.
    if len(operands) == 3 and operands[2][1] == FIELD_D:
        opvals = [((ival >> oshr) & omask) for onm, otype, oshr, omask in operands]
        oper0 = OPERCLASSES[operands[0][1]](opvals[0], va)
        opers.append(oper0)

        oper1 = PpcMemOper(opvals[1], opvals[2], va)
        opers.append(oper1)
        return opcode, opers, iflags

    for onm, otype, oshr, omask in operands:
        val = (ival >> oshr) & omask
        oper = OPERCLASSES[otype](val, va)
        opers.append(oper)

    return opcode, opers, iflags
    
def form_DS(va, ival, operands, iflags):
    opcode = None

    opvals = [((ival >> oshr) & omask) for onm, otype, oshr, omask in operands]
    oper0 = OPERCLASSES[operands[0][1]](opvals[0], va)
    oper1 = PpcMemOper(opvals[1], opvals[2], va)
    opers = (oper0, oper1)
    return opcode, opers, iflags
    
def form_MDS(va, ival, operands, iflags):
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
    
def form_MD(va, ival, operands, iflags):
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
    
def form_XS(va, ival, operands, iflags):
    opers = []
    opcode = None

    opvals = [((ival >> oshr) & omask) for onm, otype, oshr, omask in operands]
    oper0 = OPERCLASSES[operands[0][1]](opvals[0], va)
    oper1 = OPERCLASSES[operands[1][1]](opvals[1], va)
    val = (opvals[3] << 5) | opvals[2]
    oper2 = PpcImmOper(val, va)

    opers = (oper0, oper1, oper2)
    return opcode, opers, iflags
    
def form_XFX(va, ival, operands, iflags):
    opers = []
    opcode = None

    if len(operands) == 3 and operands[2][1] in (FIELD_DCRN0_4, FIELD_PMRN0_4, FIELD_SPRN0_4, FIELD_TMRN0_4, FIELD_TBRN0_4,):
        opvals = [((ival >> oshr) & omask) for onm, otype, oshr, omask in operands]
        if operands[1][1] in (FIELD_DCRN5_9, FIELD_PMRN5_9, FIELD_SPRN5_9, FIELD_TMRN5_9, FIELD_TBRN5_9,):
            val = (opvals[2] << 5) | opvals[1]
            oper0 = OPERCLASSES[operands[0][1]](opvals[0], va)
            oper1 = PpcImmOper(val, va)    # FIXME: do we want specific DCRN, PMRN, SPRN, TMRN, TBRN operand types?
        else:
            val = (opvals[2] << 5) | opvals[0]
            oper0 = PpcImmOper(val, va)    # FIXME: do we want specific DCRN, PMRN, SPRN, TMRN, TBRN operand types?
            oper1 = OPERCLASSES[operands[1][1]](opvals[1], va)

        opers = (oper0, oper1)
        return opcode, opers, iflags

    for onm, otype, oshr, omask in operands:
        val = (ival >> oshr) & omask
        oper = OPERCLASSES[otype](val, va)
        opers.append(oper)

    return opcode, opers, iflags
    
decoders = { eval(x) : form_DFLT for x in globals().keys() if x.startswith('FORM_') }
decoders[FORM_EVX] = form_EVX
decoders[FORM_D] = form_D
decoders[FORM_DS] = form_DS
decoders[FORM_XFX] = form_XFX
decoders[FORM_MDS] = form_MDS
decoders[FORM_MD] = form_MD
decoders[FORM_XS] = form_XS

        
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
