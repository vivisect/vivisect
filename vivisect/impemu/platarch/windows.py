import envi.archs.i386 as e_i386
import envi.archs.amd64 as e_amd64

import vivisect.impemu.emulator as v_i_emulator
import vivisect.impemu.platarch.i386 as v_i_i386

from vivisect.impemu.emulator import imphook

MAX_PATH = 260

# A shared place for most of the import hooks
class WindowsMixin(v_i_emulator.WorkspaceEmulator):

    def __init__(self):
        pass

    def readFilePath(self, va, unicode=False, default='unknown'):
        size = MAX_PATH
        if unicode:
            size = MAX_PATH * 2
        bytez = self.readMemory(va, size)
        if unicode:
            bytez = bytez.decode('utf-16le', 'ignore')
            bytez = bytez.split('\x00')[0]
        else:
            bytez = bytez.split(b'\x00')[0]
            bytez = bytez.decode('utf-8', 'ignore')

        if len(bytez) == MAX_PATH:
            bytez = default

        return bytez

    def readLibraryPath(self, va, unicode=False):
        bytez = self.readFilePath(va, unicode=unicode, default='unknownlib')
        return bytez.lower().split('.')[0]

    @imphook('kernel32.LoadLibraryA')
    def kernel32_LoadLibraryA(self, emu, callconv, api, argv):
        lpLibName = argv[0]
        libname = self.readLibraryPath(lpLibName)
        retval = emu.setVivTaint('dynlib',libname)
        callconv.execCallReturn(emu, retval, len(argv))

    @imphook('kernel32.LoadLibraryW')
    def kernel32_LoadLibraryW(self, emu, callconv, api, argv):
        lpLibName = argv[0]
        libname = self.readLibraryPath(lpLibName, unicode=True)
        retval = emu.setVivTaint('dynlib',libname)
        callconv.execCallReturn(emu, retval, len(argv))

    @imphook('kernel32.GetProcAddress')
    def kernel32_GetProcAddress(self, emu, callconv, api, argv):
        hLibrary,lpProcName = argv
        procname = self.readFilePath(lpProcName, default='unknownproc')

        libname = 'unknownlib'
        taint = emu.getVivTaint(hLibrary)
        if taint:
            tva,ttype,tinfo = taint
            if ttype == 'dynlib':
                libname = tinfo

        retval = emu.setVivTaint('dynfunc', (libname, procname))
        callconv.execCallReturn(emu, retval, len(argv))

    @imphook('kernel32.GetModuleHandleA')
    def kernel32_GetModuleHandleA(self, emu, callconv, api, argv):
        return self.kernel32_LoadLibraryA(emu, callconv, api, argv)

    @imphook('kernel32.GetModuleHandleW')
    def kernel32_GetModuleHandleW(self, emu, callconv, api, argv):
        return self.kernel32_LoadLibraryW(emu, callconv, api, argv)

    @imphook('kernel32.LoadLibraryExA')
    def kernel32_LoadLibraryExA(self, emu, callconv, api, argv):
        return self.kernel32_LoadLibraryA(emu, callconv, api, argv)

    @imphook('kernel32.LoadLibraryExW')
    def kernel32_LoadLibraryExW(self, emu, callconv, api, argv):
        return self.kernel32_LoadLibraryW(emu, callconv, api, argv)

    @imphook('kernel32.GetModuleHandleA')
    def kernel32_GetModuleHandleExA(self, emu, callconv, api, argv):
        dwFlags,lpLibName,phModule = argv
        libname = self.readLibraryPath(lpLibName, unicode=False)
        retval = emu.setVivTaint('dynlib',libname)
        callconv.execCallReturn(emu, retval, len(argv))

    @imphook('kernel32.GetModuleHandleW')
    def kernel32_GetModuleHandleExA(self, emu, callconv, api, argv):
        dwFlags,lpLibName,phModule = argv
        libname = self.readLibraryPath(lpLibName, unicode=True)
        retval = emu.setVivTaint('dynlib',libname)
        callconv.execCallReturn(emu, retval, len(argv))

