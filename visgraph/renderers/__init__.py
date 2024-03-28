'''
Home of the code which knows how to actually *draw* a graph which
has been layed out.
'''

class GraphRenderer:
    '''
    Only a "renderer" knows how big each node will end up based on metadata
    in the graph which is specific to the renderer.

    All renderers should be able to set the (x,y) "size" tuple
    '''
    def __init__(self, graph):
        self._vg_graph = graph
        self._vg_layout = None

        self._vg_rendering = False
        self._vg_canvas_width = 0
        self._vg_canvas_height = 0

    def beginRender(self, width, height):
        self._vg_rendering = True
        self._vg_canvas_width = width
        self._vg_canvas_height = height

    def endRender(self):
        self._vg_rendering = False

    def setNodeSizes(self, graph):
        '''
        Calculate the sizes for each node based on graph metadata (or defaults)
        '''
        raise Exception('%s must implement setNodeSizes!' % self.__class__.__name__)

    def renderNode(self, nid, ninfo, xpos, ypos):
        '''
        Render the given node at the specified position.
        '''
        raise Exception('%s must implement renderNode!' % self.__class__.__name__)

    def renderEdge(self, eid, einfo, points):
        '''
        Render an edge in the graph by drawing lines between all the listed
        points (as (x,y) tuples...)
        '''
        raise Exception('%s must implement renderEdge!' % self.__class__.__name__)

    def renderGraph(self):

        graph = self._vg_graph

        width, height = graph.getMeta('size',(800,600))
        self.beginRender(width, height)

        # Render each of the nodes (except ghost nodes...)
        for nid,ninfo in graph.getNodes():
            if ninfo.get('ghost'):
                continue
            xpos, ypos = ninfo.get('position')
            self.renderNode(nid, ninfo, xpos, ypos)

        # Render the edges
        for eid, fromid, toid, einfo in graph.getEdges():
            points = einfo.get('edge_points')
            if points is not None:
                self.renderEdge(eid, einfo, points)

        self.endRender()
