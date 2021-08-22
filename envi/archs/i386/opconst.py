
# The opcode tables were taken from Mammon_'s Guide to Writing Disassemblers in Perl, You Morons!"
# and the bastard project. http://www.eccentrix.com/members/mammon/

INSTR_PREFIX = 0xF0000000
ADDRMETH_MASK = 0x00FF0000
ADDRMETH_A = 0x00010000    # Direct address with segment prefix
ADDRMETH_B = 0x00020000    # VEX.vvvv field selects general purpose register
ADDRMETH_C = 0x00030000    # MODRM reg field defines control register
ADDRMETH_D = 0x00040000    # MODRM reg field defines debug register
ADDRMETH_E = 0x00050000    # MODRM byte defines reg/memory address
ADDRMETH_F = 0x00060000    # EFLAGS/RFLAGS register
ADDRMETH_G = 0x00070000    # MODRM byte defines general-purpose reg
ADDRMETH_H = 0x00080000    # VEX.vvvv field selects 128bit XMM or 256bit YMM register
ADDRMETH_I = 0x00090000    # Immediate data follows
ADDRMETH_J = 0x000A0000    # Immediate value is relative to EIP
ADDRMETH_L = 0x000B0000    # An immediate value follows, but bits[7:4] signifies an xmm register
ADDRMETH_M = 0x000C0000    # MODRM mod field can refer only to memory
ADDRMETH_N = 0x000D0000    # R/M field of MODRM selects a packed-quadword, MMX register
ADDRMETH_O = 0x000E0000    # Displacement follows (without modrm/sib)
ADDRMETH_P = 0x000F0000    # MODRM reg field defines MMX register
ADDRMETH_Q = 0x00100000    # MODRM defines MMX register or memory
ADDRMETH_R = 0x00110000    # MODRM mod field can only refer to register
ADDRMETH_S = 0x00120000    # MODRM reg field defines segment register
ADDRMETH_U = 0x00130000    # MODRM R/M field defines XMM register
ADDRMETH_V = 0x00140000    # MODRM reg field defines XMM register
ADDRMETH_W = 0x00150000    # MODRM defines XMM register or memory
ADDRMETH_X = 0x00160000    # Memory addressed by DS:rSI
ADDRMETH_Y = 0x00170000    # Memory addressd by ES:rDI
ADDRMETH_VEXH = 0x00180000  # Maybe Ignore the VEX.vvvv field based on what the ModRM bytes are
ADDRMETH_LAST = ADDRMETH_VEXH

ADDRMETH_VEXSKIP = 0x00800000  # This operand should be skipped if we're not in VEX mode

OPTYPE_a = 0x01000000     # 2/4   two one-word operands in memory or two double-word operands in memory (operand-size attribute)   
OPTYPE_b = 0x02000000     # 1     always 1 byte
OPTYPE_c = 0x03000000     # 1/2   byte or word, depending on operand
OPTYPE_d = 0x04000000     # 4     double-word
OPTYPE_ds = 0x04000000     # 4     double-word
OPTYPE_dq = 0x05000000     # 16    double quad-word
OPTYPE_p = 0x06000000     # 4/6   32-bit or 48-bit pointer
OPTYPE_pi = 0x07000000     # 8     quadword MMX register
OPTYPE_ps = 0x08000000     # 16    128-bit single-precision float (packed?)
OPTYPE_pd = 0x08000000     # ??    should be a double-precision float?
OPTYPE_q = 0x09000000     # 8     quad-word
OPTYPE_qp = 0x09000000     # 8     quad-word
OPTYPE_qq = 0x0A000000     # 8     quad-word
OPTYPE_s = 0x0B000000     # 6     6-byte pseudo descriptor
OPTYPE_ss = 0x0C000000     # ??    Scalar of 128-bit single-precision float
OPTYPE_si = 0x0D000000     # 4     Doubleword integer register
OPTYPE_sd = 0x0E000000     # Scalar double precision float
OPTYPE_v = 0x0F000000     # 2/4   word or double-word, depending on operand
OPTYPE_w = 0x10000000     # 2     always word
OPTYPE_x = 0x11000000     # 2     double-quadword or quad-quadword
OPTYPE_y = 0x12000000     # 4/8   dword or qword
OPTYPE_z = 0x13000000     # 2/4   is this OPTYPE_z?  word for 16-bit operand size or doubleword for 32 or 64-bit operand-size

