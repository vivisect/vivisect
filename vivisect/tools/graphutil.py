
'''
Some glue code to do workspace related things based on visgraph
'''
import time
import envi
import logging
import vivisect
import collections
import visgraph.pathcore as vg_pathcore
import visgraph.graphcore as vg_graphcore

xrskip = envi.BR_PROC | envi.BR_DEREF

logger = logging.getLogger(__name__)


def getNodeWeightHisto(g):
    '''
    Takes a graph and returns the following tuple:
        (weights_to_node, nodes_to_weight, leaves)

    where:
        weights_to_node - dict using weight as key
        nodes_to_weight - dict using nodes as key
        leaves          - dict of nodes without refs from
    '''
    nodeweights = g.getHierNodeWeights()
    leaves = collections.defaultdict(list)
    weights_to_cb = collections.defaultdict(list)

    # create default dict
    for cb, weight in sorted(nodeweights.items(), key=lambda x: x[1]):
        if not len(g.getRefsFromByNid(cb)):
            # leaves is a tuple of (cb, current path, visited nodes)
            # these are our leaf nodes
            leaves[weight].append((cb, list(), set()))

        # create histogram
        weights_to_cb[weight].append((cb, list(), set()))

    return weights_to_cb, nodeweights, leaves

def getLongPath(g):
    '''
    Yield a list of list tuples (node id, edge id) representing the longest path
    '''

    weights_to_cb, cb_to_weights, todo = getNodeWeightHisto(g)

    # unique root node code blocks
    rootnodes = set([cb for cb, nprops in g.getHierRootNodes()])
    leafmax = 0
    if len(todo):
        leafmax = max(todo.keys())

    invalidret = False
    # if the weight of the longest path to a leaf node
    # is not the highest weight then we need to fix our
    # path choices by taking the longer path
    weightmax = max(weights_to_cb.keys())
    if leafmax != weightmax:
        todo = weights_to_cb
        leafmax = weightmax
        invalidret = True

    # this is our loop that we want to yield out of..
    # start at the bottom of the graph and work our way back up
    for weight in range(leafmax, -1, -1):
        # the todo is a a list of codeblocks a specific level
        codeblocks = todo.get(weight)
        if not codeblocks:
            continue

        for cbva, paths, visited in codeblocks:
            tleafs = collections.defaultdict(list)
            if not paths:
                paths = [(cbva, None)]
            # work is a tuple of (cbva, weight, current path, visited)
            work = [(cbva, weight, paths, visited)]
            while work:
                cbva, weight, cpath, visited = work.pop()
                upweight = weight - 1
                for eid, fromid, toid, einfo in g.getRefsToByNid(cbva):
                    if fromid in visited:
                        continue
                    nweight = cb_to_weights.get(fromid)
                    newcpath = list(cpath)
                    newcpath[-1] = (cbva, eid)
                    newcpath.append((fromid, None))
                    newvisited = set(visited)
                    newvisited.add(fromid)
                    if nweight == upweight:
                        # we've moved back one level
                        work.append((fromid, upweight, newcpath, newvisited))
                    else:
                        t = (fromid, newcpath, newvisited)
                        if t not in tleafs[nweight]:
                            tleafs[nweight].append(t)
                if cbva in rootnodes:
                    l = list(cpath)
                    l.reverse()
                    yield l

            # update our todo with our new paths to resume from
            for nw, l in tleafs.items():
                todo[nw] += l

def _nodeedge(tnode):
    nid = vg_pathcore.getNodeProp(tnode, 'nid')
    eid = vg_pathcore.getNodeProp(tnode, 'eid')
    return nid,eid

def _nodeedgeloop(tnode):
    nid = vg_pathcore.getNodeProp(tnode, 'nid')
    eid = vg_pathcore.getNodeProp(tnode, 'eid')
    loop = vg_pathcore.getNodeProp(tnode, 'loops')
    return nid,eid,loop

