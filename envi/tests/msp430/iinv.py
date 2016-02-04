from envi.archs.msp430.regs import *

checks = [
    # INV
    (
        'INV R15',
        { 'regs': [(REG_R15, 0x5a5a)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "3fe3", 'data': "" },
        { 'regs': [(REG_R15, 0xa5a5)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "3fe3", 'data': "" }
    ),
    (
        'INV R15 (destination zero + overflow)',
        { 'regs': [(REG_R15, 0xffff)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "3fe3", 'data': "" },
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 0), (SR_V, 1)], 'code': "3fe3", 'data': "" }
    ),

    # INV.b
    (
        'INV.b R15',
        { 'regs': [(REG_R15, 0x115a)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "7fe3", 'data': "" },
        { 'regs': [(REG_R15, 0xa5)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "7fe3", 'data': "" }
    ),
    (
        'INV.b R15 (destination zero + overflow)',
        { 'regs': [(REG_R15, 0x11ff)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "7fe3", 'data': "" },
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 0), (SR_V, 1)], 'code': "7fe3", 'data': "" }
    ),
]
