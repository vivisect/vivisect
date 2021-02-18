import unittest

from vivisect.const import SYMT_CONST

from vivisect.symboliks.common import Arg, Var, Const, Mem, Call, \
                                      o_add, o_sub, o_xor, o_and, o_or, \
                                      evalSymbolik


def walkTree_cb(path, cur, ctx):
    ctx['path'].append(cur)


class TestWalkTree(unittest.TestCase):
    def test_mem(self):
        ctx = {'path': []}
        ast = o_sub(
                o_add(
                    o_xor(
                        o_and(
                            o_sub(
                                Mem(
                                    o_add(
                                        #Arg(0,width=8)
                                        Const(0x20000000,8)
                                        ,Const(0x00000030,8)
                                        ,8)
                                    , Const(0x00000008,8)
                                    )
                                ,o_add(
                                    Mem(
                                        o_add(
                                            Mem(
                                                #Arg(0,width=8)
                                                Const(0x20000000,8)
                                                , Const(0x00000008,8))
                                            ,Const(0x00000048,8)
                                            ,8)
                                        ,Const(0x00000008,8))
                                    ,Const(0x00000001,8)
                                    ,8)
                                ,8)
                            ,Const(0xffffffff,4)
                            ,4)
                        ,o_and(
                            o_sub(
                                Mem(
                                    o_add(
                                        #Arg(0,width=8)
                                        Const(0x20000000,8)
                                        ,Const(0x00000030,8)
                                        ,8)
                                    , Const(0x00000008,8))
                                ,o_add(
                                    Mem(
                                        o_add(
                                            Mem(
                                                #Arg(0,width=8)
                                                Const(0x20000000,8)
                                                , Const(0x00000008,8))
                                            ,Const(0x00000048,8)
                                            ,8)
                                        , Const(0x00000008,8))
                                    ,Const(0x00000001,8)
                                    ,8)
                                ,8)
                            ,Const(0xffffffff,4)
                            ,4)
                        ,4)
                    ,Const(0x00000001,8)
                ,8)
            ,Const(0x00000001,8)
            ,8)
        flattened = [Const(0x20000000,8),
                     Const(0x00000030,8),
                     o_add(Const(0x20000000,8),Const(0x00000030,8),8),
                     Const(0x00000008,8),
                     Mem(o_add(Const(0x20000000,8),Const(0x00000030,8),8), Const(0x00000008,8)),
                     Const(0x20000000,8),
                     Const(0x00000008,8),
                     Mem(Const(0x20000000,8), Const(0x00000008,8)),
                     Const(0x00000048,8),
                     o_add(Mem(Const(0x20000000,8), Const(0x00000008,8)),Const(0x00000048,8),8),
                     Const(0x00000008,8),
                     Mem(o_add(Mem(Const(0x20000000,8), Const(0x00000008,8)),Const(0x00000048,8),8), Const(0x00000008,8)),
                     Const(0x00000001,8),
                     o_add(Mem(o_add(Mem(Const(0x20000000,8), Const(0x00000008,8)),Const(0x00000048,8),8), Const(0x00000008,8)),Const(0x00000001,8),8),
                     o_sub(Mem(o_add(Const(0x20000000,8),Const(0x00000030,8),8), Const(0x00000008,8)),o_add(Mem(o_add(Mem(Const(0x20000000,8), Const(0x00000008,8)),Const(0x00000048,8),8), Const(0x00000008,8)),Const(0x00000001,8),8),8),
                     Const(0xffffffff,4),
                     o_and(o_sub(Mem(o_add(Const(0x20000000,8),Const(0x00000030,8),8), Const(0x00000008,8)),o_add(Mem(o_add(Mem(Const(0x20000000,8), Const(0x00000008,8)),Const(0x00000048,8),8), Const(0x00000008,8)),Const(0x00000001,8),8),8),Const(0xffffffff,4),4),
                     Const(0x20000000,8),
                     Const(0x00000030,8),
                     o_add(Const(0x20000000,8),Const(0x00000030,8),8),
                     Const(0x00000008,8),
                     Mem(o_add(Const(0x20000000,8),Const(0x00000030,8),8), Const(0x00000008,8)),
                     Const(0x20000000,8),
                     Const(0x00000008,8),
                     Mem(Const(0x20000000,8), Const(0x00000008,8)),
                     Const(0x00000048,8),
                     o_add(Mem(Const(0x20000000,8), Const(0x00000008,8)),Const(0x00000048,8),8),
                     Const(0x00000008,8),
                     Mem(o_add(Mem(Const(0x20000000,8), Const(0x00000008,8)),Const(0x00000048,8),8), Const(0x00000008,8)),
                     Const(0x00000001,8),
                     o_add(Mem(o_add(Mem(Const(0x20000000,8), Const(0x00000008,8)),Const(0x00000048,8),8), Const(0x00000008,8)),Const(0x00000001,8),8),
                     o_sub(Mem(o_add(Const(0x20000000,8),Const(0x00000030,8),8), Const(0x00000008,8)),o_add(Mem(o_add(Mem(Const(0x20000000,8), Const(0x00000008,8)),Const(0x00000048,8),8), Const(0x00000008,8)),Const(0x00000001,8),8),8),
                     Const(0xffffffff,4),
                     o_and(o_sub(Mem(o_add(Const(0x20000000,8),Const(0x00000030,8),8), Const(0x00000008,8)),o_add(Mem(o_add(Mem(Const(0x20000000,8), Const(0x00000008,8)),Const(0x00000048,8),8), Const(0x00000008,8)),Const(0x00000001,8),8),8),Const(0xffffffff,4),4),
                     o_xor(o_and(o_sub(Mem(o_add(Const(0x20000000,8),Const(0x00000030,8),8), Const(0x00000008,8)),o_add(Mem(o_add(Mem(Const(0x20000000,8), Const(0x00000008,8)),Const(0x00000048,8),8), Const(0x00000008,8)),Const(0x00000001,8),8),8),Const(0xffffffff,4),4),o_and(o_sub(Mem(o_add(Const(0x20000000,8),Const(0x00000030,8),8), Const(0x00000008,8)),o_add(Mem(o_add(Mem(Const(0x20000000,8), Const(0x00000008,8)),Const(0x00000048,8),8), Const(0x00000008,8)),Const(0x00000001,8),8),8),Const(0xffffffff,4),4),4),
                     Const(0x00000001,8),
                     o_add(o_xor(o_and(o_sub(Mem(o_add(Const(0x20000000,8),Const(0x00000030,8),8), Const(0x00000008,8)),o_add(Mem(o_add(Mem(Const(0x20000000,8), Const(0x00000008,8)),Const(0x00000048,8),8), Const(0x00000008,8)),Const(0x00000001,8),8),8),Const(0xffffffff,4),4),o_and(o_sub(Mem(o_add(Const(0x20000000,8),Const(0x00000030,8),8), Const(0x00000008,8)),o_add(Mem(o_add(Mem(Const(0x20000000,8), Const(0x00000008,8)),Const(0x00000048,8),8), Const(0x00000008,8)),Const(0x00000001,8),8),8),Const(0xffffffff,4),4),4),Const(0x00000001,8),8),
                     Const(0x00000001,8),
                     o_sub(o_add(o_xor(o_and(o_sub(Mem(o_add(Const(0x20000000,8),Const(0x00000030,8),8), Const(0x00000008,8)),o_add(Mem(o_add(Mem(Const(0x20000000,8), Const(0x00000008,8)),Const(0x00000048,8),8), Const(0x00000008,8)),Const(0x00000001,8),8),8),Const(0xffffffff,4),4),o_and(o_sub(Mem(o_add(Const(0x20000000,8),Const(0x00000030,8),8), Const(0x00000008,8)),o_add(Mem(o_add(Mem(Const(0x20000000,8), Const(0x00000008,8)),Const(0x00000048,8),8), Const(0x00000008,8)),Const(0x00000001,8),8),8),Const(0xffffffff,4),4),4),Const(0x00000001,8),8),Const(0x00000001,8),8)]

        ast.walkTree(walkTree_cb, ctx)
        self.assertEqual(ctx['path'], flattened)
        self.assertEqual(ctx['path'][-1], ast)

    def test_moarmem(self):
        ctx = {'path': []}
        ast = o_sub(o_add(o_xor(o_and(o_sub(Mem(o_add(Arg(0,width=8),Const(0x00000030,8),8),Const(0x00000008,8)),o_add(Mem(o_add(Mem(Const(0x20000000,8),Const(0x00000008,8)),Const(0x00000048,8),8),Const(0x00000008,8)),Const(0x00000001,8),8),8),Const(0xffffffff,4),4),o_and(o_sub(Mem( o_add( Const(0x20000000,8) ,Const(0x00000030,8) ,8) , Const(0x00000008,8)) ,o_add( Mem( o_add( Mem( Const(0x20000000,8) , Const(0x00000008,8)) ,Const(0x00000048,8) ,8) , Const(0x00000008,8)) ,Const(0x00000001,8) ,8) ,8) ,Const(0xffffffff,4) ,4) ,4) ,Const(0x00000001,8) ,8) ,Const(0x00000001,8) ,8)

        ast.walkTree(walkTree_cb, ctx)
        flattened = [Arg(0,width=8),
                     Const(0x00000030,8),
                     o_add(Arg(0,width=8),Const(0x00000030,8),8),
                     Const(0x00000008,8),
                     Mem(o_add(Arg(0,width=8),Const(0x00000030,8),8), Const(0x00000008,8)),
                     Const(0x20000000,8),
                     Const(0x00000008,8),
                     Mem(Const(0x20000000,8), Const(0x00000008,8)),
                     Const(0x00000048,8),
                     o_add(Mem(Const(0x20000000,8), Const(0x00000008,8)),Const(0x00000048,8),8),
                     Const(0x00000008,8),
                     Mem(o_add(Mem(Const(0x20000000,8), Const(0x00000008,8)),Const(0x00000048,8),8), Const(0x00000008,8)),
                     Const(0x00000001,8),
                     o_add(Mem(o_add(Mem(Const(0x20000000,8), Const(0x00000008,8)),Const(0x00000048,8),8), Const(0x00000008,8)),Const(0x00000001,8),8),
                     o_sub(Mem(o_add(Arg(0,width=8),Const(0x00000030,8),8), Const(0x00000008,8)),o_add(Mem(o_add(Mem(Const(0x20000000,8), Const(0x00000008,8)),Const(0x00000048,8),8), Const(0x00000008,8)),Const(0x00000001,8),8),8),
                     Const(0xffffffff,4),
                     o_and(o_sub(Mem(o_add(Arg(0,width=8),Const(0x00000030,8),8), Const(0x00000008,8)),o_add(Mem(o_add(Mem(Const(0x20000000,8), Const(0x00000008,8)),Const(0x00000048,8),8), Const(0x00000008,8)),Const(0x00000001,8),8),8),Const(0xffffffff,4),4),
                     Const(0x20000000,8),
                     Const(0x00000030,8),
                     o_add(Const(0x20000000,8),Const(0x00000030,8),8),
                     Const(0x00000008,8),
                     Mem(o_add(Const(0x20000000,8),Const(0x00000030,8),8), Const(0x00000008,8)),
                     Const(0x20000000,8),
                     Const(0x00000008,8),
                     Mem(Const(0x20000000,8), Const(0x00000008,8)),
                     Const(0x00000048,8),
                     o_add(Mem(Const(0x20000000,8), Const(0x00000008,8)),Const(0x00000048,8),8),
                     Const(0x00000008,8),
                     Mem(o_add(Mem(Const(0x20000000,8), Const(0x00000008,8)),Const(0x00000048,8),8), Const(0x00000008,8)),
                     Const(0x00000001,8),
                     o_add(Mem(o_add(Mem(Const(0x20000000,8), Const(0x00000008,8)),Const(0x00000048,8),8), Const(0x00000008,8)),Const(0x00000001,8),8),
                     o_sub(Mem(o_add(Const(0x20000000,8),Const(0x00000030,8),8), Const(0x00000008,8)),o_add(Mem(o_add(Mem(Const(0x20000000,8), Const(0x00000008,8)),Const(0x00000048,8),8), Const(0x00000008,8)),Const(0x00000001,8),8),8),
                     Const(0xffffffff,4),
                     o_and(o_sub(Mem(o_add(Const(0x20000000,8),Const(0x00000030,8),8), Const(0x00000008,8)),o_add(Mem(o_add(Mem(Const(0x20000000,8), Const(0x00000008,8)),Const(0x00000048,8),8), Const(0x00000008,8)),Const(0x00000001,8),8),8),Const(0xffffffff,4),4),
                     o_xor(o_and(o_sub(Mem(o_add(Arg(0,width=8),Const(0x00000030,8),8), Const(0x00000008,8)),o_add(Mem(o_add(Mem(Const(0x20000000,8), Const(0x00000008,8)),Const(0x00000048,8),8), Const(0x00000008,8)),Const(0x00000001,8),8),8),Const(0xffffffff,4),4),o_and(o_sub(Mem(o_add(Const(0x20000000,8),Const(0x00000030,8),8), Const(0x00000008,8)),o_add(Mem(o_add(Mem(Const(0x20000000,8), Const(0x00000008,8)),Const(0x00000048,8),8), Const(0x00000008,8)),Const(0x00000001,8),8),8),Const(0xffffffff,4),4),4),
                     Const(0x00000001,8),
                     o_add(o_xor(o_and(o_sub(Mem(o_add(Arg(0,width=8),Const(0x00000030,8),8), Const(0x00000008,8)),o_add(Mem(o_add(Mem(Const(0x20000000,8), Const(0x00000008,8)),Const(0x00000048,8),8), Const(0x00000008,8)),Const(0x00000001,8),8),8),Const(0xffffffff,4),4),o_and(o_sub(Mem(o_add(Const(0x20000000,8),Const(0x00000030,8),8), Const(0x00000008,8)),o_add(Mem(o_add(Mem(Const(0x20000000,8), Const(0x00000008,8)),Const(0x00000048,8),8), Const(0x00000008,8)),Const(0x00000001,8),8),8),Const(0xffffffff,4),4),4),Const(0x00000001,8),8),
                     Const(0x00000001,8),
                     o_sub(o_add(o_xor(o_and(o_sub(Mem(o_add(Arg(0,width=8),Const(0x00000030,8),8), Const(0x00000008,8)),o_add(Mem(o_add(Mem(Const(0x20000000,8), Const(0x00000008,8)),Const(0x00000048,8),8), Const(0x00000008,8)),Const(0x00000001,8),8),8),Const(0xffffffff,4),4),o_and(o_sub(Mem(o_add(Const(0x20000000,8),Const(0x00000030,8),8), Const(0x00000008,8)),o_add(Mem(o_add(Mem(Const(0x20000000,8), Const(0x00000008,8)),Const(0x00000048,8),8), Const(0x00000008,8)),Const(0x00000001,8),8),8),Const(0xffffffff,4),4),4),Const(0x00000001,8),8),Const(0x00000001,8),8)]

        self.assertEqual(ast, evalSymbolik(repr(ast)))
        self.assertEqual(ctx['path'], flattened)
        self.assertEqual(ctx['path'][-1], ast)

    def test_nested(self):
        ctx = {'path': []}
        ast = o_add(o_add(o_add(o_add(o_sub(o_sub(o_add(o_add(o_add(o_add( o_add(o_add(o_sub(o_sub(o_sub(o_sub(o_sub(o_sub(o_sub(Const(0xbfb00000,8), Const(0x00000008,8),8),Const(0x00000008,8),8),Const(0x00000008,8),8),Const(0x00000008,8),8),Const(0x00000008,8),8),Const(0x00000008,8),8),Const(0x00000068,8),8),Const(0x00000068,8),8),Const(0x00000008,8),8),Const(0x00000008,8),8),o_add(o_add(o_add(o_sub(o_sub(o_sub(o_sub(o_sub(o_sub(o_sub(Const(0xff010,8),Const(0x00000008,8),8),Const(0x00000008,8),8),Const(0x00000008,8),8),Const(0x00000008,8),8),Const(0x00000008,8),8),Const(0x00000008,8),8),Const(0x00000068,8),8),Const(0x00000068,8),8),Const(0x00000008,8),8),Const(0x00000008,8),8),8),Const(0x00000008,8),8),Const(0x00000008,8),8),Const(0x00000008,8),8),Const(0x00000008,8),8),Const(0x00000008,8),8),Const(0x00000008,8),8),Const(0x00000008,8),8),Const(0x00000008,8),8)
        ast.walkTree(walkTree_cb, ctx)
        self.assertEqual(ast.reduce(), Const(0xbfbfeff0, 8))
        self.assertEqual(ctx['path'][-1], ast)
        self.assertEqual(len(ctx['path']), 59)

    def test_flatten_constant(self):
        ctx = {'path': []}
        ast = o_add(o_add(o_add(Const(0x00000000, 8), Const(0x00000001, 8) ,8),
                           o_add(Const(0x00000002,8), Const(0x00000003, 8), 8),
                           8),
                     Const(0x00000004,8),
                     8)
        flattened = [Const(0x00000000,8),
                     Const(0x00000001,8),
                     o_add(Const(0x00000000,8),Const(0x00000001,8),8),
                     Const(0x00000002,8),
                     Const(0x00000003,8),
                     o_add(Const(0x00000002,8),Const(0x00000003,8),8),
                     o_add(o_add(Const(0x00000000,8),Const(0x00000001,8),8),o_add(Const(0x00000002,8),Const(0x00000003,8),8),8),
                     Const(0x00000004,8),
                     o_add(o_add(o_add(Const(0x00000000,8),Const(0x00000001,8),8),o_add(Const(0x00000002,8),Const(0x00000003,8),8),8),Const(0x00000004,8),8),]

        ast.walkTree(walkTree_cb, ctx)
        self.assertEqual(ctx['path'][-1], ast)
        self.assertEqual(ctx['path'], flattened)
        self.assertEqual(Const(0xa, 8), ast.reduce())

        ctx = {'path': []}
        ast = o_add(o_add(o_sub(o_add(o_sub(Const(0xbfb00000,8),
                                            Const(0x00000008,8),
                                            8),
                                      o_add(Const(0x000ff000,8),
                                            Const(0x00000008,8),
                                            8),
                                      8),
                                Const(0x00000008,8),
                                8),
                          Const(0x00000008, 8),
                          8),
                    Const(0x00000008,8),
                    8)
        flattened = [Const(0xbfb00000, 8),
                     Const(0x00000008, 8),
                     o_sub(Const(0xbfb00000, 8), Const(0x00000008, 8), 8),
                     Const(0x000ff000,8),
                     Const(0x00000008,8),
                     o_add(Const(0x000ff000,8), Const(0x00000008,8), 8),
                     o_add(o_sub(Const(0xbfb00000, 8), Const(0x00000008, 8), 8),o_add(Const(0x000ff000,8), Const(0x00000008,8), 8), 8),
                     Const(0x00000008,8),
                     o_sub(o_add(o_sub(Const(0xbfb00000,8),Const(0x00000008,8), 8), o_add(Const(0x000ff000,8), Const(0x00000008,8), 8), 8), Const(0x00000008,8), 8),
                     Const(0x00000008, 8),
                     o_add(o_sub(o_add(o_sub(Const(0xbfb00000,8), Const(0x00000008,8), 8), o_add(Const(0x000ff000,8), Const(0x00000008,8), 8), 8), Const(0x00000008,8), 8), Const(0x00000008, 8), 8),
                     Const(0x00000008,8),
                     o_add(o_add(o_sub(o_add(o_sub(Const(0xbfb00000,8), Const(0x00000008,8), 8), o_add(Const(0x000ff000,8), Const(0x00000008,8), 8), 8), Const(0x00000008,8), 8), Const(0x00000008, 8), 8), Const(0x00000008,8), 8) ]
        ast.walkTree(walkTree_cb, ctx)
        self.assertEqual(ctx['path'], flattened)
        self.assertEqual(Const(0xbfbff008, 8), ast.reduce())

    def test_memarg(self):
        ctx = {'path': []}
        ast = o_add(o_add(o_sub(o_add(o_sub(Const(0xbfb00000, 8),
                                            Mem(Arg(0, width=8), Const(0x00000008, 8)),
                                            8),
                                      o_add(Const(0x000ff000, 8),
                                            Const(0x00000008, 8),
                                            8),
                                      8),
                                Const(0x00000008,8),
                                8),
                          Const(0x00000008,8),
                          8),
                    Const(0x00000008,8),
                    8)
        flattened = [Const(0xbfb00000,8),
                     Arg(0,width=8),
                     Const(0x00000008,8),
                     Mem(Arg(0,width=8), Const(0x00000008,8)),
                     o_sub(Const(0xbfb00000,8),Mem(Arg(0,width=8), Const(0x00000008,8)),8),
                     Const(0x000ff000,8),
                     Const(0x00000008,8),
                     o_add(Const(0x000ff000,8),Const(0x00000008,8),8),
                     o_add(o_sub(Const(0xbfb00000,8),Mem(Arg(0,width=8), Const(0x00000008,8)),8),o_add(Const(0x000ff000,8),Const(0x00000008,8),8),8),
                     Const(0x00000008,8),
                     o_sub(o_add(o_sub(Const(0xbfb00000,8),Mem(Arg(0,width=8), Const(0x00000008,8)),8),o_add(Const(0x000ff000,8),Const(0x00000008,8),8),8),Const(0x00000008,8),8),
                     Const(0x00000008,8),
                     o_add(o_sub(o_add(o_sub(Const(0xbfb00000,8),Mem(Arg(0,width=8), Const(0x00000008,8)),8),o_add(Const(0x000ff000,8),Const(0x00000008,8),8),8),Const(0x00000008,8),8),Const(0x00000008,8),8),
                     Const(0x00000008,8),
                     o_add(o_add(o_sub(o_add(o_sub(Const(0xbfb00000,8),Mem(Arg(0,width=8), Const(0x00000008,8)),8),o_add(Const(0x000ff000,8),Const(0x00000008,8),8),8),Const(0x00000008,8),8),Const(0x00000008,8),8),Const(0x00000008,8),8)]
        ast.walkTree(walkTree_cb, ctx)
        self.assertEqual(ctx['path'][-1], ast)
        self.assertEqual(ctx['path'], flattened)
        answer = o_add(o_sub(Const(0x00000000,8),Mem(Arg(0,width=8), Const(0x00000008,8)),8),Const(0xbfbff010,8),8)
        self.assertEqual(answer, ast.reduce())

    def test_coverage(self):
        '''
        ((mem[piva_global(0xbfbfee08):1] | (mem[(arg0 + 72):4] & 0xffffff00)) + piva_global())
        '''
        ids = []
        piva1 = Var('piva_global', 4)
        ids.append(piva1._sym_id)
        arg = Const(0xbfbfee08, 4)
        ids.append(arg._sym_id)
        call = Call(piva1, 4, argsyms=[arg])
        ids.append(call._sym_id)
        con = Const(1, 4)
        ids.append(con._sym_id)
        mem1 = Mem(call, con)
        ids.append(mem1._sym_id)

        arg = Arg(0, 4)
        ids.append(arg._sym_id)
        addop = Const(72, 4)
        ids.append(addop._sym_id)
        add = o_add(arg, addop, 4)
        ids.append(add._sym_id)
        con = Const(4, 4)
        ids.append(con._sym_id)
        memac = Mem(add, con)
        ids.append(memac._sym_id)
        andop = Const(0xffffff00, 4)
        ids.append(andop._sym_id)
        mem2 = o_and(memac, andop, 4)
        ids.append(mem2._sym_id)
        memor = o_or(mem1, mem2, 4)
        ids.append(memor._sym_id)

        piva2 = Var('piva_global', 4)
        ids.append(piva2._sym_id)
        call2 = Call(piva2, 4, argsyms=[])
        ids.append(call2._sym_id)
        add = o_add(memor, call2, 4)
        ids.append(add._sym_id)

        traveled_ids = []
        def walkerTest(path, symobj, ctx):
            traveled_ids.append(symobj._sym_id)

        add.walkTree(walkerTest)
        self.assertEqual(traveled_ids, ids)
        self.assertEqual('((mem[piva_global(0xbfbfee08):1] | (mem[(arg0 + 72):4] & 0xffffff00)) + piva_global())', str(add))

    def test_cleanwalk(self):
        '''
        test that we don't accidentally populate the solver cache while walking the tree
        '''
        symstr = "o_add(o_xor(o_sub(Var('eax', 4), Const(98, 4), 4), Const(127, 4), 4), Const(4, 4), 4)"
        symobj = evalSymbolik(symstr)
        objs = []
        def walker(path, symobj, ctx):
            objs.append(symobj)
        symobj.walkTree(walker)

        self.assertEqual(len(objs), 7)
        for obj in objs:
            self.assertEqual(obj.cache, {})

    def test_cachewalk(self):
        '''
        Test that even if we do populate the symcache while walking we're still fine
        '''
        def populate(path, cur, ctx):
            if cur.symtype == SYMT_CONST:
                if cur.value % 2 == 0:
                    foo = str(cur)

        valu = Const(1, 4)
        for i in range(64):
            valu |= Const(i, 4)

        valu.walkTree(populate)
        populated = []
        # make sure that not all of the caches are populated, but that we can still visit all of them
        def check(path, cur, ctx):
            if cur.symtype == SYMT_CONST:
                populated.append(len(cur.cache) == 0)
        valu.walkTree(check)
        self.assertEqual(len(populated), 65)
        self.assertEqual(len([x for x in populated if x]), 33)
        self.assertEqual(len([x for x in populated if not x]), 32)

        # make sure reduction still goes through
        self.assertEqual(valu.reduce(), Const(0x3f, 4))
