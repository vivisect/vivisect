import os
import unittest

import PE
import vivisect.tests.helpers as helpers

class PETests(unittest.TestCase):

    def test_export_by_name(self):
        file_path = helpers.getTestPath('windows', 'i386', 'export_by_name.dll')
        pe = PE.peFromFileName(file_path)
        export_list = pe.getExports()
        self.assertEqual(len(export_list), 2, "expecting 2 exported functions")
        self.assertEqual(export_list[0][1], 0, "exported function with ordinal 0 not found")
        self.assertEqual(export_list[0][2], "Func1", "exported function with name 'Func1' not found")
        self.assertEqual(export_list[1][1], 1, "exported function with ordinal 1 not found")
        self.assertEqual(export_list[1][2], "Func2", "exported function with name 'Func2' not found")

    def test_export_by_ordinal_base_01(self):
        file_path = helpers.getTestPath('windows', 'i386', 'export_by_ordinal_base_01.dll')
        pe = PE.peFromFileName(file_path)
        export_list = pe.getExports()
        self.assertEqual(len(export_list), 2, "expecting 2 exported functions")
        self.assertEqual(export_list[0][1], 1, "exported function with ordinal 1 not found")
        self.assertEqual(export_list[1][1], 2, "exported function with ordinal 2 not found")

    def test_export_by_ordinal_base_45(self):
        file_path = helpers.getTestPath('windows', 'i386', 'export_by_ordinal_base_45.dll')
        pe = PE.peFromFileName(file_path)
        export_list = pe.getExports()
        self.assertEqual(len(export_list), 2, "expecting 2 exported functions")
        self.assertEqual(export_list[0][1], 45, "exported function with ordinal 45 not found")
        self.assertEqual(export_list[1][1], 55, "exported function with ordinal 55 not found")