OPTYPE_fs = 0x14000000
OPTYPE_fd = 0x15000000
OPTYPE_fe = 0x16000000
OPTYPE_fb = 0x17000000
OPTYPE_fv = 0x18000000

# FIXME this should probably be a list rather than a dictionary

OPERSIZE = {
    0: (2, 4, 8),           # We will only end up here on regs embedded in opcodes
    OPTYPE_a: (4, 8, 8),
    OPTYPE_b: (1, 1, 1),
    OPTYPE_c: (1, 2, 2),           # 1/2   byte or word, depending on operand
    OPTYPE_d: (4, 4, 4),           # 4     double-word
    OPTYPE_dq: (16, 16, 16),        # 16    double quad-word
    OPTYPE_p: (4, 6, 6),           # 4/6   32-bit or 48-bit pointer
    OPTYPE_pi: (8, 8, 8),           # 8     quadword MMX register
    OPTYPE_ps: (16, 16, 16),        # 16    128-bit single-precision float
    OPTYPE_pd: (16, 16, 16),        # ??    should be a double-precision float?
    OPTYPE_q: (8, 8, 8),           # 8     quad-word
    OPTYPE_qq: (32, 32, 32),        # 32    quad-quad-word
    OPTYPE_s: (6, 10, 10),         # 6     6-byte pseudo descriptor
    OPTYPE_ss: (16, 16, 16),        # ??    Scalar of 128-bit single-precision float
    OPTYPE_si: (4, 4, 4),           # 4     Doubleword integer register
    OPTYPE_sd: (16, 16, 16),        # ???   Scalar of 128-bit double-precision float
    OPTYPE_v: (2, 4, 8),           # 2/4   word or double-word, depending on operand
    OPTYPE_w: (2, 2, 2),           # 2     always word
    OPTYPE_x: (16, 16, 32),        # 16/32 double-quadword or quad-quadword
    OPTYPE_y: (4, 4, 8),           # 4/8   dword or qword in 64-bit mode
    OPTYPE_z: (2, 4, 4),           # word for 16-bit operand size or doubleword for 32 or 64-bit operand-size
    # Floating point crazyness FIXME these are mostly wrong
    OPTYPE_fs: (4, 4, 4),
    OPTYPE_fd: (8, 8, 8),
    OPTYPE_fe: (10, 10, 10),
    OPTYPE_fb: (10, 10, 10),
    OPTYPE_fv: (14, 14, 28),
}

INS_NOPREF = 0x10000  # This instruction diallows prefixes, and if it does, it's a different insttruction
INS_VEXREQ = 0x20000  # This instructions requires VEX
INS_VEXNOPREF = 0x40000  # This instruction doesn't get the "v" prefix common to VEX instructions

INS_EXEC = 0x1000
INS_ARITH = 0x2000
INS_LOGIC = 0x3000
INS_STACK = 0x4000
INS_COND = 0x5000
INS_LOAD = 0x6000
INS_ARRAY = 0x7000
INS_BIT = 0x8000
INS_FLAG = 0x9000
INS_FPU = 0xA000
INS_TRAPS = 0xD000
INS_SYSTEM = 0xE000
INS_OTHER = 0xF000

INS_BRANCH = INS_EXEC | 0x01
INS_BRANCHCC = INS_EXEC | 0x02
INS_CALL = INS_EXEC | 0x03
INS_CALLCC = INS_EXEC | 0x04
INS_RET = INS_EXEC | 0x05
INS_LOOP = INS_EXEC | 0x06
INS_ADD = INS_ARITH | 0x01

INS_SUB = INS_ARITH | 0x02
INS_MUL = INS_ARITH | 0x03
INS_DIV = INS_ARITH | 0x04
INS_INC = INS_ARITH | 0x05
INS_DEC = INS_ARITH | 0x06
INS_SHL = INS_ARITH | 0x07
INS_SHR = INS_ARITH | 0x08
INS_ROL = INS_ARITH | 0x09
INS_ROR = INS_ARITH | 0x0A
INS_ABS = INS_ARITH | 0x0B

