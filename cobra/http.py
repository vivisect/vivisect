"""
Implementation of Cobra using HTTP
"""

import os
import json
import time
import types
import urllib
import base64
import Cookie
import httplib
import logging
import urlparse
import traceback
import BaseHTTPServer

import cobra as c_cobra

from threading import currentThread,Thread,RLock
from SocketServer import ThreadingTCPServer

logger = logging.getLogger(__name__)
daemon = None
version = "Cobra2"
COBRA_PORT = 80
COBRASSL_PORT = 443
cobra_retrymax = None  # Optional *global* retry max count


class CobraHttpException(Exception):
    """Base for Cobra exceptions"""
    pass


def chopCobraHttpUri(uri):
    '''
    Breaks apart a URI provided by as input to a function.
    Any API call must at least contain an empty args=[] or args=()
    calls can ommit kwargs.
    URI format is:
    /[OBJECT]/[FUNCTION]?args=<JSON ARGS>&kwargs=<JSON KWARGS>

    Returns:
        [OBJECT], [FUNCTION], args or (), kwargs or {}
    '''
    url = uri
    if uri.startswith('/'):
        # get rid of starting /
        url = urlparse.urlsplit(uri[1:])

    objname, methname = url.path.split('/', 1)

    # Do we have any URL options?
    urlparams = {}
    for urlopt in urllib.unquote(url.query).split('&'):
        urlval = '1'
        if urlopt.find('=') != -1:
            urlopt, urlval = urlopt.split('=', 1)

        urlopt = urlopt.lower()
        urlparams[urlopt] = json.loads(urlval)

    return objname, methname, urlparams.get('args', ()), urlparams.get('kwargs', {})


class CobraHttpRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    '''
    Request handler for HTTP cobra
    '''
    def __init__(self, *args, **kwargs):
        self.handlers = {
                '__cobra_hello': self.handleHello,
                '__cobra_getattr': self.handleGetAttr,
                '__cobra_setattr': self.handleSetAttr,
                '__cobra_login': self.handleLogin
            }
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    def do_POST(self):
        # this is a json posted data list (args, kwargs)
        body = json.loads(urllib.unquote(self.rfile.read(int(self.headers['Content-Length']))))

        # self.handleClient(s.server, s, s.path, body=body)
        self.handleClient(body=body)

    def do_GET(self):
        self.handleClient()

    def setup(self):
        # SSLify..
        if self.server.sslkey:
            import ssl
            sslca = self.server.sslca
            keyfile = self.server.sslkey
            certfile = self.server.sslcrt
            sslreq = ssl.CERT_NONE
            # If they specify a CA key, require valid client certs
            if sslca:
                sslreq = ssl.CERT_REQUIRED

            self.request = ssl.wrap_socket(self.request,
                                           keyfile=keyfile,
                                           certfile=certfile,
                                           ca_certs=sslca,
                                           cert_reqs=sslreq,
                                           server_side=True)
        BaseHTTPServer.BaseHTTPRequestHandler.setup(self)

    def handleClient(self, body=None):
        # validate authentication
        try:
            objname, methname, args, kwargs = chopCobraHttpUri(self.path)
        except:
            # If we had an exception its a malformed request..
            self.request.send_response(httplib.INTERNAL_SERVER_ERROR)
            self.request.end_headers()
            excinfo = "%s" % traceback.format_exc()
            self.request.wfile.write(json.dumps(excinfo))
            return

        if body:
            args = body.get('args', ())
            kwargs = body.get('kwargs', {})

        # user is trying to authenticate
        if methname == '__cobra_login':
            return self.handlers['__cobra_login'](objname, kwargs)

        if self.server.authmod:
            authinfo = None
            if not self.headers.getheader('Cookie'):
                # user not authenticated
                self.request.send_response(httplib.UNAUTHORIZED)
                self.request.end_headers()
                return

            cookie = self.headers['Cookie']
            # Cookie: SessionId="[SESSIONKEY]"
            sessid = cookie.split('=',1)[1].replace("\"", "")
            # Invalid session!
            if not self.server.sessions.get(sessid):
                self.request.send_response(httplib.UNAUTHORIZED)
                self.request.end_headers()
                return

            authinfo,tstamp = self.server.sessions[sessid]

            # Ensure user cna access our object
            if not authinfo or not self.server.authmod.checkUserAccess( authinfo['user'], methname):
                self.request.send_response(httplib.UNAUTHORIZED)
                self.request.end_headers()
                return

        if self.handlers.get(methname):
            return self.handlers[methname](objname, *args, **kwargs)

        # at this point we have a call
        obj = self.server.getSharedObject(objname)
        if hasattr(obj, methname):
            meth = getattr(obj, methname)
            try:
                ret = meth(*args, **kwargs)
                self.send_response(httplib.OK)
                self.end_headers()
                self.wfile.write(json.dumps(ret))
            except Exception as e:
                self.send_response(httplib.INTERNAL_SERVER_ERROR)
                self.end_headers()
                excinfo = "%s" % traceback.format_exc()
                self.wfile.write(json.dumps(excinfo))

            return

        self.send_response(httplib.BAD_REQUEST)
        self.end_headers()
        excinfo = "Bad Request: No function named '%s'" % methname
        self.wfile.write(json.dumps(excinfo))
        return

    def handleLogin(self, objname, authinfo):
        if not self.server.getSharedObject(objname):
            raise Exception('Shared object does not exists!')

        if self.server.authmod:
            if not authinfo or not self.server.authmod.authCobraUser(authinfo):
                self.send_response(httplib.UNAUTHORIZED)
                self.end_headers()
            else:
                sesskey = base64.b64encode( os.urandom(32) )
                self.server.sessions[ sesskey ] = (authinfo, time.time())
                c = Cookie.SimpleCookie()
                c['SessionId'] = sesskey
                # set morsel
                self.send_response(httplib.OK)
                self.send_header('Set-Cookie', c.values()[0].output(header=''))
                self.send_header("Content-type", "text/html")
                self.end_headers()
            return

        self.send_response(httplib.OK)
        self.end_headers()

    def handleHello(self, objname):
        '''
        Hello messages are used to get the initial cache of
        method names for the newly connected object.
        '''
        logger.debug('Hello')
        obj = self.server.getSharedObject(objname)
        ret = {}
        for name in dir(obj):
            if type(getattr(obj, name)) in (types.MethodType, types.BuiltinMethodType):
                ret[name] = True
        self.send_response(httplib.OK)
        self.end_headers()
        self.wfile.write(json.dumps(ret))
        return

    def handleGetAttr(self, objname, attr):
        logger.debug('GetAttr: %s', attr)
        if not self.server.attr:
            self.send_response(httplib.FORBIDDEN)
            self.end_headers()
            excinfo = "__getattr__ disabled"
            self.wfile.write(json.dumps(excinfo))
            return
        obj = self.server.getSharedObject(objname)
        try:
            val = getattr(obj, attr)
            self.send_response(httplib.OK)
            self.end_headers()
            self.wfile.write(json.dumps(val))
        except Exception:
            self.send_response(httplib.NOT_FOUND)
            self.end_headers()
            excinfo = "%s" % traceback.format_exc()
            self.wfile.write(json.dumps(excinfo))

    def handleSetAttr(self, objname, name, value):
        logger.debug('SetAttr %s = %s', name, value)
        if not self.server.attr:
            self.send_response(httplib.FORBIDDEN)
            self.end_headers()
            excinfo = "__setattr__ disabled"
            self.wfile.write(json.dumps(excinfo))
            return
        obj = self.server.getSharedObject(objname)
        setattr(obj, name, value)
        self.send_response(httplib.OK)
        self.end_headers()


