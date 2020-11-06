import visgraph.pathcore as vg_pathcore
import vivisect.tools.graphutil as viv_graph
import vivisect.symboliks.effects as vsym_effects
import vivisect.symboliks.emulator as vsym_emulator

from vivisect.const import *
from vivisect.symboliks.common import *

import visgraph.graphcore as v_graphcore

class SymbolikFunctionGraph(v_graphcore.HierGraph):

    def __init__(self):
        v_graphcore.HierGraph.__init__(self)
        self.vamap = {} # va->node mapping ( even if it's not the entry )
        self.opmap = {}

    def getVaNode(self, va):
        '''
        This should *only* be called for virtual addresses
        which represent the "entry" point for a code block.

        ( in cases where the VA exists as part of an existing
        block, that block will be split in order to allow
        seperate "block" refs )
        '''
        #node = self.getNode(va)
        #if node is None:

    #def addNodeOpcode(self, node, op):
        #'''
        #'''

    #def getVaNode(self):
    #def addSymEffects(self, node, 

class SymbolikFunctionEmulator(vsym_emulator.SymbolikEmulator):
    '''
    A special symbolik emulator specifically extended for use in
    emulating functions (with things like calling conventions, etc...)
    '''
    __width__ = 4 # this *must* be set by extenders if needed!

    def __init__(self, vw):
        vsym_emulator.SymbolikEmulator.__init__(self, vw)
        self.cconvs = {}
        self.cconv = None   # This will be set by setupFunctionCall

        #self.apimod = self.getApiModule()
        self.funchooks = {}

        self.stackdown = True # cheap plumbing assuming stacks grow down
        self.stackbase = None
        self.stacksize = None

    def setStackBase(self, stackbase, stacksize):
        '''
        Set the stack base discrete value and size for the symbolik func
        emulator.  This will become the descrete value of the stack
        pointer variable and will be used to calculate memory locations
        which are considered "local".

        Example:
            emu.setStackBase(0xbfbff000, 4096)

        NOTE: architectures without a stack must raise an exception.
        '''
        self.stackbase = stackbase
        self.stacksize = stacksize
        spsym = Const(stackbase, self.__width__)
        self.setStackCounter(spsym)

    def setStackSize(self, stacksize):
        '''
        Set the current stack size ( immediate ).  This is used
        for functions which dynamically modify the stack allocation
        size.
        '''
        self.stacksize = stacksize

    def getStackSize(self):
        '''
        Return the current "size" of the stack in bytes.
        '''
        return self.stacksize

    def isStackMemory(self, symvar):
        '''
        Check if a given symbolik state is a stack/local address.

        Example:
            reg = emu.getSymbolikVariable('regfoo')
            if emu.isStackLocal(reg):
                print('regfoo is in the stack')
        '''
        return self.getStackOffset(symvar) is not None

    def isLocalMemory(self, symvar):
        '''
        Functionally equivelent to isStackMemory except where
        a platform/arch has "function local" memory that is not
        part of the stack.

        NOTE: implementers must override to get "local" vs "stack"
        '''
        return self.isStackMemory(symvar)

    def getStackOffset(self, symvar):
        '''
        Retrieve the offset of the specified symvar from the stack
        base.  If the given symvar is *not* believed to be in the
        stack area, None is returned.

        offsets are negative for "locals"

        Example:
            reg = emu.getSymbolikVariable('regfoo')
            off = emu.getStackOffset(reg)
            if off is not None:
                print('regfoo is stack offset: %d' % off)
        '''
        if self.stackbase is None or self.stacksize is None:
            return None

        va = symvar.solve(emu=self)  # solver cache will help out...
        if self.stackdown and va > self.stackbase:
            return None

        if not self.stackdown and va < self.stackbase:
            return None

        offset = va - self.stackbase

        if self.stackdown and -offset < self.stacksize:
            return offset

        if not self.stackdown and offset < self.stacksize:
            return -offset

    def getLocalOffset(self, symvar):
        '''
        Equivelent to getStackOffset on all platorms where function
        locals are stored in the stack.
        '''
        return self.getStackOffset(symvar)

    def setupFunctionCall(self, fva, args=None):
        '''
        Setup the input context for a sequence of symbolik effects which
        represent a function call.  This will initialize the emulator so
        things like [esp + 8] have an existing state which is "arg0" or even a
        value (based on input args...)
        '''
        # Setup our calling convention based on what the workspace says
        # for this function...
        apictx = self._sym_vw.getFunctionApi(fva)
        if apictx is None:
            raise Exception('No API context for function %x' % fva)

        ccname = apictx[API_CCONV]
        self.cconv = self.getCallingConvention(ccname)
        if self.cconv is None:
            raise Exception('Unknown CallingConvention (%s) for: 0x%.8x' % (ccname, fva))

        if args is None:
            # Initialize arguments by setting variables based on their arg indexes
            argc = len(self._sym_vw.getFunctionArgs(fva))
            args = [Var('arg%d' % i, self.__width__) for i in range(argc)]

        self.cconv.setSymbolikArgs(self, args)

    def getFunctionReturn(self):
        '''
        Once the symbolik code for a function has been run through the
        SymbolikFunctionEmulator the getFunctionReturns method will use the
        calling convention object to return the "return" state for this
        function...
        '''
        return self.cconv.getSymbolikReturn(self)

    def applyFunctionCall(self, funcsym):
        '''
        Apply a function call to the current emulation state (where possible,
        emulating as much as possible to update the state to match reality...)

        We return the set of parsed argument syms so the FofX effect updater
        knows...
        '''
        vw = self._sym_vw

        argv = None
        fret = None
        cconv = None
        symargs = ()

        # If this is a discrete function, use knowledge from the workspace to
        # attempt to properly cleanup the call (and setup a state)
        if funcsym.isDiscrete():

            fva = funcsym.solve(emu=self)

            # since it's discrete, call the solver and resolve fva
            if self._sym_vw.isFunction(fva):

                # If viv knows about this function, lets check if it's a thunk,
                # or if we know about it's calling info...
                fname = vw.getName(fva)
                argv = vw.getFunctionArgs(fva)
                thunk = vw.getFunctionMeta(fva, 'Thunk')

                apictx = self._sym_vw.getFunctionApi(fva)
                if apictx is None:
                    defcall = vw.getMeta("DefaultCall")
                    if defcall is None:
                        raise Exception('No API context for function %x and DefaultCall metadata not set' % fva)
                    # fake out 4 args
                    argv = (('int', None), ('int', None), ('int', None), ('int', None))
                    apictx = ('int', None, defcall, fname, argv)

                ccname = apictx[API_CCONV]

                cconv = self.getCallingConvention(ccname)
                # Either way, if we have a calling convention and a function def
                # lets parse out our arguments so the FofX() effect can have
                # more info
                if cconv is not None:
                    symargs = cconv.getSymbolikArgs(self, argv, update=True)

                # First of all, if the name of the function has a callback
                funccb = self.getFunctionCallback(fname)
                if funccb is not None:
                    fret = funccb(self, fname, symargs)

                # Next highest priority is "thunks" where there is a callback
                elif thunk is not None:
                    funccb = self.getFunctionCallback(thunk)
                    if funccb is not None:
                        fret = funccb(self, thunk, symargs)

        else:

            funcname = str(funcsym)     # Not necessarily the name but...

            # Attempt to use import api definitions...
            apidef = self._sym_vw.getImpApi(funcname)
            if apidef is None:
                defcall = vw.getMeta("DefaultCall")
                if defcall is None:
                    raise Exception('No API context for function %x and DefaultCall metadata not set' % fva)
                # fake out 4 args
                argv = (('int', None), ('int', None), ('int', None), ('int', None))
                apidef = ('int', None, defcall, funcname, argv)

            # ( 'int', None, 'stdcall', 'wininet.FindFirstUrlCacheContainerW', (('int', None), ('void *', 'ptr'), ('int', None), ('int', None)) ),
            rt, rn, cc, fn, argv = apidef
            cconv = self.getCallingConvention(cc)

            # If we managed to get a calling convention *and* argument def...
            if cconv is not None and argv is not None:
                symargs = cconv.getSymbolikArgs(self, argv, update=True)

            # Give the function callback a shot...
            funccb = self.getFunctionCallback(funcname)
            if funccb is not None:
                fret = funccb(self, funcname, symargs)

        # If we have a calling convention here, set the return state
        if cconv is not None:
            if fret is None:
                # TODO: yuck. take ez way out and use width on emu.
                # should get return value def from cc and set width according
                # to width of that?
                fret = Call(funcsym, self.__width__, symargs)
            cconv.setSymbolikReturn(self, fret, argv, precall=True)

        return symargs

    def addCallingConvention(self, name, symcconv):
        '''
        Add a *symbolik* calling convention object to this analysis context.
        The context will be used for operations like argument initialization
        and return value extraction for symbolik emulation.

        (add a calling convention with the name None (object, not string) to
        specify a "default" calling convention)
        '''
        self.cconvs[name] = symcconv

    def getCallingConvention(self, name, default=None):
        '''
        Retrieve a registered *symbolik* calling convention object by name.
        '''
        return self.cconvs.get(name, default)

    def getCallingConventions(self):
        '''
        Retrieve a list of (name, ccobj) tuples for the registered *symbolik*
        calling convention objects in this context.
        '''
        return list(self.cconvs.items())

    def addFunctionCallback(self, funcname, callback):
        '''
        Function hooks may be registered which will get an opportunity to modify
        the emulator state during *runtime* upon the detection of a call to a
        function with the same name (or an import/thunk of the same name...)

        NOTE: a function callback is expected to *completely* handle updating
        the state of the emulator for the function call.
        '''
        self.funchooks[funcname] = callback

    def getFunctionCallback(self, funcname):
        '''
        Retrieve the registered function callback for the given function by name
        (or None if there is no handler registered).
        '''
        return self.funchooks.get(funcname)

    def delFunctionCallback(self, funcname):
        '''
        Remove a registered function callback from the symbolik function
        emulator instance.
        '''
        return self.funchooks.pop(funcname, None)

