"""
Use the generic "signature" tree in the workspace to brute
force attempt to find function entry points.  This is
slightly desperate, so do it late when most locations are
already defined...  Additionally, if the "pointers" generic
module is run first, there is a reasonabily high likelyhood
that the code this finds is dead...
"""
import logging
import traceback

import envi.exc as e_exc
import envi.const as e_const

import vivisect.exc as v_exc
import vivisect.const as v_const

logger = logging.getLogger(__name__)


def analyze(vw):
    """
    Assuming that a bunch of functions have already been defined and
    fully analyzed, use the compiler against itself and attempt to
    brute force find other function entry points based on the
    entry signatures db.
    """
    # FIXME make the below code an undefined space iterator
    # and use in findPointers too
    for mapva, mapsize, mapflags, fname in vw.getMemoryMaps():

        # Segment permissions check for likely code stuff at all
        if not mapflags & e_const.MM_EXEC:
            continue
        if mapflags & e_const.MM_UNINIT:
            continue

        i = 0
        maxsize = mapsize - 4
        while i < maxsize:
            va = mapva + i
            loctup = vw.getLocation(va)
            if loctup is not None:
                i += loctup[v_const.L_SIZE]
                continue

            i += 1

            try:

                if vw.isFunctionSignature(va):
                    logger.debug('discovered new function (by signature): 0x%x', va)
                    vw.makeFunction(va)

            except v_exc.InvalidLocation as msg:
                logger.error("InvalidLocation: %s", msg)
            except e_exc.InvalidInstruction:
                continue
            except e_exc.EnviException as msg:
                logger.error("%s: %s" % (msg.__class__.__name__, msg))
            except Exception:
                logger.error(traceback.format_exc())
                continue
