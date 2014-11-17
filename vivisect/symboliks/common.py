import hashlib
import operator
import functools
import itertools
import traceback

import vstruct
import envi.bits as e_bits

from vivisect.const import *
from vivisect.symboliks.constraints import *

def symcache(f):
    def docache(*args, **kwargs):
        ret = args[0].cache.get( f.__name__ )
        if ret != None: 
            return ret

        ret = f(*args, **kwargs)
        args[0].cache[ f.__name__ ] = ret
        return ret

    functools.update_wrapper(docache, f)
    return docache

def varsolve(name,width,emu=None):
    '''
    A helper routine which unifies the way symboliks
    "solves" ( aka, generates a repeatable entropic
    value ) for a varible by name.
    '''
    if emu != None:
        name += emu.getRandomSeed()

    md5sum = hashlib.md5(name).hexdigest()
    return long( md5sum[:width*2], 16)

def evalSymbolik(reprstr):
    '''
    Take a previously repr'd symboliks object and eval it
    back into objecthood.

    Example:
        x = "o_add(Var('eax', 4), 3)"
        symobj = evalSymbolik(x)
    '''
    return eval(reprstr, globals(), {})

def getSymbolikImport(vw, impname):
    '''
    Resolve (hopefully) and return a symbolik import emulation
    function for the given import by name.
    '''
    modbase = vw.getMeta('SymbolikImportEmulation')
    if modbase == None:
        return None

    nameparts = impname.split('.')

    # FIXME *.malloc!
    # FIXME cache

    mod = vw.loadModule(modbase)
    return vstruct.resolve(mod, nameparts)

