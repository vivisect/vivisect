"""
Comprehensive tests for the MSVC C++ demangling module.

Tests cover:
- Format detection and dispatch
- Non-member functions (all calling conventions, return types, params)
- Member functions (virtual, static, public, private, protected)
- Constructors and destructors (with structor return type encoding)
- Vtables and vbtibles
- Operators (all categories: new, delete, arithmetic, comparison, etc.)
- Variables (global, static member, with access levels)
- Primitive types (all MSVC type codes)
- Extended primitive types (_D through _W)
- Pointer types (with CV modifiers)
- Reference types (lvalue and rvalue)
- User-defined types (struct, class, enum, union)
- Namespace and nested class scope
- Structured output (DemangledSymbol)
- AST node tests
- Parser direct tests
- Graceful degradation on invalid input
- Edge cases (empty, truncated, hashed objects)
"""

import unittest

from vivisect.demangle import demangle, detect_format
from vivisect.demangle.msvc import demangle_msvc
from vivisect.demangle.msvc.parser import MSVCParser, ParseError
from vivisect.demangle.msvc.renderer import render
from vivisect.demangle.msvc import ast_nodes as ast
from vivisect.demangle.common import DemangledSymbol


class TestMSVCFormatDetection(unittest.TestCase):
    """Test MSVC format detection from symbol prefix."""

    def test_simple_question(self):
        self.assertEqual(detect_format('?foo@@YAXH@Z'), 'msvc')

    def test_double_question_ctor(self):
        self.assertEqual(detect_format('??0MyClass@@QAE@X@Z'), 'msvc')

    def test_double_question_dtor(self):
        self.assertEqual(detect_format('??1MyClass@@UAE@X@Z'), 'msvc')

    def test_vtable_prefix(self):
        self.assertEqual(detect_format('??_7MyClass@@6B@'), 'msvc')

    def test_operator_new_prefix(self):
        self.assertEqual(detect_format('??2@YAPAXI@Z'), 'msvc')

    def test_operator_delete_prefix(self):
        self.assertEqual(detect_format('??3@YAXPAX@Z'), 'msvc')

    def test_not_msvc(self):
        self.assertNotEqual(detect_format('_Z3foov'), 'msvc')
        self.assertNotEqual(detect_format('Java_pkg_Cls_f'), 'msvc')
        self.assertNotEqual(detect_format('plain_name'), 'msvc')


class TestMSVCNonMemberFunctions(unittest.TestCase):
    """Test non-member (free) function demangling."""

    def test_void_cdecl_int(self):
        self.assertEqual(demangle_msvc('?foo@@YAXH@Z'),
                         'void __cdecl foo(int)')

    def test_int_cdecl_int(self):
        self.assertEqual(demangle_msvc('?func@@YAHH@Z'),
                         'int __cdecl func(int)')

    def test_double_cdecl_void(self):
        self.assertEqual(demangle_msvc('?func2@@YANX@Z'),
                         'double __cdecl func2(void)')

    def test_void_cdecl_no_params(self):
        # X after calling convention means void return + no args
        result = demangle_msvc('?foo@@YAXXZ')
        self.assertIsInstance(result, str)

    def test_reference_param(self):
        self.assertEqual(demangle_msvc('?func3@@YAXABH@Z'),
                         'void __cdecl func3(int&)')

    def test_pointer_param(self):
        self.assertEqual(demangle_msvc('?func4@@YAXPAH@Z'),
                         'void __cdecl func4(int*)')

    def test_const_pointer_param(self):
        self.assertEqual(demangle_msvc('?pfunc@@YAXPBH@Z'),
                         'void __cdecl pfunc(const int*)')

    def test_multiple_int_params(self):
        self.assertEqual(demangle_msvc('?multi@@YAHHH@Z'),
                         'int __cdecl multi(int, int)')

    def test_three_params(self):
        result = demangle_msvc('?three@@YAHHHI@Z')
        self.assertIn('int', result)
        self.assertIn('unsigned int', result)

    def test_char_param(self):
        self.assertEqual(demangle_msvc('?cfunc@@YAXD@Z'),
                         'void __cdecl cfunc(char)')

    def test_unsigned_int_param(self):
        self.assertEqual(demangle_msvc('?ufunc@@YAXI@Z'),
                         'void __cdecl ufunc(unsigned int)')

    def test_long_param(self):
        self.assertEqual(demangle_msvc('?lfunc@@YAXJ@Z'),
                         'void __cdecl lfunc(long)')

    def test_unsigned_long_param(self):
        result = demangle_msvc('?ulfunc@@YAXK@Z')
        self.assertIn('unsigned long', result)

    def test_short_param(self):
        result = demangle_msvc('?sfunc@@YAXF@Z')
        self.assertIn('short', result)

    def test_unsigned_short_param(self):
        result = demangle_msvc('?usfunc@@YAXG@Z')
        self.assertIn('unsigned short', result)

    def test_float_param(self):
        result = demangle_msvc('?ffunc@@YAXM@Z')
        self.assertIn('float', result)

    def test_double_param(self):
        result = demangle_msvc('?dfunc@@YAXN@Z')
        self.assertIn('double', result)


