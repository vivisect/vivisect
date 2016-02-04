from envi.archs.msp430.regs import *

checks = [
    # ADD
    (
        'ADD r14, r15',
        { 'regs': [(REG_R14, 0x1), (REG_R15, 0x2)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f5e", 'data': "" },
        { 'regs': [(REG_R14, 0x1), (REG_R15, 0x3)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f5e", 'data': "" }
    ),
    (
        'ADD r14, r15 (destination zero)',
        { 'regs': [(REG_R14, 0x0), (REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f5e", 'data': "" },
        { 'regs': [(REG_R14, 0x0), (REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 0), (SR_V, 0)], 'code': "0f5e", 'data': "" }
    ),
    (
        'ADD r14, r15 (destination zero + carry)',
        { 'regs': [(REG_R14, 0x1), (REG_R15, 0xffff)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "0f5e", 'data': "" },
        { 'regs': [(REG_R14, 0x1), (REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 1), (SR_V, 0)], 'code': "0f5e", 'data': "" }
    ),
    (
        'ADD r14, r15 (destination overflow + negative)',
        { 'regs': [(REG_R14, 0x1), (REG_R15, 0x7fff)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "0f5e", 'data': "" },
        { 'regs': [(REG_R14, 0x1), (REG_R15, 0x8000)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 1)], 'code': "0f5e", 'data': "" }
    ),

    # ADD.b
    (
        'ADD.b r14, r15',
        { 'regs': [(REG_R14, 0x1), (REG_R15, 0x2)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f5e", 'data': "" },
        { 'regs': [(REG_R14, 0x1), (REG_R15, 0x3)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f5e", 'data': "" }
    ),
    (
        'ADD.b r15 (carry + word src)',
        { 'regs': [(REG_R14, 0x1), (REG_R15, 0xff02)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "4f5e", 'data': "" },
        { 'regs': [(REG_R14, 0x1), (REG_R15, 0x3)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f5e", 'data': "" }
    ),
    (
        'ADD.b r14, r15 (destination zero)',
        { 'regs': [(REG_R14, 0x0), (REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f5e", 'data': "" },
        { 'regs': [(REG_R14, 0x0), (REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 0), (SR_V, 0)], 'code': "4f5e", 'data': "" }
    ),
    (
        'ADD.b r14, r15 (destination zero + carry)',
        { 'regs': [(REG_R14, 0x1), (REG_R15, 0xff)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "4f5e", 'data': "" },
        { 'regs': [(REG_R14, 0x1), (REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 1), (SR_V, 0)], 'code': "4f5e", 'data': "" }
    ),
    (
        'ADD.b r14, r15 (destination overflow + negative)',
        { 'regs': [(REG_R14, 0x1), (REG_R15, 0x7f)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "4f5e", 'data': "" },
        { 'regs': [(REG_R14, 0x1), (REG_R15, 0x80)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 1)], 'code': "4f5e", 'data': "" }
    ),
]
