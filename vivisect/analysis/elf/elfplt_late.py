from . import elfplt

def analyze(vw):
    try:
        print('PLT: ' + '\nPLT: '.join([hex(x) for x,y in elfplt.getPLTs(vw)]))
        print(elfplt.getPLTs(vw))

        for pltva, pltsz in elfplt.getPLTs(vw):
            print("PLT: --- 0x%x:%d" % (pltva, pltsz))
            # find functions currently defined in this PLT
            curplts = []
            for fva in vw.getFunctions():
                if pltva <= fva < (pltva+pltsz) and fva not in curplts:
                    print(hex(fva))
                    curplts.append(fva)

            # now figure out the distance from function start to the GOT xref:
            heur = {}
            for fva in curplts:
                fsz = vw.getFunctionMeta(fva, 'Size')
                gotva, gotsz = elfplt.getGOT(vw, fva)

                offset = 0
                while offset < fsz:
                    locva, lsz, ltype, ltinfo = vw.getLocation(fva + offset)
                    xrefsfrom = vw.getXrefsFrom(locva)
                    for xrfr, xrto, xrtype, xrtinfo in xrefsfrom:
                        if gotva <= xrto < gotva+gotsz:
                            offcnt = heur.get(offset, 0)
                            heur[offset] = offcnt + 1

                    offset += lsz

            if not len(heur):
                continue

            print("GOT: 0x%x" % gotva)
            # if we have what we need... scroll through all the non-functioned area
            # looking for GOT-xrefs
            offbycnt = [(cnt, off) for off, cnt in heur.items()]
            offbycnt.sort(reverse=True)
            print(vw.getSegment(pltva))
            cnt, realoff = offbycnt[0]

            # now roll through the PLT space and look for GOT-references from 
            # locations that aren't in a function
            offset = 0
            while offset < pltsz:
                locva, lsz, ltype, ltinfo = vw.getLocation(pltva + offset)

                xrefsfrom = vw.getXrefsFrom(locva)
                print("loc: 0x%x   xrefs: %r" % (locva, xrefsfrom))
                toGOT = False
                for xrfr, xrto, xrtype, xrtinfo in xrefsfrom:
                    if gotva <= xrto < gotva+gotsz:
                        toGOT = True

                if toGOT:
                    # we have an xref into the GOT and no function.  go!
                    funcstartva = locva - realoff
                    print("PLT Function: 0x%x (GOT jmp: 0x%x)" % (funcstartva, locva))
                    if vw.getFunction(locva) != funcstartva:
                        print("NEW!!!!!")
                    vw.makeFunction(funcstartva)

                offset += lsz
                print("offset: %d" % offset)

            import envi.interactive as ei; ei.dbg_interact(locals(), globals())

    except Exception as e:
        import sys
        sys.excepthook(*sys.exc_info())

