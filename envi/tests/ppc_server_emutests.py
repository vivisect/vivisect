emutests = {
    'FC00F024': [
        {
            'setup': (
                ('f30', 0x4010000000000000),
                ('f0', 0x4030000000000000),
            ),
            'tests': (
                ('f30', 0x4010000000000000),
                ('f0', 0x4010000000000000),
            ),
        }
    ],  # fdiv f0,f0,f30 GOOD TEST

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
    ],  # 'add r0,r0,r4' GOOD TEST.  CR is not changed nor set

    '7C005214': [
        {
            'setup': (
                ('r0', 69),
                ('r10', 420),
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
                ('r0', 0xfffffffffffffff7),
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
                ('r0',0xfffffffffffc4000),
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
    ], # '7C000194', 'addze r0,r0

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
    ], # '7C000194', 'and r0,r0,r11'

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
    ], # '7C000B039', 'and. r0,r0,r22'

    '7C003878': [
        {
            'setup': (
                ('r0', 0b00001010),
                ('r7', 0b01011111), #r0 is ANDed with the One's complement of the value in this register (0b10100000)
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
                ('r0', 0b11111010),                                                                        #0b11111010
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
                ('r0', 0b11111010),                                                           #0b11111010
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
                ('r22', 0b01011111), #0b01011111
                ('r28', 0b01000000), #0b10111111
                ('cr0', 0b0),
            ),
            'tests': (
                ('r0', 0b00011111),
                ('r22', 0b01011111),
                ('r28', 0b01000000),
                ('cr0', 0b0100),
            ),
        }
    ], # '7EC0E079', 'andc. r0,r22,r28'

    '70000007': [
        {
            'setup': (
                ('r0', 0b10000), #(ANDed with 0b0111
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
    ], # '7EC0E079', 'andi. r0,r0,0x7'

    '7780FFF8': [
        {
            'setup': (
                ('r28',0b10001111110111101000),
                ('cr0', 0),
            ),
            'tests': (
                ('r0', 0b10000000000000000000),
                ('cr0',0b0100 ),
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

    # '4BFFFFF0': [ #Branches are broken rn 2-17-2021
    #     {
    #         'setup': (
    #             ('PC', 0x10000534),
    #         ),
    #         'tests': (
    #             ('PC', 0x10000524),
    #         )
    #     } ],
    #  '4BFFFFF0', 'b -0x10'

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
    ],  #  '7CAF5000', 'cmpd cr1,r15,r10'

    '2CA00000': [  # L = 1 CR is not being set correctly
        {
            'setup': (
                ('r0', 55000),
            ),
            'tests': (
                ('cr1', 0b0100),
            ),
        }, #test#0
        {
            'setup': (
                ('r0', 0),
            ),
            'tests': (
                ('cr1', 0b0010),
            ),
        }, #test#1
        {
            'setup': (
                ('r0', -2),
            ),
            'tests': (
                ('cr1', 0b1000),
            ),
        }
    ],  #  '2CA00000', 'cmpdi cr1,r0,0x0'

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
    ], #  '7CAA7840', 'cmpld 0,1,r10,r15

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
    ], #  '28AF0008', 'cmpldi cr1,r15,0x8'

    '7C8A3840': [  #(cmp crD,0,rA,rB)
        {
            'setup': (
                ('r10', 10),
                ('r7', 9),
            ),
            'tests': (
                ('cr1', 0b0100),
            ),
        },
        {
            'setup': (
                ('r10', 10),
                ('r7', 10),
            ),
            'tests': (
                ('cr1', 0b0010),
            ),
        },
        {
            'setup': (
                ('r10', 8),
                ('r10', 10),
            ),
            'tests': (
                ('cr1', 0b1000),
            ),
        },
    ], #  '7C8A3840', 'cmplw cr1,r10,r7' (cmp crD,0,rA,rB)

    '288A0002': [  # cmpli crD,0,rA,UIMM
        {
            'setup': (
                ('r10', 10),
            ),
            'tests': (
                ('cr1', 0b0100
                 ),
            )
        },
        {
            'setup': (
                ('r10', 1),
            ),
            'tests': (
                ('cr1', 0b1000),
            )
        },
        {
            'setup': (
                ('r10', 2),
            ),
            'tests': (
                ('cr1', 0b0010),
            )
        },
    ],  # '288A0002', 'cmplwi cr1,r10,0x2' (cmp crD,0,rA,rB)

    '7C90D000': [  # (cmp crD,0,rA,rB)
        {
            'setup': (
                ('r16', 10),
                ('r26', 1)
            ),
            'tests': (
                ('cr1', 0b0100),
            )
        },
        {
            'setup': (
                ('r16', 1),
                ('r26', 1)
            ),
            'tests': (
                ('cr1', 0b0010),
            )
        },
        {
            'setup': (
                ('r16', 0),
                ('r26', 2)
            ),
            'tests': (
                ('cr1', 0b1000),
            )
        },
    ],  # '7C90D000', 'cmpw cr1,r16,r26'

    '2C800000': [  # cmp crD,0,rA,rB
        {
            'setup': (
                ('r0', 10),
            ),
            'tests': (
                ('cr1', 0b0100),
            )
        },
        {
            'setup': (
                ('r0', 0),
            ),
            'tests': (
                ('cr1', 0b0010),
            )
        },
        {
            'setup': (
                ('r0', -10),
            ),
            'tests': (
                ('cr1', 0b1000),
            )
        },
    ],  # '2C800000', 'cmpwi cr1,r0,0x0'

    # '7C000074': [  # Unsupported ins
    #    'setup': (
    #             ('r0', 0b000001),
    #         ),
    #         'tests': (
    #             ('r0', 0b000001),
    #             ('cr0', 0b0000),
    #         )
    #     },
    #  ],  # '7C000074', 'cntlzd r0,r0 # cntlzd Unsupported instruction

    # '7C0C03D2': [ *Not working
    #     {
    #         'setup': (
    #             ('r0', 9),
    #             ('r12', 56),
    #         ),
    #         'tests': (
    #             ('r0', 6),
    #             ('r12', 56),
    #             ('cr0', 0b0100),
    #         ),
    #     }
    # ],  # 'divd r0,r12,r0'

    # '7D0A5238': [ # Unsupported ins
    #     {
    #         'setup': (
    #             ('r10', 10),
    #             ('r8', 10)
    #         ),
    #         'tests': (
    #             ('r8', 0b101),
    #         )
    #     }
    # ], #'7D0A5238', 'eqv r10,r8,r10'

    # '4C42D202': [ need more explanation
    #     {
    #         'setup': (
    #             ('r0', 9),
    #             ('r12', 56),
    #         ),
    #         'tests': (
    #             ('r0', 6),
    #             ('r12', 56),
    #             ('cr0', 0b0100),
    #         ),
    #     }
    #],  # ('4C42D202', 'crand eq,eq,cr6.eq')

    # '7D4A0774': [ # ('7D4A0774', 'extsb r10,r10') Under dev 2/22/21
    #     {
    #         'setup': (
    #             ('r10', -2),
    #         ),
    #         'tests': (
    #             ('r10', 0xfffffffe)
    #         ),
    #     }
    # ],

    # 'FC00002A': [ # ('FC00002A', 'fadd f0,f0,f0') Under Dev
    #     {
    #         'setup': (
    #             ('f0', envi.bits.floattodecimel(22.7857, 4, 1)),
    #         ),
    #         'tests': (
    #             ('f0', 0x4236491d)
    #         ),
    #     }
    # ], #  ('FC00002A', 'fadd f0,f0,f0')

    # '7C1E071E': [ # ('7C1E071E', 'isel r0,r30,r0,cr7.lt') #unsupported instruction
    #     {
    #         'setup': (
    #             ('r0',  0),
    #             ('r30', 64),
    #             ('cr7', 0xb1000),
    #
    #         ),nnnngfttttttttttttttv
    #         'tests': (
    #             ('r0', 64),
    #             ('cr7', 0b1000)
    #
    #         ),
    #     }
    # ], #  ('7C1E071E', 'isel r0,r30,r0,cr7.lt')

    #     '880A0000': [ # ('880A0000', 'lbz r0,0x0(r10)')  0x0 = D, rA = r10, rD = r0   Need to have actual value in memory referenced at r10.  Dp not know if emu is capable of loading values ionto mem yet.
    #      {
    #         'setup': (
    #             ('r10',  0x),
    #         ),
    #         'tests': (
    #             ('r0', 0x),
    #
    #         ),
    #     }
    # ], #  ('880A0000', 'lbz r0,0x0(r10)')

    #     'E81DFFF0': [ # ('E81DFFF0', 'ld r0,-0x10(r29)') Load Doubleword - Not implemented
    #      {
    #         'setup': (
    #             ('r29',  0xff),
    #             ('r0', 0)
    #         ),
    #         'tests': (
    #             ('r0', 0xf5),
    #
    #         ),
    #     }
    # ], #  ('E81DFFF0', 'ld r0,-0x10(r29)')

    #     '6D29FF00': [ # ('6D29FF00', 'xoris r9,r9,) Good test but not implemented yet
    #      {
    #         'setup': (
    #             ('r9',  0b00110011),
    #         ),
    #         'tests': (
    #             ('r9', 0b11111111000000000000000000110011),
    #
    #         ),
    #     }
    # ], #  ('6D29FF00', 'xoris r9,r9,0xff00')

    '6929FFFF': [ # ('6929FFFF', 'xori r9,r9,0xffff)
         {
            'setup': (
                ('r9',  0b0000000000110011),
                #         1111111111111111
            ),
            'tests': (
                ('r9', 0b1111111111001100),

            ),
        }
    ], #  ('6929FFFF', 'xori r9,r9,0xffff)

    '7D484279': [  # ('7D484279', 'xor. r8,r10,r8')
        {
            'setup': (
                ('r8' , 0b0000000000110011),
                ('r10', 0b0000000000001011)
            ),
            'tests': (
                ('r8', 0b00111000),
                ('cr0', 0b0100)
            ),
        }
    ],  # ('7D484279', 'xor. r8,r10,r8')

    '7D294278': [  # ('7D294278', 'xor r9,r9,r8')
        {
            'setup': (
                ('r9', 0b0000000000110011),
                ('r8', 0b0000000000001011)
            ),
            'tests': (
                ('r9', 0b00111000),
            ),
        }
    ],  # ('7D294278', 'xor r9,r9,r8')

    '38000011': [  # ('380011', 'li r0,0x11')
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

    # 'FC00069C': [  # ('FC00069C', 'fcfid f0,f0') Unsupported ins
    #     {
    #         'setup': (
    #             ('f0', 0x428ad70a),
    #         ),
    #         'tests': (
    #             ('f0', 0x41d0a2b5c2800000),
    #         ),
    #     }
    # ],  # ('FC00069C', 'fcfid f0,f0')

    # '8004FFF0': [  # ('8004FFF0', 'lwz r0,-0x10(r4)') Loading stuff into mem is wonky
    #     {
    #         'setup': (
    #             (0x00000000000000ff, b'\x10'),
    #             ('r4', 0xff),
    #         ),
    #         'tests': (
    #             ('r0', 0xff - 0x10 +4),
    #         ),
    #     }
    # ],  # ('8004FFF0', 'lwz r0,-0x10(r4)')

}

GOOD_EMU_TESTS = 58
