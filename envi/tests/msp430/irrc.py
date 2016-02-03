from envi.archs.msp430.regs import *

checks = [
    # RRC
    (
        'RRC r15 (destination carry + negative)',
        { 'regs': [(REG_R15, 0x5555)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "0f10", 'data': "" },
        { 'regs': [(REG_R15, 0xaaaa)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "0f10", 'data': "" }
    ),
    (
        'RRC r15 (destination zero + carry)',
        { 'regs': [(REG_R15, 0x1)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f10", 'data': "" },
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 1), (SR_V, 0)], 'code': "0f10", 'data': "" }
    ),
    (
        'RRC r15 (destination negative)',
        { 'regs': [(REG_R15, 0x8000)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f10", 'data': "" },
        { 'regs': [(REG_R15, 0x4000)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f10", 'data': "" }
    ),

    # RRC.b
    (
        'RRC.b r15 (destination carry)',
        { 'regs': [(REG_R15, 0x1155)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "4f10", 'data': "" },
        { 'regs': [(REG_R15, 0xaa)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "4f10", 'data': "" }
    ),
    (
        'RRC.b r15 (destination zero + carry)',
        { 'regs': [(REG_R15, 0x1)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f10", 'data': "" },
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 1), (SR_V, 0)], 'code': "4f10", 'data': "" }
    ),
    (
        'RRC.b r15 (destination negative)',
        { 'regs': [(REG_R15, 0x1180)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f10", 'data': "" },
        { 'regs': [(REG_R15, 0x40)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f10", 'data': "" }
    ),
]
