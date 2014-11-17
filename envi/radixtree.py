'''
simple/fast python impl of a couple radix/prefix trees.
'''
import threading

class RadixIntTree:
    '''
    An integer indexed suffix tree.
    '''

    def __init__(self, bits=32):
        # each node is [ left, right, answers ]
        self.precount = 0
        self.bitwidth = bits
        self.treelock = threading.Lock()
        self.treeroot = [ None, None, None ]

    def addIntPrefix(self, value, bits, obj):
        '''
        Add an object to the prefix tree based on a value/bits pair.

        ( NOTE: most common use case is ipv4/ipv6 subnetting )
        '''
        with self.treelock:
            self.precount += 1
            shiftmax = self.bitwidth - 1
            bits = [ (value >> (shiftmax - i)) & 1 for i in xrange(bits) ]

            curnode = self.treeroot
            for bit in bits:
                nextnode = curnode[bit]
                if nextnode == None:
                    nextnode = [ None, None, None ]
                    curnode[bit] = nextnode
                curnode = nextnode

            curnode[2] = obj

    def getIntPrefixes(self, value):
        '''
        Retrieve a yield generator which returns the previously
        inserted objects in the prefix tree (best match last).
        '''
        shiftmax = self.bitwidth - 1
        bits = [ (value >> (shiftmax - i)) & 1 for i in xrange(self.bitwidth) ]

        curnode = self.treeroot
        for bit in bits:
            curnode = curnode[bit]
            if curnode == None:
                break

            obj = curnode[2]
            if obj != None:
                yield obj

    def getIntLongestPrefix(self, value):

        shiftmax = self.bitwidth - 1
        bits = [ (value >> (shiftmax - i)) & 1 for i in xrange(self.bitwidth) ]

        best = None
        curnode = self.treeroot
        for bit in bits:
            curnode = curnode[bit]
            if curnode == None:
                break

            obj = curnode[2]
            if obj != None:
                best = obj

        return best

if __name__ == '__main__':

    radtree = RadixIntTree()
    radtree.addIntPrefix(0x0a000000, 8, '8bitA')
    radtree.addIntPrefix(0x0a010000, 16, '16bitB')

    print list(radtree.getIntPrefixes( 0x0a010102))
    print list(radtree.getIntPrefixes( 0x56))
    print radtree.getIntLongestPrefix( 0x0a010102)
    print radtree.getIntLongestPrefix( 0x56)
