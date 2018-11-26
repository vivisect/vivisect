# this analysis module is for blobs and ihex files, and attempts to identify boot information as understood by a Boot Assist Module (BAM) found in many of the modern PPC/VLE processors.
# for reference, this module uses information from the "MPC5674F Microcontroller Reference Manual, rev 7" from NXP.
# we won't mimic the behavior exactly, but rather use BAM information to identify entry points


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
    if vw.verbose: vw.vprint('...analyzing PowerPC Entry Points.')

    # add the PPC architecture structures to the namespace
    vw.addStructureModule('ppc', 'vstruct.defs.ppc')

    # from NXP MPC5674
    for baseaddr in 0x0000, 0x4000, 0x10000, 0x1C000, 0x20000, 0x30000:
        # look for an RCHW structure
        rchw = vw.readMemValue(baseaddr, 2)
        # the top 4 bits are reserved (expected to be 0) and the last 8 bits are 01011010
        if rchw & 0xf0ff != 0x5a:
            continue

        # make the structure
        rchw = vw.makeStructure(baseaddr, 'ppc.RCHW')

        # now wrap in the pointer to the entry point and make it a function
        eva = rchw.entry_point
        vw.addEntryPoint(eva)
        vw.makeFunction(eva)
        vw.makeName(eva, 'ENTRY_%.8x' % eva)
