from envi.archs.msp430.regs import *

checks = [
    # SWPB
    (
        'DEC r15',
        { 'regs': [(REG_R15, 0xaabb)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "8f10", 'data': "" },
        { 'regs': [(REG_R15, 0xbbaa)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "8f10", 'data': "" }
    ),
]
