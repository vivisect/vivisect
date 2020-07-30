
"""
An emulation module to detect SEH setup and apply structs where possible.
"""

import vivisect.vamp.msvc as v_msvc

vs = v_msvc.VisualStudioVamp()


def analyzeFunction(vw, funcva):

    offset, bytes = vw.getByteDef(funcva)
    sig = vs.getSignature(bytes, offset)
    if sig is not None:
        fname = sig.split(".")[-1]
        vw.makeName(funcva, "%s_%.8x" % (fname, funcva), filelocal=True)
        vw.makeFunctionThunk(funcva, sig)
