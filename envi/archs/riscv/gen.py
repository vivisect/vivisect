import re
import enum
import os.path
import argparse
import itertools
import subprocess
from collections import namedtuple


_immfields = [
    r'imm\[[^]]+\]',
    r'imm',
    r'offset',
    r'jump target',
]

# The RVC instructions add lots of variation to the possible register fields
_regfields = [
    r'rs[0-9]?',
    r'rd',
    r'rd/rs[0-9]?',
    r'\\rs(?:one|two)prime',
    r'\\rdprime',
    r'\\rs(?:one|two)prime/\\rdprime',
    r'\\rdprime/\\rs(?:one|two)prime',
]

# All fields are allowed to have binary constants in them, but the funct and
# opcode fields must have constants in them.
_reqbinfields = [
    r'funct[0-9]',
    r'opcode',
    r'op',
    # Special constant/operand flags used by the FENCE instruction
    r'fm',
    # Special constant/operand flags used by the Atomic instructions
    r'aq',
    r'rl',
]

_binvalues = [
    r'[01]+',
]

# Some RVC instructions use decimal constants instead of binary
_decvalues = [
    r'[0-9]+',
]

_binfields = _regfields + _immfields

# The RVC instructions have more specific imm information than the form
_immvalues = _immfields + [
    r'shamt\[[^]]+\]',
    r'shamt',
    # Special IMM names used by the FENCE instruction
    r'pred',
    r'succ',
    r'uimm',
    r'uimm\[[^]]+\]',
    r'nzimm\[[^]]+\]',
    r'nzuimm\[[^]]+\]',
    # Atomic operation register fields (yes it's here in the IMM values on
    # purpose)
    r'csr',
]
_regvalues = _regfields + [
    r'rs[0-9]?/rd\$\\n?eq\$0',
    r'rs[0-9]?\$\\n?eq\$0',
    r'rs[0-9]?\$\\n?eq\$\$\\{[0-9,]+\\}\$',
    r'rd\$\\n?eq\$0',
    r'rd\$\\n?eq\$\$\\{[0-9,]+\\}\$',
    r'rs[0-9]?/rd\$\\n?eq\$0',
    r'rs[0-9]?/rd\$\\n?eq\$\$\\{[0-9,]+\\}\$',
]

# the required bin field may also have a value of 'rm' (rounding mode)
_reqbinvalues = _reqbinfields + _binvalues + _decvalues + [
    r'rm',
]


def _makepat(parts, options=0):
    if options & re.MULTILINE:
        return re.compile(r'(?:' + r')|(?:'.join(parts) + r')', options)
    else:
        return re.compile(r'(?:^' + r'$)|(?:^'.join(parts) + r'$)', options)


_immfieldpat = _makepat(_immfields)
_regfieldpat = _makepat(_regfields)
_reqbinfieldpat = _makepat(_reqbinfields)
_binfieldpat = _makepat(_binfields)
_immvaluepat = _makepat(_immvalues)
_regvaluepat = _makepat(_regvalues)

# Some instructions encode an IMM value (uimm) in register fields, so when
# checking for a form match we need a special pattern that is the register
# patterns + 'uimm'
_regvalueformmatchpat = _makepat(_regvalues + [r'uimm'])

_binvaluepat = _makepat(_binvalues)
_decvaluepat = _makepat(_decvalues)
_reqbinvaluepat = _makepat(_reqbinvalues)


class OpcodeType(enum.Enum):
    OPCODE = enum.auto()
    REG = enum.auto()
    CONST = enum.auto()
    IMM = enum.auto()
    RM = enum.auto()
    MEM = enum.auto()
    MEM_SP = enum.auto()
    C_OPCODE = enum.auto()
    C_REG = enum.auto()
    CSR_REG = enum.auto()


Form = namedtuple('Form', [
    'name',
    'fields',
])

Field = namedtuple('Field', [
    'value',  # "name" or integer constant
    'type',
    'columns',
    'bits',
    'mask',
    'shift',
])

Op = namedtuple('Op', [
    'name',
    'cat',
    'form',
    'mask',
    'value',
    'fields',
    'flags',
    'notes',
])


def get_instr_mask(fields):
    mask = '0b'
    value = '0b'
    for field in fields:
        if field.type in (OpcodeType.CONST, OpcodeType.OPCODE, OpcodeType.C_OPCODE):
            mask += '1' * field.bits
            if isinstance(field.value, int):
                value += bin(field.value)[2:]
            elif isinstance(field.value, str) and _binvaluepat.match(field.value):
                value += field.value
            elif isinstance(field.value, str) and _decvaluepat.match(field.value):
                # Convert the decimal value string to an integer first
                value += bin(int(field.value))[2:]
            else:
                raise Exception('Cannot create mask with non-integer field: %s' % str(field))

        else:
            mask += '0' * field.bits
            value += '0' * field.bits

    return (int(mask, 2), int(value, 2))


def get_field_type(field):
    if _immvaluepat.match(field):
        # The CSR instructions place the CSR register field in the I-Type IMM
        # field
        if 'csr' in field:
            return OpcodeType.CSR_REG
        else:
            return OpcodeType.IMM
    elif _regvaluepat.match(field):
        if 'prime' in field:
            return OpcodeType.C_REG
        else:
            return OpcodeType.REG
    elif _reqbinvaluepat.match(field):
        if 'opcode' == field:
            return OpcodeType.OPCODE
        elif 'op' == field:
            return OpcodeType.C_OPCODE
        elif 'rm' == field:
            return OpcodeType.RM
        else:
            return OpcodeType.CONST
    #elif _decvaluepat.match(field):
    #    return OpcodeType.CONST
    else:
        raise Exception('Unknown field type: %s' % str(field))


def get_field_info(instr_fields, columns):
    # Determine the field bit widths and field types
    col = 0
    fields = []
    for size, value in instr_fields:
        if isinstance(columns[col], tuple):
            start = columns[col][0]
        else:
            start = columns[col]

        col += int(size)

        # Now get the start of the next field
        if col < len(columns):
            if isinstance(columns[col], tuple):
                end = columns[col][0]
            else:
                end = columns[col]
        else:
            # If the previous column was the last field then end is -1 to keep
            # up the pattern of the end being exclusive (the start of the next
            # column)
            end = -1

        # Start is inclusive but end is not
        field_bits = start - end

        # Because end is the start of the next column beyond the current field
        # add 1 to end to get the correct shift value for this field
        field_shift = end + 1

        # Determine the type of this field by pattern
        field_type = get_field_type(value)

        # Generate the mask and shift that could be used to extract this field
        # from an instruction
        #field_mask = int('0b' + '1' * field_bits, 2)
        field_mask = (2 ** field_bits) - 1
        fields.append(Field(value, field_type, int(size), field_bits, field_mask, field_shift))

    return fields


