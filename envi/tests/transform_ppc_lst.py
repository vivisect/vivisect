#!/usr/bin/env python

import re
import sys
import collections

# VLE instructions are all prefixed with se_ or e_, but the VLE cores do
# support a small subset of EREF defined instructions (defined in section
# 3.1 of the VLEPEM).
#
# The format of all lines in the IDA produced listing is:
# address |    data   | 16 spaces | disassembly
# XXXXXXXX XX XX ?? ??     ...      e_lis ...
#
# Lines with no data are ignored, any non-code information in the listing can
# be ignored by ensuring that the data is either 2 or 4 bytes - if it is
# 2 bytes then 6 placeholder spaces will be present - 16 spaces, and then an
# instruction that does not start with a ".".  All data defined in IDA starts
# with ".":
#   .byte
#   .word
#   .dword
#   .qword
#
# This regex first finds all instructions that need to have non-register
# operands adjusted before they can be useful for using in ppc unit tests.
# After all instructions that require modification are found, there are 3
# placeholder patterns at the end to catch SE, E and PPC instructions that need
# no adjustments.
#
# All trailing whitespace and comments is dropped.

class lst_parser(object):
    Token = collections.namedtuple('Token', ['type', 'match', 'value', 'column'])

    def __init__(self):
        token_spec = [
            ('SECTION64',    r'^[0-9A-Za-z_.]+:[0-9A-Fa-f]{16}'),
            ('SECTION32',    r'^[0-9A-Za-z_.]+:[0-9A-Fa-f]{8}'),
            ('ADDR64',       r'^[0-9A-Fa-f]{16}'),
            ('ADDR32',       r'^[0-9A-Fa-f]{8}'),
            ('BYTES',        r' [0-9A-Fa-f]{2} [0-9A-Fa-f]{2}(?: [0-9A-Fa-f]{2} [0-9A-Fa-f]{2}| {6})?'),
            ('DATA',         r'\.(?:byte|short|dword|qword)'),
            ('STRUCTDATA',   r' {17}[a-zA-Z][0-9A-Za-z_.]+ +<[x0-9A-Fa-f, ]+>'),
            ('REG',          r'\b(?:cr|r|v|fpr|f)[0-9]{1,2}\b'),
            ('ASM',          r' {17}(?:e_|se_)?[a-z][a-z0-9]*\b\.?(?: |$)'),
            ('CONDITION',    r'(?:4 ?\* ?cr[0-7] ?\+ ?)?(?:lt|gt|eq|so|un)\b'),
            ('COMMENT',      r'#.*'),
            ('STRING',       r'".*"'),
            ('INDIRECT_REF', r'\(r[0-9]{1,2}\)'),
            ('LABEL_MATH',   r'\(?[^-(), ]+ ?[-+] ?[^-+(), ]+\)?(?:@[a-z]+)?'),
            ('LABEL',        r'[^-+(), 0-9][^-+(), ]*'),
            ('DEC_CONST',    r'(?:-)?\b[0-9]+\b'),
            ('HEX_CONST',    r'(?:-)?\b0x[0-9A-Fa-f]+\b'),
        ]
        self.token_regex = re.compile('|'.join('(?P<%s>%s)' % pair for pair in token_spec))

    def tokenize(self, line):
        for obj in self.token_regex.finditer(line):
            kind = obj.lastgroup
            match = obj.group().strip()

            if kind in ['SECTION32', 'SECTION64']:
                value = int(match.split(':')[1], 16)
            elif kind in ['ADDR32', 'ADDR64', 'HEX_CONST']:
                value = int(match, 16)
            elif kind == 'DEC_CONST':
                value = int(match)
            elif kind == 'BYTES':
                match = match.replace(' ', '')
                value = int(match, 16)
            else:
                value = match

            yield lst_parser.Token(kind, match, value, obj.start())

