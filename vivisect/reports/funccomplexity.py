
# Mnemonic distribution
# Reverse depth

columns = (
    ("Code Blocks",int),
    ("Mnem Dist", int),
)

def report(vw):

    ret = {}
    cbtot = {}
    mntot = {}
    for f in vw.getFunctions():
        fblocks = vw.getFunctionBlocks(f)
        cbtot[f] = len(fblocks)

    for f,c in list(cbtot.items()):
        mndist = vw.getFunctionMeta(f, "MnemDist", -1)
        ret[f] = (c,mndist)

    return ret

