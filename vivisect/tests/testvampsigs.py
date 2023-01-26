import unittest

import vivisect
import envi.memory as e_mem


class VampSigTests(unittest.TestCase):
    '''
    Tests to verify detection of signatures for special functions in PE files.
    If a signature is detected during makeFunc(), it should mark the
    function as a thunk and name it according to the signature.
    '''

    def run_test(self, opcode_string):
        # Create a Vivisect workspace, architecture does not matter.
        vw = vivisect.VivWorkspace()
        vw.setMeta('Architecture', 'i386')
        vw.setMeta('Platform', 'windows')
        vw.setMeta('Format', 'pe')

        # Add the module that detects signatures.
        vw.addFuncAnalysisModule("vivisect.analysis.ms.msvc")

        # Put the opcodes into an executable memory map.
        mapbase = 0x400000
        bufferpgsz = 2 * 4096
        vw.addMemoryMap(mapbase - bufferpgsz, e_mem.MM_RWX,
                        'test', '@' * bufferpgsz)
        bytez = bytes(bytearray.fromhex(opcode_string))
        vw.addMemoryMap(mapbase, e_mem.MM_RWX, 'test', bytez)
        vw.addSegment(mapbase, len(bytez), 'test_code_%x' % mapbase, 'test')

        # Make a function, triggering signature detection.
        fva = mapbase
        vw.makeFunction(fva)
        return vw.getFunctionMeta(fva, 'Thunk')


    def test_sig_behavior(self):
        '''
        Test the behavior of signature detection.
        '''
        # True signature.
        opcodes = '680000000064a10000000050'
        self.assertEqual(self.run_test(opcodes), 'ntdll.seh3_prolog')

        # Incorrect signature.
        opcodes = '680000000064a100000000aa'
        self.assertEqual(self.run_test(opcodes), None)

        # Signature with masked out bytes changed.
        opcodes = '68aaaaaaaa64a10000000050'
        self.assertEqual(self.run_test(opcodes), 'ntdll.seh3_prolog')

        # Signature with extra opcodes.
        opcodes = '680000000064a100000000504141414141'
        self.assertEqual(self.run_test(opcodes), 'ntdll.seh3_prolog')

        # Signature with opcodes before.
        opcodes = '4141680000000064a10000000050'
        self.assertEqual(self.run_test(opcodes), None)


    def test_seh_sigs(self):
        '''
        Test detection of seh prolog and epilog signatures.
        '''
        opcodes = '680000000064a10000000050'
        self.assertEqual(self.run_test(opcodes), 'ntdll.seh3_prolog')

        opcodes = '8b4df064890d00000000595f5e5bc951c3'
        self.assertEqual(self.run_test(opcodes), 'ntdll.seh3_epilog')

        opcodes = '680000000064ff35000000008b442410'
        self.assertEqual(self.run_test(opcodes), 'ntdll.seh4_prolog')

        opcodes = '8b4df064890d00000000595f5f5e5b8be55d51c3'
        self.assertEqual(self.run_test(opcodes), 'ntdll.seh4_epilog')

        opcodes = '8b4df064890d00000000595f5f5e5b8be55d51f2c3'
        self.assertEqual(self.run_test(opcodes), 'ntdll.seh4_epilog')

        opcodes = 'a10000000033c58945fc'
        self.assertEqual(self.run_test(opcodes), 'ntdll.gs_prolog')


    def test_alloca_probe_sigs(self):
        '''
        Test detection of alloca_probe signatures.
        '''
        opcodes = '513d001000008d4c2408721481e9001000002d0010000085013d0010000073ec2bc88bc485018be18b088b400450c3'
        self.assertEqual(self.run_test(opcodes), 'ntdll._alloca_probe')

        opcodes = '518d4c24042bc81bc0f7d023c88bc42500f0ffff3bc8720a8bc159948b00890424c32d001000008500ebe9'
        self.assertEqual(self.run_test(opcodes), 'ntdll._alloca_probe')

        opcodes = '518d4c24042bc81bc0f7d023c88bc42500f0ffff3bc8f2720b8bc159948b00890424f2c32d001000008500ebe7'
        self.assertEqual(self.run_test(opcodes), 'ntdll._alloca_probe')

        opcodes = '4883ec104c8914244c895c24084d33db4c8d5424184c2bd04d0f42d3654c8b1c25100000004d3bd37316664181e200f04d8d9b00f0ffff41c603004d3bd375f04c8b14244c8b5c24084883c410c3'
        self.assertEqual(self.run_test(opcodes), 'ntdll._alloca_probe')

        opcodes = '4883ec104c8914244c895c24084d33db4c8d5424184c2bd04d0f42d3654c8b1c25100000004d3bd3f27317664181e200f04d8d9b00f0ffff41c603004d3bd3f275ef4c8b14244c8b5c24084883c410f2c3'
        self.assertEqual(self.run_test(opcodes), 'ntdll._alloca_probe')


    def test_security_cookie_sigs(self):
        '''
        Test detection of security_check_cookie signatures.
        '''
        opcodes = '3b0d000000007502f3c3e9'
        self.assertEqual(self.run_test(opcodes), 'ntdll.security_check_cookie')

        opcodes = '3b0d00000000f27502f2c3f2e9'
        self.assertEqual(self.run_test(opcodes), 'ntdll.security_check_cookie')

        opcodes = '483b0d00000000751148c1c11066f7c1ffff7502f3c348c1c910e9'
        self.assertEqual(self.run_test(opcodes), 'ntdll.security_check_cookie_64')

        opcodes = '483b0d00000000f2751148c1c11066f7c1fffff27502f2c348c1c910e9'
        self.assertEqual(self.run_test(opcodes), 'ntdll.security_check_cookie_64')

        opcodes = '483b0d00000000f2751248c1c11066f7c1fffff27502f2c348c1c910e9'
        self.assertEqual(self.run_test(opcodes), 'ntdll.security_check_cookie_64')


    def test_gs_failure_sigs(self):
        '''
        Test detection of gs_failure signatures.
        '''
        opcodes = '3b0d000000007502f3c3e9'
        self.assertEqual(self.run_test(opcodes), 'ntdll.security_check_cookie')
        opcodes = '8bff558bec5151a300000000890d00000000891500000000891d00000000893500000000893d000000008c15000000008c0d000000008c1d000000008c05000000008c25000000008c2d000000009c'
        self.assertEqual(self.run_test(opcodes), 'ntdll.report_gsfailure')

        opcodes = '8bff558bec81ec28030000a300000000890d00000000891500000000891d00000000893500000000893d00000000668c1500000000668c0d00000000668c1d00000000668c0500000000668c2500000000668c2d000000009c'
        self.assertEqual(self.run_test(opcodes), 'ntdll.report_gsfailure')
