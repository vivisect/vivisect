from envi.archs.msp430.regs import *

msp430_checks = [
    (
        'ADC r15',
        { 'regs': [(REG_R15, 0x1)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f63", 'data': "" },
        { 'regs': [(REG_R15, 0x1)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f63", 'data': "" }
    ),
    (
        'ADC.B r15',
        { 'regs': [(REG_R15, 0x1122)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "4f63", 'data': "" },
        { 'regs': [(REG_R15, 0x23)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f63", 'data': "" }
    ),

    (
        'NOP',
        { 'regs': [], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0343", 'data': "" },
        { 'regs': [], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0343", 'data': "" }
    ),
]
