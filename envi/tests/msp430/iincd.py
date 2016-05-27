from envi.archs.msp430.regs import *

checks = [
    # INCD
    (
        'INCD r15',
        { 'regs': [(REG_R15, 0x1)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "2f53", 'data': "" },
        { 'regs': [(REG_R15, 0x3)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "2f53", 'data': "" }
    ),
    (
        'INCD r15 (destination zero + carry)',
        { 'regs': [(REG_R15, 0xfffe)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "2f53", 'data': "" },
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 1), (SR_V, 0)], 'code': "2f53", 'data': "" }
    ),
    (
        'INCD r15 (destination carry)',
        { 'regs': [(REG_R15, 0xffff)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "2f53", 'data': "" },
        { 'regs': [(REG_R15, 0x1)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "2f53", 'data': "" }
    ),
    (
        'INCD r15 (destination 0x7ffe + negative + overflow)',
        { 'regs': [(REG_R15, 0x7ffe)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "2f53", 'data': "" },
        { 'regs': [(REG_R15, 0x8000)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 1)], 'code': "2f53", 'data': "" }
    ),
    (
        'INCD r15 (destination 0x7fff + negative + overflow)',
        { 'regs': [(REG_R15, 0x7fff)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "2f53", 'data': "" },
        { 'regs': [(REG_R15, 0x8001)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 1)], 'code': "2f53", 'data': "" }
    ),

    # INCD.b
    (
        'INCD.b r15',
        { 'regs': [(REG_R15, 0xff01)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "6f53", 'data': "" },
        { 'regs': [(REG_R15, 0x3)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "6f53", 'data': "" }
    ),
    (
        'INCD.b r15 (destination zero + carry)',
        { 'regs': [(REG_R15, 0x11fe)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "6f53", 'data': "" },
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 1), (SR_V, 0)], 'code': "6f53", 'data': "" }
    ),
    (
        'INCD.b r15 (destination carry)',
        { 'regs': [(REG_R15, 0x11ff)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "6f53", 'data': "" },
        { 'regs': [(REG_R15, 0x1)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "6f53", 'data': "" }
    ),
    (
        'INCD.b r15 (destination 0x7e + negative + overflow)',
        { 'regs': [(REG_R15, 0xff7e)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "6f53", 'data': "" },
        { 'regs': [(REG_R15, 0x80)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 1)], 'code': "6f53", 'data': "" }
    ),
    (
        'INCD.b r15 (destination 0x7f + negative + overflow)',
        { 'regs': [(REG_R15, 0xff7f)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "6f53", 'data': "" },
        { 'regs': [(REG_R15, 0x81)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 1)], 'code': "6f53", 'data': "" }
    ),
]
