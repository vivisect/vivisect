# Mnemonic distribution
# Reverse depth

columns = (
    ("Code Blocks", int),
    ("Mnem Dist", int),
)


def report(vw):
    ret = {}
    cbtot = {}
    for f in vw.getFunctions():
        fblocks = vw.getFunctionBlocks(f)
        cbtot[f] = len(fblocks)

    for f, c in cbtot.items():
        mndist = vw.getFunctionMeta(f, "MnemDist", -1)
        ret[f] = (c, mndist)

    return ret
