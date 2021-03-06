
"""
Home of the PowerPC module's register specs/code.
"""
import envi.registers as e_reg

gprs32 = [('r%s' % x, 32)  for x in range(32)]
gprs64 = [('r%s' % x, 64)  for x in range(32)]
floats = [('f%s' % x, 64)  for x in range(32)]
floats.append( ('FPSCR', 64) )
vectors = [('v%s' % x, 64)  for x in range(32)]
vectors.append( ('VSCR', 64) )

sysregs = (
        ('ACC', 64),
        ('CR', 64),
        ('MSR', 64),
        ('TEN', 64),
        ('SPEFSCR', 64),
        ('PC', 64),
        )

ppc_regs32 = []
ppc_regs = ppc_regs64 = []

ppc_regs64.extend(gprs64)
ppc_regs32.extend(gprs32)

REG_OFFSET_FLOAT = len(ppc_regs)
ppc_regs64.extend(floats)
ppc_regs32.extend(floats)

REG_OFFSET_VECTOR = len(ppc_regs)
ppc_regs64.extend(vectors)
ppc_regs32.extend(vectors)

REG_OFFSET_SYSREGS = len(ppc_regs)
ppc_regs64.extend(sysregs)
ppc_regs32.extend(sysregs)

from . import spr
# populate spr_regs from the PPC SPR register list (in spr.py)
spr_regs = [('%#x' % x, 64) for x in range(1024)]
for sprnum, (rname, rdesc, bitsz) in spr.sprs.items():
    spr_regs[sprnum] = (rname, bitsz)

sprnames = {x:y.lower() for x,(y,z,b) in spr.sprs.items()}

REG_OFFSET_SPR = len(ppc_regs)
ppc_regs64.extend(spr_regs)
ppc_regs32.extend(spr_regs)


# sparse definition of TMR regs, so we fill in the gaps a bit
tmr_regs = [("TMRREG%d" % x, 64) for x in range(192) ]
tmr_regs[16] = ('tmcfg0', 64)

tpri_regs = [('tpri%d' % x, 64) for x in range(32)]
imsr_regs = [('imsr%d' % x, 64) for x in range(32)]
inia_regs = [('inia%d' % x, 64) for x in range(32)]
tmr_regs.extend(tpri_regs)
tmr_regs.extend([("TPRIREG%d" % x, 64) for x in range(224, 288) ])   # padding
tmr_regs.extend(imsr_regs)
tmr_regs.extend(inia_regs)

REG_OFFSET_TMR = len(ppc_regs)
ppc_regs64.extend(tmr_regs)
ppc_regs32.extend(tmr_regs)


REG_OFFSET_DCR = len(ppc_regs)
ppc_regs64.extend([('dcr%d' % x, 64) for x in range(1024)])
ppc_regs32.extend([('dcr%d' % x, 64) for x in range(1024)])


pmr_regs = []
pmr_regs.extend([('upmc%d' % x, 32) for x in range(16)])
pmr_regs.extend([('pmc%d' % x, 32) for x in range(16)])
pmr_regs.extend([('foo%d' % x, 32) for x in range(96)])
pmr_regs.extend([('upmlca%d' % x, 32) for x in range(16)])
pmr_regs.extend([('pmlca%d' % x, 32) for x in range(16)])
pmr_regs.extend([('bar%d' % x, 32) for x in range(96)])
pmr_regs.extend([('upmlcb%d' % x, 32) for x in range(16)])
pmr_regs.extend([('pmlcb%d' % x, 32) for x in range(16)])
pmr_regs.extend([('baz%d' % x, 32) for x in range(96)])
pmr_regs.append(('upmgc0', 64))
pmr_regs.extend([('fuq%d' % x, 32) for x in range(15)])
pmr_regs.append(('pmgc0', 64))

REG_OFFSET_PMR = len(ppc_regs)
ppc_regs64.extend(pmr_regs)
ppc_regs32.extend(pmr_regs)

#REG_OFFSET_TBR = len(ppc_regs)
REG_OFFSET_TBR = REG_OFFSET_SPR

# dynamically create REG_EAX and the like in our module
l = locals()
e_reg.addLocalEnums(l, ppc_regs)

