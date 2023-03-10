'''
Ways to access registers, flags or memory:
    'regname'       eg: 'f30'                   - get/set register by name
    'REG_CONSTANT'  eg: 'REG_R3' or 'REG_XER'   - get/set register by constant (good for
                                                        specific, hard to reach flags)
    0xADDRESS       eg: 0xdeadb33f              - read/write memory at address
    '[expression]'  eg: '[r0 + 4]'              - read/write memory at expression
                    or '[0xdeadbeef + 243]'
    '[expr:20]'     eg: '[r0+4:20]'             - read/write 20 bytes of memory at expr
'''

from envi.archs.ppc.const import *  # after adding this, I can use the variables from const.py

FDNP = FP_DOUBLE_NEG_PYNAN
FDPP = FP_DOUBLE_POS_PYNAN
FSNP = FP_SINGLE_NEG_PYNAN
FSPP = FP_SINGLE_POS_PYNAN
FDNQ = FP_DOUBLE_NEG_QNAN
FDPQ = FP_DOUBLE_POS_QNAN
FDNS = FP_DOUBLE_NEG_SNAN
FDPS = FP_DOUBLE_POS_SNAN
FDNI = FP_DOUBLE_NEG_INF
FDPI = FP_DOUBLE_POS_INF
FSNQ = FP_SINGLE_NEG_QNAN
FSPQ = FP_SINGLE_POS_QNAN
FSNS = FP_SINGLE_NEG_SNAN
FSPS = FP_SINGLE_POS_SNAN
FSNI = FP_SINGLE_NEG_INF
FSPI = FP_SINGLE_POS_INF
FDNZ = FP_DOUBLE_NEG_ZERO
FDPZ = FP_DOUBLE_POS_ZERO
FSNZ = FP_SINGLE_NEG_ZERO
FSPZ = FP_SINGLE_POS_ZERO
FHNQ = FP_HALF_NEG_QNAN
FHPQ = FP_HALF_POS_QNAN
FHNI = FP_HALF_NEG_INF
FHPI = FP_HALF_POS_INF
FHNS = FP_HALF_NEG_SNAN
FHPS = FP_HALF_POS_SNAN
FHNZ = FP_HALF_NEG_ZERO
FHPZ = FP_HALF_POS_ZERO

_1p1s = 0x3F8CCCCD # 1.1
_2p2s = 0x400CCCCD # 2.2
_3p3s = 0x40533333 # 3.3
_4p4s = 0x408CCCCD
_5p5s = 0x40B00000

n_1p1s = 0xBF8CCCCD # 1.1
n_2p2s = 0xC00CCCCD # 2.2
n_3p3s = 0xC0533333 # 3.3
n_4p4s = 0xC08CCCCD
n_5p5s = 0xC0B00000

pi_d = 0x400921fb54442d18
pi_s = 0x40490fdb

GOOD_EMU_TESTS = 522

emutests = {
    #'e9f2': [{'setup': (('pc', 0x471450), ('lr', 0x313370)),
    #    'tests': (('pc', 0x471434), ('lr', 0x471452))}],   # se_bl -0x1c

    #'e8eb': [{'setup': (('pc', 0x471450), ('lr', 0x313370 )),
    #    'tests': (('pc', 0x471450), ('lr', 0x313370))}],   # se_b -0x2a

    '7CDF0214': [
        {
            'setup': (
                ('r31', 4),
                ('r0', 16),
                ('xer', 0),
            ),
            'tests': (
                ('r6', 20),
                ('r31', 4),
                ('r0', 16),
                ('cr0', 0),
            ),
        },
    ],   # add r6,r31,r0

    '7C005214': [  # 7C005214,"add r0,r0,r10"
        {
            'setup': (
                ('r10', 4),
                ('r0', 16),
            ),
            'tests': (
                ('r0', 20),
                ('r10', 4),
            ),
        },
    ],   # 7C005214,"add r0,r0,r10"

    '7FDE1914': [ #7FDE1914,"adde r30,r30,r3"
        {
            'setup': (
                ('r30', 4),
                ('r3', 16),
                ('xer', 0x0)
            ),
            'tests': (
                ('r30', 20),
                ('r3', 16),
                ('xer', 0x0)
            ),
        },
        {
            'setup': (
                ('r30', -1),
                ('r3', 3),
                ('xer', 0x0)
            ),
            'tests': (
                ('r30', 2),
                ('r3', 3),
                ('xer', 0x20000000)
            ),
        },
        {
            'setup': (
                ('r30', 0x7fffffff),
                ('r3', 3),
                ('xer', 0x0)
            ),
            'tests': (
                ('r30', 0x80000002),
                ('r3', 3),
                ('xer', 0x0)
            ),
        },
        {
            'setup': (
                ('r30', 0x7fffffff),
                ('r3', 3),
                ('xer', 0x20000000)
            ),
            'tests': (
                ('r30', 0x80000003),
                ('r3', 3),
                ('xer', 0x0)
            ),
        },
        {
            'setup': (
                ('r30', 0xffffffff),
                ('r3', 3),
                ('xer', 0x20000000)
            ),
            'tests': (
                ('r30', 0x3),
                ('r3', 3),
                ('xer', 0x20000000)
            ),
        },
    ],   # 7FDE1914,"adde r30,r30,r3"

   '7C005215': [  # 7C005215,"add. r0,r0,r10"
        {
            'setup': (
                ('r0', 0),
                ('r10', 0xf0000001)
            ),
            'tests': (
                ('r0', 0xf0000001),
                ('cr0', 0b1000)
            ),
        },
                {
            'setup': (
                ('r0', 0x5),
                ('r10', 0xf0000001)
            ),
            'tests': (
                ('r0', 0xf0000006),
                ('cr0', 0b1000)
            ),
        },
                {
            'setup': (
                ('r0', 0xffffffff),
                ('r10', 0x3)
            ),
            'tests': (
                ('r0', 0x2),
                ('cr0', 0b0100)
            ),
        },
    ],   # 7C005215,"add r0,r0,r10"

    '7C000194': [  # 7C000194,"addze r0,r0"
        {
            'setup': (
                ('r0', 0x00050056),
                ('xer', 0x20000000)
            ),
            'tests': (
                ('r0', 0x00050057),
                ('cr0', 0b0100)
            ),
        },
        {
            'setup': (
                ('r0', 0x00050056),
                ('xer', 0x00000000)
            ),
            'tests': (
                ('r0', 0x50056),
                ('cr0', 0b0100)
            ),
        },
    ],   # 7C000194,"addze r0,r0"

     '1C00FE6A': [  # 1C00FE6A,"e_add16i r0,r0,-0x196"
        {
            'setup': (
                ('r0', 0x196),
            ),
            'tests': (
                ('r0', 0),
            ),
        },
                {
            'setup': (
                ('r0', 0x255),
            ),
            'tests': (
                ('r0', 0xbf),
            ),
        },

        {
            'setup': (
                ('r0', 0x255),
            ),
            'tests': (
                ('r0', 0xbf),
            ),
        },
        {
            'setup': (
                ('r0', 0x7fffffff),
            ),
            'tests': (
                ('r0', 0x7ffffe69),
            ),
        },
        {
            'setup': (
                ('r0', 0xffffffff),
            ),
            'tests': (
                ('r0', 0xfffffe69),
            ),
        },
    ],   # 1C00FE6A,"e_add16i r0,r0,-0x196"

       '1AD68CFF': [  # 1AD68CFF,"e_addi. r22,r22,0xffffffff"
        {
            'setup': (
                ('r22', 0),
            ),
            'tests': (
                ('r22', 0xffffffff),
                ('cr0', 0b1000)
            ),
        },
    ],   # 1AD68CFF,"e_addi. r22,r22,0xffffffff"

    '7C004039': [  # 7C004039,"and. r0,r0,r8"
        {
            'setup': (
                ('r0', 0xffffffff),
                ('r8', 0x12345678)
            ),
            'tests': (
                ('r0', 0x12345678),
                ('cr0', 0b0100)
            ),
        },
    ],   # 7C004039,"and. r0,r0,r8"

    '7CC00078': [  # 7CC00078,"andc r0,r6,r0"
        {
            'setup': (
                ('r0', 0xffffffff),
                ('r6', 0x12345678)
            ),
            'tests': (
                ('r0', 0),
                #('cr0', 0b0100)
            ),
        },
        {
            'setup': (
                ('r0', 0xffffffff),
                ('r6', 0x12345678)
            ),
            'tests': (
                ('r0', 0),
                #('cr0', 0b0100)
            ),
        },
        {
            'setup': (
                ('r0', 0x11111111),
                ('r6', 0xfffffffe)
            ),
            'tests': (
                ('r0', 0xeeeeeeee),
                #('cr0', 0b0100)
            ),
        },
    ],   # 7CC00078,"andc r0,r6,r0"

    '7C005040': [  # 7C005040,"cmplw r0,r10" (cmpl 0, 0,Rx,Ry)(cmpl 0, 0,r0,r10)
        {
            'setup': (
                ('r0', 0x1234),
                ('r10',0x0),
                ('cr0', 0b0000)
            ),
            'tests': (
                ('cr0', 0b0100),
            ),
        },
        {
            'setup': (
                ('r0', 0x1234),
                ('r10',0x1234),
                ('cr0', 0b0000)
            ),
            'tests': (
                ('cr0', 0b0010),
            ),
        },
        {
            'setup': (
                ('r0', 0x1234),
                ('r10',0x1235),
                ('cr0', 0b0000)
            ),
            'tests': (
                ('cr0', 0b1000),
            ),
        },


    ],   # 7C005040,"cmplw r0,r10"

    '7C008000': [  # 7C008000,"cmpw r0,r16"
        {
            'setup': (
                ('r0', 0x1234),
                ('r16',0x0),
                ('cr0', 0b0000)
            ),
            'tests': (
                ('cr0', 0b0100),
            ),
        },
    ],   # 7C008000,"cmpw r0,r16"

    '7C000034': [  # 7C000034,"cntlzw r0,r0"
        {
            'setup': (
                ('r0', 0x0fffffff),
            ),
            'tests': (
                ('r0', 4),
            ),
        },
    ],   # 7C000034,"cntlzw r0,r0"

    '7C0303D6': [  # 7C0303D6,"divw r0,r3,r0"
        {
            'setup': (
                ('r0', 5),
                ('r3', 35)
            ),
            'tests': (
                ('r0', 7),
            ),
        },
        {
            'setup': (
                ('r0', 4),
                ('r3', 35)
            ),
            'tests': (
                ('r0', 8),
            ),
        },
        {
            'setup': (
                ('r0', 0),
                ('r3', 35)
            ),
            'tests': (
                ('r0', 0x7fffffff),
            ),
        },
        {
            'setup': (
                ('r0', 2),
                ('r3', -10)
            ),
            'tests': (
                ('r0', 0xfffffffb),
            ),
        },
        {
            'setup': (
                ('r0', 2),
                ('r3', 0)
            ),
            'tests': (
                ('r0', 0),
            ),
        },
    ],   # 7C0303D6,"divw r0,r3,r0"

    '7C00FB96': [  # 7C00FB96,"divwu r0,r0,r31"
        {
            'setup': (
                ('r0', 5),
                ('r31', 35)
            ),
            'tests': (
                ('r0', 0),
            ),
        },
        {
            'setup': (
                ('r0', 35),
                ('r31', 5)
            ),
            'tests': (
                ('r0', 7),
            ),
        },
        {
            'setup': (
                ('r0', 35),
                ('r31', 4)
            ),
            'tests': (
                ('r0', 0x8),
            ),
        },
        {
            'setup': (
                ('r0', 2),
                ('r31', -1)
            ),
            'tests': (
                ('r0', 0),
            ),
        },
        {
            'setup': (
                ('r0', 0),
                ('r31', 10)
            ),
            'tests': (
                ('r0', 0),
            ),
        },
        {
            'setup': (
                ('r0', 10),
                ('r31', 0)
            ),
            'tests': (
                ('r0', 0xffffffff),
            ),
        },
    ],   # 7C00FB96,"divwu r0,r0,r31"

    # '7FE30774': [  # 7FE30774,"extsb r3,r31"
    #     {
    #         'setup': (
    #             ('r3', 0x0),
    #             ('r31', 0xff)
    #         ),
    #         'tests': (
    #             ('r3', 0xffffffff),
    #         ),
    #     },
    #     {
    #         'setup': (
    #             ('r3', 0x0),
    #             ('r31', 0x7f)
    #         ),
    #         'tests': (
    #             ('r3', 0x7f),
    #         ),
    #     },
    # ],   # 7FE30774,"extsb r3,r31"

    '7C60389E': [  # 7C60389E,"iseleq r3,0x0,r7"
        {
            'setup': (
                ('r3', 0x11111111),
                ('cr0', 0b0010),
                ('r7', 0x12345678)
            ),
            'tests': (
                ('r3', 0x0),
                ('cr0', 0b0010),
                ('r7', 0x12345678)
            ),
        },
        {
            'setup': (
                ('r3', 0x11111111),
                ('cr0', 0b0000),
                ('r7', 0x12345678)
            ),
            'tests': (
                ('r3', 0x12345678),
                ('cr0', 0b0000),
                ('r7', 0x12345678)
            ),
        },
        {
            'setup': (
                ('r3', 0x11111111),
                ('cr0', 0b0010),
                ('r7', 0x12345678),
                ('r0', 0x22222222)
            ),
            'tests': (
                ('r3', 0),
                ('cr0', 0b0010),
                ('r7', 0x12345678)
            ),
        },
    ],   # 7C60389E,"iseleq r3,0x0,r7"

    '7C66009E': [  # 7C66009E,"iseleq r3,r6,r0"
        {
            'setup': (
                ('r3', 0x11111111),
                ('cr0', 0b0010),
                ('r6', 0x12345678),
                ('r0', 0x22222222)
            ),
            'tests': (
                ('r3', 0x12345678),
                ('cr0', 0b0010),
                ('r6', 0x12345678),
                ('r0', 0x22222222)
            ),
        },
        {
            'setup': (
                ('r3', 0x11111111),
                ('cr0', 0b0000),
                ('r6', 0x12345678),
                ('r0', 0x22222222)
            ),
            'tests': (
                ('r3', 0x22222222),
                ('cr0', 0b0000),
                ('r6', 0x12345678)
            ),
        },
    ], #7C66009E,"iseleq r3,r6,r0"

    '7F27185E': [  # 7F27185E,"iselgt r25,r7,r3"
        {
            'setup': (
                ('r25', 0x11111111),
                ('cr0', 0b0100),
                ('r7', 0x12345678),
                ('r3', 0x22222222)
            ),
            'tests': (
                ('r25', 0x12345678),
                ('cr0', 0b0100),
                ('r7', 0x12345678),
                ('r3', 0x22222222)
            ),
        },
        {
            'setup': (
                ('r25', 0x11111111),
                ('cr0', 0b0000),
                ('r7', 0x12345678),
                ('r3', 0x22222222)
            ),
            'tests': (
                ('r25', 0x22222222),
                ('cr0', 0b0000),
                ('r7', 0x12345678)
            ),
        },
    ], # 7F27185E,"iselgt r25,r7,r3"

     '7C07001E': [  # 7C07001E,"isellt r0,r7,r0"
        {
            'setup': (
                ('r0', 0x11111111),
                ('cr0', 0b1000),
                ('r7', 0x12345678),
            ),
            'tests': (
                ('r0', 0x12345678),
                ('cr0', 0b1000),
                ('r7', 0x12345678),
            ),
        },
        {
            'setup': (
                ('r0', 0x11111111),
                ('cr0', 0b0000),
                ('r7', 0x12345678),
            ),
            'tests': (
                ('r0', 0x11111111),
                ('cr0', 0b0000),
                ('r7', 0x12345678)
            ),
        },
    ], # 7C07001E,"isellt r0,r7,r0"

    '7C1800EE': [ # 7C1800EE,"lbzux r0,r24,r0"
        {
            'setup': (
                ('r0', 0x0),
                ('r24', 0x10010100),
                (0x10010100, bytes.fromhex('11223344'))
                    ),

            'tests':(
                ('r0',0x11),
                ('r24',0x10010100),

            ),
        },
        {
            'setup': (
                ('r0', 0x100),
                ('r24', 0x10010100),
                (0x10010100 + 0x100, bytes.fromhex('11223344')),
                    ),

            'tests':(
                ('r0',0x11),
                ('r24',0x10010200),

            ),
        },
        # { # this test uses addresses from the actual memory range of teh MPC5748G
        #     'setup': (
        #         ('r0', -0x100),
        #         ('r24', 0x40008614),
        #         (0x40008614 - 0x100, bytes.fromhex('11223344'))
        #             ),

        #     'tests':(
        #         ('r0',0x11),
        #         ('r24',0x40008514),

        #     ),
        # },
        # {
        #     'setup': (
        #         ('r0', -0x100),
        #         ('r24', 0x10010500),
        #         (0x10010500 - 0x100, bytes.fromhex('11223344'))
        #             ),

        #     'tests':(
        #         ('r0',0x11),
        #         ('r24',0x10010400),

        #     ),
        # },
    ],  # 7C1800EE,"lbzux r0,r24,r0"

    '7C14F8AE': [ # 7C14F8AE,"lbzx r0,r20,r31"
        {
            'setup': (
                ('r0', 0x0),
                ('r31', 0x10010100),
                ('r20', 0x100),
                (0x10010200, bytes.fromhex('11223344')),
                #(0x10010200, bytes.fromhex('fedcba90'))
                    ),

            'tests':(
                ('r0',0x11),
                ('r31',0x10010100),
            ),
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r31', 0x10010100),
                ('r20', 0x100),
                (0x10010100 + 0x100, bytes.fromhex('abcdef01')),
                    ),

            'tests':(
                ('r0',0xab),
                ('r31',0x10010100),
            ),
        },
    ],  # 7C14F8AE,"lbzx r0,r20,r31"

    '7C0302AE': [ # 7C0302AE,"lhax r0,r3,r0"
        {
            'setup': (
                ('r0', 0x0),
                ('r3', 0x10010100),
                (0x10010100, bytes.fromhex('11223344')),
                #(0x10010200, bytes.fromhex('fedcba90'))
                    ),

            'tests':(
                ('r0',0x1122),
                ('r3',0x10010100),
            ),
        },
        {
            'setup': (
                ('r0', 0x100),
                ('r3', 0x10010100),
                (0x10010100 + 0x100, bytes.fromhex('abcdef01')),
                    ),

            'tests':(
                ('r0',0xffffabcd),
                ('r3',0x10010100),
            ),
        },
        # {
        #     'setup': (
        #         ('r0', -0x100),
        #         ('r3', 0x10010100),
        #         (0x10010100 - 0x100, bytes.fromhex('abcdef01')),
        #             ),

        #     'tests':(
        #         ('r0',0xffffabcd),
        #         ('r3',0x10010100),
        #     ),
        # },
    ],  # 7C0302AE,"lhax r0,r3,r0"

    '7C1AF26E': [ # 7C1AF26E,"lhzux r0,r26,r30"
        {
            'setup': (
                ('r0', 0x0),
                ('r26', 0x10010100),
                ('r30', 0x0),
                (0x10010100, bytes.fromhex('11223344')),
                #(0x10010200, bytes.fromhex('fedcba90'))
                    ),

            'tests':(
                ('r0',0x1122),
                ('r26',0x10010100),
            ),
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r26', 0x10010100),
                ('r30', 0x100),
                (0x10010100 + 0x100, bytes.fromhex('abcdef01')),
                    ),

            'tests':(
                ('r0',0xabcd),
                ('r26',0x10010200),
            ),
        },
        # {
        #     'setup': (
        #         ('r0', 0x0),
        #         ('r26', 0x10010100),
        #         ('r30', - 0x100),
        #         (0x10010100 - 0x100, bytes.fromhex('abcdef01')),
        #             ),

        #     'tests':(
        #         ('r0',0xabcd),
        #         ('r26',0x10010000),
        #     ),
        # },
    ],  # 7C1AF26E,"lhzux r0,r26,r30"

        '7C15DA2E': [ # 7C15DA2E,"lhzx r0,r21,r27"
        {
            'setup': (
                ('r0', 0x0),
                ('r21', 0x10010100),
                ('r27', 0x0),
                (0x10010100, bytes.fromhex('11223344')),
                #(0x10010200, bytes.fromhex('fedcba90'))
                    ),

            'tests':(
                ('r0',0x1122),
                ('r21',0x10010100),
            ),
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r21', 0x10010100),
                ('r27', 0x100),
                (0x10010100 + 0x100, bytes.fromhex('abcdef01')),
                    ),

            'tests':(
                ('r0',0xabcd),
                ('r21',0x10010100),
            ),
        },
        # {
        #     'setup': (
        #         ('r0', 0x0),
        #         ('r21', 0x10010100),
        #         ('r27', - 0x100),
        #         (0x10010100 - 0x100, bytes.fromhex('abcdef01')),
        #             ),

        #     'tests':(
        #         ('r0',0xabcd),
        #     ),
        # },
    ],  # 7C15DA2E,"lhzx r0,r21,r27"

      '7C1BC06E': [ # 7C1BC06E,"lwzux r0,r27,r24"
        {
            'setup': (
                ('r0', 0x0),
                ('r27', 0x10010100),
                ('r24', 0x0),
                (0x10010100, bytes.fromhex('11223344')),
                #(0x10010200, bytes.fromhex('fedcba90'))
                    ),

            'tests':(
                ('r0',0x11223344),
                ('r27',0x10010100),
            ),
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r27', 0x10010100),
                ('r24', 0x100),
                (0x10010100 + 0x100, bytes.fromhex('abcdef01')),
                    ),

            'tests':(
                ('r0',0xabcdef01),
                ('r27',0x10010200),
            ),
        },
        # {
        #     'setup': (
        #         ('r0', 0x0),
        #         ('r27', 0x10010100),
        #         ('r24', - 0x100),
        #         (0x10010100 - 0x100, bytes.fromhex('abcdef01')),
        #             ),

        #     'tests':(
        #         ('r0',0xabcd),
        #         ('r27', 0x10010000),
        #     ),
        # },
    ],  # 7C1BC06E,"lwzux r0,r27,r24"

       '7C17F82E': [ # 7C17F82E,"lwzx r0,r23,r31"
        {
            'setup': (
                ('r0', 0x0),
                ('r23', 0x10010100),
                ('r31', 0x0),
                (0x10010100, bytes.fromhex('11223344')),
                #(0x10010200, bytes.fromhex('fedcba90'))
                    ),

            'tests':(
                ('r0',0x11223344),
                ('r23',0x10010100),
            ),
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r23', 0x10010100),
                ('r31', 0x100),
                (0x10010100 + 0x100, bytes.fromhex('abcdef01')),
                    ),

            'tests':(
                ('r0',0xabcdef01),
            ),
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r23', 0x10010100),
                ('r31', - 0x100),
                (0x10010100 - 0x100, bytes.fromhex('abcdef01')),
                    ),

            'tests':(
                ('r0',0xabcdef01),
            ),
        },
    ],  # 7C17F82E,"lwzx r0,r23,r31"

    '7C000026': [  # 7C000026,mfcr r0
        {
            'setup': (
                ('cr', 0x11223344),
                ('r0', 0x0)
            ),
            'tests': (
                ('r0', 0x11223344),
            ),
        },
    ],   # 7C000026,mfcr r0

    '7C1F0AA6': [  # 7C1F0AA6,"mfspr r0,IVPR"
        {
            'setup': (
                ('IVPR', 0x11223344),
                ('r0', 0x0)
            ),
            'tests': (
                ('r0', 0x11223344),
            ),
        },
    ],   # 7C1F0AA6,"mfspr r0,IVPR"

    # '7C0FF120': [  # 7C0FF120,"mtcrf 0xff,r0"
    #     {
    #         'setup': (
    #             ('r21', 0x11223344),
    #             ('r10', 0x0)
    #         ),
    #         'tests': (
    #             ('r10', 0x11223344),
    #         ),
    #     },
    # ],   # 7C0FF120,"mtcrf 0xff,r0"

    '7C03D1D7': [  # 7C03D1D7,"mullw. r0,r3,r26"
        {
            'setup': (
                ('r3', 0x11223344),
                ('r26', 0x0),
                ('r0', 0x0),
            ),
            'tests': (
                ('r0', 0x0),
                ('cr0', 0b0010)

            ),
        },
        {
            'setup': (
                ('r3', 0x2),
                ('r26', 0x8),
                ('r0', 0x0),
            ),
            'tests': (
                ('r0', 0x10),
                ('cr0', 0b0100)

            ),
        },
        {
            'setup': (
                ('r3', 0x7fffffff),
                ('r26', 0x2),
                ('r0', 0x0),
            ),
            'tests': (
                ('r0', 0xfffffffe),
                ('cr0', 0b1000)

            ),
        },
    ],   # 7C03D1D7,"mullw r0,r3,r26"

    '7C0700D0': [  # ('7C0700D0,"neg. r0,r7"
        {
            'setup': (
                ('r0', 0x0),
                ('r7', 0xc)
            ),
            'tests': (
                ('r0', 0xfffffff4),
            ),
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r7', 0xfffffff4),
            ),
            'tests': (
                ('r0', 0xc),
            ),
        },
    ], # 7C0700D1,"neg. r0,r7"

    '7C005B79': [  # 7C005B78,"or r0,r0,r11"
        {
            'setup': (
                ('r0', 0x10101010),
                ('r11', 0x11111111)
            ),
            'tests': (
                ('r0', 0x11111111),
                ('cr0', 0b0100)
            ),
        },
        {
            'setup': (
                ('r0', 0x12345678),
                ('r11', 0x20000000),
            ),
            'tests': (
                ('r0', 0x32345678),
                ('cr0', 0b0100)

            ),
        },
    ], # 7C005B78,"or r0,r0,r11"

    '7C00B031': [  # 7C00B031,"slw. r0,r0,r22"
        {
            'setup': (
                ('r0', 0x100),
                ('r22', 0x11111111)
            ),
            'tests': (
                ('r0', 0x2000000),
                ('cr0', 0b0100)
            ),
        },
        {
            'setup': (
                ('r0', 0x100),
                ('r22', 0x14),
            ),
            'tests': (
                ('r0', 0x10000000),
                ('cr0', 0b0100)

            ),
        },
        {
            'setup': (
                ('r0', 0x10000000),
                ('r22', 0x11111111)
            ),
            'tests': (
                ('r0', 0),
                ('cr0', 0b0010)
            ),
        },
    ], # 7C00B031,"slw. r0,r0,r22"

    '7C600631': [  # 7C600631,"sraw. r0,r3,r0"
        {
            'setup': (
                ('r0', 0b1100),
                ('r3', 0x1)
            ),
            'tests': (
                ('r0', 0),
                ('cr0', 0b0010)
            ),
        },
        {
            'setup': (
                ('r0', 0b1100),
                ('r3', 0b11),
            ),
            'tests': (
                ('r0', 0b0),
                ('cr0', 0b0010)

            ),
        },
        {
            'setup': (
                ('r0', 0x1000),
                ('r3', 0x3)
            ),
            'tests': (
                ('r0', 3),
                ('cr0', 0b0100)
            ),
        },
        {
            'setup': (
                ('r0', 0x80000000),
                ('r3', 0x3)
            ),
            'tests': (
                ('r0', 3),
                ('cr0', 0b0100),

            ),
        },
        {
            'setup': (
                ('r0', 0x10001),
                ('r3', 0x3)
            ),
            'tests': (
                ('r0', 0x1),
                ('cr0', 0b0100),
                ('xer', 0x0)

            ),
        },
        {
            'setup': (
                ('r0', 0x10001),
                ('r3', 0x0),
                ('xer', 0x20000000)
            ),
            'tests': (
                ('r0', 0),
                ('cr0', 0b0010),
                ('xer', 0x0)

            ),
        },
        {
            'setup': (
                ('r0', 0x10001),
                ('r3', 0x10000),
                ('xer', 0x20000000)
            ),
            'tests': (
                ('r0', 0x8000),
                ('cr0', 0b0100),
                ('xer', 0x0)

            ),

        },
        {
            'setup': (
                ('r0', 0x10001),
                ('r3', 0x10000),
                ('xer', 0x20000000)
            ),
            'tests': (
                ('r0', 0x8000),
                ('cr0', 0b0100),
                ('xer', 0x0)
            ),
        },

    ], # 7C600631,"sraw. r0,r3,r0"

    '7D604671': [  # 7D604671,"srawi. r0,r11,0x8"
        {
            'setup': (
                ('r11', 0x1),
                ('xer', 0x20000000)
            ),
            'tests': (
                ('r0', 0x0),
                ('cr0', 0b0010),
                ('xer', 0x0)
            ),
        },
        {
            'setup': (
                ('r11', 0x1000),
            ),
            'tests': (
                ('r0', 0x10),
                ('cr0', 0b0100)
            ),
        },
        {
            'setup': (
                ('r11', 0x80000000),
            ),
            'tests': (
                ('r0', 0xff800000),
                ('cr0', 0b1000),

            ),
        },
        {
            'setup': (
                ('r11', 0x10000),
                ('xer', 0x20000000)
            ),
            'tests': (
                ('r0', 0x100),
                ('cr0', 0b0100),
                ('xer', 0x0)
            ),
        },

    ], # 7D604671,"srawi r0,r11,0x8"

     '7C670431': [  # 7C670431,"srw. r7,r3,r0"
        {
            'setup': (
                ('r7', 0),
                ('r3', 0x10000000),
                ('r0', 0x20),
                ('xer', 0)
            ),
            'tests': (
                ('r7', 0x0),
                ('cr0', 0b0010),
                ('xer', 0)
            ),
        },
        {
            'setup': (
                ('r7', 0),
                ('r3', 0x10000000),
                ('r0', 0x10),
                ('xer', 0)
            ),
            'tests': (
                ('r7', 0x1000),
                ('cr0', 0b0100),
                ('xer', 0)
            ),
        },
        {
            'setup': (
                ('r7', 0),
                ('r3', 0x10000000),
                ('r0', 0xfffffff0),
                ('xer', 0)
            ),
            'tests': (
                ('r7', 0),
                ('cr0', 0b0010),
                ('xer', 0x0)
            ),
        },

    ], # 7C670431,"srw. r7,r3,r0"

    '7CA701EE': [  # 7CA701EE,"stbux r5,r7,r0"
        {
            'setup': (
                ('r5', 0x11223344),
                ('r0', 0x100),
                ('r7', 0x10010010)

            ),
            'tests': (
                ('r7', 0x10010110),
                (0x10010110, bytes.fromhex('44'))
            ),
        },
        # {
        #     'setup': (
        #         ('r5', 0x11223344),
        #         ('r0', -0x10),
        #         ('r7', 0x10010010)

        #     ),
        #     'tests': (
        #         ('r7', 0x10010000),
        #         (0x10010000, bytes.fromhex('44'))
        #     ),
        # },
    ], # 7CA701EE,"stbux r5,r7,r0"

    '7C14E9AE': [  # 7C14E9AE,"stbx r0,r20,r29"
        {
            'setup': (
                ('r20', 0x10010110),
                ('r0', 0x11223344),
                ('r29', 0x10)

            ),
            'tests': (
                (0x10010120, bytes.fromhex('44')),

            ),
        },
        # {
        #     'setup': (
        #         ('r20', 0x10010110),
        #         ('r0', 0x11223344),
        #         ('r29', -0x10)

        #     ),
        #     'tests': (
        #         (0x10010100, bytes.fromhex('44')),
        #     ),
        # },
    ], # 7C14E9AE,"stbx r0,r20,r29"

    '7CA53A79': [  # 7CA53A79,"xor. r5,r5,r7"
        {
            'setup': (
                ('r5', 0b10010110),
                ('r7', 0b11001111),
                ('cr0', 0b0000)

            ),
            'tests': (
                ('r5', 0b01011001),
                ('cr0', 0b0100)

            ),
        },
    ], # 7CA53A79,"xor. r5,r5,r7"

    '7C0000A6': [  # 7C0000A6,mfmsr r0
        {
            'setup': (
                ('msr', 0x9000),
                ('r0', 0),

            ),
            'tests': (
                ('r0', 0x9000),

            ),
        },
    ], # 7C0000A6,mfmsr r0

