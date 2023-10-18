#!/usr/bin/env python2

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

conds = [
        'stz',
        'stnz',
        ]

repeats = [
        'smovb',
        'smovf',
        'smovu',
        'sstr',
        'suntil',
        'swhile',
        ]

privs = [
        'wait',
        ]

nofalls = [
        ]

def process(fbytes):
    flines = fbytes.split('\n')

    out = []
    mnems = []
    curmnem = None
    for fline in flines:
        fline = fline.strip()

        hashdx = fline.rfind('#')
        while hashdx > -1:
            print("process: comment-removal: %r" % fline)
            print("       : %r" % fline[hashdx:])
            if fline[hashdx:].startswith('#IMM') or\
                fline[hashdx:].startswith('#UIMM') or\
                fline[hashdx:].startswith('#SIMM'): 
                    # we have a immediate encoding
                    nextspc = fline.find(' ', hashdx)
                    if nextspc == -1:
                        nextspc = len(fline)
                    
                    newstuff = fline[hashdx+1: nextspc].lower()
                    fline = fline[:hashdx] + newstuff + fline[nextspc:]
                    print("immediate: %r\n    %r" % (newstuff, fline))
                    hashdx = fline.rfind('#')

            else:
                # it's a comment
                fline = fline[:hashdx].strip()
                hashdx = fline.rfind('#')
                print("comment")

        fline = fline.strip()

        # skip blank and comment-only lines
        if not len(fline) or fline.startswith('#'):
            continue

        print(fline)

        firstbyte = fline[0]
        # check for new mnemonic
        if 'a' <= firstbyte <= 'z':
            # it's a mnemonic
            curmnem = fline
            if curmnem not in mnems:
                mnems.append(curmnem)
            continue

        elif firstbyte in ['0', '1']:
            # it's a definition line
            lparts = fline.split(' ')
            #print(lparts)
            
            mask = 0
            endval = 0
            names = {}
            
            lidx = 0
            bidx = 0
            while lidx < len(lparts):
                size = 1
                item = lparts[lidx]
                #print("(%d) item: %r" % (bidx, item))

                if item in ('0', '1'):
                    # handle static bits
                    bit = int(item)
                    mask <<= 1
                    mask |= 1
                    endval <<= 1
                    endval |= bit
                    #print("%x:%x" % (mask, endval))

                else:
                    # named things
                    if '[' in item:
                        # this has multiple bits here
                        name, bits = item.replace(']','').split('[')
                        bitrange = bits.split(':')

                        #print(bitrange)
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
                        #print("looking for maxbit: ", item)
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
                    #print(cur)

                    #### finish stuff here
                lidx += 1
                bidx += size

            ldata = (fline, mask, endval, curmnem, names, bidx)
            out.append(ldata)
            print(ldata)
            #raw_input()
    return out, mnems


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

    forms = []
    nmconsts = []

    # TODO: if we have any items in the first byte, stomp them out

    for idx in range(256):
        # nexttbl, handler, mask, endval, mnems, opers, sz
        # opers should be a tuple of (type, shift, mask)'s
        if len(byte1[idx]) == 1:
            # this deserves it's own entry
            orig, mask, endval, mnem, opers, sz = byte1[idx][0]
            operands = convertOpers(opers, sz)
            form = getForm(mnem, opers, operands)
            iflagstr = getIflags(mnem, opers)

            operandstr = reprCvtdOpers(operands, nmconsts)
            if form not in forms and form != "None":
                forms.append(form)

            tblmain[idx] = "(None, %s, 0x%x, 0x%x, INS_%s, %r, %s, %r, %s)" % (form, mask, endval, mnem.upper(),mnem, operandstr, sz//8, iflagstr)

        elif not len(byte1[idx]):
            continue

        else:

            subtbl = []
            tblctr += 1
            tblname = 'tbl_%x' % idx
            tables[tblname] = subtbl

            openclist = byte1[idx]

            # sort from encoding! VERY IMPORTANT... ? 
            def cmp_to_key(mycmp):
                'Convert a cmp= function into a key= function'
                class K:
                    def __init__(self, obj, *args):
                        self.obj = obj
                    def __lt__(self, other):
                        return mycmp(self.obj, other.obj) < 0
                    def __gt__(self, other):
                        return mycmp(self.obj, other.obj) > 0
                    def __eq__(self, other):
                        return mycmp(self.obj, other.obj) == 0
                    def __le__(self, other):
                        return mycmp(self.obj, other.obj) <= 0
                    def __ge__(self, other):
                        return mycmp(self.obj, other.obj) >= 0
                    def __ne__(self, other):
                        return mycmp(self.obj, other.obj) != 0
                return K
            def thingsort(x, y):
                print("%r   ==?==   %r" % (x, y))
                xlowest = 255
                for xnm, xpart in x[4].items():
                    for key in xpart.keys():
                        if key < xlowest:
                            xlowest = key

                ylowest = 255
                for ynm, ypart in y[4].items():
                    for key in ypart.keys():
                        if key < ylowest:
                            ylowest = key

                delta = ylowest - xlowest
                if delta == 0: # they're equal size, compare mask specificity
                    xmask = x[1]
                    xbits = 0
                    while xmask:
                        if xmask & 1:
                            xbits += 1
                        xmask >>= 1

                    ymask = y[1]
                    ybits = 0
                    while ymask:
                        if ymask & 1:
                            ybits += 1
                        ymask >>= 1

                    delta = ybits - xbits
                    
                return delta

            openclist.sort(key=cmp_to_key(thingsort))

            for orig, mask, endval, mnem, opers, sz in openclist:
                operands = convertOpers(opers, sz)
                form = getForm(mnem, opers, operands)
                iflagstr = getIflags(mnem, opers)

                operandstr = reprCvtdOpers(operands, nmconsts)
                if form not in forms and form != "None":
                    forms.append(form)

                subtbl.append("(None, %s, 0x%x, 0x%x, INS_%s, %r, %s, %r, %s)" % (form, mask, endval, mnem.upper(), mnem, operandstr, sz//8, iflagstr))

            tblmain[idx] = "(%s, None, 0, 1, None, None, None, None, IF_NONE)" % (tblname)


    return tables, nmconsts, forms


def getForm(mnem, operdefs, operands):
    nms = [nm for nm in operdefs.keys()]

    if mnem == 'rtsd':
        return 'FORM_RTSD'
    elif mnem.startswith('movli'):
        return 'FORM_MOVLI'
    elif mnem.startswith('mvfa'):
        return 'FORM_MVFA'
    elif mnem == 'mov' and 'li' in nms and 'ld' in nms:
        #import envi.interactive as ei; ei.dbg_interact(locals(), globals())
        return 'FORM_MOV_RD_SZ_LD_LI'

    if 'ri' in nms:
        return 'FORM_MOV_RI_RB'
    if nms == ['rd', 'ld', 'mi', 'rs']:
        return 'FORM_RD_LD_MI_RS'
    if nms == ['rd', 'ld', 'rs']:
        if mnem in ('round','sbb','fadd','fdiv','fmul','fsqrt','fsub','ftoi','ftou',):
            return 'FORM_RD_LD_RS_L'
        elif mnem in ('bnot','bset',):
            return 'FORM_RD_LD_RS_B'
        return 'FORM_RD_LD_RS'
    if nms == ['a', 'rs2', 'rs']:
        return 'FORM_A_RS2_RS'
    if nms == ['rd', 'li']:
        return 'FORM_RD_LI'
    if nms == ['rs2', 'li']:
        return 'FORM_RS2_LI'
    if nms == ['ld','rs2',  'rs']:
        if mnem == 'fcmp':
            return 'FORM_LD_RS2_RS_L'
        elif mnem == 'tst':
            return 'FORM_LD_RS2_RS_UB'
    if nms == ['rd', 'imm']:
        return 'FORM_RD_IMM'
    if nms == ['pcdsp']:
        return 'FORM_PCDSP'
    if nms == ['rd', 'ld', 'imm', 'cd']:
        return 'FORM_BMCND' 
    if nms == ['rd', 'imm', 'cd']:
        return 'FORM_BMCND' 
    if nms == ['rd', 'sz', 'ld', 'cd']:
        return 'FORM_SCCND' 
    if len(nms) == 5:
        return 'FORM_GOOGOL'
    if 'ad' in nms:
        return 'FORM_AD'
    if 'imm' in nms:
        imm = operdefs.get('imm')
        if len(imm) == 1:
            startb, stopb = imm.values()[0] 
            if startb - stopb == 0:
                return 'FORM_IMM1'

    return 'None'

def getIflags(mnem, operdefs):
    if mnem in branches:
        pcdspvals = operdefs.get('pcdsp')

        if pcdspvals is not None:
            s, f = pcdspvals.values()[0]
            delta = s - f + 1
            if delta == 3:
                return 'IF_BRANCH | IF_NOFALL | IF_SMALL'
            elif delta == 8:
                return 'IF_BRANCH | IF_NOFALL | IF_BYTE'
            elif delta == 16:
                return 'IF_BRANCH | IF_NOFALL | IF_WORD'
            elif delta == 24:
                return 'IF_BRANCH | IF_NOFALL | IF_24BIT'
            elif delta == 32:
                return 'IF_BRANCH | IF_NOFALL | IF_LONG'

        elif mnem == 'bra' and operdefs.get('rs') is not None:
            return 'IF_BRANCH | IF_NOFALL | IF_LONG'

        return 'IF_BRANCH | IF_NOFALL'
    
    elif mnem in brconds:
        pcdspvals = operdefs.get('pcdsp')

        if pcdspvals is not None:
            s, f = pcdspvals.values()[0]
            delta = s - f + 1
            if delta == 3:
                return 'IF_BRANCH | IF_COND | IF_SMALL'
            elif delta == 8:
                return 'IF_BRANCH | IF_COND | IF_BYTE'
            elif delta == 16:
                return 'IF_BRANCH | IF_COND | IF_WORD'
            elif delta == 24:
                return 'IF_BRANCH | IF_COND | IF_24BIT'
            elif delta == 32:
                return 'IF_BRANCH | IF_COND | IF_LONG'

        return 'IF_BRANCH | IF_COND'
    
    elif mnem in calls:
        pcdspvals = operdefs.get('pcdsp')

        if pcdspvals is not None:
            s, f = pcdspvals.values()[0]
            delta = s - f + 1
            if delta == 3:
                return 'IF_CALL | IF_SMALL'
            elif delta == 8:
                return 'IF_CALL | IF_BYTE'
            elif delta == 16:
                return 'IF_CALL | IF_WORD'
            elif delta == 24:
                return 'IF_CALL | IF_24BIT'
            elif delta == 32:
                return 'IF_CALL | IF_LONG'
        elif mnem == 'bsr':
            return 'IF_CALL | IF_LONG'

        return 'IF_CALL'

    elif mnem in rets:
        return 'IF_RET | IF_NOFALL'

    elif mnem in conds:
        return 'IF_COND'

    elif mnem in repeats:
        return 'IF_REPEAT'

    elif mnem in privs:
        return 'IF_PRIV'

    elif mnem in nofalls:
        return 'IF_NOFALL'

    elif mnem == 'mov':
        odefs = operdefs.keys()
        odefs.sort()
        uirdefs = ['uimm','rd']
        uirdefs.sort()
        irdefs = ['imm','rd']
        irdefs.sort()
        lidefs = ['li','rd']
        lidefs.sort()

        if odefs in (irdefs, lidefs, uirdefs):
            return 'IF_LONG'

    return 'IF_NONE'

def convertOpers(opers, opsz):
    operands = []
    for nm, bdict in opers.items():
        nparts = []
        for pstart, (bstart, bend) in bdict.items():
            psz = 1 + bstart - bend
            pshift = opsz - pstart - psz - bend
            pmask = (1 << psz) - 1
            pmask <<= bend  # shift the mask if this is an upper part
            nparts.append((pshift, pmask))


        # fix dsp and ld to be easily determined whether it's src or dst
        if nm == 'ld':
            rdtup = opers.get('rd')
            rstup = opers.get('rs')
            rs2tup = opers.get('rs2')
            if rdtup is None:
                if rs2tup is None or rs2tup > rstup:
                    nm = 'lds'
                else:
                    nm = 'lds2'

            elif rstup is None:
                nm = 'ldd'
            elif rdtup > rstup:
                nm = 'lds'
            else:
                nm = 'ldd'

        if nm == 'dsp':
            rstup = opers.get('rs')
            rdtup = opers.get('rd')
            if rdtup is None:
                nm = 'dsps'
            elif rstup is None:
                nm = 'dspd'
            elif rdtup > rstup:
                nm = 'dsps'
            else:
                nm = 'dspd'

        if nm == 'ad':
            rstup = opers.get('rs')
            rdtup = opers.get('rd')
            if rdtup is None:
                nm = 'ads'
            elif rstup is None:
                nm = 'add'
            elif rdtup > rstup:
                nm = 'ads'
            else:
                nm = 'add'

            print("%-20s %-20s %-10s \t %50s" % (rstup, rdtup, nm, opers))

        operands.append((nm, tuple(nparts)))

    return operands

def reprCvtdOpers(operands, nmconsts):
    out = []

    for onm,oparts in operands:
        # create operand repr
        operstr = ' '.join(["(%d, 0x%x)," % (x,y) for x,y in oparts])
        nmconst = 'O_%s' % onm.upper()
        out.append(("(%s, (%s)), " % (nmconst, operstr)))

        # create nmconsts (so we're comparing numbers not strings)
        if nmconst not in nmconsts:
            nmconsts.append(nmconst)

    return '(' + ''.join(out) + ')'



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


CNDS = (
    'z',
    'nz',
    'geu',
    'ltu',
    'gtu',
    'leu',
    'pz',
    'n',
    'ge',
    'lt',
    'gt',
    'le',
    'o',
    'no',
    )

def reprConsts(mnems, nmconsts, forms):
    out = []
    out.append('''from envi.const import *
from envi import IF_NOFALL, IF_PRIV, IF_CALL, IF_BRANCH, IF_RET, IF_COND, IF_REPEAT

MODE_USER = 0
MODE_SUPV = 1

# opcode flags
IF_NONE = 0

IF_BYTE = 1<<8
IF_WORD = 1<<9
IF_LONG = 1<<10
IF_UWORD = 1<<11
IF_24BIT = 1<<12
IF_SMALL = 1<<13

SZ = [
    (IF_BYTE, 1),
    (IF_WORD, 2),
    (IF_LONG, 4),
    (IF_UWORD, 2),
    ]


# operand flags
OF_B = 1 << 0
OF_W = 1 << 1
OF_L = 1 << 2
OF_UW = 1 << 3
OF_UB = 1 << 4

MI_FLAGS = (
        (OF_B, 1),
        (OF_W, 2),
        (OF_L, 4),
        (OF_UW, 2),
        (OF_UB, 1),
        )

SIZE_BYTES = [None for x in range(17)]
SIZE_BYTES[OF_B] = 'b'
SIZE_BYTES[OF_W] = 'w'
SIZE_BYTES[OF_L] = 'l'
SIZE_BYTES[OF_UW] = 'uw'
SIZE_BYTES[OF_UB] = 'ub'


# instruction defs and mnemonics
''')

    out.append('BMCND = [')
    out.append('\n'.join(["    'bm%s'," % ins for ins in CNDS]))
    out.append(']')
    out.append('SCCND = [')
    out.append('\n'.join(["    'sc%s'," % ins for ins in CNDS]))
    out.append(']')
    out.append('mnems = [')
    out.append('\n'.join(["    '%s'," % ins for ins in mnems]))
    out.append(']')
    out.append('mnems.extend(BMCND)')
    out.append('mnems.extend(SCCND)\n')
    out.append('instrs = {}')
    out.append('for mnem in mnems:')
    out.append('    instrs["INS_%s" % mnem.upper()] = len(instrs)')
    out.append('\nglobals().update(instrs)')
    out.append('\n\n')

    out.append('nms = (')
    out.append('\n'.join(["    '%s'," % ins for ins in nmconsts]))
    out.append(')\n\n')
    out.append('nmconsts = {}')
    out.append('for nm in nms:')
    out.append('    nmconsts[nm.upper()] = len(nmconsts)')
    out.append('\nglobals().update(nmconsts)')
    out.append('\n\n')

    out.append('forms = (')
    out.append('\n'.join(["    '%s'," % ins for ins in forms]))
    out.append(')\n\n')
    out.append('formconsts = {}')
    out.append('for form in forms:')
    out.append('    formconsts[form.upper()] = len(formconsts)')
    out.append('\nglobals().update(formconsts)')
    out.append('\n\n')
    return '\n'.join(out)

def createRxTablesModule():
    data, mnems = process(open('rxtbls.raw').read()); [x for x in data if x[-1] % 8]
    tables, nmconsts, forms = genTables(data)

    out = []
    out.append('from .const import *')
    out.append(reprTables(tables))

    open('rxtables.py','w').write('\n'.join(out))
    open('const_gen.py', 'w').write(reprConsts(mnems, nmconsts, forms))

def formsHist(data):
    forms = {}
    formnms = {}
    bycnt = {}
    bynm = {}

    for thing in data:
        operdefs = thing[4]
        operdefrepr = repr(operdefs)
        operdefnmrepr = repr([nm for nm in operdefs.keys()])
        forms[operdefrepr] = forms.get(operdefrepr, 0) + 1
        formnms[operdefnmrepr] = formnms.get(operdefnmrepr, 0) + 1

        operdefcnt = len(operdefs)
        tmp = bycnt.get(operdefcnt)
        if tmp is None:
            tmp = {}
            bycnt[operdefcnt] = tmp
        tmp[operdefrepr] = tmp.get(operdefrepr, 0) + 1

        tmp = bynm.get(operdefcnt)
        if tmp is None:
            tmp = {}
            bynm[operdefcnt] = tmp
        tmp[operdefnmrepr] = tmp.get(operdefnmrepr, 0) + 1



    hist = [(y, x) for x,y in forms.items()]
    hist.sort()

    return forms, formnms, hist, bycnt, bynm




'''
import rxtprocess;reload(rxtprocess) ; data = rxtprocess.process(open('rxtbls.raw').read()); [x for x in data if x[-1] % 8]
'''

createRxTablesModule()
