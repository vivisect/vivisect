#!/usr/bin/env python3
"""
Fast VAMP Signature Generator for ELF libraries.

Generates VAMP signatures from ELF shared libraries (.so) OR static archive
libraries (.a). Static archives are the preferred source for generating
signatures that will be used to identify functions in statically-linked
binaries, because the code in .a object files matches what gets linked into
a static binary (same #ifdef code paths). Shared libraries may use different
code paths (e.g., glibc builds different implementations for shared vs static).

When a .a file is provided, the generator:
  1. Extracts each .o member from the ar archive
  2. Parses each .o as an ET_REL relocatable object
  3. Reads function bytes by section offset (section addrs are 0 in ET_REL)
  4. Masks both ELF relocations AND instruction-aware operands
  5. Aggregates signatures across all .o members in the archive

When a .so file is provided, the generator uses the original fast path:
  1. Parses the .so as ET_DYN
  2. Reads function bytes by RVA
  3. Masks instruction-aware operands (relocations are typically in .got)

Usage (static archive — preferred for static binary matching):
    python3 vamp/tools/gen_elf_sigs.py \\
        --input /usr/lib/x86_64-linux-gnu/libc.a \\
        --library glibc \\
        --version 2.39 \\
        --arch amd64 \\
        --platform linux \\
        --compiler gcc-13 \\
        --output vamp/data/glibc_2.39_x64.json

Usage (shared library — fallback when .a not available):
    python3 vamp/tools/gen_elf_sigs.py \\
        --input /lib/x86_64-linux-gnu/libc.so.6 \\
        --library glibc \\
        --version 2.39 \\
        --arch amd64 \\
        --output vamp/data/glibc_2.39_x64.json
"""

import argparse
import binascii
import hashlib
import io
import json
import os
import struct
import subprocess
import sys
import tarfile
import time

# Add vivisect to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from Elf import Elf
import envi
import envi.archs.i386 as e_i386
import envi.archs.amd64 as e_amd64
import envi.archs.aarch64 as e_a64


def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def get_reloc_offsets(elf):
    """
    Get a set of RVA values that have relocations.
    Returns a dict mapping rva -> reloc_size (pointer size in bytes).
    """
    relocs = {}
    psize = 8 if elf.bits == 64 else 4
    try:
        reloc_list = elf.getRelocs()
        for parent, reloc in reloc_list:
            try:
                r_offset = reloc.vsGetField('r_offset').vsGetValue()
                relocs[r_offset] = psize
            except Exception:
                continue
    except Exception:
        pass
    return relocs


def get_func_symbols(elf):
    """
    Extract function symbols from the ELF dynamic symbol table.
    Returns list of (rva, size, name) tuples.
    Used for .so files (ET_DYN) which have a .dynsym section.
    """
    func_syms = []
    try:
        dynsyms = elf.getDynSyms()
        for s in dynsyms:
            try:
                if s.getInfoType() != 2:  # STT_FUNC
                    continue
                rva = s.vsGetField('st_value').vsGetValue()
                size = s.vsGetField('st_size').vsGetValue()
                name = s.getName()
                if rva > 0 and size > 0 and name:
                    func_syms.append((rva, size, name))
            except Exception:
                continue
    except Exception:
        pass
    return func_syms


def get_func_symbols_relocatable(elf):
    """
    Extract function symbols from the ELF symbol table (not dynamic).
    Used for .o files (ET_REL) which have .symtab but no .dynsym.

    Returns list of (section_offset, size, name, section_index) tuples.
    section_offset is the offset within the section where the function starts.
    section_index is the index of the section containing the function.
    """
    func_syms = []
    try:
        syms = elf.getSymbols()
        for s in syms:
            try:
                if s.getInfoType() != 2:  # STT_FUNC
                    continue
                value = s.vsGetField('st_value').vsGetValue()
                size = s.vsGetField('st_size').vsGetValue()
                name = s.getName()
                # st_shndx: section index where the symbol is defined
                shndx = s.vsGetField('st_shndx').vsGetValue()
                if value >= 0 and size > 0 and name and shndx > 0:
                    func_syms.append((value, size, name, shndx))
            except Exception:
                continue
    except Exception:
        pass
    return func_syms


def get_section_by_index(elf, index):
    """Get an ELF section by its index."""
    for i, sec in enumerate(elf.getSections()):
        if i == index:
            return sec
    return None


