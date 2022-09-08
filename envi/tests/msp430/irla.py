from envi.archs.msp430.regs import *

checks = [
    # RLA
    (
        'RLA r15 (destination negative + overflow)',
        { 'regs': [(REG_R15, 0x5555)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f5f", 'data': "" },
        { 'regs': [(REG_R15, 0xaaaa)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 1)], 'code': "0f5f", 'data': "" }
    ),
    (
        'RLA r15 (destination carry + zero + overflow)',
        { 'regs': [(REG_R15, 0x8000)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f5f", 'data': "" },
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 1), (SR_V, 1)], 'code': "0f5f", 'data': "" }
    ),
    (
        'RLA r15 (destination negative + overflow)',
        { 'regs': [(REG_R15, 0x4000)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f5f", 'data': "" },
        { 'regs': [(REG_R15, 0x8000)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 1)], 'code': "0f5f", 'data': "" }
    ),
    (
        'RLA r15 (destination negative + carry)',
        { 'regs': [(REG_R15, 0xc000)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f5f", 'data': "" },
        { 'regs': [(REG_R15, 0x8000)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "0f5f", 'data': "" }
    ),

    # RLA.b
    (
        'RLA.b r15 (destination negative + overflow)',
        { 'regs': [(REG_R15, 0x1155)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f5f", 'data': "" },
        { 'regs': [(REG_R15, 0xaa)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 1)], 'code': "4f5f", 'data': "" }
    ),
    (
        'RLA.b r15 (destination carry + zero + overflow)',
        { 'regs': [(REG_R15, 0x1180)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f5f", 'data': "" },
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 1), (SR_V, 1)], 'code': "4f5f", 'data': "" }
    ),
    (
        'RLA.b r15 (destination negative + overflow)',
        { 'regs': [(REG_R15, 0x1140)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f5f", 'data': "" },
        { 'regs': [(REG_R15, 0x80)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 1)], 'code': "4f5f", 'data': "" }
    ),
    (
        'RLA.b r15 (destination negative + carry)',
        { 'regs': [(REG_R15, 0x11c0)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f5f", 'data': "" },
        { 'regs': [(REG_R15, 0x80)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "4f5f", 'data': "" }
    ),
]
