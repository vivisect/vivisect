TYPE_NONE = 0
TYPE_REG =  1
TYPE_IMM =  2
TYPE_MEM =  3
TYPE_JMP =  4
TYPE_CR =   5

import vstruct
from vstruct.primitives import *
'''
class BITMAPINFOHEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.biSize             = v_uint32()
        self.biWidth            = v_int32()
        self.biHeight           = v_int32()
        self.biPlanes           = v_uint16()
        self.biBitCount         = v_uint16()
        self.biCompression      = v_uint32()
        self.biSizeImage        = v_uint32()
        self.biXPelsPerMeter    = v_int32()
        self.biYPelsPerMeter    = v_int32()
        self.biClrUser          = v_uint32()
        self.biClrImportant     = v_uint32()



class vle_handle(vstruct.VStruct):
        vstruct.VStruct.__init__(self)
        self.end                = v_ptr32()
        self.pos                = v_ptr32()
        self.inc                = v_uint16()

class vle_field_t(vstruct.VStruct):
typedef struct {
	ut32 value;
	ut16 type;
} vle_field_t;

typedef struct {
	const char* name;
	vle_field_t fields[10];
	ut16 n;
	ut16 size;
} vle_t;

int vle_init(vle_handle* handle, const ut8* buffer, const ut32 size);
vle_t* vle_next(vle_handle* handle);
void vle_free(vle_t* instr);
void vle_snprint(char* str, int size, ut64 addr, vle_t* instr);
'''

PFMT64x = "llx"

E_NONE =  0
E_X =     1
E_XL =    2
E_D =     3
E_D8 =    4
E_I16A =  5
E_SCI8 =  6
E_SCI8I = 7
E_I16L =  8
E_I16LS = 9
E_BD24 =  10
E_BD15 =  11
E_IA16 =  12
E_LI20 =  13
E_M =     14
E_XCR =   15
E_XLSP =  16

E_MASK_X =    0x03FFF800
E_MASK_XL =   0x03FFF801
E_MASK_D =    0x01FFFFFF
E_MASK_D8 =   0x03FF00FF
E_MASK_I16A = 0x03FF07FF
E_MASK_SCI8 = 0x03FF07FF
E_MASK_I16L = 0x03FF07FF
E_MASK_BD24 = 0x03FFFFFE
E_MASK_BD15 = 0x000CFFFE
E_MASK_IA16 = 0x03FF07FF
E_MASK_LI20 = 0x03FF7FFF
E_MASK_M =    0x03FFFFFE

F_NONE =  0
F_X =     1
F_XO =    2
F_EVX =   3
F_CMP =   4
F_DCBF =  5
F_DCBL =  6
F_DCI =   7
F_EXT =   8
F_A =     9
F_XFX =  10
F_XER =  11
F_MFPR = 12
F_MTPR = 13


F_MASK_X =     0x03FFF800
F_MASK_XO =    0x03FFF800
F_MASK_EVX =   0x03FFF800
F_MASK_CMP =   0x039FF800
F_MASK_DCBF =  0x00FFF800
F_MASK_DCBL =  0x01FFF800
F_MASK_DCI =   0x00FFF800
F_MASK_EXT =   0x03FF0000
F_MASK_A =     0x01FFFFC0
F_MASK_XFX =   0x03FFF800
F_MASK_XER =   0x03FFF800
F_MASK_MFPR =  0x03FFF800
F_MASK_MTPR =  0x03FFF800