class ppc_instr(object):
    Instructions = {
        # Unconditional Branches
        'se_b':         'signed_bd8',              # BD8:  signed 8 bit value << 1
        'se_bl':        'signed_bd8',              # BD8:  signed 8 bit value << 1
        'e_b':          'signed_bd24',             # BD24: signed 24 bit value << 1
        'e_bl':         'signed_bd24',             # BD24: signed 24 bit value << 1
        'b':            'signed_i',                # I:    signed 24 bit value << 2
        'bl':           'signed_i',                # I:    signed 24 bit value << 2

        # Conditional Branches
        'se_bge':       'signed_bd8',              # BD8:  signed 8 bit value << 1
        'se_bgt':       'signed_bd8',              # BD8:  signed 8 bit value << 1
        'se_ble':       'signed_bd8',              # BD8:  signed 8 bit value << 1
        'se_blt':       'signed_bd8',              # BD8:  signed 8 bit value << 1
        'se_bne':       'signed_bd8',              # BD8:  signed 8 bit value << 1
        'se_beq':       'signed_bd8',              # BD8:  signed 8 bit value << 1
        'e_bge':        'signed_bd15',             # BD15: signed 15 bit value << 1
        'e_bgt':        'signed_bd15',             # BD15: signed 15 bit value << 1
        'e_ble':        'signed_bd15',             # BD15: signed 15 bit value << 1
        'e_blt':        'signed_bd15',             # BD15: signed 15 bit value << 1
        'e_bne':        'signed_bd15',             # BD15: signed 15 bit value << 1
        'e_beq':        'signed_bd15',             # BD15: signed 15 bit value << 1
        'e_bdnz':       'signed_bd15',             # BD15: signed 15 bit value << 1
        'bge':          'signed_b',                # B:    signed 14 bit value << 2
        'bgt':          'signed_b',                # B:    signed 14 bit value << 2
        'ble':          'signed_b',                # B:    signed 14 bit value << 2
        'blt':          'signed_b',                # B:    signed 14 bit value << 2
        'bne':          'signed_b',                # B:    signed 14 bit value << 2
        'beq':          'signed_b',                # B:    signed 14 bit value << 2
        'bdnz':         'signed_b',                # B:    signed 14 bit value << 2
        'bdnzf':        'signed_b',                # B:    signed 14 bit value << 2
        'bdnzt':        'signed_b',                # B:    signed 14 bit value << 2
        'bns':          'signed_b',                # B:    signed 14 bit value << 2
        'bdz':          'signed_b',                # B:    signed 14 bit value << 2
        'bc':           'signed_b_full',           # B:    signed 14 bit value << 2
        'bcl':          'signed_b_full',           # B:    signed 14 bit value << 2
        'bca':          'signed_b_full',           # B:    signed 14 bit value << 2
        'bcla':         'signed_b_full',           # B:    signed 14 bit value << 2

        # Integer Select
        'isel':         'special_r0_handling',     # A:    special handling of param rA r0 case
        'iseleq':       'special_r0_handling',     # A:    special handling of param rA r0 case
        'isellt':       'special_r0_handling',     # A:    special handling of param rA r0 case
        'iselgt':       'special_r0_handling',     # A:    special handling of param rA r0 case

        # Store Doubleword
        'std':          'signed_ds',               # DS:   unsigned 14 bit value << 2
        'stdu':         'signed_ds',               # DS:   unsigned 14 bit value << 2

        # Store Float Double
        'stfd':         'signed_d',                # D:    unsigned 16 bit value

        # Load Doubleword
        'ld':           'signed_ds',               # DS:   unsigned 14 bit value << 2
        'ldu':          'signed_ds',               # DS:   unsigned 14 bit value << 2

        # Store Word
        'se_stw':       'unsigned_sd4_word_addr',  # SD4:  unsigned 4 bit value << 2
        'e_stw':        'signed_d',                # D:    signed 16 bit value
        'e_stwu':       'signed_d8',               # D8:   signed 8 bit value
        'e_stmw':       'signed_d8',               # D8:   signed 8 bit value
        'e_stmvgprw':   'signed_d8',               # D8:   signed 8 bit value
        'e_stmvsprw':   'signed_d8',               # D8:   signed 8 bit value
        'e_stmvsrrw':   'signed_d8',               # D8:   signed 8 bit value
        'e_stmvcrrw':   'signed_d8',               # D8:   signed 8 bit value
        'e_stmvdrrw':   'signed_d8',               # D8:   signed 8 bit value
        'stw':          'signed_d',                # D:    unsigned 16 bit value
        'stwu':         'signed_d',                # D:    unsigned 16 bit value

        # Store Half Word
        'se_sth':       'unsigned_sd4_half_addr',  # SD4:  unsigned 4 bit value << 1
        'e_sth':        'signed_d',                # D:    signed 16 bit value
        'e_sthu':       'signed_d8',               # D8:   signed 8 bit value
        'sth':          'signed_d',                # D:    unsigned 16 bit value
        'sthu':         'signed_d',                # D:    unsigned 16 bit value

        # Store Byte
        'se_stb':       'unsigned_sd4_byte_addr',  # SD4:  unsigned 4 bit value
        'e_stb':        'signed_d',                # D:    signed 16 bit value
        'e_stbu':       'signed_d8',               # D8:   signed 8 bit value
        'stb':          'signed_d',                # D:    signed 16 bit value
        'stbu':         'signed_d',                # D:    signed 16 bit value

        # Store Float
        'stfs':         'signed_d',                # D:    signed 16 bit value
        'stfsu':        'signed_d',                # D:    signed 16 bit value
        'stfd':         'signed_d',                # D:    signed 16 bit value
        'stfdu':        'signed_d',                # D:    signed 16 bit value

        # Load Word
        'se_lwz':       'unsigned_sd4_word_addr',  # SD4:  unsigned 4 bit value << 2
        'e_lwz':        'signed_d',                # D:    signed 16 bit value
        'e_lwz':        'signed_d',                # D:    signed 16 bit value
        'e_lmw':        'signed_d8',               # D8:   signed 8 bit value
        'e_lwzu':       'signed_d8',               # D8:   signed 8 bit value
        'e_ldmvgprw':   'signed_d8',               # D8:   signed 8 bit value
        'e_ldmvsprw':   'signed_d8',               # D8:   signed 8 bit value
        'e_ldmvsrrw':   'signed_d8',               # D8:   signed 8 bit value
        'e_ldmvcrrw':   'signed_d8',               # D8:   signed 8 bit value
        'e_ldmvdrrw':   'signed_d8',               # D8:   signed 8 bit value
        'lwz':          'signed_d_handle_r0',      # D:    signed 16 bit value
        'lwa':          'signed_ds',               # DS:   unsigned 14 bit value << 2
        'lwzu':         'signed_d_handle_r0',      # D:    signed 16 bit value
        'lwzx':         'special_r0_handling',     # X:    special handling of param rA r0 case

        # Load Float Double
        'lfd':          'signed_d',                # D:    unsigned 16 bit value

        # Load Float Single
        'lfs':          'signed_d',                # D:    unsigned 16 bit value

        # Load Half
        'se_lhz':       'unsigned_sd4_half_addr',  # SD4:  unsigned 4 bit value << 1
        'e_lhz':        'signed_d',                # D:    signed 16 bit value
        'e_lhzu':       'signed_d8',               # D8:   signed 8 bit value
        'e_lha':        'signed_d',                # D:    signed 16 bit value
        'e_lhau':       'signed_d8',               # D8:   signed 8 bit value
        'lhz':          'signed_d',                # D:    signed 16 bit value
        'lha':          'signed_d',                # D:    signed 16 bit value
        'lhzu':         'signed_d',                # D:    signed 16 bit value
        'lhax':         'special_r0_handling',     # X:    special handling of param rA r0 case

        # Load Byte
        'se_lbz':       'unsigned_sd4_byte_addr',  # SD4:  unsigned 4 bit value
        'e_lbz':        'signed_d',                # D:    signed 16 bit value
        'e_lbzu':       'signed_d8',               # D8:   signed 8 bit value
        'lbz':          'signed_d',                # D:    signed 16 bit value
        'lba':          'signed_d',                # D:    signed 16 bit value
        'lbzu':         'signed_d',                # D:    signed 16 bit value

        # Load Immediate'
        'se_li':        'unsigned_im7',            # IM7:  unsigned 7 bit value
        'e_li':         'signed_li20',             # LI20: signed 20 bit value
        'e_lis':        'unsigned_i16l',           # I16L: unsigned 16 bit value
        'li':           'signed_d',                # D:    signed 16 bit value (alias of addi)
        'lis':          'signed_d',                # D:    signed 16 bit value (alias of addis)

        # OR Immediate
        'e_or2i':       'unsigned_i16l',           # I16L: unsigned 16 bit value
        'e_or2is':      'unsigned_i16l',           # I16L: unsigned 16 bit value
        'e_ori':        'unsigned_sci8',           # SCI8: "unsigned" 32 bit value
        'e_ori.':       'unsigned_sci8',           # SCI8: "unsigned" 32 bit value
        'ori':          'unsigned_d',              # D:    unsigned 16 bit value
        'ori.':         'unsigned_d',              # D:    unsigned 16 bit value
        'oris':         'unsigned_d',              # D:    unsigned 16 bit value

        # XOR Immediate
        'e_xori':       'unsigned_sci8',           # SCI8: "unsigned" 32 bit value
        'e_xori.':      'unsigned_sci8',           # SCI8: "unsigned" 32 bit value
        'xori':         'unsigned_d',              # D:    unsigned 16 bit value
        'xoris':        'unsigned_d',              # D:    unsigned 16 bit value

        # AND Immediate
        'se_andi':      'unsigned_im5',            # IM5:  unsigned 5 bit value
        'e_and2i.':     'unsigned_i16l',           # I16L: unsigned 16 bit value
        'e_and2is.':    'unsigned_i16l',           # I16L: unsigned 16 bit value
        'e_andi':       'unsigned_sci8',           # SCI8: "unsigned" 32 bit value
        'e_andi.':      'unsigned_sci8',           # SCI8: "unsigned" 32 bit value
        'andi.':        'unsigned_d',              # D:    unsigned 16 bit value
        'andis.':       'unsigned_d',              # D:    unsigned 16 bit value

        # Shift Immediate
        'se_srwi':      'unsigned_im5',            # IM5:  unsigned 5 bit value
        'se_srawi':     'unsigned_im5',            # IM5:  unsigned 5 bit value
        'se_slwi':      'unsigned_im5',            # IM5:  unsigned 5 bit value
        'e_srwi':       'unsigned_x',              # X:    unsigned 5 bit value
        'e_srwi.':      'unsigned_x',              # X:    unsigned 5 bit value
        'e_slwi':       'unsigned_x',              # X:    unsigned 5 bit value
        'e_rlwi':       'unsigned_x',              # X:    unsigned 5 bit value
        'e_rlwimi':     'unsigned_m',              # M:    3 unsigned 5 bit values
        'e_rlwinm':     'unsigned_m',              # M:    3 unsigned 5 bit values
        'rlwimi':       'unsigned_m',              # M:    3 unsigned 5 bit values
        'rlwinm':       'unsigned_m',              # M:    3 unsigned 5 bit values
        'rlwinm.':      'unsigned_m',              # M:    3 unsigned 5 bit values
        'rlwnm':        'unsigned_m_reg',          # M:    3 unsigned 5 bit values
        'rlwnm.':       'unsigned_m_reg',          # M:    3 unsigned 5 bit values
        'srawi':        'unsigned_x',              # X:    unsigned 5 bit value
        'srawi.':       'unsigned_x',              # X:    unsigned 5 bit value
        'sradi':        'unsigned_x_dw',           # X:    unsigned 6 bit value
        'sradi.':       'unsigned_x_dw',           # X:    unsigned 6 bit value
        'rldimi':       'unsigned_md',             # MD:   2 unsigned 6 bit values
        'rldimi.':      'unsigned_md',             # MD:   2 unsigned 6 bit values
        'rldicl':       'unsigned_md',             # MD:   2 unsigned 6 bit values
        'rldicl.':      'unsigned_md',             # MD:   2 unsigned 6 bit values
        'rldic':        'unsigned_md',             # MD:   2 unsigned 6 bit values
        'rldic.':       'unsigned_md',             # MD:   2 unsigned 6 bit values
        'rldicr':       'unsigned_md',             # MD:   2 unsigned 6 bit values
        'rldicr.':      'unsigned_md',             # MD:   2 unsigned 6 bit values

        # Bit Manipulate Immediate
        'se_bmaski':    'unsigned_im5',            # IM5:  unsigned 5 bit value
        'se_bclri':     'unsigned_im5',            # IM5:  unsigned 5 bit value
        'se_bseti':     'unsigned_im5',            # IM5:  unsigned 5 bit value
        'se_btsti':     'unsigned_im5',            # IM5:  unsigned 5 bit value
        'se_bgeni':     'unsigned_im5',            # IM5:  unsigned 5 bit value

        # Compare Immediate
        'se_cmpli':     'unsigned_oim5',           # OIM5: unsigned 5 bit value
        'se_cmpi':      'unsigned_im5',            # IM5:  unsigned 5 bit value
        'e_cmpli':      'unsigned_sci8',           # SCI8: "unsigned" 32 bit value
        'e_cmpi':       'signed_sci8',             # SCI8: "signed" 32 bit value
        'e_cmpl16i':    'unsigned_i16a',           # IA16 (same as I16A?): unsigned 16 bit value
        'e_cmp16i':     'signed_i16a',             # IA16 (same as I16A?): signed 16 bit value
        'cmpli':        'unsigned_d',              # D:    unsigned 16 bit value
        'cmpi':         'signed_d',                # D:    signed 16 bit value
        'cmplwi':       'unsigned_d',              # D:    unsigned 16 bit value
        'cmpwi':        'signed_d',                # D:    signed 16 bit value
        'cmpldi':       'unsigned_d',              # D:    unsigned 16 bit value (alias of cmpli)
        'cmpdi':        'signed_d',                # D:    signed 16 bit value (alias of cmpi)

        # Trap Immediate
        'twui':         'signed_d_full',           # D:    signed 16 bit value
        'tw':           'x_full',                  # X
        'twu':          'x_full',                  # X
        'twi':          'signed_d_full',           # D:    signed 16 bit value
        'trap':         'signed_d_full',           # D:    signed 16 bit value
        'twgti':        'signed_d',                # D:    signed 16 bit value
        'twlgti':       'signed_d',                # D:    signed 16 bit value
        'twnei':        'signed_d',                # D:    signed 16 bit value
        'tdi':          'signed_d',                # D:    signed 16 bit value
        'tdgti':        'signed_d',                # D:    signed 16 bit value
        'tdlgti':       'signed_d',                # D:    signed 16 bit value
        'tdnei':        'signed_d',                # D:    signed 16 bit value

        # Add Immediate
        'se_addi':      'unsigned_oim5',           # OIM5: unsigned 5 bit value
        'e_add16i':     'signed_d',                # D:    signed 16 bit value
        'e_add2i.':     'signed_i16a',             # I16A: signed 16 bit value
        'e_add2is':     'unsigned_i16a',           # I16A: unsigned 16 bit value
        'e_addi':       'unsigned_sci8',           # SCI8: "unsigned" 32 bit value
        'e_addi.':      'unsigned_sci8',           # SCI8: "unsigned" 32 bit value
        'addi':         'signed_d',                # D:    signed 16 bit value
        'addis':        'signed_d',                # D:    signed 16 bit value
        'addic':        'signed_d',                # D:    signed 16 bit value
        'addic.':       'signed_d',                # D:    signed 16 bit value

        # Multiply Immediate
        'e_mulli':      'signed_sci8',             # SCI8: "signed" 32 bit value
        'e_mull2i':     'signed_i16a',             # I16A: signed 16 bit value
        'mulli':        'signed_d',                # D:    signed 16 bit value

        # Subtract Immediate
        'se_subi':      'unsigned_oim5',           # OIM5: unsigned 5 bit value
        'se_subi.':     'unsigned_oim5',           # OIM5: unsigned 5 bit value
        'e_subfic':     'unsigned_sci8',           # SCI8: "unsigned" 32 bit value
        'e_subfic.':    'unsigned_sci8',           # SCI8: "unsigned" 32 bit value
        'subfic':       'signed_d',                # D:    signed 16 bit value

        # Move To/From SPR
        'mtspr':        'xfx_spr',                 # XFX: Special Purpose Register
        'mfspr':        'xfx_spr',                 # XFX: Special Purpose Register
        'mttmr':        'xfx_tmr',                 # XFX: Thread Management Register
        'mftmr':        'xfx_tmr',                 # XFX: Thread Management Register
        'mtpmr':        'xfx_pmr',                 # XFX: Performance Monitor Register
        'mfpmr':        'xfx_pmr',                 # XFX: Performance Monitor Register

        # Data cache
        'dcbtst':       'dcbt',                    # X:   5 bit unsigned field
        'dcbt':         'dcbt',                    # X:   5 bit unsigned field

        # Other
        'eieio':        'xfx_field1',              # XFX: special MO flag
        'mbar':         'xfx_field1',              # XFX: special MO flag
        'wrteei':       'wrteei',                  # X:   special E flag
        'mtcr':         'mtcrf',                   # XFX: special CRM flag values
        'mtcrf':        'mtcrf',                   # XFX: special CRM flag values
        'mfcrf':        'mtcrf',                   # XFX: special CRM flag values
        'mtocrf':       'mtcrf',                   # XFX: special CRM flag values
        'mfocrf':       'mtcrf',                   # XFX: special CRM flag values
        'mtfsf':        'xfx_field2',              # XFX
        'mffsf':        'xfx_field2',              # XFX
        'tlbsx':        'x_2reg_r0_handling',      # X
        'tlbsx.':       'x_2reg_r0_handling',      # X
        'tlbsrx.':      'x_2reg_r0_handling',      # X
        'tlbivax':      'x_2reg_r0_handling',      # X
        'sync':         'sync',                    # X:  special sync format
        'msync':        'sync',                    # X:  special sync format
        'lwsync':       'sync',                    # X:  special sync format
        'wait':         'wait',                    # X:  special wait format

        # altivec
        'vspltisb':     'signed_vx',               # VX: signed 5 bit value
        'vspltish':     'signed_vx',               # VX: signed 5 bit value
        'vspltisw':     'signed_vx',               # VX: signed 5 bit value
    }

    def __init__(self, tokens, line_nr):
        self._line_nr = line_nr
        self._tokens = tokens
        self.data = None
        self.op = None
        self.args = []

        for tok in tokens:
            if tok.type == 'BYTES':
                self.data = tok
            elif tok.type == 'ASM':
                self.op = tok
            elif tok.type == 'CONDITION':
                cond_str = re.sub( r'4 ?\* ?(cr[0-7]) ?\+ ?(lt|gt|eq|so|un)\b', r'\1.\2', tok.value)
                self.args.append(lst_parser.Token('CONDITION', tok, cond_str, tok.column))
            elif tok.type in ['REG', 'INDIRECT_REF', 'DEC_CONST', 'HEX_CONST']:
                self.args.append(tok)
            elif tok.type in ['LABEL', 'LABEL_MATH']:
                self.args.append(lst_parser.Token('TBD', tok, 'TBD', tok.column))

        # Some instructions tend to be decoded incorrectly by IDA, but not in 
        # a way that is dramatically wrong enough to require "fixing"
        if self.op.value in ['lbarx', 'lharx', 'lwarx', 'ldarx'] and len(self.args) > 3:
            self.args = self.args[:3]

        if self.op.value == 'tlbre' and len(self.args) > 0:
            # tlbre should not have parameters
            self.args = []

        if self.op.value in ['mtcrf'] and len(self.args) == 1:
            self.args = [lst_parser.Token('TBD', tok, 'TBD', tok.column)] + self.args[:]

        if self.op.value in ['dcbt', 'dcbtst'] and len(self.args) == 2:
            self.args = [lst_parser.Token('TBD', tok, 'TBD', tok.column)] + self.args[:]

        # Some instructions don't need fixing or re-evaluating
        dont_fix_instrs = [
                'lvx', 'lvsr', 'lvsl',
                'lxl',
                'stvx',
                'lbarx', 'lharx', 'lwarx', 'ldarx',
                'stbcx.', 'sthcx.', 'stwcx.', 'stdcx.',
                'lhbrx', 'lwbrx', 'ldbrx',
                'sthbrx', 'stwbrx', 'stwdrx',
                'ldx', 'lbzx',
                'lhau',
                'dcbst', 'dcbf', 'dcbz',
                'icbi',
                'tlbilx', 'tlbre',
        ]
        if self.op.value not in dont_fix_instrs:
            self.fix()

    def fix(self):
        # IDA listings use some incorrect mnemononics
        rename_mapping = {
            'mfsprg':      (None, 'mfspr'),
            'mtsprg':      (None, 'mtspr'),

            # 'eieio' was the old PPC instruction, it should now be called 'mbar'
            'eieio':       (None, 'mbar'),
            'msync':       (None, 'sync'),
            'lwsync':      (None, 'sync'),

            # Generic PPC forms into forms I recognize better
            'twu':         (None, 'tw'),
            'twui':        (None, 'twi'),
            'trap':        ( (0x0C000000, 'twi'),
                             (0x7C000000, 'tw') ),

            # There is no tlbsx. instruction
            'tlbsx':       (None, 'tlbsx'),
            'tlbsx.':      (None, 'tlbsx'),

            # These new ISR load/store instrucions are misnamed in IDA
            'e_lmvgprw':   (None, 'e_ldmvgprw'),
            'e_lmvsprw':   (None, 'e_ldmvsprw'),
            'e_lmvsrrw':   (None, 'e_ldmvsrrw'),
            'e_lmvcsrrw':  (None, 'e_ldmvcsrrw'),
            'e_lmvdsrrw':  (None, 'e_ldmvdsrrw'),

            # These VLE instructions should not be translated eventually.
            'e_srwi':      ( (0x74000000, 'e_rlwinm') ),
            'e_extrwi':    (None, 'e_rlwinm'),
            'e_extlwi':    (None, 'e_rlwinm'),
            'e_clrlslwi':  (None, 'e_rlwinm'),
            'e_clrlwi':    (None, 'e_rlwinm'),
            'e_insrwi':    (None, 'e_rlwimi'),
            'e_clrrwi':    (None, 'e_rlwinm'),
            'e_rotrwi':    (None, 'e_rlwinm'),
            'e_rotlwi':    (None, 'e_rlwinm'),
            'mtcr':        (None, 'mtcrf'),

            # These PPC instructions should not be translated eventually.
            'rotldi':      (None, 'rldicl'),
            'rotrdi':      (None, 'rldicl'),
            'sldi':        (None, 'rldicr'),
            'srwi':        (None, 'rlwinm'),
            'srdi':        (None, 'rldicl'),
            'extrwi':      (None, 'rlwinm'),
            'extlwi':      (None, 'rlwinm'),
            'clrlslwi':    (None, 'rlwinm'),
            'clrlwi':      (None, 'rlwinm'),
            'slwi':        (None, 'rlwinm'),
            'insrwi':      (None, 'rlwimi'),
            'insrdi':      (None, 'rldimi'),
            'clrrwi':      (None, 'rlwinm'),
            'rotrwi':      (None, 'rlwinm'),
            'rotlwi':      (None, 'rlwinm'),
            'rotlw':       (None, 'rlwnm'),
            'inslwi':      (None, 'rlwimi'),
            'clrrdi':      (None, 'rldicr'),
            'clrldi':      (None, 'rldicl'),
            'extldi':      (None, 'rldicr'),
            'extrdi':      (None, 'rldicl'),
            'clrlsldi':    (None, 'rldic'),
        }

        cr0_prepend = [
                #'cmpw', 'cmpwi', 'cmplw', 'cmplwi', 'cmpli', 'cmpl', 'cmp', 'cmpi'
                'e_bge', 'e_ble', 'e_bne', 'e_beq', 'e_bgt', 'e_blt',
                'bge', 'ble', 'bne', 'beq', 'bgt', 'blt',
                'bgea', 'blea', 'bnea', 'beqa', 'bgta', 'blta',
                'bgel', 'blel', 'bnel', 'beql', 'bgtl', 'bltl',
                'bgela', 'blela', 'bnela', 'beqla', 'bgtla', 'bltla',
                'bgelr', 'blelr', 'bnelr', 'beqlr', 'bgtlr', 'bltlr',
                'bgelrl', 'blelrl', 'bnelrl', 'beqlrl', 'bgtlrl', 'bltlrl',
                'bgectr', 'blectr', 'bnectr', 'beqctr', 'bgtctr', 'bltctr',
                'bgectrl', 'blectrl', 'bnectrl', 'beqctrl', 'bgtctrl', 'bltctrl',
        ]

        cr0_append = [
        ]

        op, cr = (self.op.value[:-1], self.op.value[-1]) if self.op.value[-1] == '.' else (self.op.value, '')
        if op in rename_mapping:
            if self.op.value in rename_mapping:
                op = self.op.value
                cr = ''

            new_op = None
            if rename_mapping[op][0] is None:
                new_op = rename_mapping[op][1]
            else:
                op_bytes = self.data.value & 0xFC000000
                matches = [ m[1] for m in rename_mapping[op] if m[0] == op_bytes ]
                if len(matches) >= 1:
                    new_op = matches[0]

            if new_op is not None:
                self.op = lst_parser.Token('ASM', self.op.match, new_op + cr, self.op.column)

                # If this is 'or', duplicate the last register
                if new_op in ['or', 'or.']:
                    last_arg = self.args[-1]
                    self.args.append(last_arg)

        # Some instructions need to be forced to re-evaluate the operands
        args_to_fix = [ a for a in self.args if a.type in ['TBD', 'DEC_CONST', 'HEX_CONST'] ]
        if self.op.value in ['rlwnm', 'ori', 'rlwnm'] and len(args_to_fix) == 0:
            self.args.append(lst_parser.Token('TBD', None, 'TBD', None))
        
        if self.op.value in ['mtcrf'] and len(args_to_fix) == 0:
            self.args = [lst_parser.Token('TBD', None, 'TBD', None)] + self.args[:]

        # Some instructions need to be completely re-generated
        regen_ops = [
            'wait',
            'mbar',
            'bc', 'bcl',
            'tlbsx', 'tlbsx.', 'tlbsrx.', 'tlbivax',
            'sync',
            'tw', 'twi',
        ]
        if self.op.value in regen_ops:
            self.args = [lst_parser.Token('TBD', None, 'TBD', None)]

        fixed_args = []
        changed = False
        for arg in self.args:
            # I can't figure out a cleaner way to handle "twi" than this
            if (self.op.value == 'twi' and arg.type == 'TBD') or \
                    (self.op.value != 'twi' and arg.type in ['TBD', 'DEC_CONST', 'HEX_CONST']):
                if self.op.value in ppc_instr.Instructions and not changed:
                    changed = True
                    new_arg = getattr(self, ppc_instr.Instructions[self.op.value])(self.data.value)
                    if isinstance(new_arg, list):
                        fixed_args.extend(new_arg)
                    else:
                        fixed_args.append(new_arg)
                elif not changed:
                    err = '{} (@ {}) needs fixing ({})'.format(self.op.value, self._line_nr, self._tokens)
                    raise NotImplementedError(err)
            else:
                fixed_args.append(arg)

        if self.op.value in cr0_prepend:
            if len(self.args) == 0:
                fixed_args.append(lst_parser.Token('REG', None, 'cr0', None))
            elif self.args[0].match[0:2] != 'cr':
                fixed_args.insert(0, lst_parser.Token('REG', None, 'cr0', None))

        if self.op.value in cr0_append and not self.args[-1].match[0:2] == 'cr':
            fixed_args.append(lst_parser.Token('REG', None, 'cr0', None))

        # Some move/to SPR instructions are missing the SPR #
        # (I'm not sure if we should translate these aliases or not)
        spr_asm = {
            'mfxer':       'mfspr',
            'mtxer':       'mtspr',
            'mflr':        'mfspr',
            'mtlr':        'mtspr',
            'mfctr':       'mfspr',
            'mtctr':       'mtspr',
            'mfsrr0':      'mfspr',
            'mtsrr0':      'mtspr',
            'mfsrr1':      'mfspr',
            'mtsrr1':      'mtspr',
            'mftb':        'mfspr',
            'mftbu':       'mfspr',
            'mfdec':       'mfspr',
            'mtdec':       'mtspr',
            'mfsprg0':     'mfspr',
            'mtsprg0':     'mtspr',
            'mfsprg1':     'mfspr',
            'mtsprg1':     'mtspr',
            'mfsprg2':     'mfspr',
            'mtsprg2':     'mtspr',
            'mfsprg3':     'mfspr',
            'mtsprg3':     'mtspr',
            'mfpvr':       'mfspr',
            'mtpvr':       'mtspr',
            'mfvtb':       'mfspr',
            'mtvtb':       'mtspr',
        }

        # The same 3 letter prefixes work for all types of conditional branches:
        #   bc
        #   bcl
        #   bca
        #   bcla
        #   bcctr
        #   bcctrl
        #   bclr
        #   bclrl
        rename_branch_instrs = {
            'blt': ('bt', '.lt'),
            'ble': ('bf', '.gt'),
            'beq': ('bt', '.eq'),
            'bge': ('bf', '.lt'),
            'bgt': ('bt', '.gt'),
            'bnl': ('bf', '.gt'),
            'bne': ('bf', '.eq'),
            'bng': ('bf', '.gt'),
            'bso': ('bt', '.so'),
            'bns': ('bf', '.so'),
            'bun': ('bt', '.so'),
            'bnu': ('bt', '.so'),
        }
        if self.op.value in spr_asm:
            new_op = lst_parser.Token('ASM', self.op.match, spr_asm[self.op.value], self.op.column)
            self.op = new_op

            if self.op.value in ['mfspr', 'mfpmr', 'mftmr'] and \
                    fixed_args[-1].type not in ['SPR', 'HEX_CONST', 'DEC_CONST']:
                new_arg = getattr(self, ppc_instr.Instructions[self.op.value])(self.data.value)
                fixed_args.append(new_arg)

            if self.op.value in ['mtspr', 'mtpmr', 'mttmr'] and \
                    fixed_args[0].type not in ['SPR', 'HEX_CONST', 'DEC_CONST']:
                new_arg = getattr(self, ppc_instr.Instructions[self.op.value])(self.data.value)
                fixed_args.insert(0, new_arg)

        elif self.op.value[0:3] in rename_branch_instrs:
            mods = rename_branch_instrs[self.op.value[0:3]]
            instr_rem = self.op.value[3:]
            new_op = lst_parser.Token('ASM', self.op.match, mods[0] + instr_rem, self.op.column)
            self.op = new_op

            fixed_cr_arg = lst_parser.Token(fixed_args[0].type, fixed_args[0].type, fixed_args[0].value + mods[1], fixed_args[0].column)
            fixed_args[0] = fixed_cr_arg
        elif self.op.value in ['bc', 'bcl'] and len(fixed_args) == 3 and fixed_args[0].value == 0x14:
            # Special case: a branch conditional with flags indicating "don't 
            # decrement and ignore the condition flags"
            fixed_args = fixed_args[-1:]

        self.args = fixed_args

    def __repr__(self):
        arg_list = ''
        if self.args:
            if self.args[-1].type == 'INDIRECT_REF':
                arg_list = ' ' + ppc_instr._str_arg_list(self.args[:-1]) + self.args[-1].value
            else:
                arg_list = ' ' + ppc_instr._str_arg_list(self.args)

        return str((self.data.match, self.op.value + arg_list))

    def __str__(self):
        arg_list = ''
        if self.args:
            if self.args[-1].type == 'INDIRECT_REF':
                arg_list = ' ' + ppc_instr._str_arg_list(self.args[:-1]) + self.args[-1].value
            else:
                arg_list = ' ' + ppc_instr._str_arg_list(self.args)

        #if self.op.value in ['tdi', 'vaddubm']:
        #    fmt = '#{0.data.match: <8} {0.op.value}{1}'
        #else:
        fmt = '{0.data.match: <8} {0.op.value}{1}'
        return fmt.format(self, arg_list)

    @classmethod
    def _str_arg(cls, arg):
        if isinstance(arg.value, str):
            if len(arg.value) == 6 and arg.value[0:4] == "cr0.":
                return arg.value[4:]
            return arg.value
        return hex(arg.value)

    @classmethod
    def _str_arg_list(cls, arg_list):
        return ','.join([cls._str_arg(a) for a in arg_list])

    @classmethod
    def _dec_token(cls, val):
        return lst_parser.Token('DEC_CONST', str(val), val, None)

    @classmethod
    def _hex_token(cls, val):
        return lst_parser.Token('HEX_CONST', hex(val), val, None)

    @classmethod
    def signed_bd8(cls, data):
        sign = 0x0080
        mask = 0x007F
        val = ((data & mask) - (data & sign)) << 1
        return cls._dec_token(val)

    @classmethod
    def signed_bd15(cls, data):
        sign = 0x00008000
        mask = 0x00007FFE
        val = (data & mask) - (data & sign)
        return cls._dec_token(val)

    @classmethod
    def signed_bd24(cls, data):
        sign = 0x01000000
        mask = 0x00FFFFFE
        val = (data & mask) - (data & sign)
        return cls._dec_token(val)

    @classmethod
    def signed_i(cls, data):
        sign = 0x02000000
        mask = 0x01FFFFFC
        val = (data & mask) - (data & sign)
        return cls._dec_token(val)

    @classmethod
    def signed_b(cls, data):
        tgt_sign = 0x00008000
        tgt_mask = 0x00007FFC
        tgt = (data & tgt_mask) - (data & tgt_sign)

        return cls._dec_token(tgt)

    @classmethod
    def signed_b_full(cls, data):
        # For non-simplified branch conditionals, grab all fields
        flags_mask = 0x03E00000
        flags = (data & flags_mask) >> 21

        cr_reg  = (data & 0x001C0000) >> 18
        cr_bits = (data & 0x00030000) >> 16
        if cr_bits == 0b00:
            cr = 'cr{}.lt'.format(cr_reg)
        elif cr_bits == 0b01:
            cr = 'cr{}.gt'.format(cr_reg)
        elif cr_bits == 0b10:
            cr = 'cr{}.eq'.format(cr_reg)
        elif cr_bits == 0b11:
            cr = 'cr{}.so'.format(cr_reg)

        tgt_sign = 0x00008000
        tgt_mask = 0x00007FFC
        tgt = (data & tgt_mask) - (data & tgt_sign)

        cr_tok = lst_parser.Token('CONDITION', cr, cr, None)
        return [cls._dec_token(flags), cr_tok, cls._dec_token(tgt)]

    @classmethod
    def unsigned_sd4_word_addr(cls, data):
        mask = 0x0F00
        val = (data & mask) >> 6 # val >> 8 then << 2
        return cls._dec_token(val)

    @classmethod
    def unsigned_sd4_half_addr(cls, data):
        mask = 0x0F00
        val = (data & mask) >> 7 # val >> 8 then << 1
        return cls._dec_token(val)

    @classmethod
    def unsigned_sd4_byte_addr(cls, data):
        mask = 0x0F00
        val = (data & mask) >> 8
        return cls._dec_token(val)

    @classmethod
    def signed_d8(cls, data):
        sign = 0x00000080
        mask = 0x0000007F
        val = (data & mask) - (data & sign)
        return cls._dec_token(val)

    @classmethod
    def signed_ds(cls, data):
        sign = 0x00008000
        mask = 0x00007FFC # This format takes bits 16-29 then left shifts by 2
                          # bits, which is the same as just masking off the
                          # lower 2 bits
        val = (data & mask) - (data & sign)
        return cls._dec_token(val)

    @classmethod
    def signed_d(cls, data):
        sign = 0x00008000
        mask = 0x00007FFF
        val = (data & mask) - (data & sign)
        return cls._dec_token(val)

    @classmethod
    def signed_d_full(cls, data):
        mask_TO = 0x03E00000
        mask_rA = 0x001F0000

        sign = 0x00008000
        mask = 0x00007FFF

        TO = (data & mask_TO) >> 21
        rA = (data & mask_rA) >> 16
        val = (data & mask) - (data & sign)

        reg_str ='r{}'.format(rA)
        return [cls._dec_token(TO),
                lst_parser.Token('REG', reg_str, reg_str, None),
                cls._dec_token(val)]

    @classmethod
    def x_full(cls, data):
        mask_TO = 0x03E00000
        mask_rA = 0x001F0000
        mask_rB = 0x0000F800

        TO = (data & mask_TO) >> 21
        rA = (data & mask_rA) >> 16
        rB = (data & mask_rB) >> 11

        rA_str ='r{}'.format(rA)
        rB_str ='r{}'.format(rB)
        return [cls._dec_token(TO),
                lst_parser.Token('REG', rA_str, rA_str, None),
                lst_parser.Token('REG', rB_str, rB_str, None)]

    @classmethod
    def signed_d_handle_r0(cls, data):
        sign = 0x00008000
        mask = 0x00007FFF
        val = (data & mask) - (data & sign)

        reg_mask = 0x001F0000
        reg = (data & reg_mask) >> 16

        if reg == 0:
            return [cls._dec_token(reg), cls._dec_token(val)]
        else:
            return cls._dec_token(val)

    @classmethod
    def unsigned_d(cls, data):
        mask = 0x0000FFFF
        val = data & mask
        return cls._hex_token(val)

    @classmethod
    def unsigned_im7(cls, data):
        mask = 0x07F0
        val = (data & mask) >> 4

        # Since this is a simple unsigned value it is most commonly used with
        # hex values
        return cls._hex_token(val)

    @classmethod
    def signed_li20(cls, data):
        mask_1 = 0x00007800
        mask_2 = 0x001F0000
        mask_3 = 0x000007FF
        up_val = (data & mask_1) << 5  # upper >> 11 then << 16
        mid_val = (data & mask_2) >> 5 # mid >> 16 then << 11
        low_val = (data & mask_3)      # no shift

        unsigned_val = up_val | mid_val | low_val

        sign = 0x00080000
        mask = 0x0007FFFF
        signed_val = (unsigned_val & mask) - (unsigned_val & sign)
        return cls._dec_token(signed_val)

    @classmethod
    def _get_i16l_imm(cls, data):
        mask_1 = 0x001F0000
        mask_2 = 0x000007FF
        up_val = (data & mask_1) >> 5  # upper >> 16 then << 11
        low_val = (data & mask_2)      # no shift
        unsigned_val = up_val | low_val
        return unsigned_val

    @classmethod
    def unsigned_i16l(cls, data):
        val = cls._get_i16l_imm(data)

        # This unsigned immediate form is most often used in logical (AND/OR)
        # operations, make the token in hex format.
        return cls._hex_token(val)

    @classmethod
    def _get_im5_imm(cls, data):
        mask = 0x01F0
        val = (data & mask) >> 4
        return val

    @classmethod
    def unsigned_im5(cls, data):
        val = cls._get_im5_imm(data)

        # Make hex tokens for logical operation operands
        return cls._hex_token(val)

    @classmethod
    def unsigned_oim5(cls, data):
        val = cls._get_im5_imm(data) + 1

        # Make since this is used in "se_addi", make this a decimal operand
        return cls._dec_token(val)

    @classmethod
    def unsigned_x(cls, data):
        mask = 0x0000F800
        val = (data & mask) >> 11

        # Make hex tokens for logical operation operands
        return cls._hex_token(val)

    @classmethod
    def unsigned_x_dw(cls, data):
        mask_1 = 0x0000F800
        mask_2 = 0x00000002
        val_1 = (data & mask_1) >> 11
        val_2 = (data & mask_2) << 4 # >> 1 then << 5
        val = val_1 | val_2

        # Make hex tokens for logical operation operands
        return cls._hex_token(val)

    @classmethod
    def unsigned_m(cls, data):
        mask_1 = 0x0000F800
        mask_2 = 0x000007C0
        mask_3 = 0x0000003E
        shift = (data & mask_1) >> 11
        mask_begin = (data & mask_2) >> 6
        mask_end = (data & mask_3) >> 1

        # Make hex tokens for logical operation operands
        return [cls._hex_token(shift), cls._hex_token(mask_begin), cls._hex_token(mask_end)]

    @classmethod
    def unsigned_m_reg(cls, data):
        mask_1 = 0x000007C0
        mask_2 = 0x0000003E
        mask_begin = (data & mask_1) >> 6
        mask_end = (data & mask_2) >> 1

        # Make hex tokens for logical operation operands
        return [cls._hex_token(mask_begin), cls._hex_token(mask_end)]

    @classmethod
    def unsigned_md(cls, data):
        sh_lower_mask = 0x0000F800
        sh_upper_mask = 0x00000002
        sh = ((data & sh_upper_mask ) << 4) | ((data & sh_lower_mask ) >> 11)

        mb_lower_mask = 0x000007C0
        mb_upper_mask = 0x00000020
        mb = (data & mb_upper_mask ) | ((data & mb_lower_mask ) >> 6)

        # Make hex tokens for logical operation operands
        return [cls._hex_token(sh), cls._hex_token(mb)]

    @classmethod
    def special_r0_handling(cls, data):
        mask = 0x001F0000
        val = (data & mask) >> 16

        if val == 0:
            return cls._dec_token(val)
        else:
            reg_str ='r{}'.format(val)
            return lst_parser.Token('REG', reg_str, reg_str, None)

    @classmethod
    def _get_sci8_imm(cls, data):
        f_mask = 0x00000400
        scl_mask = 0x00000300
        data_mask = 0x000000FF

        f = (data & f_mask) >> 10
        scl = (data & scl_mask) >> 8
        ui8 = (data & data_mask)

        fill = 0x00
        if f == 1:
            fill = 0xFF

        if scl == 0:
            val = fill << 24 | fill << 16 | fill << 8 | ui8
        elif scl == 1:
            val = fill << 24 | fill << 16 | ui8 << 8 | fill
        elif scl == 2:
            val = fill << 24 | ui8 << 16 | fill << 8 | fill
        else: # scl == 3
            val = ui8 << 24 | fill << 16 | fill << 8 | fill

        return val

    @classmethod
    def unsigned_sci8(cls, data):
        val = cls._get_sci8_imm(data)

        # The SCI8 form is used most often in mask generating instructions,
        # make this operand hex
        return cls._hex_token(val)

    @classmethod
    def signed_sci8(cls, data):
        unsigned_val = cls._get_sci8_imm(data)

        sign = 0x80000000
        mask = 0x7FFFFFFF
        signed_val = (unsigned_val & mask) - (unsigned_val & sign)

        # The "signed" SCI8 values are used in add operations, make this
        # operand decimal.
        return cls._dec_token(signed_val)

    @classmethod
    def _get_i16a_imm(cls, data):
        mask_1 = 0x03E00000
        mask_2 = 0x000007FF
        up_val = (data & mask_1) >> 10  # upper >> 21 then << 11
        low_val = (data & mask_2)       # no shift
        unsigned_val = up_val | low_val
        return unsigned_val

    @classmethod
    def signed_i16a(cls, data):
        unsigned_val = cls._get_i16a_imm(data)

        sign = 0x00100000
        mask = 0x000FFFFF
        signed_val = (unsigned_val & mask) - (unsigned_val & sign)

        # For signed values return a decimal operand
        return cls._dec_token(signed_val)

    @classmethod
    def unsigned_i16a(cls, data):
        val = cls._get_i16a_imm(data)

        # For unsigned values return a hex operand
        return cls._hex_token(val)

    @classmethod
    def signed_vx(cls, data):
        sign = 0x00100000
        mask = 0x000F0000
        val = ((data & mask) - (data & sign)) >> 16

        # For signed values return a decimal operand
        return cls._dec_token(val)

    @classmethod
    def _get_xfx_field2(cls, data):
        mask_1 = 0x0000F800
        mask_2 = 0x001F0000
        up_val = (data & mask_1) >> 6  # upper >> 11 then << 5
        low_val = (data & mask_2) >> 16 # lower >> 16
        val = up_val | low_val
        return val

    @classmethod
    def xfx_field1(cls, data):
        mask = 0x003E0000
        val = (data & mask) >> 21
        return cls._hex_token(val)

    @classmethod
    def xfx_field2(cls, data):
        val = cls._get_xfx_field2(data)
        return cls._hex_token(val)

    @classmethod
    def x_2reg_r0_handling(cls, data):
        mask_rA = 0x001F0000
        mask_rB = 0x0000F800

        rA = (data & mask_rA) >> 16
        rB = (data & mask_rB) >> 11

        if rA == 0:
            rB_str ='r{}'.format(rB)
            return [cls._dec_token(rA),
                    lst_parser.Token('REG', rB_str, rB_str, None)]
        else:
            rA_str ='r{}'.format(rA)
            rB_str ='r{}'.format(rB)
            return [lst_parser.Token('REG', rA_str, rA_str, None),
                    lst_parser.Token('REG', rB_str, rB_str, None)]
    @classmethod
    def sync(cls, data):
        mask_l = 0x00600000
        mask_e = 0x00070000

        l = (data & mask_l) >> 21
        e = (data & mask_e) >> 16

        return [cls._dec_token(l), cls._dec_token(e)]

    @classmethod
    def wait(cls, data):
        mask_WC = 0x00600000
        mask_WH = 0x00100000

        WC = (data & mask_WC) >> 21
        WH = (data & mask_WH) >> 20

        return [cls._dec_token(WC), cls._dec_token(WH)]

    @classmethod
    def xfx_spr(cls, data):
        val = cls._get_xfx_field2(data)
        spr_to_str_map = {
            1: 'XER',
            8: 'LR',
            9: 'CTR',
            22: 'DEC',
            26: 'SRR0',
            27: 'SRR1',
            48: 'PID',
            54: 'DECAR',
            56: 'LPER',
            57: 'LPERU',
            58: 'CSRR0',
            59: 'CSRR1',
            61: 'DEAR',
            62: 'ESR',
            63: 'IVPR',
            256: 'USPRG0',
            259: 'USPRG3',
            260: 'USPRG4',
            261: 'USPRG5',
            262: 'USPRG6',
            263: 'USPRG7',
            268: 'TB',
            269: 'TBU',
            272: 'SPRG0',
            273: 'SPRG1',
            274: 'SPRG2',
            275: 'SPRG3',
            276: 'SPRG4',
            277: 'SPRG5',
            278: 'SPRG6',
            279: 'SPRG7',
            283: 'CIR',
            284: 'TBL_HYP',
            285: 'TBU_HYP',
            286: 'PIR',
            287: 'PVR',
            304: 'DBSR',
            306: 'DBSRWR',
            307: 'EPCR',
            308: 'DBCR0',
            309: 'DBCR1',
            310: 'DBCR2',
            311: 'MSRP',
            312: 'IAC1',
            313: 'IAC2',
            314: 'IAC3',
            315: 'IAC4',
            316: 'DAC1',
            317: 'DAC2',
            318: 'DVC1',
            319: 'DVC2',
            336: 'TSR',
            338: 'LPIDR',
            339: 'MAS5',
            340: 'TCR',
            341: 'MAS8',
            342: 'LRATCFG',
            343: 'LRATPS',
            344: 'TLB0PS',
            345: 'TLB1PS',
            346: 'TLB2PS',
            347: 'TLB3PS',
            348: 'MAS5_MAS6',
            349: 'MAS8_MAS1',
            350: 'EPTCFG',
            368: 'GSPRG0',
            369: 'GSPRG1',
            370: 'GSPRG2',
            371: 'GSPRG3',
            372: 'MAS7_MAS3',
            373: 'MAS0_MAS1',
            378: 'GSRR0',
            379: 'GSRR1',
            380: 'GEPR',
            381: 'GDEAR',
            382: 'GPIR',
            383: 'GESR',
            400: 'IVOR0',
            401: 'IVOR1',
            402: 'IVOR2',
            403: 'IVOR3',
            404: 'IVOR4',
            405: 'IVOR5',
            406: 'IVOR6',
            407: 'IVOR7',
            408: 'IVOR8',
            409: 'IVOR9',
            410: 'IVOR10',
            411: 'IVOR11',
            412: 'IVOR12',
            413: 'IVOR13',
            414: 'IVOR14',
            415: 'IVOR15',
            432: 'IVOR38',
            433: 'IVOR39',
            434: 'IVOR40',
            435: 'IVOR41',
            436: 'IVOR42',
            437: 'TENSR',
            438: 'TENS',
            439: 'TENC',
            440: 'GIVOR2',
            441: 'GIVOR3',
            442: 'GIVOR4',
            443: 'GIVOR8',
            444: 'GIVOR13',
            445: 'GIVOR14',
            446: 'TIR',
            447: 'GIVPR',
            464: 'GIVOR35',
            512: 'SPEFSCR',
            515: 'L1CFG0',
            516: 'L1CFG1',
            517: 'NPIDR5',
            519: 'L2CFG0',
            526: 'ATBL',
            527: 'ATBU',
            528: 'IVOR32',
            529: 'IVOR33',
            530: 'IVOR34',
            531: 'IVOR35',
            532: 'IVOR36',
            533: 'IVOR37',
            561: 'DBCR3',
            569: 'DBERC0',
            569: 'MCARU',
            570: 'MCSRR0',
            571: 'MCSRR1',
            572: 'MCSR',
            573: 'MCAR',
            574: 'DSRR0',
            575: 'DSRR1',
            576: 'DDAM',
            601: 'DVC1U',
            602: 'DVC2U',
            604: 'SPRG8',
            605: 'SPRG9',
            606: 'L1CSR2',
            607: 'L1CSR3',
            624: 'MAS0',
            625: 'MAS1',
            626: 'MAS2',
            627: 'MAS3',
            628: 'MAS4',
            630: 'MAS6',
            633: 'PID1',
            634: 'PID2',
            637: 'MCARUA',
            638: 'EDBRAC0',
            688: 'TLB0CFG',
            689: 'TLB1CFG',
            690: 'TLB2CFG',
            691: 'TLB3CFG',
            696: 'CDCSR0',
            700: 'DBRR0',
            702: 'EPR',
            720: 'L2ERRINTEN',
            721: 'L2ERRATTR',
            722: 'L2ERRADDR',
            723: 'L2ERREADDR',
            724: 'L2ERRCTL',
            725: 'L2ERRDIS',
            730: 'EPIDR',
            731: 'INTLEVEL',
            732: 'GEPIDR',
            733: 'GINTLEVEL',
            898: 'PPR32',
            944: 'MAS7',
            947: 'EPLC',
            948: 'EPSC',
            959: 'L1FINV1',
            975: 'DEVENT',
            983: 'NSPD',
            984: 'NSPC',
            985: 'L2ERRINJHI',
            986: 'L2ERRINJLO',
            987: 'L2ERRINJCTL',
            988: 'L2CAPTDATAHI',
            989: 'L2CAPTDATALO',
            990: 'L2CAPTECC',
            991: 'L2ERRDET',
            1008: 'HID0',
            1009: 'HID1',
            1010: 'L1CSR0',
            1011: 'L1CSR1',
            1012: 'MMUCSR0',
            1013: 'BUCSR',
            1015: 'MMUCFG',
            1016: 'L1FINV0',
            1017: 'L2CSR0',
            1018: 'L2CSR1',
            1019: 'PWRMGTCR0',
            1022: 'SCCSRBAR',
            1023: 'SVR',
        }

        if val in spr_to_str_map:
            return lst_parser.Token('SPR', hex(val), spr_to_str_map[val], None)
        else:
            return lst_parser.Token('HEX_CONST', hex(val), val, None)

    @classmethod
    def xfx_tmr(cls, data):
        val = cls._get_xfx_field2(data)
        tmr_to_str_map = {
            289: 'IMSR1',
            290: 'IMSR2',
            291: 'IMSR3',
            292: 'IMSR4',
            293: 'IMSR5',
            294: 'IMSR6',
            295: 'IMSR7',
            296: 'IMSR8',
            297: 'IMSR9',
            298: 'IMSR10',
            299: 'IMSR11',
            300: 'IMSR12',
            301: 'IMSR13',
            302: 'IMSR14',
            303: 'IMSR15',
            304: 'IMSR16',
            305: 'IMSR17',
            306: 'IMSR18',
            307: 'IMSR19',
            308: 'IMSR20',
            309: 'IMSR21',
            310: 'IMSR22',
            311: 'IMSR23',
            312: 'IMSR24',
            313: 'IMSR25',
            314: 'IMSR26',
            315: 'IMSR27',
            316: 'IMSR28',
            317: 'IMSR29',
            318: 'IMSR30',
            319: 'IMSR31',
            320: 'INIA0',
            321: 'INIA1',
            322: 'INIA2',
            323: 'INIA3',
            324: 'INIA4',
            325: 'INIA5',
            326: 'INIA6',
            327: 'INIA7',
            328: 'INIA8',
            329: 'INIA9',
            330: 'INIA10',
            331: 'INIA11',
            332: 'INIA12',
            333: 'INIA13',
            334: 'INIA14',
            335: 'INIA15',
            336: 'INIA16',
            337: 'INIA17',
            338: 'INIA18',
            339: 'INIA19',
            340: 'INIA20',
            341: 'INIA21',
            342: 'INIA22',
            343: 'INIA23',
            344: 'INIA24',
            345: 'INIA25',
            346: 'INIA26',
            347: 'INIA27',
            348: 'INIA28',
            349: 'INIA29',
            350: 'INIA30',
            351: 'INIA31',
        }

        if val in tmr_to_str_map:
            return lst_parser.Token('SPR', hex(val), tmr_to_str_map[val], None)
        else:
            return lst_parser.Token('HEX_CONST', hex(val), val, None)

    @classmethod
    def xfx_pmr(cls, data):
        val = cls._get_xfx_field2(data)
        pmr_to_str_map = {
            0: 'UPMC0',
            1: 'UPMC1',
            2: 'UPMC2',
            3: 'UPMC3',
            4: 'UPMC4',
            5: 'UPMC5',
            16: 'PMC0',
            17: 'PMC1',
            18: 'PMC2',
            19: 'PMC3',
            20: 'PMC4',
            21: 'PMC5',
            128: 'UPMLCA0',
            129: 'UPMLCA1',
            130: 'UPMLCA2',
            131: 'UPMLCA3',
            132: 'UPMLCA4',
            133: 'UPMLCA5',
            144: 'PMLCA0',
            145: 'PMLCA1',
            146: 'PMLCA2',
            147: 'PMLCA3',
            148: 'PMLCA4',
            149: 'PMLCA5',
            256: 'UPMLCB0',
            257: 'UPMLCB1',
            258: 'UPMLCB2',
            259: 'UPMLCB3',
            260: 'UPMLCB4',
            261: 'UPMLCB5',
            272: 'PMLCB0',
            273: 'PMLCB1',
            274: 'PMLCB2',
            275: 'PMLCB3',
            276: 'PMLCB4',
            277: 'PMLCB5',
            384: 'UPMGC0',
            400: 'PMGC0',
        }

        if val in pmr_to_str_map:
            return lst_parser.Token('SPR', hex(val), pmr_to_str_map[val], None)
        else:
            return lst_parser.Token('HEX_CONST', hex(val), val, None)

    @classmethod
    def wrteei(cls, data):
        mask = 0x00008000
        val = (data & mask) >> 15
        return cls._dec_token(val)

    @classmethod
    def mtcrf(cls, data):
        mask = 0x000FF000
        val = (data & mask) >> 12
        return cls._hex_token(val)

    @classmethod
    def dcbt(cls, data):
        mask = 0x03E00000
        val = (data & mask) >> 21

        rA_mask = 0x001F0000
        rA = (data & rA_mask) >> 16

        if rA == 0:
            return [cls._hex_token(val), cls._hex_token(rA)]
        else:
            return cls._hex_token(val)


def parse(lst_lines):
    parser = lst_parser()
    instructions = []

    for line_nr, line in enumerate(lst_lines, 1):
        tokenized = list(parser.tokenize(line.strip()))
        if [tok for tok in tokenized if tok.type == 'ASM']:
            instr = ppc_instr(tokenized, line_nr)
            instructions.append(instr)
    return instructions


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: {} <input 1> [<input 2> ... <input n>] <output file>'.format(sys.argv[0]))
        sys.exit(-1)

    input_lines = []
    for file_in in sys.argv[1:-1]:
        with open(file_in, 'r') as f:
            input_lines.extend(f.readlines())

    # turn the input lines into a set before parsing to reduce the amount of 
    # time it takes to generate the tests.
    # Then turn the results into a set to get unique instructions for testing
    unique_instructions = sorted(list(set([repr(l) for l in parse(list(set(input_lines)))])))

    if sys.argv[-1] == '-':
        for line in unique_instructions:
            print(line)
    else:
        with open(sys.argv[-1], 'w') as f:
            f.write('instructions = [\n')
            for line in unique_instructions:
                f.write('\t' + line + ',\n')
            f.write(']\n')
