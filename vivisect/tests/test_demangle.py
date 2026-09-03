"""
Tests for the vivisect.demangle library.

These tests verify:
    1. Format detection (detect_format)
    2. Dispatch to the correct format handler
    3. Graceful degradation (never crash on bad input)
    4. Structured output (DemangledSymbol)
    5. Normalization (@@VERSION suffixes, trailing NUL)
    6. Each format handler individually
"""

import unittest

from vivisect.demangle import (
    demangle, detect_format,
    DemangledSymbol, DemangleError,
    FORMAT_ITANIUM, FORMAT_MSVC, FORMAT_RUST, FORMAT_D,
    FORMAT_SWIFT, FORMAT_JNI, FORMAT_OBJC, FORMAT_UNKNOWN,
)
from vivisect.demangle.common import normalize_name


class TestDetectFormat(unittest.TestCase):
    """Test format auto-detection from symbol prefix."""

    def test_itanium_prefix(self):
        self.assertEqual(detect_format('_Z3foov'), FORMAT_ITANIUM)
        self.assertEqual(detect_format('_ZN3foo3barEv'), FORMAT_ITANIUM)
        self.assertEqual(detect_format('__Z3foov'), FORMAT_ITANIUM)
        self.assertEqual(detect_format('_ZTV1A'), FORMAT_ITANIUM)

    def test_msvc_prefix(self):
        self.assertEqual(detect_format('?foo@@YAXXZ'), FORMAT_MSVC)
        self.assertEqual(detect_format('??0MyClass@@QAE@H@Z'), FORMAT_MSVC)
        self.assertEqual(detect_format('??_7MyClass@@6B@'), FORMAT_MSVC)

    def test_rust_v0_prefix(self):
        self.assertEqual(detect_format('_RNvNtCs1234_7mycrate3foo3bar'), FORMAT_RUST)
        self.assertEqual(detect_format('_RNvCs1234_7mycrate3foo'), FORMAT_RUST)

    def test_d_prefix(self):
        self.assertEqual(detect_format('_Dmain'), FORMAT_D)
        self.assertEqual(detect_format('_D3foo3barFiZv'), FORMAT_D)

    def test_swift_prefix(self):
        self.assertEqual(detect_format('$s4Test3FooC'), FORMAT_SWIFT)
        self.assertEqual(detect_format('$S4Test3FooC'), FORMAT_SWIFT)
        self.assertEqual(detect_format('_T04Test3FooC'), FORMAT_SWIFT)

    def test_jni_prefix(self):
        self.assertEqual(detect_format('Java_pkg_Cls_f'), FORMAT_JNI)
        self.assertEqual(detect_format('Java_pkg_Cls_f__ILjava_lang_String_2'), FORMAT_JNI)

    def test_objc_prefix(self):
        self.assertEqual(detect_format('_OBJC_CLASS_$_NSObject'), FORMAT_OBJC)
        self.assertEqual(detect_format('_OBJC_METACLASS_$_NSObject'), FORMAT_OBJC)
        self.assertEqual(detect_format('_OBJC_IVAR_$_NSObject._isa'), FORMAT_OBJC)
        self.assertEqual(detect_format('+[NSObject alloc]'), FORMAT_OBJC)
        self.assertEqual(detect_format('-[NSObject init]'), FORMAT_OBJC)

    def test_unknown(self):
        self.assertEqual(detect_format('plain_symbol'), FORMAT_UNKNOWN)
        self.assertEqual(detect_format('main'), FORMAT_UNKNOWN)
        self.assertEqual(detect_format(''), FORMAT_UNKNOWN)
        self.assertEqual(detect_format('_start'), FORMAT_UNKNOWN)

    def test_global_not_d(self):
        """_GLOBAL_ symbols should not be detected as D format."""
        self.assertNotEqual(detect_format('_GLOBAL__sub_I_some_file.cpp'), FORMAT_D)

    def test_common_elf_symbols_not_d(self):
        """Common ELF symbols starting with _D must not be detected as D format."""
        # These are real ELF symbol names that must NOT route to D
        self.assertEqual(detect_format('_DYNAMIC'), FORMAT_UNKNOWN)
        self.assertEqual(detect_format('_DATA'), FORMAT_UNKNOWN)
        self.assertEqual(detect_format('_DWARF'), FORMAT_UNKNOWN)
        self.assertEqual(detect_format('_DEFAULT'), FORMAT_UNKNOWN)
        self.assertEqual(detect_format('_DTORS'), FORMAT_UNKNOWN)
        self.assertEqual(detect_format('_DTRACE'), FORMAT_UNKNOWN)
        # Real D symbols still detected correctly
        self.assertEqual(detect_format('_Dmain'), FORMAT_D)
        self.assertEqual(detect_format('_D3foo3barFiZv'), FORMAT_D)