def getCoveragePaths(fgraph, maxpath=None):
    '''
    Get a set of paths which will cover every block, but will
    *end* on branches which re-merge with previously traversed
    paths.  This allows a full coverage of the graph with as
    little work as possible, but *will* omit possible states.

    Returns: yield based path generator ( where path is list if (nid,edge) tuples )
    '''
    pathcnt = 0
    nodedone = {}

    for root in fgraph.getHierRootNodes():

        proot = vg_pathcore.newPathNode(nid=root[0], eid=None)
        todo = [(root,proot), ]

        while todo:

            node,cpath = todo.pop()
            refsfrom = fgraph.getRefsFrom(node)

            # Record that we have visited this node...
            nodedone[node[0]] = True

            # This is a leaf node!
            if not refsfrom:
                path = vg_pathcore.getPathToNode(cpath)
                yield [ _nodeedge(n) for n in path ]

                pathcnt += 1
                if maxpath is not None and pathcnt >= maxpath:
                    return

            for eid, fromid, toid, einfo in refsfrom:

                # If we're branching to a visited node, return the path as is
                if nodedone.get(toid):
                    path = vg_pathcore.getPathToNode(cpath)
                    yield [ _nodeedge(n) for n in path ]

                    # Check if that was the last path we should yield
                    pathcnt += 1
                    if maxpath is not None and pathcnt >= maxpath:
                        return

                    # If we're at a completed node, take no further branches
                    continue

                npath = vg_pathcore.newPathNode(parent=cpath, nid=toid, eid=eid)
                tonode = fgraph.getNode(toid)
                todo.append((tonode,npath))

def getCodePathsThru(fgraph, tgtcbva, loopcnt=0, maxpath=None):
    '''
    Yields all the paths through the hierarchical graph which pass through
    the target codeblock "tgtcb".  Each "root" node is traced to the target,
    and all paths are traversed from there to the end.  Specify a loopcnt
    to allow loop paths to be generated with the given "loop iteration count"

    Example:
        for path in getCodePathsThru(fgraph, tgtcb):
            for node,edge in path:
                ...etc...
    '''
    cnt = 0
    for pathto in getCodePathsTo(fgraph, tgtcbva, loopcnt=loopcnt, maxpath=maxpath):
        for pathfrom in getCodePathsFrom(fgraph, tgtcbva, loopcnt=loopcnt, maxpath=maxpath):
            yield pathto + pathfrom[1:]
            cnt += 1
            if maxpath is not None and cnt >= maxpath:
                return

def getCodePathsTo(fgraph, tocbva, loopcnt=0, maxpath=None):
    '''
    Yields all the paths through the hierarchical graph starting at the
    "root nodes" and ending at tocbva.  Specify a loopcnt to allow loop
    paths to be generated with the given "loop iteration count"

    Example:
        for path in getCodePathsTo(fgraph, tocbva):
            for node,edge in path:
                ...etc...
    '''
    pathcnt = 0
    looptrack = []
    pnode = vg_pathcore.newPathNode(nid=tocbva, eid=None)

    node = fgraph.getNode(tocbva)
    todo = [(node,pnode), ]

    while todo:

        node,cpath = todo.pop()

        refsto = fgraph.getRefsTo(node)

        # Is this is the root node?
        if node[1].get('rootnode'):
            path = vg_pathcore.getPathToNode(cpath)
            path.reverse()
            yield [ _nodeedge(n) for n in path ]
            vg_pathcore.trimPath(cpath)

            pathcnt += 1
            if maxpath and pathcnt >= maxpath:
                return

        for eid, n1, n2, einfo in refsto:
            # Skip loops if they are "deeper" than we are allowed
            loops = vg_pathcore.getPathLoopCount(cpath, 'nid', n1)
            if loops > loopcnt:
                continue

            vg_pathcore.setNodeProp(cpath, 'eid', eid)
            npath = vg_pathcore.newPathNode(parent=cpath, nid=n1, eid=None)
            nid1,node1 = fgraph.getNode(n1)
            todo.append(((nid1,node1),npath))