class SymbolikBase:
    idgen = itertools.count()

    symtype = None # sub-classes *must* set this
    discrete = False
    commutative = False

    def __init__(self):
        self._sym_id       = self.idgen.next()
        self.kids          = []
        self.parents       = []
        self.cache         = {}
    
    def __add__(self, other):
        return o_add(self, other, self.getWidth())

    def __iadd__(self, other):
        return o_add(self, other, self.getWidth())

    def __sub__(self, other):
        return o_sub(self, other, self.getWidth())

    def __isub__(self, other):
        return o_sub(self, other, self.getWidth())

    def __xor__(self, other):
        return o_xor(self, other, self.getWidth())

    def __ixor__(self, other):
        return o_xor(self, other, self.getWidth())

    def __lshift__(self, count):
        return o_lshift(self, count, self.getWidth())

    def __ilshift__(self, count):
        return o_lshift(self, count, self.getWidth())

    def __rshift__(self, count):
        return o_rshift(self, count, self.getWidth())

    def __irshift__(self, count):
        return o_rshift(self, count, self.getWidth())

    def __or__(self, other):
        return o_or(self, other, self.getWidth())

    def __ior__(self, other):
        return o_or(self, other, self.getWidth())

    def __and__(self, other):
        return o_and(self, other, self.getWidth())

    def __iand__(self, other):
        return o_and(self, other, self.getWidth())

    def __mod__(self, other):
        return o_mod(self, other, self.getWidth())

    def __imod__(self, other):
        return o_mod(self, other, self.getWidth())

    def __mul__(self, other):
        return o_mul(self, other, self.getWidth())

    def __imul__(self, other):
        return o_mul(self, other, self.getWidth())

    def __div__(self, other):
        return o_div(self, other, self.getWidth())

    def __idiv__(self, other):
        return o_div(self, other, self.getWidth())

    def __pow__(self, other):
        return o_pow(self, other, self.getWidth())

    def __hash__(self):
        return hash(self.solve())

    def __eq__(self, other):

        if other == None:
            return False

        if type(other) in (int, long):
            return self.solve() == other

        return self.solve() == other.solve()

    def __ne__(self, other):
        return not self.__eq__(other)

    def clearCache(self):
        '''
        Recursively clear the solve/reduce/etc cache
        for this symbolik object/AST.
        '''
        def cb(path,obj,ctx):
            obj.cache.clear()
        self.walkTree(cb)

    #@symcache - we use the cache, but specially...
    def solve(self, emu=None, vals=None):
        '''
        Produce a reproducable answer based on the current state.

        Additionally, if a "vals" dict is specified, the solve()
        routine will calculate the solution as though any vars
        present in the vals dict had been substituted.

        NOTE: specifying a vals dict will circumvent the solve
              cache under the assumption they could be iterated.
        '''
        # only use the cache if they're not specifying vars
        if vals == None:
            ret = self.cache.get('solve')
            if ret != None:
                return ret

        ret = self._solve(emu=emu,vals=vals)
        if vals == None:
            self.cache['solve'] = ret

        return ret

    def _solve(self, emu=None, vals=None):
        '''
        Produce a reproducable answer based on the current state if provided.
        '''
        raise Exception('%s *must* implement solve(emu=emu)!' % self.__class__.__name__)

    def reduce(self, emu=None, foo=False):
        '''
        Algebraic reduction and operator folding where possible.

        Example:
            symobj = symobj.reduce()
        '''
        def doreduce(path,oldkid,ctx):
            return oldkid._reduce(emu=emu)
        
        sym = self.walkTree(doreduce)
        if foo:
            symstr = str(sym)
            while True:
                sym = sym.walkTree(doreduce)
                s1str = str(sym)
                if s1str == symstr:
                    break
                symstr = s1str

        return sym

    def _reduce(self, emu=None):
        '''
        Algebraic reduction and operator folding where possible.
        '''
        return None

    def update(self, emu):
        '''
        Return an updated representation for this symbolik state based on the given
        emulator.
        '''
        raise Exception('%s *must* implement update(emu)!' % self.__class__.__name__)

    def setSymKid(self, idx, kid):
        '''
        '''
        if idx > len(self.kids)-1:
            self.kids.append(kid)
            self.kids[idx].parents.append(self) 
        else:
            # kid already exists
            oldkid = self.kids[idx]
            if oldkid._sym_id == kid._sym_id:
                return

            # invalidate the cache
            todo = list(oldkid.parents)
            todo.append(self)

            done = set()
            while todo:
                parent = todo.pop()
                if parent._sym_id in done:
                    continue

                # track the objects whose cache has been cleared    
                done.add(parent._sym_id)
                parent.cache.clear() 
                # grow our todo list
                todo.extend(list(parent.parents))

            # remove ourselves as the parent
            if oldkid.parents:
                #oldkid.parents.remove(self)
                for i,obj in enumerate(oldkid.parents):
                    if obj._sym_id == self._sym_id:
                        oldkid.parents.pop(i)
                        break
            # add new kid
            self.kids[idx] = kid
            self.kids[idx].parents.append(self) 


    @symcache
    def isDiscrete(self, emu=None):
        '''
        Returns True if the given symbolik (from here down) does *not* depend on
        any variables or runtime values.
        '''
        if not self.kids:
            return self.discrete

        if all([ k.isDiscrete(emu=emu) for k in self.kids]):
            return True

        return False

    def walkTree(self, cb, ctx=None):
        '''
        Walk the tree of symbolik objects. (depth first)

        The callback is expected to have the following
        convention:
            newobj = callback(path,oldkid,ctx)

        NOTE: because the callback may completely replace
              the symbolik object, walkTree() returns the
              (potentially new) "self" and should be used
              similarly to "reduce()":

              symobj = symbobj.walkTree(callback)

        '''
        return self._walkTreeImpl([],cb,ctx=ctx)

    def _walkTreeImpl(self, path, cb, ctx=None):
        # the internal version of walk tree ( which is also the recursive one )
        path.append( self )
        # when kids[i] is a list of tupes then we need to call into it!
        for i in range(len(self.kids)):
            oldkid = self.kids[i]
            newkid = oldkid._walkTreeImpl(path,cb,ctx=ctx)
            if newkid._sym_id != oldkid._sym_id:
                self.setSymKid(i, newkid)

        newkid = cb(path,self,ctx)
        if newkid == None:
            newkid = self

        # lifo like a stack ( and like a baws )
        path.pop()
        return newkid

    def render(self, canvas, vw):
        canvas.addText( str(self) )

