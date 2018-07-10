
"""
Home of the PowerPC module's register specs/code.
"""
import envi.registers as e_reg

gprs = [('r%s' % x, 32)  for x in range(32)]
floats = [('f%s' % x, 64)  for x in range(32)]

sysregs = (
        ('xer', 64),
        ('acc', 64), 
        ('fpscr', 64),
        ('lr', 64),
        ('cr', 32),
        ('msr', 64),
        ('bucsr', 64),
        ('ctr', 64), 
        ('pc', 32),

        )

ppc_regs = []
ppc_regs.extend(gprs)
ppc_regs.extend(sysregs)
ppc_regs.extend(floats)

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
        
