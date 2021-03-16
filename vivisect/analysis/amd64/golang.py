'''
Perform further analysis on 64-bit GO language executables.

This module extends code flow analysis to runtime_main for Windows PE binaries.
GO binaries start from a single export and proceed thru several functions
that initialize GO.  Specific application code is launched from the GO function
runtime_main(), which is invoked by "call rax" with an address placed on the
stack many calls earlier.  Vivisect code flow analysis does not track the
address; this module finds the address and invokes makeFunction(va).

Samples have been found with different instruction sequences for reaching the
address of runtime_main(); this module attempts all observed sequences.
'''

import envi
import envi.archs.i386.disasm
import envi.archs.amd64.disasm
from vivisect.analysis.i386.golang import golang_collect_opcodes, find_golang_bblock

import logging

logger = logging.getLogger(__name__)

# Opcode sequence, where element [-6] is the important one.
_GOLANG_AMD64_INSTRS = ['cld', 'call', 'mov', 'mov', 'mov', 'mov', 'call',
                        'call', 'call', 'lea', 'push', 'push', 'call',
                        'pop', 'pop']

def analyze(vw):
    '''
    Perform further analysis on GO language executables.
    '''
    # Make sure it is a PE file, with "Go build ID:" in the first few bytes
    # of the .text segment (versus a .upxN segment of a packed sample).
    has_go_build = False
    for segment in vw.getSegments():
        va, size, name, filename = segment
        if name == '.text':
            bytez = vw.readMemory(va, 10000)
            k1 = bytez.find(b'Go build ID: ')
            if k1 != -1:
                has_go_build = True
                break
    if not has_go_build:
        return

    # Search the entry point (public export) for the pointer to runtime_main().
    # Most GO executables have a single entry point, but some are more complex.
    ep = vw.getEntryPoints()
    ptr_va, runtime_va = golang_search_eps(vw, ep, filename)
    if runtime_va is None:
        return

    # Invoke codeflow on runtime_main().
    vw.addEntryPoint(runtime_va)
    logger.debug('discovered runtime function: 0x%x', runtime_va)
    vw.makeFunction(runtime_va)

    # Also mark the ptr_va as a pointer to runtime_va.
    vw.makePointer(ptr_va, tova=runtime_va)


_GOLANG_AMD64_MEP1A_INSTRS \
    = ['sub', 'mov', 'mov', 'call', 'call', 'nop', 'nop', 'add', 'ret']
_GOLANG_AMD64_MEP1B_INSTRS \
    = ['sub', 'mov', 'call', 'call', 'nop', 'nop', 'add', 'ret']
_GOLANG_AMD64_MEP2A_INSTRS \
    = ['mov', 'mov', 'call', 'mov', 'mov', 'mov', 'mov', 'mov', 'mov', 'mov',
       'call', 'mov', 'mov', 'test', 'jz']
_GOLANG_AMD64_MEP2B_INSTRS \
    = ['mov', 'mov', 'call', 'mov', 'mov', 'mov', 'mov', 'mov', 'mov',
       'call', 'mov', 'mov', 'test', 'jz']
def golang_search_eps(vw, ep , filename):
    '''
    Search over all entry points to find main(), and then look for the
    function that calls runtime_main().
    Return two pointers, or None, None if not found.
    '''
    if len(ep) == 1:
        ep_va = ep[0]
        bblocks = vw.getFunctionBlocks(ep_va)
        if not bblocks:
            return None, None
        ptr_va, runtime_va = extract_golang_mainmain(vw, bblocks, filename)
        return ptr_va, runtime_va

    # Look for an entry point with a single basic block with a specific set
    # of instructions.  One of the call instructions has the next function.
    # There can be multiple candidate functions meeting this criteria.
    candidate_fns_1 = set()
    for next_ep in ep:
        bblocks = vw.getFunctionBlocks(next_ep)
        if (not bblocks) or (len(bblocks) != 1):
            continue
        instrs = golang_collect_opcodes(vw, bblocks[0])
        if (len(instrs) != len(_GOLANG_AMD64_MEP1A_INSTRS)) and \
           (len(instrs) != len(_GOLANG_AMD64_MEP1B_INSTRS)):
            continue
        instrs_mnem = [ op.mnem for op in instrs ]
        if (instrs_mnem != _GOLANG_AMD64_MEP1A_INSTRS) and \
           (instrs_mnem != _GOLANG_AMD64_MEP1B_INSTRS):
            continue
        opcode = instrs[-5]
        if not isinstance(opcode.opers[0],
                          envi.archs.i386.disasm.i386PcRelOper):
            continue
        try:
            candidate_fns_1.add(opcode.opers[0].getOperValue(opcode))
        except Exception:
            continue

    if not candidate_fns_1:
        return None, None

    # Next function has many basic blocks, one of which makes a call to main().
    candidate_fns_2 = set()
    for fnptr in candidate_fns_1:
        if not vw.isFunction(fnptr):
            continue
        bblocks = vw.getFunctionBlocks(fnptr)
        for bblock in bblocks:
            instrs = golang_collect_opcodes(vw, bblock)
            if (len(instrs) != len(_GOLANG_AMD64_MEP2A_INSTRS)) and \
               (len(instrs) != len(_GOLANG_AMD64_MEP2B_INSTRS)):
                continue
            instrs_mnem = [ op.mnem for op in instrs ]
            if (instrs_mnem != _GOLANG_AMD64_MEP2A_INSTRS) and \
               (instrs_mnem != _GOLANG_AMD64_MEP2B_INSTRS):
                continue
            opcode = instrs[-5]
            if not isinstance(opcode.opers[0],
                              envi.archs.i386.disasm.i386PcRelOper):
                continue
            try:
                candidate_fns_2.add(opcode.opers[0].getOperValue(opcode))
            except Exception:
                continue

    # There should be just one candidate function by now.
    if len(candidate_fns_2) != 1:
        return None, None

    ptr = candidate_fns_2.pop()

    # Analyze the function at the pointer if necessary.
    if not vw.isFunction(ptr):
        return None, None
    bblocks = vw.getFunctionBlocks(ptr)
    if not bblocks:
        return None, None

    # This might be the function that calls runtime_main(), or there might
    # be one more indirect jump in a single basic block.
    if len(bblocks) > 1:
        ptr_va, runtime_va = extract_golang_mainmain(vw, bblocks, filename)
        if runtime_va is None:
            return None, None
        return ptr_va, runtime_va

    # Look for the indirect jump.
    # Expect a function with one BB, with an indirect jump to the
    # address loaded by "lea rax,[rip + immediate]".
    instrs = golang_collect_opcodes(vw, bblocks[0])
    if not instrs:
        return None, None
    op = instrs[0]
    ptr_va, _ = parse_lea_raxriprel(vw, op, filename)
    if not vw.isFunction(ptr_va):
        return None, None
    bblocks = vw.getFunctionBlocks(ptr_va)
    ptr_va, runtime_va = extract_golang_mainmain(vw, bblocks, filename)
    return ptr_va, runtime_va