def find_form(fields, forms):
    # Special cases, some instructions split single imm fields up into multiple
    # smaller fields.
    #
    # The FENCE instruction with 'fm', 'pred', succ' are actually 3 subfields.
    # There are other instruction names that represent specific FENCE
    # instructions and those also need the same treatment.  Specifically
    # FENCE.TSO ('1000', '0011', '0011') and PAUSE ('0000', '0001', '0000')
    #
    # Some CB form RVC instructions split the rdprime/rsoneprime field into two
    # fields, one that is imm[5] or nzuimm[5] (1 bit) and a 2-bit constant.
    # Combine them into 1 "field" to make it easier to match.
    field_names = [f[1] for f in fields]
    if field_names[:3] == ['fm', 'pred', 'succ'] or \
            field_names[:3] == ['1000', '0011', '0011'] or \
            field_names[:3] == ['0000', '0001', '0000']:
        fields = [fields[:3]] + fields[3:]
    elif field_names[1:3] == ['aq', 'rl']:
        fields = [fields[:3]] + fields[3:]
    elif field_names[1] == 'shamt':
        fields = [fields[:2]] + fields[2:]
    elif field_names[1] in ('imm[5]', 'nzuimm[5]') and \
            len(field_names[2]) == 2 and \
            _binvaluepat.match(field_names[2]):
        fields = fields[:1] + [fields[1:3]] + fields[3:]

    for form_name, form in forms.items():
        #print('trying %s (%d =? %d)' % (form_name, len(fields), len(form.fields)))

        if len(fields) == len(form.fields):
            parsed = []
            for value, field in zip(fields, form.fields):
                if not isinstance(value, list):
                    # If the column width doesn't match, this doesn't work. Just
                    # checking column widths at the moment
                    if value[0] != field.columns:
                        #print('%s WIDTH MISMATCH %s' % (value, field))
                        match = False
                        break

                    # if required bin fields aren't binary constants, this form
                    # doesn't match.
                    if _reqbinfieldpat.match(field.value):
                        if _reqbinvaluepat.match(value[1]):
                            #print('%s matched %s' % (value, field))
                            if _binvaluepat.match(value[1]):
                                parsed.append((value[0], int(value[1], 2)))
                            else:
                                parsed.append((value[0], value[1]))
                        else:
                            #print('%s REQ FIELD MISMATCH %s' % (value, field))
                            match = False
                            break
                    else:
                        # The imm field matches get a little weird because the
                        # RVC instructions and forms aren't super consistent.
                        # If the field doesn't start with 'imm' then the two
                        # don't have to match.
                        #
                        # The RVC register fields get a little complicated, also
                        # ensure that both the value and field strings have
                        # 'prime' in them or they both don't.
                        if _binvaluepat.match(value[1]) and _binfieldpat.match(field.value):
                            #print('bin %s matched %s' % (value, field))
                            parsed.append((value[0], int(value[1], 2)))
                        elif _decvaluepat.match(value[1]) and _binfieldpat.match(field.value):
                            #print('dec %s matched %s' % (value, field))
                            parsed.append((value[0], int(value[1], 10)))
                        elif _immvaluepat.match(value[1]) and _immfieldpat.match(field.value) and \
                                ((_immfieldpat.match(value[1]) and value[1] == field.value) or \
                                not _immfieldpat.match(value[1]) or \
                                not field.value.startswith('imm') or \
                                (value[1].startswith('imm') and field.value == 'imm')):
                            #print('imm %s matched %s' % (value, field))
                            parsed.append(value)
                        elif _regvalueformmatchpat.match(value[1]) and _regfieldpat.match(field.value) and \
                                ((_regfieldpat.match(value[1]) and value[1] in field.value) or \
                                    not _regfieldpat.match(value[1]) or \
                                    ('prime' in value[1] and 'prime' in field.value)) and \
                                (('prime' in value[1] and 'prime' in field.value) or \
                                    ('prime' not in value[1] and 'prime' not in field.value)):
                            #print('reg %s matched %s' % (value, field))
                            parsed.append(value)

                        else:
                            #print('%s NO MATCH %s' % (value, field))
                            match = False
                            break
                else:
                    # Get the total columns that make up this aggregate field
                    col_width = sum([v[0] for v in value])

                    # Lists only match bin fields
                    if _binvaluepat.match(value[0][1]) and _reqbinfieldpat.match(field.value) and \
                            col_width == field.columns:
                        #print('%s matched %s' % (value, field))
                        parsed.extend([(value[0][0], int(value[0][1], 2))] + value[1:])
                    elif isinstance(value[0][1], str) and _binfieldpat.match(field.value) and \
                            col_width == field.columns:
                        #print('%s matched %s' % (value, field))
                        parsed.extend(value)
                    else:
                        #print('%s NO MATCH %s' % (value, field))
                        match = False
                        break
            else:
                # Find the bit width of the fields
                return form_name, parsed

    # If no form was found, and there are multiple fields in a row that are
    # binary, try collapsing them together.  The RVC instruction table gets
    # weird with how instructions are laid out sometimes.
    #
    # Try first without collapsing the first field
    idx_start = None
    idx_stop = None
    for i in range(1, len(fields)):
        if _binvaluepat.match(fields[i][1]):
            if idx_start is None:
                idx_start = i
        elif idx_start is not None:
            idx_stop = i
            break

    if idx_start is not None and idx_stop is not None and idx_stop - idx_start > 1:
        # Construct the new instruction field
        new_field = (sum(int(f[0]) for f in fields[idx_start:idx_stop]), \
                ''.join(f[1] for f in fields[idx_start:idx_stop]))
        collapsed_fields = fields[:idx_start] + [new_field] + fields[idx_stop:]
        return find_form(collapsed_fields, forms)

    # Try again but start from field 0 this time
    idx_start = None
    idx_stop = None
    for i in range(0, len(fields)):
        if _binvaluepat.match(fields[i][1]):
            if idx_start is None:
                idx_start = i
        elif idx_start is not None:
            idx_stop = i
            break

    if idx_start is not None and idx_stop is not None and idx_stop - idx_start > 1:
        # Construct the new instruction field
        new_field = (sum(int(f[0]) for f in fields[idx_start:idx_stop]), \
                ''.join(f[1] for f in fields[idx_start:idx_stop]))
        collapsed_fields = fields[:idx_start] + [new_field] + fields[idx_stop:]
        return find_form(collapsed_fields, forms)
    else:
        # This special case doesn't apply, signal a failure
        raise Exception('no form match found for %s' % str(fields))


