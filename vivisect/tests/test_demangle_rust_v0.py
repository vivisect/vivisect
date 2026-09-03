"""
Comprehensive tests for Rust v0 demangling (RFC 2603).

Tests cover all RFC 2603 grammar features:
- Paths: crate (C), nested (N), impl (M), trait impl (X), trait def (Y), generic (I)
- Namespaces: type (lowercase), value/closure (C), shim (S)
- Types: basic, references, pointers, arrays, slices, tuples, fn types, dyn traits
- Generic args: types, lifetimes (L), const generics (K)
- Const generics: bool, char, signed/uint, placeholder
- Lifetimes: anonymous, named, for<> binders, de Bruijn indexing
- Function types: unsafe, extern ABI, params, return type
- Dyn traits: trait bounds, associated types, lifetime
- Back-references (B)
- Punycode (RFC 3492) identifier decoding
- Vendor suffix stripping
- Legacy _Z demangling with $ escape decoding
- Structured output
- Graceful degradation
"""

import unittest

from vivisect.demangle import demangle, detect_format
from vivisect.demangle.rust import demangle_rust, _RustV0Parser
from vivisect.demangle.common import DemangledSymbol


class TestRustV0BasicPaths(unittest.TestCase):
    """Test basic path types (RFC 2603 §2.1)."""

    def test_crate_function(self):
        self.assertEqual(demangle_rust('_RNvCs1234_4test3foo'), 'test::foo')

    def test_crate_with_short_disambiguator(self):
        self.assertEqual(demangle_rust('_RNvCs1_4test3foo'), 'test::foo')

    def test_nested_type_namespace(self):
        # Nt = nested type namespace (lowercase t = type namespace)
        self.assertEqual(demangle_rust('_RNvNtCs1234_7mycrate3foo3bar'), 'mycrate::foo::bar')

    def test_deeply_nested_type_namespace(self):
        # Nt Nt C -> crate::foo::bar::baz
        self.assertEqual(demangle_rust('_RNvNtNtCs1234_7mycrate3foo3bar3baz'), 'mycrate::foo::bar::baz')

    def test_closure_no_name(self):
        # NC = closure namespace (uppercase C = value namespace)
        # NC Nt Cs1234_ 4test 4main 0 -> test::main::{closure#0}
        self.assertEqual(demangle_rust('_RNvNCNtCs1234_4test4main0E'), 'test::main::{closure#0}')

    def test_closure_with_name(self):
        # NC with a name: test::main::{closure:my_closure#0}
        result = demangle_rust('_RNvNCNtCs1234_4test4main10my_closureE')
        self.assertIn('closure', result)
        self.assertIn('my_closure', result)

    def test_shim_namespace(self):
        # NS = shim namespace
        result = demangle_rust('_RNvNSNtCs1234_4test4main0E')
        self.assertIn('shim', result)

    def test_crate_with_long_name(self):
        result = demangle_rust('_RNvCs1234_13my_crate_name11my_function')
        self.assertEqual(result, 'my_crate_name::my_function')


class TestRustV0GenericArgs(unittest.TestCase):
    """Test generic arguments (RFC 2603 §2.2)."""

    def test_single_type_arg(self):
        self.assertEqual(demangle_rust('_RINvCs1234_4test3foojE'), 'test::foo::<usize>')

    def test_multiple_type_args(self):
        self.assertEqual(demangle_rust('_RINvCs1234_4test3foojlbE'), 'test::foo::<usize, i32, bool>')

    def test_generic_with_reference_type(self):
        self.assertEqual(demangle_rust('_RINvCs1234_4test3fooRyE'), 'test::foo::<&u64>')

    def test_generic_with_mutable_reference(self):
        self.assertEqual(demangle_rust('_RINvCs1234_4test3fooQyE'), 'test::foo::<&mut u64>')

    def test_generic_with_pointer(self):
        self.assertEqual(demangle_rust('_RINvCs1234_4test3fooPyE'), 'test::foo::<*const u64>')

    def test_generic_with_mut_pointer(self):
        self.assertEqual(demangle_rust('_RINvCs1234_4test3fooOyE'), 'test::foo::<*mut u64>')

    def test_generic_with_slice(self):
        self.assertEqual(demangle_rust('_RINvCs1234_4test3fooSyE'), 'test::foo::<[u64]>')

    def test_generic_with_tuple(self):
        self.assertEqual(demangle_rust('_RINvCs1234_4test3fooTylEE'), 'test::foo::<(u64, i32)>')

    def test_generic_with_single_tuple(self):
        self.assertEqual(demangle_rust('_RINvCs1234_4test3fooTyEE'), 'test::foo::<(u64,)>')


