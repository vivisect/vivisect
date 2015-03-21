import os
import sys
import subprocess

import vivisect.debug.api as v_dbgapi
import vivisect.hal.memory as v_memory

from subprocess import Popen, PIPE
from vivisect.debug.lib.until import forever

dirname = os.path.dirname( __file__ )

class DebugTestHelper:

    def getPyMainExec(self, name):
        dbg = v_dbgapi.getDebugApi()
        pypath = os.path.join( dirname, name )
        cmdline = '%s %s' % (sys.executable, pypath)
        trace = dbg.exec( cmdline )
        return trace

    def getPyMainAttach(self, name):
        dbg = v_dbgapi.getDebugApi()
        pypath = os.path.join( dirname, name )
        p = Popen([ sys.executable, pypath, 'testwait'], stdin=PIPE, stdout=PIPE)

        line = p.stdout.readline().strip()
        self.assertEqual( line, b'testwait' )
        print('got line')

        trace = dbg.attach( p.pid )
        p.stdin.write('testrun\n')

        return trace

    def _run_exit42(self, trace):
        testdata = {}
        def onexit(event):
            testdata['exitcode'] = event[1].get('exitcode')

        trace.on('trace:exit', onexit)

        trace.run(until=forever, wait=True)
        self.assertEqual( testdata.get('exitcode'), 42 )

    def test_debug_exec_exit42(self):
        trace = self.getPyMainExec('pymain_exit42.py')
        self._run_exit42(trace)

    #def test_debug_attach_exit42(self):
        #trace = self.getPyMainAttach('pymain_exit42.py')
        #self._run_exit42(trace)

    def test_debug_exec_addr56(self):
        trace = self.getPyMainExec('pymain_addr56.py')

        testdata = {}
        def onsignal(event):
            testdata['signo'] = event[1].get('signo')
            testdata['signorm'] = event[1].get('signorm')

        trace.on('trace:signal', onsignal)

        trace.run(until=forever, wait=True)

        signorm = testdata.get('signorm')
        self.assertIsNotNone( signorm )

        self.assertEqual( signorm[0], 'badmem' )
        self.assertEqual( signorm[1].get('addr'), 0x56565656 )
        self.assertEqual( signorm[1].get('perm'), v_memory.MM_READ )

    def test_debug_exec_thread69(self):

        trace = self.getPyMainExec('pymain_thread69.py')

        testdata = {'inits':0,'exits':0}
        def threadinit(event):
            testdata['inits'] += 1

        def threadexit(event):
            testdata['exits'] += 1

        trace.on('trace:thread:init', threadinit)
        trace.on('trace:thread:exit', threadexit)

        trace.run(until=forever, wait=True)

        self.assertEqual( testdata.get('inits'), 2 )
        self.assertEqual( testdata.get('exits'), 2 )

    def test_debug_exec_print(self):
        trace = self.getPyMainExec('pymain_exit42.py')

        testdata = {}
        def onprint(event):
            testdata['msg'] = event[1].get('msg')

        trace.on('trace:print', onprint)
        trace.print('woot')

        self.assertEqual( testdata.get('msg'), 'woot')

    def test_debug_exec_error(self):
        trace = self.getPyMainExec('pymain_exit42.py')

        testdata = {}
        def onerr(event):
            testdata['msg'] = event[1].get('msg')

        trace.on('trace:error', onerr)
        trace.error('woot')

        self.assertEqual( testdata.get('msg'), 'woot')

    def test_debug_exec_autocont(self):
        # test the default auto continue settings

        trace = self.getPyMainExec('pymain_exit42.py')
        # we should be at trace:ready
        print(trace.runinfo['lastevent'])

        trace.run(wait=True)
        # we should be at trace:exit
        print(trace.runinfo['lastevent'])
