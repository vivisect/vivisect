"""
An analysis module which checks that all relocations *targets*
point to valid locations.
"""

import vivisect


def analyze(vw):
    for fname, vaoff, rtype, data in vw.getRelocations():
        imgbase = vw.getFileMeta(fname, 'imagebase')
        if rtype == vivisect.RTYPE_BASERELOC and not vw.isLocation(vaoff):
            vw.makePointer(imgbase + vaoff, follow=True)

        elif rtype == vivisect.RTYPE_BASEOFF:
            va = imgbase + vaoff
            if not vw.isLocation(va):
                vw.makePointer(va, follow=True)
