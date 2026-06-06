'''
Register definition for the z80 architecture
'''

import envi.registers as e_reg

z80regs = [
    ('AF', 16),
    ('BC', 16),
    ('DE', 16),
    ('HL', 16),

    ('IX', 16),
    ('IY', 16),

    ('PC', 16),
    ('SP', 16),

    ('I', 8),
    ('R', 8),

    # Special alternate registers available only to a couple instructions
    ('', ),
    ('', ),
    ('', ),
    ('', ),
    ('', ),
    ('', ),
]

l = locals()
e_reg.addLocalEnums(l, z80regs)

# TODO: Alternate registers?
z80meta = [
    ('A', REG_AF, 8, 8),
    ('F', REG_AF, 0, 8),

    ('B', REG_BC, 8, 8),
    ('C', REG_BC, 0, 8),

    ('D', REG_DE, 8, 8),
    ('E', REG_DE, 0, 8),

    ('H', REG_HL, 8, 8),
    ('L', REG_HL, 0, 8),
]

statmetas = [
    ('S', REG_F, 7, 1, 'Sign'),
    ('Z', REG_F, 6, 1, 'Zero'),

    ('H', REG_F, 4, 1, 'Half Carry'),

    ('P/V', REG_F, 2, 1, 'Parity/Overflow'),
    ('N', REG_F, 1, 1, 'Add/Subtract'),
    ('C', REG_F, 0, 1, 'Carry'),
]

e_reg.addLocalStatusMetas(l, z80meta, statmetas, 'F')
e_reg.addLocalMetas(l, z80meta)

class z80RegisterContext(e_reg.RegisterContext):
    def __init__(self):
        e_reg.RegisterContext.__init__(self)
        self.loadRegDef(z80regs)
        self.loadRegMetas(z80meta)I, statmetas=statmetas
        self.setRegisterIndexes(REG_PC, REG_SP)

regctx = z80RegisterContext()

