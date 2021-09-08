from envi.archs.i386.opconst import *
from . import regs as e_i386_regs
"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_Main = [
    (0, INS_ADD, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_G | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "add", 0, 0, 0),
    (0, INS_ADD, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_G | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "add", 0, 0, 0),
    (0, INS_ADD, ADDRMETH_G | OPTYPE_b | OP_W, ADDRMETH_E | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "add", 0, 0, 0),
    (0, INS_ADD, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "add", 0, 0, 0),
    (0, INS_ADD, OP_REG | OPTYPE_b | OP_W, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "add", e_i386_regs.REG_AL, 0, 0),  
    (0, INS_ADD, OP_REG | OP_W, ADDRMETH_I | OPTYPE_z | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "add", e_i386_regs.REG_EAX, 0, 0),  
    (0, INS_PUSH, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "push", e_i386_regs.REG_ES, 0, 0),
    (0, INS_POP, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "pop", e_i386_regs.REG_ES, 0, 0),
    (0, INS_OR, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_G | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "or", 0, 0, 0),
    (0, INS_OR, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_G | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "or", 0, 0, 0),
    (0, INS_OR, ADDRMETH_G | OPTYPE_b | OP_W, ADDRMETH_E | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "or", 0, 0, 0),
    (0, INS_OR, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "or", 0, 0, 0),
    (0, INS_OR, OP_REG | OPTYPE_b | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "or", e_i386_regs.REG_AL, 0, 0),
    (0, INS_OR, OP_REG | OP_W, ADDRMETH_I | OPTYPE_z | OP_R, ARG_NONE, cpu_80386, "or", e_i386_regs.REG_EAX, 0, 0),
    (0, INS_PUSH, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "push", e_i386_regs.REG_CS, 0, 0),
    (1, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 0, 0),  # 0x0f
# 0x10
    (0, INS_ADD, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_G | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "adc", 0, 0, 0),
    (0, INS_ADD, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_G | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "adc", 0, 0, 0),
    (0, INS_ADD, ADDRMETH_G | OPTYPE_b | OP_W, ADDRMETH_E | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "adc", 0, 0, 0),
    (0, INS_ADD, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "adc", 0, 0, 0),
    (0, INS_ADD, OP_REG | OP_W, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "adc", e_i386_regs.REG_AL, 0, 0),  
    (0, INS_ADD, OP_REG | OP_W, ADDRMETH_I | OPTYPE_z | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "adc", e_i386_regs.REG_EAX, 0, 0),  
    (0, INS_PUSH, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "push", e_i386_regs.REG_SS, 0, 0),
    (0, INS_POP, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "pop", e_i386_regs.REG_SS, 0, 0),
    (0, INS_SUB, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_G | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "sbb", 0, 0, 0),
    (0, INS_SUB, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_G | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "sbb", 0, 0, 0),
    (0, INS_SUB, ADDRMETH_G | OPTYPE_b | OP_W, ADDRMETH_E | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "sbb", 0, 0, 0),
    (0, INS_SUB, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "sbb", 0, 0, 0),
    (0, INS_SUB, OP_REG | OP_W, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "sbb", e_i386_regs.REG_AL, 0, 0),
    (0, INS_SUB, OP_REG | OP_W, ADDRMETH_I | OPTYPE_z | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "sbb", e_i386_regs.REG_EAX, 0, 0),
    (0, INS_PUSH, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "push", e_i386_regs.REG_DS, 0, 0),
    (0, INS_POP, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "pop", e_i386_regs.REG_DS, 0, 0),
# 0x20
    (0, INS_AND, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_G | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "and", 0, 0, 0),
    (0, INS_AND, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_G | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "and", 0, 0, 0),
    (0, INS_AND, ADDRMETH_G | OPTYPE_b | OP_W, ADDRMETH_E | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "and", 0, 0, 0),
    (0, INS_AND, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "and", 0, 0, 0),
    (0, INS_AND, OP_REG | OP_W, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "and", e_i386_regs.REG_AL, 0, 0),
    (0, INS_AND, OP_REG | OP_W, ADDRMETH_I | OPTYPE_z | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "and", e_i386_regs.REG_EAX, 0, 0),
    (0, INSTR_PREFIX, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 0, 0),
    (0, INS_BCDCONV, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "daa", 0, 0, 0),
    (0, INS_SUB, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_G | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "sub", 0, 0, 0),
    (0, INS_SUB, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_G | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "sub", 0, 0, 0),
    (0, INS_SUB, ADDRMETH_G | OPTYPE_b | OP_W, ADDRMETH_E | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "sub", 0, 0, 0),
    (0, INS_SUB, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "sub", 0, 0, 0),
    (0, INS_SUB, OP_REG | OP_W, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "sub", e_i386_regs.REG_AL, 0, 0),
    (0, INS_SUB, OP_REG | OP_W, ADDRMETH_I | OPTYPE_z | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "sub", e_i386_regs.REG_EAX, 0, 0),
    (0, INSTR_PREFIX, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 0, 0),
    (0, INS_BCDCONV, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "das", 0, 0, 0),
# 0x30
    (0, INS_XOR, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_G | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "xor", 0, 0, 0),
    (0, INS_XOR, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_G | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "xor", 0, 0, 0),
    (0, INS_XOR, ADDRMETH_G | OPTYPE_b | OP_W, ADDRMETH_E | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "xor", 0, 0, 0),
    (0, INS_XOR, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "xor", 0, 0, 0),
    (0, INS_XOR, OP_REG | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "xor", e_i386_regs.REG_AL, 0, 0),
    (0, INS_XOR, OP_REG | OP_W, ADDRMETH_I | OPTYPE_z | OP_R, ARG_NONE, cpu_80386, "xor", e_i386_regs.REG_EAX, 0, 0),
    (0, INSTR_PREFIX, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 0, 0),
    (0, INS_BCDCONV, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "aaa", 0, 0, 0),
    (0, INS_CMP, ADDRMETH_E | OPTYPE_b | OP_R, ADDRMETH_G | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "cmp", 0, 0, 0),
    (0, INS_CMP, ADDRMETH_E | OPTYPE_v | OP_R, ADDRMETH_G | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "cmp", 0, 0, 0),
    (0, INS_CMP, ADDRMETH_G | OPTYPE_b | OP_R, ADDRMETH_E | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "cmp", 0, 0, 0),
    (0, INS_CMP, ADDRMETH_G | OPTYPE_v | OP_R, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "cmp", 0, 0, 0),
    (0, INS_CMP, OP_REG | OP_R, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "cmp", e_i386_regs.REG_AL, 0, 0),
    (0, INS_CMP, OP_REG | OP_R, ADDRMETH_I | OPTYPE_z | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "cmp", e_i386_regs.REG_EAX, 0, 0),
    (0, INSTR_PREFIX, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 0, 0),
    (0, INS_BCDCONV, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "aas", 0, 0, 0),
# 0x40
    (0, INS_INC, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "inc", e_i386_regs.REG_EAX, 0, 0),
    (0, INS_INC, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "inc", e_i386_regs.REG_ECX, 0, 0),
    (0, INS_INC, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "inc", e_i386_regs.REG_EDX, 0, 0),
    (0, INS_INC, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "inc", e_i386_regs.REG_EBX, 0, 0),
    (0, INS_INC, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "inc", e_i386_regs.REG_ESP, 0, 0),
    (0, INS_INC, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "inc", e_i386_regs.REG_EBP, 0, 0),
    (0, INS_INC, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "inc", e_i386_regs.REG_ESI, 0, 0),
    (0, INS_INC, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "inc", e_i386_regs.REG_EDI, 0, 0),

    (0, INS_DEC, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "dec", e_i386_regs.REG_EAX, 0, 0),
    (0, INS_DEC, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "dec", e_i386_regs.REG_ECX, 0, 0),
    (0, INS_DEC, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "dec", e_i386_regs.REG_EDX, 0, 0),
    (0, INS_DEC, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "dec", e_i386_regs.REG_EBX, 0, 0),
    (0, INS_DEC, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "dec", e_i386_regs.REG_ESP, 0, 0),
    (0, INS_DEC, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "dec", e_i386_regs.REG_EBP, 0, 0),
    (0, INS_DEC, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "dec", e_i386_regs.REG_ESI, 0, 0),
    (0, INS_DEC, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "dec", e_i386_regs.REG_EDI, 0, 0),
# 0x50
    (0, INS_PUSH, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "push", e_i386_regs.REG_EAX, 0, 0),
    (0, INS_PUSH, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "push", e_i386_regs.REG_ECX, 0, 0),
    (0, INS_PUSH, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "push", e_i386_regs.REG_EDX, 0, 0),
    (0, INS_PUSH, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "push", e_i386_regs.REG_EBX, 0, 0),
    (0, INS_PUSH, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "push", e_i386_regs.REG_ESP, 0, 0),
    (0, INS_PUSH, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "push", e_i386_regs.REG_EBP, 0, 0),
    (0, INS_PUSH, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "push", e_i386_regs.REG_ESI, 0, 0),
    (0, INS_PUSH, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "push", e_i386_regs.REG_EDI, 0, 0),

    (0, INS_POP, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "pop", e_i386_regs.REG_EAX, 0, 0),
    (0, INS_POP, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "pop", e_i386_regs.REG_ECX, 0, 0),
    (0, INS_POP, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "pop", e_i386_regs.REG_EDX, 0, 0),
    (0, INS_POP, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "pop", e_i386_regs.REG_EBX, 0, 0),
    (0, INS_POP, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "pop", e_i386_regs.REG_ESP, 0, 0),
    (0, INS_POP, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "pop", e_i386_regs.REG_EBP, 0, 0),
    (0, INS_POP, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "pop", e_i386_regs.REG_ESI, 0, 0),
    (0, INS_POP, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "pop", e_i386_regs.REG_EDI, 0, 0),
# 0x60
    (0, INS_PUSHREGS, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "pushad", 0, 0, 0),
    (0, INS_POPREGS, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "popad", 0, 0, 0),
    (0, INS_BOUNDS, ADDRMETH_G | OPTYPE_v | OP_R, ADDRMETH_M | OPTYPE_a | OP_R, ARG_NONE, cpu_80386, "bound", 0, 0, 0),
    (0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_R, ADDRMETH_G | OPTYPE_w | OP_R, ARG_NONE, cpu_80386, "arpl", 0, 0, 0),
    (0, INSTR_PREFIX, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 0, 0),
    (0, INSTR_PREFIX, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 0, 0),
    (44, INSTR_PREFIX, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 0, 0),  # 0x66
    (0, INSTR_PREFIX, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 0, 0),
    (0, INS_PUSH, ADDRMETH_I | OPTYPE_v | OP_R | OP_SIGNED, ARG_NONE, ARG_NONE, cpu_80386, "push", 0, 0, 0),
    (0, INS_MUL, ADDRMETH_G | OPTYPE_v | OP_R, ADDRMETH_E | OPTYPE_v | OP_R, ADDRMETH_I | OP_SIGNED |OPTYPE_z | OP_R, cpu_80386, "imul", 0, 0, 0),
    (0, INS_PUSH, ADDRMETH_I | OPTYPE_b | OP_R | OP_SIGNED, ARG_NONE, ARG_NONE, cpu_80386, "push", 0, 0, 0),
    (0, INS_MUL, ADDRMETH_G | OPTYPE_v | OP_R, ADDRMETH_E | OPTYPE_v | OP_R, ADDRMETH_I |  OP_SIGNED | OP_R | OPTYPE_b, cpu_80386, "imul", 0, 0, 0),
    (0, INS_IN,  ADDRMETH_Y | OPTYPE_b | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "insb", 0, e_i386_regs.REG_EDX, 0),
    (0, INS_IN,  ADDRMETH_Y | OPTYPE_z | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "insd", 0, e_i386_regs.REG_EDX, 0),
    (0, INS_OUT,  OP_REG | OP_W, ADDRMETH_X | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "outsb", e_i386_regs.REG_EDX, 0, 0),
    (0, INS_OUT,  OP_REG | OP_W, ADDRMETH_X | OPTYPE_z | OP_R, ARG_NONE, cpu_80386, "outsd", e_i386_regs.REG_EDX, 0, 0),
