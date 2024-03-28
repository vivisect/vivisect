import unittest
import envi.cli as e_cli
import envi.memory as e_mem
import envi.memcanvas as e_mcanvas
import envi.memcanvas.renderers as e_render


class EnviCliTest(unittest.TestCase):
    def test_do_cmds(self):
        mem = e_mem.MemoryObject()
        mem.addMemoryMap(0x41410000, 7, 'testmem', b'@ABCDEF'*256)

        ecli = e_cli.EnviCli(mem)

        ecli.canvas = e_mcanvas.StringMemoryCanvas(mem)
        ecli.canvas.addRenderer("bytes", e_render.ByteRend())
        ecli.canvas.addRenderer("u_int_16", e_render.ShortRend())
        ecli.canvas.addRenderer("u_int_32", e_render.LongRend())
        ecli.canvas.addRenderer("u_int_64", e_render.QuadRend())

        # do_alias
        ecli.do_alias('')
        output = ecli.canvas.strval
        self.assertIn('Runtime Aliases (not saved):', output)
        self.assertIn('Configured Aliases:', output)
        ecli.canvas.clearCanvas()

        # do_binstr
        ecli.do_binstr('47145')
        output = ecli.canvas.strval
        self.assertIn('0x0000b829 (47145) 1011100000101001', output)
        ecli.canvas.clearCanvas()

        # do_clear
        ecli.vprint("foobar")
        ecli.do_clear('')
        output = ecli.canvas.strval
        self.assertEqual('', output)
        ecli.canvas.clearCanvas()

        # do_config
        ecli.do_config('')
        output = ecli.canvas.strval
        self.assertIn('cli.verbose = False\n', output)
        ecli.canvas.clearCanvas()

        # do_EOF
        ecli.do_EOF('')
        output = ecli.canvas.strval
        self.assertIn('Use quit\n', output)
        ecli.canvas.clearCanvas()

        # do_eval
        ecli.do_eval('0x40 + 0x47145')
        output = ecli.canvas.strval
        self.assertIn('0x40 + 0x47145 = 0x00047185 (291205)\n', output)
        ecli.canvas.clearCanvas()

        # do_maps
        ecli.do_maps('')
        output = ecli.canvas.strval
        self.assertIn('0x41410000', output)
        ecli.canvas.clearCanvas()

        ecli.do_maps('0x41410001')
        output = ecli.canvas.strval
        self.assertIn(' 0x41410001\n0x41410000', output)
        ecli.canvas.clearCanvas()

        # do_mem
        ecli.do_mem('0x41410001 20')
        output = ecli.canvas.strval
        self.assertIn('0x41410001  41 42 43 44 45 46 40 41 42 43 44 45 46 40 41 42   ABCDEF@ABCDEF@AB\n0x41410011  43 44 45 46 40 41 42 43 44 45 46 40 41 42 43 44   CDEF@ABCDEF@ABCD\n', output)
        ecli.canvas.clearCanvas()

        ecli.do_mem('-F u_int_16 0x41410001 20')
        output = ecli.canvas.strval
        self.assertIn('0x41410001  4241 4443 4645 4140 4342 4544 4046 4241   ABCDEF@ABCDEF@AB\n0x41410011  4443 4645 4140 4342 4544 4046 4241 4443   CDEF@ABCDEF@ABCD\n', output)
        ecli.canvas.clearCanvas()

        ecli.do_mem('-F u_int_32 0x41410001 20')
        output = ecli.canvas.strval
        self.assertIn('0x41410001  44434241 41404645 45444342 42414046   ABCDEF@ABCDEF@AB\n0x41410011  46454443 43424140 40464544 44434241   CDEF@ABCDEF@ABCD\n', output)
        ecli.canvas.clearCanvas()

        ecli.do_mem('-F u_int_64 0x41410001 20')
        output = ecli.canvas.strval
        self.assertIn('0x0000000041410001  4140464544434241 4241404645444342   ABCDEF@ABCDEF@AB\n0x0000000041410011  4342414046454443 4443424140464544   CDEF@ABCDEF@ABCD\n', output)
        ecli.canvas.clearCanvas()

        # do_memcmp
        ecli.do_memcmp('0x41410001 0x41410005 20')
        output = ecli.canvas.strval
        self.assertIn('==== 20 byte difference at offset 0\n0x41410001:4142434445464041424344454640414243444546\n0x41410005:4546404142434445464041424344454640414243\n', output)
        ecli.canvas.clearCanvas()
        
        # do_memdump
        ecli.do_memdump('0x41410001 /tmp/foo40 20')
        output = ecli.canvas.strval
        self.assertIn('wrote 20 bytes.\n', output)
        ecli.canvas.clearCanvas()
        with open('/tmp/foo40', 'rb') as testfile:
            self.assertEqual(testfile.read(), b'ABCDEF@ABCDEF@ABCDEF')
        ecli.canvas.clearCanvas()
       
        # do_python
        ecli.do_python('with open("/tmp/foo41", "wb") as testfile:\n\ttestfile.write(b"Test Worked")')
        output = ecli.canvas.strval
        with open('/tmp/foo41', 'rb') as testfile:
            self.assertEqual(testfile.read(), b'Test Worked')
        ecli.canvas.clearCanvas()

        # do_saveout
        ecli.do_saveout('/tmp/foo42 search ABCDEF')
        output = ecli.canvas.strval
        self.assertIn('\ndone (256 results).\n', output)
        ecli.canvas.clearCanvas()

        # do_search
        ecli.do_search('ABCDEF')
        output = ecli.canvas.strval
        self.assertIn('\ndone (256 results).\n', output)
        ecli.canvas.clearCanvas()

