'''
A "python objects" storage implementation.
'''
import itertools
import collections
import vertex.store.common as v_common

def ldict(): return collections.defaultdict(list)
def ddict(): return collections.defaultdict(dict)

class UniqIndex(v_common.GraphIndex):

    indextype = 'uniq'

    def __init__(self, store, prop, info):
        self.hasprop = {}
        self.propval = {}

    def put(self, noge, prop, valu, state):
        self.propval[valu] = noge
        self.hasprop[noge[0]] = noge

    def get(self, prop, valu, limit):
        if valu == None:
            return list(itertools.islice(self.hasprop.values(),limit))

        x = self.propval.get(valu)
        if x == None:
            return []
        return [x]

    def pop(self, noge, prop, valu, state):
        self.hasprop.pop(noge[0], None)
        x = self.propval.pop(valu,None)
        if x == None:
            return

        if x[0] != noge[0]:
            self.propval[valu] = x
            raise v_common.IndexProtests('%s: pop on wrong noge: %s' % (noge[0],x[0]))

    def test(self, noge, prop, valu, state):
        x = self.propval.get(valu)
        if x != None:
            raise v_common.IndexProtests('%s: %s=%s (uniq violation)' % (noge[0],prop,valu))

class KeyValIndex(v_common.GraphIndex):

    def __init__(self, store, prop, info):
        v_common.GraphIndex(store,prop,info)
        self.hasprop = {}
        self.propval = ddict()

    def put(self, noge, prop, valu, state):
        oid = noge[0]
        self.hasprop[oid] = noge
        self.propval[valu][oid] = noge

    def pop(self, noge, prop, valu, state):
        oid = noge[0]
        self.hasprop.pop(oid,None)
        vals = self.propval.get(valu)
        if vals == None:
            return

        vals.pop(oid,None)
        if not vals:
            self.propval.pop(valu)

    def get(self, prop, valu, limit):
        if valu == None:
            return list(itertools.islice(self.hasprop.values(),limit))

        valdict = self.propval.get(valu)
        if valdict == None:
            return []

        return list(itertools.islice(valdict.values(),limit))

    def test(self, noge, prop, valu, state):
        try:
            hash(valu)
        except TypeError as e:
            raise IndexProtests('%s: setting %s (%s is not hashable)' % (noge[0], prop, type(valu)))

class GraphStore(v_common.GraphStore):

    def __init__(self):
        v_common.GraphStore.__init__(self)
        self.nodesbyid = {}
        self.edgesbyid = {}
        self.initIndexCtor('uniq', UniqIndex)
        self.initIndexCtor('keyval', KeyValIndex)

    def getNodeById(self, nid):
        return self.nodesbyid.get(nid)

    def getEdgeById(self, eid):
        return self.edgesbyid.get(eid)

    def implNodeState(self, node):
        return None

    def implEdgeState(self, edge):
        return None

    def implSetNodeProp(self, node, prop, valu, state):
        nid = node[0]
        self.nodesbyid[nid][1][prop] = valu

    def implDelNodeProp(self, node, prop, valu, state):
        nid = node[0]
        self.nodesbyid[nid][1].pop(prop,None)

    def implSetEdgeProp(self, edge, prop, valu, state):
        eid = edge[0]
        self.edgesbyid[eid][1][prop] = valu

    def implDelEdgeProp(self, edge, prop, valu, state):
        eid = edge[0]
        self.edgesbyid[eid][1].pop(prop,None)

    def implAddNode(self, node):
        nid = node[0]
        self.nodesbyid[nid] = node

    def implDelNode(self, node, state):
        nid = node[0]
        self.nodesbyid.pop(nid,None)

    def implAddEdge(self, edge):
        eid = edge[0]
        self.edgesbyid[eid] = edge

    def implDelEdge(self, edge, state):
        eid = edge[0]
        self.edgesbyid.pop(eid,None)
