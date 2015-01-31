import vivisect.lib.bits as v_bits

def makemask(s):
    return int( s.replace('0','1').replace('.','0'), 2)

def makemval(s):
    return int( s.replace('.','0'), 2 )

class DecodeNode:

    def __init__(self):
        self.match = None
        self.xacts = [None] * 256
        self.masks = []
        self.cache = [None] * 256
        self.ready = False

    def __repr__(self):
        self._get_ready()
        lines = []
        self.__repr_recurse(0,lines)
        return '\n'.join(lines)

    def __repr_recurse(self, indent, lines):
        pad = ' ' * indent
        lines.append(pad + 'node[%d]' % id(self))
        for i in range(len(self.xacts)):
            n = self.xacts[i]
            if n == None:
                continue

            lines.append(pad + 'xact: %.2x' % i)
            n.__repr_recurse(indent+1,lines)

        for mt,n in self.masks:
            xct,mask,maskval = mt
            lines.append(pad + ('mask: x & %.2x == %.2x' % (mask,maskval)))
            n.__repr_recurse(indent+1,lines)

        if self.match != None:
            lines.append(pad + 'match!')

    def addBitMask(self, maskstr, match):
        '''
        addBitMask('11100....1100000', 'FOO')
        '''
        self.ready = False
        masklen = len(maskstr)
        if masklen % 8:
            raise Exception('Invalid Mask Str: %s' % maskstr)

        maskparts = [ maskstr[i:i+8] for i in range(0,masklen,8) ]

        node = self
        for mp in maskparts:
            xct = mp.count('.')
            mask = makemask(mp)
            maskval = makemval(mp)

            # if it's an exact mask ( no .'s ) optimize!
            if xct == 0:
                n = node.xacts[maskval]
                if n == None:
                    n = DecodeNode()
                    node.xacts[maskval] = n
                node = n
                continue

            # keep count so we can order by xct
            mt = ( xct, mask, maskval )

            # check if we have this exact mask
            goround = False
            for masktup in node.masks:
                if masktup[0] == mt:
                    goround = True
                    node = masktup[1]
                    break

            if goround:
                continue

            n = DecodeNode()
            node.masks.append( (mt,n) )
            node = n

        # set the match object ref
        node.match = match

    def _get_ready(self):
        if not self.ready:
            self.masks.sort()
            self.cache = [ None ] * 256

            [ n._get_ready() for (m,n) in self.masks ]
            [ n._get_ready() for n in self.xacts if n != None ]

    def getByBytes(self, bytez, offset=0):
        '''
        Retrieve a previously added object 
        '''
        self._get_ready()

        node = self
        while node != None:
            # if we've found a match, return it
            if node.match != None:
                return node.match

            startnode = node
            val = bytez[offset]

            # check for an exact match
            newnode = node.xacts[val]
            if newnode != None:
                node = newnode
                offset += 1
                continue

            # check for cached values
            newnode = node.cache[val]
            if newnode != None:
                node = newnode
                offset += 1
                continue

            # mask / cmp until we find a hit
            for mtup,newnode in node.masks:
                xct,mask,maskval = mtup
                if mask & val == maskval:
                    node.cache[val] = newnode
                    node = newnode
                    offset += 1
                    break

            if node == startnode:
                return None

class Decoder:

    def __init__(self):
        self.rootnode = DecodeNode()

        self.callbacks = {}
        self.bitparsers = {}

    def addDecodeMask(self, mask, callback, **info):
        '''
        Add an mask and decoder callback.
        '''
        self.bitparsers[mask] = v_bits.bitparser(mask)
        dectup = (mask,callback,info)

        puremask = ''.join([c if c in ('0','1') else '.' for c in mask])
        self.rootnode.addBitMask(puremask,dectup)

    def runDecodeMask(self, bytez, offset=0, **info):
        '''
        Decode the given bytes as an instruction
        '''
        dectup = self.rootnode.getByBytes(bytez, offset=offset)
        if dectup == None:
            return None

        mask,callback,cbinfo = dectup
        info.update(cbinfo)

        info['off'] = offset
        info['mask'] = mask
        info['bytes'] = bytez

        bitparser = self.bitparsers.get(mask)
        if bitparser != None:
            info['bits'] = bitparser(bytez,offset=offset)

        # protect use of the vstruct ( so we can re-use )
        try:
            return callback(info)
        except Exception as e:
            traceback.print_exc()
