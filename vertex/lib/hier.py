import vertex.graph as v_graph

from collections import deque

class HierGraph(v_graph.Graph):
    '''
    A vertex.Graph subclass to assist with hierarchical graphs.

    The HierGraph uses a few data conventions to implement additional
    graph functionality based on the assumption of a hierarchy which
    begins at root nodes and terminates at nodes which originate no
    edges.

    Concepts:
    * root      - a node that we know ( a-priori ) is a root
    * leaf      - a node with no edges originating from it
    * tiers     - graph layering concept to facilitate path short cuts
    * minpath   - cached shortest distance to a leaf
    * maxpath   - cached longest distance to a leaf

    Example:

        g = HierGraph()

        n1 = g.addNode(foo=10,root=True)
        n2 = g.addNode(foo=20)
        n3 = g.addNode(foo=30)
        n4 = g.addNode(foo=40)

        e1 = g.addEdge(n1,n2)
        e2 = g.addEdge(n1,n3)

        e3 = g.addEdge(n2,n4)
        e4 = g.addEdge(n3,n4)

        With "root" node n1:

            n1      - tier 0
           /  \ 
          n2  n3    - tier 1
           \  /
            n4      - tier 2

    '''

    def __init__(self, store=None):
        v_graph.Graph.__init__(self, store=store)
        self.initNodeIndex('tier','keyval')
        self.initNodeIndex('root','keyval')
        self.initNodeIndex('leaf','keyval')

    def calcNodeTiers(self):

        # clear out any old tiers
        nodes = self.getNodesByProp('tier')
        [ self.delNodeProp(n,'tier') for n in nodes ]

        # clear out any old leaf props
        nodes = self.getNodesByProp('leaf')
        [ self.delNodeProp(n,'leaf') for n in nodes ]

        # set all root nodes to tier 0
        roots = self.getNodesByProp('root')
        [ self.setNodeProp(n,'tier',0) for n in roots ]

        todo = deque([ (node,{node[0]:True}) for node in roots ])

        maxtier = 0

        while todo:
            node,path = todo.popleft()
            tier = node[1].get('tier')
            maxtier = max(maxtier,tier)

            destnodes = list(self.getN2NodesByN1(node))
            if len(destnodes) == 0:
                self.setNodeProp(node,'leaf',1)
                continue

            for nextnode in destnodes:

                # loop detection
                if path.get(nextnode[0]):
                    continue

                # see if we need to move him down...
                t = nextnode[1].get('tier',0)
                if t > tier:
                    continue

                nextpath = dict(path)
                nextpath[ nextnode[0] ] = True
                self.setNodeProp(nextnode,'tier',tier + 1)
                todo.append( (nextnode,nextpath) )

        # save this for later so any "reverse traversers" can use
        self.setGraphInfo('maxtier',maxtier)

        # we have now set tier=<level> on *reachable* nodes

    def calcPathHints(self):
        '''
        Calculate a set of path traversal hints for the nodes.

        Each node gets the following props:

        * minpath   - shortest distance from the node to a leaf
        * maxpath   - longest distance from the node to a leaf

        Once calculated, the values may be used to "prefer" paths
        based on the desire for either short or long paths.
        '''
        self.calcNodeTiers()

        maxtier = self.getGraphInfo('maxtier')

        # traverse the tiers in reverse
        for tier in range(maxtier,-1,-1):

            for node in self.getNodesByProp('tier',tier):
                if node[1].get('leaf'):
                    self.setNodeProp(node,'minpath',0)
                    self.setNodeProp(node,'maxpath',0)
                    continue

                n2nodes = self.getN2NodesByN1(node)
                n2nodes = [ n for n in n2nodes if n[1].get('tier') > tier ]

                n2min = [ n[1].get('minpath') for n in n2nodes ]
                n2max = [ n[1].get('maxpath') for n in n2nodes ]

                self.setNodeProp(node,'minpath',min(n2min) + 1)
                self.setNodeProp(node,'maxpath',max(n2max) + 1)

