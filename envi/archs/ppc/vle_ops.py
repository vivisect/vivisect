from typing import Dict
from .const import *
from envi import IF_NOFALL, IF_BRANCH, IF_CALL, IF_RET, IF_PRIV, IF_COND


# NOTE: e_ops and se_ops have different tuples due to legacy implementation

# tuple type clarification: Tuple[
#   mnemonic: str,
#   form: int,
#   op_type: int,
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
        0x7a000000: ( "e_bge"      ,  E_BD15 ,  INS_BGE, (TYPE_CR, TYPE_JMP), IF_COND | IF_BRANCH),
        0x7a000001: ( "e_bgel"     ,  E_BD15 ,  INS_BGEL, (TYPE_CR, TYPE_JMP), IF_COND | IF_CALL),
        0x7a010000: ( "e_ble"      ,  E_BD15 ,  INS_BLE, (TYPE_CR, TYPE_JMP), IF_COND | IF_BRANCH),
        0x7a010001: ( "e_blel"     ,  E_BD15 ,  INS_BLEL, (TYPE_CR, TYPE_JMP), IF_COND | IF_CALL),
        0x7a020000: ( "e_bne"      ,  E_BD15 ,  INS_BNE, (TYPE_CR, TYPE_JMP), IF_COND | IF_BRANCH),
        0x7a020001: ( "e_bnel"     ,  E_BD15 ,  INS_BNEL, (TYPE_CR, TYPE_JMP), IF_COND | IF_CALL),
        0x7a030000: ( "e_bns"      ,  E_BD15 ,  INS_BNS, (TYPE_CR, TYPE_JMP), IF_COND | IF_BRANCH),
        0x7a030001: ( "e_bnsl"     ,  E_BD15 ,  INS_BNSL, (TYPE_CR, TYPE_JMP), IF_COND | IF_CALL),
        0x7a100000: ( "e_blt"      ,  E_BD15 ,  INS_BLT, (TYPE_CR, TYPE_JMP), IF_COND | IF_BRANCH),
        0x7a100001: ( "e_bltl"     ,  E_BD15 ,  INS_BLTL, (TYPE_CR, TYPE_JMP), IF_COND | IF_CALL),
        0x7a110000: ( "e_bgt"      ,  E_BD15 ,  INS_BGT, (TYPE_CR, TYPE_JMP), IF_COND | IF_BRANCH),
        0x7a110001: ( "e_bgtl"     ,  E_BD15 ,  INS_BGTL, (TYPE_CR, TYPE_JMP), IF_COND | IF_CALL),
        0x7a120000: ( "e_beq"      ,  E_BD15 ,  INS_BEQ, (TYPE_CR, TYPE_JMP), IF_COND | IF_BRANCH),
        0x7a120001: ( "e_beql"     ,  E_BD15 ,  INS_BEQL, (TYPE_CR, TYPE_JMP), IF_COND | IF_CALL),
        0x7a130000: ( "e_bso"      ,  E_BD15 ,  INS_BSO, (TYPE_CR, TYPE_JMP), IF_COND | IF_BRANCH),
        0x7a130001: ( "e_bsol"     ,  E_BD15 ,  INS_BSOL, (TYPE_CR, TYPE_JMP), IF_COND | IF_CALL),
        0x7a200000: ( "e_bdnz"     ,  E_BD15, INS_BDNZ, (TYPE_NONE, TYPE_JMP), IF_COND | IF_BRANCH),
        0x7a200001: ( "e_bdnzl"    ,  E_BD15, INS_BDNZL, (TYPE_NONE, TYPE_JMP), IF_COND | IF_CALL),
        0x7a300000: ( "e_bdz"      ,  E_BD15, INS_BDZ, (TYPE_NONE, TYPE_JMP), IF_COND | IF_BRANCH),
        0x7a300001: ( "e_bdzl"     ,  E_BD15, INS_BDZL, (TYPE_NONE, TYPE_JMP), IF_COND | IF_CALL),
    },
    # NOTE: The following mask group is NOT in the VLE PEM, they're from EB696
    #       "New VLE Instructions for Improving Interrupt Handler Efficiency"
    # TODO: implement INS_(LOAD|STORE)MULT or split into specific operations
    # TODO: double check IFLAGS on these instructions; e_stmvsprw loads CR?
    0xffe0ff00: {
        0x18001000: ( "e_ldmvgprw" ,  E_D8VLS, INS_E_LDMVGPRW, (TYPE_REG, TYPE_MEM), IFLAGS_NONE),
        0x18001100: ( "e_stmvgprw" ,  E_D8VLS, INS_E_STMVGPRW, (TYPE_REG, TYPE_MEM), IFLAGS_NONE),
        0x18201000: ( "e_ldmvsprw" ,  E_D8VLS, INS_E_LDMVSPRW , (TYPE_REG, TYPE_MEM), IFLAGS_NONE),
        0x18201100: ( "e_stmvsprw" ,  E_D8VLS, INS_E_STMVSPRW, (TYPE_REG, TYPE_MEM), IFLAGS_NONE),
        0x18801000: ( "e_ldmvsrrw" ,  E_D8VLS, INS_E_LDMVSRRW , (TYPE_REG, TYPE_MEM), IFLAGS_NONE),
        0x18801100: ( "e_stmvsrrw" ,  E_D8VLS, INS_E_STMVSRRW, (TYPE_REG, TYPE_MEM), IFLAGS_NONE),
        0x18a01000: ( "e_ldmvcsrrw",  E_D8VLS, INS_E_LDMVCSRRW , (TYPE_REG, TYPE_MEM), IFLAGS_NONE),
        0x18a01100: ( "e_stmvcsrrw",  E_D8VLS, INS_E_STMVCSRRW, (TYPE_REG, TYPE_MEM), IFLAGS_NONE),
        0x18c01000: ( "e_ldmvdsrrw",  E_D8VLS, INS_E_LDMVDSRRW , (TYPE_REG, TYPE_MEM), IFLAGS_NONE),
        0x18c01100: ( "e_stmvdsrrw",  E_D8VLS, INS_E_STMVDSRRW, (TYPE_REG, TYPE_MEM), IFLAGS_NONE),
    },
    0xff80f800: {
        0x1800a800: ( "e_cmpi"     ,  E_SCI8CR, INS_CMP, (TYPE_CR, TYPE_REG, TYPE_SIMM32, TYPE_IMM, TYPE_IMM), IFLAGS_NONE),
        0x1880a800: ( "e_cmpli"    ,  E_SCI8CR, INS_CMPL, (TYPE_CR, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM), IFLAGS_NONE),
    },
    0xfc00ff00: {
        0x18000000: ( "e_lbzu"     ,  E_D8   ,  INS_LBZU, (TYPE_REG, TYPE_MEM, TYPE_REG), IFLAGS_NONE),
        0x18000100: ( "e_lhzu"     ,  E_D8   ,  INS_LHZU, (TYPE_REG, TYPE_MEM, TYPE_REG), IFLAGS_NONE),
        0x18000200: ( "e_lwzu"     ,  E_D8   ,  INS_LWZU, (TYPE_REG, TYPE_MEM, TYPE_REG), IFLAGS_NONE),
        0x18000300: ( "e_lhau"     ,  E_D8   ,  INS_LHAU, (TYPE_REG, TYPE_MEM, TYPE_REG), IFLAGS_NONE),
        0x18000400: ( "e_stbu"     ,  E_D8   , INS_STBU, (TYPE_REG, TYPE_MEM, TYPE_REG), IFLAGS_NONE),
        0x18000500: ( "e_sthu"     ,  E_D8   , INS_STHU, (TYPE_REG, TYPE_MEM, TYPE_REG), IFLAGS_NONE),
        0x18000600: ( "e_stwu"     ,  E_D8   , INS_STWU, (TYPE_REG, TYPE_MEM, TYPE_REG), IFLAGS_NONE),
        0x18000800: ( "e_lmw"      ,  E_D8   ,   INS_LMW, (TYPE_REG, TYPE_MEM, TYPE_REG), IFLAGS_NONE),
        0x18000900: ( "e_stmw"     ,  E_D8   , INS_STMW, (TYPE_REG, TYPE_MEM, TYPE_REG), IFLAGS_NONE),
    },
    0xfc00f800: {
        # MG: added ops from from 0xfc00f800 into 0xfc00f800 in order to fit
        #     both kinds of op[.] variants without adding any masks
        0x18008000: ( "e_addi"     ,  E_SCI8 ,   INS_ADD, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM), IFLAGS_NONE),
        0x18008800: ( "e_addi."    ,  E_SCI8 ,   INS_ADD, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM), IF_RC),
        0x18009000: ( "e_addic"    ,  E_SCI8 ,   INS_ADDIC, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM), IFLAGS_NONE),
        0x18009800: ( "e_addic."   ,  E_SCI8 ,   INS_ADDIC, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM), IF_RC),
        0x1800B000: ( "e_subfic"   ,  E_SCI8 ,   INS_SUBFIC, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM), IFLAGS_NONE),
        0x1800B800: ( "e_subfic."  ,  E_SCI8 ,   INS_SUBFIC, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM), IF_RC),
        0x1800C000: ( "e_andi"     ,  E_SCI8I,   INS_ANDI, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM), IFLAGS_NONE),
        0x1800C800: ( "e_andi."    ,  E_SCI8I,   INS_ANDI, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM), IF_RC),
        0x1800D000: ( "e_ori"      ,  E_SCI8I,   INS_E_ORI, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM), IFLAGS_NONE),
        0x1800D800: ( "e_ori."     ,  E_SCI8I,   INS_E_ORI, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM), IF_RC),
        0x1800E000: ( "e_xori"     ,  E_SCI8I,   INS_XORI, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM), IFLAGS_NONE),
        0x1800E800: ( "e_xori."    ,  E_SCI8I,   INS_XORI, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM), IF_RC),
        # The rest of these have forms already in this mask
        0x1800a000: ( "e_mulli"    ,  E_SCI8 ,   INS_MULLI, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM), IFLAGS_NONE),
        0x70008800: ( "e_add2i."   ,  E_I16A ,   INS_E_ADD2I, (TYPE_SIMM16, TYPE_REG, TYPE_SIMM16), IF_RC),
        0x70009000: ( "e_add2is"   ,  E_I16A ,   INS_E_ADD2IS, (TYPE_SIMM16, TYPE_REG, TYPE_SIMM16), IFLAGS_NONE),
        0x70009800: ( "e_cmp16i"   ,  E_I16A ,   INS_E_CMP16I, (TYPE_SIMM16, TYPE_REG, TYPE_SIMM16), IFLAGS_NONE),
        0x7000a000: ( "e_mull2i"   ,  E_I16A ,   INS_E_MULL2I, (TYPE_SIMM16, TYPE_REG, TYPE_SIMM16), IFLAGS_NONE),
        0x7000a800: ( "e_cmpl16i"  ,  E_I16A ,   INS_E_CMPL16I, (TYPE_IMM, TYPE_REG, TYPE_IMM), IFLAGS_NONE),
        0x7000b000: ( "e_cmph16i"  ,  E_I16A ,   INS_E_CMPH16I, (TYPE_SIMM16, TYPE_REG, TYPE_SIMM16), IFLAGS_NONE),
        0x7000b800: ( "e_cmphl16i" ,  E_I16A ,   INS_E_CMPHL16I, (TYPE_IMM, TYPE_REG, TYPE_IMM), IFLAGS_NONE),
        0x7000c000: ( "e_or2i"     ,  E_I16L ,    INS_E_OR2I, (TYPE_REG, TYPE_IMM, TYPE_IMM), IFLAGS_NONE),
        0x7000c800: ( "e_and2i."   ,  E_I16L ,   INS_E_AND2I, (TYPE_REG, TYPE_IMM, TYPE_IMM), IF_RC),
        0x7000d000: ( "e_or2is"    ,  E_I16L ,    INS_E_OR2IS, (TYPE_REG, TYPE_IMM, TYPE_IMM), IFLAGS_NONE),
        0x7000e000: ( "e_lis"      ,  E_I16L ,   INS_E_LIS, (TYPE_REG, TYPE_IMM, TYPE_IMM), IFLAGS_NONE),
        0x7000e800: ( "e_and2is."  ,  E_I16L ,   INS_E_AND2IS, (TYPE_REG, TYPE_IMM, TYPE_IMM), IF_RC),
    },
    0xfc008000: {
        0x70000000: ( "e_li"       ,  E_LI20 ,   INS_MOV, (TYPE_REG, TYPE_SIMM20), IFLAGS_NONE),
    },
    0xfc0007ff: {
        # MG: Added bit 31 to mask because these either ignore the bit or use it
        #     as Rc, which allows inclusion of both op[.] variants
        0x7c00001c: ( "e_cmph"     ,  E_XCR  ,   INS_E_CMPH, (TYPE_CR, TYPE_REG, TYPE_REG), IFLAGS_NONE),
        0x7c000020: ( "e_mcrf"     ,  E_XLSP ,   INS_MOV, (TYPE_CR, TYPE_CR), IFLAGS_NONE),
        0x7c000042: ( "e_crnor"    ,  E_XL   ,   INS_CRNOR, (TYPE_CRB, TYPE_CRB, TYPE_CRB), IFLAGS_NONE),
        0x7c00005c: ( "e_cmphl"    ,  E_XCR  ,   INS_E_CMPHL, (TYPE_CR, TYPE_REG, TYPE_REG), IFLAGS_NONE),
        0x7C000070: ( "e_slwi"     ,  E_XRA  ,   INS_E_SLWI, (TYPE_REG, TYPE_REG, TYPE_IMM), IFLAGS_NONE),
        0x7C000071: ( "e_slwi."    ,  E_XRA  ,   INS_E_SLWI, (TYPE_REG, TYPE_REG, TYPE_IMM), IF_RC),
        0x7c000102: ( "e_crandc"   ,  E_XL   ,   INS_CRANDC, (TYPE_CRB, TYPE_CRB, TYPE_CRB), IFLAGS_NONE),
        0x7c000182: ( "e_crxor"    ,  E_XL   ,   INS_CRXOR, (TYPE_CRB,  TYPE_CRB, TYPE_CRB), IFLAGS_NONE),
        0x7c0001c2: ( "e_crnand"   ,  E_XL   ,   INS_CRNAND, (TYPE_CRB, TYPE_CRB, TYPE_CRB), IFLAGS_NONE),
        0x7c000202: ( "e_crand"    ,  E_XL   ,   INS_CRAND, (TYPE_CRB, TYPE_CRB, TYPE_CRB), IFLAGS_NONE),
        0x7C000230: ( "e_rlw"      ,  E_XRA  ,   INS_E_RLW, (TYPE_REG, TYPE_REG, TYPE_REG), IFLAGS_NONE),
        0x7C000231: ( "e_rlw."     ,  E_XRA  ,   INS_E_RLW, (TYPE_REG, TYPE_REG, TYPE_REG), IF_RC),
        0x7c000242: ( "e_creqv"    ,  E_XL   ,   INS_CREQV, (TYPE_CRB, TYPE_CRB, TYPE_CRB), IFLAGS_NONE),
        0x7C000270: ( "e_rlwi"     ,  E_XRA  ,   INS_E_RLW, (TYPE_REG, TYPE_REG, TYPE_IMM), IFLAGS_NONE),
        0x7C000271: ( "e_rlwi."    ,  E_XRA  ,   INS_E_RLW, (TYPE_REG, TYPE_REG, TYPE_IMM), IF_RC),
        0x7c000342: ( "e_crorc"    ,  E_XL   ,   INS_CRORC, (TYPE_CRB, TYPE_CRB, TYPE_CRB), IFLAGS_NONE),
        0x7c000382: ( "e_cror"     ,  E_XL   ,   INS_CROR, (TYPE_CRB, TYPE_CRB, TYPE_CRB), IFLAGS_NONE),
        0x7C000470: ( "e_srwi"     ,  E_XRA  ,   INS_E_SRWI, (TYPE_REG, TYPE_REG, TYPE_IMM), IFLAGS_NONE),
        0x7C000471: ( "e_srwi."    ,  E_XRA  ,   INS_E_SRWI, (TYPE_REG, TYPE_REG, TYPE_IMM), IF_RC),
    },
    0xfc000001: {
        0x74000000: ( "e_rlwimi"   ,  E_M    ,   INS_RLWIMI, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM), IFLAGS_NONE),
        0x74000001: ( "e_rlwinm"   ,  E_M    ,   INS_RLWINM, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM), IFLAGS_NONE),
        # MG: I moved "e_b[l]" 0x78000000 from the above bitmask and split it into these two
        0x78000000: ( "e_b"        ,  E_BD24 ,   INS_B, (TYPE_JMP,), IF_BRANCH | IF_NOFALL),
        0x78000001: ( "e_bl"       ,  E_BD24 ,  INS_BL, (TYPE_JMP,), IF_CALL),
    },
    0xfc000000: {
        0x1c000000: ( "e_add16i"   ,  E_D    ,   INS_ADD, (TYPE_REG, TYPE_REG, TYPE_SIMM32), IFLAGS_NONE),
        0x30000000: ( "e_lbz"      ,  E_D    ,  INS_LBZ, (TYPE_REG, TYPE_MEM, TYPE_REG), IFLAGS_NONE),
        0x34000000: ( "e_stb"      ,  E_D    , INS_STB, (TYPE_REG, TYPE_MEM, TYPE_REG), IFLAGS_NONE),
        0x38000000: ( "e_lha"      ,  E_D    ,  INS_LHA, (TYPE_REG, TYPE_MEM, TYPE_REG), IFLAGS_NONE),
        0x50000000: ( "e_lwz"      ,  E_D    ,  INS_LWZ, (TYPE_REG, TYPE_MEM, TYPE_REG), IFLAGS_NONE),
        0x54000000: ( "e_stw"      ,  E_D    , INS_STW, (TYPE_REG, TYPE_MEM, TYPE_REG), IFLAGS_NONE),
        0x58000000: ( "e_lhz"      ,  E_D    ,  INS_LHZ, (TYPE_REG, TYPE_MEM, TYPE_REG), IFLAGS_NONE),
        0x5c000000: ( "e_sth"      ,  E_D    , INS_STH, (TYPE_REG, TYPE_MEM, TYPE_REG), IFLAGS_NONE),
    },
}



