"""
Function analysis module which sets function APIs based
on function's name matching impapi.  This should ideally go
early in the module order to get the APIs marked asap.
"""
def analyzeFunction(vw, fva):
    fname = vw.getName(fva)
    api = vw.getImpApi(fname)
    if api == None:
        return

    rettype,retname,callconv,callname,callargs = api
    callargs = [ callargs[i] if callargs[i][1] else (callargs[i][0],'arg%d' % i) for i in xrange(len(callargs)) ]

    vw.setFunctionApi(fva, (rettype,retname,callconv,callname,callargs))