def add_instr(instrs, name, cat_list, form, fields, notes, priv=False, flags=None):
    # the opcode is the last field, ensure it is a constant
    assert fields[-1].type == OpcodeType.CONST

    # If there is a note that is just 'HINT' that indicates this is a weird
    # instruction like C.SLLI64 that is only a hint but not defined as a real
    # instruction?  If so, just skip it.
    if 'HINT' in notes:
        print('Skipping HINT-ONLY instruction %s' % name)
        return

    if flags is None:
        flags = []

    # Special cases:
    # 1. For FENCE instructions the FM field should generate normal
    #    FENCE (fm = 0) and FENCE.TSO (fm = 1) instructions
    # 2. For Atomic instructions 4 should be generated:
    #    INSTR (aq = 0, rl = 0)
    #    INSTR.aq (aq = 1, rl = 0)
    #    INSTR.rl (aq = 0, rl = 1)
    #    INSTR.aq.rl (aq = 1, rl = 1) (
    if any(f.value == 'fm' for f in fields):
        # For some reason there already is a FENCE.TSO instruction in the
        # scraped tables, so just modify FM to be fixed as 0 for the normal
        # FENCE instruction
        fm_field = next(f for f in fields if f.value == 'fm')
        fm_zero_field = Field(0, fm_field.type, fm_field.columns, fm_field.bits, fm_field.bits, fm_field.shift)

        # Now let the rest of this function run for FENCE
        fields = [f if f.value != 'fm' else fm_zero_field for f in fields]

    elif any(f.value == 'aq' for f in fields):
        aq_field = next(f for f in fields if f.value == 'aq')
        aq_zero_field = Field(0, aq_field.type, aq_field.columns, aq_field.bits, aq_field.bits, aq_field.shift)
        aq_one_field = Field(1, aq_field.type, aq_field.columns, aq_field.bits, aq_field.bits, aq_field.shift)

        rl_field = next(f for f in fields if f.value == 'rl')
        rl_zero_field = Field(0, rl_field.type, rl_field.columns, rl_field.bits, rl_field.bits, rl_field.shift)
        rl_one_field = Field(1, rl_field.type, rl_field.columns, rl_field.bits, rl_field.bits, rl_field.shift)

        aq_fields = [f if f.value not in ('aq', 'rl') else aq_one_field if f.value == 'aq' else rl_zero_field for f in fields]
        rl_fields = [f if f.value not in ('aq', 'rl') else aq_zero_field if f.value == 'aq' else rl_one_field for f in fields]
        both_fields = [f if f.value not in ('aq', 'rl') else aq_one_field if f.value == 'aq' else rl_one_field for f in fields]

        # Create the .aq, and .rl instructions
        if name.startswith('LR.') or name.startswith('SC.'):
            # If this is an LR.? or SC.? instruction don't modify the
            # instruction name
            add_instr(instrs, name, cat_list, form, aq_fields, notes, priv,
                      flags=flags+['RISCV_IF.AQ'])
            add_instr(instrs, name, cat_list, form, rl_fields, notes, priv,
                      flags=flags+['RISCV_IF.RL'])
            add_instr(instrs, name, cat_list, form, both_fields, notes, priv,
                      flags=flags+['RISCV_IF.AQ', 'RISCV_IF.RL'])

        else:
            add_instr(instrs, name+'.AQ', cat_list, form, aq_fields, notes, priv,
                      flags=flags+['RISCV_IF.AQ'])
            add_instr(instrs, name+'.RL', cat_list, form, rl_fields, notes, priv,
                      flags=flags+['RISCV_IF.RL'])
            add_instr(instrs, name+'.AQ.RL', cat_list, form, both_fields, notes, priv,
                      flags=flags+['RISCV_IF.AQ', 'RISCV_IF.RL'])

        # Now create the non-acquire or release instruction
        fields = [f if f.value not in ('aq', 'rl') else aq_zero_field if f.value == 'aq' else rl_zero_field for f in fields]

    # Get the combined mask and post-mask value for this instruction based on
    # the unmodified set of fields
    op_mask, op_value = get_instr_mask(fields)

    # And generate the flags for this instruction
    op_flags = get_instr_flags(name, fields, priv) + flags

    if not cat_list:
        raise Exception('ERROR: no categories defined for: %s, %s, %s, %s, priv=%s' % (name, form, fields, notes, priv))

    for cat in cat_list:
        if cat not in instrs:
            instrs[cat] = {}
        if name not in instrs[cat]:
            # Allow for multiple instruction encodings with the same name
            instrs[cat][name] = []

        op = Op(name, cat, form, op_mask, op_value, fields, op_flags, notes)
        instrs[cat][name].append(op)
        extra_info_str = '%s-type' % op.form
        if notes:
            extra_info_str += '; ' + '; '.join(n for n in notes)
        print('Adding op [%s] %s (%s):' % (op.cat, op.name, extra_info_str))
        for field in op.fields:
            ftype = '(%s)' % field.type.name
            print('  %-7s %-20s: bits=%d, mask=0x%02x, shift=%d' % (ftype, field.value, field.bits, field.mask, field.shift))

# Find the instruction definitions
_parts = [
    r'\n +&\n((?:\\.*instbit.* [&\\]+ *\n)+)\\[a-z]+line{\d-\d+}\n',
    r'\\multicolumn[^\\]+\\bf (.*RV.*)} & \\\\ *\n',
    r'\n&\n((?:\\multicolumn.* & *\n)+\\multicolumn.* & [A-Z0-9a-z.-]+) (?:{\\em \\tiny (.*)})? *\\\\ *\n\\[a-z]+line{\d-\d+}\n',
]
_pat = _makepat(_parts, re.MULTILINE)

_field_size_parts = [
    r'\\instbit{(\d+)}',
    'instbitrange{(\d+)}{(\d+)}',
]
_field_size_pat = _makepat(_field_size_parts, re.MULTILINE)

_cat_extension_pat = re.compile(r'{(Z[^}]+)}')
_cat_pat = re.compile(r'(RV[0-9]+[^ ]*)')

_info_parts = [
    r'\\multicolumn{(\d+)}{[|c]+}{(.*)} &',
    r' ([A-Z0-9a-z.-]+)',
]
_info_pat = _makepat(_info_parts, re.MULTILINE)

# CSR register matching pattern
_csr_table_parts = [
    r'\\tt\s*(0x[A-F0-9]{3})\s*&\s*([A-Z][RWO]{2})\s*&\s*\\tt\s*([a-z0-9]+)\s*&\s*(.*)\s*\\\\',
    r'&\s&\s\\multicolumn\{1\}\{c\|\}\{\\(vdots)\}\s&\s\\\s\\\\',
]
_csr_pat = _makepat(_csr_table_parts)

def cats_from_str(catname):
    #print(catname)

    cat_list = []

    arch, extra = catname.split(' ', maxsplit=1)
    if arch[:2] == 'RV':
        # Check how many RV?? archs are listed in the first word
        cat_list = []
        for part in arch.split('/'):
            if part[:2] != 'RV':
                cat_list.append('RV' + part)
            else:
                cat_list.append(part)

        # See if this is an extension
        match = _cat_extension_pat.search(extra)
        if match:
            for i in range(len(cat_list)):
                cat_list[i] += match.group(1)

    elif arch in ('Trap-Return', 'Interrupt-Management', 'Supervisor'):
        cat_list.append('RV32S')

    elif arch == 'Hypervisor':
        if catname.endswith('RV64 only'):
            cat_list.append('RV64S')
        else:
            cat_list.append('RV32S')

    elif arch == 'Svinval':
        cat_list.append('RV32Svinval')

    return cat_list