class CobraHttpDaemon(ThreadingTCPServer):
    def __init__(self, host="", port=COBRA_PORT, sslcrt=None, sslkey=None, sslca=None, sess_timeout=24, attr=True):
        '''
        Construct a cobra daemon object.

        Parameters:
        host        - Optional hostname/ip to bind the service to (default: inaddr_any)
        port        - The port to bind (Default: COBRA_PORT)
        timeout     - The length any session can last, before forcing reconnect
        attr        - Toggle to turn off the ability to set or get attributes

        # SSL Options
        sslcrt / sslkey     - Specify sslcrt and sslkey to enable SSL server side
        sslca               - Specify an SSL CA key to use validating client certs

        '''
        self.shared = {}
        self.host = host
        self.port = port
        self.reflock = RLock()
        self.refcnts = {}
        self.authmod = None
        self.attr    = attr

        self.sessions = {} # authenticated sessions
        self.sess_timeout=sess_timeout*60

        # SSL Options
        self.sslca = sslca
        self.sslcrt = sslcrt
        self.sslkey = sslkey

        if sslcrt and not os.path.isfile(sslcrt):
            raise Exception('CobraDaemon: sslcrt param must be a file!')

        if sslkey and not os.path.isfile(sslkey):
            raise Exception('CobraDaemon: sslkey param must be a file!')

        if sslca and not os.path.isfile(sslca):
            raise Exception('CobraDaemon: sslca param must be a file!')


        #ThreadingTCPServer.__init__(self, (host, port), CobraHttpConnectionHandler)
        ThreadingTCPServer.__init__(self, (host, port), CobraHttpRequestHandler)

        t = Thread(target=self._timeoutSessions)
        t.setDaemon(1)
        t.start()

        if port == 0:
            self.port = self.socket.getsockname()[1]

        self.daemon_threads = True
        self.recvtimeout = None

    def _timeoutSessions(self):
        while True:
            time.sleep( self.sess_timeout  )
            for key, (authinfo, tstamp) in self.sessions.items():
                if time.time()-tstamp > self.sess_timeout:
                    self.sessions.pop(key)

    def fireThread(self):
        thr = Thread(target=self.serve_forever)
        thr.setDaemon(True)
        thr.start()

    def setAuthModule(self, authmod):
        '''
        Enable an authentication module for this server
        ( all connections *must* be authenticated through the authmod )

        NOTE: See cobra.auth.* for various auth module implementations

        Example:
            import cobra.auth.shadow as c_a_shadow
            authmod = c_a_shadow.ShadowFileAuth('passwdfile.txt')
            cdaemon = CobraDaemon()
            cdaemon.setAuthModule()
        '''
        self.authmod = authmod

    def getSharedObject(self, name):
        return self.shared.get(name, None)

    def shareObject(self, obj, name=None, doref=False):
        """
        Share an object in this cobra server.  By specifying
        doref=True you will let CobraProxy objects decide that
        the object is done and should be un-shared.  Also, if
        name is None a random name is chosen.

        Returns: name (or the newly generated random one)
        """
        refcnt = None
        if doref:
            refcnt = 0
        if name is None:
            raise Exception("You must specify an object name to share!")

        self.shared[name] = obj
        if doref:
            raise Exception("CobraHttp doesnt do refcnt")
        return name


class CobraHttpProxy:
    """
    A proxy object for remote objects shared with Cobra

    A few optional keyword arguments are handled by all cobra protocols:
        timeout     - Socket timeout for a cobra socket
        authinfo    - A dict, probably like {'user':'username','passwd':'mypass'}
                      ( but it can be auth module specific )
        retrymax    - Maximum number of times to try and reconnect to the HTTP server

    Additional keyword arguments may depend on protocol.

    http://
        Only the standard args

    https://
        sslca           - File path to a CA certs file.  Causes server validation.
        sslcrt / sslkey - Client side cert info

    """
    def __init__(self, URI, retrymax=None, timeout=None, **kwargs):

        scheme, host, port, name, urlparams = c_cobra.chopCobraUri(URI)
        logger.debug('Host: %s, Port: %s, Obj: %s', host, port, name)
        self._cobra_uri = URI
        self._cobra_scheme = scheme
        self._cobra_host = host
        self._cobra_port = port
        self._cobra_slookup = (host, port)
        self._cobra_name = name
        self._cobra_timeout = timeout
        self._cobra_kwargs = kwargs
        self._cobra_gothello = False
        self._cobra_sessid = None

        if kwargs.get('sslkey') and not os.path.isfile(kwargs.get('sslkey')):
            raise Exception('CobraProxy: sslkey must be a file!')

        if kwargs.get('sslcrt') and not os.path.isfile(kwargs.get('sslcrt')):
            raise Exception('CobraProxy: sslcrt must be a file!')

        if kwargs.get('sslca') and not os.path.isfile(kwargs.get('sslca')):
            raise Exception('CobraProxy: sslca must be a file!')

        csock = self._cobra_http_getsock()

        data = CobraHttpMethod(self, '__cobra_hello')()

        self._cobra_gothello = True
        self._cobra_methods = data

    def _cobra_http_getsock(self):
        thr = currentThread()
        tsocks = getattr(thr, 'cobrahttpsocks', None)
        if tsocks is None:
            tsocks = {}
            thr.cobrahttpsocks = tsocks

        sock = tsocks.get(self._cobra_slookup)
        if not sock or sock.trashed:
            # Lets build a new socket... shall we?
            sock = self._cobra_http_newsock()

            # If we have authinfo lets authenticate
            authinfo = self._cobra_kwargs.get('authinfo')
            if authinfo is not None:
                sock.authUser(authinfo)

            tsocks[self._cobra_slookup] = sock
        return sock

    def __getattr__(self, name):
        logger.debug('GetAttr: %s', name)
        if name == "__getinitargs__":
            raise AttributeError()
        # Handle methods
        if self._cobra_methods.get(name, False):
            return CobraHttpMethod(self, name)

        return CobraHttpMethod(self, '__cobra_getattr')(name)

    def __setattr__(self, name, value):
        logger.debug('SetAttr: %s = %s', name, value)
        if name.startswith('_cobra_'):
            self.__dict__[name] = value
            return

        return CobraHttpMethod(self, '__cobra_setattr')(name, value)

    def _cobra_http_newsock(self):
        """
        This is only used by *clients*
        """
        if self._cobra_scheme == 'http':
            return CobraHttpClient( CobraHttpFactory(host=self._cobra_host, port=self._cobra_port, timeout=self._cobra_timeout, factory=httplib.HTTPConnection), _cobra_name=self._cobra_name )
        else:
            return CobraHttpClient( CobraHttpFactory(host=self._cobra_host, port=self._cobra_port, timeout=self._cobra_timeout, key_file=self._cobra_kwargs.get('sslkey'), cert_file=self._cobra_kwargs.get('sslcrt'), factory=httplib.HTTPSConnection), _cobra_name=self._cobra_name )

