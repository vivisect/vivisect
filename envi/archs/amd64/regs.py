import envi.registers as e_reg
import envi.archs.i386 as e_i386

# NOTE: all REX_R registers must *directly* follow their 3 bit variants
#       in the table below
amd64regs = [
    ("rax",64),("rcx",64),("rdx",64),("rbx",64),("rsp",64),("rbp",64),("rsi",64),("rdi",64),
    # The amd64 extended GP regs
    ("r8",64),("r9",64),("r10",64),("r11",64),("r12",64),("r13",64),("r14",64),("r15",64),

    # SIMD registers
    ("ymm0",256),("ymm1",256),("ymm2",256),("ymm3",256),("ymm4",256),("ymm5",256),("ymm6",256),("ymm7",256),
    # The amd64 extended SIMD regs...
    ("ymm8",256),("ymm9",256),("ymm10",256),("ymm11",256),("ymm12",256),("ymm13",256),("ymm14",256),("ymm15",256),

    #("xmm0",128),("xmm1",128),("xmm2",128),("xmm3",128),("xmm4",128),("xmm5",128),("xmm6",128),("xmm7",128),
    ## The amd64 extended SIMD regs...
    #("xmm8",128),("xmm9",128),("xmm10",128),("xmm11",128),("xmm12",128),("xmm13",128),("xmm14",128),("xmm15",128),

    # Debug registers
    ("debug0",64),("debug1",64),("debug2",64),("debug3",64),("debug4",64),("debug5",64),("debug6",64),("debug7",64),
    # Extended Debug registers (REX.R)
    ("debug8",64),("debug9",64),("debug10",64),("debug11",64),("debug12",64),("debug13",64),("debug14",64),("debug15",64),

    # Control registers
    ("ctrl0",64),("ctrl1",64),("ctrl2",64),("ctrl3",64),("ctrl4",64),("ctrl5",64),("ctrl6",64),("ctrl7",64),
    # Extended Control registers (REX.R)
    ("ctrl8",64),("ctrl9",64),("ctrl10",64),("ctrl11",64),("ctrl12",64),("ctrl13",64),("ctrl14",64),("ctrl15",64),

    # Test registers
    ("test0", 32),("test1", 32),("test2", 32),("test3", 32),("test4", 32),("test5", 32),("test6", 32),("test7", 32),
    # Segment registers
    ("es", 16),("cs",16),("ss",16),("ds",16),("fs",16),("gs",16),
    # FPU Registers
    ("st0", 80),("st1", 80),("st2", 80),("st3", 80),("st4", 80),("st5", 80),("st6", 80),("st7", 80),

    # Leftovers ;)
    # MS doesn't support rflags in Context structure
    ("eflags", 32), ("rip", 64), ("fpsr", 16), ("fpcr", 16),
]

# Build up a set of accessable constants
l = locals()
e_reg.addLocalEnums(l, amd64regs)

