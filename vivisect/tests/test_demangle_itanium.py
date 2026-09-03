"""
Comprehensive tests for the Itanium C++ ABI demangling module.

Tests cover:
- Simple functions with various return types and parameters
- Nested names (namespaces, classes)
- Templates and template arguments
- Special names (vtable, typeinfo, VTT, guard variables)
- Constructors and destructors
- Operators (all categories)
- CV qualifiers (const, volatile, restrict)
- Reference types (lvalue, rvalue)
- Pointers and arrays
- Substitutions and back-references
- Standard substitutions (std::, std::string, etc.)
- Pointer-to-member types
- Function types with CV/ref qualifiers
- Version suffix stripping
- Structured output (DemangledSymbol)
- Graceful degradation on invalid input
- Edge cases (empty, truncated, binary garbage)
"""

import unittest

from vivisect.demangle import demangle, detect_format, DemangledSymbol
from vivisect.demangle.itanium import demangle_itanium, demangle_itanium_symbol
from vivisect.demangle.itanium.parser import ItaniumParser, ParseError
from vivisect.demangle.itanium.renderer import render
from vivisect.demangle.itanium import ast_nodes as ast
from vivisect.demangle.itanium import grammar


class TestItaniumBasicFunctions(unittest.TestCase):
    """Test basic Itanium function demangling."""

    def test_void_function_no_params(self):
        self.assertEqual(demangle_itanium('_Z3foov'), 'foo()')

    def test_void_function_void_param(self):
        # _Z3foo v — v is void, meaning no parameters
        self.assertEqual(demangle_itanium('_Z3foov'), 'foo()')

    def test_int_function_int_param(self):
        self.assertEqual(demangle_itanium('_Z3fooii'), 'foo(int, int)')

    def test_simple_name_no_encoding(self):
        # _Z3foo is just a name (no function type)
        self.assertEqual(demangle_itanium('_Z3foo'), 'foo')

    def test_double_return(self):
        result = demangle_itanium('_Z3food')
        self.assertIn('double', result)

    def test_float_param(self):
        result = demangle_itanium('_Z3foof')
        self.assertIn('float', result)

    def test_char_param(self):
        result = demangle_itanium('_Z3fooc')
        self.assertIn('char', result)

    def test_bool_param(self):
        result = demangle_itanium('_Z3foob')
        self.assertIn('bool', result)

    def test_long_param(self):
        result = demangle_itanium('_Z3fool')
        self.assertIn('long', result)

    def test_unsigned_int_param(self):
        result = demangle_itanium('_Z3fooj')
        self.assertIn('unsigned int', result)

    def test_unsigned_long_param(self):
        result = demangle_itanium('_Z3foom')
        self.assertIn('unsigned long', result)

    def test_long_long_param(self):
        result = demangle_itanium('_Z3foox')
        self.assertIn('long long', result)

    def test_short_param(self):
        result = demangle_itanium('_Z3foos')
        self.assertIn('short', result)

    def test_wchar_t_param(self):
        result = demangle_itanium('_Z3foow')
        self.assertIn('wchar_t', result)

    def test_ellipsis_param(self):
        result = demangle_itanium('_Z3foozi')
        self.assertIn('...', result)

    def test_multiple_params(self):
        result = demangle_itanium('_Z3fooibdc')
        # Should contain int, bool, double, char
        self.assertIn('int', result)
        self.assertIn('bool', result)
        self.assertIn('double', result)
        self.assertIn('char', result)


class TestItaniumBuiltinTypes(unittest.TestCase):
    """Test all builtin type codes."""

    def test_signed_char(self):
        result = demangle_itanium('_Z3fooa')
        self.assertIn('signed char', result)

    def test_unsigned_char(self):
        result = demangle_itanium('_Z3fooh')
        self.assertIn('unsigned char', result)

    def test_long_double(self):
        result = demangle_itanium('_Z3fooe')
        self.assertIn('long double', result)

    def test_float128(self):
        result = demangle_itanium('_Z3foog')
        self.assertIn('__float128', result)

    def test_int128(self):
        result = demangle_itanium('_Z3foon')
        self.assertIn('__int128', result)

    def test_unsigned_int128(self):
        result = demangle_itanium('_Z3fooo')
        self.assertIn('unsigned __int128', result)

    def test_unsigned_short(self):
        result = demangle_itanium('_Z3foot')
        self.assertIn('unsigned short', result)

    def test_unsigned_long_long(self):
        result = demangle_itanium('_Z3fooy')
        self.assertIn('unsigned long long', result)

    def test_extended_decimal64(self):
        result = demangle_itanium('_Z3fooDd')
        self.assertIn('decimal64', result)

    def test_extended_decimal128(self):
        result = demangle_itanium('_Z3fooDe')
        self.assertIn('decimal128', result)

    def test_extended_char32_t(self):
        result = demangle_itanium('_Z3fooDi')
        self.assertIn('char32_t', result)

    def test_extended_char16_t(self):
        result = demangle_itanium('_Z3fooDs')
        self.assertIn('char16_t', result)

    def test_extended_char8_t(self):
        result = demangle_itanium('_Z3fooDu')
        self.assertIn('char8_t', result)

    def test_extended_auto(self):
        result = demangle_itanium('_Z3fooDa')
        self.assertIn('auto', result)


