from envi.archs.msp430.regs import *

checks = [
    #BIS
    (
        'BIS r14, r15 (result 0xffff)',
        { 'regs': [(REG_R14, 0xffff), (REG_R15, 0xaaaa)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0fde", 'data': "" },
        { 'regs': [(REG_R14, 0xffff), (REG_R15, 0xffff)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0fde", 'data': "" }
    ),
    (
        'BIS r14, r15 (result zero)',
        { 'regs': [(REG_R14, 0x0), (REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0fde", 'data': "" },
        { 'regs': [(REG_R14, 0x0), (REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0fde", 'data': "" }
    ),
    (
        'BIS r14, r15 (result eq to destination and source)',
        { 'regs': [(REG_R14, 0xaaaa), (REG_R15, 0xaaaa)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0fde", 'data': "" },
        { 'regs': [(REG_R14, 0xaaaa), (REG_R15, 0xaaaa)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0fde", 'data': "" }
    ),

    #BIS.b
    (
        'BIS.b r14, r15 (result 0xffff)',
        { 'regs': [(REG_R14, 0xffff), (REG_R15, 0xaaaa)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4fde", 'data': "" },
        { 'regs': [(REG_R14, 0xffff), (REG_R15, 0xff)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4fde", 'data': "" }
    ),
    (
        'BIS.b r14, r15 (result zero)',
        { 'regs': [(REG_R14, 0x0), (REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4fde", 'data': "" },
        { 'regs': [(REG_R14, 0x0), (REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4fde", 'data': "" }
    ),
    (
        'BIS.b r14, r15 (result eq to destination and source)',
        { 'regs': [(REG_R14, 0xaaaa), (REG_R15, 0xaaaa)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4fde", 'data': "" },
        { 'regs': [(REG_R14, 0xaaaa), (REG_R15, 0xaa)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4fde", 'data': "" }
    ),
]
