"""
Comprehensive tests for the shared demangle infrastructure.

Tests cover:
- Format detection (all formats, edge cases, false positives)
- Main dispatch (demangle() routing to correct handler)
- Name normalization (@@VERSION, NUL, MSVC preservation)
- DemangledSymbol (all attributes, methods, equality, hashing)
- Symbol class (from_demangled_symbol, structured property, to_dict)
- Graceful degradation (never crash on any input)
- Force-format override
- Structured vs string output
"""

import unittest

from vivisect.demangle import (
    demangle, detect_format,
    DemangledSymbol, DemangleError,
    FORMAT_ITANIUM, FORMAT_MSVC, FORMAT_RUST, FORMAT_D,
    FORMAT_SWIFT, FORMAT_JNI, FORMAT_OBJC, FORMAT_UNKNOWN,
)
from vivisect.demangle.common import normalize_name
from vivisect.demangle.symbol import Symbol


class TestFormatDetection(unittest.TestCase):
    """Comprehensive format detection tests."""

    # --- Itanium ---
    def test_itanium_z(self):
        self.assertEqual(detect_format('_Z3foov'), FORMAT_ITANIUM)
        self.assertEqual(detect_format('_ZN3foo3barEv'), FORMAT_ITANIUM)

    def test_itanium_double_z(self):
        self.assertEqual(detect_format('__Z3foov'), FORMAT_ITANIUM)

    def test_itanium_vtable(self):
        self.assertEqual(detect_format('_ZTV1A'), FORMAT_ITANIUM)

    def test_itanium_typeinfo(self):
        self.assertEqual(detect_format('_ZTI1A'), FORMAT_ITANIUM)

    # --- MSVC ---
    def test_msvc_question(self):
        self.assertEqual(detect_format('?foo@@YAXH@Z'), FORMAT_MSVC)

    def test_msvc_ctor(self):
        self.assertEqual(detect_format('??0MyClass@@QAE@X@Z'), FORMAT_MSVC)

    def test_msvc_dtor(self):
        self.assertEqual(detect_format('??1MyClass@@UAE@X@Z'), FORMAT_MSVC)

    def test_msvc_vtable(self):
        self.assertEqual(detect_format('??_7MyClass@@6B@'), FORMAT_MSVC)

    def test_msvc_operator(self):
        self.assertEqual(detect_format('??2@YAPAXI@Z'), FORMAT_MSVC)

    # --- Rust ---
    def test_rust_v0(self):
        self.assertEqual(detect_format('_RNvCs1234_4test3foo'), FORMAT_RUST)

    # --- D ---
    def test_d_with_digit(self):
        self.assertEqual(detect_format('_D3foo3barFiZv'), FORMAT_D)

    def test_d_main(self):
        self.assertEqual(detect_format('_Dmain'), FORMAT_D)

    # --- Swift ---
    def test_swift_s(self):
        self.assertEqual(detect_format('$s5Hello4testyyF'), FORMAT_SWIFT)

    def test_swift_S(self):
        self.assertEqual(detect_format('$S5Hello4testyyF'), FORMAT_SWIFT)

    def test_swift_T0(self):
        self.assertEqual(detect_format('_T05Hello4testyyF'), FORMAT_SWIFT)

    # --- JNI ---
    def test_jni_prefix(self):
        self.assertEqual(detect_format('Java_pkg_Cls_f'), FORMAT_JNI)

    def test_jni_overloaded(self):
        self.assertEqual(detect_format('Java_pkg_Cls_f__ILjava_lang_String_2'),
                         FORMAT_JNI)

    # --- ObjC ---
    def test_objc_class(self):
        self.assertEqual(detect_format('_OBJC_CLASS_$_NSObject'), FORMAT_OBJC)

    def test_objc_metaclass(self):
        self.assertEqual(detect_format('_OBJC_METACLASS_$_NSObject'),
                         FORMAT_OBJC)

    def test_objc_ivar(self):
        self.assertEqual(detect_format('_OBJC_IVAR_$_NSObject._isa'),
                         FORMAT_OBJC)

    def test_objc_class_method(self):
        self.assertEqual(detect_format('+[NSObject alloc]'), FORMAT_OBJC)

    def test_objc_instance_method(self):
        self.assertEqual(detect_format('-[NSObject init]'), FORMAT_OBJC)

    # --- Unknown ---
    def test_unknown_plain(self):
        self.assertEqual(detect_format('plain_symbol'), FORMAT_UNKNOWN)

    def test_unknown_main(self):
        self.assertEqual(detect_format('main'), FORMAT_UNKNOWN)

    def test_unknown_empty(self):
        self.assertEqual(detect_format(''), FORMAT_UNKNOWN)

    def test_unknown_start(self):
        self.assertEqual(detect_format('_start'), FORMAT_UNKNOWN)

    # --- False positive prevention ---
    def test_dynamic_not_d(self):
        self.assertNotEqual(detect_format('_DYNAMIC'), FORMAT_D)

    def test_data_not_d(self):
        self.assertNotEqual(detect_format('_DATA'), FORMAT_D)

    def test_dwarf_not_d(self):
        self.assertNotEqual(detect_format('_DWARF'), FORMAT_D)

    def test_global_not_d(self):
        self.assertNotEqual(detect_format('_GLOBAL__sub_I_some_file'), FORMAT_D)


