from envi.archs.msp430.regs import *

checks = [
    # BIT
    (
        'BIT r14, r15 (result zero)',
        { 'regs': [(REG_R14, 0xaaaa), (REG_R15, 0x5555)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 1)], 'code': "0fbe", 'data': "" },
        { 'regs': [(REG_R14, 0xaaaa), (REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 0), (SR_V, 0)], 'code': "0fbe", 'data': "" }
    ),
    (
        'BIT r14, r15 (result non-zero + msb)',
        { 'regs': [(REG_R14, 0xaaaa), (REG_R15, 0x8555)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 0), (SR_V, 1)], 'code': "0fbe", 'data': "" },
        { 'regs': [(REG_R14, 0xaaaa), (REG_R15, 0x8000)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "0fbe", 'data': "" }
    ),

    # BIT.b
    (
        'BIT.b r14, r15 (result zero)',
        { 'regs': [(REG_R14, 0xaaaa), (REG_R15, 0x8555)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 1)], 'code': "4fbe", 'data': "" },
        { 'regs': [(REG_R14, 0xaaaa), (REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 0), (SR_V, 0)], 'code': "4fbe", 'data': "" }
    ),
    (
        'BIT.b r14, r15 (result non-zero + msb)',
        { 'regs': [(REG_R14, 0xaaaa), (REG_R15, 0xaa80)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 0), (SR_V, 1)], 'code': "4fbe", 'data': "" },
        { 'regs': [(REG_R14, 0xaaaa), (REG_R15, 0x80)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "4fbe", 'data': "" }
    ),
]
