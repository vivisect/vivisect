import operator
import itertools

import vivisect.lib.bits as v_bits

counter = itertools.count()

class SymState:
    '''
    SymState object wraps symbolik state tuples to allow
    more "pythonic" syntax when manipulating them.

    NOTE: these should mostly be instantiated by StateBuilder
          classes.
    '''
    def __init__(self, builder, state):
        self.sid = next(counter)
        self.state = state
        self.builder = builder

        state[3]['sid'] = self.sid

    def norm(self, o):
        if type(o) == int:
            return imm(o)
        return o.state

    def bits(self):
        return self.state[-1].get('bits')

    def cast(self, bits):
        '''
        "Inline" cast this SymState to a given bit width.
        '''
        self.state[-1]['bits'] = bits
        return self

    def const(self):
        '''
        Returns True if the given SymState contains no variables.
        '''

    def wrap(self, state):
        return SymState( self.builder, state )

    def value(self):
        return self.builder.cpu.getSymValue( self.state )

    def __repr__(self):
        return repr(self.state)

    def __str__(self):
        return self.__str_recurse(self.state)

    def __str_recurse(self, state):
        if state[0] == 'var': return state[1]
        if state[0] == 'imm':
            imm = state[1]
            if imm < 4096:
                return str(imm)

            return '0x%x' % imm

        if state[0] in ('oper','cond'):
            a = self.__str_recurse(state[2][0])
            b = self.__str_recurse(state[2][1])
            return '(%s %s %s)' % ( a, state[1], b )

        if state[0] == 'mem':
            addr = self.__str_recurse(state[2][0])
            size = self.__str_recurse(state[2][1])
            return '[%s:%s]' % (addr,size)
            
        return 'derp!'

    def __add__(self, o): return self.wrap( add( self.state, self.norm(o) ) )
    def __iadd__(self, o): self.state = add( self.state, self.norm(o) )

    def __sub__(self, o): return self.wrap( sub( self.state, self.norm(o) ) )
    def __isub__(self, o): self.state = sub( self.state, self.norm(o) )

    def __xor__(self, o): return self.wrap( xor( self.state, self.norm(o) ) )
    def __ixor__(self, o): self.state = xor( self.state, self.norm(o) )

    def __or__(self, o): return self.wrap( lor( self.state, self.norm(o) ) )
    def __ior__(self, o): self.state = lor( self.state, self.norm(o) )

    def __and__(self, o): return self.wrap( land( self.state, self.nnorm(o) ) )
    def __iand__(self, o): self.state = land( self.state, self.norm(o) )

    def __lshift__(self, o): return self.wrap( shl( self.state, self.norm(o) ) )
    def __ilshift__(self, o): self.state = shl( self.state, self.norm(o) )

    def __rshift__(self, o): return self.wrap( shr( self.state, self.norm(o) ) )
    def __irshift__(self, o): self.state = shr( self.state, self.norm(o) )

    def __mul__(self, o): return self.wrap( mul( self.state, self.norm(o) ) )
    def __imul__(self, o): self.state = mul( self.state, self.norm(o) )

    def __div__(self, o): return self.wrap( div( self.state, self.norm(o) ) )
    def __idiv__(self, o): self.state = div( self.state, self.norm(o) )

    def __mod__(self, o): return self.wrap( mod( self.state, self.norm(o) ) )
    def __imod__(self, o): self.state = mod( self.state, self.norm(o) )

    def __pow__(self, o): return self.wrap( powr( self.state, self.norm(o) ) )

    def __eq__(self, o): return self.wrap( eq( self.state, self.norm(o) ) ).cast(1)
    def __ne__(self, o): return self.wrap( ne( self.state, self.norm(o) ) ).cast(1)

class UnknownVariable(Exception):pass

class StateBuilder:
    '''
    Helper for constructing symbolik states and effects.

    A StateBuilder may be used to construct symbolik states
    using a terse syntax which is register width aware. Also,
    it may be used to create a sequence of symbolik effects.

    Example:
        b = cpu.getSymBuilder()

        y = (b.eax + 30) * b.edi # returns SymState of ((eax + 30) * edi)
    '''
    def __init__(self, cpu):
        self.cpu = cpu
        self.effects = []

    def __getattr__(self, name):
        if type(name) == str:
            bits = self.cpu.sizeof(name)
            if bits == None:
                raise UnknownVariable(name)

        return SymState(self, var(name,bits=bits) )

    def wrap(self, state):
        return SymState(self, state)

    def var(self, name, **info):
        bits = info.get('bits')
        if bits == None:
            info['bits'] = self.cpu.sizeof(name)
        return self.wrap( var(name,**info) )

    def imm(self, valu, **info):
        return self.wrap( imm(valu,**info) )

    def mem(self, addr, size, **info):
        addr = self.norm(addr)
        size = self.norm(size)
        return self.wrap( mem(addr, size,**info) )

    def norm(self, x):
        xtype = type(x)
        if xtype == int:
            return imm(x)

        if xtype == str:
            bits = self.cpu.sizeof(x)
            if bits != None:
                return var(x,bits=bits)

        return x.state

    def cast(self, x, bits):
        x[-1]['bits'] = bits

    #def pure(self, x):
        # purify various types into a pure state tuple

    #def __getitem__(self, x):
    def __setitem__(self, x, y):
        '''
        Create a "set" effect by assignment.

        Example:
            sym['eax'] = sym.eax + sym.ebx
        '''
        x = self.norm(x)
        y = self.norm(y)

        if x[0] not in ('var','mem'):
            raise Exception('AssignError: %s' % (x,))

        if y[3].get('bits') == None:
            y[3]['bits'] = x[3]['bits']

        self.effects.append( ('set', x, y ) )

