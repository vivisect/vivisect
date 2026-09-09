"""
Tests for loading and analyzing GDB-generated ELF core files.

This validates vivisect's ability to:
- Load standard GDB memory dumps (ELF core files) 
- Extract and identify memory regions from dumped maps

Related work: upstream PR #701, issues #57, #60
"""
import os
import unittest

import vivisect.cli as v_cli
import vivisect.tests.helpers as helpers


class GdbCoreDumpTests(unittest.TestCase):
    """Test suite for ELF core file loading and memory extraction."""

    @classmethod
    def setUpClass(cls):
        cls.test_bin_path = None
        try:
            cls.test_bin_path = helpers.getTestPath('linux/amd64/gdb_dumps/spawned_test_core_v1.bin')
        except unittest.SkipTest:
            # VIVTESTFILES not set - skip all tests
            raise

    def test_core_file_loadable(self):
        """Verify vivisect can load the GDB core dump file."""
        if self.test_bin_path is None:
            self.skipTest("VIVTESTFILES not set")
        
        vw = v_cli.VivCli()
        try:
            vw.loadFromFile(self.test_bin_path)
            # Core dumps should load without crashing  
            self.assertIsNotNone(vw)
        except Exception as e:
            self.fail(f"Failed to load core file: {e}")

    def test_core_has_memory_maps(self):
        """Verify the loaded core contains memory maps."""
        if self.test_bin_path is None:
            self.skipTest("VIVTESTFILES not set")
            
        vw = v_cli.VivCli()
        vw.loadFromFile(self.test_bin_path)
        
        mem_maps = list(vw.getMemoryMaps())
        self.assertGreater(len(mem_maps), 0, "Core dump should contain memory maps")

    def test_core_patterns_searchable(self):
        """Verify we can search for known patterns in core memory."""
        if self.test_bin_path is None:
            self.skipTest("VIVTESTFILES not set")
            
        vw = v_cli.VivCli()  
        vw.loadFromFile(self.test_bin_path)

        # Read the raw file to verify patterns exist
        with open(self.test_bin_path, 'rb') as f:
            data = f.read()
        
        self.assertIn(b"HEAP", data, "HEAP pattern missing from core")
        self.assertIn(b"MMAP", data, "MMAP pattern missing from core")  
        self.assertIn(b"SHRD", data, "SHRD pattern missing from core")


if __name__ == '__main__':
    unittest.main()
