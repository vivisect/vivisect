
"""
Home of the PowerPC module's register specs/code.
"""
import envi.registers as e_reg

gprs = [('r%s' % x, 32)  for x in range(32)]
floats = [('f%s' % x, 64)  for x in range(32)]
floats.append( ('fpscr', 64) )
vectors = [('v%s' % x, 64)  for x in range(32)]
vectors.append( ('vscr', 64) )

sysregs = (
        #('xer', 64),
        ('acc', 64), 
        #('lr', 64),
        ('cr', 32),
        ('msr', 64),
        #('bucsr', 64),
        #('msrp', 64),
        #('epcr', 64),
        #('hid0', 64),
        #('hid1', 64),
        #('pir', 64),
        #('pvr', 64),
        #('svr', 64),
        #('cvr', 64),
        #('gpir', 64),
        ('tmcfg0', 64),
        ('imsr0', 64),
        ('tpri0', 64),
        #('tir', 64),
        ('ten', 64),
        #('tens', 64),
        #('tenc', 64),
        #('tensr', 64),
        #('sccsrbar', 64),
        #('ppr32', 64),
        #('ctr', 64), 
        ('pc', 32),
        )

ppc_regs = []
ppc_regs.extend(gprs)

REG_OFFSET = len(ppc_regs)
ppc_regs.extend(floats)

REG_OFFSET = len(ppc_regs)
ppc_regs.extend(vectors)

REG_OFFSET = len(ppc_regs)
ppc_regs.extend(sysregs)

import spr
spr_regs = [(rname, bitsz) for sprnum, (rname, rdesc, bitsz) in spr.sprs.items()]
ppc_regs.extend(spr_regs)

# dynamically create REG_EAX and the like in our module
l = locals()
e_reg.addLocalEnums(l, ppc_regs)

ppc_meta = [ 
        ('sp', REG_R1, 0, 32),
        ('toc', REG_R2, 0, 32),
        ('cr0', REG_CR, 32, 4),
        ('cr1', REG_CR, 36, 4),
        ('cr2', REG_CR, 40, 4),
        ('cr3', REG_CR, 44, 4),
        ('cr4', REG_CR, 48, 4),
        ('cr5', REG_CR, 52, 4),
        ('cr6', REG_CR, 56, 4),
        ('cr7', REG_CR, 60, 4),
]
REG_SP = REG_R1


statmetas = [   # FIXME
        ('LT', REG_CR, 32, 1, 'Less Than Flag'),
        ('GT', REG_CR, 33, 1, 'Greater Than Flag'),
        ('EQ', REG_CR, 34, 1, 'Equal to Flag'),
        ('SO', REG_CR, 35, 1, 'Summary Overflow Flag'),
        ('CR1_LT', REG_CR, 36, 1, 'Less Than Flag'),
        ('CR1_GT', REG_CR, 37, 1, 'Greater Than Flag'),
        ('CR1_EQ', REG_CR, 38, 1, 'Equal to Flag'),
        ('CR1_SO', REG_CR, 39, 1, 'Summary Overflow Flag'),
        ('CR2_LT', REG_CR, 40, 1, 'Less Than Flag'),
        ('CR2_GT', REG_CR, 41, 1, 'Greater Than Flag'),
        ('CR2_EQ', REG_CR, 42, 1, 'Equal to Flag'),
        ('CR2_SO', REG_CR, 43, 1, 'Summary Overflow Flag'),
        ('CR3_LT', REG_CR, 44, 1, 'Less Than Flag'),
        ('CR3_GT', REG_CR, 45, 1, 'Greater Than Flag'),
        ('CR3_EQ', REG_CR, 46, 1, 'Equal to Flag'),
        ('CR3_SO', REG_CR, 47, 1, 'Summary Overflow Flag'),
        ('CR4_LT', REG_CR, 48, 1, 'Less Than Flag'),
        ('CR4_GT', REG_CR, 49, 1, 'Greater Than Flag'),
        ('CR4_EQ', REG_CR, 50, 1, 'Equal to Flag'),
        ('CR4_SO', REG_CR, 51, 1, 'Summary Overflow Flag'),
        ('CR5_LT', REG_CR, 52, 1, 'Less Than Flag'),
        ('CR5_GT', REG_CR, 53, 1, 'Greater Than Flag'),
        ('CR5_EQ', REG_CR, 54, 1, 'Equal to Flag'),
        ('CR5_SO', REG_CR, 55, 1, 'Summary Overflow Flag'),
        ('CR6_LT', REG_CR, 56, 1, 'Less Than Flag'),
        ('CR6_GT', REG_CR, 57, 1, 'Greater Than Flag'),
        ('CR6_EQ', REG_CR, 58, 1, 'Equal to Flag'),
        ('CR6_SO', REG_CR, 59, 1, 'Summary Overflow Flag'),
        ('CR7_LT', REG_CR, 60, 1, 'Less Than Flag'),
        ('CR7_GT', REG_CR, 61, 1, 'Greater Than Flag'),
        ('CR7_EQ', REG_CR, 62, 1, 'Equal to Flag'),
        ('CR7_SO', REG_CR, 63, 1, 'Summary Overflow Flag'),
        ]
# FIXME: FPSCR bits
# FIXME: CR bits!


def getCrFields(regval):
    ret = []
    for name,regval,shift,bits,desc in statmetas:
        ret.append( (name, regval >> shift & 1) )
    return ret

e_reg.addLocalStatusMetas(l, ppc_meta, statmetas, 'FLAGS')
e_reg.addLocalMetas(l, ppc_meta)

class PpcRegisterContext(e_reg.RegisterContext):
    def __init__(self):
        e_reg.RegisterContext.__init__(self)
        self.loadRegDef(ppc_regs)
        self.loadRegMetas(ppc_meta, statmetas=statmetas)
        self.setRegisterIndexes(REG_PC, REG_SP, srindex=REG_CR)
 

import spr
sprnames = {x:y.lower() for x,(y,z,b) in spr.sprs.items()}