def scrape_instr_table(text, default_cat=None, forms=None, priv=False):
    columns = []
    if forms is None:
        forms = {}
    instructions = {}
    #if default_cat is not None:
    #    instructions[default_cat] = {}
    #cur_cat = default_cat
    cur_cats = []

    for match in _pat.findall(text):
        #print(match)
        fieldbits, catname, instrmatch, notesmatch = match
        if fieldbits:
            columns = [int(m[0]) if m[0] else (int(m[1]), int(m[2])) \
                    for m in _field_size_pat.findall(fieldbits)]
        elif instrmatch:
            instr_fields = [(int(m[0]), m[1]) if m[1] else m[2] for m in _info_pat.findall(instrmatch)]
            #print(instr_fields)
            # If the last field of instrmatch ends in '-type' this is a form
            # name (the relevant forms are repeated each section
            instr_name = instr_fields[-1]
            if instr_name.endswith('-type'):
                form_name = instr_fields[-1].upper().replace('-', '_')
                fields = get_field_info(instr_fields[:-1], columns)
                print('Adding form %s (%s)' % (form_name, fields))
                forms[form_name] = Form(form_name, fields)
            else:
                cat_list = []

                # Remove any surrounding ()
                if len(notesmatch) >= 2 and notesmatch[0] == '(' and notesmatch[-1] == ')':
                    notesmatch = notesmatch[1:-1]

                # Split the notes on any semicolons
                notes = []
                for notepart in notesmatch.split(';'):
                    note = notepart.strip()
                    if note[:2] == 'RV' and note[:11] != 'RV32 Custom':
                        # If there is a space in this then the stuff after the
                        # space should be a separate note
                        extra = None
                        if ' ' in note:
                            cat_note, extra = note.split(' ', maxsplit=1)
                            note = cat_note

                        # Turn this into one or more categories
                        for catpart in note.split('/'):
                            if catpart[:2] != 'RV':
                                catpart = 'RV' + catpart

                            if default_cat is not None:
                                # Append the last character of the supplied
                                # default category to the new category
                                catpart += default_cat[-1]
                            cat_list.append(catpart)

                        # If there was an extra note add it to the notes list
                        if extra is not None:
                            notes.append(extra)
                    elif note:
                        notes.append(note)

                # If the category list is still empty, use the default category
                if not cat_list:
                    if cur_cats:
                        cat_list.extend(cur_cats)
                    elif default_cat is not None:
                        cat_list.append(default_cat)

                descr = instr_fields[:-1]
                # We don't need the parsed form info right now
                form_name, _ = find_form(descr, forms)

                # Now find the bit width of the fields
                op_fields = get_field_info(descr, columns)
                add_instr(instructions, instr_name, cat_list, form_name, op_fields, tuple(notes), priv=priv)
        else:
            # If there are any category names found, add them to the instruction
            # table
            cur_cats = cats_from_str(catname)
            for cat in cur_cats:
                assert cat not in instructions
                instructions[cat] = {}
            #print(cur_cats)

    return forms, instructions


def scrape_rvc_forms(text):
    form_lines = [
        r'\\[a-z]+line{3-18}\n\n',
        r'([^&]+) & [^&]+ &\n',
        r'((?:\\multicolumn{[0-9]+}{[|c]+}{[^}]+} [&\\]+ *\n)+)',
    ]
    form_pat = re.compile(r''.join(form_lines), re.MULTILINE)
    field_pat = re.compile(r'^\\multicolumn{([0-9]+)}{[|c]+}{([^}]+)}', re.MULTILINE)

    # Because the RVC table doesn't use columns the same way, use a fixed
    # 16-element list where each column is 1 bit wide in the get_field_info()
    # function call, this list should be the bit position in reverse order
    rvc_columns = [i for i in reversed(range(16))]

    forms = {}
    for formmatch in form_pat.findall(text):
        form_name = formmatch[0]
        form_fields = [(int(m[0]), m[1]) for m in field_pat.findall(formmatch[1])]

        bit_total = sum([int(f[0]) for f in form_fields])
        if bit_total != 16:
            raise Exception('missing bits! %d != 16' % bit_total)

        fields = get_field_info(form_fields, rvc_columns)
        print('Adding form %s: %s' % (form_name, fields))
        forms[form_name] = Form(form_name, fields)

    return forms


def copy_carried_over_instrs(instrs, from_instrs, to_instrs):
    for name in instrs[from_instrs]:
        if to_instrs not in instrs:
            instrs[to_instrs] = {}
        if name not in instrs[to_instrs]:
            for instr in instrs[from_instrs][name]:
                add_instr(instrs, name, [to_instrs], instr.form, instr.fields, instr.notes, priv=False)


def scrape_instrs(git_repo):
    forms = {}
    instrs = {}

    with open(git_repo + '/src/instr-table.tex', 'r') as f:
        instr_table = f.read()
    unpriv_forms, unpriv_instrs = scrape_instr_table(instr_table)
    forms.update(unpriv_forms)

    # SPECIAL CASES:
    #   Unconditional Jumps are JAL with rd set to 0, so find JAL and make a
    #   duplicate entry for "J"
    jmps = ('JAL', 'JALR')
    uncond_jmps = [j.replace('AL', '') for j in jmps]

    print('Creating special case instructions not in the RISCV tables: %s' % uncond_jmps)

    for cat in unpriv_instrs.keys():
        # turn JAL into J and JALR into JR
        for old, new in zip(jmps, uncond_jmps):
            if old in unpriv_instrs[cat]:
                for old_instr in unpriv_instrs[cat][old]:
                    new_fields = []
                    for field in old_instr.fields:
                        if field.value == 'rd':
                            new_field = Field(0, OpcodeType.CONST, field.columns,
                                    field.bits, field.mask, field.shift)
                            new_fields.append(new_field)
                        else:
                            # copy from JAL field
                            new_fields.append(field)

                    add_instr(unpriv_instrs, new, [cat], old_instr.form, new_fields, old_instr.notes, priv=False)

    # TODO: automate this?
    # Some instructions should be in multiple categories
    copy_carried_over_instrs(unpriv_instrs, 'RV32I', 'RV64I')
    copy_carried_over_instrs(unpriv_instrs, 'RV32M', 'RV64M')
    copy_carried_over_instrs(unpriv_instrs, 'RV32A', 'RV64A')
    copy_carried_over_instrs(unpriv_instrs, 'RV32F', 'RV64F')
    copy_carried_over_instrs(unpriv_instrs, 'RV32D', 'RV64D')
    copy_carried_over_instrs(unpriv_instrs, 'RV32Q', 'RV64Q')
    copy_carried_over_instrs(unpriv_instrs, 'RV32Zfh', 'RV64Zfh')

    for cat, data in unpriv_instrs.items():
        if cat not in instrs:
            instrs[cat] = data
        else:
            instrs[cat].update(data)

    with open(git_repo + '/src/priv-instr-table.tex', 'r') as f:
        instr_table = f.read()

    # the privileged instructions should default to the base RV32S (supervisor)
    # category
    priv_forms, priv_instrs = scrape_instr_table(instr_table, default_cat='RV32S', priv=True)
    forms.update(priv_forms)

    # TODO: automate this?
    # Some instructions should be in multiple categories
    copy_carried_over_instrs(priv_instrs, 'RV32S', 'RV64S')

    for cat, data in priv_instrs.items():
        if cat not in instrs:
            instrs[cat] = data
        else:
            instrs[cat].update(data)

    with open(git_repo + '/src/c.tex', 'r') as f:
        instr_table = f.read()

    # the compact instruction tables specific architecture size with each
    # instruction
    rvc_forms = scrape_rvc_forms(instr_table)
    forms.update(rvc_forms)

    with open(git_repo + '/src/rvc-instr-table.tex', 'r') as f:
        instr_table = f.read()
    _, rvc_instrs = scrape_instr_table(instr_table, default_cat='RV32C', forms=rvc_forms)

    for cat, data in rvc_instrs.items():
        if cat not in instrs:
            instrs[cat] = data
        else:
            instrs[cat].update(data)

    return forms, instrs