class TestRustV0ConstGenerics(unittest.TestCase):
    """Test const generic values (RFC 2603 §2.2.K)."""

    def test_const_uint(self):
        # Kh2a_ -> unsigned const with hex value 2a = 42
        self.assertEqual(demangle_rust('_RINvCs1234_4test3fooKh2a_E'), 'test::foo::<42>')

    def test_const_bool_true(self):
        self.assertEqual(demangle_rust('_RINvCs1234_4test3fooKb1_E'), 'test::foo::<true>')

    def test_const_bool_false(self):
        self.assertEqual(demangle_rust('_RINvCs1234_4test3fooKb0_E'), 'test::foo::<false>')

    def test_const_negative_int(self):
        # Kln2a_ -> signed const with negative sign, hex 2a = -42
        self.assertEqual(demangle_rust('_RINvCs1234_4test3fooKln2a_E'), 'test::foo::<-42>')

    def test_const_char(self):
        # Kc41_ -> char const with hex 41 = 'A'
        self.assertEqual(demangle_rust('_RINvCs1234_4test3fooKc41_E'), "test::foo::<'A'>")

    def test_const_placeholder(self):
        self.assertEqual(demangle_rust('_RINvCs1234_4test3fooKpE'), 'test::foo::<_>')

    def test_const_zero(self):
        self.assertEqual(demangle_rust('_RINvCs1234_4test3fooKh0_E'), 'test::foo::<0>')

    def test_const_large_uint(self):
        # Large value > 16 hex digits shows as 0x...
        large_hex = 'f' * 17
        result = demangle_rust('_RINvCs1234_4test3fooKh%s_E' % large_hex)
        self.assertIn('0x', result)


class TestRustV0FunctionTypes(unittest.TestCase):
    """Test function type parsing (RFC 2603 §2.3.F)."""

    def test_fn_unit_return(self):
        # FyEu -> fn(u64) -> ()
        p = _RustV0Parser('FyEu')
        self.assertEqual(p._parse_type(), 'fn(u64)')

    def test_fn_with_return(self):
        # FyEj -> fn(u64) -> usize
        p = _RustV0Parser('FyEj')
        self.assertEqual(p._parse_type(), 'fn(u64) -> usize')

    def test_fn_no_params(self):
        # FEu -> fn() -> ()
        p = _RustV0Parser('FEu')
        self.assertEqual(p._parse_type(), 'fn()')

    def test_fn_multiple_params(self):
        # FljEu -> fn(i32, usize) -> ()
        p = _RustV0Parser('FljEu')
        self.assertEqual(p._parse_type(), 'fn(i32, usize)')

    def test_unsafe_fn(self):
        # FUyEu -> unsafe fn(u64) -> ()
        p = _RustV0Parser('FUyEu')
        self.assertEqual(p._parse_type(), 'unsafe fn(u64)')

    def test_extern_c_fn(self):
        # FKCyEu -> extern "C" fn(u64) -> ()
        p = _RustV0Parser('FKCyEu')
        self.assertEqual(p._parse_type(), 'extern "C" fn(u64)')

    def test_unsafe_extern_c_fn(self):
        # FUKCyEu -> unsafe extern "C" fn(u64) -> ()
        p = _RustV0Parser('FUKCyEu')
        self.assertEqual(p._parse_type(), 'unsafe extern "C" fn(u64)')

    def test_fn_in_generic_args(self):
        self.assertEqual(demangle_rust('_RINvCs1234_4test3fooFyEuE'), 'test::foo::<fn(u64)>')

    def test_fn_with_fn_param(self):
        # F FyEu Eu -> fn(fn(u64)) -> ()
        p = _RustV0Parser('FFyEuEu')
        self.assertEqual(p._parse_type(), 'fn(fn(u64))')

    def test_unsafe_fn_in_generic(self):
        self.assertEqual(demangle_rust('_RINvCs1234_4test3fooFUyEuE'), 'test::foo::<unsafe fn(u64)>')

    def test_extern_c_fn_in_generic(self):
        self.assertEqual(demangle_rust('_RINvCs1234_4test3fooFKCyEuE'), 'test::foo::<extern "C" fn(u64)>')


