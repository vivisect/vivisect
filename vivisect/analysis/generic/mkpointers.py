"""
generic workspace analysis module to seek through the undiscovered
country looking for pointers to interesting things.

in a previous life, this analysis code lived inside VivWorkspace.analyze()
This will *actually* make pointers!
"""
import logging
logger = logging.getLogger(__name__)


def analyze(vw):

    logger.debug('...analyzing pointers.')

    # Now, lets find likely free-hanging pointers
    for addr, pval in vw.findPointers():
        try:
            vw.followPointer(pval)
            if vw.getLocation(addr) is None:
                # RP we need to make pointers out of what we find...
                # otherwise we miss a ton of functions because we mark sections exec
                # when subsystem < win7
                vw.makePointer(addr)
        except Exception as e:
            logger.warning("followPointer() failed for 0x%.8x (pval: 0x%.8x) (Error: %s)", addr, pval, e)
