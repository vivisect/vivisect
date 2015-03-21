import unittest

import vivisect.hal.cpu as v_cpu
import vivisect.hal.registers as v_regs

rax = 0x4141414156564242
rbx = 0x3030303080808080
amd64 = v_cpu.getArchCpu('amd64')

class RegisterTest(unittest.TestCase):

    def getregs(self):
        return amd64._init_regs()

    def test_getreg(self):
        regs = self.getregs()
        regs['rax'] = rax
        self.assertEqual( regs.rax, rax )
        self.assertEqual( regs['rax'], rax )
        self.assertEqual( regs.get('rax'), rax )

    def test_getreg_meta(self):
        regs = self.getregs()
        regs['rax'] = rax

        self.assertEqual( regs.ax, rax & 0xffff)
        self.assertEqual( regs['ax'], rax & 0xffff)
        self.assertEqual( regs.get('ax'), rax & 0xffff)

        self.assertEqual( regs.eax, rax & 0xffffffff)
        self.assertEqual( regs['eax'], rax & 0xffffffff)
        self.assertEqual( regs.get('eax'), rax & 0xffffffff)

    def test_getreg_alias(self):
        regs = self.getregs()
        regs['rip'] = 0x41414141
        regs['rsp'] = 0x42424242
        self.assertEqual( regs.rip, regs.getpc() )
        self.assertEqual( regs.rsp, regs.getsp() )

    def test_setreg(self):
        regs = self.getregs()
        regs['rbx'] = rbx
        self.assertEqual( regs.rbx, rbx )

    def test_setreg_meta(self):
        regs = self.getregs()
        regs['rax'] = 0x4141414141414141
        regs['eax'] = 0x42424242
        regs['ax'] = 0x4343
        self.assertEqual( regs.ax, 0x4343 )
        self.assertEqual( regs.eax, 0x42424343 )
        self.assertEqual( regs.rax, 0x4141414142424343 )

    def test_setreg_alias(self):
        regs = self.getregs()

    def test_regs_save(self):
        regs = self.getregs()
        regs['rax'] = rax
        self.assertEqual( regs.save().get('rax'), rax )

    def test_regs_load(self):
        regs = self.getregs()
        regs.load({'rax':rax,'rbx':rbx})
        self.assertEqual( regs.rax, rax )
        self.assertEqual( regs.rbx, rbx )

    def test_regs_oncache(self):

        def oncache():
            return {'rax':0x41414141}

        regs = self.getregs()
        self.assertEqual( regs.rax, 0 )

        regs.oncache( oncache )
        self.assertEqual( regs.rax, 0x41414141 )