def get_section_relocs(elf, target_section_index):
    """
    Get relocations that apply to a specific section.

    In ET_REL files, relocations are in .rela.<section> sections where
    sh_info points to the target section index. This function finds
    relocation sections whose sh_info matches target_section_index and
    returns a dict mapping r_offset -> (reloc_size, reloc_type) for each reloc.

    reloc_size is 4 for PC32/PLT32/GOTPCREL (the common 32-bit reloc types)
    and 8 for R_X86_64_64 (absolute 64-bit).
    """
    relocs = {}
    psize = 8 if elf.bits == 64 else 4
    try:
        for sec in elf.getSections():
            sh_type = sec.vsGetField('sh_type').vsGetValue() if sec.vsHasField('sh_type') else 0
            # SHT_RELA=4, SHT_REL=9
            if sh_type not in (4, 9):
                continue
            sh_info = sec.vsGetField('sh_info').vsGetValue() if sec.vsHasField('sh_info') else 0
            if sh_info != target_section_index:
                continue

            # Read the relocation entries from this section
            sh_offset = sec.vsGetField('sh_offset').vsGetValue()
            sh_size = sec.vsGetField('sh_size').vsGetValue()
            sh_entsize = sec.vsGetField('sh_entsize').vsGetValue() if sec.vsHasField('sh_entsize') else 0
            if sh_entsize == 0:
                sh_entsize = 24 if sh_type == 4 else 16  # RELA=24, REL=16

            data = elf.readAtOffset(sh_offset, sh_size)
            is_rela = (sh_type == 4)
            entry_size = sh_entsize

            for i in range(0, len(data), entry_size):
                if is_rela:
                    if elf.bits == 64:
                        r_offset, r_info, r_addend = struct.unpack_from('<QQq', data, i)
                    else:
                        r_offset, r_info, r_addend = struct.unpack_from('<IIi', data, i)
                else:
                    if elf.bits == 64:
                        r_offset, r_info = struct.unpack_from('<QQ', data, i)
                    else:
                        r_offset, r_info = struct.unpack_from('<II', data, i)

                if elf.bits == 64:
                    rel_type = r_info & 0xffffffff
                else:
                    rel_type = r_info & 0xff

                # Determine reloc size by type:
                if rel_type == 1 and elf.bits == 64:  # R_X86_64_64
                    rsize = 8
                else:
                    rsize = 4

                relocs[r_offset] = (rsize, rel_type)
    except Exception:
        pass
    return relocs


def is_ar_archive(filepath):
    """Check if a file is an ar archive (starts with '!<arch>\\n')."""
    try:
        with open(filepath, 'rb') as f:
            magic = f.read(8)
        return magic == b'!<arch>\n'
    except Exception:
        return False


def extract_ar_members(filepath):
    """
    Extract all member files from an ar archive.

    Returns a list of (member_name, bytes_io) tuples.
    Uses the `ar` command for reliability — Python's tarfile module can
    handle GNU ar archives in some cases but not all variants (e.g., thin
    archives, BSD extended format).
    """
    members = []
    try:
        # Try Python's tarfile first — it handles standard ar format
        with open(filepath, 'rb') as f:
            # ar format is not quite tar, but tarfile doesn't handle it
            # Use the ar command instead
            pass
    except Exception:
        pass

    # Use the system `ar` command to list and extract
    try:
        # List members
        result = subprocess.run(['ar', 't', filepath], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"ar list failed: {result.stderr}")
            return []

        member_names = [n.strip() for n in result.stdout.split('\n') if n.strip()]

        # Extract each member to a temp dir
        import tempfile
        tmpdir = tempfile.mkdtemp(prefix='vamp_ar_')

        for name in member_names:
            # Extract this member
            result = subprocess.run(
                ['ar', 'p', filepath, name],
                capture_output=True
            )
            if result.returncode == 0 and result.stdout:
                members.append((name, io.BytesIO(result.stdout)))

        # Clean up temp dir (we didn't write anything there)
        try:
            os.rmdir(tmpdir)
        except Exception:
            pass

    except FileNotFoundError:
        print("ERROR: 'ar' command not found — needed for .a archive extraction")
    except Exception as e:
        print(f"ERROR extracting ar archive: {e}")

    return members


def get_first_linear_block(elf, rva, func_size):
    """
    Read the first linear code block of a function.
    Uses elf.readAtRva to read bytes at the given RVA.

    Returns: (bytes, size) or (None, 0) on failure
    """
    max_read = min(func_size, 256)  # Cap at 256 bytes for sig
    try:
        bytez = elf.readAtRva(rva, max_read)
        return bytez, len(bytez)
    except Exception:
        return None, 0


