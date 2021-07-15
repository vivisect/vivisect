from typing import Dict
from .const import *
from envi import IF_NOFALL, IF_BRANCH, IF_CALL, IF_RET, IF_PRIV, IF_COND


# NOTE: e_ops and se_ops have different tuples due to legacy implementation

# tuple type clarification: Tuple[
#   mnemonic: str,
#   opcode: int,
#   mask: int,
#   form: int,
#   op_type: int,
#   condition: int,
#   operands_spec: Tuple[int],
#   iflags: int
# ]
e_ops: Dict[int, Dict[int, tuple]]= {
    # NOTE: Descending sort to detect less-specific masks from misidentification
    #       Strict ordering not necessary, but some issues can happen.
    #       Example: 0x7a000000: "e_bge" misidentified as 0x78000000: "e_b"
    0xfff30001: {
        # MG: changed mask from 0xffc00000 to 0xfff30001 to allow splitting of
        #     e_bc[l] into its specific conditional variants under one mask
        # 0x7a000000: "e_bc[l]",
        0x7a000000: ( "e_bge"      , 0x7A000000, 0x7A000000 | E_MASK_BD15, E_BD15 ,  INS_CJMP, COND_GE, (TYPE_CR, TYPE_JMP, TYPE_NONE, TYPE_NONE, TYPE_NONE), IF_COND | IF_BRANCH),
        0x7a000001: ( "e_bgel"     , 0x7A000001, 0x7A000001 | E_MASK_BD15, E_BD15 ,  INS_CCALL, COND_GE, (TYPE_CR, TYPE_JMP, TYPE_NONE, TYPE_NONE, TYPE_NONE), IF_COND | IF_CALL),
        0x7a010000: ( "e_ble"      , 0x7A010000, 0x7A010000 | E_MASK_BD15, E_BD15 ,  INS_CJMP, COND_LE, (TYPE_CR, TYPE_JMP, TYPE_NONE, TYPE_NONE, TYPE_NONE), IF_COND | IF_BRANCH),
        0x7a010001: ( "e_blel"     , 0x7A010001, 0x7A010001 | E_MASK_BD15, E_BD15 ,  INS_CCALL, COND_LE, (TYPE_CR, TYPE_JMP, TYPE_NONE, TYPE_NONE, TYPE_NONE), IF_COND | IF_CALL),
        0x7a020000: ( "e_bne"      , 0x7A020000, 0x7A020000 | E_MASK_BD15, E_BD15 ,  INS_CJMP, COND_NE, (TYPE_CR, TYPE_JMP, TYPE_NONE, TYPE_NONE, TYPE_NONE), IF_COND | IF_BRANCH),
        0x7a020001: ( "e_bnel"     , 0x7A020001, 0x7A020001 | E_MASK_BD15, E_BD15 ,  INS_CCALL, COND_NE, (TYPE_CR, TYPE_JMP, TYPE_NONE, TYPE_NONE, TYPE_NONE), IF_COND | IF_CALL),
        0x7a030000: ( "e_bns"      , 0x7A030000, 0x7A030000 | E_MASK_BD15, E_BD15 ,  INS_CJMP, COND_VC, (TYPE_CR, TYPE_JMP, TYPE_NONE, TYPE_NONE, TYPE_NONE), IF_COND | IF_BRANCH),
        0x7a030001: ( "e_bnsl"     , 0x7A030001, 0x7A030001 | E_MASK_BD15, E_BD15 ,  INS_CCALL, COND_VC, (TYPE_CR, TYPE_JMP, TYPE_NONE, TYPE_NONE, TYPE_NONE), IF_COND | IF_CALL),
        0x7a100000: ( "e_blt"      , 0x7A100000, 0x7A100000 | E_MASK_BD15, E_BD15 ,  INS_CJMP, COND_LT, (TYPE_CR, TYPE_JMP, TYPE_NONE, TYPE_NONE, TYPE_NONE), IF_COND | IF_BRANCH),
        0x7a100001: ( "e_bltl"     , 0x7A100001, 0x7A100001 | E_MASK_BD15, E_BD15 ,  INS_CCALL, COND_LT, (TYPE_CR, TYPE_JMP, TYPE_NONE, TYPE_NONE, TYPE_NONE), IF_COND | IF_CALL),
        0x7a110000: ( "e_bgt"      , 0x7A110000, 0x7A110000 | E_MASK_BD15, E_BD15 ,  INS_CJMP, COND_GT, (TYPE_CR, TYPE_JMP, TYPE_NONE, TYPE_NONE, TYPE_NONE), IF_COND | IF_BRANCH),
        0x7a110001: ( "e_bgtl"     , 0x7A110001, 0x7A110001 | E_MASK_BD15, E_BD15 ,  INS_CCALL, COND_GT, (TYPE_CR, TYPE_JMP, TYPE_NONE, TYPE_NONE, TYPE_NONE), IF_COND | IF_CALL),
        0x7a120000: ( "e_beq"      , 0x7A120000, 0x7A120000 | E_MASK_BD15, E_BD15 ,  INS_CJMP, COND_EQ, (TYPE_CR, TYPE_JMP, TYPE_NONE, TYPE_NONE, TYPE_NONE), IF_COND | IF_BRANCH),
        0x7a120001: ( "e_beql"     , 0x7A120001, 0x7A120001 | E_MASK_BD15, E_BD15 ,  INS_CCALL, COND_EQ, (TYPE_CR, TYPE_JMP, TYPE_NONE, TYPE_NONE, TYPE_NONE), IF_COND | IF_CALL),
        0x7a130000: ( "e_bso"      , 0x7A130000, 0x7A130000 | E_MASK_BD15, E_BD15 ,  INS_CJMP, COND_VS, (TYPE_CR, TYPE_JMP, TYPE_NONE, TYPE_NONE, TYPE_NONE), IF_COND | IF_BRANCH),
        0x7a130001: ( "e_bsol"     , 0x7A130001, 0x7A130001 | E_MASK_BD15, E_BD15 ,  INS_CCALL, COND_VS, (TYPE_CR, TYPE_JMP, TYPE_NONE, TYPE_NONE, TYPE_NONE), IF_COND | IF_CALL),
        0x7a200000: ( "e_bdnz"     , 0x7A200000, 0x7A200000 | E_MASK_BD15CTR, E_BD15, INS_CJMP, COND_EQ, (TYPE_NONE, TYPE_JMP, TYPE_NONE, TYPE_NONE, TYPE_NONE), IF_COND | IF_BRANCH),
        0x7a200001: ( "e_bdnzl"    , 0x7A200001, 0x7A200001 | E_MASK_BD15CTR, E_BD15, INS_CCALL, COND_EQ, (TYPE_NONE, TYPE_JMP, TYPE_NONE, TYPE_NONE, TYPE_NONE), IF_COND | IF_CALL),
        0x7a300000: ( "e_bdz"      , 0x7A300000, 0x7A300000 | E_MASK_BD15CTR, E_BD15, INS_CJMP, COND_NE, (TYPE_NONE, TYPE_JMP, TYPE_NONE, TYPE_NONE, TYPE_NONE), IF_COND | IF_BRANCH),
        0x7a300001: ( "e_bdzl"     , 0x7A300001, 0x7A300001 | E_MASK_BD15CTR, E_BD15, INS_CCALL, COND_NE, (TYPE_NONE, TYPE_JMP, TYPE_NONE, TYPE_NONE, TYPE_NONE), IF_COND | IF_CALL),
    },
    # NOTE: The following mask group is NOT in the VLE PEM, they're from EB696
    #       "New VLE Instructions for Improving Interrupt Handler Efficiency"
    # TODO: implement INS_(LOAD|STORE)MULT or split into specific operations
    # TODO: double check IFLAGS on these instructions; e_stmvsprw loads CR?
    0xffe0ff00: {
        0x18001000: ( "e_ldmvgprw" , 0x18001000, 0x18001000 | E_MASK_D8, E_D8VLS, INS_LOADMULT , COND_AL, (TYPE_REG, TYPE_MEM, TYPE_NONE, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x18001100: ( "e_stmvgprw" , 0x18001100, 0x18001100 | E_MASK_D8, E_D8VLS, INS_STOREMULT, COND_AL, (TYPE_REG, TYPE_MEM, TYPE_NONE, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x18201000: ( "e_ldmvsprw" , 0x18201000, 0x18201000 | E_MASK_D8, E_D8VLS, INS_LOADMULT , COND_AL, (TYPE_REG, TYPE_MEM, TYPE_NONE, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x18201100: ( "e_stmvsprw" , 0x18201100, 0x18201100 | E_MASK_D8, E_D8VLS, INS_STOREMULT, COND_AL, (TYPE_REG, TYPE_MEM, TYPE_NONE, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x18801000: ( "e_ldmvsrrw" , 0x18801000, 0x18801000 | E_MASK_D8, E_D8VLS, INS_LOADMULT , COND_AL, (TYPE_REG, TYPE_MEM, TYPE_NONE, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x18801100: ( "e_stmvsrrw" , 0x18801100, 0x18801100 | E_MASK_D8, E_D8VLS, INS_STOREMULT, COND_AL, (TYPE_REG, TYPE_MEM, TYPE_NONE, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x18a01000: ( "e_ldmvcsrrw", 0x18A01000, 0x18A01000 | E_MASK_D8, E_D8VLS, INS_LOADMULT , COND_AL, (TYPE_REG, TYPE_MEM, TYPE_NONE, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x18a01100: ( "e_stmvcsrrw", 0x18A01100, 0x18A01100 | E_MASK_D8, E_D8VLS, INS_STOREMULT, COND_AL, (TYPE_REG, TYPE_MEM, TYPE_NONE, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x18c01000: ( "e_ldmvdsrrw", 0x18C01000, 0x18C01000 | E_MASK_D8, E_D8VLS, INS_LOADMULT , COND_AL, (TYPE_REG, TYPE_MEM, TYPE_NONE, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x18c01100: ( "e_stmvdsrrw", 0x18C01100, 0x18C01100 | E_MASK_D8, E_D8VLS, INS_STOREMULT, COND_AL, (TYPE_REG, TYPE_MEM, TYPE_NONE, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
    },
    0xff80f800: {
        0x1800a800: ( "e_cmpi"     , 0x1800A800, 0x1800A800 | E_MASK_SCI8CR, E_SCI8CR, INS_CMP, COND_AL, (TYPE_CR, TYPE_REG, TYPE_SIMM, TYPE_IMM, TYPE_IMM), IFLAGS_NONE),
        0x1880a800: ( "e_cmpli"    , 0x1880A800, 0x1880A800 | E_MASK_SCI8CR, E_SCI8CR, INS_CMP, COND_AL, (TYPE_CR, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM), IFLAGS_NONE),
    },
    0xfc00ff00: {
        0x18000000: ( "e_lbzu"     , 0x18000000, 0x18000000 | E_MASK_D8  , E_D8   ,  INS_LOAD, COND_AL, (TYPE_REG, TYPE_MEM, TYPE_REG, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x18000100: ( "e_lhzu"     , 0x18000100, 0x18000100 | E_MASK_D8  , E_D8   ,  INS_LOAD, COND_AL, (TYPE_REG, TYPE_MEM, TYPE_REG, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x18000200: ( "e_lwzu"     , 0x18000200, 0x18000200 | E_MASK_D8  , E_D8   ,  INS_LOAD, COND_AL, (TYPE_REG, TYPE_MEM, TYPE_REG, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x18000300: ( "e_lhau"     , 0x18000300, 0x18000300 | E_MASK_D8  , E_D8   ,  INS_LOAD, COND_AL, (TYPE_REG, TYPE_MEM, TYPE_REG, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x18000400: ( "e_stbu"     , 0x18000400, 0x18000400 | E_MASK_D8  , E_D8   , INS_STORE, COND_AL, (TYPE_REG, TYPE_MEM, TYPE_REG, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x18000500: ( "e_sthu"     , 0x18000500, 0x18000500 | E_MASK_D8  , E_D8   , INS_STORE, COND_AL, (TYPE_REG, TYPE_MEM, TYPE_REG, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x18000600: ( "e_stwu"     , 0x18000600, 0x18000600 | E_MASK_D8  , E_D8   , INS_STORE, COND_AL, (TYPE_REG, TYPE_MEM, TYPE_REG, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x18000800: ( "e_lmw"      , 0x18000800, 0x18000800 | E_MASK_D8  , E_D8   ,   INS_MUL, COND_AL, (TYPE_REG, TYPE_MEM, TYPE_REG, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x18000900: ( "e_stmw"     , 0x18000900, 0x18000900 | E_MASK_D8  , E_D8   , INS_STORE, COND_AL, (TYPE_REG, TYPE_MEM, TYPE_REG, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
    },
    0xfc00f800: {
        # MG: added ops from from 0xfc00f800 into 0xfc00f800 in order to fit
        #     both kinds of op[.] variants without adding any masks
        0x18008000: ( "e_addi"     , 0x18008000, 0x18008000 | E_MASK_SCI8, E_SCI8 ,   INS_ADD, COND_AL, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM), IFLAGS_NONE),
        0x18008800: ( "e_addi."    , 0x18008800, 0x18008800 | E_MASK_SCI8, E_SCI8 ,   INS_ADD, COND_AL, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM), IF_RC),
        0x18009000: ( "e_addic"    , 0x18009000, 0x18009000 | E_MASK_SCI8, E_SCI8 ,   INS_ADD, COND_AL, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM), IFLAGS_NONE),
        0x18009800: ( "e_addic."   , 0x18009800, 0x18009800 | E_MASK_SCI8, E_SCI8 ,   INS_ADD, COND_AL, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM), IF_RC),
        0x1800B000: ( "e_subfic"   , 0x1800B000, 0x1800B000 | E_MASK_SCI8, E_SCI8 ,   INS_SUB, COND_AL, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM), IFLAGS_NONE),
        0x1800B800: ( "e_subfic."  , 0x1800B800, 0x1800B800 | E_MASK_SCI8, E_SCI8 ,   INS_SUB, COND_AL, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM), IF_RC),
        0x1800C000: ( "e_andi"     , 0x1800C000, 0x1800C000 | E_MASK_SCI8, E_SCI8I,   INS_AND, COND_AL, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM), IFLAGS_NONE),
        0x1800C800: ( "e_andi."    , 0x1800C800, 0x1800C800 | E_MASK_SCI8, E_SCI8I,   INS_AND, COND_AL, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM), IF_RC),
        0x1800D000: ( "e_ori"      , 0x1800D000, 0x1800D000 | E_MASK_SCI8, E_SCI8I,    INS_OR, COND_AL, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM), IFLAGS_NONE),
        # TODO: Decide how to handle simplification passes and whether the
        #       the two "simplified" tuples below are helpful
        # ( "e_nop"      , 0x1800D000, 0x1800D000                , E_NONE,  INS_NOP, COND_AL, (TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        # ( "e_mr"       , 0x1800D000, 0x1800D000 | E_MASK_SCI8_2, E_SCI8,  INS_MOV, COND_AL, (TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x1800D800: ( "e_ori."     , 0x1800D800, 0x1800D800 | E_MASK_SCI8, E_SCI8I,    INS_OR, COND_AL, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM), IF_RC),
        0x1800E000: ( "e_xori"     , 0x1800E000, 0x1800E000 | E_MASK_SCI8, E_SCI8I,   INS_XOR, COND_AL, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM), IFLAGS_NONE),
        0x1800E800: ( "e_xori."    , 0x1800E800, 0x1800E800 | E_MASK_SCI8, E_SCI8I,   INS_XOR, COND_AL, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM), IF_RC),
        # The rest of these have forms already in this mask
        0x1800a000: ( "e_mulli"    , 0x1800A000, 0x1800A000 | E_MASK_SCI8, E_SCI8 ,   INS_MUL, COND_AL, (TYPE_REG, TYPE_REG, TYPE_SIMM, TYPE_IMM, TYPE_IMM), IFLAGS_NONE),
        0x70008800: ( "e_add2i."   , 0x70008800, 0x70008800 | E_MASK_I16A, E_I16A ,   INS_ADD, COND_AL, (TYPE_IMM, TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE), IF_RC),
        0x70009000: ( "e_add2is"   , 0x70009000, 0x70009000 | E_MASK_I16A, E_I16A ,   INS_ADD, COND_AL, (TYPE_IMM, TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x70009800: ( "e_cmp16i"   , 0x70009800, 0x70009800 | E_MASK_I16A, E_I16A ,   INS_CMP, COND_AL, (TYPE_IMM, TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x7000a000: ( "e_mull2i"   , 0x7000A000, 0x7000A000 | E_MASK_I16A, E_I16A ,   INS_MUL, COND_AL, (TYPE_IMM, TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x7000a800: ( "e_cmpl16i"  , 0x7000A800, 0x7000A800 | E_MASK_I16A, E_I16A ,   INS_CMP, COND_AL, (TYPE_IMM, TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x7000b000: ( "e_cmph16i"  , 0x7000B000, 0x7000B000 | E_MASK_I16A, E_I16A ,   INS_CMP, COND_AL, (TYPE_IMM, TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x7000b800: ( "e_cmphl16i" , 0x7000B800, 0x7000B800 | E_MASK_I16A, E_I16A ,   INS_CMP, COND_AL, (TYPE_IMM, TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x7000c000: ( "e_or2i"     , 0x7000C000, 0x7000C000 | E_MASK_I16L, E_I16L ,    INS_OR, COND_AL, (TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x7000c800: ( "e_and2i."   , 0x7000C800, 0x7000C800 | E_MASK_I16L, E_I16L ,   INS_AND, COND_AL, (TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_NONE, TYPE_NONE), IF_RC),
        0x7000d000: ( "e_or2is"    , 0x7000D000, 0x7000D000 | E_MASK_I16L, E_I16L ,    INS_OR, COND_AL, (TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x7000e000: ( "e_lis"      , 0x7000E000, 0x7000E000 | E_MASK_I16L, E_I16L ,   INS_MOV, COND_AL, (TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x7000e800: ( "e_and2is."  , 0x7000E800, 0x7000E800 | E_MASK_I16L, E_I16L ,   INS_AND, COND_AL, (TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
    },
    0xfc008000: {
        0x70000000: ( "e_li"       , 0x70000000, 0x70000000 | E_MASK_LI20, E_LI20 ,   INS_MOV, COND_AL, (TYPE_REG, TYPE_SIMM, TYPE_NONE, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
    },
    0xfc0007ff: {
        # MG: Added bit 31 to mask because these either ignore the bit or use it
        #     as Rc, which allows inclusion of both op[.] variants
        0x7c00001c: ( "e_cmph"     , 0x7C00001C, 0x7C00001D | E_MASK_X   , E_XCR  ,   INS_CMP, COND_AL, (TYPE_CR, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x7c000020: ( "e_mcrf"     , 0x7C000020, 0x7C000020 | E_MASK_XL  , E_XLSP ,   INS_MOV, COND_AL, (TYPE_CR, TYPE_CR, TYPE_NONE, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x7c000042: ( "e_crnor"    , 0x7C000042, 0x7C000042 | E_MASK_XL  , E_XL   ,   INS_NOR, COND_AL, (TYPE_CR, TYPE_CR, TYPE_CR, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x7c00005c: ( "e_cmphl"    , 0x7C00005C, 0x7C00005D | E_MASK_X   , E_XCR  ,   INS_CMP, COND_AL, (TYPE_CR, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x7C000070: ( "e_slwi"     , 0x7C000070, 0x7C000070 | E_MASK_X   , E_XRA  ,   INS_SHL, COND_AL, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x7C000071: ( "e_slwi."    , 0x7C000071, 0x7C000071 | E_MASK_X   , E_XRA  ,   INS_SHL, COND_AL, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE), IF_RC),
        0x7c000102: ( "e_crandc"   , 0x7C000102, 0x7C000102 | E_MASK_XL  , E_XL   ,   INS_AND, COND_AL, (TYPE_CR, TYPE_CR, TYPE_CR, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x7c000182: ( "e_crxor"    , 0x7C000182, 0x7C000182 | E_MASK_XL  , E_XL   ,   INS_XOR, COND_AL, (TYPE_CR, TYPE_CR, TYPE_CR, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x7c0001c2: ( "e_crnand"   , 0x7C0001C2, 0x7C0001C2 | E_MASK_XL  , E_XL   ,   INS_AND, COND_AL, (TYPE_CR, TYPE_CR, TYPE_CR, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x7c000202: ( "e_crand"    , 0x7C000202, 0x7C000202 | E_MASK_XL  , E_XL   ,   INS_AND, COND_AL, (TYPE_CR, TYPE_CR, TYPE_CR, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x7C000230: ( "e_rlw"      , 0x7C000230, 0x7C000230 | E_MASK_X   , E_XRA  ,   INS_ROR, COND_AL, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x7C000231: ( "e_rlw."     , 0x7C000231, 0x7C000231 | E_MASK_X   , E_XRA  ,   INS_ROR, COND_AL, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE), IF_RC),
        0x7c000242: ( "e_creqv"    , 0x7C000242, 0x7C000242 | E_MASK_XL  , E_XL   ,   INS_AND, COND_AL, (TYPE_CR, TYPE_CR, TYPE_CR, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x7C000270: ( "e_rlwi"     , 0x7C000270, 0x7C000270 | E_MASK_X   , E_XRA  ,   INS_ROR, COND_AL, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x7C000271: ( "e_rlwi."    , 0x7C000271, 0x7C000271 | E_MASK_X   , E_XRA  ,   INS_ROR, COND_AL, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE), IF_RC),
        0x7c000342: ( "e_crorc"    , 0x7C000342, 0x7C000342 | E_MASK_XL  , E_XL   ,    INS_OR, COND_AL, (TYPE_CR, TYPE_CR, TYPE_CR, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x7c000382: ( "e_cror"     , 0x7C000382, 0x7C000382 | E_MASK_XL  , E_XL   ,    INS_OR, COND_AL, (TYPE_CR, TYPE_CR, TYPE_CR, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x7C000470: ( "e_srwi"     , 0x7C000470, 0x7C000470 | E_MASK_X   , E_XRA  ,   INS_SHR, COND_AL, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x7C000471: ( "e_srwi."    , 0x7C000471, 0x7C000471 | E_MASK_X   , E_XRA  ,   INS_SHR, COND_AL, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE), IF_RC),
    },
    0xfc000001: {
        0x74000000: ( "e_rlwimi"   , 0x74000000, 0x74000000 | E_MASK_M   , E_M    ,   INS_ROR, COND_AL, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM), IFLAGS_NONE),
        0x74000001: ( "e_rlwinm"   , 0x74000001, 0x74000001 | E_MASK_M   , E_M    ,   INS_ROR, COND_AL, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM), IFLAGS_NONE),
        # MG: I moved "e_b[l]" 0x78000000 from the above bitmask and split it into these two
        0x78000000: ( "e_b"        , 0x78000000, 0x78000000 | E_MASK_BD24, E_BD24 ,   INS_JMP, COND_AL, (TYPE_JMP, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE), IF_BRANCH | IF_NOFALL),
        0x78000001: ( "e_bl"       , 0x78000001, 0x78000001 | E_MASK_BD24, E_BD24 ,  INS_CALL, COND_AL, (TYPE_JMP, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE), IF_CALL),
    },
    0xfc000000: {
        0x1c000000: ( "e_add16i"   , 0x1C000000, 0x1F000000 | E_MASK_D   , E_D    ,   INS_ADD, COND_AL, (TYPE_REG, TYPE_REG, TYPE_SIMM, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x30000000: ( "e_lbz"      , 0x30000000, 0x30000000 | E_MASK_D   , E_D    ,  INS_LOAD, COND_AL, (TYPE_REG, TYPE_MEM, TYPE_REG, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x34000000: ( "e_stb"      , 0x34000000, 0x34000000 | E_MASK_D   , E_D    , INS_STORE, COND_AL, (TYPE_REG, TYPE_MEM, TYPE_REG, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x38000000: ( "e_lha"      , 0x38000000, 0x38000000 | E_MASK_D   , E_D    ,  INS_LOAD, COND_AL, (TYPE_REG, TYPE_MEM, TYPE_REG, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x50000000: ( "e_lwz"      , 0x50000000, 0x53000000 | E_MASK_D   , E_D    ,  INS_LOAD, COND_AL, (TYPE_REG, TYPE_MEM, TYPE_REG, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x54000000: ( "e_stw"      , 0x54000000, 0x56000000 | E_MASK_D   , E_D    , INS_STORE, COND_AL, (TYPE_REG, TYPE_MEM, TYPE_REG, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x58000000: ( "e_lhz"      , 0x58000000, 0x58000000 | E_MASK_D   , E_D    ,  INS_LOAD, COND_AL, (TYPE_REG, TYPE_MEM, TYPE_REG, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
        0x5c000000: ( "e_sth"      , 0x5C000000, 0x5C000000 | E_MASK_D   , E_D    , INS_STORE, COND_AL, (TYPE_REG, TYPE_MEM, TYPE_REG, TYPE_NONE, TYPE_NONE), IFLAGS_NONE),
    },
}



# tuple type clarification: Tuple[
#   name: str,
#   op: int,
#   mask: int,
#   num_fields: int,
#   op_type: int,
#   condition: int,
#   oper_spec: Tuple[Tuple[int]],
#   iflags: int
# ]
se_ops: Dict[int, Dict[int, tuple]] = {
    0xffff: {
        0x0000: ( "se_illegal", 0x0000, 0x0000, 0,   INS_ILL, COND_NV, ((0), (0), (0), (0), (0)), IF_NOFALL),
        0x0001: ( "se_isync"  , 0x0001, 0x0001, 0,  INS_SYNC, COND_AL, ((0), (0), (0), (0), (0)), IFLAGS_NONE),
        0x0002: ( "se_sc"     , 0x0002, 0x0002, 0,   INS_SWI, COND_AL, ((0), (0), (0), (0), (0)), IFLAGS_NONE),
        0x0004: ( "se_blr"    , 0x0004, 0x0004, 0,   INS_RET, COND_AL, ((0), (0), (0), (0), (0)), IF_RET | IF_NOFALL),
        0x0005: ( "se_blrl"   , 0x0005, 0x0005, 0,   INS_RET, COND_AL, ((0), (0), (0), (0), (0)), IF_RET | IF_NOFALL),
        0x0006: ( "se_bctr"   , 0x0006, 0x0006, 0,  INS_RJMP, COND_AL, ((0), (0), (0), (0), (0)), IF_BRANCH | IF_NOFALL),
        0x0007: ( "se_bctrl"  , 0x0007, 0x0007, 0, INS_RCALL, COND_AL, ((0), (0), (0), (0), (0)), IF_CALL),
        0x0008: ( "se_rfi"    , 0x0008, 0x0008, 0,  INS_TRAP, COND_AL, ((0), (0), (0), (0), (0)), IF_RET | IF_NOFALL | IF_PRIV),
        0x0009: ( "se_rfci"   , 0x0009, 0x0009, 0,  INS_TRAP, COND_AL, ((0), (0), (0), (0), (0)), IF_RET | IF_NOFALL | IF_PRIV),
        0x000a: ( "se_rfdi"   , 0x000A, 0x000A, 0,  INS_TRAP, COND_AL, ((0), (0), (0), (0), (0)), IF_RET | IF_NOFALL | IF_PRIV),
        0x000b: ( "se_rfmci"  , 0x000B, 0x000B, 0,  INS_TRAP, COND_AL, ((0), (0), (0), (0), (0)), IF_RET | IF_NOFALL | IF_PRIV),
    },
    0xfff0: {
        0x0020: ( "se_not"    , 0x0020, 0x002F, 1,   INS_NOT, COND_AL, ((0x000F,  0,  0,  0, 0, TYPE_REG_SE), (0), (0), (0), (0)), IFLAGS_NONE),
        0x0030: ( "se_neg"    , 0x0030, 0x003F, 1,   INS_NOT, COND_AL, ((0x000F,  0,  0,  0, 0, TYPE_REG_SE), (0), (0), (0), (0)), IFLAGS_NONE),
        0x0080: ( "se_mflr"   , 0x0080, 0x008F, 1,   INS_MOV, COND_AL, ((0x000F,  0,  0,  0, 0, TYPE_REG_SE), (0), (0), (0), (0)), IFLAGS_NONE),
        0x0090: ( "se_mtlr"   , 0x0090, 0x009F, 1,   INS_MOV, COND_AL, ((0x000F,  0,  0,  0, 0, TYPE_REG_SE), (0), (0), (0), (0)), IFLAGS_NONE),
        0x00a0: ( "se_mfctr"  , 0x00A0, 0x00AF, 1,   INS_MOV, COND_AL, ((0x000F,  0,  0,  0, 0, TYPE_REG_SE), (0), (0), (0), (0)), IFLAGS_NONE),
        0x00b0: ( "se_mtctr"  , 0x00B0, 0x00BF, 1,   INS_MOV, COND_AL, ((0x000F,  0,  0,  0, 0, TYPE_REG_SE), (0), (0), (0), (0)), IFLAGS_NONE),
        0x00c0: ( "se_extzb"  , 0x00C0, 0x00CF, 1,    INS_OR, COND_AL, ((0x000F,  0,  0,  0, 0, TYPE_REG_SE), (0), (0), (0), (0)), IFLAGS_NONE),
        0x00d0: ( "se_extsb"  , 0x00D0, 0x00DF, 1,    INS_OR, COND_AL, ((0x000F,  0,  0,  0, 0, TYPE_REG_SE), (0), (0), (0), (0)), IFLAGS_NONE),
        0x00e0: ( "se_extzh"  , 0x00E0, 0x00EF, 1,    INS_OR, COND_AL, ((0x000F,  0,  0,  0, 0, TYPE_REG_SE), (0), (0), (0), (0)), IFLAGS_NONE),
        0x00f0: ( "se_extsh"  , 0x00F0, 0x00FF, 1,    INS_OR, COND_AL, ((0x000F,  0,  0,  0, 0, TYPE_REG_SE), (0), (0), (0), (0)), IFLAGS_NONE),
    },
    0xff00: {
        0x0100: ( "se_mr"     , 0x0100, 0x01FF, 2,   INS_MOV, COND_AL, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  0,  0, TYPE_REG_SE), (0), (0), (0)), IFLAGS_NONE),
        0x0200: ( "se_mtar"   , 0x0200, 0x02FF, 2,   INS_MOV, COND_AL, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  8,  0, TYPE_REG), (0), (0), (0)), IFLAGS_NONE),
        0x0300: ( "se_mfar"   , 0x0300, 0x03FF, 2,   INS_MOV, COND_AL, ((0x00F0,  4,  0,  8, 1, TYPE_REG), (0x000F,  0,  0,  0,  0, TYPE_REG_SE), (0), (0), (0)), IFLAGS_NONE),
        0x0400: ( "se_add"    , 0x0400, 0x04FF, 2,   INS_ADD, COND_AL, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  0,  0, TYPE_REG_SE), (0), (0), (0)), IFLAGS_NONE),
        0x0500: ( "se_mullw"  , 0x0500, 0x05FF, 2,   INS_MUL, COND_AL, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  0,  0, TYPE_REG_SE), (0), (0), (0)), IFLAGS_NONE),
        0x0600: ( "se_sub"    , 0x0600, 0x06FF, 2,   INS_SUB, COND_AL, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  0,  0, TYPE_REG_SE), (0), (0), (0)), IFLAGS_NONE),
        0x0700: ( "se_subf"   , 0x0700, 0x07FF, 2,   INS_SUB, COND_AL, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  0,  0, TYPE_REG_SE), (0), (0), (0)), IFLAGS_NONE),
        0x0c00: ( "se_cmp"    , 0x0C00, 0x0CFF, 2,   INS_CMP, COND_AL, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  0,  0, TYPE_REG_SE), (0), (0), (0)), IFLAGS_NONE),
        0x0d00: ( "se_cmpl"   , 0x0D00, 0x0DFF, 2,   INS_CMP, COND_AL, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  0,  0, TYPE_REG_SE), (0), (0), (0)), IFLAGS_NONE),
        0x0e00: ( "se_cmph"   , 0x0E00, 0x0EFF, 2,   INS_CMP, COND_AL, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  0,  0, TYPE_REG_SE), (0), (0), (0)), IFLAGS_NONE),
        0x0f00: ( "se_cmphl"  , 0x0F00, 0x0FFF, 2,   INS_CMP, COND_AL, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  0,  0, TYPE_REG_SE), (0), (0), (0)), IFLAGS_NONE),
        0x4000: ( "se_srw"    , 0x4000, 0x40FF, 2,   INS_SHR, COND_AL, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  0,  0, TYPE_REG_SE), (0), (0), (0)), IFLAGS_NONE),
        0x4100: ( "se_sraw"   , 0x4100, 0x41FF, 2,   INS_SHR, COND_AL, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  0,  0, TYPE_REG_SE), (0), (0), (0)), IFLAGS_NONE),
        0x4200: ( "se_slw"    , 0x4200, 0x42FF, 2,   INS_SHL, COND_AL, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  0,  0, TYPE_REG_SE), (0), (0), (0)), IFLAGS_NONE),
        0x4400: ( "se_or"     , 0x4400, 0x44FF, 2,    INS_OR, COND_AL, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  0,  0, TYPE_REG_SE), (0), (0), (0)), IFLAGS_NONE),
        0x4500: ( "se_andc"   , 0x4500, 0x45FF, 2,   INS_AND, COND_AL, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  0,  0, TYPE_REG_SE), (0), (0), (0)), IFLAGS_NONE),
        0x4600: ( "se_and"    , 0x4600, 0x46FF, 2,   INS_AND, COND_AL, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  0,  0, TYPE_REG_SE), (0), (0), (0)), IFLAGS_NONE),
        0x4700: ( "se_and."   , 0x4700, 0x47FF, 2,   INS_AND, COND_AL, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  0,  0, TYPE_REG_SE), (0), (0), (0)), IF_RC),
        # MG: Moved se_b into this mask to include both variants of se_b[l]
        #     in the same mask
        0xe800: ( "se_b"      , 0xE800, 0xE8FF, 1,   INS_JMP, COND_AL, ((0x00FF,  0,  1,  0, 0, TYPE_JMP), (0), (0), (0), (0)), IF_BRANCH | IF_NOFALL),
        0xe900: ( "se_bl"     , 0xE900, 0xE9FF, 1,  INS_CALL, COND_AL, ((0x00FF,  0,  1,  0, 0, TYPE_JMP), (0), (0), (0), (0)), IF_CALL),
        # MG: Moved all conditional variants of se_bc from 0xf800 to here since
        #     they are selected by via this mask
        # TODO: is BO16 (bit 5) correct to mask here? it seems to be used to control mnemonic choice...
        #0xe000: ( "se_bc"     , 0xE000, 0xE7FF, 2,  INS_CJMP, COND_VS, ((0x0700,  8,  0, 32, 0, TYPE_JMP), (0x00FF,  0,  1,  0,  1, TYPE_IMM), (0), (0), (0)), IF_COND | IF_BRANCH),
        0xe000: ( "se_bge"    , 0xE000, 0xE0FF, 1,  INS_CJMP, COND_GE, ((0x00FF,  0,  1,  0, 0, TYPE_JMP), (0), (0), (0), (0)), IF_COND | IF_BRANCH),
        0xe100: ( "se_ble"    , 0xE000, 0xE1FF, 1,  INS_CJMP, COND_LE, ((0x00FF,  0,  1,  0, 0, TYPE_JMP), (0), (0), (0), (0)), IF_COND | IF_BRANCH),
        0xe200: ( "se_bne"    , 0xE000, 0xE2FF, 1,  INS_CJMP, COND_NE, ((0x00FF,  0,  1,  0, 0, TYPE_JMP), (0), (0), (0), (0)), IF_COND | IF_BRANCH),
        0xe300: ( "se_bns"    , 0xE000, 0xE3FF, 1,  INS_CJMP, COND_VC, ((0x00FF,  0,  1,  0, 0, TYPE_JMP), (0), (0), (0), (0)), IF_COND | IF_BRANCH),
        0xe400: ( "se_blt"    , 0xE000, 0xE4FF, 1,  INS_CJMP, COND_LT, ((0x00FF,  0,  1,  0, 0, TYPE_JMP), (0), (0), (0), (0)), IF_COND | IF_BRANCH),
        0xe500: ( "se_bgt"    , 0xE000, 0xE5FF, 1,  INS_CJMP, COND_GT, ((0x00FF,  0,  1,  0, 0, TYPE_JMP), (0), (0), (0), (0)), IF_COND | IF_BRANCH),
        0xe600: ( "se_beq"    , 0xE000, 0xE6FF, 1,  INS_CJMP, COND_EQ, ((0x00FF,  0,  1,  0, 0, TYPE_JMP), (0), (0), (0), (0)), IF_COND | IF_BRANCH),
        0xe700: ( "se_bso"    , 0xE000, 0xE7FF, 1,  INS_CJMP, COND_VS, ((0x00FF,  0,  1,  0, 0, TYPE_JMP), (0), (0), (0), (0)), IF_COND | IF_BRANCH),
    },
    0xfe00: {
        0x2000: ( "se_addi"   , 0x2000, 0x21FF, 2,   INS_ADD, COND_AL, ((0x01F0,  4,  0,  1, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG_SE), (0), (0), (0)), IFLAGS_NONE),
        0x2200: ( "se_cmpli"  , 0x2200, 0x23FF, 2,   INS_CMP, COND_AL, ((0x01F0,  4,  0,  1, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG_SE), (0), (0), (0)), IFLAGS_NONE),
        0x2400: ( "se_subi"   , 0x2400, 0x25FF, 2,   INS_SUB, COND_AL, ((0x01F0,  4,  0,  1, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG_SE), (0), (0), (0)), IFLAGS_NONE),
        0x2600: ( "se_subi."  , 0x2600, 0x27FF, 2,   INS_SUB, COND_AL, ((0x01F0,  4,  0,  1, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG_SE), (0), (0), (0)), IFLAGS_NONE),
        0x2a00: ( "se_cmpi"   , 0x2A00, 0x2BFF, 2,   INS_CMP, COND_AL, ((0x01F0,  4,  0,  0, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG_SE), (0), (0), (0)), IFLAGS_NONE),
        0x2c00: ( "se_bmaski" , 0x2C00, 0x2DFF, 2,    INS_OR, COND_AL, ((0x01F0,  4,  0,  0, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG_SE), (0), (0), (0)), IFLAGS_NONE),
        0x2e00: ( "se_andi"   , 0x2E00, 0x2FFF, 2,   INS_AND, COND_AL, ((0x01F0,  4,  0,  0, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG_SE), (0), (0), (0)), IFLAGS_NONE),
        0x6000: ( "se_bclri"  , 0x6000, 0x61FF, 2,    INS_OR, COND_AL, ((0x01F0,  4,  0,  0, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG_SE), (0), (0), (0)), IFLAGS_NONE),
        0x6200: ( "se_bgeni"  , 0x6200, 0x63FF, 2,    INS_OR, COND_AL, ((0x01F0,  4,  0,  0, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG_SE), (0), (0), (0)), IFLAGS_NONE),
        0x6400: ( "se_bseti"  , 0x6400, 0x65FF, 2,    INS_OR, COND_AL, ((0x01F0,  4,  0,  0, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG_SE), (0), (0), (0)), IFLAGS_NONE),
        0x6600: ( "se_btsti"  , 0x6600, 0x67FF, 2,    INS_OR, COND_AL, ((0x01F0,  4,  0,  0, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG_SE), (0), (0), (0)), IFLAGS_NONE),
        0x6800: ( "se_srwi"   , 0x6800, 0x69FF, 2,   INS_SHR, COND_AL, ((0x01F0,  4,  0,  0, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG_SE), (0), (0), (0)), IFLAGS_NONE),
        0x6a00: ( "se_srawi"  , 0x6A00, 0x6BFF, 2,   INS_SHR, COND_AL, ((0x01F0,  4,  0,  0, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG_SE), (0), (0), (0)), IFLAGS_NONE),
        0x6c00: ( "se_slwi"   , 0x6C00, 0x6DFF, 2,   INS_SHL, COND_AL, ((0x01F0,  4,  0,  0, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG_SE), (0), (0), (0)), IFLAGS_NONE),
    },
    0xf800: {
        # NOTE: Form IM7's bit depiction in VLE PEM (Fig A-5) is incorrect,
        #       see se_li description on page 3-42 (page 74 in PDF)
        0x4800: ( "se_li"     , 0x4800, 0x4FFF, 2,   INS_MOV, COND_AL, ((0x07F0,  4,  0,  0, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG_SE), (0), (0), (0)), IFLAGS_NONE),
    },
    0xf000: {
        0x8000: ( "se_lbz"    , 0x8000, 0x8FFF, 3,  INS_LOAD, COND_AL, ((0x0F00,  8,  0,  0, 2, TYPE_IMM), (0x00F0,  4,  0,  0,  0, TYPE_REG_SE), (0x000F,  0,  0,  0,  1, TYPE_MEM), (0), (0)), IFLAGS_NONE),
        0x9000: ( "se_stb"    , 0x9000, 0x9FFF, 3, INS_STORE, COND_AL, ((0x0F00,  8,  0,  0, 2, TYPE_IMM), (0x00F0,  4,  0,  0,  0, TYPE_REG_SE), (0x000F,  0,  0,  0,  1, TYPE_MEM), (0), (0)), IFLAGS_NONE),
        0xa000: ( "se_lhz"    , 0xA000, 0xAFFF, 3,  INS_LOAD, COND_AL, ((0x0F00,  7,  0,  0, 2, TYPE_IMM), (0x00F0,  4,  0,  0,  0, TYPE_REG_SE), (0x000F,  0,  0,  0,  1, TYPE_MEM), (0), (0)), IFLAGS_NONE),
        0xb000: ( "se_sth"    , 0xB000, 0xBFFF, 3, INS_STORE, COND_AL, ((0x0F00,  7,  0,  0, 2, TYPE_IMM), (0x00F0,  4,  0,  0,  0, TYPE_REG_SE), (0x000F,  0,  0,  0,  1, TYPE_MEM), (0), (0)), IFLAGS_NONE),
        0xc000: ( "se_lwz"    , 0xC000, 0xCFFF, 3,  INS_LOAD, COND_AL, ((0x0F00,  6,  0,  0, 2, TYPE_IMM), (0x00F0,  4,  0,  0,  0, TYPE_REG_SE), (0x000F,  0,  0,  0,  1, TYPE_MEM), (0), (0)), IFLAGS_NONE),
        0xd000: ( "se_stw"    , 0xD000, 0xDFFF, 3, INS_STORE, COND_AL, ((0x0F00,  6,  0,  0, 2, TYPE_IMM), (0x00F0,  4,  0,  0,  0, TYPE_REG_SE), (0x000F,  0,  0,  0,  1, TYPE_MEM), (0), (0)), IFLAGS_NONE),
    },
}
