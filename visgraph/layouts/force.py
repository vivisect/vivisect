import math
import random
import logging
import itertools
import traceback

import visgraph.layouts as vg_layouts

logger = logging.getLogger(__name__)

# coulomb's constant approximation
ke = 8.98755

def irand():
    return random.randint(100, 200)

class vector:

    def __init__(self, force=0.0, angle=0.0):
        self.force = force
        self.angle = angle

    def addDrag(self, drag):
        self.force *= drag

    def addVect(self, force, angle):
        '''
        Update the vector by adding the given force/angle.
        '''
        # Use head-to-tail addition
        dx = math.cos(self.angle) * self.force + math.cos(angle) * force
        dy = math.sin(self.angle) * self.force + math.sin(angle) * force
        self.force = math.hypot(dx,dy)
        self.angle = math.atan2(dy, dx)

    def getMovement(self, x, y, maxmov=None):
        dx = math.cos(self.angle) * self.force
        dy = math.sin(self.angle) * self.force
        if maxmov:
            dx = min(dx,maxmov)
            dy = min(dy,maxmov)
        return x+dx,y+dy

class ForceLayout(vg_layouts.GraphLayout):

    def __init__(self, graph):
        vg_layouts.GraphLayout.__init__(self, graph)

        self._f_rand = random.SystemRandom()
        self._f_randint = self._f_rand.randint
        self._f_mmax = 200          # Max delta for X or Y during ticks
        self._f_imax = None         # Max physx ticks from on call to layoutGraph()
        self._f_drag = 0.80         # Drag coeficient to slow nodes down
        self._f_charge = 80         # Used in coulomb calcs
        #self._f_minforce = 4        # When is the graph "stable enough"
        self._f_springrate = 0.1    # Used in hooke calcs
        self._f_minavgforce = 0.25

    def setMaxTickMove(self, mmax):
        '''
        Set the maximum distance that any one node is allowed
        to move in one tick of the engine. This can keep overly
        strong repulsion reactions in check.
        '''
        self._f_mmax = mmax

    def getLayoutSize(self):
        return 99999,99999

    def setRandomLayout(self, graph):

        rands = {}
        nodes = graph.getNodes()
        # give a small random layout to any node with no position
        randmax = len( nodes ) * 10
        for nid,nprops in nodes:

            if nprops.get('position'):
                continue

            rpos = ( self._f_randint( 1, randmax ), self._f_randint( 1, randmax ) )
            while rands.get(rpos):
                rpos = ( self._f_randint( 1, randmax ), self._f_randint( 1, randmax ) )

            rands[rpos] = True
            nprops['position'] = rpos


    def layoutGraph(self):

        # Setup a random layout to start with
        self.setRandomLayout( self.graph )

        # Layout each contiguous cluster seperately
        cgraphs = self.graph.getClusterGraphs()
        for graph in cgraphs:

            nodes = graph.getNodes()
            edges = graph.getEdges()

            try:

                for i in itertools.count():

                    totforce = self._tickPhysicsEngine(graph)

                    # If the system's overall energy is less than minforce, done!
                    #if totforce < self._f_minforce:
                    if totforce / len(nodes) < self._f_minavgforce:
                        break

                    if self._f_imax and i >= self._f_imax:
                        break

            except Exception:
                logger.error(traceback.format_exc())

        # Now, in order from largest to smallest, shift them back toward 0,0
        cgraphs.sort( cmp=lambda x,y: cmp(y.getNodeCount(), x.getNodeCount()) )

        offset = 0
        for graph in cgraphs:
            x,y,xmax,ymax = self._getLayoutGeom(graph)
            self._shiftGraphLayout( graph, 0 - x, offset - y )
            offset += ( ymax - y )
            #self._shiftGraphLayout( graph, offset - x, 0 - y )
            #offset += ( xmax - x )

        # Now lets calculate some straight line edges
        self._setEdgePoints()

    def _shiftGraphLayout(self, graph, dx, dy):
        nodes = graph.getNodes()
        # ugly speed hack... "ephemeral list comprehension"
        [ graph.setNodeProp(n, 'position', (n[1]['position'][0] + dx, n[1]['position'][1] + dy) ) for n in nodes ]

    def _getLayoutGeom(self, graph):
        # return x,y,xmax,ymax for this graph
        xmin = 0xffffffff
        ymin = 0xffffffff
        xmax = 0
        ymax = 0
        nodes = graph.getNodes()
        for nid,nprops in nodes:

            w,h = nprops.get('size')
            x,y = nprops.get('position')

            xmin = min( xmin, x - ( w / 2 ) )
            ymin = min( ymin, y - ( h / 2 ) )
            xmax = max( xmax, x + ( w / 2 ) )
            ymax = max( ymax, y + ( h / 2 ) )

        return xmin,ymin,xmax,ymax

    def incLayoutGraph(self):
        '''
        Layout the graph "incrementally" ( and return bool showing
        weather or not we need another increment ).

        Example:
            while l.incLayoutGraph():

        '''
        self.setRandomLayout( self.graph )
        cgraphs = self.graph.getClusterGraphs()

        needmore = False

        for graph in cgraphs:

            nodes = graph.getNodes()
            edges = graph.getEdges()

            try:

                totforce = self._tickPhysicsEngine(graph)
                if totforce / len(nodes) > self._f_minavgforce:
                    needmore = True

            except Exception as e:
                logger.error(traceback.format_exc())

        # Now, in order from largest to smallest, shift them back toward 0,0
        cgraphs.sort( cmp=lambda x,y: cmp(y.getNodeCount(), x.getNodeCount()) )

        offset = 0
        for graph in cgraphs:
            x,y,xmax,ymax = self._getLayoutGeom( graph )
            self._shiftGraphLayout( graph, 0 - x, offset - y )
            offset += ( ymax - y )
            #self._shiftGraphLayout( graph, offset - x, 0 - y )
            #offset += ( xmax - x )

        # Now lets calculate some straight line edges
        self._setEdgePoints()
        return needmore

    def _setEdgePoints(self):
        for eid,n1,n2,einfo in self.graph.getEdges():
            n1pos = self.graph.getNodeProps(n1)['position']
            n2pos = self.graph.getNodeProps(n2)['position']
            einfo['edge_points'] = [ n1pos, n2pos ]

    def _tickPhysicsEngine(self, graph):

        totforce = 0

        nodes = graph.getNodes()

        for nid, nprops in nodes:

            vect = vector()

            # For each other node, calculate the coulomb repulsion
            # as a directional vector and sum them
            vadd = vect.addVect
            repul = self._coulombRepulsion

            # Speed hack (ephemeral list comprehension)
            [ vadd( *repul(nprops, n2props ) ) for (n2id,n2props) in nodes if n2id != nid ]

            # Now lets calculate some edge "spring" forces and add
            # those in too...
            for eid,n1,n2,einfo in graph.getRefsFromByNid( nid ):
                n2props = graph.getNodeProps( n2 )
                force,angle = self._hookeAttraction( nprops, n2props )
                vect.addVect(force, angle)

            for eid,n1,n2,einfo in graph.getRefsToByNid( nid ):
                n2props = graph.getNodeProps( n1 )
                force,angle = self._hookeAttraction( nprops, n2props )
                vect.addVect(force, angle)

            # All repulsive forces are added to this node's vect
            # time to add some drag....
            drag = nprops.get('drag')
            if drag is None:
                drag = self._f_drag
            vect.addDrag( drag )
            # FIXME allow the graph to specify drag per node

            newpos = vect.getMovement( *nprops['position'], maxmov=self._f_mmax)
            graph.setNodeProp( (nid,nprops), 'position', newpos)

            totforce += vect.force

        return totforce

    def _coulombRepulsion(self, n1props, n2props ):
        x1,y1 = n1props.get('position')
        x2,y2 = n2props.get('position')

        # Calculate the deltas
        dx = x2-x1
        dy = y2-y1

        distance = math.hypot(dx, dy)
        force = ke * ( ( self._f_charge * self._f_charge ) / distance**2 )
        # Invert the angle to make the force "repulsion"
        angle = math.atan2(dy, dx) - math.pi
        return force,angle

    def _hookeAttraction(self, n1props, n2props):
        x1,y1 = n1props.get('position')
        x2,y2 = n2props.get('position')
        dx = x2-x1
        dy = y2-y1
        distance = math.hypot(dx, dy)
        angle = math.atan2(dy, dx)
        force = distance * self._f_springrate
        return force,angle

