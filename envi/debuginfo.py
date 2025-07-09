# So there's a lot we can do with type definitions in this
# but let's save that until we also have a PDB parser, since there
# might be some tricky bits in unifying the two there.

class DebugBase:
    def __init__(self, name, file):
        self.name = name
        self.file = file


class DebugParam(DebugBase):
    def __init__(self, name, file, line, type):
        super().__init__(name, file)
        self.line = line


class DebugFunction(DebugBase):
    def __init__(self, name, file, line, params, start, end, accessibility):
        super().__init__(name, file)
        self.line = line

        # TODO: do we bundle template parameters into here as well?
        # self.params = params
        for param in params:
            self.params.append(DebugParam(param))
        self.accessibility = accessibility
        self.start = start
        self.end = end


class DebugImport(DebugBase):
    def __init__(self, info):
        pass


class DebugString(DebugBase):
    def __init__(self, name, file, valu, offset):
        super().__init__(name, file)
        self.valu = valu
        self.offset = offset


class DebugStructMember(DebugBase):
    pass


class DebugStructure(DebugBase):
    def __init__(self, name, file, line):
        super().__init__(name, file)
        self.line = line


class DebugLocal(DebugBase):
    def __init__(self, name, file, line, type):
        super().__init__(name, file)
        self.line = line
        self.type = type


class DebugNamespace(DebugBase):
    def __init__(self, name, file, line, parent):
        super().__init__(name, file)
        self.line = line
        self.parent = parent


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

    def addChild(self):
        pass
