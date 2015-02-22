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
        ('bazprop', {'type':'utf8','defval':None,'indexes':['keyval'] } )
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

        # manually initialize ctors for intrinsic types
        self.node_ctors['type'] = self._ctor_node
        self.node_ctors['prop'] = self._ctor_node
        self.node_ctors['noun'] = self._ctor_node
        self.node_ctors['verb'] = self._ctor_node

        self.edge_ctors = {}
        self.edge_dtors = {}

        self.type_disps = {}
        self.type_norms = {}

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
            ret['props'][name] = propinfo

        for node in self.graph.getNodesByProp('noun'):
            noun = node[1].get('noun')

            nouninfo = {}
            ret['nouns'][noun] = nouninfo

        for node in self.graph.getNodesByProp('verb'):
            verb = node[1].get('verb')
            verbinfo = {}
            ret['verbs'][verb] = verbinfo

        return {}

    def initDataModel(self):
        '''
        Allows sub-classes a callback during construction.
        '''
        pass

    def bumpDataModel(self):
        self.datamodel = self.getDataModel()
        self.synFireEvent('model:bump',{'datamodel':self.datamodel})

    def _ctor_node(self, noun, valu, **props):
        # base node constructor
        nid = graphid( (noun,valu) )
        nprops = { noun:valu, '_:noun':noun, '_:created':now() }

        prefix = '%s:' % noun
        for key,val in props.items():
            if not key.startswith(prefix):
                continue

            norm = self.type_norms.get(key,nop)
            nprops[key] = norm(val)

        # FIXME set default values from data model
        node = (nid,nprops)
        return self.graph._addNode(node)

    def _dtor_node(self, node):
        print('FIXME _dtor_node')

    def _ctor_edge(self, n1, verb, valu, n2, **props):
        eid = graphid( (n1[0],verb,valu,n2[0]) )
        eprops = { verb:valu, '_:verb':verb, '_:created':now() }

        prefix = '%s:' % verb
        for key,val in props.items():
            if not key.startswith(prefix):
                continue

            norm = self.type_norms.get(key,nop)
            eprops[key] = norm(val)

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
        node = self.formNodeByNoun('noun',noun)
        self.graph.initNodeIndex(noun,'uniq')

        if ctor == None: ctor = self._ctor_node
        if dtor == None: dtor = self._dtor_node

        self.node_ctors[noun] = ctor
        self.node_dtors[noun] = dtor

    def initModelProp(self, prop, datatype='utf8', indexes=()):
        node = self.formNodeByNoun('prop',prop,datatype=datatype)
        # hrm...  we need to know if it's a node prop or an edge prop
        for index in indexes:
            self.graph.initNodeIndex(prop,index)

    def initModelVerb(self, n1, verb, n2, ctor=None, dtor=None):

        props = {'verb:n1':n1,'verb:n2':n2}
        node = self.formNodeByNoun('verb',verb,**props)

        self.graph.initEdgeIndex(verb,'keyval')

        if ctor == None: ctor = self._ctor_edge
        if dtor == None: dtor = self._dtor_edge

        self.edge_ctors[verb] = ctor
        self.edge_dtors[verb] = dtor

    def formNodeByNoun(self, noun, valu, **props):
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
        norm = self.type_norms.get(noun,nop)
        return self.formNodeByNoun(noun,norm(valu),**props)

    def getNodeByNoun(self, noun, valu):
        nodes = self.graph.getNodesByProp(noun,valu)
        if nodes:
            return nodes[0]
        return None

    def getNodesByProp(self, prop, valu=None, limit=None, index='keyval'):
        return self.graph.getNodesByProp(prop,valu=valu,limit=limit,index=index)

    def formEdgeByVerb(self, n1, verb, valu, n2, **props):

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

    def getNodesByDisp(self, prop, valu, limit=None, index='keyval'):
        norm = self.type_norms.get(prop,nop)
        return self.getNodesByProp(prop,valu=norm(valu),limit=limit,index=index)
            
    def getEdgesByDisp(self, prop, valu, limit=None, index='keyval'):
        norm = self.type_norms.get(prop,nop)
        return self.getEdgesByProp(prop,valu=norm(valu),limit=limit,index=index)

    def setNodeProp(self, node, prop, valu):
        return self.graph.setNodeProp(node,prop,valu)

    def setEdgeProp(self, edge, prop, valu):
        return self.graph.setEdgeProp(edge,prop,valu)

    def setNodeProps(self, node, **props):
        return self.graph.setNodeProps(node,**props)

    def setEdgeProps(self, edge, **props):
        return self.graph.setEdgeProps(edge,**props)

    def getPropDisp(self, noge, prop):
        disp = self.type_disps.get(prop)
        return disp( noge[1].get(prop) )