def get_field_name(field):
    # Make the field names look a little nicer
    if '\\vert' in field.value:
        # Squash any latex $\vert$ sequences into a ',' character
        return field.value.replace('$\\vert$', ',')
    elif '\\neq' in field.value:
        return field.value.replace('$\\neq$', '!=').replace('$\{', '{').replace('\}$', '}')
    elif field.value == '\\rdprime':
        return "rd`"
    elif field.value == '\\rsoneprime':
        return "rs1`"
    elif field.value == '\\rstwoprime':
        return "rs2`"
    elif field.value == '\\rsoneprime/\\rdprime':
        return "rs1`/rd`"
    else:
        return field.value


def fix_mnem(mnem):
    # make the mnemonic lowercase
    # Remove any "C." prefixes
    if mnem.startswith('C.'):
        return mnem[2:].lower()
    else:
        return mnem.lower()


def get_field_flags(name, field):
    flags = []
    if field.type in (OpcodeType.REG, OpcodeType.C_REG):
        if name.startswith('rs'):
            flags.append('RISCV_OF.SRC')
        elif name.startswith('rd'):
            flags.append('RISCV_OF.DEST')
        else:
            raise Exception('unexpected register name %f' % field)
    elif field.type == OpcodeType.CSR_REG:
        # CSR registers/fields are always both source and destinations
        flags.append('RISCV_OF.SRC')
        flags.append('RISCV_OF.DEST')
    elif name.startswith('imm'):
        flags.append('RISCV_OF.SIGNED')
    elif name.startswith('uimm'):
        flags.append('RISCV_OF.UNSIGNED')
    elif name.startswith('nzimm'):
        flags.append('RISCV_OF.SIGNED')
        flags.append('RISCV_OF.NON_ZERO')
    elif name.startswith('nzuimm'):
        flags.append('RISCV_OF.UNSIGNED')
        flags.append('RISCV_OF.NON_ZERO')
    return flags


imm_bits_pat = re.compile(r'^.*\[([0-9,:]+)]$')

def create_imm_mask_and_shifts(names_and_fields_list):
    parts = []
    matches = [(f, imm_bits_pat.match(n)) for n, f in names_and_fields_list]

    masks_and_shifts = []

    # If there is a failed match then there should also be only 1 IMM field
    if any(m == None for _, m in matches):
        assert len(names_and_fields_list) == 1
        # The standard RiscVField order of operations is shift then mask, so
        # adjust the standard mask to work for the IMM-specific mask/shift
        # order.
        field = names_and_fields_list[0][1]
        masks_and_shifts.append((field.mask << field.shift, field.shift))
    else:
        # Construct a list of operations
        for f, m in matches:
            pos = f.shift
            for chunk in reversed(m.group(1).split(',')):
                bit_values = chunk.split(':')
                if len(bit_values) == 1:
                    # Single bit
                    start = int(bit_values[0])
                    masks_and_shifts.append((1 << pos, pos - start))
                    pos += 1
                else:
                    end = int(bit_values[0])
                    start = int(bit_values[1])
                    width = end - start + 1
                    mask = int('0b' + ('1' * width) + ('0' * pos), 2)
                    masks_and_shifts.append((mask, pos - start))
                    pos += width
    return tuple(masks_and_shifts)


LOAD_INSTRS = (
    'LB', 'LH', 'LW', 'LD', 'LQ', 'LBU', 'LHU', 'LWU', 'LDU',
    'C.LW', 'C.LD', 'C.LQ', 'C.LWSP', 'C.LDSP', 'C.LQSP',
    'FLH', 'FLW', 'FLD', 'FLQ',
    'C.FLW', 'C.FLD', 'C.FLWSP', 'C.FLDSP',
)

STORE_INSTRS = (
    'SB', 'SH', 'SW', 'SD', 'SQ',
    'C.SW', 'C.SD', 'C.SQ', 'C.SWSP', 'C.SDSP', 'C.SQSP',
    'FSH', 'FSW', 'FSD', 'FSQ',
    'C.FSW', 'C.FSD', 'C.FSWSP', 'C.FSDSP',
)

OP_MEM_SIZES = (
    ('RISCV_OF.BYTE',       ('LB', 'LBU', 'SB')),
    ('RISCV_OF.HALFWORD',   ('LH', 'LHU', 'FLH', 'SH', 'FSH')),
    ('RISCV_OF.WORD',       ('LW', 'LWU', 'C.LW', 'C.LWSP', 'FLW', 'C.FLW',
                             'C.FLWSP', 'SW', 'C.SW', 'FSW', 'C.FSW',
                             'C.FSWSP', 'C.LWSP', 'C.SWSP',
                             'LR.W', 'SC.W')),
    ('RISCV_OF.DOUBLEWORD', ('LD', 'LDU', 'C.LD', 'C.LDSP', 'FLD', 'C.FLD',
                             'C.FLDSP', 'SD', 'C.SD', 'FSD', 'C.FSD',
                             'C.FSDSP', 'C.LDSP', 'C.SDSP',
                             'LR.D', 'SC.D')),
    ('RISCV_OF.QUADWORD',   ('LQ', 'C.LQ', 'C.LQSP', 'FLQ', 'SQ', 'C.SQ',
                             'C.SQSP', 'FSQ')),
)