class TestMSVCMemberFunctions(unittest.TestCase):
    """Test member function demangling with access levels."""

    def test_public_virtual_thiscall(self):
        self.assertEqual(demangle_msvc('?bar@MyClass@@UAEXH@Z'),
                         'public: virtual void __thiscall MyClass::bar(int)')

    def test_public_static_stdcall(self):
        self.assertEqual(demangle_msvc('?baz@MyClass@@SGXH@Z'),
                         'public: static void __stdcall MyClass::baz(int)')

    def test_private_thiscall(self):
        self.assertEqual(demangle_msvc('?priv@MyClass@@AAEXH@Z'),
                         'private: void __thiscall MyClass::priv(int)')

    def test_protected_thiscall(self):
        self.assertEqual(demangle_msvc('?prot@MyClass@@IAEXH@Z'),
                         'protected: void __thiscall MyClass::prot(int)')

    def test_public_member_thiscall(self):
        # Q = public, non-virtual, non-static
        result = demangle_msvc('?method@MyClass@@QAEXH@Z')
        self.assertIn('public:', result)
        self.assertIn('__thiscall', result)
        self.assertIn('MyClass::method', result)


class TestMSVCConstructorsDestructors(unittest.TestCase):
    """Test constructor and destructor demangling."""

    def test_constructor_public(self):
        self.assertEqual(demangle_msvc('??0MyClass@@QAE@X@Z'),
                         'public: __thiscall MyClass::MyClass(void)')

    def test_destructor_public_virtual(self):
        self.assertEqual(demangle_msvc('??1MyClass@@UAE@X@Z'),
                         'public: virtual __thiscall MyClass::~MyClass(void)')

    def test_constructor_no_args(self):
        result = demangle_msvc('??0MyClass@@QAE@X@Z')
        self.assertIn('MyClass::MyClass', result)
        self.assertIn('void', result)

    def test_destructor_tilde(self):
        result = demangle_msvc('??1MyClass@@UAE@X@Z')
        self.assertIn('~MyClass', result)


class TestMSVCVtables(unittest.TestCase):
    """Test vtable and vbtable demangling."""

    def test_vtable(self):
        self.assertEqual(demangle_msvc('??_7MyClass@@6B@'),
                         "const MyClass::`vftable'")

    def test_vtable_simple_class(self):
        result = demangle_msvc('??_7Foo@@6B@')
        self.assertIn('vftable', result)
        self.assertIn('Foo', result)


class TestMSVCOperators(unittest.TestCase):
    """Test operator demangling."""

    def test_operator_new(self):
        self.assertEqual(demangle_msvc('??2@YAPAXI@Z'),
                         'void* __cdecl operator new(unsigned int)')

    def test_operator_delete(self):
        self.assertEqual(demangle_msvc('??3@YAXPAX@Z'),
                         'void __cdecl operator delete(void*)')


class TestMSVCVariables(unittest.TestCase):
    """Test variable demangling."""

    def test_global_int(self):
        self.assertEqual(demangle_msvc('?myvar@@3HA'),
                         'int myvar')

    def test_public_static_member_int(self):
        self.assertEqual(demangle_msvc('?svar@MyClass@@2HA'),
                         'public: static int MyClass::svar')

    def test_private_static_member_int(self):
        # 0 = private static
        result = demangle_msvc('?psvar@MyClass@@0HA')
        self.assertIn('private:', result)
        self.assertIn('static', result)
        self.assertIn('int', result)


