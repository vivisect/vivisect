from envi.archs.msp430.regs import *

checks = [
    # JC / JHS
    (
        'JC #0x4410 (C=0)',
        { 'regs': [], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "072c", 'data': "" },
        { 'regs': [(REG_PC, 0x4402)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "072c", 'data': "" }
    ),
    (
        'JC #0x4410 (C=1)',
        { 'regs': [], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "072c", 'data': "" },
        { 'regs': [(REG_PC, 0x4410)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "072c", 'data': "" }
    ),

    # JEQ / JZ
    (
        'JEQ #0x4410 (Z=0)',
        { 'regs': [], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0724", 'data': "" },
        { 'regs': [(REG_PC, 0x4402)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0724", 'data': "" }
    ),
    (
        'JEQ #0x4410 (Z=1)',
        { 'regs': [], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 0), (SR_V, 0)], 'code': "0724", 'data': "" },
        { 'regs': [(REG_PC, 0x4410)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 0), (SR_V, 0)], 'code': "0724", 'data': "" }
    ),

    # JGE
    (
        'JGE #0x4410 (N=0 V=0)',
        { 'regs': [], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0734", 'data': "" },
        { 'regs': [(REG_PC, 0x4410)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0734", 'data': "" }
    ),
    (
        'JGE #0x4410 (N=1 V=1)',
        { 'regs': [], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 1)], 'code': "0734", 'data': "" },
        { 'regs': [(REG_PC, 0x4410)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 1)], 'code': "0734", 'data': "" }
    ),
    (
        'JGE #0x4410 (N=1 V=0)',
        { 'regs': [], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0734", 'data': "" },
        { 'regs': [(REG_PC, 0x4402)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0734", 'data': "" }
    ),
    (
        'JGE #0x4410 (N=0 V=1)',
        { 'regs': [], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 1)], 'code': "0734", 'data': "" },
        { 'regs': [(REG_PC, 0x4402)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 1)], 'code': "0734", 'data': "" }
    ),

    # JL
    (
        'JL #0x4410 (N=0 V=0)',
        { 'regs': [], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0738", 'data': "" },
        { 'regs': [(REG_PC, 0x4402)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0738", 'data': "" }
    ),
    (
        'JL #0x4410 (N=1 V=1)',
        { 'regs': [], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 1)], 'code': "0738", 'data': "" },
        { 'regs': [(REG_PC, 0x4402)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 1)], 'code': "0738", 'data': "" }
    ),
    (
        'JL #0x4410 (N=1 V=0)',
        { 'regs': [], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0738", 'data': "" },
        { 'regs': [(REG_PC, 0x4410)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0738", 'data': "" }
    ),
    (
        'JL #0x4410 (N=0 V=1)',
        { 'regs': [], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 1)], 'code': "0738", 'data': "" },
        { 'regs': [(REG_PC, 0x4410)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 1)], 'code': "0738", 'data': "" }
    ),

    # JMP
    (
        'JMP #0x4410',
        { 'regs': [], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "073c", 'data': "" },
        { 'regs': [(REG_PC, 0x4410)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "073c", 'data': "" }
    ),

    # JN
    (
        'JN #0x4410 (N=0)',
        { 'regs': [], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0730", 'data': "" },
        { 'regs': [(REG_PC, 0x4402)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0730", 'data': "" }
    ),
    (
        'JN #0x4410 (N=1)',
        { 'regs': [], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0730", 'data': "" },
        { 'regs': [(REG_PC, 0x4410)], 'flags': [(SR_N, 1), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0730", 'data': "" }
    ),

    # JNC / JLO
    (
        'JNC #0x4410 (C=0)',
        { 'regs': [], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0728", 'data': "" },
        { 'regs': [(REG_PC, 0x4410)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0728", 'data': "" }
    ),
    (
        'JNC #0x4410 (C=1)',
        { 'regs': [], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "0728", 'data': "" },
        { 'regs': [(REG_PC, 0x4402)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 1), (SR_V, 0)], 'code': "0728", 'data': "" }
    ),

    # JNE / JNZ
    (
        'JNC #0x4410 (Z=0)',
        { 'regs': [], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0720", 'data': "" },
        { 'regs': [(REG_PC, 0x4410)], 'flags': [(SR_N, 0), (SR_Z, 0), (SR_C, 0), (SR_V, 0)], 'code': "0720", 'data': "" }
    ),
    (
        'JNC #0x4410 (Z=1)',
        { 'regs': [], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 0), (SR_V, 0)], 'code': "0720", 'data': "" },
        { 'regs': [(REG_PC, 0x4402)], 'flags': [(SR_N, 0), (SR_Z, 1), (SR_C, 0), (SR_V, 0)], 'code': "0720", 'data': "" }
    ),
]