# 0x70
    (0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jo", 0, 0, 0),
    (0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jno", 0, 0, 0),
    (0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jc", 0, 0, 0),
    (0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jnc", 0, 0, 0),
    (0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jz", 0, 0, 0),
    (0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jnz", 0, 0, 0),
    (0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jbe", 0, 0, 0),
    (0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "ja", 0, 0, 0),
    (0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "js", 0, 0, 0),
    (0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jns", 0, 0, 0),
    (0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jpe", 0, 0, 0),
    (0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jpo", 0, 0, 0),
    (0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jl", 0, 0, 0),
    (0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jge", 0, 0, 0),
    (0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jle", 0, 0, 0),
    (0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jg", 0, 0, 0),
# 0x80
    (2, 0, ADDRMETH_E | OPTYPE_b, ADDRMETH_I | OPTYPE_b, ARG_NONE,cpu_80386, 0, 0, 0, 0),
    (3, 0, ADDRMETH_E | OPTYPE_v, ADDRMETH_I | OPTYPE_v, ARG_NONE, cpu_80386, 0, 0, 0, 0),
    (4, 0, ADDRMETH_E | OPTYPE_v, ADDRMETH_I | OPTYPE_b, ARG_NONE, cpu_80386, 0, 0, 0, 0),
    (5, 0,  ADDRMETH_E | OPTYPE_v, ADDRMETH_I | OPTYPE_b, ARG_NONE, cpu_80386, 0, 0, 0, 0),
    (0, INS_TEST, ADDRMETH_E | OPTYPE_b | OP_R, ADDRMETH_G | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "test", 0, 0, 0),
    (0, INS_TEST, ADDRMETH_E | OPTYPE_v | OP_R, ADDRMETH_G | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "test", 0, 0, 0),
    (0, INS_XCHG, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_G | OPTYPE_b | OP_W, ARG_NONE, cpu_80386, "xchg", 0, 0, 0),
    (0, INS_XCHG, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_G | OPTYPE_v | OP_W, ARG_NONE, cpu_80386, "xchg", 0, 0, 0),
    (0, INS_MOV, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_G | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "mov", 0, 0, 0),
    (0, INS_MOV, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_G | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "mov", 0, 0, 0),
    (0, INS_MOV, ADDRMETH_G | OPTYPE_b | OP_W, ADDRMETH_E | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "mov", 0, 0, 0),
    (0, INS_MOV, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "mov", 0, 0, 0),
    (0, INS_MOV, ADDRMETH_E | OPTYPE_v | OP_W | OP_MEM_W, ADDRMETH_S | OPTYPE_w | OP_R, ARG_NONE, cpu_80386, "mov", 0, 0, 0),
    (0, INS_LEA, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_M | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "lea", 0, 0, 0),
    (0, INS_MOV, ADDRMETH_S | OPTYPE_w | OP_W, ADDRMETH_E | OPTYPE_v | OP_R | OP_MEM_W, ARG_NONE, cpu_80386, "mov", 0, 0, 0),
    (0, INS_POP, ADDRMETH_M | OPTYPE_v | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "pop", 0, 0, 0),
# 0x90
    (0, INS_NOP, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "nop", 0, 0, 0),
    (0, INS_XCHG, OP_REG | OP_W, OP_REG | OP_W, ARG_NONE, cpu_80386, "xchg", e_i386_regs.REG_EAX, e_i386_regs.REG_ECX, 0),
    (0, INS_XCHG, OP_REG | OP_W, OP_REG | OP_W, ARG_NONE, cpu_80386, "xchg", e_i386_regs.REG_EAX, e_i386_regs.REG_EDX, 0),
    (0, INS_XCHG, OP_REG | OP_W, OP_REG | OP_W, ARG_NONE, cpu_80386, "xchg", e_i386_regs.REG_EAX, e_i386_regs.REG_EBX, 0),
    (0, INS_XCHG, OP_REG | OP_W, OP_REG | OP_W, ARG_NONE, cpu_80386, "xchg", e_i386_regs.REG_EAX, e_i386_regs.REG_ESP, 0),
    (0, INS_XCHG, OP_REG | OP_W, OP_REG | OP_W, ARG_NONE, cpu_80386, "xchg", e_i386_regs.REG_EAX, e_i386_regs.REG_EBP, 0),
    (0, INS_XCHG, OP_REG | OP_W, OP_REG | OP_W, ARG_NONE, cpu_80386, "xchg", e_i386_regs.REG_EAX, e_i386_regs.REG_ESI, 0),
    (0, INS_XCHG, OP_REG | OP_W, OP_REG | OP_W, ARG_NONE, cpu_80386, "xchg", e_i386_regs.REG_EAX, e_i386_regs.REG_EDI, 0),
    (0, INS_SZCONV, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "cwde", 0, 0, 0),
    (0, INS_SZCONV, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "cdq", 0, 0, 0),
    (0, INS_CALL, ADDRMETH_A | OPTYPE_p | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "callf", 0, 0, 0),
    (0, INS_SYSTEM, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "wait", 0, 0, 0),
    (0, INS_PUSHFLAGS, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "pushfd", 0, 0, 0),
    (0, INS_POPFLAGS, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "popfd", 0, 0, 0),
    (0, INS_MOV, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "sahf", 0, 0, 0),
    (0, INS_MOV, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "lahf", 0, 0, 0),
# 0xa0
    (0, INS_MOV, OP_REG | OP_W, ADDRMETH_O | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "mov", e_i386_regs.REG_AL, 0, 0),
    (0, INS_MOV, OP_REG | OP_W, ADDRMETH_O | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "mov", e_i386_regs.REG_EAX, 0, 0),
    (0, INS_MOV, ADDRMETH_O | OPTYPE_b | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "mov", 0, e_i386_regs.REG_AL, 0),
    (0, INS_MOV, ADDRMETH_O | OPTYPE_v | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "mov", 0, e_i386_regs.REG_EAX, 0),
    (0, INS_STRMOV, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "movsb", 0, 0, 0),
    (0, INS_STRMOV, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "movsd", 0, 0, 0),
    (0, INS_STRCMP, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "cmpsb", 0, 0, 0),
    (0, INS_STRCMP, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "cmpsd", 0, 0, 0),
    (0, INS_TEST, OP_REG | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "test", e_i386_regs.REG_AL, 0, 0),
    (0, INS_TEST, OP_REG | OP_R, ADDRMETH_I | OPTYPE_z | OP_R, ARG_NONE, cpu_80386, "test", e_i386_regs.REG_EAX, 0, 0),
    (0, INS_STRSTOR, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "stosb", 0, 0, 0),
    (0, INS_STRSTOR, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "stosd", 0, 0, 0),
    (0, INS_STRLOAD, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "lodsb", 0, 0, 0),
    (0, INS_STRLOAD, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "lodsd", 0, 0, 0),
    (0, INS_STRCMP, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "scasb", 0, 0, 0),
    (0, INS_STRCMP, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "scasd", 0, 0, 0),
# 0xb0
    (0, INS_MOV, OP_REG | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "mov", e_i386_regs.REG_AL, 0, 0),
    (0, INS_MOV, OP_REG | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "mov", e_i386_regs.REG_CL, 0, 0),  
    (0, INS_MOV, OP_REG | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "mov", e_i386_regs.REG_DL, 0, 0),  
    (0, INS_MOV, OP_REG | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "mov", e_i386_regs.REG_BL, 0, 0),  
# FIXME 64
    (0, INS_MOV, OP_REG | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "mov", e_i386_regs.REG_AH, 0, 0),  
    (0, INS_MOV, OP_REG | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "mov", e_i386_regs.REG_CH, 0, 0),  
    (0, INS_MOV, OP_REG | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "mov", e_i386_regs.REG_DH, 0, 0),  
    (0, INS_MOV, OP_REG | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "mov", e_i386_regs.REG_BH, 0, 0),  

    (0, INS_MOV, OP_REG | OP_W, ADDRMETH_I | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "mov", e_i386_regs.REG_EAX, 0, 0),  
    (0, INS_MOV, OP_REG | OP_W, ADDRMETH_I | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "mov", e_i386_regs.REG_ECX, 0, 0),  
    (0, INS_MOV, OP_REG | OP_W, ADDRMETH_I | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "mov", e_i386_regs.REG_EDX, 0, 0),  
    (0, INS_MOV, OP_REG | OP_W, ADDRMETH_I | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "mov", e_i386_regs.REG_EBX, 0, 0),  
    (0, INS_MOV, OP_REG | OP_W, ADDRMETH_I | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "mov", e_i386_regs.REG_ESP, 0, 0),  
    (0, INS_MOV, OP_REG | OP_W, ADDRMETH_I | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "mov", e_i386_regs.REG_EBP, 0, 0),  
    (0, INS_MOV, OP_REG | OP_W, ADDRMETH_I | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "mov", e_i386_regs.REG_ESI, 0, 0),  
    (0, INS_MOV, OP_REG | OP_W, ADDRMETH_I | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "mov", e_i386_regs.REG_EDI, 0, 0),  
# 0xc0
    (6, 0,  ADDRMETH_E | OPTYPE_b, ADDRMETH_I | OPTYPE_b, ARG_NONE, cpu_80386, 0, 0, 0, 0),  
    (7, 0,  ADDRMETH_E | OPTYPE_v, ADDRMETH_I | OPTYPE_b, ARG_NONE, cpu_80386, 0, 0, 0, 0),  
    (0, INS_RET, ADDRMETH_I | OPTYPE_w | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "ret", 0, 0, 0),  
    (0, INS_RET, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "ret", 0, 0, 0),  
    (0, INS_MOV, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_M | OPTYPE_p | OP_R, ARG_NONE, cpu_80386, "les", 0, 0, 0),  
    (0, INS_MOV, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_M | OPTYPE_p | OP_R, ARG_NONE, cpu_80386, "lds", 0, 0, 0),  
    (0, INS_MOV, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "mov", 0, 0, 0),  
    (0, INS_MOV, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_I | OPTYPE_z | OP_R, ARG_NONE, cpu_80386, "mov", 0, 0, 0),  
    (0, INS_ENTER, ADDRMETH_I | OPTYPE_w | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "enter", 0, 0, 0),  
    (0, INS_LEAVE, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "leave", 0, 0, 0),  
    (0, INS_RET, ADDRMETH_I | OPTYPE_w | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "retf", 0, 0, 0),  
    (0, INS_RET, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "retf", 0, 0, 0),  
    (0, INS_DEBUG, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "int3", 0, 0, 0),  
    (0, INS_TRAP, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "int", 0, 0, 0),  
    (0, INS_OFLOW, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "into", 0, 0, 0),  
    (0, INS_TRET, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "iret", 0, 0, 0),  
# 0xd0
    (8, 0,  ADDRMETH_E | OPTYPE_b, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 1, 0),  
    (9, 0, ADDRMETH_E | OPTYPE_v, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 1, 0),  
    (10, 0, ADDRMETH_E | OPTYPE_b, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, e_i386_regs.REG_CL, 0),  
    (11, 0, ADDRMETH_E | OPTYPE_v, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, e_i386_regs.REG_CL, 0),  
    (0, INS_BCDCONV, ADDRMETH_I | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "aam", 0, 0, 0),  
    (0, INS_BCDCONV, ADDRMETH_I | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "aad", 0, 0, 0),  
    (0, INS_OTHER, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "salc", e_i386_regs.REG_AL, 0, 0),
    (0, INS_XLAT, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "xlat", 0, 0, 0),  
    (26, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 0, 0),  
    (28, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 0, 0),  
    (30, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 0, 0),  
    (32, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 0, 0),  
    (34, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 0, 0),  
    (36, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 0, 0),  
    (38, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 0, 0),  
    (40, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 0, 0),  
# 0xe0
    (0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "loopnz", 0, 0, 0),  
    (0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "loopz", 0, 0, 0),  
    (0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "loop", 0, 0, 0),  
    (0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jecxz", 0, 0, 0),  
    (0, INS_IN, OP_REG | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "in", e_i386_regs.REG_AL, 0, 0),  
    (0, INS_IN, OP_REG | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "in", e_i386_regs.REG_EAX, 0, 0),  
    (0, INS_OUT, ADDRMETH_I | OPTYPE_b | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "out", 0, e_i386_regs.REG_AL, 0),  
    (0, INS_OUT, ADDRMETH_I | OPTYPE_b | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "out", 0, e_i386_regs.REG_EAX, 0),  
    (0, INS_CALL, ADDRMETH_J | OPTYPE_v | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "call", 0, 0, 0),  
    (0, INS_BRANCH, ADDRMETH_J | OPTYPE_v | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jmp", 0, 0, 0),  
    (0, INS_BRANCH, ADDRMETH_A | OPTYPE_p | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jmp", 0, 0, 0),  
    (0, INS_BRANCH, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jmp", 0, 0, 0),  
    (0, INS_IN, OP_REG | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "in", e_i386_regs.REG_AL, e_i386_regs.REG_DX, 0),  
    (0, INS_IN, OP_REG | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "in", e_i386_regs.REG_EAX, e_i386_regs.REG_DX, 0),  
    (0, INS_OUT, OP_REG | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "out", e_i386_regs.REG_DX, e_i386_regs.REG_AL, 0),  
    (0, INS_OUT, OP_REG | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "out", e_i386_regs.REG_DX, e_i386_regs.REG_EAX, 0),  
# 0xf0
    ( 0, INSTR_PREFIX, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "lock:", 0, 0, 0),  
    (0, INS_TRAP, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "int1", 0, 0, 0),
    (45, INSTR_PREFIX, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 0, 0),  
    (46, INSTR_PREFIX, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 0, 0),  
    (0, INS_HALT, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "hlt", 0, 0, 0),  
    (0, INS_TOGCF, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "cmc", 0, 0, 0),  
    (12, 0,  ADDRMETH_E | OPTYPE_b, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 0, 0),  
    (13, 0, ADDRMETH_E | OPTYPE_v, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 0, 0),  
    (0, INS_CLEARCF, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "clc", 0, 0, 0),  
    (0, INS_SETCF, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "stc", 0, 0, 0),  
    (0, INS_SYSTEM, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "cli", 0, 0, 0),  
    (0, INS_SYSTEM, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "sti", 0, 0, 0),  
    (0, INS_CLEARDF, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "cld", 0, 0, 0),  
    (0, INS_SETDF, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "std", 0, 0, 0),  
    (14, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 0, 0),  
    (15, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 0, 0   )
]



"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_0F = [
# 0f00
(16, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 0, 0),  
(17, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 0, 0),  
(0, INS_SYSTEM, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_w | OP_R, ARG_NONE, cpu_80386, "lar", 0, 0, 0),  
( 0, INS_SYSTEM, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_w | OP_R, ARG_NONE, cpu_80386, "lsl", 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, INS_SYSTEM, ARG_NONE, ARG_NONE, ARG_NONE, cpu_AMD64, "syscall", 0, 0, 0),
(0, INS_SYSTEM, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "clts", 0, 0, 0),  
(0, INS_SYSTEM, ARG_NONE, ARG_NONE, ARG_NONE, cpu_AMD64, "sysret", 0, 0, 0),
(0, INS_SYSTEM, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80486, "invd", 0, 0, 0),  
(0, INS_SYSTEM, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80486, "wbinvd", 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 0, 0),  
(0, INS_INVALIDOP, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "ud2", 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, INS_OTHER, ADDRMETH_E | OPTYPE_v, ARG_NONE, ARG_NONE, cpu_80386, "prefetchw", 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
# 0f10
( 0, INS_MOV, ADDRMETH_V | OPTYPE_ps | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R, ARG_NONE, cpu_PENTIUM2, "movups", 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_W | OPTYPE_ps | OP_W, ADDRMETH_V | OPTYPE_ps | OP_R, ARG_NONE, cpu_PENTIUM2, "movups", 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_V | OPTYPE_q | OP_W, ADDRMETH_W | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "movlps", 0, 0, 0),
( 0, INS_MOV, ADDRMETH_M | OPTYPE_q | OP_W, ADDRMETH_V | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "movlps", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_V | OPTYPE_ps | OP_W, ADDRMETH_W | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "unpcklps", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_V | OPTYPE_ps | OP_W, ADDRMETH_W | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "unpckhps", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_V | OPTYPE_q | OP_W, ADDRMETH_M | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "movhps", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_M | OPTYPE_q | OP_W, ADDRMETH_V | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "movhps", 0, 0, 0),  
(18, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, INS_NOP, ADDRMETH_E | OPTYPE_v, ARG_NONE, ARG_NONE, cpu_80386, "nop", 0, 0, 0),
(0, INS_NOP, ADDRMETH_E | OPTYPE_v, ARG_NONE, ARG_NONE, cpu_80386, "nop", 0, 0, 0),
(0, INS_NOP, ADDRMETH_E | OPTYPE_v, ARG_NONE, ARG_NONE, cpu_80386, "nop", 0, 0, 0),
(0, INS_NOP, ADDRMETH_E | OPTYPE_v, ARG_NONE, ARG_NONE, cpu_80386, "nop", 0, 0, 0),
# 0f20
( 0, INS_MOV, ADDRMETH_R | OPTYPE_d | OP_W, ADDRMETH_C | OPTYPE_d | OP_R, ARG_NONE, cpu_80386, "mov", 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_R | OPTYPE_d | OP_W, ADDRMETH_D | OPTYPE_d | OP_R, ARG_NONE, cpu_80386, "mov", 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_C | OPTYPE_d | OP_W, ADDRMETH_R | OPTYPE_d | OP_R, ARG_NONE, cpu_80386, "mov", 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_D | OPTYPE_d | OP_W, ADDRMETH_R | OPTYPE_d | OP_R, ARG_NONE, cpu_80386, "mov", 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_V | OPTYPE_ps | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R, ARG_NONE, cpu_PENTIUM2, "movaps", 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_W | OPTYPE_ps | OP_W, ADDRMETH_V | OPTYPE_ps | OP_R, ARG_NONE, cpu_PENTIUM2, "movaps", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_V | OPTYPE_ps | OP_R, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "cvtpi2ps", 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_M | OPTYPE_ps | OP_W, ADDRMETH_V | OPTYPE_ps | OP_R, ARG_NONE, cpu_PENTIUM2, "movntps", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_W | OPTYPE_pi | OP_R, ARG_NONE, cpu_PENTIUM2, "cvttps2pi", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_Q | OPTYPE_q | OP_R, ADDRMETH_W | OPTYPE_ps | OP_R, ARG_NONE, cpu_PENTIUM2, "cvtps2pi", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_W | OPTYPE_ss | OP_R, ARG_NONE, cpu_PENTIUM2, "ucomiss", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_V | OPTYPE_ps | OP_W, ADDRMETH_W | OPTYPE_ps | OP_W, ARG_NONE, cpu_PENTIUM2, "comiss", 0, 0, 0),  
# 0f30
(0, INS_SYSTEM, ARG_NONE, ARG_NONE, ARG_NONE, cpu_PENTIUM, "wrmsr", 0, 0, 0),  
(0, INS_SYSTEM, ARG_NONE, ARG_NONE, ARG_NONE, cpu_PENTIUM, "rdtsc", 0, 0, 0),  
(0, INS_SYSTEM, ARG_NONE, ARG_NONE, ARG_NONE, cpu_PENTIUM, "rdmsr", 0, 0, 0),  
(0, INS_OTHER, ARG_NONE, ARG_NONE, ARG_NONE, cpu_PENTPRO, "rdpmc", 0, 0, 0),  
(0, INS_SYSTEM, ARG_NONE, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "sysenter", 0, 0, 0),  
(0, INS_SYSTEM, ARG_NONE, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "sysexit", 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(55, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  # 3-byte escape 38
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(57, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  # 3-byte escape 3a
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
# 0f40
( 0, INS_MOVCC, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_PENTPRO, "cmovo", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_PENTPRO, "cmovno", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_PENTPRO, "cmovc", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_PENTPRO, "cmovnc", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_PENTPRO, "cmovz", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_PENTPRO, "cmovnz", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_PENTPRO, "cmovbe", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_PENTPRO, "cmova", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_PENTPRO, "cmovs", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_PENTPRO, "cmovns", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_PENTPRO, "cmovpe", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_PENTPRO, "cmovpo", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_PENTPRO, "cmovl", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_PENTPRO, "cmovge", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_PENTPRO, "cmovle", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_PENTPRO, "cmovg", 0, 0, 0),  
# 0f50
( 0, INS_MOV, ADDRMETH_G | OPTYPE_d | OP_W, ADDRMETH_U | OPTYPE_ps | OP_R, ARG_NONE, cpu_PENTIUM2, "movmskps", 0, 0, 0),
( 0, INS_ARITH, ADDRMETH_V | OPTYPE_ps | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R, ARG_NONE, cpu_PENTIUM2, "sqrtps", 0, 0, 0),  
( 0, INS_ARITH, ADDRMETH_V | OPTYPE_ps | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R, ARG_NONE, cpu_PENTIUM2, "rsqrtps", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_V | OPTYPE_ps | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R, ARG_NONE, cpu_PENTIUM2, "rcpps", 0, 0, 0),  
( 0, INS_AND, ADDRMETH_V | OPTYPE_ps | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R, ARG_NONE, cpu_PENTIUM2, "andps", 0, 0, 0),  
( 0, INS_AND, ADDRMETH_V | OPTYPE_ps | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R, ARG_NONE, cpu_PENTIUM2, "andnps", 0, 0, 0),  
( 0, INS_OR, ADDRMETH_V | OPTYPE_ps | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R, ARG_NONE, cpu_PENTIUM2, "orps", 0, 0, 0),  
( 0, INS_XOR, ADDRMETH_V | OPTYPE_ps | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R, ARG_NONE, cpu_PENTIUM2, "xorps", 0, 0, 0),  
( 0, INS_ADD, ADDRMETH_V | OPTYPE_ps | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R, ARG_NONE, cpu_PENTIUM2, "addps", 0, 0, 0),  
( 0, INS_MUL, ADDRMETH_V | OPTYPE_ps | OP_R, ADDRMETH_W | OPTYPE_ps | OP_R, ARG_NONE, cpu_PENTIUM2, "mulps", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_V | OPTYPE_pd | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R, ARG_NONE, cpu_PENTIUM2, "cvtps2pd", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_V | OPTYPE_ps | OP_W, ADDRMETH_W | OPTYPE_dq |OP_R, ARG_NONE, cpu_PENTIUM2, "cvtdq2ps", 0, 0, 0),  
( 0, INS_SUB, ADDRMETH_V | OPTYPE_ps | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R, ARG_NONE, cpu_PENTIUM2, "subps", 0, 0, 0),  
( 0, INS_ARITH, ADDRMETH_V | OPTYPE_ps | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R, ARG_NONE, cpu_PENTIUM2, "minps", 0, 0, 0),  
( 0, INS_DIV, ADDRMETH_V | OPTYPE_ps | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R, ARG_NONE, cpu_PENTIUM2, "divps", 0, 0, 0),  
( 0, INS_ARITH, ADDRMETH_V | OPTYPE_ps | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R, ARG_NONE, cpu_PENTIUM2, "maxps", 0, 0, 0),  
# 0f60
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTMMX, "punpcklbw", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTMMX, "punpcklwd", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTMMX, "punpckldq", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "packsswb", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "pcmpgtb", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "pcmpgtw", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "pcmpgtd", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "packuswb", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTMMX, "punpckhbw", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTMMX, "punpckhwd", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTMMX, "punpckhdq", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTMMX, "packssdw", 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_P | OPTYPE_d | OP_W, ADDRMETH_E | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTMMX, "movd", 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "movq", 0, 0, 0),  
# 0f70
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ADDRMETH_I |  OPTYPE_b | OP_R, cpu_PENTIUM2, "pshufw", 0, 0, 0),  
(19, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_PENTMMX, 0, 0, 0, 0),  
(20, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_PENTMMX, 0, 0, 0, 0),  
(21, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_PENTMMX, 0, 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "pcmpeqb", 0, 0, 0),  
( 0, INS_CMP, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "pcmpeqw", 0, 0, 0),  
( 0, INS_CMP, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "pcmpeqd", 0, 0, 0),  
(0, INS_OTHER, ARG_NONE, ARG_NONE, ARG_NONE, cpu_PENTMMX, "emms", 0, 0, 0),  
(0, INS_SYSTEM, ADDRMETH_E | OPTYPE_d | OP_W, ADDRMETH_G | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTIUM2, "vmread", 0, 0, 0),  
(0, INS_SYSTEM, ADDRMETH_G | OPTYPE_d | OP_W, ADDRMETH_E | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTIUM2, "vmwrite", 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_Q | OPTYPE_d | OP_W, ADDRMETH_P | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTMMX, "movd", 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_Q | OPTYPE_q | OP_W, ADDRMETH_P | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "movq", 0, 0, 0),  
# 0f80
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_z | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jo", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_z | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jno", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_z | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jc", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_z | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jnc", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_z | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jz", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_z | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jnz", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_z | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jbe", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_z | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "ja", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_z | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "js", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_z | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jns", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_z | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jpe", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_z | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jpo", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_z | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jl", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_z | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jge", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_z | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jle", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_z | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jg", 0, 0, 0),  
# 0f90
( 0, INS_MOVCC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "seto", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "setno", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "setc", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "setnc", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "setz", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "setnz", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "setbe", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "seta", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "sets", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "setns", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "setpe", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "setpo", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "setl", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "setge", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "setle", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "setg", 0, 0, 0),  
# 0fa0
(0, INS_PUSH, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "push", e_i386_regs.REG_FS, 0, 0),  
(0, INS_POP, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "pop", e_i386_regs.REG_FS, 0, 0),  
(0, INS_CPUID, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80486, "cpuid", 0, 0, 0),  
(0, INS_BITTEST, ADDRMETH_E | OPTYPE_v | OP_R, ADDRMETH_G | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "bt", 0, 0, 0),  
(0, INS_SHL, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_G | OPTYPE_v | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_80386, "shld", 0, 0, 0),  
(0, INS_SHL, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_G | OPTYPE_v | OP_R, OP_R | OP_REG, cpu_80386, "shld", 0, 0, e_i386_regs.REG_CL), 
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, INS_PUSH, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "push", e_i386_regs.REG_GS, 0, 0),  
(0, INS_POP, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "pop", e_i386_regs.REG_GS, 0, 0),  
(0, INS_SYSTEM, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "rsm", 0, 0, 0),
(0, INS_BITTEST, ADDRMETH_E | OPTYPE_v | OP_R, ADDRMETH_G | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "bts", 0, 0, 0),  
(0, INS_SHR, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_G | OPTYPE_v | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_80386, "shrd", 0, 0, 0),  
(0, INS_SHR, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_G | OPTYPE_v | OP_R, OP_R | OP_REG, cpu_80386, "shrd", 0, 0, e_i386_regs.REG_CL), 
(22, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_PENTIUM2, 0, 0, 0, 0),  
(0, INS_MUL, ADDRMETH_G | OPTYPE_v | OP_R, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "imul", 0, 0, 0),  
# 0fb0
(0, INS_XCHGCC, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_G | OPTYPE_b | OP_W, ARG_NONE, cpu_80486, "cmpxchg", 0, 0, 0),  
(0, INS_XCHGCC, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_G | OPTYPE_v | OP_W, ARG_NONE, cpu_80486, "cmpxchg", 0, 0, 0),  
(0, INS_MOV, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_M | OPTYPE_p | OP_R, ARG_NONE, cpu_80386, "lss", 0, 0, 0),  
(0, INS_BITTEST, ADDRMETH_E | OPTYPE_v | OP_R, ADDRMETH_G | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "btr", 0, 0, 0),  
(0, INS_MOV, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_M | OPTYPE_p| OP_R, ARG_NONE, cpu_80386, "lfs", 0, 0, 0),  
(0, INS_MOV, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_M | OPTYPE_p | OP_R, ARG_NONE, cpu_80386, "lgs", 0, 0, 0),  
(0, INS_MOV, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "movzx", 0, 0, 0),  
(0, INS_MOV, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_w | OP_R, ARG_NONE, cpu_80386, "movzx", 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, INS_INVALIDOP, ADDRMETH_R | OPTYPE_d | OP_W, ADDRMETH_E | OPTYPE_d | OP_R, ARG_NONE, cpu_80386, "ud1", 0, 0, 0),  #### GROUP 10?
(23, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 0, 0),  
(0, INS_BITTEST, ADDRMETH_E | OPTYPE_v | OP_R, ADDRMETH_G | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "btc", 0, 0, 0),  
(0, INS_BITTEST, ADDRMETH_G | OPTYPE_v | OP_R | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "bsf", 0, 0, 0),  
(0, INS_BITTEST, ADDRMETH_G | OPTYPE_v | OP_R | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "bsr", 0, 0, 0),  
(0, INS_MOV, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "movsx", 0, 0, 0),  
(0, INS_MOV, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_w | OP_R, ARG_NONE, cpu_80386, "movsx", 0, 0, 0),  
# 0fc0
(0, INS_ADD, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_G | OPTYPE_b | OP_W, ARG_NONE, cpu_80486, "xadd", 0, 0, 0),  
(0, INS_ADD, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_G | OPTYPE_v, ARG_NONE, cpu_80486, "xadd", 0, 0, 0),  
(0, INS_CMP, ADDRMETH_V | OPTYPE_ps| OP_W, ADDRMETH_W | OPTYPE_ps| OP_W, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTIUM2, "cmpps", 0, 0, 0),  
(0, INS_MOV, ADDRMETH_M | OPTYPE_q | OP_W, ADDRMETH_G | OPTYPE_q |OP_R, ARG_NONE, cpu_PENTIUM2, "movnti", 0, 0, 0),  
(0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_E | OPTYPE_w | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTIUM2, "pinsrw", 0, 0, 0),  
(0, INS_OTHER, ADDRMETH_G | OPTYPE_d | OP_W, ADDRMETH_N | OPTYPE_q | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTIUM2, "pextrw", 0, 0, 0),
(0, INS_OTHER, ADDRMETH_V | OPTYPE_ps | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTIUM2, "shufps", 0, 0, 0),  
(24, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_PENTMMX, 0, 0, 0, 0),  # group 9
(0, INS_XCHG, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80486, "bswap", e_i386_regs.REG_EAX, 0, 0),  
(0, INS_XCHG, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80486, "bswap", e_i386_regs.REG_ECX, 0, 0),  
(0, INS_XCHG, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80486, "bswap", e_i386_regs.REG_EDX, 0, 0),  
(0, INS_XCHG, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80486, "bswap", e_i386_regs.REG_EBX, 0, 0),  
(0, INS_XCHG, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80486, "bswap", e_i386_regs.REG_ESP, 0, 0),  
(0, INS_XCHG, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80486, "bswap", e_i386_regs.REG_EBP, 0, 0),  
(0, INS_XCHG, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80486, "bswap", e_i386_regs.REG_ESI, 0, 0),  
(0, INS_XCHG, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80486, "bswap", e_i386_regs.REG_EDI, 0, 0),  
# 0fd0
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "psrlw", 0, 0, 0),  
(0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "psrld", 0, 0, 0),  
(0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "psrlq", 0, 0, 0),  
(0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "paddq", 0, 0, 0),  
(0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "pmullw", 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, INS_OTHER, ADDRMETH_G | OPTYPE_d | OP_W, ADDRMETH_N | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "pmovmskb", 0, 0, 0),  
(0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "psubusb", 0, 0, 0),  
(0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "psubusw", 0, 0, 0),  
(0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "pminub", 0, 0, 0),  
(0, INS_AND, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "pand", 0, 0, 0),  
(0, INS_ADD, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "paddusb", 0, 0, 0),  
(0, INS_ADD, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "paddusw", 0, 0, 0),  
(0, INS_ARITH, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "pmaxub", 0, 0, 0),  
(0, INS_AND, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "pandn", 0, 0, 0),  
# 0fe0
(0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "pavgb", 0, 0, 0),  
(0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "psraw", 0, 0, 0),  
(0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "psrad", 0, 0, 0),  
(0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "pavgw", 0, 0, 0),  
(0, INS_MUL, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "pmulhuw", 0, 0, 0),  
(0, INS_MUL, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "pmulhw", 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, INS_MOV, ADDRMETH_M | OPTYPE_dq | OP_W, ADDRMETH_V | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "movntq", 0, 0, 0),  
(0, INS_SUB, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "psubsb", 0, 0, 0),  
(0, INS_SUB, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "psubsw", 0, 0, 0),  
(0, INS_ARITH, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "pminsw", 0, 0, 0),  
(0, INS_OR, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "por", 0, 0, 0),  
(0, INS_ADD, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "paddsb", 0, 0, 0),  
(0, INS_ADD, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "paddsw", 0, 0, 0),  
(0, INS_ARITH, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "pmaxsw", 0, 0, 0),  
(0, INS_XOR, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "pxor", 0, 0, 0),  
# 0ff0
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "psllw", 0, 0, 0),  
(0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "pslld", 0, 0, 0),  
(0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "psllq", 0, 0, 0),  
(0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "pmuludq", 0, 0, 0),  
(0, INS_ADD, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "pmaddwd", 0, 0, 0),  
(0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "psadbw", 0, 0, 0),  
(0, INS_MOV, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_N | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "maskmovq", 0, 0, 0),  
(0, INS_SUB, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "psubb", 0, 0, 0),  
(0, INS_SUB, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "psubw", 0, 0, 0),  
(0, INS_SUB, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "psubd", 0, 0, 0),  
(0, INS_SUB, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "psubq", 0, 0, 0),  
(0, INS_ADD, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "paddb", 0, 0, 0),  
(0, INS_ADD, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "paddw", 0, 0, 0),  
(0, INS_ADD, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "paddd", 0, 0, 0),  
(0, INS_INVALIDOP, ADDRMETH_R | OPTYPE_d | OP_W, ADDRMETH_E | OPTYPE_d | OP_R, ARG_NONE, cpu_80386, "ud0", 0, 0, 0),
]

tbl32_660F = [(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0) for x in range(256)]
tbl32_660F[0x10] = (0, INS_MOV, ADDRMETH_V | OPTYPE_pd | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ARG_NONE, cpu_PENTIUM2, "movupd", 0, 0, 0)
tbl32_660F[0x11] = (0, INS_MOV, ADDRMETH_W | OPTYPE_pd | OP_W, ADDRMETH_V | OPTYPE_pd | OP_R, ARG_NONE, cpu_PENTIUM2, "movupd", 0, 0, 0)
tbl32_660F[0x12] = (0, INS_MOV, ADDRMETH_V | OPTYPE_q | OP_W, ADDRMETH_M | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "movlpd", 0, 0, 0)
tbl32_660F[0x13] = (0, INS_MOV, ADDRMETH_M | OPTYPE_q | OP_W, ADDRMETH_V | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "movlpd", 0, 0, 0)
tbl32_660F[0x14] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_pd | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ARG_NONE, cpu_PENTIUM2,"unpcklpd", 0, 0, 0)
tbl32_660F[0x15] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_pd | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ARG_NONE, cpu_PENTIUM2,"unpckhpd", 0, 0, 0)
tbl32_660F[0x16] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_pd | OP_W, ADDRMETH_M | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "movhpd", 0, 0, 0)
tbl32_660F[0x17] = (0, INS_OTHER, ADDRMETH_M | OPTYPE_pd | OP_W, ADDRMETH_V | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "movhpd", 0, 0, 0)
tbl32_660F[0x28] = (0, INS_MOV, ADDRMETH_V | OPTYPE_pd | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ARG_NONE, cpu_PENTIUM2, "movapd", 0, 0, 0)
tbl32_660F[0x29] = (0, INS_MOV, ADDRMETH_W | OPTYPE_pd | OP_W, ADDRMETH_V | OPTYPE_pd | OP_R, ARG_NONE, cpu_PENTIUM2, "movapd", 0, 0, 0)
tbl32_660F[0x2A] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_pd | OP_W, ADDRMETH_Q | OPTYPE_pi | OP_R, ARG_NONE, cpu_PENTIUM2, "cvtpi2pd", 0, 0, 0)
tbl32_660F[0x2B] = (0, INS_MOV, ADDRMETH_M | OPTYPE_pd | OP_W, ADDRMETH_V | OPTYPE_pd | OP_R, ARG_NONE, cpu_PENTIUM2, "movntpd", 0, 0, 0)
tbl32_660F[0x2C] = (0, INS_OTHER, ADDRMETH_P | OPTYPE_pi | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ARG_NONE, cpu_PENTIUM2, "cvttpd2pi", 0, 0, 0)
tbl32_660F[0x2D] = (0, INS_OTHER, ADDRMETH_P | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ARG_NONE, cpu_PENTIUM2, "cvtpd2pi", 0, 0, 0)
tbl32_660F[0x2E] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_pd | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ARG_NONE, cpu_PENTIUM2, "ucomisd", 0, 0, 0)
tbl32_660F[0x2F] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_pd | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ARG_NONE, cpu_PENTIUM2, "comisd", 0, 0, 0)

tbl32_660F[0x38] = (56, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0)
tbl32_660F[0x3a] = (58, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0)

tbl32_660F[0x50] = (0, INS_MOV, ADDRMETH_G | OPTYPE_d | OP_W, ADDRMETH_U | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTIUM2, "movmskpd", 0, 0, 0)
tbl32_660F[0x51] = (0, INS_ARITH, ADDRMETH_V | OPTYPE_pd | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ARG_NONE, cpu_PENTIUM2, "sqrtpd", 0, 0, 0)
tbl32_660F[0x54] = (0, INS_AND, ADDRMETH_V | OPTYPE_pd | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ARG_NONE, cpu_PENTIUM2, "andpd", 0, 0, 0)
tbl32_660F[0x55] = (0, INS_AND, ADDRMETH_V | OPTYPE_pd | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ARG_NONE, cpu_PENTIUM2, "andnpd", 0, 0, 0)
tbl32_660F[0x56] = (0, INS_AND, ADDRMETH_V | OPTYPE_pd | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ARG_NONE, cpu_PENTIUM2, "orpd", 0, 0, 0)
tbl32_660F[0x57] = (0, INS_AND, ADDRMETH_V | OPTYPE_pd | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ARG_NONE, cpu_PENTIUM2, "xorpd", 0, 0, 0)
tbl32_660F[0x58] = (0, INS_AND, ADDRMETH_V | OPTYPE_pd | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ARG_NONE, cpu_PENTIUM2, "addpd", 0, 0, 0)
tbl32_660F[0x59] = (0, INS_AND, ADDRMETH_V | OPTYPE_pd | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ARG_NONE, cpu_PENTIUM2, "mulpd", 0, 0, 0)
tbl32_660F[0x5a] = (0, INS_AND, ADDRMETH_V | OPTYPE_ps | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ARG_NONE, cpu_PENTIUM2, "cvtpd2ps", 0, 0, 0)
tbl32_660F[0x5b] = (0, INS_AND, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R, ARG_NONE, cpu_PENTIUM2, "cvtps2dq", 0, 0, 0)
tbl32_660F[0x5c] = (0, INS_AND, ADDRMETH_V | OPTYPE_pd | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ARG_NONE, cpu_PENTIUM2, "subpd", 0, 0, 0)
tbl32_660F[0x5d] = (0, INS_AND, ADDRMETH_V | OPTYPE_pd | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ARG_NONE, cpu_PENTIUM2, "minpd", 0, 0, 0)
tbl32_660F[0x5e] = (0, INS_AND, ADDRMETH_V | OPTYPE_pd | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ARG_NONE, cpu_PENTIUM2, "divpd", 0, 0, 0)
tbl32_660F[0x5f] = (0, INS_AND, ADDRMETH_V | OPTYPE_pd | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ARG_NONE, cpu_PENTIUM2, "maxpd", 0, 0, 0)
tbl32_660F[0x60] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "punpcklbw", 0, 0, 0)
tbl32_660F[0x61] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "punpcklwd", 0, 0, 0)
tbl32_660F[0x62] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "punpckldq", 0, 0, 0)
tbl32_660F[0x63] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "packsswb", 0, 0, 0)
tbl32_660F[0x64] = (0, INS_CMP, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "pcmpgtb", 0, 0, 0)
tbl32_660F[0x65] = (0, INS_CMP, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "pcmpgtw", 0, 0, 0)
tbl32_660F[0x66] = (0, INS_CMP, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "pcmpgtd", 0, 0, 0)
tbl32_660F[0x67] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "packuswb", 0, 0, 0)
tbl32_660F[0x68] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "punpckhbw", 0, 0, 0)
tbl32_660F[0x69] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "punpckhwd", 0, 0, 0)
tbl32_660F[0x6a] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "punpckhdq", 0, 0, 0)
tbl32_660F[0x6b] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "packssdw", 0, 0, 0)
tbl32_660F[0x6c] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "punpcklqdq", 0, 0, 0)
tbl32_660F[0x6d] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "punpckhqdq", 0, 0, 0)
tbl32_660F[0x6e] = (0, INS_MOV, ADDRMETH_V | OPTYPE_d | OP_W, ADDRMETH_W | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTIUM2, "movd", 0, 0, 0)
tbl32_660F[0x6f] = (0, INS_MOV, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "movdqa", 0, 0, 0)
tbl32_660F[0x70] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_d | OP_W, ADDRMETH_W | OPTYPE_d | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTIUM2, "pshufd", 0, 0, 0)
tbl32_660F[0x71] = (59, 0, 0, 0, 0, 0, 0, 0, 0, 0)
tbl32_660F[0x72] = (60, 0, 0, 0, 0, 0, 0, 0, 0, 0)
tbl32_660F[0x73] = (54, 0, 0, 0, 0, 0, 0, 0, 0, 0)
tbl32_660F[0x74] = (0, INS_CMP, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "pcmpeqb", 0, 0, 0)
tbl32_660F[0x75] = (0, INS_CMP, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "pcmpeqw", 0, 0, 0)
tbl32_660F[0x76] = (0, INS_CMP, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "pcmpeqd", 0, 0, 0)
tbl32_660F[0x7c] = (0, INS_ADD, ADDRMETH_V | OPTYPE_pd | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ARG_NONE, cpu_PENTIUM2, "haddpd", 0, 0, 0)
tbl32_660F[0x7d] = (0, INS_SUB, ADDRMETH_V | OPTYPE_pd | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ARG_NONE, cpu_PENTIUM2, "hsubpd", 0, 0, 0)
tbl32_660F[0x7e] = (0, INS_MOV, ADDRMETH_E | OPTYPE_d | OP_W, ADDRMETH_V | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTIUM2, "movd", 0, 0, 0)
tbl32_660F[0x7f] = (0, INS_MOV, ADDRMETH_W | OPTYPE_x | OP_W, ADDRMETH_V | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "movdqa", 0, 0, 0)
tbl32_660F[0xc2] = (0, INS_CMP, ADDRMETH_V | OPTYPE_pd | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTIUM2, "cmppd", 0, 0, 0)
tbl32_660F[0xc4] = (0, INS_MOV, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_E | OPTYPE_w | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTIUM2, "pinsrw", 0, 0, 0)
tbl32_660F[0xc5] = (0, INS_MOV, ADDRMETH_G | OPTYPE_d | OP_W, ADDRMETH_U | OPTYPE_w | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTIUM2, "pextrw", 0, 0, 0)
tbl32_660F[0xc6] = (0, INS_MOV, ADDRMETH_V | OPTYPE_pd | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTIUM2, "shufpd", 0, 0, 0)
tbl32_660F[0xc7] = (47, 0, 0, 0, 0, 0, 0, 0, 0, 0)

