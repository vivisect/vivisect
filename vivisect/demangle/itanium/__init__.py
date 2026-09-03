"""
vivisect.demangle.itanium - Itanium C++ ABI demangling (_Z prefix).

Phase 1: Pure-Python recursive descent parser.  No cxxfilt dependency.

The Itanium C++ ABI is used by GCC, Clang, and ICC on Linux/macOS.
Mangled symbols start with ``_Z`` (or ``__Z`` for old GCC).

Reference:
    - Itanium C++ ABI section 5.1 (External Names)
    - GNU libiberty cp-demangle.c (the gold standard)
    - LLVM ItaniumDemangle.cpp
"""

import logging

from vivisect.demangle.common import DemangledSymbol, normalize_name
from vivisect.demangle.itanium.parser import ItaniumParser, ParseError
from vivisect.demangle.itanium.renderer import render
from vivisect.demangle.symbol import Symbol

logger = logging.getLogger(__name__)

__all__ = ['demangle_itanium', 'demangle_itanium_symbol']


def demangle_itanium(mangled, structured=False):
    """
    Demangle an Itanium C++ ABI mangled symbol (_Z prefix).

    Uses the pure-Python recursive descent parser.  Falls back to cxxfilt
    if available and the pure-Python parser fails (for edge cases not yet
    handled).

    Args:
        mangled (str): The mangled symbol string.
        structured (bool): If True, return a DemangledSymbol object.

    Returns:
        str or DemangledSymbol: The demangled name, or the original if
        demangling fails.
    """
    original = mangled
    mangled = normalize_name(mangled)

    demangled = None
    parse_warnings = []

    # Try the pure-Python parser first
    try:
        parser = ItaniumParser(mangled)
        ast_root = parser.parse()
        demangled = render(ast_root, subs=parser.subs)
        parse_warnings = parser.warnings
    except ParseError as e:
        logger.debug('pure-Python Itanium parser failed for %r: %r', mangled, e)
        parse_warnings.append('parser error: %r' % e)
    except Exception as e:
        logger.debug('Itanium parser exception for %r: %r', mangled, e)
        parse_warnings.append('parser exception: %r' % e)

    # If the parser failed or produced nothing, try cxxfilt as fallback
    if demangled is None or demangled == mangled or '/*' in demangled:
        try:
            import cxxfilt
            cxx_result = cxxfilt.demangle(mangled)
            if cxx_result and cxx_result != mangled:
                if demangled is None:
                    demangled = cxx_result
                    parse_warnings = ['cxxfilt fallback']
                else:
                    # Prefer cxxfilt if the parser produced garbage
                    if '/*' in demangled:
                        demangled = cxx_result
                        parse_warnings = ['cxxfilt fallback (parser produced placeholders)']
        except Exception as e:
            logger.debug('cxxfilt fallback failed for %r: %r', mangled, e)

    # If all methods failed, return the original
    if demangled is None or demangled == mangled:
        if structured:
            return DemangledSymbol(
                format='itanium',
                full_name=original,
                name=original,
                original_mangled=original,
                parse_warnings=parse_warnings or ['unable to demangle'],
            )
        return original

    if not structured:
        return demangled

    # Build structured result
    sym = _build_structured(demangled, original, parse_warnings)
    return sym


def demangle_itanium_symbol(mangled):
    """
    Demangle an Itanium symbol and return a Symbol object with full
    structured data (original, demangled, stripped, type/return/arg info).

    Args:
        mangled (str): The original mangled symbol string.

    Returns:
        Symbol: The Symbol object with all available structured data.
    """
    original = mangled
    mangled = normalize_name(mangled)

    stripped = {}
    if original != mangled:
        # Record what was stripped
        suffix = original[len(mangled):]
        stripped['version_suffix'] = suffix

    demangled = None
    parse_warnings = []
    ast_root = None
    subs = []

    try:
        parser = ItaniumParser(mangled)
        ast_root = parser.parse()
        subs = parser.subs
        demangled = render(ast_root, subs=subs)
        parse_warnings = parser.warnings
    except ParseError as e:
        parse_warnings.append('parser error: %r' % e)
    except Exception as e:
        parse_warnings.append('parser exception: %r' % e)

    # cxxfilt fallback
    if demangled is None or demangled == mangled or '/*' in demangled:
        try:
            import cxxfilt
            cxx_result = cxxfilt.demangle(mangled)
            if cxx_result and cxx_result != mangled:
                if demangled is None or '/*' in (demangled or ''):
                    demangled = cxx_result
                    if not ast_root:
                        parse_warnings = ['cxxfilt fallback']
        except Exception:
            pass

    if demangled is None:
        demangled = original

    # Build the Symbol with structured data from the AST
    sym = Symbol(original=original, demangled=demangled, format='itanium',
                 stripped=stripped, parse_warnings=parse_warnings)

    if ast_root is not None:
        _populate_symbol_from_ast(sym, ast_root, subs)

    return sym


