"""

Yay!  It's NOT IDA!!!1!!1!one!

"""

import os
import re
import sys
import time
import queue
import string
import hashlib
import logging
import itertools
import traceback
import threading
import collections


import envi
import envi.exc as e_exc
import envi.bits as e_bits
import envi.common as e_common
import envi.memory as e_mem
import envi.config as e_config
import envi.bytesig as e_bytesig
import envi.symstore.resolver as e_resolv
import envi.symstore.symcache as e_symcache

import vstruct
import vstruct.cparse as vs_cparse
import vstruct.primitives as vs_prims

import vivisect.base as viv_base
import vivisect.parsers as viv_parsers
import vivisect.codegraph as viv_codegraph
import vivisect.impemu.lookup as viv_imp_lookup

from vivisect.exc import *
from vivisect.const import *
from vivisect.defconfig import *

import vivisect.analysis.generic.emucode as v_emucode

logger = logging.getLogger(__name__)

STOP_LOCS = (LOC_STRING, LOC_UNI, LOC_STRUCT, LOC_CLSID, LOC_VFTABLE, LOC_IMPORT, LOC_PAD, LOC_NUMBER)
STORAGE_MAP = {
    'viv': 'vivisect.storage.basicfile',
    'mpviv': 'vivisect.storage.mpfile',
}


def guid(size=16):
    return e_common.hexify(os.urandom(size))