def mask_relocations_with_instructions(bytez, rva_start, reloc_offsets, psize,
                                         arch, disasm):
    """
    Mask out relocation slots, with targeted extra masking for relaxable
    relocation types.

    For .a object files compiled with -fPIC, the linker can 'relax' certain
    relocation types (GOTPCRELX, PLT32, PC32) by replacing the instruction
    encoding. For example:
      mov rax, [rip+GOT]  (48 8b 05 <disp32>)  →  mov rax, imm32  (48 c7 c0 <imm32>)

    The reloc offset points to the disp32/imm32 (already masked). But the
    opcode and ModRM bytes also change (8b 05 → c7 c0). We mask the 2-3
    bytes immediately before the reloc offset to cover the opcode + ModRM
    without masking the entire instruction. This is more targeted than
    full-instruction masking and avoids false positives.

    For non-relaxable relocations (R_X86_64_64, R_X86_64_32, etc.), we only
    mask the reloc bytes themselves.

    reloc_offsets is a dict mapping rva -> (reloc_size, reloc_type).

    Returns (sig_bytes, mask_bytes).
    """
    sig = bytearray(bytez)
    mask = bytearray(b'\xff' * len(bytez))

    # x86_64 relaxable reloc types:
    # R_X86_64_PC32=2, R_X86_64_PLT32=4, R_X86_64_GOTPCREL=9,
    # R_X86_64_GOTPCRELX=22, R_X86_64_REX_GOTPCRELX=23
    relaxable_types = {2, 4, 9, 22, 23}

    for reloc_rva, reloc_info in reloc_offsets.items():
        offset_in_block = reloc_rva - rva_start
        if not (0 <= offset_in_block < len(bytez)):
            continue

        # Handle both old format (just size) and new format (size, type)
        if isinstance(reloc_info, tuple):
            rsize, rel_type = reloc_info
        else:
            rsize = reloc_info
            rel_type = 0

        rsize = rsize if rsize > 0 else psize

        # Mask the reloc bytes themselves
        end = min(offset_in_block + rsize, len(bytez))
        for i in range(offset_in_block, end):
            sig[i] = 0x00
            mask[i] = 0x00

        # For relaxable types, also mask the opcode+ModRM bytes before the reloc.
        # x86_64: the 2 bytes before the reloc offset are the opcode + ModRM
        # that change during relaxation (e.g., 8b 05 → c7 c0).
        # PLT32 (type 4) and PC32 (type 2) are used for call/jmp rel32 — the
        # opcode (E8/E9) doesn't change during relaxation, only the disp32
        # changes. So don't mask extra bytes for those.
        # GOTPCREL/GOTPCRELX (types 9, 22, 23) are used for mov/lea [rip+GOT]
        # where the opcode AND ModRM change. Mask 3 extra bytes before the reloc
        # (REX + opcode + ModRM, or opcode + ModRM + SIB).
        if rel_type in (9, 22, 23):
            # Mask 3 bytes before the reloc offset
            # (covers REX.W + opcode + ModRM, or similar patterns)
            extra_start = max(0, offset_in_block - 3)
            for i in range(extra_start, offset_in_block):
                sig[i] = 0x00
                mask[i] = 0x00

    return bytes(sig), bytes(mask)


def mask_relocations(bytez, rva_start, reloc_offsets, psize):
    """
    Mask out relocation slots in the byte sequence.
    Returns (sig_bytes, mask_bytes) with relocatable addresses zeroed.

    reloc_offsets is a dict mapping rva -> reloc_size or (reloc_size, reloc_type).
    For .so files, reloc_size is typically psize (pointer size).
    For .a files, reloc_size is 4 for PC32/PLT32/GOTPCREL or 8 for R_X86_64_64.
    """
    sig = bytearray(bytez)
    mask = bytearray(b'\xff' * len(bytez))

    for reloc_rva, reloc_info in reloc_offsets.items():
        # Handle both formats: just size, or (size, type) tuple
        if isinstance(reloc_info, tuple):
            reloc_size = reloc_info[0]
        else:
            reloc_size = reloc_info

        # Check if this relocation falls within our byte range
        offset_in_block = reloc_rva - rva_start
        if 0 <= offset_in_block < len(bytez):
            # Use the actual reloc_size from the dict, not psize.
            # Fall back to psize if reloc_size is 0 (shouldn't happen).
            rsize = reloc_size if reloc_size > 0 else psize
            end = min(offset_in_block + rsize, len(bytez))
            for i in range(offset_in_block, end):
                sig[i] = 0x00
                mask[i] = 0x00

    return bytes(sig), bytes(mask)


# ---------------------------------------------------------------------------
# Instruction-aware masking
# ---------------------------------------------------------------------------

def _get_disassembler(arch):
    """Get the envi disassembler for the given architecture string."""
    if arch in ('amd64', 'x64', 'x86_64'):
        return e_amd64.Amd64Disasm(), 'amd64'
    elif arch in ('i386', 'x86', 'ia32'):
        return e_i386.i386Disasm(), 'i386'
    elif arch in ('aarch64', 'arm64'):
        return e_a64.A64Disasm(), 'aarch64'
    elif arch in ('arm', 'arm32', 'armv7'):
        import envi.archs.arm as e_arm
        return e_arm.ArmDisasm(), 'arm'
    else:
        return None, None


