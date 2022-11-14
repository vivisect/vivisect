import vstruct.defs.pepdb as v_d_pdb

class PDB:
    def __init__(self, byts):
        self.byts = byts
        self.superblock = SuperBlock()
        self.superblock.vsParse(byts)

        self.streamsdirs = self.getStreamDirs()

    def getStreamDirs(self):
        '''
        The stream directory is not guaranteed to fit in a single block
        so an MSF adds a layer of indirection.
        '''
        block = self.getBlockByIdx(self.superblock.blockmapaddr)
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
            sdir = StreamDirectory(int(self.superblock.blocksize))
            sdir.vsParse(block)

            dirs.append(sdir)

        return dirs

    def getBlockByIdx(self, idx):
        bsize = self.superblock.blocksize
        offset = idx * bsize
        if offset < len(self.byts):
            return self.byts[offset:offset+bsize]
        return None

    def iterblocks(self):
        idx = 0
        offset = 0
        while offset < len(self.byts):
            yield idx, self.byts[offset:(offset+self.superblock.blocksize)]
            idx += 1
            offset += self.superblock.blocksize

if __name__ == '__main__':
    with open('C:\\Users\\James\\Documents\\Visual Studio 2015\\Projects\\devicelist\\Debug\\devicelist.pdb', 'rb') as fd:
        byts = fd.read()
    pdb = PDB(byts)
    breakpoint()
    print('wat')
