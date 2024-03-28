'''
Home of the newer, cleaner iterators (yield based generators...)
'''
import envi
import vivisect


def iterOps(vw, va):
    '''
    Iterate over the virtual addresses of all the code blocks from the
    specified function downward...

    Example: for va in fscope.iterOps(vw, funcaddr):
    '''
    fva = vw.getFunction(va)
    fdone = {}
    todo = [fva, ]
    while len(todo):
        fva = todo.pop()
        if fdone.get(fva, False):
            continue
        fdone[fva] = True

        for cbva, cbsize, fva in vw.getFunctionBlocks(fva):

            cbend = cbva + cbsize
            while cbva < cbend:

                yield cbva

                # Go through the locations in this code block
                lva, lsize, ltype, linfo = vw.getLocation(cbva)
                for xrfrom, xrto, rtype, rflags in vw.getXrefsFrom(lva):
                    if rtype != vivisect.REF_CODE:
                        continue

                    # Skip non-procedural branches
                    if not rflags & envi.BR_PROC:
                        continue

                    # Skip dereference calls
                    if rflags & envi.BR_DEREF:
                        continue

                    # Procedural code branches w/o deref should always
                    # target other functions.
                    if not vw.isFunction(xrto):
                        continue

                    # Check if we've done this function before
                    if fdone.get(xrto):
                        continue

                    todo.append(xrto)

                # round and round!
                cbva += lsize


def getImportCalls(vw, va):
    '''
    Get all the import calls which happen from the given function
    and down....

    Example: for callva,impname in getImportCalls(vw, fva)
    '''

    ret = []
    for lva in iterOps(vw, va):

        for xrfrom, xrto, rtype, rflags in vw.getXrefsFrom(lva):
            if rtype != vivisect.REF_CODE:
                continue

            # Skip non-procedural branches
            if not rflags & envi.BR_PROC:
                continue

            # This may be an actual import call!
            if rflags & envi.BR_DEREF:
                loc = vw.getLocation(xrto)
                if loc is not None:
                    drva, drsize, drtype, drinfo = loc
                    if drtype == vivisect.LOC_IMPORT:
                        ret.append((lva, drinfo))
    return ret


def getStringRefs(vw, va):
    '''
    Get all of the immedates which point to string or unicode types
    in the workspace for this function scope. Returns a list of
    (refva, strva, strval) tuples.

    Example: for instrva, strva, strrepr in getStringRefs(vw, funcva)
    '''
    ret = []
    for lva in iterOps(vw, va):
        for xrfrom, xrto, rtype, rflags in vw.getXrefsFrom(lva):
            if rtype != vivisect.REF_PTR:
                continue

            ploc = vw.getLocation(xrto)
            if ploc is None:
                continue

            plva, plsize, pltype, plinfo = ploc
            if pltype == vivisect.LOC_STRING:
                r = vw.reprLocation(ploc)
                ret.append((lva, plva, r))
            elif pltype == vivisect.LOC_UNI:
                r = vw.reprLocation(ploc)
                ret.append((lva, plva, r))

    return ret
