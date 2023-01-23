import envi.registers as e_reg

registers = [
    # constant zero
    '$zero',
    # $at is reserved for the assembler
    '$at',
    # result registers
    '$v0', '$v1',
    # argument registers
    '$a0', '$a1', '$a3', '$a4',
    # temporary registers
    '$t0', '$t1', '$t2', '$t3', '$t4', '$t5', '$t6', '$t7',
    # saved registers
    '$s0', '$s1', '$s2', '$s3', '$s4', '$s5', '$s6', '$s7',
    # more temporary registers
    '$t8', '$t9',
    # 26 and 27 reserved as well
    '$k0', '$k1',
    # general data pointer, stack pointer, frame pointer, return address
    '$gp', '$sp', '$fp', '$ra',
    # output of mult/div
    '$hi', '$lo',
    # program counter - not directly accessible
    '$pc'
]

# all registers are 32 bits, TODO does this change if we extend this later to support MIPS III-V?
registers_info = [ (reg, 32) for reg in registers ]

l = locals()
e_reg.addLocalEnums(l, registers_info)

# TODO are there other names for the registers above?
# TODO are there partial registers?
# TODO define flags

class MipsRegisterContext(e_reg.RegisterContext):
    def __init__(self):
        e_reg.RegisterContext.__init__(self)
        self.loadRegDef(registers_info)
        self.setRegisterIndexes(REG_PC, REG_SP)
