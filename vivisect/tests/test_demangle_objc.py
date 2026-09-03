"""
Comprehensive tests for the Objective-C demangling module.

Tests cover:
- Class references (_OBJC_CLASS_$_)
- Metaclass references (_OBJC_METACLASS_$_)
- Instance variables (_OBJC_IVAR_$_)
- Exception types (_OBJC_EHTYPE_$_)
- Category symbols
- Class method syntax (+[Class method])
- Instance method syntax (-[Class method])
- Structured output
- Graceful degradation
"""

import unittest

from vivisect.demangle import demangle, detect_format
from vivisect.demangle.objc import demangle_objc
from vivisect.demangle.common import DemangledSymbol


class TestObjCClassRef(unittest.TestCase):
    """Test _OBJC_CLASS_$_ symbol demangling."""

    def test_simple_class(self):
        self.assertEqual(demangle_objc('_OBJC_CLASS_$_NSObject'), 'NSObject')

    def test_custom_class(self):
        self.assertEqual(demangle_objc('_OBJC_CLASS_$_MyViewController'),
                         'MyViewController')


class TestObjCMetaclassRef(unittest.TestCase):
    """Test _OBJC_METACLASS_$_ symbol demangling."""

    def test_metaclass(self):
        self.assertEqual(demangle_objc('_OBJC_METACLASS_$_NSObject'),
                         'NSObject')

    def test_custom_metaclass(self):
        self.assertEqual(demangle_objc('_OBJC_METACLASS_$_MyClass'),
                         'MyClass')


class TestObjCIVar(unittest.TestCase):
    """Test _OBJC_IVAR_$_ symbol demangling."""

    def test_ivar(self):
        result = demangle_objc('_OBJC_IVAR_$_NSObject._isa')
        self.assertIn('NSObject', result)
        self.assertIn('_isa', result)

    def test_custom_ivar(self):
        result = demangle_objc('_OBJC_IVAR_$_MyClass._myField')
        self.assertIn('MyClass', result)
        self.assertIn('_myField', result)


class TestObjCExceptionType(unittest.TestCase):
    """Test _OBJC_EHTYPE_$_ symbol demangling."""

    def test_exception_type(self):
        result = demangle_objc('_OBJC_EHTYPE_$_MyException')
        self.assertEqual(result, 'MyException')


class TestObjCMethodSyntax(unittest.TestCase):
    """Test +[Class method] / -[Class method] syntax."""

    def test_class_method_alloc(self):
        self.assertEqual(demangle_objc('+[NSObject alloc]'),
                         '+[NSObject alloc]')

    def test_instance_method_init(self):
        self.assertEqual(demangle_objc('-[NSObject init]'),
                         '-[NSObject init]')

    def test_class_method_custom(self):
        self.assertEqual(demangle_objc('+[MyClass sharedInstance]'),
                         '+[MyClass sharedInstance]')

    def test_instance_method_with_args(self):
        self.assertEqual(demangle_objc('-[NSObject setValue:forKey:]'),
                         '-[NSObject setValue:forKey:]')


class TestObjCStructuredOutput(unittest.TestCase):
    """Test structured DemangledSymbol output for ObjC."""

    def test_structured_class_ref(self):
        sym = demangle_objc('_OBJC_CLASS_$_NSObject', structured=True)
        self.assertIsInstance(sym, DemangledSymbol)
        self.assertEqual(sym.format, 'objc')
        self.assertEqual(sym.kind, 'class_ref')
        self.assertEqual(sym.name, 'NSObject')

    def test_structured_metaclass(self):
        sym = demangle_objc('_OBJC_METACLASS_$_NSObject', structured=True)
        self.assertEqual(sym.kind, 'metaclass_ref')

    def test_structured_ivar(self):
        sym = demangle_objc('_OBJC_IVAR_$_NSObject._isa', structured=True)
        self.assertEqual(sym.kind, 'ivar')
        self.assertIn('NSObject', sym.scope)

    def test_structured_method(self):
        sym = demangle_objc('+[NSObject alloc]', structured=True)
        self.assertEqual(sym.kind, 'method')

    def test_structured_original(self):
        orig = '_OBJC_CLASS_$_NSObject'
        sym = demangle_objc(orig, structured=True)
        self.assertEqual(sym.original_mangled, orig)


class TestObjCGracefulDegradation(unittest.TestCase):
    """Test graceful degradation for invalid ObjC symbols."""

    def test_non_objc_returns_original(self):
        result = demangle_objc('plain_function')
        self.assertEqual(result, 'plain_function')

    def test_empty_string(self):
        result = demangle_objc('')
        self.assertEqual(result, '')

    def test_non_objc_structured(self):
        sym = demangle_objc('plain_function', structured=True)
        self.assertIsInstance(sym, DemangledSymbol)
        self.assertTrue(sym.parse_warnings)


class TestObjCDispatch(unittest.TestCase):
    """Test ObjC through the main demangle() dispatch."""

    def test_detect_class_ref(self):
        self.assertEqual(detect_format('_OBJC_CLASS_$_NSObject'), 'objc')

    def test_detect_metaclass(self):
        self.assertEqual(detect_format('_OBJC_METACLASS_$_NSObject'), 'objc')

    def test_detect_ivar(self):
        self.assertEqual(detect_format('_OBJC_IVAR_$_NSObject._isa'), 'objc')

    def test_detect_class_method(self):
        self.assertEqual(detect_format('+[NSObject alloc]'), 'objc')

    def test_detect_instance_method(self):
        self.assertEqual(detect_format('-[NSObject init]'), 'objc')

    def test_demangle_dispatch(self):
        result = demangle('_OBJC_CLASS_$_NSObject')
        self.assertEqual(result, 'NSObject')

    def test_demangle_structured(self):
        sym = demangle('_OBJC_CLASS_$_NSObject', structured=True)
        self.assertEqual(sym.format, 'objc')


if __name__ == '__main__':
    unittest.main()