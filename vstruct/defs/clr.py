import enum

import vstruct
from vstruct.primitives import *

SIZEMAP = {
    2: v_uint16,
    4: v_uint32,
    8: v_uint64,
}

# Soooo.technically there's a few of these that aren't TokenTypes, but are just Types,
# but the numbers line up either way, so screw 'em
class Types(enum.Enum):
    Module = 0
    TypeRef = 1
    TypeDef = 2
    FieldPtr = 3
    Field = 4
    MethodPtr = 5
    Method = 6
    ParamPtr = 7
    Param = 8
    InterfaceImpl = 9
    MemberRef = 10
    Constant = 11
    CustomAttribute = 12
    FieldMarshal = 13
    DeclSecurity = 14
    ClassLayout = 15
    FieldLayout = 16
    StandaloneSig = 17
    EventMap = 18
    EventPtr = 19
    Event = 20
    PropertyMap = 21
    PropertyPtr = 22
    Property = 23
    MethodSemantics = 24
    MethodImp = 25
    ModuleRef = 26
    TypeSpec = 27
    ImplMap = 28
    FieldRVA = 29
    ENCLog = 30
    ENCMap = 31
    Assembly = 32
    AssemblyProcessor = 33
    AssemblyOS = 34
    AssemblyRef = 35
    AssemblyRefProcessor = 36
    AssemblyRefOS = 37
    File = 38
    ExportedType = 39
    ManifestResource = 40
    NestedClass = 41
    GenericParam = 42
    MethodSpec = 43
    GenericParamConstraint = 44


class CodedTokenTypes(enum.Enum):
    TypeDefOrRef = 64
    HasConstant = 65
    HasCustomAttribute = 66
    HasFieldMarshal = 67
    HasDeclSecurity = 68
    MemberRefParent = 69
    HasSemantics = 70
    MethodDefOrRef = 71
    MemberForwarded = 72
    Implementation = 73
    CustomAttributeType = 74
    ResolutionScope = 75
    TypeOrMethodDef = 76


CodedTokenTypeMap = {
    CodedTokenTypes.TypeDefOrRef: [Types.TypeDef, Types.TypeRef, Types.TypeSpec],
    CodedTokenTypes.HasConstant: [Types.Field, Types.Param, Types.Property],
    CodedTokenTypes.HasCustomAttribute: [
        Types.Method, Types.Field, Types.TypeRef, Types.TypeDef, Types.Param,
        Types.InterfaceImpl, Types.MemberRef, Types.Module, Types.DeclSecurity, Types.Property,
        Types.Event, Types.StandaloneSig, Types.ModuleRef, Types.TypeSpec, Types.Assembly,
        Types.AssemblyRef, Types.File, Types.ExportedType, Types.ManifestResource,
        Types.GenericParam, Types.GenericParamConstraint, Types.MethodSpec
    ],
    CodedTokenTypes.HasFieldMarshal: [Types.Field, Types.Param],
    CodedTokenTypes.HasDeclSecurity: [Types.TypeDef, Types.Method, Types.Assembly],
    CodedTokenTypes.MemberRefParent: [
        Types.TypeDef, Types.TypeRef, Types.ModuleRef, Types.Method, Types.MethodSpec
    ],
    CodedTokenTypes.HasSemantics: [Types.Event, Types.Property],
    CodedTokenTypes.MethodDefOrRef: [Types.Method, Types.MemberRef],
    CodedTokenTypes.MemberForwarded: [Types.Field, Types.Method],
    CodedTokenTypes.Implementation: [Types.File, Types.AssemblyRef, Types.ExportedType],
    CodedTokenTypes.CustomAttributeType: [
        None, None, Types.Method, Types.MemberRef, None,
        # the ones marked none must not be used
    ],
    CodedTokenTypes.ResolutionScope: [
        Types.Module, Types.ModuleRef, Types.AssemblyRef, Types.TypeRef
    ],
    CodedTokenTypes.TypeOrMethodDef: [Types.TypeDef, Types.Method],
}

def cttBitLen(base, idx):
    return base + len(bin(len(CodedTokenTypeMap[idx]))[2:])


