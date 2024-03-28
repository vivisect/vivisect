import unittest

from vivisect.symboliks.common import Var, Const, Arg, Constraint, Call, Mem, \
                                      o_add, o_sub, o_lshift, eq, ne, o_or, o_div, o_and, o_rshift
from vivisect.symboliks.effects import ReadMemory, WriteMemory, SetVariable, \
                                       CallFunction, ConstrainPath

from vivisect.symboliks.tests.helpers import MockEmulator
from vivisect.tests.helpers import MockVw

# Algebraic notations to test:
# idempotency, associativity, commutative, distributive, double negation, de morgans


def walker(path, cur, ctx):
    ctx.append(cur)

class TestSymbolikEffects(unittest.TestCase):
    def test_readmem(self):
        # idempotent
        addr = Var('eax', 4)
        size = Var('GetFileSize', 4)
        rm = ReadMemory(0x44, addr, size)
        self.assertEqual(str(rm), '[ eax : GetFileSize ]')
        rm.reduce()
        self.assertEqual(rm, ReadMemory(0x59, addr, size))

        # reduction
        addr = ((((Var('eax', 4) * Var('ebx', 4) + Const(9, 4)) - Const(4, 4))) << Const(3, 4)) * Const(2, 4)
        size = ((Const(0x73, 4) | Const(0x84, 4)) | Const(0xCC00, 4)) ^ Var('ecx', 4)
        rm = ReadMemory(0x44, addr, size)
        rm.reduce()
        self.assertEqual(str(rm), '[ (((eax * ebx) + 5) * 16) : (0x0000ccf7 ^ ecx) ]')
        self.assertEqual(str(rm.symaddr), '(((eax * ebx) + 5) * 16)')
        self.assertEqual(str(rm.symsize), '(0x0000ccf7 ^ ecx)')

        # walkTree
        addr = (Var('edx', 4) + Var('mm0', 4)) - Var('edx', 4)
        addr <<= (Var('foo', 4) + Var('foo', 4) - (Var('foo', 4) * Const(2, 4)))
        size = (Var('bar', 4) - Const(0x19, 4)) - (Var('biz', 4) - Const(0x20, 4))
        rm = ReadMemory(0x44, addr, size)
        visited = []
        rm.walkTree(walker, ctx=visited)
        answer = [
            'edx',
            'mm0',
            '(edx + mm0)',
            'edx',
            '((edx + mm0) - edx)',
            'foo',
            'foo',
            '(foo + foo)',
            'foo',
            '2',
            '(foo * 2)',
            '((foo + foo) - (foo * 2))',
            '(((edx + mm0) - edx) << ((foo + foo) - (foo * 2)))',
            'bar',
            '25',
            '(bar - 25)',
            'biz',
            '32',
            '(biz - 32)',
            '((bar - 25) - (biz - 32))',
        ]
        strd = [str(x) for x in visited]
        self.assertEqual(answer, strd)
        self.assertEqual(str(rm), '[ (((edx + mm0) - edx) << ((foo + foo) - (foo * 2))) : ((bar - 25) - (biz - 32)) ]')
        rm.reduce()
        self.assertEqual(str(rm), '[ mm0 : ((bar - biz) + 7) ]')

        # application
        emu = MockEmulator(MockVw())
        emu.setSymVariable('mm0', Var('bar', 4))
        emu.setSymVariable('biz', Const(4, 4))
        new_rm = rm.applyEffect(emu)
        self.assertEqual(str(new_rm), '[ bar : ((bar - 4) + 7) ]')
        new_rm.reduce()
        self.assertEqual(str(new_rm), '[ bar : (bar + 3) ]')

    def test_writemem(self):
        # reduction
        msg = 'the quick brown dog'
        base = Arg(0, 4) * Const(8, 4) | Const(0x410000, 4)
        size = Const(1, 4)

        writes = []
        for c in msg:
            valu = Const(ord(c), 4)
            wm = WriteMemory(0x44, base, size, valu)
            base += Const(1, 4)
            writes.append(wm)
        answer = [
            '[ ((arg0 * 8) | 0x00410000) : 1 ] = 116',
            '[ (((arg0 * 8) | 0x00410000) + 1) : 1 ] = 104',
            '[ (((arg0 * 8) | 0x00410000) + 2) : 1 ] = 101',
            '[ (((arg0 * 8) | 0x00410000) + 3) : 1 ] = 32',
            '[ (((arg0 * 8) | 0x00410000) + 4) : 1 ] = 113',
            '[ (((arg0 * 8) | 0x00410000) + 5) : 1 ] = 117',
            '[ (((arg0 * 8) | 0x00410000) + 6) : 1 ] = 105',
            '[ (((arg0 * 8) | 0x00410000) + 7) : 1 ] = 99',
            '[ (((arg0 * 8) | 0x00410000) + 8) : 1 ] = 107',
            '[ (((arg0 * 8) | 0x00410000) + 9) : 1 ] = 32',
            '[ (((arg0 * 8) | 0x00410000) + 10) : 1 ] = 98',
            '[ (((arg0 * 8) | 0x00410000) + 11) : 1 ] = 114',
            '[ (((arg0 * 8) | 0x00410000) + 12) : 1 ] = 111',
            '[ (((arg0 * 8) | 0x00410000) + 13) : 1 ] = 119',
            '[ (((arg0 * 8) | 0x00410000) + 14) : 1 ] = 110',
            '[ (((arg0 * 8) | 0x00410000) + 15) : 1 ] = 32',
            '[ (((arg0 * 8) | 0x00410000) + 16) : 1 ] = 100',
            '[ (((arg0 * 8) | 0x00410000) + 17) : 1 ] = 111',
            '[ (((arg0 * 8) | 0x00410000) + 18) : 1 ] = 103',
        ]

        for idx, write in enumerate(writes):
            write.reduce()
            self.assertEqual(str(write), answer[idx])

        # walkTree
        addr = Mem(Call(Var('seek', 4), Const(4, 4)), Const(16, 4))
        size = Var('ecx', 4)
        valu = Arg(0, 4)
        wm = WriteMemory(0x44, addr, size, valu)

        answer = [
            Arg(0, 4),
            Var('seek', 4),
            Call(Var('seek', 4), Const(4, 4)),
            Const(16, 4),
            Mem(Call(Var('seek', 4), Const(4, 4)), Const(16, 4)),
            Var('ecx', 4)
        ]
        visited = []
        wm.walkTree(walker, ctx=visited)
        self.assertEqual(answer, visited)

        # application
        emu = MockEmulator(MockVw())
        addr = Call(Var('malloc', 4), Const(4, 4), argsyms=[Var('eax', 4)])
        size = (Const(2, 4) ** Var('ebx', 4)) >> Const(2, 4)
        size *= Const(4, 4)
        valu = Mem(Const(0x41424344, 4), Const(8, 4))
        wm = WriteMemory(0x44, addr, size, valu)

        emu.setSymVariable('ebx', Const(6, 4))
        newwm = wm.applyEffect(emu)
        newwm.reduce(emu=emu)
        self.assertEqual(str(newwm), '[ malloc(eax) : 64 ] = mem[0x41424344:8]')

    def test_setvar(self):
        # reduction
        valu = Var('esp', 4) >> Var('ebp', 4)
        sv = SetVariable(0x44, 'vivisect', valu)
        self.assertEqual(str(sv), 'vivisect = (esp >> ebp)')

        valu = eq(Var('eax', 4), Var('eax', 4))
        sv = SetVariable(0x44, 'ultra', valu)
        self.assertEqual(str(sv), 'ultra = (eax == eax)')
        sv.reduce()
        self.assertEqual(str(sv), 'ultra = 1')

        # walkTree
        valu = ne(Const(0, 1), Const(0, 2))
        for i in range(8):
            valu |= Const(0x2 << i, 4)
        sv = SetVariable(0x44, 'vtrace', valu)
        visited = []
        sv.walkTree(walker, ctx=visited)
        answer = [
            Const(0, 1),
            Const(0, 2),
            ne(Const(0, 1), Const(0, 2)),
            Const(2, 4),
            o_or(ne(Const(0, 1), Const(0, 2)), Const(2, 4), 1),
            Const(4, 4),
            o_or(o_or(ne(Const(0, 1), Const(0, 2)), Const(2, 4), 1), Const(4, 4), 1),
            Const(8, 4),
            o_or(o_or(o_or(ne(Const(0, 1), Const(0, 2)), Const(2, 4), 1), Const(4, 4), 1), Const(8, 4), 1),
            Const(0x10, 4),
            o_or(o_or(o_or(o_or(ne(Const(0, 1), Const(0, 2)), Const(2, 4),1), Const(4, 4), 1), Const(8, 4), 1), Const(0x10, 4), 1),
            Const(0x20, 4),
            o_or(o_or(o_or(o_or(o_or(ne(Const(0, 1), Const(0, 2)), Const(2, 4), 1), Const(4, 4), 1), Const(8, 4), 1),Const(0x10, 4), 1), Const(0x20, 4), 1),
            Const(0x40, 4),
            o_or(o_or(o_or(o_or(o_or(o_or(ne(Const(0, 1), Const(0, 2)), Const(2, 4), 1),Const(4, 4), 1), Const(8, 4), 1), Const(0x10, 4), 1), Const(0x20, 4), 1), Const(0x40, 4), 1),
            Const(0x80, 4),
            o_or(o_or(o_or(o_or(o_or(o_or(o_or(ne(Const(0, 1), Const(0, 2)), Const(2, 4), 1),Const(4, 4), 1), Const(8, 4), 1), Const(0x10, 4), 1), Const(0x20, 4), 1), Const(0x40, 4), 1), Const(0x80, 4), 1),
            Const(0x100, 4),
            o_or(o_or(o_or(o_or(o_or(o_or(o_or(o_or(ne(Const(0, 1),Const(0, 2)),Const(2, 4), 1), Const(4, 4), 1), Const(8, 4), 1), Const(0x10, 4), 1), Const(0x20, 4), 1), Const(0x40, 4), 1),Const(0x80, 4), 1), Const(0x100, 4), 1)
        ]
        self.assertEqual(visited, answer)
        sv.reduce()
        self.assertEqual(sv, SetVariable(0x9001, 'vtrace', Const(254, 4)))

        # application
        emu = MockEmulator(MockVw())
        sv.applyEffect(emu)
        self.assertEqual(emu.getSymVariable('vtrace'), Const(254, 4))

    def test_callfunc(self):
        # reduction, with and without argsyms
        funcsym = Var('NeatoBurrito', 4)
        argsyms = [
            (Const(1, 4) ** Var('edx', 4)) ^ Const(0x10, 4),
            (Var('eax', 4) ^ Var('eax', 4) | Const(0x10, 4)) << Const(0, 4),
            (Var('ebx', 4) & Var('ebx', 4)) | Const(0x40, 4) | Const(0x80, 4),
            Mem(Const(0x41414141, 4), Const(32, 4)),
        ]
        cf = CallFunction(0x44, funcsym, argsyms=argsyms)
        self.assertEqual(str(cf), 'NeatoBurrito(((1 ** edx) ^ 16),(((eax ^ eax) | 16) << 0),(((ebx & ebx) | 64) | 128),mem[0x41414141:32])')
        cf.reduce()
        self.assertEqual(str(cf), 'NeatoBurrito(17,16,(ebx | 192),mem[0x41414141:32])')

        # walkTree
        funcsym = Var('NeatoBurrito', 4)
        argsyms = [
            (Var('eax', 4) + Const(47, 4)) + (Var('ebx', 4) + Const(12, 4)),
            Var('foo', 4) & Var('foo', 4),
            Var('eax', 4) / Const(4, 4),
            Var('eax', 4) >> Const(2, 4),
            Const(4, 4) / Var('eax', 4),
        ]
        cf = CallFunction(0x44, funcsym, argsyms=argsyms)
        answer = [
            Var('NeatoBurrito', 4),
            Var('eax', 4),
            Const(47, 4),
            o_add(Var("eax", 4), Const(47, 4), 4),
            Var('ebx', 4),
            Const(12, 4),
            o_add(Var('ebx', 4), Const(12, 4), 4),
            (Var('eax', 4) + Const(47, 4)) + (Var('ebx', 4) + Const(12, 4)),
            Var('foo', 4),
            Var('foo', 4),
            o_and(Var('foo', 4), Var('foo', 4), 4),
            Var('eax', 4),
            Const(4, 4),
            o_div(Var('eax', 4), Const(4, 4), 4),
            Var('eax', 4),
            Const(2, 4),
            o_rshift(Var('eax', 4), Const(2, 4), 4),
            Const(4, 4),
            Var('eax', 4),
            o_div(Const(4, 4), Var('eax', 4), 4),
        ]
        visited = []
        cf.walkTree(walker, ctx=visited)
        self.assertEqual(visited, answer)

        # application, with argsyms
        emu = MockEmulator(MockVw())
        emu.setSymVariable('eax', Const(100, 4))
        newcf = cf.applyEffect(emu=emu)
        newcf.reduce()
        self.assertEqual(str(newcf), 'NeatoBurrito((ebx + 159),foo,25,25,0)')

        # application, without argsyms
        # by itself, emu.applyFunctionCall is just a NOP
        emu = MockEmulator(MockVw())
        funcsym = Var('ebx', 4)
        cf = CallFunction(0x44, funcsym)
        newcf = cf.applyEffect(emu=emu)
        newcf.reduce()
        self.assertEqual(newcf, cf)

    def test_constrainpath(self):
        # reduction
        addrsym = Var('eax', 4) * Const(4, 4) + Const(0x4357, 4)
        consym = eq(Var('ebx', 4), Var('ebx', 4))
        cons = ConstrainPath(0x44, addrsym, consym)
        self.assertEqual(repr(cons), 'ConstrainPath( 0x00000044, o_add(o_mul(Var("eax", width=4),Const(0x00000004,4),4),Const(0x00004357,4),4), eq(Var("ebx", width=4),Var("ebx", width=4)) )')
        cons.reduce()
        self.assertEqual(repr(cons), 'ConstrainPath( 0x00000044, o_add(o_mul(Var("eax", width=4),Const(0x00000004,4),4),Const(0x00004357,4),4), Const(0x00000001,4) )')

        # walkTree
        addrsym = Var('eax', 4)
        consym = eq(eq(Var('ebx', 4), Var('edx', 4)), Const(1, 4))
        cons = ConstrainPath(0x44, addrsym, consym)
        visited = []

        cons.walkTree(walker, ctx=visited)
        answer = [
            Var('ebx', 4),
            Var('edx', 4),
            eq(Var('ebx', 4), Var('edx', 4)),
            Const(1, 4),
            eq(eq(Var('ebx', 4), Var('edx', 4)), Const(1, 4)),
        ]
        self.assertEqual(visited, answer)

        # application
        emu = MockEmulator(MockVw())
        addrsym = Var('ebx', 4)
        consym = eq(eq(Var('eax', 4), Var('ecx', 4)), Const(1, 4))
        cons = ConstrainPath(0x44, addrsym, consym)
        emu.setSymVariable('eax', Const(44, 4))
        emu.setSymVariable('ecx', Const(36, 4))
        newcons = cons.applyEffect(emu)
        newcons.reduce()
        self.assertEqual(newcons, ConstrainPath(0x1994578, Var('ebx', 4), Const(0, 4)))
