# This analysis module initializes the initial PPC MMU entries which are
# required for some of the embedded/bare-metal analysis in other analysis
# modules
#
# For reference, this module uses information from the following reference
# manuals:
#   - "MPC5674F Microcontroller Reference Manual, rev 7" from NXP
#   - "MPC5646C Microcontroller Reference Manual, rev. 5" from NXP
#   - "MPC5777C Microcontroller Reference Manual, rev. 8" from NXP
#
import logging
logger = logging.getLogger(__name__)

import vivisect.exc as viv_exc
import vivisect.const as viv_const


# Default memory maps as defined by the boot assist module (BAM).
DEFAULT_PPC_PAGES = {
    0: [0xFFE00000, 0x00200000, False],
    1: [0x00000000, 0x20000000, False],
    2: [0x20000000, 0x20000000, False],
    3: [0x40000000, 0x00080000, False],
    4: [0xC3E00000, 0x00200000, False],
}

DEFAULT_PPC_PAGES_VLE = {
    0: [0xFFE00000, 0x00200000, False],
    1: [0x00000000, 0x20000000, True],
    2: [0x20000000, 0x20000000, True],
    3: [0x40000000, 0x00080000, True],
    4: [0xC3E00000, 0x00200000, False],
}


def analyze(vw):
    # Add in the initial MMU entries manually from the vivisect configuration
    # options, or initialize a probably accurate enough default memory map
    vle_pages = vw.config.viv.arch.ppc.vle_pages
    if vle_pages:
        if isinstance(vle_pages, (list, tuple)):
            maps = {}
            for idx, entry in enumerate(vle_pages):
                if entry is None:
                    # Allow Null/None entries to make it easy to mimic the MMU
                    # table settings from real firmware
                    continue
                elif len(entry) == 2:
                    base, size = entry
                    name = str(idx)
                    vle = True
                elif len(entry) == 3:
                    base, size = entry[:2]
                    vle = bool(entry[2])
                else:
                    logger.error('Invalid format for PPC VLE page %d: %r', entry)
                    continue

                logger.debug('Adding initial PPC VLE pages %d: 0x%x - 0x%x (%s)', base, base+size, vle)
                maps[idx] = [base, size, vle]
            vw.setMeta('PpcVlePages', maps)
        else:
            logger.error('Invalid format for PPC VLE Pages config: %r', vle_pages)
            logger.error('PPC VLE Pages config must be have format of: (([name,] <baseaddr>, <size>, [True/False]), ...)')
    else:
        logger.debug('Setting default PPC VLE Pages')
        vw.setMeta('PpcVlePages', DEFAULT_PPC_PAGES)
