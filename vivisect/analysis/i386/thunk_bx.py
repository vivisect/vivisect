import vivisect

thunk_bx_sig = '8b1c24c3'.decode('hex')
def analyzeFunction(vw, fva):
    '''
    this analysis module will identify thunk_bx functions, which take the return value and place 
    it into EBX.  this is done for position-independent code in i386 elf binaries.  a call to this
    function will be followed by an immediate add to find the start of the module.  that value is
    then used with fixed offsets to access resources within the binary.  it's a bit like the old
    shellcode trick.

    store funcva in "thunk_bx" VaSet in case we identify multiples (not likely) or misidentify 
    something.

    then store the module base in metadata as "PIE_ebx", accessible by other analysis modules.
    '''
    if vw.readMemory(fva, 4) == thunk_bx_sig:

        # have we already recorded this thunk_bx?
        if vw.getVaSetRow('thunk_bx', fva) != None:
            if vw.verbose: print("ditching thunk_bx: %s")
            return
        
        vw.setVaSetRow('thunk_bx', (fva,))


        # determine where ebx ends up pointing to
        # this requires checking the calling function's next instruction
        refs = vw.getXrefsTo(fva)
        if refs == None or not len(refs):
            return

        va = refs[0][0]
        op = vw.parseOpcode(va)
        op2 = vw.parseOpcode(va + len(op))
        if op2.mnem != "add":
            if vw.verbose: print("call to thunk_bx not followed by an add: %s" % op2)
            return
        
        addt = op2.opers[1].getOperValue(op2)
        ebx = op2.va + addt
        if vw.getMeta('PIE_ebx') != None:
            return

        if vw.verbose: print("__x86.get_pc_thunk.bx:  ", hex(ebx))
        curname = vw.getName(fva)
        if curname == None or curname == "sub_%.8x"%fva:
            vw.makeName(fva, "thunk_bx_%.8x"%fva)

        vw.setMeta('PIE_ebx', ebx)
