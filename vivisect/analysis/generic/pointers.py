"""
generic workspace analysis module to seek through the undiscovered
country looking for pointers to interesting things.

in a previous life, this analysis code lived inside VivWorkspace.analyze()
"""


def analyze(vw):

    if vw.verbose:
        vw.vprint('...analyzing pointers.')

    # Now, lets find likely free-hanging pointers
    for addr, pval in vw.findPointers():
        if vw.isDeadData(pval):
            continue
        try:
            vw.followPointer(pval)
        except Exception:
            if vw.verbose:
                vw.vprint("followPointer() failed for 0x%.8x (pval: 0x%.8x)" % (addr, pval))
