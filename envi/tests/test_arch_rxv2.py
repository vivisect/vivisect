import struct
import binascii

import envi
import envi.exc as e_exc
import envi.memory as e_mem
import envi.memcanvas as e_memcanvas
import envi.memcanvas.renderers as e_rend
import vivisect

import logging
import platform
import unittest

from envi import IF_RET, IF_NOFALL, IF_BRANCH, IF_CALL, IF_COND


logger = logging.getLogger(__name__)
#import envi.common as e_common
#e_common.initLogging(logger, logging.WARN)


GOOD_TESTS = 231
GOOD_EMU_TESTS = 0


instrs = [
        ('06a202f4a020', 0x4560, 'adc 0x8280[r15].l,r4', 0, ()),   # FORM_RD_LD_MI_RS
        ('06e302f4', 0x4560, 'adc r15,r4', 0, ()),                  # FORM_RD_LD_MI_RS
        ('06a102f421', 0x4560, 'adc 0x84[r15].l,r4', 0, ()),        # FORM_RD_LD_MI_RS
        ('fd7c24434241', 0x4560, 'adc #0x414243,r4', 0, ()),        # FORM_RD_LI
        ('fda432', 0x4560, 'shar #0x4,r3,r2', 0, ()),               # DFLT-3/4
        ('7f14', 0x4560, 'jsr r4', envi.IF_CALL, ()),               # DFLT-1
        ('7e24', 0x4560, 'abs r4', 0, ()),                          # DFLT-1
        ('fc0f42', 0x4560, 'abs r4,r2', 0, ()),                     # DFLT-2
        ('623b', 0x4560, 'add #0x3,r11', 0, ()),                    # FORM_RD_IMM
        ('4a234241', 0x4560, 'add 0x4142[r2].ub,r3', 0, ()),        # FORM_RD_LD_RS
        ('06ca454241', 0x4560, 'add 0x8284[r4].uw,r5', 0, ()),      # FORM_RD_LD_MI_RS
        ('068823', 0x4560, 'add [r2].l,r3', 0, ()),                 # FORM_RD_LD_MI_RS
        ('6423', 0x4560, 'and #0x2,r3', 0, ()),                     # FORM_RD_IMM
        ('742344434241', 0x4560, 'and #0x41424344,r3', 0, ()),      # FORM_RD_LI
        ('5323', 0x4560, 'and r2,r3', 0, ()),                       # FORM_RD_LD_RS
        ('52234342', 0x4560, 'and 0x4243[r2].ub,r3', 0, ()),        # FORM_RD_LD_RS
        ('2423', 0x4560, 'bgtu.b 0x4583', 0, ()),                     # FORM_PCDSP
        ('1f', 0x4560, 'bnz.s 0x4567', 0, ()),                        # FORM_PCDSP
        ('18', 0x4560, 'bnz.s 0x4568', 0, ()),                        # FORM_PCDSP
        ('2240', 0x4560, 'bgeu.b 0x45a0', 0, ()),                     # FORM_PCDSP
        ('3b1547', 0x4560, 'bnz.w 0x8c75', 0, ()),                    # FORM_PCDSP
        ('fced3468', 0x4560, 'bmgtu #0x3,0x68[r3].b', 0, ()),         # FORM_BMCND
        ('fde734', 0x4560, 'bmltu #0x7,r4', 0, ()),               # FORM_
        ('fcf23f4645', 0x4560, 'bnot #0x4,0x4546[r3].b', 0, ()),    # FORM_
        ('fc6e3f6845', 0x4560, 'bnot r15,0x4568[r3].b', 0, ()),    # FORM_
        ('fde6f4', 0x4560, 'bnot #0x6,r4', 0, ()),                  # FORM_PCDSP
        ('fc6f36', 0x4560, 'bnot r6,r3', 0, ()),                    # FORM_BMCND
        ('08', 0x4560, 'bra.s 0x4568', 0, ()),                        # FORM_BMCND
        ('2e05', 0x4560, 'bra.b 0x4565', 0, ()),                      # FORM_BMCND
        ('381547', 0x4560, 'bra.w 0x8c75', 0, ()),                    # FORM_BMCND
        ('7f45', 0x4560, 'bra.l r5', 0, ()),                          # FORM_BMCND
        ('00', 0x4560, 'brk', 0, ()),                               # FORM_BMCND
        ('f2336845', 0x4560, 'bset #0x3,0x4568[r3].b', 0, ()),      # FORM_BMCND
        ('fc62346845', 0x4560, 'bset r4,0x4568[r3].b', 0, ()),     # FORM_BMCND
        ('7834', 0x4560, 'bset #0x3,r4', 0, ()),             # FORM_BMCND
        ('7934', 0x4560, 'bset #0x13,r4', 0, ()),             # FORM_BMCND
        ('fc6334', 0x4560, 'bset r4,r3', 0, ()),             # FORM_BMCND
        ('396845', 0x4560, 'bsr.w 0x8ac8', 0, ()),             # FORM_BMCND
        ('05006845', 0x4560, 'bsr.a 0x45ad60', 0, ()),             # FORM_BMCND
        ('7f53', 0x4560, 'bsr.l r3', 0, ()),             # FORM_BMCND
        ('f6336845', 0x4560, 'btst #0x3,0x4568[r3].b', 0, ()),             # FORM_BMCND
        ('fc6aab6845', 0x4560, 'btst r11,0x4568[r10].b', 0, ()),             # FORM_BMCND
        ('7d44', 0x4560, 'btst #0x14,r4', 0, ()),             # FORM_BMCND
        ('fc6bab', 0x4560, 'btst r11,r10', 0, ()),             # FORM_BMCND
        ('7fb3', 0x4560, 'clrpsw O', 0, ()),             # FORM_BMCND
        ('6134', 0x4560, 'cmp #0x3,r4', 0, ()),             # FORM_BMCND
        ('75547f', 0x4560, 'cmp #0x7f,r4', 0, ()),             # FORM_BMCND
        ('76042017', 0x4560, 'cmp #0x1720,r4', 0, ()),             # FORM_BMCND
        ('46348017', 0x4560, 'cmp 0x1780[r3].ub,r4', 0, ()),             # FORM_BMCND
        ('0686348017', 0x4560, 'cmp 0x5e00[r3].l,r4', 0, ()),             # FORM_BMCND
        ('fd78848017', 0x4560, 'div #0x1780,r4', 0, ()),             # FORM_BMCND
        ('fc22348017', 0x4560, 'div 0x1780[r3].ub,r4', 0, ()),             # FORM_BMCND
        ('06a208348017', 0x4560, 'div 0x5e00[r3].l,r4', 0, ()),             # FORM_BMCND
        ('fd78938017', 0x4560, 'divu #0x1780,r3', 0, ()),             # FORM_BMCND
        ('fc26348017', 0x4560, 'divu 0x1780[r3].ub,r4', 0, ()),             # FORM_BMCND
        ('06a209348017', 0x4560, 'divu 0x5e00[r3].l,r4', 0, ()),             # FORM_BMCND
        ('fd0f34', 0x4560, 'emaca r3,r4,acc1', 0, ()),             # FORM_BMCND
        ('fd4f34', 0x4560, 'emsba r3,r4,acc1', 0, ()),             # FORM_BMCND
        ('fd78648017', 0x4560, 'emul #0x1780,r4', 0, ()),             # FORM_BMCND
        ('06a206348017', 0x4560, 'emul 0x5e00[r3].l,r4', 0, ()),             # FORM_BMCND
        ('fd0b34', 0x4560, 'emula r3,r4,acc1', 0, ()),             # FORM_BMCND
        ('fd78748017', 0x4560, 'emulu #0x1780,r4', 0, ()),             # FORM_BMCND
        ('fc1e348017', 0x4560, 'emulu 0x1780[r3].ub,r4', 0, ()),             # FORM_BMCND
        ('06a207348017', 0x4560, 'emulu 0x5e00[r3].l,r4', 0, ()),             # FORM_BMCND
        ('fd722445710400', 0x4560, 'fadd #0x47145,r4', 0, ()),             # FORM_BMCND
        ('fc8a348017', 0x4560, 'fadd 0x5e00[r3].l,r4', 0, ()),             # FORM_BMCND
        ('ffa345', 0x4560, 'fadd r4,r5,r3', 0, ()),             # FORM_BMCND
        ('fd721445710400', 0x4560, 'fcmp #0x47145,r4', 0, ()),             # FORM_BMCND
        ('fc86348017', 0x4560, 'fcmp 0x5e00[r3].l,r4', 0, ()),             # FORM_BMCND    should be: fcmp 0x1780[r3].l,r4  - is: fcmp 0x1780[r3].b,r4
        ('fd724445710400', 0x4560, 'fdiv #0x47145,r4', 0, ()),             # FORM_BMCND
        ('fc92348017', 0x4560, 'fdiv 0x5e00[r3].l,r4', 0, ()),             # FORM_BMCND
        ('fd723445710400', 0x4560, 'fmul #0x47145,r4', 0, ()),             # FORM_BMCND
        ('fc8e348017', 0x4560, 'fmul 0x5e00[r3].l,r4', 0, ()),             # FORM_BMCND
        ('ffb345', 0x4560, 'fmul r4,r5,r3', 0, ()),             # FORM_BMCND
        ('fca2348017', 0x4560, 'fsqrt 0x5e00[r3].l,r4', 0, ()),             # FORM_BMCND
        ('fd720445710400', 0x4560, 'fsub #0x47145,r4', 0, ()),             # FORM_BMCND
        ('fc82348017', 0x4560, 'fsub 0x5e00[r3].l,r4', 0, ()),             # FORM_BMCND
        ('ff8345', 0x4560, 'fsub r4,r5,r3', 0, ()),             # FORM_BMCND
        ('fc96348017', 0x4560, 'ftoi 0x5e00[r3].l,r4', 0, ()),             # FORM_BMCND
        ('fca6348017', 0x4560, 'ftou 0x5e00[r3].l,r4', 0, ()),             # FORM_BMCND
        ('756045', 0x4560, 'int #0x45', 0, ()),             # FORM_BMCND
        ('fc46348017', 0x4560, 'itof 0x1780[r3].ub,r4', 0, ()),             # FORM_BMCND
        ('06a211348017', 0x4560, 'itof 0x5e00[r3].l,r4', 0, ()),             # FORM_BMCND
        ('7f04', 0x4560, 'jmp r4', 0, ()),             # FORM_BMCND
        ('7f14', 0x4560, 'jsr r4', 0, ()),             # FORM_BMCND
        ('fd0c34', 0x4560, 'machi r3,r4,acc1', 0, ()),             # FORM_BMCND
        ('fd0e34', 0x4560, 'maclh r3,r4,acc1', 0, ()),             # FORM_BMCND
        ('fd0d34', 0x4560, 'maclo r3,r4,acc1', 0, ()),             # FORM_BMCND
        ('fd78448017', 0x4560, 'max #0x1780,r4', 0, ()),             # FORM_BMCND
        ('fc12348017', 0x4560, 'max 0x1780[r3].ub,r4', 0, ()),             # FORM_BMCND
        ('06a204348017', 0x4560, 'max 0x5e00[r3].l,r4', 0, ()),             # FORM_BMCND
        ('fd745417', 0x4560, 'min #0x17,r4', 0, ()),             # FORM_BMCND
        ('fc153417', 0x4560, 'min 0x17[r3].ub,r4', 0, ()),             # FORM_BMCND
        ('0661043417', 0x4560, 'max 0x2e[r3].w,r4', 0, ()),             # FORM_BMCND
        ('97cb', 0x4560, 'mov.w r3,0x3e[r4]', 0, ()),             # FORM_BMCND
        ('9fcb', 0x4560, 'mov.w 0x3e[r4],r3', 0, ()),             # FORM_BMCND
        ('66f4', 0x4560, 'mov.l #0xf,r4', 0, ()),             # FORM_BMCND # wrong, but doesn't really need a size?
        ('3ecc17', 0x4560, 'mov.l #0x17,0x70[r4]', 0, ()),             # FORM_BMCND
        ('754321', 0x4560, 'mov.l #0x21,r3', 0, ()),             # FORM_BMCND # doesn't really need a size?
        ('fb3a8017', 0x4560, 'mov.l #0x1780,r3', 0, ()),             # FORM_BMCND # doesn't really need a size?
        ('fb3245710400', 0x4560, 'mov.l #0x47145,r3', 0, ()),             # FORM_BMCND # doesn't really need a size?
        ### FIXME: go back through and make sense of all the SIMM/IMM/UIMM parsing.  should these be operand flags?
        ('ef34', 0x4560, 'mov.l r3,r4', 0, ()),             # FORM_
        ('fa3a80171547', 0x4560, 'mov.l #0x4715,0x5e00[r3]', 0, ()),             # FORM_
        ('fe6234', 0x4560, 'mov.l [r2, r3],r4', 0, ()),             # FORM_
        ('eb348017', 0x4560, 'mov.l r4,0x5e00[r3]', 0, ()),             # FORM_
        ('fe2234', 0x4560, 'mov.l r4,[r2, r3]', 0, ()),             # FORM_
        ('e934408017', 0x4560, 'mov.l 0x100[r3],0x5e00[r4]', 0, ()),             # FORM_
        ('fd2234', 0x4560, 'mov.l r4,[r3+]', 0, ()),             # FORM_
        ('fd2634', 0x4560, 'mov.l r4,[-r3]', 0, ()),             # FORM_
        ('fd2a34', 0x4560, 'mov.l [r3+],r4', 0, ()),             # FORM_
        ('fd2e34', 0x4560, 'mov.l [-r3],r4', 0, ()),             # FORM_
        ('fd2c34', 0x4560, 'mov.b [-r3],r4', 0, ()),             # FORM_
        ('fd2f34', 0x4560, 'movli [r3],r4', 0, ()),             # FORM_
        ('bf34', 0x4560, 'movu.w 0x38[r3],r4', 0, ()),             # FORM_
        ('5e348017', 0x4560, 'movu.w 0x2f00[r3],r4', 0, ()),             # FORM_
        ('fed234', 0x4560, 'movu.w [r2, r3],r4', 0, ()),             # FORM_
        ('fd3934', 0x4560, 'movu.w [r3+],r4', 0, ()),             # FORM_
        ('fd4c34', 0x4560, 'msbhi r3,r4,acc1', 0, ()),             # FORM_
        ('fd4634', 0x4560, 'msblh r3,r4,acc0', 0, ()),             # FORM_
        ('fd4d34', 0x4560, 'msblo r3,r4,acc1', 0, ()),             # FORM_
        ('6334', 0x4560, 'mul #0x3,r4', 0, ()),             # FORM_
        ('76138017', 0x4560, 'mul #0x1780,r3', 0, ()),             # FORM_
        ('4e348017', 0x4560, 'mul 0x1780[r3].ub,r4', 0, ()),             # FORM_
        ('068e348017', 0x4560, 'mul 0x5e00[r3].l,r4', 0, ()),             # FORM_
        ('fd0834', 0x4560, 'mulhi r3,r4,acc1', 0, ()),             # FORM_
        ('fd0a34', 0x4560, 'mullh r3,r4,acc1', 0, ()),             # FORM_
        ('fd0934', 0x4560, 'mullo r3,r4,acc1', 0, ()),             # FORM_
        ('fd1ff4', 0x4560, 'mvfacgu #0x1,acc1,r4', 0, ()),             # FORM_
        ('fd1fc4', 0x4560, 'mvfachi #0x1,acc1,r4', 0, ()),             # FORM_
        ('fd1fd4', 0x4560, 'mvfaclo #0x1,acc1,r4', 0, ()),             # FORM_
        ('fd1fe4', 0x4560, 'mvfacmi #0x1,acc1,r4', 0, ()),             # FORM_
        ('fd6a34', 0x4560, 'mvfc fpsw,r4', 0, ()),             # FORM_
        ('fd17b4', 0x4560, 'mvtacgu r4,acc1', 0, ()),             # FORM_
        ('fd1784', 0x4560, 'mvtachi r4,acc1', 0, ()),             # FORM_
        ('fd1794', 0x4560, 'mvtaclo r4,acc1', 0, ()),             # FORM_
        ('fd7b038017', 0x4560, 'mvtc #0x1780,fpsw', 0, ()),             # FORM_
        ('fd6833', 0x4560, 'mvtc r3,fpsw', 0, ()),             # FORM_
        ('757004', 0x4560, 'mvtipl #0x4', 0, ()),             # FORM_
        ('7e14', 0x4560, 'neg r4', 0, ()),             # FORM_
        ('fc0734', 0x4560, 'neg r3,r4', 0, ()),             # FORM_
        ('03', 0x4560, 'nop', 0, ()),             # FORM_
        ('7e04', 0x4560, 'not r4', 0, ()),             # FORM_
        ('fc3b34', 0x4560, 'not r3,r4', 0, ()),             # FORM_
        ('6534', 0x4560, 'or #0x3,r4', 0, ()),             # FORM_
        ('76348017', 0x4560, 'or #0x1780,r4', 0, ()),             # FORM_
        ('56348017', 0x4560, 'or 0x1780[r3].ub,r4', 0, ()),             # FORM_
        ('0696348017', 0x4560, 'or 0x5e00[r3].l,r4', 0, ()),             # FORM_
        ('ff5234', 0x4560, 'or r3,r4,r2', 0, ()),             # FORM_
        ('7eb4', 0x4560, 'pop r4', 0, ()),             # FORM_
        ('7ee3', 0x4560, 'popc fpsw', 0, ()),             # FORM_
        ('7ea3', 0x4560, 'push.l r3', 0, ()),             # FORM_
        ('f63a8017', 0x4560, 'push.l 0x5e00[r3]', 0, ()),             # FORM_
        ('7ec3', 0x4560, 'pushc fpsw', 0, ()),             # FORM_
        ('6e34', 0x4560, 'pushm r3,r4', 0, ()),             # FORM_
        ('fd1990', 0x4560, 'racl #0x2,acc1', 0, ()),             # FORM_
        ('fd1810', 0x4560, 'racw #0x2,acc0', 0, ()),             # FORM_
        ('fd1890', 0x4560, 'racw #0x2,acc1', 0, ()),             # FORM_
        ('fd19d0', 0x4560, 'rdacl #0x2,acc1', 0, ()),             # FORM_
        ('fd18d0', 0x4560, 'rdacw #0x2,acc1', 0, ()),             # FORM_
        ('fd6734', 0x4560, 'revl r3,r4', 0, ()),             # FORM_
        ('fd6534', 0x4560, 'revw r3,r4', 0, ()),             # FORM_
        ('7f8e', 0x4560, 'rmpa.l', 0, ()),             # FORM_
        ('7e54', 0x4560, 'rolc r4', 0, ()),             # FORM_
        ('7e44', 0x4560, 'rorc r4', 0, ()),             # FORM_
        ('fd6fc4', 0x4560, 'rotl #0x1c,r4', 0, ()),             # FORM_
        ('fd6634', 0x4560, 'rotl r3,r4', 0, ()),             # FORM_
        ('fd6dc4', 0x4560, 'rotr #0x1c,r4', 0, ()),             # FORM_
        ('fd6434', 0x4560, 'rotr r3,r4', 0, ()),             # FORM_
        ('fc9a348017', 0x4560, 'round 0x5e00[r3].l,r4', 0, ()),             # FORM_
        ('7f95', 0x4560, 'rte', 0, ()),             # FORM_
        ('7f94', 0x4560, 'rtfi', 0, ()),             # FORM_
        ('02', 0x4560, 'rts', 0, ()),             # FORM_
        ('6740', 0x4560, 'rtsd #0x100', 0, ()),             # FORM_
        ('3f3440', 0x4560, 'rtsd #0x100,r3,r4', 0, ()),             # FORM_
        ('7e34', 0x4560, 'sat r4', 0, ()),             # FORM_
        ('7f93', 0x4560, 'satr', 0, ()),             # FORM_
        ('fc0334', 0x4560, 'sbb r3,r4', 0, ()),             # FORM_
        ('06a200348017', 0x4560, 'sbb 0x5e00[r3].l,r4', 0, ()),             # FORM_
        ('fcda308017', 0x4560, 'scz.l 0x5e00[r3]', 0, ()),             # FORM_
        ('fcda318017', 0x4560, 'scnz.l 0x5e00[r3]', 0, ()),             # FORM_
        ('fcda328017', 0x4560, 'scgeu.l 0x5e00[r3]', 0, ()),             # FORM_
        ('fcda338017', 0x4560, 'scltu.l 0x5e00[r3]', 0, ()),             # FORM_
        ('fcda348017', 0x4560, 'scgtu.l 0x5e00[r3]', 0, ()),             # FORM_
        ('fcda358017', 0x4560, 'scleu.l 0x5e00[r3]', 0, ()),             # FORM_
        ('fcda368017', 0x4560, 'scpz.l 0x5e00[r3]', 0, ()),             # FORM_
        ('fcda378017', 0x4560, 'scn.l 0x5e00[r3]', 0, ()),             # FORM_
        ('fcda388017', 0x4560, 'scge.l 0x5e00[r3]', 0, ()),             # FORM_
        ('fcda398017', 0x4560, 'sclt.l 0x5e00[r3]', 0, ()),             # FORM_
        ('fcda3a8017', 0x4560, 'scgt.l 0x5e00[r3]', 0, ()),             # FORM_
        ('fcda3b8017', 0x4560, 'scle.l 0x5e00[r3]', 0, ()),             # FORM_
        ('fcda3c8017', 0x4560, 'sco.l 0x5e00[r3]', 0, ()),             # FORM_
        ('fcda3d8017', 0x4560, 'scno.l 0x5e00[r3]', 0, ()),             # FORM_
        ('7f83', 0x4560, 'scmpu', 0, ()),             # FORM_
        ('7fa3', 0x4560, 'setpsw o', 0, ()),             # FORM_
        ('6bc4', 0x4560, 'shar #0x1c,r4', 0, ()),             # FORM_
        ('fd6134', 0x4560, 'shar r3,r4', 0, ()),             # FORM_
        ('fdbc34', 0x4560, 'shar #0x1c,r3,r4', 0, ()),             # FORM_
        ('6dc4', 0x4560, 'shll #0x1c,r4', 0, ()),             # FORM_
        ('fd6234', 0x4560, 'shll r3,r4', 0, ()),             # FORM_
        ('fddc34', 0x4560, 'shll #0x1c,r3,r4', 0, ()),             # FORM_
        ('69c4', 0x4560, 'shlr #0x1c,r4', 0, ()),             # FORM_
        ('fd6034', 0x4560, 'shlr r3,r4', 0, ()),             # FORM_
        ('fd9c34', 0x4560, 'shlr #0x1c,r3,r4', 0, ()),             # FORM_
        ('7f8b', 0x4560, 'smovb', 0, ()),             # FORM_
        ('7f8f', 0x4560, 'smovf', 0, ()),             # FORM_
        ('7f87', 0x4560, 'smovu', 0, ()),             # FORM_
        ('7f8a', 0x4560, 'sstr.l', 0, ()),             # FORM_
        ('fd78f48017', 0x4560, 'stnz #0x1780,r4', 0, ()),             # FORM_
        ('fc4f34', 0x4560, 'stnz r3,r4', 0, ()),             # FORM_
        ('fd78e48017', 0x4560, 'stz #0x1780,r4', 0, ()),             # FORM_
        ('fc4b34', 0x4560, 'stz r3,r4', 0, ()),             # FORM_        FIXME: DOCS ARE WRONG! THIS IS THE SAME AS stnz
        ('6034', 0x4560, 'sub #0x3,r4', 0, ()),             # FORM_
        ('42348017', 0x4560, 'sub 0x1780[r3].ub,r4', 0, ()),             # FORM_
        ('0682348017', 0x4560, 'sub 0x5e00[r3].l,r4', 0, ()),             # FORM_
        ('ff0234', 0x4560, 'sub r3,r4,r2', 0, ()),             # FORM_
        ('7f82', 0x4560, 'suntil.l', 0, ()),             # FORM_
        ('7f86', 0x4560, 'swhile.l', 0, ()),             # FORM_
        ('fd78c38017', 0x4560, 'tst #0x1780,r3', 0, ()),             # FORM_
        ('fc32348017', 0x4560, 'tst 0x1780[r3].ub,r4', 0, ()),             # FORM_     should be: tst 0x1780[r3].ub,r4  - is: tst 0x1780[r3].b,r4
        ('06a20c348017', 0x4560, 'tst 0x5e00[r3].l,r4', 0, ()),             # FORM_
        ('fc56348017', 0x4560, 'utof 0x1780[r3].ub,r4', 0, ()),             # FORM_
        ('06a215348017', 0x4560, 'utof 0x5e00[r3].l,r4', 0, ()),             # FORM_
        ('7f96', 0x4560, 'wait', 0, ()),             # FORM_
        ('fc42348017', 0x4560, 'xchg 0x1780[r3].ub,r4', 0, ()),             # FORM_
        ('06a210348017', 0x4560, 'xchg 0x5e00[r3].l,r4', 0, ()),             # FORM_
        ('fd78d48017', 0x4560, 'xor #0x1780,r4', 0, ()),             # FORM_
        ('fc36348017', 0x4560, 'xor 0x1780[r3].ub,r4', 0, ()),             # FORM_
        ('06a20d348017', 0x4560, 'xor 0x5e00[r3].l,r4', 0, ()),             # FORM_

        ('f812ffffff47', 0x4560, 'mov.l #0x47ffffff,[r1]', 0, ()),
        ('f91601ff', 0x4560, 'mov.l #0xffffffff,0x4[r1]', 0, ()),
        ('f91e020000ff', 0x4560, 'mov.l #0xffff0000, 0x8[r1]', 0, ()),

]

