from envi.archs.aarch64.const import *
from envi.archs.aarch64 import sysregs

import envi.registers as e_reg

'''
Strategy:
    * Use only distinct register for Register Context (unique in each bank)
    * Store a lookup table for the different banks of registers, based on the 
        register data in proc_modes (see const.py)
    * Emulator does translation from register/mode to actual storage container
        using reg_table and some math (see _getRegIdx)
'''
META_B_BASE = 0x080000
META_H_BASE = 0x100000
META_W_BASE = 0x200000
META_D_BASE = 0x400000  # only for SIMD registers
META_Q_BASE = 0

meta_reg_bases = (0,
        META_B_BASE,
        META_H_BASE,
        0,
        META_W_BASE,
        0,
        0,
        0,
        META_D_BASE,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        META_Q_BASE,
)

aarch64_regs_tups = [('x%d'%x, 64) for x in range(31)]  # x31 is zero register

REG_SP = len(aarch64_regs_tups)
aarch64_regs_tups.append(('sp', 64))
REG_PC = len(aarch64_regs_tups)
aarch64_regs_tups.append(('pc', 64))
REG_CPSR = len(aarch64_regs_tups)
aarch64_regs_tups.append(('cpsr', 64))
REG_XZR = len(aarch64_regs_tups)
aarch64_regs_tups.append(('xzr', 64))

REG_PSTATE = REG_CPSR

MAX_REGS = len(aarch64_regs_tups) - 1

# metas:   zr is x31.  w* is 32-bit versions of x* regs

reg_data = aarch64_regs_tups
aarch64_regs = [r for r,sz in aarch64_regs_tups]

# Defining general registers 0 - 30
aarch64_metas = [("w%d" % x, x, 0, 32) for x in range(31)]          
aarch64_metas.extend([("h%d" % x, x, 0, 16) for x in range(31)])
aarch64_metas.extend([("b%d" % x, x, 0, 8) for x in range(31)])

# Adding register 31 context (wzr or xzr) separately
aarch64_metas.append(("wzr", REG_XZR, 0, 32))

REG_FPSCR = len(reg_data)
reg_data.append(('fpcr', 32))
reg_data.append(('fpsr', 32))

REGS_SYSTEM_REGS = len(reg_data)

# System Registers - build from sysregs module
sys_regs = [(reg, 64) for reg, _, _, _, _, _, _ in sysregs.system_registers]
reg_data.extend(sys_regs)

# VFP Registers
#    VFPv2 consists of 16 doubleword registers
#    VFPv3 either 32 or 16 doubleword registers
#       VFPv3-D32 - implementation with 32 doubleword regs
#       VFPv3-D16 - implementation with 16 doubleword regs
#    VFPv4 - same as VFPv3
# Advanced SIMD and Floating point views are *not* identical
#
# we implement VFPv4-D32 since it should be backwards-compatible with all others
#  the largest accessor of this extended register bank is 128bits so we'll go with that.

REGS_VECTOR_BASE_IDX = len(reg_data)
for simdreg in range(VFP_QWORD_REG_COUNT):
    simd_idx = REGS_VECTOR_BASE_IDX + simdreg
    d = simdreg #* 2
    s = d #* 2
    reg_data.append(("v%d" % simdreg, 256))
    aarch64_metas.append(("q%d" % (d),   simd_idx, 0, 128))
    aarch64_metas.append(("d%d" % (d),   simd_idx, 0, 64))
    aarch64_metas.append(("s%d" % (s),   simd_idx, 0, 32))
    aarch64_metas.append(("h%d" % (s),   simd_idx, 0, 16))
    aarch64_metas.append(("b%d" % (s),   simd_idx, 0, 8))

l = locals()
e_reg.addLocalEnums(l, aarch64_regs_tups)
REG_LR = REG_X30



PSR_N = 31  # negative
PSR_Z = 30  # zero
PSR_C = 29  # carry
PSR_V = 28  # oVerflow
PSR_Q = 27
PSR_IT = 25
PSR_J = 24
PSR_DNM = 20
PSR_GE = 16
PSR_E = 9
PSR_A = 8
PSR_I = 7
PSR_F = 6
PSR_T = 5
PSR_M = 0

PSR_N_bit  = 1 << PSR_N
PSR_N_mask = 0xffffffff ^ PSR_N_bit
PSR_Z_bit  = 1 << PSR_Z
PSR_Z_mask = 0xffffffff ^ PSR_Z_bit
PSR_C_bit  = 1 << PSR_C
PSR_C_mask = 0xffffffff ^ PSR_C_bit
PSR_V_bit  = 1 << PSR_V
PSR_V_mask = 0xffffffff ^ PSR_V_bit
PSR_T_bit  = 1 << PSR_T
PSR_T_mask = 0xffffffff ^ PSR_T_bit

