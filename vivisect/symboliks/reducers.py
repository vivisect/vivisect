import copy

import envi.bits as e_bits

from vivisect.const import *
from vivisect.symboliks.common import *
from vivisect.symboliks.expression import symexp

def ismatch(sym,tmp):
    '''
    FIXME - eventually optimize this into one match call
            against a set of trees....

    Given a sym and s "symbolik template" determine if
    the given sym matches the specified template.

    A symbolik "template" declares a symbolik expression
    which represents a given combination of consts, non-consts,
    operators, and spcific values using the following rules:

        ( where N is a number chosen to unique the variable )

        * cN - any constant expression
        * xN - any non-constant expression
        * <num> - A specific constant value
        * <oper> - An exactly matching operator

    For example

        truths:
        ismatch( symexp('eax + 20'), symexp('x1 + c1'))
        ismatch( symexp('(eax + 20) + ebx'), symexp('(x1 + c1) + x2'))

        falses:
        ismatch( symexp('eax + 20'), symexp('x1 + 30'))
        ismatch( symexp('eax + 20'), symexp('x1 + x2'))
        ismatch( symexp('eax - 20'), symexp('x1 + c1'))

    Returns: None or a dict of template var names to sym
             objects ( Const instances are replaced with
             python integer values to symplify reduction
             syntax...

        ismatch( symexp('eax + 20'), symexp('x1 + c1')) -> {'x1':Var('eax'), 'c1':20}
    '''
    todo = [(sym, tmp)]

    symwidth = sym.getWidth()

    ret = {}
    while todo:
        s, t = todo.pop()

        if s.getWidth() != symwidth and s.symtype != SYMT_CONST:
            return None

        if t.symtype == SYMT_VAR:
            if t.name.startswith('c') and s.symtype != SYMT_CONST:
                return None

            if t.name.startswith('x') and s.symtype == SYMT_CONST:
                return None

            # haz? if so, require equality...
            haz = ret.get(t.name)
            if haz and haz.solve() != s.solve():
                return None

            ret[t.name] = s
            continue

        if t.symtype != s.symtype:
            return None

        if t.symtype & SYMT_OPER:
            todo.append((s.kids[0], t.kids[0]))
            todo.append((s.kids[1], t.kids[1]))
            continue

        if t.symtype in (SYMT_CON_EQ, SYMT_CON_NE):
            todo.append((s.kids[0], t.kids[0]))
            todo.append((s.kids[1], t.kids[1]))
            continue

        if t.symtype == SYMT_CONST:
            if t.value != s.value:
                return None
            continue

        raise Exception(str(t))

    # replace all consts with their solved values...
    for k, v in ret.items():
        if k.startswith('c'):
            ret[k] = v.solve()

    return ret

def variants(sym):
    '''
    Given a SymbolikBase, generate all of the comutative
    combinations of the given expression.

    Example:

        variants( symexpr('(x + 20) + y') )

        Would return a list of sym objects with the
        given structure:

            (x + 20) + y
            (x + y) + 20
            (y + 20) + x
            (y + x) + 20
    '''
    todo = [sym]
    swaps = []

    while todo:
        t = todo.pop()
        if t.commutative:
            k0 = list(t.kids)
            k1 = list(t.kids)
            k1.reverse()
            swaps.append((t, (k0, k1)))

        todo.extend(t.kids)

    for i in range(2**len(swaps)):
        for t, k in swaps:
            t.kids[0:2] = k[i & 1]
            i >>= 1

        sym.clearCache()
        yield copy.deepcopy(sym)  # s.clone()

def addsub(x, c):
    '''
    Given the sign of c, return either an o_add or
    an o_sub with x on the left and abs(c) on the right.

    ( or just x if c happens to be 0 )
    '''
    if c > 0:
        return x + Const(c, x.getWidth())
    elif c < 0:
        return x - Const(abs(c), x.getWidth())
    else:
        return x

def sub_c_x(c, x):
    '''
    Construct an o_sub for c - x.
    If c is negative, build (0 - c) - x
    '''
    xwidth = x.getWidth()
    if c < 0:
        return (Const(0, xwidth) - Const(c, xwidth)) - x
    return Const(c,xwidth) - x

def ormask(v,c):
    vwidth = v.getWidth()
    if c == 0:
        return v

    if e_bits.u_maxes[vwidth] == c:
        return e_bits.u_maxes[vwidth]

    return v | Const(c,vwidth)

def andmask(v,c):
    vwidth = v.getWidth()
    if c == 0:
        return Const(0,vwidth)

    umax = e_bits.u_maxes[vwidth]
    if umax == c:
        return v

    if umax & c == 0:
        return Const(0,vwidth)

    return v & Const(c,vwidth)

def mulbase(v, c):
    vwidth = v.getWidth()
    if c == 0:
        return Const(0, vwidth)
    if c == 1:
        return v
    return v * Const(c,vwidth)

