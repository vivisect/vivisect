# So there's a lot we can do with type definitions in this
# but let's save that until we also have a PDB parser, since there
# might be some tricky bits in unifying the two there.

class DebugParam:
    def __init__(self, info):
        self.name = info.get('name')
        self.file = info.get('file')
        self.location = info.get('location')


class DebugFunction:
    def __init__(self, info):
        self.name = info.get('name')
        self.file = info.get('file')
        # TODO: do we bundle template parameters into here as well?
        self.params = info.get('params')
        for param in info.get('params', ()):
            self.params.append(DebugParam(param))
        self.accessibility = info.get('accessibility')

        # self.functype = info.get('type')
        self.line = info.get('line')

        self.startaddr = info.get('start')
        self.endaddr = info.get('end')


class DebugImport:
    def __init__(self, info):
        pass


class DebugString:
    def __init__(self, info):
        self.valu = info.get('value')
        self.offset = info.get('offset')


class DebugInfo:
    def __init__(self):
        # there's a lot of accessor methods/indexing we should do here.
        self.strings = []
        self.imports = []
        self.functions = []

    def addFunction(self, info):
        self.functions.append(DebugFunction(info))

    def addString(self, info):
        self.strings.append(DebugString(info))

    def addImport(self, info):
        self.imports.append(DebugImport(info))
