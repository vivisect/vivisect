import optparse

import envi.cli as e_cli
import vdb.extensions.windows as v_ext_windows
import vtrace.platforms.winkern as vt_winkern
# FIXME bugcheck lookup

KERNEL_MODE_EXCEPTION_NOT_HANDLED = 0x0000008e

def getBugCheckName(code):
    return 'FIXME BUGCHECK NAME'

'''
//
// Flags used in the VAD
//
typedef struct _MMVAD_FLAGS
{
    ULONG CommitCharge:19;
    ULONG NoChange:1;
    ULONG VadType:3;
    ULONG MemCommit:1;
    ULONG Protection:5;
    ULONG Spare:2;
    ULONG PrivateMemory:1;
} MMVAD_FLAGS, *PMMVAD_FLAGS;

//
// Extended flags used in the VAD
//
typedef struct _MMVAD_FLAGS2
{
    ULONG FileOffset:24;
    ULONG SecNoChange:1;
    ULONG OneSecured:1;
    ULONG MultipleSecured:1;
    ULONG ReadOnly:1;
    ULONG LongVad:1;
    ULONG ExtendableFile:1;
    ULONG Inherit:1;
    ULONG CopyOnWrite:1;
} MMVAD_FLAGS2, *PMMVAD_FLAGS2;
'''

#b1971ba0 (140) KTRAP_FRAME: KTRAP_FRAME
#b1971ba0 (04)   DbgEbp: 0xb1971c1c (2979470364)
#b1971ba4 (04)   DbgEip: 0x80536e9e (2152951454)
#b1971ba8 (04)   DbgArgMark: 0xbadb0d00 (3134917888)
#b1971bac (04)   DbgArgPointer: 0x00000002 (2)
#b1971bb0 (04)   TempSegCs: 0xe1371848 (3778484296)
#b1971bb4 (04)   TempEsp: 0x00000000 (0)
#b1971bb8 (04)   Dr0: 0x8212f810 (2182281232)
#b1971bbc (04)   Dr1: 0x00000000 (0)
#b1971bc0 (04)   Dr2: 0x00000000 (0)
#b1971bc4 (04)   Dr3: 0xb1971c24 (2979470372)
#b1971bc8 (04)   Dr6: 0x8055b740 (2153101120)
#b1971bcc (04)   Dr7: 0x805453e1 (2153010145)
#b1971bd0 (04)   SegGs: 0x00000000 (0)
#b1971bd4 (04)   SegEs: 0x00000023 (35)
#b1971bd8 (04)   SegDs: 0x00000023 (35)
#b1971bdc (04)   Edx: 0x00000002 (2)
#b1971be0 (04)   Ecx: 0x00000000 (0)
#b1971be4 (04)   Eax: 0xb1971c5c (2979470428)
#b1971be8 (04)   PreviousPreviousMode: 0xe1371848 (3778484296)
#b1971bec (04)   ExceptionList: 0xb1971c80 (2979470464)
#b1971bf0 (04)   SegFs: 0x00000030 (48)
#b1971bf4 (04)   Edi: 0x00000000 (0)
#b1971bf8 (04)   Esi: 0xb1971c64 (2979470436)
#b1971bfc (04)   Ebx: 0x00000000 (0)
#b1971c00 (04)   Ebp: 0xb1971c1c (2979470364)
#b1971c04 (04)   ErrCode: 0x00000002 (2)
#b1971c08 (04)   Eip: 0x80536e9e (2152951454)
#b1971c0c (04)   SegCs: 0x00000008 (8)
#b1971c10 (04)   EFlags: 0x00010293 (66195)
#b1971c14 (04)   HardwareEsp: 0x82331648 (2184386120)
#b1971c18 (04)   HardwareSegSs: 0x00000002 (2)
#b1971c1c (04)   V86Es: 0xb1971c3c (2979470396)
#b1971c20 (04)   V86Ds: 0x8052819f (2152890783)
#b1971c24 (04)   V86Fs: 0x00000000 (0)
#b1971c28 (04)   V86Gs: 0xb1971c64 (2979470436)

