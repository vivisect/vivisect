"""
vivisect.demangle.itanium.ast_nodes - AST node classes for Itanium demangling.

The parser produces an AST of these node objects.  The renderer walks the
AST to produce the demangled string.  Each node type represents one
construct from the Itanium C++ ABI mangling grammar.

All nodes inherit from Node and implement:
    - __repr__: for debugging
    - children(): list of child nodes (for walking)
"""

__all__ = [
    'Node', 'Name', 'SourceName', 'NestedName', 'UnqualifiedName',
    'OperatorName', 'CtorDtorName', 'TemplateArgs', 'TemplateArg',
    'BuiltinType', 'PointerType', 'ReferenceType', 'RvalueReferenceType',
    'CVQualifiedType', 'FunctionType', 'BareFunctionType',
    'Substitution', 'TemplateParam', 'SpecialName', 'Array',
    'PointerToMember', 'VendorExtendedType', 'Decltype',
    'ModuleName', 'AbiTag',
]


class Node:
    """Base class for all AST nodes."""
    def children(self):
        return []

    def __repr__(self):
        return '<%s>' % self.__class__.__name__


class Name(Node):
    """A top-level name (function or data name)."""
    def __init__(self, qualified_name, is_function=False, bare_function=None):
        self.qualified_name = qualified_name  # Node (NestedName, SourceName, etc.)
        self.is_function = is_function
        self.bare_function = bare_function  # BareFunctionType or None

    def children(self):
        c = [self.qualified_name]
        if self.bare_function:
            c.append(self.bare_function)
        return c

    def __repr__(self):
        return '<Name func=%r %r>' % (self.is_function, self.qualified_name)


class SourceName(Node):
    """A source name: <length><identifier> (e.g. 3foo -> foo)."""
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<SourceName %r>' % self.name


class NestedName(Node):
    """A nested name: N [<CV-qualifiers>] [<ref-qualifier>] <prefix> <unqualified-name> E"""
    def __init__(self, prefix, unqualified_name, cv_qualifiers='',
                 ref_qualifier=''):
        self.prefix = prefix            # list of Node (scope chain)
        self.unqualified_name = unqualified_name  # Node
        self.cv_qualifiers = cv_qualifiers  # str: 'const', 'volatile', etc.
        self.ref_qualifier = ref_qualifier  # str: '', '&', '&&'
        self.bare_function = None  # optional BareFunctionType (set by _parse_encoding)

    def children(self):
        return self.prefix + [self.unqualified_name]

    def __repr__(self):
        return '<NestedName prefix=%r unq=%r cv=%r ref=%r>' % (
            self.prefix, self.unqualified_name, self.cv_qualifiers,
            self.ref_qualifier)


class UnqualifiedName(Node):
    """An unqualified name: source name, operator, or ctor/dtor."""
    def __init__(self, kind, value, abi_tags=None):
        self.kind = kind  # 'source', 'operator', 'ctor', 'dtor', 'unnamed', 'template'
        self.value = value  # str or Node
        self.abi_tags = abi_tags or []  # list of str

    def children(self):
        if isinstance(self.value, Node):
            return [self.value]
        return []

    def __repr__(self):
        return '<UnqualifiedName kind=%r value=%r>' % (self.kind, self.value)


class OperatorName(Node):
    """An operator name: e.g. 'pl' -> '+'."""
    def __init__(self, code, symbol, num_args=2):
        self.code = code        # str: the 2-char code
        self.symbol = symbol   # str: the operator symbol/name
        self.num_args = num_args

    def __repr__(self):
        return '<OperatorName %s=%s>' % (self.code, self.symbol)


class CtorDtorName(Node):
    """A constructor or destructor name."""
    def __init__(self, kind, is_destructor=False):
        self.kind = kind  # 'complete', 'base', 'allocating', 'deleting', etc.
        self.is_destructor = is_destructor

    def __repr__(self):
        return '<CtorDtorName %s%s>' % ('~' if self.is_destructor else '', self.kind)


class TemplateArgs(Node):
    """Template arguments: I <template-arg>+ E"""
    def __init__(self, args):
        self.args = args  # list of Node

    def children(self):
        return self.args

    def __repr__(self):
        return '<TemplateArgs args=%r>' % (self.args,)


class TemplateArg(Node):
    """A single template argument."""
    def __init__(self, kind, value):
        self.kind = kind  # 'type', 'expression', 'pack', 'pack_expansion'
        self.value = value  # Node or str

    def children(self):
        if isinstance(self.value, Node):
            return [self.value]
        return []

    def __repr__(self):
        return '<TemplateArg kind=%r value=%r>' % (self.kind, self.value)


class BuiltinType(Node):
    """A builtin type (e.g. 'i' -> int)."""
    def __init__(self, name, code=None):
        self.name = name  # str: 'int', 'void', etc.
        self.code = code  # str: the mangled code (e.g. 'i', 'Dd')

    def __repr__(self):
        return '<BuiltinType %s>' % self.name


