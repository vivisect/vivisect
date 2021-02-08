# this analysis module is for blobs and ihex files, and attempts to identify boot information as understood by a Boot Assist Module (BAM) found in many of the modern PPC/VLE processors.
# for reference, this module uses information from the "MPC5674F Microcontroller Reference Manual, rev 7" from NXP, as well as "MPC5646C Microcontroller Reference Manual, rev. 5".
# we won't mimic the behavior exactly, but rather use BAM information to identify entry points
import logging
logger = logging.getLogger(__name__)

MEM_BAM_PERIPH_B    = 0xfff00000
MSZ_BAM_PERIPH_B    = 0x00100000
MEM_INTERNAL_FLASH  = 0x00000000
MSZ_INTERNAL_FLASH  = 0x01000000
MEM_EBI             = 0x20000000
MSZ_EBI             = 0x01000000
MEM_INTERNAL_SRAM   = 0x40000000
MSZ_INTERNAL_SRAM   = 0x00040000
MEM_PERIPH_BRIDGEA  = 0xC3F00000
MSZ_PERIPH_BRIDGEA  = 0x00100000


def analyze(vw):
    # TODO:  Boot Config 0, 1, 2, 3
    if logger.getEffectiveLevel() < 40: vw.vprint('...analyzing PowerPC Entry Points.')
    logger.info('...analyzing PowerPC Entry Points.')
    print('...analyzing PowerPC Entry Points.')

    # add the PPC architecture structures to the namespace
    vw.addStructureModule('ppc', 'vstruct.defs.ppc')

    # from NXP MPC5674
    bootentries = []
    for baseaddr in 0x0000, 0x4000, 0x8000, 0x10000, 0x18000, 0x1C000, 0x20000, 0x30000:
        try:
            # look for an RCHW structure
            rchw = vw.readMemValue(baseaddr, 2)
            
            if logger.getEffectiveLevel() < 40: vw.vprint("analyzing: 0x%x : 0x%x" % (baseaddr, rchw))
            logger.info("analyzing: 0x%x : 0x%x" % (baseaddr, rchw))
            print("analyzing: 0x%x : 0x%x" % (baseaddr, rchw))
            # the top 4 bits are reserved (expected to be 0) and the last 8 bits are 01011010
            if rchw & 0xf0ff != 0x5a:
                continue

            # make the structure
            rchw = vw.makeStructure(baseaddr, 'ppc.RCHW')

            # now wrap in the pointer to the entry point and make it a function
            eva = rchw.entry_point
            vw.addEntryPoint(eva)
            vw.makeName(eva, 'ENTRY_%.8x' % eva)
            bootentries.append((baseaddr, eva, rchw))
        except Exception as  e:
            vw.vprint(" Bootstrap analysis failed for address 0x%x: %r" % (baseaddr, e))
            logger.info(" Bootstrap analysis failed for address 0x%x: %r" % (baseaddr, e))
            print(" Bootstrap analysis failed for address 0x%x: %r" % (baseaddr, e))
            print(vw.getMemoryMaps())

    return bootentries
