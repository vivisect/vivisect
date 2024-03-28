import os
import sys
import time
import unittest
import subprocess

import vtrace

import envi.tests as e_test


class VtraceProcessTest(unittest.TestCase):

    pypath = os.path.join('vtrace', 'tests', 'mains', 'main.py')

    @e_test.skip('darwin')
    def setUp(self):
        self.exitrun = False
        self.proc = subprocess.Popen([sys.executable, self.pypath], stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
        assert(self.proc.stdout.readline().strip() == 'testwait')
        self.trace = vtrace.getTrace()
        self.trace.attach(self.proc.pid)

    def tearDown(self):
        retry = 0
        while retry < 5:
            if not self.exitrun and self.trace.isAttached():
                self.trace.setMode('RunForever', True)
                self.proc.stdin.write('testmod\n')
                self.proc.stdin.flush()
                self.trace.run()
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                pass
            finally:
                retry += 1

        if self.proc.returncode is None:
            # FINE. shoot the process and keep going. Ain't nobody got time for that.
            self.proc.kill()
        try:
            self.proc.stdout.close()
            self.proc.stdin.close()
        except:
            pass
        self.trace.release()

    def runProcess(self):
        self.trace.setMode('RunForever', True)
        self.trace.setMode('NonBlocking', True)
        self.proc.stdin.write('testmod\n')
        self.proc.stdin.flush()
        self.trace.run()

    def runUntilExit(self):
        self.exitrun = True
        self.trace.setMode('RunForever', True)
        self.trace.setMode('NonBlocking', False)
        self.proc.stdin.write('testmod\n')
        self.proc.stdin.flush()
        self.trace.run()
        time.sleep(1)

        self.assertEqual(self.trace.getMeta('ExitCode'), 33)


class VtraceExecTest(VtraceProcessTest):

    pypath = os.path.join('vtrace', 'tests', 'mains', 'mainexec.py')

    @e_test.skip('darwin')
    def setUp(self):
        self.exitrun = False
        self.trace = vtrace.getTrace()
        self.trace.execute('%s %s' % (sys.executable, self.pypath))
        self.trace.requireAttached()

    def tearDown(self):
        if self.trace.isAttached():
            self.trace.setMode('RunForever', True)
            self.trace.setMode('NonBlocking', False)
            self.trace.run()
        self.trace.release()

    def runUntilExit(self):
        self.exitrun = True
        self.trace.setMode('RunForever', True)
        self.trace.setMode('NonBlocking', False)
        self.trace.run()

        self.assertEqual(self.trace.getMeta('ExitCode'), 33)

    def runProcess(self):
        self.trace.setMode('RunForever', True)
        self.trace.setMode('NonBlocking', True)
        self.trace.run()
