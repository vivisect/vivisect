"""
AST node classes for MSVC C++ demangling.

These nodes represent the parsed structure of a Microsoft Visual C++
mangled symbol.  The renderer converts them to demangled strings.
"""


# ---- Name nodes ----

class FragmentName:
    """A simple name fragment (e.g. 'foo' in ?foo@@YA...)."""
    __slots__ = ('name',)
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'FragmentName(%r)' % self.name


class SpecialName:
    """A special name: constructor, destructor, operator, RTTI, etc."""
    __slots__ = ('name', 'kind', 'is_ctor', 'is_dtor', 'is_operator', 'is_type_cast',
                 'rtti_number')
    def __init__(self, name, kind='special', is_ctor=False, is_dtor=False,
                 is_operator=False, is_type_cast=False, rtti_number=-1):
        self.name = name
        self.kind = kind
        self.is_ctor = is_ctor
        self.is_dtor = is_dtor
        self.is_operator = is_operator
        self.is_type_cast = is_type_cast
        self.rtti_number = rtti_number

    def __repr__(self):
        return 'SpecialName(%r, kind=%r)' % (self.name, self.kind)


class TemplateName:
    """A template name with arguments: ?$name@@..."""
    __slots__ = ('base_name', 'args')
    def __init__(self, base_name, args):
        self.base_name = base_name  # FragmentName or SpecialName
        self.args = args  # list of type strings

    def __repr__(self):
        return 'TemplateName(%r, args=%r)' % (self.base_name, self.args)


class QualifiedName:
    """A qualified name: scope chain + basic name."""
    __slots__ = ('scope', 'basic_name')
    def __init__(self, scope, basic_name):
        self.scope = scope  # list of FragmentName/TemplateName strings
        self.basic_name = basic_name  # FragmentName, SpecialName, or TemplateName

    def __repr__(self):
        return 'QualifiedName(scope=%r, basic=%r)' % (self.scope, self.basic_name)


class AnonymousNamespace:
    """Anonymous namespace marker (?A@)."""
    __slots__ = ()
    def __repr__(self):
        return 'AnonymousNamespace()'


# ---- Type nodes ----

class PrimitiveType:
    """A primitive type (int, char, void, etc.)."""
    __slots__ = ('name',)
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'PrimitiveType(%r)' % self.name


class PointerType:
    """A pointer type."""
    __slots__ = ('pointee', 'is_const', 'is_volatile', 'is_far')
    def __init__(self, pointee, is_const=False, is_volatile=False, is_far=False):
        self.pointee = pointee
        self.is_const = is_const
        self.is_volatile = is_volatile
        self.is_far = is_far

    def __repr__(self):
        return 'PointerType(%r, const=%r, volatile=%r, far=%r)' % (
            self.pointee, self.is_const, self.is_volatile, self.is_far)


class ReferenceType:
    """An lvalue reference type."""
    __slots__ = ('referent',)
    def __init__(self, referent):
        self.referent = referent

    def __repr__(self):
        return 'ReferenceType(%r)' % self.referent


class RvalueReferenceType:
    """An rvalue reference type (&&)."""
    __slots__ = ('referent',)
    def __init__(self, referent):
        self.referent = referent

    def __repr__(self):
        return 'RvalueReferenceType(%r)' % self.referent


class UserDefinedType:
    """A user-defined type (class, struct, union, enum)."""
    __slots__ = ('kind', 'qualified_name')
    def __init__(self, kind, qualified_name):
        self.kind = kind  # 'class', 'struct', 'union', 'enum'
        self.qualified_name = qualified_name

    def __repr__(self):
        return 'UserDefinedType(%r, %r)' % (self.kind, self.qualified_name)


class FunctionType:
    """A function type: calling convention, return type, args, CV modifiers."""
    __slots__ = ('calling_convention', 'return_type', 'parameters',
                 'is_member', 'cv_modifiers', 'is_static', 'is_virtual',
                 'access', 'is_thunk', 'thunk_adjustment')
    def __init__(self, calling_convention=None, return_type=None, parameters=None,
                 is_member=False, cv_modifiers='', is_static=False, is_virtual=False,
                 access=None, is_thunk=False, thunk_adjustment=None):
        self.calling_convention = calling_convention
        self.return_type = return_type
        self.parameters = parameters if parameters is not None else []
        self.is_member = is_member
        self.cv_modifiers = cv_modifiers
        self.is_static = is_static
        self.is_virtual = is_virtual
        self.access = access  # 'private', 'protected', 'public', None
        self.is_thunk = is_thunk
        self.thunk_adjustment = thunk_adjustment

    def __repr__(self):
        return 'FunctionType(cc=%r, ret=%r, params=%r, member=%r)' % (
            self.calling_convention, self.return_type, self.parameters, self.is_member)


class VariableInfo:
    """A variable (data) symbol: storage class, access, type."""
    __slots__ = ('access', 'is_static', 'var_type', 'is_guard')
    def __init__(self, access=None, is_static=False, var_type=None, is_guard=False):
        self.access = access
        self.is_static = is_static
        self.var_type = var_type
        self.is_guard = is_guard

    def __repr__(self):
        return 'VariableInfo(access=%r, static=%r, type=%r)' % (
            self.access, self.is_static, self.var_type)


class VFTable:
    """Virtual function table."""
    __slots__ = ('scope', 'parents')
    def __init__(self, scope, parents=None):
        self.scope = scope
        self.parents = parents if parents is not None else []

    def __repr__(self):
        return 'VFTable(scope=%r)' % (self.scope,)


# ---- Top-level symbol ----

class MSVCSymbol:
    """Top-level parsed MSVC symbol."""
    __slots__ = ('qualified_name', 'type_info', 'is_embedded', 'kind')
    def __init__(self, qualified_name=None, type_info=None, is_embedded=False, kind='unknown'):
        self.qualified_name = qualified_name
        self.type_info = type_info  # FunctionType, VariableInfo, VFTable, etc.
        self.is_embedded = is_embedded
        self.kind = kind

    def __repr__(self):
        return 'MSVCSymbol(name=%r, type=%r, kind=%r)' % (
            self.qualified_name, self.type_info, self.kind)