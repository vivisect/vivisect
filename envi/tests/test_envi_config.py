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

        self.assertEquals(cfg.woot, 10)
        self.assertEquals(cfg.foosub.bar, 'qwer')
        self.assertEquals(cfg.foosub.baz[0], 'one')
        self.assertEquals(cfg.biz, '0x41414141')
        for idx, item in enumerate(cfg.foosub.baz):
            self.assertEquals(defaults['foosub']['baz'][idx], item)
