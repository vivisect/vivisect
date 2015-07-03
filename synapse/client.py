import time
import threading

from urllib.parse import urlparse

import synapse.lib.socket as s_socket

class SynClient:

    def __init__(self, sockaddr, **info):
        info.setdefault('retries', 3)       # reconnect tries before exc
        #info.setdefault('keyfile', None)
        info.setdefault('timeout', None)    # set the sock recv timeout
        info.setdefault('sockper', False)   # form a connection for each call

        info.setdefault('backmax', 2)       # max back off during retry loop
        info.setdefault('backoff', 0.1)     # back off delta for retry loop

        info['sockaddr'] = sockaddr

        self._syn_info = info
        self._syn_sock = None
        self._syn_shut = False
        self._syn_lock = threading.Lock()

    def synFini(self):
        '''
        Shutdown and release resources for the SynClient.
        '''
        with self._syn_lock:
            self._syn_shut = True
            self._synShutSock()

    def synGetInfo(self, prop):
        '''
        Retrieve an info property from the SynClient.
        '''
        return self._syn_info.get(prop)

    def synSetInfo(self, prop, valu):
        '''
        Set an info property on the SynClient.
        '''
        self._syn_info[prop] = valu

    def synPingServ(self):
        t = time.time()
        msg = self._synFireTrans('syn:ping')
        msg[1]['rtt'] = time.time() - t
        self._synCheckMsg(msg,'syn:ping:ret')
        return msg

    def _synShutSock(self):
        # only call this with the lock!
        if self._syn_sock != None:
            self._syn_sock.close()
        self._syn_sock = None

    def _synSockPerTrans(self, name, info):
        sock = self._synNewSock()
        try:
            sock.sendmsg( (name,info) )
            return sock.recvmsg()
        finally:
            sock.close()

    def _synFireTrans(self, name, **info):

        if self._syn_info.get('sockper'):
            return self._synSockPerTrans(name,info)

        tries = 0
        sleep = 0
        with self._syn_lock:

            if self._syn_shut:
                raise s_socket.SocketClosed()

            while True:
                try:

                    if self._syn_sock == None:
                        self._syn_sock = self._synNewSock()

                    self._syn_sock.firemsg(name,**info)

                    return self._syn_sock.recvmsg()

                except s_socket.SocketClosed as e:
                    self._synShutSock()
                    tries += 1
                    if tries > self._syn_info.get('retries'):
                        raise

                    time.sleep(sleep)
                    backoff = self._syn_info.get('backoff')
                    backmax = self._syn_info.get('backmax')
                    sleep = min( sleep + backoff, backmax )

    def _synCheckMsg(self, msg, name):
        if msg[0] == 'syn:err':
            raise Exception( msg[1].get('msg') )

        if msg[0] != name:
            raise Exception('Invalid Message: %s (wanted:%s)' % (msg[0],name))

    def _synNewSock(self):
        '''
        Create a new synapse socket connected to the server sockaddr.
        '''
        sock = s_socket.Socket()
        sock.connect( self.synGetInfo('sockaddr') )
        sock.settimeout( self.synGetInfo('timeout') )
        return sock

class SynRemoteException(Exception):pass

class SynMeth:

    def __init__(self, proxy, objname, methname):
        self.proxy = proxy
        self.objname = objname
        self.methname = methname

    def __call__(self, *args, **kwargs):
        msginfo = {
            'obj':self.objname,
            'meth':self.methname,

            'args':args,
            'kwargs':kwargs,
        }
        msg = self.proxy._synFireTrans('syn:obj:call', **msginfo)
        if msg[0] == 'syn:obj:call:ret':
            return msg[1].get('retval')

        if msg[0] == 'syn:obj:call:exc':
            raise SynRemoteException( msg[1].get('exc') )

        raise Exception(repr(msg))

class SynProxy(SynClient):
    '''
    A SynProxy may be used access objects methods published by a SynServer.

    Example:

        foo = SynProxy(sockaddr,'foo')

    '''
    def __init__(self, sockaddr, objname, **info):
        info['objname'] = objname
        SynClient.__init__(self, sockaddr, **info)

        msg = self._synFireTrans('syn:obj:meths',objname=objname)
        self._synCheckMsg(msg,'syn:obj:meths:ret')

        retval = msg[1].get('retval')
        if retval == None:
            raise Exception('No Shared Object: %s' % (name,))

        # FIXME doc strings and such retrieved?

        for methname in retval:
            meth = SynMeth(self, objname, methname )
            setattr(self,methname,meth)

#class SynAsyncProxy:
    #'''
    #A SynAsyncProxy is a SynProxy for use with asynchronous calls.
    #'''