def _mask_range(mask, sig, start, length):
    """Mask out a range of bytes in the mask and sig arrays."""
    end = min(start + length, len(mask))
    for i in range(start, end):
        sig[i] = 0x00
        mask[i] = 0x00


def mask_instruction_operands_amd64(bytez, rva, disasm):
    """
    Disassemble x86_64 instructions and mask position-dependent operands.

    Masks:
    - call rel32 (E8): 4-byte relative offset
    - jmp rel32 (E9): 4-byte relative offset
    - jcc rel32 (0F 8x): 4-byte relative offset
    - RIP-relative memory operands (Amd64RipRelOper): 4-byte RIP displacement

    Returns: (sig_bytes, mask_bytes) with position-dependent bytes zeroed.
    """
    sig = bytearray(bytez)
    mask = bytearray(bytes([0xff]) * len(bytez))
    offset = 0

    while offset < len(bytez):
        try:
            op = disasm.disasm(bytez, offset, rva + offset)
        except Exception:
            # Can't decode — treat as single byte and move on
            offset += 1
            continue

        if op is None or op.size == 0:
            offset += 1
            continue

        instr_start = offset
        instr_end = offset + op.size

        for oper in op.opers:
            # PC-relative branch/call operands (call/jmp/jcc rel32)
            if isinstance(oper, e_i386.i386PcRelOper):
                # The rel32 is the last 4 bytes of the instruction
                rel_start = instr_end - 4
                _mask_range(mask, sig, rel_start, 4)

            # RIP-relative memory operands (lea/mov [rip+disp32])
            elif isinstance(oper, e_amd64.Amd64RipRelOper):
                # The imm32 displacement is the last 4 bytes
                rel_start = instr_end - 4
                _mask_range(mask, sig, rel_start, 4)

        offset += op.size

    return bytes(sig), bytes(mask)


def mask_instruction_operands_i386(bytez, rva, disasm):
    """
    Disassemble x86 (32-bit) instructions and mask position-dependent operands.

    Masks:
    - call rel32 (E8): 4-byte relative offset
    - jmp rel32 (E9): 4-byte relative offset
    - jcc rel32 (0F 8x): 4-byte relative offset
    - call/jmp [imm32] (FF 15/FF 25): 4-byte absolute address (GOT indirection)
    - mov reg, [imm32] (A1): 4-byte absolute address (PIC GOT reference)

    Returns: (sig_bytes, mask_bytes) with position-dependent bytes zeroed.
    """
    sig = bytearray(bytez)
    mask = bytearray(bytes([0xff]) * len(bytez))
    offset = 0

    while offset < len(bytez):
        try:
            op = disasm.disasm(bytez, offset, rva + offset)
        except Exception:
            offset += 1
            continue

        if op is None or op.size == 0:
            offset += 1
            continue

        instr_start = offset
        instr_end = offset + op.size

        for oper in op.opers:
            # PC-relative branch/call operands
            if isinstance(oper, e_i386.i386PcRelOper):
                rel_start = instr_end - 4
                _mask_range(mask, sig, rel_start, 4)

            # Immediate memory operands (absolute addresses via GOT in PIC)
            # e.g., call [0xXXXX], jmp [0xXXXX], mov eax, [0xXXXX]
            elif isinstance(oper, e_i386.i386ImmMemOper):
                # The imm32 address is the last 4 bytes of the instruction
                # (or embedded depending on encoding, but for the common
                # FF 15/FF 25/A1 forms it's at instr_end-4)
                imm_start = instr_end - 4
                if imm_start >= instr_start:
                    _mask_range(mask, sig, imm_start, 4)

        offset += op.size

    return bytes(sig), bytes(mask)


