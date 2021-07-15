

# VLE opcode types
# FIXME: generate automatically like mnems.py
mnems = (
    'ill',

    'add',
    'sub',
    'mul',
    'div',
    'shr',
    'shl',
    'ror',

    'and',
    'or',
    'xor',
    'nor',
    'not',

    'io',
    'load',
    'store',
    'mov',

    'cmp',
    'jmp',
    'cjmp',
    'call',
    'ccall',
    'rjmp',
    'rcall',
    'ret',

    'sync',
    'swi',
    'trap',
    # Added for EB696 Interrupt Helper instructions (e.g. "e_ldmvgprw")
    'loadmult',
    'storemult',
)