class TestNormalization(unittest.TestCase):
    """Test name normalization."""

    def test_strip_glibc_suffix(self):
        self.assertEqual(normalize_name('foo@@GLIBC_2.4'), 'foo')

    def test_strip_glibc_217(self):
        self.assertEqual(normalize_name('foo@@GLIBC_2.17'), 'foo')

    def test_strip_itanium_with_suffix(self):
        self.assertEqual(normalize_name('_Z3foo@@GLIBC_2.4'), '_Z3foo')

    def test_msvc_atat_preserved(self):
        """MSVC symbols use @@ as scope terminator, not version suffix."""
        self.assertEqual(normalize_name('?foo@@YAXXZ'), '?foo@@YAXXZ')
        self.assertEqual(normalize_name('??0MyClass@@QAE@H@Z'),
                         '??0MyClass@@QAE@H@Z')

    def test_strip_trailing_nul(self):
        self.assertEqual(normalize_name('foo\x00'), 'foo')

    def test_empty(self):
        self.assertEqual(normalize_name(''), '')

    def test_none(self):
        self.assertIsNone(normalize_name(None))

    def test_no_change(self):
        self.assertEqual(normalize_name('plain_name'), 'plain_name')
        self.assertEqual(normalize_name('_Z3foov'), '_Z3foov')

    def test_no_version_suffix(self):
        self.assertEqual(normalize_name('?foo@@YAXH@Z'), '?foo@@YAXH@Z')


class TestDemangledSymbol(unittest.TestCase):
    """Test DemangledSymbol class thoroughly."""

    def test_default_construction(self):
        sym = DemangledSymbol()
        self.assertIsNone(sym.format)
        self.assertEqual(sym.full_name, '')
        self.assertEqual(sym.name, '')
        self.assertEqual(sym.kind, 'unknown')
        self.assertEqual(sym.scope, [])
        self.assertEqual(sym.parameters, [])
        self.assertEqual(sym.parse_warnings, [])
        self.assertEqual(sym.template_args, [])
        self.assertFalse(sym.is_template)
        self.assertFalse(sym.is_member)
        self.assertFalse(sym.is_static)
        self.assertFalse(sym.is_virtual)

    def test_full_construction(self):
        sym = DemangledSymbol(
            format='itanium',
            full_name='foo::bar(int)',
            name='bar(int)',
            kind='function',
            scope=['foo'],
            is_template=True,
            template_args=['int'],
            is_member=True,
            is_static=False,
            is_virtual=True,
            access='public',
            calling_convention='cdecl',
            return_type='void',
            parameters=['int'],
            cv_qualifiers='const',
            ref_qualifier='&',
            original_mangled='_ZN3foo3barEi',
        )
        self.assertEqual(sym.format, 'itanium')
        self.assertEqual(sym.full_name, 'foo::bar(int)')
        self.assertTrue(sym.is_template)
        self.assertTrue(sym.is_virtual)
        self.assertEqual(sym.access, 'public')

    def test_str(self):
        sym = DemangledSymbol(full_name='foo::bar()')
        self.assertEqual(str(sym), 'foo::bar()')

    def test_repr(self):
        sym = DemangledSymbol(format='itanium', full_name='foo()')
        r = repr(sym)
        self.assertIn('itanium', r)
        self.assertIn('foo()', r)

    def test_eq_same(self):
        a = DemangledSymbol(format='itanium', full_name='foo()')
        b = DemangledSymbol(format='itanium', full_name='foo()')
        self.assertEqual(a, b)

    def test_eq_different_format(self):
        a = DemangledSymbol(format='itanium', full_name='foo()')
        b = DemangledSymbol(format='msvc', full_name='foo()')
        self.assertNotEqual(a, b)

    def test_eq_different_name(self):
        a = DemangledSymbol(format='itanium', full_name='foo()')
        b = DemangledSymbol(format='itanium', full_name='bar()')
        self.assertNotEqual(a, b)

    def test_eq_non_symbol(self):
        a = DemangledSymbol(format='itanium', full_name='foo()')
        self.assertNotEqual(a, 'foo()')
        self.assertNotEqual(a, 42)

    def test_hash(self):
        a = DemangledSymbol(format='itanium', full_name='foo()')
        b = DemangledSymbol(format='itanium', full_name='foo()')
        s = {a, b}
        self.assertEqual(len(s), 1)

    def test_hash_in_dict(self):
        a = DemangledSymbol(format='itanium', full_name='foo()')
        b = DemangledSymbol(format='itanium', full_name='foo()')
        d = {a: 'value'}
        self.assertEqual(d[b], 'value')

    def test_to_dict(self):
        sym = DemangledSymbol(format='itanium', full_name='foo()')
        d = sym.to_dict()
        self.assertEqual(d['format'], 'itanium')
        self.assertEqual(d['full_name'], 'foo()')
        self.assertIn('original_mangled', d)
        self.assertIn('parse_warnings', d)
        self.assertIn('scope', d)
        self.assertIn('parameters', d)

    def test_all_slots_in_to_dict(self):
        sym = DemangledSymbol(format='msvc', full_name='x')
        d = sym.to_dict()
        expected_keys = {
            'format', 'full_name', 'kind', 'scope', 'name',
            'is_template', 'template_args', 'is_member', 'is_static',
            'is_virtual', 'access', 'calling_convention', 'return_type',
            'parameters', 'cv_qualifiers', 'ref_qualifier',
            'this_adjustment', 'abi_tags', 'storage_class',
            'original_mangled', 'parse_warnings',
        }
        self.assertEqual(set(d.keys()), expected_keys)