class CobraHttpFactory:
    '''
    Cobra HTTP wrapper for HTTP connection
    '''
    def __init__(self, *args, **kwargs):
        self.http = kwargs.pop('factory')
        self.kwargs = kwargs
        self.args = args

    def __call__(self):
        return self.http(*self.args, **self.kwargs)


class CobraHttpClient:
    '''
    Wrapper for HTTP client uses Cobra web services protocol
    '''
    def __init__(self, httpfact, _cobra_name, retrymax=cobra_retrymax):
        self.httpfact = httpfact
        self.retries = 0
        self.trashed = False
        self.retrymax = retrymax
        self._cobra_name = _cobra_name
        self._cobra_sessid = None # stores our session id
        self.authinfo = None

        self.conn = httpfact()

        self.connected = True

    def authUser(self, authinfo):
        body = urllib.quote(json.dumps({'kwargs': authinfo}))
        self.conn.request("POST", "/%s/__cobra_login" %  self._cobra_name, body)

        resp = self.conn.getresponse()
        if resp.status != httplib.OK:
            raise CobraHttpException("Access Denied")

        cookie = resp.getheader('set-cookie')
        if cookie:
            self._cobra_sessid = cookie
            self.authinfo = authinfo

    def _cobra_http_geturi(self, methname, *args, **kwargs):
        uri = "/%s/%s?args=%s" % (self._cobra_name, methname, urllib.quote(json.dumps(args)))
        if kwargs:
            uri += "&kwargs=%s" % urllib.quote(json.dumps(kwargs))
        return uri

    def reConnect(self):
        while self.retrymax is None or self.retries < self.retrymax:
            logger.info('Cobra reconnection attempt')
            try:
                self.conn = self.httpfact()
                if self._cobra_sessid:
                    self.authUser(self.authinfo)
                self.retries = 0
                return
            except Exception as e:
                time.sleep(2 ** self.retries)
                self.retries += 1
        self.trashed = True

        raise CobraHttpException('Retry Exceeded!')

    def cobraHttpTransaction(self, methname, data):
        args, kwargs = data
        url = self._cobra_http_geturi(methname, *args, **kwargs)
        headers = {}

        while True:
            if self._cobra_sessid:
                headers['cookie'] = self._cobra_sessid
            self.conn.request("GET", url, headers=headers)
            resp = self.conn.getresponse()

            if resp.status == httplib.NOT_FOUND:
                exc = json.loads( resp.read())
                raise CobraHttpException(exc)

            if resp.status == httplib.UNAUTHORIZED and self._cobra_sessid:
                self.reConnect()
                continue
            if resp.status == httplib.UNAUTHORIZED:
                self.trashed = True
                raise CobraHttpException("Access Denied")
            if resp.status == httplib.INTERNAL_SERVER_ERROR:
                exc = json.loads( resp.read())
                raise CobraHttpException(exc)
            if resp.status == httplib.BAD_REQUEST:
                exc = json.loads( resp.read())
                raise CobraHttpException(exc)
            if resp.status == httplib.FORBIDDEN:
                exc = json.loads( resp.read())
                raise CobraHttpException(exc)

            data = resp.read()
            if data:
                return json.loads(data)
            return None

class CobraHttpMethod:
    def __init__(self, proxy, methname):
        self.proxy = proxy
        self.methname = methname

    def __call__(self, *args, **kwargs):
        name = self.proxy._cobra_name
        logger.debug('Calling %s:%s,(%s, %s)', name, self.methname, repr(args)[:20], repr(kwargs)[:20])
        sock = self.proxy._cobra_http_getsock()
        return sock.cobraHttpTransaction(self.methname, (args,kwargs))
