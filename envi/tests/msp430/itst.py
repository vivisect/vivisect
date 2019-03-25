from envi.archs.msp430.regs import *

checks = [
    # TST
    (
        'TST R15 (destination negative)',
        { 'regs': [(REG_R15, 0x8000)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 1)], 'code': "0f93", 'data': "" },
        { 'regs': [(REG_R15, 0x8000)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "0f93", 'data': "" }
    ),
    (
        'TST R15 (destination zero)',
        { 'regs': [(REG_R15, 0x0000)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 1)], 'code': "0f93", 'data': "" },
        { 'regs': [(REG_R15, 0x0000)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 1), (SR_V, 0)], 'code': "0f93", 'data': "" }
    ),

    # TST.b
    (
        'TST.b R15 (destination negative)',
        { 'regs': [(REG_R15, 0x1180)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 1)], 'code': "4f93", 'data': "" },
        { 'regs': [(REG_R15, 0x1180)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "4f93", 'data': "" }
    ),
    (
        'TST.b R15 (destination zero)',
        { 'regs': [(REG_R15, 0x1100)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 1)], 'code': "4f93", 'data': "" },
        { 'regs': [(REG_R15, 0x1100)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 1), (SR_V, 0)], 'code': "4f93", 'data': "" }
    ),
]
