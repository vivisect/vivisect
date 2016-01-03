from envi.archs.msp430.regs import *

checks = [
    # SUBC
    (
        'SUBC r14, r15 (C=0)',
        { 'regs': [(REG_R14, 0x3), (REG_R15, 0x5)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f7e", 'data': "" },
        { 'regs': [(REG_R14, 0x3), (REG_R15, 0x1)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "0f7e", 'data': "" }
    ),
    (
        'SUBC r14, r15 (C=1)',
        { 'regs': [(REG_R14, 0x3), (REG_R15, 0x5)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "0f7e", 'data': "" },
        { 'regs': [(REG_R14, 0x3), (REG_R15, 0x2)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "0f7e", 'data': "" }
    ),
    (
        'SUBC r14, r15 (destination zero)',
        { 'regs': [(REG_R14, 0x5), (REG_R15, 0x5)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "0f7e", 'data': "" },
        { 'regs': [(REG_R14, 0x5), (REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 1), (SR_V, 0)], 'code': "0f7e", 'data': "" }
    ),
    (
        'SUBC r14, r15 (destination carry + negative)',
        { 'regs': [(REG_R14, 0x5), (REG_R15, 0x3)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "0f7e", 'data': "" },
        { 'regs': [(REG_R14, 0x5), (REG_R15, 0xfffe)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f7e", 'data': "" }
    ),
    (
        'SUBC r14, r15 (destination overflow)',
        { 'regs': [(REG_R14, 0x2), (REG_R15, 0x8000)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "0f7e", 'data': "" },
        { 'regs': [(REG_R14, 0x2), (REG_R15, 0x7ffe)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 1)], 'code': "0f7e", 'data': "" }
    ),

    # SUBC.b
    (
        'SUBC.b r14, r15 (C=0)',
        { 'regs': [(REG_R14, 0x1103), (REG_R15, 0x1105)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f7e", 'data': "" },
        { 'regs': [(REG_R14, 0x1103), (REG_R15, 0x1)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "4f7e", 'data': "" }
    ),
    (
        'SUBC.b r14, r15 (C=1)',
        { 'regs': [(REG_R14, 0x1103), (REG_R15, 0x1105)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "4f7e", 'data': "" },
        { 'regs': [(REG_R14, 0x1103), (REG_R15, 0x2)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "4f7e", 'data': "" }
    ),
    (
        'SUBC.b r14, r15 (destination zero)',
        { 'regs': [(REG_R14, 0x1105), (REG_R15, 0x1105)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "4f7e", 'data': "" },
        { 'regs': [(REG_R14, 0x1105), (REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 1), (SR_V, 0)], 'code': "4f7e", 'data': "" }
    ),
    (
        'SUBC.b r14, r15 (destination carry + negative)',
        { 'regs': [(REG_R14, 0x1105), (REG_R15, 0x1103)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "4f7e", 'data': "" },
        { 'regs': [(REG_R14, 0x1105), (REG_R15, 0xfe)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f7e", 'data': "" }
    ),
    (
        'SUBC.b r14, r15 (destination overflow)',
        { 'regs': [(REG_R14, 0x1102), (REG_R15, 0x1180)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "4f7e", 'data': "" },
        { 'regs': [(REG_R14, 0x1102), (REG_R15, 0x7e)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 1)], 'code': "4f7e", 'data': "" }
    ),
]
