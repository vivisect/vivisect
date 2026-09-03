"""
vivisect.demangle.rust - Rust symbol demangling.

Implements both legacy (_Z prefix, with $ escape decoding) and v0
(_R prefix, RFC 2603) Rust mangling schemes.

Full RFC 2603 v0 support includes:
    - Crate paths (C), nested paths (N), impl paths (M, X, Y)
    - Generic arguments (I) with lifetimes (L), const generics (K), types
    - Function types (F) with binders (G), unsafe (U), ABI (K/C), params, return
    - Dyn types (D) with trait bounds, associated types (p), lifetime
    - References (R, Q) with lifetimes
    - Pointers (P, O) - const/mut
    - Arrays (A) with const length, slices (S)
    - Tuples (T) with single-element trailing comma
    - Back-references (B) with byte-offset resolution
    - Lifetimes with depth tracking and for<> binders
    - Const generics: bool, char, signed/unsigned integers, placeholder
    - Punycode (RFC 3492) identifier decoding
    - Namespace rendering: closures (::C), shims (::S), etc.
    - Vendor suffix stripping (.llvm.<hash>, etc.)
    - Instantiating crate suffix

References:
    - RFC 2603 (Rust v0 mangling)
    - rustc-demangle crate
    - LLVM RustDemangle.cpp
"""

import logging
import re

from vivisect.demangle.common import DemangledSymbol, normalize_name

logger = logging.getLogger(__name__)

__all__ = ['demangle_rust']


def demangle_rust(mangled, structured=False):
    """
    Demangle a Rust mangled symbol.

    Handles both v0 (_R prefix, RFC 2603) and legacy (_Z prefix with
    Rust-specific $ escape sequences).
    """
    original = mangled
    mangled = normalize_name(mangled)

    demangled = None
    parse_warnings = []

    if mangled.startswith('_R'):
        try:
            demangled = _demangle_rust_v0(mangled)
        except Exception as e:
            logger.debug('Rust v0 parser failed for %r: %r', mangled, e)
            parse_warnings.append('v0 parser error: %r' % e)
    elif mangled.startswith('_Z') or mangled.startswith('__Z'):
        try:
            demangled = _demangle_rust_legacy(mangled)
        except Exception as e:
            logger.debug('Rust legacy parser failed for %r: %r', mangled, e)
            parse_warnings.append('legacy parser error: %r' % e)

    if demangled is None or demangled == mangled or not demangled:
        if structured:
            return DemangledSymbol(
                format='rust',
                full_name=original,
                name=original,
                original_mangled=original,
                parse_warnings=parse_warnings or ['unable to demangle'],
            )
        return original

    if not structured:
        return demangled

    sym = DemangledSymbol(
        format='rust',
        full_name=demangled,
        original_mangled=original,
        parse_warnings=parse_warnings,
    )
    _parse_basic_structure(sym, demangled)
    return sym


# ---------------------------------------------------------------------------
# Rust v0 demangling (RFC 2603) - Full implementation
# ---------------------------------------------------------------------------

# Basic type tags -> Rust type names (RFC 2603 §2.3)
_BASIC_TYPES = {
    'a': 'i8', 'b': 'bool', 'c': 'char', 'd': 'f64',
    'e': 'str', 'f': 'f32', 'h': 'u8', 'i': 'isize',
    'j': 'usize', 'l': 'i32', 'm': 'u32', 'n': 'i128',
    'o': 'u128', 's': 'i16', 't': 'u16', 'u': '()',
    'v': '...', 'x': 'i64', 'y': 'u64', 'z': '!',
    'p': '_',
}

# Unsigned integer type tags for const generics
_CONST_UINT_TYPES = {'h', 't', 'm', 'y', 'o', 'j'}
# Signed integer type tags for const generics
_CONST_INT_TYPES = {'a', 's', 'l', 'x', 'n', 'i'}

# Namespace special names (uppercase only)
_NS_NAMES = {
    'C': 'closure',
    'S': 'shim',
}


def _demangle_rust_v0(mangled):
    """Demangle a Rust v0 symbol (_R prefix)."""
    s = mangled[2:]  # skip _R

    # Strip vendor suffix (e.g. .llvm.<hash>)
    dot_pos = s.find('.')
    if dot_pos > 0:
        s = s[:dot_pos]

    parser = _RustV0Parser(s)
    result = parser._parse_path(in_value=True)

    # Check for instantiating crate suffix (another path starting with uppercase)
    # This is a second path that follows the main path — we skip it
    # (it's the crate that instantiated the symbol, not part of the name)
    if parser.pos < len(s) and s[parser.pos].isupper():
        try:
            parser._parse_path(in_value=False)
        except Exception:
            pass

    return result