# in order to make numbers work out the same, we translate bits differently from the manual
# the PPC Arch Ref Manual indicates the lower bits as 32-63.
ppc_meta32 = [
        ('SP', REG_R1, 0, 32),
        ('TOC', REG_R2, 0, 32),
        ('cr0', REG_CR, 60-32, 4),
        ('cr1', REG_CR, 60-36, 4),
        ('cr2', REG_CR, 60-40, 4),
        ('cr3', REG_CR, 60-44, 4),
        ('cr4', REG_CR, 60-48, 4),
        ('cr5', REG_CR, 60-52, 4),
        ('cr6', REG_CR, 60-56, 4),
        ('cr7', REG_CR, 60-60, 4),
        ('CA',  REG_XER, 63-34, 1),
        ('SO',  REG_XER, 63-32, 1),
        ('OV',  REG_XER, 63-33, 1),
]
ppc_meta64 = [
        ('SP', REG_R1, 0, 64),
        ('TOC', REG_R2, 0, 64),
        ('cr0', REG_CR, 60-32, 4),
        ('cr1', REG_CR, 60-36, 4),
        ('cr2', REG_CR, 60-40, 4),
        ('cr3', REG_CR, 60-44, 4),
        ('cr4', REG_CR, 60-48, 4),
        ('cr5', REG_CR, 60-52, 4),
        ('cr6', REG_CR, 60-56, 4),
        ('cr7', REG_CR, 60-60, 4),
        ('CA',  REG_XER, 63-34, 1),
        ('SO',  REG_XER, 63-32, 1),
        ('OV',  REG_XER, 63-33, 1),
]
REG_SP = REG_R1


