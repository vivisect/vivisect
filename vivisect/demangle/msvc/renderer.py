"""
Renderer for MSVC C++ demangled AST nodes.

Converts the parsed AST into a demangled string representation
matching Microsoft's undname output format.
"""

import logging
from vivisect.demangle.msvc import ast_nodes as ast

logger = logging.getLogger(__name__)

__all__ = ['render']


def render(symbol):
    """Render an MSVCSymbol AST into a demangled string."""
    if symbol is None:
        return ''

    parts = []

    # Render type info (access modifiers, function/variable type)
    type_info = symbol.type_info

    # Build access/storage prefix
    prefix = _build_prefix(type_info)
    if prefix:
        parts.append(prefix)

    # Render the qualified name
    name_str = _render_qualified_name(symbol.qualified_name)
    if name_str:
        parts.append(name_str)

    # Render function signature or variable type
    if isinstance(type_info, ast.FunctionType):
        sig = _render_function_signature(type_info, name_str)
        # Replace the name with the full signature
        if parts and parts[-1] == name_str:
            parts[-1] = sig
        else:
            parts.append(sig)
    elif isinstance(type_info, ast.VariableInfo):
        var_str = _render_variable(type_info, name_str)
        if parts and parts[-1] == name_str:
            parts[-1] = var_str
        else:
            parts.append(var_str)
    elif isinstance(type_info, ast.VFTable):
        vft_str = _render_vftable(type_info, name_str)
        if parts and parts[-1] == name_str:
            parts[-1] = vft_str
        else:
            parts.append(vft_str)

    result = ' '.join(parts)
    return result.strip()


def _build_prefix(type_info):
    """Build the access/storage modifier prefix."""
    if type_info is None:
        return ''

    prefix_parts = []

    if isinstance(type_info, ast.FunctionType):
        if type_info.is_thunk:
            prefix_parts.append('[thunk]:')
        if type_info.access:
            prefix_parts.append(type_info.access + ':')
        if type_info.is_virtual:
            prefix_parts.append('virtual')
        if type_info.is_static:
            prefix_parts.append('static')
    elif isinstance(type_info, ast.VariableInfo):
        if type_info.access:
            prefix_parts.append(type_info.access + ':')
        if type_info.is_static:
            prefix_parts.append('static')

    return ' '.join(prefix_parts)


def _render_qualified_name(qname):
    """Render a QualifiedName to string."""
    if qname is None:
        return ''

    parts = []

    # Scope
    if qname.scope:
        for s in qname.scope:
            parts.append(_render_name_component(s))

    # Basic name
    parts.append(_render_name_component(qname.basic_name))

    return '::'.join(parts)


def _render_name_component(component):
    """Render a single name component (FragmentName, SpecialName, TemplateName, etc.)."""
    if isinstance(component, ast.FragmentName):
        return component.name
    elif isinstance(component, ast.SpecialName):
        return component.name
    elif isinstance(component, ast.TemplateName):
        base = _render_name_component(component.base_name)
        args = ','.join(str(a) for a in component.args)
        return '%s<%s>' % (base, args)
    elif isinstance(component, ast.AnonymousNamespace):
        return '`anonymous-namespace\''
    elif isinstance(component, str):
        return component
    else:
        return str(component)


def _render_function_signature(func, name_str):
    """Render a function type as: ret_type calling_conv name(params) cv_modifiers."""
    parts = []

    # Return type — always show it, including void (matches MSVC undname output)
    ret = func.return_type or ''
    if ret:
        parts.append(ret)

    # Calling convention
    cc = func.calling_convention or ''
    if cc:
        parts.append(cc)

    # Function name (already rendered)
    parts.append(name_str)

    result = ' '.join(parts)

    # Parameters
    params = func.parameters
    if not params:
        params_str = 'void'
    else:
        param_strs = [p for p in params if p and p != 'void']
        if not param_strs:
            params_str = 'void'
        else:
            params_str = ', '.join(param_strs)

    result += '(%s)' % params_str

    # CV modifiers (const/volatile on this pointer)
    if func.cv_modifiers:
        result += ' ' + func.cv_modifiers

    return result


def _render_variable(var, name_str):
    """Render a variable: type name."""
    if var.is_guard:
        return '`local static guard\'' if not name_str else name_str
    var_type = var.var_type or ''
    if var_type:
        return '%s %s' % (var_type, name_str)
    return name_str


def _render_vftable(vft, name_str):
    """Render a vtable/vbtable."""
    if vft.scope is not None:
        # VFTable with explicit scope
        return 'const %s::`vftable\'' % _render_qualified_name(vft.scope)
    return 'const %s::`vftable\'' % name_str