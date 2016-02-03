from envi.archs.msp430.regs import *

checks = [
    # RRA
    (
        'RRA r15 (destination carry)',
        { 'regs': [(REG_R15, 0x5555)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "0f11", 'data': "" },
        { 'regs': [(REG_R15, 0x2aaa)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "0f11", 'data': "" }
    ),
    (
        'RRA r15 (destination zero + carry)',
        { 'regs': [(REG_R15, 0x1)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f11", 'data': "" },
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 1), (SR_V, 0)], 'code': "0f11", 'data': "" }
    ),
    (
        'RRA r15 (destination negative)',
        { 'regs': [(REG_R15, 0x8000)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f11", 'data': "" },
        { 'regs': [(REG_R15, 0xc000)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f11", 'data': "" }
    ),

    # RRA.b
    (
        'RRA.b r15 (destination carry)',
        { 'regs': [(REG_R15, 0x1155)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "4f11", 'data': "" },
        { 'regs': [(REG_R15, 0x2a)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "4f11", 'data': "" }
    ),
    (
        'RRA.b r15 (destination zero + carry)',
        { 'regs': [(REG_R15, 0x1)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f11", 'data': "" },
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 1), (SR_V, 0)], 'code': "4f11", 'data': "" }
    ),
    (
        'RRA.b r15 (destination negative)',
        { 'regs': [(REG_R15, 0x1180)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f11", 'data': "" },
        { 'regs': [(REG_R15, 0xc0)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f11", 'data': "" }
    ),
]
