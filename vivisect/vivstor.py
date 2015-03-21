'''
Utilities for VivWorkspace management via directory structure
'''
import os
import time

import vertex.graph as v_graph
import vivisect.lib.bits as v_bits
import synapse.lib.common as s_common

import msgpack # version checked by s_common

from urllib.parse import urlparse

class VivStor:

    def __init__(self, uri):
        self.storuri = uri

    def saveVivWork(self, vw):
        '''
        Save a VivWorkspace instance to the VivStor.

        Example:

            vw = VivWorkspace()
            ...
            import vivisect.vivstor as v_vivstor

            stor = v_vivstor.getDefaultStor()
            stor.saveVivWork(vw)

        NOTE: this need only be called on first saving.
              ( when loaded from stor, saves are automatic )
        '''
        return self._vstor_save(vw)

    def initVivWork(self):
        '''
        Create a new VivWorkspace in the VivStor.

        vw = stor.initVivWork()
        '''
        return self._vstor_init()

    def loadVivWork(self, ident):
        '''
        Load a VivWorkspace by identifier.

        Example:

            import vivisect.vivstor as v_vivstor
            stor = v_vivstor.getDefaultStor()
            vw = stor.loadVivWork(ident)
        '''
        return self._vstor_load(ident)

    def findVivWork(self, filehash):
        '''
        Find a VivWorkspace ident for the given file hash (or None)

        Checks to see if the VivStor is aware of a workspace containing
        the given filehash, and returns it's ident.
        '''
        return self._vstor_find(filehash)

    def _vstor_init(self):
        raise Exception('ImplementMe')

    def _vstor_save(self, vw):
        raise Exception('ImplementMe')

    def _vstor_load(self, ident):
        raise Exception('ImplementMe')

    def _vstor_find(self, filehash):
        raise Exception('ImplementMe')

    @staticmethod
    def storWantsUri(self, uri):
        return False

class VivDirLock:
    '''
    A simple exclusion lock to protect directory access.
    '''
    def __init__(self, dirname, timeout=None):
        self.dirname = dirname
        self.timeout = timeout

        self.pathname = os.path.join(dirname, '.vivlock')

    def acquire(self):
        start = time.time()
        while True:
            if self.timeout != None and (time.time() - start ) > self.timeout:
                return False

            try:
                os.mkdir( self.pathname )
                return True

            except OSError as e:
                time.sleep(0.1)

    def release(self):
        os.rmdir( self.pathname )

    def __enter__(self):
        self.acquire()

    def __exit__(self, ex, exc, tb):
        self.release()

class VivDirStor(VivStor):

    version = (2,0,0)

    def __init__(self, uri):
        VivStor.__init__(self, uri)
        # trim leading '/'
        self.vivdir = urlparse(uri).path[1:]
        if not os.path.isdir( self.vivdir ):
            raise Exception('Invalid VivDirStor path: %s' % self.vivdir )

        self.dirlock = VivDirLock(self.vivdir)

        with self.dirlock:
            metapath = os.path.join( self.vivdir, 'vivstor.mpk' )
            if not os.path.isfile(metapath):
                self._setMetaDict({'version':self.version})

    #def _vstor_init(self):
    #def _vstor_find(self, filehash):
    #def _vstor_load(self, ident):

    def _initStoreWork(self, vw):
        # setup vw runtime for backing by this stor
        vw.on('viv:stor:save',self._slot_stor_save)
        vw.on('viv:stor:close',self._slot_stor_close)

    def _slot_stor_save(self, event):
        vw = event[1].get('vw')
        full = event[1].get('fullsave')
        ident = v_bits.b2h( vw.getVivConfig('ident') )

    def _slot_stor_close(self, event):
        vw = event[1].get('vw')

        lock = vw.getRunInfo('stor:lock')
        if lock != None:
            lock.release()

        #ident = v_bits.b2h( vw.getVivConfig('ident') )

    def _vstor_save(self, vw):

        ident = v_bits.b2h( vw.getVivConfig('ident') )
        with self.dirlock:

            vwdir = os.path.join( self.vivdir, ident )
            if os.path.isdir(vwdir):
                raise Exception('VivDirStor: %s already saved!' % (ident,))

            os.makedirs(vwdir,0o700)
            vwpath = os.path.join( vwdir, '%s.viv' % (ident,) )

            lock = VivDirLock(vwdir)
            lock.acquire()

            vw.setRunInfo('stor:lock',lock)
            self._initStorWork(vw)

        # do save stuff here!

    def _addVwFileMaps(self, ident, hashes):
        # only with lock
        meta = self._getMetaDict()

        qh = meta.setdefault('quickhash',{})
        ws = meta.setdefault('workspace',{})

        vwinfo = ws.setdefault(ident,{})
        vwinfo['files'] = hashes

        for filehash in hashes:
            qh[filehash] = ident

        self._setMetaDict(meta)

    def _getMetaDict(self):
        metapath = os.path.join( self.vivdir, 'vivstor.mpk' )
        metablob = open(metapath,'rb').read()
        return msgpack.unpackb(metablob)

    def _setMetaDict(self, info):
        metapath = os.path.join( self.vivdir, 'vivstor.mpk' )
        metablob = msgpack.packb(info,use_bin_type=True)
        open(metapath,'wb').write(metablob)

    @staticmethod
    def storWantsUri(uri):
        if urlparse(uri).scheme == 'dir':
            return True

vwstors = [VivDirStor]
def addStorClass(cls):
    '''
    Add a VivStor storage class to the runtime.
    '''
    vwstors.append( cls )

def getStorUri():
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

def getVivStor(uri=None):
    '''
    Retrieve the current VivStor based on VIVSTOR env var.
    ( deafults to dir:///~/.vivstor )
    '''
    if uri == None:
        uri = getStorUri()

    for cls in vwstors:
        if cls.storWantsUri(uri):
            return cls(uri)

