"""
vivisect.demangle.itanium.grammar - Grammar constants for the Itanium C++ ABI.

This module contains the lookup tables for the Itanium mangling grammar:
    - Builtin type codes (single char and D* extended types)
    - Operator name codes (two-char)
    - Standard substitution abbreviations (St, Sa, Sb, Ss, Si, So, Sd)
    - Constructor/destructor codes
    - Special name codes (TV, TT, TI, TS, GV, etc.)

Reference: Itanium C++ ABI section 5.1 (External Names)
           GNU libiberty cp-demangle.c (the gold standard implementation)
"""

__all__ = [
    'BUILTIN_TYPES', 'EXTENDED_BUILTIN_TYPES',
    'OPERATORS', 'STD_SUBS',
    'CTOR_KINDS', 'DTOR_KINDS',
    'SPECIAL_NAMES',
    'STDLIB_NAMESPACE_PREFIX',
]


# Single-character builtin type codes -> type name
# From cp-demangle.c cplus_demangle_builtin_types[]
BUILTIN_TYPES = {
    'a': 'signed char',
    'b': 'bool',
    'c': 'char',
    'd': 'double',
    'e': 'long double',
    'f': 'float',
    'g': '__float128',
    'h': 'unsigned char',
    'i': 'int',
    'j': 'unsigned int',
    # 'k' is not used (NULL in the table)
    'l': 'long',
    'm': 'unsigned long',
    'n': '__int128',
    'o': 'unsigned __int128',
    # 'p', 'q', 'r' are not used
    's': 'short',
    't': 'unsigned short',
    # 'u' is vendor extended (handled separately)
    'v': 'void',
    'w': 'wchar_t',
    'x': 'long long',
    'y': 'unsigned long long',
    'z': '...',
}

# Extended builtin type codes starting with 'D'
# From cp-demangle.c d_builtin_type() handling
EXTENDED_BUILTIN_TYPES = {
    'Dd': 'decimal64',
    'De': 'decimal128',
    'Df': 'decimal32',
    'Dh': 'half',           # __fp16 / _Float16
    'Di': 'char32_t',
    'Ds': 'char16_t',
    'Du': 'char8_t',         # C++20 char8_t
    'Da': 'auto',
    'Dc': 'decltype(auto)',
    'Dn': 'nullptr_t',
    # DF<number>_ = _Float<number> (handled specially in parser)
    # DF<number>b = std::bfloat16_t (handled specially)
}


# Two-character operator codes -> operator symbol/name
# From cp-demangle.c cplus_demangle_operators[]
# Each entry: code -> (symbol, num_args)
OPERATORS = {
    'nw': ('new', 3),
    'na': ('new[]', 3),
    'dl': ('delete', 1),
    'da': ('delete[]', 1),
    'ps': ('+', 1),       # unary plus
    'ng': ('-', 1),       # unary minus
    'ad': ('&', 1),       # address-of (unary)
    'de': ('*', 1),       # dereference (unary)
    'co': ('~', 1),       # bitwise not (unary)
    'pl': ('+', 2),       # binary plus
    'mi': ('-', 2),       # binary minus
    'ml': ('*', 2),
    'dv': ('/', 2),
    'rm': ('%', 2),
    'an': ('&', 2),       # bitwise and
    'or': ('|', 2),
    'eo': ('^', 2),
    'aS': ('=', 2),
    'pL': ('+=', 2),
    'mI': ('-=', 2),
    'mL': ('*=', 2),
    'dV': ('/=', 2),
    'rM': ('%=', 2),
    'aN': ('&=', 2),
    'oR': ('|=', 2),
    'eO': ('^=', 2),
    'ls': ('<<', 2),
    'rs': ('>>', 2),
    'lS': ('<<=', 2),
    'rS': ('>>=', 2),
    'eq': ('==', 2),
    'ne': ('!=', 2),
    'lt': ('<', 2),
    'gt': ('>', 2),
    'le': ('<=', 2),
    'ge': ('>=', 2),
    'nt': ('!', 1),       # logical not (unary)
    'aa': ('&&', 2),
    'oo': ('||', 2),
    'pp': ('++', 1),
    'mm': ('--', 1),
    'cm': (',', 2),
    'pm': ('->*', 2),
    'pt': ('->', 2),
    'cl': ('()', 2),
    'ix': ('[]', 2),
    'qu': ('?', 3),
    'st': ('sizeof', 1),
    'sz': ('sizeof', 1),
    'at': ('alignof', 1),
    'az': ('alignof', 1),
    'ss': ('<=>', 2),     # C++20 spaceship operator
    'ds': ('.*', 2),
    'dt': ('.', 2),       # member access
    'dx': ('[]=', 2),     # [expr] = expr
    'dX': ('[...]=', 3),  # [expr...expr] = expr
    'cv': ('cast', 2),    # conversion operator (special handling)
    'sc': ('static_cast', 2),
    'rc': ('reinterpret_cast', 2),
    'dc': ('dynamic_cast', 2),
    'cc': ('const_cast', 2),
    'nx': ('noexcept', 1),
    'tw': ('throw', 1),
    'tr': ('throw', 0),   # rethrow
    'aw': ('co_await', 1),
    'gs': ('::', 1),      # global scope
    'li': ('operator""', 1),  # literal operator
    'sP': ('sizeof...', 1),
    'sZ': ('sizeof...', 1),
    'fl': ('...', 2),     # pack fold (left)
    'fr': ('...', 2),     # pack fold (right)
    'fL': ('...', 3),     # binary fold (left)
    'fR': ('...', 3),     # binary fold (right)
    'di': ('=', 2),       # .name = expr (designated init)
}