class TestNormalizeName(unittest.TestCase):
    """Test name normalization."""

    def test_strip_version_suffix(self):
        self.assertEqual(normalize_name('foo@@GLIBC_2.4'), 'foo')
        self.assertEqual(normalize_name('foo@@GLIBC_2.17'), 'foo')
        self.assertEqual(normalize_name('_Z3foo@@GLIBC_2.4'), '_Z3foo')

    def test_msvc_atat_preserved(self):
        """MSVC symbols use @@ as scope terminator, not version suffix."""
        self.assertEqual(normalize_name('?foo@@YAXXZ'), '?foo@@YAXXZ')
        self.assertEqual(normalize_name('??0MyClass@@QAE@H@Z'), '??0MyClass@@QAE@H@Z')

    def test_trailing_nul(self):
        self.assertEqual(normalize_name('foo\x00'), 'foo')

    def test_empty(self):
        self.assertEqual(normalize_name(''), '')
        self.assertIsNone(normalize_name(None))

    def test_no_change(self):
        self.assertEqual(normalize_name('plain_name'), 'plain_name')
        self.assertEqual(normalize_name('_Z3foov'), '_Z3foov')


class TestDispatch(unittest.TestCase):
    """Test the main demangle() dispatch."""

    def test_itanium_dispatch(self):
        result = demangle('_ZN3foo3barEv')
        self.assertIsInstance(result, str)
        self.assertEqual(result, 'foo::bar()')

    def test_msvc_dispatch(self):
        """MSVC demangling is now implemented."""
        result = demangle('?foo@@YAXH@Z')
        self.assertEqual(result, 'void __cdecl foo(int)')

    def test_rust_dispatch(self):
        """Rust v0 demangling is now implemented."""
        result = demangle('_RNvCs1234_4test3foo')
        self.assertIsInstance(result, str)

    def test_jni_dispatch(self):
        result = demangle('Java_pkg_Cls_f__ILjava_lang_String_2')
        self.assertIsInstance(result, str)
        self.assertIn('pkg', result)

    def test_objc_dispatch(self):
        result = demangle('_OBJC_CLASS_$_NSObject')
        self.assertEqual(result, 'NSObject')
        result = demangle('+[NSObject alloc]')
        self.assertEqual(result, '+[NSObject alloc]')

    def test_unknown_returns_original(self):
        result = demangle('plain_symbol')
        self.assertEqual(result, 'plain_symbol')

    def test_empty_returns_empty(self):
        self.assertEqual(demangle(''), '')

    def test_force_format(self):
        """Test forcing a specific format."""
        result = demangle('_Z3foov', fmt=FORMAT_ITANIUM)
        self.assertEqual(result, 'foo()')

    def test_graceful_degradation(self):
        """demangle() should never raise on bad input."""
        bad_inputs = [
            '_Z',  # truncated
            '_Z!',  # invalid char
            '?',  # truncated MSVC
            '???',  # invalid MSVC
            '\x00\x01\x02',  # binary garbage
            'a' * 1000,  # very long
        ]
        for inp in bad_inputs:
            result = demangle(inp)
            self.assertIsInstance(result, str, 'demangle(%r) returned non-str' % inp)

    def test_version_suffix_stripped(self):
        """@@VERSION suffixes should be stripped."""
        result = demangle('foo@@GLIBC_2.4')
        self.assertEqual(result, 'foo')


