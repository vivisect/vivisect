"""
All the exception types raised by workspace APIs go here.
"""


class BlobArchException(Exception):
    def __init__(self):
        Exception.__init__(self, 'Blob loader *requires* arch option (-O viv.parsers.blob.arch="<archname>")')


class BadOutInstruction(Exception):
    def __init__(self, va):
        Exception.__init__(self, 'Hit out instruction at 0x%.8x' % va)


class InvalidLocation(Exception):
    def __init__(self, va, msg=None):
        Exception.__init__(self, 'Invalid Location 0x%.8x: %s' % (va, msg))


class DuplicateName(Exception):
    def __init__(self, origva, newva, name):
        Exception.__init__(self, 'Duplicate Name: %s at 0x%.8x and 0x%.8x' % (name, origva, newva))


class InvalidVaSet(Exception):
    def __init__(self, name):
        Exception.__init__(self, 'Invalid Va Set Specified: %s' % name)


class InvalidFunction(Exception):
    def __init__(self, va):
        Exception.__init__(self, 'VA 0x%.8x is not a function' % va)


class InvalidCodeBlock(Exception):
    def __init__(self, va):
        Exception.__init__(self, 'VA 0x%.8x is not in a code block!' % va)


class BadOpBytes(Exception):
    def __init__(self, va):
        Exception.__init__(self, 'Hit known badop bytes at va 0x%.8x ' % va)


class UnknownCallingConvention(Exception):
    def __init__(self, fva, cc=None):
        Exception.__init__(self, 'Function 0x%.8x has unknown CallingConvention: %s' % (fva, cc))


class InvalidWorkspace(Exception):
    """
    Raised when a storage module is given bunk data for loading
    a workspace.
    """
    def __init__(self, nameinfo, errinfo):
        Exception.__init__(self, 'Failed to load %s: %s' % (nameinfo, errinfo))


class InvalidArchitecture(Exception):
    def __init__(self, fileformat, arch):
        Exception.__init__(self, 'Architecture %s is not supported for %s' % (arch, fileformat))
        self.fileformat = fileformat
        self.arch = arch


class CorruptFile(Exception):
    def __init__(self, fileformat, message):
        super(CorruptFile, self).__init__('%s: corrupt file: %s' % (fileformat, message))
        self.fileformat = fileformat
        self.message = message


class CorruptPeFile(CorruptFile):
    def __init__(self, message):
        super(CorruptPeFile, self).__init__("PE", message)
