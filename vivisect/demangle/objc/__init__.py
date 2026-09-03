"""
vivisect.demangle.objc - Objective-C symbol demangling.

Objective-C symbols in Mach-O binaries use special prefixes:

    _OBJC_CLASS_$_ClassName        - class reference
    _OBJC_METACLASS_$_ClassName    - metaclass reference
    _OBJC_IVAR_$_ClassName.ivar    - instance variable
    _OBJC_EHTYPE_$_ClassName       - exception type
    +[ClassName method]            - class method (already human-readable)
    -[ClassName method]            - instance method (already human-readable)

The ``_OBJC_*`` symbols are mostly already readable and just need the
prefix stripped.  The ``+[``/``-[`` method syntax is not really mangled
but is included here for completeness.
"""

import logging

from vivisect.demangle.common import DemangledSymbol

logger = logging.getLogger(__name__)

__all__ = ['demangle_objc']

_OBJC_PREFIXES = (
    ('_OBJC_CLASS_$_', 'class_ref'),
    ('_OBJC_METACLASS_$_', 'metaclass_ref'),
    ('_OBJC_IVAR_$_', 'ivar'),
    ('_OBJC_EHTYPE_$_', 'exception_type'),
    ('_OBJC_CLASSLIST_IMAGES_$_', 'classlist_images'),
    ('_OBJC_CATEGORY_CLASS_$_', 'category_class'),
    ('_OBJC_CATEGORY_$_', 'category'),
)


def demangle_objc(mangled, structured=False):
    """
    Demangle an Objective-C symbol.

    Args:
        mangled (str): The mangled ObjC symbol.
        structured (bool): If True, return a DemangledSymbol.

    Returns:
        str or DemangledSymbol: The demangled symbol.
    """
    original = mangled

    # Handle +[ClassName method] / -[ClassName method] syntax
    # These are already human-readable; just return them
    if mangled.startswith('+[') or mangled.startswith('-['):
        if not structured:
            return mangled
        return DemangledSymbol(
            format='objc',
            full_name=mangled,
            kind='method',
            name=mangled,
            original_mangled=original,
        )

    # Handle _OBJC_* prefixed symbols
    for prefix, kind in _OBJC_PREFIXES:
        if mangled.startswith(prefix):
            name = mangled[len(prefix):]
            if not structured:
                return name
            sym = DemangledSymbol(
                format='objc',
                full_name=name,
                kind=kind,
                name=name,
                original_mangled=original,
            )
            # For ivar symbols, split on '.'
            if '.' in name:
                parts = name.split('.')
                sym.scope = [parts[0]]
                sym.name = parts[1] if len(parts) > 1 else name
            return sym

    # Not a recognized ObjC symbol — return as-is
    if not structured:
        return original

    return DemangledSymbol(
        format='objc',
        full_name=original,
        name=original,
        original_mangled=original,
        parse_warnings=['not a recognized Objective-C mangled symbol'],
    )