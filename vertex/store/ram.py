'''
A "python objects" storage implementation.
'''
import itertools
import collections
import vertex.store.common as v_common

def ldict(): return collections.defaultdict(list)
def ddict(): return collections.defaultdict(dict)

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

class GraphStore(v_common.GraphStore):

    def __init__(self):
        v_common.GraphStore.__init__(self)
        self.nodesbyid = {}
        self.edgesbyid = {}
        self.initIndexCtor('keyval',self._ctor_index_keyval)

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

    def _ctor_index_keyval(self, store, prop, info):
        return KeyValIndex(store,prop,info)
