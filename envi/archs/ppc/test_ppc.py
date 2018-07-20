
import sys
import struct
import envi.archs.ppc.disasm as eapd


def testByCategory(verbose=False):
    data = []
    for cat in eapd.CATEGORIES.keys():
        d = eapd.PpcDisasm(options=cat)
        out = []
        if verbose: print "\n====== CAT: %r ======" % eapd.CATEGORIES.get(cat)
        for key,instrlist in eapd.instr_dict.items():
            for instrline in instrlist:
                opcodenum = instrline[1]
                opcat = instrline[2][3]
                if not opcat & cat:
                    continue

                shifters = [(shl, mask) for nm,tp,shl,mask in instrline[2][-2]]
                shifters.sort()
                for oidx in range(len(shifters)):
                    shl, mask = shifters[oidx]
                    opcodenum |= (((len(shifters)-oidx) & mask) << shl)
                opbin = struct.pack(">I", opcodenum)
                try:
                    op = d.disasm(opbin, 0, 0x4000)
                    if verbose: print "0x%.8x:  %s" % (opcodenum, op)
                    data.append((opcodenum, op))
                except Exception, e:
                    sys.stderr.write("ERROR: 0x%x: %r\n" % (opcodenum, e))
                out.append(opbin)
    file("test_ppc.bin", "wb").write("".join(out))
    return data

def testDocs(docfile):
    docs = file('instructionset_table.txt').read()
    rightness = [line for line in docs.split('\n') if len(line) and line[0] not in ('I','T','M','E','F')] 
    
    realdata = testByCategory()
    realdata.sort()
    for opnum, op in realdata:
        #raw_input((opnum, op))
        match = False
        for r in rightness:

            if r.startswith('('):
                rmnem = rmnem[1:-1]
                ropers = ''
            else:
                rmnem, ropers = r.split()[:2]

            if rmnem == op.mnem:
                #print "Got It"
                match = True
                ropers = ropers.split(',')
                rlopers = [x.repr(op) for x in op.opers]
                #print op, ropers, rlopers
                break

        if not match:
            for r in rightness:
                if r.startswith('('):
                    rmnem = rmnem[1:-1]
                    ropers = ''
                else:
                    rmnem, ropers = r.split()[:2]

                if len(rmnem) and rmnem[-1] == '.':
                    fake = op.mnem[:-1] + 'x.'
                else:
                    fake = op.mnem + 'x'

                #print repr(r), repr(fake)
                if rmnem == fake:
                    #print "Got It"
                    match = True
                    ropers = ropers.split(',')
                    rlopers = [x.repr(op) for x in op.opers]
                    #print op, ropers, rlopers
                    break

        if not match:
            print("Couldn't find match in 'control' data  %x: %r" % (opnum, op))
            continue

        fail = compareOpers(ropers, rlopers)

        ### CHECK THE OPERANDS
        if fail:
            raw_input('  Compare Fail:  %r %r     %r    %r' % (rmnem, op.mnem, ropers, rlopers))




def compareOpers(ropers, rlopers):
    fail = False
    if len(ropers) != len(rlopers):
        if len(ropers) == 1 and len(rlopers) == 0 and ropers[0] == '\xe2\x80\x94':
            return False

        fail = True
    else:
        for oidx in range(len(ropers)):
            if ropers[oidx] == 'vD' and rlopers[oidx] == 'v1':
                ##print 1
                continue

            if ropers[oidx] == 'vS' and rlopers[oidx] == 'v1':
                #print 2
                continue

            if ropers[oidx].startswith('v') and rlopers[oidx] in ('v1', 'v2', 'v3', 'v4'):
                #print 3
                continue

            if ropers[oidx] == 'rD' and rlopers[oidx] == 'r1':
                #print 4
                continue

            if ropers[oidx] == 'frS' and rlopers[oidx] == 'f1':
                #print 4
                continue

            if ropers[oidx] == 'frD' and rlopers[oidx] == 'f1':
                #print 4
                continue

            if ropers[oidx].startswith('fr') and rlopers[oidx] in ('f1', 'f2', 'f3', 'f4'):
                #print 6
                continue


            if ropers[oidx] == 'rS' and rlopers[oidx] == 'r1':
                #print 5
                continue

            if ropers[oidx].startswith('r') and rlopers[oidx] in ('r1', 'r2', 'r3', 'r4'):
                #print 6
                continue

            if ropers[oidx].startswith('d(') and rlopers[oidx].startswith('0x') and rlopers[oidx].find('(r') != -1:
                #print 61
                continue

            if ropers[oidx].endswith('IMM') and rlopers[oidx].startswith('0x'):
                #print 7
                continue

            if ropers[oidx].endswith('RN') and rlopers[oidx].startswith('0x'):
                #print 8
                continue

            if ropers[oidx] in ('TO', 'SHB', 'L', 'LI', 'SH', 'ME', 'MB', 'BO', 'BI', 'BD', 'LEV', 'DUI', 'DUIS', 'OC', 'E', 'MO', 'CRM', 'T', 'CT', 'TH', 'SPR', 'WC', 'WH', 'SS', 'IU', 'OU', 'SA', 'FM', ) and rlopers[oidx].startswith('0x'):
                #print 9
                continue

            if ropers[oidx].startswith('cr') and ropers[oidx][2].isupper() and rlopers[oidx].startswith('cr') and len(rlopers[oidx]) == 3:
                continue

            if ropers[oidx].startswith('crb') and rlopers[oidx].startswith('cr') and rlopers[oidx].find('.') != -1:
                continue

            fail = True

    return fail


testDocs('instructionset_table.txt')
    
