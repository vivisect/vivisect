import vstruct
from vstruct.primitives import *

RIDMAP = {
    1: v_uint8,
    2: v_uint16,
    4: v_uint32,
}

OFFMAP = {
    0: v_uint16,
    1:  v_uint32,
}

class Module(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self, ridlen=2, offlen=0)
        self.Generation = v_uint16()
        self.Name = OFFMAP[offlen]()
        self.Mvid = OFFMAP[offlen]()
        self.EncId = OFFMAP[offlen]()
        self.EncBaseId = OFFMAP[offlen]()


class TypeRef(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        vstruct.VStruct.__init__(self)
        self.ResolutionScope = None  # TODO: A coded token type
        self.Name = v_uint32()
        self.Namespace = v_uint32()


class TypeDef(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.Flags = v_int32()
        self.Name = OFFMAP[offlen]()
        self.Namespace = OFFMAP[offlen]()
        self.Extends = None  # TODO: TypedefOrRef, how do we model that?
        self.FieldList = RIDMAP[ridlen]()
        self.MethodList = RIDMAP[ridlen]()


class FieldPtr(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.Field = RIDMAP[ridlen]()


class Field(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.Flags = v_uint16()
        self.Name = OFFMAP[offlen]()
        self.Signature = OFFMAP[offlen]()


class MethodPtr(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.Method = RIDMAP[ridlen]()


class Method(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.RVA = v_uint32()
        self.ImplFlags = v_uint16()
        self.Flags = v_uint16()
        self.Name = OFFMAP[offlen]()
        self.Signature = OFFMAP[offlen]()
        self.ParamList = RIDMAP[ridlen]()


class ParamPtr(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.Param = self.RIDMAP[ridlen]()


class Param(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.Flags = v_uint16()
        self.Sequence = v_uint16()
        self.Name = OFFMAP[offlen]()


class InterfaceImpl(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.Class = RIDMAP[ridlen]()
        self.Interface = None  # TODO: Another TypeDefOrRef


class MemberRef(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.Class = None  # TODO: MemberRefParent, cannot be typedef
        self.Name = OFFMAP[offlen]()
        self.Signature = OFFMAP[offlen]()


class Constant(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.Type = v_uint8()
        self.Parent = None  # TODO: HasConstant
        self.Value = OFFMAP[offlen]()


class CustomAttribute(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.Parent = None  # TODO: HashCustomAttribute
        self.Type = None  # TODO: CustomAttributeType
        self.Value = OFFMAP[offlen]()


class FieldMarshal(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.Parent = None  # TODO: FieldMarshal
        self.NativeType = OFFMAP[offlen]()


class DeclSecurity(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.Action = v_uint16()
        self.Parent = None  # TODO: HasDeclSecurity
        self.PermissionSet = OFFMAP[offlen]()


class ClassLayout(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.PackingSize = v_uint16()
        self.ClassSize = v_uint32()
        self.Parent = RIDMAP[ridlen]()


class FieldLayout(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.OffSet = v_uint32()
        self.Field = RIDMAP[ridlen]()


class StandaloneSig(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.Signature = OFFMAP[offlen]()


class EventMap(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.Parent = RIDMAP[ridlen]()
        self.EventList = RIDMAP[ridlen]()


class EventPtr(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.Event = RIDMAP[ridlen]()


class Event(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.EventFlags = v_uint16()
        self.Name = OFFMAP[offlen]()
        self.EventType = None  # TODO: TypeDefOrRef


class PropertyMap(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.Parent = RIDMAP[ridlen]()
        self.PropertyList = RIDMAP[ridlen]()


class PropertyPtr(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.Property = RIDMAP[ridlen]()


class Property(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.PropFlags = v_uint16()
        self.Name = OFFMAP[offlen]()
        self.Type = OFFMAP[offlen]()


class MethodSemantics(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.Semantic = v_uint16()
        self.Method = RIDMAP[ridlen]()
        self.Association = None  # TODO: HasSemantics


class MethodImpl(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.Class = RIDMAP[ridlen]()
        self.MethodBody = None  # TODO: MethodDefOrRef  # Overriding method
        self.MethodDeclaration = None  # TODO: MethodDefOrRet  # overridden method


class ModuleRef(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.Name = OFFMAP[offlen]()  # no longer than 512. enforce?


class TypeSpec(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.Signature = OFFMAP[offlen]()

class ENCLog(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.Token = v_uint32()
        self.FuncCode = v_uint32()


class ImplMap(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.MappingFlags = v_uint16()
        self.MemberForwarded = None  # TODO: MemberForwarded?
        self.ImportName = OFFMAP[offlen]()
        self.ImportScope = RIDMAP[ridlen]()


class ENCMap(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.Token = v_uint32()


class FieldRVA(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.RVA = v_uint32()
        self.Field = RIDMAP[ridlen]


class Assembly(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.HashAlgId = v_uint32()
        self.MajorVersion = v_uint16()
        self.MinorVersion = v_uint16()
        self.BuildNumber= v_uint16()
        self.RevisionNumber = v_uint16()
        self.Flags = v_uint32()
        self.PublicKey = OFFMAP[offlen]()
        self.Name = OFFMAP[offlen]()
        self.Locale = OFFMAP[offlen]()


class AssemblyProcessor(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.Processor = v_uint32()


class AssemblyOS(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.OSPlatformID = v_uint32()
        self.OSMajorVersion = v_uint32()
        self.OSMinorVersion = v_uint32()


class AssemblyRef(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.MajorVersion = v_uint16()
        self.MinorVersion = v_uint16()
        self.BuildNumber= v_uint16()
        self.RevisionNumber = v_uint16()
        self.Flags = v_uint32()
        self.PublicKeyOrToken = OFFMAP[offlen]()
        self.Name = OFFMAP[offlen]()
        self.Locale = OFFMAP[offlen]()
        self.HashValue = OFFMAP[offlen]()


class AssemblyRefProcessor(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.Processor = v_uint32()
        self.AssemblyRef = RIDMAP[ridlen]()


# TODO: Subclass AssemblyOS instead?
class AssemblyRefOS(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.OSPlatformID = v_uint32()
        self.OSMajorVersion = v_uint32()
        self.OSMinorVersion = v_uint32()
        self.AssemblyRef = RIDMAP[ridlen]()


class File(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.Flags = v_uint32()  # either 1 or 0, so why did they make this 32 bits?
        self.Name = OFFMAP[offlen]()
        self.HashValue = OFFMAP[offlen]()


class ExportedType(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.Flags = v_uint32()
        self.TypeDefId = v_uint32()
        self.TypeName = OFFMAP[offlen]()
        self.TypeNameSpace = OFFMAP[offlen]()
        self.Implementation = None  # TODO: Implementation(File, ExportedType, AssemblyRef)


class ManifestResource(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.Offset = v_uint32()
        self.Flags = v_uint32()
        self.Name = OFFMAP[offlen]()
        self.Implementation = None  # TODO: Implementation (0, File, AssemblyRef)


class NestedClass(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.Nested = RIDMAP[ridlen]
        self.Enclosing = RIDMAP[ridlen]


class GenericParam(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.Number = v_uint16()
        self.Flags = v_uint16()
        self.Owner = None  # TODO: TypeOrMethodDef
        self.Name = OFFMAP[offlen]


class MethodSpec(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.Method = None  # MethodDefOrRef
        self.Instantiation = OFFMAP[offlen]


class GenericParamConstraint(vstruct.VStruct):
    def __init__(self, ridlen=2, offlen=0):
        self.Owner = RIDMAP[ridlen]
        self.Constraint = None  # TODO: TypeDefOrRef
