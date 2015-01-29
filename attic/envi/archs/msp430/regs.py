import envi.registers as e_reg

from const import *
# Registers 
# There are 16 registers, the first four are the
# primary functional registers but they are simply
# referred to in the same manner as the other registers
#'PC',   # reg0 is the Program Counter
#'SP',   # reg1 is the Stack Pointer
#'SR',   # reg2 is the Status Register
#'CG',   # reg3 is the Constant Generator

registers = [
    'r0','r1','r2','r3','r4','r5','r6','r7',
    'r8','r9','r10','r11','r12','r13','r14','r15'
]

priregisters = [
    'pc','sp','sr','cg','r4','r5','r6','r7',
    'r8','r9','r10','r11','r12','r13','r14','r15'
]

reginfo = [ (reg, 16) for reg in priregisters ]

GeneralRegGroup = ('general', priregisters, )


metaregs = [ (registers[x], x, 0, 16) for x in range(len(registers)) ]

statmetas = [
        ('C',       REG_SR, 0, 1, 'Carry Flag'),
        ('Z',       REG_SR, 1, 1, 'Zero Flag'),
        ('N',       REG_SR, 2, 1, 'Negative (Sign) Flag'),
        ('GIE',     REG_SR, 3, 1, 'General Interrupt Enable Flag'),
        ('CPUOFF',  REG_SR, 4, 1, 'CPU Off Flag'),
        ('OSCOFF',  REG_SR, 5, 1, 'Oscillator Off Flag'),
        ('SCG0',    REG_SR, 6, 1, 'System Clock Generator 0 Off Flag'),
        ('SCG1',    REG_SR, 7, 1, 'System Clock Generotor 1 Off Flag'),
        ('V',       REG_SR, 8, 1, 'Overflow Flag'),
        ]

l = locals()
e_reg.addLocalEnums(l, reginfo)

e_reg.addLocalStatusMetas(l, priregisters, statmetas, 'SR')
#e_reg.addLocalMetas(l, i386meta)

class Msp430RegisterContext(e_reg.RegisterContext):
    def __init__(self):
        e_reg.RegisterContext.__init__(self)
        self.loadRegDef(reginfo)
        self.loadRegMetas(metaregs, statmetas=statmetas)
        self.setRegisterIndexes(REG_PC, REG_SP, srindex=REG_SR)
