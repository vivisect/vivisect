effects = {
    # instruction name -> [bytes, newva, contraints, effects]
    'rdtsc': ('0f31', None, (),
              ('rdx = TSC_HIGH',
               'rax = TSC_LOW')
              ),
    'cwde': ('98', None, (),
             ('rax = signextend((rax & 0x0000ffff), 8)',)
             ),
    'cdq': ('99', None, (),
            ('rax = signextend((rax & 0x0000ffff), 8)',
             'rdx = (signextend((rax & 0x0000ffff), 16) >> 64)')
            ),
    'div16': ('66f7f2', None, (),
              ('rax = (((((rdx & 0x0000ffff) << 16) | (rax & 0x0000ffff)) / (rdx & 0x0000ffff)) | (rax & 0xffffffffffff0000))',
               'rdx = (((((rdx & 0x0000ffff) << 16) | (rax & 0x0000ffff)) % (rdx & 0x0000ffff)) | (rdx & 0xffffffffffff0000))',)
              ),
    'div32': ('f7f1', None, (),
              ('rax = ((((rdx & 0xffffffff) << 32) | (rax & 0xffffffff)) / (rcx & 0xffffffff))',
               'rdx = ((((rdx & 0xffffffff) << 32) | (rax & 0xffffffff)) % (rcx & 0xffffffff))',)
              ),
    'div64': ('49f7f3', None, (),
              ('rax = (((rdx << 64) | rax) / r11)',
               'rdx = (((rdx << 64) | rax) % r11)')
              ),
    'ror': ('C1C90C', None, (),
            ('rcx = (((rcx & 0xffffffff) >> (12 % 32)) | ((rcx & 0xffffffff) << (32 - (12 % 32))))',)
            ),
    'rol': ('49d3c3', None, (),
            ('r11 = ((r11 << ((rcx & 255) % 64)) | (r11 >> (64 - ((rcx & 255) % 64))))',)
            ),
    # rcr ax, 1
    'rcr': ('66d1d8', None, (),
            ('rax = (((((eflags_cf << 16) | (rax & 0x0000ffff)) >> (1 % 16)) | (((eflags_cf << 16) | (rax & 0x0000ffff)) << (16 - (1 % 16)))) | (rax & 0xffffffffffff0000))',
             'eflags_cf = (((((eflags_cf << 16) | (rax & 0x0000ffff)) >> (1 % 16)) | (((eflags_cf << 16) | (rax & 0x0000ffff)) << (16 - (1 % 16)))) >> (16 - 1))')),

    'rcl': ('66d1d0', None, (),
            ('rax = (((((eflags_cf << 16) | (rax & 0x0000ffff)) << (1 % 16)) | (((eflags_cf << 16) | (rax & 0x0000ffff)) >> (16 - (1 % 16)))) | (rax & 0xffffffffffff0000))',
             'eflags_cf = (((((eflags_cf << 16) | (rax & 0x0000ffff)) << (1 % 16)) | (((eflags_cf << 16) | (rax & 0x0000ffff)) >> (16 - (1 % 16)))) >> (16 - 1))')),

    # mulx r12, rax, rcx
    'mulx': ('C462FBF6E1', None, (),
             ('r12 = ((rdx * rcx) & 0xffffffffffffffff)',
              'rax = ((rdx * rcx) >> 64)')
             ),
    # mul eax
    'mul': ('f7e0', None, (),
            ('rax = (((rax & 0xffffffff) * (rax & 0xffffffff)) & 0xffffffff)',
             'rdx = (((rax & 0xffffffff) * (rax & 0xffffffff)) >> 32)',
             'eflags_of = ((((rax & 0xffffffff) * (rax & 0xffffffff)) >> 32) != 0)',
             'eflags_cf = ((((rax & 0xffffffff) * (rax & 0xffffffff)) >> 32) != 0)')
            ),

    # idiv r11
    'idiv': ('49F7Fb', None, (),
             ('rax = (((rdx << 64) | rax) / r11)',
              'rdx = (((rdx << 64) | rax) % r11)',)
             ),

    # bt dword [0x41414141], ebx
    'bt': ('0FA31C2541414141', None, (),
           ('[ (0x41414141 - 0) : 4 ]',
            'eflags_cf = ((mem[(0x41414141 - 0):4] >> (rbx & 0xffffffff)) & 1)',)
           ),
    # bts rax, rbx
    'bts': ('480FABD8', None, (),
            ('eflags_cf = ((rax >> rbx) & 1)',
             'rax = (rax | (1 << rbx))')),

    # btc eax, ebx
    'btc': ('0FBBD8', None, (),
            ('rax = ((rax & 0xffffffff) ^ (1 << (rbx & 0xffffffff)))',
             'eflags_cf = (((rax & 0xffffffff) >> (rbx & 0xffffffff)) & 1)')
            ),
    'btr': ('0FBA34254141414111', None, (),
            ('[ (0x41414141 - 0) : 4 ]',  # the read effect
             '[ (0x41414141 - 0) : 4 ] = (mem[(0x41414141 - 0):4] & 0xfffdffff)',
             'eflags_cf = ((mem[(0x41414141 - 0):4] >> 17) & 1)')
            ),

    'btr_2': ('4C0FB3D8', None, (),
              ('rax = (rax & (0xffffffffffffffff ^ (1 << r11)))',
               'eflags_cf = ((rax >> r11) & 1)')
              ),

    # imul ecx
    'imul': ('f7e9', None, (),
             ('rax = (((rax & 0xffffffff) * (rcx & 0xffffffff)) & 0xffffffff)',
              'rdx = (((rax & 0xffffffff) * (rcx & 0xffffffff)) >> 32)',
              'eflags_of = (((rax & 0xffffffff) * (rcx & 0xffffffff)) == signextend((rcx & 0xffffffff), 8))',
              'eflags_cf = (((rax & 0xffffffff) * (rcx & 0xffffffff)) == signextend((rcx & 0xffffffff), 8))')),

    # imul rcx, r11, 0xabcd
    'imul 2': ('4969CBCDAB0000', None, (),
               ('rcx = (r11 * 0x0000abcd)',
                'eflags_cf = ((r11 * 0x0000abcd) == signextend(rcx, 16))',
                'eflags_of = ((r11 * 0x0000abcd) == signextend(rcx, 16))')
               ),

    # sub esp, 0x200
    'sub': ('81EC00020000', None, (),
            ('rsp = ((rsp & 0xffffffff) - 512)',
             'eflags_gt = ((rsp & 0xffffffff) > 512)',
             'eflags_lt = ((rsp & 0xffffffff) < 512)',
             'eflags_sf = ((rsp & 0xffffffff) < 512)',
             'eflags_eq = ((rsp & 0xffffffff) == 512)',
             'eflags_of = (((rsp & 0xffffffff) - 512) > 0x00007fff)',
             'SKIPeflags_pf = ')
            ),
    # add ax, 0xa3f4
    'add': ('6605F4A3', None, (),
            ('rax = (((rax & 0x0000ffff) + 0x0000a3f4) | (rax & 0xffffffffffff0000))',
             'eflags_gt = ((rax & 0x0000ffff) > 0x0000a3f4)',
             'eflags_lt = ((rax & 0x0000ffff) < 0x0000a3f4)',
             'eflags_sf = (((rax & 0x0000ffff) + 0x0000a3f4) < 0)',
             'eflags_eq = (((rax & 0x0000ffff) + 0x0000a3f4) == 0)',
             'eflags_of = (((rax & 0x0000ffff) + 0x0000a3f4) > 127)',
             'SKIPeflags_pf = ')  # TODO: Re-review the parity generator to make sure it's not a mess
            ),
    # div rcx
    'div': ('48F7F1', None, (),
            ('rax = (((rdx << 64) | rax) / rcx)',
             'rdx = (((rdx << 64) | rax) % rcx)')
            ),
    # not al
    'not': ('f6d0', None, (),
            ('rax = (((rax & 255) ^ 255) | (rax & 0xffffffffffffff00))',)),
    # not ax
    'not2': ('66f7d0', None, (),
             ('rax = (((rax & 0x0000ffff) ^ 0x0000ffff) | (rax & 0xffffffffffff0000))',)),
    # not eax
    'not3': ('f7d0', None, (),
             ('rax = ((rax & 0xffffffff) ^ 0xffffffff)',)),
    # not rax
    'not4': ('48f7d0', None, (),
             ('rax = (rax ^ 0xffffffffffffffff)',)),
}
