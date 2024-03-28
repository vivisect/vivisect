"""
The vivisect.parsers package contains all the known file format parsers
for vivisect.  Each parser module must implement the following functions:

    parseFile(workspace, filename):
        Load the file into the given workspace
    parseBytes(workspace, bytes):
        Load the file (pre-read in) into the workspace

"""
# Some parser utilities

import io
import sys
import struct
import hashlib
import zipfile

import vstruct.defs.macho as vs_macho

def md5File(filename):
    d = hashlib.md5()
    with open(filename, 'rb') as f:
        bytes = f.read(4096)
        while len(bytes):
            d.update(bytes)
            bytes = f.read(4096)
    return d.hexdigest()

def md5Bytes(bytes):
    d = hashlib.md5()
    d.update(bytes)
    return d.hexdigest()

def sha256File(filename):
    with open(filename, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest().upper()

def sha256Bytes(bytes):
    return hashlib.sha256(bytes).hexdigest().upper()

macho_magics = (
    vs_macho.MH_MAGIC,
    vs_macho.MH_CIGAM,
    vs_macho.MH_MAGIC_64,
    vs_macho.MH_CIGAM_64,
    vs_macho.FAT_MAGIC,
    vs_macho.FAT_CIGAM,
)

def guessFormat(bytez):
    if bytez.startswith(b'VIV'):
        return 'viv'

    if b'MSGVIV' in bytez[:8]:
        return 'mpviv'

    if bytez.startswith(b"MZ"):
        return 'pe'

    if bytez.startswith(b'\x7fELF'):
        return 'elf'

    if bytez.startswith(b'\x7fCGC'):
        return 'cgc'

    bytemagic = struct.unpack('<I', bytez[:4])[0]
    if bytemagic in macho_magics:
        return 'macho'

    if bytez[0] == ord(':'):
        return 'ihex'

    if bytez[0] == ord('S'):
        return 'srec'

    return 'blob'


def guessFormatFilename(filename):
    with open(filename, 'rb') as f:
        return guessFormat(f.read(32))


def getParserModule(fmt):
    mname = "vivisect.parsers.%s" % fmt
    mod = sys.modules.get(mname)
    if mod is None:
        __import__(mname)
        mod = sys.modules[mname]
    return mod


def getBytesParser(fmt):
    if fmt == 'pe':
        import PE
        return PE.peFromBytes
    elif fmt == 'elf':
        import Elf
        return Elf.elfFromBytes
    return None


ZIPKEY = 'filebytes'


def compressBytes(byts):
    with io.BytesIO() as fd:
        with zipfile.ZipFile(fd, mode='w', compression=zipfile.ZIP_DEFLATED) as zipr:
            zipr.writestr(ZIPKEY, byts)
        fd.seek(0)
        return fd.read()


def uncompressBytes(byts):
    with io.BytesIO(byts) as fd:
        with zipfile.ZipFile(fd, mode='r', compression=zipfile.ZIP_DEFLATED) as zipr:
            return zipr.read(ZIPKEY)
