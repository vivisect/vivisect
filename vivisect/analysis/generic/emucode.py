"""
Find all undefined reference targets and attempt to determine
if they are code by emulation behaviorial analysis.

(This module works best very late in the analysis passes)
"""
import envi
import vivisect
import vivisect.exc as v_exc
from envi.archs.i386.opconst import *
import vivisect.impemu.monitor as viv_imp_monitor

import logging

from vivisect.const import *

logger = logging.getLogger(__name__)


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

    def looksgood(self):
        if not self.hasret or self.badcode:
            return False

        # if there is 1 mnem that makes up over 50% of all instructions then flag it as invalid
        for mnem, count in self.mndist.items():
            if round(float( float(count) / float(self.insn_count)), 3) >= .67 and self.insn_count > 4:
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
        if op.mnem == "out":  # FIXME arch specific. see above idea.
            emu.stopEmu()
            raise v_exc.BadOutInstruction(op.va)

        if op in self.badops:
            emu.stopEmu()
            raise v_exc.BadOpBytes(op.va)

        if op.iflags & envi.IF_RET:
            self.hasret = True
            emu.stopEmu()

        self.lastop = op

        loc = self.vw.getLocation(eip)
        if loc is not None:
            va, size, ltype, linfo = loc
            if ltype != vivisect.LOC_OP:
                emu.stopEmu()
                raise Exception("HIT LOCTYPE %d AT 0x%.8x" % (ltype, va))

        cnt = self.mndist.get(op.mnem, 0)
        self.mndist[op.mnem] = cnt + 1
        self.insn_count += 1
        if self.vw.isNoReturnVa(eip):
            self.hasret = True
            emu.stopEmu()

        # FIXME do we need a way to terminate emulation here?
    def apicall(self, emu, op, pc, api, argv):
        # if the call is to a noret API we are done
        if self.vw.isNoReturnVa(pc):
            self.hasret = True
            emu.stopEmu()


def analyze(vw):

    flist = vw.getFunctions()

    tried = set()
    while True:
        docode = []
        bcode = []

        vatodo = set([va for va, name in vw.getNames() if vw.getLocation(va) is None and va not in tried])
        vatodo = vatodo.union([tova for _, tova, _, _ in vw.getXrefs(rtype=REF_PTR) if vw.getLocation(tova) is None and tova not in tried])
        for va in vatodo:
            loc = vw.getLocation(va)
            if loc is not None:
                if loc[L_LTYPE] == LOC_STRING:
                    vw.makeString(va)
                    tried.add(va)
                elif loc[L_LTYPE] == LOC_UNI:
                    vw.makeUnicode(va)
                    tried.add(va)
                continue

            if vw.isDeadData(va):
                continue

            # Skip it if we've tried it already.
            if va in tried:
                continue

            tried.add(va)

            # if it's not exectuable, check to see if it's at least readable, in which case
            # we can check for other location types
            # otherwise, try emulating it to see if it feels like code
            if not vw.isExecutable(va):
                if not vw.isReadable(va):
                    continue
                if vw.isProbablyUnicode(va):
                    vw.makeUnicode(va)
                elif vw.isProbablyString(va):
                    vw.makeString(va)
            else:
                emu = vw.getEmulator()
                wat = watcher(vw, va)
                emu.setEmulationMonitor(wat)

                try:
                    emu.runFunction(va, maxhit=1)
                except Exception:
                    continue

                if wat.looksgood():
                    docode.append(va)
                # flag to tell us to be greedy w/ finding code
                # XXX - visi is going to hate this..
                elif wat.iscode() and vw.greedycode:
                    bcode.append(va)
                else:
                    if vw.isProbablyUnicode(va):
                        vw.makeUnicode(va)
                    elif vw.isProbablyString(va):
                        vw.makeString(va)
                    else:
                        # if we get all the way down here, and it has a name, it's gotta be *something*
                        if vw.getName(va):
                            vw.makePointer(va)

        if len(docode) == 0:
            break

        docode.sort()
        for va in docode:
            if vw.getLocation(va) is not None:
                continue
            try:
                logger.debug('discovered new function: 0x%x', va)
                vw.makeFunction(va)
            except:
                continue

        bcode.sort()
        for va in bcode:
            if vw.getLocation(va) is not None:
                continue
            # TODO: consider elevating to functions?
            vw.makeCode(va)

    dlist = vw.getFunctions()

    newfuncs = set(dlist) - set(flist)
    for fva in newfuncs:
        vw.setVaSetRow('EmucodeFunctions', (fva,))

    vw.vprint("emucode: %d new functions defined (now total: %d)" % (len(dlist)-len(flist), len(dlist)))
