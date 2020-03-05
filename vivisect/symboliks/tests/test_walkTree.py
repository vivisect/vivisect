import copy
import unittest

from vivisect.symboliks.common import *
from vivisect.symboliks.expression import symexp

ast = o_add(
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
                                                    o_add(
                                                        o_add(
                                                            o_add(
                                                                o_add(
                                                                    o_add(
                                                                        o_add(
                                                                            o_add(
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
                                                                                                                                    Const(0xbfbff000,8)
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
                                                                                                        ,Const(0x00000000,8)
                                                                                                        ,8)
                                                                                                    ,Const(0x00000000,8)
                                                                                                    ,8)
                                                                                                ,Const(0x00000000,8)
                                                                                                ,8)
                                                                                            ,Const(0x00000000,8)
                                                                                            ,8)
                                                                                        ,Const(0x00000000,8)
                                                                                        ,8)
                                                                                    ,Const(0x00000000,8)
                                                                                    ,8)
                                                                                ,Const(0x00000068,8)
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
                                            ,Const(0x00000008,8)
                                            ,8)
                                        ,Const(0x00000008,8)
                                        ,8)
                                    ,Const(0x00000008,8)
                                    ,8)
                                ,Const(0x00000000,8)
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


class TestWalkTree(unittest.TestCase):
    '''
    '''
    def test_full_pass(self):
        def cb(path, cur, ctx):
            ctx['path'].append(cur)

        testast = copy.deepcopy(ast)
        path = []
        ctx = {'path': path}

        testast.walkTree(cb, ctx)

        print "AST results: " + '\n'.join([repr(x) for x in path])



