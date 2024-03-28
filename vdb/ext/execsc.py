import sys
import shlex

import vtrace


class ShellcodeLoadNotifier(vtrace.Notifier):
    def __init__(self, db, fname):
        self.db = db
        self.fname = fname

    def notify(self, event, trace):
        if event != vtrace.NOTIFY_BREAK:
            return

        bytez = None
        with open(self.fname, 'rb') as f:
            bytez = f.read()

        va = trace.allocateMemory(len(bytez))
        trace.writeMemory(va, bytez)

        self.db.vprint('Loaded shellcode at address: 0x%x' % va)

        trace.setProgramCounter(va)
        trace.addBreakByAddr(va)

        self.db.deregisterNotifier(vtrace.NOTIFY_BREAK, self)


def execsc(db, line):
    '''
    Load and execute shellcode stub from file

    Usage: execsc <fname>
    '''
    argv = shlex.split(line)
    if len(argv) != 1:
        return db.do_help('execsc')

    cmd = sys.executable
    trace = db.newTrace()
    db.vprint('Executing %s' % cmd)

    sc = ShellcodeLoadNotifier(db, argv[0])
    db.registerNotifier(vtrace.NOTIFY_BREAK, sc)

    trace.execute(cmd)


def vdbExtension(vdb, trace):
    vdb.registerCmdExtension(execsc)
