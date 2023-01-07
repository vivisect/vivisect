import vstruct.defs.vpdb as v_d_pdb

from vstruct.primitives import v_uint32

class PDB:
    def __init__(self, byts):
        self.byts = byts
        self.superblock = v_d_pdb.SuperBlock()
        self.superblock.vsParse(byts)

        self.streamsdirs = self.getStreamDirs()

    def getStreamDirs(self):
        '''
        The stream directory is not guaranteed to fit in a single block
        so an MSF adds a layer of indirection.
        '''
        block = self.getBlockByIdx(self.superblock.blockMapAddr)
        if not block:
            return []
        valus = []
        offset = 0

        while offset < len(block):
            valu = v_uint32(bigend=False)
            valu.vsParse(block[offset:offset+4])
            offset += 4
            if valu == 0:
                continue
            valus.append(valu.vsGetValue())

        dirs = []
        for idx in valus:
            block = self.getBlockByIdx(idx)
            sdir = v_d_pdb.StreamDirectory(int(self.superblock.blockSize))
            sdir.vsParse(block)

            dirs.append(sdir)

        return dirs

    def getBlockByIdx(self, idx):
        bsize = self.superblock.blockSize
        offset = idx * bsize
        if offset < len(self.byts):
            return self.byts[offset:offset+bsize]
        return None

    def iterblocks(self):
        idx = 0
        offset = 0
        while offset < len(self.byts):
            yield idx, self.byts[offset:(offset+self.superblock.blockSize)]
            idx += 1
            offset += self.superblock.blockSize

if __name__ == '__main__':
    with open('C:\\Users\\James\\Documents\\Visual Studio 2015\\Projects\\raytracing\\Debug\\raytracing.pdb', 'rb') as fd:
        byts = fd.read()
    obj = PDB(byts)
    breakpoint()
    print('wat')
