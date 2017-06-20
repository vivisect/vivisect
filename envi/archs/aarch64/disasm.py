
inittable = [
    ( None, None ), #0
    ( None, None ), #1
    ( None, None ), #2
    ( None, None ), #3
    ( None, s_4_table ), #4
    ( IENC_DATA_PROC, None ), #5
    ( None, s_6_table ), #6
    (IENC_DATA_SIMD, None), #7
    ( None, s_8_table ), #8
    ( None, s_9_table ), #9
    ( IENC_BRANCH_EXC, None ), #a
    ( IENC_BRANCH_EXC, None ), #b
    ( None, s_c_table ), #c
    ( IENC_DATA_PROC, None ), #d
    ( None, s_e_table ), #e
    (IENC_DATA_SIMD, None) #f
]

s_8_table = [
    (0b00000011000000000000000000000000, 0b00000000000000000000000000000000, IENC_PC_ADDR),
    (0b00000011000000000000000000000000, 0b00000001000000000000000000000000, IENC_ADD_SUB),
    (0b00000011100000000000000000000000, 0b00000010000000000000000000000000, IENC_LOG_IMM),
    (0b00000011100000000000000000000000, 0b00000010100000000000000000000000, IENC_MOV_WIDE),
    (0b00000011100000000000000000000000, 0b00000011000000000000000000000000, IENC_BITFIELD),
    (0b00000011100000000000000000000000, 0b00000011100000000000000000000000, IENC_EXTRACT),
    (0,0,IENC_UNDEF) #catch-all
]

ienc_parsers_tmp = [None for x in range(IENC_MAX)]

ienc_parsers_tmp[IENC_DATA_PROC] = p_data_proc
ienc_parsers_tmp[IENC_DATA_SIMD] = p_data_simd
ienc_parsers_tmp[IENC_BRANCH_EXC] = p_branch_exc
ienc_parsers_tmp[IENC_PC_ADDR] = p_pc_addr
ienc_parsers_tmp[IENC_ADD_SUB] = p_add_sub
ienc_parsers_tmp[IENC_LOG_IMM] = p_log_imm
ienc_parsers_tmp[IENC_MOV_WIDE] = p_mov_wide
ienc_parsers_tmp[IENC_BITFIELD] = p_bitfield
ienc_parsers_tmp[IENC_EXTRACT] = p_extract


def p_add_sub(opval, va):
    opcode = INS_ADD
    mnem = 'add'
    cond = opval >> 29
    shift = opval >> 22 & 0x3
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f
    imm = opval >> 10 & 0xfff
    if shift == 0x00:
        olist = [
            (A64RegOper(rd, va=va))
            (A64RegOper(rn, va=va))
            (A64ImmOper(imm, 0, S_LSL, va)
        ]
    elif shift == 0x01:
        olist = [
            (A64RegOper(rd, va=va))
            (A64RegOper(rn, va=va))
            (A64ImmOper(imm, 12, S_LSL, va)
        ]
        
    return opcode, mnem, olist, 0, 0

class A64Operand(envi.Operand):
    tsize = 4
    def involvesPC(self):
        return False

    def getOperAddr(self, op, emu=None):
        return None

class A64RegOper(A64Operand):
    def __init__(self, reg, va=0, oflags=0):
        if reg == None:
            raise Exception("ArmRegOper: None Reg Type!")
            raise envi.InvalidInstruction(mesg="None Reg Type!",
                    bytez='f00!', va=va)
        self.va = va
        self.reg = reg
        self.oflags = oflags

class A64ImmOper(A64Operand):
    def __init__(self, val, shval=0, shtype=S_ROR, va=0, size=4):
        self.val = val
        self.shval = shval
        self.shtype = shtype
        self.size = size

         
class A64Opcode(envi.Opcode):
    _def_arch = envi.ARCH_ARMV8

    def __init__(self, va, opcode, mnem, prefixes, size, operands, iflags=0, simdflags=0):
        """
        constructor for the basic Envi Opcode object.  Arguments as follows:
        opcode   - An architecture specific numerical value for the opcode
        mnem     - A humon readable mnemonic for the opcode
        prefixes - a bitmask of architecture specific instruction prefixes
        size     - The size of the opcode in bytes
        operands - A list of Operand objects for this opcode
        iflags   - A list of Envi (architecture independant) instruction flags (see IF_FOO)
        va       - The virtual address the instruction lives at (used for PC relative immediates etc...)
        NOTE: If you want to create an architecture spcific opcode, I'd *highly* recommend you
              just copy/paste in the following simple initial code rather than calling the parent
              constructor.  The extra
        """
        self.opcode = opcode
        self.mnem = mnem
        self.prefixes = prefixes
        self.size = size
        self.opers = operands
        self.repr = None
        self.iflags = iflags
        self.simdflags = simdflags
        self.va = va
    

class AArch64Disasm:
    #weird thing in envi/__init__. Figure out later
    _optype = envi.ARCH_ARMV8
    _opclass = A64Opcode
    fmt = None
    #This holds the current running Arm instruction version and mask
    #ARCH_REVS is a file containing all masks for various versions of ARM. In const.py
    _archVersionMask = ARCH_REVS['ARMv8A']

    def __init__(self, endian=ENDIAN_LSB, mask = 'ARMv8A'):
        self.setArchMask(mask)
        self.setEndian(endian)


    def setArchMask(self, key = 'ARMv8R'):
        ''' set arch version mask '''
        self._archVersionMask = ARCH_REVS.get(key,0)

    def getArchMask(self):
        return self._archVersionMask

    def setEndian(self, endian):
        self.endian = endian
        self.fmt = ("<I", ">I")[endian]

    def getEndian(self):
        return self.endian

    def disasm(self, bytez, offset, va):
        '''
        Parse a series of bytes into an envi.Opcode instance
        ''' 
        opbytes = bytez[offset:offset+4]
        opval = struct.unpack(self.fmt, opbytes)

        cond = opval >> 29 & 0x7

        opcode, mnem, olist, flags, smdflags = self.doDecode(va, opval, bytez, offset)

        if mnem == None or type(mnem) == int:
            raise Exception("mnem == %r!  0x%x" % (mnem, opval))

        #FIXME insert some stuff in here. Check out ArmV7 for better idea. Flag modification


        op = A64Opcode(va, opcode, mnem, cond, 4, olist, flags, simdflags)
        return op

    def doDecode(self, va, opval, bytez, offset):
        encfam = (opval >> 25) & 0xf

        '''
        Using encfam,find encoding. If we can't find an encoding (enc == None),
        then throw an exception.
        '''
        enc,nexttab = inittable[encfam]
        if nexttab != None: # we have to sub-parse...
            for mask,val,penc in nexttab:
                #print "penc", penc
                if (opval & mask) == val:
                    enc = penc
                    break

        # If we don't know the encoding by here, we never will ;)
        if enc == None:
            raise envi.InvalidInstruction(mesg="No encoding found!",
                    bytez=bytez[offset:offset+4], va=va)

        '''
        ienc_parsers is a dictionary of encoding names mapped to corresponding functions
        i.e. ienc_parsers[IENC_UNCOND] = p_uncond
        therefore calling ienc_parsers[enc](opval, va+8) calls the corresponding function with parameters
        opval and va+8
        '''
        opcode, mnem, olist, flags, simdflags = ienc_parsers[enc](opval, va+8)
        return opcode, mnem, olist, flags, simdflags


        


        


if __name__=="__main__":
    import envi.archs
    envi.archs.dismain( AArch64Disasm() )
    
