'''
'''
import sys
import struct

from io import StringIO
from itertools import cycle

import PE


def xorbytes(data: bytearray, key: bytearray) -> bytearray:
    return b''.join((x ^ y) & 0xff for (x, y) in zip(data, cycle(key)))


def xorstatic(data: bytearray, xval) -> bytearray:
    return bytearray([(c ^ xval) & 0xff for c in data])


mz_xor = [(xorstatic(b'MZ', i), xorstatic(b'PE', i), i) for i in range(0xff)]


def carve(pbytes, offset=0):
    '''
    Return a list of (offset, size, xor) tuples of embedded PEs
    '''
    pblen = len(pbytes)
    todo = [(pbytes.find(mzx, offset), mzx, pex, i) for mzx, pex, i in mz_xor]
    todo = [(off, mzx, pex, i) for (off, mzx, pex, i) in todo if off != -1]

    while len(todo):

        off, mzx, pex, i = todo.pop()

        # The MZ header has one field we will check
        # e_lfanew is at 0x3c
        e_lfanew = off + 0x3c
        if pblen < (e_lfanew + 4):
            continue

        newoff = struct.unpack('<I', xorstatic(pbytes[e_lfanew: e_lfanew + 4], i))[0]

        peoff = off + newoff
        if pblen < (peoff + 2):
            continue

        if pbytes[peoff: peoff + 2] == pex:
            yield (off, i)

        nextres = pbytes.find(mzx, off + 1)
        if nextres != -1:
            todo.append((nextres, mzx, pex, i))


class CarvedPE(PE.PE):
    def __init__(self, fbytes, offset, xkey):
        self.carved_offset = offset
        self.fbytes = fbytes
        self.xorkey = xkey
        PE.PE.__init__(self, StringIO())

    def readAtOffset(self, offset, size):
        offset += self.carved_offset
        return xorbytes(self.fbytes[offset:offset + size], self.xorkey)

    def getFileSize(self):
        ret = 0
        for sec in self.getSections():
            ret = max(ret, sec.PointerToRawData + sec.SizeOfRawData)
        return ret


if __name__ == '__main__':

    fbytes = open(sys.argv[1], 'rb').read()
    for offset, i in carve(fbytes):
        print('OFFSET: %d (xor: %d)' % (offset, i))
        p = CarvedPE(fbytes, offset, chr(i))
        print('SIZE', p.getFileSize())
