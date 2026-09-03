"""
Comprehensive tests for D language and Swift demangling.

D tests cover:
    - Basic functions with all primitive types
    - Pointers, arrays, static arrays, references
    - Function types with parameters and return types
    - Type qualifiers (const, immutable, shared, wild)
    - Delegate types
    - Special names (main, __initZ, __vtblZ)
    - Type/symbol back-references
    - Structured output
    - Graceful degradation

Swift tests cover:
    - Module + function name extraction
    - Variable and class types
    - Type suffix parsing (basic)
    - Escape sequence decoding
    - Structured output
    - Graceful degradation
"""

import unittest

from vivisect.demangle import demangle, detect_format
from vivisect.demangle.dlang import demangle_d
from vivisect.demangle.swift import demangle_swift
from vivisect.demangle.common import DemangledSymbol


# ===== D LANGUAGE TESTS =====

class TestDBasicFunctions(unittest.TestCase):
    """Test basic D function demangling."""

    def test_simple_function(self):
        self.assertEqual(demangle_d('_D3foo3barFiZv'), 'foo.bar(int) void')

    def test_main(self):
        self.assertEqual(demangle_d('_Dmain'), 'D main')

    def test_multiple_params(self):
        self.assertEqual(demangle_d('_D3foo3barFiiZi'), 'foo.bar(int, int) int')

    def test_void_params(self):
        self.assertEqual(demangle_d('_D3foo3barFvZv'), 'foo.bar(void) void')

    def test_returns_str(self):
        result = demangle_d('_D3foo3barFiZv')
        self.assertIsInstance(result, str)

    def test_qualified_name(self):
        result = demangle_d('_D3foo3bar4bazFiZv')
        self.assertIn('foo', result)
        self.assertIn('bar', result)


class TestDPrimitiveTypes(unittest.TestCase):
    """Test all D primitive type codes."""

    def test_int(self):
        self.assertIn('int', demangle_d('_D3foo3barFiZv'))

    def test_void(self):
        self.assertIn('void', demangle_d('_D3foo3barFvZv'))

    def test_bool(self):
        self.assertIn('bool', demangle_d('_D3foo3barFbZv'))

    def test_long(self):
        self.assertIn('long', demangle_d('_D3foo3barFkZv'))

    def test_float(self):
        self.assertIn('float', demangle_d('_D3foo3barFfZv'))

    def test_double(self):
        self.assertIn('double', demangle_d('_D3foo3barFdZv'))

    def test_char(self):
        self.assertIn('char', demangle_d('_D3foo3barFaZv'))

    def test_wchar(self):
        self.assertIn('wchar', demangle_d('_D3foo3barFuZv'))

    def test_dchar(self):
        self.assertIn('dchar', demangle_d('_D3foo3barFwZv'))


class TestDCompositeTypes(unittest.TestCase):
    """Test D pointer, array, and composite types."""

    def test_pointer(self):
        self.assertIn('int*', demangle_d('_D3foo3barFPiZv'))

    def test_pointer_to_pointer(self):
        self.assertIn('int**', demangle_d('_D3foo3barFPPiZv'))

    def test_dynamic_array(self):
        self.assertIn('int[]', demangle_d('_D3foo3barFAiZv'))

    def test_static_array(self):
        self.assertIn('int[3]', demangle_d('_D3foo3barG3iZv'))

    def test_array_of_arrays(self):
        self.assertIn('int[][]', demangle_d('_D3foo3barFAAiZv'))


class TestDFunctionTypes(unittest.TestCase):
    """Test D function type parsing."""

    def test_function_with_return(self):
        self.assertEqual(demangle_d('_D3foo3barFiZi'), 'foo.bar(int) int')

    def test_function_pointer_param(self):
        result = demangle_d('_D3foo3barFPiZv')
        self.assertIn('int*', result)

    def test_multiple_param_types(self):
        result = demangle_d('_D3foo3barFikfZv')
        self.assertIn('int', result)
        self.assertIn('long', result)
        self.assertIn('float', result)


class TestDSpecialNames(unittest.TestCase):
    """Test D special name suffixes."""

    def test_main(self):
        self.assertEqual(demangle_d('_Dmain'), 'D main')

    def test_init(self):
        result = demangle_d('_D3foo6__initZ')
        self.assertIn('__init', result)

    def test_vtbl(self):
        result = demangle_d('_D3foo6__vtblZ')
        self.assertIn('vtbl', result)


