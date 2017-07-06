'''
A disasm file for the AArch64 Architecture, ARMv8.
'''

#from envi.archs.aarch64.const import *
#from envi.archs.aarch64.regs import *

#-----------------------------data-----------------------------------------|

'''
All the various tables inittable references
'''
s_4_table = (
	(0b00100001000000000000000000000000, 0b00000000000000000000000000000000, IENC_LS_EXCL),
	(0b00100001100000000000000000000000, 0b00100000000000000000000000000000, IENC_LS_NAPAIR_OFFSET),
	(0b00100001100000000000000000000000, 0b00100000100000000000000000000000, IENC_LS_REGPAIR_POSTI),
	(0b00100001100000000000000000000000, 0b00100001000000000000000000000000, IENC_LS_REGPAIR_OFFSET),
	(0b00100001100000000000000000000000, 0b00100001100000000000000000000000, IENC_LS_REGPAIR_PREI),
	(0,0,IENC_UNDEF),#catch-all
)

s_5_table = (
	(0b00000001000000000000000000000000, 0b00000000000000000000000000000000, IENC_LOG_SHFT_REG),
	(0b00000001001000000000000000000000, 0b00000001000000000000000000000000, IENC_ADDSUB_SHFT_REG),
	(0b00000001001000000000000000000000, 0b00000001001000000000000000000000, IENC_ADDSUB_EXT_REG),
	(0,0, IENC_UNDEF),#catch-all
)

s_6_table = (
	(0b10100001101111110000000000000000, 0b00000000000000000000000000000000, IENC_SIMD_LS_MULTISTRUCT)
	(0b10100001101000000000000000000000, 0b00000000100000000000000000000000, IENC_SIMD_LS_MULTISTRUCT_POSTI),
	(0b10100001100111110000000000000000, 0b00000000000000000000000000000000, IENC_SIMD_LS_ONESTRUCT),
	(0b10100001100000000000000000000000, 0b00000000000000000000000000000000, IENC_SIMD_LS_ONESTRUCT_POSTI),
	(0b00100001100000000000000000000000, 0b00100000000000000000000000000000, IENC_LS_NAPAIR_OFFSET),
	(0b00100001100000000000000000000000, 0b00100000100000000000000000000000, IENC_LS_REGPAIR_POSTI),
	(0b00100001100000000000000000000000, 0b00100001000000000000000000000000, IENC_LS_REGPAIR_OFFSET),
	(0b00100001100000000000000000000000, 0b00100001100000000000000000000000, IENC_LS_REGPAIR_PREI),
	(0,0,IENC_UNDEF), #catch-all
)

s_8_table = (
	(0b00000011000000000000000000000000, 0b00000000000000000000000000000000, IENC_PC_ADDR),
	(0b00000011000000000000000000000000, 0b00000001000000000000000000000000, IENC_ADDSUB),
	(0,0,IENC_UNDEF), #catch-all
)

s_9_table = (
	(0b00000011100000000000000000000000, 0b00000010000000000000000000000000, IENC_LOG_IMM),
	(0b00000011100000000000000000000000, 0b00000010100000000000000000000000, IENC_MOV_WIDE),
	(0b00000011100000000000000000000000, 0b00000011000000000000000000000000, IENC_BITFIELD),
	(0b00000011100000000000000000000000, 0b00000011100000000000000000000000, IENC_EXTRACT),
	(0,0,IENC_UNDEF),#catch-all
)

s_a_table = (
	(0b01100000000000000000000000000000, 0b00100000000000000000000000000000, IENC_CMP_BRANCH_IMM),
	(0b01100000000000000000000000000000, 0b00000000000000000000000000000000, IENC_BRANCH_UNCOND_IMM),
	(0b11100000000000000000000000000000, 0b01000000000000000000000000000000, IENC_BRANCH_COND_IMM),
	(0b11100001000000000000000000000000, 0b11000000000000000000000000000000, IENC_EXCP_GEN),
	(0b11100001110000000000000000000000, 0b11000001000000000000000000000000, IENC_SYS)
	(0,0,IENC_UNDEF),#catch-all
)

s_b_table = (
	(0b01100000000000000000000000000000, 0b00100000000000000000000000000000, IENC_TEST_BRANCH_IMM),
	(0b11100000000000000000000000000000, 0b11000000000000000000000000000000, IENC_BRANCH_UNCOND_REG),
	(0b01100000000000000000000000000000, 0b00000000000000000000000000000000, IENC_BRANCH_UNCOND_IMM),
	(0,0,IENC_UNDEF),#catch-all
)

s_ce_table = (
	(0b00100001000000000000000000000000, 0b00000000000000000000000000000000, IENC_LOAD_REG_LIT),
	(0b00100001000000000000000000000000, 0b00100001000000000000000000000000, IENC_LS_REG_US_IMM),
	(0b00100001001000000000110000000000, 0b00100000000000000000000000000000, IENC_LS_REG_UNSC_IMM),
	(0b00100001001000000000110000000000, 0b00100000000000000000010000000000, IENC_LS_REG_IMM_POSTI),
	(0b00100001001000000000110000000000, 0b00100000000000000000100000000000, IENC_LS_REG_UNPRIV),
	(0b00100001001000000000110000000000, 0b00100000000000000000110000000000, IENC_LS_REG_IMM_PREI),
	(0b00100001001000000000110000000000, 0b00100000001000000000100000000000, IENC_LS_REG_OFFSET),
	(0,0,IENC_UNDEF),#catch-all
)

s_d_table = (
	(0b00000001111000000000000000000000, 0b00000000000000000000000000000000, IENC_ADDSUB_CARRY),
	(0b00000001111000000000100000000000, 0b00000000010000000000000000000000, IENC_COND_CMP_REG),
	(0b00000001111000000000100000000000, 0b00000000010000000000100000000000, IENC_COND_CMP_IMM),
	(0b00000001111000000000000000000000, 0b00000000100000000000000000000000, IENC_COND_SEL),
	(0b00000001000000000000000000000000, 0b00000001000000000000000000000000, IENC_DATA_PROC_3),
	(0b01000001111000000000000000000000, 0b00000000110000000000000000000000, IENC_DATA_PROC_2),
	(0b01000001111000000000000000000000, 0b01000000110000000000000000000000, IENC_DATA_PROC_1),
	(0,0,IENC_UNDEF),#catch-all
)

#Init table to help us find encfam. Either returns an enc, or a mask-val table with an enc
inittable = (
	( None, None ), #0
	( None, None ), #1
	( None, None ), #2
	( None, None ), #3
	( None, s_4_table ), #4
	( None, s_5_table ), #5
	( None, s_6_table ), #6
	(IENC_DATA_SIMD, None), #7
	( None, s_8_table ), #8
	( None, s_9_table ), #9
	( None, s_a_table ), #a
	( None, s_b_table ), #b
	( None, s_ce_table ), #c
	( None, s_d_table ), #d
	( None, s_ce_table ), #e
	(IENC_DATA_SIMD, None), #f
)

'''
ienc_parsers_tmp will be put into a tuple that will contain all iencs and their corresponding function
'''
ienc_parsers_tmp = [None for x in range(IENC_MAX)]

ienc_parsers_tmp[IENC_DATA_SIMD] = p_data_simd
ienc_parsers_tmp[IENC_LS_EXCL] = p_ls_excl
ienc_parsers_tmp[IENC_LS_NAPAIR_OFFSET] = p_ls_napair_offset
ienc_parsers_tmp[IENC_LS_REGPAIR_POSTI] = p_ls_regpair
ienc_parsers_tmp[IENC_LS_REGPAIR_OFFSET] = p_ls_regpair
ienc_parsers_tmp[IENC_LS_REGPAIR_PREI] = p_ls_regpair
ienc_parsers_tmp[IENC_LOG_SHFT_REG] = p_log_shft_reg
ienc_parsers_tmp[IENC_ADDSUB_SHFT_REG] = p_addsub_shft_reg
ienc_parsers_tmp[IENC_ADDSUB_EXT_REG] = p_addsub_ext_reg
ienc_parsers_tmp[IENC_SIMD_LS_MULTISTRUCT] = p_simd_ls_multistruct
ienc_parsers_tmp[IENC_SIMD_LS_MULTISTRUCT_POSTI] = p_simd_ls_multistruct_posti
ienc_parsers_tmp[IENC_SIMD_LS_ONESTRUCT] = p_simd_ls_onestruct
ienc_parsers_tmp[IENC_SIMD_LS_ONESTRUCT_POSTI] = p_simd_ls_onestruct_posti
ienc_parsers_tmp[IENC_PC_ADDR] = p_pc_addr
ienc_parsers_tmp[IENC_ADDSUB_IMM] = p_addsub_imm
ienc_parsers_tmp[IENC_LOG_IMM] = p_log_imm
ienc_parsers_tmp[IENC_MOV_WIDE_IMM] = p_mov_wide_imm
ienc_parsers_tmp[IENC_BITFIELD] = p_bitfield
ienc_parsers_tmp[IENC_EXTRACT] = p_extract
ienc_parsers_tmp[IENC_CMP_BRANCH_IMM] = p_cmp_branch_imm
ienc_parsers_tmp[IENC_BRANCH_UNCOND_IMM] = p_branch_uncond_imm
ienc_parsers_tmp[IENC_BRANCH_COND_IMM] = p_branch_cond_imm
ienc_parsers_tmp[IENC_EXCP_GEN] = p_excp_gen
ienc_parsers_tmp[IENC_SYS] = p_sys
ienc_parsers_tmp[IENC_TEST_BRANCH_IMM] = p_test_branch_imm
ienc_parsers_tmp[IENC_BRANCH_UNCOND_REG] = p_branch_uncond_reg
ienc_parsers_tmp[IENC_LOAD_REG_LIT] = p_load_reg_lit
ienc_parsers_tmp[IENC_LS_REG_US_IMM] = p_ls_reg_us_imm
ienc_parsers_tmp[IENC_LS_REG_UNSC_IMM] = p_ls_reg_unsc_imm
ienc_parsers_tmp[IENC_LS_REG_IMM_POSTI] = p_ls_reg_imm
ienc_parsers_tmp[IENC_LS_REG_UNPRIV] = p_ls_reg_unpriv
ienc_parsers_tmp[IENC_LS_REG_IMM_PREI] = p_ls_reg_imm
ienc_parsers_tmp[IENC_LS_REG_OFFSET] = p_ls_reg_offset
ienc_parsers_tmp[IENC_ADDSUB_CARRY] = p_addsub_carry
ienc_parsers_tmp[IENC_COND_CMP_REG] = p_cond_cmp_reg
ienc_parsers_tmp[IENC_COND_CMP_IMM] = p_cond_cmp_imm
ienc_parsers_tmp[IENC_COND_SEL] = p_cond_sel
ienc_parsers_tmp[IENC_DATA_PROC_3] = p_data_proc_3
ienc_parsers_tmp[IENC_DATA_PROC_2] = p_data_proc_2
ienc_parsers_tmp[IENC_DATA_PROC_1] = p_data_proc_1
ienc_parsers_tmp[IENC_UNDEF] = p_undef

ienc_parsers = tuple(ienc_parsers_tmp)


#--------------------instruction parsing functions----------------------------|