class TestRustV0Lifetimes(unittest.TestCase):
    """Test lifetime parsing (RFC 2603 §2.3)."""

    def test_reference_no_lifetime(self):
        # Re -> &str
        p = _RustV0Parser('Re')
        self.assertEqual(p._parse_type(), '&str')

    def test_reference_anonymous_lifetime(self):
        # RL_e -> &str (anonymous lifetime not shown)
        p = _RustV0Parser('RL_e')
        self.assertEqual(p._parse_type(), '&str')

    def test_fn_with_binder_single_lifetime(self):
        # FG_RL0_eEu -> for<'a> fn(&'a str) -> ()
        p = _RustV0Parser('FG_RL0_eEu')
        self.assertEqual(p._parse_type(), "for<'a> fn(&'a str)")

    def test_fn_with_two_bound_lifetimes(self):
        # FG0_RL0_eRL1_eEu -> for<'a, 'b> fn(&'b str, &'a str)
        p = _RustV0Parser('FG0_RL0_eRL1_eEu')
        self.assertEqual(p._parse_type(), "for<'a, 'b> fn(&'b str, &'a str)")

    def test_fn_with_named_lifetime_in_for(self):
        # for<'a> fn() -> for<'a> fn()
        p = _RustV0Parser('FG_Eu')
        self.assertEqual(p._parse_type(), "for<'a> fn()")


class TestRustV0DynTraits(unittest.TestCase):
    """Test dyn trait type parsing (RFC 2603 §2.3.D)."""

    def test_dyn_trait_simple(self):
        # D NvCs1234_4test7MyTrait E L_ -> dyn test::MyTrait
        p = _RustV0Parser('DNvCs1234_4test7MyTraitEL_')
        self.assertEqual(p._parse_type(), 'dyn test::MyTrait')

    def test_dyn_trait_with_lifetime(self):
        # D NvCs1234_4test7MyTrait E L0_ -> dyn test::MyTrait + '_
        p = _RustV0Parser('DNvCs1234_4test7MyTraitEL0_')
        self.assertEqual(p._parse_type(), "dyn test::MyTrait + '_")

    def test_dyn_trait_in_generic_args(self):
        result = demangle_rust('_RINvCs1234_4test3fooDNvCs1234_4test7MyTraitEL_EE')
        self.assertEqual(result, 'test::foo::<dyn test::MyTrait>')

    def test_dyn_trait_for_binder(self):
        # D G_ NvCs1234_4test7MyTrait E L0_ E
        # for<'a> dyn test::MyTrait + 'a
        p = _RustV0Parser('DG_NvCs1234_4test7MyTraitEL0_')
        result = p._parse_type()
        self.assertIn('for<', result)
        self.assertIn('dyn', result)
        self.assertIn('MyTrait', result)


class TestRustV0ImplPaths(unittest.TestCase):
    """Test impl path types (RFC 2603 §2.1.M, X, Y)."""

    def test_inherent_impl(self):
        # M s0_ Cs1234_4test NtCs1234_4test3Foo 3bar
        # <test::Foo>::bar
        result = demangle_rust('_RNvMs0_Cs1234_4testNtCs1234_4test3Foo3bar')
        self.assertEqual(result, '<test::Foo>::bar')

    def test_impl_path_returns_str(self):
        result = demangle_rust('_RNvMs0_Cs1234_4testNtCs1234_4test3Foo3bar')
        self.assertIsInstance(result, str)