def bugcheck(db, line):
    '''
    Analysze and print out the current state of a windows
    bugcheck ( blue screen ).

    Usage: bugcheck
    '''
    trace = db.getTrace()
    sp = trace.getStackCounter()
    pc = trace.getProgramCounter()
    sym = trace.getSymByAddr(pc)
    if sym is None:
        db.vprint('Not currently at known bugcheck entry: 0x%.8x' % pc)
        return

    db.vprint('')

    sig = trace.getMeta('PendingSignal')
    symname = str(sym)

    if symname == 'nt.KeBugCheck':
        db.vprint('KeBugCheck( 0x%.8x ) - %s' % (sig, getBugCheckName(sig)))
        db.vprint('(no further info available from KeBugCheck)')
        return

    if symname == 'nt.KeBugCheckEx':
        db.vprint('KeBugCheckEx( 0x%.8x ) - %s' % (sig, getBugCheckName(sig)))
        db.vprint('')
        # FIXME use calling convention / impapi?
        if sig == KERNEL_MODE_EXCEPTION_NOT_HANDLED:
            retaddr,stacksig,excode,exaddr,extrap = trace.readMemoryFormat(sp, '<5I')

            trap = trace.getStruct('nt.KTRAP_FRAME', extrap)
            #db.vprint( trap.tree(va=extrap) )
            #db.vprint('')
            segs1 = ( trap.SegDs, trap.V86Ds, trap.SegEs, trap.V86Es )
            segs2 = ( trap.SegFs, trap.V86Fs, trap.SegGs, trap.V86Gs )
            db.vprint('Segments:')
            db.vprint('ds=%.2d:0x%.8x es=%.2d:0x%.8x' % segs1 )
            db.vprint('fs=%.2d:0x%.8x gs=%.2d:0x%.8x' % segs2 )

            db.vprint('')
            db.vprint('Registers:')
            db.vprint('eax=0x%.8x ebx=0x%.8x ecx=0x%.8x edx=0x%.8x' % (trap.Eax,trap.Ebx,trap.Ecx,trap.Edx))
            db.vprint('esi=0x%.8x edi=0x%.8x ebp=0x%.8x esp=0x????????' % (trap.Esi,trap.Edi,trap.Ebp))

            db.vprint('')

            db.vprint('Exception Trace:')

            eip = exaddr
            ebp = trap.Ebp

            while True:

                args = []
                bpvalid = trace.isValidPointer(ebp)
                if bpvalid:
                    args = trace.readMemoryFormat(ebp + 8, '<6I')

                loopbp = ebp

                argstr = ' '.join([ ('0x%.8x' % a) for a in args ])

                framestr = '0x%.8x [0x%.8x] %s' % (eip,ebp,argstr)

                sym = trace.getSymByAddr(eip, exact=False)
                if sym is not None:
                    framestr += ' (%s + %d)' % (sym, eip - int(sym))

                db.vprint(framestr)

                if not bpvalid:
                    break

                ebp,eip = trace.readMemoryFormat(ebp, '<2I')

                if ebp == loopbp:
                    break

            sym = trace.getSymByAddr(exaddr, exact=False)
            db.vprint('')
            db.vprint('Exception Trap: 0x%.8x' % extrap)
            db.vprint('Exception Addr: 0x%.8x (%s + %d)' % (exaddr, sym, exaddr-int(sym)))
            db.vprint('Exception Code: 0x%.8x' % excode)
            db.vprint('Exception Inst: %r' % trace.parseOpcode(exaddr))

def ktrap(db, line):
    '''
    Parse a KTRAP_FRAME structure from the given memory address.

    Usage: ktrap <addr_expression>
    '''
    trace = db.getTrace()
    trapaddr = trace.parseExpression( line )
    trap = trace.getStruct('nt.KTRAP_FRAME', trapaddr)
    db.vprint( trap.tree(va=trapaddr) )

