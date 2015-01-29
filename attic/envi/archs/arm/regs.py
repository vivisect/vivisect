from envi.archs.arm.const import *
import envi.registers as e_reg

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
    ('sp', 32),
    ('lr', 32),
    ('pc', 32),
    ('cpsr', 32),
    # FIXME shadow regs go here (but are not encoded in
    # instructions... they are used by context only)
)

# build a translation table to allow for fast access of banked registers
modes = proc_modes.keys()
modes.sort()

reg_table = [ x for x in range(16 * 17) ]
reg_data = [ (reg, sz) for reg,sz in arm_regs ]

for modenum in modes[1:]:       # skip first since we're already done
    (mname, msname, desc, offset, mode_reg_count, PSR_offset) = proc_modes.get(modenum)
    # shared regs
    for ridx in range(mode_reg_count):
        # don't create new entries for this
        reg_table[ridx+offset] = ridx

    # mode-regs (including PC)
    for ridx in range(mode_reg_count, 16):
        idx = len(reg_data)
        reg_data.append((msname+"_"+arm_regs[ridx][0], 32))
        reg_table[ridx+offset] = idx

    # PSR
    reg_table[PSR_offset] = len(reg_data)
    reg_data.append((msname+"_SPSR", 32))
# done with banked register translation table

l = locals()
e_reg.addLocalEnums(l, arm_regs)

PSR_N = 31  # negative
PSR_Z = 30  # zero
PSR_C = 29  # carry
PSR_V = 28  # oVerflow
PSR_Q = 27
PSR_J = 24
PSR_GE = 16
PSR_E = 9
PSR_A = 8
PSR_I = 7
PSR_F = 6
PSR_T = 5
PSR_M = 0

PSR_C_bit  = 1 << PSR_C
PSR_C_mask = 0xffffffff ^ PSR_C_bit

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
psr_fields[PSR_J] = "J"
psr_fields[PSR_Q] = "Q"
psr_fields[PSR_V] = "V"
psr_fields[PSR_C] = "C"
psr_fields[PSR_Z] = "Z"
psr_fields[PSR_N] = "N"

# FIXME this is....  hmm....
ArmMeta =tuple([("N", REG_FLAGS, PSR_N, 1),
                ("Z", REG_FLAGS, PSR_Z, 1),
                ("C", REG_FLAGS, PSR_C, 1),
                ("V", REG_FLAGS, PSR_V, 1),
                ("Q", REG_FLAGS, PSR_Q, 1),
                ("J", REG_FLAGS, PSR_J, 1),
                ("GE",REG_FLAGS, PSR_GE, 4),
                ("E", REG_FLAGS, PSR_E, 1),
                ("A", REG_FLAGS, PSR_A, 1),
                ("I", REG_FLAGS, PSR_I, 1),
                ("F", REG_FLAGS, PSR_F, 1),
                ("T", REG_FLAGS, PSR_T, 1),
                ("M", REG_FLAGS, PSR_M, 5),
                ])


class ArmRegisterContext(e_reg.RegisterContext):
    def __init__(self):
        e_reg.RegisterContext.__init__(self)
        self.loadRegDef(reg_data)
        #self.loadRegDef(arm_regs)
        #self.loadRegMetas(ArmMeta)
        self.setRegisterIndexes(REG_PC, REG_SP)

