from envi.archs.i386.opconst import *
from . import regs as e_amd64_regs

# in order to be included, table name must be listed here.
tablenames = [  None,           # nexttable index 0 means NO TABLE!
                'tbl32_0F',
                'tbl32_0F00',
                'tbl32_0F01_00BF',
                'tbl32_0F01_rest',
                'tbl32_0F18',
                'tbl32_0F38',
                'tbl32_0F38F3',
                'tbl32_0F3A',
                'tbl32_0F71',
                'tbl32_0F72',
                'tbl32_0F73',
                'tbl32_0FAE_00BF',
                'tbl32_0FAE_rest',
                'tbl32_0FBA',
                'tbl32_0FC7_00BF',
                'tbl32_0FC7_rest',
                'tbl32_660F',
                'tbl32_660F38',
                'tbl32_660F3A',
                'tbl32_660F71',
                'tbl32_660F72',
                'tbl32_660F73',
                'tbl32_660FC7_00BF',
                'tbl32_660FC7_rest',
                'tbl32_80',
                'tbl32_81',
                'tbl32_82',
                'tbl32_83',
                'tbl32_C0',
                'tbl32_C1',
                'tbl32_D0',
                'tbl32_D1',
                'tbl32_D2',
                'tbl32_D3',
                'tbl32_F20F',
                'tbl32_F20F38',
                'tbl32_F20F3A',
                'tbl32_F30F',
                'tbl32_F30F38',
                'tbl32_F30FC7_00BF',
                'tbl32_F30FC7_rest',
                'tbl32_F30FAE_00BF',
                'tbl32_F30FAE_rest',
                #'tbl32_F3660F38',
                #'tbl32_F2660F',
                #'tbl32_F266',
                #'tbl32_F2660F38',
                #'tbl32_F3660F',
                #'tbl32_F366',
                'tbl32_F6',
                'tbl32_F7',
                'tbl32_FE',
                'tbl32_FF',
                'tbl32_Main',
                'tbl32_fpuD8_00BF',
                'tbl32_fpuD8_rest',
                'tbl32_fpuD9_00BF',
                'tbl32_fpuD9_rest',
                'tbl32_fpuDA_00BF',
                'tbl32_fpuDA_rest',
                'tbl32_fpuDB_00BF',
                'tbl32_fpuDB_rest',
                'tbl32_fpuDC_00BF',
                'tbl32_fpuDC_rest',
                'tbl32_fpuDD_00BF',
                'tbl32_fpuDD_rest',
                'tbl32_fpuDE_00BF',
                'tbl32_fpuDE_rest',
                'tbl32_fpuDF_00BF',
                'tbl32_fpuDF_rest',
                'tbl32_INVALID',
    ]
tables_lookup = {}

# generate TBL_* "constants"
for nidx in range(1, len(tablenames)):
    name = tablenames[nidx]
    stub = name[6:]
    const = "TBL_" + stub
    globals()[const] = nidx
    tables_lookup[nidx] = const

