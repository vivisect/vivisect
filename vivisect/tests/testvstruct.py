import vstruct
import vivisect
import envi.memcanvas as e_mcanvas
import vstruct.primitives as v_prim
import vivisect.renderers as v_rend
import vivisect.tests.utils as v_t_utils

class VivisectVstructTest(v_t_utils.VivTest):

    def test_render_vstruct(self):
        structcmp = '''.dynsym:0x000099e0  Elf32Symbol: 
.dynsym:0x000099e0    st_name:     0x5ba   (1466)
.dynsym:0x000099e4    st_value:    0x21769   (137065)
.dynsym:0x000099e8    st_size:     0x6c   (108)
.dynsym:0x000099ec    st_info:     0x12   (18)
.dynsym:0x000099ed    st_other:    0x0   (0)
.dynsym:0x000099ee    st_shndx:    0xb   (11)
'''

        vw = vivisect.VivWorkspace()
        vw.setMeta('Architecture', 'i386')
        canvas = e_mcanvas.StringMemoryCanvas(vw)
        vw.addSegment(0x1000, 0x9000, '.dynsym', 'foobar')
        vw.addMemoryMap(0x99e0, 7, 'foobar', b'\xba\x05\x00\x00\x69\x17\x02\x00\x6c\x00\x00\x00\x12\x00\x0b' + b'\0'*1000)
        wsr = v_rend.WorkspaceRenderer(vw)

        mod = vw.loadModule('vstruct.defs.elf')
        vw.vsbuilder.addVStructNamespace('elf', mod)
        vw.makeStructure(0x99e0, 'elf.Elf32Symbol')
        wsr = v_rend.WorkspaceRenderer(vw)
        loc = vw.getLocation(0x99e0)

        struct = vw.getStructure(0x99e0, loc[vivisect.L_TINFO])
        wsr.renderLocation(canvas, loc, None, False, 'cmnt', struct)
        self.maxDiff=1000
        self.assertEqual(canvas.strval, structcmp)