def getCodePathsFrom(fgraph, fromcbva, loopcnt=0, maxpath=None):
    '''
    Yields all the paths through the hierarchical graph beginning with 
    "fromcbva", which is traced to all terminating points.  Specify a loopcnt
    to allow loop paths to be generated with the given "loop iteration count"

    Example:
        for path in getCodePathsFrom(fgraph, fromcbva):
            for node,edge in path:
                ...etc...
    '''
    pathcnt = 0
    proot = vg_pathcore.newPathNode(nid=fromcbva, eid=None)

    cbnid,cbnode = fgraph.getNode(fromcbva)
    todo = [(cbnid,proot), ]

    while todo:

        nid,cpath = todo.pop()

        refsfrom = fgraph.getRefsFromByNid(nid)

        # This is a leaf node!
        if not refsfrom:
            path = vg_pathcore.getPathToNode(cpath)
            yield [ _nodeedge(n) for n in path ]
            vg_pathcore.trimPath(cpath)

            pathcnt += 1
            if maxpath and pathcnt >= maxpath:
                return

        for eid, fromid, n2, einfo in refsfrom:
            # Skip loops if they are "deeper" than we are allowed
            loops = vg_pathcore.getPathLoopCount(cpath, 'nid', n2)
            if loops > loopcnt:
                continue

            npath = vg_pathcore.newPathNode(parent=cpath, nid=n2, eid=eid)
            todo.append((n2,npath))

def getCodePaths(fgraph, loopcnt=0, maxpath=None):
    '''
    Yields all the paths through the hierarchical graph.  Each
    "root" node is traced to all terminating points.  Specify a loopcnt
    to allow loop paths to be generated with the given "loop iteration count"

    Example:
        for path in getCodePaths(fgraph):
            for node,edge in path:
                ...etc...
    '''
    pathcnt = 0
    for root in fgraph.getHierRootNodes():
        proot = vg_pathcore.newPathNode(nid=root[0], eid=None)
        todo = [(root,proot), ]

        while todo:

            node,cpath = todo.pop()

            refsfrom = fgraph.getRefsFrom(node)

            # This is a leaf node!
            if not refsfrom:
                path = vg_pathcore.getPathToNode(cpath)
                yield [ _nodeedge(n) for n in path ]
                vg_pathcore.trimPath(cpath)

                pathcnt += 1
                if maxpath and pathcnt >= maxpath:
                    return

            for eid, fromid, toid, einfo in refsfrom:
                # Skip loops if they are "deeper" than we are allowed
                if vg_pathcore.getPathLoopCount(cpath, 'nid', toid) > loopcnt:
                    continue

                npath = vg_pathcore.newPathNode(parent=cpath, nid=toid, eid=eid)
                tonode = fgraph.getNode(toid)
                todo.append((tonode,npath))

def walkCodePaths(fgraph, callback, loopcnt=0, maxpath=None):
    '''
    walkCodePaths is a path generator which uses a callback function to determine the 
    viability of each particular path.  This approach allows the calling function 
    (eg. walkSymbolikPaths) to do in-generator checks/processing and trim paths which
    are simply not possible/desireable.

    Callbacks will receive the current path, the current edge, and the new path node.
    For root nodes, the current path and edge will be None types.  
    '''
    pathcnt = 0
    routed = fgraph.getMeta('Routed', False)
    for root in fgraph.getHierRootNodes():
        proot = vg_pathcore.newPathNode(nid=root[0], eid=None)

        # Fire callback once to init the dest "path node"
        callback(None, None, proot)

        todo = [(root,proot), ]

        while todo:

            node,cpath = todo.pop()
            refsfrom = fgraph.getRefsFrom(node)

            # This is a leaf node!
            if not refsfrom:
                #path = vg_pathcore.getPathToNode(cpath)
                #yield [ _nodeedge(n) for n in path ]

                # let the callback know we've reached one...
                #if callback(cpath, None, None):
                yield cpath

                vg_pathcore.trimPath(cpath)

                pathcnt += 1
                if maxpath and pathcnt >= maxpath:
                    return

            for eid, fromid, toid, einfo in refsfrom:
                # skip edges which are not marked "follow"
                if routed and not einfo.get('follow', False):
                    continue
                # Skip loops if they are "deeper" than we are allowed
                if vg_pathcore.getPathLoopCount(cpath, 'nid', toid) > loopcnt:
                    continue

                edge = (eid,fromid,toid,einfo)

                npath = vg_pathcore.newPathNode(parent=cpath, nid=toid, eid=eid)

                if not callback(cpath, edge, npath):
                    vg_pathcore.trimPath(npath)
                    continue

                todo.append((fgraph.getNode(toid),npath))