class cnot(SymbolikBase):
    '''
    Mostly used to wrap the reverse of a contraint which is based on
    a variable.
    '''
    symtype     = SYMT_SEXT

    def __init__(self, v1):
        SymbolikBase.__init__(self)
        self.setSymKid(0, v1)
    @symcache
    def __repr__(self):
        return 'cnot( %s )' % (repr(self.kids[0]))

    @symcache
    def __str__(self):
        return 'cnot(%s)' % str(self.kids[0])

    def _solve(self, emu=None, vals=None):
        return int( not bool( self.kids[0].solve(emu=emu, vals=vals)) )

    def update(self, emu):
        # FIXME dependancy loop...
        from vivisect.symboliks.constraints import Constraint
        v1 = self.kids[0].update(emu=emu)
        if isinstance(v1, Constraint):
            return v1.reverse()
        return cnot(v1)

    def _reduce(self, emu=None):
        # FIXME dependancy loop...
        from vivisect.symboliks.constraints import Constraint
        #self.kids[0] = self.kids[0].reduce(emu=emu)

        if isinstance( self.kids[0], Constraint):
            return self.kids[0].reverse()

        if isinstance( self.kids[0], cnot):
            return self.kids[0].kids[0]

    def getWidth(self):
        return self.kids[0].getWidth()

class Call(SymbolikBase):
    '''
    This represents the return value of an instance of a call to
    a function.
    '''
    symtype = SYMT_CALL

    def __init__(self, funcsym, width, argsyms=[]):
        SymbolikBase.__init__(self)
        self.width = width
        self.setSymKid(0, funcsym)
        for i in range(len(argsyms)):
            self.setSymKid(i+1, argsyms[i])

    def getWidth(self):
        return self.width

    @symcache
    def __str__(self):
        args = ','.join( [ str(sym) for sym in self.kids[1:]] )
        return '%s(%s)' % (self.kids[0], args)

    @symcache
    def __repr__(self):
        return 'Call(%s,%s, argsyms=%s)' % (repr(self.kids[0]), repr(self.width), repr(self.kids[1:]))

    def render(self, canvas, vw):

        self.kids[0].render(canvas, vw)
        canvas.addText('(')

        symobjs = self.kids[1:]
        symmax = len(symobjs) - 1

        for i,symobj in enumerate(symobjs):
            symobj.render(canvas,vw)
            if i < symmax:
                canvas.addText(',')

        canvas.addText(')')

    def _solve(self, emu=None, vals=None):
        ret = 0
        for s in [ k.solve(emu=emu,vals=vals) for k in self.kids ]:
            ret ^= s
        return ret

    def update(self, emu):
        symfunc  = self.kids[0].update(emu)
        symargs  = [ x.update(emu) for x in self.kids[1:] ]
        return Call(symfunc, self.width, symargs) 

    @symcache
    def isDiscrete(self, emu=None):
        # symbolik calls are *never* discrete
        return False

