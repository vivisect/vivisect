import vstruct
from vstruct.primitives import *

SIZEMAP = {
    2: v_uint16,
    4: v_uint32,
    8: v_uint64,
}

# all the length params are in bytes

class Module(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Generation = v_uint16()
        self.Name = SIZEMAP[slen]()
        self.Mvid = SIZEMAP[glen]()
        self.EncId = SIZEMAP[glen]()
        self.EncBaseId = SIZEMAP[glen]()


class TypeRef(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.ResolutionScope = SIZEMAP[cttlen]()
        self.Name = v_uint32()
        self.Namespace = v_uint32()


class TypeDef(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Flags = v_int32()
        self.Name = SIZEMAP[slen]()
        self.Namespace = SIZEMAP[slen]()
        self.Extends = SIZEMAP[cttlen]()
        self.FieldList = SIZEMAP[ridlen]()
        self.MethodList = SIZEMAP[ridlen]()


class FieldPtr(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Field = SIZEMAP[ridlen]()


class Field(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Flags = v_uint16()
        self.Name = SIZEMAP[slen]()
        self.Signature = SIZEMAP[blen]()


class MethodPtr(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Method = SIZEMAP[ridlen]()


class Method(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.RVA = v_uint32()
        self.ImplFlags = v_uint16()
        self.Flags = v_uint16()
        self.Name = SIZEMAP[slen]()
        self.Signature = SIZEMAP[blen]()
        self.ParamList = SIZEMAP[ridlen]()


class ParamPtr(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Param = self.SIZEMAP[ridlen]()


class Param(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Flags = v_uint16()
        self.Sequence = v_uint16()
        self.Name = SIZEMAP[slen]()


class InterfaceImpl(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Class = SIZEMAP[ridlen]()
        self.Interface = SIZEMAP[cttlen]()  # TODO: Another TypeDefOrRef


class MemberRef(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Class = SIZEMAP[cttlen]()  # TODO: MemberRefParent, cannot be typedef
        self.Name = SIZEMAP[slen]()
        self.Signature = SIZEMAP[blen]()


class Constant(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint8()
        self.Padding = v_uint8()
        self.Parent = SIZEMAP[cttlen]()  # HasConstant
        self.Value = SIZEMAP[blen]()


class CustomAttribute(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Parent = SIZEMAP[cttlen]()  # HasCustomAttribute
        self.Type = SIZEMAP[cttlen]()  # CustomAttributeType
        self.Value = SIZEMAP[blen]()


class FieldMarshal(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Parent = SIZEMAP[cttlen]()  # FieldMarshal
        self.NativeType = SIZEMAP[blen]()


class DeclSecurity(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Action = v_uint16()
        self.Parent = SIZEMAP[cttlen]()  # HasDeclSecurity
        self.PermissionSet = SIZEMAP[blen]()


class ClassLayout(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.PackingSize = v_uint16()
        self.ClassSize = v_uint32()
        self.Parent = SIZEMAP[ridlen]()


class FieldLayout(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.OffSet = v_uint32()
        self.Field = SIZEMAP[ridlen]()


class StandaloneSig(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Signature = SIZEMAP[blen]()


class EventMap(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Parent = SIZEMAP[ridlen]()
        self.EventList = SIZEMAP[ridlen]()


class EventPtr(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Event = SIZEMAP[ridlen]()


class Event(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.EventFlags = v_uint16()
        self.Name = SIZEMAP[slen]()
        self.EventType = SIZEMAP[cttlen]() # TypeDefOrRef


class PropertyMap(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Parent = SIZEMAP[ridlen]()
        self.PropertyList = SIZEMAP[ridlen]()


class PropertyPtr(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Property = SIZEMAP[ridlen]()


class Property(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.PropFlags = v_uint16()
        self.Name = SIZEMAP[slen]()
        self.Type = SIZEMAP[blen]()


class MethodSemantics(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Semantic = v_uint16()
        self.Method = SIZEMAP[ridlen]()
        self.Association = SIZEMAP[cttlen]()  # HasSemantics


class MethodImpl(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Class = SIZEMAP[ridlen]()
        self.MethodBody = SIZEMAP[cttlen]()  # MethodDefOrRef  # Overriding method
        self.MethodDeclaration = SIZEMAP[cttlen]()  # MethodDefOrRet  # overridden method


class ModuleRef(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Name = SIZEMAP[slen]()  # no longer than 512. enforce?


class TypeSpec(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Signature = SIZEMAP[blen]()


class ENCLog(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Token = v_uint32()
        self.FuncCode = v_uint32()


class ImplMap(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.MappingFlags = v_uint16()
        self.MemberForwarded = SIZEMAP[cttlen]()  # MemberForwarded
        self.ImportName = SIZEMAP[slen]()
        self.ImportScope = SIZEMAP[ridlen]()


class ENCMap(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Token = v_uint32()


class FieldRVA(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.RVA = v_uint32()
        self.Field = SIZEMAP[ridlen]()


class Assembly(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
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
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Processor = v_uint32()


class AssemblyOS(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.OSPlatformID = v_uint32()
        self.OSMajorVersion = v_uint32()
        self.OSMinorVersion = v_uint32()


class AssemblyRef(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
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
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Processor = v_uint32()
        self.AssemblyRef = SIZEMAP[ridlen]()


# TODO: Subclass AssemblyOS instead?
class AssemblyRefOS(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.OSPlatformID = v_uint32()
        self.OSMajorVersion = v_uint32()
        self.OSMinorVersion = v_uint32()
        self.AssemblyRef = SIZEMAP[ridlen]()


class File(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Flags = v_uint32()  # either 1 or 0, so why did they make this 32 bits?
        self.Name = SIZEMAP[slen]()
        self.HashValue = SIZEMAP[blen]()


class ExportedType(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Flags = v_uint32()
        self.TypeDefId = v_uint32()
        self.TypeName = SIZEMAP[slen]()
        self.TypeNameSpace = SIZEMAP[slen]()
        self.Implementation = SIZEMAP[cttlen]()  # Implementation(File, ExportedType, AssemblyRef)


class ManifestResource(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Offset = v_uint32()
        self.Flags = v_uint32()
        self.Name = SIZEMAP[slen]()
        self.Implementation = SIZEMAP[cttlen]()  # Implementation (0, File, AssemblyRef)


class NestedClass(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Nested = SIZEMAP[ridlen]
        self.Enclosing = SIZEMAP[ridlen]()


class GenericParam(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Number = v_uint16()
        self.Flags = v_uint16()
        self.Owner = SIZEMAP[cttlen]()  # TypeOrMethodDef
        self.Name = SIZEMAP[slen]()


class MethodSpec(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Method = SIZEMAP[cttlen]()  # MethodDefOrRef
        self.Instantiation = SIZEMAP[blen]()


class GenericParamConstraint(vstruct.VStruct):
    def __init__(self, ridlen=2, cttlen=2, slen=2, glen=2, blen=2):
        vstruct.VStruct.__init__(self)
        self.Owner = SIZEMAP[ridlen]()
        self.Constraint = SIZEMAP[cttlen]()  # TypeDefOrRef
