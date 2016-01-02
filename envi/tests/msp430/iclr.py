from envi.archs.msp430.regs import *

checks = [
    # CLR
    (
        'CLR R15',
        { 'regs': [(REG_R15, 0xffff)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f43", 'data': "" },
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f43", 'data': "" }
    ),
    (
        'CLR @R15',
        { 'regs': [(REG_R15, 0x1000)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "8f430000", 'data': "11223344" },
        { 'regs': [(REG_R15, 0x1000)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "8f430000", 'data': "00003344" }
    ),

    # CLR.b
    (
        'CLR.b R15',
        { 'regs': [(REG_R15, 0xffff)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f43", 'data': "" },
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f43", 'data': "" }
    ),
    (
        'CLR @R15',
        { 'regs': [(REG_R15, 0x1000)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "cf430000", 'data': "11223344" },
        { 'regs': [(REG_R15, 0x1000)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "cf430000", 'data': "00223344" }
    ),
]
