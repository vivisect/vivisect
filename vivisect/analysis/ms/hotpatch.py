"""
A function analysis module to detect and properly mark
microsoft hotpatch pads...
"""


def analyzeFunction(vw, funcva):

    offset, bytez = vw.getByteDef(funcva)
    ob = bytez[offset-1]
    if ob not in [0x90, 0xcc]:
        return

    count = 1
    newb = bytez[offset-count]
    while newb == ob:
        count += 1
        newb = bytez[offset-count]

    count -= 1

    va = funcva - count
    if count >= 5 and not vw.isLocation(va):
        vw.makePad(va, count)