# Constructor/destructor kinds
# C1=complete, C2=base, C3=allocating, CI1/CI2=inheriting
# D0=deleting, D1=complete, D2=base
CTOR_KINDS = {
    'C1': 'complete',
    'C2': 'base',
    'C3': 'allocating',
    'CI1': 'inheriting complete',
    'CI2': 'inheriting base',
}

DTOR_KINDS = {
    'D0': 'deleting',
    'D1': 'complete',
    'D2': 'base',
}


# Standard substitution abbreviations
# From cp-demangle.c standard_subs[]
# S_ = first substitution (index 0), S0_ = second (index 1), etc.
# But St, Sa, Sb, Ss, Si, So, Sd are predefined:
# Per the Itanium ABI, Ss/Si/So/Sd expand to the FULL type, not just the name.
# c++filt expands these to their full template instantiations.
STD_SUBS = {
    't': 'std',
    'a': 'std::allocator',
    'b': 'std::basic_string',
    's': 'std::basic_string<char, std::char_traits<char>, std::allocator<char> >',
    'i': 'std::basic_istream<char, std::char_traits<char> >',
    'o': 'std::basic_ostream<char, std::char_traits<char> >',
    'd': 'std::basic_iostream<char, std::char_traits<char> >',
}


# Special name codes (T* and G*)
# From cp-demangle.c d_special_name()
SPECIAL_NAMES = {
    'TV': 'vtable',          # vtable for <type>
    'TT': 'VTT',             # VTT for <type>
    'TI': 'typeinfo',        # typeinfo for <type>
    'TS': 'typeinfo name',   # typeinfo name for <type>
    'TF': 'typeinfo fn',     # typeinfo function for <type>
    'TJ': 'java class',      # Java class
    'TH': 'tls init',        # TLS init function
    'TW': 'tls wrapper',     # TLS wrapper function
    'TA': 'template parm',   # template parameter object
    'GV': 'guard variable',  # guard variable for <name>
    'GR': 'reference temp',  # reference temporary for <name>
    'GA': 'hidden alias',    # hidden alias
    'GTt': 'transaction clone',
    'GTn': 'non-transaction clone',
    'Th': 'thunk',           # non-virtual thunk: Th<offset>_
    'Tv': 'virtual thunk',   # virtual thunk: Tv<offset>_<offset>_
    'Tc': 'covariant thunk', # covariant return thunk
    'TC': 'construction vtable',  # construction vtable
}


# The std:: namespace prefix
STDLIB_NAMESPACE_PREFIX = 'std::'