class Mem(SymbolikBase):
    '''
    This is effectivly a cop-out for symbolic states read in from
    memory which has not been initialized yet.
    '''
    symtype = SYMT_MEM

    def __init__(self, symaddr, symsize):
        SymbolikBase.__init__(self)
        self.setSymKid(0, symaddr)
        self.setSymKid(1, symsize)

    @symcache
    def __repr__(self):
        return 'Mem(%s, %s)' % (repr(self.kids[0]), repr(self.kids[1]))

    @symcache
    def __str__(self):
        return 'mem[%s:%s]' % (str(self.kids[0]), str(self.kids[1]))

    def update(self, emu):
        symaddr = self.kids[0].update(emu)
        symsize = self.kids[1].update(emu)

        # If the emulator (or is viv) knows about us, update to his...
        ret = emu.readSymMemory(symaddr, symsize)
        if ret != None:
            return ret

        return Mem(symaddr, symsize)

    @symcache
    def isDiscrete(self, emu=None):
        # non-updated memory locations are *never* discrete
        return False

    def _solve(self, emu=None, vals=None):
        addrval = self.kids[0].solve(emu=emu, vals=vals)
        sizeval = self.kids[1].solve(emu=emu, vals=vals)
        # FIXME higher entropy!
        return hash(str(addrval)) & 0xffffffff

    def getWidth(self):
        # FIXME should we do something about that?
        return self.kids[1].solve()

class Var(SymbolikBase):

    symtype = SYMT_VAR

    def __init__(self, name, width):
        SymbolikBase.__init__(self)
        self.name  = name
        self.width = width

    def render(self, canvas, vw):

        strval = str(self)
        value = self.solve()

        if vw.isValidPointer( value ):
            canvas.addVaText(strval, va=value)
            return

        sym = vw.getSymByName( strval )
        if sym != None:
            value = long(sym)
            canvas.addVaText(strval, va=value)
            return

        #canvas.addNameText(strval, name=strval, typename="registers")
        canvas.addNameText(strval)

    @symcache
    def __repr__(self):
        return 'Var("%s", width=%d)' % (self.name, self.width)

    @symcache
    def __str__(self):
        return self.name

    def _solve(self, emu=None, vals=None):
        if vals != None:
            ret = vals.get(self.name)
            if ret != None:
                return ret

        return varsolve(self.name, self.width, emu=emu)

    def update(self, emu):
        ret = emu.getSymVariable(self.name, create=False)
        if ret != None:
            return ret
        return Var(self.name, width=self.width)

    def getWidth(self):
        return self.width

class LookupVar (Var):
    '''
    A 'LookupVar' is a special kind of variable used to track hardware-level 
    information, such as the VMREAD data.  Because VMREAD instructions require
    a register value to determine what is being read, and this register info 
    isn't available until symbolik emulation, LookupVar allows the important
    data to be tracked between simple effects and applied effects.
    '''

    symtype = SYMT_LOOKUP

    def __init__(self, prefix, offset, lookupdict, width):
        Var.__init__(self, prefix, width)
        self.offset = offset
        self.lookupdict = lookupdict

    @symcache
    def __repr__(self):
        return 'LookupVar(%s,%s,%s, width=%s)' % (repr(self.name), repr(self.offset), repr(self.lookupdict), repr(self.width))

    @symcache
    def __str__(self):
        if self._strval:
            return self._strval

        if not self.offset.isDiscrete():
            return '%s::%s' % (self.name, self.offset)

        self._strval = '%s_%s' % (self.name, self.lookupdict.get(self.offset.solve()))
        return self._strval

    def _solve(self, emu=None):
        name = 'LookupVar:%s:%s' % (self.name, self.offset)

        if emu != None:
            name += emu.getRandomSeed()

        return long(hashlib.md5(name).hexdigest()[:self.width*2], 16)

    def update(self, emu):
        offset = self.offset.update(emu=emu)
        if offset.isDiscrete():
            return Var('%s_%s' % (self.name, self.lookupdict.get(offset.solve())), self.width)

        return LookupVar(self.name, offset, lookupdict=self.lookupdict, width=self.width)

    def _reduce(self, emu=None):
        self.offset._reduce(emu=emu) 
        return self

    def getWidth(self):
        return self.width

    def isDiscrete(self, emu=None):
        return False

