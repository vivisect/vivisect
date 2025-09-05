'''
Stuff still to do:
* Support for macros (mostly a v5 thing)
    * I'll worry about this when I can actually find something real that generates it. So far I can't find anything
'''
import logging

import Elf
import envi.bits as e_bits

import vstruct
import vstruct.primitives as v_s_prim

import vstruct.defs.dwarf as v_d_dwarf

logger = logging.getLogger(__name__)


INDIRECT_STRINGS = (
    v_d_dwarf.DW_FORM_strx,
    v_d_dwarf.DW_FORM_strx1,
    v_d_dwarf.DW_FORM_strx2,
    v_d_dwarf.DW_FORM_strx3,
    v_d_dwarf.DW_FORM_strx4,
)

class LineStateMachine:
    '''
    So line information in dwarf is modelled as a state machine with
    1 byte opcodes, a few special opcodes, and (possibly) extensions to such.

    There's a base set of opcode, a couple extensions that are accessed by a 00
    opcode, and the possibly a set of special opcodes that I'm not going to
    currently support for a POC
    '''
    def __init__(self, byts, offset, header, bigend=False):
        '''
        * header
            - Type: Dwarf32UnitLineHeader or Dwarf64UnitLineHeader
            - Desc: Header info for the compile unit we're looking at currently
                    (We need it for grabbing things like file names and the opcode_base)
        '''
        self.header = header
        self.consumed = 0
        self.bigend = bigend
        self.byts = byts[offset:]
        self.offset = offset

        # don't mess with the order here. The indexing matches what the DWARF spec states
        self.funcs = [
            self._op_extended,
            self._op_copy,
            self._op_advance_pc,
            self._op_advance_line,
            self._op_set_file,
            self._op_set_column,
            self._op_negate_stmt,
            self._op_set_basic_block,
            self._op_const_add_pc,
            self._op_fixed_advance_pc,
            self._op_set_prologue_end,
            self._op_set_epilogue_begin,
            self._op_set_isa,
        ]

        self.extended_funcs = [
            None,
            self._op_ext_end_sequence,
            self._op_ext_set_address,
            self._op_ext_define_file,
            self._op_ext_set_discriminator,
        ]

        self.matrix = []

        self._reset_registers()

        self._reg_address = offset

    def _reset_registers(self):
        self._reg_address = 0  # pc
        self._reg_op_index = 0
        self._reg_file = 1  # indicates the index of the file
        self._reg_line = 1
        self._reg_column = 0  # begins at 1
        self._reg_is_stmt = False   # TODO: This is determined by the header actually
        self._reg_basic_block = False
        self._reg_end_sequence = False
        self._reg_prologue_end = False
        self._reg_epilogue_begin = False
        self._reg_isa = 0
        self._reg_discriminator = 0

    def serializeRegisters(self):
        return [
            self._reg_address,
            self._reg_op_index,
            self._reg_file,
            self._reg_line,
            self._reg_column,
            self._reg_is_stmt,
            self._reg_basic_block,
            self._reg_end_sequence,
            self._reg_prologue_end,
            self._reg_epilogue_begin,
            self._reg_isa,
            self._reg_discriminator
        ]

    def _op_special(self, opcode):
        '''
        See pages 116-117 in DWARFv4 standard for the full formulas and procedures here
        '''
        adjusted = opcode - self.header.opcode_base
        adv = adjusted // self.header.line_range

        addr_add = self.header.min_instr_len * ((self._reg_op_index + adv) // self.header.max_ops_per_instr)
        opidx = (self._reg_op_index + adv) % self.header.max_ops_per_instr
        line_add = self.header.line_base + (adjusted % self.header.line_range)

        # NOTE: The address and op_index registers, taken together, form an operation pointer that can reference any individual operation with the instruction stream.
        self._reg_address += addr_add
        self._reg_op_index = opidx
        self._reg_line += line_add

        self.matrix.append(self.serializeRegisters())

        self._reg_discriminator = 0
        self._reg_basic_block = False
        self._reg_prologue_end = False
        self._reg_epilogue_begin = False

    def _op_extended(self):
        oplen, con = v_d_dwarf.leb128ToInt(self.byts[self.consumed:], signed=False)
        self.consumed += con

        opcode = self.byts[self.consumed]
        self.consumed += 1
        # TODO: raise?
        #if opcode > len(self.extended_funcs):
            #pass

        self.extended_funcs[opcode](oplen - 1)

    def _op_copy(self):
        '''
        should be more here
        '''
        self.matrix.append(self.serializeRegisters())
        self._reg_discriminator = 0
        self._reg_basic_block = False
        self._reg_prologue_end = False
        self._reg_epilogue_begin = False

    def _op_advance_pc(self):
        # modified address and op_indx according to the same stuff
        # as a special opcode, except the parameter is unsigned leb128
        # that acts as the operation advance
        adv, con = v_d_dwarf.leb128ToInt(self.byts[self.consumed:])
        self.consumed += con

        addr_add = self.header.min_instr_len * ((self._reg_op_index + adv) // self.header.max_ops_per_instr)
        opidx = (self._reg_op_index + adv) % self.header.max_ops_per_instr

        self._reg_address += addr_add
        self._reg_op_index = opidx

    def _op_advance_line(self):
        adv, con = v_d_dwarf.leb128ToInt(self.byts[self.consumed:], signed=True)
        self.consumed += con
        self._reg_line += adv

    def _op_set_file(self):
        fidx, con = v_d_dwarf.leb128ToInt(self.byts[self.consumed:])
        self.consumed += con
        self._reg_file = fidx

    def _op_set_column(self):
        column, con = v_d_dwarf.leb128ToInt(self.byts[self.consumed:])
        self.consumed += con
        self._reg_column = column

    def _op_negate_stmt(self):
        self._reg_is_stmt = ~self._reg_is_stmt

    def _op_set_basic_block(self):
        self._reg_basic_block = True

    def _op_const_add_pc(self):
        # advances address and op_index by increments corresponding to special
        # opcode 255.
        # TODO: Functionalize this since it's kinda in a couple spots
        adjusted = 255 - self.header.opcode_base
        adv = adjusted // self.header.line_range

        addr_add = self.header.min_instr_len * ((self._reg_op_index + adv) // self.header.max_ops_per_instr)
        opidx = (self._reg_op_index + adv) % self.header.max_ops_per_instr
        self._reg_address += addr_add
        self._reg_op_index = opidx

    def _op_fixed_advance_pc(self):
        addend = e_bits.parsebytes(self.byts[self.consumed:], offset=0, size=2, bigend=self.bigend)
        self._reg_address += addend
        self._reg_op_index = 0

    def _op_set_prologue_end(self):
        self._reg_prologue_end = True

    def _op_set_epilogue_begin(self):
        self._reg_epilogue_begin = True

    def _op_set_isa(self):
        isa, con = v_d_dwarf.leb128ToInt(self.byts[self.consumed:])
        self.consumed += con
        self._reg_isa = isa

    def _op_ext_end_sequence(self, blen):
        self.matrix.append(self.serializeRegisters())
        self._reset_registers()
        self._reg_end_sequence = True

    def _op_ext_set_address(self, blen):
        addr = e_bits.parsebytes(self.byts[self.consumed:], offset=0, size=blen, bigend=self.bigend)
        self.consumed += blen
        self._reg_address = addr

    def _op_ext_define_file(self, blen):
        # TODO: Should this emit some debug info? Or is it *literally* just
        # defining a file?
        # this is deprecated in dwarf V5 btw
        srcfile = v_s_prim.v_str(val=self.byts[self.consumed:])
        srcfile.vsSetLength(len(srcfile) + 1)
        self.consumed += len(srcfile)

        diridx, con = v_d_dwarf.leb128ToInt(self.byts[self.consumed:])
        self.consumed += con

        modtime, con = v_d_dwarf.leb128ToInt(self.byts[self.consumed:])
        self.consumed += con

        filelen, con = v_d_dwarf.leb128ToInt(self.byts[self.consumed:])
        self.consumed += con

    def _op_ext_set_discriminator(self, blen):
        dis, con = v_d_dwarf.leb128ToInt(self.byts[self.consumed:])
        self.consumed += con
        self._reg_discriminator = dis

    def getConsumed(self):
        return self.consumed

    def run(self):
        '''
        Run a set of line program bytes through the state machine.
        Eventually will yield out a bunch of events that should
        go into the even stream
        '''
        opbase = self.header.opcode_base
        # oplen = len(self.funcs)
        while self.consumed < len(self.byts):
            byt = self.byts[self.consumed]
            print('%.8x -- 0x%.8x -- %d' % (self.offset + self.consumed, self._reg_address, self._reg_line))
            self.consumed += 1
            if byt >= opbase:
                yield self._op_special(byt)
                continue

            yield self.funcs[byt]()


class DwarfInfo:
    def __init__(self, vw, pbin, strtab=b''):
        self.vw = vw
        self.pbin = pbin
        self.is64BitDwarf = False

        self.dirs = []
        self.files = []

        self.cuheaders = []
        self.lineheaders = []
        self.linesms = []

        # strab typically only shows up in cygwin binaries
        self.secmap = {}
        self.strtable = strtab
        # cygwin PE binaries can use debug info, but in a special way where the names
        # of the sections are just refs into a different section
        if self.strtable:
            for sec in pbin.getSections():
                # so this is cygwin's shorthand for certain section with long names
                if sec.Name.startswith('/'):
                    indx = int(sec.Name[1:], 10)
                    name = self.strtable[indx:].split(b'\x00', 1)[0]
                    self.secmap[name.decode('utf-8')] = sec
        # TODO: abbrevByIndex seems like a good idea, but who consumes it realistically?
        self.abbrevByIndex, self.abbrevByOffset = self._parseDebugAbbrev()
        self.stroffsets = self._preprocStrOffsets()

        self.info = self._parseDebugInfo()
        self._parseDebugLine()

    def getFormalParam(self, cu, cuidx, param):
        if cu.vsHasField('str_offsets_base'):
            offset = cu.str_offsets_base
        else:
            offset = 0

        utf8 = False
        if cu.vsHasField('use_utf8'):
            utf8 = True

        div = 8 if isinstance(cu, v_d_dwarf.Dwarf64CompileHeader) else 4
        info = {}
        for name, valu in param.vsGetFields():
            if name == 'dwarf_children':
                continue
            typ = param.getFieldDwarfType(name)
            rval = valu.vsGetValue()
            # TODO: parse more type info
            # TODO: DW_AT_location
            if name == 'type':
                info['type'] = rval
            elif name == 'artificial':
                info['artificial'] = rval
            elif name == 'name':
                info['name'] = self._getRealString(typ, valu, offset // div, utf8=utf8)
            elif name == 'line':
                info['line'] = rval
            elif name == 'decl_column':
                info['column'] = rval
            elif name == 'file':
                file = self.files[cuidx][rval]
                filename = file.get('valu')
                info['file'] = filename
                diridx = file.get('diridx')
                if diridx is not None:
                    info['dirn'] = self.dirs[cuidx][diridx]['valu']

        return info

    def getFunctionInfo(self, cu, cuidx, prog):
        if cu.vsHasField('str_offsets_base'):
            offset = cu.str_offsets_base
        else:
            offset = 0

        utf8 = False
        if cu.vsHasField('use_utf8'):
            utf8 = True

        info = {}
        params = []
        div = 8 if isinstance(cu, v_d_dwarf.Dwarf64CompileHeader) else 4
        for name, valu in prog.vsGetFields():
            if name == 'dwarf_children':
                continue
            typ = prog.getFieldDwarfType(name)
            rval = valu.vsGetValue()
            if name == 'name':
                info['name'] = self._getRealString(typ, valu, offset // div, utf8=utf8)
            elif name == 'linkage_name':
                info['link_name'] = self._getRealString(typ, valu, offset // div, utf8=utf8)
            elif name == 'decl_file':
                file = self.files[cuidx][rval]
                filename = file.get('valu')
                info['file'] = filename
                diridx = file.get('diridx')
                if diridx is not None:
                    info['dirn'] = self.dirs[cuidx][diridx]['valu']
            elif name == 'decl_line':
                info['line'] = rval
            elif name == 'decl_column':
                info['column'] = rval
            elif name == 'low_pc':
                info['start'] = rval
            elif name == 'high_pc':
                # usually an offset from low_pc
                info['end'] = rval

        if prog.vsHasField('dwarf_children'):
            for _, child in prog.dwarf_children:
                # Be nice if I could tighten this up into a dictionary or something
                if child.tag == v_d_dwarf.DW_TAG_formal_parameter:
                    param = self.getFormalParam(cu, cuidx, child)
                    if param:
                        params.append(param)
                # DW_AT_type?
            info['params'] = params
        return info

    def getStructureMemberInfo(self, cu, cuidx, member):
        info = {}

        # TOOD: Functionalize this preamble
        if cu.vsHasField('str_offsets_base'):
            offset = cu.str_offsets_base
        else:
            offset = 0

        utf8 = False
        if cu.vsHasField('use_utf8'):
            utf8 = True

        div = 8 if isinstance(cu, v_d_dwarf.Dwarf64CompileHeader) else 4
        for name, valu in member.vsGetFields():
            if name == 'dwarf_children':
                continue
            rval = valu.vsGetValue()
            type = member.getFieldDwarfType(name)
            if name == 'name':
                info['name'] = self._getRealString(type, valu, offset // div, utf8=utf8)
            elif name == 'decl_file':
                file = self.files[cuidx][rval]
                filename = file.get('valu')
                info['file'] = filename
                diridx = file.get('diridx')
                if diridx is not None:
                    info['dirn'] = self.dirs[cuidx][diridx]['valu']
            elif name == 'decl_line':
                info['line'] = rval
            elif name == 'data_member_location':
                info['offset'] = rval
            # TODO: DW_AT_type??

        return info

    def getStructureInfo(self, cu, cuidx, struct):
        info = {}

        if cu.vsHasField('str_offsets_base'):
            offset = cu.str_offsets_base
        else:
            offset = 0

        utf8 = False
        if cu.vsHasField('use_utf8'):
            utf8 = True

        div = 8 if isinstance(cu, v_d_dwarf.Dwarf64CompileHeader) else 4
        for name, valu in struct.vsGetFields():
            if name == 'dwarf_children':
                continue
            rval = valu.vsGetValue()
            type = struct.getFieldDwarfType(name)
            if name == 'name':
                info['name'] = self._getRealString(type, valu, offset // div, utf8=utf8)
            elif name == 'decl_file':
                file = self.files[cuidx][rval]
                filename = file.get('valu')
                info['file'] = filename
                diridx = file.get('diridx')
                if diridx is not None:
                    info['dirn'] = self.dirs[cuidx][diridx]['valu']
            elif name == 'decl_line':
                info['line'] = rval
            elif name == 'byte_size':
                info['size'] = rval

        members = []
        if struct.vsHasField('dwarf_children'):
            for _, child in struct.dwarf_children:
                if child.tag == v_d_dwarf.DW_TAG_member:
                    members.append(self.getStructureMemberInfo(cu, cuidx, child))
        info['members'] = members

        return info

    def addChildrenToWorkspace(self, vw, cu, cuidx, children, pns=None, pfunc=None):
        for indx, child in children:
            if child.tag == v_d_dwarf.DW_TAG_subprogram:
                if child.vsHasField('abstract_origin'):
                    continue
                func = self.getFunctionInfo(cu, cuidx, child)
                vw.addDebugInfo('function', func)
            elif child.tag == v_d_dwarf.DW_TAG_structure_type:
                struct = self.getStructureInfo(cu, cuidx, child)
                if struct:
                    vw.addDebugInfo('struct', struct)
            # elif child.tag == v_d_dwarf.DW_TAG_subroutine_type:
            # elif child.tag == v_d_dwarf.DW_TAG_inlined_subroutine:
            elif child.tag == v_d_dwarf.DW_TAG_namespace:
                if child.vsHasField('dwarf_children'):
                    self.addChildrenToWorkspace(vw, cu, cuidx, child.dwarf_children, pns=child, pfunc=pfunc)
            elif child.tag == v_d_dwarf.DW_TAG_class_type:
                pass

    def addToWorkspace(self, vw):
        for idx, (compunit, offsets) in enumerate(self.info):
            if compunit.vsHasField('dwarf_children'):
                self.addChildrenToWorkspace(vw, compunit, idx, compunit.dwarf_children)

    def getSectionBytes(self, name):
        if isinstance(self.pbin, Elf.Elf):
            return self.pbin.getSectionBytes(name)

        sec = self.secmap.get(name)
        if not sec:
            logger.warning('Could not find bytes for section %s', name)
            return None
        return self.pbin.readAtRva(sec.VirtualAddress, sec.VirtualSize)

    def _getRealString(self, type, valu, offs, utf8=False):
        if type in INDIRECT_STRINGS:
            offset = self._getDebugStrOffset(valu + offs)
            return self._getDebugString(offset, utf8=utf8)

        return valu.vsGetValue()

    def _getDebugStrOffset(self, offset):
        # This really only exists in v5. v4 does it totally different
        if offset >= len(self.stroffsets):
            return None
        return self.stroffsets[offset]

    def _getDebugString(self, offset, utf8=False, line=False):
        bytez = self.getSectionBytes('.debug_str' if not line else '.debug_line_str')
        if bytez is None or offset > len(bytez):
            return None

        byts = bytez[offset:].split(b'\x00', 1)[0]
        if utf8 is True:
            return byts.decode('utf-8')
        if utf8 is False:
            return byts.decode('ascii')
        return byts

    def _getContentStrings(self, entries, formats, utf8=False):
        for _, file_name_info in entries:
            info = {}
            for formatidx, valu in file_name_info:
                rval = valu.vsGetValue()
                fidx = int(formatidx)
                type = formats[fidx][0].vsGetValue()
                form = formats[fidx][1].vsGetValue()
                if type == v_d_dwarf.DW_LNCT_path:
                    if form == v_d_dwarf.DW_FORM_string:
                        # string is already collected in the header, we
                        # can just promote it here
                        s = valu.vsGetValue()
                        info['valu'] = s
                    elif form == v_d_dwarf.DW_FORM_strp:
                        # .debug_str section
                        s = self._getDebugString(rval, utf8=utf8)
                        if s is not None:
                            info['valu'] = s
                    elif form == v_d_dwarf.DW_FORM_line_strp:
                        # .debug_line_str section
                        s = self._getDebugString(rval, utf8=utf8, line=True)
                        if s is not None:
                            info['valu'] = s
                    elif form == v_d_dwarf.DW_FORM_strp_sup:
                        # "supplementary strings section"???
                        # I have no idea where to go for this
                        pass

                elif type == v_d_dwarf.DW_LNCT_directory_index:
                    info['diridx'] = rval
                elif type == v_d_dwarf.DW_LNCT_timestamp:
                    info['timestamp'] = rval
                elif type == v_d_dwarf.DW_LNCT_size:
                    info['size'] = rval
                elif type == v_d_dwarf.DW_LNCT_md5:
                    info['md5'] = rval

            yield info

    def _preprocStrOffsets(self):
        bytez = self.getSectionBytes('.debug_str_offsets')
        if bytez is None:
            return
        if self.is64BitDwarf:
            ctor = v_s_prim.v_uint64
        else:
            ctor = v_s_prim.v_uint32

        retn = []
        consumed = 0
        while consumed < len(bytez):
            valu = ctor(bigend=self.vw.bigend)
            valu.vsParse(bytez[consumed:])
            retn.append(valu.vsGetValue())
            consumed += len(valu)

        return retn

    def _getBlock(self, length, bytez):
        block = v_s_prim.v_bytes(size=length.vsGetValue())
        block.vsParse(bytez)
        return block

    def _getExprLoc(self, bytez):
        # TODO: wut?
        pass

    def _getFormData(self, form, bytez, addrsize, utf8=False):
        '''
        TODO: So for anything marked "constant", we technically have to use "context" to determine if it's
        signed, unsigned, target machine endianness, etc. as per the dwarf docs

        Returns a tuple of (attribute name, vstruct data, how many bytes were consumed)
        '''
        extra = 0
        # TODO: is the bigend here right?
        if form == v_d_dwarf.DW_FORM_addr:
            # So this is technically supposed to come from the compilation header in the info section,
            # but for now we're going to cheat and just use the info we grabbed from the elf header itself
            if addrsize == 8:
                vsData = v_s_prim.v_ptr64(bigend=self.vw.bigend)
            else:
                vsData = v_s_prim.v_ptr32(bigend=self.vw.bigend)
            vsData.vsParse(bytez)

        elif form == v_d_dwarf.DW_FORM_block:  # special block
            # TODO
            blocklen, extra = v_d_dwarf.leb128ToInt(bytez)
            vsData = v_s_prim.v_bytes(size=blocklen)
            vsData.vsParse(bytez, extra)

        elif form == v_d_dwarf.DW_FORM_block1:  # block
            blocklen = v_s_prim.v_uint8(bigend=self.vw.bigend)
            blocklen.vsParse(bytez)
            vsData = self._getBlock(blocklen, bytez[len(blocklen):])
            extra = blocklen

        elif form == v_d_dwarf.DW_FORM_block2:  # block
            blocklen = v_s_prim.v_uint16(bigend=self.vw.bigend)
            blocklen.vsParse(bytez)
            vsData = self._getBlock(blocklen, bytez[len(blocklen):])
            extra = blocklen

        elif form == v_d_dwarf.DW_FORM_block4:  # block
            blocklen = v_s_prim.v_uint32(bigend=self.vw.bigend)
            blocklen.vsParse(bytez)
            vsData = self._getBlock(blocklen, bytez[len(blocklen):])
            extra = blocklen

        elif form == v_d_dwarf.DW_FORM_data1:  # constant
            vsData = v_s_prim.v_uint8(bigend=self.vw.bigend)
            vsData.vsParse(bytez)

        elif form == v_d_dwarf.DW_FORM_data2:  # constant
            vsData = v_s_prim.v_uint16(bigend=self.vw.bigend)
            vsData.vsParse(bytez)

        elif form == v_d_dwarf.DW_FORM_data4:  # constant
            vsData = v_s_prim.v_uint32(bigend=self.vw.bigend)
            vsData.vsParse(bytez)

        elif form == v_d_dwarf.DW_FORM_data8:  # constant
            vsData = v_s_prim.v_uint64(bigend=self.vw.bigend)
            vsData.vsParse(bytez)

        elif form == v_d_dwarf.DW_FORM_string:  # string
            # Directly in the .debug_info section
            vsData = v_s_prim.v_str(size=bytez.index(b'\x00'))
            vsData.vsParse(bytez)
            # Don't forget about skipping the null terminator
            extra = 1

        elif form == v_d_dwarf.DW_FORM_flag:  # flag
            vsData = v_s_prim.v_uint8(bigend=self.vw.bigend)
            vsData.vsParse(bytez)

        elif form == v_d_dwarf.DW_FORM_strp:  # string
            # a ptr-sized offset into the string table .debug_str
            if self.is64BitDwarf:
                offset = v_s_prim.v_int64(bigend=self.vw.bigend)
                offset.vsParse(bytez)
            else:
                offset = v_s_prim.v_int32(bigend=self.vw.bigend)
                offset.vsParse(bytez)

            strp = self._getDebugString(offset.vsGetValue(), utf8=None)
            vsData = v_s_prim.v_str(len(strp), val=strp)

            # strp is special since it's an easy reference into a table
            return vsData, len(offset)

        elif form == v_d_dwarf.DW_FORM_line_strp:  # string
            # a ptr-sized offset into the string table .debug_line_str section
            if self.is64BitDwarf:
                offset = v_s_prim.v_int64(bigend=self.vw.bigend)
                offset.vsParse(bytez)
            else:
                offset = v_s_prim.v_int32(bigend=self.vw.bigend)
                offset.vsParse(bytez)

            strp = self._getDebugString(offset.vsGetValue(), utf8=None, line=True)
            vsData = v_s_prim.v_str(len(strp), val=strp)

            # strp is special since it's an easy reference into a table
            return vsData, len(offset)

        elif form == v_d_dwarf.DW_FORM_sdata:  # constant
            bits = self.vw.psize * 8
            slen, extra = v_d_dwarf.leb128ToInt(bytez, bitlen=bits, signed=True)
            slen = e_bits.signed(slen, extra)
            if bits == 64:
                return v_s_prim.v_int64(slen), extra
            return v_s_prim.v_int32(slen), extra

        elif form == v_d_dwarf.DW_FORM_udata:  # constant
            bits = self.vw.psize * 8
            ulen, extra = v_d_dwarf.leb128ToInt(bytez, bitlen=bits)
            if bits == 64:
                return v_s_prim.v_uint64(ulen), extra
            return v_s_prim.v_uint32(ulen), extra

        elif form == v_d_dwarf.DW_FORM_ref_addr:  # ref
            if self.is64BitDwarf:
                vsData = v_s_prim.v_ptr64(bigend=self.vw.bigend)
            else:
                vsData = v_s_prim.v_ptr32(bigend=self.vw.bigend)
            vsData.vsParse(bytez)

        elif form == v_d_dwarf.DW_FORM_ref1:  # ref
            vsData = v_s_prim.v_uint8(bigend=self.vw.bigend)
            vsData.vsParse(bytez)

        elif form == v_d_dwarf.DW_FORM_ref2:  # ref
            vsData = v_s_prim.v_uint16(bigend=self.vw.bigend)
            vsData.vsParse(bytez)

        elif form == v_d_dwarf.DW_FORM_ref4:  # ref
            vsData = v_s_prim.v_uint32(bigend=self.vw.bigend)
            vsData.vsParse(bytez)

        elif form == v_d_dwarf.DW_FORM_ref8:  # ref
            vsData = v_s_prim.v_uint64(bigend=self.vw.bigend)
            vsData.vsParse(bytez)

        elif form == v_d_dwarf.DW_FORM_ref_udata:  # ref
            # refers to something within the .debug_info section
            # variable length offset
            reflen, extra = v_d_dwarf.leb128ToInt(bytez)
            vsData = v_s_prim.v_uint64(value=reflen, bigend=self.vw.bigend)
            return vsData, extra

        elif form == v_d_dwarf.DW_FORM_indirect:  # SPECIAL
            # TODO: Is this right?
            valu, extra = v_d_dwarf.leb128ToInt(bytez)
            vsData = v_s_prim.v_uint64(value=valu, bigend=self.vw.bigend)
            return vsData, extra

        elif form == v_d_dwarf.DW_FORM_sec_offset:  # lineptr, loclistptr, macptr, rangelistptr
            if self.is64BitDwarf:
                vsData = v_s_prim.v_int64(bigend=self.vw.bigend)
                vsData.vsParse(bytez)
            else:
                vsData = v_s_prim.v_int32(bigend=self.vw.bigend)
                vsData.vsParse(bytez)
            # raise Exception("IMPLEMENT ME!")
            # TODO: so where the offset is depends on what subtype the sec_offset is, but that's determined
            # by the attr name, and honestly, right now, I don't care about that

        elif form == v_d_dwarf.DW_FORM_exprloc:  # exprloc
            loclen, extra = v_d_dwarf.leb128ToInt(bytez)
            vsData = v_s_prim.v_bytes(loclen)
            vsData.vsParse(bytez[extra:])
            # self._getExprLoc(vsData)

        elif form == v_d_dwarf.DW_FORM_flag_present:  # flag
            # Don't actually consume any bytes, but do indicate the flag is there
            vsData = v_s_prim.v_uint8(value=1)
            return vsData, 0

        elif form == v_d_dwarf.DW_FORM_ref_sig8:  # reference
            vsData = v_s_prim.v_int64(bigend=self.vw.bigend)
            vsData.vsParse(bytez)

        elif form == v_d_dwarf.DW_FORM_rnglistx:
            vsData = v_d_dwarf.v_uleb()
            vsData.vsParse(bytez)

        # these are all indexes into the .debug_str_offsets section. All of
        # those are DW_FORM_strp
        elif form == v_d_dwarf.DW_FORM_strx:
            vsData = v_d_dwarf.v_uleb()
            vsData.vsParse(bytez)
        elif form == v_d_dwarf.DW_FORM_strx1:
            vsData = v_s_prim.v_uint8()
            vsData.vsParse(bytez)
        elif form == v_d_dwarf.DW_FORM_strx2:
            vsData = v_s_prim.v_uint16()
            vsData.vsParse(bytez)
        elif form == v_d_dwarf.DW_FORM_strx3:
            vsData = v_s_prim.v_uint24()
            vsData.vsParse(bytez)
        elif form == v_d_dwarf.DW_FORM_strx4:
            vsData = v_s_prim.v_uint32()
            vsData.vsParse(bytez)

        # similar to above, these are parsed the same but are indexes into the
        # .debug_addr section
        elif form == v_d_dwarf.DW_FORM_addrx:
            vsData = v_d_dwarf.v_uleb()
            vsData.vsParse(bytez)
        elif form == v_d_dwarf.DW_FORM_addrx1:
            vsData = v_s_prim.v_uint8()
            vsData.vsParse(bytez)
        elif form == v_d_dwarf.DW_FORM_addrx2:
            vsData = v_s_prim.v_uint16()
            vsData.vsParse(bytez)
        elif form == v_d_dwarf.DW_FORM_addrx3:
            vsData = v_s_prim.v_uint24()
            vsData.vsParse(bytez)
        elif form == v_d_dwarf.DW_FORM_addrx4:
            vsData = v_s_prim.v_uint32()
            vsData.vsParse(bytez)

        else:
            # TODO: loosen this up?
            raise Exception('Unrecognized debug form 0x%.4x' % form)

        return vsData, len(vsData) + extra

    def _parseDebugInfo(self):
        '''
        Parse out the main body of debug info. This sets a couple useful properties
        '''
        # Use that to parse out things from the .debug_info section
        vw = self.vw
        debuginfo = []
        bytez = self.getSectionBytes('.debug_info')
        if bytez is None:
            return

        consumed = 0

        version = v_s_prim.v_uint32(bigend=vw.bigend)
        if version == 0xFFFFFFFF:
            consumed += 4
            headerctor = v_d_dwarf.Dwarf64CompileHeader
        else:
            headerctor = v_d_dwarf.Dwarf32CompileHeader
            # So it says it's 12 bytes, but the first 4 are ffffffff
        while consumed < len(bytez):
            # Parse the compile unit header
            # we can have 32 bit dwarf in a 64 bit binary and the way they dynamic repr that
            # is by all the 64 bit addresses being 12 bytes long, but the first 4 are 0xffffffff

            header = headerctor()
            # TODO: there's a unit type header for like TYPE structures that we need to handle
            header.vsParse(bytez[consumed:])
            self.cuheaders.append(header)
            cuoffs = {}

            utf8 = False
            if header.vsHasField('use_utf8'):
                utf8 = True

            # so the header in 64 bit is weird, since the first 4 are going to all f's for the length field
            consumed += len(header)
            toConsume = len(header) + header.vsGetField('length')
            unitConsumed = 0
            startoff = len(header)
            parentChain = []
            # Need to grab the compile headers attributes and promote those for things like use_utf8
            # Or just parse out the first header block?

            while len(header) + unitConsumed < toConsume:
                idx, ulen = v_d_dwarf.leb128ToInt(bytez[consumed + unitConsumed:])
                unitConsumed += ulen
                if idx == 0:
                    startoff += 1
                    if parentChain:
                        parentChain.pop()
                        if not parentChain:
                            break
                    continue

                tag, hasKids, typeinfo = self.abbrevByOffset[header.abbrev_offset][idx]
                # Need to actually do something with struct
                child = v_d_dwarf.DwarfTypedStruct()
                child.vsAddField('tag', v_s_prim.v_uint16(tag))
                for info in typeinfo:
                    attr = info['name']
                    form = info['form']
                    extra = info['extra']
                    if v_d_dwarf.DW_AT_lo_user < attr < v_d_dwarf.DW_AT_hi_user:
                        # try reaching into the gnu attribute names since they're a well known
                        # "vendor"
                        name = v_d_dwarf.gnu_attribute_names.get(attr, "UNK")
                    else:
                        name = v_d_dwarf.dwarf_attribute_names.get(attr, "UNK")

                    # implict const you use the value from the abbrev section and nothing is stored here
                    # but the value is a signed LEB128 number that we've already fetched
                    # technically we shouldn't be storing this here because a LEB128 number can be arbitrarily large
                    # so....yea. Need a way around that.
                    if extra == v_d_dwarf.DW_FORM_implicit_const:
                        vsForm = v_s_prim.v_int64(value=form)
                        flen = 0
                    else:
                        vsForm, flen = self._getFormData(form,
                                                         bytez[consumed+unitConsumed:],
                                                         addrsize=header.ptrsize,
                                                         utf8=utf8)
                    child.addField(name, vsForm, type=form)
                    unitConsumed += flen

                cuoffs[startoff] = child
                startoff = unitConsumed + len(header)
                if parentChain:
                    parentChain[-1].dwarf_children.vsAddElement(child)
                else:
                    debuginfo.append((child, cuoffs))

                if hasKids:
                    parentChain.append(child)
                    child.vsAddField('dwarf_children', vstruct.VArray())

            consumed += unitConsumed

        return debuginfo

    def _parseDebugLine(self):
        vw = self.vw
        consumed = 0
        byts = self.getSectionBytes('.debug_line')

        # TODO: By this point we should have already snagged the compile
        # unit info, because there are as much Line Program headers/sections
        # as there are compile units (and parsing needs to reflect that

        version = v_s_prim.v_uint32(bigend=vw.bigend)
        if version == 0xFFFFFFFF:
            consumed += 4
            headerctor = v_d_dwarf.Dwarf64UnitLineHeader
            ulen = 8
        else:
            headerctor = v_d_dwarf.Dwarf32UnitLineHeader
            ulen = 4

        for idx, (cu, offsets) in enumerate(self.info):
            dirs = []
            files = []
            headerstart = consumed
            header = headerctor(self, bigend=vw.bigend)
            header.vsParse(byts[consumed:], offset=0)
            self.lineheaders.append(header)
            consumed += len(header)

            utf8 = False
            if cu.vsHasField('use_utf8'):
                utf8 = True

            if header.version == 4:
                # TODO: actually test with v4 again
                dirs.append(None)
                while byts[consumed] != 0:
                    dirn = v_s_prim.v_str(val=byts[consumed:])
                    dirs.append({
                        'valu': dirn.vsGetValue()
                    })
                    dirn.vsSetLength(len(dirn.vsGetValue()) + 1)
                    consumed += len(dirn)
                # TODO: I think this is one based for indexing
                self.dirs.append(dirs)

                # skip over terminator byte
                consumed += 1

                files.append(None)
                while byts[consumed] != 0:
                    srcpath = v_s_prim.v_str(val=byts[consumed:])
                    srcpath.vsSetLength(len(srcpath.vsGetValue()) + 1)
                    consumed += len(srcpath)

                    diridx, con = v_d_dwarf.leb128ToInt(byts[consumed:])
                    consumed += con

                    modtime, con = v_d_dwarf.leb128ToInt(byts[consumed:])
                    consumed += con

                    filelen, con = v_d_dwarf.leb128ToInt(byts[consumed:])
                    consumed += con

                    files.append({
                        'valu': srcpath,
                        'diridx': diridx,
                        'modified': modtime,
                        'size': filelen
                    })
                self.files.append(files)

                # skip over terminator byte
                consumed += 1
            elif header.version == 5:
                # TODO: We're sorta reparsing this? Would be nice to collapse all
                # this with the vstruct def. But that means handing the Dwarf obj
                # down into the vstruct parse, which isn't a line I'm quite ready
                # to cross
                for info in self._getContentStrings(header.directories,
                                                    header.directory_entry_format,
                                                    utf8=utf8):
                    dirs.append(info)
                self.dirs.append(dirs)

                for info in self._getContentStrings(header.file_names,
                                                    header.file_names_entry_formats,
                                                    utf8=utf8):
                    files.append(info)
                self.files.append(files)
            # directly following the header is the byts of the line program.

            self.linesms.append(LineStateMachine(byts, consumed, header, bigend=vw.bigend))
            consumed = headerstart + header.unit_length + ulen

    def _parseDebugAbbrev(self):
        bytez = self.getSectionBytes('.debug_abbrev')
        if bytez is None:
            return

        consumed = 0
        retnIdx = {}
        retnOff = {}
        # Compile units are referenced by their offsets in the .debug_info section.
        # but abbrevs are also reference by an index number, so....we have to track
        # this in two ways :(
        dies = {}
        # we have to track index ourselves because it can reset between compile units
        idx = 0
        offset = consumed
        while consumed < len(bytez):
            idx += 1
            code, con = v_d_dwarf.leb128ToInt(bytez[consumed:])
            consumed += con
            tag, con = v_d_dwarf.leb128ToInt(bytez[consumed:])
            consumed += con
            hasKids = bytez[consumed]
            consumed += 1

            typeinfo = []
            attr, attrType = 0xff, 0xff
            while True:
                implicit = False
                # name
                attr, alen = v_d_dwarf.leb128ToInt(bytez[consumed:])
                consumed += alen

                # form
                attrType, alen = v_d_dwarf.leb128ToInt(bytez[consumed:])
                consumed += alen

                extra = None
                # should only show up in v5?
                if attrType == v_d_dwarf.DW_FORM_implicit_const:
                    # we need to consume another byte
                    implicit, alen = v_d_dwarf.leb128ToInt(bytez[consumed:], signed=True)
                    consumed += alen

                    extra = attrType
                    attrType = implicit

                if attr == 0 and attrType == 0:
                    break

                # typeinfo.append((attr, attrType))
                # attrType should be something of DW_FORM_*
                # attr should be something of DW_AT_*
                typeinfo.append({'name': attr, 'form': attrType, 'extra': extra})

            retnIdx[idx] = dies[code] = (tag, hasKids, typeinfo)
            # diesByOff[offset] = (tag, hasKids, typeinfo)
            # if the next byte is 0, we're done with this compile unit
            if bytez[consumed] == 0:
                consumed += 1
                idx += 1

                dies[idx] = None
                retnOff[offset] = dies
                offset = consumed
                dies = {}

        return retnIdx, retnOff


def parseDwarf(vw, pbin, strtab=b''):
    # First parse out type information from the .debug_abbrev section
    return DwarfInfo(vw, pbin, strtab)


def addDwarfToWorkspace(vw, dwarf):
    try:
        dwarf.addToWorkspace(vw)
    except Exception as e:
        import traceback
        logger.warning("DWARF parsing ran into bug: %s", e)
        traceback.print_exc()