class _RustV0Parser:
    """Recursive descent parser for Rust v0 mangling (RFC 2603).

    Implements the full grammar: paths, types, generic args, lifetimes,
    const generics, function types, dyn types, back-references, and
    Punycode identifier decoding.
    """

    def __init__(self, s):
        self.s = s
        self.pos = 0
        self.warnings = []
        self._bound_lifetime_depth = 0

    # --- Low-level helpers ---

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
        """Consume a single character if it matches. Returns True/False."""
        if self._peek() == ch:
            self.pos += 1
            return True
        return False

    # --- Number parsing ---

    def _parse_decimal(self):
        """Parse a decimal number (for ident lengths)."""
        result = 0
        while self._peek().isdigit():
            result = result * 10 + int(self._next())
        return result

    def _parse_digit_62(self):
        """Parse a single base-62 digit. Returns int value.

        0-9 = 0-9, a-z = 10-35, A-Z = 36-61
        """
        ch = self._next()
        if ch.isdigit():
            return int(ch)
        elif ch.islower():
            return 10 + (ord(ch) - ord('a'))
        elif ch.isupper():
            return 10 + 26 + (ord(ch) - ord('A'))
        else:
            raise ValueError('invalid base-62 digit: %r' % ch)

    def _parse_integer_62(self):
        """Parse a base-62 integer terminated by '_'.

        Returns the decoded value. A lone '_' means 0.
        Otherwise the value is (decoded) + 1.
        """
        if self._eat('_'):
            return 0
        x = 0
        while not self._eat('_'):
            d = self._parse_digit_62()
            x = x * 62 + d
        return x + 1

    def _parse_opt_integer_62(self, tag):
        """Parse an optional base-62 integer prefixed by a tag character.

        If tag is present, returns (value + 1). If not, returns 0.
        """
        if not self._eat(tag):
            return 0
        return self._parse_integer_62() + 1

    def _parse_disambiguator(self):
        """Parse an optional disambiguator (s prefix + base-62 number)."""
        return self._parse_opt_integer_62('s')

    def _parse_hex_nibbles(self):
        """Parse hex nibbles terminated by '_'. Returns the hex string."""
        start = self.pos
        while True:
            ch = self._next()
            if ch in '0123456789abcdef':
                continue
            elif ch == '_':
                break
            else:
                raise ValueError('invalid hex nibble: %r' % ch)
        return self.s[start:self.pos - 1]

    # --- Identifier parsing (with Punycode support) ---

    def _parse_ident(self):
        """Parse an identifier with optional Punycode encoding.

        Grammar: [u] <decimal-number> [_] <bytes>
        If 'u' prefix is present, the identifier is Punycode-encoded (RFC 3492).
        """
        is_punycode = self._eat('u')

        length = self._parse_decimal()
        if length == 0:
            return ''

        # Optional underscore separator after length
        self._eat('_')

        if self.pos + length > len(self.s):
            raise ValueError('ident length %d exceeds input at pos %d' % (length, self.pos))

        name = self.s[self.pos:self.pos + length]
        self.pos += length

        if is_punycode:
            name = _punycode_decode_ident(name)

        # Decode $ escape sequences (shouldn't appear in v0 but be safe)
        name = _decode_rust_escapes(name)

        return name

    # --- Path parsing ---

    def _parse_path(self, in_value=False):
        """Parse a path (RFC 2603 §2.1).

        Grammar:
            C = crate          -> C <disambiguator> <ident>
            N = nested         -> N <namespace> <path> <disambiguator> <ident>
            M = impl           -> M <disambiguator> <path> <type>
            X = impl-trait     -> X <disambiguator> <path> <type> <path>
            Y = trait-def      -> Y <type> <path>
            I = generic        -> I <path> {<generic-arg>} E
            B = backref        -> B <base-62-number>

        The in_value parameter controls whether `::` is inserted before
        generic angle brackets. Top-level paths use in_value=True.
        """
        ch = self._next()

        if ch == 'C':
            self._parse_disambiguator()
            return self._parse_ident()

        if ch == 'N':
            ns = self._next()
            if not ns.isalpha():
                raise ValueError('invalid namespace: %r' % ns)
            path = self._parse_path(in_value=in_value)
            dis = self._parse_disambiguator()
            name = self._parse_ident()

            if ns.islower():
                # Type namespace: just path::name (no decoration)
                if name:
                    return '%s::%s' % (path, name)
                return path
            else:
                # Value namespace: path::{ns_name:name#dis} or path::{ns_name#dis}
                ns_name = _NS_NAMES.get(ns, ns)
                if name:
                    return '%s::{%s:%s#%d}' % (path, ns_name, name, dis)
                else:
                    return '%s::{%s#%d}' % (path, ns_name, dis)

        if ch == 'M':
            self._parse_disambiguator()
            impl_path = self._parse_path()
            ty = self._parse_type()
            return '<%s>' % ty

        if ch == 'X':
            self._parse_disambiguator()
            impl_path = self._parse_path()
            ty = self._parse_type()
            trait_path = self._parse_path()
            return '<%s as %s>' % (ty, trait_path)

        if ch == 'Y':
            ty = self._parse_type()
            trait_path = self._parse_path()
            return '<%s as %s>' % (ty, trait_path)

        if ch == 'I':
            path = self._parse_path(in_value=in_value)
            args = self._parse_generic_args()
            # Top-level (in_value=True) gets `::` before `<` per RFC 2603
            sep = '::' if in_value else ''
            return '%s%s<%s>' % (path, sep, args)

        if ch == 'B':
            idx = self._parse_integer_62()
            # Back-reference: save and restore position
            # The backref index is a byte offset (0-based from start of path)
            save_pos = self.pos
            self.pos = idx
            result = self._parse_path(in_value=in_value)
            self.pos = save_pos
            return result

        raise ValueError('invalid path tag: %r at pos %d' % (ch, self.pos - 1))

    def _parse_generic_args(self):
        """Parse generic arguments (RFC 2603 §2.2).

        Grammar: {<generic-arg>} E
        Generic arg = L <lifetime> | K <const> | <type>
        """
        args = []
        while not self._eat('E'):
            if self.pos >= len(self.s):
                raise ValueError('unexpected end of input in generic args')
            arg = self._parse_generic_arg()
            args.append(arg)
        return ', '.join(args)

    def _parse_generic_arg(self):
        """Parse a single generic argument."""
        if self._eat('L'):
            lt = self._parse_integer_62()
            return self._format_lifetime(lt)
        if self._eat('K'):
            return self._parse_const()
        return self._parse_type()

    # --- Type parsing ---

    def _parse_type(self):
        """Parse a type (RFC 2603 §2.3).

        Grammar:
            Basic types (single char)
            R = &<type>         (shared reference, optional lifetime)
            Q = &mut <type>     (mutable reference, optional lifetime)
            P = *const <type>   (const pointer)
            O = *mut <type>     (mut pointer)
            A = [<type>; <const>]
            S = [<type>]        (slice)
            T = ({<type>}+) E   (tuple)
            F = fn(...) -> ...  (function type)
            D = dyn ...         (dyn trait type)
            B = backref
            Path types (C, N, M, X, Y, I)
        """
        ch = self._next()

        # Basic types
        if ch in _BASIC_TYPES:
            return _BASIC_TYPES[ch]

        # References
        if ch == 'R':
            lifetime = ''
            if self._eat('L'):
                lt = self._parse_integer_62()
                if lt != 0:
                    lifetime = self._format_lifetime(lt) + ' '
            ty = self._parse_type()
            return '&%s%s' % (lifetime, ty)

        if ch == 'Q':
            lifetime = ''
            if self._eat('L'):
                lt = self._parse_integer_62()
                if lt != 0:
                    lifetime = self._format_lifetime(lt) + ' '
            ty = self._parse_type()
            return '&mut %s%s' % (lifetime, ty)

        # Pointers
        if ch == 'P':
            ty = self._parse_type()
            return '*const %s' % ty

        if ch == 'O':
            ty = self._parse_type()
            return '*mut %s' % ty

        # Arrays and slices
        if ch == 'A':
            ty = self._parse_type()
            const = self._parse_const()
            return '[%s; %s]' % (ty, const)

        if ch == 'S':
            ty = self._parse_type()
            return '[%s]' % ty

        # Tuples
        if ch == 'T':
            args = []
            while not self._eat('E'):
                if self.pos >= len(self.s):
                    raise ValueError('unexpected end of input in tuple')
                args.append(self._parse_type())
            if len(args) == 1:
                return '(%s,)' % args[0]
            return '(%s)' % ', '.join(args)

        # Function types
        if ch == 'F':
            return self._parse_fn_type()

        # Dyn trait types
        if ch == 'D':
            return self._parse_dyn_type()

        # Back-reference
        if ch == 'B':
            idx = self._parse_integer_62()
            save_pos = self.pos
            self.pos = idx
            result = self._parse_type()
            self.pos = save_pos
            return result

        # Path types - back up and parse as path
        self.pos -= 1
        return self._parse_path()

    def _parse_fn_type(self):
        """Parse a function type (RFC 2603 §2.3.F).

        Grammar: F [G <bound-lifetimes>] [U] [K <abi>] {<type>} E <type>
        The return type is omitted if it's the unit type 'u'.
        """
        # Optional binder (G prefix + base-62 count of bound lifetimes)
        bound_lifetimes = self._parse_opt_integer_62('G')

        prefix = ''
        if bound_lifetimes > 0:
            lts = []
            for i in range(bound_lifetimes):
                self._bound_lifetime_depth += 1
                lts.append(self._format_lifetime(1))
            prefix = 'for<%s> ' % ', '.join(lts)
            # Note: bound_lifetime_depth stays incremented during type parsing,
            # then we decrement after the fn type is fully parsed

        # Optional unsafe
        is_unsafe = self._eat('U')

        # Optional ABI
        abi = ''
        if self._eat('K'):
            if self._eat('C'):
                abi = 'extern "C" '
            else:
                # Custom ABI - read as ident
                abi_ident = self._parse_ident()
                if abi_ident:
                    abi = 'extern "%s" ' % abi_ident

        fn_prefix = prefix
        if is_unsafe:
            fn_prefix += 'unsafe '
        fn_prefix += abi
        fn_prefix += 'fn('

        # Parameters
        params = []
        while not self._eat('E'):
            if self.pos >= len(self.s):
                raise ValueError('unexpected end of input in fn params')
            params.append(self._parse_type())

        # Return type
        ret = self._parse_type()
        # Decrement bound lifetime depth after the fn type is parsed
        self._bound_lifetime_depth -= bound_lifetimes

        if ret == '()':
            return '%s%s)' % (fn_prefix, ', '.join(params))
        return '%s%s) -> %s' % (fn_prefix, ', '.join(params), ret)

    def _parse_dyn_type(self):
        """Parse a dyn trait type (RFC 2603 §2.3.D).

        Grammar: D [G <bound-lifetimes>] {<dyn-trait>} E L <lifetime>
        dyn-trait = <path> {p <ident> <type>}
        """
        # Optional binder
        bound_lifetimes = self._parse_opt_integer_62('G')

        prefix = 'dyn '
        if bound_lifetimes > 0:
            lts = []
            for i in range(bound_lifetimes):
                self._bound_lifetime_depth += 1
                lts.append(self._format_lifetime(1))
            prefix = 'for<%s> dyn ' % ', '.join(lts)
            # bound_lifetime_depth stays incremented during trait parsing

        # Parse dyn traits
        traits = []
        while not self._eat('E'):
            if self.pos >= len(self.s):
                raise ValueError('unexpected end of input in dyn traits')
            traits.append(self._parse_dyn_trait())

        # Lifetime
        lifetime = ''
        if self._eat('L'):
            lt = self._parse_integer_62()
            if lt != 0:
                lifetime = ' + ' + self._format_lifetime(lt)

        # Decrement bound lifetime depth after dyn type is parsed
        self._bound_lifetime_depth -= bound_lifetimes

        return '%s%s%s' % (prefix, ' + '.join(traits), lifetime)

    def _parse_dyn_trait(self):
        """Parse a single dyn trait (RFC 2603 §2.3.D).

        Grammar: <path> {p <ident> <type>}
        The path may have open generics.
        """
        path = self._parse_path()

        # Parse associated type bindings (p prefix)
        bindings = []
        while self._eat('p'):
            name = self._parse_ident()
            ty = self._parse_type()
            bindings.append('%s = %s' % (name, ty))

        if bindings:
            return '%s<%s>' % (path, ', '.join(bindings))
        return path

    # --- Const parsing ---

    def _parse_const(self):
        """Parse a const generic value (RFC 2603 §2.2.K).

        Grammar: K <const>
        const = B <backref> | <type-tag> [n] <hex-nibbles>_
                p = placeholder (_)
        """
        if self._eat('B'):
            idx = self._parse_integer_62()
            save_pos = self.pos
            self.pos = idx
            result = self._parse_const()
            self.pos = save_pos
            return result

        ty_tag = self._next()

        if ty_tag == 'p':
            return '_'

        if ty_tag == 'b':
            # bool
            hex_val = self._parse_hex_nibbles()
            if hex_val == '0':
                return 'false'
            elif hex_val == '1':
                return 'true'
            else:
                raise ValueError('invalid bool const: 0x%s' % hex_val)

        if ty_tag == 'c':
            # char
            hex_val = self._parse_hex_nibbles()
            if len(hex_val) > 8:
                raise ValueError('char const too long: 0x%s' % hex_val)
            char_val = int(hex_val, 16)
            return repr(chr(char_val))

        if ty_tag in _CONST_UINT_TYPES:
            # Unsigned integer
            hex_val = self._parse_hex_nibbles()
            if len(hex_val) > 16:
                return '0x%s' % hex_val
            return str(int(hex_val, 16))

        if ty_tag in _CONST_INT_TYPES:
            # Signed integer
            negative = self._eat('n')
            hex_val = self._parse_hex_nibbles()
            if len(hex_val) > 16:
                val = '0x%s' % hex_val
            else:
                val = str(int(hex_val, 16))
            return '-%s' % val if negative else val

        raise ValueError('invalid const type tag: %r' % ty_tag)

    # --- Lifetime formatting ---

    def _format_lifetime(self, index):
        """Format a lifetime from a de Bruijn index.

        RFC 2603 uses de Bruijn indexing for lifetimes:
            - index 0 = anonymous lifetime ('_)
            - index N > 0 = the Nth bound lifetime, counting from the
              innermost binder outward

        The bound_lifetime_depth tracks how many binders we're inside.
        At depth D, lifetime index K (K > 0) refers to the binder at
        level D - K. If D - K == 0, it's the innermost -> 'a.
        If D - K == 1, it's the next outer -> 'b, etc.
        """
        if index == 0:
            return "'_"

        depth = self._bound_lifetime_depth - index
        if depth < 0:
            # Lifetime references outside any binder — graceful fallback
            return "'_"
        if depth < 26:
            return "'%s" % chr(ord('a') + depth)
        return "'_%d" % depth


