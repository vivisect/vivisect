"""
vivisect.demangle.rust - Rust symbol demangling.

Implements both legacy (_Z prefix, with $ escape decoding) and v0
(_R prefix, RFC 2603) Rust mangling schemes.

Reference:
    - RFC 2603 (Rust v0 mangling)
    - rustc-demangle crate
"""

import logging
import re

from vivisect.demangle.common import DemangledSymbol, normalize_name

logger = logging.getLogger(__name__)

__all__ = ["demangle_rust"]


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

    if mangled.startswith("_R"):
        try:
            demangled = _demangle_rust_v0(mangled)
        except Exception as e:
            logger.debug("Rust v0 parser failed for %r: %r", mangled, e)
            parse_warnings.append("v0 parser error: %r" % e)
    elif mangled.startswith("_Z") or mangled.startswith("__Z"):
        try:
            demangled = _demangle_rust_legacy(mangled)
        except Exception as e:
            logger.debug("Rust legacy parser failed for %r: %r", mangled, e)
            parse_warnings.append("legacy parser error: %r" % e)

    if demangled is None or demangled == mangled or not demangled:
        if structured:
            return DemangledSymbol(
                format="rust",
                full_name=original,
                name=original,
                original_mangled=original,
                parse_warnings=parse_warnings or ["unable to demangle"],
            )
        return original

    if not structured:
        return demangled

    sym = DemangledSymbol(
        format="rust",
        full_name=demangled,
        original_mangled=original,
        parse_warnings=parse_warnings,
    )
    _parse_basic_structure(sym, demangled)
    return sym


# --- Rust v0 demangling (RFC 2603) ---


def _demangle_rust_v0(mangled):
    """Demangle a Rust v0 symbol (_R prefix)."""
    s = mangled[2:]  # skip _R
    dot_pos = s.find(".")
    if dot_pos > 0:
        s = s[:dot_pos]
    parser = _RustV0Parser(s)
    return parser.parse()


