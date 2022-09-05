'''
Some of the basic/universal memory renderers.
'''

import struct

import envi.common as e_common
import envi.memory as e_memory
import envi.memcanvas as e_canvas

class ByteRend(e_canvas.MemoryRenderer):

    __fmt_char__ = 'B'
    __pad__ = False

    def __init__(self, bigend=False):

        self.fmtbase = '<'
        if bigend:
            self.fmtbase = '>'

        self.width = struct.calcsize('%s%s' % (self.fmtbase, self.__fmt_char__))
        self.bformat = '%%.%dx' % (self.width * 2)
        self.pformat = '0x%s' % self.bformat

    def render(self, mcanv, va, numbytes=16):
        bytez = mcanv.mem.readMemory(va, numbytes)
        if self.__pad__:
            bytez = bytez.ljust(numbytes, b'\x00')

        mcanv.addVaText(self.pformat % va, va)
        mcanv.addText('  ')

        cnt = len(bytez) // self.width
        packfmt = self.fmtbase + (self.__fmt_char__ * cnt)
        for val in struct.unpack(packfmt, bytez):
            bstr = self.bformat % val
            if mcanv.mem.isValidPointer(val):
                mcanv.addVaText(bstr, val)
            else:
                mcanv.addNameText(bstr)

            mcanv.addText(' ')

        # add padding space for anything less than 16.
        # this only 'works' if your display font is monospaced.
        diff = numbytes - len(bytez)
        mcanv.addText(' ' * 3 * diff) # 2 hex chars + space
        mcanv.addText('  ')
        self.rendChars(mcanv, bytez)
        mcanv.addText('\n')

        return len(bytez)

class ShortRend(ByteRend):

    __fmt_char__ = 'H'
    __pad__ = True

class LongRend(ByteRend):

    __fmt_char__ = 'I'
    __pad__ = True

class QuadRend(ByteRend):
    __fmt_char__ = 'Q'
    __pad__ = True

def isAscii(bytez: bytes):
    bytez = bytez.split(b'\x00')[0]
    if len(bytez) < 4:
        return False, None
    for i in range(len(bytez)):
        o = bytez[i]
        if o < 0x20 or o > 0x7e:
            return False, None
    return True, bytez

def isBasicUnicode(bytez: bytes):
    bytez = bytez.split(b'\x00\x00')[0]
    if len(bytez) < 8:
        return False, None
    nonull = bytez.replace(b'\x00', b'')
    if (len(bytez) // 2) - 1 != len(nonull):
        return False, None
    return isAscii(nonull)

def getAsciiFormatted(bytez):
    is_ascii, bytez = isAscii(bytez)
    if bytez is not None:
        bytez = "'%s'" % bytez
    return bytez

def getBasicUnicodeFormatted(bytez):
    is_uni, bytez = isBasicUnicode(bytez)
    if bytez is not None:
        bytez = "u'%s'" % bytez
    return bytez

def getSymByAddrFormatted(trace, va):
    sym = trace.getSymByAddr(va, exact=False)
    if sym is not None:
        return '%s + %d' % (repr(sym), va-int(sym))
    return sym

def getFilenameFromFdFormatted(trace, va):
    for fd, ttype, bestname in trace.getFds():
        if fd == va:
            return 'HANDLE/FD?: %s' % bestname
    return None

class AutoBytesRenderer(e_canvas.MemoryRenderer):

    def __init__(self, maxrend=32, readsize=64):
        self.maxrend = maxrend
        self.readsize = readsize

    def render(self, mcanv, va):
        trace = mcanv.mem
        max_readable = trace.getMaxReadSize(va)
        if max_readable <= 0:
            return ''
        rsize = min(self.readsize, max_readable)
        bytez = trace.readMemory(va, rsize)

        prettyperm = ''
        mmap = trace.getMemoryMap(va)
        if mmap is not None:
            addr, size, perm, fname = mmap
            prettyperm = e_memory.reprPerms(perm)

        ascii_text = getAsciiFormatted(bytez)
        uni_text = getBasicUnicodeFormatted(bytez)
        sym = getSymByAddrFormatted(trace, va)
        fname = getFilenameFromFdFormatted(trace, va)

        desc = ''
        pdesc = (ascii_text, uni_text, sym, fname)
        items = [ppdesc for ppdesc in pdesc if ppdesc is not None]
        if len(items) == 1:
            desc = items[0]
        elif len(items) == 0:
            # if none match, just return the bytes.
            desc = e_common.hexify(bytez)
        elif len(items) > 1:
            # we only really expect one or none of these to match.
            desc = 'Error, multiple matches for this address!'
        else:
            raise Exception('should never get here')

        best_desc = '%s %s' % (prettyperm, desc)
        chopped_best_desc = best_desc[:self.maxrend]
        if len(best_desc) > len(chopped_best_desc):
            mcanv.addText(' %s...' % chopped_best_desc)
        else:
            mcanv.addText(' %s' % chopped_best_desc)

        return len(chopped_best_desc)
