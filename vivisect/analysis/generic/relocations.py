"""
An analysis module which checks that all relocations *targets*
point to valid locations.
"""

import vivisect

def analyze(vw):
    for va, rtype in vw.getRelocations():
        if rtype == vivisect.RTYPE_BASERELOC and not vw.isLocation(va):
            vw.makePointer(va, follow=True)
