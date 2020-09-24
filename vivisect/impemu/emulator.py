import struct
import itertools

import envi
import envi.exc as e_exc
import envi.bits as e_bits
import envi.memory as e_mem

import visgraph.pathcore as vg_path

import vivisect.exc as v_exc

from vivisect.const import *

import logging
logger = logging.getLogger(__name__)

# Pre-initialize a default stack size
init_stack_size = 0x8000
init_stack_map = b'\xfe' * init_stack_size

def imphook(impname):

    def imptemp(f):
        f.__imphook__ = impname
        return f

    return imptemp

class WorkspaceEmulator:

    taintregs = []

    def __init__(self, vw, logwrite=False, logread=False):

        self.vw = vw
        self.funcva = None # Set if using runFunction
        self.emustop = False

        self.hooks = {}
        self.taints = {}
        self.taintva = itertools.count(0x4156000F, 0x2000)
        self.taintoffset = 0x1000
        self.taintmask = 0xffffe000
        self.taintrepr = {}

        self.uninit_use = {}
        self.logwrite = logwrite
        self.logread = logread
        self.path = self.newCodePathNode()
        self.curpath = self.path
        self.op = None
        self.opcache = {}
        self.emumon = None
        self.psize = self.getPointerSize()

        # Possibly need an "options" API?
        self._safe_mem = True   # Should we be forgiving about memory accesses?
        self._func_only = True  # is this emulator meant to stay in one function scope?

        self.strictops = True   # should we bail on emulation if unsupported instruction encountered

        # Map in all the memory associated with the workspace
        for va, size, perms, fname in vw.getMemoryMaps():
            offset, bytes = vw.getByteDef(va)
            self.addMemoryMap(va, perms, fname, bytes)

        for regidx in self.taintregs:
            rname = self.getRegisterName(regidx)
            regval = self.setVivTaint( 'uninitreg', regidx )
            self.setRegister(regidx, regval)

        for name in dir(self):
            val = getattr(self, name, None)
            if val is None:
                continue

            impname = getattr(val, '__imphook__',None)
            if impname is None:
                continue

            self.hooks[impname] = val

        self.stack_map_mask = None
        self.stack_map_base = None
        self.stack_map_top = None
        self.stack_pointer = None
        self.initStackMemory()

    def initStackMemory(self, stacksize=init_stack_size):
        '''
        Setup and initialize stack memory.
        You may call this prior to emulating instructions.
        '''
        if self.stack_map_base is None:
            self.stack_map_mask = e_bits.sign_extend(0xfff00000, 4, self.vw.psize)
            self.stack_map_base = e_bits.sign_extend(0xbfb00000, 4, self.vw.psize)
            self.stack_map_top = self.stack_map_base + stacksize
            self.stack_pointer = self.stack_map_top

            stack_map = init_stack_map
            if stacksize != init_stack_size:
                stack_map = b'\xfe' * stacksize

            # Map in a memory map for the stack

            self.addMemoryMap(self.stack_map_base, 6, "[stack]", stack_map)
            self.setStackCounter(self.stack_pointer)

            # Create some pre-made taints for positive stack indexes
            # NOTE: This is *ugly* for speed....
            taints = [ self.setVivTaint('funcstack', i * self.psize) for i in range(20) ]
            taintbytes = ''.join([ e_bits.buildbytes(taint,self.psize) for taint in taints ])

            self.writeMemory(self.stack_pointer, taintbytes)
        else:
            existing_map_size = self.stack_map_top - self.stack_map_base
            new_map_size = stacksize - existing_map_size
            if new_map_size < 0:
                raise RuntimeError('cannot shrink stack')

            new_map_top = self.stack_map_base
            new_map_base = new_map_top - new_map_size

            stack_map = ''.join([struct.pack('<I', new_map_base+(i*4))
                                    for i in range(new_map_size)])

            self.addMemoryMap(new_map_base, 6, "[stack]", stack_map)
            self.stack_map_base = new_map_base

            # no need to do tainting here, since SP will always be in the
            #   first map

    def stopEmu(self):
        '''
        This is called by monitor to stop emulation
        '''
        self.emustop = True

    def getPathProp(self, key):
        '''
        Retrieve a named value from the current code path context.
        '''
        return vg_path.getNodeProp(self.curpath, key)

    def setPathProp(self, key, value):
        """
        Set a named value which is only relevant for the current code path.
        """
        return vg_path.setNodeProp(self.curpath, key, value)

    def setEmulationMonitor(self, emumon):
        """
        Snap in an emulation monitor. (see EmulationMonitor doc from vivisect.impemu)
        """
        self.emumon = emumon

    def parseOpcode(self, va, arch=envi.ARCH_DEFAULT):
        # We can make an opcode *faster* with the workspace because of
        # getByteDef etc... use it.
        op = self.opcache.get(va)
        if op is None:
            op = envi.Emulator.parseOpcode(self, va, arch=arch)
            self.opcache[va] = op
        return op

    def checkCall(self, starteip, endeip, op):
        """
        Check if this was a call, and if so, do the required
        import emulation and such...
        """
        iscall = bool(op.iflags & envi.IF_CALL)
        if iscall:
            # Either way, if it's a call PC goes to next instruction
            if self._func_only:
                self.setProgramCounter(starteip+len(op))
            api = self.getCallApi(endeip)
            rtype, rname, convname, callname, funcargs = api
            callconv = self.getCallingConvention(convname)
            if callconv is None:
                return iscall

            argv = callconv.getCallArgs(self, len(funcargs))

            ret = None
            if self.emumon is not None:
                try:
                    ret = self.emumon.apicall(self, op, endeip, api, argv)
                except Exception as e:
                    self.emumon.logAnomaly(self, endeip, "%s.apicall failed: %s" % (self.emumon.__class__.__name__, e))

            hook = self.hooks.get(callname)
            if ret is None and hook:
                hook(self, callconv, api, argv)
            elif self._func_only:
                if ret is None:
                    ret = self.setVivTaint('apicall', (op, endeip, api, argv))
                callconv.execCallReturn(self, ret, len(funcargs))
            # no else since we'll emulate into the function

        return iscall

    def newCodePathNode(self, parent=None, bva=None):
        '''
        NOTE: Right now, this is only called from the actual branch state which
        needs it.  it must stay that way for now (register context is being copied
        for symbolic emulator...)
        '''
        props = {
            'bva': bva,      # the entry virtual address for this branch
            'valist': [],    # the virtual addresses in this node in order
            'readlog': [],   # a log of all memory reads from this block
            'writelog': [],  # a log of all memory writes from this block
        }
        ret = vg_path.newPathNode(parent=parent, **props)
        return ret

    def getBranchNode(self, node, bva):
        '''
        If a node exists already for the specified branch, return it. Otherwise,
        create a new one and return that...
        '''
        for knode in vg_path.getNodeKids(node):
            if vg_path.getNodeProp(knode, 'bva') == bva:
                return knode
        return self.newCodePathNode(node, bva)

    def checkBranches(self, starteip, endeip, op):
        """
        This routine gets the current branch list for this opcode, adds branch
        entries to the current path, and updates current path as needed
        (returns a list of (va, CodePath) tuples.
        """
        '''
        So I've kinda gone back and forth on this one a bit. On one hand, the emulator
        should be free to iterate over things as it needs. On the other, it's operating with
        imperfect information as to what's a valid path and what's not.
        '''
        vw = self.vw
        ret = []
        paths = set()
        # if we've already hunted this location down, know it's a table, and we've resolved it
        # step carefully so we don't conflate tables together
        xrefs = vw.getXrefsFrom(op.va, rtype=REF_CODE)
        branches = []
        for bva, bflags in op.getBranches(emu=None):
            if bflags & envi.BR_TABLE and vw.getLocation(op.va) and len(xrefs):
                for xrfrom, xrto, xrtype, xrflags in xrefs:
                    # if it's not in a codeblock it's probably something like an import, so we
                    # can ignore it
                    if self.vw.getCodeBlock(xrto) is None:
                        continue
                    if xrto in paths:
                        continue
                    bpath = self.getBranchNode(self.curpath, xrto)
                    ret.append((xrto, bpath))
                    paths.add(xrto)
                return ret

        # FIXME this should actually check for conditional...
        # If there is more than one branch target, we need a new code block
        blist = op.getBranches(emu=self)
        if len(blist) > 1:
            for bva, bflags in blist:
                if bva is None:
                    logger.warn("Unresolved branch even WITH an emulator?")
                    continue
                if bva in paths:
                    continue

                bpath = self.getBranchNode(self.curpath, bva)
                ret.append((bva, bpath))
                paths.add(bva)

        if op.iflags & envi.IF_BRANCH \
                and not op.iflags & envi.IF_COND \
                and len(xrefs):
                    # we've hit a branch that doesn't go anywhere.  probably a switchcase we don't handle here.
                    for xrfr, xrto, xrt, xrflag in xrefs:
                        # skip existing, skip DEREFS
                        if xrto in paths or xrflag & envi.BR_DEREF:
                            continue

                        bpath = self.getBranchNode(self.curpath, xrto)
                        ret.append((xrto, bpath))
                        paths.add(xrto)

        # let's also take into account some of the dynamic branches we may have found
        # like our table pointers

        return ret

    def stepi(self):
        # NOTE: when we step, we *always* want to be stepping over calls
        # (and possibly import emulate them)
        starteip = self.getProgramCounter()

        # parse out an opcode
        op = self.parseOpcode(starteip)
        if self.emumon:
            self.emumon.prehook(self, op, starteip)

        # Execute the opcode
        self.executeOpcode(op)
        vg_path.getNodeProp(self.curpath, 'valist').append(starteip)

        endeip = self.getProgramCounter()

        if self.emumon:
            self.emumon.posthook(self, op, endeip)

        if not self.checkCall(starteip, endeip, op):
            self.checkBranches(starteip, endeip, op)

    def runFunction(self, funcva, stopva=None, maxhit=None, maxloop=None):
        """
        This is a utility function specific to WorkspaceEmulation (and impemu) that
        will emulate, but only inside the given function.  You may specify a stopva
        to return once that location is hit.
        """

        self.funcva = funcva

        # Let the current (should be base also) path know where we are starting
        vg_path.setNodeProp(self.curpath, 'bva', funcva)
        hits = {}
        todo = [(funcva, self.getEmuSnap(), self.path)]
        vw = self.vw  # Save a dereference many many times

        while len(todo):

            va, esnap, self.curpath = todo.pop()

            self.setEmuSnap(esnap)

            self.setProgramCounter(va)

            # Check if we are beyond our loop max...
            if maxloop is not None:
                lcount = vg_path.getPathLoopCount(self.curpath, 'bva', va)
                if lcount > maxloop:
                    continue

            while True:

                starteip = self.getProgramCounter()

                if not vw.isValidPointer(starteip):
                    break

                if starteip == stopva:
                    return

                # Check straight hit count...
                if maxhit is not None:
                    h = hits.get(starteip, 0)
                    h += 1
                    if h > maxhit:
                        break
                    hits[starteip] = h

                # If we ran out of path (branches that went
                # somewhere that we couldn't follow)?
                if self.curpath is None:
                    break

                try:
                    # FIXME unify with stepi code...
                    op = self.parseOpcode(starteip)
                    self.op = op
                    if self.emumon:
                        try:
                            self.emumon.prehook(self, op, starteip)
                        except v_exc.BadOpBytes as e:
                            logger.debug(str(e))
                        except Exception as e:
                            if not self.getMeta('silent'):
                                logger.warn("Emulator prehook failed on fva: 0x%x, opva: 0x%x, op: %s, err: %s", funcva, starteip, str(op), str(e))

                        if self.emustop:
                            return
                    # Execute the opcode
                    self.executeOpcode(op)
                    vg_path.getNodeProp(self.curpath, 'valist').append(starteip)

                    endeip = self.getProgramCounter()

                    if self.emumon:
                        try:
                            self.emumon.posthook(self, op, endeip)
                        except v_exc.BadOpBytes as e:
                            logger.debug(str(e))
                        except Exception as e:
                            if not self.getMeta('silent'):
                                logger.warn("funcva: 0x%x opva: 0x%x:  %r   (%r) (in emumon posthook)", funcva, starteip, op, e)

                        if self.emustop:
                            return
                    iscall = self.checkCall(starteip, endeip, op)
                    if self.emustop:
                        return

                    # TODO: hook things like error(...) when they have a param that indicates to 
                    # exit. Might be a bit hairy since we'll possibly have to fix up codeblocks
                    if self.vw.isNoReturnVa(endeip):
                        vg_path.setNodeProp(self.curpath, 'cleanret', False)
                        break

                    # If it wasn't a call, check for branches, if so, add them to
                    # the todo list and go around again...
                    if not iscall:
                        blist = self.checkBranches(starteip, endeip, op)
                        if len(blist):
                            # pc in the snap will be wrong, but over-ridden at restore
                            esnap = self.getEmuSnap()
                            for bva, bpath in blist:
                                todo.append((bva, esnap, bpath))
                            break

                    # If we enounter a procedure exit, it doesn't
                    # matter what EIP is, we're done here.
                    if op.iflags & envi.IF_RET:
                        vg_path.setNodeProp(self.curpath, 'cleanret', True)
                        break
                except envi.UnsupportedInstruction as e:
                    if self.strictops:
                        logger.debug('runFunction failed: unsupported instruction: 0x%08x %s', e.op.va, e.op.mnem)
                        break
                    else:
                        logger.debug('runFunction continuing after unsupported instruction: 0x%08x %s', e.op.va, e.op.mnem)
                        self.setProgramCounter(e.op.va + e.op.size)
                except Exception as e:
                    if self.emumon is not None and not isinstance(e, e_exc.BreakpointHit):
                        self.emumon.logAnomaly(self, starteip, str(e))

                    break  # If we exc during execution, this branch is dead.

    def getCallApi(self, va):
        '''
        Retrieve an API definition from either the vivisect workspace
        ( if the call target is a function within the workspace ) or
        the impapi definition subsystem ( if the call target is a known
        import definition )
        '''
        vw = self.vw
        ret = None

        if vw.isFunction(va):
            ret = vw.getFunctionApi(va)
            if ret is not None:
                return ret

        else:

            taint = self.getVivTaint(va)
            if taint:
                tva,ttype,tinfo = taint

                if ttype == 'import':
                    lva,lsize,ltype,linfo = tinfo
                    ret = vw.getImpApi( linfo )

                elif ttype == 'dynfunc':
                    libname,funcname = tinfo
                    ret = vw.getImpApi('%s.%s' % (libname,funcname))

                if ret:
                    return ret

        defcall = vw.getMeta("DefaultCall")
        return ('int', None, defcall, 'UnknownApi', () )

    def nextVivTaint(self):
        # One page into the new taint range
        return self.taintva.next() + self.taintoffset

    def setVivTaint(self, typename, taint):
        '''
        Set a taint in the emulator.  Returns the new value for
        the created taint.
        '''
        va = self.nextVivTaint()
        self.taints[ va & self.taintmask ] = (va,typename,taint)
        return va

    def getVivTaint(self, va):
        '''
        Retrieve a previously registered taint ( this will automagically
        mask values down and allow you to retrieve "near taint" values.)
        '''
        return self.taints.get( va & self.taintmask )

    def reprVivTaint(self, taint):
        '''
        For the base "known" taint types, return a humon readable string
        to represent the value of the taint.
        '''

        va, ttype, tinfo = taint

        if ttype == 'uninitreg':
            trepr = self.getRegisterName(tinfo)
        elif ttype == 'import':
            lva,lsize,ltype,linfo = tinfo
            trepr = linfo
        elif ttype == 'dynlib':
            libname = tinfo
            trepr = libname
        elif ttype == 'dynfunc':
            libname,funcname = tinfo
            trepr = '%s.%s' % (libname,funcname)
        elif ttype == 'funcstack':
            stackoff = tinfo
            if self.funcva:
                flocal = self.vw.getFunctionLocal(self.funcva, stackoff)
                if flocal is not None:
                    typename,argname = flocal
                    return argname
            o = '+'
            if stackoff < 0:
                o = '-'
            trepr = 'sp%s%d' % (o, abs(stackoff))
        elif ttype == 'apicall':
            op, pc, api, argv = tinfo
            if op.va in self.taintrepr:
                return '<0x%.8x>' % op.va
            rettype, retname, callconv, callname, callargs = api
            callstr = self.reprVivValue(pc)
            argsstr = ','.join([self.reprVivValue(x) for x in argv])
            trepr = '%s(%s)' % (callstr, argsstr)
            self.taintrepr[op.va] = trepr
        else:
            trepr = 'taint: 0x%.8x %s %r' % (va, ttype, tinfo)

        return trepr

    def reprVivValue(self, val):
        '''
        Return a humon readable string which is the best description for
        the given value ( given knowledge of the workspace, emu,
        and taint subsystems ).
        '''
        if self.vw.isFunction(val):
            thunk = self.vw.getFunctionMeta(val, 'Thunk')
            if thunk:
                return thunk

        vivname = self.vw.getName(val)
        if vivname:
            return vivname

        taint = self.getVivTaint(val)
        if taint:
            va, ttype, tinfo = taint
            if ttype == 'apicall':
                op, pc, api, argv = tinfo
                rettype, retname, callconv, callname, callargs = api
                if val not in argv:
                    return self.reprVivTaint(taint)

        stackoff = self.getStackOffset(val)
        if stackoff is not None:
            funclocal = self.vw.getFunctionLocal(self.funcva, stackoff)
            if funclocal is not None:
                typename, varname = funclocal
                return varname

        if val < 4096:
            return str(val)

        return '0x%.8x' % val

    def _useVirtAddr(self, va):
        taint = self.getVivTaint(va)
        if taint is None:
            return

        tva,ttype,tinfo = taint

        if ttype == 'uninitreg':
            self.logUninitRegUse(tinfo)

    def writeMemory(self, va, bytes):
        """
        Try to write the bytes to the memory object, otherwise, dont'
        complain...
        """
        if self.logwrite:
            wlog = vg_path.getNodeProp(self.curpath, 'writelog')
            wlog.append((self.getProgramCounter(),va,bytes))

        self._useVirtAddr( va )

        # It's totally ok to write to invalid memory during the
        # emulation pass (as long as safe_mem is true...)
        probeok = self.probeMemory(va, len(bytes), e_mem.MM_WRITE)
        if self._safe_mem and not probeok:
            return

        return e_mem.MemoryObject.writeMemory(self, va, bytes)

    def logUninitRegUse(self, regid):
        self.uninit_use[regid] = True

    def getUninitRegUse(self):
        return self.uninit_use.keys()

    def readMemory(self, va, size):
        if self.logread:
            rlog = vg_path.getNodeProp(self.curpath, 'readlog')
            rlog.append((self.getProgramCounter(),va,size))

        # If they read an import entry, start a taint...
        loc = self.vw.getLocation(va)
        if loc is not None:
            lva, lsize, ltype, ltinfo = loc
            if ltype == LOC_IMPORT and lsize == size: # They just read an import.
                ret = self.setVivTaint('import', loc)
                return e_bits.buildbytes(ret, lsize)

        self._useVirtAddr(va)

        # Read from the emulator's pages if we havent resolved it yet
        probeok = self.probeMemory(va, size, e_mem.MM_READ)
        if self._safe_mem and not probeok:
            return 'A' * size

        return e_mem.MemoryObject.readMemory(self, va, size)

    # Some APIs for telling if pointers are in runtime memory regions

    def isUninitStack(self, val):
        """
        If val is a numerical value in the same memory page
        as the un-initialized stack values return True
        """
        #NOTE: If uninit_stack_byte changes, so must this!
        if (val & 0xfffff000) == 0xfefef000:
            return True
        return False

    def isStackPointer(self, va):
        return (va & self.stack_map_mask) == self.stack_map_base

    def getStackOffset(self, va):
        if (va & self.stack_map_mask) == self.stack_map_base:
            return va - self.stack_pointer

