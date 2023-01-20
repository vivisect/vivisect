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

_1p1 = 0x3FF199999999999A # 1.1
_2p2 = 0x400199999999999A # 2.2
_3p3 = 0x400A666666666667 # 3.3
_4p4 = 0x401199999999999A
_5p5 = 0x4016000000000000
pi = 0x400921fb54442d18


emutests = {
    'FC00F025': [ # fdiv. f0,f0,f30
       {
           'setup': (
                ('f30', 0x400199999999999A),
                ('f0', 0x3FF199999999999A),
                ('cr1',0b0000),
                ('fpscr',0x0)
           ),
           'tests': (
               ('f30', 0x400199999999999A),
               ('f0', 0x3fe0000000000000),
               ('cr1', 0b0000),
               ('fpscr',0x40000)
           ),
       },
       {
           'setup': (
                ('f30', 0),
                ('f0', 0x3FF199999999999A),
                ('cr1',0b0000),
                ('fpscr',0x0)
           ),
           'tests': (
               ('f30', 0),
               ('f0', 0),
               ('cr1', 0b1000),
               ('fpscr',0x84020000)
           ),
       }
    ],  # fdiv f0,f0,f30  Would like to see how noisy handles NAN operations with this

    'eC00F025': [ # fdivs. f0,f0,f30
       {
           'setup': (
                ('f30', 0x400199999999999A),
                ('f0', 0x3FF199999999999A),
                ('cr1',0b0000),
                ('fpscr',0x0)
           ),
           'tests': (
               ('f30', 0x400199999999999A),
               ('f0', 0x3fe0000000000000),
               ('cr1', 0b0000),
               ('fpscr',0x40000)
           ),
       },
       {
           'setup': (
                ('f30', 0),
                ('f0', 0x3FF1999980000000),
                ('cr1',0b0000),
                ('fpscr',0x0)
           ),
           'tests': (
               ('f30', 0),
               ('f0', 0),
               ('cr1', 0b1000),
               ('fpscr',0x84020000)
           ),
       }
    ],  # fdivs f0,f0,f30  Would like to see how noisy handles NAN operations with this

    'fc0118bb': [ # fmadd. f0,f1,f2,f3
       {
           'setup': (
                ('f0', 0),
                ('f1', 0x3FF199999999999A), # 1.1
                ('f2', 0x400199999999999A), # 2.2
                ('f3', 0x3FF0000000000000), # 1
                ('cr1',0b0000),
                ('fpscr',0x0)
           ),
           'tests': (
               ('f0', 0x400B5C28F5C28F5D), # 3.42
               ('cr1', 0b0000),
               ('fpscr',0x40000)
           ),
       },
       {
           'setup': (
                ('f0', 0),
                ('f1', 0), 
                ('f2', 0x400199999999999A), # 2.2
                ('f3', 0x3FF0000000000000), # 1
                ('cr1',0b0000),
                ('fpscr',0x0)
           ),
           'tests': (
               ('f0', 0x3FF0000000000000), # 1
               ('cr1', 0b0000),
               ('fpscr',0x40000)
           ),
       },
       # {  Can't confirm NAN stuff
       #     'setup': (
       #          ('f0', 0),
       #          ('f1', FP_DOUBLE_NEG_PYNAN), # 
       #          ('f2', 0x400199999999999A), # 2.2
       #          ('f3', 0x3FF0000000000000), # 1
       #          ('cr1',0b0000),
       #          ('fpscr',0x0)
       #     ),
       #     'tests': (
       #         ('f0', 0x3FF0000000000000), # 1
       #         ('cr1', 0b0000),
       #         ('fpscr',0x40000)
       #     ),
       # },
       
    ],  # fmadd. f0,f1,f2,f3

    'ec0110fb': [ # fmadds. f0,f1,f3,f2
       {
           'setup': (
                ('f0', 0),
                ('f1', 0x3FF199999999999A), # 1.1
                ('f2', 0x3FF0000000000000), # 2.2
                ('f3', 0x400199999999999A), # 0x400199999999999A
                ('cr1',0b0000),
                ('fpscr',0x0)
           ),
           'tests': (
               ('f0', 0x400b5c28e0000000), # 3.42
               ('cr1', 0b0000),
               ('fpscr',0x40000)
           ),
       },
       {
           'setup': (
                ('f0', 0),
                ('f1', 0), 
                ('f2', 0x400199999999999A), # 2.2
                ('f3', 0x3FF0000000000000), # 1
                ('cr1',0b0000),
                ('fpscr',0x0)
           ),
           'tests': (
               ('f0', 0x4001999980000000), # 2.2
               ('cr1', 0b0000),
               ('fpscr',0x40000)
           ),
       },
       {
           'setup': (
                ('f0', 0),
                ('f1', pi), 
                ('f2', 0x400199999999999A), # 2.2
                ('f3', 0x400199999999999A), # 2.2
                ('cr1',0b0000),
                ('fpscr',0x0)

           ),
           'tests': (
               ('f0', 0x4022391700000000), # 1
               ('cr1', 0b0000),
               ('fpscr',0x40000)
           ),
       },
       # {  Can't confirm NAN stuff
       #     'setup': (
       #          ('f0', 0),
       #          ('f1', FP_DOUBLE_NEG_PYNAN), # 
       #          ('f2', 0x400199999999999A), # 2.2
       #          ('f3', 0x3FF0000000000000), # 1
       #          ('cr1',0b0000),
       #          ('fpscr',0x0)
       #     ),
       #     'tests': (
       #         ('f0', 0x3FF0000000000000), # 1
       #         ('cr1', 0b0000),
       #         ('fpscr',0x40000)
       #     ),
       # },
       
    ],  # fmadds. f0,f1,f2,f3

    'fc0118b9': [ # fmsub. f0,f1,f2,f3
       {
           'setup': (
                ('f0', 0),
                ('f1', 0x3FF199999999999A), # 1.1
                ('f2', 0x400199999999999A), # 2.2
                ('f3', 0x3FF0000000000000), # 1
                ('cr1',0b0000),
                ('fpscr',0x0)
           ),
           'tests': (
               ('f0', 0x3ff6b851eb851eba), # 3.42
               ('cr1', 0b0000),
               ('fpscr',0x40000)
           ),
       },
       {
           'setup': (
                ('f0', 0),
                ('f1', 0), 
                ('f2', 0x400199999999999A), # 2.2
                ('f3', 0x3FF0000000000000), # 1
                ('cr1',0b0000),
                ('fpscr',0x0)
           ),
           'tests': (
               ('f0', 0xbff0000000000000), # 1
               ('cr1', 0b0000),
               ('fpscr',0x80000)
           ),
       },
       
    ],  # fmsub. f0,f1,f2,f3

    'ec0118b9': [ # fmsubs. f0,f1,f2,f3
       {
           'setup': (
                ('f0', 0),
                ('f1', 0x3FF199999999999A), # 1.1
                ('f2', 0x400199999999999A), # 2.2
                ('f3', 0x3FF0000000000000), # 1
                ('cr1',0b0000),
                ('fpscr',0x0)
           ),
           'tests': (
               ('f0', 0x3ff6b851e0000000), # 3.42
               ('cr1', 0b0000),
               ('fpscr',0x40000)
           ),
       },
       {
           'setup': (
                ('f0', 0),
                ('f1', 0), 
                ('f2', 0x400199999999999A), # 2.2
                ('f3', 0x3FF0000000000000), # 1
                ('cr1',0b0000),
                ('fpscr',0x0)
           ),
           'tests': (
               ('f0', 0xbff0000000000000), # 1
               ('cr1', 0b0000),
               ('fpscr',0x80000)
           ),
       },
       {
           'setup': (
                ('f0', 0),
                ('f1', pi), 
                ('f2', 0x400199999999999A), # 2.2
                ('f3', 0x3FF0000000000000), # 1
                ('cr1',0b0000),
                ('fpscr',0x0)
           ),
           'tests': (
               ('f0', 0x4017a56140000000), # 1
               ('cr1', 0b0000),
               ('fpscr',0x40000)
           ),
       },
    ],  # fmsubs. f0,f1,f2,f3

    'fc01f8b3': [ # fmul. f0,f1,f2
       {
           'setup': (
                ('f0', 0),
                ('f1', 0x3FF199999999999A), # 1.1
                ('f2', 0x400199999999999A), # 2.2
                ('cr1',0b0000),
                ('fpscr',0x0)
           ),
           'tests': (
                ('f3', 0x3FF0000000000000), # 1
                ('f0', 0x40035C28F5C28F5D),# 2.42
                ('cr1', 0b0000),
                ('fpscr',0x40000)
           ),
       },
       {
           'setup': (
                ('f0', 0),
                ('f1', 0), 
                ('f2', 0x400199999999999A), # 2.2
                ('cr1',0b0000),
                ('fpscr',0x0)
           ),
           'tests': (
               ('f0', 0x0),
               ('cr1', 0b0000),
               ('fpscr',0x20000)
           ),
       },
       {
           'setup': (
                ('f0', 0),
                ('f1', 0x3FF0000000000000), 
                ('f2', 0xC00199999999999A), # -2.2
                ('cr1',0b0000),
                ('fpscr',0x0)
           ),
           'tests': (
               ('f0', 0xC00199999999999A),
               ('cr1', 0b0000),
               ('fpscr',0x80000)
           ),
       },
       {
           'setup': (
                ('f0', 0),
                ('f1', 0x4000000000000000), # 2
                ('f2', 0xC00199999999999A), # -2.2
                ('cr1',0b0000),
                ('fpscr',0x0)
           ),
           'tests': (
               ('f0', 0xC01199999999999A), # -4.4
               ('cr1', 0b0000),
               ('fpscr',0x80000)
           ),
       },
       
    ],  # fmul. f0,f1,f2,f3

    'ec0100b3': [ # fmuls. f0,f1,f2
       {
           'setup': (
                ('f0', 0),
                ('f1', 0x3FF199999999999A), # 1.1
                ('f2', 0x400199999999999A), # 2.2
                ('cr1',0b0000),
                ('fpscr',0x0)
           ),
           'tests': (
                ('f0', 0x40035c28e0000000),# 2.42
                ('cr1', 0b0000),
                ('fpscr',0x40000)
           ),
       },
       {
           'setup': (
                ('f0', 0),
                ('f1', 0), 
                ('f2', 0x400199999999999A), # 2.2
                ('cr1',0b0000),
                ('fpscr',0x0)
           ),
           'tests': (
               ('f0', 0x0),
               ('cr1', 0b0000),
               ('fpscr',0x20000)
           ),
       },
       {
           'setup': (
                ('f0', 0),
                ('f1', 0x3FF0000000000000), 
                ('f2', 0xC00199999999999A), # -2.2
                ('cr1',0b0000),
                ('fpscr',0x0)
           ),
           'tests': (
               ('f0', 0xc001999980000000),
               ('cr1', 0b0000),
               ('fpscr',0x80000)
           ),
       },
       {
           'setup': (
                ('f0', 0),
                ('f1', 0x4000000000000000), # 2
                ('f2', 0xC00199999999999A), # -2.2
                ('cr1',0b0000),
                ('fpscr',0x0)
           ),
           'tests': (
               ('f0', 0xc011999980000000), # -4.4
               ('cr1', 0b0000),
               ('fpscr',0x80000)
           ),
       },
       
    ],  # fmuls. f0,f1,f2,f3

    'fc000891': [ # fmr. f0,f1
        {
            'setup': (
                ('f0', 42),
                ('f1', 64),
                ('cr1',0b0000)
            ),
            'tests': (
                ('f0', 64),
                ('cr1', 0b0000),
            ),
        },
        {
            'setup': (
                ('f0', 1),
                ('f1', 0x400199999999999A),
                ('cr1',0b0000),
                ('fpscr', 0x80000000)
            ),
            'tests': (
                ('f0', 0x400199999999999A),
                ('cr1', 0b1000),
            ),
        },
    ],  # 

    'fc000911': [ # fnabs. f0,f1
        {
            'setup': (
                ('f0', 0x4883),
                ('f1', 0x4050000000000000),
                ('cr1',0b0000),
                ('fpscr', 0x0)
            ),
            'tests': (
                ('f0', 0xc050000000000000),
                ('cr1', 0b0),
                ('fpscr', 0x80000)
            ),
        },
        {
            'setup': (
                ('f0', 1),
                ('f1', 0xC00199999999999A), # -2.2
                ('cr1',0b0000),
                ('fpscr', 0x0)
            ),
            'tests': (
                ('f0', 0xC00199999999999A),
                ('cr1', 0b0000),
                ('fpscr', 0x80000)
            ),
        },
    ],  # 

    'fc000851': [ # fneg. f0,f1
        {
            'setup': (
                ('f0', 0x4883),
                ('f1', 0x4050000000000000),
                ('cr1',0b0000),
                ('fpscr',0x0)
            ),
            'tests': (
                ('f0', 0xc050000000000000),
                ('cr1', 0b0),
                ('fpscr', 0x80000)
            ),
        },
        {
            'setup': (
                ('f0', 1),
                ('f1', 0xC00199999999999A), # -2.2
                ('cr1',0b0000),
                ('fpscr', 0x0)
            ),
            'tests': (
                ('f0', 0x400199999999999A),
                ('cr1', 0b0000),
                ('fpscr', 0x40000)
            ),
        },
    ],  # fneg. f0,f1

    'fc0118bf': [ # fnmadd. f0,f1, f2, f3
        {
            'setup': (
                ('f0', 0x4883),
                ('f1', 0x400A666666666666),
                ('f2', 0x3FF199999999999A),
                ('f3', 0x400199999999999A),
                ('cr1',0b0000),
                ('fpscr',0x0)
            ),
            'tests': (
                ('f0', 0xc01751eb851eb852),
                ('cr1', 0b0),
                ('fpscr', 0x80000)
            ),
        },
        {
            'setup': (
                ('f0', 0x4883),
                ('f1', 0xc00A666666666666),
                ('f2', 0x3FF199999999999A),
                ('f3', 0x400199999999999A),
                ('cr1',0b0000),
                ('fpscr',0x0)
            ),
            'tests': (
                ('f0', 0x3FF6E147AE147AE0),
                ('cr1', 0b0),
                ('fpscr', 0x40000)
            ),
        },
    ],  # fnmadd. f0,f1, f2, f3

    'ec0118bf': [ # fnmadds. f0,f1, f2, f3
        {
            'setup': (
                ('f0', 0x4883),
                ('f1', 0x400A666666666666),
                ('f2', 0x3FF199999999999A),
                ('f3', 0x400199999999999A),
                ('cr1',0b0000),
                ('fpscr',0x0)
            ),
            'tests': (
                ('f0', 0xc01751eb80000000),
                ('cr1', 0b0),
                ('fpscr', 0x80000)
            ),
        },
        {
            'setup': (
                ('f0', 0x4883),
                ('f1', 0xc00A666666666666),
                ('f2', 0x3FF199999999999A),
                ('f3', 0x400199999999999A),
                ('cr1',0b0000),
                ('fpscr',0x0)
            ),
            'tests': (
                ('f0', 0x3ff6e147a0000000),
                ('cr1', 0b0),
                ('fpscr', 0x40000)
            ),
        },
    ],  # fnmadds. f0,f1, f2, f3

    'fc0118bd': [ # fnmsub. f0,f1, f2, f3
        {
            'setup': (
                ('f0', 0x4883),
                ('f1', 0x400A666666666666), # 3.3
                ('f2', 0x3FF199999999999A), # 1.1
                ('f3', 0x400199999999999A), # 2.2
                ('cr1',0b0000),
                ('fpscr',0x0)
            ),
            'tests': (
                ('f0', 0xbff6e147ae147ae0),
                ('cr1', 0b0),
                ('fpscr', 0x80000)
            ),
        },
        {
            'setup': (
                ('f0', 0x4883),
                ('f1', 0xc00A666666666666), # -3.3
                ('f2', 0x3FF199999999999A), # 1.1
                ('f3', 0x400199999999999A), # 2.2
                ('cr1',0b0000),
                ('fpscr',0x0)
            ),
            'tests': (
                ('f0', 0x401751eb851eb852),
                ('cr1', 0b0),
                ('fpscr', 0x40000)
            ),
        },
    ],  # fnmsub. f0,f1, f2, f3

    'ec0118bd': [ # fnmsubs. f0,f1, f2, f3
        {
            'setup': (
                ('f0', 0x4883),
                ('f1', 0x400A666666666666), # 3.3
                ('f2', 0x3FF199999999999A), # 1.1
                ('f3', 0x400199999999999A), # 2.2
                ('cr1',0b0000),
                ('fpscr',0x0)
            ),
            'tests': (
                ('f0', 0xbff6e147a0000000),
                ('cr1', 0b0),
                ('fpscr', 0x80000)
            ),
        },
        {
            'setup': (
                ('f0', 0x4883),
                ('f1', 0xc00A666666666666), # -3.3
                ('f2', 0x3FF199999999999A), # 1.1
                ('f3', 0x400199999999999A), # 2.2
                ('cr1',0b0000),
                ('fpscr',0x0)
            ),
            'tests': (
                ('f0', 0x401751eb80000000),
                ('cr1', 0b0),
                ('fpscr', 0x40000)
            ),
        },
    ],  # fnmsubs. f0,f1, f2, f3

    '7C002214': [
        {
            'setup': (
                ('r0', 42),
                ('r4', 31337),
            ),
            'tests': (
                ('r0', 42 + 31337),
                ('r4', 31337),
            ),
        }
    ],  # 'add r0,r0,r4' 

    '7C005214': [
        {
            'setup': (
                ('r0', 69),
                ('r10', 420),
                ('cr0', 0),
            ),
            'tests': (
                ('r0', 69 + 420),
                ('r10', 420),
                ('cr0', 0),
            ),
        }
    ],  # 'add r0,r0,r10' GOOD TEST

    '7C634A15': [
        {
            'setup': (
                ('r3', 1337),
                ('r9', 7331),
                ('cr0', 0),
            ),
            'tests': (
                ('r3', 1337 + 7331),
                ('r9', 7331),
                ('cr0', 4),
            ),
        },
    ],  # 'add. r3,r3,r9' GOOD TEST

    '7C002814': [
        {
            'setup': (
                ('r0', 1234),
                ('r5', 4321),
            ),
            'tests': (
                ('r0', 1234 + 4321),
                ('r5', 4321),
            ),
        }
    ],  # 'addc r0,r0,r5' GOOD TEST

    '3000FFFF': [
        {
            'setup': (
                ('r0', 0),
                ('CA', 0),
            ),
            'tests': (
                ('r0', 0xffffffffffffffff),
                ('CA', 1),
            ),
            # GOOD TEST BUT IS 64bit.  32bit r0 == 0xffffffff
        },
        {
            'setup': (
                ('r0', 1337),
                ('CA', 0),
            ),
            'tests': (
                ('r0', 1336),
                ('CA', 0),
            ),
        }

    ],  # 'addic r0,r0,-0x1' GOOD TEST,  2 SETUPS IN HERE.  ONE NEGATIVE AND ONE POSITIVE

    '7C005114': [
        {
            'setup': (
                ('r0', 10),
                ('r10', 11),
            ),
            'tests': (
                ('r0', 21),
                ('r10', 11),
            ),
        },
        {
            'setup': (
                ('r0', -50),
                ('r10', 60),
            ),
            'tests': (
                ('r0', 10),
                ('r10', 60),
            ),
        },
        {
            'setup': (
                ('r0', -60),
                ('r10', 50),
            ),
            'tests': (
                ('r0', 0xfffffffffffffff6),
                ('r10', 50),
            ),
        }

    ],  # adde r0,r0,r10' GOOD TEST, 3 SETUPS IN HERE

    '3801FFC0': [
        {
            'setup': (
                ('r0', 255),
                ('r1', 0),
            ),
            'tests': (
                ('r0', 0xffffffffffffffc0),
                ('r1', 0),
            ),
        }
    ],  # 'addi r0,r1,-0x40' GOOD TEST

    '38010100': [
        {
            'setup': (
                ('r0', 255),
                ('r1', 0),
            ),
            'tests': (
                ('r0', 0x100),
                ('r1', 0),
            ),
        },
        {
            'setup': (
                ('r0', 255),
                ('r1', 1),
            ),
            'tests': (
                ('r0', 0x101),
                ('r1', 1),
            ),
        }
    ],  # 'addi r0,r1,0x100' GOOD TEST, 2 SETUPS

    '3400FFFF': [

        {
            'setup': (
                ('r0', 0),
                ('CA', 0),
            ),
            'tests': (
                ('r0', 0xffffffffffffffff),
                ('CA', 1),
                ('cr0', 0b1000),
            ),
            #
        },
        {
            'setup': (
                ('r0', 1337),
                ('CA', 0),
            ),
            'tests': (
                ('r0', 1336),
                ('CA', 0),
                ('cr0', 0b0100),
            ),
        }
    ],  # 'addic. r0,r1,-0x1' GOOD TEST, 2 SETUPS

    '3C02FFFC': [
        {
            'setup': (
                ('r0', 0),
                ('r2', 0x40000),
            ),
            'tests': (
                ('r0', 0),
                ('r2', 0x40000),
            ),
        },
        {
            'setup': (
                ('r0', 0),
                ('r2', 0x04000),
            ),
            'tests': (
                ('r0', 0xfffffffffffc4000),
            ),
        },
        {
            'setup': (
                ('r0', 0x50000),
                ('r2', 0x40000),
            ),
            'tests': (
                ('r0', 0),
                ('r2', 0x40000),

            ),
        }
    ],  # 'addis r0,r2,-0x4' GOOD TEST, 3 SETUPS

    '7C000194': [
        {
            'setup': (
                ('r0', 197),
                ('CA', 0),
            ),
            'tests': (
                ('r0', 197),
                ('CA', 0),
            ),
        }
    ],  # '7C000194', 'addze r0,r0

    '7c005838': [
        {
            'setup': (
                ('r0', 0b00001010),
                ('r11', 0b01011111),
            ),
            'tests': (
                ('r0', 0b00001010),
                ('r11', 0b01011111),
            ),
        }
    ],  # '7C000194', 'and r0,r0,r11'

    '7c00B039': [
        {
            'setup': (
                ('r0', 0b00001010),
                ('r22', 0b01011111),
                ('cr0', 0b0000),
            ),
            'tests': (
                ('r0', 0b00001010),
                ('r22', 0b01011111),
                ('cr0', 0b0100),
            ),
        }
    ],  # '7C000B039', 'and. r0,r0,r22'

    '7C003878': [
        {
            'setup': (
                ('r0', 0b00001010),
                ('r7', 0b01011111),  # r0 is ANDed with the One's complement of the value in this register (0b10100000)
                ('cr0', 0b0000),
            ),
            'tests': (
                ('r0', 0b00000000),
                ('r7', 0b01011111),
                ('cr0', 0b0000),
            ),
        },
        {
            'setup': (
                ('r0', 0b11111010),  # 0b11111010
                ('r7', 0b01011111),  # r0 is ANDed with the One's complement of the value in this register (0b10100000)
                ('cr0', 0b0000),
            ),
            'tests': (
                ('r0', 0b10100000),
                ('r7', 0b01011111),
                ('cr0', 0b0000),
            ),
        },
        {
            'setup': (
                ('r0', 0b11111010),  # 0b11111010
                ('r7', 0b0),  # ANDed with the One's complement of the value in this register (0b11111111)
                ('cr0', 0b0000),
            ),
            'tests': (
                ('r0', 0b11111010),
                ('r7', 0b0),
                ('cr0', 0b0000),
            ),
        }
    ],  # 7C003878', 'andc r0,r0,r7

    '7EC0E079': [
        {
            'setup': (
                ('r0', 0b0),
                ('r22', 0b01011111),  # 0b01011111
                ('r28', 0b01000000),  # 0b10111111
                ('cr0', 0b0),
            ),
            'tests': (
                ('r0', 0b00011111),
                ('r22', 0b01011111),
                ('r28', 0b01000000),
                ('cr0', 0b0100),
            ),
        }
    ],  # '7EC0E079', 'andc. r0,r22,r28'

    '70000007': [
        {
            'setup': (
                ('r0', 0b10000),  # (ANDed with 0b0111
                ('cr0', 0b0),
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
    ],  # '7EC0E079', 'andi. r0,r0,0x7'

    '7780FFF8': [
        {
            'setup': (
                ('r28', 0b10001111110111101000),
                ('cr0', 0),
            ),
            'tests': (
                ('r0', 0b10000000000000000000),
                ('cr0', 0b0100),
            ),
        },
        {
            'setup': (
                ('r28', 0),
                ('cr0', 0),
            ),
            'tests': (
                ('r0', 0),
                ('cr0', 0b0010),
            ),
        }
    ],  # '7780FFF8', 'andis r0,r28,0xfff8'

    '4BFFFFF0': [
        {
            'setup': (
                ('pc', 0x10000534),
            ),
            'tests': (
                ('pc', 0x10000524),
            ),
        }
    ],  # '4BFFFFF0', 'b -0x10'

    '429F0005': [  # ('429F0005', 'bcl 0x4') actually
        {
            'setup': (
                ('pc', 0x10000534),
            ),
            'tests': (
                ('pc', 0x10000538),
            ),
        }
    ],  # ('429F0005', 'bcl 0x4')

    '7CAF5000': [  # L = 1
        {
            'setup': (
                ('r15', 55000),
                ('r10', 65000),
            ),
            'tests': (
                ('cr1', 0b1000),
            ),
        },
        {
            'setup': (
                ('r15', 65000),
                ('r10', 65000),
            ),
            'tests': (
                ('cr1', 0b0010),
            ),
        },
        {
            'setup': (
                ('r15', 55000),
                ('r10', 5000),
            ),
            'tests': (
                ('cr1', 0b0100),
            ),
        }
    ],  # '7CAF5000', 'cmpd cr1,r15,r10'

    '2CA00000': [
        {
            'setup': (
                ('r0', 55000),
            ),
            'tests': (
                ('cr1', 0b0100),
            ),
        },  # test#0
        {
            'setup': (
                ('r0', 0),
            ),
            'tests': (
                ('cr1', 0b0010),
            ),
        },  # test#1
        {
            'setup': (
                ('r0', -2),
            ),
            'tests': (
                ('cr1', 0b1000),
            ),
        }
    ],  # '2CA00000', 'cmpdi cr1,r0,0x0'

    '7CAA7840': [  # crfD = 0, L = 1
        {
            'setup': (
                ('r10', 55000),
                ('r15', 65000),
            ),
            'tests': (
                ('cr1', 0b1000),
            ),
        },
        {
            'setup': (
                ('r10', 65000),
                ('r15', 55000),
            ),
            'tests': (
                ('cr1', 0b0100),
            ),
        },
        {
            'setup': (
                ('r10', 65000),
                ('r15', 65000),
            ),
            'tests': (
                ('cr1', 0b0010),
            ),
        },
    ],  # '7CAA7840', 'cmpld 0,1,r10,r15

    '28AF0008': [  # cr1 = 0, L = 1
        {
            'setup': (
                ('r15', 65000),
            ),
            'tests': (
                ('cr1', 0b0100),
            ),
        },
        {
            'setup': (
                ('r15', 7),
            ),
            'tests': (
                ('cr1', 0b1000),
            ),
        },
        {
            'setup': (
                ('r15', 8),
            ),
            'tests': (
                ('cr1', 0b0010),
            ),
        },
    ],  # '28AF0008', 'cmpldi cr1,r15,0x8'

    '7C8A3840': [  # cmplw cr1,r10,r7 (cmp crD,0,rA,rB)
        {
            'setup': (
                ('r10', 10),
                ('r7', 9),
                ('cr1', 0)
            ),
            'tests': (
                ('cr1', 0b0100),
            ),
        },
        {
            'setup': (
                ('r10', 10),
                ('r7', 10),
                ('cr1', 0)
            ),
            'tests': (
                ('cr1', 0b0010),
            ),
        },
        {
            'setup': (
                ('r10', 8),
                ('r7', 10),
                ('cr1', 0)
            ),
            'tests': (
                ('cr1', 0b1000),
            ),
        },
    ],  # '7C8A3840', 'cmplw cr1,r10,r7' (cmp crD,0,rA,rB)

    '288A0002': [  # cmpli crD,0,rA,UIMM
        {
            'setup': (
                ('r10', 10),
            ),
            'tests': (
                ('cr1', 0b0100
                 ),
            ),
        },
        {
            'setup': (
                ('r10', 1),
            ),
            'tests': (
                ('cr1', 0b1000),
            ),
        },
        {
            'setup': (
                ('r10', 2),
            ),
            'tests': (
                ('cr1', 0b0010),
            ),
        },
    ],  # '288A0002', 'cmplwi cr1,r10,0x2' (cmp crD,0,rA,rB)

    '7C90D000': [  # (cmp crD,0,rA,rB)
        {
            'setup': (
                ('r16', 10),
                ('r26', 1),
            ),
            'tests': (
                ('cr1', 0b0100),
            ),
        },
        {
            'setup': (
                ('r16', 1),
                ('r26', 1),
            ),
            'tests': (
                ('cr1', 0b0010),
            ),
        },
        {
            'setup': (
                ('r16', 0),
                ('r26', 2),
            ),
            'tests': (
                ('cr1', 0b1000),
            ),
        },
    ],  # '7C90D000', 'cmpw cr1,r16,r26'

    '2C800000': [  # cmp crD,0,rA,rB
        {
            'setup': (
                ('r0', 10),
            ),
            'tests': (
                ('cr1', 0b0100),
            ),
        },
        {
            'setup': (
                ('r0', 0),
            ),
            'tests': (
                ('cr1', 0b0010),
            ),
        },
        {
            'setup': (
                ('r0', -10),
            ),
            'tests': (
                ('cr1', 0b1000),
            ),
        },
    ],  # '2C800000', 'cmpwi cr1,r0,0x0'

    '7C000074': [
        {
            'setup': (
                ('r0', 0b000001),
                ('cr0', 0b0000)
            ),
            'tests': (
                ('r0', 0b111111),
                ('cr0', 0b0000),
            ),
        },
        {
            'setup': (
                ('r0', 0b0000011),
            ),
            'tests': (
                ('r0', 0b111110),
                ('cr0', 0b0000),
            ),
        },
    ],  # '7C000074', 'cntlzd r0,r0

    '7C000075': [
        {
            'setup': (
                ('r0', 0b000001),
                ('cr0', 0b0000)
            ),
            'tests': (
                ('r0', 0b111111),
                ('cr0', 0b0100),
            ),
        },
        {
            'setup': (
                ('r0', 0b0000011),
            ),
            'tests': (
                ('r0', 0b111110),
                ('cr0', 0b0100),
            ),
        },
    ],  # '7C000075', 'cntlzd. r0,r0


    '7C0C03D2': [
    {
            'setup': (
                ('r0', 9),
                ('r12', 54),
            ),
            'tests': (
                ('r0', 6),
            ),
        },

        {
            'setup': (
                ('r0', -9),
                ('r12', 54),
            ),
            'tests': (
                ('r0', 0xfffffffffffffffa),
            ),
        },

        {
            'setup': (
                ('r0', 0),
                ('r12', 54),
            ),
            'tests': (
                ('r0', 0x0),
            ),
        },

        {
            'setup': (
                ('r0', 1),
                ('r12', 54),
            ),
            'tests': (
                ('r0', 54),
            ),
        },

        {
            'setup': (
                ('r0', -1),
                ('r12', 54)
            ),
            'tests': (
                ('r0', 0xffffffffffffffca),
            ),
        },
    ],  # 'divd r0,r12,r0'

    '7C0C03D3': [
    {
            'setup': (
                ('r0', 9),
                ('r12', 54),
            ),
            'tests': (
                ('r0', 6),
                ('cr0', 0b0100)
            ),
        },

        {
            'setup': (
                ('r0', -9),
                ('r12', 54),
            ),
            'tests': (
                ('r0', 0xfffffffffffffffa),
                ('cr0', 0b1000)
            ),
        },

        {
            'setup': (
                ('r0', 0),
                ('r12', 54),
            ),
            'tests': (
                ('r0', 0),
                ('cr0', 0b010)
            ),
        },

        {
            'setup': (
                ('r0', 1),
                ('r12', 54),
            ),
            'tests': (
                ('r0', 54),
                ('cr0', 0b0100)
            ),
        },

        {
            'setup': (
                ('r0', -1),
                ('r12', 54)
            ),
            'tests': (
                ('r0', 0xffffffffffffffca),
                ('cr0', 0b1000)
            ),
        },

        {
            'setup': (
                ('r0', -1),
                ('r12', -1)
            ),
            'tests': (
                ('r0', 1),
                ('cr0', 0b0100)
            ),
        },
    ],  # 'divd. r0,r12,r0'

    '7c0c07d2': [
        {
            'setup': (
                ('r0', 9),
                ('r12', 54),
            ),
            'tests': (
                ('r0', 6),
                ('XER', 0)
            ),
        },

        {
            'setup': (
                ('r0', -9),
                ('r12', 54),
            ),
            'tests': (
                ('r0', 0xfffffffffffffffa),
                ('XER', 0)
            ),
        },

        {
            'setup': (
                ('r0', 0),
                ('r12', 54),
            ),
            'tests': (
                ('r0', 0x0),
                ('XER', 0xc0000000)
            ),
        },

        {
            'setup': (
                ('r0', 1),
                ('r12', 54),
            ),
            'tests': (
                ('r0', 54),
                ('XER', 0)
            ),
        },

        {
            'setup': (
                ('r0', -1),
                ('r12', 54)
            ),
            'tests': (
                ('r0', 0xffffffffffffffca),
                ('XER', 0)
            ),
        },
    ],  # 'divdo r0,r12,r0'

    '7c0c07d3': [
        {
            'setup': (
                ('r0', 9),
                ('r12', 57),  # Remainder will not be supplied
                ('XER', 0),
                ('cr0', 0b0000)

            ),
            'tests': (
                ('r0', 6),
                ('XER', 0),
                ('cr0', 0b0100)
            ),
        },

        {
            'setup': (
                ('r0', -9),
                ('r12', 54),
                ('cr0', 0b0000),
                ('XER', 0)

            ),
            'tests': (
                ('r0', 0xfffffffffffffffa),
                ('XER', 0),
                ('cr0', 0b1000)
            ),
        },

        {
            'setup': (
                ('r0', 0),
                ('r12', 54),
                ('cr0', 0b0000),
                ('XER', 0)

            ),
            'tests': (
                ('r0', 0x0),
                ('XER', 0xc0000000),
                ('cr0', 0b0011)
            ),
        },

        {
            'setup': (
                ('r0', 1),
                ('r12', 54),
                ('cr0', 0b0000),
                ('XER', 0)

            ),
            'tests': (
                ('r0', 54),
                ('XER', 0),
                ('cr0', 0b0100)
            ),
        },

        {
            'setup': (
                ('r0', -1),
                ('r12', 54),
                ('cr0', 0b0000)

            ),
            'tests': (
                ('r0', 0xffffffffffffffca),
                ('XER', 0),
                ('cr0', 0b1000)
            ),
        },
    ],  # 'divdo. r0,r12,r0'


    '7D0A5238': [
        {
            'setup': (
                ('r10', 10),
                ('r8', 10),
            ),
            'tests': (
                ('r10', 0xffffffffffffffff),
            ),
        },
        {
                'setup': (
                    ('r10', 1),
                    ('r8', 10),
                ),
                'tests': (
                    ('r10', 0xfffffffffffffff4),
                ),
        },
        {
                'setup': (
                    ('r10', 10),
                    ('r8', 1),
                ),
                'tests': (
                    ('r10', 0xfffffffffffffff4),
                ),
        },


    ],  # '7D0A5238', 'eqv. r10,r8,r10'




    # '7D0A5239': [
    #     {
    #         'setup': (
    #             ('r10', 10),
    #             ('r8', 10),
    #         ),
    #         'tests': (
    #             ('r10', 0xffffffffffffffff),
    #             ('cr0', 0b1000)
    #         ),
    #     },
    #     {
    #             'setup': (
    #                 ('r10', 10),
    #                 ('r8', 1),
    #             ),
    #             'tests': (
    #                 ('r10', 0xfffffffffffffff4),
    #                 ('cr0', 0b1000)
    #             ),
    #     },
    #     {
    #             'setup': (
    #                 ('r10', 1),
    #                 ('r8', 10),
    #             ),
    #             'tests': (
    #                 ('r10', 0xfffffffffffffff4),
    #                 ('cr0', 0b1000)
    #             ),
    #     }
    #
    #     ], # '7D0A5238', 'eqv. r10,r8,r10'

    # For the following condition register tests:
    # - the third bit is the one being operated on
    # - the result goes into the third bit of cr0
    # - cr6 is checked to make sure it doesn't change
    '4C42D202': [  # ('4C42D202', 'crand eq,eq,cr6.eq')
       {
           'setup': (
               ('cr0', 0b1111),
               ('cr6', 0b1101),
           ),
           'tests': (
               ('cr0', 0b1101),
               ('cr6', 0b1101),
           ),
       },
       {
           'setup': (
               ('cr0', 0b1010),
               ('cr6', 0b0010),
           ),
           'tests': (
               ('cr0', 0b1010),
               ('cr6', 0b0010),
           ),
       },
       {
           'setup': (
               ('cr0', 0b1101),
               ('cr6', 0b1010),
           ),
           'tests': (
               ('cr0', 0b1101),
               ('cr6', 0b1010),
           ),
       },
       {
           'setup': (
               ('cr0', 0b1101),
               ('cr6', 0b1101),
           ),
           'tests': (
               ('cr0', 0b1101),
               ('cr6', 0b1101),
           ),
       },
    ],  # ('4C42D202', 'crand eq,eq,cr6.eq') crbD,crbA,crbB

    '4C42D102': [  # ('4C42D102', 'crandc eq,eq,cr6.eq')
       {
           'setup': (
               ('cr0', 0b1111),
               ('cr6', 0b1101),
           ),
           'tests': (
               ('cr0', 0b1111),
               ('cr6', 0b1101),
           ),
       },
       {
           'setup': (
               ('cr0', 0b1010),
               ('cr6', 0b0010),
           ),
           'tests': (
               ('cr0', 0b1000),
               ('cr6', 0b0010),
           ),
       },
       {
           'setup': (
               ('cr0', 0b1101),
               ('cr6', 0b1010),
           ),
           'tests': (
               ('cr0', 0b1101),
               ('cr6', 0b1010),
           ),
       },
       {
           'setup': (
               ('cr0', 0b1101),
               ('cr6', 0b1101),
           ),
           'tests': (
               ('cr0', 0b1101),
               ('cr6', 0b1101),
           ),
       },
    ],  # ('4C42D102', 'crandc eq,eq,cr6.eq') crbD,crbA,crbB

    '4C42D242': [  # ('4C42D242', 'creqv eq,eq,cr6.eq')
       {
           'setup': (
               ('cr0', 0b1111),
               ('cr6', 0b1101),
           ),
           'tests': (
               ('cr0', 0b1101),
               ('cr6', 0b1101),
           ),
       },
       {
           'setup': (
               ('cr0', 0b1010),
               ('cr6', 0b0010),
           ),
           'tests': (
               ('cr0', 0b1010),
               ('cr6', 0b0010),
           ),
       },
       {
           'setup': (
               ('cr0', 0b1101),
               ('cr6', 0b1010),
           ),
           'tests': (
               ('cr0', 0b1101),
               ('cr6', 0b1010),
           ),
       },
       {
           'setup': (
               ('cr0', 0b1101),
               ('cr6', 0b1101),
           ),
           'tests': (
               ('cr0', 0b1111),
               ('cr6', 0b1101),
           ),
       },
    ],  # ('4C42D242', 'creqv eq,eq,cr6.eq') crbD,crbA,crbB

    '4C42D1C2': [  # ('4C42D1C2', 'crnand eq,eq,cr6.eq')
       {
           'setup': (
               ('cr0', 0b1111),
               ('cr6', 0b1101),
           ),
           'tests': (
               ('cr0', 0b1111),
               ('cr6', 0b1101),
           ),
       },
       {
           'setup': (
               ('cr0', 0b1010),
               ('cr6', 0b0010),
           ),
           'tests': (
               ('cr0', 0b1000),
               ('cr6', 0b0010),
           ),
       },
       {
           'setup': (
               ('cr0', 0b1101),
               ('cr6', 0b1010),
           ),
           'tests': (
               ('cr0', 0b1111),
               ('cr6', 0b1010),
           ),
       },
       {
           'setup': (
               ('cr0', 0b1101),
               ('cr6', 0b1101),
           ),
           'tests': (
               ('cr0', 0b1111),
               ('cr6', 0b1101),
           ),
       },
    ],  # ('4C42D1C2', 'crnand eq,eq,cr6.eq') crbD,crbA,crbB

    '4C42D042': [  # ('4C42D042', 'crnor eq,eq,cr6.eq')
       {
           'setup': (
               ('cr0', 0b1111),
               ('cr6', 0b1101),
           ),
           'tests': (
               ('cr0', 0b1101),
               ('cr6', 0b1101),
           ),
       },
       {
           'setup': (
               ('cr0', 0b1010),
               ('cr6', 0b0010),
           ),
           'tests': (
               ('cr0', 0b1000),
               ('cr6', 0b0010),
           ),
       },
       {
           'setup': (
               ('cr0', 0b1101),
               ('cr6', 0b1010),
           ),
           'tests': (
               ('cr0', 0b1101),
               ('cr6', 0b1010),
           ),
       },
       {
           'setup': (
               ('cr0', 0b1101),
               ('cr6', 0b1101),
           ),
           'tests': (
               ('cr0', 0b1111),
               ('cr6', 0b1101),
           ),
       },
    ],  # ('4C42D042', 'crnor eq,eq,cr6.eq') crbD,crbA,crbB

    '4C42D382': [  # ('4C42D382', 'cror eq,eq,cr6.eq')
       {
           'setup': (
               ('cr0', 0b1111),
               ('cr6', 0b1101),
           ),
           'tests': (
               ('cr0', 0b1111),
               ('cr6', 0b1101),
           ),
       },
       {
           'setup': (
               ('cr0', 0b1010),
               ('cr6', 0b0010),
           ),
           'tests': (
               ('cr0', 0b1010),
               ('cr6', 0b0010),
           ),
       },
       {
           'setup': (
               ('cr0', 0b1101),
               ('cr6', 0b1010),
           ),
           'tests': (
               ('cr0', 0b1111),
               ('cr6', 0b1010),
           ),
       },
       {
           'setup': (
               ('cr0', 0b1101),
               ('cr6', 0b1101),
           ),
           'tests': (
               ('cr0', 0b1101),
               ('cr6', 0b1101),
           ),
       },
    ],  # ('4C42D382', 'cror eq,eq,cr6.eq') crbD,crbA,crbB

    '4C42D342': [  # ('4C42D342', 'crorc eq,eq,cr6.eq')
       {
           'setup': (
               ('cr0', 0b1111),
               ('cr6', 0b1101),
           ),
           'tests': (
               ('cr0', 0b1111),
               ('cr6', 0b1101),
           ),
       },
       {
           'setup': (
               ('cr0', 0b1010),
               ('cr6', 0b0010),
           ),
           'tests': (
               ('cr0', 0b1010),
               ('cr6', 0b0010),
           ),
       },
       {
           'setup': (
               ('cr0', 0b1101),
               ('cr6', 0b1010),
           ),
           'tests': (
               ('cr0', 0b1101),
               ('cr6', 0b1010),
           ),
       },
       {
           'setup': (
               ('cr0', 0b1101),
               ('cr6', 0b1101),
           ),
           'tests': (
               ('cr0', 0b1111),
               ('cr6', 0b1101),
           ),
       },
    ],  # ('4C42D342', 'crorc eq,eq,cr6.eq') crbD,crbA,crbB

    '4C42D182': [  # ('4C42D182', 'crxor eq,eq,cr6.eq')
       {
           'setup': (
               ('cr0', 0b1111),
               ('cr6', 0b1101),
           ),
           'tests': (
               ('cr0', 0b1111),
               ('cr6', 0b1101),
           ),
       },
       {
           'setup': (
               ('cr0', 0b1010),
               ('cr6', 0b0010),
           ),
           'tests': (
               ('cr0', 0b1000),
               ('cr6', 0b0010),
           ),
       },
       {
           'setup': (
               ('cr0', 0b1101),
               ('cr6', 0b1010),
           ),
           'tests': (
               ('cr0', 0b1111),
               ('cr6', 0b1010),
           ),
       },
       {
           'setup': (
               ('cr0', 0b1101),
               ('cr6', 0b1101),
           ),
           'tests': (
               ('cr0', 0b1101),
               ('cr6', 0b1101),
           ),
       },
    ],  # ('4C42D182', 'crxor eq,eq,cr6.eq') crbD,crbA,crbB

    '7D4A0775': [  # ('7D4A0775', 'extsb. r10,r10') - Not working
        {
            'setup': (
                ('r10', 0x12345880),
                ('cr0', 0b0000)
            ),
            'tests': (
                ('r10', 0xffffffffffffff80),
                ('cr0', 0b1000)
            ),
        },
        {
            'setup': (
                ('r10', 0xffffff70),
                ('cr0', 0b0000)
            ),
            'tests': (
                ('r10', 0x70),
                ('cr0', 0b0100)
            ),
        },
        {
            'setup': (
                ('r10', 0x12345670),
                ('cr0', 0b0000)
            ),
            'tests': (
                ('r10', 0x70),
                ('cr0', 0b0100)
            ),
        },
        {
            'setup': (
                ('r10', 0x80),
                ('cr0', 0b0000)
            ),
            'tests': (
                ('r10', 0xffffffffffffff80),
                ('cr0', 0b1000)
            ),
        },
        {
            'setup': (
                ('r10', 0x0),
                ('cr0', 0b0000)
            ),
            'tests': (
                ('r10', 0x0),
                ('cr0', 0b0010)
            ),
        },
    ],

    '7D4A0735': [  # ('7D4A0735', 'extsh. r10,r10')
        {
            'setup': (
                ('r10', 0x8800),
                ('cr0', 0b0000)
            ),
            'tests': (
                ('r10', 0xffffffffffff8800),
                ('cr0', 0b1000)
            ),
        },
        {
            'setup': (
                ('r10', 0x87800),
                ('cr0', 0b0000)
            ),
            'tests': (
                ('r10', 0x7800),
                ('cr0', 0b0100)
            ),
        },        {
            'setup': (
                ('r10', 0x12348800),
                ('cr0', 0b0000)
            ),
            'tests': (
                ('r10', 0xffffffffffff8800),
                ('cr0', 0b1000)
            ),
        },
        {
            'setup': (
                ('r10', 0x0),
                ('cr0', 0b0000)
            ),
            'tests': (
                ('r10', 0x0),
                ('cr0', 0b0010)
            ),
        },        
    ],  #  ('7D4A0735', 'extsh. r10,r10')

    '7c01ffb5': [  # ('7D4A0735', 'extsw. r1,r0')
        {
            'setup': (
                ('r0', 0x80008800),
                ('cr0', 0b0000)
            ),
            'tests': (
                ('r1', 0xffffffff80008800),
                ('cr0', 0b1000)
            ),
        },
        {
            'setup': (
                ('r0', 0xffff70087800),
                ('cr0', 0b0000)
            ),
            'tests': (
                ('r1', 0x70087800),
                ('cr0', 0b0100)
            ),
        },        {
            'setup': (
                ('r0', 0xf12348800),
                ('cr0', 0b0000)
            ),
            'tests': (
                ('r1', 0x12348800),
                ('cr0', 0b0100)
            ),
        },
        {
            'setup': (
                ('r0', 0x0),
                ('cr0', 0b0000)
            ),
            'tests': (
                ('r1', 0x0),
                ('cr0', 0b0010)
            ),
        },
        
    ],  #  ('7c01ffb5', 'extsw. r10,r10')


    # 'FC00002A': [  # ('FC00002A', 'fadd f0,f0,f0')
    #     {
    #         'setup': (
    #             ('f0', 0x4036c923a29c779a),  # IEEE754 double 22.785699999999999
    #         ),
    #         'tests': (
    #             ('f0', 0x4046c923a29c779a),  # IEEE754 double 45.571399999999997
    #         ),
    #     }
    # ],  # ('FC00002A', 'fadd f0,f0,f0')

    # Both 7C1E071E and 7C1E071F are  tested for isel because the last bit is
    # a "don't care" bit, and we want to make sure both states are tested.

    '7C1E071E': [  # ('7C1E071E', 'isel r0,r30,r0,cr7.lt')
        {
            'setup': (
                ('r0', 0xff),
                ('r30', 0x1234),
                ('cr7', 0b1000),

            ),

            'tests': (
                ('r0', 0x1234),
                ('r30', 0x1234),
                ('cr7', 0b1000),

            ),
        },

        {
            'setup': (
                ('r0', 64),
                ('r30', 0),
                ('cr7', 0b1000),

            ),

            'tests': (
                ('r0', 0),
                ('r30', 0),
                ('cr7', 0b1000),

            ),
        },

        {
            'setup': (
                ('r0', 64),
                ('r30', 55),
                ('cr7', 0b0000),

            ),

            'tests': (
                ('r0', 64),
                ('r30', 55),
                ('cr7', 0b0000),

            ),
        },

    ],  # ('7C1E071E', 'isel r0,r30,r0,cr7.lt')

    '7C1E071F': [  # ('7C1E071F', 'isel r0,r30,r0,cr7.lt')
        {
            'setup': (
                ('r0', 0xff),
                ('r30', 0x1234),
                ('cr7', 0b1000),

            ),

            'tests': (
                ('r0', 0x1234),
                ('r30', 0x1234),
                ('cr7', 0b1000),

            ),
        },

        {
            'setup': (
                ('r0', 64),
                ('r30', 0),
                ('cr7', 0b1000),

            ),

            'tests': (
                ('r0', 0),
                ('r30', 0),
                ('cr7', 0b1000),

            ),
        },

        {
            'setup': (
                ('r0', 64),
                ('r30', 55),
                ('cr7', 0b0000),

            ),

            'tests': (
                ('r0', 64),
                ('r30', 55),
                ('cr7', 0b0000),

            ),
        },

    ],  # ('7C1E071F', 'isel r0,r30,r0,cr7.lt')

    '880A0000': [  # ('880A0000', 'lbz r0,0x0(r10)')
        {
            'setup': (
                                # Set the register to be filled with some generic data
                        ('r0', 0x0102030405060708),
                                # Fill memory with an 8-byte pattern
                        (0x000000f8, bytes.fromhex('F1F2F3F4F5F6F7F8')),
                                # Set the address to be the last byte of the pattern
                        ('r10', 0x00000000000000FF),
            ),
            'tests': (
                ('r0', 0xF8),
            ),
        }
    ],  # ('880A0000', 'lbz r0,0x0(r10)')

    'A00A0000': [  # lhz r0,0x0(r10)
        {
            'setup': (
                # Set the register to be filled with some generic data
                ('r0', 0x0102030405060708),
                # Fill memory with an 8-byte pattern
                (0x000000f8, bytes.fromhex('F1F2F3F4F5F6F7F8')),
                # Set the address to be the last byte of the pattern
                ('r10', 0x00000000000000FE),
            ),
            'tests': (
                ('r0', 0xF7F8),
            ),
        }
    ],

    '6D29FF00': [  # ('6D29FF00', 'xoris r9,r9,)
        {
            'setup': (
                ('r9', 0b00110011),
            ),
            'tests': (
                ('r9', 0b11111111000000000000000000110011),

            ),
        }
    ],  # ('6D29FF00', 'xoris r9,r9,0xff00')

    '6929FFFF': [  # ('6929FFFF', 'xori r9,r9,0xffff)
        {
            'setup': (
                ('r9', 0b0000000000110011),
                #         1111111111111111
            ),
            'tests': (
                ('r9', 0b1111111111001100),

            ),
        }
    ],  # ('6929FFFF', 'xori r9,r9,0xffff)
#
    # '7D484279': [  # ('7D484279', 'xor. r8,r10,r8')
    #     {
    #         'setup': (
    #             ('r8', 0b0000000000110011),
    #             ('r10', 0b0000000000001011),
    #         ),
    #         'tests': (
    #             ('r8', 0b00111000),
    #             ('cr0', 0b0100),
    #         ),
    #     }
    # ],  # ('7D484279', 'xor. r8,r10,r8')

    '7D294278': [  # ('7D294278', 'xor r9,r9,r8')
        {
            'setup': (
                ('r9', 0b0000000000110011),
                ('r8', 0b0000000000001011),
            ),
            'tests': (
                ('r9', 0b00111000),
            ),
        }
    ],  # ('7D294278', 'xor r9,r9,r8')

    '38000011': [  # ('38000011', 'li r0,0x11')
        {
            'setup': (
                ('r0', 0x4),
            ),
            'tests': (
                ('r0', 0x11),
            ),
        }
    ],  # ('38000011', 'li r0,0x11')

    '3800FFFF': [  # ('3800FFFF', 'li r0,-0x1')
        {
            'setup': (
                ('r0', 0x4),
            ),
            'tests': (
                ('r0', 0xffffffffffffffff),
            ),
        }
    ],  # ('38000011', 'li r0,0x11')


    # 'FC00069C': [  # ('FC00069C', 'fcfid f0,f0') Unsupported
    #    {
    #        'setup': (
    #            ('f0', 0x428ad70a),
    #        ),
    #        'tests': (
    #            ('f0', 0x41d0a2b5c2800000),
    #        ),
    #    }
    # ],  # ('FC00069C', 'fcfid f0,f0')

    '8004FFF0': [ # ('8004FFF0', 'lwz r0,-0x10(r4)')
        {
            'setup': (
                        # Set the register to be filled with some generic data
                ('r0', 0x0102030405060708),
                        # Fill memory with an 8-byte pattern
                (0x000000f8, bytes.fromhex('F1F2F3F4F5F6F7F8')),
                        # Set r4 be the last 4 bytes of the pattern (0xFC) + 16
                        # (so r4 - 0x10 == 0xF8)
                ('r4', 0xFC + 16),
            ),
            'tests': (
                ('r0', 0x00000000F5F6F7F8),
            ),
        }
    ],  # ('8004FFF0', 'lwz r0,-0x10(r4)')

    '8004FFF1': [  # ('8004FFF1', 'lwz r0,-0x11(r4)')
        {
            'setup': (
                        # Set the register to be filled with some generic data
                ('r0', 0x0102030405060708),
                        # Fill memory with an 8-byte pattern
                        # 0x00001050 is the starting address.
                        # F1F2F3F4 gets put in 0x1050 - 0x1053
                        # Ultimatly this range is 0x1050 - 0x1057
                (0x00001050, bytes.fromhex('F1F2F3F4F5F6F7F8')),
                        # Set r4 be the last 4 bytes of the pattern (0x1054) + 16
                        # (so r4 - 0x10 == 0xF8)
                ('r4', 0x1054 + 15), #0x10c
            ),
            'tests': (
                #Takes the values stored in the memory range 0x1054 - 0x1057 and put is in r0
                ('r0', 0x00000000F5F6F7F8),
                ('r4', 0x1054 + 15)
            ),
        }
    ],      # ('8004FFF1', 'lwz r0,-0x11(r4)')

    '7C0AF8EE': [ #('7C0AF8EE', 'lbzux r0,r10,r31')  #Aaron is fixing this
        {
            'setup': (
                ('r0', 0x7740),
                ('r10', 0x10010100),
                ('r31', 0x100),
                (0x10010100 + 0x100, bytes.fromhex('11223344'))
                    ),
    
            'tests':(
                ('r0',0x11),
                ('r10',0x10010200),
                ('r31', 0x100)
    
            ),
        }
    ],  # ('7C0AF8EE', 'lbzux r0,r10,r31')

    # '7C0C00AE': [ # ('7C0C00AE', 'lbzx r0,r12,r0')
    #     {
    #         'setup': (
    #             ('r0', 0x10010123),
    #             ('r12', 0x0),
    #             (0x10010123, bytes.fromhex('1020304050607080'))
    #                 ),
    #
    #         'tests':(
    #             ('r0', 0x1),
    #             ('r12', 0)
    #         ),
    #     }
    # ],  # ('7C0C00AE', 'lbzx r0,r12,r0')


    'E8010000': [ # ld r0,0x0(r21)
        {
            'setup': (
                ('r0', 0x0),
                ('r1', 0x10000400),
                (0x10000400, bytes.fromhex('AB9371D0FEDCBA98'))
            ),
            'tests':(
                ('r0', 0xAB9371D0FEDCBA98),
            ),
        }
    ],

    '7C0C00AE': [ # ('7C0C00AE', 'lbzx r0,r12,r0')
        {
            'setup': (
                ('r0', 0x000000f8),
                ('r12', 0x0),
                (0x000000f8, bytes.fromhex('f1f2f3f4f5f6f7f8'))
                    ),

            'tests':(
                ('r0', 0xf1),

            ),
        }
    ],  # ('7C0C00AE', 'lbzx r0,r12,r0')

    # '7C0007B5': [  # ('7C0007B4', 'extsw. r0,r0')
    #     {
    #         'setup': (
    #             ('r0', -2),
    #         ),
    #         'tests': (
    #             ('r0', 0xfffffffffffffffe),
    #             ('cr0', 0b1000)
    #         ),
    #     },
    #     {
    #         'setup': (
    #             ('r0', 0),
    #             ('r30', 64),
    #             ('cr7', 0b1000),

    #         ),
    #         'tests': (
    #             ('r0', 0x2),
    #             ('cr0', 0b0100)
    #         ),
    #     },
    # ],  # ('7C0007B4', 'extsw. r0,r0')

    'F81FFFF0': [  # ('F81FFFF0', 'std r0,-0x10(r31)')
        {
            'setup': (
                ('r0', 0x12345678),
                ('r31', 0x000000e8 + 0x10),
                (0x000000e8, bytes.fromhex('0000000000000000')),

            ),

            'tests': (
            (0x000000e8, bytes.fromhex('0000000012345678')),

            ),
        },

        {
            'setup': (
                ('r0', 0x0123456789abcdef),
                ('r31', 0x000000e8 + 0x10),
                (0x000000e8, bytes.fromhex('0000000000000000')),

            ),

            'tests': (
            (0x000000e8, bytes.fromhex('0123456789abcdef')),

            ),
        },
    ],  # ('F81FFFF0', 'std r0,-0x10(r31)')

    '981CFFFF':  # ('981CFFFF', 'stb r0,-0x1(r28)')
        [
            {
                'setup': (
                    ('r0', 0x12345678),
                    ('r28', 0x000000e8 + 0x1),
                    (0x000000e8, bytes.fromhex('0000000000000000'))

                ),

                'tests': (
                    (0x000000e8, bytes.fromhex('7800000000000000')),

                ),
            },
        ],

    'B0030000':  # ('('B0030000', 'sth r0,0x0(r3)')
        [
            {
                'setup': (
                    ('r0', 0x12345678),
                    ('r3', 0x000000e8),
                    (0x000000e8, bytes.fromhex('0000000000000000'))

                ),

                'tests': (
                    (0x000000e8, bytes.fromhex('5678000000000000')),

                ),
            },
        ],  #  ('B0030000', 'sth r0,0x0(r3))

    '900AFFEC':  # ('900AFFEC', 'stw r0,-0x14(r10)')
        [
            {
                'setup': (
                    ('r0', 0x12345678),
                    ('r10', 0x000000e8 + 0x14),
                    (0x000000e8, bytes.fromhex('0000000000000000'))

                ),

                'tests': (
                    (0x000000e8, bytes.fromhex('1234567800000000')),

                ),
            },
        ],  #  ('900AFFEC', 'stw r0,-0x14(r10)')

      '78001788': [  # ('78001788', 'rldic r0,r0,0x2,0x1e')
        {
            'setup': (
                ('r0', 0),
            ),
            'tests': (
                ('r0', 0x0),
            ),
        }
    ], # ('7C0007B4', 'extsw r0,r0')

    '3C00FFFF': [  # ('3C00FFFF', 'lis r0,-0x1' (equivalent to addis rD,0,value))
        {
            'setup': (
                ('r0', 0x4),
            ),
            'tests': (
                ('r0', 0xffffffffffff0000),
            ),
        }
    ],  # ('3C00FFFF', 'lis r0,-0x1' )

    # 'E8070122': [  # ('E8070122', 'lwa r0,0b100101001(r7)')
    #     {
    #         'setup': (
    #             ('r7', 0x10010100),
    #             ('r0', 0x0102030405060708)
    #         ),
    #         'tests': (
    #             ('r0', 0xb),
    #         ),
    #     }
    # ],  # ('E8070122', 'lwa r0,0x120(r7)')

    '8C04FFFF': [ #('8C04FFFF', 'lbzu r0,-0x1(r4)')
        {
            'setup': (
                ('r0', 0x0102030405060708),
                (0x000000f8, bytes.fromhex('F1F2F3F4F5F6F7F8')),
                ('r4', 0xf9 -1),
            ),
            'tests':(
                ('r0', 0xff),
            ),
        }
    ],  # ('8C04FFFF', 'lbzu r0,-0x1(r4)')

    # '7C001828': [  # ('7C001828', 'lwarx r0,0x0,r3') unsupported
    #     {
    #         'setup': (
    #             ('r0', 0x10010124),
    #             ('r3', 0x4),  # (EA should be r0+r3 and a multiple of 4
    #         ),
    #
    #         'tests': (
    #             ('r0', 0x10010128),
    #         ),
    #     }
    # ],  # ('7C001828', 'lwarx r0,0x0,r3')
    #
    # '8404FFFC': [ # ('8404FFFC', 'lwzu r0,-0x4(r4)')
    #     {
    #         'setup': (
    #                     # Set the register to be filled with some generic data
    #             ('r0', 0x12345678),
    #             (0x10000150, bytes.fromhex('F1F2F3F4F5F6F7F8')),
    #             ('r4', 0x10000150 + 4),
    #         ),
    #         'tests': (
    #             ('r0', 0xf1f2f3f4),
    #             ('r4', 0x1000150)
    #         ),
    #     }
    # ],  # ('8404FFFC', 'lwzu r0,-0x4(r4)')

    # '4C100000': [ # ('4C100000', 'mcrf cr0,cr4')
    #     {
    #         'setup': (
    #             ('cr0', 0b0100),
    #             ('cr4', 0b0010)
    #         ),
    #
    #         'tests': (
    #             ('cr0', 0b0010),
    #             ),
    #     }
    # ], # ('4C100000', 'mcrf cr0,cr4')

    #
    # '7C000026': [  # ('7C000026', 'mfcr r0')
    #     {
    #         'setup': (
    #             ('cr0', 0b0010),
    #
    #         ),
    #
    #         'tests': (
    #             ('r0', 0b0010),
    #
    #         ),
    #     }
    # ],  # ('7C000026', 'mfcr r0')

    # 'FC00048E': [  # ('FC00048E', 'mffs f0')
    #     {
    #         'setup': (
    #             ('fpscr', 0b0010),
    #             ('f0', 0)
    #
    #         ),
    #
    #         'tests': (
    #             ('f0', 0b0010),
    #
    #         ),
    #     }
    # ],  # ('FC00048E', 'mffs f0')

    # 'F81FFFF0': [  # ('F81FFFF0', 'std r0,-0x10(r31)')
    #     {
    #         'setup': (
    #             ('r0', 0x12345678),
    #             ('r31', 0x10000150 + 0x10),
    #             (0x10000160, bytes.fromhex('F1F2F3F4F5F6F7F8')),
    #
    #         ),
    #
    #         'tests': (
    #         (0x10000160, bytes.fromhex('12345678')),
    #         ),
    #     }
    # ],  # ('F81FFFF0', 'std r0,-0x10(r31)')

    '7C005850': [  # ('7C005850', 'subf r0,r0,r11')
        {
            'setup': (
                ('r0', 0b0000),
                ('r11', 0b00000000000000000000000000000011) # One's comp = 0b11111111111111111111111111111100

            ),

            'tests': (
                ('r0', 3),

            ),
        },
        {
            'setup': (
                ('r0', 0b0010),
                ('r11', 0b0000000000000000000000000000001)

            ),

            'tests': (
                ('r0', 0xffffffffffffffff),

            ),
        }
    ],  # ('7C005850', 'subf r0,r0,r11')

    '7C005851': [  # ('7C005850', 'subf r0,r0,r11')
        {
            'setup': (
                ('r0', 0b0000),
                ('r11', 0b00000000000000000000000000000011) # One's comp = 0b11111111111111111111111111111100

            ),

            'tests': (
                ('r0', 3),
                ('cr0', 0b0100)

            ),
        },
        {
            'setup': (
                ('r0', 0b0010),
                ('r11', 0b0000000000000000000000000000001)

            ),

            'tests': (
                ('r0', 0xffffffffffffffff),
                ('cr0', 0b1000)

            ),
        }
    ],  # ('7C005851', 'subf. r0,r0,r11')

     '7C044010': [  # ('7C044010', 'subfc r0,r4,r8')
        {
            'setup': (
                ('r4',50),
                ('r8', 255 )

            ),

            'tests': (
                ('r0', 205),

            ),
        },
         {
             'setup': (
                 ('r4', 100),
                 ('r8', 50)

             ),

             'tests': (
                 ('r0', 0xffffffffffffffce),

             ),
         },
         {
             'setup': (
                 ('r4', 100),
                 ('r8', 100)

             ),

             'tests': (
                 ('r0', 0),

             ),
         },
    ],  # ('7C044010', 'subfc r0,r4,r8')

    '7C044011': [  # ('7C044011', 'subfc. r0,r4,r8')
        {
            'setup': (
                ('r4',50),
                ('r8', 255 )

            ),

            'tests': (
                ('r0', 205),
                ('cr0', 0b0100)

            ),
        },
         {
             'setup': (
                 ('r4', 100),
                 ('r8', 50)

             ),

             'tests': (
                 ('r0', 0xffffffffffffffce),
                 ('cr0', 0b1000)

             ),
         },
         {
             'setup': (
                 ('r4', 100),
                 ('r8', 100)

             ),

             'tests': (
                 ('r0', 0),
                 ('cr0', 0b0010)

             ),
         },
    ],  # ('7C044011', 'subfc. r0,r4,r8')

    '7C044410': [  # ('7C044410', 'subfco r0,r4,r8')
        {
            'setup': (
                ('r4', 0xFFFFFFFFFFFFFFFF),
                ('r8', -0xFFFFFFFFFFFFFFFF)

            ),

            'tests': (
                ('r0', 0x2),
            ),
        },

        {
            'setup': (
                ('r4', 100),
                ('r8', 50)

            ),

            'tests': (
                ('r0', 0xffffffffffffffce),
            ),
        },

        {
            'setup': (
                ('r4', 100),
                ('r8', 100)

            ),

            'tests': (
                ('r0', 0),
            ),
        },
    ],  #  ('7C044410', 'subfco r0,r4,r8')

    '7C044411': [  # ('7C044411', 'subfco. r0,r4,r8')
        {
            'setup': (
                ('r4', 0xFFFFFFFFFFFFFFFF),
                ('r8', -0xFFFFFFFFFFFFFFFF)

            ),

            'tests': (
                ('r0', 0x2),
                ('cr0', 0b0100)
            ),
        },

        {
            'setup': (
                ('r4', 100),
                ('r8', 50)

            ),

            'tests': (
                ('r0', 0xffffffffffffffce),
                ('cr0', 0b1000)
            ),
        },

        {
            'setup': (
                ('r4', 100),
                ('r8', 100)

            ),

            'tests': (
                ('r0', 0),
                ('cr0', 0b0010)
            ),
        },
    ],  # ('7C044411', 'subfco. r0,r4,r8')

    '7c011511': [  # 7c011511:  subfeo. r0,r1,r2
        {
            'setup': (
                ('r0',0x7000), 
                ('r1',0x7000),
                ('r2',0x2),
                ('cr0', 0b0000),
                ('XER', 0x0)
    
            ),
    
            'tests': (
                ('r0', 0xffffffffffff9001),
                ('cr0', 0b1000),
                ('XER', 0)
    
            ),
        },
        {
             'setup': (
                 ('r0', 100),
                 ('r1', 300),
                 ('r2', 600),
                 ('cr0', 0b0000),
                 ('XER', 0x80000000)
    
             ),
             'tests': (
                 ('r0', 0x12b),
                 ('XER', 0xa0000000),
                 ('cr0', 0b0101)
    
             ),
        },
        {
             'setup': (
                 ('r0', 100),
                 ('r1', -300),
                 ('r2', 600),
                 ('cr0', 0b0000),
                 ('XER', 0x80000000)
    
             ),
             'tests': (
                 ('r0', 0x383),
                 ('XER', 0x80000000),
                 ('cr0', 0b0101)
    
             ),
        },
    ],  # 7c011511:  subfeo. r0,r1,r2

    # '7C0B5092': [  # ('7C0B5092', 'mulhd r0,r11,r10')
    #     {
    #         'setup': (
    #             ('r11',10),
    #             ('r10', 255 )
    #
    #         ),
    #
    #         'tests': (
    #             ('r0', 2550),
    #             # ('cr0', 0b0100)
    #
    #         ),
    #     },
    #      {
    #          'setup': (
    #              ('r11', 100),
    #              ('r10', 50)
    #
    #          ),
    #
    #          'tests': (
    #              ('r0', 5000),
    #              # ('cr0', 0b1000)
    #
    #          ),
    #      },
    #      {
    #          'setup': (
    #              ('r11', 100),
    #              ('r10', 100)
    #
    #          ),
    #
    #          'tests': (
    #              ('r0', 10000),
    #              # ('cr0', 0b0010)
    #
    #          ),
    #      },
    #  ],  # ('7C0B5092', 'mulhd r0,r11,r10')

    '7D4A53B8': [  # ('7D4A53B8', 'nand r10,r10,r10')
        {
            'setup': (
                ('r10', 0b11001100),

            ),

            'tests': (
                ('r10', 0xffffffffffffff33),
                # ('cr0', 0b0100)

            ),
        },
    ],

    '7D4A53B9': [  # ('7D4A53B9', 'nand. r10,r10,r10')
        {
            'setup': (
                ('r10', 0b11001100),

            ),

            'tests': (
                ('r10', 0xffffffffffffff33),
                ('cr0', 0b1000)

            ),
        },
    ],

    '7C0000D0': [  # ('7C0000D0', 'neg r0,r0')
        {
            'setup': (
                ('r0', 0xc),

            ),

            'tests': (
                ('r0', 0xfffffffffffffff4),
                # ('cr0', 0b1)

            ),
        },
        {
            'setup': (
                ('r0', 0xfffffffffffffff4),

            ),

            'tests': (
                ('r0', 0xc),
                # ('cr0', 0b1)

            ),
        },
    ],

    # '7D4900D1': [  # ('7D4900D1', 'neg. r10,r9')  Cr Isn't being set
    #     {
    #         'setup': (
    #             ('r9', 0xc),
    #
    #         ),
    #
    #         'tests': (
    #             ('r10', 0xfffffffffffffff4),
    #             ('cr0', 0b1000)
    #
    #         ),
    #     },
    #     {
    #         'setup': (
    #             ('r9', 0xfffffffffffffff4),
    #
    #         ),
    #
    #         'tests': (
    #             ('r10', 0xc),
    #             ('cr0', 0b0100)
    #
    #         ),
    #     },
    # ], # ('7D4900D1', 'neg. r10,r9')


    '7D4A40F8': [  # ('7D4A40F8', 'nor r10,r10,r8')
        {
            'setup': (
                ('r10', 0xc),
                ('r8', 0xc)

            ),

            'tests': (
                ('r10', 0xfffffffffffffff3),
                #('cr0', 0b1000)

            ),
        },
        {
            'setup': (
                ('r10', 0xffffffffffffff23),
                ('r8', 0x0)

            ),

            'tests': (
                ('r10', 0xdc),
                #('cr0', 0b0100)

            ),
        },
    ], # ('7D4A40F8', 'nor r10,r10,r8')

    '7D4A40F9': [  # ('7D4A40F8', 'nor. r10,r10,r8')
        {
            'setup': (
                ('r10', 0xc),
                ('r8', 0xc)

            ),

            'tests': (
                ('r10', 0xfffffffffffffff3),
                ('cr0', 0b1000)

            ),
        },
        {
            'setup': (
                ('r10', 0xffffffffffffff23),
                ('r8', 0x0)

            ),

            'tests': (
                ('r10', 0xdc),
                ('cr0', 0b0100)

            ),
        },
    ],  # ('7D4A40F9', 'nor. r10,r10,r8')

    '7C005378': [  # ('7C005378', 'or r0,r0,r10')
        {
            'setup': (
                ('r0', 0b0110),
                ('r10', 0b1001)

            ),

            'tests': (
                ('r0', 0b1111),
            ),
        },
        {
            'setup': (
                ('r0', 0b0001),
                ('r10', 0b0001)


            ),

            'tests': (
                ('r0', 0b0001),

            ),
        },
    ],  # ('7C005378', 'or r0,r0,r10')

    '7C005379': [  # ('7C005379', 'or. r0,r0,r10')
        {
            'setup': (
                ('r0', 0b0110),
                ('r10', 0b1001)

            ),

            'tests': (
                ('r0', 0b1111),
                ('cr0', 0b0100)
            ),
        },
        {
            'setup': (
                ('r0', 0b0001),
                ('r10', 0b0001)

            ),

            'tests': (
                ('r0', 0b0001),
                ('cr0', 0b0100)
            ),
        },
    ],  # ('7C005379', 'or. r0,r0,r10')

    '7E004339': [  # ('7E004338', 'orc. r0,r16,r8')
        {
            'setup': (
                ('r16', 0b0110),
                ('r8', 0b1001),
            ),

            'tests': (
                ('r0', 0xfffffffffffffff6),
                ('cr0', 0b1000)            ),
        },
        {
            'setup': (
                ('r16', 0b0001),
                ('r8', 0b0001)

            ),

            'tests': (
                ('r0', 0xffffffffffffffff),
                ('cr0', 0b1000)
            ),
        },
    ],  # ('7E004339', 'orc. r0,r16,r8')

    '60000001': [  # ('60000001', 'ori r0,r0,0x1')
        {
            'setup': (
                ('r0', 0b0110),


            ),

            'tests': (
                ('r0', 0b0111),
            ),
        },
        {
            'setup': (
                ('r0', 0b0001),
                ('r10', 0b0001)

            ),

            'tests': (
                ('r0', 0b0001),

            ),
        },
    ],  # ('60000001', 'ori r0,r0,0x1')

    '60000002': [  # ('60000002', 'ori r0,r0,0x2')
        {
            'setup': (
                ('r0', 0b0110),


            ),

            'tests': (
                ('r0', 0b0110),

            ),
        },
        {
            'setup': (
                ('r0', 0b0010),


            ),

            'tests': (
                ('r0', 0b0010),


            ),
        },
    ],  # ('60000002', 'ori r0,r0,0x2')

    '64000001': [  #('64000001', 'oris r0,r0,0x1')
        {
            'setup': (
                ('r0', 0b0110),

            ),

            'tests': (
                ('r0', 0x10006),

            ),
        },
        {
            'setup': (
                ('r0', 0b0010),

            ),

            'tests': (
                ('r0', 0x10002),

            ),
        },
    ],  # ('64000001', 'oris r0,r0,0x2')

    # '7C6300F4': [  # ('7C6300F4', 'popcntb r3,r3') unsupported
    #     {
    #         'setup': (
    #             ('r3', 0b0110),
    #
    #         ),
    #
    #         'tests': (
    #             ('r3', 0x10006),
    #
    #         ),
    #     },
    #     {
    #         'setup': (
    #             ('r3', 0b0010),
    #
    #         ),
    #
    #         'tests': (
    #             ('r3', 0x10002),
    #
    #         ),
    #     },
    # ],  # ('7C6300F4', 'popcntb r3,r3')

    # '7C6303F4': [  # ('7C6303F4', 'popcntd r3,r3') Unsupported
    #     {
    #         'setup': (
    #             ('r0', 0b0110),
    #
    #         ),
    #
    #         'tests': (
    #             ('r0', 0x10006),
    #
    #         ),
    #     },
    #     {
    #         'setup': (
    #             ('r0', 0b0010),
    #
    #         ),
    #
    #         'tests': (
    #             ('r0', 0x10002),
    #
    #         ),
    #     },
    # ],  # ('7C6303F4', 'popcntd r3,r3')

    '78001788':  # ('78001788', 'rldic r0,r0,0x2,0x1e')
    [
        {
            'setup': (
                ('r0', 0b1),

            ),

            'tests': (
                ('r0', 0b100),

            ),
        },
        {
            'setup': (
                ('r0', 0b0010),

            ),

            'tests': (
                ('r0', 0b1000),

            ),
        },
        {
            'setup': (
                ('r0', 0x80000000),

            ),

            'tests': (
                ('r0', 0x200000000),

            ),
        },
        #  This setup not working correctly in emulator.  Test case is correct though
        # { 'setup': (
        #         ('r0', 0x8000000000000000),
        #
        #     ),
        #
        #     'tests': (
        #         ('r0', 0x0),
        #
        #     ),
        # },

    ],  # ('78001788', 'rldic r0,r0,0x2,0x1e')


    '7EC00036':  # ('7EC00036', 'sld r0,r22,r0')
    [
        {
            'setup': (
                ('r0', 0b1),
                ('r22',0b1)

            ),

            'tests': (
                ('r0', 0b10),

            ),
        },

        {
            'setup': (
                ('r0', 0b1),
                ('r22',0b10)

            ),

            'tests': (
                ('r0', 0b100),

            ),
        },

        {
            'setup': (
                ('r0', 0b11),
                ('r22',0b11)

            ),

            'tests': (
                ('r0', 0b11000),

            ),
        },

        {
            'setup': (
                ('r0', 0b11),
                ('r22',0x8000000000000000)

            ),

            'tests': (
                ('r0', 0b0),

            ),
        },
    ],  # ('7EC00036', 'sld r0,r22,r0')

    '7EC00037':  # ('7EC00037', 'sld. r0,r22,r0')
    [
        {
            'setup': (
                ('r0', 0b1),
                ('r22',0b1)

            ),

            'tests': (
                ('r0', 0b10),
                ('cr0', 0b0100)

            ),
        },

        {
            'setup': (
                ('r0', 0b1),
                ('r22',0b10)

            ),

            'tests': (
                ('r0', 0b100),
                ('cr0', 0b0100)

            ),
        },

        {
            'setup': (
                ('r0', 0b11),
                ('r22',0b11)

            ),

            'tests': (
                ('r0', 0b11000),
                ('cr0', 0b0100)

            ),
        },

        {
            'setup': (
                ('r0', 0b11),
                ('r22',0x8000000000000000)

            ),

            'tests': (
                ('r0', 0b0),
                ('cr0', 0b0010)

            ),
        },
    ],  # ('7EC00037', 'sld. r0,r22,r0') ('7C00F830', 'slw r0,r0,r31')

    '7C00F830':  # ('7C00F830', 'slw r0,r0,r31')
    [
        {
            'setup': (
                ('r0', 0b1),
                ('r31',0b1)

            ),

            'tests': (
                ('r0', 0b10),
                # ('cr0', 0b0100)

            ),
        },

        {
            'setup': (
                ('r0', 0b1),
                ('r31',0b10)

            ),

            'tests': (
                ('r0', 0b100),
               # ('cr0', 0b0100)

            ),
        },

        {
            'setup': (
                ('r0', 0b11),
                ('r31',0b11)

            ),

            'tests': (
                ('r0', 0b11000),
                # ('cr0', 0b0100)

            ),
        },

        {
            'setup': (
                ('r0', 0b11),
                ('r31',0x8000000000000000)

            ),

            'tests': (
                ('r0', 0b11),
                # ('cr0', 0b0010)

            ),
        },
    ],  # ('7C00F830', 'slw r0,r0,r31')

    '7C00F831':  # ('7C00F831', 'slw. r0,r0,r31')
    [
        {
            'setup': (
                ('r0', 0b1),
                ('r31',0b1)

            ),

            'tests': (
                ('r0', 0b10),
                ('cr0', 0b0100)

            ),
        },

        {
            'setup': (
                ('r0', 0b1),
                ('r31',0b10)

            ),

            'tests': (
                ('r0', 0b100),
                ('cr0', 0b0100)

            ),
        },

        {
            'setup': (
                ('r0', 0b11),
                ('r31',0b11)

            ),

            'tests': (
                ('r0', 0b11000),
                ('cr0', 0b0100)

            ),
        },

        {
            'setup': (
                ('r0', 0b11),
                ('r31',0x8000000000000000)

            ),

            'tests': (
                ('r0', 0b11),
                ('cr0', 0b0100)

            ),
        },
    ],  # ('7C00F831', 'slw. r0,r0,r31')

    '7D4A2E34':  # ('7D4A2E34', 'srad r10,r10,r5')
    [
        {
            'setup': (
                ('r10', 0b1100),
                ('r5',0b1)

            ),

            'tests': (
                ('r10', 0b110),
                # ('cr0', 0b0100)

            ),
        },
        {
            'setup': (
                ('r10', 0b1100),
                ('r5',0b10)

            ),

            'tests': (
                ('r10', 0b11),
                # ('cr0', 0b0100)

            ),
        },

        {
            'setup': (
                ('r10', 0b1100),
                ('r5',0b11)

            ),

            'tests': (
                ('r10', 0b1),
                # ('cr0', 0b0100)

            ),
        },
        {
            'setup': (
                ('r10', 0b1100),
                ('r5',0b100)

            ),

            'tests': (
                ('r10', 0b0),
                # ('cr0', 0b0100)

            ),
        },
    ],

    '7D4A2E35':  # ('7D4A2E35', 'srad. r10,r10,r5')
    [
        {
            'setup': (
                ('r10', 0b1100),
                ('r5',0b1)

            ),

            'tests': (
                ('r10', 0b110),
                ('cr0', 0b0100)

            ),
        },
        {
            'setup': (
                ('r10', 0b1100),
                ('r5',0b10)

            ),

            'tests': (
                ('r10', 0b11),
                ('cr0', 0b0100)

            ),
        },

        {
            'setup': (
                ('r10', 0b1100),
                ('r5',0b11)

            ),

            'tests': (
                ('r10', 0b1),
                ('cr0', 0b0100)

            ),
        },
        {
            'setup': (
                ('r10', 0b1100),
                ('r5',0b0100)

            ),

            'tests': (
                ('r10', 0b0),
                ('cr0', 0b0010)

            ),
        },
        # {  #  issue made
        #     'setup': (
        #         ('r10', -4),
        #         ('r5',0b100)
        #
        #     ),
        #
        #     'tests': (
        #         ('r10', 0xfffffffffffffff),
        #         ('cr0', 0b1000)
        #
        #     ),
        # },
    ],

    '7C009674':  # ('7C009674', 'sradi r0,r0,0x12')
    [
        {
            'setup': (
                ('r0', 0b1100),

            ),

            'tests': (
                ('r0', 0b0),
                #  ('cr0', 0b0010)

            ),
        },
        {
            'setup': (
                ('r0', 0b11000000000000000000),
            ),

            'tests': (
                ('r0', 0b11),
                # ('cr0', 0b0100)
            ),
        },

        {
            'setup': (
                ('r0', 0b11000000000000000000000000000000),
            ),
            'tests': (
                ('r0', 0b0011000000000000),
                # ('cr0', 0b0100)

            ),
        },
        {
            'setup': (
                ('r0', 0b1100),
            ),

            'tests': (
                ('r0', 0b0),
                # ('cr0', 0b0010)

            ),
        },
        # {
        #     'setup': ( #still being weird about negative numbers
        #         ('r0', -4),
        #         ),
        #
        #     'tests': (
        #         ('r10', 0xfffffffffffffff),
        #         # ('cr0', 0b1000)
        #
        #     ),
        # },
    ],

    '7D4AEE30':  # ('7D4AEE30', 'sraw r10,r10,r29')
    [
        {
            'setup': (
                ('r10', 0b1100),
                ('r29',0b1)

            ),

            'tests': (
                ('r10', 0b110),
                # ('cr0', 0b0100)

            ),
        },
        {
            'setup': (
                ('r10', 0b1100),
                ('r29',0b11)

            ),

            'tests': (
                ('r10', 0b1),
                # ('cr0', 0b0100)

            ),
        },
        {
            'setup': (
                ('r10', 0b1100),
                ('r29',0b11)

            ),

            'tests': (
                ('r10', 0b1),
                # ('cr0', 0b0100)

            ),
        },
        {
            'setup': (
                ('r10', 0b1100),
                ('r29',0b100)

            ),

            'tests': (
                ('r10', 0b0),
                # ('cr0', 0b0100)

            ),
        },

        {
            'setup': (
                ('r10', 0b1100),
                ('r29',-128)

            ),

            'tests': (
                ('r10', 0b1100),
                # ('cr0', 0b0100)

            ),
        },

        {
            'setup': (
                ('r10', 0b1100),
                ('r29', -1)

            ),

            'tests': (
                ('r10', 0),
                # ('cr0', 0b0100)

            ),
        },
    ],

    '7D4AEE31':  # ('7D4AEE30', 'sraw. r10,r10,r29')
    [
        {
            'setup': (
                ('r10', 0b1100),
                ('r29',0b1)

            ),

            'tests': (
                ('r10', 0b110),
                ('cr0', 0b0100)

            ),
        },
        {
            'setup': (
                ('r10', 0b1100),
                ('r29',0b11)

            ),

            'tests': (
                ('r10', 0b1),
                ('cr0', 0b0100)

            ),
        },
        {
            'setup': (
                ('r10', 0b1100),
                ('r29',0b11)

            ),

            'tests': (
                ('r10', 0b1),
                ('cr0', 0b0100)

            ),
        },
        {
            'setup': (
                ('r10', 0b1100),
                ('r29',0b100)

            ),

            'tests': (
                ('r10', 0b0),
                ('cr0', 0b0010)

            ),
        },

        {
            'setup': (
                ('r10', 0b1100),
                ('r29',-128)

            ),

            'tests': (
                ('r10', 0b1100),
                ('cr0', 0b0100)

            ),
        },

        {
            'setup': (
                ('r10', 0b1100),
                ('r29', -1)

            ),

            'tests': (
                ('r10', 0),
                ('cr0', 0b0010)

            ),
        },
    ],

    # '7C00FE70':  # ('7C00FE70', 'srawi r0,r0,0x1f')
    # [
    #     {
    #         'setup': (
    #             ('r0', 0x80000000),
    #
    #         ),
    #
    #         'tests': (
    #             ('r0', 0xffffffffffffffff),
    #             #  ('cr0', 0b0100)
    #
    #         ),
    #     },
    # ],

    '7c01c436':  # ('7C01C436', 'srd r1,r0,r24')
        [
            {
                'setup': (
                    ('r0', 0b1000),
                    ('r24', 0)

                ),

                'tests': (
                    ('r1', 0x8),
                    #  ('cr0', 0b0100)

                ),
            },
            {
                'setup': (
                    ('r0', 0x800),
                    ('r24', 4)

                ),

                'tests': (
                    ('r1', 0x80),
                    #  ('cr0', 0b0100)

                ),
            },

            {
                'setup': (
                    ('r0', 0x80000000),
                    ('r24', 1)

                ),

                'tests': (
                    ('r1', 0x40000000),
                    #  ('cr0', 0b0100)

                ),
            },

            {
                'setup': (
                    ('r0', 0x80000000),
                    ('r24', -1)

                ),

                'tests': (
                    ('r1', 0x0),
                    #  ('cr0', 0b0100)

                ),
            },
        ],

    '7D4ACC30':  # ('7D4ACC30', 'srw r10,r10,r25')
        [
            {
                'setup': (
                    ('r10', 0b1000),
                    ('r25', 0)

                ),

                'tests': (
                    ('r10', 0x8),
                    #  ('cr0', 0b0100)

                ),
            },
            {
                'setup': (
                    ('r10', 0x800),
                    ('r25', 4)

                ),

                'tests': (
                    ('r10', 0x80),
                    #  ('cr0', 0b0100)

                ),
            },

            {
                'setup': (
                    ('r10', 0x80000000),
                    ('r25', 1)

                ),

                'tests': (
                    ('r10', 0x40000000),
                    #  ('cr0', 0b0100)

                ),
            },

            {
                'setup': (
                    ('r10', 0x80000000),
                    ('r25', -1)

                ),

                'tests': (
                    ('r10', 0x0),
                    #  ('cr0', 0b0100)

                ),
            },
        ],

    # '981CFFFF':  # ('981CFFFF', 'stb r0,-0x1(r28)')
    #     [
    #         {
    #             'setup': (
    #                 ('r0', 0x3),
    #                 ('r28', 0x10000150 + 0x10)
    #
    #             ),
    #
    #             'tests': (
    #                 (0x00001050, bytes.fromhex('0003')),
    #                 #  ('cr0', 0b0100)
    #
    #             ),
    #         },
    #     ]

    '2000FFF8': [  # ('2000FFF8', 'subfic r0,r0,-0x8')
        {
            'setup': (
                ('r0', 8),

            ),

            'tests': (
                ('r0', 0xfffffffffffffff0),

            ),
        },

        {
            'setup': (
                ('r0', -8),

            ),

            'tests': (
                ('r0', 0),

            ),
        },

        {
            'setup': (
                ('r0', -16),

            ),

            'tests': (
                ('r0', 8),

            ),
        },

        {
            'setup': (
                ('r0', 0),

            ),

            'tests': (
                ('r0', 0xfffffffffffffff8),

            ),
        },
    ],  # ('64000001', 'oris r0,r0,0x2')

    '200000FF': [  # ('2000FFF8', 'subfic r0,r0,255')
        {
            'setup': (
                ('r0', 50),

            ),

            'tests': (
                ('r0', 205),

            ),
        },

        {
            'setup': (
                ('r0', -8),

            ),

            'tests': (
                ('r0', 263),

            ),
        },

        {
            'setup': (
                ('r0', 0),

            ),

            'tests': (
                ('r0', 255),

            ),
        },

    ],  # ('64000001', 'oris r0,r0,0x2')

    # '7D400106': [  # ('7D400106', 'wrtee r10')
    #     {
    #         'setup': (
    #             ('r10', 0xffffffffffffffff),
    #
    #         ),
    #
    #         'tests': (
    #             ('MSR', 0x8),
    #
    #         ),
    #     },
    #
    # ],  # ('7D400106', 'wrtee r10')

      '78001788': [  # ('78001788', 'rldic r0,r0,0x2,0x1e')
        {
            'setup': (
                ('r0', 0xffffffffffff0000),


            ),
            'tests': (
                ('r0', 0x3fffc0000),

            ),
        },
        {
            'setup': (
                ('r0', 0b1),


            ),
            'tests': (
                ('r0', 0b100),

            ),
        }
    ],  # ('78001788', 'rldic r0,r0,0x2,0x1e')

    '78001789': [  # ('78001788', 'rldic r0,r0,0x2,0x1e')
        {
            'setup': (
                ('r0', 0xffffffffffff0000),


            ),
            'tests': (
                ('r0', 0x3fffc0000),
                ('cr0', 0b0100)

            ),
        },
        {
            'setup': (
                ('r0', 0b1),


            ),
            'tests': (
                ('r0', 0b100),
                ('cr0', 0b0100)

            ),
        },
        {
            'setup': (
                ('r0', 0b11111000011111),
            ),
            'tests': (
                ('r0', 0b1111100001111100),
                ('cr0', 0b0100)
            ),
        },
        {
            'setup': (
                ('r0', 0x8000000000000000),


            ),
            'tests': (
                ('r0', 0x0),
                ('cr0', 0b0010)

            ),
        },
        {
            'setup': (
                ('r0', 0xf000000000000000),


            ),
            'tests': (
                ('r0', 0x0),
                ('cr0', 0b0010)

            ),
        },
    ],  # ('78001788', 'rldic r0,r0,0x2,0x1e')

     '7C000026': [  # ('7C000026', 'mfcr r0')
        {
            'setup': (
                ('r0', 0),
                ('CR', 0b0010),

            ),

            'tests': (
                ('CR', 0b0010),
                ('r0', 0b0010)
            ),
        },

        {
            'setup': (

                ('r0', 0),
                ('CR', 0x88882222),

            ),

            'tests': (

                ('r0', 0x88882222),
                ('CR', 0x88882222),

            ),
        }
    ],  # ('7C000026', 'mfcr r0')

    'E8070122': [ # ('E8070122', 'lwa r0,0x120(r7)')
        {
            'setup': (
                ('r0', 0x0),
                ('r7', 0x10000200 - 0x120),
                (0x10000200, bytes.fromhex('EEDCBA98'))
                    ),

            'tests':(
                ('r0', 0xFFFFFFFFEEDCBA98),
            ),
        },

        {
            'setup': (
                ('r0', 0x0),
                ('r7', 0x10000200 - 0x120),
                (0x10000200, bytes.fromhex('00000001'))
                    ),

            'tests':(
                ('r0', 0x1),
            ),
        },

                {
            'setup': (
                ('r0', 0x0),
                ('r7', 0x10000200 - 0x120),
                (0x10000200, bytes.fromhex('1EDCBA98'))
                    ),

            'tests':(
                ('r0', 0x1EDCBA98),
            ),
        },

        {
            'setup': (
                ('r0', 0x0),
                ('r7', 0x10000200 - 0x120),
                (0x10000200, bytes.fromhex('00000001'))
                    ),

            'tests':(
                ('r0', 0x1),
            ),
        },

        {
            'setup': (
                ('r0', 0x0),
                ('r7', 0x10000200 - 0x120),
                (0x10000200, bytes.fromhex('8EDCBA98'))
                    ),

            'tests':(
                ('r0', 0xffffffff8EDCBA98),
            ),
        },

        {
            'setup': (
                ('r0', 0x0),
                ('r7', 0x10000200 - 0x120),
                (0x10000200, bytes.fromhex('7EDCBA98'))
                    ),

            'tests':(
                ('r0', 0x7EDCBA98),
            ),
        },

    ],  # ('E8070122', 'lwa r0,0x120(r7)')

    '5D4A383E': [ # ('5D4A383E', 'rlwnm r10,r10,r7,0x0,0x1f') (rotlw r10,r10,r7)

        {
            'setup': (
                ('r10', 0x84210124),
                ('r7', 0x11223344)
            ),

            'tests': (
                ('r10', 0x42101248),

            ),
        },

        {
            'setup': (
                ('r10', 0x84210124),
                ('r7', 0x11223345)
            ),

            'tests': (
                ('r10', 0x84202490),

            ),
        },
    ],

    ###### Unconditional Branch ######

    '48000000': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
            ),
        }
    ], # b 0x40004560 (unconditional branch relative +0x0)

    '48000200': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004760 ),
                ('LR', 0x12345678 ),
            ),
        }
    ], # b 0x40004760 (unconditional branch relative +0x200)

    '4BFFD000': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40001560 ),
                ('LR', 0x12345678 ),
            ),
        }
    ], # b 0x40001560 (unconditional branch relative -0x3000)

    ##################################
    ###### Unconditional Branch ######
    ##################################

    ###### Unconditional Branch Absolute ######

    '48000002': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x00000000 ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xFFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x00000000 ),
                ('LR', 0x12345678 ),
            ),
        },
    ], # ba 0x40004560 (unconditional branch relative 0x0)

    '48000202': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x00000200 ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xFFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x00000200 ),
                ('LR', 0x12345678 ),
            ),
        },
    ], # ba 0x00000200 (unconditional branch absolute 0x200)

    '4BFFD002': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0xffffffffffffd000 ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xFFFFFFFF ),
            ),
            'tests': (
                ('pc', 0xffffffffffffd000 ),
                ('LR', 0x12345678 ),
            ),
        },
    ], # ba 0xffffffffffffd000 (unconditional branch absolute -0x3000)

    ###### Unconditional Branch with Link ######

    '48000001': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004560 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xFFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x40004560 ),
                ('LR', 0x40004564 ),
            ),
        },
    ], # bl 0x40004560 (unconditional branch relative +0x0)

    '48000201': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004760 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xFFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x40004760 ),
                ('LR', 0x40004564 ),
            ),
        },
    ], # bl 0x40004760 (unconditional branch relative +0x200)

    '4BFFD001': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40001560 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xFFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x40001560 ),
                ('LR', 0x40004564 ),
            ),
        },
    ], # bl 0x40001560 (unconditional branch relative -0x3000)

    ###### Unconditional Branch Absolute with Link ######

    '48000003': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x00000000 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xFFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x00000000 ),
                ('LR', 0x40004564 ),
            ),
        },
    ], # bla 0x40004560 (unconditional branch relative 0x0)

    '48000203': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x00000200 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xFFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x00000200 ),
                ('LR', 0x40004564 ),
            ),
        },
    ], # bla 0x00000200 (unconditional branch absolute 0x200)

    '4BFFD003': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0xffffffffffffd000 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xFFFFFFFF ),
            ),
            'tests': (
                ('pc', 0xffffffffffffd000 ),
                ('LR', 0x40004564 ),
            ),
        },
    ], # bla 0xffffffffffffd000 (unconditional branch absolute -0x3000)

    ###### Unconditional Conditional Branch (BO == 0b1x1xx) ######

    '42800002': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x00000000 ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xFFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x00000000 ),
                ('LR', 0x12345678 ),
            ),
        },
    ], # ba 0x00000000 (unconditional branch absolute 0x0)

    '42800202': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x00000200 ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xFFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x00000200 ),
                ('LR', 0x12345678 ),
            ),
        },
    ], # ba 0x00000200 (unconditional branch absolute 0x200)

    '428FD002': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0xffffffffffffd000 ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xFFFFFFFF ),
            ),
            'tests': (
                ('pc', 0xffffffffffffd000 ),
                ('LR', 0x12345678 ),
            ),
        },
    ], # ba 0xffffffffffffd000 (unconditional branch absolute -0x3000)

    '42800001': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004560 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xFFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x40004560 ),
                ('LR', 0x40004564 ),
            ),
        },
    ], # bl 0x40004560 (unconditional branch relative +0x0)

    '42800201': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004760 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xFFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x40004760 ),
                ('LR', 0x40004564 ),
            ),
        },
    ], # bl 0x40004760 (unconditional branch relative +0x200)

    '4280D001': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40001560 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xFFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x40001560 ),
                ('LR', 0x40004564 ),
            ),
        },
    ], # bl 0x40001560 (unconditional branch relative -0x3000)

    '42800003': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x00000000 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xFFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x00000000 ),
                ('LR', 0x40004564 ),
            ),
        },
    ], # bla 0x40004560 (unconditional branch relative 0x0)

    '42800203': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x00000200 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xFFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x00000200 ),
                ('LR', 0x40004564 ),
            ),
        },
    ], # bla 0x00000200 (unconditional branch absolute 0x200)

    '4280D003': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0xffffffffffffd000 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xFFFFFFFF ),
            ),
            'tests': (
                ('pc', 0xffffffffffffd000 ),
                ('LR', 0x40004564 ),
            ),
        },
    ], # bla 0xffffffffffffd000 (unconditional branch absolute -0x3000)

    ###### Unconditional Branch to CTR ######

    '4E800420': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xFFFFFFFF ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x12345678 ),
            ),
        },
    ], # bctr (unconditional branch to CTR)

    '4E800421': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xFFFFFFFF ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
            ),
        },
    ], # bctrl (unconditional branch to CTR)

    ###### Unconditional Branch to LR ######

    '4E800020': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xFFFFFFFF ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
            ),
        },
    ], # blr (unconditional branch to LR)

    '4E800021': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xFFFFFFFF ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # blrl (unconditional branch to LR)

    #####################################################
    ###### Branch Decrement and branch if CTR != 0 ######
    #####################################################

    '42000060': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        }
    ], # bdnz

    '42000061': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        }
    ], # bdnzl

    '42000062': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        }
    ], # bdnza

    '42000063': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        }
    ], # bdnzla

    #######################################################################
    ###### Branch Decrement and branch if CTR != 0 OR CONDITION TRUE ######
    #######################################################################

    ###### Branch Decrement and branch if CTR != 0 OR LT ######

    '41000060': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        }
    ], # bdnzlt (branch LR if --CTR != 0 OR 4*cr0+lt == 1)

    '41000061': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
    ], # bdnzltl (branch LR if --CTR != 0 OR 4*cr0+lt == 1)

    '41000062': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
    ], # bdnzlta 0x60 (branch 0x60 if --CTR != 0 OR 4*cr0+lt == 1)

    '41000063': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
    ], # bdnzltla 0x60 (branch 0x60 if --CTR != 0 OR 4*cr0+lt == 1)

    ###### Branch Decrement and branch if CTR != 0 OR GT ######

    '41010060': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        }
    ], # bdnzgt (branch LR if --CTR != 0 OR 4*cr0+gt == 1)

    '41010061': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
    ], # bdnzgtl (branch LR if --CTR != 0 OR 4*cr0+gt == 1)

    '41010062': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
    ], # bdnzgta 0x60 (branch 0x60 if --CTR != 0 OR 4*cr0+gt == 1)

    '41010063': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
    ], # bdnzgtla 0x60 (branch 0x60 if --CTR != 0 OR 4*cr0+gt == 1)

    ###### Branch Decrement and branch if CTR != 0 OR EQ ######

    '41020060': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        }
    ], # bdnzeq (branch LR if --CTR != 0 OR 4*cr0+eq == 1)

    '41020061': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
    ], # bdnzeql (branch LR if --CTR != 0 OR 4*cr0+eq == 1)

    '41020062': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
    ], # bdnzeqa 0x60 (branch 0x60 if --CTR != 0 OR 4*cr0+eq == 1)

    '41020063': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
    ], # bdnzeqla 0x60 (branch 0x60 if --CTR != 0 OR 4*cr0+eq == 1)

    ###### Branch Decrement and branch if CTR != 0 OR SO ######

    '41030060': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        }
    ], # bdnzso (branch LR if --CTR != 0 OR 4*cr0+so == 1)

    '41030061': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
    ], # bdnzsol (branch LR if --CTR != 0 OR 4*cr0+so == 1)

    '41030062': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
    ], # bdnzsoa 0x60 (branch 0x60 if --CTR != 0 OR 4*cr0+so == 1)

    '41030063': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
    ], # bdnzsola 0x60 (branch 0x60 if --CTR != 0 OR 4*cr0+so == 1)

    ########################################################################
    ###### Branch Decrement and branch if CTR != 0 OR CONDITION FALSE ######
    ########################################################################

    ###### Branch Decrement and branch if CTR != 0 OR GE ######

    '40000060': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        }
    ], # bdnzge (branch LR if --CTR != 0 OR 4*cr0+lt == 0)

    '40000061': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
    ], # bdnzgel (branch LR if --CTR != 0 OR 4*cr0+lt == 0)

    '40000062': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
    ], # bdnzgea 0x60 (branch 0x60 if --CTR != 0 OR 4*cr0+lt == 0)

    '40000063': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
    ], # bdnzgela 0x60 (branch 0x60 if --CTR != 0 OR 4*cr0+lt == 0)

    ###### Branch Decrement and branch if CTR != 0 OR LE ######

    '40010060': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        }
    ], # bdnzle (branch LR if --CTR != 0 OR 4*cr0+gt == 0)

    '40010061': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
    ], # bdnzlel (branch LR if --CTR != 0 OR 4*cr0+gt == 0)

    '40010062': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
    ], # bdnzlea 0x60 (branch 0x60 if --CTR != 0 OR 4*cr0+gt == 0)

    '40010063': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
    ], # bdnzlela 0x60 (branch 0x60 if --CTR != 0 OR 4*cr0+gt == 0)

    ###### Branch Decrement and branch if CTR != 0 OR NE ######

    '40020060': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        }
    ], # bdnzne (branch LR if --CTR != 0 OR 4*cr0+eq == 0)

    '40020061': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
    ], # bdnznel (branch LR if --CTR != 0 OR 4*cr0+eq == 0)

    '40020062': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
    ], # bdnznea 0x60 (branch 0x60 if --CTR != 0 OR 4*cr0+eq == 0)

    '40020063': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
    ], # bdnznela 0x60 (branch 0x60 if --CTR != 0 OR 4*cr0+eq == 0)

    ###### Branch Decrement and branch if CTR != 0 OR NS ######

    '40030060': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        }
    ], # bdnzns (branch LR if --CTR != 0 OR 4*cr0+so == 0)

    '40030061': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
    ], # bdnznsl (branch LR if --CTR != 0 OR 4*cr0+so == 0)

    '40030062': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
    ], # bdnznsa 0x60 (branch 0x60 if --CTR != 0 OR 4*cr0+so == 0)

    '40030063': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
    ], # bdnznsla 0x60 (branch 0x60 if --CTR != 0 OR 4*cr0+so == 0)

    #####################################################
    ###### Branch Decrement and branch if CTR == 0 ######
    #####################################################

    '42400060': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        }
    ], # bdz

    '42400061': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        }
    ], # bdzl

    '42400062': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        }
    ], # bdza

    '42400063': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        }
    ], # bdzla

    #######################################################################
    ###### Branch Decrement and branch if CTR == 0 OR CONDITION TRUE ######
    #######################################################################

    ###### Branch Decrement and branch if CTR == 0 OR LT ######

    '41400060': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        }
    ], # bdzlt (branch LR if --CTR == 0 OR 4*cr0+lt == 1)

    '41400061': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bdzltl (branch LR if --CTR == 0 OR 4*cr0+lt == 1)

    '41400062': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bdzlta 0x60 (branch 0x60 if --CTR == 0 OR 4*cr0+lt == 1)

    '41400063': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bdzltla 0x60 (branch 0x60 if --CTR == 0 OR 4*cr0+lt == 1)

    ###### Branch Decrement and branch if CTR == 0 OR GT ######

    '41410060': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        }
    ], # bdzgt (branch LR if --CTR == 0 OR 4*cr0+gt == 1)

    '41410061': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bdzgtl (branch LR if --CTR == 0 OR 4*cr0+gt == 1)

    '41410062': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bdzgta 0x60 (branch 0x60 if --CTR == 0 OR 4*cr0+gt == 1)

    '41410063': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bdzgtla 0x60 (branch 0x60 if --CTR == 0 OR 4*cr0+gt == 1)

    ###### Branch Decrement and branch if CTR == 0 OR EQ ######

    '41420060': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        }
    ], # bdzeq (branch LR if --CTR == 0 OR 4*cr0+eq == 1)

    '41420061': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bdzeql (branch LR if --CTR == 0 OR 4*cr0+eq == 1)

    '41420062': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bdzeqa 0x60 (branch 0x60 if --CTR == 0 OR 4*cr0+eq == 1)

    '41420063': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bdzeqla 0x60 (branch 0x60 if --CTR == 0 OR 4*cr0+eq == 1)

    ###### Branch Decrement and branch if CTR == 0 OR SO ######

    '41430060': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        }
    ], # bdzso (branch LR if --CTR == 0 OR 4*cr0+so == 1)

    '41430061': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bdzsol (branch LR if --CTR == 0 OR 4*cr0+so == 1)

    '41430062': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bdzsoa 0x60 (branch 0x60 if --CTR == 0 OR 4*cr0+so == 1)

    '41430063': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bdzsola 0x60 (branch 0x60 if --CTR == 0 OR 4*cr0+so == 1)

    ########################################################################
    ###### Branch Decrement and branch if CTR == 0 OR CONDITION FALSE ######
    ########################################################################

    ###### Branch Decrement and branch if CTR == 0 OR GE ######

    '40400060': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        }
    ], # bdzge (branch LR if --CTR == 0 OR 4*cr0+lt == 0)

    '40400061': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bdzgel (branch LR if --CTR == 0 OR 4*cr0+lt == 0)

    '40400062': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bdzgea 0x60 (branch 0x60 if --CTR == 0 OR 4*cr0+lt == 0)

    '40400063': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bdzgela 0x60 (branch 0x60 if --CTR == 0 OR 4*cr0+lt == 0)

    ###### Branch Decrement and branch if CTR == 0 OR LE ######

    '40410060': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        }
    ], # bdzle (branch LR if --CTR == 0 OR 4*cr0+gt == 0)

    '40410061': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bdzlel (branch LR if --CTR == 0 OR 4*cr0+gt == 0)

    '40410062': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bdzlea 0x60 (branch 0x60 if --CTR == 0 OR 4*cr0+gt == 0)

    '40410063': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bdzlela 0x60 (branch 0x60 if --CTR == 0 OR 4*cr0+gt == 0)

    ###### Branch Decrement and branch if CTR == 0 OR NE ######

    '40420060': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        }
    ], # bdzne (branch LR if --CTR == 0 OR 4*cr0+eq == 0)

    '40420061': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bdznel (branch LR if --CTR == 0 OR 4*cr0+eq == 0)

    '40420062': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bdznea 0x60 (branch 0x60 if --CTR == 0 OR 4*cr0+eq == 0)

    '40420063': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bdznela 0x60 (branch 0x60 if --CTR == 0 OR 4*cr0+eq == 0)

    ###### Branch Decrement and branch if CTR == 0 OR NS ######

    '40430060': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        }
    ], # bdzns (branch LR if --CTR == 0 OR 4*cr0+so == 0)

    '40430061': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bdznsl (branch LR if --CTR == 0 OR 4*cr0+so == 0)

    '40430062': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bdznsa 0x60 (branch 0x60 if --CTR == 0 OR 4*cr0+so == 0)

    '40430063': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bdznsla 0x60 (branch 0x60 if --CTR == 0 OR 4*cr0+so == 0)

    ###########################################################
    ###### Branch Decrement and branch to LR if CTR != 0 ######
    ###########################################################

    '4E000020': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000001 ),
            ),
        }
    ], # bdnzlr

    '4E000021': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        }
    ], # bdnzlrl

    #######################################################################
    ###### Branch Decrement and branch to LR if CTR != 0 OR CONDITION TRUE ######
    #######################################################################

    ###### Branch Decrement and branch to LR if CTR != 0 OR LT ######

    '4D000020': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000000 ),
            ),
        }
    ], # bdnzltlr (branch LR if --CTR != 0 OR 4*cr0+lt == 1)

    '4D000021': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
    ], # bdnzltlrl (branch LR if --CTR != 0 OR 4*cr0+lt == 1)

    ###### Branch Decrement and branch to LR if CTR != 0 OR GT ######

    '4D010020': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000000 ),
            ),
        }
    ], # bdnzgtlr (branch LR if --CTR != 0 OR 4*cr0+gt == 1)

    '4D010021': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
    ], # bdnzgtlrl (branch LR if --CTR != 0 OR 4*cr0+gt == 1)

    ###### Branch Decrement and branch to LR if CTR != 0 OR EQ ######

    '4D020020': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000000 ),
            ),
        }
    ], # bdnzeqlr (branch LR if --CTR != 0 OR 4*cr0+eq == 1)

    '4D020021': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
    ], # bdnzeqlrl (branch LR if --CTR != 0 OR 4*cr0+eq == 1)

    ###### Branch Decrement and branch to LR if CTR != 0 OR SO ######

    '4D030020': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000000 ),
            ),
        }
    ], # bdnzsolr (branch LR if --CTR != 0 OR 4*cr0+so == 1)

    '4D030021': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
    ], # bdnzsolrl (branch LR if --CTR != 0 OR 4*cr0+so == 1)

    ########################################################################
    ###### Branch Decrement and branch to LR if CTR != 0 OR CONDITION FALSE ######
    ########################################################################

    ###### Branch Decrement and branch to LR if CTR != 0 OR GE ######

    '4C000020': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000000 ),
            ),
        }
    ], # bdnzgelr (branch LR if --CTR != 0 OR 4*cr0+lt == 0)

    '4C000021': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
    ], # bdnzgelrl (branch LR if --CTR != 0 OR 4*cr0+lt == 0)

    ###### Branch Decrement and branch to LR if CTR != 0 OR LE ######

    '4C010020': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000000 ),
            ),
        }
    ], # bdnzlelr (branch LR if --CTR != 0 OR 4*cr0+gt == 0)

    '4C010021': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
    ], # bdnzlelrl (branch LR if --CTR != 0 OR 4*cr0+gt == 0)

    ###### Branch Decrement and branch to LR if CTR != 0 OR NE ######

    '4C020020': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000000 ),
            ),
        }
    ], # bdnznelr (branch LR if --CTR != 0 OR 4*cr0+eq == 0)

    '4C020021': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
    ], # bdnznelrl (branch LR if --CTR != 0 OR 4*cr0+eq == 0)

    ###### Branch Decrement and branch to LR if CTR != 0 OR NS ######

    '4C030020': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000000 ),
            ),
        }
    ], # bdnznslr (branch LR if --CTR != 0 OR 4*cr0+so == 0)

    '4C030021': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
    ], # bdnznslrl (branch LR if --CTR != 0 OR 4*cr0+so == 0)

    #####################################################
    ###### Branch Decrement and branch to LR if CTR == 0 ######
    #####################################################

    '4E400020': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000000 ),
            ),
        }
    ], # bdzlr

    '4E400021': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x00000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        }
    ], # bdzlrl

    #######################################################################
    ###### Branch Decrement and branch to LR if CTR == 0 OR CONDITION TRUE ######
    #######################################################################

    ###### Branch Decrement and branch to LR if CTR == 0 OR LT ######
    '4D400020': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000001 ),
            ),
        }
    ], # bdzltlr (branch LR if --CTR == 0 OR 4*cr0+lt == 1)

    '4D400021': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bdzltlrl (branch LR if --CTR == 0 OR 4*cr0+lt == 1)

    ###### Branch Decrement and branch to LR if CTR == 0 OR GT ######

    '4D410020': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000001 ),
            ),
        }
    ], # bdzgtlr (branch LR if --CTR == 0 OR 4*cr0+gt == 1)

    '4D410021': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bdzgtlrl (branch LR if --CTR == 0 OR 4*cr0+gt == 1)

    ###### Branch Decrement and branch to LR if CTR == 0 OR EQ ######

    '4D420020': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000001 ),
            ),
        }
    ], # bdzeqlr (branch LR if --CTR == 0 OR 4*cr0+eq == 1)

    '4D420021': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bdzeqlrl (branch LR if --CTR == 0 OR 4*cr0+eq == 1)

    ###### Branch Decrement and branch to LR if CTR == 0 OR SO ######

    '4D430020': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000001 ),
            ),
        }
    ], # bdzsolr (branch LR if --CTR == 0 OR 4*cr0+so == 1)

    '4D430021': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bdzsolrl (branch LR if --CTR == 0 OR 4*cr0+so == 1)

    ########################################################################
    ###### Branch Decrement and branch to LR if CTR == 0 OR CONDITION FALSE ######
    ########################################################################

    ###### Branch Decrement and branch to LR if CTR == 0 OR GE ######

    '4C400020': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000001 ),
            ),
        }
    ], # bdzgelr (branch LR if --CTR == 0 OR 4*cr0+lt == 0)

    '4C400021': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bdzgelrl (branch LR if --CTR == 0 OR 4*cr0+lt == 0)

    ###### Branch Decrement and branch to LR if CTR == 0 OR LE ######

    '4C410020': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000001 ),
            ),
        }
    ], # bdzlelr (branch LR if --CTR == 0 OR 4*cr0+gt == 0)

    '4C410021': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x40000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bdzlelrl (branch LR if --CTR == 0 OR 4*cr0+gt == 0)

    ###### Branch Decrement and branch to LR if CTR == 0 OR NE ######

    '4C420020': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000001 ),
            ),
        }
    ], # bdznelr (branch LR if --CTR == 0 OR 4*cr0+eq == 0)

    '4C420021': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x20000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bdznelrl (branch LR if --CTR == 0 OR 4*cr0+eq == 0)

    ###### Branch Decrement and branch to LR if CTR == 0 OR NS ######

    '4C430020': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000001 ),
            ),
        }
    ], # bdznslr (branch LR if --CTR == 0 OR 4*cr0+so == 0)

    '4C430021': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x10000000 ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bdznslrl LR (branch LR if --CTR == 0 OR 4*cr0+so == 0)

    ######################################################################
    ###### Branch Conditional (unsimplified, non-standard BO hints) ######
    ######################################################################

    '40A00060': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
            ),
        }
    ], # bc 0x5,lt,0x400045c0 (branch LR if 4*cr0+lt == 0)

    '40A00062': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
            ),
        }
    ], # bca 0x5,lt,0x60 (branch LR if 4*cr0+lt == 0)

    '40A00061': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # bcl 0x5,lt,0x400045c0 (branch LR if 4*cr0+lt == 0)

    '40A00063': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # bcla 0x5,lt,0x60 (branch LR if 4*cr0+lt == 0)

    ############################################################
    ###### Branch Conditional (simplified) CONDITION TRUE ######
    ############################################################

    ###### Branch if LT ######

    '41800060': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
            ),
        }
    ], # blt +0x60 (branch +0x60 if 4*cr0+lt == 1)

    '41800061': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # bltl +0x60 (branch +0x60 if 4*cr0+lt == 1)

    '41800062': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
            ),
        }
    ], # blta 0x000000060 (branch 0x60 if 4*cr0+lt == 1)

    '41800063': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # bltla 0x000000060 (branch 0x60 if 4*cr0+lt == 1)

    ###### Branch if GT ######

    '41810060': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
            ),
        }
    ], # bgt +0x60 (branch +0x60 if 4*cr0+gt == 1)

    '41810061': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # bgtl +0x60 (branch +0x60 if 4*cr0+gt == 1)

    '41810062': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
            ),
        }
    ], # bgta 0x000000060 (branch 0x60 if 4*cr0+gt == 1)

    '41810063': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # bgtla 0x000000060 (branch 0x60 if 4*cr0+gt == 1)

    ###### Branch if EQ ######

    '41820060': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
            ),
        }
    ], # beq +0x60 (branch +0x60 if 4*cr0+eq == 1)

    '41820061': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # beql +0x60 (branch +0x60 if 4*cr0+eq == 1)

    '41820062': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
            ),
        }
    ], # beqa 0x000000060 (branch 0x60 if 4*cr0+eq == 1)

    '41820063': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # beqla 0x000000060 (branch 0x60 if 4*cr0+eq == 1)

    ###### Branch if SO ######

    '41830060': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
            ),
        }
    ], # bso +0x60 (branch +0x60 if 4*cr0+so == 1)

    '41830061': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # bsol +0x60 (branch +0x60 if 4*cr0+so == 1)

    '41830062': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
            ),
        }
    ], # bsoa 0x000000060 (branch 0x60 if 4*cr0+so == 1)

    '41830063': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # bsola 0x000000060 (branch 0x60 if 4*cr0+so == 1)

    ############################################################
    ###### Branch Conditional (simplified) CONDITION FALSE ######
    ############################################################

    ###### Branch if GE ######

    '40800060': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
            ),
        }
    ], # bge +0x60 (branch +0x60 if 4*cr0+lt == 0)

    '40800061': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # bgel +0x60 (branch +0x60 if 4*cr0+lt == 0)

    '40800062': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
            ),
        }
    ], # bgea 0x000000060 (branch 0x60 if 4*cr0+lt == 0)

    '40800063': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # bgela 0x000000060 (branch 0x60 if 4*cr0+lt == 0)

    ###### Branch if LE ######

    '40810060': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
            ),
        }
    ], # ble +0x60 (branch +0x60 if 4*cr0+gt == 0)

    '40810061': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # blel +0x60 (branch +0x60 if 4*cr0+gt == 0)

    '40810062': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
            ),
        }
    ], # blea 0x000000060 (branch 0x60 if 4*cr0+gt == 0)

    '40810063': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # blela 0x000000060 (branch 0x60 if 4*cr0+gt == 0)

    ###### Branch if NE ######

    '40820060': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
            ),
        }
    ], # bne +0x60 (branch +0x60 if 4*cr0+eq == 0)

    '40820061': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # bnel +0x60 (branch +0x60 if 4*cr0+eq == 0)

    '40820062': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
            ),
        }
    ], # bnea 0x000000060 (branch 0x60 if 4*cr0+eq == 0)

    '40820063': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # bnela 0x000000060 (branch 0x60 if 4*cr0+eq == 0)

    ###### Branch if NS ######

    '40830060': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x12345678 ),
            ),
        }
    ], # bns +0x60 (branch +0x60 if 4*cr0+so == 0)

    '40830061': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x400045c0 ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # bnsl +0x60 (branch +0x60 if 4*cr0+so == 0)

    '40830062': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x12345678 ),
            ),
        }
    ], # bnsa 0x000000060 (branch 0x60 if 4*cr0+so == 0)

    '40830063': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x00000060 ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # bnsla 0x000000060 (branch 0x60 if 4*cr0+so == 0)

    #############################################################################
    ###### Branch Conditional to CTR (unsimplified, non-standard BO hints) ######
    #############################################################################

    '4DA00420': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
                ('CTR', 0xAAAAAAAA ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x12345678 ),
                ('CTR', 0xAAAAAAAA ),
            ),
        },
    ], # bcctr 0xD,lt,0x0 (branch CTR if 4*cr0+lt == 1)

    '4DA00421': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xAAAAAAAA ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0xAAAAAAAA ),
            ),
        },
    ], # bcctrl 0xD,lt,0x0 (branch CTR if 4*cr0+lt == 1)

    ###################################################################
    ###### Branch Conditional (simplified) to CTR CONDITION TRUE ######
    ###################################################################

    ###### Branch CTR if LT ######

    '4D800420': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x12345678 ),
            ),
        }
    ], # bltctr (branch CTR if 4*cr0+lt == 1)

    '4D800421': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # bltctrl (branch CTR if 4*cr0+lt == 1)

    ###### Branch CTR if GT ######

    '4D810420': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x12345678 ),
            ),
        }
    ], # bgtctr (branch CTR if 4*cr0+lt == 1)

    '4D810421': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # bgtctrl (branch CTR if 4*cr0+lt == 1)

    ###### Branch CTR if EQ ######

    '4D820420': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x12345678 ),
            ),
        }
    ], # beqctr (branch CTR if 4*cr0+eq == 1)

    '4D820421': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # beqctrl (branch CTR if 4*cr0+eq == 1)

    ###### Branch CTR if SO ######

    '4D830420': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x12345678 ),
            ),
        }
    ], # bsoctr (branch CTR if 4*cr0+so == 1)

    '4D830421': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # bsoctrl (branch CTR if 4*cr0+so == 1)

    ####################################################################
    ###### Branch Conditional (simplified) to CTR CONDITION FALSE ######
    ####################################################################

    ###### Branch CTR if GE ######

    '4C800420': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x12345678 ),
            ),
        }
    ], # bgectr (branch CTR if 4*cr0+lt == 0)

    '4C800421': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x80000000 ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # bgectrl (branch CTR if 4*cr0+lt == 0)

    ###### Branch CTR if GT ######

    '4C810420': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x12345678 ),
            ),
        }
    ], # blectr (branch CTR if 4*cr0+gt == 0)

    '4C810421': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x40000000 ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xBFFFFFFF ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # blectrl (branch CTR if 4*cr0+gt == 0)

    ###### Branch CTR if NE ######

    '4C820420': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x12345678 ),
            ),
        }
    ], # bnectr (branch CTR if 4*cr0+eq == 0)

    '4C820421': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x20000000 ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xDFFFFFFF ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # bnectrl (branch CTR if 4*cr0+eq == 0)

    ###### Branch CTR if NS ######

    '4C830420': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x12345678 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x12345678 ),
            ),
        }
    ], # bnsctr (branch CTR if 4*cr0+so == 0)

    '4C830421': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0x10000000 ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0x12345678 ),
                ('CR', 0xEFFFFFFF ),
                ('CTR', 0xAAAAAAAA ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # bnsctrl (branch CTR if 4*cr0+so == 0)

    ############################################################################
    ###### Branch Conditional to LR (unsimplified, non-standard BO hints) ######
    ############################################################################

    '4D600020': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
                ('CTR', 0x00000001 ),
            ),
        }
    ], # bclr 0xB,lt,0x0 (branch LR if --CTR == 0 OR 4*cr0+lt == 1)

    '4D600021': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
                ('CTR', 0xFFFFFFFFFFFFFFFF ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x7FFFFFFF ),
                ('CTR', 0x00000001 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000000 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x80000000 ),
                ('CTR', 0x00000002 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
                ('CTR', 0x00000001 ),
            ),
        },
    ], # bclrl 0xB,lt,0x0 (branch LR if --CTR == 0 OR 4*cr0+lt == 1)

    ##################################################################
    ###### Branch Conditional (simplified) to LR CONDITION TRUE ######
    ##################################################################

    ###### Branch LR if LT ######

    '4D800020': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x7FFFFFFF ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x80000000 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
            ),
        }
    ], # bltlr (branch LR if 4*cr0+lt == 1)

    '4D800021': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x7FFFFFFF ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x80000000 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # bltlrl (branch LR if 4*cr0+lt == 1)

    ###### Branch LR if GT ######

    '4D810020': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xBFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x40000000 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
            ),
        }
    ], # bgtlr (branch LR if 4*cr0+lt == 1)

    '4D810021': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xBFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x40000000 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # bgtlrl (branch LR if 4*cr0+lt == 1)

    ###### Branch LR if EQ ######

    '4D820020': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xDFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x20000000 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
            ),
        }
    ], # beqlr (branch LR if 4*cr0+eq == 1)

    '4D820021': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xDFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x20000000 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # beqlrl (branch LR if 4*cr0+eq == 1)

    ###### Branch LR if SO ######

    '4D830020': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xEFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x10000000 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
            ),
        }
    ], # bsolr (branch LR if 4*cr0+so == 1)

    '4D830021': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xEFFFFFFF ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x10000000 ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # bsolrl (branch LR if 4*cr0+so == 1)

    ###################################################################
    ###### Branch Conditional (simplified) to LR CONDITION FALSE ######
    ###################################################################

    ###### Branch LR if GE ######

    '4C800020': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x80000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x7FFFFFFF ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
            ),
        }
    ], # bgelr (branch LR if 4*cr0+lt == 0)

    '4C800021': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x80000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x7FFFFFFF ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # bgelrl (branch LR if 4*cr0+lt == 0)

    ###### Branch LR if GT ######

    '4C810020': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x40000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xBFFFFFFF ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
            ),
        }
    ], # blelr (branch LR if 4*cr0+gt == 0)

    '4C810021': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x40000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xBFFFFFFF ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # blelrl (branch LR if 4*cr0+gt == 0)

    ###### Branch LR if NE ######

    '4C820020': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x20000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xDFFFFFFF ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
            ),
        }
    ], # bnelr (branch LR if 4*cr0+eq == 0)

    '4C820021': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x20000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xDFFFFFFF ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # bnelrl (branch LR if 4*cr0+eq == 0)

    ###### Branch LR if NS ######

    '4C830020': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x10000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0xAAAAAAAA ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xEFFFFFFF ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0xAAAAAAAA ),
            ),
        }
    ], # bnslr (branch LR if 4*cr0+so == 0)

    '4C830021': [
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0x10000000 ),
            ),
            'tests': (
                ('pc', 0x40004564 ),
                ('LR', 0x40004564 ),
            ),
        },
        {
            'setup': (
                ('pc', 0x40004560 ),
                ('LR', 0xAAAAAAAA ),
                ('CR', 0xEFFFFFFF ),
            ),
            'tests': (
                ('pc', 0xAAAAAAAA ),
                ('LR', 0x40004564 ),
            ),
        }
    ], # bnslrl (branch LR if 4*cr0+so == 0)

    # For the following load tests:
    # - r0 is the destination, which we initialize to 0
    # - r1 is the base address of the bytes that get written to r0
    'A8010400': [ # lha r0,0x400(r1) - load half word algebraic
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                (0x10000400, bytes.fromhex('8311'))
            ),
            'tests': (
                ('r0', 0xFFFFFFFFFFFF8311), # sign-extended with 1
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

    'A8000400': [ # lha r0,0x400(0) - load half word algebraic (with rA = 0)
        {
            'setup': (
                ('r0', 0),
                (0x400, bytes.fromhex('8311'))
            ),
            'tests': (
                ('r0', 0xFFFFFFFFFFFF8311), # sign-extended with 1
            )
        },

        {
            'setup': (
                ('r0', 0),
                (0x400, bytes.fromhex('4011'))
            ),
            'tests': (
                ('r0', 0x4011), # sign-extended with 0
            )
        }
    ],

    # Note that rA = 0 is an invalid form for loads with updates, so we don't test it
    'AC010400': [ # lhau r0,0x400(r1) - load half word algebraic with update
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                (0x10000400, bytes.fromhex('8311'))
            ),
            'tests': (
                ('r0', 0xFFFFFFFFFFFF8311), # sign-extended with 1
                ('r1', 0x10000400)
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
                ('r1', 0x10000400)
            )
        }
    ],

    '7C0112AE': [ # lhax r0,r1,r2 - load half word algebraic indexed
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                ('r2', 0x400),
                (0x10000400, bytes.fromhex('8311'))
            ),
            'tests': (
                ('r0', 0xFFFFFFFFFFFF8311), # sign-extended with 1
                ('r1', 0x10000000)
            )
        },

        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                ('r2', 0x400),
                (0x10000400, bytes.fromhex('4011'))
            ),
            'tests': (
                ('r0', 0x4011), # sign-extended with 0
                ('r1', 0x10000000)
            )
        }
    ],

    '7C0112AA': [ # lwax r0,r1,r2 - load word algebraic indexed
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                ('r2', 0x400),
                (0x10000400, bytes.fromhex('8C627311'))
            ),
            'tests': (
                ('r0', 0xFFFFFFFF8C627311), # sign-extended with 1
                ('r1', 0x10000000)
            )
        },

        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                ('r2', 0x400),
                (0x10000400, bytes.fromhex('7D9A4011'))
            ),
            'tests': (
                ('r0', 0x7D9A4011), # sign-extended with 0
                ('r1', 0x10000000)
            )
        }
    ],

    '7C0112EE': [ # lhaux r0,r1,r2 - load half word algebraic with update indexed
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                ('r2', 0x400),
                (0x10000400, bytes.fromhex('8311'))
            ),
            'tests': (
                ('r0', 0xFFFFFFFFFFFF8311), # sign-extended with 1
                ('r1', 0x10000400)
            )
        },

        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                ('r2', 0x400),
                (0x10000400, bytes.fromhex('4011'))
            ),
            'tests': (
                ('r0', 0x4011), # sign-extended with 0
                ('r1', 0x10000400)
            )
        }
    ],

    '7C0112EA': [ # lwaux r0,r1,r2 - load word algebraic with update indexed
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                ('r2', 0x400),
                (0x10000400, bytes.fromhex('8C627311'))
            ),
            'tests': (
                ('r0', 0xFFFFFFFF8C627311), # sign-extended with 1
                ('r1', 0x10000400)
            )
        },

        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                ('r2', 0x400),
                (0x10000400, bytes.fromhex('7D9A4011'))
            ),
            'tests': (
                ('r0', 0x7D9A4011), # sign-extended with 0
                ('r1', 0x10000400)
            )
        }
    ],

    'A4010400': [ # lhzu r0,0x400(r1) - load half word and zero with update
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                (0x10000400, bytes.fromhex('8311'))
            ),
            'tests': (
                ('r0', 0x8311),
                ('r1', 0x10000400)
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
                ('r1', 0x10000400)
            )
        }
    ],

    '84010400': [ # lwzu r0,0x400(r1) - load word and zero with update
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                (0x10000400, bytes.fromhex('8C627311'))
            ),
            'tests': (
                ('r0', 0x8C627311),
                ('r1', 0x10000400)
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
                ('r1', 0x10000400)
            )
        }
    ],

    'E8010401': [ # ldu r0,0x400(r1) - load doubleword with update
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                (0x10000400, bytes.fromhex('AB9371D0FEDCBA98'))
            ),
            'tests': (
                ('r0', 0xAB9371D0FEDCBA98),
                ('r1', 0x10000400)
            )
        },
    ],

    '7C01122E': [ # lhzx r0,r1,r2 - load half word and zero indexed
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                ('r2', 0x400),
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
                ('r2', 0x400),
                (0x10000400, bytes.fromhex('4011'))
            ),
            'tests': (
                ('r0', 0x4011),
                ('r1', 0x10000000)
            )
        }
    ],

    '7C01102E': [ # lwzx r0,r1,r2 - load word and zero indexed
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                ('r2', 0x400),
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
                ('r2', 0x400),
                (0x10000400, bytes.fromhex('7D9A4011'))
            ),
            'tests': (
                ('r0', 0x7D9A4011),
                ('r1', 0x10000000)
            )
        }
    ],

    '7C01102A': [ # ldx r0,r1,r2 - load doubleword indexed
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                ('r2', 0x400),
                (0x10000400, bytes.fromhex('AB9371D0FEDCBA98'))
            ),
            'tests': (
                ('r0', 0xAB9371D0FEDCBA98),
                ('r1', 0x10000000)
            )
        },
    ],

    '7C0110EE': [ # lbzux r0,r1,r2 - load byte and zero with update indexed
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                ('r2', 0x400),
                (0x10000400, bytes.fromhex('FB'))
            ),
            'tests': (
                ('r0', 0xFB),
                ('r1', 0x10000400)
            )
        },

        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                ('r2', 0x400),
                (0x10000400, bytes.fromhex('4C'))
            ),
            'tests': (
                ('r0', 0x4C),
                ('r1', 0x10000400)
            )
        }
    ],

    '7C01126E': [ # lhzux r0,r1,r2 - load half word and zero with update indexed
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                ('r2', 0x400),
                (0x10000400, bytes.fromhex('8311'))
            ),
            'tests': (
                ('r0', 0x8311),
                ('r1', 0x10000400)
            )
        },

        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                ('r2', 0x400),
                (0x10000400, bytes.fromhex('4011'))
            ),
            'tests': (
                ('r0', 0x4011),
                ('r1', 0x10000400)
            )
        }
    ],

    '7C01106E': [ # lwzux r0,r1,r2 - load word and zero with update indexed
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                ('r2', 0x400),
                (0x10000400, bytes.fromhex('8C627311'))
            ),
            'tests': (
                ('r0', 0x8C627311),
                ('r1', 0x10000400)
            )
        },

        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                ('r2', 0x400),
                (0x10000400, bytes.fromhex('7D9A4011'))
            ),
            'tests': (
                ('r0', 0x7D9A4011),
                ('r1', 0x10000400)
            )
        }
    ],

    '7C01106A': [ # ldux r0,r1,r2 - load doubleword with update indexed
        {
            'setup': (
                ('r0', 0),
                ('r1', 0x10000000),
                ('r2', 0x400),
                (0x10000400, bytes.fromhex('AB9371D0FEDCBA98'))
            ),
            'tests': (
                ('r0', 0xAB9371D0FEDCBA98),
                ('r1', 0x10000400)
            )
        },
    ],

    '9C010400': [ # stbu r0,0x400(r1) - store byte with update
        {
            'setup': (
                ('r0', 0xAB),
                ('r1', 0x10000000),
                (0x10000400, b"\x00")
            ),
            'tests': (
                (0x10000400, b"\xAB"),
                ('r1', 0x10000400)
            )
        },
    ],

    'B4010400': [ # sthu r0,0x400(r1) - store half word with update
        {
            'setup': (
                ('r0', 0xABDF),
                ('r1', 0x10000000),
                (0x10000400, bytes.fromhex('0000'))
            ),
            'tests': (
                (0x10000400, bytes.fromhex('ABDF')),
                ('r1', 0x10000400)
            )
        },
    ],

    '94010400': [ # stwu r0,0x400(r1) - store word with update
        {
            'setup': (
                ('r0', 0xABDF1539),
                ('r1', 0x10000000),
                (0x10000400, bytes.fromhex('00000000'))
            ),
            'tests': (
                (0x10000400, bytes.fromhex('ABDF1539')),
                ('r1', 0x10000400)
            )
        },
    ],

    'F8010401': [ # stdu r0,0x400(r1) - store doubleword with update
        {
            'setup': (
                ('r0', 0xABDF153977820C0B),
                ('r1', 0x10000000),
                (0x10000400, bytes.fromhex('0000000000000000'))
            ),
            'tests': (
                (0x10000400, bytes.fromhex('ABDF153977820C0B')),
                ('r1', 0x10000400)
            )
        },
    ],

    '7C0111AE': [ # stbx r0,r1,r2 - store byte indexed
        {
            'setup': (
                ('r0', 0xAB),
                ('r1', 0x10000000),
                ('r2', 0x400),
                (0x10000400, b"\x00")
            ),
            'tests': (
                (0x10000400, b"\xAB"),
                ('r1', 0x10000000)
            )
        },
    ],

    '7C01132E': [ # sthx r0,r1,r2 - store half word indexed
        {
            'setup': (
                ('r0', 0xABDF),
                ('r1', 0x10000000),
                ('r2', 0x400),
                (0x10000400, bytes.fromhex('0000'))
            ),
            'tests': (
                (0x10000400, bytes.fromhex('ABDF')),
                ('r1', 0x10000000)
            )
        },
    ],

    '7C01112E': [ # stwx r0,r1,r2 - store word indexed
        {
            'setup': (
                ('r0', 0xABDF1539),
                ('r1', 0x10000000),
                ('r2', 0x400),
                (0x10000400, bytes.fromhex('00000000'))
            ),
            'tests': (
                (0x10000400, bytes.fromhex('ABDF1539')),
                ('r1', 0x10000000)
            )
        },
    ],

    '7C01112A': [ # stdx r0,r1,r2 - store doubleword indexed
        {
            'setup': (
                ('r0', 0xABDF153977820C0B),
                ('r1', 0x10000000),
                ('r2', 0x400),
                (0x10000400, bytes.fromhex('0000000000000000'))
            ),
            'tests': (
                (0x10000400, bytes.fromhex('ABDF153977820C0B')),
                ('r1', 0x10000000)
            )
        },
    ],

    '7C0111EE': [ # stbux r0,r1,r2 - store byte with update indexed
        {
            'setup': (
                ('r0', 0xAB),
                ('r1', 0x10000000),
                ('r2', 0x400),
                (0x10000400, b"\x00")
            ),
            'tests': (
                (0x10000400, b"\xAB"),
                ('r1', 0x10000400)
            )
        },
    ],

    '7C01136E': [ # sthux r0,r1,r2 - store half word with update indexed
        {
            'setup': (
                ('r0', 0xABDF),
                ('r1', 0x10000000),
                ('r2', 0x400),
                (0x10000400, bytes.fromhex('0000'))
            ),
            'tests': (
                (0x10000400, bytes.fromhex('ABDF')),
                ('r1', 0x10000400)
            )
        },
    ],

    '7C01116E': [ # stwux r0,r1,r2 - store word with update indexed
        {
            'setup': (
                ('r0', 0xABDF1539),
                ('r1', 0x10000000),
                ('r2', 0x400),
                (0x10000400, bytes.fromhex('00000000'))
            ),
            'tests': (
                (0x10000400, bytes.fromhex('ABDF1539')),
                ('r1', 0x10000400)
            )
        },
    ],

    '7C01116A': [ # stdux r0,r1,r2 - store doubleword with update indexed
        {
            'setup': (
                ('r0', 0xABDF153977820C0B),
                ('r1', 0x10000000),
                ('r2', 0x400),
                (0x10000400, bytes.fromhex('0000000000000000'))
            ),
            'tests': (
                (0x10000400, bytes.fromhex('ABDF153977820C0B')),
                ('r1', 0x10000400)
            )
        },
    ],

    # These check the case where rD == rB
    '7C0100EE': [ # lbzux r0,r1,r0 - load byte and zero with update indexed
        {
            'setup': (
                ('r0', 0x400),
                ('r1', 0x10000000),
                (0x10000400, bytes.fromhex('FB'))
            ),
            'tests': (
                ('r0', 0xFB),
                ('r1', 0x10000400)
            )
        },
    ],

    '7C0102EE': [ # lhaux r0,r1,r0 - load half word algebraic with update indexed
        {
            'setup': (
                ('r0', 0x400),
                ('r1', 0x10000000),
                (0x10000400, bytes.fromhex('8311'))
            ),
            'tests': (
                ('r0', 0xFFFFFFFFFFFF8311), # sign-extended with 1
                ('r1', 0x10000400)
            )
        },
    ],

    # 'FC1EF82B': [ # ('FC1EF82B', 'fadd. f0,f30,f31')
    #     {
    #         'setup': (
    #             ('f30', 0x400921F9F01B866E), # 3.14159 (pi)
    #             ('f31', 0x3FF9E3736CDF266C), # 1.61803 (Golden Ratio)
    #             ('f0', 0x0),
    #             ('fpscr',0)
    #         ),
    #         'tests': (
    #             ('f0',0x401309d9d3458cd2),
    #             ('f30', 0x400921F9F01B866E), # 3.14159 (pi)
    #             ('f31', 0x3FF9E3736CDF266C), # 1.61803 (Golden Ratio) #4.75962
    #             ('fpscr', 0x40000)
    #         )
    #     },
    #     {
    #         'setup': (
    #             ('f30', 0x3FF199999999999A), 
    #             ('f31', 0x400199999999999A), # 
    #             ('f0', 0x0),
    #             ('fpscr',0)
    #         ),
    #         'tests': (
    #             ('f0',0x400a666666666667),
    #             ('fpscr',0x40000)
    #         )
    #     },
    #     {
    #         'setup': (
    #             ('f30', 0xBFF199999999999A), 
    #             ('f31', 0x400199999999999A), # 
    #             ('f0', 0x0),
    #             ('fpscr',0x0)
    #         ),
    #         'tests': (
    #             ('f0',0x3ff199999999999a),
    #             ('fpscr',0x40000)
    #         )
    #     },
    #     {
    #         'setup': (
    #             ('f30', 0xC00A666666666666), 
    #             ('f31', 0xC01199999999999A), # 
    #             ('f0', 0x0),
    #             ('fpscr',0)
    #         ),
    #         'tests': (
    #             ('f0',0xC01ECCCCCCCCCCCD),
    #             ('fpscr',0x80000)
    #         )
    #     },
    #     {
    #         'setup': (
    #             ('f30', 0), 
    #             ('f31', 0xC01199999999999A), # 
    #             ('f0', 0x0),
    #             ('fpscr',0)
    #         ),
    #         'tests': (
    #             ('f0',0xC01199999999999A),
    #             ('fpscr',0x80000)
    #         )
    #     },
    #     {
    #         'setup': (
    #             ('f30', 0), 
    #             ('f31', 0), # 
    #             ('f0', 0x0),
    #             ('fpscr',0)
    #         ),
    #         'tests': (
    #             ('f0',0x0),
    #             ('fpscr',0x20000)
    #         )
    #     },
    #     {
    #         'setup': (
    #             ('f30', FDNP), 
    #             ('f31', 0x3FF199999999999A), # 
    #             ('f0', 0x0),
    #             ('fpscr',0)
    #         ),
    #         'tests': (
    #             ('f0',0xfffc000000000001),
    #             ('fpscr',0x110000)
    #         )
    #     },
    # ], # ('FC1EF82A', 'fadd f0,f30,f31')

    'fc000800': [ # ('fc000800', 'fcmpu cr0,f0,f1')
        {
            'setup': (
                ('f0', 0x3FF199999999999A), # 
                ('f1', 0x3FF199999999999A), # 
                ('cr0', 0x0),
                ('fpscr',0),
                ('VXSANN', 0)
            ),
            'tests': (
                ('f0',0x3FF199999999999A),
                ('f1', 0x3FF199999999999A),
                ('cr0', 0b0010),
                ('VXSANN', 0),
                ('fpscr_FPCC', 0b0010)
            )
        },
        {
            'setup': (
                ('f0', 0x7FF8000000000001), # 
                ('f1', 0x3FF199999999999A), # 
                ('cr0', 0x0),
                ('fpscr',0),
                ('VXSANN', 0)
            ),
            'tests': (
                ('f0',0x7FF8000000000001),
                ('f1', 0x3FF199999999999A),
                ('cr0', 0b0001),
                ('VXSANN', 1),
                ('fpscr_FPCC', 0b0001)
            )
        },
        {
            'setup': (
                ('f0', FP_DOUBLE_NEG_QNAN), # 
                ('f1', 0x3FF199999999999A), # 
                ('cr0', 0x0),
                ('fpscr',0),
                ('VXSANN', 0)
            ),
            'tests': (
                ('f0',FP_DOUBLE_NEG_QNAN),
                ('f1', 0x3FF199999999999A),
                ('cr0', 0b0001),
                ('VXSANN', 1),
                ('fpscr_FPCC', 0b0001),
            )
        },
    ], # ('fc000800', 'fcmpu cr0,f0,f1')

    'fc000840': [ # ('fc000840', 'fcmpo cr0,f0,f1')
        {
            'setup': (
                ('f0', 0x3FF199999999999A), # 
                ('f1', 0x3FF199999999999A), # 
                ('cr0', 0x0),
                ('fpscr',0),
                ('VXSANN', 0)
            ),
            'tests': (
                ('f0',0x3FF199999999999A),
                ('f1', 0x3FF199999999999A),
                ('cr0', 0b0010),
                ('VXSANN', 0),
                ('fpscr_FPCC', 0b0010)
            )
        },
        {
            'setup': (
                ('f0', 0x7FF8000000000001), # 
                ('f1', 0x3FF199999999999A), # 
                ('cr0', 0x0),
                ('fpscr',0),
                ('VXSANN', 0)
            ),
            'tests': (
                ('f0',0x7FF8000000000001),
                ('f1', 0x3FF199999999999A),
                ('cr0', 0b0001),
                ('VXSANN', 1),
                ('fpscr_FPCC', 0b0001)
            )
        },
        {
            'setup': (
                ('f0', FP_DOUBLE_NEG_QNAN), # 
                ('f1', 0x3FF199999999999A), # 
                ('cr0', 0x0),
                ('fpscr',0),
                ('VXSANN', 0),
                ('fpscr_VXVC',0)
            ),
            'tests': (
                ('f0',FP_DOUBLE_NEG_QNAN),
                ('f1', 0x3FF199999999999A),
                ('cr0', 0b0001),
                ('VXSANN', 0),
                ('fpscr_FPCC', 0b0001),
                ('fpscr_VXVC',1)
            )
        },
        {
            'setup': (
                ('f0', FP_DOUBLE_NEG_SNAN), # 
                ('f1', 0x3FF199999999999A), # 
                ('cr0', 0x0),
                ('fpscr',0),
                ('VXSANN', 0),
                ('fpscr_VXVC',0),
                ('fpscr_VE',0)
            ),
            'tests': (
                ('f0',FP_DOUBLE_NEG_SNAN),
                ('f1', 0x3FF199999999999A),
                ('cr0', 0b0001),
                ('VXSANN', 1),
                ('fpscr_FPCC', 0b0001),
                ('fpscr_VXVC', 1)
            )
        },
        {
            'setup': (
                ('f0', FP_DOUBLE_NEG_SNAN), # 
                ('f1', 0x3FF199999999999A), # 
                ('cr0', 0x0),
                ('fpscr',0),
                ('VXSANN', 0),
                ('fpscr_VXVC',0),
                ('fpscr_VE',1)
            ),
            'tests': (
                ('f0',FP_DOUBLE_NEG_SNAN),
                ('f1', 0x3FF199999999999A),
                ('cr0', 0b0001),
                ('VXSANN', 1),
                ('fpscr_FPCC', 0b0001),
                ('fpscr_VXVC', 0)
            )
        },
    ], # ('fc000800', 'fcmpo cr0,f0,f1')

    # 'EC000831': [ # fres. f0,f1
    #     {
    #         'setup': (
    #             ('f0', 0),
    #             ('f1', 0x4010000000000000),
    #             ('fpscr', 0x0)
    #         ),
    #         'tests': (
    #             ('f0', 0x3FD0000000000000),
    #             ('f1', 0x4010000000000000),
    #             ('fpscr', 0x40000) #actual hardware is 0x4000
    #         )
    #     },
    #     # {
    #     #     'setup': (
    #     #         ('f0', 0),
    #     #         ('f1', 0x3FC2492492492494),
    #     #         ('fpscr', 0x0)
    #     #     ),
    #     #     'tests': (
    #     #         ('f0', 0x401c00ca80000000), # test result is hardware value.  Emlator value = 0x401bfffffffffffd
    #     #         ('f1', 0x3FC2492492492494),
    #     #         ('fpscr', 0x40000)
    #     #     )
    #     # },
    #     {
    #         'setup': (
    #             ('f0', 0),
    #             ('f1', 0xFFFC000000000000),
    #             ('fpscr', 0x0)
    #         ),
    #         'tests': (
    #             ('f0', 0xfffc000000000000), # rounding mode will change the result by one bit.
    #             ('f1', 0xFFFC000000000000),
    #             #('fpscr', 0x110000) #fpscr being incorrectrly set.  issue already made
    #         )
    #     },
        # {
        #     'setup': (
        #         ('f0', 0),
        #         ('f1', 0x7FFC000000000000),  needs functionality to accomodate NaN's
        #         ('fpscr', 0x0)
        #     ),
        #     'tests': (
        #         ('f0', 0x0), # 
        #         ('f1', 0x7FFC000000000000),
        #         ('fpscr', 0x110000)
        #     )
        # },
    # ], # fres. f0,f1

