from envi.archs.msp430.regs import *

checks = [
    # CMP
    (
        'CMP r14, r15 (src == dst)',
        { 'regs': [(REG_R14, 0xaaaa), (REG_R15, 0xaaaa)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f9e", 'data': "" },
        { 'regs': [(REG_R14, 0xaaaa), (REG_R15, 0xaaaa)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 1), (SR_V, 0)], 'code': "0f9e", 'data': "" }
    ),
    (
        'CMP r14, r15 (src < dst)',
        { 'regs': [(REG_R14, 0x3333), (REG_R15, 0x4444)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f9e", 'data': "" },
        { 'regs': [(REG_R14, 0x3333), (REG_R15, 0x4444)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "0f9e", 'data': "" },
    ),
    (
        'CMP r14, r15 (src < dst) result overflow',
        { 'regs': [(REG_R14, 0x1), (REG_R15, 0x8000)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f9e", 'data': "" },
        { 'regs': [(REG_R14, 0x1), (REG_R15, 0x8000)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 1)], 'code': "0f9e", 'data': "" }
    ),
    (
        'CMP r14, r15 (src > dst) result carry',
        { 'regs': [(REG_R14, 0xffff), (REG_R15, 0x3333)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f9e", 'data': "" },
        { 'regs': [(REG_R14, 0xffff), (REG_R15, 0x3333)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f9e", 'data': "" }
    ),
    (
        'CMP r14, r15 (src > dst) result negative + carry + overflow',
        { 'regs': [(REG_R14, 0xffff), (REG_R15, 0x7fff)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f9e", 'data': "" },
        { 'regs': [(REG_R14, 0xffff), (REG_R15, 0x7fff)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 1)], 'code': "0f9e", 'data': "" }
    ),

    # CMP.b
    (
        'CMP.b r14, r15 (src == dst)',
        { 'regs': [(REG_R14, 0x11aa), (REG_R15, 0x12aa)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f9e", 'data': "" },
        { 'regs': [(REG_R14, 0x11aa), (REG_R15, 0x12aa)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 1), (SR_V, 0)], 'code': "4f9e", 'data': "" }
    ),
    (
        'CMP.b r14, r15 (src < dst)',
        { 'regs': [(REG_R14, 0x1133), (REG_R15, 0x0044)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f9e", 'data': "" },
        { 'regs': [(REG_R14, 0x1133), (REG_R15, 0x0044)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "4f9e", 'data': "" },
    ),
    (
        'CMP.b r14, r15 (src < dst) result overflow',
        { 'regs': [(REG_R14, 0x1101), (REG_R15, 0x0080)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f9e", 'data': "" },
        { 'regs': [(REG_R14, 0x1101), (REG_R15, 0x0080)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 1)], 'code': "4f9e", 'data': "" }
    ),
    (
        'CMP.b r14, r15 (src > dst) result carry',
        { 'regs': [(REG_R14, 0x00ff), (REG_R15, 0x1133)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f9e", 'data': "" },
        { 'regs': [(REG_R14, 0x00ff), (REG_R15, 0x1133)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f9e", 'data': "" }
    ),
    (
        'CMP.b r14, r15 (src > dst) result negative + carry + overflow',
        { 'regs': [(REG_R14, 0x00ff), (REG_R15, 0x117f)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f9e", 'data': "" },
        { 'regs': [(REG_R14, 0x00ff), (REG_R15, 0x117f)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 1)], 'code': "4f9e", 'data': "" }
    ),
]
