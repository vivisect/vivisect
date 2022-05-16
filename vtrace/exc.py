'''
Various vtrace exceptions
'''
import ctypes


class PtraceException(Exception):
    def __init__(self, request):
        Exception.__init__(self, 'Ptrace raised exception on request %s (ERRNO: %d)' % (request, ctypes.get_errno()))
