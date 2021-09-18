'''
A dynadag-ish graph layout calculator...
'''

import visgraph.layouts as vg_layout
import visgraph.drawing.bezier as vg_bezier

zero_zero = (0,0)

def revenumerate(l):
    return list(zip(range(len(l)-1, -1, -1), reversed(l)))

SCOOCH_LEFT     = 0
SCOOCH_RIGHT    = 1

class DynadagLayout(vg_layout.GraphLayout):

    def __init__(self, graph, barry=10):

        vg_layout.GraphLayout.__init__(self, graph)

        self._addGhostNodes()

        self._barry_count = barry
        self.width_pad = 20
        self.height_pad = 40

    def getLayoutSize(self):
        '''
        Return the width,height of this layout.
        '''
        height = 0
        width  = 0
        for layer in self.layers:

            lheight = 0
            lwidth = 0

            for nid,ninfo in layer:
                xsize, ysize = ninfo.get('size', zero_zero)
                lheight = max(lheight, ysize + self.height_pad)
                lwidth += xsize + self.width_pad

            height += lheight
            width = max(lwidth, width)

        return width, height

    def _baryCenter(self, nid, ninfo):
        tot = 0
        cnt = 0
        for eid, n1, n2, einfo in self.graph.getRefsFromByNid(nid):
            node2 = self.graph.getNode(n2)
            tot += node2[1].get('layerpos')
            cnt += 1

        for eid, n1, n2, einfo in self.graph.getRefsToByNid(nid):
            node1 = self.graph.getNode(n1)
            tot += node1[1].get('layerpos')
            cnt += 1
        barry = 0
        if cnt:
            barry = tot / float(cnt)
        ninfo['barycenter'] = barry

    # Try out "barycenter" averaging and re-ordering.
    def _orderNodesByBary(self):
        # Go through the layers and do barycenter calcs first.
        # FIXME how do we tell when we're done?
        for i in range(self._barry_count):
            for layer in self.layers:
                for nid, ninfo in layer:
                    self._baryCenter(nid, ninfo)

            for layer in self.layers:
                layer.sort(key=lambda k: k[1].get('barycenter'))
                for i, (nid, ninfo) in enumerate(layer):
                    ninfo['layerpos'] = i

    def _getNodeRelPos(self, nid, ninfo):

        weight = ninfo['weight']

        abovepos = []
        for eid, n1, n2, einfo in self.graph.getRefsToByNid(nid):
            fprops = self.graph.getNodeProps(n1)
            if fprops['weight'] != weight-1:
                continue
            abovepos.append(fprops['layerpos'])
        abovepos.sort()

        belowpos = []
        for eid, n1, n2, einfo in self.graph.getRefsFromByNid(nid):
            tprops = self.graph.getNodeProps(n2)
            if tprops['weight'] != weight+1:
                continue
            belowpos.append(tprops['layerpos'])
        belowpos.sort()

        return abovepos, belowpos

    def _getLayerCross(self, layernum):
        ccount = 0

        layer = self.layers[layernum]
        for i in range(1, len(layer)):

            myabove, mybelow = self._getNodeRelPos(*layer[i])
            hisabove, hisbelow = self._getNodeRelPos(*layer[i-1])

            # If I have any nodes above with position lower
            # than any of his, those are cross overs...
            for mya in myabove:
                for hisa in hisabove:
                    if mya < hisa:
                        ccount += 1

            # If I have any nodes below with position lower
            # than any of his, those acre cross overs...
            for myb in mybelow:
                for hisb in hisbelow:
                    if myb < hisb:
                        ccount += 1

        return ccount

    def _bubSortNodes(self):

        # Go through nodes and see if we can re-order children to
        # reduce crossovers...

        for i in range(len(self.layers)):

            layer = self.layers[i]

            reduced = True
            while reduced:

                reduced = False

                # Get the current crossover count for this layer
                score = self._getLayerCross(i)

                # TODO should we do this multipliciative rather than
                # neighbors only?
                for j in range(len(layer)-1):

                    n1 = layer[j]
                    n2 = layer[j+1]

                    layer[j] = n2
                    layer[j+1] = n1

                    newscore = self._getLayerCross(i)
                    # If this was optimal, keep it and continue
                    if newscore < score:
                        reduced = True
                        n1[1]['layerpos'] = j+1
                        n2[1]['layerpos'] = j
                        break

                    # Nope, put it back...
                    layer[j] = n1
                    layer[j+1] = n2
                    
    def _addGhostNodes(self):
        '''
        Translate the hierarchical graph we are given into dynadag
        friendly graph with ghost nodes....
        '''
        weights = self.graph.getHierNodeWeights()

        # First lets take care of any loop edges
        # (These will be nodes in the graph which are marked "reverse=True"
        # but have been added with src/dst swapped to make graphing easier)
        for eid, n1, n2, einfo in self.graph.getEdges():

            if not einfo.get('reverse'):
                continue

            topweight = weights.get(n1)
            botweight = weights.get(n2)

            # In the case of a single block loop, add one ghost and
            # connect them all
            #if n1 == n2:
            if topweight == botweight:
                bridgenode = self.graph.addNode(ghost=True, weight=topweight)
                weights[bridgenode[0]] = topweight

                self.graph.delEdgeByEid(eid)
                self.graph.addEdgeByNids(n1, bridgenode[0], looptop=True)
                self.graph.addEdgeByNids(bridgenode[0], n2, loopbot=True)
                continue

            # For a "reverse" edge, add a node in the weight for each
            # and connect them.
            topnode = self.graph.addNode(ghost=True, weight=topweight)
            weights[topnode[0]] = topweight

            botnode = self.graph.addNode(ghost=True, weight=botweight)
            weights[botnode[0]] = botweight

            self.graph.addEdge(topnode, botnode) # For rendering, these will be normal!

            # Now, remove the "reverse" edge, and add a 'looptop' and 'loopbot' edge
            self.graph.delEdgeByEid(eid)
            self.graph.addEdgeByNids(n1, topnode[0], looptop=True)
            self.graph.addEdgeByNids(botnode[0], n2, loopbot=True)

        # Create ghost nodes for edges which pass through a weight layer
        for eid, n1, n2, einfo in self.graph.getEdges():
            xweight = weights.get(n1, 0)
            yweight = weights.get(n2, 0)
            if xweight + 1 < yweight:
                self.graph.delEdgeByEid(eid)
                while xweight + 1 < yweight:
                    xweight += 1
                    ghostid = self.graph.addNode(ghost=True, weight=xweight)[0]
                    self.graph.addEdgeByNids(n1, ghostid)
                    n1 = ghostid
                self.graph.addEdgeByNids(n1, n2)

    def layoutGraph(self):

        self.maxweight = 0

        for nid, ninfo in self.graph.getNodes():
            self.maxweight = max(ninfo.get('weight', 0), self.maxweight)

        self.layers = [ [] for i in range(self.maxweight + 1) ]

        done = set()
        def doit(node):
            '''
            Roll through all the nodes and assign them positions in their layer (based on weight)
            '''

            if node[0] in done:
                return

            done.add(node[0])
            efrom = self.graph.getRefsFrom(node)

            for eid, n1, n2, einfo in efrom:
                tonode = self.graph.getNode(n2)
                doit(tonode)

            w = node[1].get('weight', 0)

            layer = self.layers[w]
            self.graph.setNodeProp(node, 'layerpos', len(layer))
            layer.append(node)

        # FIXME support more than one root!
        for rootnode in self.graph.getHierRootNodes():
            doit(rootnode)

        # Now lets use positional averaging to order nodes in the layer
        self._orderNodesByBary()
        self._bubSortNodes()

        self.maxwidth = 0

        # Calculate the width / height of each layer...
        lwidths = []        # The width of this total layer
        self.lheights = []       # The tallest node in this layer
        for layer in self.layers:
            x = self.width_pad
            y = 0

            heightmax = 0
            for nid, ninfo in layer:
                size = ninfo.get('size', zero_zero)
                xx, yy = size

                heightmax = max(heightmax, yy)

                x += xx
                y += yy

            lwidths.append(x)
            self.lheights.append(heightmax)

            self.maxwidth = max(self.maxwidth, x)

        # Now that we have them sorted, lets set their individual positions...
        vpad = 0
        for i,layer in enumerate(self.layers):
            hpad = (self.maxwidth - lwidths[i]) / 2
            hpad += self.width_pad
            for nid,ninfo in layer:
                xpos = hpad
                ypos = vpad

                xsize, ysize = ninfo.get('size', zero_zero)

                ninfo['position'] = (xpos,ypos)
                ninfo['vert_pad'] = self.lheights[i] - ysize

                hpad += xsize

                hpad += self.width_pad

            vpad += self.lheights[i]
            vpad += self.height_pad


        # Optimize the positions of nodes by moving them outward to align

        # First from top to bottom
        for i, layer in enumerate(self.layers):

            layermid = len(layer) / 2

            # From the left side, scooch kids out...
            for j, (nid,ninfo) in enumerate(layer):

                if not ninfo.get('ghost'):
                    break

                self._scoochXKids(nid, ninfo, SCOOCH_LEFT)

            # From the right side, scooch kids out...
            for j, (nid, ninfo) in revenumerate(layer):

                if not ninfo.get('ghost'):
                    break

                self._scoochXKids(nid, ninfo, SCOOCH_RIGHT)

        # From the bottom to the top!
        for i, layer in revenumerate(self.layers):

            layermid = len(layer) / 2

            # From the left side, scooch kids out...
            for j, (nid,ninfo) in enumerate(layer):

                if not ninfo.get('ghost'):
                    break

                self._scoochXParents(nid, ninfo, SCOOCH_LEFT)

            # From the right side, scooch kids out...
            for j, (nid, ninfo) in revenumerate(layer):

                if not ninfo.get('ghost'):
                    break

                self._scoochXParents(nid, ninfo, SCOOCH_RIGHT)

        # Finally, we calculate the drawing for the edge lines
        self._calcEdgeLines()

    def _scoochXParents(self, nid, ninfo, lr=None):

        weight = ninfo['weight']

        for eid, n1, n2, einfo in self.graph.getRefsToByNid(nid):

            pinfo = self.graph.getNodeProps(n1)

            # Only do ghost nodes (for now...)
            if not pinfo.get('ghost'):
                continue

            # Only do this to parents in the layer above us...
            if pinfo['weight'] != weight-1:
                continue

            self._scoochXAlign(ninfo, pinfo, lr=lr)

    def _scoochXKids(self, nid, ninfo, lr=None):

        weight = ninfo['weight']

        for eid, n1, n2, einfo in self.graph.getRefsFromByNid(nid):

            kinfo = self.graph.getNodeProps(n2)

            # Only do ghost nodes (for now...)
            if not kinfo.get('ghost'):
                continue

            # Only do this to kids in the layer beneath us...
            if kinfo['weight'] != weight+1:
                continue

            self._scoochXAlign(ninfo, kinfo, lr=lr)

    def _scoochXAlign(self, ninfo, kinfo, lr=None):
        '''
        If possible, move the "kidinfo" node toward ninfo
        along the X axis...  If "lr" is specified, only move
        the "kidnode" (which may be "above" you...) if it is
        moving either SCOOCH_LEFT or SCOOCH_RIGHT as specified.
        '''
        xpos, ypos = ninfo['position']
        xsize, ysize = ninfo.get('size', zero_zero)
        xmid = xpos + ( xsize / 2 )

        kxpos, kypos = kinfo['position']
        kxsize, kysize = kinfo.get('size', zero_zero)
        kxmid = kxpos + ( kxsize / 2 )

        xdelta = xmid - kxmid

        # If they only want us to go left, and the delta
        # is right, bail...
        if lr == SCOOCH_LEFT and xdelta >= 0:
            return

        # If they only want us to go right, and the delta
        # is left, bail...
        if lr == SCOOCH_RIGHT and xdelta <= 0:
            return

        self._scoochX(kinfo, xdelta)

    def _scoochX(self, ninfo, xdelta):

        layerpos = ninfo.get('layerpos')
        x, y = ninfo['position']
        xsize, ysize = ninfo.get('size', zero_zero)
        layer = self.layers[ninfo['weight']]
        layermax = len(layer) - 1

        # There's always room on the left if we're the first...
        if layerpos == 0 and xdelta < 0:
            ninfo['position'] = (x+xdelta, y)
            return

        # Always room on the right if we're last!
        if layerpos == layermax and xdelta > 0:
            ninfo['position'] = (x+xdelta, y)
            return

        # Sigh... now we have to get fancy...

        # If they're asking us to go left, find out about our
        # left sibling
        if xdelta < 0:
            snid, sinfo = layer[layerpos - 1]
            sx, sy = sinfo['position']
            sxsize, sysize = sinfo.get('size', zero_zero)

            sright = (sx + sxsize) + self.width_pad

            #leftroom = sright - x
            # "greater" is less movement here...
            xdelta = max(xdelta, sright - x)
            ninfo['position'] = (x+xdelta, y)
            return

        # If they're asking us to go right, find out about our
        # right sibling
        if xdelta > 0:
            snid, sinfo = layer[layerpos + 1]
            sx, sy = sinfo['position']
            sxsize, sysize = sinfo.get('size', zero_zero)

            myright = x + xsize + self.width_pad

            xdelta = min(xdelta, sx-myright)
            ninfo['position'] = (x+xdelta, y)
            return

    def _calcEdgeLines(self):

        h_hpad = self.width_pad / 2
        h_vpad = self.height_pad / 2

        for eid, n1, n2, einfo in self.graph.getEdges():

            pre_lines = []
            post_lines = []

            pinfo = self.graph.getNodeProps(n1)
            kinfo = self.graph.getNodeProps(n2)

            pwidth, pheight = pinfo.get('size', (0,0))
            pweight = pinfo.get('weight')
            lheight = self.lheights[pweight]
            voffset = lheight - pheight

            if einfo.get('looptop'):

                x1, y1 = vg_layout.entry_pos(pinfo)
                x2, y2 = vg_layout.entry_pos(kinfo)

                xhalf = (x1 - x2) / 2

                b = [ (x1, y1),
                      (x1, y1 - h_vpad),
                      (x2, y2 - h_vpad),
                      (x2, y2),
                    ]

            elif einfo.get('loopbot'):

                x1, y1 = vg_layout.exit_pos(pinfo)
                x2, y2 = vg_layout.exit_pos(kinfo)

                kwidth, kheight = kinfo.get('size', (0,0))
                kweight = kinfo.get('weight')
                klheight = self.lheights[kweight]

                kvoffset = klheight - kheight

                pre_lines = [(x1, y1), (x1, y1 + voffset)]
                post_lines = [(x2, y2), (x2, y2 + kvoffset)]

                b = [ (x1, y1 + voffset),
                      (x1, y1 + voffset + h_vpad),
                      (x2, y2 + kvoffset + h_vpad),
                      (x2, y2 + kvoffset),
                    ]

            else:

                x1, y1 = vg_layout.exit_pos(pinfo)
                x2, y2 = vg_layout.entry_pos(kinfo)

                pre_lines = [(x1,y1), (x1, y1 + voffset)]

                b = [ (x1, y1 + voffset),
                      (x1, y1 + voffset + h_vpad),
                      (x2, y2 - h_vpad),
                      (x2, y2),
                    ]

            bez_lines = vg_bezier.calculate_bezier(b, 20)

            einfo['edge_points'] = pre_lines + bez_lines + post_lines
            #einfo['edge_points'] = bez_lines

