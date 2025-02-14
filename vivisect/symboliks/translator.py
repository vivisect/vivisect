from vivisect.symboliks.common import *
from vivisect.symboliks.effects import *

class SymbolikTranslator:
    '''
    The SymbolikTranslator is responsible for translating architecture specific
    sequences of Envi Opcode objects into a sequence of purely symbolik effects.
    '''

    def __init__(self, vw):
        self.vw = vw
        self._eff_log = []
        self._con_log = []
        self._op_methods = {}
        for name in dir(self):
            if name.startswith("i_"):
                self._op_methods[name[2:]] = getattr(self, name)
        self._cur_va = None

    def effSetVariable(self, rname, rsym):
        '''
        This may *only* be called with 'natural' register definitions or
        pure symbols...
        (any meta register processing is the responsiblity of the translator
        calling this interface!)
        '''
        self._eff_log.append(SetVariable(self._cur_va, rname, rsym))

    def effReadMemory(self, symaddr, symsize):
        self._eff_log.append(ReadMemory(self._cur_va, symaddr, symsize))
        return Mem(symaddr, symsize)

    def effWriteMemory(self, symaddr, symsize, symobj):
        self._eff_log.append(WriteMemory(self._cur_va, symaddr, symsize, symobj))

    def effFofX(self, funcsym, argsyms=None):
        self._eff_log.append(CallFunction(self._cur_va, funcsym, argsyms))

    def effConstrain(self, addrsym, conssym):
        self._con_log.append(ConstrainPath(self._cur_va, addrsym, conssym))

    def effDebug(self, msg):
        self._eff_log.append(DebugEffect(self._cur_va, msg))

    def translateOpcode(self, op):
        self._cur_va = op.va
        meth = self._op_methods.get(op.mnem, None)
        if meth is None:
            # print('Symboliks: %s: %s Needs: %s' % (hex(op.va), self.__class__.__name__, repr(op)))
            self.effDebug("%s Needs %s" % (self.__class__.__name__, repr(op)))
            return DebugEffect(op.va, "%s Needs %s" % (self.__class__.__name__, repr(op)))

        # instruction translator methods may return branches / constraints
        ret = meth(op)
        if ret is not None:
            for symaddr, symcons in ret:
                self.effConstrain(symaddr, symcons)

        return ret

    def getEffects(self, copy=False):
        '''
        Return the list of symboliks effects which have been logged by
        this translator.
        '''
        if copy:
            return list(self._eff_log)
        return self._eff_log

    def getConstraints(self, copy=False):
        '''
        Return the list of constraints which have been logged by this
        translator.
        '''
        if copy:
            return list(self._con_log)
        return self._con_log

    def clearEffects(self):
        '''
        Clear the translator's list of symbolik effects thus far.
        '''
        self._eff_log = []
        self._con_log = []

    ### support code for instruction implementation (override as necessary)
    def getRegObj(self, regidx):
        '''
        Returns a size/offset-appropriate symbolik object for a given register
        using standard RegisterContext setup.
        '''
        ridx = regidx & 0xffff
        rname = self._reg_ctx.getRegisterName(ridx)
        rbitwidth = self._reg_ctx.getRegisterWidth(ridx)
        val = Var(rname, rbitwidth / 8 )

        # Translate to meta if needed...
        if ridx != regidx:
            # we cannot call _xlateToMetaReg since we'd pass in a symbolik
            # object that would trigger an and operation; the code in envi
            # obviously is NOT symboliks aware (2nd op in & operation is NOT
            # a symbolik); so we do it manually here since we are symbolik
            # aware.
            rreg, lshift, mask = self._reg_ctx.getMetaRegInfo(regidx)
            metawidth = e_bits.u_maxes.index(mask)
            if lshift != 0:
                val = o_rshift(val, Const(lshift, metawidth), metawidth)

            # We must be explicit about the width!
            val = o_and(val, Const(mask, metawidth), metawidth)

        return val

    def setRegObj(self, regidx, obj):
        ridx = regidx & 0xffff
        rname = self._reg_ctx.getRegisterName(ridx)
        rbitwidth = self._reg_ctx.getRegisterWidth(ridx)
        val = Var(rname, rbitwidth / 8 )

        # Translate to native if needed...
        if ridx != regidx:
            # we cannot call _xlateToNativReg since we'd pass in a symbolik
            # object that would trigger an or operation; the code in envi
            # obviously is NOT symboliks aware (2nd op in | operation is NOT
            # a symbolik); so we do it manually here since we are symbolik
            # aware.
            #obj = self._reg_ctx._xlateToNativeReg(regidx, obj)
            basemask = (2**rbitwidth) - 1
            rreg, lshift, mask = self._reg_ctx.getMetaRegInfo(regidx)
            # cut hole in mask
            finalmask = basemask ^ (mask << lshift)
            if lshift != 0:
                obj <<= Const(lshift, rbitwidth / 8)

            obj = obj | (val & Const(finalmask, rbitwidth / 8))

        self.effSetVariable(rname, obj)

    def getOperAddrObj(self, op, idx):
        '''
        Returns a Tuple!

        (symOperAddrObj,  (reg, newupdate))

        The second part of the tuple is because sometimes ARM updates a register *after*
        the address is used.  This second component should be None if nothing needs to 
        be done for updates.

        This allows the caller to decide whether updates need to be done... and apply 
        the effects at the appropriate time in the event stream, but leaving the operand
        responsible for the calculation/etc...
        '''
        oper = op.opers[idx]
        return oper.getOperAddrObj(op, self)

    def getOperObj(self, op, idx):
        '''
        Translate the specified operand to a symbol compatible with
        the symbolic translation system.

        Returns a tuple: (OperObj, AfterEffs)
        where:
            OperObj is the symbolic operand
            AfterEffs is a list of effects which may be applied after this
                    this allows for ARM's Post-Indexed processing, etc...
                    None by default
        '''
        oper = op.opers[idx]
        if oper.isReg():
            return (self.getRegObj(oper.reg), None)

        elif oper.isDeref():
            addrsym, aftereffs = self.getOperAddrObj(op, idx)
            return self.effReadMemory(addrsym, Const(oper.tsize, self._psize))

        elif oper.isImmed():
            ret = oper.getOperValue(op, self)
            return (Const(ret, self._psize), None)

        raise Exception('Unknown operand class: %s' % oper.__class__.__name__)

    def setOperObj(self, op, idx, obj):
        '''
        Set the operand to the new symbolic object.
        '''
        oper = op.opers[idx]
        if oper.isReg():
            self.setRegObj(oper.reg, obj)
            return

        if oper.isDeref():
            addrsym = self.getOperAddrObj(op, idx)
            return self.effWriteMemory(addrsym, Const(oper.tsize, self._psize), obj)

        raise Exception('Umm..... really?')

    def doPush(self, val):
        sp = Var(self.__sp__, self._psize)
        sp -= Const(self._psize, self._psize)

        self.effSetVariable(self.__sp__, sp)
        self.effWriteMemory(sp, Const(self._psize, self._psize), val)

    def doPop(self):
        sp = Var(self.__sp__, self._psize)
        val = self.effReadMemory(sp, Const(self._psize, self._psize))
        self.effSetVariable(self.__sp__, sp+Const(self._psize, self._psize))
        return val

