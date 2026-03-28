# Base Microsoft protocol, but many fields are left undocumented
# https://winprotocoldoc.blob.core.windows.net/productionwindowsarchives/MS-SHLLINK/%5bMS-SHLLINK%5d.pdf

# Other research for filling in the things Microsoft didn't
# https://github.com/libyal/libfwsi/blob/main/documentation/Windows%20Shell%20Item%20format.asciidoc

# NOTE: all things are little-endian

import logging

import vstruct

from enum import IntFlag, IntEnum, auto

from vstruct.primitives import v_uint32, v_uint16, v_uint8, v_zstr, v_zwstr, GUID, v_uint64, v_wstr, v_str, v_bytes

from vstruct.defs.mspropstore import PropertyStorage

logger = logging.getLogger(__name__)


class LinkFlags(IntFlag):
    HasLinkTargetIDList = auto()
    HasLinkInfo = auto()
    HasName = auto()
    HasRelativePath = auto()
    HasWorkingDir = auto()
    HasArguments = auto()
    HasIconLocation = auto()
    IsUnicode = auto()
    ForceNoLinkInfo = auto()
    HasExpString = auto()
    RunInSeparateProcess = auto()
    Unused1 = auto()
    HasDawinID = auto()
    RunAsUser = auto()
    HasExpIcon = auto()
    NoPidAlias = auto()
    Unused2 = auto()
    RunWithShimLayer = auto()
    ForceNoLinkTrack = auto()
    EnableTargetMetadata = auto()
    DisableLinkPathTracking = auto()
    DisableKnownFolderTracking = auto()
    DisableKnownFolderAlias = auto()
    AllowLinkToLink = auto()
    UnaliasOnSave = auto()
    PreferEnvironmentPath = auto()
    KeepLocalIDListForUNCTarget = auto()


class LinkInfoFlags(IntFlag):
    VolumeIDAndLocalBasePath = auto()
    CommonNetworkRelativeLinkAndPathSuffix = auto()


class DriveTypes(IntEnum):
    Unknown = auto()
    NoRootDir = auto()
    Removable = auto()
    Fixed = auto()
    Remote = auto()
    Cdrom = auto()
    Ramdisk = auto()


class ExtraDataSigs(IntEnum):
    Console = 0xA0000002
    ConsoleFE = 0xA0000004
    Darwin = 0xA0000006
    Environment = 0xA0000001
    IconEnvironment = 0xA0000007
    KnownFolder = 0xA000000B
    PropertyStore = 0xA0000009
    Shim = 0xA0000008
    SpecialFolder = 0xA0000005
    Tracker = 0xA0000003
    VistaAndAboveIDList = 0xA000000C


# <Header> [<Link target Id LIST>] [<LinkInfo>] [<String data>] [<extra data>]
class LnkShellLinkHeader(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)

        self.headersize = v_uint32()
        self.linkclsid = GUID()
        self.linkflags = v_uint32()
        self.fileattrs = v_uint32()

        self.created = v_uint64()
        self.accessed = v_uint64()
        self.written = v_uint64()

        self.filesize = v_uint32()
        self.iconindex = v_uint32()
        self.showcmd = v_uint32()

        self.hotkey = v_uint16()

        self.reserved1 = v_uint16()
        self.reserved2 = v_uint32()
        self.reserved3 = v_uint32()