def _build_structured(demangled, original, parse_warnings):
    """Build a DemangledSymbol from the demangled string (Phase 0 compat)."""
    sym = DemangledSymbol(
        format='itanium',
        full_name=demangled,
        original_mangled=original,
        parse_warnings=parse_warnings,
    )
    _parse_basic_structure(sym, demangled)
    return sym


def _parse_basic_structure(sym, demangled):
    """Best-effort extraction of basic structure from a demangled string."""
    # Special names
    for prefix, kind in [
        ('vtable for ', 'vtable'),
        ('typeinfo for ', 'typeinfo'),
        ('typeinfo name for ', 'typeinfo_name'),
        ('VTT for ', 'vtt'),
        ('guard variable for ', 'guard'),
    ]:
        if demangled.startswith(prefix):
            sym.kind = kind
            sym.name = demangled[len(prefix):]
            sym.scope = sym.name.split('::')
            return

    # Function or variable: split scope from the last ::
    if '::' in demangled:
        depth = 0
        split_pos = -1
        for i in range(len(demangled) - 1):
            c = demangled[i]
            if c == '<':
                depth += 1
            elif c == '>':
                depth -= 1
            elif depth == 0 and c == ':' and demangled[i + 1] == ':':
                split_pos = i

        if split_pos > -1:
            sym.scope = demangled[:split_pos].split('::')
            sym.name = demangled[split_pos + 2:]
        else:
            sym.name = demangled
    else:
        sym.name = demangled

    if '<' in sym.name:
        sym.is_template = True

    if sym.kind == 'unknown':
        if '(' in sym.name:
            sym.kind = 'function'
        else:
            sym.kind = 'variable'


def _populate_symbol_from_ast(sym, ast_root, subs):
    """Populate Symbol fields from the parsed AST."""
    from vivisect.demangle.itanium import ast_nodes as ast

    sym.kind = 'unknown'

    if isinstance(ast_root, ast.SpecialName):
        sym.kind = ast_root.kind
        if ast_root.target is not None:
            target_str = render(ast_root.target, subs=subs)
            sym.name = target_str
            sym.scope = target_str.split('::') if '::' in target_str else []
        return

    if isinstance(ast_root, ast.Name):
        qualified = ast_root.qualified_name

        # Extract scope and name
        if isinstance(qualified, ast.NestedName):
            scope_parts = []
            for p in qualified.prefix:
                r = render(p, subs=subs) if not (isinstance(p, ast.UnqualifiedName) and p.kind == 'template') else ''
                if r and not (isinstance(p, ast.UnqualifiedName) and p.kind == 'template'):
                    scope_parts.append(r)
            sym.scope = scope_parts
            sym.is_member = len(scope_parts) > 0

            # Get the unqualified name
            unq = qualified.unqualified_name
            if isinstance(unq, ast.UnqualifiedName):
                if unq.kind == 'source':
                    sym.name = render(unq, subs=subs)
                elif unq.kind == 'ctor':
                    sym.kind = 'ctor'
                    sym.name = scope_parts[-1] if scope_parts else '<ctor>'
                elif unq.kind == 'dtor':
                    sym.kind = 'dtor'
                    sym.name = '~' + (scope_parts[-1] if scope_parts else '<dtor>')
                elif unq.kind == 'operator':
                    sym.name = 'operator' + unq.value.symbol
                elif unq.kind == 'template':
                    base_name = scope_parts[-1] if scope_parts else ''
                    targs_str = render(unq.value, subs=subs)
                    sym.name = base_name + targs_str
                    sym.is_template = True
        elif isinstance(qualified, ast.UnqualifiedName):
            if qualified.kind == 'source':
                sym.name = render(qualified, subs=subs)
            elif qualified.kind == 'template':
                sym.is_template = True
                targs_str = render(qualified.value, subs=subs)
                sym.name = targs_str
        elif isinstance(qualified, ast.SourceName):
            sym.name = qualified.name
        elif isinstance(qualified, ast.Substitution):
            sym.name = render(qualified, subs=subs)

        # Extract function signature data
        if ast_root.is_function and ast_root.bare_function:
            sym.kind = 'function' if sym.kind == 'unknown' else sym.kind

            types = ast_root.bare_function.types
            if types:
                # Determine if there's a return type
                is_template = sym.is_template
                if is_template and len(types) > 1:
                    sym.return_type = render(types[0], subs=subs)
                    param_nodes = types[1:]
                else:
                    param_nodes = types

                # Apply void→empty convention
                param_strs = [render(t, subs=subs) for t in param_nodes]
                if len(param_strs) == 1 and param_strs[0] == 'void':
                    param_strs = []
                sym.parameters = param_strs
        else:
            sym.kind = 'variable' if sym.kind == 'unknown' else sym.kind