'''
Various codeflow oriented graph constructs.
'''
import envi
import visgraph.graphcore as v_graphcore

from vivisect.const import *

class CallGraph(v_graphcore.HierGraph):
    '''
    A graph which represents procedural branches.
    '''
    def __init__(self):
        v_graphcore.Graph.__init__(self)

    def getFunctionNode(self, va):
        node = self.getNode(va)
        if node is None:
            node = self.addNode(nid=va)
        return node

    def getCallEdge(self, f1va, f2va):
        f1 = self.getFunctionNode(f1va)

        # deconflict call graph edges...
        for edge in self.getRefsFrom(f1):
            if edge[2] == f2va:
                return edge

        f2 = self.getFunctionNode(f2va)
        return self.addEdge(f1,f2)

class CodeBlockGraph(v_graphcore.HierGraph):

    def __init__(self, vw):
        v_graphcore.Graph.__init__(self)
        self.vw = vw
        self.nodevas = {}

    def addEntryPoint(self, va):
        node = self.getNode(va)
        if node is not None:
            return node

        # entry point, by de-facto has a node
        enode = self.getCodeBlockNode(va)

        done = set()

        todo = [ va, ]
        while todo:

            va = todo.pop()
            if va in done:
                continue

            done.add(va)

            branches = self._getCodeBranches(va)
            tdone = set()
            for tova,bflags in branches:
                if tova in tdone:
                    continue

                tdone.add(tova)
                node = self.getNodeByVa(va)
                if self._addCodeBranch(node,va,tova,bflags):
                    todo.append( tova )

        return enode

    def _getCodeBranches(self, va):
        loc = self.vw.getLocation(va)
        if loc is None or loc[L_LTYPE] != LOC_OP:
            return []

        lva,lsize,ltype,ltinfo = loc

        xrefs = self.vw.getXrefsFrom(va, rtype=REF_CODE)

        crefs = [ (xto,xflags) for (xfrom,xto,xtype,xflags) in xrefs ]

        # If any of our other branches are conditional, so is our fall
        if not ltinfo & envi.IF_NOFALL:

            bflags = envi.BR_FALL
            if any([ (x[3] & envi.BR_COND) for x in xrefs]):
                bflags |= envi.BR_COND

            crefs.append( (lva+lsize, bflags) )

        return crefs

    def _addCodeBranch(self, node, va, brva, bflags):
        if self.isCodeBlockNode(brva):
            self.addCodeBlockEdge(node,va,brva)
            return True

        if bflags & envi.BR_FALL and not bflags & envi.BR_COND:
            self.addVaToNode(node,brva)
            return True

        if bflags & envi.BR_DEREF:
            # FIXME handle these
            return False

        n2node = self.addCodeBlockEdge(node,va,brva)

        if bflags & envi.BR_PROC:
            self.setNodeProp(n2node,'isfunc',True)

        return True

    def isCodeBlockNode(self, va):
        return self.getNode(va) is not None

    def getCodeBlockBounds(self, node):
        cbva = node[0]
        lastva = node[1]['valist'][-1]
        cbsize = (lastva - cbva) + 1
        return cbva,cbsize

    def getCodeBlockNode(self, va):
        '''
        Create or retrieve a codeblock node for the given va.

        NOTE: If the given va is already present within another
        node, this API will *split* the other node.
        '''
        # is it already a cb node?
        node = self.getNode(va)
        if node is not None:
            return node

        # is it part of another block already?
        node = self.getNodeByVa(va)
        newnode = self.addNode(nid=va,cbva=va,valist=())
        self.addVaToNode(newnode,va)

        if node is None:
            return newnode

        # we need to split an existing node... neato...
        valist = node[1]['valist']
        vaidx = valist.index(va)

        vabeg = valist[:vaidx]
        vaend = valist[vaidx:]

        lastva = vabeg[-1]
        newlastva = vaend[-1]

        self.setNodeVaList(node, vabeg)
        self.setNodeVaList(newnode, vaend)

        # steal all his outbound codeflow edges
        for edge in self.getRefsFrom(node):
            codeflow = edge[3].get('codeflow')
            if codeflow is None:
                continue
            self.addCodeBlockEdge(newnode, codeflow[0], codeflow[1])
            self.delEdge(edge)

        # add an outbound to us...
        self.addCodeBlockEdge(node, lastva, va)
        return newnode

    def addCodeBlockEdge(self, node1, va1, va2):
        vatup = (va1,va2)

        edges = self.getEdgesByProp('codeflow',vatup)
        if len(edges):
            return edges[0]

        node2 = self.getCodeBlockNode(va2)
        edge = self.addEdge(node1, node2)

        self.setEdgeProp(edge, 'va1', va1)
        self.setEdgeProp(edge, 'va2', va2)
        self.setEdgeProp(edge, 'codeflow', vatup)

        #w1 = node1[1].get('weight',0)
        #w2 = node2[1].get('weight',0)
        # track weights in real time ( per func? )
        #self.setNodeProp(node2,'weight',max(w2,w1+1))

        return node2

    def addVaToNode(self, node, va):
        self.nodevas[va] = node
        valist = node[1]['valist']
        self.setNodeProp(node,'valist',valist + (va,))

    def setNodeVaList(self, node, valist):
        [ self.nodevas.pop(va,None) for va in node[1]['valist'] ]
        [ self.nodevas.__setitem__(va,node) for va in valist ]
        self.setNodeProp(node,'valist',valist)

    def getNodeByVa(self, va):
        return self.nodevas.get(va)

class FuncBlockGraph(CodeBlockGraph):

    def __init__(self, vw, fva):
        CodeBlockGraph.__init__(self,vw)
        root = self.addEntryPoint(fva)
        self.setHierRootNode(root)

    def _getCodeBranches(self, va):
        return [ x for x in CodeBlockGraph._getCodeBranches(self,va) if not x[1] & envi.BR_PROC ]