INS_AND = INS_LOGIC | 0x01
INS_OR = INS_LOGIC | 0x02
INS_XOR = INS_LOGIC | 0x03
INS_NOT = INS_LOGIC | 0x04
INS_NEG = INS_LOGIC | 0x05

INS_PUSH =        INS_STACK | 0x01
INS_POP =         INS_STACK | 0x02
INS_PUSHREGS =    INS_STACK | 0x03
INS_POPREGS =     INS_STACK | 0x04
INS_PUSHFLAGS =   INS_STACK | 0x05
INS_POPFLAGS =    INS_STACK | 0x06
INS_ENTER =       INS_STACK | 0x07
INS_LEAVE =       INS_STACK | 0x08

INS_TEST  =              INS_COND | 0x01
INS_CMP   =      INS_COND | 0x02
INS_MOV    =     INS_LOAD | 0x01

INS_MOVCC  =             INS_LOAD | 0x02
INS_XCHG   =             INS_LOAD | 0x03
INS_XCHGCC =     INS_LOAD | 0x04
INS_LEA    =     INS_LOAD | 0x05

INS_STRCMP  = INS_ARRAY | 0x01
INS_STRLOAD = INS_ARRAY | 0x02
INS_STRMOV  = INS_ARRAY | 0x03
INS_STRSTOR = INS_ARRAY | 0x04
INS_XLAT    = INS_ARRAY | 0x05

INS_BITTEST =  INS_BIT | 0x01
INS_BITSET  =  INS_BIT | 0x02
INS_BITCLR  =  INS_BIT | 0x03

INS_CLEARCF  = INS_FLAG | 0x01
INS_CLEARZF  = INS_FLAG | 0x02
INS_CLEAROF  = INS_FLAG | 0x03
INS_CLEARDF  = INS_FLAG | 0x04
INS_CLEARSF  = INS_FLAG | 0x05
INS_CLEARPF  = INS_FLAG | 0x06
INS_SETCF    = INS_FLAG | 0x07
INS_SETZF    = INS_FLAG | 0x08
INS_SETOF    = INS_FLAG | 0x09
INS_SETDF    = INS_FLAG | 0x0A
INS_SETSF    = INS_FLAG | 0x0B
INS_SETPF    = INS_FLAG | 0x0C
INS_CLEARAF  = INS_FLAG | 0x0D
INS_SETAF    = INS_FLAG | 0x0E

INS_TOGCF    = INS_FLAG | 0x10  # /* toggle */
INS_TOGZF    = INS_FLAG | 0x20
INS_TOGOF    = INS_FLAG | 0x30
INS_TOGDF    = INS_FLAG | 0x40
INS_TOGSF    = INS_FLAG | 0x50
INS_TOGPF    = INS_FLAG | 0x60

INS_TRAP = INS_TRAPS | 0x01         # generate trap
INS_TRAPCC = INS_TRAPS | 0x02       # conditional trap gen
INS_TRET = INS_TRAPS | 0x03         # return from trap
INS_BOUNDS = INS_TRAPS | 0x04       # gen bounds trap
INS_DEBUG = INS_TRAPS | 0x05        # gen breakpoint trap
INS_TRACE = INS_TRAPS | 0x06        # gen single step trap
INS_INVALIDOP = INS_TRAPS | 0x07    # gen invalid instruction
INS_OFLOW = INS_TRAPS | 0x08       # gen overflow trap

#/* INS_SYSTEM */
INS_HALT    = INS_SYSTEM | 0x01 # halt machine
INS_IN      = INS_SYSTEM | 0x02 # input form port
INS_OUT     = INS_SYSTEM | 0x03 # output to port
INS_CPUID   = INS_SYSTEM | 0x04 # iden

INS_NOP     = INS_OTHER | 0x01
INS_BCDCONV = INS_OTHER | 0x02  # convert to/from BCD
INS_SZCONV  = INS_OTHER | 0x03  # convert size of operand
INS_CRYPT   = INS_OTHER | 0x4  # AES-NI instruction support


