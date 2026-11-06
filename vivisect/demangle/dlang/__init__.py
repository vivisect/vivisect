"""
vivisect.demangle.dlang - D language symbol demangling (_D prefix).

D mangling uses _D prefix followed by length-prefixed names and type codes.

Reference:
    - LLVM DLangDemangle.cpp
    - D ABI documentation (https://dlang.org/spec/abi.html#name_mangling)
"""

import logging

from vivisect.demangle.common import DemangledSymbol, normalize_name

logger = logging.getLogger(__name__)

__all__ = ["demangle_d"]


def demangle_d(mangled, structured=False):
    """Demangle a D language mangled symbol (_D prefix)."""
    original = mangled
    mangled = normalize_name(mangled)

    demangled = None
    parse_warnings = []

    try:
        parser = _DParser(mangled)
        demangled = parser.parse()
        parse_warnings = parser.warnings
    except Exception as e:
        logger.debug("D parser failed for %r: %r", mangled, e)
        parse_warnings.append("parser error: %r" % e)

    if demangled is None or demangled == mangled or not demangled:
        if structured:
            return DemangledSymbol(
                format="d",
                full_name=original,
                name=original,
                original_mangled=original,
                parse_warnings=parse_warnings or ["unable to demangle"],
            )
        return original

    if not structured:
        return demangled

    sym = DemangledSymbol(
        format="d",
        full_name=demangled,
        original_mangled=original,
        parse_warnings=parse_warnings,
    )
    _parse_basic_structure(sym, demangled)
    return sym


class _DParser:
    """Parser for D language mangled symbols."""

    TYPE_MAP = {
        "v": "void",
        "b": "bool",
        "y": "byte",
        "g": "ubyte",
        "h": "short",
        "t": "ushort",
        "i": "int",
        "j": "uint",
        "k": "long",
        "m": "ulong",
        "l": "real",
        "f": "float",
        "d": "double",
        "e": "real",
        "c": "ifloat",
        "q": "idouble",
        "r": "ireal",
        "p": "creal",
        "a": "char",
        "u": "wchar",
        "w": "dchar",
        "s": "string",
        "o": "wstring",
        "x": "dstring",
        "n": "char[]",
        "z": "void",
    }

    def __init__(self, mangled):
        self.mangled = mangled
        self.pos = 0
        self.warnings = []

    def _peek(self, offset=0):
        idx = self.pos + offset
        if idx >= len(self.mangled):
            return "\x00"
        return self.mangled[idx]

    def _next(self):
        if self.pos >= len(self.mangled):
            raise ValueError("unexpected end of input")
        ch = self.mangled[self.pos]
        self.pos += 1
        return ch

    def parse(self):
        if not self.mangled.startswith("_D"):
            raise ValueError("D symbols must start with _D")
        self.pos = 2

        result = self._parse_mangled_name()
        return result

    def _parse_mangled_name(self):
        """Parse <mangled-name> ::= <number> <name> <type>"""
        name_parts = []
        while self._peek().isdigit():
            length = self._parse_number()
            if length == 0 or self.pos + length > len(self.mangled):
                break
            name = self.mangled[self.pos : self.pos + length]
            self.pos += length
            name_parts.append(name)

        name = ".".join(name_parts) if name_parts else self.mangled[2:]

        if not self._at_end():
            type_str = self._parse_type()
            if type_str:
                if type_str.startswith("("):
                    return "%s%s" % (name, type_str)
                else:
                    return "%s %s" % (type_str, name)

        return name

    def _parse_number(self):
        result = 0
        while self._peek().isdigit():
            result = result * 10 + int(self._next())
        return result

    def _parse_type(self):
        ch = self._peek()

        if ch in self.TYPE_MAP:
            self._next()
            return self.TYPE_MAP[ch]

        if ch == "P":
            self._next()
            inner = self._parse_type()
            return "%s*" % inner

        if ch == "A":
            self._next()
            inner = self._parse_type()
            return "%s[]" % inner

        if ch == "G":
            self._next()
            n = self._parse_number()
            inner = self._parse_type()
            return "%s[%d]" % (inner, n)

        if ch == "F":
            self._next()
            params = []
            while self._peek() != "Z" and self._peek() != "\x00":
                params.append(self._parse_type())
            if self._peek() == "Z":
                self._next()
            return "(%s)" % ", ".join(params)

        if ch.isdigit():
            length = self._parse_number()
            if length > 0 and self.pos + length <= len(self.mangled):
                name = self.mangled[self.pos : self.pos + length]
                self.pos += length
                return name

        self._next()
        return "?%s" % ch

    def _at_end(self):
        return self.pos >= len(self.mangled)


def _parse_basic_structure(sym, demangled):
    if "." in demangled:
        parts = demangled.rsplit(".", 1)
        sym.scope = parts[0].split(".")
        sym.name = parts[1]
    else:
        sym.name = demangled
    sym.kind = "function" if "(" in sym.name else "variable"
