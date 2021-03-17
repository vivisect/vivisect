import logging

import Elf
import envi.bits as e_bits
import vivisect.exc as v_exc
import vstruct
import vstruct.primitives as vs_prim
import vstruct.defs.dwarf as vs_dwarf

from vstruct.defs.dwarf import *

logger = logging.getLogger(__name__)


def leb128ToInt(bytez, bitlen=64, signed=False):
    '''
    Return tuple of the decoded value and how many bytes it consumed to decode the value
    '''
    valu = 0
    shift = 0
    signBit = False
    for i, bz in enumerate(bytez, start=1):
        bz = bz
        valu |= (bz & 0x7f) << shift
        shift += 7
        if not bz & 0x80:
            signBit = True if bz & 0x40 else False
            break

    if signed and signBit and shift < bitlen:
        valu |= - (1 << shift)

    return valu, i


class DwarfInfo:
    def __init__(self, vw, pbin, strtab=b''):
        self.vw = vw
        self.pbin = pbin
        # strab typically only shows up in cygwin binaries
        self.secmap = {}
        self.strtable = strtab
        if self.strtable:
            for sec in pbin.getSections():
                # so this is cygwin's shorthand for certain section with long names
                if sec.Name.startswith('/'):
                    indx = int(sec.Name[1:], 10)
                    name = self.strtable[indx:].split(b'\x00', 1)[0]
                    self.secmap[name.decode('utf-8')] = sec
        self.abbrev = self._parseDebugAbbrev()
        self.info = self._parseDebugInfo()
        self.line = self._parseDebugLine()

    def getSectionBytes(self, name):
        if isinstance(self.pbin, Elf.Elf):
            return self.pbin.getSectionBytes(name)
        else:
            sec = self.secmap.get(name)
            if not sec:
                logger.warning('Could not find bytes for section %s', name)
                return None
            return self.pbin.readAtRva(sec.VirtualAddress, sec.VirtualSize)

    def _getDebugString(self, offset, use_utf8=False):
        '''
        TODO: We can make this so much faster by just preparsing and indexing them by
        their offsets
        '''
        bytez = self.getSectionBytes('.debug_str')
        if bytez is None or offset > len(bytez):
            return None
        return bytez[offset:].split(b'\x00', 1)[0]

    def _getBlock(self, length, bytez):
        block = vs_prim.v_bytes(size=length.vsGetValue())
        block.vsParse(bytez)
        return block

    def _getExprLoc(self, bytez):
        pass

    def _getFormData(self, form, bytez, addrsize, is64BitDwarf=False, use_utf8=False):
        '''
        TODO: So for anything marked "constant", we technically have to use "context" to determine if it's
        signed, unsigned, target machine endianness, etc. as per the dwarf docs

        Returns a tuple of (attribute name, vstruct data, how many bytes were consumed)
        '''
        extra = 0
        if form == DW_FORM_addr:
            # So this is technically supposed to come from the compilation header in the info section,
            # but for now we're going to cheat and just use the info we grabbed from the elf header itself
            if addrsize == 8:
                vsData = vs_prim.v_ptr64(bigend=self.vw.bigend)
            else:
                vsData = vs_prim.v_ptr32(bigend=self.vw.bigend)
            vsData.vsParse(bytez)

        elif form == DW_FORM_block:  # special block
            # TODO
            blocklen, extra = leb128ToInt(bytez)
            vsData = vs_prim.v_bytes(size=blocklen)
            vsData.vsParse(bytez, extra)

        elif form == DW_FORM_block1:  # block
            blocklen = vs_prim.v_uint8(bigend=self.vw.bigend)
            blocklen.vsParse(bytez)
            vsData = self._getBlock(blocklen, bytez[len(blocklen):])
            extra = blocklen

        elif form == DW_FORM_block2:  # block
            blocklen = vs_prim.v_uint16(bigend=self.vw.bigend)
            blocklen.vsParse(bytez)
            vsData = self._getBlock(blocklen, bytez[len(blocklen):])
            extra = blocklen

        elif form == DW_FORM_block4:  # block
            blocklen = vs_prim.v_uint32(bigend=self.vw.bigend)
            blocklen.vsParse(bytez)
            vsData = self._getBlock(blocklen, bytez[len(blocklen):])
            extra = blocklen

        elif form == DW_FORM_data1:  # constant
            vsData = vs_prim.v_uint8(bigend=self.vw.bigend)
            vsData.vsParse(bytez)

        elif form == DW_FORM_data2:  # constant
            vsData = vs_prim.v_uint16(bigend=self.vw.bigend)
            vsData.vsParse(bytez)

        elif form == DW_FORM_data4:  # constant
            vsData = vs_prim.v_uint32(bigend=self.vw.bigend)
            vsData.vsParse(bytez)

        elif form == DW_FORM_data8:  # constant
            vsData = vs_prim.v_uint64(bigend=self.vw.bigend)
            vsData.vsParse(bytez)

        elif form == DW_FORM_string:  # string
            # Directly in the .debug_info section
            vsData = vs_prim.v_str(size=bytez.index(b'\x00'))
            vsData.vsParse(bytez)
            # Don't forget about skipping the null terminator
            extra = 1

        elif form == DW_FORM_flag:  # flag
            vsData = vs_prim.v_uint8(bigend=self.vw.bigend)
            vsData.vsParse(bytez)

        elif form == DW_FORM_strp:  # string
            # a ptr-sized offset into the string table .debug_str
            if is64BitDwarf:
                offset = vs_prim.v_int64(bigend=self.vw.bigend)
                offset.vsParse(bytez)
            else:
                offset = vs_prim.v_int32(bigend=self.vw.bigend)
                offset.vsParse(bytez)
            strp = self._getDebugString(offset.vsGetValue(), use_utf8)
            vsData = vs_prim.v_str(len(strp), val=strp)

            # strp is special since it's an easy reference into a table
            return vsData, len(offset)

        elif form == DW_FORM_sdata:  # constant
            bits = self.vw.psize * 8
            slen, extra = leb128ToInt(bytez, bitlen=bits, signed=True)
            slen = e_bits.signed(slen, extra)
            if bits == 64:
                return vs_prim.v_int64(slen), extra
            else:
                return vs_prim.v_int32(slen), extra

        elif form == DW_FORM_udata:  # constant
            bits = self.vw.psize * 8
            ulen, extra = leb128ToInt(bytez, bitlen=bits)
            if bits == 64:
                return vs_prim.v_uint64(ulen), extra
            else:
                return vs_prim.v_uint32(ulen), extra

        elif form == DW_FORM_ref_addr:  # ref
            if is64BitDwarf:
                vsData = vs_prim.v_ptr64(bigend=self.vw.bigend)
            else:
                vsData = vs_prim.v_ptr32(bigend=self.vw.bigend)
            vsData.vsParse(bytez)

        elif form == DW_FORM_ref1:  # ref
            vsData = vs_prim.v_uint8(bigend=self.vw.bigend)
            vsData.vsParse(bytez)

        elif form == DW_FORM_ref2:  # ref
            vsData = vs_prim.v_uint16(bigend=self.vw.bigend)
            vsData.vsParse(bytez)

        elif form == DW_FORM_ref4:  # ref
            vsData = vs_prim.v_uint32(bigend=self.vw.bigend)
            vsData.vsParse(bytez)

        elif form == DW_FORM_ref8:  # ref
            vsData = vs_prim.v_uint64(bigend=self.vw.bigend)
            vsData.vsParse(bytez)

        elif form == DW_FORM_ref_udata:  # ref
            # refers to something within the .debug_info section
            # variable length offset
            # XXX
            reflen, extra = leb128ToInt(bytez)
            vsData = vs_prim.v_uint64(value=reflen, bigend=self.vw.bigend)
            return vsData, extra

        elif form == DW_FORM_indirect:  # SPECIAL
            # TODO: Is this right?
            valu, extra = leb128ToInt(bytez)
            vsData = vs_prim.v_uint64(value=valu, bigend=self.vw.bigend)
            return vsData, extra

        elif form == DW_FORM_sec_offset:  # lineptr, loclistptr, macptr, rangelistptr
            if is64BitDwarf:
                vsData = vs_prim.v_int64(bigend=self.vw.bigend)
                vsData.vsParse(bytez)
            else:
                vsData = vs_prim.v_int32(bigend=self.vw.bigend)
                vsData.vsParse(bytez)
            # raise Exception("IMPLEMENT ME!")
            # TODO: so where the offset is depends on what subtype the sec_offset is, but that's determined
            # by the attr name, and honestly, right now, I don't care about that

        elif form == DW_FORM_exprloc:  # exprloc
            loclen, extra = leb128ToInt(bytez)
            vsData = vs_prim.v_bytes(loclen)
            vsData.vsParse(bytez[extra:])
            # self._getExprLoc(vsData)

        elif form == DW_FORM_flag_present:  # flag
            # Don't actually consume any bytes, but do indicate the flag is there
            vsData = vs_prim.v_uint8(value=1)
            return vsData, 0

        elif form == DW_FORM_ref_sig8:  # reference
            vsData = vs_prim.v_int64(bigend=self.vw.bigend)
            vsData.vsParse(bytez)

        else:
            raise Exception('Unrecognized debug form 0x%.4x' % form)

        return vsData, len(vsData) + extra

    def _parseDebugInfo(self):
        '''
        '''
        # Use that to parse out things from the .debug_info section
        vw = self.vw
        debuginfo = []
        is64BitDwarf = False
        bytez = self.getSectionBytes('.debug_info')
        if bytez is None:
            return
        consumed = 0
        while consumed < len(bytez):
            # Parse the compile unit header
            # we can have 32 bit dwarf in a 64 bit binary and the way they dynamic repr that
            # is by all the 64 bit addresses being 12 bytes long, but the first 4 are 0xffffffff
            version = vs_prim.v_uint32(bigend=vw.bigend)
            if version == 0xFFFFFFFF:
                consumed += 4
                header = vs_dwarf.Dwarf64CompileHeader(bigend=vw.bigend)
                is64BitDwarf = True
            else:
                header = vs_dwarf.Dwarf32CompileHeader(bigend=vw.bigend)
                # So it says it's 12 bytes, but the first 4 are ffffffff

            header.vsParse(bytez[consumed:])
            abbrev = self.abbrev[header.abbrev_offset]
            cuoffs = {}

            # so the header in 64 bit is weird, since the first 4 are going to all f's for the length field
            consumed += len(header)
            toConsume = header.length + len(header.vsGetField('length'))
            unitConsumed = 0
            startoff = len(header)
            parentChain = []
            # Need to grab the compile headers attributes and promote those for things like use_utf8
            # Or just parse out the first header block?

            while len(header) + unitConsumed < toConsume:
                idx, ulen = leb128ToInt(bytez[consumed + unitConsumed:])
                unitConsumed += ulen
                if idx == 0:
                    startoff += 1
                    parentChain.pop()
                    continue

                tag, hasKids, typeinfo = abbrev[idx]
                # Need to actually do something with struct
                struct = vstruct.VStruct()
                struct.vsAddField('tag', vs_prim.v_uint16(tag))
                for attr, attrForm in typeinfo:
                    if attr > DW_AT_lo_user and attr < DW_AT_hi_user:
                        # try reaching into the gnu attribute names since they're a well known
                        # "vendor"
                        name = gnu_attribute_names.get(attr, "UNK")
                    else:
                        name = dwarf_attribute_names.get(attr, "UNK")

                    vsForm, flen = self._getFormData(attrForm,
                                                     bytez[consumed+unitConsumed:],
                                                     addrsize=header.ptrsize,
                                                     is64BitDwarf=is64BitDwarf)
                    struct.vsAddField(name, vsForm)
                    unitConsumed += flen

                cuoffs[startoff] = struct
                startoff = unitConsumed + len(header)
                if parentChain:
                    parentChain[-1].dwarf_children.vsAddElement(struct)
                else:
                    debuginfo.append((struct, cuoffs))

                if hasKids:
                    parentChain.append(struct)
                    struct.vsAddField('dwarf_children', vstruct.VArray())

            consumed += unitConsumed
        return debuginfo

    def _parseDebugLine(self):
        pass

    def _parseDebugAbbrev(self):
        bytez = self.getSectionBytes('.debug_abbrev')
        if bytez is None:
            return
        consumed = offset = 0
        # Compile units are referenced by their offsets in the .debug_info section.
        compileunits = {}
        dies = {}
        while consumed < len(bytez):
            idx, con = leb128ToInt(bytez[consumed:])
            consumed += con
            tag, con = leb128ToInt(bytez[consumed:])
            consumed += con
            hasKids = bytez[consumed]
            consumed += 1

            typeinfo = []
            attr, attrType = 0xff, 0xff
            while True:
                attr, alen = leb128ToInt(bytez[consumed:])
                consumed += alen
                attrType, alen = leb128ToInt(bytez[consumed:])
                consumed += alen

                if attr == 0 and attrType == 0:
                    break
                typeinfo.append((attr, attrType))

            dies[idx] = (tag, hasKids, typeinfo)
            # if the next byte is 0, we're done with this compile unit
            if bytez[consumed] == 0:
                compileunits[offset] = dies
                consumed += 1
                offset = consumed
                dies = {}

        return compileunits


