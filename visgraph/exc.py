
class VisGraphException(Exception):
    pass

class DuplicateNode(VisGraphException):
    def __init__(self, node):
        Exception.__init__(self, repr(node))
        self.node = node

class NodeNonExistant(VisGraphException):
    def __init__(self, nodeid):
        self.nodeid = nodeid
        Exception.__init__(self, 'Node %d does not exist!' % nodeid)

class EdgeNonExistant(VisGraphException):
    def __init__(self, edgeid):
        self.edgeid = edgeid
        Exception.__init__(self, 'Edge %d does not exist!' % edgeid)
