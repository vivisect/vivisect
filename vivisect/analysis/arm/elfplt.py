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


MAX_INSTR_COUNT = 3

def analyzeFunction(vw, funcva):
    #global emu, op, oper0, opval
    #try:
        seg = vw.getSegment(funcva)
        if seg == None:
            return

        segva, segsize, segname, segfname = seg

        if segname not in (".plt", ".plt.got"):
            return
        #print "ARM EMU-PLT: %x" % funcva

        emu = vw.getEmulator()
        emu.setProgramCounter(funcva)
        offset = 0
        branch = False
        for cnt in range(MAX_INSTR_COUNT):
            op = vw.parseOpcode(funcva + offset)
            if op.iflags & envi.IF_BRANCH == 0:
                emu.executeOpcode(op)
                offset += len(op)
                #print "skip->", hex(emu.getProgramCounter())
                continue
            branch = True
            break

        if not branch:
            return

        #print "got branch"
        loctup = None
        oper1 = op.opers[1]
        #print oper1
        opval = oper1.getOperAddr(op, emu=emu)
        #raw_input("ASDFASDF")
        #if opval == None:
            #print op, hex(op.va), (opval)
        #else:
            #print op, hex(op.va), hex(opval)
        loctup = vw.getLocation(opval)
        #raw_input( loctup)

        if loctup == None:
            return

        if loctup[vivisect.L_LTYPE] != vivisect.LOC_IMPORT: # FIXME: Why are AMD64 IMPORTS showing up as POINTERs?
            print "0x%x: " % funcva, loctup[vivisect.L_LTYPE], ' != ', vivisect.LOC_IMPORT
            #return

        gotname = vw.getName(opval)
        #print hex(opval), gotname
        tinfo = gotname
        #vw.makeName(funcva, "plt_%s" % fname, filelocal=True)
        vw.makeFunctionThunk(funcva, tinfo)

    #except Exception, e:
        #print e
