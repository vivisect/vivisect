import unittest

import vivisect
import envi.const as e_const


class VampSigTests(unittest.TestCase):
    '''
    Tests to verify detection of signatures for special functions in PE files.
    If a signature is detected during makeFunc(), it should mark the
    function as a thunk and name it according to the signature.
    '''

    def run_test(self, opcode_string):
        # Create a Vivisect workspace, architecture does not matter.
        vw = vivisect.VivWorkspace()
        vw.setMeta('Architecture', 'i386')
        vw.setMeta('Platform', 'windows')
        vw.setMeta('Format', 'pe')

        # Add the module that detects signatures.
        vw.addFuncAnalysisModule("vivisect.analysis.ms.msvc")

        # Put the opcodes into an executable memory map.
        mapbase = 0x400000
        bufferpgsz = 2 * 4096
        vw.addMemoryMap(mapbase - bufferpgsz, e_const.MM_RWX,
                        'test', '@' * bufferpgsz)
        bytez = bytes(bytearray.fromhex(opcode_string))
        vw.addMemoryMap(mapbase, e_const.MM_RWX, 'test', bytez)
        vw.addSegment(mapbase, len(bytez), 'test_code_%x' % mapbase, 'test')

        # Make a function, triggering signature detection.
        fva = mapbase
        vw.makeFunction(fva)
        return vw.getFunctionMeta(fva, 'Thunk')


    def test_sig_behavior(self):
        '''
        Test the behavior of signature detection.
        '''
        # True signature.
        opcodes = '680000000064a10000000050'
        self.assertEqual(self.run_test(opcodes), 'ntdll.seh3_prolog')

        # Incorrect signature.
        opcodes = '680000000064a100000000aa'
        self.assertEqual(self.run_test(opcodes), None)

        # Signature with masked out bytes changed.
        opcodes = '68aaaaaaaa64a10000000050'
        self.assertEqual(self.run_test(opcodes), 'ntdll.seh3_prolog')

        # Signature with extra opcodes.
        opcodes = '680000000064a100000000504141414141'
        self.assertEqual(self.run_test(opcodes), 'ntdll.seh3_prolog')

        # Signature with opcodes before.
        opcodes = '4141680000000064a10000000050'
        self.assertEqual(self.run_test(opcodes), None)


    def test_seh_sigs(self):
        '''
        Test detection of seh prolog and epilog signatures.
        '''
        opcodes = '680000000064a10000000050'
        self.assertEqual(self.run_test(opcodes), 'ntdll.seh3_prolog')

        opcodes = '8b4df064890d00000000595f5e5bc951c3'
        self.assertEqual(self.run_test(opcodes), 'ntdll.seh3_epilog')

        opcodes = '680000000064ff35000000008b442410'
        self.assertEqual(self.run_test(opcodes), 'ntdll.seh4_prolog')

        opcodes = '8b4df064890d00000000595f5f5e5b8be55d51c3'
        self.assertEqual(self.run_test(opcodes), 'ntdll.seh4_epilog')

        opcodes = '8b4df064890d00000000595f5f5e5b8be55d51f2c3'
        self.assertEqual(self.run_test(opcodes), 'ntdll.seh4_epilog')

        opcodes = 'a10000000033c58945fc'
        self.assertEqual(self.run_test(opcodes), 'ntdll.gs_prolog')


    def test_alloca_probe_sigs(self):
        '''
        Test detection of alloca_probe signatures.
        '''
        opcodes = '513d001000008d4c2408721481e9001000002d0010000085013d0010000073ec2bc88bc485018be18b088b400450c3'
        self.assertEqual(self.run_test(opcodes), 'ntdll._alloca_probe')

        opcodes = '518d4c24042bc81bc0f7d023c88bc42500f0ffff3bc8720a8bc159948b00890424c32d001000008500ebe9'
        self.assertEqual(self.run_test(opcodes), 'ntdll._alloca_probe')

        opcodes = '518d4c24042bc81bc0f7d023c88bc42500f0ffff3bc8f2720b8bc159948b00890424f2c32d001000008500ebe7'
        self.assertEqual(self.run_test(opcodes), 'ntdll._alloca_probe')

        opcodes = '4883ec104c8914244c895c24084d33db4c8d5424184c2bd04d0f42d3654c8b1c25100000004d3bd37316664181e200f04d8d9b00f0ffff41c603004d3bd375f04c8b14244c8b5c24084883c410c3'
        self.assertEqual(self.run_test(opcodes), 'ntdll._alloca_probe')

        opcodes = '4883ec104c8914244c895c24084d33db4c8d5424184c2bd04d0f42d3654c8b1c25100000004d3bd3f27317664181e200f04d8d9b00f0ffff41c603004d3bd3f275ef4c8b14244c8b5c24084883c410f2c3'
        self.assertEqual(self.run_test(opcodes), 'ntdll._alloca_probe')


    def test_security_cookie_sigs(self):
        '''
        Test detection of security_check_cookie signatures.
        '''
        opcodes = '3b0d000000007502f3c3e9'
        self.assertEqual(self.run_test(opcodes), 'ntdll.security_check_cookie')

        opcodes = '3b0d00000000f27502f2c3f2e9'
        self.assertEqual(self.run_test(opcodes), 'ntdll.security_check_cookie')

        opcodes = '483b0d00000000751148c1c11066f7c1ffff7502f3c348c1c910e9'
        self.assertEqual(self.run_test(opcodes), 'ntdll.security_check_cookie_64')

        opcodes = '483b0d00000000f2751148c1c11066f7c1fffff27502f2c348c1c910e9'
        self.assertEqual(self.run_test(opcodes), 'ntdll.security_check_cookie_64')

        opcodes = '483b0d00000000f2751248c1c11066f7c1fffff27502f2c348c1c910e9'
        self.assertEqual(self.run_test(opcodes), 'ntdll.security_check_cookie_64')


    def test_gs_failure_sigs(self):
        '''
        Test detection of gs_failure signatures.
        '''
        opcodes = '3b0d000000007502f3c3e9'
        self.assertEqual(self.run_test(opcodes), 'ntdll.security_check_cookie')
        opcodes = '8bff558bec5151a300000000890d00000000891500000000891d00000000893500000000893d000000008c15000000008c0d000000008c1d000000008c05000000008c25000000008c2d000000009c'
        self.assertEqual(self.run_test(opcodes), 'ntdll.report_gsfailure')

        opcodes = '8bff558bec81ec28030000a300000000890d00000000891500000000891d00000000893500000000893d00000000668c1500000000668c0d00000000668c1d00000000668c0500000000668c2500000000668c2d000000009c'
        self.assertEqual(self.run_test(opcodes), 'ntdll.report_gsfailure')