class _RustV0Parser:
    """Recursive descent parser for Rust v0 mangling (RFC 2603)."""

    BASIC_TYPES = {
        "a": "i8",
        "b": "bool",
        "c": "char",
        "d": "f64",
        "e": "str",
        "f": "f32",
        "h": "u8",
        "i": "isize",
        "j": "usize",
        "l": "i32",
        "m": "u32",
        "n": "i128",
        "o": "u128",
        "s": "i16",
        "t": "u16",
        "u": "()",
        "v": "...",
        "x": "i64",
        "y": "u64",
        "z": "!",
        "p": "_",
    }

    def __init__(self, s):
        self.s = s
        self.pos = 0
        self.warnings = []
        self._substs = []

    def _peek(self, offset=0):
        idx = self.pos + offset
        if idx >= len(self.s):
            return "\x00"
        return self.s[idx]

    def _next(self):
        if self.pos >= len(self.s):
            raise ValueError("unexpected end of input")
        ch = self.s[self.pos]
        self.pos += 1
        return ch

    def parse(self):
        result = self._parse_path()
        return result

    def _parse_path(self):
        ch = self._peek()

        if ch == "N":
            self._next()
            ns = self._next()
            self._parse_disambiguator()
            path = self._parse_path()
            name = self._parse_ident()
            return "%s::%s" % (path, name)

        if ch == "I":
            self._next()
            path = self._parse_path()
            args = self._parse_generic_args()
            return "%s<%s>" % (path, args)

        if ch == "B":
            self._next()
            idx = self._parse_base62()
            if idx < len(self._substs):
                return self._substs[idx]
            return "<backref:%d>" % idx

        if ch == "C":
            self._next()
            self._parse_disambiguator()
            name = self._parse_ident()
            return name

        if ch == "M":
            self._next()
            self._parse_disambiguator()
            ty = self._parse_type()
            return "<impl %s>" % ty

        name = self._parse_ident()
        return name

    def _parse_ident(self):
        length = self._parse_number()
        if length == 0:
            return ""
        if self._peek() == "_":
            self._next()
        if self.pos + length > len(self.s):
            raise ValueError("ident length exceeds input")
        name = self.s[self.pos : self.pos + length]
        self.pos += length

        # Decode $ escape sequences
        name = name.replace("$SP$", "@")
        name = name.replace("$BP$", "*")
        name = name.replace("$RF$", "&")
        name = name.replace("$LT$", "<")
        name = name.replace("$GT$", ">")
        name = name.replace("$LP$", "(")
        name = name.replace("$RP$", ")")
        name = name.replace("$C$", ",")
        name = re.sub(
            r"\$u([0-9a-fA-F]{2})\$", lambda m: chr(int(m.group(1), 16)), name
        )
        return name

    def _parse_number(self):
        result = 0
        while self._peek().isdigit():
            result = result * 10 + int(self._next())
        return result

    def _parse_base62(self):
        chars = []
        while self._peek() != "_" and self._peek() != "\x00":
            chars.append(self._next())
        if self._peek() == "_":
            self._next()
        if not chars:
            return 0
        result = 0
        for c in chars:
            if c.isdigit():
                v = int(c) + 1
            elif c.islower():
                v = ord(c) - ord("a") + 11
            else:
                v = ord(c) - ord("A") + 37
            result = result * 62 + v
        return result - 1

    def _parse_disambiguator(self):
        if self._peek() == "s":
            self._next()
            return self._parse_number()
        return 0

    def _parse_generic_args(self):
        args = []
        while self._peek() != "E" and self._peek() != "\x00":
            ty = self._parse_type()
            args.append(ty)
        if self._peek() == "E":
            self._next()
        return ", ".join(args)

    def _parse_type(self):
        ch = self._peek()

        if ch in self.BASIC_TYPES:
            self._next()
            return self.BASIC_TYPES[ch]

        if ch == "A":
            self._next()
            ty = self._parse_type()
            n = self._parse_number()
            return "[%s; %d]" % (ty, n)

        if ch == "S":
            self._next()
            ty = self._parse_type()
            return "[%s]" % ty

        if ch == "R":
            self._next()
            ty = self._parse_type()
            return "&%s" % ty

        if ch == "Q":
            self._next()
            ty = self._parse_type()
            return "&mut %s" % ty

        if ch == "P":
            self._next()
            ty = self._parse_type()
            return "*const %s" % ty

        if ch == "O":
            self._next()
            ty = self._parse_type()
            return "*mut %s" % ty

        if ch == "T":
            self._next()
            args = []
            while self._peek() != "E" and self._peek() != "\x00":
                args.append(self._parse_type())
            if self._peek() == "E":
                self._next()
            return "(%s)" % ", ".join(args)

        if ch in ("C", "N", "M", "I", "B"):
            return self._parse_path()

        self._next()
        return "?%s" % ch


# --- Rust legacy demangling ---


def _demangle_rust_legacy(mangled):
    """Demangle a legacy Rust symbol (_Z prefix with $ escapes)."""
    try:
        from vivisect.demangle.itanium import demangle_itanium

        result = demangle_itanium(mangled)
        if result and result != mangled:
            result = _decode_rust_escapes(result)
            result = re.sub(r"\.h[0-9a-f]+$", "", result)
            return result
    except Exception as e:
        logger.debug("Rust legacy Itanium fallback failed: %r", e)

    s = mangled
    if s.startswith("_Z"):
        s = s[2:]
    elif s.startswith("__Z"):
        s = s[3:]
    s = _decode_rust_escapes(s)
    return s


def _decode_rust_escapes(s):
    s = s.replace("$SP$", "@")
    s = s.replace("$BP$", "*")
    s = s.replace("$RF$", "&")
    s = s.replace("$LT$", "<")
    s = s.replace("$GT$", ">")
    s = s.replace("$LP$", "(")
    s = s.replace("$RP$", ")")
    s = s.replace("$C$", ",")
    s = re.sub(r"\$u([0-9a-fA-F]{2})\$", lambda m: chr(int(m.group(1), 16)), s)
    return s


def _parse_basic_structure(sym, demangled):
    if "::" in demangled:
        parts = demangled.rsplit("::", 1)
        sym.scope = parts[0].split("::")
        sym.name = parts[1]
    else:
        sym.name = demangled
    if "<" in sym.name:
        sym.is_template = True
    sym.kind = "function"
