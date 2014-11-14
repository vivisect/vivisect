"""
An analysis module which checks that all relocations *targets*
point to valid locations.
"""

import vivisect

def analyze(vw):
    for va, rtype in vw.getRelocations():
        if rtype == vivisect.RTYPE_BASERELOC:
            ptr = vw.castPointer(va)
            if vw.isValidPointer(ptr):
                loc = vw.getLocation(ptr)
                if loc == None:
                    vw.followPointer(ptr)

