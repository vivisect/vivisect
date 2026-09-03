"""
MSVC C++ ABI demangling parser.

Recursive descent parser for Microsoft Visual C++ mangled symbols.
Symbols start with '?' and use '@'-terminated scope chains.

Reference:
    - Ghidra MicrosoftDmang (mdemangler) package
    - LLVM MicrosoftDemangle.cpp
    - Microsoft undname.c documentation
    - http://www.geoffchappell.com/studies/msvc/language/decoration/name.htm
"""

import logging
from vivisect.demangle.msvc import ast_nodes as ast

logger = logging.getLogger(__name__)

__all__ = ['MSVCParser', 'ParseError']


class ParseError(Exception):
    pass


class MSVCParser:
    """Recursive descent parser for MSVC mangled symbols."""

    # --- Operator name lookup tables ---

    # Single-char operator codes (after ?)
    OPERATORS = {
        '0': ('constructor', True, False),
        '1': ('destructor', False, True),
        '2': 'operator new',
        '3': 'operator delete',
        '4': 'operator=',
        '5': 'operator>>',
        '6': 'operator<<',
        '7': 'operator!',
        '8': 'operator==',
        '9': 'operator!=',
        'A': 'operator[]',
        # B = operator [type cast] — handled specially
        'C': 'operator->',
        'D': 'operator*',
        'E': 'operator++',
        'F': 'operator--',
        'G': 'operator-',
        'H': 'operator+',
        'I': 'operator&',
        'J': 'operator->*',
        'K': 'operator/',
        'L': 'operator%',
        'M': 'operator<',
        'N': 'operator<=',
        'O': 'operator>',
        'P': 'operator>=',
        'Q': 'operator,',
        'R': 'operator()',
        'S': 'operator~',
        'T': 'operator^',
        'U': 'operator|',
        'V': 'operator&&',
        'W': 'operator||',
        'X': 'operator*=',
        'Y': 'operator+=',
        'Z': 'operator-=',
    }

    # Two-char operator codes (after ?_)
    OPERATORS_EXT = {
        '0': 'operator/=',
        '1': 'operator%=',
        '2': 'operator>>=',
        '3': 'operator<<=',
        '4': 'operator&=',
        '5': 'operator|=',
        '6': 'operator^=',
        '7': '`vftable\'',
        '8': '`vbtable\'',
        '9': '`vcall\'',
        'A': '`typeof\'',
        'B': '`local static guard\'',
        # C = string — handled specially
        'D': '`vbase destructor\'',
        'E': '`vector deleting destructor\'',
        'F': '`default constructor closure\'',
        'G': '`scalar deleting destructor\'',
        'H': '`vector constructor iterator\'',
        'I': '`vector destructor iterator\'',
        'J': '`vector vbase constructor iterator\'',
        'K': '`virtual displacement map\'',
        'L': '`eh vector constructor iterator\'',
        'M': '`eh vector destructor iterator\'',
        'N': '`eh vector vbase constructor iterator\'',
        'O': '`copy constructor closure\'',
        'S': '`local vftable\'',
        'T': '`local vftable constructor closure\'',
        'U': 'operator new[]',
        'V': 'operator delete[]',
        'W': '`omni callsig\'',
        'X': '`placement delete closure\'',
        'Y': '`placement delete[] closure\'',
    }

    # Three-char operator codes (after ?__)
    OPERATORS_EXT3 = {
        'A': '`managed vector constructor iterator\'',
        'B': '`managed vector destructor iterator\'',
        'C': '`eh vector copy constructor iterator\'',
        'D': '`eh vector vbase copy constructor iterator\'',
        'E': '`dynamic initializer for \'',  # needs object name appended
        'F': '`dynamic atexit destructor for \'',
        'G': '`vector copy constructor iterator\'',
        'H': '`vector vbase copy constructor iterator\'',
        'I': '`managed vector copy constructor iterator\'',
        'J': '`local static thread guard\'',
        'K': 'operator "" ',  # UDL — needs fragment name
    }

    # RTTI names (after ?_R)
    RTTI_NAMES = {
        '0': '`RTTI Type Descriptor\'',
        '2': '`RTTI Base Class Array\'',
        '3': '`RTTI Class Hierarchy Descriptor\'',
        '4': '`RTTI Complete Object Locator\'',
    }

    # Primitive type codes → type name
    PRIMITIVES = {
        'C': 'char',
        'D': 'char',
        'E': 'unsigned char',
        'F': 'short',
        'G': 'unsigned short',
        'H': 'int',
        'I': 'unsigned int',
        'J': 'long',
        'K': 'unsigned long',
        'M': 'float',
        'N': 'double',
        'O': 'long double',
        'X': 'void',
        'Z': '...',
    }

    # Extended primitive types (after _)
    EXTENDED_PRIMITIVES = {
        'D': 'signed char',
        'E': 'unsigned char',
        'F': 'short',
        'G': 'unsigned short',
        'H': 'int',
        'I': 'unsigned int',
        'J': '__int64',
        'K': 'unsigned __int64',
        'L': '__int128',
        'M': 'unsigned __int128',
        'N': 'bool',
        'Q': 'char8_t',
        'S': 'char16_t',
        'U': 'char32_t',
        'W': 'wchar_t',
    }

    # Calling convention codes → name
    CALLING_CONVENTIONS = {
        'A': '__cdecl', 'B': '__cdecl',
        'C': '__pascal', 'D': '__pascal',
        'E': '__thiscall', 'F': '__thiscall',
        'G': '__stdcall', 'H': '__stdcall',
        'I': '__fastcall', 'J': '__fastcall',
        'K': '', 'L': '',
        'M': '__clrcall', 'N': '__clrcall',
    }

    def __init__(self, mangled):
        self.mangled = mangled
        self.pos = 0
        self.warnings = []
        self._backrefs = []  # Type back-reference table
        self._name_backrefs = []  # Name back-reference table

    # --- Low-level cursor ---

    def _peek(self, offset=0):
        idx = self.pos + offset
        if idx >= len(self.mangled):
            return '\x00'  # DONE
        return self.mangled[idx]

    def _next(self):
        if self.pos >= len(self.mangled):
            raise ParseError('unexpected end of input at pos %d' % self.pos)
        ch = self.mangled[self.pos]
        self.pos += 1
        return ch

    def _expect(self, ch):
        c = self._next()
        if c != ch:
            raise ParseError('expected %r, got %r at pos %d' % (ch, c, self.pos - 1))
        return c

    def _at_end(self):
        return self.pos >= len(self.mangled)

    # --- Public entry point ---

    def parse(self):
        """Parse the mangled symbol and return an MSVCSymbol AST."""
        if self._peek() != '?':
            raise ParseError('MSVC symbols must start with ?')

        self._next()  # consume '?'

        # Check for special prefixes
        # ??@ = hashed object (MD5-based)
        if self._peek() == '@':
            # Hashed object — can't demangle, return as-is
            raise ParseError('hashed object (??@) cannot be demangled')

        # ?? = could be embedded object, RTTI, or special name (ctor/dtor/operator)
        if self._peek() == '?':
            # Check what follows the second ?
            next2 = self._peek(1)
            if next2 == '_' or next2 == '?':
                # ??_X (RTTI/vtable) or ??? (embedded)
                return self._parse_double_question()
            # ??0, ??1, ??B, etc. = special name (constructor, destructor, operator)
            # Fall through to normal C++ symbol parsing
            pass

        # ?$ = template
        if self._peek() == '$':
            return self._parse_template_symbol()

        # Standard ?name@@typeinfo pattern
        return self._parse_cpp_symbol()

    # --- Double-question symbols (??, ??_) ---

    def _parse_double_question(self):
        """Parse symbols starting with ?? (second ? consumed)."""
        self._next()  # consume second '?'

        # ??_7Foo@@6B = vtable for Foo
        # ??_8Foo@@6B = vbtable for Foo
        # ??_0 through ??_4 = RTTI
        if self._peek() == '_':
            self._next()  # consume '_'
            code = self._next()

            if code == '7':
                # vtable: ??_7Class@@6B
                qname = self._parse_qualified_name()
                return ast.MSVCSymbol(
                    qualified_name=qname,
                    type_info=ast.VFTable(scope=qname),
                    kind='vtable',
                )
            elif code == '8':
                # vbtable
                qname = self._parse_qualified_name()
                return ast.MSVCSymbol(
                    qualified_name=qname,
                    type_info=ast.VFTable(scope=qname),
                    kind='vbtable',
                )
            elif code in self.RTTI_NAMES:
                rtti_name = self.RTTI_NAMES[code]
                # RTTI 0 has a type
                if code == '0':
                    type_str = self._parse_data_type()
                    name = '%s `RTTI Type Descriptor\'' % type_str
                elif code == '1':
                    # RTTI Base Class Descriptor — has 4 numbers
                    a = self._parse_encoded_number()
                    b = self._parse_encoded_number()
                    c = self._parse_encoded_number()
                    d = self._parse_encoded_number()
                    name = '`RTTI Base Class Descriptor at (%s,%s,%s,%s)\'' % (a, b, c, d)
                else:
                    name = rtti_name
                return ast.MSVCSymbol(
                    qualified_name=ast.QualifiedName([], ast.SpecialName(name, kind='rtti')),
                    type_info=None,
                    kind='rtti',
                )
            else:
                raise ParseError('unknown ??_%s symbol' % code)

        # ??? prefix = embedded object
        if self._peek() == '?':
            # Embedded — parse the inner symbol
            inner = self._parse_embedded_name()
            return ast.MSVCSymbol(
                qualified_name=inner,
                type_info=None,
                is_embedded=True,
                kind='embedded',
            )

        # ??B, ??C, etc. — might be other special forms
        # Try parsing as a regular C++ symbol with extra ? prefix
        raise ParseError('unknown ?? prefix: %r' % self._peek())

    # --- Template symbol ($ prefix) ---

    def _parse_template_symbol(self):
        """Parse a top-level ?$ template symbol."""
        self._next()  # consume '$'
        template = self._parse_template_name()
        # After the template name, there may be type info
        type_info = None
        if not self._at_end():
            type_info = self._parse_type_info(-1)

        return ast.MSVCSymbol(
            qualified_name=template,
            type_info=type_info,
            kind='template',
        )

    # --- Standard C++ symbol ---

    def _parse_cpp_symbol(self):
        """Parse a standard ?name@@typeinfo C++ symbol."""
        qname = self._parse_qualified_name()
        rtti_num = -1
        if isinstance(qname.basic_name, ast.SpecialName):
            rtti_num = qname.basic_name.rtti_number

        type_info = None
        if not self._at_end():
            type_info = self._parse_type_info(rtti_num)

        return ast.MSVCSymbol(
            qualified_name=qname,
            type_info=type_info,
            kind='function' if isinstance(type_info, ast.FunctionType) else 'variable',
        )

    # --- Name parsing ---

    def _parse_qualified_name(self):
        """Parse a qualified name: name@scope1@scope2@@ or name@@.

        In MSVC mangling, the basic name comes first, then scope fragments
        as @-terminated strings, and the whole qualified name ends with @@.
        The pattern is: name@scope1@scope2@...@@
        A single @@ after the name means no scope.
        """
        scope = []
        basic_name = None

        # Check for ? prefix (special name or template)
        if self._peek() == '?':
            self._next()  # consume '?'
            basic_name = self._parse_special_name()
        elif self._peek() == '$':
            self._next()  # consume '$'
            basic_name = self._parse_template_name()
        else:
            # Plain name fragment
            basic_name = self._parse_fragment_name()

        # Now parse scope fragments. Each @ after the name either:
        # - starts a scope fragment (name@MyClass@...)
        # - ends the qualified name (name@@ or operator@@)
        # For special names (constructor/destructor), the scope follows
        # directly without an @ separator: ?0MyClass@@
        # For operators, a single @ means end of name (global scope)
        is_special = isinstance(basic_name, ast.SpecialName)
        is_operator = is_special and basic_name.is_operator

        while True:
            ch = self._peek()
            if ch == '@':
                self._next()  # consume @
                if self._peek() == '@':
                    # @@ = end of qualified name
                    self._next()
                    break
                if self._peek() == '\x00':
                    break
                # For operators, a single @ means end of name (global scope)
                if is_operator:
                    break
                # Parse scope fragment (goes before the basic name in scope chain)
                frag = self._parse_scope_fragment_or_name()
                if frag is not None:
                    scope.insert(0, frag)
            elif is_special and not is_operator and ch != '\x00':
                # Special names (ctor/dtor) have scope directly after, no @ separator
                frag = self._parse_scope_fragment_or_name()
                if frag is not None:
                    scope.insert(0, frag)
            else:
                # No more @ — end of qualified name
                break

        # For constructor/destructor, the name is the class name from scope
        if isinstance(basic_name, ast.SpecialName):
            if basic_name.is_ctor and scope:
                cls_name = scope[-1].name if hasattr(scope[-1], 'name') else str(scope[-1])
                basic_name.name = cls_name
            elif basic_name.is_dtor and scope:
                base = scope[-1].name if hasattr(scope[-1], 'name') else str(scope[-1])
                basic_name.name = '~' + base

        return ast.QualifiedName(scope, basic_name)

    def _parse_scope_fragment_or_name(self):
        """Parse a scope fragment (handles ?, $, or plain name)."""
        if self._peek() == '?':
            return self._parse_scope_fragment()
        elif self._peek() == '$':
            self._next()
            return self._parse_template_name()
        else:
            return self._parse_fragment_name()

    def _parse_scope_fragment(self):
        """Parse a scope fragment that starts with ?."""
        if self._peek() == '?':
            # Check for ?A (anonymous namespace)
            if self._peek(1) == 'A':
                self._next()  # ?
                self._next()  # A
                if self._peek() == '@':
                    self._next()
                return ast.AnonymousNamespace()
            # Check for ?$ (template in scope)
            if self._peek(1) == '$':
                self._next()  # ?
                self._next()  # $
                tmpl = self._parse_template_name()
                return tmpl
            # Numeric back-reference (?0, ?1, ...)
            if self._peek(1).isdigit():
                self._next()  # ?
                idx = self._next()
                # TODO: resolve back-reference
                return None  # skip for now
            # Unknown ? in scope
            self._next()
            return None
        return self._parse_fragment_name()

    def _parse_fragment_name(self):
        """Parse a simple name fragment terminated by @."""
        chars = []
        while True:
            ch = self._peek()
            if ch == '@' or ch == '\x00':
                break
            chars.append(ch)
            self.pos += 1
        name = ''.join(chars)
        if not name:
            raise ParseError('empty fragment name at pos %d' % self.pos)
        frag = ast.FragmentName(name)
        self._name_backrefs.append(frag)
        return frag

    def _parse_template_name(self):
        """Parse a template name: name@@template-args."""
        # The base name fragment
        base = self._parse_fragment_name()
        # Consume @ separator (template names end with @@)
        if self._peek() == '@':
            self._next()
            if self._peek() == '@':
                self._next()

        # Parse template arguments
        args = self._parse_template_args()

        tmpl = ast.TemplateName(base, args)
        self._name_backrefs.append(tmpl)
        return tmpl

    def _parse_template_args(self):
        """Parse template arguments until we hit a non-type boundary."""
        args = []
        # Template args are types or values, terminated implicitly
        while not self._at_end() and self._peek() != '@':
            try:
                arg = self._parse_template_arg()
                args.append(arg)
            except ParseError:
                break
        # Consume trailing @ if present
        if self._peek() == '@':
            self._next()
        return args

    def _parse_template_arg(self):
        """Parse a single template argument (type or value)."""
        # Template args can be:
        # - A type (starts with a type code)
        # - A numeric value (digits)
        # - A named value (?$ + name)
        ch = self._peek()
        if ch == '?':
            # Could be a nested template or special
            self._next()
            if self._peek() == '$':
                self._next()
                tmpl = self._parse_template_name()
                return tmpl
            # Try as type
            return '?' + self._parse_type_string()
        if ch.isdigit():
            # Integer value
            num = ''
            while self._peek().isdigit():
                num += self._next()
            if self._peek() == '@':
                self._next()
            return num
        # Parse as type
        return self._parse_data_type()

    def _parse_special_name(self):
        """Parse a special name following the ? prefix."""
        code = self._next()

        if code in self.OPERATORS:
            info = self.OPERATORS[code]
            if isinstance(info, tuple):
                name, is_ctor, is_dtor = info
                return ast.SpecialName('', kind='ctor' if is_ctor else 'dtor',
                                       is_ctor=is_ctor, is_dtor=is_dtor)
            return ast.SpecialName(info, kind='operator', is_operator=True)

        if code == 'B':
            # Type cast operator — type determined later from return type
            return ast.SpecialName('operator', kind='operator', is_type_cast=True)

        if code == '_':
            code2 = self._next()
            if code2 in self.OPERATORS_EXT:
                name = self.OPERATORS_EXT[code2]
                if code2 == 'B':
                    # local static guard — may have a number
                    pass
                if code2 == 'C':
                    # string — parse MDString
                    return ast.SpecialName(self._parse_md_string(), kind='string')
                return ast.SpecialName(name, kind='special')

            if code2 == 'R':
                # RTTI
                rtti_code = self._next()
                rtti_num = int(rtti_code) if rtti_code.isdigit() else -1
                if rtti_code in self.RTTI_NAMES:
                    return ast.SpecialName(self.RTTI_NAMES[rtti_code],
                                          kind='rtti', rtti_number=rtti_num)
                if rtti_code == '1':
                    # RTTI Base Class Descriptor — has 4 encoded numbers
                    a = self._parse_encoded_number()
                    b = self._parse_encoded_number()
                    c = self._parse_encoded_number()
                    d = self._parse_encoded_number()
                    return ast.SpecialName(
                        '`RTTI Base Class Descriptor at (%s,%s,%s,%s)\'' % (a, b, c, d),
                        kind='rtti', rtti_number=1)

            if code2 == '_':
                code3 = self._next()
                if code3 in self.OPERATORS_EXT3:
                    name = self.OPERATORS_EXT3[code3]
                    if code3 in ('E', 'F'):
                        # dynamic initializer/destructor for — needs object
                        obj = self._parse_fragment_name()
                        name = '%s%s\'' % (name, obj.name)
                    if code3 == 'K':
                        # UDL operator — needs fragment name
                        frag = self._parse_fragment_name()
                        name = 'operator "" %s' % frag.name
                    return ast.SpecialName(name, kind='special')

            raise ParseError('unknown operator code ?_%s' % code2)

        raise ParseError('unknown special name code %r' % code)

    def _parse_md_string(self):
        """Parse an MDString (embedded string data)."""
        # MDString format: length@@data
        # For now, return a placeholder
        chars = []
        while self._peek() != '@' and self._peek() != '\x00':
            chars.append(self._next())
        if self._peek() == '@':
            self._next()
        return ''.join(chars)

    # --- Type info parsing ---

    def _parse_type_info(self, rtti_num):
        """Parse the type info section (access, storage, function/variable type)."""
        is_based = False
        if self._peek() == '_':
            is_based = True
            self._next()

        code = self._peek()

        # $ prefix = special handling function
        if code == '$':
            self._next()
            return self._parse_special_handling_function(rtti_num)

        # Variable info (data)
        if code in '01234':
            self._next()
            access_map = {'0': 'private', '1': 'protected', '2': 'public'}
            access = access_map.get(code)
            is_static = code in '012'
            if code in '01234':
                var_type = None
                if not self._at_end():
                    var_type = self._parse_data_type()
                return ast.VariableInfo(access=access, is_static=is_static,
                                        var_type=var_type)

        if code == '5':
            self._next()
            return ast.VariableInfo(is_guard=True)

        if code == '6':
            self._next()
            # VFTable or RTTI4
            if rtti_num == 4:
                return ast.VFTable(scope=None)
            return ast.VFTable(scope=None)

        if code == '7':
            self._next()
            return ast.VFTable(scope=None)  # VBTable

        # Member function access codes
        # A-Z encode: access × (static/virtual/thunk) × (near/far)
        access_map = {
            'A': 'private', 'B': 'private',
            'C': 'private', 'D': 'private',
            'E': 'private', 'F': 'private',
            'G': 'private', 'H': 'private',
            'I': 'protected', 'J': 'protected',
            'K': 'protected', 'L': 'protected',
            'M': 'protected', 'N': 'protected',
            'O': 'protected', 'P': 'protected',
            'Q': 'public', 'R': 'public',
            'S': 'public', 'T': 'public',
            'U': 'public', 'V': 'public',
            'W': 'public', 'X': 'public',
        }

        if code in access_map:
            self._next()
            access = access_map[code]
            idx = ord(code) - ord('A')

            is_static = code in 'CDKLST'
            is_virtual = code in 'EFMNUV'
            is_thunk = code in 'GHWXOP'
            is_member = True

            # Parse function type — CV modifier only for non-static member functions
            has_cv = not is_static
            func = self._parse_function_type(is_member=True, has_cv_mod=has_cv)
            func.access = access
            func.is_static = is_static
            func.is_virtual = is_virtual
            if is_thunk:
                func.is_thunk = True
            return func

        if code in 'YZ':
            self._next()
            # Non-member function
            func = self._parse_function_type(is_member=False, has_cv_mod=False)
            return func

        raise ParseError('unknown type info code %r at pos %d' % (code, self.pos))

    def _parse_special_handling_function(self, rtti_num):
        """Parse $-prefixed special function type."""
        code = self._next()
        # Vtordisp, vcall, etc.
        if code in '012345':
            access_map = {'0': 'private', '1': 'private',
                          '2': 'protected', '3': 'protected',
                          '4': 'public', '5': 'public'}
            access = access_map.get(code, 'private')
            func = self._parse_function_type(is_member=True, has_cv_mod=True)
            func.access = access
            return func

        if code == '$':
            code2 = self._next()
            if code2 in 'JNO':
                # extern "C" — skip count then recurse
                cnt_ch = self._next()
                if cnt_ch.isdigit():
                    cnt = int(cnt_ch)
                    for _ in range(cnt):
                        self._next()
                inner = self._parse_type_info(rtti_num)
                return inner
            if code2 in 'FHLMQ':
                inner = self._parse_type_info(rtti_num)
                return inner
            if code2 == 'R':
                # vtordispex
                access_code = self._next()
                access_map = {'0': 'private', '1': 'private',
                              '2': 'protected', '3': 'protected',
                              '4': 'public', '5': 'public'}
                func = self._parse_function_type(is_member=True, has_cv_mod=True)
                func.access = access_map.get(access_code, 'private')
                return func
            if code2 == 'B':
                # vcall
                return ast.FunctionType(is_member=False)

        raise ParseError('unknown special handling function %r' % code)

    # --- Function type ---

    def _parse_function_type(self, is_member, has_cv_mod):
        """Parse a function type: calling convention, return type, args."""
        func = ast.FunctionType(is_member=is_member)

        # CV modifier for this pointer (member functions, non-static only)
        if has_cv_mod:
            func.cv_modifiers = self._parse_cv_mod()

        # Calling convention
        cc_code = self._next()
        func.calling_convention = self.CALLING_CONVENTIONS.get(cc_code, '')

        # Return type: @ means no return type (constructors/destructors)
        if self._peek() == '@':
            self._next()
            func.return_type = ''  # No return type for structors
        else:
            func.return_type = self._parse_data_type()

        # Arguments
        func.parameters = self._parse_arguments()

        # Throw attribute (optional, ends with Z or @)
        if self._peek() == 'Z':
            self._next()
        elif self._peek() == '@':
            self._next()

        return func

    def _parse_cv_mod(self):
        """Parse CV modifier for this pointer."""
        # CV modifier format: [E/F/N/O] qualifiers
        # E = __ptr32, F = __ptr32 __ptr64, etc.
        # Simpler: read until we hit a calling convention letter
        modifiers = []
        code = self._next()

        # CV modifier encoding:
        # A = none, B = const, C = volatile, D = const volatile
        # E = far, F = const far, G = volatile far, H = const volatile far
        # I = based(0), ...
        # N = __ptr64, O = const __ptr64, P = volatile __ptr64, Q = const volatile __ptr64
        cv_map = {
            'A': '', 'B': 'const', 'C': 'volatile', 'D': 'const volatile',
            'E': '', 'F': 'const', 'G': 'volatile', 'H': 'const volatile',
            'I': '', 'J': 'const', 'K': 'volatile', 'L': 'const volatile',
            'M': '', 'N': '', 'O': 'const', 'P': 'volatile', 'Q': 'const volatile',
        }

        result = cv_map.get(code, '')
        if not result and code not in cv_map:
            self.warnings.append('unknown CV modifier code %r' % code)
        return result

    def _parse_arguments(self):
        """Parse function argument list."""
        args = []
        while True:
            ch = self._peek()
            if ch == '\x00':
                break
            if ch == 'X':
                self._next()
                # void = end of arguments (either no args or void param)
                break
            if ch == 'Z':
                self._next()
                break
            if ch == '@':
                self._next()
                break
            try:
                arg_type = self._parse_data_type()
                if arg_type and arg_type != 'void':
                    args.append(arg_type)
            except ParseError:
                break
        return args

    # --- Data type parsing ---

    def _parse_data_type(self):
        """Parse a data type and return its string representation."""
        ch = self._peek()

        if ch == '\x00':
            raise ParseError('unexpected end of input parsing type')

        if ch == '?':
            self._next()
            # Custom type or question modifier
            return '?'

        if ch == 'X':
            self._next()
            return 'void'

        if ch == 'A':
            # Reference type: A = reference, then CV modifier, then referent
            self._next()
            cv_code = self._next()
            # For references, CV modifier is usually ignored in output (refs are always const)
            ref = self._parse_data_type()
            return ref + '&'

        if ch == 'B':
            # B = far reference variant (same as A for output)
            self._next()
            cv_code = self._next()
            ref = self._parse_data_type()
            return ref + '&'

        # Extended types ($)
        if ch == '$':
            self._next()
            ext_code = self._next()
            if ext_code == 'A':
                return self._parse_function_indirect_type()
            if ext_code == 'T':
                return 'std::nullptr_t'
            if ext_code == 'V':
                return ''
            if ext_code == 'Z':
                return '...'
            if ext_code == 'C':
                ref = self._parse_data_type()
                return ref + '&'
            if ext_code == 'Q':
                ref = self._parse_data_type()
                return ref + '&&'
            if ext_code == 'R':
                ref = self._parse_data_type()
                return ref + '&&'
            if ext_code == 'B':
                ref = self._parse_data_type()
                return ref + '*'
            self.warnings.append('unknown $ type code %r' % ext_code)
            return '$' + ext_code

        # Pointer types: P/Q/R/S followed by CV modifier code, then pointee
        if ch in 'PQRS':
            self._next()
            # Read the pointer's CV modifier
            ptr_cv = self._next()
            cv_map = {
                'A': '', 'B': 'const ', 'C': 'volatile ', 'D': 'const volatile ',
                'E': '', 'F': 'const ', 'G': 'volatile ', 'H': 'const volatile ',
            }
            cv = cv_map.get(ptr_cv, '')
            # Check if next is a function type (function pointer)
            pointee = self._parse_data_type()
            return '%s%s*' % (cv, pointee)

        # User-defined types
        if ch == 'T':
            self._next()
            qname = self._parse_qualified_name_type()
            return 'union ' + qname
        if ch == 'U':
            self._next()
            qname = self._parse_qualified_name_type()
            return 'struct ' + qname
        if ch == 'V':
            self._next()
            qname = self._parse_qualified_name_type()
            return 'class ' + qname
        if ch == 'W':
            self._next()
            # W4 prefix for enum — consume the '4'
            if self._peek() == '4':
                self._next()
            qname = self._parse_qualified_name_type()
            return 'enum ' + qname

        # Extended primitives (_ prefix)
        if ch == '_':
            self._next()
            ext_code = self._next()
            if ext_code == '$':
                inner = self._parse_data_type()
                return inner
            if ext_code in self.EXTENDED_PRIMITIVES:
                return self.EXTENDED_PRIMITIVES[ext_code]
            self.warnings.append('unknown extended type _%r' % ext_code)
            return '_' + ext_code

        # Primitive types
        if ch in self.PRIMITIVES:
            self._next()
            return self.PRIMITIVES[ch]

        raise ParseError('unknown type code %r at pos %d' % (ch, self.pos))

    def _parse_qualified_name_type(self):
        """Parse a qualified name used as a type (UDT name)."""
        parts = []
        while True:
            if self._peek() == '@':
                self._next()
                if self._peek() == '@':
                    self._next()
                break
            if self._peek() == '\x00':
                break
            if self._peek() == '?':
                # ?0 backref or ?A anonymous
                self._next()
                if self._peek() == 'A':
                    self._next()
                    parts.insert(0, '`anonymous namespace\'')
                else:
                    idx = self._next()
                    # Back-reference — TODO: resolve
                continue
            if self._peek() == '$':
                self._next()
                tmpl = self._parse_template_name()
                parts.insert(0, self._render_template(tmpl))
                continue
            frag = self._parse_fragment_name()
            parts.insert(0, frag.name)

        return '::'.join(parts)

    def _parse_function_indirect_type(self):
        """Parse a function indirect type ($A)."""
        func = self._parse_function_type(is_member=False, has_cv_mod=False)
        # Render as function pointer
        ret = func.return_type or 'void'
        params = ', '.join(func.parameters) if func.parameters else 'void'
        cc = func.calling_convention
        if cc:
            return '%s (%s*)(%s)' % (ret, cc, params)
        return '%s (*)(%s)' % (ret, params)

    def _parse_type_string(self):
        """Parse a type string (for template args)."""
        return self._parse_data_type()

    # --- Number parsing ---

    def _parse_encoded_number(self):
        """Parse an encoded number (used in RTTI, thunks)."""
        ch = self._next()
        if ch == '?':
            # Negative: next char + 1
            sign = self._next()
            return str(-ord(sign) + ord('A') - 1)
        if ch == '@':
            return '0'
        if ch == '$':
            # Hex encoding
            high = self._next()
            low = self._next()
            return str(int(high + low, 16))
        # Direct digit
        result = 0
        while ch != '@' and ch != '\x00':
            if ch.isdigit():
                result = result * 10 + int(ch)
            ch = self._next()
        return str(result)

    # --- Rendering helpers (for inline type strings) ---

    def _render_template(self, tmpl):
        """Render a template name as a string."""
        base = tmpl.base_name.name if hasattr(tmpl.base_name, 'name') else str(tmpl.base_name)
        args_str = ','.join(str(a) for a in tmpl.args)
        return '%s<%s>' % (base, args_str)

    # --- Embedded name ---

    def _parse_embedded_name(self):
        """Parse an embedded object name (??? prefix)."""
        # The third ? starts another symbol
        # For now, parse as qualified name
        return self._parse_qualified_name()