class Module(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Generation = v_uint16()
        self.Name = SIZEMAP[slen]()
        self.Mvid = SIZEMAP[glen]()
        self.EncId = SIZEMAP[glen]()
        self.EncBaseId = SIZEMAP[glen]()


class TypeRef(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        cttlen = cttBitLen(cttbase, CodedTokenTypes.ResolutionScope)
        self.ResolutionScope = v_uint32() if cttlen > 16 else v_uint16()
        self.Name = v_uint32()
        self.Namespace = v_uint32()


class TypeDef(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Flags = v_int32()
        self.Name = SIZEMAP[slen]()
        self.Namespace = SIZEMAP[slen]()
        cttlen = cttBitLen(cttbase, CodedTokenTypes.TypeDefOrRef)
        self.Extends = v_uint32() if cttlen > 16 else v_uint16()
        self.FieldList = SIZEMAP[ridlen]()
        self.MethodList = SIZEMAP[ridlen]()


class FieldPtr(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Field = SIZEMAP[ridlen]()


class Field(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Flags = v_uint16()
        self.Name = SIZEMAP[slen]()
        self.Signature = SIZEMAP[blen]()


class MethodPtr(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Method = SIZEMAP[ridlen]()


class Method(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.RVA = v_uint32()
        self.ImplFlags = v_uint16()
        self.Flags = v_uint16()
        self.Name = SIZEMAP[slen]()
        self.Signature = SIZEMAP[blen]()
        self.ParamList = SIZEMAP[ridlen]()


class ParamPtr(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Param = self.SIZEMAP[ridlen]()


class Param(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Flags = v_uint16()
        self.Sequence = v_uint16()
        self.Name = SIZEMAP[slen]()


class InterfaceImpl(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Class = SIZEMAP[ridlen]()
        cttlen = cttBitLen(cttbase, CodedTokenTypes.TypeDefOrRef)
        self.Interface = v_uint32() if cttlen > 16 else v_uint16()


class MemberRef(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        cttlen = cttBitLen(cttbase, CodedTokenTypes.MemberRefParent)
        self.Class = v_uint32() if cttlen > 16 else v_uint16()
        self.Name = SIZEMAP[slen]()
        self.Signature = SIZEMAP[blen]()


class Constant(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint8()
        self.Padding = v_uint8()
        cttlen = cttBitLen(cttbase, CodedTokenTypes.HasConstant)
        self.Parent = v_uint32() if cttlen > 16 else v_uint16()
        self.Value = SIZEMAP[blen]()


class CustomAttribute(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        cttlen = cttBitLen(cttbase, CodedTokenTypes.HasCustomAttribute)
        self.Parent = v_uint32() if cttlen > 16 else v_uint16()
        cttlen = cttBitLen(cttbase, CodedTokenTypes.CustomAttributeType)
        self.Type = v_uint32() if cttlen > 16 else v_uint16()
        self.Value = SIZEMAP[blen]()


class FieldMarshal(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        cttlen = cttBitLen(cttbase, CodedTokenTypes.HasFieldMarshal)
        self.Parent = v_uint32() if cttlen > 16 else v_uint16()
        self.NativeType = SIZEMAP[blen]()


class DeclSecurity(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Action = v_uint16()
        cttlen = cttBitLen(cttbase, CodedTokenTypes.HasDeclSecurity)
        self.Parent = v_uint32() if cttlen > 16 else v_uint16()
        self.PermissionSet = SIZEMAP[blen]()


class ClassLayout(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.PackingSize = v_uint16()
        self.ClassSize = v_uint32()
        self.Parent = SIZEMAP[ridlen]()


class FieldLayout(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.OffSet = v_uint32()
        self.Field = SIZEMAP[ridlen]()


class StandaloneSig(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Signature = SIZEMAP[blen]()


class EventMap(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Parent = SIZEMAP[ridlen]()
        self.EventList = SIZEMAP[ridlen]()


class EventPtr(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Event = SIZEMAP[ridlen]()


class Event(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.EventFlags = v_uint16()
        self.Name = SIZEMAP[slen]()
        cttlen = cttBitLen(cttbase, CodedTokenTypes.TypeDefOrRef)
        self.EventType = v_uint32() if cttlen > 16 else v_uint16()


class PropertyMap(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Parent = SIZEMAP[ridlen]()
        self.PropertyList = SIZEMAP[ridlen]()


class PropertyPtr(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Property = SIZEMAP[ridlen]()


class Property(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.PropFlags = v_uint16()
        self.Name = SIZEMAP[slen]()
        self.Type = SIZEMAP[blen]()


class MethodSemantics(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Semantic = v_uint16()
        self.Method = SIZEMAP[ridlen]()
        cttlen = cttBitLen(cttbase, CodedTokenTypes.TypeDefOrRef)
        self.Association = v_uint32() if cttlen > 16 else v_uint16()


class MethodImpl(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Class = SIZEMAP[ridlen]()

        cttlen = cttBitLen(cttbase, CodedTokenTypes.MethodDefOrRef)
        self.MethodBody = v_uint32() if cttlen > 16 else v_uint16()
        cttlen = cttBitLen(cttbase, CodedTokenTypes.MethodDefOrRef)
        self.MethodDeclaration = v_uint32() if cttlen > 16 else v_uint16()


class ModuleRef(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Name = SIZEMAP[slen]()  # no longer than 512. enforce?


class TypeSpec(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Signature = SIZEMAP[blen]()


class ENCLog(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Token = v_uint32()
        self.FuncCode = v_uint32()


class ImplMap(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.MappingFlags = v_uint16()
        cttlen = cttBitLen(cttbase, CodedTokenTypes.MemberForwarded)
        self.MemberForwarded = v_uint32() if cttlen > 16 else v_uint16()
        self.ImportName = SIZEMAP[slen]()
        self.ImportScope = SIZEMAP[ridlen]()


class ENCMap(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Token = v_uint32()


class FieldRVA(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.RVA = v_uint32()
        self.Field = SIZEMAP[ridlen]()


class Assembly(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.HashAlgId = v_uint32()
        self.MajorVersion = v_uint16()
        self.MinorVersion = v_uint16()
        self.BuildNumber= v_uint16()
        self.RevisionNumber = v_uint16()
        self.Flags = v_uint32()
        self.PublicKey = SIZEMAP[blen]()
        self.Name = SIZEMAP[slen]()
        self.Locale = SIZEMAP[slen]()


class AssemblyProcessor(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Processor = v_uint32()


class AssemblyOS(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.OSPlatformID = v_uint32()
        self.OSMajorVersion = v_uint32()
        self.OSMinorVersion = v_uint32()


class AssemblyRef(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.MajorVersion = v_uint16()
        self.MinorVersion = v_uint16()
        self.BuildNumber= v_uint16()
        self.RevisionNumber = v_uint16()
        self.Flags = v_uint32()
        self.PublicKeyOrToken = SIZEMAP[blen]()
        self.Name = SIZEMAP[slen]()
        self.Locale = SIZEMAP[slen]()
        self.HashValue = SIZEMAP[blen]()


class AssemblyRefProcessor(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Processor = v_uint32()
        self.AssemblyRef = SIZEMAP[ridlen]()


# TODO: Subclass AssemblyOS instead?
class AssemblyRefOS(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.OSPlatformID = v_uint32()
        self.OSMajorVersion = v_uint32()
        self.OSMinorVersion = v_uint32()
        self.AssemblyRef = SIZEMAP[ridlen]()


class File(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Flags = v_uint32()  # either 1 or 0, so why did they make this 32 bits?
        self.Name = SIZEMAP[slen]()
        self.HashValue = SIZEMAP[blen]()


class ExportedType(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Flags = v_uint32()
        self.TypeDefId = v_uint32()
        self.TypeName = SIZEMAP[slen]()
        self.TypeNameSpace = SIZEMAP[slen]()
        cttlen = cttBitLen(cttbase, CodedTokenTypes.Implementation)
        self.Implementation = v_uint32() if cttlen > 16 else v_uint16()


class ManifestResource(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Offset = v_uint32()
        self.Flags = v_uint32()
        self.Name = SIZEMAP[slen]()
        cttlen = cttBitLen(cttbase, CodedTokenTypes.Implementation)
        self.Implementation = v_uint32() if cttlen > 16 else v_uint16()


class NestedClass(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Nested = SIZEMAP[ridlen]()
        self.Enclosing = SIZEMAP[ridlen]()


class GenericParam(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Number = v_uint16()
        self.Flags = v_uint16()
        cttlen = cttBitLen(cttbase, CodedTokenTypes.TypeOrMethodDef)
        self.Owner = v_uint32() if cttlen > 16 else v_uint16()
        self.Name = SIZEMAP[slen]()


class MethodSpec(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        cttlen = cttBitLen(cttbase, CodedTokenTypes.MethodDefOrRef)
        self.Method = v_uint32() if cttlen > 16 else v_uint16()
        self.Instantiation = SIZEMAP[blen]()


class GenericParamConstraint(vstruct.VStruct):
    def __init__(self, ridlen=2, cttbase=12, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Owner = SIZEMAP[ridlen]()
        cttlen = cttBitLen(cttbase, CodedTokenTypes.TypeDefOrRef)
        self.Constraint = v_uint32() if cttlen > 16 else v_uint16()
