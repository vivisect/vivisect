import vstruct
from vstruct.primitives import *

SIZEMAP = {
    1: v_uint8,
    2: v_uint16,
    4: v_uint32,
    8: v_uint64,
}


class Module(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self, ridlen=2, offlen=2, cttlen=2)
        self.Generation = v_uint16()
        self.Name = SIZEMAP[offlen]()
        self.Mvid = SIZEMAP[offlen]()
        self.EncId = SIZEMAP[offlen]()
        self.EncBaseId = SIZEMAP[offlen]()


class TypeRef(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        vstruct.VStruct.__init__(self)
        self.ResolutionScope = SIZEMAP[cttlen]()
        self.Name = v_uint32()
        self.Namespace = v_uint32()


class TypeDef(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.Flags = v_int32()
        self.Name = SIZEMAP[offlen]()
        self.Namespace = SIZEMAP[offlen]()
        self.Extends = SIZEMAP[cttlen]()
        self.FieldList = SIZEMAP[ridlen]()
        self.MethodList = SIZEMAP[ridlen]()


class FieldPtr(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.Field = SIZEMAP[ridlen]()


class Field(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.Flags = v_uint16()
        self.Name = SIZEMAP[offlen]()
        self.Signature = SIZEMAP[offlen]()


class MethodPtr(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.Method = SIZEMAP[ridlen]()


class Method(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.RVA = v_uint32()
        self.ImplFlags = v_uint16()
        self.Flags = v_uint16()
        self.Name = SIZEMAP[offlen]()
        self.Signature = SIZEMAP[offlen]()
        self.ParamList = SIZEMAP[ridlen]()


class ParamPtr(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.Param = self.SIZEMAP[ridlen]()


class Param(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.Flags = v_uint16()
        self.Sequence = v_uint16()
        self.Name = SIZEMAP[offlen]()


class InterfaceImpl(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.Class = SIZEMAP[ridlen]()
        self.Interface = SIZEMAP[cttlen]()  # TODO: Another TypeDefOrRef


class MemberRef(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.Class = SIZEMAP[cttlen]()  # TODO: MemberRefParent, cannot be typedef
        self.Name = SIZEMAP[offlen]()
        self.Signature = SIZEMAP[offlen]()


class Constant(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.Type = v_uint8()
        self.Parent = SIZEMAP[cttlen]()  # HasConstant
        self.Value = SIZEMAP[offlen]()


class CustomAttribute(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.Parent = SIZEMAP[cttlen]()  # HashCustomAttribute
        self.Type = SIZEMAP[cttlen]()  # CustomAttributeType
        self.Value = SIZEMAP[offlen]()


class FieldMarshal(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.Parent = SIZEMAP[cttlen]()  # FieldMarshal
        self.NativeType = SIZEMAP[offlen]()


class DeclSecurity(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.Action = v_uint16()
        self.Parent = SIZEMAP[cttlen]()  # HasDeclSecurity
        self.PermissionSet = SIZEMAP[offlen]()


class ClassLayout(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.PackingSize = v_uint16()
        self.ClassSize = v_uint32()
        self.Parent = SIZEMAP[ridlen]()


class FieldLayout(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.OffSet = v_uint32()
        self.Field = SIZEMAP[ridlen]()


class StandaloneSig(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.Signature = SIZEMAP[offlen]()


class EventMap(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.Parent = SIZEMAP[ridlen]()
        self.EventList = SIZEMAP[ridlen]()


class EventPtr(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.Event = SIZEMAP[ridlen]()


class Event(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.EventFlags = v_uint16()
        self.Name = SIZEMAP[offlen]()
        self.EventType = SIZEMAP[cttlen]() # TypeDefOrRef


class PropertyMap(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.Parent = SIZEMAP[ridlen]()
        self.PropertyList = SIZEMAP[ridlen]()


class PropertyPtr(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.Property = SIZEMAP[ridlen]()


class Property(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.PropFlags = v_uint16()
        self.Name = SIZEMAP[offlen]()
        self.Type = SIZEMAP[offlen]()


class MethodSemantics(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.Semantic = v_uint16()
        self.Method = SIZEMAP[ridlen]()
        self.Association = SIZEMAP[cttlen]()  # HasSemantics


class MethodImpl(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.Class = SIZEMAP[ridlen]()
        self.MethodBody = SIZEMAP[cttlen]()  # MethodDefOrRef  # Overriding method
        self.MethodDeclaration = SIZEMAP[cttlen]()  # MethodDefOrRet  # overridden method


class ModuleRef(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.Name = SIZEMAP[offlen]()  # no longer than 512. enforce?


class TypeSpec(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.Signature = SIZEMAP[offlen]()

class ENCLog(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.Token = v_uint32()
        self.FuncCode = v_uint32()


class ImplMap(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.MappingFlags = v_uint16()
        self.MemberForwarded = SIZEMAP[cttlen]()  # MemberForwarded
        self.ImportName = SIZEMAP[offlen]()
        self.ImportScope = SIZEMAP[ridlen]()


class ENCMap(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.Token = v_uint32()


class FieldRVA(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.RVA = v_uint32()
        self.Field = SIZEMAP[ridlen]()


class Assembly(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.HashAlgId = v_uint32()
        self.MajorVersion = v_uint16()
        self.MinorVersion = v_uint16()
        self.BuildNumber= v_uint16()
        self.RevisionNumber = v_uint16()
        self.Flags = v_uint32()
        self.PublicKey = SIZEMAP[offlen]()
        self.Name = SIZEMAP[offlen]()
        self.Locale = SIZEMAP[offlen]()


class AssemblyProcessor(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.Processor = v_uint32()


class AssemblyOS(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.OSPlatformID = v_uint32()
        self.OSMajorVersion = v_uint32()
        self.OSMinorVersion = v_uint32()


class AssemblyRef(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.MajorVersion = v_uint16()
        self.MinorVersion = v_uint16()
        self.BuildNumber= v_uint16()
        self.RevisionNumber = v_uint16()
        self.Flags = v_uint32()
        self.PublicKeyOrToken = SIZEMAP[offlen]()
        self.Name = SIZEMAP[offlen]()
        self.Locale = SIZEMAP[offlen]()
        self.HashValue = SIZEMAP[offlen]()


class AssemblyRefProcessor(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.Processor = v_uint32()
        self.AssemblyRef = SIZEMAP[ridlen]()


# TODO: Subclass AssemblyOS instead?
class AssemblyRefOS(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.OSPlatformID = v_uint32()
        self.OSMajorVersion = v_uint32()
        self.OSMinorVersion = v_uint32()
        self.AssemblyRef = SIZEMAP[ridlen]()


class File(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.Flags = v_uint32()  # either 1 or 0, so why did they make this 32 bits?
        self.Name = SIZEMAP[offlen]()
        self.HashValue = SIZEMAP[offlen]()


class ExportedType(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.Flags = v_uint32()
        self.TypeDefId = v_uint32()
        self.TypeName = SIZEMAP[offlen]()
        self.TypeNameSpace = SIZEMAP[offlen]()
        self.Implementation = SIZEMAP[cttlen]()  # Implementation(File, ExportedType, AssemblyRef)


class ManifestResource(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.Offset = v_uint32()
        self.Flags = v_uint32()
        self.Name = SIZEMAP[offlen]()
        self.Implementation = SIZEMAP[cttlen]()  # Implementation (0, File, AssemblyRef)


class NestedClass(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.Nested = SIZEMAP[ridlen]
        self.Enclosing = SIZEMAP[ridlen]()


class GenericParam(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.Number = v_uint16()
        self.Flags = v_uint16()
        self.Owner = SIZEMAP[cttlen]()  # TypeOrMethodDef
        self.Name = SIZEMAP[offlen]()


class MethodSpec(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.Method = SIZEMAP[cttlen]()  # MethodDefOrRef
        self.Instantiation = SIZEMAP[offlen]()


class GenericParamConstraint(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=2, cttlen=2):
        self.Owner = SIZEMAP[ridlen]()
        self.Constraint = SIZEMAP[cttlen]()  # TypeDefOrRef
