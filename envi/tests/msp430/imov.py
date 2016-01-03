from envi.archs.msp430.regs import *

checks = [
    # MOV
    (
        'MOV r14, r15',
        { 'regs': [(REG_R14, 0x1122), (REG_R15, 0x3344)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f4e", 'data': "" },
        { 'regs': [(REG_R14, 0x1122), (REG_R15, 0x1122)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f4e", 'data': "" }
    ),
    (
        'MOV pc, r15',
        { 'regs': [], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f40", 'data': "" },
        { 'regs': [(REG_R15, 0x4402)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f40", 'data': "" }
    ),
    (
        'MOV #0xaabb, r15',
        { 'regs': [], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "3f40bbaa", 'data': "" },
        { 'regs': [(REG_R15, 0xaabb)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "3f40bbaa", 'data': "" }
    ),
    (
        'MOV @r14, r15',
        { 'regs': [(REG_R14, 0x1002)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "2f4e", 'data': "00112233445566" },
        { 'regs': [(REG_R14, 0x1002), (REG_R15, 0x3322)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "2f4e", 'data': "00112233445566" }
    ),
    (
        'MOV r14, @r15',
        { 'regs': [(REG_R14, 0xaabb), (REG_R15, 0x1002)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "8f4e0000", 'data': "00112233445566" },
        { 'regs': [(REG_R14, 0xaabb), (REG_R15, 0x1002)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "8f4e0000", 'data': "0011bbaa445566" }
    ),
    (
        'MOV @r14+, r15',
        { 'regs': [(REG_R14, 0x1002)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "3f4e", 'data': "00112233445566" },
        { 'regs': [(REG_R14, 0x1004), (REG_R15, 0x3322)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "3f4e", 'data': "00112233445566" }
    ),

    # MOV.b
    (
        'MOV.b r14, r15',
        { 'regs': [(REG_R14, 0x1122), (REG_R15, 0x3344)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f4e", 'data': "" },
        { 'regs': [(REG_R14, 0x1122), (REG_R15, 0x22)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f4e", 'data': "" }
    ),
    (
        'MOV.b pc, r15',
        { 'regs': [], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f40", 'data': "" },
        { 'regs': [(REG_R15, 0x02)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f40", 'data': "" }
    ),
    (
        'MOV.b #0xaabb, r15',
        { 'regs': [], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "7f40bb00", 'data': "" },
        { 'regs': [(REG_R15, 0xbb)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "7f40bb00", 'data': "" }
    ),
    (
        'MOV.b @r14, r15',
        { 'regs': [(REG_R14, 0x1002)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "6f4e", 'data': "00112233445566" },
        { 'regs': [(REG_R14, 0x1002), (REG_R15, 0x22)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "6f4e", 'data': "00112233445566" }
    ),
    (
        'MOV.b r14, @r15',
        { 'regs': [(REG_R14, 0xaabb), (REG_R15, 0x1002)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "cf4e0000", 'data': "00112233445566" },
        { 'regs': [(REG_R14, 0xaabb), (REG_R15, 0x1002)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "cf4e0000", 'data': "0011bb33445566" }
    ),
    (
        'MOV.b @r14+, r15',
        { 'regs': [(REG_R14, 0x1002)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "7f4e", 'data': "00112233445566" },
        { 'regs': [(REG_R14, 0x1003), (REG_R15, 0x22)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "7f4e", 'data': "00112233445566" }
    ),
]
