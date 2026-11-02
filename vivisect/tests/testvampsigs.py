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

    def test_generic_vamp_arch_filter(self):
        '''Test that the generic VAMP module filters sigs by architecture.'''
        import vivisect
        import envi.const as e_const
        import vivisect.analysis.generic.vamp as gvamp

        # amd64 workspace should not load i386 sigs and vice versa
        vw = vivisect.VivWorkspace()
        vw.setMeta('Architecture', 'aarch64')
        vw.setMeta('Platform', 'windows')
        vw.setMeta('Format', 'pe')

        # Clear the sigtree cache so arch filtering runs fresh
        gvamp._sigtree_cache.clear()

        vw.addFuncAnalysisModule("vivisect.analysis.generic.vamp")

        # seh3_prolog is an i386 sig — should NOT match on aarch64
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
        # Should be None — no aarch64 sigs match this i386 pattern
        self.assertIsNone(thunk)


class VampDataDirTests(unittest.TestCase):
    '''
    Tests for the configurable VAMP signature data directory system:
    VAMP_SIG_DIR env var, ~/.viv/vamp-sigs/data/ fallback,
    colon-separated multi-dir support, and package-level fallback.
    '''

    def setUp(self):
        '''Save VAMP_SIG_DIR so we can restore it after each test.'''
        import os
        self._saved_env = os.environ.get('VAMP_SIG_DIR')
        os.environ.pop('VAMP_SIG_DIR', None)

    def tearDown(self):
        import os
        if self._saved_env is not None:
            os.environ['VAMP_SIG_DIR'] = self._saved_env
        else:
            os.environ.pop('VAMP_SIG_DIR', None)

    def test_no_env_returns_package_dir(self):
        '''Without VAMP_SIG_DIR, package-level dir is the fallback.'''
        import os
        import vivisect.vamp as v_vamp
        dirs = v_vamp.getSigDataDirs()
        self.assertGreaterEqual(len(dirs), 1)
        # Package dir should always be in the list
        self.assertTrue(any(d.endswith('vamp/data') for d in dirs))

    def test_get_sig_data_dir_backward_compat(self):
        '''getSigDataDir() returns a single string (backward compat).'''
        import vivisect.vamp as v_vamp
        d = v_vamp.getSigDataDir()
        self.assertIsInstance(d, str)
        self.assertTrue(len(d) > 0)

    def test_single_env_dir(self):
        '''Single VAMP_SIG_DIR directory is included in the list.'''
        import os
        import tempfile
        import vivisect.vamp as v_vamp

        with tempfile.TemporaryDirectory() as td:
            os.environ['VAMP_SIG_DIR'] = td
            dirs = v_vamp.getSigDataDirs()
            self.assertIn(td, dirs)
            # Package dir still appended
            self.assertTrue(any(d.endswith('vamp/data') for d in dirs))

    def test_multiple_env_dirs(self):
        '''Colon-separated VAMP_SIG_DIR directories are all included.'''
        import os
        import tempfile
        import vivisect.vamp as v_vamp

        with tempfile.TemporaryDirectory() as td1, tempfile.TemporaryDirectory() as td2:
            os.environ['VAMP_SIG_DIR'] = '%s:%s' % (td1, td2)
            dirs = v_vamp.getSigDataDirs()
            self.assertIn(td1, dirs)
            self.assertIn(td2, dirs)

    def test_nonexistent_dirs_skipped(self):
        '''Non-existent directories in VAMP_SIG_DIR are silently skipped.'''
        import os
        import tempfile
        import vivisect.vamp as v_vamp

        with tempfile.TemporaryDirectory() as td:
            os.environ['VAMP_SIG_DIR'] = '/nonexistent/path12345:%s' % td
            dirs = v_vamp.getSigDataDirs()
            self.assertNotIn('/nonexistent/path12345', dirs)
            self.assertIn(td, dirs)

    def test_duplicate_dirs_deduped(self):
        '''Duplicate directories in VAMP_SIG_DIR are deduplicated.'''
        import os
        import tempfile
        import vivisect.vamp as v_vamp

        with tempfile.TemporaryDirectory() as td:
            os.environ['VAMP_SIG_DIR'] = '%s:%s' % (td, td)
            dirs = v_vamp.getSigDataDirs()
            self.assertEqual(dirs.count(td), 1)

    def test_empty_env_var_ignored(self):
        '''Empty VAMP_SIG_DIR is treated as unset.'''
        import os
        import vivisect.vamp as v_vamp
        os.environ['VAMP_SIG_DIR'] = ''
        dirs = v_vamp.getSigDataDirs()
        # Should just be the package dir
        self.assertGreaterEqual(len(dirs), 1)

    def test_load_all_sig_sets_multi_dir(self):
        '''loadAllSigSets merges sigs from multiple directories.'''
        import os
        import tempfile
        import json
        import vivisect.vamp as v_vamp

        with tempfile.TemporaryDirectory() as td1, tempfile.TemporaryDirectory() as td2:
            # Write a test sig set to each dir
            for i, td in enumerate([td1, td2]):
                sigset = v_vamp.serializeSigSet(
                    library='testlib%d' % i, version='1.0', arch='amd64',
                    platform='linux', compiler='gcc-9',
                    compiled_flags='', binary_sha256='abc%d' % i,
                    signatures=[
                        {'name': 'testlib%d.func_%d' % (i, i),
                         'bytes': '9090909090909090',
                         'mask': 'ffffffffffffffff',
                         'func_size': 8, 'first_block_size': 8,
                         'reloc_count': 0, 'masked_ratio': 0.0,
                         'confidence': 'high'},
                    ]
                )
                v_vamp.saveSigSet(os.path.join(td, 'test_sigs_%d.json' % i), sigset)

            os.environ['VAMP_SIG_DIR'] = '%s:%s' % (td1, td2)
            sets = v_vamp.loadAllSigSets()
            # Should find sig sets from both dirs (plus package MSVC if present)
            libraries = [meta.get('library') for _, meta, _ in sets]
            self.assertIn('testlib0', libraries)
            self.assertIn('testlib1', libraries)

    def test_load_sig_set_index_multi_dir(self):
        '''loadSigSetIndex merges index.json from multiple directories.'''
        import os
        import tempfile
        import json
        import vivisect.vamp as v_vamp

        with tempfile.TemporaryDirectory() as td1, tempfile.TemporaryDirectory() as td2:
            # Write an index.json to each dir
            for i, td in enumerate([td1, td2]):
                idx = {
                    'format_version': 1,
                    'sig_set_count': 1,
                    'total_signatures': 10,
                    'sig_sets': [{'library': 'lib%d' % i, 'file': 'lib%d.json' % i}],
                }
                with open(os.path.join(td, 'index.json'), 'w') as f:
                    json.dump(idx, f)

            os.environ['VAMP_SIG_DIR'] = '%s:%s' % (td1, td2)
            merged = v_vamp.loadSigSetIndex()
            self.assertIn('sig_sets', merged)
            libs = [s['library'] for s in merged['sig_sets']]
            self.assertIn('lib0', libs)
            self.assertIn('lib1', libs)

    def test_msvc_search_all_dirs(self):
        '''MSVC module searches all data dirs for msvc_*.json files.'''
        import os
        import tempfile
        import vivisect.vamp.msvc as v_msvc

        # Create a temp dir with a custom msvc_x86.json that has a test sig
        with tempfile.TemporaryDirectory() as td:
            import json
            sigset = {
                'format_version': 1,
                'library': 'msvc',
                'version': 'test',
                'arch': 'i386',
                'signatures': [
                    {'name': 'test.custom_msvc_sig',
                     'bytes': 'deadbeefcafebabe',
                     'mask': 'ffffffffffffffff',
                     'func_size': 8, 'first_block_size': 8,
                     'reloc_count': 0, 'masked_ratio': 0.0,
                     'confidence': 'high'},
                ]
            }
            with open(os.path.join(td, 'msvc_x86.json'), 'w') as f:
                json.dump(sigset, f)

            os.environ['VAMP_SIG_DIR'] = td
            vs = v_msvc.VisualStudioVamp()
            # Should have loaded at least our test sig
            self.assertGreater(len(vs.sigs), 0)

            import binascii
            bytez = binascii.unhexlify('deadbeefcafebabe')
            match = vs.getSignature(bytez, offset=0)
            self.assertEqual(match, 'test.custom_msvc_sig')


