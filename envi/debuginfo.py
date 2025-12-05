'''
Some debugging formats (like DWARF) are super permissive about what they populate
about the debugging structures they have, and the debugging subsystem is still
very much in "first stab at things".

So most of the classes here are going to accept a **info kwargs argument that
we pull fields out of. That way, if we decide to change formats/fields/etc, we don't
invalidate old workspaces (we can still pull those fields out without doing any kind
of migration), and we can support whatever PDB (or another format) is going to look like.
'''

class DebugBase:
    def __init__(self, name, file):
        self.name = name
        self.file = file


class DebugParam(DebugBase):
    def __init__(self, **info):
        super().__init__(info.get('name'), info.get('file'))
        self.line = info.get('line')
        self.type = info.get('type')
        self.optional = info.get('optional')


class DebugFunction(DebugBase):
    def __init__(self, **info):
        super().__init__(info.get('name'), info.get('file'))
        self.dirn = info.get('dirn')
        self.line = info.get('line')
        self.cc = info.get('calling_convention')

        self.params = []
        for param in info.get('parameters', ()):
            self.params.append(DebugParam(**param))
        # self.accessibility = accessibility
        self.start = info.get('start')
        self.end = info.get('end')

        self.call_line = info.get('call_line')
        self.call_file = info.get('call_file')
        self.call_column = info.get('call_column')

class DebugImport(DebugBase):
    def __init__(self, **info):
        imp = info.get('import')
        name = info.get('name')
        if name is None:
            name = imp.get('name')
        # file and line in this case mean the line and file where the import occurred
        super().__init__(name, info.get('file'))
        self.line = info.get('line')
        self.imp = imp

class DebugString(DebugBase):
    def __init__(self, **info):
        super().__init__(info.get('name'), info.get('file'))
        self.valu = info.get('valu')
        self.offset = info.get('offset')


class DebugStructMember(DebugBase):
    def __init__(self, **info):
        super().__init__(info.get('name'), info.get('file'))
        self.dirn = info.get('dirn')
        self.line = info.get('line')
        self.offset = info.get('offset')


class DebugStructure(DebugBase):
    def __init__(self, **info):
        super().__init__(info.get('name'), info.get('file'))
        self.union = info.get('union')
        self.dirn = info.get('dirn')
        self.line = info.get('line')
        self.size = info.get('size')
        # for the constructor it looks like
        self.cc = info.get('calling_convention')

        self.members = []
        for member in info.get('members', ()):
            self.members.append(DebugStructMember(**member))

        self.functions = []
        for func in info.get('functions', ()):
            self.functions.append(DebugFunction(**func))

        self.parameters = []
        for param in info.get('parameters', ()):
            self.members.append(DebugParam(**param))

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

    def addChild(self, type, info):
        if type == 'function':
            self.functions.append(DebugFunction(**info))
        elif type == 'struct' or type == 'class':
            self.structs.append(DebugStructure(**info))
        elif type == 'import':
            self.imports.append(DebugImport(**info))