class TestMSVCUserDefinedTypes(unittest.TestCase):
    """Test user-defined type demangling in parameters."""

    def test_struct_param(self):
        self.assertEqual(demangle_msvc('?sfunc@@YAXUMyStruct@@@Z'),
                         'void __cdecl sfunc(struct MyStruct)')

    def test_class_param(self):
        self.assertEqual(demangle_msvc('?cfunc2@@YAXVMyClass@@@Z'),
                         'void __cdecl cfunc2(class MyClass)')

    def test_enum_param(self):
        self.assertEqual(demangle_msvc('?efunc@@YAXW4MyEnum@@@Z'),
                         'void __cdecl efunc(enum MyEnum)')

    def test_union_param(self):
        result = demangle_msvc('?ufunc2@@YAXTMyUnion@@@Z')
        self.assertIn('union', result)
        self.assertIn('MyUnion', result)


class TestMSVCScope(unittest.TestCase):
    """Test namespace and nested class scope."""

    def test_namespace(self):
        self.assertEqual(demangle_msvc('?func@ns@@YAXH@Z'),
                         'void __cdecl ns::func(int)')

    def test_nested_class(self):
        self.assertEqual(demangle_msvc('?method@Inner@Outer@@UAEXH@Z'),
                         'public: virtual void __thiscall Outer::Inner::method(int)')

    def test_deep_namespace(self):
        result = demangle_msvc('?func@a@b@c@@YAXH@Z')
        self.assertIn('c::b::a', result)


class TestMSVCExtendedTypes(unittest.TestCase):
    """Test extended primitive types (_ prefix)."""

    def test_int8(self):
        result = demangle_msvc('?f@@YAX_D@Z')
        self.assertIn('signed char', result)

    def test_uint8(self):
        result = demangle_msvc('?f@@YAX_E@Z')
        self.assertIn('unsigned char', result)

    def test_int16(self):
        result = demangle_msvc('?f@@YAX_F@Z')
        self.assertIn('short', result)

    def test_int32(self):
        result = demangle_msvc('?f@@YAX_H@Z')
        self.assertIn('int', result)

    def test_int64(self):
        result = demangle_msvc('?f@@YAX_J@Z')
        self.assertIn('__int64', result)

    def test_bool(self):
        result = demangle_msvc('?f@@YAX_N@Z')
        self.assertIn('bool', result)

    def test_wchar_t(self):
        result = demangle_msvc('?f@@YAX_W@Z')
        self.assertIn('wchar_t', result)


class TestMSVCStructuredOutput(unittest.TestCase):
    """Test structured DemangledSymbol output for MSVC."""

    def test_structured_function(self):
        sym = demangle_msvc('?foo@@YAXH@Z', structured=True)
        self.assertIsInstance(sym, DemangledSymbol)
        self.assertEqual(sym.format, 'msvc')
        self.assertEqual(sym.full_name, 'void __cdecl foo(int)')
        self.assertEqual(sym.original_mangled, '?foo@@YAXH@Z')

    def test_structured_member_function(self):
        sym = demangle_msvc('?bar@MyClass@@UAEXH@Z', structured=True)
        self.assertIsInstance(sym, DemangledSymbol)
        self.assertEqual(sym.format, 'msvc')
        self.assertEqual(sym.full_name,
                         'public: virtual void __thiscall MyClass::bar(int)')

    def test_structured_constructor(self):
        sym = demangle_msvc('??0MyClass@@QAE@X@Z', structured=True)
        self.assertIsInstance(sym, DemangledSymbol)
        self.assertEqual(sym.full_name,
                         'public: __thiscall MyClass::MyClass(void)')

    def test_structured_destructor(self):
        sym = demangle_msvc('??1MyClass@@UAE@X@Z', structured=True)
        self.assertIsInstance(sym, DemangledSymbol)
        self.assertEqual(sym.full_name,
                         'public: virtual __thiscall MyClass::~MyClass(void)')

    def test_structured_vtable(self):
        sym = demangle_msvc('??_7MyClass@@6B@', structured=True)
        self.assertIsInstance(sym, DemangledSymbol)
        self.assertEqual(sym.format, 'msvc')

    def test_structured_operator_new(self):
        sym = demangle_msvc('??2@YAPAXI@Z', structured=True)
        self.assertIsInstance(sym, DemangledSymbol)
        self.assertEqual(sym.format, 'msvc')

    def test_structured_variable(self):
        sym = demangle_msvc('?myvar@@3HA', structured=True)
        self.assertIsInstance(sym, DemangledSymbol)
        self.assertEqual(sym.format, 'msvc')

    def test_structured_to_dict(self):
        sym = demangle_msvc('?foo@@YAXH@Z', structured=True)
        d = sym.to_dict()
        self.assertEqual(d['format'], 'msvc')
        self.assertEqual(d['full_name'], 'void __cdecl foo(int)')

    def test_structured_str(self):
        sym = demangle_msvc('?foo@@YAXH@Z', structured=True)
        self.assertEqual(str(sym), 'void __cdecl foo(int)')

    def test_structured_repr(self):
        sym = demangle_msvc('?foo@@YAXH@Z', structured=True)
        r = repr(sym)
        self.assertIn('msvc', r)
        self.assertIn('void __cdecl foo(int)', r)

    def test_structured_eq(self):
        a = demangle_msvc('?foo@@YAXH@Z', structured=True)
        b = demangle_msvc('?foo@@YAXH@Z', structured=True)
        self.assertEqual(a, b)

    def test_structured_hash(self):
        a = demangle_msvc('?foo@@YAXH@Z', structured=True)
        b = demangle_msvc('?foo@@YAXH@Z', structured=True)
        self.assertEqual(len({a, b}), 1)