class VampSerializationTests(unittest.TestCase):
    '''
    Tests for VAMP signature JSON serialization: roundtrip fidelity,
    metadata preservation, mask handling, and edge cases.
    '''

    def test_serialize_preserves_all_fields(self):
        '''serializeSigSet preserves all metadata fields.'''
        import vivisect.vamp as v_vamp

        sigset = v_vamp.serializeSigSet(
            library='zlib', version='1.3', arch='amd64',
            platform='linux', compiler='gcc-13',
            compiled_flags='-O2 -fPIC',
            binary_sha256='abc123def456',
            source_url='https://example.com/zlib.a',
            generated_by='test-suite',
            signatures=[
                {'name': 'zlib.compress', 'bytes': '554889e5',
                 'mask': 'ffffffff', 'func_size': 100,
                 'first_block_size': 4, 'reloc_count': 0,
                 'masked_ratio': 0.0, 'confidence': 'high'},
            ]
        )
        self.assertEqual(sigset['format_version'], 1)
        self.assertEqual(sigset['library'], 'zlib')
        self.assertEqual(sigset['version'], '1.3')
        self.assertEqual(sigset['arch'], 'amd64')
        self.assertEqual(sigset['platform'], 'linux')
        self.assertEqual(sigset['compiler'], 'gcc-13')
        self.assertEqual(sigset['compiled_flags'], '-O2 -fPIC')
        self.assertEqual(sigset['binary_sha256'], 'abc123def456')
        self.assertEqual(sigset['source_url'], 'https://example.com/zlib.a')
        self.assertEqual(sigset['generated_by'], 'test-suite')
        self.assertEqual(len(sigset['signatures']), 1)

    def test_json_roundtrip_with_mask(self):
        '''JSON roundtrip preserves sig bytes and masks exactly.'''
        import tempfile, os, binascii
        import vivisect.vamp as v_vamp

        # In VAMP sigs, both the sig byte AND mask byte are 0x00 at masked
        # positions. The SignatureTree checks: input_byte & mask == sig_byte.
        # So sig bytes must be pre-masked (bytes & mask).
        test_bytes = '554889e548890000ebfe'  # bytes 6-7 are 0x00 (masked)
        test_mask = 'ffffffffffff0000ffff'

        sigset = v_vamp.serializeSigSet(
            library='test', version='1.0', arch='amd64',
            platform='linux', compiler='gcc-13',
            compiled_flags='', binary_sha256='deadbeef',
            signatures=[
                {'name': 'test.func_a', 'bytes': test_bytes,
                 'mask': test_mask, 'func_size': 10,
                 'first_block_size': 10, 'reloc_count': 2,
                 'masked_ratio': 0.2, 'confidence': 'medium'},
            ]
        )

        tmpdir = tempfile.mkdtemp()
        filepath = os.path.join(tmpdir, 'test.json')
        v_vamp.saveSigSet(filepath, sigset)

        tree, meta = v_vamp.loadSigSet(filepath)
        self.assertEqual(len(tree.sigs), 1)

        # Verify the sig matches with the exact bytes
        bytez = binascii.unhexlify(test_bytes)
        match = tree.getSignature(bytez, offset=0)
        self.assertEqual(match, 'test.func_a')

        # Verify masked bytes also match (change the masked-out bytes)
        # Original: 554889e548890000ebfe, mask: ffffffffffff0000ffff
        # Bytes 6-7 are masked (0x00), so any value there should still match
        bytez_masked = binascii.unhexlify('554889e54889aabbebfe')
        match_masked = tree.getSignature(bytez_masked, offset=0)
        self.assertEqual(match_masked, 'test.func_a')

        os.unlink(filepath)
        os.rmdir(tmpdir)

    def test_json_roundtrip_no_mask(self):
        '''JSON roundtrip handles sigs with no mask (None).'''
        import tempfile, os, binascii
        import vivisect.vamp as v_vamp

        sigset = v_vamp.serializeSigSet(
            library='test', version='1.0', arch='i386',
            platform='windows', compiler='msvc',
            compiled_flags='', binary_sha256='aaa',
            signatures=[
                {'name': 'test.no_mask', 'bytes': '90909090c3',
                 'mask': None, 'func_size': 5,
                 'first_block_size': 5, 'reloc_count': 0,
                 'masked_ratio': 0.0, 'confidence': 'high'},
            ]
        )

        tmpdir = tempfile.mkdtemp()
        filepath = os.path.join(tmpdir, 'test.json')
        v_vamp.saveSigSet(filepath, sigset)

        tree, meta = v_vamp.loadSigSet(filepath)
        self.assertEqual(len(tree.sigs), 1)

        bytez = binascii.unhexlify('90909090c3')
        match = tree.getSignature(bytez, offset=0)
        self.assertEqual(match, 'test.no_mask')

        os.unlink(filepath)
        os.rmdir(tmpdir)

    def test_empty_sigset(self):
        '''Loading an empty sigset (0 signatures) works.'''
        import tempfile, os
        import vivisect.vamp as v_vamp

        sigset = v_vamp.serializeSigSet(
            library='empty', version='0.1', arch='amd64',
            platform='linux', compiler='gcc',
            compiled_flags='', binary_sha256='',
            signatures=[]
        )

        tmpdir = tempfile.mkdtemp()
        filepath = os.path.join(tmpdir, 'empty.json')
        v_vamp.saveSigSet(filepath, sigset)

        tree, meta = v_vamp.loadSigSet(filepath)
        self.assertEqual(len(tree.sigs), 0)
        self.assertEqual(meta['library'], 'empty')

        os.unlink(filepath)
        os.rmdir(tmpdir)

    def test_multiple_sigs_same_file(self):
        '''Multiple sigs in one JSON file all load correctly.'''
        import tempfile, os, binascii
        import vivisect.vamp as v_vamp

        sigs = []
        for i in range(20):
            hex_bytes = '%08x' % (0x90909090 + i)
            sigs.append({
                'name': 'test.func_%02d' % i,
                'bytes': hex_bytes,
                'mask': 'ffffffff',
                'func_size': 4, 'first_block_size': 4,
                'reloc_count': 0, 'masked_ratio': 0.0,
                'confidence': 'high',
            })

        sigset = v_vamp.serializeSigSet(
            library='test', version='1.0', arch='amd64',
            platform='linux', compiler='gcc', compiled_flags='',
            binary_sha256='multi', signatures=sigs
        )

        tmpdir = tempfile.mkdtemp()
        filepath = os.path.join(tmpdir, 'multi.json')
        v_vamp.saveSigSet(filepath, sigset)

        tree, meta = v_vamp.loadSigSet(filepath)
        self.assertEqual(len(tree.sigs), 20)

        # Check that each sig matches
        for i in range(20):
            bytez = binascii.unhexlify('%08x' % (0x90909090 + i))
            match = tree.getSignature(bytez, offset=0)
            self.assertEqual(match, 'test.func_%02d' % i)

        os.unlink(filepath)
        os.rmdir(tmpdir)