def divbase_vc(v, c):
    vwidth = v.getWidth()
    if c == 1:
        return v
    return v / Const(c,vwidth)

def divbase_cv(c, v):
    vwidth = v.getWidth()
    if c == 0:
        return Const(0,vwidth)
    return Const(c,vwidth) / v

def muldiv(v, m, d):
    vwidth = v.getWidth()

    if m == d:
        return v

    if m % d == 0:
        return v * Const(int(m/d), vwidth)

def xpandrules(rules):
    reducers = []
    for symtmp, reducer in rules:
        for symtmp in variants(symexp(symtmp)):
            reducers.append((symtmp, reducer))
    return reducers

def symneg(x):
    return Const(0, x.getWidth()) - x

# NOTE: all reducers *must* be declared in most->least
# specific order.
reducers = {
    SYMT_OPER_ADD: xpandrules([
        ('(x1 - c1) + (x2 - c2)', lambda m, emu=None: addsub(m['x1'] + m['x2'], -(m['c1'] + m['c2']))),
        ('(c1 - x1) + (x2 + c2)', lambda m, emu=None: addsub(m['x2'] - m['x1'], m['c1'] + m['c2'])),
        ('(x1 + c1) + (x2 - c2)', lambda m, emu=None: addsub(m['x1'] + m['x2'], m['c1'] - m['c2'])),
        ('(x1 + c1) + (x2 + c2)', lambda m, emu=None: addsub(m['x1'] + m['x2'], m['c1'] + m['c2'])),
        ('(x1 + c1) + c2', lambda m, emu=None: addsub(m['x1'], m['c1'] + m['c2'])),
        ('(x1 + c1) + x2', lambda m, emu=None: addsub(m['x1'] + m['x2'], m['c1'])),
        ('(x1 - c1) + c2', lambda m, emu=None: addsub(m['x1'], m['c2'] - m['c1'])),
        ('(c1 - x1) + x2', lambda m, emu=None: addsub(m['x2'] - m['x1'], m['c1'])),
        ('(c1 - x1) + c2', lambda m, emu=None: addsub(symneg(m['x1']), m['c1'] + m['c2'])),
        ('(x1 - x2) + x2', lambda m, emu=None: m['x1']),
        ('(x1 + 0)', lambda m, emu=None: m['x1']),
        ('(x1 + x1)', lambda m, emu=None: m['x1'] * Const(2, m['x1'].getWidth())),
        ('(x1 + x2) + x1', lambda m, emu=None: m['x2'] + (m['x1'] * Const(2,m['x1'].getWidth()))),
        ('(x1 * c1) + x1', lambda m, emu=None: m['x1'] * Const( m['c1'] + 1, m['x1'].getWidth())),
    ]),

    SYMT_OPER_SUB: xpandrules([
        ('(x1 - c1) - (x2 - c2)',
            lambda m,emu=None: addsub(m['x1'] - m['x2'], -(m['c1']-m['c2']))), # ((x1 - c1) + c2) - x2 # x1 - (c1 - c2) - x2 # (x1 - x2) - (c1 - c2)
        ('(x1 - c1) - (x2 + c2)', lambda m,emu=None: addsub(m['x1'] - m['x2'], -(m['c1'] + m['c2']))), # x1 - (c1 + c2) - x2 # (x1 - x2) - (c1 + c2)
        ('(c1 - x1) - (x2 + c2)', # (0 - x1) + c1 - x2 - c2 # ((0 - x1) - x2) + (c1-c2)
            lambda m,emu=None: addsub(symneg(m['x1']) - m['x2'], m['c1'] - m['c2'])),
        ('(x1 + c1) - (x2 - c2)', lambda m,emu=None: addsub(m['x1'] - m['x2'], m['c1'] + m['c2'])), # x1 + (c1 + c2) - x2 # (x1 - x2) + (c1 + c2)
        ('(x1 + c1) - (x2 + c2)', lambda m,emu=None: addsub(m['x1'] - m['x2'], m['c1'] - m['c2'])), # x1 + (c1 - c2) - x2 # (x1 - x2) + (c1 - c2)
        #('(x + x) - (x * 2)', lambda m,emu=None:

        ('(x1 + c1) - c2', lambda m,emu=None: addsub(m['x1'], m['c1'] - m['c2'])),  # x1 + (c1 - c2) #
        ('(x1 - c1) - c2', lambda m,emu=None: addsub(m['x1'], -(m['c1'] + m['c2']))),  # x1 - (c1 + c2) #
        ('(c1 - x1) - c2', lambda m,emu=None: sub_c_x(m['c1'] - m['c2'], m['x1'])), # (c1 - c2) - x1 #
        ('(x1 + x2) - x2', lambda m, emu=None: m['x1']),

        ('c1 - (x1 - c2)', lambda m,emu=None: sub_c_x(m['c1'] + m['c2'], m['x1'])), # (c1 + c2) - x1 # 
        ('c1 - (c2 - x1)', lambda m,emu=None: addsub(m['x1'], m['c1'] - m['c2'])),#  (c1 + x1) - c2 # (x1 + c1) - c2 # x1 + (c1 - c2) #
        ('c1 - (x1 + c2)', lambda m,emu=None: sub_c_x(m['c1'] - m['c2'], m['x1'])), #  (c1 - c2) - x1 # 

        ('(x1 - 0)', lambda m,emu=None: m['x1']),
        ('(x1 - x1)', lambda m,emu=None: 0),
    ]),

    SYMT_OPER_AND: xpandrules([
        ('(x1 & c1) & (x2 & c2)', lambda m,emu=None: andmask(m['x1'] & m['x2'], m['c1'] & m['c2'])),
        ('(x1 & c1) & c2', lambda m,emu=None: andmask(m['x1'], m['c1'] & m['c2'])),
        ('(x1 & c1)', lambda m,emu=None: andmask(m['x1'], m['c1'])),
        ('(x1 & x1)', lambda m,emu=None: m['x1']),
    ]),

    SYMT_OPER_OR: xpandrules([
        ('(x1 | c1) | (x2 | c2)', lambda m,emu=None: ormask(m['x1'] | m['x2'], m['c1'] | m['c2'])),
        ('(x1 | c1) | c2', lambda m,emu=None: ormask(m['x1'], m['c1'] | m['c2'])),
        ('(x1 | c1)', lambda m,emu=None: ormask(m['x1'], m['c1'])),
        ('(x1 | x1)', lambda m,emu=None: m['x1']),
    ]),

    SYMT_OPER_XOR: xpandrules([
        ('(x1 ^ c1) ^ c2', lambda m,emu=None: m['x1'] ^ Const( m['c1'] ^ m['c2'], m['x1'].getWidth())),
        ('(x1 ^ x1)', lambda m,emu=None: 0),
        ('(x1 ^ 0)', lambda m,emu=None: m['x1']),
    ]),

    SYMT_OPER_MUL: xpandrules([
        ('(x1 * c1) * (x2 * c2)', lambda m,emu=None: mulbase(m['x1'] * m['x2'], m['c1'] * m['c2'])),
        # NOT OK ('(x1 / c1) * c2', lambda m,emu=None: muldiv(m['x1'],m['c2'],m['c1'])),
        ('(x1 * c1) * c2', lambda m,emu=None: mulbase(m['x1'], m['c1'] * m['c2'])),
        ('(x1 * c1)', lambda m,emu=None: mulbase(m['x1'], m['c1'])),
    ]),

    SYMT_OPER_DIV: xpandrules([
        ('(x1 * c1) / c2', lambda m, emu=None: muldiv(m['x1'],m['c1'],m['c2'])),
        ('(x1 / c1)', lambda m, emu=None: divbase_vc(m['x1'], m['c1'])),
        ('(c1 / x1)', lambda m, emu=None: divbase_cv(m['c1'], m['x1'])),
        ('(x1 / x1)', lambda m, emu=None: 1),
    ]),

    SYMT_OPER_POW: xpandrules([
        ('(x1 ** 1)', lambda m, emu=None: m['x1']),
        ('(1 ** x1)', lambda m, emu=None: 1),
        ('(x1 ** 0)', lambda m, emu=None: 1),
        ('(0 ** x1)', lambda m, emu=None: 0),
    ]),

    SYMT_OPER_RSHIFT: xpandrules([
        ('(x1 >> 0)', lambda m, emu=None: m['x1']),
        ('(0 >> x1)', lambda m, emu=None: 0),
        ('(x1 >> c1)', lambda m, emu=None: divbase_vc(m['x1'], 2**m['c1'])),
    ]),

    SYMT_OPER_LSHIFT: xpandrules([
        ('(x1 << 0)', lambda m, emu=None: m['x1']),
        ('(0 << x1)', lambda m, emu=None: 0),
        ('(x1 << c1)', lambda m, emu=None: mulbase(m['x1'], 2**m['c1'])),
    ]),

    SYMT_CON_EQ: xpandrules([
        ('(x1 == x1)', lambda m, emu=None: 1),
    ]),

    SYMT_CON_NE: xpandrules([
        ('(x1 != x1)', lambda m, emu=None: 0),
    ]),
}

def reduceoper(sym,emu=None):
    '''
    Apply the current set of operator reducers to the given
    SymbolikBase.  Sym *must* be an instance of the
    Operator(SymbolikBase) class..
    '''
    if not reducers.get(sym.symtype):
        return
    for symtmp, reducer in reducers.get(sym.symtype):
        m = ismatch(sym, symtmp)
        if m is not None:
            ret = reducer(m, emu=emu)
            # do this to much simplify reducers...
            if type(ret) is int:
                ret = Const(ret,sym.getWidth())
            return ret
