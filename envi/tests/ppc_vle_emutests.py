'''
Ways to access registers, flags or memory:
    'regname'       eg: 'f30'                   - get/set register by name
    'REG_CONSTANT'  eg: 'REG_R3' or 'REG_XER'   - get/set register by constant (good for 
                                                        specific, hard to reach flags)
    0xADDRESS       eg: 0xdeadb33f              - read/write memory at address
    '[expression]'  eg: '[r0 + 4]'              - read/write memory at expression
                    or '[0xdeadbeef + 243]'
    '[expr:20]'     eg: '[r0+4:20]'             - read/write 20 bytes of memory at expr
'''

GOOD_EMU_TESTS = 1
emutests = {
    #'e9f2': [{'setup': (('PC', 0x471450), ('LR', 0x313370)),
    #    'tests': (('PC', 0x471434), ('LR', 0x471452))}],   # se_bl -0x1c

    #'e8eb': [{'setup': (('PC', 0x471450), ('LR', 0x313370 )),
    #    'tests': (('PC', 0x471450), ('LR', 0x313370))}],   # se_b -0x2a

    '7CDF0214': [
        {
            'setup': (
                ('r31', 4),
                ('r0', 16),
                ('XER', 0),
            ),
            'tests': (
                ('r6', 20),
                ('r31', 4),
                ('r0', 16),
                ('cr0', 0),
            ),
        },
    ],   # add r6,r31,r0
}

