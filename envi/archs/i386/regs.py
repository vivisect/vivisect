"""
Home of the i386 module's register specs/code.
"""
import envi.registers as e_reg

## Definitions for some of the i386 MSRs from intel...
MSR_DEBUGCTL             = 0x01d9 # Intel p4 and forward, debug behavior control
MSR_DEBUGCTL_LBR         = 0x0001 # last branch recording (in msr's)
MSR_DEBUGCTL_BTF         = 0x0002 # single-step on branches (break on branch)
MSR_DEBUGCTL_TR          = 0x0004 # enable sending "branch trace messages" !!
MSR_DEBUGCTL_BTS         = 0x0008 # enable logging BTMs to circular buffer
MSR_DEBUGCTL_BTINT       = 0x0010 # Branch-trace-interrupt (gen interrupt on BTS full)
MSR_DEBUGCTL_BTS_OFF_OS  = 0x0020 # disable ring0 branch trace store
MSR_DEBUGCTL_BTS_OFF_USR = 0x0040 # disable non-ring0 branch trace store

MSR_SYSENTER_EIP         = 0x0176 # Where is EIP at sysenter?

IA32_DS_AREA_MSR         = 0x0600 # pointer to the configured debug storage area

i386regs = [
    ("eax",32),("ecx",32),("edx",32),("ebx",32),("esp",32),("ebp",32),("esi",32),("edi",32),
    # SIMD registers
    ("xmm0",128),("xmm1",128),("xmm2",128),("xmm3",128),("xmm4",128),("xmm5",128),("xmm6",128),("xmm7",128),
    # Debug registers
    ("debug0",32),("debug1",32),("debug2",32),("debug3",32),("debug4",32),("debug5",32),("debug6",32),("debug7",32),
    # Control registers
    ("ctrl0",32),("ctrl1",32),("ctrl2",32),("ctrl3",32),("ctrl4",32),("ctrl5",32),("ctrl6",32),("ctrl7",32),
    # Test registers
    ("test0", 32),("test1", 32),("test2", 32),("test3", 32),("test4", 32),("test5", 32),("test6", 32),("test7", 32),
    # Segment registers
    ("es", 16),("cs",16),("ss",16),("ds",16),("fs",16),("gs",16),
    # FPU Registers
    ("st0", 80),("st1", 80),("st2", 80),("st3", 80),("st4", 80),("st5", 80),("st6", 80),("st7", 80),
    # Leftovers ;)
    ("eflags", 32), ("eip", 32), ("fpsr", 16), ("fpcr", 16),
    # TODO there's a bunch of floating point stuff that we basically just ignore
]

def getRegOffset(regs, regname):
    # NOTE: dynamically calculate this on import so we are less
    # likely to fuck it up...
    for i,(name,width) in enumerate(regs):
        if name == regname:
            return i
    raise Exception("getRegOffset doesn't know about: %s" % regname)

# dynamically create REG_EAX and the like in our module
l = locals()
e_reg.addLocalEnums(l, i386regs)

i386meta = [
    ("mm0", REG_ST0, 0, 64),
    ("mm1", REG_ST1, 0, 64),
    ("mm2", REG_ST2, 0, 64),
    ("mm3", REG_ST3, 0, 64),
    ("mm4", REG_ST4, 0, 64),
    ("mm5", REG_ST5, 0, 64),
    ("mm6", REG_ST6, 0, 64),
    ("mm7", REG_ST7, 0, 64),
    ("ax", REG_EAX, 0, 16),
    ("cx", REG_ECX, 0, 16),
    ("dx", REG_EDX, 0, 16),
    ("bx", REG_EBX, 0, 16),
    ("sp", REG_ESP, 0, 16),
    ("bp", REG_EBP, 0, 16),
    ("si", REG_ESI, 0, 16),
    ("di", REG_EDI, 0, 16),

    ("al", REG_EAX, 0, 8),
    ("cl", REG_ECX, 0, 8),
    ("dl", REG_EDX, 0, 8),
    ("bl", REG_EBX, 0, 8),

    ("ah", REG_EAX, 8, 8),
    ("ch", REG_ECX, 8, 8),
    ("dh", REG_EDX, 8, 8),
    ("bh", REG_EBX, 8, 8),
]

statmetas = [
        ('CF', REG_EFLAGS, 0, 1, 'Carry Flag'),
        ('PF', REG_EFLAGS, 2, 1, 'Parity Flag'),
        ('AF', REG_EFLAGS, 4, 1, 'Adjust Flag'),
        ('ZF', REG_EFLAGS, 6, 1, 'Zero Flag'),
        ('SF', REG_EFLAGS, 7, 1, 'Sign Flag'),
        ('TF', REG_EFLAGS, 8, 1, 'Trap Flag'),
        ('IF', REG_EFLAGS, 9, 1, 'Interrupt Enable Flag'),
        ('DF', REG_EFLAGS, 10, 1, 'Direction Flag'),
        ('OF', REG_EFLAGS, 11, 1, 'Overflow Flag'),
        ('IOPL', REG_EFLAGS, 12, 2, 'I/O Privilege Level'),
        ('NT', REG_EFLAGS, 14, 1, 'Nested Task'),
        ('RF', REG_EFLAGS, 16, 1, 'Resume Flag'),
        ('VM', REG_EFLAGS, 17, 1, 'Virtual-8086 Mode'),
        ('AC', REG_EFLAGS, 18, 1, 'Alignment Check'),
        ('VIF', REG_EFLAGS, 19, 1, 'Virtual Interrupt Flag'),
        ('VIP', REG_EFLAGS, 20, 1, 'Virtual Interrupt Pending'),
        ('ID', REG_EFLAGS, 21, 1, 'ID Flag'),
        ]

def getEflagsFields(regval):
    ret = []
    for name,_,shift,bits,desc in statmetas:
        ret.append( (name, regval >> shift & 1) )
    return ret

e_reg.addLocalStatusMetas(l, i386meta, statmetas, 'EFLAGS')
e_reg.addLocalMetas(l, i386meta)

class i386RegisterContext(e_reg.RegisterContext):
    def __init__(self):
        e_reg.RegisterContext.__init__(self)
        self.loadRegDef(i386regs)
        self.loadRegMetas(i386meta, statmetas=statmetas)
        self.setRegisterIndexes(REG_EIP, REG_ESP, srindex=REG_EFLAGS)
