import time
import vivisect
import vivisect.cli as viv_cli
import vivisect.qt.main as viv_qt_main

def remotemain(appsrv):

    # The "appsrv" is a remote workspace...
    vw = viv_cli.VivCli()
    vw.initWorkspaceClient(appsrv)

    # If we are interactive, lets turn on extended output...
    vw.verbose = True
    viv_qt_main.main(vw)