class TestItaniumNestedNames(unittest.TestCase):
    """Test nested names (namespaces, classes)."""

    def test_single_namespace(self):
        self.assertEqual(demangle_itanium('_ZN3foo3barEv'),
                         'foo::bar()')

    def test_double_namespace(self):
        self.assertEqual(demangle_itanium('_ZN3foo3bar3bazEv'),
                         'foo::bar::baz()')

    def test_deep_namespace(self):
        result = demangle_itanium('_ZN2ns12nested_class4funcEv')
        self.assertIn('ns', result)
        self.assertIn('nested_class', result)
        self.assertIn('func', result)

    def test_std_namespace(self):
        result = demangle_itanium('_ZSt5state')
        self.assertIn('std', result)


class TestItaniumSpecialNames(unittest.TestCase):
    """Test special name demangling (vtable, typeinfo, etc.)."""

    def test_vtable(self):
        self.assertEqual(demangle_itanium('_ZTV1A'), 'vtable for A')

    def test_typeinfo(self):
        self.assertEqual(demangle_itanium('_ZTI1A'), 'typeinfo for A')

    def test_typeinfo_name(self):
        self.assertEqual(demangle_itanium('_ZTS1A'), 'typeinfo name for A')

    def test_vtt(self):
        result = demangle_itanium('_ZTT1A')
        self.assertIn('VTT', result)
        self.assertIn('A', result)

    def test_guard_variable(self):
        result = demangle_itanium('_ZGV1A')
        self.assertIn('guard', result)


class TestItaniumConstructorsDestructors(unittest.TestCase):
    """Test constructor and destructor demangling."""

    def test_complete_constructor(self):
        result = demangle_itanium('_ZN1AC1Ev')
        self.assertIn('A', result)

    def test_base_constructor(self):
        result = demangle_itanium('_ZN1AC2Ev')
        self.assertIn('A', result)

    def test_deleting_destructor(self):
        result = demangle_itanium('_ZN1AD0Ev')
        self.assertIn('~A', result)

    def test_complete_destructor(self):
        result = demangle_itanium('_ZN1AD1Ev')
        self.assertIn('~A', result)

    def test_base_destructor(self):
        result = demangle_itanium('_ZN1AD2Ev')
        self.assertIn('~A', result)


class TestItaniumOperators(unittest.TestCase):
    """Test operator demangling."""

    def test_operator_plus(self):
        result = demangle_itanium('_ZN1aplEi')
        self.assertIn('operator+', result)

    def test_operator_minus(self):
        result = demangle_itanium('_ZN1amiEi')
        self.assertIn('operator-', result)

    def test_operator_assign(self):
        result = demangle_itanium('_ZN1aaSEi')
        self.assertIn('operator=', result)

    def test_operator_call(self):
        result = demangle_itanium('_ZN1aclEv')
        self.assertIn('operator()', result)

    def test_operator_subscript(self):
        result = demangle_itanium('_ZN1aixEi')
        self.assertIn('operator[]', result)

    def test_operator_new(self):
        result = demangle_itanium('_Znwm')
        self.assertIn('operator', result)
        self.assertIn('new', result)

    def test_operator_delete(self):
        result = demangle_itanium('_ZdlPv')
        self.assertIn('operator', result)
        self.assertIn('delete', result)

    def test_operator_shift_left(self):
        result = demangle_itanium('_ZN1alsEi')
        self.assertIn('operator<<', result)

    def test_operator_shift_right(self):
        result = demangle_itanium('_ZN1arsEi')
        self.assertIn('operator>>', result)

    def test_operator_equals(self):
        result = demangle_itanium('_ZN1aeqEi')
        self.assertIn('operator==', result)

    def test_operator_not_equals(self):
        result = demangle_itanium('_ZN1aneEi')
        self.assertIn('operator!=', result)

    def test_operator_less(self):
        result = demangle_itanium('_ZN1altEi')
        self.assertIn('operator<', result)

    def test_operator_greater(self):
        result = demangle_itanium('_ZN1agtEi')
        self.assertIn('operator>', result)

    def test_operator_arrow(self):
        result = demangle_itanium('_ZN1aptEi')
        self.assertIn('operator->', result)


