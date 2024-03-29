import envi.bits as e_bits
import envi.registers as e_reg

from envi.archs.arm.const import *

'''
Strategy:
    * Use only distinct register for Register Context (unique in each bank)
    * Store a lookup table for the different banks of registers, based on the
        register data in proc_modes (see const.py)
    * Emulator does translation from register/mode to actual storage container
        using reg_table and some math (see _getRegIdx)
'''
arm_regs_tups = [
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
    ('sp', 32),  # also r13
    ('lr', 32),  # also r14
    ('pc', 32),  # also r15
    ('cpsr', 32),
    ('nil', 32),    # place holder
    ('spsr', 32),   # updated for each level
    # FIXME: need to deal with ELR_hyp
]

# force them into a tuple for faster run-time access
arm_regs_tups = tuple(arm_regs_tups)
arm_regs = [r for r,sz in arm_regs_tups]

arm_metas = [
        ("r13", REG_SP, 0, 32),
        ("r14", REG_LR, 0, 32),
        ("r15", REG_PC, 0, 32),
]

REG_PC =   15
REG_CPSR = 16
REG_NIL =  17
REG_SPSR = 18

REG_APSR_MASK = 0xffff0000

# build a translation table to allow for fast access of banked registers
modes = list(proc_modes.keys())
modes.sort()

# ARMv7/A32/T32 registers as complicated.  each processor mode accesses a particular set of 
# registers.  some regs are shared with other modes, and some are unique to a particular mode.
# to achieve this using high-performance disassembly and emulation, and the power of the Viv
# RegisterContext model, we've had to get creative.  

# the solution we've chosen is to use a big lookup table and an extra layer to access the actual
# emulated register data.  the larger list of registers (below, reg_table_data) defines a large 
# list of registers, grouped into an equal size list of register definitions per processor mode.
# the smaller list (reg_data) defines a collapsed list of registers, including only the register 
# definitions which have unique data storage.
# we use another large list (reg_table) for mapping indexes into 
# reg_table_data to indexes into reg_data

# so, thats:
# reg_table is the redirection table between MATH-COUNT-Index and Real Register Index: #index
# reg_data is that compressed "only what's needed" table of register entries:  ('name', size)
# reg_table_data is the expanded reg_data completing the all modes, etc:       ('name', size')

# other details:
# emulator get/setRegister() access the emulator data as per *reg_data*
# disassembly creates *RegOper*s using indexes into *reg_table_data*
# the ArmRegisterContext class override get/setRegister() to handle translation
# as far as the rest of the ArmRegisterContext is concern, there is only reg_data
# *RegOper* operands only care about the *reg_tables_data* since they only care about render/repr
#    and the getOperValue() defers to the ArmRegisterContext() for actually accessing the emu data

# this setup allows us to have ranges of "registers" to match the different processor modes
# where some of those registers are unique to a given mode, and others are shared (banked regs)

# all modes' CPSR's point to the one and only CPSR
# all modes` SPSR's are their own thing, and should get a copy of the current CPSR's data on 
#       mode-change.        # NOTE: THIS IS IMPORTANT FOR FULL EMULATION


# start off creating the data for the first mode (USR mode)
# and then pre-populating the reg_table and reg_table_data
reg_data = [ (reg, sz) for reg,sz in arm_regs_tups ]
reg_table = [ x for x in range(MODE_COUNT * REGS_PER_MODE) ]
reg_table_data = [ (None, 32) for x in range(MODE_COUNT * REGS_PER_MODE) ]

for idx,data in enumerate(reg_data):
    reg_table_data[idx] = data

# banked registers for different processor modes
for modenum in modes[1:]:       # skip first since we're already done
    (mname, msname, desc, offset, mode_reg_count, PSR_offset, priv_level) = proc_modes.get(modenum)
    #print("Building %s (%x): offset=0x%x   PSR_offset: 0x%x" % (msname, modenum, offset, PSR_offset))
    #import envi.interactive as ei; ei.dbg_interact(locals(), globals())
    # shared regs
    for ridx in range(mode_reg_count):
        # don't create new entries for this register, use the usr-mode reg
        reg_table[ridx+offset] = ridx

        rnm, rsz = arm_regs_tups[ridx]
        reg_table_data[ridx+offset] = ('%s_%s' % (rnm, msname), rsz) 

    # mode-regs (not including PC)
    for ridx in range(mode_reg_count, 15):
        idx = len(reg_data)
        rnm, rsz = arm_regs_tups[ridx]
        regname = rnm+"_"+msname
        reg_data.append((regname, 32))
        reg_table[ridx+offset] = idx

        reg_table_data[ridx+offset] = (regname, rsz) 

    # PC    - always the original PC
    reg_table[PSR_offset-3] = REG_PC
    reg_table_data[PSR_offset-3] = ('pc_%s' % (msname), 32)
    # CPSR  - always the original CPSR
    reg_table[PSR_offset-2] = REG_CPSR   # SPSR....??
    reg_table_data[PSR_offset-2] = ('CPSR_%s' % (msname), 32) 
    # NIL
    reg_table[PSR_offset-1] = REG_NIL
    reg_table_data[PSR_offset-1] = ('NIL_%s' % (msname), 32) 
    # PSR
    reg_table[PSR_offset] = len(reg_data)                   # -2 because we want SPSR_foo to point at the CPSR_foo.  i think?
    reg_table_data[PSR_offset] = ('SPSR_%s' % (msname), 32)
    reg_data.append(("SPSR_"+msname, 32))

