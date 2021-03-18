'''
A utility for creating "remote applications" which are dcode
enabled and cobra driven.  All API arguments/returns *must* be
serializable using msgpack.

NOTE: enabling a dcode server means source for local python modules
      will be delivered directly to clients over the network!

Running a remote application will also attempt to prefer code from
the server rather than the local python current working directory.
( and uses multiprocessing for import/process isolation )
'''
import os
import sys
import importlib
import subprocess
import multiprocessing

import cobra
import cobra.dcode


class RemoteAppServer:
    def __init__(self):
        pass


def shareRemoteApp(name, appsrv=None, daemon=None, port=443):
    '''
    Fire an appropriate dcode enabled cobra daemon and share
    the appsrv object with the given name.
    '''
    if appsrv is None:
        appsrv = RemoteAppServer()

    if daemon is None:
        daemon = cobra.CobraDaemon(msgpack=True, port=port)
        daemon.fireThread()

    cobra.dcode.enableDcodeServer(daemon=daemon)
    return daemon.shareObject(appsrv, name)


def getAndRunApp(uri):
    # We dont want our *local* code, we want the remote code.
    cwd = os.getcwd()
    if cwd in sys.path:
        sys.path.remove(cwd)
    if '' in sys.path:
        sys.path.remove('')

    duri = cobra.swapCobraObject(uri, 'DcodeServer')
    cobra.dcode.addDcodeUri(duri)

    server = cobra.CobraProxy(uri, msgpack=True)
    scheme, host, port, name, urlparams = cobra.chopCobraUri(uri)

    module = importlib.import_module(name)

    if hasattr(module, 'remotemain'):
        module.remotemain(server)
    else:
        module.main()


def runRemoteApp(uri, join=True):
    p = multiprocessing.Process(target=getAndRunApp, args=(uri,))
    p.start()
    if join:
        p.join()


def execRemoteApp(uri):
    '''
    Exec a remoteapp without using multiprocessing (may be needed if fork()
    causes the child to have an unacceptably dirty environment)
    '''
    subprocess.Popen([sys.executable, '-m', 'cobra.remoteapp', uri])


def main():
    runRemoteApp(sys.argv[1])


if __name__ == '__main__':
    sys.exit(main())