def getLoopPaths(fgraph):
    '''
    Similar to getCodePaths(), however, getLoopPaths() will return path lists
    which loop.  The last element in the (node,edge) list will be the first
    "looped" block.
    '''
    for root in fgraph.getHierRootNodes():
        proot = vg_pathcore.newPathNode(nid=root[0], eid=None)
        todo = [ (root[0],proot,0), ]

        while todo:
            node,cpath,loopcnt = todo.pop()

            count = 0
            free = []
            if loopcnt == 1:
                yield [ _nodeedge(n) for n in vg_pathcore.getPathToNode(npath) ]

            else:
                for eid, fromid, toid, einfo in fgraph.getRefsFromByNid(node):

                    loopcnt = vg_pathcore.getPathLoopCount(cpath, 'nid', toid)
                    if loopcnt > 1:
                        continue

                    count += 1
                    npath = vg_pathcore.newPathNode(parent=cpath, nid=toid, eid=eid)
                    todo.append((toid,npath,loopcnt))

            if not count:
                vg_pathcore.trimPath(cpath)

def getOpsFromPath(vw, fgraph, path):
    '''
    Retrieve the opcodes for a given path.

    '''
    # FIXME cache opcodes in function graph for replay speed
    ret = []
    for nid,eid in path:
        node = fgraph.getNode(nid)
        cbva = node[1].get('cbva')
        cbmax = cbva + node[1].get('cbsize')
        while cbva < cbmax:
            op = vw.parseOpcode(cbva)
            ret.append(op)
            cbva += op.size
    return ret

def buildFunctionGraph(vw, fva, revloop=False, g=None):
    '''
    Build a visgraph HierGraph for the specified function.
    '''

    if g is None:
        g = vg_graphcore.HierGraph()
        g.setMeta('fva', fva)

    colors = vw.getFunctionMeta(fva, 'BlockColors', default={})
    fcb = vw.getCodeBlock(fva)
    if fcb is None:
        t = (fva, vw.isFunction(fva))
        raise Exception('Invalid initial code block for 0x%.8x isfunc: %s' % t)

    todo = [ (fcb, []), ]

    fcbva, fcbsize, fcbfunc = fcb

    # Add the root node...
    bcolor = colors.get(fva, '#0f0')
    g.addNode(nid=fva, rootnode=True, cbva=fva, cbsize=fcbsize, color=bcolor)

    while todo:

        (cbva, cbsize, cbfunc), path = todo.pop()

        path.append(cbva)

        # If the code block va doesn't have a node yet, make one
        if not g.hasNode(cbva):
            bcolor = colors.get(cbva, '#0f0')
            g.addNode(nid=cbva, cbva=cbva, cbsize=cbsize, color=bcolor)

        # Grab the location for the last instruction in the block
        nextva = cbva + cbsize - 1
        loc = vw.getLocation(nextva)
        if loc is None:
            raise Exception("buildFunctionGraph: Attempt to get location at 0x%x" % nextva)

        lva, lsize, ltype, linfo = loc

        for xrfrom, xrto, xrtype, xrflags in vw.getXrefsFrom(lva, vivisect.REF_CODE):

            # For now, the graph doesn't cross function boundaries
            # or indirects.
            if xrflags & xrskip:
                continue

            if not g.hasNode(xrto):
                cblock = vw.getCodeBlock(xrto)
                if cblock is None:
                    logger.warning('CB is None in graph building?!?! (0x%x)', xrto)
                    logger.warning('(fva: 0x%.8x cbva: 0x%.8x)', fva, xrto)
                    continue

                tova, tosize, tofunc = cblock
                if tova != xrto:
                    logger.warning('CBVA != XREFTO in graph building!?')
                    logger.warning('(cbva: 0x%.8x xrto: 0x%.8x)', tova, xrto)
                    continue

                # Since we haven't seen this node, lets add it to todo
                # and build a new node for it.
                todo.append(((tova,tosize,tofunc), list(path)))
                bcolor = colors.get(tova, '#0f0')
                g.addNode(nid=tova, cbva=tova, cbsize=tosize, color=bcolor)

            # If they want it, reverse "loop" edges (graph layout...)
            if revloop and xrto in path:
                g.addEdgeByNids(xrto, cbva, reverse=True)
            else:
                g.addEdgeByNids(cbva, xrto)

        if ltype == vivisect.LOC_OP and linfo & envi.IF_NOFALL:
            continue

        # If this codeblock can fall through into another, add it to
        # todo!
        fallva = lva + lsize
        if not g.hasNode(fallva):
            fallblock = vw.getCodeBlock(fallva)
            if fallblock is None:
                logger.warning('FB is None in graph building!??!')
                logger.warning('(fva: 0x%.8x  fallva: 0x%.8x', fva, fallva)
            elif fallva != fallblock[0]:
                logger.warning('FALLVA != CBVA in graph building!??!')
                logger.warning('(fallva: 0x%.8x CBVA: 0x%.8x', fallva, fallblock[0])
            else:
                fbva, fbsize, fbfunc = fallblock
                #if fbfunc != fva and fbva not in blocks:
                #    continue

                todo.append( ((fbva,fbsize,fbfunc), list(path)) )
                bcolor = colors.get(fallva, '#0f0')
                g.addNode(nid=fallva, cbva=fallva, cbsize=fbsize, color=bcolor)

        # If we ended up with a destination node, make the edge
        if g.hasNode(fallva):
            # If they want it, reverse "loop" edges (graph layout...)
            if revloop and fallva in path:
                g.addEdgeByNids(fallva, cbva, reverse=True)
            else:
                g.addEdgeByNids(cbva, fallva)

    return g

