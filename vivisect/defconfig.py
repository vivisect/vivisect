import vdb
import cobra
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
                'offset':0,
            },
            'srec':{
                'arch':'',
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
            }
        },
        'remote':{
            'wait_for_plat_arch': 10,
            'timeout_wait': 10,
            'timeout_aban': 120,
        },
        'server':{
            'queue_chunksize': 70000,
        },
    },
    'cli':vdb.defconfig.get('cli'), # FIXME make our own...
    'vdb':vdb.defconfig.get('vdb'),
    'cobra':cobra.defconfig.get('cobra'),
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
        },
        'remote':{
            'wait_for_plat_arch':'How many secs to wait for the remote server/workspace to provide a Platform or Architecture before moving on.',
            'timeout_wait': "Timeout waiting for getNextEvent() to have more Viv events to send.",
            'timeout_aban': "Server channel timeout.  At this point, clean up and delete the channel.  The connection is dead.",
        },

        'server':{
            'queue_chunksize':"VivServer Queue Chunk Size, the largest chunk of events the server will send at a time.  This affects queue time and overall efficiency of serving large workspaces",
        },
    },

    'vdb':vdb.docconfig.get('vdb'),
    'user':{
        'name': 'Username.  When not set, defaults to current system user.',
    }
}
