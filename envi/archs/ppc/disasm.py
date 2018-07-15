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
    def __init__(self, endian=ENDIAN_MSB, options=CAT_NONE):  # FIXME: options needs to be paired down into a few common bitmasks, like CAT_ALTIVEC, etc...  right now this causes collisions, so first in list wins...
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

        return PpcOpcode(va, opcode, mnem, size=4, operands=opers, iflags=iflags)

def form_DFLT(va, ival, operands, iflags):
    opers = []
    opcode = None

    for onm, otype, oshr, omask in operands:
        val = (ival >> oshr) & omask
        oper = OPERCLASSES[otype](val, va)
        opers.append(oper)

    return opcode, opers, iflags
    
decoders = { eval(x) : form_DFLT for x in globals().keys() if x.startswith('FORM_') }

        
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