# tuple type clarification: Tuple[
#   name: str,
#   num_fields: int,
#   op_type: int,
#   oper_spec: Tuple[Tuple[int]],
#   iflags: int
# ]
se_ops: Dict[int, Dict[int, tuple]] = {
    0xffff: {
        #0x0000: ( "se_illegal", 0,   INS_ILL, (), IF_NOFALL),
        0x0001: ( "se_isync"  , 0,  INS_SYNC, (), IFLAGS_NONE),
        0x0002: ( "se_sc"     , 0,   INS_SE_SC, (), IFLAGS_NONE),
        0x0004: ( "se_blr"    , 0,   INS_BLR, (), IF_RET | IF_NOFALL),
        0x0005: ( "se_blrl"   , 0,   INS_BLRL, (), IF_RET | IF_NOFALL),
        0x0006: ( "se_bctr"   , 0,  INS_BCTR, (), IF_BRANCH | IF_NOFALL),
        0x0007: ( "se_bctrl"  , 0, INS_BCTRL, (), IF_CALL),
        0x0008: ( "se_rfi"    , 0,  INS_TRAP, (), IF_RET | IF_NOFALL | IF_PRIV | IF_RFI),
        0x0009: ( "se_rfci"   , 0,  INS_TRAP, (), IF_RET | IF_NOFALL | IF_PRIV | IF_RFI),
        0x000a: ( "se_rfdi"   , 0,  INS_TRAP, (), IF_RET | IF_NOFALL | IF_PRIV | IF_RFI),
        0x000b: ( "se_rfmci"  , 0,  INS_TRAP, (), IF_RET | IF_NOFALL | IF_PRIV | IF_RFI),
        0x4400: ( "se_nop"    , 0,    INS_NOP, (), IF_NOFALL),
    },
    0xfff0: {
        0x0020: ( "se_not"    , 1,   INS_SE_NOT, ((0x000F,  0,  0,  0, 0, TYPE_REG_SE),), IFLAGS_NONE),
        0x0030: ( "se_neg"    , 1,   INS_SE_NEG, ((0x000F,  0,  0,  0, 0, TYPE_REG_SE),), IFLAGS_NONE),
        0x0080: ( "se_mflr"   , 1,   INS_SE_MFLR, ((0x000F,  0,  0,  0, 0, TYPE_REG_SE),), IFLAGS_NONE),
        0x0090: ( "se_mtlr"   , 1,   INS_SE_MTLR, ((0x000F,  0,  0,  0, 0, TYPE_REG_SE),), IFLAGS_NONE),
        0x00a0: ( "se_mfctr"  , 1,   INS_SE_MFCTR, ((0x000F,  0,  0,  0, 0, TYPE_REG_SE),), IFLAGS_NONE),
        0x00b0: ( "se_mtctr"  , 1,   INS_SE_MTCTR, ((0x000F,  0,  0,  0, 0, TYPE_REG_SE),), IFLAGS_NONE),
        0x00c0: ( "se_extzb"  , 1,    INS_EXTZB, ((0x000F,  0,  0,  0, 0, TYPE_REG_SE),), IFLAGS_NONE),
        0x00d0: ( "se_extsb"  , 1,    INS_SE_EXTSB, ((0x000F,  0,  0,  0, 0, TYPE_REG_SE),), IFLAGS_NONE),
        0x00e0: ( "se_extzh"  , 1,    INS_EXTZH, ((0x000F,  0,  0,  0, 0, TYPE_REG_SE),), IFLAGS_NONE),
        0x00f0: ( "se_extsh"  , 1,    INS_SE_EXTSH, ((0x000F,  0,  0,  0, 0, TYPE_REG_SE),), IFLAGS_NONE),
    },
    0xff00: {
        0x0100: ( "se_mr"     , 2,   INS_MOV, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  0,  0, TYPE_REG_SE),), IFLAGS_NONE),
        0x0200: ( "se_mtar"   , 2,   INS_MOV, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  8,  0, TYPE_REG),), IFLAGS_NONE),
        0x0300: ( "se_mfar"   , 2,   INS_MOV, ((0x00F0,  4,  0,  8, 1, TYPE_REG), (0x000F,  0,  0,  0,  0, TYPE_REG_SE),), IFLAGS_NONE),
        0x0400: ( "se_add"    , 2,   INS_SE_ADD, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  0,  0, TYPE_REG_SE),), IFLAGS_NONE),
        0x0500: ( "se_mullw"  , 2,   INS_SE_MULLW, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  0,  0, TYPE_REG_SE),), IFLAGS_NONE),
        0x0600: ( "se_sub"    , 2,   INS_SE_SUB, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  0,  0, TYPE_REG_SE),), IFLAGS_NONE),
        0x0700: ( "se_subf"   , 2,   INS_SE_SUB, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  0,  0, TYPE_REG_SE),), IFLAGS_NONE),
        0x0c00: ( "se_cmp"    , 2,   INS_CMP, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  0,  0, TYPE_REG_SE),), IFLAGS_NONE),
        0x0d00: ( "se_cmpl"   , 2,   INS_CMPL, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  0,  0, TYPE_REG_SE),), IFLAGS_NONE),
        0x0e00: ( "se_cmph"   , 2,   INS_CMP, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  0,  0, TYPE_REG_SE),), IFLAGS_NONE),
        0x0f00: ( "se_cmphl"  , 2,   INS_CMP, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  0,  0, TYPE_REG_SE),), IFLAGS_NONE),
        0x4000: ( "se_srw"    , 2,   INS_SE_SRW, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  0,  0, TYPE_REG_SE),), IFLAGS_NONE),
        0x4100: ( "se_sraw"   , 2,   INS_SE_SRAW, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  0,  0, TYPE_REG_SE),), IFLAGS_NONE),
        0x4200: ( "se_slw"    , 2,   INS_SE_SLW, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  0,  0, TYPE_REG_SE),), IFLAGS_NONE),
        0x4400: ( "se_or"     , 2,   INS_SE_OR, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  0,  0, TYPE_REG_SE),), IFLAGS_NONE),
        0x4500: ( "se_andc"   , 2,   INS_SE_ANDC, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  0,  0, TYPE_REG_SE),), IFLAGS_NONE),
        0x4600: ( "se_and"    , 2,   INS_SE_AND, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  0,  0, TYPE_REG_SE),), IFLAGS_NONE),
        0x4700: ( "se_and."   , 2,   INS_SE_AND, ((0x00F0,  4,  0,  0, 1, TYPE_REG_SE), (0x000F,  0,  0,  0,  0, TYPE_REG_SE),), IF_RC),
        # MG: Moved se_b into this mask to include both variants of se_b[l]
        #     in the same mask
        0xe800: ( "se_b"      , 1,   INS_B, ((0x00FF,  0,  1,  0, 0, TYPE_JMP),), IF_BRANCH | IF_NOFALL),
        0xe900: ( "se_bl"     , 1,  INS_BL, ((0x00FF,  0,  1,  0, 0, TYPE_JMP),), IF_CALL),
        # MG: Moved all conditional variants of se_bc from 0xf800 to here since
        #     they are selected by via this mask
        # TODO: is BO16 (bit 5) correct to mask here? it seems to be used to control mnemonic choice...
        #0xe000: ( "se_bc"     , 2,  INS_CJMP, ((0x0700,  8,  0, 32, 0, TYPE_JMP), (0x00FF,  0,  1,  0,  1, TYPE_IMM),), IF_COND | IF_BRANCH),
        0xe000: ( "se_bge"    , 1,  INS_BGE, ((0x00FF,  0,  1,  0, 0, TYPE_JMP),), IF_COND | IF_BRANCH),
        0xe100: ( "se_ble"    , 1,  INS_BLE, ((0x00FF,  0,  1,  0, 0, TYPE_JMP),), IF_COND | IF_BRANCH),
        0xe200: ( "se_bne"    , 1,  INS_BNE, ((0x00FF,  0,  1,  0, 0, TYPE_JMP),), IF_COND | IF_BRANCH),
        0xe300: ( "se_bns"    , 1,  INS_BNS, ((0x00FF,  0,  1,  0, 0, TYPE_JMP),), IF_COND | IF_BRANCH),
        0xe400: ( "se_blt"    , 1,  INS_BLT, ((0x00FF,  0,  1,  0, 0, TYPE_JMP),), IF_COND | IF_BRANCH),
        0xe500: ( "se_bgt"    , 1,  INS_BGT, ((0x00FF,  0,  1,  0, 0, TYPE_JMP),), IF_COND | IF_BRANCH),
        0xe600: ( "se_beq"    , 1,  INS_BEQ, ((0x00FF,  0,  1,  0, 0, TYPE_JMP),), IF_COND | IF_BRANCH),
        0xe700: ( "se_bso"    , 1,  INS_BSO, ((0x00FF,  0,  1,  0, 0, TYPE_JMP),), IF_COND | IF_BRANCH),
    },
    0xfe00: {
        0x2000: ( "se_addi"   , 2,   INS_SE_ADD, ((0x01F0,  4,  0,  1, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG_SE),), IFLAGS_NONE),
        0x2200: ( "se_cmpli"  , 2,   INS_CMPLI, ((0x01F0,  4,  0,  1, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG_SE),), IFLAGS_NONE),
        0x2400: ( "se_subi"   , 2,   INS_SE_SUB, ((0x01F0,  4,  0,  1, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG_SE),), IFLAGS_NONE),
        0x2600: ( "se_subi."  , 2,   INS_SE_SUB, ((0x01F0,  4,  0,  1, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG_SE),), IFLAGS_NONE),
        0x2a00: ( "se_cmpi"   , 2,   INS_CMP, ((0x01F0,  4,  0,  0, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG_SE),), IFLAGS_NONE),
        0x2c00: ( "se_bmaski" , 2,    INS_SE_BMASKI, ((0x01F0,  4,  0,  0, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG_SE),), IFLAGS_NONE),
        0x2e00: ( "se_andi"   , 2,   INS_SE_AND, ((0x01F0,  4,  0,  0, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG_SE),), IFLAGS_NONE),
        0x6000: ( "se_bclri"  , 2,    INS_SE_BCLRI, ((0x01F0,  4,  0,  0, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG_SE),), IFLAGS_NONE),
        0x6200: ( "se_bgeni"  , 2,    INS_SE_BGENI, ((0x01F0,  4,  0,  0, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG_SE),), IFLAGS_NONE),
        0x6400: ( "se_bseti"  , 2,    INS_SE_BSETI, ((0x01F0,  4,  0,  0, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG_SE),), IFLAGS_NONE),
        0x6600: ( "se_btsti"  , 2,    INS_SE_BTSTI, ((0x01F0,  4,  0,  0, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG_SE),), IFLAGS_NONE),
        0x6800: ( "se_srwi"   , 2,   INS_SE_SRW, ((0x01F0,  4,  0,  0, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG_SE),), IFLAGS_NONE),
        0x6a00: ( "se_srawi"  , 2,   INS_SE_SRAWI, ((0x01F0,  4,  0,  0, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG_SE),), IFLAGS_NONE),
        0x6c00: ( "se_slwi"   , 2,   INS_SE_SLW, ((0x01F0,  4,  0,  0, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG_SE),), IFLAGS_NONE),
    },
    0xf800: {
        # NOTE: Form IM7's bit depiction in VLE PEM (Fig A-5) is incorrect,
        #       see se_li description on page 3-42 (page 74 in PDF)
        0x4800: ( "se_li"     , 2,   INS_LI, ((0x07F0,  4,  0,  0, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG_SE),), IFLAGS_NONE),
    },
    0xf000: {
        0x8000: ( "se_lbz"    , 3,  INS_LBZ, ((0x0F00,  8,  0,  0, 2, TYPE_IMM), (0x00F0,  4,  0,  0,  0, TYPE_REG_SE), (0x000F,  0,  0,  0,  1, TYPE_SE_MEM),), IFLAGS_NONE),
        0x9000: ( "se_stb"    , 3, INS_STB, ((0x0F00,  8,  0,  0, 2, TYPE_IMM), (0x00F0,  4,  0,  0,  0, TYPE_REG_SE), (0x000F,  0,  0,  0,  1, TYPE_SE_MEM),), IFLAGS_NONE),
        0xa000: ( "se_lhz"    , 3,  INS_LHZ, ((0x0F00,  7,  0,  0, 2, TYPE_IMM), (0x00F0,  4,  0,  0,  0, TYPE_REG_SE), (0x000F,  0,  0,  0,  1, TYPE_SE_MEM),), IFLAGS_NONE),
        0xb000: ( "se_sth"    , 3, INS_STH, ((0x0F00,  7,  0,  0, 2, TYPE_IMM), (0x00F0,  4,  0,  0,  0, TYPE_REG_SE), (0x000F,  0,  0,  0,  1, TYPE_SE_MEM),), IFLAGS_NONE),
        0xc000: ( "se_lwz"    , 3,  INS_LWZ, ((0x0F00,  6,  0,  0, 2, TYPE_IMM), (0x00F0,  4,  0,  0,  0, TYPE_REG_SE), (0x000F,  0,  0,  0,  1, TYPE_SE_MEM),), IFLAGS_NONE),
        0xd000: ( "se_stw"    , 3, INS_STW, ((0x0F00,  6,  0,  0, 2, TYPE_IMM), (0x00F0,  4,  0,  0,  0, TYPE_REG_SE), (0x000F,  0,  0,  0,  1, TYPE_SE_MEM),), IFLAGS_NONE),
    },
}
