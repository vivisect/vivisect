import os
import binascii

import vtrace.tests as vt_tests


class VtraceWritememTest(vt_tests.VtraceProcessTest):

    pypath = os.path.join('vtrace', 'tests', 'mains', 'mainwritemem.py')

    def test_vtrace_writemem(self):

        self.runProcess()

        addrstr = self.proc.stdout.readline()
        addr = int(addrstr, 16)

        testbuf = binascii.hexlify(os.urandom(10))

        # Stop him so we can write to the buffer he created
        self.trace.sendBreak()
        self.trace.writeMemory(addr, testbuf)

        self.runUntilExit()

        # He should now print what we wrote...
        gotline = self.proc.stdout.readline().strip()
        self.assertEqual(testbuf.decode('utf-8'), gotline)