class TestSymbolClass(unittest.TestCase):
    """Test the Symbol wrapper class."""

    def test_construction(self):
        sym = Symbol(original='_Z3foov', demangled='foo()',
                     format='itanium', kind='function')
        self.assertEqual(sym.original, '_Z3foov')
        self.assertEqual(sym.demangled, 'foo()')
        self.assertEqual(sym.format, 'itanium')
        self.assertEqual(sym.kind, 'function')

    def test_default_demangled_is_original(self):
        sym = Symbol(original='plain')
        self.assertEqual(sym.demangled, 'plain')

    def test_str(self):
        sym = Symbol(demangled='foo::bar()')
        self.assertEqual(str(sym), 'foo::bar()')

    def test_repr(self):
        sym = Symbol(format='itanium', demangled='foo()')
        r = repr(sym)
        self.assertIn('itanium', r)
        self.assertIn('foo()', r)

    def test_eq(self):
        a = Symbol(demangled='foo()', format='itanium')
        b = Symbol(demangled='foo()', format='itanium')
        self.assertEqual(a, b)

    def test_eq_different(self):
        a = Symbol(demangled='foo()', format='itanium')
        b = Symbol(demangled='bar()', format='itanium')
        self.assertNotEqual(a, b)

    def test_hash(self):
        a = Symbol(demangled='foo()', format='itanium')
        b = Symbol(demangled='foo()', format='itanium')
        self.assertEqual(len({a, b}), 1)

    def test_to_dict(self):
        sym = Symbol(original='orig', demangled='dem', format='itanium')
        d = sym.to_dict()
        self.assertEqual(d['original'], 'orig')
        self.assertEqual(d['demangled'], 'dem')
        self.assertEqual(d['format'], 'itanium')

    def test_structured_property(self):
        sym = Symbol(original='_Z3foov', demangled='foo()',
                     format='itanium', kind='function')
        dsym = sym.structured
        self.assertIsInstance(dsym, DemangledSymbol)
        self.assertEqual(dsym.format, 'itanium')
        self.assertEqual(dsym.full_name, 'foo()')
        self.assertEqual(dsym.kind, 'function')

    def test_from_demangled_symbol(self):
        dsym = DemangledSymbol(
            format='msvc',
            full_name='void __cdecl foo(int)',
            kind='function',
            original_mangled='?foo@@YAXH@Z',
        )
        sym = Symbol.from_demangled_symbol(dsym)
        self.assertEqual(sym.format, 'msvc')
        self.assertEqual(sym.demangled, 'void __cdecl foo(int)')
        self.assertEqual(sym.original, '?foo@@YAXH@Z')

    def test_from_demangled_symbol_with_stripped(self):
        dsym = DemangledSymbol(format='itanium', full_name='foo()')
        sym = Symbol.from_demangled_symbol(dsym, original='_Z3foov@@GLIBC_2.4',
                                           stripped={'version_suffix': '@@GLIBC_2.4'})
        self.assertEqual(sym.original, '_Z3foov@@GLIBC_2.4')
        self.assertEqual(sym.stripped['version_suffix'], '@@GLIBC_2.4')


