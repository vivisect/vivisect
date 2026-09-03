"""
vivisect.demangle.common - Shared types and utilities for all demanglers.
"""

import re

__all__ = [
    'DemangledSymbol', 'DemangleError',
    'normalize_name',
]


class DemangleError(Exception):
    """
    Raised internally by demanglers when parsing fails catastrophically.

    The public :func:`vivisect.demangle.demangle` wrapper catches this and
    returns the original mangled string (graceful degradation).
    """
    pass


class DemangledSymbol:
    """
    Structured representation of a demangled symbol.

    Not all fields are populated by every format demangler.  Fields that
    don't apply to a given format are left at their default (``None``,
    ``False``, ``[]``, ``''``).

    Attributes:
        format (str): The mangling format ('itanium', 'msvc', 'rust', etc.).
        full_name (str): The fully rendered demangled name.
        kind (str): Symbol kind: 'function', 'variable', 'vtable',
            'typeinfo', 'ctor', 'dtor', 'thunk', 'guard', 'template', etc.
        scope (list[str]): Namespace/class path (e.g. ['std', '__cxx11', 'string']).
        name (str): The unqualified name.
        is_template (bool): True if this is a template instantiation.
        template_args (list): Template parameter type/value strings.
        is_member (bool): True if this is a class member.
        is_static (bool): True if this is static (mainly MSVC).
        is_virtual (bool): True if this is virtual (mainly MSVC).
        access (str): 'public', 'private', 'protected', or None.
        calling_convention (str): 'cdecl', 'stdcall', 'thiscall', etc.
        return_type (str or None): Return type string, if known.
        parameters (list[str]): Parameter type strings.
        cv_qualifiers (str): 'const', 'volatile', 'const volatile', or ''.
        ref_qualifier (str): '', '&', or '&&'.
        this_adjustment (int): MSVC thunk this-adjustment value.
        abi_tags (list[str]): ABI tag names (Itanium).
        storage_class (str or None): MSVC storage class.
        original_mangled (str): The original mangled name.
        parse_warnings (list[str]): Non-fatal parse issues.
    """

    __slots__ = (
        'format', 'full_name', 'kind', 'scope', 'name',
        'is_template', 'template_args', 'is_member', 'is_static',
        'is_virtual', 'access', 'calling_convention', 'return_type',
        'parameters', 'cv_qualifiers', 'ref_qualifier',
        'this_adjustment', 'abi_tags', 'storage_class',
        'original_mangled', 'parse_warnings',
    )

    def __init__(self, format=None, full_name='', name='', kind='unknown',
                 scope=None, is_template=False, template_args=None,
                 is_member=False, is_static=False, is_virtual=False,
                 access=None, calling_convention=None, return_type=None,
                 parameters=None, cv_qualifiers='', ref_qualifier='',
                 this_adjustment=0, abi_tags=None, storage_class=None,
                 original_mangled='', parse_warnings=None):
        self.format = format
        self.full_name = full_name
        self.kind = kind
        self.scope = scope if scope is not None else []
        self.name = name
        self.is_template = is_template
        self.template_args = template_args if template_args is not None else []
        self.is_member = is_member
        self.is_static = is_static
        self.is_virtual = is_virtual
        self.access = access
        self.calling_convention = calling_convention
        self.return_type = return_type
        self.parameters = parameters if parameters is not None else []
        self.cv_qualifiers = cv_qualifiers
        self.ref_qualifier = ref_qualifier
        self.this_adjustment = this_adjustment
        self.abi_tags = abi_tags if abi_tags is not None else []
        self.storage_class = storage_class
        self.original_mangled = original_mangled
        self.parse_warnings = parse_warnings if parse_warnings is not None else []

    def __repr__(self):
        return '<DemangledSymbol format=%r kind=%r full_name=%r>' % (
            self.format, self.kind, self.full_name)

    def __eq__(self, other):
        if not isinstance(other, DemangledSymbol):
            return NotImplemented
        return self.full_name == other.full_name and self.format == other.format

    def __hash__(self):
        return hash((self.format, self.full_name))

    def __str__(self):
        return self.full_name

    def to_dict(self):
        """Return a dict representation suitable for JSON serialization."""
        return {k: getattr(self, k) for k in self.__slots__}


# Regex for stripping ELF @@VERSION suffixes (e.g. @@GLIBC_2.4)
_VERSION_SUFFIX_RE = re.compile(r'@@[A-Za-z0-9_.+-]+$')


def normalize_name(name):
    """
    Normalize a mangled symbol name by stripping platform-specific suffixes.

    Currently handles:
        - ELF ``@@VERSION`` suffixes (e.g. ``foo@@GLIBC_2.4``) — but only
          for non-MSVC symbols, since MSVC uses ``@@`` as a scope terminator
        - Trailing NUL bytes

    This replaces the ELF-specific ``normName()`` in the old elf.py parser
    so it can be shared across all binary formats.
    """
    if not name:
        return name
    # Strip @@VERSION suffixes (ELF dynamic linker convention).
    # MSVC mangled symbols start with '?' and use @@ as a scope terminator,
    # so don't strip those.  Use the regex to only strip if the content after
    # @@ looks like a version string (not just any @@).
    if not name.startswith('?'):
        name = _VERSION_SUFFIX_RE.sub('', name)
    # Strip trailing NUL
    if name.endswith('\x00'):
        name = name[:-1]
    return name