'''
Synapse RPC

for the old skewlies, yes, this is cobra... :)
'''
import os
import synapse.socket as s_socket
import synapse.common as s_common

# FIXME WORK IN PROGRESS

class TelepathError(Exception):pass

class NoSuchToken(TelepathError):pass
class NoSuchMethod(TelepathError):pass

class Server(s_socket.Server):

    def __init__(self, sockaddr, pool=10, timeout=None):
        s_socket.Server.__init__(self, *args, **kwargs)
        self.shared = {}
        self.tokens = {}
        self.on( 'sockmsg', self._slot_sockmsg )

    def synShareObject(self, obj, name=None, meths=None):
        '''
        Share an object interface for RPC
        '''
        if name == None:
            name = s_common.guid().decode('ascii')

        self.shared[name] = obj

    def synCallToken(self, token, methname, args, kwargs):
        tok = self.tokens.get(token)
        if tok == None:
            raise NoSuchToken()

        meth = tok.get(methname)
        if meth == None:
            raise NoSuchMethod()

        return meth(*args,**kwargs)


    def _slot_sockmsg(self, evt, evtinfo):
        msg = evtinfo.get('msg')
        sock = evtinfo.get('sock')
