'''
This module implements the SymbolikExpressionParser which is
a form of syntactic sugar for creating symbolik states and
constraints from humon input.
'''
import ast

import vivisect.const as v_const

import vivisect.symboliks.common as v_s_com
import vivisect.symboliks.effects as v_s_eff

op2op = {
    ast.Pow: v_s_com.o_pow,
    ast.Add: v_s_com.o_add,
    ast.Sub: v_s_com.o_sub,
    ast.Div: v_s_com.o_div,
    ast.Mult: v_s_com.o_mul,
    ast.BitOr: v_s_com.o_or,
    ast.BitAnd: v_s_com.o_and,
    ast.BitXor: v_s_com.o_xor,
    ast.LShift: v_s_com.o_lshift,
    ast.RShift: v_s_com.o_rshift,
}

cmp2cons = {
    ast.LtE: v_s_com.le,
    ast.GtE: v_s_com.ge,
    ast.Lt: v_s_com.lt,
    ast.Gt: v_s_com.gt,
    ast.Eq: v_s_com.eq,
    ast.NotEq: v_s_com.ne,
}

defexp = {}
def symexp(expr, defwidth=4):
    p = defexp.get(defwidth)
    if p is None:
        p = SymbolikExpressionParser(defwidth=defwidth)
        defexp[defwidth] = p
    return p.parseExpression(expr)

class SymbolikExpressionParser:
    '''
    A parser which implements a "translator" for a simplified
    pythonic notation for creating symboliks states.
    '''
    def __init__(self, defwidth=4):
        self._sym_defwidth = defwidth

    def parseExpression(self, expr):
        '''
        Parse a pythonic expression into symboliks state.

        Example:
            vw = vivisect.VivWorkspace()
            vw.setMeta('Architecture','i386')

            p = SymbolikExpressionParser(defwidth=vw.psize)

            # If all var/imm elements are the "default width":
            s = p.parseExpression('x + 30')

            # Specifying index notation to override width:
            s = p.parseExpression('x[2] + 30')
        '''
        a = ast.parse(expr)
        return self.astToSymboliks(a.body[0])

    def astToSymboliks(self, a):

        if isinstance(a, ast.Assign):
            if len(a.targets) != 1:
                raise Exception('Unsupported multi-asignment: %s' % ast.dump(a))
            if not isinstance(a.targets[0], ast.Name):
                raise Exception('Unsupported Asigment: %s' % ast.dump(a))

            sym = self.astToSymboliks(a.value)
            return v_s_eff.SetVariable(0, a.targets[0].id, sym)

        if isinstance(a, ast.Compare):
            v1 = self.astToSymboliks(a.left)
            v2 = self.astToSymboliks(a.comparators[0])
            cons = cmp2cons.get(a.ops[0].__class__)
            if not cons:
                raise Exception('Unhandled Compare Type: %s' % (ast.dump(a)))

            return cons(v1, v2)

        if isinstance(a, ast.Expr):
            return self.astToSymboliks(a.value)

        if isinstance(a, ast.BinOp):
            left = self.astToSymboliks(a.left)
            right = self.astToSymboliks(a.right)

            # assume basic width promotion
            widths = []
            if not left.symtype == v_const.SYMT_CONST:
                widths.append(left.getWidth())

            if not right.symtype == v_const.SYMT_CONST:
                widths.append(right.getWidth())

            if not widths:
                widths.append(self._sym_defwidth)

            width = max(widths)

            myop = op2op.get(a.op.__class__)
            if myop is None:
                raise Exception('Unsupported Op: %r' % a.op)

            return myop(left, right, width)

        if isinstance(a, ast.Name):
            return v_s_com.Var(a.id, self._sym_defwidth)

        if isinstance(a, ast.Constant):
            if not isinstance(a.value, int):
                raise Exception('Unsupported constant type: %s' % type(a.value))
            return v_s_com.Const(a.value, self._sym_defwidth)

        if isinstance(a, ast.Subscript):
            # value is what's being subscripted
            # slice is either Slice or Index
            # For "index" we assume they mean to specify width
            slclass = a.slice.__class__
            # TODO: support ast.Name for variable assignment?
            if slclass == ast.Constant:
                ival = a.slice.value
                if isinstance(ival, int):
                    pass
                elif isinstance(ival, ast.Constant):
                    ival = ival.value
                else:
                    raise Exception('Unsupported Expression (symbolik width index)')

                # Override width for "value"
                value = self.astToSymboliks(a.value)
                if value.symtype == v_const.SYMT_VAR:
                    return v_s_com.Var(value.name, ival)

                if value.symtype == v_const.SYMT_CONST:
                    return v_s_com.Const(value.value, ival)

                raise Exception('Unsupported Expression (symbolik width on %s)' % value.__class__.__name__)

            if slclass == ast.Slice:
                # so far we only support mem[foo:bar] syntax
                if a.slice.step is not None:
                    raise Exception('Unsupported Step Slice: %s' % ast.dump(a))

                if not isinstance(a.value, ast.Name):
                    raise Exception('Unsupported Slice Syntax: %s' % ast.dump(a))

                if a.value.id == 'mem':
                    # A memory slice expression
                    symaddr = self.astToSymboliks(a.slice.lower)
                    symsize = self.astToSymboliks(a.slice.upper)
                    return v_s_com.Mem(symaddr, symsize)

            raise Exception('Unsupported Subscript: %s' % ast.dump(a))

        if isinstance(a, ast.Call):
            funcsym = self.astToSymboliks(a.func)
            argsyms = [self.astToSymboliks(a) for a in a.args]
            return v_s_com.Call(funcsym, self._sym_defwidth, argsyms=argsyms)

        if isinstance(a, ast.Attribute):
            # handle module.function viv style symbols
            if not isinstance(a.value, ast.Name):
                raise Exception('Unsupported Attribute Base: %s' % ast.dump(a))
            symname = '%s.%s' % (a.value.id, a.attr)
            return v_s_com.Var(symname, self._sym_defwidth)

        raise Exception('Unsupported AST Element: %s' % ast.dump(a))
