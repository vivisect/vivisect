'''
The recon subsystem for monitoring well known library
calls and identifying dangerous calling mechanisms.

NOTE: This subsystem pretty much assumes some intel-like
conventions...

Recon Format Chars:
    A - A NULL terminated ascii string
    W - A NULL terminated utf-16le string
    P - A platform width pointer
    I - An integer (32 bits for now...)
'''

import logging

import vtrace.breakpoints as vt_breakpoints

logger = logging.getLogger(__name__)


def reprargs(trace, fmt, args):
    r = []
    for i in range(len(fmt)):
        arg = args[i]
        fchr = fmt[i]

        if fchr == 'P':
            sym = trace.getSymByAddr(arg)
            if sym is not None:
                rstr = repr(sym)
            else:
                rstr = '0x%.8x'

        elif fchr == 'I':
            rstr = repr(arg)

        elif fchr == 'U':

            if arg == 0:
                rstr = 'NULL'

            elif not trace.isValidPointer(arg):
                rstr = '0x%.8x' % arg

            else:
                buf = trace.readMemory(arg, 260*2)
                ubuf = buf.decode('utf-16le', 'ignore')
                rstr = repr(ubuf.split('\x00')[0])

        elif fchr == 'S':

            if arg == 0:
                rstr = 'NULL'

            elif not trace.isValidPointer(arg):
                rstr = '0x%.8x' % arg

            else:
                buf = trace.readMemory(arg, 260)
                rstr = repr(buf.split('\x00')[0])

        elif fchr == 'C':
            rstr = repr(chr(arg & 0xff))

        elif fchr == 'X':
            rstr = '0x%.8x' % arg

        else:
            raise Exception('Unknown Recon Format: %s' % fchr)

        r.append(rstr)
    return r


class ReconBreak(vt_breakpoints.Breakpoint):
    '''
    '''
    def __init__(self, symname, reconfmt):
        vt_breakpoints.Breakpoint.__init__(self, None, expression=symname)
        self.fastbreak = True  # We are a fast-break, don't notify the trace
        self._symname = symname
        self._reconfmt = reconfmt

    def getName(self):
        return '%s(%s)' % (self._symname, self._reconfmt)

    def notify(self, event, trace):
        thid = trace.getMeta('ThreadId')
        stackptr = trace.getStackCounter()

        rawargs = trace.readMemoryFormat(stackptr, '<%dP' % (len(self._reconfmt) + 1))
        savedeip = rawargs[0]
        args = rawargs[1:]

        recon_hits = trace.getMeta('recon_hits')

        argrep = reprargs(trace, self._reconfmt, args)
        recon_hits.append((thid, savedeip, self._symname, args, argrep))

        if not trace.getMeta('recon_quiet'):
            argstr = '(%s)' % ', '.join(argrep)
            logger.info('RECON: %.4d 0x%.8x %s%s', thid, savedeip, self._symname, argstr)


def addReconBreak(trace, symname, reconfmt):
    if trace.getMeta('recon_hits') is None:
        trace.setMeta('recon_hits', [])
    bp = ReconBreak(symname, reconfmt)
    bpid = trace.addBreakpoint(bp)
    return bpid


def clearReconHits(trace):
    '''
    Clear the current list of recon hits.
    '''
    trace.setMeta('recon_hits', [])


def getReconHits(trace):
    '''
    Get the list of recon "hits" entries.  Each hit entry is a tuple
    of (threadid, savedeip, symname, argtup, argreprtup).
    '''
    return trace.getMeta('recon_hits', [])