class TestDispatch(unittest.TestCase):
    """Test the main demangle() dispatch."""

    def test_itanium_dispatch(self):
        self.assertEqual(demangle('_ZN3foo3barEv'), 'foo::bar()')

    def test_msvc_dispatch(self):
        self.assertEqual(demangle('?foo@@YAXH@Z'),
                         'void __cdecl foo(int)')

    def test_jni_dispatch(self):
        result = demangle('Java_pkg_Cls_f__ILjava_lang_String_2')
        self.assertIsInstance(result, str)
        self.assertIn('int', result)

    def test_objc_dispatch(self):
        self.assertEqual(demangle('_OBJC_CLASS_$_NSObject'), 'NSObject')

    def test_unknown_returns_original(self):
        self.assertEqual(demangle('plain_symbol'), 'plain_symbol')

    def test_empty_returns_empty(self):
        self.assertEqual(demangle(''), '')

    def test_force_format_itanium(self):
        result = demangle('_Z3foov', fmt=FORMAT_ITANIUM)
        self.assertEqual(result, 'foo()')

    def test_force_format_msvc(self):
        result = demangle('?foo@@YAXH@Z', fmt=FORMAT_MSVC)
        self.assertEqual(result, 'void __cdecl foo(int)')

    def test_version_suffix_stripped(self):
        self.assertEqual(demangle('foo@@GLIBC_2.4'), 'foo')

    def test_version_suffix_stripped_function(self):
        self.assertEqual(demangle('_Z3foov@@GLIBC_2.4'), 'foo()')


class TestStructuredDispatch(unittest.TestCase):
    """Test structured output through the main dispatch."""

    def test_itanium_structured(self):
        sym = demangle('_ZN3foo3barEv', structured=True)
        self.assertIsInstance(sym, DemangledSymbol)
        self.assertEqual(sym.format, FORMAT_ITANIUM)
        self.assertEqual(sym.full_name, 'foo::bar()')

    def test_msvc_structured(self):
        sym = demangle('?foo@@YAXH@Z', structured=True)
        self.assertIsInstance(sym, DemangledSymbol)
        self.assertEqual(sym.format, FORMAT_MSVC)

    def test_unknown_structured(self):
        sym = demangle('plain_symbol', structured=True)
        self.assertIsInstance(sym, DemangledSymbol)
        self.assertEqual(sym.format, FORMAT_UNKNOWN)

    def test_original_preserved_with_version(self):
        sym = demangle('_ZN3foo3barEv@@GLIBC_2.4', structured=True)
        self.assertEqual(sym.original_mangled, '_ZN3foo3barEv@@GLIBC_2.4')
        self.assertEqual(sym.full_name, 'foo::bar()')

    def test_original_preserved_plain(self):
        sym = demangle('_ZN3foo3barEv', structured=True)
        self.assertEqual(sym.original_mangled, '_ZN3foo3barEv')


class TestGracefulDegradation(unittest.TestCase):
    """Test that demangle() never raises on any input."""

    def test_truncated_itanium(self):
        result = demangle('_Z')
        self.assertIsInstance(result, str)

    def test_invalid_char_itanium(self):
        result = demangle('_Z!')
        self.assertIsInstance(result, str)

    def test_truncated_msvc(self):
        result = demangle('?')
        self.assertIsInstance(result, str)

    def test_double_question_msvc(self):
        result = demangle('???')
        self.assertIsInstance(result, str)

    def test_binary_garbage(self):
        result = demangle('\x00\x01\x02\x03')
        self.assertIsInstance(result, str)

    def test_very_long_input(self):
        result = demangle('a' * 10000)
        self.assertIsInstance(result, str)

    def test_null_bytes(self):
        result = demangle('\x00\x00\x00')
        self.assertIsInstance(result, str)

    def test_unicode(self):
        result = demangle('café_function')
        self.assertIsInstance(result, str)

    def test_mixed_prefixes(self):
        # Inputs that look like they might match multiple formats
        for inp in ['_Z?foo', '?_Zfoo', 'Java_?foo', '$s?foo']:
            result = demangle(inp)
            self.assertIsInstance(result, str,
                                  'demangle(%r) crashed' % inp)

    def test_no_crash_on_partial_mangled(self):
        partials = [
            '_Z3', '_ZN3', '_ZN3foo', '_ZTV', '_ZTI', '_ZTS',
            '?foo', '?foo@', '?foo@@', '??0', '??1', '??_7',
            '_R', '_D', '$s', '_T0', 'Java_',
        ]
        for inp in partials:
            result = demangle(inp)
            self.assertIsInstance(result, str,
                                  'demangle(%r) crashed' % inp)


class TestDemangleError(unittest.TestCase):
    """Test DemangleError exception class."""

    def test_is_exception(self):
        self.assertTrue(issubclass(DemangleError, Exception))

    def test_can_raise(self):
        with self.assertRaises(DemangleError):
            raise DemangleError('test error')

    def test_has_message(self):
        try:
            raise DemangleError('test message')
        except DemangleError as e:
            self.assertIn('test message', str(e))


if __name__ == '__main__':
    unittest.main()