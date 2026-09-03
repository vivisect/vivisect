"""
vivisect.demangle.itanium.parser - Recursive descent parser for Itanium C++ ABI.

Parses mangled names like ``_ZN3foo3barEv`` into an AST of
``vivisect.demangle.itanium.ast_nodes`` objects.

The parser is a recursive descent parser with a cursor-based state object.
It maintains:
    - The input string and current position
    - A substitution table (list of AST nodes)
    - Template parameter context
    - A list of warnings (non-fatal parse issues)

Reference: Itanium C++ ABI section 5.1 (External Names)
           GNU libiberty cp-demangle.c
"""

import logging

from vivisect.demangle.itanium import ast_nodes as ast
from vivisect.demangle.itanium import grammar

logger = logging.getLogger(__name__)

__all__ = ['ItaniumParser', 'ParseError', 'parse']


class ParseError(Exception):
    """Raised when the parser cannot proceed."""
    pass


# Characters used for base-36 substitution indices
_DIGITS = '0123456789abcdefghijklmnopqrstuvwxyz'


class ItaniumParser:
    """
    Recursive descent parser for Itanium C++ ABI mangled names.

    Usage:
        parser = ItaniumParser('_ZN3foo3barEv')
        node = parser.parse()
    """

    def __init__(self, mangled):
        self.input = mangled
        self.pos = 0
        self.subs = []          # Substitution table (list of AST nodes)
        self.template_subs = [] # Template parameter substitutions (list of AST nodes)
        self.warnings = []
        self.last_name = None   # Last unqualified name (for ctor/dtor)
        self._is_conversion = False

    # --- Cursor helpers ---

    def _peek(self, offset=0):
        idx = self.pos + offset
        if idx < len(self.input):
            return self.input[idx]
        return ''

    def _remaining(self):
        return self.input[self.pos:]

    def _at_end(self):
        return self.pos >= len(self.input)

    def _consume_char(self):
        if self.pos >= len(self.input):
            raise ParseError('unexpected end of input at pos %d' % self.pos)
        c = self.input[self.pos]
        self.pos += 1
        return c

    def _check_char(self, c):
        return self._peek() == c

    def _expect_char(self, c):
        if self._peek() != c:
            raise ParseError('expected %r at pos %d, got %r' % (c, self.pos, self._peek()))
        self.pos += 1

    def _consume_if(self, c):
        if self._peek() == c:
            self.pos += 1
            return True
        return False

    # --- Number parsing ---

    def _parse_number(self):
        """Parse a positive integer (for source name lengths, array dims, etc.)."""
        start = self.pos
        if self._peek() == 'n':
            # Negative number (for some contexts)
            self.pos += 1
        while self._peek().isdigit():
            self.pos += 1
        if self.pos == start:
            raise ParseError('expected number at pos %d' % self.pos)
        s = self.input[start:self.pos]
        return int(s)

    def _parse_seq_id(self):
        """Parse a base-36 sequence ID (for substitutions)."""
        if not (self._peek().isdigit() or self._peek().isupper()):
            raise ParseError('expected seq-id at pos %d' % self.pos)
        id_val = 0
        while self._peek().isdigit() or self._peek().isupper():
            c = self._consume_char()
            if c.isdigit():
                id_val = id_val * 36 + (ord(c) - ord('0'))
            else:
                id_val = id_val * 36 + (ord(c) - ord('A') + 10)
        self._expect_char('_')
        return id_val + 1  # S_ is index 0, S0_ is index 1, etc.

    # --- Substitution management ---

    def _add_substitution(self, node):
        """Add a node to the substitution table."""
        self.subs.append(node)

    def _get_substitution(self, index):
        if index >= len(self.subs):
            raise ParseError('substitution index %d out of range (have %d)' %
                             (index, len(self.subs)))
        return self.subs[index]

    # --- Top-level grammar ---

    def parse(self):
        """Parse the full mangled name and return the root AST node."""
        if self.input.startswith('_Z') or self.input.startswith('__Z'):
            # Strip _Z or __Z prefix
            if self.input.startswith('__Z'):
                self.pos = 3
            else:
                self.pos = 2
            node = self._parse_encoding()
            # Vendor extension suffix (after '.')
            if self._peek() == '.':
                self.pos += 1  # skip the dot and the rest is vendor extension
            return node
        # Not a valid mangled name
        raise ParseError('not an Itanium mangled name (missing _Z prefix)')

    def _parse_encoding(self):
        """<encoding> ::= <function name> <bare-function-type>
                       ::= <data name>
                       ::= <special-name>"""
        if self._peek() == 'T' or self._peek() == 'G':
            return self._parse_special_name()

        # It's a name, possibly followed by a bare-function-type
        name = self._parse_name(substable=False)

        # Check for bare-function-type (only if there's more input and it
        # looks like a type list)
        if not self._at_end() and self._looks_like_type():
            bare_func = self._parse_bare_function_type(has_return=False)
            # Wrap in a Name node indicating this is a function
            if isinstance(name, ast.NestedName):
                name.bare_function = bare_func
            return ast.Name(name, is_function=True, bare_function=bare_func)

        return ast.Name(name, is_function=False)

    def _looks_like_type(self):
        """Heuristic: does the current position look like the start of a type?"""
        c = self._peek()
        if c == '':
            return False
        # Most type productions start with one of these
        if c in grammar.BUILTIN_TYPES or c in ('P', 'R', 'O', 'K', 'V', 'r',
                                               'F', 'A', 'M', 'N', 'S', 'T',
                                               'D', 'u', 'L', 'Z'):
            return True
        return False

    # --- Name parsing ---

    def _parse_name(self, substable=False):
        """<name> ::= <nested-name>
                   ::= <unscoped-name>
                   ::= <unscoped-template-name> <template-args>
                   ::= <local-name>"""
        c = self._peek()

        if c == 'N':
            return self._parse_nested_name(substable=substable)

        if c == 'Z':
            return self._parse_local_name()

        if c == 'S':
            # Could be a substitution (St, Sa, Ss, etc. used as a prefix)
            node = self._parse_substitution(prefix=True)
            if node is not None:
                if isinstance(node, ast.Substitution) and node.std_sub:
                    # St followed by a source name = std::name
                    if node.std_sub == 't' and self._peek().isdigit():
                        # St<source-name> = std::<source-name>
                        inner_name = self._parse_source_name()
                        # Check for template args after the name
                        if self._peek() == 'I':
                            targs = self._parse_template_args()
                            result = ast.NestedName(
                                [ast.SourceName('std'), ast.UnqualifiedName('source', inner_name)],
                                ast.UnqualifiedName('template', targs)
                            )
                            self._add_substitution(result)
                            return result
                        result = ast.NestedName(
                            [ast.SourceName('std')],
                            ast.UnqualifiedName('source', inner_name)
                        )
                        self._add_substitution(result)
                        return result
                    # Other std subs (Sa, Sb, Ss, Si, So, Sd) are complete names
                    return node
                # Check for template args after a substitution
                if self._peek() == 'I':
                    targs = self._parse_template_args()
                    prefix_name = grammar.STD_SUBS.get(node.std_sub, 'std') if isinstance(node, ast.Substitution) else 'std'
                    base = ast.SourceName(prefix_name)
                    result = ast.NestedName([base], ast.UnqualifiedName('template', targs))
                    return result
                return node

        # Unscoped name
        unq = self._parse_unqualified_name()
        if substable:
            self._add_substitution(unq)

        # Check for template args (unscoped-template-name)
        if self._peek() == 'I':
            targs = self._parse_template_args()
            # Build a template name: the base name + template args
            # Store as a NestedName where the prefix is the base name
            # and the unqualified_name is the template args
            result = ast.NestedName([unq], ast.UnqualifiedName('template', targs))
            if substable:
                self._add_substitution(result)
            return result

        return unq

    def _parse_nested_name(self, substable=False):
        """<nested-name> ::= N [<CV-qualifiers>] [<ref-qualifier>] <prefix> <unqualified-name> E

        The substable parameter controls whether the full nested name is added
        to the substitution table. When called from _parse_name (encoding level),
        it should be False — only intermediate prefixes are sub candidates, not
        the top-level encoding name. When called from _parse_type (as a type),
        it should be True.
        """
        self._expect_char('N')

        # CV-qualifiers
        cv = self._parse_cv_qualifiers()

        # ref-qualifier
        ref = ''
        if self._peek() == 'R':
            self.pos += 1
            ref = '&'
        elif self._peek() == 'O':
            self.pos += 1
            ref = '&&'

        # Parse the prefix chain
        prefix = self._parse_prefix()

        # The last element of the prefix is the unqualified name
        if not prefix:
            raise ParseError('empty nested name prefix at pos %d' % self.pos)

        unqualified = prefix[-1]
        prefix_chain = prefix[:-1]

        self._expect_char('E')

        node = ast.NestedName(prefix_chain, unqualified, cv, ref)

        # Only add to substitution table when used as a type (not encoding name)
        if substable:
            self._add_substitution(node)

        return node

    def _parse_prefix(self):
        """<prefix> ::= <prefix> <unqualified-name>
                     ::= <template-prefix> <template-args>
                     ::= ...
        Returns a list of nodes representing the scope chain.
        The template args are stored as a separate UnqualifiedName('template')
        entry, and the renderer combines them with the preceding name."""
        result = []

        while True:
            c = self._peek()
            if c == '' or c == 'E':
                break

            if c == 'S':
                # Substitution as a prefix component
                sub = self._parse_substitution(prefix=True)
                if sub is not None:
                    if isinstance(sub, ast.Substitution) and sub.std_sub:
                        if sub.std_sub == 't':
                            name = 'std'
                        else:
                            name = grammar.STD_SUBS.get(sub.std_sub, 'std')
                        result.append(ast.SourceName(name))
                    elif isinstance(sub, ast.Substitution) and sub.index is not None:
                        # Resolve indexed substitution to the actual node
                        if sub.index < len(self.subs):
                            actual = self.subs[sub.index]
                            if isinstance(actual, ast.NestedName):
                                # Flatten the NestedName's prefix into our result
                                result.extend(actual.prefix)
                                # Don't add the unqualified_name if template
                                # args follow (they replace it)
                                if self._peek() != 'I':
                                    result.append(actual.unqualified_name)
                            else:
                                result.append(actual)
                        else:
                            result.append(sub)
                    else:
                        result.append(sub)
                    # Check for template args after substitution
                    if self._peek() == 'I':
                        targs = self._parse_template_args()
                        result.append(ast.UnqualifiedName('template', targs))
                        # Add the combined substitution+template to subs
                        combined = ast.NestedName(
                            list(result[:-1]), result[-1]
                        )
                        self._add_substitution(combined)
                    continue
                break

            # Parse unqualified name
            unq = self._parse_unqualified_name()
            result.append(unq)

            # Check for template args
            if self._peek() == 'I':
                targs = self._parse_template_args()
                # The template-prefix (name without args) is a substitution candidate.
                # result currently has the name components without the template args.
                # Add it as a substitution before adding the template args.
                if len(result) == 1:
                    self._add_substitution(result[0])
                else:
                    self._add_substitution(ast.NestedName(list(result[:-1]), result[-1]))

                result.append(ast.UnqualifiedName('template', targs))
                # Also add the full template instantiation (prefix + args)
                template_full = ast.NestedName(
                    list(result[:-1]), result[-1]
                )
                self._add_substitution(template_full)

            if self._peek() == 'E':
                break

            # Add the current prefix chain to substitutions.
            # For the first component (result has 1 element), add it directly.
            # For longer chains, add as a NestedName.
            if not (result and isinstance(result[-1], ast.UnqualifiedName) and result[-1].kind == 'template'):
                if len(result) == 1:
                    self._add_substitution(result[0])
                else:
                    self._add_substitution(ast.NestedName(list(result[:-1]), result[-1]))

        return result

    def _parse_unqualified_name(self):
        """<unqualified-name> ::= <operator-name> [<abi-tags>]
                              ::= <ctor-dtor-name>
                              ::= <source-name>
                              ::= <unnamed-type-name>"""
        c = self._peek()

        if c == 'C':
            # Constructor: C1, C2, C3, CI1, CI2
            self.pos += 1
            kind_char = self._consume_char()
            if kind_char == 'I':
                # Inheriting constructor: CI1, CI2
                num = self._consume_char()
                kind = 'CI' + num
            else:
                kind = 'C' + kind_char
            ctor_kind = grammar.CTOR_KINDS.get(kind, kind)
            self.last_name = ast.CtorDtorName(ctor_kind, is_destructor=False)
            return ast.UnqualifiedName('ctor', self.last_name)

        if c == 'D':
            # Could be destructor D0, D1, D2 or a D* builtin type
            next_c = self._peek(1)
            if next_c in ('0', '1', '2'):
                self.pos += 1
                num = self._consume_char()
                kind = 'D' + num
                dtor_kind = grammar.DTOR_KINDS.get(kind, kind)
                self.last_name = ast.CtorDtorName(dtor_kind, is_destructor=True)
                return ast.UnqualifiedName('dtor', self.last_name)
            # Otherwise it's a D* builtin type — fall through to type parsing

        if c.isdigit():
            # Source name
            name = self._parse_source_name()
            self.last_name = name
            unq = ast.UnqualifiedName('source', name)

            # Check for ABI tags
            if self._peek() == 'B':
                tags = self._parse_abi_tags()
                unq.abi_tags = tags

            return unq

        # Operator name (two chars)
        if self.pos + 1 < len(self.input):
            c1 = self._consume_char()
            c2 = self._consume_char()
            code = c1 + c2
            if code in grammar.OPERATORS:
                sym, nargs = grammar.OPERATORS[code]
                op = ast.OperatorName(code, sym, nargs)
                self.last_name = op
                return ast.UnqualifiedName('operator', op)
            raise ParseError('unknown operator code %r at pos %d' % (code, self.pos - 2))

        raise ParseError('cannot parse unqualified name at pos %d' % self.pos)

    def _parse_source_name(self):
        """<source-name> ::= <positive length number> <identifier>"""
        length = self._parse_number()
        if self.pos + length > len(self.input):
            raise ParseError('source name length %d exceeds remaining input at pos %d' % (length, self.pos))
        name = self.input[self.pos:self.pos + length]
        self.pos += length
        return ast.SourceName(name)

    def _parse_abi_tags(self):
        """<abi-tags> ::= B <source-name> <abi-tags>*"""
        tags = []
        while self._peek() == 'B':
            self._consume_char()
            tag_name = self._parse_source_name()
            tags.append(tag_name.name)
        return tags

    # --- Type parsing ---

    def _parse_type(self):
        """<type> ::= <builtin-type>
                   ::= <function-type>
                   ::= <class-enum-type>
                   ::= <array-type>
                   ::= <pointer-to-member-type>
                   ::= <template-param>
                   ::= <template-template-param> <template-args>
                   ::= <substitution>
                   ::= <CV-qualifiers> <type>
                   ::= P <type>
                   ::= R <type>
                   ::= O <type>
                   ::= C <type>
                   ::= G <type>
                   ::= U <source-name> <type>"""
        # CV-qualifiers (K, V, r) come before the base type
        cv = self._parse_cv_qualifiers()
        if cv:
            base = self._parse_type()
            node = ast.CVQualifiedType(base, cv)
            self._add_substitution(node)
            return node

        c = self._peek()

        # Pointer, reference, rvalue reference
        if c == 'P':
            self.pos += 1
            target = self._parse_type()
            node = ast.PointerType(target)
            self._add_substitution(node)
            return node

        if c == 'R':
            self.pos += 1
            target = self._parse_type()
            node = ast.ReferenceType(target)
            self._add_substitution(node)
            return node

        if c == 'O':
            self.pos += 1
            target = self._parse_type()
            node = ast.RvalueReferenceType(target)
            self._add_substitution(node)
            return node

        # Function type
        if c == 'F':
            node = self._parse_function_type()
            self._add_substitution(node)
            return node

        # Array type
        if c == 'A':
            node = self._parse_array_type()
            self._add_substitution(node)
            return node

        # Pointer to member
        if c == 'M':
            self.pos += 1
            class_type = self._parse_type()
            member_type = self._parse_type()
            node = ast.PointerToMember(class_type, member_type)
            self._add_substitution(node)
            return node

        # Substitution
        if c == 'S':
            sub = self._parse_substitution(prefix=False)
            if sub is not None:
                # St followed by a source name = std::<name> as a type
                if isinstance(sub, ast.Substitution) and sub.std_sub == 't' and self._peek().isdigit():
                    inner_name = self._parse_source_name()
                    # Check for template args
                    if self._peek() == 'I':
                        targs = self._parse_template_args()
                        result = ast.NestedName(
                            [ast.SourceName('std'), ast.UnqualifiedName('source', inner_name)],
                            ast.UnqualifiedName('template', targs)
                        )
                        self._add_substitution(result)
                        return result
                    result = ast.NestedName(
                        [ast.SourceName('std')],
                        ast.UnqualifiedName('source', inner_name)
                    )
                    self._add_substitution(result)
                    return result
                # Could be followed by template args (template-template-param)
                if self._peek() == 'I':
                    targs = self._parse_template_args()
                    # Wrap in a template instantiation
                    return ast.NestedName([sub], ast.UnqualifiedName('template', targs))
                return sub

        # Template parameter
        if c == 'T':
            return self._parse_template_param()

        # Builtin type (single char or D* extended)
        if c in grammar.BUILTIN_TYPES:
            self.pos += 1
            return ast.BuiltinType(grammar.BUILTIN_TYPES[c], c)

        if c == 'D':
            # Extended builtin type (Dd, De, Df, etc.)
            if self.pos + 1 < len(self.input):
                code = self.input[self.pos:self.pos + 2]
                if code in grammar.EXTENDED_BUILTIN_TYPES:
                    self.pos += 2
                    return ast.BuiltinType(grammar.EXTENDED_BUILTIN_TYPES[code], code)
                # DF<number>_ = _Float<number>
                if self._peek(1) == 'F':
                    self.pos += 2
                    num = self._parse_number()
                    self._expect_char('_')
                    return ast.BuiltinType('_Float%d' % num, 'DF%d_' % num)
            # Fall through: D could also be a destructor (handled elsewhere)

        # Vendor extended type: u <source-name>
        if c == 'u':
            self.pos += 1
            name = self._parse_source_name()
            template_args = None
            if self._peek() == 'I':
                template_args = self._parse_template_args()
            node = ast.VendorExtendedType(name.name, template_args)
            self._add_substitution(node)
            return node

        # Nested name (class/enum type as a qualified name)
        if c == 'N':
            return self._parse_nested_name(substable=True)

        # Source name as a class-enum-type (unqualified)
        if c.isdigit():
            name = self._parse_source_name()
            # Check for template args
            if self._peek() == 'I':
                targs = self._parse_template_args()
                node = ast.NestedName([name], ast.UnqualifiedName('template', targs))
                self._add_substitution(node)
                return node
            self._add_substitution(name)
            return name

        # Decltype
        if c == 'D' and self._peek(1) == 't':
            self.pos += 2
            expr = self._parse_until_char('E')
            self._expect_char('E')
            return ast.Decltype(expr, is_template=False)

        if c == 'D' and self._peek(1) == 'T':
            self.pos += 2
            expr = self._parse_until_char('E')
            self._expect_char('E')
            return ast.Decltype(expr, is_template=True)

        raise ParseError('cannot parse type at pos %d (char=%r)' % (self.pos, c))

    def _parse_cv_qualifiers(self):
        """Parse CV-qualifiers (K=const, V=volatile, r=restrict)."""
        parts = []
        while True:
            c = self._peek()
            if c == 'K':
                parts.append('const')
                self.pos += 1
            elif c == 'V':
                parts.append('volatile')
                self.pos += 1
            elif c == 'r':
                parts.append('restrict')
                self.pos += 1
            else:
                break
        return ' '.join(parts)

    def _parse_function_type(self):
        """<function-type> ::= F [Y] <bare-function-type> [<ref-qualifier>] E"""
        self._expect_char('F')
        # Y = extern "C"
        self._consume_if('Y')
        bare = self._parse_bare_function_type(has_return=True)
        cv = self._parse_cv_qualifiers()
        ref = ''
        if self._peek() == 'R':
            self.pos += 1
            ref = '&'
        elif self._peek() == 'O':
            self.pos += 1
            ref = '&&'
        self._expect_char('E')
        return ast.FunctionType(bare, cv, ref)

    def _parse_bare_function_type(self, has_return=False):
        """<bare-function-type> ::= <type>+"""
        types = []
        if has_return:
            # First type is the return type
            ret = self._parse_type()
            types.append(ret)
        # Remaining types are parameters
        while not self._at_end() and self._peek() != 'E' and self._peek() != 'N':
            # Check if we've hit something that's clearly not a type
            if not self._looks_like_type() and self._peek() not in grammar.BUILTIN_TYPES:
                break
            # Save position — _parse_type() may advance before failing
            saved_pos = self.pos
            try:
                t = self._parse_type()
                types.append(t)
            except ParseError:
                # Restore position so caller can see what stopped us
                self.pos = saved_pos
                break
        return ast.BareFunctionType(types)

    def _parse_array_type(self):
        """<array-type> ::= A <dimension> _ <type>"""
        self._expect_char('A')
        # Dimension: could be a number or an expression
        dim_start = self.pos
        if self._peek().isdigit():
            while self._peek().isdigit():
                self.pos += 1
        elif self._peek() == '_':
            pass  # empty dimension
        else:
            # Expression-based dimension (template param reference, etc.)
            self._parse_until_char('_')
        dim = self.input[dim_start:self.pos]
        self._expect_char('_')
        element = self._parse_type()
        return ast.Array(dim, element)

    def _parse_template_param(self):
        """<template-param> ::= T_ # first param
                            ::= T <parameter-2 non-negative number> _"""
        self._expect_char('T')
        if self._peek() == '_':
            self.pos += 1
            return ast.TemplateParam(0)
        num = self._parse_number()
        self._expect_char('_')
        return ast.TemplateParam(num + 1)

    def _parse_template_args(self):
        """<template-args> ::= I <template-arg>+ E"""
        self._expect_char('I')
        args = []
        while self._peek() != 'E' and not self._at_end():
            arg = self._parse_template_arg()
            args.append(arg)
        self._expect_char('E')
        node = ast.TemplateArgs(args)
        # NOTE: Template args themselves are NOT added to the substitution
        # table.  The template-prefix (name before the args) is the
        # substitution candidate, not the args.
        return node

    def _parse_template_arg(self):
        """<template-arg> ::= <type>
                           ::= X <expression> E
                           ::= <expr-primary>
                           ::= J <template-arg>* E"""
        c = self._peek()
        if c == 'X':
            # Expression
            self.pos += 1
            expr = self._parse_until_char('E')
            self._expect_char('E')
            return ast.TemplateArg('expression', expr)
        if c == 'J':
            # Argument pack
            self.pos += 1
            pack_args = []
            while self._peek() != 'E' and not self._at_end():
                pack_args.append(self._parse_template_arg())
            self._expect_char('E')
            return ast.TemplateArg('pack', pack_args)
        if c == 'L':
            # Expr-primary: L <type> <value> E
            self.pos += 1
            type_node = self._parse_type()
            value = self._parse_until_char('E')
            self._expect_char('E')
            # Render the type properly and convert known value formats
            if isinstance(type_node, ast.BuiltinType):
                type_name = type_node.name
                # For bool, convert 0->false, 1->true
                if type_name == 'bool':
                    if value == '0':
                        value = 'false'
                    elif value == '1':
                        value = 'true'
                # For integer types, render as the decimal value
                # c++filt shows e.g. '42' for Li42E
                elif value.isdigit() or (value.startswith('n') and value[1:].isdigit()):
                    if value.startswith('n'):
                        value = '-' + value[1:]
                # For char, show the character
                elif type_name == 'char' and len(value) <= 3:
                    pass  # keep as-is
                return ast.TemplateArg('primary', '%s' % value)
            # Fallback: render as type+value
            from vivisect.demangle.itanium.renderer import render as _render
            type_str = _render(type_node)
            return ast.TemplateArg('primary', '%s%s' % (type_str, value))
        # Default: it's a type
        type_node = self._parse_type()
        return ast.TemplateArg('type', type_node)

    def _parse_substitution(self, prefix=False):
        """<substitution> ::= S <seq-id> _
                           ::= S_
                           ::= St | Sa | Sb | Ss | Si | So | Sd"""
        if self._peek() != 'S':
            return None
        self.pos += 1  # consume S
        c = self._peek()
        if c == '_':
            self.pos += 1
            return ast.Substitution(index=0)
        if c.isdigit() or c.isupper():
            # seq-id
            id_val = self._parse_seq_id()
            return ast.Substitution(index=id_val)
        # Standard substitution
        if c in grammar.STD_SUBS:
            self.pos += 1
            sub = ast.Substitution(std_sub=c)
            # Check for ABI tags
            if self._peek() == 'B':
                tags = self._parse_abi_tags()
                # Tags make it a substitution candidate
                self._add_substitution(sub)
            return sub
        raise ParseError('invalid substitution at pos %d' % self.pos)

    def _parse_special_name(self):
        """<special-name> ::= TV <type>   # vtable
                           ::= TT <type>   # VTT
                           ::= TI <type>   # typeinfo
                           ::= TS <type>   # typeinfo name
                           ::= T <call-offset> <base encoding>  # thunk
                           ::= GV <object name>  # guard variable
                           ::= GR <object name> _  # lifetime-extended temporary
                           ::= GTt <encoding>  # transaction clone"""
        if self._peek() == 'T':
            self.pos += 1
            c = self._consume_char()
            code = 'T' + c

            # Handle two-char special names
            if c == 'T':
                kind = grammar.SPECIAL_NAMES.get('TT', 'VTT')
                target = self._parse_type()
                return ast.SpecialName(kind, target)
            if c == 'V':
                kind = grammar.SPECIAL_NAMES.get('TV', 'vtable')
                target = self._parse_type()
                return ast.SpecialName(kind, target)
            if c == 'I':
                kind = grammar.SPECIAL_NAMES.get('TI', 'typeinfo')
                target = self._parse_type()
                return ast.SpecialName(kind, target)
            if c == 'S':
                kind = grammar.SPECIAL_NAMES.get('TS', 'typeinfo name')
                target = self._parse_type()
                return ast.SpecialName(kind, target)
            if c == 'F':
                kind = grammar.SPECIAL_NAMES.get('TF', 'typeinfo fn')
                target = self._parse_type()
                return ast.SpecialName(kind, target)
            if c == 'J':
                kind = grammar.SPECIAL_NAMES.get('TJ', 'java class')
                target = self._parse_type()
                return ast.SpecialName(kind, target)
            if c == 'H':
                kind = grammar.SPECIAL_NAMES.get('TH', 'tls init')
                target = self._parse_name()
                return ast.SpecialName(kind, target)
            if c == 'W':
                kind = grammar.SPECIAL_NAMES.get('TW', 'tls wrapper')
                target = self._parse_name()
                return ast.SpecialName(kind, target)
            if c == 'A':
                kind = grammar.SPECIAL_NAMES.get('TA', 'template parm')
                target = self._parse_template_arg()
                return ast.SpecialName(kind, target)
            if c == 'C':
                # Construction vtable: TC <type> <number> _ <type>
                kind = grammar.SPECIAL_NAMES.get('TC', 'construction vtable')
                derived = self._parse_type()
                offset = self._parse_number()
                self._expect_char('_')
                base = self._parse_type()
                return ast.SpecialName(kind, base)
            if c == 'h':
                # Non-virtual thunk: Th <offset> _ <encoding>
                self._parse_call_offset('h')
                kind = grammar.SPECIAL_NAMES.get('Th', 'thunk')
                target = self._parse_encoding()
                return ast.SpecialName(kind, target)
            if c == 'v':
                # Virtual thunk: Tv <offset> _ <offset> _ <encoding>
                self._parse_call_offset('v')
                kind = grammar.SPECIAL_NAMES.get('Tv', 'virtual thunk')
                target = self._parse_encoding()
                return ast.SpecialName(kind, target)
            if c == 'c':
                # Covariant thunk: Tc <offset> _ <offset> _ <encoding>
                self._parse_call_offset('')
                self._parse_call_offset('')
                kind = grammar.SPECIAL_NAMES.get('Tc', 'covariant thunk')
                target = self._parse_encoding()
                return ast.SpecialName(kind, target)

            raise ParseError('unknown special name T%c at pos %d' % (c, self.pos - 1))

        if self._peek() == 'G':
            self.pos += 1
            c = self._consume_char()
            if c == 'V':
                kind = grammar.SPECIAL_NAMES.get('GV', 'guard variable')
                target = self._parse_name()
                return ast.SpecialName(kind, target)
            if c == 'R':
                kind = grammar.SPECIAL_NAMES.get('GR', 'reference temp')
                target = self._parse_name()
                self._consume_if('_')
                return ast.SpecialName(kind, target)
            if c == 'A':
                kind = grammar.SPECIAL_NAMES.get('GA', 'hidden alias')
                target = self._parse_encoding()
                return ast.SpecialName(kind, target)
            if c == 'T':
                # GTt or GTn
                next_c = self._consume_char()
                code = 'GT' + next_c
                kind = grammar.SPECIAL_NAMES.get(code, 'transaction clone')
                target = self._parse_encoding()
                return ast.SpecialName(kind, target)

            raise ParseError('unknown special name G%c at pos %d' % (c, self.pos - 1))

        raise ParseError('not a special name at pos %d' % self.pos)

    def _parse_call_offset(self, c):
        """Parse a call-offset: h <number> _ or v <number> _ <number> _"""
        if c == '':
            c = self._consume_char()
        if c == 'h':
            self._parse_number()
            self._expect_char('_')
        elif c == 'v':
            self._parse_number()
            self._expect_char('_')
            self._parse_number()
            self._expect_char('_')
        else:
            raise ParseError('invalid call offset %r' % c)

    def _parse_local_name(self):
        """<local-name> ::= Z <function encoding> E <entity name> [<discriminator>]
                         ::= Z <function encoding> E s [<discriminator>]"""
        self._expect_char('Z')
        func = self._parse_encoding()
        self._expect_char('E')
        if self._peek() == 's':
            self.pos += 1
            self._parse_discriminator()
            return func  # string literal
        name = self._parse_name()
        self._parse_discriminator()
        return ast.NestedName([func], name)

    def _parse_discriminator(self):
        """<discriminator> ::= _ <non-negative number> _"""
        if self._peek() == '_':
            self.pos += 1
            self._parse_number()
            self._consume_if('_')

    def _parse_until_char(self, end_char):
        """Parse raw characters until the end char (for expressions)."""
        start = self.pos
        depth = 0
        while self.pos < len(self.input):
            c = self.input[self.pos]
            if c == end_char and depth == 0:
                break
            self.pos += 1
        return self.input[start:self.pos]


def parse(mangled):
    """
    Parse an Itanium mangled name and return the AST root node.

    Args:
        mangled (str): The mangled name (with _Z prefix).

    Returns:
        Node: The root AST node.

    Raises:
        ParseError: If the name cannot be parsed.
    """
    parser = ItaniumParser(mangled)
    return parser.parse()