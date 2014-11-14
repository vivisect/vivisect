import envi.archs.i386.opcode86 as e_opcode86
def analyze(vw):

    for fva in vw.getFunctions():
        fname =vw.getName(fva)
        # XXX - get func by name 
        # find the security_check_cookie function
        if fname.startswith('security_check_cookie'):
            # parse teh first opcode in the function
            op = vw.parseOpcode(fva)
            if len(op.opers) != 2:
                return 

            gscookie = None
            if op.opers[1].isDeref():
                # get the address of the cookie
                gscookie  = op.opers[1].getOperAddr(op, None)

            if not gscookie:
                return
            
            # iterate over all references to the cookie
            for fromva, tova, rtype, rflags in vw.getXrefsTo(gscookie):
                op = vw.parseOpcode(fromva)
                cb = vw.getCodeBlock(fromva) 
                if not cb:
                    continue

                va, cbsize, funcva = cb 
                # if the start of the code block containing a reference to the gs cookie location isn't a  function then we need to make it
                # XXX - do we want to hard code mov or use a flag?? If so which flag? 
                if not vw.isFunction(va) and op.mnem == 'mov':
                    vw.makeFunction(va)

