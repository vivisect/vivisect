"""
Unified expression helpers.
"""
class ExpressionFail(Exception):
    def __init__(self, pycode):
        Exception.__init__(self)
        self.pycode = pycode

    def __repr__(self):
        return "ExpressionFail: %r is not a valid expression in this context" % self.pycode

    def __str__(self): 
        return self.__repr__()

def evaluate(pycode, locals):
    try:
        val = eval(pycode, {}, locals)
    except NameError, e:
        try:
            # check through the keys for anything we might want to replace
            keys = locals.keys()

            # sort the keys in reverse order so that longer matching strings take priority
            keys.sort(reverse=True)

            # replace the substrings with the string versions of the lookup value
            for key in keys:
                if key in pycode:
                    pval = locals[key]
                    pycode = pycode.replace(key, str(pval))
            
            val = eval(pycode, {}, locals)

        except NameError, e:
            raise ExpressionFail(pycode)

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
        if self.symobj != None:
            ret = self.symobj.getSymByName(name)
            if ret != None: return ret.value
        return dict.__getitem__(self, name)

    def __iter__(self):
        for va, name in self.symobj.getNames():
            yield name

        dict.__iter__(self)

    def keys(self):
        return [key for key in self]
        


class MemoryExpressionLocals(ExpressionLocals):

    def __init__(self, memobj, symobj=None):
        ExpressionLocals.__init__(self, symobj=symobj)
        self.memobj = memobj
        self.update({
            'mapbase':self.mapbase,
            'maplen':self.maplen,
            'ispoi':self.ispoi,
            'mem':self.mem,
            'poi':self.poi,
            'sym':self.sym,
        })

    def sym(self, symstr):
        '''
        An easy to use utility for symbols which have un-pythonic names.

        Example x = sym('kernel32.??2@$$FYAPAXI@Z')
        '''
        return long(evaluate(symstr, self))

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

