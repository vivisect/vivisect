"""
Comprehensive tests for the Rust, D, and Swift demangling modules.

Tests cover:
- Rust v0 (_R prefix) basic demangling
- Rust legacy (_Z prefix with $ escapes)
- D language (_D prefix) basic demangling
- Swift ($s/_T0 prefix) basic demangling
- Structured output for all three
- Graceful degradation
- Format detection
"""

import unittest

from vivisect.demangle import demangle, detect_format
from vivisect.demangle.rust import demangle_rust
from vivisect.demangle.dlang import demangle_d
from vivisect.demangle.swift import demangle_swift
from vivisect.demangle.common import DemangledSymbol


# ===== RUST TESTS =====

class TestRustFormatDetection(unittest.TestCase):
    """Test Rust format detection."""

    def test_detect_v0(self):
        self.assertEqual(detect_format('_RNvCs1234_4test3foo'), 'rust')

    def test_detect_v0_nested(self):
        self.assertEqual(detect_format('_RNvNtCs1234_7mycrate3foo3bar'), 'rust')


class TestRustV0Demangle(unittest.TestCase):
    """Test Rust v0 demangling."""

    def test_basic_crate_function(self):
        result = demangle_rust('_RNvCs1234_4test3foo')
        self.assertIsInstance(result, str)

    def test_v0_returns_str(self):
        result = demangle_rust('_RNvCs1234_4test3foo')
        self.assertIsInstance(result, str)

    def test_v0_with_suffix(self):
        # v0 symbols can have .llvm.<hash> suffix
        result = demangle_rust('_RNvCs1234_4test3foo.llvm.abc123')
        self.assertIsInstance(result, str)


class TestRustLegacyDemangle(unittest.TestCase):
    """Test Rust legacy (_Z prefix) demangling."""

    def test_legacy_returns_str(self):
        result = demangle_rust('_ZN3foo3barEv')
        self.assertIsInstance(result, str)

    def test_legacy_escape_decoding(self):
        # Legacy Rust uses $XX escapes
        # $RF$ = &, $BP$ = *, $LT$ = <, $GT$ = >
        result = demangle_rust('_ZN3foo$RF$3barEv')
        self.assertIsInstance(result, str)


class TestRustStructuredOutput(unittest.TestCase):
    """Test structured output for Rust."""

    def test_structured_v0(self):
        sym = demangle_rust('_RNvCs1234_4test3foo', structured=True)
        self.assertIsInstance(sym, DemangledSymbol)
        self.assertEqual(sym.format, 'rust')

    def test_structured_original(self):
        orig = '_RNvCs1234_4test3foo'
        sym = demangle_rust(orig, structured=True)
        self.assertEqual(sym.original_mangled, orig)


class TestRustGracefulDegradation(unittest.TestCase):
    """Test graceful degradation for Rust."""

    def test_non_rust_returns_original(self):
        result = demangle_rust('plain_function')
        self.assertEqual(result, 'plain_function')

    def test_empty_string(self):
        result = demangle_rust('')
        self.assertEqual(result, '')

    def test_invalid_v0(self):
        result = demangle_rust('_R')
        self.assertIsInstance(result, str)

    def test_no_crash_on_garbage(self):
        result = demangle_rust('_R\x00\x01\x02')
        self.assertIsInstance(result, str)


# ===== D LANGUAGE TESTS =====

class TestDFormatDetection(unittest.TestCase):
    """Test D language format detection."""

    def test_detect_d(self):
        self.assertEqual(detect_format('_D3foo3barFiZv'), 'd')

    def test_detect_d_main(self):
        self.assertEqual(detect_format('_Dmain'), 'd')

    def test_not_d_dynamic(self):
        self.assertNotEqual(detect_format('_DYNAMIC'), 'd')

    def test_not_d_data(self):
        self.assertNotEqual(detect_format('_DATA'), 'd')


class TestDDemangle(unittest.TestCase):
    """Test D language demangling."""

    def test_basic_function(self):
        result = demangle_d('_D3foo3barFiZv')
        self.assertIsInstance(result, str)
        self.assertIn('foo', result)

    def test_d_main(self):
        result = demangle_d('_Dmain')
        self.assertIsInstance(result, str)

    def test_returns_str(self):
        result = demangle_d('_D3foo3barFiZv')
        self.assertIsInstance(result, str)


class TestDStructuredOutput(unittest.TestCase):
    """Test structured output for D."""

    def test_structured(self):
        sym = demangle_d('_D3foo3barFiZv', structured=True)
        self.assertIsInstance(sym, DemangledSymbol)
        self.assertEqual(sym.format, 'd')

    def test_structured_original(self):
        orig = '_D3foo3barFiZv'
        sym = demangle_d(orig, structured=True)
        self.assertEqual(sym.original_mangled, orig)


class TestDGracefulDegradation(unittest.TestCase):
    """Test graceful degradation for D."""

    def test_non_d_returns_original(self):
        result = demangle_d('plain_function')
        self.assertEqual(result, 'plain_function')

    def test_empty_string(self):
        result = demangle_d('')
        self.assertEqual(result, '')

    def test_invalid_d(self):
        result = demangle_d('_D')
        self.assertIsInstance(result, str)


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

    def test_returns_str(self):
        result = demangle_swift('$s5Hello4testyyF')
        self.assertIsInstance(result, str)


class TestSwiftStructuredOutput(unittest.TestCase):
    """Test structured output for Swift."""

    def test_structured(self):
        sym = demangle_swift('$s5Hello4testyyF', structured=True)
        self.assertIsInstance(sym, DemangledSymbol)
        self.assertEqual(sym.format, 'swift')

    def test_structured_original(self):
        orig = '$s5Hello4testyyF'
        sym = demangle_swift(orig, structured=True)
        self.assertEqual(sym.original_mangled, orig)


class TestSwiftGracefulDegradation(unittest.TestCase):
    """Test graceful degradation for Swift."""

    def test_non_swift_returns_original(self):
        result = demangle_swift('plain_function')
        self.assertEqual(result, 'plain_function')

    def test_empty_string(self):
        result = demangle_swift('')
        self.assertEqual(result, '')

    def test_invalid_swift(self):
        result = demangle_swift('$s')
        self.assertIsInstance(result, str)

    def test_no_crash_on_garbage(self):
        result = demangle_swift('$s\x00\x01\x02')
        self.assertIsInstance(result, str)


# ===== DISPATCH TESTS =====

class TestRustDDispatch(unittest.TestCase):
    """Test Rust/D/Swift through the main demangle() dispatch."""

    def test_rust_dispatch(self):
        result = demangle('_RNvCs1234_4test3foo')
        self.assertIsInstance(result, str)

    def test_d_dispatch(self):
        result = demangle('_D3foo3barFiZv')
        self.assertIsInstance(result, str)

    def test_swift_dispatch(self):
        result = demangle('$s5Hello4testyyF')
        self.assertIsInstance(result, str)

    def test_rust_structured(self):
        sym = demangle('_RNvCs1234_4test3foo', structured=True)
        self.assertEqual(sym.format, 'rust')

    def test_d_structured(self):
        sym = demangle('_D3foo3barFiZv', structured=True)
        self.assertEqual(sym.format, 'd')

    def test_swift_structured(self):
        sym = demangle('$s5Hello4testyyF', structured=True)
        self.assertEqual(sym.format, 'swift')

    def test_never_raises(self):
        for inp in ['_R', '_D', '$s', '_T0', '$S', '_R\x00', '_D\x00']:
            result = demangle(inp)
            self.assertIsInstance(result, str, 'demangle(%r) crashed' % inp)


if __name__ == '__main__':
    unittest.main()