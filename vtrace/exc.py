'''
Various vtrace exceptions
'''
import ctypes


class PtraceException(Exception):
    def __init__(self, request):
        Exception.__init__(self, 'Ptrace raised exception on request %s (ERRNO: %d)' % (request, ctypes.get_errno()))

class RegisterException(Exception):
    def __init__(self, msg, emuregs, traceregs):
        Exception.__init__(self, msg)
        self.emuregs = emuregs
        self.traceregs = traceregs

class MemoryException(Exception):
    pass

class TargetAddrCalcException(Exception):
    pass

