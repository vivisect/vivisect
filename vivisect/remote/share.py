import cobra.dcode
import cobra.remoteapp

def shareWorkspace(vw, doref=False):
    daemon = cobra.CobraDaemon('', 0, msgpack=True)
    daemon.fireThread()
    cobra.dcode.enableDcodeServer(daemon=daemon)
    cobra.remoteapp.shareRemoteApp('vivisect.remote.client', appsrv=vw, daemon=daemon)
    return daemon
