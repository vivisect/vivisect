"""
If a "function" is in the plt it's a wrapper for something in the GOT.
Make that apparent.
"""

import envi
import vivisect

import logging
logger = logging.getLogger(__name__)

def analyze(vw):
    """
    Do simple linear disassembly of the .plt section if present.
    """
    return
    for sva,ssize,sname,sfname in vw.getSegments():
        if sname != ".plt":
            continue
        nextva = sva + ssize
        while sva < nextva:
            vw.makeCode(sva)
            ltup = vw.getLocation(sva)
            sva += ltup[vivisect.L_SIZE]


MAX_INSTR_COUNT = 3

def analyzeFunction(vw, funcva):
    '''
    Function Analysis Module.  This gets run on all functions, so we need to identify that we're 
    in a PLT quickly.

    Emulates the first few instructions of each PLT function to determine the correct offset 
    into the Global Offset Table.  Then tags names, etc...
    '''
    seg = vw.getSegment(funcva)
    if seg == None:
        logger.debug("no segment for funcva 0x%x", funcva)
        return

    segva, segsize, segname, segfname = seg

    if segname not in (".plt", ".plt.got"):
        logger.debug("not in PLT segment for funcva 0x%x (%r)", funcva, segname)
        return

    
    emu = vw.getEmulator()
    emu.setProgramCounter(funcva)
    offset = 0
    branch = False
    for cnt in range(MAX_INSTR_COUNT):
        op = emu.parseOpcode(funcva + offset)
        if op.iflags & envi.IF_BRANCH == 0:
            emu.executeOpcode(op)
            offset += len(op)
            continue
        branch = True
        break

    if not branch:
        logger.debug("no branch found for funcva 0x%x (after %r instrs)", funcva, cnt)
        return

    loctup = None
    oper1 = op.opers[1]
    opval = oper1.getOperAddr(op, emu=emu)
    loctup = vw.getLocation(opval)

    if loctup == None:
        logger.debug("no location found for funcva 0x%x (%r)", funcva, oper1)
        return

    if loctup[vivisect.L_LTYPE] != vivisect.LOC_IMPORT:
        logger.debug("0x%x: %r != %r (LOC_IMPORT)", funcva, loctup[vivisect.L_LTYPE], vivisect.LOC_IMPORT)

    vw.addXref(op.va, opval, vivisect.REF_DATA)
    tva = vw.readMemoryPtr(opval)
    if vw.isValidPointer(tva):
        vw.addXref(op.va, tva, vivisect.REF_CODE)

    gotname = vw.getName(opval)
    vw.makeFunctionThunk(funcva, gotname)