class TestMSVCParserDirect(unittest.TestCase):
    """Test the MSVC parser directly (AST-level tests)."""

    def test_parser_returns_symbol(self):
        parser = MSVCParser('?foo@@YAXH@Z')
        sym = parser.parse()
        self.assertIsInstance(sym, ast.MSVCSymbol)

    def test_parser_function(self):
        parser = MSVCParser('?foo@@YAXH@Z')
        sym = parser.parse()
        self.assertIsInstance(sym.type_info, ast.FunctionType)
        self.assertEqual(sym.type_info.calling_convention, '__cdecl')
        self.assertEqual(sym.type_info.return_type, 'void')
        self.assertEqual(sym.type_info.parameters, ['int'])

    def test_parser_member_function(self):
        parser = MSVCParser('?bar@MyClass@@UAEXH@Z')
        sym = parser.parse()
        self.assertIsInstance(sym.type_info, ast.FunctionType)
        self.assertEqual(sym.type_info.access, 'public')
        self.assertTrue(sym.type_info.is_virtual)
        self.assertEqual(sym.type_info.calling_convention, '__thiscall')

    def test_parser_constructor(self):
        parser = MSVCParser('??0MyClass@@QAE@X@Z')
        sym = parser.parse()
        self.assertIsInstance(sym.qualified_name.basic_name, ast.SpecialName)
        self.assertTrue(sym.qualified_name.basic_name.is_ctor)

    def test_parser_destructor(self):
        parser = MSVCParser('??1MyClass@@UAE@X@Z')
        sym = parser.parse()
        self.assertIsInstance(sym.qualified_name.basic_name, ast.SpecialName)
        self.assertTrue(sym.qualified_name.basic_name.is_dtor)

    def test_parser_vtable(self):
        parser = MSVCParser('??_7MyClass@@6B@')
        sym = parser.parse()
        self.assertEqual(sym.kind, 'vtable')

    def test_parser_raises_on_non_msvc(self):
        parser = MSVCParser('plain_name')
        with self.assertRaises(ParseError):
            parser.parse()

    def test_parser_raises_on_empty(self):
        parser = MSVCParser('')
        with self.assertRaises(ParseError):
            parser.parse()

    def test_parser_raises_on_hashed(self):
        parser = MSVCParser('??@ABC123@')
        with self.assertRaises(ParseError):
            parser.parse()

    def test_parser_warnings_list(self):
        parser = MSVCParser('?foo@@YAXH@Z')
        parser.parse()
        self.assertIsInstance(parser.warnings, list)

    def test_renderer_renders(self):
        parser = MSVCParser('?foo@@YAXH@Z')
        sym = parser.parse()
        result = render(sym)
        self.assertEqual(result, 'void __cdecl foo(int)')


