'''
Graphcore contains all the base graph manipulation objects.
'''
import os
import json
import threading
import collections

from binascii import hexlify

from visgraph.exc import *
import visgraph.pathcore as vg_pathcore


def guid(size=16):
    return hexlify(os.urandom(size)).decode('utf-8')


def zdict():
    return collections.defaultdict(int)


def ldict():
    return collections.defaultdict(list)


def pdict():
    return collections.defaultdict(ldict)


class Graph:

    '''
    The base Graph object implements a simple nodes and edges graph.

    Nodes -
        Nodes consist of a dicionary of properties about that node and
        a unique id which identifies the node in the current graph.  From
        API perspective a node is a tuple of (nid, nodeprops).

    Edges -
        Edges are directional sets of a from node-id and to node-id and
        a piece of arbitrary edge information.
    '''
    def __init__(self):
        self.wipeGraph()
        self.formlock = threading.Lock()

    def setMeta(self, mprop, mval):
        self.metadata[mprop] = mval

    def getMeta(self, mprop, default=None):
        '''
        Retrieve a value from the dictionary of metadata about this graph.

        Example:
            m = g.getMeta('made-up-property')
        '''
        return self.metadata.get(mprop, default)

    def toJson(self):
        '''
        convert the graph to a json serializable
        data set.
        '''
        graph = {'nodes': {}, 'edges':[]}
        graph['nodes'] = {node[0]: node[1] for node in self.getNodes()}
        graph['edges'] = [edge for edge in self.getEdges()]
        return json.dumps(graph)

    @classmethod
    def fromJsonFd(cls, fd):
        '''
        instiate a graph from a file descriptor
        containing serialized json.
        '''
        g = cls()
        g.fromJson(json.loads(fd.read()))
        return g

    @classmethod
    def fromJsonBuf(cls, buf):
        '''
        instiatiate a graph from a seralized json buffer
        '''
        g = cls()
        g.fromJson(json.loads(buf))
        return g

    def fromJson(self, graph):
        '''
        load a json serializable graph
        '''
        for nid,nprops in graph['nodes'].items():
            self.addNode(nid=nid, nprops=nprops)

        for eid, n1, n2, eprops in graph['edges']:
            node1 = (n1, graph['nodes'][n1])
            node2 = (n2, graph['nodes'][n2])
            self.addEdge(node1, node2, eid=eid, eprops=eprops)

    def merge(self, graph):
        '''
        duplicate another graph's contents.  subclasses may wish to modify this
        function to duplicate more properties if present.
        '''
        self.wipeGraph()

        self.metadata.update(graph.metadata)
        self.formnodes.update(graph.formnodes)

        for nid,nprops in graph.nodes.values():
            self.addNode(nid=nid, nprops=nprops)

        for eid, n1, n2, eprops in graph.edges.values():
            node1 = graph.getNode(n1)
            node2 = graph.getNode(n2)
            self.addEdge(node1, node2, eid=eid, eprops=eprops)
        

    def wipeGraph(self):
        '''
        Re-initialize the graph structures and start clean again.
        '''
        self.edges          = {}
        self.nodes          = {}
        self.metadata       = {}
        self.formnodes      = {}
        self.nodeprops      = pdict() # nodeprops[key][value] = list of nodes
        self.edgeprops      = pdict() # edgeprops[key][value] = list of edges
        self.edge_by_to     = ldict()
        self.edge_by_from   = ldict()

    def getEdges(self):
        '''
        Get the list of edges in the graph.  Edges are defined
        as (eid, n1, n2, eprops) tuples.

        Example: for eid, n1, n2, eprops in g.getEdges():
        '''
        return list(self.edges.values())

    def getEdge(self, eid):
        '''
        Get the (eid, n1, n2, eprops) tuple for the specified
        edge.

        Example: e = g.getEdge(eid)
        '''
        return self.edges.get(eid)

    def getEdgeProps(self, eid):
        '''
        Retrieve the properties dictionary for the given edge id.
        '''
        edge = self.edges.get(eid)
        if not edge:
            raise Exception('Invalid edge id')
        return edge[3]

    def getEdgesByProp(self, prop, val=None):
        '''
        Retrieve all the edges with the specified prop (optionally value).

        Example:
            # my made up "score" property on edges...
            for edge in g.getEdgesByProp("score",300):
                print(edge)
        '''
        if val is not None:
            return self.edgeprops.get(prop,{}).get(val,[])

        ret = []
        [ ret.extend(v) for v in self.edgeprops.get(prop,{}).values() ]
        return ret

    def setEdgeProp(self, edge, prop, value):
        '''
        Set a key/value pair about a given edge.

        Example: g.setEdgeProp(edge, 'awesomeness', 99)
        '''
        curval = edge[3].get(prop)
        if curval == value:
            return False


        edge[3][prop] = value

        try:
            if curval is not None:
                curlist = self.edgeprops[prop][curval]
                curlist.remove( edge )
            self.edgeprops[prop][value].append(edge)
        except TypeError:
            pass

        return True

    def setNodeProp(self, node, prop, value):
        '''
        Store a piece of information (by prop:value) about a given node.
        ( value must *not* be None )

        Example:
            g.setNodeProp(node, 'Description', 'My Node Is Awesome!')
        '''
        if value is None:
            raise Exception('graph prop values may not be None! %r' % (node,))

        curval = node[1].get(prop)
        if curval == value:
            return False

        node[1][prop] = value

        try:
            if curval is not None:
                curlist = self.nodeprops[prop][curval]
                curlist.remove( node )

            self.nodeprops[prop][value].append(node)
        except TypeError:
            pass # no value indexing for un-hashable values

        return True

    def getNodesByProp(self, prop, val=None):
        '''
        Retrieve a list of nodes with the given property (optionally value).

        Example:
            for node in g.getNodesByProp("awesome",1):
                print(node)
        '''
        if val is not None:
            return self.nodeprops.get(prop,{}).get(val,[])

        ret = []
        [ ret.extend(v) for v in self.nodeprops.get(prop,{}).values() ]
        return ret

    def addNode(self, nid=None, nprops=None, **kwargs):
        '''
        Add a Node object to the graph.  Returns the node. (nid,nprops)

        Example: node = g.addNode()
                 - or -
                 node = g.addNode('woot', {'height':20, 'width':20})

        NOTE: If nid is unspecified, it is considered an 'anonymous'
              node and will have an ID automagically assigned.
        '''
        if nid is None:
            nid = guid()

        p = self.nodes.get(nid)
        if p is not None:
            raise DuplicateNode(nid)

        myprops = {}
        myprops.update(kwargs)
        if nprops is not None:
            myprops.update(nprops)

        node = (nid, myprops)
        self.nodes[nid] = node

        for k, v in myprops.items():
            try:
                self.nodeprops[k][v].append(node)
            except TypeError:
                pass

        return node

    def formNode(self, prop, value, ctor=None):
        '''
        Retrieve or create a node with the given prop=value.

        If no node with the given property exists, create a new
        one and trigger the optional ctor function.  This allows
        uniq'd "primary property" nodes in the graph.

        NOTE: this will *only* be deconflicted with other formNode
              calls.

        Example:
            def fooctor(node):
                g.setNodeProp(node,"thing",0)

            node1 = g.formNode("foo","bar",ctor=fooctor)
            ...
            node2 = g.formNode("foo","bar",ctor=fooctor)
            # node2 is a ref to node1 and fooctor was called once.
        '''
        with self.formlock:
            node = self.formnodes.get( (prop,value) )
            if node is not None:
                return node

            nid = guid()
            node = (nid,{prop:value})

            self.nodes[nid] = node
            self.formnodes[ (prop,value) ] = node
            self.nodeprops[prop][value].append(node)

            # fire ctor with lock to prevent an un-initialized retrieve.
            if ctor is not None:
                ctor(node)
            return node

    def delNodeProp(self, node, prop):
        '''
        Delete a property from a node.

        Example:
            g.delNodeProp(node,"foo")
        '''
        pval = node[1].pop(prop,None)
        if pval is not None:
            try:
                vlist = self.nodeprops[prop][pval]
                vlist.remove(node)
                if not vlist:
                    self.nodeprops[prop].pop(pval,None)
            except TypeError:
                pass # no value indexes for unhashable types
        return pval

    def delNodesProps(self, props):
        '''
        Delete all listed properties from all nodes in the graph.

        Example:
            g.delNodesProps(('foo', 'bar'))
        '''
        for prop in props:
            for node in self.getNodesByProp(prop):
                self.delNodeProp(node, prop)

    def delNode(self, node):
        '''
        Delete a node from the graph.

        Example:
            g.delNode(node)
        '''
        for edge in self.getRefsFrom(node)[:]:
            self.delEdge(edge)
        for edge in self.getRefsTo(node)[:]:
            self.delEdge(edge)
        [ self.delNodeProp(node, k) for k in list(node[1].keys()) ]
        return self.nodes.pop(node[0])

    def getNode(self, nid):
        '''
        Return the dictionary of properties for the specified node id.
        '''
        return self.nodes.get(nid)

    def getNodeProps(self, nid):
        return self.nodes.get(nid)[1]

    def getNodes(self):
        '''
        Return a list of (nid, nprops) tuples.
        '''
        return list(self.nodes.values())

    def getNodeCount(self):
        return len(self.nodes)

    def isLeafNode(self, node):
        '''
        A node is a "leaf" node if he has no "outgoing" edges.
        '''
        return len(self.getRefsFrom(node)) == 0

    def isRootNode(self, node):
        '''
        A node is a "root" node if he has no "incoming" edges.
        '''
        return len(self.getRefsTo(node)) == 0

    def hasEdge(self, edgeid):
        return self.edges.get(edgeid) is not None

    def hasNode(self, nid):
        '''
        Check if a given node is present within the graph.

        Example: if g.hasNode('yermom'): print('woot')
        '''
        return self.getNode(nid) is not None

    def addEdgeByNids(self, n1, n2, eid=None, eprops=None, **kwargs):
        node1 = self.getNode(n1)
        node2 = self.getNode(n2)
        return self.addEdge(node1, node2, eid=eid, eprops=eprops, **kwargs)

    def addEdge(self, node1, node2, eid=None, eprops=None, **kwargs):
        '''
        Add an edge to the graph.  Edges are directional.

        Example: g.addEdge(node1, node2, eprops={'name':'Woot Edge'})
        '''
        if eprops is None:
            eprops = {}

        eprops.update(kwargs)
        if eid is None:
            eid = guid()

        n1 = node1[0]
        n2 = node2[0]

        edge = (eid, n1, n2, eprops)

        self.edges[eid] = edge
        self.edge_by_to[n2].append(edge)
        self.edge_by_from[n1].append(edge)

        for k, v in eprops.items():
            try:
                self.edgeprops[k][v].append(edge)
            except TypeError:
                pass # no value indexes for unhashable types

        return edge

    def delEdge(self, edge):
        eid,n1,n2,eprops = edge
        [ self.delEdgeProp(edge,k) for k in list(eprops.keys()) ]

        self.edges.pop(eid)
        self.edge_by_to[n2].remove(edge)
        self.edge_by_from[n1].remove(edge)

    def delEdgeByEid(self, eid):
        '''
        Delete an edge from the graph (by eid).

        Example: g.delEdge(eid)
        '''
        edge = self.getEdge(eid)
        return self.delEdge(edge)

    def delEdgeProp(self, edge, prop):
        '''
        '''
        v = edge[3].pop(prop,None)
        if v is not None:
            try:
                vlist = self.edgeprops[prop][v]
                vlist.remove(edge)
                if not vlist:
                    self.edgeprops[prop].pop(v,None)
            except TypeError:
                pass # no value indexes for unhashable types
        return v

    def delEdgesProps(self, props):
        '''
        Delete all listed properties from all edges in the graph.

        Example:
            g.delEdgesProps(('foo', 'bar'))
        '''
        for prop in props:
            for edge in self.getEdgesByProp(prop):
                self.delEdgeProp(edge, prop)

    def getRefsFrom(self, node):
        '''
        Return a list of edges which originate with us.

        Example: for eid, n1, n2, eprops in g.getRefsFrom(node):
        '''
        return self.edge_by_from.get(node[0],[])

    def getRefsFromByNid(self, nid):
        return self.edge_by_from.get(nid,[])

    def getRefsTo(self, node):
        '''
        Return a list of edges which terminate at us.

        Example: for eid, n1, n2, eprops in g.getRefsFrom(node):
        '''
        return self.edge_by_to.get(node[0],[])

    def getRefsToByNid(self, nid):
        return self.edge_by_to.get(nid,[])

    def getClusterGraphs(self):
        '''
        Return a list of the subgraph clusters (as graphs) contained
        within this graph.  A subgraph "cluster" is defined as a
        group of interconnected nodes.  This can be used to split
        out grouped subgraphs from within a larger graph.
        '''
        ret = []

        nodes = self.getNodes()
        done = {}
        for nid, nprops in nodes:

            if done.get(nid):
                continue

            # Generate the cluster subgraph
            todo = [ (nid, nprops), ]
            g = Graph()

            while len(todo):
                gnid, gnprops = todo.pop()

                done[gnid] = True

                if not g.hasNode(gnid):
                    g.addNode(nid=gnid, nprops=gnprops)

                for eid, n1, n2, eprops in self.getRefsFromByNid(gnid):

                    if not g.getNode(n2):
                        n2props = self.getNodeProps(n2)
                        g.addNode(nid=n2, nprops=n2props)
                        todo.append((n2, n2props))

                    if not g.getEdge(eid):
                        g.addEdgeByNids(n1, n2, eid=eid, eprops=eprops)

                for eid, n1, n2, eprops in self.getRefsToByNid(gnid):

                    if not g.getNode(n1):
                        n1props = self.getNodeProps(n1)
                        g.addNode(nid=n1, nprops=n1props)
                        todo.append((n1, n1props))

                    if not g.getEdge(eid):
                        g.addEdgeByNids(n1, n2, eid=eid, eprops=eprops)

            ret.append(g)

        return ret


    def pathSearchOne(self, *args, **kwargs):
        for p in self.pathSearch(*args, **kwargs):
            return p

    def pathSearch(self, n1, n2=None, edgecb=None, tocb=None):
        '''
        Search for the shortest path from one node to another
        with the option to filter based on edges using
        edgecb.  edgecb should be a function:

        def myedgecb(graph, eid, n1, n2, depth)

        which returns True if it's OK to traverse this node
        in the search.

        Additionally, n2 may be None and the caller may specify
        tocb with a function such as:

        def mytocb(graph, nid)

        which must return True on finding the target node

        Returns a list of edge ids...
        '''

        if n2 is None and tocb is None:
            raise Exception('You must use either n2 or tocb!')

        root = vg_pathcore.newPathNode(nid=n1, eid=None)

        todo = [(root, 0),]

        # FIXME make this a deque so it can be FIFO
        while len(todo):

            pnode,depth = todo.pop() # popleft()
            ppnode, pkids, pprops = pnode

            nid = pprops.get('nid')
            for edge in self.getRefsFromByNid(nid):

                eid, srcid, dstid, eprops = edge

                if vg_pathcore.isPathLoop(pnode, 'nid', dstid):
                    continue

                # Check if the callback is present and likes us...
                if edgecb is not None:
                    if not edgecb(self, edge, depth):
                        continue

                # Are we the match?
                match = False
                if dstid == n2:
                    match = True

                if tocb and tocb(self, dstid):
                    match = True

                if match:

                    m = vg_pathcore.newPathNode(pnode, nid=dstid, eid=eid)
                    path = vg_pathcore.getPathToNode(m)

                    ret = []
                    for ppnode, pkids, pprops in path:
                        eid = pprops.get('eid')
                        if eid is not None:
                            ret.append(eid)

                    yield ret

                # Add the next set of choices to evaluate.
                branch = vg_pathcore.newPathNode(pnode, nid=dstid, eid=eid)
                todo.append((branch, depth+1))

        #return []

    def pathSearchFrom(self, n1, nodecb, edgecb=None):
        '''
        Search from the specified node (breadth first) until you
        find a node where nodecb(graph, nid) == True.  See
        pathSearchFromTo for docs on edgecb...
        '''