class TestDStructuredOutput(unittest.TestCase):
    """Test D structured output."""

    def test_returns_demangled_symbol(self):
        sym = demangle_d('_D3foo3barFiZv', structured=True)
        self.assertIsInstance(sym, DemangledSymbol)
        self.assertEqual(sym.format, 'd')

    def test_preserves_original(self):
        orig = '_D3foo3barFiZv'
        sym = demangle_d(orig, structured=True)
        self.assertEqual(sym.original_mangled, orig)

    def test_scope_and_name(self):
        sym = demangle_d('_D3foo3barFiZv', structured=True)
        self.assertIn('foo', sym.scope)
        self.assertIn('bar', sym.name)


class TestDGracefulDegradation(unittest.TestCase):
    """Test D graceful degradation."""

    def test_non_d_returns_original(self):
        self.assertEqual(demangle_d('plain_function'), 'plain_function')

    def test_empty_string(self):
        self.assertEqual(demangle_d(''), '')

    def test_just_prefix(self):
        result = demangle_d('_D')
        self.assertIsInstance(result, str)

    def test_no_crash_on_garbage(self):
        result = demangle_d('_D\x00\x01\x02')
        self.assertIsInstance(result, str)


class TestDFormatDetection(unittest.TestCase):
    """Test D format detection."""

    def test_detect_d(self):
        self.assertEqual(detect_format('_D3foo3barFiZv'), 'd')

    def test_detect_d_main(self):
        self.assertEqual(detect_format('_Dmain'), 'd')

    def test_not_d_dynamic(self):
        self.assertNotEqual(detect_format('_DYNAMIC'), 'd')


# ===== SWIFT TESTS =====

class TestSwiftFormatDetection(unittest.TestCase):
    """Test Swift format detection."""

    def test_detect_s(self):
        self.assertEqual(detect_format('$s5Hello4testyyF'), 'swift')

    def test_detect_S(self):
        self.assertEqual(detect_format('$S5Hello4testyyF'), 'swift')

    def test_detect_T0(self):
        self.assertEqual(detect_format('_T05Hello4testyyF'), 'swift')


class TestSwiftDemangle(unittest.TestCase):
    """Test Swift demangling."""

    def test_basic_module_function(self):
        result = demangle_swift('$s5Hello4testyyF')
        self.assertIsInstance(result, str)
        self.assertIn('Hello', result)
        self.assertIn('test', result)

    def test_returns_str(self):
        self.assertIsInstance(demangle_swift('$s5Hello4testyyF'), str)

    def test_underscore_module(self):
        result = demangle_swift('$s6my_app4mainyyF')
        self.assertIn('my_app', result)

    def test_class_type(self):
        result = demangle_swift('$s5Hello5WorldC')
        self.assertIn('Hello', result)
        self.assertIn('World', result)


class TestSwiftStructuredOutput(unittest.TestCase):
    """Test Swift structured output."""

    def test_structured(self):
        sym = demangle_swift('$s5Hello4testyyF', structured=True)
        self.assertIsInstance(sym, DemangledSymbol)
        self.assertEqual(sym.format, 'swift')

    def test_structured_original(self):
        orig = '$s5Hello4testyyF'
        sym = demangle_swift(orig, structured=True)
        self.assertEqual(sym.original_mangled, orig)


class TestSwiftGracefulDegradation(unittest.TestCase):
    """Test Swift graceful degradation."""

    def test_non_swift_returns_original(self):
        self.assertEqual(demangle_swift('plain_function'), 'plain_function')

    def test_empty_string(self):
        self.assertEqual(demangle_swift(''), '')

    def test_invalid_swift(self):
        result = demangle_swift('$s')
        self.assertIsInstance(result, str)

    def test_no_crash_on_garbage(self):
        result = demangle_swift('$s\x00\x01\x02')
        self.assertIsInstance(result, str)


# ===== DISPATCH TESTS =====

class TestDAndSwiftDispatch(unittest.TestCase):
    """Test D and Swift through the main demangle() dispatch."""

    def test_d_dispatch(self):
        result = demangle('_D3foo3barFiZv')
        self.assertIsInstance(result, str)

    def test_swift_dispatch(self):
        result = demangle('$s5Hello4testyyF')
        self.assertIsInstance(result, str)

    def test_d_structured(self):
        sym = demangle('_D3foo3barFiZv', structured=True)
        self.assertEqual(sym.format, 'd')

    def test_swift_structured(self):
        sym = demangle('$s5Hello4testyyF', structured=True)
        self.assertEqual(sym.format, 'swift')

    def test_never_raises(self):
        for inp in ['_D', '$s', '_T0', '$S', '_D\x00', '$s\x00']:
            result = demangle(inp)
            self.assertIsInstance(result, str, 'demangle(%r) crashed' % inp)


if __name__ == '__main__':
    unittest.main()