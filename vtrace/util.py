# Copyright (C) 2007 Invisigoth - See LICENSE file for details

import logging
import hashlib
import collections

import vtrace
import vtrace.notifiers as v_notifiers
import vtrace.rmi as v_rmi

import envi
import envi.const as e_const
import envi.archs.i386 as e_i386
import envi.archs.amd64 as e_amd64


logger = logging.getLogger(__name__)


class TraceManager:
    """
    A trace-manager is a utility class to extend from when you may be dealing
    with multiple tracer objects.  It allows for persistant mode settings and
    persistent metadata as well as bundling a DistributedNotifier.  You may also
    extend from this to get auto-magic remote stuff for your managed traces.
    """
    def __init__(self, trace=None):
        self.trace = trace
        self.dnotif = v_notifiers.DistributedNotifier()
        self.modes = {}  # See docs for trace modes
        self.metadata = {}  # Like traces, but persistant

    def manageTrace(self, trace):
        """
        Set all the modes/meta/notifiers in this trace for management
        by this TraceManager.
        """
        self.trace = trace
        if vtrace.remote:
            trace.registerNotifier(vtrace.NOTIFY_ALL, v_rmi.getCallbackProxy(trace, self.dnotif))
        else:
            trace.registerNotifier(vtrace.NOTIFY_ALL, self.dnotif)

        for name, val in self.modes.items():
            trace.setMode(name, val)

        for name, val in self.metadata.items():
            trace.setMeta(name, val)

    def unManageTrace(self, trace):
        """
        Untie this trace manager from the trace.
        """
        if vtrace.remote:
            trace.deregisterNotifier(vtrace.NOTIFY_ALL, v_rmi.getCallbackProxy(trace, self.dnotif))
        else:
            trace.deregisterNotifier(vtrace.NOTIFY_ALL, self.dnotif)

    def setMode(self, name, value):
        if self.trace is not None:
            self.trace.setMode(name, value)
        self.modes[name] = value

    def getMode(self, name, default=False):
        if self.trace is not None:
            return self.trace.getMode(name, default)
        return self.modes.get(name, default)

    def setMeta(self, name, value):
        if self.trace is not None:
            self.trace.setMeta(name, value)
        self.metadata[name] = value

    def getMeta(self, name, default=None):
        if self.trace is not None:
            return self.trace.getMeta(name, default)
        return self.metadata.get(name, default)

    def registerNotifier(self, event, notif):
        self.dnotif.registerNotifier(event, notif)

    def deregisterNotifier(self, event, notif):
        self.dnotif.deregisterNotifier(event, notif)

    def fireLocalNotifiers(self, event, trace):
        """
        Deliver a local event to the DistributedNotifier managing
        the traces. (used to locally bump notifiers)
        """
        self.dnotif.notify(event, trace)


def emuFromTrace(trace):
    '''
    Produce an envi emulator for this tracer object.
    '''
    arch = trace.getMeta('Architecture')
    plat = trace.getMeta('Platform')
    amod = envi.getArchModule(arch)
    emu = amod.getEmulator()
    [emu.setMeta(key, val) for key, val in trace.metadata.items()]

    # could use {get,set}MemorySnap if trace inherited from MemoryObject
    for va, size, perms, fname in trace.getMemoryMaps():
        try:
            # So linux maps in a PROT_NONE page for efficient library sharing, so we have to take that into account
            if (not perms & e_const.MM_READ):
                continue
            if plat == 'linux' and fname in ['[vvar]']:
                continue
            bytez = trace.readMemory(va, size)
            emu.addMemoryMap(va, perms, fname, bytez)
        except vtrace.PlatformException:
            logger.warning('failed to map: 0x{:x} into emu'.format(va, size))
            continue

    rsnap = trace.getRegisterContext().getRegisterSnap()
    emu.setRegisterSnap(rsnap)

    if plat == 'windows':
        psize = trace.getPointerSize()
        # capture PEB and TIB
        peb = trace.getMeta('PEB')
        if hasattr(trace, 'win32threads'):
            tebs = dict(trace.win32threads)
            vw.setMeta('TEBs', tebs)
        else:
            metatebs = trace.getMeta('TEBs')
            if metatebs:
                vw.setMeta('TEBs', tebs)

        emu.setMeta('PEB', peb)

        seginfo = trace.getThreads()[trace.getMeta('ThreadId')]
        if psize == 4:
            emu.setSegmentInfo(e_i386.SEG_FS, seginfo, 0xffffffff)
        elif psize == 8:
            emu.setSegmentInfo(e_amd64.SEG_GS, seginfo, 0xffffffffffff)

    return emu


