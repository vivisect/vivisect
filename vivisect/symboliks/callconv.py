from envi.const import *
from vivisect.symboliks.common import *

class SymbolikCallingConvention(object):
    '''
    use as a mixin to an existing envi calling convention.
    '''
    def __init__(self):
        self.argdefemu = self.__argdefemu__()
        # Set up the symbolic constants
        self._width = self.align

        self.pad = Const(self.pad, self._width)
        self.align = Const(self.align, self._width)
        self.delta = Const(self.delta, self._width)

    def _dealloc(self, delta, argc):
        # Special method to allow symbolik cconv to hook...
        return delta + (self.align * Const(argc, self._width))

    def getSymbolikArgs(self, emu, argv, update=False):
        '''
        Used when symbolik emulation discovers a call while doing emulation.
        This allows per-arch-calling-convention argument parsing for updates to
        fofx effects...
        '''
        args = self.getPreCallArgs(self.argdefemu, len(argv))
        if update:
            args = [arg.update(emu) for arg in args]

        return args

    def setSymbolikArgs(self, emu, argv):
        '''
        Setup the emulator for emulation of a call to a function with this
        calling convention and the specified arguments in argv.

        Example:
            cconv.setSymbolikArgs(emu, [sym1, sym2])
        '''
        arglocs = self.getPreCallArgs(self.argdefemu, len(argv))
        for idx, arg in enumerate(argv):
            argloc = arglocs[idx]

            if isinstance(argloc, Var):
                emu.setSymVariable(argloc.name, arg)

            elif isinstance(argloc, Mem):
                # writeSymMemory takes an symaddr NOT a Mem object.  therefore
                # we get the symaddr out of the Mem object and update it's
                # state using the emulator.  then we add to it any alignment
                # specified by the calling convention.  normally we'd use the
                # getCallArgs API instead of getPreCallArgs, but getCallArgs
                # adjusts the sp using getStackCounter which we cannot easily
                # hook in this context. (and don't really want to add
                # additional effects anyway)
                argloc = argloc.kids[0].update(emu=emu)
                emu.writeSymMemory(argloc + self.align, arg)
            else:
                raise Exception('invalid arg location')

    def setSymbolikReturn(self, emu, sym, argv, precall=False):
        '''
        Set the fofx() return state in the calling emulator to reflect that
        state introduced by our callee.

        Example:
            cconv.setSymbolikReturn(emu, Var('foo', self._psize))
        '''
        # TODO: consider renaming func name (see new envi cc stuff)
        # we could get more re-use here if we plumb/snap in methods that map
        # setReturnValue -> setSymVariable, etc.
        atype, aval = self.retval_def
        if atype != CC_REG:
            raise Exception('implement non-register symbolik return vals')

        rname = self.argdefemu.xlator._reg_ctx.getRegisterName(aval)
        emu.setSymVariable(rname, sym)

        spdelta = self.deallocateCallSpace(self.argdefemu, len(argv), precall=precall)

        spidx = self.argdefemu.xlator._reg_ctx._rctx_spindex
        spname = self.argdefemu.xlator._reg_ctx.getRegisterName(spidx)
        sp = emu.getSymVariable(spname)
        emu.setSymVariable(spname, sp + spdelta)

    def getSymbolikReturn(self, emu):
        atype, aval = self.retval_def
        if atype != CC_REG:
            raise Exception('implement non-register symbolik return vals')

        rname = self.argdefemu.xlator._reg_ctx.getRegisterName(aval)
        return emu.getSymVariable(rname)
