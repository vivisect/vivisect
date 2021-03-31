import logging
import binascii
import unittest

import vivisect

import vivisect.symboliks.archs.i386 as i386sym
import vivisect.symboliks.archs.amd64 as amd64sym

import vivisect.symboliks.tests.data_i386 as i386_data
import vivisect.symboliks.tests.data_amd64 as amd64_data

logger = logging.getLogger(__name__)

xlators = {
    'amd64': amd64sym.Amd64SymbolikTranslator,
    'i386': i386sym.i386SymbolikTranslator,
}

answers = {
    'amd64': amd64_data.effects,
    'i386': i386_data.effects,
}


class TranslatorTests(unittest.TestCase):

    def _run_translator_test(self, arch):
        vw = vivisect.VivWorkspace()
        vw.setMeta('Architecture', arch)
        xlate = xlators[arch](vw)
        effects = answers[arch]

        failures = []
        for name, desc in effects.items():
            opbytes, tesva, testcons, testeffs = desc
            op = vw.arch.archParseOpcode(binascii.unhexlify(opbytes), 0, 0x400)
            xlate.translateOpcode(op)

            effs = [str(e) for e in xlate.getEffects()]
            cons = [str(c) for c in xlate.getConstraints()]

            try:
                self.assertEqual(len(effs), len(testeffs))
                self.assertEqual(len(cons), len(testcons))
            except AssertionError:
                failures.append(op)
                xlate.clearEffects()
                continue

            try:
                for e in testeffs:
                    if e.startswith('SKIP'):
                        continue
                    self.assertTrue(str(e) in effs)
                for c in testcons:
                    if c.startswith('SKIP'):
                        continue
                    self.assertTrue(str(c) in cons)
            except AssertionError:
                failures.append(op)
            except Exception as e:
                logger.warning('%s failed due to exception %s', op, str(e))
                failures.append(op)
            xlate.clearEffects()

        if failures:
            msg = ', '.join([str(o) for o in failures])
            self.fail('(Arch: %s) These instructions failed to produce correct effects: %s' % (arch, msg))

    def test_amd64_instructions(self):
        self._run_translator_test('amd64')

    def test_i386_instructions(self):
        self._run_translator_test('i386')