# 'fc1f265d': [ # (fc1f265d:  fctid. f0,f2)  Cannot confirm behavior on hardware.
#         {
#             'setup': (
#                 ('f0', _1p1), # 
#                 ('f2', _2p2), # 
#                 ('cr0', 0x0),
#                 ('fpscr',0),
#                 ('VXSANN', 0)
#             ),
#             'tests': (
#                 ('f0',0x),
#                 ('f2', 0x),
#                 ('cr0', 0b0010),
#                 ('VXSANN', 0),
#                 ('fpscr_FPCC', 0b0010)
#             )
#         },
#         {
#             'setup': (
#                 ('f0', 0x7FF8000000000001), # 
#                 ('f2', 0x3Ff299999999999A), # 
#                 ('cr0', 0x0),
#                 ('fpscr',0),
#                 ('VXSANN', 0)
#             ),
#             'tests': (
#                 ('f0',0x7FF8000000000001),
#                 ('f2', 0x3Ff299999999999A),
#                 ('cr0', 0b0001),
#                 ('VXSANN', 1),
#                 ('fpscr_FPCC', 0b0001)
#             )
#         },
#         {
#             'setup': (
#                 ('f0', FP_DOUBLE_NEG_QNAN), # 
#                 ('f2', 0x3Ff299999999999A), # 
#                 ('cr0', 0x0),
#                 ('fpscr',0),
#                 ('VXSANN', 0),
#                 ('fpscr_VXVC',0)
#             ),
#             'tests': (
#                 ('f0',FP_DOUBLE_NEG_QNAN),
#                 ('f2', 0x3Ff299999999999A),
#                 ('cr0', 0b0001),
#                 ('VXSANN', 0),
#                 ('fpscr_FPCC', 0b0001),
#                 ('fpscr_VXVC',1)
#             )
#         },
#         {
#             'setup': (
#                 ('f0', FP_DOUBLE_NEG_SNAN), # 
#                 ('f2', 0x3Ff299999999999A), # 
#                 ('cr0', 0x0),
#                 ('fpscr',0),
#                 ('VXSANN', 0),
#                 ('fpscr_VXVC',0),
#                 ('fpscr_VE',0)
#             ),
#             'tests': (
#                 ('f0',FP_DOUBLE_NEG_SNAN),
#                 ('f2', 0x3Ff299999999999A),
#                 ('cr0', 0b0001),
#                 ('VXSANN', 1),
#                 ('fpscr_FPCC', 0b0001),
#                 ('fpscr_VXVC', 0)
#             )
#         },
#     ], # (fc1f265d:  fctid. f0,f2)



    'EC1EF82B': [ # ('EC1EF82B', 'fadds. f0,f30,f31') #needs rounding still
        {
            'setup': (
                ('f30', _1p1),
                ('f31', _1p1),
                ('f0', 0x0),
                ('fpscr',0),
                ('cr1', 0b0000)
            ),
            'tests': (
                ('f0', 0x4001999980000000),
                ('fpscr', 0x40000), # actual hardware 0x82064000
                ('cr1', 0b0000)     # Actual hardware = 0b1000 
            )
        },
        {
            'setup': (
                ('f30', 0x3FF55555547044B7), # 1.33333333
                ('f31', 0x3FF55555547044B7), # 1.33333333
                ('f0', 0x0),
                ('fpscr',0),
                ('cr1', 0b0000)
            ),
            'tests': (
                ('f0',0x4005555540000000), # 2.66666666
                ('fpscr',0x40000),
                ('cr1', 0b0000)
            )
        },
        {
            'setup': (
                ('f30', 0x400921fb54442d18),
                ('f31', 0x400921fb54442d18),
                ('f0', 0x0),
                ('fpscr',0),
                ('cr1', 0b0000)
            ),
            'tests': (
                ('f0', 0x401921fb40000000),
                ('fpscr', 0x40000), # actual hardware 0x82064000
                ('cr1', 0b0000)     # Actual hardware = 0b1000 
            )
        },
    ],

    # '200222c0': [ # ('200222c0', 'efsadd r0,r1,r2')
    #     {
    #         'setup': (
    #             ('r1', 0x400C000000000000), # 3.5
    #             ('r2', 0x400C000000000000), # 3.5
    #             ('r0', 0x0),
    #             ('fpscr',0)
    #         ),
    #         'tests': (
    #             ('r0',0x401C000000000000), #7
    #         )
    #     },
        # {
        #     'setup': (
        #         ('f30', 0x3FF55555547044B7), # 1.33333333
        #         ('f31', 0x3FF55555547044B7), # 1.33333333
        #         ('f0', 0x0),
        #         ('fpscr',0)
        #     ),
        #     'tests': (
        #         ('f0',0x402AAAAB00000000), # 2.66666666
        #     )
        # },
    #  ],

    'fc011029': [ # fsub. f0,f1, f2
        {
            'setup': (
                ('f0', 0),
                ('f1', _2p2),
                ('f2', _2p2),
                ('fpscr', 0x0)
            ),
            'tests': (
                ('f0', 0),
                ('fpscr', 0x20000) # Actual hardware is 0x2000 
                ),
        },
        {
            'setup': (
                ('f0', 0),
                ('f1', _1p1),
                ('f2', _2p2),
                ('fpscr', 0x0)
            ),
            'tests': (
                ('f0', 0xbff199999999999a),
                ('fpscr', 0x80000) # noisy = 0x8000 
                ),
        },
    ],    # fsub. f0,f1, f2

    'ec011029': [ # fsub. f0,f1, f2
        {
            'setup': (
                ('f0', 0),
                ('f1', _2p2),
                ('f2', _2p2),
                ('fpscr', 0x0)
            ),
            'tests': (
                ('f0', 0),
                ('fpscr', 0x20000) # Actual hardware is 0x2000 
                ),
        },
        {
            'setup': (
                ('f0', 0),
                ('f1', _1p1),
                ('f2', _2p2),
                ('fpscr', 0x0)
            ),
            'tests': (
                ('f0', 0xbff1999980000000),
                ('fpscr', 0x80000) # noisy = 0x8000 
                ),
        },
    ],    # fsub. f0,f1, f2

    'fc1ffc8f': [ # mffs. f0
        {
            'setup': (
                ('f0', 0),
                ('fpscr', 0x12345678),
                ('cr1', 0b0000)
            ),
            'tests': (
                ('f0', 0x12345678),
                ('fpscr', 0x12345678),
                ('cr1',0b0001) 
                ),
        },
        {
            'setup': (
                ('f0', 0x12345678),
                ('fpscr', 0x0),
                ('cr1',0b1000)
            ),
            'tests': (
                ('f0', 0x0),
                ('fpscr', 0x0), 
                ('cr1',0b0000)
                ),
        },
    ],    # fsub. f0,f1, f2

    'fc000a11': [ # fabs. f0,f1
        {
            'setup': (
                ('f1', 0xbff199999999999a),
                ('fpscr', 0x0),
                ('cr1', 0b0000)
            ),
            'tests': (
                ('f0', _1p1),
                ('fpscr', 0x40000),
                ('cr1',0b0000) 
                ),
        },
        {
            'setup': (
                ('f1', 0x12345678),
                ('fpscr', 0x0),
                ('cr1',0b0000)
            ),
            'tests': (
                ('f0', 0x12345678),
                ('fpscr', 0x140000), 
                ('cr1',0b0000)
                ),
        },
    ],    # fsub. f0,f1, f2

    'c8010000': [ #  lfd f0,0x0(r1)
        {
            'setup': (
                ('f0', 0),
                ('r1', 0x10000000),
                (0x10000000, bytes.fromhex('3Ff299999999999A'))
            ),
            'tests': (
                ('f0', 0x3Ff299999999999A), 
                ('r1', 0x10000000),
            )
        },
    ],
    
    'c8010001': [ #  lfd f0,0x1(r1)
        {
            'setup': (
                ('f0', 0x0),
                ('r1', 0x10000000),
                (0x10000000 + 1, bytes.fromhex('3Ff299999999999A'))
            ),
            'tests': (
                ('f0', 0x3Ff299999999999A), 
                ('r1', 0x10000000),
            )
        },
    ],

    'c0010000': [ #  lfs f0,0x0(r1) needs single precision conversion stuff
        {
            'setup': (
                ('f0', 0x0),
                ('r1', 0x10000000),
                (0x10000000, bytes.fromhex('3Ff299999999999A'))
            ),
            'tests': (
                ('f0', 0x3ffe533320000000), 
                ('r1', 0x10000000),
            )
        },
    ],

    # '7c011647': [ #  lfddx f0,r1,r2 needs decoding help.  Too many opers
    #     {
    #         'setup': (
    #             ('f0', 0x0),
    #             ('r1', 0x10000000),
    #             ('r2', 0xaaaaaaaa),
    #             (0x10000000, bytes.fromhex('3Ff299999999999A'))
    #         ),
    #         'tests': (
    #             ('f0', 0x3Ff299999999999A), 
    #             ('r1', 0x10000000),
    #         )
    #     },
    # ], # lfddx f0,r1,r2

        '10221800': [ # vaddubm v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x000102030405060708090a0b0c0d0e0f),
                ('v3', 0x000102030405060708090a0b0c0d0e0f),
            ),
            'tests': (
                ('v1', 0x00020406080a0c0e10121416181a1c1e),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x000102030405060708090a0b0c0d0e0f),
                ('v3', 0x0f0e0d0c0b0a09080706050403020100),
            ),
            'tests': (
                ('v1', 0x0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x000102030405060708090a0b0c0d0e0f),
                ('v3', 0xffffffffffffffffffffffffffffffff),
            ),
            'tests': (
                ('v1', 0xff000102030405060708090a0b0c0d0e),
            )
        },
    ],

    '10221840': [ # vadduhm v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x000102030405060708090a0b0c0d0e0f),
                ('v3', 0x000102030405060708090a0b0c0d0e0f),
            ),
            'tests': (
                ('v1', 0x00020406080a0c0e10121416181a1c1e),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x000102030405060708090a0b0c0d0e0f),
                ('v3', 0x0f0e0d0c0b0a09080706050403020100),
            ),
            'tests': (
                ('v1', 0x0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x000102030405060708090a0b0c0d0e0f),
                ('v3', 0xffffffffffffffffffffffffffffffff),
            ),
            'tests': (
                ('v1', 0x000002020404060608080a0a0c0c0e0e),
            )
        },
    ],

    '10221880': [ # vadduwm v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x000102030405060708090a0b0c0d0e0f),
                ('v3', 0x000102030405060708090a0b0c0d0e0f),
            ),
            'tests': (
                ('v1', 0x00020406080a0c0e10121416181a1c1e),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x000102030405060708090a0b0c0d0e0f),
                ('v3', 0x0f0e0d0c0b0a09080706050403020100),
            ),
            'tests': (
                ('v1', 0x0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x000102030405060708090a0b0c0d0e0f),
                ('v3', 0xffffffffffffffffffffffffffffffff),
            ),
            'tests': (
                ('v1', 0x000102020405060608090a0a0c0d0e0e),
            )
        },
    ],

    '10221C04': [ # vand v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x0123456789abcdeffedcba9876543210),
                ('v3', 0xff00ff00ff00ff00ff00ff00ff00ff00),
            ),
            'tests': (
                ('v1', 0x010045008900cd00fe00ba0076003200),
            )
        },
    ],

    '10221C44': [ # vandc v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x0123456789abcdeffedcba9876543210),
                ('v3', 0xff00ff00ff00ff00ff00ff00ff00ff00),
            ),
            'tests': (
                ('v1', 0x0023006700ab00ef00dc009800540010),
            )
        },
    ],

    '10221C84': [ # vor v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x0123456789abcdeffedcba9876543210),
                ('v3', 0xff00ff00ff00ff00ff00ff00ff00ff00),
            ),
            'tests': (
                ('v1', 0xff23ff67ffabffefffdcff98ff54ff10),
            )
        },
    ],

    '10221D04': [ # vnor v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x0123456789abcdeffedcba9876543210),
                ('v3', 0xff00ff00ff00ff00ff00ff00ff00ff00),
            ),
            'tests': (
                ('v1', 0x00dc0098005400100023006700ab00ef),
            )
        },
    ],

    '10221A00': [ # vaddubs v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x000102030405060708090a0b0c0d0e0f),
                ('v3', 0x000102030405060708090a0b0c0d0e0f),
                ('VSCR', 0),
            ),
            'tests': (
                ('v1', 0x00020406080a0c0e10121416181a1c1e),
                ('VSCR', 0),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x000102030405060708090a0b0c0d0e0f),
                ('v3', 0x0f0e0d0c0b0a09080706050403020100),
                ('VSCR', 0),
            ),
            'tests': (
                ('v1', 0x0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f),
                ('VSCR', 0),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x000102030405060708090a0b0c0d0e0f),
                ('v3', 0xffffffffffffffffffffffffffffffff),
                ('VSCR', 0),
            ),
            'tests': (
                ('v1', 0xffffffffffffffffffffffffffffffff),
                ('VSCR', 1),
            )
        },
    ],

    '10221A40': [ # vadduhs v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x000102030405060708090a0b0c0d0e0f),
                ('v3', 0x000102030405060708090a0b0c0d0e0f),
                ('VSCR', 0),
            ),
            'tests': (
                ('v1', 0x00020406080a0c0e10121416181a1c1e),
                ('VSCR', 0),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x000102030405060708090a0b0c0d0e0f),
                ('v3', 0x0f0e0d0c0b0a09080706050403020100),
                ('VSCR', 0),
            ),
            'tests': (
                ('v1', 0x0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f),
                ('VSCR', 0),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x000102030405060708090a0b0c0d0e0f),
                ('v3', 0xffffffffffffffffffffffffffffffff),
                ('VSCR', 0),
            ),
            'tests': (
                ('v1', 0xffffffffffffffffffffffffffffffff),
                ('VSCR', 1),
            )
        },
    ],

    '10221A80': [ # vadduws v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x000102030405060708090a0b0c0d0e0f),
                ('v3', 0x000102030405060708090a0b0c0d0e0f),
                ('VSCR', 0),
            ),
            'tests': (
                ('v1', 0x00020406080a0c0e10121416181a1c1e),
                ('VSCR', 0),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x000102030405060708090a0b0c0d0e0f),
                ('v3', 0x0f0e0d0c0b0a09080706050403020100),
                ('VSCR', 0),
            ),
            'tests': (
                ('v1', 0x0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f),
                ('VSCR', 0),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x000102030405060708090a0b0c0d0e0f),
                ('v3', 0xffffffffffffffffffffffffffffffff),
                ('VSCR', 0),
            ),
            'tests': (
                ('v1', 0xffffffffffffffffffffffffffffffff),
                ('VSCR', 1),
            )
        },
    ],

    '10221980': [ # vaddcuw v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x000102030405060708090a0b0c0d0e0f),
                ('v3', 0xffffffff04050607ffffffff0c0d0e0f),
            ),
            'tests': (
                ('v1', 0x00000001000000000000000100000000),
            )
        },
    ],

    '10221B00': [ # vaddsbs v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x70ce70c07576cdcbccbcdc67570c07ec),
                ('v3', 0x70ce70c07576cdcbccbcdc67570c07ec),
                ('VSCR', 0),
            ),
            'tests': (
                ('v1', 0x7f9c7f807f7f9a969880b87f7f180ed8),
                ('VSCR', 1),
            )
        },
    ],

    '10221B40': [ # vaddshs v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x70ce70c07576cdcbccbcdc67570c07ec),
                ('v3', 0x70ce70c07576cdcbccbcdc67570c07ec),
                ('VSCR', 0),
            ),
            'tests': (
                ('v1', 0x7fff7fff7fff9b969978b8ce7fff0fd8),
                ('VSCR', 1),
            )
        },
    ],

    '10221B80': [ # vaddsws v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x70ce70c07576cdcbccbcdc67570c07ec),
                ('v3', 0x70ce70c07576cdcbccbcdc67570c07ec),
                ('VSCR', 0),
            ),
            'tests': (
                ('v1', 0x7fffffff7fffffff9979b8ce7fffffff),
                ('VSCR', 1),
            )
        },
    ],

    '10200604': [ # mfvscr  v1
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('VSCR', 0x1),
            ),
            'tests': (
                ('v1', 0x1),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('VSCR', 0xffffffff),
            ),
            'tests': (
                ('v1', 0x10001),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('VSCR', 0xfefe),
            ),
            'tests': (
                ('v1', 0x0),
            )
        },
    ],

    '10000E44': [ # mtvscr  v1
        {
            'setup': (
                ('v1', 0xffffffffffffffffffffffffffffffff),
                ('VSCR', 0xabababab),
            ),
            'tests': (
                ('VSCR', 0x10001),
            )
        },
        {
            'setup': (
                ('v1', 0xffffffff),
                ('VSCR', 0xabababab),
            ),
            'tests': (
                ('VSCR', 0x10001),
            )
        },
        {
            'setup': (
                ('v1', 0x0),
                ('VSCR', 0xabababab),
            ),
            'tests': (
                ('VSCR', 0x0),
            )
        },
    ],

    '10221D02': [ # vavgsb  v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x000102030405060708090a0b0c0d0e0f),
                ('v3', 0x000102030405060708090a0b0c0d0e0f),
            ),
            'tests': (
                ('v1', 0x000102030405060708090a0b0c0d0e0f),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x000102030405060708090a0b0c0d0e0f),
                ('v3', 0x0f0e0d0c0b0a09080706050403020100),
            ),
            'tests': (
                ('v1', 0x08080808080808080808080808080808),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xfbfbfbfbfbfbfbfbfbfbfbfbfbfbfbfb),
                ('v3', 0xf9f9f9f9f9f9f9f9f9f9f9f9f9f9f9f9),
            ),
            'tests': (
                ('v1', 0xfafafafafafafafafafafafafafafafa),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x40404040404040404040404040404040),
                ('v3', 0xe0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0),
            ),
            'tests': (
                ('v1', 0x10101010101010101010101010101010),
            )
        },
    ],

    '10221D42': [ # vavgsh  v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x102030405060708090a0b0c0d0e0f),
                ('v3', 0x102030405060708090a0b0c0d0e0f),
            ),
            'tests': (
                ('v1', 0x102030405060708090a0b0c0d0e0f),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x102030405060708090a0b0c0d0e0f),
                ('v3', 0xf0e0d0c0b0a09080706050403020100),
            ),
            'tests': (
                ('v1', 0x7880788078807880788078807880788),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xfbfbfbfbfbfbfbfbfbfbfbfbfbfbfbfb),
                ('v3', 0xf9f9f9f9f9f9f9f9f9f9f9f9f9f9f9f9),
            ),
            'tests': (
                ('v1', 0xfafafafafafafafafafafafafafafafa),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x40404040404040404040404040404040),
                ('v3', 0xe0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0),
            ),
            'tests': (
                ('v1', 0x10901090109010901090109010901090),
            )
        },
    ],

    '10221D82': [ # vavgsw  v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x102030405060708090a0b0c0d0e0f),
                ('v3', 0x102030405060708090a0b0c0d0e0f),
            ),
            'tests': (
                ('v1', 0x102030405060708090a0b0c0d0e0f),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x102030405060708090a0b0c0d0e0f),
                ('v3', 0xf0e0d0c0b0a09080706050403020100),
            ),
            'tests': (
                ('v1', 0x7878788078787880787878807878788),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xfbfbfbfbfbfbfbfbfbfbfbfbfbfbfbfb),
                ('v3', 0xf9f9f9f9f9f9f9f9f9f9f9f9f9f9f9f9),
            ),
            'tests': (
                ('v1', 0xfafafafafafafafafafafafafafafafa),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x40404040404040404040404040404040),
                ('v3', 0xe0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0),
            ),
            'tests': (
                ('v1', 0x10909090109090901090909010909090),
            )
        },
    ],

    '10221C02': [ # vavgub  v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x102030405060708090a0b0c0d0e0f),
                ('v3', 0x102030405060708090a0b0c0d0e0f),
            ),
            'tests': (
                ('v1', 0x102030405060708090a0b0c0d0e0f),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x102030405060708090a0b0c0d0e0f),
                ('v3', 0xf0e0d0c0b0a09080706050403020100),
            ),
            'tests': (
                ('v1', 0x8080808080808080808080808080808),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xfbfbfbfbfbfbfbfbfbfbfbfbfbfbfbfb),
                ('v3', 0xf9f9f9f9f9f9f9f9f9f9f9f9f9f9f9f9),
            ),
            'tests': (
                ('v1', 0xfafafafafafafafafafafafafafafafa),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x40404040404040404040404040404040),
                ('v3', 0xe0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0),
            ),
            'tests': (
                ('v1', 0x90909090909090909090909090909090),
            )
        },
    ],

    '10221C42': [ # vavguh  v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x102030405060708090a0b0c0d0e0f),
                ('v3', 0x102030405060708090a0b0c0d0e0f),
            ),
            'tests': (
                ('v1', 0x102030405060708090a0b0c0d0e0f),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x102030405060708090a0b0c0d0e0f),
                ('v3', 0xf0e0d0c0b0a09080706050403020100),
            ),
            'tests': (
                ('v1', 0x7880788078807880788078807880788),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xfbfbfbfbfbfbfbfbfbfbfbfbfbfbfbfb),
                ('v3', 0xf9f9f9f9f9f9f9f9f9f9f9f9f9f9f9f9),
            ),
            'tests': (
                ('v1', 0xfafafafafafafafafafafafafafafafa),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x40404040404040404040404040404040),
                ('v3', 0xe0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0),
            ),
            'tests': (
                ('v1', 0x90909090909090909090909090909090),
            )
        },
    ],

    '10221C82': [ # vavguw  v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x102030405060708090a0b0c0d0e0f),
                ('v3', 0x102030405060708090a0b0c0d0e0f),
            ),
            'tests': (
                ('v1', 0x102030405060708090a0b0c0d0e0f),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x102030405060708090a0b0c0d0e0f),
                ('v3', 0xf0e0d0c0b0a09080706050403020100),
            ),
            'tests': (
                ('v1', 0x7878788078787880787878807878788),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xfbfbfbfbfbfbfbfbfbfbfbfbfbfbfbfb),
                ('v3', 0xf9f9f9f9f9f9f9f9f9f9f9f9f9f9f9f9),
            ),
            'tests': (
                ('v1', 0xfafafafafafafafafafafafafafafafa),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x40404040404040404040404040404040),
                ('v3', 0xe0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0),
            ),
            'tests': (
                ('v1', 0x90909090909090909090909090909090),
            )
        },
    ],

    '7C21100E': [ # lvebx   v1,r1,r2
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x400),
                ('r2', 0x10000000),
                (0x10000400, bytes.fromhex('abcdef12')),
            ),
            'tests': (
                ('v1', 0xab000000000000000000000000000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x401),
                ('r2', 0x10000000),
                (0x10000401, bytes.fromhex('abcdef12')),
            ),
            'tests': (
                ('v1', 0xab0000000000000000000000000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x44f),
                ('r2', 0x10000000),
                (0x1000044f, bytes.fromhex('abcdef12')),
            ),
            'tests': (
                ('v1', 0xab),
            )
        },
    ],

    '7C21104E': [ # lvehx   v1,r1,r2
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x400),
                ('r2', 0x10000000),
                (0x10000400, bytes.fromhex('abcdef12')),
            ),
            'tests': (
                ('v1', 0xabcd0000000000000000000000000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x401),
                ('r2', 0x10000000),
                (0x10000400, bytes.fromhex('abcdef12')),
            ),
            'tests': (
                ('v1', 0xabcd0000000000000000000000000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x44f),
                ('r2', 0x10000000),
                (0x1000044e, bytes.fromhex('abcdef12')),
            ),
            'tests': (
                ('v1', 0xabcd),
            )
        },
    ],

    '7C21108E': [ # lvewx   v1,r1,r2
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x400),
                ('r2', 0x10000000),
                (0x10000400, bytes.fromhex('abcdef12')),
            ),
            'tests': (
                ('v1', 0xabcdef12000000000000000000000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x401),
                ('r2', 0x10000000),
                (0x10000400, bytes.fromhex('abcdef12')),
            ),
            'tests': (
                ('v1', 0xabcdef12000000000000000000000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x44f),
                ('r2', 0x10000000),
                (0x1000044c, bytes.fromhex('abcdef12')),
            ),
            'tests': (
                ('v1', 0xabcdef12),
            )
        },
    ],

    '7C2110CE': [ # lvx     v1,r1,r2
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x400),
                ('r2', 0x10000000),
                (0x10000400, bytes.fromhex('dfac022520210fcd08072021dfbf8487')),
            ),
            'tests': (
                ('v1', 0xdfac022520210fcd08072021dfbf8487),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x401),
                ('r2', 0x10000000),
                (0x10000400, bytes.fromhex('dfac022520210fcd08072021dfbf8487')),
            ),
            'tests': (
                ('v1', 0xdfac022520210fcd08072021dfbf8487),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x44f),
                ('r2', 0x10000000),
                (0x10000440, bytes.fromhex('dfac022520210fcd08072021dfbf8487')),
            ),
            'tests': (
                ('v1', 0xdfac022520210fcd08072021dfbf8487),
            )
        },
    ],

    '7C2112CE': [ # lvxl    v1,r1,r2
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x400),
                ('r2', 0x10000000),
                (0x10000400, bytes.fromhex('dfac022520210fcd08072021dfbf8487')),
            ),
            'tests': (
                ('v1', 0xdfac022520210fcd08072021dfbf8487),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x401),
                ('r2', 0x10000000),
                (0x10000400, bytes.fromhex('dfac022520210fcd08072021dfbf8487')),
            ),
            'tests': (
                ('v1', 0xdfac022520210fcd08072021dfbf8487),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x44f),
                ('r2', 0x10000000),
                (0x10000440, bytes.fromhex('dfac022520210fcd08072021dfbf8487')),
            ),
            'tests': (
                ('v1', 0xdfac022520210fcd08072021dfbf8487),
            )
        },
    ],

    '7C21100C': [ # lvsl    v1,r1,r2
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x0),
                ('r2', 0x0),
            ),
            'tests': (
                ('v1', 0x102030405060708090a0b0c0d0e0f),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x1),
                ('r2', 0x0),
            ),
            'tests': (
                ('v1', 0x102030405060708090a0b0c0d0e0f10),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x0),
                ('r2', 0x2),
            ),
            'tests': (
                ('v1', 0x2030405060708090a0b0c0d0e0f1011),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x4),
                ('r2', 0x1),
            ),
            'tests': (
                ('v1', 0x5060708090a0b0c0d0e0f1011121314),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0xf),
                ('r2', 0xf),
            ),
            'tests': (
                ('v1', 0xe0f101112131415161718191a1b1c1d),
            )
        },
    ],

    '7C21104C': [ # lvsr    v1,r1,r2
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x0),
                ('r2', 0x0),
            ),
            'tests': (
                ('v1', 0x101112131415161718191a1b1c1d1e1f),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x1),
                ('r2', 0x0),
            ),
            'tests': (
                ('v1', 0xf101112131415161718191a1b1c1d1e),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x0),
                ('r2', 0x2),
            ),
            'tests': (
                ('v1', 0xe0f101112131415161718191a1b1c1d),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x4),
                ('r2', 0x1),
            ),
            'tests': (
                ('v1', 0xb0c0d0e0f101112131415161718191a),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0xf),
                ('r2', 0xf),
            ),
            'tests': (
                ('v1', 0x2030405060708090a0b0c0d0e0f1011),
            )
        },
    ],

    '7C21110E': [ # stvebx  v1,r1,r2
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x400),
                ('r2', 0x10010000),
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010400, bytes.fromhex('abdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            )
        },
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x401),
                ('r2', 0x10010000),
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010400, bytes.fromhex('dfacdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            )
        },
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x44f),
                ('r2', 0x10010000),
                (0x10010440, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010440, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdf87')),
            )
        },
    ],

    '7C21114E': [ # stvehx  v1,r1,r2
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x400),
                ('r2', 0x10010000),
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010400, bytes.fromhex('abacdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            )
        },
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x401),
                ('r2', 0x10010000),
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010400, bytes.fromhex('abacdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            )
        },
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x44f),
                ('r2', 0x10010000),
                (0x10010440, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010440, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdf8487')),
            )
        },
    ],

    '7C21118E': [ # stvewx  v1,r1,r2
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x400),
                ('r2', 0x10010000),
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010400, bytes.fromhex('abac0225dfdfdfdfdfdfdfdfdfdfdfdf')),
            )
        },
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x401),
                ('r2', 0x10010000),
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010400, bytes.fromhex('abac0225dfdfdfdfdfdfdfdfdfdfdfdf')),
            )
        },
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x44f),
                ('r2', 0x10010000),
                (0x10010440, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010440, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfbf8487')),
            )
        },
    ],

    '7C2111CE': [ # stvx    v1,r1,r2
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x400),
                ('r2', 0x10010000),
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010400, bytes.fromhex('abac022520210fcd08072021dfbf8487')),
            )
        },
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x401),
                ('r2', 0x10010000),
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010400, bytes.fromhex('abac022520210fcd08072021dfbf8487')),
            )
        },
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x44f),
                ('r2', 0x10010000),
                (0x10010440, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010440, bytes.fromhex('abac022520210fcd08072021dfbf8487')),
            )
        },
    ],

    '7C2113CE': [ # stvxl   v1,r1,r2
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x400),
                ('r2', 0x10010000),
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010400, bytes.fromhex('abac022520210fcd08072021dfbf8487')),
            )
        },
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x401),
                ('r2', 0x10010000),
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010400, bytes.fromhex('abac022520210fcd08072021dfbf8487')),
            )
        },
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x44f),
                ('r2', 0x10010000),
                (0x10010440, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010440, bytes.fromhex('abac022520210fcd08072021dfbf8487')),
            )
        },
    ],

    '10221B06': [ # vcmpgtsb v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f),
                ('v3', 0xbd9cd03caec992b2f24a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0xffffffffffffffffffffffffffffffff),
                ('CR', 0x00000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x80808080808080808080808080808080),
                ('v3', 0xbd9cd03caec992b2f24a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0x00000000000000000000000000000000),
                ('CR', 0x00000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x00000000000000000000000000000000),
                ('v3', 0xbd9cd03caec992b2f24a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0xffffff00ffffffffff00ff00ff00ff00),
                ('CR', 0x00000000),
            )
        },
    ],

    '10221F06': [ # vcmpgtsb. v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f),
                ('v3', 0xbd9cd03caec992b2f24a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0xffffffffffffffffffffffffffffffff),
                ('CR', 0x00000080),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x80808080808080808080808080808080),
                ('v3', 0xbd9cd03caec992b2f24a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0x00000000000000000000000000000000),
                ('CR', 0x00000020),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x00000000000000000000000000000000),
                ('v3', 0xbd9cd03caec992b2f24a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0xffffff00ffffffffff00ff00ff00ff00),
                ('CR', 0x00000000),
            )
        },
    ],

    '10221B46': [ # vcmpgtsh v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x7fff7fff7fff7fff7fff7fff7fff7fff),
                ('v3', 0xbd9c703caec992b2f24a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0xffffffffffffffffffffffffffffffff),
                ('CR', 0x00000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x80008000800080008000800080008000),
                ('v3', 0xbd9c703caec992b2f24a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0x00000000000000000000000000000000),
                ('CR', 0x00000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x00000000000000000000000000000000),
                ('v3', 0xbd9c703caec992b2f24a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0xffff0000ffffffffffffffffffffffff),
                ('CR', 0x00000000),
            )
        },
    ],

    '10221F46': [ # vcmpgtsh. v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x7fff7fff7fff7fff7fff7fff7fff7fff),
                ('v3', 0xbd9c703caec992b2f24a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0xffffffffffffffffffffffffffffffff),
                ('CR', 0x00000080),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x80008000800080008000800080008000),
                ('v3', 0xbd9c703caec992b2f24a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0x00000000000000000000000000000000),
                ('CR', 0x00000020),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x00000000000000000000000000000000),
                ('v3', 0xbd9c703caec992b2f24a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0xffff0000ffffffffffffffffffffffff),
                ('CR', 0x00000000),
            )
        },
    ],

    '10221B86': [ # vcmpgtsw v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x7fffffff7fffffff7fffffff7fffffff),
                ('v3', 0xbd9c703c7ec992b2f24a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0xffffffffffffffffffffffffffffffff),
                ('CR', 0x00000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x80000000800000008000000080000000),
                ('v3', 0xbd9c703c7ec992b2f24a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0x00000000000000000000000000000000),
                ('CR', 0x00000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x00000000000000000000000000000000),
                ('v3', 0xbd9c703c7ec992b2f24a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0xffffffff00000000ffffffffffffffff),
                ('CR', 0x00000000),
            )
        },
    ],

    '10221F86': [ # vcmpgtsw. v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x7fffffff7fffffff7fffffff7fffffff),
                ('v3', 0xbd9c703c7ec992b2f24a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0xffffffffffffffffffffffffffffffff),
                ('CR', 0x00000080),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x80000000800000008000000080000000),
                ('v3', 0xbd9c703c7ec992b2f24a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0x00000000000000000000000000000000),
                ('CR', 0x00000020),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x00000000000000000000000000000000),
                ('v3', 0xbd9c703c7ec992b2f24a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0xffffffff00000000ffffffffffffffff),
                ('CR', 0x00000000),
            )
        },
    ],

    '10221A06': [ # vcmpgtub v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xffffffffffffffffffffffffffffffff),
                ('v3', 0xbd9cd03caec992b2f24a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0xffffffffffffffffffffffffffffffff),
                ('CR', 0x00000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x00000000000000000000000000000000),
                ('v3', 0xbd9cd03caec992b2f24a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0x00000000000000000000000000000000),
                ('CR', 0x00000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f),
                ('v3', 0xbd9cd03caec992b2f24a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0xff0000000000ff00ff00ff00ff),
                ('CR', 0x00000000),
            )
        },
    ],

    '10221E06': [ # vcmpgtub. v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xffffffffffffffffffffffffffffffff),
                ('v3', 0xbd9cd03caec992b2f24a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0xffffffffffffffffffffffffffffffff),
                ('CR', 0x00000080),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x00000000000000000000000000000000),
                ('v3', 0xbd9cd03caec992b2f24a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0x00000000000000000000000000000000),
                ('CR', 0x00000020),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f),
                ('v3', 0xbd9cd03caec992b2f24a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0xff0000000000ff00ff00ff00ff),
                ('CR', 0x00000000),
            )
        },
    ],

    '10221A46': [ # vcmpgtuh v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xffffffffffffffffffffffffffffffff),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0xffffffffffffffffffffffffffffffff),
                ('CR', 0x00000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x00000000000000000000000000000000),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0x00000000000000000000000000000000),
                ('CR', 0x00000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x7fff7fff7fff7fff7fff7fff7fff7fff),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0x0000000000000000ffff000000000000),
                ('CR', 0x00000000),
            )
        },
    ],

    '10221E46': [ # vcmpgtuh. v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xffffffffffffffffffffffffffffffff),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0xffffffffffffffffffffffffffffffff),
                ('CR', 0x00000080),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x00000000000000000000000000000000),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0x00000000000000000000000000000000),
                ('CR', 0x00000020),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x7fff7fff7fff7fff7fff7fff7fff7fff),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0x0000000000000000ffff000000000000),
                ('CR', 0x00000000),
            )
        },
    ],

    '10221A86': [ # vcmpgtuw v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xffffffffffffffffffffffffffffffff),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0xffffffffffffffffffffffffffffffff),
                ('CR', 0x00000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x00000000000000000000000000000000),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0x00000000000000000000000000000000),
                ('CR', 0x00000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x7fffffff7fffffff7fffffff7fffffff),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0x0000000000000000ffffffff00000000),
                ('CR', 0x00000000),
            )
        },
    ],

    '10221E86': [ # vcmpgtuw. v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xffffffffffffffffffffffffffffffff),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0xffffffffffffffffffffffffffffffff),
                ('CR', 0x00000080),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x00000000000000000000000000000000),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0x00000000000000000000000000000000),
                ('CR', 0x00000020),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x7fffffff7fffffff7fffffff7fffffff),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0x0000000000000000ffffffff00000000),
                ('CR', 0x00000000),
            )
        },
    ],

    '10221806': [ # vcmpequb v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0xffffffffffffffffffffffffffffffff),
                ('CR', 0x00000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x00000000000000000000000000000000),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0x00000000000000000000000000000000),
                ('CR', 0x00000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('v3', 0xbd9cd03c00000000624a841700000000),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0xffffffff00000000ffffffff00000000),
                ('CR', 0x00000000),
            )
        },
    ],

    '10221C06': [ # vcmpequb. v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0xffffffffffffffffffffffffffffffff),
                ('CR', 0x00000080),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x00000000000000000000000000000000),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0x00000000000000000000000000000000),
                ('CR', 0x00000020),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('v3', 0xbd9cd03c00000000624a841700000000),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0xffffffff00000000ffffffff00000000),
                ('CR', 0x00000000),
            )
        },
    ],

    '10221846': [ # vcmpequh v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0xffffffffffffffffffffffffffffffff),
                ('CR', 0x00000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x00000000000000000000000000000000),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0x00000000000000000000000000000000),
                ('CR', 0x00000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('v3', 0xbd9cd03c00000000624a841700000000),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0xffffffff00000000ffffffff00000000),
                ('CR', 0x00000000),
            )
        },
    ],

    '10221C46': [ # vcmpequh. v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0xffffffffffffffffffffffffffffffff),
                ('CR', 0x00000080),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x00000000000000000000000000000000),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0x00000000000000000000000000000000),
                ('CR', 0x00000020),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('v3', 0xbd9cd03c00000000624a841700000000),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0xffffffff00000000ffffffff00000000),
                ('CR', 0x00000000),
            )
        },
    ],

    '10221886': [ # vcmpequw v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0xffffffffffffffffffffffffffffffff),
                ('CR', 0x00000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x00000000000000000000000000000000),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0x00000000000000000000000000000000),
                ('CR', 0x00000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('v3', 0xbd9cd03c00000000624a841700000000),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0xffffffff00000000ffffffff00000000),
                ('CR', 0x00000000),
            )
        },
    ],

    '10221C86': [ # vcmpequw. v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0xffffffffffffffffffffffffffffffff),
                ('CR', 0x00000080),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x00000000000000000000000000000000),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0x00000000000000000000000000000000),
                ('CR', 0x00000020),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('v3', 0xbd9cd03c00000000624a841700000000),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0xffffffff00000000ffffffff00000000),
                ('CR', 0x00000000),
            )
        },
    ],

    '10221902': [ # vmaxsb v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x22222222444444448888888866666666),
                ('v3', 0x111111115555555577777777ffffffff),
            ),
            'tests': (
                ('v1', 0x22222222555555557777777766666666),
            )
        },
    ],

    '10221942': [ # vmaxsh v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x22222222444444448888888866666666),
                ('v3', 0x111111115555555577777777ffffffff),
            ),
            'tests': (
                ('v1', 0x22222222555555557777777766666666),
            )
        },
    ],

    '10221982': [ # vmaxsw v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x22222222444444448888888866666666),
                ('v3', 0x111111115555555577777777ffffffff),
            ),
            'tests': (
                ('v1', 0x22222222555555557777777766666666),
            )
        },
    ],

    '10221802': [ # vmaxub v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x22222222444444448888888866666666),
                ('v3', 0x111111115555555577777777ffffffff),
            ),
            'tests': (
                ('v1', 0x222222225555555588888888ffffffff),
            )
        },
    ],

    '10221842': [ # vmaxuh v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x22222222444444448888888866666666),
                ('v3', 0x111111115555555577777777ffffffff),
            ),
            'tests': (
                ('v1', 0x222222225555555588888888ffffffff),
            )
        },
    ],

    '10221882': [ # vmaxuw v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x22222222444444448888888866666666),
                ('v3', 0x111111115555555577777777ffffffff),
            ),
            'tests': (
                ('v1', 0x222222225555555588888888ffffffff),
            )
        },
    ],

    '10221B02': [ # vminsb v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x22222222444444448888888866666666),
                ('v3', 0x111111115555555577777777ffffffff),
            ),
            'tests': (
                ('v1', 0x111111114444444488888888ffffffff),
            )
        },
    ],

    '10221B42': [ # vminsh v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x22222222444444448888888866666666),
                ('v3', 0x111111115555555577777777ffffffff),
            ),
            'tests': (
                ('v1', 0x111111114444444488888888ffffffff),
            )
        },
    ],

    '10221B82': [ # vminsw v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x22222222444444448888888866666666),
                ('v3', 0x111111115555555577777777ffffffff),
            ),
            'tests': (
                ('v1', 0x111111114444444488888888ffffffff),
            )
        },
    ],

    '10221A02': [ # vminub v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x22222222444444448888888866666666),
                ('v3', 0x111111115555555577777777ffffffff),
            ),
            'tests': (
                ('v1', 0x11111111444444447777777766666666),
            )
        },
    ],

    '10221A42': [ # vminuh v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x22222222444444448888888866666666),
                ('v3', 0x111111115555555577777777ffffffff),
            ),
            'tests': (
                ('v1', 0x11111111444444447777777766666666),
            )
        },
    ],

    '10221A82': [ # vminuw v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x22222222444444448888888866666666),
                ('v3', 0x111111115555555577777777ffffffff),
            ),
            'tests': (
                ('v1', 0x11111111444444447777777766666666),
            )
        },
    ],

    '10221922': [ # vmladduhm v1,v2,v3,v4
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x22223333111144448888555500006666),
                ('v3', 0x111144440000666677770000ffff2222),
                ('v4', 0x33336666222200009999111122223333),
            ),
            'tests': (
                ('v1', 0xb9758bf222224b1848d11111222258bf),
            )
        },
    ],

    '1022180C': [ # vmrghb  v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x11111111222222223333333344444444),
                ('v3', 0x55555555666666667777777788888888),
            ),
            'tests': (
                ('v1', 0x11551155115511552266226622662266),
            )
        },
    ],

    '1022184C': [ # vmrghh  v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x11111111222222223333333344444444),
                ('v3', 0x55555555666666667777777788888888),
            ),
            'tests': (
                ('v1', 0x11115555111155552222666622226666),
            )
        },
    ],

    '1022188C': [ # vmrghw  v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x11111111222222223333333344444444),
                ('v3', 0x55555555666666667777777788888888),
            ),
            'tests': (
                ('v1', 0x11111111555555552222222266666666),
            )
        },
    ],

    '1022190C': [ # vmrglb  v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x11111111222222223333333344444444),
                ('v3', 0x55555555666666667777777788888888),
            ),
            'tests': (
                ('v1', 0x33773377337733774488448844884488),
            )
        },
    ],

    '1022194C': [ # vmrglh  v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x11111111222222223333333344444444),
                ('v3', 0x55555555666666667777777788888888),
            ),
            'tests': (
                ('v1', 0x33337777333377774444888844448888),
            )
        },
    ],

    '1022198C': [ # vmrglw  v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x11111111222222223333333344444444),
                ('v3', 0x55555555666666667777777788888888),
            ),
            'tests': (
                ('v1', 0x33333333777777774444444488888888),
            )
        },
    ],

    '10221925': [ # vmsummbm v1,v2,v3,v4
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x2222cccc111144448888555500006666),
                ('v3', 0x11114444eeee666677770000ffff2222),
                ('v4', 0x33336666222200009999111122223333),
            ),
            'tests': (
                ('v1', 0x33334f4a222255cc9998a18122224e4b),
            )
        },
    ],

    '10221928': [ # vmsumshm v1,v2,v3,v4
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x2222cccc111144448888555500006666),
                ('v3', 0x11114444eeee666677770000ffff2222),
                ('v4', 0x33336666222200009999111122223333),
            ),
            'tests': (
                ('v1', 0x27d282d83c4cf6e661d8c0492fc958bf),
            )
        },
    ],

    '10221924': [ # vmsumubm v1,v2,v3,v4
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x2222cccc111144448888555500006666),
                ('v3', 0x11114444eeee666677770000ffff2222),
                ('v4', 0x33336666222200009999111122223333),
            ),
            'tests': (
                ('v1', 0x3333d74a222255cc99998f8122224e4b),
            )
        },
    ],

    '10221926': [ # vmsumuhm v1,v2,v3,v4
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x2222cccc111144448888555500006666),
                ('v3', 0x11114444eeee666677770000ffff2222),
                ('v4', 0x33336666222200009999111122223333),
            ),
            'tests': (
                ('v1', 0x6c1682d84d5df6e6d94fc0492fc958bf),
            )
        },
    ],

    '10221929': [ # vmsumshs v1,v2,v3,v4
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x2222cccc111144448888555500006666),
                ('v3', 0x11114444eeee666677770000ffff2222),
                ('v4', 0x33336666222200009999111122223333),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x27d282d83c4cf6e6800000002fc958bf),
                ('VSCR', 0x1),
            )
        },
    ],

    '10221927': [ # vmsumuhs v1,v2,v3,v4
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x2222cccc111144448888555500006666),
                ('v3', 0x11114444eeee666677770000ffff2222),
                ('v4', 0x33336666222200009999111122223333),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x6c1682d84d5df6e6d94fc0492fc958bf),
                ('VSCR', 0x0),
            )
        },
    ],

    '10221B08': [ # vmulesb v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x2222cccc111144448888555500006666),
                ('v3', 0x11114444eeee666677770000ffff2222),
            ),
            'tests': (
                ('v1', 0x242f230fece1b18c838000000000d8c),
            )
        },
    ],

    '10221B48': [ # vmulesh v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x2222cccc111144448888555500006666),
                ('v3', 0x11114444eeee666677770000ffff2222),
            ),
            'tests': (
                ('v1', 0x2468642fedcabcec83faf3800000000),
            )
        },
    ],

    '10221A08': [ # vmuleub v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x2222cccc111144448888555500006666),
                ('v3', 0x11114444eeee666677770000ffff2222),
            ),
            'tests': (
                ('v1', 0x24236300fce1b183f38000000000d8c),
            )
        },
    ],

    '10221A48': [ # vmuleuh v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x2222cccc111144448888555500006666),
                ('v3', 0x11114444eeee666677770000ffff2222),
            ),
            'tests': (
                ('v1', 0x24686420fedabce3fb6af3800000000),
            )
        },
    ],

    '10221908': [ # vmulosb v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x2222cccc111144448888555500006666),
                ('v3', 0x11114444eeee666677770000ffff2222),
            ),
            'tests': (
                ('v1', 0x242f230fece1b18c838000000000d8c),
            )
        },
    ],

    '10221948': [ # vmulosh v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x2222cccc111144448888555500006666),
                ('v3', 0x11114444eeee666677770000ffff2222),
            ),
            'tests': (
                ('v1', 0xf25896301b4e4b18000000000da7258c),
            )
        },
    ],

    '10221808': [ # vmuloub v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x2222cccc111144448888555500006666),
                ('v3', 0x11114444eeee666677770000ffff2222),
            ),
            'tests': (
                ('v1', 0x24236300fce1b183f38000000000d8c),
            )
        },
    ],

    '10221848': [ # vmulouh v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x2222cccc111144448888555500006666),
                ('v3', 0x11114444eeee666677770000ffff2222),
            ),
            'tests': (
                ('v1', 0x369c96301b4e4b18000000000da7258c),
            )
        },
    ],

    '1022192B': [ # vperm   v1,v2,v3,v4
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x202122232425262728292a2b2c2d2e2f),
                ('v3', 0x303132333435363738393a3b3c3d3e3f),
                ('v4', 0x11418101615191a1c1c1c13081d1b0e),
            ),
            'tests': (
                ('v1', 0x213438303635393a3c3c3c33283d3b2e),
            )
        },
    ],

    '10221B0E': [ # vpkpx   v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x202122232425262728292a2b2c2d2e2f),
                ('v3', 0x303132333435363738393a3b3c3d3e3f),
            ),
            'tests': (
                ('v1', 0x1084108414a514a518c618c61ce71ce7),
            )
        },
    ],

    '1022198E': [ # vpkshss v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xd874007f4dd1ca86949e9fb41a72f609),
                ('v3', 0x6131b9696d5feddcd382007517165cde),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x807f7f8080807f807f807f8080757f7f),
                ('VSCR', 0x1),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x10002000300040005000600070008),
                ('v3', 0x10002000300040005000600070007f),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x102030405060708102030405060707f),
                ('VSCR', 0x0),
            )
        },
    ],

    '1022190E': [ # vpkshus v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xd874007f4dd1ca86949e9fb41a72f609),
                ('v3', 0x6131b9696d5feddcd382007517165cde),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x007fff000000ff00ff00ff000075ffff),
                ('VSCR', 0x1),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x00010002000300040005000600070008),
                ('v3', 0x00100020003000400050006000700080),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x01020304050607081020304050607080),
                ('VSCR', 0x0),
            )
        },
    ],

    '102219CE': [ # vpkswss v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xd874007f4dd1ca86949e9fb41a72f609),
                ('v3', 0x6131b9696d5feddcd382007517165cde),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x80007fff80007fff7fff7fff80007fff),
                ('VSCR', 0x1),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x00000001000000020000000300000004),
                ('v3', 0x00001000000020000000300000004000),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x10002000300041000200030004000),
                ('VSCR', 0x0),
            )
        },
    ],

    '1022194E': [ # vpkswus v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xd874007f4dd1ca86949e9fb41a72f609),
                ('v3', 0x6131b9696d5feddcd382007517165cde),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0xffff0000ffffffffffff0000ffff),
                ('VSCR', 0x1),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x1000000020000000300000004),
                ('v3', 0x1000000020000000300000004000),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x10002000300041000200030004000),
                ('VSCR', 0x0),
            )
        },
    ],

    '1022180E': [ # vpkuhum v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xd874007f4dd1ca86949e9fb41a72f609),
                ('v3', 0x6131b9696d5feddcd382007517165cde),
            ),
            'tests': (
                ('v1', 0x747fd1869eb4720931695fdc827516de),
            )
        },
    ],

    '1022188E': [ # vpkuhus v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xd874007f4dd1ca86949e9fb41a72f609),
                ('v3', 0x6131b9696d5feddcd382007517165cde),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0xff7fffffffffffffffffffffff75ffff),
                ('VSCR', 0x1),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x00000001000000020000000300000004),
                ('v3', 0x0010002000300040005000600070007f),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x0001000200030004102030405060707f),
                ('VSCR', 0x0),
            )
        },
    ],

    '1022184E': [ # vpkuwum v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xd874007f4dd1ca86949e9fb41a72f609),
                ('v3', 0x6131b9696d5feddcd382007517165cde),
            ),
            'tests': (
                ('v1', 0x07fca869fb4f609b969eddc00755cde),
            )
        },
    ],

    '102218CE': [ # vpkuwus v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xd874007f4dd1ca86949e9fb41a72f609),
                ('v3', 0x6131b9696d5feddcd382007517165cde),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0xffffffffffffffffffffffffffffffff),
                ('VSCR', 0x1),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x00000001000000020000000300000004),
                ('v3', 0x00001000000020000000300000004000),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x00010002000300041000200030004000),
                ('VSCR', 0x0),
            )
        },
    ],

    '10221804': [ # vrlb    v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x112233445566778899aabbccddeeff),
                ('v3', 0x102030405060708090a0b0c0d0e0f),
            ),
            'tests': (
                ('v1', 0x22889944aa99bb8833aaddccbbbbff),
            )
        },
    ],

    '10221844': [ # vrlh    v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x112233445566778899aabbccddeeff),
                ('v3', 0x102030405060708090a0b0c0d0e0f),
            ),
            'tests': (
                ('v1', 0x2211998aa83bb33311dd55b99bf77f),
            )
        },
    ],

    '10221884': [ # vrlw    v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x112233445566778899aabbccddeeff),
                ('v3', 0x102030405060708090a0b0c0d0e0f),
            ),
            'tests': (
                ('v1', 0x8911982ab33ba2cd55dc44f77fe66e),
            )
        },
    ],

    '102219C4': [ # vsl     v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xdfac022520210fcd08072021dfbf8487),
                ('v3', 0x0),
            ),
            'tests': (
                ('v1', 0xdfac022520210fcd08072021dfbf8487),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xdfac022520210fcd08072021dfbf8487),
                ('v3', 0x01010101010101010101010101010101),
            ),
            'tests': (
                ('v1', 0xbf58044a40421f9a100e4043bf7f090e),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xdfac022520210fcd08072021dfbf8487),
                ('v3', 0x07070707070707070707070707070707),
            ),
            'tests': (
                ('v1', 0xd60112901087e684039010efdfc24380),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xdfac022520210fcd08072021dfbf8487),
                ('v3', 0x0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f),
            ),
            'tests': (
                ('v1', 0xd60112901087e684039010efdfc24380),
            )
        },
    ],

    '10221904': [ # vslb    v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x00112233445566778899aabbccddeeff),
                ('v3', 0x000102030405060708090a0b0c0d0e0f),
            ),
            'tests': (
                ('v1', 0x0022889840a080808832a8d8c0a08080),
            )
        },
    ],

    '10221944': [ # vslh    v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x00112233445566778899aabbccddeeff),
                ('v3', 0x000102030405060708090a0b0c0d0e0f),
            ),
            'tests': (
                ('v1', 0x002211988aa03b803200d800a0008000),
            )
        },
    ],

    '10221984': [ # vslw    v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x00112233445566778899aabbccddeeff),
                ('v3', 0x000102030405060708090a0b0c0d0e0f),
            ),
            'tests': (
                ('v1', 0x008911982ab33b80cd55d800f77f8000),
            )
        },
    ],

    '10221AC4': [ # vsr     v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xdfac022520210fcd08072021dfbf8487),
                ('v3', 0x0),
            ),
            'tests': (
                ('v1', 0xdfac022520210fcd08072021dfbf8487),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xdfac022520210fcd08072021dfbf8487),
                ('v3', 0x1010101010101010101010101010101),
            ),
            'tests': (
                ('v1', 0x6fd60112901087e684039010efdfc243),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xdfac022520210fcd08072021dfbf8487),
                ('v3', 0x7070707070707070707070707070707),
            ),
            'tests': (
                ('v1', 0x1bf58044a40421f9a100e4043bf7f09),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xdfac022520210fcd08072021dfbf8487),
                ('v3', 0xf0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f),
            ),
            'tests': (
                ('v1', 0x1bf58044a40421f9a100e4043bf7f09),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xefac022520210fcd08072021dfbf8487),
                ('v3', 0x7070707070707070707070707070707),
            ),
            'tests': (
                ('v1', 0x1df58044a40421f9a100e4043bf7f09),
            )
        },
    ],

    '10221B04': [ # vsrab   v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x00112233445566778899aabbccddeeff),
                ('v3', 0x000102030405060708090a0b0c0d0e0f),
            ),
            'tests': (
                ('v1', 0x000808060402010088cceaf7fcfeffff),
            )
        },
    ],

    '10221B44': [ # vsrah   v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x00112233445566778899aabbccddeeff),
                ('v3', 0x000102030405060708090a0b0c0d0e0f),
            ),
            'tests': (
                ('v1', 0x00080446022200ccffc4fff5fffeffff),
            )
        },
    ],

    '10221B84': [ # vsraw   v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x00112233445566778899aabbccddeeff),
                ('v3', 0x000102030405060708090a0b0c0d0e0f),
            ),
            'tests': (
                ('v1', 0x000224460088aaccfff11335ffff99bb),
            )
        },
    ],

    '10221A04': [ # vsrb    v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x00112233445566778899aabbccddeeff),
                ('v3', 0x000102030405060708090a0b0c0d0e0f),
            ),
            'tests': (
                ('v1', 0x0008080604020100884c2a170c060301),
            )
        },
    ],

    '10221A44': [ # vsrh    v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x00112233445566778899aabbccddeeff),
                ('v3', 0x000102030405060708090a0b0c0d0e0f),
            ),
            'tests': (
                ('v1', 0x00080446022200cc0044001500060001),
            )
        },
    ],

    '10221A84': [ # vsrw    v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x00112233445566778899aabbccddeeff),
                ('v3', 0x000102030405060708090a0b0c0d0e0f),
            ),
            'tests': (
                ('v1', 0x000224460088aacc00111335000199bb),
            )
        },
    ],