RS1_MEM_REF_INSTRS = tuple(list(LOAD_INSTRS) + list(STORE_INSTRS) + [
    'LR.W', 'LR.D', 'SC.W', 'SC.D',
])


def get_instr_flags(name, fields, priv=False):
    """
    Return the correct set of standard envi flags for the instruction
      envi.IF_NOFALL
      envi.IF_PRIV
      envi.IF_CALL
      envi.IF_BRANCH
      envi.IF_RET
      envi.IF_COND
      envi.IF_REPEAT
      envi.IF_BRANCH_COND
    """

    flags = []
    if name in ('J', 'JR', 'C.JR', 'C.J'):
        flags.append('envi.IF_CALL')
        flags.append('envi.IF_NOFALL')
    elif name in ('JAL', 'JALR', 'C.JAL', 'C.JALR'):
        flags.append('envi.IF_CALL')
    elif name in ('BEQ', 'BNE', 'BLT', 'BGE', 'BLTU', 'BGEU', 'C.BNEZ', 'C.BEQZ'):
        flags.append('envi.IF_COND')
        flags.append('envi.IF_BRANCH')

    if priv:
        flags.append('envi.IF_PRIV')

    return flags


def get_instr_final_flags(instr):
    """
    Return the complete flag list for an instruction based on all gathered
    information
    """
    flags = instr.flags

    if instr.name in LOAD_INSTRS or instr.name.startswith('LR.'):
        if instr.name.endswith('SP'):
            flags.append('RISCV_IF.LOAD_SP')
        else:
            flags.append('RISCV_IF.LOAD')
    elif instr.name in STORE_INSTRS or instr.name.startswith('SC.'):
        if instr.name.endswith('SP'):
            flags.append('RISCV_IF.STORE_SP')
        else:
            flags.append('RISCV_IF.STORE')

    if flags:
        return ' | '.join(flags)
    else:
        return '0'


def get_instr_mnem(mnem):
    """
    Make the mnemonic lowercase and remove any "C." prefixes
    """
    if mnem.startswith('C.'):
        return mnem[2:].lower()
    else:
        return mnem.lower()


def get_instr_name(name):
    """
    Replace all load/store instructions with a single LOAD/STORE instruction.
    Otherwise just change any '.'s to '_'s
    """
    if name in LOAD_INSTRS:
        return 'LOAD'
    elif name in STORE_INSTRS:
        return 'STORE'

    # The LR and SC instructions are essentially load and store
    # instructions but have slightly different functionality so
    # change the instruction name to LOAD_RESERVED and
    # STORE_CONDITIONAL
    elif name.startswith('LR.'):
        return 'LOAD_RESERVED'
    elif name.startswith('SC.'):
        return 'STORE_CONDITIONAL'

    else:
        # Remove any trailing '.AQ' or '.RL' parts
        # change all .'s to _'s
        return name.replace('.AQ', '').replace('.RL', '').replace('.', '_')


def make_field_args_str(mask, shift, flags=None):
    return 'RiscVFieldArgs(0x%x, %d)' % (mask, shift)


# Mapping of RiscV*Field type used by the make_field_str() function
FIELD_TYPE_MAP = {
    OpcodeType.REG: 'RiscVField',
    OpcodeType.C_REG: 'RiscVField',
    OpcodeType.CSR_REG: 'RiscVField',
    OpcodeType.RM: 'RiscVField',
    OpcodeType.IMM: 'RiscVImmField',
    OpcodeType.MEM: 'RiscVMemField',
    OpcodeType.MEM_SP: 'RiscVMemSPField',
}


def make_field_str(instr_name, op, bits, args=None, field_type=None, field_name=None):
    if field_type is None:
        field_type = op.type
    named_type = FIELD_TYPE_MAP[field_type]

    if field_name is None:
        field_name = get_field_name(op)
    flags = get_field_flags(field_name, op)
    # Add in instruction-specific flags
    for flag, instr_list in OP_MEM_SIZES:
        if instr_name in instr_list:
            flags.append(flag)
    if flags:
        flags_str = ' | '.join(flags)
    else:
        flags_str = '0'

    if not args:
        # Turn the old shift/mask operands into the newer mask/shift tuple
        args_str = make_field_args_str(op.mask << op.shift, op.shift)
    elif len(args) >= 2 and isinstance(args[0], int) and isinstance(args[1], int):
        # Check if the args are a simple (int, int) tuple
        args_str = make_field_args_str(*args)
    else:
        # We need to support multiple argument lists, because the
        # RiscVMemField has an argument list for the base register and a
        # second argument list for the offset immediate value.
        field_args = []
        for arglist in args:
            #if bits is None:
            #    arglist
            # If this argument a tuple of two integers, just make the field,
            # otherwise make a list of fields.
            if len(arglist) >= 2 and isinstance(arglist[0], int) and isinstance(arglist[1], int):
                field_args.append(make_field_args_str(*arglist))
            else:
                # Each individual set of arglist should be wrapped in
                # parenthesis
                field_args.append('(' + ', '.join(make_field_args_str(*a) for a in arglist) + ',)')
        # Don't wrap the field args in parenthesis, more args list means more
        # required positional args to this field
        args_str = '(' + ', '.join(field_args) + ',)'

    operand_str = "%s('%s', RISCV_FIELD.%s, %d, (%s), %s)" % \
            (named_type, field_name, field_type.name, bits, args_str, flags_str)

    return operand_str


# Only some "opcode" fields are exported
EXPORT_FIELDS = (OpcodeType.REG, OpcodeType.C_REG, OpcodeType.CSR_REG,
        OpcodeType.IMM, OpcodeType.RM)


