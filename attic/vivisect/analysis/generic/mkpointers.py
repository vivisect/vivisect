"""
generic workspace analysis module to seek through the undiscovered 
country looking for pointers to interesting things.

in a previous life, this analysis code lived inside VivWorkspace.analyze()
This will *actually* make pointers!
"""
def analyze(vw):

    if vw.verbose: vw.vprint('...analyzing pointers.')

    # Now, lets find likely free-hanging pointers
    for addr, pval in vw.findPointers():
        try:
            vw.followPointer(pval)
            if vw.getLocation(addr) == None:
                # RP we need to make pointers out of what we find... 
                # otherwise we miss a ton of functions because we mark sections exec when subsystem < win7
                vw.makePointer(addr)
        except Exception, e:
            if vw.verbose: vw.vprint("followPointer() failed for 0x%.8x (pval: 0x%.8x)" % (addr,pval))

