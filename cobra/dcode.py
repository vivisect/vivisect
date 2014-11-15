'''
Cobra's distributed code module capable of allowing serialization of code from
one system to another.

Useful for clustering and workunit stuff.
'''
import os
import sys
import imp

import cobra

verbose = False

class DcodeServer(object):
    def __init__(self, upaths=None):
        self.paths = set()
        if upaths != None:
            [self.addPath(upath) for upath in paths]

    def addPath(self, path):
        '''
        adds a path that allows python code to be 'served' from.
        '''
        path = os.path.abspath(path)
        self.paths.add(path)

    def isValidPath(self, upath):
        '''
        checks if the specified path is allowed according to our whitelisted
        paths.
        '''
        for path in self.paths:
            fpath = os.path.join(path, upath)
            fpath = os.path.abspath(fpath)

            if fpath.startswith(path):
                return True

        if verbose: print('dcode: not a valid path, {}'.format(upath))
        return False

    def getPythonModule(self, fullname, pkgpath=None):
        '''
        called by a remote callers to retrieve code they dont have.
        '''
        if verbose: print('getPythonModule: {} {}'.format(fullname, pkgpath))

        # Some serialization causes this to be a tuple and find_module is SUPER
        # SERIOUS about it being a *list*... ;)
        # TODO: this is a hack for old skewl msgpack.  can we remove this?
        if pkgpath != None:
            pkgpath = list(pkgpath)

        fullname = fullname.split('.')[-1]
        fobj = None
        try:
            fobj, fname, typeinfo = imp.find_module(fullname, pkgpath)
        except ImportError as e:
            return None
        finally:
            if fobj != None:
                fobj.close()

        if not self.isValidPath(os.path.dirname(fname)):
            return None

        if os.path.isdir(fname):
            typeinfo = ('.py', 'U', 1)
            fname = os.path.join(fname, '__init__.py')

        if not os.path.exists(fname):
            return None

        if typeinfo[0] != '.py':
            return None

        path = os.path.dirname(fname)
        bytez = None
        with open(fname, 'rU') as f:
            bytez = f.read()
        return (bytez, fname, path)

class DcodeLoader(object):
    '''
    returned if finder found import src on remote server.  loads bytes.
    '''
    def __init__(self, bytez, fname, path):
        self.bytez = bytez
        self.fname = fname
        self.path = path

    def get_source(self, name):
        return self.bytez

    def load_module(self, fullname):
        mod = sys.modules.get(fullname)
        if mod != None:
            return mod

        mod = imp.new_module(fullname)
        sys.modules[fullname] = mod
        mod.__file__ = self.fname
        mod.__loader__ = self
        if self.path != None:
            mod.__path__ = [self.path]

        exec(self.bytez, mod.__dict__)

        return mod

class ImpWrapLoader(object):
    '''
    wraps imp.load_module; returned if finder found a local import.
    '''
    def __init__(self, fobj, path, desc):
        self.fobj = fobj
        self.path = path
        self.desc = desc

    def load_module(self, fullname):
        try:
            return imp.load_module(fullname, self.fobj, self.path, self.desc)
        finally:
            if self.fobj != None:
                self.fobj.close()

class DcodeFinder(object):
    '''
    This object goes into the client side import path_hooks to allow one or more
    cobra:// uri's to be added to the import path.
    '''
    def __init__(self, proxies):
        self.proxies = set(proxies)

    def addDcodeProxy(self, proxy):
        self.proxies.add(proxy)

    def find_module(self, fullname, path=None):
        '''
        see:
        http://legacy.python.org/dev/peps/pep-0302/
        https://docs.python.org/2/library/sys.html#sys.meta_path
        https://docs.python.org/2/library/imp.html#imp.find_module
        '''
        # foo.bar.os -> os
        mname = fullname.split('.')[-1]

        # search built-in, frozen, reg, etc and on sys.path for mname
        if verbose: print('dcode: searching for {}'.format(mname))
        try:
            ftup = imp.find_module(mname)
            return ImpWrapLoader(*ftup)
        except ImportError as e:
            pass

        # search on specified paths (path kwarg) for mname
        if path != None:
            try:
                if verbose: print('dcode: searching for {}'.format(fullname))
                ftup = imp.find_module(mname, path)
                return ImpWrapLoader(*ftup)
            except ImportError as e:
                pass

        # search on remote servers
        for proxy in self.proxies:
            if verbose: print('dcode: searching for {} on remote'.format(fullname))
            pymod = proxy.getPythonModule(fullname, path)
            if pymod:
                if verbose: print('dcode: found, {}'.format(fullname))
                return DcodeLoader(*pymod)

        # allow import processing to continue normally (instead of raising
        # exception and stopping it)
        return None

def addDcodeUri(uri):
    '''
    adds a dcode uri by constructing a CobraProxy.  we put all dcode
    CobraProxies in the *same* DcodeFinder object in sys.meta_path.
    (there should only ever be a single DcodeFinder if you always add dcode
    uris through this api.)
    '''
    proxy = cobra.CobraProxy(uri, timeout=120, retrymax=3)
    for fobj in sys.meta_path:
        if isinstance(fobj, DcodeFinder):
            fobj.addDcodeProxy(proxy)
            return

    finder = DcodeFinder( (proxy, ) )
    sys.meta_path.append(finder)

def addDcodeServer(server, port=cobra.COBRA_PORT, ssl=False, msgpack=False):
    scheme = 'cobra'
    if ssl:
        scheme = 'cobrassl'

    uri = '{}://{}:{}/DcodeServer?msgpack={:d}'.format(scheme, server, port, msgpack)
    addDcodeUri(uri)

def delAllDcodeServers():
    for fobj in list(sys.meta_path):
        if isinstance(fobj, DcodeFinder):
            sys.meta_path.remove(fobj)
            return

def enableDcodeServer(daemon=None):
    server = DcodeServer()
    if daemon:
        daemon.shareObject(server, 'DcodeServer')
        return
    cobra.shareObject(server, 'DcodeServer')