amd64meta = [
    ("mm0", REG_ST0, 0, 64),
    ("mm1", REG_ST1, 0, 64),
    ("mm2", REG_ST2, 0, 64),
    ("mm3", REG_ST3, 0, 64),
    ("mm4", REG_ST4, 0, 64),
    ("mm5", REG_ST5, 0, 64),
    ("mm6", REG_ST6, 0, 64),
    ("mm7", REG_ST7, 0, 64),

    ("eax", REG_RAX, 0, 32),
    ("ecx", REG_RCX, 0, 32),
    ("edx", REG_RDX, 0, 32),
    ("ebx", REG_RBX, 0, 32),
    ("esp", REG_RSP, 0, 32),
    ("ebp", REG_RBP, 0, 32),
    ("esi", REG_RSI, 0, 32),
    ("edi", REG_RDI, 0, 32),

    ("ax", REG_RAX, 0, 16),
    ("cx", REG_RCX, 0, 16),
    ("dx", REG_RDX, 0, 16),
    ("bx", REG_RBX, 0, 16),
    ("sp", REG_RSP, 0, 16),
    ("bp", REG_RBP, 0, 16),
    ("si", REG_RSI, 0, 16),
    ("di", REG_RDI, 0, 16),

    ("al", REG_RAX, 0, 8),
    ("cl", REG_RCX, 0, 8),
    ("dl", REG_RDX, 0, 8),
    ("bl", REG_RBX, 0, 8),

    ("ah", REG_RAX, 8, 8),
    ("ch", REG_RCX, 8, 8),
    ("dh", REG_RDX, 8, 8),
    ("bh", REG_RBX, 8, 8),

    # NOTE: with a REX prefix, all ah/ch regs get
    # mapped back to being sil/dil etc...
    ("spl", REG_RSP, 0, 8),
    ("bpl", REG_RBP, 0, 8),
    ("sil", REG_RSI, 0, 8),
    ("dil", REG_RDI, 0, 8),

    # The new GP regs are accessible in all modes.
    ("r8d",  REG_R8,  0, 32),
    ("r9d",  REG_R9,  0, 32),
    ("r10d", REG_R10, 0, 32),
    ("r11d", REG_R11, 0, 32),
    ("r12d", REG_R12, 0, 32),
    ("r13d", REG_R13, 0, 32),
    ("r14d", REG_R14, 0, 32),
    ("r15d", REG_R15, 0, 32),

    ("r8w",  REG_R8,  0, 16),
    ("r9w",  REG_R9,  0, 16),
    ("r10w", REG_R10, 0, 16),
    ("r11w", REG_R11, 0, 16),
    ("r12w", REG_R12, 0, 16),
    ("r13w", REG_R13, 0, 16),
    ("r14w", REG_R14, 0, 16),
    ("r15w", REG_R15, 0, 16),

    ("r8l",  REG_R8,  0, 8),
    ("r9l",  REG_R9,  0, 8),
    ("r10l", REG_R10, 0, 8),
    ("r11l", REG_R11, 0, 8),
    ("r12l", REG_R12, 0, 8),
    ("r13l", REG_R13, 0, 8),
    ("r14l", REG_R14, 0, 8),
    ("r15l", REG_R15, 0, 8),

    ("xmm0", REG_YMM0, 0, 128),
    ("xmm1", REG_YMM1, 0, 128),
    ("xmm2", REG_YMM2, 0, 128),
    ("xmm3", REG_YMM3, 0, 128),
    ("xmm4", REG_YMM4, 0, 128),
    ("xmm5", REG_YMM5, 0, 128),
    ("xmm6", REG_YMM6, 0, 128),
    ("xmm7", REG_YMM7, 0, 128),
    ("xmm8", REG_YMM8, 0, 128),
    ("xmm9", REG_YMM9, 0, 128),
    ("xmm10", REG_YMM10, 0, 128),
    ("xmm11", REG_YMM11, 0, 128),
    ("xmm12", REG_YMM12, 0, 128),
    ("xmm13", REG_YMM13, 0, 128),
    ("xmm14", REG_YMM14, 0, 128),
    ("xmm15", REG_YMM15, 0, 128),

]

statmetas = []
# have to rebuild this because the register index is different inside this
# scope.  rebuild with the REG_EFLAGS index inside this module.
for name, idx, offset, width, desc in e_i386.statmetas:
    statmetas.append( (name, REG_EFLAGS, offset, width, desc) )

e_reg.addLocalStatusMetas(l, amd64meta, statmetas, 'EFLAGS')
e_reg.addLocalMetas(l, amd64meta)

RMETA_LOW32 = 0x00200000

class Amd64RegisterContext(e_reg.RegisterContext):
    def __init__(self):
        self.loadRegDef(amd64regs)
        self.loadRegMetas(amd64meta, statmetas=statmetas)
        self.setRegisterIndexes(REG_RIP, REG_RSP, srindex=REG_EFLAGS)

    def setRegister(self, index, value):
        # NOTE: A special override is needed here because setting "eax" automagicall
        # zero extends into RAX...
        if (index & 0xffff0000) == RMETA_LOW32:
            index = index & 0xffff
        e_reg.RegisterContext.setRegister(self, index, value)

