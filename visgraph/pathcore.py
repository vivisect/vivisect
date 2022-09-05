'''
Paths are enumerated threads through a particular graph.  They
are implemented as an optimized hierarchical graph using python
primitives to save memory and processing time...

Each "leaf" node may be tracked back for it's entire path by
tracking back to parents.
'''

def newPathNode(parent=None, **kwargs):
    '''
    Create a new path node with the given properties
    '''
    ret = (parent, [], kwargs)
    if parent is not None:
        parent[1].append(ret)
    return ret

def getNodeParent(pnode):
    return pnode[0]

def delPathNode(pnode):
    '''
    Prune (remove) this node from the parent...
    '''
    p = getNodeParent(pnode)
    if p is not None:
        p[1].remove(pnode)

def getNodeIndex(pnode):
    p = getNodeParent(pnode)
    if p is not None:
        return p[1].index(pnode)
    return None

def getNodeKids(pnode):
    '''
    Return the list of children nodes for the specified
    node.

    Example: for knode in getNodeKids(pnode):
    '''
    return pnode[1]

def getRootNode(pnode):
    '''
    Get the root node for the path tree which contains
    pnode.

    Example: root = getRootNode(branchnode)
    '''
    ret = pnode
    while pnode[0] is not None:
        pnode = pnode[0]
    return pnode

def getLeafNodes(pnode):
    '''
    Get all the leaf nodes for the path tree which contains
    the pnode.

    Example: for leaf in getLeafNodes(root):
    '''
    root = getRootNode(pnode)
    ret = []
    todo = [root, ]
    while len(todo):
        x = todo.pop()
        if len(x[1]) == 0:
            ret.append(x)
            continue
        for n in x[1]:
            todo.append(n)
    return ret

def getPathToNode(pnode):
    '''
    Return a list of the path nodes which lead from the
    root node to the specified path node.
    '''
    path = []
    while pnode is not None:
        path.append(pnode)
        pnode = pnode[0]

    path.reverse()
    return path

def getAllPaths(pnode):
    '''
    Get a list of lists which has each path flattened out.

    Example: for path in getAllPaths(pnode):
                 for node in path:
                    doStuff()
    '''
    leafs = getLeafNodes(pnode)
    paths = []
    for leaf in leafs:
        path = getPathToNode(leaf)
        paths.append(path)
    return paths

def getNodeProp(pnode, key, default=None):
    '''
    Get a property from the given node, returning
    default in the case that the specified property is
    not present.

    Example:
        name = getNodeProp(pnode, 'name', 'Unknown')
    '''
    return pnode[2].get(key, default)

def getPathProp(pnode, key, default=None):
    '''
    Retrieve the specified property by walking the give
    path backward until the property is found.  Returns
    the specified default if the specified key is not found
    as a property of any node in the given path.

    Example:
        name = getPathProp(pnode, 'name', 'Unknown')
    '''
    parent = pnode
    while parent is not None:
        parent, kids, props = parent
        x = props.get(key)
        if x is not None:
            return x
    return default

def setNodeProp(pnode, key, value):
    '''
    Set a spcified property on the given path node.

    Example:
        setNodeProp(pnode, 'name', 'woot')
    '''
    pnode[2][key] = value

def isPathLoop(pnode, key, value):
    '''
    Assuming you have some identifier property (such as graph node id)
    being set on the path nodes, you may use this API to determine if
    the current path has a node with the specified key/value property.

    Example:
        if searchPathLoop(pnode, 'nid', 5):
            continue
    '''
    parent = pnode
    while parent is not None:
        parent, kids, props = parent
        if props.get(key) == value:
            return True
    return False

def getPathLoopCount(pnode, key, value):
    '''
    Assuming that the key is unique, walk the current path and see how
    many times "key" has the specified value.  This will be how many instances
    of a loop have been encountered.
    '''
    count = 0
    parent = pnode
    while parent is not None:
        parent, kids, props = parent
        if props.get(key) == value:
            count += 1
    return count


def trimPath(pnode):
    '''
    Doing analysis on a path tree can be very memory consuming.  If an analysis tool is
    powering through bajillions of nodes, the tree can consume all RAM.  However,
    the analysis may be doable with some selective trimming of the path tree.
    Only trim when you are done with a path node, and make sure your algorithm uses
    newPathNode on all "children" before traversing into one of them.

    trimPath() will remove pnode from it's parent node, then check if the parent node
    has any other children nodes, and recursively remove path links to all unnecessary
    path nodes leading up to pnode.

    caveat: if you are not calling newPathNode (which adds a reference from it's parent)
    on all child nodes before traversing into any of them, it is possible that the
    current node could be trimmed because it looks like it doesn't have any children.
    '''
    while True:
        p = getNodeParent(pnode)

        # if we don't have a parent, we're done
        if p is None:
            break

        # remove our burden from our parent
        if pnode in p[1]:
            p[1].remove(pnode)

        # if our parent still has kids living at home, we're done
        if len(p[1]):
            break

        # time to kill our parent
        pnode = p


def reprPath(node, startFromRoot=True):
    r = ''

    if startFromRoot:
        node = getRootNode(node)

    snid = getNodeProp(node, 'nid')
    todo = [(snid, node, 1)]
    r += hex(snid)
    r += '\n'

    while len(todo):
        nid, pnode, indent = todo.pop()

        for tpnode in pnode[1]:
            tnid = getNodeProp(tpnode, 'nid')
            outstr = "   |"*indent + "--" + hex(tnid)
            if tnid == snid:
                outstr += "  <<<<-- our node!"
            r += outstr
            r += '\n'

            todo.append((tnid, tpnode, indent + 1))

    return r