def export_instrs(forms, instrs, git_info):
    # Export all the forms
    form_list = list(forms.keys())

    # Make a list of the categories (the categories are the primary keys of the
    # instructions)
    #cat_list = list(instrs.keys())

    # To turn the instruction names into python constants we first need to
    # remove any embedded '.'s.  Also while looping through the instruction
    # categories build up a list of all the categories that each instruction is
    # present in.
    instr_to_cat_map = {}
    for cat, cat_data in instrs.items():
        for name in cat_data.keys():
            if name not in instr_to_cat_map:
                # generate the RISCV_INSTR const string now
                instr_to_cat_map[name] = (get_instr_name(name), [cat])
            else:
                instr_to_cat_map[name][1].append(cat)

    # Create these files in the envi/archs/riscv/ directory, not the directory
    # that the python command is run in (which is what os.getcwd() will return).
    cur_dir = os.path.dirname(__file__)
    with open(os.path.join(cur_dir, 'const_gen.py'), 'w') as out:
        # First log the git information
        out.write('# Generated from:\n')
        for info in git_info:
            out.write('#   %s\n' % info)
        out.write('\n')

        # These constants will be IntEnums
        out.write('import enum\n')
        out.write('from collections import namedtuple\n\n\n')

        # Write the custom IF_??? and OF_??? flags used by RISC-V instructions
        # (if any)
        #out.write('IF_NONE = 0\n\n')
        #out.write('OF_NONE = 0\n\n\n')

        # Now save the scraped FORM, CAT, and OP (instruction) values
        out.write('class RISCV_FORM(enum.IntEnum):\n')
        for form in form_list:
            out.write('    %s = enum.auto()\n' % form.upper())
        out.write('\n\n')

        # TODO: The category name strings don't yet match between the
        # instruction encodings and the table entries
        #out.write('class RISCV_CAT(enum.IntEnum):\n')
        #for cat in cat_list:
        #    out.write('    %s = enum.auto()\n' % cat.upper())
        #out.write('\n\n')

        # Write out the field types
        out.write('class RISCV_FIELD(enum.IntEnum):\n')
        for field_type in ('REG', 'C_REG', 'F_REG', 'CSR_REG', 'MEM', 'MEM_SP', 'IMM', 'RM'):
            out.write('    %s = enum.auto()\n' % field_type)
        out.write('\n\n')

        # Get a list of all of the instructions
        instr_consts = sorted(set(n for n, _ in instr_to_cat_map.values()))
        out.write('class RISCV_INS(enum.IntEnum):\n')
        for instr in instr_consts:
            out.write('    %s = enum.auto()\n' % instr.upper())
        out.write('\n')

        # Write out the RiscV instruction and operand flags
        out.write('''
# Additional RiscV-specific instruction flags
class RISCV_IF(enum.IntFlag):
    # Indicate normal load/store instructions
    LOAD        = 1 << 8
    STORE       = 1 << 9

    # Indicate this is a compressed load/store instruction that uses the SP (x2)
    # as the base register
    LOAD_SP     = 1 << 10
    STORE_SP    = 1 << 11

    # acquire or release spinlock flags
    AQ          = 1 << 12
    RL          = 1 << 13


# RiscV operand flags
class RISCV_OF(enum.IntFlag):
    SRC         = 1 << 1
    DEST        = 1 << 2
    NON_ZERO    = 1 << 3
    SIGNED      = 1 << 4
    UNSIGNED    = 1 << 5

    # Flags used to indicate size these definitions match those used in the
    # RiscV manual
    BYTE        = 1 << 6   # 1 byte
    HALFWORD    = 1 << 7   # 2 bytes
    WORD        = 1 << 8   # 4 bytes
    DOUBLEWORD  = 1 << 9   # 8 bytes
    QUADWORD    = 1 << 10  # 16 bytes
''')

        # Now write the namedtuple types used in construction of the instruction
        # table.
        out.write('''
# Standard types used in the generated instruction list
RiscVInsCat = namedtuple('RiscVInsCat', ['xlen', 'cat'])
RiscVIns = namedtuple('RiscVIns', ['name', 'opcode', 'form', 'cat', 'mask', 'value', 'fields', 'flags'])

# A simple field where the field value can be masked and shifted out of the
# instruction value.
RiscVField = namedtuple('RiscVField', ['name', 'type', 'bits', 'args', 'flags'])

# Many RiscV instructions have complex immediate values like:
#   BEQ  imm[12,10:5] | rs2 | rs1 | imm[4:1,11]
#
# This field type contains a list of mask and shift operations that can be used
# to re-assemble the correct immediate from the instruction value
RiscVImmField = namedtuple('RiscVImmField', ['name', 'type', 'bits', 'args', 'flags'])

# RiscV load/store instructions use an immediate value to define an offset from
# a source/base register This field contains the arguments necessary to extract
# the source register value and immediate offset value from the instruction
# value
#   LWU  imm[11:0] | rs1 | rd
RiscVMemField = namedtuple('RiscVMemField', ['name', 'type', 'bits', 'args', 'flags'])

# RiscV compressed load/store instructions are like normal load/store
# instructions but they always use the x2 (the stack pointer) register as the
# base register
RiscVMemSPField = namedtuple('RiscVMemSPField', ['name', 'type', 'bits', 'args', 'flags'])

# A field type to hold mask/shift arguments for IMM and MEM fields
RiscVFieldArgs = namedtuple('RiscVFieldArgs', ['mask', 'shift'])
''')

    cur_dir = os.path.dirname(__file__)
    with open(os.path.join(cur_dir, 'instr_table.py'), 'w') as out:
        # First log the git information
        out.write('# Generated from:\n')
        for info in git_info:
            out.write('#   %s\n' % info)

        # Dump the types used to encode the instructions
        out.write('''
import envi
from envi.archs.riscv.const import *

__all__ = ['instructions']

''')

        # Dump the form and instructions
        # TODO:
        #
        # - figure out how to actually handle the weird imm[*****] fields
        #
        # - do we want unsigned flags for some IMM fields for unsigned
        #   functions? (LWU vs LW) or should that be a different field type?
        #   Or maybe based on the field name like imm vs uimm (or nzuimm)
        #
        # - Is the 'funct' field something that would be useful to turn into
        #   flags or some other info?
        out.write('instructions = (\n')
        try:
            for name, (instr_name, cats) in instr_to_cat_map.items():
                for instr in instrs[cats[0]][name]:
                    all_fields = [(get_field_name(op), op) for op in instr.fields if op.type in EXPORT_FIELDS]

                    imm_fields = [(fn, op) for fn, op in all_fields if \
                            op.type == OpcodeType.IMM and ('imm' in fn or 'shamt' in fn)]

                    non_imm_fields = [(fn, op) for fn, op in all_fields if not
                            (op.type == OpcodeType.IMM and ('imm' in fn or 'shamt' in fn))]

                    if name in RS1_MEM_REF_INSTRS:
                        fields = [op for fn, op in non_imm_fields if 'rs1' not in fn]
                        imm_args = create_imm_mask_and_shifts(imm_fields)

                        rs1_op = [op for fn, op in all_fields if 'rs1' in fn]
                        if rs1_op:
                            assert len(rs1_op) == 1

                            # for the LR and SC instructions instead create a
                            # "constant" 0 offset field argument that will consume
                            # no bits but ensure the load/store operand has a valid
                            # offset
                            if not imm_fields:
                                imm_fields = [('zero', Field('zero', type=OpcodeType.IMM, columns=0, bits=0, mask=0, shift=0))]
                                imm_args = ((0, 0),)

                            rs1_args = (rs1_op[0].mask << rs1_op[0].shift, rs1_op[0].shift)
                            # Bit width of this field is the width of the IMM arg,
                            last_field = make_field_str(name, imm_fields[0][1], \
                                    bits=sum(op.bits for _, op in imm_fields), \
                                    args=(rs1_args, imm_args), field_type=OpcodeType.MEM)
                        else:
                            # This should only be true for "compressed" load
                            # instructions
                            assert name.startswith('C.')
                            last_field = make_field_str(name, imm_fields[0][1],
                                    bits=sum(op.bits for _, op in imm_fields), \
                                    args=imm_args, field_type=OpcodeType.MEM_SP)

                    elif imm_fields:
                        # Build a list of only the non-imm fields to be turned into
                        # operands
                        fields = [op for _, op in non_imm_fields]
                        imm_args = create_imm_mask_and_shifts(imm_fields)

                        # Extract the non-bits portion of the first field name to
                        # identify what this one should be called.
                        imm_field_name = imm_fields[0][1].value.split('[', 1)[0]

                        last_field = make_field_str(name, imm_fields[0][1], args=imm_args, \
                                bits=sum(op.bits for _, op in imm_fields), \
                                field_type=OpcodeType.IMM, field_name=imm_field_name)

                    elif any(op.type == OpcodeType.RM for op in instr.fields):
                        # If there is a rounding mode operand in this instruction move
                        # it to the end of the operand list
                        fields = [op for _, op in all_fields if op.type != OpcodeType.RM]
                        rm_op = next(op for _, op in all_fields if op.type == OpcodeType.RM)
                        last_field = make_field_str(name, rm_op, rm_op.bits)

                    else:
                        fields = [op for _, op in all_fields]
                        last_field = None

                    operand_list = []
                    # In general regsiter operands should be displayed in reverse order
                    # than they are encoded in the instruction so reverse the operand
                    # fields now.
                    for op in reversed(fields):
                        if op.type in (OpcodeType.REG, OpcodeType.C_REG, OpcodeType.CSR_REG):
                            operand_list.append(make_field_str(name, op, op.bits))
                        elif op.type == OpcodeType.IMM and op.value in ('pred', 'succ'):
                            # The 'pred' and 'succ' fields should be normal IMM, but
                            # they are not moved to the end of the param list so
                            # they should be processed in place here.

                            # Convert the normal shift/mask values into IMM
                            # mask/shift values
                            imm_args = ((op.mask << op.shift, op.shift),)
                            operand_list.append(make_field_str(name, op, op.bits, args=imm_args))
                        else:
                            print('%s missing %s field' % (name, str(op)))

                    if last_field is not None:
                        operand_list.append(last_field)

                    # Turn the categories from strings into RiscVInsCat values
                    cat_list = []
                    cat_parts_pat = re.compile(r'^RV([0-9]+)([^ ]*)$')
                    for cat in cats:
                        match = cat_parts_pat.search(cat)
                        assert match
                        cat_list.append('RiscVInsCat(%s, RISCV_CAT.%s)' % (match.group(1), match.group(2)))

                    # we need to have a trailing comma on the category and fields
                    # lists so a single-element list will be correctly created as a
                    # tuple
                    cats_str = '(' + ', '.join(cat_list) + ',)'
                    if operand_list:
                        operand_str = '(' + ', '.join(operand_list) + ',)'
                    else:
                        operand_str = '()'

                    instr_str = "RiscVIns('%s', RISCV_INS.%s, RISCV_FORM.%s, %s, 0x%x, 0x%x, %s, %s)" % \
                            (get_instr_mnem(name), instr_name, instr.form, cats_str, \
                            instr.mask, instr.value, operand_str, \
                            get_instr_final_flags(instr))
                    out.write("    %s,\n" % instr_str)
        finally:
            out.write(')\n')


