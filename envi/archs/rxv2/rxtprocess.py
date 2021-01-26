branches = [
        'jmp',
        'bra',
        ]

brconds = [
        'bz', 
        'bge',
        'bnz', 
        'blt',
        'bgeu',
        'bgt',
        'bltu', 
        'ble',
        'bgtu', 
        'bo',
        'bleu', 
        'bno',
        'bpz', 
        'bn', 
        ]

calls = [
        'bsr',
        'jsr',
        ]

rets = [
        'rte',
        'rtfi',
        'rts',
        'rtsd',
        ]

def process(fbytes):
    flines = fbytes.split('\n')

    out = []
    curmnem = None
    for fline in flines:
        fline = fline.strip()

        hashdx = fline.find('#')
        if hashdx > -1:
            fline = fline[:hashdx].strip()

        # skip blank and comment-only lines
        if not len(fline) or fline.startswith('#'):
            continue

        print fline

        firstbyte = fline[0]
        # check for new mnemonic
        if 'a' <= firstbyte <= 'z':
            # it's a mnemonic
            curmnem = fline
            continue

        elif firstbyte in ['0', '1']:
            # it's a definition line
            lparts = fline.split(' ')
            #print lparts
            
            mask = 0
            endval = 0
            names = {}
            
            lidx = 0
            bidx = 0
            while lidx < len(lparts):
                size = 1
                item = lparts[lidx]
                #print "(%d) item: %r" % (bidx, item)

                if item in ('0', '1'):
                    # handle static bits
                    bit = int(item)
                    mask <<= 1
                    mask |= 1
                    endval <<= 1
                    endval |= bit
                    #print "%x:%x" % (mask, endval)

                else:
                    # named things
                    if '[' in item:
                        # this has multiple bits here
                        name, bits = item.replace(']','').split('[')
                        bitrange = bits.split(':')

                        #print bitrange
                        if len(bitrange) > 1:
                            bithi, bitlo = [int(x) for x in bitrange] # of that field
                            size += bithi - bitlo
                            valadd = (bithi, bitlo)

                            # let's store optimized for a "shift/mask" approach
                            # or maybe for now, let's just store the data closer to the docs... fix up later
                        else:
                            valadd = (int(bitrange[0]), int(bitrange[0]))

                    elif ':' in item:
                        # no [] but : - we're talking about pcdsp:8 style
                        #print "looking for maxbit: ", item
                        name, bits = item.split(':')
                        size = int(bits)
                        valadd = (size-1, 0)

                    else:
                        name = item
                        valadd = (0, 0)

                    mask <<= size
                    endval <<= size

                    # get cur name entry, create if new
                    cur = names.get(name)
                    if cur is None:
                        cur = {}
                        names[name] = cur

                    cur[bidx] = valadd
                    #print cur

                    #### finish stuff here
                lidx += 1
                bidx += size

            ldata = (fline, mask, endval, curmnem, names, bidx)
            out.append(ldata)
            print ldata
            #raw_input()
    return out


def getHist(data):
    hist = {}
    for x in data:                     
        sig = x[4]                       
        hist[repr(sig)] = hist.get(repr(sig), 0) + 1

    return hist

def orderByByte1(data):
    byte1 = [[] for x in range(256)]
    for ld in data:
        a,mask,endval,mnem,fields,sz = ld
        tmask = mask >> (sz-8)
        tval = endval >> (sz-8)
        for x in range(256):
            if x & tmask == tval:
                byte1[x].append(ld)
    return byte1

def genTables(data):
    byte1 = orderByByte1(data)

    tblctr = 0
    tables = {}

    tblmain = [None for x in range(256)]
    tables['tblmain'] = tblmain

    for idx in range(256):
        # nexttbl, handler, mask, endval, mnems, opers, sz
        # opers should be a tuple of (type, shift, mask)'s
        if len(byte1[idx]) == 1:
            # this deserves it's own entry
            orig, mask, endval, mnem, opers, sz = byte1[idx][0]
            operands = convertOpers(opers, sz)
            iflagstr = getIflags(mnem)

            # fix dsp to be easily determined whether it's src or dst

            # if we have any items in the first byte, stomp them out

            tblmain[idx] = "(None, None, 0x%x, 0x%x, INS_%s, %r, %r, %r, %s)" % (mask, endval, mnem.upper(),mnem, operands, sz//8, iflagstr)

        elif not len(byte1[idx]):
            continue

        else:

            subtbl = []
            tblctr += 1
            tblname = 'tbl_%x' % idx
            tables[tblname] = subtbl
            iflagstr = getIflags(mnem)

            for orig, mask, endval, mnem, opers, sz in byte1[idx]:
                operands = convertOpers(opers, sz)
                subtbl.append("(None, None, 0x%x, 0x%x, INS_%s, %r, %r, %r, %s)" % (mask, endval, mnem.upper(), mnem, operands, sz//8, iflagstr))

            tblmain[idx] = "(%s, None, 0, 1, None, None, None, None, IF_NONE)" % (tblname)


    return tables
def getIflags(mnem):
    if mnem in branches:
        return 'IF_BRANCH | IF_NOFALL'
    
    elif mnem in brconds:
        return 'IF_BRANCH | IF_COND'
    
    elif mnem in calls:
        return 'IF_CALL'

    elif mnem in rets:
        return 'IF_RET | IF_NOFALL'

    return 'IF_NONE'

def convertOpers(opers, opsz):
    operands = []
    for nm, bdict in opers.items():
        nparts = []
        for pstart, (bstart, bend) in bdict.items():
            psz = 1 + bstart - bend
            pshift = opsz - pstart - psz
            pmask = (1 << psz) - 1
            pmask <<= bend  # shift the mask if this is an upper part
            nparts.append((pshift, pmask))

        operands.append((nm, tuple(nparts)))

    return operands


def reprTables(tables):
    out = []

    for tkidx in range(256):
        tkey = 'tbl_%x' % tkidx
        tvals = tables.get(tkey)
        if tvals is None:
            continue
        _ptAppendTdata(tkey, tvals, out)

    # add the tblmain at the end
    tkey = 'tblmain'
    tvals = tables.get(tkey)
    _ptAppendTdata(tkey, tvals, out)

    return '\n'.join(out)

def _ptAppendTdata(tkey, tvals, out):
        tout = ['    %s,' % vline for vline in tvals]
        out.append('%s = (\\' % tkey)
        out.extend(tout)
        out.append(')\n\n')


def createRxTablesModule():
    out = []
    out.append('''
from envi import *

IF_NONE = 0
SZ = [
    IF_BYTE,
    IF_WORD,
    IF_LONG,
    IF_UWORD,
    ]

''')
    data = process(open('rxtbls.raw').read()); [x for x in data if x[-1] % 8]
    tables = genTables(data)
    out.append(reprTables(tables))

    open('rxtables.py','w').write('\n'.join(out))






'''
import rxtprocess;reload(rxtprocess) ; data = rxtprocess.process(open('rxtbls.raw').read()); [x for x in data if x[-1] % 8]
'''


