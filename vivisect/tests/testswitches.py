import unittest
import vivisect
import envi.memory as e_mem

MS_MAPS = [
    (0x884ee0, 112L, e_mem.MM_RWX, 'H\x83\xecHH\x85\xc9\x0f\x84{\xbe\x01\x00\x83\xf9\xf4\x0f\x83\xb97\x01\x00H\x85\xc9\x0f\x84i\xbe\x01\x00L\x8dD$PH\x8dT$0A\xb9\x08\x00\x00\x00\xc7D$ \x04\x00\x00\x00\xff\x15\xcbS\x04\x00\x85\xc0\x0f\x88\xa77\x01\x00H\x8bD$P\x83\xf8\x07\x0f\x85\xff\xc2\x00\x00\xb8\x01\x00\x00\x00H\x83\xc4H\xc3\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90'),
    (0x891232, 68L, e_mem.MM_RWX, '\x8dH\xfe\x83\xf9)\x0f\x87\x89\xfb\x00\x00H\x8d\x15\xbb\xed\xfe\xff\x0f\xb6\x84\n@\xc5\x01\x00\x8b\x8c\x820\xc5\x01\x00H\x03\xca\xff\xe1\xb8\x03\x00\x00\x00H\x83\xc4H\xc3\x8b\xc1%\x00\x00\x00\xc0=\x00\x00\x00\x80\x0f\x84\xe8\xfa\x00\x00\xe8'),
    (0x8986af, 62L, e_mem.MM_RWX, '\x0f\x84\xf8\x86\x00\x00\x83\xf9\xf5\x0f\x84\xd5\x86\x00\x00\x83\xf9\xf6\x0f\x85/\xc8\xfe\xff\xe9\xad\x86\x00\x00\x8b\xc8\xe8=\x90\xfe\xff3\xc0H\x83\xc4H\xc3H\x8d\r?\x90\x04\x00\xff\x15\x81\x1b\x03\x00\xe84\x04\xff\xffH'),
    (0x899db9, 29L, e_mem.MM_RWX, '\xb8\x02\x00\x00\x00H\x83\xc4H\xc3\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90H\x83\xec(D\x0f'),

    (0x89c634, 24L, e_mem.MM_RWX, '\x89\xf2\x00\x00\x89\xf2\x00\x00\x89\xf2\x00\x00\x89\xf2\x00\x00W\x98\x00\x00\x0f\xf9\x00\x00'),
    (0x8a0d68, 129L, e_mem.MM_RWX, '\xb9\x08\x00\x00\xc0\xe8\x9e\t\xfe\xff3\xc0H\x83\xc4H\xc3eH\x8b\x04%0\x00\x00\x00H\x8bH`H\x8bA H\x8bH \xe9cA\xfe\xffeH\x8b\x04%0\x00\x00\x00H\x8bH`H\x8bA H\x8bH(\xe9IA\xfe\xffeH\x8b\x04%0\x00\x00\x00H\x8bH`H\x8bA H\x8bH0\xe9/A\xfe\xff3\xc9\xff\x15\xd1\x92\x02\x003\xc0H\x83\xc4H\xc3eH\x8b\x04%0\x00\x00\x00L\x8b\xc73\xd2H\x8bH`H'),
    (0x8ca0a0, 28L, e_mem.MM_RWX, '@ \xeax\x00\x00\x00\x00@\xff\xe9x\x00\x00\x00\x00p\x1e\xeax\x00\x00\x00\x00p\x12\xeax'),
    (0x8ca2e8, 28L, e_mem.MM_RWX, '@\x03\xeax\x00\x00\x00\x00\x10\xff\xe9x\x00\x00\x00\x000\xff\xe9x\x00\x00\x00\x00`\x03\xeax'),

    (0x89c530, 64, e_mem.MM_READ, '3O\x00\x00\xb9\x9d\x01\x00Y\x12\x01\x00\xc7\r\x02\x00\x00\x00\x00\x00\x00\x00\x00\x03\x03\x01\x03\x03\x03\x01\x03\x02\x03\x03\x03\x01\x01\x03\x01\x03\x03\x01\x01\x01\x03\x03\x03\x03\x03\x03\x00\x03\x03\x03\x03\x03\x03\x01\x90\x90\x9cz\x01\x00'), # table
]

