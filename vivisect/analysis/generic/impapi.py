"""
Function analysis module which sets function APIs based
on function's name matching impapi.  This should ideally go
early in the module order to get the APIs marked asap.
"""
import logging
logger = logging.getLogger(__name__)


def analyzeFunction(vw, fva):
    fname = vw.getName(fva)
    filename = vw.getFileByVa(fva)
    if fname.startswith(filename + "."):
        fname = fname[len(filename)+1:]

    api = vw.getImpApi(fname)
    if api is None:
        return

    rettype, retname, callconv, callname, callargs = api
    callargs = [callargs[i] if callargs[i][1] else (callargs[i][0], 'arg%d' % i) for i in range(len(callargs))]

    funcapi = (rettype, retname, callconv, callname, callargs)
    vw.setFunctionApi(fva, funcapi)
    logger.debug("vw.setFunctionApi(0x%x, %r)", fva, funcapi)