tbl32_660F[0xd0] = (0, INS_ARITH, ADDRMETH_V | OPTYPE_pd | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ARG_NONE, cpu_PENTMMX, "addsubpd", 0, 0, 0)
tbl32_660F[0xd1] = (0, INS_SHR, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTMMX, "psrlw", 0, 0, 0)
tbl32_660F[0xd2] = (0, INS_SHR, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTMMX, "psrld", 0, 0, 0)
tbl32_660F[0xd3] = (0, INS_SHR, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTMMX, "psrlq", 0, 0, 0)
tbl32_660F[0xd4] = (0, INS_ADD, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTMMX, "paddq", 0, 0, 0)
tbl32_660F[0xd5] = (0, INS_MUL, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTMMX, "pmullw", 0, 0, 0)
tbl32_660F[0xd6] = (0, INS_MOV, ADDRMETH_W | OPTYPE_q | OP_W, ADDRMETH_V | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "movq", 0, 0, 0)
tbl32_660F[0xd7] = (0, INS_OTHER, ADDRMETH_G | OPTYPE_d | OP_W, ADDRMETH_U | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTMMX, "pmovmskb", 0, 0, 0)
tbl32_660F[0xd8] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTMMX, "psubusb", 0, 0, 0)
tbl32_660F[0xd9] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTMMX, "psubusw", 0, 0, 0)
tbl32_660F[0xda] = (0, INS_ARITH, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTMMX, "pminub", 0, 0, 0)
tbl32_660F[0xdb] = (0, INS_AND, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTMMX, "pand", 0, 0, 0)
tbl32_660F[0xdc] = (0, INS_ADD, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTMMX, "paddusb", 0, 0, 0)
tbl32_660F[0xdd] = (0, INS_ADD, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTMMX, "paddusw", 0, 0, 0)
tbl32_660F[0xde] = (0, INS_ARITH, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTMMX, "pmaxub", 0, 0, 0)
tbl32_660F[0xdf] = (0, INS_AND, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTMMX, "pandn", 0, 0, 0)

