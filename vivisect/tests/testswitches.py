import unittest
import vivisect
import envi.memory as e_mem

MAPS = [
    (0x884ee0, 112L, 'H\x83\xecHH\x85\xc9\x0f\x84{\xbe\x01\x00\x83\xf9\xf4\x0f\x83\xb97\x01\x00H\x85\xc9\x0f\x84i\xbe\x01\x00L\x8dD$PH\x8dT$0A\xb9\x08\x00\x00\x00\xc7D$ \x04\x00\x00\x00\xff\x15\xcbS\x04\x00\x85\xc0\x0f\x88\xa77\x01\x00H\x8bD$P\x83\xf8\x07\x0f\x85\xff\xc2\x00\x00\xb8\x01\x00\x00\x00H\x83\xc4H\xc3\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90'),
    (0x891232, 68L, '\x8dH\xfe\x83\xf9)\x0f\x87\x89\xfb\x00\x00H\x8d\x15\xbb\xed\xfe\xff\x0f\xb6\x84\n@\xc5\x01\x00\x8b\x8c\x820\xc5\x01\x00H\x03\xca\xff\xe1\xb8\x03\x00\x00\x00H\x83\xc4H\xc3\x8b\xc1%\x00\x00\x00\xc0=\x00\x00\x00\x80\x0f\x84\xe8\xfa\x00\x00\xe8'),
    (0x8986af, 62L, '\x0f\x84\xf8\x86\x00\x00\x83\xf9\xf5\x0f\x84\xd5\x86\x00\x00\x83\xf9\xf6\x0f\x85/\xc8\xfe\xff\xe9\xad\x86\x00\x00\x8b\xc8\xe8=\x90\xfe\xff3\xc0H\x83\xc4H\xc3H\x8d\r?\x90\x04\x00\xff\x15\x81\x1b\x03\x00\xe84\x04\xff\xffH'),
    (0x899db9, 29L, '\xb8\x02\x00\x00\x00H\x83\xc4H\xc3\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90H\x83\xec(D\x0f'),

    (0x89c634, 24L, '\x89\xf2\x00\x00\x89\xf2\x00\x00\x89\xf2\x00\x00\x89\xf2\x00\x00W\x98\x00\x00\x0f\xf9\x00\x00'),
    (0x8a0d68, 129L, '\xb9\x08\x00\x00\xc0\xe8\x9e\t\xfe\xff3\xc0H\x83\xc4H\xc3eH\x8b\x04%0\x00\x00\x00H\x8bH`H\x8bA H\x8bH \xe9cA\xfe\xffeH\x8b\x04%0\x00\x00\x00H\x8bH`H\x8bA H\x8bH(\xe9IA\xfe\xffeH\x8b\x04%0\x00\x00\x00H\x8bH`H\x8bA H\x8bH0\xe9/A\xfe\xff3\xc9\xff\x15\xd1\x92\x02\x003\xc0H\x83\xc4H\xc3eH\x8b\x04%0\x00\x00\x00L\x8b\xc73\xd2H\x8bH`H'),
    (0x8ca0a0, 28L, '@ \xeax\x00\x00\x00\x00@\xff\xe9x\x00\x00\x00\x00p\x1e\xeax\x00\x00\x00\x00p\x12\xeax'),
    (0x8ca2e8, 28L, '@\x03\xeax\x00\x00\x00\x00\x10\xff\xe9x\x00\x00\x00\x000\xff\xe9x\x00\x00\x00\x00`\x03\xeax')
 ]


maptblbase = 0x89c530
maptblbytes = '3O\x00\x00\xb9\x9d\x01\x00Y\x12\x01\x00\xc7\r\x02\x00\x00\x00\x00\x00\x00\x00\x00\x03\x03\x01\x03\x03\x03\x01\x03\x02\x03\x03\x03\x01\x01\x03\x01\x03\x03\x01\x01\x01\x03\x03\x03\x03\x03\x03\x00\x03\x03\x03\x03\x03\x03\x01\x90\x90\x9cz\x01\x00'



def genMsSwitchWorkspace(maps=MAPS, mapbase=0x400000, bufferpages=2):
    vw = vivisect.VivWorkspace()
    vw.setMeta('Architecture', 'i386')
    vw.setMeta('Platform', 'windows')
    vw.setMeta('Format', 'pe')
    vw._snapInAnalysisModules()

    applyMaps(vw, maps, mapbase, bufferpages)
    return vw

def applyMaps(vw, maps=MAPS, mapbase=0x400000, bufferpages=2):
    bufferpgsz = bufferpages * 4096
    vw.addMemoryMap(mapbase - bufferpgsz, e_mem.MM_RWX, 'testswitches', '@' * bufferpgsz)

    mapdelta = mapbase - maps[0][0]
    

    vw.addFile('testswitches', mapbase, "@@@@@@@@")
    for mapva, sz, mem in maps:
        mapva += mapdelta
        vw.addMemoryMap(mapva, e_mem.MM_RWX, 'testswitches', mem)
        vw.addSegment(mapva, len(mem), 'switch_code_%x' % mapva, 'testswitches')

    # map with table(s)
    tblbase = maptblbase + mapdelta
    vw.addMemoryMap(tblbase, e_mem.MM_READ, 'testswitches', maptblbytes)
    vw.addSegment(tblbase, len(maptblbytes), 'switch_table_%x' % mapva, 'testswitches')

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

class MsSwitchTest(unittest.TestCase):
    def test_ms_switch_0(self):
        vw = genMsSwitchWorkspace(MAPS, 0x400000)
        vw.makeFunction(0x400000)
        
        self.assertEqual(vw.getFunctionBlocks(0x400000), cbs_ms_0)




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
    lastva = startva = vas[0]
    for va in vas:
        #print hex(va), hex(lastva), hex(startva)
        if (va - lastva) > MAX_GAP:
            size = lastva+MAX_INSTR_SIZE - startva
            memory = vw.readMemory(startva, size)
            maps.append((startva, size, memory))
            startva = va

        lastva = va

    # grab the last map
    size = lastva+MAX_INSTR_SIZE - startva
    memory = vw.readMemory(startva, size)
    maps.append((startva, size, memory))

    return maps

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
                if vw.isValidPointer(refva):
                    refvas['reads'].append(refva)
                    refvas['reads'].append(refva+refsz)

            for opva, refva, wdata in ndata.get('writelog'):
                refsz = len(wdata)
                if vw.isValidPointer(refva):
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
    for startva, sz, mem in maps:
        print('(0x%x, 0x%x, %r),' % (startva, sz, mem))
