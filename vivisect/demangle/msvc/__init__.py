"""
vivisect.demangle.msvc - Microsoft Visual C++ ABI demangling (? prefix).

Pure-Python recursive descent parser for MSVC mangled symbols.
No external dependencies — works fully offline.

The MSVC C++ ABI is used by Microsoft Visual C++ and ICC on Windows.
Mangled symbols start with ``?`` and use ``@``-terminated scope chains.

Reference:
    - Ghidra MicrosoftDmang (mdemangler) package
    - LLVM MicrosoftDemangle.cpp
    - Microsoft undname.c documentation
"""

import logging

from vivisect.demangle.common import DemangledSymbol, normalize_name
from vivisect.demangle.msvc.parser import MSVCParser, ParseError
from vivisect.demangle.msvc.renderer import render

logger = logging.getLogger(__name__)

__all__ = ['demangle_msvc']


def demangle_msvc(mangled, structured=False):
    """
    Demangle an MSVC C++ ABI mangled symbol (? prefix).

    Uses the pure-Python recursive descent parser.

    Args:
        mangled (str): The mangled symbol string.
        structured (bool): If True, return a DemangledSymbol object.

    Returns:
        str or DemangledSymbol: The demangled name, or the original if
        demangling fails (graceful degradation).
    """
    original = mangled
    mangled = normalize_name(mangled)

    demangled = None
    parse_warnings = []

    ast_root = None
    try:
        parser = MSVCParser(mangled)
        ast_root = parser.parse()
        demangled = render(ast_root)
        parse_warnings = parser.warnings
    except ParseError as e:
        logger.debug('MSVC parser failed for %r: %r', mangled, e)
        parse_warnings.append('parser error: %r' % e)
    except Exception as e:
        logger.debug('MSVC parser exception for %r: %r', mangled, e)
        parse_warnings.append('parser exception: %r' % e)

    if demangled is None or demangled == mangled or not demangled:
        if structured:
            return DemangledSymbol(
                format='msvc',
                full_name=original,
                name=original,
                original_mangled=original,
                parse_warnings=parse_warnings or ['unable to demangle'],
            )
        return original

    if not structured:
        return demangled

    # Build structured result
    sym = _build_structured(demangled, original, parse_warnings, ast_root)
    return sym


def _build_structured(demangled, original, parse_warnings, ast_root=None):
    """Build a DemangledSymbol from the demangled string and AST."""
    sym = DemangledSymbol(
        format='msvc',
        full_name=demangled,
        original_mangled=original,
        parse_warnings=parse_warnings,
    )

    # Parse basic structure from the demangled string
    _parse_basic_structure(sym, demangled)

    # Populate from AST if available
    if ast_root is not None:
        _populate_from_ast(sym, ast_root)

    return sym


def _parse_basic_structure(sym, demangled):
    """Best-effort extraction of basic structure from a demangled string."""
    # Check for common MSVC patterns
    if '`vftable\'' in demangled:
        sym.kind = 'vtable'
    elif '`vbtable\'' in demangled:
        sym.kind = 'vbtable'
    elif '`RTTI' in demangled:
        sym.kind = 'rtti'
    elif 'ctor' in demangled:
        sym.kind = 'ctor'
    elif 'dtor' in demangled or '~' in demangled:
        sym.kind = 'dtor'
    elif 'operator' in demangled:
        sym.kind = 'operator'
    elif '(' in demangled:
        sym.kind = 'function'
    else:
        sym.kind = 'variable'

    # Extract scope and name
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


def _populate_from_ast(sym, ast_root):
    """Populate DemangledSymbol fields from the parsed AST."""
    from vivisect.demangle.msvc import ast_nodes as ast

    if ast_root.qualified_name:
        qname = ast_root.qualified_name
        if qname.scope:
            sym.scope = [_render_name_part(s) for s in qname.scope]
            sym.is_member = len(qname.scope) > 0
        if qname.basic_name:
            sym.name = _render_name_part(qname.basic_name)

    if isinstance(ast_root.type_info, ast.FunctionType):
        sym.kind = 'function' if sym.kind == 'unknown' else sym.kind
        ti = ast_root.type_info
        if ti.access:
            sym.access = ti.access
        if ti.calling_convention:
            sym.calling_convention = ti.calling_convention
        if ti.is_static:
            sym.is_static = True
        if ti.is_virtual:
            sym.is_virtual = True
        if ti.return_type and ti.return_type != 'void':
            sym.return_type = ti.return_type
        sym.parameters = [p for p in ti.parameters if p and p != 'void']
        if ti.cv_modifiers:
            sym.cv_qualifiers = ti.cv_modifiers
    elif isinstance(ast_root.type_info, ast.VariableInfo):
        sym.kind = 'variable' if sym.kind == 'unknown' else sym.kind
        ti = ast_root.type_info
        if ti.access:
            sym.access = ti.access
        if ti.is_static:
            sym.is_static = True
        if ti.var_type:
            sym.return_type = ti.var_type


def _render_name_part(part):
    """Render a name part to string."""
    from vivisect.demangle.msvc import ast_nodes as ast
    if isinstance(part, ast.FragmentName):
        return part.name
    if hasattr(part, 'name'):
        return part.name
    return str(part)