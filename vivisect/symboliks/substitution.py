'''
Symboliks algebraic substitution helpers (SubStates)

Users of this API probably want the following two classes:

sset - Produces a given set of values ( ie. [1,3,33,9384] )
srange - Iterates similar to range (ie. max,min,inc )

Once instanciated, any SubState may be multiplied or added to
others to create the implied set of states.

For example, the following little example:
=======================================
    x = srange('arg0', 3)
    y = sset('arg1', [1,9,13])

    print('added:')
    for i in (x+y):
        print repr(i)

    print('multiplied:')
    for i in (x*y):
        print repr(i)
=======================================

Produces the following output:
=======================================
added:
{'arg0': 0, 'arg1': 1}
{'arg0': 1, 'arg1': 1}
{'arg0': 2, 'arg1': 1}
{'arg0': 0, 'arg1': 1}
{'arg0': 0, 'arg1': 9}
{'arg0': 0, 'arg1': 13}
multiplied:
{'arg0': 0, 'arg1': 1}
{'arg0': 1, 'arg1': 1}
{'arg0': 2, 'arg1': 1}
{'arg0': 0, 'arg1': 9}
{'arg0': 1, 'arg1': 9}
{'arg0': 2, 'arg1': 9}
{'arg0': 0, 'arg1': 13}
{'arg0': 1, 'arg1': 13}
{'arg0': 2, 'arg1': 13}
=======================================
'''


class SubState:
    '''
    The base SubState class designed to help out creating
    iterable combinatorc states.
    '''
    def __init__(self, iname, icount):
        self.iname = iname
        self.icount = icount

    def getCombState(self, i, d=None):
        if d is None:
            d = {}
        d[self.iname] = self[i]
        return d

    def __iter__(self):
        for i in range(len(self)):
            yield self.getCombState(i)

    def __getslice__(self, x, y):
        for i in range(x, y+1):
            yield self.getCombState(i)

    def __add__(self, x):
        return AddSubState(self, x)

    def __mul__(self, x):
        return MultSubState(self, x)

    def __len__(self):
        return self.icount

    def __getitem__(self, i):
        raise Exception('SubState must implement __getitem__!')


class AddSubState(SubState):
    '''
    A combiner which produces the union of the two
    given combiner.
    '''
    def __init__(self, comb1, comb2):
        comb1len = len(comb1)
        comb2len = len(comb2)

        SubState.__init__(self, None, comb1len + comb2len)
        self.comb1 = comb1
        self.comb2 = comb2
        self.comb1len = comb1len
        self.comb2len = comb2len

    def getCombState(self, i, d=None):
        if d is None:
            d = {}

        if i >= self.comb1len:
            c1 = 0
            c2 = i - self.comb1len
            # Do these in this order in case they have
            # two sets for the same var...
            self.comb1.getCombState(c1, d=d)
            self.comb2.getCombState(c2, d=d)
        else:
            c1 = i
            c2 = 0
            # and likewise... ( see above )
            self.comb2.getCombState(c2, d=d)
            self.comb1.getCombState(c1, d=d)

        return d


class MultSubState(SubState):

    def __init__(self, comb1, comb2):
        comb1len = len(comb1)
        comb2len = len(comb2)

        SubState.__init__(self, None, comb1len * comb2len)
        self.comb1 = comb1
        self.comb2 = comb2
        self.comb1len = comb1len
        self.comb2len = comb2len

    def getCombState(self, i, d=None):
        if d is None:
            d = {}

        c2, c1 = divmod(i, self.comb1len)

        self.comb1.getCombState(c1, d=d)
        self.comb2.getCombState(c2, d=d)
        return d


class srange(SubState):
    '''
    A SubState class which produces values over a range similar
    to the python builtin range.

    Example:
        # substitute arg0 from 4 to 29 (inclusive)
        srange('arg0', 30, 4)
    '''
    def __init__(self, iname, imax, imin=0, iinc=1):
        icount = int((imax - imin) / iinc)
        SubState.__init__(self, iname, icount)
        self.imin = imin
        self.imax = imax
        self.iinc = iinc

    def __getitem__(self, i):
        return self.imin + (self.iinc * i)


class sset(SubState):
    '''
    A SubState class which produces values from an
    iterable object (which it must turn into a list).

    Example:
        # substitute arg1 through the values 5,56,90
        sset('arg1', [5,56,90])
    '''
    def __init__(self, iname, items):
        items = list(items)
        SubState.__init__(self, iname, len(items))
        self.combitems = items

    def __getitem__(self, i):
        return self.combitems[i]
