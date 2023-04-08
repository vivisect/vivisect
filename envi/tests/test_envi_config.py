import unittest

import envi.config as e_config


class ConfigTest(unittest.TestCase):
    def test_config_params(self):
        defaults = {
            'woot': 10,
            'biz': '0x41414141',
            'foosub': {
                'bar': 'qwer',
                'baz': ('one', 'two', 'three'),
            }
        }
        cfg = e_config.EnviConfig(defaults=defaults)

        self.assertEqual(cfg.woot, 10)
        self.assertEqual(cfg.foosub.bar, 'qwer')
        self.assertEqual(cfg.foosub.baz[0], 'one')
        self.assertEqual(cfg.biz, '0x41414141')
        for idx, item in enumerate(cfg.foosub.baz):
            self.assertEqual(defaults['foosub']['baz'][idx], item)

    def test_config_by_string(self):
        defaults = {
            'woot': 10,
            'biz': '0x41414141',
            'foosub': {
                'bar': 'qwer',
                'baz': ('one', 'two', 'three'),
            }
        }
        cfg = e_config.EnviConfig(defaults=defaults)

        self.assertEqual(cfg.getOptionByString('woot'), 0xa)
        self.assertEqual(cfg.getOptionByString('biz'), '0x41414141')
        self.assertEqual(cfg.getOptionByString('foosub.bar'), 'qwer')
        self.assertEqual(cfg.getOptionByString('foosub.baz'), ('one', 'two', 'three'))

