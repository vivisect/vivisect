import unittest
import vivisect
import envi.memory as e_mem

import logging
import envi.common as e_common
logger = logging.getLogger(__name__)
#e_common.initLogging(logger, logging.DEBUG)

MS_MAPS = [
    (0x880000, 1, e_mem.MM_READ, b'\x00'),
    (0x884ec0, 32, e_mem.MM_RWX, b'\xb7D$*f\x89C\x0c\x0f\xb7D$,f\x89C\x0eH\x83\xc40[\xc3\x90\x90\x90\x90\x90\x90\x90\x90\x90'),
    (0x884ee0, 112, e_mem.MM_RWX, b'H\x83\xecHH\x85\xc9\x0f\x84{\xbe\x01\x00\x83\xf9\xf4\x0f\x83\xb97\x01\x00H\x85\xc9\x0f\x84i\xbe\x01\x00L\x8dD$PH\x8dT$0A\xb9\x08\x00\x00\x00\xc7D$ \x04\x00\x00\x00\xff\x15\xcbS\x04\x00\x85\xc0\x0f\x88\xa77\x01\x00H\x8bD$P\x83\xf8\x07\x0f\x85\xff\xc2\x00\x00\xb8\x01\x00\x00\x00H\x83\xc4H\xc3\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90'),
    (0x891232, 68, e_mem.MM_RWX, b'\x8dH\xfe\x83\xf9)\x0f\x87\x89\xfb\x00\x00H\x8d\x15\xbb\xed\xfe\xff\x0f\xb6\x84\n@\xc5\x01\x00\x8b\x8c\x820\xc5\x01\x00H\x03\xca\xff\xe1\xb8\x03\x00\x00\x00H\x83\xc4H\xc3\x8b\xc1%\x00\x00\x00\xc0=\x00\x00\x00\x80\x0f\x84\xe8\xfa\x00\x00\xe8'),
    (0x8986af, 62, e_mem.MM_RWX, b'\x0f\x84\xf8\x86\x00\x00\x83\xf9\xf5\x0f\x84\xd5\x86\x00\x00\x83\xf9\xf6\x0f\x85/\xc8\xfe\xff\xe9\xad\x86\x00\x00\x8b\xc8\xe8=\x90\xfe\xff3\xc0H\x83\xc4H\xc3H\x8d\r?\x90\x04\x00\xff\x15\x81\x1b\x03\x00\xe84\x04\xff\xffH'),
    (0x899db9, 29, e_mem.MM_RWX, b'\xb8\x02\x00\x00\x00H\x83\xc4H\xc3\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90H\x83\xec(D\x0f'),

    (0x89c540, 41, e_mem.MM_RWX, b'\x00\x00\x00\x00\x00\x00\x00\x03\x03\x01\x03\x03\x03\x01\x03\x02\x03\x03\x03\x01\x01\x03\x01\x03\x03\x01\x01\x01\x03\x03\x03\x03\x03\x03\x00\x03\x03\x03\x03\x03\x03'),
    (0x89c634, 24, e_mem.MM_RWX, b'\x89\xf2\x00\x00\x89\xf2\x00\x00\x89\xf2\x00\x00\x89\xf2\x00\x00W\x98\x00\x00\x0f\xf9\x00\x00'),
    (0x8a0d68, 129, e_mem.MM_RWX, b'\xb9\x08\x00\x00\xc0\xe8\x9e\t\xfe\xff3\xc0H\x83\xc4H\xc3eH\x8b\x04%0\x00\x00\x00H\x8bH`H\x8bA H\x8bH \xe9cA\xfe\xffeH\x8b\x04%0\x00\x00\x00H\x8bH`H\x8bA H\x8bH(\xe9IA\xfe\xffeH\x8b\x04%0\x00\x00\x00H\x8bH`H\x8bA H\x8bH0\xe9/A\xfe\xff3\xc9\xff\x15\xd1\x92\x02\x003\xc0H\x83\xc4H\xc3eH\x8b\x04%0\x00\x00\x00L\x8b\xc73\xd2H\x8bH`H'),
    (0x8ca0a0, 28, e_mem.MM_RWX, b'@ \xeax\x00\x00\x00\x00@\xff\xe9x\x00\x00\x00\x00p\x1e\xeax\x00\x00\x00\x00p\x12\xeax'),
    (0x8ca2e8, 28, e_mem.MM_RWX, b'@\x03\xeax\x00\x00\x00\x00\x10\xff\xe9x\x00\x00\x00\x000\xff\xe9x\x00\x00\x00\x00`\x03\xeax'),

    (0x89c530, 64, e_mem.MM_READ, b'3O\x00\x00\xb9\x9d\x01\x00Y\x12\x01\x00\xc7\r\x02\x00\x00\x00\x00\x00\x00\x00\x00\x03\x03\x01\x03\x03\x03\x01\x03\x02\x03\x03\x03\x01\x01\x03\x01\x03\x03\x01\x01\x01\x03\x03\x03\x03\x03\x03\x00\x03\x03\x03\x03\x03\x03\x01\x90\x90\x9cz\x01\x00'), # table
]