def mask_instruction_operands_aarch64(bytez, rva, disasm):
    """
    Disassemble AArch64 instructions and mask position-dependent operands.

    Masks:
    - bl (branch with link): 26-bit immediate (covers full 4 bytes)
    - b (unconditional branch): 26-bit immediate
    - b.cond (conditional branch): 19-bit immediate (bits 23:5)
    - adrp (PC-relative address): 21-bit immediate (bits 23:5 + bit 30:29)
    - ldr/str with PC-relative literal: 19-bit immediate

    For all AArch64 instructions, the entire 4-byte encoding may contain
    position-dependent bits, so we mask the entire instruction for branches
    and PC-relative loads.

    Returns: (sig_bytes, mask_bytes) with position-dependent bytes zeroed.
    """
    sig = bytearray(bytez)
    mask = bytearray(bytes([0xff]) * len(bytez))
    offset = 0

    while offset + 4 <= len(bytez):
        try:
            op = disasm.disasm(bytez, offset, rva + offset)
        except Exception:
            offset += 4
            continue

        if op is None or op.size == 0:
            offset += 4
            continue

        instr_start = offset
        instr_end = offset + op.size  # Should be 4 for AArch64

        mnem = op.mnem

        # Branch instructions — mask entire instruction
        # (the offset bits are interleaved with condition codes etc.)
        if mnem in ('bl', 'b', 'br', 'blr'):
            _mask_range(mask, sig, instr_start, op.size)

        # Conditional branches: b.eq, b.ne, b.cs, b.cc, b.mi, b.pl, b.vs,
        # b.vc, b.hi, b.ls, b.ge, b.lt, b.gt, b.le, b.al, b.nv
        # and cbz/cbnz (compare and branch)
        elif mnem.startswith('b.') or mnem in ('cbz', 'cbnz', 'tbz', 'tbnz'):
            _mask_range(mask, sig, instr_start, op.size)

        # ADRP — PC-relative address computation
        elif mnem == 'adrp':
            _mask_range(mask, sig, instr_start, op.size)

        # ADR — PC-relative address (smaller offset)
        elif mnem == 'adr':
            _mask_range(mask, sig, instr_start, op.size)

        # LDR literal (PC-relative load from literal pool)
        elif mnem == 'ldr' and len(op.opers) >= 2:
            # Check if it's a PC-relative literal load
            # LDR with #imm (literal pool) has specific encoding
            # For simplicity, mask ldr where the second operand is an immediate
            pass  # Conservative: don't mask data loads, they may be register offsets

        offset += op.size

    return bytes(sig), bytes(mask)


def mask_instruction_operands_arm(bytez, rva, disasm):
    """
    Disassemble ARM (32-bit) instructions and mask position-dependent operands.

    ARM branch instructions encode the offset in the instruction bits, so
    we mask the entire 4-byte instruction for branches.

    Masks:
    - bl (branch with link): 24-bit immediate
    - b (unconditional branch): 24-bit immediate
    - b<cond> (conditional branch): 24-bit immediate
    - bl<cond> (conditional branch with link): 24-bit immediate
    - ldr pc, [pc, #imm] (PC-relative load): immediate offset

    Returns: (sig_bytes, mask_bytes) with position-dependent bytes zeroed.
    """
    sig = bytearray(bytez)
    mask = bytearray(bytes([0xff]) * len(bytez))
    offset = 0

    while offset + 4 <= len(bytez):
        try:
            op = disasm.disasm(bytez, offset, rva + offset)
        except Exception:
            offset += 4
            continue

        if op is None or op.size == 0:
            offset += 4
            continue

        instr_start = offset
        mnem = op.mnem

        # Branch instructions
        if mnem in ('bl', 'b', 'blx', 'bx'):
            _mask_range(mask, sig, instr_start, op.size)

        # Conditional branches: b<cond>, bl<cond>
        elif mnem.startswith('b') and len(mnem) > 1 and mnem[1] in (
                'eq', 'ne', 'cs', 'cc', 'mi', 'pl', 'vs', 'vc',
                'hi', 'ls', 'ge', 'lt', 'gt', 'le', 'al', 'nv',
        ):
            _mask_range(mask, sig, instr_start, op.size)

        # ldr to PC (literal pool load)
        elif mnem == 'ldr':
            # Check if PC is involved as a base register
            for oper in op.opers:
                if hasattr(oper, 'reg') and hasattr(oper, 'tsize'):
                    # PC register number in ARM is 15 (e_reg)
                    # We check by looking for operand resolving to PC
                    pass

        offset += op.size

    return bytes(sig), bytes(mask)


def mask_instruction_operands(bytez, rva, arch):
    """
    Disassemble the byte sequence and mask position-dependent operands.

    This is the key function that makes VAMP sigs work across different
    binary layouts (static linking, different base addresses, etc.).

    Returns: (sig_bytes, mask_bytes) with position-dependent bytes zeroed.
    """
    disasm, arch_type = _get_disassembler(arch)
    if disasm is None:
        # No disassembler available — fall back to all-ff mask
        return bytez, bytes([0xff]) * len(bytez)

    if arch_type == 'amd64':
        return mask_instruction_operands_amd64(bytez, rva, disasm)
    elif arch_type == 'i386':
        return mask_instruction_operands_i386(bytez, rva, disasm)
    elif arch_type == 'aarch64':
        return mask_instruction_operands_aarch64(bytez, rva, disasm)
    elif arch_type == 'arm':
        return mask_instruction_operands_arm(bytez, rva, disasm)
    else:
        return bytez, bytes([0xff]) * len(bytez)


