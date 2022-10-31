import unittest

import vivisect.tests.helpers as helpers
import vivisect.tests.utils as v_t_utils

import vdb.recon as v_rec
import vtrace
		

sym_name = {
    'windows': 'kernel32.WriteFile',
    'linux': 'libc.exit',
    'freebsd': 'libc.exit',
}

class VdbReconTests(v_t_utils.VivTest):
    '''
    Tests to verify recon hooking during execution.
    '''

    @classmethod
    def setUpClass(cls):
        cls.hello_i386_vw = helpers.getTestWorkspace('windows', 'i386',
                                                     'helloworld.exe')
        cls.hello_amd64_vw = helpers.getTestWorkspace('windows', 'amd64',
                                                      'helloworld.exe')

    def test_vdb_recon_i386(self):    
        trace = vtrace.getTrace()
        plat = trace.getMeta('Platform')
        sym = sym_name.get(plat)
		
        trace.execute(helpers.getTestPath('windows', 'i386',
                                                     'helloworld.exe'))
        trace.setMode('RunForever', True)
        v_rec.addReconBreak(trace, sym, 'PPXPP')   
        trace.run()

        self.assertGreater(len(v_rec.getReconHits(trace)), 0)
		
    def test_vdb_recon_amd64(self):    
        trace = vtrace.getTrace()
        plat = trace.getMeta('Platform')
        sym = sym_name.get(plat)
		
        trace.execute(helpers.getTestPath('windows', 'amd64',
                                                     'helloworld.exe'))
        trace.setMode('RunForever', True)
        v_rec.addReconBreak(trace, sym, 'PPXPP')
        trace.run()

        self.assertGreater(len(v_rec.getReconHits(trace)), 0)

if __name__ == '__main__':
    unittest.main()