# 32bit libc-2.13.so.  switch jmp at 0x0205af11
LIBC_MAPS = [\
    (0x205ab40, 0x107, e_mem.MM_RWX, b'U\x89\xe5WVS\x83\xec\x14\x8bM\x08\xe8\x1e\xc1\xfb\xff\x81\xc3\xa3\xe4\x0f\x00\x8bu\x0c\x85\xc9\x0f\x84\x9c\x00\x00\x00\x8b\x93\xf8\xfe\xff\xff\x85\xd2tt\x8bE\x08\x8b@h\x85\xc0~j\x89e\xf0\x894$\xe8\xff\x8c\x01\x00\x8dx\x01\x8d\x04\xbd\x10\x00\x00\x00)\xc4\x8dD$\x1f\x83\xe0\xf0\x85\xfft%\x0f\xb6\x0e\x84\xc9xo1\xd2\xeb\r\x90\x8dt&\x00\x0f\xb6\x0c\x16\x84\xc9x^\x0f\xbe\xc9\x89\x0c\x90\x83\xc2\x019\xd7w\xeb\x8dU\x10\x89T$\x08\x89D$\x04\x8bE\x08\x89\x04$\xe8mN\xff\xff\x8be\xf0\x8de\xf4[^_]\xc3f\x90\x8dU\x10\x89t$\x04\x89T$\x08\x8bE\x08\x89\x04$\xe8\x1a#\xfe\xff\x8de\xf4[^_]\xc3\x8b\x83H\xff\xff\xff\x8b\x00\x89E\x08\xe9T\xff\xff\xff\x8d\x836\xa1\xfd\xff\x89D$\x0c\x8d\x83\x11\xa1\xfd\xff\x89D$\x04\x8d\x83\x1c\xa1\xfd\xff\xc7D$\x08/\x00\x00\x00\x89\x04$\xe8\x98\x8a\xfc\xff\x90\x90\x90\x90\x90\x90\x90\x90U\x89\xe5WVS\x83'),
    ]



WALKER_MAPS = maps = [\
    (0x201a5a0, 0x9b, e_mem.MM_RWX, b'UH\x89\xe5H\x83\xec0@\x88\xf0H\x89}\xf8\x88E\xf7H\x89U\xe8H\x8bU\xf8H\x89\xd7H\x83\xc7`H\x8bu\xe8H\x89U\xe0\xe8R\x1a\x00\x00\xa8\x01\x0f\x85\x05\x00\x00\x00\xe9\x05\x00\x00\x00\xe9V\x01\x00\x00H\x8bE\xe0H\x8bH8H\x83\xc18H\x8bu\xe8H\x89\xcf\xe8\x98\x1a\x00\x00H\x89\xc7\xe8\xb0\x1a\x00\x00\x83\xc0\xff\x89\xc1\x83\xe8\x0bH\x89M\xd8\x89E\xd4\x0f\x87\x1c\x01\x00\x00H\x8d\x05\xec\xc6\x05\x00H\x8bM\xd8Hc\x14\x88H\x01\xc2\xff\xe2\x8aE\xf7H\x8bU\xe8H\x8b}\xe0\x0f\xb6\xf0\xe8\x84\x1a\x00'),
    (0x201a731, 0x1e, e_mem.MM_RWX, b'\xe9\x00\x00\x00\x00H\x83\xc40]\xc3\x0f\x1f@\x00UH\x89\xe5H\x89}\xf8H\x8b}\xf8H\x8b\x07'),
    (0x2076d08, 0x30, e_mem.MM_READ, b'\x11:\xfa\xff!9\xfa\xff\xe19\xfa\xffi9\xfa\xff\x819\xfa\xff\x999\xfa\xff\xb19\xfa\xff99\xfa\xffQ9\xfa\xff):\xfa\xff\xc99\xfa\xff\xf99\xfa\xff'),
]

def applyMaps(vw, maps=MS_MAPS, mapbase=0x400000, bufferpages=2):
    bufferpgsz = bufferpages * 4096
    vw.addMemoryMap(mapbase - bufferpgsz, e_mem.MM_RWX, 'testswitches', '@' * bufferpgsz)

    mapdelta = mapbase - maps[0][0]
    

    vw.addFile('testswitches', mapbase, "@@@@@@@@")
    for mapva, sz, perms, mem in maps:
        mapva += mapdelta
        vw.addMemoryMap(mapva, perms, 'testswitches', mem)
        vw.addSegment(mapva, len(mem), 'switch_code_%x' % mapva, 'testswitches')


def genMsSwitchWorkspace(maps=MS_MAPS, mapbase=0x400000, bufferpages=2, arch='amd64'):
    vw = vivisect.VivWorkspace()
    vw.setMeta('Architecture', arch)
    vw.setMeta('Platform', 'windows')
    vw.setMeta('Format', 'pe')
    vw._snapInAnalysisModules()

    applyMaps(vw, maps, mapbase, bufferpages)
    return vw

def genLinuxSwitchWorkspace(maps=LIBC_MAPS, mapbase=0x400000, bufferpages=2):
    vw = vivisect.VivWorkspace()
    vw.setMeta('Architecture', 'i386')
    vw.setMeta('Platform', 'linux')
    vw.setMeta('Format', 'elf')
    vw._snapInAnalysisModules()

    applyMaps(vw, maps, mapbase, bufferpages)
    return vw

cbs_ms_0 = [  
        (4194304, 13, 4194304),
        (4194317, 9, 4194304),
        (4194326, 9, 4194304),
        (4194335, 38, 4194304),
        (4194373, 14, 4194304),
        (4194387, 10, 4194304),
        (4244306, 12, 4194304),
        (4244318, 27, 4194304),
        (4274127, 6, 4194304),
        (4274133, 9, 4194304),
        (4274142, 9, 4194304),
        (4274151, 5, 4194304),
        (4274156, 14, 4194304),
        (4308616, 17, 4194304),
        (4308633, 26, 4194304),
        (4308659, 26, 4194304),
        (4308685, 26, 4194304),
        (4308711, 15, 4194304)]