class Windowsi386Emulator(WindowsMixin, v_i_i386.i386WorkspaceEmulator):

    taintregs = [
        e_i386.REG_EAX, e_i386.REG_ECX, e_i386.REG_EDX,
        e_i386.REG_EBX, e_i386.REG_EBP, e_i386.REG_ESI,
        e_i386.REG_EDI,
    ]

    def __init__(self, vw, **kwargs):
        '''
        Please see the base emulator class in vivisect/impemu/emulator.py for the parameters
        that can be passed through kwargs
        '''
        v_i_i386.i386WorkspaceEmulator.__init__(self, vw, **kwargs)
        WindowsMixin.__init__(self)

    @imphook('ntdll.seh3_prolog')
    def seh3_prolog(self, emu, callconv, api, argv):

        scopetable, localsize = argv

        emu.doPush(0) # seh3_handler
        emu.doPush(0) # saved seh3 scopetable

        ebp = emu.getRegister(e_i386.REG_EBP)
        esp = emu.getRegister(e_i386.REG_ESP)
        emu.writeMemValue(esp+16, ebp, 4)

        ebp = esp+16 # [saved_scope, seh3_handler, saved_eip, new_scope, <size>]
        esp -= localsize

        emu.setRegister(e_i386.REG_EBP, ebp)
        emu.setRegister(e_i386.REG_ESP, esp)
        emu.doPush(emu.getRegister(e_i386.REG_EBX))
        emu.doPush(emu.getRegister(e_i386.REG_ESI))
        emu.doPush(emu.getRegister(e_i386.REG_EDI))

    @imphook('ntdll.seh4_prolog')
    def seh4_prolog(self, emu, callconv, api, argv):
        self.seh3_prolog(emu, callconv, api, argv)
        emu.doPush(0xc0c0c0c0)
        emu.doPush(0)

    @imphook('ntdll.seh4_gs_prolog')
    def seh4_gs_prolog(self, emu, callconv, api, argv):
        self.seh3_prolog(emu, callconv, api, argv)
        emu.doPush(0xc0c0c0c0)
        emu.doPush(0)

    @imphook('ntdll.seh3_epilog')
    def seh3_epilog(self, emu, callconv, api, argv):

        emu.doPop()
        emu.setRegister(e_i386.REG_EDI, emu.doPop())
        emu.setRegister(e_i386.REG_ESI, emu.doPop())
        emu.setRegister(e_i386.REG_EBX, emu.doPop())

        ebp = emu.getRegister(e_i386.REG_EBP)
        emu.setRegister(e_i386.REG_ESP, ebp)
        emu.setRegister(e_i386.REG_EBP, emu.doPop())

    @imphook('ntdll.seh4_epilog')
    def seh4_epilog(self, emu, callconv, api, argv):

        emu.doPop()
        emu.setRegister(e_i386.REG_EDI, emu.doPop())
        emu.setRegister(e_i386.REG_EDI, emu.doPop())
        emu.setRegister(e_i386.REG_ESI, emu.doPop())
        emu.setRegister(e_i386.REG_EBX, emu.doPop())

        ebp = emu.getRegister(e_i386.REG_EBP)
        emu.setRegister(e_i386.REG_ESP, ebp)
        emu.setRegister(e_i386.REG_EBP, emu.doPop())

    @imphook('ntdll.eh_prolog')
    def eh_prolog(self, emu, callconv, api, argv):
        emu.doPop()  # Remove saved eip

        # Push ebp, move ebp, esp
        emu.doPush(emu.getRegister(e_i386.REG_EBP))
        esp = emu.getRegister(e_i386.REG_ESP)
        emu.setRegister(e_i386.REG_EBP, esp)

        # Push a new EH record
        emu.doPush(0xffffffff)
        emu.doPush(emu.getRegister(e_i386.REG_EAX))
        emu.doPush(0xc0c0c0c0)

    @imphook('ntdll._alloca_probe')
    def alloca_probe(self, emu, callconv, api, argv):
        esp = emu.getRegister(e_i386.REG_ESP)
        eax = emu.getRegister(e_i386.REG_EAX)
        if eax < 0x1000:
            eax -= 4
            emu.setRegister(e_i386.REG_ESP,  (esp-eax))
        else:
            while eax > 0x1000:
                eax -= 0x1000
                emu.setRegister(e_i386.REG_ESP,  (esp-0x1000))
                esp -= 0x1000

            emu.setRegister(e_i386.REG_ESP,  (esp-eax))

    @imphook('ntdll.gs_prolog')
    def gs_prolog(self, emu, callconv, api, argv):
        esp = emu.getRegister(e_i386.REG_ESP)
        esp += 8
        eax = emu.getRegister(e_i386.REG_EAX)
        # XXX - this is not a complete implementation..
        if eax < 0x1000:
            emu.setRegister(e_i386.REG_ESP,  (esp-eax))

