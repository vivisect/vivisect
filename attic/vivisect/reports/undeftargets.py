"""Locate any xrefs/names to undefined locations"""

import vivisect

ref_names = {
    vivisect.REF_CODE:"Code",
    vivisect.REF_DATA:"Data",
    vivisect.REF_PTR:"Pointer",
}

columns = ( ("Bytes",str), ("Name", str) )

def report(vw):

    res = {}

    for fromva, tova, reftype, rflags in vw.getXrefs():
        if vw.getLocation(tova, range=True) == None:
            rname = ref_names.get(reftype, "Unknown")
            sname = "Unknown"
            seg = vw.getSegment(tova)
            if seg != None:
                sname = seg[vivisect.SEG_NAME]
            try:
                b = vw.readMemory(tova, 8).encode('hex')
            except Exception, e:
                b = str(e)
            res[tova] = (b, "%s ref from 0x%x (%s)" % (rname,fromva,sname))

    for va, name in vw.getNames():
        if vw.getLocation(va) == None:
            try:
                b = vw.readMemory(tova, 8).encode('hex')
            except Exception, e:
                b = str(e)
            res[va] = (b, name)

    return res

