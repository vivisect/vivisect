'''
Base classes for vertex graph storge abstraction.
'''
import time
import threading
import collections

import synapse.event.dist as s_evtdist

def now(): return int(time.time())
def ldict(): return collections.defaultdict(list)

class NoSuchIndex(Exception):pass
class IndexProtests(Exception):pass
class IndexNotSupported(Exception):pass
class GraphStoreImplementMe(Exception):pass

class GraphIndex:

    indextype = 'keyval'

    def __init__(self, store, prop, info):
        self.info = info
        self.prop = prop
        self.store = store

    def get(self, prop, valu, limit):
        raise GraphStoreImplementMe()

    def pop(self, noge, prop, valu, state):
        raise GraphStoreImplementMe()

    def put(self, noge, prop, valu, state):
        raise GraphStoreImplementMe()

    def test(self, noge, prop, valu, state):
        raise GraphStoreImplementMe()

class GraphStore(s_evtdist.EventDist):

    def __init__(self):
        s_evtdist.EventDist.__init__(self)
        self.lock = threading.Lock()    # held by "transactional" APIs
        self._syn_asplode = True    # it's *not* ok for our callbacks to fail *ever*
        self.indextypes = {}        # typename = builder
        self.node_indexes = {}      # (prop,name) = indexobj
        self.edge_indexes = {}      # (prop,name) = indexobj
        self.node_propidx = ldict() # prop = [ index, ... ]
        self.edge_propidx = ldict() # prop = [ index, ... ]
        self.node_indexfree = {}    # node properties that we dont index
        self.edge_indexfree = {}    # edge properties that we dont index

    def fireStoreEvent(self, evt, **evtinfo):
        evtinfo['time'] = now()
        self.fire(evt,**evtinfo)

    def getNodeById(self, nid): raise GraphStoreImplementMe()
    def getEdgeById(self, eid): raise GraphStoreImplementMe()

    def implAddNode(self, node): raise GraphStoreImplementMe()
    def implDelNode(self, node, state): raise GraphStoreImplementMe()

    def implNodeState(self, node): raise GraphStoreImplementMe()
    def implEdgeState(self, edge): raise GraphStoreImplementMe()

    def implAddEdge(self, edge): raise GraphStoreImplementMe()
    def implDelEdge(self, edge, state): raise GraphStoreImplementMe()

    def implSetNodeProp(self, node, prop, valu, state): raise GraphStoreImplementMe()
    def implSetEdgeProp(self, edge, prop, valu, state): raise GraphStoreImplementMe()

    def implDelNodeProp(self, node, prop, valu, state): raise GraphStoreImplementMe()
    def implDelEdgeProp(self, edge, prop, valu, state): raise GraphStoreImplementMe()

    def addNode(self, node):
        '''
        Add a node to the graph storage
        '''
        with self.lock:
            state = self.implAddNode(node)
            # FIXME make this "unwind" if an index refuses
            for prop,valu in node[1].items():
                indexes = self.node_propidx.get(prop)
                if indexes != None:
                    [ i.test(node,prop,valu,state) for i in indexes ]
                    [ i.put(node,prop,valu,state) for i in indexes ]

        self.fireStoreEvent('store:node:add',node=node)
        return node

    def addEdge(self, edge):
        '''
        Add an edge to the graph storage
        '''
        with self.lock:
            state = self.implAddEdge(edge)
            for prop,valu in edge[1].items():
                indexes = self.edge_propidx.get(prop)
                if indexes != None:
                    [ i.test(edge,prop,valu,state) for i in indexes ]
                    [ i.put(edge,prop,valu,state) for i in indexes ]

        self.fireStoreEvent('store:edge:add',edge=edge)
        return edge

    def delNode(self, node):
        '''
        Delete a node from the graph storage.
        '''
        with self.lock:
            state = self.implNodeState(node)
            # pop from all indexes
            for prop,valu in node[1].items():
                indexes = self.node_propidx.get(prop)
                if indexes == None:
                    continue
                [ i.pop(node,prop,valu,state) for i in indexes ]
            self.implDelNode(node,state)
        self.fireStoreEvent('store:node:del',node=node)

    def delEdge(self, edge):
        '''
        Delete an edge from the graph storage.
        '''
        with self.lock:
            state = self.implEdgeState(edge)
            for prop,valu in edge[1].items():
                indexes = self.edge_propidx.get(prop)
                if indexes == None:
                    continue
                [ i.pop(edge,prop,valu,state) for i in indexes ]
            self.implDelEdge(edge,state)
        self.fireStoreEvent('store:edge:del',edge=edge)

    def delNodeProp(self, node, prop):
        '''
        Delete a node property from the graph storage.
        '''
        valu = node[1].get(prop)
        with self.lock:
            state = self.implNodeState(node)
            indexes = self.node_propidx.get(prop)
            if indexes != None:
                [ i.pop(node,prop,valu,state) for i in indexes ]
            self.implDelNodeProp(node,prop,valu,state)
        node[1].pop(prop,None)
        self.fireStoreEvent('store:node:prop:del',node=node,prop=prop,valu=valu)
        return node

    def delEdgeProp(self, edge, prop):
        '''
        Delete an edge property from the graph storage.
        '''
        valu = edge[1].get(prop)
        with self.lock:
            state = self.implEdgeState(edge)
            indexes = self.edge_propidx.get(prop)
            if indexes != None:
                [ i.pop(edge,prop,valu,state) for i in indexes ]
            self.implDelEdgeProp(edge,prop,valu,state)
        edge[1].pop(prop,None)
        self.fireStoreEvent('store:edge:prop:del',edge=edge,prop=prop,valu=valu)
        return edge

    def setNodeProp(self, node, prop, valu):
        oldval = node[1].get(prop)
        with self.lock:
            state = self.implNodeState(node)
            indexes = self.node_propidx.get(prop)
            if indexes != None:
                [ i.test(node,prop,valu,state) for i in indexes ]
                if oldval != None:
                    [ i.pop(node,prop,oldval,state) for i in indexes ]
                [ i.put(node,prop,valu,state) for i in indexes ]
            self.implSetNodeProp(node,prop,valu,state)
        node[1][prop] = valu
        self.fireStoreEvent('store:node:prop:set',node=node,prop=prop,valu=valu,oldval=oldval)
        return node

    def setEdgeProp(self, edge, prop, valu):
        oldval = edge[1].get(prop)
        with self.lock:
            state = self.implEdgeState(edge)
            indexes = self.edge_propidx.get(prop)
            if indexes != None:
                [ i.test(edge,prop,valu,state) for i in indexes ]
                if oldval != None:
                    [ i.pop(edge,prop,oldval,state) for i in indexes ]
                [ i.put(edge,prop,valu,state) for i in indexes ]
            self.implSetEdgeProp(edge,prop,valu,state)
        edge[1][prop] = valu
        self.fireStoreEvent('store:edge:prop:set',edge=edge,prop=prop,valu=valu,oldval=oldval)
        return edge

    def getNodesByProp(self, prop, valu=None, limit=None, index='keyval'):
        idxkey = (prop,index)
        idx = self.node_indexes.get(idxkey)
        if idx == None:
            raise NoSuchIndex(prop,index)
        return idx.get(prop,valu,limit)

    def getEdgesByProp(self, prop, valu=None, limit=None, index='keyval'):
        idxkey = (prop,index)
        idx = self.edge_indexes.get(idxkey)
        if idx == None:
            raise NoSuchIndex(prop,index)
        return idx.get(prop,valu,limit)

    def initIndexCtor(self, indextype, ctor):
        '''
        Initialize an index constructor by type name.
        '''
        self.indextypes[indextype] = ctor

    def initNodeIndex(self, prop, indextype, **info):
        '''
        Initialize a new storage index for the given prop.

        Storage layers may implement various index types which
        may be in use by particular models.  The expected "base"
        index types are:

        keyval      - exact key=valu matching ( each prop gets one by default )
        keylist     - a "keyval" style match for *each* value in a list
        intrange    - integer range indexing

        Example:
            g.initNodeIndex(prop,'intrange')

        NOTE: storage implementations must load pre-existing
              indexes with addNodeIndex during startup to allow
              this API to "smile and nod" if it's called with an
              existing index.
        '''
        idxkey = (prop,indextype)
        index = self.node_indexes.get(idxkey)
        if index != None:
            return

        ctor = self.indextypes.get(indextype)
        if ctor == None:
            raise IndexNotSupported(indextype)

        # FIXME index existing data!

        index = ctor(self,prop,info)
        self.node_indexes[idxkey] = index
        self.node_propidx[prop].append( index )

    def initEdgeIndex(self, prop, indextype='keyval', **info):
        idxkey = (prop,indextype)
        index = self.edge_indexes.get(idxkey)
        if index != None:
            return

        ctor = self.indextypes.get(indextype)
        if ctor == None:
            raise IndexNotSupported(indextype)

        index = ctor(self,prop,info)
        self.edge_indexes[idxkey] = index
        self.edge_propidx[prop].append( index )

    def addNodeIndex(self, prop, name, index):
        '''
        Used by storage implementations to register an index.
        '''
        self.node_propidx[prop].append(index)
        self.node_indexes[(prop,name)] = index

    def addEdgeIndex(self, prop, name, index):
        self.edge_propidx[prop].append(index)
        self.edge_indexes[(prop,name)] = index

    def getNodeIndex(self, prop, name):
        '''
        Retrieve an index object for a node property.
        '''
        return self.node_indexes.get((prop,name))

    def getEdgeIndex(self, prop, name):
        return self.edge_indexes.get((prop,name))

