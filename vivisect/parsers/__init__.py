
"""
The vivisect.parsers package contains all the known file format parsers
for vivisect.  Each parser module must implement the following functions:

    parseFile(workspace, filename):
        Load the file into the given workspace
    parseBytes(workspace, bytes):
        Load the file (pre-read in) into the workspace

"""
# Some parser utilities

import imp
import md5
import sys
import glob
import struct
import hashlib
import importlib

import vstruct.defs.macho as vs_macho

from os.path import dirname, basename, isfile, join
parserpaths = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [ basename(f)[:-3] for f in parserpaths if isfile(f) and not f.endswith('__init__.py')]

def md5File(filename):
    d = md5.md5()
    f = file(filename,"rb")
    bytes = f.read(4096)
    while len(bytes):
        d.update(bytes)
        bytes = f.read(4096)
    return d.hexdigest()

def md5Bytes(bytes):
    d = md5.md5()
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

def guessFormat(bytes):
    if bytes.startswith('VIV'):
        return 'viv'

    for parser in getParsers():
        if parser.isParser(bytes):
            return parser.__mname__

    return 'blob'

def guessFormatFilename(filename):
    bytez = file(filename, "rb").read(32)
    return guessFormat(bytez)

def getParserModule(fmt):
    mname = "vivisect.parsers.%s" % fmt
    mod = sys.modules.get(mname)
    if mod == None:
        __import__(mname)
        mod = sys.modules[mname]
    return mod