class TestItaniumPointersReferences(unittest.TestCase):
    """Test pointer, reference, and CV-qualified types."""

    def test_pointer_to_int(self):
        result = demangle_itanium('_Z3fooPi')
        self.assertIn('int', result)
        self.assertIn('*', result)

    def test_pointer_to_char(self):
        result = demangle_itanium('_Z3fooPc')
        self.assertIn('char', result)
        self.assertIn('*', result)

    def test_double_pointer(self):
        result = demangle_itanium('_Z3fooPPi')
        self.assertIn('int', result)
        self.assertIn('*', result)

    def test_lvalue_reference(self):
        result = demangle_itanium('_Z3fooRi')
        self.assertIn('int', result)
        self.assertIn('&', result)

    def test_rvalue_reference(self):
        result = demangle_itanium('_Z3fooOi')
        self.assertIn('int', result)
        self.assertIn('&&', result)

    def test_const_int(self):
        result = demangle_itanium('_Z3fooKi')
        self.assertIn('const', result)
        self.assertIn('int', result)

    def test_volatile_int(self):
        result = demangle_itanium('_Z3fooVi')
        self.assertIn('volatile', result)
        self.assertIn('int', result)

    def test_const_pointer(self):
        result = demangle_itanium('_Z3fooPKi')
        self.assertIn('const', result)
        self.assertIn('int', result)
        self.assertIn('*', result)

    def test_pointer_to_const(self):
        result = demangle_itanium('_Z3fooPKi')
        # PKi = pointer to const int (Itanium renders as "int const*")
        self.assertIn('const', result)
        self.assertIn('int', result)
        self.assertIn('*', result)


class TestItaniumTemplates(unittest.TestCase):
    """Test template demangling."""

    def test_simple_template(self):
        result = demangle_itanium('_ZN1N1TIiiE2mfES0_IddE')
        self.assertIn('N::T', result)

    def test_template_args(self):
        result = demangle_itanium('_Z3fooIiEvT_')
        # foo<int>(int)
        self.assertIn('foo', result)


class TestItaniumPointerToMember(unittest.TestCase):
    """Test pointer-to-member types."""

    def test_ptr_to_member_data(self):
        result = demangle_itanium('_Z1fM1Ai')
        self.assertIn('A::*', result)
        self.assertIn('int', result)

    def test_ptr_to_member_function_const_ref(self):
        self.assertEqual(demangle_itanium('_Z1fM1AKFvvRE'),
                         'f(void (A::*)() const &)')

    def test_ptr_to_member_function_const(self):
        self.assertEqual(demangle_itanium('_Z1fM1AKFvvE'),
                         'f(void (A::*)() const)')

    def test_ptr_to_member_function_plain(self):
        self.assertEqual(demangle_itanium('_Z1fM1AFvvE'),
                         'f(void (A::*)())')

    def test_ptr_to_member_function_ref(self):
        self.assertEqual(demangle_itanium('_Z1fM1AFvvRE'),
                         'f(void (A::*)() &)')

    def test_ptr_to_member_function_const_rvalue(self):
        self.assertEqual(demangle_itanium('_Z1fM1AKFvvOE'),
                         'f(void (A::*)() const &&)')


class TestItaniumSubstitutions(unittest.TestCase):
    """Test substitution and back-reference handling."""

    def test_std_substitution(self):
        result = demangle_itanium('_ZSt5state')
        self.assertIn('std', result)

    def test_std_string_substitution(self):
        result = demangle_itanium('_ZSs')
        # Ss = std::string
        self.assertIn('std', result)

    def test_substitution_backref(self):
        # _Z3fooPiS_ — S_ refers to the first substitution (int*)
        result = demangle_itanium('_Z3fooPiS_')
        self.assertIn('int', result)
        self.assertIn('*', result)


