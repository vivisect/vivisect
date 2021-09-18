import collections

# Symbol Type Constants ( for serialization )
SYMSTOR_SYM_SYMBOL = 0
SYMSTOR_SYM_FUNCTION = 1
SYMSTOR_SYM_SECTION = 2
SYMSTOR_SYM_MODULE = 3


class Symbol:

    symtype = SYMSTOR_SYM_SYMBOL

    def __init__(self, name, value, size=0, fname=None):
        self.name = name
        self.value = value
        self.size = size
        self.fname = fname

    def __ge__(self, other):
        return int(self) >= int(other)
    def __le__(self, other):
        return int(self) <= int(other)
    def __gt__(self, other):
        return int(self) > int(other)
    def __lt__(self, other):
        return int(self) < int(other)
    def __eq__(self, other):
        if not isinstance(other, Symbol):
            return False
        return int(self) == int(other)
    def __add__(self, other):
        return int(self) + int(other)
    def __sub__(self, other):
        return int(self) - int(other)
    def __mul__(self, other):
        return int(self) * int(other)
    def __div__(self, other):
        return int(self) / int(other)
    def __floordiv__(self, other):
        return int(self) // int(other)
    def __mod__(self, other):
        return int(self) % int(other)
    def __divmod__(self, other):
        return divmod(int(self), int(other))
    def __pow__(self, other, modulo=None):
        return pow(int(self), int(other), modulo)
    def __lshift__(self, other):
        return int(self) << int(other)
    def __rshift__(self, other):
        return int(self) >> int(other)
    def __and__(self, other):
        return int(self) & int(other)
    def __xor__(self, other):
        return int(self) ^ int(other)
    def __or__(self, other):
        return int(self) | int(other)
    # Operator swapped variants
    def __radd__(self, other):
        return int(other) + int(self)
    def __rsub__(self, other):
        return int(other) - int(self)
    def __rmul__(self, other):
        return int(other) * int(self)
    def __rdiv__(self, other):
        return int(other) / int(self)
    def __rfloordiv__(self, other):
        return int(other) // int(self)
    def __rmod__(self, other):
        return int(other) % int(self)
    def __rdivmod__(self, other):
        return divmod(int(other), int(self))
    def __rpow__(self, other, modulo=None):
        return pow(int(other), int(self), modulo)
    def __rlshift__(self, other):
        return int(other) << int(self)
    def __rrshift__(self, other):
        return int(other) >> int(self)
    def __rand__(self, other):
        return int(other) & int(self)
    def __rxor__(self, other):
        return int(other) ^ int(self)
    def __ror__(self, other):
        return int(other) | int(self)

    # Inplace variants
    def __iadd__(self, other):
        self.value += int(other)
        return self
    def __isub__(self, other):
        self.value -= int(other)
        return self
    def __imul__(self, other):
        self.value *= int(other)
        return self
    def __idiv__(self, other):
        self.value = int(self.value / int(other))
        return self
    def __ifloordiv__(self, other):
        self.value //= int(other)
        return self
    def __imod__(self, other):
        self.vsSetValue(self % other)
        self.value %= int(other)
        return self
    def __ipow__(self, other, modulo=None):
        self.value = pow(self.value, other, modulo)
        return self
    def __ilshift__(self, other):
        self.value <<= other
        return self
    def __irshift__(self, other):
        self.value >>= other
        return self
    def __iand__(self, other):
        self.value &= other
        return self
    def __ixor__(self, other):
        self.value ^= other
        return self
    def __ior__(self, other):
        self.value |= other
        return self

    def __hash__(self):
        return hash(int(self))

    def __int__(self):
        return int(self.value)

    def __len__(self):
        return self.size

    def __str__(self):
        if self.fname is not None:
            return "%s.%s" % (self.fname, self.name)
        return self.name

    def __repr__(self):
        return str(self)


class FunctionSymbol(Symbol):
    """
    Used to represent functions.
    """
    symtype = SYMSTOR_SYM_FUNCTION

    def __repr__(self):
        return "%s.%s()" % (self.fname, self.name)


class SectionSymbol(Symbol):
    """
    Used for file sections/segments.
    """
    symtype = SYMSTOR_SYM_SECTION

    def __repr__(self):
        return "%s[%s]" % (self.fname, self.name)


