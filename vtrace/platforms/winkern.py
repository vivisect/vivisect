'''
Code for helping out windows kernel debugging...
'''
import logging

import vtrace
import vstruct
import vstruct.builder as vs_builder

from vstruct.primitives import *

logger = logging.getLogger(__name__)

class KeBugCheckBreak(vtrace.Breakpoint):

    def __init__(self, symname):
        vtrace.Breakpoint.__init__(self, None, expression=symname)
        self.stealthbreak = True # No NOTIFY_BREAK

    def notify(self, event, trace):
        sp = trace.getStackCounter()
        savedpc, exccode = trace.readMemoryFormat(sp, '<PP')
        trace._fireSignal(exccode)

win_builds = {
    2600: 'Windows XP',
}

class KDDEBUGGER_DATA64(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self._vs_field_align = True

        List = vstruct.VStruct()
        List.Flink   = v_ptr64()
        List.Blink   = v_ptr64()

        Header = vstruct.VStruct()
        Header.List     = List
        Header.OwnerTag = v_uint32()
        Header.Size     = v_uint32()

        self.Header = Header

        self.KernBase  = v_ptr64()
        self.BreakpointWithStatus  = v_ptr64()
        self.SavedContext  = v_ptr64()
        self.ThCallbackStack = v_uint16()
        self.NextCallback    = v_uint16()
        self.FramePointer    = v_uint16()
        #self.PaeEnabled:1    = v_uint16()
        self.PaeEnabled      = v_uint16()
        self.KiCallUserMode    = v_ptr64()
        self.KeUserCallbackDispatcher  = v_ptr64()
        self.PsLoadedModuleList    = v_ptr64()
        self.PsActiveProcessHead   = v_ptr64()
        self.PspCidTable   = v_ptr64()
        self.ExpSystemResourcesList    = v_ptr64()
        self.ExpPagedPoolDescriptor    = v_ptr64()
        self.ExpNumberOfPagedPools = v_ptr64()
        self.KeTimeIncrement   = v_ptr64()
        self.KeBugCheckCallbackListHead    = v_ptr64()
        self.KiBugcheckData    = v_ptr64()
        self.IopErrorLogListHead   = v_ptr64()
        self.ObpRootDirectoryObject    = v_ptr64()
        self.ObpTypeObjectType = v_ptr64()
        self.MmSystemCacheStart    = v_ptr64()
        self.MmSystemCacheEnd  = v_ptr64()
        self.MmSystemCacheWs   = v_ptr64()
        self.MmPfnDatabase = v_ptr64()
        self.MmSystemPtesStart = v_ptr64()
        self.MmSystemPtesEnd   = v_ptr64()
        self.MmSubsectionBase  = v_ptr64()
        self.MmNumberOfPagingFiles = v_ptr64()
        self.MmLowestPhysicalPage  = v_ptr64()
        self.MmHighestPhysicalPage = v_ptr64()
        self.MmNumberOfPhysicalPages   = v_ptr64()
        self.MmMaximumNonPagedPoolInBytes  = v_ptr64()
        self.MmNonPagedSystemStart = v_ptr64()
        self.MmNonPagedPoolStart   = v_ptr64()
        self.MmNonPagedPoolEnd = v_ptr64()
        self.MmPagedPoolStart  = v_ptr64()
        self.MmPagedPoolEnd    = v_ptr64()
        self.MmPagedPoolInformation    = v_ptr64()
        self.MmPageSize    = v_ptr64()
        self.MmSizeOfPagedPoolInBytes  = v_ptr64()
        self.MmTotalCommitLimit    = v_ptr64()
        self.MmTotalCommittedPages = v_ptr64()
        self.MmSharedCommit    = v_ptr64()
        self.MmDriverCommit    = v_ptr64()
        self.MmProcessCommit   = v_ptr64()
        self.MmPagedPoolCommit = v_ptr64()
        self.MmExtendedCommit  = v_ptr64()
        self.MmZeroedPageListHead  = v_ptr64()
        self.MmFreePageListHead    = v_ptr64()
        self.MmStandbyPageListHead = v_ptr64()
        self.MmModifiedPageListHead    = v_ptr64()
        self.MmModifiedNoWritePageListHead = v_ptr64()
        self.MmAvailablePages  = v_ptr64()
        self.MmResidentAvailablePages  = v_ptr64()
        self.PoolTrackTable    = v_ptr64()
        self.NonPagedPoolDescriptor    = v_ptr64()
        self.MmHighestUserAddress  = v_ptr64()
        self.MmSystemRangeStart    = v_ptr64()
        self.MmUserProbeAddress    = v_ptr64()
        self.KdPrintCircularBuffer = v_ptr64()
        self.KdPrintCircularBufferEnd  = v_ptr64()
        self.KdPrintWritePointer   = v_ptr64()
        self.KdPrintRolloverCount  = v_ptr64()
        self.MmLoadedUserImageList = v_ptr64()
        # NT 5.1 Addition
        self.NtBuildLab    = v_ptr64()
        self.KiNormalSystemCall    = v_ptr64()
        # NT 5.0 QFE addition
        self.KiProcessorBlock  = v_ptr64()
        self.MmUnloadedDrivers = v_ptr64()
        self.MmLastUnloadedDriver  = v_ptr64()
        self.MmTriageActionTaken   = v_ptr64()
        self.MmSpecialPoolTag  = v_ptr64()
        self.KernelVerifier    = v_ptr64()
        self.MmVerifierData    = v_ptr64()
        self.MmAllocatedNonPagedPool   = v_ptr64()
        self.MmPeakCommitment  = v_ptr64()
        self.MmTotalCommitLimitMaximum = v_ptr64()
        self.CmNtCSDVersion    = v_ptr64()
        # NT 5.1 Addition
        self.MmPhysicalMemoryBlock = v_ptr64()
        self.MmSessionBase = v_ptr64()
        self.MmSessionSize = v_ptr64()
        self.MmSystemParentTablePage   = v_ptr64()
        # Server 2003 addition
        self.MmVirtualTranslationBase  = v_ptr64()
        self.OffsetKThreadNextProcessor    = v_uint16()
        self.OffsetKThreadTeb  = v_uint16()
        self.OffsetKThreadKernelStack  = v_uint16()
        self.OffsetKThreadInitialStack = v_uint16()
        self.OffsetKThreadApcProcess   = v_uint16()
        self.OffsetKThreadState    = v_uint16()
        self.OffsetKThreadBStore   = v_uint16()
        self.OffsetKThreadBStoreLimit  = v_uint16()
        self.SizeEProcess  = v_uint16()
        self.OffsetEprocessPeb = v_uint16()
        self.OffsetEprocessParentCID   = v_uint16()
        self.OffsetEprocessDirectoryTableBase  = v_uint16()
        self.SizePrcb  = v_uint16()
        self.OffsetPrcbDpcRoutine  = v_uint16()
        self.OffsetPrcbCurrentThread   = v_uint16()
        self.OffsetPrcbMhz = v_uint16()
        self.OffsetPrcbCpuType = v_uint16()
        self.OffsetPrcbVendorString    = v_uint16()
        self.OffsetPrcbProcStateContext    = v_uint16()
        self.OffsetPrcbNumber  = v_uint16()
        self.SizeEThread   = v_uint16()
        self.KdPrintCircularBufferPtr  = v_ptr64()
        self.KdPrintBufferSize = v_ptr64()
        self.KeLoaderBlock = v_ptr64()
        self.SizePcr   = v_uint16()
        self.OffsetPcrSelfPcr  = v_uint16()
        self.OffsetPcrCurrentPrcb  = v_uint16()
        self.OffsetPcrContainedPrcb    = v_uint16()
        self.OffsetPcrInitialBStore    = v_uint16()
        self.OffsetPcrBStoreLimit  = v_uint16()
        self.OffsetPcrInitialStack = v_uint16()
        self.OffsetPcrStackLimit   = v_uint16()
        self.OffsetPrcbPcrPage = v_uint16()
        self.OffsetPrcbProcStateSpecialReg = v_uint16()
        self.GdtR0Code = v_uint16()
        self.GdtR0Data = v_uint16()
        self.GdtR0Pcr  = v_uint16()
        self.GdtR3Code = v_uint16()
        self.GdtR3Data = v_uint16()
        self.GdtR3Teb  = v_uint16()
        self.GdtLdt    = v_uint16()
        self.GdtTss    = v_uint16()
        self.Gdt64R3CmCode = v_uint16()
        self.Gdt64R3CmTeb  = v_uint16()
        self.IopNumTriageDumpDataBlocks    = v_ptr64()
        self.IopTriageDumpDataBlocks   = v_ptr64()
        # Longhorn
        self.VfCrashDataBlock  = v_ptr64()
        self.MmBadPagesDetected    = v_ptr64()
        self.MmZeroedPageSingleBitErrorsDetected   = v_ptr64()
        # Windows 7
        self.MmBadPagesDetected    = v_ptr64()
        self.OffsetPrcbContext = v_uint16()

def addBugCheckBreaks(trace):
    trace.addBreakpoint(KeBugCheckBreak('nt.KeBugCheck'))
    trace.addBreakpoint(KeBugCheckBreak('nt.KeBugCheckEx'))

def initWinkernTrace(trace, kpcrva):

    # FIXME snap in structs depending on version
    import vstruct.defs.windows.win_5_1_i386.ntoskrnl as vs_w_ntoskrnl
    trace.vsbuilder.addVStructNamespace('nt', vs_w_ntoskrnl) # FIXME no remote!

    b =vs_builder.VStructBuilder()
    b.addVStructCtor('KDDEBUGGER_DATA64',KDDEBUGGER_DATA64)
    trace.vsbuilder.addVStructNamespace('winkern',b)
    # Create a "struct" namespace "winkern" for our custom defined structures.

    trace.casesens = False

    kpcr = trace.getStruct('nt.KPCR', kpcrva)

    kver = trace.getStruct('nt.DBGKD_GET_VERSION64', kpcr.KdVersionBlock)
    dbgdata64va = trace.readMemoryFormat(kver.DebuggerDataList & trace.bigmask,'<I')[0]

    dbgdata64 = KDDEBUGGER_DATA64()
    dbgdata64.vsParse( trace.readMemory( dbgdata64va, len(dbgdata64) ))

    winver = win_builds.get( kver.MinorVersion )
    if winver is None:
        winver = 'Untested Windows Build! (%d)' % kver.MinorVersion

    kernbase = kver.KernBase & trace.bigmask
    modlist = kver.PsLoadedModuleList & trace.bigmask

    # FIXME hard coded page sizes!
    trace.setMeta('PAGE_SIZE', 1024)
    trace.setMeta('PAGE_SHIFT', 12)

    trace.setVariable('kpcr', kpcrva)
    trace.setVariable('kddebuggerdata64',dbgdata64va)
    trace.setVariable('KernelBase', kernbase)
    trace.setVariable('PsLoadedModuleList', modlist)

    trace.fireNotifiers(vtrace.NOTIFY_ATTACH)

    trace.addLibraryBase('nt', kernbase, always=True)

    ldr_entry = trace.readMemoryFormat(modlist, '<P')[0]
    while ldr_entry != modlist:
        ldte = trace.getStruct('nt.LDR_DATA_TABLE_ENTRY', ldr_entry)
        try:
            dllname = trace.readMemory(ldte.FullDllName.Buffer, ldte.FullDllName.Length).decode('utf-16le')
            dllbase = ldte.DllBase & trace.bigmask
            trace.addLibraryBase(dllname, dllbase, always=True)
        except Exception as e:
            logger.warning('Trouble while parsing one...')
        ldr_entry = ldte.InLoadOrderLinks.Flink & trace.bigmask

    addBugCheckBreaks(trace)

def walkListEntry(trace, va, sname, fname):
    '''
    Walk a list of structures (sname) with embedded
    LIST_ENTRY structs at field (fname) and yield each
    containing (va,structure).
    '''
    s = trace.getStruct(sname)
    listoff = s.vsGetOffset(fname)
    listva = va
    while True:
        structva = listva - listoff
        yield structva,trace.getStruct(sname,structva)
        nextva,prevva = trace.readMemoryFormat(listva,'<PP')
        if nextva == va:
            break

        listva = nextva

def walkListEntryHead(trace, va, sname, fname):
    '''
    Walk a list of structures (sname) with embedded
    LIST_ENTRY structs at field (fname) and yield each
    containing (va,structure).
    '''
    s = trace.getStruct(sname)
    listoff = s.vsGetOffset(fname)
    listva,prevva = trace.readMemoryFormat(va,'<PP')

    while True:
        structva = listva - listoff
        yield structva,trace.getStruct(sname,structva)
        nextva,prevva = trace.readMemoryFormat(listva,'<PP')
        if nextva == va:
            break

        listva = nextva

