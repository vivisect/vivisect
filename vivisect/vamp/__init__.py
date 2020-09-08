
"""
Vamp is a function/codeblock signaturing framework which is
a subcomponent of vivisect.  These may be used to import/export
signature sets and potentially identify code reuse or static
linking...

Current signature ideas:
    function arg count
    code block count
    globals refs
    code block refs
    unusual instruction use
    odd immediates
    import calls
    other signature calls
    certianty index
    Exception handling

    There will be function characteristics and code-block
    characteristics...

NOTE: Initial signature code consists entirely of the envi
bytesig module and byte/mask sets for known function signatures.
"""


class Signature:
    """
    A function/procedure signature.
    """
    pass

from vivisect.const import *

def genSigAndMask(vw, funcva):

    """
    Generate an envi bytesig signature and mask for the given
    function block.  This will properly mask off relocations
    if present.
    """

    fsize = 0
    if funcva not in vw.getFunctions():
        funcva = vw.getFunction(funcva)
        if funcva is None:
            raise Exception('Given funcva not a function or within a known function')
    func_blocks = [cbva for cbva, _, _ in vw.getFunctionBlocks(funcva)]
    # Figure out the size of the first linear chunk
    # in this function...
    cb = vw.getCodeBlock(funcva)
    if cb[CB_VA] not in func_blocks:
        raise Exception("funcva not in given func")
    while cb is not None:
        cbva, cbsize, cbfunc = cb
        if cbfunc != funcva:
            break
        fsize += cbsize
        cb = vw.getCodeBlock(cbva+cbsize)

    if fsize == 0:
        raise Exception("0 length function??!?1")

    bytez = vw.readMemory(funcva, fsize)

    sig = ""
    mask = ""
    i = 0
    while i < fsize:
        rtype = vw.getRelocation(funcva + i)
        if rtype is None:
            sig += bytez[i]
            mask += "\xff"
            i += 1
        elif rtype == RTYPE_BASERELOC:
            x = "\x00" * vw.psize
            sig += x
            mask += x
            i += vw.psize
        else:
            raise Exception("Unhandled Reloc Type: %d" % rtype)

    return sig, mask
