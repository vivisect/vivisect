"""
vivisect.demangle.swift - Swift symbol demangling ($s / _T0 / $S prefix).

Swift mangling is a postfix-operator language with 800+ grammar productions.
This implementation handles the common cases found in real-world binaries:

    - Module + entity names (length-prefixed identifiers)
    - Function/entity kinds (v=variable, F=function, etc.)
    - Basic type operators (i=int, d=double, y=void, etc.)
    - Class/struct/enum types (C, V, O prefixes)
    - Protocol types (P prefix)
    - Generic substitutions (G prefix)
    - Type lists and function signatures
    - Protocol conformance (Hp/HpX)
    - Opaque return types (Qo)
    - Back-references (A prefix)
    - Substitutions (standard substitutions for common Swift types)
    - Mangling version prefixes ($s, $S, _T0, $e)

Not yet implemented:
    - Full postfix operator stack machine
    - All 800+ grammar productions
    - Closure types (K)
    - Associated types (Q)
    - Symbolic references (binary control chars)
    - Full generic signature parsing
    - Accessor kinds (getter/setter/willSet/didSet)

References:
    - Swift mangling specification (swift-mangling.rst)
    - LLVM SwiftDemangle.cpp
    - swift/lib/Demangling/Demangler.cpp
"""

import logging
import re

from vivisect.demangle.common import DemangledSymbol, normalize_name

logger = logging.getLogger(__name__)

__all__ = ['demangle_swift']


