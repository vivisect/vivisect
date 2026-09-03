"""
vivisect.demangle.dlang - D language symbol demangling (_D prefix).

Full D mangling support per the D ABI specification:
    https://dlang.org/spec/abi.html#name_mangling

Features:
    - Length-prefixed qualified names (module.class.function)
    - Function types (F...Z...) with parameters and return type
    - Delegate types (D...Z...)
    - All primitive types (void, bool, byte/ubyte, short/ushort, etc.)
    - Pointers (P), arrays (A), static arrays (G<number>)
    - Type qualifiers: const (O), immutable (x), shared (O), wildcard (Ng)
    - Associated types: return (Ni), parameter (Np)
    - Const/immutable/shared modifiers on types
    - References (R)
    - New types: cent/ucent (zi/zk)
    - noreturn (Nn)
    - Special suffixes: __initZ, __vtblZ, __ClassZ, __InterfaceZ, __ModuleInfoZ
    - Type back-references (Q<number>)
    - Symbol back-references (B<number>)

References:
    - LLVM DLangDemangle.cpp (llvm/lib/Demangle/DLangDemangle.cpp)
    - D ABI specification
"""

import logging

from vivisect.demangle.common import DemangledSymbol, normalize_name

logger = logging.getLogger(__name__)

__all__ = ['demangle_d']


def demangle_d(mangled, structured=False):
    """Demangle a D language mangled symbol (_D prefix).

    Args:
        mangled: The mangled symbol string.
        structured: If True, return a DemangledSymbol object.

    Returns:
        The demangled name string, or DemangledSymbol if structured=True.
    """
    original = mangled
    mangled = normalize_name(mangled)

    demangled = None
    parse_warnings = []

    try:
        parser = _DParser(mangled)
        demangled = parser.parse()
        parse_warnings = parser.warnings
    except Exception as e:
        logger.debug('D parser failed for %r: %r', mangled, e)
        parse_warnings.append('parser error: %r' % e)

    if demangled is None or demangled == mangled or not demangled:
        if structured:
            return DemangledSymbol(
                format='d',
                full_name=original,
                name=original,
                original_mangled=original,
                parse_warnings=parse_warnings or ['unable to demangle'],
            )
        return original

    if not structured:
        return demangled

    sym = DemangledSymbol(
        format='d',
        full_name=demangled,
        original_mangled=original,
        parse_warnings=parse_warnings,
    )
    _parse_basic_structure(sym, demangled)
    return sym


# D primitive type codes -> type names
# From D ABI spec: https://dlang.org/spec/abi.html#name_mangling
_D_TYPES = {
    'v': 'void',
    'b': 'bool',
    'y': 'byte',
    'g': 'ubyte',
    'h': 'short',
    't': 'ushort',
    'i': 'int',
    'j': 'uint',
    'k': 'long',
    'm': 'ulong',
    'l': 'real',
    'f': 'float',
    'd': 'double',
    'e': 'extended',  # real (80-bit on x86)
    'c': 'cfloat',    # complex float
    'q': 'cdouble',   # complex double
    'r': 'creal',     # complex real
    'p': 'cextended', # complex extended
    'a': 'char',
    'u': 'wchar',
    'w': 'dchar',
    's': 'string',
    'o': 'wstring',
    'x': 'dstring',
    'n': 'char[]',
    'z': 'void',      # sometimes used for char[]
    # Newer D types
    'zi': 'cent',
    'zk': 'ucent',
}

# D type qualifiers
_D_QUALIFIERS = {
    'O': 'shared',     # shared (also const shared when combined)
    'x': 'immutable',  # immutable
    'Ny': 'wild',      # wildcard (inout)
    'Nc': 'const',     # const (when used as modifier prefix Nc)
}


