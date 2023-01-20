import envi
import envi.archs.ppc as e_ppc
import envi.archs.ppc.const as eapc
import envi.archs.ppc.disasm_classes as eapdc
import vivisect.impemu.emulator as v_i_emulator


import logging
logger = logging.getLogger(__name__)


# MAS0 - MAS3 masks and shifts
MAS0_ESEL_MASK     = 0x001F0000
MAS0_ESEL_SHIFT    = 16

MAS1_TSIZ_MASK     = 0x00000F80
MAS1_TSIZ_SHIFT    = 7

MASx_EPN_MASK      = 0xFFFFFC00
MAS2_VLE_MASK      = 0x00000020


# MMU TSIZ field to memory map size mappings
MAS1_TSIZE_MAP = (
    0x00000400, # 1KB
    0x00000800, # 2KB
    0x00001000, # 4KB
    0x00002000, # 8KB
    0x00004000, # 16KB
    0x00008000, # 32KB
    0x00010000, # 64KB
    0x00020000, # 128KB
    0x00040000, # 256KB
    0x00080000, # 512KB
    0x00100000, # 1MB
    0x00200000, # 2MB
    0x00400000, # 4MB
    0x00800000, # 8MB
    0x01000000, # 16MB
    0x02000000, # 32MB
    0x04000000, # 64MB
    0x08000000, # 128MB
    0x10000000, # 256MB
    0x20000000, # 512MB
    0x40000000, # 1GB
    0x80000000, # 2GB
    0x100000000, # 4GB
)


class PpcWorkspaceEmulator(v_i_emulator.WorkspaceEmulator):

    # Taint the argument parameters
    taintregs = [
            e_ppc.REG_R3, e_ppc.REG_R4, e_ppc.REG_R5, e_ppc.REG_R6,
            e_ppc.REG_R7, e_ppc.REG_R8, e_ppc.REG_R9, e_ppc.REG_R10,
    ]

    def __init__(self, vw, **kwargs):
        '''
        Please see the base emulator class in vivisect/impemu/emulator.py for the parameters
        that can be passed through kwargs
        '''
        v_i_emulator.WorkspaceEmulator.__init__(self, vw, **kwargs)

        # If there is a PpcVlePages Meta defined, update the emulator now.
        # This has to be checked here because the workspace emulators are
        # created after the metadata events are parsed
        maps = vw.getMeta('PpcVlePages')
        if maps is not None:
            self.setVleMaps(maps)

        # Track if we should automatically find VLE pages or not
        self.findvlepages = vw.config.viv.arch.ppc.findvlepages

    def getRegister(self, index):
        """
        Return the current value of the specified register index. Modified to
        support taint tracking during function analysis.
        """
        value = super().getRegister(index)

        # If there is no saved instruction, or the register is not one of the
        # taint registers, just return the value.
        if self.op is None or index not in self.taintregs:
            return value

        # TODO: We need src/dest flags for operands to make this easier
        if self.isRegUse(self.op, index):
            self._useVirtAddr(value)
        return value

    def isRegUse(self, op, ridx):
        '''
        If the register is the second operand then assume this is a register
        "use" and we need to check if the value is tainted. Except for store
        instructions.
        '''
        if op.opcode in eapc.STORE_INSTRS:
            # For STORE instructions on the first operand is a possible source
            # the base register is caught by the normal writeMemory() hook
            return op.opers[0].reg == ridx
        elif op.opcode not in eapc.LOAD_INSTRS:
            # LOAD instructions are caught by the normal readMemory() hooks
            try:
                reg_use = next(o for o in op.opers[1:] if \
                        isinstance(o, eapdc.PpcRegOper) and o.reg == ridx)
                return True
            except StopIteration:
                pass

        return False

    def i_tlbwe(self, op):
        '''
        Custom handling of the tlbwe instruction to update the workspace
        PpcVlePages meta variable to allow detection of VLE pages
        '''
        # Replace or add an MMU entry if the PpcVlePages meta variable is
        # defined and the findvlepages configuration option is enabled
        if self.findvlepages:
            vle_pages = self.vw.getMeta('PpcVlePages')

            mas0 = self.getRegister(e_ppc.REG_MAS0)
            mas1 = self.getRegister(e_ppc.REG_MAS1)
            mas2 = self.getRegister(e_ppc.REG_MAS2)
            #mas3 = self.getRegister(e_ppc.REG_MAS3)

            idx = (mas0 & MAS0_ESEL_MASK) >> MAS0_ESEL_SHIFT
            tsiz = (mas1 & MAS1_TSIZ_MASK) >> MAS1_TSIZ_SHIFT
            size = MAS1_TSIZE_MAP[tsiz]
            base = mas2 & MASx_EPN_MASK
            vle = bool(mas2 & MAS2_VLE_MASK)

            logger.debug('Writing PPC MMU entry %d: 0x%x - 0x%x (%s)', idx, base, base+size, vle)
            vle_pages[idx] = [base, size, vle]

            self.vw.setMeta('PpcVlePages', vle_pages)


class Ppc64EmbeddedWorkspaceEmulator(PpcWorkspaceEmulator, e_ppc.Ppc64EmbeddedEmulator):
    def __init__(self, vw, **kwargs):
        '''
        Please see the base emulator class in vivisect/impemu/emulator.py for the parameters
        that can be passed through kwargs
        '''
        e_ppc.Ppc64EmbeddedEmulator.__init__(self)
        PpcWorkspaceEmulator.__init__(self, vw, **kwargs)


class Ppc32EmbeddedWorkspaceEmulator(PpcWorkspaceEmulator, e_ppc.Ppc32EmbeddedEmulator):
    def __init__(self, vw, **kwargs):
        '''
        Please see the base emulator class in vivisect/impemu/emulator.py for the parameters
        that can be passed through kwargs
        '''
        e_ppc.Ppc32EmbeddedEmulator.__init__(self)
        PpcWorkspaceEmulator.__init__(self, vw, **kwargs)


class PpcVleWorkspaceEmulator(PpcWorkspaceEmulator, e_ppc.PpcVleEmulator):
    def __init__(self, vw, **kwargs):
        '''
        Please see the base emulator class in vivisect/impemu/emulator.py for the parameters
        that can be passed through kwargs
        '''
        e_ppc.PpcVleEmulator.__init__(self)
        PpcWorkspaceEmulator.__init__(self, vw, **kwargs)


class Ppc64ServerWorkspaceEmulator(PpcWorkspaceEmulator, e_ppc.Ppc64ServerEmulator):
    def __init__(self, vw, **kwargs):
        '''
        Please see the base emulator class in vivisect/impemu/emulator.py for the parameters
        that can be passed through kwargs
        '''
        e_ppc.Ppc64ServerEmulator.__init__(self)
        PpcWorkspaceEmulator.__init__(self, vw, **kwargs)


class Ppc32ServerWorkspaceEmulator(PpcWorkspaceEmulator, e_ppc.Ppc32ServerEmulator):
    def __init__(self, vw, **kwargs):
        '''
        Please see the base emulator class in vivisect/impemu/emulator.py for the parameters
        that can be passed through kwargs
        '''
        e_ppc.Ppc32ServerEmulator.__init__(self)
        PpcWorkspaceEmulator.__init__(self, vw, **kwargs)
