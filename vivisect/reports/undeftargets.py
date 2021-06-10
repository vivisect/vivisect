"""Locate any xrefs/names to undefined locations"""

import envi.common as e_common
import vivisect.const as v_const

columns = (("Bytes", str), ("Name", str))


def report(vw):
    res = {}

    for fromva, tova, reftype, rflags in vw.getXrefs():
        if vw.getLocation(tova, range=True) is None:
            rname = v_const.ref_type_names.get(reftype, "Unknown")
            sname = "Unknown"
            seg = vw.getSegment(tova)
            if seg is not None:
                sname = seg[v_const.SEG_NAME]
            try:
                b = e_common.hexify(vw.readMemory(tova, 8))
            except Exception as e:
                b = str(e)
            res[tova] = (b, "%s ref from 0x%x (%s)" % (rname, fromva, sname))

    for va, name in vw.getNames():
        if vw.getLocation(va) is None:
            try:
                b = e_common.hexify(vw.readMemory(tova, 8))
            except Exception as e:
                b = str(e)
            res[va] = (b, name)

    return res