def getGraphNodeByVa(fgraph, va):
    '''
    Returns graph node a given VA falls within.
    Similar to VivWorkspace.getCodeBlock(va).

    Because this involves the concept of CodeBlocks, it does not fit in the
    GraphCore.

    DEPRECATED as soon as visi's new CodeGraph gains this functionality inherently
    '''
    for nva, ninfo in fgraph.nodes.values():
        nvamax = ninfo.get('cbsize')
        if nvamax is None: 
            raise Exception('getGraphNodeByVa() called on graph with non-codeblock nodes')

        nvamax += nva
        if va >= nva and va < nvamax:
            return nva
    return None

def findRemergeDown(graph, va):
    '''
    starting at a given va, figure out the nodes connecting va to the next place something remerges
    '''
    startnid = getGraphNodeByVa(graph, va)

    # paint down graph, 
    preRouteGraphDown(graph, startnid, mark='hit', loop=False)

    histo, nodewts, leaves = getNodeWeightHisto(graph)
    startnode = graph.getNode(startnid)
    startweight = nodewts.get(startnid)

    for node in graph.getNodesByProp('hit'):
        # skip the starting node
        if node[0] == startnid: 
            continue

        if node[1].get('hit') is None: 
            continue

        for eid, frva, tova, einfo in graph.getRefsTo(node):
            frnode = graph.getNode(frva)
            if frnode[1].get('hit') is None:
                # clear from here down
                clearMarkDown(graph, tova, mark='hit')
                break

# path routing through a graph.  reduces aimless wandering when we know where we want to be
def preRouteGraph(graph, fromva, tova, clearFirst=True):
    '''
    Package it all together
    '''
    if clearFirst:
        clearRouting(graph)

    preRouteGraphUp(graph, tova)
    preRouteGraphDown(graph, fromva)
    preRouteGraphEdges(graph)

def preRouteGraphEdges(graph):
    '''
    Mark edges as 'follow' if from-node is marked 'up' and to-node id marked 'down'
    Note: unlike the other preRoute functions, this is not flexible on naming.
    '''
    for edge in graph.getEdges():
        eid, frnid, tonid, einfo = edge
        if not graph.getNodeProps(frnid).get('up'):
            continue
        if not graph.getNodeProps(tonid).get('down'):
            continue

        graph.setEdgeProp(edge, 'follow', True)