OP_R = 0x001
OP_W = 0x002
OP_X = 0x004
OP_64AUTO = 0x008  # operand is in 64bit mode with amd64!
# So these this exists is because in the opcode mappings intel puts out, they very 
# *specifically* call out things like pmovsx* using U/M for their operand mappings,
# but *not* W. The reason for this being there
# is a size difference between the U and M portions, whereas W uses a uniform size for both
OP_MEM_B = 0x010  # force only *memory* to be 8 bit.
OP_MEM_W = 0x020  # force only *memory* to be 16 bit.
OP_MEM_D = 0x030  # force only *memory* to be 32 bit.
OP_MEM_Q = 0x040  # force only *memory* to be 64 bit.
OP_MEM_DQ = 0x050  # force only *memory* to be 128 bit.
OP_MEM_QQ = 0x060  # force only *memory* to be 256 bit.
OP_MEMMASK = 0x070  # this forces the memory to be a different size than the register. Reaches into OP_EXTRA_MEMSIZES

OP_NOVEXL = 0x080  # don't apply VEX.L here (even though it's set). TLDR: always 128/xmm reg

OP_EXTRA_MEMSIZES = [None, 1, 2, 4, 8, 16, 32]

OP_UNK = 0x000
OP_REG = 0x100
OP_IMM = 0x200
OP_REL = 0x300
OP_ADDR = 0x400
OP_EXPR = 0x500
OP_PTR = 0x600
OP_OFF = 0x700

OP_SIGNED = 0x001000
OP_STRING = 0x002000
OP_CONST = 0x004000
OP_NOREX = 0x008000

ARG_NONE = 0
cpu_8086 = 0x00001000
cpu_80286 = 0x00002000
cpu_80386 = 0x00003000
cpu_80387 = 0x00004000
cpu_80486 = 0x00005000
cpu_PENTIUM = 0x00006000
cpu_PENTPRO = 0x00007000
cpu_PENTMMX = 0x00008000
cpu_PENTIUM2 = 0x00009000
cpu_AMD64 = 0x0000a000
cpu_AESNI = 0x0000b000
cpu_AVX   = 0x0000c000
cpu_BMI   = 0x0000d000
cpu_OSPKE = 0x0000e000

#eventually, change this for your own codes
#ADDEXP_SCALE_OFFSET= 0 
#ADDEXP_INDEX_OFFSET= 8
#ADDEXP_BASE_OFFSET = 16
#ADDEXP_DISP_OFFSET = 24
#MODRM_EA =  1
#MODRM_reg=  0
ADDRMETH_MASK = 0x00FF0000
OPTYPE_MASK = 0xFF000000
OPFLAGS_MASK = 0x0000FFFF

# NOTE: some notes from the intel manual...
# REX.W overrides 66, but alternate registers (via REX.B etc..) can have 66 to be 16 bit..
# REX.R only modifies reg for GPR/SSE(SIMD)/ctrl/debug addressing modes.
# REX.X only modifies the SIB index value
# REX.B modifies modrm r/m field, or SIB base (if SIB present), or opcode reg.
# We inherit all the regular intel prefixes...
# VEX replaces REX, and mixing them is invalid
PREFIX_REX   = 0x100000  # Shows that the rex prefix is present
PREFIX_REX_B = 0x010000  # Bit 0 in REX prefix (0x41) means ModR/M r/m field, SIB base, or opcode reg
PREFIX_REX_X = 0x020000  # Bit 1 in REX prefix (0x42) means SIB index extension
PREFIX_REX_R = 0x040000  # Bit 2 in REX prefix (0x44) means ModR/M reg extention
PREFIX_REX_W = 0x080000  # Bit 3 in REX prefix (0x48) means 64 bit operand
PREFIX_REX_MASK = PREFIX_REX_B | PREFIX_REX_X | PREFIX_REX_W | PREFIX_REX_R
PREFIX_REX_RXB  = PREFIX_REX_B | PREFIX_REX_X | PREFIX_REX_R