class VampFilterTests(unittest.TestCase):
    '''
    Tests for signature filtering: length thresholds, masked ratio limits,
    and confidence levels.
    '''

    def _make_sigset(self, sigs):
        import vivisect.vamp as v_vamp
        return v_vamp.serializeSigSet(
            library='test', version='1.0', arch='amd64',
            platform='linux', compiler='gcc', compiled_flags='',
            binary_sha256='filter', signatures=sigs
        )

    def test_min_length_filter(self):
        '''Filter removes sigs shorter than min_length.'''
        import vivisect.vamp as v_vamp
        sigset = self._make_sigset([
            {'name': 'short', 'bytes': '9090', 'mask': 'ffff',
             'first_block_size': 2, 'masked_ratio': 0.0, 'confidence': 'high'},
            {'name': 'long', 'bytes': '9090909090909090', 'mask': 'ffffffff',
             'first_block_size': 8, 'masked_ratio': 0.0, 'confidence': 'high'},
        ])
        filtered = v_vamp.filterSigs(sigset, min_length=4)
        names = [s['name'] for s in filtered['signatures']]
        self.assertIn('long', names)
        self.assertNotIn('short', names)

    def test_max_masked_ratio_filter(self):
        '''Filter removes sigs with masked_ratio above threshold.'''
        import vivisect.vamp as v_vamp
        sigset = self._make_sigset([
            {'name': 'clean', 'bytes': '9090909090909090', 'mask': 'ffffffffffffffff',
             'first_block_size': 8, 'masked_ratio': 0.0, 'confidence': 'high'},
            {'name': 'masked', 'bytes': '9090909090909090', 'mask': 'ff00ff00ff00ff00',
             'first_block_size': 8, 'masked_ratio': 0.5, 'confidence': 'high'},
        ])
        filtered = v_vamp.filterSigs(sigset, max_masked_ratio=0.25)
        names = [s['name'] for s in filtered['signatures']]
        self.assertIn('clean', names)
        self.assertNotIn('masked', names)

    def test_confidence_filter(self):
        '''Filter removes sigs below the confidence threshold.'''
        import vivisect.vamp as v_vamp
        sigset = self._make_sigset([
            {'name': 'high_conf', 'bytes': '9090909090909090', 'mask': 'ffffffffffffffff',
             'first_block_size': 8, 'masked_ratio': 0.0, 'confidence': 'high'},
            {'name': 'low_conf', 'bytes': '9090909090909090', 'mask': 'ffffffffffffffff',
             'first_block_size': 8, 'masked_ratio': 0.0, 'confidence': 'low'},
        ])
        filtered = v_vamp.filterSigs(sigset, min_length=1, min_confidence='high')
        names = [s['name'] for s in filtered['signatures']]
        self.assertIn('high_conf', names)
        self.assertNotIn('low_conf', names)

    def test_combined_filters(self):
        '''All filter criteria applied together.'''
        import vivisect.vamp as v_vamp
        sigset = self._make_sigset([
            {'name': 'pass_all', 'bytes': '90909090909090909090', 'mask': 'ffffffffffffffffffff',
             'first_block_size': 10, 'masked_ratio': 0.0, 'confidence': 'high'},
            {'name': 'fail_short', 'bytes': '9090', 'mask': 'ffff',
             'first_block_size': 2, 'masked_ratio': 0.0, 'confidence': 'high'},
            {'name': 'fail_masked', 'bytes': '9090909090909090', 'mask': 'ff00ff00ff00ff00',
             'first_block_size': 8, 'masked_ratio': 0.5, 'confidence': 'high'},
            {'name': 'fail_conf', 'bytes': '9090909090909090', 'mask': 'ffffffffffffffff',
             'first_block_size': 8, 'masked_ratio': 0.0, 'confidence': 'low'},
        ])
        filtered = v_vamp.filterSigs(sigset, min_length=4, max_masked_ratio=0.25,
                                     min_confidence='high')
        names = [s['name'] for s in filtered['signatures']]
        self.assertIn('pass_all', names)
        self.assertNotIn('fail_short', names)
        self.assertNotIn('fail_masked', names)
        self.assertNotIn('fail_conf', names)


