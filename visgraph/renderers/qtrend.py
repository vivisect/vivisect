from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *

import visgraph.renderers as vg_render

class QtGraphRenderer(vg_render.GraphRenderer, QGraphicsView):

    def __init__(self, graph, parent=None):
        QGraphicsView.__init__(self, parent=parent)
        vg_render.GraphRenderer.__init__(self, graph)

        scene = QGraphicsScene(parent=self)
        self.setScene(scene)

    def delNode(self, nid, ninfo):
        g = self._vg_graph
        scene = self.scene()
        scene.removeItem(ninfo['gproxy'])
        [scene.removeItem(einfo['gproxy']) for (eid, n1, n2, einfo) in g.getRefsToByNid(nid)]
        [scene.removeItem(einfo['gproxy']) for (eid, n1, n2, einfo) in g.getRefsFromByNid(nid)]
        g.delNode(nid)

    def setNodeSizes(self, graph):
        nodes = graph.getNodes()
        [self._getNodeWidget(nid, nprops) for (nid, nprops) in nodes]

    def _getNodeWidget(self, nid, ninfo):

        wid = ninfo.get('widget')
        if wid is None:
            rep = ninfo.get('repr')
            if rep is None:
                rep = 'node: %s' % nid

            wid = QLabel(rep)
            ninfo['widget'] = wid

        gproxy = ninfo.get('gproxy')
        if gproxy is None:
            gproxy = self.scene().addWidget(wid)
            # Nodes always get drawn on top!
            # gproxy.setZValue( 1.0 )
            ninfo['gproxy'] = gproxy
            geom = gproxy.geometry()
            ninfo['size'] = (int(geom.width()), int(geom.height()))

        return gproxy

    def renderEdge(self, eid, einfo, points):
        scene = self.scene()

        # If we have been drawn already, get rid of it.
        gproxy = einfo.get('gproxy')
        if gproxy:
            scene.removeItem(gproxy)

        qpoints = [QtCore.QPointF(x, y) for (x, y) in points]
        qpoly = QtGui.QPolygonF(qpoints)

        ecolor = self._vg_graph.getMeta('edgecolor', '#000')
        ecolor = einfo.get('color', ecolor)

        pen = QtGui.QPen(QtGui.QColor(ecolor))
        gproxy = self.scene().addPolygon(qpoly, pen=pen)
        gproxy.setZValue(-1.0)

        einfo['gproxy'] = gproxy

    def renderNode(self, nid, ninfo, xpos, ypos):
        scene = self.scene()

        gproxy = self._getNodeWidget(nid, ninfo)

        x, y = ninfo.get('position')
        w, h = ninfo.get('size')

        geom = gproxy.geometry()
        geom.moveTo(x - (w >> 1), y - (h >> 1))
        gproxy.setGeometry(geom)
