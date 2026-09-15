import os
import signal
import unittest

import vtrace
import vtrace.tests as vt_tests
import vtrace.platforms.linux as v_linux

class ThreadNotifier(vtrace.Notifier):

    def __init__(self):
        vtrace.Notifier.__init__(self)
        self.threadexit = False
        self.threadcreate = False

    def notify(self, event, trace):
        if event == vtrace.NOTIFY_CREATE_THREAD:
            self.threadcreate = True
            return

        if event == vtrace.NOTIFY_EXIT_THREAD:
            self.threadexit = True
            return

class VtraceThreadTest(vt_tests.VtraceProcessTest):

    pypath = os.path.join('vtrace','tests','mains','mainthreads.py')

    def test_vtrace_threads(self):
        n = ThreadNotifier()

        self.trace.registerNotifier(vtrace.NOTIFY_ALL, n)
        self.runUntilExit()

        self.assertTrue(n.threadcreate)
        self.assertTrue(n.threadexit)


class LinuxThreadEventRegressionTest(unittest.TestCase):

    class FakeTrace:

        def __init__(self, event_tid=0):
            self.pid = 31337
            self.execing = False
            self._stopped_hack = True
            self._stopped_cache = {}
            self.event_tid = event_tid
            self.attach_calls = []
            self.pthreads = [self.pid]

        def getPtraceEvent(self, tid=None):
            return self.event_tid

        def attachThread(self, tid, attached=False):
            self.attach_calls.append((tid, attached))

        def _attachThreadFromEvent(self, tid):
            return v_linux.LinuxMixin._attachThreadFromEvent(self, tid)

        def _getStoppedThreadFallback(self):
            return v_linux.LinuxMixin._getStoppedThreadFallback(self)

        def runAgain(self):
            pass

        def handlePosixSignal(self, sig):
            raise AssertionError('unexpected signal handling path')

    def test_stopped_hack_ignores_zero_thread_id(self):
        trace = self.FakeTrace(event_tid=0)
        status = (signal.SIGSTOP << 8) | 0x7f

        v_linux.LinuxMixin.platformProcessEvent(trace, (trace.pid, status))

        self.assertEqual(trace.attach_calls, [])

    def test_stopped_hack_falls_back_to_cached_thread_id(self):
        trace = self.FakeTrace(event_tid=0)
        trace._stopped_cache[4242] = True
        status = (signal.SIGSTOP << 8) | 0x7f

        v_linux.LinuxMixin.platformProcessEvent(trace, (trace.pid, status))

        self.assertEqual(trace.attach_calls, [(4242, True)])

    def test_stopped_hack_attaches_valid_thread_id(self):
        trace = self.FakeTrace(event_tid=4242)
        status = (signal.SIGSTOP << 8) | 0x7f

        v_linux.LinuxMixin.platformProcessEvent(trace, (trace.pid, status))

        self.assertEqual(trace.attach_calls, [(4242, True)])

    def test_validate_thread_id_rejects_zero(self):
        with self.assertRaises(vtrace.PlatformException):
            v_linux.LinuxMixin._validateThreadId(self.FakeTrace(), 0)
