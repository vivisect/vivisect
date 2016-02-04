from envi.archs.msp430.regs import *

checks = [
    # BR
    (
        'BR #0x4412',
        { 'regs': [], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "30401244", 'data': "" },
        { 'regs': [(REG_PC, 0x4412)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "30401244", 'data': "" }
    ),
]
