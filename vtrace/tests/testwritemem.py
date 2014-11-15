import os
import sys
import ctypes
import unittest

import vtrace.tests as vt_tests

class VtraceWritememTest(vt_tests.VtraceProcessTest):

    pypath = os.path.join('vtrace','tests','mains','mainwritemem.py')

    def test_vtrace_writemem(self):

        self.runProcess()

        addrstr = self.proc.stdout.readline()
        addr = long( addrstr, 16 )

        testbuf = os.urandom( 10 ).encode('hex')

        # Stop him so we can write to the buffer he created
        self.trace.sendBreak()
        self.trace.writeMemory( addr, testbuf )

        self.runUntilExit()

        # He should now print what we wrote...
        gotline = self.proc.stdout.readline().strip()
        self.assertEqual(testbuf,gotline)

