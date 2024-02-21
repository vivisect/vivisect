"""

Cobra's distributed code module capable of allowing
serialization of code from one system to another.

Particularly useful for clustering and workunit stuff.

"""
import os
import sys
import logging
import importlib

import cobra

from importlib.abc import Loader, MetaPathFinder
from importlib.util import spec_from_loader, module_from_spec

logger = logging.getLogger(__name__)


class DcodeServer:
    '''
    Server-side Dcode class.  Allows the sharing of Server-side python modules to the remote client
    '''

    def getPythonModule(self, fullname, path=None):

        # Some serialization causes this to be a tuple
        # and find_module is SUPER SERIOUS about it being
        # a *list*... ;)
        if path is not None:
            path = list(path)

        fullname = fullname.split(".")[-1]

        try:
            mspec = importlib.util.find_spec(fullname)
            filename = mspec.origin
        except ImportError:
            return None

        if not os.path.exists(filename):
            return None

        path = os.path.dirname(filename)
        with open(filename, 'r') as f:
            fbytes = f.read()
        return (fbytes, filename, path)


class DcodeLoader(Loader):
    """
    This object gets returned by the DcodeFinder (client-side)
    """
    def __init__(self, fbytes, filename, path):
        object.__init__(self)
        self.fbytes = fbytes
        self.filename = filename
        self.path = path

    def get_source(self, name):
        return self.fbytes

    def load_module(self, fullname):
        mod = sys.modules.get(fullname)
        if mod is None:
            spec = spec_from_loader(fullname, loader=None)
            mod = module_from_spec(spec)
            sys.modules[fullname] = mod
            exec(self.fbytes, mod.__dict__)
            mod.__file__ = self.filename
            mod.__loader__ = self
            if self.path is not None:
                mod.__path__ = [self.path]

        return mod


    def create_module(self, spec):
        return None

    def exec_module(self, mod):
        exec(self.fbytes, mod.__dict__)
        mod.__file__ = self.filename
        mod.__loader__ = self
        if self.path is not None:
            mod.__path__ = [self.path]
        


class DcodeFinder(object):
    """
    This object goes into the client side import path_hooks
    to allow cobra:// uri's to be added to the import path.

    For reference, this is a MetaPathFinder
    """
    def __init__(self, proxy):
        self.proxy = proxy
        self.counter = 0

    def find_module(self, fullname, path=None):

        # Check for local modules first...
        localname = fullname.split('.')[-1]
        name, ext = os.path.splitext(localname)

        try:
            mspec = importlib.util.find_spec(fullname)
        except ValueError:

            logger.info('Dcode Searching: %s (%s)', name, path)
            pymod = self.proxy.getPythonModule(fullname, path)
            if pymod:
                logger.info('Dcode Loaded: %s', fullname)
                return DcodeLoader(*pymod)

    def find_spec(self, fullname, path, target=None):
        if self.counter:
            raise AttributeError("find_spec called by itself....  stop recursion")
        self.counter += 1

        # Check for local modules first...
        localname = fullname.split('.')[-1]
        name, ext = os.path.splitext(localname)

        try:
            mspec = importlib.util.find_spec(fullname, path)

        except AttributeError as e:
            logger.info('Dcode Searching: %s (%s)', name, path)
            pymod = self.proxy.getPythonModule(fullname, path)
            if pymod:
                logger.info('Dcode Loaded: %s', fullname)
                # need to return a spec
                return spec_from_loader(fullname, DcodeLoader(*pymod))

        finally:
            self.counter -= 1

# Client-side helper functions
def addDcodeProxy(proxy):
    finder = DcodeFinder(proxy)
    sys.meta_path.append(finder)


def addDcodeUri(uri):
    proxy = cobra.CobraProxy(uri, timeout=120, retrymax=3)
    addDcodeProxy(proxy)


def addDcodeServer(server, port=cobra.COBRA_PORT, ssl=False, msgpack=True):
    scheme = "cobra"
    if ssl:
        scheme = "cobrassl"

    uri = "%s://%s:%d/DcodeServer" % (scheme, server, port)
    if msgpack:
        uri += "?msgpack=1"

    addDcodeUri(uri)


# Server-side helper function
def enableDcodeServer(daemon=None):
    server = DcodeServer()
    if daemon:
        daemon.shareObject(server, 'DcodeServer')
        return
    cobra.shareObject(server, 'DcodeServer')



def main():
    '''
    Launch a Dcode server including any paths you list on the command line
    '''
    import argparse
    parser = argparse.ArgumentParser(prog='cobraDcode', usage='%(prog)s [options] [additional_path1 [additional_path2] [...]]>')
    parser.add_argument('-C', '--clearpath', default=False, help='Clear the PYTHONPATH and only share specified paths')
    parser.add_argument('-P', '--port', dest='port', type=int, default=cobra.COBRA_PORT,
                        help='Listen on what port')
    parser.add_argument('--cacrt', default=None, help='Use TLS encryption: With this Certificate Authority Cert (file)')
    parser.add_argument('--srvcrt', default=None, help='Use TLS encryption: With this Server Cert (file)')
    parser.add_argument('--srvkey', default=None, help='Use TLS encryption: With this Server Key (file)')
    parser.add_argument('path', nargs='*')
    args = parser.parse_args()

    if args.clearpath:
        sys.path = []

    for path in args.path:
        if path not in sys.path:
            logger.info('Adding path "%s" to system path (ie. will serve to Dcode clients)', path)
            sys.path.append(path)

    # first start a cobra server on the specified port
    daemon = cobra.startCobraServer(port=args.port, sslca=args.cacrt, sslcrt=args.srvcrt, sslkey=args.srvkey, msgpack=1)

    # next, enable Dcode
    enableDcodeServer(daemon)

    # wait forever (or until the process is killed)
    daemon.thr.join()




if __name__ == "__main__":
    import envi.common as ecmn
    ecmn.initLogging(logger, logging.DEBUG)
    main()
