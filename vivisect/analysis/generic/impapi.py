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

    logger.info("impapi.analyzeFunction(0x%x):   name: %r", fva, fname)
    api = vw.getImpApi(fname)
    if api == None:
        logger.debug("  === skipping!!")
        return

    logger.debug("   === applying")
    rettype,retname,callconv,callname,callargs = api
    callargs = [ callargs[i] if callargs[i][1] else (callargs[i][0],'arg%d' % i) for i in xrange(len(callargs)) ]

    vw.setFunctionApi(fva, (rettype,retname,callconv,callname,callargs))
    logger.debug("vw.setFunctionApi(0x%x, %r)", fva, (rettype,retname,callconv,callname,callargs))