# '7FA0E8F8': [  # 7FA0E8F8,"not r0,r29"
    #     {
    #         'setup': (
    #             ('r0', 0x0),
    #             ('r29', 0x0)
    #         ),
    #         'tests': (
    #             ('r0', 0xffffffff),
    #         ),
    #     },
    #     {
    #         'setup': (
    #             ('r0', 0x0),
    #             ('r29', 0xffffffff),
    #         ),
    #         'tests': (
    #             ('r0', 0x0),
    #         ),
    #     },
    # ], # 7FA0E8F8,"not r0,r29"


    # '7C0700D1': [  # ('7C0700D1,"neg. r0,r7"
    #     {
    #         'setup': (
    #             ('r0', 0x0),
    #             ('r7', 0xc)

    #         ),

    #         'tests': (
    #             ('r0', 0xfffffffffffffff4),
    #             ('cr0', 0b1000)

    #         ),
    #     },
    #     {
    #         'setup': (
    #             ('r0', 0x0),
    #             ('r7', 0xfffffffffffffff4),


    #         ),

    #         'tests': (
    #             ('r0', 0xc),
    #             ('cr0', 0b0100)

    #         ),
    #     },
    # ], # 7C0700D1,"neg. r0,r7"

    '7EAAAB79': [  # 7EAAAB79,"mr. r10,r21"
        {
            'setup': (
                ('r21', 0x81223344),
                ('r10', 0x0),
                ('cr0', 0b0000)
            ),
            'tests': (
                ('r10', 0x81223344),
                ('cr0', 0b1000)
            ),
        },
        {
            'setup': (
                ('r21', 0x11223344),
                ('r10', 0x0),
                ('cr0', 0b0000)
            ),
            'tests': (
                ('r10', 0x11223344),
                ('cr0', 0b0100)
            ),
        },
        {
            'setup': (
                ('r21', 0x0),
                ('r10', 0x12345678),
                ('cr0', 0b0000)
            ),
            'tests': (
                ('r10', 0x0),
                ('cr0', 0b0010)
            ),
        },

    ],   # 7EAAAB78,"mr r10,r21"

    # '73408E0C': [  # 73408E0C,"e_add2i. r0,0xd60c"
    #     {
    #         'setup': (
    #             ('r0', 1),
    #         ),
    #         'tests': (
    #             ('r0', 0xd60d),
    #             ('cr0', 0b0100)
    #         ),
    #     },
    # ],   # 73408E0C,"e_add2i. r0,0xd60c"

    # '70009003': [  # 70009003,"e_add2is r0,0x3"
    #     {
    #         'setup': (
    #             ('r0', 1),
    #         ),
    #         'tests': (
    #             ('r0', 0x40000),
    #             ('cr0', 0b0100)
    #         ),
    #     },
    # ],   # 70009003,"e_add2is r0,0x3"

    # '7000C801': [  # 7000C801,"e_and2i. r0,0x1"
    #     {
    #         'setup': (
    #             ('r0', 1),
    #         ),
    #         'tests': (
    #             ('r0', 0x1),
    #             ('cr0', 0b0100)
    #         ),
    #     },
    # ],   # 7000C801,"e_and2i. r0,0x1"

    # '7010E800': [  # 7010E800,"e_and2is. r0,0x8000"
    #     {
    #         'setup': (
    #             ('r0', 1),
    #         ),
    #         'tests': (
    #             ('r0', 0x1),
    #             ('cr0', 0b0100)
    #         ),
    #     },
    # ],   # 7010E800,"e_and2is. r0,0x8000"

    # '79FB59A6': [  # 79FB59A6,e_b 0x3ffb9f06
    #     {
    #         'setup': (
    #             ('pc', 0x10000534),
    #         ),
    #         'tests': (
    #             ('pc', 0x3ffb9f06),

    #         ),
    #     },
    # ],   # 79FB59A6,e_b 0x3ffb9f06

    # '79F6BD8F': [  # 79F6BD8F,e_bl 0x3ff702ee
    #     {
    #         'setup': (
    #             ('pc', 0x10000534),
    #         ),
    #         'tests': (
    #             ('pc', 0x3ff702ee),

    #         ),
    #     },
    # ],   # 79F6BD8F,e_bl 0x3ff702ee

    '7A00FE4E': [  # e_bge [cr0,] 0x3ffffe4e
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b1000),    # LT bit, don't branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x40000004),
                ('lr', 0x0),
            ),
        },
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b0100),    # GT bit, branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x3ffffe4e),
                ('lr', 0x0),
            ),
        },
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b0010),    # EQ bit, branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x3ffffe4e),
                ('lr', 0x0),
            ),
        },
    ],

    # '7040A80B': [  # 7040A80B,"e_cmpl16i r0,0x100b"
    #     {
    #         'setup': (
    #             ('r0', 0x1234),
    #         ),
    #         'tests': (
    #             ('cr0', 0b0100),
    #         ),
    #     },
    # ],   # 7040A80B,"e_cmpl16i r0,0x100b"

    # '3004FFFF': [  # 3004FFFF,"e_lbz r0,-0x1(r4)"
    # {
    #         'setup': (
    #                             # Set the register to be filled with some generic data
    #                     ('r0', 0x0102030405060708),
    #                             # Fill memory with an 8-byte pattern
    #                     (0x000000f8, bytes.fromhex('F1F2F3F4F5F6F7F8')),
    #                             # Set the address to be the last byte of the pattern
    #                     ('r4', 1 + 0x00000000000000FF),
    #         ),
    #         'tests': (
    #             ('r0', 0xF8),
    #         ),
    #     }
    # ],   # 3004FFFF,"e_lbz r0,-0x1(r4)"

    # '701F7FED': [  # 701F7FED,"e_li r0,-0x13"
    #     {
    #         'setup': (
    #             ('r0', 0x50),
    #         ),
    #         'tests': (
    #             ('r0', 0xFFFFFFFFFFFFFFF3),

    #         ),
    #     },
    # ],   # 701F7FED,"e_li r0,-0x13"

    # '1B010801': [  # 1B010801,"e_lmw r24,0x1(r1)"
    #     {
    #         'setup': (
    #             ('r1', 0x10000534),
    #             ('r24', 0x0),
    #             ('0x10000534', bytes.fromhex('1234567890ABCDEF'))
    #         ),
    #         'tests': (
    #             ('r24', 0x12345678),
    #             ('r25', 0x12345678),
    #             ('r26', 0x12345678),
    #         ),
    #     },
    # ],   # 1B010801,"e_lmw r24,0x1(r1)"

    '0480': [  # 0480,"se_add r0,r24"

        {
            'setup': (
                ('r0', 0x10000534),
                ('r24', 0x0),
            ),
            'tests': (
                ('r0', 0x10000534),
            ),
        },
    ],   # 0480,"se_add r0,r24"

    '2000': [  # 2000,"se_addi r0,0x1"

        {
            'setup': (
                ('r0', 0x10000534),
            ),
            'tests': (
                ('r0', 0x10000535),
            ),
        },
    ],   # 2000,"se_addi r0,0x1"

 '47B0': [  # 47B0,"se_and. r0,r27"

        {
            'setup': (
                ('cr0', 0x0),
                ('r0', 0xffffffff),
                ('r27', 0x12345678),
                ('cr0', 0b0000)
            ),
            'tests': (
                ('r0', 0x12345678),
                ('cr0', 0b0100)
            ),
        },
        {
            'setup': (
                ('r0', 0xffffffff),
                ('r27', 0x82345678),
                ('cr0', 0b0000)
            ),
            'tests': (
                ('r0', 0x82345678),
                ('cr0', 0b1000)
            ),
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r27', 0x82345678),
                ('cr0', 0b0000)
            ),
            'tests': (
                ('r0', 0x0),
                ('cr0', 0b0010)
            ),
        },
    ],   # 47B0,"se_and. r0,r27"

