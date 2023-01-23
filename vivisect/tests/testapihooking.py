import unittest

import envi.archs.amd64 as e_amd64
import envi.archs.i386 as e_i386

import vivisect.tests.helpers as helpers
import vivisect.tests.utils as v_t_utils


class ApiHookingTests(v_t_utils.VivTest):
    '''
    Tests to verify API hooking during emulation.
    '''

    @classmethod
    def setUpClass(cls):
        cls.hello_i386_vw = helpers.getTestWorkspace('windows', 'i386',
                                                     'helloworld.exe')
        cls.hello_amd64_vw = helpers.getTestWorkspace('windows', 'amd64',
                                                      'helloworld.exe')


    def test_alloca_i386(self):
        '''
        alloca_probe() is compiled statically in the test sample.
        Verify it is detected and emulated correctly.
        '''
        alloca_fnva = 0x407690
        test_fnva = 0x4059f3

        # Verify alloca_probe is detected by a signature.
        # (For this sample, the signature for the MSVC 2010 compiler.)
        alloca_api = self.hello_i386_vw.getFunctionApi(alloca_fnva)
        assert alloca_api[3] == 'ntdll._alloca_probe'

        # The test function starts with these instructions:
        #     mov edi, edi
        #     push ebp
        #     mov ebp, esp
        #     mov eax, 0x1ae4
        #     call _alloca_probe
        # Step an emulator to the alloca_probe call.
        emu = self.hello_i386_vw.getEmulator()
        emu.setProgramCounter(test_fnva)
        for i in range(4):
            emu.stepi()
        ip = emu.getProgramCounter()
        opcode = emu.parseOpcode(ip)
        assert repr(opcode) == "call 0x{0:08x}".format(alloca_fnva)

        esp_before = emu.getRegister(e_i386.REG_ESP)
        eax_before = emu.getRegister(e_i386.REG_EAX)

        # Step over the call and verify ESP and EAX.
        emu.stepi()
        ip = emu.getProgramCounter()
        esp_after = emu.getRegister(e_i386.REG_ESP)
        eax_after = emu.getRegister(e_i386.REG_EAX)
        assert eax_after == ip
        assert esp_after == esp_before - eax_before


    def test_alloca_amd64(self):
        '''
        alloca_probe() is compiled statically in the test sample.
        Verify it is detected and emulated correctly.
        '''
        alloca_fnva = 0x1400081c0
        test_fnva = 0x140006360

        # Verify alloca_probe is detected by a signature.
        # (For this sample, the signature for the MSVC 2010 compiler.)
        alloca_api = self.hello_amd64_vw.getFunctionApi(alloca_fnva)
        assert alloca_api[3] == 'ntdll._alloca_probe'

        # The test function starts with these instructions:
        #     mov [rsp-8+arg_18], rbx
        #     push rbp
        #     push other registers...
        #     mov eax, 0x1b30
        #     call _alloca_probe
        #     sub rsp, rax
        # Step an emulator to the alloca_probe call.
        emu = self.hello_amd64_vw.getEmulator()
        emu.setProgramCounter(test_fnva)
        for i in range(10):
            emu.stepi()
        ip = emu.getProgramCounter()
        opcode = emu.parseOpcode(ip)
        assert repr(opcode) == "call 0x{0:08x}".format(alloca_fnva)

        rsp_before = emu.getRegister(e_amd64.REG_RSP)
        rax_before = emu.getRegister(e_amd64.REG_RAX)

        # Step over the call and verify RSP and RAX are unchanged.
        emu.stepi()
        rsp_after = emu.getRegister(e_amd64.REG_RSP)
        assert rsp_after == rsp_before

        # Step one more and verify the stack was decremented (not due to
        # API hooking, but it is another test of emulation).
        emu.stepi()
        rsp_after = emu.getRegister(e_amd64.REG_RSP)
        assert rsp_after == rsp_before - rax_before


    def test_getprocaddr_i386(self):
        '''
        Test sample calls getProcAddress() to dynamically load import functions.
        Verify a taint is created for the function.
        '''
        test_fnva = 0x40262f

        # The test function starts with these instructions:
        #     mov edi, edi
        #     ...
        #     call ds:GetModuleHandleW
        #     ...
        #     call ds:GetProcAddress
        # Step an emulator past the GetProcAddress call.
        emu = self.hello_i386_vw.getEmulator()
        emu.setProgramCounter(test_fnva)
        for i in range(10):
            emu.stepi()

        # Verify an appropriate taint was created.
        for tval in emu.taints.values():
            taint_va, taint_type, taint_info = tval
            if taint_type == 'dynfunc':
                assert taint_info == (u'mscoree', u'CorExitProcess')
                return
        assert False, 'No dynlib taint found'


    def test_getprocaddr_amd64(self):
        '''
        Test sample calls getProcAddress() to dynamically load import functions.
        Verify a taint is created for the function.
        '''
        test_fnva = 0x140002720

        # The test function starts with these instructions:
        #     push rbx
        #     ...
        #     call cs:GetModuleHandleW
        #     ...
        #     call cs:GetProcAddress
        # Step an emulator past the GetProcAddress call.
        emu = self.hello_amd64_vw.getEmulator()
        emu.setProgramCounter(test_fnva)
        for i in range(10):
            emu.stepi()

        # Verify an appropriate taint was created.
        for tval in emu.taints.values():
            taint_va, taint_type, taint_info = tval
            if taint_type == 'dynfunc':
                assert taint_info == (u'mscoree', u'CorExitProcess')
                return
        assert False, 'No dynlib taint found'
