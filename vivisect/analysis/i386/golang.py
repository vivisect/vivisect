'''
Perform further analysis on 32-bit GO language executables.

This module extends code flow analysis to runtime_main for Windows PE binaries.
GO binaries start from a single export and proceed thru several functions
that initialize GO.  Specific application code is launched from the GO function
runtime_main(), which is invoked by "call eax" with an address placed on the
stack many calls earlier.  Vivisect code flow analysis does not track the
address; this module finds the address and invokes makeFunction(va).

Samples have been found with different instruction sequences for reaching the
address of runtime_main(); this module attempts all observed sequences.
'''

import logging

import envi
import envi.archs.i386.disasm

logger = logging.getLogger(__name__)

# Opcode sequence, where element [-5] is the important one.
_GOLANG_I386_INSTRS = ['cld', 'call', 'mov', 'mov', 'mov', 'mov', 'call',
                       'call', 'call', 'push', 'push', 'call', 'pop', 'pop']

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

    # There should be just one entry point (the public export).
    ep = vw.getEntryPoints()
    if len(ep) != 1:
        return

    # Search from the entry point function.
    ep_va = ep[0]
    bblocks = vw.getFunctionBlocks(ep_va)
    if not bblocks:
        return
    ptr_va, runtime_va = extract_golang_mainmain(vw, bblocks, filename)
    if runtime_va is None:
        return

    # Invoke codeflow on runtime_main().
    vw.addEntryPoint(runtime_va)
    logger.debug('discovered runtime function: 0x%x', runtime_va)
    vw.makeFunction(runtime_va)

    # Also mark the ptr_va as a pointer to runtime_va.
    vw.makePointer(ptr_va, tova=runtime_va)


def extract_golang_mainmain(vw, basic_blocks, filename):
    '''
    Find the basic block of interest and return the address of
    the pointer and its contents, runtime_main().

    The BB will contain the sequence of opcodes in _GOLANG_I386_INSTRS.
    The push instruction -5 from the end will load the contents of a memory
    address, and those contents are the runtime_main() address.
    '''
    op = find_golang_bblock(vw, basic_blocks, _GOLANG_I386_INSTRS, 5)
    if op is None:
        op = find_golang_bblock_via_stack(vw, filename)
        if op is None:
            return None, None

    # The key opcode is "push immediate", which identifies a pointer which
    # in turn identifies the GO function runtime_mainPC (aka runtime_main).
    ptr_va, runtime_va = parse_push_imm(vw, op, filename, get_content=True)
    return ptr_va, runtime_va


def find_golang_bblock(vw, basic_blocks, match, idx):
    '''
    Find the basic block of interest and return the opcode where
    the special sequence of opcodes begins.  Return None if not found.

    For this case, Vivisect interprets the entry as one large function
    (IDA Pro may break it into 2 or 3 functions linked by jmp instructions).
    The basic block of interest is in this function.
    '''
    the_bblock = None
    for bblock in basic_blocks:
        next_va = bblock[0]
        instrs = []
        while next_va < bblock[0] + bblock[1]:
            try:
                op = vw.parseOpcode(next_va)
            except envi.InvalidInstruction:
                op = None
            if op is None:
                return None
            if (len(instrs) > 0) or (op.mnem == match[0]):
                # Record instructions from the first opcode match.
                instrs.append(op)
            next_va += op.size
        if len(instrs) >= len(match):
            the_bblock = bblock
            break
    if the_bblock is None:
        return None

    for k in range(len(match)):
        if instrs[k].mnem != match[k]:
            return None
    return instrs[len(match) - idx]


def find_golang_bblock_via_stack(vw, filename):
    '''
    Find the basic block of interest and return the address where
    the special sequence of opcodes begins.  Return None if not found.

    Some GO executables use a stack manipulation in the entry point,
    and special logic is needed to locate the BB of interest.
    Example:  1897d2de0837090ec350004ef2f9fa87.
    '''
    # Start from the entry point (we already know there is only one).
    ep_va = vw.getEntryPoints()[0]

    # Expect a function with one BB, with a push to the next function
    # just before returning.
    basic_blocks = vw.getFunctionBlocks(ep_va)
    if len(basic_blocks) != 1:
        return None
    instrs = golang_collect_opcodes(vw, basic_blocks[0])
    if (len(instrs) < 2) or \
       (instrs[-1].mnem != 'ret') or \
       (instrs[-2].mnem != 'push'):
        return None
    op = instrs[-2]
    ptr_va, _ = parse_push_imm(vw, op, filename)
    if not ptr_va:
        return None

    # Analyze the function at the pointer if necessary.
    if not vw.isFunction(ptr_va):
        logger.debug('discovered new function(ptr): 0x%x', ptr_va)
        vw.makeFunction(ptr_va)

    # This function should contain the special basic block.
    basic_blocks = vw.getFunctionBlocks(ptr_va)
    return find_golang_bblock(vw, basic_blocks, _GOLANG_I386_INSTRS, 5)


def parse_push_imm(vw, opcode, filename, get_content=False):
    '''
    Parse an opcode that should be "push immediate", returning
    the address of the second operand.  Also return the content of the
    address if so requested.
    Return None, None if there is an error.
    '''
    if len(opcode.opers) != 1:
        return None, None
    if not isinstance(opcode.opers[0], envi.archs.i386.disasm.i386ImmOper):
        return None, None
    try:
        ptr_va = opcode.opers[0].getOperValue(opcode)
        if len(vw.readMemory(ptr_va, 4)) != 4:
            return None, None
        if get_content:
            runtime_va = vw.castPointer(ptr_va)
            if len(vw.readMemory(runtime_va, 4)) != 4:
                return None, None
        else:
            runtime_va = None
        return ptr_va, runtime_va
    except Exception as e:
        return None, None


def golang_collect_opcodes(vw, basic_block):
    '''
    Return a list of opcodes in a basic block.
    Return an empty list of an opcode could not be parsed.
    '''
    next_va = basic_block[0]
    opcodes = []
    while next_va < basic_block[0] + basic_block[1]:
        try:
            op = vw.parseOpcode(next_va)
        except envi.InvalidInstruction:
            return []
        opcodes.append(op)
        next_va += op.size
    return opcodes
