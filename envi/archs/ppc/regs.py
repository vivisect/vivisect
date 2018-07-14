
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
        ('xer', 64),
        ('acc', 64), 
        ('lr', 64),
        ('cr', 32),
        ('msr', 64),
        ('bucsr', 64),
        ('msrp', 64),
        ('epcr', 64),
        ('hid0', 64),
        ('hid1', 64),
        ('pir', 64),
        ('pvr', 64),
        ('svr', 64),
        ('cvr', 64),
        ('gpir', 64),
        ('tmcfg0', 64),
        ('imsr0', 64),
        ('tpri0', 64),
        ('tir', 64),
        ('ten', 64),
        ('tens', 64),
        ('tenc', 64),
        ('tensr', 64),
        ('sccsrbar', 64),
        ('ppr32', 64),
        ('ctr', 64), 
        ('pc', 32),
        )

ppc_regs = []
ppc_regs.extend(gprs)
REG_IDX_FP = len(ppc_regs)
ppc_regs.extend(floats)
REG_IDX_VECTOR = len(ppc_regs)
ppc_regs.extend(vectors)

ppc_regs.extend(sysregs)

# dynamically create REG_EAX and the like in our module
l = locals()
e_reg.addLocalEnums(l, ppc_regs)

ppc_meta = [ 
        ('sp', REG_R1, 0, 32),
        ('toc', REG_R2, 0, 32),
]
REG_SP = REG_R1


statmetas = [   # FIXME
        ('CF', REG_CR, 0, 1, 'Carry Flag'),
        ('PF', REG_CR, 2, 1, 'Parity Flag'),
        ('AF', REG_CR, 4, 1, 'Adjust Flag'),
        ('ZF', REG_CR, 6, 1, 'Zero Flag'),
        ('SF', REG_CR, 7, 1, 'Sign Flag'),
        ('TF', REG_CR, 8, 1, 'Trap Flag'),
        ('IF', REG_CR, 9, 1, 'Interrupt Enable Flag'),
        ('DF', REG_CR, 10, 1, 'Direction Flag'),
        ('OF', REG_CR, 11, 1, 'Overflow Flag'),
        ]


def getCrFields(regval):
    ret = []
    for name,regval,shift,bits,desc in statmetas:
        ret.append( (name, regval >> shift & 1) )
    return ret

e_reg.addLocalStatusMetas(l, ppc_meta, statmetas, 'FLAGS')
#e_reg.addLocalMetas(l, ppc_meta)

class PpcRegisterContext(e_reg.RegisterContext):
    def __init__(self):
        e_reg.RegisterContext.__init__(self)
        self.loadRegDef(ppc_regs)
        self.loadRegMetas(ppc_meta, statmetas=statmetas)
        self.setRegisterIndexes(REG_PC, REG_SP, srindex=REG_CR)
 

