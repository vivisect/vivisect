import vstruct
from vstruct.primitives import *

class Module(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self, ridlen=2)
        self.Generation = v_uint16()
        self.Name = v_uint32()
        self.Mvid = v_uint32()
        self.EncId = v_uint32()
        self.EncBaseId = v_uint32()


class TypeRef(vstruct.VStruct):
    def __init__(self, ridlen=2):
        vstruct.VStruct.__init__(self)
        self.ResolutionScope = None  # What the fuck is this supposed to be?
        self.Name = v_uint32()
        self.Namespace = v_uint32()


class TypeDef(vstruct.VStruct):
    def __init__(self, ridlen=2):
        self.Flags = 
        self.Name = 
        self.Namespace = 
        self.Extends = None# TypedefOrRef, how do we model that?
        self.FieldList = # rid
        self.MethodList = #rid


class FieldPtr(vstruct.VStruct):
    def __init__(self, ridlen=2):
        self.


class Field(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class MethodPtr(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class Method(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class ParamPtr(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class Param(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class InterfaceImpl(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class MemberRef(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class Constant(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class CustomAttribute(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class FieldMarshal(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class DeclSecurity(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class ClassLayout(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class FieldLayout(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class StandaloneSig(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class EventMap(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class EventPtr(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class Event(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class PropertyMap(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class PropertyPtr(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass

class Property(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class MethodSemantics(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class MethodImpl(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class ModuleRef(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass

class TypeSpec(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass

class ENCLog(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class ImplMap(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class ENCMap(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class FieldRVA(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class Assembly(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class AssemblyProcessor(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class AssemblyOS(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class AssemblyRef(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class AssemblyRefProcessor(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class AssemblyRefOS(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class File(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class ExportedType(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class ManifestResource(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class NestedClass(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class GenericParam(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class MethodSpec(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass


class GenericParamConstraint(vstruct.VStruct):
    def __init__(self, ridlen=2):
        pass