def parseDwarf(vw, pbin, strtab=b''):
    # First parse out type information from the .debug_abbrev section
    return DwarfInfo(vw, pbin, strtab)


def _add_children(vw, parent, offsets, children):
    for indx, child in children:
        if child.tag == DW_TAG_subprogram:
            if not hasattr(child, 'low_pc'):
                continue
            hasAbstract = child.vsHasField('abstract_origin')
            hasInline = child.vsHasField('inline')
            if hasAbstract and child.abstract_origin:
                # So...this highly depends on what type of ref we've got, so we need to
                # plumb not just what type of ref we're looking at, but also the various different
                # offsets (file, compunit, etc) all the way through
                origin = child.abstract_origin
                parent = offsets.get(origin)
                if parent:
                    try:
                        vw.makeName(child.low_pc, parent.name, filelocal=False)
                    except v_exc.DuplicateName:
                        pass
            else:
                try:
                    vw.makeName(child.low_pc, child.name, filelocal=True)
                except v_exc.DuplicateName:
                    # someone else beat us to it. Whatever. Keep chugging
                    pass
        if child.vsHasField('dwarf_children'):
            _add_children(vw, child, offsets, child.dwarf_children)


def addDwarfToWorkspace(vw, dwarf):
    for compunit, offsets in dwarf.info:
        if compunit.vsHasField('dwarf_children'):
            _add_children(vw, compunit, offsets, compunit.dwarf_children)
