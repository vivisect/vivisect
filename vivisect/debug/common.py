
class VivDebugError(Exception): pass
class NoSuchProcess(VivDebugError): pass

# Some pre-defined "run until" callbacks for use in trace.run()

def forever(trace):
    '''
    run(until=forever) - run trace until exit
    '''
    return False

def tilsig(code):
    '''
    run(until=tilsig(code)) - run trace until signal code
    '''
    def sigfunc(trace):
        return trace.getTraceInfo('signo') == code

    return sigfunc

def tillib(name):
    '''
    trace.run(until=tillib(name))  - run trace until lib <name> loads
    '''
    def libfunc(trace):
        return trace.lib(name) != None
    return libfunc