statmetas = [   # FIXME
        ('CR0_LT', REG_CR, 63-32, 1, 'Less Than Flag'),
        ('CR0_GT', REG_CR, 63-33, 1, 'Greater Than Flag'),
        ('CR0_EQ', REG_CR, 63-34, 1, 'Equal to Flag'),
        ('CR0_SO', REG_CR, 63-35, 1, 'Summary Overflow Flag'),
        ('CR1_LT', REG_CR, 63-36, 1, 'Less Than Flag'),
        ('CR1_GT', REG_CR, 63-37, 1, 'Greater Than Flag'),
        ('CR1_EQ', REG_CR, 63-38, 1, 'Equal to Flag'),
        ('CR1_SO', REG_CR, 63-39, 1, 'Summary Overflow Flag'),
        ('CR2_LT', REG_CR, 63-40, 1, 'Less Than Flag'),
        ('CR2_GT', REG_CR, 63-41, 1, 'Greater Than Flag'),
        ('CR2_EQ', REG_CR, 63-42, 1, 'Equal to Flag'),
        ('CR2_SO', REG_CR, 63-43, 1, 'Summary Overflow Flag'),
        ('CR3_LT', REG_CR, 63-44, 1, 'Less Than Flag'),
        ('CR3_GT', REG_CR, 63-45, 1, 'Greater Than Flag'),
        ('CR3_EQ', REG_CR, 63-46, 1, 'Equal to Flag'),
        ('CR3_SO', REG_CR, 63-47, 1, 'Summary Overflow Flag'),
        ('CR4_LT', REG_CR, 63-48, 1, 'Less Than Flag'),
        ('CR4_GT', REG_CR, 63-49, 1, 'Greater Than Flag'),
        ('CR4_EQ', REG_CR, 63-50, 1, 'Equal to Flag'),
        ('CR4_SO', REG_CR, 63-51, 1, 'Summary Overflow Flag'),
        ('CR5_LT', REG_CR, 63-52, 1, 'Less Than Flag'),
        ('CR5_GT', REG_CR, 63-53, 1, 'Greater Than Flag'),
        ('CR5_EQ', REG_CR, 63-54, 1, 'Equal to Flag'),
        ('CR5_SO', REG_CR, 63-55, 1, 'Summary Overflow Flag'),
        ('CR6_LT', REG_CR, 63-56, 1, 'Less Than Flag'),
        ('CR6_GT', REG_CR, 63-57, 1, 'Greater Than Flag'),
        ('CR6_EQ', REG_CR, 63-58, 1, 'Equal to Flag'),
        ('CR6_SO', REG_CR, 63-59, 1, 'Summary Overflow Flag'),
        ('CR7_LT', REG_CR, 63-60, 1, 'Less Than Flag'),
        ('CR7_GT', REG_CR, 63-61, 1, 'Greater Than Flag'),
        ('CR7_EQ', REG_CR, 63-62, 1, 'Equal to Flag'),
        ('CR7_SO', REG_CR, 63-63, 1, 'Summary Overflow Flag'),

        ('SO',   REG_XER, 63-32, 1, 'Summary Overflow'),
        ('OV',   REG_XER, 63-33, 1, 'Overflow'),
        ('CA',   REG_XER, 63-34, 1, 'Carry'),

        ('FPSCR_FX',     REG_FPSCR, 63-32, 1, 'Floating-Point Exception Summary'),
        ('FPSCR_FEX',    REG_FPSCR, 63-33, 1, 'Floating-Point Enabled Exception Summary'),
        ('FPSCR_VX',     REG_FPSCR, 63-34, 1, 'Floating-Point Invalid Operation Exception Summary'),
        ('FPSCR_OX',     REG_FPSCR, 63-35, 1, 'Floating-Point Overflow Exception'),
        ('FPSCR_UX',     REG_FPSCR, 63-36, 1, 'Floating-Point Underflow Exception'),
        ('FPSCR_ZX',     REG_FPSCR, 63-37, 1, 'Floating-Point Zero Divide Exception'),
        ('FPSCR_XX',     REG_FPSCR, 63-38, 1, 'Floating-Point Inexact Exception'),
        ('FPSCR_VXSNAN', REG_FPSCR, 63-39, 1, 'Floating-Point Invalid Operation Exception (SNAN)'),
        ('FPSCR_VXISI',  REG_FPSCR, 63-40, 1, 'Floating-Point Invalid Operation Exception (∞ − ∞)'),
        ('FPSCR_VXIDI',  REG_FPSCR, 63-41, 1, 'Floating-Point Invalid Operation Exception (∞ ÷ ∞)'),
        ('FPSCR_VXZDZ',  REG_FPSCR, 63-42, 1, 'Floating-Point Invalid Operation Exception (0 ÷ 0)'),
        ('FPSCR_VXIMZ',  REG_FPSCR, 63-43, 1, 'Floating-Point Invalid Operation Exception (∞ × 0)'),
        ('FPSCR_VXVC',   REG_FPSCR, 63-44, 1, 'Floating-Point Invalid Operation Exception (invalid compare)'),
        ('FPSCR_FR',     REG_FPSCR, 63-45, 1, 'Floating-Point Fraction Rounded'),
        ('FPSCR_FI',     REG_FPSCR, 63-46, 1, 'Floating-Point Fraction Inexact'),
        ('FPSCR_FPRF',   REG_FPSCR, 63-46, 5, 'Floating-Point Results Flags'),
        ('FPSCR_C',      REG_FPSCR, 63-47, 1, 'Floating-Point Result Class Descriptor'),
        ('FPSCR_FPCC',   REG_FPSCR, 63-48, 4, 'Floating-Point Condition Code'),
        ('FPSCR_C_FPCC', REG_FPSCR, 63-47, 5, 'Floating-Point Result Class Descriptor and Condition Code'),
        ('FPCC_FL',      REG_FPSCR, 63-48, 1, 'Floating-Point Less Than or Negative'),
        ('FPCC_FG',      REG_FPSCR, 63-49, 1, 'Floating-Point Greater Than or Positive'),
        ('FPCC_FE',      REG_FPSCR, 63-50, 1, 'Floating-Point Equal or Zero'),
        ('FPCC_FU',      REG_FPSCR, 63-51, 1, 'Floating-Point Unordered or NaN'),
        ('FPSCR_VXSOFT', REG_FPSCR, 63-53, 1, 'Floating-Point Invalid Operation Exception (software request)'),
        ('FPSCR_VXSQRT', REG_FPSCR, 63-54, 1, 'Floating-Point Invalid Operation Exception (invalid square root)'),
        ('FPSCR_VXCVI',  REG_FPSCR, 63-55, 1, 'Floating-Point Invalid Operation Exception (invalid integer convert)'),
        ('FPSCR_VE',     REG_FPSCR, 63-56, 1, 'Floating-Point Invalid Operation Exception Enable'),
        ('FPSCR_OE',     REG_FPSCR, 63-57, 1, 'Floating-Point Overflow Exception Enable'),
        ('FPSCR_UE',     REG_FPSCR, 63-58, 1, 'Floating-Point Underflow Exception Enable'),
        ('FPSCR_ZE',     REG_FPSCR, 63-59, 1, 'Floating-Point Zero Divide Exception Enable'),
        ('FPSCR_XE',     REG_FPSCR, 63-60, 1, 'Floating-Point Inexact Exception Enable'),
        ('FPSCR_NI',     REG_FPSCR, 63-61, 1, 'Floating-Point non-IEEE Mode'),
        ('FPSCR_RN',     REG_FPSCR, 63-62, 2, 'Floating-Point Rounding Control'),

        ('MSR_CM',       REG_MSR, 63-32, 1, 'Computation Mode'),
        ('MSR_GS',       REG_MSR, 63-35, 1, 'Guest State'),
        ('MSR_UCLE',     REG_MSR, 63-37, 1, 'User-Mode Cache Lock Enable'),
        ('MSR_SPV',      REG_MSR, 63-38, 1, 'SP/Embedded Floating-Point/Vector Available'),
        ('MSR_WE',       REG_MSR, 63-45, 1, 'Wait State Enable'),
        ('MSR_CE',       REG_MSR, 63-46, 1, 'Critical Enable'),
        ('MSR_EE',       REG_MSR, 63-48, 1, 'External Enable'),
        ('MSR_PR',       REG_MSR, 63-49, 1, 'User Mode (problem State)'),
        ('MSR_FP',       REG_MSR, 63-50, 1, 'Floating-Point Available'),
        ('MSR_ME',       REG_MSR, 63-51, 1, 'Machine Check Enable'),
        ('MSR_FE0',      REG_MSR, 63-52, 1, 'Floating-Point Exception Mode 0'),
        ('MSR_DE',       REG_MSR, 63-54, 1, 'Debug Interrupt Enable'),
        ('MSR_FE1',      REG_MSR, 63-55, 1, 'Floating-Point Exception Mode 1'),
        ('MSR_IS',       REG_MSR, 63-58, 1, 'Instruction Address Space'),
        ('MSR_DS',       REG_MSR, 63-59, 1, 'Data Address Space'),
        ('MSR_PMM',      REG_MSR, 63-61, 1, 'Performance Monitor Mark'),
        ('MSR_RI',       REG_MSR, 63-62, 1, 'Recoverable Interrupt'),
]

