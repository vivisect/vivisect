from envi.archs.msp430.regs import *

checks = [
    # MOV
    (
        'MOV r14, r15',
        { 'regs': [(REG_R14, 0x1122), (REG_R15, 0x3344)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f4e", 'data': "" },
        { 'regs': [(REG_R14, 0x1122), (REG_R15, 0x1122)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f4e", 'data': "" }
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

    # PC
    (
        'MOV pc, r15',
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f40", 'data': "" },
        { 'regs': [(REG_R15, 0x4402)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f40", 'data': "" }
    ),
    (
        'MOV @pc, r15',
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "2f40aabb", 'data': "" },
        { 'regs': [(REG_R15, 0xbbaa)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "2f40aabb", 'data': "" }
    ),
    (
        'MOV r15, @pc',
        { 'regs': [(REG_R15, 0xaabb)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "804f0000", 'data': "" },
        { 'regs': [(REG_R15, 0xaabb)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "804f0000bbaa", 'data': "" }
    ),

    # Constant Generators
    # SR   X(Rn)  (0)
    (
        'MOV 0(sr), r15',
        { 'regs': [(REG_R15, 0xaabb)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "1f420000", 'data': "" },
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "1f420000", 'data': "" }
    ),
    # SR   @Rn    4
    (
        'MOV @sr, r15',
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "2f42", 'data': "" },
        { 'regs': [(REG_R15, 0x4)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "2f42", 'data': "" }
    ),
    # SR   @Rn+   8
    (
        'MOV @sr+, r15',
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "3f42", 'data': "" },
        { 'regs': [(REG_R15, 0x8)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "3f42", 'data': "" }
    ),
    # CG   Rn     0
    (
        'MOV cg, r15',
        { 'regs': [(REG_R15, 0xaabb)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f43", 'data': "" },
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0f43", 'data': "" }
    ),
    # CG   X(Rn)  1
    (
        'MOV 0(cg), r15',
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "1f430000", 'data': "" },
        { 'regs': [(REG_R15, 0x1)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "1f430000", 'data': "" }
    ),
    # CG   @Rn    2
    (
        'MOV @cg, r15',
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "2f43", 'data': "" },
        { 'regs': [(REG_R15, 0x2)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "2f43", 'data': "" }
    ),
    # CG   @Rn+   -1
    (
        'MOV @cg+, r15',
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "3f43", 'data': "" },
        { 'regs': [(REG_R15, 0xffff)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "3f43", 'data': "" }
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

    # PC
    (
        'MOV.b pc, r15',
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f40", 'data': "" },
        { 'regs': [(REG_R15, 0x02)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f40", 'data': "" }
    ),
    (
        'MOV.b @pc, r15',
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "6f40aabb", 'data': "" },
        { 'regs': [(REG_R15, 0xaa)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "6f40aabb", 'data': "" }
    ),
    (
        'MOV.b r15, @pc',
        { 'regs': [(REG_R15, 0xaabb)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "c04f0000", 'data': "" },
        { 'regs': [(REG_R15, 0xaabb)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "c04f0000bb", 'data': "" }
    ),

    # Constant Generators
    # SR   X(Rn)  (0)
    (
        'MOV.b 0(sr), r15',
        { 'regs': [(REG_R15, 0xaabb)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "5f420000", 'data': "" },
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "5f420000", 'data': "" }
    ),
    # SR   @Rn    4
    (
        'MOV.b @sr, r15',
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "6f42", 'data': "" },
        { 'regs': [(REG_R15, 0x4)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "6f42", 'data': "" }
    ),
    # SR   @Rn+   8
    (
        'MOV.b @sr+, r15',
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "7f42", 'data': "" },
        { 'regs': [(REG_R15, 0x8)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "7f42", 'data': "" }
    ),
    # CG   Rn     0
    (
        'MOV.b cg, r15',
        { 'regs': [(REG_R15, 0xaabb)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f43", 'data': "" },
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "4f43", 'data': "" }
    ),
    # CG   X(Rn)  1
    (
        'MOV.b 0(cg), r15',
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "5f430000", 'data': "" },
        { 'regs': [(REG_R15, 0x1)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "5f430000", 'data': "" }
    ),
    # CG   @Rn    2
    (
        'MOV.b @cg, r15',
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "6f43", 'data': "" },
        { 'regs': [(REG_R15, 0x2)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "6f43", 'data': "" }
    ),
    # CG   @Rn+   -1
    (
        'MOV.b @cg+, r15',
        { 'regs': [(REG_R15, 0x0)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "7f43", 'data': "" },
        { 'regs': [(REG_R15, 0xff)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "7f43", 'data': "" }
    ),
]
