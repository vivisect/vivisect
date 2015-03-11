
import vivisect.vdb.debug as v_debug
import vivisect.vdb.trace as v_trace
import vivisect.vdb.target as v_target
import vivisect.lib.thishost as v_thishost

from ctypes import *
from vivisect.runtime.windows.winapi import *

class WindowsTarget(v_target.DebugTarget):

    def __init__(self, **info):
        v_target.DebugTarget.__init__(self, **info)
        self._init_dosmaps()

        self.addExtApi('getDosPath', self.getDosPath)

    def _proc_attach(self, proc):

        if not kernel32.DebugActiveProcess(pid):
            raise WinError()

        event = DEBUG_EVENT()
        proc[1]['DEBUG_EVENT'] = event

        if not kernel32.WaitForDebugEvent(addressof(event), INFINITE):
            raise WinError()

        return self._make_events(proc, event)

    def _make_events(self, proc, event):

        pid = event.ProcessId
        tid = event.ThreadId

        if pid != proc[0]:
            raise Exception('DEBUG_EVENT.ProcessId != pid (%s)' % (proc[0],))

        ret = []
        proc[1]['stoptid'] = tid

        if event.DebugEventCode == CREATE_PROCESS_DEBUG_EVENT:

            cpi = event.u.CreateProcessInfo

            hProc = cpi.Process
            baseaddr = cpi.BaseOfImage
            teb = cpi.ThreadLocalBase

            proc[1]['hProc'] = hProc

            pbi = self.getProcBasicInfo(hProc)

            retproc = self._make_proc(pid,hProc)
            attach = self.initProcEvent('trace:attach', proc=retproc)

            path = retproc[1]['path']
            name = retproc[1]['name']
            libload = self.initProcEvent('trace:lib:load', name=name, addr=baseaddr, path=path)

            thread = (tid,{'teb':teb})
            thrinit = self.initProcEvent('trace:thread:init', thread=thread)

            return [attach, thrinit, libload]

    def _make_proc(self, pid, hProc):
        needed = c_uint()
        hModule = HANDLE()
        name = (c_wchar * 512)()

        psapi.EnumProcessModules(hProc, addressof(hModule), 4, addressof(needed))
        psapi.GetModuleBaseNameW(hProc, hModule, name, 512)

        path = (c_wchar * 1024)()
        psapi.GetProcessImageFileNameW(hProc, path, 1024)

        dospath = self.getDosPath(path.value)
        uac = self.getProcUacLevel(hProc)

        pbi = self.getProcBasicInfo(hProc)
        peb = pbi.get('peb')

        info = {
            'name':name.value,
            'path':dospath,
            'uac':uac,
            'peb':peb
        }

        kernel32.CloseHandle(hModule)
        return (pid,info)

    #def procAttach(self, pid):
    #def procRun(self, proc):
    #def procDetach(self, proc):
    def _proc_break(self, proc):
        hProc = proc[1].get('hProc')
        if not kernel32.DebugBreakProcess( hProc ):
            raise WinError()

    def _proc_memwrite(self, proc, addr, mem):
        ret = c_ulong(0)
        hProc = proc[1].get('hProc')
        if not kernel32.WriteProcessMemory(hProc, addr, mem, len(mem), addressof(ret)):
            raise WinError()

        return ret.value

    def _proc_memread(self, proc, addr, size):
        ret = c_ulong()
        mem = (c_char * size)()

        hProc = proc[1].get('hProc')
        if not kernel32.ReadProcessMemory(hProc, addr, addressof(mem), size, addressof(ret)):
            raise WinError()

        return mem.raw

    def getProcBasicInfo(self, hProc):
        '''
        Retrieve a dictionary populated with PROCESS_BASIC_INFORMATION.

        Example:
            pbi = tgt.getProcBasicInfo(hProc)
            peb = pbi.get('PebBaseAddress')

        '''
        got = DWORD()
        pbi = PROCESS_BASIC_INFORMATION()
        ntdll.NtQueryInformationProcess(hProc, ProcessBasicInformation, addressof(pbi), sizeof(pbi), addressof(got))
        return {'peb':pbi.PebBaseAddress,'pid':pbi.UniqueProcessId}

    def getDosPath(self, path):
        '''
        Translate an NT path to a DOS path.

        Example:

            dospath = tgt.getDosPath(ntpath)

        '''
        for drive,device in self.dosdevs:
            if path.startswith(device):
                return path.replace(device,drive)

    def getProcUacLevel(self, hProc):
        '''
        Retrieve the UAC elevation type for a process (by handle).

        Example:

            uac = tgt.getProcUacLevel(hProc)
            if uac == TokenElevationTypeFull:
                dostuff()

        '''

        token = HANDLE(0)
        etype = DWORD(0)
        outsize = DWORD(0)
        if not advapi32.OpenProcessToken(hProc, TOKEN_QUERY, addressof(token)):
            raise WinError()

        advapi32.GetTokenInformation(token, TokenElevationType, addressof(etype), 4, addressof(outsize))

        return etype.value

    def _init_dosmaps(self):
        self.dosdevs = []
        namebuf = (c_char * 1024)()
        size = kernel32.GetLogicalDriveStringsW(512, namebuf)
        dosdevs = namebuf.raw.decode('utf-16le').strip('\x00').split('\x00')

        for dosdev in dosdevs:

            drive = '%s:' % dosdev[0]
            device = (c_wchar * 512)()

            kernel32.QueryDosDeviceW(drive, device, 512)
            self.dosdevs.append( (drive, device.value) )

    def getProcList(self):
        count = 4096
        needed = c_int(0)

        while True:
            pids = (c_int * count)()
            if not psapi.EnumProcesses(addressof(pids), 4*count, addressof(needed)):
                raise WinError()

            if needed.value > count:
                count *= 2
                continue

            break

        ret = []
        for i in range(needed.value // 4):
            pid = pids[i]

            hProc = kernel32.OpenProcess( PROCESS_ALL_ACCESS, 0, pid )
            if not hProc:
                ret.append( (pids[i], {'name':'<permission denied>'}) )
                continue

            ret.append( self._make_proc(pid,hProc) )

            kernel32.CloseHandle(hProc)

        return ret

class WinTargetI386(WindowsTarget): pass
class WinTargetAmd64(WindowsTarget): pass

def winDebugCtor(**info):

    if v_thishost.check(arch='i386'):
        targ = WinTargetI386(**info)
        return v_debug.DebugApi(targ)

    if v_thishost.check(arch='amd64'):
        targ = WinTargetAmd64(**info)
        return v_debug.DebugApi(targ)

    print('winDebugCtor')

v_debug.addDebugApi('this',winDebugCtor)