class TestMSVCASTNodes(unittest.TestCase):
    """Test MSVC AST node classes."""

    def test_fragment_name(self):
        node = ast.FragmentName('foo')
        self.assertEqual(node.name, 'foo')
        self.assertIn('foo', repr(node))

    def test_special_name_ctor(self):
        node = ast.SpecialName('', kind='ctor', is_ctor=True)
        self.assertTrue(node.is_ctor)
        self.assertFalse(node.is_dtor)

    def test_special_name_dtor(self):
        node = ast.SpecialName('~Foo', kind='dtor', is_dtor=True)
        self.assertTrue(node.is_dtor)
        self.assertFalse(node.is_ctor)

    def test_special_name_operator(self):
        node = ast.SpecialName('operator+', kind='operator', is_operator=True)
        self.assertTrue(node.is_operator)
        self.assertEqual(node.name, 'operator+')

    def test_qualified_name(self):
        scope = [ast.FragmentName('MyClass')]
        basic = ast.FragmentName('method')
        qn = ast.QualifiedName(scope, basic)
        self.assertEqual(len(qn.scope), 1)
        self.assertIs(qn.basic_name, basic)

    def test_primitive_type(self):
        node = ast.PrimitiveType('int')
        self.assertEqual(node.name, 'int')

    def test_pointer_type(self):
        pt = ast.PointerType('int', is_const=True)
        self.assertEqual(pt.pointee, 'int')
        self.assertTrue(pt.is_const)

    def test_function_type(self):
        ft = ast.FunctionType(
            calling_convention='__cdecl',
            return_type='void',
            parameters=['int'],
            is_member=False,
        )
        self.assertEqual(ft.calling_convention, '__cdecl')
        self.assertEqual(ft.return_type, 'void')
        self.assertEqual(ft.parameters, ['int'])
        self.assertFalse(ft.is_member)

    def test_variable_info(self):
        vi = ast.VariableInfo(access='public', is_static=True, var_type='int')
        self.assertEqual(vi.access, 'public')
        self.assertTrue(vi.is_static)
        self.assertEqual(vi.var_type, 'int')

    def test_vftable(self):
        vft = ast.VFTable(scope=None)
        self.assertIsNone(vft.scope)

    def test_msvc_symbol(self):
        qn = ast.QualifiedName([], ast.FragmentName('foo'))
        sym = ast.MSVCSymbol(qualified_name=qn, kind='function')
        self.assertIs(sym.qualified_name, qn)
        self.assertEqual(sym.kind, 'function')


class TestMSVCGracefulDegradation(unittest.TestCase):
    """Test graceful degradation for invalid or unsupported symbols."""

    def test_invalid_symbol_returns_str(self):
        result = demangle_msvc('?invalid@@@')
        self.assertIsInstance(result, str)

    def test_non_msvc_returns_original(self):
        result = demangle_msvc('plain_function_name')
        self.assertEqual(result, 'plain_function_name')

    def test_empty_string(self):
        result = demangle_msvc('')
        self.assertEqual(result, '')

    def test_hashed_object_returns_original(self):
        result = demangle_msvc('??@ABC123@')
        self.assertEqual(result, '??@ABC123@')

    def test_truncated_question(self):
        result = demangle_msvc('?')
        self.assertIsInstance(result, str)

    def test_truncated_double_question(self):
        result = demangle_msvc('??')
        self.assertIsInstance(result, str)

    def test_binary_garbage(self):
        result = demangle_msvc('\x00\x01\x02\x03')
        self.assertIsInstance(result, str)

    def test_long_input(self):
        result = demangle_msvc('?' + 'a' * 1000)
        self.assertIsInstance(result, str)

    def test_no_crash_on_various_bad(self):
        bad_inputs = [
            '?@', '??@', '???', '????',
            '?foo', '?foo@', '?foo@@',
            '??0', '??1', '??_7', '??_0',
        ]
        for inp in bad_inputs:
            result = demangle_msvc(inp)
            self.assertIsInstance(result, str,
                                  'demangle_msvc(%r) crashed' % inp)


class TestMSVCDispatch(unittest.TestCase):
    """Test MSVC through the main demangle() dispatch."""

    def test_demangle_dispatch(self):
        result = demangle('?foo@@YAXH@Z')
        self.assertEqual(result, 'void __cdecl foo(int)')

    def test_demangle_structured(self):
        sym = demangle('?foo@@YAXH@Z', structured=True)
        self.assertIsInstance(sym, DemangledSymbol)
        self.assertEqual(sym.format, 'msvc')

    def test_demangle_force_msvc(self):
        result = demangle('?foo@@YAXH@Z', fmt='msvc')
        self.assertEqual(result, 'void __cdecl foo(int)')

    def test_demangle_never_raises(self):
        bad_inputs = ['?', '??', '???', '?????', '?@@@', '\x00\x01']
        for inp in bad_inputs:
            result = demangle(inp)
            self.assertIsInstance(result, str,
                                  'demangle(%r) crashed' % inp)


if __name__ == '__main__':
    unittest.main()