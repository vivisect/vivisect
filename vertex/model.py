import time
import hashlib

import vertex.graph as v_graph
import synapse.lib.common as s_common
import synapse.event.dist as s_evtdist

import msgpack # version was checked by s_common

datamodel = {
    'nouns':[
        ('foo',{'doc':'a foo!'}),
    ],
    'verbs':[
        ('bar',{'n1:noun':'foo','n2:noun':'bar','uniq':'bazprop','doc':'the bar edge!'})
    ],
    'props':[
        ('bazprop', {'type':'str','defval':None,'indexes':['keyval'] } )
    ],
    'types':[
    ],
}

def nop(x):
    return x

def now():
    return int(time.time())

def graphid(x):
    return hashlib.md5( msgpack.packb(x, use_bin_type=True) ).digest()

class DataModelProtests(Exception):pass

class GraphModel(s_evtdist.EventDist):
    '''
    A graph model implements a graph with strong data types and
    defined relationships which are defined within the graph to
    allow the data model to be introspected.

    '''
    def __init__(self, graph=None):
        s_evtdist.EventDist.__init__(self)

        if graph == None:
            graph = v_graph.Graph()

        self.graph = graph

        # initialize for our built in types
        self.graph.initNodeIndex('type','keyval')
        self.graph.initNodeIndex('prop','keyval')
        self.graph.initNodeIndex('noun','keyval')
        self.graph.initNodeIndex('verb','keyval')

        self.node_ctors = {}
        self.node_dtors = {}

        self.node_setrs = {}
        self.edge_setrs = {}

        # manually initialize ctors for intrinsic types
        self.node_ctors['type'] = self._ctor_node
        self.node_ctors['prop'] = self._ctor_node
        self.node_ctors['noun'] = self._ctor_node
        self.node_ctors['verb'] = self._ctor_node

        self.edge_ctors = {}
        self.edge_dtors = {}

        self.type_disps = {}
        self.type_norms = {}

        self.datamodel = {'nouns':{},'verbs':{},'props':{},'types':{}}

        self.initModelType('str', disp=nop, norm=str)
        self.initModelType('int', disp=str, norm=int)

        self.bumpDataModel()

        self.initDataModel()
        self.bumpDataModel()

    def getDataModel(self):
        '''
        Build and return a dict which describes the current data model.

        datamodel = {

            'types':{
                <name>: {}, # typeinfo
            },

            'props':{
                <name>: {}, # propinfo
            },

            'nouns':{
                <noun>: {}, # nouninfo
            },

            'verbs':{
                <verb>: {}, # verbinfo
            },
        }

        '''
        ret = {'nouns':{},'verbs':{},'props':{},'types':{}}

        for node in self.graph.getNodesByProp('type'):
            name = node[1].get('type')

            typeinfo = {}
            ret['types'][name] = typeinfo

        for node in self.graph.getNodesByProp('prop'):
            name = node[1].get('prop')

            propinfo = {}
            propinfo['datatype'] = node[1].get('prop:type')
            ret['props'][name] = propinfo

        for node in self.graph.getNodesByProp('noun'):
            noun = node[1].get('noun')

            nouninfo = {}
            ret['nouns'][noun] = nouninfo

        for node in self.graph.getNodesByProp('verb'):
            verb = node[1].get('verb')
            verbinfo = {}
            ret['verbs'][verb] = verbinfo

        return ret

    def initDataModel(self):
        '''
        Allows sub-classes a callback during construction.
        '''
        pass

    def bumpDataModel(self):
        self.datamodel = self.getDataModel()
        self.fire('model:bump', datamodel=self.datamodel)

    def normPropValu(self, prop, valu):
        '''
        Normalize a property value using the data model.

        Example:

            valu = g.normPropValu('foo:bar',valu)

        '''
        if valu == None:
            return None

        propinfo = self.datamodel['props'].get(prop)
        if propinfo == None:
            return valu

        datatype = propinfo.get('datatype')
        if datatype == None:
            return valu

        norm = self.type_norms.get(datatype)
        if norm == None:
            return valu

        return norm(valu)

    def _ctor_node(self, noun, valu, **props):
        # base node constructor
        nid = graphid( (noun,valu) )
        nprops = { noun:valu, '_:noun':noun, '_:created':now() }

        prefix = '%s:' % noun
        for key,val in props.items():
            if not key.startswith(prefix):
                continue

            nprops[key] = self.normPropValu(key,val)

        # FIXME set default values from data model
        node = (nid,nprops)
        return self.graph._addNode(node)

    def _dtor_node(self, node):
        self.graph.delNode(node)

    def _ctor_edge(self, n1, verb, valu, n2, **props):
        eid = graphid( (n1[0],verb,valu,n2[0]) )
        eprops = { verb:valu, '_:verb':verb, '_:created':now() }

        prefix = '%s:' % verb
        for key,val in props.items():
            if not key.startswith(prefix):
                continue

            eprops[key] = self.normPropValu(key,val)

        # FIXME set default values from data model

        eprops['_:n1'] = n1[0]
        eprops['_:n2'] = n2[0]

        edge = (eid,eprops)
        return self.graph._addEdge(edge)

    def _dtor_edge(self, edge):
        print('FIXME _dtor_edge')

    #def _ctor_noun(self, noun, valu, **props):
    #def _ctor_verb(self, noun, valu, **props):
    #def _ctor_prop(self, noun, valu, **props):
    #def _ctor_type(self, noun, valu, **props):

    def initModelType(self, name, disp=None, norm=None):
        '''
        Initialize a "type" in the data model.

        For each data type a "display" callback and a "normalizer" callback
        may be specified to facilitate interfaces.
        '''
        node = self.formNodeByNoun('type',name)
        self.type_disps[name] = disp
        self.type_norms[name] = norm

    def initModelNoun(self, noun, ctor=None, dtor=None):
        '''
        Initialize a noun within the GraphModel.
        Optionally specify ctor/dtor routines for node construction / deletion.

        Example:

            m = GraphModel()

            def _ctor_woot(noun,valu,**props):
                props.setdefault('woot:score',0)

                score = props.get('woot:score')
                if score > 9999: # some kinda max...
                    raise DataModelProtests('woot:score may not be larger than 9999')

                return m._ctor_node(noun,valu,**props)

            m.initModelNoun('woot', ctor=_ctor_woot)

        '''
        node = self.formNodeByNoun('noun',noun)
        #self.graph.initNodeIndex(noun,'uniq')
        self.graph.initNodeIndex(noun,'keyval')

        if ctor == None: ctor = self._ctor_node
        if dtor == None: dtor = self._dtor_node

        self.node_ctors[noun] = ctor
        self.node_dtors[noun] = dtor

    def initModelProp(self, prop, datatype='str', indexes=('keyval',)):
        props = {'prop:type':datatype}
        node = self.formNodeByNoun('prop',prop,**props)
        # hrm...  we need to know if it's a node prop or an edge prop
        for index in indexes:
            self.graph.initNodeIndex(prop,index)

    def addNodePropSetr(self, prop, setr):
        '''
        Add a "setter" method to the GraphModel for the given node property.

        Example:

            m = GraphModel()

            def setwoot(node,prop,valu):
                return m.graph.setNodeProp(node,prop,valu + 30)

            m.addNodePropSetr('woot',setwoot)
                

        Notes:

            * setter is expected to update graph layer
            * setter will recieve normalized values

        '''
        self.node_setrs[prop] = setr

    def addEdgePropSetr(self, prop, setr):
        '''
        Add a "setter" method to the GraphModel for the given edge property.

        ( see addNodePropSetr for details )
        '''
        self.edge_setrs[prop] = setr

    def initModelVerb(self, n1, verb, n2, ctor=None, dtor=None):
        '''
        Initialize an edge verb in the GraphModel.

        Each type of edge within the GraphModel must be declared in advance.
        For a given verb, a constructor/destructor may be specified which
        will be called to handle the creation/destruction of that edge type.
        If none are specified, default ctor/dtors will form and delete the edge.

        Example:

            g.initModelVerb('file','containsfile','file')


        '''
        props = {'verb:n1':n1,'verb:n2':n2}
        node = self.formNodeByNoun('verb',verb,**props)

        self.graph.initEdgeIndex(verb,'keyval')

        if ctor == None: ctor = self._ctor_edge
        if dtor == None: dtor = self._dtor_edge

        self.edge_ctors[verb] = ctor
        self.edge_dtors[verb] = dtor

    def formNodeByNoun(self, noun, valu, **props):
        '''
        Create or retrieve a node from the GraphModel.

        Example:

            node = g.formNodeByNoun('foo',10)

        '''
        ctor = self.node_ctors.get(noun)

        if ctor == None:
            raise DataModelProtests('%s is not a valid noun' % (noun,))

        nid = graphid( (noun,valu) )

        # FIXME with storage lock?
        node = self.graph.getNodeById(nid)
        if node == None:
            node = ctor( noun, valu, **props)

        return node

    def formNodeByDisp(self, noun, valu, **props):
        valu = self.normPropValu(noun,valu)
        return self.formNodeByNoun(noun,valu,**props)

    def getNodeByNoun(self, noun, valu):
        '''
        Retrieve an existing node from the GraphModel by noun.

        Example:

            node = g.getNodeByNoun('foo',10)
            if node != None:
                dostuff(node)

        '''
        nodes = self.graph.getNodesByProp(noun,valu)
        if nodes:
            return nodes[0]
        return None

    def getNodesByProp(self, prop, valu=None, limit=None, index='keyval'):
        '''
        Retrieve a list of nodes from the GraphModel by prop[=valu].

        Example:

            nodes = g.getNodesByProp('vehicle:type','car')
            print('there are %d cars' % (len(nodes),))

        '''
        return self.graph.getNodesByProp(prop,valu=valu,limit=limit,index=index)

    def delNode(self, node):
        '''
        Delete a node from the GraphModel.

        Example:

            node = g.getNodeByProp('foo',10)

            g.delNode(node)

        '''
        noun = node[1].get('_:noun')
        dtor = self.node_dtors.get(noun, self._dtor_node)
        return dtor(node)

    def formEdgeByVerb(self, n1, verb, valu, n2, **props):
        '''
        Create or retrieve an edge from the GraphModel.

        Example:

            node1 = g.formNodeByNoun('foo',10)
            node2 = g.formNodeByNoun('foo',20)

            g.formEdgeByVerb(node1, 'parentof', node2 )

        Notes:

            * the verb must have been declared in the model using
              initModelVerb.

        '''
        ctor = self.edge_ctors.get(verb)
        if ctor == None:
            raise DataModelProtests('%s is not a valid verb' % (verb,))

        eid = graphid( (n1[0],verb,valu,n2[0]) )
        edge = self.graph.getEdgeById(eid)

        if edge == None:
            edge = ctor( n1, verb, valu, n2, **props )

        return edge

    def getEdgesByProp(self, prop, valu=None, limit=None, index='keyval'):
        '''
        Retrieve edges from the GraphModel which have the specified prop[=valu].

        Example:

            for edge in g.getEdgesByProp('foo',valu=20,limit=100):
                dostuff(edge)
        '''
        return self.graph.getEdgesByProp(prop,valu=valu,limit=limit,index=index)

    def getNodesByProp(self, prop, valu=None, limit=None, index='keyval'):
        '''
        Retrieve nodes from the GraphModel which have the specified prop[=valu].

        Example:
            for node in g.getNodesByProp('foo',valu=20,limit=100):
                dostuff(node)

        '''
        return self.graph.getNodesByProp(prop,valu=valu,limit=limit,index=index)

    def setNodeProp(self, node, prop, valu):
        '''
        Set a node property in the GraphModel.

        Example:

            g.setNodeProp(node, 'foo', 30)

        '''
        valu = self.normPropValu(prop,valu)
        setr = self.node_setrs.get(prop, self.graph.setNodeProp )
        return setr(node, prop, valu)

    def setEdgeProp(self, edge, prop, valu):
        '''
        Set an edge property in the GraphModel.

        Example:

            g.setEdgeProp(edge, 'foo', 30)

        '''
        valu = self.normPropValu(prop,valu)
        setr = self.edge_setrs.get(prop, self.graph.setEdgeProp )
        return setr(edge, prop, valu)

    def getNodeById(self, nid):
        '''
        Return a node from the GraphModel by node id.

        Example:

            node = g.getNodeById(nid)

        '''
        return self.graph.getNodeById(nid)

    def getEdgeById(self, nid):
        '''
        Return an edge from the GraphModel by edge id.

        Example:

            edge = g.getEdgeById(eid)

        '''
        self.graph.getEdgeById(eid)

    def getPropDisp(self, noge, prop):
        disp = self.type_disps.get(prop)
        return disp( noge[1].get(prop) )