class VampDedupTests(unittest.TestCase):
    '''
    Tests for signature deduplication: duplicate detection, conflict tracking,
    and keeping the first occurrence.
    '''

    def test_no_duplicates(self):
        '''Dedup on a set with no duplicates returns unchanged count.'''
        import vivisect.vamp as v_vamp
        sigset = {
            'format_version': 1, 'library': 'test',
            'signatures': [
                {'name': 'a', 'bytes': '90909090', 'mask': 'ffffffff'},
                {'name': 'b', 'bytes': 'cccccccc', 'mask': 'ffffffff'},
            ]
        }
        deduped = v_vamp.dedupSigs(sigset)
        self.assertEqual(len(deduped['signatures']), 2)

    def test_duplicates_removed(self):
        '''Duplicate sigs (same bytes+mask) are removed, keeping the first.'''
        import vivisect.vamp as v_vamp
        sigset = {
            'format_version': 1, 'library': 'test',
            'signatures': [
                {'name': 'original', 'bytes': '90909090', 'mask': 'ffffffff'},
                {'name': 'alias', 'bytes': '90909090', 'mask': 'ffffffff'},
                {'name': 'unique', 'bytes': 'cccccccc', 'mask': 'ffffffff'},
            ]
        }
        deduped = v_vamp.dedupSigs(sigset)
        self.assertEqual(len(deduped['signatures']), 2)
        names = [s['name'] for s in deduped['signatures']]
        self.assertIn('original', names)
        self.assertNotIn('alias', names)
        self.assertIn('unique', names)

    def test_dedup_conflicts_tracked(self):
        '''Dedup tracks which names conflicted with which kept name.'''
        import vivisect.vamp as v_vamp
        sigset = {
            'format_version': 1, 'library': 'test',
            'signatures': [
                {'name': 'keep', 'bytes': '90909090', 'mask': 'ffffffff'},
                {'name': 'drop1', 'bytes': '90909090', 'mask': 'ffffffff'},
                {'name': 'drop2', 'bytes': '90909090', 'mask': 'ffffffff'},
            ]
        }
        deduped = v_vamp.dedupSigs(sigset)
        self.assertIn('dedup_conflicts', deduped)
        # Two dups → two conflict entries
        self.assertEqual(len(deduped['dedup_conflicts']), 2)
        # Each conflict has name1 (kept) and name2 (dropped)
        for conflict in deduped['dedup_conflicts']:
            self.assertEqual(conflict['name1'], 'keep')
            self.assertIn(conflict['name2'], ('drop1', 'drop2'))

    def test_dedup_different_masks_not_duplicates(self):
        '''Sigs with same bytes but different masks are NOT duplicates.'''
        import vivisect.vamp as v_vamp
        sigset = {
            'format_version': 1, 'library': 'test',
            'signatures': [
                {'name': 'a', 'bytes': '90909090', 'mask': 'ffffffff'},
                {'name': 'b', 'bytes': '90909090', 'mask': 'ff00ff00'},
            ]
        }
        deduped = v_vamp.dedupSigs(sigset)
        self.assertEqual(len(deduped['signatures']), 2)