def preRouteGraphUp(graph, tova, loop=True, mark='down'):
    '''
    paint a route from our destination, 'up' the graph
    '''
    graph.setMeta('Routed', True)
    tonid = getGraphNodeByVa(graph, tova)
    if tonid is None:
        raise Exception("tova not in graph 0x%x" % tova)

    tonode = graph.getNode(tonid)
    nwlist = graph.getHierNodeWeights()
    todo = [ (tonode) ]
    while todo:
        curnode = todo.pop()
        graph.setNodeProp(curnode, mark, True)
        for eid, fr, to, einfo in graph.getRefsTo(curnode):
            if graph.getNodeProps(fr).get(mark) == True:
                continue
            if not loop and nwlist.get(fr) <= nwlist.get(to):
                continue
            frnode = graph.getNode(fr)
            todo.append(frnode)
   
def preRouteGraphDown(graph, fromva, loop=False, mark='up'):
    '''
    paint a route from our starting point, 'down' the graph
    '''
    graph.setMeta('Routed', True)
    fromnode = getGraphNodeByVa(graph, fromva)
    if fromnode is None:
        raise Exception("fromva not in graph 0x%x" % fromva)

    nwlist = graph.getHierNodeWeights()
    todo = [ graph.getNode(fromnode) ]
    while todo:
        curnode = todo.pop()
        curnodeva, curninfo = curnode
        graph.setNodeProp(curnode, mark, True)
        for eid, fr, to, einfo in graph.getRefsFrom(curnode):
            if graph.getNodeProps(to).get(mark) == True:
                continue
            if not loop and nwlist.get(fr) >= nwlist.get(to):
                continue

            todo.append(graph.getNode(to))

def clearMarkDown(graph, fromva, loop=False, mark='up'):
    '''
    clear a route from our starting point, 'down' the graph.
    ie. remove the mark
    '''
    fromnode = getGraphNodeByVa(graph, fromva)
    if fromnode is None:
        raise Exception("fromva not in graph 0x%x" % fromva)

    nwlist = graph.getHierNodeWeights()
    todo = [ graph.getNode(fromnode) ]
    while len(todo):
        curnode = todo.pop()
        curnodeva, curninfo = curnode

        # actually delete the node property, not just remove value
        graph.delNodeProp(curnode, mark)

        for eid, fr, to, einfo in graph.getRefsFrom(curnode):
            if graph.getNodeProps(to).get(mark) == True:
                continue
            if not loop and nwlist.get(fr) >= nwlist.get(to):
                continue

            todo.append(graph.getNode(to))

def clearRouting(graph, nmarks=('up','down'), emarks=('follow',)):
    graph.delNodesProps(nmarks)
    graph.delEdgesProps(emarks)
    graph.setMeta('Routed', False)

def reduceGraph(graph, props=('up','down')):
    '''
    trims all nodes that don't have all the props in the props list
    '''
    for node in graph.getNodes():
        for prop in props:
            if node[1].get(prop) is None:
                graph.delNode(node)
                break


# TODO: Move into base exception file
class PathForceQuitException(Exception):
    def __repr__(self):
        return "Path Generator forced to stop seeking a new path.  Possibly Timeout."