class TestStructuredOutput(unittest.TestCase):
    """Test structured DemangledSymbol output."""

    def test_itanium_structured(self):
        sym = demangle('_ZN3foo3barEv', structured=True)
        self.assertIsInstance(sym, DemangledSymbol)
        self.assertEqual(sym.format, FORMAT_ITANIUM)
        self.assertEqual(sym.full_name, 'foo::bar()')
        self.assertEqual(sym.scope, ['foo'])
        self.assertEqual(sym.name, 'bar()')
        self.assertEqual(sym.kind, 'function')
        self.assertEqual(sym.original_mangled, '_ZN3foo3barEv')

    def test_itanium_vtable_structured(self):
        sym = demangle('_ZTV1A', structured=True)
        self.assertIsInstance(sym, DemangledSymbol)
        self.assertEqual(sym.kind, 'vtable')
        self.assertEqual(sym.name, 'A')

    def test_jni_structured(self):
        sym = demangle('Java_pkg_Cls_f__ILjava_lang_String_2', structured=True)
        self.assertIsInstance(sym, DemangledSymbol)
        self.assertEqual(sym.format, FORMAT_JNI)
        self.assertEqual(sym.kind, 'function')
        self.assertIn('int', sym.parameters)
        self.assertIn('java.lang.String', sym.parameters)

    def test_objc_structured(self):
        sym = demangle('_OBJC_CLASS_$_NSObject', structured=True)
        self.assertIsInstance(sym, DemangledSymbol)
        self.assertEqual(sym.format, FORMAT_OBJC)
        self.assertEqual(sym.kind, 'class_ref')
        self.assertEqual(sym.name, 'NSObject')

    def test_msvc_structured(self):
        sym = demangle('?foo@@YAXH@Z', structured=True)
        self.assertIsInstance(sym, DemangledSymbol)
        self.assertEqual(sym.format, FORMAT_MSVC)
        self.assertEqual(sym.full_name, 'void __cdecl foo(int)')

    def test_unknown_structured(self):
        sym = demangle('plain_symbol', structured=True)
        self.assertIsInstance(sym, DemangledSymbol)
        self.assertEqual(sym.format, FORMAT_UNKNOWN)
        self.assertEqual(sym.full_name, 'plain_symbol')

    def test_original_mangled_preserved_with_version_suffix(self):
        """original_mangled must preserve the true original, not the normalized form."""
        sym = demangle('_ZN3foo3barEv@@GLIBC_2.4', structured=True)
        self.assertEqual(sym.original_mangled, '_ZN3foo3barEv@@GLIBC_2.4')
        self.assertEqual(sym.full_name, 'foo::bar()')

    def test_original_mangled_preserved_plain(self):
        """original_mangled must match input when no normalization occurs."""
        sym = demangle('_ZN3foo3barEv', structured=True)
        self.assertEqual(sym.original_mangled, '_ZN3foo3barEv')

    def test_demangled_symbol_str(self):
        """DemangledSymbol.__str__ should return full_name."""
        sym = DemangledSymbol(full_name='foo::bar()')
        self.assertEqual(str(sym), 'foo::bar()')

    def test_demangled_symbol_to_dict(self):
        """DemangledSymbol.to_dict should return all slots."""
        sym = DemangledSymbol(format='itanium', full_name='foo()')
        d = sym.to_dict()
        self.assertEqual(d['format'], 'itanium')
        self.assertEqual(d['full_name'], 'foo()')
        self.assertIn('original_mangled', d)
        self.assertIn('parse_warnings', d)

    def test_demangled_symbol_eq(self):
        """DemangledSymbol.__eq__ should compare format and full_name."""
        a = DemangledSymbol(format='itanium', full_name='foo()')
        b = DemangledSymbol(format='itanium', full_name='foo()')
        c = DemangledSymbol(format='msvc', full_name='foo()')
        d = DemangledSymbol(format='itanium', full_name='bar()')
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertNotEqual(a, d)
        self.assertNotEqual(a, 'foo()')

    def test_demangled_symbol_hash(self):
        """DemangledSymbol.__hash__ should allow set/dict usage."""
        a = DemangledSymbol(format='itanium', full_name='foo()')
        b = DemangledSymbol(format='itanium', full_name='foo()')
        s = {a, b}
        self.assertEqual(len(s), 1)
        d = {a: 'val'}
        self.assertEqual(d[b], 'val')

    def test_demangled_symbol_repr(self):
        """DemangledSymbol.__repr__ should include format and full_name."""
        sym = DemangledSymbol(format='itanium', full_name='foo()')
        r = repr(sym)
        self.assertIn('itanium', r)
        self.assertIn('foo()', r)