# ---------------------------------------------------------------------------
# Punycode decoding (RFC 3492)
# ---------------------------------------------------------------------------

def _punycode_decode_ident(encoded):
    """Decode a Punycode-encoded Rust identifier.

    The identifier may contain a '_' separator between the ASCII prefix
    and the Punycode suffix. If there's no '_', the entire string is
    Punycode.
    """
    # Split on the last underscore
    if '_' in encoded:
        idx = encoded.rfind('_')
        ascii_part = encoded[:idx]
        punycode_part = encoded[idx + 1:]
    else:
        ascii_part = ''
        punycode_part = encoded

    if not punycode_part:
        return ascii_part

    try:
        decoded = _punycode_decode(ascii_part, punycode_part)
        return decoded
    except Exception:
        # Fallback: show as punycode{...}
        if ascii_part:
            return 'punycode{%s-%s}' % (ascii_part, punycode_part)
        return 'punycode{%s}' % punycode_part


def _punycode_decode(ascii_prefix, punycode_str):
    """Decode a Punycode string (RFC 3492).

    Parameters:
        ascii_prefix: the basic (ASCII) code points that appear before
                      the Punycode suffix
        punycode_str: the Punycode-encoded suffix (base-36 variable-length
                      integers)
    """
    output = list(ascii_prefix)
    base = 36
    t_min = 1
    t_max = 26
    skew = 38
    damp = 700
    bias = 72
    n = 0x80  # initial value for code point
    i = 0
    idx = 0  # position in punycode_str

    output_len = len(output)

    while idx < len(punycode_str):
        old_i = i
        w = 1
        k = base
        while True:
            if idx >= len(punycode_str):
                raise ValueError('punycode: premature end of input')
            ch = punycode_str[idx]
            idx += 1

            # In standard Punycode, digits are a-z=0-25, 0-5=26-35
            if 'a' <= ch <= 'z':
                digit = ord(ch) - ord('a')
            elif '0' <= ch <= '9':
                digit = 26 + (ord(ch) - ord('0'))
            else:
                raise ValueError('punycode: invalid char %r' % ch)

            i += digit * w
            t = min(max(k - bias, t_min), t_max)
            if digit < t:
                break
            w *= (base - t)
            k += base

        output_len += 1
        delta = i - old_i
        delta = delta // output_len if output_len > 0 else delta

        # Bias adaptation
        if old_i == 0:
            delta //= damp
        else:
            delta //= 2

        delta += delta // output_len
        k = 0
        while delta > ((base - t_min) * t_max) // 2:
            delta = delta // (base - t_min)
            k += base
        bias = k + ((base - t_min + 1) * delta) // (delta + skew)

        n += i // output_len
        i = i % output_len

        # Insert code point n at position i
        output.insert(i, chr(n))
        i += 1

    return ''.join(output)


