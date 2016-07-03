from envi.archs.msp430.regs import *

checks = [
    # INC
    (
        'INC r15',
        { 'regs': [(REG_R15, 0x1)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "1f53", 'data': "" },
        { 'regs': [(REG_R15, 0x2)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "1f53", 'data': "" }
    ),
    (
        'INC r15 (destination zero + carry)',
        { 'regs': [(REG_R15, 0xffff)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "1f53", 'data': "" },
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 1), (SR_V, 0)], 'code': "1f53", 'data': "" }
    ),
    (
        'INC r15 (destination overflow + negative)',
        { 'regs': [(REG_R15, 0x7fff)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "1f53", 'data': "" },
        { 'regs': [(REG_R15, 0x8000)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 1)], 'code': "1f53", 'data': "" }
    ),

    # INC.b
    (
        'INC.b r15',
        { 'regs': [(REG_R15, 0xff01)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "5f53", 'data': "" },
        { 'regs': [(REG_R15, 0x2)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "5f53", 'data': "" }
    ),
    (
        'INC.b r15 (destination 0xffff + zero + carry)',
        { 'regs': [(REG_R15, 0xffff)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "5f53", 'data': "" },
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 1), (SR_V, 0)], 'code': "5f53", 'data': "" }
    ),
    (
        'INC.b r15 (destination 0xff + zero + carry)',
        { 'regs': [(REG_R15, 0xff)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "5f53", 'data': "" },
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 1), (SR_V, 0)], 'code': "5f53", 'data': "" }
    ),
    (
        'INC.b r15 (destination overflow + negative)',
        { 'regs': [(REG_R15, 0xff7f)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "5f53", 'data': "" },
        { 'regs': [(REG_R15, 0x80)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 1)], 'code': "5f53", 'data': "" }
    ),
]
