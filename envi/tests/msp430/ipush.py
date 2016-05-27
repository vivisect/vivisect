from envi.archs.msp430.regs import *

checks = [
    # PUSH
    (
        'PUSH R15',
        { 'regs': [(REG_SP, 0x1004), (REG_R15, 0xaabb)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f12", 'data': "112233445566" },
        { 'regs': [(REG_SP, 0x1002), (REG_R15, 0xaabb)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f12", 'data': "1122bbaa5566" }
    ),

    # PUSH.b
    (
        'PUSH.b R15',
        { 'regs': [(REG_SP, 0x1004), (REG_R15, 0xaabb)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f12", 'data': "112233445566" },
        { 'regs': [(REG_SP, 0x1002), (REG_R15, 0xaabb)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f12", 'data': "1122bb445566" }
    ),
]