class Arg(SymbolikBase):
    '''
    An "Arg" is a special kind of variable used to facilitate cross
    function boundary solving.
    '''
    symtype = SYMT_ARG

    def __init__(self, idx, width):
        SymbolikBase.__init__(self)
        self.idx = idx
        self.width = width

    @symcache
    def __repr__(self):
        return 'Arg(%d,width=%d)' % (self.idx, self.width)

    @symcache
    def __str__(self):
        return 'arg%d' % self.idx

    def render(self, canvas, vw):
        canvas.addNameText( str(self) )

    def _solve(self, emu=None, vals=None):
        name = 'arg%d' % self.idx

        if vals != None:
            ret = vals.get(name)
            if ret != None:
                return ret

        return varsolve(name, self.width, emu=emu)

    def update(self, emu):
        return Arg(self.idx, width=self.width)

    def getWidth(self):
        return self.width

class Const(SymbolikBase):

    symtype     = SYMT_CONST
    discrete    = True

    def __init__(self, value, width, ptrname=None, constname=None):
        '''
        A symbolik constant.  Optionally specify ptrname or constname
        ( or set them during walkTree() ) to allow the const to render
        itself with humon readable names.
        '''
        SymbolikBase.__init__(self)
        self.width = width
        self.value = value % (2**(self.width*8))

        self.ptrname = ptrname
        self.constname = constname

    def render(self, canvas, vw):

        # Do we have a "ptrname"?
        if self.ptrname:
            canvas.addText('&')
            canvas.addVaText(self.ptrname, va=self.value)
            return

        # Are we a "named" constant?
        if self.constname:
            canvas.addNameText(self.constname, name=self.constname)
            return

        # if our const is a named pointer...
        if vw.isValidPointer( self.value ):
            name = str(vw.getSymByAddr( self.value ))
            canvas.addText('&')
            canvas.addVaText(name, va=self.value)
            return
        canvas.addNameText( str(self) )

    def _solve(self, emu=None, vals=None):
        return self.value

    @symcache
    def __repr__(self):
        return 'Const(0x%.8x,%d)' % (self.value,self.width)

    @symcache
    def __str__(self):
        if self.value > 4096:
            return '0x%.8x' % self.value
        return str(self.value)

    def getWidth(self):
        return self.width

    def update(self, emu):
        # const's are immutable... don't copy...
        return self
        #return Const(self.value, self.width, ptrname=self.ptrname, constname=self.constname)

    @symcache
    def isDiscrete(self, emu=None):
        return True

class Operator(SymbolikBase):
    '''
    A class representing an algebraic operator being carried out on two
    symboliks.
    '''
    oper = None
    operstr = None
    def __init__(self, v1, v2, width):
        SymbolikBase.__init__(self)
        self.width = width
        self.mod = e_bits.u_maxes[width] + 1
        self.setSymKid(0, v1)
        self.setSymKid(1, v2)

    def getWidth(self):
        return self.width

    def _reduce(self, emu=None):

        v1 = self.kids[0]
        v2 = self.kids[1]

        v1d = v1.isDiscrete()
        v2d = v2.isDiscrete()

        if v1d and v2d:
            return Const( self.solve(emu=emu), self.getWidth() )

        v1val = self.kids[0].solve(emu=emu)
        v2val = self.kids[1].solve(emu=emu)

        # FIXME - dependancy loop.  does this effect perf?
        from vivisect.symboliks.reducers import reduceoper
        ret = reduceoper(self,emu=emu)
        if ret != None:
            return ret
        return self._op_reduce(v1, v1val, v2, v2val, emu)

    def _op_reduce(self, v1, v1val, v2, v2val, emu):
        # Override this to do per operator special reduction
        return None

    def update(self, emu):
        v1 = self.kids[0].update(emu)
        v2 = self.kids[1].update(emu)
        return self.__class__(v1, v2, self.width)

    def _solve(self, emu=None, vals=None):
        v1 = self.kids[0].solve(emu=emu, vals=vals)
        v2 = self.kids[1].solve(emu=emu, vals=vals)
    
        if self.operstr == '/' or self.operstr == '%':
            # catch divide by zero
            if v2 == 0: 
                return Var("NaN", width=self.width).solve(emu=emu)
        if self.mod == 0:
            return Var("NaN", width=self.width).solve(emu=emu)
        try:
            return self.oper(v1, v2) % self.mod
        except OverflowError:
            return Var("NaN", width=self.width).solve(emu=emu)

    @symcache
    def __repr__(self):
        name = self.__class__.__name__
        v1 = repr(self.kids[0])
        v2 = repr(self.kids[1])
        return '%s(%s,%s,%d)' % (name,v1,v2,self.getWidth())

    @symcache
    def __str__(self):
        if self.operstr == None:
            raise Exception('Operators *must* set operstr')
        x,y = self.kids
        return '(%s %s %s)' % (str(x), self.operstr, str(y))

    def render(self, canvas, vw):
        canvas.addText('(')
        self.kids[0].render(canvas,vw)
        canvas.addText(' ')
        canvas.addNameText(self.operstr)
        canvas.addText(' ')
        self.kids[1].render(canvas,vw)
        canvas.addText(')')

