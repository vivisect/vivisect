import logging
import unittest

import PE
import envi.memory as e_memory

import vivisect
import vivisect.const as viv_con
import vivisect.tests.helpers as helpers

logger = logging.getLogger(__name__)


class PETests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(PETests, cls).setUpClass()
        cls.psexec_fn = helpers.getTestPath('windows', 'i386', 'PsExec.exe')

        cls.vw_psexec = helpers.getTestWorkspace('windows', 'i386', 'PsExec.exe')
        cls.vw_sphinx = helpers.getTestWorkspace('windows', 'i386', 'sphinx_livepretend.exe')

        cls.vw_mimi = vivisect.VivWorkspace()
        mimi_fn = helpers.getTestPath('windows', 'i386', 'mimikatz.exe_')
        cls.vw_mimi.loadFromFile(mimi_fn)

    def test_function_disasm(self):
        disasm = [
            (0x4028e0, 1, 'push ebp'),
            (0x4028e1, 2, 'mov ebp,esp'),
            (0x4028e3, 3, 'sub esp,8'),
            (0x4028e6, 1, 'push esi'),
            (0x4028e7, 3, 'mov esi,dword [ebp + 8]'),
            (0x4028ea, 1, 'push edi'),
            (0x4028eb, 2, 'push 64'),
            (0x4028ed, 1, 'push esi'),
            (0x4028ee, 6, 'call dword [0x0041a168]'),
            (0x4028f4, 5, 'push 0x00420944'),
            (0x4028f9, 5, 'push 0x0042095c'),
            (0x4028fe, 6, 'call dword [0x0041a178]'),
            (0x402904, 1, 'push eax'),
            (0x402905, 6, 'call dword [0x0041a18c]'),
            (0x40290b, 2, 'mov edi,eax'),
            (0x40290d, 2, 'test edi,edi'),
            (0x40290f, 2, 'jz 0x00402935'),
        ]

        cbva = 0x4028e0
        self.assertEqual(self.vw_psexec.getFunction(cbva), cbva)
        for (va, size, inst) in disasm:
            lva, lsize, ltype, linfo = self.vw_psexec.getLocation(cbva)
            op = self.vw_psexec.parseOpcode(lva)
            self.assertEqual(ltype, viv_con.LOC_OP)
            self.assertEqual(size, lsize)
            self.assertEqual(str(op), inst)
            cbva += size

    def test_export_by_name(self):
        file_path = helpers.getTestPath('windows', 'i386', 'export_by_name.dll')
        pe = PE.peFromFileName(file_path)
        export_list = pe.getExports()
        self.assertEqual(len(export_list), 2, "expecting 2 exported functions")
        self.assertEqual(export_list[0][1], 0, "exported function with ordinal 0 not found")
        self.assertEqual(export_list[0][2], "Func1", "exported function with name 'Func1' not found")
        self.assertEqual(export_list[1][1], 1, "exported function with ordinal 1 not found")
        self.assertEqual(export_list[1][2], "Func2", "exported function with name 'Func2' not found")

    def test_export_by_ordinal_base_01(self):
        file_path = helpers.getTestPath('windows', 'i386', 'export_by_ordinal_base_01.dll')
        pe = PE.peFromFileName(file_path)
        export_list = pe.getExports()
        self.assertEqual(len(export_list), 2, "expecting 2 exported functions")
        self.assertEqual(export_list[0][1], 1, "exported function with ordinal 1 not found")
        self.assertEqual(export_list[1][1], 2, "exported function with ordinal 2 not found")

    def test_export_by_ordinal_base_45(self):
        file_path = helpers.getTestPath('windows', 'i386', 'export_by_ordinal_base_45.dll')
        pe = PE.peFromFileName(file_path)
        export_list = pe.getExports()
        self.assertEqual(len(export_list), 2, "expecting 2 exported functions")
        self.assertEqual(export_list[0][1], 45, "exported function with ordinal 45 not found")
        self.assertEqual(export_list[1][1], 55, "exported function with ordinal 55 not found")

    def test_pe_metainfo(self):
        self.assertEqual(self.vw_psexec.getMeta('Architecture'), 'i386')
        self.assertEqual(self.vw_psexec.getMeta('DefaultCall'), 'cdecl')
        self.assertEqual(self.vw_psexec.getMeta('Format'), 'pe')
        self.assertEqual(self.vw_psexec.getMeta('Platform'), 'windows')
        self.assertEqual(self.vw_psexec.getMeta('StorageModule'), 'vivisect.storage.basicfile')
        self.assertEqual(self.vw_psexec.getMeta('StorageName'), self.psexec_fn + '.viv')

        self.assertEqual(len(self.vw_psexec.getMeta('NoReturnApis')), 5)
        self.assertTrue(self.vw_psexec.metadata['NoReturnApis']['kernel32.exitprocess'])
        self.assertTrue(self.vw_psexec.metadata['NoReturnApis']['kernel32.exitthread'])
        self.assertTrue(self.vw_psexec.metadata['NoReturnApis']['kernel32.fatalexit'])
        self.assertTrue(self.vw_psexec.metadata['NoReturnApis']['ntdll.rtlexituserthread'])
        self.assertTrue(self.vw_psexec.metadata['NoReturnApis']['ntoskrnl.kebugcheckex'])

        noret = [
            0x41a1c0,  # ExitProcess
            0x412380,  # calls 0x407027
            0x409143,  # legit no return
            0x40ba2b,  # ends in int3 only
            0x407027,  # calls 0x4070e5 and then in3
            0x412389,  # every path ends in int3
            0x40ba07,  # ends in call to 0x412389 and int3
            0x4018d0,  # ends in call to 0x4072ca and int3
            0x407011,  # Ends in a call to ExitProcess
            0x409be3,  # Calls Exit thread, but also ends in a call to 0x409b77 followed by cccccccc bytes
            0x41a1f4,  # Actual ExitThread import
            0x409bb8,  # Ends in a call to ExitThread and then int3
            0x4090bd,  # Ends in a call to ExitThread and then int3
            0x409dbf,  # Ends in a call to 0x407011
        ]
        meta = self.vw_psexec.getMeta('NoReturnApisVa')
        for nva in noret:
            self.assertTrue(nva in meta, msg='0x%.8x is not a no return va!' % nva)
        self.assertTrue(self.vw_psexec.metadata['NoReturnApisVa'][4301248])
        self.assertTrue(self.vw_psexec.metadata['NoReturnApisVa'][4301300])

    def test_pe_filemeta(self):
        vw = self.vw_psexec
        files = vw.getFiles()
        self.assertTrue('psexec' in files)
        self.assertEqual('27304b246c7d5b4e149124d5f93c5b01', vw.getFileMeta('psexec', 'md5sum'))
        self.assertEqual('3337E3875B05E0BFBA69AB926532E3F179E8CFBF162EBB60CE58A0281437A7EF',
                         vw.getFileMeta('psexec', 'sha256'))
        self.assertEqual('2.2', vw.getFileMeta('psexec', 'Version'))
        self.assertEqual(0x400000, vw.getFileMeta('psexec', 'imagebase'))
        self.assertTrue(vw.getFileMeta('psexec', 'SafeSEH'))

    def test_delay_imports(self):
        vw = self.vw_psexec
        delays = sorted(vw.getVaSetRows('DelayImports'))
        ans = [
            (0x42b2ec, 'gdi32.EndPage'),
            (0x42b2f0, 'gdi32.EndDoc'),
            (0x42b2f4, 'gdi32.StartDocW'),
            (0x42b2f8, 'gdi32.SetMapMode'),
            (0x42b2fc, 'gdi32.GetDeviceCaps'),
            (0x42b300, 'gdi32.StartPage'),
            (0x42b308, 'user32.GetSysColorBrush'),
            (0x42b30c, 'user32.SetCursor'),
            (0x42b310, 'user32.LoadCursorW'),
            (0x42b314, 'user32.LoadStringW'),
            (0x42b318, 'user32.SetWindowTextW'),
            (0x42b31c, 'user32.GetDlgItem'),
            (0x42b320, 'user32.EndDialog'),
            (0x42b324, 'user32.DialogBoxIndirectParamW'),
            (0x42b328, 'user32.InflateRect'),
            (0x42b32c, 'user32.SendMessageW'),
        ]
        self.assertEqual(delays, ans)

    def test_imports(self):
        vw = self.vw_psexec
        imps = vw.getImports()
        ans = [(4301428, 4, 9, 'version.GetFileVersionInfoSizeW'), (4301432, 4, 9, 'version.GetFileVersionInfoW'),
               (4301436, 4, 9, 'version.VerQueryValueW'), (4301416, 4, 9, 'netapi32.NetServerEnum'),
               (4301420, 4, 9, 'netapi32.NetApiBufferFree'), (4301444, 4, 9, 'ws2_32.gethostname'),
               (4301448, 4, 9, 'ws2_32.WSAStartup'), (4301452, 4, 9, 'ws2_32.inet_ntoa'),
               (4301456, 4, 9, 'ws2_32.gethostbyname'), (4301404, 4, 9, 'mpr.WNetCancelConnection2W'),
               (4301408, 4, 9, 'mpr.WNetAddConnection2W'), (4300984, 4, 9, 'kernel32.GetExitCodeProcess'),
               (4300988, 4, 9, 'kernel32.ResumeThread'), (4300992, 4, 9, 'kernel32.WaitForMultipleObjects'),
               (4300996, 4, 9, 'kernel32.GetFileTime'), (4301000, 4, 9, 'kernel32.DuplicateHandle'),
               (4301004, 4, 9, 'kernel32.DisconnectNamedPipe'), (4301008, 4, 9, 'kernel32.SetNamedPipeHandleState'),
               (4301012, 4, 9, 'kernel32.TransactNamedPipe'), (4301016, 4, 9, 'kernel32.CreateEventW'),
               (4301020, 4, 9, 'kernel32.GetCurrentProcessId'), (4301024, 4, 9, 'kernel32.GetFullPathNameW'),
               (4301028, 4, 9, 'kernel32.SetFileAttributesW'), (4301032, 4, 9, 'kernel32.GetFileAttributesW'),
               (4301036, 4, 9, 'kernel32.CopyFileW'), (4301040, 4, 9, 'kernel32.WaitNamedPipeW'),
               (4301044, 4, 9, 'kernel32.SetConsoleCtrlHandler'), (4301048, 4, 9, 'kernel32.SetConsoleTitleW'),
               (4301052, 4, 9, 'kernel32.ReadConsoleW'), (4301056, 4, 9, 'kernel32.GetVersion'),
               (4301060, 4, 9, 'kernel32.SetProcessAffinityMask'), (4301064, 4, 9, 'kernel32.ReadFile'),
               (4301068, 4, 9, 'kernel32.GetConsoleScreenBufferInfo'), (4301072, 4, 9, 'kernel32.MultiByteToWideChar'),
               (4301076, 4, 9, 'kernel32.GetComputerNameW'), (4301080, 4, 9, 'kernel32.DeleteFileW'),
               (4301084, 4, 9, 'kernel32.CreateFileW'), (4301088, 4, 9, 'kernel32.GetSystemDirectoryW'),
               (4301092, 4, 9, 'kernel32.FindResourceW'), (4301096, 4, 9, 'kernel32.LoadLibraryExW'),
               (4301100, 4, 9, 'kernel32.FormatMessageA'), (4301104, 4, 9, 'kernel32.GetTickCount'),
               (4301108, 4, 9, 'kernel32.CloseHandle'), (4301112, 4, 9, 'kernel32.WriteFile'),
               (4301116, 4, 9, 'kernel32.SizeofResource'), (4301120, 4, 9, 'kernel32.LoadResource'),
               (4301124, 4, 9, 'kernel32.Sleep'), (4301128, 4, 9, 'kernel32.WaitForSingleObject'),
               (4301132, 4, 9, 'kernel32.SetEndOfFile'), (4301136, 4, 9, 'kernel32.SetEvent'),
               (4301140, 4, 9, 'kernel32.SetLastError'), (4301144, 4, 9, 'kernel32.GetLastError'),
               (4301148, 4, 9, 'kernel32.GetCurrentProcess'), (4301152, 4, 9, 'kernel32.FreeLibrary'),
               (4301156, 4, 9, 'kernel32.LockResource'), (4301160, 4, 9, 'kernel32.SetPriorityClass'),
               (4301164, 4, 9, 'kernel32.GetModuleFileNameW'), (4301168, 4, 9, 'kernel32.GetCommandLineW'),
               (4301172, 4, 9, 'kernel32.GetModuleHandleW'), (4301176, 4, 9, 'kernel32.LoadLibraryW'),
               (4301180, 4, 9, 'kernel32.GetStdHandle'), (4301184, 4, 9, 'kernel32.GetFileType'),
               (4301188, 4, 9, 'kernel32.LocalFree'), (4301192, 4, 9, 'kernel32.LocalAlloc'),
               (4301196, 4, 9, 'kernel32.GetProcAddress'), (4301200, 4, 9, 'kernel32.FreeEnvironmentStringsW'),
               (4301204, 4, 9, 'kernel32.LCMapStringW'), (4301208, 4, 9, 'kernel32.OutputDebugStringW'),
               (4301212, 4, 9, 'kernel32.HeapSize'), (4301216, 4, 9, 'kernel32.HeapReAlloc'),
               (4301220, 4, 9, 'kernel32.SetFilePointerEx'), (4301224, 4, 9, 'kernel32.WriteConsoleW'),
               (4301228, 4, 9, 'kernel32.GetEnvironmentVariableW'), (4301232, 4, 9, 'kernel32.RaiseException'),
               (4301236, 4, 9, 'kernel32.LoadLibraryExA'), (4301240, 4, 9, 'kernel32.EncodePointer'),
               (4301244, 4, 9, 'kernel32.DecodePointer'), (4301248, 4, 9, 'kernel32.ExitProcess'),
               (4301252, 4, 9, 'kernel32.GetModuleHandleExW'), (4301256, 4, 9, 'kernel32.WideCharToMultiByte'),
               (4301260, 4, 9, 'kernel32.HeapFree'), (4301264, 4, 9, 'kernel32.HeapAlloc'),
               (4301268, 4, 9, 'kernel32.GetConsoleMode'), (4301272, 4, 9, 'kernel32.ReadConsoleInputA'),
               (4301276, 4, 9, 'kernel32.SetConsoleMode'), (4301280, 4, 9, 'kernel32.EnterCriticalSection'),
               (4301284, 4, 9, 'kernel32.LeaveCriticalSection'), (4301288, 4, 9, 'kernel32.SetStdHandle'),
               (4301292, 4, 9, 'kernel32.CreateThread'), (4301296, 4, 9, 'kernel32.GetCurrentThreadId'),
               (4301300, 4, 9, 'kernel32.ExitThread'), (4301304, 4, 9, 'kernel32.IsDebuggerPresent'),
               (4301308, 4, 9, 'kernel32.IsProcessorFeaturePresent'), (4301312, 4, 9, 'kernel32.GetStringTypeW'),
               (4301316, 4, 9, 'kernel32.IsValidCodePage'), (4301320, 4, 9, 'kernel32.GetACP'),
               (4301324, 4, 9, 'kernel32.GetOEMCP'), (4301328, 4, 9, 'kernel32.GetCPInfo'),
               (4301332, 4, 9, 'kernel32.DeleteCriticalSection'), (4301336, 4, 9, 'kernel32.UnhandledExceptionFilter'),
               (4301340, 4, 9, 'kernel32.SetUnhandledExceptionFilter'), (4301344, 4, 9, 'kernel32.InitializeCriticalSectionAndSpinCount'),
               (4301348, 4, 9, 'kernel32.TerminateProcess'), (4301352, 4, 9, 'kernel32.TlsAlloc'),
               (4301356, 4, 9, 'kernel32.TlsGetValue'), (4301360, 4, 9, 'kernel32.TlsSetValue'),
               (4301364, 4, 9, 'kernel32.TlsFree'), (4301368, 4, 9, 'kernel32.GetStartupInfoW'),
               (4301372, 4, 9, 'kernel32.GetProcessHeap'), (4301376, 4, 9, 'kernel32.FlushFileBuffers'),
               (4301380, 4, 9, 'kernel32.GetConsoleCP'), (4301384, 4, 9, 'kernel32.RtlUnwind'),
               (4301388, 4, 9, 'kernel32.QueryPerformanceCounter'), (4301392, 4, 9, 'kernel32.GetSystemTimeAsFileTime'),
               (4301396, 4, 9, 'kernel32.GetEnvironmentStringsW'), (4300976, 4, 9, 'comdlg32.PrintDlgW'),
               (4300800, 4, 9, 'advapi32.LsaClose'), (4300804, 4, 9, 'advapi32.CreateProcessAsUserW'),
               (4300808, 4, 9, 'advapi32.CryptHashData'), (4300812, 4, 9, 'advapi32.CryptCreateHash'),
               (4300816, 4, 9, 'advapi32.CryptDecrypt'), (4300820, 4, 9, 'advapi32.CryptEncrypt'),
               (4300824, 4, 9, 'advapi32.CryptImportKey'), (4300828, 4, 9, 'advapi32.CryptExportKey'),
               (4300832, 4, 9, 'advapi32.CryptDestroyKey'), (4300836, 4, 9, 'advapi32.CryptDeriveKey'),
               (4300840, 4, 9, 'advapi32.CryptGenKey'), (4300844, 4, 9, 'advapi32.CryptReleaseContext'),
               (4300848, 4, 9, 'advapi32.CryptAcquireContextW'), (4300852, 4, 9, 'advapi32.StartServiceW'),
               (4300856, 4, 9, 'advapi32.QueryServiceStatus'), (4300860, 4, 9, 'advapi32.OpenServiceW'),
               (4300864, 4, 9, 'advapi32.OpenSCManagerW'), (4300868, 4, 9, 'advapi32.DeleteService'),
               (4300872, 4, 9, 'advapi32.CreateServiceW'), (4300876, 4, 9, 'advapi32.ControlService'),
               (4300880, 4, 9, 'advapi32.CloseServiceHandle'), (4300884, 4, 9, 'advapi32.OpenProcessToken'),
               (4300888, 4, 9, 'advapi32.LsaEnumerateAccountRights'), (4300892, 4, 9, 'advapi32.LsaOpenPolicy'),
               (4300896, 4, 9, 'advapi32.LsaFreeMemory'), (4300900, 4, 9, 'advapi32.SetSecurityInfo'),
               (4300904, 4, 9, 'advapi32.GetSecurityInfo'), (4300908, 4, 9, 'advapi32.LookupPrivilegeValueW'),
               (4300912, 4, 9, 'advapi32.AddAccessAllowedAce'), (4300916, 4, 9, 'advapi32.GetAce'),
               (4300920, 4, 9, 'advapi32.AddAce'), (4300924, 4, 9, 'advapi32.InitializeAcl'),
               (4300928, 4, 9, 'advapi32.GetLengthSid'), (4300932, 4, 9, 'advapi32.FreeSid'),
               (4300936, 4, 9, 'advapi32.AllocateAndInitializeSid'), (4300940, 4, 9, 'advapi32.SetTokenInformation'),
               (4300944, 4, 9, 'advapi32.GetTokenInformation'), (4300948, 4, 9, 'advapi32.RegSetValueExW'),
               (4300952, 4, 9, 'advapi32.RegQueryValueExW'), (4300956, 4, 9, 'advapi32.RegOpenKeyExW'),
               (4300960, 4, 9, 'advapi32.RegOpenKeyW'), (4300964, 4, 9, 'advapi32.RegCreateKeyW'),
               (4300968, 4, 9, 'advapi32.RegCloseKey'), (4371208, 4, 9, 'user32.GetSysColorBrush'),
               (4371212, 4, 9, 'user32.SetCursor'), (4371216, 4, 9, 'user32.LoadCursorW'),
               (4371220, 4, 9, 'user32.LoadStringW'), (4371224, 4, 9, 'user32.SetWindowTextW'),
               (4371228, 4, 9, 'user32.GetDlgItem'), (4371232, 4, 9, 'user32.EndDialog'),
               (4371236, 4, 9, 'user32.DialogBoxIndirectParamW'), (4371240, 4, 9, 'user32.InflateRect'),
               (4371244, 4, 9, 'user32.SendMessageW'), (4371180, 4, 9, 'gdi32.EndPage'),
               (4371184, 4, 9, 'gdi32.EndDoc'), (4371188, 4, 9, 'gdi32.StartDocW'),
               (4371192, 4, 9, 'gdi32.SetMapMode'), (4371196, 4, 9, 'gdi32.GetDeviceCaps'),
               (4371200, 4, 9, 'gdi32.StartPage')]

        self.assertEqual(sorted(imps), sorted(ans))

    def test_pe_jmptable(self):
        vw = self.vw_sphinx

        tblins = 0x00403b3c
        xrefs = vw.getXrefsFrom(tblins, viv_con.REF_PTR)
        self.assertEqual(len(xrefs), 1)
        self.assertEqual(xrefs[0], (tblins, 0x403bc4, 3, 0))

        xrefs = vw.getXrefsFrom(tblins, viv_con.REF_CODE)
        self.assertEqual(len(xrefs), 4)
        codeblocks = [
            (4209468, 4209475, 1, 2),
            (4209468, 4209509, 1, 2),
            (4209468, 4209517, 1, 2),
            (4209468, 4209525, 1, 2)
        ]
        for xr in xrefs:
            self.assertTrue(xr in codeblocks)

    def test_pe_dynamic_noret(self):
        vw = self.vw_sphinx
        noret = [0x408d40, 0x408da0, 0x429229, 0x426e8a, 0x43b06c, 0x4268d4, 0x4268ba, 0x4291fd]
        for va in noret:
            self.assertTrue(vw.isNoReturnVa(va), msg='0x%.8x is not no return!' % va)

    def test_emulation_vaset(self):
        vw = self.vw_psexec
        funcs = set([4281345, 4294188, 4289086, 4293695, 4282944, 4290121, 4198480, 4290145, 4210288, 4282482, 4280472, 4268701, 4208800, 4210848, 4290211, 4209328, 4291252, 4290228, 4289721, 4239035, 4293319, 4281548, 4287692, 4288719, 4293840, 4221654, 4233944, 4221660, 4207328, 4209376, 4221666, 4291296, 4221672, 4280554, 4288749, 4287725, 4281584, 4259060, 4289292, 4282646, 4285732, 4216112, 4291392, 4280642, 4290370, 4206416, 4259158, 4208992, 4209504, 4280685, 4290929, 4287859, 4293495, 4208512, 4259207, 4211088, 4293008, 4199824, 4280730, 4241818, 4259229, 4211616, 4282788, 4294064, 4284338, 4289976, 4209088, 4209600, 4289993, 4198864, 4213200, 4206032, 4259282, 4209120, 4209632, 4231139, 4269557, 4289528])
        for fva in funcs:
            self.assertEqual(fva, vw.getFunction(fva))

        # if we reorder analysis passes or new ones, this might change, and that's okay.
        # this is more designed to be a smoke test that we actually get a populated vaset
        emufuncs = vw.getVaSet('EmucodeFunctions')
        self.assertTrue(len(emufuncs) > 0)
        e = set(emufuncs.keys())
        f = set(funcs)
        self.assertTrue(f.intersection(e) == f)

    def test_get_imports(self):
        vw = self.vw_psexec
        imps = set([(4301428, 4, 9, 'version.GetFileVersionInfoSizeW'),
                    (4301432, 4, 9, 'version.GetFileVersionInfoW'),
                    (4301436, 4, 9, 'version.VerQueryValueW'),
                    (4301416, 4, 9, 'netapi32.NetServerEnum'),
                    (4301420, 4, 9, 'netapi32.NetApiBufferFree'),
                    (4301444, 4, 9, 'ws2_32.gethostname'),
                    (4301448, 4, 9, 'ws2_32.WSAStartup'),
                    (4301452, 4, 9, 'ws2_32.inet_ntoa'),
                    (4301456, 4, 9, 'ws2_32.gethostbyname'),
                    (4301404, 4, 9, 'mpr.WNetCancelConnection2W'),
                    (4301408, 4, 9, 'mpr.WNetAddConnection2W'),
                    (4300984, 4, 9, 'kernel32.GetExitCodeProcess'),
                    (4300988, 4, 9, 'kernel32.ResumeThread'),
                    (4300992, 4, 9, 'kernel32.WaitForMultipleObjects'),
                    (4300996, 4, 9, 'kernel32.GetFileTime'),
                    (4301000, 4, 9, 'kernel32.DuplicateHandle'),
                    (4301004, 4, 9, 'kernel32.DisconnectNamedPipe'),
                    (4301008, 4, 9, 'kernel32.SetNamedPipeHandleState'),
                    (4301012, 4, 9, 'kernel32.TransactNamedPipe'),
                    (4301016, 4, 9, 'kernel32.CreateEventW'),
                    (4301020, 4, 9, 'kernel32.GetCurrentProcessId'),
                    (4301024, 4, 9, 'kernel32.GetFullPathNameW'),
                    (4301028, 4, 9, 'kernel32.SetFileAttributesW'),
                    (4301032, 4, 9, 'kernel32.GetFileAttributesW'),
                    (4301036, 4, 9, 'kernel32.CopyFileW'),
                    (4301040, 4, 9, 'kernel32.WaitNamedPipeW'),
                    (4301044, 4, 9, 'kernel32.SetConsoleCtrlHandler'),
                    (4301048, 4, 9, 'kernel32.SetConsoleTitleW'),
                    (4301052, 4, 9, 'kernel32.ReadConsoleW'),
                    (4301056, 4, 9, 'kernel32.GetVersion'),
                    (4301060, 4, 9, 'kernel32.SetProcessAffinityMask'),
                    (4301064, 4, 9, 'kernel32.ReadFile'),
                    (4301068, 4, 9, 'kernel32.GetConsoleScreenBufferInfo'),
                    (4301072, 4, 9, 'kernel32.MultiByteToWideChar'),
                    (4301076, 4, 9, 'kernel32.GetComputerNameW'),
                    (4301080, 4, 9, 'kernel32.DeleteFileW'),
                    (4301084, 4, 9, 'kernel32.CreateFileW'),
                    (4301088, 4, 9, 'kernel32.GetSystemDirectoryW'),
                    (4301092, 4, 9, 'kernel32.FindResourceW'),
                    (4301096, 4, 9, 'kernel32.LoadLibraryExW'),
                    (4301100, 4, 9, 'kernel32.FormatMessageA'),
                    (4301104, 4, 9, 'kernel32.GetTickCount'),
                    (4301108, 4, 9, 'kernel32.CloseHandle'),
                    (4301112, 4, 9, 'kernel32.WriteFile'),
                    (4301116, 4, 9, 'kernel32.SizeofResource'),
                    (4301120, 4, 9, 'kernel32.LoadResource'),
                    (4301124, 4, 9, 'kernel32.Sleep'),
                    (4301128, 4, 9, 'kernel32.WaitForSingleObject'),
                    (4301132, 4, 9, 'kernel32.SetEndOfFile'),
                    (4301136, 4, 9, 'kernel32.SetEvent'),
                    (4301140, 4, 9, 'kernel32.SetLastError'),
                    (4301144, 4, 9, 'kernel32.GetLastError'),
                    (4301148, 4, 9, 'kernel32.GetCurrentProcess'),
                    (4301152, 4, 9, 'kernel32.FreeLibrary'),
                    (4301156, 4, 9, 'kernel32.LockResource'),
                    (4301160, 4, 9, 'kernel32.SetPriorityClass'),
                    (4301164, 4, 9, 'kernel32.GetModuleFileNameW'),
                    (4301168, 4, 9, 'kernel32.GetCommandLineW'),
                    (4301172, 4, 9, 'kernel32.GetModuleHandleW'),
                    (4301176, 4, 9, 'kernel32.LoadLibraryW'),
                    (4301180, 4, 9, 'kernel32.GetStdHandle'),
                    (4301184, 4, 9, 'kernel32.GetFileType'),
                    (4301188, 4, 9, 'kernel32.LocalFree'),
                    (4301192, 4, 9, 'kernel32.LocalAlloc'),
                    (4301196, 4, 9, 'kernel32.GetProcAddress'),
                    (4301200, 4, 9, 'kernel32.FreeEnvironmentStringsW'),
                    (4301204, 4, 9, 'kernel32.LCMapStringW'),
                    (4301208, 4, 9, 'kernel32.OutputDebugStringW'),
                    (4301212, 4, 9, 'kernel32.HeapSize'),
                    (4301216, 4, 9, 'kernel32.HeapReAlloc'),
                    (4301220, 4, 9, 'kernel32.SetFilePointerEx'),
                    (4301224, 4, 9, 'kernel32.WriteConsoleW'),
                    (4301228, 4, 9, 'kernel32.GetEnvironmentVariableW'),
                    (4301232, 4, 9, 'kernel32.RaiseException'),
                    (4301236, 4, 9, 'kernel32.LoadLibraryExA'),
                    (4301240, 4, 9, 'kernel32.EncodePointer'),
                    (4301244, 4, 9, 'kernel32.DecodePointer'),
                    (4301248, 4, 9, 'kernel32.ExitProcess'),
                    (4301252, 4, 9, 'kernel32.GetModuleHandleExW'),
                    (4301256, 4, 9, 'kernel32.WideCharToMultiByte'),
                    (4301260, 4, 9, 'kernel32.HeapFree'),
                    (4301264, 4, 9, 'kernel32.HeapAlloc'),
                    (4301268, 4, 9, 'kernel32.GetConsoleMode'),
                    (4301272, 4, 9, 'kernel32.ReadConsoleInputA'),
                    (4301276, 4, 9, 'kernel32.SetConsoleMode'),
                    (4301280, 4, 9, 'kernel32.EnterCriticalSection'),
                    (4301284, 4, 9, 'kernel32.LeaveCriticalSection'),
                    (4301288, 4, 9, 'kernel32.SetStdHandle'),
                    (4301292, 4, 9, 'kernel32.CreateThread'),
                    (4301296, 4, 9, 'kernel32.GetCurrentThreadId'),
                    (4301300, 4, 9, 'kernel32.ExitThread'),
                    (4301304, 4, 9, 'kernel32.IsDebuggerPresent'),
                    (4301308, 4, 9, 'kernel32.IsProcessorFeaturePresent'),
                    (4301312, 4, 9, 'kernel32.GetStringTypeW'),
                    (4301316, 4, 9, 'kernel32.IsValidCodePage'),
                    (4301320, 4, 9, 'kernel32.GetACP'),
                    (4301324, 4, 9, 'kernel32.GetOEMCP'),
                    (4301328, 4, 9, 'kernel32.GetCPInfo'),
                    (4301332, 4, 9, 'kernel32.DeleteCriticalSection'),
                    (4301336, 4, 9, 'kernel32.UnhandledExceptionFilter'),
                    (4301340, 4, 9, 'kernel32.SetUnhandledExceptionFilter'),
                    (4301344, 4, 9, 'kernel32.InitializeCriticalSectionAndSpinCount'),
                    (4301348, 4, 9, 'kernel32.TerminateProcess'),
                    (4301352, 4, 9, 'kernel32.TlsAlloc'),
                    (4301356, 4, 9, 'kernel32.TlsGetValue'),
                    (4301360, 4, 9, 'kernel32.TlsSetValue'),
                    (4301364, 4, 9, 'kernel32.TlsFree'),
                    (4301368, 4, 9, 'kernel32.GetStartupInfoW'),
                    (4301372, 4, 9, 'kernel32.GetProcessHeap'),
                    (4301376, 4, 9, 'kernel32.FlushFileBuffers'),
                    (4301380, 4, 9, 'kernel32.GetConsoleCP'),
                    (4301384, 4, 9, 'kernel32.RtlUnwind'),
                    (4301388, 4, 9, 'kernel32.QueryPerformanceCounter'),
                    (4301392, 4, 9, 'kernel32.GetSystemTimeAsFileTime'),
                    (4301396, 4, 9, 'kernel32.GetEnvironmentStringsW'),
                    (4300976, 4, 9, 'comdlg32.PrintDlgW'),
                    (4300800, 4, 9, 'advapi32.LsaClose'),
                    (4300804, 4, 9, 'advapi32.CreateProcessAsUserW'),
                    (4300808, 4, 9, 'advapi32.CryptHashData'),
                    (4300812, 4, 9, 'advapi32.CryptCreateHash'),
                    (4300816, 4, 9, 'advapi32.CryptDecrypt'),
                    (4300820, 4, 9, 'advapi32.CryptEncrypt'),
                    (4300824, 4, 9, 'advapi32.CryptImportKey'),
                    (4300828, 4, 9, 'advapi32.CryptExportKey'),
                    (4300832, 4, 9, 'advapi32.CryptDestroyKey'),
                    (4300836, 4, 9, 'advapi32.CryptDeriveKey'),
                    (4300840, 4, 9, 'advapi32.CryptGenKey'),
                    (4300844, 4, 9, 'advapi32.CryptReleaseContext'),
                    (4300848, 4, 9, 'advapi32.CryptAcquireContextW'),
                    (4300852, 4, 9, 'advapi32.StartServiceW'),
                    (4300856, 4, 9, 'advapi32.QueryServiceStatus'),
                    (4300860, 4, 9, 'advapi32.OpenServiceW'),
                    (4300864, 4, 9, 'advapi32.OpenSCManagerW'),
                    (4300868, 4, 9, 'advapi32.DeleteService'),
                    (4300872, 4, 9, 'advapi32.CreateServiceW'),
                    (4300876, 4, 9, 'advapi32.ControlService'),
                    (4300880, 4, 9, 'advapi32.CloseServiceHandle'),
                    (4300884, 4, 9, 'advapi32.OpenProcessToken'),
                    (4300888, 4, 9, 'advapi32.LsaEnumerateAccountRights'),
                    (4300892, 4, 9, 'advapi32.LsaOpenPolicy'),
                    (4300896, 4, 9, 'advapi32.LsaFreeMemory'),
                    (4300900, 4, 9, 'advapi32.SetSecurityInfo'),
                    (4300904, 4, 9, 'advapi32.GetSecurityInfo'),
                    (4300908, 4, 9, 'advapi32.LookupPrivilegeValueW'),
                    (4300912, 4, 9, 'advapi32.AddAccessAllowedAce'),
                    (4300916, 4, 9, 'advapi32.GetAce'),
                    (4300920, 4, 9, 'advapi32.AddAce'),
                    (4300924, 4, 9, 'advapi32.InitializeAcl'),
                    (4300928, 4, 9, 'advapi32.GetLengthSid'),
                    (4300932, 4, 9, 'advapi32.FreeSid'),
                    (4300936, 4, 9, 'advapi32.AllocateAndInitializeSid'),
                    (4300940, 4, 9, 'advapi32.SetTokenInformation'),
                    (4300944, 4, 9, 'advapi32.GetTokenInformation'),
                    (4300948, 4, 9, 'advapi32.RegSetValueExW'),
                    (4300952, 4, 9, 'advapi32.RegQueryValueExW'),
                    (4300956, 4, 9, 'advapi32.RegOpenKeyExW'),
                    (4300960, 4, 9, 'advapi32.RegOpenKeyW'),
                    (4300964, 4, 9, 'advapi32.RegCreateKeyW'),
                    (4300968, 4, 9, 'advapi32.RegCloseKey'),
                    (4371208, 4, 9, 'user32.GetSysColorBrush'),
                    (4371212, 4, 9, 'user32.SetCursor'),
                    (4371216, 4, 9, 'user32.LoadCursorW'),
                    (4371220, 4, 9, 'user32.LoadStringW'),
                    (4371224, 4, 9, 'user32.SetWindowTextW'),
                    (4371228, 4, 9, 'user32.GetDlgItem'),
                    (4371232, 4, 9, 'user32.EndDialog'),
                    (4371236, 4, 9, 'user32.DialogBoxIndirectParamW'),
                    (4371240, 4, 9, 'user32.InflateRect'),
                    (4371244, 4, 9, 'user32.SendMessageW'),
                    (4371180, 4, 9, 'gdi32.EndPage'),
                    (4371184, 4, 9, 'gdi32.EndDoc'),
                    (4371188, 4, 9, 'gdi32.StartDocW'),
                    (4371192, 4, 9, 'gdi32.SetMapMode'),
                    (4371196, 4, 9, 'gdi32.GetDeviceCaps'),
                    (4371200, 4, 9, 'gdi32.StartPage')])

        failed = False
        # self.assertEqual(imps, vw.getImports())
        for iloc in vw.getImports():
            if iloc not in imps:
                logger.critical(f'{iloc} was not found in the predefined imports. A new one?')
                failed = True

        oimp = set(vw.getImports())
        for iloc in imps:
            if iloc not in oimp:
                logger.critical(f'The imports are missing {iloc}.')

        if failed:
            self.fail('Please see test logs for import test failures')

    def test_hiaddr_imports(self):
        # Test if imports located at a high relative address are discovered.
        file_path = helpers.getTestPath('windows', 'i386', 'section_has_hi_virtualaddr.exe')
        pe = PE.peFromFileName(file_path)
        import_list = pe.getImports()
        self.assertEqual(len(import_list), 36, "expecting 36 imported functions")
        self.assertEqual(import_list[0][1], "advapi32.dll", "imported function with name 'advapi32.dll' not found")

    def test_mimikatz_segments(self):
        vw = self.vw_mimi
        ans = {
            # name -> (Base, Size, Flags)
            'PE_Header': (0x400000, 0x1000, e_memory.MM_READ),
            '.text': (0x401000, 0x72000, e_memory.MM_READ | e_memory.MM_EXEC),
            '.data': (0x4b6000, 0x5000, e_memory.MM_READ | e_memory.MM_WRITE),
            '.rdata': (0x473000, 0x43000, e_memory.MM_READ),
            '.reloc': (0x4bf000, 0x7000, e_memory.MM_READ),
        }
        for sva, ssize, sname, sfname in vw.getSegments():
            self.assertEqual(ans[sname][0], sva)
            self.assertEqual(ans[sname][1], ssize)
            self.assertEqual(sfname, 'mimikatz')

            mva, msize, flags, mfname = vw.getMemoryMap(sva)
            self.assertEqual(mva, sva)
            self.assertEqual(msize, ssize)
            self.assertEqual(flags, ans[sname][2])
            self.assertEqual(mfname, sfname)

    def test_saved_structures(self):
        ans = [
            0x4001f0,
            0x400218,
            0x400240,
            0x400268,
            0x400290
        ]
        vw = self.vw_psexec
        for va in ans:
            loc = vw.getLocation(va)
            self.assertIsNotNone(loc)
            self.assertEqual(loc[0], va)
            self.assertEqual(loc[1], 40)
            self.assertEqual(loc[2], viv_con.LOC_STRUCT)
            self.assertEqual(loc[3], 'pe.IMAGE_SECTION_HEADER')
