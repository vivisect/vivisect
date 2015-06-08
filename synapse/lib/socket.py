'''
Synapse extensible/hookable sockets.
'''
import time
import types
import socket
import msgpack
import selectors
import traceback

import synapse.lib.common as s_common
import synapse.event.dist as s_evtdist
import synapse.lib.threads as s_threads

class SocketError(Exception):pass
class SocketClosed(SocketError):pass

class Socket(s_evtdist.EventDist):
    '''
    An extensible socket object.
    '''
    def __init__(self, sock=None):
        if sock == None:
            sock = socket.socket()

        self.sock = sock

        self._sock_info = {
            'unpacker':msgpack.Unpacker(use_list=False,encoding='utf8')
        }

        s_evtdist.EventDist.__init__(self)

    def getSockInfo(self, prop, default=None):
        '''
        Returns a socket metadata property by name.

        Example:

            woot = sock.getSockInfo('woot')

        '''
        return self._sock_info.get(prop,default)

    def setSockInfo(self, prop, valu):
        '''
        Store a socket metadata prop=valu for later use.

        Example:

            sock.setSockInfo('woot',20)

        '''
        self._sock_info[prop] = valu

    def connect(self, sockaddr):
        '''
        Connect the socket to a remote sockaddr.
        ( API compatible with python socket object )

        Example:

            sock.connect( ('127.0.0.1',8989) )

        '''
        self.sock.connect(sockaddr)
        self.fire('sock:conn', sock=self, sockaddr=sockaddr)

    def accept(self):
        '''
        Accept a new connection on a listening socket.
        ( API compatible with python socket object )

        Example:

            newsock = sock.accept()

        '''
        s,addr = self.sock.accept()

        sock = Socket(s)
        self.fire('sock:accept', sock=self, newsock=sock)

        sock.fire('sock:conn', sock=sock)
        return sock

    def fileno(self):
        '''
        Retrieve the file descriptor number for the socket.
        ( API compatible with python socket object )

        Example:

            i = sock.fileno()

        '''
        return self.sock.fileno()

    def recv(self, size=None):
        '''
        Recieve transmitted bytes on the socket.
        ( API compatible with python socket object )

        Example:

            byts = sock.recv(30)

        '''
        byts = self._sock_recv(size)
        self.fire('sock:rx', size=size, byts=byts, sock=self)
        return byts

    def send(self, byts):
        sent = self._sock_send(byts)
        self.fire('sock:tx', sent=sent, byts=byts, sock=self)
        return sent

    def sendmsg(self, obj):
        '''
        Use msgpack to serialize an object to the socket.

        Example:
            x = (1,2,3,'qwer')
            sock.sendmsg(x)
        '''
        try:
            self.sendall( msgpack.packb(obj,use_bin_type=True) )
            return True

        except SocketError as e:
            return False

    def firemsg(self, name, **kwargs):
        '''
        Construct and send a (name,info) message tuple.

        Example:
            sock.firemsg('woot',val=10)
        '''
        self.sendmsg( (name,kwargs) )

    def recvmsg(self):
        '''
        Receive a single msgpack (name,info) message tuple.

        Example:

            msg = sock.recvmsg()

        Notes:

            * this API must be *only* used when the whole socket
              is msgpack.  Intermingling msgs and arbitrary data
              is not supported in this API.

        '''
        for msg in self.itermsgs():
            return msg

    def _sock_send(self, byts):
        try:
            return self.sock.sendall(byts)
        except OSError as e:
            raise SocketClosed()

    def shutdown(self, how):
        self.sock.shutdown(how)
        self.fire('sock:shut', sock=self)

    def close(self):
        self.sock.close()

    def teardown(self):

        if not self.getSockInfo('listen'):
            try:
                self.sock.shutdown(socket.SHUT_WR)
            except Exception as e:
                print('teardown shutdown: %s' % e)

        try:
            self.sock.close()
        except Exception as e:
            print('teardown close: %s' % e)

        self.fire('sock:shut', sock=self)

    def _sock_recv(self, size):
        try:
            return self.sock.recv(size)
        except OSError as e:
            raise SocketClosed()

    def sendall(self, byts):
        # our send() *is* sendall()
        return self.send(byts)

    def recvall(self, size):
        byts = b''
        remain = size
        while remain:
            x = self.recv(size-len(byts))
            if not x:
                raise SocketClosed()
            byts += x
            remain -= len(x)
        return byts

    def itermsgs(self):
        unpk = self.getSockInfo('unpacker')
        for msg in unpk:
            yield msg

        while True:
            byts = self.recv(1024000)
            if not byts:
                break

            unpk.feed(byts)
            for msg in unpk:
                yield msg

    # socket API pass throughs...
    def settimeout(self, t):
        self.sock.settimeout(t)

