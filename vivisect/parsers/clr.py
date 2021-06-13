import logging
from pprint import pprint

from vstruct.defs.clr import Types

logger = logging.getLogger(__name__)

# TODO: There's a tooooon more to implement and add here
def _checkAssembly(pe):
    pass

def _checkAssemblyRef(pe):
    pass

def _checkModule(pe):
    pass

def _checkModuleRef(pe):
    pass

def _checkFile(pe):
    pass

def _checkManifestResource(pe):
    pass

def _checkExportedType(pe):
    pass


validityCheckers = [
    _checkAssembly,
    _checkAssemblyRef,
    _checkModule,
    _checkModuleRef,
    _checkFile,
    _checkManifestResource,
    _checkExportedType,
]


def getCLRString(pe, offset):
    return pe.CLRStrings.get(offset, None)


def parseTypeDefs(vw, pe):
    methods = []
    midxs = sorted([t.MethodList for t in pe.CLRTables[Types.TypeDef][1:]])
    for idx, typedef in enumerate(pe.CLRTables[Types.TypeDef][1:]):
        cname = getCLRString(pe, typedef.Name)
        namespace = getCLRString(pe, typedef.Namespace)
        mstart = typedef.MethodList
        mend = midxs.index(mstart)
        if mend + 1 >= len(midxs):
            mend = mend + 1
        else:
            mend = midxs[mend + 1]
        #print(f'{cname}:\tFlags: {hex(typedef.Flags)}, Start: {hex(mstart)}, End: {hex(mend)}, Field: {hex(typedef.FieldList)}')
        for i in range(mstart, mend, 1):
            meth = pe.CLRTables[Types.Method][i]
            mname = getCLRString(pe, meth.Name)
            mname = f'{namespace}.{cname}.{mname}'
            # param list
            methods.append((meth.RVA, mname, meth))
    return methods


def loadCLRIntoWorkspace(vw, pe):
    '''
    So....CLR is weird in that it's both a full-fledged architecture on it's own, but also
    can bring along with it unmanaged (native) code and can switch to those when it needs to
    (kinda like how ARM/Thumb can switch). So that's something we need to keep in mind when
    parsing things out
    '''
    pe.parseCLR()
    for func in validityCheckers:
        func(pe)
    try:
        methods = parseTypeDefs(vw, pe)
    except:
        import pdb, sys
        pdb.post_mortem(sys.exc_info()[2])

    breakpoint()
    return
    # So at this point we effectively have a parsed DB of various metadata, and we need to apportion
    # that out