def p_pc_addr(opval,va):
	'''
	Get the A64Opcode parameters for a PC release address instruction
	'''
	op = opval >> 31
	rd = opval & 0xf
	immhi = opval >> 5 & 0x3ffff
	immlo = opval >> 29 & 0x3
	mnem = 'adr'
	opcode = INS_ADR
	olist = (
		A64RegOper(rd, va=va, size=64),
		A64ImmOper((immhi + immlo), va=va)
	)
	if op == 1:
		iflag = IF_P
	else:
		iflag = 0

	return opcode, mnem, olist, iflag, 0

def p_addsub_imm(opval, va):
	'''
	Get the A64Opcode parameters for an Add/Subtract (immediate) instruction
	'''
	sf = opval >> 31 & 0x1
	op = opval >> 30 & 0x1
	S = opval >> 29 & 0x1
	shift = opval >> 22 & 0x3
	rn = opval >> 5 & 0x1f
	rd = opval & 0x1f
	imm = opval >> 10 & 0xfff
	if op == 0b0:
		mnem = 'add'
		opcode = INS_ADD
	else:
		mnem = 'sub'
		opcode = INS_SUB
	if S == 0b0:
		iflag = 0
	else:
		iflag = IF_PSR_S	   
	if shift == 0b00:
		shiftX = 0
	elif shift == 0b01:
		shiftX = 12
	if sf == 0b0:
		olist = (
			A64RegOper(rd, va=va, size=32),
			A64RegOper(rn, va=va, size=32),
			A64ImmOper(imm, shiftX, S_LSL, va)
		)
	else:
		olist = (
			A64RegOper(rd, va=va, size=64),
			A64RegOper(rn, va=va, size=64),
			A64ImmOper(imm, shiftX, S_LSL, va)
		)		
	return opcode, mnem, olist, iflag, 0

def p_log_imm(opval, va):
	'''
	Get the A64Opcode parameters for a logical (immediate) instruction
	'''
	sf = opval >> 31
	opc = opval >> 29 & 0x3
	N = opval >> 22
	immr = opval >> 16 & 0x3f
	imms = opval >> 10 & 0x3f
	rn = opval >> 5 & 0x1f
	rd = opval & 0x1f

	iflags = 0
	
	if opc == 0x00:
		mnem = 'and'
		opcode = INS_AND
	elif opc == 0x01:
		mnem = 'orr'
		opcode = INS_ORR
	elif opc == 0x10:
		mnem = 'eor'
		opcode = INS_EOR
	else:
		mnem = 'and'
		opcode = INS_AND
		iflags = IF_PSR_S
		
	if sf == 0b0 and N == 0b0:
		olist = (
			A64RegOper(rn, va, size=32),
			A64RegOper(rd, va, size=32),
			A64ImmOper((N + imms + immr), 0, S_LSL, va),
		)
	elif sf == 0b1:
		olist = (
			A64RegOper(rn, va, size=64),
			A64RegOper(rd, va, size=64),
			A64ImmOper((N + imms + immr), 0, S_LSL, va),
		)		

	return opcode, mnem, olist, iflags, 0

def p_mov_wide_imm(opval, va):
	'''
	Get the A64Opcode parameters for a Move Wide (immediate) instruction
	'''
	sf = opval >> 31
	opc = opval >> 29 & 0x3
	hw = opval >> 21 & 0x3
	imm16 = opval >> 5 & 0xffff
	rd = opval & 0x1f

	if sf == 0b0:
		olist = (
			A64RegOper(rd, va, size=32),
			A64ImmOper(imm16, hw*0b10000, S_LSL, va),
		)
	else:
		olist = (
			A64RegOper(rd, va, size=64),
			A64ImmOper(imm16, hw*0b10000, S_LSL, va),
		)		
	mnem = 'mov'
	opcode = INS_MOV
	if opc == 0x00:
		iflag = IF_N
	elif opc == 0x10:
		iflag = IF_Z
	elif opc == 0x11:
		iflag = IF_K
	else:
		raise envi.InvalidInstruction(
			mesg="p_undef: invalid instruction (by definition in ARM spec)",
			bytez=struct.pack("<I", opval), va=va)
		opcode = IENC_UNDEF
		mnem = "undefined instruction"
		olist = (
			A64ImmOper(opval),
		)		

	return opcode, mnem, olist, 0,0


#flags before mnemonic?
def p_bitfield(opval, va):
	'''
	Get the parameters for an A64Opcode for a bitfield instruction
	'''
	sf = opval >> 31
	opc = opval >> 29 & 0x3
	N = opval >> 22
	immr = opval >> 16 & 0x3f
	imms = opval >> 10 & 0x3f
	rn = opval >> 5 & 0x1f
	rd = opval >> 5 & 0x1f
	olist = (
		A64ImmOper(opval),
	)
	mnem, opcode, flags = bitfield_table[opc]
	if opcode != IENC_UNDEF:
		if sf == 0b0 and N == 0b0:
			olist = (
				A64RegOper(rd, va, size=32),
				A64RegOper(rn, va, size=32),
				A64ImmOper(immr, va=va),
				A64ImmOper(imms, va=va),
			)
		elif sf == 0b1 and N == 0b1:
			olist = (
				A64RegOper(rd, va, size=64),
				A64RegOper(rn, va, size=64),
				A64ImmOper(immr, va=va),
				A64ImmOper(imms, va=va),
			)	

	return opcode, mnem, olist, flags, 0


bitfield_table = (
	('sbfm', INS_SBFM, (1,1)),
	('bfm', INS_BFM, (0,0)),
	('ubfm', INS_UBFM, (1,0))
	('undefined instruction', IENC_UNDEF, 0)
)

def p_extract(opval, va):
	'''
	Get the parameters for an A64Opcode for a extract instruction
	'''
	sf = opval >> 31
	N = opval >> 22 & 0x1
	rm = opval >> 16 & 0x1f
	imms = opval >> 10 & 0x3f
	rn = opval >> 5 & 0x1f
	rd = opval & 0x1f

	mnem = 'extr'
	opcode = INS_EXTR
	if sf == 0b0 and N == 0b0 and imms & 0x100000 == 0x000000:
		olist = (
			A64RegOper(rd, va, size=32),
			A64RegOper(rn, va, size=32),
			A64RegOper(rm, va, size=32),
			A64ImmOper(imms, 0, S_LSL, va),
		)
	elif sf == 0b0 and N == 0b1:
		olist = (
			A64RegOper(rd, va, size=64),
			A64RegOper(rn, va, size=64),
			A64RegOper(rm, va, size=64),
			A64ImmOper(imms, 0, S_LSL, va),
		)

	return opcode, mnem, olist, 0, 0

def p_branch_uncond_imm(opval, va):
	'''
	Get the parameters for an A64Opcode for a Branch Unconditional (immediate) instruction
	'''
	op = opval >> 31
	imm26 = opval & 0x3ffffffff
	mnem = 'b'
	opcode = INS_B
	if op == 0:
		iflag = 0
	else:
		iflag = IF_L

	olist = (
		A64ImmOper(imm26*0x100, va=va),
	)

	return opcode, mnem, olist, iflag, 0

def p_cmp_branch_imm(opval, va):
	'''
	Get the parameters for an A64Opcode for a Compare Branch (immediate) instruction
	'''
	sf = opval >> 31
	op = opval >> 24 & 0x1
	imm19 = opval >> 5 & 0x7ffff
	rt = opval & 0x1f

	if op == 0:
		mnem = 'cbz'
		opcode = INS_CBZ
	else:
		mnem = 'cbnz'
		opcode = INS_CBNZ
	if sf == 0b0:
		olist = (
			A64RegOper(rt, va, size=32),
			A64Imm32Oper(imm19*0b100, 0, S_LSL, va),
		)
	else:
		olist = (
			A64RegOper(rt, va, size=64),
			A64ImmOper(imm19*0b100, 0, S_LSL, va),
		)

	return opcode, mnem, olist, 0, 0

def p_test_branch_imm(opval, va):
	'''
	Test branch (immediate) instruction
	'''
	pass #FIXME

def p_branch_cond_imm(opval, va):
	'''
	Conditional branch (immediate) instruction
	'''
	pass #FIXME

def p_excp_gen(opval, va):
	'''
	Exception generation instruction
	'''
	opc = opval >> 21 & 0x7
	imm16 = opval >> 5 & 0xffff
	op2 = opval >> 2 & 0x7
	LL = opval & 0x3

	olist = (
		A64ImmOper(imm16, 0, S_LSL, va),
	)
	
	if opc == 0x000:
		if LL == 0x01:
			mnem = 'sbc'
			opcode = INS_SVC
		elif LL == 0x10:
			mnem = 'hvc'
			opcode = INS_HVC
		elif LL == 0x11:
			mnem = 'smc'
			opcode = INS_SMC
		else:
			raise envi.InvalidInstruction(
				mesg="p_undef: invalid instruction (by definition in ARM spec)",
				bytez=struct.pack("<I", opval), va=va)
			opcode = IENC_UNDEF
			mnem = "undefined instruction"
			olist = (
				A64ImmOper(opval)
			)
	elif opc == 0x001:
		mnem = 'brk'
		opcode = INS_BRK
	elif opc == 0x010:
		mnem = 'hlt'
		opcode = INS_HLT
	elif opc == 0x101:
		if LL == 0x01:
			mnem = 'dcps1'
			opcode = INS_DCPS1
		elif LL == 0x10:
			mnem = 'dcps2'
			opcode = INS_DCPS2
		elif LL == 0x11:
			mnem = 'dcps3'
			opcode = INS_DCPS3
		else:
			raise envi.InvalidInstruction(
				mesg="p_undef: invalid instruction (by definition in ARM spec)",
				bytez=struct.pack("<I", opval), va=va)
			opcode = IENC_UNDEF
			mnem = "undefined instruction"
			olist = (
				A64ImmOper(opval)
			)
	else:
		raise envi.InvalidInstruction(
			mesg="p_undef: invalid instruction (by definition in ARM spec)",
			bytez=struct.pack("<I", opval), va=va)
		opcode = IENC_UNDEF
		mnem = "undefined instruction"
		olist = (
			A64ImmOper(opval)
		)
	return (opcode, mnem, olist, 0, 0)