def _process_function_sigs(bytez, rva, func_size, arch, disasm,
                           reloc_offsets, rva_start, psize,
                           min_length, max_masked_ratio,
                           mask_full_instructions=False):
    """
    Core signature generation logic shared between .so and .a paths.

    Takes raw function bytes, applies relocation masking + instruction-aware
    masking, computes confidence, and returns a (sig_bytes, mask_bytes,
    block_size, confidence, masked_ratio) tuple, or None if filtered out.

    If mask_full_instructions=True (for .a files), relocations are masked
    by masking the entire containing instruction, not just the reloc bytes.
    This handles linker relaxation (GOTPCRELX → direct immediate, etc.).
    """
    block_size = len(bytez)
    if block_size == 0:
        return None

    # Step 1: Mask relocations
    if mask_full_instructions and disasm is not None:
        reloc_sig, reloc_mask = mask_relocations_with_instructions(
            bytez, rva_start, reloc_offsets, psize, arch, disasm)
    else:
        reloc_sig, reloc_mask = mask_relocations(
            bytez, rva_start, reloc_offsets, psize)

    # Step 2: Instruction-aware masking
    if disasm is not None:
        instr_sig, instr_mask = mask_instruction_operands(
            bytez, rva, arch)

        # Merge both masks
        sig_bytes = bytearray(bytez)
        mask_bytes = bytearray(b'\xff' * len(bytez))
        for i in range(len(mask_bytes)):
            if reloc_mask[i] == 0x00 or instr_mask[i] == 0x00:
                sig_bytes[i] = 0x00
                mask_bytes[i] = 0x00

        sig_bytes = bytes(sig_bytes)
        mask_bytes = bytes(mask_bytes)
    else:
        sig_bytes = reloc_sig
        mask_bytes = reloc_mask

    # Compute metrics
    masked_count = sum(1 for b in mask_bytes if b == 0)
    masked_ratio = masked_count / block_size if block_size > 0 else 1.0

    # Confidence scoring
    if block_size >= 16 and masked_ratio < 0.25:
        confidence = 'high'
    elif block_size >= 8 and masked_ratio < 0.50:
        confidence = 'medium'
    else:
        confidence = 'low'

    # Filter
    if block_size < min_length:
        return None
    if masked_ratio > max_masked_ratio:
        return None

    return sig_bytes, mask_bytes, block_size, confidence, masked_ratio


def generate_elf_sigs_from_so(input_path, library, version, arch, platform_name,
                               compiler, compiled_flags, source_url,
                               min_length, max_masked_ratio,
                               min_confidence, dedup, binary_sha256):
    """
    Generate VAMP signatures from an ELF shared library (.so).

    Uses dynamic symbol table (getDynSyms) and reads bytes by RVA.
    """
    f = open(input_path, 'rb')
    elf = Elf(f)

    psize = 8 if elf.bits == 64 else 4

    func_syms = get_func_symbols(elf)
    print(f"  Found {len(func_syms)} function symbols (dynamic)")

    reloc_offsets = get_reloc_offsets(elf)
    print(f"  Found {len(reloc_offsets)} relocations (data section)")

    disasm, arch_type = _get_disassembler(arch)
    if disasm is None:
        print(f"  WARNING: No disassembler for arch '{arch}', "
              f"sig masks will be all-ff (no instruction-aware masking)")
    else:
        print(f"  Using {arch_type} disassembler for instruction-aware masking")

    signatures = []
    skipped = 0
    errors = 0
    instr_masked = 0

    for rva, func_size, name in sorted(func_syms):
        try:
            bytez, block_size = get_first_linear_block(elf, rva, func_size)
            if bytez is None or block_size == 0:
                skipped += 1
                continue

            result = _process_function_sigs(
                bytez, rva, func_size, arch, disasm,
                reloc_offsets, rva, psize,
                min_length, max_masked_ratio)
            if result is None:
                skipped += 1
                continue

            sig_bytes, mask_bytes, block_size, confidence, masked_ratio = result

            if disasm is not None:
                instr_mask_check = mask_instruction_operands(bytez, rva, arch)[1]
                if any(b == 0x00 for b in instr_mask_check):
                    instr_masked += 1

            clean_name = name.split('@@')[0].split('@')[0]

            sig_entry = {
                'name': '%s.%s' % (library, clean_name),
                'bytes': sig_bytes.hex(),
                'mask': mask_bytes.hex(),
                'func_size': func_size,
                'first_block_size': block_size,
                'reloc_count': sum(1 for b in mask_bytes if b == 0) // psize,
                'masked_ratio': round(masked_ratio, 4),
                'confidence': confidence,
            }
            signatures.append(sig_entry)

        except Exception:
            errors += 1
            continue

    f.close()

    print(f"  Generated {len(signatures)} signatures (skipped {skipped}, errors {errors})")
    print(f"  Signatures with instruction-aware masking: {instr_masked}")

    return signatures


