import io
import synapse.event.store as s_store
import vivisect.storage.common as v_storage

class VivRamStore(v_storage.VivStore):

    def __init__(self, uri):
        v_storage.VivStore.__init__(self, uri)

        self.fdbymd5 = {}
        self.evtstores = {}

    def _hasVivFile(self, filemd5):
        return self.fdbymd5.get(filemd5) != None

    def _loadVivFileEvents(self, vf):
        evtstor = self.evtstores.get(vf.filemd5)
        evtstor.synLoadAndStore(vf.evtbus)

    def _initVivFile(self, filemd5):
        fd = io.BytesIO()
        evtstor = s_store.EventFdStore(fd)
        self.evtstores[filemd5] = evtstor

    def _saveVivFileFd(self, filemd5, fd):
        self.fdbymd5[filemd5] = fd

ramstores = {}
def getVivStore(uri):
    vs = ramstores.get(uri)
    if vs == None:
        vs = VivRamStore(uri)
        ramstores[uri] = vs
    return vs