tbl32_660F[0xe0] = (0, INS_ARITH, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "pavgb", 0, 0, 0)
tbl32_660F[0xe1] = (0, INS_SHR, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "psraw", 0, 0, 0)
tbl32_660F[0xe2] = (0, INS_SHR, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "psrad", 0, 0, 0)
tbl32_660F[0xe3] = (0, INS_ARITH, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "pavgb", 0, 0, 0)
tbl32_660F[0xe4] = (0, INS_MUL, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "pmulhuw", 0, 0, 0)
tbl32_660F[0xe5] = (0, INS_MUL, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "pmulhw", 0, 0, 0)

# tbl32_660F[0xe6] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_ | OP_W, ADDRMETH_W | OPTYPE_ | OP_R, ARG_NONE, cpu_PENTIUM2, "cvttpd2dq", 0, 0, 0)
tbl32_660F[0xe7] = (0, INS_MOV, ADDRMETH_M | OPTYPE_dq | OP_W, ADDRMETH_V | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "movntdq", 0, 0, 0)
tbl32_660F[0xe8] = (0, INS_SUB, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "psubsb", 0, 0, 0)
tbl32_660F[0xe9] = (0, INS_SUB, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "psubsw", 0, 0, 0)
tbl32_660F[0xea] = (0, INS_ARITH, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "pminsw", 0, 0, 0)
tbl32_660F[0xeb] = (0, INS_OR, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "por", 0, 0, 0)
tbl32_660F[0xec] = (0, INS_ADD, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "paddsb", 0, 0, 0)
tbl32_660F[0xed] = (0, INS_ADD, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "paddsw", 0, 0, 0)
tbl32_660F[0xee] = (0, INS_ARITH, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "pmaxsw", 0, 0, 0)
tbl32_660F[0xef] = (0, INS_XOR, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "pxor", 0, 0, 0)

tbl32_660F[0xf1] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "psllw", 0, 0, 0)
tbl32_660F[0xf2] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "pslld", 0, 0, 0)
tbl32_660F[0xf3] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "psllq", 0, 0, 0)
tbl32_660F[0xf4] = (0, INS_MUL, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "pmuludq", 0, 0, 0)
tbl32_660F[0xf5] = (0, INS_ARITH, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "pmaddwd", 0, 0, 0)
tbl32_660F[0xf6] = (0, INS_ARITH, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "psadbw", 0, 0, 0)

tbl32_660F[0xf8] = (0, INS_SUB, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "psubb", 0, 0, 0)
tbl32_660F[0xf9] = (0, INS_SUB, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "psubw", 0, 0, 0)
tbl32_660F[0xfa] = (0, INS_SUB, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "psubd", 0, 0, 0)
tbl32_660F[0xfb] = (0, INS_SUB, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "psubq", 0, 0, 0)
tbl32_660F[0xfc] = (0, INS_ADD, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "paddb", 0, 0, 0)
tbl32_660F[0xfd] = (0, INS_ADD, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "paddw", 0, 0, 0)
tbl32_660F[0xfe] = (0, INS_ADD, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "paddd", 0, 0, 0)

"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_F20F = [(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0) for x in range(256)]
tbl32_F20F[0x10] = (0, INS_MOV, ADDRMETH_V | OPTYPE_sd | OP_W, ADDRMETH_W | OPTYPE_sd | OP_MEM_Q | OP_R, ARG_NONE, cpu_PENTIUM2, "movsd", 0, 0, 0)
tbl32_F20F[0x11] = (0, INS_MOV, ADDRMETH_W | OPTYPE_sd | OP_MEM_Q | OP_W, ADDRMETH_V | OPTYPE_sd | OP_R, ARG_NONE, cpu_PENTIUM2, "movsd", 0, 0, 0)
tbl32_F20F[0x12] = (0, INS_MOV, ADDRMETH_V | OPTYPE_sd | OP_W, ADDRMETH_W | OPTYPE_sd | OP_R, ARG_NONE, cpu_PENTIUM2, "movddup", 0, 0, 0)

tbl32_F20F[0x2a] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_sd | OP_W, ADDRMETH_E | OPTYPE_ds | OP_R, ARG_NONE, cpu_PENTIUM2, "cvtsi2sd", 0, 0, 0)
tbl32_F20F[0x2c] = (0, INS_OTHER, ADDRMETH_G | OPTYPE_q | OP_W, ADDRMETH_W | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "cvttsd2si", 0, 0, 0)
tbl32_F20F[0x2d] = (0, INS_OTHER, ADDRMETH_G | OPTYPE_d | OP_W, ADDRMETH_W | OPTYPE_sd | OP_R, ARG_NONE, cpu_PENTIUM2, "cvtsd2si", 0, 0, 0)
tbl32_F20F[0x38] = (61, 0, 0, 0, 0, 0, 0, 0, 0, 0)
tbl32_F20F[0x51] = (0, INS_ARITH, ADDRMETH_V | OPTYPE_sd | OP_W, ADDRMETH_W | OPTYPE_sd | OP_R, ARG_NONE, cpu_PENTIUM2, "sqrtsd", 0, 0, 0)
tbl32_F20F[0x58] = (0, INS_ADD, ADDRMETH_V | OPTYPE_sd | OP_W, ADDRMETH_W | OPTYPE_sd | OP_R, ARG_NONE, cpu_PENTIUM2, "addsd", 0, 0, 0)
tbl32_F20F[0x59] = (0, INS_MUL, ADDRMETH_V | OPTYPE_sd | OP_R, ADDRMETH_W | OPTYPE_sd | OP_R, ARG_NONE, cpu_PENTIUM2, "mulsd", 0, 0, 0)
tbl32_F20F[0x5a] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_sd | OP_R,ADDRMETH_W | OPTYPE_sd | OP_R, ARG_NONE, cpu_AMD64, "cvtsd2ss", 0, 0, 0)
tbl32_F20F[0x5c] = (0, INS_SUB, ADDRMETH_V | OPTYPE_sd | OP_W,ADDRMETH_W | OPTYPE_sd | OP_R, ARG_NONE, cpu_PENTIUM2, "subsd", 0, 0, 0)
tbl32_F20F[0x5d] = (0, INS_ARITH, ADDRMETH_V | OPTYPE_sd | OP_W,ADDRMETH_W | OPTYPE_sd | OP_R, ARG_NONE, cpu_PENTIUM2, "minsd", 0, 0, 0)
tbl32_F20F[0x5e] = (0, INS_DIV, ADDRMETH_V | OPTYPE_sd | OP_W,ADDRMETH_W | OPTYPE_sd | OP_R, ARG_NONE, cpu_PENTIUM2, "divsd", 0, 0, 0)
tbl32_F20F[0x5f] = (0, INS_ARITH, ADDRMETH_V | OPTYPE_sd | OP_W,ADDRMETH_W | OPTYPE_sd | OP_R, ARG_NONE, cpu_PENTIUM2, "maxsd", 0, 0, 0)

tbl32_F20F[0x70] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTIUM2, "pshuflw", 0, 0, 0)
tbl32_F20F[0x7c] = (0, INS_MOV, ADDRMETH_V | OPTYPE_ps | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R, ARG_NONE, cpu_PENTMMX, "haddps", 0, 0, 0)
tbl32_F20F[0x7d] = (0, INS_MOV, ADDRMETH_V | OPTYPE_ps | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R, ARG_NONE, cpu_PENTMMX, "hsubps", 0, 0, 0)
tbl32_F20F[0xc2] = (0, INS_CMP, ADDRMETH_V | OPTYPE_sd | OP_W, ADDRMETH_W | OPTYPE_sd | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTIUM2, "cmpsd", 0, 0, 0)
tbl32_F20F[0xd0] = (0, INS_ADD, ADDRMETH_V | OPTYPE_ps | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R, ARG_NONE, cpu_PENTMMX, "addsubps", 0, 0, 0)
tbl32_F20F[0xd6] = (0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_V | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "movdq2q", 0, 0, 0)
tbl32_F20F[0xe6] = (0, INS_MUL, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ARG_NONE, cpu_PENTMMX, "cvtpd2dq", 0, 0, 0)
tbl32_F20F[0xf0] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_M | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTMMX, "lddqu", 0, 0, 0)


tbl32_F20F38 = [(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0) for x in range(8)]
tbl32_F20F38[0] = (0, INS_OTHER, ADDRMETH_G | OPTYPE_d | OP_W, ADDRMETH_E | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTIUM, "crc32", 0, 0, 0)
tbl32_F20F38[1] = (0, INS_OTHER, ADDRMETH_G | OPTYPE_d | OP_W, ADDRMETH_E | OPTYPE_z | OP_R, ARG_NONE, cpu_PENTIUM, "crc32", 0, 0, 0)

tbl32_F30F38 = [(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0) for x in range(8)]
tbl32_F30F38[6] = (0, INS_ADD, ADDRMETH_G | OPTYPE_y | OP_W, ADDRMETH_E | OPTYPE_y | OP_R, ARG_NONE, cpu_AMD64, "adox", 0, 0, 0)
"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_F30F = [(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0) for x in range(256)]
tbl32_F30F[0x10] = (0, INS_MOV, ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_W | OPTYPE_ds | OP_R, ARG_NONE, cpu_PENTIUM2, "movss", 0, 0, 0)
tbl32_F30F[0x11] = (0, INS_MOV, ADDRMETH_W | OPTYPE_ds | OP_W, ADDRMETH_V | OPTYPE_ss | OP_R, ARG_NONE, cpu_PENTIUM2, "movss", 0, 0, 0)
tbl32_F30F[0x12] = (0, INS_MOV, ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_W | OPTYPE_ss | OP_R, ARG_NONE, cpu_PENTMMX, "movsldup", 0, 0, 0)

tbl32_F30F[0x16] = (0, INS_MOV,   ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_W | OPTYPE_ss | OP_R, ARG_NONE, cpu_PENTIUM2, "movshdup", 0, 0, 0)
tbl32_F30F[0x2a] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_E | OPTYPE_si | OP_R, ARG_NONE, cpu_PENTIUM2, "cvtsi2ss", 0, 0, 0)
tbl32_F30F[0x2c] = (0, INS_OTHER, ADDRMETH_G | OPTYPE_ds | OP_W, ADDRMETH_W | OPTYPE_ds | OP_R, ARG_NONE, cpu_PENTIUM2, "cvttss2si", 0, 0, 0)
tbl32_F30F[0x2d] = (0, INS_OTHER, ADDRMETH_G | OPTYPE_ds | OP_W, ADDRMETH_W | OPTYPE_ss | OP_R, ARG_NONE, cpu_PENTIUM2, "cvtss2si", 0, 0, 0)
tbl32_F30F[0x38] = (62, 0, 0, 0, 0, 0, 0, 0, 0, 0)
tbl32_F30F[0x51] = (0, INS_ARITH, ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_W | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTIUM2, "sqrtss", 0, 0, 0)
tbl32_F30F[0x52] = (0, INS_ARITH, ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_W | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTIUM2, "rsqrtss", 0, 0, 0)

