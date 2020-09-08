import logging

import envi.bits as e_bits

logger = logging.getLogger(__name__)


def ffTermFptrArray(vw, va, max=100):
    ret = []
    ffterm = e_bits.u_maxes[vw.psize]
    for i in range(max):

        vw.makeNumber(va, vw.psize)

        val = vw.parseNumber(va, vw.psize)
        if val == ffterm:
            return ret

        try:
            logger.debug('ffTermFptrArray(): discovered new function: 0x%x', val)
            vw.makeFunction(val)
            ret.append(val)
        except Exception as e:
            logger.warning("FIXME (ffTermFptrArray): %s", e)
        va += vw.psize
    return ret


def analyze(vw):

    # Go through the elf sections and handle known types.
    for segva, segsize, segname, segfname in vw.getSegments():
        if segname == ".ctors":
            if vw.getLocation(segva) is not None:  # Check if it's already done
                continue
            for f in ffTermFptrArray(vw, segva):
                vw.makeName(f, "ctor_%.8x" % f)

        elif segname == ".dtors":
            if vw.getLocation(segva) is not None:  # Check if it's already done
                continue
            for f in ffTermFptrArray(vw, segva):
                vw.makeName(f, "dtor_%.8x" % f)

        elif segname == ".plt":
            pass
            # FIXME: Do linear disassembly of the PLT here...