def p_sys(opval, va):
	'''
	Returns parameters for an A64Opcode for a system instruction
	'''
	L = opval >> 21 & 0x1
	op0 = opval >> 19 & 0x3
	op1 = opval >> 16 & 0x7
	crn = opval >> 12 & 0xf
	crm = opval >> 8 & 0xf
	op2 = opval >> 5 & 0x3
	rt = opval & 0x1f
	relevant = opval & 0x3fffff

	if relevant & 0b1110001111000000011111 == 0b0000000100000000011111:
		opcode = INS_MSRI
		mnem = 'msr'
		olist = (
			#FIXME
		)
		#FIXME flags =
		#FIXME simdflags =
		
	elif relevant & 0b1111111111000000011111 == 0b00001100100000000011111:
		opcode = INS_HINT
		mnem = 'hint'
		olist = (
			A64ImmOper(crm + op2, 0, S_LSL, va)
		)
		flags = 0
		simdflags = 0
		
	elif relevant & 0b1111111111000011111111 == 0b00001100110000001011111:
		opcode = INS_CLREX
		mnem = 'clrex'
		olist = (
			A64ImmOper(crm, 0, S_LSL, va)
		)
		flags = 0
		simdflags = 0

	elif relevant & 0b1111111111000011111111 == 0b00001100110000010011111:
		opcode = INS_DSB
		mnem = 'dsb'
		olist = (
			#FIXME
		)
		#FIXME flags
		#FIXME simdflags

	elif relevant & 0b1111111111000011111111 == 0b00001100110000010111111:
		opcode = INS_DMB
		mnem = 'dmb'
		olist = (
			#FIXME
		)
		#FIXME flags
		#FIXME simdflags

	elif relevant & 0b1111111111000011111111 == 0b00001100110000011011111:
		opcode = INS_ISB
		mnem = 'isb'
		olist = (
			#FIXME
		)
		#FIXME flags
		#FIXME simdflags

	elif (L + op0) == 0x001:
		opcode = INS_SYS
		mnem = 'sys'
		olist = (
			A64ImmOper(op1, 0, S_LSL, va),
			#FIXME cn name oper?
			#FIXME cm name oper?
			A64ImmOper(op2, 0, S_LSL, va),
			A64RegOper(rt, va, size=64), #optional operand
		)
		flags = 0
		simdflags = 0

	elif (L + op0) & 0b110 == 0b010:
		opcode = INS_MSRR
		mnem = 'msr'
		olist = (
			#A64RegOper(opval >> 5 & 0x7fff, va), system register?
			A64RegOper(rt, va, size=64),
		)
		flags = 0
		simdflags = 0

	elif (L + op0) & 0b111 == 0b101:
		opcode = INS_SYSL
		mnem = 'sysl'
		olist = (
			A64RegOper(rt, va, size=64),
			A64ImmOper(op1, 0, S_LSL, va),
			#FIXME name oper?
			#FIXME name oper?
			A64ImmOper(op2, 0, S_LSL, va),
		)
		flags = 0
		simdflags = 0

	elif (L + op0) & 0b110 == 0b110:
		opcode = INS_MRS
		mnem = 'mrs'
		olist = (
			A64RegOper(rt, va, size=64),
			#A64RegOper(opval >> 5 & 0x7fff, va) system register? see msrr
		)
		flags = 0
		simdflags = 0

	else:
		raise envi.InvalidInstruction(
			mesg="p_undef: invalid instruction (by definition in ARM spec)",
			bytez=struct.pack("<I", opval), va=va)
		opcode = IENC_UNDEF
		mnem = "undefined instruction"
		olist = (
			A64ImmOper(opval),
		)
		flags = 0
		simdflags = 0
	
	return opcode, mnem, olist, flags, simdflags

def p_branch_uncond_reg(opval, va):
	'''
	Return A64Opcode parameters for an Unconditional Branch (register) instruction
	'''
	opc = opval >> 21 & 0xf
	op2 = opval >> 16 & 0x1f
	op3 = opval >> 10 & 0x3f
	rn = opval >> 5 & 0x1f
	op4 = opval & 0x1f
	if op2 == 0b11111 and op3 == 0b000000 and op4 == 0b00000:
		olist = (
			A64RegOper(rn, va, size=64),
		)
		if opc == 0b0000:
			opcode = INS_BR
			mnem = 'br'
		elif opc == 0b0001:
			opcode = INS_BLR
			mnem = 'blr'
		elif opc == 0b0010:
			opcode = INS_RET
			mnem = 'ret'
		elif opc == 0b0100 and rn == 0b11111:
			opcode = INS_ERET
			mnem = 'eret'
			olist = () #NOT A FIXME, EMPTY LIST
		elif opc == 0b0101 and rn == 0b11111:
			opcode = INS_DRPS
			mnem = 'drps'
			olist = () #NOT A FIXME
		else:
			raise envi.InvalidInstruction(
				mesg="p_undef: invalid instruction (by definition in ARM spec)",
				bytez=struct.pack("<I", opval), va=va)
			opcode = IENC_UNDEF
			mnem = "undefined instruction"
			olist = (
				A64ImmOper(opval),
			)		   
	else:
		raise envi.InvalidInstruction(
			mesg="p_undef: invalid instruction (by definition in ARM spec)",
			bytez=struct.pack("<I", opval), va=va)
		opcode = IENC_UNDEF
		mnem = "undefined instruction"
		olist = (
			A64ImmOper(opval),
		)

	return opcode, mnem, olist, 0,0   

def p_ls_excl(opval, va):
	'''
	Load/store exclusive instruction
	'''
	size = opval >> 30 & 0x3
	o2 = opval >> 23 & 0x1
	L = opval >> 22 & 0x1
	o1 = opval >> 21 & 0x1
	rs = opval >> 16 & 0x1f
	o0 = opval >> 15 & 0x1
	rt2 = opval >> 10 & 0x1f
	rn = opval >> 5 & 0x1f
	rt = opval & 0x1f

	if L == 0b0:
		mnem = 'st'
		opcode = INS_ST
		optional_iflag = IF_L
	else:
		mnem = 'ld'
		opcode = INS_LD
		optional_iflag = IF_A
	if o0 == 0b1:
		iflag |= optional_iflag
	if o2 == 0b0:
		iflag |= IF_X
	if o1 == 0b0:
		iflag |= IF_R
	else:
		iflag |= IF_P
	if size == 0b00:
		iflag |= IF_B
	elif size == 0b01:
		iflag |= IF_H
	
	if size == 0b00 or size == 0b01:
		if o2 == 0b0:
			o10 = o1 + o0
			if L == 0b0:
				olist = (
					A64RegOper(rs, va, size=32),
					A64RegOper(rt, va, size=32),
					A64RegOper(rn, va, size=64),
				)
			else: #L == 1
				olist = (
					A64RegOper(rt, va, size=32),
					A64RegOper(rn, va, size=64),
				)
		else: #o2 == 1
			Lo1o0 = L + o1 + o0
			olist = (
				A64RegOper(rt, va, size=32),
				A64RegOper(rn, va, size=64),
			)
	else:  #size == 10 or 11
		if o2 == 0b0:
			if L == 0b0:
				if o1 == 0b0:
					if size == 0b10:
						olist = (
							A64RegOper(rs, va, size=32),
							A64RegOper(rt, va, size=32),
							A64RegOper(rn, va, size=64),
						)
					else:
						olist = (
							A64RegOper(rs, va, size=32),
							A64RegOper(rt, va, size=64),
							A64RegOper(rn, va, size=64),
						)						
				else:
					if size == 0b10:
						olist = (
							A64RegOper(rs, va, size=32),
							A64RegOper(rt, va, size=32),
							A64RegOper(rt2, va, size=32),
							A64RegOper(rn, va, size=64),
						)
					else:
						olist = (
							A64RegOper(rs, va, size=32),
							A64RegOper(rt, va, size=64),
							A64RegOper(rt2, va, size=64),
							A64RegOper(rn, va, size=64),
						)					 
			else: #L == 1
				if o1 == 0b0:
					if size == 0b10:
						olist = (
							A64RegOper(rt, va, size=32),
							A64RegOper(rn, va, size=64),
						)
					else:
						olist = (
							A64RegOper(rt, va, size=64),
							A64RegOper(rn, va, size=64),
						) 
				else: #o1 == 1x0110
					if size == 0b10:
						olist = (
							A64RegOper(rt, va, size=32),
							A64RegOper(rt2, va, size=32),
							A64RegOper(rn, va, size=64),
						)
					else:
						olist = (
							A64RegOper(rt, va, size=64),
							A64RegOper(rt2, va, size=64),
							A64RegOper(rn, va, size=64),
						)									   
		else: #o2 == 1
			if size == 0b10:
				olist = (
					A64RegOper(rt, va, size=32),
					A64RegOper(rn, va, size=64),
				)
			else:
				olist = (
					A64RegOper(rt, va, size=64),
					A64RegOper(rn, va, size=64),
				)

	return opcode, mnem, olist, iflags, 0

def p_load_reg_lit(opval, va):
	'''
	Load register (literal) instruction
	'''
	opc = opval >> 30 & 0x3
	V = opval >> 26 & 0x1
	imm19 = opval >> 5 & 0x7ffff
	rt = opval & 0x1f
	opcode = INS_LDR
	mnem = 'ldr'
	iflags = 0
	if opc == 0b00:
		olist = (
			A64RegOper(rt, va, size=32),
			A64ImmOper(imm19*0b100, 0, S_LSL, va),
		)
	elif opc == 0b01:
		olist = (
			A64RegOper(rt, va, size=64),
			A64ImmOper(imm19*0b100, 0, S_LSL, va),
		)
	elif opc == 0b10:
		if V == 0b0:
			iflag = IF_SW
			olist = (
				A64RegOper(rt, va, size=64),
				A64ImmOper(imm19*0b100, 0, S_LSL, va),
			)
		else:
			olist = (
				A64RegOper(rt, va, size=128),
				A64ImmOper(imm19*0b100, 0, S_LSL, va),
			)
	else:
		if V == 0b0:
			mnem = 'prfm'
			opcode = INS_PRFM
			olist = (
				prfop[rt],
				A64ImmOper(imm19*0b100, 0, S_LSL, va),
			)
		else:
			raise envi.InvalidInstruction(
				mesg="p_undef: invalid instruction (by definition in ARM spec)",
				bytez=struct.pack("<I", opval), va=va)
			opcode = IENC_UNDEF
			mnem = "undefined instruction"
			olist = (
				A64ImmOper(opval),
			)
	return opcode, mnem, olist, 0, 0

def p_ls_napair_offset(opval, va):
	'''
	Load/store no-allocate pair (offset)
	'''
	opc = opval >> 30 & 0x3
	V = opval >> 26 & 0x1
	L = opval >> 22 & 0x1
	imm7 = opval >> 15 & 0x7f
	rt2 = opval >> 10 & 0x1f
	rn = opval >> 5 & 0x1f
	rt = opval & 0x1f

	if L == 0b0:
		mnem = 'stnp'
		opcode = INS_STNP
	else:
		mnem = 'ldnp'
		opcode = INS_LDNP
	if V == 0b1:
		if opc == 0b00:
			olist = (
				A64RegOper(rt, va, size=32),
				A64RegOper(rt2, va, size=32),
				A64RegOper(rn, va, size=64),
				A64ImmOper(imm7*0b100, 0, S_LSL, va),
			)
		elif opc == 0b01:
			olist = (
				A64RegOper(rt, va, size=64),
				A64RegOper(rt2, va, size=64),
				A64RegOper(rn, va, size=64),
				A64ImmOper(imm7*0b1000, 0, S_LSL, va),
			)
		elif opc == 0b10:
			olist = (
				A64RegOper(rt, va, size=128),
				A64RegOper(rt2, va, size=128),				
				A64RegOper(rn, va, size=64),
				A64ImmOper(imm7*0b10000, 0, S_LSL, va),
			)
		else:
			raise envi.InvalidInstruction(
				mesg="p_undef: invalid instruction (by definition in ARM spec)",
				bytez=struct.pack("<I", opval), va=va)
			opcode = IENC_UNDEF
			mnem = "undefined instruction"
			olist = (
				A64ImmOper(opval),
			)
			
	else:
		if opc == 0b00:
			olist = (
				A64RegOper(rt, va, size=32),
				A64RegOper(rt2, va, size=32),
				A64ImmOper(imm7*0b100, 0, S_LSL, va),
			)
		elif opc == 0b10:
			olist = (
				A64RegOper(rt, va, size=64),
				A64RegOper(rt2, va, size=64),
				A64ImmOper(imm7*0b1000, 0, S_LSL, va),
			)
		else:
			raise envi.InvalidInstruction(
				mesg="p_undef: invalid instruction (by definition in ARM spec)",
				bytez=struct.pack("<I", opval), va=va)
			opcode = IENC_UNDEF
			mnem = "undefined instruction"
			olist = (
				A64ImmOper(opval),
			)
	return opcode, mnem, olist, 0, 0