class VolumeID(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.size = v_uint32()
        self.drivetype = v_uint32()
        self.driveserial = v_uint32()
        self.volumelabeloffset = v_uint32()

    def pcb_volumelabeloffset(self):
        if self.volumelabeloffset == 0x14:
            self.volumelabeloffsetunicode = v_uint32()
            self.data = v_zwstr()
        else:
            self.data = v_zstr()


class ItemBase(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)

        self.size = v_uint16()
        self.iden = v_uint8()


class ExtraDataBlock(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.blocksize = v_uint32()
        self.blocksig = v_uint32()


class ConsoleBlock(ExtraDataBlock):
    def __init__(self):
        ExtraDataBlock.__init__(self)

        self.fillAttrs = v_uint16()
        self.popupFillAttrs = v_uint16()

        self.screenBufferSizeX = v_uint16()
        self.screenBufferSizeY = v_uint16()

        self.windowSizeX = v_uint16()
        self.windowSizeY = v_uint16()

        self.windowOriginX = v_uint16()
        self.windowOriginY = v_uint16()

        self.unused1 = v_uint32()
        self.unused2 = v_uint32()

        self.fontSize = v_uint32()
        self.fontFamily = v_uint32()
        self.fontWeight = v_uint32()

        self.faceName = v_wstr(size=32)  # unicode, 64 bytes

        self.cursorSize = v_uint32()
        self.fullScreen = v_uint32()
        self.quickEdit = v_uint32()

        self.insertMode = v_uint32()
        self.autoPosition = v_uint32()
        self.historyBufferSize = v_uint32()
        self.numberofHistoryBuffers = v_uint32()
        self.historyNoDup = v_uint32()
        self.colorTable = vstruct.VArray([v_uint32() for i in range(16)])


class ConsoleFEBlock(ExtraDataBlock):
    def __init__(self):
        ExtraDataBlock.__init__(self)

        self.codepage = v_uint32()


class TargetBlock(ExtraDataBlock):
    def __init__(self):
        ExtraDataBlock.__init__(self)
        self.targetAnsi = v_str(size=260)
        self.targetUnicode = v_wstr(size=520)


class FolderBlock(ExtraDataBlock):
    def __init__(self):
        ExtraDataBlock.__init__(self)
        self.folderid = GUID()
        self.offset = v_uint32()


class ShimBlock(ExtraDataBlock):
    def __init__(self):
        ExtraDataBlock.__init__(self)
        self.layername = v_zwstr()


class TrackerBlock(ExtraDataBlock):
    # See: https://winprotocoldoc.blob.core.windows.net/productionwindowsarchives/MS-DLTW/%5bMS-DLTW%5d.pdf
    def __init__(self):
        ExtraDataBlock.__init__(self)
        self.length = v_uint32()
        self.version = v_uint32()
        self.machineid = v_str(size=16)

        self.droidfile = GUID()
        self.droidvolume = GUID()

        self.droibirthfile = GUID()
        self.droibirthvolume = GUID()


class RootFolderItem(ItemBase):
    def __init__(self):
        ItemBase.__init__(self)

        self.sortidx = v_uint8()
        self.folderiden = GUID()

        # TODO: There's a pair of possible extension items here, but they're undocumented
        # even through extensive research by others. Skip for now.


class VolumeItem(ItemBase):
    def __init__(self):
        ItemBase.__init__(self)

    def pcb_iden(self):
        if self.iden & 0x1 == 0:
            self.flags = v_uint8()
        self.volume = v_str()


class FileEntryItem(ItemBase):
    def __init__(self):
        ItemBase.__init__(self)

    def pcb_iden(self):
        self.unk = v_uint8()
        self.filesize = v_uint32()
        self.lastmod = v_uint32()

        self.fileattrs = v_uint16()

        unicode = self.iden & 0x04 != 0
        if unicode:
            self.primary_name = v_zwstr()
        else:
            self.primary_name = v_zstr()

    def pcb_primary_name(self):
        # if this is an ascii string and we're not 16-bit aligned,
        # consume an extra padded byte to get us to 16 alignment
        unicode = self.iden & 0x04 != 0
        # include null terminator in length calculation
        if unicode == 0 and ((len(self.primary_name) + 1) * 8) % 16 != 0:
            self.padding = v_bytes(size=1)

        self.extsize = v_uint16()
        self.extver = v_uint16()
        self.extsig = v_uint32()
        self.extcreate = v_uint32()
        self.extaccess = v_uint32()
        self.extunk = v_uint16()

    def pcb_extver(self):
        if self.extver >= 7:
            self.o_unk = v_uint16()
            self.o_ref = v_uint64()
            self.o_wat = v_uint64()

        if self.extver >= 3:
            self.longstr_size = v_uint16()

        if self.extver >= 9:
            self.unk3 = v_uint32()

        if self.extver >= 8:
            self.unk4 = v_uint32()

        if self.extver >= 3:
            self.longname = v_zwstr()

    def pcb_longstr_size(self):
        if self.longstr_size > 0:
            if self.extver >= 7:
                self.localname = v_zwstr()
            elif self.extver >= 3:
                self.localname = v_str()

        if self.extver >= 3:
            self.firstextoffset = v_uint16()


class CommonNetworkRelativeLink(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)

        self.size = v_uint32()
        self.flags = v_uint32()

        self.netnameoffset = v_uint32()
        self.devicenameoffset = v_uint32()
        self.networkprovidertype = v_uint32()

    def pcb_networkprovidertype(self):
        if self.netnameoffset > 0x14:
            self.netnameoffsetunicode = v_wstr()
            self.devicenameoffsetunicode = v_wstr()

        self.netname = v_str()
        self.devicename = v_str()

        self.netnameunicode = v_wstr()
        self.devicenameunicode = v_wstr()


class LinkInfo(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)

        self.size = v_uint32()
        self.headersize = v_uint32()
        self.flags = v_uint32()

        self.VolumeIdOffset = v_uint32()
        self.LocalBasePathOffset = v_uint32()
        self.CommonNetworkRelativeLinkOffset = v_uint32()
        self.CommonPathSuffixOffset = v_uint32()

    def pcb_CommonNetworkRelativeLinkOffset(self):
        if self.headersize >= 0x24:
            self.LocalBasePathOffsetUnicode = v_uint32()
            self.CommonPathSuffixOffsetUnicode = v_uint32()

        if self.flags & LinkInfoFlags.VolumeIDAndLocalBasePath:
            self.volumeid = VolumeID()
            self.localbasepath = v_zstr()

        if self.flags & LinkInfoFlags.CommonNetworkRelativeLinkAndPathSuffix:
            self.CommonNetworkRelativeLink = CommonNetworkRelativeLink()

        self.CommonPathSuffix = v_zstr()

        if self.flags & LinkInfoFlags.VolumeIDAndLocalBasePath and self.headersize >= 0x24:
            self.LocalBasePathUnicode = v_zwstr()
            self.CommonPathSuffixUnicode = v_zwstr()


class StringDataItem(vstruct.VStruct):
    def __init__(self, unicode=False):
        vstruct.VStruct.__init__(self)

        self.unicode = unicode
        self.count = v_uint16()

    def pcb_count(self):
        # The "string" mentioned is specifcally stated "MUST NOT be NULL TERMINATED"
        if self.unicode:
            self.data = v_bytes(size=self.count*2)
        else:
            self.data = v_bytes(size=self.count)


class Lnk:
    def __init__(self, byts):
        offset = 0
        self.header = LnkShellLinkHeader()
        self.header.vsParse(byts)

        self.items = None
        self.linkinfo = None

        # StringData items
        self.nameInfo = None
        self.relPath = None
        self.workingDir = None
        self.cmdargs = None
        self.iconLoc = None

        # ExtraData items
        self.console = None
        self.consolefe = None
        self.darwin = None
        self.envVar = None
        self.iconEnvData = None
        self.knownFolder = None
        self.propStore = None
        self.shimData = None
        self.specialFolder = None
        self.trackerData = None
        self.vistaIDList = None

        self.leftovers = None

        offset += len(self.header)
        unicode = self.header.linkflags & LinkFlags.IsUnicode != 0

        if self.header.linkflags & LinkFlags.HasLinkTargetIDList:
            self.items, offset = self._parseItemID(byts, offset)

        if self.header.linkflags & LinkFlags.HasLinkInfo:
            # LinkInfo
            self.linkinfo = LinkInfo()
            self.linkinfo.vsParse(byts[offset:])

            offset += self.linkinfo.size

        # NOTE: StringData isn't really one unifed structure.
        # It's a collection of things controlled by various flags that all happen to look the same.
        if self.header.linkflags & LinkFlags.HasName:
            self.nameInfo = StringDataItem(unicode=unicode)
            self.nameInfo.vsParse(byts[offset:])
            offset += len(self.nameInfo)

        if self.header.linkflags & LinkFlags.HasRelativePath:
            self.relPath = StringDataItem(unicode=unicode)
            self.relPath.vsParse(byts[offset:])
            offset += len(self.relPath)

        if self.header.linkflags & LinkFlags.HasWorkingDir:
            self.workingDir = StringDataItem(unicode=unicode)
            self.workingDir.vsParse(byts[offset:])
            offset += len(self.workingDir)

        if self.header.linkflags & LinkFlags.HasArguments:
            self.cmdargs = StringDataItem(unicode=unicode)
            self.cmdargs.vsParse(byts[offset:])
            offset += len(self.cmdargs)

        if self.header.linkflags & LinkFlags.HasIconLocation:
            self.iconLoc = StringDataItem(unicode=unicode)
            self.iconLoc.vsParse(byts[offset:])
            offset += len(self.iconLoc)

        # ExtraData
        while True:
            if offset >= len(byts) - 3:
                break

            size = v_uint32()
            size.vsParse(byts[offset:])
            if size < 0x4:
                # Terminal "block"
                offset += 4
                break

            item = ExtraDataBlock()
            item.vsParse(byts[offset:])
            if item.blocksig == ExtraDataSigs.PropertyStore:
                # The spec doesn't mention this at all, but this isn't a SerializedPropertyStore
                # it's a seriesi of SerializedPropertyStorage (yes those are different) structures
                # and you know to stop when the last has a size of 0, like a few of the other structures
                # in this LNK file
                try:
                    propStore = vstruct.VArray()
                    step = len(item)
                    while True:
                        ps = PropertyStorage()
                        ps.vsParse(byts[offset+step:])
                        propStore.vsAddElement(ps)
                        step += ps.size
                        if ps.size == 0:
                            break
                    self.propStore = propStore
                except Exception as exc:
                    logger.warning('PropertyStore failed to parse: %r', exc)
                offset += item.blocksize
                # offset += self.propStore.size + 8  # This gets us to some kinda alignment I think?
                continue
            elif item.blocksig == ExtraDataSigs.VistaAndAboveIDList:
                self.vistaIDList, offset = self._parseItemID(byts, offset)
                continue
            elif item.blocksig == ExtraDataSigs.Console:
                self.console = block = ConsoleBlock()
            elif item.blocksig == ExtraDataSigs.ConsoleFE:
                self.consolefe = block = ConsoleFEBlock()
            elif item.blocksig == ExtraDataSigs.Darwin:
                self.darwin = block = TargetBlock()
            elif item.blocksig == ExtraDataSigs.Environment:
                self.envVar = block = TargetBlock()
            elif item.blocksig == ExtraDataSigs.IconEnvironment:
                self.iconEnvData = block = TargetBlock()
            elif item.blocksig == ExtraDataSigs.KnownFolder:
                self.knownFolder = block = FolderBlock()
            elif item.blocksig == ExtraDataSigs.Shim:
                self.shimData = block = ShimBlock()
            elif item.blocksig == ExtraDataSigs.SpecialFolder:
                self.specialFolder = block = FolderBlock()
            elif item.blocksig == ExtraDataSigs.Tracker:
                self.trackerData = block = TrackerBlock()
            else:
                # More malicious ones will stash things here that aren't valid blocks, so
                # we can't really go any further if the block is invalid
                logger.warning(f'Unhandled ExtraData with Signature {hex(item.blocksig)} of size {item.blocksize}')
                offset += item.blocksize
                continue

            block.vsParse(byts[offset:])
            offset += item.blocksize

        if offset < len(byts):
            self.leftovers = byts[offset:]

    def _parseItemID(self, byts, offset):
        items = []
        idlistsize = v_uint16()
        idlistsize.vsParse(byts[offset:])
        offset += len(idlistsize)

        while True:
            base = ItemBase()
            base.vsParse(byts[offset:])

            size = base.size
            iden = base.iden
            if size == 0:
                offset += 2
                break
            elif iden == 0x1f:
                item = RootFolderItem()
                item.vsParse(byts[offset:])
                offset += item.size
            elif iden & 0x70 == 0x20:
                item = VolumeItem()
                item.vsParse(byts[offset:])
                offset += item.size
            elif iden & 0x70 == 0x30:
                item = FileEntryItem()
                item.vsParse(byts[offset:])
                offset += item.size
            else:
                logger.warning(f'ItemID: Got unhandled iden of {hex(iden)}?')
                offset += size
                continue

            items.append(item)

        return items, offset


def parseFromBytes(byts):
    return Lnk(byts)


if __name__ == '__main__':
    import sys
    with open(sys.argv[1], 'rb') as fd:
        parseFromBytes(fd.read())
