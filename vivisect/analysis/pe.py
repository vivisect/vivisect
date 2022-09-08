"""
PE Extended analysis module.
"""

import vivisect
import envi.bits as e_bits

def analyze(vw):
    """
    """
    # Go through the relocations and create locations for them
    for segva, segsize, segname, segfname in vw.getSegments():
        reloc_va = vw.getFileMeta(segfname, "reloc_va")
        # Found binaries with multiple sections named .reloc where one was iat another
        # was actual reloc
        if reloc_va != segva:
            continue

        offset, bytes = vw.getByteDef(segva)
        while offset < segsize:
            # error cehck to make sure we are providing four bytes
            # to the parse routine
            if len(bytes[offset+4:offset+8]) != 4:
                break

            basepage = e_bits.parsebytes(bytes, offset, 4)

            vaoff = segva + offset
            vw.makeNumber(vaoff, 4)
            vw.makeName(vaoff, "reloc_chunk_%.8x" % vaoff)

            recsize = e_bits.parsebytes(bytes, offset+4, 4)
            if offset + recsize > segsize:
                break
            vw.makeNumber(segva+offset+4, 4)

            ioff = offset + 8
            while ioff < offset+recsize:
                vw.makeNumber(segva + ioff, 2)
                ioff += 2

            offset += recsize
            if recsize == 0:
                break


