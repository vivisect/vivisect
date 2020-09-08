from pycparser import c_parser
import pycparser.c_ast as c_ast

import vstruct
import vstruct.primitives as vs_prim

class StructParser:

    def __init__(self, psize=4, bigend=False):

        self.psize = psize
        self.pclass = vs_prim.v_ptr32

        self.cls_parsers = {
            c_ast.Decl:             self.c_getVsDecl,
            c_ast.Struct:           self.c_getVsStruct,
            c_ast.FileAST:          self.c_getFileAst,
            c_ast.PtrDecl:          self.c_getPointer,
            #c_ast.FuncDecl:         self.c_getFuncDecl,
            c_ast.Constant:         self.c_getConstant,
            c_ast.TypeDecl:         self.c_getVsType,
            c_ast.ArrayDecl:        self.c_getVsArray,
            c_ast.IdentifierType:   self.c_getIdentType,
        }

        self.vs_ctypes = {
            ('char',):                  vs_prim.v_int8,
            ('unsigned','char'):        vs_prim.v_uint8,

            ('short',):                 vs_prim.v_int16,
            ('short','int'):            vs_prim.v_int16,

            ('unsigned', 'short',):     vs_prim.v_uint16,
            ('unsigned', 'short','int'):vs_prim.v_uint16,

            ('int',):                   vs_prim.v_int32,
            ('unsigned','int',):        vs_prim.v_uint32,

            ('long',):                  vs_prim.v_int32,
            ('long','int'):             vs_prim.v_int32,

            ('unsigned','long',):       vs_prim.v_uint32,
            ('unsigned','long','int'):  vs_prim.v_uint32,
        }

        if psize == 8:
            self.pclass = vs_prim.v_ptr64
            self.vs_ctypes.update({
                ('long',):                    vs_prim.v_int64,
                ('long', 'int'):              vs_prim.v_int64,
                ('long', 'long'):             vs_prim.v_int64,

                ('unsigned', 'long',):        vs_prim.v_uint64,
                ('unsigned', 'long', 'int'):  vs_prim.v_uint64,
                ('unsigned', 'long', 'long'): vs_prim.v_uint64,
            })

    def _getVsChildElements(self, astelem):
        return [ self._getVsElement( c ) for c in astelem[1].children() ]

    def _getVsElement(self, astelem):
        # An ast element comes as a tuple of namething, realstuff
        namething,elem = astelem
        p = self.cls_parsers.get( elem.__class__ )
        if p is None:
            raise Exception('OMG NO PARSER FOR: %r' % elem)
        return p( astelem )

    def c_getPointer(self, pdecl):
        vsclass = self._getVsChildElements( pdecl )[ 0 ]
        return self.pclass

    def c_getVsArray(self, ardecl):
        cls, size = self._getVsChildElements(ardecl)
        # Special case char arrays into v_bytes
        if cls == vs_prim.v_int8:
            return lambda: vs_prim.v_str(size=size)

        return lambda: vstruct.VArray( [ cls() for i in range(size) ] )

    def c_getIdentType(self, itelem):
        ename, einst = itelem
        c = self.vs_ctypes.get(tuple(einst.names))
        if not c:
            raise Exception('Un-plumbed type: %r' % (einst.names,))
        return c

    def c_getVsType(self, idelem):
        ename, einst = idelem
        cls = self._getVsChildElements(idelem)[0]
        return cls

    def c_getVsDecl(self, decelem):
        decname = decelem[1].name
        return decname,self._getVsChildElements(decelem)[0]

    def c_getVsStruct(self, selem):
        sname,sinst = selem
        def bstruct():
            vs = vstruct.VStruct()
            vs._vs_name = sinst.name
            for cname,chclass in self._getVsChildElements( selem ):
                vobj = chclass()
                vs.vsAddField(cname, vobj)
            return vs
        return bstruct

    def c_getFileAst(self, elem):
        return self._getVsChildElements(elem)

    def c_getConstant(self, celem):
        return int(celem[1].value)

    def c_getFuncDecl(self, felem):
        raise NotImplementedError("Implement function declaration parsing!")

    def parseStructSource(self, src):
        src = preProcessSource( src )
        parser = c_parser.CParser()
        ast = parser.parse(src)
        #ast.show()

        for child in ast.children():
            xname, decl =  self._getVsElement( child )
            yield decl

def preProcessSource( src ):
    '''
    Carry out some *very* basic pre-processor parsing on the given source.

    (only function now is remove "//" style comments!)
    '''
    lines = src.splitlines()
    return '\n'.join( [ line.split('//')[0] for line in lines ] )

def ctorFromCSource(src, psize=4, bigend=False):
    '''
    Parse and return a callable constructor for the
    input C structure source.
    '''
    p = StructParser(psize=psize, bigend=bigend)
    return list(p.parseStructSource( src ))[0]

def vsFromCSource(src, psize=4, bigend=False):
    '''
    Return a vsobj for a structure parsed from C.
    '''
    return ctorFromCSource(src, psize, bigend)()

class CVStruct(object):
    '''
    struct example {
        int x;
        char y[30];
        int *z;
    };
    '''
    psize = 4
    bigend = False

    def __new__(self):
        return vsFromCSource(self.__doc__, self.psize, self.bigend)

class awesome(CVStruct):
    '''
    struct awesome {
        int x,z;
        char stuff[20];
        int y;
        struct haha {
            int blah;
        } s;
        int *q;
    };
    '''
