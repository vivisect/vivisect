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
    IF_BYTE,
    IF_WORD,
    IF_LONG,
    IF_UWORD,
    ]


mnems = (
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
)


instrs = {}
for mnem in mnems:
    instrs["INS_%s" % mnem.upper()] = len(instrs)

globals().update(instrs)


nms = (
    'O_PCDSP',
    'O_RD',
    'O_LDS',
    'O_MI',
    'O_RS',
    'O_RS2',
    'O_DSP',
    'O_SZ',
    'O_RD2',
    'O_IMM',
    'O_LI',
    'O_CR',
    'O_CB',
    'O_LDD',
    'O_BRD',
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