class VivWorkspace(e_mem.MemoryObject, viv_base.VivWorkspaceCore):
    '''
    VivWorkspace is the heart of vivisect's binary analysis. Most APIs accept a VivWorkspace
    as their first parameter, and the workspace is responsible for all the user facing functions
    of getters/adders, running analysis passes, making the various locations, loading files, and
    more.

    Current keyword arguments:
    * confdir:
      * Type: String (path to directory)
      * Description: A path to a directory to save/load vivisect's analysis configuration options (options will be saved to/loaded from the viv.json file in the directory
      * Default: $HOME/.viv/
    * autosave (boolean):
      * Type: Boolean
      * Description: If true, autosave any configuration changes to the <confdir>/viv.json upon changing them.
      * Default: False
    '''
    def __init__(self, **kwargs):

        e_mem.MemoryObject.__init__(self)
        viv_base.VivWorkspaceCore.__init__(self)

        autosave = kwargs.get('autosave', False)
        cfgdir = kwargs.get('confdir', None)
        if cfgdir:
            self.vivhome = os.path.abspath(cfgdir)
        else:
            self.vivhome = e_config.gethomedir(".viv", makedir=autosave)
        self._viv_gui = None    # If a gui is running, he will put a ref here...
        self._ext_ctxmenu_hooks = {}
        self._extensions = {}

        self.saved = False  # TODO: Have a warning when we try to close the UI if the workspace hasn't been saved
        self.rchan = None
        self.server = None
        self.chanids = itertools.count()

        self.arch = None  # The placeholder for the Envi architecture module
        self.psize = None  # Used so much, optimization is appropriate

        cfgpath = os.path.join(self.vivhome, 'viv.json')
        self.config = e_config.EnviConfig(filename=cfgpath, defaults=defconfig, docs=docconfig, autosave=autosave)

        # Ideally, *none* of these are modified except by _handleFOO funcs...
        self.segments = []
        self.exports = []
        self.imports = []
        self.codeblocks = []
        self.relocations = []
        self._dead_data = []
        self.iscode = {}

        self.xrefs = []
        self.xrefs_by_to = {}
        self.xrefs_by_from = {}

        # XXX - make config option
        self.greedycode = 0

        self.metadata = {}
        self.comments = {}  # Comment by VA.
        self.symhints = {}

        self.filemeta = {}  # Metadata Dicts stored by filename
        self.transmeta = {}  # Metadata that is *not* saved/evented

        self.cfctx = viv_base.VivCodeFlowContext(self)

        self.va_by_name = {}
        self.name_by_va = {}
        self.codeblocks_by_funcva = {}
        self.exports_by_va = {}
        self.colormaps = {}
        self.vasetdefs = {}
        self.vasets = {}
        self.reloc_by_va = {}

        self.func_args = {}
        self.funcmeta = {}  # Function metadata stored in the workspace
        self.frefs = {}

        # Extended analysis modules
        self.amods = {}
        self.amodlist = []
        # Extended *function* analysis modules
        self.fmods = {}
        self.fmodlist = []

        self.chan_lookup = {}
        self.nextchanid = 1

        self._cached_emus = {}

        # The function entry signature decision tree
        # FIXME add to export
        self.sigtree = e_bytesig.SignatureTree()
        self.siglist = []

        self._op_cache = {}

        self._initEventHandlers()

        # Some core meta types that exist
        self.setMeta('NoReturnApis', {})
        self.setMeta('SymbolikImportEmulation', None)

        # Default to basic file storage
        self.setMeta("StorageModule", "vivisect.storage.basicfile")

        # There are a few default va sets for use in analysis
        self.addVaSet('EntryPoints', (('va', VASET_ADDRESS),))
        self.addVaSet('NoReturnCalls', (('va', VASET_ADDRESS),))
        self.addVaSet("Emulation Anomalies", (("va", VASET_ADDRESS), ("Message", VASET_STRING)))
        self.addVaSet("Bookmarks", (("va", VASET_ADDRESS), ("Bookmark Name", VASET_STRING)))
        self.addVaSet('DynamicBranches', (('va', VASET_ADDRESS), ('opcode', VASET_STRING), ('bflags', VASET_INTEGER)))
        self.addVaSet('SwitchCases', (('va', VASET_ADDRESS), ('setup_va', VASET_ADDRESS), ('Cases', VASET_INTEGER)))
        self.addVaSet('PointersFromFile', (('va', VASET_ADDRESS), ('target', VASET_ADDRESS), ('file', VASET_STRING), ('comment', VASET_STRING), ))
        self.addVaSet('CodeFragments', (('va', VASET_ADDRESS), ('calls_from', VASET_COMPLEX)))
        self.addVaSet('EmucodeFunctions', (('va', VASET_ADDRESS),))
        self.addVaSet('FuncWrappers', (('va', VASET_ADDRESS), ('wrapped_va', VASET_ADDRESS),))

    def vprint(self, msg):
        logger.info(msg)

    def getVivGui(self):
        '''
        Return a reference to the vivisect GUI object for this workspace.  If
        the GUI is not running (aka, the workspace is being used programatically)
        this routine returns None.

        Example:
            vwgui = vw.getVivGui()
            if vwgui:
                vwgui.doStuffAndThings()
        '''
        return self._viv_gui

    def getPointerSize(self):
        return self.psize

    def addCtxMenuHook(self, name, handler):
        '''
        Extensions can add Context Menu hooks to modify the menu as they wish.
        This would most often happen from the Extension's vivExtension() init function.
        see vivisect.qt.ctxmenu for more details

        handler should have the following prototype (inc. example code):


        from vqt.common import ACT
        def myExtCtxMenuHandler(vw, menu):
            toymenu = menu.addMenu('myToys')
            toymenu.addAction('Voodoo Wizbang ZeroDay Finder Thingy', ACT(doCoolShit, vw, va))

        Currently, this should live in a loaded module, not in your Viv Extension's main py file.
        '''
        if name in self._ext_ctxmenu_hooks:
            cur = self._ext_ctxmenu_hooks[name]
            logger.warning("Attempting to hook the context menu: %r is already registered \
                    (cur: %r new: %r)", name, cur, handler)
            return

        self._ext_ctxmenu_hooks[name] = handler

    def delCtxMenuHook(self, name):
        '''
        Remove a context-menu hook that has been installed by an extension
        '''
        self._ext_ctxmenu_hooks.pop(name, None)

    def addExtension(self, name, extmod):
        '''
        Add extension module to a list of extensions.
        This keeps a list of installed extension modules, with the added value
        of keeping the loaded module in memory.
        '''
        if name in self._extensions:
            cur = self._extensions[name]
            logger.warning("Attempting to register an extension: %r is already registered \
                    (cur: %r new: %r)", name, cur, handler)
            return

        self._extensions[name] = extmod

    def delExtension(self, name):
        '''
        Remove's extension module from the list of extensions.
        '''
        self._extensions.pop(name, None)

    def getVivGuid(self):
        '''
        Return the GUID for this workspace.  Every newly created VivWorkspace
        should have a unique GUID, for identifying a particular workspace for
        a given binary/process-space versus another created at a different
        time.  Filesystem-copies of the same workspace will have the same GUID
        by design.  This easily allows for workspace-specific GUI layouts as
        well as comparisons of Server-based workspaces to the original file-
        based workspace used to store to the server.
        '''
        vivGuid = self.getMeta('GUID')
        if vivGuid is None:
            vivGuid = guid()
            self.setMeta('GUID', vivGuid)

        return vivGuid

    def loadWorkspace(self, wsname):
        mname = self.getMeta("StorageModule")
        mod = self.loadModule(mname)
        mod.loadWorkspace(self, wsname)
        self.setMeta("StorageName", wsname)
        # The event list thusfar came *only* from the load...
        self._createSaveMark()
        # Snapin our analysis modules
        self._snapInAnalysisModules()

    def addFref(self, fva, va, idx, val):
        """
        Add a reference from the operand at virtual address 'va'
        index 'idx' to a function local offset.  Positive values
        (beginning with 0) are considered argument references.  Negative
        values are considered function local storage and are relative to
        the stack pointer at function entry.
        """
        # FIXME this should probably be an argument
        r = (va, idx, val)
        self._fireEvent(VWE_ADDFREF, r)

    def getFref(self, va, idx):
        """
        Get back the fref value (or None) for the given operand index
        from the instruction at va.
        """
        return self.frefs.get((va, idx))

    def getEmulator(self, **kwargs):
        """
        Get an instance of a WorkspaceEmulator for this workspace.

        Use logread/logwrite to enable memory access tracking.
        """
        plat = self.getMeta('Platform')
        arch = self.getMeta('Architecture')

        eclass = viv_imp_lookup.workspace_emus.get((plat, arch))
        if eclass is None:
            eclass = viv_imp_lookup.workspace_emus.get(arch)

        if eclass is None:
            raise Exception("WorkspaceEmulation not supported on %s yet!" % arch)

        emu = eclass(self, **kwargs)
        emu.setEndian(self.getEndian())

        return emu

    def getCachedEmu(self, emuname):
        """
        Get a cached emulator by name. If one doesn't exist it is
        created and then cached.
        """

        emu = self._cached_emus.get(emuname)
        if emu is None:
            emu = self.getEmulator()
            self._cached_emus[emuname] = emu
        return emu

    def addLibraryDependancy(self, libname):
        """
        Add a *normalized* library name to the import search
        chain for this binary.  This is only needed for formats
        whose imports don't explicitly state their library name.
        """
        # FIXME this needs to be event enabled... either plumb it special,
        # or allow the get/append/set race...
        dl = self.getMeta("DepLibs", None)
        if dl is None:
            dl = []
        dl.append(libname)
        self.setMeta("DepLibs", dl)

    def getLibraryDependancies(self):
        '''
        Retrieve the list of *normalized* library dependancies.
        '''
        dl = self.getMeta("DepLibs", None)
        if dl is None:
            return []
        return list(dl)

    def setComment(self, va, comment, check=False):
        '''
        Set the humon readable comment for a given virtual.
        Comments will be displayed by the code renderer, and
        are an important part of this balanced breakfast.

        Example:
            vw.setComment(callva, "This actually calls FOO...")
        '''
        if check and self.comments.get(va):
            return
        self._fireEvent(VWE_COMMENT, (va, comment))

    def getComment(self, va):
        '''
        Returns the comment string (or None) for a given
        virtual address.

        Example:
            cmnt = vw.getComment(va)
            print('COMMENT: %s' % cmnt)
        '''
        return self.comments.get(va)

    def getComments(self):
        '''
        Retrieve all the comments in the viv workspace as
        (va, cmnt) tuples.

        Example:
            for va,cmnt in vw.getComments():
                print('Comment at 0x%.8x: %s' % (va, cmnt))
        '''
        return list(self.comments.items())

    def addRelocation(self, va, rtype, data=None):
        """
        Add a relocation entry for tracking.
        Expects data to have whatever is necessary for the reloc type. eg. addend
        """
        # split "current" va into fname and offset.  future relocations will want to base all va's from an image base
        mmva, mmsz, mmperm, fname = self.getMemoryMap(va)    # FIXME: getFileByVa does not obey file defs
        imgbase = self.getFileMeta(fname, 'imagebase')
        offset = va - imgbase

        self._fireEvent(VWE_ADDRELOC, (fname, offset, rtype, data))

    def getRelocations(self):
        """
        Get the current list of relocation entries.
        """
        return self.relocations

    def getRelocation(self, va):
        """
        Return the type of relocation at the specified
        VA or None if there isn't a relocation entry for
        the address.
        """
        return self.reloc_by_va.get(va)

    def pointerString(self, va):
        return self.arch.pointerString(va)

    def getAnalysisModuleNames(self):
        return list(self.amodlist)

    def getFuncAnalysisModuleNames(self):
        return list(self.fmodlist)

    def addFunctionSignatureBytes(self, bytez, mask=None):
        """
        Add a function signature entry by bytes.  This is mostly used by
        file parsers/loaders to manually tell the workspace about known
        entry signature types.

        see envi.bytesig for details.
        """
        self.sigtree.addSignature(bytez, mask)
        self.siglist.append((bytez, mask))

    def isFunctionSignature(self, va):
        """
        Check if the specified va is a function entry signature
        according to the current entry point signature tree...
        """
        if not self.isValidPointer(va):
            return False
        offset, bytes = self.getByteDef(va)
        return self.sigtree.isSignature(bytes, offset=offset)

    def addNoReturnVa(self, va):
        noretva = self.getMeta('NoReturnApisVa', {})
        noretva[va] = True
        self.setMeta('NoReturnApisVa', noretva)

        self.cfctx.addNoReturnAddr(va)

    def addNoReturnApi(self, funcname):
        """
        Inform vivisect code-flow disassembly that any call target
        which matches the specified name ("funcname" or "libname.funcname"
        for imports) does *not* exit and code-flow should be stopped...
        """
        funcname = funcname.lower()
        m = self.getMeta('NoReturnApis', {})
        m[funcname] = True
        self.setMeta('NoReturnApis', m)

        noretva = self.getMeta('NoReturnApisVa', {})

        # If we already have an import entry, we need to update codeflow
        for lva, lsize, ltype, linfo in self.getImports():
            if linfo.lower() != funcname:
                continue
            self.cfctx.addNoReturnAddr(lva)
            noretva[lva] = True
        self.setMeta('NoReturnApisVa', noretva)

    def addNoReturnApiRegex(self, funcre):
        '''
        Inform vivisect code-flow disassembly that any call target
        which matches the specified regex ("funcname" or "libname.funcname"
        for imports) does *not* exit and code-flow should be stopped...
        '''
        c = re.compile(funcre, re.IGNORECASE)
        m = self.getMeta('NoReturnApisRegex', [])
        m.append(funcre)
        self.setMeta('NoReturnApisRegex', m)

        for lva, lsize, ltype, linfo in self.getImports():
            if c.match(linfo):
                self.addNoReturnApi(linfo)

    def isNoReturnVa(self, va):
        '''
        Check if a VA is a no return API
        '''
        isva = self.getMeta('NoReturnApisVa', {}).get(va, False)
        iscall = self.getVaSetRow('NoReturnCalls', va) is not None
        return isva or iscall

    def checkNoRetApi(self, apiname, va):
        '''
        Called as new APIs (thunks) are discovered, checks to see
        if they wrap a NoReturnApi. Updates if it is a no ret API thunk
        '''
        noretva = self.getMeta('NoReturnApisVa', {})

        for funcre in self.getMeta('NoReturnApisRegex', []):
            c = re.compile(funcre, re.IGNORECASE)
            if c.match(apiname):
                self.cfctx.addNoReturnAddr(va)
                noretva[va] = True

        for funcname in self.getMeta('NoReturnApis', {}).keys():
            if funcname.lower() == apiname.lower():
                self.cfctx.addNoReturnAddr(va)
                noretva[va] = True

        self.setMeta('NoReturnApisVa', noretva)

    def addAnalysisModule(self, modname):
        """
        Add an analysis module by python import path
        """
        if modname in self.amods:
            return
        mod = self.loadModule(modname)
        self.amods[modname] = mod
        self.amodlist.append(modname)
        logger.debug('Adding Analysis Module: %s', modname)

    def delAnalysisModule(self, modname):
        """
        Remove an analysis module from the list used during analysis()
        """
        if modname not in self.amods:
            raise Exception("Unknown Module in delAnalysisModule: %s" % modname)
        x = self.amods.pop(modname, None)
        if x is not None:
            self.amodlist.remove(modname)

    def loadModule(self, modname):
        __import__(modname)
        return sys.modules[modname]

    def addFuncAnalysisModule(self, modname):
        """
        Snap in a per-function analysis module (by name) which
        will be triggered during the creation of a new function
        (makeFunction).
        """
        if modname in self.fmods:
            return
        mod = self.loadModule(modname)
        self.fmods[modname] = mod
        self.fmodlist.append(modname)
        logger.debug('Adding Function Analysis Module: %s', modname)

    def delFuncAnalysisModule(self, modname):
        '''
        Remove a currently registered function analysis module.

        Example:
            vw.delFuncAnalysisModule('mypkg.mymod')
        '''
        x = self.fmods.pop(modname, None)
        if x is None:
            raise Exception("Unknown Module in delAnalysisModule: %s" % modname)
        self.fmodlist.remove(modname)

    def createEventChannel(self):
        chanid = next(self.chanids)
        self.chan_lookup[chanid] = queue.Queue()
        return chanid

    def importWorkspace(self, wsevents):
        """
        Import and initialize data from the given vivisect workspace
        export.
        """
        # During import, if we have a server, be sure not to notify
        # the server about the events he just gave us...
        local = False
        if self.server is not None:
            local = True

        # Process the events from the import data...
        fe = self._fireEvent
        for event, einfo in wsevents:
            fe(event, einfo, local=local)
        return

    def exportWorkspace(self):
        '''
        Return the (probably big) list of events which define this
        workspace.
        '''
        return self._event_list

    def exportWorkspaceChanges(self):
        '''
        Export the list of events which have been applied to the
        workspace since the last save.
        '''
        return self._event_list[self._event_saved:]

    def initWorkspaceClient(self, remotevw):
        """
        Initialize this workspace as a workspace
        client to the given (potentially cobra remote)
        workspace object.
        """
        uname = e_config.getusername()
        self.server = remotevw
        self.rchan = remotevw.createEventChannel()

        self.server.vprint('%s connecting...' % uname)
        wsevents = self.server.exportWorkspace()
        self.importWorkspace(wsevents)
        self.server.vprint('%s connection complete!' % uname)

        thr = threading.Thread(target=self._clientThread)
        thr.setDaemon(True)
        thr.start()

    def _clientThread(self):
        """
        The thread that monitors events on a server to stay
        in sync.
        """
        if self.server is None:
            raise Exception("_clientThread() with no server?!?!")

        while self.server is not None:
            event, einfo = self.server.waitForEvent(self.rchan)
            self._fireEvent(event, einfo, local=True)

    def waitForEvent(self, chanid, timeout=None):
        """
        Return an event,eventinfo tuple.
        """
        q = self.chan_lookup.get(chanid)
        if q is None:
            raise Exception("Invalid Channel")
        return q.get(timeout=timeout)

    def deleteEventChannel(self, chanid):
        """
        Remove a previously allocated event channel from
        the workspace.
        """
        self.chan_lookup.pop(chanid)

    def reprPointer(vw, va):
        """
        Do your best to create a humon readable name for the
        value of this pointer.

        note: This differs from parent function from envi.cli:
        * Locations database is checked
        * Strings are returned, not named (partially)
        * <function> + 0x<offset> is returned if inside a function
        * <filename> + 0x<offset> is returned instead of loc_#####
        """
        if va == 0:
            return "NULL"

        loc = vw.getLocation(va)
        if loc is not None:
            locva, locsz, lt, ltinfo = loc
            if lt in (LOC_STRING, LOC_UNI):
                return vw.reprVa(locva)

        mbase, msize, mperm, mfile = vw.getMemoryMap(va)
        ret = mfile + " + 0x%x" % (va - mbase)

        sym = vw.getName(va, smart=True)
        if sym is not None:
            ret = sym
        return ret

    def reprVa(self, va):
        """
        A quick way for scripts to get a string for a given virtual address.
        """
        loc = self.getLocation(va)
        if loc is not None:
            return self.reprLocation(loc)
        return "None"

    def reprLocation(self, loctup):
        if loctup is None:
            return 'no loc info'

        lva,lsize,ltype,tinfo = loctup
        if ltype == LOC_OP:
            op = self.parseOpcode(lva, arch=tinfo & envi.ARCH_MASK)
            return repr(op)

        elif ltype == LOC_STRING:
            return repr(self.readMemory(lva, lsize).decode('utf-8'))

        elif ltype == LOC_UNI:
            # FIXME super ghetto "simple" unicode handling for now
            bytes = b''.join(self.readMemory(lva, lsize).split(b'\x00'))
            try:
                return f"u'%s'" % bytes.decode('utf-8')
            except:
                return bytes.hex()

        elif ltype == LOC_STRUCT:
            lstruct = self.getStructure(lva, tinfo)
            return repr(lstruct)

        elif ltype == LOC_NUMBER:
            value = self.parseNumber(lva, lsize)
            hexstr = "0x%%.%dx" % lsize
            hexstr = hexstr % value
            if lsize == 1:
                return "BYTE: %d (%s)" % (value, hexstr)
            else:
                return "%d BYTES: %d (%s)" % (lsize, value, hexstr)

        elif ltype == LOC_IMPORT:
            return "IMPORT: %s" % tinfo

        elif ltype == LOC_POINTER:
            return "PTR: %s" % self.arch.pointerString(self.getXrefsFrom(lva)[0][XR_TO])

        else:
            n = self.getName(lva)
            if n is not None:
                return n
            return e_common.hexify(self.readMemory(lva, lsize))

    def followPointer(self, va):
        """
        Do pointer analysis and folllow up the recomendation
        by creating locations etc...
        """
        ltype = self.analyzePointer(va)
        if ltype is None:
            return False

        # Note, we only implement the types possibly
        # returned from analyzePointer...
        if ltype == LOC_OP:
            # NOTE: currently analyzePointer returns LOC_OP
            # based on function entries, lets make a func too...
            logger.debug('discovered new function (followPointer(0x%x))', va)
            self.makeFunction(va)
            return True

        elif ltype == LOC_STRING:
            self.makeString(va)
            return True

        elif ltype == LOC_UNI:
            self.makeUnicode(va)
            return True

        return False

    def processEntryPoints(self):
        '''
        Roll through EntryPoints and make them into functions (if not already)
        '''
        for eva in self.getEntryPoints():
            if self.isFunction(eva):
                continue
            if not self.probeMemory(eva, 1, e_mem.MM_EXEC):
                continue
            logger.debug('processEntryPoint: 0x%x', eva)
            self.makeFunction(eva)

    def analyze(self):
        """
        Call this to ask any available analysis modules
        to do their thing...
        """
        self.vprint('Beginning analysis...')

        starttime = time.time()
        # Now lets engage any analysis modules.  If any modules return
        # true, they managed to change things and we should run again...
        for mname in self.amodlist:
            mod = self.amods.get(mname)
            self.vprint("Extended Analysis: %s" % mod.__name__)
            try:
                mod.analyze(self)
            except Exception as e:
                self.vprint("Extended Analysis Exception %s: %s" % (mod.__name__, e))

        endtime = time.time()
        self.vprint('...analysis complete! (%d sec)' % (endtime-starttime))
        self.printDiscoveredStats()
        self._fireEvent(VWE_AUTOANALFIN, (endtime, starttime))

    def analyzeFunction(self, fva):
        for fmname in self.fmodlist:
            fmod = self.fmods.get(fmname)
            try:
                fmod.analyzeFunction(self, fva)
            except Exception as e:
                self.vprint("Function Analysis Exception for function 0x%x, module: %s" % (fva, fmod.__name__))
                self.vprint("Exception Traceback: %s" % traceback.format_exc())
                self.setFunctionMeta(fva, "%s fail" % fmod.__name__, traceback.format_exc())

    def getStats(self):
        stats = {
            'functions': len(self.funcmeta),
            'relocations': len(self.relocations),
        }
        return stats

    def printDiscoveredStats(self):
        (disc,
         undisc,
         numXrefs,
         numLocs,
         numFuncs,
         numBlocks,
         numOps,
         numUnis,
         numStrings,
         numNumbers,
         numPointers,
         numVtables) = self.getDiscoveredInfo()

        percentage = disc*100.0/(disc+undisc) if disc or undisc else 0
        self.vprint("Percentage of discovered executable surface area: %.1f%% (%s / %s)" % (percentage, disc, disc+undisc))
        self.vprint("   Xrefs/Blocks/Funcs:                             (%s / %s / %s)" % (numXrefs, numBlocks, numFuncs))
        self.vprint("   Locs,  Ops/Strings/Unicode/Nums/Ptrs/Vtables:   (%s:  %s / %s / %s / %s / %s / %s)" % (numLocs, numOps, numStrings, numUnis, numNumbers, numPointers, numVtables))

    def getDiscoveredInfo(self):
        """
        Returns tuple of ( bytes_with_locations, bytes_without_locations ) for all executable maps.
        """
        disc = 0
        undisc = 0
        for mva, msz, mperms, mname in self.getMemoryMaps():
            if not self.isExecutable(mva):
                continue

            off = 0
            while off < msz:
                loc = self.getLocation(mva+off)
                if loc is None:
                    off += 1
                    undisc += 1
                else:
                    off += loc[L_SIZE]
                    disc += loc[L_SIZE]

        numXrefs = len(self.getXrefs())
        numLocs = len(self.getLocations())
        numFuncs = len(self.getFunctions())
        numBlocks = len(self.getCodeBlocks())
        numOps = len(self.getLocations(LOC_OP))
        numUnis = len(self.getLocations(LOC_UNI))
        numStrings = len(self.getLocations(LOC_STRING))
        numNumbers = len(self.getLocations(LOC_NUMBER))
        numPointers = len(self.getLocations(LOC_POINTER))
        numVtables = len(self.getLocations(LOC_VFTABLE))

        return disc, undisc, numXrefs, numLocs, numFuncs, numBlocks, numOps, numUnis, numStrings, numNumbers, numPointers, numVtables

    def getImports(self):
        """
        Return a list of imports, including delay imports, in location tuple format.
        """
        return list(self.getLocations(LOC_IMPORT))

    def makeImport(self, va, libname, impname):
        """
        Add an import entry.
        """
        if libname != '*':
            libname = self.normFileName(libname)
        tinfo = "%s.%s" % (libname, impname)
        self.makeName(va, "%s_%.8x" % (tinfo, va))
        return self.addLocation(va, self.psize, LOC_IMPORT, tinfo=tinfo)

    def getExports(self):
        """
        Return a list of exports in (va,etype,name,filename) tuples.
        """
        return list(self.exports)

    def addExport(self, va, etype, name, filename, makeuniq=False):
        """
        Add an already created export object.

        makeuniq allows Vivisect to append some number to make the name unique.
        This behavior allows for colliding names (eg. different versions of a function)
        to coexist in the same workspace.
        """
        rname = "%s.%s" % (filename,name)

        # check if it exists and is *not* what we're trying to make it
        curval = self.vaByName(rname)

        if curval is not None and curval != va and not makeuniq:
            # if we don't force it to make a uniq name, bail
            raise Exception("Duplicate Name: %s => 0x%x  (cur: 0x%x)" % (rname, va, curval))

        rname = self.makeName(va, rname, makeuniq=makeuniq)
        self._fireEvent(VWE_ADDEXPORT, (va,etype,name,filename))

    def getExport(self, va):
        """
        Get a reference to the export object at the given va
        (or none).
        """
        return self.exports_by_va.get(va)

    def findPointers(self, cache=True):
        """
        Search through all currently "undefined" space and see
        if you can find pointers there...  Returns a list of tuples
        where the tuple is (<ptr at>,<pts to>).
        """
        align = self.arch.archGetPointerAlignment()
        if cache:
            ret = self.getTransMeta('findPointers')
            if ret is not None:
                # Filter locations added since last run...
                ret = [(va, x) for (va, x) in ret if self.getLocation(va) is None and not (va % align)]
                self.setTransMeta('findPointers', ret)
                return ret

        ret = []
        size = self.psize

        for mva, msize, mperm, mname in self.getMemoryMaps():

            offset, bytes = self.getByteDef(mva)
            maxsize = len(bytes) - size

            # if our memory map is not starting off aligned appropriately
            if offset % align:
                offset &= -align
                offset += align

            while offset + size < maxsize:
                va = mva + offset

                loctup = self.getLocation(va)
                if loctup is not None:
                    offset += loctup[L_SIZE]
                    if offset % align:
                        offset += align
                        offset &= -align
                    continue

                x = e_bits.parsebytes(bytes, offset, size, bigend=self.bigend)
                if self.isValidPointer(x):
                    ret.append((va, x))
                    offset += size
                    continue

                offset += align
                offset &= -align

        if cache:
            self.setTransMeta('findPointers', ret)

        return ret

    def detectString(self, va):
        '''
        If the address appears to be the start of a string, then
        return the string length in bytes, else return -1.
        '''
        plen = 0  # pascal string length
        dlen = 0  # delphi string length
        left = self.getMemoryMap(va-4)
        # DEV: Make sure there's space left in the map
        if self.isReadable(va-4) and left and (left[MAP_VA] + left[MAP_SIZE] - va + 4) >= 4:
            plen = self.readMemValue(va - 2, 2)  # pascal string length
            dlen = self.readMemValue(va - 4, 4)  # delphi string length

        offset, bytez = self.getByteDef(va)
        maxlen = len(bytez) - offset
        count = 0
        while count < maxlen:
            # If we hit another thing, then probably not.
            # Ignore when count==0 so detection can check something
            # already set as a location.
            if count > 0:
                loc = self.getLocation(va+count)
                if loc is not None:
                    if loc[L_LTYPE] == LOC_STRING:
                        if loc[L_VA] == va:
                            return loc[L_SIZE]
                        if bytez[offset+count] != 0:
                            # we probably hit a case where the string at the lower va is
                            # technically the start of the full string, but the binary does
                            # some optimizations and just ref's inside the full string to save 
                            # some space
                            return count + loc[L_SIZE]
                        return loc[L_VA] - (va + count) + loc[L_SIZE]
                    return -1

            c = bytez[offset+count]
            # The "strings" algo basically says 4 or more...
            if c == 0 and count >= 4:
                return count

            elif c == 0 and (count == dlen or count == plen):
                return count

            if chr(c) not in string.printable:
                return -1

            count += 1
        return -1

    def isProbablyString(self, va):
        if self.detectString(va) > 0 :
            return True
        return False

    def detectUnicode(self, va):
        '''
        If the address appears to be the start of a unicode string, then
        return the string length in bytes, else return -1.

        This will return true if the memory location is likely
        *simple* UTF16-LE unicode (<ascii><0><ascii><0><0><0>).
        '''
        # FIXME this does not detect Unicode...

        offset, bytes = self.getByteDef(va)
        maxlen = len(bytes) - offset
        count = 0
        if maxlen < 2:
            return -1
        charset = bytes[offset + 1]
        while count < maxlen:
            # If we hit another thing, then probably not.
            # Ignore when count==0 so detection can check something
            # already set as a location.
            if (count > 0):
                loc = self.getLocation(va+count)
                if loc:
                    if loc[L_LTYPE] == LOC_UNI:
                        if loc[L_VA] == va:
                            return loc[L_SIZE]
                        if bytes[offset+count] != 0:
                            # same thing as in the string case, a binary can ref into a string
                            # only part of the full string.
                            return count + loc[L_SIZE]
                        return loc[L_VA] - (va + count) + loc[L_SIZE]
                    return -1

            c0 = bytes[offset+count]
            if offset + count+1 >= len(bytes):
                return -1
            c1 = bytes[offset+count+1]

            # If we find our null terminator after more
            # than 4 chars, we're probably a real string
            if c0 == 0:
                if count > 8:
                    return count
                return -1

            # If the first byte char isn't printable, then
            # we're probably not a real "simple" ascii string
            if chr(c0) not in string.printable:
                return -1

            # If it's not null,char,null,char then it's
            # not simple unicode...
            if c1 != charset:
                return -1

            count += 2
        return -1

    def isProbablyUnicode(self, va):
        if self.detectUnicode(va) > 0 :
            return True
        return False

    def isProbablyCode(self, va, **kwargs):
        """
        Most of the time, absolute pointers which point to code
        point to the function entry, so test it for the sig.
        """
        if not self.isExecutable(va):
            return False
        ret = self.isFunctionSignature(va)
        if ret:
            return ret

        rerun = kwargs.pop('rerun', False)
        if va in self.iscode and not rerun:
            return self.iscode[va]

        self.iscode[va] = True
        # because we're doing partial emulation, demote some of the logging
        # messages to low priority.
        kwargs['loglevel'] = e_common.EMULOG
        emu = self.getEmulator(**kwargs)
        wat = v_emucode.watcher(self, va)
        emu.setEmulationMonitor(wat)
        try:
            emu.runFunction(va, maxhit=1)
        except Exception as e:
            self.iscode[va] = False
            return False

        if wat.looksgood():
            self.iscode[va] = True
        else:
            self.iscode[va] = False

        return self.iscode[va]

    #################################################################
    #
    # Opcode API
    #
    def parseOpcode(self, va, arch=envi.ARCH_DEFAULT, skipcache=False):
        '''
        Parse an opcode from the specified virtual address.

        Example: op = m.parseOpcode(0x7c773803, skipcache=True)

        Set skipcache=True in order to bypass the opcode cache and force a reparsing of bytes
        '''
        off, b = self.getByteDef(va)
        if arch == envi.ARCH_DEFAULT:
            loctup = self.getLocation(va)
            # XXX - in the case where we've set a location on what should be an
            # opcode lets make sure L_LTYPE == LOC_OP if not lets reset L_TINFO = original arch param
            # so that at least parse opcode wont fail
            if loctup is not None and loctup[L_TINFO] and loctup[L_LTYPE] == LOC_OP:
                arch = loctup[L_TINFO]
        if not skipcache:
            key = (va, arch, b[:16])
            valu = self._op_cache.get(key, None)
            if not valu:
                valu = self.imem_archs[(arch & envi.ARCH_MASK) >> 16].archParseOpcode(b, off, va)
            self._op_cache[key] = valu
            return valu
        return self.imem_archs[(arch & envi.ARCH_MASK) >> 16].archParseOpcode(b, off, va)

    def clearOpcache(self):
        '''
        Remove all elements from the opcode cache
        '''
        self._op_cache.clear()

    def iterJumpTable(self, startva, step=None, maxiters=None, rebase=False):
        if not step:
            step = self.psize
        fname = self.getMemoryMap(startva)
        if fname is None:
            return

        fname = fname[3]
        imgbase = self.getFileMeta(fname, 'imagebase')
        iters = 0
        ptrbase = startva
        rdest = self.readMemValue(ptrbase, step)
        if rebase and rdest < imgbase:
            rdest += imgbase

        while self.isValidPointer(rdest) and self.isProbablyCode(rdest):
            if self.analyzePointer(ptrbase) in STOP_LOCS:
                break

            yield rdest

            ptrbase += step
            if len(self.getXrefsTo(ptrbase)):
                break
            rdest = self.readMemValue(ptrbase, step)
            if rebase and rdest < imgbase:
                rdest += imgbase

            iters += 1
            if maxiters is not None and iters >= maxiters:
                break

    def moveCodeBlock(self, cbva, newfva):
        cb = self.getCodeBlock(cbva)

        if cb is None:
            return

        if cb[CB_FUNCVA] == newfva:
            return

        self.delCodeBlock(cb)
        self.addCodeBlock((cb[CB_VA], cb[CB_SIZE], newfva))

    def splitJumpTable(self, callingVa, prevRefVa, newTablAddr, rebase=False, psize=4):
        '''
        So we have the case where if we have two jump tables laid out consecutively in memory (let's
        call them tables Foo and Bar, with Foo coming before Bar), and we see Foo first, we're going to
        recognize Foo as being a giant table, with all of Bar overlapping with Foo

        So we need to construct a list of now invalid references from prevRefVa, starting at newTablAddr
        newTablAddr should point to the new jump table, and those new codeblock VAs should be removed from
        the list of references that prevRefVa refs to (and delete the name)

        We also need to check to see if the functions themselves line up (ie, do these two jump tables
        even belong to the same function, or should we remove the code block from the function entirely?)
        '''
        # Due to how codeflow happens, we have no guarantee if these two adjacent jump tables are
        # even in the same function
        codeblocks = set()
        curfva = self.getFunction(callingVa)
        # collect all the entries for the new jump table
        for cb in self.iterJumpTable(newTablAddr, rebase=rebase, step=psize):
            if cb in codeblocks:
                continue
            codeblocks.add(cb)
            prevcb = self.getCodeBlock(cb)
            if prevcb is None:
                continue
            # we may also have to break these codeblocks from the old function
            # 1 -- new func is none, old func is none
            #   * can't happen. if the codeblock is defined, we at least have an old function
            # 2 -- new func is not none, old func is none
            #   * Can't happen. see above
            # 3 -- new func is none, old func is not none
            #   * delete the codeblock. we've dropped into a new function that is different from the old
            #     since how codeflow discover functions, we should have all the code blocks for function
            # 4 -- neither are none
            #   * moveCodeBlock -- that func will handle whether or not functions are the same
            if curfva is not None:
                self.moveCodeBlock(cb, curcb[CB_FUNCVA])
            else:
                self.delCodeBlock(prevcb[CB_VA])

        # now delete those entries from the previous jump table
        oldrefs = self.getXrefsFrom(prevRefVa)
        todel = [xref for xref in self.getXrefsFrom(prevRefVa) if xref[1] in codeblocks]
        for va in todel:
            self.setComment(va[1], None)
            self.delXref(va)

    def makeJumpTable(self, op, tova, rebase=False, psize=4):
        fname = self.getFileByVa(tova)
        imgbase = self.getFileMeta(fname, 'imagebase')

        ptrbase = tova
        rdest = self.readMemValue(ptrbase, psize)
        if rebase and rdest < imgbase:
            rdest += imgbase

        # if there's already an Xref to this address from another jump table, we overshot
        # the other table, and need to cut that one short, delete its Xrefs starting at this one
        # and then let the rest of this function build the new jump table
        # This jump table also may not be in the same function as the other jump table, so we need
        # to remove those codeblocks (and child codeblocks) from this function

        # at this point, rdest should be the first codeblock in the jumptable, so get all the xrefs to him
        # (but skipping over the current jumptable base address we're looking at)
        for xrfrom, xrto, rtype, rflags in self.getXrefsTo(rdest):
            if tova == xrfrom:
                continue

            refva, refsize, reftype, refinfo = self.getLocation(xrfrom)
            if reftype != LOC_OP:
                continue
            # If we've already constructed this opcode location and made the xref to the new codeblock,
            # that should mean we've already made the jump table, so there should be no need to split this
            # jump table.
            if refva == op.va:
                continue
            refop = self.parseOpcode(refva)
            for refbase, refbflags in refop.getBranches():
                if refbflags & envi.BR_TABLE:
                    self.splitJumpTable(op.va, refva, tova, psize=psize)

        tabdone = {}
        for i, rdest in enumerate(self.iterJumpTable(ptrbase, rebase=rebase, step=psize)):
            if not tabdone.get(rdest):
                tabdone[rdest] = True
                self.addXref(op.va, rdest, REF_CODE, envi.BR_COND)
                if self.getName(rdest) is None:
                    self.makeName(rdest, "case%d_%.8x" % (i, op.va))
            else:
                cmnt = self.getComment(rdest)
                if cmnt is None:
                    self.setComment(rdest, "Other Case(s): %d" % i)
                else:
                    cmnt += ", %d" % i
                    self.setComment(rdest, cmnt)

        # This must be second (len(xrefsto))
        self.addXref(op.va, tova, REF_PTR)

    def makeOpcode(self, va, op=None, arch=envi.ARCH_DEFAULT):
        """
        Create a single opcode location.  If you have already parsed the
        opcode object, you may pass it in.
        """
        if op is None:
            try:
                op = self.parseOpcode(va, arch=arch)
            except envi.InvalidInstruction as msg:
                # FIXME something is just not right about this...
                bytez = self.readMemory(va, 16)
                logger.warning("Invalid Instruct Attempt At:", hex(va), e_common.hexify(bytez))
                raise InvalidLocation(va, msg)
            except Exception as msg:
                raise InvalidLocation(va, msg)

        # Add our opcode location first (op flags become ldata)
        loc = self.addLocation(va, op.size, LOC_OP, op.iflags)

        # This takes care of all normal indirect immediates

        brdone = {}
        brlist = op.getBranches()
        for tova, bflags in brlist:

            # If there were unresolved dynamic branches, oh well...
            if tova is None:
                continue
            if not self.isValidPointer(tova):
                continue

            brdone[tova] = True

            # Special case, if it's a table branch, lets resolve it now.
            if bflags & envi.BR_TABLE:
                self.makeJumpTable(op, tova)

            elif bflags & envi.BR_DEREF:

                self.addXref(va, tova, REF_DATA)
                ptrdest = None
                if self.getLocation(tova) is None:
                    ptrdest = self.makePointer(tova, follow=False)

                # If the actual dest is executable, make a code ref fixup
                # which *removes* the deref flag...
                # If we're an xref to something real, rip out the deref flag, but if we're
                # an xref to a big fat 0, fuggedaboutit
                if ptrdest and self.analyzePointer(ptrdest[0]):
                    self.addXref(va, ptrdest[0], REF_CODE, bflags & ~envi.BR_DEREF)
                else:
                    self.addXref(va, tova, REF_CODE, bflags)


            else:
                # vivisect does NOT create REF_CODE entries for
                # instruction fall through
                if bflags & envi.BR_FALL:
                    continue

                self.addXref(va, tova, REF_CODE, bflags)

        # Check the instruction for static d-refs
        for oidx, o in op.genRefOpers(emu=None):
            # FIXME it would be nice if we could just do this one time
            # in the emulation pass (or hint emulation that some have already
            # been done.
            # unfortunately, emulation pass only occurs for code identified
            # within a marked function.
            # future fix: move this all into VivCodeFlowContext.

            # Does the operand touch memory ?
            if o.isDeref():

                ref = o.getOperAddr(op, None)

                if brdone.get(ref, False):
                    continue

                if ref is not None and self.isValidPointer(ref):

                    # It's a data reference. lets also check if the data is
                    # a pointer.

                    self.addXref(va, ref, REF_DATA)

                    # If we don't already know what type this location is,
                    # lets make it either a pointer or a number...
                    if self.getLocation(ref) is None:
                        self.guessDataPointer(ref, o.tsize)
            else:
                ref = o.getOperValue(op)
                if brdone.get(ref, False):
                    continue
                if ref is not None and type(ref) is int and self.isValidPointer(ref):
                    self.addXref(va, ref, REF_PTR)

        return loc

    def _dbgLocEntry(self, va):
        """
        Display the human-happy version of a location
        """
        loc = self.getLocation(va)
        if loc is None:
            return 'None'

        lva, lsz, ltype, ltinfo = loc
        ltvar = loc_lookups.get(ltype)
        ltdesc = loc_type_names.get(ltype)
        locrepr = '(0x%x, %d, %s, %r)  # %s' % (lva, lsz, ltvar, ltinfo, ltdesc)
        return locrepr

    def updateCallsFrom(self, fva, ncalls):
        function = self.getFunction(fva)
        prev_call = self.getFunctionMeta(function, 'CallsFrom')
        newcall = set(prev_call).union(set(ncalls))
        self.setFunctionMeta(function, 'CallsFrom', list(newcall))

    def makeCode(self, va, arch=envi.ARCH_DEFAULT, fva=None):
        """
        Attempt to begin code-flow based disassembly by
        starting at the given va.  The va will be made into
        an OpcodeLoc and refs will be walked continuing to
        make code where possible.
        """
        # If this is already a location, bail.
        if self.isLocation(va):
            return

        calls_from = self.cfctx.addCodeFlow(va, arch=arch)
        if fva is None:
            self.setVaSetRow('CodeFragments', (va, calls_from))
        else:
            self.updateCallsFrom(fva, calls_from)
        return calls_from

    def previewCode(self, va, arch=envi.ARCH_DEFAULT):
        '''
        Show the repr of an instruction in the current canvas *before* making it that
        '''
        try:
            op = self.parseOpcode(va, arch)
            if op is None:
                self.vprint("0x%x - None")
            else:
                self.vprint("0x%x  (%d bytes)  %s" % (va, len(op), repr(op)))
        except Exception:
            self.vprint("0x%x - decode exception" % va)
            logger.exception("preview opcode exception:")

    #################################################################
    #
    # Function API
    #

    def isFunction(self, funcva):
        """
        Return True if funcva is a function entry point.
        """
        return self.funcmeta.get(funcva) is not None

    def isFunctionThunk(self, funcva):
        """
        Return True if funcva is a function thunk
        """
        # TODO: could we do more here?
        try:
            return self.getFunctionMeta(funcva, 'Thunk') is not None
        except InvalidFunction:
            return False

    def getFunctions(self):
        """
        Return a list of the function virtual addresses
        defined in the workspace.
        """
        return list(self.funcmeta.keys())

    def getFunction(self, va):
        """
        Return the VA for this function.  This will search code blocks
        and check for a function va.
        """
        if self.funcmeta.get(va) is not None:
            return va
        cbtup = self.getCodeBlock(va)
        if cbtup is not None:
            return cbtup[CB_FUNCVA]
        return None

    def makeFunction(self, va, meta=None, arch=envi.ARCH_DEFAULT):
        """
        Do parsing for function information and add a new function doodad.
        This function should probably only be called once code-flow for the
        area is complete.
        """
        logger.debug('makeFunction(0x%x, %r, 0x%x)', va, meta, arch)
        if self.isFunction(va):
            logger.debug('0x%x is already a function, skipping', va)
            return

        if not self.isValidPointer(va):
            raise InvalidLocation(va)

        loc = self.getLocation(va)
        if loc is not None and loc[L_TINFO] is not None and loc[L_LTYPE] == LOC_OP:
            arch = loc[L_TINFO]

        realfva = self.cfctx.addEntryPoint(va, arch=arch)

        if meta is not None:
            for key, val in meta.items():
                self.setFunctionMeta(realfva, key, val)
        return realfva

    def delFunction(self, funcva):
        """
        Remove a function, it's code blocks and all associated meta
        """
        if self.funcmeta.get(funcva) is None:
            raise InvalidLocation(funcva)

        self._fireEvent(VWE_DELFUNCTION, funcva)

    def setFunctionArg(self, fva, idx, atype, aname):
        '''
        Set the name and type information for a single function arguemnt by index.

        Example:
            # If we were setting up main...
            vw.setFunctionArg(fva, 0, 'int','argc')
            vw.setFunctionArg(fva, 1, 'char **','argv')
        '''
        rettype,retname,callconv,callname,callargs = self.getFunctionApi(fva)
        while len(callargs) <= idx:
            callargs.append( ('int','arg%d' % len(callargs)) )

        callargs[idx] = (atype,aname)
        self.setFunctionApi(fva, (rettype,retname,callconv,callname,callargs))

    def getFunctionArgs(self, fva):
        '''
        Returns the list of (typename,argname) tuples which define the
        arguments for the specified function.

        Example:
            for typename,argname in vw.getFunctionArgs(fva):
                print('Takes: %s %s' % (typename,argname))
        '''
        rettype, retname, callconv, callname, callargs = self.getFunctionApi(fva)
        return list(callargs)

    def getFunctionApi(self, fva):
        '''
        Retrieve the API definition for the given function address.

        Returns: an API tuple (similar to impapi subsystem) or None
            ( rettype, retname, callconv, funcname, ( (argtype, argname), ...) )
        '''
        ret = self.getFunctionMeta(fva, 'api')
        if ret is not None:
            return ret

        defcall = self.getMeta('DefaultCall','unkcall')
        return ('void', None, defcall, None, ())

    def setFunctionApi(self, fva, apidef):
        '''
        Set a function's API definition.
        NOTE: apidef is a tuple similar to the impapi subsystem
            ( rettype, retname, callconv, funcname, ( (argtype, argname), ...) )

        Example:
            apidef = ('int','size','stdcall','getThingSize', ( ('void *','thing'), ))
            vw.setFunctionApi(fva, apidef)
        '''
        self.setFunctionMeta(fva, 'api', apidef)

    def getFunctionLocals(self, fva):
        '''
        Retrieve the list of (fva,spdelta,symtype,syminfo) tuples which
        represent the given function's local memory offsets.
        '''
        if not self.isFunction(fva):
            raise InvalidFunction(fva)
        return list(self.localsyms[fva].values())

    def getFunctionLocal(self, fva, spdelta):
        '''
        Retrieve a function local symbol definition as a
        (typename,symname) tuple or None if not found.

        NOTE: If the local symbol references a LSYM_FARG, this API
        will resolve the argument name/type from the function API
        definition.

        Example:
            locsym = vw.getFunctionLocal(fva, 8)
            if locsym:
                symtype,symname = locsym
                print('%s %s;' % (symtype,symname))
        '''
        locsym = self.localsyms[fva].get(spdelta)
        if locsym is None:
            return None

        fva,spdelta,symtype,syminfo = locsym
        if symtype == LSYM_NAME:
            return syminfo

        if symtype == LSYM_FARG:

            apidef = self.getFunctionApi(fva)
            if apidef is None:
                return None

            funcargs = apidef[-1]
            if syminfo >= len(funcargs):
                return None

            return funcargs[syminfo]

        raise Exception('Unknown Local Symbol Type: %d' % symtype)

    def setFunctionLocal(self, fva, spdelta, symtype, syminfo):
        '''
        Assign a local symbol within a function (addressed
        by delta from initial sp).  For each symbol, a "symtype"
        and "syminfo" field are used to specify the details.

        Example:
            # Setup a regular local integer
            vw.setFunctionLocal(fva, -4, LSYM_NAME, ('int','x'))

            # Setup a link to a stack argument... (ie. i386 cdecl)
            vw.setFunctionLocal(fva, 4, LSYM_FARG, 0)

            # Setup amd64 style shadow space
            vw.setFunctionLocal(fva, 8, LSYM_NAME, ('void *','shadow0'))
        '''
        metaname = 'LocalSymbol:%d' % spdelta
        metavalue = (fva,spdelta,symtype,syminfo)
        self.setFunctionMeta(fva, metaname, metavalue)

    def setFunctionMeta(self, funcva, key, value):
        """
        Set meta key,value pairs that describe a particular
        function (by funcva).

        Example: vw.setFunctionMeta(fva, "WootKey", 10)
        """
        if not self.isFunction(funcva):
            raise InvalidFunction(funcva)
        self._fireEvent(VWE_SETFUNCMETA, (funcva, key, value))

    def getFunctionMeta(self, funcva, key, default=None):
        m = self.funcmeta.get(funcva)
        if m is None:
            raise InvalidFunction(funcva)
        return m.get(key, default)

    def getFunctionMetaDict(self, funcva):
        """
        Return the entire dictionary of function metadata
        for the function specified at funcva
        """
        return self.funcmeta.get(funcva)

    def getFunctionBlocks(self, funcva):
        """
        Return the code-block objects for the given function va
        """
        ret = self.codeblocks_by_funcva.get(funcva)
        if ret is None:
            ret = []
        return ret

    def makeFunctionThunk(self, fva, thname, addVa=True, filelocal=False):
        """
        Inform the workspace that a given function is considered a "thunk" to another.
        This allows the workspace to process argument inheritance and several other things.

        Usage: vw.makeFunctionThunk(0xvavavava, "kernel32.CreateProcessA")
        """
        self.checkNoRetApi(thname, fva)
        self.setFunctionMeta(fva, "Thunk", thname)
        n = self.getName(fva)

        base = thname.split(".")[-1]
        if addVa:
            name = "%s_%.8x" % (base,fva)
        else:
            name = base
        newname = self.makeName(fva, name, filelocal=filelocal, makeuniq=True)

        api = self.getImpApi(thname)
        if api:
            # Set any argument names that are None
            rettype,retname,callconv,callname,callargs = api
            callargs = [ callargs[i] if callargs[i][1] else (callargs[i][0],'arg%d' % i) for i in range(len(callargs)) ]
            self.setFunctionApi(fva, (rettype,retname,callconv,callname,callargs))

    def getCallers(self, va):
        '''
        Get the va for all the callers of the given function/import.

        Example:
            for va in vw.getCallers( importva ):
                dostuff(va)
        '''
        ret = []
        for fromva, tova, rtype, rflags in self.getXrefsTo(va, rtype=REF_CODE):
            if rflags & envi.BR_PROC:
                ret.append(fromva)
        return ret

    def getCallGraph(self):
        '''
        Retrieve a visgraph Graph object representing all known inter procedural
        branches in the workspace.  Each node has an ID that is the same as the
        function va.

        Example:
            graph = vw.getCallGraph()
        '''
        return self._call_graph

    def getFunctionGraph(self, fva):
        '''
        Retrieve a code-block graph for the specified virtual address.
        Procedural branches (ie, calls) will not be followed during graph
        construction.
        '''
        return viv_codegraph.FuncBlockGraph(self,fva)

    def getImportCallers(self, name):
        """
        Get a list of all the callers who reference the specified import
        by name. (If we detect that the name is actually *in* our workspace,
        return those callers too...
        """
        ret = []

        # If it's a local function, do that too..
        fva = self.vaByName(name)
        if fva is not None and self.isFunction(fva):
            ret = self.getCallers(fva)

        for fva in self.getFunctions():
            if self.getFunctionMeta(fva, 'Thunk') == name:
                ret.extend( self.getCallers( fva ) )

        for lva,lsize,ltype,tinfo in self.getLocations(LOC_IMPORT):
            if tinfo == name:
                ret.extend( self.getCallers( lva ) )

        return ret

    #################################################################
    #
    # Xref API
    #

    def getXrefs(self, rtype=None):
        """
        Return the entire list of XREF tuples for this workspace.
        """
        if rtype:
            return [ xtup for xtup in self.xrefs if xtup[XR_RTYPE] == rtype ]
        return self.xrefs

    def getXrefsFrom(self, va, rtype=None):
        """
        Return a list of tuples for the xrefs whose origin is the
        specified va.  Optionally, only return xrefs whose type
        field is rtype if specified.

        example:
        for fromva, tova, rtype, rflags in vw.getXrefsFrom(0x41414141):
            dostuff(tova)
        """
        ret = []
        xrefs = self.xrefs_by_from.get(va, None)
        if xrefs is None:
            return ret
        if rtype is None:
            return xrefs
        return [ xtup for xtup in xrefs if xtup[XR_RTYPE] == rtype ]

    def getXrefsTo(self, va, rtype=None):
        """
        Get a list of xrefs which point to the given va. Optionally,
        specify an rtype to get only xrefs of that type.
        """
        # FIXME make xrefs use MapLookup!
        ret = []
        xrefs = self.xrefs_by_to.get(va, None)
        if xrefs is None:
            return ret
        if rtype is None:
            return xrefs
        return [ xtup for xtup in xrefs if xtup[XR_RTYPE] == rtype ]

    def addMemoryMap(self, va, perms, fname, bytes):
        """
        Add a memory map to the workspace.  This is the *only* way to
        get memory backings into the workspace.
        """
        self._fireEvent(VWE_ADDMMAP, (va, perms, fname, bytes))

    def delMemoryMap(self, mapva):
        '''
        Remove a memory map from the workspace.
        '''
        self._fireEvent(VWE_DELMMAP, mapva)

    def addSegment(self, va, size, name, filename):
        """
        Add a "segment" to the workspace.  A segment is generally some meaningful
        area inside of a memory map.  For PE binaries, a segment and a memory map
        are synonymous.  However, some platforms (Elf) specify their memory maps
        (program headers) and segments (sectons) seperately.
        """
        self._fireEvent(VWE_ADDSEGMENT, (va,size,name,filename))

    def getSegment(self, va):
        """
        Return the tuple representation of a segment. With the
        following format:

        (va, size, name, filename)
        """
        for seg in self.segments:
            sva, ssize, sname, sfile = seg
            if va >= sva and va < (sva + ssize):
                return seg
        return None

    def getSegments(self):
        """
        Return a list of segment tuples (see getSegment) for all
        the segments defined in the current worksace
        """
        return list(self.segments)

    def addCodeBlock(self, va, size, funcva):
        """
        Add a region of code which belongs to a function.  Code-block boundaries
        are at all logical branches and have more in common with a logical
        graph view than function chunks.
        """
        loc = self.getLocation( va )
        if loc is None:
            raise Exception('Adding Codeblock on *non* location?!?: 0x%.8x' % va)
        self._fireEvent(VWE_ADDCODEBLOCK, (va,size,funcva))

    def getCodeBlock(self, va):
        """
        Return the codeblock which contains the given va.  A "codeblock"
        is a location compatable tuple: (va, size, funcva)
        """
        return self.blockmap.getMapLookup(va)

    def delCodeBlock(self, va):
        """
        Remove a code-block definition from the codeblock namespace.
        """
        cb = self.getCodeBlock(va)
        if cb is None:
            raise Exception("Unknown Code Block: 0x%x" % va)
        self._fireEvent(VWE_DELCODEBLOCK, cb)

    def getCodeBlocks(self):
        """
        Return a list of all the codeblock objects.
        """
        return list(self.codeblocks)

    def addXref(self, fromva, tova, reftype, rflags=0):
        """
        Add an xref with the specified fromva, tova, and reftype
        (see REF_ macros).  This will *not* trigger any analysis.
        Callers are expected to do their own xref analysis (ie, makeCode() etc)
        """
        # Architecture gets to decide on actual final VA (ARM/THUMB/etc...)
        tova, reftype, rflags = self.arch.archModifyXrefAddr(tova, reftype, rflags)

        ref = (fromva, tova, reftype, rflags)
        if ref in self.getXrefsFrom(fromva):
            return
        self._fireEvent(VWE_ADDXREF, (fromva, tova, reftype, rflags))

    def delXref(self, ref):
        """
        Remove the given xref.  This *will* exception if the
        xref doesn't already exist...
        """
        if ref not in self.getXrefsFrom(ref[XR_FROM]):
            raise Exception("Unknown Xref: %x %x %d" % ref)
        self._fireEvent(VWE_DELXREF, ref)

    def analyzePointer(self, va):
        """
        Assume that a new pointer has been created.  Check if it's
        target has a defined location and if not, try to figure out
        what's there. Will return the location type of the location
        it recommends or None if a location is already there or it has
        no idea.
        """
        if self.getLocation(va) is not None:
            return None
        if self.isProbablyUnicode(va):
            return LOC_UNI
        elif self.isProbablyString(va):
            return LOC_STRING
        elif self.isProbablyCode(va):
            return LOC_OP
        return None

    def getMeta(self, name, default=None):
        return self.metadata.get(name, default)

    def setMeta(self, name, value):
        """
        Set a meta key,value pair for this workspace.
        """
        self._fireEvent(VWE_SETMETA, (name,value))

    def markDeadData(self, start, end):
        """
        mark a virtual range as dead code.
        """
        self.setMeta("deaddata:0x%08x" % start, (start, end))

    def unmarkDeadData(self, start, end):
        """
        unmark a virtual range as dead code
        """
        self._dead_data.remove( (start,end) )

    def _mcb_deaddata(self, name, value):
        """
        callback from setMeta with namespace
        deaddata:
        that indicates a range has been added
        as dead data.
        """
        if value not in self._dead_data:
            self._dead_data.append( value )

    def isDeadData(self, va):
        """
        Return boolean indicating va is in
        a dead data range.
        """
        for start,end in self._dead_data:
            if va >= start and va <= end:
                return True
        return False

    def initMeta(self, name, value):
        """
        Set a metakey ONLY if it is not already set. Either
        way return the value of the meta key.
        """
        m = self.getMeta(name)
        if m is None:
            self.setMeta(name, value)
            m = value
        return m

    def getTransMeta(self, mname, default=None):
        '''
        Retrieve a piece of "transient" metadata which is *not*
        stored across runs or pushed through the event subsystem.
        '''
        return self.transmeta.get(mname,default)

    def setTransMeta(self, mname, value):
        '''
        Store a piece of "transient" metadata which is *not*
        stored across runs or pushed through the event subsystem.
        '''
        self.transmeta[mname] = value

    def castPointer(self, va):
        """
        Return the value for a pointer in memory at
        the given location.  This method does NOT
        create a location object or do anything other
        than parse memory.
        """
        offset, bytes = self.getByteDef(va)
        return e_bits.parsebytes(bytes, offset, self.psize, bigend=self.bigend)

    def guessDataPointer(self, ref, tsize):
        '''
        Trust vivisect to do the right thing and make a value and a
        pointer to that value
        '''
        # So we need the size check to avoid things like "aaaaa", maybe
        # but maybe if we do something like the tsize must be either the
        # target pointer size or in a set of them that the arch defines?
        nloc = None
        try:
            if self.isProbablyUnicode(ref):
                nloc = self.makeUnicode(ref)
            elif self.isProbablyString(ref):
                nloc = self.makeString(ref)
        except e_exc.SegmentationViolation:
            # Usually means val is 0 and we can just ignore this error
            nloc = None
        except Exception as e:
            logger.warning('makeOpcode string making hit error %s', str(e))
            nloc = None

        if not nloc:
            val = self.parseNumber(ref, tsize)
            if (self.psize == tsize and self.isValidPointer(val)):
                nloc = self.makePointer(ref, tova=val)
            else:
                nloc = self.makeNumber(ref, tsize)

        return nloc

    def makePointer(self, va, tova=None, follow=True):
        """
        Create a new pointer location in the workspace.  If you have already
        parsed out the pointers value, you may specify tova to speed things
        up.
        """
        loctup = self.getLocation(va)
        if loctup is not None:
            if loctup[L_LTYPE] != LOC_POINTER or loctup[L_VA] != va:
                logger.warning("0x%x: Attempting to make a Pointer where another location object exists (of type %r)", va, self.reprLocation(loctup))
            return None

        psize = self.psize

        # Get and document the xrefs created for the new location
        if tova is None:
            tova = self.castPointer(va)

        self.addXref(va, tova, REF_PTR)

        ploc = self.addLocation(va, psize, LOC_POINTER)

        if follow and self.isValidPointer(tova):
            self.followPointer(tova)

        return ploc

    def makePad(self, va, size):
        """
        A special utility for making a pad of a particular size.
        """
        return self.addLocation(va, size, LOC_PAD, None)

    def makeNumber(self, va, size, val=None):
        """
        Create a number location in memory of the given size.

        (you may specify val if you have already parsed the value
         from memory and would like to save CPU cycles)
        """
        return self.addLocation(va, size, LOC_NUMBER, None)

    def parseNumber(self, va, size):
        '''
        Parse a <size> width numeric value from memory at <va>.

        Example:
            val = vw.parseNumber(0x41414140, 4)
        '''
        offset, bytes = self.getByteDef(va)
        return e_bits.parsebytes(bytes, offset, size, bigend=self.bigend)

    def _getSubstrings(self, va, size, ltyp):
        # rip through the desired memory range to populate any substrings
        subs = set()
        end = va + size
        for offs in range(va, end, 1):
            loc = self.getLocation(offs, range=True)
            if loc and loc[L_LTYPE] == LOC_STRING and loc[L_VA] > va:
                subs.add((loc[L_VA], loc[L_SIZE]))
                if loc[L_TINFO]:
                    subs = subs.union(set(loc[L_TINFO]))
        return list(subs)

    def _getStrTinfo(self, va, size, subs):
        ploc = self.getLocation(va, range=False)
        if ploc:
            # the string we're making is a substring of some outer one
            # still make this string location, but let the parent know about us too and our
            # children as well. Ultimately, the outermost parent should be responsible for
            # knowing about all it's substrings
            modified = False
            pva, psize, ptype, pinfo = ploc
            if ptype not in (LOC_STRING, LOC_UNI):
                return va, size, subs
            if (va, size) not in pinfo:
                modified = True
                pinfo.append((va, size))

            for sva, ssize in subs:
                if (sva, ssize) not in pinfo:
                    modified = True
                    pinfo.append((sva, ssize))

            tinfo = pinfo
            if modified:
                va = pva
                size = psize
        else:
            tinfo = subs

        return va, size, tinfo

    def makeString(self, va, size=None):
        """
        Create a new string location at the given VA.  You may optionally
        specify size.  If size==None, the string will be parsed as a NULL
        terminated ASCII string.

        Substrings are also handled here. Generally, the idea is:
        * if the memory range is completey undefined, we just create a new string at the VA specified (provided that asciiStringSize return a size greater than 0 or the parameter size is greater than 0)

        * if we create a string A at virtual address 0x40 with size 20, and then later a string B at virtual
          address 0x44, we won't actually make a new location for the string B, but rather add info to the
          tinfo portion of the location tuple for string A, and when trying to retrieve string B via getLocation,
          we'll make up a (sort of) fake location tuple for string B, provided that range=True is passed to
          getLocation

        * if we create string A at virtual address 0x40, and then later a string B at virtual 0x30
          that has a size of 16 or more, we overwrite the string A with the location information for string B,
          and demote string A to being a tuple of (VA, size) inside of string B's location information.

        This method only captures suffixes, but perhaps in the future we'll have symbolik resolution that can
        capture true substrings that aren't merely suffixes.

        This same formula is applied to unicode detection as well
        """
        if size is None:
            size = self.asciiStringSize(va)

        if size <= 0:
            raise Exception("Invalid String Size: %d" % size)

        # rip through the desired memory range to populate any substrings
        subs = self._getSubstrings(va, size, LOC_STRING)
        pva, psize, tinfo = self._getStrTinfo(va, size, subs)

        if self.getName(va) is None:
            m = self.readMemory(va, size-1).replace(b'\n', b'')
            self.makeName(va, "str_%s_%.8x" % (m[:16].decode('utf-8'), va))
        return self.addLocation(pva, psize, LOC_STRING, tinfo=tinfo)

    def makeUnicode(self, va, size=None):
        if size is None:
            size = self.uniStringSize(va)

        if size <= 0:
            raise Exception("Invalid Unicode Size: %d" % size)

        subs = self._getSubstrings(va, size, LOC_UNI)
        pva, psize, tinfo = self._getStrTinfo(va, size, subs)

        if self.getName(va) is None:
            m = self.readMemory(va, size-1).replace(b'\n', b'').replace(b'\0', b'')
            try:
                self.makeName(va, "wstr_%s_%.8x" % (m[:16].decode('utf-8'), va))
            except:
                self.makeName(va, "wstr_%s_%.8x" % (m[:16],va))
        return self.addLocation(pva, psize, LOC_UNI, tinfo=tinfo)

    def addConstModule(self, modname):
        '''
        Add constants declared within the named module
        to the constants resolver namespace.

        Example: vw.addConstModule('vstruct.constants.ntstatus')
        '''
        mod = self.loadModule(modname)
        self.vsconsts.addModule(mod)

    def addStructureModule(self, namespace, modname):
        '''
        Add a vstruct structure module to the workspace with the given
        namespace.

        Example: vw.addStructureModule('ntdll', 'vstruct.defs.windows.win_5_1_i386.ntdll')

        This allows subsequent struct lookups by names like
        '''

        mod = self.loadModule(modname)
        self.vsbuilder.addVStructNamespace(namespace, mod)

    def getStructure(self, va, vstructname):
        """
        Parse and return a vstruct object for the given name.  This
        (like parseOpcode) does *not* require that the location be a struct
        and will not create one (use makeStructure).
        """
        s = vstruct.getStructure(vstructname)
        if s is None:
            s = self.vsbuilder.buildVStruct(vstructname)
        if s is not None:
            bytes = self.readMemory(va, len(s))
            s.vsParse(bytes)
        return s

    def makeStructure(self, va, vstructname, vs=None):
        """
        Make a location which is a structure and will be parsed/accessed
        by vstruct.  You must specify the vstruct name for the structure
        you wish to have at the location.  Returns a vstruct from the
        location.
        """
        if vs is None:
            vs = self.getStructure(va, vstructname)
        self.addLocation(va, len(vs), LOC_STRUCT, vstructname)

        # Determine if there are any pointers we need make
        # xrefs for...
        offset = 0
        for p in vs.vsGetPrims():
            if isinstance(p, vs_prims.v_ptr):
                vptr = p.vsGetValue()
                if self.isValidPointer(vptr):
                    self.addXref(va+offset, vptr, REF_PTR)

            offset += len(p)

        return vs

    def getUserStructNames(self):
        '''
        Retrive the list of the existing user-defined structure
        names.

        Example:
            for name in vw.getUserStructNames():
                print('Structure Name: %s' % name)
        '''
        return self.vsbuilder.getVStructCtorNames()

    def getUserStructSource(self, sname):
        '''
        Get the source code (as a string) for the given user
        defined structure.

        Example:
            ssrc = vw.getUserStructSource('MyStructureThing')
        '''
        return self.getMeta('ustruct:%s' % sname)

    def setUserStructSource(self, ssrc):
        '''
        Save the input string as a C structure definition for the
        workspace.  User-defined structures may then be applied
        to locations, or further edited in the future.

        Example:
            src = "struct woot { int x; int y; };"
            vw.setUserStructSource( src )
        '''
        # First, we make sure it compiles...
        ctor = vs_cparse.ctorFromCSource( ssrc )
        # Then, build one to get the name from it...
        vs = ctor()
        cname = vs.vsGetTypeName()
        self.setMeta('ustruct:%s' % cname, ssrc)
        return cname

    def asciiStringSize(self, va):
        """
        Return the size (in bytes) of the ascii string
        at the specified location (or -1 if no terminator
        is found in the memory map)
        """
        offset, bytez = self.getByteDef(va)
        foff = bytez.find(b'\x00', offset)
        if foff == -1:
            return foff
        return (foff - offset) + 1

    def uniStringSize(self, va):
        """
        Return the size (in bytes) of the unicode string
        at the specified location (or -1 if no terminator
        is found in the memory map)
        """
        offset, bytez = self.getByteDef(va)
        foff = bytez.find(b'\x00\x00', offset)
        if foff == -1:
            return foff
        return (foff - offset) + 2

    def addLocation(self, va, size, ltype, tinfo=None):
        """
        Add a location tuple.
        """
        ltup = (va, size, ltype, tinfo)
        #loc = self.locmap.getMapLookup(va)
        #if loc is not None:
            #raise Exception('Duplicate Location: (is: %r wants: %r)' % (loc,ltup))

        self._fireEvent(VWE_ADDLOCATION, ltup)
        return ltup

    def getLocations(self, ltype=None, linfo=None):
        """
        Return a list of location objects from the workspace
        of a particular type.
        """
        if ltype is None:
            return list(self.loclist)

        if linfo is None:
            return [ loc for loc in self.loclist if loc[2] == ltype ]

        return [ loc for loc in self.loclist if (loc[2] == ltype and loc[3] == linfo) ]

    def isLocation(self, va, range=False):
        """
        Return True if the va represents a location already.
        """
        if self.getLocation(va, range=range) is not None:
            return True
        return False

    def isLocType(self, va, ltype):
        """
        You may use this to test if a given VA represents
        a location of the specified type.

        example:
        if vw.isLocType(0x41414141, LOC_STRING):
            print("string at: 0x41414141")
        """
        # make it operate like py2 did
        if va is None:
            return False
        tup = self.getLocation(va)
        if tup is None:
            return False
        return tup[L_LTYPE] == ltype

    def getLocation(self, va, range=True):
        """
        Return the va,size,ltype,tinfo tuple for the given location.
        (specify range=True to potentially match a va that is inside
        a location rather than the beginning of one, this behavior
        only affects strings/substring retrieval currently)
        """
        loc = self.locmap.getMapLookup(va)
        if not loc:
            return loc

        if range and loc[L_LTYPE] in (LOC_STRING, LOC_UNI):
            # dig into any sublocations that may have been created, trying to find the best match
            # possible, where "best" means the substring that both contains the va, and has no substrings
            # that contain the va.
            if not loc[L_TINFO]:
                return loc
            subs = sorted(loc[L_TINFO], key=lambda k: k[0], reverse=False)
            ltup = loc
            for sva, ssize in subs:
                if sva <= va < sva + ssize:
                    ltup = (sva, ssize, loc[L_LTYPE], [])
            return ltup
        else:
            return loc

    def getLocationRange(self, va, size):
        """
        A "location range" is a list of location tuples where
        undefined space *will* be represented by LOC_UNDEF tuples
        to provide a complete accounting of linear workspace.
        """
        ret = []
        endva = va+size
        undefva = None
        while va < endva:
            ltup = self.getLocation(va)
            if ltup is None:
                if undefva is None:
                    undefva = va
                va += 1
            else:
                if undefva is not None:
                    ret.append((undefva, va-undefva, LOC_UNDEF, None))
                    undefva = None
                ret.append(ltup)
                va += ltup[L_SIZE]

        # Mop up any hanging udefs
        if undefva is not None:
            ret.append((undefva, va-undefva, LOC_UNDEF, None))

        return ret

    def delLocation(self, va):
        """
        Delete the given Location object from the binary
        (removes any xrefs/etc for the location as well)

        This will raise InvalidLocation if the va is not
        an exact match for the beginning of a location.
        """
        loc = self.getLocation(va)
        if loc is None:
            raise InvalidLocation(va)
        # remove xrefs from this location
        for xref in self.getXrefsFrom(va):
            self.delXref(xref)
        self._fireEvent(VWE_DELLOCATION, loc)

    def getRenderInfo(self, va, size):
        """
        Get nearly everything needed to render a workspace area
        to a display.  This function *greatly* speeds up interface
        code and is considered "tightly coupled" with the asmview
        code.  (and is therefore subject to change).
        """
        locs = []
        funcs = {}
        names = {}
        comments = {}
        extras = {}

        for loc in self.getLocationRange(va, size):
            lva, lsize, ltype, tinfo = loc
            locs.append(loc)

            name = self.getName(lva)
            isfunc = self.isFunction(lva)
            cmnt = self.getComment(lva)

            if name is not None:
                names[lva] = name
            if isfunc == True:
                funcs[lva] = True
            if cmnt is not None:
                comments[lva] = cmnt

            if ltype == LOC_UNDEF:
                # Expand out all undefs so we can send all the info
                endva = lva + lsize
                while lva < endva:
                    uname = self.getName(lva)
                    ucmnt = self.getComment(lva)
                    if uname is not None:
                        names[lva] = uname
                    if ucmnt is not None:
                        comments[lva] = ucmnt
                    #ret.append(((lva, 1, LOC_UNDEF, None), self.getName(lva), False, self.getComment(lva)))
                    lva += 1

            elif ltype == LOC_OP:
                extras[lva] = self.parseOpcode(lva)

            elif ltype == LOC_STRUCT:
                extras[lva] = self.getStructure(lva, tinfo)

        return locs, funcs, names, comments, extras

    def getPrevLocation(self, va, adjacent=True):
        """
        Get the previous location behind this one.  If adjacent
        is true, only return a location which is IMMEDIATELY behind
        the given va, otherwise search backward for a location until
        you find one or hit the edge of the segment.
        """
        va -= 1
        ret = self.locmap.getMapLookup(va)
        if ret is not None:
            return ret
        if adjacent:
            return None
        va -= 1
        while va > 0:
            ret = self.locmap.getMapLookup(va)
            if ret is not None:
                return ret
            va -= 1
        return None

    def vaByName(self, name):
        return self.va_by_name.get(name, None)

    def getLocationByName(self, name):
        """
        Return a location object by the name of the
        location.
        """
        va = self.vaByName(name)
        if va is None:
            raise InvalidLocation(0, "Unknown Name: %s" % name)
        return self.getLocation(va)

    def getNames(self):
        """
        Return a list of tuples containing (va, name)
        """
        return list(self.name_by_va.items())

    def getName(self, va, smart=False):
        '''
        Returns the name of the specified virtual address (or None).

        Smart mode digs beyond simple name lookups, as follows:
        If va falls within a known function in the workspace, we return "funcname+<delta>".
        If not, and the va falls within a mapped binary, we return "filename+<delta>"
        '''
        name = self.name_by_va.get(va)

        if name is not None or not smart:
            return name

        # TODO: by previous symbol?

        # by function
        baseva = self.getFunction(va)
        basename = self.name_by_va.get(baseva, None)

        if self.isFunction(va):
            basename = 'sub_0%x' % va

        # by filename
        if basename is None:
            basename = self.getFileByVa(va)
            if basename is None:
                return None

            baseva = self.getFileMeta(basename, 'imagebase')

        delta = va - baseva

        if delta:
            pom = ('', '+')[delta>0]
            name = "%s%s%s" % (basename, pom, hex(delta))
        else:
            name = basename
        return name

    def makeName(self, va, name, filelocal=False, makeuniq=False):
        """
        Set a readable name for the given location by va. There
        *must* be a Location defined for the VA before you may name
        it.  You may set a location's name to None to remove a name.

        makeuniq allows Vivisect to append some number to make the name unique.
        This behavior allows for colliding names (eg. different versions of a function)
        to coexist in the same workspace.

        default behavior is to fail on duplicate (False).
        """
        if filelocal:
            segtup = self.getSegment(va)
            if segtup is None:
                self.vprint("Failed to find file for 0x%.8x (%s) (and filelocal == True!)"  % (va, name))
            if segtup is not None:
                fname = segtup[SEG_FNAME]
                if fname is not None:
                    name = "%s.%s" % (fname, name)

        oldva = self.vaByName(name)
        # If that's already the name, ignore the event
        if oldva == va:
            return

        if oldva is not None:
            if not makeuniq:
                raise DuplicateName(oldva, va, name)

            else:
                logger.debug('makeName: %r already lives at 0x%x', name, oldva)
                # tack a number on the end
                index = 0
                newname = "%s_%d" % (name, index)
                newoldva = self.vaByName(newname)
                while self.vaByName(newname) not in (None, newname):
                    # if we run into the va we're naming, that's the name still
                    if newoldva == va:
                        return newname
                    logger.debug('makeName: %r already lives at 0x%x', newname, newoldva)
                    index += 1
                    newname = "%s_%d" % (name, index)
                    newoldva = self.vaByName(newname)

                name = newname

        self._fireEvent(VWE_SETNAME, (va,name))
        return name

    def saveWorkspace(self, fullsave=True):

        if self.server is not None:
            return

        modname = self.getMeta("StorageModule")
        filename = self.getMeta("StorageName")
        if modname is None:
            raise Exception("StorageModule not specified!")
        if filename is None:
            raise Exception("StorageName not specified!")

        # Usually this is "vivisect.storage.basicfile
        mod = self.loadModule(modname)

        # If they specified a full save, *or* this event list
        # has never been saved before, do a full save.
        if fullsave:
            mod.saveWorkspace(self, filename)
        else:
            mod.saveWorkspaceChanges(self, filename)

        self._createSaveMark()

    def loadFromFd(self, fd, fmtname=None, baseaddr=None):
        """
        Read the first bytes of the file descriptor and see if we can identify the type.
        If so, load up the parser for that file type, otherwise raise an exception.

        Returns the file md5
        """
        mod = None
        fd.seek(0)
        if fmtname is None:
            bytes = fd.read(32)
            fmtname = viv_parsers.guessFormat(bytes)

        mod = viv_parsers.getParserModule(fmtname)
        if hasattr(mod, "config"):
            self.mergeConfig(mod.config)

        fd.seek(0)
        fname = mod.parseFd(self, fd, filename=None, baseaddr=baseaddr)

        outfile = hashlib.md5(fd.read()).hexdigest()
        self.initMeta("StorageName", outfile+".viv")

        # Snapin our analysis modules
        self._snapInAnalysisModules()

        return fname

    def loadParsedBin(self, pbin, fmtname=None, baseaddr=None):
        '''
        Load an already parsed PE or Elf file into the workspace. Raises an exception if
        the file isn't one of those two.

        Returns the file md5
        '''
        fd = pbin.fd
        fd.seek(0)
        if fmtname is None:
            byts = fd.read(32)
            fmtname = viv_parsers.guessFormat(byts)

        filename = hashlib.md5(fd.read()).hexdigest()

        mod = viv_parsers.getParserModule(fmtname)
        if hasattr(mod, "config"):
            self.mergeConfig(mod.config)

        if fmtname == 'pe':
            mod.loadPeIntoWorkspace(self, pbin)
        elif fmtname == 'elf':
            mod.loadElfIntoWorkspace(self, pbin)
        else:
            raise Exception('Failed to load in the parsed module for format %s', fmtname)

        self.initMeta("StorageName", filename+".viv")
        self._snapInAnalysisModules()

        return fname

    def _saveSymbolCaches(self):

        if not self.config.vdb.SymbolCacheActive:
            return

        pathstr = self.config.vdb.SymbolCachePath
        symcache = e_symcache.SymbolCachePath(pathstr)

        symsbyfile = collections.defaultdict(list)

        # Get the image base addresses
        imgbases = {}
        for fname in self.getFiles():
            imgbases[ fname ] = self.getFileMeta(fname,'imagebase')

        for va,name in self.name_by_va.items():
            mmap = self.getMemoryMap(va)
            if mmap is None:
                continue

            symva = va - imgbases.get(mmap[3], va)
            if symva:

                symtype = e_resolv.SYMSTOR_SYM_SYMBOL
                if self.isFunction(va):
                    symtype = e_resolv.SYMSTOR_SYM_FUNCTION

                symsbyfile[mmap[3]].append((symva, 0, name, symtype))

        for filenorm, symtups in symsbyfile.items():
            symhash = self.getFileMeta(filenorm, 'SymbolCacheHash')
            if symhash is None:
                continue

            self.vprint('Saving Symbol Cache: %s (%d syms)' % (symhash,len(symtups)))
            symcache.setCacheSyms( symhash, symtups )

    def loadFromFile(self, filename, fmtname=None, baseaddr=None):
        """
        Read the first bytes of the file and see if we can identify the type.
        If so, load up the parser for that file type, otherwise raise an exception.
        ( if it's a workspace, trigger loadWorkspace() as a convenience )

        Returns the basename the file was given on load.
        """
        mod = None
        if fmtname is None:
            fmtname = viv_parsers.guessFormatFilename(filename)

        if fmtname in STORAGE_MAP:
            self.setMeta('StorageModule', STORAGE_MAP[fmtname])
            self.loadWorkspace(filename)
            return self.normFileName(filename)

        mod = viv_parsers.getParserModule(fmtname)
        fname = mod.parseFile(self, filename=filename, baseaddr=baseaddr)

        self.initMeta("StorageName", filename+".viv")

        # Snapin our analysis modules
        self._snapInAnalysisModules()

        return fname

    def loadFromMemory(self, memobj, baseaddr, fmtname=None):
        """
        Load a memory map (or potentially a mapped binary file)
        from the memory object's map at baseaddr.
        """
        mod = None
        if fmtname is None:
            bytez = memobj.readMemory(baseaddr, 32)
            fmtname = viv_parsers.guessFormat(bytez)

        # TODO: Load workspace from memory?
        mod = viv_parsers.getParserModule(fmtname)
        mod.parseMemory(self, memobj, baseaddr)

        mapva, mapsize, mapperm, mapfname = memobj.getMemoryMap(baseaddr)
        if not mapfname:
            mapfname = 'mem_map_%.8x' % mapva

        self.initMeta('StorageName', mapfname+".viv")
        # Snapin our analysis modules
        self._snapInAnalysisModules()

    def getFiles(self):
        """
        Return the current list of file objects in this
        workspace.
        """
        return list(self.filemeta.keys())

    def normFileName(self, filename):
        normname = os.path.basename(filename).lower()

        # Strip off an extension
        if normname.find('.') != -1:
            parts = normname.split('.')
            normname = '_'.join(parts[:-1])

        ok = string.ascii_letters + string.digits + '_'

        chars = list(normname)
        for i in range(len(chars)):
            if chars[i] not in ok:
                chars[i] = '_'

        normname = ''.join(chars)
        #if normname[0].isdigit():
            #normname = '_' + normname

        return normname

    def addFile(self, filename, imagebase, md5sum):
        """
        Create and add a new vivisect File object for the
        specified information.  This will return the file
        object which you may then use to do things like
        add imports/exports/segments etc...
        """
        nname = self.normFileName(filename)
        if nname in self.filemeta:
            raise Exception("Duplicate File Name: %s" % nname)
        self._fireEvent(VWE_ADDFILE, (nname, imagebase, md5sum))
        return nname

    def addEntryPoint(self, va):
        '''
        Add an entry point to the definition for the given file.  This
        will hint the analysis system to create functions when analysis
        is run.

        NOTE: No analysis is triggered by this function.
        '''
        self.setVaSetRow('EntryPoints', (va,))

    def getEntryPoints(self):
        '''
        Get all the parsed entry points for all the files loaded into the
        workspace.

        Example:  for va in vw.getEntryPoints():
        '''
        return [ x for x, in self.getVaSetRows('EntryPoints') ]

    def setFileMeta(self, fname, key, value):
        """
        Store a piece of file specific metadata (python primatives are best for values)
        """
        if fname not in self.filemeta:
            raise Exception("Invalid File: %s" % fname)
        self._fireEvent(VWE_SETFILEMETA, (fname, key, value))

    def getFileMeta(self, filename, key, default=None):
        """
        Retrieve a piece of file specific metadata
        """
        d = self.filemeta.get(filename)
        if d is None:
            raise Exception("Invalid File: %s" % filename)
        return d.get(key, default)

    def getFileMetaDict(self, filename):
        '''
        Retrieve the file metadata for this file as a key:val dict.
        '''
        d = self.filemeta.get(filename)
        if d is None:
            raise Exception('Invalid File: %s' % filename)
        return d

    def getFileByVa(self, va):
        segtup = self.getSegment(va)
        if segtup is None:
            return None
        return segtup[SEG_FNAME]

    def getLocationDistribution(self):
        # NOTE: if this changes, don't forget the report module!
        totsize = 0
        for mapva, mapsize, mperm, mname in self.getMemoryMaps():
            totsize += mapsize
        loctot = 0
        ret = {}
        for i in range(LOC_MAX):
            cnt = 0
            size = 0
            for lva,lsize,ltype,tinfo in self.getLocations(i):
                cnt += 1
                size += lsize
            loctot += size

            tname = loc_type_names.get(i, 'Unknown')
            ret[i] = (tname, cnt, size, int((size/float(totsize))*100))

        # Update the undefined based on totals...
        undeftot = totsize-loctot
        ret[LOC_UNDEF] = ('Undefined', 0, undeftot, int((undeftot/float(totsize)) * 100))

        return ret

