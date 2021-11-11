# Mnemonic distribution
# Reverse depth

columns = (
    ("Function", str),
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
        funcstr = "0x%x (%r)" % (f, vw.getName(f))
        mndist = vw.getFunctionMeta(f, "MnemDist", -1)
        ret[f] = (funcstr, c, mndist)

    return ret
