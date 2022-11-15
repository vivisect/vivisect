import vdb
import getpass


defconfig = {
    'viv':{

        'SymbolCacheSave':True,

        'parsers':{
            'pe':{
                'baseaddr': 0x200000,
                'loadresources':False,
                'carvepes':True,
                'nx':False,
            },
            'elf':{
                'baseaddr': 0x200000,
            },
            'blob':{
                'arch':'',
                'bigend':False,
                'baseaddr':0x20200000,
            },
            'macho':{
                'baseaddr':0x70700000,
                'fatarch':'',
            },
            'ihex':{
                'arch':'',
                'bigend':False,
                'offset':0,
            },
            'vbf':{
                'arch':'',
                'bigend':False,
            },
            'srec':{
                'arch':'',
                'bigend':False,
                'offset':0,
            },
        },

        'analysis':{
            'pointertables':{
                'table_min_len':4,
            },
            'symswitchcase':{
                'max_instr_count': 10,
                'max_cases': 500,
                'case_failure': 5000,
                'min_func_instr_size': 10,
                'timeout_secs': 45,
            },
            'stack':{
                'base': 0xBFB00000,
                'mask': 0xFFF00000,
                'top':  0xBFB08000,
                'pointer': None,
            },
            'taint':{
                'base': 0x4156000F,
                'byte': 'a',
                'offset': 0x1000,
                'mask': 0xffffe000,
            },
        },

        'arch':{
            'ppc':{
                'options':'spe',
                'bootstrap':{
                    'rchwaddrs':[
                        0x0000, 0x4000, 0x10000, 0x1C000, 0x20000, 0x30000,
                        0x800000
                    ],
                },
                'findvlepages':True,
                'mmu':[],
            },
        },

        'remote':{
            'wait_for_plat_arch': 10,
        },
    },
    'cli':vdb.defconfig.get('cli'), # FIXME make our own...
    'vdb':vdb.defconfig.get('vdb'),
    'user':{
        'name': getpass.getuser(),
    }
}

defconfig.get('cli').update(vdb.defconfig.get('cli'))

# Config elements docs
docconfig = {

    'viv':{

        'SymbolCacheSave':'Save vivisect names to the vdb configured symbol cache?',

        'parsers':{
            'pe':{
                'baseaddr': 'Address used to relocate PE files if base-address is 0 and PE is relocatable',
                'loadresources':'Should we load resource segments?',
                'carvepes':'Should we carve pes?',
                'nx':'Should we truly treat sections that dont execute as non executable?'
            },
            'elf':{
                'baseaddr': 'Address used to relocate ELF files if base-address is 0 and ELF is relocatable',
            },
            'blob':{
                'arch':'What architecture is the blob?',
                'baseaddr':'Base virtual address for loading the blob.',
            },
            'macho':{
                'baseaddr':'Base virtual address for loading the macho',
                'fatarch':'Which architecture binary to extract from a FAT macho',
            },
            'ihex':{
                'arch':'What architecture is the ihex dump?',
                'bigend':'Is the architecture Big-Endian (MSB)?',
            },
            'srec':{
                'arch':'What architecture is the srec dump?',
                'offset':'Skip over initial bytes in the file',
            },
        },

        'analysis':{
            'pointertables':{
                'table_min_len':'How many pointers must be in a row to make a table?',
            },
            'stack':{
                'base':'Stack base address',
                'mask':'Stack mask',
                'top':'Stack top address',
                'pointer':'Stack pointer',
            },
            'taint':{
                'base':'Taint base address',
                'byte':'Taint byte value',
                'offset':'Taint VA offset',
                'mask':'Taint mask',
            },
        },

        'arch':{
            'ppc':{
                'options':'PowerPC processor features to enable',
                'bootstrap':{
                    'rchwaddrs':'A list of addresses to look for at for the reset-control half word (RCHW) used for PowerPC boot target identification',
                },
                'findvlepages':'Flag to search and automatically add VLE memory map pages from MMU instructions',
                'mmu':'A list of [<address>, <size>] values that indicate memory segments where PowerPC VLE instructions can be found',
            },
        },

        'remote':{
            'wait_for_plat_arch':'How many secs to wait for the remote server/workspace to provide a Platform or Architecture before moving on.',
        }
    },

    'vdb':vdb.docconfig.get('vdb'),
    'user':{
        'name': 'Username.  When not set, defaults to current system user.',
    }
}