class o_add(Operator):
    oper        = operator.add
    operstr     = '+'
    symtype     = SYMT_OPER_ADD
    commutative = True

class o_sub(Operator):
    oper        = operator.sub
    operstr     = '-'
    symtype     = SYMT_OPER_SUB

class o_xor(Operator):
    oper        = operator.xor
    operstr     = '^'
    symtype     = SYMT_OPER_XOR
    commutative = True

class o_and(Operator):
    oper        = operator.and_
    operstr     = '&'
    symtype     = SYMT_OPER_AND
    commutative = True

class o_or(Operator):
    oper        = operator.or_
    operstr     = '|'
    symtype     = SYMT_OPER_OR
    commutative = True

class o_mul(Operator):
    oper        = operator.mul
    operstr     = '*'
    symtype     = SYMT_OPER_MUL
    commutative = True

class o_div(Operator):
    oper        = operator.div # should this be floordiv?
    operstr     = '/'
    symtype     = SYMT_OPER_DIV

class o_mod(Operator):
    oper        = operator.mod
    operstr     = '%'
    symtype     = SYMT_OPER_MOD

class o_lshift(Operator):
    oper        = operator.lshift
    operstr     = '<<'
    symtype     = SYMT_OPER_LSHIFT

class o_rshift(Operator):
    oper        = operator.rshift
    operstr     = '>>'
    symtype     = SYMT_OPER_RSHIFT

class o_pow(Operator):
    oper        = operator.pow
    operstr     = '**'
    symtype     = SYMT_OPER_POW

# introduce the concept of a modifier?  or keep this an operator?
class o_sextend(SymbolikBase):
    symtype     = SYMT_SEXT

    def __init__(self, v1, tgtsz):
        SymbolikBase.__init__(self)
        self.setSymKid(0, v1)
        self.setSymKid(1, tgtsz)

    @symcache
    def __repr__(self):
        symobj,tgtsz = self.kids
        return '%s(%s,%s)' % (self.__class__.__name__, repr(symobj), repr(tgtsz))

    @symcache
    def __str__(self):
        symobj,tgtsz = self.kids
        return 'signextend(%s, %s)' % (str(symobj), str(tgtsz))

    def getWidth(self):
        return self.kids[1].solve()

    def _solve(self, emu=None, vals=None):
        symval = self.kids[0].solve(emu=emu,vals=vals)
        cursz  = self.kids[0].getWidth()
        tgtsz  = self.kids[1].solve(emu=emu,vals=vals)
        return e_bits.sign_extend(symval, cursz, tgtsz)

    def update(self, emu):
        kids = [ k.update(emu) for k in self.kids ]
        return self.__class__(*kids)