class SymbolikCpu:

    def __init__(self):
        # a fake register model for "ephemeral" variables
        #self.ephem = v_regs.Registers()
        self.symcalcs = {
            'var':self._sym_var_value,
            'imm':self._sym_imm_value,
            'oper':self._sym_oper_value,
            'cond':self._sym_cond_value,
        }

        self.symvars = {}
        self.symcache = {}

        self.cpubus.on('cpu:reg:set', self._slot_clear_symcache )
        self.cpubus.on('cpu:mem:write', self._slot_clear_symcache )

    def _slot_clear_symcache(self, event):
        self.symcache.clear()

    def getSymValue(self, state):
        '''
        Calculate the value of a symbolik state for this cpu.

        Example:
            cpu['eax'] = 3
            cpu['ebx'] = 2

            sym = cpu.getSymBuilder()
            s = (sym.eax + sym.ebx) * 30

            x = cpu.getSymValue( s.state ) # x == 150

        NOTE: this API is mostly present for the SymState internals.
              you may most easily access it directly from there.

                x = s.value()

        '''
        sid = state[3].get('sid')
        if sid != None:
            valu = self.symcache.get(sid)
            if valu != None:
                return valu

        valu = self.symcalcs[ state[0] ](state)
        if sid != None:
            self.symcache[sid] = valu

        return valu

    def _sym_imm_value(self, s):
        return s[1]

    def _sym_var_value(self, s):
        name = s[1]
        # NOTE: we assume we're a CPU instance here!
        valu = self._cpu_regs.get(name)
        if valu != None:
            return valu
        return self.ephem.get(name)

    def _sym_kidsvals(self, s):
        return [ self.getSymValue(k) for k in s[2] ]

    def _sym_oper_value(self, s):
        oper = s[1]
        bits = s[3].get('bits')

        if bits == None:
            raise Exception('No Bit Width: %r' % (s,))

        a,b = self._sym_kidsvals(s)
        valu = operimpl[oper](a,b)
        return v_bits.bitmask(valu,bits)

    def _sym_cond_value(self, s):
        cond = s[1]
        bits = s[3].get('bits')

        if bits == None:
            raise Exception('No Bit Width: %r' % (s,))

        a,b = self._sym_kidsvals(s)
        return int( condimpl[cond](a,b) )

def var(r,**info):
    return ('var',r,(),info)

def imm(v,**info):
    return ('imm',v,(),info)

def add(a,b,**info):
    return ('oper','+',[a,b],info)

def sub(a,b,**info):
    return ('oper','-',[a,b],info)

def mul(a,b,**info):
    return ('oper','*',[a,b],info)

def div(a,b,**info):
    return ('oper','/',[a,b],info)

def mod(a,b,**info):
    return ('oper','%',[a,b],info)

def shr(a,b,**info):
    return ('oper','>>',[a,b],info)

def shl(a,b,**info):
    return ('oper','<<',[a,b],info)

def rol(a,b,**info):
    return ('oper','FIXME',[a,b],info)

def ror(a,b,**info):
    return ('oper','FIXME',[a,b],info)

def land(a,b,**info):
    return ('oper','&',[a,b],info)

def lor(a,b,**info):
    return ('oper','|',[a,b],info)

def xor(a,b,**info):
    return ('oper','^',[a,b],info)

def powr(a,b,**info):
    return ('oper','**',[a,b],info)

def mem(addr,size,**info):
    return ('mem','mem',[addr,size],info)

def eq(a,b,**info):
    return ('cond','==',[a,b],info)

def ne(a,b,**info):
    return ('cond','!=',[a,b],info)

def gt(a,b,**info):
    return ('cond','>',[a,b],info)

def lt(a,b,**info):
    return ('cond','<',[a,b],info)

operimpl = {
    '+':operator.add,
    '-':operator.sub,
    '*':operator.mul,
    '/':operator.floordiv,
}

condimpl = {
    '==':operator.eq,
    '!=':operator.ne,
    '>':operator.gt,
    '<':operator.lt,
    '>=':operator.ge,
    '<=':operator.le,
}