cbs_ms_0 = [
        (0x404ee0, 0xd , 0x404ee0),
        (0x404eed, 0x9 , 0x404ee0),
        (0x404ef6, 0x9 , 0x404ee0),
        (0x404eff, 0x26, 0x404ee0),
        (0x404f25, 0xe , 0x404ee0),
        (0x404f33, 0xa , 0x404ee0),
        (0x411232, 0xc , 0x404ee0),
        (0x41123e, 0x1b, 0x404ee0),
        (0x411259, 0xa , 0x404ee0),
        (0x4186af, 0x6 , 0x404ee0),
        (0x4186b5, 0x9 , 0x404ee0),
        (0x4186be, 0x9 , 0x404ee0),
        (0x4186c7, 0x5 , 0x404ee0),
        (0x4186cc, 0xe , 0x404ee0),
        (0x419db9, 0xa , 0x404ee0),
        (0x420d68, 0x11, 0x404ee0),
        (0x420d79, 0x1a, 0x404ee0),
        (0x420d93, 0x1a, 0x404ee0),
        (0x420dad, 0x1a, 0x404ee0),
        (0x420dc7, 0xf , 0x404ee0)]

cbs_libc_0 = [
        (5242880, 34, 5242880),
        (5242914, 10, 5242880),
        (5242924, 10, 5242880),
        (5242934, 34, 5242880),
        (5242968, 7, 5242880),
        (5242975, 4, 5242880),
        (5242984, 8, 5242880),
        (5242992, 13, 5242880),
        (5243005, 33, 5242880),
        (5243040, 30, 5242880),
        (5243070, 16, 5242880),
        (5243086, 56, 5242880)]

cbs_walker_0 = [
        (5242880, 54, 5242880),
        (5242934, 5, 5242880),
        (5242939, 5, 5242880),
        (5242944, 53, 5242880),
        (5242997, 20, 5242880),
        (5243281, 5, 5242880),
        (5243286, 6, 5242880),
        (5243017, 24, 5242880),
        (5243041, 24, 5242880),
        (5243065, 24, 5242880),
        (5243089, 24, 5242880),
        (5243113, 24, 5242880),
        (5243137, 24, 5242880),
        (5243161, 24, 5242880),
        (5243185, 24, 5242880),
        (5243209, 24, 5242880),
        (5243233, 24, 5242880),
        (5243257, 24, 5242880),

]