def p_ls_regpair(opval, va):
	'''
	Load/store register pair (pre-indexed, post-indexed or offset)
	'''
	opc = opval >> 30 & 0x3
	V = opval >> 26 & 0x1
	L = opval >> 22 & 0x1
	imm7 = opval >> 15 & 0x7f
	rt2 = opval >> 10 & 0x1f
	rn = opval >> 5 & 0x1f
	rt = opval & 0x1f

	VL = V + L
	if opc == 0b00: #32-bit variant
		mnem, opcode = ls_regpair_table[VL]
		olist = (
			A64RegOper(rt, va, size=32),
			A64RegOper(rt2,va, size=32),
			A64RegOper(rn, va, size=64),
			A64ImmOper(imm7*0b100),
		)
	elif opc == 0b01:
		if VL == 0b00:
			raise envi.InvalidInstruction(
				mesg="p_undef: invalid instruction (by definition in ARM spec)",
				bytez=struct.pack("<I", opval), va=va)
			opcode = IENC_UNDEF
			mnem = "undefined instruction"
			olist = (
				A64ImmOper(opval),
			)		   
		elif VL == 0b01:
			mnem = 'ldpsw'
			opcode = INS_LDPSW
			olist = (
				A64RegOper(rt, va, size=64),
				A64RegOper(rt2,va, size=64),
				A64RegOper(rn, va, size=64),
				A64ImmOper(imm7*0b100),
			)
		else:
			mnem, opcode = ls_regpair_table[VL]
			olist = (
				A64RegOper(rt, va, size=64),
				A64RegOper(rt2,va, size=64),
				A64RegOper(rn, va, size=64),
				A64ImmOper(imm7*0b1000),
			)			
	elif opc == 0b10:
		mnem, opcode = ls_regpair_table[VL]
		if V == 0b0:
			olist = (
				A64RegOper(rt, va, size=64),
				A64RegOper(rt2,va, size=64),
				A64RegOper(rn, va, size=64),
				A64ImmOper(imm7*0b1000),
			) 
		else:
			olist = (
				A64RegOper(rt, va, size=128),
				A64RegOper(rt2, va, size=128),
				A64RegOper(rn, va, size=64),
				A64ImmOper(imm7*0b10000),
			)
	else:
		raise envi.InvalidInstruction(
			mesg="p_undef: invalid instruction (by definition in ARM spec)",
			bytez=struct.pack("<I", opval), va=va)
		opcode = IENC_UNDEF
		mnem = "undefined instruction"
		olist = (
			A64ImmOper(opval),
		)
	


ls_regpair_table = (
	('stp', INS_STP),
	('ldp', INS_LDP),
	('stp', INS_STP),
	('ldp', INS_LDP),	
)


def p_ls_reg_unsc_imm(opval, va):
	'''
	Load/store register (unscaled immediate)
	'''
	size = opval >> 30 & 0x3
	V = opval >> 26 & 0x1
	opc = opval >> 22 & 0x3
	imm9 = opval >> 12 & 0x1ff
	rn = opval >> 5 & 0x1f
	rt = opval & 0x1f
	   
	if opc == 0b00 or opc == 0b01:
		if opc == 0b01:
			opcode = INS_LDUR
			mnem = 'ldur'
		else:
			opcode = INS_STUR
			mnem = 'stur'
		if V == 0b0:
			if size == 0b11:
				olist = (
					A64RegOper(rt, va, size=64),
					A64RegOper(rn, va, size=64),
					A64ImmOper(imm9, va=va),
				)
			else:
				olist = (
					A64RegOper(rt, va, size=32),
					A64RegOper(rn, va, size=64),
					A64ImmOper(imm9, va=va),
				)
				if size == 0b00:
					iflag |= IF_B
				elif size == 0b01:
					iflag |= IF_H							 
		else:
			if size == 0b00:
				olist = (
					A64RegOper(rt, va, size=8),
					A64RegOper(rn, va, size=64),
					A64ImmOper(imm9, va=va),
				)
			elif size == 0b01:
				olist = (
					A64RegOper(rt, va, size=16),
					A64RegOper(rn, va, size=64),
					A64ImmOper(imm9, va=va),
				)
			elif size == 0b10:
				olist = (
					A64RegOper(rt, va, size=32),
					A64RegOper(rn, va, size=64),
					A64ImmOper(imm9, va=va),
				)
			else:
				olist = (
					A64RegOper(rt, va, size=64),
					A64RegOper(rn, va, size=64),
					A64ImmOper(imm9, va=va),
				)
	else:
		if V == 0b1:
			if opc == 0b10:
				opcode = INS_STUR
				mnem = 'stur'
			else:
				opcode = INS_LDUR
				mnem = 'ldur'
			olist = (
				A64RegOper(rt, va, size=128),
				A64RegOper(rn, va, size=64),
				A64ImmOper(imm9, va=va),
			)
		else:
			if size == 0b11:
				mnem == 'prfum'
				opcode = INS_PRFUM
				olist = (
					prfop[rt],
					A64RegOper(rn, va, size=64),
					A64ImmOper(imm9, va=va),
				)
			else:
				if opc == 0b10:
					olist = (
						A64RegOper(rt, va, size=64),
						A64RegOper(rn, va, size=64),
						A64ImmOper(imm9, va=va),
					)
				else:
					olist = (
						A64RegOper(rt, va, size=32),
						A64RegOper(rn, va, size=64),
						A64ImmOper(imm9, va=va),
					)
				mnem = 'ldur'
				opcode = INS_LDUR
				iflag |= IF_S
				if size == 0b00:
					iflag |= IF_B
				elif size == 0b01:
					iflag |= IF_H
				elif size == 0b10:
					iflag |= IF_W

	return opcode, mnem, olist, flags, 0

def p_ls_reg_unpriv(opval, va):
	'''
	Load/store register (unprivileged)
	'''
	size = opval >> 30 & 0x3
	V = opval >> 26 & 0x1
	opc = opval >> 22 & 0x3
	imm9 = opval >> 12 & 0x1ff
	rn = opval >> 5 & 0x1f
	rt = opval & 0x1f
	if V == 0b0:
		if opc == 0b00:
			mnem = 'sttr'
			opcode = INS_STTR
		else:
			mnem = 'ldtr'
			opcode = INS_LDTR
			if opc == 0b10 or opc == 0b11:
				iflag |= IF_S
				if size == 10:
					iflag |= IF_W
		if size == 0b00:
			iflag |= IF_B
		elif size == 0b01:
			iflag |= IF_H
		if size != 0b11 and opc != 0b10:
			olist = (
				A64RegOper(rt, va, size=32),
				A64RegOper(rn, va, size=64),
				A64ImmOper(imm9, va),
			)
		else:
			olist = (
				A64RegOper(rt, va, size=64),
				A64RegOper(rn, va, size=64),
				A64ImmOper(imm9, va),
			)
	else:
		raise envi.InvalidInstruction(
				mesg="p_undef: invalid instruction (by definition in ARM spec)",
				bytez=struct.pack("<I", opval), va=va)
		opcode = IENC_UNDEF
		mnem = "undefined instruction"
		olist = (
			A64ImmOper(opval),
		)
		iflag = 0
		
	return (opcode, mnem, olist, iflag, 0)		
			
def p_ls_reg_imm(opval, va):
	'''
	Load/store register (immediate post and pre-indexed)
	'''
	size = opval >> 30 & 0x3
	V = opval >> 26 & 0x1
	opc = opval >> 22 & 0x3
	imm9 = opval >> 12 & 0x1ff
	rn = opval >> 5 & 0x1f
	rt = opval & 0x1f
	if V == 0b0:
		if opc == 0b00:
			mnem = 'str'
			opcode = INS_STR
		else:
			mnem = 'ldr'
			opcode = INS_LDR
		if opc == 0b10 or opc == 0b11:
			iflag |= IF_S
			if size == 0b10:
				iflag |= IF_W
		if size == 0b00:
			iflag |= IF_B
		elif size == 0b01:
			iflag |= IF_H
		if opc == 0b10 or size == 0b11:
			olist = (
				A64RegOper(rt, va, size=64),
				A64RegOper(rn, va, size=64),
				A64ImmOper(imm9, va=va),
			)
		else:
			olist = (
				A64RegOper(rt, va, size=32),
				A64RegOper(rn, va, size=64),
				A64ImmOper(imm9, va=va),
			)
	else:
		if opc == 0b00 or opc == 0b10:
			mnem = 'str'
			opcode = INS_STR
		else:
			mnem = 'ldr'
			opcode = INS_LDR
		if size == 0b00:
			if opc == 0b00 or opc == 0b01:
				olist = (
					A64RegOper(rt, va, size=8),
					A64RegOper(rn, va, size=64),
					A64ImmOper(imm9, va=va),
				)
			else:
				olist = (
					A64RegOper(rt, va, size=128),
					A64RegOper(rn, va, size=64),
					A64ImmOper(imm9, va=va),
				)
		elif size == 0b01:
			olist = (
				A64RegOper(rt, va, size=16),
				A64RegOper(rn, va, size=64),
				A64ImmOper(imm9, va=va),
			)
		elif size == 0b10:
			olist = (
				A64RegOper(rt, va, size=32),
				A64RegOper(rn, va, size=64),
				A64ImmOper(imm9, va=va),
			)
		else:
			olist = (
				A64RegOper(rt, va, size=64),
				A64RegOper(rn, va, size=64),
				A64ImmOper(imm9, va=va),
			)

	return opcode, mnem, olist, iflag, 0
		


def p_ls_reg_offset(opval, va):
	'''
	Load/store register (register offset)
	'''
	size = opval >> 30 & 0x3
	V = opval >> 26 & 0x1
	opc = opval >> 22 & 0x3
	rm = opval >> 16 & 0x1f
	option = opval >> 13 & 0x7
	S = opval >> 12 & 0x1
	rn = opval >> 5 & 0x1f
	rt = opval & 0x1f

	if V == 0b0:
		if opc == 0b00:
			mnem = 'str'
			opcode = INS_STR
		else:
			if size == 0b11 and opc == 0b10:
				mnem =  'prfm'
				opcode = INS_PRFM
				olist = (
					#FIXME
				)
				return opcode, mnem, olist, 0, 0
			else:
				mnem = 'ldr'
				opcode = INS_LDR
		if opc == 0b10 or opc == 0b11:
			iflag |= IF_S
			if size == 0b10:
				iflag |= IF_W
		if size == 0b00:
			iflag |= IF_B
		elif size == 0b01:
			iflag |= IF_H
		if opc == 0b10 or size == 0b11:
			#64-bit variant
			pass
		else:
			#32-bit variant
			pass
		
	else:
		if opc == 0b10 or opc == 0b00:
			mnem = 'str'
			opcode = INS_STR
		else:
			mnem = 'ldr'
			opcode = INS_LDR
		if size == 0b00:
			if opc == 0b00 or opc == 0b01:
				olist = (
					#FIXME 8-bit
				)
			else:
				olist = (
					#FIXME 128-bit
				)
		elif size == 0b01:
			olist = (
				#FIXME 16-bit
			)
		elif size == 0b10:
			olist = (
				#FIXME 32-bit
			)
		else:
			olist = (
				#FIXME 64-bit
			)

	return opcode, mnem, olist, iflag, 0

