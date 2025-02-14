import envi.registers as e_reg

from envi.archs.riscv.const import *
from envi.archs.riscv.info import *
from envi.archs.riscv.regs_gen import csr_regs as _csr_regs


general_registers = (
    # x0 always zero
    'zero',

    # x1 return address
    'ra',

    # x2 stack pointer
    'sp',

    # x3 global pointer
    'gp',

    # x4 thread pointer
    'tp',

    # x5 temporary / alternate return address
    't0',

    # x6 - x7 temporary
    't1', 't2',

    # x8 saved / frame pointer
    's0',

    # x9 saved
    's1',

    # x10 - x11 argument / return value
    'a0', 'a1',

    # x12 - x17 argument
    'a2', 'a3', 'a4', 'a5', 'a6', 'a7',

    # x18 - x27 saved
    's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 's11',

    # x28 - x31 temporary
    't3', 't4', 't5', 't6',
)

internal_registers = (
    'pc',
)

system_registers = tuple(reg.name for reg in _csr_regs.values())

float_registers = (
    # f0 - f7 temporaries
    'ft0', 'ft1', 'ft2', 'ft3', 'ft4', 'ft5', 'ft6', 'ft7',

    # f8 - f9 saved
    'fs0', 'fs1',

    # f10 - f11 arguments / return values
    'fa0', 'fa1',

    # f12 - f17 arguments
    'fa2', 'fa3', 'fa4', 'fa5', 'fa6', 'fa7',

    # f18 - f27 saved
    'fs2', 'fs3', 'fs4', 'fs5', 'fs6', 'fs7', 'fs8', 'fs9', 'fs10', 'fs11',

    # f28 - f31 temporaries
    'ft8', 'ft9', 'ft10', 'fa11',
)

# The real register width will be for each instance of the RiscVRegisterContext
# class, for now we just need to get the REG_* constants defined so we will use
# a size of 32
registers_info = tuple(
    [[reg, 32] for reg in general_registers] +
    [[reg, 32] for reg in internal_registers] +
    [[reg, 32] for reg in system_registers] +
    [[reg, 32] for reg in float_registers]
)

_l = locals()
e_reg.addLocalEnums(_l, registers_info)

# Add meta registers for the standard X0-X31 and F0-F31 register names, the
# width is important to the meta register constant, but we don't yet know the
# register width for a specific machine, so define the width to be the maximum
# allowed for RiscV.
metas = tuple(
    # Maximum integer reg width is XLEN, which is currently 64 for RV64? archs
    [('x%d' % i, _l['REG_%s' % reg.upper()], 0, 64) \
            for i, reg in enumerate(general_registers)] +

    # Maximum float reg width is FLEN, which is currently 128 for RV?Q archs
    [('f%d' % i, _l['REG_%s' % reg.upper()], 0, 128) \
            for i, reg in enumerate(float_registers)]
)
e_reg.addLocalMetas(_l, metas)


class RiscVRegisterContext(e_reg.RegisterContext):
    def __init__(self, description=None):
        e_reg.RegisterContext.__init__(self)

        if description is None:
            description = DEFAULT_RISCV_DESCR

        self.xlen = getRiscVXLEN(description)
        self.flen = getRiscVFLEN(description)

        # Populate the info with the correct info now
        # The system register sizes can vary but for now use XLEN
        if self.flen is not None:
            info = [(reg, self.xlen) for reg in general_registers] + \
                    [(reg, self.xlen) for reg in internal_registers] + \
                    [(reg, self.xlen) for reg in system_registers] + \
                    [(reg, self.flen) for reg in float_registers]
        else:
            info = [(reg, self.xlen) for reg in general_registers] + \
                    [(reg, self.xlen) for reg in internal_registers] + \
                    [(reg, self.xlen) for reg in system_registers]
        self.loadRegDef(info)

        # But don't change the metas
        self.loadRegMetas(metas, statmetas=[])

        self.setRegisterIndexes(REG_PC, REG_SP)

    def addRegister(self, name, width=None, defval=0):
        """
        Support adding new system registers dynamically.
        This is necessary to allow non-standard CSR registers to get added on
        the fly if disassembly indicates something non-standard.
        """
        if width is None:
            width = self.xlen

        new_id = len(self._rctx_ids)
        self._rctx_regdef.append((name, width))
        self._rctx_names[name] = new_id
        self._rctx_ids.append(name)
        self._rctx_widths.append(width)
        self._rctx_masks.append((2**width)-1)
        self._rctx_vals.append(defval)


# Create a default RiscV register context
riscv_regs = RiscVRegisterContext()