class TestItaniumVersionSuffix(unittest.TestCase):
    """Test @@VERSION suffix handling."""

    def test_strip_glibc_suffix(self):
        self.assertEqual(demangle_itanium('_Z3foo@@GLIBC_2.4'), 'foo')

    def test_strip_glibc_suffix_function(self):
        self.assertEqual(demangle_itanium('_Z3foov@@GLIBC_2.4'), 'foo()')

    def test_strip_long_version(self):
        result = demangle_itanium('_Z3foo@@GLIBC_2.17')
        self.assertEqual(result, 'foo')


class TestItaniumStructuredOutput(unittest.TestCase):
    """Test structured DemangledSymbol output."""

    def test_structured_function(self):
        sym = demangle_itanium('_ZN3foo3barEv', structured=True)
        self.assertIsInstance(sym, DemangledSymbol)
        self.assertEqual(sym.format, 'itanium')
        self.assertEqual(sym.full_name, 'foo::bar()')
        self.assertEqual(sym.original_mangled, '_ZN3foo3barEv')

    def test_structured_vtable(self):
        sym = demangle_itanium('_ZTV1A', structured=True)
        self.assertIsInstance(sym, DemangledSymbol)
        self.assertEqual(sym.kind, 'vtable')
        self.assertEqual(sym.name, 'A')

    def test_structured_typeinfo(self):
        sym = demangle_itanium('_ZTI1A', structured=True)
        self.assertIsInstance(sym, DemangledSymbol)
        self.assertEqual(sym.kind, 'typeinfo')

    def test_structured_typeinfo_name(self):
        sym = demangle_itanium('_ZTS1A', structured=True)
        self.assertIsInstance(sym, DemangledSymbol)
        self.assertEqual(sym.kind, 'typeinfo_name')

    def test_symbol_object(self):
        sym = demangle_itanium_symbol('_ZN3foo3barEv')
        self.assertIsNotNone(sym)
        self.assertEqual(sym.format, 'itanium')
        self.assertEqual(sym.demangled, 'foo::bar()')

    def test_symbol_original_preserved(self):
        sym = demangle_itanium_symbol('_ZN3foo3barEv@@GLIBC_2.4')
        self.assertEqual(sym.original, '_ZN3foo3barEv@@GLIBC_2.4')
        self.assertEqual(sym.demangled, 'foo::bar()')


class TestItaniumGracefulDegradation(unittest.TestCase):
    """Test graceful degradation on invalid input."""

    def test_truncated_input(self):
        result = demangle_itanium('_Z')
        self.assertIsInstance(result, str)

    def test_invalid_char(self):
        result = demangle_itanium('_Z!')
        self.assertIsInstance(result, str)

    def test_empty_string(self):
        result = demangle_itanium('')
        self.assertEqual(result, '')

    def test_non_mangled(self):
        result = demangle_itanium('plain_function')
        self.assertEqual(result, 'plain_function')

    def test_garbage_input(self):
        result = demangle_itanium('\x00\x01\x02\x03')
        self.assertIsInstance(result, str)

    def test_long_input(self):
        result = demangle_itanium('a' * 1000)
        self.assertIsInstance(result, str)

    def test_no_crash_on_partial(self):
        # Partial mangled names should not crash
        for partial in ['_Z3', '_ZN3', '_ZN3foo', '_ZTV', '_ZTI']:
            result = demangle_itanium(partial)
            self.assertIsInstance(result, str,
                                  'demangle_itanium(%r) crashed' % partial)


class TestItaniumParserDirect(unittest.TestCase):
    """Test the parser directly (AST-level tests)."""

    def test_parser_returns_ast(self):
        parser = ItaniumParser('_ZN3foo3barEv')
        node = parser.parse()
        self.assertIsNotNone(node)

    def test_parser_simple_function(self):
        parser = ItaniumParser('_Z3foov')
        node = parser.parse()
        self.assertIsInstance(node, ast.Name)

    def test_parser_vtable(self):
        parser = ItaniumParser('_ZTV1A')
        node = parser.parse()
        self.assertIsInstance(node, ast.SpecialName)
        self.assertEqual(node.kind, 'vtable')

    def test_parser_typeinfo(self):
        parser = ItaniumParser('_ZTI1A')
        node = parser.parse()
        self.assertIsInstance(node, ast.SpecialName)
        self.assertEqual(node.kind, 'typeinfo')

    def test_parser_raises_on_empty(self):
        parser = ItaniumParser('')
        with self.assertRaises(ParseError):
            parser.parse()

    def test_renderer_renders_ast(self):
        parser = ItaniumParser('_ZN3foo3barEv')
        node = parser.parse()
        result = render(node, subs=parser.subs)
        self.assertEqual(result, 'foo::bar()')

    def test_substitutions_populated(self):
        parser = ItaniumParser('_ZN3foo3barEv')
        parser.parse()
        # After parsing a nested name, there should be substitutions
        self.assertIsInstance(parser.subs, list)