'45B0': [  # 45B0,"se_andc r0,r27"

        {
            'setup': (
                ('r0', 0x12345678),
                ('r27', 0x88888888),  # r0 is ANDed with the One's complement of the value in this register (0b10100000)
            ),
            'tests': (
                ('r0', 0x12345670),
            ),
        },
    ],   # 45B0,"se_andc r0,r27"

'2E10': [  # 2E10,"se_andi r0,0x1"
        {
            'setup': (
                ('r0', 0b10000),  # (ANDed with 0b0001)
            ),
            'tests': (
                ('r0', 0b0000),
            ),
        },
        {
            'setup': (
                ('r0', 0b0111),
            ),
            'tests': (
                ('r0', 0b0001),
            ),
        }
    ],  # # 2E10,"se_andi r0,0x1"

'E880': [  # E880,se_b -0x100
        {
            'setup': (
                ('pc', 0x10001110),
            ),
            'tests': (
                ('pc', 0x10001010),
            ),
        },
    ],  # #E880,se_b 0x40004460

'6000': [  # 6000,"se_bclri r0,0x0"
        {
            'setup': (
                ('r0', 0xffffffff),
            ),
            'tests': (
                ('r0', 0x7fffffff),
            ),
        },
    ],  # 6000,"se_bclri r0,0x0"

'6010': [  # 6010,"se_bclri r0,0x1"
        {
            'setup': (
                ('r0', 0xffffffff),
            ),
            'tests': (
                ('r0', 0xbfffffff),
            ),
        },
    ],  # 6010,"se_bclri r0,0x1"

'6100': [  # 6100,"se_bclri r0,0x10"
        {
            'setup': (
                ('r0', 0xffffffff),
            ),
            'tests': (
                ('r0', 0xffff7fff),
            ),
        },
    ],  # 6100,"se_bclri r0,0x10"

'0006': [  # 0006,se_bctr
        {
            'setup': (
                ('ctr', 0x10001010),
                ('pc', 0x40004560)
            ),
            'tests': (
                ('pc', 0x10001010),
            ),
        },
    ],  # 0006,se_bctr

'0007': [  # 0007,se_bctrl
        {
            'setup': (
                ('ctr', 0x10001010),
                ('pc', 0x40004560),
                ('lr', 0x10000010)
            ),
            'tests': (
                ('pc', 0x10001010),
                ('lr', 0x40004562)
            ),
        },
    ],  # 0007,se_bctrl

