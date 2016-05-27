from envi.archs.msp430.regs import *

checks = [
    # CLRC
    (
        'CLRC',
        { 'regs': [], 'flags': [(SR_N, 1), (SR_Z, 1), (SR_C, 1), (SR_V, 1)], 'code': "12c3", 'data': "" },
        { 'regs': [], 'flags': [(SR_N, 1), (SR_Z, 1), (SR_C, 0), (SR_V, 1)], 'code': "12c3", 'data': "" }
    ),
]
