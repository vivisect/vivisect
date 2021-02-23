
"""
An analysis module that looks for likely *code* pointers by
checking for them to be pointing to imports and having
"call [deref]" bytes before them.
"""

from vivisect.const import *


def analyze(vw):

    for va, dest in vw.findPointers():
        # Is there a location already at the target?
        loc = vw.getLocation(dest)
        if loc is None:
            continue

        if loc[L_LTYPE] != LOC_IMPORT:
            continue

        offset, bytes = vw.getByteDef(va)
        if offset < 2:
            continue

        if bytes[offset-2:offset] == b"\xff\x15":  # call [importloc]
            # If there's a pointer here, remove it.
            if vw.getLocation(va):
                vw.delLocation(va)
            vw.makeCode(va-2)
