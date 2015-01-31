'''
Implements the vertex graph class.
'''
import synapse.lib.common as s_common
import synapse.event.dist as s_evtdist

import vertex.store.ram as v_storeram

class Graph(s_evtdist.EventDist):

    def __init__(self, store=None):
        s_evtdist.EventDist.__init__(self)

        self._node_stors = {}
        self._edge_stors = {}

        if store == None:
            store = v_storeram.GraphStore()

        self.store = store
        self.store.initEdgeIndex('edge:n1')
        self.store.initEdgeIndex('edge:n2')

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
        node = self.store.addNode((nid,props))
        self.synFireEvent('graph:node:add',{'node':node})
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
        self.synFireEventKw('graph:node:prop:del',node=node,prop=prop,valu=valu)
        return node

    def delNode(self, node):
        '''
        Delete a node from the graph
        '''
        for edge in self.getEdgesByProp('edge:n1',valu=node[0]):
            self.delEdge(edge)
        for edge in self.getEdgesByProp('edge:n2',valu=node[0]):
            self.delEdge(edge)
        self.store.delNode(node)
        self.synFireEventKw('graph:node:del',node=node)

    def addEdge(self, node1, node2, **props):
        '''
        Add an edge to the graph with the given src->dst and properties.
        '''
        eid = self.initEdgeId(props)
        props['edge:n1'] = node1[0]
        props['edge:n2'] = node2[0]
        edge = self.store.addEdge((eid,props))
        self.synFireEventKw('graph:edge:add',edge=edge)
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

