import os

import envi.common as e_common
import vivisect.symboliks.expression as v_s_expr

from vivisect.const import *
from vivisect.symboliks.common import *

class SymbolikEmulator:

    # FIXME possible  _sym_width set automatically from vw?
    # FIXME possible "sym factory" mixin that builds Vars/Consts/Opers etc?
    # ( v = emu.initSymvar('woot')  ( with size default etc.. )

    __width__ = None    # Extenders *must* set this.

    def __init__(self, vw):
        '''
        The SymbolikEmulator is used to keep state on symbolik execution.
        '''
        self._sym_meta = {}
        self._sym_vars = {}
        self._sym_mem = {}
        self._sym_rseed = ''
        self._sym_vw = vw
        self._sym_cconvs = {}    # function emulation can be calling convention aware

        self._sym_expr_parser = v_s_expr.SymbolikExpressionParser(defwidth=vw.psize)

    def getSymSnapshot(self):
        return (dict(self._sym_meta),
                dict(self._sym_vars),
                dict(self._sym_mem),
                self._sym_rseed)

    def setSymSnapshot(self, snap):
        (self._sym_meta,
         self._sym_vars,
         self._sym_mem,
         self._sym_rseed) = snap

    def setMeta(self, name, val):
        '''
        Store metadata in the emulator instance for later.
        '''
        self._sym_meta[name] = val

    def getMeta(self, name, default=None):
        '''
        Retrieve previously stored emulator metadata.
        '''
        return self._sym_meta.get(name, default)

    def parseExpression(self, expr, update=True):
        sym = self._sym_expr_parser.parseExpression(expr)
        if update:
            sym = sym.update(emu=self)
        return sym

    def solveExpression(self, expr, update=True):
        sym = self._sym_expr_parser.parseExpression(expr)
        if update:
            sym = sym.update(emu=self)
        return sym.solve(emu=self)

    def applyEffects(self, effects):
        '''
        Apply the given effects to the emulator.  Return a list of updated
        effects which reflect the state during emulation.
        '''
        return [e.applyEffect(self) for e in effects]

    def applyFunctionCall(self, funcsym):
        '''
        This API allows arch/platform specific emulators to handle (and expand
        out) function calls to modify the emulator state.  A symbolik emulator
        by itself is *not* function aware, so this does nothing, but on
        SymbolikFunctionEmulator instances this will modify the machine state
        to account for the function call...
        '''
        pass

    def addRandomSeed(self):
        '''
        Add a random seed to the name hashing subsystem.  This will
        produce values which may *only* be compared to other values
        generated by this solver.  It also lets you calculate deltas
        by solving for deltas between two symbols in different seed
        inputs to see if they are likely arithmetically related.
        '''
        self._sym_rseed = e_common.hexify(os.urandom(10))

    def getRandomSeed(self):
        return self._sym_rseed

    def readSymMemory(self, symaddr, symsize, vals=None):
        '''
        The readSymMemory API is designed to read from the given
        symbolik address for the specified symbolik length.  If the
        current symbolik emulator has no knowledge of the state of
        the given memory symbol, None is returned.
        '''
        addrval = symaddr.solve(emu=self, vals=vals)

        # check for a previous write first...
        symmem = self._sym_mem.get(addrval)
        if symmem is not None:
            symaddr, symval = symmem
            return symval

        # If we have a workspace, check it for meaningful
        # symbols etc...
        if self._sym_vw is not None:
            # Make a special check for imports...
            loc = self._sym_vw.getLocation(addrval)
            if loc is not None:
                lva, lsize, ltype, linfo = loc
                if ltype == LOC_IMPORT:
                    return Var(linfo, self.__width__)

        return None

    def writeSymMemory(self, symaddr, symval, vals=None):
        # FIXME handle memory offsets etc...
        # FIXME handle write size.. (using isDiscrete?)
        addrval = symaddr.solve(emu=self, vals=vals)
        # sizeval = symsize.solve(slvctx=self)
        self._sym_mem[addrval] = (symaddr, symval)

    def setSymVariable(self, name, symval, width=None):
        if width is None:
            width = self.__width__
        self._sym_vars[name] = symval

    def getSymVariable(self, name, create=True):
        '''
        Get the current state of a named symbolic variable.

        Example:
            v = self.getSymVariable('eax')
        '''
        ret = self._sym_vars.get(name)
        if ret is None and create:
            return Var(name, self.__width__)

        return ret

    def getSymVariables(self):
        '''
        Retrieve a list of (<varname>, <varsym>) tuples.

        Example:
            for vname, vsym in t.getSymVariables():
                print('%s = %s' % (vname, str(vsym)))
        '''
        return list(self._sym_vars.items())
