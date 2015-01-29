
"""
A function analysis module to detect and properly mark
microsoft hotpatch pads...
"""

import vivisect

def analyzeFunction(vw, funcva):

    offset, bytes = vw.getByteDef(funcva)
    ob = ord(bytes[offset-1])
    if ob not in [0x90, 0xcc]:
        return

    count = 1
    newb = ord(bytes[offset-count])
    while newb == ob:
        count += 1
        newb = ord(bytes[offset-count])

    count -= 1

    va = funcva - count
    if count >= 5 and not vw.isLocation(va):
        vw.makePad(va, count)