class SymbolikAnalysisContext:
    '''
    A symbolik analysis context holds arch/platform specific functionality
    which is needed during symboliks analysis...  It is also a context which
    allows over-rides for things like symbolik imports during runtime.
    '''

    def __init__(self, vw, consolve=False):
        self.vw = vw
        self.funccb = {}    # Callbacks
        self.consolve = consolve
        # TODO: is this used?
        self._sym_resolve = False
        self.preeffects = []
        self.preconstraints = []

    def setSymPreEffects(self, effects):
        '''
        Set the current list of "pre effects"
        '''
        self.preeffects = list(effects)

    def addSymPreEffects(self, effects):
        '''
        Append to the current list of "pre effects"
        '''
        self.preeffects.extend(effects)

    def setSymPreConstraints(self, cons):
        '''
        Add a set of "pre constraints" to this symbolik analysis context.
        '''
        self.preconstraints = list(cons)

    def addSymPreConstraints(self, cons):
        '''
        Add a set of "pre constraints" to this symbolik analysis context.
        '''
        self.preconstraints.extend(cons)

    def getSymbolikGraph(self, fva, fgraph=None):
        '''
        Instantiate a standard vivisect function graph (visgraph
        hierarchical graph) and translate all the opcodes in each block
        to un-applied symbolik effects.  The list of effects for each node
        is stored in 'symbolik_effects' list in the node properties.
        '''
        xlate = self.getTranslator()

        if fgraph is None:
            fgraph = viv_graph.buildFunctionGraph(self.vw, fva)

        for nodeva, ninfo in fgraph.getNodes():

            cbva = ninfo.get('cbva')
            cbsize = ninfo.get('cbsize')

            cbmax = cbva + cbsize
            oplist = []
            while cbva < cbmax:
                op = self.vw.parseOpcode(cbva)
                oplist.append(op)
                cbva += len(op)

            for op in oplist:
                xlate.translateOpcode(op)

            efflist = xlate.getEffects()  # we needn't copy
            conlist = xlate.getConstraints()
            xlate.clearEffects()
            # Put constraints into a dictionary lookup by target address
            con_lookup = {}
            for coneff in conlist:
                addrva = coneff.addrsym.solve()
                clist = con_lookup.get(addrva)
                if clist is None:
                    clist = []
                    con_lookup[addrva] = clist
                clist.append(coneff)

            # Save these off in node info for later
            ninfo['opcodes'] = oplist
            ninfo['symbolik_effects'] = efflist

            # Add the constraints to the edges
            for eid, fromid, toid, einfo in fgraph.getRefsFromByNid(nodeva):
                clist = con_lookup.pop(toid, None)
                if clist is None:
                    continue
                einfo['symbolik_constraints'] = clist

            #if len(con_lookup):
                #raise Exception('FIXME: We ditched a constraint! %s' % repr(con_lookup))

        return fgraph

    def _oposet_cons(self, c1, c2):

        c1v1 = c1._v1.solve()
        c1v2 = c1._v2.solve()

        c2v1 = c2._v1.solve()
        c2v2 = c2._v2.solve()

        if c1v1 == c2v1 and c1v2 == c2v2 and c1.revclass == c2.__class__:
            return True

        if c1v1 == c2v2 and c1v2 == c2v1 and c1.__class__ == c2.__class__:
            return True

        return False

    def addSymFuncCallback(self, name, callback):
        '''
        Register a function callback ( mostly for imports ) in the
        analysis context.  Each function callback will be called when
        an import with the specified name is requested.
        '''
        self.funccb[name] = callback

    def getSymbolikPathsTo(self, fva, tova, args=None, maxpath=1000):
        '''
        For each path from the function start to tova, run all symbolik
        effects in an emulator instance and yield emu, effects tuples.
        Differs from getSymbolikPaths() in that it stops at tova rather
        than continuing to a ret or loop path.
        '''
        graph = self.getSymbolikGraph(fva)
        tocb = self.vw.getCodeBlock(tova)
        if tocb is None:
            raise Exception("No codeblock for 'tova': 0x%x" % tova)

        paths = viv_graph.getCodePathsTo(graph, tocb[0])
        spaths = self.getSymbolikPaths(fva, paths=paths, args=args, maxpath=maxpath, graph=graph)
        for emu, effs in spaths:
            # we have symboliks up to the codeblock, but not into it.
            seffs = graph.getNodeProps(tocb[0]).get('symbolik_effects')
            for idx in range(len(seffs)):
                if tova == seffs[idx].va:
                    break
            effs.extend(emu.applyEffects(seffs[:idx+1]))
            yield emu, effs

    def walkSymbolikPaths(self, fva, graph=None, maxpath=1000, loopcnt=0):
        '''
        walkSymbolikPaths is a function-focused symbolik path generator, using the
        walkCodePaths generator foundation.  Symbolik effects are dragged through
        each code block, and constraints are evaluated in-process to determine and
        trim dead code paths.

        Begins first node by applying self.preeffects and self.preconstraints
        '''

        if graph is None:
            graph = self.getSymbolikGraph(fva)

        # our callback routine for code path walking
        def codewalker(ppath, edge, path):
            # first, test for the "entry" case
            if ppath is None and edge is None:
                emu = self.getFuncEmu(fva)
                for fname, funccb in self.funccb.items():
                    emu.addFunctionCallback(fname, funccb)

                patheffs = emu.applyEffects(self.preeffects)
                pathcons = emu.applyEffects(self.preconstraints)

                node = graph.getNode(fva)
                effects = node[1].get('symbolik_effects',())
                patheffs.extend(emu.applyEffects(effects))

                vg_pathcore.setNodeProp(path, 'pathemu', emu)
                vg_pathcore.setNodeProp(path, 'pathcons', pathcons)
                vg_pathcore.setNodeProp(path, 'patheffs', patheffs)
                return True

            # we are now in the "walking" case
            emu = self.getFuncEmu(fva)
            pemu = vg_pathcore.getNodeProp(ppath, 'pathemu')

            emu.setSymSnapshot( pemu.getSymSnapshot() )
            patheffs = list( vg_pathcore.getNodeProp(ppath, 'patheffs') )
            pathcons = list( vg_pathcore.getNodeProp(ppath, 'pathcons') )

            vg_pathcore.setNodeProp(path,'pathemu',emu)
            vg_pathcore.setNodeProp(path,'patheffs',patheffs)
            vg_pathcore.setNodeProp(path,'pathcons',pathcons)

            # pick up the edge constraints
            newcons = graph.getEdgeProps(edge[0]).get('symbolik_constraints', ())
            newcons = emu.applyEffects(newcons)

            [ c.reduce(emu=emu) for c in newcons ]
            for coneff in newcons:
                # bail if the constraint is dorked
                if coneff.cons.isDiscrete():
                    if not coneff.cons._solve():
                        return False
                    continue

                # bail if the constraint is mutex
                # FIXME
                #if any([ oldconeff.isMutualExclusion( coneff ) for oldconeff in pathcons ]):
                    #return False
                # TODO: collective failed constraints 
                #   (previous constraint "var > 3" and this constraint "var == 2")

                patheffs.append( coneff )
                pathcons.append( coneff )

            # We have survived constraints!
            node2 = graph.getNode(edge[2])
            neweffs = node2[1].get('symbolik_effects',())
            neweffs = emu.applyEffects(neweffs)
            patheffs.extend(neweffs)
            return True

        for pathnode in viv_graph.walkCodePaths(graph, codewalker, loopcnt=loopcnt, maxpath=maxpath):
            emu = vg_pathcore.getNodeProp(pathnode, 'pathemu')
            patheffs = vg_pathcore.getNodeProp(pathnode, 'patheffs')
            yield emu, patheffs

    def getSymbolikPaths(self, fva, paths=None, args=None, maxpath=1000, graph=None):
        '''
        For each path through the function, run all symbolik
        effects in an emulator instance and yield
        emu, effects tuples...
        '''
        if graph is None:
            graph = self.getSymbolikGraph(fva)

        if args is None:
            argdef = self.vw.getFunctionArgs(fva)
            args = [Arg(i, width=self.vw.psize) for i in range(len(argdef))]

        if paths is None:
            paths = viv_graph.getCodePaths(graph, maxpath=maxpath)

        pcnt = 0
        for path in paths:
            if pcnt > maxpath:
                break

            pcnt += 1
            skippath = False
            emu = self.getFuncEmu(fva, fargs=args)

            for fname, funccb in self.funccb.items():
                emu.addFunctionCallback(fname, funccb)

            opcodes = []

            patheffects = emu.applyEffects(self.preeffects)

            for nid, eid in path:
                # This is the edge that *got us here* so it has to
                # be processed first!
                if eid is not None:
                    constraints = graph.getEdgeProps(eid).get('symbolik_constraints', ())
                    constraints = emu.applyEffects(constraints)

                    if self.consolve:
                        # If any of the constraints are discrete and false we skip the path
                        [c.reduce() for c in constraints]
                        discs = [c.cons._solve() for c in constraints if c.cons.isDiscrete()]
                        if not all(discs):  # emtpy discs is True...
                            skippath = True
                            break

                        # reduce/remove constraints that were discrete and passed
                        constraints = [c for c in constraints if not c.cons.isDiscrete()]

                    patheffects += constraints

                if skippath:
                    break

                patheffects += emu.applyEffects(graph.getNodeProps(nid).get('symbolik_effects', ()))

                opcodes += graph.getNodeProps(nid).get('opcodes', ())

            if not skippath:
                # Store off some info into emu meta for analysis to use
                emu.setMeta('opcodes', opcodes)
                yield emu, patheffects

    def getSymbolikOutputs(self, fva, args=None):
        '''
        For each path in the specified function, run the path with the given
        args (or populate by arg names from workspace).

        Outputs should include:
            globals written to
            input pointers written to
            functions called (with args)
            output registers modified
        '''
        if args is None:
            argdef = self.vw.getFunctionArgs( fva )
            args = [Arg(i, width=self.vw.psize) for i in range(len(argdef))]

        for emu, effects in self.getSymbolikPaths(fva, args=args):

            outputeffects = []

            self.vw.vprint('='*80)
            for effect in effects:

                # FIXME calls are probably "outputs" too? (especially import calls...)
                if effect.efftype == vsym_effects.EFFTYPE_WRITEMEM:
                    if not emu.isLocalMemory(effect.symaddr):
                        effect.symaddr.reduce()
                        effect.symval.reduce()
                        outputeffects.append(effect)
                        self.vw.vprint('    WRITE: %s' % str(effect))

            ret = emu.getFunctionReturn()
            ret.reduce()
            self.vw.vprint('RETURN VALUE %s' % ret)
            self.vw.vprint('='*80)

            yield ret, outputeffects

    def getTranslator(self):
        '''
        Return a symbolik translator for the workspace specified in the
        constructor.
        '''
        return self.__xlator__(self.vw)

    def getFuncEmu(self, fva, fargs=None, args=()):
        '''
        Instantiates a symbolik emulator and if fva is not None, initializes
        the emu for the specified fva.
        Arguments will be populated either by name (from the workspace's
        function definition) or from the argument list specified in args.
        (arguments will be symbolikified if they are strings/ints with a width
        equal to what is specified in the symbolic function emulator)

        Example:
            femu = symctx.getFuncEmu(fva, ['arg0', 'arg1', 20])
            femu = symctx.getFuncEmu(None)
        '''
        emu = self.__emu__(self.vw, *args)
        emu._sym_resolve = self._sym_resolve
        if fva is not None:
            emu.setupFunctionCall(fva, args=fargs)
        return emu

def getSymbolikAnalysisContext(vw, consolve=False):
    '''
    Return a symbolik analysis context which is appropriate for the given
    VivWorkspace.  Returns None if the given arch/platform does not support
    symboliks based analysis yet...
    '''

    arch = vw.getMeta('Architecture')
    if arch == 'i386':
        import vivisect.symboliks.archs.i386 as vsym_i386
        return vsym_i386.i386SymbolikAnalysisContext(vw, consolve=consolve)

    elif arch == 'amd64':
        import vivisect.symboliks.archs.amd64 as vsym_amd64
        return vsym_amd64.Amd64SymbolikAnalysisContext(vw, consolve=consolve)

    return None
