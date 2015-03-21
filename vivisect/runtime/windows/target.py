import os

import vivisect.debug.api as v_dbgapi
import vivisect.debug.trace as v_trace
import vivisect.debug.target as v_target
import vivisect.lib.thishost as v_thishost

import vivisect.platforms.windows.dbgapi as v_win_dbgapi

from ctypes import *
from vertex.lib.common import tufo
from vivisect.runtime.windows.winapi import *

archctx = {
    'i386':CONTEXTx86,
    'amd64':CONTEXTx64,
}

class WindowsTarget(v_target.DebugTarget):

    def __init__(self, **info):
        v_target.DebugTarget.__init__(self, **info)
        self._init_dosmaps()

    def _proc_attach(self, proc):

        pid = proc[0]
        self.initPidThread(pid)

        def perpid():

            if not kernel32.DebugActiveProcess(pid):
                raise WinError()

            return self._proc_wait(proc)

        return self.callPidThread(pid,perpid)

    def _init_proc(self, pid, **info):
        proc = v_target.DebugTarget._init_proc(self, pid, **info)
        proc[1]['DEBUG_EVENT'] = DEBUG_EVENT()  # re-usable struct buf
        return proc

    def _init_thread(self, proc, tid, **info):
        thread = v_target.DebugTarget._init_thread(self, proc, tid, **info)

        arch = proc[1].get('arch')
        thread[1]['context'] = archctx.get(arch)()

        return thread

    def _proc_wait(self, proc):
        event = proc[1].get('DEBUG_EVENT')

        if not kernel32.WaitForDebugEvent(addressof(event), INFINITE):
            raise WinError()

        return self._make_events(proc,event)

    def _proc_detach(self, proc):
        pid = proc[0]
        def perpid():
            return self._real_proc_detach(proc)

        ret = self.callPidThread(pid,perpid)
        self.finiPidThread(pid)
        return ret

    def _real_proc_detach(self, proc):
        kernel32.DebugActiveProcessStop(proc[0])
        kernel32.CloseHandle( proc[1]['hProc'] )

    def _proc_stop(self, proc):
        hProc = proc[1].get('hProc')
        kernel32.DebugBreakProcess(hProc)

    def _proc_run(self, proc, signo=None):
        pid = proc[0]

        def perpid():
            tid = proc[1].get('stoptid')
            status = DBG_CONTINUE
            if signo != None:
                status = DBG_EXCEPTION_NOT_HANDLED

            if not kernel32.ContinueDebugEvent(pid,tid,status):
                raise WinError()

            return self._proc_wait(proc)

        return self.callPidThread(pid,perpid)

    def _trace_exec(self, cmdline, **opts):

        procinfo = {}
        def perpid():

            sinfo = STARTUPINFO()
            pinfo = PROCESS_INFORMATION()

            if not kernel32.CreateProcessW(0, cmdline, 0, 0, 0,
                    DEBUG_ONLY_THIS_PROCESS, 0, 0, addressof(sinfo), addressof(pinfo)):
                raise WinError()

            pid = pinfo.ProcessId
            hProc = pinfo.Process
            hThread = pinfo.Thread

            proc = self._init_proc(pid)

            #pinfo = self._winProcInfo(hProc)
            # update both the "return proc" *and* ours

            kernel32.CloseHandle(hProc)
            kernel32.CloseHandle(hThread)

            return proc

        proc = self.execPidThread(perpid)
        events = self.callPidThread(proc[0], self._proc_wait, proc)

        hProc = proc[1]['hProc']

        retproc = (proc[0], self._winProcInfo(hProc))
        return retproc,events

    def _proc_kill(self, proc):
        hProc = proc[1].get('hProc')
        kernel32.TerminateProcess(hProc, 0)

    def _make_events(self, proc, event):

        pid = event.ProcessId
        tid = event.ThreadId

        if pid != proc[0]:
            raise Exception('DEBUG_EVENT.ProcessId != pid (%s)' % (proc[0],))

        ret = []
        proc[1]['stoptid'] = tid

        dbgcode = event.DebugEventCode

        # tight loops tend to be around exceptions/breaks
        # ( so handle them first )
        if dbgcode == EXCEPTION_DEBUG_EVENT:

            exc = event.u.Exception

            first = exc.FirstChance
            excrec = exc.ExceptionRecord

            code = excrec.ExceptionCode
            addr = excrec.ExceptionAddress
            flags = excrec.ExceptionFlags

            pcount = excrec.NumberParameters
            params = [ excrec.ExceptionInformation[i] for i in range(pcount) ]

            # since it takes context awareness to know what to fire
            # we'll just send an event back that's our trace knows how
            # to interpret into trace: events.
            sig = tufo('target:win:exception',
                    code=code,
                    addr=addr,
                    flags=flags,
                    params=params,
                  )

            return [ sig ]

        if dbgcode == CREATE_PROCESS_DEBUG_EVENT:

            cpi = event.u.CreateProcessInfo

            hProc = cpi.Process
            hThread = cpi.Thread
            baseaddr = cpi.BaseOfImage
            teb = cpi.ThreadLocalBase

            proc[1]['hProc'] = hProc
            procinfo = self._winProcInfo(hProc)

            # shove the win proc info into our proc as well
            proc[1].update( procinfo )

            thread = self._init_thread(proc, tid, handle=hThread, teb=teb)

            retproc = (pid, procinfo)
            retproc[1]['handle'] = hProc

            attach = tufo('target:attach', proc=retproc)

            path = retproc[1]['path']
            name = self._make_libname(path)
            lib = tufo( baseaddr, name=name, path=path )
            libload = tufo('target:lib:load', lib=lib, tid=tid)

            thrinit = tufo('target:thread:init', thread=thread)

            return [attach, thrinit, libload]

        if dbgcode == EXIT_PROCESS_DEBUG_EVENT:
            exitcode = event.u.ExitProcess.ExitCode
            exit = tufo('target:exit', exitcode=exitcode)
            self._real_proc_detach(proc)
            return [ exit ]

        if dbgcode == CREATE_THREAD_DEBUG_EVENT:
            teb = event.u.CreateThread.ThreadLocalBase
            hThread = event.u.CreateThread.Thread
            #FIXME WANT? startaddr = event.u.CreateThread.StartAddress
            thread = self._init_thread(proc, tid, handle=hThread, teb=teb)
            thrinit = tufo('target:thread:init', thread=thread)
            return [ thrinit ]

        if dbgcode == EXIT_THREAD_DEBUG_EVENT:
            exitcode = event.u.ExitThread.ExitCode

            threxit = tufo('target:thread:exit', tid=tid, exitcode=exitcode)
            self._fini_thread(proc, tid)

            return [ threxit ]

        if dbgcode == LOAD_DLL_DEBUG_EVENT:

            hProc = proc[1]['hProc']

            addr = event.u.LoadDll.BaseOfDll
            path = self._getMappedFileName(hProc, addr)
            name = self._make_libname(path)

            lib = tufo(addr, addr=addr, path=path, name=name)
            libload = tufo('target:lib:load', lib=lib, tid=tid)

            kernel32.CloseHandle(event.u.LoadDll.File)

            return [ libload ]

        if dbgcode == UNLOAD_DLL_DEBUG_EVENT:
            addr = event.u.UnloadDll.BaseOfDll
            libfree = tufo('target:lib:unload',addr=addr,tid=tid)
            return [ libfree ]

        err = tufo('target:err',msg='unknown DebugEventCode: %d' % (dbgcode,))
        return [ err ]

    def _make_libname(self, path):
        libname = os.path.basename(path.lower())
        if libname[-4:] in ('.exe','.dll','.sys','.ocx'):
            libname = libname[:-4]
        return libname

    def _winProcInfo(self, hProc):
        # windows specific, build out a proc tufo from pid/handle.
        needed = c_uint()
        hModule = HANDLE()
        name = (c_wchar * 512)()

        psapi.EnumProcessModules(hProc, addressof(hModule), 4, addressof(needed))
        psapi.GetModuleBaseNameW(hProc, hModule, name, 512)

        path = (c_wchar * 1024)()
        psapi.GetProcessImageFileNameW(hProc, path, 1024)

        dospath = self.getDosPath(path.value).lower()
        uac = self.getProcUacLevel(hProc)

        pbi = self.getProcBasicInfo(hProc)
        peb = pbi.get('peb')

        info = {
            'name':name.value.lower(),
            'path':dospath,
            'uac':uac,
            'peb':peb,
            'arch':v_thishost.get('arch'),
        }

        if IsWow64Process != None:
            b = BOOL()
            IsWow64Process(hProc, addressof(b))
            if b.value:
                info['wow64'] = True
                info['arch'] = 'i386'


        kernel32.CloseHandle(hModule)
        return info

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

    def _getMappedFileName(self, hProc, addr):
        name = (WCHAR * 1024)()
        if psapi.GetMappedFileNameW(hProc, addr, name, 1024):
            return self.getDosPath( name.value ).lower()

        if psapi.GetModuleFileNameExW(hProc, addr, name, 1024):
            return self.getDosPath( name.value ).lower()

        return None

    def _proc_memmaps(self, proc):

        ret = []
        addr = 0

        hProc = proc[1].get('hProc')

        mbi = MEMORY_BASIC_INFORMATION()

        while kernel32.VirtualQueryEx(hProc, addr, addressof(mbi), sizeof(mbi)) > 0:

            size = mbi.RegionSize
            if mbi.State == MEM_COMMIT:

                addr = mbi.BaseAddress
                prot = mbi.Protect & 0xff
                perm = perm_lookup.get(prot, 0)

                path = self._getMappedFileName(hProc, addr)

                ret.append( tufo(addr, size=size, path=path, perm=perm) )

            addr += size

        return ret
        
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

    def _proc_forpid(self, pid):

        hProc = kernel32.OpenProcess( PROCESS_ALL_ACCESS, 0, pid )
        if not hProc:
            return None

        info = self._winProcInfo(hProc)

        kernel32.CloseHandle(hProc)

        return tufo(pid,**info)

    def ps(self):
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
            proc = self._proc_forpid(pids[i])
            if proc == None:
                continue

            ret.append( proc )

        return ret

    def _proc_getregs(self, proc, thread):
        ctx = thread[1]['context']
        ctx.initContextFlags()

        hThread = thread[1]['handle']

        def perpid():

            if not kernel32.GetThreadContext( hThread, ctypes.addressof(ctx) ):
                raise WinError()

            return ctx.getRegDict()

        return self.callPidThread( proc[0], perpid )

    def _proc_setregs(self, proc, thread, regdict):
        ctx = thread[1]['context']
        hThread = thread[1]['handle']

        ctx.setRegDict(regdict)

        def perpid():
            if not kernel32.SetThreadContext( hThread, ctypes.addressof(ctx) ):
                raise WinError()

        return self.callPidThread(proc[0], perpid)


class WinTargetI386(WindowsTarget): pass
class WinTargetAmd64(WindowsTarget): pass

def winDebugCtor(**info):

    getDebugPrivileges()

    if v_thishost.check(arch='i386'):
        targ = WinTargetI386(**info)
        return v_win_dbgapi.WinDebugApi(targ)

    if v_thishost.check(arch='amd64'):
        targ = WinTargetAmd64(**info)
        return v_win_dbgapi.WinDebugApi(targ)

v_dbgapi.addDebugApi('this',winDebugCtor)
