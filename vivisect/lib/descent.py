'''
Descent into madness...  A recursive descent parser generator.
'''
import itertools

white = set(' \t\r\n')
binchars= set('01')
numchars = set('01234567890')
hexchars = set('0123456789abcdefABCDEF')
idenchars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789')

#class tok(string):
#class stmt(string):
    #def __eq__(self, o):

class Stream:

    def __init__(self, desc, src):
        self.off = 0
        self.src = src
        self.desc = desc

    def tokens(self, count):
        '''
        Parse and return the specified number of tokens ( or None )
        '''
        tokiter = self.desc.tokenize(self.src, off=self.off)
        ret = list( itertools.islice(tokiter, count) )
        if len(ret) != count:
            return None
        return ret

    def isdef(self, exprdef):
        '''
        Compare the specified token chars with the next tokens for equality.
        If they match, consume and return the tokens, otherwise return None.
        '''
        cnt = len(exprdef)

        toks = self.tokens(cnt)
        if toks == None:
            return None

        for tok,expr in 

        for i in range(cnt):
            if toks[i][1] != cmptoks[i]:
                return None

        self.off = toks[-1][2].get('end')
        return toks

    def parse(self, name):
        '''
        Attempt to parse and return an AST for the given type.
        '''
        self.desc._parse(name,self)

def token(ttype,tstr,**tinfo):
    return (ttype,tstr,tinfo)

class Descent:
    '''
    Descent is recursive descent parser for defining hybrid bnf language parsers.
    '''
    def __init__(self):
        self.tokens = []        # a list of static tokens
        self.parsers = []       # token parser callbacks
        self.descenders = {}    # add a recursive descent parser

        self._expr_defs = collections.defaultdict(list)
        self._expr_parsers = collections.defaultdict(list)

    def addExprSyntax(self, name, *exprdef):
        self._expr_defs[name].append( exprdef )

    def addExprParser(self, name, callback):
        self._expr_callbacks[name].apppend( callback )

    #def addDescent(self, name, callback):
        #self.descenders[name] = callback

    def initIntTokens(self):
        '''
        Shorthand way to enable numeric parsing of int tokens.
        The default parser accepts the following syntaxes:
        1234    - the integer 1234
        0xff  - the hex integer 255
        0b0101  - the bin integer 5
        '''
        self.parsers.append( self._tok_int )

    def initIdentTokens(self, chars=idenchars):

        def _tok_ident(src,off):
            s = eat(src,off,chars)
            if s:
                return ('ident',s,{'off':off,'end':off + len(s)})

        self.parsers.append( _tok_ident )

    def _tok_int(self, src, off):

        print('_tok_int')
        if src.startswith('0x',off):
            s = eat(src,off+2,hexchars)
            if s:
                val = int(s,16)
                return token('intconst','0x' + s, off=off, val=val, end=off + len(s) + 2)

        if src.startswith('0b',off):
            s = eat(src,off+2,binchars)
            if s:
                val = int(s,2)
                return token('intconst','0b%s' % s, off=off, val=val, end=off + len(s) + 2)

        s = eat(src,off,numchars)
        if s:
            newoff = off + len(s)
            return token('intconst',s, off=off, val=int(s), end=off + len(s))

    #def _tok_str(self, src, off):

    def addStaticToken(self, toktype, tokstr):
        '''
        Add a static token to the parser with a token type.

        Example:
            d.addStaticToken('+','addsub')
        '''
        self.tokens.append((toktype,tokstr))

    def addTokenParser(self, callback):
        self.parsers.append(callback)

    #def callTokenParser(self, name, tokstream, offset):
        #'''
        #Call a token stream parser with the given tokens and offset.
        #'''

    def _tok_static(self,src,off,tokdefs):
        '''
        Check src starting at off for beginning with a static token.

        Returns: (off,tok) # updated offset and token or (off,None)
        '''
        for toktype,tokstr in tokdefs:
            if src.startswith(tokstr,off):
                return (toktype,tokstr,{'off':off,'end':off + len(tokstr)})

    def tokenize(self, src, off=0):
        '''
        Yields tokens from the given source string.

        NOTE: This is implemented as a yield generator to allow
              tokens/types and token parsers to be dynamically
              updated during parsing.
        '''
        maxoff = len(src)

        tokdefs = list(self.tokens)
        tokdefs.sort( key=_tokdef_key, reverse=True )

        while off < maxoff:
            off += len( eat(src,off,white) )
            if off >= maxoff:
                break

            # check for static tokens...
            tok = self._tok_static(src,off,tokdefs)
            if tok != None:

                yield tok

                off = tok[2]['end']
                continue

            # give the token parsers a shot
            for p in self.parsers:
                tok = p(src,off)
                if tok != None:
                    break

            if tok != None:

                yield tok

                off = tok[2]['end']
                continue

            raise Exception('Invalid Tokens (offset: %d) %s' % (off,src[off:off+20]))

        #return ret

    #def nexttypes(self, toks, off, *ttypes):
        #'''
        #Compare the specified types with the next tokens for equality.
        #'''
        #for i in range(len(ttypes)):
            #offi = off + i
            #if offi >= len(toks):
                #return False
            #if toks[offi][0] != ttypes[i]:
                #return False
        #return True

    def stream(self, src):
        '''
        Retrieve a stream parser for the given src.
        '''
        return Stream(self, src)

    def _parse(self, name, stream):
        '''
        Parse the token stream for a statement type.

        Example:
            toks = d.getTokenStream(src)
            off,retval = d.parse('assignexpr',toks)
        '''
        # give all parser callbacks precedence
        for cb in self._expr_parsers.get(name,()):
            ret = cb(stream)
            if ret != None:
                return ret

        for exprdef in self._expr_defs.get(name,()):
            toks = stream.nexttypes

        #toks = self.getTokenStream(src)
        #return self.parse(desc,toks,0)
        cb = self.descenders.get(name)
        if cb == None:
            raise Exception('No Such Descender: %s' % name)

        return cb(stream)