tbl32_F30F[0x53] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_W | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTIUM2, "rcpss", 0, 0, 0)
tbl32_F30F[0x58] = (0, INS_ADD,   ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_W | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTIUM2, "addss", 0, 0, 0)
tbl32_F30F[0x59] = (0, INS_MUL,   ADDRMETH_V | OPTYPE_ss | OP_R, ADDRMETH_W | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTIUM2, "mulss", 0, 0, 0)
tbl32_F30F[0x5a] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_sd | OP_W, ADDRMETH_W | OPTYPE_ss | OP_R, ARG_NONE, cpu_PENTMMX, "cvtss2sd", 0, 0, 0)
tbl32_F30F[0x5b] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_ps | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R, ARG_NONE, cpu_PENTMMX, "cvttps2dq", 0, 0, 0)
tbl32_F30F[0x5c] = (0, INS_SUB,   ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_W | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTIUM2, "subss", 0, 0, 0)
tbl32_F30F[0x5d] = (0, INS_ARITH, ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_W | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTIUM2, "minss", 0, 0, 0)
tbl32_F30F[0x5e] = (0, INS_DIV,   ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_W | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTIUM2, "divss", 0, 0, 0)
tbl32_F30F[0x5f] = (0, INS_ARITH, ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_W | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTIUM2, "maxss", 0, 0, 0)
tbl32_F30F[0x6f] = (0, INS_MOV,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "movdqu", 0, 0, 0)
tbl32_F30F[0x70] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTIUM2, "pshufhw", 0, 0, 0)
tbl32_F30F[0x7e] = (0, INS_MOV,   ADDRMETH_V | OPTYPE_q | OP_W, ADDRMETH_W | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "movq", 0, 0, 0)
tbl32_F30F[0x7f] = (0, INS_MOV,   ADDRMETH_W | OPTYPE_x | OP_W, ADDRMETH_V | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "movdqu", 0, 0, 0)
tbl32_F30F[0xb8] = (0, INS_BITTEST, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "popcnt", 0, 0, 0)
tbl32_F30F[0xbd] = (0, INS_BITTEST, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "lzcnt", 0, 0, 0)
tbl32_F30F[0xc2] = (0, INS_CMP,   ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_W | OPTYPE_ss | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTIUM2, "cmpss", 0, 0, 0)
tbl32_F30F[0xc7] = (51, 0, 0, 0, 0, 0, 0, 0, 0, 0)
tbl32_F30F[0xd6] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_N | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTMMX, "movq2dq", 0, 0, 0)
tbl32_F30F[0xe6] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x  | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ARG_NONE, cpu_PENTMMX, "cvtdq2pd", 0, 0, 0)


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""

tbl32_0F00 = [
    (0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "sldt", 0, 0, 0),
    (0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "str", 0, 0, 0),
    (0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "lldt", 0, 0, 0),
    (0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "ltr", 0, 0, 0),
    (0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "verr", 0, 0, 0),
    (0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "verw", 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0)
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""

tbl32_0F01_00BF = [
    (0, INS_SYSTEM, ADDRMETH_M | OPTYPE_s | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "sgdt", 0, 0, 0),
    (0, INS_SYSTEM, ADDRMETH_M | OPTYPE_s | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "sidt", 0, 0, 0),
    (0, INS_SYSTEM, ADDRMETH_M | OPTYPE_s | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "lgdt", 0, 0, 0),
    (0, INS_SYSTEM, ADDRMETH_M | OPTYPE_s | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "lidt", 0, 0, 0),
    (0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "smsw", 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "lmsw", 0, 0, 0),
    (0, INS_SYSTEM, ADDRMETH_M | OPTYPE_b | OP_R, ARG_NONE, ARG_NONE, cpu_80486, "invlpg", 0, 0, 0)
]

tbl32_0F01_rest = [
# 0f01c0
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, INS_SYSTEM, ARG_NONE, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "vmcall", 0, 0, 0),  
(0, INS_SYSTEM, ARG_NONE, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "vmlaunch", 0, 0, 0),  
(0, INS_SYSTEM, ARG_NONE, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "vmresume", 0, 0, 0),  
(0, INS_SYSTEM, ARG_NONE, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "vmxoff", 0, 0, 0),  
(0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "smsw", 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "lmsw", 0, 0, 0),  
(0, INS_SYSTEM, ARG_NONE, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "monitor", 0, 0, 0),  
(0, INS_SYSTEM, ARG_NONE, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "mwait", 0, 0, 0),
(0, INS_CLEARAF, ARG_NONE, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "clac", 0, 0, 0),
(0, INS_SETAF, ARG_NONE, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "stac", 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
# 0f01d0
(0, INS_SYSTEM, OP_R | OP_REG, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "xgetbv", e_i386_regs.REG_ECX, 0, 0),
(0, INS_SYSTEM, OP_R | OP_REG, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "xsetbv", e_i386_regs.REG_ECX, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, INS_SYSTEM, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "vmfunc", 0, 0, 0),
(0, INS_SYSTEM, ARG_NONE, ARG_NONE, ARG_NONE, cpu_PENTIUM, "xend", 0, 0, 0),
(0, INS_SYSTEM, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "xtest", 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
# 0f01e0
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "smsw", 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "lmsw", 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, INS_SYSTEM, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "rdpkru", e_i386_regs.REG_EAX, 0, 0),
(0, INS_SYSTEM, ARG_NONE, ARG_NONE, ARG_NONE, cpu_OSPKE, "wrpkru", 0, 0, 0),
(0, INS_OTHER, ARG_NONE, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "swapgs", 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
( 0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "smsw", 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
( 0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "lmsw", 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, INS_SYSTEM, ARG_NONE, ARG_NONE, ARG_NONE, cpu_PENTIUM, "rdtscp", 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0)
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_0F18 = [
( 0, INS_SYSTEM,  OP_W | ADDRMETH_M, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "prefetch", 0, 0, 0),  
( 0, INS_SYSTEM, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "prefetch", e_i386_regs.REG_TEST0, 0, 0),
( 0, INS_SYSTEM, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "prefetch", e_i386_regs.REG_TEST1, 0, 0),
( 0, INS_SYSTEM, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "prefetch", e_i386_regs.REG_TEST2, 0, 0),
#( 0, INS_SYSTEM, OP_REG | OP_W | ADDRMETH_M, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "prefetch", 0 + REG_TEST_OFFSET, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0)
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_0F38 = [(0, 0, 0, 0, 0, 0, 0, 0, 0, 0) for x in range(256)]
tbl32_0F38[0x0] = (0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "pshufb", 0, 0, 0)
tbl32_0F38[0x1] = (0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "phaddw", 0, 0, 0)
tbl32_0F38[0x2] = (0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "phaddd", 0, 0, 0)
tbl32_0F38[0x3] = (0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "phaddsw", 0, 0, 0)
tbl32_0F38[0x4] = (0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "pmaddubsw", 0, 0, 0)
tbl32_0F38[0x5] = (0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "phsubw", 0, 0, 0)
tbl32_0F38[0x6] = (0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "phsubd", 0, 0, 0)
tbl32_0F38[0x7] = (0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "phsubsw", 0, 0, 0)
tbl32_0F38[0x8] = (0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "psignb", 0, 0, 0)
tbl32_0F38[0x9] = (0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "psignw", 0, 0, 0)
tbl32_0F38[0xa] = (0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "psignd", 0, 0, 0)
tbl32_0F38[0xb] = (0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "pmulhrsw", 0, 0, 0)
tbl32_0F38[0x1c] = (0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "pabsb", 0, 0, 0)
tbl32_0F38[0x1d] = (0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "pabsw", 0, 0, 0)
tbl32_0F38[0x1e] = (0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "pabsd", 0, 0, 0)

tbl32_0F38[0xf0] = (0, INS_MOV, ADDRMETH_G | OPTYPE_z | OP_W, ADDRMETH_M | OPTYPE_z | OP_R, ARG_NONE, cpu_PENTIUM, "movbe", 0, 0, 0)
tbl32_0F38[0xf1] = (0, INS_MOV, ADDRMETH_M | OPTYPE_z | OP_W, ADDRMETH_G | OPTYPE_z | OP_R, ARG_NONE, cpu_PENTIUM, "movbe", 0, 0, 0)
# tbl32_0F38[0xf2] = (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0) requires vex parsing in i386
# tbl32_0F38[0xf3] = (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0) requires vex parsing in i386
# tbl32_0F38[0xf7] = (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0) requires vex parsing in i386

"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_660F38 = [(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0) for x in range(256)]
tbl32_660F38[0x0] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "pshufb", 0, 0, 0)
tbl32_660F38[0x1] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "phaddw", 0, 0, 0)
tbl32_660F38[0x2] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "phaddd", 0, 0, 0)
tbl32_660F38[0x3] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "phaddsw", 0, 0, 0)
tbl32_660F38[0x4] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "pmaddubsw", 0, 0, 0)
tbl32_660F38[0x5] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "phsubw", 0, 0, 0)
tbl32_660F38[0x6] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "phsubd", 0, 0, 0)
tbl32_660F38[0x7] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "phsubsw", 0, 0, 0)
tbl32_660F38[0x8] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "psignb", 0, 0, 0)
tbl32_660F38[0x9] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "psignw", 0, 0, 0)
tbl32_660F38[0xa] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "psignd", 0, 0, 0)
tbl32_660F38[0xb] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "pmulhrsw", 0, 0, 0)
tbl32_660F38[0xc] = (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0)
tbl32_660F38[0xd] = (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0)
tbl32_660F38[0xe] = (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0)
tbl32_660F38[0xf] = (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0)
tbl32_660F38[0x10] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_W, ARG_NONE, cpu_PENTMMX, "pblendvb", 0, 0, 0)
tbl32_660F38[0x11] = (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0)
tbl32_660F38[0x12] = (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0)
tbl32_660F38[0x13] = (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0)
tbl32_660F38[0x14] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "blendvps", 0, 0, 0)
tbl32_660F38[0x15] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "blendvpd", 0, 0, 0)
tbl32_660F38[0x16] = (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0)
tbl32_660F38[0x17] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "ptest", 0, 0, 0)
tbl32_660F38[0x18] = (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0)
tbl32_660F38[0x19] = (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0)
tbl32_660F38[0x1a] = (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0)
tbl32_660F38[0x1b] = (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0)

tbl32_660F38[0x1c] = (0, INS_ABS, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "pabsb", 0, 0, 0)
tbl32_660F38[0x1d] = (0, INS_ABS, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "pabsw", 0, 0, 0)
tbl32_660F38[0x1e] = (0, INS_ABS, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "pabsd", 0, 0, 0)

tbl32_660F38[0x20] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "pmovsxbw", 0, 0, 0)
tbl32_660F38[0x21] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTIUM2, "pmovsxbd", 0, 0, 0)
tbl32_660F38[0x22] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_w | OP_R, ARG_NONE, cpu_PENTIUM2, "pmovsxbq", 0, 0, 0)
tbl32_660F38[0x23] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "pmovsxwd", 0, 0, 0)
tbl32_660F38[0x24] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTIUM2, "pmovsxwq", 0, 0, 0)
tbl32_660F38[0x25] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "pmovsxdq", 0, 0, 0)

tbl32_660F38[0x28] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "pmuldq", 0, 0, 0)
tbl32_660F38[0x29] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "pcmpeqq", 0, 0, 0)
tbl32_660F38[0x2A] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_M | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "movntdqa", 0, 0, 0)
tbl32_660F38[0x2B] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "packusdw", 0, 0, 0)

tbl32_660F38[0x30] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "pmovzxbw", 0, 0, 0)
tbl32_660F38[0x31] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTIUM2, "pmovzxbd", 0, 0, 0)
tbl32_660F38[0x32] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_w | OP_R, ARG_NONE, cpu_PENTIUM2, "pmovzxbq", 0, 0, 0)
tbl32_660F38[0x33] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "pmovzxwd", 0, 0, 0)
tbl32_660F38[0x34] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTIUM2, "pmovzxwq", 0, 0, 0)
tbl32_660F38[0x35] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "pmovzxdq", 0, 0, 0)

tbl32_660F38[0x37] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "pcmpgtq", 0, 0, 0)
tbl32_660F38[0x38] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "pminsb", 0, 0, 0)
tbl32_660F38[0x39] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "pminsd", 0, 0, 0)
tbl32_660F38[0x3A] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "pminuw", 0, 0, 0)
tbl32_660F38[0x3B] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "pminud", 0, 0, 0)
tbl32_660F38[0x3C] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "pmaxsb", 0, 0, 0)
tbl32_660F38[0x3D] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "pmaxsd", 0, 0, 0)
tbl32_660F38[0x3E] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "pmaxuw", 0, 0, 0)
tbl32_660F38[0x3F] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "pmaxud", 0, 0, 0)

tbl32_660F38[0x1c] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "pabsb", 0, 0, 0)
tbl32_660F38[0x1d] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "pabsw", 0, 0, 0)
tbl32_660F38[0x1e] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_PENTIUM2, "pabsd", 0, 0, 0)

tbl32_660F38[0xdb] = (0, INS_CRYPT, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_AESNI, "aesimc", 0, 0, 0)
tbl32_660F38[0xdc] = (0, INS_CRYPT, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_AESNI, "aesenc", 0, 0, 0)
tbl32_660F38[0xdd] = (0, INS_CRYPT, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_AESNI, "aesenclast", 0, 0, 0)
tbl32_660F38[0xde] = (0, INS_CRYPT, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_AESNI, "aesdec", 0, 0, 0)
tbl32_660F38[0xdf] = (0, INS_CRYPT, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_AESNI, "aesdeclast", 0, 0, 0)

tbl32_660F38[0xf6] = (0, INS_ADD, ADDRMETH_G | OPTYPE_y | OP_W, ADDRMETH_E | OPTYPE_y | OP_R, ARG_NONE, cpu_BMI, "adcx", 0, 0, 0)
"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_0F3A = [
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    ( 0, INS_OTHER, ADDRMETH_V | OPTYPE_q | OP_W, ADDRMETH_W | OPTYPE_q | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTIUM2, "palignr", 0, 0, 0),  
]   # more available upon request!



"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_660F3A = [(0, 0, 0, 0, 0, 0, 0, 0, 0, 0) for x in range(256)]
tbl32_660F3A[0x0f] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTIUM2, "palignr", 0, 0, 0)
tbl32_660F3A[0x14] = (0, INS_OTHER, ADDRMETH_E | OPTYPE_d | OP_W | OP_MEM_B, ADDRMETH_V | OPTYPE_dq | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTMMX, "pextrb", 0, 0, 0)
tbl32_660F3A[0x16] = (0, INS_OTHER, ADDRMETH_E | OPTYPE_d | OP_W, ADDRMETH_V | OPTYPE_dq | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTMMX, "pextrd", 0, 0, 0)
tbl32_660F3A[0x20] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_y | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTMMX, "pinsrb", 0, 0, 0)
tbl32_660F3A[0x44] = (0, INS_CRYPT, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_AESNI, "pclmulqdq", 0, 0, 0)
tbl32_660F3A[0x63] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_R, ADDRMETH_W | OPTYPE_dq | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTMMX, "pcmpistri", 0, 0, 0)
tbl32_660F3A[0xdf] = (0, INS_CRYPT, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_AESNI, "aeskeygenassist", 0, 0, 0)

"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_0F71 = [
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, INS_OTHER, ADDRMETH_N | OPTYPE_q | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTMMX, "psrlw", 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, INS_OTHER, ADDRMETH_N | OPTYPE_q | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTMMX, "psraw", 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, INS_OTHER, ADDRMETH_N | OPTYPE_q | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTMMX, "psllw", 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0)
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_0F72 = [
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, INS_OTHER, ADDRMETH_N | OPTYPE_q | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTMMX, "psrld", 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, INS_OTHER, ADDRMETH_N | OPTYPE_q | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTMMX, "psrad", 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, INS_OTHER, ADDRMETH_N | OPTYPE_q | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTMMX, "pslld", 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0)
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_0F73 = [
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, INS_OTHER, ADDRMETH_N | OPTYPE_q | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTMMX, "psrlq", 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, INS_OTHER, ADDRMETH_N | OPTYPE_q | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTMMX, "psllq", 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0)
]

"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_660F71 = [
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, INS_OTHER, ADDRMETH_U | OPTYPE_q | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTMMX, "psrlw", 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, INS_OTHER, ADDRMETH_U | OPTYPE_q | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTMMX, "psraw", 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, INS_OTHER, ADDRMETH_U | OPTYPE_q | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTMMX, "psllw", 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0)
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_660F72 = [
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, INS_OTHER, ADDRMETH_U | OPTYPE_q | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTMMX, "psrld", 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, INS_OTHER, ADDRMETH_U | OPTYPE_q | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTMMX, "psrad", 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, INS_OTHER, ADDRMETH_U | OPTYPE_q | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTMMX, "pslld", 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0)
]

