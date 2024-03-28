import os
import binascii
import unittest

import vstruct
import vstruct.cparse as vs_cparse
import vstruct.builder as vs_builder


csrc_simple = '''
struct monty {
    int life;
    char of;
    long brian;
};
'''

csrc_nested = '''
struct python {
    unsigned short meaning;
    struct andthe {
        unsigned long int of;
        char life[20];
    } holygrail;
    int hollywood[64];
    unsigned char bow[5];
};
'''


class VstructBuilderTest(unittest.TestCase):

    def test_init(self):
        simple = vs_cparse.ctorFromCSource(csrc_simple)
        nested = vs_cparse.ctorFromCSource(csrc_nested)

        bldr = vs_builder.VStructBuilder()
        bldr.addVStructCtor('pe.simple', simple)
        bldr.addVStructCtor('elf.nested', nested)
        self.assertEqual(set(['pe.simple', 'elf.nested']), set(bldr.getVStructNames()))

        bldr.delVStructCtor('elf.nested')
        self.assertEqual(['pe.simple'], bldr.getVStructNames())

    def test_constructor(self):
        pass

    def test_namespaces(self):
        bldr = vs_builder.VStructBuilder()
        subb = vs_builder.VStructBuilder()

        bldr.addVStructNamespace('subname', subb)
        bldr.addVStructNamespace('dupname', subb)
        self.assertTrue(bldr.hasVStructNamespace('subname'))
        self.assertEqual(set(bldr.getVStructNamespaces()), set([('subname', subb), ('dupname', subb)]))
        self.assertEqual(set(bldr.getVStructNamespaceNames()), set(['subname', 'dupname']))

        nested = vs_cparse.ctorFromCSource(csrc_nested)
        bldr.addVStructCtor('foo', nested)
        self.assertEqual(bldr.getVStructCtorNames(), ['foo'])

    def test_get_pycode(self):
        # TODO: Windows CI
        pass