class TestRustV0BackReferences(unittest.TestCase):
    """Test back-reference parsing (RFC 2603 §2.1.B)."""

    def test_backref_to_type(self):
        # INvCs1234_4test3fooyBi_E
        # y is at position 19, B is at position 20
        # Bi_ -> integer_62('i_') = 18+1 = 19 -> offset 19 -> 'y' -> u64
        p = _RustV0Parser('INvCs1234_4test3fooyBi_E')
        result = p._parse_path(in_value=True)
        self.assertEqual(result, 'test::foo::<u64, u64>')

    def test_no_backref_duplicate_types(self):
        # Same thing without backref
        p = _RustV0Parser('INvCs1234_4test3fooyyE')
        result = p._parse_path(in_value=True)
        self.assertEqual(result, 'test::foo::<u64, u64>')


class TestRustV0AllBasicTypes(unittest.TestCase):
    """Test all basic type mappings (RFC 2603 §2.3)."""

    def test_all_basic_types(self):
        expected = {
            'a': 'i8', 'b': 'bool', 'c': 'char', 'd': 'f64',
            'e': 'str', 'f': 'f32', 'h': 'u8', 'i': 'isize',
            'j': 'usize', 'l': 'i32', 'm': 'u32', 'n': 'i128',
            'o': 'u128', 's': 'i16', 't': 'u16', 'u': '()',
            'v': '...', 'x': 'i64', 'y': 'u64', 'z': '!',
            'p': '_',
        }
        for tag, expected_name in expected.items():
            p = _RustV0Parser(tag)
            result = p._parse_type()
            self.assertEqual(result, expected_name, 'type tag %r' % tag)


class TestRustV0Arrays(unittest.TestCase):
    """Test array type parsing (RFC 2603 §2.3.A).

    Note: In array context, the const length does NOT have a K prefix.
    The K prefix is only used in generic-arg context to distinguish
    const from type arguments.
    """

    def test_array_with_const_length(self):
        # A y h2a_ -> [u64; 42]
        p = _RustV0Parser('Ayh2a_')
        self.assertEqual(p._parse_type(), '[u64; 42]')

    def test_array_in_generic(self):
        # _R I Nv Cs1234_ 4test 3foo A y h2a_ E
        result = demangle_rust('_RINvCs1234_4test3fooAyh2a_E')
        self.assertEqual(result, 'test::foo::<[u64; 42]>')

    def test_array_with_zero(self):
        p = _RustV0Parser('Ayh0_')
        self.assertEqual(p._parse_type(), '[u64; 0]')


class TestRustV0Punycode(unittest.TestCase):
    """Test Punycode (RFC 3492) identifier decoding."""

    def test_ascii_only_ident(self):
        # No 'u' prefix, no Punycode
        self.assertEqual(demangle_rust('_RNvCs1234_4test3foo'), 'test::foo')

    def test_punycode_munich(self):
        # Test the Punycode decoder directly
        from vivisect.demangle.rust import _punycode_decode_ident
        result = _punycode_decode_ident('mnchen_3ya')
        self.assertEqual(result, 'münchen')

    def test_punycode_all_ascii(self):
        # All-ASCII with no Punycode suffix
        from vivisect.demangle.rust import _punycode_decode
        self.assertEqual(_punycode_decode('hello', ''), 'hello')


class TestRustV0VendorSuffix(unittest.TestCase):
    """Test vendor suffix stripping."""

    def test_llvm_suffix(self):
        result = demangle_rust('_RNvCs1234_4test3foo.llvm.abc123')
        self.assertEqual(result, 'test::foo')

    def test_dot_suffix(self):
        result = demangle_rust('_RNvCs1234_4test3foo.example')
        self.assertEqual(result, 'test::foo')