def p_ls_reg_us_imm(opval, va):
	'''
	Load/store register (unsigned immediate)
	'''
	size = opval >> 30 & 0x3
	V = opval >> 26 & 0x1
	opc = opval >> 22 & 0x3
	imm12 = opval >> 10 & 0xfff
	rn = opval >> 5 & 0x1f
	rt = opval & 0x1f
	if V == 0b0:
		if opc == 0b00:
			mnem = 'str'
			opcode = INS_STR
		else:
			if size == 0b11 and opc == 0b10:
				mnem =  'prfm'
				opcode = INS_PRFM
				olist = (
					prfop[rt],
					A64RegOper(rn, va, size=64),
					A64ImmOper(imm12*0b1000, va=va),
				)
				return opcode, mnem, olist, 0, 0
			else:
				mnem = 'ldr'
				opcode = INS_LDR
		if opc == 0b10 or opc == 0b11:
			iflag |= IF_S
			if size == 0b10:
				iflag |= IF_W
		if size == 0b00:
			iflag |= IF_B
		elif size == 0b01:
			iflag |= IF_H
		if opc == 0b10 or size == 0b11:
			A64RegOper(rt, va, size=64),
			A64RegOper(rn, va, size=64),
			A64ImmOper(imm12, va=va),
		else:
			A64RegOper(rt, va, size=32),
			A64RegOper(rn, va, size=64),
			A64ImmOper(imm12, va=va),
		
	else:
		if opc == 0b10 or opc == 0b00:
			mnem = 'str'
			opcode = INS_STR
		else:
			mnem = 'ldr'
			opcode = INS_LDR
		if size == 0b00:
			if opc == 0b00 or opc == 0b01:
				olist = (
					A64RegOper(rt, va, size=8),
					A64RegOper(rn, va, size=64),
					A64ImmOper(imm12, va=va),
				)
			else:
				olist = (
					A64RegOper(rt, va, size=128),
					A64RegOper(rn, va, size=64),
					A64ImmOper(imm12*0b10000, va=va),
				)
		elif size == 0b01:
			olist = (
				A64RegOper(rt, va, size=16),
				A64RegOper(rn, va, size=64),
				A64ImmOper(imm12*0b10, va=va),
			)
		elif size == 0b10:
			olist = (
				A64RegOper(rt, va, size=32),
				A64RegOper(rn, va, size=64),
				A64ImmOper(imm12*0b100, va=va),
			)
		else:
			olist = (
				A64RegOper(rt, va, size=64),
				A64RegOper(rn, va, size=64),
				A64ImmOper(imm12*0b1000, va=va),
			)

	return opcode, mnem, olist, iflag, 0

def p_simd_ls_multistruct(opval, va):
	'''
	AdvSIMD Load/store multiple structures
	'''
	#FIXME olists
	Q = opval >> 30 & 0x1
	L = opval >> 22 & 0x1
	opc = opval >> 12 & 0xf
	size = opval >> 10 & 0x3
	rn = opval >> 5 & 0x1f
	rt = opval & 0x1f
	if opc == 0b0000 or opc == 0b0010:
		olist = (
			#4
		)
		if L == 0b0:
			if opc == 0b0000:
				mnem = 'st4'
				opcode = INS_ST4
			else:
				mnem = 'st1'
				opcode = INS_ST1
		else:
			if opc == 0b0000:
				mnem = 'ld4'
				opcode = INS_LD4
			else:
				mnem = 'ld1'
				opcode = INS_LD1
	elif opc == 0b0100 or opc == 0b0110:
		olist = (
			#3
		)
		if L == 0b0:
			if opc == 0b0100:
				mnem = 'st3'
				opcode = INS_ST3
			else:
				mnem = 'st1'
				opcode = INS_ST1
		else:
			if opc == 0b0100:
				mnem = 'ld3'
				opcode = INS_LD3
			else:
				mnem = 'ld1'
				opcode = INS_LD1
	elif opc == 0b0111:
		olist = (
			#1
		)
		if L == 0b0:
			mnem = 'st1'
			opcode = INS_ST1			
		else:
			mnem = 'ld1'
			opcode = INS_LD1

	elif opc == 0b1000 or opc == 0b1010:
		olist = (
			#2
		)
		if L == 0b0:
			if opc == 0b1000:
				mnem = 'st2'
				opcode = INS_ST2
			else:
				mnem = 'st1'
				opcode = INS_ST1
		else:
			if opc == 0b1000:
				mnem = 'ld2'
				opcode = INS_LD2
			else:
				mnem = 'ld1'
				opcode = INS_LD1
	else:
		raise envi.InvalidInstruction(
				mesg="p_undef: invalid instruction (by definition in ARM spec)",
				bytez=struct.pack("<I", opval), va=va)
		opcode = IENC_UNDEF
		mnem = "undefined instruction"
		olist = (
			A64ImmOper(opval),
		)
		
	return (opcode, mnem, olist, 0, 0)

t_table = (
	'8B'
	'16B'
	'4H'
	'8H'
	'2S'
	'4S'
	'RESERVED'
	'2D'
)

def p_simd_ls_multistruct_posti(opval, va):
	'''
	AdvSIMD load/store multiple structures (post-indexed)
	'''
	#FIXME olists
	Q = opval >> 30 & 0x1
	L = opval >> 22 & 0x1
	rm = opval >> 16 & 0x1f
	opc = opval >> 12 & 0xf
	size = opval >> 10 & 0x3
	rn = opval >> 5 & 0x1f
	rt = opval & 0x1f
	if opc & 0b0010 == 0b0010:
		if L == 0b0:
			mnem = 'st1'
			opcode = INS_ST1
		else:
			mnem = 'ld1'
			opcode = INS_LD1
	if L == 0b0:
		if opc == 0b0000:
			mnem = 'st4'
			opcode = INS_ST4
		elif opc == 0b0100:
			mnem = 'st3'
			opcode = INS_ST3
		elif opc == 0b1000:
			mnem = 'st2'
			opcode = INS_ST2
	else:
		if opc == 0b0000:
			mnem = 'ld4'
			opcode = INS_LD4
		elif opc == 0b0100:
			mnem = 'ld3'
			opcode = INS_LD3
		elif opc == 0b1000:
			mnem = 'ld2'
			opcode = INS_LD2
	if rm != 0b11111:
		if opc == 0b0000 or opc == 0b0010:
			olist = (

			)
		elif opc == 0b0100 or opc == 0b0110:
			olist = (

			)
		elif opc == 0b0111:
			olist = (

			)
		elif opc == 0b1000 or opc == 0b1010:
			olist = (

			)
		else:
			raise envi.InvalidInstruction(
					mesg="p_undef: invalid instruction (by definition in ARM spec)",
					bytez=struct.pack("<I", opval), va=va)
			opcode = IENC_UNDEF
			mnem = "undefined instruction"
			olist = (
				A64ImmOper(opval),
			)
	else:
		if opc == 0b0000 or opc == 0b0010:
			olist = (

			)
		elif opc == 0b0100 or opc == 0b0110:
			olist = (

			)
		elif opc == 0b0111:
			olist = (

			)
		elif opc == 0b1000 or opc == 0b1010:
			olist = (

			)
		else:
			raise envi.InvalidInstruction(
					mesg="p_undef: invalid instruction (by definition in ARM spec)",
					bytez=struct.pack("<I", opval), va=va)
			opcode = IENC_UNDEF
			mnem = "undefined instruction"
			olist = (
				A64ImmOper(opval),
			)

	return opcode, mnem, olist, 0, 0

def p_simd_ls_onestruct(opval, va):
	'''
	AdvSIMD load/store one structure
	'''

def p_simd_ls_onestruct_posti(opval, va):
	'''
	AdvSIMD load/store one structure (post-indexed)
	'''

def p_log_shft_reg(opval, va):
	'''
	Logical (shifted register)
	'''
	sf = opval >> 31 & 0x1
	opc = opval >> 29 & 0x3
	shift = opval >> 22 & 0x3
	N = opval >> 21 & 0x1
	rm = opval >> 16 & 0x1f
	imm6 = opval >> 10 & 0x3f
	rn = opval >> 5 & 0x1f
	rd = opval & 0x1f
	if sf == 0b0:
		olist = (
			A64RegOper(rd, va, size=32),
			A64RegOper(rn, va, size=32),
			A64RegOper(rm, va, size=32),
			#FIXME
		)
	else:
		olist = (
			A64RegOper(rd, va, size=64),
			A64RegOper(rn, va, size=64),
			A64RegOper(rm, va, size=64),
			#FIXME
		)
	if opc == 0b00 or opc == 0b11:
		if N == 0b0:
			mnem = 'and'
			opcode = INS_AND
		else:
			mnem = 'bic'
			opcode = INS_BIC
		if opc == 0b11:
			iflag |= IF_S
	elif opc == 0b01:
		mnem = 'or'
		opcode = INS_OR
		if N == 0b0:
			iflag |= IF_R
		else:
			iflag |= IF_N
	else:
		mnem = 'eo'
		opcode = IF_EO
		if N == 0b0:
			iflag |= IF_R
		else:
			iflag |= IF_N

def p_addsub_shft_reg(opval, va):
	'''
	Add/sub (shifted register)
	'''
	sf = opval >> 31 & 0x1
	op = opval >> 30 & 0x1
	S = opval >> 29 & 0x1
	shift = opval >> 22 & 0x3
	rm = opval >> 16 & 0x1f
	imm6 = opval >> 10 & 0x3f
	rn = opval >> 5 & 0x1f
	rd = opval & 0x1f

	if op ==  0b0:
		mnem = 'add'
		opcode = INS_ADD
	else:
		mnem = 'sub'
		opcode = INS_SUB
	if S == 0b1:
		iflag |= IF_S
	if shift == 0b00:
		shtype = S_LSL
	elif shift == 0b01:
		shtype = S_LSR
	elif shift == 0b10:
		shtype = S_ASR
	else:
		#FIXME
		shtype = 0
		
	if sf == 0b0:
		olist = (
			A64RegOper(rd, va, size=32),
			A64RegOper(rn, va, size=32),
			A64RegOper(rm, va, size=32),
			A64ShiftOper(rm, shtype, imm6),
		)
	else:
		olist = (
			A64RegOper(rd, va, size=64),
			A64RegOper(rn, va, size=64),
			A64RegOper(rm, va, size=64),
			A64ShiftOper(rm, shtype, imm6),
		)

	return opcode, mnem, olist, iflag, 0