# ---------------------------------------------------------------------------
# Rust legacy demangling
# ---------------------------------------------------------------------------

def _demangle_rust_legacy(mangled):
    """Demangle a legacy Rust symbol (_Z prefix with $ escapes)."""
    try:
        from vivisect.demangle.itanium import demangle_itanium
        result = demangle_itanium(mangled)
        if result and result != mangled:
            result = _decode_rust_escapes(result)
            result = re.sub(r'\.h[0-9a-f]+$', '', result)
            return result
    except Exception as e:
        logger.debug('Rust legacy Itanium fallback failed: %r', e)

    s = mangled
    if s.startswith('_Z'):
        s = s[2:]
    elif s.startswith('__Z'):
        s = s[3:]
    s = _decode_rust_escapes(s)
    return s


def _decode_rust_escapes(s):
    """Decode Rust-specific $ escape sequences."""
    s = s.replace('$SP$', '@')
    s = s.replace('$BP$', '*')
    s = s.replace('$RF$', '&')
    s = s.replace('$LT$', '<')
    s = s.replace('$GT$', '>')
    s = s.replace('$LP$', '(')
    s = s.replace('$RP$', ')')
    s = s.replace('$C$', ',')
    s = s.replace('$u7e$', '~')
    s = s.replace('$u20$', ' ')
    s = s.replace('$u27$', "'")
    s = s.replace('$u3d$', '=')
    s = s.replace('$u5b$', '[')
    s = s.replace('$u5d$', ']')
    s = s.replace('$u7b$', '{')
    s = s.replace('$u7d$', '}')
    s = s.replace('$u22$', '"')
    s = s.replace('$u3c$', '<')
    s = s.replace('$u3e$', '>')
    s = s.replace('$u3b$', ';')
    s = s.replace('$u2e$', '.')
    s = s.replace('$u2d$', '-')
    s = s.replace('$u2b$', '+')
    s = s.replace('$u2f$', '/')
    s = s.replace('$u5f$', '_')
    s = s.replace('$u21$', '!')
    s = s.replace('$u23$', '#')
    s = s.replace('$u24$', '$')
    s = s.replace('$u25$', '%')
    s = s.replace('$u26$', '&')
    s = s.replace('$u28$', '(')
    s = s.replace('$u29$', ')')
    s = s.replace('$u2a$', '*')
    s = s.replace('$u2c$', ',')
    s = s.replace('$u3a$', ':')
    s = s.replace('$u3f$', '?')
    s = s.replace('$u40$', '@')
    s = s.replace('$u5c$', '\\\\')
    s = s.replace('$u7c$', '|')
    s = s.replace('$u60$', '`')
    s = s.replace('$u5e$', '^')
    # Generic $uXX$ hex escape (must be last)
    s = re.sub(r'\$u([0-9a-fA-F]{2})\$',
               lambda m: chr(int(m.group(1), 16)), s)
    return s


# ---------------------------------------------------------------------------
# Structured output helper
# ---------------------------------------------------------------------------

def _parse_basic_structure(sym, demangled):
    """Parse basic structure from a demangled Rust name."""
    if '::' in demangled:
        parts = demangled.rsplit('::', 1)
        sym.scope = parts[0].split('::')
        sym.name = parts[1]
    else:
        sym.name = demangled
    if '<' in sym.name:
        sym.is_template = True
    sym.kind = 'function'