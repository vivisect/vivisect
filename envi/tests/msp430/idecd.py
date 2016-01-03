from envi.archs.msp430.regs import *

checks = [
    # DECD
    (
        'DECD r15',
        { 'regs': [(REG_R15, 0x3)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "2f83", 'data': "" },
        { 'regs': [(REG_R15, 0x1)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "2f83", 'data': "" }
    ),
    (
        'DECD r15 (destination zero)',
        { 'regs': [(REG_R15, 0x2)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "2f83", 'data': "" },
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 1), (SR_V, 0)], 'code': "2f83", 'data': "" }
    ),
    (
        'DECD r15 (destination overflow)',
        { 'regs': [(REG_R15, 0x8001)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "2f83", 'data': "" },
        { 'regs': [(REG_R15, 0x7fff)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 1)], 'code': "2f83", 'data': "" }
    ),
    (
        'DECD r15 (destination 0x0 + carry + negative)',
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "2f83", 'data': "" },
        { 'regs': [(REG_R15, 0xfffe)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "2f83", 'data': "" }
    ),
    (
        'DECD r15 (destination 0x1 + carry + negative)',
        { 'regs': [(REG_R15, 0x1)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "2f83", 'data': "" },
        { 'regs': [(REG_R15, 0xffff)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "2f83", 'data': "" }
    ),

    # DECD.b
    (
        'DECD.b r15',
        { 'regs': [(REG_R15, 0xff03)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "6f83", 'data': "" },
        { 'regs': [(REG_R15, 0x1)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "6f83", 'data': "" }
    ),
    (
        'DECD.b r15 (destination zero)',
        { 'regs': [(REG_R15, 0xff02)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "6f83", 'data': "" },
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 1), (SR_V, 0)], 'code': "6f83", 'data': "" }
    ),
    (
        'DECD.b r15 (destination overflow)',
        { 'regs': [(REG_R15, 0xff81)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "6f83", 'data': "" },
        { 'regs': [(REG_R15, 0x7f)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 1)], 'code': "6f83", 'data': "" }
    ),
    (
        'DECD.b r15 (destination 0x0 + carry + negative)',
        { 'regs': [(REG_R15, 0xff00)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "6f83", 'data': "" },
        { 'regs': [(REG_R15, 0xfe)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "6f83", 'data': "" }
    ),
    (
        'DECD.b r15 (destination 0x1 + carry + negative)',
        { 'regs': [(REG_R15, 0xff01)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "6f83", 'data': "" },
        { 'regs': [(REG_R15, 0xff)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "6f83", 'data': "" }
    ),
]
