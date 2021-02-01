from envi.const import *
from envi import IF_NOFALL, IF_PRIV, IF_CALL, IF_BRANCH, IF_RET, IF_COND

MODE_USER = 0
MODE_SUPV = 1

IF_NONE = 0

IF_BYTE = 1<<8
IF_WORD = 1<<9
IF_LONG = 1<<10
IF_UWORD = 1<<11

SZ = [
    (IF_BYTE, 1),
    (IF_WORD, 2),
    (IF_LONG, 4),
    (IF_UWORD, 2),
    ]


OF_B = 1 << 0
OF_W = 1 << 1
OF_L = 1 << 2
OF_UW = 1 << 3
OF_UB = 1 << 4

MI_FLAGS = (
        (OF_B, 1),
        (OF_W, 2),
        (OF_L, 4),
        (OF_UW, 2),
        (OF_UB, 1),
        )

SIZE_BYTES = [None for x in range(17)]
SIZE_BYTES[OF_B] = 'b'
SIZE_BYTES[OF_W] = 'w'
SIZE_BYTES[OF_L] = 'l'
SIZE_BYTES[OF_UW] = 'uw'
SIZE_BYTES[OF_UB] = 'ub'


BMCND = [
    'bmz',
    'bmnz',
    'bmgeu',
    'bmltu',
    'bmgtu',
    'bmleu',
    'bmpz',
    'bmn',
    'bmge',
    'bmlt',
    'bmgt',
    'bmle',
    'bmo',
    'bmno',
]
SCCND = [
    'scz',
    'scnz',
    'scgeu',
    'scltu',
    'scgtu',
    'scleu',
    'scpz',
    'scn',
    'scge',
    'sclt',
    'scgt',
    'scle',
    'sco',
    'scno',
]
mnems = [
    'abs',
    'adc',
    'add',
    'and',
    'bclr',
    'bz',
    'bge',
    'bnz',
    'blt',
    'bgeu',
    'bgt',
    'bltu',
    'ble',
    'bgtu',
    'bo',
    'bleu',
    'bno',
    'bpz',
    'bn',
    'bmcnd',
    'bnot',
    'bra',
    'brk',
    'bset',
    'bsr',
    'btst',
    'clrpsw',
    'cmp',
    'div',
    'divu',
    'emaca',
    'emsba',
    'emul',
    'emula',
    'emulu',
    'fadd',
    'fcmp',
    'fdiv',
    'fmul',
    'fsqrt',
    'fsub',
    'ftoi',
    'ftou',
    'int',
    'itof',
    'jmp',
    'jsr',
    'machi',
    'maclh',
    'maclo',
    'max',
    'min',
    'mov',
    'movco',
    'movli',
    'movu',
    'msbhi',
    'msblh',
    'msblo',
    'mul',
    'mulhi',
    'mullh',
    'mullo',
    'mvfacgu',
    'mvfachi',
    'mvfaclo',
    'mvfacmi',
    'mvfc',
    'mvtacgu',
    'mvtachi',
    'mvtaclo',
    'mvtc',
    'mvtipl',
    'neg',
    'nop',
    'not',
    'or',
    'pop',
    'popc',
    'popm',
    'push',
    'pushc',
    'pushm',
    'racl',
    'racw',
    'rdacl',
    'rdacw',
    'revl',
    'revw',
    'rmpa',
    'rolc',
    'rorc',
    'rotl',
    'rotr',
    'round',
    'rte',
    'rtfi',
    'rts',
    'rtsd',
    'sat',
    'satr',
    'sbb',
    'sccnd',
    'scmpu',
    'setpsw',
    'shar',
    'shll',
    'shlr',
    'smovb',
    'smovf',
    'smovu',
    'sstr',
    'stnz',
    'stz',
    'sub',
    'suntil',
    'swhile',
    'tst',
    'utof',
    'wait',
    'xchg',
    'xor',
]
mnems.extend(BMCND)
mnems.extend(SCCND)

instrs = {}
for mnem in mnems:
    instrs["INS_%s" % mnem.upper()] = len(instrs)

globals().update(instrs)



nms = (
    'O_PCDSP',
    'O_RD',
    'O_LDS',
    'O_RS',
    'O_MI',
    'O_RS2',
    'O_DSP',
    'O_SZ',
    'O_RD2',
    'O_IMM',
    'O_LI',
    'O_CR',
    'O_CB',
    'O_LDD',
    'O_CD',
    'O_A',
    'O_AD',
    'O_RI',
    'O_RB',
)


nmconsts = {}
for nm in nms:
    nmconsts[nm.upper()] = len(nmconsts)

globals().update(nmconsts)



forms = (
    'FORM_PCDSP',
    'FORM_RD_LD_RS',
    'FORM_RD_LD_MI_RS',
    'FORM_RD_IMM',
    'FORM_RD_LI',
    'FORM_SCCND',
    'FORM_BMCND',
    'FORM_A_RS2_RS',
)


formconsts = {}
for form in forms:
    formconsts[form.upper()] = len(formconsts)

globals().update(formconsts)



