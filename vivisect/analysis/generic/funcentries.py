"""
Use the generic "signature" tree in the workspace to brute
force attempt to find function entry points.  This is 
slightly desperate, so do it late when most locations are
already defined...  Additionally, if the "pointers" generic
module is run first, there is a reasonabily high likelyhood
that the code this finds is dead...
"""
import traceback

import envi
import envi.memory as e_mem
import vivisect

def analyze(vw):
    """
    Assuming that a bunch of functions have already been defined and
    fully analyzed, use the compiler against itself and attempt to
    brute force find other function entry points based on the
    entry signatures db.
    """
    # FIXME make the below code an undefined space iterator
    # and use in findPointers too
    for mapva,mapsize,mapflags,fname in vw.getMemoryMaps():

        # Segment permissions check for likely code stuff at all
        if not mapflags & e_mem.MM_EXEC:
            continue

        i = 0
        maxsize = mapsize - 4
        while i < maxsize:
            va = mapva + i
            loctup = vw.getLocation(va)
            if loctup != None:
                i += loctup[vivisect.L_SIZE]
                continue

            i+=1

            try:

                if vw.isFunctionSignature(va):
                    #print "MATCH MATCH MATCH: 0x%.8x" % va
                    vw.makeFunction(va)

            except vivisect.InvalidLocation, msg:
                if vw.verbose: vw.vprint("InvalidLocation: %s" % msg)
            except envi.InvalidInstruction, e:
                continue
            except envi.EnviException, msg:
                if vw.verbose: vw.vprint("%s: %s" % (msg.__class__.__name__,msg))
            except Exception, msg:
                traceback.print_exc()
                continue

