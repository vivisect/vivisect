from envi.archs.msp430.regs import *

checks = [
    #BIC
    (
        'BIC r14, r15',
        { 'regs': [(REG_R14, 0x5555), (REG_R15, 0xaaaa)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0fce", 'data': "" },
        { 'regs': [(REG_R14, 0x5555), (REG_R15, 0xaaaa)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0fce", 'data': "" }
    ),
    (
        'BIC r14, r15 (result zero)',
        { 'regs': [(REG_R14, 0x5555), (REG_R15, 0x5555)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0fce", 'data': "" },
        { 'regs': [(REG_R14, 0x5555), (REG_R15, 0x0000)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0fce", 'data': "" }
    ),
    (
        'BIC r14, r15 (result eq destination)',
        { 'regs': [(REG_R14, 0x0), (REG_R15, 0x5555)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0fce", 'data': "" },
        { 'regs': [(REG_R14, 0x0), (REG_R15, 0x5555)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0fce", 'data': "" }
    ),

    #BIC.b
    (
        'BIC.b r14, r15',
        { 'regs': [(REG_R14, 0x5555), (REG_R15, 0xaaaa)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4fce", 'data': "" },
        { 'regs': [(REG_R14, 0x5555), (REG_R15, 0xaa)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4fce", 'data': "" }
    ),
    (
        'BIC.b r14, r15 (result zero)',
        { 'regs': [(REG_R14, 0x5555), (REG_R15, 0x5555)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4fce", 'data': "" },
        { 'regs': [(REG_R14, 0x5555), (REG_R15, 0x00)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4fce", 'data': "" }
    ),
    (
        'BIC.b r14, r15 (result eq src)',
        { 'regs': [(REG_R14, 0x0), (REG_R15, 0x5555)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4fce", 'data': "" },
        { 'regs': [(REG_R14, 0x0), (REG_R15, 0x55)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4fce", 'data': "" }
    ),
]
