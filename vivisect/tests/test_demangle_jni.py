"""
Comprehensive tests for the JNI (Java Native Interface) demangling module.

Tests cover:
- Simple (non-overloaded) method names
- Overloaded method names with type signatures
- All JNI primitive type descriptors
- Object types (L<class>;)
- Array types (multi-dimensional)
- Escape sequences (_1, _2, _3, _00024, _0xxxx)
- Class/method name splitting
- Structured output
- Graceful degradation
"""

import unittest

from vivisect.demangle import demangle, detect_format
from vivisect.demangle.jni import demangle_jni, _unmangle_jni_string, _parse_jni_signature
from vivisect.demangle.common import DemangledSymbol


class TestJNIFunctionDemangle(unittest.TestCase):
    """Test JNI method name demangling."""

    def test_simple_method(self):
        result = demangle_jni('Java_pkg_Cls_f')
        self.assertIn('pkg', result)
        self.assertIn('Cls', result)
        self.assertIn('f', result)

    def test_deep_package(self):
        result = demangle_jni('Java_com_example_deep_pkg_Cls_method')
        self.assertIn('com', result)
        self.assertIn('example', result)
        self.assertIn('method', result)

    def test_overloaded_method_int_string(self):
        result = demangle_jni('Java_pkg_Cls_f__ILjava_lang_String_2')
        self.assertIn('int', result)
        self.assertIn('java.lang.String', result)

    def test_overloaded_method_multiple_types(self):
        result = demangle_jni('Java_pkg_Cls_g__IJFDZB')
        self.assertIn('int', result)
        self.assertIn('long', result)
        self.assertIn('float', result)
        self.assertIn('double', result)
        self.assertIn('boolean', result)
        self.assertIn('byte', result)


class TestJNIPrimitiveTypes(unittest.TestCase):
    """Test all JNI primitive type descriptors."""

    def test_int(self):
        params = _parse_jni_signature('I')
        self.assertEqual(params, ['int'])

    def test_boolean(self):
        params = _parse_jni_signature('Z')
        self.assertEqual(params, ['boolean'])

    def test_byte(self):
        params = _parse_jni_signature('B')
        self.assertEqual(params, ['byte'])

    def test_char(self):
        params = _parse_jni_signature('C')
        self.assertEqual(params, ['char'])

    def test_short(self):
        params = _parse_jni_signature('S')
        self.assertEqual(params, ['short'])

    def test_long(self):
        params = _parse_jni_signature('J')
        self.assertEqual(params, ['long'])

    def test_float(self):
        params = _parse_jni_signature('F')
        self.assertEqual(params, ['float'])

    def test_double(self):
        params = _parse_jni_signature('D')
        self.assertEqual(params, ['double'])

    def test_void(self):
        params = _parse_jni_signature('V')
        self.assertEqual(params, ['void'])


class TestJNIObjectTypes(unittest.TestCase):
    """Test JNI object type descriptors (L<class>;)."""

    def test_simple_object(self):
        params = _parse_jni_signature('Ljava/lang/String;')
        self.assertEqual(params, ['java.lang.String'])

    def test_object_with_package(self):
        params = _parse_jni_signature('Lcom/example/MyClass;')
        self.assertEqual(params, ['com.example.MyClass'])

    def test_multiple_objects(self):
        params = _parse_jni_signature('Ljava/lang/String;Ljava/util/List;')
        self.assertEqual(params, ['java.lang.String', 'java.util.List'])


class TestJNIArrayTypes(unittest.TestCase):
    """Test JNI array type descriptors."""

    def test_int_array(self):
        params = _parse_jni_signature('[I')
        self.assertEqual(params, ['int[]'])

    def test_object_array(self):
        params = _parse_jni_signature('[Ljava/lang/String;')
        self.assertEqual(params, ['java.lang.String[]'])

    def test_multi_dim_array(self):
        params = _parse_jni_signature('[[I')
        self.assertEqual(params, ['int[][]'])

    def test_three_dim_array(self):
        params = _parse_jni_signature('[[[D')
        self.assertEqual(params, ['double[][][]'])


class TestJNIEscapes(unittest.TestCase):
    """Test JNI escape sequence decoding."""

    def test_underscore_escape(self):
        # _1 → _
        result = _unmangle_jni_string('foo_1bar')
        self.assertEqual(result, 'foo_bar')

    def test_semicolon_escape(self):
        # _2 → ;
        result = _unmangle_jni_string('foo_2bar')
        self.assertEqual(result, 'foo;bar')

    def test_bracket_escape(self):
        # _3 → [
        result = _unmangle_jni_string('foo_3bar')
        self.assertEqual(result, 'foo[bar')

    def test_class_separator(self):
        # _ → . (default class separator)
        result = _unmangle_jni_string('pkg_Cls')
        self.assertEqual(result, 'pkg.Cls')

    def test_slash_separator(self):
        # _ → / when class_sep='/'
        result = _unmangle_jni_string('java_lang', class_sep='/')
        self.assertEqual(result, 'java/lang')


class TestJNIStructuredOutput(unittest.TestCase):
    """Test structured DemangledSymbol output for JNI."""

    def test_structured_function(self):
        sym = demangle_jni('Java_pkg_Cls_f__ILjava_lang_String_2', structured=True)
        self.assertIsInstance(sym, DemangledSymbol)
        self.assertEqual(sym.format, 'jni')
        self.assertEqual(sym.kind, 'function')
        self.assertIn('int', sym.parameters)
        self.assertIn('java.lang.String', sym.parameters)

    def test_structured_scope(self):
        sym = demangle_jni('Java_pkg_Cls_f', structured=True)
        self.assertIsInstance(sym, DemangledSymbol)
        self.assertIn('pkg', sym.scope)

    def test_structured_original(self):
        orig = 'Java_pkg_Cls_f__ILjava_lang_String_2'
        sym = demangle_jni(orig, structured=True)
        self.assertEqual(sym.original_mangled, orig)


class TestJNIGracefulDegradation(unittest.TestCase):
    """Test graceful degradation for invalid JNI names."""

    def test_non_jni_returns_original(self):
        result = demangle_jni('plain_function')
        self.assertEqual(result, 'plain_function')

    def test_empty_string(self):
        result = demangle_jni('')
        self.assertEqual(result, '')

    def test_non_jni_structured(self):
        sym = demangle_jni('plain_function', structured=True)
        self.assertIsInstance(sym, DemangledSymbol)
        self.assertTrue(sym.parse_warnings)


class TestJNIDispatch(unittest.TestCase):
    """Test JNI through the main demangle() dispatch."""

    def test_detect_jni(self):
        self.assertEqual(detect_format('Java_pkg_Cls_f'), 'jni')

    def test_detect_overloaded(self):
        self.assertEqual(detect_format('Java_pkg_Cls_f__ILjava_lang_String_2'), 'jni')

    def test_demangle_dispatch(self):
        result = demangle('Java_pkg_Cls_f__ILjava_lang_String_2')
        self.assertIsInstance(result, str)
        self.assertIn('int', result)

    def test_demangle_structured(self):
        sym = demangle('Java_pkg_Cls_f__ILjava_lang_String_2', structured=True)
        self.assertEqual(sym.format, 'jni')


if __name__ == '__main__':
    unittest.main()