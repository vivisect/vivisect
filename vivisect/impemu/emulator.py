import struct
import traceback
import itertools

import envi
import envi.bits as e_bits
import envi.memory as e_mem
import envi.registers as e_reg

import visgraph.pathcore as vg_path

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
        self.taintva = itertools.count(0x41560000, 8192)

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
            if val == None:
                continue

            impname = getattr(val, '__imphook__',None)
            if impname == None:
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
            taints = [ self.setVivTaint('funcstack', i * self.psize) for i in xrange(20) ]
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
                                    for i in xrange(new_map_size)])

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
        if op == None:
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
            api = self.getCallApi(endeip)
            rtype,rname,convname,callname,funcargs = api
            callconv = self.getCallingConvention(convname)
            argv = callconv.getCallArgs(self, len(funcargs))

            ret = None
            if self.emumon != None:
                try:
                    ret = self.emumon.apicall(self, op, endeip, api, argv)
                except Exception, e:
                    self.emumon.logAnomaly(self, endeip, "%s.apicall failed: %s" % (self.emumon.__class__.__name__, e))

            hook = self.hooks.get(callname)
            if ret == None and hook:
                hook( self, callconv, api, argv )

            else:

                if ret == None:
                    ret = self.setVivTaint('apicall', (op,endeip,api,argv))

                callconv.execCallReturn( self, ret, len(funcargs) )

            # Either way, if it's a call PC goes to next instruction
            if self._func_only:
                self.setProgramCounter(starteip+len(op))

        return iscall

    def newCodePathNode(self, parent=None, bva=None):
        '''
        NOTE: Right now, this is only called from the actual branch state which
        needs it.  it must stay that way for now (register context is being copied
        for symbolic emulator...)
        '''
        props = {
            'bva':bva,    # the entry virtual address for this branch
            'valist':[],  # the virtual addresses in this node in order
            'calllog':[], # FIXME is this even used?
            'readlog':[], # a log of all memory reads from this block
            'writelog':[],# a log of all memory writes from this block
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

        ret = []
        # Add all the known branches to the list
        blist = op.getBranches(emu=self)

        # FIXME this should actually check for conditional...
        # If there is more than one branch target, we need a new code block
        if len(blist) > 1:
            for bva,bflags in blist:
                if bva == None:
                    logger.warn("Unresolved branch even WITH an emulator?")
                    continue

                bpath = self.getBranchNode(self.curpath, bva)
                ret.append((bva, bpath))

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
        todo = [(funcva,self.getEmuSnap(),self.path),]
        vw = self.vw # Save a dereference many many times

        while len(todo):

            va,esnap,self.curpath = todo.pop()

            self.setEmuSnap(esnap)

            self.setProgramCounter(va)

            # Check if we are beyond our loop max...
            if maxloop != None:
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
                if maxhit != None:
                    h = hits.get(starteip, 0)
                    h += 1
                    if h > maxhit:
                        break
                    hits[starteip] = h

                # If we ran out of path (branches that went
                # somewhere that we couldn't follow?
                if self.curpath == None:
                    break

                try:

                    # FIXME unify with stepi code...
                    op = self.parseOpcode(starteip)
                    self.op = op
                    if self.emumon:
                        try:
                            self.emumon.prehook(self, op, starteip)
                        except Exception, e:
                            print("funcva: 0x%x opva: 0x%x:  %r   %r (in emumon prehook)" % (funcva, starteip, op, e))


                        if self.emustop:
                            return 

                    # Execute the opcode
                    self.executeOpcode(op)
                    vg_path.getNodeProp(self.curpath, 'valist').append(starteip)

                    endeip = self.getProgramCounter()

                    if self.emumon:
                        try:
                            self.emumon.posthook(self, op, endeip)
                        except Exception, e:
                            print("funcva: 0x%x opva: 0x%x:  %r   %r (in emumon posthook)" % (funcva, starteip, op, e))

                        if self.emustop:
                            return 

                    iscall = self.checkCall(starteip, endeip, op)
                    if self.emustop:
                        return

                    # If it wasn't a call, check for branches, if so, add them to
                    # the todo list and go around again...
                    if not iscall:
                        blist = self.checkBranches(starteip, endeip, op)
                        if len(blist):
                            # pc in the snap will be wrong, but over-ridden at restore
                            esnap = self.getEmuSnap()
                            for bva,bpath in blist:
                                todo.append((bva, esnap, bpath))
                            break

                    # If we enounter a procedure exit, it doesn't
                    # matter what EIP is, we're done here.
                    if op.iflags & envi.IF_RET:
                        vg_path.setNodeProp(self.curpath, 'cleanret', True)
                        break

                except envi.UnsupportedInstruction, e:
                    if self.strictops:
                        logger.debug('runFunction failed: unsupported instruction: 0x%08x %s', e.op.va, e.op.mnem)
                        break
                    else:
                        logger.debug('runFunction continuing after unsupported instruction: 0x%08x %s' % (e.op.va, e.op.mnem))
                        self.setProgramCounter(e.op.va+ e.op.size)
                except Exception, e:
                    #traceback.print_exc()
                    if self.emumon != None:
                        self.emumon.logAnomaly(self, starteip, str(e))

                    break # If we exc during execution, this branch is dead.

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
            if ret != None:
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
        return self.taintva.next() + 4096

    def setVivTaint(self, typename, taint):
        '''
        Set a taint in the emulator.  Returns the new value for
        the created taint.
        '''
        va = self.nextVivTaint()
        self.taints[ va & 0xffffe000 ] = (va,typename,taint)
        return va

    def getVivTaint(self, va):
        '''
        Retrieve a previously registered taint ( this will automagically
        mask values down and allow you to retrieve "near taint" values.)
        '''
        return self.taints.get( va & 0xffffe000 )

    def reprVivTaint(self, taint):
        '''
        For the base "known" taint types, return a humon readable string
        to represent the value of the taint.
        '''
        va,ttype,tinfo = taint
        if ttype == 'uninitreg':
            return self.getRegisterName(tinfo)

        if ttype == 'import':
            lva,lsize,ltype,linfo = tinfo
            return linfo

        if ttype == 'dynlib':
            libname = tinfo
            return libname

        if ttype == 'dynfunc':
            libname,funcname = tinfo
            return '%s.%s' % (libname,funcname)

        if ttype == 'funcstack':
            stackoff = tinfo
            if self.funcva:
                flocal = self.vw.getFunctionLocal(self.funcva, stackoff)
                if flocal != None:
                    typename,argname = flocal
                    return argname

            o = '+'
            if stackoff < 0:
                o = '-'

            return 'sp%s%d' % (o, abs(stackoff))

        if ttype == 'apicall':
            op,pc,api,argv = tinfo
            rettype,retname,callconv,callname,callargs = api
            callstr = self.reprVivValue( pc )
            argsstr = ','.join([ self.reprVivValue( x ) for x in argv])
            return '%s(%s)' % (callstr,argsstr)

        return 'taint: 0x%.8x %s %r' % (va, ttype, tinfo)

    def reprVivValue(self, val):
        '''
        Return a humon readable string which is the best description for
        the given value ( given knowledge of the workspace, emu,
        and taint subsystems ).
        '''
        if self.vw.isFunction(val):
            thunk = self.vw.getFunctionMeta(val,'Thunk')
            if thunk:
                return thunk

        vivname = self.vw.getName(val)
        if vivname:
            return vivname

        taint = self.getVivTaint(val)
        if taint:
            # NOTE we need to prevent infinite recursion due to args being
            # tainted and then referencing the same api call 
            va,ttype,tinfo = taint
            if ttype == 'apicall':
                op,pc,api,argv = tinfo
                rettype,retname,callconv,callname,callargs = api
                if val not in argv:
                    return self.reprVivTaint(taint)

        stackoff = self.getStackOffset(val)
        if stackoff != None:
            funclocal = self.vw.getFunctionLocal(self.funcva, stackoff)
            if funclocal != None:
                typename,varname = funclocal
                return varname

        if val < 4096:
            return str(val)

        return '0x%.8x' % val

    def _useVirtAddr(self, va):
        taint = self.getVivTaint(va)
        if taint == None:
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
        if loc != None:
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

