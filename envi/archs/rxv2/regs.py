import envi.registers as e_reg

from envi.archs.rxv2.const import *

regs32 = [
    'sp','r1','r2','r3','r4','r5','r6','r7',
    'r8','r9','r10','r11','r12','r13','r14','r15',
    'isp','usp','intb','pc','psw','bpc','bpsw','fintv','fpdw','extb',
]

regs_acc = [ 'acc0', 'acc1' ]

registers_info = []
registers_info.extend([(r, 32) for r in regs32])
registers_info.extend([(r, 72) for r in regs_acc])

l = locals()
e_reg.addLocalEnums(l, registers_info)

registers_meta = [
    ("r0", REG_PC, 0, 32),
]

status_meta = [
    ('C',       REG_PSW, 0, 1, 'Carry Flag'),
    ('Z',       REG_PSW, 1, 1, 'Zero Flag'),
    ('S',       REG_PSW, 2, 1, 'Sign Flag'),
    ('O',       REG_PSW, 3, 1, 'Overflow Flag'),
    ('I',       REG_PSW, 16, 1, 'Interrupt Enable Flag'),
    ('U',       REG_PSW, 17, 1, 'Stack pointer select Flag'),
    ('PM',      REG_PSW, 20, 1, 'Processor mode select Flag'),
    ('IPL',     REG_PSW, 24, 4, 'Processor Interrupt Priority Flag'),
    ('RM',      REG_FPSW, 0, 2, 'Floating Point Rounding Mode Flag'),
    ('CV',      REG_FPSW, 2, 1, 'Invalid Operation Cause Flag'),
    ('CO',      REG_FPSW, 3, 1, 'Overflow Flag'),
    ('CZ',      REG_FPSW, 4, 1, 'Division By Zero Flag'),
    ('CU',      REG_FPSW, 5, 1, 'Underflow Cause Flag'),
    ('CX',      REG_FPSW, 6, 1, 'Inexact Cause Flag'),
    ('CE',      REG_FPSW, 7, 1, 'Unimplemented Processing Cause Flag'),
    ('DN',      REG_FPSW, 8, 1, '0 Flusb bit of denormalized number'),
    ('EV',      REG_FPSW, 10, 1, 'Invalid operation exception Enable Flag'),
    ('EO',      REG_FPSW, 11, 1, 'Overflow Exception Enable Flag'),
    ('EZ',      REG_FPSW, 12, 1, 'Division-by-Zero Enable Flag'),
    ('EU',      REG_FPSW, 13, 1, 'Underflow Exception Enable Flag'),
    ('EX',      REG_FPSW, 14, 1, 'Inexact Exception Enable Flag'),
    ('FV',      REG_FPSW, 26, 1, 'Invalid Operation Flag'),
    ('FO',      REG_FPSW, 27, 1, 'Overflow Flag'),
    ('FZ',      REG_FPSW, 28, 1, 'Division By Zero Flag'),
    ('FU',      REG_FPSW, 29, 1, 'Underflow Flag'),
    ('FX',      REG_FPSW, 30, 1, 'Inexact Flag'),
    ('FS',      REG_FPSW, 31, 1, 'Floating-point error summary Flag'),
]

e_reg.addLocalStatusMetas(l, registers_meta, status_meta, 'SR')
e_reg.addLocalMetas(l, registers_meta)

class RXv2RegisterContext(e_reg.RegisterContext):
    def __init__(self):
        e_reg.RegisterContext.__init__(self)
        self.loadRegDef(registers_info)
        self.loadRegMetas([], statmetas=status_meta)
        self.setRegisterIndexes(REG_PC, REG_SP, srindex=REG_SR)

rctx = RXv2RegisterContext()