def extract_golang_mainmain(vw, basic_blocks, filename):
    '''
    Find the basic block of interest and return the address of
    the pointer and its contents, runtime_main().

    The BB will contain the sequence of opcodes in _GOLANG_AMD64_INSTRS.
    The push instruction -6 from the end will load the contents of a memory
    address, and those contents are the runtime_main() address.
    '''
    op = find_golang_bblock(vw, basic_blocks, _GOLANG_AMD64_INSTRS, 6)
    if op is None:
        op = find_golang_bblock_via_ind_jmp(vw, filename)
        if op is None:
            return None, None

    # The key opcode is "lea rax,[rip + immediate]", which points to
    # the GO function runtime_mainPC (aka runtime_main).
    ptr_va, runtime_va = parse_lea_raxriprel(vw, op, filename, get_content=True)
    return ptr_va, runtime_va


def find_golang_bblock_via_ind_jmp(vw, filename):
    '''
    Find the basic block of interest and return the address where
    the special sequence of opcodes begins.  Return None if not found.

    Some GO executables use an indirect jmp in the entry point,
    and special logic is needed to locate the BB of interest.
    Example:  1897d2de0837090ec350004ef2f9fa87.
    '''
    # Start from the entry point (we already know there is only one).
    ep_va = vw.getEntryPoints()[0]

    # Expect a function with one BB, ending with an indirect jump
    # to the address loaded by "lea rax,[rip + immediate]".
    basic_blocks = vw.getFunctionBlocks(ep_va)
    if len(basic_blocks) != 1:
        return None
    instrs = golang_collect_opcodes(vw, basic_blocks[0])
    if (len(instrs) < 2) or \
       (instrs[-1].mnem != 'jmp') or \
       (instrs[-2].mnem != 'lea'):
        return None
    op = instrs[-2]
    ptr_va, _ = parse_lea_raxriprel(vw, op, filename)
    if not ptr_va:
        return None

    # Analyze the function at the pointer if necessary.
    if not vw.isFunction(ptr_va):
        logger.debug('discovered new function (ptr): 0x%x', ptr_va)
        vw.makeFunction(ptr_va)

    # Expect a function with one BB, ending with an indirect jump
    # to the address loaded by "lea rax,[rip + immediate]".
    basic_blocks = vw.getFunctionBlocks(ptr_va)
    if len(basic_blocks) != 1:
        return None
    instrs = golang_collect_opcodes(vw, basic_blocks[0])
    if (len(instrs) < 2) or \
       (instrs[-1].mnem != 'jmp') or \
       (instrs[-2].mnem != 'lea'):
        return None
    op = instrs[-2]
    ptr_va, _ = parse_lea_raxriprel(vw, op, filename)
    if not ptr_va:
        return None

    # This function should contain the special basic block.
    basic_blocks = vw.getFunctionBlocks(ptr_va)
    return find_golang_bblock(vw, basic_blocks, _GOLANG_AMD64_INSTRS, 6)


def parse_lea_raxriprel(vw, opcode, filename, get_content=False):
    '''
    Parse an opcode that should be "lea rax,[rip + immediate]", returning
    the address of the second operand.  Also return the content of the
    address if so requested.
    Return None, None if there is an error.
    '''
    if len(opcode.opers) != 2:
        return None, None
    if not isinstance(opcode.opers[1], envi.archs.amd64.disasm.Amd64RipRelOper):
        return None, None
    try:
        ptr_va = opcode.opers[1].getOperValue(opcode)
        if len(vw.readMemory(ptr_va, 8)) != 8:
            return None, None
        if get_content:
            runtime_va = vw.castPointer(ptr_va)
            if len(vw.readMemory(runtime_va, 8)) != 8:
                return None, None
        else:
            runtime_va = None
        return ptr_va, runtime_va
    except Exception as e:
        return None, None