def ethread(db, line):
    '''
    Display the details for the ethreads.

    Usage: ethread [addrexpr]
    '''
    t = db.getTrace()
    kpcr = t.getStruct('nt.KPCR', va=t.getVariable('kpcr'))
    if not line:
        db.vprint('CurrentThread: 0x%.8x' % kpcr.PrcbData.CurrentThread)
        db.vprint('NextThread: 0x%.8x' % kpcr.PrcbData.CurrentThread)
        return
    va = t.parseExpression(line)
    ethread = t.getStruct('nt.ETHREAD',va=va)
    db.vprint(ethread.tree(va=va))

def vads(db,line):
    '''
    Walk and display the VADs from the specified root.

    Usage: vads <addrexpr>
    '''
    t = db.getTrace()
    if not line:
        return db.do_help('vads')

    vadroot = t.parseExpression(line)

    vads = list(walkVads(db,t,vadroot))
    vads.sort(cmp=lambda x,y: cmp(x[1].StartingVpn,y[1].StartingVpn))

    for va,vad in vads:
        start = vad.StartingVpn << t.getMeta('PAGE_SHIFT')
        end = vad.EndingVpn << t.getMeta('PAGE_SHIFT')
        flags = vad.u.LongFlags
        db.vprint('vad: 0x%.8x 0x%.8x-0x%.8x 0x%.8x' % (va,start,end,flags))

def walkVads(db,trace,vadroot):
    todo = [ (vadroot,trace.getStruct('nt.MMVAD_SHORT',va=vadroot)), ]
    while todo:
        va,vad = todo.pop()
        yield va,vad

        l = vad.LeftChild
        r = vad.RightChild

        if l: todo.append((l,trace.getStruct('nt.MMVAD_SHORT',va=l)))
        if r: todo.append((r,trace.getStruct('nt.MMVAD_SHORT',va=r)))

def walkEprocesses(db,trace):
    dbgdata64 = db.getRunCacheVar('KDDEBUGGER_DATA64')
    phead = dbgdata64.PsActiveProcessHead
    for va,obj in vt_winkern.walkListEntryHead(trace,phead,'nt.EPROCESS','ActiveProcessLinks'):
        yield va,obj

def walkEThreads(db,trace,listva):
    for va,obj in vt_winkern.walkListEntryHead(trace,listva,'nt.ETHREAD','ThreadListEntry'):
        yield va,obj

def walkHandleTables(db,trace,listva):
    for va,obj in vt_winkern.walkListEntry(trace,listva,'nt.HANDLE_TABLE','HandleTableList'):
        yield va,obj

def showeproc(db,trace,opts,eprocva,eproc):
    pname = ''.join([ chr(c[1]) for c in eproc.ImageFileName ]).strip('\x00')

    peb = eproc.Peb
    vadroot = eproc.VadRoot
    objtable = eproc.ObjectTable
    db.vprint('eprocess: 0x%.8x vad: 0x%.8x peb: 0x%.8x objs: 0x%.8x %s' % (eprocva, vadroot, peb, objtable, pname))

    if opts.dothreads:
        thead = eprocva + eproc.vsGetOffset('ThreadListHead')
        for eva,ethread in walkEThreads(db,trace,thead):
            db.vprint('  ethread: 0x%.8x' % eva)

    if opts.dohandles:
        thead = eprocva + eproc.vsGetOffset('ThreadListHead')
        for hva,htable in walkEThreads(db,trace,thead):
            db.vprint('  handle_table: 0x%.8x' % hva)

