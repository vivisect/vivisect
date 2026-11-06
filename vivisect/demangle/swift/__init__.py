"""
vivisect.demangle.swift - Swift symbol demangling ($s / _T0 / $S prefix).

Swift mangling is complex. This implementation handles common patterns
and falls back gracefully for unsupported symbols.

Reference:
    - Swift mangling specification (swift-mangling.rst)
    - LLVM SwiftDemangle.cpp
"""

import re
import logging

from vivisect.demangle.common import DemangledSymbol, normalize_name

logger = logging.getLogger(__name__)

__all__ = ["demangle_swift"]


def demangle_swift(mangled, structured=False):
    """Demangle a Swift mangled symbol ($s / _T0 / $S prefix)."""
    original = mangled
    mangled = normalize_name(mangled)

    demangled = None
    parse_warnings = []

    try:
        demangled = _demangle_swift_basic(mangled)
        if demangled and demangled != mangled:
            parse_warnings = ["basic Swift demangling (not full parser)"]
        else:
            demangled = None
    except Exception as e:
        logger.debug("Swift parser failed for %r: %r", mangled, e)
        parse_warnings.append("parser error: %r" % e)

    if demangled is None or not demangled:
        if structured:
            return DemangledSymbol(
                format="swift",
                full_name=original,
                name=original,
                original_mangled=original,
                parse_warnings=parse_warnings or ["unable to demangle"],
            )
        return original

    if not structured:
        return demangled

    sym = DemangledSymbol(
        format="swift",
        full_name=demangled,
        original_mangled=original,
        parse_warnings=parse_warnings,
    )
    _parse_basic_structure(sym, demangled)
    return sym


def _demangle_swift_basic(mangled):
    """Basic Swift symbol demangling.

    Swift symbols use length-prefixed names for modules and functions.
    Pattern: $s<module_length><module><func_length><func>...
    """
    if mangled.startswith("$s"):
        s = mangled[2:]
    elif mangled.startswith("$S"):
        s = mangled[2:]
    elif mangled.startswith("_T0"):
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

        name = s[pos : pos + length]
        pos += length

        name = _decode_swift_escapes(name)
        parts.append(name)

        # Skip type encoding (non-digit characters between names)
        while pos < len(s) and not s[pos].isdigit():
            pos += 1

    if parts:
        return ".".join(parts)

    return None


def _decode_swift_escapes(s):
    """Decode Swift-specific escape sequences in names."""
    s = re.sub(r"\$([0-9A-Fa-f]{2})\$", lambda m: chr(int(m.group(1), 16)), s)
    return s


def _parse_basic_structure(sym, demangled):
    if "." in demangled:
        parts = demangled.rsplit(".", 1)
        sym.scope = parts[0].split(".")
        sym.name = parts[1]
    else:
        sym.name = demangled
    sym.kind = "function"