cbs_amd64_ls_0 = [
        (0x402755, 5, 0x404223),
        (0x40309f, 20, 0x404223),
        (0x4030b3, 13, 0x404223),
        (0x4030c0, 13, 0x404223),
        (0x4030cd, 11, 0x404223),
        (0x4030d8, 9, 0x404223),
        (0x4030e1, 7, 0x404223),
        (0x4030e8, 2, 0x404223),
        (0x4030ea, 19, 0x404223),
        (0x4030fd, 59, 0x404223),
        (0x403138, 7, 0x404223),
        (0x40313f, 33, 0x404223),
        (0x403160, 14, 0x404223),
        (0x40316e, 22, 0x404223),
        (0x403184, 12, 0x404223),
        (0x403190, 26, 0x404223),
        (0x4031aa, 10, 0x404223),
        (0x4031b4, 59, 0x404223),
        (0x4031ef, 14, 0x404223),
        (0x4031fd, 24, 0x404223),
        (0x403215, 15, 0x404223),
        (0x403224, 8, 0x404223),
        (0x40322c, 70, 0x404223),
        (0x403272, 9, 0x404223),
        (0x40327b, 27, 0x404223),
        (0x403296, 34, 0x404223),
        (0x4032b8, 9, 0x404223),
        (0x4032c1, 13, 0x404223),
        (0x4032ce, 9, 0x404223),
        (0x4032d7, 21, 0x404223),
        (0x4032ec, 11, 0x404223),
        (0x4032f7, 8, 0x404223),
        (0x4032ff, 20, 0x404223),
        (0x403313, 47, 0x404223),
        (0x403342, 24, 0x404223),
        (0x40335a, 18, 0x404223),
        (0x40336c, 35, 0x404223),
        (0x40338f, 17, 0x404223),
        (0x4033a0, 30, 0x404223),
        (0x4033be, 18, 0x404223),
        (0x4033d0, 15, 0x404223),
        (0x4033df, 4, 0x404223),
        (0x4033e3, 12, 0x404223),
        (0x4033ef, 1, 0x404223),
        (0x4033f0, 20, 0x404223),
        (0x403404, 9, 0x404223),
        (0x40340d, 12, 0x404223),
        (0x403419, 7, 0x404223),
        (0x403420, 24, 0x404223),
        (0x403438, 9, 0x404223),
        (0x403441, 18, 0x404223),
        (0x403453, 10, 0x404223),
        (0x40345d, 29, 0x404223),
        (0x40347a, 13, 0x404223),
        (0x403487, 13, 0x404223),
        (0x403494, 13, 0x404223),
        (0x4034a1, 25, 0x404223),
        (0x403526, 8, 0x404223),
        (0x403530, 18, 0x404223),
        (0x403542, 4, 0x404223),
        (0x403546, 13, 0x404223),
        (0x403553, 11, 0x404223),
        (0x40355e, 52, 0x404223),
        (0x403592, 6, 0x404223),
        (0x403598, 22, 0x404223),
        (0x4035ae, 26, 0x404223),
        (0x4035c8, 5, 0x404223),
        (0x403624, 44, 0x404223),
        (0x403650, 30, 0x404223),
        (0x40366e, 23, 0x404223),
        (0x403685, 9, 0x404223),
        (0x40368e, 13, 0x404223),
        (0x40369b, 18, 0x404223),
        (0x4036ad, 14, 0x404223),
        (0x4036bb, 13, 0x404223),
        (0x4036c8, 14, 0x404223),
        (0x4036d6, 13, 0x404223),
        (0x4036e3, 18, 0x404223),
        (0x4036f5, 13, 0x404223),
        (0x403702, 30, 0x404223),
        (0x403720, 13, 0x404223),
        (0x40372d, 10, 0x404223),
        (0x403737, 37, 0x404223),
        (0x40375c, 24, 0x404223),
        (0x403774, 33, 0x404223),
        (0x403795, 10, 0x404223),
        (0x40379f, 5, 0x404223),
        (0x4037fa, 14, 0x404223),
        (0x403808, 9, 0x404223),
        (0x403811, 15, 0x404223),
        (0x403820, 11, 0x404223),
        (0x403830, 9, 0x404223),
        (0x403839, 43, 0x404223),
        (0x403864, 16, 0x404223),
        (0x403874, 18, 0x404223),
        (0x403886, 12, 0x404223),
        (0x403892, 13, 0x404223),
        (0x40389f, 13, 0x404223),
        (0x4038ac, 71, 0x404223),
        (0x4038f3, 11, 0x404223),
        (0x4038fe, 96, 0x404223),
        (0x40395e, 11, 0x404223),
        (0x403969, 8, 0x404223),
        (0x403971, 10, 0x404223),
        (0x40397b, 5, 0x404223),
        (0x403980, 68, 0x404223),
        (0x4039c4, 13, 0x404223),
        (0x4039d1, 9, 0x404223),
        (0x4039da, 14, 0x404223),
        (0x4039e8, 5, 0x404223),
        (0x4039ed, 16, 0x404223),
        (0x4039fd, 14, 0x404223),
        (0x403a0b, 22, 0x404223),
        (0x403a21, 11, 0x404223),
        (0x403a30, 8, 0x404223),
        (0x403a38, 10, 0x404223),
        (0x403a42, 8, 0x404223),
        (0x403a4a, 5, 0x404223),
        (0x403a4f, 6, 0x404223),
        (0x403a55, 45, 0x404223),
        (0x403a82, 17, 0x404223),
        (0x403a93, 37, 0x404223),
        (0x403ab8, 21, 0x404223),
        (0x403acd, 26, 0x404223),
        (0x403ae7, 20, 0x404223),
        (0x403afb, 64, 0x404223),
        (0x403b3b, 62, 0x404223),
        (0x403b79, 40, 0x404223),
        (0x403ba1, 48, 0x404223),
        (0x403bd1, 20, 0x404223),
        (0x403be5, 23, 0x404223),
        (0x403bfc, 76, 0x404223),
        (0x403c48, 27, 0x404223),
        (0x403c63, 27, 0x404223),
        (0x403c7e, 27, 0x404223),
        (0x403c99, 27, 0x404223),
        (0x403d18, 37, 0x404223),
        (0x403d3d, 13, 0x404223),
        (0x403d4a, 13, 0x404223),
        (0x403d57, 13, 0x404223),
        (0x403d64, 25, 0x404223),
        (0x403d7d, 13, 0x404223),
        (0x403d8a, 13, 0x404223),
        (0x403d97, 13, 0x404223),
        (0x403da4, 5, 0x404223),
        (0x403da9, 8, 0x404223),
        (0x403db1, 13, 0x404223),
        (0x403dbe, 4, 0x404223),
        (0x403dc2, 10, 0x404223),
        (0x403dcc, 5, 0x404223),
        (0x403dd1, 9, 0x404223),
        (0x403dda, 69, 0x404223),
        (0x403e1f, 12, 0x404223),
        (0x403e2b, 10, 0x404223),
        (0x403e35, 25, 0x404223),
        (0x403e4e, 12, 0x404223),
        (0x403e5a, 25, 0x404223),
        (0x403e73, 12, 0x404223),
        (0x403e7f, 11, 0x404223),
        (0x403e8a, 9, 0x404223),
        (0x403e93, 9, 0x404223),
        (0x403e9c, 26, 0x404223),
        (0x403eb6, 19, 0x404223),
        (0x403ec9, 30, 0x404223),
        (0x403ee7, 49, 0x404223),
        (0x403f18, 50, 0x404223),
        (0x403f4a, 9, 0x404223),
        (0x403f53, 9, 0x404223),
        (0x403f5c, 6, 0x404223),
        (0x403f62, 11, 0x404223),
        (0x403f6d, 36, 0x404223),
        (0x403f91, 28, 0x404223),
        (0x403fad, 22, 0x404223),
        (0x403fc3, 48, 0x404223),
        (0x403ff3, 4, 0x404223),
        (0x403ff7, 19, 0x404223),
        (0x40400a, 55, 0x404223),
        (0x404041, 49, 0x404223),
        (0x404072, 12, 0x404223),
        (0x40407e, 7, 0x404223),
        (0x4040b8, 13, 0x404223),
        (0x4040c5, 30, 0x404223),
        (0x4040e3, 9, 0x404223),
        (0x4040ec, 11, 0x404223),
        (0x4040f7, 12, 0x404223),
        (0x404103, 18, 0x404223),
        (0x404115, 14, 0x404223),
        (0x404123, 26, 0x404223),
        (0x40413d, 21, 0x404223),
        (0x404152, 11, 0x404223),
        (0x40415d, 25, 0x404223),
        (0x404176, 22, 0x404223),
        (0x4041b5, 15, 0x404223),
        (0x4041c4, 5, 0x404223),
        (0x4041c9, 30, 0x404223),
        (0x404203, 15, 0x404223),
        (0x404212, 17, 0x404223),
        (0x404223, 50, 0x404223),
        (0x404255, 5, 0x404223),
        (0x40425a, 14, 0x404223),
        (0x4042c3, 7, 0x404223),
        (0x4042ca, 14, 0x404223),
        (0x4042d8, 30, 0x404223),
        (0x4042f6, 12, 0x404223),
        (0x4044ab, 18, 0x404223),
        (0x4044bd, 57, 0x404223),
        (0x4044f6, 27, 0x404223),
        (0x404511, 30, 0x404223),
        (0x40452f, 14, 0x404223),
        (0x40453d, 16, 0x404223),
        (0x40454d, 5, 0x404223),
        (0x404552, 25, 0x404223),
        (0x40456b, 15, 0x404223),
        (0x40457a, 15, 0x404223),
        (0x404589, 27, 0x404223),
]