class RXv2InstructionSet(unittest.TestCase):
    ''' main unit test with all tests to run '''
    def test_envi_rxv2_assorted_instrs(self):
        #setup initial work space for test
        vw = vivisect.VivWorkspace()
        vw.setMeta("Architecture", "rxv2")
        vw.addMemoryMap(0, 7, 'firmware', '\xff' * 16384*1024)
        vw.addMemoryMap(0x400000, 7, 'firmware', '\xff' * 16384*1024)
        #emu = vw.getEmulator()
        #emu.setMeta('forrealz', True)
        #emu._forrealz = True
        #emu.logread = emu.logwrite = True
        badcount = 0
        goodcount = 0
        goodemu = 0
        bademu = 0

        for bytez, va, reprOp, iflags, emutests in instrs:
            print("Test: %r" % bytez)
            op = vw.arch.archParseOpcode(binascii.unhexlify(bytez), 0, va)
            redoprepr = repr(op).replace(' ','').lower()
            redgoodop = reprOp.replace(' ','').lower()

            bytezlen = len(bytez) // 2 # hex encoded
            oplen = len(op)

            if oplen != bytezlen:
                print("Length mismatch: %r: %r  (decoded: %r, test: %r)" % (bytez, op, oplen, bytezlen))

            if redoprepr != redgoodop:
                badcount += 1
                raise Exception("%d FAILED to decode instr:  %.8x %s - should be: %s  - is: %s" % \
                        (goodcount, va, bytez, reprOp, repr(op) ) )
                self.assertEqual((goodcount, bytez, redoprepr), (goodcount, bytez, redgoodop))

            else:
                goodcount += 1


            # NO EMUTESTS YET
            continue

            if not len(emutests):
                try:
                    # if we don't have special tests, let's just run it in the emulator anyway and see if things break
                    if not self.validateEmulation(emu, op, (), ()):
                        goodemu += 1
                    else:
                        bademu += 1
                except envi.UnsupportedInstruction:
                    bademu += 1
                except Exception as exp:
                    logger.exception("Exception in Emulator for command - %r  %r  %r\n  %r", repr(op), bytez, reprOp, exp)
                    bademu += 1
            else:
                # if we have a special test lets run it
                for tidx, sCase in enumerate(emutests):
                    #allows us to just have a result to check if no setup needed
                    if 'tests' in sCase:
                        setters = ()
                        if 'setup' in sCase:
                            setters = sCase['setup']
                        tests = sCase['tests']
                        if not self.validateEmulation(emu, op, (setters), (tests), tidx):
                            goodcount += 1
                            goodemu += 1
                        else:
                            bademu += 1
                            raise Exception( "FAILED emulation (special case): %.8x %s - %s" % (va, bytez, op) )

                    else:
                        bademu += 1
                        raise Exception( "FAILED special case test format bad:  Instruction test does not have a 'tests' field: %.8x %s - %s" % (va, bytez, op))

        logger.info("Done with assorted instructions test.  DISASM: %s tests passed.  %s tests failed.  EMU: %s tests passed.  %s tests failed" % \
                (goodcount, badcount, goodemu, bademu))
        logger.info("Total of %d tests completed." % (goodcount + badcount))
        self.assertEqual(goodcount, GOOD_TESTS)
        #self.assertEqual(goodemu, GOOD_EMU_TESTS)

