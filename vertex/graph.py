'''
Implements the vertex graph class.
'''
import synapse.lib.common as s_common
import synapse.event.dist as s_evtdist

import vertex.store.ram as v_storeram

class Graph(s_evtdist.EventDist):

    def __init__(self, store=None, **info):
        s_evtdist.EventDist.__init__(self)

        self._graf_info = info

        self._node_stors = {}
        self._edge_stors = {}

        if store == None:
            store = v_storeram.GraphStore()

        self.store = store
        self.store.initEdgeIndex('_:n1')
        self.store.initEdgeIndex('_:n2')

    def getGraphInfo(self, prop):
        return self._graf_info.get(prop)

    def setGraphInfo(self, prop, valu):
        self._graf_info[prop] = valu

    def delGraphInfo(self, prop):
        return self._graf_info.pop(prop,None)

    def initNodeIndex(self, prop, idxtype, **info):
        '''
        Initialize a node index in the underlying storage layer.

        NOTE: if the index already exists, the call is ignored
        '''
        return self.store.initNodeIndex(prop, idxtype, **info)

    def initEdgeIndex(self, prop, idxtype, **info):
        '''
        Initialize an edge index in the underlying storage layer.

        NOTE: if the index already exists, the call is ignored
        '''
        return self.store.initEdgeIndex(prop, idxtype, **info)

    def initNodeId(self, props):
        return s_common.guid()

    def initEdgeId(self, props):
        return s_common.guid()

    def getNodeById(self, nid):
        '''
        Retrieve a node by it's globally unique id
        '''
        return self.store.getNodeById(nid)

    def getEdgeById(self, eid):
        '''
        Retrieve an edge by it's globally unique id
        '''
        return self.store.getEdgeById(eid)

    def addNode(self, **props):
        '''
        Add a node to the graph with the given properties.
        '''
        nid = self.initNodeId(props)
        return self._addNode( (nid,props) )

    def _addNode(self, node):
        # FIXME what to call this?
        node = self.store.addNode(node)
        self.synFireEvent('graph:node:add',{'node':node})
        return node

    def setNodeProps(self, node, **props):
        for key,val in props.items():
            node = self.setNodeProp(node,key,val)
        return node

    def setNodeProp(self, node, prop, valu):
        '''
        Set a property on a node in the graph
        '''
        prev = node[1].get(prop)
        node = self.store.setNodeProp(node,prop,valu)
        self.synFireEventKw('graph:node:prop:set',node=node,prop=prop,valu=valu,prev=prev)
        return node

    def delNodeProp(self, node, prop):
        '''
        Delete a property from a node in the graph
        '''
        valu = node[1].get(prop)
        node = self.store.delNodeProp(node,prop)
        node[1].pop(prop,None)
        self.synFireEventKw('graph:node:prop:del',node=node,prop=prop,valu=valu)
        return node

    def delNode(self, node):
        '''
        Delete a node from the graph
        '''
        for edge in self.getEdgesByProp('_:n1',valu=node[0]):
            self.delEdge(edge)
        for edge in self.getEdgesByProp('_:n2',valu=node[0]):
            self.delEdge(edge)
        self.store.delNode(node)
        self.synFireEventKw('graph:node:del',node=node)

    def addEdge(self, node1, node2, **props):
        '''
        Add an edge to the graph with the given src->dst and properties.
        '''
        eid = self.initEdgeId(props)
        props['_:n1'] = node1[0]
        props['_:n2'] = node2[0]
        edge = (eid,props)
        return self._addEdge(edge)

    def _addEdge(self, edge):
        edge = self.store.addEdge(edge)
        self.synFireEventKw('graph:edge:add',edge=edge)
        return edge

    def setEdgeProps(self, edge, **props):
        for key,val in props.items():
            edge = self.setEdgeProp(edge,key,val)
        return edge

    def setEdgeProp(self, edge, prop, valu):
        '''
        Set a property on an edge in the graph
        '''
        prev = edge[1].get(prop)
        edge = self.store.setEdgeProp(edge,prop,valu)
        self.synFireEventKw('graph:edge:prop:set',edge=edge,prop=prop,valu=valu,prev=prev)
        return edge

    def delEdgeProp(self, edge, prop):
        '''
        Delete a property from the given edge
        '''
        prev = edge[1].get('prop')
        edge = self.store.delEdgeProp(edge,prop)
        edge[1].pop(prop,None)
        self.synFireEventKw('graph:edge:prop:del',edge=edge,prop=prop,prev=prev)
        return edge

    def delEdge(self, edge):
        '''
        Delete an edge from the graph
        '''
        self.store.delEdge(edge)
        self.synFireEventKw('graph:edge:del',edge=edge)

    def getNodeByProp(self, prop, valu=None):
        '''
        Retrieve a single node with the given prop[=valu]
        '''
        nodes = self.getNodesByProp(prop,valu=valu,limit=1)
        if nodes:
            return nodes[0]

    def getNodesByProp(self, prop, valu=None, limit=None, index='keyval'):
        '''
        Retrieve a list of graph nodes by prop[=valu].

        Options:
        limit       - the max number of nodes to return
        index       - which index to ask to resolve the key/val
        '''
        return self.store.getNodesByProp(prop,valu=valu,limit=limit,index=index)

    def getN2NodesByN1(self, node, limit=None):
        for edge in self.getEdgesByProp('_:n1',valu=node[0],limit=limit):
            yield self.getNodeById( edge[1].get('_:n2') )

    def getN1NodesByN2(self, node, limit=None):
        for edge in self.getEdgesByProp('_:n2',valu=node[0],limit=limit):
            yield self.getNodeById( edge[1].get('_:n1') )

    def getEdgeByProp(self, prop, valu=None):
        '''
        Retrieve a single edge with the given prop[=valu]
        '''
        edges = self.getEdgesByProp(prop,valu=valu,limit=1)
        if edges:
            return edges[0]

    def getEdgesByProp(self, prop, valu=None, limit=None, index='keyval'):
        '''
        Retrieve a list of graph edges by prop[=valu].

        Options:
        limit       - the max number of edges to return
        index       - which index to ask to resolve the key/val

        Example:
            for edge in g.getEdgesByProp('woot',10):
                dostuff(edge)
        '''
        return self.store.getEdgesByProp(prop,valu=valu,limit=limit,index=index)

