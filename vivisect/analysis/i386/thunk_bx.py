import vivisect

thunk_bx_sig = '8b1c24c3'.decode('hex')
def analyzeFunction(vw, fva):
    '''
    '''
    if vw.readMemory(fva, 4) == thunk_bx_sig:
        if not 'thunk_bx' in vw.getVaSetNames():
            vw.addVaSet('thunk_bx', ( ('fva', vivisect.VASET_ADDRESS), ) )
            
        # have we already recorded this thunk_bx?
        for afva, in vw.getVaSetRows('thunk_bx'):
            if fva == afva:
                if vw.verbose: print "ditching thunk_bx: %s"
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
            if vw.verbose: print "call to thunk_bx not followed by an add: %s" % op2
            return
        
        addt = op2.opers[1].getOperValue(op2)
        ebx = op2.va + addt
        if vw.getMeta('PIE_ebx') != None:
            return

        if vw.verbose: print "__x86.get_pc_thunk.bx:  ", hex(ebx)
        vw.setMeta('PIE_ebx', ebx)