cbs_amd64_ls_1 = [
        (0x402690, 187, 0x402690),
        (0x40274b, 5, 0x402690),
        (0x402750, 5, 0x402690),
        (0x402755, 5, 0x402690),
        (0x40275a, 18, 0x402690),
        (0x40276c, 19, 0x402690),
        (0x40277f, 22, 0x402690),
        (0x402795, 139, 0x402690),
        (0x402820, 31, 0x402690),
        (0x40283f, 16, 0x402690),
        (0x40284f, 40, 0x402690),
        (0x402877, 14, 0x402690),
        (0x402885, 29, 0x402690),
        (0x4028a2, 9, 0x402690),
        (0x4028ab, 30, 0x402690),
        (0x4028c9, 13, 0x402690),
        (0x4028d6, 10, 0x402690),
        (0x4028e0, 29, 0x402690),
        (0x4028fd, 34, 0x402690),
        (0x40291f, 15, 0x402690),
        (0x402968, 12, 0x402690),
        (0x402974, 12, 0x402690),
        (0x402980, 7, 0x402690),
        (0x402fb0, 27, 0x402690),
        (0x402fcb, 22, 0x402690),
        (0x402fe1, 38, 0x402690),
        (0x403007, 11, 0x402690),
        (0x403012, 19, 0x402690),
        (0x403025, 34, 0x402690),
        (0x403047, 41, 0x402690),
        (0x403070, 9, 0x402690),
        (0x403079, 7, 0x402690),
        (0x403080, 18, 0x402690),
        (0x403092, 13, 0x402690),
        (0x40309f, 20, 0x402690),
        (0x4030b3, 13, 0x402690),
        (0x4030c0, 13, 0x402690),
        (0x4030cd, 11, 0x402690),
        (0x4030d8, 9, 0x402690),
        (0x4030e1, 7, 0x402690),
        (0x4030e8, 2, 0x402690),
        (0x4030ea, 19, 0x402690),
        (0x4030fd, 59, 0x402690),
        (0x403138, 7, 0x402690),
        (0x40313f, 33, 0x402690),
        (0x403160, 14, 0x402690),
        (0x40316e, 22, 0x402690),
        (0x403184, 12, 0x402690),
        (0x403190, 26, 0x402690),
        (0x4031aa, 10, 0x402690),
        (0x4031b4, 59, 0x402690),
        (0x4031ef, 14, 0x402690),
        (0x4031fd, 24, 0x402690),
        (0x403215, 15, 0x402690),
        (0x403224, 8, 0x402690),
        (0x40322c, 70, 0x402690),
        (0x403272, 9, 0x402690),
        (0x40327b, 27, 0x402690),
        (0x403296, 34, 0x402690),
        (0x4032b8, 9, 0x402690),
        (0x4032c1, 13, 0x402690),
        (0x4032ce, 9, 0x402690),
        (0x4032d7, 21, 0x402690),
        (0x4032ec, 11, 0x402690),
        (0x4032f7, 8, 0x402690),
        (0x4032ff, 20, 0x402690),
        (0x403313, 47, 0x402690),
        (0x403342, 24, 0x402690),
        (0x40335a, 18, 0x402690),
        (0x40336c, 35, 0x402690),
        (0x40338f, 17, 0x402690),
        (0x4033a0, 30, 0x402690),
        (0x4033be, 18, 0x402690),
        (0x4033d0, 15, 0x402690),
        (0x4033df, 4, 0x402690),
        (0x4033e3, 12, 0x402690),
        (0x4033ef, 1, 0x402690),
        (0x4033f0, 20, 0x402690),
        (0x403404, 9, 0x402690),
        (0x40340d, 12, 0x402690),
        (0x403419, 7, 0x402690),
        (0x403420, 24, 0x402690),
        (0x403438, 9, 0x402690),
        (0x403441, 18, 0x402690),
        (0x403453, 10, 0x402690),
        (0x40345d, 29, 0x402690),
        (0x40347a, 13, 0x402690),
        (0x403487, 13, 0x402690),
        (0x403494, 13, 0x402690),
        (0x4034a1, 25, 0x402690),
        (0x4034ba, 34, 0x402690),
        (0x4034dc, 17, 0x402690),
        (0x4034ed, 12, 0x402690),
        (0x4034f9, 15, 0x402690),
        (0x403508, 15, 0x402690),
        (0x403517, 15, 0x402690),
        (0x403526, 8, 0x402690),
        (0x403530, 18, 0x402690),
        (0x403542, 4, 0x402690),
        (0x403546, 13, 0x402690),
        (0x403553, 11, 0x402690),
        (0x40355e, 52, 0x402690),
        (0x403592, 6, 0x402690),
        (0x403598, 22, 0x402690),
        (0x4035ae, 26, 0x402690),
        (0x4035c8, 5, 0x402690),
        (0x4035cd, 9, 0x402690),
        (0x4035d6, 13, 0x402690),
        (0x4035e3, 15, 0x402690),
        (0x4035f2, 50, 0x402690),
        (0x403624, 44, 0x402690),
        (0x403650, 30, 0x402690),
        (0x40366e, 23, 0x402690),
        (0x403685, 9, 0x402690),
        (0x40368e, 13, 0x402690),
        (0x40369b, 18, 0x402690),
        (0x4036ad, 14, 0x402690),
        (0x4036bb, 13, 0x402690),
        (0x4036c8, 14, 0x402690),
        (0x4036d6, 13, 0x402690),
        (0x4036e3, 18, 0x402690),
        (0x4036f5, 13, 0x402690),
        (0x403702, 30, 0x402690),
        (0x403720, 13, 0x402690),
        (0x40372d, 10, 0x402690),
        (0x403737, 37, 0x402690),
        (0x40375c, 24, 0x402690),
        (0x403774, 33, 0x402690),
        (0x403795, 10, 0x402690),
        (0x40379f, 5, 0x402690),
        (0x4037fa, 14, 0x402690),
        (0x403808, 9, 0x402690),
        (0x403811, 15, 0x402690),
        (0x403820, 11, 0x402690),
        (0x403830, 9, 0x402690),
        (0x403839, 43, 0x402690),
        (0x403864, 16, 0x402690),
        (0x403874, 18, 0x402690),
        (0x403886, 12, 0x402690),
        (0x403892, 13, 0x402690),
        (0x40389f, 13, 0x402690),
        (0x4038ac, 71, 0x402690),
        (0x4038f3, 11, 0x402690),
        (0x4038fe, 96, 0x402690),
        (0x40395e, 11, 0x402690),
        (0x403969, 8, 0x402690),
        (0x403971, 10, 0x402690),
        (0x40397b, 5, 0x402690),
        (0x403980, 68, 0x402690),
        (0x4039c4, 13, 0x402690),
        (0x4039d1, 9, 0x402690),
        (0x4039da, 14, 0x402690),
        (0x4039e8, 5, 0x402690),
        (0x4039ed, 16, 0x402690),
        (0x4039fd, 14, 0x402690),
        (0x403a0b, 22, 0x402690),
        (0x403a21, 11, 0x402690),
        (0x403a30, 8, 0x402690),
        (0x403a38, 10, 0x402690),
        (0x403a42, 8, 0x402690),
        (0x403a4a, 5, 0x402690),
        (0x403a4f, 6, 0x402690),
        (0x403a55, 45, 0x402690),
        (0x403a82, 17, 0x402690),
        (0x403a93, 37, 0x402690),
        (0x403ab8, 21, 0x402690),
        (0x403acd, 26, 0x402690),
        (0x403ae7, 20, 0x402690),
        (0x403afb, 64, 0x402690),
        (0x403b3b, 62, 0x402690),
        (0x403b79, 40, 0x402690),
        (0x403ba1, 48, 0x402690),
        (0x403bd1, 20, 0x402690),
        (0x403be5, 23, 0x402690),
        (0x403bfc, 76, 0x402690),
        (0x403c48, 27, 0x402690),
        (0x403c63, 27, 0x402690),
        (0x403c7e, 27, 0x402690),
        (0x403c99, 27, 0x402690),
        (0x403cb4, 50, 0x402690),
        (0x403ce6, 50, 0x402690),
        (0x403d18, 37, 0x402690),
        (0x403d3d, 13, 0x402690),
        (0x403d4a, 13, 0x402690),
        (0x403d57, 13, 0x402690),
        (0x403d64, 25, 0x402690),
        (0x403d7d, 13, 0x402690),
        (0x403d8a, 13, 0x402690),
        (0x403d97, 13, 0x402690),
        (0x403da4, 5, 0x402690),
        (0x403da9, 8, 0x402690),
        (0x403db1, 13, 0x402690),
        (0x403dbe, 4, 0x402690),
        (0x403dc2, 10, 0x402690),
        (0x403dcc, 5, 0x402690),
        (0x403dd1, 9, 0x402690),
        (0x403dda, 69, 0x402690),
        (0x403e1f, 12, 0x402690),
        (0x403e2b, 10, 0x402690),
        (0x403e35, 25, 0x402690),
        (0x403e4e, 12, 0x402690),
        (0x403e5a, 25, 0x402690),
        (0x403e73, 12, 0x402690),
        (0x403e7f, 11, 0x402690),
        (0x403e8a, 9, 0x402690),
        (0x403e93, 9, 0x402690),
        (0x403e9c, 26, 0x402690),
        (0x403eb6, 19, 0x402690),
        (0x403ec9, 30, 0x402690),
        (0x403ee7, 49, 0x402690),
        (0x403f18, 50, 0x402690),
        (0x403f4a, 9, 0x402690),
        (0x403f53, 9, 0x402690),
        (0x403f5c, 6, 0x402690),
        (0x403f62, 11, 0x402690),
        (0x403f6d, 36, 0x402690),
        (0x403f91, 28, 0x402690),
        (0x403fad, 22, 0x402690),
        (0x403fc3, 48, 0x402690),
        (0x403ff3, 4, 0x402690),
        (0x403ff7, 19, 0x402690),
        (0x40400a, 55, 0x402690),
        (0x404041, 61, 0x402690),
        (0x40407e, 7, 0x402690),
        (0x404085, 27, 0x402690),
        (0x4040a0, 19, 0x402690),
        (0x4040b3, 5, 0x402690),
        (0x4040b8, 13, 0x402690),
        (0x4040c5, 30, 0x402690),
        (0x4040e3, 9, 0x402690),
        (0x4040ec, 11, 0x402690),
        (0x4040f7, 12, 0x402690),
        (0x404103, 18, 0x402690),
        (0x404115, 14, 0x402690),
        (0x404123, 26, 0x402690),
        (0x40413d, 21, 0x402690),
        (0x404152, 11, 0x402690),
        (0x40415d, 25, 0x402690),
        (0x404176, 22, 0x402690),
        (0x4041b5, 15, 0x402690),
        (0x4041c4, 5, 0x402690),
        (0x4041c9, 30, 0x402690),
        (0x404203, 15, 0x402690),
        (0x404212, 17, 0x402690),
        (0x4044ab, 18, 0x402690),
        (0x4044bd, 57, 0x402690),
        (0x4044f6, 27, 0x402690),
        (0x404511, 30, 0x402690),
        (0x40452f, 14, 0x402690),
        (0x40453d, 16, 0x402690),
        (0x40454d, 5, 0x402690),
        (0x404552, 25, 0x402690),
        (0x40456b, 15, 0x402690),
        (0x40457a, 15, 0x402690),
        (0x404589, 27, 0x402690),
        (0x40292e, 10, 0x402690),
        (0x402938, 48, 0x402690),
        (0x402987, 7, 0x402690),
        (0x40298e, 12, 0x402690),
        (0x40299a, 37, 0x402690),
        (0x4029bf, 12, 0x402690),
        (0x4029cb, 37, 0x402690),
        (0x4029f0, 22, 0x402690),
        (0x402a06, 33, 0x402690),
        (0x402a27, 25, 0x402690),
        (0x402a40, 12, 0x402690),
        (0x402a4c, 15, 0x402690),
        (0x402a5b, 17, 0x402690),
        (0x402a6c, 15, 0x402690),
        (0x402a7b, 12, 0x402690),
        (0x402a87, 21, 0x402690),
        (0x402a9c, 21, 0x402690),
        (0x402ab1, 35, 0x402690),
        (0x402ad4, 20, 0x402690),
        (0x402ae8, 21, 0x402690),
        (0x402afd, 12, 0x402690),
        (0x402b09, 17, 0x402690),
        (0x402b1a, 14, 0x402690),
        (0x402b28, 15, 0x402690),
        (0x402b37, 17, 0x402690),
        (0x402b48, 15, 0x402690),
        (0x402b57, 12, 0x402690),
        (0x402b63, 15, 0x402690),
        (0x402b72, 12, 0x402690),
        (0x402b7e, 15, 0x402690),
        (0x402b8d, 25, 0x402690),
        (0x402ba6, 13, 0x402690),
        (0x402bb3, 15, 0x402690),
        (0x402bc2, 13, 0x402690),
        (0x402bcf, 15, 0x402690),
        (0x402c3b, 12, 0x402690),
        (0x402c47, 64, 0x402690),
        (0x402c87, 37, 0x402690),
        (0x402cac, 58, 0x402690),
        (0x402ce6, 12, 0x402690),
        (0x402cf2, 59, 0x402690),
        (0x402d2d, 58, 0x402690),
        (0x402d67, 43, 0x402690),
        (0x402d92, 12, 0x402690),
        (0x402d9e, 21, 0x402690),
        (0x402db3, 58, 0x402690),
        (0x402ded, 15, 0x402690),
        (0x402dfc, 15, 0x402690),
        (0x402e0b, 16, 0x402690),
        (0x402e1b, 49, 0x402690),
        (0x402e4c, 9, 0x402690),
        (0x402e55, 12, 0x402690),
        (0x402e61, 30, 0x402690),
        (0x402e7f, 19, 0x402690),
        (0x402e92, 12, 0x402690),
        (0x402e9e, 15, 0x402690),
        (0x402ead, 31, 0x402690),
        (0x402ecc, 11, 0x402690),
        (0x402ed7, 52, 0x402690),
        (0x402f0b, 20, 0x402690),
        (0x402f1f, 21, 0x402690),
        (0x402f34, 15, 0x402690),
        (0x402f43, 21, 0x402690),
        (0x402f58, 12, 0x402690),
        (0x402f64, 12, 0x402690),
        (0x402f70, 12, 0x402690),
        (0x402f7c, 15, 0x402690),
        (0x402f8b, 22, 0x402690),
        (0x402fa1, 15, 0x402690),
        (0x4037a4, 57, 0x402690),
        (0x4037dd, 29, 0x402690),
        (0x40418c, 18, 0x402690),
        (0x40419e, 23, 0x402690),
        (0x4041e7, 28, 0x402690),
]