def scrape_csr_regs(git_repo):
    regs = []
    with open(git_repo + '/src/priv-csrs.tex', 'r') as f:
        csr_table = []
        for line in f:
            m = _csr_pat.match(line)
            if m:
                csr_table.append(m.groups())

    regname_parts_pat = re.compile(r'([a-z]+)([0-9]+)([a-z]*)')

    for i in range(len(csr_table)):
        num, perm, name, descr, vdots = csr_table[i]
        if not vdots:
            regs.append((num, perm, name, descr))
        else:
            # Get the start and end register names/numbers
            prev_reg_num_str, prev_perm, prev_name_str, _, _ = csr_table[i - 1]
            next_reg_num_str, next_perm, next_name_str, _, _ = csr_table[i + 1]

            prev_reg_num = int(prev_reg_num_str, 16)
            m = regname_parts_pat.match(prev_name_str)
            assert m
            prev_name_prefix, prev_name_num_str, prev_name_postfix = m.groups()
            prev_name_num = int(prev_name_num_str, 10)

            next_reg_num = int(next_reg_num_str, 16)
            m = regname_parts_pat.match(next_name_str)
            assert m
            next_name_prefix, next_name_num_str, next_name_postfix = m.groups()
            next_name_num = int(next_name_num_str, 10)

            # Sanity check, the previous and next pre/post name strings should
            # match
            assert prev_perm == next_perm
            assert prev_name_prefix == next_name_prefix
            assert prev_name_postfix == next_name_postfix

            # Add the CSRs
            reg_num_range = range(prev_reg_num + 1, next_reg_num)
            name_num_range = range(prev_name_num + 1, next_name_num)
            for reg_num, name_num in zip(reg_num_range, name_num_range):
                name = '%s%d%s' % (prev_name_prefix, name_num, prev_name_postfix)
                regs.append((hex(reg_num), prev_perm, name, ''))
    return regs


def export_csr_regs(regs, git_info):
    cur_dir = os.path.dirname(__file__)
    with open(os.path.join(cur_dir, 'regs_gen.py'), 'w') as out:
        # First log the git information
        out.write('# Generated from:\n')
        for info in git_info:
            out.write('#   %s\n' % info)

        out.write('''
from collections import namedtuple


# Standard types used in the generated instruction list
RiscVCSRReg = namedtuple('RiscVCSRReg', ['num', 'perm', 'name', 'description'])


csr_regs = {
''')
        # Dump the types used to encode the instructions
        for num, perm, name, descr in regs:
            out.write("    %s: RiscVCSRReg(%s, '%s', '%s', '%s'),\n" % (num, num, perm, name, descr))
        out.write('}\n')


def main(git_repo):
    # First get a hash/version so we can capture that in the output
    cmd = ['git', '-C', git_repo, 'remote', 'get-url', 'origin']
    with subprocess.Popen(cmd, stdout=subprocess.PIPE) as p:
        git_url = p.stdout.read().strip()

    cmd = ['git', '-C', git_repo, 'describe', '--all']
    with subprocess.Popen(cmd, stdout=subprocess.PIPE) as p:
        git_tag = p.stdout.read().strip()

    cmd = ['git', '-C', git_repo, 'rev-parse', 'HEAD']
    with subprocess.Popen(cmd, stdout=subprocess.PIPE) as p:
        git_hash = p.stdout.read().strip()

    forms, instrs = scrape_instrs(git_repo)
    export_instrs(forms, instrs, (git_url, git_tag, git_hash))

    csr_regs = scrape_csr_regs(git_repo)
    export_csr_regs(csr_regs, (git_url, git_tag, git_hash))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='path to RISC-V manual git repo')
    args = parser.parse_args()
    main(args.path)
