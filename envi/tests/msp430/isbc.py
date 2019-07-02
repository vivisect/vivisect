from envi.archs.msp430.regs import *

checks = [
    # SBC
    (
        'SBC r15 (C=0)',
        { 'regs': [(REG_R15, 0x2)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f73", 'data': "" },
        { 'regs': [(REG_R15, 0x1)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "0f73", 'data': "" }
    ),
    (
        'SBC r15 (C=1)',
        { 'regs': [(REG_R15, 0x2)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "0f73", 'data': "" },
        { 'regs': [(REG_R15, 0x2)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "0f73", 'data': "" }
    ),
    (
        'SBC r15 (destination zero)',
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "0f73", 'data': "" },
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 1), (SR_V, 0)], 'code': "0f73", 'data': "" }
    ),
    (
        'SBC r15 (destination overflow)',
        { 'regs': [(REG_R15, 0x8000)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f73", 'data': "" },
        { 'regs': [(REG_R15, 0x7fff)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 1)], 'code': "0f73", 'data': "" }
    ),
    (
        'SBC r15 (destination carry + negative)',
        { 'regs': [(REG_R15, 0x0000)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f73", 'data': "" },
        { 'regs': [(REG_R15, 0xffff)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f73", 'data': "" }
    ),

    # SBC.b
    (
        'SBC.b r15 (C=0)',
        { 'regs': [(REG_R15, 0x1102)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f73", 'data': "" },
        { 'regs': [(REG_R15, 0x1)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "4f73", 'data': "" }
    ),
    (
        'SBC.b r15 (C=1)',
        { 'regs': [(REG_R15, 0x1102)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "4f73", 'data': "" },
        { 'regs': [(REG_R15, 0x2)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "4f73", 'data': "" }
    ),
    (
        'SBC.b r15 (destination zero)',
        { 'regs': [(REG_R15, 0x1100)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "4f73", 'data': "" },
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 1), (SR_V, 0)], 'code': "4f73", 'data': "" }
    ),
    (
        'SBC.b r15 (destination overflow)',
        { 'regs': [(REG_R15, 0x1180)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f73", 'data': "" },
        { 'regs': [(REG_R15, 0x7f)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 1)], 'code': "4f73", 'data': "" }
    ),
    (
        'SBC.b r15 (destination carry + negative)',
        { 'regs': [(REG_R15, 0x1100)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f73", 'data': "" },
        { 'regs': [(REG_R15, 0xff)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f73", 'data': "" }
    ),
]
