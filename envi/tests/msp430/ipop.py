from envi.archs.msp430.regs import *

checks = [
    # POP
    (
        'POP R15',
        { 'regs': [(REG_SP, 0x1000)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "3f41", 'data': "11223344" },
        { 'regs': [(REG_SP, 0x1002), (REG_R15, 0x2211)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "3f41", 'data': "11223344" }
    ),

    # POP.b
    (
        'POP.b R15',
        { 'regs': [(REG_SP, 0x1000)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "7f41", 'data': "11223344" },
        { 'regs': [(REG_SP, 0x1002), (REG_R15, 0x11)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "7f41", 'data': "11223344" }
    ),
]