ppc_ops = (
	#( "name"       , op        , mask                    , type   , (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_REG, TYPE_REG))
	( "add"        , 0x7C000214, 0x7C000214 | F_MASK_XO  ,    F_XO, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "add."       , 0x7C000214, 0x7C000211 | F_MASK_XO  ,    F_XO, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "addo"       , 0x7C000214, 0x7C000614 | F_MASK_XO  ,    F_XO, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "addo."      , 0x7C000214, 0x7C000615 | F_MASK_XO  ,    F_XO, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "addc"       , 0x7C000014, 0x7C000014 | F_MASK_XO  ,    F_XO, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "addc."      , 0x7C000014, 0x7C000011 | F_MASK_XO  ,    F_XO, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "addco"      , 0x7C000014, 0x7C000414 | F_MASK_XO  ,    F_XO, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "addco."     , 0x7C000014, 0x7C000415 | F_MASK_XO  ,    F_XO, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "adde"       , 0x7C000114, 0x7C000114 | F_MASK_XO  ,    F_XO, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "adde."      , 0x7C000114, 0x7C000111 | F_MASK_XO  ,    F_XO, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "addeo"      , 0x7C000114, 0x7C000514 | F_MASK_XO  ,    F_XO, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "addeo."     , 0x7C000114, 0x7C000515 | F_MASK_XO  ,    F_XO, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "addme"      , 0x7C0001D4, 0x7C0001D4 | F_MASK_XO  ,    F_XO, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "addme."     , 0x7C0001D4, 0x7C0001D1 | F_MASK_XO  ,    F_XO, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "addmeo"     , 0x7C0001D4, 0x7C0005D4 | F_MASK_XO  ,    F_XO, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "addmeo."    , 0x7C0001D4, 0x7C0005D5 | F_MASK_XO  ,    F_XO, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "addze"      , 0x7C000194, 0x7C000194 | F_MASK_XO  ,    F_XO, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "addze."     , 0x7C000194, 0x7C000191 | F_MASK_XO  ,    F_XO, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "addzeo"     , 0x7C000194, 0x7C000594 | F_MASK_XO  ,    F_XO, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "addzeo."    , 0x7C000194, 0x7C000595 | F_MASK_XO  ,    F_XO, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "and"        , 0x7C000038, 0x7C000038 | F_MASK_X   ,     F_X, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "and."       , 0x7C000038, 0x7C000039 | F_MASK_X   ,     F_X, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "andc"       , 0x7C000078, 0x7C000078 | F_MASK_X   ,     F_X, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "andc."      , 0x7C000078, 0x7C000079 | F_MASK_X   ,     F_X, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "or"         , 0x7C000378, 0x7C000378 | F_MASK_X   ,     F_X, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "or."        , 0x7C000378, 0x7C000379 | F_MASK_X   ,     F_X, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "nor"        , 0x7C0000f8, 0x7C0000f8 | F_MASK_X   ,     F_X, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "nor."       , 0x7C0000f8, 0x7C0000f9 | F_MASK_X   ,     F_X, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "brinc"      , 0x1000020F, 0x1000020F | F_MASK_EVX ,   F_EVX, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "cmp"        , 0x7C000000, 0x7C000000 | F_MASK_CMP ,   F_CMP, (TYPE_CR, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "cmpl"       , 0x7C000040, 0x7C000040 | F_MASK_CMP ,   F_CMP, (TYPE_CR, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "cntlzd"     , 0x7C000074, 0x7C000074 | F_MASK_X   ,     F_X, (TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "cntlzd."    , 0x7C000074, 0x7C000075 | F_MASK_X   ,     F_X, (TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "cntlzw"     , 0x7C000034, 0x7C000034 | F_MASK_X   ,     F_X, (TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "cntlzw."    , 0x7C000034, 0x7C000035 | F_MASK_X   ,     F_X, (TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "dcba"       , 0x7C0005EC, 0x7C0005EC | F_MASK_X   ,     F_X, (TYPE_NONE, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "dcbf"       , 0x7C0000AC, 0x7C0000AC | F_MASK_DCBF,  F_DCBF, (TYPE_IMM, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "dcbfep"     , 0x7C0000FE, 0x7C0000FE | F_MASK_DCBF,  F_DCBF, (TYPE_IMM, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "dcbi"       , 0x7C0003AC, 0x7C0003AC | F_MASK_X   ,     F_X, (TYPE_NONE, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "dcblc"      , 0x7C00030C, 0x7C00030C | F_MASK_DCBL,  F_DCBL, (TYPE_IMM, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "dcbst"      , 0x7C00006C, 0x7C00006C | F_MASK_X   ,     F_X, (TYPE_NONE, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "dcbt"       , 0x7C00022C, 0x7C00022C | F_MASK_X   ,     F_X, (TYPE_IMM, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "dcbtep"     , 0x7C00027E, 0x7C00027E | F_MASK_X   ,     F_X, (TYPE_IMM, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "dcbtls"     , 0x7C00014C, 0x7C00014C | F_MASK_DCBL,  F_DCBL, (TYPE_IMM, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "dcbtst"     , 0x7C0001EC, 0x7C0001EC | F_MASK_DCBL,  F_DCBL, (TYPE_IMM, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "dcbtstep"   , 0x7C0001FE, 0x7C0001FE | F_MASK_X   ,     F_X, (TYPE_IMM, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "dcbtstls"   , 0x7C00010C, 0x7C00010C | F_MASK_DCBL,  F_DCBL, (TYPE_IMM, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "dcbz"       , 0x7C0007EC, 0x7C0007EC | F_MASK_X   ,     F_X, (TYPE_NONE, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "dcbzep"     , 0x7C0007FE, 0x7C0007FE | F_MASK_X   ,     F_X, (TYPE_NONE, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "dci"        , 0x7C00038C, 0x7C00038C | F_MASK_DCI ,   F_DCI, (TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "dcread"     , 0x7C00028C, 0x7C00028C | F_MASK_X   ,     F_X, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "dcread"     , 0x7C0003CC, 0x7C0003CC | F_MASK_X   ,     F_X, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "divw"       , 0x7C0003D6, 0x7C0003D6 | F_MASK_XO  ,    F_XO, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "divw."      , 0x7C0003D6, 0x7C0003D7 | F_MASK_XO  ,    F_XO, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "divwo"      , 0x7C0003D6, 0x7C0007D6 | F_MASK_XO  ,    F_XO, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "divwo."     , 0x7C0003D6, 0x7C0007D7 | F_MASK_XO  ,    F_XO, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "divwu"      , 0x7C000396, 0x7C000396 | F_MASK_XO  ,    F_XO, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "divwu."     , 0x7C000396, 0x7C000397 | F_MASK_XO  ,    F_XO, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "divwuo"     , 0x7C000396, 0x7C000796 | F_MASK_XO  ,    F_XO, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "divwuo."    , 0x7C000396, 0x7C000797 | F_MASK_XO  ,    F_XO, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "extsb"      , 0x7C000774, 0x7C000774 | F_MASK_EXT ,   F_EXT, (TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "extsb."     , 0x7C000774, 0x7C000775 | F_MASK_EXT ,   F_EXT, (TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "extsw"      , 0x7C000734, 0x7C000734 | F_MASK_EXT ,   F_EXT, (TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "extsw."     , 0x7C000734, 0x7C000735 | F_MASK_EXT ,   F_EXT, (TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "icbi"       , 0x7C0007AC, 0x7C0007AC | F_MASK_X   ,     F_X, (TYPE_NONE, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "icbiep"     , 0x7C0007BE, 0x7C0007BE | F_MASK_X   ,     F_X, (TYPE_NONE, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "icblc"      , 0x7C0001CC, 0x7C0001CC | F_MASK_DCBL,  F_DCBL, (TYPE_IMM, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "icbt"       , 0x7C00002C, 0x7C00002C | F_MASK_DCBL,  F_DCBL, (TYPE_IMM, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "icbtls"     , 0x7C0003CC, 0x7C0003CC | F_MASK_DCBL,  F_DCBL, (TYPE_IMM, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "ici"        , 0x7C00078C, 0x7C00078C | F_MASK_DCI ,   F_DCI, (TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "icread"     , 0x7C0007CC, 0x7C0007CC | F_MASK_X   ,     F_X, (TYPE_NONE, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	# apply only X instead of A for lt, gt, eq
	( "isellt"     , 0x7C00001E, 0x7C00001E | F_MASK_X   ,     F_A, (TYPE_NONE, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "iselgt"     , 0x7C00001E, 0x7C00005E | F_MASK_X   ,     F_A, (TYPE_NONE, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "iseleq"     , 0x7C00001E, 0x7C00009E | F_MASK_X   ,     F_A, (TYPE_NONE, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "isel"       , 0x7C00001E, 0x7C00001E | F_MASK_A   ,     F_A, (TYPE_NONE, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "lbepx"      , 0x7C0000BE, 0x7C0000BE | F_MASK_X   ,     F_X, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "lbzux"      , 0x7C0000AE, 0x7C0000AE | F_MASK_X   ,     F_X, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "lhaux"      , 0x7C0002EE, 0x7C0002EE | F_MASK_X   ,     F_X, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
 	( "lhax"       , 0x7C0002AE, 0x7C0002AE | F_MASK_X   ,     F_X, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
 	( "lhbrx"      , 0x7C00062C, 0x7C00062C | F_MASK_X   ,     F_X, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
 	( "lhepx"      , 0x7C00023E, 0x7C00023E | F_MASK_X   ,     F_X, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
 	( "lhzux"      , 0x7C00026E, 0x7C00026E | F_MASK_X   ,     F_X, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
 	( "lhzx"       , 0x7C00022E, 0x7C00022E | F_MASK_X   ,     F_X, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
 	( "lswi"       , 0x7C0004AA, 0x7C0004AA | F_MASK_X   ,     F_X, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE)),
 	( "lswx"       , 0x7C00042A, 0x7C00042A | F_MASK_X   ,     F_X, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE)),
 	( "lwarx"      , 0x7C000028, 0x7C000028 | F_MASK_X   ,     F_X, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
 	( "lwarx."     , 0x7C000029, 0x7C000029 | F_MASK_X   ,     F_X, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
 	( "lwbrx"      , 0x7C00042C, 0x7C00042C | F_MASK_X   ,     F_X, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
 	( "lwepx"      , 0x7C00003E, 0x7C00003E | F_MASK_X   ,     F_X, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
 	( "lwzux"      , 0x7C00006E, 0x7C00006E | F_MASK_X   ,     F_X, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
 	( "lwzx"       , 0x7C00002E, 0x7C00002E | F_MASK_X   ,     F_X, (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
 	( "mbar"       , 0x7C00002E, 0x7C00002E | F_MASK_XFX ,   F_XFX, (TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
 	( "mcrxr"      , 0x7C000400, 0x7C000400 | F_MASK_XER ,   F_XER, (TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
 	( "mfdcr"      , 0x7C000286, 0x7C000286 | F_MASK_MFPR,  F_MFPR, (TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "mfdcrux"    , 0x7C000246, 0x7C000246 | F_MASK_EXT ,   F_EXT, (TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "mfdcrx"     , 0x7C000206, 0x7C000206 | F_MASK_EXT ,   F_EXT, (TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
 	( "mfmsr"      , 0x7C0000A6, 0x7C0000A6 | F_MASK_XFX ,   F_XFX, (TYPE_REG, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
 	( "mfspr"      , 0x7C0002A6, 0x7C0002A6 | F_MASK_MFPR,  F_MFPR, (TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
 	( "mtspr"      , 0x7C0003A6, 0x7C0003A6 | F_MASK_MTPR,  F_MTPR, (TYPE_IMM, TYPE_REG, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
 	( "mtmsr"      , 0x7C000124, 0x7C000124 | F_MASK_XFX ,   F_XFX, (TYPE_REG, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "msync"      , 0x7C0004AC, 0x7C0004AC | F_MASK_XFX ,   F_XFX, (TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "tlbre"      , 0x7C000764, 0x7C000764 | F_MASK_XFX ,  F_NONE, (TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "tlbwe"      , 0x7C0007A4, 0x7C0007A4 | F_MASK_XFX ,  F_NONE, (TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "stwx"       , 0x7C00012E, 0x7C00012E | E_MASK_XL  ,   E_XL , (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "mfcr"       , 0x7C000026, 0x7C000026 | E_MASK_XL  ,   E_XL , (TYPE_REG, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "mtcrf"      , 0x7C000120, 0x7C000120 | E_MASK_XL  ,   E_XL , (TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)), #crf rossz
) 

e_ops = (
        #"name"       , op        , mask                    , type   , (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_REG, TYPE_REG))
	( "e_add16i"   , 0x1C000000, 0x1F000000 | E_MASK_D   , E_D    , (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE)),
	( "e_add2i."   , 0x70008800, 0x70008800 | E_MASK_I16A, E_I16A , (TYPE_IMM, TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE)),
	( "e_add2is"   , 0x70009000, 0x70009000 | E_MASK_I16A, E_I16A , (TYPE_IMM, TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE)),
	( "e_addi"     , 0x18008000, 0x18008000 | E_MASK_SCI8, E_SCI8 , (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM)),
	( "e_addi."    , 0x18008800, 0x18008800 | E_MASK_SCI8, E_SCI8 , (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM)),
	( "e_addic"    , 0x18009000, 0x18009000 | E_MASK_SCI8, E_SCI8 , (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM)),
	( "e_addic."   , 0x18009800, 0x18009800 | E_MASK_SCI8, E_SCI8 , (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM)),
	( "e_and2i."   , 0x7000C800, 0x7000C800 | E_MASK_I16L, E_I16L , (TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_NONE, TYPE_NONE)),
	( "e_and2is."  , 0x7000E800, 0x7000E800 | E_MASK_I16L, E_I16LS, (TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_NONE, TYPE_NONE)),
	( "e_andi"     , 0x1800C000, 0x1800C000 | E_MASK_SCI8, E_SCI8I, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM)),
	( "e_andi."    , 0x1800C800, 0x1800C800 | E_MASK_SCI8, E_SCI8I, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM)),
	#  has cr0-cr3 
	( "e_bge"      , 0x7A000000, 0x7A000000 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_ble"      , 0x7A000000, 0x7A010000 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_bne"      , 0x7A000000, 0x7A020000 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_bns"      , 0x7A000000, 0x7A030000 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_blt"      , 0x7A000000, 0x7A110000 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_bgt"      , 0x7A000000, 0x7A120000 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_beq"      , 0x7A000000, 0x7A130000 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_bso"      , 0x7A000000, 0x7A140000 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_bc"       , 0x7A000000, 0x7A140000 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_bgel"     , 0x7A000001, 0x7A000001 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_blel"     , 0x7A000001, 0x7A010001 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_bnel"     , 0x7A000001, 0x7A020001 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_bnsl"     , 0x7A000001, 0x7A030001 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_bltl"     , 0x7A000001, 0x7A110001 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_bgtl"     , 0x7A000001, 0x7A120001 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_beql"     , 0x7A000001, 0x7A130001 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_bsol"     , 0x7A000001, 0x7A140001 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_bcl"      , 0x7A000001, 0x7A140001 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	#  has cr0-cr3  
	( "e_bgectr"   , 0x7A000000, 0x7A200000 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_blectr"   , 0x7A000000, 0x7A210000 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_bnectr"   , 0x7A000000, 0x7A220000 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_bnsctr"   , 0x7A000000, 0x7A230000 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_bltctr"   , 0x7A000000, 0x7A310000 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_bgtctr"   , 0x7A000000, 0x7A320000 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_beqctr"   , 0x7A000000, 0x7A330000 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_bsoctr"   , 0x7A000000, 0x7A340000 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_bcctr"    , 0x7A000000, 0x7A340000 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_bgectrl"  , 0x7A000001, 0x7A200001 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_blectrl"  , 0x7A000001, 0x7A210001 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_bnectrl"  , 0x7A000001, 0x7A220001 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_bnsctrl"  , 0x7A000001, 0x7A230001 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_bltctrl"  , 0x7A000001, 0x7A310001 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_bgtctrl"  , 0x7A000001, 0x7A320001 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_beqctrl"  , 0x7A000001, 0x7A330001 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_bsoctrl"  , 0x7A000001, 0x7A340001 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_bcctrl"   , 0x7A000001, 0x7A340001 | E_MASK_BD15, E_BD15 , (TYPE_CR, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_b"        , 0x78000000, 0x78000000 | E_MASK_BD24, E_BD24 , (TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_bl"       , 0x78000001, 0x78000001 | E_MASK_BD24, E_BD24 , (TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_cmp16i"   , 0x70009800, 0x70009800 | E_MASK_IA16, E_IA16 , (TYPE_IMM, TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE)),
	( "e_cmph16i"  , 0x7000B000, 0x7000B000 | E_MASK_IA16, E_IA16 , (TYPE_IMM, TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE)),
	( "e_cmph"     , 0x7C00001C, 0x7C00001D | E_MASK_X   , E_XCR  , (TYPE_CR, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "e_cmphl16i" , 0x7000B800, 0x7000B800 | E_MASK_IA16, E_IA16 , (TYPE_IMM, TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE)),
	( "e_cmphl"    , 0x7C00005C, 0x7C00005D | E_MASK_X   , E_XCR  , (TYPE_CR, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "e_cmpli"    , 0x1880A800, 0x1880A800 | E_MASK_SCI8, E_SCI8 , (TYPE_CR, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM)),
	( "e_cmpi"     , 0x1800A800, 0x1800A800 | E_MASK_SCI8, E_SCI8 , (TYPE_CR, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM)),
	( "e_cmpl16i"  , 0x7000A800, 0x7000A800 | E_MASK_IA16, E_IA16 , (TYPE_IMM, TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE)),
	( "e_crand"    , 0x7C000202, 0x7C000202 | E_MASK_XL  , E_XL   , (TYPE_CR, TYPE_CR, TYPE_CR, TYPE_NONE, TYPE_NONE)),
	( "e_crandc"   , 0x7C000102, 0x7C000102 | E_MASK_XL  , E_XL   , (TYPE_CR, TYPE_CR, TYPE_CR, TYPE_NONE, TYPE_NONE)),
	( "e_creqv"    , 0x7C000242, 0x7C000242 | E_MASK_XL  , E_XL   , (TYPE_CR, TYPE_CR, TYPE_CR, TYPE_NONE, TYPE_NONE)),
	( "e_crnand"   , 0x7C0001C2, 0x7C0001C2 | E_MASK_XL  , E_XL   , (TYPE_CR, TYPE_CR, TYPE_CR, TYPE_NONE, TYPE_NONE)),
	( "e_crnor"    , 0x7C000042, 0x7C000042 | E_MASK_XL  , E_XL   , (TYPE_CR, TYPE_CR, TYPE_CR, TYPE_NONE, TYPE_NONE)),
	( "e_cror"     , 0x7C000382, 0x7C000382 | E_MASK_XL  , E_XL   , (TYPE_CR, TYPE_CR, TYPE_CR, TYPE_NONE, TYPE_NONE)),
	( "e_crorc"    , 0x7C000342, 0x7C000342 | E_MASK_XL  , E_XL   , (TYPE_CR, TYPE_CR, TYPE_CR, TYPE_NONE, TYPE_NONE)),
	( "e_crxor"    , 0x7C000182, 0x7C000182 | E_MASK_XL  , E_XL   , (TYPE_CR, TYPE_CR, TYPE_CR, TYPE_NONE, TYPE_NONE)),
	( "e_lbz"      , 0x30000000, 0x30000000 | E_MASK_D   , E_D    , (TYPE_REG, TYPE_MEM, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "e_lbzu"     , 0x18000000, 0x18000000 | E_MASK_D8  , E_D8   , (TYPE_REG, TYPE_MEM, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "e_lha"      , 0x38000000, 0x38000000 | E_MASK_D   , E_D    , (TYPE_REG, TYPE_MEM, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "e_lhau"     , 0x18000300, 0x18000300 | E_MASK_D8  , E_D8   , (TYPE_REG, TYPE_MEM, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "e_lhz"      , 0x58000000, 0x58000000 | E_MASK_D   , E_D    , (TYPE_REG, TYPE_MEM, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "e_lhzu"     , 0x18000100, 0x18000100 | E_MASK_D8  , E_D8   , (TYPE_REG, TYPE_MEM, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "e_li"       , 0x70000000, 0x70000000 | E_MASK_LI20, E_LI20 , (TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_lis"      , 0x7000E000, 0x7000E000 | E_MASK_I16L, E_I16LS, (TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_NONE, TYPE_NONE)),
	( "e_lmw"      , 0x18000800, 0x18000800 | E_MASK_D8  , E_D8   , (TYPE_REG, TYPE_MEM, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "e_lwz"      , 0x50000000, 0x53000000 | E_MASK_D   , E_D    , (TYPE_REG, TYPE_MEM, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "e_lwzu"     , 0x18000200, 0x18000200 | E_MASK_D8  , E_D8   , (TYPE_REG, TYPE_MEM, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "e_mcrf"     , 0x7C000020, 0x7C000020 | E_MASK_XL  , E_XLSP , (TYPE_CR, TYPE_CR, TYPE_NONE, TYPE_NONE, TYPE_NONE)),
	( "e_mull2i"   , 0x7000A000, 0x7000A000 | E_MASK_I16A, E_I16A , (TYPE_IMM, TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE)),
	( "e_mulli"    , 0x1800A000, 0x1800A000 | E_MASK_SCI8, E_SCI8 , (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM)),
	( "e_or2i"     , 0x7000C000, 0x7000C000 | E_MASK_I16L, E_I16L , (TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_NONE, TYPE_NONE)),
	( "e_or2is"    , 0x7000D000, 0x7000D000 | E_MASK_I16L, E_I16LS, (TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_NONE, TYPE_NONE)),
	( "e_ori"      , 0x1800D000, 0x1800D000 | E_MASK_SCI8, E_SCI8 , (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM)),
	( "e_ori."     , 0x1800D800, 0x1800D800 | E_MASK_SCI8, E_SCI8 , (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM)),
	( "e_rlw"      , 0x7C000230, 0x7C000230 | E_MASK_X   , E_X    , (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "e_rlw."     , 0x7C000231, 0x7C000231 | E_MASK_X   , E_X    , (TYPE_REG, TYPE_REG, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "e_rlwi"     , 0x7C000270, 0x7C000270 | E_MASK_X   , E_X    , (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE)),
	( "e_rlwi."    , 0x7C000271, 0x7C000271 | E_MASK_X   , E_X    , (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE)),
	( "e_rlwimi"   , 0x74000000, 0x74000000 | E_MASK_M   , E_M    , (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM)),
	( "e_rlwinm"   , 0x74000001, 0x74000001 | E_MASK_M   , E_M    , (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM)),
	( "e_slwi"     , 0x7C000070, 0x7C000070 | E_MASK_X   , E_X    , (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE)),
	( "e_slwi."    , 0x7C000071, 0x7C000071 | E_MASK_X   , E_X    , (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE)),
	( "e_srwi"     , 0x7C000470, 0x7C000470 | E_MASK_X   , E_X    , (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE)),
	( "e_srwi."    , 0x7C000471, 0x7C000471 | E_MASK_X   , E_X    , (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_NONE, TYPE_NONE)),
	( "e_stb"      , 0x34000000, 0x34000000 | E_MASK_D   , E_D    , (TYPE_REG, TYPE_MEM, TYPE_IMM, TYPE_NONE, TYPE_NONE)),
	( "e_stbu"     , 0x18000400, 0x18000400 | E_MASK_D8  , E_D8   , (TYPE_REG, TYPE_MEM, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "e_sth"      , 0x5C000000, 0x5C000000 | E_MASK_D   , E_D    , (TYPE_REG, TYPE_MEM, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "e_sthu"     , 0x18000500, 0x18000500 | E_MASK_D8  , E_D8   , (TYPE_REG, TYPE_MEM, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "e_stmw"     , 0x18000900, 0x18000900 | E_MASK_D8  , E_D8   , (TYPE_REG, TYPE_MEM, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "e_stw"      , 0x54000000, 0x56000000 | E_MASK_D   , E_D    , (TYPE_REG, TYPE_MEM, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "e_stwu"     , 0x18000600, 0x18000600 | E_MASK_D8  , E_D8   , (TYPE_REG, TYPE_MEM, TYPE_REG, TYPE_NONE, TYPE_NONE)),
	( "e_subfic"   , 0x1800B000, 0x1800B000 | E_MASK_SCI8, E_SCI8 , (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM)),
	( "e_subfic."  , 0x1800B800, 0x1800B800 | E_MASK_SCI8, E_SCI8 , (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM)),
	( "e_xori"     , 0x1800E000, 0x1800E000 | E_MASK_SCI8, E_SCI8I, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM)),
	( "e_xori."    , 0x1800E800, 0x1800E800 | E_MASK_SCI8, E_SCI8I, (TYPE_REG, TYPE_REG, TYPE_IMM, TYPE_IMM, TYPE_IMM)),
);

se_ops = (
        #( "name"      , op    , mask  , n,   op_type           , ((field ,shl,shr,  +, i, TYPE_REG), ...)
	( "se_illegal", 0x0000, 0x0000, 0, ((0), (0), (0), (0), (0))),
	( "se_isync"  , 0x0001, 0x0001, 0, ((0), (0), (0), (0), (0))),
	( "se_sc"     , 0x0002, 0x0002, 0, ((0), (0), (0), (0), (0))),
	( "se_blr"    , 0x0004, 0x0004, 0, ((0), (0), (0), (0), (0))),
	( "se_blrl"   , 0x0005, 0x0005, 0, ((0), (0), (0), (0), (0))),
	( "se_bctr"   , 0x0006, 0x0006, 0, ((0), (0), (0), (0), (0))),
	( "se_bctrl"  , 0x0007, 0x0007, 0, ((0), (0), (0), (0), (0))),
	( "se_rfi"    , 0x0008, 0x0008, 0, ((0), (0), (0), (0), (0))),
	( "se_rfci"   , 0x0009, 0x0009, 0, ((0), (0), (0), (0), (0))),
	( "se_rfdi"   , 0x000A, 0x000A, 0, ((0), (0), (0), (0), (0))),
	( "se_not"    , 0x0020, 0x002F, 1, ((0x000F,  0,  0,  0, 0, TYPE_REG), (0), (0), (0), (0))),
	( "se_neg"    , 0x0030, 0x003F, 1, ((0x000F,  0,  0,  0, 0, TYPE_REG), (0), (0), (0), (0))),
	( "se_mflr"   , 0x0080, 0x008F, 1, ((0x000F,  0,  0,  0, 0, TYPE_REG), (0), (0), (0), (0))),
	( "se_mtlr"   , 0x0090, 0x009F, 1, ((0x000F,  0,  0,  0, 0, TYPE_REG), (0), (0), (0), (0))),
	( "se_mfctr"  , 0x00A0, 0x00AF, 1, ((0x000F,  0,  0,  0, 0, TYPE_REG), (0), (0), (0), (0))),
	( "se_mtctr"  , 0x00B0, 0x00BF, 1, ((0x000F,  0,  0,  0, 0, TYPE_REG), (0), (0), (0), (0))),
	( "se_extzb"  , 0x00C0, 0x00CF, 1, ((0x000F,  0,  0,  0, 0, TYPE_REG), (0), (0), (0), (0))),
	( "se_extsb"  , 0x00D0, 0x00DF, 1, ((0x000F,  0,  0,  0, 0, TYPE_REG), (0), (0), (0), (0))),
	( "se_extzh"  , 0x00E0, 0x00EF, 1, ((0x000F,  0,  0,  0, 0, TYPE_REG), (0), (0), (0), (0))),
	( "se_extsh"  , 0x00F0, 0x00FF, 1, ((0x000F,  0,  0,  0, 0, TYPE_REG), (0), (0), (0), (0))),
	( "se_mr"     , 0x0100, 0x01FF, 2, ((0x00F0,  4,  0,  0, 1, TYPE_REG), (0x000F,  0,  0,  0,  0, TYPE_REG), (0), (0), (0))),
	( "se_mtar"   , 0x0200, 0x02FF, 2, ((0x00F0,  4,  0,  0, 1, TYPE_REG), (0x000F,  0,  0,  8,  0, TYPE_REG), (0), (0), (0))),
	( "se_mfar"   , 0x0300, 0x03FF, 2, ((0x00F0,  4,  0,  8, 1, TYPE_REG), (0x000F,  0,  0,  0,  0, TYPE_REG), (0), (0), (0))),
	( "se_add"    , 0x0400, 0x04FF, 2, ((0x00F0,  4,  0,  0, 1, TYPE_REG), (0x000F,  0,  0,  0,  0, TYPE_REG), (0), (0), (0))),
	( "se_mullw"  , 0x0500, 0x05FF, 2, ((0x00F0,  4,  0,  0, 1, TYPE_REG), (0x000F,  0,  0,  0,  0, TYPE_REG), (0), (0), (0))),
	( "se_sub"    , 0x0600, 0x06FF, 2, ((0x00F0,  4,  0,  0, 0, TYPE_REG), (0x000F,  0,  0,  0,  2, TYPE_REG), (0), (0), (0))),
	( "se_subf"   , 0x0700, 0x07FF, 2, ((0x00F0,  4,  0,  0, 0, TYPE_REG), (0x000F,  0,  0,  0,  2, TYPE_REG), (0), (0), (0))),
	( "se_cmp"    , 0x0C00, 0x0CFF, 2, ((0x00F0,  4,  0,  0, 1, TYPE_REG), (0x000F,  0,  0,  0,  0, TYPE_REG), (0), (0), (0))),
	( "se_cmpl"   , 0x0D00, 0x0DFF, 2, ((0x00F0,  4,  0,  0, 1, TYPE_REG), (0x000F,  0,  0,  0,  0, TYPE_REG), (0), (0), (0))),
	( "se_cmph"   , 0x0E00, 0x0EFF, 2, ((0x00F0,  4,  0,  0, 1, TYPE_REG), (0x000F,  0,  0,  0,  0, TYPE_REG), (0), (0), (0))),
	( "se_cmphl"  , 0x0F00, 0x0FFF, 2, ((0x00F0,  4,  0,  0, 1, TYPE_REG), (0x000F,  0,  0,  0,  0, TYPE_REG), (0), (0), (0))),
	( "se_addi"   , 0x2000, 0x21FF, 2, ((0x01F0,  4,  0,  1, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG), (0), (0), (0))),
	( "se_and"    , 0x4600, 0x46FF, 2, ((0x00F0,  4,  0,  0, 1, TYPE_REG), (0x000F,  0,  0,  0,  0, TYPE_REG), (0), (0), (0))),
	( "se_and."   , 0x4700, 0x47FF, 2, ((0x00F0,  4,  0,  0, 1, TYPE_REG), (0x000F,  0,  0,  0,  0, TYPE_REG), (0), (0), (0))),
	( "se_andi"   , 0x2E00, 0x2FFF, 2, ((0x01F0,  4,  0,  0, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG), (0), (0), (0))),
	( "se_andc"   , 0x4500, 0x45FF, 2, ((0x00F0,  4,  0,  0, 1, TYPE_REG), (0x000F,  0,  0,  0,  0, TYPE_REG), (0), (0), (0))),
	( "se_b"      , 0xE800, 0xE8FF, 1, ((0x00FF,  0,  1,  0, 0, TYPE_JMP), (0), (0), (0), (0))),
	( "se_bl"     , 0xE900, 0xE9FF, 1, ((0x00FF,  0,  1,  0, 0, TYPE_JMP), (0), (0), (0), (0))),
	#  cr0
	( "se_bge"    , 0xE000, 0xE0FF, 1, ((0x00FF,  0,  1,  0, 0, TYPE_JMP), (0), (0), (0), (0))),
	( "se_ble"    , 0xE000, 0xE1FF, 1, ((0x00FF,  0,  1,  0, 0, TYPE_JMP), (0), (0), (0), (0))),
	( "se_bne"    , 0xE000, 0xE2FF, 1, ((0x00FF,  0,  1,  0, 0, TYPE_JMP), (0), (0), (0), (0))),
	( "se_bns"    , 0xE000, 0xE3FF, 1, ((0x00FF,  0,  1,  0, 0, TYPE_JMP), (0), (0), (0), (0))),
	( "se_blt"    , 0xE000, 0xE4FF, 1, ((0x00FF,  0,  1,  0, 0, TYPE_JMP), (0), (0), (0), (0))),
	( "se_bgt"    , 0xE000, 0xE5FF, 1, ((0x00FF,  0,  1,  0, 0, TYPE_JMP), (0), (0), (0), (0))),
	( "se_beq"    , 0xE000, 0xE6FF, 1, ((0x00FF,  0,  1,  0, 0, TYPE_JMP), (0), (0), (0), (0))),
	( "se_bso"    , 0xE000, 0xE7FF, 1, ((0x00FF,  0,  1,  0, 0, TYPE_JMP), (0), (0), (0), (0))),
	( "se_bc"     , 0xE000, 0xE7FF, 2, ((0x0700,  8,  0, 32, 0, TYPE_JMP), (0x00FF,  0,  1,  0,  1, TYPE_IMM), (0), (0), (0))),
	( "se_bclri"  , 0x6000, 0x61FF, 2, ((0x01F0,  4,  0,  0, 1, TYPE_JMP), (0x000F,  0,  0,  0,  0, TYPE_REG), (0), (0), (0))),
	( "se_bgeni"  , 0x6200, 0x63FF, 2, ((0x01F0,  4,  0,  0, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG), (0), (0), (0))),
	( "se_bmaski" , 0x2C00, 0x2DFF, 2, ((0x01F0,  4,  0,  0, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG), (0), (0), (0))),
	( "se_bseti"  , 0x6400, 0x65FF, 2, ((0x01F0,  4,  0,  0, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG), (0), (0), (0))),
	( "se_btsti"  , 0x6600, 0x67FF, 2, ((0x01F0,  4,  0,  0, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG), (0), (0), (0))),
	( "se_cmpi"   , 0x2A00, 0x2BFF, 2, ((0x01F0,  4,  0,  0, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG), (0), (0), (0))),
	( "se_cmpli"  , 0x2200, 0x23FF, 2, ((0x01F0,  4,  0,  1, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG), (0), (0), (0))),
	( "se_lbz"    , 0x8000, 0x8FFF, 3, ((0x0F00,  6,  0,  0, 2, TYPE_MEM), (0x00F0,  4,  0,  0,  0, TYPE_REG), (0x000F,  0,  0,  0,  1, TYPE_MEM), (0), (0))),
	( "se_lbh"    , 0xA000, 0xAFFF, 3, ((0x0F00,  6,  0,  0, 2, TYPE_MEM), (0x00F0,  4,  0,  0,  0, TYPE_REG), (0x000F,  0,  0,  0,  1, TYPE_MEM), (0), (0))),
	( "se_li"     , 0x4800, 0x4FFF, 2, ((0x07F0,  4,  0,  0, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG), (0), (0), (0))),
	( "se_lwz"    , 0xC000, 0xCFFF, 3, ((0x0F00,  6,  0,  0, 2, TYPE_MEM), (0x00F0,  4,  0,  0,  0, TYPE_REG), (0x000F,  0,  0,  0,  1, TYPE_MEM), (0), (0))),
	( "se_or"     , 0x4400, 0x44FF, 2, ((0x00F0,  4,  0,  0, 1, TYPE_REG), (0x000F,  0,  0,  0,  0, TYPE_REG), (0), (0), (0))),
	( "se_slw"    , 0x4200, 0x42FF, 2, ((0x00F0,  4,  0,  0, 0, TYPE_REG), (0x000F,  0,  0,  0,  2, TYPE_REG), (0), (0), (0))),
	( "se_slwi"   , 0x6C00, 0x6DFF, 2, ((0x01F0,  4,  0,  0, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG), (0), (0), (0))),
	( "se_sraw"   , 0x4100, 0x41FF, 2, ((0x00F0,  4,  0,  0, 0, TYPE_REG), (0x000F,  0,  0,  0,  2, TYPE_REG), (0), (0), (0))),
	( "se_srawi"  , 0x6A00, 0x6BFF, 2, ((0x01F0,  4,  0,  0, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG), (0), (0), (0))),
	( "se_srw"    , 0x4000, 0x40FF, 2, ((0x00F0,  4,  0,  0, 0, TYPE_REG), (0x000F,  0,  0,  0,  2, TYPE_REG), (0), (0), (0))),
	( "se_srwi"   , 0x6800, 0x69FF, 2, ((0x01F0,  4,  0,  0, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG), (0), (0), (0))),
	( "se_stb"    , 0x9000, 0x9FFF, 3, ((0x0F00,  6,  0,  0, 2, TYPE_MEM), (0x00F0,  4,  0,  0,  0, TYPE_REG), (0x000F,  0,  0,  0,  1, TYPE_MEM), (0), (0))),
	( "se_sth"    , 0xB000, 0xBFFF, 3, ((0x0F00,  6,  0,  0, 2, TYPE_MEM), (0x00F0,  4,  0,  0,  0, TYPE_REG), (0x000F,  0,  0,  0,  1, TYPE_MEM), (0), (0))),
	( "se_stw"    , 0xD000, 0xDFFF, 3, ((0x0F00,  6,  0,  0, 2, TYPE_MEM), (0x00F0,  4,  0,  0,  0, TYPE_REG), (0x000F,  0,  0,  0,  1, TYPE_MEM), (0), (0))),
	( "se_subi"   , 0x2400, 0x25FF, 2, ((0x01F0,  4,  0,  1, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG), (0), (0), (0))),
	( "se_subi."  , 0x2600, 0x27FF, 2, ((0x01F0,  4,  0,  1, 1, TYPE_IMM), (0x000F,  0,  0,  0,  0, TYPE_REG), (0), (0), (0))),
)
