effects = {
    # instruction name -> [bytes, newva, contraints, effects]
    'rdtsc': ('0f31', None, (),
              ('edx = TSC_HIGH',
               'eax = TSC_LOW')),
    'div16': ('66f7f2', None, (),
              ('eax = (((((edx & 0x0000ffff) << 16) | (eax & 0x0000ffff)) / (edx & 0x0000ffff)) | (eax & 0xffff0000))',
               'edx = (((((edx & 0x0000ffff) << 16) | (eax & 0x0000ffff)) % (edx & 0x0000ffff)) | (edx & 0xffff0000))')
              ),
    'div32': ('f7f1', None, (),
              ('eax = (((edx << 32) | eax) / ecx)',
               'edx = (((edx << 32) | eax) % ecx)')
              ),
    'cwde': ('98', None, (),
             ('eax = signextend((eax & 0x0000ffff), 4)',)
             ),
    'cdq': ('99', None, (),
            ('eax = signextend((eax & 0x0000ffff), 4)',
             'edx = (signextend((eax & 0x0000ffff), 8) >> 32)')
            ),
    'ror': ('C1C90C', None, (),
            ('ecx = ((ecx >> (12 % 32)) | (ecx << (32 - (12 % 32))))',)
            ),
    # rol ebx,cl
    'rol': ('d3c3', None, (),
            ('ebx = ((ebx << ((ecx & 255) % 32)) | (ebx >> (32 - ((ecx & 255) % 32))))',)
            ),
}