class SymbolResolver:
    """
    NOTE: Nothing should reach directly into a SymbolResolver!
    """

    def __init__(self, width=4, casesens=True, baseaddr=0):
        self.width = width
        self.widthmask = (2**(width*8))-1
        self.casesens = casesens
        self.baseaddr = baseaddr    # Set if this is an RVA sym resolver

        # Lets use 4096 byte buckes for now
        self.bucketsize = 4096
        self.bucketmask = self.widthmask ^ (self.bucketsize-1)

        self.buckets = collections.defaultdict(list)

        # holds tuples by name/addr, instantiated on demand and subsequently
        # stored in symobjsbyaddr and symobjsbyname
        self.symnames = {}
        self.symaddrs = {}

        # caches that hold instantiated Symbol objects
        self.symobjsbyaddr = {}
        self.symobjsbyname = {}

    def delSymbol(self, sym):
        """
        Delete a symbol from the resolver's namespace
        """
        symval = int(sym)
        self.symaddrs.pop(symval, None)

        # bbase = symval & self.bucketmask
        # self.objbuckets[bbase].remove(sym)

        subres = None
        if sym.fname is not None:
            subres = self.symnames.get(sym.fname)

        # Potentially del it from the sub resolver's namespace
        if subres is not None and not isinstance(subres, tuple):
            subres.delSymbol(sym)

        # Otherwise del it from our namespace
        else:
            symname = sym.name
            if not self.casesens:
                symname = symname.lower()
            self.symnames.pop(symname, None)

    def addSymbol(self, sym):
        """
        Add a symbol to the resolver.
        """
        # Fake these out for the API ( optimized implementations should *not* call this )
        symtup = (sym.value, sym.size, sym.name, sym.symtype, sym.fname)
        symtups = [symtup]

        self._nomSymTupAddrs(symtups)

        subres = self.symobjsbyname.get(sym.fname)
        if subres:
            subres._nomSymTupAddrs(symtups)
            subres._nomSymTupNames(symtups)
        else:
            self._nomSymTupNames(symtups)

        self._nomSymTupAddrs(symtups)

        return self._addSymObject(sym)

    def getSymByName(self, name):
        '''
        Retrieve a Symbol object by name.
        '''
        if not self.casesens:
            name = name.lower()

        # Do we have a cached object?
        sym = self.symobjsbyname.get(name)
        if sym is not None:
            return sym

        # Do we have a symbol tuple?
        symtup = self.symnames.get(name)
        if symtup is not None:
            return self._symFromTup(symtup)

    def delSymByName(self, name):
        if not self.casesens:
            name = name.lower()

        sym = self.symnames.get(name, None)
        if sym is not None:
            self.delSymbol(self._symFromTup(sym))

    def _symFromTup(self, symtup):
        # Create a symbol object and cache it...
        symaddr, symsize, symname, symtype, symfname = symtup
        symclass = symclasses[symtype]
        if symtype == SYMSTOR_SYM_MODULE:
            sym = FileSymbol(symname, symaddr, symsize, width=self.width)
        else:
            sym = symclass(symname, symaddr, size=symsize, fname=symfname)

        self._addSymObject(sym)
        return sym

    def _addSymObject(self, sym):
        # Add a symbol object to our datastructures.
        self.symobjsbyaddr[sym.value] = sym

        symmax = sym.value + sym.size

        bbase = sym.value & self.bucketmask

        if sym.fname:
            subres = self.symobjsbyname.get(sym.fname)
            if subres is not None:
                subres._addSymObject(sym)
                return

        symname = sym.name
        if not self.casesens:
            symname = symname.lower()

        self.symobjsbyname[symname] = sym

    def getSymByAddr(self, va, exact=True):
        """
        Return a symbol object for the given virtual address.
        """
        va = va & self.widthmask

        sym = self.symobjsbyaddr.get(va)
        if sym is not None:
            return sym

        symtup = self.symaddrs.get(va)
        if symtup:
            return self._symFromTup(symtup)

        # In the "not exact" case, go by the tuples...
        # ...and try 2 buckets... ( more than 8k away is bunk )
        if not exact:
            bucketva = va & self.bucketmask
            b1 = [ b for b in self.buckets[bucketva] if b[0] <= va ]
            if not b1:
                b1 = self.buckets[bucketva - self.bucketsize]

            if b1:
                b1.sort()
                symtup = b1[-1]
                sym = self.symobjsbyaddr.get(symtup[0])
                if sym is not None:
                    return sym

                return self._symFromTup(symtup)

    def getSymList(self):
        """
        Return a list of the symbols which are contained in this resolver.
        """
        out = [self.getSymByName(name) for name in self.symobjsbyname]
        out.extend([self.getSymByName(name) for name in self.symnames])
        return out

    def getSymHint(self, va, hidx):
        """
        May be used by symbol resolvers who know what type they are
        resolving to store and retrieve "hints" with indexes.

        Used specifically by opcode render methods to resolve
        any memory dereference info for a given operand.

        NOTE: These are mostly symbolic references to FRAME LOCAL
              names....
        """
        return None

    def _nomSymTupAddrs(self, symtups):

        # Ugly list comprehensions for speed...
        [self.symaddrs.__setitem__(n[0], n) for n in symtups]

        for symtup in symtups:
            # do the size range...
            self.buckets[symtup[0] & self.bucketmask].append(symtup)
            if symtup[1]:
                [self.buckets[b].append(symtup) for b in range(symtup[0], symtup[0] + symtup[1], self.bucketsize)]

    def _nomSymTupNames(self, symtups):
        if not self.casesens:
            [self.symnames.__setitem__( n[2].lower(), n ) for n in symtups]
        else:
            [self.symnames.__setitem__( n[2], n ) for n in symtups]

    def impSymCache(self, symcache, symfname=None, baseaddr=0):
        '''
        Import a list of symbol tuples (see getCacheSyms()) at the
        given base address ( and for the given sub-file )
        '''
        # Recieve a "cache" list and make it into our kind of tuples.
        symtups = [(symaddr + baseaddr, symsize, symname, symtype, symfname) for (symaddr, symsize, symname, symtype) in symcache]

        # Either way, index the addresses
        self._nomSymTupAddrs(symtups)

        if symfname:
            # If we have a sub-resolver, no need to add the names to
            # our name space...
            subres = self.symobjsbyname.get(symfname)
            if isinstance(subres, SymbolResolver):
                subres._nomSymTupAddrs(symtups)
                subres._nomSymTupNames(symtups)
                return

        self._nomSymTupNames(symtups)