'''
eventually, routing will include the ability to 'source-route', picking N specific points a path must go through
'''
class PathGenerator:
    '''
    PathGenerator provides routed paths using yield generators, with some external 
    control.  Because these generators are typically layered with other API's 
    (ie. Symboliks subsystem calls) on top, PathGenerator provides a timeout and 
    some external control.

    PathGenerator should be used one per thread, not shared between threads.  The stop() 
    method is good for use by a single management thread.
    '''

    def __init__(self, graph):
        self.graph = graph
        self.__go__ = False

    def stop(self):
        '''
        stops path generation.
        '''
        self.__go__ = False

    def getFuncCbRoutedPaths_genback(self, fromva, tova, loopcnt=0, maxpath=None, timeout=None):
        '''
        Yields all the paths through the hierarchical graph starting at the 
        "root nodes" and ending at tocbva.  Specify a loopcnt to allow loop 
        paths to be generated with the given "loop iteration count"

        Example:
            for path in getCodePathsTo(fgraph, tocbva):
                for node,edge in path:
                    ...etc...
        '''
        fgraph = self.graph
        self.__update = 0
        self.__go__ = True
        pathcnt = 0
        tocbva = getGraphNodeByVa(fgraph, tova)
        frcbva = getGraphNodeByVa(fgraph, fromva)

        preRouteGraph(fgraph, fromva, tova)
        
        pnode = vg_pathcore.newPathNode(nid=tocbva, eid=None)

        todo = [(tocbva,pnode), ]

        maxtime = None
        if timeout:
            maxtime = time.time() + timeout

        while todo:
            if maxtime and time.time() > maxtime:
                raise PathForceQuitException()

            if not self.__go__:
                raise PathForceQuitException()

            nodeid,cpath = todo.pop()

            refsto = fgraph.getRefsTo((nodeid, None))

            # This is the root node!
            if nodeid == frcbva:
                path = vg_pathcore.getPathToNode(cpath)
                path.reverse()
                self.__steplock.acquire()
                yield [ viv_graph._nodeedge(n) for n in path ]
                vg_pathcore.trimPath(cpath)

                pathcnt += 1
                self.__update = 1
                self.__steplock.release()
                if maxpath and pathcnt >= maxpath:
                    return

            for eid, fromid, toid, einfo in refsto:
                if fgraph.getNodeProps(fromid).get('up') != True:
                    # TODO: drop the bad edges from graph in preprocessing? instead of "if" here
                    vg_pathcore.trimPath(cpath)
                    continue

                # Skip loops if they are "deeper" than we are allowed
                loops = vg_pathcore.getPathLoopCount(cpath, 'nid', fromid)
                if loops > loopcnt:
                    continue

                vg_pathcore.setNodeProp(cpath, 'eid', eid)
                npath = vg_pathcore.newPathNode(parent=cpath, nid=fromid, eid=None)
                todo.append((fromid,npath))

        self.__go__ = False

    def getFuncCbRoutedPaths(self, fromva, tova, loopcnt=0, maxpath=None, timeout=None):
        '''
        Yields all the paths through the hierarchical graph starting at the 
        "root nodes" and ending at tocbva.  Specify a loopcnt to allow loop 
        paths to be generated with the given "loop iteration count"

        Example:
            for path in getCodePathsTo(fgraph, tocbva):
                for node,edge in path:
                    ...etc...
        '''
        fgraph = self.graph
        self.__update = 0
        self.__go__ = True
        pathcnt = 0
        tocbva = getGraphNodeByVa(fgraph, tova)
        frcbva = getGraphNodeByVa(fgraph, fromva)

        preRouteGraph(fgraph, fromva, tova)
        
        pnode = vg_pathcore.newPathNode(nid=frcbva, eid=None)

        todo = [(frcbva,pnode), ]

        maxtime = None
        if timeout:
            maxtime = time.time() + timeout

        while todo:
            if maxtime and time.time() > maxtime:
                raise PathForceQuitException()

            if not self.__go__:
                raise PathForceQuitException()

            nodeid,cpath = todo.pop()

            refsfrom = fgraph.getRefsFrom((nodeid, None))

            # This is the root node!
            if nodeid == tocbva:
                path = vg_pathcore.getPathToNode(cpath)
                yield [ _nodeedge(n) for n in path ]
                vg_pathcore.trimPath(cpath)

                pathcnt += 1
                self.__update = 1
                if maxpath and pathcnt >= maxpath:
                    return

            for eid, fromid, toid, einfo in refsfrom:
                if fgraph.getNodeProps(fromid).get('down') != True:
                    #sys.stderr.write('.')
                    # TODO: drop the bad edges from graph in preprocessing? instead of "if" here
                    continue

                # Skip loops if they are "deeper" than we are allowed
                loops = vg_pathcore.getPathLoopCount(cpath, 'nid', fromid)
                if loops > loopcnt:
                    vg_pathcore.trimPath(cpath)
                    #sys.stderr.write('o')

                    # as long as we have at least one path, we count loops as paths, lest we die.
                    if pathcnt: 
                        pathcnt += 1
                    continue

                npath = vg_pathcore.newPathNode(parent=cpath, nid=toid, eid=eid)
                todo.append((toid,npath))

            vg_pathcore.trimPath(cpath)

        self.__go__ = False
