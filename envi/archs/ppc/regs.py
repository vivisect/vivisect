
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

import spr
# populate spr_regs from the PPC SPR register list (in spr.py)
spr_regs = [('%#x' % x, 64) for x in range(1024)]
for sprnum, (rname, rdesc, bitsz) in spr.sprs.items():
    spr_regs[sprnum] = (rname, bitsz)

sprnames = {x:y.lower() for x,(y,z,b) in spr.sprs.items()}

REG_OFFSET_SPR = len(ppc_regs)
ppc_regs64.extend(spr_regs)
ppc_regs32.extend(spr_regs)

tmr_regs = [
        ('tmcfg0', 64),
        ]
tmr_regs.extend([('tpri%d' % x, 64) for x in range(32)]) 
tmr_regs.extend([('imsr%d' % x, 64) for x in range(32)]) 
tmr_regs.extend([('inia%d' % x, 64) for x in range(32)]) 

REG_OFFSET_TMR = len(ppc_regs)
ppc_regs64.extend(tmr_regs)
ppc_regs32.extend(tmr_regs)

REG_OFFSET_DCR = len(ppc_regs)
ppc_regs64.extend([('dcr%d' % x, 64) for x in range(32)]) 
ppc_regs32.extend([('dcr%d' % x, 64) for x in range(32)]) 

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

        ('SO64', REG_XER, 63-61, 1, 'Summary Overflow 64'),
        ('OV64', REG_XER, 63-62, 1, 'Overflow 64'),
        ('CA64', REG_XER, 63-63, 1, 'Carry 64'),
        ('SO',   REG_XER, 63-32, 1, 'Summary Overflow'),
        ('OV',   REG_XER, 63-33, 1, 'Overflow'),
        ('CA',   REG_XER, 63-34, 1, 'Carry'),

        ]
# FIXME: FPSCR bits

def getCrFields(regval):
    ret = []
    for name,regval,shift,bits,desc in statmetas:
        ret.append( (name, regval >> shift & 1) )
    return ret

e_reg.addLocalStatusMetas(l, ppc_meta64, statmetas, 'FLAGS')
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
general_regs.extend(gprs64)
general_regs.extend(floats)
general_regs.extend(vectors)
general_regs.extend(sysregs)
general_regs.append(('LR', 64))