def eproc(db, line):
    '''
    Display the details for the eprocesses.

    Usage: eproc [addrexpr]
    '''
    argv = e_cli.splitargs(line)

    parser = optparse.OptionParser('eproc')
    parser.add_option('--name',dest='doname',default=None)
    parser.add_option('--threads',dest='dothreads',default=False,action='store_true')
    parser.add_option('--handles',dest='dohandles',default=False,action='store_true')
    parser.add_option('--objects',dest='doobjects',default=False,action='store_true')

    opts,argv = parser.parse_args(argv)

    t = db.getTrace()

    if argv:
        for expr in argv:
            eprocva = t.parseExpression(expr)
            eproc = t.getStruct('nt.EPROCESS',eprocva)
            showeproc(db,t,opts,eprocva,eproc)
        return

    dbgdata64 = db.getRunCacheVar('KDDEBUGGER_DATA64')

    phead = dbgdata64.PsActiveProcessHead
    for eprocva,eproc in walkEprocesses(db,t):
        if opts.doname:
            pname = ''.join([ chr(c[1]) for c in eproc.ImageFileName ]).strip('\x00').lower()
            if opts.doname.lower() != pname:
                continue

        showeproc(db,t,opts,eprocva,eproc)
        #pname = ''.join([ chr(c[1]) for c in eproc.ImageFileName ]).strip('\x00')
        #db.vprint('eprocess: 0x%.8x %s' % (eprocva, pname))
        #thead = eprocva + eproc.vsGetOffset('ThreadListHead')
        #for eva,ethread in walkEThreads(db,t,thead):
            #db.vprint('  ethread: 0x%.8x' % eva)

        #if pname == 'calc.exe':
            #mynext,myprev = t.readMemoryFormat(elist,'<II')
            #t.writeMemoryFormat(myprev, '<I', mynext)
            #t.writeMemoryFormat(mynext+4, '<I', myprev)

        #elist = t.readMemoryFormat(elist,'<I')[0]


    #kpcr = t.getStruct('nt.KPCR', va=t.getVariable('kpcr'))
    #ethread = t.getStruct('nt.ETHREAD', va=kpcr.PrcbData.CurrentThread)
    #print ethread.tree(va=kpcr.PrcbData.CurrentThread)
    #eprocfirst = ethread.ThreadsProcess
    #db.vprint('EPROC: 0x%.8x' % eprocfirst)
    #eproc = t.getStruct('nt.EPROCESS', va=eprocfirst)
    #print eproc.tree()
    #print eproc.ImageFileName
    #eproc.Pcb.
    #listoff = eproc.vsGetOffset(

    #va = t.parseExpression(line)
    #ethread = t.getStruct('nt.ETHREAD',va=va)
    #db.vprint(ethread.tree(va=va))

def pools(db,line):
    '''
    Display various information about the kernel allocation
    pools. ( Default lists the non-paged pools )

    Usage: pools [options]
    '''
    t = db.getTrace()

    dbgdata64va = t.getVariable('kddebuggerdata64')
    dbgdata64 = vt_winkern.KDDEBUGGER_DATA64()
    dbgdata64.vsParse(t.readMemory(dbgdata64va, len(dbgdata64)))

    s = dbgdata64.MmNonPagedPoolStart
    e = dbgdata64.MmNonPagedPoolEnd
    db.vprint('Non-Paged Pool: 0x%.8x - 0x%.8x (%d bytes)' % (s,e,(e-s)))
    nppool = dbgdata64.NonPagedPoolDescriptor
    pooldesc = t.getStruct('nt.POOL_DESCRIPTOR',va=nppool)
    #print(pooldesc.tree(va=nppool))

def _ctor_KDDEBUGGER_DATA64(db):
    t = db.getTrace()
    dbgdata64va = t.getVariable('kddebuggerdata64')
    dbgdata64 = vt_winkern.KDDEBUGGER_DATA64()
    dbgdata64.vsParse(t.readMemory(dbgdata64va, len(dbgdata64)))
    return dbgdata64

def vdbExtension(db, trace):
    db.registerCmdExtension(vads,subsys='winkern')
    db.registerCmdExtension(eproc,subsys='winkern')
    db.registerCmdExtension(ktrap,subsys='winkern')
    db.registerCmdExtension(pools,subsys='winkern')
    db.registerCmdExtension(bugcheck,subsys='winkern')
    db.registerCmdExtension(ethread,subsys='winkern')
    db.registerCmdExtension(v_ext_windows.pe,subsys='winkern')

    db.addRunCacheCtor('KDDEBUGGER_DATA64',_ctor_KDDEBUGGER_DATA64)

#bugcheck(db,'')