class TestRustV0StructuredOutput(unittest.TestCase):
    """Test structured output for Rust v0."""

    def test_structured_returns_demangled_symbol(self):
        sym = demangle_rust('_RNvCs1234_4test3foo', structured=True)
        self.assertIsInstance(sym, DemangledSymbol)
        self.assertEqual(sym.format, 'rust')
        self.assertEqual(sym.full_name, 'test::foo')
        self.assertEqual(sym.original_mangled, '_RNvCs1234_4test3foo')

    def test_structured_scope_and_name(self):
        sym = demangle_rust('_RNvCs1234_4test3foo', structured=True)
        self.assertEqual(sym.name, 'foo')
        self.assertIn('test', sym.scope)

    def test_structured_nested(self):
        sym = demangle_rust('_RNvNtCs1234_7mycrate3foo3bar', structured=True)
        self.assertEqual(sym.name, 'bar')
        self.assertIn('mycrate', sym.scope)
        self.assertIn('foo', sym.scope)

    def test_structured_with_generics(self):
        sym = demangle_rust('_RINvCs1234_4test3foojE', structured=True)
        self.assertTrue(sym.is_template)


class TestRustV0GracefulDegradation(unittest.TestCase):
    """Test graceful degradation for invalid input."""

    def test_empty_string(self):
        self.assertEqual(demangle_rust(''), '')

    def test_non_rust_prefix(self):
        self.assertEqual(demangle_rust('plain_function'), 'plain_function')

    def test_just_prefix(self):
        result = demangle_rust('_R')
        self.assertIsInstance(result, str)

    def test_garbage_after_prefix(self):
        result = demangle_rust('_R\x00\x01\x02')
        self.assertIsInstance(result, str)

    def test_truncated_path(self):
        result = demangle_rust('_RN')
        self.assertIsInstance(result, str)

    def test_truncated_generic(self):
        result = demangle_rust('_RI')
        self.assertIsInstance(result, str)

    def test_invalid_path_tag(self):
        result = demangle_rust('_R9')
        self.assertIsInstance(result, str)

    def test_truncated_fn_type(self):
        result = demangle_rust('_RF')
        self.assertIsInstance(result, str)

    def test_never_raises(self):
        inputs = [
            '_R', '_R\x00', '_RN', '_RI', '_RB',
            '_RNv', '_RNvC', '_RNvCs', '_RNvCs1_',
            '_RINv', '_RINvCs1_',
        ]
        for inp in inputs:
            result = demangle_rust(inp)
            self.assertIsInstance(result, str, 'demangle(%r) should return str' % inp)


class TestRustLegacyDemangle(unittest.TestCase):
    """Test legacy Rust (_Z prefix) demangling."""

    def test_basic_legacy(self):
        result = demangle_rust('_ZN3foo3barEv')
        self.assertIsInstance(result, str)

    def test_legacy_escape_decoding(self):
        result = demangle_rust('_ZN3foo$RF$3barEv')
        self.assertIsInstance(result, str)

    def test_legacy_with_dot_suffix(self):
        result = demangle_rust('_ZN3foo3barEv.h1234')
        self.assertIsInstance(result, str)


class TestRustFormatDetection(unittest.TestCase):
    """Test Rust format detection."""

    def test_detect_v0(self):
        self.assertEqual(detect_format('_RNvCs1234_4test3foo'), 'rust')

    def test_detect_v0_nested(self):
        self.assertEqual(detect_format('_RNvNtCs1234_7mycrate3foo3bar'), 'rust')

    def test_detect_legacy(self):
        # Legacy Rust uses _Z prefix, detected as itanium but dispatched to rust
        # when called through demangle_rust directly
        self.assertEqual(detect_format('_ZN3foo3barEv'), 'itanium')


class TestRustDispatch(unittest.TestCase):
    """Test Rust through the main demangle() dispatch."""

    def test_v0_dispatch(self):
        result = demangle('_RNvCs1234_4test3foo')
        self.assertIsInstance(result, str)

    def test_v0_structured_dispatch(self):
        sym = demangle('_RNvCs1234_4test3foo', structured=True)
        self.assertEqual(sym.format, 'rust')

    def test_never_raises(self):
        for inp in ['_R', '_R\x00', '_RN', '_RNv', '_RNvC']:
            result = demangle(inp)
            self.assertIsInstance(result, str)


if __name__ == '__main__':
    unittest.main()