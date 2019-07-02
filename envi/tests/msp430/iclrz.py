from envi.archs.msp430.regs import *

checks = [
    # CLRZ
    (
        'CLRZ',
        { 'regs': [], 'flags': [(SR_N, 1), (SR_Z, 1), (SR_C, 1), (SR_V, 1)], 'code': "22c3", 'data': "" },
        { 'regs': [], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 1), (SR_V, 1)], 'code': "22c3", 'data': "" }
    ),
]
