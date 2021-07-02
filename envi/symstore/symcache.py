import os
import json
import logging

import envi.exc as e_exc
import envi.config as e_config

logger = logging.getLogger(__name__)

def symCacheHashFromPe(pe):
    checksum = pe.IMAGE_NT_HEADERS.OptionalHeader.CheckSum
    codesize = pe.IMAGE_NT_HEADERS.OptionalHeader.SizeOfCode
    timestamp = pe.IMAGE_NT_HEADERS.FileHeader.TimeDateStamp
    return 'pe.%.8x.%.8x.%.8x' % (timestamp,checksum,codesize)

def symCacheHashFromElf(elf):
    pass #FIXME

class SymbolCache:
    '''
    A SymbolCache is a location where pre-parsed symbols for
    a given file's "symcache hash" are stored.  This allows faster
    loading of symbol information on re-load etc...

    Also, this object's API *must* be compatible with cobra
    shared object API to allow "symbol servers" to be cobra
    shared instances of SymbolCache objects.
    '''
    def __init__(self, dirname=None):

        if dirname is None:
            dirname = e_config.gethomedir('.envi', 'symcache')

        if not os.path.isdir(dirname):
            os.makedirs(dirname)

        self._sym_cachedir = os.path.abspath(dirname)

    def setCacheSyms(self, vhash, symcache):
        '''
        Save a set of symbol cache tuples to the symbol cache.

        Example:
            tups = [ ( rva, size, 'wootfunc', SYMSTOR_SYM_FUNCTION), ]
            cache = SymbolCache()
            cache.setCacheSyms( vhash, tups )
        '''
        cachefile = os.path.join(self._sym_cachedir, vhash)

        abspath = os.path.abspath(cachefile)
        if not abspath.startswith(self._sym_cachedir):
            raise e_exc.InvalidSymbolCache(vhash)

        # FIXME check input path
        with open(cachefile, 'w', encoding='utf-8') as fd:
            json.dump(symcache, fd)

    def getCacheSyms(self, vhash):
        '''
        Retrieve a list of symbol tuples ( rva, size, name, symtype )
        or None if the symbol cache doesn't have the given file hash.

        Example:
            cache = SymbolCache()
            for rva, size, name, stype in cache.getCacheSyms():
                dostuff()
        '''
        cachefile = os.path.join(self._sym_cachedir, vhash)

        abspath = os.path.abspath(cachefile)
        if not abspath.startswith(self._sym_cachedir):
            raise e_exc.InvalidSymbolCache(vhash)

        if not os.path.isfile(cachefile):
            return None

        try:
            with open(cachefile, 'r', encoding='utf-8') as fd:
                return json.load(fd)
        except Exception as e:
            logger.warning('Failed to load cachefile: %s', e)
            return None


class SymbolCachePath:

    def __init__(self, path):
        self.symcaches = []

        for path in path.split(';'):

            if os.path.isdir(path):
                self.symcaches.append(SymbolCache(dirname=path))
                continue

            if path.startswith('cobra://') or path.startswith('cobrassl://'):
                import cobra
                self.symcaches.append(cobra.CobraProxy(path))
                continue

            #if path.startswith('http://') or path.startswith('https://'):
                #FIXME

    def getCacheSyms(self, symhash):

        for symcache in self.symcaches:
            ret = symcache.getCacheSyms(symhash)
            if ret is not None:
                return ret

    def setCacheSyms(self, symhash, symcache):
        if self.symcaches:
            self.symcaches[0].setCacheSyms(symhash, symcache)
