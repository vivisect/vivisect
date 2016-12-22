"""
The vivisect.parsers package contains all the known file format parsers
for vivisect.  Each parser module must implement the following functions:

    parseFile(workspace, filename):
        Load the file into the given workspace
    parseBytes(workspace, bytes):
        Load the file (pre-read in) into the workspace

"""
# Some parser utilities

import sys
import struct
import hashlib

import vstruct.defs.macho as vs_macho


def md5File(filename: str):
    d = hashlib.md5()
    with open(filename, "rb") as f:
        bytes = f.read(4096)
        while len(bytes):
            d.update(bytes)
            bytes = f.read(4096)
    return d.hexdigest()


def md5Bytes(bytes):
    d = hashlib.md5()
    d.update(bytes)
    return d.hexdigest()


macho_magics = (
    vs_macho.MH_MAGIC,
    vs_macho.MH_CIGAM,
    vs_macho.MH_MAGIC_64,
    vs_macho.MH_CIGAM_64,
    vs_macho.FAT_MAGIC,
    vs_macho.FAT_CIGAM,
)


def guessFormat(bytes):
    if bytes.startswith(b'VIV'):
        return 'viv'

    if bytes.startswith(b"MZ"):
        return 'pe'

    if bytes.startswith(b"\x7fELF"):
        return 'elf'

    if bytes.startswith(b"\x7fCGC"):
        return 'cgc'

    bytemagic = struct.unpack('<I', bytes[:4])[0]
    if bytemagic in macho_magics:
        return 'macho'

    if bytes[0] == b':':
        return 'ihex'

    return 'blob'


def guessFormatFilename(filename):
    bytez = open(filename, "rb").read(32)
    return guessFormat(bytez)


def getParserModule(fmt):
    mname = "vivisect.parsers.%s" % fmt
    mod = sys.modules.get(mname)
    if mod is None:
        __import__(mname)
        mod = sys.modules[mname]
    return mod