class HierGraph(Graph):
    '''
    An extension to the directed Graph class which facilitates the
    idea of node "hierarchies" which begin with root nodes.

    NOTE: rootnodes are designated by the presence of the "rootnode"
          property.
    '''
    def __init__(self):
        Graph.__init__(self)

    def addHierRootNode(self,*args,**kwargs):
        '''
        This API is the same as Graph.addNode but will also
        mark the newly created node as a rootnode.
        '''
        node = self.addNode(*args,**kwargs)
        self.setNodeProp(node,'rootnode',True)
        return node

    def setHierRootNode(self, node):
        return self.setNodeProp(node,'rootnode',True)

    def getHierRootNodes(self):
        '''
        Get all the node id's in this graph which are weight 0 (meaning
        they have no parents)...
        '''
        return self.getNodesByProp('rootnode')

    def getHierNodeWeights(self):
        '''
        Calculate the node weights for the given nodes in the hierarchical
        graph based on the added "rootnode" nodes.  This will return a dict
        of { nid: weight, } key-pairs.

        # NOTE: This will also set the 'weight' property on the nodes
        '''
        weights = {}

        rootnodes = self.getHierRootNodes()
        if not len(rootnodes):
            raise Exception('getHierNodeWeights() with no root nodes!')

        todo = [ (root[0], {}) for root in rootnodes ]
        while len(todo):

            nid,path = todo.pop()

            cweight = weights.get(nid, 0)
            weights[nid] = max(cweight, len(path))

            path[nid] = True

            for eid, n1, n2, eprops in self.getRefsFromByNid(nid):
                if weights.get(n2, -1) >= len(path):
                    continue
                if not path.get(n2):
                    todo.append((n2, dict(path)))

        for nid,weight in weights.items():
            node = self.getNode(nid)
            self.setNodeProp(node,'weight',weight)

        return weights

    def getHierPathCount(self):
        '''
        Retrieve the total number of paths from the specified
        node to any "leaf" nodes which are reachable.

        Example:

            if g.getHierPathCount() > pathmax:
                print('skipping huge graph!')

        '''
        # We must put all nodes into weight order
        weights = self.getHierNodeWeights()

        # root nodes get a beginning score of 1
        pcounts = zdict()
        for root in self.getHierRootNodes():
            pcounts[root[0]] = 1

        def weightcmp(n1node,n2node):
            return cmp(n1node[1]['weight'],n2node[1]['weight'])

        nodes = self.getNodes()

        # Lets make the list of nodes *ordered* by weight
        nodes.sort(key=lambda k: k[1]['weight'])

        # Here's the magic... In *hierarchy order* each node
        # gets the sum of the paths of his parents.
        ret = 0
        for node in nodes:

            for eid, n1, n2, eprops in self.getRefsFrom(node):
                # edge to node with == weight is a loop...
                if weights[n1] == weights[n2]:
                    continue

                pcounts[n2] += pcounts[n1]

        return sum([ pcounts[n[0]] for n in nodes if self.isLeafNode(n) ])

    def getHierPathsFrom(self, node, loopcnt=0, maxpath=None, maxlen=None):
        '''
        Retrieve a generator of lists of (node,edge) tuples which represent
        the paths from the specified node to any terminating "leaf" nodes.

        Options:
            loopcnt - how many times may a single node be repeated in a path
            maxpath - maximum number of paths to yield
            maxlen  - maximum "length" of a path ( trunc if too long )

        NOTE: The last tuple in the list will have edge is None.
              However, if the last element in the list represents a
              truncated loop, the last tuple's "edge" field will be
              filled in with the loop's edge.

        Example:
            for path in g.getHierPathsFrom():
                for node,edge in path:
                    checkstuff(node,edge)
        '''
        cnt = 0
        todo = [(node,[],[node[0],])] # [ node, path, nids ]

        while todo:

            # nids is a speed hack...
            pnode,path,nids = todo.pop()

            edges = self.getRefsFrom(pnode)

            if len(edges) == 0: # leaf/root...

                path.append( (pnode,None) )
                yield path

                cnt += 1
                if maxpath is not None and cnt >= maxpath:
                    return

                continue

            if maxlen and len(path) >= maxlen:
                continue

            for edge in edges:
                # yep... coppies...
                # ( still faster than keeping/culling tree )
                newpath = list(path)
                newpath.append((pnode,edge))

                etoid = edge[2]
                if nids.count(etoid) > loopcnt:

                    yield newpath

                    cnt += 1
                    if maxpath is not None and cnt >= maxpath:
                        return

                    continue

                newnids = list(nids)
                newnids.append(etoid)

                nnode = self.getNode(etoid)
                todo.append((nnode,newpath,newnids))

    def getHierPathsThru(self, node, maxpath=None, maxlen=None):
        '''
        Retrieve a generator of paths from root-->leaf nodes in this
        graph which must also traverse the specified node.
        '''
        cnt = 0
        for pathto in self.getHierPathsTo(node, maxpath=maxpath, maxlen=maxlen):
            for pathfrom in self.getHierPathsFrom(node, maxpath=maxpath, maxlen=maxlen):
                yield pathto[:-1] + pathfrom
                cnt += 1
                if maxpath is not None and cnt >= maxpath:
                    return

    def getHierPathsTo(self, node, maxpath=None, maxlen=None):
        '''
        Retrieve a generator of lists of (node,edge) tuples which represent
        the paths to specified node from any root nodes.

        (See getHierPathsFrom for details )
        '''
        cnt = 0
        todo = [(node,[(node,None)],[node[0],])] # [ node, path, nids ]

        while todo:

            # nids is a speed hack...
            pnode,path,nids = todo.pop()

            edges = self.getRefsTo(pnode)
            if len(edges) == 0: # leaf/root...

                path.reverse()
                yield path

                cnt += 1
                if maxpath is not None and cnt >= maxpath:
                    return

                continue

            if maxlen and len(path) >= maxlen:
                continue

            for edge in edges:
                # yep... coppies...
                # ( still faster than keeping/culling tree )
                etoid = edge[1]
                nnode = self.getNode(etoid)

                newpath = list(path)
                newpath.append((nnode,edge))

                if etoid in nids:
                    continue

                newnids = list(nids)
                newnids.append(etoid)

                todo.append((nnode,newpath,newnids))
