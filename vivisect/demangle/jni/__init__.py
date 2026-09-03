"""
vivisect.demangle.jni - Java/JNI native method name demangling.

JNI native methods are mangled according to the JNI specification:

    Java_<mangled-class-name>_<mangled-method-name>
    Java_<class>_<method>__<mangled-signature>   (for overloaded methods)

Mangling rules:
    - Class name: dots -> underscores, '/' stays
    - '_' in original -> _1
    - ';' -> _2
    - '[' -> _3
    - '$' -> _00024
    - Non-ASCII -> _0xxxx (4 hex digits)

Reference:
    - JNI specification, "Resolving Native Method Names"
    - https://docs.oracle.com/javase/8/docs/technotes/guides/jni/spec/design.html
"""

import logging

from vivisect.demangle.common import DemangledSymbol

logger = logging.getLogger(__name__)

__all__ = ['demangle_jni']

_JNI_PREFIX = 'Java_'


def demangle_jni(mangled, structured=False):
    """
    Demangle a Java/JNI native method name.

    Args:
        mangled (str): The mangled JNI method name (e.g.
            ``Java_pkg_Cls_f__ILjava_lang_String_2``).
        structured (bool): If True, return a DemangledSymbol.

    Returns:
        str or DemangledSymbol: The demangled method name (e.g.
        ``pkg.Cls.f(int, String)``) or the original if it doesn't look
        like a valid JNI mangled name.
    """
    original = mangled

    if not mangled.startswith(_JNI_PREFIX):
        if structured:
            return DemangledSymbol(
                format='jni',
                full_name=original,
                name=original,
                original_mangled=original,
                parse_warnings=['not a JNI mangled name'],
            )
        return original

    body = mangled[len(_JNI_PREFIX):]

    # Split on '__' to separate method name from signature (overloaded methods).
    # But '__' could also appear as part of an escape sequence, so we need
    # to be careful.  In practice, '__' as a separator appears between the
    # method name and the overloaded signature.
    sig_idx = body.find('__')
    if sig_idx > -1:
        name_part = body[:sig_idx]
        sig_part = body[sig_idx + 2:]
    else:
        name_part = body
        sig_part = ''

    # Unmangle the class+method name (uses '.' as class separator)
    demangled_name = _unmangle_jni_string(name_part, class_sep='.')

    # Parse the signature if present (uses '/' as class separator)
    params = []
    if sig_part:
        # First unmangle the signature, then parse the type descriptors.
        # In the signature, '_' means '/' (Java package separator).
        unmangled_sig = _unmangle_jni_string(sig_part, class_sep='/')
        params = _parse_jni_signature(unmangled_sig)
        # Format as: class.method(arg1, arg2)
        last_dot = demangled_name.rfind('.')
        if last_dot > -1:
            class_name = demangled_name[:last_dot]
            method = demangled_name[last_dot + 1:]
            demangled_full = '%s.%s(%s)' % (class_name, method, ', '.join(params))
        else:
            demangled_full = '%s(%s)' % (demangled_name, ', '.join(params))
    else:
        demangled_full = demangled_name
        # Try to split class.method
        last_dot = demangled_name.rfind('.')
        if last_dot > -1:
            class_name = demangled_name[:last_dot]
            method = demangled_name[last_dot + 1:]
            demangled_full = '%s.%s' % (class_name, method)

    if not structured:
        return demangled_full

    sym = DemangledSymbol(
        format='jni',
        full_name=demangled_full,
        kind='function',
        original_mangled=original,
        parameters=params,
    )
    # Split scope and name
    if '.' in demangled_name:
        parts = demangled_name.split('.')
        sym.scope = parts[:-1]
        sym.name = parts[-1]
    else:
        sym.name = demangled_name
    return sym


def _unmangle_jni_string(s, class_sep='.'):
    """
    Unmangle a JNI class/method name string.

    Handles:
        _1 -> _
        _2 -> ;
        _3 -> [
        _00024 -> $ (and _0xxxx for Unicode)
        _ (other) -> class_sep (default '.')
    """
    result = []
    i = 0
    while i < len(s):
        c = s[i]
        if c == '_':
            if i + 1 < len(s):
                next_c = s[i + 1]
                if next_c == '1':
                    result.append('_')
                    i += 2
                elif next_c == '2':
                    result.append(';')
                    i += 2
                elif next_c == '3':
                    result.append('[')
                    i += 2
                elif next_c == '0' and i + 5 < len(s):
                    # Unicode: _0xxxx (4 hex digits)
                    hex_str = s[i + 2:i + 6]
                    try:
                        result.append(chr(int(hex_str, 16)))
                        i += 6
                    except ValueError:
                        result.append(c)
                        i += 1
                else:
                    # Treat _ as class separator
                    result.append(class_sep)
                    i += 1
            else:
                result.append(class_sep)
                i += 1
        else:
            result.append(c)
            i += 1
    return ''.join(result)


def _parse_jni_signature(sig):
    """
    Parse a JNI type signature string into a list of parameter type strings.

    JNI type descriptors:
        I=int, Z=boolean, B=byte, C=char, S=short, J=long, F=float, D=double
        L<class>;  for objects
        [          for arrays (prefix)
        V          for void (return type, not param)
    """
    type_map = {
        'I': 'int', 'Z': 'boolean', 'B': 'byte', 'C': 'char',
        'S': 'short', 'J': 'long', 'F': 'float', 'D': 'double',
        'V': 'void',
    }

    params = []
    i = 0
    while i < len(sig):
        c = sig[i]
        # Array dimensions
        array_depth = 0
        while c == '[':
            array_depth += 1
            i += 1
            if i >= len(sig):
                break
            c = sig[i]

        if c == 'L':
            # Object type: L<class>;
            end = sig.find(';', i)
            if end > -1:
                class_part = sig[i + 1:end].replace('/', '.')
                # Unmangle JNI escapes in class names
                class_part = _unmangle_jni_string(class_part)
                type_str = class_part
                i = end + 1
            else:
                type_str = 'object'
                i += 1
        elif c in type_map:
            type_str = type_map[c]
            i += 1
        else:
            type_str = c
            i += 1

        type_str += '[]' * array_depth
        params.append(type_str)

    return params