class TestItaniumDemangle(unittest.TestCase):
    """Test Itanium ABI demangling (via cxxfilt fallback in Phase 0)."""

    def test_simple_function(self):
        self.assertEqual(demangle('_Z3foov'), 'foo()')

    def test_nested_name(self):
        self.assertEqual(demangle('_ZN3foo3barEv'), 'foo::bar()')

    def test_std_namespace(self):
        self.assertEqual(demangle('_ZSt5state'), 'std::state')

    def test_vtable(self):
        self.assertEqual(demangle('_ZTV1A'), 'vtable for A')

    def test_typeinfo(self):
        self.assertEqual(demangle('_ZTI1A'), 'typeinfo for A')

    def test_typeinfo_name(self):
        self.assertEqual(demangle('_ZTS1A'), 'typeinfo name for A')

    def test_template(self):
        result = demangle('_ZN1N1TIiiE2mfES0_IddE')
        self.assertIn('N::T', result)

    def test_version_suffix(self):
        """Itanium symbols with @@VERSION should be demangled after stripping."""
        # _Z3foo is a data name (no bare-function-type), so demangles to 'foo'
        self.assertEqual(demangle('_Z3foo@@GLIBC_2.4'), 'foo')
        # _Z3foov is a function (v = void params), demangles to 'foo()'
        self.assertEqual(demangle('_Z3foov@@GLIBC_2.4'), 'foo()')

    def test_pointer_to_member_function(self):
        """Pointer-to-member function types with CV/ref qualifiers."""
        # const & ref-qualifier
        self.assertEqual(demangle('_Z1fM1AKFvvRE'),
                         'f(void (A::*)() const &)')
        # const only, no ref
        self.assertEqual(demangle('_Z1fM1AKFvvE'),
                         'f(void (A::*)() const)')
        # no CV, no ref
        self.assertEqual(demangle('_Z1fM1AFvvE'),
                         'f(void (A::*)())')
        # ref only, no const
        self.assertEqual(demangle('_Z1fM1AFvvRE'),
                         'f(void (A::*)() &)')
        # const && (rvalue ref)
        self.assertEqual(demangle('_Z1fM1AKFvvOE'),
                         'f(void (A::*)() const &&)')

    def test_pointer_to_member_data(self):
        """Pointer-to-member data (non-function member type)."""
        # M <class> <type> where type is not a function
        # _Z1fM1Ai => f(int A::*)
        result = demangle('_Z1fM1Ai')
        self.assertIn('A::*', result)
        self.assertIn('int', result)


class TestJNIDemangle(unittest.TestCase):
    """Test JNI native method name demangling."""

    def test_simple_method(self):
        result = demangle('Java_pkg_Cls_f')
        self.assertIn('pkg', result)
        self.assertIn('Cls', result)
        self.assertIn('f', result)

    def test_overloaded_method(self):
        result = demangle('Java_pkg_Cls_f__ILjava_lang_String_2')
        self.assertIn('int', result)
        self.assertIn('java.lang.String', result)

    def test_structured(self):
        sym = demangle('Java_pkg_Cls_f__ILjava_lang_String_2', structured=True)
        self.assertEqual(sym.kind, 'function')
        self.assertIn('int', sym.parameters)


class TestObjCDemangle(unittest.TestCase):
    """Test Objective-C symbol demangling."""

    def test_class_ref(self):
        self.assertEqual(demangle('_OBJC_CLASS_$_NSObject'), 'NSObject')

    def test_metaclass_ref(self):
        self.assertEqual(demangle('_OBJC_METACLASS_$_NSObject'), 'NSObject')

    def test_ivar(self):
        result = demangle('_OBJC_IVAR_$_NSObject._isa')
        self.assertIn('NSObject', result)

    def test_method_syntax(self):
        self.assertEqual(demangle('+[NSObject alloc]'), '+[NSObject alloc]')
        self.assertEqual(demangle('-[NSObject init]'), '-[NSObject init]')


if __name__ == '__main__':
    unittest.main()