
"""
If a "function" is in the plt it's a wrapper for something in the GOT.
Make that apparent.
"""

import vivisect
import envi
import envi.archs.i386 as e_i386
import envi.archs.i386.opcode86 as opcode86

def analyze(vw):
    """
    Do simple linear disassembly of the .plt section if present.
    """
    for sva,ssize,sname,sfname in vw.getSegments():
        if sname != ".plt":
            continue
        nextva = sva + ssize
        while sva < nextva:
            vw.makeCode(sva)
            ltup = vw.getLocation(sva)
            sva += ltup[vivisect.L_SIZE]

def analyzeFunction(vw, funcva):

    seg = vw.getSegment(funcva)
    if seg == None:
        return

    segva, segsize, segname, segfname = seg

    if segname != ".plt":
        return

    #FIXME check for i386
    op = vw.parseOpcode(funcva)
    if op.opcode != opcode86.INS_BRANCH:
        return

    loctup = None
    oper0 = op.opers[0]

    if isinstance(oper0, e_i386.i386ImmMemOper):
        
        loctup = vw.getLocation(oper0.getOperAddr(op))

    elif isinstance(oper0, e_i386.i386RegMemOper):
        # FIXME this is i386 elf only!
        if oper0.reg != e_i386.REG_EBX:
            print "UNKNOWN PLT CALL",hex(funcva)
        got = vw.vaByName("%s._GLOBAL_OFFSET_TABLE_" % segfname)

        #FIXME this totally sucks
        if got == None:
            for va,size,name,fname in vw.getSegments():
                if name == ".got.plt":
                    got = va
                    break

        if got != None:
            loctup = vw.getLocation(got+oper0.disp)

    if loctup == None:
        return

    if loctup[vivisect.L_LTYPE] != vivisect.LOC_IMPORT:
        return

    tinfo = loctup[vivisect.L_TINFO]
    lname,fname = tinfo.split(".")
    #vw.makeName(funcva, "plt_%s" % fname, filelocal=True)
    vw.makeFunctionThunk(funcva, tinfo)

