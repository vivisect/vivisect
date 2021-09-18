"""
Similar to the memory subsystem, this is a unified way to
access information about objects which contain registers
"""

import envi.exc as e_exc
from envi.const import *

class RegisterContext:

    def __init__(self, regdef=(), metas=(), pcindex=None, spindex=None, srindex=None):
        """
        Hand in a register definition which consists of
        a list of (<name>, <width>) tuples.
        """
        self.loadRegDef(regdef)
        self.loadRegMetas(metas)
        self.setRegisterIndexes(pcindex, spindex, srindex=srindex)

        self._rctx_dirty = False

    def getRegisterSnap(self):
        """
        Use this to bulk save off the register state.
        """
        return list(self._rctx_vals)

    def setRegisterSnap(self, snap):
        """
        Use this to bulk restore the register state.

        NOTE: This may only be used under the assumption that the
              RegisterContext has been initialized the same way
              (like context switches in tracers, or emulaction snaps)
        """
        self._rctx_vals = list(snap)

    def isDirty(self):
        """
        Returns true if registers in this context have been modififed
        since their import.
        """
        return self._rctx_dirty

    def setIsDirty(self, bool):
        self._rctx_dirty = bool

    def setRegisterIndexes(self, pcindex, spindex, srindex=None):
        self._rctx_pcindex = pcindex
        self._rctx_spindex = spindex
        self._rctx_srindex = srindex

    def loadRegDef(self, regdef, defval=0):
        """
        Load a register definition.  A register definition consists
        of a list of tuples with the following format:
        (regname, regwidth)

        NOTE: All widths in envi RegisterContexts are in bits.
        """
        self._rctx_regdef = regdef # Save this for snaps etc..
        self._rctx_names = {}
        self._rctx_ids = {}
        self._rctx_widths = []
        self._rctx_vals  = []
        self._rctx_masks = []

        for i, (name, width) in enumerate(regdef):
            self._rctx_names[name] = i
            self._rctx_ids[i] = name
            self._rctx_widths.append(width)
            self._rctx_masks.append((2**width)-1)
            self._rctx_vals.append(defval)

    def getRegDef(self):
        return self._rctx_regdef

    def loadRegMetas(self, metas, statmetas=None):
        """
        Load a set of defined "meta" registers for this architecture.  Meta
        registers are defined as registers who exist as a subset of the bits
        in some other "real" register. The argument metas is a list of tuples
        with the following format:
        (regname, regidx, reg_shift_offset, reg_width)
        The given example is for the AX register in the i386 subsystem
        regname: "ax"
        reg_shift_offset: 0
        reg_width: 16

        Optionally a set of status meta registers can be loaded as well.
        The argument is a list of tuples with the following format:
        (regname, regidx, reg_shift_offset, reg_width, description)
        """
        self._rctx_regmetas = metas
        for name, idx, offset, width in metas:
            self.addMetaRegister(name, idx, offset, width)

        self._rctx_statmetas = statmetas

    def addMetaRegister(self, name, idx, offset, width):
        """
        Meta registers are registers which are really just directly
        addressable parts of already existing registers (eax -> al).

        To add a meta register, you give the name, the idx of the *real*
        register, the width of the meta reg, and it's left shifted (in bits)
        offset into the real register value.  The RegisterContext will take
        care of accesses after that.
        """
        newidx = (offset << 24) + (width << 16) + idx
        self._rctx_names[name] = newidx
        self._rctx_ids[newidx] = name

    def isMetaRegister(self, index):
        return (index & 0xffff) != index

    def _rctx_Import(self, sobj):
        """
        Given an object with attributes with the same names as
        registers in our context, populate our values from it.

        NOTE: This also clears the dirty flag
        """
        # On import from a structure, we are clean again.
        self._rctx_dirty = False
        for name,idx in self._rctx_names.items():
            # Skip meta registers
            if (idx & 0xffff) != idx:
                continue
            x = getattr(sobj, name, None)
            if x is not None:
                self._rctx_vals[idx] = x

    def _rctx_Export(self, sobj):
        """
        Given an object with attributes with the same names as
        registers in our context, set the ones he has to match
        our values.
        """
        for name,idx in self._rctx_names.items():
            # Skip meta registers
            if (idx & 0xffff) != idx:
                continue
            if hasattr(sobj, name):
                setattr(sobj, name, self._rctx_vals[idx])

    def getRegisterInfo(self, meta=False):
        """
        Return an object which can be stored off, and restored
        to re-initialize a register context.  (much like snapshot
        but it takes the definitions with it)
        """
        regdef = self._rctx_regdef
        regmeta = self._rctx_regmetas
        pcindex = self._rctx_pcindex
        spindex = self._rctx_spindex
        snap = self.getRegisterSnap()

        return (regdef, regmeta, pcindex, spindex, snap)

    def setRegisterInfo(self, info):
        regdef, regmeta, pcindex, spindex, snap = info
        self.loadRegDef(regdef)
        self.loadRegMetas(regmeta)
        self.setRegisterIndexes(pcindex, spindex)
        self.setRegisterSnap(snap)

    def getRegisterName(self, index):
        return self._rctx_ids.get(index,"REG%.8x" % index)

    def getProgramCounter(self):
        """
        Get the value of the program counter for this register context.
        """
        return self.getRegister(self._rctx_pcindex)

    def setProgramCounter(self, value):
        """
        Set the value of the program counter for this register context.
        """
        self.setRegister(self._rctx_pcindex, value)

    def getStackCounter(self):
        return self.getRegister(self._rctx_spindex)

    def setStackCounter(self, value):
        self.setRegister(self._rctx_spindex, value)

    def hasStatusRegister(self):
        '''
        Returns True if this context is aware of a status register.
        '''
        if self._rctx_srindex is None:
            return False

        return True

    def getStatusRegNameDesc(self):
        '''
        Return a list of status register names and descriptions.
        '''
        return [(name, desc) for name, idx, offset, width, desc in self._rctx_statmetas]

    def getStatusRegister(self):
        '''
        Gets the status register for this register context.
        '''
        return self.getRegister(self._rctx_srindex)

    def setStatusRegister(self, value):
        '''
        Sets the status register for this register context.
        '''
        self.setRegister(self._rctx_srindex, value)

    def getStatusFlags(self):
        '''
        Return a dictionary of reg name and reg value for the meta registers
        that are part of the status register.
        '''
        ret = {}
        for name, idx, offset, width, desc in self._rctx_statmetas:
            ret[name] = self.getRegisterByName(name)

        return ret

    def getRegisterByName(self, name):
        idx = self._rctx_names.get(name)
        if idx is None:
            raise e_exc.InvalidRegisterName("Unknown Register: %s" % name)
        return self.getRegister(idx)

    def setRegisterByName(self, name, value):
        idx = self._rctx_names.get(name)
        if idx is None:
            raise e_exc.InvalidRegisterName("Unknown Register: %s" % name)
        self.setRegister(idx, value)

    def getRegisterNames(self):
        '''
        Returns a list of the 'real' (non meta) registers.
        '''
        regs = [rname for rname, ridx in self._rctx_names.items()
                if not self.isMetaRegister(ridx)]
        return regs

    def getRegisterNameIndexes(self):
        '''
        Return a list of all the 'real' (non meta) registers and their indexes.

        Example: for regname, regidx in x.getRegisterNameIndexes():
        '''
        regs = [(rname, ridx) for rname, ridx in self._rctx_names.items()
                if not self.isMetaRegister(ridx)]
        return regs

    def getRegisters(self):
        """
        Get all the *real* registers from this context as a dictionary of name
        value pairs.
        """
        ret = {}
        for name,idx in self._rctx_names.items():
            if (idx & 0xffff) != idx:
                continue
            ret[name] = self.getRegister(idx)
        return ret

    def setRegisters(self, regdict):
        """
        For any name value pairs in the specified dictionary, set the current
        register values in this context.
        """
        for name,value in regdict.items():
            self.setRegisterByName(name, value)

    def getRegisterIndex(self, name):
        """
        Get a register index by name.
        (faster to use the index multiple times)
        """
        return self._rctx_names.get(name)

    def getRegisterWidth(self, index):
        """
        Return the width of the register which lives at the specified
        index (width is always in bits).
        """
        ridx = index & 0xffff
        if ridx == index:
            return self._rctx_widths[index]
        width  = (index >> 16) & 0xff
        return width

    def getRegister(self, index):
        """
        Return the current value of the specified register index.
        """
        ridx = index & 0xffff
        value = self._rctx_vals[ridx]
        if ridx != index:
            value = self._xlateToMetaReg(index, value)
        return value

    def getMetaRegInfo(self, index):
        '''
        Return the appropriate realreg, shift, mask info
        for the specified metareg idx (or None if it's not
        meta).

        Example:
            real_reg, lshift, mask = r.getMetaRegInfo(x)
        '''
        ridx = index & 0xffff
        if ridx == index:
            return None

        offset = (index >> 24) & 0xff
        width  = (index >> 16) & 0xff

        mask = (2**width)-1
        return ridx, offset, mask

    def _xlateToMetaReg(self, index, value):
        '''
        Translate a register value to the meta register value
        (used when getting a meta register)
        '''
        ridx = index & 0xffff
        offset = (index >> 24) & 0xff
        width  = (index >> 16) & 0xff

        mask = (2**width)-1

        if offset != 0:
            value >>= offset

        return value & mask

    def _xlateToNativeReg(self, index, value):
        '''
        Translate a register value to the native register value
        (used when setting a meta register)
        '''
        ridx = index & 0xffff
        width = (index >> 16) & 0xff
        offset = (index >> 24) & 0xff

        # FIXME is it faster to generate or look these up?
        mask = (2 ** width) - 1
        mask = mask << offset

        # NOTE: basewidth is in *bits*
        basewidth = self._rctx_widths[ridx]
        basemask = (2 ** basewidth) - 1

        # cut a whole in basemask at the size/offset of mask
        finalmask = basemask ^ mask

        curval = self._rctx_vals[ridx]

        if offset:
            value <<= offset

        return (value & mask) | (curval & finalmask)

    def setRegister(self, index, value):
        """
        Set a register value by index.
        """
        self._rctx_dirty = True

        ridx = index & 0xffff

        # If it's a meta register index, lets mask it into
        # the real thing...
        if ridx != index:
            value = self._xlateToNativeReg(index, value)

        self._rctx_vals[ridx] = (value & self._rctx_masks[ridx])

    def getRealRegisterNameByIdx(self, regidx):
        """
        Returns the Name of the Containing register (in the case
        of meta-registers) or the name of the register.
        (by Index)
        """
        return self.getRegisterName(regidx & RMETA_NMASK)

    def getRealRegisterName(self, regname):
        """
        Returns the Name of the Containing register (in the case
        of meta-registers) or the name of the register.
        """
        ridx = self.getRegisterIndex(regname)
        if ridx is not None:
            return self.getRegisterName(ridx & RMETA_NMASK)
        return regname


def addLocalEnums(l, regdef):
    """
    Update a dictionary (or module locals) with REG_FOO index
    values for all the base registers defined in regdef.
    """
    for i,(rname,width) in enumerate(regdef):
        l["REG_%s" % rname.upper()] = i

def addLocalStatusMetas(l, metas, statmetas, regname):
    '''
    Dynamically create data based on the status register meta register
    definition.
    Adds new meta registers and bitmask constants.
    '''
    for metaname, idx, offset, width, desc in statmetas:
        # create meta registers
        metas.append( (metaname, idx, offset, width) )

        # create local bitmask constants (EFLAGS_%)
        l['%s_%s' % (regname, metaname)] = 1 << offset # TODO: fix for arbitrary width

def addLocalMetas(l, metas):
    """
    Update a dictionary (or module locals) with REG_FOO index
    values for all meta registers defined in metas.
    """
    for name, idx, offset, width in metas:
        l["REG_%s" % name.upper()] = (offset << 24) | (width << 16) | idx
