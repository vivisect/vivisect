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

def analyze(vw):
    # For bare metal/embedded targets SPR reads and writes are important to
    # track.
    try:
        vaset = vw.getVaSet("ppc_spr_reads")
    except viv_exc.InvalidVaSet:
        vw.addVaSet("ppc_spr_reads", (("funcva", viv_const.VASET_ADDRESS), ("reads", viv_const.VASET_COMPLEX)))

    try:
        vaset = vw.getVaSet("ppc_spr_writes")
    except viv_exc.InvalidVaSet:
        vw.addVaSet("ppc_spr_writes", (("funcva", viv_const.VASET_ADDRESS), ("writes", viv_const.VASET_COMPLEX)))

    # Add in the initial MMU entries manually from the vivisect configuration
    # options, or initialize a probably accurate enough default memory map
    mmu_entries = vw.config.viv.arch.ppc.mmu
    if mmu_entries:
        if isinstance(mmu_entries, (list, tuple)):
            maps = {}
            for idx, entry in enumerate(mmu_entries):
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
                    logger.error('Invalid format for MMU entry %d: %r', entry)
                    continue

                logger.debug('Adding initial PPC Memory Map entry %d: 0x%x - 0x%x (%s)', base, base+size, vle)
                maps[idx] = [base, size, vle]
            vw.setMeta('PpcMemoryMaps', maps)
        else:
            logger.error('Invalid format for PPC MMU config: %r', mmu_entries)
            logger.error('PPC MMU config must be have format of: (([name,] <baseaddr>, <size>, [True/False]), ...)')
    else:
        maps = {
            0: [0xFFE00000, 0x00200000, False],
            1: [0x00000000, 0x20000000, False],
            2: [0x20000000, 0x40000000, False],
            3: [0x40000000, 0x00080000, False],
            4: [0xC3E00000, 0x00200000, False],
        }
        logger.debug('Setting default PPC Memory Map entries')
        vw.setMeta('PpcMemoryMaps', maps)
