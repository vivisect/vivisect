from envi.archs.msp430.regs import *

checks = [
    # RET
    (
        'RET',
        { 'regs': [(REG_SP, 0x1000)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "3041", 'data': "11223344" },
        { 'regs': [(REG_SP, 0x1002), (REG_PC, 0x2211)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "3041", 'data': "11223344" }
    ),
]