def generate_elf_sigs_from_archive(input_path, library, version, arch,
                                    platform_name, compiler, compiled_flags,
                                    source_url, min_length, max_masked_ratio,
                                    min_confidence, dedup, binary_sha256):
    """
    Generate VAMP signatures from a static archive (.a).

    Extracts each .o member, parses as ET_REL, reads function bytes by
    section offset, and masks both ELF relocations AND instruction-aware
    operands. This is the preferred source for static binary matching.
    """
    # Extract .o members from the ar archive
    members = extract_ar_members(input_path)
    print(f"  Extracted {len(members)} object files from archive")

    if not members:
        print("  ERROR: No members extracted — cannot generate signatures")
        return []

    disasm, arch_type = _get_disassembler(arch)
    if disasm is None:
        print(f"  WARNING: No disassembler for arch '{arch}', "
              f"sig masks will be all-ff (no instruction-aware masking)")
    else:
        print(f"  Using {arch_type} disassembler for instruction-aware masking")

    signatures = []
    total_skipped = 0
    total_errors = 0
    total_instr_masked = 0
    obj_count = 0

    for member_name, member_io in members:
        try:
            elf = Elf(member_io)
        except Exception as e:
            # Some members might not be ELF (e.g., __.SYMDEF, table of contents)
            continue

        obj_count += 1
        psize = 8 if elf.bits == 64 else 4

        # Get function symbols from .symtab (not .dynsym)
        func_syms = get_func_symbols_relocatable(elf)
        if not func_syms:
            member_io.close()
            continue

        # Build a map of section index -> section object for quick lookup
        sections_by_index = {}
        for i, sec in enumerate(elf.getSections()):
            sections_by_index[i] = sec

        # Process each function symbol
        for func_offset, func_size, name, shndx in func_syms:
            try:
                sec = sections_by_index.get(shndx)
                if sec is None:
                    total_skipped += 1
                    continue

                # Verify this is a code section (SHT_PROGBITS=1 with SHF_EXECINSTR)
                sh_type = sec.vsGetField('sh_type').vsGetValue() if sec.vsHasField('sh_type') else 0
                sh_flags = sec.vsGetField('sh_flags').vsGetValue() if sec.vsHasField('sh_flags') else 0
                if sh_type != 1:  # SHT_PROGBITS
                    total_skipped += 1
                    continue
                # SHF_EXECINSTR = 0x4 — check if this section is executable
                if not (sh_flags & 0x4):
                    total_skipped += 1
                    continue

                # Read bytes by section offset (not RVA — section addrs are 0 in ET_REL)
                sh_offset = sec.vsGetField('sh_offset').vsGetValue()
                sh_size = sec.vsGetField('sh_size').vsGetValue()

                # The function starts at sh_offset + func_offset within the file
                file_offset = sh_offset + func_offset
                max_read = min(func_size, 256)
                # Don't read past section end
                bytes_left_in_section = sh_size - func_offset
                max_read = min(max_read, bytes_left_in_section)

                try:
                    bytez = elf.readAtOffset(file_offset, max_read)
                except Exception:
                    total_skipped += 1
                    continue

                block_size = len(bytez)
                if block_size == 0:
                    total_skipped += 1
                    continue

                # Get relocations for this specific section
                section_relocs = get_section_relocs(elf, shndx)

                # For ET_REL, reloc offsets are relative to the section start.
                # Our function starts at func_offset within the section.
                # Adjust reloc offsets to be relative to our function start.
                adjusted_relocs = {}
                for reloc_offset, reloc_info in section_relocs.items():
                    offset_in_func = reloc_offset - func_offset
                    if 0 <= offset_in_func < block_size:
                        adjusted_relocs[offset_in_func] = reloc_info

                # For instruction-aware masking, use func_offset as the base RVA.
                # The actual RVA doesn't matter for masking — only relative
                # instruction offsets matter. Using func_offset ensures the
                # disassembler sees correct branch targets for instruction
                # boundary alignment.
                #
                # mask_full_instructions=True: for .a files, mask the entire
                # instruction containing each relocation (handles linker
                # relaxation of GOTPCRELX/PLT32/PC32 relocations).
                result = _process_function_sigs(
                    bytez, func_offset, func_size, arch, disasm,
                    adjusted_relocs, 0,  # rva_start=0 for section-relative
                    psize, min_length, max_masked_ratio,
                    mask_full_instructions=True)
                if result is None:
                    total_skipped += 1
                    continue

                sig_bytes, mask_bytes, block_size, confidence, masked_ratio = result

                if disasm is not None:
                    instr_mask_check = mask_instruction_operands(
                        bytez, func_offset, arch)[1]
                    if any(b == 0x00 for b in instr_mask_check):
                        total_instr_masked += 1

                clean_name = name.split('@@')[0].split('@')[0]

                sig_entry = {
                    'name': '%s.%s' % (library, clean_name),
                    'bytes': sig_bytes.hex(),
                    'mask': mask_bytes.hex(),
                    'func_size': func_size,
                    'first_block_size': block_size,
                    'reloc_count': sum(1 for b in mask_bytes if b == 0) // psize,
                    'masked_ratio': round(masked_ratio, 4),
                    'confidence': confidence,
                    'source_object': member_name,
                }
                signatures.append(sig_entry)

            except Exception:
                total_errors += 1
                continue

        member_io.close()

    print(f"  Processed {obj_count} object files")
    print(f"  Generated {len(signatures)} signatures "
          f"(skipped {total_skipped}, errors {total_errors})")
    print(f"  Signatures with instruction-aware masking: {total_instr_masked}")

    return signatures