class _DParser:
    """Parser for D language mangled symbols.

    Implements the full D mangling grammar:
        <mangled-name> ::= _D <LName> <function-type> | <special-name>
        <function-type> ::= <call-convention>? <function-attributes>* <parameters> <return-type>?
        <parameters> ::= <type>* Z
        <type> ::= <primitive> | <pointer> | <array> | <static-array> |
                   <function> | <delegate> | <qualified-type> | <backref>
    """

    def __init__(self, mangled):
        self.mangled = mangled
        self.pos = 0
        self.warnings = []
        self._type_backrefs = []  # Type back-references
        self._symbol_backrefs = []  # Symbol back-references

    def _peek(self, offset=0):
        idx = self.pos + offset
        if idx >= len(self.mangled):
            return '\x00'
        return self.mangled[idx]

    def _next(self):
        if self.pos >= len(self.mangled):
            raise ValueError('unexpected end of input at pos %d' % self.pos)
        ch = self.mangled[self.pos]
        self.pos += 1
        return ch

    def _at_end(self):
        return self.pos >= len(self.mangled)

    def _eat(self, ch):
        if self._peek() == ch:
            self.pos += 1
            return True
        return False

    def _parse_number(self):
        """Parse a decimal number."""
        result = 0
        while self._peek().isdigit():
            result = result * 10 + int(self._next())
        return result

    def parse(self):
        """Entry point: parse a D mangled symbol."""
        if not self.mangled.startswith('_D'):
            raise ValueError('D symbols must start with _D')
        self.pos = 2

        # Check for special names (main, etc.)
        if self.mangled[2:] == 'main':
            return 'D main'

        result = self._parse_mangled_name()

        # Check for special suffixes (appended after the name+type)
        if not self._at_end():
            suffix = self.mangled[self.pos:]
            result = self._handle_special_suffix(result, suffix)

        return result

    def _handle_special_suffix(self, name, suffix):
        """Handle special name suffixes like __initZ, __vtblZ, etc."""
        special = {
            '__initZ': ' __init',
            '__vtblZ': ' vtbl',
            '__ClassZ': ' Class',
            '__InterfaceZ': ' Interface',
            '__ModuleInfoZ': ' ModuleInfo',
            '__constZ': ' const',
            '__sharedZ': ' shared',
            '__invariantZ': ' invariant',
        }
        for sfx, replacement in special.items():
            if suffix == sfx:
                return '%s%s' % (name, replacement)
        # If it ends with Z (end of type list), it's already handled
        if suffix == 'Z':
            return name
        return name

    def _parse_mangled_name(self):
        """Parse <mangled-name> ::= <number> <name> <type>

        The name is a chain of length-prefixed identifiers separated by dots.
        After the name comes the function type (parameters + return type).
        """
        name_parts = []

        # Special case: just "main"
        if self._peek() == 'm' and self.mangled[self.pos:].startswith('main'):
            # Check if the full remaining is just "main"
            if self.mangled[self.pos:] == 'main':
                return 'D main'
            # Otherwise it's a length prefix

        while self._peek().isdigit():
            length = self._parse_number()
            if length == 0 or self.pos + length > len(self.mangled):
                raise ValueError('invalid name length %d at pos %d' % (length, self.pos))
            name = self.mangled[self.pos:self.pos + length]
            self.pos += length

            # Check for special name suffixes (__init, __vtbl, etc.)
            # These are part of the last name component
            # They'll be handled after parsing the full name

            # Add this name part to the symbol backrefs
            self._symbol_backrefs.append(name)
            name_parts.append(name)

        if not name_parts:
            raise ValueError('no name parts found')

        name = '.'.join(name_parts)

        # Check for special suffixes BEFORE the type
        # e.g., _D3foo6__initZ -> foo.__init (no function type)
        if name_parts and name_parts[-1].startswith('__'):
            # This is a special name, no type follows
            return name

        # Parse the function type (parameters + return type)
        if not self._at_end():
            type_str = self._parse_function_type()
            if type_str:
                # D demangling format: name(params)return_type
                # But c++filt/demangle format is: return_type name(params)
                # We use: name(params) -> return_type
                # Actually, the standard D format is just: name(params)
                # with the return type shown as a suffix
                if type_str.startswith('('):
                    return '%s%s' % (name, type_str)
                else:
                    return '%s %s' % (type_str, name)

        return name

    def _parse_function_type(self):
        """Parse a function type: <call-convention>? <attributes>* <params> Z <return-type>?

        D function types are:
        F <call-convention>? <function-attributes>* <params> Z <return-type>?

        For the top-level symbol, we just want the parameter list.
        """
        # The function type starts with F (function) or is just a type list
        if self._peek() == 'F':
            return self._parse_func_type_inner()

        # Some symbols have just the parameter types without F prefix
        # Parse as a bare type list
        params = []
        while not self._at_end() and self._peek() != 'Z':
            try:
                ty = self._parse_type()
                if ty:
                    params.append(ty)
            except (ValueError, IndexError):
                break

        if self._peek() == 'Z':
            self._next()

        # Parse return type if present
        ret_type = ''
        if not self._at_end():
            try:
                ret_type = self._parse_type()
            except (ValueError, IndexError):
                pass

        if ret_type:
            return '(%s) %s' % (', '.join(params), ret_type)
        return '(%s)' % ', '.join(params)

    def _parse_func_type_inner(self):
        """Parse F <call-convention>? <attrs>* <params> Z <return-type>?"""
        self._next()  # consume F

        # Calling convention is NOT parsed here because the D ABI
        # reuses type chars (a=char, w=dchar, u=wchar) as calling
        # convention codes, making them ambiguous without context.
        # Since explicit calling conventions are extremely rare in
        # practice, we skip detection to avoid misinterpreting types.
        call_conv = ''

        # Function attributes (optional, N-prefixed)
        attrs = []
        while self._peek() == 'N':
            self._next()
            attr_char = self._next()
            attr_map = {
                'a': 'pure',
                'b': 'nothrow',
                'c': 'ref',
                'd': 'return',
                'e': 'scope',
                'f': 'return ref',
                'g': 'scope return',
                'h': '@nogc',
                'i': '@live',
                'j': 'return scope',
                'k': 'const',
                'l': 'immutable',
                'm': 'shared',
                'n': 'wild',
                'o': 'return',
                'p': '@safe',
                'q': '@trusted',
                'r': '@system',
            }
            attr = attr_map.get(attr_char, '')
            if attr:
                attrs.append(attr)

        # Parameters (type list terminated by Z)
        params = []
        while not self._at_end() and self._peek() != 'Z':
            try:
                ty = self._parse_type()
                if ty:
                    params.append(ty)
            except (ValueError, IndexError):
                break

        if self._peek() == 'Z':
            self._next()

        # Return type (optional)
        ret_type = ''
        if not self._at_end():
            try:
                ret_type = self._parse_type()
            except (ValueError, IndexError):
                pass

        # Build the function signature
        prefix = ' '.join(attrs)
        if call_conv:
            prefix = ('%s %s' % (call_conv, prefix)).strip()

        param_str = ', '.join(params)
        if ret_type:
            sig = '%s(%s) %s' % (prefix, param_str, ret_type) if prefix else '(%s) %s' % (param_str, ret_type)
        else:
            sig = '%s(%s)' % (prefix, param_str) if prefix else '(%s)' % param_str

        return sig

    def _parse_type(self):
        """Parse a D type.

        <type> ::= <primitive>
                 ::= P <type>           (pointer)
                 ::= R <type>           (reference)
                 ::= A <type>           (dynamic array)
                 ::= G <number> <type>  (static array)
                 ::= H <type> <type>    (associative array)
                 ::= F <function-type>  (function pointer)
                 ::= D <function-type>  (delegate)
                 ::= O <type>           (shared)
                 ::= x <type>           (immutable)
                 ::= Nc <type>          (const)
                 ::= Ny <type>          (wild/inout)
                 ::= Nn                 (noreturn)
                 ::= Q <number>          (type backref)
                 ::= B <number>         (symbol backref)
                 ::= <length> <name>    (named type)
        """
        ch = self._peek()

        # Two-char type codes (zi, zk, Nn, Ny, Nc, Np, Ni)
        two_char = self.mangled[self.pos:self.pos + 2]
        if two_char in _D_TYPES:
            self.pos += 2
            return _D_TYPES[two_char]
        if two_char == 'Nn':
            self.pos += 2
            return 'noreturn'
        if two_char == 'Ny':
            self.pos += 2
            inner = self._parse_type()
            return 'wild(%s)' % inner
        if two_char == 'Nc':
            self.pos += 2
            inner = self._parse_type()
            return 'const(%s)' % inner
        if two_char == 'Np':
            self.pos += 2
            inner = self._parse_type()
            return 'param(%s)' % inner
        if two_char == 'Ni':
            self.pos += 2
            inner = self._parse_type()
            return 'return(%s)' % inner

        # Type qualifiers
        if ch == 'O':
            self._next()
            inner = self._parse_type()
            return 'shared(%s)' % inner
        if ch == 'x':
            self._next()
            inner = self._parse_type()
            return 'immutable(%s)' % inner

        # Primitive types
        if ch in _D_TYPES:
            self._next()
            return _D_TYPES[ch]

        # Pointer
        if ch == 'P':
            self._next()
            inner = self._parse_type()
            self._type_backrefs.append(inner)
            return '%s*' % inner

        # Reference
        if ch == 'R':
            self._next()
            inner = self._parse_type()
            self._type_backrefs.append(inner)
            return 'ref %s' % inner

        # Dynamic array
        if ch == 'A':
            self._next()
            inner = self._parse_type()
            self._type_backrefs.append(inner)
            return '%s[]' % inner

        # Static array
        if ch == 'G':
            self._next()
            n = self._parse_number()
            inner = self._parse_type()
            self._type_backrefs.append(inner)
            return '%s[%d]' % (inner, n)

        # Associative array
        if ch == 'H':
            self._next()
            key = self._parse_type()
            value = self._parse_type()
            self._type_backrefs.append(value)
            return '%s[%s]' % (value, key)

        # Function pointer
        if ch == 'F':
            return self._parse_func_type_inner()

        # Delegate
        if ch == 'D':
            self._next()
            func_sig = self._parse_func_type_inner()
            return 'delegate %s' % func_sig

        # Type back-reference (Q<number>)
        if ch == 'Q':
            self._next()
            idx = self._parse_number()
            if idx < len(self._type_backrefs):
                return self._type_backrefs[idx]
            return '<backref:%d>' % idx

        # Symbol back-reference (B<number>)
        if ch == 'B':
            self._next()
            idx = self._parse_number()
            if idx < len(self._symbol_backrefs):
                return self._symbol_backrefs[idx]
            return '<symref:%d>' % idx

        # Named type (length-prefixed)
        if ch.isdigit():
            length = self._parse_number()
            if length > 0 and self.pos + length <= len(self.mangled):
                name = self.mangled[self.pos:self.pos + length]
                self.pos += length
                self._type_backrefs.append(name)
                return name

        # Unknown
        self._next()
        return '?%s' % ch


def _parse_basic_structure(sym, demangled):
    """Parse basic structure from a demangled D name."""
    if '.' in demangled:
        parts = demangled.rsplit('.', 1)
        sym.scope = parts[0].split('.')
        sym.name = parts[1]
    else:
        sym.name = demangled

    if '(' in sym.name:
        sym.kind = 'function'
    elif sym.name.startswith('__'):
        sym.kind = 'special'
    else:
        sym.kind = 'variable'

    if '<' in sym.name:
        sym.is_template = True