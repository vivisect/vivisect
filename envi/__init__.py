'''
The Envi framework allows architecture abstraction through the use of the
ArchitectureModule, Opcode, Operand, and Emulator objects.
'''

import types
import struct
import logging
import platform
import contextlib

from envi.exc import *

logger = logging.getLogger(__name__)

# TODO: move into const.py
# Parsed Opcode Formats
ARCH_DEFAULT     = 0 << 16   # arch 0 is whatever the mem object has as default
ARCH_I386        = 1 << 16
ARCH_AMD64       = 2 << 16
ARCH_ARMV7       = 3 << 16
ARCH_THUMB16     = 4 << 16
ARCH_THUMB       = 5 << 16
ARCH_MSP430      = 6 << 16
ARCH_H8          = 7 << 16
ARCH_MASK        = 0xffff0000   # Masked into IF_FOO and BR_FOO values

arch_names = {
    ARCH_DEFAULT:   'default',
    ARCH_I386:      'i386',
    ARCH_AMD64:     'amd64',
    ARCH_ARMV7:     'arm',
    ARCH_THUMB16:   'thumb16',
    ARCH_THUMB:     'thumb',
    ARCH_MSP430:    'msp430',
    ARCH_H8:        'h8',
}

arch_by_name = {
    'default':  ARCH_DEFAULT,
    'i386':     ARCH_I386,
    'amd64':    ARCH_AMD64,
    'arm':      ARCH_ARMV7,
    'armv6l':   ARCH_ARMV7,
    'armv7l':   ARCH_ARMV7,
    'thumb16':  ARCH_THUMB16,
    'thumb':    ARCH_THUMB,
    'thumb2':   ARCH_THUMB,
    'msp430':   ARCH_MSP430,
    'h8':       ARCH_H8,
}

# Instruction flags (The first 8 bits are reserved for arch independant use)
IF_NOFALL = 0x01  # Set if this instruction does *not* fall through
IF_PRIV   = 0x02  # Set if this is a "privileged mode" instruction
IF_CALL   = 0x04  # Set if this instruction branches to a procedure
IF_BRANCH = 0x08  # Set if this instruction branches
IF_RET    = 0x10  # Set if this instruction terminates a procedure
IF_COND   = 0x20  # Set if this instruction is conditional
IF_REPEAT = 0x40  # set if this instruction repeats (including 0 times)

IF_BRANCH_COND = IF_COND | IF_BRANCH

# Branch flags (flags returned by the getBranches() method on an opcode)
BR_PROC  = 1<<0  # The branch target is a procedure (call <foo>)
BR_COND  = 1<<1  # The branch target is conditional (jz <foo>)
BR_DEREF = 1<<2  # the branch target is *dereferenced* into PC (call [0x41414141])
BR_TABLE = 1<<3  # The branch target is the base of a pointer array of jmp/call slots
BR_FALL  = 1<<4  # The branch is a "fall through" to the next instruction
BR_ARCH  = 1<<5  # The branch *switches opcode formats*. ( ARCH_FOO in high bits )

from envi.const import *
import envi.bits as e_bits
import envi.memory as e_mem
import envi.registers as e_reg
import envi.memcanvas as e_canvas

