import vivisect.lib.bexfile as v_bexfile

class PeBexFile(v_bexfile.BexFile):
    pass

    #def _bex_entry(self):

    #def _bex_info_dos_header(self):

def checker(fd):
    # maybe do more here...
    if fd.read(2) == 'MZ':
        return True

v_bexfile.addBexFormat('pe',checker,PeBexFile)
