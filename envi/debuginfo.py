# So there's a lot we can do with type definitions in this
# but let's save that until we also have a PDB parser, since there
# might be some tricky bits in unifying the two there.

class DebugBase:
    def __init__(self, name, file):
        self.name = name
        self.file = file


class DebugParam(DebugBase):
    def __init__(self, **info):
        super().__init__(info.get('name'), info.get('file'))
        self.line = info.get('line')
        self.type = info.get('type')


class DebugFunction(DebugBase):
    # TODO: I should cut these down...
    def __init__(self, **info):
        super().__init__(info.get('name'), info.get('file'))
        self.dirn = info.get('dirn')
        self.line = info.get('line')

        # TODO: do we bundle template parameters into here as well?
        self.params = []
        for param in info.get('params', ()):
            self.params.append(DebugParam(**param))
        # self.accessibility = accessibility
        self.start = info.get('start')
        self.end = info.get('end')


class DebugImport(DebugBase):
    def __init__(self, **info):
        pass


class DebugString(DebugBase):
    def __init__(self, **info):
        super().__init__(info.get('name'), info.get('file'))
        self.valu = info.get('valu')
        self.offset = info.get('offset')


class DebugStructMember(DebugBase):
    def __init__(self, **info):
        # TODO: Functionalize this preamble too
        name = info.get('name')
        file = info.get('file')
        super().__init__(name, file)
        self.dirn = info.get('dirn')
        self.line = info.get('line')
        self.offset = info.get('offset')


class DebugStructure(DebugBase):
    def __init__(self, **info):
        name = info.get('name')
        file = info.get('file')
        super().__init__(name, file)
        self.dirn = info.get('dirn')
        self.line = info.get('line')
        self.size = info.get('size')

        self.members = []
        for member in info.get('members', ()):
            self.members.append(DebugStructMember(**member))

class DebugLocal(DebugBase):
    def __init__(self, **info):
        super().__init__(info.get('name'), info.get('file'))
        self.line = info.get('line')
        self.type = info.get('type')


class DebugNamespace(DebugBase):
    def __init__(self, **info):
        super().__init__(info.get('name'), info.get('file'))
        self.line = info.get('line')
        self.parent = info.get('parent')


class DebugInfo:
    '''
    Our general holder for any debug information we parse out. Right now just a
    holder of DWARF info, but one day that will change.

    Right now a POD until we hammer out how we want to surface this information
    in the UI and the cmd line
    '''
    def __init__(self):
        # there's a lot of accessor methods/indexing we should do here.
        # like should we index by name/va combo or something?
        self.strings = []
        self.imports = []
        self.functions = []
        self.structs = []
        self.kids = []

    def addChild(self, type, info):
        self.kids.append((type, info))
        if type == 'function':
            self.functions.append(DebugFunction(**info))
        elif type == 'struct':
            self.structs.append(DebugStructure(**info))
