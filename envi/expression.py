"""
Unified expression helpers.
"""


class ExpressionFail(Exception):
    def __init__(self, pycode, exception):
        Exception.__init__(self)
        self.pycode = pycode
        self.exception = exception

    def __repr__(self):
        return "ExpressionFail: %r is not a valid expression in this context (%r)" % \
                (self.pycode, self.exception)

    def __str__(self):
        return self.__repr__()


def evaluate(pycode, locvars):
    try:
        val = eval(pycode, {}, locvars)
    except Exception:
        try:
            # check through the keys for anything we might want to replace
            keys = list(locvars.keys())

            # sort the keys in reverse order so that longer matching strings take priority
            keys.sort(reverse=True)

            # replace the substrings with the string versions of the lookup value
            for key in keys:
                if key in pycode:
                    pval = locvars[key]
                    pycode = pycode.replace(key, str(pval))

            val = eval(pycode, {}, locvars)

        except Exception as e:
            raise ExpressionFail(pycode, e)

    return val


class ExpressionLocals(dict):
    """
    An object to act as the locals dictionary for the evaluation
    of envi expressions.  You may pass in an envi.symstore.resolver.SymbolResolver
    object to automagically use symbols in your expressions.
    """
    def __init__(self, symobj=None):
        dict.__init__(self)
        self.symobj = symobj

    def __getitem__(self, name):
        if self.symobj is not None:
            ret = self.symobj.getSymByName(name)
            if ret is not None:
                if ret.symtype == 3:
                    return ret
                else:
                    return ret.value
        return dict.__getitem__(self, name)

    get = __getitem__

    def __iter__(self):
        if self.symobj is not None:
            for va, name in self.symobj.getNames():
                yield name

        yield from dict.__iter__(self)

    def keys(self):
        return [key for key in self]

    def __contains__(self, key):
        return self.__getitem__(key) is not None

class MemoryExpressionLocals(ExpressionLocals):

    def __init__(self, memobj, symobj=None):
        ExpressionLocals.__init__(self, symobj=symobj)
        self.memobj = memobj
        self.update({
            'mapbase': self.mapbase,
            'maplen': self.maplen,
            'ispoi': self.ispoi,
            'mem': self.mem,
            'poi': self.poi,
            'sym': self.sym,
        })

    def sym(self, symstr):
        '''
        An easy to use utility for symbols which have un-pythonic names.

        Example x = sym('kernel32.??2@$$FYAPAXI@Z')
        '''
        return int(evaluate(symstr, self))

    def mapbase(self, address):
        """
        The expression mapbase(address) returns the base address of the
        memory mapped area containing "address"
        """
        map = self.memobj.getMemoryMap(address)
        if not map:
            raise Exception("ERROR - un-mapped address in mapbase()")
        return map[0]

    def maplen(self, address):
        """
        The expression maplen(address) returns the length of the
        memory mapped area containing "address".
        """
        map = self.memobj.getMemoryMap(address)
        if not map:
            raise Exception("ERROR - un-mapped address in maplen()")
        return map[1]

    def ispoi(self, addr):
        """
        The expression ispoi(value) returns True if the specified value
        is a valid pointer.  Otherwise, False.
        """
        return self.memobj.isValidPointer(addr)

    def mem(self, addr, size):
        """
        Read and return memory.

        Example: mem(ecx, 20)
        """
        return self.memobj.readMemory(addr, size)

    def poi(self, address):
        """
        When expression contains "poi(addr)" this will return
        the address pointed to by addr.
        """
        return self.memobj.readMemoryPtr(address)