class ArchitectureModule:
    """
    An architecture module implementes methods to deal
    with the creation of envi objects for the specified
    architecture.
    """
    _default_call = None
    _plat_def_calls = {}
    def __init__(self, archname, maxinst=32, endian=ENDIAN_LSB):
        self._arch_id = getArchByName(archname)
        self._arch_name = archname
        self._arch_maxinst = maxinst
        self._arch_badopbytes = [b'\x00\x00\x00\x00\x00', b'\xff\xff\xff\xff\xff']
        self.setEndian(endian)
        self.badops = []

    def getArchId(self):
        '''
        Return the envi ARCH_FOO value for this arch.
        '''
        return self._arch_id

    def getArchName(self):
        '''
        Get the "humon" readable name for the arch implemented
        in this module.
        '''
        return self._arch_name

    def getEndian(self):
        '''
        Every architecture stores numbers either Most-Significant-Byte-first (MSB)
        or Least-Significant-Byte-first (LSB).  Most modern architectures are
        LSB, however many legacy systems still use MSB architectures.
        '''
        return self._endian

    def setEndian(self, endian):
        '''
        Set the architecture endianness.  Subclasses should make sure this is handled
        correctly in any Disasm object(s)
        '''
        self._endian = endian

    def archGetBreakInstr(self):
        """
        Return a python string of the byte sequence which corresponds to
        a breakpoint (if present) for this architecture.
        """
        raise ArchNotImplemented("archGetBreakInstr")

    def archGetNopInstr(self):
        """
        Return a python string of the byte sequence that corresponds to
        a no-op (if present) for this architecture.

        Return None if not present for this architecture.
        """
        raise ArchNotImplemented("archGetNopInstr")

    def archGetRegCtx(self):
        """
        Return an initialized register context object for the architecture.
        """
        raise ArchNotImplemented("archGetRegCtx")

    def archParseOpcode(self, bytez, offset=0, va=0):
        '''
        Parse an architecture specific Opcode object from the given bytes.

        offset  - Offset into bytes to begin opcode parsing
        va      - Virtual address of the instruction ( for rel calcs )

        Example:
            a.archParseOpcode('\xeb\xfe', va=0x41414141)
        '''
        raise ArchNotImplemented('archParseOpcode')

    def archGetRegisterGroups(self):
        '''
        Returns a tuple of tuples of registers for different register groups.
        If not implemented for an architecture, returns a single group with
        all non-meta registers.

        Example:
            [ ('all', ['eax', 'ebx', ...] ), ...]
        '''
        regctx = self.archGetRegCtx()
        allr = [rname for rname in regctx.getRegisterNames()]
        return [('all', allr)]

    def archModifyFuncAddr(self, va, info):
        '''
        Can modify the VA and context based on architecture-specific info.
        Default: return the same va, info

        This hook allows an architecture to correct VA and Architecture, such
        as is necessary for ARM/Thumb.

        "info" should be a dictionary with the {'arch': ARCH_FOO}

        eg.  for ARM, the ARM disassembler would hand in
            {'arch': ARCH_ARMV7}

        and if va is odd, that architecture's implementation would return
            (va & -2), {'arch': ARCH_THUMB}
        '''
        return va, info

    def archModifyXrefAddr(self, tova, reftype, rflags):
        '''
        Returns a potentially modified set of (tova, reftype, rflags).
        Default: return the same tova, reftype, rflags

        This hook allows an architecture to modify an Xref before it's set,
        which can be helpful for ARM/Thumb.
        '''
        return tova, reftype, rflags

    def archGetBadOps(self, byteslist=None):
        '''
        Returns a list of opcodes which are indicators of wrong disassembly.
        byteslist is None to use the architecture default, or can be a custom list.
        '''
        if byteslist is None:
            # if we've already done this exercize...
            if len(self.badops):
                return self.badops

            # otherwise, let's start with the architecture's badops list
            byteslist = self._arch_badopbytes

        self.badops = []
        for badbytes in byteslist:
            try:
                self.badops.append(self.archParseOpcode(badbytes))
            except:
                pass

        return self.badops

    def getEmulator(self):
        """
        Return a default instance of an emulator for the given arch.
        """
        raise ArchNotImplemented("getEmulator")

    def getPointerSize(self):
        """
        Get the size of a pointer in memory on this architecture.
        """
        raise ArchNotImplemented("getPointerSize")

    def pointerString(self, va):
        """
        Return a string representation for a pointer on this arch
        """
        raise ArchNotImplemented("pointerString")

    def getArchDefaultCall(self):
        return self._default_call

    def getPlatDefaultCall(self, platform):
        defcall = self._plat_def_calls.get(platform)
        return defcall

    def archGetPointerAlignment(self):
        return 1

def stealArchMethods(obj, archname):
    '''
    Used by objects which are expected to inherit from an
    architecture module but don't know which one until runtime!
    '''
    arch = getArchModule(archname)
    for name in dir(arch):
        o = getattr(arch, name, None)
        if type(o) == types.MethodType:
            setattr(obj, name, o)

class Operand:

    """
    Thses are the expected methods needed by any implemented operand object
    attached to an envi Opcode.  This does *not* have a constructor of it's
    pwn on purpose to cut down on memory use and constructor CPU cost.
    """

    def getOperValue(self, op, emu=None):
        """
        Get the current value for the operand.  If needed, use
        the given emulator/workspace/trace to resolve things like
        memory and registers.

        NOTE: This API may be passed a None emu and should return what it can
              (or None if it can't be resolved)
        """
        raise NotImplementedError("%s needs to implement getOperValue!" % self.__class__.__name__)

    def setOperValue(self, op, emu, val):
        """
        Set the current value for the operand.  If needed, use
        the given emulator/workspace/trace to assign things like
        memory and registers.
        """
        logger.warning("%s needs to implement setOperAddr!" % self.__class__.__name__)

    def isDeref(self):
        """
        If the given operand will dereference memory, this method must return True.
        """
        return False

    def isImmed(self):
        '''
        If the given operand represents an immediate value, this must return True.
        '''
        return False

    def isReg(self):
        '''
        If the given operand represents a register value, this must return True.
        '''
        return False

    def isDiscrete(self):
        '''
        If the given operand can be completly resolved without an emulator, return True.
        '''
        return False

    def getOperAddr(self, op, emu=None):
        """
        If the operand is a "dereference" operand, this method should use the
        specified op/emu to resolve the address of the dereference.

        NOTE: This API may be passed a None emu and should return what it can
              (or None if it can't be resolved)
        """
        logger.warning("%s needs to implement getOperAddr!" % self.__class__.__name__)

    def repr(self, op):
        """
        Used by the Opcode class to get a humon readable string for this operand.
        """
        return "unknown"

    def render(self, mcanv, op, idx):
        """
        Used by the opcode class when rendering to a memory canvas.
        """
        mcanv.addText(self.repr(op))

    def __ne__(self, op):
        return not op == self

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        #FIXME each one will need this...
        return True