# done with banked register translation table

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

REGS_VECTOR_TABLE_IDX = len(reg_table)
REGS_VECTOR_DATA_IDX = len(reg_data)
REGS_VECTOR_DELTA = REGS_VECTOR_TABLE_IDX - REGS_VECTOR_DATA_IDX

for simdreg in range(VFP_QWORD_REG_COUNT):
    simd_idx = REGS_VECTOR_TABLE_IDX + simdreg
    d = simdreg * 2
    s = d * 2
    reg_table.append(len(reg_data))
    reg_data.append(("q%d" % simdreg, 128))
    reg_table_data.append(("q%d" % simdreg, 128))
    if simdreg < 8: # VFPv4 only allows S# indexing up to S31
        arm_metas.append(("s%d" % (s),   simd_idx, 0, 32))
        arm_metas.append(("s%d" % (s+1), simd_idx, 32, 32))
        arm_metas.append(("s%d" % (s+2), simd_idx, 64, 32))
        arm_metas.append(("s%d" % (s+3), simd_idx, 96, 32))
    arm_metas.append(("d%d" % (d),   simd_idx, 0, 64))
    arm_metas.append(("d%d" % (d+1), simd_idx, 32, 64))

REG_FPSCR = len(reg_table)
reg_table.append(len(reg_data))
reg_data.append(('fpscr', 32))
reg_table_data.append(('fpscr', 32))

reg_table.append(len(reg_data))
reg_data.append(('IPSR', 32))
reg_table_data.append(('IPSR', 32))
reg_table.append(len(reg_data))
reg_data.append(('EPSR', 32))
reg_table_data.append(('EPSR', 32))
reg_table.append(len(reg_data))
reg_data.append(('PRIMASK', 32))
reg_table_data.append(('PRIMASK', 32))
reg_table.append(len(reg_data))
reg_data.append(('FAULTMASK', 32))
reg_table_data.append(('FAULTMASK', 32))
reg_table.append(len(reg_data))
reg_data.append(('BASEPRI', 32))
reg_table_data.append(('BASEPRI', 32))
reg_table.append(len(reg_data))
reg_data.append(('BASEPRI_MAX', 32))
reg_table_data.append(('BASEPRI_MAX', 32))
reg_table.append(len(reg_data))
reg_data.append(('CONTROL', 32))
reg_table_data.append(('CONTROL', 32))
reg_table.append(len(reg_data))
reg_data.append(('MSP', 32))
reg_table_data.append(('MSP', 32))
reg_table.append(len(reg_data))
reg_data.append(('PSP', 32))
reg_table_data.append(('PSP', 32))

MAX_TABLE_SIZE = len(reg_table_data)

l = locals()
e_reg.addLocalEnums(l, reg_table_data)

PSR_N = 31  # negative
PSR_Z = 30  # zero
PSR_C = 29  # carry
PSR_V = 28  # oVerflow
PSR_Q = 27
PSR_IT_BASE = 25
PSR_IT_SIZE = 10
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
psr_fields[PSR_IT_BASE] = "IT_BASE"
psr_fields[PSR_IT_BASE+1] = "IT_BASE+1"
psr_fields[PSR_IT_BASE+2] = "IT_BASE+2"
psr_fields[PSR_IT_SIZE] = "IT_SIZE"  # IT is split into two sections
psr_fields[PSR_IT_SIZE+1] = "IT_SIZE+1"  # IT is split into two sections
psr_fields[PSR_IT_SIZE+2] = "IT_SIZE+2"  # IT is split into two sections
psr_fields[PSR_IT_SIZE+3] = "IT_SIZE+3"  # IT is split into two sections
psr_fields[PSR_IT_SIZE+4] = "IT_SIZE+4"  # IT is split into two sections
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
        ("IT_BASE0",REG_FLAGS, PSR_IT_BASE, 1, "IfThen 0 bit"),
        ("IT_BASE1",REG_FLAGS, PSR_IT_BASE+1, 1, "IfThen 1 bit"),
        ("IT_BASE2",REG_FLAGS, PSR_IT_BASE+2, 1, "IfThen 2 bit"),
        ("IT_SIZE0",REG_FLAGS, PSR_IT_SIZE, 1, "IfThen 0 bit"),
        ("IT_SIZE1",REG_FLAGS, PSR_IT_SIZE+1, 1, "IfThen 1 bit"),
        ("IT_SIZE2",REG_FLAGS, PSR_IT_SIZE+2, 1, "IfThen 2 bit"),
        ("IT_SIZE3",REG_FLAGS, PSR_IT_SIZE+3, 1, "IfThen 3 bit"),
        ("IT_SIZE4",REG_FLAGS, PSR_IT_SIZE+4, 1, "IfThen 4 bit"),
        ('IT_SIZE',REG_FLAGS, PSR_IT_SIZE, 5, "IfThen Block Size"),
        ('IT_BASE',REG_FLAGS, PSR_IT_BASE, 3, "IfThen Base Condition"),
        ("E", REG_FLAGS, PSR_E, 1, "Data Endian bit"),
        ("A", REG_FLAGS, PSR_A, 1, "Imprecise Abort Disable bit"),
        ("I", REG_FLAGS, PSR_I, 1, "IRQ disable bit"),
        ("F", REG_FLAGS, PSR_F, 1, "FIQ disable bit"),
        ("T", REG_FLAGS, PSR_T, 1, "Thumb Mode bit"),
        ("M", REG_FLAGS, PSR_M, 5, "Processor Mode"),
        ]

