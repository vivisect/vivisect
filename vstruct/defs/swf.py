import zlib

from vstruct import VStruct,VArray
from vstruct.bitfield import *
from vstruct.primitives import *

'''
0 End
1 ShowFrame
2 DefineShape
4 PlaceObject
5 RemoveObject
6 DefineBits
7 DefineButton
8 JPEGTables
9 SetBackgroundColor
10 DefineFont
11 DefineText
12 DoAction
13 DefineFontInfo
14 DefineSound
15 StartSound
17 DefineButtonSound
18 SoundStreamHead
19 SoundStreamBlock
20 DefineBitsLossless
21 DefineBitsJPEG2
22 DefineShape2
23 DefineButtonCxform
24 Protect
26 PlaceObject2
28 RemoveObject2
32 DefineShape3
33 DefineText2
34 DefineButton2
35 DefineBitsJPEG3
36 DefineBitsLossless2
37 DefineEditText
39 DefineSprite
43 FrameLabel
45 SoundStreamHead2
46 DefineMorphShape
48 DefineFont2
56 ExportAssets
57 ImportAssets
58 EnableDebugger
59 DoInitAction
60 DefineVideoStream
61 VideoFrame
62 DefineFontInfo2
64 EnableDebugger2
65 ScriptLimits
66 SetTabIndex
69 FileAttributes
70 PlaceObject3
71 ImportAssets2
73 DefineFontAlignZones
74 CSMTextSettings
75 DefineFont3
76 SymbolClass
77 Metadata
78 DefineScalingGrid
82 DoABC
83 DefineShape4
84 DefineMorphShape2
86 DefineSceneAndFrameLabelData
87 DefineBinaryData
88 DefineFontName
89 StartSound2
90 DefineBitsJPEG4
91 DefineFont4
93 EnableTelemetry
'''

swftags = {
    0: 'End',
    1: 'ShowFrame',
    2: 'DefineShape',
    4: 'PlaceObject',
    5: 'RemoveObject',
    6: 'DefineBits',
    7: 'DefineButton',
    8: 'JPEGTables',
    9: 'SetBackgroundColor',
    10: 'DefineFont',
    11: 'DefineText',
    12: 'DoAction',
    13: 'DefineFontInfo',
    14: 'DefineSound',
    15: 'StartSound',
    17: 'DefineButtonSound',
    18: 'SoundStreamHead',
    19: 'SoundStreamBlock',
    20: 'DefineBitsLossless',
    21: 'DefineBitsJPEG2',
    22: 'DefineShape2',
    23: 'DefineButtonCxform',
    24: 'Protect',
    26: 'PlaceObject2',
    28: 'RemoveObject2',
    32: 'DefineShape3',
    33: 'DefineText2',
    34: 'DefineButton2',
    35: 'DefineBitsJPEG3',
    36: 'DefineBitsLossless2',
    37: 'DefineEditText',
    39: 'DefineSprite',
    41: 'SerialNumber',
    43: 'FrameLabel',
    45: 'SoundStreamHead2',
    46: 'DefineMorphShape',
    48: 'DefineFont2',
    56: 'ExportAssets',
    57: 'ImportAssets',
    58: 'EnableDebugger',
    59: 'DoInitAction',
    60: 'DefineVideoStream',
    61: 'VideoFrame',
    62: 'DefineFontInfo2',
    64: 'EnableDebugger2',
    65: 'ScriptLimits',
    66: 'SetTabIndex',
    69: 'FileAttributes',
    70: 'PlaceObject3',
    71: 'ImportAssets2',
    73: 'DefineFontAlignZones',
    74: 'CSMTextSettings',
    75: 'DefineFont3',
    76: 'SymbolClass',
    77: 'Metadata',
    78: 'DefineScalingGrid',
    82: 'DoABC',
    83: 'DefineShape4',
    84: 'DefineMorphShape2',
    86: 'DefineSceneAndFrameLabelData',
    87: 'DefineBinaryData',
    88: 'DefineFontName',
    89: 'StartSound2',
    90: 'DefineBitsJPEG4',
    91: 'DefineFont4',
    93: 'EnableTelemetry',
}


class RECT(VBitField):
    def __init__(self):
        VBitField.__init__(self)
        self.Nbits = v_bits(5)
        self.Xmin = v_bits(1)
        self.Xmax = v_bits(1)
        self.Ymin = v_bits(1)
        self.Ymax = v_bits(1)

    def pcb_Nbits(self):
        bitwidth = self.Nbits
        self['Xmin'].vsSetBitWidth(bitwidth)
        self['Xmax'].vsSetBitWidth(bitwidth)
        self['Ymin'].vsSetBitWidth(bitwidth)
        self['Ymax'].vsSetBitWidth(bitwidth)

