import unittest

import vivisect.lib.pagelook as v_pagelook

class PageLookTest(unittest.TestCase):

    def test_pagelook_basic(self):
        p = v_pagelook.PageLook()
        p.put( 0x41414100, 0xffff, 'woot' )

        self.assertEqual( p.get(0x41414000), 'woot' )
        self.assertEqual( p.get(0x41414100), 'woot' )
        self.assertEqual( p.get(0x41415555), 'woot' )

        self.assertIsNone( p.get(0x56560000) )
