from envi.archs.msp430.regs import *

checks = [
    # CLRN
    (
        'CLRN',
        { 'regs': [], 'flags': [(SR_N, 1), (SR_Z, 1), (SR_C, 1), (SR_V, 1)], 'code': "22c2", 'data': "" },
        { 'regs': [], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 1), (SR_V, 1)], 'code': "22c2", 'data': "" }
    ),
]