class EncodedU32(v_number):

    def __init__(self):
        v_number.__init__(self)
        self._vs_fmt = None # to prevent misuse

    def vsParse(self, bytez, offset=0):
        self._vs_value = 0
        # this shit is *not* my fault... ;)
        for i in range(5):
            b = ord(bytez[offset + i])
            self._vs_value |= (b & 0x7f) << (7 * i)
            if not b & 0x80:
                break
        self._vs_length = i + 1
        return offset + self._vs_length

    def vsEmit(self):
        raise Exception('swf.EncodedU32() needs vsEmit!')

    def __repr__(self):
        return 'U32: %d' % self.vsGetValue()


class RGB(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.Red    = v_uint8()
        self.Green  = v_uint8()
        self.Blue   = v_uint8()

class RGBA(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.Red    = v_uint8()
        self.Green  = v_uint8()
        self.Blue   = v_uint8()
        self.Alpha  = v_uint8()

class MATRIX(VBitField):
    def __init__(self):
        VBitField.__init__(self)
        self.HasScale = v_bits(1)
        self.NScaleBits  = v_bits(5)
        self.ScaleX      = v_bits(1)
        self.ScaleY      = v_bits(1)
        self.HasRotate   = v_bits(1)
        self.NRotateBits = v_bits(5)
        self.RotateSkew0 = v_bits(1)
        self.RotateSkew1 = v_bits(1)
        self.NTransBits  = v_bits(5)
        self.TranslateX  = v_bits(1)
        self.TranslateY  = v_bits(1)

    def pcb_HasScale(self):
        if not self.HasScale:
            self.vsDelField('NScaleBits')
            self.vsDelField('ScaleX')
            self.vsDelField('ScaleY')

    def pcb_NScaleBits(self):
        bitwidth = self.NScaleBits
        self['ScaleX'].vsSetBitWidth(bitwidth)
        self['ScaleY'].vsSetBitWidth(bitwidth)

    def pcb_HasRotate(self):
        if not self.HasRotate:
            self.vsDelField('NRotateBits')
            self.vsDelField('RotateSkew0')
            self.vsDelField('RotateSkew1')

    def pcb_NRotateBits(self):
        bitwidth = self.NRotateBits
        self['RotateSkew0'].vsSetBitWidth(bitwidth)
        self['RotateSkew1'].vsSetBitWidth(bitwidth)

    def pcb_NTransBits(self):
        bitwidth = self.NTransBits
        self['TranslateX'].vsSetBitWidth(bitwidth)
        self['TranslateY'].vsSetBitWidth(bitwidth)

class GRADRECORD(VStruct):
    def __init__(self,shape=1):
        VStruct.__init__(self)
        self.Ratio  = v_uint8()
        if shape <= 2:
            self.Color = RGB()
        else:
            self.Color = RGBA()

class GRADIENT(VStruct):
    def __init__(self,shape=1):
        VStruct.__init__(self)
        self._swf_shape = shape
        self.BitFields       = VBitField()
        self.BitFields.SpreadMode           = v_bits(2)
        self.BitFields.InterpolationMode    = v_bits(2)
        self.BitFields.NumGradients         = v_bits(4)
        self.GradientRecords = VArray()

    def pcb_BitFields(self):
        gcount = self.BitFields.NumGradients
        for i in range(gcount):
            g = GRADRECORD(shape=self._swf_shape)
            self.GradientRecords.vsAddElement(g)

class FOCALGRADIENT(GRADIENT):
    def __init__(self,shape=4):
        GRADIENT.__init__(self)
        self.FocalPoint = FIXED8()

FILL_SOLID              = 0x00
FILL_LINEAR_GRADIENT    = 0x10
FILL_RADIAL_GRADIENT    = 0x12
FILL_FOCAL_GRADIENT     = 0x13
FILL_BITMAP_REPEAT      = 0x40
FILL_BITMAP_CLIPPED     = 0x41
FILL_BITMAP_NSMOOTH_REP = 0x42
FILL_BITMAP_NSMOOTH_CLP = 0x43

class FILLSTYLE(VStruct):
    def __init__(self, shape=1):
        VStruct.__init__(self)
        self._swf_shape = shape
        self.FillStyleType      = v_uint8()
        self.Color              = RGB()
        self.GradientMatrix     = MATRIX()
        self.Gradient           = GRADIENT(shape=shape)
        self.BitmapId           = v_uint16()
        self.BitmapMatrix       = MATRIX()

    def pcb_FillStyleType(self):
        fstype = self.FillStyleType
        if fstype != 0x00:
            self.vsDelField('Color')

        if fstype not in (0x10, 0x12, 0x13):
            self.vsDelField('GradientMatrix')
            self.vsDelField('Gradient')
        else:
            if fstype == 0x13:
                self.Gradient = FOCALGRADIENT()

        if fstype not in (0x40,0x41,0x42,0x43):
            self.vsDelField('BitmapId')
            self.vsDelField('BitmapMatrix')

class FILLSTYLEARRAY(VStruct):
    def __init__(self, shape=1):
        VStruct.__init__(self)
        self._swf_shape = shape
        self.FillStyleCount     = v_uint8()
        self.FillStyleCountEx   = v_uint16()
        self.FillStyles         = VArray()

    def pcb_FillStyleCount(self):
        if self.FillStyleCount != 0xff:
            self.vsDelField('FillStyleCountEx')
            self.swfAddFillStyles(self.FillStyleCount)

    def pcb_FillStyleCountEx(self):
        self.swfAddFillStyles(self.FillStyleCountEx)

    def swfAddFillStyles(self, count):
        for i in range(count):
            elem = FILLSTYLE(shape=self._swf_shape)
            self.FillStyles.vsAddElement(elem)

class LINESTYLE(VStruct):
    def __init__(self,shape=1):
        VStruct.__init__(self)
        self._swf_shape = shape
        self.Width  = v_uint16()
        colorcls = RGB
        if shape >= 3:
            colorcls = RGBA
        self.Color = colorcls()

class LINESTYLEARRAY(VStruct):
    def __init__(self,shape=1):
        VStruct.__init__(self)
        self._swf_shape = 1
        self.LineStyleCount     = v_uint8()
        self.LineStyleCountEx   = v_uint16()
        self.LineStyles         = VArray()

    def pcb_LineStyleCount(self):
        if self.LineStyleCount != 0xff:
            self.vsDelField('LineStyleCountEx')
            self.swfAddLineStyles(self.LineStyleCount)

    def pcb_LineStyleCountEx(self):
        self.swfAddLineStyles(self.LineStyleCountEx)

    def swfAddLineStyles(self, count):
        for i in range(count):
            elem = LINESTYLE(shape=self._swf_shape)
            self.LineStyles.vsAddElement(elem)

class SHAPEWITHSTYLE(VStruct):
    def __init__(self, shape=1):
        VStruct.__init__(self)
        self.FillStyles     = FILLSTYLEARRAY(shape=shape)
        self.LineStyles     = LINESTYLEARRAY(shape=shape)
        self.NumBits        = VBitField()
        self.NumBits.NumFillBits    = v_bits(4)
        self.NumBits.NumLineBits    = v_bits(4)
        self.ShapeRecords           = VArray()

class SwfColorTransform(VBitField):
    def __init__(self):
        VBitField.__init__(self)
        self.HasAddTerms    = v_bits(1)
        self.HasMultTerms   = v_bits(1)
        self.Nbits          = v_bits(4)
        self.RedMultTerm    = v_bits(1)
        self.GreenMultTerm  = v_bits(1)
        self.BlueMultTerm   = v_bits(1)
        self.RedAddTerm     = v_bits(1)
        self.GreenAddTerm   = v_bits(1)
        self.BlueAddTerm    = v_bits(1)

    def pcb_Nbits(self):
        bitwidth = self.Nbits

        if not self.HasAddTerms:
            self.vsDelField('RedAddTerm')
            self.vsDelField('GreenAddTerm')
            self.vsDelField('BlueAddTerm')
        else:
            self['RedAddTerm'].vsSetBitWidth(bitwidth)
            self['GreenAddTerm'].vsSetBitWidth(bitwidth)
            self['BlueAddTerm'].vsSetBitWidth(bitwidth)

        if not self.HasMultTerms:
            self.vsDelField('RedMultTerm')
            self.vsDelField('GreenMultTerm')
            self.vsDelField('BlueMultTerm')
        else:
            self['RedMultTerm'].vsSetBitWidth(bitwidth)
            self['GreenMultTerm'].vsSetBitWidth(bitwidth)
            self['BlueMultTerm'].vsSetBitWidth(bitwidth)

class SwfTagCodeLength(VBitField):
    def __init__(self):
        VBitField.__init__(self)
        self.TagCode = v_bits(10)
        self.TagLength = v_bits(6)

class SwfTagHeader(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.TagCodeAndLength = v_uint16()
        self.OptionalLength   = v_uint32()

    def __repr__(self):
        tagcode = self.getSwfTagCode()
        taglen = self.getSwfTagLength()
        tagname = swftags.get(tagcode,'Unknown')
        return '%s (%d)' % (tagname,taglen)

    def pcb_TagCodeAndLength(self):
        if self.TagCodeAndLength & 0x3f != 0x3f:
            self.vsDelField('OptionalLength')

    def getSwfTagCode(self):
        return self.TagCodeAndLength >> 6

    def getSwfTagLength(self):
        taglen = self.TagCodeAndLength & 0x3f
        if taglen == 0x3f:
            taglen = self.OptionalLength
        return taglen

class PlaceObject(VStruct):
    def __init__(self, size):
        VStruct.__init__(self)
        self.CharacterId    = v_uint16()
        self.Depth          = v_uint16()
        self.Matrix         = MATRIX()
        self.ColorTransform = SwfColorTransform()

        self._swf_tagsize = size

    def vsParse(self, bytez, offset=0):
        # we *only* do this this way because we dont know
        # how big the Matrix field is until we parse it...
        offset = self['CharacterId'].vsParse(bytez,offset=offset)
        offset = self['Depth'].vsParse(bytez,offset=offset)
        offset = self['Matrix'].vsParse(bytez,offset=offset)
        if offset >= self._swf_tagsize:
            self.vsDelField('ColorTransform')
        else:
            offset = self['ColorTransform'].vsParse(bytez,offset=offset)
        return offset

class FileAttributes(VBitField):
    def __init__(self, size):
        VBitField.__init__(self)
        self.Reserved0      = v_bits(1)
        self.UseDirectBlit  = v_bits(1)
        self.UseGPU         = v_bits(1)
        self.HasMetadata    = v_bits(1)
        self.ActionScript3  = v_bits(1)
        self.Reserved1      = v_bits(2)
        self.UseNetwork     = v_bits(1)
        self.ReservedEnd    = v_bits(24)

class SetBackgroundColor(VStruct):
    def __init__(self, size):
        VStruct.__init__(self)
        self.BackgroundColor = RGB()

class OffsetName(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.Offset     = EncodedU32()
        self.Name       = v_zstr()

class DefineSceneAndFrameLabelData(VStruct):
    def __init__(self, size):
        VStruct.__init__(self)
        self.SceneCount         = EncodedU32()
        self.Scenes             = VArray()
        self.FrameLabelCount    = EncodedU32()
        self.Frames             = VArray()

    def pcb_SceneCount(self):
        count = self.SceneCount
        self.Scenes.vsAddElements(count, OffsetName)

    def pcb_FrameLabelCount(self):
        count = self.FrameLabelCount
        self.Scenes.vsAddElements(count, OffsetName)

class DefineShape4(VStruct):
    def __init__(self, size):
        VStruct.__init__(self)
        self.ShapeId        = v_uint16()
        self.ShapeBounds    = RECT()
        self.EdgeBounds     = RECT()
        self.ShapeFlags     = VBitField()
        self.Shapes         = SHAPEWITHSTYLE(shape=4)

        self.ShapeFlags.Reserved                = v_bits(5)
        self.ShapeFlags.UsesFillWindingRule     = v_bits(1)
        self.ShapeFlags.UsesNonScalingStrokes   = v_bits(1)
        self.ShapeFlags.UsesScalingStrokes      = v_bits(1)

class SwfTag(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.TagHeader = SwfTagHeader()
        self.TagData = VStruct()

    def pcb_TagHeader(self):
        taglen = self.TagHeader.getSwfTagLength()
        tagcode = self.TagHeader.getSwfTagCode()
        tagname = swftags.get(tagcode,'UnknownTag')
        tagclass = globals().get(tagname,v_bytes)
        self.TagData = tagclass(taglen)

class SwfHeader(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.Signature  = v_str(3)
        self.Version    = v_uint8()
        self.FileLength = v_uint32()
        self.FrameSize  = RECT()
        self.FrameRate  = v_uint16()
        self.FrameCount = v_uint16()

class SwfFile(VStruct):

    def __init__(self):
        VStruct.__init__(self)
        self.Header = SwfHeader()
        self.Tags = VArray()

    def vsParse(self, bytez, offset=0):
        magic = bytez[offset:offset+3]
        if magic not in ('FWS','CWS','ZWS'):
            raise Exception('Invalid Swf Magic')

        if magic == 'CWS':
            bytez = bytez[:8] + zlib.decompress(bytez[8:])

        offset = self.Header.vsParse(bytez, offset=offset)
        i = 0
        while offset < len(bytez):
            swftag = SwfTag()
            offset = swftag.vsParse(bytez, offset=offset)
            self.Tags.vsAddElement(swftag)
            i += 1
            if i > 3:
                break