def getCrFields(regval):
    ret = []
    for name,regval,shift,bits,desc in statmetas:
        ret.append( (name, regval >> shift & 1) )
    return ret

e_reg.addLocalStatusMetas(l, ppc_meta64, statmetas, 'REG_FIELD')
e_reg.addLocalMetas(l, ppc_meta64)

class Ppc32RegisterContext(e_reg.RegisterContext):
    def __init__(self):
        e_reg.RegisterContext.__init__(self)
        self.loadRegDef(ppc_regs32)
        self.loadRegMetas(ppc_meta32, statmetas=statmetas)
        self.setRegisterIndexes(REG_PC, REG_SP, srindex=REG_CR)

class Ppc64RegisterContext(e_reg.RegisterContext):
    def __init__(self):
        e_reg.RegisterContext.__init__(self)
        self.loadRegDef(ppc_regs64)
        self.loadRegMetas(ppc_meta64, statmetas=statmetas)
        self.setRegisterIndexes(REG_PC, REG_SP, srindex=REG_CR)



general_regs = []
general_regs.extend([reg for reg, size in gprs64])
general_regs.extend([reg for reg, size in floats])
general_regs.extend([reg for reg, size in vectors])
general_regs.append('LR')
general_regs.append('XER')
general_regs.append('CTR')
general_regs.extend([reg for reg, size in sysregs])


rctx32 = Ppc32RegisterContext()
rctx64 = Ppc64RegisterContext()


