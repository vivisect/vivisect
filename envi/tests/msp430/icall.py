from envi.archs.msp430.regs import *

checks = [
    # CALL
    (
        'CALL #0x4412',
        { 'regs': [(REG_SP, 0x1002)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "b0121244", 'data': "00001122" },
        { 'regs': [(REG_PC, 0x4412), (REG_SP, 0x1000)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "b0121244", 'data': "04441122" }
    ),
]