class VampJsonTests(unittest.TestCase):
    '''
    Tests for the JSON-based VAMP signature infrastructure:
    serialization, loading, filtering, deduplication, and the
    generic analysis module.
    '''

    def test_json_roundtrip(self):
        '''Test that a sigset can be serialized to JSON and loaded back.'''
        import tempfile
        import os
        import vivisect.vamp as v_vamp

        sigset = v_vamp.serializeSigSet(
            library='testlib', version='1.0', arch='amd64',
            platform='linux', compiler='gcc-9', compiled_flags='-O2',
            binary_sha256='abc123',
            signatures=[
                {'name': 'testlib.func_a', 'bytes': '90909090cccc',
                 'mask': 'ffffffffffff', 'func_size': 6,
                 'first_block_size': 6, 'reloc_count': 0,
                 'masked_ratio': 0.0, 'confidence': 'high'},
                {'name': 'testlib.func_b', 'bytes': '554889e5',
                 'mask': 'ffffffff', 'func_size': 4,
                 'first_block_size': 4, 'reloc_count': 0,
                 'masked_ratio': 0.0, 'confidence': 'low'},
            ]
        )

        # Write to temp file
        tmpdir = tempfile.mkdtemp()
        filepath = os.path.join(tmpdir, 'test_sig.json')
        v_vamp.saveSigSet(filepath, sigset)

        # Load it back
        tree, meta = v_vamp.loadSigSet(filepath)
        self.assertEqual(len(tree.sigs), 2)
        self.assertEqual(meta['library'], 'testlib')
        self.assertEqual(meta['version'], '1.0')
        self.assertEqual(meta['arch'], 'amd64')

        # Verify the sigs match
        import binascii
        bytez = binascii.unhexlify('90909090cccc')
        match = tree.getSignature(bytez, offset=0)
        self.assertEqual(match, 'testlib.func_a')

        # Clean up
        os.unlink(filepath)
        os.rmdir(tmpdir)

    def test_format_version_check(self):
        '''Test that loading rejects unsupported format versions.'''
        import tempfile
        import os
        import json
        import vivisect.vamp as v_vamp

        bad_data = {
            'format_version': 999,
            'library': 'test', 'signatures': []
        }
        tmpdir = tempfile.mkdtemp()
        filepath = os.path.join(tmpdir, 'bad_sig.json')
        with open(filepath, 'w') as f:
            json.dump(bad_data, f)

        with self.assertRaises(ValueError):
            v_vamp.loadSigSet(filepath)

        os.unlink(filepath)
        os.rmdir(tmpdir)

    def test_filter_sigs(self):
        '''Test signature filtering by length and confidence.'''
        import vivisect.vamp as v_vamp

        sigset = {
            'format_version': 1,
            'library': 'test',
            'signatures': [
                {'name': 'short', 'bytes': '9090', 'mask': 'ffff',
                 'first_block_size': 2, 'masked_ratio': 0.0,
                 'confidence': 'high'},
                {'name': 'medium', 'bytes': '9090909090909090', 'mask': 'ffffffff',
                 'first_block_size': 8, 'masked_ratio': 0.0,
                 'confidence': 'medium'},
                {'name': 'long_high', 'bytes': '90909090909090909090909090909090',
                 'mask': 'ffffffffffffffffffffffffffffffff',
                 'first_block_size': 16, 'masked_ratio': 0.0,
                 'confidence': 'high'},
                {'name': 'too_masked', 'bytes': '9090909090909090',
                 'mask': 'ff000000ff000000',
                 'first_block_size': 8, 'masked_ratio': 0.75,
                 'confidence': 'low'},
            ]
        }

        # Filter: min_length=8, max_masked=0.50, min_confidence='low'
        filtered = v_vamp.filterSigs(sigset, min_length=8, max_masked_ratio=0.50,
                                     min_confidence='low')
        names = [s['name'] for s in filtered['signatures']]
        self.assertIn('medium', names)
        self.assertIn('long_high', names)
        self.assertNotIn('short', names)  # too short
        self.assertNotIn('too_masked', names)  # too masked

        # Filter: min_confidence='high'
        filtered = v_vamp.filterSigs(sigset, min_length=1, max_masked_ratio=1.0,
                                     min_confidence='high')
        names = [s['name'] for s in filtered['signatures']]
        self.assertIn('long_high', names)
        self.assertNotIn('medium', names)

    def test_dedup_sigs(self):
        '''Test that duplicate signatures are removed.'''
        import vivisect.vamp as v_vamp

        sigset = {
            'format_version': 1,
            'library': 'test',
            'signatures': [
                {'name': 'func_a', 'bytes': '90909090', 'mask': 'ffffffff'},
                {'name': 'func_b', 'bytes': '90909090', 'mask': 'ffffffff'},  # dup
                {'name': 'func_c', 'bytes': 'cccccccc', 'mask': 'ffffffff'},
            ]
        }

        deduped = v_vamp.dedupSigs(sigset)
        self.assertEqual(len(deduped['signatures']), 2)
        self.assertIn('dedup_conflicts', deduped)
        self.assertEqual(len(deduped['dedup_conflicts']), 1)

    def test_load_all_sig_sets(self):
        '''Test that loadAllSigSets finds the MSVC JSON data files.'''
        import vivisect.vamp as v_vamp

        sets = v_vamp.loadAllSigSets()
        self.assertGreaterEqual(len(sets), 1, "Should find at least one sig set")

        for tree, meta, filepath in sets:
            self.assertGreater(len(tree.sigs), 0, "Each set should have sigs")
            self.assertIn('library', meta)
            self.assertIn('version', meta)

    def test_load_sig_set_index(self):
        '''Test that the index file can be loaded.'''
        import vivisect.vamp as v_vamp

        index = v_vamp.loadSigSetIndex()
        self.assertIn('sig_sets', index)
        self.assertGreaterEqual(len(index['sig_sets']), 1)

    def test_msvc_json_backward_compat(self):
        '''Test that the refactored MSVC module still matches signatures.'''
        import vivisect.vamp.msvc as v_msvc

        vs = v_msvc.VisualStudioVamp()
        # Should have loaded sigs (either from JSON or fallback)
        self.assertGreater(len(vs.sigs), 0)

        # Test a known signature match
        import binascii
        bytez = binascii.unhexlify('680000000064a10000000050')
        match = vs.getSignature(bytez, offset=0)
        self.assertEqual(match, 'ntdll.seh3_prolog')

    def test_generic_vamp_analysis(self):
        '''Test that the generic VAMP analysis module can match sigs.'''
        import vivisect
        import envi.const as e_const
        import vivisect.analysis.generic.vamp as gvamp

        # Create a workspace with the generic vamp module
        vw = vivisect.VivWorkspace()
        vw.setMeta('Architecture', 'i386')
        vw.setMeta('Platform', 'windows')
        vw.setMeta('Format', 'pe')

        vw.addFuncAnalysisModule("vivisect.analysis.generic.vamp")

        # Put seh3_prolog opcodes into an executable memory map
        mapbase = 0x400000
        bufferpgsz = 2 * 4096
        vw.addMemoryMap(mapbase - bufferpgsz, e_const.MM_RWX,
                        'test', '@' * bufferpgsz)
        bytez = bytes(bytearray.fromhex('680000000064a10000000050'))
        vw.addMemoryMap(mapbase, e_const.MM_RWX, 'test', bytez)
        vw.addSegment(mapbase, len(bytez), 'test_code_%x' % mapbase, 'test')

        fva = mapbase
        vw.makeFunction(fva)
        thunk = vw.getFunctionMeta(fva, 'Thunk')
        self.assertEqual(thunk, 'ntdll.seh3_prolog')
