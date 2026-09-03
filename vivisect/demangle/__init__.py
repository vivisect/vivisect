"""
vivisect.demangle - Multi-format C++ symbol demangling library.

This package provides pure-Python demangling for all major compiler mangling
schemes:

    - Itanium C++ ABI  (GCC, Clang, ICC on Linux/macOS)   _Z...
    - MSVC C++ ABI     (Microsoft Visual C++)              ?...@@...
    - Rust            (legacy and v0)                      _Z...  /  _R...
    - D language                                           _D...
    - Swift                                               $s... / _T0... / $S...
    - Java/JNI                                            Java_...
    - Objective-C                                         _OBJC_...

The public API is :func:`demangle`, which auto-detects the mangling format
from the symbol prefix and returns the demangled string.  Pass
``structured=True`` to receive a :class:`DemangledSymbol` AST object that
exposes the parsed components (scope, name, template args, return type,
parameters, calling convention, access, etc.) for downstream analysis.

This library replaces the previous ``cxxfilt``-only implementation (which
was Itanium-only and broken on Windows) and the VivisectION ``demangle.py``
HTTP-to-demangler.com approach (which leaked symbols in cleartext and
required internet access).  It works fully offline with no native
dependencies.
"""

from vivisect.demangle.common import DemangledSymbol, DemangleError, normalize_name
from vivisect.demangle.itanium import demangle_itanium
from vivisect.demangle.msvc import demangle_msvc
from vivisect.demangle.rust import demangle_rust
from vivisect.demangle.dlang import demangle_d
from vivisect.demangle.swift import demangle_swift
from vivisect.demangle.jni import demangle_jni
from vivisect.demangle.objc import demangle_objc

__all__ = [
    'demangle', 'detect_format',
    'DemangledSymbol', 'DemangleError',
    'FORMAT_ITANIUM', 'FORMAT_MSVC', 'FORMAT_RUST', 'FORMAT_D',
    'FORMAT_SWIFT', 'FORMAT_JNI', 'FORMAT_OBJC', 'FORMAT_UNKNOWN',
]

FORMAT_ITANIUM = 'itanium'
FORMAT_MSVC = 'msvc'
FORMAT_RUST = 'rust'
FORMAT_D = 'd'
FORMAT_SWIFT = 'swift'
FORMAT_JNI = 'jni'
FORMAT_OBJC = 'objc'
FORMAT_UNKNOWN = 'unknown'

# Dispatch table mapping format name -> demangle function.
# Each function signature: demangle_xxx(mangled: str, structured: bool = False)
_DISPATCH = {
    FORMAT_ITANIUM: demangle_itanium,
    FORMAT_MSVC: demangle_msvc,
    FORMAT_RUST: demangle_rust,
    FORMAT_D: demangle_d,
    FORMAT_SWIFT: demangle_swift,
    FORMAT_JNI: demangle_jni,
    FORMAT_OBJC: demangle_objc,
}


def detect_format(mangled):
    """
    Identify the mangling format from the symbol prefix.

    Args:
        mangled (str): The mangled symbol string.

    Returns:
        str: One of the FORMAT_* constants.  Returns FORMAT_UNKNOWN if no
        known prefix is recognized.
    """
    if not mangled:
        return FORMAT_UNKNOWN

    # Itanium: _Z prefix, or __Z prefix (old GCC/NM)
    if mangled.startswith('_Z') or mangled.startswith('__Z'):
        # Rust legacy also uses _Z but with specific patterns (e.g. _ZN3foo...h<hex>E)
        # We try Itanium first; the Rust handler will fall back if Itanium parse
        # produces something that looks like a Rust hash suffix.
        return FORMAT_ITANIUM

    # MSVC: ? prefix
    if mangled.startswith('?'):
        return FORMAT_MSVC

    # Rust v0: _R prefix (RFC 2603)
    if mangled.startswith('_R'):
        return FORMAT_RUST

    # D language: _D prefix followed by a digit (length-prefixed name) or 'main'
    # Must be tight to avoid matching common ELF symbols like _DYNAMIC, _DATA, etc.
    if mangled.startswith('_D') and len(mangled) > 2:
        if mangled[2].isdigit() or mangled[2:6] == 'main':
            return FORMAT_D

    # Swift: $s, $S, _T0, $e prefixes
    if mangled.startswith('$s') or mangled.startswith('$S') or mangled.startswith('_T0'):
        return FORMAT_SWIFT
    # Embedded Swift uses $e
    if mangled.startswith('$e') and len(mangled) > 2:
        return FORMAT_SWIFT

    # Java/JNI: Java_ prefix
    if mangled.startswith('Java_'):
        return FORMAT_JNI

    # Objective-C: _OBJC_ prefix or +[/-[ method syntax
    if mangled.startswith('_OBJC_'):
        return FORMAT_OBJC
    if mangled.startswith('+[') or mangled.startswith('-['):
        return FORMAT_OBJC

    return FORMAT_UNKNOWN


def demangle(mangled, fmt=None, structured=False):
    """
    Demangle a C++/Rust/D/Swift/JNI mangled symbol name.

    Args:
        mangled (str): The mangled symbol string.
        fmt (str): Force a specific format (one of the FORMAT_* constants).
            If ``None``, auto-detect from the symbol prefix.
        structured (bool): If ``True``, return a :class:`DemangledSymbol`
            AST object.  If ``False`` (default), return the demangled string.

    Returns:
        str or DemangledSymbol: The demangled name, or the original mangled
        string if demangling fails (graceful degradation — never raises for
        unparseable input).  When ``structured=True``, returns a
        ``DemangledSymbol`` whose ``full_name`` may equal the original
        mangled name if parsing failed.

    This function never raises ``DemangleError`` for unparseable input — it
    returns the original string instead.  Parse warnings are recorded in the
    ``DemangledSymbol.parse_warnings`` list when ``structured=True``.
    """
    if not mangled:
        return mangled

    # Detect format from the normalized name (so @@VERSION suffixes don't
    # interfere with prefix detection), but pass the ORIGINAL to handlers.
    if fmt is None:
        fmt = detect_format(normalize_name(mangled))

    handler = _DISPATCH.get(fmt)
    if handler is None:
        # Unknown format — return normalized name (strips @@VERSION etc.)
        normalized = normalize_name(mangled)
        if structured:
            return DemangledSymbol(
                format=FORMAT_UNKNOWN,
                full_name=normalized,
                name=normalized,
                original_mangled=mangled,
                parse_warnings=['unknown mangling format'],
            )
        return normalized

    try:
        # Pass the ORIGINAL mangled name — handlers normalize internally
        # and preserve the true original in DemangledSymbol.original_mangled
        return handler(mangled, structured=structured)
    except Exception as e:
        # Graceful degradation: never crash binary loading
        normalized = normalize_name(mangled)
        if structured:
            return DemangledSymbol(
                format=fmt,
                full_name=normalized,
                name=normalized,
                original_mangled=mangled,
                parse_warnings=['demangle failed: %r' % e],
            )
        return normalized