
import vtrace
import vdb.extensions.windows as vdb_windows

def ethread(db, line):
    '''
    Display information about the currently stopped ethread.

    Usage: ethread
    #FIXME support listing them
    #FIXME support ethread interp arbitrary address
    '''
    t = db.getTrace()
    t.requireNotRunning()
    fsbase = t.getVariable('fsbase')
    kpcr = t.getStruct('nt.KPCR', fsbase)
    ethraddr = kpcr.PrcbData.CurrentThread
    ethr = t.getStruct('nt.ETHREAD', ethraddr)
    db.vprint(ethr.tree(va=ethraddr))

def eprocess(db, line):
    '''
    Display information about the currently stopped eprocess.

    Usage: eprocess
    #FIXME support listing
    #FIXME support eprocess interp address
    '''
    t = db.getTrace()
    t.requireNotRunning()
    fsbase = t.getVariable('fsbase')
    kpcr = t.getStruct('nt.KPCR', fsbase)
    ethraddr = kpcr.PrcbData.CurrentThread
    ethr = t.getStruct('nt.ETHREAD', ethraddr)
    eprocaddr = ethr.Tcb.ApcState.Process
    eproc = t.getStruct('nt.EPROCESS', eprocaddr)
    db.vprint(eproc.tree(va=eprocaddr))

def kpcr(db, line):
    '''
    Show the kpcr structure for the currently stopped kernel.

    Usage: kpcr
    '''
    t = db.getTrace()
    t.requireNotRunning()
    fsbase = t._getVmwareReg('fs')
    kpcr = t.getStruct('nt.KPCR', fsbase)
    db.vprint(kpcr.tree(va=fsbase))

# FIXME do we need to make gdbstub a package so it can have subs?

def armcore(db, line):
    '''
    Show / set the 'mode' of the arm core between arm and thumb.

    Usage: armcore [arm|thumb]
    '''
    t = db.getTrace()
    t.requireNotRunning()

    if line:
        if line not in ('arm','thumb'):
            return db.do_help('armcore')
        cmdstr = t._monitorCommand('arm core_state %s' % line)
    else:
        cmdstr = t._monitorCommand('arm core_state')

    mode = cmdstr.split(':')[1].strip()
    db.vprint('Arm Core Mode: %s' % mode)

class GdbStubNotifier(vtrace.Notifier):

    def __init__(self, db):
        vtrace.Notifier.__init__(self)
        self._db = db

    def notify(self, event, trace):
        if event != vtrace.NOTIFY_ATTACH:
            return

        targarch = trace.getMeta('Architecture')
        gdbplatform = trace.getMeta('GdbPlatform')
        targplatform = trace.getMeta('GdbTargetPlatform')

        #print 'Target Architecture: %s' % targarch
        #print 'Gdb Platform: %s' % gdbplatform
        #print 'Target Platform: %s' % targplatform

        if gdbplatform in ('VMware32','Qemu32'):

            if targplatform == 'Windows':
                self._db.registerCmdExtension(vdb_windows.aslr)
                self._db.registerCmdExtension(vdb_windows.pe)
                self._db.registerCmdExtension(ethread)
                self._db.registerCmdExtension(eprocess)

        elif gdbplatform == 'OpenOCD':

            # If we are openocd, lets add some commands for jtag etc..
            if targarch == 'arm':
                #import vdb.extensions.arm as vdb_arm
                self._db.registerCmdExtension(armcore)
                #self._db.registerCmdExtension(vdb_arm.thumb)

def gdbmon(db, line):
    '''
    Issue a gdb "monitor" command which allows access to the extensions
    inside the gdb stub.

    Example: gdbmon r fs

    (try: "gdbmon help" for info on supported commands in the target stub)
    '''
    if len(line) == 0:
        return db.do_help('gdbmon')
    t = db.getTrace()
    #t.requireNotRunning()
    resp = t._monitorCommand(line)
    db.vprint('gdb> %s' % line)
    db.vprint(resp)

def vdbExtension(db, trace):
    notif = GdbStubNotifier(db)
    db.registerCmdExtension(gdbmon)
    db.registerNotifier(vtrace.NOTIFY_ATTACH, notif)

