# This analysis module is for blobs and ihex files, and attempts to identify
# boot information as understood by a Boot Assist Module (BAM) found in many of
# the modern PPC/VLE processors.
#
# For reference, this module uses information from the following reference
# manuals:
#   - "MPC5674F Microcontroller Reference Manual, rev 7" from NXP
#   - "MPC5646C Microcontroller Reference Manual, rev. 5" from NXP
#   - "MPC5777C Microcontroller Reference Manual, rev. 8" from NXP
#
# We won't mimic the behavior exactly, but rather use BAM information to
# identify entry points
import logging
logger = logging.getLogger(__name__)


from vivisect.analysis.ppc.vlepages import DEFAULT_PPC_PAGES, DEFAULT_PPC_PAGES_VLE


def set_rchw_vle(vw):
    # If a VLE page configuration was specified manually, don't override it.
    vle_pages = vw.getMeta('PpcVlePages')
    if vle_pages is DEFAULT_PPC_PAGES
        # If the VLE pages are still the default pages, update entries 1, 2,
        # and 3 (Flash, EBI, SRAM) to be VLE.
        vw.setMeta('PpcVlePages', DEFAULT_PPC_PAGES_VLE)


def analyze(vw):
    logger.info('...analyzing PowerPC Entry Points.')

    bootentries = []
    # The default PowerPC RCHW address list includes the default RCHW addresses
    # for the MPC5674F and MPC5777C processors.
    rchwaddrs = vw.config.viv.arch.ppc.bootstrap.rchwaddrs
    for baseaddr in rchwaddrs:
        try:
            # look for an RCHW structure
            rchw = vw.readMemValue(baseaddr, 2)

            logger.info("analyzing: 0x%x : 0x%x" % (baseaddr, rchw))
            # the top 4 bits are reserved (expected to be 0) and the last 8 bits
            # are 01011010
            if rchw & 0xf0ff != 0x5a:
                continue

            # make the structure
            rchw = vw.makeStructure(baseaddr, 'ppc.RCHW')

            # now wrap in the pointer to the entry point and make it a function
            eva = rchw.entry_point

            # Check if the boot entry should be VLE
            if rchw.flags & 0x01:
                set_rchw_vle(vw)

            # Now that the VLE/not VLE flag is sorted out, try adding the
            # initial entry point
            vw.addEntryPoint(eva)
            vw.makeName(eva, 'ENTRY_%.8x' % eva)
            bootentries.append((baseaddr, eva, rchw))

        except Exception as e:
            logger.info("Bootstrap analysis failed for address 0x%x: %r", baseaddr, e)

    return bootentries