class TestItaniumGrammarConstants(unittest.TestCase):
    """Test that grammar lookup tables are properly populated."""

    def test_builtin_types_has_int(self):
        self.assertIn('i', grammar.BUILTIN_TYPES)
        self.assertEqual(grammar.BUILTIN_TYPES['i'], 'int')

    def test_builtin_types_has_void(self):
        self.assertIn('v', grammar.BUILTIN_TYPES)
        self.assertEqual(grammar.BUILTIN_TYPES['v'], 'void')

    def test_builtin_types_has_double(self):
        self.assertIn('d', grammar.BUILTIN_TYPES)
        self.assertEqual(grammar.BUILTIN_TYPES['d'], 'double')

    def test_operators_has_plus(self):
        self.assertIn('pl', grammar.OPERATORS)
        symbol, num_args = grammar.OPERATORS['pl']
        self.assertEqual(symbol, '+')
        self.assertEqual(num_args, 2)

    def test_operators_has_new(self):
        self.assertIn('nw', grammar.OPERATORS)

    def test_operators_has_delete(self):
        self.assertIn('dl', grammar.OPERATORS)

    def test_ctor_kinds(self):
        self.assertIn('C1', grammar.CTOR_KINDS)
        self.assertEqual(grammar.CTOR_KINDS['C1'], 'complete')

    def test_dtor_kinds(self):
        self.assertIn('D0', grammar.DTOR_KINDS)
        self.assertEqual(grammar.DTOR_KINDS['D0'], 'deleting')

    def test_std_subs(self):
        self.assertIn('t', grammar.STD_SUBS)
        self.assertEqual(grammar.STD_SUBS['t'], 'std')

    def test_special_names_vtable(self):
        self.assertIn('TV', grammar.SPECIAL_NAMES)
        self.assertEqual(grammar.SPECIAL_NAMES['TV'], 'vtable')

    def test_special_names_typeinfo(self):
        self.assertIn('TI', grammar.SPECIAL_NAMES)
        self.assertEqual(grammar.SPECIAL_NAMES['TI'], 'typeinfo')


class TestItaniumASTNodes(unittest.TestCase):
    """Test AST node classes."""

    def test_node_repr(self):
        node = ast.Node()
        self.assertIn('Node', repr(node))

    def test_source_name(self):
        node = ast.SourceName('foo')
        self.assertEqual(node.name, 'foo')

    def test_builtin_type(self):
        node = ast.BuiltinType('int', 'i')
        self.assertEqual(node.name, 'int')
        self.assertEqual(node.code, 'i')

    def test_pointer_type(self):
        target = ast.BuiltinType('int', 'i')
        ptr = ast.PointerType(target)
        self.assertIs(ptr.target, target)
        self.assertEqual(ptr.children(), [target])

    def test_nested_name(self):
        prefix = [ast.SourceName('foo')]
        unq = ast.UnqualifiedName('source', ast.SourceName('bar'))
        nn = ast.NestedName(prefix, unq)
        self.assertEqual(len(nn.prefix), 1)
        self.assertIs(nn.unqualified_name, unq)

    def test_template_args(self):
        arg1 = ast.BuiltinType('int', 'i')
        args = ast.TemplateArgs([arg1])
        self.assertEqual(len(args.args), 1)
        self.assertEqual(args.children(), [arg1])

    def test_special_name(self):
        target = ast.BuiltinType('int', 'i')
        sn = ast.SpecialName('vtable', target)
        self.assertEqual(sn.kind, 'vtable')
        self.assertIs(sn.target, target)
        self.assertEqual(sn.children(), [target])

    def test_special_name_no_target(self):
        sn = ast.SpecialName('guard')
        self.assertIsNone(sn.target)
        self.assertEqual(sn.children(), [])

    def test_pointer_to_member(self):
        cls = ast.BuiltinType('A', 'i')
        member = ast.BuiltinType('int', 'i')
        ptm = ast.PointerToMember(cls, member)
        self.assertEqual(len(ptm.children()), 2)


if __name__ == '__main__':
    unittest.main()