class MsSwitchTest(unittest.TestCase):
    def test_ms_switch_0(self):
        base = 0x400000     # looks for reg at 0x3fb120
        fva = base + 0x4ee0
        vw = genMsSwitchWorkspace(MS_MAPS, base)
        vw.setMeta('DefaultCall', 'msx64call')
        vw.makeFunction(fva)
        funcblocks = vw.getFunctionBlocks(fva)
        funcblocks.sort()

        logger.debug("\n\n%s blocks:\n\t%r\n\t%r" % (self, funcblocks, cbs_ms_0))
        logger.debug("switches: %r" % vw.getVaSetRows('SwitchCases') )
        self.assertEqual(vw.getFunctionBlocks(fva), cbs_ms_0)
        self.assertEqual(len(vw.getXrefsFrom(base+0x11257)), 5)

class PosixSwitchTest(unittest.TestCase):
    def test_libc_switch_0(self):
        vw = genLinuxSwitchWorkspace(LIBC_MAPS, 0x500000)
        vw.makeFunction(0x500000)
        funcblocks = vw.getFunctionBlocks(0x500000)
        funcblocks.sort()

        logger.debug("\n\n%s blocks:\n\t%r\n\t%r" % (self, funcblocks, cbs_libc_0))
        logger.debug("switches: %r" % vw.getVaSetRows('SwitchCases') )
        self.assertEqual(vw.getFunctionBlocks(0x500000), cbs_libc_0)

