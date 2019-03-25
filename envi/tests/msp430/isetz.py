from envi.archs.msp430.regs import *

checks = [
    # SETZ
    (
        'SETZ',
        { 'regs': [], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "22d3", 'data': "" },
        { 'regs': [], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 0), (SR_V, 0)], 'code': "22d3", 'data': "" }
    ),
]