class DerefOper(Operand):

    def isDeref(self):
        return True

class ImmedOper(Operand):

    def isImmed(self):
        return True

    def isDiscrete(self):
        return True

class RegisterOper(Operand):

    def isReg(self):
        return True

class Opcode:
    """
    A universal representation for an opcode
    """
    prefix_names = [] # flag->humon tuples

    def __init__(self, va, opcode, mnem, prefixes, size, operands, iflags=0):
        """
        constructor for the basic Envi Opcode object.  Arguments as follows:

        opcode   - An architecture specific numerical value for the opcode
        mnem     - A humon readable mnemonic for the opcode
        prefixes - a bitmask of architecture specific instruction prefixes
        size     - The size of the opcode in bytes
        operands - A list of Operand objects for this opcode
        iflags   - A list of Envi (architecture independant) instruction flags (see IF_FOO)
        va       - The virtual address the instruction lives at (used for PC relative immediates etc...)

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
        self.va = va

    def __ne__(self, op):
        return not op == self

    def __eq__(self, op):
        if not isinstance(op, Opcode):
            return False
        if self.opcode != op.opcode:
            return False
        if self.mnem != op.mnem:
            return False
        if self.size != op.size:
            return False
        if self.iflags != op.iflags:
            return False
        if len(self.opers) != len(op.opers):
            return False
        for i in range(len(self.opers)):
            if self.opers[i] != op.opers[i]:
                return False
        return True

    def __hash__(self):
        return int(hash(self.mnem) ^ (self.size << 4))

    def __repr__(self):
        """
        Over-ride this if you want to make arch specific repr.
        """
        pfx = self.getPrefixName()
        if pfx:
            pfx = '%s: ' % pfx
        return pfx + self.mnem + " " + ",".join([o.repr(self) for o in self.opers])

    def __len__(self):
        return int(self.size)

    # NOTE: From here down is mostly things that architecture specific opcode
    #       extensions should override.
    def isCall(self):
        return bool(self.iflags & IF_CALL)

    def isReturn(self):
        return bool(self.iflags & IF_RET)

    def getTargets(self, emu=None):
        """
        Determines the targets of call/branch instructions.  Fall throughs are
        not considered as targets. Deref branches are resolved.

        Returns ((bva, bflags),...)

        addr can be None in cases where the branch target cannot be computed.
        (for example, if BR_DEREF flag is set and cannot read the memory)
        Once resolved, the BR_DEREF flag is removed from branch flags.
        """
        remote_branches = []
        for bva, bflags in self.getBranches(emu=emu):
            if bflags & BR_FALL:
                continue

            if bva and (bflags & BR_DEREF):
                if emu is not None:
                    bva = emu.readMemoryFormat(bva, '<P')[0]
                    bflags &= (~BR_DEREF)
                else:
                    bva = None

            remote_branches.append((bva, bflags))

        return remote_branches

    def getBranches(self, emu=None):
        """
        Return a list of tuples.  Each tuple contains the target VA of the
        branch, and a possible set of flags showing what type of branch it is.

        See the BR_FOO types for all the supported envi branch flags....
        Example: for bva,bflags in op.getBranches():
        """
        return ()

    def genRefOpers(self, emu=None):
        '''
        Operand generator, yielding an (oper-index, operand) tuple from this
        Opcode... but only for operands which make sense for XREF analysis.
        Override when architecture makes use of odd operands like the program
        counter, which returns a real value even without an emulator.
        '''
        for oidx, o in enumerate(self.opers):
            yield (oidx, o)

    def render(self, mcanv):
        """
        Render this opcode to the memory canvas passed in.  This is used for both
        simple printing AND more complex representations.
        """
        mcanv.addText(repr(self))

    def getPrefixName(self):
        """
        Get the name of the prefixes associated with the specified
        architecture specific prefix bitmask.
        """
        ret = []
        for byte, name in self.prefix_names:
            if self.prefixes & byte:
                ret.append(name)
        return " ".join(ret)

    def getOperValue(self, idx, emu=None):
        oper = self.opers[idx]
        return oper.getOperValue(self, emu=emu)

    def getOperands(self):
        return self.opers

class Emulator(e_reg.RegisterContext, e_mem.MemoryObject):
    """
    The Emulator class is mostly "Abstract" in the java
    Interface sense.  The emulator should be able to
    be extended for the architecutures which are included
    in the envi framework.  You *must* mix in
    an instance of your architecture abstraction module.

    (NOTE: Most users will just use an arch mod and call getEmulator())

    The intention is for "light weight" emulation to be
    implemented mostly for user-space emulation of
    protected mode execution.
    """
    def __init__(self, archmod=None):

        self.metadata = {}
        e_mem.MemoryObject.__init__(self, arch=archmod._arch_id)
        e_reg.RegisterContext.__init__(self)

        self._emu_segments = [(0, 0xffffffff)]
        self._emu_call_convs = {}
        self._emu_opts = {}
        self._emu_optdocs = {}

        # Automagically setup an instruction mnemonic handler dict
        # by finding all methods starting with i_ and assume they
        # implement an instruction by mnemonic
        self.op_methods = {}
        for name in dir(self):
            if name.startswith("i_"):
                self.op_methods[name[2:]] = getattr(self, name)

    def initEmuOpt(self, opt, defval, doc):
        '''
        Initialize an emulator option used by the emulator type.
        Arch specific options should begin with <arch>: and platform
        options should begin with <platform>:
        '''
        self._emu_opts[opt] = defval
        self._emu_optdocs[opt] = doc

    def setEmuOpt(self, opt, val):
        '''
        Set a (previously initialized) emulator option.
        '''
        if opt not in self._emu_opts:
            raise Exception('Unknown Emu Opt: %s' % opt)
        self._emu_opts[opt] = val

    def getEmuOpt(self, opt):
        '''
        Retrieve the current value of an emulator option.
        ( emu impls may directly access _emu_opts for speed )
        '''
        if opt not in self._emu_opts:
            raise Exception('Unknown Emu Opt: %s' % opt)
        return self._emu_opts.get(opt)

    def setEndian(self, endian):
        '''
        Sets Endianness for the Emulator.
        '''
        for arch in self.imem_archs:
            arch.setEndian(endian)

    def getEndian(self):
        '''
        Returns the current Endianness for the emulator
        '''
        return self.imem_archs[0].getEndian()

    def getMeta(self, name, default=None):
        return self.metadata.get(name, default)

    def setMeta(self, name, value):
        """
        Set a meta key,value pair for this workspace.
        """
        self.metadata[name] = value

    def getArchModule(self):
        raise Exception('Emulators *must* implement getArchModule()!')

    def getEmuSnap(self):
        """
        Return the data needed to "snapshot" this emulator.  For most
        archs, this method will be enough (it takes the memory object,
        and register values with it)
        """
        regs = self.getRegisterSnap()
        mem = self.getMemorySnap()
        return regs,mem

    def setEmuSnap(self, snap):
        regs,mem = snap
        self.setRegisterSnap(regs)
        self.setMemorySnap(mem)

    @contextlib.contextmanager
    def snap(self):
        '''
        Utility function to try something with an emulator, and then revert it.
        If we fail to get a valid snap, we raise a base EmuException. Otherwise,
        we yield out the snap we received.

        On close, we try to rollback the emulator using the snap.
        '''
        try:
            snap = self.getEmuSnap()
        except Exception as e:
            raise EmuException(self, str(e)) from None

        try:
            yield snap
        finally:
            self.setEmuSnap(snap)

    def executeOpcode(self, opobj):
        """
        This is the core method for an emulator to do any running of instructions and
        setting of the program counter should an instruction require that.
        """
        raise ArchNotImplemented()

    def run(self, stepcount=None):
        """
        Run the emulator until "something" happens.
        (breakpoint, segv, syscall, etc...)

        Set stepcount in order to run that many instructions before pausing emulation
        """
        if stepcount is not None:
            for i in range(stepcount):
                self.stepi()
        else:
            while True:
                self.stepi()

    def stepi(self):
        pc = self.getProgramCounter()
        op = self.parseOpcode(pc)
        self.executeOpcode(op)

    def getSegmentInfo(self, op):
        idx = self.getSegmentIndex(op)
        return self._emu_segments[idx]

    def getSegmentIndex(self, op):
        """
        The *default* segmentation is none (most arch's will over-ride).
        This method may be implemented to return a segment index based on either
        emulator state or properties of the particular instruction in question.
        """
        return 0

    def setSegmentInfo(self, idx, base, size):
        '''
        Set a base and size for a given segment index.
        '''
        if len(self._emu_segments) - idx == 0:
            self._emu_segments.append( (base, size) )
            return

        self._emu_segments[idx] = (base,size)

    def getOperValue(self, op, idx):
        """
        Return the value for the operand at index idx for
        the given opcode reading memory and register states if necessary.

        In partially-defined emulation, this may return None
        """
        oper = op.opers[idx]
        return oper.getOperValue(op, self)

    def getOperAddr(self, op, idx):
        """
        Return the address that an operand which deref's memory
        would read from on getOperValue().
        """
        oper = op.opers[idx]
        return oper.getOperAddr(op, self)

    def setOperValue(self, op, idx, value):
        """
        Set the value of the target operand at index idx from
        opcode op.
        (obviously OM_IMMEDIATE *cannot* be set)
        """
        oper = op.opers[idx]
        return oper.setOperValue(op, self, value)

    def getCallArgs(self, count, cc):
        """
        Emulator implementors can implement this method to allow
        analysis modules a platform/architecture independant way
        to get stack/reg/whatever args.

        Usage: getCallArgs(3, "stdcall") -> (0, 32, 0xf00)
        """
        c = self._emu_call_convs.get(cc, None)
        if c is None:
            raise UnknownCallingConvention(cc)

        return c.getCallArgs(self, count)

    def execCallReturn(self, value, cc, argc=0):
        """
        Emulator implementors can implement this method to allow
        analysis modules a platform/architecture independant way
        to set a function return value. (this should also take
        care of any argument cleanup or other return time tasks
        for the calling convention)
        """
        c = self._emu_call_convs.get(cc, None)
        if c is None:
            raise UnknownCallingConvention(cc)

        return c.execCallReturn(self, value, argc)

    def addCallingConvention(self, name, obj):
        self._emu_call_convs[name] = obj

    def hasCallingConvention(self, name):
        if self._emu_call_convs.get(name) is not None:
            return True
        return False

    def getCallingConvention(self, name):
        return self._emu_call_convs.get(name)

    def getCallingConventions(self):
        return list(self._emu_call_convs.items())

    def readMemValue(self, addr, size):
        """
        Returns the value of the bytes at the "addr" address, given the size (currently, power of 2 only)
        """
        bytes = self.readMemory(addr, size)
        if bytes is None:
            return None
        if len(bytes) != size:
            raise Exception("Read Gave Wrong Length At 0x%.8x (va: 0x%.8x wanted %d got %d)" % (self.getProgramCounter(),addr, size, len(bytes)))

        return e_bits.parsebytes(bytes, 0, size, False, self.getEndian())

    def writeMemValue(self, addr, value, size):
        #FIXME change this (and all uses of it) to passing in format...
        #FIXME: Remove byte check and possibly half-word check.  (possibly all but word?)
        mask = e_bits.u_maxes[size]
        bytes = e_bits.buildbytes(value & mask, size, self.getEndian())

        self.writeMemory(addr, bytes)

    def readMemSignedValue(self, addr, size):
        #FIXME: Remove byte check and possibly half-word check.  (possibly all but word?)
        #FIXME: Handle endianness
        bytes = self.readMemory(addr, size)
        if bytes is None:
            return None
        fmttbl = e_bits.fmt_schars[self.getEndian()]
        return struct.unpack(fmttbl[size], bytes)[0]

    def integerSubtraction(self, op, sidx=0, midx=1):
        """
        Do the core of integer subtraction but only *return* the
        resulting value rather than assigning it.
        (allows cmp and sub to use the same code)
        """
        # Src op gets sign extended to dst
        ssize = op.opers[sidx].tsize
        msize = op.opers[midx].tsize
        subtra = self.getOperValue(op, sidx)
        minuend = self.getOperValue(op, midx)

        if subtra is None or minuend is None:
            self.undefFlags()
            return None

        return self.intSubBase(subtra, minuend, ssize, msize)

    def intSubBase(self, subtrahend, minuend, ssize, msize):
        '''
        Base for integer subtraction.
        Segmented such that order of operands can easily be overridden by
        subclasses.  Does not set flags (arch-specific), and doesn't set
        the dest operand.  That's up to the instruction implementation.

        So we can either do a BUNCH of crazyness with xor and shifting to
        get the necessary flags here, *or* we can just do both a signed and
        unsigned sub and use the results.

        Math vocab refresher: Subtrahend - Minuend = Difference
        '''
        usubtra = e_bits.unsigned(subtrahend, ssize)
        uminuend = e_bits.unsigned(minuend, msize)

        ssubtra = e_bits.signed(subtrahend, ssize)
        sminuend = e_bits.signed(minuend, msize)

        ures = usubtra - uminuend
        sres = ssubtra - sminuend

        return (ssize, msize, sres, ures, ssubtra, usubtra)

    def integerAddition(self, op):
        """
        Do the core of integer addition but only *return* the
        resulting value rather than assigning it.

        Architectures shouldn't have to override this as operand order 
        doesn't matter
        """
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)

        #FIXME PDE and flags
        if src is None:
            self.undefFlags()
            self.setOperValue(op, 1, None)
            return

        ssize = op.opers[0].tsize
        dsize = op.opers[1].tsize

        udst = e_bits.unsigned(dst, dsize)
        sdst = e_bits.signed(dst, dsize)

        usrc = e_bits.unsigned(src, dsize)
        ssrc = e_bits.signed(src, dsize)

        ures = usrc + udst
        sres = ssrc + sdst

        return (ssize, dsize, sres, ures, sdst, udst)

    def logicalAnd(self, op):
        src1 = self.getOperValue(op, 0)
        src2 = self.getOperValue(op, 1)

        # PDE
        if src1 is None or src2 is None:
            self.undefFlags()
            self.setOperValue(op, 1, None)
            return

        res = src1 & src2

        return res


class CallingConvention(object):
    '''
    Base class for all calling conventions. You must define class locals that
    define the fields below.

    All offsets defined in the constructor are relative to the stack counter at
    function entrypoint.

    Provides primitives that support the following situations:
    1. You are breakpointed at first instruction inside a function, have not
       executed that instruction, and want to modify the arguments, the return
       address, or the return value.  To modify the arguments or the return
       address, use 'setCallArgsRet'.  To modify the return value and then
       return, use 'execCallReturn'.
    2. You are breakpointed on the call to a function, have not executed the
       call instruction, and want to modify the arguments.  To modify the
       arguments use 'setPreCallArgs'.  You cannot change the return address
       from this location because once you step through the call, the processor
       will overwrite whatever you wrote at that location.
    3. You want to call a arbitrary function and return to the same location
       you are currently breakpointed at or another arbitrary location.  To
       call an arbitrary function, use 'executeCall'.

    Details:
        pad - # of bytes on stack to allocate between RET and First Stack Arg

        align - stack alignment.  as this is >= pointer size, this is used as
                the amount of space to leave for RET and Args

        delta - stack delta to apply before arguments

        flags - flags for this convention, namely Caller or Callee Cleanup

        arg_def - list of tuples indicating what each arg is.
            (CC_REG, REG_which)     - this Arg is a register, specifically
                                        REG_which
            (CC_STACK_INF, #)       - indicates the start of STACK-based Args
                                        Currently the number is ignored

        retaddr_def  - where does the function get a return address from?
            (CC_STACK, #) - on the stack, at offset 0
            (CC_REG, REG_which) - in register "REG_which", eg. REG_LR

        retval_def  - where does the function return value go?
            (CC_STACK, #) - on the stack, at offset 0
            (CC_REG, REG_which) - in register "REG_which", eg. REG_EAX

        CC_REG      - Ret, Retval or Arg use a particular register
        CC_STACK    - Ret, Retval or Arg use stack memory at offset #
        CC_STACK_INF- the rest of Args use stack memory starting at #

    '''
    pad = 0
    align = 4
    delta = 0       # FIXME: possible duplicate use with pad
    flags = 0
    arg_def = []
    retval_def = (CC_STACK, 0)
    retaddr_def = (CC_STACK, 0)

    # Examples...
    #flags = CC_CALLEE_CLEANUP
    #arg_def = [(CC_STACK_INF, 4),]
    #retaddr_def = (CC_STACK, 0)
    #retval_def = (CC_REG, REG_EAX)

    def getNumStackArgs(self, emu, argc):
        '''
        Returns the number of stack arguments.
        '''
        rargs = [ v for (t, v) in self.arg_def if t == CC_REG ]
        return max(argc - len(rargs), 0)

    def getStackArgOffset(self, emu, argc):
        '''
        Returns the number of bytes from RET to the first Stack Arg
        '''
        return self.pad + self.align

    def getPreCallArgs(self, emu, argc):
        '''
        Returns a list of the arguments passed to the function.

        Expects to be called at call/jmp to function entrypoint.
        '''
        args = []
        sp = emu.getStackCounter()
        sp += self.pad
        for arg_type, arg_val in self.arg_def:
            if argc <= 0:
                break

            if arg_type == CC_REG:
                args.append(emu.getRegister(arg_val))
                argc -= 1
            elif arg_type == CC_STACK:
                args.append(emu.readMemoryFormat(sp, '<P')[0])
                argc -= 1
                sp += self.align
            elif arg_type == CC_STACK_INF:
                values = emu.readMemoryFormat(sp, '<%dP' % argc)
                args.extend(values)
                argc -= len(values)
                if argc != 0:
                    raise Exception('wrong num of args from readMemoryFormat')
            else:
                raise Exception('unknown argument type')

        return args

    def getCallArgs(self, emu, argc):
        '''
        Returns a list of the arguments passed to the function.

        Expects to be called at the function entrypoint.
        '''
        sp = emu.getStackCounter()
        emu.setStackCounter(sp + self.align)
        args = self.getPreCallArgs(emu, argc)
        emu.setStackCounter(sp)
        return args

    def setPreCallArgs(self, emu, args):
        '''
        Writes arguments to appropriate locations.  No allocation is performed.

        Expects to be called at call/jmp to function entrypoint.
        '''
        cur_arg = 0
        argc = len(args)
        sp = emu.getStackCounter()
        sp += self.pad
        for arg_type, arg_val in self.arg_def:
            if argc <= 0:
                break

            if arg_type == CC_REG:
                emu.setRegister(arg_val, args[cur_arg])
                argc -= 1
                cur_arg += 1
            elif arg_type == CC_STACK:
                args += emu.writeMemoryFormat(sp, '<P', args[cur_arg])
                argc -= 1
                cur_arg += 1
                sp += self.align
            elif arg_type == CC_STACK_INF:
                arg_val -= self.align
                emu.writeMemoryFormat(sp, '<%dP' % argc, *args[cur_arg:])
                argc -= len(args[cur_arg:])
                if argc != 0:
                    raise Exception('wrong num of args from readMemoryFormat')
            else:
                raise Exception('unknown argument type')

    def setCallArgs(self, emu, args):
        '''
        Writes arguments to appropriate locations.  No allocation is performed.

        Expects to be called at the function entrypoint.
        '''
        emu.setStackCounter(emu.getStackCounter() + self.align)
        self.setPreCallArgs(emu, args)
        emu.setStackCounter(emu.getStackCounter() - self.align)

    def getReturnAddress(self, emu):
        '''
        Returns the return address.

        Expects to be called at the function entrypoint.
        '''
        rtype, rvalue = self.retaddr_def
        if rtype == CC_REG:
            ra = emu.getRegister(rvalue)
        elif rtype == CC_STACK:
            sp = emu.getStackCounter() + rvalue
            ra = emu.readMemoryFormat(sp, '<P')[0]
        else:
            raise Exception('unknown argument type')

        return ra

    def getReturnValue(self, emu):
        '''
        Returns the return value.

        Expects to be called after the function return.
        '''
        rtype, rvalue = self.retval_def
        if rtype == CC_REG:
            rv = emu.getRegister(rvalue)
        elif rtype == CC_STACK:
            sp = emu.getStackCounter() + rvalue
            rv = emu.readMemoryFormat(sp, '<P')[0]
        else:
            raise Exception('unknown argument type')

        return rv

    def setReturnAddress(self, emu, ra):
        '''
        Sets the return address.

        Expects to be called at the function entrypoint.
        '''
        rtype, rvalue = self.retaddr_def
        if rtype == CC_REG:
            emu.setRegister(rvalue, ra)
        elif rtype == CC_STACK:
            sp = emu.getStackCounter() + rvalue
            emu.writeMemoryFormat(sp, '<P', ra)
        else:
            raise Exception('unknown argument type')

    def setReturnValue(self, emu, rv):
        '''
        Sets the return value.
        '''
        rtype, rvalue = self.retval_def
        if rtype == CC_REG:
            emu.setRegister(rvalue, rv)
        elif rtype == CC_STACK:
            sp = emu.getStackCounter() + rvalue
            emu.writeMemoryFormat(sp, '<P', rv)
        else:
            raise Exception('unknown argument type')

    def allocateReturnAddress(self, emu):
        '''
        Allocates space on the stack for the return address.
        '''
        rtype, rvalue = self.retaddr_def
        if rtype != CC_STACK:
            return 0

        sp = emu.getStackCounter()
        sp -= self.align
        emu.setStackCounter(sp)
        return self.align

    def allocateArgSpace(self, emu, argc):
        '''
        Allocates space on the stack for arguments.
        '''
        num_stackargs = self.getNumStackArgs(emu, argc)
        sp = emu.getStackCounter()
        sp -= self.pad
        sp -= (self.align * num_stackargs)
        emu.setStackCounter(sp)

    def allocateCallSpace(self, emu, argc):
        '''
        Allocates space on the stack for arguments and the return address.
        '''
        self.allocateReturnAddress(emu)
        self.allocateArgSpace(emu, argc)

    def _dealloc(self, delta, argc):
        # Special method to allow symbolik cconv to hook...
        return delta + self.align * argc

    def deallocateCallSpace(self, emu, argc, precall=False):
        '''
        Removes space on the stack made for the arguments and the return
        address depending on the flags value of the calling convention.

        Returns the delta for the stack counter.

        Set precall=True if the calling convention has not allocated
        return address space ( ie, the "call" was not executed ).
        '''
        delta = self.delta

        rtype, rvalue = self.retaddr_def
        if rtype == CC_STACK and not precall:
            delta += self.align

        rtype, rvalue = self.retval_def
        if rtype == CC_STACK:
            delta += self.align

        if self.flags & CC_CALLEE_CLEANUP:
            for arg_type, arg_val in self.arg_def:
                if argc <= 0:
                    break
                if arg_type == CC_REG:
                    argc -= 1
                elif arg_type == CC_STACK:
                    delta += self.align
                    argc -= 1
                elif arg_type == CC_STACK_INF:
                    delta = self._dealloc(delta, argc)
                    argc = 0
                else:
                    raise Exception('unknown argument type')

        emu.setStackCounter(emu.getStackCounter() + delta)
        return delta

    def setCallArgsRet(self, emu, args=None, ra=None):
        '''
        Modifies the arguments and return address. No allocation is performed.

        If the return address is None, sets return address to instruction
        after the address currently set as the return address.

        Expects to be called at the function entrypoint.
        '''
        self.setCallArgs(emu, args)

        if ra is not None:
            self.setReturnAddress(emu, ra)

    def setupCall(self, emu, args=None, ra=None):
        '''
        Sets up a function with the given args and the specified return
        address.  Allocates space for the arguments and the return address,
        sets the args and return address.

        If the return address is None, sets return address to the current
        program counter.
        '''
        argv = []
        if args is not None:
            argv.extend(args)

        argc = len(argv)

        if ra is None:
            ra = emu.getProgramCounter()

        self.allocateCallSpace(emu, argc)
        self.setCallArgsRet(emu, args=argv, ra=ra)

    def executeCall(self, emu, va, args=None, ra=None):
        '''
        Calls setupCall and then directly sets the program counter to the
        specified address.
        '''
        self.setupCall(emu, args=args, ra=ra)
        emu.setProgramCounter(va)

    def execCallReturn(self, emu, value, argc):
        '''
        Forces a function to return the specified value.

        Reads the return address from the stack, deallocates the stack space
        allocated for the call, sets the return value, and sets the program
        counter to the previously read return address.

        Expects to be called at the function entrypoint.
        '''
        sp = emu.getStackCounter()
        ip = self.getReturnAddress(emu)
        self.deallocateCallSpace(emu, argc)

        self.setReturnValue(emu, value)
        emu.setProgramCounter(ip)

# NOTE: This mapping is needed because of inconsistancies
# in how different compilers and versions of python embed
# the machine setting.
arch_xlate_32 = {
    'i386':'i386',
    'i486':'i386',
    'i586':'i386',
    'i686':'i386',
    'x86':'i386',
    'i86pc':'i386', # Solaris
    '':'i386', # Stupid windows...
    'AMD64':'i386', # ActiveState python can say AMD64 in 32 bit install?
    # Arm!
    'armv6l':'armv6l',
    'armv7l':'armv7l',
}

arch_xlate_64 = {
    'x86_64':'amd64',
    'AMD64':'amd64',
    'amd64':'amd64',
    'i386':'amd64', # MAC ports builds are 64bit and say i386
    '':'amd64', # And again....
}

def getArchByName(archname):
    '''
    Get the architecture constant by the humon name.
    '''
    return arch_by_name.get(archname)

def getArchById(archid):
    '''
    Get the architecture name by the constant.
    '''
    return arch_names.get(archid)

def getCurrentArch():
    """
    Return an envi normalized name for the current arch.
    """
    width = struct.calcsize("P")
    mach = platform.machine()   # 'i386','ppc', etc...

    if width == 4:
        ret = arch_xlate_32.get(mach)

    elif width == 8:
        ret = arch_xlate_64.get(mach)

    if ret is None:
        raise ArchNotImplemented(mach)

    return ret

def getArchModule(name=None):
    """
    return an Envi architecture module instance for the following
    architecture name.

    Current architectures include:

    i386 - Intel i386
    amd64 - The new 64bit AMD spec.
    """
    if name is None:
        name = getCurrentArch()

    # Some builds have x86 (py2.6) and some have other stuff...
    if name in ['i386', 'i486', 'i586', 'i686', 'x86']:
        import envi.archs.i386 as e_i386
        return e_i386.i386Module()

    elif name in ('amd64', 'x86_64'):
        import envi.archs.amd64 as e_amd64
        return e_amd64.Amd64Module()

    elif name in ('arm', 'armv6l', 'armv7l'):
        import envi.archs.arm as e_arm
        return e_arm.ArmModule()

    elif name in ('thumb', 'thumb16', 'thumb2'):
        import envi.archs.thumb16 as e_thumb
        return e_thumb.Thumb16Module()

    elif name in ('msp430',):
        import envi.archs.msp430 as e_msp430
        return e_msp430.Msp430Module()

    elif name in ('h8',):
        import envi.archs.h8 as e_h8
        return e_h8.H8Module()

    else:
        raise ArchNotImplemented(name)

def getArchModules(default=ARCH_DEFAULT):
    '''
    Retrieve a default array of arch modules ( where index 0 is
    also the "named" or "default" arch module.
    '''
    import envi.archs.h8 as e_h8
    import envi.archs.arm as e_arm
    import envi.archs.i386 as e_i386
    import envi.archs.amd64 as e_amd64
    import envi.archs.thumb16 as e_thumb16
    import envi.archs.msp430 as e_msp430

    archs = [None]

    # These must be in ARCH_FOO order
    archs.append(e_i386.i386Module())
    archs.append(e_amd64.Amd64Module())
    archs.append(e_arm.ArmModule())
    archs.append(e_thumb16.Thumb16Module())
    archs.append(e_thumb16.ThumbModule())
    archs.append(e_msp430.Msp430Module())
    archs.append(e_h8.H8Module())

    # Set the default module ( or None )
    archs[ARCH_DEFAULT] = archs[default >> 16]

    return archs
