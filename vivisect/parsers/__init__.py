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
import glob
import struct
import hashlib
import importlib
import zipfile

import vstruct.defs.macho as vs_macho

from os.path import dirname, basename, isfile, join
parserpaths = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [ basename(f)[:-3] for f in parserpaths if isfile(f) and not f.endswith('__init__.py')]

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

parsers = []
parsedict = {}

def getParsers():
    global parsers, parsedict
    if len(parsers):
        return parsers

    for idx, mname in enumerate(__all__):
        parserpath = parserpaths[idx]
        parser = importlib.import_module('vivisect.parsers.' + mname)
        parser.__mname__ = mname
        parsers.append(parser)
        parsedict[mname] = parser

    return parsers

def guessFormat(bytez):
    if bytez.startswith(b'VIV'):
        return 'viv'

    elif bytez.startswith(b'MSGVIV'):
        return 'mpviv'

    for parser in getParsers():
        if parser.isParser(bytez):
            return parser.__mname__

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
