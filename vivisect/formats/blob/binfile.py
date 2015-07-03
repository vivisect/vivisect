import vivisect.hal.memory as v_memory
import vivisect.lib.binfile as v_binfile

from vertex.lib.common import tufo

class BlobBinFile(v_binfile.BinFile):
    '''
    A BlobBinFile is for use with blobs of bytes.

    The only things the parser knows is what you tell it. For
    each of the top level bin.stuff() APIs you may specify
    stuff=<answer> in the initializer info.

    Example:

        bf = v_binfile.getFile(fd, format='blob', arch='i386')

    '''
    def __init__(self, fd, **info):
        v_binfile.BinFile.__init__(self, fd, **info)

    def _getArch(self):
        return self.getInfo('arch')

    def _getFormat(self):
        return 'blob'

    def _getMemoryMaps(self):
        return [ tufo(0, init=self._bin_bytes) ]

v_binfile.addBinFormat('blob',BlobBinFile)
