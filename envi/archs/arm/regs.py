from envi.archs.arm.const import *
import envi.registers as e_reg

'''
Strategy:
    * Use only distinct register for Register Context (unique in each bank)
    * Store a lookup table for the different banks of registers, based on the 
        register data in proc_modes (see const.py)
    * Emulator does translation from register/mode to actual storage container
        using reg_table and some math (see _getRegIdx)
'''
arm_regs = (
    ('r0', 32),
    ('r1', 32),
    ('r2', 32),
    ('r3', 32),
    ('r4', 32),
    ('r5', 32),
    ('r6', 32),
    ('r7', 32),
    ('r8', 32),
    ('r9', 32),
    ('r10', 32),
    ('r11', 32),
    ('r12', 32),
    ('sp', 32), # also r13
    ('lr', 32), # also r14
    ('pc', 32), # also r15
    ('cpsr', 32),
    ('nil', 32),   # place holder
    # FIXME: need to deal with ELR_hyp
)
MAX_REGS = 17

# build a translation table to allow for fast access of banked registers
modes = proc_modes.keys()
modes.sort()

reg_table = [ x for x in range(16 * 18) ]
reg_data = [ (reg, sz) for reg,sz in arm_regs ]

for modenum in modes[1:]:       # skip first since we're already done
    (mname, msname, desc, offset, mode_reg_count, PSR_offset, priv_level) = proc_modes.get(modenum)
    # shared regs
    for ridx in range(mode_reg_count):
        # don't create new entries for this register, use the usr-mode reg
        reg_table[ridx+offset] = ridx

    # mode-regs (including PC)
    for ridx in range(mode_reg_count, 15):
        idx = len(reg_data)
        reg_data.append((arm_regs[ridx][0]+"_"+msname, 32))
        reg_table[ridx+offset] = idx

    # PC
    reg_table[PSR_offset-2] = 15
    # CPSR
    reg_table[PSR_offset-1] = 16
    # PSR
    reg_table[PSR_offset] = len(reg_data)
    reg_data.append(("SPSR_"+msname, 32))

# done with banked register translation table

l = locals()
e_reg.addLocalEnums(l, arm_regs)

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

psr_fields = [None for x in xrange(32)]
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

arm_status_metas = [
        ("N", REG_FLAGS, PSR_N, 1, "Negative/LessThan flag"),
        ("Z", REG_FLAGS, PSR_Z, 1, "Zero flag"),
        ("C", REG_FLAGS, PSR_C, 1, "Carry/Borrow/Extend flag"),
        ("V", REG_FLAGS, PSR_V, 1, "oVerflow flag"),
        ("Q", REG_FLAGS, PSR_Q, 1, "Sticky Overflow flag"),
        ("J", REG_FLAGS, PSR_J, 1, "Jazelle Mode bit"),
        ("GE",REG_FLAGS, PSR_GE, 4, "Greater/Equal flag"),
        ("DNM",REG_FLAGS, PSR_DNM, 4, "DO NOT MODIFY bits"),
        ("IT0",REG_FLAGS, PSR_IT, 1, "IfThen 0 bit"),
        ("IT1",REG_FLAGS, PSR_IT+1, 1, "IfThen 1 bit"),
        ("IT2",REG_FLAGS, PSR_IT+2, 1, "IfThen 2 bit"),
        ("IT3",REG_FLAGS, PSR_IT+3, 1, "IfThen 3 bit"),
        ("IT4",REG_FLAGS, PSR_IT+4, 1, "IfThen 4 bit"),
        ("IT5",REG_FLAGS, PSR_IT+5, 1, "IfThen 5 bit"),
        ("IT6",REG_FLAGS, PSR_IT+6, 1, "IfThen 6 bit"),
        ("IT7",REG_FLAGS, PSR_IT+7, 1, "IfThen 7 bit"),
        ("E", REG_FLAGS, PSR_E, 1, "Data Endian bit"),
        ("A", REG_FLAGS, PSR_A, 1, "Imprecise Abort Disable bit"),
        ("I", REG_FLAGS, PSR_I, 1, "IRQ disable bit"),
        ("F", REG_FLAGS, PSR_F, 1, "FIQ disable bit"),
        ("T", REG_FLAGS, PSR_T, 1, "Thumb Mode bit"),
        ("M", REG_FLAGS, PSR_M, 5, "Processor Mode"),
        ]

arm_metas = [
        ("R13", REG_SP, 0, 32),
        ("R14", REG_LR, 0, 32),
        ("R15", REG_PC, 0, 32),
        ]

e_reg.addLocalStatusMetas(l, arm_metas, arm_status_metas, "CPSC")
e_reg.addLocalMetas(l, arm_metas)


class ArmRegisterContext(e_reg.RegisterContext):
    def __init__(self):
        e_reg.RegisterContext.__init__(self)
        self.loadRegDef(reg_data)
        self.loadRegMetas(arm_metas, statmetas=arm_status_metas)
        self.setRegisterIndexes(REG_PC, REG_SP)

