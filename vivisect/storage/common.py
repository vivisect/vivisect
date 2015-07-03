import os
import hashlib
import importlib

from urllib.parse import urlparse

import vivisect.workspace as v_workspace

class VivStoreImplementMe(Exception):pass

class VivStore:
    '''
    A VivStore manages VivFile and VivWorkspace storage.
    '''

    def __init__(self, uri):
        self.uri = uri

    def addVivFile(self, fd):
        '''
        Add a file to the VivStore.

        Example:

            fd = open('myfile.dll','rb')
            vf = vs.addVivFile(fd)

        '''
        fd.seek(0)
        md5 = hashlib.md5()
        x = fd.read(1024000)
        while x:
            md5.update(x)
            x = fd.read(1024000)

        filemd5 = md5.hexdigest()

        vf = self.getVivFile(filemd5)
        if vf != None:
            return vf

        fd.seek(0)
        self._initVivFile(filemd5)
        self._saveVivFileFd(filemd5, fd)
        return self.getVivFile(filemd5)

    def hasVivFile(self, filemd5):
        '''
        Returns True if the VivStore already contains filemd5.

        Example:

            if vs.hasVivFile(filemd5):
                dostuff()

        '''
        return self._hasVivFile(filemd5)

    def getVivFile(self, filemd5):
        '''
        Open, load, and return a VivFile by md5.
        '''
        if not self._hasVivFile(filemd5):
            return None
        vf = v_workspace.VivFile( self, filemd5 )
        self._loadVivFileEvents(vf)
        return vf

    def getVivWork(self, ident):
        '''
        Open, load and return a VivWorkspace by ident.

        Example:

            vw = vs.getVivWork('foobar')

        '''
        vw = v_workspace.VivWorkspace()
        self._loadVivWorkEvents(vw)

    def delVivWork(self, ident):
        pass # TODO

    def _hasVivFile(self, filemd5):
        raise VivStoreImplementMe()

    def _loadVivFileEvents(self, vf):
        raise VivStoreImplementMe()

    def _loadVivWorkEvents(self, vw):
        raise VivStoreImplementMe()

    def _initVivFile(self, filemd5):
        raise VivStoreImplementMe()

    def _saveVivFileFd(self, filemd5, fd):
        raise VivStoreImplementMe()

storenames = {}
def addStoreModule(scheme,modname):
    '''
    Add a vivisect storage module by name for a uri scheme.

    Example:

        import vivisect.storage as v_storage
        v_storage.addStorModule('woot','mything.wootstor')

        # now you may open a custom VivStore.
        vs = getVivStore('woot://stuff/blah')
    '''
    storenames[scheme] = modname

# load a few built-ins
addStoreModule('dir','vivisect.storage.dir')
addStoreModule('ram','vivisect.storage.ram')

def getVivStore(uri=None):
    '''
    Open a VivStore by uri which defaults to user specific directory storage.

    Example:

        vs = getVivStore()

    '''
    if uri == None:
        uri = getStoreUri()

    p = urlparse(uri)
    mod = getStoreModule(p.scheme)
    return mod.getVivStore(uri)

storemods = {}
def getStoreModule(scheme):
    '''
    Retrieve the viv storage module by uri scheme.
    '''
    mod = storemods.get(scheme)
    if mod == None:
        name = storenames.get(scheme)
        if name == None:
            raise Exception('Unknown Viv Storage: %s' % (scheme,))
        mod = importlib.import_module(name)
        storemods[scheme] = mod
    return mod

def getStoreUri():
    '''
    Get the uri describing the currently configured VivStor.

    Defaults to dir:///<homedir>/.vivstor use VIVSTOR to override.
    '''
    uri = os.getenv('VIVSTOR')
    if uri:
        return uri

    stordir = os.path.join(os.path.expanduser('~'),'.vivstor')
    stordir = os.path.abspath(stordir)

    os.makedirs(stordir,0o700,exist_ok=True)

    return 'dir:///' + stordir
