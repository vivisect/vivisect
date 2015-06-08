import unittest

import vivisect.hal.cpu as v_cpu

from vivisect.lib.bits import *
from vertex.lib.common import tufo

class i386Test(unittest.TestCase):

    def _run_gp_regtest(self, cpu, name):
        cpu[name] = 0x41424344

        regx = '%sx' % (name[1],)
        regh = '%sh' % (name[1],)
        regl = '%sl' % (name[1],)

        self.assertEqual( cpu[regh], 0x43 )
        self.assertEqual( cpu[regl], 0x44 )
        self.assertEqual( cpu[regx], 0x4344 )
        self.assertEqual( cpu[name], 0x41424344 )

        cpu[regh] = 0x56
        self.assertEqual( cpu[name], 0x41425644 )
        cpu[regl] = 0x57
        self.assertEqual( cpu[name], 0x41425657 )

    def test_i386_regs_basic(self):
        cpu = v_cpu.getArchCpu('i386')
        self._run_gp_regtest(cpu,'eax')
        self._run_gp_regtest(cpu,'ebx')
        self._run_gp_regtest(cpu,'ecx')
        self._run_gp_regtest(cpu,'edx')

    def test_i386_regs_alias(self):
        cpu = v_cpu.getArchCpu('i386')
        cpu['eip'] = 0x41424344
        cpu['esp'] = 0x44434241
        self.assertEqual( cpu.getpc(), 0x41424344 )
        self.assertEqual( cpu.getsp(), 0x44434241 )

    def _get_inst(self, hexstr):
        b = h2b(hexstr)
        cpu = v_cpu.getArchCpu('i386')
        cpu.initMemoryMap(0x41410000, 4096, init=b)
        return cpu,cpu.disasm(0x41410000)

    def _test_inst(self, hexstr, mnem, **info):
        cpu,inst = self._get_inst(hexstr)
        if inst == None:
            raise Exception('no instr: %s' % (hexstr,))

        self.assertEqual( mnem, inst.inst[0] )

        r = info.pop('repr',None)
        if r != None:
            i = str(inst)
            self.assertEqual(i,r)

        for prop,valu in info.items():
            self.assertEqual( inst.inst[2].get(prop), valu )

        return cpu,inst

    def test_i386_decode_66(self):
        cpu,inst = self._test_inst('6640','inc',prefixes=[0x66])
        #print('TYPE: %s' % (type(inst[1][0]),))
        #print('INST: %r' % (inst,))

    def test_i386_instr(self):
        cpu = v_cpu.getArchCpu('i386')
        cpu.initMemoryMap(0x41410000, 4096, init=h2b('40'))
        inst = cpu.disasm(0x41410000)

    #def test_i386_aas(self):
        #cpu,inst = self._test_inst('3f','adc')

    def test_i386_adc(self):
        # reg1->reg2
        cpu,inst = self._test_inst('10d8','adc', repr='adc al,bl',size=2)
        cpu,inst = self._test_inst('11d8','adc', repr='adc eax,ebx',size=2)
        # reg2->reg1
        cpu,inst = self._test_inst('12d8','adc', repr='adc bl,al',size=2)
        cpu,inst = self._test_inst('13d8','adc', repr='adc ebx,eax',size=2)
        # imm->eax ( and imm->al, imm->ax )
        cpu,inst = self._test_inst('1442565656','adc', repr='adc al,66',size=2)
        cpu,inst = self._test_inst('1542424343','adc', repr='adc eax,0x43434242',size=5)
        cpu,inst = self._test_inst('661542424343','adc', repr='adc ax,0x4242',size=4)

        #cpu,inst = self._test_inst('81505641424344','adc', repr='woot',size=4)
        cpu,inst = self._test_inst('6681d141424344','adc',repr='adc cx,0x4241',size=5)

    def test_i386_add(self):
        cpu,inst = self._test_inst('01d8','add',repr='add eax,ebx',size=2)
        cpu,inst = self._test_inst('834201020304','add', repr='add [(edx + 1):4],2',size=4)
        cpu,inst = self._test_inst('04010203','add', repr='add al,1',size=2)

    def test_i386_arpl(self):
        cpu,inst = self._test_inst('63d8','arpl',repr='arpl ax,bx',size=2)

    def test_i386_bound(self):
        cpu,inst = self._test_inst('6201','bound',repr='bound eax,[ecx:4]',size=2)

    def test_i386_bsf(self):
        cpu,inst = self._test_inst('0fbcca','bsf',repr='bsf ecx,edx', size=3)

    def test_i386_bsr(self):
        cpu,inst = self._test_inst('0fbdca','bsr',repr='bsr ecx,edx', size=3)

    def test_i386_bswap(self):
        cpu,inst = self._test_inst('0fc9','bswap',repr='bswap ecx', size=2)
        cpu,inst = self._test_inst('660fc9','bswap',repr='bswap cx', size=3)

    def test_i386_bt(self):
        cpu,inst = self._test_inst('0fbae101','bt',repr='bt ecx,1',size=4)
        cpu,inst = self._test_inst('0fa3d8','bt',repr='bt eax,ebx',size=3)

    def test_i386_call(self):
        cpu,inst = self._test_inst('e800000000','call',repr='call 0x41410005',size=5)
        cpu,inst = self._test_inst('ffd1','call',repr='call ecx',size=2)
        cpu,inst = self._test_inst('ff5101','call',repr='call [(ecx + 1):4]',size=3)
        cpu,inst = self._test_inst('ff9101020304','call',repr='call [(ecx + 0x4030201):4]',size=6)

    def test_i386_cbw(self):
        cpu,inst = self._test_inst('98','cbw',repr='cbw',size=1)

    def test_i386_cdq(self):
        cpu,inst = self._test_inst('99','cdq',repr='cdq',size=1)

    def test_i386_clc(self):
        cpu,inst = self._test_inst('f8','clc',repr='clc',size=1)

    def test_i386_cld(self):
        cpu,inst = self._test_inst('fc','cld',repr='cld',size=1)

    def test_i386_cli(self):
        cpu,inst = self._test_inst('fa','cli',repr='cli',size=1)

    def test_i386_clts(self):
        cpu,inst = self._test_inst('0f06','clts',repr='clts',size=2)

    def test_i386_cmc(self):
        cpu,inst = self._test_inst('f5','cmc',repr='cmc',size=1)

    def test_i386_cmp(self):
        cpu,inst = self._test_inst('38d8','cmp',repr='cmp al,bl',size=2)
        cpu,inst = self._test_inst('39d8','cmp',repr='cmp eax,ebx',size=2)
        cpu,inst = self._test_inst('6639d8','cmp',repr='cmp ax,bx',size=3)

    def test_i386_modrm(self):
        cpu,inst = self._test_inst('104041','adc',repr='adc [(eax + 65):1],al',size=3)
        cpu,inst = self._test_inst('134041','adc',repr='adc eax,[(eax + 65):4]',size=3)
        cpu,inst = self._test_inst('138041414141','adc',repr='adc eax,[(eax + 0x41414141):4]',size=6)

    def test_i386_regimm(self):
        cpu,inst = self._test_inst('83d186','adc',repr='adc ecx,0xffffff86',size=3)
        cpu,inst = self._test_inst('80d186','adc',repr='adc cl,134',size=3)
        cpu,inst = self._test_inst('81d141414141','adc',repr='adc ecx,0x41414141',size=6)

    def test_i386_regimm_inval(self):
        self.assertIsNone( self._get_inst('82d141414141')[1] )
