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
