"""
vivisect.demangle.symbol - The Symbol class for demangled symbol representation.

A Symbol holds:
    - original:    The original mangled name (exact input, no normalization)
    - demangled:   The fully demangled name string
    - stripped:    Extra metadata (e.g. stripped @@VERSION suffixes, comments)
    - structured:  Parsed components (scope, name, kind, template_args,
                   return_type, parameters, calling_convention, etc.)

For functions that contain type, return, and argument data, all of that
information is available as structured fields.  The Symbol class is the
canonical object that parsers, the workspace, and downstream analysis
tools pass around.
"""

from vivisect.demangle.common import DemangledSymbol, normalize_name

__all__ = ['Symbol']


class Symbol:
    """
    Canonical symbol object holding original, demangled, stripped, and
    structured data for a (potentially mangled) symbol name.

    Attributes:
        original (str):    The exact original input (mangled or plain).
                           Never modified — preserves provenance.
        demangled (str):    The demangled name string.  If demangling
                           failed, equals the normalized original.
        stripped (dict):    Extra data stripped during normalization
                           (e.g. ``{'version_suffix': '@@GLIBC_2.4'}``).
        format (str):       The mangling format ('itanium', 'msvc', etc.)
                           or 'unknown'.
        kind (str):         Symbol kind: 'function', 'variable', 'vtable',
                           'typeinfo', 'ctor', 'dtor', 'thunk', 'guard',
                           'template', etc.
        scope (list[str]):  Namespace/class path (e.g.
                           ['std', '__cxx11', 'string']).
        name (str):         The unqualified name.
        is_template (bool): True if this is a template instantiation.
        template_args (list[str]): Template parameter type strings.
        is_member (bool):   True if this is a class member.
        is_static (bool):   True if static (mainly MSVC).
        is_virtual (bool):  True if virtual (mainly MSVC).
        access (str):       'public', 'private', 'protected', or None.
        calling_convention (str): 'cdecl', 'stdcall', etc.
        return_type (str or None): Return type string, if known.
        parameters (list[str]):   Parameter type strings.
        cv_qualifiers (str):  'const', 'volatile', 'const volatile', ''.
        ref_qualifier (str):   '', '&', or '&&'.
        abi_tags (list[str]):  ABI tag names (Itanium).
        parse_warnings (list[str]): Non-fatal parse issues.

    The ``structured`` property returns a DemangledSymbol for backward
    compatibility with the Phase 0 API.
    """

    __slots__ = (
        'original', 'demangled', 'stripped', 'format', 'kind',
        'scope', 'name', 'is_template', 'template_args',
        'is_member', 'is_static', 'is_virtual', 'access',
        'calling_convention', 'return_type', 'parameters',
        'cv_qualifiers', 'ref_qualifier', 'abi_tags',
        'parse_warnings',
    )

    def __init__(self, original='', demangled=None, format='unknown',
                 kind='unknown', scope=None, name='', is_template=False,
                 template_args=None, is_member=False, is_static=False,
                 is_virtual=False, access=None, calling_convention=None,
                 return_type=None, parameters=None, cv_qualifiers='',
                 ref_qualifier='', abi_tags=None, stripped=None,
                 parse_warnings=None):
        self.original = original
        self.demangled = demangled if demangled is not None else original
        self.stripped = stripped if stripped is not None else {}
        self.format = format
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
        self.abi_tags = abi_tags if abi_tags is not None else []
        self.parse_warnings = parse_warnings if parse_warnings is not None else []

    @property
    def structured(self):
        """Return a DemangledSymbol for backward compat with Phase 0 API."""
        sym = DemangledSymbol(
            format=self.format,
            full_name=self.demangled,
            kind=self.kind,
            scope=list(self.scope),
            name=self.name,
            is_template=self.is_template,
            template_args=list(self.template_args),
            is_member=self.is_member,
            is_static=self.is_static,
            is_virtual=self.is_virtual,
            access=self.access,
            calling_convention=self.calling_convention,
            return_type=self.return_type,
            parameters=list(self.parameters),
            cv_qualifiers=self.cv_qualifiers,
            ref_qualifier=self.ref_qualifier,
            this_adjustment=0,
            abi_tags=list(self.abi_tags),
            storage_class=None,
            original_mangled=self.original,
            parse_warnings=list(self.parse_warnings),
        )
        return sym

    @classmethod
    def from_demangled_symbol(cls, dsym, original=None, stripped=None):
        """Build a Symbol from a DemangledSymbol (Phase 0 compat)."""
        return cls(
            original=original if original is not None else dsym.original_mangled,
            demangled=dsym.full_name,
            format=dsym.format,
            kind=dsym.kind,
            scope=list(dsym.scope),
            name=dsym.name,
            is_template=dsym.is_template,
            template_args=list(dsym.template_args),
            is_member=dsym.is_member,
            is_static=dsym.is_static,
            is_virtual=dsym.is_virtual,
            access=dsym.access,
            calling_convention=dsym.calling_convention,
            return_type=dsym.return_type,
            parameters=list(dsym.parameters),
            cv_qualifiers=dsym.cv_qualifiers,
            ref_qualifier=dsym.ref_qualifier,
            abi_tags=list(dsym.abi_tags),
            stripped=stripped,
            parse_warnings=list(dsym.parse_warnings),
        )

    def __str__(self):
        return self.demangled

    def __repr__(self):
        return '<Symbol format=%r kind=%r demangled=%r>' % (
            self.format, self.kind, self.demangled)

    def __eq__(self, other):
        if not isinstance(other, Symbol):
            return NotImplemented
        return self.demangled == other.demangled and self.format == other.format

    def __hash__(self):
        return hash((self.format, self.demangled))

    def to_dict(self):
        """Return a dict representation suitable for JSON serialization."""
        return {k: getattr(self, k) for k in self.__slots__}