e_reg.addLocalStatusMetas(l, arm_metas, arm_status_metas, "CPSR")
e_reg.addLocalMetas(l, arm_metas)

def getRegDataIdx(idx):
    ridx = reg_table[idx]  # magic pointers allowing overlapping banks of registers
    return ridx

class ArmRegisterContext(e_reg.RegisterContext):
    def __init__(self):
        e_reg.RegisterContext.__init__(self)
        self.loadRegDef(reg_table_data)
        self.loadRegMetas(arm_metas, statmetas=arm_status_metas)
        self.setRegisterIndexes(REG_PC, REG_SP)

    def getProcMode(self):
        '''
        get current ARM processor mode.  see proc_modes (const.py)
        '''
        return self._rctx_vals[REG_CPSR] & 0x1f

    def setProcMode(self, mode):
        '''
        set the current processor mode.  stored in CPSR
        '''
        # write current psr to the saved psr register for target mode
        # but not for USR or SYS modes, which don't have their own SPSR
        if mode not in (PM_usr, PM_sys):
            curSPSRidx = proc_modes[mode]
            self._rctx_vals[curSPSRidx] = self.getCPSR()

        # set current processor mode
        cpsr = self._rctx_vals[REG_CPSR] & 0xffffffe0
        self._rctx_vals[REG_CPSR] = cpsr | mode

    def getRegister(self, index, mode=None):
        """
        Return the current value of the specified register index.
        """
        if mode is None:
            mode = self.getProcMode() & 0xf
        else:
            mode &= 0xf

        idx = (index & 0xffff)
        ridx = _getRegIdx(idx, mode)

        if (index & 0xffff) == index:   # not a metaregister
            return self._rctx_vals[ridx]

        offset = (index >> 24) & 0xff
        width  = (index >> 16) & 0xff

        mask = (2**width)-1
        return (self._rctx_vals[ridx] >> offset) & mask

    def setRegister(self, index, value, mode=None):
        """
        Set a register value by index.
        """
        if mode is None:
            mode = self.getProcMode() & 0xf
        else:
            mode &= 0xf

        self._rctx_dirty = True

        # the raw index (in case index is a metaregister)
        idx = (index & 0xffff)

        # have to translate every register index to find the right home
        ridx = _getRegIdx(idx, mode)

        if (index & 0xffff) == index:   # not a metaregister
            self._rctx_vals[ridx] = (value & self._rctx_masks[ridx])      # FIXME: hack.  should look up index in proc_modes dict?
            return

        # If we get here, it's a meta register index.
        # NOTE: offset/width are in bits...
        offset = (index >> 24) & 0xff
        width  = (index >> 16) & 0xff

        mask = e_bits.b_masks[width]
        mask = mask << offset

        # NOTE: basewidth is in *bits*
        basewidth = self._rctx_widths[ridx]
        basemask  = (2**basewidth)-1

        # cut a whole in basemask at the size/offset of mask
        finalmask = basemask ^ mask

        curval = self._rctx_vals[ridx]

        self._rctx_vals[ridx] = (curval & finalmask) | (value << offset)


def _getRegIdx(idx, mode):
    if idx >= REGS_VECTOR_TABLE_IDX:
        return reg_table[idx]

    mode &= 0xf
    ridx = idx + (mode*REGS_PER_MODE)  # account for different banks of registers
    ridx = reg_table[ridx]  # magic pointers allowing overlapping banks of registers
    return ridx


def reg_mode_base(mode):
    '''
    Get the base register index for a given mode (full-sized table)
    '''
    mdata = proc_modes.get(mode)
    if mdata is None:
        raise Exception("Invalid Mode access (reg_mode_base): %d" % mode)

    return mdata[3]



rctx = ArmRegisterContext()