class PointerType(Node):
    """A pointer: P <type>"""
    def __init__(self, target):
        self.target = target  # Node

    def children(self):
        return [self.target]

    def __repr__(self):
        return '<Pointer %r>' % self.target


class ReferenceType(Node):
    """An lvalue reference: R <type>"""
    def __init__(self, target):
        self.target = target

    def children(self):
        return [self.target]

    def __repr__(self):
        return '<LvalueRef %r>' % self.target


class RvalueReferenceType(Node):
    """An rvalue reference: O <type>"""
    def __init__(self, target):
        self.target = target

    def children(self):
        return [self.target]

    def __repr__(self):
        return '<RvalueRef %r>' % self.target


class CVQualifiedType(Node):
    """A CV-qualified type: K (const), V (volatile), r (restrict)."""
    def __init__(self, base, qualifiers):
        self.base = base  # Node
        self.qualifiers = qualifiers  # str: 'const', 'volatile', 'const volatile', etc.

    def children(self):
        return [self.base]

    def __repr__(self):
        return '<CVQualified %s %r>' % (self.qualifiers, self.base)


class FunctionType(Node):
    """A full function type: F [Y] <bare-function-type> [<ref-qualifier>] E"""
    def __init__(self, bare_function, cv='', ref=''):
        self.bare_function = bare_function  # BareFunctionType
        self.cv = cv  # CV-qualifiers on the function (for member functions)
        self.ref = ref  # ref-qualifier on the function

    def children(self):
        return [self.bare_function]

    def __repr__(self):
        return '<FunctionType cv=%r ref=%r>' % (self.cv, self.ref)


class BareFunctionType(Node):
    """A bare function type: <type>+ (return type + params, or just params)."""
    def __init__(self, types):
        self.types = types  # list of Node: [return_type?, param1, param2, ...]

    def children(self):
        return self.types

    def __repr__(self):
        return '<BareFunctionType types=%r>' % (self.types,)


class Substitution(Node):
    """A substitution reference: S_, S0_, SA_, St, Sa, Sb, Ss, Si, So, Sd."""
    def __init__(self, index=None, std_sub=None):
        self.index = index  # int: the substitution index (S_ = 0, S0_ = 1, ...)
        self.std_sub = std_sub  # str: standard sub key ('t','a','b','s','i','o','d') or None

    def __repr__(self):
        if self.std_sub:
            return '<Substitution std=%r>' % self.std_sub
        return '<Substitution %d>' % self.index


class TemplateParam(Node):
    """A template parameter reference: T_, T0_, T1_, ..."""
    def __init__(self, index):
        self.index = index  # int: 0 for T_, 1 for T0_, etc.

    def __repr__(self):
        return '<TemplateParam %d>' % self.index


class SpecialName(Node):
    """A special name: TV (vtable), TT (VTT), TI (typeinfo), TS (typeinfo name), GV (guard), etc."""
    def __init__(self, kind, target=None):
        self.kind = kind  # str: 'vtable', 'VTT', 'typeinfo', 'typeinfo name', 'guard', etc.
        self.target = target  # Node (the type or name this refers to)

    def children(self):
        if self.target is not None:
            return [self.target]
        return []

    def __repr__(self):
        return '<SpecialName %r>' % self.kind


class Array(Node):
    """An array type: A <dimension> _ <type>"""
    def __init__(self, dimension, element_type):
        self.dimension = dimension  # str: the dimension expression
        self.element_type = element_type  # Node

    def children(self):
        return [self.element_type]

    def __repr__(self):
        return '<Array dim=%r %r>' % (self.dimension, self.element_type)


class PointerToMember(Node):
    """A pointer-to-member: M <class-type> <member-type>"""
    def __init__(self, class_type, member_type):
        self.class_type = class_type  # Node
        self.member_type = member_type  # Node

    def children(self):
        return [self.class_type, self.member_type]

    def __repr__(self):
        return '<PointerToMember class=%r member=%r>' % (
            self.class_type, self.member_type)


class VendorExtendedType(Node):
    """A vendor-extended type: u <source-name> [<template-args>]"""
    def __init__(self, name, template_args=None):
        self.name = name  # str
        self.template_args = template_args  # TemplateArgs or None

    def children(self):
        return [self.template_args] if self.template_args else []

    def __repr__(self):
        return '<VendorExt %r>' % self.name


class Decltype(Node):
    """A decltype expression: Dt <expression> E or DT <expression> E"""
    def __init__(self, expression, is_template=False):
        self.expression = expression  # str or Node
        self.is_template = is_template  # True for DT (toplevel)

    def __repr__(self):
        return '<Decltype tmpl=%r %r>' % (self.is_template, self.expression)


class ModuleName(Node):
    """A module name (C++20 modules): C1.2 etc."""
    def __init__(self, name, is_partition=False):
        self.name = name  # str
        self.is_partition = is_partition

    def __repr__(self):
        return '<Module %r>' % self.name


class AbiTag(Node):
    """An ABI tag: B <source-name>."""
    def __init__(self, tag):
        self.tag = tag  # str

    def __repr__(self):
        return '<AbiTag %r>' % self.tag