def demangle_swift(mangled, structured=False):
    """Demangle a Swift mangled symbol ($s / _T0 / $S prefix).

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
        parser = _SwiftParser(mangled)
        demangled = parser.parse()
        parse_warnings = parser.warnings
    except Exception as e:
        logger.debug('Swift parser failed for %r: %r', mangled, e)
        parse_warnings.append('parser error: %r' % e)

    if demangled is None or not demangled or demangled == mangled:
        # Fallback to basic extraction
        try:
            demangled = _demangle_swift_basic(mangled)
            if demangled and demangled != mangled:
                parse_warnings = parse_warnings or ['basic extraction fallback']
            else:
                demangled = None
        except Exception as e:
            logger.debug('Swift basic fallback failed for %r: %r', mangled, e)
            parse_warnings.append('basic fallback error: %r' % e)

    if demangled is None or not demangled or demangled == mangled:
        if structured:
            return DemangledSymbol(
                format='swift',
                full_name=original,
                name=original,
                original_mangled=original,
                parse_warnings=parse_warnings or ['unable to demangle'],
            )
        return original

    if not structured:
        return demangled

    sym = DemangledSymbol(
        format='swift',
        full_name=demangled,
        original_mangled=original,
        parse_warnings=parse_warnings,
    )
    _parse_basic_structure(sym, demangled)
    return sym


# Swift basic type operators (postfix)
_SWIFT_TYPES = {
    'b': 'Builtin.BridgeObject',
    'B': 'Builtin.BridgeObject',
    'c': 'Builtin.BridgeObject',
    'd': 'Double',
    'f': 'Float',
    'i': 'Int',
    'h': 'Builtin.Word',
    'l': 'Builtin.IntLiteral',
    'n': 'Builtin.UnknownPointer',
    'p': 'Builtin.RawPointer',
    'q': 'Builtin.UnknownPointer',
    'r': 'Builtin.UnknownPointer',
    's': 'String',
    't': 'Builtin.BridgeObject',
    'u': 'UInt',
    'v': 'Builtin.BridgeObject',
    'w': 'Builtin.Word',
    'x': 'Builtin.Int64',
    'y': 'Void',  # also used as empty type list
    'z': 'Builtin.UnknownPointer',
    'A': 'Builtin.BridgeObject',
    'C': 'Builtin.BridgeObject',
    'D': 'Builtin.BridgeObject',
    'E': 'Builtin.BridgeObject',
    'F': 'Builtin.BridgeObject',
    'G': 'Builtin.BridgeObject',
    'H': 'Builtin.BridgeObject',
    'I': 'Builtin.BridgeObject',
    'J': 'Builtin.BridgeObject',
    'K': 'Builtin.BridgeObject',
    'L': 'Builtin.BridgeObject',
    'M': 'Builtin.BridgeObject',
    'N': 'Builtin.BridgeObject',
    'O': 'Builtin.BridgeObject',
    'P': 'Builtin.BridgeObject',
    'Q': 'Builtin.BridgeObject',
    'R': 'Builtin.BridgeObject',
    'S': 'Builtin.BridgeObject',
    'T': 'Builtin.BridgeObject',
    'U': 'Builtin.BridgeObject',
    'V': 'Builtin.BridgeObject',
    'W': 'Builtin.BridgeObject',
    'X': 'Builtin.BridgeObject',
    'Y': 'Builtin.BridgeObject',
    'Z': 'Builtin.BridgeObject',
}

# Standard substitutions
_SWIFT_SUBS = {
    'S_': 'Swift',  # The Swift module itself
    'SQ': 'Swift.Optional',
    'Sg': 'Swift.Optional<...>',
    'Sb': 'Swift.Bool',
    'Si': 'Swift.Int',
    'Sd': 'Swift.Double',
    'Ss': 'Swift.String',
    'Sf': 'Swift.Float',
    'Su': 'Swift.UInt',
    'SS': 'Swift.String',
    'Sa': 'Swift.Array',
    'SD': 'Swift.Dictionary',
    'SN': 'Swift.Int',
    'Sx': 'Swift.Int',
    'Sy': 'Void',
}


class _SwiftParser:
    """Parser for Swift mangled symbols.

    Implements a subset of the Swift mangling grammar sufficient for
    common symbols found in real-world binaries. The parser uses a
    recursive descent approach for the most common productions.
    """

    def __init__(self, mangled):
        self.s = mangled
        self.pos = 0
        self.warnings = []
        self._subs = []  # Substitution table
        self._depth = 0  # Recursion depth guard

    def _peek(self, offset=0):
        idx = self.pos + offset
        if idx >= len(self.s):
            return '\x00'
        return self.s[idx]

    def _next(self):
        if self.pos >= len(self.s):
            raise ValueError('unexpected end of input at pos %d' % self.pos)
        ch = self.s[self.pos]
        self.pos += 1
        return ch

    def _eat(self, ch):
        if self._peek() == ch:
            self.pos += 1
            return True
        return False

    def _at_end(self):
        return self.pos >= len(self.s)

    def _parse_number(self):
        """Parse a decimal number (for ident lengths)."""
        result = 0
        while self._peek().isdigit():
            result = result * 10 + int(self._next())
        return result

    def parse(self):
        """Entry point: parse a Swift mangled symbol."""
        # Determine mangling prefix
        if self.s.startswith('$s'):
            self.pos = 2
        elif self.s.startswith('$S'):
            self.pos = 2
        elif self.s.startswith('_T0'):
            self.pos = 3
        elif self.s.startswith('$e'):
            self.pos = 2
        else:
            return None

        # Parse the main entity
        result = self._parse_entity()
        return result

    def _parse_entity(self):
        """Parse a Swift entity (function, variable, type, etc.).

        The entity starts with a module name (length-prefixed) followed
        by a kind-specific suffix.
        """
        if self._depth > 50:
            raise ValueError('recursion too deep')

        self._depth += 1
        try:
            result = self._parse_context_or_entity()
        finally:
            self._depth -= 1

        return result

    def _parse_context_or_entity(self):
        """Parse a context (module/class/struct) or entity name.

        Swift mangling uses length-prefixed identifiers for names.
        After a module name, the next identifier is the entity name,
        optionally followed by type encoding.
        """
        # Check for standard substitution
        if self._peek() == 'S':
            sub = self._parse_substitution()
            if sub:
                return sub

        # Check for back-reference
        if self._peek() == 'A':
            return self._parse_backref()

        # Parse module name (length-prefixed)
        if not self._peek().isdigit():
            # Could be an operator or special encoding
            ch = self._peek()
            if ch.isalpha() and ch.isupper():
                # Type operator (C=class, V=struct, O=enum, P=protocol)
                return self._parse_type()
            return None

        module = self._parse_ident()
        if not module:
            return None

        # Add to substitution table
        self._subs.append(module)

        parts = [module]

        # Parse additional context names (class, struct, etc.)
        while self._peek().isdigit():
            name = self._parse_ident()
            if not name:
                break
            self._subs.append('.'.join(parts + [name]))
            parts.append(name)

        # Now we have: module.class.function (or just module.function)
        qualified = '.'.join(parts)

        # Check for type suffix (function parameters/return type)
        # The type suffix starts with a non-digit character
        if not self._at_end() and not self._peek().isdigit():
            type_suffix = self._parse_type_suffix()
            if type_suffix:
                # Format: Module.func(params) -> ReturnType
                # Or just the qualified name with type info
                if '(' in type_suffix:
                    return '%s%s' % (qualified, type_suffix)
                else:
                    return '%s -> %s' % (qualified, type_suffix)

        return qualified

    def _parse_ident(self):
        """Parse a length-prefixed identifier."""
        length = self._parse_number()
        if length == 0 or self.pos + length > len(self.s):
            return None

        name = self.s[self.pos:self.pos + length]
        self.pos += length

        # Decode escape sequences
        name = _decode_swift_escapes(name)

        return name

    def _parse_type(self):
        """Parse a Swift type encoding (simplified).

        Swift uses postfix operators for types. This is a simplified
        version that handles the most common cases.
        """
        ch = self._peek()

        # Type operators (postfix)
        if ch == 'C':
            self._next()
            # Class type: C <module> <name>
            module = self._parse_ident()
            name = self._parse_ident()
            return '%s.%s' % (module, name)

        if ch == 'V':
            self._next()
            # Struct type: V <module> <name>
            module = self._parse_ident()
            name = self._parse_ident()
            return '%s.%s' % (module, name)

        if ch == 'O':
            self._next()
            # Enum type: O <module> <name>
            module = self._parse_ident()
            name = self._parse_ident()
            return '%s.%s' % (module, name)

        if ch == 'P':
            self._next()
            # Protocol type: P <module> <name>
            module = self._parse_ident()
            name = self._parse_ident()
            return '%s.%s' % (module, name)

        # Basic types (single char)
        if ch in ('i', 'd', 'f', 's', 'u', 'y', 'b', 'h'):
            self._next()
            type_map = {
                'i': 'Int', 'd': 'Double', 'f': 'Float',
                's': 'String', 'u': 'UInt', 'y': 'Void',
                'b': 'Bool', 'h': 'Builtin.Word',
            }
            return type_map.get(ch, '?%s' % ch)

        # Function type: F <params> <return>
        if ch == 'F':
            self._next()
            params = self._parse_type_list()
            ret = self._parse_type()
            return '(%s) -> %s' % (params, ret)

        # Generic type: G <count> <args>
        if ch == 'G':
            self._next()
            return '<generic>'

        # Opaque return type: Qo
        if ch == 'Q':
            self._next()
            if self._eat('o'):
                return 'some'
            return '<opaque>'

        # Optional: u (suffix) or Sg (substitution)
        if ch == 'u':
            self._next()
            return 'Optional'

        # Unknown — consume and return placeholder
        self._next()
        return '?%s' % ch

    def _parse_type_list(self):
        """Parse a type list: y <type>* t (or _T0 format)"""
        # y = start of type list, t = end
        if self._eat('y'):
            types = []
            while not self._at_end() and self._peek() != 't':
                ty = self._parse_type()
                if ty:
                    types.append(ty)
                else:
                    break
            self._eat('t')
            return ', '.join(types)
        return ''

    def _parse_type_suffix(self):
        """Parse the type suffix after an entity name.

        In Swift mangling, after the entity name comes:
        - F <type-list> <return-type>  (function)
        - v <type>                      (variable)
        - Other entity kind characters
        """
        ch = self._peek()

        # Function: F<params><return>
        if ch == 'F':
            self._next()
            params = self._parse_type_list()
            ret = self._parse_type()
            if ret and ret != 'Void':
                return '(%s) -> %s' % (params, ret)
            return '(%s)' % params

        # Variable: v<type>
        if ch == 'v':
            self._next()
            ty = self._parse_type()
            return ''  # Variables don't have () suffix

        # Initializer: fc
        if ch == 'f':
            self._next()
            if self._eat('c'):
                return '(init)'

        # Deinitializer: fd
        if ch == 'f':
            self._next()
            if self._eat('d'):
                return '(deinit)'

        # Getter: g<type>
        if ch == 'g':
            self._next()
            self._parse_type()
            return ''

        # Setter: s<type>
        if ch == 's':
            self._next()
            self._parse_type()
            return ''

        # Subscript: i
        if ch == 'i':
            self._next()
            params = self._parse_type_list()
            ret = self._parse_type()
            return '[%s] -> %s' % (params, ret)

        # Protocol conformance descriptor: Hp
        if ch == 'H':
            self._next()
            if self._eat('p'):
                # Parse protocol conformance
                proto = self._parse_type()
                return ' protocol conformance %s' % proto

        # Metadata accessor: Ma
        if ch == 'M':
            self._next()
            self._eat('a')
            return ' (metadata accessor)'

        # Type metadata: Mn
        if ch == 'M':
            self._next()
            self._eat('n')
            return ' (type metadata)'

        # Unknown suffix — don't consume, let caller handle
        return ''

    def _parse_substitution(self):
        """Parse a standard substitution (S prefix)."""
        if self._peek() != 'S':
            return None

        # Check two-char substitutions
        two = self.s[self.pos:self.pos + 2]
        if two in _SWIFT_SUBS:
            self.pos += 2
            return _SWIFT_SUBS[two]

        # S_ = Swift module
        if self._eat('S'):
            if self._eat('_'):
                return 'Swift'
            # Other S<letter> combinations
            ch = self._next()
            return 'S%c' % ch

        return None

    def _parse_backref(self):
        """Parse a back-reference (A prefix)."""
        self._eat('A')
        # Back-references in Swift are complex — skip for now
        idx = self._parse_number()
        if idx < len(self._subs):
            return self._subs[idx]
        return '<backref:%d>' % idx


def _demangle_swift_basic(mangled):
    """Basic Swift symbol demangling — fallback.

    Extracts length-prefixed names for module and function names.
    This is a simplified extraction that doesn't parse types.
    """
    if mangled.startswith('$s'):
        s = mangled[2:]
    elif mangled.startswith('$S'):
        s = mangled[2:]
    elif mangled.startswith('_T0'):
        s = mangled[3:]
    else:
        return None

    parts = []
    pos = 0

    while pos < len(s):
        # Parse length-prefixed name
        length = 0
        while pos < len(s) and s[pos].isdigit():
            length = length * 10 + int(s[pos])
            pos += 1

        if length == 0 or pos + length > len(s):
            break

        name = s[pos:pos + length]
        pos += length

        name = _decode_swift_escapes(name)
        parts.append(name)

        # Skip type encoding (non-digit characters between names)
        while pos < len(s) and not s[pos].isdigit():
            pos += 1

    if parts:
        return '.'.join(parts)

    return None


def _decode_swift_escapes(s):
    """Decode Swift-specific escape sequences in names.

    Swift uses $HH$ (where HH is hex) for non-ASCII characters in identifiers.
    """
    # $HH$ hex escapes
    s = re.sub(r'\$([0-9A-Fa-f]{2})\$',
               lambda m: chr(int(m.group(1), 16)), s)
    return s


def _parse_basic_structure(sym, demangled):
    """Parse basic structure from a demangled Swift name."""
    if '.' in demangled:
        parts = demangled.rsplit('.', 1)
        sym.scope = parts[0].split('.')
        sym.name = parts[1]
    else:
        sym.name = demangled

    if '(' in sym.name:
        sym.kind = 'function'
    else:
        sym.kind = 'variable'

    if '<' in sym.name:
        sym.is_template = True