class WalkerSwitchTest(unittest.TestCase):
    def test_walker_switch_0(self):
        vw = genLinuxSwitchWorkspace(WALKER_MAPS, 0x500000)
        vw.makeFunction(0x500000)
        funcblocks = vw.getFunctionBlocks(0x500000)
        funcblocks.sort()

        #self.assertEqual(vw.getFunctionBlocks(0x500000), cbs_walker_0)
        # TODO: enable this when we actually identify this switchcase


import vivisect.tests.helpers as helpers
class LsSwitchTest(unittest.TestCase):
    def test_ls_switch(self):
        self.maxDiff = None
        vw = helpers.getTestWorkspace('linux', 'amd64', 'ls')

        fva = 0x404223
        vw.makeFunction(fva)
        funcblocks = vw.getFunctionBlocks(fva)
        funcblocks.sort()
        cbs_amd64_ls_0.sort()
        logger.debug("\n\n%s (2) blocks:\n\t%r\n\t%r" % (self, funcblocks, cbs_amd64_ls_0))
        logger.debug("switches: %r" % vw.getVaSetRows('SwitchCases') )
        self.assertEqual(funcblocks, cbs_amd64_ls_0)

        fva = 0x402690
        vw.makeFunction(fva)
        funcblocks = vw.getFunctionBlocks(fva)
        funcblocks.sort()
        cbs_amd64_ls_1.sort()
        logger.debug("\n\n%s blocks:\n\t%r\n\t%r" % (self, funcblocks, cbs_amd64_ls_1))
        logger.debug("switches: %r" % vw.getVaSetRows('SwitchCases') )
        self.assertEqual(funcblocks, cbs_amd64_ls_1)


