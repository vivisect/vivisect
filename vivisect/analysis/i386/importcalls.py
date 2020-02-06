
"""
An analysis module that looks for likely *code* pointers by
checking for them to be pointing to imports and having
"call [deref]" bytes before them.
"""

import vivisect.const as v_const


def analyze(vw):

    for va, dest in vw.findPointers():
        # Is there a location already at the target?
        loc = vw.getLocation(dest)
        if loc is None:
            continue

        if loc[v_const.L_LTYPE] != v_const.LOC_IMPORT:
            continue

        offset, bytes = vw.getByteDef(va)
        if offset < 2:
            continue

        if bytes[offset-2:offset] == "\xff\x15":  # call [importloc]
            # If there's a pointer here, remove it.
            if vw.getLocation(va):
                vw.delLocation(va)
            vw.makeCode(va-2)