def generate_elf_sigs(input_path, library, version, arch, platform_name,
                      compiler, compiled_flags='', source_url=None,
                      min_length=8, max_masked_ratio=0.50,
                      min_confidence='low', dedup=True):
    """
    Generate VAMP signatures from an ELF library.

    Automatically detects whether the input is a static archive (.a) or
    a shared library (.so) and uses the appropriate extraction method.
    Static archives are preferred for generating sigs that match static
    binaries; .so is used as a fallback when .a is not available.

    Returns: sigset dict ready for JSON serialization.
    """
    binary_sha256 = compute_sha256(input_path)

    if is_ar_archive(input_path):
        print(f"Input is a static archive (.a) — extracting object files...")
        signatures = generate_elf_sigs_from_archive(
            input_path, library, version, arch, platform_name,
            compiler, compiled_flags, source_url,
            min_length, max_masked_ratio, min_confidence, dedup,
            binary_sha256)
    else:
        print(f"Input is a shared library (.so)...")
        signatures = generate_elf_sigs_from_so(
            input_path, library, version, arch, platform_name,
            compiler, compiled_flags, source_url,
            min_length, max_masked_ratio, min_confidence, dedup,
            binary_sha256)

    # Serialize
    import vivisect.vamp as v_vamp
    sigset = v_vamp.serializeSigSet(
        library=library,
        version=version,
        arch=arch,
        platform=platform_name,
        compiler=compiler,
        compiled_flags=compiled_flags,
        binary_sha256=binary_sha256,
        signatures=signatures,
        source_url=source_url,
    )

    # Deduplicate
    if dedup:
        sigset = v_vamp.dedupSigs(sigset)
        print(f"After dedup: {len(sigset['signatures'])} signatures")
        if sigset.get('dedup_conflicts'):
            print(f"Dedup conflicts: {len(sigset['dedup_conflicts'])}")

    return sigset


def main():
    parser = argparse.ArgumentParser(
        description='Fast VAMP Signature Generator for ELF libraries (.a or .so)')
    parser.add_argument('--input', '-i', required=True,
                        help='Input ELF library (.a static archive or .so shared library)')
    parser.add_argument('--output', '-o', required=True, help='Output JSON signature file')
    parser.add_argument('--library', required=True, help='Library name (e.g., glibc)')
    parser.add_argument('--version', required=True, help='Library version (e.g., 2.39)')
    parser.add_argument('--arch', required=True, help='Architecture (i386, amd64, arm, aarch64)')
    parser.add_argument('--platform', default='linux', help='Platform')
    parser.add_argument('--compiler', default='unknown', help='Compiler')
    parser.add_argument('--flags', default='', help='Compilation flags')
    parser.add_argument('--source-url', help='URL to source/binary')
    parser.add_argument('--min-length', type=int, default=8)
    parser.add_argument('--max-masked', type=float, default=0.50)
    parser.add_argument('--min-confidence', default='low', choices=['low', 'medium', 'high'])
    parser.add_argument('--no-dedup', action='store_true')
    args = parser.parse_args()

    sigset = generate_elf_sigs(
        input_path=args.input,
        library=args.library,
        version=args.version,
        arch=args.arch,
        platform_name=args.platform,
        compiler=args.compiler,
        compiled_flags=args.flags,
        source_url=args.source_url,
        min_length=args.min_length,
        max_masked_ratio=args.max_masked,
        min_confidence=args.min_confidence,
        dedup=not args.no_dedup,
    )

    import vivisect.vamp as v_vamp
    v_vamp.saveSigSet(args.output, sigset)
    print(f"Wrote {len(sigset['signatures'])} signatures to {args.output}")


if __name__ == '__main__':
    main()