class FileSymbol(Symbol, SymbolResolver):
    """
    A file symbol is both a symbol resolver of it's own, and
    a symbol.

    File symbols are used to do heirarchal symbol lookups and don't
    actually add anything but the name to their lookup (it is assumed
    that the parent Resolver of the FileSymbol takes care of addr lookups.
    """
    symtype = SYMSTOR_SYM_MODULE

    def __init__(self, fname, base, size, width=4):
        if fname is None:
            raise Exception('fname must not be None for a FileSymbol')

        SymbolResolver.__init__(self, width=width, baseaddr=base)
        Symbol.__init__(self, fname, base, size=size, fname=None)

    def __getattr__(self, name):
        """
        File symbols may be dereferenced like python objects to resolve
        symbols within them.
        """
        ret = self.getSymByName(name)
        if ret is None:
            raise AttributeError("%s has no symbol %s" % (self.name, name))
        return ret

    def __getitem__(self, name):
        """
        Allow dictionary style access for mangled incompatible names...
        """
        ret = self.getSymByName(name)
        if ret is None:
            raise KeyError("%s has no symbol %s" % (self.name, name))
        return ret

    # we need __getstate__ and __setstate__ because of serialization.  if
    # these are not overridden, __getattr__ is called, which subsequently calls
    # getSymByName, which tries to access self.casesens, which causes a
    # __getattr__ call, which leads to recursion.
    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, sdict):
        self.__dict__.update(sdict)

    # we don't *have* to override the other object methods, but otherwise
    # we will get incur the cost of extra symbol lookups for things like
    # __eq__, __ne__, etc.  we chose not to do it for lt, le, gt, ge, del and
    # others that we don't expect to see called often.
    def __repr__(self):
        return Symbol.__repr__(self)

    def __str__(self):
        return Symbol.__str__(self)

    def __eq__(self, other):
        return Symbol.__eq__(self, other)

    def __ne__(self, other):
        return not Symbol.__eq__(self, other)

    def __hash__(self):
        return Symbol.__hash__(self)

    def __nonzero__(self):
        return True

symclasses = (Symbol, FunctionSymbol, SectionSymbol, FileSymbol)