#################################################################
#
#  VA Set API
#

    def getVaSetNames(self):
        """
        Get a list of the names of the current VA lists.
        """
        return list(self.vasets.keys())

    def getVaSetDef(self, name):
        """
        Get the list of (name, type) pairs which make up the
        rows for this given VA set (the first one *always* the VA, but
        you can name it as you like...)
        """
        x = self.vasetdefs.get(name)
        if x is None:
            raise InvalidVaSet(name)
        return x

    def getVaSetRows(self, name):
        """
        Get a list of the rows in this VA set.
        """
        x = self.vasets.get(name)
        if x is None:
            raise InvalidVaSet(name)
        # yes, this is weird. but it's how python2 returns values()
        return list(x.values())

    def getVaSet(self, name):
        """
        Get the dictionary of va:<rowdata> entries.
        """
        x = self.vasets.get(name)
        if x is None:
            raise InvalidVaSet(name)
        return x

    def addVaSet(self, name, defs, rows=()):
        """
        Add a va set:

        name - The name for this VA set
        defs - List of (<name>,<type>) tuples for the rows (va is always first)
        rows - An initial set of rows for values in this set.
        """
        self._fireEvent(VWE_ADDVASET, (name, defs, rows))

    def delVaSet(self, name):
        """
        Delete a VA set by name.
        """
        if name not in self.vasets:
            raise Exception("Unknown VA Set: %s" % name)
        self._fireEvent(VWE_DELVASET, name)

    def setVaSetRow(self, name, rowtup):
        """
        Use this API to update the row data for a particular
        entry in the VA set.
        """
        self._fireEvent(VWE_SETVASETROW, (name, rowtup))

    def getVaSetRow(self, name, va):
        '''
        Retrieve the va set row for va in the va set named name.

        Example:
            row = vw.getVaSetRow('WootFunctions', fva)
        '''
        vaset = self.vasets.get( name )
        if vaset is None:
            return None
        return vaset.get( va )

    def delVaSetRow(self, name, va):
        """
        Use this API to delete the rowdata associated
        with the specified VA from the set.
        """
        if name not in self.vasets:
            raise Exception("Unknown VA Set: %s" % name)
        self._fireEvent(VWE_DELVASETROW, (name, va))