def p_addsub_ext_reg(opval, va):
	'''
	Add/sub (extended register)
	'''
	#FIXME this is unclear and almost certainly wrong
	sf = opval >> 31 & 0x1
	op = opval >> 30 & 0x1
	S = opval >> 29 & 0x1
	opt = opval >> 22 & 0x3
	rm = opval >> 16 & 0x1f
	option = opval >> 13 & 0x7
	imm3 = opval >> 10 & 0x7
	rn = opval >> 5 & 0x1f
	rd = opval & 0x1f
	
	if op ==  0b0:
		mnem = 'add'
		opcode = INS_ADD
	else:
		mnem = 'sub'
		opcode = INS_SUB
	if S == 0b1:
		iflag |= IF_S
	if option & 0b011 == 0b011:
		sizeRM = 64
	else:
		sizeRM = 32
	if rd == 0b11111 or rn ==  0b11111:
		if option == 0b010:
			extoper = 'LSL'
	else:
		extoper = exttable[option]

	if sf == 0b0:
		olist = (
			A64RegOper(rd, va, size=32),
			A64RegOper(rn, va, size=32),
			A64RegOper(rm, va, size=32),
			A64ExtendOper(rm, extoper, imm3),
		)
	else:
		olist = (
			A64RegOper(rd, va, size=64),
			A64RegOper(rn, va, size=64),
			A64RegOper(rm, va, size=sizeRM),
			
		)

	return opcode, mnem, olist, iflag, 0

exttable = (
	'UXTB',
	'UXTH',
	'UXTW',
	'UXTX',
	'SXTB',
	'SXTH',
	'SXTW',
	'SXTX',
)


		
def p_addsub_carry(opval, va):
	'''
	Add/sub (with carry)
	'''
	sf = opval >> 31 & 0x1
	op = opval >> 30 & 0x1
	S = opval >> 29 & 0x1
	rm = opval >> 16 & 0x1f
	opcode2 = opval >> 10 & 0x3f
	rn = opval >> 5 & 0x1f
	rd = opval & 0x1f
	if opcode2 == 0b000000:
		if op ==  0b0:
			mnem = 'adc'
			opcode = INS_ADC
		else:
			mnem = 'sbc'
			opcode = INS_SBC
		if S == 0b1:
			iflag |= IF_S
		if sf == 0b0:
			olist = (
				A64RegOper(rd, va, size=32),
				A64RegOper(rn, va, size=32),
				A64RegOper(rm, va, size=32),
			)
		else:
			olist = (
				A64RegOper(rd, va, size=64),
				A64RegOper(rn, va, size=64),
				A64RegOper(rm, va, size=64),
			)
	else:
		raise envi.InvalidInstruction(
				mesg="p_undef: invalid instruction (by definition in ARM spec)",
				bytez=struct.pack("<I", opval), va=va)
		opcode = IENC_UNDEF
		mnem = "undefined instruction"
		olist = (
			A64ImmOper(opval),
		)
		iflag = 0

		
	return opcode, mnem, olist, iflag, 0

def p_cond_cmp_reg(opval, va):
	'''
	Conditional compare (register)
	'''

def p_cond_cmp_imm(opval, va):
	'''
	Conditional compare (immediate)
	'''

def p_cond_sel(opval, va):
	'''
	Conditional select
	'''

def p_data_proc_3(opval, va):
	'''
	Data processing (3 source)
	'''

def p_data_proc_2(opval, va):
	'''
	Data processing (2 source)
	'''

def p_data_proc_1(opval, va):
	'''
	Data processing (1 source)
	'''

datasimdtable = (
	(0x5f200000, 0x1e000000, IENC_FP_FP_CONV), #p_fp_fp_conv
	(0x5f200c00, 0x1e200400, IENC_FP_COND_COMPARE), #p_fp_cond_compare
	(0x5f200c00, 0x1e200800, IENC_FP_DP2), #p_fp_dp2
	(0x5f200c00, 0x1e200c00, IENC_FP_COND_SELECT), #p_fp_cond_select
	(0x5f201c00, 0x1e201000, IENC_FP_IMMEDIATE), #p_fp_immediate
	(0x5f203c00, 0x1e202000, IENC_FP_COMPARE), #p_fp_compare
	(0x5f207c00, 0x1e204000, IENC_FP_DP1), #p_fp_dp1
	(0x5f20fc00, 0x1e200000, IENC_FP_INT_CONV), #p_fp_int_conv
	(0x5f000000, 0x1f000000, IENC_FP_DP3), #p_fp_dp3
	(0x9f200400, 0x0e200400, IENC_SIMD_THREE_SAME), #p_simd_three_same
	(0x9f200c00, 0x0e200000, IENC_SIMD_THREE_DIFF), #p_simd_three_diff
	(0x9f3e0c00, 0x0e200800, IENC_SIMD_TWOREG_MISC), #p_simd_tworeg_misc
	(0x9f3e0c00, 0x0e300800, IENC_SIMD_ACROSS_LANES), #p_simd_across_lanes
	(0x9fe08400, 0x0e000400, IENC_SIMD_COPY), #p_simd_copy
	(0x9f000400, 0x0f000000, IENC_SIMD_VECTOR_IE), #p_simd_vector_ie
	(0x9f800400, 0x0f000400, IENC_SIMD_MOD_IMM), #p_simd_mod_imm (also shift_imm)
	(0xbf208c00, 0x0e000000, IENC_SIMD_TBL_TBX), #p_simd_tbl_tbx
	(0xbf208c00, 0x0e000800, IENC_SIMD_ZIP_UZP_TRN), #p_simd_zip_uzp_trn
	(0xbf208400, 0x2e000000, IENC_SIMD_EXT), #p_simd_ext
	(0xdf200400, 0x5e200400, IENC_SIMD_SCALAR_THREE_SAME), #p_simd_scalar_three_same
	(0xdf200c00, 0x5e200000, IENC_SIMD_SCALAR_THREE_DIFF), #p_simd_scalar_three_diff
	(0xdf3e0c00, 0x5e200800, IENC_SIMD_SCALAR_TWOREG_MISC), #p_simd_scalar_tworeg_misc
	(0xdf3e0c00, 0x5e300800, IENC_SIMD_SCALAR_PAIRWISE), #p_simd_scalar_pairwise
	(0xdfe08400, 0x5e300800, IENC_SIMD_SCALAR_COPY), #p_simd_scalar_copy
	(0xdf000400, 0x5f000000, IENC_SIMD_SCALAR_IE), #p_simd_scalar_ie
	(0xdf800400, 0x5f000400, IENC_SIMD_SCALAR_SHIFT_IMM), #p_simd_scalar_shift_imm
	(0xff3e0c00, 0x4e280800, IENC_CRPYTO_AES), #p_crypto_aes
	(0xff208c00, 0x5e000000, IENC_CRYPTO_THREE_SHA), #p_crypto_three_sha
	(0xff3e0c00, 0x5e280800, IENC_CRYPTO_TWO_SHA), #p_crypto_two_sha
)
def p_data_simd(opval, va):
	for mask,val,penc in datasimdtable:
		if (opval & mask) == val:
			enc = penc
			break
	opcode, mnem, olist, flags, simdflags = ienc_parsers[enc](opval, va)
	return opcode, mnem, olist, flags, simdflags

def p_fp_fp_conv(opval, va):
	sf = opval >> 31
	s = opval >> 29 & 0x1
	typ = opval >> 22 & 0x3
	mode = opval >> 19 & 0x3
	opcode = opval >> 16 & 0x7
	scale = opval >> 10 & 0x3f
	rn = opval >> 5 & 0x1f
	rd = opval & 0x1f
	relevant = s + mode + opcode
	#First get the mnem and opcode
	if relevant == 0b00000010:
		mnem = 'scvtf'
		opcode = INS_SCVTF
	elif relevant == 0b00000011:
		mnem = 'ucvtf'
		opcode = INS_UCVTF
	elif relevant == 0b00011000:
		mnem = 'fcvtzs'
		opcode = INS_FCVTZS
	elif relevant == 0b00011001:
		mnem = 'fcvtzu'
		opcode = INS_FCVTZU
	else:
		raise envi.InvalidInstruction(
		mesg="p_undef: invalid instruction (by definition in ARM spec)",
		bytez=struct.pack("<I", opval), va=va)
		opcode = IENC_UNDEF
		mnem = "undefined instruction"
		olist = (
			A64ImmOper(opval),
		)
		return opcode, mnem, olist, 0,0

	if sf == 0 and typ == 0b00:
		olist = (
			A64RegOper(rd, va, size=32),
			A64RegOper(rn, va, size=32),
			A64ImmOper(64-scale),
		)
	elif sf == 0 and typ == 0b01:
		olist = (
			A64RegOper(rd, va, size=64),
			A64RegOper(rn, va, size=32),
			A64ImmOper(64-scale),
		)
	elif sf == 1 and typ == 0b00:
		olist = (
			A64RegOper(rd, va, size=32),
			A64RegOper(rn, va, size=64),
			A64ImmOper(64-scale),
		)
	elif sf == 1 and typ == 0b01:
		olist = (
			A64RegOper(rd, va, size=64),
			A64RegOper(rn, va, size=64),
			A64ImmOper(64-scale),
		)
	else:
		raise envi.InvalidInstruction(
		mesg="p_undef: invalid instruction (by definition in ARM spec)",
		bytez=struct.pack("<I", opval), va=va)
		opcode = IENC_UNDEF
		mnem = "undefined instruction"
		olist = (
			A64ImmOper(opval),
		)
		return opcode, mnem, olist, 0,0
	return opcode, mnem, olist, 0, 0

def p_fp_cond_compare(opval, va):
	m = opval >> 31 & 0x1
	s = opval >> 29 & 0x1
	typ = opval >> 22 & 0x3
	rm = opval >> 16 & 0x1f
	cond = opval >> 12 & 0xf
	rn = opval >> 5 & 0x1f
	op = opval >> 4 & 0x1
	nzcv = opval & 0xf
	mnem = 'fccmp'
	opcode = INS_FCCMP
	if m == 0 and s == 0 and op == 0:
		iflags |= 0
	elif m == 0 and s == 0 and op == 1:
		iflags |= IF_E
	else:
		raise envi.InvalidInstruction(
		mesg="p_undef: invalid instruction (by definition in ARM spec)",
		bytez=struct.pack("<I", opval), va=va)
		opcode = IENC_UNDEF
		mnem = "undefined instruction"
		olist = (
			A64ImmOper(opval),
		)
		return opcode, mnem, olist, 0,0
	if typ == 0b00:
		olist = (
			A64RegOper(rn, va, size=32),
			A64RegOper(rm, va, size=32),
			A64ImmOper(nzcv),
			#ConditionOper
		)
	elif typ == 0b01:
		olist = (
			A64RegOper(rn, va, size=64),
			A64RegOper(rm, va, size=64),
			A64ImmOper(nzcv),
			#ConditionOper
		)
	else:
		raise envi.InvalidInstruction(
		mesg="p_undef: invalid instruction (by definition in ARM spec)",
		bytez=struct.pack("<I", opval), va=va)
		opcode = IENC_UNDEF
		mnem = "undefined instruction"
		olist = (
			A64ImmOper(opval),
		)
		return opcode, mnem, olist, 0,0

	return opcode, mnem, olist, iflags, 0

