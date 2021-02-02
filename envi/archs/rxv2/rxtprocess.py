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
    mnems = []
    curmnem = None
    for fline in flines:
        fline = fline.strip()

        hashdx = fline.rfind('#')
        while hashdx > -1:
            if fline[hashdx:].startswith('#IMM') or\
                fline[hashdx:].startswith('#UIMM') or\
                fline[hashdx:].startswith('#SIMM'): 
                    # we have a immediate encoding
                    nextspc = fline.find(' ', hashdx)
                    if nextspc == -1:
                        nextspc = len(fline)
                    
                    newstuff = fline[hashdx+1: nextspc].lower()
                    fline = fline[:hashdx] + newstuff + fline[nextspc:]

            else:
                # it's a comment
                fline = fline[:hashdx].strip()
                hashdx = fline.rfind('#')

        fline = fline.strip()

        # skip blank and comment-only lines
        if not len(fline) or fline.startswith('#'):
            continue

        print fline

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
            iflagstr = getIflags(mnem)

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
            def thingsort(x, y):
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
                return ylowest - xlowest

            openclist.sort(cmp=thingsort)

            for orig, mask, endval, mnem, opers, sz in openclist:
                operands = convertOpers(opers, sz)
                form = getForm(mnem, opers, operands)
                iflagstr = getIflags(mnem)

                operandstr = reprCvtdOpers(operands, nmconsts)
                if form not in forms and form != "None":
                    forms.append(form)

                subtbl.append("(None, %s, 0x%x, 0x%x, INS_%s, %r, %s, %r, %s)" % (form, mask, endval, mnem.upper(), mnem, operandstr, sz//8, iflagstr))

            tblmain[idx] = "(%s, None, 0, 1, None, None, None, None, IF_NONE)" % (tblname)


    return tables, nmconsts, forms


def getForm(mnem, operdefs, operands):
    nms = [nm for nm in operdefs.keys()]

    if nms == ['rd', 'ld', 'mi', 'rs']:
        return 'FORM_RD_LD_MI_RS'
    elif nms == ['rd', 'ld', 'rs']:
        return 'FORM_RD_LD_RS'
    elif nms == ['a', 'rs2', 'rs']:
        return 'FORM_A_RS2_RS'
    elif nms == ['rd', 'li']:
        return 'FORM_RD_LI'
    elif nms == ['rd', 'imm']:
        return 'FORM_RD_IMM'
    elif nms == ['pcdsp']:
        return 'FORM_PCDSP'
    elif nms == ['rd', 'ld', 'imm', 'cd']:
        return 'FORM_BMCND' 
    elif nms == ['rd', 'imm', 'cd']:
        return 'FORM_BMCND' 
    elif nms == ['rd', 'sz', 'ld', 'cd']:
        return 'FORM_SCCND' 
    elif len(nms) == 5:
        return 'FORM_GOOGOL'

    return 'None'

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


        # fix dsp to be easily determined whether it's src or dst
        if nm == 'ld':
            rstup = opers.get('rs')
            rdtup = opers.get('rd')
            if rdtup is None:
                nm = 'lds'
            elif rstup is None:
                nm = 'ldd'
            elif rdtup > rstup:
                nm = 'lds'
            else:
                nm = 'ldd'

            print "%-20s %-20s %-10s \t %50s" % (rstup, rdtup, nm, opers)

            #import envi.interactive as ei; ei.dbg_interact(locals(), globals()) 

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
from envi import IF_NOFALL, IF_PRIV, IF_CALL, IF_BRANCH, IF_RET, IF_COND

MODE_USER = 0
MODE_SUPV = 1

IF_NONE = 0

IF_BYTE = 1<<8
IF_WORD = 1<<9
IF_LONG = 1<<10
IF_UWORD = 1<<11

SZ = [
    (IF_BYTE, 1),
    (IF_WORD, 2),
    (IF_LONG, 4),
    (IF_UWORD, 2),
    ]


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
    out.append('from const import *')
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


