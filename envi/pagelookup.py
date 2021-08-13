'''
A home for the page lookup construct.  Basically it is a
python object which implements a similar lookup mechanism
to the i386 page table lookups...
'''
import collections

# FIXME move functions in here too so there is procedural "speed" way
# and objecty pythonic way...
def pagedict():
    return collections.defaultdict( lambda: [None] * 0xffff )

class PageLookup:
    '''
    An object capable of rapid lookups across a sparse address
    space which will also NOT eat *all* the RAMS like a straight
    dictionary full of millions of entries would.
    '''

    def __init__(self):
        self._page_dict = pagedict()

    def getPageLookup(self, va):
        page = self._page_dict.get( va >> 16 )
        if page is None:
            return None
        return page[ va & 0xffff ]

    def setPageLookup(self, va, size, obj):
        vamax = va+size

        p = self._page_dict
        # Super ugly, *very* fast speed hack
        [ p[ va >> 16 ].__setitem__( va & 0xffff, obj ) for va in range(va, vamax) ]

    # __getitem__
    # __getslice__
    # __setslice__

class MapLookup:

    '''
    A specialized lookup object for large densely populated ranges
    which are layed out in a sparse field space themselves...
    '''

    def __init__(self):
        self._maps_list = []

    def initMapLookup(self, va, size, obj=None):
        marray = [obj] * size
        # FIXME optimize by size!
        self._maps_list.append((va, va+size, marray))

    def setMapLookup(self, va, size, obj):
        for mva, mvamax, marray in self._maps_list:
            if va >= mva and va < mvamax:
                off = va - mva
                marray[off:off+size] = [obj] * size
                return
        raise Exception('Address (0x%.8x) not in maps!' % va)

    def getMapLookup(self, va):
        for mva, mvamax, marray in self._maps_list:
            if va >= mva and va < mvamax:
                return marray[ va - mva ]
        return None

    def delMapLookup(self, va):
        for midx in range(len(self._maps_list)):
            mva, mvamax, marray = self._maps_list[midx]
            if va >= mva and va < mvamax:
                return self._maps_list.pop(midx)

        raise e_exc.MapNotFoundException(va=va)


    def __getslice__(self, start, end):
        raise NotImplementedError("__getslice__ on MapLookup needs implementing")