fp_dp2_table = (
	(INS_FMUL, 'fmul'),
	(INS_FDIV, 'fdiv'),
	(INS_FADD, 'fadd'),
	(INS_FSUB, 'fsub'),
	(INS_FMAX, 'fmax'),
	(INS_FMIN, 'fmin'),
	(INS_MAXNM, 'fmaxnm'),
	(INS_MINNM, 'fminnm'),
	(INS_FNMUL, 'fnmul'),
	(0, 0),
)
def p_fp_dp2(opval, va):
	m = opval >> 31
	s = opval >> 29 & 0x1
	typ = opval >> 22 & 0x3
	rm = opval >> 16 & 0x1f
	opc = opval >> 12 & 0xf
	rn = opval >> 5 & 0x1f
	rd = opval & 0x1f
	if m + s == 0:
		opcode, mnem = fp_dp2_table[opc]
		if typ == 0b00:
			olist = (
				A64RegOper(rd, va, size=32),
				A64RegOper(rn, va, size=32),
				A64RegOper(rm, va, size=32),
			)
		elif typ == 0b01:
			olist = (
				A64RegOper(rd, va, size=64),
				A64RegOper(rn, va, size=64),
				A64RegOper(rm, va, size=64),
			)
		else:
			raise envi.InvalidInstruction(
			mesg="p_undef: invalid instruction (by definition in ARM spec)",
			bytez=struct.pack("<I", opval), va=va)
		return opcode, mnem, olist, 0,0
	else:
		raise envi.InvalidInstruction(
		mesg="p_undef: invalid instruction (by definition in ARM spec)",
		bytez=struct.pack("<I", opval), va=va)
		opcode = IENC_UNDEF
		mnem = "undefined instruction"
		olist = (
			A64ImmOper(opval),
		)
		return opcode, mnem, olist, 0,0
	return opcode, mnem, olist, 0, 0

def p_fp_cond_select(opval, va):
	m = opval >> 31
	s = opval >> 29 & 0x1
	typ = opval >> 22 & 0x3
	rm = opval >> 16 & 0x1f
	cond = opval >> 12 & 0xf
	rn = opval >> 5 & 0x1f
	rd = opval & 0x1f
	mnem = 'fcsel'
	opcode = INS_FCSEL
	if m == 0 and s == 0:
		if typ == 0b00:
			olist = (
				A64RegOper(rd, va, size=32),
				A64RegOper(rn, va, size=32),
				A64RegOper(rm, va, size=32),
				#cond
			)
		elif typ == 0b01:
			olist = (
				A64RegOper(rd, va, size=64),
				A64RegOper(rn, va, size=64),
				A64RegOper(rm, va, size=64),
				#cond
			)
		else:
			raise envi.InvalidInstruction(
			mesg="p_undef: invalid instruction (by definition in ARM spec)",
			bytez=struct.pack("<I", opval), va=va)return opcode, mnem, olist, 0,0
	else:
		raise envi.InvalidInstruction(
		mesg="p_undef: invalid instruction (by definition in ARM spec)",
		bytez=struct.pack("<I", opval), va=va)
		opcode = IENC_UNDEF
		mnem = "undefined instruction"
		olist = (
			A64ImmOper(opval),
		)
		return opcode, mnem, olist, 0,0
	return opcode, mnem, olist, 0, 0

def p_fp_immediate(opval, va):
	m = opval >> 31
	s = opval >> 29 & 0x1
	typ = opval >> 22 & 0x3
	o1 = opval >> 21 & 0x1
	rm = opval >> 16 & 0x1f
	o0 = opval >> 15 & 0x1
	ra = opval >> 10 & 0x1f
	rn = opval >> 5 & 0x1f
	rd = opval & 0x1f
	if o0 == 0:
		if o1 == 0:
			mnem = 'fmadd'
			opcode = INS_FMADD
		else:
			mnem = 'fnmadd'
			opcode = INS_FNMADD
	else:
		if o1 == 0:
			mnem = 'fmsub'
			opcode = INS_FMSUB
		else:
			mnem = 'fnmsub'
			opcode = INS_FNMSUB
	if m == 0 and s == 0:
		if typ == 0b00:
			olist = (
				A64RegOper(rd, va, size=32),
				A64RegOper(rn, va, size=32),
				A64RegOper(rm, va, size=32),
				A64RegOper(ra, va, size=32),
			)
		elif typ == 0b01:
			olist = (
				A64RegOper(rd, va, size=64),
				A64RegOper(rn, va, size=64),
				A64RegOper(rm, va, size=64),
				A64RegOper(ra, va, size=64),
			)
		else:
			raise envi.InvalidInstruction(
			mesg="p_undef: invalid instruction (by definition in ARM spec)",
			bytez=struct.pack("<I", opval), va=va)
			)
			return opcode, mnem, olist, 0,0
	else:
		raise envi.InvalidInstruction(
		mesg="p_undef: invalid instruction (by definition in ARM spec)",
		bytez=struct.pack("<I", opval), va=va)
return opcode, mnem, olist, 0,0
	return opcode, mnem, olist, 0, 0

def p_fp_compare(opval, va):
	m = opval >> 31
	s = opval >> 29 & 0x1
	typ = opval >> 22 & 0x3
	rm = opval >> 16 & 0x1f
	op = opval >> 14 & 0x3
	rn = opval >> 5 & 0x1f
	opcode2 = opval & 0x1f
	mnem = 'fcmp'
	opcode = INS_FCMP
	if m == 0 and s == 0 and op == 0b00:
		if typ == 0b00:
			if opcode2 == 0b00000 or opcode2 == 0b10000:
				olist = (
					A64RegOper(rn, va, size=32),
					A64RegOper(rm, va, size=32),
				)
			elif opcode2 == 0b01000 or opcode2 == 0b11000:
				olist = (
					A64RegOper(rn, va, size=32),
					A64ImmOper(0, va=va),
				)
			else:
				raise envi.InvalidInstruction(
				mesg="p_undef: invalid instruction (by definition in ARM spec)",
				bytez=struct.pack("<I", opval), va=va)
				opcode = IENC_UNDEF
				mnem = "undefined instruction"
				olist = (
					A64ImmOper(opval),
				)
				return opcode, mnem, olist, 0,0
		elif typ == 0b01:
			if opcode2 == 0b00000 or opcode2 == 0b10000:
				olist = (
					A64RegOper(rn, va, size=64),
					A64RegOper(rm, va, size=64),
				)
			elif opcode2 == 0b01000 or opcode2 == 0b11000:
				olist = (
					A64RegOper(rn, va, size=64),
					A64ImmOper(0, va=va),
				)
			else:
				raise envi.InvalidInstruction(
				mesg="p_undef: invalid instruction (by definition in ARM spec)",
				bytez=struct.pack("<I", opval), va=va)
				opcode = IENC_UNDEF
				mnem = "undefined instruction"
				olist = (
					A64ImmOper(opval),
				)
				return opcode, mnem, olist, 0,0
		else:
			raise envi.InvalidInstruction(
			mesg="p_undef: invalid instruction (by definition in ARM spec)",
			bytez=struct.pack("<I", opval), va=va)
			opcode = IENC_UNDEF
			mnem = "undefined instruction"
			olist = (
				A64ImmOper(opval),
			)
			return opcode, mnem, olist, 0,0
	else:
		raise envi.InvalidInstruction(
		mesg="p_undef: invalid instruction (by definition in ARM spec)",
		bytez=struct.pack("<I", opval), va=va)
return opcode, mnem, olist, 0,0
	if opcode2 >> 4 == 1:
		iflags |= IF_E
	return opcode, mnem, olist, iflags, 0

fp_dp1_table = (
	('fmov', INS_FMOV, 0),
	('fabs', INS_FABS, 0),
	('fneg', INS_FNEG, 0),
	('fsqrt', INS_FSQRT, 0),
	(0, 0, 0), #Missing instr
	('fcvt', INS_FCVT, 0),
	(0, 0, 0), #Missing instr
	('fcvt', INS_FCVT, 0),
	('frint', INS_FRINT, IF_N),
	('frint', INS_FRINT, IF_P),
	('frint', INS_FRINT, IF_M),
	('frint', INS_FRINT, IF_Z),
	('frint', INS_FRINT, IF_A),
	('frint', INS_FRINT, IF_X),
	(0, 0, 0), #Missing instr
	('frint', INS_FRINT, IF_I),
	(0, 0, 0), #Catch-all
)
def p_fp_dp1(opval, va):
	m = opval >> 31
	s = opval >> 29 & 0x1
	typ = opval >> 22 & 0x3
	opc = opval >> 15 & 0x3f
	rn = opval >> 5 & 0x1f
	rd = opval & 0x1f
	mnem, opcode, iflags = fp_dp1_table[opc]
	if mnem == 0:
		raise envi.InvalidInstruction(
		mesg="p_undef: invalid instruction (by definition in ARM spec)",
		bytez=struct.pack("<I", opval), va=va)
		opcode = IENC_UNDEF
		mnem = "undefined instruction"
		olist = (
			A64ImmOper(opval),
		)
		return opcode, mnem, olist, 0,0
	elif m == 0 and s == 0:
		if typ == 0b00:
			if opc == 0b000101:
				olist = (
					A64RegOper(rd, va, size=64),
					A64RegOper(rn, va, size=32),
				)
			elif opc == 0b000111:
				olist = (
					#16 Register (rd)
					A64RegOper(rn, va, size=32)
				)
			else:
				olist = (
					A64RegOper(rd, va, size=32),
					A64RegOper(rn, va, size=32),
				)
		elif typ == 0b01:
			if opc == 0b000100:
				olist = (
					A64RegOper(rd, va, size=32),
					A64RegOper(rn, va, size=64),
				)
			elif opc == 0b000111:
				olist = (
					#16 Register (rd)
					A64RegOper(rn, va, size=64),
				)
			else:
				olist = (
					A64RegOper(rd, va, size=64),
					A64RegOper(rn, va, size=64),
				)
		elif typ == 0b11:
			if opc == 0b000100:
				olist = (
					A64RegOper(rd, va, size=32),
					A64RegOper(rn, va, size=16),
				)
			elif opc == 0b000111:
				olist = (
					A64RegOper(rd, va, size=64),
					A64RegOper(rn, va, size=16),
				)
			else:
				raise envi.InvalidInstruction(
				mesg="p_undef: invalid instruction (by definition in ARM spec)",
				bytez=struct.pack("<I", opval), va=va)
				opcode = IENC_UNDEF
				mnem = "undefined instruction"
				olist = (
					A64ImmOper(opval),
				)
				return opcode, mnem, olist, 0,0
		else:
			raise envi.InvalidInstruction(
			mesg="p_undef: invalid instruction (by definition in ARM spec)",
			bytez=struct.pack("<I", opval), va=va)
			opcode = IENC_UNDEF
			mnem = "undefined instruction"
			olist = (
				A64ImmOper(opval),
			)
			return opcode, mnem, olist, 0,0
	else:
		raise envi.InvalidInstruction(
		mesg="p_undef: invalid instruction (by definition in ARM spec)",
		bytez=struct.pack("<I", opval), va=va)
		return opcode, mnem, olist, 0,0

	return opcode, mnem, olist, iflags, 0