# 32bit libc-2.13.so.  switch jmp at 0x0205af11
LIBC_MAPS = [\
    (0x205ab40, 0x107, e_mem.MM_RWX, 'U\x89\xe5WVS\x83\xec\x14\x8bM\x08\xe8\x1e\xc1\xfb\xff\x81\xc3\xa3\xe4\x0f\x00\x8bu\x0c\x85\xc9\x0f\x84\x9c\x00\x00\x00\x8b\x93\xf8\xfe\xff\xff\x85\xd2tt\x8bE\x08\x8b@h\x85\xc0~j\x89e\xf0\x894$\xe8\xff\x8c\x01\x00\x8dx\x01\x8d\x04\xbd\x10\x00\x00\x00)\xc4\x8dD$\x1f\x83\xe0\xf0\x85\xfft%\x0f\xb6\x0e\x84\xc9xo1\xd2\xeb\r\x90\x8dt&\x00\x0f\xb6\x0c\x16\x84\xc9x^\x0f\xbe\xc9\x89\x0c\x90\x83\xc2\x019\xd7w\xeb\x8dU\x10\x89T$\x08\x89D$\x04\x8bE\x08\x89\x04$\xe8mN\xff\xff\x8be\xf0\x8de\xf4[^_]\xc3f\x90\x8dU\x10\x89t$\x04\x89T$\x08\x8bE\x08\x89\x04$\xe8\x1a#\xfe\xff\x8de\xf4[^_]\xc3\x8b\x83H\xff\xff\xff\x8b\x00\x89E\x08\xe9T\xff\xff\xff\x8d\x836\xa1\xfd\xff\x89D$\x0c\x8d\x83\x11\xa1\xfd\xff\x89D$\x04\x8d\x83\x1c\xa1\xfd\xff\xc7D$\x08/\x00\x00\x00\x89\x04$\xe8\x98\x8a\xfc\xff\x90\x90\x90\x90\x90\x90\x90\x90U\x89\xe5WVS\x83'),
    ]



WALKER_MAPS = maps = [\
    (0x201a5a0, 0x9b, e_mem.MM_RWX, 'UH\x89\xe5H\x83\xec0@\x88\xf0H\x89}\xf8\x88E\xf7H\x89U\xe8H\x8bU\xf8H\x89\xd7H\x83\xc7`H\x8bu\xe8H\x89U\xe0\xe8R\x1a\x00\x00\xa8\x01\x0f\x85\x05\x00\x00\x00\xe9\x05\x00\x00\x00\xe9V\x01\x00\x00H\x8bE\xe0H\x8bH8H\x83\xc18H\x8bu\xe8H\x89\xcf\xe8\x98\x1a\x00\x00H\x89\xc7\xe8\xb0\x1a\x00\x00\x83\xc0\xff\x89\xc1\x83\xe8\x0bH\x89M\xd8\x89E\xd4\x0f\x87\x1c\x01\x00\x00H\x8d\x05\xec\xc6\x05\x00H\x8bM\xd8Hc\x14\x88H\x01\xc2\xff\xe2\x8aE\xf7H\x8bU\xe8H\x8b}\xe0\x0f\xb6\xf0\xe8\x84\x1a\x00'),
    (0x201a731, 0x1e, e_mem.MM_RWX, '\xe9\x00\x00\x00\x00H\x83\xc40]\xc3\x0f\x1f@\x00UH\x89\xe5H\x89}\xf8H\x8b}\xf8H\x8b\x07'),
    (0x2076d08, 0x30, e_mem.MM_READ, '\x11:\xfa\xff!9\xfa\xff\xe19\xfa\xffi9\xfa\xff\x819\xfa\xff\x999\xfa\xff\xb19\xfa\xff99\xfa\xffQ9\xfa\xff):\xfa\xff\xc99\xfa\xff\xf99\xfa\xff'),
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


def genMsSwitchWorkspace(maps=MS_MAPS, mapbase=0x400000, bufferpages=2):
    vw = vivisect.VivWorkspace()
    vw.setMeta('Architecture', 'i386')
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
        (5243286, 6, 5242880)]

class MsSwitchTest(unittest.TestCase):
    def test_ms_switch_0(self):
        vw = genMsSwitchWorkspace(MS_MAPS, 0x400000)
        vw.makeFunction(0x400000)
        
        self.assertEqual(vw.getFunctionBlocks(0x400000), cbs_ms_0)
        #self.assertEqual(vw.getXrefsFrom(0x

class PosixSwitchTest(unittest.TestCase):
    def test_libc_switch_0(self):
        vw = genLinuxSwitchWorkspace(LIBC_MAPS, 0x500000)
        vw.makeFunction(0x500000)
        self.assertEqual(vw.getFunctionBlocks(0x500000), cbs_libc_0)

class WalkerSwitchTest(unittest.TestCase):
    def test_walker_switch_0(self):
        self.maxDiff = None
        vw = genLinuxSwitchWorkspace(WALKER_MAPS, 0x500000)
        vw.makeFunction(0x500000)
        self.assertEqual(vw.getFunctionBlocks(0x500000), cbs_walker_0)


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
