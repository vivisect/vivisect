import envi.bits as e_bits

class BinaryTree:
    '''
    A simple binary search tree capable of using integers
    or string representations of binary integers as inputs.

    NOTE: the lookup routines assume once a node is found which
    has nodeinfo, we have matched.  It does *not* need to walk
    the rest of the values...
    '''
    def __init__(self):
        self.basenode = [None, None, None]

    def addInt(self, intval, width, nodeinfo):
        node = self.basenode
        for sh in range(width-1, -1, -1):
            choice = (intval >> sh) & 1
            if node[choice] is None:
                node[choice] = [None, None, None]
            node = node[choice]
        node[2] = nodeinfo

    def addBinstr(self, binstr, nodeinfo):
        bval = e_bits.binary(binstr)
        return self.addInt(bval, len(binstr), nodeinfo)

    #def addString(self, charstr, nodeinfo):
    # e_bits the whole string to a huge int?

    def getInt(self, intval, width):
        '''
        Get an element back out of the tree.

        width is in bits...
        '''
        node = self.basenode
        for sh in range(width-1, -1, -1):
            choice = (intval >> sh) & 1
            node = node[choice]
            ninfo = node[2]
            if ninfo is not None:
                return ninfo
        return node[2]

    def getBinstr(self, binstr):
        bval = e_bits.binary(binstr)
        return self.getInt(bval, len(binstr))
