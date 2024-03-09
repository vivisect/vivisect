import logging
from binascii import unhexlify

logger = logging.getLogger(__name__)

thunk_lookup = {
    unhexlify('8b0424c3'): 'eax',
    unhexlify('8b0c24c3'): 'ecx',
    unhexlify('8b1424c3'): 'edx',
    unhexlify('8b1c24c3'): 'ebx',
    unhexlify('8b3424c3'): 'esi',
    unhexlify('8b3c24c3'): 'edi',
    unhexlify('8b2c24c3'): 'ebp',
}

def analyzeFunction(vw, fva):
    '''
    this analysis module will identify thunk_reg functions, which take the return value and place
    it into EBX.  this is done for position-independent code in i386 elf binaries.  a call to this
    function will be followed by an immediate add to find the start of the module.  that value is
    then used with fixed offsets to access resources within the binary.  it's a bit like the old
    shellcode trick.

    store funcva in "thunk_reg" VaSet in case we identify multiples (not likely) or misidentify
    something.

    then store the module base in metadata as "PIE_ebx", accessible by other analysis modules.
    '''
    sigbytes = vw.readMemory(fva, 4)
    sigreg = thunk_lookup.get(sigbytes)
    logger.debug("0x%x: sigreg: %r", fva, sigreg)

    if sigreg is not None:
        # have we already recorded this thunk_reg?
        if vw.getVaSetRow('thunk_reg', fva) is not None:
            logger.info("Not overriding thunk_reg 0x%x", fva)
            return

        # determine where reg ends up pointing to
        # this requires checking the calling function's next instruction
        refs = vw.getXrefsTo(fva)
        if refs is None or not len(refs):
            logger.info("No xrefs to thunk_reg 0x%x", fva)
            return

        va = refs[0][0]
        op = vw.parseOpcode(va)
        op2 = vw.parseOpcode(va + len(op))
        if op2.mnem != "add":
            logger.warning("Call to thunk_reg not followed by an add: %s", op2)
            return

        addt = op2.opers[1].getOperValue(op2)
        tgtval = op2.va + addt

        logger.debug("__x86.get_pc_thunk.%s: %s", sigreg[1:], hex(tgtval))
        curname = vw.getName(fva)
        if curname is None or curname == "sub_%.8x" % fva:
            vw.makeName(fva, "thunk_%s_%.8x" % (sigreg, fva))

        vw.setVaSetRow('thunk_reg', (fva, sigreg, tgtval))