def eat(src,off,chrset,ttype=None):
    '''
    Eat chars in charset from src starting at off.

    Returns: (off,tok) # updated offset, and any parsed chars...
    '''
    s = ''
    #start = off
    while off < len(src) and src[off] in chrset:
        s += src[off]
        off += 1
    return s

def _tokdef_key(t):
    return len(t[1])

if __name__ == '__main__':
    d = Descent()

    [ d.addStaticToken('bits',c) for c in ('&','|','^','!','<<','>>') ]
    [ d.addStaticToken('addsub',c) for c in ('+','-') ]
    [ d.addStaticToken('muldiv',c) for c in ('*','/','%') ]
    [ d.addStaticToken('cond',c) for c in ('<','>','<=','>=','==') ]
    #[ d.addStaticToken('prec',c) for c in ('(',')') ]
    [ d.addStaticToken('assignop',c) for c in ('=','+=','-=','*=','/=','%=','&=','|=','^=','<<=','>>=') ]

    d.addStaticToken('paren-open','(')
    d.addStaticToken('paren-close',')')

    d.addStaticToken('brace-open','{')
    d.addStaticToken('brace-close','}')

    # int tokens first to prevent ident's beginning with nums
    d.initIntTokens()
    d.initIdentTokens()

    def statement(desc,toks,off):
        off,ast = desc.parse('assignexpr',toks,off)
        if ast != None: return off,ast

        off,ast = desc.parse('expression',toks,off)
        if ast != None: return off,ast

    #def callexpr(desc,toks,off):
        #if not desc.nexttypes(toks,off,'ident') and desc.nexttoks(toks,off+1,'('):
            #return off,None

    def assignexpr(stream):
        toks = stream.nexttypes('ident','assign','expression')
        if toks != None:
            expr = stream.parse('expression')
            return (
        
        if stream.nexttypes('ident','assign'):
            ident = toks[off][1]
            off,expr = desc.parse('expression',toks,off+2)
            if expr != None:
                print('ASSIGN!')
                return off,(ident,'=',expr)

        return off,None

    def expression(desc,toks,off):
        #if desc.nexttoks(toks,off,('(',)):
            #off,expr = desc.parse('expression',toks,off+1)
        #if desc.nexttoks(toks,off,('ident','math'

        #off,ast = desc.parse('callexpr',toks,off)
        #if ast != None: return off,ast

        off,ast = desc.parse('addsubexpr',toks,off)
        if ast != None: return off,ast
        #if ast != None:
            #print('VAL1 %r' % (ast,))
            ##print('NEXT TOKS',toks[off])
            #if desc.nexttypes(toks,off,'math'):
                #print('MATHS')
                #oper = toks[off][1]
                #off,val2 = desc.parse('expression',toks,off+1)
                #if val2 != None:
                    #print("FULL EXPRESSION!")
                    #return off,(ast,oper,val2)
            #return off,ast
        #return off,None

    #def addsubexpr(desc,toks,off):
        #off,ast = desc.parse('muldivexpr',toks,off)
        #if desc.nexttypes(toks,off,'addsub'):
            #oper = toks[off][1]
            #off,nextast = desc.parse('addsubexpr',toks,off+1)
            #print('ADDSUB!')
            #return off,(ast,oper,nextast)
        #return off,None

    #def muldivexpr(desc,toks,off):
        #off,ast = desc.parse('bitsexpr',toks,off)
        #if desc.nexttypes(toks,off,'muldiv'):
            #pass

    #def bitsexpr(desc,toks,off):
        #off,ast = desc.parse('valueexpr',toks,off)
        #if ast and desc.nexttypes(toks,off,'bits'):
            #pass

    #def valueexpr(desc,toks,off):
        #off,ast = desc.parse('constexpr',toks,off)
        #if ast: return off,ast

        #off,ast = desc.parse('identexpr',toks,off)
        #if ast: return off,ast

        #return off,None

    def constexpr(stream):
        toks = stream.nexttypes('intconst')
        if toks != None:
            return toks[0]

        toks = stream.nexttypes('strconst')
        if toks != None:
            return toks[0]

    def primaryexpr(stream):
        #toks = stream.nexttypes('(', 
        toks = stream.nexttypes('ident')
        if toks != None:
            return toks[0]

        toks = stream.nexttypes('constexpr')
        if toks != None:
            return toks[0]

    #def identexpr(desc,toks,off):
        #if desc.nexttypes(toks,off,'ident'):
            #print('AST ROOT IDENT %s' % toks[off][1])
            #return off+1,toks[off]
        #return off,None

    #def intconst(desc,toks,off):
        #if desc.nexttypes(toks,off,'int'):
            #print('AST ROOT INT')
            #return off+1,toks[off]
        #return off,None

    #def mathexpr(desc,toks,off):
        #if desc.nexttoks(toks,off,'int
    #def bitsexpr(desc,toks,off):
    #def callexpr(desc,toks,off):

    #d.addDescent('assignexpr',assignexpr)
    #d.addDescent('expression',expression)

    #d.addDescent('addsubexpr',addsubexpr)
    #d.addDescent('muldivexpr',muldivexpr)

    #d.addDescent('valueexpr',valueexpr)
    #d.addDescent('identexpr',identexpr)
    #d.addDescent('constexpr',constexpr)
    #d.addDescent('intconst',intconst)

    print(list(d.tokenize('ebx = eax + 0x20')))

    stream = d.stream('ebx = eax + 20')
    print(stream.parse('assignexpr'))
    #off,ast = d.parse('assignexpr',toks)
    #print('parsed: %d %s' % (off,ast))
    #print(d.parse('ebx = eax + 20','assignexpr'))
