import sys
import errno
import subprocess

import vtrace

def waitForTest():
    sys.stdout.write('testwait\n')
    sys.stdout.flush()
    while True:
        line = sys.stdin.readline().strip()
        if line == 'testmod':
            break

def safeReadline():
    while True:
        try: # Crazy loop for freebsd readline failure
            r = sys.stdin.readline()
            break
        except IOError as e:
            if e.errno == errno.EINTR:
                continue
            raise
    return r

class SkipTest(Exception):
    pass

class TestModule:

    def __init__(self):
        pass

    def prepTest(self):
        pass

    def runTest(self):
        pass

    def skipTest(self, msg):
        raise SkipTest(msg)

    def cleanTest(self):
        pass

class VtracePythonTest(TestModule):
    '''
    An "easy" test module which executes a python interpreter
    with the given "main" module.  The runTest method should
    assume the process is attached as self.trace.
    '''
    modname = 'FIXME'

    def __init__(self):
        TestModule.__init__(self)
        self.trace = None

    def prepTest(self):
        self.trace = vtrace.getTrace()
        self.trace.execute('%s -m %s' % (sys.executable, self.modname))
        self.trace.requireAttached()

    def cleanTest(self):
        if self.trace.isAttached():
            self.trace.kill()
        self.trace.release()

class VtracePythonProcTest(TestModule):
    modname = 'FIXME'
    def __init__(self):
        TestModule.__init__(self)
        self.proc = None
        self.trace = None

    def prepTest(self):
        self.proc = subprocess.Popen([ sys.executable, '-m', self.modname ], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        assert(self.proc.stdout.readline().strip() == 'testwait')
        self.trace = vtrace.getTrace()
        self.trace.attach( self.proc.pid )

    def runProcess(self):
        self.proc.stdin.write('testmod\n')
        self.trace.run()

    def cleanTest(self):
        try:
            self.proc.wait(timeout=120)
        except subprocess.TimeoutExpired:
            pass
        finally:
            self.proc.stdin.close()
            self.proc.stdout.close()
            self.proc.kill()
        self.trace.release()
