# the PDB file format is a specialized case of a "Multistream File"
# LLVM has excellent resources on it: https://llvm.org/docs/PDB/index.html
# and https://llvm.org/docs/PDB/MsfFile.html
# Microsoft also has published info here on it: https://github.com/Microsoft/microsoft-pdb

import math

import vstruct
from vstruct.primitives import *

PDBSIG = b''

class SuperBlock(vstruct.VStruct):
    def __init__(self):
        super().__init__()
        self.magic = v_bytes(size=0x20)
        self.blockSize = v_uint32(bigend=False)
        self.freeBlockMapBlock = v_uint32(bigend=False)
        self.numBlocks = v_uint32(bigend=False)
        self.numDirBytes = v_uint32(bigend=False)
        self.unknown = v_uint32(bigend=False)
        self.blockMapAddr = v_uint32(bigend=False)

class StreamDirectory(vstruct.VStruct):
    def __init__(self, blksize):
        super().__init__()
        self.blockSize = blksize
        self.numStreams = v_uint32(bigend=False)
        # self.streamSizes = vstruct.VArray()
        # self.streamBlocks = vstruct.VArray()

    def pcb_numStreams(self):
        self.streamSizes = vstruct.VArray([v_uint32(bigend=False) for i in range(self.numStreams)])

    def pcb_streamSizes(self):
        nums = []
        maxSize = 2 ** 32 - 1
        for idx, valu in self.streamSizes:
            if valu == maxSize:
                nums.append(0)
                continue
            nums.append(math.ceil(int(valu)/self.blockSize))

        self.streamBlocks = vstruct.VArray()
        for numblks in nums:
            blks = vstruct.VArray([v_uint32(bigend=False) for i in range(numblks)])
            self.streamBlocks.vsAddElement(blks)

class PDBStreamHeader(vstruct.VStruct):
    def __init__(self):
        super().__init__()
        self.version = v_uint32(bigend=False)
        self.sig = v_uint32(bigend=False)
        self.age = v_uint32(bigend=False)
        self.guid = GUID()

class TPIStreamHeader(vstruct.VStruct):
    def __init__(self):
        super().__init__()

        self.Version = v_uint32(bigend=False)
        self.headerSize = v_uint32(bigend=False)
        self.typeIndexBegin = v_uint32(bigend=False)
        self.typeIndexEnd = v_uint32(bigend=False)
        self.typeRecordBytes = v_uint32(bigend=False)

        self.hashStreamIdx = v_uint16(bigend=False)
        self.hashAuxStreamIdx = v_uint16(bigend=False)
        self.HashKeySize = v_uint32(bigend=False)
        self.NumHashBuckets = v_uint32(bigend=False)

        self.HashValueBufferOffset = v_int32(bigend=False)
        self.HashValueBufferLength = v_uint32(bigend=False)

        self.IndexOffsetBufferOffset = v_int32(bigend=False)
        self.IndexOffsetBufferLength = v_uint32(bigend=False)

        self.HashAdjBufferOffset = v_int32(bigend=False)
        self.HashAdjBufferLength = v_uint32(bigend=False)

class DBIStreamHeader(vstruct.VStruct):
    def __init__(self):
        super().__init__()
        self.VersionSignature = v_int32(bigend=False)
        self.VersionHeader = v_uint32(bigend=False)
        self.Age = v_uint32(bigend=False)
        self.GlobalStreamIndex = v_uint16(bigend=False)
        self.BuildNumber = v_uint16(bigend=False)
        self.PublicStreamIndex = v_uint16(bigend=False)
        self.PdbDllVersion = v_uint16(bigend=False)
        self.SymRecordStream = v_uint16(bigend=False)
        self.PdbDllRbld = v_uint16(bigend=False)
        self.ModInfoSize = v_int32(bigend=False)
        self.SectionContributionSize = v_int32(bigend=False)
        self.SectionMapSize = v_int32(bigend=False)
        self.SourceInfoSize = v_int32(bigend=False)
        self.TypeServerMapSize = v_int32(bigend=False)
        self.MFCTypeServerIndex = v_uint32(bigend=False)
        self.OptionalDbgHeaderSize = v_int32(bigend=False)
        self.ECSubstreamSize = v_int32(bigend=False)
        self.Flags = v_uint16(bigend=False)
        self.Machine = v_uint16(bigend=False)
        self.Padding = v_uint32(bigend=False)