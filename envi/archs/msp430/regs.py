import envi.registers as e_reg

from envi.archs.msp430.const import *

registers = [
    'pc','sp','sr','cg','r4','r5','r6','r7',
    'r8','r9','r10','r11','r12','r13','r14','r15'
]

registers_info = [ (reg, 16) for reg in registers ]

l = locals()
e_reg.addLocalEnums(l, registers_info)

registers_meta = [
    ("r0", REG_PC, 0, 16),
    ("r1", REG_SP, 0, 16),
    ("r2", REG_SR, 0, 16),
    ("r3", REG_CG, 0, 16),
]

status_meta = [
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

e_reg.addLocalStatusMetas(l, registers_meta, status_meta, 'SR')
e_reg.addLocalMetas(l, registers_meta)

class Msp430RegisterContext(e_reg.RegisterContext):
    def __init__(self):
        e_reg.RegisterContext.__init__(self)
        self.loadRegDef(registers_info)
        self.loadRegMetas([], statmetas=status_meta)
        self.setRegisterIndexes(REG_PC, REG_SP, srindex=REG_SR)