#################################################################
#
#  Shared Workspace APIs
#
    def chat(self, msg):
        uname = e_config.getusername()
        # FIXME this should be part of a UI event model.
        self._fireEvent(VWE_CHAT, (uname, msg))

    def iAmLeader(self, winname):
        '''
        Announce that your workspace is leading a window with the
        specified name.  This allows others to opt-in to following
        the nav events for the given window name.

        Example:
            vw.iAmLeader('WindowTitle')
        '''
        if not self.server:
            raise Exception('iAmLeader() requires being connected to a server.')

        user = e_config.getusername()
        self.server._fireEvent(VTE_MASK | VTE_IAMLEADER, (user,winname))

    def followTheLeader(self, winname, expr):
        '''
        Announce a new memory expression to navigate to if if a given window
        is following the specified user/winname

        Example:
            vw.followTheLeader('FunExample', 'sub_08042323')
        '''
        if not self.server:
            raise Exception('followTheLeader() requires being connected to a server.')
        user = e_config.getusername()
        self.server._fireEvent(VTE_MASK | VTE_FOLLOWME, (user,winname, expr))

#################################################################
#
#  Color Map API
#

    def getColorMaps(self):
        """
        Return a list of the names of the given color maps
        """
        return list(self.colormaps.keys())

    def addColorMap(self, mapname, colormap):
        """
        Add a colormap dictionary with the given name for the map.
        (A colormap dictionary is va:color entries)
        """
        self._fireEvent(VWE_ADDCOLOR, (mapname, colormap))

    def delColorMap(self, mapname):
        self._fireEvent(VWE_DELCOLOR, mapname)

    def getColorMap(self, mapname):
        """
        Return the colormap dictionary for the given map name.
        """
        return self.colormaps.get(mapname)

    def _getNameParts(self, name, va):
        '''
        Return the given name in three parts:
        fpart: filename, if applicable (for file-local names)
        npart: base name
        vapart: address, if tacked on the end

        If any of these are not applicable, they will return None for that field.
        '''
        fpart = None
        npart = name
        vapart = None
        fname = self.getFileByVa(va)
        vastr = '_%.8x' % va

        if name.startswith(fname + '.'):
            fpart, npart = name.split('.', 1)
        elif name.startswith('*.'):
            skip, npart = name.split('.', 1)

        if npart.endswith(vastr) and not npart == 'sub' + vastr:
            npart, vapart = npart.rsplit('_', 1)

        return fpart, npart, vapart


    def _addNamePrefix(self, name, va, prefix, joinstr=''):
        '''
        Add a prefix to the given name paying attention to the filename prefix, and
        any VA suffix which may exist.
        '''
        fpart, npart, vapart = self._getNameParts(name, va)
        if fpart is None and vapart is None:
            name = joinstr.join([prefix, npart])

        elif vapart is None:
            name = fpart + '.' + joinstr.join([prefix, npart])

        elif fpart is None:
            name = joinstr.join([prefix, npart])

        else:
            name = fpart + '.' + joinstr.join([prefix, npart]) + '_%s' % vapart
        return name


