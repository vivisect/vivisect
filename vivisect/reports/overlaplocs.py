"""Locate locations which overlap"""
from vivisect.const import *


columns = (
    ("Overlap Size",   int),
    ("This Location",  str),
    ("Other Location", str),
)


def report(vw):
    res = {}
    for i in range(LOC_MAX):
        for lva, size, ltype, tinfo in vw.getLocations(i):
            va = lva + 1
            maxva = lva + size
            while va < maxva:
                othr = vw.getLocation(va, range=True)
                if othr is not None:
                    if lva != othr[0]:
                        res[lva] = (va-lva, vw.reprLocation((lva, size, ltype, tinfo)), vw.reprLocation(othr))
                va += 1
    return res
