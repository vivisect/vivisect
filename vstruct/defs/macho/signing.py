import vstruct

from vstruct.primitives import *
from vstruct.defs.macho.const import *


class CS_CodeDirectory(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.magic = v_uint32(bigend=True)
        self.length = v_uint32(bigend=True)
        self.version = v_uint32(bigend=True)
        self.flags = v_uint32()  # setup and mode flags
        self.hashOffset = v_uint32(bigend=True)
        self.identOffset = v_uint32(bigend=True)
        self.nSpecialSlots = v_uint32(bigend=True)
        self.nCodeSlots = v_uint32(bigend=True)
        self.codeLimit = v_uint32(bigend=True)

        self.hashSize = v_uint8()
        self.hashType = v_uint8()
        self.platform = v_uint8()
        self.pageSize = v_uint8()
        self.spare2 = v_uint32(bigend=True)

    def vsParse(self, bytes, offset=0):
        vstruct.VStruct.vsParse(self, bytes, offset=offset)
        # parse out the base struct, grab the version, and then reparse to
        # grab the mess of extended fields

        if self.version >= CS_SUPPORTSSCATTER:
            self.scatterOffset = v_uint32(bigend=True)

        if self.version >= CS_SUPPORTSTEAMID:
            self.teamOffset = v_uint32(bigend=True)

        if self.version >= CS_SUPPORTSCODELIMIT64:
            self.spare3 = v_uint32(bigend=True)
            self.codeLimit64 = v_uint64(bigend=True)

        if self.version >= CS_SUPPORTSEXECSEG:
            self.execSegBase = v_uint64(bigend=True)
            self.execSegLimit = v_uint64(bigend=True)
            self.execSegFlags = v_uint64(bigend=True)

        return vstruct.VStruct.vsParse(self, bytes, offset=offset)


class CS_Blob(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.magic = v_uint32(bigend=True)
        self.length = v_uint32(bigend=True)


class CS_BlobIndex(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.type = v_uint32(bigend=True)
        self.offset = v_uint32(bigend=True)


class CS_SuperBlob(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.magic = v_uint32(bigend=True)
        self.length = v_uint32(bigend=True)
        self.count = v_uint32(bigend=True)

        self.blobindexes = vstruct.VArray()

    def vsParse(self, bytes, offset=0):
        # parse out count and then the blob indexes
        retoff = vstruct.VStruct.vsParse(self, bytes, offset=offset)
        newoff = offset + retoff
        for i in range(self.count):
            indx = CS_BlobIndex()
            indx.vsParse(bytes, offset=newoff)
            newoff += len(indx)
            self.blobindexes.vsAddElement(indx)
        return retoff


'''
Preserving for posterity, but this struct was pulled from llvm's mach-o code, which is about
the only decent place I could find the most up to date version of this

struct CS_CodeDirectory {
  uint32_t magic;         /* magic number (CSMAGIC_CODEDIRECTORY) */
  uint32_t length;        /* total length of CodeDirectory blob */
  uint32_t version;       /* compatibility version */
  uint32_t flags;         /* setup and mode flags */
  uint32_t hashOffset;    /* offset of hash slot element at index zero */
  uint32_t identOffset;   /* offset of identifier string */
  uint32_t nSpecialSlots; /* number of special hash slots */
  uint32_t nCodeSlots;    /* number of ordinary (code) hash slots */
  uint32_t codeLimit;     /* limit to main image signature range */
  uint8_t hashSize;       /* size of each hash in bytes */
  uint8_t hashType;       /* type of hash (cdHashType* constants) */
  uint8_t platform;       /* platform identifier; zero if not platform binary */
  uint8_t pageSize;       /* log2(page size in bytes); 0 => infinite */
  uint32_t spare2;        /* unused (must be zero) */

  /* Version 0x20100 */
  uint32_t scatterOffset; /* offset of optional scatter vector */

  /* Version 0x20200 */
  uint32_t teamOffset; /* offset of optional team identifier */

  /* Version 0x20300 */
  uint32_t spare3;      /* unused (must be zero) */
  uint64_t codeLimit64; /* limit to main image signature range, 64 bits */

  /* Version 0x20400 */
  uint64_t execSegBase;  /* offset of executable segment */
  uint64_t execSegLimit; /* limit of executable segment */
  uint64_t execSegFlags; /* executable segment flags */
};

'''
