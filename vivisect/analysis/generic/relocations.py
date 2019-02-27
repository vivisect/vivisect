"""
An analysis module which checks that all relocations *targets*
point to valid locations.
"""

import vivisect

def analyze(vw):
    for fname, vaoff, rtype, data in vw.getRelocations():
        if rtype == vivisect.RTYPE_BASERELOC and not vw.isLocation(va):
            vw.makePointer(va, follow=True)

        elif rtype == vivisect.RTYPE_BASEOFF:
            imgbase = vw.getFileMeta(fname, 'imagebase')
            va = imgbase + vaoff
            if not vw.isLocation(va):
                vw.makePointer(va, follow=True)
