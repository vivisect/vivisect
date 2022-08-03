GOOD_EMU_TESTS = 388

emutests = {
    '10210208': [ # evabs   r1,r1
        {
            'setup': (
                ('r1', 0x7fffffff80000000),
            ),
            'tests': (
                ('r1', 0x7fffffff80000000),
            )
        },
        {
            'setup': (
                ('r1', 0x7735940088ca6c00),
            ),
            'tests': (
                ('r1', 0x7735940077359400),
            )
        },
    ],
    '103F0A02': [ # evaddiw r1,r1,0x1f
        {
            'setup': (
                ('r1', 0x7fffffff80000000),
            ),
            'tests': (
                ('r1', 0x8000001e8000001f),
            )
        },
        {
            'setup': (
                ('r1', 0x7735940088ca6c00),
            ),
            'tests': (
                ('r1', 0x7735941f88ca6c1f),
            )
        },
    ],
    '10211200': [ # evaddw  r1,r1,r2
        {
            'setup': (
                ('r1', 0x7fffffff80000000),
                ('r2', 0x100000001000000),
            ),
            'tests': (
                ('r1', 0x80ffffff81000000),
            )
        },
    ],
    '10221A11': [ # evand   r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x123456789abcdef),
                ('r3', 0xff00ff00ff00ff00),
            ),
            'tests': (
                ('r1', 0x10045008900cd00),
            )
        },
    ],
    '10221A12': [ # evandc  r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x123456789abcdef),
                ('r3', 0xff00ff00ff00ff00),
            ),
            'tests': (
                ('r1', 0x23006700ab00ef),
            )
        },
    ],
    '1022020E': [ # evcntlsw r1,r2
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0xfffffffe00000001),
            ),
            'tests': (
                ('r1', 0x1f0000001f),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0xbfffffff40000000),
            ),
            'tests': (
                ('r1', 0x100000001),
            )
        },
    ],
    '1022020D': [ # evcntlzw r1,r2
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0xfffffffe00000001),
            ),
            'tests': (
                ('r1', 0x1f),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0xbfffffff40000000),
            ),
            'tests': (
                ('r1', 0x1),
            )
        },
    ],
    '10221A19': [ # eveqv   r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1122334455667788),
                ('r3', 0x1122334488766755),
            ),
            'tests': (
                ('r1', 0xffffffff22efef22),
            )
        },
    ],
    '1022020A': [ # evextsb r1,r2
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x00f0f0f0ffffff70),
            ),
            'tests': (
                ('r1', 0xfffffff000000070),
            )
        },
    ],
    '1022020B': [ # evextsh r1,r2
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0xf0f0f0ffff7070),
            ),
            'tests': (
                ('r1', 0xfffff0f000007070),
            )
        },
    ],
    '10220284': [ # evfsabs r1,r2
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x3f800000bf800000),
            ),
            'tests': (
                ('r1', 0x3f8000003f800000),
            )
        },
    ],
    '10221A80': [ # evfsadd r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x3f80000041200000),
                ('r3', 0x3f8000003f800000),
            ),
            'tests': (
                ('r1', 0x4000000041300000),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x3fd555554021e1e2),
                ('r3', 0x3fd555554021e1e2),
            ),
            'tests': (
                ('r1', 0x4055555540a1e1e2),
            )
        },
    ],
    '10228301': [ # evldd   r1,0x80(r2)
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x10000000),
                (0x10000080, bytes.fromhex('ab9371d0fedcba98')),
            ),
            'tests': (
                ('r1', 0xab9371d0fedcba98),
            )
        },
    ],
    '10221B00': [ # evlddx  r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x10000000),
                ('r3', 0x400),
                (0x10000400, bytes.fromhex('ab9371d0fedcba98')),
            ),
            'tests': (
                ('r1', 0xab9371d0fedcba98),
            )
        },
    ],
    '7C221E3E': [ # evlddepx r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x10000000),
                ('r3', 0x400),
                (0x10000400, bytes.fromhex('ab9371d0fedcba98')),
            ),
            'tests': (
                ('r1', 0xab9371d0fedcba98),
            )
        },
    ],
    '10228305': [ # evldh   r1,0x80(r2)
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x10000000),
                (0x10000080, bytes.fromhex('ab9371d0fedcba98')),
            ),
            'tests': (
                ('r1', 0xab9371d0fedcba98),
            )
        },
    ],
    '10221B04': [ # evldhx  r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x10000000),
                ('r3', 0x400),
                (0x10000400, bytes.fromhex('ab9371d0fedcba98')),
            ),
            'tests': (
                ('r1', 0xab9371d0fedcba98),
            )
        },
    ],
    '10228303': [ # evldw   r1,0x80(r2)
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x10000000),
                (0x10000080, bytes.fromhex('ab9371d0fedcba98')),
            ),
            'tests': (
                ('r1', 0xab9371d0fedcba98),
            )
        },
    ],
    '10221B02': [ # evldwx  r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x10000000),
                ('r3', 0x400),
                (0x10000400, bytes.fromhex('ab9371d0fedcba98')),
            ),
            'tests': (
                ('r1', 0xab9371d0fedcba98),
            )
        },
    ],
    '10228309': [ # evlhhesplat r1,0x20(r2)
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x10000000),
                (0x10000020, bytes.fromhex('ab9371d0fedcba98')),
            ),
            'tests': (
                ('r1', 0xab930000ab930000),
            )
        },
    ],
    '10221B08': [ # evlhhesplatx r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x10000000),
                ('r3', 0x400),
                (0x10000400, bytes.fromhex('ab9371d0fedcba98')),
            ),
            'tests': (
                ('r1', 0xab930000ab930000),
            )
        },
    ],
    '1022830F': [ # evlhhossplat r1,0x20(r2)
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x10000000),
                (0x10000020, bytes.fromhex('ab9371d0fedcba98')),
            ),
            'tests': (
                ('r1', 0xffffab93ffffab93),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x10000000),
                (0x10000020, bytes.fromhex('2b9371d0fedcba98')),
            ),
            'tests': (
                ('r1', 0x2b9300002b93),
            )
        },
    ],
    '10221B0E': [ # evlhhossplatx r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x10000000),
                ('r3', 0x400),
                (0x10000400, bytes.fromhex('ab9371d0fedcba98')),
            ),
            'tests': (
                ('r1', 0xffffab93ffffab93),
            )
        },
    ],
    '1022830D': [ # evlhhousplat r1,0x20(r2)
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x10000000),
                (0x10000020, bytes.fromhex('ab9371d0fedcba98')),
            ),
            'tests': (
                ('r1', 0xab930000ab93),
            )
        },
    ],
    '10221B0C': [ # evlhhousplatx r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x10000000),
                ('r3', 0x400),
                (0x10000400, bytes.fromhex('ab9371d0fedcba98')),
            ),
            'tests': (
                ('r1', 0xab930000ab93),
            )
        },
    ],
    '10228311': [ # evlwhe  r1,0x40(r2)
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x10000000),
                (0x10000040, bytes.fromhex('ab9371d0fedcba98')),
            ),
            'tests': (
                ('r1', 0xab93000071d00000),
            )
        },
    ],
    '10221B10': [ # evlwhex r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x10000000),
                ('r3', 0x400),
                (0x10000400, bytes.fromhex('ab9371d0fedcba98')),
            ),
            'tests': (
                ('r1', 0xab93000071d00000),
            )
        },
    ],
    '10228317': [ # evlwhos r1,0x40(r2)
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x10000000),
                (0x10000040, bytes.fromhex('ab9371d0fedcba98')),
            ),
            'tests': (
                ('r1', 0xffffab93000071d0),
            )
        },
    ],
    '10221B16': [ # evlwhosx r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x10000000),
                ('r3', 0x400),
                (0x10000400, bytes.fromhex('ab9371d0fedcba98')),
            ),
            'tests': (
                ('r1', 0xffffab93000071d0),
            )
        },
    ],
    '10228315': [ # evlwhou r1,0x40(r2)
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x10000000),
                (0x10000040, bytes.fromhex('ab9371d0fedcba98')),
            ),
            'tests': (
                ('r1', 0xab93000071d0),
            )
        },
    ],
    '10221B14': [ # evlwhoux r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x10000000),
                ('r3', 0x400),
                (0x10000400, bytes.fromhex('ab9371d0fedcba98')),
            ),
            'tests': (
                ('r1', 0xab93000071d0),
            )
        },
    ],
    '1022831D': [ # evlwhsplat r1,0x40(r2)
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x10000000),
                (0x10000040, bytes.fromhex('ab9371d0fedcba98')),
            ),
            'tests': (
                ('r1', 0xab93ab9371d071d0),
            )
        },
    ],
    '10221B1C': [ # evlwhsplatx r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x10000000),
                ('r3', 0x400),
                (0x10000400, bytes.fromhex('ab9371d0fedcba98')),
            ),
            'tests': (
                ('r1', 0xab93ab9371d071d0),
            )
        },
    ],
    '10228319': [ # evlwwsplat r1,0x40(r2)
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x10000000),
                (0x10000040, bytes.fromhex('ab9371d0fedcba98')),
            ),
            'tests': (
                ('r1', 0xab9371d0ab9371d0),
            )
        },
    ],
    '10221B18': [ # evlwwsplatx r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x10000000),
                ('r3', 0x400),
                (0x10000400, bytes.fromhex('ab9371d0fedcba98')),
            ),
            'tests': (
                ('r1', 0xab9371d0ab9371d0),
            )
        },
    ],
    '10221A2C': [ # evmergehi r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x11223344556677),
                ('r3', 0x8899aabbccddeeff),
            ),
            'tests': (
                ('r1', 0x1122338899aabb),
            )
        },
    ],
    '10221A2E': [ # evmergehilo r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x11223344556677),
                ('r3', 0x8899aabbccddeeff),
            ),
            'tests': (
                ('r1', 0x112233ccddeeff),
            )
        },
    ],
    '10221A2D': [ # evmergelo r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x11223344556677),
                ('r3', 0x8899aabbccddeeff),
            ),
            'tests': (
                ('r1', 0x44556677ccddeeff),
            )
        },
    ],
    '10221A2F': [ # evmergelohi r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x11223344556677),
                ('r3', 0x8899aabbccddeeff),
            ),
            'tests': (
                ('r1', 0x445566778899aabb),
            )
        },
    ],
    '102204C4': [ # evmra r1,r2
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x0000000000000000),
                ('ACC', 0xacacacacacacacac),
            ),
            'tests': (
                ('r1', 0x0000000000000000),
                ('ACC', 0x0000000000000000),
            )
        },
    ],
    '102204C9': [ # evaddsmiaaw r1,r2
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1111111122222222),
                ('ACC', 0x333333337fffffff),
            ),
            'tests': (
                ('r1', 0x44444444a2222221),
                ('ACC', 0x44444444a2222221),
            )
        },
    ],
    '102204C1': [ # evaddssiaaw r1,r2
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1111111122222222),
                ('ACC', 0x333333337fffffff),
            ),
            'tests': (
                ('r1', 0x444444447fffffff),
                ('ACC', 0x444444447fffffff),
            )
        },
    ],
    '102204C8': [ # evaddumiaaw r1,r2
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1111111122222222),
                ('ACC', 0x33333333ffffffff),
            ),
            'tests': (
                ('r1', 0x4444444422222221),
                ('ACC', 0x4444444422222221),
            )
        },
    ],
    '102204C0': [ # evaddusiaaw r1,r2
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1111111122222222),
                ('ACC', 0x33333333ffffffff),
            ),
            'tests': (
                ('r1', 0x44444444ffffffff),
                ('ACC', 0x44444444ffffffff),
            )
        },
    ],
    '10221D2B': [ # evmhegsmfaa r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x20000),
                ('r3', 0x30000),
                ('ACC', 0x4),
            ),
            'tests': (
                ('r1', 0x10),
                ('ACC', 0x10),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x20000),
                ('r3', 0xffff0000),
                ('ACC', 0x4),
            ),
            'tests': (
                ('r1', 0x0),
                ('ACC', 0x0),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x40000),
                ('r3', 0xffff0000),
                ('ACC', 0x4),
            ),
            'tests': (
                ('r1', 0xfffffffffffffffc),
                ('ACC', 0xfffffffffffffffc),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x80000000),
                ('r3', 0x7fff0000),
                ('ACC', 0x1),
            ),
            'tests': (
                ('r1', 0xffffffff80010001),
                ('ACC', 0xffffffff80010001),
            )
        },
    ],
    '10221DAB': [ # evmhegsmfan r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x20000),
                ('r3', 0x30000),
                ('ACC', 0x4),
            ),
            'tests': (
                ('r1', 0xfffffffffffffff8),
                ('ACC', 0xfffffffffffffff8),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x20000),
                ('r3', 0xffff0000),
                ('ACC', 0x4),
            ),
            'tests': (
                ('r1', 0x8),
                ('ACC', 0x8),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x40000),
                ('r3', 0xffff0000),
                ('ACC', 0x4),
            ),
            'tests': (
                ('r1', 0xc),
                ('ACC', 0xc),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x80000000),
                ('r3', 0x7fff0000),
                ('ACC', 0x1),
            ),
            'tests': (
                ('r1', 0x7fff0001),
                ('ACC', 0x7fff0001),
            )
        },
    ],
    '10221D29': [ # evmhegsmiaa r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x20000),
                ('r3', 0x30000),
                ('ACC', 0x4),
            ),
            'tests': (
                ('r1', 0xa),
                ('ACC', 0xa),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x20000),
                ('r3', 0xffff0000),
                ('ACC', 0x4),
            ),
            'tests': (
                ('r1', 0x2),
                ('ACC', 0x2),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x40000),
                ('r3', 0xffff0000),
                ('ACC', 0x4),
            ),
            'tests': (
                ('r1', 0x0),
                ('ACC', 0x0),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x80000000),
                ('r3', 0x7fff0000),
                ('ACC', 0x1),
            ),
            'tests': (
                ('r1', 0xffffffffc0008001),
                ('ACC', 0xffffffffc0008001),
            )
        },
    ],
    '10221DA9': [ # evmhegsmian r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x20000),
                ('r3', 0x30000),
                ('ACC', 0x4),
            ),
            'tests': (
                ('r1', 0xfffffffffffffffe),
                ('ACC', 0xfffffffffffffffe),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x20000),
                ('r3', 0xffff0000),
                ('ACC', 0x4),
            ),
            'tests': (
                ('r1', 0x6),
                ('ACC', 0x6),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x40000),
                ('r3', 0xffff0000),
                ('ACC', 0x4),
            ),
            'tests': (
                ('r1', 0x8),
                ('ACC', 0x8),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x80000000),
                ('r3', 0x7fff0000),
                ('ACC', 0x1),
            ),
            'tests': (
                ('r1', 0x3fff8001),
                ('ACC', 0x3fff8001),
            )
        },
    ],
    '10221D28': [ # evmhegumiaa r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x20000),
                ('r3', 0x30000),
                ('ACC', 0x4),
            ),
            'tests': (
                ('r1', 0xa),
                ('ACC', 0xa),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x20000),
                ('r3', 0xffff0000),
                ('ACC', 0x4),
            ),
            'tests': (
                ('r1', 0x20002),
                ('ACC', 0x20002),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x40000),
                ('r3', 0xffff0000),
                ('ACC', 0x4),
            ),
            'tests': (
                ('r1', 0x40000),
                ('ACC', 0x40000),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x80000000),
                ('r3', 0x7fff0000),
                ('ACC', 0x1),
            ),
            'tests': (
                ('r1', 0x3fff8001),
                ('ACC', 0x3fff8001),
            )
        },
    ],
    '10221DA8': [ # evmhegumian r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x20000),
                ('r3', 0x30000),
                ('ACC', 0x4),
            ),
            'tests': (
                ('r1', 0xfffffffffffffffe),
                ('ACC', 0xfffffffffffffffe),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x20000),
                ('r3', 0xffff0000),
                ('ACC', 0x4),
            ),
            'tests': (
                ('r1', 0xfffffffffffe0006),
                ('ACC', 0xfffffffffffe0006),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x40000),
                ('r3', 0xffff0000),
                ('ACC', 0x4),
            ),
            'tests': (
                ('r1', 0xfffffffffffc0008),
                ('ACC', 0xfffffffffffc0008),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x80000000),
                ('r3', 0x7fff0000),
                ('ACC', 0x1),
            ),
            'tests': (
                ('r1', 0xffffffffc0008001),
                ('ACC', 0xffffffffc0008001),
            )
        },
    ],
    '10221C0B': [ # evmhesmf r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xa0000000c),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffff0000ffff0000),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffffffefffffffc),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffff0000ffff0000),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffffff8fffffff8),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x8001000080010000),
                ('ACC', 0x100000001),
            )
        },
    ],
    '10221C2B': [ # evmhesmfa r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xa0000000c),
                ('ACC', 0xa0000000c),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffff0000ffff0000),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffffffefffffffc),
                ('ACC', 0xfffffffefffffffc),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffff0000ffff0000),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffffff8fffffff8),
                ('ACC', 0xfffffff8fffffff8),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x8001000080010000),
                ('ACC', 0x8001000080010000),
            )
        },
    ],
    '10221D0B': [ # evmhesmfaaw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xe00000010),
                ('ACC', 0xe00000010),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffff0000ffff0000),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x200000000),
                ('ACC', 0x200000000),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffff0000ffff0000),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffffffcfffffffc),
                ('ACC', 0xfffffffcfffffffc),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x8001000180010001),
                ('ACC', 0x8001000180010001),
            )
        },
    ],
    '10221D8B': [ # evmhesmfanw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffffffafffffff8),
                ('ACC', 0xfffffffafffffff8),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffff0000ffff0000),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x600000008),
                ('ACC', 0x600000008),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffff0000ffff0000),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xc0000000c),
                ('ACC', 0xc0000000c),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x7fff00017fff0001),
                ('ACC', 0x7fff00017fff0001),
            )
        },
    ],
    '10221C09': [ # evmhesmi r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x500000006),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffff0000ffff0000),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffffffffffffffe),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffff0000ffff0000),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffffffcfffffffc),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0xc0008000c0008000),
                ('ACC', 0x100000001),
            )
        },
    ],
    '10221C29': [ # evmhesmia r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x500000006),
                ('ACC', 0x500000006),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffff0000ffff0000),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffffffffffffffe),
                ('ACC', 0xfffffffffffffffe),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffff0000ffff0000),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffffffcfffffffc),
                ('ACC', 0xfffffffcfffffffc),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0xc0008000c0008000),
                ('ACC', 0xc0008000c0008000),
            )
        },
    ],
    '10221D09': [ # evmhesmiaaw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x90000000a),
                ('ACC', 0x90000000a),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffff0000ffff0000),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x300000002),
                ('ACC', 0x300000002),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffff0000ffff0000),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x0),
                ('ACC', 0x0),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0xc0008001c0008001),
                ('ACC', 0xc0008001c0008001),
            )
        },
    ],
    '10221D89': [ # evmhesmianw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffffffffffffffe),
                ('ACC', 0xfffffffffffffffe),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffff0000ffff0000),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x500000006),
                ('ACC', 0x500000006),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffff0000ffff0000),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x800000008),
                ('ACC', 0x800000008),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x3fff80013fff8001),
                ('ACC', 0x3fff80013fff8001),
            )
        },
    ],
    '10221C08': [ # evmheumi r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x500000006),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffff0000ffff0000),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xffff0001fffe),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffff0000ffff0000),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x3fffc0003fffc),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x3fff80003fff8000),
                ('ACC', 0x100000001),
            )
        },
    ],
    '10221C28': [ # evmheumia r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x500000006),
                ('ACC', 0x500000006),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffff0000ffff0000),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xffff0001fffe),
                ('ACC', 0xffff0001fffe),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffff0000ffff0000),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x3fffc0003fffc),
                ('ACC', 0x3fffc0003fffc),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x3fff80003fff8000),
                ('ACC', 0x3fff80003fff8000),
            )
        },
    ],
    '10221D08': [ # evmheumiaaw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x90000000a),
                ('ACC', 0x90000000a),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffff0000ffff0000),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x1000300020002),
                ('ACC', 0x1000300020002),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffff0000ffff0000),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x4000000040000),
                ('ACC', 0x4000000040000),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x3fff80013fff8001),
                ('ACC', 0x3fff80013fff8001),
            )
        },
    ],
    '10221D88': [ # evmheumianw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffffffffffffffe),
                ('ACC', 0xfffffffffffffffe),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffff0000ffff0000),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xffff0005fffe0006),
                ('ACC', 0xffff0005fffe0006),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffff0000ffff0000),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffc0008fffc0008),
                ('ACC', 0xfffc0008fffc0008),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0xc0008001c0008001),
                ('ACC', 0xc0008001c0008001),
            )
        },
    ],
    '10221D2F': [ # evmhogsmfaa r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x40000003c),
                ('ACC', 0x40000003c),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x3fffffffc),
                ('ACC', 0x3fffffffc),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x3fffffffc),
                ('ACC', 0x3fffffffc),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x800000008000),
                ('r3', 0x7fff00007fff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x80010001),
                ('ACC', 0x80010001),
            )
        },
    ],
    '10221DAF': [ # evmhogsmfan r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x3ffffffcc),
                ('ACC', 0x3ffffffcc),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x40000000c),
                ('ACC', 0x40000000c),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x40000000c),
                ('ACC', 0x40000000c),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x800000008000),
                ('r3', 0x7fff00007fff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x17fff0001),
                ('ACC', 0x17fff0001),
            )
        },
    ],
    '10221D2D': [ # evmhogsmiaa r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x400000020),
                ('ACC', 0x400000020),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x400000000),
                ('ACC', 0x400000000),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x400000000),
                ('ACC', 0x400000000),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x800000008000),
                ('r3', 0x7fff00007fff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0xc0008001),
                ('ACC', 0xc0008001),
            )
        },
    ],
    '10221DAD': [ # evmhogsmian r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x3ffffffe8),
                ('ACC', 0x3ffffffe8),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x400000008),
                ('ACC', 0x400000008),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x400000008),
                ('ACC', 0x400000008),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x800000008000),
                ('r3', 0x7fff00007fff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x13fff8001),
                ('ACC', 0x13fff8001),
            )
        },
    ],
    '10221D2C': [ # evmhogumiaa r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x400000020),
                ('ACC', 0x400000020),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x400040000),
                ('ACC', 0x400040000),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x400040000),
                ('ACC', 0x400040000),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x800000008000),
                ('r3', 0x7fff00007fff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x13fff8001),
                ('ACC', 0x13fff8001),
            )
        },
    ],
    '10221DAC': [ # evmhogumian r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x3ffffffe8),
                ('ACC', 0x3ffffffe8),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x3fffc0008),
                ('ACC', 0x3fffc0008),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x3fffc0008),
                ('ACC', 0x3fffc0008),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x800000008000),
                ('r3', 0x7fff00007fff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0xc0008001),
                ('ACC', 0xc0008001),
            )
        },
    ],
    '10221C0F': [ # evmhosmf r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x2400000038),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffffffafffffff8),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffffff8fffffff8),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x800000008000),
                ('r3', 0x7fff00007fff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x8001000080010000),
                ('ACC', 0x100000001),
            )
        },
    ],
    '10221C2F': [ # evmhosmfa r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x2400000038),
                ('ACC', 0x2400000038),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffffffafffffff8),
                ('ACC', 0xfffffffafffffff8),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffffff8fffffff8),
                ('ACC', 0xfffffff8fffffff8),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x800000008000),
                ('r3', 0x7fff00007fff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x8001000080010000),
                ('ACC', 0x8001000080010000),
            )
        },
    ],
    '10221D0F': [ # evmhosmfaaw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x280000003c),
                ('ACC', 0x280000003c),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffffffefffffffc),
                ('ACC', 0xfffffffefffffffc),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffffffcfffffffc),
                ('ACC', 0xfffffffcfffffffc),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x800000008000),
                ('r3', 0x7fff00007fff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x8001000180010001),
                ('ACC', 0x8001000180010001),
            )
        },
    ],
    '10221D8F': [ # evmhosmfanw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xffffffe0ffffffcc),
                ('ACC', 0xffffffe0ffffffcc),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xa0000000c),
                ('ACC', 0xa0000000c),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xc0000000c),
                ('ACC', 0xc0000000c),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x800000008000),
                ('r3', 0x7fff00007fff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x7fff00017fff0001),
                ('ACC', 0x7fff00017fff0001),
            )
        },
    ],
    '10221C0D': [ # evmhosmi r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x120000001c),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffffffdfffffffc),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffffffcfffffffc),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x800000008000),
                ('r3', 0x7fff00007fff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0xc0008000c0008000),
                ('ACC', 0x100000001),
            )
        },
    ],
    '10221C2D': [ # evmhosmia r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x120000001c),
                ('ACC', 0x120000001c),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffffffdfffffffc),
                ('ACC', 0xfffffffdfffffffc),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffffffcfffffffc),
                ('ACC', 0xfffffffcfffffffc),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x800000008000),
                ('r3', 0x7fff00007fff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0xc0008000c0008000),
                ('ACC', 0xc0008000c0008000),
            )
        },
    ],
    '10221D0D': [ # evmhosmiaaw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x1600000020),
                ('ACC', 0x1600000020),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x100000000),
                ('ACC', 0x100000000),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x0),
                ('ACC', 0x0),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x800000008000),
                ('r3', 0x7fff00007fff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0xc0008001c0008001),
                ('ACC', 0xc0008001c0008001),
            )
        },
    ],
    '10221D8D': [ # evmhosmianw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffffff2ffffffe8),
                ('ACC', 0xfffffff2ffffffe8),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x700000008),
                ('ACC', 0x700000008),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x800000008),
                ('ACC', 0x800000008),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x800000008000),
                ('r3', 0x7fff00007fff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x3fff80013fff8001),
                ('ACC', 0x3fff80013fff8001),
            )
        },
    ],
    '10221C0C': [ # evmhoumi r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x120000001c),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x2fffd0003fffc),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x3fffc0003fffc),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x800000008000),
                ('r3', 0x7fff00007fff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x3fff80003fff8000),
                ('ACC', 0x100000001),
            )
        },
    ],
    '10221C2C': [ # evmhoumia r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x120000001c),
                ('ACC', 0x120000001c),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x2fffd0003fffc),
                ('ACC', 0x2fffd0003fffc),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x3fffc0003fffc),
                ('ACC', 0x3fffc0003fffc),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x800000008000),
                ('r3', 0x7fff00007fff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x3fff80003fff8000),
                ('ACC', 0x3fff80003fff8000),
            )
        },
    ],
    '10221D0C': [ # evmhoumiaaw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x1600000020),
                ('ACC', 0x1600000020),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x3000100040000),
                ('ACC', 0x3000100040000),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x4000000040000),
                ('ACC', 0x4000000040000),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x800000008000),
                ('r3', 0x7fff00007fff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x3fff80013fff8001),
                ('ACC', 0x3fff80013fff8001),
            )
        },
    ],
    '10221D8C': [ # evmhoumianw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffffff2ffffffe8),
                ('ACC', 0xfffffff2ffffffe8),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffd0007fffc0008),
                ('ACC', 0xfffd0007fffc0008),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffc0008fffc0008),
                ('ACC', 0xfffc0008fffc0008),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x800000008000),
                ('r3', 0x7fff00007fff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0xc0008001c0008001),
                ('ACC', 0xc0008001c0008001),
            )
        },
    ],
    '10221C4F': [ # evmwhsmf r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xa0000000c),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x200000004),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x700000007),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x8000000180000001),
                ('ACC', 0x100000001),
            )
        },
    ],
    '10221C6F': [ # evmwhsmfa r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xa0000000c),
                ('ACC', 0xa0000000c),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x200000004),
                ('ACC', 0x200000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x700000007),
                ('ACC', 0x700000007),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x8000000180000001),
                ('ACC', 0x8000000180000001),
            )
        },
    ],
    '10221C4D': [ # evmwhsmi r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x500000006),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffffffffffffffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xffffffffffffffff),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffffffffffffffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xffffffffffffffff),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0xc0000000c0000000),
                ('ACC', 0x100000001),
            )
        },
    ],
    '10221C6D': [ # evmwhsmia r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x500000006),
                ('ACC', 0x500000006),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffffffffffffffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xffffffffffffffff),
                ('ACC', 0xffffffffffffffff),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffffffffffffffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xffffffffffffffff),
                ('ACC', 0xffffffffffffffff),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0xc0000000c0000000),
                ('ACC', 0xc0000000c0000000),
            )
        },
    ],
    '10221C4C': [ # evmwhumi r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x500000006),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffffffffffffffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x1000200020003),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffffffffffffffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x4000300040003),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x3fffffff3fffffff),
                ('ACC', 0x100000001),
            )
        },
    ],
    '10221C6C': [ # evmwhumia r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x500000006),
                ('ACC', 0x500000006),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffffffffffffffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x1000200020003),
                ('ACC', 0x1000200020003),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffffffffffffffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x4000300040003),
                ('ACC', 0x4000300040003),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x3fffffff3fffffff),
                ('ACC', 0x3fffffff3fffffff),
            )
        },
    ],
    '10221D49': [ # evmwlsmiaaw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x150016001a0020),
                ('ACC', 0x150016001a0020),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffffffffffffffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xffff0001fffe0000),
                ('ACC', 0xffff0001fffe0000),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffffffffffffffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffc0000fffc0000),
                ('ACC', 0xfffc0000fffc0000),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x8000000180000001),
                ('ACC', 0x8000000180000001),
            )
        },
    ],
    '10221DC9': [ # evmwlsmianw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xffeafff2ffe5ffe8),
                ('ACC', 0xffeafff2ffe5ffe8),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0xffffffffffffffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x1000700020008),
                ('ACC', 0x1000700020008),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffffffffffffffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x4000800040008),
                ('ACC', 0x4000800040008),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x8000000180000001),
                ('ACC', 0x8000000180000001),
            )
        },
    ],
    '10221C48': [ # evmwlumi r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x150012001a001c),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffffffffffffffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffbfffcfffbfffc),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x8000000080000000),
                ('ACC', 0x100000001),
            )
        },
    ],
    '10221C68': [ # evmwlumia r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x150012001a001c),
                ('ACC', 0x150012001a001c),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffffffffffffffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffbfffcfffbfffc),
                ('ACC', 0xfffbfffcfffbfffc),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x8000000080000000),
                ('ACC', 0x8000000080000000),
            )
        },
    ],
    '10221D48': [ # evmwlumiaaw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x150016001a0020),
                ('ACC', 0x150016001a0020),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffffffffffffffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffc0000fffc0000),
                ('ACC', 0xfffc0000fffc0000),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x8000000180000001),
                ('ACC', 0x8000000180000001),
            )
        },
    ],
    '10221DC8': [ # evmwlumianw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xffeafff2ffe5ffe8),
                ('ACC', 0xffeafff2ffe5ffe8),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffffffffffffffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x4000800040008),
                ('ACC', 0x4000800040008),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x8000000180000001),
                ('ACC', 0x8000000180000001),
            )
        },
    ],
    '10221C5B': [ # evmwsmf r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xc00340038),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffffffffffffffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffffffffff7fff8),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x8000000100000000),
                ('ACC', 0x100000001),
            )
        },
    ],
    '10221C7B': [ # evmwsmfa r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xc00340038),
                ('ACC', 0xc00340038),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffffffffffffffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffffffffff7fff8),
                ('ACC', 0xfffffffffff7fff8),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x8000000100000000),
                ('ACC', 0x8000000100000000),
            )
        },
    ],
    '10221D5B': [ # evmwsmfaa r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x100034003c),
                ('ACC', 0x100034003c),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffffffffffffffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x3fff7fffc),
                ('ACC', 0x3fff7fffc),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x8000000200000001),
                ('ACC', 0x8000000200000001),
            )
        },
    ],
    '10221DDB': [ # evmwsmfan r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffffff7ffcbffcc),
                ('ACC', 0xfffffff7ffcbffcc),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffffffffffffffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x40008000c),
                ('ACC', 0x40008000c),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x8000000000000001),
                ('ACC', 0x8000000000000001),
            )
        },
    ],
    '10221C59': [ # evmwsmi r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x6001a001c),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffffffffffffffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffffffffffbfffc),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0xc000000080000000),
                ('ACC', 0x100000001),
            )
        },
    ],
    '10221C79': [ # evmwsmia r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x6001a001c),
                ('ACC', 0x6001a001c),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffffffffffffffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffffffffffbfffc),
                ('ACC', 0xfffffffffffbfffc),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0xc000000080000000),
                ('ACC', 0xc000000080000000),
            )
        },
    ],
    '10221D59': [ # evmwsmiaa r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xa001a0020),
                ('ACC', 0xa001a0020),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffffffffffffffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x3fffc0000),
                ('ACC', 0x3fffc0000),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0xc000000180000001),
                ('ACC', 0xc000000180000001),
            )
        },
    ],
    '10221DD9': [ # evmwsmian r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffffffdffe5ffe8),
                ('ACC', 0xfffffffdffe5ffe8),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffffffffffffffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x400040008),
                ('ACC', 0x400040008),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x4000000080000001),
                ('ACC', 0x4000000080000001),
            )
        },
    ],
    '10221C58': [ # evmwumi r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x6001a001c),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffffffffffffffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x40003fffbfffc),
                ('ACC', 0x400000004),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x3fffffff80000000),
                ('ACC', 0x100000001),
            )
        },
    ],
    '10221C78': [ # evmwumia r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x6001a001c),
                ('ACC', 0x6001a001c),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffffffffffffffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x40003fffbfffc),
                ('ACC', 0x40003fffbfffc),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x3fffffff80000000),
                ('ACC', 0x3fffffff80000000),
            )
        },
    ],
    '10221D58': [ # evmwumiaa r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xa001a0020),
                ('ACC', 0xa001a0020),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffffffffffffffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0x40007fffc0000),
                ('ACC', 0x40007fffc0000),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0x4000000080000001),
                ('ACC', 0x4000000080000001),
            )
        },
    ],
    '10221DD8': [ # evmwumian r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffffffdffe5ffe8),
                ('ACC', 0xfffffffdffe5ffe8),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffffffffffffffff),
                ('ACC', 0x400000004),
            ),
            'tests': (
                ('r1', 0xfffc000000040008),
                ('ACC', 0xfffc000000040008),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000080000000),
                ('r3', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
            ),
            'tests': (
                ('r1', 0xc000000180000001),
                ('ACC', 0xc000000180000001),
            )
        },
    ],
    '10221C03': [ # evmhessf r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0xa0000000c),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffffffffffffffff),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0xfffffff8fffffff8),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000800080008000),
                ('r3', 0x8000800080008000),
                ('ACC', 0x100000001),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
                ('SPEFSCR', 0xc000c000),
            )
        },
    ],
    '10221C23': [ # evmhessfa r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0xa0000000c),
                ('ACC', 0xa0000000c),
                ('SPEFSCR', 0x0),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffffffffffffffff),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0xfffffff8fffffff8),
                ('ACC', 0xfffffff8fffffff8),
                ('SPEFSCR', 0x0),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000800080008000),
                ('r3', 0x8000800080008000),
                ('ACC', 0x100000001),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x7fffffff7fffffff),
                ('ACC', 0x7fffffff7fffffff),
                ('SPEFSCR', 0xc000c000),
            )
        },
    ],
    '10221D03': [ # evmhessfaaw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0xe00000010),
                ('ACC', 0xe00000010),
                ('SPEFSCR', 0x0),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x3fff00003fff0000),
                ('r3', 0x3fff0000ffff0000),
                ('ACC', 0x7fffffff80000000),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x7fffffff80000000),
                ('ACC', 0x7fffffff80000000),
                ('SPEFSCR', 0xc000c000),
            )
        },
    ],
    '10221D83': [ # evmhessfanw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0xfffffffafffffff8),
                ('ACC', 0xfffffffafffffff8),
                ('SPEFSCR', 0x0),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x3fff00003fff0000),
                ('r3', 0x3fff0000ffff0000),
                ('ACC', 0x7fffffff80000000),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x6000fffd80007ffe),
                ('ACC', 0x6000fffd80007ffe),
                ('SPEFSCR', 0x0),
            )
        },
    ],
    '10221C07': [ # evmhossf r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x2400000038),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffffffffffffffff),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0xfffffff8fffffff8),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000800080008000),
                ('r3', 0x8000800080008000),
                ('ACC', 0x100000001),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x7fffffff7fffffff),
                ('ACC', 0x100000001),
                ('SPEFSCR', 0xc000c000),
            )
        },
    ],
    '10221C27': [ # evmhossfa r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x2400000038),
                ('ACC', 0x2400000038),
                ('SPEFSCR', 0x0),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4000400040004),
                ('r3', 0xffffffffffffffff),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0xfffffff8fffffff8),
                ('ACC', 0xfffffff8fffffff8),
                ('SPEFSCR', 0x0),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000800080008000),
                ('r3', 0x8000800080008000),
                ('ACC', 0x100000001),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x7fffffff7fffffff),
                ('ACC', 0x7fffffff7fffffff),
                ('SPEFSCR', 0xc000c000),
            )
        },
    ],
    '10221D07': [ # evmhossfaaw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x280000003c),
                ('ACC', 0x280000003c),
                ('SPEFSCR', 0x0),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x3fff00003fff),
                ('r3', 0x3fff0000ffff),
                ('ACC', 0x7fffffff80000000),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x7fffffff80000000),
                ('ACC', 0x7fffffff80000000),
                ('SPEFSCR', 0xc000c000),
            )
        },
    ],
    '10221D87': [ # evmhossfanw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0xffffffe0ffffffcc),
                ('ACC', 0xffffffe0ffffffcc),
                ('SPEFSCR', 0x0),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x3fff00003fff),
                ('r3', 0x3fff0000ffff),
                ('ACC', 0x7fffffff80000000),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x6000fffd80007ffe),
                ('ACC', 0x6000fffd80007ffe),
                ('SPEFSCR', 0x0),
            )
        },
    ],
    '10221D01': [ # evmhessiaaw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x90000000a),
                ('ACC', 0x90000000a),
                ('SPEFSCR', 0x0),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x3fff00003fff0000),
                ('r3', 0x3fff0000ffff0000),
                ('ACC', 0x7fffffff80000000),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x7fffffff80000000),
                ('ACC', 0x7fffffff80000000),
                ('SPEFSCR', 0xc000c000),
            )
        },
    ],
    '10221D81': [ # evmhessianw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0xfffffffffffffffe),
                ('ACC', 0xfffffffffffffffe),
                ('SPEFSCR', 0x0),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x3fff00003fff0000),
                ('r3', 0x3fff0000ffff0000),
                ('ACC', 0x7fffffff80000000),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x70007ffe80003fff),
                ('ACC', 0x70007ffe80003fff),
                ('SPEFSCR', 0x0),
            )
        },
    ],
    '10221D00': [ # evmheusiaaw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0xffff00003fff0000),
                ('r3', 0xffff0000ffff0000),
                ('ACC', 0xffffffff80000000),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0xffffffffbffec001),
                ('ACC', 0xffffffffbffec001),
                ('SPEFSCR', 0xc0000000),
            )
        },
    ],
    '10221D80': [ # evmheusianw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0xffff00003fff0000),
                ('r3', 0xffff0000ffff0000),
                ('ACC', 0x80000000),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x40013fff),
                ('ACC', 0x40013fff),
                ('SPEFSCR', 0xc0000000),
            )
        },
    ],
    '10221D05': [ # evmhossiaaw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x1600000020),
                ('ACC', 0x1600000020),
                ('SPEFSCR', 0x0),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x3fff00003fff),
                ('r3', 0x3fff0000ffff),
                ('ACC', 0x7fffffff80000000),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x7fffffff80000000),
                ('ACC', 0x7fffffff80000000),
                ('SPEFSCR', 0xc000c000),
            )
        },
    ],
    '10221D85': [ # evmhossianw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1000300020004),
                ('r3', 0x5000600030007),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0xfffffff2ffffffe8),
                ('ACC', 0xfffffff2ffffffe8),
                ('SPEFSCR', 0x0),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x3fff00003fff),
                ('r3', 0x3fff0000ffff),
                ('ACC', 0x7fffffff80000000),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x70007ffe80003fff),
                ('ACC', 0x70007ffe80003fff),
                ('SPEFSCR', 0x0),
            )
        },
    ],
    '10221D04': [ # evmhousiaaw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0xffff00003fff),
                ('r3', 0xffff0000ffff),
                ('ACC', 0xffffffff80000000),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0xffffffffbffec001),
                ('ACC', 0xffffffffbffec001),
                ('SPEFSCR', 0xc0000000),
            )
        },
    ],
    '10221D84': [ # evmhousianw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0xffff00003fff),
                ('r3', 0xffff0000ffff),
                ('ACC', 0x80000000),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x40013fff),
                ('ACC', 0x40013fff),
                ('SPEFSCR', 0xc0000000),
            )
        },
    ],
    '10221C47': [ # evmwhssf r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1234567880000000),
                ('r3', 0x8765432180000000),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0xeed8ed1a7fffffff),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0xc000),
            )
        },
    ],
    '10221C67': [ # evmwhssfa r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1234567880000000),
                ('r3', 0x8765432180000000),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0xeed8ed1a7fffffff),
                ('ACC', 0xeed8ed1a7fffffff),
                ('SPEFSCR', 0xc000),
            )
        },
    ],
    '10221C53': [ # evmwssf r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1234567880000000),
                ('r3', 0x8765432180000000),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x7fffffffffffffff),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0xc000),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000012345678),
                ('r3', 0x8000000087654321),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0xeed8ed1ae1711af0),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            )
        },
    ],
    '10221C73': [ # evmwssfa r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1234567880000000),
                ('r3', 0x8765432180000000),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x7fffffffffffffff),
                ('ACC', 0x7fffffffffffffff),
                ('SPEFSCR', 0xc000),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000012345678),
                ('r3', 0x8000000087654321),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0xeed8ed1ae1711af0),
                ('ACC', 0xeed8ed1ae1711af0),
                ('SPEFSCR', 0x0),
            )
        },
    ],
    '10221D53': [ # evmwssfaa r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1234567880000000),
                ('r3', 0x8765432180000000),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x7fffffffffffffff),
                ('ACC', 0x7fffffffffffffff),
                ('SPEFSCR', 0xc000),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000012345678),
                ('r3', 0x8000000087654321),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0xeed8ed1ee1711af4),
                ('ACC', 0xeed8ed1ee1711af4),
                ('SPEFSCR', 0x0),
            )
        },
    ],
    '10221DD3': [ # evmwssfan r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1234567880000000),
                ('r3', 0x8765432180000000),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x8000000400000005),
                ('ACC', 0x8000000400000005),
                ('SPEFSCR', 0xc000),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000012345678),
                ('r3', 0x8000000087654321),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x112712e91e8ee514),
                ('ACC', 0x112712e91e8ee514),
                ('SPEFSCR', 0x0),
            )
        },
    ],
    '10221D41': [ # evmwlssiaaw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1234567880000000),
                ('r3', 0x8765432180000000),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x70b88d7c00000004),
                ('ACC', 0x70b88d7c00000004),
                ('SPEFSCR', 0x0),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000012345678),
                ('r3', 0x8000000087654321),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x470b88d7c),
                ('ACC', 0x470b88d7c),
                ('SPEFSCR', 0x0),
            )
        },
    ],
    '10221DC1': [ # evmwlssianw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1234567880000000),
                ('r3', 0x8765432180000000),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x8f47728c00000004),
                ('ACC', 0x8f47728c00000004),
                ('SPEFSCR', 0x0),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000012345678),
                ('r3', 0x8000000087654321),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x48f47728c),
                ('ACC', 0x48f47728c),
                ('SPEFSCR', 0x0),
            )
        },
    ],
    '10221D40': [ # evmwlusiaaw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1234567880000000),
                ('r3', 0x8765432180000000),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x70b88d7c00000004),
                ('ACC', 0x70b88d7c00000004),
                ('SPEFSCR', 0x0),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000012345678),
                ('r3', 0x8000000087654321),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x470b88d7c),
                ('ACC', 0x470b88d7c),
                ('SPEFSCR', 0x0),
            )
        },
    ],
    '10221DC0': [ # evmwlusianw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1234567880000000),
                ('r3', 0x8765432180000000),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x4),
                ('ACC', 0x4),
                ('SPEFSCR', 0xc0000000),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000012345678),
                ('r3', 0x8000000087654321),
                ('ACC', 0x400000004),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x400000000),
                ('ACC', 0x400000000),
                ('SPEFSCR', 0xc000),
            )
        },
    ],
    '10221CC7': [ # evdivwu r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4444444411111111),
                ('r3', 0x2222222200000000),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x2ffffffff),
                ('SPEFSCR', 0xc000),
            )
        },
    ],
    '10221CC6': [ # evdivws r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x4444444411111111),
                ('r3', 0x2222222200000000),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x27fffffff),
                ('SPEFSCR', 0xc000),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0xffffffff33333333),
                ('r3', 0x22222222),
                ('SPEFSCR', 0x0),
            ),
            'tests': (
                ('r1', 0x8000000000000001),
                ('SPEFSCR', 0xc0000000),
            )
        },
    ],
    '13011234': [ # evcmpeq cr6,r1,r2
        {
            'setup': (
                ('r1', 0x1111111122222222),
                ('r2', 0x1111111122222222),
                ('cr', 0x0),
            ),
            'tests': (
                ('cr', 0xf0),
            )
        },
        {
            'setup': (
                ('r1', 0x1111111122222222),
                ('r2', 0x3333333322222222),
                ('cr', 0x0),
            ),
            'tests': (
                ('cr', 0x60),
            )
        },
        {
            'setup': (
                ('r1', 0x1111111122222222),
                ('r2', 0x3333333344444444),
                ('cr', 0x0),
            ),
            'tests': (
                ('cr', 0x0),
            )
        },
    ],
    '13011231': [ # evcmpgts cr6,r1,r2
        {
            'setup': (
                ('r1', 0x1111111122222222),
                ('r2', 0x1111111122222222),
                ('cr', 0x0),
            ),
            'tests': (
                ('cr', 0x0),
            )
        },
        {
            'setup': (
                ('r1', 0x1111111122222222),
                ('r2', 0x4444444444444444),
                ('cr', 0x0),
            ),
            'tests': (
                ('cr', 0x0),
            )
        },
        {
            'setup': (
                ('r1', 0x1111111122222222),
                ('r2', 0xffffffffffffffff),
                ('cr', 0x0),
            ),
            'tests': (
                ('cr', 0xf0),
            )
        },
    ],
    '13011230': [ # evcmpgtu cr6,r1,r2
        {
            'setup': (
                ('r1', 0x1111111122222222),
                ('r2', 0x1111111122222222),
                ('cr', 0x0),
            ),
            'tests': (
                ('cr', 0x0),
            )
        },
        {
            'setup': (
                ('r1', 0x1111111122222222),
                ('r2', 0x0),
                ('cr', 0x0),
            ),
            'tests': (
                ('cr', 0xf0),
            )
        },
        {
            'setup': (
                ('r1', 0x1111111122222222),
                ('r2', 0xffffffffffffffff),
                ('cr', 0x0),
            ),
            'tests': (
                ('cr', 0x0),
            )
        },
    ],
    '13011233': [ # evcmplts cr6,r1,r2
        {
            'setup': (
                ('r1', 0x1111111122222222),
                ('r2', 0x1111111122222222),
                ('cr', 0x0),
            ),
            'tests': (
                ('cr', 0x0),
            )
        },
        {
            'setup': (
                ('r1', 0x1111111122222222),
                ('r2', 0x4444444444444444),
                ('cr', 0x0),
            ),
            'tests': (
                ('cr', 0xf0),
            )
        },
        {
            'setup': (
                ('r1', 0x1111111122222222),
                ('r2', 0xffffffffffffffff),
                ('cr', 0x0),
            ),
            'tests': (
                ('cr', 0x0),
            )
        },
    ],
    '13011232': [ # evcmpltu cr6,r1,r2
        {
            'setup': (
                ('r1', 0x1111111122222222),
                ('r2', 0x1111111122222222),
                ('cr', 0x0),
            ),
            'tests': (
                ('cr', 0x0),
            )
        },
        {
            'setup': (
                ('r1', 0x1111111122222222),
                ('r2', 0x4444444444444444),
                ('cr', 0x0),
            ),
            'tests': (
                ('cr', 0xf0),
            )
        },
        {
            'setup': (
                ('r1', 0x1111111122222222),
                ('r2', 0xffffffffffffffff),
                ('cr', 0x0),
            ),
            'tests': (
                ('cr', 0xf0),
            )
        },
    ],
    '10221A1E': [ # evnand  r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x123456789abcdef),
                ('r3', 0xff00ff00ff00ff00),
            ),
            'tests': (
                ('r1', 0xfeffbaff76ff32ff),
            )
        },
    ],
    '10221A18': [ # evnor   r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x123456789abcdef),
                ('r3', 0xff00ff00ff00ff00),
            ),
            'tests': (
                ('r1', 0xdc009800540010),
            )
        },
    ],
    '10221A17': [ # evor    r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x123456789abcdef),
                ('r3', 0xff00ff00ff00ff00),
            ),
            'tests': (
                ('r1', 0xff23ff67ffabffef),
            )
        },
    ],
    '10221A16': [ # evxor   r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x123456789abcdef),
                ('r3', 0xff00ff00ff00ff00),
            ),
            'tests': (
                ('r1', 0xfe23ba6776ab32ef),
            )
        },
    ],
    '10221A1B': [ # evorc   r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x123456789abcdef),
                ('r3', 0xff00ff00ff00ff00),
            ),
            'tests': (
                ('r1', 0x1ff45ff89ffcdff),
            )
        },
    ],
    '10220209': [ # evneg   r1,r2
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1111111188888888),
            ),
            'tests': (
                ('r1', 0xeeeeeeef77777778),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x8000000000000000),
            ),
            'tests': (
                ('r1', 0x8000000000000000),
            )
        },
    ],
    '10221A28': [ # evrlw   r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x123456789abcdef),
                ('r3', 0x1f00000001),
            ),
            'tests': (
                ('r1', 0x8091a2b313579bdf),
            )
        },
    ],
    '10221A2A': [ # evrlwi  r1,r2,0x3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x123456789abcdef),
            ),
            'tests': (
                ('r1', 0x91a2b384d5e6f7c),
            )
        },
    ],
    '1022020C': [ # evrndw r1,r2
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x123456789abcdef),
            ),
            'tests': (
                ('r1', 0x123000089ac0000),
            )
        },
    ],
    '10221A7E': [ # evsel   r1,r2,r3,cr6
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x11223344556677),
                ('r3', 0x8899aabbccddeeff),
                ('cr', 0x40),
            ),
            'tests': (
                ('r1', 0x8899aabb44556677),
            )
        },
    ],
    '10221A24': [ # evslw   r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x11223344556677),
                ('r3', 0x8899aa05ccddee11),
            ),
            'tests': (
                ('r1', 0x2244660ccee0000),
            )
        },
    ],
    '10221A26': [ # evslwi  r1,r2,0x3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x11223344556677),
            ),
            'tests': (
                ('r1', 0x89119822ab33b8),
            )
        },
    ],
    '10221A23': [ # evsrwis r1,r2,0x3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1122338899aabb),
            ),
            'tests': (
                ('r1', 0x22446f1133557),
            )
        },
    ],
    '10221A22': [ # evsrwiu r1,r2,0x3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1122338899aabb),
            ),
            'tests': (
                ('r1', 0x2244611133557),
            )
        },
    ],
    '10221A21': [ # evsrws  r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1122338899aabb),
                ('r3', 0x3fffffff02),
            ),
            'tests': (
                ('r1', 0xe2266aae),
            )
        },
    ],
    '10221A20': [ # evsrwu  r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1122338899aabb),
                ('r3', 0x3fffffff02),
            ),
            'tests': (
                ('r1', 0x22266aae),
            )
        },
    ],
    '102204CB': [ # evsubfsmiaaw r1,r2
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x200000002),
                ('ACC', 0x180000000),
            ),
            'tests': (
                ('r1', 0xffffffff7ffffffe),
            )
        },
    ],
    '102204C3': [ # evsubfssiaaw r1,r2
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x200000002),
                ('ACC', 0x180000000),
            ),
            'tests': (
                ('r1', 0xffffffff80000000),
            )
        },
    ],
    '102204CA': [ # evsubfumiaaw r1,r2
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x200000002),
                ('ACC', 0x180000000),
            ),
            'tests': (
                ('r1', 0xffffffff7ffffffe),
            )
        },
    ],
    '102204C2': [ # evsubfusiaaw r1,r2
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x200000002),
                ('ACC', 0x180000000),
            ),
            'tests': (
                ('r1', 0x7ffffffe),
            )
        },
    ],
    '10221A04': [ # evsubfw r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x200000002),
                ('r3', 0x180000000),
            ),
            'tests': (
                ('r1', 0xffffffff7ffffffe),
            )
        },
    ],
    '103F1206': [ # evsubifw r1,31,r2
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0xdfac02252020dfbf),
                ('ACC', 0xacacacacacacacac),
            ),
            'tests': (
                ('r1', 0xdfac02062020dfa0),
                ('ACC', 0xacacacacacacacac),
            )
        },
    ],
    '103C022B': [ # evsplatfi r1,-0x4
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
            ),
            'tests': (
                ('r1', 0xe0000000e0000000),
            )
        },
    ],
    '103C0229': [ # evsplati r1,-0x4
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
            ),
            'tests': (
                ('r1', 0xfffffffcfffffffc),
            )
        },
    ],
    '102C0229': [ # evsplati r1,0xc
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
            ),
            'tests': (
                ('r1', 0xc0000000c),
            )
        },
    ],
    '10228321': [ # evstdd  r1,0x80(r2)
        {
            'setup': (
                ('r1', 0xab9371d0fedcba98),
                ('r2', 0x10000000),
                (0x10000080, bytes.fromhex('dfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10000080, bytes.fromhex('ab9371d0fedcba98')),
            )
        },
    ],
    '10221B20': [ # evstddx r1,r2,r3
        {
            'setup': (
                ('r1', 0xab9371d0fedcba98),
                ('r2', 0x10000000),
                ('r3', 0x80),
                (0x10000080, bytes.fromhex('dfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10000080, bytes.fromhex('ab9371d0fedcba98')),
            )
        },
    ],
    '7C221F3E': [ # evstddepx r1,r2,r3
        {
            'setup': (
                ('r1', 0xab9371d0fedcba98),
                ('r2', 0x10000000),
                ('r3', 0x80),
                (0x10000080, bytes.fromhex('dfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10000080, bytes.fromhex('ab9371d0fedcba98')),
            )
        },
    ],
    '10228325': [ # evstdh  r1,0x80(r2)
        {
            'setup': (
                ('r1', 0xab9371d0fedcba98),
                ('r2', 0x10000000),
                (0x10000080, bytes.fromhex('dfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10000080, bytes.fromhex('ab9371d0fedcba98')),
            )
        },
    ],
    '10228323': [ # evstdw  r1,0x80(r2)
        {
            'setup': (
                ('r1', 0xab9371d0fedcba98),
                ('r2', 0x10000000),
                (0x10000080, bytes.fromhex('dfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10000080, bytes.fromhex('ab9371d0fedcba98')),
            )
        },
    ],
    '10221B24': [ # evstdhx r1,r2,r3
        {
            'setup': (
                ('r1', 0xab9371d0fedcba98),
                ('r2', 0x10000000),
                ('r3', 0x80),
                (0x10000080, bytes.fromhex('dfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10000080, bytes.fromhex('ab9371d0fedcba98')),
            )
        },
    ],
    '10221B22': [ # evstdwx r1,r2,r3
        {
            'setup': (
                ('r1', 0xab9371d0fedcba98),
                ('r2', 0x10000000),
                ('r3', 0x80),
                (0x10000080, bytes.fromhex('dfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10000080, bytes.fromhex('ab9371d0fedcba98')),
            )
        },
    ],
    '10228331': [ # evstwhe r1,0x40(r2)
        {
            'setup': (
                ('r1', 0xab9371d0fedcba98),
                ('r2', 0x10000000),
                (0x10000040, bytes.fromhex('dfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10000040, bytes.fromhex('ab93fedcdfdfdfdf')),
            )
        },
    ],
    '10228335': [ # evstwho r1,0x40(r2)
        {
            'setup': (
                ('r1', 0xab9371d0fedcba98),
                ('r2', 0x10000000),
                (0x10000040, bytes.fromhex('dfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10000040, bytes.fromhex('71d0ba98dfdfdfdf')),
            )
        },
    ],
    '10221B30': [ # evstwhex r1,r2,r3
        {
            'setup': (
                ('r1', 0xab9371d0fedcba98),
                ('r2', 0x10000000),
                ('r3', 0x40),
                (0x10000040, bytes.fromhex('dfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10000040, bytes.fromhex('ab93fedcdfdfdfdf')),
            )
        },
    ],
    '10221B34': [ # evstwhox r1,r2,r3
        {
            'setup': (
                ('r1', 0xab9371d0fedcba98),
                ('r2', 0x10000000),
                ('r3', 0x40),
                (0x10000040, bytes.fromhex('dfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10000040, bytes.fromhex('71d0ba98dfdfdfdf')),
            )
        },
    ],
    '10228339': [ # evstwwe r1,0x40(r2)
        {
            'setup': (
                ('r1', 0xab9371d0fedcba98),
                ('r2', 0x10000000),
                (0x10000040, bytes.fromhex('dfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10000040, bytes.fromhex('ab9371d0dfdfdfdf')),
            )
        },
    ],
    '1022833D': [ # evstwwo r1,0x40(r2)
        {
            'setup': (
                ('r1', 0xab9371d0fedcba98),
                ('r2', 0x10000000),
                (0x10000040, bytes.fromhex('dfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10000040, bytes.fromhex('fedcba98dfdfdfdf')),
            )
        },
    ],
    '10221B38': [ # evstwwex r1,r2,r3
        {
            'setup': (
                ('r1', 0xab9371d0fedcba98),
                ('r2', 0x10000000),
                ('r3', 0x40),
                (0x10000040, bytes.fromhex('dfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10000040, bytes.fromhex('ab9371d0dfdfdfdf')),
            )
        },
    ],
    '10221B3C': [ # evstwwox r1,r2,r3
        {
            'setup': (
                ('r1', 0xab9371d0fedcba98),
                ('r2', 0x10000000),
                ('r3', 0x40),
                (0x10000040, bytes.fromhex('dfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10000040, bytes.fromhex('fedcba98dfdfdfdf')),
            )
        },
    ],
    '10221A0F': [ # brinc   r1,r2,r3
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1122334455667788),
                ('r3', 0x0),
            ),
            'tests': (
                ('r1', 0xdfdfdfdf55660000),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1122334455667788),
                ('r3', 0xffffffffffff0000),
            ),
            'tests': (
                ('r1', 0xdfdfdfdf55660000),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1122334455667788),
                ('r3', 0xffffffffffffff00),
            ),
            'tests': (
                ('r1', 0xdfdfdfdf5566f700),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1122334455667788),
                ('r3', 0xffffffffffff00ff),
            ),
            'tests': (
                ('r1', 0xdfdfdfdf55660048),
            )
        },
        {
            'setup': (
                ('r1', 0xdfdfdfdfdfdfdfdf),
                ('r2', 0x1122334455667788),
                ('r3', 0xff),
            ),
            'tests': (
                ('r1', 0xdfdfdfdf55660048),
            )
        },
    ],
}