def vwFromTrace(trace, storagename='binary_workspace_from_vsnap.viv', filefmt=None, collapse=True, strict=True):
    '''
    Produce an envi emulator for this tracer object.

    If filefmt is None, it will be auto-determined

    If collapse, join adjacent maps
    If strict, only join maps with the same permissions
    '''
    import vivisect
    vw = vivisect.VivWorkspace()
    arch = trace.getMeta('Architecture')
    plat = trace.getMeta('Platform')
    psize = trace.getPointerSize()

    # determine file format (if not specified above)
    if filefmt is None:
        if 'win' in plat.lower():
            filefmt = 'pe'
            from vivisect.parsers.pe import archcalls
        else:
            filefmt = 'elf'
            from vivisect.parsers.elf import archcalls

    vw.setMeta("Architecture", arch)
    vw.setMeta("Platform", plat)
    vw.setMeta('Format', filefmt)
    vw.setMeta('DefaultCall', archcalls.get(arch,'unknown'))
    vw.setMeta('StorageName', storagename)
    
    if 'win' in plat.lower():
        ossep = '\\'
        exts = ('exe', 'dll')

    else:
        ossep = '/'
        exts = ('so')

    # could use {get,set}MemorySnap if trace inherited from MemoryObject
    maps = []
    fnames = collections.defaultdict(int)
    filemeta = collections.defaultdict(hashlib.md5)

    for va, size, perms, fname in trace.getMemoryMaps():
        # strip off unwanted parts
        trimfname = fname.split(ossep)[-1]
        stripfname = trimfname
        for ext in exts:
            if trimfname.endswith('.' + ext):
                stripfname = trimfname[:-(len(ext) + 1)]

        # add map to the workspace
        try:
            # So linux maps in a PROT_NONE page for efficient library sharing, so we have to take that into account
            if (not perms & e_const.MM_READ):
                continue
            if plat == 'linux' and stripfname in ['[vvar]']:
                continue
            bytez = trace.readMemory(va, size)
            maps.append((va, perms, stripfname, bytez))

        except vtrace.PlatformException:
            logger.warning('failed to map: 0x{:x} into emu'.format(va, size))
            continue

    # filter maps
    if collapse:
        maps = collapseMemoryMaps(maps, strict=strict)

    # add maps
    for midx, (va, perms, fname, bytez) in enumerate(maps):
        count = fnames.get(fname, 0)
        fnames[fname] = count + 1

        vw.addMemoryMap(va, perms, fname, bytez)
        vw.addSegment(va, len(bytez), "%s_%d" % (fname, count), fname)
        filemeta[fname].update(bytez)

    # now actually add the files
    for fname in filemeta.keys():
        # find first va:
        for va, perms, mnm, btz in maps:
            if mnm == fname:
                break

        vw.addFile(fname, va, filemeta[fname].hexdigest())

    # windows stuff
    if plat == 'windows':
        # capture PEB and TIB
        peb = trace.getMeta('PEB')
        if hasattr(trace, 'win32threads'):
            tebs = dict(trace.win32threads)
            vw.setMeta('TEBs', tebs)
        else:
            metatebs = trace.getMeta('TEBs')
            if metatebs:
                vw.setMeta('TEBs', metatebs)

        vw.setMeta('PEB', peb)

    return vw


def collapseMemoryMaps(oldmaps, strict=True):
    '''
    Sort through a list of memory maps and collapse any which abutt.
    If strict, only collapse if the permissions are the same.
    Otherwise, collapse them and or the permissions together.

    TODO: make all map bytes collapsed and make maps start at an offset?
        or poss
    '''
    # if we have no maps, skip the whole process
    if not len(oldmaps):
        return

    oldmaps.sort()

    # start off with the current map as the first oldmap, and add it
    newmaps = [oldmaps[0]]
    curva, curperms, curfname, curbytez = oldmaps[0]
    cursz = len(curbytez)
    curvamax = curva + cursz
    logger.debug("initial map: 0x%x, perms:%x, %r, %d-bytes, curvamax: 0x%x", curva, curperms, curfname, cursz, curvamax)

    for omidx in range(1, len(oldmaps)):
        ova, operms, ofname, obytez = oldmaps[omidx]
        omsz = len(obytez)
        ovamax = ova + omsz
        logger.debug("next map: 0x%x, perms:%x, %r, %d-bytes, curvamax: 0x%x", ova, operms, ofname, omsz, ovamax)
        if ova == curvamax and curfname == ofname and (not strict or curperms == operms):
            # collapse this into previous and update curvamax and curbytes if perms or not strict
            curvamax = ovamax
            newfname = None
            if len(curfname):
                if len(ofname) and ofname != curfname:
                    newfname = '%s + %s' % (curfname, ofname)
                else:
                    newfname = curfname
            else:
                newfname = ofname

            curbytez += obytez
            curfname = newfname
            newmaps[-1] = curva, curperms, newfname, curbytez
            logger.debug("collapsing: initial map: 0x%x, perms:%x, %r, %d-bytes, curvamax: 0x%x", \
                    curva, curperms, curfname, cursz, curvamax)

        else:
            #logger.debug("ova (0x%x) != curvamax (0x%x) or curperms (%r) != operms (%r)", ova, curvamax, curperms, operms)
            # add this map to newmaps and update cur*
            newmaps.append(oldmaps[omidx])
            curva, curperms, curfname, curbytez = oldmaps[omidx]
            cursz = len(curbytez)
            curvamax = curva + cursz

    return newmaps

