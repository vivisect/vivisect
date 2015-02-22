'''
Classes which implement shift/mask based lookups which are
similar to i386 page table lookups.
'''
import collections

class PageLook:

    def __init__(self, pagesize=4096):
        self.pagesize = pagesize
        self.pagemask = ~ (pagesize - 1)
        self.pagedict = {}

    def put(self, addr, size, val):
        '''
        Put an object into the page dictionary.

        Adding an object will allow any subsequent get() calls
        to return "val" when >= addr and < addr+size.

        Example:

            p = PageLook()
            p.put(0x41414000, 0xffff, 'woot')
            p.get(0x41414141) # returns 'woot'

        '''
        base = addr & self.pagemask
        maxaddr = addr + size

        while base < maxaddr:
            self.pagedict[base] = val
            base += self.pagesize

    def get(self, addr):
        '''
        Return an object previously added to the PageLook.

        Example:

            p = PageLook()
            p.put(0x41414000, 0xffff, 'woot')
            p.get(0x41414141) # returns 'woot'

        '''
        return self.pagedict.get( addr & self.pagemask )

    def clear(self):
        self.pagedict.clear()

class PageList:

    def __init__(self, pagesize=4096):
        self.pagesize = pagesize
        self.pagemask = ~ (pagesize - 1)
        self.pagedict = collections.defaultdict()

    def append(self, addr, size, obj):
        base = addr & self.pagemask
        maxaddr = addr + size

        while base < maxaddr:
            self.pagedict[base].append( val )
            base += self.pagesize

    def get(self, addr):
        return self.pagedict.get( addr & self.pagemask, () )

    def clear(self):
        self.pagedict.clear()


