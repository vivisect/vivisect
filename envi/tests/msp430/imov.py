from envi.archs.msp430.regs import *

checks = [
    # MOV
    (
        'MOV r14, r15',
        { 'regs': [(REG_R14, 0x1122), (REG_R15, 0x3344)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f4e", 'data': "" },
        { 'regs': [(REG_R14, 0x1122), (REG_R15, 0x1122)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f4e", 'data': "" }
    ),

    # MOV.b
    (
        'MOV.b r14, r15',
        { 'regs': [(REG_R14, 0x1122), (REG_R15, 0x3344)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f4e", 'data': "" },
        { 'regs': [(REG_R14, 0x1122), (REG_R15, 0x22)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f4e", 'data': "" }
    ),
]
