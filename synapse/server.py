import time
import types
import socket
import selectors
import traceback

import synapse.lib.queue as s_queue
import synapse.lib.socket as s_socket
import synapse.event.dist as s_evtdist
import synapse.lib.threads as s_threads

class SynServer:
    '''
    A synapse server implementation.

    A SynServer provides access to synapse resources such as async
    eventing, messaging, and remote method invocation.
    '''
    def __init__(self, sockaddr=('0.0.0.0',0) , pool=None, timeout=None):
        self.sock = socket.socket()
        self.srvthr = None
        self.seltor = None
        self.srvshut = False
        self.timeout = timeout
        self.sockaddr = sockaddr

        self.servbus = s_evtdist.EventDist()

        self.servmeths = {}
        self.sharemeths = {}
        self.sockthreads = {}

        self.pool = pool        # also used to check sync/async
        self.poolq = s_queue.Queue()
        self.poolthreads = []

        if pool != None:
            for i in range(pool):
                thr = s_threads.fireWorkThread( self._runPoolThread )
                self.poolthreads.append( thr )

        self.synServMeth('syn:ping', self._meth_synping )
        self.synServMeth('syn:open', self._meth_synopen )
        self.synServMeth('syn:join', self._meth_synjoin )

        self.synServMeth('syn:obj:call', self._meth_synobjcall )
        self.synServMeth('syn:obj:meths', self._meth_synobjmeths )

    def _meth_synping(self, sock, msg):
        sock.firemsg('syn:ping:ret', time=time.time())

    def _meth_synobjmeths(self, sock, msg):
        '''
        Return a list of the shared APIs on a named object.
        '''
        async = msg[1].get('async')
        objname = msg[1].get('objname')
        meths = self.sharemeths.get(objname)
        if meths == None:
            sock.firemsg('syn:obj:meths:ret',retval=None,async=async)
            return

        sock.firemsg('syn:obj:meths:ret',retval=list(meths.keys()),async=async)

    def _runPoolThread(self):
        '''
        The main loop for a pool thread handling msgs.
        '''
        for sock,msg in self.poolq:
            self._runServMeth(sock,msg)

    def synServOn(self, name, meth):
        '''
        Add a synapse event handler to the server.

        Example:

            def newsock(event):
                sock = event[1].get('sock')
                stuff(sock)

            srv.synServOn('sock:conn',newsock)

        '''
        self.servbus.on(name,meth)

    def synServMeth(self, name, meth):
        '''
        Add a method to handle a socket message by name.

        Example:

            def woot(event):
                stuff()

            srv.synServMeth('woot',woot)

        '''
        self.servmeths[name] = meth

    def synShareObj(self, obj, name=None):
        '''
        Share an object via the synapse server.

            foo = FooThing()
            srv.synShareObj( foo, 'foo' )

        Notes:

            * if name is not specified, one is generated and returned

        '''
        if name == None:
            name = s_common.guid()

        meths = {}
        for methname in dir(obj):
            meth = getattr(obj,methname,None)
            if not type(meth) in (types.MethodType, types.BuiltinMethodType, types.FunctionType):
                continue

            meths[methname] = meth

        self.sharemeths[name] = meths
        return name

    def synRevokeObj(self, name):
        '''
        Delete a shared object ( previously shared with synShareObj ).

        Example:

            foo = FooThing()
            name = srv.synShareObj(foo)
            # ... 
            srv.synRevokeObj(name)

        '''
        self.sharemeths.pop(name)

    def _meth_synobjcall(self, sock, msg):
        evt,evtinfo = msg

        args = evtinfo.get('args')      # args for the call
        async = evtinfo.get('async')    # async call id ( if present )
        kwargs = evtinfo.get('kwargs')  # kwargs for the call

        objname = evtinfo.get('obj')     # name of the shared object
        methname = evtinfo.get('meth')     # name of the method

        meths = self.sharemeths.get(objname)
        if meths == None:
            sock.firemsg('syn:err', async=async, msg='no such share: %s' % (objname,))
            return

        meth = meths.get(methname)
        if meth == None:
            sock.firemsg('syn:err', async=async, msg='no such method: %s' % (methname,))
            return

        try:
            ret = meth(*args,**kwargs)
            sock.firemsg('syn:obj:call:ret', async=async, retval=ret)
        except Exception as e:
            exc = traceback.format_exc()
            sock.firemsg('syn:obj:call:exc', exc=exc)

    def _meth_synjoin(self, sock, msg):
        sock.sendmsg( ('syn:err', {'msg':'TODO'}) )

    def _meth_synfire(self, sock, msg):
        sock.sendmsg( ('syn:err', {'msg':'TODO'}) )

    def _meth_synopen(self, sock, msg):
        sock.sendmsg( ('syn:err', {'msg':'TODO'}) )

    def synFiniServer(self):
        '''
        Shut down the Server instance and clean up all sockets/threads.

        Example:

            srv.synFiniServer()

        '''
        self.srvshut = True
        self.synWakeServer()

        if self.seltor != None:
            self.seltor.close()

        self.srvthr.join()
        self.servbus.fini()

        self.poolq.shutdown()
        [ t.join() for t in self.poolthreads ]

        for sock,thr in list(self.sockthreads.items()):
            sock.close()
            thr.join()

    def _runServMeth(self, sock, msg):
        '''
        Execute the method for this message ( or error ).
        '''
        async = msg[1].get('async')
        meth = self.servmeths.get( msg[0] )
        if meth == None:
            errmsg = 'no method: %s' % (msg[0],)
            sock.firemsg('syn:err', async=async, msg=errmsg)
            self._servError(errmsg)
            return

        try:
            meth( sock, msg )
        except Exception as e:
            sock.firemsg('syn:err', async=async, msg=str(e))
            self._servError(str(e))

    def _servError(self, msg, **info):
        self.servbus.fire('serv:error', msg=msg, **info)

    def synRunServer(self):
        '''
        Bind the socket and begin processing connections.
        Returns the sockaddr tuple for the bound address.

        Example:

            addr = srv.sunRunServer()
            # server is running...

        '''
        self.sock.bind( self.sockaddr )
        self.sock.listen(100)

        self.sockaddr = self.sock.getsockname()

        self.srvthr = s_threads.fireWorkThread( self._runMainLoop )
        return self.sockaddr

    def _runMainLoop(self):
        if self.pool != None:
            return self._runPoolLoop()

        self._runThreadLoop()

    def synWaitServer(self):
        '''
        Wait for the server to terminate ( but do not instruct it to ).
        ( mostly useful for cli tools that want to just run a server )

        Example:

            srv.synRunServer()
            srv.synWaitServer()

        '''
        self.srvthr.join()

    def synWakeServer(self):
        sock = socket.socket()
        sock.connect( self.sockaddr )
        sock.close()

    def synGetServAddr(self):
        '''
        Return the sockaddr tuple for the listening socket.

        Example:

            sockaddr = srv.synGetServAddr()

        '''
        return self.sockaddr

    def _runThreadLoop(self):
        '''
        The version of the "main loop" for per-connection threading
        '''
        while True:

            sock,addr = self.sock.accept()
            if self.srvshut:
                sock.close()
                break

            sock = self._initSock(sock,addr)
            self.sockthreads[sock] = s_threads.fireWorkThread( self._runThreadSock, sock )

        self._finiServ()
        return

    def _runThreadSock(self, sock):
        '''
        The thread entry point for per-socket threads ( if not in pool mode )
        '''
        try:

            for msg in sock.itermsgs():
                self._runServMeth(sock,msg)

        # if the socket closes, we're dunzo
        except s_socket.SocketClosed as e:
            pass

        finally:
            self.sockthreads.pop(sock,None)
            self._finiSock(sock)

    def _initSock(self, sock, addr):
        sock.settimeout( self.timeout )
        sock = s_socket.Socket(sock)
        sock.setSockInfo('sockaddr',addr)
        self.servbus.fire('sock:conn', addr=addr, sock=sock)
        return sock

    def _finiSock(self, sock):
        self.servbus.fire('sock:shut', sock=sock)
        sock.close()

    def _finiServ(self):
        self.sock.close()
        self.servbus.fire('serv:shut', serv=self)

    def _runPoolLoop(self):

        self.seltor = selectors.DefaultSelector()
        key = self.seltor.register(self.sock, selectors.EVENT_READ)

        while True:

            for key,events in self.seltor.select():

                if self.srvshut:
                    break

                if key.data == None:
                    conn,addr = key.fileobj.accept()
                    sock = self._initSock(conn,addr)
                    sockdata = {'sock':sock}

                    self.seltor.register(conn, selectors.EVENT_READ, data=sockdata)
                    continue

                sock = key.data['sock']
                byts = sock.recv(102400)
                if not byts:
                    self.seltor.unregister(key.fileobj)
                    self._finiSock(sock)
                    continue
                    
                unpk = sock.getSockInfo('unpacker')

                unpk.feed(byts)
                [ self.poolq.append((sock,m)) for m in unpk ]

            if self.srvshut:
                self._finiServ()
                return

    def synGetServAddr(self):
        '''
        Retrieve a tuple of (host,port) for this server.

        NOTE: the "host" part is the return value from
              socket.gethostname()
        '''
        host = socket.gethostname()
        return (host,self.sockaddr[1])