'E696': [  # E696,se_beq -0xD4
        {
            'setup': (
                ('pc', 0x40004560),
                ('cr0', 0b0000)
            ),
            'tests': (
                ('pc', 0x40004562),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560),
                ('cr0', 0b0010)
            ),
            'tests': (
                ('pc', 0x4000448C),
            ),
        },
    ],  # E696,se_beq 0x4000448c

    'E08C': [  # E08C,se_bge -0xE8
        {
            'setup': (
                ('pc', 0x400045E8),
                ('cr0', 0b1000)
            ),
            'tests': (
                ('pc', 0x400045EA),
            ),
        },
        {
            'setup': (
                ('pc', 0x400045E8),
                ('cr0', 0b0010)
            ),
            'tests': (
                ('pc', 0x40004500),
            ),
        },
        {
            'setup': (
                ('pc', 0x400045E8),
                ('cr0', 0b0100)
            ),
            'tests': (
                ('pc', 0x40004500),
            ),
        },

    ],  # E08C,se_bge 0x40004478

    '6290': [  # 6290,"se_bgeni r0,0x9"
        {
            'setup': (
                ('r0', 0),
            ),
            'tests': (
                ('r0', 0x00400000),
            ),
        },
    ],  # 6290,"se_bgeni r0,0x9"

    '6278': [  # 6728,"se_bgeni r24,0x7"
        {
            'setup': (
                ('r24', 0x12345678),
            ),
            'tests': (
                ('r24', 0x01000000),
            ),
        },
    ],  # 6278,"se_bgeni r24,0x7"

    '6200': [  # 6200,"se_bgeni r0,0x0"
        {
            'setup': (
                ('r0', 0x12345678),
            ),
            'tests': (
                ('r0', 0x80000000),
            ),
        },
    ],  # 6200,"se_bgeni r0,0x0"

    'E5A6': [  # E5A6,se_bgt 0x400044ac
        {
            'setup': (
                ('pc', 0x400045B4),
                ('cr0', 0b1000)
            ),
            'tests': (
                ('pc', 0x400045B6),
            ),
        },
        {
            'setup': (
                ('pc', 0x400045B4),
                ('cr0', 0b0010)
            ),
            'tests': (
                ('pc', 0x400045B6),
            ),
        },
        {
            'setup': (
                ('pc', 0x400045B4),
                ('cr0', 0b0100)
            ),
            'tests': (
                ('pc', 0x40004500),
            ),
        },
    ],  #E5A6,se_bgt 0x400044ac

    'E980': [  # E980,se_bl -0x100
        {
            'setup': (
                ('pc', 0x400045B4),
            ),
            'tests': (
                ('pc', 0x400044B4),
            ),
        },
        {
            'setup': (
                ('pc', 0x400046B6),
               ),
            'tests': (
                ('pc', 0x400045B6),
            ),
        },
    ],  # E980,se_bl 0x40004460

 'E188': [  # E188,se_ble -0xF0
        {
            'setup': (
                ('pc', 0x40004560),
                ('cr0', 0b1000)
            ),
            'tests': (
                ('pc', 0x40004470),
            ),
        },
        {
            'setup': (
                ('pc', 0x400045F0),
                ('cr0', 0b0010)
            ),
            'tests': (
                ('pc', 0x40004500),
            ),
        },
        {
            'setup': (
                ('pc', 0x400045F0),
                ('cr0', 0b0100)
            ),
            'tests': (
                ('pc', 0x400045F2),
            ),
        },
    ],  # E188,se_ble -0xF0

    '0004': [  # 0004,se_blr
        {
            'setup': (
                ('lr', 0x40006540),
            ),
            'tests': (
                ('pc', 0x40006540),
            ),
        },
        {
            'setup': (
                ('pc', 0x400045F0),
                ('lr',0x40004560)
            ),
            'tests': (
                ('pc', 0x40004560),
            ),
        },
    ],  # 0004,se_blr

    '0005': [  # 000l,se_blrl
        {
            'setup': (
                ('pc', 0x400045F0),
                ('lr',0x40004560)
            ),
            'tests': (
                ('pc', 0x40004560),
                ('lr', 0x400045f2)
            ),
        },
        {
            'setup': (
                ('pc', 0x400046F0),
                ('lr',0x40004560)
            ),
            'tests': (
                ('pc', 0x40004560),
                ('lr', 0x400046f2)
            ),
        },
    ],  # 0005,se_blrl

    'E486': [  # E486,se_blt -0xF4
        {
            'setup': (
                ('pc', 0x400045f4),
                ('cr0', 0b1000)
            ),
            'tests': (
                ('pc', 0x40004500),
            ),
        },
        {
            'setup': (
                ('pc', 0x400045F4),
                ('cr0', 0b0010)
            ),
            'tests': (
                ('pc', 0x400045F6),
            ),
        },
        {
            'setup': (
                ('pc', 0x400045F4),
                ('cr0', 0b0100)
            ),
            'tests': (
                ('pc', 0x400045F6),
            ),
        },
    ],  # E486,se_blt 0x4000446c

    '2C00': [  # 2C00,"se_bmaski r0,0x0"
        {
            'setup': (
                ('r0', 0x12345678),
            ),
            'tests': (
                ('r0', 0xffffffff),
            ),
        },

    ],  # 2C00,"se_bmaski r0,0x0"

    '2D00': [  # 2C00,"se_bmaski r0,0x10"
        {
            'setup': (
                ('r0', 0x12345678),
            ),
            'tests': (
                ('r0', 0xffff),
            ),
        },

    ],  # 2C00,"se_bmaski r0,0x0"

    '2D80': [  # 2D80,"se_bmaski r0,0x18"
        {
            'setup': (
                ('r0', 0x12345678),
            ),
            'tests': (
                ('r0', 0xffffff),
            ),
        },

    ],  # 2D80,"se_bmaski r0,0x18"

     'E281': [  # E281,se_bne -0xFE
        {
            'setup': (
                ('pc', 0x400045FE),
                ('cr0', 0b1000)
            ),
            'tests': (
                ('pc', 0x40004500),
            ),
        },
        {
            'setup': (
                ('pc', 0x400045FE),
                ('cr0', 0b0100)
            ),
            'tests': (
                ('pc', 0x40004500),
            ),
        },
       {
            'setup': (
                ('pc', 0x400045FE),
                ('cr0', 0b0010)
            ),
            'tests': (
                ('pc', 0x40004600),
            ),
        },
    ],  # E281,se_bne -0xFE

    '6400': [  # 6400,"se_bseti r0,0x0"

        {
            'setup': (
                ('r0', 0),
            ),
            'tests': (
                ('r0', 0x80000000),
            ),
        },
    ],  # 6400,"se_bseti r0,0x0"

    '6410': [  # 6410,"se_bseti r0,0x1"

        {
            'setup': (
                ('r0', 0),
            ),
            'tests': (
                ('r0', 0x40000000),
            ),
        },
    ],  # 6410,"se_bseti r0,0x1"

    '6600': [  # 6600,"se_btsti r0,0x0"

        {
            'setup': (
                ('r0', 0),
                ('xer', 0x0)
            ),
            'tests': (
                ('cr0', 0b0010),
            ),
        },
        {
            'setup': (
                ('r0', 0xffffffff),
                ('xer', 0x80000000)
            ),
            'tests': (
                ('cr0', 0b0101),
            ),
        },
        {
            'setup': (
                ('r0', 0x7fffffff),
                ('xer', 0x80000000)
            ),
            'tests': (
                ('cr0', 0b0011),
            ),
        },

    ],  # 6600,"se_btsti r0,0x0"  6700,"se_btsti r0,0x10"

    '6700': [  # 6700,"se_btsti r0,0x10"

        {
            'setup': (
                ('r0', 0),
                ('xer', 0x0)
            ),
            'tests': (
                ('cr0', 0b0010),
            ),
        },
        {
            'setup': (
                ('r0', 0xffffffff),
                ('xer', 0x80000000)
            ),
            'tests': (
                ('cr0', 0b0101),
            ),
        },
        {
            'setup': (
                ('r0', 0xffff7fff),
                ('xer', 0x80000000)
            ),
            'tests': (
                ('cr0', 0b0011),
            ),
        },

    ],  # 6700,"se_btsti r0,0x10"

    '0C80': [  # 0C80,"se_cmp r0,r24"
        {
            'setup': (
                ('r0', 0),
                ('r24', 0x12345678),
                ('xer', 0x80000000)
            ),
            'tests': (
                ('cr0', 0b1001),
            ),
        },
        {
            'setup': (
                ('r0', 0),
                ('r24', 0x82345678),
                ('xer', 0x80000000)
            ),
            'tests': (
                ('cr0', 0b0101),
            ),
        },
        {
            'setup': (
                ('r0', 0x82345678),
                ('r24', 0x82345678),
                ('xer', 0x80000000)
            ),
            'tests': (
                ('cr0', 0b0011),
            ),
        },
    ],  # 0C80,"se_cmp r0,r24"

    '2A00': [  # 2A00,"se_cmpi r0,0x0"
        {
            'setup': (
                ('r0', 0x80000000),
                ('xer', 0x80000000)
            ),
            'tests': (
                ('cr0', 0b1001),
            ),
        },
        {
            'setup': (
                ('r0', 0),
                ('xer', 0x80000000)
            ),
            'tests': (
                ('cr0', 0b0011),
            ),
        },
        {
            'setup': (
                ('r0', 1),
                ('xer', 0x0)
            ),
            'tests': (
                ('cr0', 0b0100),
            ),
        },
    ],  # 2A00,"se_cmpi r0,0x0"

    '0D80': [  # 0D80,"se_cmpl r0,r24"
        {
            'setup': (
                ('r0', 0x80000000),
                ('r24', 0x80000000),
                ('xer', 0x80000000)
            ),
            'tests': (
                ('cr0', 0b0011),
            ),
        },
        {
            'setup': (
                ('r0', 0x60000000),
                ('r24', 0x80000000),
                ('xer', 0x80000000)
            ),
            'tests': (
                ('cr0', 0b1001),
            ),
        },
        {
            'setup': (
                ('r0', 0x90000000),
                ('r24', 0x80000000),
                ('xer', 0x80000000)
            ),
            'tests': (
                ('cr0', 0b00101),
            ),
        },
        {
            'setup': (
                ('r0', 0x80000000),
                ('r24', 0x80000000),
                ('xer', 0x0)
            ),
            'tests': (
                ('cr0', 0b0010),
            ),
        },
    ],  # 0D80,"se_cmpl r0,r24"

        '2200': [  #2200,"se_cmpli r0,0x1"
        {
            'setup': (
                ('r0', 0x80000000),
                ('xer', 0x80000000)
            ),
            'tests': (
                ('cr0', 0b0101),
            ),
        },
        {
            'setup': (
                ('r0', 0x60000000),
                ('xer', 0x80000000)
            ),
            'tests': (
                ('cr0', 0b0101),
            ),
        },
        {
            'setup': (
                ('r0', 0x0),
                ('xer', 0x0)
            ),
            'tests': (
                ('cr0', 0b1000),
            ),
        },
        {
            'setup': (
                ('r0', 0x1),
                ('xer', 0x0)
            ),
            'tests': (
                ('cr0', 0b0010),
            ),
        },
    ],  # 2200,"se_cmpli r0,0x1"

    # '00D0': [  # 00D0,se_extsb r0
    #     {
    #         'setup': (
    #             ('r0', 0xfe),
    #         ),
    #         'tests': (
    #             ('r0', 0xfffffffe),
    #         ),
    #     },
    #     {
    #         'setup': (
    #             ('r0', 0x77777770),
    #         ),
    #         'tests': (
    #             ('r0', 0x70),
    #         ),
    #     },
    # ],  # 00D0,se_extsb r0

    '00C0': [  # 00C0,se_extzb r0
        {
            'setup': (
                ('r0', 0x123456fe),
            ),
            'tests': (
                ('r0', 0xfe),
            ),
        },
        {
            'setup': (
                ('r0', 0x77777770),
            ),
            'tests': (
                ('r0', 0x70),
            ),
        },
    ],  # 00C0,se_extzb r0

    '00E0': [  # 00C0,se_extzb r0
        {
            'setup': (
                ('r0', 0x123456fe),
            ),
            'tests': (
                ('r0', 0x56fe),
            ),
        },
        {
            'setup': (
                ('r0', 0x77777770),
            ),
            'tests': (
                ('r0', 0x7770),
            ),
        },
    ],  # 00C0,se_extzb r0

    '8008': [  # se_lbz r0,0x0(r24)
        {
            'setup': (
                ('r0', 0x0),
                ('r24', 0x10000100),
                (0x10000100, bytes.fromhex('12345678'))
            ),
            'tests': (
                ('r0', 0x12),
            ),
        },
    ],

    'A008': [  # se_lhz r0,0x0(r24)
        {
            'setup': (
                ('r0', 0x0),
                ('r24', 0x10000100),
                (0x10000100, bytes.fromhex('12345678'))
            ),
            'tests': (
                ('r0', 0x1234),
            ),
        },
    ],

    'C008': [  # se_lwz r0,0x0(r24)
        {
            'setup': (
                ('r0', 0x0),
                ('r24', 0x10000100),
                (0x10000100, bytes.fromhex('12345678'))
            ),
            'tests': (
                ('r0', 0x12345678),
            ),
        },
    ],

    '4800': [  # 4800,"se_li r0,0x0"
        {
            'setup': (
                ('r0', 0x123456fe),
            ),
            'tests': (
                ('r0', 0x0),
            ),
        },
    ],  # 4800,"se_li r0,0x0"

    '4810': [  # 4810,"se_li r0,0x1"
        {
            'setup': (
                ('r0', 0x123456fe),
            ),
            'tests': (
                ('r0', 0x1),
            ),
        },
    ],  # 4810,"se_li r0,0x1"

    '0330': [  # 0330,"se_mfar r0,r11"
        {
            'setup': (
                ('r0', 0x123456fe),
                ('r11', 0x77777777)
            ),
            'tests': (
                ('r0', 0x77777777),
            ),
        },
    ],  # 0330,"se_mfar r0,r11"

    '03B0': [  # 03B0,"se_mfar r0,r19"
        {
            'setup': (
                ('r0', 0x123456fe),
                ('r19', 0x77777777)
            ),
            'tests': (
                ('r0', 0x77777777),
            ),
        },
    ],  # 03B0,"se_mfar r0,r19"

    '00A0': [  # 00A0,se_mfctr r0
        {
            'setup': (
                ('r0', 0x123456fe),
                ('ctr', 0x77777777)
            ),
            'tests': (
                ('r0', 0x77777777),
            ),
        },
    ],  # 00A0,se_mfctr r0

    '0080': [  # 0080,se_mflr r0
        {
            'setup': (
                ('r0', 0x123456fe),
                ('lr', 0x77777777)
            ),
            'tests': (
                ('r0', 0x77777777),
            ),
        },
    ],  # 0080,se_mflr r0

    '0190': [  # 0190,"se_mr r0,r25"
        {
            'setup': (
                ('r0', 0x123456fe),
                ('r25', 0x77777777)
            ),
            'tests': (
                ('r0', 0x77777777),
            ),
        },
    ],  # 0190,"se_mr r0,r25"

    '0202': [  # 0202,"se_mtar r10,r0"
        {
            'setup': (
                ('r10', 0x123456fe),
                ('r0', 0x77777777)
            ),
            'tests': (
                ('r10', 0x77777777),
            ),
        },
    ],  # 0202,"se_mtar r10,r0"

    '00B0': [  # 00B0,se_mtctr r0
        {
            'setup': (
                ('r0', 0x77777777),
                ('ctr', 0x0)

            ),
            'tests': (
                ('ctr', 0x77777777),
            ),
        },
    ],  # 00B0,se_mtctr r0

    '0090': [  # 0090,se_mtlr r0
        {
            'setup': (
                ('r0', 0x77777777),
                ('lr', 0x0)

            ),
            'tests': (
                ('lr', 0x77777777),
            ),
        },
    ],  # 0090,se_mtlr r0

    '0038': [  # 0038,se_neg r24
        {
            'setup': (
                ('r24', 0x77777777),

            ),
            'tests': (
                ('r24', 0x88888889),
            ),
        },
    ],  # 0038,se_neg r24

    '0020': [  # 0020,se_not r0
        {
            'setup': (
                ('r0', 0x77777777),

            ),
            'tests': (
                ('r0', 0x88888888),
            ),
        },
    ],  # 0020,se_not r0


    '4400': [  # 4400,"se_nop"
        {
            'setup': (
                ('r0', 0x77777777),

            ),
            'tests': (
                ('r0', 0x77777777),
            ),
        },
    ],  # 4400,"se_or r0,r0"

    '4480': [  # 4480,"se_or r0,r24"
        {
            'setup': (
                ('r0', 0x77777777),
                ('r24', 0xffffffff)
            ),
            'tests': (
                ('r0', 0xffffffff),
            ),
        },
        {
            'setup': (
                ('r0', 0x77777777),
                ('r24', 0x88888888)

            ),
            'tests': (
                ('r0', 0xffffffff),
            ),
        },
        {
            'setup': (
                ('r0', 0x77777777),
                ('r24', 0x0)

            ),
            'tests': (
                ('r0', 0x77777777),
            ),
        },
    ],  # 4480,"se_or r0,r24"


    '4290': [  # 4290,"se_slw r0,r25"
        {
            'setup': (
                ('r0', 0x4),
                ('r25', 0x8)

            ),
            'tests': (
                ('r0', 0x400),
            ),
        },
        {
            'setup': (
                ('r0', 0x80000000),
                ('r25', 0x4)

            ),
            'tests': (
                ('r0', 0x0),
            ),
        },


    ],  # 4290,"se_slw r0,r25"  6D03,"se_slwi r3,0x10"

    '6D03': [  # 6D03,"se_slwi r3,0x10"
        {
            'setup': (
                ('r3', 0x4),

            ),
            'tests': (
                ('r3', 0x40000),
            ),
        },
        {
            'setup': (
                ('r3', 0x80000000),

            ),
            'tests': (
                ('r3', 0x0),
            ),
        },


    ],  #  6D03,"se_slwi r3,0x10"

    '6A30': [  # 6A30,"se_srawi r0,0x3"
        {
            'setup': (
                ('r0', 0x8),

            ),
            'tests': (
                ('r0', 0x1),
            ),
        },
        {
            'setup': (
                ('r0', 0x1),

            ),
            'tests': (
                ('r0', 0x0),
            ),
        },


    ],  #  6A30,"se_srawi r0,0x3"

    '40B0': [  # 40B0,"se_srw r0,r27"
        {
            'setup': (
                ('r0', 0x8),
                ('r27', 0x3)

            ),
            'tests': (
                ('r0', 0x1),
            ),
        },
        {
            'setup': (
                ('r0', 0x800000),
                ('r27', 0x10)

            ),
            'tests': (
                ('r0', 0x80),
            ),
        },
        {
            'setup': (
                ('r0', 0x80000000),
                ('r27', 0x21)
            ),
            'tests': (
                ('r0', 0x0),
            ),
        },

    ],  # 40B0,"se_srw r0,r27"

    '6810': [  # 6810,"se_srwi r0,0x1"
        {
            'setup': (
                ('r0', 0x8),

            ),
            'tests': (
                ('r0', 0x4),
            ),
        },
        {
            'setup': (
                ('r0', 0x800000),

            ),
            'tests': (
                ('r0', 0x400000),
            ),
        },
        {
            'setup': (
                ('r0', 0x80000000),
            ),
            'tests': (
                ('r0', 0x40000000),
            ),
        },

    ],  # 6810,"se_srwi r0,0x1"


    '9008':  # 9008,"se_stb r0,0x0(r24)"
        [
            {
                'setup': (
                    ('r0', 0x12345678),
                    ('r24', 0x10010110),
                    (0x10010110, bytes.fromhex('00000000'))

                ),

                'tests': (
                    (0x10010110, bytes.fromhex('78000000')),

                ),
            },
        ], # 9008,"se_stb r0,0x0(r24)"

    '9108':  # 9108,"se_stb r0,0x1(r24)"

        [
            {
                'setup': (
                    ('r0', 0x12345678),
                    ('r24', 0x10010110 - 0x1 ),
                    (0x10010110, bytes.fromhex('00000000'))

                ),

                'tests': (
                    (0x10010110, bytes.fromhex('78000000')),

                ),
            },
        ], # 9108,"se_stb r0,0x1(r24)"


    'B801':  # B801,"se_sth r0,0x10(r1)"

        [
            {
                'setup': (
                    ('r0', 0x12345678),
                    ('r1', 0x10010110 - 0x10 ),
                    (0x10010110, bytes.fromhex('00000000'))

                ),

                'tests': (
                    (0x10010110, bytes.fromhex('56780000')),

                ),
            },
        ], # B801,"se_sth r0,0x10(r1)"

    'D40F':  # D40F,"se_stw r0,0x10(r31)"

        [
            {
                'setup': (
                    ('r0', 0x12345678),
                    ('r31', 0x10010110 - 0x10 ),
                    (0x10010110, bytes.fromhex('00000000'))

                ),

                'tests': (
                    (0x10010110, bytes.fromhex('12345678')),

                ),
            },
        ], # D40F,"se_stw r0,0x10(r31)"


    '06B0':  # 06B0,"se_sub r0,r27"
        [
            {
                'setup': (
                    ('r0', 0x12345678),
                    ('r27', 0x2)
                ),
                'tests': (
                  ('r0', 0x12345676),
                ),
            },
            {
                'setup': (
                    ('r0', 0xfffffffe),
                    ('r27', 0x2)
                ),
                'tests': (
                  ('r0', 0xfffffffc),
                ),
            },
            {
                'setup': (
                    ('r0', 0xfffffffe),
                    ('r27', 0xfffffffe)
                ),

                'tests': (
                  ('r0', 0x0),
                ),
            },
            {
                'setup': (
                    ('r0', 0x0),
                    ('r27', 0xfffffffe)
                ),

                'tests': (
                  ('r0', 0x2),
                ),
            },
        ], # 06B0,"se_sub r0,r27"

    '0790':  # 0790,"se_subf r0,r25"
        [
            {
                'setup': (
                    ('r0', 0x12345678),
                    ('r25', 0x2)
                ),
                'tests': (
                  ('r0', 0x12345676),
                ),
            },
            {
                'setup': (
                    ('r0', 0xfffffffe),
                    ('r25', 0x2)
                ),
                'tests': (
                  ('r0', 0xfffffffc),
                ),
            },
            {
                'setup': (
                    ('r0', 0xfffffffe),
                    ('r25', 0xfffffffe)
                ),

                'tests': (
                  ('r0', 0x0),
                ),
            },
            {
                'setup': (
                    ('r0', 0x0),
                    ('r25', 0xfffffffe)
                ),

                'tests': (
                  ('r0', 0x2),
                ),
            },
        ], # 0790,"se_subf r0,r25"

    '2400':  # 2400,"se_subi r0,0x1"
        [
            {
                'setup': (
                    ('r0', 0x12345678),
                ),
                'tests': (
                    ('r0', 0x12345677),
                ),
            },
            {
                'setup': (
                    ('r0', 0xfffffffe),
                ),

                'tests': (
                  ('r0', 0xfffffffd),
                ),
            },
            {
                'setup': (
                    ('r0', 0x0),
                ),

                'tests': (
                  ('r0', 0xffffffff),
                ),
            },
        ], # 2400,"se_subi r0,0x1"

    # '2600':  # 2600,"se_subi. r0,0x1"
    #     [
    #         {
    #             'setup': (
    #                 ('r0', 0x12345678),
    #             ),
    #             'tests': (
    #                 ('r0', 0x12345677),
    #                 ('cr0', 0b0100)
    #             ),
    #         },
    #         {
    #             'setup': (
    #                 ('r0', 0xfffffffe),
    #             ),2600
    #             'tests': (
    #                 ('r0', 0xfffffffd),
    #                 ('cr0', 0b1000)
    #             ),
    #         },
    #         {
    #             'setup': (
    #                 ('r0', 0xfffffffe),
    #             ),

    #             'tests': (
    #               ('r0', 0x0),
    #               ('cr0', 0b0010)
    #             ),
    #         },
    #         {
    #             'setup': (
    #                 ('r0', 0x0),
    #                 ('xer', 0x20000000)
    #             ),

    #             'tests': (
    #                 ('r0', 0x2),
    #                 ('cr0', 0b0011)
    #             ),
    #         },
    #     ], # 2600,"se_subi. r0,0x1"

    'E711': [  # E711,se_bso 0x22

        {
            'setup': (
                ('pc', 0x10001110),
                ('cr0', 0b0011)
            ),
            'tests': (
                ('pc', 0x10001132),
            ),
        },
         {
            'setup': (
                ('pc', 0x10001110),
                ('cr0', 0b0010)
            ),
            'tests': (
                ('pc', 0x10001112),
            ),
        },
    ],  # #E880,se_b 0x40004460

    'E211': [  # E211,se_bne 0x22

        {
            'setup': (
                ('pc', 0x10001110),
                ('cr0', 0b0101)
            ),
            'tests': (
                ('pc', 0x10001132),
            ),
        },
         {
            'setup': (
                ('pc', 0x10001110),
                ('cr0', 0b0010)
            ),
            'tests': (
                ('pc', 0x10001112),
            ),
        },
    ],  # #E880,se_b 0x40004460

    '7A00FE4F': [  # e_bgel [cr0,] 0x3ffffe4e
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b1000),    # LT bit, don't branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x40000004),
                ('lr', 0x40000004),
            ),
        },
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b0100),    # GT bit, branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x3ffffe4e),
                ('lr', 0x40000004),
            ),
        },
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b0010),    # EQ bit, branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x3ffffe4e),
                ('lr', 0x40000004),
            ),
        },
    ],

    '7A01FE4E': [  # e_ble [cr0,] 0x3ffffe4e
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b1000),    # LT bit, branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x3ffffe4e),
                ('lr', 0x0),
            ),
        },
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b0100),    # GT bit, don't branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x40000004),
                ('lr', 0x0),
            ),
        },
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b0010),    # EQ bit, branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x3ffffe4e),
                ('lr', 0x0),
            ),
        },
    ],

    '7A01FE4F': [  # e_blel [cr0,] 0x3ffffe4e
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b1000),    # LT bit, branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x3ffffe4e),
                ('lr', 0x40000004),
            ),
        },
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b0100),    # GT bit, don't branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x40000004),
                ('lr', 0x40000004),
            ),
        },
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b0010),    # EQ bit, branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x3ffffe4e),
                ('lr', 0x40000004),
            ),
        },
    ],

    '7A02FE4E': [  # e_bne [cr0,] 0x3ffffe4e
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b1000),    # LT bit, branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x3ffffe4e),
                ('lr', 0x0),
            ),
        },
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b0100),    # GT bit, branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x3ffffe4e),
                ('lr', 0x0),
            ),
        },
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b0010),    # EQ bit, don't branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x40000004),
                ('lr', 0x0),
            ),
        },
    ],

    '7A02FE4F': [  # e_bnel [cr0,] 0x3ffffe4e
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b1000),    # LT bit, branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x3ffffe4e),
                ('lr', 0x40000004),
            ),
        },
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b0100),    # GT bit, branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x3ffffe4e),
                ('lr', 0x40000004),
            ),
        },
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b0010),    # EQ bit, don't branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x40000004),
                ('lr', 0x40000004),
            ),
        },
    ],

    '7A03FE4E': [  # e_bns [cr0,] 0x3ffffe4e
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b0000),    # no SO bit, branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x3ffffe4e),
                ('lr', 0x0),
            ),
        },
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b0001),    # SO bit, don't branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x40000004),
                ('lr', 0x0),
            ),
        },
    ],

    '7A03FE4F': [  # e_bnsl [cr0,] 0x3ffffe4e
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b0000),    # no SO bit, branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x3ffffe4e),
                ('lr', 0x40000004),
            ),
        },
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b0001),    # SO bit, don't branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x40000004),
                ('lr', 0x40000004),
            ),
        },
    ],

    '7A10FE4E': [  # e_blt [cr0,] 0x3ffffe4e
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b1000),    # LT bit, branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x3ffffe4e),
                ('lr', 0x0),
            ),
        },
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b0100),    # GT bit, don't branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x40000004),
                ('lr', 0x0),
            ),
        },
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b0010),    # EQ bit, don't branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x40000004),
                ('lr', 0x0),
            ),
        },
    ],

    '7A10FE4F': [  # e_bltl [cr0,] 0x3ffffe4e
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b1000),    # LT bit, branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x3ffffe4e),
                ('lr', 0x40000004),
            ),
        },
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b0100),    # GT bit, don't branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x40000004),
                ('lr', 0x40000004),
            ),
        },
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b0010),    # EQ bit, don't branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x40000004),
                ('lr', 0x40000004),
            ),
        },
    ],

    '7A11FE4E': [  # e_bgt [cr0,] 0x3ffffe4e
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b1000),    # LT bit, don't branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x40000004),
                ('lr', 0x0),
            ),
        },
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b0100),    # GT bit, branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x3ffffe4e),
                ('lr', 0x0),
            ),
        },
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b0010),    # EQ bit, don't branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x40000004),
                ('lr', 0x0),
            ),
        },
    ],

    '7A11FE4F': [  # e_bgtl [cr0,] 0x3ffffe4e
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b1000),    # LT bit, don't branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x40000004),
                ('lr', 0x40000004),
            ),
        },
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b0100),    # GT bit, branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x3ffffe4e),
                ('lr', 0x40000004),
            ),
        },
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b0010),    # EQ bit, don't branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x40000004),
                ('lr', 0x40000004),
            ),
        },
    ],

    '7A12FE4E': [  # e_beq [cr0,] 0x3ffffe4e
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b1000),    # LT bit, don't branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x40000004),
                ('lr', 0x0),
            ),
        },
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b0100),    # GT bit, don't branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x40000004),
                ('lr', 0x0),
            ),
        },
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b0010),    # EQ bit, branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x3ffffe4e),
                ('lr', 0x0),
            ),
        },
    ],

    '7A12FE4F': [  # e_beql [cr0,] 0x3ffffe4e
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b1000),    # LT bit, don't branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x40000004),
                ('lr', 0x40000004),
            ),
        },
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b0100),    # GT bit, don't branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x40000004),
                ('lr', 0x40000004),
            ),
        },
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b0010),    # EQ bit, branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x3ffffe4e),
                ('lr', 0x40000004),
            ),
        },
    ],

    '7A13FE4E': [  # e_bso [cr0,] 0x3ffffe4e
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b0000),    # no SO bit, don't branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x40000004),
                ('lr', 0x0),
            ),
        },
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b0001),    # SO bit, branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x3ffffe4e),
                ('lr', 0x0),
            ),
        },
    ],

    '7A13FE4F': [  # e_bsol [cr0,] 0x3ffffe4e
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b0000),    # no SO bit, don't branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x40000004),
                ('lr', 0x40000004),
            ),
        },
        {
            'setup': (
                ('pc', 0x40000000),
                ('cr0', 0b0001),    # SO bit, branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x3ffffe4e),
                ('lr', 0x40000004),
            ),
        },
    ],

    '7A20FE4E': [  # e_bdnz [cr0,] 0x3ffffe4e
        {
            'setup': (
                ('pc', 0x40000000),
                ('ctr', 0x1),   # decrements to 0, don't branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x40000004),
                ('lr', 0x0),
            ),
        },
        {
            'setup': (
                ('pc', 0x40000000),
                ('ctr', 0x2),   # decrements to non-zero, branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x3ffffe4e),
                ('lr', 0x0),
            ),
        },
    ],

    '7A20FE4F': [  # e_bdnzl [cr0,] 0x3ffffe4e
        {
            'setup': (
                ('pc', 0x40000000),
                ('ctr', 0x1),   # decrements to 0, don't branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x40000004),
                ('lr', 0x40000004),
            ),
        },
        {
            'setup': (
                ('pc', 0x40000000),
                ('ctr', 0x2),   # decrements to non-zero, branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x3ffffe4e),
                ('lr', 0x40000004),
            ),
        },
    ],

    '7A30FE4E': [  # e_bdz [cr0,] 0x3ffffe4e
        {
            'setup': (
                ('pc', 0x40000000),
                ('ctr', 0x1),   # decrements to 0, branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x3ffffe4e),
                ('lr', 0x0),
            ),
        },
        {
            'setup': (
                ('pc', 0x40000000),
                ('ctr', 0x2),   # decrements to non-zero, don't branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x40000004),
                ('lr', 0x0),
            ),
        },
    ],

    '7A30FE4F': [  # e_bdzl [cr0,] 0x3ffffe4e
        {
            'setup': (
                ('pc', 0x40000000),
                ('ctr', 0x1),   # decrements to 0, branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x3ffffe4e),
                ('lr', 0x40000004),
            ),
        },
        {
            'setup': (
                ('pc', 0x40000000),
                ('ctr', 0x2),   # decrements to non-zero, don't branch
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x40000004),
                ('lr', 0x40000004),
            ),
        },
    ],

    '1820AC81': [  # e_cmpi cr1,r0,-0x7f
        {
            'setup': (
                ('r0', -0x1234), # less than
                ('cr1', 0),
            ),
            'tests': (
                ('cr1', 0b1000),
            ),
        },
        {
            'setup': (
                ('r0', 0x1234), # greater than
                ('cr1', 0),
            ),
            'tests': (
                ('cr1', 0b0100),
            ),
        },
        {
            'setup': (
                ('r0', -0x7f), # equal to
                ('cr1', 0),
            ),
            'tests': (
                ('cr1', 0b0010),
            ),
        },
    ],

    '1880A806': [  # e_cmpli cr0,r0,6
        {
            'setup': (
                ('r0', 0x5),    # less than
            ),
            'tests': (
                ('cr0', 0b1000),
            ),
        },
        {
            'setup': (
                ('r0', 0x10),   # greater than (positive)
            ),
            'tests': (
                ('cr0', 0b0100),
            ),
        },
        {
            'setup': (
                ('r0', -0x10),  # greater than (negative, unsigned)
            ),
            'tests': (
                ('cr0', 0b0100),
            ),
        },
        {
            'setup': (
                ('r0', 0x6),   # equal to
            ),
            'tests': (
                ('cr0', 0b0010),
            ),
        },
    ],

    '18010040': [ # e_lbzu r0,0x40(r1) - load byte and zero with update
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                (0x10000040, bytes.fromhex('FB'))
            ),
            'tests': (
                ('r0', 0xFB),
                ('r1', 0x10000040)
            )
        },
    ],

    '18010140': [ # e_lhzu r0,0x40(r1) - load half word and zero with update
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                (0x10000040, bytes.fromhex('8311'))
            ),
            'tests': (
                ('r0', 0x8311),
                ('r1', 0x10000040)
            )
        },
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                (0x10000040, bytes.fromhex('4011'))
            ),
            'tests': (
                ('r0', 0x4011),
                ('r1', 0x10000040)
            )
        }
    ],

    '18010240': [ # e_lwzu r0,0x40(r1) - load word and zero with update
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                (0x10000040, bytes.fromhex('8C627311'))
            ),
            'tests': (
                ('r0', 0x8C627311),
                ('r1', 0x10000040)
            )
        },

        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                (0x10000040, bytes.fromhex('7D9A4011'))
            ),
            'tests': (
                ('r0', 0x7D9A4011),
                ('r1', 0x10000040)
            )
        }
    ],

    # Note that rA = 0 is an invalid form for loads with updates, so we don't test it
    '18010340': [ # e_lhau r0,0x40(r1) - load half word algebraic with update
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                (0x10000040, bytes.fromhex('8311'))
            ),
            'tests': (
                ('r0', 0xFFFF8311), # sign-extended with 1
                ('r1', 0x10000040)
            )
        },

        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                (0x10000040, bytes.fromhex('4011'))
            ),
            'tests': (
                ('r0', 0x4011), # sign-extended with 0
                ('r1', 0x10000040)
            )
        }
    ],

    '18010440': [ # e_stbu r0,0x40(r1) - store byte with update
        {
            'setup': (
                ('r0', 0xAB),
                ('r1', 0x10000000),
                (0x10000040, b"\x00")
            ),
            'tests': (
                (0x10000040, b"\xAB"),
                ('r1', 0x10000040)
            )
        },
    ],

    '18010540': [ # e_sthu r0,0x40(r1) - store half word with update
        {
            'setup': (
                ('r0', 0xABDF),
                ('r1', 0x10000000),
                (0x10000040, bytes.fromhex('0000'))
            ),
            'tests': (
                (0x10000040, bytes.fromhex('ABDF')),
                ('r1', 0x10000040)
            )
        },
    ],

    '18010640': [ # e_stwu r0,0x400(r1) - store word with update
        {
            'setup': (
                ('r0', 0xABDF1539),
                ('r1', 0x10000000),
                (0x10000040, bytes.fromhex('00000000'))
            ),
            'tests': (
                (0x10000040, bytes.fromhex('ABDF1539')),
                ('r1', 0x10000040)
            )
        },
    ],

    '1B810840': [ # e_lmw r28,0x40(r1)
        {
            'setup': (
                ('r1', 0x10000000),
                ('r28', 0),
                ('r29', 0),
                ('r30', 0),
                ('r31', 0),
                (0x10000040 + (4 * 0), bytes.fromhex('DEADBEEF')),
                (0x10000040 + (4 * 1), bytes.fromhex('BEEFFACE')),
                (0x10000040 + (4 * 2), bytes.fromhex('FEEDFACE')),
                (0x10000040 + (4 * 3), bytes.fromhex('FEEDBEEF')),
            ),
            'tests': (
                ('r28', 0xDEADBEEF),
                ('r29', 0xBEEFFACE),
                ('r30', 0xFEEDFACE),
                ('r31', 0xFEEDBEEF),
            )
        }
    ],

    '1B810940': [ # e_stmw r28,0x40(r1)
        {
            'setup': (
                ('r1', 0x10000000),
                ('r28', 0xDEADBEEF),
                ('r29', 0xBEEFFACE),
                ('r30', 0xFEEDFACE),
                ('r31', 0xFEEDBEEF),
                (0x10000040 + (4 * 0), b'00000000'),
                (0x10000040 + (4 * 1), b'00000000'),
                (0x10000040 + (4 * 2), b'00000000'),
                (0x10000040 + (4 * 3), b'00000000'),
            ),
            'tests': (
                (0x10000040 + (4 * 0), bytes.fromhex('DEADBEEF')),
                (0x10000040 + (4 * 1), bytes.fromhex('BEEFFACE')),
                (0x10000040 + (4 * 2), bytes.fromhex('FEEDFACE')),
                (0x10000040 + (4 * 3), bytes.fromhex('FEEDBEEF')),
            )
        }
    ],

    '18018040': [ # e_addi r0,r1,0x40
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x50),   # Normal addition
                ('cr0', 0)
            ),
            'tests': (
                ('r0', 0x90),
                ('cr0', 0),
            )
        },
        {
            'setup': (
                ('r0', 0),
                ('r1', 0xffffffff),   # Subtraction (-1)
                ('cr0', 0)
            ),
            'tests': (
                ('r0', 0x3f),
                ('cr0', 0),
            )
        },
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x7fffffff),   # Overflow addition
                ('cr0', 0)
            ),
            'tests': (
                ('r0', 0x8000003f),
                ('cr0', 0),
            )
        },
    ],

    '18018840': [ # e_addi. r0,r1,0x40
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x50),   # Normal addition
                ('cr0', 0)
            ),
            'tests': (
                ('r0', 0x90),
                ('cr0', 0b0100),    # result > 0
            )
        },
        {
            'setup': (
                ('r0', 0),
                ('r1', 0xffffffff), # Subtraction (-1)
                ('cr0', 0)
            ),
            'tests': (
                ('r0', 0x3f),
                ('cr0', 0b0100), # result > 0
            )
        },
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x7fffffff),   # Overflow addition
                ('cr0', 0)
            ),
            'tests': (
                ('r0', 0x8000003f),
                ('cr0', 0b1000), # result < 0, e_addi. doesn't set overflow bit
            )
        },
    ],

    '18019040': [ # e_addic r0,r1,0x40
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x50),   # Normal addition
                ('cr0', 0),
                ('CA', 0),
            ),
            'tests': (
                ('r0', 0x90),
                ('cr0', 0),
                ('CA', 0),
            )
        },
        {
            'setup': (
                ('r0', 0),
                ('r1', 0xffffffff), # Subtraction (-1)
                ('cr0', 0),
                ('CA', 0),
            ),
            'tests': (
                ('r0', 0x3f),
                ('cr0', 0),
                ('CA', 1),
            )
        },
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x7fffffff),   # Signed overflow addition
                ('cr0', 0),
                ('CA', 0),
            ),
            'tests': (
                ('r0', 0x8000003f),
                ('cr0', 0),
                ('CA', 0),
            )
        },
        {
            'setup': (
                ('r0', 0),
                ('r1', 0xffffffff),   # Overflow addition
                ('cr0', 0),
                ('CA', 0),
            ),
            'tests': (
                ('r0', 0x3f),
                ('cr0', 0),
                ('CA', 1),
            )
        },
    ],

    '18019840': [ # e_addic. r0,r1,0x40
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x50),   # Normal addition
                ('cr0', 0),
                ('CA', 0),
            ),
            'tests': (
                ('r0', 0x90),
                ('cr0', 0b0100),    # result > 0
                ('CA', 0),
            )
        },
        {
            'setup': (
                ('r0', 0),
                ('r1', 0xffffffff), # Subtraction (-1)
                ('cr0', 0),
                ('CA', 0),
            ),
            'tests': (
                ('r0', 0x3f),
                ('cr0', 0b0100),    # result > 0
                ('CA', 1),
            )
        },
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x7fffffff),   # Signed overflow addition
                ('cr0', 0),
                ('CA', 0),
            ),
            'tests': (
                ('r0', 0x8000003f),
                ('cr0', 0b1000),    # result < 0, e_addic. doesn't set overflow bit
                ('CA', 0),
            )
        },
        {
            'setup': (
                ('r0', 0),
                ('r1', 0xffffffff),   # Overflow addition
                ('cr0', 0),
                ('CA', 0),
            ),
            'tests': (
                ('r0', 0x3f),
                ('cr0', 0b0100),    # result > 0, e_addic. doesn't set overflow bit
                ('CA', 1),
            )
        },
    ],

    '1801B040': [ # e_subfic r0,r1,0x40
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x30),   # Subtraction with positive numbers
                ('cr0', 0),
                ('CA', 0),
            ),
            'tests': (
                ('r0', 0x10),
                ('cr0', 0),
                ('CA', 1),
            )
        },
        {
            'setup': (
                ('r0', 0),
                ('r1', 0xffffffff), # Subtraction with negative number
                ('cr0', 0),
                ('CA', 0),
            ),
            'tests': (
                ('r0', 0x41),
                ('cr0', 0),
                ('CA', 0),
            )
        },
        {
            'setup': (
                ('r0', 0),
                ('r1', 0xffffff80),
                ('cr0', 0),
                ('CA', 0),
            ),
            'tests': (
                ('r0', 0xc0),
                ('cr0', 0),
                ('CA', 0),
            )
        },
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x50),
                ('cr0', 0),
                ('CA', 0),
            ),
            'tests': (
                ('r0', 0xfffffff0),
                ('cr0', 0),
                ('CA', 0),
            )
        },
    ],

    '1801B840': [ # e_subfic. r0,r1,0x40
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x30),   # Subtraction with positive numbers
                ('cr0', 0),
                ('CA', 0),
            ),
            'tests': (
                ('r0', 0x10),
                ('cr0', 0b0100),
                ('CA', 1),
            )
        },
        {
            'setup': (
                ('r0', 0),
                ('r1', 0xffffffff), # Subtraction with negative number
                ('cr0', 0),
                ('CA', 0),
            ),
            'tests': (
                ('r0', 0x41),
                ('cr0', 0b0100),
                ('CA', 0),
            )
        },
        {
            'setup': (
                ('r0', 0),
                ('r1', 0xffffff80),   # Signed overflow addition
                ('cr0', 0),
                ('CA', 0),
            ),
            'tests': (
                ('r0', 0xc0),
                ('cr0', 0b0100),
                ('CA', 0),
            )
        },
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x50),
                ('cr0', 0),
                ('CA', 0),
            ),
            'tests': (
                ('r0', 0xfffffff0),
                ('cr0', 0b1000),
                ('CA', 0),
            )
        },
    ],

    '1800C007': [ # e_andi r0,r0,0x7 (7 = 0b0111)
        {
            'setup': (
                ('r0', 0b10000),
                ('cr0', 0),
            ),
            'tests': (
                ('r0', 0b0000),
                ('cr0', 0),
            ),
        },
        {
            'setup': (
                ('r0', 0b0111),
                ('cr0', 0),
            ),
            'tests': (
                ('r0', 0b0111),
                ('cr0', 0),
            ),
        }
    ],

    '1800C807': [ # e_andi. r0,r0,0x7 (7 = 0b0111)
        {
            'setup': (
                ('r0', 0b10000),
                ('cr0', 0),
            ),
            'tests': (
                ('r0', 0b0000),
                ('cr0', 0b0010),
            ),
        },
        {
            'setup': (
                ('r0', 0b0111),
                ('cr0', 0),
            ),
            'tests': (
                ('r0', 0b0111),
                ('cr0', 0b0100),
            ),
        }
    ],

    '1800D00A': [ # e_ori r0,r0,0b1010
        {
            'setup': (
                ('r0', 0b1010),
                ('cr0', 0),
            ),
            'tests': (
                ('r0', 0b1010),
                ('cr0', 0),
            ),
        },
        {
            'setup': (
                ('r0', 0b0101),
                ('cr0', 0),
            ),
            'tests': (
                ('r0', 0b1111),
                ('cr0', 0),
            ),
        },
    ],

    '1800D80A': [ # e_ori. r0,r0,0b1010
        {
            'setup': (
                ('r0', 0b1010),
                ('cr0', 0),
            ),
            'tests': (
                ('r0', 0b1010),
                ('cr0', 0b0100),

            ),
        },
        {
            'setup': (
                ('r0', 0b0101),
                ('cr0', 0),
            ),
            'tests': (
                ('r0', 0b1111),
                ('cr0', 0b0100),
            ),
        },
    ],

    '1800E00A': [ # e_xori r0,r0,0b1010
        {
            'setup': (
                ('r0', 0b1010),
                ('cr0', 0),
            ),
            'tests': (
                ('r0', 0b0000),
                ('cr0', 0),
            ),
        },
        {
            'setup': (
                ('r0', 0b0101),
                ('cr0', 0),
            ),
            'tests': (
                ('r0', 0b1111),
                ('cr0', 0),
            ),
        },
    ],

    '1800E80A': [ # e_xori. r0,r0,0b1010
        {
            'setup': (
                ('r0', 0b1010),
                ('cr0', 0),
            ),
            'tests': (
                ('r0', 0b0000),
                ('cr0', 0b0010),

            ),
        },
        {
            'setup': (
                ('r0', 0b0101),
                ('cr0', 0),
            ),
            'tests': (
                ('r0', 0b1111),
                ('cr0', 0b0100),
            ),
        },
    ],

    '1801A040': [ # e_mulli r0,r1,0x40
        {
            'setup': (
                ('r0', 0),
                ('r1', 0),
            ),
            'tests': (
                ('r0', 0),
            )
        },
        {
            'setup': (
                ('r0', 0),
                ('r1', 1),
            ),
            'tests': (
                ('r0', 0x40),
            )
        },
        {
            'setup': (
                ('r0', 0),
                ('r1', 2),
            ),
            'tests': (
                ('r0', 0x80),
            )
        },
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x40000000),
            ),
            'tests': (
                ('r0', 0),
            )
        },
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x89abcdef),
            ),
            'tests': (
                ('r0', 0x6af37bc0),
            )
        },
    ],

    '18011040': [ # e_ldmvgprw 0x40(r1)
        {
            'setup': (
                ('r1', 0x10000000),
                ('r0', 0xdfdfdfdf),
                ('r3', 0xdfdfdfdf),
                ('r4', 0xdfdfdfdf),
                ('r5', 0xdfdfdfdf),
                ('r6', 0xdfdfdfdf),
                ('r7', 0xdfdfdfdf),
                ('r8', 0xdfdfdfdf),
                ('r9', 0xdfdfdfdf),
                ('r10', 0xdfdfdfdf),
                ('r11', 0xdfdfdfdf),
                ('r12', 0xdfdfdfdf),
                (0x10000040 + (4 * 0), bytes.fromhex('00000000')),
                (0x10000040 + (4 * 1), bytes.fromhex('33333333')),
                (0x10000040 + (4 * 2), bytes.fromhex('44444444')),
                (0x10000040 + (4 * 3), bytes.fromhex('55555555')),
                (0x10000040 + (4 * 4), bytes.fromhex('66666666')),
                (0x10000040 + (4 * 5), bytes.fromhex('77777777')),
                (0x10000040 + (4 * 6), bytes.fromhex('88888888')),
                (0x10000040 + (4 * 7), bytes.fromhex('99999999')),
                (0x10000040 + (4 * 8), bytes.fromhex('aaaaaaaa')),
                (0x10000040 + (4 * 9), bytes.fromhex('bbbbbbbb')),
                (0x10000040 + (4 * 10), bytes.fromhex('cccccccc')),
            ),
            'tests': (
                ('r1', 0x10000000),
                ('r0', 0x00000000),
                ('r3', 0x33333333),
                ('r4', 0x44444444),
                ('r5', 0x55555555),
                ('r6', 0x66666666),
                ('r7', 0x77777777),
                ('r8', 0x88888888),
                ('r9', 0x99999999),
                ('r10', 0xaaaaaaaa),
                ('r11', 0xbbbbbbbb),
                ('r12', 0xcccccccc),
            )
        }
    ],

    '18011140': [ # e_stmvgprw 0x40(r1)
        {
            'setup': (
                ('r1', 0x10000000),
                ('r0', 0x00000000),
                ('r3', 0x33333333),
                ('r4', 0x44444444),
                ('r5', 0x55555555),
                ('r6', 0x66666666),
                ('r7', 0x77777777),
                ('r8', 0x88888888),
                ('r9', 0x99999999),
                ('r10', 0xaaaaaaaa),
                ('r11', 0xbbbbbbbb),
                ('r12', 0xcccccccc),
                (0x10000040 + (4 * 0), bytes.fromhex('dfdfdfdf')),
                (0x10000040 + (4 * 1), bytes.fromhex('dfdfdfdf')),
                (0x10000040 + (4 * 2), bytes.fromhex('dfdfdfdf')),
                (0x10000040 + (4 * 3), bytes.fromhex('dfdfdfdf')),
                (0x10000040 + (4 * 4), bytes.fromhex('dfdfdfdf')),
                (0x10000040 + (4 * 5), bytes.fromhex('dfdfdfdf')),
                (0x10000040 + (4 * 6), bytes.fromhex('dfdfdfdf')),
                (0x10000040 + (4 * 7), bytes.fromhex('dfdfdfdf')),
                (0x10000040 + (4 * 8), bytes.fromhex('dfdfdfdf')),
                (0x10000040 + (4 * 9), bytes.fromhex('dfdfdfdf')),
                (0x10000040 + (4 * 10), bytes.fromhex('dfdfdfdf')),
            ),
            'tests': (
                (0x10000040 + (4 * 0), bytes.fromhex('00000000')),
                (0x10000040 + (4 * 1), bytes.fromhex('33333333')),
                (0x10000040 + (4 * 2), bytes.fromhex('44444444')),
                (0x10000040 + (4 * 3), bytes.fromhex('55555555')),
                (0x10000040 + (4 * 4), bytes.fromhex('66666666')),
                (0x10000040 + (4 * 5), bytes.fromhex('77777777')),
                (0x10000040 + (4 * 6), bytes.fromhex('88888888')),
                (0x10000040 + (4 * 7), bytes.fromhex('99999999')),
                (0x10000040 + (4 * 8), bytes.fromhex('aaaaaaaa')),
                (0x10000040 + (4 * 9), bytes.fromhex('bbbbbbbb')),
                (0x10000040 + (4 * 10), bytes.fromhex('cccccccc')),
            )
        }
    ],

    '18211040': [ # e_ldmvsprw 0x40(r1)
        {
            'setup': (
                ('r1', 0x10000000),
                ('cr', 0xdfdfdfdf),
                ('lr', 0xdfdfdfdf),
                ('ctr', 0xdfdfdfdf),
                ('xer', 0xdfdfdfdf),
                (0x10000040 + (4 * 0), bytes.fromhex('00000000')),
                (0x10000040 + (4 * 1), bytes.fromhex('33333333')),
                (0x10000040 + (4 * 2), bytes.fromhex('44444444')),
                (0x10000040 + (4 * 2), bytes.fromhex('44444444')),
            ),
            'tests': (
                ('r1', 0x10000000),
                ('cr', 0x00000000),
                ('lr', 0x33333333),
                ('ctr', 0x44444444),
                ('xer', 0x55555555),
            )
        }
    ],

    '18211140': [ # e_stmvsprw 0x40(r1)
        {
            'setup': (
                ('r1', 0x10000000),
                ('cr', 0x00000000),
                ('lr', 0x33333333),
                ('ctr', 0x44444444),
                ('xer', 0x55555555),
                (0x10000040 + (4 * 0), bytes.fromhex('dfdfdfdf')),
                (0x10000040 + (4 * 1), bytes.fromhex('dfdfdfdf')),
                (0x10000040 + (4 * 2), bytes.fromhex('dfdfdfdf')),
                (0x10000040 + (4 * 3), bytes.fromhex('dfdfdfdf')),
            ),
            'tests': (
                (0x10000040 + (4 * 0), bytes.fromhex('00000000')),
                (0x10000040 + (4 * 1), bytes.fromhex('33333333')),
                (0x10000040 + (4 * 2), bytes.fromhex('44444444')),
                (0x10000040 + (4 * 3), bytes.fromhex('55555555')),
            )
        }
    ],

    '18811040': [ # e_ldmvsrrw 0x40(r1)
        {
            'setup': (
                ('r1', 0x10000000),
                ('SRR0', 0xdfdfdfdf),
                ('SRR1', 0xdfdfdfdf),
                (0x10000040 + (4 * 0), bytes.fromhex('00000000')),
                (0x10000040 + (4 * 1), bytes.fromhex('33333333')),
            ),
            'tests': (
                ('r1', 0x10000000),
                ('SRR0', 0x00000000),
                ('SRR1', 0x33333333),
            )
        }
    ],

    '18811140': [ # e_stmvsrrw 0x40(r1)
        {
            'setup': (
                ('r1', 0x10000000),
                ('SRR0', 0x00000000),
                ('SRR1', 0x33333333),
                (0x10000040 + (4 * 0), bytes.fromhex('dfdfdfdf')),
                (0x10000040 + (4 * 1), bytes.fromhex('dfdfdfdf')),
            ),
            'tests': (
                (0x10000040 + (4 * 0), bytes.fromhex('00000000')),
                (0x10000040 + (4 * 1), bytes.fromhex('33333333')),
            )
        }
    ],

    '18A11040': [ # e_ldmvcsrrw 0x40(r1)
        {
            'setup': (
                ('r1', 0x10000000),
                ('CSRR0', 0xdfdfdfdf),
                ('CSRR1', 0xdfdfdfdf),
                (0x10000040 + (4 * 0), bytes.fromhex('00000000')),
                (0x10000040 + (4 * 1), bytes.fromhex('33333333')),
            ),
            'tests': (
                ('r1', 0x10000000),
                ('CSRR0', 0x00000000),
                ('CSRR1', 0x33333333),
            )
        }
    ],

    '18A11140': [ # e_stmvcsrrw 0x40(r1)
        {
            'setup': (
                ('r1', 0x10000000),
                ('CSRR0', 0x00000000),
                ('CSRR1', 0x33333333),
                (0x10000040 + (4 * 0), bytes.fromhex('dfdfdfdf')),
                (0x10000040 + (4 * 1), bytes.fromhex('dfdfdfdf')),
            ),
            'tests': (
                (0x10000040 + (4 * 0), bytes.fromhex('00000000')),
                (0x10000040 + (4 * 1), bytes.fromhex('33333333')),
            )
        }
    ],

    '18C11040': [ # e_ldmvdsrrw 0x40(r1)
        {
            'setup': (
                ('r1', 0x10000000),
                ('DSRR0', 0xdfdfdfdf),
                ('DSRR1', 0xdfdfdfdf),
                (0x10000040 + (4 * 0), bytes.fromhex('00000000')),
                (0x10000040 + (4 * 1), bytes.fromhex('33333333')),
            ),
            'tests': (
                ('r1', 0x10000000),
                ('DSRR0', 0x00000000),
                ('DSRR1', 0x33333333),
            )
        }
    ],

    '18C11140': [ # e_stmvdsrrw 0x40(r1)
        {
            'setup': (
                ('r1', 0x10000000),
                ('DSRR0', 0x00000000),
                ('DSRR1', 0x33333333),
                (0x10000040 + (4 * 0), bytes.fromhex('dfdfdfdf')),
                (0x10000040 + (4 * 1), bytes.fromhex('dfdfdfdf')),
            ),
            'tests': (
                (0x10000040 + (4 * 0), bytes.fromhex('00000000')),
                (0x10000040 + (4 * 1), bytes.fromhex('33333333')),
            )
        }
    ],

    '70008840': [ # e_add2i. r0,0x40
        {
            'setup': (
                ('r0', 0x50),   # Normal addition
                ('cr0', 0)
            ),
            'tests': (
                ('r0', 0x90),
                ('cr0', 0b0100),    # result > 0
            )
        },
        {
            'setup': (
                ('r0', 0xffffffff), # Subtraction (-1)
                ('cr0', 0)
            ),
            'tests': (
                ('r0', 0x3f),
                ('cr0', 0b0100), # result > 0
            )
        },
        {
            'setup': (
                ('r0', 0x7fffffff),   # Overflow addition
                ('cr0', 0)
            ),
            'tests': (
                ('r0', 0x8000003f),
                ('cr0', 0b1000), # result < 0, e_addi. doesn't set overflow bit
            )
        },
    ],

    '73E08FFF': [ # e_add2i. r0,-1  specifically test sign extension
        {
            'setup': (
                ('r0', 0x40),   # Normal addition
                ('cr0', 0)
            ),
            'tests': (
                ('r0', 0x3f),
                ('cr0', 0b0100),    # result > 0
            )
        },
    ],

    '70009040': [ # e_add2is r0,0x40
        {
            'setup': (
                ('r0', 0x50),   # Normal addition
            ),
            'tests': (
                ('r0', 0x400050),
            )
        },
        {
            'setup': (
                ('r0', 0xffffffff), # Subtraction (-1)
            ),
            'tests': (
                ('r0', 0x3fffff),
            )
        },
        {
            'setup': (
                ('r0', 0x7fffffff),   # Overflow addition
            ),
            'tests': (
                ('r0', 0x803fffff),
            )
        },
    ],

    '73E09F81': [  # e_cmp16i r0,-0x7f
        {
            'setup': (
                ('r0', -0x1234), # less than
            ),
            'tests': (
                ('cr0', 0b1000),
            ),
        },
        {
            'setup': (
                ('r0', 0x1234), # greater than
            ),
            'tests': (
                ('cr0', 0b0100),
            ),
        },
        {
            'setup': (
                ('r0', -0x7f), # equal to
            ),
            'tests': (
                ('cr0', 0b0010),
            ),
        },
    ],

    '7000A040': [ # e_mull2i r0,0x40
        {
            'setup': (
                ('r0', 0),
            ),
            'tests': (
                ('r0', 0),
            )
        },
        {
            'setup': (
                ('r0', 1),
            ),
            'tests': (
                ('r0', 0x40),
            )
        },
        {
            'setup': (
                ('r0', 2),
            ),
            'tests': (
                ('r0', 0x80),
            )
        },
        {
            'setup': (
                ('r0', 0x40000000),
            ),
            'tests': (
                ('r0', 0),
            )
        },
        {
            'setup': (
                ('r0', 0x89abcdef),
            ),
            'tests': (
                ('r0', 0x6af37bc0),
            )
        },
    ],

    '73E0A7C0': [ # e_mull2i r0,-0x40
        {
            'setup': (
                ('r0', 0),
            ),
            'tests': (
                ('r0', 0),
            )
        },
        {
            'setup': (
                ('r0', 1),
            ),
            'tests': (
                ('r0', 0xffffffc0),
            )
        },
        {
            'setup': (
                ('r0', 2),
            ),
            'tests': (
                ('r0', 0xffffff80),
            )
        },
        {
            'setup': (
                ('r0', 0x40000000),
            ),
            'tests': (
                ('r0', 0),
            )
        },
        {
            'setup': (
                ('r0', 0x89abcdef),
            ),
            'tests': (
                ('r0', 0x950c8440),
            )
        },
    ],

    '73E0AF81': [  # e_cmpl16i r0,0xff81
        {
            'setup': (
                ('r0', -0x1234), # greater than
            ),
            'tests': (
                ('cr0', 0b0100),
            ),
        },
        {
            'setup': (
                ('r0', 0x1234), # less than
            ),
            'tests': (
                ('cr0', 0b1000),
            ),
        },
        {
            'setup': (
                ('r0', 0xff81), # equal to
            ),
            'tests': (
                ('cr0', 0b0010),
            ),
        },
    ],

    '7000B040': [  # e_cmph16i r0,0x40
        {
            'setup': (
                ('r0', 0x50), # greater than
            ),
            'tests': (
                ('cr0', 0b0100),
            ),
        },
        {
            'setup': (
                ('r0', 0x30), # less than
            ),
            'tests': (
                ('cr0', 0b1000),
            ),
        },
        {
            'setup': (
                ('r0', 0x40), # equal to
            ),
            'tests': (
                ('cr0', 0b0010),
            ),
        },
        {
            'setup': (
                ('r0', 0x10040), # equal to, only bottom 16 bits should matter
            ),
            'tests': (
                ('cr0', 0b0010),
            ),
        },
    ],

    '73E0BFC0': [  # e_cmphl16i r0,-0x40 (-0x40 = 0xffc0)
        {
            'setup': (
                ('r0', 0xffd0), # greater than
            ),
            'tests': (
                ('cr0', 0b0100),
            ),
        },
        {
            'setup': (
                ('r0', 0xffb0), # less than
            ),
            'tests': (
                ('cr0', 0b1000),
            ),
        },
        {
            'setup': (
                ('r0', 0xffc0), # equal to
            ),
            'tests': (
                ('cr0', 0b0010),
            ),
        },
        {
            'setup': (
                ('r0', 0x1ffc0), # equal to, only bottom 16 bits should matter
            ),
            'tests': (
                ('cr0', 0b0010),
            ),
        },
    ],

    '7015C2AA': [ # e_or2i r0,0xAAAA
        {
            'setup': (
                ('r0', 0xAAAAAAAA),
                ('cr0', 0),
            ),
            'tests': (
                ('r0', 0xAAAAAAAA),
                ('cr0', 0),
            ),
        },
        {
            'setup': (
                ('r0', 0x55555555),
                ('cr0', 0),
            ),
            'tests': (
                ('r0', 0x5555FFFF),
                ('cr0', 0),
            ),
        },
    ],

    '7015CAAA': [ # e_and2i. r0,0xAAAA
        {
            'setup': (
                ('r0', 0xAAAAAAAA),
                ('cr0', 0),
            ),
            'tests': (
                ('r0', 0xAAAA),
                ('cr0', 0b0100),
            ),
        },
        {
            'setup': (
                ('r0', 0x55555555),
                ('cr0', 0),
            ),
            'tests': (
                ('r0', 0),
                ('cr0', 0b0010),
            ),
        }
    ],

    '7015D2AA': [ # e_or2is r0,0xAAAA
        {
            'setup': (
                ('r0', 0xAAAAAAAA),
                ('cr0', 0),
            ),
            'tests': (
                ('r0', 0xAAAAAAAA),
                ('cr0', 0),
            ),
        },
        {
            'setup': (
                ('r0', 0x55555555),
                ('cr0', 0),
            ),
            'tests': (
                ('r0', 0xFFFF5555),
                ('cr0', 0),
            ),
        },
    ],

    '7000E040': [ # e_lis r0,0x40
        {
            'setup': (
                ('r0', 0xdfdfdfdf),
            ),
            'tests': (
                ('r0', 0x400000),
            ),
        },
    ],

    '7015EAAA': [ # e_and2is. r0,0xAAAA
        {
            'setup': (
                ('r0', 0xAAAAAAAA),
                ('cr0', 0),
            ),
            'tests': (
                ('r0', 0xAAAA0000),
                ('cr0', 0b1000),
            ),
        },
        {
            'setup': (
                ('r0', 0x55555555),
                ('cr0', 0),
            ),
            'tests': (
                ('r0', 0),
                ('cr0', 0b0010),
            ),
        },
    ],

    '701F6DFD': [ # e_li r0,0xdfdfd
        {
            'setup': (
                ('r0', 0xaaaaaaaa),
            ),
            'tests': (
                ('r0', 0xfffdfdfd),
            ),
        },
    ],

    '701B07DF': [ # e_li r0,0xdfdf
        {
            'setup': (
                ('r0', 0xaaaaaaaa),
            ),
            'tests': (
                ('r0', 0xdfdf),
            ),
        },
    ],

    '7D00081C': [  # e_cmph cr2,r0,r1
        {
            'setup': (
                ('r0', 0x40),
                ('r1', 0x50),
                ('cr2', 0),
            ),
            'tests': (
                ('cr2', 0b1000),
            ),
        },
        {
            'setup': (
                ('r0', 0x40),
                ('r1', 0x30),
                ('cr2', 0),
            ),
            'tests': (
                ('cr2', 0b0100),
            ),
        },
        {
            'setup': (
                ('r0', 0x40),
                ('r1', 0x40),
                ('cr2', 0)
            ),
            'tests': (
                ('cr2', 0b0010),
            ),
        },
        {
            'setup': (
                ('r0', 0x0040), # equal to, only bottom 16 bits should matter
                ('r1', 0x10040),
                ('cr2', 0),
            ),
            'tests': (
                ('cr2', 0b0010),
            ),
        },
        {
            'setup': (
                ('r0', 0x40),
                ('r1', 0xffffffff),
                ('cr2', 0),
            ),
            'tests': (
                ('cr2', 0b0100),
            ),
        },
    ],

    '7D040020': [  # e_mcrf cr2,cr1
        {
            'setup': (
                ('cr', 0x12345678),
            ),
            'tests': (
                ('cr', 0x12245678),
            ),
        },
    ],

    '7F465042': [  # e_crnor cr6.eq,cr1.eq,cr2.eq
       {
           'setup': (
               ('cr1', 0b1111),
               ('cr2', 0b1101),
               ('cr6', 0),
           ),
           'tests': (
               ('cr6', 0),
           ),
       },
       {
           'setup': (
               ('cr1', 0b1010),
               ('cr2', 0b0010),
               ('cr6', 0),
           ),
           'tests': (
               ('cr6', 0),
           ),
       },
       {
           'setup': (
               ('cr1', 0b1101),
               ('cr2', 0b1010),
               ('cr6', 0),
           ),
           'tests': (
               ('cr6', 0),
           ),
       },
       {
           'setup': (
               ('cr1', 0b1101),
               ('cr2', 0b1101),
               ('cr6', 0),
           ),
           'tests': (
               ('cr6', 0b0010),
           ),
       },
    ],

    '7C81105C': [  # e_cmphl cr1,r1,r2
        {
            'setup': (
                ('r1', 0x40),
                ('r2', 0x50),
                ('cr1', 0),
            ),
            'tests': (
                ('cr1', 0b1000),
            ),
        },
        {
            'setup': (
                ('r1', 0x40),
                ('r2', 0x30),
                ('cr1', 0),
            ),
            'tests': (
                ('cr1', 0b0100),
            ),
        },
        {
            'setup': (
                ('r1', 0x40),
                ('r2', 0x40),
                ('cr1', 0)
            ),
            'tests': (
                ('cr1', 0b0010),
            ),
        },
        {
            'setup': (
                ('r1', 0x0040), # equal to, only bottom 16 bits should matter
                ('r2', 0x10040),
                ('cr1', 0),
            ),
            'tests': (
                ('cr1', 0b0010),
            ),
        },
        {
            'setup': (
                ('r1', 0x40),
                ('r2', 0xffffffff),
                ('cr1', 0),
            ),
            'tests': (
                ('cr1', 0b1000),
            ),
        },
    ],

    # For e_slwi[.], we mostly want to test different rotations, which
    # are encoded into the instruction, so we have to do separate tests
    '7C412070':  # e_slwi r1,r2,0x4
    [
        {
            'setup': (
                ('r1', 0xdfdfdfdf),
                ('r2', 0xbeefface),
                ('cr0', 0),
            ),

            'tests': (
                ('r1', 0xeefface0),
                ('cr0', 0),
            ),
        },
    ],

    '7C41F870':  # e_slwi r1,r2,0x1f
    [
        {
            'setup': (
                ('r1', 0xdfdfdfdf),
                ('r2', 0xbeefface),
                ('cr0', 0),
            ),

            'tests': (
                ('r1', 0),
                ('cr0', 0),
            ),
        },
    ],

    '7C418070':  # e_slwi r1,r2,0x10
    [
        {
            'setup': (
                ('r1', 0xdfdfdfdf),
                ('r2', 0xbeefface),
                ('cr0', 0),
            ),

            'tests': (
                ('r1', 0xface0000),
                ('cr0', 0),
            ),
        },
    ],

    '7C412071':  # e_slwi. r1,r2,0x4
    [
        {
            'setup': (
                ('r1', 0xdfdfdfdf),
                ('r2', 0xbeefface),
                ('cr0', 0),
            ),

            'tests': (
                ('r1', 0xeefface0),
                ('cr0', 0b1000),
            ),
        },
    ],

    '7C41F871':  # e_slwi. r1,r2,0x1f
    [
        {
            'setup': (
                ('r1', 0xdfdfdfdf),
                ('r2', 0xbeefface),
                ('cr0', 0),
            ),

            'tests': (
                ('r1', 0),
                ('cr0', 0b0010),
            ),
        },
    ],

    '7C418071':  # e_slwi. r1,r2,0x10
    [
        {
            'setup': (
                ('r1', 0xdfdfdfdf),
                ('r2', 0xbeefface),
                ('cr0', 0),
            ),

            'tests': (
                ('r1', 0xface0000),
                ('cr0', 0b1000),
            ),
        },
    ],

    '7F465102': [  # e_crandc cr6.eq,cr1.eq,cr2.eq
       {
           'setup': (
               ('cr1', 0b1111),
               ('cr2', 0b1101),
               ('cr6', 0),
           ),
           'tests': (
               ('cr6', 0b0010),
           ),
       },
       {
           'setup': (
               ('cr1', 0b1010),
               ('cr2', 0b0010),
               ('cr6', 0),
           ),
           'tests': (
               ('cr6', 0),
           ),
       },
       {
           'setup': (
               ('cr1', 0b1101),
               ('cr2', 0b1010),
               ('cr6', 0),
           ),
           'tests': (
               ('cr6', 0),
           ),
       },
       {
           'setup': (
               ('cr1', 0b1101),
               ('cr2', 0b1101),
               ('cr6', 0),
           ),
           'tests': (
               ('cr6', 0),
           ),
       },
    ],

    '7F465182': [  # e_crxor cr6.eq,cr1.eq,cr2.eq
       {
           'setup': (
               ('cr1', 0b1111),
               ('cr2', 0b1101),
               ('cr6', 0),
           ),
           'tests': (
               ('cr6', 0b0010),
           ),
       },
       {
           'setup': (
               ('cr1', 0b1010),
               ('cr2', 0b0010),
               ('cr6', 0),
           ),
           'tests': (
               ('cr6', 0),
           ),
       },
       {
           'setup': (
               ('cr1', 0b1101),
               ('cr2', 0b1010),
               ('cr6', 0),
           ),
           'tests': (
               ('cr6', 0b0010),
           ),
       },
       {
           'setup': (
               ('cr1', 0b1101),
               ('cr2', 0b1101),
               ('cr6', 0),
           ),
           'tests': (
               ('cr6', 0),
           ),
       },
    ],

    '7F4651C2': [  # e_crnand cr6.eq,cr1.eq,cr2.eq
       {
           'setup': (
               ('cr1', 0b1111),
               ('cr2', 0b1101),
               ('cr6', 0),
           ),
           'tests': (
               ('cr6', 0b0010),
           ),
       },
       {
           'setup': (
               ('cr1', 0b1010),
               ('cr2', 0b0010),
               ('cr6', 0),
           ),
           'tests': (
               ('cr6', 0),
           ),
       },
       {
           'setup': (
               ('cr1', 0b1101),
               ('cr2', 0b1010),
               ('cr6', 0),
           ),
           'tests': (
               ('cr6', 0b0010),
           ),
       },
       {
           'setup': (
               ('cr1', 0b1101),
               ('cr2', 0b1101),
               ('cr6', 0),
           ),
           'tests': (
               ('cr6', 0b0010),
           ),
       },
    ],


    '7F465202': [  # e_crand cr6.eq,cr1.eq,cr2.eq
       {
           'setup': (
               ('cr1', 0b1111),
               ('cr2', 0b1101),
               ('cr6', 0),
           ),
           'tests': (
               ('cr6', 0),
           ),
       },
       {
           'setup': (
               ('cr1', 0b1010),
               ('cr2', 0b0010),
               ('cr6', 0),
           ),
           'tests': (
               ('cr6', 0b0010),
           ),
       },
       {
           'setup': (
               ('cr1', 0b1101),
               ('cr2', 0b1010),
               ('cr6', 0),
           ),
           'tests': (
               ('cr6', 0),
           ),
       },
       {
           'setup': (
               ('cr1', 0b1101),
               ('cr2', 0b1101),
               ('cr6', 0),
           ),
           'tests': (
               ('cr6', 0),
           ),
       },
    ],

    '7C411A30': [   # e_rlw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdf),
                ('r2', 0xbeefface),
                ('r3', 4),
                ('cr0', 0),
            ),
            'tests': (
                ('r1', 0xeeffaceb),
                ('cr0', 0),
            ),
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdf),
                ('r2', 0xbeefface),
                ('r3', 0x1f),
                ('cr0', 0),
            ),
            'tests': (
                ('r1', 0x5f77fd67),
                ('cr0', 0),
            ),
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdf),
                ('r2', 0xbeefface),
                ('r3', 0x10),
                ('cr0', 0),
            ),
            'tests': (
                ('r1', 0xfacebeef),
                ('cr0', 0),
            ),
        },
    ],

    '7C411A31': [   # e_rlw. r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdf),
                ('r2', 0xbeefface),
                ('r3', 4),
                ('cr0', 0),
            ),
            'tests': (
                ('r1', 0xeeffaceb),
                ('cr0', 0b1000),
            ),
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdf),
                ('r2', 0xbeefface),
                ('r3', 0x1f),
                ('cr0', 0),
            ),
            'tests': (
                ('r1', 0x5f77fd67),
                ('cr0', 0b0100),
            ),
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdf),
                ('r2', 0xbeefface),
                ('r3', 0x10),
                ('cr0', 0),
            ),
            'tests': (
                ('r1', 0xfacebeef),
                ('cr0', 0b1000),
            ),
        },
    ],

    '7F465242': [  # e_creqv cr6.eq,cr1.eq,cr2.eq
       {
           'setup': (
               ('cr1', 0b1111),
               ('cr2', 0b1101),
               ('cr6', 0),
           ),
           'tests': (
               ('cr6', 0),
           ),
       },
       {
           'setup': (
               ('cr1', 0b1010),
               ('cr2', 0b0010),
               ('cr6', 0),
           ),
           'tests': (
               ('cr6', 0b0010),
           ),
       },
       {
           'setup': (
               ('cr1', 0b1101),
               ('cr2', 0b1010),
               ('cr6', 0),
           ),
           'tests': (
               ('cr6', 0),
           ),
       },
       {
           'setup': (
               ('cr1', 0b1101),
               ('cr2', 0b1101),
               ('cr6', 0),
           ),
           'tests': (
               ('cr6', 0b0010),
           ),
       },
    ],

    # For e_rlwi[.], we mostly want to test different rotations, which
    # are encoded into the instruction, so we have to do separate tests
    '7C412270':  # e_rlwi r1,r2,0x4
    [
        {
            'setup': (
                ('r1', 0xdfdfdfdf),
                ('r2', 0xbeefface),
                ('cr0', 0),
            ),

            'tests': (
                ('r1', 0xeeffaceb),
                ('cr0', 0),
            ),
        },
    ],

    '7C41FA70':  # e_rlwi r1,r2,0x1f
    [
        {
            'setup': (
                ('r1', 0xdfdfdfdf),
                ('r2', 0xbeefface),
                ('cr0', 0),
            ),

            'tests': (
                ('r1', 0x5f77fd67),
                ('cr0', 0),
            ),
        },
    ],

    '7C418270':  # e_rlwi r1,r2,0x10
    [
        {
            'setup': (
                ('r1', 0xdfdfdfdf),
                ('r2', 0xbeefface),
                ('cr0', 0),
            ),

            'tests': (
                ('r1', 0xfacebeef),
                ('cr0', 0),
            ),
        },
    ],

    '7C412271':  # e_rlwi. r1,r2,0x4
    [
        {
            'setup': (
                ('r1', 0xdfdfdfdf),
                ('r2', 0xbeefface),
                ('cr0', 0),
            ),

            'tests': (
                ('r1', 0xeeffaceb),
                ('cr0', 0b1000),
            ),
        },
    ],

    '7C41FA71':  # e_rlwi. r1,r2,0x1f
    [
        {
            'setup': (
                ('r1', 0xdfdfdfdf),
                ('r2', 0xbeefface),
                ('cr0', 0),
            ),

            'tests': (
                ('r1', 0x5f77fd67),
                ('cr0', 0b0100),
            ),
        },
    ],

    '7C418271':  # e_rlwi. r1,r2,0x10
    [
        {
            'setup': (
                ('r1', 0xdfdfdfdf),
                ('r2', 0xbeefface),
                ('cr0', 0),
            ),

            'tests': (
                ('r1', 0xfacebeef),
                ('cr0', 0b1000),
            ),
        },
    ],

    '7F465342': [  # e_crorc cr6.eq,cr1.eq,cr2.eq
       {
           'setup': (
               ('cr1', 0b1111),
               ('cr2', 0b1101),
               ('cr6', 0),
           ),
           'tests': (
               ('cr6', 0b0010),
           ),
       },
       {
           'setup': (
               ('cr1', 0b1010),
               ('cr2', 0b0010),
               ('cr6', 0),
           ),
           'tests': (
               ('cr6', 0b0010),
           ),
       },
       {
           'setup': (
               ('cr1', 0b1101),
               ('cr2', 0b1010),
               ('cr6', 0),
           ),
           'tests': (
               ('cr6', 0),
           ),
       },
       {
           'setup': (
               ('cr1', 0b1101),
               ('cr2', 0b1101),
               ('cr6', 0),
           ),
           'tests': (
               ('cr6', 0b0010),
           ),
       },
    ],

    '7F465382': [  # e_cror cr6.eq,cr1.eq,cr2.eq
       {
           'setup': (
               ('cr1', 0b1111),
               ('cr2', 0b1101),
               ('cr6', 0),
           ),
           'tests': (
               ('cr6', 0b0010),
           ),
       },
       {
           'setup': (
               ('cr1', 0b1010),
               ('cr2', 0b0010),
               ('cr6', 0),
           ),
           'tests': (
               ('cr6', 0b0010),
           ),
       },
       {
           'setup': (
               ('cr1', 0b1101),
               ('cr2', 0b1010),
               ('cr6', 0),
           ),
           'tests': (
               ('cr6', 0b0010),
           ),
       },
       {
           'setup': (
               ('cr1', 0b1101),
               ('cr2', 0b1101),
               ('cr6', 0),
           ),
           'tests': (
               ('cr6', 0),
           ),
       },
    ],

    # For e_srwi[.], we mostly want to test different rotations, which
    # are encoded into the instruction, so we have to do separate tests
    '7C412470':  # e_srwi r1,r2,0x4
    [
        {
            'setup': (
                ('r1', 0xdfdfdfdf),
                ('r2', 0xbeefface),
                ('cr0', 0),
            ),

            'tests': (
                ('r1', 0x0beeffac),
                ('cr0', 0),
            ),
        },
    ],

    '7C41FC70':  # e_srwi r1,r2,0x1f
    [
        {
            'setup': (
                ('r1', 0xdfdfdfdf),
                ('r2', 0xbeefface),
                ('cr0', 0),
            ),

            'tests': (
                ('r1', 1),
                ('cr0', 0),
            ),
        },
    ],

    '7C418470':  # e_srwi r1,r2,0x10
    [
        {
            'setup': (
                ('r1', 0xdfdfdfdf),
                ('r2', 0xbeefface),
                ('cr0', 0),
            ),

            'tests': (
                ('r1', 0x0000beef),
                ('cr0', 0),
            ),
        },
    ],

    '7C412471':  # e_srwi. r1,r2,0x4
    [
        {
            'setup': (
                ('r1', 0xdfdfdfdf),
                ('r2', 0xbeefface),
                ('cr0', 0),
            ),

            'tests': (
                ('r1', 0x0beeffac),
                ('cr0', 0b0100),
            ),
        },
    ],

    '7C41FC71':  # e_srwi. r1,r2,0x1f
    [
        {
            'setup': (
                ('r1', 0xdfdfdfdf),
                ('r2', 0xbeefface),
                ('cr0', 0),
            ),

            'tests': (
                ('r1', 1),
                ('cr0', 0b0100),
            ),
        },
    ],

    '7C418471':  # e_srwi. r1,r2,0x10
    [
        {
            'setup': (
                ('r1', 0xdfdfdfdf),
                ('r2', 0xbeefface),
                ('cr0', 0),
            ),

            'tests': (
                ('r1', 0x0000beef),
                ('cr0', 0b0100),
            ),
        },
    ],

    # For e_rlwimi, we mostly want to test different masks, which are
    # encoded into the instruction, so we have to do separate tests
    '7441203E':  # e_rlwimi r1,r2,0x4,0x0,0x1f
    [
        {
            'setup': (
                ('r1', 0xdfdfdfdf),
                ('r2', 0xbeefface),
                ('cr0', 0),
            ),

            'tests': (
                ('r1', 0xeeffaceb),
                ('cr0', 0),
            ),
        },
    ],

    '74412436':  # e_rlwimi r1,r2,0x4,0x10,0x1b
    [
        {
            'setup': (
                ('r1', 0xdfdfdfdf),
                ('r2', 0xbeefface),
                ('cr0', 0),
            ),

            'tests': (
                ('r1', 0xdfdfacef),
                ('cr0', 0),
            ),
        },
    ],

    '74412000':  # e_rlwimi r1,r2,0x4,0x0,0x0
    [
        {
            'setup': (
                ('r1', 0xdfdfdfdf),
                ('r2', 0xbeefface),
                ('cr0', 0),
            ),

            'tests': (
                ('r1', 0xdfdfdfdf),
                ('cr0', 0),
            ),
        },
    ],

    # For e_rlwinm, we mostly want to test different masks, which are
    # encoded into the instruction, so we have to do separate tests
    '7441203F':  # e_rlwinm r1,r2,0x4,0x0,0x1f
    [
        {
            'setup': (
                ('r1', 0xdfdfdfdf),
                ('r2', 0xbeefface),
                ('cr0', 0),
            ),

            'tests': (
                ('r1', 0xeeffaceb),
                ('cr0', 0),
            ),
        },
    ],

    '74412437':  # e_rlwinm r1,r2,0x4,0x10,0x1b
    [
        {
            'setup': (
                ('r1', 0xdfdfdfdf),
                ('r2', 0xbeefface),
                ('cr0', 0),
            ),

            'tests': (
                ('r1', 0x0000ace0),
                ('cr0', 0),
            ),
        },
    ],

    '74412001':  # e_rlwinm r1,r2,0x4,0x0,0x0
    [
        {
            'setup': (
                ('r1', 0xdfdfdfdf),
                ('r2', 0xbeefface),
                ('cr0', 0),
            ),

            'tests': (
                ('r1', 0x80000000),
                ('cr0', 0),
            ),
        },
    ],

    # Note that for e_b and e_bl, the immediate BD24 (-0x10) has 0b0
    # concatenated on the right, meaning -0x10 is effectively -0x20
    '79FFFFE0': [  # e_b -0x10
        {
            'setup': (
                ('pc', 0x40000050),
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x40000030),
                ('lr', 0x0),
            ),
        },
    ],

    '79FFFFE1': [  # e_bl -0x10
        {
            'setup': (
                ('pc', 0x40000050),
                ('lr', 0x0),
            ),
            'tests': (
                ('pc', 0x40000030),
                ('lr', 0x40000054),
            ),
        },
    ],

    '30010040': [ # e_lbz r0,0x40(r1) - load byte and zero
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                (0x10000040, bytes.fromhex('FB'))
            ),
            'tests': (
                ('r0', 0xFB),
                ('r1', 0x10000000)
            )
        },
    ],

    '34010400': [ # e_stb r0,0x400(r1) - store byte
        {
            'setup': (
                ('r0', 0xAB),
                ('r1', 0x10000000),
                (0x10000400, b"\x00")
            ),
            'tests': (
                (0x10000400, b"\xAB"),
                ('r1', 0x10000000)
            )
        },
    ],

    '38010400': [ # e_lha r0,0x400(r1) - load half word algebraic
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                (0x10000400, bytes.fromhex('8311'))
            ),
            'tests': (
                ('r0', 0xFFFF8311), # sign-extended with 1
                ('r1', 0x10000000)
            )
        },

        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                (0x10000400, bytes.fromhex('4011'))
            ),
            'tests': (
                ('r0', 0x4011), # sign-extended with 0
                ('r1', 0x10000000)
            )
        }
    ],

    '50010400': [ # e_lwz r0,0x400(r1) - load word and zero
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                (0x10000400, bytes.fromhex('8C627311'))
            ),
            'tests': (
                ('r0', 0x8C627311),
                ('r1', 0x10000000)
            )
        },

        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                (0x10000400, bytes.fromhex('7D9A4011'))
            ),
            'tests': (
                ('r0', 0x7D9A4011),
                ('r1', 0x10000000)
            )
        }
    ],

    '54010400': [ # e_stw r0,0x400(r1) - store word
        {
            'setup': (
                ('r0', 0xABDF1539),
                ('r1', 0x10000000),
                (0x10000400, bytes.fromhex('00000000'))
            ),
            'tests': (
                (0x10000400, bytes.fromhex('ABDF1539')),
                ('r1', 0x10000000)
            )
        },
    ],

    '58010400': [ # e_lhz r0,0x400(r1) - load half word and zero
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                (0x10000400, bytes.fromhex('8311'))
            ),
            'tests': (
                ('r0', 0x8311),
                ('r1', 0x10000000)
            )
        },

        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                (0x10000400, bytes.fromhex('4011'))
            ),
            'tests': (
                ('r0', 0x4011),
                ('r1', 0x10000000)
            )
        }
    ],

    '5C010400': [ # e_sth r0,0x400(r1) - store half word
        {
            'setup': (
                ('r0', 0xABDF),
                ('r1', 0x10000000),
                (0x10000400, bytes.fromhex('0000'))
            ),
            'tests': (
                (0x10000400, bytes.fromhex('ABDF')),
                ('r1', 0x10000000)
            )
        },
    ],

    '100112c9':[ # efsdiv r0,r1,r2
        {
            'setup':(
                ('r0',0x0),
                ('r1',_1p1s),
                ('r2',_3p3s)),
            'tests':(
                ('r0',0x3EAAAAAB),
                )
        },
            {'setup':(
                ('r0',0x0),
                ('r1',n_1p1s),
                ('r2',_3p3s)
                ),
            'tests':(
                ('r0',0xbEAAAAAB),
                )
        },
        {
            'setup':(
                ('r0',0x0),
                ('r1',FSNS),
                ('r2',0x7F80_000),
                ),
            'tests':(
                ('r0',0xff7fffff),
                )
        },
            {'setup':(
                ('r0',0x0),
                ('r1',0x40800000),
                ('r2',0x40000000)
                ),
            'tests':(
                ('r0',0x40000000),
                )
        },
            {'setup':(
                ('r0',0x0),
                ('r1',0x40800000),
                ('r2',0)),
            'tests':(
                ('r0',0x7f7fffff),)
        },
    ],

    '100112c0': [ # efsadd r0,r1,r2
        {
            'setup': (
                ('r0', 0x0),
                ('r1', _1p1s),
                ('r2', _1p1s)
            ),
            'tests': (
                ('r0', 0x400ccccd),
            )
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r1', 0x40800000),
                ('r2', 0x40800000)
            ),
            'tests': (
                ('r0', 0x41000000),
            )
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r1', 0xBF8CCCCD),
                ('r2', 0xBF8CCCCD)
            ),
            'tests': (
                ('r0', 0xc00ccccd),
            )
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r1', 0x40800000),
                ('r2', 0x40000000)
            ),
            'tests': (
                ('r0', 0x40c00000),
            )
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r1', 0x40800000),
                ('r2', FSNS)
            ),
            'tests': (
                ('r0', 0xff7fffff),
            )
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r1', FSNS),
                ('r2', 0x40800000)
            ),
            'tests': (
                ('r0', 0xff7fffff),
            )
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r1', FSPS),
                ('r2', 0x40800000)
            ),
            'tests': (
                ('r0', 0x7f7fffff),
            )
        },
    ],

    '100112c1': [ # efssub r0,r1,r2
        {
            'setup': (
                ('r0', 0x0),
                ('r1', _1p1s),
                ('r2', _1p1s)
            ),
            'tests': (
                ('r0', 0x0),
            )
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r1', 0x40800000),
                ('r2', 0x40400000)
            ),
            'tests': (
                ('r0', 0x3F800000),
            )
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r1', 0x3F8CCCCD),
                ('r2', 0xBF8CCCCD)
            ),
            'tests': (
                ('r0', 0x400CCCCD),
            )
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r1', 0x40800000),
                ('r2', 0x40000000)
            ),
            'tests': (
                ('r0', 0x40000000),
            )
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r1', 0x40800000),
                ('r2', FSNS)
            ),
            'tests': (
                ('r0', 0xff7fffff),
            )
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r1', FSNS),
                ('r2', 0x40800000)
            ),
            'tests': (
                ('r0', 0xff7fffff),
            )
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r1', FSPS),
                ('r2', 0x40800000)
            ),
            'tests': (
                ('r0', 0x7f7fffff),
            )
        },
    ],

    '100102c4': [ # efsabs r0,r1
        {
            'setup': (
                ('r0', 0x0),
                ('r1', n_1p1s),
            ),
            'tests': (
                ('r0', _1p1s),
            )
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r1', n_2p2s),
            ),
            'tests': (
                ('r0', _2p2s),
            )
        },
    ],

    '10040ad1': [ # efscfh r0,r1
        {
            'setup': (
                ('r0', 0x0),
                ('r1', 0x8123),
            ),
            'tests': (
                ('r0', 0x80000000),
            )
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r1', 0x123),
            ),
            'tests': (
                ('r0', 0x0),
            )
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r1', 0xc222),
            ),
            'tests': (
                ('r0', 0xC0444000),
            )
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r1', 0x8823),
            ),
            'tests': (
                ('r0', 0xb9046000),
            )
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r1', 0x8823),
            ),
            'tests': (
                ('r0', 0xb9046000),
            )
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r1', FHPQ),
                ('SPEFSCR_FINVE', 0)
            ),
            'tests': (
                ('r0', 0x7f7fffff),
                ('SPEFSCR_FINV', 1),

            )
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r1', FHNQ),
            ),
            'tests': (
                ('r0', 0xff7fffff),
            )
        },
        {
            'setup': (
                ('r0', 0x1234),
                ('r1', FHPQ),
                ('SPEFSCR_FGH', 1),
                ('SPEFSCR_FXH', 1),
                ('SPEFSCR_FG', 1),
                ('SPEFSCR_FX', 1),
                ('SPEFSCR_FINVE', 1),
            ),
            'tests': (
                ('r0', 0x1234),
                ('r1', FHPQ),
                ('SPEFSCR_FGH', 0),
                ('SPEFSCR_FXH', 0),
                ('SPEFSCR_FG', 0),
                ('SPEFSCR_FX', 0),
                ('SPEFSCR_FINVE', 1),
            )
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r1', 0x8000),
            ),
            'tests': (
                ('r0', 0x80000000),

            )
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r1', FHNQ),
                ('SPEFSCR_FINVE', 1),
            ),
            'tests': (
                ('r0', 0),
            )
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r1', FHNQ),
                ('SPEFSCR_FINVE', 0),
            ),
            'tests': (
                ('r0', 0xff7fffff),
            )
        },
    ],

    '10000ad3': [ # efscfsf r0,r1 Does not match hardware 100%
        {
            'setup': (
                ('r0', 0x0),
                ('r1', 0x40900000),
            ),
            'tests': (
                ('r0', 0x3F000000),  #hardware = 0x3f012000
            )
        },
    ],

    '100112c2': [ # efsmadd r0,r1, r2
        {
            'setup': (
                ('r0', 0x3F800000),
                ('r1', 0x40800000),
                ('r2', 0x40800000)
            ),
            'tests': (
                ('r0', 0x41880000),  #
            )
        },
        {
            'setup': (
                ('r0', 0x3F800000),
                ('r1', 0),
                ('r2', 0x40800000)
            ),
            'tests': (
                ('r0', 0x3F800000),  #
            )
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r1', 0x0),
                ('r2', 0x80000000)
            ),
            'tests': (
                ('r0', 0x0),  #
            )
        },
        {
            'setup': (
                ('r0', 0x12345678),
                ('r1', 0x0),
                ('r2', 0x0)
            ),
            'tests': (
                ('r0', 0x12345678),  #
            )
        },
        {
            'setup': (
                ('r0', 0x80002345),
                ('r1', 0x0),
                ('r2', 0x0)
            ),
            'tests': (
                ('r0', 0),  #
            )
        },
        {
            'setup': (
                ('r0', 0x40400000),
                ('r1', 0x0),
                ('r2', 0x0)
            ),
            'tests': (
                ('r0', 0x40400000),  #
            )
        },
        {
            'setup': (
                ('r0', 0x40400000),
                ('r1', 0x80012345),
                ('r2', 0x80012345),
                ('SPEFSCR_FINV', 0)
            ),
            'tests': (
                ('r0', 0),
                ('SPEFSCR_FINV', 1)
            )
        },
    ],

    '100112c3': [ # efsmsub r0,r1, r2
        {
            'setup': (
                ('r0', 0x3F800000),
                ('r1', 0x40800000),
                ('r2', 0x40800000)
            ),
            'tests': (
                ('r0', 0x41700000),  #
            )
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r1', 0x0),
                ('r2', 0x80000000)
            ),
            'tests': (
                ('r0', 0x0),  #
            )
        },
        {
            'setup': (
                ('r0', 0x12345678),
                ('r1', 0x0),
                ('r2', 0x0)
            ),
            'tests': (
                ('r0', 0x12345678),  #
            )
        },
        {
            'setup': (
                ('r0', 0x80002345),
                ('r1', 0x0),
                ('r2', 0x0)
            ),
            'tests': (
                ('r0', 0),  #
            )
        },
        {
            'setup': (
                ('r0', 0x40400000),
                ('r1', 0x0),
                ('r2', 0x0)
            ),
            'tests': (
                ('r0', 0x40400000),  #
            )
        },
        {
            'setup': (
                ('r0', 0x40400000),
                ('r1', 0x80012345),
                ('r2', 0x80012345),
                ('SPEFSCR_FINV', 0)
            ),
            'tests': (
                ('r0', 0),
                ('SPEFSCR_FINV', 1)
            )
        },
    ],

    '100112c8': [ # efsmul r0,r1, r2
        {
            'setup': (
                ('r0', 0x3F800000),
                ('r1', 0x40800000),
                ('r2', 0x40800000)
            ),
            'tests': (
                ('r0', 0x41800000),  #
            )
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r1', 0x0),
                ('r2', 0x80000000)
            ),
            'tests': (
                ('r0', 0x0),  #
            )
        },
        {
            'setup': (
                ('r0', 0x12345678),
                ('r1', 0x0),
                ('r2', 0x0)
            ),
            'tests': (
                ('r0', 0x0),  #
            )
        },
        {
            'setup': (
                ('r0', 0x80002345),
                ('r1', 0x0),
                ('r2', 0x40800000)
            ),
            'tests': (
                ('r0', 0),  #
            )
        },
        {
            'setup': (
                ('r0', 0x40400000),
                ('r1', _1p1s),
                ('r2', 0x7F800001)   # positive NaN
            ),
            'tests': (
                ('r0', 0x7F7FFFFF),  # max positive
            )
        },
        {
            'setup': (
                ('r0', 0x40400000),
                ('r1', 0x0),
                ('r2', 0x7F800001)   # positive NaN
            ),
            'tests': (
                ('r0', 0x00000000),  # zero
            )
        },
        {
            'setup': (
                ('r0', 0x40400000),
                ('r1', 0xFF800001),  # negative NaN
                ('r2', _1p1s),
            ),
            'tests': (
                ('r0', 0xFF7FFFFF),  # max negative
            )
        },
        {
            'setup': (
                ('r0', 0x40400000),
                ('r1', 0xFF800001),  # negative NaN
                ('r2', 0x0),
            ),
            'tests': (
                ('r0', 0x00000000),  # zero
            )
        },
        {
            'setup': (
                ('r0', 0x40400000),
                ('r1', _1p1s),
                ('r2', 0x80000000),  # negative zero
            ),
            'tests': (
                ('r0', 0x00000000),  # positive zero
            )
        },
        {
            'setup': (
                ('r0', 0x40400000),
                ('r1', _1p1s),
                ('r2', 0x80012345),  # denormalized
            ),
            'tests': (
                ('r0', 0),
            )
        },
        {
            'setup': (
                ('r0', 0x40400000),
                ('r2', 0x00012345),  # denormalized
                ('r1', n_1p1s),
            ),
            'tests': (
                ('r0', 0),
            )
        },
    ],

    '100102c5': [ # efsnabs r0,r1 Does not match hardware 100%
        {
            'setup': (
                ('r0', 0x0),
                ('r1', 0xc0900000),
            ),
            'tests': (
                ('r0', 0xc0900000),
            )
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r1', 0x40900000),
            ),
            'tests': (
                ('r0', 0xc0900000),
            )
        },
        {
            'setup': (
                ('r0', 0x0),
                ('r1', FSPS),
                ("SPEFSCR_FINV", 0),
                ("SPEFSCR_FG", 1),
                ("SPEFSCR_FX", 1),
                ("SPEFSCR_FGH", 1),
                ("SPEFSCR_FXH", 1),
            ),
            'tests': (
                ('r0', FSNS),
                ("SPEFSCR_FINV", 1),
                ("SPEFSCR_FG", 0),
                ("SPEFSCR_FX", 0),
                ("SPEFSCR_FGH", 0),
                ("SPEFSCR_FXH", 0),
            )
        },
    ],

}



