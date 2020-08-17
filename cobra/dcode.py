"""

Cobra's distributed code module capable of allowing
serialization of code from one system to another.

Particularly useful for clustering and workunit stuff.

"""
import os
import sys
import imp
import logging

import cobra

logger = logging.getLogger(__name__)


class DcodeServer:

    def getPythonModule(self, fullname, path=None):

        # Some serialization causes this to be a tuple
        # and find_module is SUPER SERIOUS about it being
        # a *list*... ;)
        if path is not None:
            path = list(path)

        fullname = fullname.split(".")[-1]

        try:
            fobj, filename, typeinfo = imp.find_module(fullname, path)
        except ImportError:
            return None

        if os.path.isdir(filename):
            typeinfo = ('.py', 'U', 1)
            filename = os.path.join(filename, "__init__.py")

        if not os.path.exists(filename):
            return None

        if typeinfo[0] != '.py':
            return None

        path = os.path.dirname(filename)
        with open(filename, 'rU') as f:
            fbytes = f.read()
        return (fbytes, filename, path)


def toutf8(s):
    if type(s) == unicode:
        s = s.encode('utf8')
    return s


class DcodeLoader(object):

    """
    This object gets returned by the DcodeFinder
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
            mod = imp.new_module(fullname)
            sys.modules[fullname] = mod
            mod.__file__ = self.filename
            mod.__loader__ = self
            if self.path is not None:
                mod.__path__ = [self.path]

            exec toutf8(self.fbytes) in mod.__dict__

        return mod


class DcodeFinder(object):
    """
    This object goes into the client side import path_hooks
    to allow cobra:// uri's to be added to the import path.
    """
    def __init__(self, proxy):
        self.proxy = proxy

    def find_module(self, fullname, path=None):

        # Check for local modules first...
        localname = fullname.split('.')[-1]
        name, ext = os.path.splitext(localname)

        try:
            fobj, filename, typeinfo = imp.find_module(name, path)
        except ImportError:

            logger.info('Dcode Searching: %s (%s)', name, path)
            pymod = self.proxy.getPythonModule(fullname, path)
            if pymod:
                logger.info('Dcode Loaded: %s', fullname)
                return DcodeLoader(*pymod)


def addDcodeProxy(proxy):
    finder = DcodeFinder(proxy)
    sys.meta_path.append(finder)


def addDcodeUri(uri):
    proxy = cobra.CobraProxy(uri, timeout=120, retrymax=3)
    addDcodeProxy(proxy)


def addDcodeServer(server, port=cobra.COBRA_PORT, ssl=False):
    scheme = "cobra"
    if ssl:
        scheme = "cobrassl"

    uri = "%s://%s:%d/DcodeServer" % (scheme, server, port)
    addDcodeUri(uri)


def enableDcodeServer(daemon=None):
    server = DcodeServer()
    if daemon:
        daemon.shareObject(server, 'DcodeServer')
        return
    cobra.shareObject(server, 'DcodeServer')