"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodenane", op0Register, op1Register, op2Register)
"""
tbl32_Main = [
(0, INS_ADD, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_G | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "add", 0, 0, 0),
(0, INS_ADD, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_G | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "add", 0, 0, 0),
(0, INS_ADD, ADDRMETH_G | OPTYPE_b | OP_W, ADDRMETH_E | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "add", 0, 0, 0),
(0, INS_ADD, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "add", 0, 0, 0),
(0, INS_ADD, OP_REG | OP_W, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "add", e_amd64_regs.REG_AL, 0, 0),  
(0, INS_ADD, OP_REG | OP_W, ADDRMETH_I | OPTYPE_z | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "add", e_amd64_regs.REG_EAX, 0, 0),  
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(0, INS_OR, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_G | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "or", 0, 0, 0),  
(0, INS_OR, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_G | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "or", 0, 0, 0),  
(0, INS_OR, ADDRMETH_G | OPTYPE_b | OP_W, ADDRMETH_E | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "or", 0, 0, 0),  
(0, INS_OR, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "or", 0, 0, 0),  
(0, INS_OR, OP_REG | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "or", e_amd64_regs.REG_AL, 0, 0),  
(0, INS_OR, OP_REG | OP_W, ADDRMETH_I | OPTYPE_z | OP_R, ARG_NONE, cpu_80386, "or", e_amd64_regs.REG_EAX, 0, 0),  
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(TBL_0F, 0, 0, 0, 0, cpu_80386, 0, 0, 0, 0),  # 0x0f
# 0x10
( 0, INS_ADD, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_G | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "adc", 0, 0, 0),  
( 0, INS_ADD, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_G | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "adc", 0, 0, 0),  
( 0, INS_ADD, ADDRMETH_G | OPTYPE_b | OP_W, ADDRMETH_E | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "adc", 0, 0, 0),  
( 0, INS_ADD, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "adc", 0, 0, 0),  
( 0, INS_ADD, OP_REG | OP_W, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "adc", e_amd64_regs.REG_AL, 0, 0),  
( 0, INS_ADD, OP_REG | OP_W, ADDRMETH_I | OPTYPE_z | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "adc", e_amd64_regs.REG_EAX, 0, 0),  
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
( 0, INS_SUB, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_G | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "sbb", 0, 0, 0),  
( 0, INS_SUB, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_G | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "sbb", 0, 0, 0),  
( 0, INS_SUB, ADDRMETH_G | OPTYPE_b | OP_W, ADDRMETH_E | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "sbb", 0, 0, 0),  
( 0, INS_SUB, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "sbb", 0, 0, 0),  
( 0, INS_SUB, OP_REG | OP_W, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "sbb", e_amd64_regs.REG_AL, 0, 0),  
( 0, INS_SUB, OP_REG | OP_W, ADDRMETH_I | OPTYPE_z | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "sbb", e_amd64_regs.REG_EAX, 0, 0),  
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
# 0x20
( 0, INS_AND, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_G | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "and", 0, 0, 0),  
( 0, INS_AND, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_G | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "and", 0, 0, 0),  
( 0, INS_AND, ADDRMETH_G | OPTYPE_b | OP_W, ADDRMETH_E | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "and", 0, 0, 0),  
( 0, INS_AND, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "and", 0, 0, 0),  
( 0, INS_AND, OP_REG | OP_W, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "and", e_amd64_regs.REG_AL, 0, 0),  
( 0, INS_AND, OP_REG | OP_W, ADDRMETH_I | OPTYPE_z | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "and", e_amd64_regs.REG_EAX, 0, 0),
( 0, INSTR_PREFIX, 0, 0, 0, cpu_80386, 0, 0, 0, 0),
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
( 0, INS_SUB, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_G | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "sub", 0, 0, 0),  
( 0, INS_SUB, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_G | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "sub", 0, 0, 0),  
( 0, INS_SUB, ADDRMETH_G | OPTYPE_b | OP_W, ADDRMETH_E | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "sub", 0, 0, 0),  
( 0, INS_SUB, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "sub", 0, 0, 0),  
( 0, INS_SUB, OP_REG | OP_W, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "sub", e_amd64_regs.REG_AL, 0, 0),  
( 0, INS_SUB, OP_REG | OP_W, ADDRMETH_I | OPTYPE_z | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "sub", e_amd64_regs.REG_EAX, 0, 0),  
( 0, INSTR_PREFIX, 0, 0, 0, cpu_80386, 0, 0, 0, 0),
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
# 0x30
( 0, INS_XOR, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_G | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "xor", 0, 0, 0),  
( 0, INS_XOR, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_G | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "xor", 0, 0, 0),  
( 0, INS_XOR, ADDRMETH_G | OPTYPE_b | OP_W, ADDRMETH_E | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "xor", 0, 0, 0),  
( 0, INS_XOR, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "xor", 0, 0, 0),  
( 0, INS_XOR, OP_REG | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "xor", e_amd64_regs.REG_AL, 0, 0),  
( 0, INS_XOR, OP_REG | OP_W, ADDRMETH_I | OPTYPE_z | OP_R, ARG_NONE, cpu_80386, "xor", e_amd64_regs.REG_EAX, 0, 0),  
( 0, INSTR_PREFIX, 0, 0, 0, cpu_80386, 0, 0, 0, 0),  
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
( 0, INS_CMP, ADDRMETH_E | OPTYPE_b | OP_R, ADDRMETH_G | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "cmp", 0, 0, 0),  
( 0, INS_CMP, ADDRMETH_E | OPTYPE_v | OP_R, ADDRMETH_G | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "cmp", 0, 0, 0),  
( 0, INS_CMP, ADDRMETH_G | OPTYPE_b | OP_R, ADDRMETH_E | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "cmp", 0, 0, 0),  
( 0, INS_CMP, ADDRMETH_G | OPTYPE_v | OP_R, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "cmp", 0, 0, 0),  
( 0, INS_CMP, OP_REG | OP_R, ADDRMETH_I | OPTYPE_b | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "cmp", e_amd64_regs.REG_AL, 0, 0),  
( 0, INS_CMP, OP_REG | OP_R, ADDRMETH_I | OPTYPE_z | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "cmp", e_amd64_regs.REG_EAX, 0, 0),  
( 0, INSTR_PREFIX, 0, 0, 0, cpu_80386, 0, 0, 0, 0),  
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
# 0x40 - inc/dec not ok in AMD64 - REX area
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
# 0x50
( 0, INS_PUSH, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "push", e_amd64_regs.REG_RAX, 0, 0),  
( 0, INS_PUSH, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "push", e_amd64_regs.REG_RCX, 0, 0),  
( 0, INS_PUSH, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "push", e_amd64_regs.REG_RDX, 0, 0),  
( 0, INS_PUSH, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "push", e_amd64_regs.REG_RBX, 0, 0),  
( 0, INS_PUSH, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "push", e_amd64_regs.REG_RSP, 0, 0),  
( 0, INS_PUSH, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "push", e_amd64_regs.REG_RBP, 0, 0),  
( 0, INS_PUSH, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "push", e_amd64_regs.REG_RSI, 0, 0),  
( 0, INS_PUSH, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "push", e_amd64_regs.REG_RDI, 0, 0),  

( 0, INS_POP, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "pop", e_amd64_regs.REG_RAX, 0, 0),
( 0, INS_POP, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "pop", e_amd64_regs.REG_RCX, 0, 0),
( 0, INS_POP, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "pop", e_amd64_regs.REG_RDX, 0, 0),
( 0, INS_POP, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "pop", e_amd64_regs.REG_RBX, 0, 0),
( 0, INS_POP, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "pop", e_amd64_regs.REG_RSP, 0, 0),
( 0, INS_POP, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "pop", e_amd64_regs.REG_RBP, 0, 0),
( 0, INS_POP, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "pop", e_amd64_regs.REG_RSI, 0, 0),
( 0, INS_POP, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "pop", e_amd64_regs.REG_RDI, 0, 0),
# 0x60
( 0, INS_PUSHREGS, 0, 0, 0, cpu_80386, "pushad", 0, 0, 0),  
( 0, INS_POPREGS, 0, 0, 0, cpu_80386, "popad", 0, 0, 0),  
( 0, INS_BOUNDS, ADDRMETH_G | OPTYPE_v | OP_R, ADDRMETH_M | OPTYPE_a | OP_R, ARG_NONE, cpu_80386, "bound", 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_G | OPTYPE_qp | OP_W, ADDRMETH_E | OPTYPE_ds | OP_R, ARG_NONE, cpu_AMD64, "movsxd", 0, 0, 0),
( 0, INSTR_PREFIX, 0, 0, 0, cpu_80386, 0, 0, 0, 0),  
( 0, INSTR_PREFIX, 0, 0, 0, cpu_80386, 0, 0, 0, 0),  
(TBL_660F, INSTR_PREFIX, 0, 0, 0, cpu_80386, 0, 0, 0, 0),  # 0x66
( 0, INSTR_PREFIX, 0, 0, 0, cpu_80386, 0, 0, 0, 0),  
( 0, INS_PUSH, ADDRMETH_I | OPTYPE_v | OP_R | OP_SIGNED, ARG_NONE, ARG_NONE, cpu_80386, "push", 0, 0, 0),
( 0, INS_MUL,  ADDRMETH_G | OPTYPE_v | OP_R, ADDRMETH_E | OPTYPE_v | OP_R, ADDRMETH_I | OP_SIGNED | OPTYPE_z | OP_R, cpu_80386, "imul", 0, 0, 0),
( 0, INS_PUSH, ADDRMETH_I | OPTYPE_b | OP_R | OP_SIGNED, ARG_NONE, ARG_NONE, cpu_80386, "push", 0, 0, 0),
( 0, INS_MUL,  ADDRMETH_G | OPTYPE_v | OP_R, ADDRMETH_E | OPTYPE_v | OP_R, ADDRMETH_I | OP_SIGNED | OP_R | OPTYPE_b, cpu_80386, "imul", 0, 0, 0),
( 0, INS_IN,  ADDRMETH_Y | OPTYPE_b | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "insb", 0, e_amd64_regs.REG_DX, 0),  
( 0, INS_IN,  ADDRMETH_Y | OPTYPE_z | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "insd", 0, e_amd64_regs.REG_DX, 0),  
( 0, INS_OUT,  OP_REG | OP_W, ADDRMETH_X | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "outsb", e_amd64_regs.REG_DX, 0, 0),  
( 0, INS_OUT,  OP_REG | OP_W, ADDRMETH_X | OPTYPE_z | OP_R, ARG_NONE, cpu_80386, "outsd", e_amd64_regs.REG_DX, 0, 0),  
# 0x70
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jo", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jno", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jc", 0, 0, 0),
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jnc", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jz", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jnz", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jbe", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "ja", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "js", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jns", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jpe", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jpo", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jl", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jge", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jle", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jg", 0, 0, 0),  
# 0x80
(TBL_80, 0, ADDRMETH_E | OPTYPE_b, ADDRMETH_I | OPTYPE_b, ARG_NONE,cpu_80386, 0, 0, 0, 0),  
(TBL_81, 0, ADDRMETH_E | OPTYPE_v, ADDRMETH_I | OPTYPE_v, ARG_NONE, cpu_80386, 0, 0, 0, 0),  
(TBL_82, 0, ADDRMETH_E | OPTYPE_v, ADDRMETH_I | OPTYPE_b, ARG_NONE, cpu_80386, 0, 0, 0, 0),  
(TBL_83, 0, ADDRMETH_E | OPTYPE_v, ADDRMETH_I | OPTYPE_b, ARG_NONE, cpu_80386, 0, 0, 0, 0),  
( 0, INS_TEST, ADDRMETH_E | OPTYPE_b | OP_R, ADDRMETH_G | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "test", 0, 0, 0),  
( 0, INS_TEST, ADDRMETH_E | OPTYPE_v | OP_R, ADDRMETH_G | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "test", 0, 0, 0),  
( 0, INS_XCHG, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_G | OPTYPE_b | OP_W, ARG_NONE, cpu_80386, "xchg", 0, 0, 0),  
( 0, INS_XCHG, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_G | OPTYPE_v | OP_W, ARG_NONE, cpu_80386, "xchg", 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_G | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "mov", 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_G | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "mov", 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_G | OPTYPE_b | OP_W, ADDRMETH_E | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "mov", 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "mov", 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_E | OPTYPE_v | OP_W | OP_MEM_W, ADDRMETH_S | OPTYPE_w | OP_R, ARG_NONE, cpu_80386, "mov", 0, 0, 0),
( 0, INS_LEA, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_M | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "lea", 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_S | OPTYPE_w | OP_W, ADDRMETH_E | OPTYPE_v | OP_R | OP_MEM_W, ARG_NONE, cpu_80386, "mov", 0, 0, 0),
( 0, INS_POP, OP_64AUTO | ADDRMETH_M | OPTYPE_v | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "pop", 0, 0, 0),
# 0x90
(0, INS_NOP, 0, 0, 0, cpu_80386, "nop", 0, 0, 0),  
( 0, INS_XCHG, OP_REG | OP_W, OP_REG | OP_W, ARG_NONE, cpu_80386, "xchg", e_amd64_regs.REG_EAX, e_amd64_regs.REG_ECX, 0),  
( 0, INS_XCHG, OP_REG | OP_W, OP_REG | OP_W, ARG_NONE, cpu_80386, "xchg", e_amd64_regs.REG_EAX, e_amd64_regs.REG_EDX, 0),  
( 0, INS_XCHG, OP_REG | OP_W, OP_REG | OP_W, ARG_NONE, cpu_80386, "xchg", e_amd64_regs.REG_EAX, e_amd64_regs.REG_EBX, 0),  
( 0, INS_XCHG, OP_REG | OP_W, OP_REG | OP_W, ARG_NONE, cpu_80386, "xchg", e_amd64_regs.REG_EAX, e_amd64_regs.REG_ESP, 0),  
( 0, INS_XCHG, OP_REG | OP_W, OP_REG | OP_W, ARG_NONE, cpu_80386, "xchg", e_amd64_regs.REG_EAX, e_amd64_regs.REG_EBP, 0),  
( 0, INS_XCHG, OP_REG | OP_W, OP_REG | OP_W, ARG_NONE, cpu_80386, "xchg", e_amd64_regs.REG_EAX, e_amd64_regs.REG_ESI, 0),  
( 0, INS_XCHG, OP_REG | OP_W, OP_REG | OP_W, ARG_NONE, cpu_80386, "xchg", e_amd64_regs.REG_EAX, e_amd64_regs.REG_EDI, 0),  
( 0, INS_SZCONV, 0, 0, 0, cpu_80386, "cwde", 0, 0, 0),  
( 0, INS_SZCONV, 0, 0, 0, cpu_80386, "cdq", 0, 0, 0),  
( 0, INS_CALL, ADDRMETH_A | OPTYPE_p | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "callf", 0, 0, 0),  
( 0, INS_SYSTEM, 0, 0, 0, cpu_80386, "wait", 0, 0, 0),  # TODO: There's a whole set of screw you opcodes that also start here like fstenv
( 0, INS_PUSHFLAGS, 0, 0, 0, cpu_80386, "pushfd", 0, 0, 0),  
( 0, INS_POPFLAGS, 0, 0, 0, cpu_80386, "popfd", 0, 0, 0),  
( 0, INS_MOV, 0, 0, 0, cpu_80386, "sahf", 0, 0, 0),  
( 0, INS_MOV, 0, 0, 0, cpu_80386, "lahf", 0, 0, 0),  
# 0xa0
(0, INS_MOV, OP_REG | OP_W, ADDRMETH_O | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "mov", e_amd64_regs.REG_AL, 0, 0),  
(0, INS_MOV, OP_REG | OP_W, ADDRMETH_O | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "mov", e_amd64_regs.REG_EAX, 0, 0),  
(0, INS_MOV, ADDRMETH_O | OPTYPE_b | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "mov", 0, e_amd64_regs.REG_AL, 0),  
(0, INS_MOV, ADDRMETH_O | OPTYPE_v | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "mov", 0, e_amd64_regs.REG_EAX, 0),  
(0, INS_STRMOV, 0, 0, 0, cpu_80386, "movsb", 0, 0, 0),
# Yes there should be movsw here, but it shares the same opcode as movsw, so skip it
(0, INS_STRMOV, 0, 0, 0, cpu_80386, "movsd", 0, 0, 0),
(0, INS_STRCMP, 0, 0, 0, cpu_80386, "cmpsb", 0, 0, 0),
(0, INS_STRCMP, 0, 0, 0, cpu_80386, "cmpsd", 0, 0, 0),
(0, INS_TEST, OP_REG | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "test", e_amd64_regs.REG_AL, 0, 0),  
(0, INS_TEST, OP_REG | OP_R, ADDRMETH_I | OPTYPE_z | OP_R, ARG_NONE, cpu_80386, "test", e_amd64_regs.REG_EAX, 0, 0),  
(0, INS_STRSTOR, 0, 0, 0, cpu_80386, "stosb", 0, 0, 0),
# Yes there should be stosw here, but it shares the same opcode as stosd, so skip it
(0, INS_STRSTOR, 0, 0, 0, cpu_80386, "stosd", 0, 0, 0),
(0, INS_STRLOAD, 0, 0, 0, cpu_80386, "lodsb", 0, 0, 0),
(0, INS_STRLOAD, 0, 0, 0, cpu_80386, "lodsd", 0, 0, 0),
(0, INS_STRCMP, 0, 0, 0, cpu_80386, "scasb", 0, 0, 0),
(0, INS_STRCMP, 0, 0, 0, cpu_80386, "scasd", 0, 0, 0),
# 0xb0
( 0, INS_MOV, OP_REG | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "mov", e_amd64_regs.REG_AL, 0, 0),  
( 0, INS_MOV, OP_REG | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "mov", e_amd64_regs.REG_CL, 0, 0),  
( 0, INS_MOV, OP_REG | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "mov", e_amd64_regs.REG_DL, 0, 0),  
( 0, INS_MOV, OP_REG | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "mov", e_amd64_regs.REG_BL, 0, 0),  
# FIXME 64
( 0, INS_MOV, OP_REG | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "mov", e_amd64_regs.REG_AH, 0, 0),  
( 0, INS_MOV, OP_REG | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "mov", e_amd64_regs.REG_CH, 0, 0),  
( 0, INS_MOV, OP_REG | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "mov", e_amd64_regs.REG_DH, 0, 0),  
( 0, INS_MOV, OP_REG | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "mov", e_amd64_regs.REG_BH, 0, 0),  

( 0, INS_MOV, OP_REG | OP_W, ADDRMETH_I | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "mov", e_amd64_regs.REG_EAX, 0, 0),  
( 0, INS_MOV, OP_REG | OP_W, ADDRMETH_I | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "mov", e_amd64_regs.REG_ECX, 0, 0),  
( 0, INS_MOV, OP_REG | OP_W, ADDRMETH_I | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "mov", e_amd64_regs.REG_EDX, 0, 0),  
( 0, INS_MOV, OP_REG | OP_W, ADDRMETH_I | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "mov", e_amd64_regs.REG_EBX, 0, 0),  
( 0, INS_MOV, OP_REG | OP_W, ADDRMETH_I | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "mov", e_amd64_regs.REG_ESP, 0, 0),  
( 0, INS_MOV, OP_REG | OP_W, ADDRMETH_I | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "mov", e_amd64_regs.REG_EBP, 0, 0),  
( 0, INS_MOV, OP_REG | OP_W, ADDRMETH_I | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "mov", e_amd64_regs.REG_ESI, 0, 0),  
( 0, INS_MOV, OP_REG | OP_W, ADDRMETH_I | OPTYPE_v | OP_R, ARG_NONE, cpu_80386, "mov", e_amd64_regs.REG_EDI, 0, 0),  
# 0xc0
(TBL_C0, 0,  ADDRMETH_E | OPTYPE_b, ADDRMETH_I | OPTYPE_b, ARG_NONE, cpu_80386, 0, 0, 0, 0),  
(TBL_C1, 0,  ADDRMETH_E | OPTYPE_v, ADDRMETH_I | OPTYPE_b, ARG_NONE, cpu_80386, 0, 0, 0, 0),  
( 0, INS_RET, ADDRMETH_I | OPTYPE_w | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "ret", 0, 0, 0),  
( 0, INS_RET, 0, 0, 0, cpu_80386, "ret", 0, 0, 0),  
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0), # VEX 3 byte
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  #lds (AMD) # VEX 2 byte
( 0, INS_MOV, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "mov", 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_I | OPTYPE_z | OP_R, ARG_NONE, cpu_80386, "mov", 0, 0, 0),  
( 0, INS_ENTER, ADDRMETH_I | OPTYPE_w | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "enter", 0, 0, 0),  
( 0, INS_LEAVE, 0, 0, 0, cpu_80386, "leave", 0, 0, 0),  
( 0, INS_RET, ADDRMETH_I | OPTYPE_w | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "retf", 0, 0, 0),  
( 0, INS_RET, 0, 0, 0, cpu_80386, "retf", 0, 0, 0),  
( 0, INS_DEBUG, 0, 0, 0, cpu_80386, "int3", 0, 0, 0),  
( 0, INS_TRAP, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "int", 0, 0, 0),  
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
( 0, INS_TRET, 0, 0, 0, cpu_80386, "iret", 0, 0, 0),  
# 0xd0
(TBL_D0, 0,  ADDRMETH_E | OPTYPE_b, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 1, 0),  
(TBL_D1, 0, ADDRMETH_E | OPTYPE_v, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 1, 0),  
(TBL_D2, 0, ADDRMETH_E | OPTYPE_b, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, e_amd64_regs.REG_CL, 0),  
(TBL_D3, 0, ADDRMETH_E | OPTYPE_v, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, e_amd64_regs.REG_CL, 0),  
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(0, 0, 0, 0, 0, cpu_80386, 0, 0, 0, 0),  
(0, INS_XLAT, 0, 0, 0, cpu_80386, "xlat", 0, 0, 0),  
(TBL_fpuD8_00BF, 0, 0, 0, 0, cpu_80386, 0, 0, 0, 0),  
(TBL_fpuD9_00BF, 0, 0, 0, 0, cpu_80386, 0, 0, 0, 0),  
(TBL_fpuDA_00BF, 0, 0, 0, 0, cpu_80386, 0, 0, 0, 0),  
(TBL_fpuDB_00BF, 0, 0, 0, 0, cpu_80386, 0, 0, 0, 0),  
(TBL_fpuDC_00BF, 0, 0, 0, 0, cpu_80386, 0, 0, 0, 0),  
(TBL_fpuDD_00BF, 0, 0, 0, 0, cpu_80386, 0, 0, 0, 0),  
(TBL_fpuDE_00BF, 0, 0, 0, 0, cpu_80386, 0, 0, 0, 0),  
(TBL_fpuDF_00BF, 0, 0, 0, 0, cpu_80386, 0, 0, 0, 0),  
# 0xe0
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "loopnz", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "loopz", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "loop", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jecxz", 0, 0, 0),  
( 0, INS_IN, OP_REG | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "in", e_amd64_regs.REG_AL, 0, 0),  
( 0, INS_IN, OP_REG | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "in", e_amd64_regs.REG_EAX, 0, 0),  
( 0, INS_OUT, ADDRMETH_I | OPTYPE_b | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "out", 0, e_amd64_regs.REG_AL, 0),  
( 0, INS_OUT, ADDRMETH_I | OPTYPE_b | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "out", 0, e_amd64_regs.REG_EAX, 0),  
( 0, INS_CALL, ADDRMETH_J | OPTYPE_v | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "call", 0, 0, 0),  
( 0, INS_BRANCH, ADDRMETH_J | OPTYPE_v | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jmp", 0, 0, 0),  
( 0, INS_BRANCH, ADDRMETH_A | OPTYPE_p | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jmp", 0, 0, 0),  
( 0, INS_BRANCH, ADDRMETH_J | OPTYPE_b | OP_X, ARG_NONE, ARG_NONE, cpu_80386, "jmp", 0, 0, 0),  
( 0, INS_IN, OP_REG | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "in", e_amd64_regs.REG_AL, e_amd64_regs.REG_DX, 0),  
( 0, INS_IN, OP_REG | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "in", e_amd64_regs.REG_EAX, e_amd64_regs.REG_DX, 0),  
( 0, INS_OUT, OP_REG | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "out", e_amd64_regs.REG_DX, e_amd64_regs.REG_AL, 0),  
( 0, INS_OUT, OP_REG | OP_W, OP_REG | OP_R, ARG_NONE, cpu_80386, "out", e_amd64_regs.REG_DX, e_amd64_regs.REG_EAX, 0),  
# 0xf0
( 0, INSTR_PREFIX, 0, 0, 0, cpu_80386, "lock:", 0, 0, 0),  
(0, INS_TRAP, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "int1", 0, 0, 0),
(TBL_F20F, INSTR_PREFIX, 0, 0, 0, cpu_80386, "repne:", 0, 0, 0),
(TBL_F30F, INSTR_PREFIX, 0, 0, 0, cpu_80386, "rep:", 0, 0, 0),
( 0, INS_HALT, 0, 0, 0, cpu_80386, "hlt", 0, 0, 0),  
( 0, INS_TOGCF, 0, 0, 0, cpu_80386, "cmc", 0, 0, 0),  
(TBL_F6, 0,  ADDRMETH_E | OPTYPE_b, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 0, 0),  
(TBL_F7, 0, ADDRMETH_E | OPTYPE_v, ARG_NONE, ARG_NONE, cpu_80386, 0, 0, 0, 0),  
( 0, INS_CLEARCF, 0, 0, 0, cpu_80386, "clc", 0, 0, 0),  
( 0, INS_SETCF, 0, 0, 0, cpu_80386, "stc", 0, 0, 0),  
( 0, INS_SYSTEM, 0, 0, 0, cpu_80386, "cli", 0, 0, 0),  
( 0, INS_SYSTEM, 0, 0, 0, cpu_80386, "sti", 0, 0, 0),  
( 0, INS_CLEARDF, 0, 0, 0, cpu_80386, "cld", 0, 0, 0),  
( 0, INS_SETDF, 0, 0, 0, cpu_80386, "std", 0, 0, 0),  
(TBL_FE, 0, 0, 0, 0, cpu_80386, 0, 0, 0, 0),  
(TBL_FF, 0, 0, 0, 0, cpu_80386, 0, 0, 0, 0   )
]
desc_Main       = (tbl32_Main,3,0,0xff,0,0xff)

"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_0F = [
# 0f00
(TBL_0F00, 0, 0, 0, 0, ARG_NONE, cpu_80386, 0, 0, 0, 0),  
(TBL_0F01_00BF, 0, 0, 0, 0, ARG_NONE, cpu_80386, 0, 0, 0, 0),  
( 0, INS_SYSTEM, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_w | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "lar", 0, 0, 0),  
( 0, INS_SYSTEM, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_w | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "lsl", 0, 0, 0),  
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
( 0, INS_SYSTEM, 0, 0, 0, ARG_NONE, cpu_AMD64, "syscall", 0, 0, 0),
( 0, INS_SYSTEM, 0, 0, 0, ARG_NONE, cpu_80386, "clts", 0, 0, 0),  
( 0, INS_SYSTEM, 0, 0, 0, ARG_NONE, cpu_AMD64, "sysret", 0, 0, 0),
( 0, INS_SYSTEM, 0, 0, 0, ARG_NONE, cpu_80486, "invd", 0, 0, 0),  
( 0, INS_SYSTEM, 0, 0, 0, ARG_NONE, cpu_80486, "wbinvd", 0, 0, 0),  
( 0, 0, 0, 0, 0, ARG_NONE, cpu_80386, 0, 0, 0, 0),  
( 0, INS_INVALIDOP, 0, 0, 0, ARG_NONE, cpu_80386, "ud2", 0, 0, 0),
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_E | OPTYPE_v, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "prefetchw", 0, 0, 0),  
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
# 0f10
( 0, INS_MOV,   ADDRMETH_V | OPTYPE_ps | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "movups", 0, 0, 0),  
( 0, INS_MOV,   ADDRMETH_W | OPTYPE_ps | OP_W, ADDRMETH_V | OPTYPE_ps | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "movups", 0, 0, 0),  
( 0, INS_MOV,   ADDRMETH_V | OPTYPE_q | OP_W, ADDRMETH_W | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "movlps", 0, 0, 0),
( 0, INS_MOV,   ADDRMETH_M | OPTYPE_q | OP_W, ADDRMETH_V | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "movlps", 0, 0, 0),
( 0, INS_OTHER, ADDRMETH_V | OPTYPE_ps | OP_W, ADDRMETH_W | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "unpcklps", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_V | OPTYPE_ps | OP_W, ADDRMETH_W | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "unpckhps", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_V | OPTYPE_q | OP_W, ADDRMETH_M | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "movhps", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_M | OPTYPE_q | OP_W, ADDRMETH_V | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "movhps", 0, 0, 0),  
(TBL_0F18, 0, 0, 0, 0, ARG_NONE, cpu_80386, 0, 0, 0, 0),  
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(0, INS_NOP, ADDRMETH_E | OPTYPE_v, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "nop", 0, 0, 0),
(0, INS_NOP, ADDRMETH_E | OPTYPE_v, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "nop", 0, 0, 0),
(0, INS_NOP, ADDRMETH_E | OPTYPE_v, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "nop", 0, 0, 0),
(0, INS_NOP, ADDRMETH_E | OPTYPE_v, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "nop", 0, 0, 0),
# 0f20
( 0, INS_MOV,   ADDRMETH_R | OPTYPE_q | OP_W, ADDRMETH_C | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "mov", 0, 0, 0),
( 0, INS_MOV,   ADDRMETH_R | OPTYPE_q | OP_W, ADDRMETH_D | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "mov", 0, 0, 0),
( 0, INS_MOV,   ADDRMETH_C | OPTYPE_q | OP_W, ADDRMETH_R | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "mov", 0, 0, 0),
( 0, INS_MOV,   ADDRMETH_D | OPTYPE_q | OP_W, ADDRMETH_R | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "mov", 0, 0, 0),
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
( 0, INS_MOV,   ADDRMETH_V | OPTYPE_ps | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "movaps", 0, 0, 0),  
( 0, INS_MOV,   ADDRMETH_W | OPTYPE_ps | OP_W, ADDRMETH_V | OPTYPE_ps | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "movaps", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_V | OPTYPE_ps | OP_R, ADDRMETH_Q | OPTYPE_q  | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "cvtpi2ps", 0, 0, 0),  
( 0, INS_MOV,   ADDRMETH_M | OPTYPE_ps | OP_W, ADDRMETH_V | OPTYPE_ps | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "movntps", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_pi | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "cvttps2pi", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_pi | OP_R, ADDRMETH_W | OPTYPE_ps | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "cvtps2pi", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_W | OPTYPE_ss | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "ucomiss", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_V | OPTYPE_ps | OP_W, ADDRMETH_W | OPTYPE_ps | OP_W, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "comiss", 0, 0, 0),  
# 0f30
( 0, INS_SYSTEM, 0, 0, 0, ARG_NONE, cpu_PENTIUM, "wrmsr", 0, 0, 0),  
( 0, INS_SYSTEM, 0, 0, 0, ARG_NONE, cpu_PENTIUM, "rdtsc", 0, 0, 0),  
( 0, INS_SYSTEM, 0, 0, 0, ARG_NONE, cpu_PENTIUM, "rdmsr", 0, 0, 0),  
( 0, INS_OTHER, 0, 0, 0, ARG_NONE, cpu_PENTPRO, "rdpmc", 0, 0, 0),  
( 0, INS_SYSTEM, 0, 0, 0, ARG_NONE, cpu_PENTIUM2, "sysenter", 0, 0, 0),  
( 0, INS_SYSTEM, 0, 0, 0, ARG_NONE, cpu_PENTIUM2, "sysexit", 0, 0, 0),  
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
(TBL_0F38, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  # 3-byte escape 38
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
(TBL_0F3A, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  # 3-byte escape 3a
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
# 0f40
( 0, INS_MOVCC, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_PENTPRO, "cmovo", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_PENTPRO, "cmovno", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_PENTPRO, "cmovc", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_PENTPRO, "cmovnc", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_PENTPRO, "cmovz", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_PENTPRO, "cmovnz", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_PENTPRO, "cmovbe", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_PENTPRO, "cmova", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_PENTPRO, "cmovs", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_PENTPRO, "cmovns", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_PENTPRO, "cmovpe", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_PENTPRO, "cmovpo", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_PENTPRO, "cmovl", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_PENTPRO, "cmovge", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_PENTPRO, "cmovle", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_PENTPRO, "cmovg", 0, 0, 0),  
# 0f50
( 0, INS_MOV,   ADDRMETH_G | OPTYPE_d  | OP_W, ADDRMETH_U | OPTYPE_x | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "movmskps", 0, 0, 0),
( 0, INS_ARITH, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "sqrtps", 0, 0, 0),
( 0, INS_ARITH, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "rsqrtps", 0, 0, 0),
( 0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "rcpps", 0, 0, 0),
( 0, INS_AND,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "andps", 0, 0, 0),
( 0, INS_AND,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "andnps", 0, 0, 0),
( 0, INS_OR,    ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "orps", 0, 0, 0),
( 0, INS_XOR,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "xorps", 0, 0, 0),
( 0, INS_ADD,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "addps", 0, 0, 0),
( 0, INS_MUL,   ADDRMETH_V | OPTYPE_x | OP_R, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "mulps", 0, 0, 0),
( 0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "cvtps2pd", 0, 0, 0),
( 0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "cvtdq2ps", 0, 0, 0),
( 0, INS_SUB,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "subps", 0, 0, 0),
( 0, INS_ARITH, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "minps", 0, 0, 0),
( 0, INS_DIV,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "divps", 0, 0, 0),
( 0, INS_ARITH, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "maxps", 0, 0, 0),
# 0f60
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_d | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "punpcklbw", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_d | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "punpcklwd", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_d | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "punpckldq", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "packsswb", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "pcmpgtb", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "pcmpgtw", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "pcmpgtd", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "packuswb", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_d | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "punpckhbw", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_d | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "punpckhwd", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_d | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "punpckhdq", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_d | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "packssdw", 0, 0, 0),  
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_P | OPTYPE_d | OP_W, ADDRMETH_E | OPTYPE_d | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "movd", 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "movq", 0, 0, 0),  
# 0f70
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ADDRMETH_I |  OPTYPE_b | OP_R, ARG_NONE, cpu_PENTIUM2, "pshufw", 0, 0, 0),  
(TBL_0F71, 0, 0, 0, 0, ARG_NONE, cpu_PENTMMX, 0, 0, 0, 0),  
(TBL_0F72, 0, 0, 0, 0, ARG_NONE, cpu_PENTMMX, 0, 0, 0, 0),  
(TBL_0F73, 0, 0, 0, 0, ARG_NONE, cpu_PENTMMX, 0, 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "pcmpeqb", 0, 0, 0),  
( 0, INS_CMP, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "pcmpeqw", 0, 0, 0),  
( 0, INS_CMP, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "pcmpeqd", 0, 0, 0),  
( 0, INS_OTHER, 0, 0, 0, ARG_NONE, cpu_PENTMMX, "emms", 0, 0, 0),  
( 0, INS_SYSTEM, ADDRMETH_E | OPTYPE_q | OP_W, ADDRMETH_G | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "vmread", 0, 0, 0),
( 0, INS_SYSTEM, ADDRMETH_G | OPTYPE_q | OP_W, ADDRMETH_E | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "vmwrite", 0, 0, 0),
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_E | OPTYPE_d | OP_W, ADDRMETH_P | OPTYPE_d | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "movd", 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_Q | OPTYPE_q | OP_W, ADDRMETH_P | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "movq", 0, 0, 0),  
# 0f80
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_z | OP_X, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "jo", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_z | OP_X, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "jno", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_z | OP_X, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "jc", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_z | OP_X, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "jnc", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_z | OP_X, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "jz", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_z | OP_X, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "jnz", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_z | OP_X, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "jbe", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_z | OP_X, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "ja", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_z | OP_X, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "js", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_z | OP_X, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "jns", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_z | OP_X, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "jpe", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_z | OP_X, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "jpo", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_z | OP_X, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "jl", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_z | OP_X, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "jge", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_z | OP_X, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "jle", 0, 0, 0),  
( 0, INS_BRANCHCC, ADDRMETH_J | OPTYPE_z | OP_X, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "jg", 0, 0, 0),  
# 0f90
( 0, INS_MOVCC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "seto", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "setno", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "setc", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "setnc", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "setz", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "setnz", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "setbe", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "seta", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "sets", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "setns", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "setpe", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "setpo", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "setl", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "setge", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "setle", 0, 0, 0),  
( 0, INS_MOVCC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "setg", 0, 0, 0),  
# 0fa0
( 0, INS_PUSH, OP_REG | OP_R, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "push", e_amd64_regs.REG_FS, 0, 0),  
( 0, INS_POP, OP_REG | OP_W, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "pop", e_amd64_regs.REG_FS, 0, 0),  
( 0, INS_CPUID, 0, 0, 0, ARG_NONE, cpu_80486, "cpuid", 0, 0, 0),  
( 0, INS_BITTEST, ADDRMETH_E | OPTYPE_v | OP_R, ADDRMETH_G | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "bt", 0, 0, 0),  
( 0, INS_SHL, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_G | OPTYPE_v | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "shld", 0, 0, 0),  
( 0, INS_SHL, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_G | OPTYPE_v | OP_R, OP_R | OP_REG, ARG_NONE, cpu_80386, "shld", 0, 0, e_amd64_regs.REG_CL), 
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
( 0, INS_PUSH, OP_REG | OP_R, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "push", e_amd64_regs.REG_GS, 0, 0),  
( 0, INS_POP, OP_REG | OP_W, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80386, "pop", e_amd64_regs.REG_GS, 0, 0),  
( 0, INS_SYSTEM, 0, 0, 0, ARG_NONE, cpu_80386, "rsm", 0, 0, 0),  
( 0, INS_BITTEST, ADDRMETH_E | OPTYPE_v | OP_R, ADDRMETH_G | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "bts", 0, 0, 0),  
( 0, INS_SHR, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_G | OPTYPE_v | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "shrd", 0, 0, 0),  
( 0, INS_SHR, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_G | OPTYPE_v | OP_R, OP_R | OP_REG, ARG_NONE, cpu_80386, "shrd", 0, 0, e_amd64_regs.REG_CL), 
(TBL_0FAE_00BF, 0, 0, 0, 0, ARG_NONE, cpu_PENTIUM2, 0, 0, 0, 0),  
( 0, INS_MUL, ADDRMETH_G | OPTYPE_v | OP_R, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "imul", 0, 0, 0),  
# 0fb0
( 0, INS_XCHGCC, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_G | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, cpu_80486, "cmpxchg", 0, 0, 0),  
( 0, INS_XCHGCC, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_G | OPTYPE_v | OP_W, ARG_NONE, ARG_NONE, cpu_80486, "cmpxchg", 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_M | OPTYPE_p | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "lss", 0, 0, 0),  
( 0, INS_BITTEST, ADDRMETH_E | OPTYPE_v | OP_R, ADDRMETH_G | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "btr", 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_M | OPTYPE_p| OP_R, ARG_NONE, ARG_NONE, cpu_80386, "lfs", 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_M | OPTYPE_p | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "lgs", 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_b | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "movzx", 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_w | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "movzx", 0, 0, 0),  
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
(0, INS_INVALIDOP, ADDRMETH_R | OPTYPE_d | OP_W, ADDRMETH_E | OPTYPE_d | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "ud1", 0, 0, 0),  #### GROUP 10?
(TBL_0FBA, 0, 0, 0, 0, ARG_NONE, cpu_80386, 0, 0, 0, 0),
( 0, INS_BITTEST, ADDRMETH_E | OPTYPE_v | OP_R, ADDRMETH_G | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "btc", 0, 0, 0),  
( 0, INS_BITTEST, ADDRMETH_G | OPTYPE_v | OP_R | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "bsf", 0, 0, 0),  
( 0, INS_BITTEST, ADDRMETH_G | OPTYPE_v | OP_R | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "bsr", 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_b | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "movsx", 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_w | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "movsx", 0, 0, 0),  
# 0fc0
( 0, INS_ADD, ADDRMETH_E | OPTYPE_b | OP_W, ADDRMETH_G | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, cpu_80486, "xadd", 0, 0, 0),  
( 0, INS_ADD, ADDRMETH_E | OPTYPE_v | OP_W, ADDRMETH_G | OPTYPE_v, ARG_NONE, ARG_NONE, cpu_80486, "xadd", 0, 0, 0),  
( 0, INS_CMP, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x| OP_W, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTIUM2, "cmpps", 0, 0, 0),
( 0, INS_MOV, ADDRMETH_M | OPTYPE_q | OP_W, ADDRMETH_G | OPTYPE_q |OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "movnti", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_E | OPTYPE_w | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTIUM2, "pinsrw", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_G | OPTYPE_q | OP_W, ADDRMETH_N | OPTYPE_q | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTIUM2, "pextrw", 0, 0, 0),
( 0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTIUM2, "shufps", 0, 0, 0),
(TBL_0FC7_00BF, 0, 0, 0, 0, ARG_NONE, cpu_PENTMMX, 0, 0, 0, 0),  # group 9
( 0, INS_XCHG, OP_REG | OP_W, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80486, "bswap", e_amd64_regs.REG_EAX, 0, 0),  
( 0, INS_XCHG, OP_REG | OP_W, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80486, "bswap", e_amd64_regs.REG_ECX, 0, 0),  
( 0, INS_XCHG, OP_REG | OP_W, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80486, "bswap", e_amd64_regs.REG_EDX, 0, 0),  
( 0, INS_XCHG, OP_REG | OP_W, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80486, "bswap", e_amd64_regs.REG_EBX, 0, 0),  
( 0, INS_XCHG, OP_REG | OP_W, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80486, "bswap", e_amd64_regs.REG_ESP, 0, 0),  
( 0, INS_XCHG, OP_REG | OP_W, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80486, "bswap", e_amd64_regs.REG_EBP, 0, 0),  
( 0, INS_XCHG, OP_REG | OP_W, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80486, "bswap", e_amd64_regs.REG_ESI, 0, 0),  
( 0, INS_XCHG, OP_REG | OP_W, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80486, "bswap", e_amd64_regs.REG_EDI, 0, 0),  
# 0fd0
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "psrlw", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "psrld", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "psrlq", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "paddq", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "pmullw", 0, 0, 0),  
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_G | OPTYPE_d | OP_W, ADDRMETH_N | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "pmovmskb", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "psubusb", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "psubusw", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "pminub", 0, 0, 0),  
( 0, INS_AND, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "pand", 0, 0, 0),  
( 0, INS_ADD, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "paddusb", 0, 0, 0),  
( 0, INS_ADD, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "paddusw", 0, 0, 0),  
( 0, INS_ARITH, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "pmaxub", 0, 0, 0),  
( 0, INS_AND, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "pandn", 0, 0, 0),  
# 0fe0
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "pavgb", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "psraw", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "psrad", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "pavgw", 0, 0, 0),  
( 0, INS_MUL, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "pmulhuw", 0, 0, 0),  
( 0, INS_MUL, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "pmulhw", 0, 0, 0),  
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_M | OPTYPE_dq | OP_W, ADDRMETH_V | OPTYPE_dq | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "movntq", 0, 0, 0),  
( 0, INS_SUB, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "psubsb", 0, 0, 0),  
( 0, INS_SUB, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "psubsw", 0, 0, 0),  
( 0, INS_ARITH, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "pminsw", 0, 0, 0),  
( 0, INS_OR, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "por", 0, 0, 0),  
( 0, INS_ADD, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "paddsb", 0, 0, 0),  
( 0, INS_ADD, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "paddsw", 0, 0, 0),  
( 0, INS_ARITH, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "pmaxsw", 0, 0, 0),  
( 0, INS_XOR, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "pxor", 0, 0, 0),  
# 0ff0
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "psllw", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "pslld", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "psllq", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "pmuludq", 0, 0, 0),
# TODO: so...uhhh, slight problem. in VEX mode, bzhi resolves to here (0FF5) instead of pmaddwd
( 0, INS_ADD, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "pmaddwd", 0, 0, 0),  
( 0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "psadbw", 0, 0, 0),  
( 0, INS_MOV, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_N | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "maskmovq", 0, 0, 0),  
( 0, INS_SUB, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "psubb", 0, 0, 0),  
( 0, INS_SUB, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "psubw", 0, 0, 0),  
( 0, INS_SUB, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "psubd", 0, 0, 0),  
( 0, INS_SUB, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "psubq", 0, 0, 0),  
( 0, INS_ADD, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "paddb", 0, 0, 0),  
( 0, INS_ADD, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "paddw", 0, 0, 0),  
( 0, INS_ADD, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "paddd", 0, 0, 0),
(0, INS_INVALIDOP, ADDRMETH_R | OPTYPE_d | OP_W, ADDRMETH_E | OPTYPE_d | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "ud0", 0, 0, 0),
]
desc_0F         = (tbl32_0F,4,0,0xff,0,0xff)

# linkage

"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_660F = [(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0) for x in range(256)]
tbl32_660F[0x10] = (0, INS_MOV,     ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "movupd", 0, 0, 0)
tbl32_660F[0x11] = (0, INS_MOV,     ADDRMETH_W | OPTYPE_x | OP_W, ADDRMETH_V | OPTYPE_x | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "movupd", 0, 0, 0)
tbl32_660F[0x12] = (0, INS_MOV,     ADDRMETH_V | OPTYPE_q | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_M | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "movlpd", 0, 0, 0)
tbl32_660F[0x13] = (0, INS_MOV,     ADDRMETH_M | OPTYPE_q | OP_W, ADDRMETH_V | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "movlpd", 0, 0, 0)
tbl32_660F[0x14] = (0, INS_OTHER,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "unpcklpd", 0, 0, 0)
tbl32_660F[0x15] = (0, INS_OTHER,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "unpckhpd", 0, 0, 0)
tbl32_660F[0x16] = (0, INS_OTHER,   ADDRMETH_V | OPTYPE_q | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_M | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "movhpd", 0, 0, 0)
tbl32_660F[0x17] = (0, INS_OTHER,   ADDRMETH_M | OPTYPE_q | OP_W, ADDRMETH_V | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "movhpd", 0, 0, 0)

tbl32_660F[0x28] = (0, INS_MOV,     ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "movapd", 0, 0, 0)
tbl32_660F[0x29] = (0, INS_MOV,     ADDRMETH_W | OPTYPE_x | OP_W, ADDRMETH_V | OPTYPE_x | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "movapd", 0, 0, 0)
tbl32_660F[0x2a] = (0, INS_OTHER,   ADDRMETH_V | OPTYPE_pd | OP_W, ADDRMETH_Q | OPTYPE_pi | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "cvtpi2pd", 0, 0, 0)
tbl32_660F[0x2b] = (0, INS_MOV,     ADDRMETH_M | OPTYPE_x | OP_W, ADDRMETH_V | OPTYPE_x | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "movntpd", 0, 0, 0)
tbl32_660F[0x2c] = (0, INS_OTHER,   ADDRMETH_P | OPTYPE_pi | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "cvttpd2pi", 0, 0, 0)
tbl32_660F[0x2d] = (0, INS_OTHER,   ADDRMETH_P | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "cvtpd2pi", 0, 0, 0)
tbl32_660F[0x2e] = (0, INS_OTHER,   ADDRMETH_V | OPTYPE_sd | OP_W, ADDRMETH_W | OPTYPE_sd | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "ucomisd", 0, 0, 0)
tbl32_660F[0x2f] = (0, INS_OTHER,   ADDRMETH_V | OPTYPE_sd | OP_W, ADDRMETH_W | OPTYPE_sd | OP_W, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "comisd", 0, 0, 0)
tbl32_660F[0x38] = (TBL_660F38, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
tbl32_660F[0x3a] = (TBL_660F3A, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

tbl32_660F[0x50] = (0, INS_MOV,     ADDRMETH_G | OPTYPE_y | OP_W, ADDRMETH_U | OPTYPE_pd | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "movmskpd", 0, 0, 0)
tbl32_660F[0x51] = (0, INS_ARITH,   ADDRMETH_V | OPTYPE_pd | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "sqrtpd", 0, 0, 0)
# XXX: In an interesting case of asymmetry, neither of these are a thing. Nasm refuses to assemble them, that are no refs in the manual for them,
# nothing
#tbl32_660F[0x52] = (0, INS_ARITH,   ADDRMETH_V | OPTYPE_pd | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "rsqrtpd", 0, 0, 0)
#tbl32_660F[0x53] = (0, INS_OTHER,   ADDRMETH_V | OPTYPE_pd | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "rcppd", 0, 0, 0)

tbl32_660F[0x54] = (0, INS_AND,     ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "andpd", 0, 0, 0)
tbl32_660F[0x55] = (0, INS_AND,     ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "andnpd", 0, 0, 0)
tbl32_660F[0x56] = (0, INS_OR,      ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "orpd", 0, 0, 0)
tbl32_660F[0x57] = (0, INS_XOR,     ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "xorpd", 0, 0, 0)
tbl32_660F[0x58] = (0, INS_ADD,     ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "addpd", 0, 0, 0)
tbl32_660F[0x59] = (0, INS_MUL,     ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "mulpd", 0, 0, 0)
tbl32_660F[0x5a] = (0, INS_OTHER,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, ARG_NONE, cpu_AMD64, "cvtpd2ps", 0, 0, 0)
tbl32_660F[0x5b] = (0, INS_MOV,     ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, ARG_NONE, cpu_AMD64, "cvtps2dq", 0, 0, 0)
tbl32_660F[0x5c] = (0, INS_SUB,     ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "subpd", 0, 0, 0)
tbl32_660F[0x5d] = (0, INS_ARITH,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "minpd", 0, 0, 0)
tbl32_660F[0x5e] = (0, INS_DIV,     ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "divpd", 0, 0, 0)
tbl32_660F[0x5f] = (0, INS_ARITH,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "maxpd", 0, 0, 0)

tbl32_660F[0x60] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "punpcklbw", 0, 0, 0)
tbl32_660F[0x61] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "punpcklwd", 0, 0, 0)
tbl32_660F[0x62] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "punpckldq", 0, 0, 0)
tbl32_660F[0x63] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "packsswb", 0, 0, 0)
tbl32_660F[0x64] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "pcmpgtb", 0, 0, 0)
tbl32_660F[0x65] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "pcmpgtw", 0, 0, 0)
tbl32_660F[0x66] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "pcmpgtd", 0, 0, 0)
tbl32_660F[0x67] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "packuswb", 0, 0, 0)
tbl32_660F[0x68] = (0, INS_OTHER, ADDRMETH_P | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "punpckhbw", 0, 0, 0)
tbl32_660F[0x69] = (0, INS_OTHER, ADDRMETH_P | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "punpckhwd", 0, 0, 0)
tbl32_660F[0x6a] = (0, INS_OTHER, ADDRMETH_P | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "punpckhdq", 0, 0, 0)
tbl32_660F[0x6b] = (0, INS_OTHER, ADDRMETH_P | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "packssdw", 0, 0, 0)
tbl32_660F[0x6c] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "punpcklqdq", 0, 0, 0)
tbl32_660F[0x6d] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "punpckhqdq", 0, 0, 0)

tbl32_660F[0x6e] = (0, INS_MOV,   ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_E | OPTYPE_dq | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "movd_q", 0, 0, 0)  #     FIXME: HORKED - VEX.W/REX.W sets D or Q
tbl32_660F[0x6f] = (0, INS_MOV,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_E | OPTYPE_x | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "movdqa", 0, 0, 0)

tbl32_660F[0x70] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ADDRMETH_I |  OPTYPE_b | OP_R,  ARG_NONE,cpu_PENTIUM2, "pshufd", 0, 0, 0)
tbl32_660F[0x71] = (TBL_660F71, 0, 0, 0, 0, ARG_NONE, cpu_PENTMMX, 0, 0, 0, 0)  # FIXME: << grp 12
tbl32_660F[0x72] = (TBL_660F72, 0, 0, 0, 0, ARG_NONE, cpu_PENTMMX, 0, 0, 0, 0)  # FIXME: << grp 13
tbl32_660F[0x73] = (TBL_660F73, 0, 0, 0, 0, ARG_NONE, cpu_PENTMMX, 0, 0, 0, 0)  # 66 0f 73
tbl32_660F[0x74] = (0, INS_CMP, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "pcmpeqb", 0, 0, 0)
tbl32_660F[0x75] = (0, INS_CMP, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "pcmpeqw", 0, 0, 0)
tbl32_660F[0x76] = (0, INS_CMP, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "pcmpeqd", 0, 0, 0)
tbl32_660F[0x7c] = (0, INS_MOV, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "haddpd", 0, 0, 0)
tbl32_660F[0x7d] = (0, INS_MOV, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "hsubpd", 0, 0, 0)
tbl32_660F[0x7e] = (0, INS_MOV, ADDRMETH_E | OPTYPE_y  | OP_W, ADDRMETH_V | OPTYPE_y | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "movd", 0, 0, 0)
tbl32_660F[0x7f] = (0, INS_MOV, ADDRMETH_W | OPTYPE_x  | OP_W, ADDRMETH_V | OPTYPE_x | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "movq", 0, 0, 0)

tbl32_660F[0xc2] = ( 0, INS_CMP,   ADDRMETH_V | OPTYPE_pd | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_pd | OP_R, ADDRMETH_W | OPTYPE_pd| OP_W, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTIUM2, "cmppd", 0, 0, 0)
tbl32_660F[0xc4] = ( 0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_pd | OP_R, ADDRMETH_E | OPTYPE_w | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTIUM2, "pinsrw", 0, 0, 0)
tbl32_660F[0xc5] = ( 0, INS_OTHER, ADDRMETH_G | OPTYPE_q | OP_W, ADDRMETH_U | OPTYPE_dq | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTIUM2, "pextrw", 0, 0, 0)
tbl32_660F[0xc6] = ( 0, INS_OTHER, ADDRMETH_V | OPTYPE_pd | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_pd | OP_R, ADDRMETH_W | OPTYPE_pd | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTIUM2, "shufps", 0, 0, 0)
tbl32_660F[0xc7] = (TBL_660FC7_00BF, 0, 0, 0, 0, ARG_NONE, cpu_PENTMMX, 0, 0, 0, 0)

tbl32_660F[0xd0] = (0, INS_ADD,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "addsubpd", 0, 0, 0)
tbl32_660F[0xd1] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "psrlw", 0, 0, 0)
tbl32_660F[0xd2] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_dq | OP_R | OP_NOVEXL, ARG_NONE, cpu_PENTMMX, "psrld", 0, 0, 0)
tbl32_660F[0xd3] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_dq | OP_R | OP_NOVEXL, ARG_NONE, cpu_PENTMMX, "psrlq", 0, 0, 0)
tbl32_660F[0xd4] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "paddq", 0, 0, 0)
tbl32_660F[0xd5] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "pmullw", 0, 0, 0)
tbl32_660F[0xd6] = (0, INS_OTHER, ADDRMETH_W | OPTYPE_q | OP_W, ADDRMETH_V | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "movq", 0, 0, 0)
tbl32_660F[0xd7] = (0, INS_OTHER, ADDRMETH_G | OPTYPE_d | OP_W, ADDRMETH_U | OPTYPE_x | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "pmovmskb", 0, 0, 0)
tbl32_660F[0xd8] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "psubusb", 0, 0, 0)
tbl32_660F[0xd9] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "psubusw", 0, 0, 0)
tbl32_660F[0xda] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "pminub", 0, 0, 0)
tbl32_660F[0xdb] = (0, INS_AND,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX,  "pand", 0, 0, 0)
tbl32_660F[0xdc] = (0, INS_ADD,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX,  "paddusb", 0, 0, 0)
tbl32_660F[0xdd] = (0, INS_ADD,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX,  "paddusw", 0, 0, 0)
tbl32_660F[0xde] = (0, INS_ARITH, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "pmaxub", 0, 0, 0)
tbl32_660F[0xdf] = (0, INS_AND,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX,  "pandn", 0, 0, 0)
tbl32_660F[0xe0] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "pavgb", 0, 0, 0)
tbl32_660F[0xe1] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R | OP_NOVEXL, ARG_NONE, cpu_PENTMMX,  "psraw", 0, 0, 0)
tbl32_660F[0xe2] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R | OP_NOVEXL, ARG_NONE, cpu_PENTMMX,  "psrad", 0, 0, 0)
tbl32_660F[0xe3] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "pavgw", 0, 0, 0)
tbl32_660F[0xe4] = (0, INS_MUL,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "pmulhuw", 0, 0, 0)
tbl32_660F[0xe5] = (0, INS_MUL,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX,  "pmulhw", 0, 0, 0)
tbl32_660F[0xe6] = (0, INS_MUL,   ADDRMETH_V | OPTYPE_dq | OP_W | OP_NOVEXL, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX,  "cvttpd2dq", 0, 0, 0)
tbl32_660F[0xe7] = (0, INS_MOV,   ADDRMETH_M | OPTYPE_dq | OP_W, ADDRMETH_V | OPTYPE_dq | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "movntdq", 0, 0, 0)
tbl32_660F[0xe8] = (0, INS_SUB,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX,  "psubsb", 0, 0, 0)
tbl32_660F[0xe9] = (0, INS_SUB,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX,  "psubsw", 0, 0, 0)
tbl32_660F[0xea] = (0, INS_ARITH, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "pminsw", 0, 0, 0)
tbl32_660F[0xeb] = (0, INS_OR,    ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX,  "por", 0, 0, 0)
tbl32_660F[0xec] = (0, INS_ADD,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX,  "paddsb", 0, 0, 0)
tbl32_660F[0xed] = (0, INS_ADD,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX,  "paddsw", 0, 0, 0)
tbl32_660F[0xee] = (0, INS_ARITH, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "pmaxsw", 0, 0, 0)
tbl32_660F[0xef] = (0, INS_XOR,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX,  "pxor", 0, 0, 0)
tbl32_660F[0xf1] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R | OP_NOVEXL, ARG_NONE, cpu_PENTMMX, "psllw", 0, 0, 0)
tbl32_660F[0xf2] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R | OP_NOVEXL, ARG_NONE, cpu_PENTMMX, "pslld", 0, 0, 0)
tbl32_660F[0xf3] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R | OP_NOVEXL, ARG_NONE, cpu_PENTMMX, "psllq", 0, 0, 0)
tbl32_660F[0xf4] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "pmuludq", 0, 0, 0)
tbl32_660F[0xf5] = (0, INS_ADD,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "pmaddwd", 0, 0, 0)
tbl32_660F[0xf6] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTIUM2, "psadbw", 0, 0, 0)
tbl32_660F[0xf8] = (0, INS_SUB,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "psubb", 0, 0, 0)
tbl32_660F[0xf9] = (0, INS_SUB,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "psubw", 0, 0, 0)
tbl32_660F[0xfa] = (0, INS_SUB,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "psubd", 0, 0, 0)
tbl32_660F[0xfb] = (0, INS_SUB,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "psubq", 0, 0, 0)
tbl32_660F[0xfc] = (0, INS_ADD,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "paddb", 0, 0, 0)
tbl32_660F[0xfd] = (0, INS_ADD,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "paddw", 0, 0, 0)
tbl32_660F[0xfe] = (0, INS_ADD,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_PENTMMX, "paddd", 0, 0, 0)


tbl32_F20F = [(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0) for x in range(256)]
tbl32_F20F[0x10] = (0, INS_MOV, ADDRMETH_V | OPTYPE_sd | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_VEXH | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_sd | OP_MEM_Q | OP_R, ARG_NONE, cpu_PENTIUM2, "movsd", 0, 0, 0)
tbl32_F20F[0x11] = (0, INS_MOV, ADDRMETH_W | OPTYPE_sd | OP_MEM_Q | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_VEXH | OPTYPE_x | OP_R, ADDRMETH_V | OPTYPE_sd | OP_R, ARG_NONE, cpu_PENTIUM2, "movsd", 0, 0, 0)
tbl32_F20F[0x12] = (0, INS_MOV, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "movddup", 0, 0, 0)
tbl32_F20F[0x2a] = (0, INS_OTHER,   ADDRMETH_V | OPTYPE_sd | OP_R, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_sd | OP_R, ADDRMETH_E | OPTYPE_y | OP_R, ARG_NONE, cpu_PENTIUM2, "cvtsi2sd", 0, 0, 0)
tbl32_F20F[0x2c] = (0, INS_OTHER,   ADDRMETH_G | OPTYPE_y | OP_R, ADDRMETH_W | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "cvttsd2si", 0, 0, 0)
tbl32_F20F[0x2d] = (0, INS_OTHER,   ADDRMETH_G | OPTYPE_y | OP_R, ADDRMETH_W | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "cvtsd2si", 0, 0, 0)
tbl32_F20F[0x38] = (TBL_F20F38, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
tbl32_F20F[0x3a] = (TBL_F20F3A, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
tbl32_F20F[0x51] = (0, INS_ARITH,   ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_ss | OP_R, ADDRMETH_W | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "sqrtsd", 0, 0, 0)
tbl32_F20F[0x58] = (0, INS_ADD,     ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_ss | OP_R, ADDRMETH_W | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "addsd", 0, 0, 0)
tbl32_F20F[0x59] = (0, INS_MUL,     ADDRMETH_V | OPTYPE_ss | OP_R, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_ss | OP_R, ADDRMETH_W | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "mulsd", 0, 0, 0)
tbl32_F20F[0x5a] = (0, INS_OTHER,   ADDRMETH_V | OPTYPE_ss | OP_R, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x  | OP_R, ADDRMETH_W | OPTYPE_q | OP_R, ARG_NONE, cpu_AMD64, "cvtsd2ss", 0, 0, 0)
tbl32_F20F[0x5c] = (0, INS_SUB,     ADDRMETH_V | OPTYPE_sd | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_sd | OP_R, ADDRMETH_W | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "subsd", 0, 0, 0)
tbl32_F20F[0x5d] = (0, INS_ARITH,   ADDRMETH_V | OPTYPE_sd | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_sd | OP_R, ADDRMETH_W | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "minsd", 0, 0, 0)
tbl32_F20F[0x5e] = (0, INS_DIV,     ADDRMETH_V | OPTYPE_sd | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_sd | OP_R, ADDRMETH_W | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "divsd", 0, 0, 0)
tbl32_F20F[0x5f] = (0, INS_ARITH,   ADDRMETH_V | OPTYPE_sd | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_sd | OP_R, ADDRMETH_W | OPTYPE_q | OP_R, ARG_NONE, cpu_PENTIUM2, "maxsd", 0, 0, 0)
tbl32_F20F[0x70] = (0, INS_OTHER,   ADDRMETH_V | OPTYPE_x  | OP_W, ADDRMETH_W | OPTYPE_x  | OP_R, ADDRMETH_I |  OPTYPE_b | OP_R, ARG_NONE, cpu_PENTIUM2, "pshuflw", 0, 0, 0)
tbl32_F20F[0x7c] = (0, INS_MOV,     ADDRMETH_V | OPTYPE_ps | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_ps | OP_R, ADDRMETH_W | OPTYPE_ps | OP_R, ARG_NONE, cpu_PENTMMX, "haddps", 0, 0, 0)
tbl32_F20F[0x7d] = (0, INS_MOV,     ADDRMETH_V | OPTYPE_ps | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_ps | OP_R, ADDRMETH_W | OPTYPE_ps | OP_R, ARG_NONE, cpu_PENTMMX, "hsubps", 0, 0, 0)
tbl32_F20F[0xc2] = (0, INS_CMP,     ADDRMETH_V | OPTYPE_sd | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_sd | OP_R, ADDRMETH_W | OPTYPE_sd | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTIUM2, "cmpsd", 0, 0, 0)
tbl32_F20F[0xd0] = (0, INS_ADD,     ADDRMETH_V | OPTYPE_ps | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_ps | OP_R, ADDRMETH_W | OPTYPE_ps | OP_R, ARG_NONE, cpu_PENTMMX, "addsubps", 0, 0, 0)
tbl32_F20F[0xd6] = (0, INS_OTHER,   ADDRMETH_P | OPTYPE_q  | OP_W, ADDRMETH_U | OPTYPE_q | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "movdq2q", 0, 0, 0)
tbl32_F20F[0xe6] = (0, INS_MUL,     ADDRMETH_V | OPTYPE_dq | OP_NOVEXL | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "cvtpd2dq", 0, 0, 0)
tbl32_F20F[0xf0] = (0, INS_OTHER,   ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_M | OPTYPE_x | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "lddqu", 0, 0, 0)

tbl32_F30F = [(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, ARG_NONE, 0, 0, 0, 0, 0) for x in range(256)]
tbl32_F30F[0x10] = (0, INS_MOV, ADDRMETH_V | OPTYPE_x  | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_VEXH | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_ds | OP_R, ARG_NONE, cpu_PENTIUM2, "movss", 0, 0, 0)
tbl32_F30F[0x11] = (0, INS_MOV, ADDRMETH_W | OPTYPE_ds | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_VEXH | OPTYPE_x | OP_R, ADDRMETH_V | OPTYPE_ss | OP_R, ARG_NONE, cpu_PENTIUM2, "movss", 0, 0, 0)
tbl32_F30F[0x12] = (0, INS_MOV, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "movsldup", 0, 0, 0)
tbl32_F30F[0x16] = (0, INS_MOV, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "movshdup", 0, 0, 0)
tbl32_F30F[0x2a] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_ss | OP_R, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_ss | OP_R, ADDRMETH_E | OPTYPE_y  | OP_R, ARG_NONE, cpu_PENTIUM2, "cvtsi2ss", 0, 0, 0)
tbl32_F30F[0x2c] = (0, INS_OTHER, ADDRMETH_G | OPTYPE_y | OP_R, ADDRMETH_W | OPTYPE_ds | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "cvttss2si", 0, 0, 0)
tbl32_F30F[0x2d] = (0, INS_OTHER,ADDRMETH_G | OPTYPE_y | OP_R, ADDRMETH_W | OPTYPE_ds | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "cvtss2si", 0, 0, 0)
tbl32_F30F[0x38] = (TBL_F30F38, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
tbl32_F30F[0x51] = (0, INS_ARITH,   ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_ss | OP_R, ADDRMETH_W | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTIUM2, "sqrtss", 0, 0, 0)
tbl32_F30F[0x52] = (0, INS_ARITH,   ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_ss | OP_R, ADDRMETH_W | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTIUM2, "rsqrtss", 0, 0, 0)
tbl32_F30F[0x53] = (0, INS_OTHER,   ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_ss | OP_R, ADDRMETH_W | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTIUM2, "rcpss", 0, 0, 0)
tbl32_F30F[0x58] = (0, INS_ADD,     ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_ss | OP_R, ADDRMETH_W | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTIUM2, "addss", 0, 0, 0)
tbl32_F30F[0x59] = (0, INS_MUL,     ADDRMETH_V | OPTYPE_ss | OP_R, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_ss | OP_R, ADDRMETH_W | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTIUM2, "mulss", 0, 0, 0)
tbl32_F30F[0x5a] = (0, INS_OTHER,   ADDRMETH_V | OPTYPE_sd | OP_R, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x  | OP_R, ADDRMETH_W | OPTYPE_d | OP_R, ARG_NONE, cpu_AMD64, "cvtss2sd", 0, 0, 0)
tbl32_F30F[0x5b] = (0, INS_OTHER,   ADDRMETH_V | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, ARG_NONE, cpu_AMD64, "cvttps2dq", 0, 0, 0)
tbl32_F30F[0x5c] = (0, INS_SUB,     ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_ss | OP_R, ADDRMETH_W | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTIUM2, "subss", 0, 0, 0)
tbl32_F30F[0x5d] = (0, INS_ARITH,   ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_ss | OP_R, ADDRMETH_W | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTIUM2, "minss", 0, 0, 0)
tbl32_F30F[0x5e] = (0, INS_DIV,     ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_ss | OP_R, ADDRMETH_W | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTIUM2, "divss", 0, 0, 0)
tbl32_F30F[0x5f] = (0, INS_ARITH,   ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_ss | OP_R, ADDRMETH_W | OPTYPE_d | OP_R, ARG_NONE, cpu_PENTIUM2, "maxss", 0, 0, 0)
tbl32_F30F[0x6f] = (0, INS_MOV,     ADDRMETH_V | OPTYPE_x  | OP_W, ADDRMETH_W | OPTYPE_x  | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "movdqu", 0, 0, 0)
tbl32_F30F[0x70] = (0, INS_OTHER,   ADDRMETH_V | OPTYPE_x  | OP_W, ADDRMETH_W | OPTYPE_x  | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTIUM2, "pshufhw", 0, 0, 0)
tbl32_F30F[0x7e] = (0, INS_MOV,     ADDRMETH_V | OPTYPE_q  | OP_W, ADDRMETH_W | OPTYPE_q  | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "movd_q", 0, 0, 0) # HORKED!
tbl32_F30F[0x7f] = (0, INS_MOV,     ADDRMETH_W | OPTYPE_x  | OP_W, ADDRMETH_V | OPTYPE_x  | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "movdqu", 0, 0, 0)
tbl32_F30F[0xae] = (TBL_F30FAE_00BF, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
tbl32_F30F[0xb8] = (0, INS_BITTEST, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "popcnt", 0, 0, 0)
tbl32_F30F[0xbd] = (0, INS_BITTEST, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "lzcnt", 0, 0, 0)
tbl32_F30F[0xc2] = (0, INS_CMP,     ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTIUM2, "cmpss", 0, 0, 0)
tbl32_F30F[0xc7] = (TBL_F30FC7_00BF, 0, 0, 0, 0, ARG_NONE, cpu_PENTMMX, 0, 0, 0, 0)  # group 9
tbl32_F30F[0xd6] = (0, INS_OTHER,   ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_N | OPTYPE_q  | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "movq2dq", 0, 0, 0)
# TODO: Memory is a different size here than the reg
tbl32_F30F[0xe6] = (0, INS_OTHER,   ADDRMETH_V | OPTYPE_x  | OP_W, ADDRMETH_W | OPTYPE_pd | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "cvtdq2pd", 0, 0, 0)

desc_660F         = (tbl32_660F,4,0,0xff,0,0xff)
desc_F20F         = (tbl32_F20F,4,0,0xff,0,0xff)
desc_F30F         = (tbl32_F30F,4,0,0xff,0,0xff)
######################################### END 0F ##############################


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""

tbl32_0F00 = [
( 0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "sldt", 0, 0, 0),  
( 0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "str", 0, 0, 0),  
( 0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "lldt", 0, 0, 0),  
( 0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "ltr", 0, 0, 0),  
( 0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "verr", 0, 0, 0),  
( 0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "verw", 0, 0, 0),  
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
]
desc_0F00       = (tbl32_0F00,3,3,0x07,0,0xff)


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""

tbl32_0F01_00BF = [
( 0, INS_SYSTEM, ADDRMETH_M | OPTYPE_s | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "sgdt", 0, 0, 0),  
( 0, INS_SYSTEM, ADDRMETH_M | OPTYPE_s | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "sidt", 0, 0, 0),  
( 0, INS_SYSTEM, ADDRMETH_M | OPTYPE_s | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "lgdt", 0, 0, 0),  
( 0, INS_SYSTEM, ADDRMETH_M | OPTYPE_s | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "lidt", 0, 0, 0),  
( 0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "smsw", 0, 0, 0),  
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
( 0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "lmsw", 0, 0, 0),  
( 0, INS_SYSTEM, ADDRMETH_M | OPTYPE_b | OP_R, ARG_NONE, ARG_NONE, cpu_80486, "invlpg", 0, 0, 0),
]

tbl32_0F01_rest = [
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
( 0, INS_SYSTEM, 0, 0, 0, cpu_PENTIUM2, "vmcall", 0, 0, 0),  
( 0, INS_SYSTEM, 0, 0, 0, cpu_PENTIUM2, "vmlaunch", 0, 0, 0),  
( 0, INS_SYSTEM, 0, 0, 0, cpu_PENTIUM2, "vmresume", 0, 0, 0),  
( 0, INS_SYSTEM, 0, 0, 0, cpu_PENTIUM2, "vmxoff", 0, 0, 0),  
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
( 0, INS_SYSTEM, 0, 0, 0, cpu_PENTIUM2, "monitor", 0, 0, 0),
( 0, INS_SYSTEM, 0, 0, 0, cpu_PENTIUM2, "mwait", 0, 0, 0),
( 0, INS_SYSTEM, 0, 0, 0, cpu_PENTIUM2, "clac", 0, 0, 0),
( 0, INS_SETAF, ARG_NONE, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "stac", 0, 0, 0),
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
( 0, INS_SYSTEM, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_AMD64, "xgetbv", e_amd64_regs.REG_ECX, 0, 0),
( 0, INS_SYSTEM, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_AMD64, "xsetbv", e_amd64_regs.REG_ECX, 0, 0),
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
( 0, INS_SYSTEM, ARG_NONE, ARG_NONE, ARG_NONE, cpu_AMD64, "vmfunc", 0, 0, 0),
( 0, INS_SYSTEM, ARG_NONE, ARG_NONE, ARG_NONE, cpu_PENTIUM, "xend", 0, 0, 0),
( 0, INS_SYSTEM, ARG_NONE, ARG_NONE, ARG_NONE, cpu_PENTIUM, "xtest", 0, 0, 0),
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
( 0, INS_SYSTEM, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_AMD64, "vmrun", e_amd64_regs.REG_RAX, 0, 0),  
( 0, INS_SYSTEM, 0, 0, 0, cpu_AMD64, "vmmcall", 0, 0, 0),  
( 0, INS_SYSTEM, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_AMD64, "vmload", e_amd64_regs.REG_RAX, 0, 0),  
( 0, INS_SYSTEM, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_AMD64, "vmsave", e_amd64_regs.REG_RAX, 0, 0),  
( 0, INS_SYSTEM, 0, 0, 0, cpu_AMD64, "stgi", 0, 0, 0),  
( 0, INS_SYSTEM, 0, 0, 0, cpu_AMD64, "clgi", 0, 0, 0),  
( 0, INS_SYSTEM, OP_REG | OP_R, ARG_NONE, ARG_NONE, cpu_AMD64, "skinit", e_amd64_regs.REG_EAX, 0, 0),  
( 0, INS_SYSTEM, 0, 0, 0, cpu_AMD64, "invlpga", 0, 0, 0),  
( 0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "smsw", 0, 0, 0),  
( 0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "smsw", 0, 0, 0),  
( 0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "smsw", 0, 0, 0),  
( 0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "smsw", 0, 0, 0),  
( 0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "smsw", 0, 0, 0),  
( 0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "smsw", 0, 0, 0),  
( 0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "smsw", 0, 0, 0),  
( 0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "smsw", 0, 0, 0),  
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
( 0, INS_SYSTEM, ARG_NONE, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "rdpkru", 0, 0, 0),
( 0, INS_SYSTEM, ARG_NONE, ARG_NONE, ARG_NONE, cpu_OSPKE, "wrpkru", 0, 0, 0),
( 0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "lmsw", 0, 0, 0),  
( 0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "lmsw", 0, 0, 0),  
( 0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "lmsw", 0, 0, 0),  
( 0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "lmsw", 0, 0, 0),  
( 0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "lmsw", 0, 0, 0),  
( 0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "lmsw", 0, 0, 0),  
( 0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "lmsw", 0, 0, 0),  
( 0, INS_SYSTEM, ADDRMETH_E | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "lmsw", 0, 0, 0),  
( 0, INS_OTHER, 0, 0, 0, cpu_PENTIUM2, "swapgs", 0, 0, 0),
(0, INS_SYSTEM, ARG_NONE, ARG_NONE, ARG_NONE, cpu_PENTIUM, "rdtscp", 0, 0, 0),
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
]
desc_0F01_00BF  = (tbl32_0F01_00BF,3,3,0x07,0,0xbf, TBL_0F01_rest)
desc_0F01_rest  = (tbl32_0F01_rest,3,0,0xff,0xc0,0xff)


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_0F18 = [
( 0, INS_SYSTEM, OPTYPE_b | OP_R | ADDRMETH_M, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "prefetchnta", 0, 0, 0),
( 0, INS_SYSTEM, OPTYPE_b | OP_R | ADDRMETH_M, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "prefetch0", 0, 0, 0),
( 0, INS_SYSTEM, OPTYPE_b | OP_R | ADDRMETH_M, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "prefetch1", 0, 0, 0),
( 0, INS_SYSTEM, OPTYPE_b | OP_R | ADDRMETH_M, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "prefetch2", 0, 0, 0),
#( 0, INS_SYSTEM, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "prefetch", e_amd64_regs.REG_TEST0, 0, 0),
#( 0, INS_SYSTEM, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "prefetch", e_amd64_regs.REG_TEST1, 0, 0),
#( 0, INS_SYSTEM, OP_REG | OP_W, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "prefetch", e_amd64_regs.REG_TEST2, 0, 0),
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0   ) ,
]
desc_0F18       = (tbl32_0F18,3,3,0x07,0,0xff)


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

tbl32_0F38[0x1c] = (0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_AMD64, "pabsb", 0, 0, 0)
tbl32_0F38[0x1d] = (0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_AMD64, "pabsw", 0, 0, 0)
tbl32_0F38[0x1e] = (0, INS_OTHER, ADDRMETH_P | OPTYPE_q | OP_W, ADDRMETH_Q | OPTYPE_q | OP_R, ARG_NONE, cpu_AMD64, "pabsd", 0, 0, 0)

tbl32_0F38[0xC8] = (0, INS_CRYPT, ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_W | OPTYPE_ss | OP_R, ARG_NONE, cpu_AESNI, "sha1nexte", 0, 0, 0)
tbl32_0F38[0xC9] = (0, INS_CRYPT, ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_W | OPTYPE_ss | OP_R, ARG_NONE, cpu_AESNI, "sha1msg1", 0, 0, 0)
tbl32_0F38[0xCA] = (0, INS_CRYPT, ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_W | OPTYPE_ss | OP_R, ARG_NONE, cpu_AESNI, "sha1msg2", 0, 0, 0)
tbl32_0F38[0xCB] = (0, INS_CRYPT, ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_W | OPTYPE_ss | OP_R, OP_REG | OP_R, cpu_AESNI, "sha256rnds2", 0, 0, e_amd64_regs.REG_XMM0)
tbl32_0F38[0xCC] = (0, INS_CRYPT, ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_W | OPTYPE_ss | OP_R, ARG_NONE, cpu_AESNI, "sha256msg1", 0, 0, 0)
tbl32_0F38[0xCD] = (0, INS_CRYPT, ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_W | OPTYPE_ss | OP_R, ARG_NONE, cpu_AESNI, "sha256msg2", 0, 0, 0)

tbl32_0F38[0xf0] = (0, INS_SYSTEM, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_M | OPTYPE_v | OP_R, ARG_NONE, cpu_AMD64, "movbe", 0, 0, 0)
tbl32_0F38[0xf1] = (0, INS_SYSTEM, ADDRMETH_M | OPTYPE_v | OP_W, ADDRMETH_G | OPTYPE_v | OP_R, ARG_NONE, cpu_AMD64, "movbe", 0, 0, 0)
tbl32_0F38[0xf2] = (0, INS_VEXNOPREF | INS_AND, ADDRMETH_G | OPTYPE_v | OP_W, ADDRMETH_B | OPTYPE_v | OP_R, ADDRMETH_E | OPTYPE_v | OP_R, cpu_AMD64, "andn", 0, 0, 0)
tbl32_0F38[0xf3] = (TBL_0F38F3, 0, 0, 0, 0, 0, 0, 0, 0, 0)
tbl32_0F38[0xf7] = (0, INS_VEXNOPREF | INS_BIT, ADDRMETH_G | OPTYPE_y | OP_W, ADDRMETH_E | OPTYPE_y | OP_R, ADDRMETH_B | OPTYPE_y | OP_R, cpu_AMD64, "bextr", 0, 0, 0)


tbl32_660F38 = [(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0) for x in range(256)]
tbl32_660F38[0x00] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, "pshufb", 0, 0, 0)   # all of these require VEX prefix
tbl32_660F38[0x01] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, "phaddw", 0, 0, 0)
tbl32_660F38[0x02] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, "phaddd", 0, 0, 0)
tbl32_660F38[0x03] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, "phaddsw", 0, 0, 0)
tbl32_660F38[0x04] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, "pmaddubsw", 0, 0, 0)
tbl32_660F38[0x05] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, "phsubw", 0, 0, 0)
tbl32_660F38[0x06] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, "phsubd", 0, 0, 0)
tbl32_660F38[0x07] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, "phsubsw", 0, 0, 0)
tbl32_660F38[0x08] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, "psignb", 0, 0, 0)
tbl32_660F38[0x09] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, "psignw", 0, 0, 0)
tbl32_660F38[0x0a] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, "psignd", 0, 0, 0)
tbl32_660F38[0x0b] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, "pmulhrsw", 0, 0, 0)
# So while the above all have non-VEX counterparts, most of the remaining ones here don't. permilps for instance,
# is only decoded as vpermilps, at least according to the intel manual
tbl32_660F38[0x0c] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, "permilps", 0, 0, 0)
tbl32_660F38[0x0d] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, "permilpd", 0, 0, 0)
tbl32_660F38[0x0e] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, "testps", 0, 0, 0)
tbl32_660F38[0x0f] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, "testpd", 0, 0, 0)
tbl32_660F38[0x10] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, ARG_NONE, "pblendvb", 0, 0, 0)
tbl32_660F38[0x13] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x  | OP_W, ADDRMETH_W | OPTYPE_x  | OP_R, ARG_NONE, ARG_NONE, cpu_AMD64, "cvtph2ps", 0, 0, 0)

tbl32_660F38[0x14] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_dq | OP_R, ADDRMETH_VEXSKIP | ADDRMETH_V | OPTYPE_b | OP_R, cpu_AMD64, "blendvps", 0, 0, 0)
tbl32_660F38[0x15] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_dq | OP_R, ADDRMETH_VEXSKIP | ADDRMETH_V | OPTYPE_b | OP_R, cpu_AMD64, "blendvpd", 0, 0, 0)

tbl32_660F38[0x16] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_qq | OP_W, ADDRMETH_H | OPTYPE_qq | OP_R, ADDRMETH_W | OPTYPE_qq | OP_R, ARG_NONE, cpu_AMD64, "permps", 0, 0, 0)
tbl32_660F38[0x17] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x  | OP_W, ADDRMETH_W | OPTYPE_x  | OP_R, ARG_NONE, ARG_NONE, cpu_AMD64, "ptest", 0, 0, 0)
tbl32_660F38[0x18] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x  | OP_W, ADDRMETH_W | OPTYPE_ss | OP_R | OP_NOVEXL | OP_MEM_D, ARG_NONE, ARG_NONE, cpu_AMD64, "broadcastss", 0, 0, 0)
tbl32_660F38[0x19] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_qq | OP_W, ADDRMETH_W | OPTYPE_ss | OP_R | OP_NOVEXL | OP_MEM_Q, ARG_NONE, ARG_NONE, cpu_AMD64, "broadcastsd", 0, 0, 0)
tbl32_660F38[0x1a] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_qq | OP_W, ADDRMETH_M | OPTYPE_dq | OP_R, ARG_NONE, ARG_NONE, cpu_AMD64, "broadcastf128", 0, 0, 0)
tbl32_660F38[0x1c] = (0, INS_ABS, ADDRMETH_V | OPTYPE_x  | OP_W, ADDRMETH_W | OPTYPE_x  | OP_R, ARG_NONE, ARG_NONE, cpu_AMD64, "pabsb", 0, 0, 0)
tbl32_660F38[0x1d] = (0, INS_ABS, ADDRMETH_V | OPTYPE_x  | OP_W, ADDRMETH_W | OPTYPE_x  | OP_R, ARG_NONE, ARG_NONE, cpu_AMD64, "pabsw", 0, 0, 0)
tbl32_660F38[0x1e] = (0, INS_ABS, ADDRMETH_V | OPTYPE_x  | OP_W, ADDRMETH_W | OPTYPE_x  | OP_R, ARG_NONE, ARG_NONE, cpu_AMD64, "pabsd", 0, 0, 0)

# TODO: There's a ymm version on this one that has a memory size of 128. Dammit. Though that only happens in vex256 land, it's still annoying
tbl32_660F38[0x20] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R | OP_MEM_Q | OP_NOVEXL, ARG_NONE, ARG_NONE, cpu_AMD64, "pmovsxbw", 0, 0, 0)
tbl32_660F38[0x21] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R | OP_MEM_D | OP_NOVEXL, ARG_NONE, ARG_NONE, cpu_AMD64, "pmovsxbd", 0, 0, 0)
tbl32_660F38[0x22] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R | OP_MEM_W | OP_NOVEXL, ARG_NONE, ARG_NONE, cpu_AMD64, "pmovsxbq", 0, 0, 0)
tbl32_660F38[0x23] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R | OP_MEM_Q | OP_NOVEXL, ARG_NONE, ARG_NONE, cpu_AMD64, "pmovsxwd", 0, 0, 0)
tbl32_660F38[0x24] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R | OP_MEM_D | OP_NOVEXL, ARG_NONE, ARG_NONE, cpu_AMD64, "pmovsxwq", 0, 0, 0)
tbl32_660F38[0x25] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R | OP_MEM_Q | OP_NOVEXL, ARG_NONE, ARG_NONE, cpu_AMD64, "pmovsxdq", 0, 0, 0)

tbl32_660F38[0x28] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, "pmuldq", 0, 0, 0)
tbl32_660F38[0x29] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, "pcmpeqq", 0, 0, 0)
tbl32_660F38[0x2A] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_M | OPTYPE_x | OP_R, ARG_NONE, ARG_NONE, cpu_AMD64, "movntdqa", 0, 0, 0)
tbl32_660F38[0x2B] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, "packusdw", 0, 0, 0)
tbl32_660F38[0x2C] = (0, INS_VEXREQ | INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_M | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, "maskmovps", 0, 0, 0)
tbl32_660F38[0x2D] = (0, INS_VEXREQ | INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_M | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, "maskmovpd", 0, 0, 0)
tbl32_660F38[0x2E] = (0, INS_VEXREQ | INS_OTHER, ADDRMETH_M | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_V | OPTYPE_x | OP_W, ARG_NONE, cpu_AMD64, "maskmovps", 0, 0, 0)
tbl32_660F38[0x2F] = (0, INS_VEXREQ | INS_OTHER, ADDRMETH_M | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_V | OPTYPE_x | OP_W, ARG_NONE, cpu_AMD64, "maskmovpd", 0, 0, 0)

# TODO: There's a ymm version on this one that has a memory size of 128. Dammit
tbl32_660F38[0x30] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R | OP_MEM_Q | OP_NOVEXL, ARG_NONE, ARG_NONE, cpu_AMD64, "pmovzxbw", 0, 0, 0)
tbl32_660F38[0x31] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R | OP_MEM_D | OP_NOVEXL, ARG_NONE, ARG_NONE, cpu_AMD64, "pmovzxbd", 0, 0, 0)
tbl32_660F38[0x32] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R | OP_MEM_W | OP_NOVEXL, ARG_NONE, ARG_NONE, cpu_AMD64, "pmovzxbq", 0, 0, 0)
tbl32_660F38[0x33] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R | OP_MEM_Q | OP_NOVEXL, ARG_NONE, ARG_NONE, cpu_AMD64, "pmovzxwd", 0, 0, 0)
tbl32_660F38[0x34] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R | OP_MEM_D | OP_NOVEXL, ARG_NONE, ARG_NONE, cpu_AMD64, "pmovzxwq", 0, 0, 0)
tbl32_660F38[0x35] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_ps | OP_R | OP_MEM_Q | OP_NOVEXL, ARG_NONE, ARG_NONE, cpu_AMD64, "pmovzxdq", 0, 0, 0)
tbl32_660F38[0x36] = (0, INS_VEXREQ | INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, "permd", 0, 0, 0)
tbl32_660F38[0x37] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, "pcmpgtq", 0, 0, 0)
tbl32_660F38[0x38] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, "pminsb", 0, 0, 0)
tbl32_660F38[0x39] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, "pminsd", 0, 0, 0)
tbl32_660F38[0x3A] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, "pminuw", 0, 0, 0)
tbl32_660F38[0x3B] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, "pminud", 0, 0, 0)
tbl32_660F38[0x3C] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, "pmaxsb", 0, 0, 0)
tbl32_660F38[0x3D] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, "pmaxsd", 0, 0, 0)
tbl32_660F38[0x3E] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, "pmaxuw", 0, 0, 0)
tbl32_660F38[0x3F] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, "pmaxud", 0, 0, 0)

tbl32_660F38[0x40] = (0, INS_MUL, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AMD64, "pmulld", 0, 0, 0)

tbl32_660F38[0x58] = (0, INS_VEXREQ | INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_dq | OP_MEM_D | OP_R, ARG_NONE, ARG_NONE, cpu_AVX, "pbroadcastd", 0, 0, 0)
tbl32_660F38[0x59] = (0, INS_VEXREQ | INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_dq | OP_MEM_Q | OP_R, ARG_NONE, ARG_NONE, cpu_AVX, "pbroadcastq", 0, 0, 0)
tbl32_660F38[0x5a] = (0, INS_VEXREQ | INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, ARG_NONE, cpu_AVX, "pbroadcasti128", 0, 0, 0)

tbl32_660F38[0x78] = (0, INS_VEXREQ | INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_dq | OP_MEM_B | OP_R, ARG_NONE, ARG_NONE, cpu_AVX, "pbroadcastb", 0, 0, 0)
tbl32_660F38[0x79] = (0, INS_VEXREQ | INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_dq | OP_MEM_W | OP_R, ARG_NONE, ARG_NONE, cpu_AVX, "pbroadcastw", 0, 0, 0)

# more here necessary....
tbl32_660F38[0x80] = (0, INS_SYSTEM, ADDRMETH_G | OPTYPE_q | OP_R, ADDRMETH_M | OPTYPE_dq | OP_R, ARG_NONE, ARG_NONE, cpu_AMD64, "invept", 0, 0, 0)
tbl32_660F38[0x81] = (0, INS_SYSTEM, ADDRMETH_G | OPTYPE_q | OP_R, ADDRMETH_M | OPTYPE_dq | OP_R, ARG_NONE, ARG_NONE, cpu_AMD64, "invvpid", 0, 0, 0)
tbl32_660F38[0x82] = (0, INS_SYSTEM, ADDRMETH_G | OPTYPE_q | OP_R, ADDRMETH_M | OPTYPE_dq | OP_R, ARG_NONE, ARG_NONE, cpu_AMD64, "invpcid", 0, 0, 0)

# TODO: Ugh. Add decoding for the whole VSIB stuff eventually.
tbl32_660F38[0x96] = (0, INS_ARITH | INS_VEXREQ, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "fmaddsub132ps_d", 0, 0, 0) # TODO: Ugh. REX.W again
tbl32_660F38[0x97] = (0, INS_ARITH | INS_VEXREQ, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "fmsubadd132ps_d", 0, 0, 0) # TODO: Ugh. REX.W again

tbl32_660F38[0x98] = (0, INS_ARITH | INS_VEXREQ, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "fmadd132ps_d", 0, 0, 0)
tbl32_660F38[0x99] = (0, INS_ARITH | INS_VEXREQ, ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_H | OPTYPE_ss | OP_R, ADDRMETH_W | OPTYPE_ss | OP_R | OP_MEM_Q, ARG_NONE, cpu_AVX, "fmadd132ss_d", 0, 0, 0)
tbl32_660F38[0x9a] = (0, INS_ARITH | INS_VEXREQ, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "fmsub132ps_d", 0, 0, 0)
tbl32_660F38[0x9b] = (0, INS_ARITH | INS_VEXREQ, ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_H | OPTYPE_ss | OP_R, ADDRMETH_W | OPTYPE_ss | OP_R | OP_MEM_Q, ARG_NONE, cpu_AVX, "fmsub132ss_d", 0, 0, 0)
tbl32_660F38[0x9c] = (0, INS_ARITH | INS_VEXREQ, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "fnmadd132ps_d", 0, 0, 0)
tbl32_660F38[0x9d] = (0, INS_ARITH | INS_VEXREQ, ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_H | OPTYPE_ss | OP_R, ADDRMETH_W | OPTYPE_ss | OP_R | OP_MEM_Q, ARG_NONE, cpu_AVX, "fnmadd132ss_d", 0, 0, 0)
tbl32_660F38[0x9e] = (0, INS_ARITH | INS_VEXREQ, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "fnmsub132ps_d", 0, 0, 0)
tbl32_660F38[0x9f] = (0, INS_ARITH | INS_VEXREQ, ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_H | OPTYPE_ss | OP_R, ADDRMETH_W | OPTYPE_ss | OP_R | OP_MEM_Q, ARG_NONE, cpu_AVX, "fnmsub132ss_d", 0, 0, 0)

tbl32_660F38[0xa6] = (0, INS_ARITH | INS_VEXREQ, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "fmaddsub213ps_d", 0, 0, 0) # TODO: Ugh. REX.W again
tbl32_660F38[0xa7] = (0, INS_ARITH | INS_VEXREQ, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "fmsubadd213ps_d", 0, 0, 0) # TODO: Ugh. REX.W again

tbl32_660F38[0xa8] = (0, INS_ARITH | INS_VEXREQ, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "fmadd213ps_d", 0, 0, 0)
tbl32_660F38[0xa9] = (0, INS_ARITH | INS_VEXREQ, ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_H | OPTYPE_ss | OP_R, ADDRMETH_W | OPTYPE_ss | OP_R | OP_MEM_Q, ARG_NONE, cpu_AVX, "fmadd213ss_d", 0, 0, 0)
tbl32_660F38[0xaa] = (0, INS_ARITH | INS_VEXREQ, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "fmsub213ps_d", 0, 0, 0)
tbl32_660F38[0xab] = (0, INS_ARITH | INS_VEXREQ, ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_H | OPTYPE_ss | OP_R, ADDRMETH_W | OPTYPE_ss | OP_R | OP_MEM_Q, ARG_NONE, cpu_AVX, "fmsub213ss_d", 0, 0, 0)
tbl32_660F38[0xac] = (0, INS_ARITH | INS_VEXREQ, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "fnmadd213ps_d", 0, 0, 0)
tbl32_660F38[0xad] = (0, INS_ARITH | INS_VEXREQ, ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_H | OPTYPE_ss | OP_R, ADDRMETH_W | OPTYPE_ss | OP_R | OP_MEM_Q, ARG_NONE, cpu_AVX, "fnmadd213ss_d", 0, 0, 0)
tbl32_660F38[0xae] = (0, INS_ARITH | INS_VEXREQ, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "fnmsub213ps_d", 0, 0, 0)
tbl32_660F38[0xaf] = (0, INS_ARITH | INS_VEXREQ, ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_H | OPTYPE_ss | OP_R, ADDRMETH_W | OPTYPE_ss | OP_R | OP_MEM_Q, ARG_NONE, cpu_AVX, "fnmsub213ss_d", 0, 0, 0)

tbl32_660F38[0xb6] = (0, INS_ARITH | INS_VEXREQ, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "fmaddsub231ps_d", 0, 0, 0) # TODO: Ugh. REX.W again
tbl32_660F38[0xb7] = (0, INS_ARITH | INS_VEXREQ, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "fmsubadd231ps_d", 0, 0, 0) # TODO: Ugh. REX.W again

tbl32_660F38[0xb8] = (0, INS_ARITH | INS_VEXREQ, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "fmadd231ps_d", 0, 0, 0)
tbl32_660F38[0xb9] = (0, INS_ARITH | INS_VEXREQ, ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_H | OPTYPE_ss | OP_R, ADDRMETH_W | OPTYPE_ss | OP_R | OP_MEM_Q, ARG_NONE, cpu_AVX, "fmadd231ss_d", 0, 0, 0)
tbl32_660F38[0xba] = (0, INS_ARITH | INS_VEXREQ, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "fmsub231ps_d", 0, 0, 0)
tbl32_660F38[0xbb] = (0, INS_ARITH | INS_VEXREQ, ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_H | OPTYPE_ss | OP_R, ADDRMETH_W | OPTYPE_ss | OP_R | OP_MEM_Q, ARG_NONE, cpu_AVX, "fmsub231ss_d", 0, 0, 0)
tbl32_660F38[0xbc] = (0, INS_ARITH | INS_VEXREQ, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "fnmadd231ps_d", 0, 0, 0)
tbl32_660F38[0xbd] = (0, INS_ARITH | INS_VEXREQ, ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_H | OPTYPE_ss | OP_R, ADDRMETH_W | OPTYPE_ss | OP_R | OP_MEM_Q, ARG_NONE, cpu_AVX, "fnmadd231ss_d", 0, 0, 0)
tbl32_660F38[0xbe] = (0, INS_ARITH | INS_VEXREQ, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ARG_NONE, cpu_AVX, "fnmsub231ps_d", 0, 0, 0)
tbl32_660F38[0xbf] = (0, INS_ARITH | INS_VEXREQ, ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_H | OPTYPE_ss | OP_R, ADDRMETH_W | OPTYPE_ss | OP_R | OP_MEM_Q, ARG_NONE, cpu_AVX, "fnmsub231ss_d", 0, 0, 0)

tbl32_660F38[0xdb] = (0, INS_CRYPT, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, ARG_NONE, cpu_AESNI, "aesimc", 0, 0, 0)
tbl32_660F38[0xdc] = (0, INS_CRYPT, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_dq | OP_R, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_AESNI, "aesenc", 0, 0, 0)
tbl32_660F38[0xdd] = (0, INS_CRYPT, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_dq | OP_R, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_AESNI, "aesenclast", 0, 0, 0)
tbl32_660F38[0xde] = (0, INS_CRYPT, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_dq | OP_R, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_AESNI, "aesdec", 0, 0, 0)
tbl32_660F38[0xdf] = (0, INS_CRYPT, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_dq | OP_R, ADDRMETH_W | OPTYPE_dq | OP_R, ARG_NONE, cpu_AESNI, "aesdeclast", 0, 0, 0)

tbl32_660F38[0xf6] = (0, INS_ADD, ADDRMETH_G | OPTYPE_y | OP_W, ADDRMETH_E | OPTYPE_y | OP_R, ARG_NONE, ARG_NONE, cpu_BMI, "adcx", 0, 0, 0)
tbl32_660F38[0xf7] = (0, INS_SHL | INS_VEXREQ | INS_VEXNOPREF, ADDRMETH_G | OPTYPE_y | OP_W, ADDRMETH_E | OPTYPE_y | OP_R, ADDRMETH_B | OPTYPE_y | OP_R, ARG_NONE, cpu_BMI, "shlx", 0, 0, 0)

tbl32_F20F38 = [ (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0) for x in range(8) ]
tbl32_F20F38[0] = (0, INS_OTHER, ADDRMETH_G | OPTYPE_d | OP_W, ADDRMETH_E | OPTYPE_b | OP_R, ARG_NONE, ARG_NONE, cpu_AMD64, "crc32", 0, 0, 0)
#XXX: Thanks intel for not differentiating between 16 and 32 here
tbl32_F20F38[1] = (0, INS_OTHER, ADDRMETH_G | OPTYPE_d | OP_W, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_AMD64, "crc32", 0, 0, 0)
tbl32_F20F38[5] = (0, INS_OTHER | INS_VEXNOPREF | INS_VEXREQ, ADDRMETH_G | OPTYPE_y | OP_W, ADDRMETH_B | OPTYPE_y | OP_R, ADDRMETH_E | OPTYPE_y | OP_R, ARG_NONE, cpu_BMI, "pdep", 0, 0, 0)
tbl32_F20F38[6] = (0, INS_OTHER | INS_VEXNOPREF | INS_VEXREQ, ADDRMETH_G | OPTYPE_y | OP_W, ADDRMETH_B | OPTYPE_y | OP_R, ADDRMETH_E | OPTYPE_y | OP_R, ARG_NONE, cpu_BMI, "mulx", 0, 0, 0)
tbl32_F20F38[7] = (0, INS_OTHER | INS_VEXNOPREF | INS_VEXREQ, ADDRMETH_G | OPTYPE_y | OP_W, ADDRMETH_E | OPTYPE_y | OP_R, ADDRMETH_B | OPTYPE_y | OP_R, ARG_NONE, cpu_BMI, "shrx", 0, 0, 0)


tbl32_F30F38 = [(0, 0, 0, 0, 0, 0, 0, 0, 0,) for x in range(8)]
tbl32_F30F38[5] = (0, INS_OTHER | INS_VEXREQ | INS_VEXNOPREF, ADDRMETH_G | OPTYPE_y | OP_W, ADDRMETH_B | OPTYPE_y | OP_R, ADDRMETH_E | OPTYPE_y | OP_R, cpu_AMD64, "pext", 0, 0, 0)
tbl32_F30F38[6] = (0, INS_ADD, ADDRMETH_G | OPTYPE_y | OP_W, ADDRMETH_E | OPTYPE_y | OP_R, ARG_NONE, cpu_AMD64, "adox", 0, 0, 0)
tbl32_F30F38[7] = (0, INS_SHR | INS_VEXREQ | INS_VEXNOPREF, ADDRMETH_G | OPTYPE_y | OP_W, ADDRMETH_E | OPTYPE_y | OP_R, ADDRMETH_B | OPTYPE_y | OP_R, cpu_AMD64, "sarx", 0, 0, 0)


desc_0F38   = (tbl32_0F38, 3, 0, 0xff, 0, 0xff)
desc_660F38 = (tbl32_660F38, 4, 0, 0xff, 0, 0xff)
desc_F20F38 = (tbl32_F20F38, 4, 0, 0xff, 0xf0, 0xff)
desc_F30F38 = (tbl32_F30F38, 3, 0, 0xff, 0xf0, 0xff)


tbl32_0F38F3 = [ (0, 0, 0, 0, 0, 0, 0, 0, 0, 0) for x in range(256) ]
tbl32_0F38F3[1] = (0, INS_VEXNOPREF | INS_VEXREQ | INS_OTHER, ADDRMETH_B | OPTYPE_y | OP_W, ADDRMETH_E | OPTYPE_y | OP_R, ARG_NONE, cpu_AMD64, "blsr", 0, 0, 0)
tbl32_0F38F3[2] = (0, INS_VEXNOPREF | INS_VEXREQ | INS_OTHER, ADDRMETH_B | OPTYPE_y | OP_W, ADDRMETH_E | OPTYPE_y | OP_R, ARG_NONE, cpu_AMD64, "blsmsk", 0, 0, 0)
tbl32_0F38F3[3] = (0, INS_VEXNOPREF | INS_VEXREQ | INS_OTHER, ADDRMETH_B | OPTYPE_y | OP_W, ADDRMETH_E | OPTYPE_y | OP_R, ARG_NONE, cpu_AMD64, "blsi", 0, 0, 0)

desc_0F38F3 = (tbl32_0F38F3,3,3,0x7,0,0xff)


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
##### NOTE: this table configured for 4 arguments
tbl32_0F3A = [ (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0) for x in range(256) ]
tbl32_0F3A[0x0f] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_q | OP_W, ADDRMETH_W | OPTYPE_q | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTIUM2, "palignr", 0, 0, 0)
tbl32_0F3A[0xcc] = (0, INS_CRYPT, ADDRMETH_V | OPTYPE_ss | OP_W, ADDRMETH_W | OPTYPE_ss | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_AESNI, "sha1rnds4", 0, 0, 0)

tbl32_660F3A = [(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0) for x in range(256)]
tbl32_660F3A[0x00] = (0, INS_VEXREQ | INS_OTHER, ADDRMETH_V | OPTYPE_qq | OP_W, ADDRMETH_W | OPTYPE_qq | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_AMD64, "permq", 0, 0, 0)    # requires VEX
tbl32_660F3A[0x01] = (0, INS_VEXREQ | INS_OTHER, ADDRMETH_V | OPTYPE_qq | OP_W, ADDRMETH_W | OPTYPE_qq | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_AMD64, "permpd", 0, 0, 0)   # requires VEX
tbl32_660F3A[0x02] = (0, INS_VEXREQ | INS_OTHER, ADDRMETH_V | OPTYPE_x  | OP_W, ADDRMETH_H | OPTYPE_x  | OP_R, ADDRMETH_W | OPTYPE_x  | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_AMD64, "pblendd", 0, 0, 0)   # requires VEX
tbl32_660F3A[0x04] = (0, INS_VEXREQ | INS_OTHER, ADDRMETH_V | OPTYPE_x  | OP_W, ADDRMETH_W | OPTYPE_x  | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_AMD64, "permilps", 0, 0, 0) # requires VEX
tbl32_660F3A[0x05] = (0, INS_VEXREQ | INS_OTHER, ADDRMETH_V | OPTYPE_x  | OP_W, ADDRMETH_W | OPTYPE_q  | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_AMD64, "permilpd", 0, 0, 0) # requires VEX
tbl32_660F3A[0x06] = (0, INS_VEXREQ | INS_OTHER, ADDRMETH_V | OPTYPE_qq | OP_W, ADDRMETH_H | OPTYPE_qq | OP_R, ADDRMETH_W | OPTYPE_qq | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_AMD64, "perm2f128", 0, 0, 0)    # requires VEX

tbl32_660F3A[0x08] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_AMD64, "roundps", 0, 0, 0)
tbl32_660F3A[0x09] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_AMD64, "roundpd", 0, 0, 0)

tbl32_660F3A[0x0A] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_dq | OP_R, ADDRMETH_W | OPTYPE_ds | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_AMD64, "roundss", 0, 0, 0)
tbl32_660F3A[0x0B] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_dq | OP_R, ADDRMETH_W | OPTYPE_q | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_AMD64, "roundsd", 0, 0, 0)

tbl32_660F3A[0x0C] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_AMD64, "blendps", 0, 0, 0)
tbl32_660F3A[0x0D] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_AMD64, "blendpd", 0, 0, 0)
tbl32_660F3A[0x0E] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_AMD64, "pblendw", 0, 0, 0)
tbl32_660F3A[0x0f] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_W | OPTYPE_x | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTIUM2, "palignr", 0, 0, 0)

tbl32_660F3A[0x14] = (0, INS_OTHER, ADDRMETH_E | OPTYPE_y | OP_W | OP_MEM_B, ADDRMETH_V | OPTYPE_dq | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_AMD64, "pextrb", 0, 0, 0)
tbl32_660F3A[0x15] = (0, INS_OTHER, ADDRMETH_E | OPTYPE_y | OP_W | OP_MEM_D, ADDRMETH_V | OPTYPE_dq | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_AMD64, "pextrw", 0, 0, 0)
tbl32_660F3A[0x16] = (0, INS_OTHER, ADDRMETH_E | OPTYPE_y | OP_W, ADDRMETH_V | OPTYPE_dq | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_AMD64, "pextrd_q", 0, 0, 0)

tbl32_660F3A[0x17] = (0, INS_OTHER, ADDRMETH_E | OPTYPE_d  | OP_W, ADDRMETH_V | OPTYPE_dq | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_AMD64, "extractps", 0, 0, 0)    # requires VEX
tbl32_660F3A[0x18] = (0, INS_VEXREQ | INS_OTHER, ADDRMETH_V | OPTYPE_qq | OP_W, ADDRMETH_H | OPTYPE_qq | OP_R, ADDRMETH_W | OPTYPE_qq | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_AMD64, "insertf128", 0, 0, 0)    # requires VEX
tbl32_660F3A[0x19] = (0, INS_VEXREQ | INS_OTHER, ADDRMETH_W | OPTYPE_dq | OP_W, ADDRMETH_V | OPTYPE_qq | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_AMD64, "extractf128", 0, 0, 0)    # requires VEX
tbl32_660F3A[0x1d] = (0, INS_VEXREQ | INS_OTHER, ADDRMETH_W | OPTYPE_x  | OP_W, ADDRMETH_V | OPTYPE_x  | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_AMD64, "cvtps2ph", 0, 0, 0)    # requires VEX
# TODO: Need more in OPTYPE_* dictionary for sizes

tbl32_660F3A[0x20] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_dq | OP_R, ADDRMETH_E | OPTYPE_d | OP_R | OP_MEM_B, ADDRMETH_I | OPTYPE_b | OP_R, cpu_AMD64, "pinsrb", 0, 0, 0)
tbl32_660F3A[0x21] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_dq | OP_R, ADDRMETH_W | OPTYPE_ds | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_AMD64, "insertps", 0, 0, 0)    # requires VEX
tbl32_660F3A[0x22] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_dq  | OP_R, ADDRMETH_E | OPTYPE_y  | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_AMD64, "pinsrd", 0, 0, 0)    # requires VEX

tbl32_660F3A[0x38] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_qq | OP_W, ADDRMETH_H | OPTYPE_qq  | OP_R, ADDRMETH_W | OPTYPE_qq | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_AMD64, "inserti128", 0, 0, 0)    # requires VEX
tbl32_660F3A[0x39] = (0, INS_OTHER, ADDRMETH_W | OPTYPE_dq | OP_W, ADDRMETH_V | OPTYPE_qq  | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_AMD64, "extracti128", 0, 0, 0)    # requires VEX

tbl32_660F3A[0x40] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x  | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x   | OP_R, ADDRMETH_W | OPTYPE_x  | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_AMD64, "dpps", 0, 0, 0)    # requires VEX
tbl32_660F3A[0x41] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_dq  | OP_R, ADDRMETH_W | OPTYPE_dq | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_AMD64, "dppd", 0, 0, 0)    # requires VEX
tbl32_660F3A[0x42] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_x  | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x   | OP_R, ADDRMETH_W | OPTYPE_x  | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_AMD64, "mpsadbw", 0, 0, 0)    # requires VEX
tbl32_660F3A[0x44] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_dq  | OP_R, ADDRMETH_W | OPTYPE_dq | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_AMD64, "pclmulqdq", 0, 0, 0)    # requires VEX
tbl32_660F3A[0x46] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_qq | OP_W, ADDRMETH_H | OPTYPE_qq  | OP_R, ADDRMETH_W | OPTYPE_qq | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_AMD64, "perm2i128", 0, 0, 0)    # requires VEX

tbl32_660F3A[0x4a] = (0, INS_VEXREQ | INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ADDRMETH_L | OPTYPE_x | OP_R, cpu_AMD64, "blendvps", 0, 0, 0)
tbl32_660F3A[0x4b] = (0, INS_VEXREQ | INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ADDRMETH_L | OPTYPE_x | OP_R, cpu_AMD64, "blendvpd", 0, 0, 0)
tbl32_660F3A[0x4c] = (0, INS_VEXREQ | INS_OTHER, ADDRMETH_V | OPTYPE_x | OP_W, ADDRMETH_H | OPTYPE_x | OP_R, ADDRMETH_W | OPTYPE_x | OP_R, ADDRMETH_L | OPTYPE_x | OP_R, cpu_AMD64, "pblendvb", 0, 0, 0)

tbl32_660F3A[0x60] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq  | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_AMD64, "pcmpestrm", 0, 0, 0)
tbl32_660F3A[0x61] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq  | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_AMD64, "pcmpestri", 0, 0, 0)
tbl32_660F3A[0x62] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq  | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_AMD64, "pcmpistrm", 0, 0, 0)
tbl32_660F3A[0x63] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq  | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_AMD64, "pcmpistri", 0, 0, 0)

tbl32_660F3A[0xdf] = (0, INS_OTHER, ADDRMETH_V | OPTYPE_dq | OP_W, ADDRMETH_W | OPTYPE_dq  | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_AMD64, "aeskeygenassist", 0, 0, 0)


tbl32_F20F3A = list(tbl32_0F3A)
tbl32_F20F3A[0xf0] = ( 0, INS_OTHER, ADDRMETH_G | OPTYPE_y | OP_W, ADDRMETH_E | OPTYPE_y | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_AMD64, "rorx", 0, 0, 0)

desc_0F3A           = (tbl32_0F3A,3,0,0xff,0,0xff)
desc_660F3A         = (tbl32_660F3A,4,0,0xff,0,0xff)
desc_F20F3A         = (tbl32_F20F3A,3,0,0xff,0,0xff)


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_0F71 = [(0, 0, 0, 0, 0, 0, 0, 0, 0, 0) for x in range(8)]
tbl32_0F71[2] = (0, INS_OTHER, ADDRMETH_N | OPTYPE_q | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTMMX, "psrlw", 0, 0, 0)
tbl32_0F71[4] = (0, INS_OTHER, ADDRMETH_N | OPTYPE_q | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTMMX, "psraw", 0, 0, 0)
tbl32_0F71[6] = (0, INS_OTHER, ADDRMETH_N | OPTYPE_q | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTMMX, "psllw", 0, 0, 0)

tbl32_660F71 = [(0, 0, 0, 0, 0, 0, 0, 0, 0, 0) for x in range(8)]
tbl32_660F71[2] = (0, INS_OTHER, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_W, ADDRMETH_U | OPTYPE_x | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTMMX, "psrlw", 0, 0, 0)
tbl32_660F71[4] = (0, INS_OTHER, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_W, ADDRMETH_U | OPTYPE_x | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTMMX, "psraw", 0, 0, 0)
tbl32_660F71[6] = (0, INS_OTHER, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_W, ADDRMETH_U | OPTYPE_x | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTMMX, "psllw", 0, 0, 0)

desc_0F71 = (tbl32_0F71,3,3,0x07,0,0xff)
desc_660F71 = (tbl32_660F71,3,3,0x07,0,0xff)


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_0F72 = [(0, 0, 0, 0, 0, 0, 0, 0, 0, 0) for x in range(8)]
tbl32_0F72[2] = (0, INS_OTHER, ADDRMETH_N | OPTYPE_q | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTMMX, "psrld", 0, 0, 0)
tbl32_0F72[4] = (0, INS_OTHER, ADDRMETH_N | OPTYPE_q | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTMMX, "psrad", 0, 0, 0)
tbl32_0F72[6] = (0, INS_OTHER, ADDRMETH_N | OPTYPE_q | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTMMX, "pslld", 0, 0, 0)

tbl32_660F72 = [(0, 0, 0, 0, 0, 0, 0, 0, 0, 0) for x in range(8)]
tbl32_660F72[2] = (0, INS_OTHER, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_W, ADDRMETH_U | OPTYPE_x | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTMMX, "psrld", 0, 0, 0)
tbl32_660F72[4] = (0, INS_OTHER, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_W, ADDRMETH_U | OPTYPE_x | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTMMX, "psrad", 0, 0, 0)
tbl32_660F72[6] = (0, INS_OTHER, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_W, ADDRMETH_U | OPTYPE_x | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTMMX, "pslld", 0, 0, 0)
desc_0F72 = (tbl32_0F72, 3, 3, 0x07, 0, 0xff)
desc_660F72 = (tbl32_660F72, 3, 3, 0x07, 0, 0xff)


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_0F73 = [(0, 0, 0, 0, 0, 0, 0, 0, 0, 0) for x in range(8)]
tbl32_0F73[2] = (0, INS_OTHER, ADDRMETH_N | OPTYPE_q | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTMMX, "psrlq", 0, 0, 0)
tbl32_0F73[6] = (0, INS_OTHER, ADDRMETH_N | OPTYPE_q | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTMMX, "psllq", 0, 0, 0)
tbl32_0F73[7] = (0, INS_OTHER, ADDRMETH_N | OPTYPE_q | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_PENTMMX, "pslldq", 0, 0, 0)

tbl32_660F73 = [(0, 0, 0, 0, 0, 0, 0, 0, 0, 0) for x in range(8)]
tbl32_660F73[2] = (0, INS_OTHER, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_W, ADDRMETH_U | OPTYPE_dq | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTMMX, "psrlq", 0, 0, 0)
tbl32_660F73[3] = (0, INS_OTHER, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_W, ADDRMETH_U | OPTYPE_x  | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTMMX, "psrldq", 0, 0, 0)
tbl32_660F73[6] = (0, INS_OTHER, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_W, ADDRMETH_U | OPTYPE_dq | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTMMX, "psllq", 0, 0, 0)
tbl32_660F73[7] = (0, INS_OTHER, ADDRMETH_VEXSKIP | ADDRMETH_H | OPTYPE_x | OP_W, ADDRMETH_U | OPTYPE_dq | OP_W, ADDRMETH_I | OPTYPE_b | OP_R, cpu_PENTMMX, "pslldq", 0, 0, 0)

desc_0F73 = (tbl32_0F73, 3, 3, 0x07, 0, 0xff)
desc_660F73 = (tbl32_660F73, 3, 3, 0x07, 0, 0xff)

"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_0FAE_00BF = [	# IA32 manuals don't list an actual address method... guessing by trial/error
( 0, INS_FPU, ADDRMETH_E | OPTYPE_v | OP_W, ARG_NONE, ARG_NONE, cpu_PENTMMX, "fxsave", 0, 0, 0),  
( 0, INS_FPU, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_PENTMMX, "fxrstor", 0, 0, 0),  
( 0, INS_FPU, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "ldmxcsr", 0, 0, 0),  
( 0, INS_FPU, ADDRMETH_E | OPTYPE_v | OP_W, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "stmxcsr", 0, 0, 0),  
( 0, INS_FPU, ADDRMETH_E | OPTYPE_v | OP_W, ARG_NONE, ARG_NONE, cpu_AMD64, 'xsave', 0, 0, 0  ), 
( 0, INS_FPU, ADDRMETH_E | OPTYPE_v | OP_W, ARG_NONE, ARG_NONE, cpu_AMD64, 'xrstor', 0, 0, 0  ), 
( 0, INS_FPU, ADDRMETH_E | OPTYPE_v | OP_W, ARG_NONE, ARG_NONE, cpu_AMD64, 'xsaveopt', 0, 0, 0  ), 
( 0, INS_FPU, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, cpu_PENTIUM2, "clflush", 0, 0, 0  )
]

tbl32_F30FAE_00BF = list( tbl32_0FAE_00BF )

tbl32_0FAE_rest = [ ( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0  ) for x in range(8) ]
tbl32_0FAE_rest[5] = (0, INS_FPU, 0, 0, 0, cpu_PENTIUM2, "lfence", 0, 0, 0)
tbl32_0FAE_rest[6] = (0, INS_FPU, 0, 0, 0, cpu_PENTIUM2, "mfence", 0, 0, 0)
tbl32_0FAE_rest[7] = (0, INS_FPU, 0, 0, 0, cpu_PENTIUM2, "sfence", 0, 0, 0)


tbl32_F30FAE_rest = [ (0, 0, 0, 0, 0, 0, 0, 0, 0, 0  ) for x in range(8) ]
tbl32_F30FAE_rest[0] = (0, INS_OTHER, ADDRMETH_R | OPTYPE_y | OP_R, ARG_NONE, ARG_NONE, cpu_AMD64, "rdfsbase", 0, 0, 0)
tbl32_F30FAE_rest[1] = (0, INS_OTHER, ADDRMETH_R | OPTYPE_y | OP_R, ARG_NONE, ARG_NONE, cpu_AMD64, "rdgsbase", 0, 0, 0)
tbl32_F30FAE_rest[2] = (0, INS_OTHER, ADDRMETH_R | OPTYPE_y | OP_R, ARG_NONE, ARG_NONE, cpu_AMD64, "wrfsbase", 0, 0, 0)
tbl32_F30FAE_rest[3] = (0, INS_OTHER, ADDRMETH_R | OPTYPE_y | OP_R, ARG_NONE, ARG_NONE, cpu_AMD64, "wrgsbase", 0, 0, 0)


desc_0FAE_00BF      = (tbl32_0FAE_00BF,3,3,0x07,0,0xbf, TBL_0FAE_rest)
desc_F30FAE_00BF    = (tbl32_F30FAE_00BF,3,3,0x07,0,0xbf, TBL_F30FAE_rest)
desc_0FAE_rest      = (tbl32_0FAE_rest,3,3,0xFF,0xc0,0xff)
desc_F30FAE_rest    = (tbl32_F30FAE_rest,3,3,0x07,0xc0,0xff)


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_0FBA = [
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0  ), 
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0  ), 
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0  ), 
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0  ), 
( 0, INS_BITTEST, ADDRMETH_E | OPTYPE_v | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "bt", 0, 0, 0),  
( 0, INS_BITTEST, ADDRMETH_E | OPTYPE_v | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "bts", 0, 0, 0),  
( 0, INS_BITTEST, ADDRMETH_E | OPTYPE_v | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "btr", 0, 0, 0),  
( 0, INS_BITTEST, ADDRMETH_E | OPTYPE_v | OP_R, ADDRMETH_I | OPTYPE_b | OP_R, ARG_NONE, cpu_80386, "btc", 0, 0, 0   ) 
]
desc_0FBA       = (tbl32_0FBA,3,3,0x07,0,0xff)


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_0FC7_00BF = [ (0, 0, 0, 0, 0, 0, 0, 0, 0, 0) for x in range(8) ]
tbl32_0FC7_00BF[1] =    ( 0, INS_XCHGCC, ADDRMETH_M | OPTYPE_q | OP_W, ARG_NONE, ARG_NONE, cpu_PENTIUM, "cmpxch8b", 0, 0, 0   )    #FIXME: cmpxch16b??
tbl32_0FC7_00BF[6] =    ( 0, INS_SYSTEM, ADDRMETH_M | OPTYPE_q | OP_W, ARG_NONE, ARG_NONE, cpu_AMD64, "vmptrld", 0, 0, 0)
tbl32_0FC7_00BF[7] =    ( 0, INS_SYSTEM, ADDRMETH_M | OPTYPE_q | OP_W, ARG_NONE, ARG_NONE, cpu_AMD64, "vmptrst", 0, 0, 0)

tbl32_660FC7_00BF = [ (0, 0, 0, 0, 0, 0, 0, 0, 0, 0) for x in range(8) ]
tbl32_660FC7_00BF[6] =  (0, INS_SYSTEM, ADDRMETH_M | OPTYPE_q | OP_W, ARG_NONE, ARG_NONE, cpu_AMD64, "vmclear", 0, 0, 0)

tbl32_F30FC7_00BF = [ (0, 0, 0, 0, 0, 0, 0, 0, 0, 0) for x in range(8) ]
tbl32_F30FC7_00BF[6] =  (0, INS_SYSTEM, ADDRMETH_M | OPTYPE_q | OP_W, ARG_NONE, ARG_NONE, cpu_AMD64, "vmxon", 0, 0, 0)
#tbl32_F30FC7_00BF[7] =  (0, INS_SYSTEM, ADDRMETH_M | OPTYPE_q | OP_W, ARG_NONE, ARG_NONE, cpu_AMD64, "vmptrst", 0, 0, 0) FIXME: No prefix, goes into straight 0f table



tbl32_0FC7_rest = [ (0, 0, 0, 0, 0, 0, 0, 0, 0, 0) for x in range(8) ]
tbl32_0FC7_rest[6] =    (0, INS_SYSTEM, ADDRMETH_R | OPTYPE_v | OP_W, ARG_NONE, ARG_NONE, cpu_AMD64, "rdrand", 0, 0, 0)
tbl32_0FC7_rest[7] =    (0, INS_SYSTEM, ADDRMETH_R | OPTYPE_v | OP_W, ARG_NONE, ARG_NONE, cpu_AMD64, "rdseed", 0, 0, 0)

tbl32_660FC7_rest = list( tbl32_0FC7_rest )

tbl32_F30FC7_rest = list( tbl32_0FC7_rest )


desc_0FC7_00BF   = (tbl32_0FC7_00BF, 3, 3, 0x07, 0, 0xbf, TBL_0FC7_rest)
desc_0FC7_rest   = (tbl32_0FC7_rest, 3, 3, 0x07, 0xc0, 0xff)
desc_660FC7_00BF = (tbl32_660FC7_00BF, 3, 3, 0x07, 3, 0xff, TBL_660FC7_rest)
desc_660FC7_rest = (tbl32_660FC7_rest, 3, 3, 0x07, 0xc0, 0xff)
desc_F30FC7_00BF = (tbl32_F30FC7_00BF, 3, 3, 0x07, 3, 0xff, TBL_F30FC7_rest)
desc_F30FC7_rest = (tbl32_F30FC7_rest, 3, 3, 0x07, 0xc0, 0xff)


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_F30FC7_00BF = [ (0, 0, 0, 0, 0, 0, 0, 0, 0, 0) for x in range(8) ]
tbl32_F30FC7_00BF[6] = (0, INS_SYSTEM, ADDRMETH_M | OPTYPE_q | OP_W, ARG_NONE, ARG_NONE, cpu_AMD64, "vmxon", 0, 0, 0)

tbl32_F30FC7_rest = [ (0, 0, 0, 0, 0, 0, 0, 0, 0, 0) for x in range(8) ]


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
desc_80         = (tbl32_80,3,3,0x07,0,0xff)


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
desc_81         = (tbl32_81,3,3,0x07,0,0xff)


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
desc_82         = (tbl32_82,3,3,0x07,0,0xff)


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
desc_83         = (tbl32_83,3,3,0x07,0,0xff)


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
desc_C0         = (tbl32_C0,3,3,0x07,0,0xff)


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
desc_C1         = (tbl32_C1,3,3,0x07,0,0xff)


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_D0 = [
( 0, INS_ROL, ADDRMETH_E | OPTYPE_b | OP_W, OP_IMM | OP_R, ARG_NONE, cpu_80386, "rol", 0, 1, 0),
( 0, INS_ROR, ADDRMETH_E | OPTYPE_b | OP_W, OP_IMM | OP_R, ARG_NONE, cpu_80386, "ror", 0, 1, 0),
( 0, INS_ROL, ADDRMETH_E | OPTYPE_b | OP_W, OP_IMM | OP_R, ARG_NONE, cpu_80386, "rcl", 0, 1, 0),
( 0, INS_ROR, ADDRMETH_E | OPTYPE_b | OP_W, OP_IMM | OP_R, ARG_NONE, cpu_80386, "rcr", 0, 1, 0),
( 0, INS_SHL, ADDRMETH_E | OPTYPE_b | OP_W, OP_IMM | OP_R, ARG_NONE, cpu_80386, "shl", 0, 1, 0),
( 0, INS_SHR, ADDRMETH_E | OPTYPE_b | OP_W, OP_IMM | OP_R, ARG_NONE, cpu_80386, "shr", 0, 1, 0),
( 0, INS_SHL, ADDRMETH_E | OPTYPE_b | OP_W, OP_IMM | OP_R, ARG_NONE, cpu_80386, "sal", 0, 1, 0),
( 0, INS_SHR, ADDRMETH_E | OPTYPE_b | OP_W, OP_IMM | OP_R, ARG_NONE, cpu_80386, "sar", 0, 1, 0   )
]
desc_D0         = (tbl32_D0,3,3,0x07,0,0xff)

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
desc_D1         = (tbl32_D1,3,3,0x07,0,0xff)



"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_D2 = [
( 0, INS_ROL, ADDRMETH_E | OPTYPE_b | OP_W, OP_NOREX | OP_REG | OP_R, ARG_NONE, cpu_80386, "rol", 0, e_amd64_regs.REG_CL, 0),
( 0, INS_ROR, ADDRMETH_E | OPTYPE_b | OP_W, OP_NOREX | OP_REG | OP_R, ARG_NONE, cpu_80386, "ror", 0, e_amd64_regs.REG_CL, 0),
( 0, INS_ROL, ADDRMETH_E | OPTYPE_b | OP_W, OP_NOREX | OP_REG | OP_R, ARG_NONE, cpu_80386, "rcl", 0, e_amd64_regs.REG_CL, 0),
( 0, INS_ROR, ADDRMETH_E | OPTYPE_b | OP_W, OP_NOREX | OP_REG | OP_R, ARG_NONE, cpu_80386, "rcr", 0, e_amd64_regs.REG_CL, 0),
( 0, INS_SHL, ADDRMETH_E | OPTYPE_b | OP_W, OP_NOREX | OP_REG | OP_R, ARG_NONE, cpu_80386, "shl", 0, e_amd64_regs.REG_CL, 0),
( 0, INS_SHR, ADDRMETH_E | OPTYPE_b | OP_W, OP_NOREX | OP_REG | OP_R, ARG_NONE, cpu_80386, "shr", 0, e_amd64_regs.REG_CL, 0),
( 0, INS_SHL, ADDRMETH_E | OPTYPE_b | OP_W, OP_NOREX | OP_REG | OP_R, ARG_NONE, cpu_80386, "sal", 0, e_amd64_regs.REG_CL, 0),
( 0, INS_SHR, ADDRMETH_E | OPTYPE_b | OP_W, OP_NOREX | OP_REG | OP_R, ARG_NONE, cpu_80386, "sar", 0, e_amd64_regs.REG_CL, 0   )
]
desc_D2         = (tbl32_D2,3,3,0x07,0,0xff)

"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_D3 = [
( 0, INS_ROL, ADDRMETH_E | OPTYPE_v | OP_W, OP_NOREX | OP_REG | OP_R, ARG_NONE, cpu_80386, "rol", 0, e_amd64_regs.REG_CL, 0),
( 0, INS_ROR, ADDRMETH_E | OPTYPE_v | OP_W, OP_NOREX | OP_REG | OP_R, ARG_NONE, cpu_80386, "ror", 0, e_amd64_regs.REG_CL, 0),
( 0, INS_ROL, ADDRMETH_E | OPTYPE_v | OP_W, OP_NOREX | OP_REG | OP_R, ARG_NONE, cpu_80386, "rcl", 0, e_amd64_regs.REG_CL, 0),
( 0, INS_ROR, ADDRMETH_E | OPTYPE_v | OP_W, OP_NOREX | OP_REG | OP_R, ARG_NONE, cpu_80386, "rcr", 0, e_amd64_regs.REG_CL, 0),
( 0, INS_SHL, ADDRMETH_E | OPTYPE_v | OP_W, OP_NOREX | OP_REG | OP_R, ARG_NONE, cpu_80386, "shl", 0, e_amd64_regs.REG_CL, 0),
( 0, INS_SHR, ADDRMETH_E | OPTYPE_v | OP_W, OP_NOREX | OP_REG | OP_R, ARG_NONE, cpu_80386, "shr", 0, e_amd64_regs.REG_CL, 0),
( 0, INS_SHL, ADDRMETH_E | OPTYPE_v | OP_W, OP_NOREX | OP_REG | OP_R, ARG_NONE, cpu_80386, "sal", 0, e_amd64_regs.REG_CL, 0),
( 0, INS_SHR, ADDRMETH_E | OPTYPE_v | OP_W, OP_NOREX | OP_REG | OP_R, ARG_NONE, cpu_80386, "sar", 0, e_amd64_regs.REG_CL, 0   )
]
desc_D3         = (tbl32_D3,3,3,0x07,0,0xff)



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
desc_F6         = (tbl32_F6,3,3,0x07,0,0xff)


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_F7 = [
    (0, INS_TEST, ADDRMETH_E | OPTYPE_v | OP_R, ADDRMETH_I | OPTYPE_z | OP_R, ARG_NONE, cpu_80386, "test", 0, 0, 0),
    (0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    # ( 0, INS_TEST, ADDRMETH_E | OPTYPE_v | OP_R, ADDRMETH_I | OPTYPE_z | OP_SIGNED | OP_R, ARG_NONE, cpu_80386, "test", 0, 0, 0),
    (0, INS_NOT, ADDRMETH_E | OPTYPE_v | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "not", 0, 0, 0),
    (0, INS_NEG, ADDRMETH_E | OPTYPE_v | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "neg", 0, 0, 0),
    (0, INS_MUL, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "mul", 0, 0, 0),
    (0, INS_MUL, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "imul", 0, 0, 0),
    (0, INS_DIV, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "div", 0, 0, 0),
    (0, INS_DIV, ADDRMETH_E | OPTYPE_v | OP_R, ARG_NONE, ARG_NONE, cpu_80386, "idiv", 0, 0, 0)
]
desc_F7 = (tbl32_F7, 3, 3, 0x07, 0, 0xff)


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_FE = [
( 0, INS_INC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "inc", 0, 0, 0),  
( 0, INS_DEC, ADDRMETH_E | OPTYPE_b | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "dec", 0, 0, 0), 
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0   ),
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0   ),
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0   ),
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0   ),
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0   ),
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0   ) 
]
desc_FE         = (tbl32_FE,3,3,0x07,0,0xff)


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_FF = [
( 0, INS_INC, ADDRMETH_E | OPTYPE_v | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "inc", 0, 0, 0),  
( 0, INS_DEC, ADDRMETH_E | OPTYPE_v | OP_W, ARG_NONE, ARG_NONE, cpu_80386, "dec", 0, 0, 0),  
( 0, INS_CALL, ADDRMETH_E | OPTYPE_v | OP_X | OP_64AUTO , ARG_NONE, ARG_NONE, cpu_80386, "call", 0, 0, 0),  
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
( 0, INS_BRANCH, ADDRMETH_E | OPTYPE_v | OP_X | OP_64AUTO, ARG_NONE, ARG_NONE, cpu_80386, "jmp", 0, 0, 0),  # on amd64 this is jmp rnx
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
( 0, INS_PUSH, ADDRMETH_E | OPTYPE_v | OP_R | OP_64AUTO, ARG_NONE, ARG_NONE, cpu_80386, "push", 0, 0, 0),
( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0   ) 
]
desc_FF         = (tbl32_FF,3,3,0x07,0,0xff)


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
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fadd",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fadd",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fadd",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fadd",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fadd",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fadd",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fadd",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fadd",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST7,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmul",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmul",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmul",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmul",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmul",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmul",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmul",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmul",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST7,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcom",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcom",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcom",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcom",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcom",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcom",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcom",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcom",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST7,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomp",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomp",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomp",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomp",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomp",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomp",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomp",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomp",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST7,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsub",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsub",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsub",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsub",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsub",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsub",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsub",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsub",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST7,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubr",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubr",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubr",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubr",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubr",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubr",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubr",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubr",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST7,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdiv",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdiv",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdiv",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdiv",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdiv",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdiv",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdiv",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdiv",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST7,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivr",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivr",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivr",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivr",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivr",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivr",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivr",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivr",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST7,0 )
]
desc_fpuD8_00BF =(tbl32_fpuD8_00BF,3,3,0x07,0,0xbf, TBL_fpuD8_rest)
desc_fpuD8_rest =(tbl32_fpuD8_rest,3,0,0xff,0xc0,0xff)


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_fpuD9_00BF = [
(0, INS_FPU, ADDRMETH_M | OPTYPE_fs | OP_W, ARG_NONE, ARG_NONE, cpu_80387, "fld", 0, 0, 0),
(0, 0, ARG_NONE, ARG_NONE, ARG_NONE, cpu_80387, 0, 0, 0, 0),
(0, INS_FPU, ADDRMETH_M | OPTYPE_fs | OP_W, ARG_NONE, ARG_NONE, cpu_80387, "fst", 0, 0, 0),
(0, INS_FPU, ADDRMETH_M | OPTYPE_fs | OP_W, ARG_NONE, ARG_NONE, cpu_80387, "fstp", 0, 0, 0),
(0, INS_FPU, ADDRMETH_M | OPTYPE_fv | OP_W, ARG_NONE, ARG_NONE, cpu_80387, "fldenv", 0, 0, 0),
(0, INS_FPU, ADDRMETH_M | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80387, "fldcw", 0, 0, 0),
(0, INS_FPU, ADDRMETH_M | OPTYPE_fv | OP_W, ARG_NONE, ARG_NONE, cpu_80387, "fnstenv", 0, 0, 0),
(0, INS_FPU, ADDRMETH_M | OPTYPE_w | OP_W, ARG_NONE, ARG_NONE, cpu_80387, "fnstcw", 0, 0, 0)
]

"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_fpuD9_rest = [
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fld",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fld",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fld",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fld",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fld",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fld",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fld",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fld",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST7,0 ),  

( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fxch",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fxch",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fxch",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fxch",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fxch",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fxch",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fxch",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fxch",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST7,0 ),  
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
desc_fpuD9_00BF =(tbl32_fpuD9_00BF,3,3,0x07,0,0xbf, TBL_fpuD9_rest)
desc_fpuD9_rest =(tbl32_fpuD9_rest,3,0,0xff,0xc0,0xff)


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
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovb",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovb",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovb",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovb",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovb",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovb",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovb",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovb",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST7,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmove",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmove",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmove",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmove",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmove",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmove",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmove",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmove",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST7,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovbe",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovbe",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovbe",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovbe",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovbe",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovbe",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovbe",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovbe",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST7,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovu",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovu",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovu",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovu",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovu",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovu",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovu",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovu",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST7,0 ),  
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
desc_fpuDA_00BF =(tbl32_fpuDA_00BF,3,3,0x07,0,0xbf, TBL_fpuDA_rest)
desc_fpuDA_rest =(tbl32_fpuDA_rest,3,0,0xff,0xc0,0xff)

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
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnb",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnb",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnb",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnb",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnb",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnb",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnb",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnb",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST7,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovne",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovne",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovne",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovne",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovne",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovne",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovne",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovne",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST7,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnbe",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnbe",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnbe",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnbe",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnbe",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnbe",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnbe",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnbe",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST7,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnu",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnu",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnu",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnu",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnu",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnu",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnu",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcmovnu",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST7,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"fnclex",0,0,0 ),
( 0,INS_FPU,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,"fninit",0,0,0 ),
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucomi",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucomi",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucomi",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucomi",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucomi",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucomi",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucomi",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucomi",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST7,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomi",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomi",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomi",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomi",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomi",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomi",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomi",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomi",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST7,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 )
]
desc_fpuDB_00BF =(tbl32_fpuDB_00BF,3,3,0x07,0,0xbf, TBL_fpuDB_rest)
desc_fpuDB_rest =(tbl32_fpuDB_rest,3,0,0xff,0xc0,0xff)



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
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fadd",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fadd",e_amd64_regs.REG_ST1,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fadd",e_amd64_regs.REG_ST2,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fadd",e_amd64_regs.REG_ST3,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fadd",e_amd64_regs.REG_ST4,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fadd",e_amd64_regs.REG_ST5,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fadd",e_amd64_regs.REG_ST6,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fadd",e_amd64_regs.REG_ST7,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmul",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmul",e_amd64_regs.REG_ST1,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmul",e_amd64_regs.REG_ST2,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmul",e_amd64_regs.REG_ST3,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmul",e_amd64_regs.REG_ST4,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmul",e_amd64_regs.REG_ST5,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmul",e_amd64_regs.REG_ST6,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmul",e_amd64_regs.REG_ST7,e_amd64_regs.REG_ST0,0 ),  
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
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubr",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubr",e_amd64_regs.REG_ST1,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubr",e_amd64_regs.REG_ST2,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubr",e_amd64_regs.REG_ST3,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubr",e_amd64_regs.REG_ST4,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubr",e_amd64_regs.REG_ST5,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubr",e_amd64_regs.REG_ST6,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubr",e_amd64_regs.REG_ST7,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsub",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsub",e_amd64_regs.REG_ST1,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsub",e_amd64_regs.REG_ST2,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsub",e_amd64_regs.REG_ST3,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsub",e_amd64_regs.REG_ST4,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsub",e_amd64_regs.REG_ST5,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsub",e_amd64_regs.REG_ST6,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsub",e_amd64_regs.REG_ST7,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivr",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivr",e_amd64_regs.REG_ST1,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivr",e_amd64_regs.REG_ST2,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivr",e_amd64_regs.REG_ST3,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivr",e_amd64_regs.REG_ST4,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivr",e_amd64_regs.REG_ST5,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivr",e_amd64_regs.REG_ST6,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivr",e_amd64_regs.REG_ST7,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdiv",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdiv",e_amd64_regs.REG_ST1,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdiv",e_amd64_regs.REG_ST2,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdiv",e_amd64_regs.REG_ST3,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdiv",e_amd64_regs.REG_ST4,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdiv",e_amd64_regs.REG_ST5,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdiv",e_amd64_regs.REG_ST6,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdiv",e_amd64_regs.REG_ST7,e_amd64_regs.REG_ST0,0 )
]
desc_fpuDC_00BF =(tbl32_fpuDC_00BF,3,3,0x07,0,0xbf, TBL_fpuDC_rest)
desc_fpuDC_rest =(tbl32_fpuDC_rest,3,0,0xff,0xc0,0xff)


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_fpuDD_00BF = [
(0,INS_FPU,ADDRMETH_M|OPTYPE_fd|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fld",0,0,0 ),
(0,INS_FPU,ADDRMETH_M|OPTYPE_q|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fisttp",0,0,0),
(0,INS_FPU,ADDRMETH_M|OPTYPE_fd|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fst",0,0,0 ),
(0,INS_FPU,ADDRMETH_M|OPTYPE_fd|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fstp",0,0,0 ),
(0,INS_FPU,ADDRMETH_M|OPTYPE_fv|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"frstor",0,0,0 ),
(0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),
(0,INS_FPU,ADDRMETH_M|OPTYPE_fv|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fnsave",0,0,0 ),
(0,INS_FPU,ADDRMETH_M|OPTYPE_w|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fnstsw",0,0,0 )
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_fpuDD_rest = [
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"ffree",e_amd64_regs.REG_ST0,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"ffree",e_amd64_regs.REG_ST1,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"ffree",e_amd64_regs.REG_ST2,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"ffree",e_amd64_regs.REG_ST3,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"ffree",e_amd64_regs.REG_ST4,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"ffree",e_amd64_regs.REG_ST5,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"ffree",e_amd64_regs.REG_ST6,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"ffree",e_amd64_regs.REG_ST7,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fst",e_amd64_regs.REG_ST0,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fst",e_amd64_regs.REG_ST1,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fst",e_amd64_regs.REG_ST2,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fst",e_amd64_regs.REG_ST3,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fst",e_amd64_regs.REG_ST4,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fst",e_amd64_regs.REG_ST5,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fst",e_amd64_regs.REG_ST6,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fst",e_amd64_regs.REG_ST7,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fstp",e_amd64_regs.REG_ST0,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fstp",e_amd64_regs.REG_ST1,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fstp",e_amd64_regs.REG_ST2,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fstp",e_amd64_regs.REG_ST3,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fstp",e_amd64_regs.REG_ST4,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fstp",e_amd64_regs.REG_ST5,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fstp",e_amd64_regs.REG_ST6,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fstp",e_amd64_regs.REG_ST7,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucom",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucom",e_amd64_regs.REG_ST1,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucom",e_amd64_regs.REG_ST2,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucom",e_amd64_regs.REG_ST3,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucom",e_amd64_regs.REG_ST4,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucom",e_amd64_regs.REG_ST5,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucom",e_amd64_regs.REG_ST6,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucom",e_amd64_regs.REG_ST7,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fucomp",e_amd64_regs.REG_ST0,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fucomp",e_amd64_regs.REG_ST1,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fucomp",e_amd64_regs.REG_ST2,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fucomp",e_amd64_regs.REG_ST3,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fucomp",e_amd64_regs.REG_ST4,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fucomp",e_amd64_regs.REG_ST5,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fucomp",e_amd64_regs.REG_ST6,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fucomp",e_amd64_regs.REG_ST7,0,0 ),  
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
desc_fpuDD_00BF =(tbl32_fpuDD_00BF,3,3,0x07,0,0xbf, TBL_fpuDD_rest)
desc_fpuDD_rest =(tbl32_fpuDD_rest,3,0,0xff,0xc0,0xff)


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
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"faddp",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"faddp",e_amd64_regs.REG_ST1,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"faddp",e_amd64_regs.REG_ST2,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"faddp",e_amd64_regs.REG_ST3,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"faddp",e_amd64_regs.REG_ST4,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"faddp",e_amd64_regs.REG_ST5,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"faddp",e_amd64_regs.REG_ST6,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"faddp",e_amd64_regs.REG_ST7,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmulp",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmulp",e_amd64_regs.REG_ST1,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmulp",e_amd64_regs.REG_ST2,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmulp",e_amd64_regs.REG_ST3,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmulp",e_amd64_regs.REG_ST4,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmulp",e_amd64_regs.REG_ST5,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmulp",e_amd64_regs.REG_ST6,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fmulp",e_amd64_regs.REG_ST7,e_amd64_regs.REG_ST0,0 ),  
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
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubrp",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubrp",e_amd64_regs.REG_ST1,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubrp",e_amd64_regs.REG_ST2,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubrp",e_amd64_regs.REG_ST3,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubrp",e_amd64_regs.REG_ST4,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubrp",e_amd64_regs.REG_ST5,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubrp",e_amd64_regs.REG_ST6,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubrp",e_amd64_regs.REG_ST7,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubp",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubp",e_amd64_regs.REG_ST1,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubp",e_amd64_regs.REG_ST2,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubp",e_amd64_regs.REG_ST3,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubp",e_amd64_regs.REG_ST4,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubp",e_amd64_regs.REG_ST5,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubp",e_amd64_regs.REG_ST6,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fsubp",e_amd64_regs.REG_ST7,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivrp",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivrp",e_amd64_regs.REG_ST1,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivrp",e_amd64_regs.REG_ST2,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivrp",e_amd64_regs.REG_ST3,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivrp",e_amd64_regs.REG_ST4,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivrp",e_amd64_regs.REG_ST5,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivrp",e_amd64_regs.REG_ST6,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivrp",e_amd64_regs.REG_ST7,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivp",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivp",e_amd64_regs.REG_ST1,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivp",e_amd64_regs.REG_ST2,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivp",e_amd64_regs.REG_ST3,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivp",e_amd64_regs.REG_ST4,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivp",e_amd64_regs.REG_ST5,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivp",e_amd64_regs.REG_ST6,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fdivp",e_amd64_regs.REG_ST7,e_amd64_regs.REG_ST0,0 )
]
desc_fpuDE_00BF =(tbl32_fpuDE_00BF,3,3,0x07,0,0xbf, TBL_fpuDE_rest)
desc_fpuDE_rest =(tbl32_fpuDE_rest,3,0,0xff,0xc0,0xff)



"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_fpuDF_00BF = [ 
( 0,INS_FPU,ADDRMETH_M|OPTYPE_w|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fild",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_w|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fisttp",0,0,0),
( 0,INS_FPU,ADDRMETH_M|OPTYPE_w|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fist",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_w|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fistp",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_fb|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fbld",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_q|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fild",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_fb|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fbstp",0,0,0 ),  
( 0,INS_FPU,ADDRMETH_M|OPTYPE_q|OP_W,ARG_NONE,ARG_NONE,cpu_80387,"fistp",0,0,0 ) 
]


"""
(optable, optype, operand 0, operand 1, operand 2, CPU required, "opcodename", op0Register, op1Register, op2Register)
"""
tbl32_fpuDF_rest = [ 
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
( 0,INS_FPU,OP_REG,ARG_NONE,ARG_NONE,cpu_80387,"fnstsw",e_amd64_regs.REG_AX,0,0 ),
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucomip",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucomip",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucomip",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucomip",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucomip",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucomip",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucomip",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fucomip",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST7,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomip",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST0,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomip",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST1,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomip",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST2,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomip",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST3,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomip",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST4,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomip",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST5,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomip",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST6,0 ),  
( 0,INS_FPU,OP_REG | OP_W,OP_REG | OP_R,ARG_NONE,cpu_80387,"fcomip",e_amd64_regs.REG_ST0,e_amd64_regs.REG_ST7,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),  
( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,cpu_80387,0,0,0,0 ),
]
desc_fpuDF_00BF =(tbl32_fpuDF_00BF,3,3,0x07,0,0xbf, TBL_fpuDF_rest)
desc_fpuDF_rest =(tbl32_fpuDF_rest,3,0,0xff,0xc0,0xff)


tbl_INVALID = [ ( 0,0,ARG_NONE,ARG_NONE,ARG_NONE,0,0,0,0,0 ) ]
desc_INVALID    = (tbl_INVALID, 0, 0,0x00, 0, 0xff)

"""

Descriptor Information:
These values allow an opcode to be sliced and diced to make it fit correctly into the current lookup table.

    (tbl32_0F, 3, 0, 0xff, 0, 0xff),
    (tbl32_80, 3, 3, 0x07, 0, 0xff, 4),

           Table pointer
           argument count           typically 3, this allows a table to hold more arguments 
                                        (4 is common with AMD64 and Haswell)
           shift bits right         (eg.  >> 4 makes each line in the table valid for 16 
                                        numbers... ie 0xc0-0xcf are all one entry in the table)
           mask part of the byte    (eg.  & 0x7 only makes use of the 00000111 bits...)
           simple subtraction
           highest acceptable value
           tables86 entry to handle the falloff (from the previous check)

IMPORTANT: the decoder will assume the opcode is ultimately selected by bits in a MOD/RM 
    byte if the field in tabdesc[2] != 0xff
"""

# this generation must be placed after all tables are defined
tables86=[ None for x in range(256) ]

for nidx in range(1, len(tablenames)):
    name = tablenames[nidx]
    stub = name[6:]
    desc = "desc_" + stub
    const = "TBL_" + stub

    tables86[nidx] = globals()[desc]