class VampMsvcFallbackTests(unittest.TestCase):
    '''
    Tests that the MSVC module falls back to hardcoded sigs when
    JSON files are not available, and that both paths produce
    working signatures.
    '''

    def test_fallback_sigs_loaded(self):
        '''Hardcoded fallback sigs work even without JSON files.'''
        import os
        import vivisect.vamp.msvc as v_msvc

        # Point to a nonexistent dir so JSON files aren't found
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            os.environ['VAMP_SIG_DIR'] = td
            vs = v_msvc.VisualStudioVamp()
            self.assertGreater(len(vs.sigs), 0)

            # Test a known hardcoded sig still matches
            import binascii
            bytez = binascii.unhexlify('680000000064a10000000050')
            match = vs.getSignature(bytez, offset=0)
            self.assertEqual(match, 'ntdll.seh3_prolog')

    def test_msvc_sigs_match_various_patterns(self):
        '''Multiple MSVC sig patterns all match correctly.'''
        import binascii
        import vivisect.vamp.msvc as v_msvc

        vs = v_msvc.VisualStudioVamp()
        self.assertGreater(len(vs.sigs), 0)

        # Test several known sigs
        test_cases = [
            ('680000000064a10000000050', 'ntdll.seh3_prolog'),
            ('8b4df064890d00000000595f5e5bc951c3', 'ntdll.seh3_epilog'),
            ('a10000000033c58945fc', 'ntdll.gs_prolog'),
        ]

        for hex_str, expected in test_cases:
            bytez = binascii.unhexlify(hex_str)
            match = vs.getSignature(bytez, offset=0)
            self.assertEqual(match, expected,
                             msg='Expected %s for %s, got %s' % (expected, hex_str, match))

    def test_msvc_masked_bytes_match(self):
        '''MSVC sigs with masked bytes match regardless of masked values.'''
        import binascii
        import vivisect.vamp.msvc as v_msvc

        vs = v_msvc.VisualStudioVamp()

        # seh3_prolog has masked bytes (push 0x00000000 → mask allows any dword)
        # Original: 680000000064a10000000050
        # With different masked bytes: 68deadbeef64a10000000050
        bytez = binascii.unhexlify('68deadbeef64a10000000050')
        match = vs.getSignature(bytez, offset=0)
        self.assertEqual(match, 'ntdll.seh3_prolog')

    def test_msvc_no_false_match(self):
        '''Random bytes that don't match any MSVC sig return None.'''
        import binascii
        import vivisect.vamp.msvc as v_msvc

        vs = v_msvc.VisualStudioVamp()
        bytez = binascii.unhexlify('ffffffffffffffffffffffffffffffff')
        match = vs.getSignature(bytez, offset=0)
        self.assertIsNone(match)