def p_fp_int_conv(opval, va):
	sf = opval >> 31
	s = opval >> 29 & 0x1
	typ = opval >> 22 & 0x3
	rmode = opval >> 19 & 0x3
	opc = opval >> 16 & 0x7
	rn = opval >> 5 & 0x1f
	rd = opval & 0x1f
	if opc >> 1 & 0x1 == 0:
		mnem = 'fcvt'
		opcode = INS_FCVT
		if rmode == 0b00:
			if opc >> 2 & 0x1 == 0:
				iflags |= IF_N
			else:
				iflags |= IF_A
		elif rmode == 0b01:
			iflags |= IF_P
		elif rmode == 0b10:
			iflags |= IF_M
		else:
			iflags |= IF_Z
		if opc >> 0 & 0x1 == 0:
			iflags |= IF_S
		else:
			iflags |= IF_U
		
		if sf == 0 and typ == 0b00:
			olist = (
				A64RegOper(rd, va, size=32),
				A64RegOper(rn, va, size=32),
			)
		elif sf == 0 and typ == 0b01:
			olist = (
				A64RegOper(rd, va, size=32),
				A64RegOper(rn, va, size=64),
			)
		elif sf == 1 and typ == 0b00:
			olist = (
				A64RegOper(rd, va, size=64),
				A64RegOper(rn, va, size=32),
			)
		elif sf == 1 and typ == 0b01:
			olist = (
				A64RegOper(rd, va, size=64),
				A64RegOper(rn, va, size=64),
			)
		else:
			raise envi.InvalidInstruction(
			mesg="p_undef: invalid instruction (by definition in ARM spec)",
			bytez=struct.pack("<I", opval), va=va)
			return opcode, mnem, olist, 0,0
	else:
		if opc >> 2 & 0x1 == 0:
			if opc >> 0 & 0x1 == 0:
				mnem = 'scvtf'
				opcode = INS_SCVTF
				iflags = 0
			else:
				mnem = 'ucvtf'
				opcode = INS_UCVTF
				iflags = 0
			if sf == 0 and typ == 0b00:
				olist = (
					A64RegOper(rd, va, size=32),
					A64RegOper(rn, va, size=32),
				)
			elif sf == 0 and typ == 0b01:
				olist = (
					A64RegOper(rd, va, size=64),
					A64RegOper(rn, va, size=32),
				)
			elif sf == 1 and typ == 0b00:
				olist = (
					A64RegOper(rd, va, size=32),
					A64RegOper(rn, va, size=64),
				)
			elif sf == 1 and typ == 0b01:
				olist = (
					A64RegOper(rd, va, size=64),
					A64RegOper(rn, va, size=64),
				)
		else:
			mnem = 'fmov'
			opcode = INS_FMOV
			iflags = 0
			if sf == 0 and typ == 0b00 and rmode == 0b00 and opc & 0x1 == 1:
				olist = (
					A64RegOper(rd, va, size=32),
					A64RegOper(rd, va, size=32),
				)
			elif sf == 0 and typ == 0b00 and rmode == 0b00 and opc & 0x1 == 0:
				olist = (
					A64RegOper(rd, va, size=32),
					A64RegOper(rd, va, size=32),
				)
			elif sf == 1 and typ == 0b01 and rmode == 0b00 and opc & 0x1 == 1:
				olist = (
					A64RegOper(rd, va, size=64),
					A64RegOper(rn, va, size=64),
				)
			elif sf == 1 and typ == 0b10 and rmode == 0b01 and opc & 0x1 == 1:
				olist = (
					#top half of 128-bit reg (rd)
					A64RegOper(rn, va, size=64),
				)
			elif sf == 1 and typ == 0b01 and rmode == 0b00 and opc & 0x1 == 0:
				olist = (
					A64RegOper(rd, va, size=64),
					A64RegOper(rn, va, size=64),
				)
			elif sf == 1 and typ == 0b10 and rmode == 0b01 and opc & 0x1 == 1:
				olist = (
					A64RegOper(rd, va, size=64),
					#top half of 128-bit reg (rn)
				)
			else:
				raise envi.InvalidInstruction(
				mesg="p_undef: invalid instruction (by definition in ARM spec)",
				bytez=struct.pack("<I", opval), va=va)
				opcode = IENC_UNDEF
				mnem = "undefined instruction"
				olist = (
					A64ImmOper(opval),
				)
				return opcode, mnem, olist, 0,0
	return opcode, mnem, olist, iflags, 0

def p_fp_ds3(opval, va):
	m = opval >> 31
	s = opval >> 29 & 0x1
	typ = opval >> 22 & 0x3
	o1 = opval >> 21 & 0x1
	rm = opval >> 16 & 0x1f
	o0 = opval >> 15 & 0x1
	ra = opval >> 10 & 0x1f
	rn = opval >> 5 & 0x1f
	rd = opval & 0x1f
	if m == 0 and s == 0:
		if o1 == 0 and o0 == 0:
			mnem = 'fmadd'
			opcode = INS_FMADD
		elif o1 == 0 and o0 == 1:
			mnem = 'fmsub'
			opcode = INS_FMSUB
		elif o1 == 1 and o0 == 0:
			mnem = 'fnmadd'
			opcode = INS_FNMADD
		else:
			mnem = 'fnmsub'
			opcode = INS_FNMSUB
		if typ == 0b00:
			olist = (
				A64RegOper(rd, va, size=32),
				A64RegOper(rn, va, size=32),
				A64RegOper(rm, va, size=32),
				A64RegOper(ra, va, size=32),
			)
		elif typ == 0b01:
			olist = (
				A64RegOper(rd, va, size=32),
				A64RegOper(rn, va, size=32),
				A64RegOper(rm, va, size=32),
				A64RegOper(ra, va, size=32),
			)
		else:
			raise envi.InvalidInstruction(
			mesg="p_undef: invalid instruction (by definition in ARM spec)",
			bytez=struct.pack("<I", opval), va=va)
			opcode = IENC_UNDEF
			mnem = "undefined instruction"
			olist = (
				A64ImmOper(opval),
			)
			return opcode, mnem, olist, 0,0
	else:
		raise envi.InvalidInstruction(
		mesg="p_undef: invalid instruction (by definition in ARM spec)",
		bytez=struct.pack("<I", opval), va=va)

def p_undef(opval, va):
	'''
	Undefined encoding family
	'''
	# FIXME: make this an actual opcode with the opval as an imm oper
	raise envi.InvalidInstruction(
			mesg="p_undef: invalid instruction (by definition in ARM spec)",
			bytez=struct.pack("<I", opval), va=va)
	opcode = IENC_UNDEF
	mnem = "undefined instruction"
	olist = (
		A64ImmOper(opval),
	)
		
	return (opcode, mnem, olist, 0, 0)


#------------------------------classes---------------------------------------|







class A64Operand(envi.Operand):
	'''
	Superclass for all types of A64 instruction operands
	'''
	tsize = 4
	def involvesPC(self):
		return False

	def getOperAddr(self, op, emu=None):
		return None

class A64RegOper(A64Operand):
	'''
	Subclass of A64Operand. X-bit Register operand class
	'''
	def __init__(self, reg, va=0, oflags=0, size=0):
		if reg == None:
			raise Exception("ArmRegOper: None Reg Type!")
			raise envi.InvalidInstruction(mesg="None Reg Type!",
					bytez='f00!', va=va)
		self.va = va
		self.reg = reg
		self.oflags = oflags

class A64ImmOper(A64Operand):
	'''
	Subclass of A64Operand. Immediate operand class
	'''
	def __init__(self, val=0, shval=0, shtype=S_ROR, va=0, size=4):
		self.val = val
		self.shval = shval
		self.shtype = shtype
		self.size = size

class A64PreFetchOper(A64Operand):
	'''
	Subclass of A64Operand. prfop operand class (pre-fetch operation)
	'''
	def __init__(self, prfoptype, target, policy):
		self.type = prfoptype
		self.target = target
		self.policy = policy

class A64ShiftOper(A64Operand):
	'''
	Subclass of A64Operand. Shift applied to an operand/register
	'''
	def __init__(self, register, shtype, shval):
		self.register = register
		self.shtype = shtype
		self.shval = shval

class A64ExtendOper(A64Operand):
	'''
	Subclass of A64Operand. Extension applied to an operand/register
	'''
	def __init__(self, register, exttype, shval=0):
		self.register = register
		self.exttype = exttype
		if exttype == 'LSL':
			self.shval = shval
		else:
			self.shval = 0
		 
class A64Opcode(envi.Opcode):
	_def_arch = envi.ARCH_ARMV8

	def __init__(self, va, opcode, mnem, prefixes, size, operands, iflags=0, simdflags=0):
		"""
		constructor for the basic Envi Opcode object.  Arguments as follows:
		opcode   - An architecture specific numerical value for the opcode
		mnem	 - A humon readable mnemonic for the opcode
		prefixes - a bitmask of architecture specific instruction prefixes
		size	 - The size of the opcode in bytes
		operands - A list of Operand objects for this opcode
		iflags   - A list of Envi (architecture independant) instruction flags (see IF_FOO)
		va	   - The virtual address the instruction lives at (used for PC relative immediates etc...)
		NOTE: If you want to create an architecture spcific opcode, I'd *highly* recommend you
			  just copy/paste in the following simple initial code rather than calling the parent
			  constructor.  The extra
		"""
		self.opcode = opcode
		self.mnem = mnem
		self.prefixes = prefixes
		self.size = size
		self.opers = operands
		self.repr = None
		self.iflags = iflags
		self.simdflags = simdflags
		self.va = va
	

class AArch64Disasm:
	#weird thing in envi/__init__. Figure out later
	_optype = envi.ARCH_ARMV8
	_opclass = A64Opcode
	fmt = None
	#This holds the current running Arm instruction version and mask
	#ARCH_REVS is a file containing all masks for various versions of ARM. In const.py
	_archVersionMask = ARCH_REVS['ARMv8A']

	def __init__(self, endian=ENDIAN_LSB, mask = 'ARMv8A'):
		self.setArchMask(mask)
		self.setEndian(endian)


	def setArchMask(self, key = 'ARMv8R'):
		''' set arch version mask '''
		self._archVersionMask = ARCH_REVS.get(key,0)

	def getArchMask(self):
		return self._archVersionMask

	def setEndian(self, endian):
		self.endian = endian
		self.fmt = ("<I", ">I")[endian]

	def getEndian(self):
		return self.endian

	def disasm(self, bytez, offset, va):
		'''
		Parse a series of bytes into an envi.Opcode instance
		''' 
		opbytes = bytez[offset:offset+4]
		opval = struct.unpack(self.fmt, opbytes)

		cond = opval >> 29 & 0x7

		opcode, mnem, olist, flags, smdflags = self.doDecode(va, opval, bytez, offset)

		if mnem == None or type(mnem) == int:
			raise Exception("mnem == %r!  0x%x" % (mnem, opval))

		#FIXME insert some stuff in here. Check out ArmV7 for better idea. Flag modification


		op = A64Opcode(va, opcode, mnem, cond, 4, olist, flags, simdflags)
		return op

	def doDecode(self, va, opval, bytez, offset):
		encfam = (opval >> 25) & 0xf

		'''
		Using encfam,find encoding. If we can't find an encoding (enc == None),
		then throw an exception.
		'''
		enc,nexttab = inittable[encfam]
		if nexttab != None: # we have to sub-parse...
			for mask,val,penc in nexttab:
				#print "penc", penc
				if (opval & mask) == val:
					enc = penc
					break

		# If we don't know the encoding by here, we never will ;)
		if enc == None:
			raise envi.InvalidInstruction(mesg="No encoding found!",
					bytez=bytez[offset:offset+4], va=va)

		'''
		ienc_parsers is a dictionary of encoding names mapped to corresponding functions
		i.e. ienc_parsers[IENC_UNCOND] = p_uncond
		therefore calling ienc_parsers[enc](opval, va+8) calls the corresponding function with parameters
		opval and va+8
		'''
		opcode, mnem, olist, flags, simdflags = ienc_parsers[enc](opval, va+8)
		return opcode, mnem, olist, flags, simdflags


		


		


if __name__=="__main__":
	import envi.archs
	envi.archs.dismain( AArch64Disasm() )
	
