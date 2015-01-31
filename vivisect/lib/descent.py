'''
Descent into madness.
'''

white = set(' \t\r\n')
binchars= set('01')
numchars = set('01234567890')
hexchars = set('0123456789abcdefABCDEF')
idenchars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789')

class Descent:
    '''
    Descent is recursive descent parser for defining hybrid bnf language parsers.
    '''
    def __init__(self):
        self.tokens = []        # a list of static tokens
        self.parsers = []       # token parser callbacks
        self.descenders = {}    # add a recursive descent parser

    def addDescent(self, name, callback):
        self.descenders[name] = callback

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
                return off+len(s),('ident',s,{'off':off})
            return off,None

        self.parsers.append( _tok_ident )

    def _tok_int(self, src, off):

        print('_tok_int')
        if src.startswith('0x',off):
            s = eat(src,off+2,hexchars)
            if s:
                val = int(s,16)
                newoff = off + len(s) + 2
                return newoff,('int','0x%s' % s,{'off':off,'val':val})

        if src.startswith('0b',off):
            s = eat(src,off+2,binchars)
            if s:
                val = int(s,2)
                newoff = off + len(s) + 2
                return newoff,('int','0b%s' % s,{'off':off,'val':val})

        s = eat(src,off,numchars)
        if s:
            newoff = off + len(s)
            return newoff,('int',s,{'off':off,'val':int(s)})

        return off,None

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
                # FIXME make it report ttype?
                return (off + len(tokstr), (toktype,tokstr,{'off':off}))
        return (off,None)

    def tokenize(self,src):
        '''
        Yields tokens from the given source string.

        NOTE: This is implemented as a yield generator to allow
              tokens/types and token parsers to be dynamically
              updated during parsing.
        '''
        off = 0
        maxoff = len(src)

        tokdefs = list(self.tokens)
        tokdefs.sort( key=_tokdef_key, reverse=True )

        while off < maxoff:
            off += len( eat(src,off,white) )
            if off >= maxoff:
                break

            # check for static tokens...
            off,tok = self._tok_static(src,off,tokdefs)
            if tok != None:
                yield tok
                continue

            # give the token parsers a shot
            for p in self.parsers:
                off,tok = p(src,off)
                if tok != None:
                    break

            if tok != None:
                yield tok
                continue

            raise Exception('Invalid Tokens (offset: %d) %s' % (off,src[off:off+20]))

        return ret

    def nexttypes(self, toks, off, *ttypes):
        '''
        Compare the specified types with the next tokens for equality.
        '''
        for i in range(len(ttypes)):
            offi = off + i
            if offi >= len(toks):
                return False
            if toks[offi][0] != ttypes[i]:
                return False
        return True

    def nexttoks(self, toks, off, *cmptoks):
        '''
        Compare the specified token chars with the next tokens for equality.
        '''
        for i in range(len(cmptoks)):
            offi = off + i
            if offi >= len(toks):
                return False
            if toks[offi][1] != cmptoks[i]:
                return False
        return True

    def parse(self, name, toks, off=0):
        '''
        Parse the token stream for a statement type.

        Example:
            toks = d.getTokenStream(src)
            off,retval = d.parse('assignment',toks)
        '''
        #toks = self.getTokenStream(src)
        #return self.parse(desc,toks,0)
        cb = self.descenders.get(name)
        if cb == None:
            raise Exception('No Such Descender: %s' % name)
        return cb(self,toks,off)

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
    [ d.addStaticToken('prec',c) for c in ('(',')') ]
    [ d.addStaticToken('assign',c) for c in ('=',) ]

    # int tokens first to prevent ident's beginning with nums
    d.initIntTokens()
    d.initIdentTokens()

    def statement(desc,toks,off):
        off,ast = desc.parse('assignment',toks,off)
        if ast != None: return off,ast

        off,ast = desc.parse('expression',toks,off)
        if ast != None: return off,ast

    #def callexpr(desc,toks,off):
        #if not desc.nexttypes(toks,off,'ident') and desc.nexttoks(toks,off+1,'('):
            #return off,None

    def assignment(desc,toks,off):
        if desc.nexttypes(toks,off,'ident','assign'):
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

    def addsubexpr(desc,toks,off):
        off,ast = desc.parse('muldivexpr',toks,off)
        if desc.nexttypes(toks,off,'addsub'):
            oper = toks[off][1]
            off,nextast = desc.parse('addsubexpr',toks,off+1)
            print('ADDSUB!')
            return off,(ast,oper,nextast)
        return off,None

    def muldivexpr(desc,toks,off):
        off,ast = desc.parse('bitsexpr',toks,off)
        if desc.nexttypes(toks,off,'muldiv'):

    def bitsexpr(desc,toks,off):
        off,ast = desc.parse('valueexpr',toks,off)
        if ast and desc.nexttypes(toks,off,'bits'):

    def valueexpr(desc,toks,off):
        off,ast = desc.parse('constexpr',toks,off)
        if ast: return off,ast

        off,ast = desc.parse('identexpr',toks,off)
        if ast: return off,ast

        return off,None

    def constexpr(desc,toks,off):
        off,ast = desc.parse('intconst',toks,off)
        if ast: return off,ast
        return off,None

    def identexpr(desc,toks,off):
        if desc.nexttypes(toks,off,'ident'):
            print('AST ROOT IDENT %s' % toks[off][1])
            return off+1,toks[off]
        return off,None

    def intconst(desc,toks,off):
        if desc.nexttypes(toks,off,'int'):
            print('AST ROOT INT')
            return off+1,toks[off]
        return off,None

    #def mathexpr(desc,toks,off):
        #if desc.nexttoks(toks,off,'int
    #def bitsexpr(desc,toks,off):
    #def callexpr(desc,toks,off):

    d.addDescent('assignment',assignment)
    d.addDescent('expression',expression)

    d.addDescent('addsubexpr',addsubexpr)
    d.addDescent('muldivexpr',muldivexpr)

    d.addDescent('valueexpr',valueexpr)
    d.addDescent('identexpr',identexpr)
    d.addDescent('constexpr',constexpr)
    d.addDescent('intconst',intconst)

    toks = d.tokenize('ebx = eax + 20')
    off,ast = d.parse('assignment',toks)
    print('parsed: %d %s' % (off,ast))
    #print(d.parse('ebx = eax + 20','assignment'))
