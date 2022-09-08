from envi.archs.msp430.regs import *

checks = [
    # DADD
    (
        'DADD r14, r15',
        { 'regs': [(REG_R14, 0x1), (REG_R15, 0x2)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0fae", 'data': "" },
        { 'regs': [(REG_R14, 0x1), (REG_R15, 0x3)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0fae", 'data': "" }
    ),
    (
        'DADD r14, r15 (destination zero)',
        { 'regs': [(REG_R14, 0x0), (REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0fae", 'data': "" },
        { 'regs': [(REG_R14, 0x0), (REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 0), (SR_V, 0)], 'code': "0fae", 'data': "" }
    ),
    (
        'DADD r14, r15 (destination zero + carry)',
        { 'regs': [(REG_R14, 0x1), (REG_R15, 0x9999)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "0fae", 'data': "" },
        { 'regs': [(REG_R14, 0x1), (REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 1), (SR_V, 0)], 'code': "0fae", 'data': "" }
    ),
    (
        'DADD r14, r15 (destination negative)',
        { 'regs': [(REG_R14, 0x1), (REG_R15, 0x7999)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "0fae", 'data': "" },
        { 'regs': [(REG_R14, 0x1), (REG_R15, 0x8000)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0fae", 'data': "" }
    ),

    # DADD.b
    (
        'DADD.b r14, r15',
        { 'regs': [(REG_R14, 0x1), (REG_R15, 0xff02)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4fae", 'data': "" },
        { 'regs': [(REG_R14, 0x1), (REG_R15, 0x3)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4fae", 'data': "" }
    ),
    (
        'DADD.b r14, r15 (destination zero)',
        { 'regs': [(REG_R14, 0x0), (REG_R15, 0xff00)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4fae", 'data': "" },
        { 'regs': [(REG_R14, 0x0), (REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 0), (SR_V, 0)], 'code': "4fae", 'data': "" }
    ),
    (
        'DADD.b r14, r15 (destination zero + carry)',
        { 'regs': [(REG_R14, 0x1), (REG_R15, 0xff99)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "4fae", 'data': "" },
        { 'regs': [(REG_R14, 0x1), (REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 1), (SR_V, 0)], 'code': "4fae", 'data': "" }
    ),
    (
        'DADD.b r14, r15 (destination negative)',
        { 'regs': [(REG_R14, 0x1), (REG_R15, 0xff79)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "4fae", 'data': "" },
        { 'regs': [(REG_R14, 0x1), (REG_R15, 0x80)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4fae", 'data': "" }
    ),
]
