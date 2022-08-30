import unittest
import contextlib

import vivisect.cli as v_cli

class VivTest(unittest.TestCase):
    '''
    Base class for vivisect unit tests so that we have a common place to throw certain common
    utilities.
    '''

    def eq(self, x, y):
        '''
        Assert x is equal to y
        '''
        self.assertEqual(x, y)

    def len(self, x, y):
        '''
        Assert that length of x is equal to y
        '''
        self.assertEqual(len(x), y)

    def none(self, x):
        '''
        Assert x is none
        '''
        self.assertIsNone(x)

    def nn(self, x):
        '''
        Assert x is not none
        '''
        self.assertIsNotNone(x)

    def isin(self, x, y):
        '''
        Assert that x is a member of the container y
        '''
        self.assertIn(x, y)

    @contextlib.contextmanager
    def snap(self, vw):
        '''
        Checkpoint a workspace. Yields a new workspace that can be editted
        as the test needs, and once the context handler ends, all changes will
        tossed

        To be used with some caution, as it does create a duplicate workspace.
        '''
        safe = v_cli.VivCli()
        events = list(vw.exportWorkspace())
        safe.importWorkspace(events)
        yield safe


#=======  test generator code =======
'''
the code below helps us build unittests for switchcases, particularly in cases where the 
executable cannot be included in our test-suite.
'''

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

        for oper in op.opers:
            ref = oper.getOperValue(op, emu=emu)
            #print("==0x%x:  0x%x" % (starteip, ref))
            if self.vw.isValidPointer(ref):
                for x in range(30):
                    self.vas.append(ref + (x*emu.psize))

            if oper.isDeref():
                tsize = oper.tsize
                ref = oper.getOperAddr(op, emu=emu)
                #print("      -- ref 0x%x" % (ref,))
                if self.vw.isValidPointer(ref):
                    for x in range(30):
                        self.vas.append(ref + (x*emu.psize))

def getFuncMaps(vw, fva):
    opvas, refvas = getVas(vw, fva)

    vas = list(opvas)
    vas.extend(refvas['reads'])
    vas.sort()

    maps = []
    perms = 'e_mem.MM_RWX'
    lastva = startva = vas[0]
    #print (vas)
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

def printFuncBlocks(vw, fva, fakebase=None):
    offset=0
    if fakebase:
        offset = fakebase - fva

    print('\t[' + '\n\t '.join(['(0x%x, %d, 0x%x),' % (x+offset,y,z+offset) for x,y,z in vw.getFunctionBlocks(fva)]) + ']')


'''
we allow this to be run as a script from within Vivisect in order to easily extract relevant memory for a function
'''
if globals().get('vw') is not None:
    va = vw.parseExpression(argv[1])
    fva = vw.getFunction(va)
    vprint("analyzing Funcva (0x%x) for provided va (0x%x)" % (va, fva))
    maps = getFuncMaps(vw, fva)
    vprint('maps = [\\')
    for startva, sz, perms, mem in maps:
        vprint('    (0x%x, 0x%x, %s, %r),' % (startva, sz, perms, mem))

    vprint(']')
