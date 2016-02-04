from envi.archs.msp430.regs import *

checks = [
    # XOR
    (
        'XOR R14, R15 (destination negative + carry)',
        { 'regs': [(REG_R14, 0xffff), (REG_R15, 0x5555)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 1)], 'code': "0fee", 'data': "" },
        { 'regs': [(REG_R14, 0xffff), (REG_R15, 0xaaaa)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "0fee", 'data': "" }
    ),
    (
        'XOR R14, R15 (destination zero)',
        { 'regs': [(REG_R14, 0x5555), (REG_R15, 0x5555)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 1)], 'code': "0fee", 'data': "" },
        { 'regs': [(REG_R14, 0x5555), (REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 0), (SR_V, 0)], 'code': "0fee", 'data': "" }
    ),
    (
        'XOR R14, R15 (carry + overflow)',
        { 'regs': [(REG_R14, 0x8000), (REG_R15, 0x8001)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 1)], 'code': "0fee", 'data': "" },
        { 'regs': [(REG_R14, 0x8000), (REG_R15, 0x0001)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 1)], 'code': "0fee", 'data': "" }
    ),

    # XOR
    (
        'XOR.b R14, R15 (destination negative + carry)',
        { 'regs': [(REG_R14, 0xffff), (REG_R15, 0x5555)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 1)], 'code': "4fee", 'data': "" },
        { 'regs': [(REG_R14, 0xffff), (REG_R15, 0x00aa)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "4fee", 'data': "" }
    ),
    (
        'XOR.b R14, R15 (destination zero)',
        { 'regs': [(REG_R14, 0x1155), (REG_R15, 0x2255)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 1)], 'code': "4fee", 'data': "" },
        { 'regs': [(REG_R14, 0x1155), (REG_R15, 0x0000)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 0), (SR_V, 0)], 'code': "4fee", 'data': "" }
    ),
    (
        'XOR.b R14, R15 (carry + overflow)',
        { 'regs': [(REG_R14, 0x1180), (REG_R15, 0x1181)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 1)], 'code': "4fee", 'data': "" },
        { 'regs': [(REG_R14, 0x1180), (REG_R15, 0x0001)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 1)], 'code': "4fee", 'data': "" }
    ),
]
