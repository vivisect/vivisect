from vivisect.const import *


STRTYPES = (LOC_UNI, LOC_STRING)


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

                    # we've already processed this one
                    loc = vw.getLocation(ref)
                    if loc is not None and loc[L_LTYPE] in STRTYPES:
                        continue

                    # Candidates will be listed with the Xrefs thanks to
                    # logic in makeOpcode().
                    if not (vw.getXrefsTo(ref) and vw.getXrefsFrom(va)):
                        continue

                    # String constants must be in a defined memory segment.
                    if not vw.getSegment(ref):
                        continue

                    # Look for Unicode before ASCII to catch UTF-16 LE.
                    sz = vw.detectUnicode(ref)
                    if sz > 0:
                        vw.addLocation(ref, sz, LOC_UNI)
                    else:
                        sz = vw.detectString(ref)
                        if sz > 0:
                            vw.addLocation(ref, sz, LOC_STRING)

                va += len(op)
    return
