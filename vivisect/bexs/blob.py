
import vivisect.hal.memory as v_memory
import vivisect.lib.bexfile as v_bexfile

class BlobBexFile(v_bexfile.BexFile):
    '''
    A BlobBexFile is for use with blobs of bytes.

    The only things the parser knows is what you tell it. For
    each of the top level bex.stuff() APIs you may specify
    stuff=<answer> in the initializer info.

    Example:

        bex = v_bexfile.getBexFile(fd, format='blob', arch='i386')

    '''
    def __init__(self, fd, **info):
        v_bexfile.BexFile.__init__(self, fd, **info)

    def _bex_arch(self):
        return self.info('arch')

    def _bex_format(self):
        return 'blob'

    def _bex_memmaps(self):
        self._bex_fd.seek(0)
        mem = self._bex_fd.read()
        return ( ( 0, v_memory.MM_RWX, mem), )

def noway(fd):
    # never auto-ident a blob
    return False

v_bexfile.addBexFormat('blob',noway,BlobBexFile)
