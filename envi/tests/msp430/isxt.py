from envi.archs.msp430.regs import *

checks = [
    # SXT
    (
        'SXT r15 (destionation carry)',
        { 'regs': [(REG_R15, 0xaa11)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "8f11", 'data': "" },
        { 'regs': [(REG_R15, 0x0011)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "8f11", 'data': "" }
    ),
    (
        'SXT r15 (destination negative + extend sign + carry)',
        { 'regs': [(REG_R15, 0x0080)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "8f11", 'data': "" },
        { 'regs': [(REG_R15, 0xff80)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "8f11", 'data': "" }
    ),
    (
        'SXT r15 (destination zero)',
        { 'regs': [(REG_R15, 0x0000)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "8f11", 'data': "" },
        { 'regs': [(REG_R15, 0x0000)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 0), (SR_V, 0)], 'code': "8f11", 'data': "" }
    ),
]
