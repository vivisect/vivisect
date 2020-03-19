import copy
import unittest

import vivisect
import vivisect.symboliks.emulator as vs_emu
from vivisect.symboliks.common import *
from vivisect.symboliks.expression import symexp

ast = o_add(
        o_add(
            o_add(
                o_add(
                    o_sub(
                        o_sub(
                            o_add(
                                o_add(
                                    o_add(
                                        o_add(
                                            o_add(
                                                o_add(
                                                    o_sub(
                                                        o_sub(
                                                            o_sub(
                                                                o_sub(
                                                                    o_sub(
                                                                        o_sub(
                                                                            o_sub(
                                                                                Const(0xbfb00000,8)
                                                                                ,Const(0x00000008,8)
                                                                                ,8)
                                                                            ,Const(0x00000008,8)
                                                                            ,8)
                                                                        ,Const(0x00000008,8)
                                                                        ,8)
                                                                    ,Const(0x00000008,8)
                                                                    ,8)
                                                                ,Const(0x00000008,8)
                                                                ,8)
                                                            ,Const(0x00000008,8)
                                                            ,8)
                                                        ,Const(0x00000068,8)
                                                        ,8)
                                                    ,Const(0x00000068,8)
                                                    ,8)
                                                ,Const(0x00000008,8)
                                                ,8)
                                            ,Const(0x00000008,8)
                                            ,8),
                                            o_add(
                                                o_add(
                                                    o_add(
                                                        o_sub(
                                                            o_sub(
                                                                o_sub(
                                                                    o_sub(
                                                                        o_sub(
                                                                            o_sub(
                                                                                o_sub(
                                                                                    Const(0xff010,8)
                                                                                    ,Const(0x00000008,8)
                                                                                    ,8)
                                                                                ,Const(0x00000008,8)
                                                                                ,8)
                                                                            ,Const(0x00000008,8)
                                                                            ,8)
                                                                        ,Const(0x00000008,8)
                                                                        ,8)
                                                                    ,Const(0x00000008,8)
                                                                    ,8)
                                                                ,Const(0x00000008,8)
                                                                ,8)
                                                            ,Const(0x00000068,8)
                                                            ,8)
                                                        ,Const(0x00000068,8)
                                                        ,8)
                                                    ,Const(0x00000008,8)
                                                    ,8)
                                                ,Const(0x00000008,8)
                                                ,8)
                                        #,Const(0x00000008,8)
                                        ,8)
                                    ,Const(0x00000008,8)
                                    ,8)
                                ,Const(0x00000008,8)
                                ,8)
                            ,Const(0x00000008,8)
                            ,8)
                        ,Const(0x00000008,8)
                        ,8)
                    ,Const(0x00000008,8)
                    ,8)
                ,Const(0x00000008,8)
                ,8)
            ,Const(0x00000008,8)
            ,8)
        ,Const(0x00000008,8)
        ,8)

ast1 = o_add(
        o_add(
            o_sub(
                o_add(
                    o_sub(
                        Const(0xbfb00000,8)
                        ,Const(0x00000008,8)
                        ,8)
                    ,o_add(
                        Const(0x000ff000,8)
                        ,Const(0x00000008,8)
                        ,8)
                    ,8)
                ,Const(0x00000008,8)
                ,8)
            ,Const(0x00000008,8)
            ,8)
        ,Const(0x00000008,8)
        ,8)

ast2 = o_add(
        o_add(
            o_sub(
                o_add(
                    o_sub(
                        Const(0xbfb00000,8)
                        ,Mem(
                            Arg(0,width=8),
                            Const(0x00000008, 8)
                            )
                        ,8)
                    ,o_add(
                        Const(0x000ff000,8)
                        ,Const(0x00000008,8)
                        ,8)
                    ,8)
                ,Const(0x00000008,8)
                ,8)
            ,Const(0x00000008,8)
            ,8)
        ,Const(0x00000008,8)
        ,8)

ast3 = o_sub(
        o_add(
            o_xor(
                o_and(
                    o_sub(
                        Mem(
                            o_add(
                                Arg(
                                    0,width=8)
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

ast4 = o_sub(
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

ast5 = o_add(
            o_add(
                o_add(
                    Const(0x00000000,8)
                    ,Const(0x00000001,8)
                    ,8)
                ,o_add(
                    Const(0x00000002,8)
                    , Const(0x00000003,8)
                    ,8)
                ,8)
            ,Const(0x00000004,8)
            ,8)

answer5 = (
        Const(0x00000000,8),
        Const(0x00000001,8),
        o_add(Const(0x00000000,8),Const(0x00000001,8),8),
        Const(0x00000002,8),
        Const(0x00000003,8),
        o_add(Const(0x00000002,8),Const(0x00000003,8),8),
        o_add(o_add(Const(0x00000000,8),Const(0x00000001,8),8),o_add(Const(0x00000002,8),Const(0x00000003,8),8),8),
        Const(0x00000004,8),
        o_add(o_add(o_add(Const(0x00000000,8),Const(0x00000001,8),8),o_add(Const(0x00000002,8),Const(0x00000003,8),8),8),Const(0x00000004,8),8),
        )
reduced5 = Const(0x0000000a,8)


class TestWalkTree(unittest.TestCase):
    '''
    '''
    def test_full_pass(self):
        def cb(path, cur, ctx):
            ctx['path'].append(cur)

        testast = copy.deepcopy(ast3)
        path = []
        ctx = {'path': path}

        testast.walkTree(cb, ctx)

        print "AST results: \n\t" + '\n\t'.join([repr(x) for x in path])
        vw = vivisect.VivWorkspace()
        vw.addMemoryMap(0x20000000, 7, 'foo', '@'*200)
        emu = vs_emu.SymbolikEmulator(vw)
        print "reduced: " + repr(testast.reduce())

    def test_full_pass5(self):
        def cb(path, cur, ctx):
            ctx['path'].append(cur)

        testast = copy.deepcopy(ast5)
        path = []
        ctx = {'path': path}

        testast.walkTree(cb, ctx)

        print "AST results: \n\t" + '\n\t'.join([repr(x) for x in path])
        self.assertEqual(answer5, path)
        vw = vivisect.VivWorkspace()
        vw.addMemoryMap(0x20000000, 7, 'foo', '@'*200)
        emu = vs_emu.SymbolikEmulator(vw)
        print "reduced: " + repr(testast.reduce())
        


