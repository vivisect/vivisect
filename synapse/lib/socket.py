'''
Synapse extensible/hookable sockets.
'''
import socket
import msgpack
import selectors
import traceback

import synapse.lib.common as s_common
import synapse.lib.threads as s_threads
import synapse.event.dist as s_eventdist

class SocketError(Exception):pass
class SocketClosed(SocketError):pass

class Socket(s_eventdist.EventDist):
    '''
    An extensible socket object.

    Event Names:
    connected       - the socket is newly connected
    datasent        - the socket returned from sending data
    datarecvd       - the socket returned from recieving data
    disconnected    - the socket connection has terminated
    '''
    def __init__(self, sock=None):
        if sock == None:
            sock = socket.socket()
        self.sock = sock
        s_eventdist.EventDist.__init__(self)

    def connect(self,sockaddr):
        self.sock.connect(sockaddr)
        self.synFireEvent('connected',{'sockaddr':sockaddr,'sock':self})

    def fileno(self):
        return self.sock.fileno()

    def recv(self, size=None):
        buf = self.realrecv(size)
        self.synFireEvent('datarecvd',{'size':size,'buf':buf,'sock':self})
        return buf

    def send(self, buf):
        sent = self.realsend(buf)
        self.synFireEvent('datasent',{'sent':sent,'buf':buf,'sock':self})
        return sent

    def emit(self, obj):
        '''
        Use msgpack to serialize an object to the socket.

        Example:
            x = (1,2,3,'qwer')
            sock.emit(x)
        '''
        self.sendall( msgpack.packb(obj,use_bin_type=True) )

    def realsend(self, buf):
        try:
            return self.sock.send(buf)
        except socket.error as e:
            raise SocketClosed()

    def shutdown(self, how):
        self.sock.shutdown(how)

    def close(self):
        self.sock.close()

    def teardown(self):
        try:
            self.sock.shutdown(socket.SHUT_RD)
        except Exception as e:
            print('teardown shutdown: %s' % e)

        try:
            self.sock.close()
        except Exception as e:
            print('teardown close: %s' % e)

    def realrecv(self, size):
        try:
            return self.sock.recv(size)
        except socket.error as e:
            raise SocketClosed()

    def sendall(self, buf):
        sent = 0
        size = len(buf)
        while sent < size:
            off = self.send(buf)
            sent += off

    def recvall(self, size):
        buf = b''
        while len(buf) < size:
            x = self.recv(size-len(buf))
            if not x:
                raise SocketClosed()
            buf += x
        return buf

    # socket API pass throughs...
    def settimeout(self, t):
        self.sock.settimeout(t)

class Server(s_eventdist.EventQueue):
    '''
    A socket server using multiplexed IO and EventDist.
    '''

    def __init__(self, sockaddr, pool=10, timeout=None):
        self.sock = socket.socket()
        self.srvthr = None
        self.seltor = None
        self.wakesock = None
        self.srvshut = False
        self.timeout = timeout
        self.sockaddr = sockaddr
        s_eventdist.EventQueue.__init__(self,pool=pool)

    def synShutDown(self):
        self.srvshut = True
        self.sock.close()
        self.wakesock.close()
        self.seltor.close()
        self.srvthr.join()
        s_eventdist.EventQueue.synShutDown(self)

    def synRunServer(self):
        self.sock.bind( self.sockaddr )
        self.sockaddr = self.sock.getsockname()
        self.sock.listen(100)

        self.srvthr = s_threads.fireWorkThread(self._runServerLoop)
        return self.sockaddr

    def synWaitServer(self):
        '''
        Wait for the server to terminate ( but do not instruct it to ).
        '''
        self.srvthr.join()

    def synGetServAddr(self):
        return self.sockaddr

    def _runServerLoop(self):

        self.seltor = selectors.DefaultSelector()
        key = self.seltor.register(self.sock, selectors.EVENT_READ)

        self.wakesock,s2 = socketpair()
        self.seltor.register(s2, selectors.EVENT_READ)

        #s1,s2 = socket.socketpair()
        # stuff a socket into the selector to wake on close

        while True:

            for key,events in self.seltor.select():

                if self.srvshut:
                    break

                if key.data == None:
                    conn,sockaddr = key.fileobj.accept()
                    # TIMEOUT
                    sock = Socket(conn)

                    unpacker = msgpack.Unpacker(use_list=False,encoding='utf8')
                    sockdata = {'sock':sock,'unpacker':unpacker,'serv':self,'sockaddr':sockaddr}

                    self.seltor.register(conn, selectors.EVENT_READ, data=sockdata)
                    continue

                sock = key.data['sock']
                buf = sock.recv(102400)
                if not buf:
                    self.seltor.unregister(key.fileobj)
                    self.synFireEvent('sockshut',key.data)
                    key.fileobj.close()
                    continue
                    
                unpk = key.data['unpacker']

                unpk.feed(buf)
                for msg in unpk:
                    evtinfo = {'msg':msg}
                    evtinfo.update( key.data )
                    self.synFireEvent('sockmsg',evtinfo)

            if self.srvshut:
                s2.close()
                self.synFireEvent('shutdown',{})
                return

    def synGetServAddr(self):
        '''
        Retrieve a tuple of (host,port) for this server.

        NOTE: the "host" part is the return value from
              socket.gethostname()
        '''
        host = socket.gethostname()
        return (host,self.sockaddr[1])

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