class Plex(s_evtdist.EventDist):
    '''
    Manage multiple Sockets using a multi-plexor IO thread.
    '''
    def __init__(self):
        s_evtdist.EventDist.__init__(self)

        self._plex_sel = selectors.DefaultSelector()
        self._plex_shut = False
        self._plex_socks = set()

        self._plex_wake, self._plex_s2 = socketpair()

        self._plex_thr = s_threads.fireWorkThread( self._plexMainLoop )

        self.on('sock:conn', self._on_sockconn)
        self.on('sock:shut', self._on_sockshut)
        self.on('sock:accept', self._on_sockaccept)

    def connect(self, host, port):
        '''
        Create and connect a new TCP Socket within the Plex.

        Example:

            plex = Plex()
            plex.connect(host,port)

        '''
        sock = Socket()
        sock.link(self)
        sock.connect( (host,port) )

    def listen(self, host='0.0.0.0', port=0):
        '''
        Create and bind a new TCP Server within the Plex.

        Example:

            plex = Plex()
            sockaddr = plex.listen(port=3333)

        Notes:

            * if port=0, an OS chosen ephemeral port will be used

        '''

        s = socket.socket()
        s.bind( (host,port) )
        s.listen( 100 )

        port = s.getsockname()[1]

        sock = Socket(s)
        sock.setSockInfo('listen', True)

        sock.link( self )

        self._sock_on( sock )
        return s.getsockname()

    def wrap(self, s):
        sock = Socket(s)
        sock.link(self)
        sock.fire('sock:conn', sock=sock)
        return sock

    #def sock(self, sock):

    #def addPlexSock(self, sock, listen=False):
        #'''
        #Add a socket to the multiplexor.
#
        #Example:
#
            #plex.addPlexSock( sock )
#
        #Use listen=True when adding a listening socket which should
        #call accept() on read events.
#
        #'''
        #sock = Socket(sock)
        #sock.info('listen',listen)
        #self._init_plexsock( sock )
#
    #def runPlexMain(self, thread=False):
        #if thread:
             #s_threads.fireWorkThread( self.runPlexMain, thread=False )

    def _on_sockaccept(self, event):
        sock = event[1].get('newsock')
        sock.link( self )

    def _on_sockconn(self, event):
        sock = event[1].get('sock')
        self._sock_on(sock)

    def _on_sockshut(self, event):
        sock = event[1].get('sock')
        self._sock_off(sock)

    def _sock_off(self, sock):
        self._plex_sel.unregister(sock)
        self._plex_socks.remove(sock)
        self._plexWake()

    def _sock_on(self, sock):

        unpacker = msgpack.Unpacker(use_list=False, encoding='utf8')
        sock.setSockInfo('unpacker', unpacker)

        self._plex_sel.register(sock, selectors.EVENT_READ)
        self._plex_socks.add(sock)
        self._plexWake()

    def _plexWake(self):
        self._plex_wake.sendall(b'\x00')

    def _plexMainLoop(self):

        self._plex_sel.register( self._plex_s2, selectors.EVENT_READ )

        while True:

            for key,events in self._plex_sel.select(timeout=1):

                if self._plex_shut:
                    break

                sock = key.fileobj
                if sock == self._plex_s2:
                    sock.recv(1024)
                    continue

                if sock.getSockInfo('listen'):
                    # his sock:conn event handles reg
                    sock.accept()
                    continue

                byts = sock.recv(102400)

                if not byts:
                    # his sock:shut handles unreg
                    sock.teardown()
                    continue

                unpk = sock.getSockInfo('unpacker')

                unpk.feed( byts )

                for msg in unpk:
                    sock.fire('sock:msg', plex=self, msg=msg, sock=sock)

            if self._plex_shut:
                break

        self._plex_s2.close()
        for sock in list(self._plex_socks):
            sock.teardown()

        self._plex_sel.close()

    def fini(self):
        self._plex_shut = True
        self._plex_wake.close()
        self._plex_thr.join()

def _sockpair():
    s = socket.socket()
    s.bind(('127.0.0.1',0))
    s.listen(1)

    s1 = socket.socket()
    s1.connect( s.getsockname() )

    s2 = s.accept()[0]

    s.close()
    return s1,s2

def socketpair():
    '''
    Standard sockepair() on posix systems, and pure shinanegans on windows.
    '''
    try:
        return socket.socketpair()
    except AttributeError as e:
        return _sockpair()

def connect(host,port):
    '''
    Instantiate a Socket and connect to the given host:port.
    '''
    sock = Socket()
    sock.connect( (host,port) )
    return sock

