from envi.archs.msp430.regs import *

checks = [
    # SETC
    (
        'SETC',
        { 'regs': [], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "12d3", 'data': "" },
        { 'regs': [], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "12d3", 'data': "" }
    ),
]
