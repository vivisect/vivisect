"""
An analysis module which checks that all relocations *targets*
point to valid locations.
"""

import vivisect.const as v_const


def analyze(vw):
    for fname, vaoff, rtype, data in vw.getRelocations():
        imgbase = vw.getFileMeta(fname, 'imagebase')
        va = imgbase + vaoff
        if rtype == v_const.RTYPE_BASERELOC and not vw.isLocation(va):
            vw.makePointer(va, follow=True)

        elif rtype == v_const.RTYPE_BASEOFF:
            if not vw.isLocation(va):
                vw.makePointer(va, follow=True)
