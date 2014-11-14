'''
Utilities for windows tracer objects.
'''
import PE
import vtrace
import envi.bits as e_bits

def deAslr(trace, va):
    '''
    Given an address in an ASLR'd library, rebase
    it back to the address as it would be if the
    given PE were at it's suggested address...
    '''

    if vtrace.remote:
        raise Exception('deAslr only works for local debuggers!')

    map = trace.getMemoryMap(va)
    if map == None:
        return va

    mapva, mapsize, mapperm, mapfname = map
    if not mapfname:
        return va

    normname = trace.normFileName(mapfname)
    sym = trace.getSymByName(normname)
    if sym == None:
        return va

    membase = long(sym)

    pe = PE.peFromFileName(mapfname)
    filebase = pe.IMAGE_NT_HEADERS.OptionalHeader.ImageBase

    rva = va - membase

    return filebase + rva