"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
#FIXME there are more...  like 660F72 and all the VM ones...
tbl32_660F73 = [
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, INS_OTHER, ADDRMETH_U | OPTYPE_dq | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTMMX, "psrlq", 0, 0, 0),
    (0, INS_OTHER, ADDRMETH_U | OPTYPE_dq | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTMMX, "psrldq", 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, INS_OTHER, ADDRMETH_U | OPTYPE_dq | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTMMX, "psllq", 0, 0, 0),
    (0, INS_OTHER, ADDRMETH_U | OPTYPE_dq | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTMMX, "pslldq", 0, 0, 0),
]

"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_0FAE_00BF = [	# IA32 manuals don't list an actual address method... guessing by trial/error
( 0, INS_FPU, ADDRMETH_E | OPTYPE_v | OP_W, ARG_NONE, ARG_NONE, cpu_PENTMMX, "fxsave", 0, 0, 0),
( 0, INS_FPU, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "fxrstor", 0, 0, 0),
( 0, INS_FPU, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "ldmxcsr", 0, 0, 0),
( 0, INS_FPU, ADDRMETH_E | OPTYPE_v | OP_W, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "stmxcsr", 0, 0, 0),
( 0, INS_FPU, ADDRMETH_E | OPTYPE_v | OP_W, ARG_NONE, ARG_NONE, cpu_PENTIUM2, 'xsave', 0, 0, 0  ),
( 0, INS_FPU, ADDRMETH_E | OPTYPE_v | OP_W, ARG_NONE, ARG_NONE, cpu_PENTIUM2, 'xrstor', 0, 0, 0  ),
#( 0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0  ),
#( 0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0  ),
( 0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0  ),
( 0, INS_FPU, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "clflush", 0, 0, 0  )
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_0FAE_rest = [
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
( 0, INS_FPU, ARG_NONE, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "lfence", 0, 0, 0),
( 0, INS_FPU, ARG_NONE, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "mfence", 0, 0, 0),
( 0, INS_FPU, ARG_NONE, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "sfence", 0, 0, 0)
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_0FBA = [
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0  ), 
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0  ), 
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0  ), 
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0  ), 
( 0, INS_BITTEST, ADDRMETH_E | OPTYPE_v | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "bt", 0, 0, 0),  
( 0, INS_BITTEST, ADDRMETH_E | OPTYPE_v | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "bts", 0, 0, 0),  
( 0, INS_BITTEST, ADDRMETH_E | OPTYPE_v | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "btr", 0, 0, 0),  
( 0, INS_BITTEST, ADDRMETH_E | OPTYPE_v | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "btc", 0, 0, 0   ) 
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_0FC2 = [
( 0, INS_XCHGCC, ADDRMETH_M | OPTYPE_q | OP_W, ARG_NONE, ARG_NONE, cpu_PENTIUM, "cmpxch8b", 0, 0, 0   ),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, INS_SYSTEM, ADDRMETH_M | OPTYPE_q | OP_W, ARG_NONE, ARG_NONE, 0, "vmptrld", 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0)
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_0FC7_00BF = [
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
( 0, INS_XCHGCC, ADDRMETH_M | OPTYPE_q | OP_W, ARG_NONE, ARG_NONE, cpu_PENTIUM, "cmpxch8b", 0, 0, 0   ),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, INS_SYSTEM, ADDRMETH_M | OPTYPE_q | OP_W, ARG_NONE, ARG_NONE, 0, "vmptrld", 0, 0, 0),  
(0, INS_SYSTEM, ADDRMETH_M | OPTYPE_q | OP_W, ARG_NONE, ARG_NONE, 0, "vmptrst", 0, 0, 0)  
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_0FC7_rest = [
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, INS_SYSTEM, ADDRMETH_R | OPTYPE_d | OP_W, ARG_NONE, ARG_NONE, 0, 'rdrand', 0, 0, 0),
(0, INS_SYSTEM, ADDRMETH_R | OPTYPE_d | OP_W, ARG_NONE, ARG_NONE, 0, 'rdseed', 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0)
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_660FC7_00BF = [
( 0, INS_XCHGCC, ADDRMETH_M | OPTYPE_q | OP_W, ARG_NONE, ARG_NONE, cpu_PENTIUM, "cmpxch8b", 0, 0, 0   ),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, INS_SYSTEM, ADDRMETH_M | OPTYPE_q | OP_W, ARG_NONE, ARG_NONE, 0, "vmclear", 0, 0, 0),  
(0, INS_SYSTEM, ADDRMETH_M | OPTYPE_q | OP_W, ARG_NONE, ARG_NONE, 0, "vmptrst", 0, 0, 0)  
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_660FC7_rest = [
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0)
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_F20FC7_00BF = [
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0)
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_F20FC7_rest = [
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0)
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_F30FC7_00BF = [
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, INS_SYSTEM, ADDRMETH_M | OPTYPE_q | OP_W, ARG_NONE, ARG_NONE, 0, "vmxon", 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0)
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_F30FC7_rest = [
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0)
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_80 = [
( 0, INS_ADD, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "add", 0, 0, 0),  
( 0, INS_OR,  ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "or", 0, 0, 0),  
( 0, INS_ADD, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "adc", 0, 0, 0),  
( 0, INS_SUB, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "sbb", 0, 0, 0),  
( 0, INS_AND, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "and", 0, 0, 0),  
( 0, INS_SUB, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "sub", 0, 0, 0),  
( 0, INS_XOR, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "xor", 0, 0, 0),  
( 0, INS_CMP, ADDRMETH_E | OPTYPE_b | OP_R, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "cmp", 0, 0, 0   ) 
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_81 = [
( 0, INS_ADD, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_I | OPTYPE_z | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "add", 0, 0, 0),  
( 0, INS_OR,  ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_I | OPTYPE_z | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "or", 0, 0, 0),  
( 0, INS_ADD, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_I | OPTYPE_z | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "adc", 0, 0, 0),  
( 0, INS_SUB, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_I | OPTYPE_z | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "sbb", 0, 0, 0),  
( 0, INS_AND, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_I | OPTYPE_z | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "and", 0, 0, 0),  
( 0, INS_SUB, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_I | OPTYPE_z | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "sub", 0, 0, 0),  
( 0, INS_XOR, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_I | OPTYPE_z | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "xor", 0, 0, 0),  
( 0, INS_CMP, ADDRMETH_E | OPTYPE_v | OP_R, ADDRMETH_I | OPTYPE_z | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "cmp", 0, 0, 0   ) 
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_82 = [
( 0, INS_ADD, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "add", 0, 0, 0),  
( 0, INS_OR,  ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "or", 0, 0, 0),  
( 0, INS_ADD, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "adc", 0, 0, 0),  
( 0, INS_SUB, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "sbb", 0, 0, 0),  
( 0, INS_AND, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "and", 0, 0, 0),  
( 0, INS_SUB, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "sub", 0, 0, 0),  
( 0, INS_XOR, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "xor", 0, 0, 0),  
( 0, INS_CMP, ADDRMETH_E | OPTYPE_b | OP_R, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "cmp", 0, 0, 0   ) 
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_83 = [
( 0, INS_ADD, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "add", 0, 0, 0),  
( 0, INS_OR,  ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "or", 0, 0, 0),  
( 0, INS_ADD, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "adc", 0, 0, 0),  
( 0, INS_SUB, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "sbb", 0, 0, 0),  
( 0, INS_AND, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "and", 0, 0, 0),  
( 0, INS_SUB, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "sub", 0, 0, 0),  
( 0, INS_XOR, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "xor", 0, 0, 0),  
( 0, INS_CMP, ADDRMETH_E | OPTYPE_v | OP_R, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "cmp", 0, 0, 0   ) 
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_C0 = [
( 0, INS_ROL, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "rol", 0, 0, 0),  
( 0, INS_ROR, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "ror", 0, 0, 0),  
( 0, INS_ROL, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "rcl", 0, 0, 0),  
( 0, INS_ROR, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "rcr", 0, 0, 0),  
( 0, INS_SHL, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "shl", 0, 0, 0),  
( 0, INS_SHR, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "shr", 0, 0, 0),  
( 0, INS_SHL, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "sal", 0, 0, 0),  
( 0, INS_SHR, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "sar", 0, 0, 0   ) 
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_C1 = [
( 0, INS_ROL, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "rol", 0, 0, 0),  
( 0, INS_ROR, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "ror", 0, 0, 0),  
( 0, INS_ROL, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "rcl", 0, 0, 0),  
( 0, INS_ROR, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "rcr", 0, 0, 0),  
( 0, INS_SHL, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "shl", 0, 0, 0),  
( 0, INS_SHR, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "shr", 0, 0, 0),  
( 0, INS_SHL, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "sal", 0, 0, 0),  
( 0, INS_SHR, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "sar", 0, 0, 0   ) 
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_D0 = [
( 0, INS_ROL, ADDRMETH_E | OPTYPE_b | OP_W, OP_IMM  | OP_R, ARG_NONE, cpu_80386, "rol", 0, 1, 0),  
( 0, INS_ROR, ADDRMETH_E | OPTYPE_b | OP_W, OP_IMM  | OP_R, ARG_NONE, cpu_80386, "ror", 0, 1, 0),  
( 0, INS_ROL, ADDRMETH_E | OPTYPE_b | OP_W, OP_IMM  | OP_R, ARG_NONE, cpu_80386, "rcl", 0, 1, 0),  
( 0, INS_ROR, ADDRMETH_E | OPTYPE_b | OP_W, OP_IMM  | OP_R, ARG_NONE, cpu_80386, "rcr", 0, 1, 0),  
( 0, INS_SHL, ADDRMETH_E | OPTYPE_b | OP_W, OP_IMM  | OP_R, ARG_NONE, cpu_80386, "shl", 0, 1, 0),  
( 0, INS_SHR, ADDRMETH_E | OPTYPE_b | OP_W, OP_IMM  | OP_R, ARG_NONE, cpu_80386, "shr", 0, 1, 0),  
( 0, INS_SHL, ADDRMETH_E | OPTYPE_b | OP_W, OP_IMM  | OP_R, ARG_NONE, cpu_80386, "sal", 0, 1, 0),  
( 0, INS_SHR, ADDRMETH_E | OPTYPE_b | OP_W, OP_IMM  | OP_R, ARG_NONE, cpu_80386, "sar", 0, 1, 0   ) 
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_D1 = [
( 0, INS_ROL, ADDRMETH_E | OPTYPE_v | OP_W, OP_IMM | OP_R, ARG_NONE, cpu_80386, "rol", 0, 1, 0),  
( 0, INS_ROR, ADDRMETH_E | OPTYPE_v | OP_W, OP_IMM | OP_R, ARG_NONE, cpu_80386, "ror", 0, 1, 0),  
( 0, INS_ROL, ADDRMETH_E | OPTYPE_v | OP_W, OP_IMM | OP_R, ARG_NONE, cpu_80386, "rcl", 0, 1, 0),  
( 0, INS_ROR, ADDRMETH_E | OPTYPE_v | OP_W, OP_IMM | OP_R, ARG_NONE, cpu_80386, "rcr", 0, 1, 0),  
( 0, INS_SHL, ADDRMETH_E | OPTYPE_v | OP_W, OP_IMM | OP_R, ARG_NONE, cpu_80386, "shl", 0, 1, 0),  
( 0, INS_SHR, ADDRMETH_E | OPTYPE_v | OP_W, OP_IMM | OP_R, ARG_NONE, cpu_80386, "shr", 0, 1, 0),  
( 0, INS_SHL, ADDRMETH_E | OPTYPE_v | OP_W, OP_IMM | OP_R, ARG_NONE, cpu_80386, "sal", 0, 1, 0),  
( 0, INS_SHR, ADDRMETH_E | OPTYPE_v | OP_W, OP_IMM | OP_R, ARG_NONE, cpu_80386, "sar", 0, 1, 0   ) 
]
#( 0, INS_SHR, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_I | OP_IMM | OP_R, ARG_NONE, cpu_80386, "sar", 0, 1, 0   ) 


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_D2 = [
( 0, INS_ROL, ADDRMETH_E | OPTYPE_b | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "rol", 0, e_i386_regs.REG_CL, 0),  
( 0, INS_ROR, ADDRMETH_E | OPTYPE_b | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "ror", 0, e_i386_regs.REG_CL, 0),  
( 0, INS_ROL, ADDRMETH_E | OPTYPE_b | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "rcl", 0, e_i386_regs.REG_CL, 0),  
( 0, INS_ROR, ADDRMETH_E | OPTYPE_b | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "rcr", 0, e_i386_regs.REG_CL, 0),  
( 0, INS_SHL, ADDRMETH_E | OPTYPE_b | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "shl", 0, e_i386_regs.REG_CL, 0),  
( 0, INS_SHR, ADDRMETH_E | OPTYPE_b | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "shr", 0, e_i386_regs.REG_CL, 0),  
( 0, INS_SHL, ADDRMETH_E | OPTYPE_b | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "sal", 0, e_i386_regs.REG_CL, 0),  
( 0, INS_SHR, ADDRMETH_E | OPTYPE_b | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "sar", 0, e_i386_regs.REG_CL, 0   ) 
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_D3 = [
( 0, INS_ROL, ADDRMETH_E | OPTYPE_v | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "rol", 0, e_i386_regs.REG_CL, 0),  
( 0, INS_ROR, ADDRMETH_E | OPTYPE_v | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "ror", 0, e_i386_regs.REG_CL, 0),  
( 0, INS_ROL, ADDRMETH_E | OPTYPE_v | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "rcl", 0, e_i386_regs.REG_CL, 0),  
( 0, INS_ROR, ADDRMETH_E | OPTYPE_v | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "rcr", 0, e_i386_regs.REG_CL, 0),  
( 0, INS_SHL, ADDRMETH_E | OPTYPE_v | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "shl", 0, e_i386_regs.REG_CL, 0),  
( 0, INS_SHR, ADDRMETH_E | OPTYPE_v | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "shr", 0, e_i386_regs.REG_CL, 0),  
( 0, INS_SHL, ADDRMETH_E | OPTYPE_v | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "sal", 0, e_i386_regs.REG_CL, 0),  
( 0, INS_SHR, ADDRMETH_E | OPTYPE_v | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "sar", 0, e_i386_regs.REG_CL, 0   ) 
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_F6 = [
    (0, INS_TEST, ADDRMETH_E | OPTYPE_b | OP_R, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "test", 0, 0, 0),
    (0, INS_TEST, ADDRMETH_E | OPTYPE_b | OP_R, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "test", 0, 0, 0),
    (0, INS_NOT, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "not", 0, 0, 0),
    (0, INS_NEG, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "neg", 0, 0, 0),
    (0, INS_MUL, ADDRMETH_E | OPTYPE_b | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "mul", 0, 0, 0),
    (0, INS_MUL, ADDRMETH_E | OPTYPE_b | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "imul", 0, 0, 0),
    (0, INS_DIV, ADDRMETH_E | OPTYPE_b | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "div", 0, 0, 0),
    (0, INS_DIV, ADDRMETH_E | OPTYPE_b | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "idiv", 0, 0, 0)
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_F7 = [
    (0, INS_TEST, ADDRMETH_E | OPTYPE_v | OP_R, ADDRMETH_I | OPTYPE_z | OP_R, ARG_NONE, cpu_80386, "test", 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0   ),
    #( 0, INS_TEST, ADDRMETH_E | OPTYPE_v | OP_R, ADDRMETH_I | OPTYPE_z | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "test", 0, 0, 0),
    (0, INS_NOT, ADDRMETH_E | OPTYPE_v | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "not", 0, 0, 0),
    (0, INS_NEG, ADDRMETH_E | OPTYPE_v | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "neg", 0, 0, 0),
    (0, INS_MUL, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "mul", 0, 0, 0),
    (0, INS_MUL, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "imul", 0, 0, 0),
    (0, INS_DIV, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "div", 0, 0, 0),
    (0, INS_DIV, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "idiv", 0, 0, 0)
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_FE = [
    (0, INS_INC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "inc", 0, 0, 0),
    (0, INS_DEC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "dec", 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0)
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_FF = [
( 0, INS_INC, ADDRMETH_E | OPTYPE_v | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "inc", 0, 0, 0),  
( 0, INS_DEC, ADDRMETH_E | OPTYPE_v | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "dec", 0, 0, 0),  
( 0, INS_CALL, ADDRMETH_E | OPTYPE_v | OP_X | OP_64AUTO , ARG_NONE, ARG_NONE, cpu_80386, "call", 0, 0, 0),  
( 0, INS_CALL, ADDRMETH_E | OPTYPE_p | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "call", 0, 0, 0),  
( 0, INS_BRANCH, ADDRMETH_E | OPTYPE_v | OP_X | OP_64AUTO, ARG_NONE, ARG_NONE, cpu_80386, "jmp", 0, 0, 0),  # on amd64 this is jmp rnx
( 0, INS_BRANCH, ADDRMETH_E | OPTYPE_p | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jmp", 0, 0, 0),  
( 0, INS_PUSH, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "push", 0, 0, 0),  
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0   ) 
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_fpuD8_00BF = [
( 0,INS_FPU,ADDRMETH_M|OPTYPE_fs|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fadd",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_fs|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fmul",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_fs|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fcom",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_fs|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fcomp",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_fs|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fsub",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_fs|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fsubr",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_fs|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fdiv",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_fs|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fdivr",0,0,0)
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_fpuD8_rest = [
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fadd",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fadd",e_i386_regs.REG_ST0,e_i386_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fadd",e_i386_regs.REG_ST0,e_i386_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fadd",e_i386_regs.REG_ST0,e_i386_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fadd",e_i386_regs.REG_ST0,e_i386_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fadd",e_i386_regs.REG_ST0,e_i386_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fadd",e_i386_regs.REG_ST0,e_i386_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fadd",e_i386_regs.REG_ST0,e_i386_regs.REG_ST7,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmul",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmul",e_i386_regs.REG_ST0,e_i386_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmul",e_i386_regs.REG_ST0,e_i386_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmul",e_i386_regs.REG_ST0,e_i386_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmul",e_i386_regs.REG_ST0,e_i386_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmul",e_i386_regs.REG_ST0,e_i386_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmul",e_i386_regs.REG_ST0,e_i386_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmul",e_i386_regs.REG_ST0,e_i386_regs.REG_ST7,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcom",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcom",e_i386_regs.REG_ST0,e_i386_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcom",e_i386_regs.REG_ST0,e_i386_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcom",e_i386_regs.REG_ST0,e_i386_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcom",e_i386_regs.REG_ST0,e_i386_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcom",e_i386_regs.REG_ST0,e_i386_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcom",e_i386_regs.REG_ST0,e_i386_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcom",e_i386_regs.REG_ST0,e_i386_regs.REG_ST7,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomp",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomp",e_i386_regs.REG_ST0,e_i386_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomp",e_i386_regs.REG_ST0,e_i386_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomp",e_i386_regs.REG_ST0,e_i386_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomp",e_i386_regs.REG_ST0,e_i386_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomp",e_i386_regs.REG_ST0,e_i386_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomp",e_i386_regs.REG_ST0,e_i386_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomp",e_i386_regs.REG_ST0,e_i386_regs.REG_ST7,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsub",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsub",e_i386_regs.REG_ST0,e_i386_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsub",e_i386_regs.REG_ST0,e_i386_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsub",e_i386_regs.REG_ST0,e_i386_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsub",e_i386_regs.REG_ST0,e_i386_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsub",e_i386_regs.REG_ST0,e_i386_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsub",e_i386_regs.REG_ST0,e_i386_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsub",e_i386_regs.REG_ST0,e_i386_regs.REG_ST7,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubr",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubr",e_i386_regs.REG_ST0,e_i386_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubr",e_i386_regs.REG_ST0,e_i386_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubr",e_i386_regs.REG_ST0,e_i386_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubr",e_i386_regs.REG_ST0,e_i386_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubr",e_i386_regs.REG_ST0,e_i386_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubr",e_i386_regs.REG_ST0,e_i386_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubr",e_i386_regs.REG_ST0,e_i386_regs.REG_ST7,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdiv",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdiv",e_i386_regs.REG_ST0,e_i386_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdiv",e_i386_regs.REG_ST0,e_i386_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdiv",e_i386_regs.REG_ST0,e_i386_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdiv",e_i386_regs.REG_ST0,e_i386_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdiv",e_i386_regs.REG_ST0,e_i386_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdiv",e_i386_regs.REG_ST0,e_i386_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdiv",e_i386_regs.REG_ST0,e_i386_regs.REG_ST7,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivr",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivr",e_i386_regs.REG_ST0,e_i386_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivr",e_i386_regs.REG_ST0,e_i386_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivr",e_i386_regs.REG_ST0,e_i386_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivr",e_i386_regs.REG_ST0,e_i386_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivr",e_i386_regs.REG_ST0,e_i386_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivr",e_i386_regs.REG_ST0,e_i386_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivr",e_i386_regs.REG_ST0,e_i386_regs.REG_ST7,0 )
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_fpuD9_00BF = [
( 0,INS_FPU,ADDRMETH_M|OPTYPE_fs|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fld",0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_fs|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fst",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_fs|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fstp",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_fv|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fldenv",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_w|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fldcw",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_fv|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fnstenv",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_w|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fnstcw",0,0,0 )
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_fpuD9_rest = [
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fld",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fld",e_i386_regs.REG_ST0,e_i386_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fld",e_i386_regs.REG_ST0,e_i386_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fld",e_i386_regs.REG_ST0,e_i386_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fld",e_i386_regs.REG_ST0,e_i386_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fld",e_i386_regs.REG_ST0,e_i386_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fld",e_i386_regs.REG_ST0,e_i386_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fld",e_i386_regs.REG_ST0,e_i386_regs.REG_ST7,0 ),  

( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fxch",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fxch",e_i386_regs.REG_ST0,e_i386_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fxch",e_i386_regs.REG_ST0,e_i386_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fxch",e_i386_regs.REG_ST0,e_i386_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fxch",e_i386_regs.REG_ST0,e_i386_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fxch",e_i386_regs.REG_ST0,e_i386_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fxch",e_i386_regs.REG_ST0,e_i386_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fxch",e_i386_regs.REG_ST0,e_i386_regs.REG_ST7,0 ),  
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"fnop",0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"fchs",0,0,0 ),  
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"fabs",0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"ftst",0,0,0 ),  
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"fxam",0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"fld1",0,0,0 ),  
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"fldl2t",0,0,0 ),  
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"fldl2e",0,0,0 ),  
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"fldpi",0,0,0 ),  
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"fldlg2",0,0,0 ),  
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"fldln2",0,0,0 ),  
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"fldz",0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"f2xm1",0,0,0 ),  
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"fyl2x",0,0,0 ),  
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"fptan",0,0,0 ),  
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"fpatan",0,0,0 ),  
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"fxtract",0,0,0 ),  
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"fprem1",0,0,0 ),  
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"fdecstp",0,0,0 ),  
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"fincstp",0,0,0 ),  
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"fprem",0,0,0 ),  
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"fyl2xp1",0,0,0 ),  
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"fsqrt",0,0,0 ),  
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"fsincos",0,0,0 ),
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"frndint",0,0,0 ),
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"fscale",0,0,0 ),
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"fsin",0,0,0 ),
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"fcos",0,0,0 )
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_fpuDA_00BF = [
( 0,INS_FPU,ADDRMETH_M|OPTYPE_d|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fiadd",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_d|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fimul",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_d|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"ficom",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_d|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"ficomp",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_d|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fisub",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_d|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fisubr",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_d|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fidiv",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_d|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fidivr",0,0,0)
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_fpuDA_rest = [
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovb",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovb",e_i386_regs.REG_ST0,e_i386_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovb",e_i386_regs.REG_ST0,e_i386_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovb",e_i386_regs.REG_ST0,e_i386_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovb",e_i386_regs.REG_ST0,e_i386_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovb",e_i386_regs.REG_ST0,e_i386_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovb",e_i386_regs.REG_ST0,e_i386_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovb",e_i386_regs.REG_ST0,e_i386_regs.REG_ST7,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmove",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmove",e_i386_regs.REG_ST0,e_i386_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmove",e_i386_regs.REG_ST0,e_i386_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmove",e_i386_regs.REG_ST0,e_i386_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmove",e_i386_regs.REG_ST0,e_i386_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmove",e_i386_regs.REG_ST0,e_i386_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmove",e_i386_regs.REG_ST0,e_i386_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmove",e_i386_regs.REG_ST0,e_i386_regs.REG_ST7,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovbe",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovbe",e_i386_regs.REG_ST0,e_i386_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovbe",e_i386_regs.REG_ST0,e_i386_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovbe",e_i386_regs.REG_ST0,e_i386_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovbe",e_i386_regs.REG_ST0,e_i386_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovbe",e_i386_regs.REG_ST0,e_i386_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovbe",e_i386_regs.REG_ST0,e_i386_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovbe",e_i386_regs.REG_ST0,e_i386_regs.REG_ST7,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovu",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovu",e_i386_regs.REG_ST0,e_i386_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovu",e_i386_regs.REG_ST0,e_i386_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovu",e_i386_regs.REG_ST0,e_i386_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovu",e_i386_regs.REG_ST0,e_i386_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovu",e_i386_regs.REG_ST0,e_i386_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovu",e_i386_regs.REG_ST0,e_i386_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovu",e_i386_regs.REG_ST0,e_i386_regs.REG_ST7,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"fucompp",0,0,0 ), 
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 )
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_fpuDB_00BF = [
( 0,INS_FPU,ADDRMETH_M|OPTYPE_d|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fild",0,0,0 ),
(0,INS_FPU,ADDRMETH_M|OPTYPE_d|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fisttp",0,0,0),
( 0,INS_FPU,ADDRMETH_M|OPTYPE_d|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fist",0,0,0 ),
( 0,INS_FPU,ADDRMETH_M|OPTYPE_d|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fistp",0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_fe|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fld",0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_fe|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fstp",0,0,0)
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_fpuDB_rest = [
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnb",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnb",e_i386_regs.REG_ST0,e_i386_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnb",e_i386_regs.REG_ST0,e_i386_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnb",e_i386_regs.REG_ST0,e_i386_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnb",e_i386_regs.REG_ST0,e_i386_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnb",e_i386_regs.REG_ST0,e_i386_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnb",e_i386_regs.REG_ST0,e_i386_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnb",e_i386_regs.REG_ST0,e_i386_regs.REG_ST7,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovne",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovne",e_i386_regs.REG_ST0,e_i386_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovne",e_i386_regs.REG_ST0,e_i386_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovne",e_i386_regs.REG_ST0,e_i386_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovne",e_i386_regs.REG_ST0,e_i386_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovne",e_i386_regs.REG_ST0,e_i386_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovne",e_i386_regs.REG_ST0,e_i386_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovne",e_i386_regs.REG_ST0,e_i386_regs.REG_ST7,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnbe",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnbe",e_i386_regs.REG_ST0,e_i386_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnbe",e_i386_regs.REG_ST0,e_i386_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnbe",e_i386_regs.REG_ST0,e_i386_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnbe",e_i386_regs.REG_ST0,e_i386_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnbe",e_i386_regs.REG_ST0,e_i386_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnbe",e_i386_regs.REG_ST0,e_i386_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnbe",e_i386_regs.REG_ST0,e_i386_regs.REG_ST7,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnu",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnu",e_i386_regs.REG_ST0,e_i386_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnu",e_i386_regs.REG_ST0,e_i386_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnu",e_i386_regs.REG_ST0,e_i386_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnu",e_i386_regs.REG_ST0,e_i386_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnu",e_i386_regs.REG_ST0,e_i386_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnu",e_i386_regs.REG_ST0,e_i386_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnu",e_i386_regs.REG_ST0,e_i386_regs.REG_ST7,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"fclex",0,0,0 ),  
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"finit",0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucomi",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucomi",e_i386_regs.REG_ST0,e_i386_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucomi",e_i386_regs.REG_ST0,e_i386_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucomi",e_i386_regs.REG_ST0,e_i386_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucomi",e_i386_regs.REG_ST0,e_i386_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucomi",e_i386_regs.REG_ST0,e_i386_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucomi",e_i386_regs.REG_ST0,e_i386_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucomi",e_i386_regs.REG_ST0,e_i386_regs.REG_ST7,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomi",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomi",e_i386_regs.REG_ST0,e_i386_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomi",e_i386_regs.REG_ST0,e_i386_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomi",e_i386_regs.REG_ST0,e_i386_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomi",e_i386_regs.REG_ST0,e_i386_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomi",e_i386_regs.REG_ST0,e_i386_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomi",e_i386_regs.REG_ST0,e_i386_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomi",e_i386_regs.REG_ST0,e_i386_regs.REG_ST7,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 )
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_fpuDC_00BF = [
( 0,INS_FPU,ADDRMETH_M|OPTYPE_fd|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fadd",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_fd|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fmul",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_fd|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fcom",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_fd|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fcomp",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_fd|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fsub",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_fd|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fsubr",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_fd|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fdiv",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_fd|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fdivr",0,0,0)
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_fpuDC_rest = [
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fadd",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fadd",e_i386_regs.REG_ST1,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fadd",e_i386_regs.REG_ST2,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fadd",e_i386_regs.REG_ST3,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fadd",e_i386_regs.REG_ST4,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fadd",e_i386_regs.REG_ST5,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fadd",e_i386_regs.REG_ST6,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fadd",e_i386_regs.REG_ST7,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmul",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmul",e_i386_regs.REG_ST1,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmul",e_i386_regs.REG_ST2,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmul",e_i386_regs.REG_ST3,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmul",e_i386_regs.REG_ST4,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmul",e_i386_regs.REG_ST5,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmul",e_i386_regs.REG_ST6,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmul",e_i386_regs.REG_ST7,e_i386_regs.REG_ST0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubr",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubr",e_i386_regs.REG_ST1,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubr",e_i386_regs.REG_ST2,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubr",e_i386_regs.REG_ST3,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubr",e_i386_regs.REG_ST4,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubr",e_i386_regs.REG_ST5,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubr",e_i386_regs.REG_ST6,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubr",e_i386_regs.REG_ST7,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsub",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsub",e_i386_regs.REG_ST1,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsub",e_i386_regs.REG_ST2,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsub",e_i386_regs.REG_ST3,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsub",e_i386_regs.REG_ST4,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsub",e_i386_regs.REG_ST5,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsub",e_i386_regs.REG_ST6,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsub",e_i386_regs.REG_ST7,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivr",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivr",e_i386_regs.REG_ST1,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivr",e_i386_regs.REG_ST2,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivr",e_i386_regs.REG_ST3,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivr",e_i386_regs.REG_ST4,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivr",e_i386_regs.REG_ST5,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivr",e_i386_regs.REG_ST6,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivr",e_i386_regs.REG_ST7,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdiv",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdiv",e_i386_regs.REG_ST1,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdiv",e_i386_regs.REG_ST2,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdiv",e_i386_regs.REG_ST3,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdiv",e_i386_regs.REG_ST4,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdiv",e_i386_regs.REG_ST5,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdiv",e_i386_regs.REG_ST6,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdiv",e_i386_regs.REG_ST7,e_i386_regs.REG_ST0,0 )
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_fpuDD_00BF = [
( 0,INS_FPU,ADDRMETH_M|OPTYPE_fd|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fld",0,0,0 ),
(0,INS_FPU,ADDRMETH_M|OPTYPE_q|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fisttp",0,0,0),
( 0,INS_FPU,ADDRMETH_M|OPTYPE_fd|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fst",0,0,0 ),
( 0,INS_FPU,ADDRMETH_M|OPTYPE_fd|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fstp",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_fv|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"frstor",0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_fv|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fsave",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_w|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fstsw",0,0,0 )
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_fpuDD_rest = [
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"ffree",e_i386_regs.REG_ST0,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"ffree",e_i386_regs.REG_ST1,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"ffree",e_i386_regs.REG_ST2,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"ffree",e_i386_regs.REG_ST3,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"ffree",e_i386_regs.REG_ST4,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"ffree",e_i386_regs.REG_ST5,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"ffree",e_i386_regs.REG_ST6,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"ffree",e_i386_regs.REG_ST7,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fst",e_i386_regs.REG_ST0,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fst",e_i386_regs.REG_ST1,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fst",e_i386_regs.REG_ST2,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fst",e_i386_regs.REG_ST3,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fst",e_i386_regs.REG_ST4,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fst",e_i386_regs.REG_ST5,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fst",e_i386_regs.REG_ST6,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fst",e_i386_regs.REG_ST7,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fstp",e_i386_regs.REG_ST0,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fstp",e_i386_regs.REG_ST1,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fstp",e_i386_regs.REG_ST2,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fstp",e_i386_regs.REG_ST3,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fstp",e_i386_regs.REG_ST4,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fstp",e_i386_regs.REG_ST5,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fstp",e_i386_regs.REG_ST6,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fstp",e_i386_regs.REG_ST7,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucom",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucom",e_i386_regs.REG_ST1,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucom",e_i386_regs.REG_ST2,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucom",e_i386_regs.REG_ST3,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucom",e_i386_regs.REG_ST4,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucom",e_i386_regs.REG_ST5,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucom",e_i386_regs.REG_ST6,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucom",e_i386_regs.REG_ST7,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fucomp",e_i386_regs.REG_ST0,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fucomp",e_i386_regs.REG_ST1,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fucomp",e_i386_regs.REG_ST2,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fucomp",e_i386_regs.REG_ST3,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fucomp",e_i386_regs.REG_ST4,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fucomp",e_i386_regs.REG_ST5,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fucomp",e_i386_regs.REG_ST6,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fucomp",e_i386_regs.REG_ST7,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 )
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_fpuDE_00BF = [
( 0,INS_FPU,ADDRMETH_M|OPTYPE_w|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fiadd",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_w|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fimul",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_w|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"ficom",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_w|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"ficomp",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_w|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fisub",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_w|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fisubr",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_w|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fidiv",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_w|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fidivr",0,0,0)
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_fpuDE_rest = [
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"faddp",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"faddp",e_i386_regs.REG_ST1,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"faddp",e_i386_regs.REG_ST2,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"faddp",e_i386_regs.REG_ST3,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"faddp",e_i386_regs.REG_ST4,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"faddp",e_i386_regs.REG_ST5,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"faddp",e_i386_regs.REG_ST6,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"faddp",e_i386_regs.REG_ST7,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmulp",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmulp",e_i386_regs.REG_ST1,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmulp",e_i386_regs.REG_ST2,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmulp",e_i386_regs.REG_ST3,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmulp",e_i386_regs.REG_ST4,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmulp",e_i386_regs.REG_ST5,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmulp",e_i386_regs.REG_ST6,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmulp",e_i386_regs.REG_ST7,e_i386_regs.REG_ST0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"fcompp",0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubrp",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubrp",e_i386_regs.REG_ST1,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubrp",e_i386_regs.REG_ST2,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubrp",e_i386_regs.REG_ST3,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubrp",e_i386_regs.REG_ST4,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubrp",e_i386_regs.REG_ST5,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubrp",e_i386_regs.REG_ST6,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubrp",e_i386_regs.REG_ST7,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubp",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubp",e_i386_regs.REG_ST1,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubp",e_i386_regs.REG_ST2,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubp",e_i386_regs.REG_ST3,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubp",e_i386_regs.REG_ST4,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubp",e_i386_regs.REG_ST5,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubp",e_i386_regs.REG_ST6,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubp",e_i386_regs.REG_ST7,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivrp",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivrp",e_i386_regs.REG_ST1,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivrp",e_i386_regs.REG_ST2,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivrp",e_i386_regs.REG_ST3,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivrp",e_i386_regs.REG_ST4,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivrp",e_i386_regs.REG_ST5,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivrp",e_i386_regs.REG_ST6,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivrp",e_i386_regs.REG_ST7,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivp",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivp",e_i386_regs.REG_ST1,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivp",e_i386_regs.REG_ST2,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivp",e_i386_regs.REG_ST3,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivp",e_i386_regs.REG_ST4,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivp",e_i386_regs.REG_ST5,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivp",e_i386_regs.REG_ST6,e_i386_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivp",e_i386_regs.REG_ST7,e_i386_regs.REG_ST0,0 )
]



"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_fpuDF_00BF = [
    (0, INS_FPU, ADDRMETH_M | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80387, "fild", 0, 0, 0),
    (0, INS_FPU, ADDRMETH_M | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80387, "fisttp", 0, 0, 0),
    (0, INS_FPU, ADDRMETH_M | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80387, "fist", 0, 0, 0),
    (0, INS_FPU, ADDRMETH_M | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80387, "fistp", 0, 0, 0),
    (0, INS_FPU, ADDRMETH_M | OPTYPE_fb | OP_W, ARG_NONE, ARG_NONE, cpu_80387, "fbld", 0, 0, 0),
    (0, INS_FPU, ADDRMETH_M | OPTYPE_q | OP_W, ARG_NONE, ARG_NONE, cpu_80387, "fild", 0, 0, 0),
    (0, INS_FPU, ADDRMETH_M | OPTYPE_fb | OP_W, ARG_NONE, ARG_NONE, cpu_80387, "fbstp", 0, 0, 0),
    (0, INS_FPU, ADDRMETH_M | OPTYPE_q | OP_W, ARG_NONE, ARG_NONE, cpu_80387, "fistp", 0, 0, 0)
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_fpuDF_rest = [
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0, 0),
    (0, INS_FPU, OP_REG, ARG_NONE, ARG_NONE, cpu_80387, "fstsw", e_i386_regs.REG_AX, 0, 0),
    (0, 0, ARG_NONE, ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0),
    (0, 0, ARG_NONE, ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0),
    (0, 0, ARG_NONE, ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0),
    (0, 0, ARG_NONE, ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0),
    (0, 0, ARG_NONE, ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0),
    (0, 0, ARG_NONE, ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0),
    (0, 0, ARG_NONE, ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0),
    (0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucomip",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0),  
    (0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucomip",e_i386_regs.REG_ST0,e_i386_regs.REG_ST1,0),  
    (0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucomip",e_i386_regs.REG_ST0,e_i386_regs.REG_ST2,0),  
    (0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucomip",e_i386_regs.REG_ST0,e_i386_regs.REG_ST3,0),  
    (0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucomip",e_i386_regs.REG_ST0,e_i386_regs.REG_ST4,0),  
    (0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucomip",e_i386_regs.REG_ST0,e_i386_regs.REG_ST5,0),  
    (0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucomip",e_i386_regs.REG_ST0,e_i386_regs.REG_ST6,0),  
    (0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucomip",e_i386_regs.REG_ST0,e_i386_regs.REG_ST7,0),  
    (0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomip",e_i386_regs.REG_ST0,e_i386_regs.REG_ST0,0),
    (0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomip",e_i386_regs.REG_ST0,e_i386_regs.REG_ST1,0),
    (0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomip",e_i386_regs.REG_ST0,e_i386_regs.REG_ST2,0),
    (0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomip",e_i386_regs.REG_ST0,e_i386_regs.REG_ST3,0),
    (0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomip",e_i386_regs.REG_ST0,e_i386_regs.REG_ST4,0),
    (0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomip",e_i386_regs.REG_ST0,e_i386_regs.REG_ST5,0),
    (0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomip",e_i386_regs.REG_ST0,e_i386_regs.REG_ST6,0),
    (0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomip",e_i386_regs.REG_ST0,e_i386_regs.REG_ST7,0),
    (0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0),
    (0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0),
    (0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0),
    (0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0),
    (0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0),
    (0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0),
    (0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0),
    (0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0)
]


tbl_INVALID = [
    (0, 0, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0)
]

"""
These values allow an opcode to be sliced and diced to make it fit correctly into the current lookup table.

    (tbl32_0F, 0, 0xff, 0, 0xff),
    (tbl32_80, 3, 0x07, 0, 0xff, 4),

           Table pointer
           shift bits right        (eg.  >> 4 makes each line in the table valid for 16 
                                    numbers... ie 0xc0-0xcf are all one entry in the table)
           mask part of the byte   (eg.  & 0x7 only makes use of the 00000111 bits...)
           simple subtraction
           highest acceptable value
           tables86 entry to handle the falloff (from the previous check)

IMPORTANT: the decoder will assume the opcode is ultimately selected by bits in a MOD/RM 
    byte if the field in tabdesc[2] != 0xff
"""
tables86=[
    (tbl32_Main, 0, 0xff, 0, 0xff),              # 0
    (tbl32_0F, 0, 0xff, 0, 0xff),                # 1
    (tbl32_80, 3, 0x07, 0, 0xff),                # 2
    (tbl32_81, 3, 0x07, 0, 0xff),                # 3
    (tbl32_82, 3, 0x07, 0, 0xff),                # 4
    (tbl32_83, 3, 0x07, 0, 0xff),                # 5
    (tbl32_C0, 3, 0x07, 0, 0xff),                # 6
    (tbl32_C1, 3, 0x07, 0, 0xff),                # 7
    (tbl32_D0, 3, 0x07, 0, 0xff),                # 8
    (tbl32_D1, 3, 0x07, 0, 0xff),                # 9
    (tbl32_D2, 3, 0x07, 0, 0xff),                # 10
    (tbl32_D3, 3, 0x07, 0, 0xff),                # 11
    (tbl32_F6, 3, 0x07, 0, 0xff),                # 12
    (tbl32_F7, 3, 0x07, 0, 0xff),                # 13
    (tbl32_FE, 3, 0x07, 0, 0xff),                # 14
    (tbl32_FF, 3, 0x07, 0, 0xff),                # 15
    (tbl32_0F00, 3, 0x07, 0, 0xff),              # 16
    (tbl32_0F01_00BF, 3, 0x07, 0, 0xbf, 42),     # 17
    (tbl32_0F18, 3, 0x07, 0, 0xff),              # 18
    (tbl32_0F71, 3, 0x07, 0, 0xff),              # 19
    (tbl32_0F72, 3, 0x07, 0, 0xff),              # 20
    (tbl32_0F73, 3, 0x07, 0, 0xff),              # 21
    (tbl32_0FAE_00BF, 3, 0x07, 0, 0xbf, 53),     # 22
    (tbl32_0FBA, 3, 0x07, 0, 0xff),              # 23
    (tbl32_0FC7_00BF, 3, 0x07, 0, 0xbf, 25),     # 24
    (tbl32_0FC7_rest, 3, 0x07, 0xc0, 0xff),      # 25
    (tbl32_fpuD8_00BF, 3, 0x07, 0, 0xbf, 27),    # 26
    (tbl32_fpuD8_rest, 0, 0xff, 0xc0, 0xff),     # 27
    (tbl32_fpuD9_00BF, 3, 0x07, 0, 0xbf, 29),    # 28
    (tbl32_fpuD9_rest, 0, 0xff, 0xc0, 0xff),     # 29
    (tbl32_fpuDA_00BF, 3, 0x07, 0, 0xbf, 31),    # 30
    (tbl32_fpuDA_rest, 0, 0xff, 0xc0, 0xff),     # 31
    (tbl32_fpuDB_00BF, 3, 0x07, 0, 0xbf, 33),    # 32
    (tbl32_fpuDB_rest, 0, 0xff, 0xc0, 0xff),     # 33
    (tbl32_fpuDC_00BF, 3, 0x07, 0, 0xbf, 35),    # 34
    (tbl32_fpuDC_rest, 0, 0xff, 0xc0, 0xff),     # 35
    (tbl32_fpuDD_00BF, 3, 0x07, 0, 0xbf, 37),    # 36
    (tbl32_fpuDD_rest, 0, 0xff, 0xc0, 0xff),     # 37
    (tbl32_fpuDE_00BF, 3, 0x07, 0, 0xbf, 39),    # 38
    (tbl32_fpuDE_rest, 0, 0xff, 0xc0, 0xff),     # 39
    (tbl32_fpuDF_00BF, 3, 0x07, 0, 0xbf, 41),    # 40
    (tbl32_fpuDF_rest, 0, 0xff, 0xc0, 0xff),     # 41
    (tbl32_0F01_rest, 0, 0xff, 0xc0, 0xff),      # 42
    (tbl_INVALID, 0,0x00, 0, 0xff),              # 43
    (tbl32_660F, 0, 0xff, 0, 0xff),              # 44
    (tbl32_F20F, 0, 0xff, 0, 0xff),              # 45
    (tbl32_F30F, 0, 0xff, 0, 0xff),              # 46
    (tbl32_660FC7_00BF, 3, 0x07, 0, 0xff, 48),   # 47
    (tbl32_660FC7_rest, 3, 0x07, 0xc0, 0xff),    # 48
    (tbl32_F20FC7_00BF, 3, 0x07, 0, 0xff, 50),   # 49
    (tbl32_F20FC7_rest, 3, 0x07, 0xc0, 0xff),    # 50
    (tbl32_F30FC7_00BF, 3, 0x07, 0, 0xff, 52),   # 51
    (tbl32_F30FC7_rest, 3, 0x07, 0xc0, 0xff),    # 52
    (tbl32_0FAE_rest, 3, 0xff, 0xc0, 0xff),      # 53
    (tbl32_660F73, 3, 0x7, 0, 0xff),             # 54
    (tbl32_0F38, 0, 0xff, 0, 0xff),              # 55
    (tbl32_660F38, 0, 0xff, 0, 0xff),            # 56
    (tbl32_0F3A, 0, 0xff, 0, 0xff),              # 57
    (tbl32_660F3A, 0, 0xff, 0, 0xff),            # 58    - unused at present
    (tbl32_660F71, 3, 0x7, 0, 0xff),             # 59
    (tbl32_660F72, 3, 0x7, 0, 0xff),             # 60
    (tbl32_F20F38, 0, 0xff, 0xf0, 0xff),         # 61
    (tbl32_F30F38, 0, 0xff, 0xf0, 0xff),         # 62
]

regs=[
        ("eax", "REG_GENERAL,REG_RET", 4),
        ("ecx", "REG_GENERAL,REG_COUNT", 4),
        ("edx", "REG_GENERAL", 4),
        ("ebx", "REG_GENERAL", 4),
        ("esp", "REG_SP", 4),
        ("ebp", "REG_GENERAL,REG_FP", 4),
        ("esi", "REG_GENERAL,REG_SRC", 4),
        ("edi", "REG_GENERAL,REG_DEST", 4),
        ("ax", "REG_GENERAL,REG_RET", 2),
        ("cx", "REG_GENERAL,REG_COUNT", 2),
        ("dx", "REG_GENERAL", 2),
        ("bx", "REG_GENERAL", 2),
        ("sp", "REG_SP", 2),
        ("bp", "REG_GENERAL,REG_FP", 2),
        ("si", "REG_GENERAL,REG_SRC", 2),
        ("di", "REG_GENERAL,REG_DEST", 2),
        ("al", "REG_GENERAL", 1),
        ("cl", "REG_GENERAL", 1),
        ("dl", "REG_GENERAL", 1),
        ("bl", "REG_GENERAL", 1),
        ("ah", "REG_GENERAL", 1),
        ("ch", "REG_GENERAL", 1),
        ("dh", "REG_GENERAL", 1),
        ("bh", "REG_GENERAL", 1),
        ("mm0", "REG_SIMD", 4),
        ("mm1", "REG_SIMD", 4),
        ("mm2", "REG_SIMD", 4),
        ("mm3", "REG_SIMD", 4),
        ("mm4", "REG_SIMD", 4),
        ("mm5", "REG_SIMD", 4),
        ("mm6", "REG_SIMD", 4),
        ("mm7", "REG_SIMD", 4),
        ("xmm0", "REG_SIMD", 4),
        ("xmm1", "REG_SIMD", 4),
        ("xmm2", "REG_SIMD", 4),
        ("xmm3", "REG_SIMD", 4),
        ("xmm4", "REG_SIMD", 4),
        ("xmm5", "REG_SIMD", 4),
        ("xmm6", "REG_SIMD", 4),
        ("xmm7", "REG_SIMD", 4),
        ("dr0", "REG_DEBUG", 4),
        ("dr1", "REG_DEBUG", 4),
        ("dr2", "REG_DEBUG", 4),
        ("dr3", "REG_DEBUG", 4),
        ("dr4", "REG_DEBUG", 4),
        ("dr5", "REG_DEBUG", 4),
        ("dr6", "REG_DEBUG,REG_SYS", 4),
        ("dr7", "REG_DEBUG,REG_SYS", 4),
        ("cr0", "REG_SYS", 4),
        ("cr1", "REG_SYS", 4),
        ("cr2", "REG_SYS", 4),
        ("cr3", "REG_SYS", 4),
        ("cr4", "REG_SYS", 4),
        ("cr5", "REG_SYS", 4),
        ("cr6", "REG_SYS", 4),
        ("cr7", "REG_SYS", 4),
        ("tr0", "REG_SYS", 4),
        ("tr1", "REG_SYS", 4),
        ("tr2", "REG_SYS", 4),
        ("tr3", "REG_SYS", 4),
        ("tr4", "REG_SYS", 4),
        ("tr5", "REG_SYS", 4),
        ("tr6", "REG_SYS", 4),
        ("tr7", "REG_SYS", 4),
        ("es", "REG_DATASEG", 2),
        ("cs", "REG_CODESEG", 2),
        ("ss", "REG_STACKSEG", 2),
        ("ds", "REG_DATASEG", 2),
        ("fs", "REG_DATASEG", 2),
        ("gs", "REG_DATASEG", 2),
        (" ", "REG_INVALID", 0),
        (" ", "REG_INVALID", 0),
        ("st(0)", "REG_FPU", "OPSIZE_FPREG"),
        ("st(1)", "REG_FPU", "OPSIZE_FPREG"),
        ("st(2)", "REG_FPU", "OPSIZE_FPREG"),
        ("st(3)", "REG_FPU", "OPSIZE_FPREG"),
        ("st(4)", "REG_FPU", "OPSIZE_FPREG"),
        ("st(5)", "REG_FPU", "OPSIZE_FPREG"),
        ("st(6)", "REG_FPU", "OPSIZE_FPREG"),
        ("st(7)", "REG_FPU", "OPSIZE_FPREG"),
        ("eflags", "REG_CC", "OPSIZE_FPREG"),
        ("fpctrl", "REG_FPU,REG_SYS", 2),
        ("fpstat", "REG_FPU,REG_SYS", 2),
        ("fptag", "REG_FPU,REG_SYS", 2),
        ("eip", "REG_PC", 4),
        ("ip", "REG_PC", 2) ]

'''      DEPRECATED 131016 by atlas
prefix_table = {
    0xF0 : PREFIX_LOCK ,
    0xF2: PREFIX_REPNZ,
    0xF3: PREFIX_REP,
    0x2E: PREFIX_CS,
    0x36: PREFIX_SS,
    0x3E: PREFIX_DS,
    0x26: PREFIX_ES,
    0x64: PREFIX_FS,
    0x65: PREFIX_GS,
    0x66: PREFIX_OP_SIZE,
    0x67: PREFIX_ADDR_SIZE,
    0:    0
}
'''