##########################################################
#
# The envi.symstore.resolver.SymbolResolver API...
#
    def getSymByName(self, name):

        # Check for a sym
        va = self.vaByName(name)
        if va is not None:
            return e_resolv.Symbol(name, va, 0)

        # check for the need for a deref.
        d = self.filemeta.get(name)
        if d is not None:
            return VivFileSymbol(self, name, d.get("imagebase"), 0, self.psize)

    def getSymByAddr(self, addr, exact=True):
        name = self.getName(addr)
        if name is None:
            if self.isValidPointer(addr):
                name = "loc_%.8x" % addr

        if name is not None:
            #FIXME fname
            #FIXME functions/segments/etc...
            return e_resolv.Symbol(name, addr, 0)

    def setSymHint(self, va, idx, hint):
        '''
        Set a symbol hint which will be used in place of operand
        values during disassembly among other things...

        You may also set hint=None to delete sym hints.
        '''
        self._fireEvent(VWE_SYMHINT, (va, idx, hint))

    def getSymHint(self, va, idx):
        h = self.getFref(va, idx)
        if h is not None:
            f = self.getFunction(va)
            loctup = self.getFunctionLocal(f, h)
            if loctup:
                return loctup[1]

        return self.symhints.get((va, idx), None)


class VivFileSymbol(e_resolv.FileSymbol):
    # A namespace tracker thingie...
    def __init__(self, vw, fname, base, size, width=4):
        self.vw = vw
        e_resolv.FileSymbol.__init__(self, fname, base, size, width)

    def getSymByName(self, name):
        return self.vw.getSymByName("%s.%s" % (self.name, name))


def getVivPath(*pathents):
    dname = os.path.dirname(__file__)
    dname = os.path.abspath(dname)
    return os.path.join(dname, *pathents)


##############################################################################
# The following are touched during the release process by bump2version.
# You should have no reason to modify these directly
version = (1, 0, 4)
verstring = '.'.join([str(x) for x in version])
commit = ''