psr_fields = [None for x in range(32)]
psr_fields[PSR_M] = "M"
psr_fields[PSR_T] = "T"
psr_fields[PSR_F] = "F"
psr_fields[PSR_I] = "I"
psr_fields[PSR_A] = "A"
psr_fields[PSR_E] = "E"
psr_fields[PSR_GE] = "GE"
psr_fields[PSR_GE+1] = "GE+1"
psr_fields[PSR_GE+2] = "GE+2"
psr_fields[PSR_GE+3] = "GE+3"
psr_fields[PSR_DNM] = "DNM"
psr_fields[PSR_DNM+1] = "DNM+1"
psr_fields[PSR_DNM+2] = "DNM+2"
psr_fields[PSR_DNM+3] = "DNM+3"
psr_fields[PSR_J] = "J"
psr_fields[PSR_IT] = "IT"
psr_fields[PSR_IT+1] = "IT+1"
psr_fields[PSR_IT-15] = "IT+2"  # IT is split into two sections
psr_fields[PSR_IT-14] = "IT+3"
psr_fields[PSR_IT-13] = "IT+4"
psr_fields[PSR_IT-12] = "IT+5"
psr_fields[PSR_IT-11] = "IT+6"
psr_fields[PSR_IT-10] = "IT+7"
psr_fields[PSR_Q] = "Q"
psr_fields[PSR_V] = "V"
psr_fields[PSR_C] = "C"
psr_fields[PSR_Z] = "Z"
psr_fields[PSR_N] = "N"

aarch64_status_metas = [
        ("N", REG_PSTATE, PSR_N, 1, "Negative/LessThan flag"),
        ("Z", REG_PSTATE, PSR_Z, 1, "Zero flag"),
        ("C", REG_PSTATE, PSR_C, 1, "Carry/Borrow/Extend flag"),
        ("V", REG_PSTATE, PSR_V, 1, "oVerflow flag"),
        ("Q", REG_PSTATE, PSR_Q, 1, "Sticky Overflow flag"),
        ("J", REG_PSTATE, PSR_J, 1, "Jazelle Mode bit"),
        ("GE",REG_PSTATE, PSR_GE, 4, "Greater/Equal flag"),
        ("DNM",REG_PSTATE, PSR_DNM, 4, "DO NOT MODIFY bits"),
        ("IT0",REG_PSTATE, PSR_IT, 1, "IfThen 0 bit"),
        ("IT1",REG_PSTATE, PSR_IT+1, 1, "IfThen 1 bit"),
        ("IT2",REG_PSTATE, PSR_IT+2, 1, "IfThen 2 bit"),
        ("IT3",REG_PSTATE, PSR_IT+3, 1, "IfThen 3 bit"),
        ("IT4",REG_PSTATE, PSR_IT+4, 1, "IfThen 4 bit"),
        ("IT5",REG_PSTATE, PSR_IT+5, 1, "IfThen 5 bit"),
        ("IT6",REG_PSTATE, PSR_IT+6, 1, "IfThen 6 bit"),
        ("IT7",REG_PSTATE, PSR_IT+7, 1, "IfThen 7 bit"),
        ("E", REG_PSTATE, PSR_E, 1, "Data Endian bit"),
        ("A", REG_PSTATE, PSR_A, 1, "Imprecise Abort Disable bit"),
        ("I", REG_PSTATE, PSR_I, 1, "IRQ disable bit"),
        ("F", REG_PSTATE, PSR_F, 1, "FIQ disable bit"),
        ("T", REG_PSTATE, PSR_T, 1, "Thumb Mode bit"),
        ("M", REG_PSTATE, PSR_M, 5, "Processor Mode"),
        ]

e_reg.addLocalStatusMetas(l, aarch64_metas, aarch64_status_metas, "CPSC")
e_reg.addLocalMetas(l, aarch64_metas)


class A64RegisterContext(e_reg.RegisterContext):
    def __init__(self):
        e_reg.RegisterContext.__init__(self)
        self.loadRegDef(reg_data)
        self.loadRegMetas(aarch64_metas, statmetas=aarch64_status_metas)
        self.setRegisterIndexes(REG_PC, REG_SP)

rctx = A64RegisterContext()

