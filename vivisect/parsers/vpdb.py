import math

import vstruct.defs.vpdb as v_d_pdb

from vstruct.primitives import v_uint32

class PDB:
    def __init__(self, byts):
        self.byts = byts
        self.superblock = v_d_pdb.SuperBlock()
        self.superblock.vsParse(byts)

        self.streamdir = self.getStreamDir()

    def getStreamDir(self):
        '''
        The stream directory is not guaranteed to fit in a single block
        so an MSF adds a layer of indirection per the blockMapAddr field.

        We use that to stitch together enough bytes to construct the
        StreamDirectory.
        '''
        block = self.getBlockByIdx(self.superblock.blockMapAddr)
        if not block:
            return []

        valus = []
        offset = 0
        numBlocks = math.ceil(self.superblock.numDirBytes / self.superblock.blockSize)

        for i in range(numBlocks):
            valu = v_uint32(bigend=False)
            valu.vsParse(block[offset:offset+4])
            offset += 4
            if valu == 0:
                continue
            valus.append(valu.vsGetValue())

        # get the byts needed to stitch together what's needed for the stream directory
        byts = b''
        for idx in valus:
            block = self.getBlockByIdx(idx)
            if block:
                byts += block

        sdir = v_d_pdb.StreamDirectory(int(self.superblock.blockSize))
        sdir.vsParse(byts)

        return sdir

    def getBlockByIdx(self, idx):
        bsize = self.superblock.blockSize
        offset = idx * bsize
        if offset < len(self.byts):
            return self.byts[offset:offset+bsize]
        return None

    def getStreamByIdx(self):
        pass

if __name__ == '__main__':
    with open('C:\\Users\\James\\Documents\\Visual Studio 2015\\Projects\\raytracing\\Debug\\raytracing.pdb', 'rb') as fd:
        byts = fd.read()
    obj = PDB(byts)
    breakpoint()
    print('wat')