"""
Find all undefined reference targets and attempt to determine
if they are code by emulation behaviorial analysis.

(This module works best very late in the analysis passes)
"""
import envi
import vivisect
import vivisect.reports as viv_rep
from envi.archs.i386.opconst import *
import vivisect.impemu.monitor as viv_imp_monitor

from vivisect.const import *

verbose = False

class watcher(viv_imp_monitor.EmulationMonitor):

    def __init__(self, vw, tryva):
        viv_imp_monitor.EmulationMonitor.__init__(self)
        self.vw = vw
        self.tryva = tryva
        self.hasret = False
        self.mndist = {}
        self.insn_count = 0
        self.lastop = None
        self.badcode = False

        self.badops = vw.arch.archGetBadOps()

    def logAnomaly(self, emu, eip, msg):
        self.badcode = True
        emu.stopEmu()
        
        #self.vw.verbprint("Emucode: 0x%.8x (f:0x%.8x) %s" % (eip, self.tryva, msg))

    def looksgood(self):
        if not self.hasret or self.badcode: 
            return False

        # if there is 1 mnem that makes up over 50% of all instructions then flag it as invalid
        for mnem, count in self.mndist.items():
            if round(float( float(count) / float(self.insn_count)), 3) >= .67:
                return False

        return True

    def iscode(self):
        op = self.lastop

        if not self.lastop:
            return False

        if not (op.iflags & envi.IF_RET) and not (op.iflags & envi.IF_BRANCH) and not (op.iflags & envi.IF_CALL):
            return False

        for mnem, count in self.mndist.items():
            # XXX - CONFIG OPTION
            if round(float( float(count) / float(self.insn_count)), 3) >= .60:
                return False

        return True


    def prehook(self, emu, op, eip):
        if op.mnem == "out": #FIXME arch specific. see above idea.
            emu.stopEmu()
            raise Exception("Out instruction...")

        if op in self.badops:
            emu.stopEmu()
            raise Exception("Hit known BADOP at 0x%.8x %s" % (eip,repr(op)))

        if op.iflags & envi.IF_RET:
            self.hasret = True
            emu.stopEmu()

        self.lastop = op
        # Make sure we didn't run into any other
        # defined locations...
        if self.vw.isFunction(eip):
            emu.stopEmu()
            # FIXME: this is a problem.  many time legit code falls into other functions...  "hydra" functions are more and more common.
            raise Exception("Fell Through Into Function: %.8x" % eip)

        loc = self.vw.getLocation(eip)
        if loc != None:
            va, size, ltype, linfo = loc
            if ltype != vivisect.LOC_OP:
                emu.stopEmu()
                raise Exception("HIT LOCTYPE %d AT %.8x" % (ltype, va))

        cnt = self.mndist.get(op.mnem, 0)
        self.mndist[ op.mnem ] = cnt+1
        self.insn_count += 1

        # FIXME do we need a way to terminate emulation here?
    def apicall(self, emu, op, pc, api, argv):
        # if the call is to a noret API we are done
        if self.vw.isNoReturnVa(pc):
            self.hasret = True
            emu.stopEmu()

def analyze(vw):

    flist = vw.getFunctions()

    tried = {}
    vasetrows = []
    while True:
        docode = []
        bcode  = []
       
        vatodo = []
        vatodo = [ va for va, name in vw.getNames() if vw.getLocation(va) == None ]
        vatodo.extend( [tova for fromva, tova, reftype, rflags in vw.getXrefs(rtype=REF_PTR) if vw.getLocation(tova) == None] )

        for va in set(vatodo):
            if vw.getLocation(va) != None:
                continue
            if vw.isDeadData(va):
                continue

            # Make sure it's executable
            if not vw.isExecutable(va):
                continue

            # Skip it if we've tried it already.
            if tried.get(va):
                continue

            tried[va] = True
            emu = vw.getEmulator()
            wat = watcher(vw, va)
            emu.setEmulationMonitor(wat)
            try:
                emu.runFunction(va, maxhit=1)
            except Exception, e:
                continue
            if wat.looksgood():
                docode.append(va)
            # flag to tell us to be greedy w/ finding code
            # XXX - visi is going to hate this..
            elif wat.iscode() and vw.greedycode:
                bcode.append(va)
            else:
                if vw.isProbablyString(va):
                    vw.makeString(va)
                elif vw.isProbablyUnicode(va):
                    vw.makeUnicode(va)

        if len(docode) == 0:
            break

        docode.sort()
        for va in docode:
            if vw.getLocation(va) != None:
                continue
            # XXX - RP 
            try:
                vw.makeFunction(va)
            except: 
                continue
            vasetrows.append((va,))
    
        bcode.sort()
        for va in bcode:
            if vw.getLocation(va) != None:
                continue
            vw.makeCode(va)

    dlist = vw.getFunctions()

    vw.verbprint("emucode: %d new functions defined (now total: %d)" % (len(dlist)-len(flist), len(dlist)))

