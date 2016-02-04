from envi.archs.msp430.regs import *

checks = [
    # NOP
    (
        'NOP',
        { 'regs': [], 'flags': [(SR_N, 1), (SR_Z, 1), (SR_C, 1), (SR_V, 1)], 'code': "0343", 'data': "" },
        { 'regs': [], 'flags': [(SR_N, 1), (SR_Z, 1), (SR_C, 1), (SR_V, 1)], 'code': "0343", 'data': "" }
    ),
]
