import binascii


class ConfigNoAssignment(Exception):
    def __init__(self, optstr):
        Exception.__init__(self)
        self.optstr = optstr

    def __str__(self):
        return "No value given in option %s" % self.optstr


class ConfigInvalidName(Exception):
    def __init__(self, optpath):
        Exception.__init__(self)
        self.optpath = optpath

    def __str__(self):
        return 'Invalid Config Name: %s' % self.optpath


class ConfigInvalidOption(Exception):
    def __init__(self, optname):
        Exception.__init__(self)
        self.optname = optname

    def __str__(self):
        return 'Invalid Config Option: %s' % self.optname


class InvalidRegisterName(Exception):
    pass


class QueueShutdown(Exception):
    pass


class EnviException(Exception):
    def __str__(self):
        return repr(self)


class InvalidSymbolCache(EnviException):
    def __init__(self, vhash):
        EnviException.__init__(self, 'Invalid Symbol Cache Hash: %s' % vhash)


class InvalidInstruction(EnviException):
    """
    Raised by opcode parsers when the specified
    bytes do not represent a valid opcode
    """
    def __init__(self, bytez=None, mesg=None, va=0):
        msg = []
        if mesg is not None:
            msg = [mesg]

        if bytez is not None:
            msg.append("'" + binascii.hexlify(bytez).decode('utf-8') + "'")

        if va != 0:
            msg.append('at ' + hex(va))
        EnviException.__init__(self, ' '.join(msg))


class BadOpcode(EnviException):
    def __init__(self, op):
        EnviException.__init__(self, 'Hit opcode that cannot be emulated at 0x%.8x: %s' % (op.va, str(op)))


class InvalidAddress(EnviException):
    def __init__(self, va):
        self.va = va
        msg = 'Invalid Address: %s' % str(va)
        EnviException.__init__(self, msg)


class SegmentationViolation(EnviException):
    """
    Raised by an Emulator extension when you
    bad-touch memory. (Likely from memobj).
    """
    def __init__(self, va, msg=None):
        if msg is None:
            msg = "Bad Memory Access: %s" % hex(va)
        EnviException.__init__(self, msg)
        self.va = va


class ArchNotImplemented(EnviException):
    """
    Raised by various Envi components when the architecture
    does not implement that envi component.
    """
    pass


class EmuException(EnviException):
    """
    A parent for all emulation exceptions so catching
    them can be easy.
    """
    def __init__(self, emu, msg=None):
        EnviException.__init__(self, msg)
        self.va = emu.getProgramCounter()

    def __repr__(self):
        return "%s at %s" % (self.__class__.__name__, hex(self.va))


class UnsupportedInstruction(EmuException):
    """
    Raised by emulators when the given instruction
    is not implemented by the emulator.
    """
    def __init__(self, emu, op):
        EmuException.__init__(self, emu)
        self.op = op

    def __repr__(self):
        return "Unsupported Instruction: 0x%.8x %s" % (self.va, repr(self.op))


class DivideByZero(EmuException):
    """
    Raised by an Emulator when a divide/mod has
    a 0 divisor...
    """
    pass


class MultiplyError(EmuException):
    """
    Raised by an Emulator when multiply falls outside of the specified range
    """
    pass


class DivideError(EmuException):
    """
    Raised by an Emulator when a a divide falls out
    of the specified range.
    """
    pass


class BreakpointHit(EmuException):
    """
    Raised by an emulator when you execute a breakpoint instruction
    """
    pass


class PDEUndefinedFlag(EmuException):
    """
    This exception is raised when a conditional operation is dependant on
    a flag state that is unknown.
    """
    pass


class PDEException(EmuException):
    """
    This exception is used in partially defined emulation to signal where
    execution flow becomes un-known due to undefined values.  This is considered
    un-recoverable.
    """
    pass


class UnknownCallingConvention(EmuException):
    """
    Raised when the getCallArgs() or execCallReturn() methods
    are given an unknown calling convention type.
    """
    pass


class MapOverlapException(EnviException):
    """
    Raised when adding a memory map to a MemoryObject which overlaps
    with another already existing map.
    """
    def __init__(self, map1, map2):
        self.map1 = map1
        self.map2 = map2
        margs = (map1[0], map1[1], map2[0], map2[1])
        EnviException.__init__(self, "Map At 0x%.8x (%d) overlaps map at 0x%.8x (%d)" % margs)


class QuietNaN(Exception):
    pass


class SignalNaN(Exception):
    pass


class InvalidOperand(Exception):
    def __init__(self, valu):
        self.valu = valu

    def __repr__(self):
        return "%s at %s" % (self.__class__.__name__, str(self.valu))

class GeneralProtection(EnviException):
    def __init__(self, op):
        EnviException.__init__(self, 'General Protection exception (0x%.8x: %s)' % (op.va, str(op)))
        self.op = op
