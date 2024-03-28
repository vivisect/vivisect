import hashlib
import operator
import functools
import itertools

import vstruct
import envi.bits as e_bits

from vivisect.const import *

def symcache(f):
    def docache(*args, **kwargs):
        ret = args[0].cache.get(f.__name__)
        if ret is not None:
            return ret

        ret = f(*args, **kwargs)
        args[0].cache[f.__name__] = ret
        return ret

    functools.update_wrapper(docache, f)
    return docache

def varsolve(name, width, emu=None):
    '''
    A helper routine which unifies the way symboliks
    "solves" (aka, generates a repeatable entropic
    value) for a varible by name.
    '''
    if emu is not None:
        name += emu.getRandomSeed()

    md5sum = hashlib.md5(name.encode('utf-8')).hexdigest()
    return int(md5sum[:width*2], 16)

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
    if modbase is None:
        return None

    nameparts = impname.split('.')

    # FIXME *.malloc!
    # FIXME cache

    mod = vw.loadModule(modbase)
    return vstruct.resolve(mod, nameparts)

def cb_astNodeCount(path,obj,ctx):
    ctx['count'] += 1
    if len(path) > ctx['depth']:
        ctx['depth'] = len(path)

class SymbolikBase:
    idgen = itertools.count()

    symtype = None  # sub-classes *must* set this
    discrete = False
    commutative = False

    def __init__(self):
        self._sym_id = next(self.idgen)
        self.kids = []
        self.parents = []
        self.cache = {}

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

    def __truediv__(self, other):
        return o_div(self, other, self.getWidth())

    def __idiv__(self, other):
        return o_div(self, other, self.getWidth())

    def __floordiv__(self, other):
        return o_div(self, other, self.getWidth())

    def __pow__(self, other):
        return o_pow(self, other, self.getWidth())

    def __hash__(self):
        return hash(self.solve())

    def __eq__(self, other):

        if other is None:
            return False

        if isinstance(other, int):
            return self.solve() == other

        return self.solve() == other.solve()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __le__(self, other):
        if other is None:
            return False

        if isinstance(other, int):
            return self.solve() <= other

        return self.solve() <= other.solve()

    def __lt__(self, other):
        if other is None:
            return False

        if isinstance(other, int):
            return self.solve() < other

        return self.solve() < other.solve()

    def __ge__(self, other):
        if other is None:
            return False

        if isinstance(other, int):
            return self.solve() >= other

        return self.solve() >= other.solve()

    def __gt__(self, other):
        if other is None:
            return False

        if isinstance(other, int):
            return self.solve() > other

        return self.solve() > other.solve()

    def clearCache(self):
        '''
        Recursively clear the solve/reduce/etc cache
        for this symbolik object/AST.
        '''
        def cb(path, obj, ctx):
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
        if vals is None:
            ret = self.cache.get('solve')
            if ret is not None:
                return ret

        ret = self._solve(emu=emu, vals=vals)
        if vals is None:
            self.cache['solve'] = ret

        return ret

    def _solve(self, emu=None, vals=None):
        '''
        Produce a reproducable answer based on the current state if provided.
        '''
        raise Exception('%s *must* implement solve(emu=emu)!' % self.__class__.__name__)

    def reduce(self, emu=None, foo=True):
        '''
        Algebraic reduction and operator folding where possible.

        Example:
            symobj = symobj.reduce()
        '''
        def doreduce(path, oldkid, ctx):
            return oldkid._reduce(emu=emu)

        sym = self.walkTree(doreduce, once=True)
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
        Creates or sets a child for the current symbolik object

        The sticky bit here is when the child already exists and we're setting it to a new value
        (as in the case of things like symbolik reduction). In that case we have to invalidate
        the symcaches of every parent node up all of the ASTs that the child exists in. However,
        that can get exceedingly repetative and expensive, especially in the reduction cases
        where we don't need to constantly clear the ASTs, since during the traversal they'll be
        cleared once and then only really need to be cleared if any of the cached methods
        (isDiscrete, __repr__, or __str__) are called again (which doesn't happen during
        reduction).

        We can take advantage of this behavior when clearing the parent caches during setSymKid.
        If the cache of a parent node is cleared, we don't need to traverse up the tree to clear
        the caches of the rest of the parents, since those should already be cleared. During
        reduction this should generally hold true. During other types of walks, calling any of the
        cache methods recursively populates the cache downwards, and replacing a child would still
        force setSymKid to traverse up the parent chain to clear all the parent caches, so custom
        walks, such as in vivisect.symboliks.archind.wipeAstArch, will still work as expected.

        Usage of setSymKid outside of walkTree should see little impact, though it is best to have
        clear caches depending on your use case. Both the new child and the new parent should have
        clear caches or populated caches, a mix is not recommended.

        On the downside, this does impose the constraints that if you mean to do any out of API
        ASTs manipulations such as merging trees or node replacement without doing a walkTree,
        you had best make sure the caches are clear or that there are no gaps in the caches
        of the consecutive levels of the AST. This can easily be achieved using the clearCache()
        method on the root node of the AST (or ASTs in the case of multiple), like so:

        for obj in root_symobjs:
            obj.clearCache()
        '''
        if idx > len(self.kids) - 1:
            self.kids.append(kid)
            self.kids[idx].parents.append(self)
        else:
            # kid already exists
            oldkid = self.kids[idx]
            if oldkid._sym_id == kid._sym_id:
                return

            # invalidate the cache, but be careful not to repopulate it
            todo = {p._sym_id: p for p in oldkid.parents}
            done = set()
            while todo:
                pid, parent = todo.popitem()
                if pid in done:
                    continue

                # track the objects whose cache has been cleared
                done.add(pid)
                parent.cache.clear()
                # grow our todo list
                for prnt in parent.parents:
                    if prnt.cache:
                        todo[prnt._sym_id] = prnt
                    else:
                        done.add(prnt._sym_id)

            # remove ourselves as the parent
            if oldkid.parents:
                for i, obj in enumerate(oldkid.parents):
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

        if all([k.isDiscrete(emu=emu) for k in self.kids]):
            return True

        return False

    def walkTree(self, cb, ctx=None, once=True):
        '''
        this version basically mirrors the original walkTree/_walkTreeImpl combination
        not sure about the stack usage.
        probably want to track index separately so we can just hand stack in as the path (and have it be correct)
        '''
        path = []
        idxs = []
        done = set()

        cur = self
        idx = 0

        while True:
            # follow kids if there are any left...
            if idx < len(cur.kids):
                kid = cur.kids[idx]
                if once and kid._sym_id in done:
                    idx += 1
                    continue

                # store current info for this level
                path.append(cur)
                idxs.append(idx)

                # let's get into the minds of our kids...
                cur = kid
                idx = 0
                continue

            # do self
            path.append(cur)    # old walkTree expects cur to be on the top of the stack
            newb = cb(path, cur, ctx)
            path.pop()          # clean up, since our algorithm doesn't expect cur on the top...

            if not path:
                if newb:
                    return newb
                return cur

            done.add(cur._sym_id)

            # pop back up a level
            cur = path.pop()
            idx = idxs.pop()

            # tie newb in
            if newb is not None:
                cur.setSymKid(idx, newb)

            idx += 1

    def render(self, canvas, vw):
        canvas.addText(str(self))

    def countAstNodes(ast):
        ctx = {'count': 0, 'depth': 0}

        ast.walkTree(cb_astNodeCount, ctx)
        return ctx['count'], ctx['depth']

class cnot(SymbolikBase):
    '''
    Mostly used to wrap the reverse of a contraint which is based on
    a variable.
    '''
    symtype = SYMT_NOT

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
        return int(not bool(self.kids[0].solve(emu=emu, vals=vals)))

    def update(self, emu):
        v1 = self.kids[0].update(emu=emu)
        if v1.symtype & SYMT_CON:
            return v1.reverse()
        return cnot(v1)

    def _reduce(self, emu=None):
        '''
        # FIXME dependancy loop...
        if self._reduced:
            return self

        self._reduced = True
        '''
        #self.kids[0] = self.kids[0].reduce(emu=emu)

        kidzero = self.kids[0]
        if kidzero.symtype == SYMT_CON:
            return kidzero.reverse()

        if kidzero.symtype == SYMT_NOT:
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
        args = ','.join([str(sym) for sym in self.kids[1:]])
        return '%s(%s)' % (self.kids[0], args)

    @symcache
    def __repr__(self):
        return 'Call(%s,%s, argsyms=%s)' % (repr(self.kids[0]), repr(self.width), repr(self.kids[1:]))

    def render(self, canvas, vw):

        self.kids[0].render(canvas, vw)
        canvas.addText('(')

        symobjs = self.kids[1:]
        symmax = len(symobjs) - 1

        for i, symobj in enumerate(symobjs):
            symobj.render(canvas, vw)
            if i < symmax:
                canvas.addText(',')

        canvas.addText(')')

    def _reduce(self, emu=None):
        args = []
        for symkid in self.kids[1:]:
            kid = symkid._reduce(emu=emu)
            kid = kid if kid else symkid
            args.append(kid)
        func = self.kids[0]._reduce(emu=emu)
        func = func if func else self.kids[0]
        return Call(func, self.width, args)

    def _solve(self, emu=None, vals=None):
        ret = 0
        for s in [k.solve(emu=emu, vals=vals) for k in self.kids]:
            ret ^= s
        return ret

    def update(self, emu):
        symfunc = self.kids[0].update(emu)
        symargs = [x.update(emu) for x in self.kids[1:]]
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
        if ret is not None:
            return ret

        return Mem(symaddr, symsize)

    @symcache
    def isDiscrete(self, emu=None):
        # non-updated memory locations are *never* discrete
        return False

    def _solve(self, emu=None, vals=None):
        if emu is not None:
            val = emu.readSymMemory(self.kids[0], self.kids[1], vals=vals)
            if val and val.isDiscrete():
                return val.solve()

        addrval = self.kids[0].solve(emu=emu, vals=vals)
        sizeval = self.kids[1].solve(emu=emu, vals=vals)

        return varsolve(f'[{addrval}:{sizeval}]', 32)

    def getWidth(self):
        # FIXME should we do something about that?
        return self.kids[1].solve()

    def _reduce(self, emu):
        addr = self.kids[0]._reduce(emu=emu)
        addr = addr if addr else self.kids[0]
        size = self.kids[1]._reduce(emu=emu)
        size = size if size else self.kids[1]
        return Mem(addr, size)

class Var(SymbolikBase):

    symtype = SYMT_VAR

    def __init__(self, name, width):
        SymbolikBase.__init__(self)
        self.name = name
        self.width = width

    def render(self, canvas, vw):

        strval = str(self)
        value = self.solve()

        if vw.isValidPointer(value):
            canvas.addVaText(strval, va=value)
            return

        sym = vw.getSymByName(strval)
        if sym is not None:
            value = int(sym)
            canvas.addVaText(strval, va=value)
            return

        # canvas.addNameText(strval, name=strval, typename="registers")
        canvas.addNameText(strval)

    @symcache
    def __repr__(self):
        return 'Var("%s", width=%d)' % (self.name, self.width)

    @symcache
    def __str__(self):
        return self.name

    def _solve(self, emu=None, vals=None):
        if vals is not None:
            ret = vals.get(self.name)
            if ret is not None:
                return ret

        return varsolve(self.name, self.width, emu=emu)

    def update(self, emu):
        ret = emu.getSymVariable(self.name, create=False)
        if ret is not None:
            return ret
        return Var(self.name, width=self.width)

    def getWidth(self):
        return self.width

class LookupVar(Var):
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

        if emu is not None:
            name += emu.getRandomSeed()

        return int(hashlib.md5(name).hexdigest()[:self.width*2], 16)

    def update(self, emu):
        offset = self.offset.update(emu=emu)
        if offset.isDiscrete():
            return Var('%s_%s' % (self.name, self.lookupdict.get(offset.solve())), self.width)

        return LookupVar(self.name, offset, lookupdict=self.lookupdict, width=self.width)

    def _reduce(self, emu=None):
        offset = self.offset._reduce(emu=emu)
        offset = offset if offset else self.offset

        return LookupVar(self.name, offset, self.lookupdict, self.width)

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
        canvas.addNameText(str(self))

    def _solve(self, emu=None, vals=None):
        name = 'arg%d' % self.idx

        if vals is not None:
            ret = vals.get(name)
            if ret is not None:
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
        if vw.isValidPointer(self.value):
            name = str(vw.getSymByAddr(self.value))
            canvas.addText('&')
            canvas.addVaText(name, va=self.value)
            return
        canvas.addNameText(str(self))

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
            return Const(self.solve(emu=emu), self.getWidth())

        v1val = self.kids[0].solve(emu=emu)
        v2val = self.kids[1].solve(emu=emu)

        # FIXME - dependancy loop.  does this effect perf?
        from vivisect.symboliks.reducers import reduceoper
        ret = reduceoper(self, emu=emu)
        if ret is not None:
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
        return '%s(%s,%s,%d)' % (name, v1, v2, self.getWidth())

    @symcache
    def __str__(self):
        if self.operstr is None:
            raise Exception('Operators *must* set operstr')
        x, y = self.kids
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
    oper        = operator.floordiv
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
    symtype = SYMT_SEXT

    def __init__(self, v1, tgtsz):
        SymbolikBase.__init__(self)
        self.setSymKid(0, v1)
        self.setSymKid(1, tgtsz)

    @symcache
    def __repr__(self):
        symobj, tgtsz = self.kids
        return '%s(%s,%s)' % (self.__class__.__name__, repr(symobj), repr(tgtsz))

    @symcache
    def __str__(self):
        symobj, tgtsz = self.kids
        return 'signextend(%s, %s)' % (str(symobj), str(tgtsz))

    def getWidth(self):
        return self.kids[1].solve()

    def _solve(self, emu=None, vals=None):
        symval = self.kids[0].solve(emu=emu, vals=vals)
        cursz = self.kids[0].getWidth()
        tgtsz = self.kids[1].solve(emu=emu, vals=vals)
        return e_bits.sign_extend(symval, cursz, tgtsz)

    def update(self, emu):
        kids = [k.update(emu) for k in self.kids]
        return self.__class__(*kids)

class Constraint(Operator):
    '''
    A class to represent algebraic constraints that are tracked by a given
    polynomial.
    '''
    revclass = None
    operstr = None

    def __init__(self, v1, v2, width=None):
        if width is None:
            width = v1.getWidth()
        Operator.__init__(self, v1, v2, width)

    def getWidth(self):
        return self.kids[0].getWidth()

    def __repr__(self):
        return '%s(%s,%s)' % (self.__class__.__name__, repr(self.kids[0]), repr(self.kids[1]))

    def _solve(self, emu=None, vals=None):
        v1 = self.kids[0].solve(emu=emu, vals=vals)
        v2 = self.kids[1].solve(emu=emu, vals=vals)
        return int(self.oper(v1, v2))

    def __eq__(self, con):
        '''
        Is this constraint the same as some other?
        '''
        if not isinstance(con, Constraint):
            return False

        c1v1 = self.kids[0].solve()
        c1v2 = self.kids[1].solve()
        c2v1 = con.kids[0].solve()
        c2v2 = con.kids[1].solve()

        if c1v1 == c2v1 and c1v2 == c2v2 and self.__class__ == con.__class__:
            return True

        if c1v1 == c2v2 and c1v2 == c2v1 and self.__class__ == con.revclass:
            return True

        return False

    def reverse(self):
        if self.revclass is None:
            raise Exception('Constraints Must Define revclass!')
        return self.revclass(self.kids[0], self.kids[1])

    def _op_reduce(self, v1, v1val, v2, v2val, emu):
        return self.__class__(v1, v2)


def oppose(c1, c2):
    c1.revclass = c2
    c2.revclass = c1


class eq(Constraint):
    oper = operator.eq
    operstr = '=='
    symtype = SYMT_CON_EQ


class ne(Constraint):
    oper = operator.ne
    operstr = '!='
    symtype = SYMT_CON_NE


class le(Constraint):
    oper = operator.le
    operstr = '<='
    symtype = SYMT_CON_LE


class gt(Constraint):
    oper = operator.gt
    operstr = '>'
    symtype = SYMT_CON_GT


class lt(Constraint):
    oper = operator.lt
    operstr = '<'
    symtype = SYMT_CON_LT


class ge(Constraint):
    oper = operator.ge
    operstr = '>='
    symtype = SYMT_CON_GE


class UNK(Constraint):
    operstr = 'UNK'
    symtype = SYMT_CON_UNK
    def oper(self, v1, v2):
        raise Exception('Attempted reduce/solve on UNK, which has no oper')


class NOTUNK(Constraint):
    operstr = '!UNK'
    symtype = SYMT_CON_NOTUNK
    def oper(self, v1, v2):
        raise Exception('Attempted reduce/solve on NOUNK, which has no oper')

# Create our oposing constraints
oppose(ne, eq)
oppose(le, gt)
oppose(lt, ge)
oppose(UNK, NOTUNK)