'1022182C': [ # vsldoi  v1,v2,v3,0
    {
        'setup': (
            ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
            ('v2', 0x102030405060708090a0b0c0d0e0f),
            ('v3', 0x101112131415161718191a1b1c1d1e1f),
        ),
        'tests': (
            ('v1', 0x102030405060708090a0b0c0d0e0f),
        )
    },
],

    '1022182C': [ # vsldoi  v1,v2,v3,0
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x102030405060708090a0b0c0d0e0f),
                ('v3', 0x101112131415161718191a1b1c1d1e1f),
            ),
            'tests': (
                ('v1', 0x102030405060708090a0b0c0d0e0f),
            )
        },
    ],

    '1022186C': [ # vsldoi  v1,v2,v3,1
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x000102030405060708090a0b0c0d0e0f),
                ('v3', 0x101112131415161718191a1b1c1d1e1f),
            ),
            'tests': (
                ('v1', 0x0102030405060708090a0b0c0d0e0f10),
            )
        },
    ],

    '10221BEC': [ # vsldoi  v1,v2,v3,15
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x000102030405060708090a0b0c0d0e0f),
                ('v3', 0x101112131415161718191a1b1c1d1e1f),
            ),
            'tests': (
                ('v1', 0x0f101112131415161718191a1b1c1d1e),
            )
        },
    ],

    '10221C0C': [ # vslo    v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x000102030405060708090a0b0c0d0e0f),
                ('v3', 0x00000000000000000000000000000000),
            ),
            'tests': (
                ('v1', 0x102030405060708090a0b0c0d0e0f),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x000102030405060708090a0b0c0d0e0f),
                ('v3', 0x00000000000000000000000000000030),
            ),
            'tests': (
                ('v1', 0x60708090a0b0c0d0e0f000000000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x000102030405060708090a0b0c0d0e0f),
                ('v3', 0x00000000000000000000000000000078),
            ),
            'tests': (
                ('v1', 0x0f000000000000000000000000000000),
            )
        },
    ],

    '10221C4C': [ # vsro    v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x000102030405060708090a0b0c0d0e0f),
                ('v3', 0x00000000000000000000000000000000),
            ),
            'tests': (
                ('v1', 0x000102030405060708090a0b0c0d0e0f),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x000102030405060708090a0b0c0d0e0f),
                ('v3', 0x00000000000000000000000000000030),
            ),
            'tests': (
                ('v1', 0x000000000000000010203040506070809),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x000102030405060708090a0b0c0d0e0f),
                ('v3', 0x00000000000000000000000000000078),
            ),
            'tests': (
                ('v1', 0x00000000000000000000000000000000),
            )
        },
    ],

    '1022192A': [ # vsel    v1,v2,v3,v4
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x9ca74c44585af074f763e435a6687f75),
                ('v3', 0x68ac172bbe8ac4161556bf14a68318ea),
                ('v4', 0x4c72c083f597302040dda69952af7750),
            ),
            'tests': (
                ('v1', 0xd8a50c47bccac054b776e634a6c31865),
            )
        },
    ],

    '1026120C': [ # vspltb  v1,v2,6
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x9ca74c44585af074f763e435a6687f75),
            ),
            'tests': (
                ('v1', 0xf0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0),
            )
        },
    ],

    '1026124C': [ # vsplth  v1,v2,6
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x9ca74c44585af074f763e435a6687f75),
            ),
            'tests': (
                ('v1', 0xa668a668a668a668a668a668a668a668),
            )
        },
    ],

    '1026128C': [ # vsplth  v1,v2,6 -- 6 is too big, but it gets masked
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x9ca74c44585af074f763e435a6687f75),
            ),
            'tests': (
                ('v1', 0xf763e435f763e435f763e435f763e435),
            )
        },
    ],

    '1028030C': [ # vspltisb v1,8
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
            ),
            'tests': (
                ('v1', 0x08080808080808080808080808080808),
            )
        },
    ],

    '1030030C': [ # vspltisb v1,-16
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
            ),
            'tests': (
                ('v1', 0xf0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0),
            )
        },
    ],

    '1028034C': [ # vspltish v1,8
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
            ),
            'tests': (
                ('v1', 0x00080008000800080008000800080008),
            )
        },
    ],

    '1030034C': [ # vspltish v1,-16
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
            ),
            'tests': (
                ('v1', 0xfff0fff0fff0fff0fff0fff0fff0fff0),
            )
        },
    ],

    '1028038C': [ # vspltisw v1,8
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
            ),
            'tests': (
                ('v1', 0x00000008000000080000000800000008),
            )
        },
    ],

    '1030038C': [ # vspltisw v1,-16
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
            ),
            'tests': (
                ('v1', 0xfffffff0fffffff0fffffff0fffffff0),
            )
        },
    ],

    '10221D80': [ # vsubcuw v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x000102030405060708090a0b0c0d0e0f),
                ('v3', 0xffffffff04050607ffffffff0c0d0e0f),
            ),
            'tests': (
                ('v1', 0x00000000000000010000000000000001),
            )
        },
    ],

    '10221F00': [ # vsubsbs v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x80808080222222227f7f7f7f44444444),
                ('v3', 0x0202020277777777fefefefe66666666),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x80808080abababab7f7f7f7fdededede),
                ('VSCR', 0x1),
            )
        },
    ],

    '10221F40': [ # vsubshs v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x80808080222222227f7f7f7f44444444),
                ('v3', 0x0202020277777777fefefefe66666666),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x80008000aaabaaab7fff7fffdddeddde),
                ('VSCR', 0x1),
            )
        },
    ],

    '10221F80': [ # vsubsws v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x80808080222222227f7f7f7f44444444),
                ('v3', 0x0202020277777777fefefefe66666666),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x80000000aaaaaaab7fffffffddddddde),
                ('VSCR', 0x1),
            )
        },
    ],

    '10221C00': [ # vsububm v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x80808080222222227f7f7f7f44444444),
                ('v3', 0x0202020277777777fefefefe66666666),
            ),
            'tests': (
                ('v1', 0x7e7e7e7eabababab81818181dededede),
            )
        },
    ],

    '10221C40': [ # vsubuhm v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x80808080222222227f7f7f7f44444444),
                ('v3', 0x0202020277777777fefefefe66666666),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x7e7e7e7eaaabaaab80818081dddeddde),
            )
        },
    ],

    '10221C80': [ # vsubuwm v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x80808080222222227f7f7f7f44444444),
                ('v3', 0x0202020277777777fefefefe66666666),
            ),
            'tests': (
                ('v1', 0x7e7e7e7eaaaaaaab80808081ddddddde),
            )
        },
    ],

    '10221E00': [ # vsububs v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x80808080222222227f7f7f7f44444444),
                ('v3', 0x0202020277777777fefefefe66666666),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x7e7e7e7e000000000000000000000000),
                ('VSCR', 0x1),
            )
        },
    ],

    '10221E40': [ # vsubuhs v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x80808080222222227f7f7f7f44444444),
                ('v3', 0x0202020277777777fefefefe66666666),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x7e7e7e7e000000000000000000000000),
                ('VSCR', 0x1),
            )
        },
    ],

    '10221E80': [ # vsubuws v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x80808080222222227f7f7f7f44444444),
                ('v3', 0x0202020277777777fefefefe66666666),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x7e7e7e7e000000000000000000000000),
                ('VSCR', 0x1),
            )
        },
    ],

    '10221F88': [ # vsumsws v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x00000001000000010000000100000001),
                ('v3', 0x00000001000000010000000100000001),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x5),
                ('VSCR', 0x0),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x3fffffff3fffffff3fffffff3fffffff),
                ('v3', 0x3fffffff3fffffff3fffffff3fffffff),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x7fffffff),
                ('VSCR', 0x1),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v3', 0x80000000800000008000000080000000),
                ('v2', 0x80000000800000008000000080000000),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x80000000),
                ('VSCR', 0x1),
            )
        },
    ],

    '10221E88': [ # vsum2sws v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v3', 0x00000001000000010000000100000001),
                ('v2', 0x00000001000000010000000100000001),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x00000000000000030000000000000003),
                ('VSCR', 0x0),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x3fffffff3fffffff3fffffff3fffffff),
                ('v3', 0x3fffffff3fffffff3fffffff3fffffff),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x000000007fffffff000000007fffffff),
                ('VSCR', 0x1),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v3', 0x80000000800000008000000080000000),
                ('v2', 0x80000000800000008000000080000000),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x00000000800000000000000080000000),
                ('VSCR', 0x1),
            )
        },
    ],

    '10221F08': [ # vsum4sbs v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x1000000010000000100000001),
                ('v3', 0x1000000010000000100000001),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x2000000020000000200000002),
                ('VSCR', 0x0),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x3fffffff3fffffff3fffffff3fffffff),
                ('v3', 0x3fffffff3fffffff3fffffff3fffffff),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x4000003b4000003b4000003b4000003b),
                ('VSCR', 0x0),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v3', 0x80000000800000008000000080000000),
                ('v2', 0x80000000800000008000000080000000),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x80000000800000008000000080000000),
                ('VSCR', 0x1),
            )
        },
    ],

    '10221E48': [ # vsum4shs v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x1000000010000000100000001),
                ('v3', 0x1000000010000000100000001),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x2000000020000000200000002),
                ('VSCR', 0x0),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x3fffffff3fffffff3fffffff3fffffff),
                ('v3', 0x3fffffff3fffffff3fffffff3fffffff),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x40003ffd40003ffd40003ffd40003ffd),
                ('VSCR', 0x0),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v3', 0x80000000800000008000000080000000),
                ('v2', 0x80000000800000008000000080000000),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x80000000800000008000000080000000),
                ('VSCR', 0x1),
            )
        },
    ],

    '10221E08': [ # vsum4ubs v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x1000000010000000100000001),
                ('v3', 0x1000000010000000100000001),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x2000000020000000200000002),
                ('VSCR', 0x0),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x3fffffff3fffffff3fffffff3fffffff),
                ('v3', 0x3fffffff3fffffff3fffffff3fffffff),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x4000033b4000033b4000033b4000033b),
                ('VSCR', 0x0),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v3', 0x80000000800000008000000080000000),
                ('v2', 0x80000000800000008000000080000000),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x80000080800000808000008080000080),
                ('VSCR', 0x0),
            )
        },
    ],

    '1020134E': [ # vupkhpx v1,v2
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x042184210000ffffacacacacacacacac),
            ),
            'tests': (
                ('v1', 0x00010101ff01010100000000ff1f1f1f),
            )
        },
    ],

    '102013CE': [ # vupklpx v1,v2
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xacacacacacacacac042184210000ffff),
            ),
            'tests': (
                ('v1', 0x00010101ff01010100000000ff1f1f1f),
            )
        },
    ],

    '1020120E': [ # vupkhsb v1,v2
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x01807f8166ee77ddacacacacacacacac),
            ),
            'tests': (
                ('v1', 0x0001ff80007fff810066ffee0077ffdd),
            )
        },
    ],

    '1020124E': [ # vupkhsh v1,v2
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x000180007fff8111acacacacacacacac),
            ),
            'tests': (
                ('v1', 0x00000001ffff800000007fffffff8111),
            )
        },
    ],

    '1020128E': [ # vupklsb v1,v2
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xacacacacacacacac01807f8166ee77dd),
            ),
            'tests': (
                ('v1', 0x0001ff80007fff810066ffee0077ffdd),
            )
        },
    ],

    '102012CE': [ # vupklsh v1,v2
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xacacacacacacacac000180007fff8111),
            ),
            'tests': (
                ('v1', 0x00000001ffff800000007fffffff8111),
            )
        },
    ],

    '10221CC4': [ # vxor    v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xf0f0f0f00f0f0f0fc3c3c3c33c3c3c3c),
                ('v3', 0xf0f0f0f00f0f0f0fc3c3c3c33c3c3c3c),
            ),
            'tests': (
                ('v1', 0x0),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xf0f0f0f00f0f0f0fc3c3c3c33c3c3c3c),
                ('v3', 0xf0f0f0ff0f0f0f03c3c3c3cc3c3c3c3),
            ),
            'tests': (
                ('v1', 0xffffffffffffffffffffffffffffffff),
            )
        },
    ],

    '7C21120A': [ # lvexbx  v1,r1,r2
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x400),
                ('r2', 0x10000000),
                (0x10000400, bytes.fromhex('abcdef12abcdef12')),
            ),
            'tests': (
                ('v1', 0xab000000000000000000000000000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x400),
                ('r2', 0x10000001),
                (0x10000401, bytes.fromhex('abcdef12')),
            ),
            'tests': (
                ('v1', 0xab0000000000000000000000000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x440),
                ('r2', 0x1000000f),
                (0x1000044f, bytes.fromhex('abcdef12')),
            ),
            'tests': (
                ('v1', 0xab),
            )
        },
    ],

    '7C21124A': [ # lvexhx  v1,r1,r2
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x400),
                ('r2', 0x10000000),
                (0x10000400, bytes.fromhex('abcdef12abcdef12')),
            ),
            'tests': (
                ('v1', 0xabcd0000000000000000000000000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x400),
                ('r2', 0x10000001),
                (0x10000400, bytes.fromhex('abcdef12')),
            ),
            'tests': (
                ('v1', 0xabcd0000000000000000000000000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x440),
                ('r2', 0x1000000f),
                (0x1000044e, bytes.fromhex('abcdef12')),
            ),
            'tests': (
                ('v1', 0xabcd),
            )
        },
    ],

    '7C21128A': [ # lvexwx  v1,r1,r2
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x400),
                ('r2', 0x10000000),
                (0x10000400, bytes.fromhex('abcdef12')),
            ),
            'tests': (
                ('v1', 0xabcdef12000000000000000000000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x400),
                ('r2', 0x10000001),
                (0x10000400, bytes.fromhex('abcdef12')),
            ),
            'tests': (
                ('v1', 0xabcdef12000000000000000000000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x440),
                ('r2', 0x1000000f),
                (0x1000044c, bytes.fromhex('abcdef12')),
            ),
            'tests': (
                ('v1', 0xabcdef12),
            )
        },
    ],

    '7C21160A': [ # lvsm    v1,r1,r2
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x400),
                ('r2', 0x10000000),
            ),
            'tests': (
                ('v1', 0xffffffffffffffffffffffffffffffff),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x403),
                ('r2', 0x10000000),
            ),
            'tests': (
                ('v1', 0xffffffffffffffffffffffffff000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x44f),
                ('r2', 0x10000000),
            ),
            'tests': (
                ('v1', 0xff000000000000000000000000000000),
            )
        },
    ],

    '7C2114CA': [ # lvswx   v1,r1,r2
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x400),
                ('r2', 0x10000000),
                (0x10000400, bytes.fromhex('dfac022520210fcd08072021dfbf8487')),
            ),
            'tests': (
                ('v1', 0xdfac022520210fcd08072021dfbf8487),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x403),
                ('r2', 0x10000000),
                (0x10000400, bytes.fromhex('dfac022520210fcd08072021dfbf8487')),
            ),
            'tests': (
                ('v1', 0x2520210fcd08072021dfbf8487dfac02),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x44f),
                ('r2', 0x10000000),
                (0x10000440, bytes.fromhex('dfac022520210fcd08072021dfbf8487')),
            ),
            'tests': (
                ('v1', 0x87dfac022520210fcd08072021dfbf84),
            )
        },
    ],

    '7C2116CA': [ # lvswxl   v1,r1,r2
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x400),
                ('r2', 0x10000000),
                (0x10000400, bytes.fromhex('dfac022520210fcd08072021dfbf8487')),
            ),
            'tests': (
                ('v1', 0xdfac022520210fcd08072021dfbf8487),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x403),
                ('r2', 0x10000000),
                (0x10000400, bytes.fromhex('dfac022520210fcd08072021dfbf8487')),
            ),
            'tests': (
                ('v1', 0x2520210fcd08072021dfbf8487dfac02),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x44f),
                ('r2', 0x10000000),
                (0x10000440, bytes.fromhex('dfac022520210fcd08072021dfbf8487')),
            ),
            'tests': (
                ('v1', 0x87dfac022520210fcd08072021dfbf84),
            )
        },
    ],

    '7C21148A': [ # lvtlx   v1,r1,r2
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x400),
                ('r2', 0x10000000),
                (0x10000400, bytes.fromhex('dfac022520210fcd08072021dfbf8487')),
            ),
            'tests': (
                ('v1', 0xdfac022520210fcd08072021dfbf8487),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x403),
                ('r2', 0x10000000),
                (0x10000400, bytes.fromhex('dfac022520210fcd08072021dfbf8487')),
            ),
            'tests': (
                ('v1', 0x2520210fcd08072021dfbf8487000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x44f),
                ('r2', 0x10000000),
                (0x10000440, bytes.fromhex('dfac022520210fcd08072021dfbf8487')),
            ),
            'tests': (
                ('v1', 0x87000000000000000000000000000000),
            )
        },
    ],

    '7C21168A': [ # lvtlxl  v1,r1,r2
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x400),
                ('r2', 0x10000000),
                (0x10000400, bytes.fromhex('dfac022520210fcd08072021dfbf8487')),
            ),
            'tests': (
                ('v1', 0xdfac022520210fcd08072021dfbf8487),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x403),
                ('r2', 0x10000000),
                (0x10000400, bytes.fromhex('dfac022520210fcd08072021dfbf8487')),
            ),
            'tests': (
                ('v1', 0x2520210fcd08072021dfbf8487000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x44f),
                ('r2', 0x10000000),
                (0x10000440, bytes.fromhex('dfac022520210fcd08072021dfbf8487')),
            ),
            'tests': (
                ('v1', 0x87000000000000000000000000000000),
            )
        },
    ],

    '7C21144A': [ # lvtrx   v1,r1,r2
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x400),
                ('r2', 0x10000000),
                (0x10000400, bytes.fromhex('dfac022520210fcd08072021dfbf8487')),
            ),
            'tests': (
                ('v1', 0x0),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x403),
                ('r2', 0x10000000),
                (0x10000400, bytes.fromhex('dfac022520210fcd08072021dfbf8487')),
            ),
            'tests': (
                ('v1', 0xdfac02),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x44f),
                ('r2', 0x10000000),
                (0x10000440, bytes.fromhex('dfac022520210fcd08072021dfbf8487')),
            ),
            'tests': (
                ('v1', 0xdfac022520210fcd08072021dfbf84),
            )
        },
    ],

    '7C21164A': [ # lvtrxl  v1,r1,r2
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x400),
                ('r2', 0x10000000),
                (0x10000400, bytes.fromhex('dfac022520210fcd08072021dfbf8487')),
            ),
            'tests': (
                ('v1', 0x0),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x403),
                ('r2', 0x10000000),
                (0x10000400, bytes.fromhex('dfac022520210fcd08072021dfbf8487')),
            ),
            'tests': (
                ('v1', 0xdfac02),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x44f),
                ('r2', 0x10000000),
                (0x10000440, bytes.fromhex('dfac022520210fcd08072021dfbf8487')),
            ),
            'tests': (
                ('v1', 0xdfac022520210fcd08072021dfbf84),
            )
        },
    ],

    '7C21105C': [ # mviwsplt v1,r1,r2
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0xdfac022520210fcd),
                ('r2', 0x8072021dfbf8487),
            ),
            'tests': (
                ('v1', 0x20210fcddfbf848720210fcddfbf8487),
            )
        },
    ],

    '7C21130A': [ # stvexbx v1,r1,r2
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x400),
                ('r2', 0x10010000),
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010400, bytes.fromhex('abdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            )
        },
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x400),
                ('r2', 0x10010001),
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010400, bytes.fromhex('dfacdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            )
        },
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x440),
                ('r2', 0x1001000f),
                (0x10010440, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010440, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdf87')),
            )
        },
    ],

    '7C21134A': [ # stvexhx v1,r1,r2
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x400),
                ('r2', 0x10010000),
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010400, bytes.fromhex('abacdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            )
        },
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x400),
                ('r2', 0x10010001),
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010400, bytes.fromhex('abacdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            )
        },
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x440),
                ('r2', 0x1001000f),
                (0x10010440, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010440, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdf8487')),
            )
        },
    ],

    '7C21138A': [ # stvexwx v1,r1,r2
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x400),
                ('r2', 0x10010000),
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010400, bytes.fromhex('abac0225dfdfdfdfdfdfdfdfdfdfdfdf')),
            )
        },
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x400),
                ('r2', 0x10010001),
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010400, bytes.fromhex('abac0225dfdfdfdfdfdfdfdfdfdfdfdf')),
            )
        },
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x440),
                ('r2', 0x1001000f),
                (0x10010440, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010440, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfbf8487')),
            )
        },
    ],

    '7C21158A': [ # stvflx  v1,r1,r2
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x400),
                ('r2', 0x10010000),
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010400, bytes.fromhex('abac022520210fcd08072021dfbf8487')),
            )
        },
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x400),
                ('r2', 0x10010001),
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010400, bytes.fromhex('dfabac022520210fcd08072021dfbf84')),
            )
        },
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x440),
                ('r2', 0x1001000f),
                (0x10010440, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010440, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfab')),
            )
        },
    ],

    '7C21178A': [ # stvflxl v1,r1,r2
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x400),
                ('r2', 0x10010000),
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010400, bytes.fromhex('abac022520210fcd08072021dfbf8487')),
            )
        },
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x400),
                ('r2', 0x10010001),
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010400, bytes.fromhex('dfabac022520210fcd08072021dfbf84')),
            )
        },
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x440),
                ('r2', 0x1001000f),
                (0x10010440, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010440, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfab')),
            )
        },
    ],

    '7C21154A': [ # stvfrx  v1,r1,r2
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x400),
                ('r2', 0x10010000),
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            )
        },
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x400),
                ('r2', 0x10010001),
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010400, bytes.fromhex('87dfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            )
        },
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x440),
                ('r2', 0x1001000f),
                (0x10010440, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010440, bytes.fromhex('ac022520210fcd08072021dfbf8487df')),
            )
        },
    ],

    '7C21174A': [ # stvfrxl v1,r1,r2
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x400),
                ('r2', 0x10010000),
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            )
        },
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x400),
                ('r2', 0x10010001),
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010400, bytes.fromhex('87dfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            )
        },
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x440),
                ('r2', 0x1001000f),
                (0x10010440, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010440, bytes.fromhex('ac022520210fcd08072021dfbf8487df')),
            )
        },
    ],

    '7C2117CA': [ # stvswx  v1,r1,r2
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x400),
                ('r2', 0x10010000),
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010400, bytes.fromhex('abac022520210fcd08072021dfbf8487')),
            )
        },
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x400),
                ('r2', 0x10010001),
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010400, bytes.fromhex('87abac022520210fcd08072021dfbf84')),
            )
        },
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x440),
                ('r2', 0x1001000f),
                (0x10010440, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010440, bytes.fromhex('ac022520210fcd08072021dfbf8487ab')),
            )
        },
    ],

    '7C2115CA': [ # stvswxl v1,r1,r2
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x400),
                ('r2', 0x10010000),
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010400, bytes.fromhex('abac022520210fcd08072021dfbf8487')),
            )
        },
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x400),
                ('r2', 0x10010001),
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010400, bytes.fromhex('87abac022520210fcd08072021dfbf84')),
            )
        },
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x440),
                ('r2', 0x1001000f),
                (0x10010440, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010440, bytes.fromhex('ac022520210fcd08072021dfbf8487ab')),
            )
        },
    ],

    '10221C03': [ # vabsdub v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x80808080222222227f7f7f7f44444444),
                ('v3', 0x202020277777777fefefefe66666666),
            ),
            'tests': (
                ('v1', 0x7e7e7e7e555555557f7f7f7f22222222),
            )
        },
    ],

    '10221C43': [ # vabsduh v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x80808080222222227f7f7f7f44444444),
                ('v3', 0x202020277777777fefefefe66666666),
            ),
            'tests': (
                ('v1', 0x7e7e7e7e555555557f7f7f7f22222222),
            )
        },
    ],

    '10221C83': [ # vabsduw v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x80808080222222227f7f7f7f44444444),
                ('v3', 0x202020277777777fefefefe66666666),
            ),
            'tests': (
                ('v1', 0x7e7e7e7e555555557f7f7f7f22222222),
            )
        },
    ],

    '10221920': [ # vmhaddshs v1,v2,v3,v4
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x22223333111144448888555500006666),
                ('v3', 0x111144440000666677770000ffff2222),
                ('v4', 0x33336666222200009999111122223333),
                ('VCSR', 0x0),
            ),
            'tests': (
                ('v1', 0x37c07fff2222369c8000111122224e81),
                ('VCSR', 0x1),
            )
        },
    ],

    '10221921': [ # vmhraddshs v1,v2,v3,v4
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x22223333111144448888555500006666),
                ('v3', 0x111144440000666677770000ffff2222),
                ('v4', 0x33336666222200009999111122223333),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x37c07fff2222369d8000111122224e81),
                ('VSCR', 0x1),
            )
        },
    ],

    '1022180A': [ # vaddfp  v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x3f800000412000003f8000003f800000),
                ('v3', 0x3f8000003f8000003f8000003f800000),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x40000000413000004000000040000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x3fd555554021e1e23e93205e4075c28f),
                ('v3', 0x3fd555554021e1e23e93205e4075c28f),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x4055555540a1e1e23f13205e40f5c28f),
            )
        },
    ],

    '1020134A': [ # vcfsx   v1,v2,0
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x3fd555554021e1e23e93205e4075c28f),
            ),
            'tests': (
                ('v1', 0x4e7f55554e8043c44e7a4c814e80eb85),
            )
        },
    ],

    '1034134A': [ # vcfsx   v1,v2,20
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x3fd555554021e1e23e93205e4075c28f),
            ),
            'tests': (
                ('v1', 0x447f5555448043c4447a4c814480eb85),
            )
        },
    ],

    '1020130A': [ # vcfux   v1,v2,0
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x3fd555554021e1e23e93205e4075c28f),
            ),
            'tests': (
                ('v1', 0x4e7f55554e8043c44e7a4c814e80eb85),
            )
        },
    ],

    '1038130A': [ # vcfux   v1,v2,24
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x3fd555554021e1e23e93205e4075c28f),
            ),
            'tests': (
                ('v1', 0x427f5555428043c4427a4c814280eb85),
            )
        },
    ],

    '102013CA': [ # vctsxs  v1,v2,0
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x3f8000003f8000003f8000003f800000),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x1000000010000000100000001),
                ('VSCR', 0x0),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x3fd555554021e1e23e93205e4075c28f),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x1000000020000000000000003),
                ('VSCR', 0x0),
            )
        },
    ],

    '103813CA': [ # vctsxs  v1,v2,24
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x3fd555554021e1e23e93205e4075c28f),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x1aaaaaa028787880049902f03d70a3c),
                ('VSCR', 0x0),
            )
        },
    ],

    '1020138A': [ # vctuxs  v1,v2,0
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x3f8000003f8000003f8000003f800000),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x1000000010000000100000001),
                ('VSCR', 0x0),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x3fd555554021e1e23e93205e4075c28f),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x1000000020000000000000003),
                ('VSCR', 0x0),
            )
        },
    ],

    '1038138A': [ # vctuxs  v1,v2,24
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x3fd555554021e1e23e93205e4075c28f),
                ('VSCR', 0x0),
            ),
            'tests': (
                ('v1', 0x1aaaaaa028787880049902f03d70a3c),
                ('VSCR', 0x0),
            )
        },
    ],

    '10221BC6': [ # vcmpbfp v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x40d70a3d44f48b1fc24b3333c61844cd),
                ('v3', 0x412b851f447a2466c24f3333c43a4ccd),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0x0000000080000000c000000040000000),
                ('CR', 0x00000000),
            )
        },
    ],

    '10221FC6': [ # vcmpbfp. v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x40d70a3d40d70a3d40d70a3d40d70a3d),
                ('v3', 0x412b851f412b851f412b851f412b851f),
                ('CR', 0x00000000),
            ),
            'tests': (
                ('v1', 0x0),
                ('CR', 0x00000020),
            )
        },
    ],

    '102218C6': [ # vcmpeqfp v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x0),
            ),
            'tests': (
                ('v1', 0xffffffffffffffffffffffffffffffff),
                ('CR', 0x0),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x0),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x0),
            ),
            'tests': (
                ('v1', 0x0),
                ('CR', 0x0),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('v3', 0xbd9cd03c00000000624a841700000000),
                ('CR', 0x0),
            ),
            'tests': (
                ('v1', 0xffffffff00000000ffffffff00000000),
                ('CR', 0x0),
            )
        },
    ],

    '10221CC6': [ # vcmpeqfp. v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x0),
            ),
            'tests': (
                ('v1', 0xffffffffffffffffffffffffffffffff),
                ('CR', 0x80),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x0),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x0),
            ),
            'tests': (
                ('v1', 0x0),
                ('CR', 0x20),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('v3', 0xbd9cd03c00000000624a841700000000),
                ('CR', 0x0),
            ),
            'tests': (
                ('v1', 0xffffffff00000000ffffffff00000000),
                ('CR', 0x0),
            )
        },
    ],

    '102219C6': [ # vcmpgefp v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x0),
            ),
            'tests': (
                ('v1', 0xffffffffffffffffffffffffffffffff),
                ('CR', 0x0),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x0),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x0),
            ),
            'tests': (
                ('v1', 0xffffffffffffffff00000000ffffffff),
                ('CR', 0x0),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('v3', 0xbd9cd03c00000000624a841700000000),
                ('CR', 0x0),
            ),
            'tests': (
                ('v1', 0xffffffff00000000ffffffff00000000),
                ('CR', 0x0),
            )
        },
    ],

    '10221DC6': [ # vcmpgefp. v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x0),
            ),
            'tests': (
                ('v1', 0xffffffffffffffffffffffffffffffff),
                ('CR', 0x80),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x0),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x0),
            ),
            'tests': (
                ('v1', 0xffffffffffffffff00000000ffffffff),
                ('CR', 0x0),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('v3', 0xbd9cd03c00000000624a841700000000),
                ('CR', 0x0),
            ),
            'tests': (
                ('v1', 0xffffffff00000000ffffffff00000000),
                ('CR', 0x0),
            )
        },
    ],

    '10221AC6': [ # vcmpgtfp v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x0),
            ),
            'tests': (
                ('v1', 0x0),
                ('CR', 0x0),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x0),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x0),
            ),
            'tests': (
                ('v1', 0xffffffffffffffff00000000ffffffff),
                ('CR', 0x0),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('v3', 0xbd9cd03c00000000624a841700000000),
                ('CR', 0x0),
            ),
            'tests': (
                ('v1', 0x0),
                ('CR', 0x0),
            )
        },
    ],

    '10221EC6': [ # vcmpgtfp. v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x0),
            ),
            'tests': (
                ('v1', 0x0),
                ('CR', 0x20),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x0),
                ('v3', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('CR', 0x0),
            ),
            'tests': (
                ('v1', 0xffffffffffffffff00000000ffffffff),
                ('CR', 0x0),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0xbd9cd03caec992b2624a8417c90ebb7b),
                ('v3', 0xbd9cd03c00000000624a841700000000),
                ('CR', 0x0),
            ),
            'tests': (
                ('v1', 0x0),
                ('CR', 0x20),
            )
        },
    ],

    '1022192E': [ # vmaddfp v1,v2,v4,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x3fd555554021e1e23e93205e4075c28f),
                ('v3', 0x3fd555554021e1e28000000080000000),
                ('v4', 0x3fd555554021e1e2800000004075c28f),
            ),
            'tests': (
                ('v1', 0x408e38e3410ed65e80000000416bedfa),
            )
        },
    ],

    '1022192F': [ # vnmsubfp v1,v2,v4,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x3fd555554021e1e23e93205e4075c28f),
                ('v3', 0x3fd555554021e1e28000000080000000),
                ('v4', 0x3fd555554021e1e2800000004075c28f),
            ),
            'tests': (
                ('v1', 0xbf8e38e3c07795b480000000c16bedfa),
            )
        },
    ],

    '10221C0A': [ # vmaxfp  v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x3fd555554021e1e2000000004075c28f),
                ('v3', 0x3fd555554021e1e28000000080000000),
            ),
            'tests': (
                ('v1', 0x3fd555554021e1e2000000004075c28f),
            )
        },
    ],

    '10221C4A': [ # vminfp  v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x3fd555554021e1e2000000004075c28f),
                ('v3', 0x3fd555554021e1e28000000080000000),
            ),
            'tests': (
                ('v1', 0x3fd555554021e1e28000000080000000),
            )
        },
    ],

    '1022184A': [ # vsubfp  v1,v2,v3
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x3f800000412000003f8000003f800000),
                ('v3', 0x3f8000003f8000003f8000003f800000),
            ),
            'tests': (
                ('v1', 0x411000000000000000000000),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x3fd555554021e1e23e93205e4075c28f),
                ('v3', 0x4021e1e23e93205e4075c28f3fd55555),
            ),
            'tests': (
                ('v1', 0xbf5cdcde400f7dd6c0635e83400b17e4),
            )
        },
    ],

    '102012CA': [ # vrfim   v1,v2
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x3f8ccccd3fc00000bf8ccccdbfc00000),
            ),
            'tests': (
                ('v1', 0x3f8000003f800000c0000000c0000000),
            )
        },
    ],

    '1020120A': [ # vrfin   v1,v2
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x3f8ccccd3fc00000bf8ccccdbfc00000),
            ),
            'tests': (
                ('v1', 0x3f80000040000000bf800000c0000000),
            )
        },
    ],

    '1020128A': [ # vrfip   v1,v2
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x3f8ccccd3fc00000bf8ccccdbfc00000),
            ),
            'tests': (
                ('v1', 0x4000000040000000bf800000bf800000),
            )
        },
    ],

    '1020124A': [ # vrfiz   v1,v2
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('v2', 0x3f8ccccd3fc00000bf8ccccdbfc00000),
            ),
            'tests': (
                ('v1', 0x3f8000003f800000bf800000bf800000),
            )
        },
    ],

    '7C2110DC': [ # mvidsplt v1,r1,r2
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0xdfac022520210fcd),
                ('r2', 0x8072021dfbf8487),
            ),
            'tests': (
                ('v1', 0xdfac022520210fcd08072021dfbf8487),
            )
        },
    ],

    '7C21124E': [ # lvepx     v1,r1,r2
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x400),
                ('r2', 0x10000000),
                (0x10000400, bytes.fromhex('dfac022520210fcd08072021dfbf8487')),
            ),
            'tests': (
                ('v1', 0xdfac022520210fcd08072021dfbf8487),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x401),
                ('r2', 0x10000000),
                (0x10000400, bytes.fromhex('dfac022520210fcd08072021dfbf8487')),
            ),
            'tests': (
                ('v1', 0xdfac022520210fcd08072021dfbf8487),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x44f),
                ('r2', 0x10000000),
                (0x10000440, bytes.fromhex('dfac022520210fcd08072021dfbf8487')),
            ),
            'tests': (
                ('v1', 0xdfac022520210fcd08072021dfbf8487),
            )
        },
    ],

    '7C21120E': [ # lvepxl     v1,r1,r2
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x400),
                ('r2', 0x10000000),
                (0x10000400, bytes.fromhex('dfac022520210fcd08072021dfbf8487')),
            ),
            'tests': (
                ('v1', 0xdfac022520210fcd08072021dfbf8487),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x401),
                ('r2', 0x10000000),
                (0x10000400, bytes.fromhex('dfac022520210fcd08072021dfbf8487')),
            ),
            'tests': (
                ('v1', 0xdfac022520210fcd08072021dfbf8487),
            )
        },
        {
            'setup': (
                ('v1', 0xdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf),
                ('r1', 0x44f),
                ('r2', 0x10000000),
                (0x10000440, bytes.fromhex('dfac022520210fcd08072021dfbf8487')),
            ),
            'tests': (
                ('v1', 0xdfac022520210fcd08072021dfbf8487),
            )
        },
    ],

    '7C21164E': [ # stvepx    v1,r1,r2
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x400),
                ('r2', 0x10010000),
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010400, bytes.fromhex('abac022520210fcd08072021dfbf8487')),
            )
        },
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x401),
                ('r2', 0x10010000),
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010400, bytes.fromhex('abac022520210fcd08072021dfbf8487')),
            )
        },
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x44f),
                ('r2', 0x10010000),
                (0x10010440, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010440, bytes.fromhex('abac022520210fcd08072021dfbf8487')),
            )
        },
    ],

    '7C21160E': [ # stvepxl   v1,r1,r2
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x400),
                ('r2', 0x10010000),
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010400, bytes.fromhex('abac022520210fcd08072021dfbf8487')),
            )
        },
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x401),
                ('r2', 0x10010000),
                (0x10010400, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010400, bytes.fromhex('abac022520210fcd08072021dfbf8487')),
            )
        },
        {
            'setup': (
                ('v1', 0xabac022520210fcd08072021dfbf8487),
                ('r1', 0x44f),
                ('r2', 0x10010000),
                (0x10010440, bytes.fromhex('dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf')),
            ),
            'tests': (
                (0x10010440, bytes.fromhex('abac022520210fcd08072021dfbf8487')),
            )
        },
    ],
}

GOOD_EMU_TESTS = 1371