#=======  test generator code =======

import visgraph.pathcore as vg_path
import vivisect.impemu.monitor as viv_imp_monitor

MAX_GAP = 100
MAX_INSTR_SIZE = 20

class AnalysisMonitor(viv_imp_monitor.AnalysisMonitor):
    def __init__(self, vw, fva):
        viv_imp_monitor.AnalysisMonitor.__init__(self, vw, fva)
        self.vas = []
        
    def prehook(self, emu, op, starteip):
        #print "0x%x: %r" % (op.va, op)
        if starteip not in self.vas:
            self.vas.append(starteip)

def analyzeFunction(vw, fva):
    maps = getFuncMaps(vw, fva)
    return maps


def getFuncMaps(vw, fva):
    opvas, refvas = getVas(vw, fva)

    vas = list(opvas)
    vas.extend(refvas['reads'])
    vas.sort()

    maps = []
    perms = 'e_mem.MM_RWX'
    lastva = startva = vas[0]
    for va in vas:
        #print hex(va), hex(lastva), hex(startva)
        if (va - lastva) > MAX_GAP:
            size = lastva+MAX_INSTR_SIZE - startva
            memory = vw.readMemory(startva, size)
            maps.append((startva, size, perms, memory))
            startva = va

        lastva = va

    # grab the last map
    size = lastva+MAX_INSTR_SIZE - startva
    memory = vw.readMemory(startva, size)
    maps.append((startva, size, perms, memory))

    return maps

emu = None
def getVas(vw, fva):
    global emu
    emumon = AnalysisMonitor(vw, fva)
    emu = vw.getEmulator(logread=True, logwrite=True)
    emu.setEmulationMonitor(emumon)
    emu.runFunction(fva, maxhit=1)

    opvas = list(emumon.vas)

    refvas = getReadsWrites(emu)

    return opvas, refvas

def getReadsWrites(emu):
    refvas = {'reads':[], 'writes':{}}
    count = 0
    for path in vg_path.getAllPaths(emu.path):
        #print("PATH %d" % count)
        for nparent, nkids, ndata in path:
            #print ndata
            for opva, refva, refsz in ndata.get('readlog'):
                if emu.vw.isValidPointer(refva):
                    refvas['reads'].append(refva)
                    refvas['reads'].append(refva+refsz)

            for opva, refva, wdata in ndata.get('writelog'):
                refsz = len(wdata)
                if emu.vw.isValidPointer(refva):
                    refvas['writes'].append(refva)
                    refvas['writes'].append(refva+refsz)

        count += 1

    return refvas

if globals().get('vw') is not None:
    va = vw.parseExpression(argv[1])
    fva = vw.getFunction(va)
    vprint("analyzing Funcva (0x%x) for provided va (0x%x)" % (va, fva))
    maps = getFuncMaps(vw, fva)
    print('maps = [\\')
    for startva, sz, perms, mem in maps:
        print('(0x%x, 0x%x, %s, %r),' % (startva, sz, perms, mem))
