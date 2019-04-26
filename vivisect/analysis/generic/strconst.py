from vivisect.const import *


def analyze(vw):
    '''
    Find string constants used in function calls and add them to the
    workspace location set.  The goal is to identify string constants
    for symboliks parsing, where they become string arguments.

    Functions and xrefs have already been identified.  Analysis of opcodes
    is closely related to the makeOpcode() logic in vivisect/__init__.py.
    '''

    for fva in vw.getFunctions():
        for va, size, funcva in vw.getFunctionBlocks(fva):
            maxva = va + size
            while va < maxva:
                op = vw.parseOpcode(va)
                for o in op.opers:
                    if o.isDeref():
                        continue
                    ref = o.getOperValue(op, None)

                    # Candidates will be listed with the Xrefs thanks to
                    # logic in makeOpcode().
                    if not (vw.getXrefsTo(ref) and vw.getXrefsFrom(va)):
                        continue

                    # String constants must be in a defined memory segment.
                    if not vw.getSegment(ref):
                        continue

                    sz = vw.detectString(ref)
                    if sz > 0:
                        vw.addLocation(ref, sz, LOC_STRING)
                    else:
                        sz = vw.detectUnicode(ref)
                        if sz > 0:
                            vw.addLocation(ref, sz, LOC_UNI)

                va += len(op)
    return
