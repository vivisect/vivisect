import vertex.model as v_model

import synapse.lib.common as s_common
import synapse.event.dist as s_evtdist

import vivisect.lib.bits as v_bits
import vivisect.hal.memory as v_memory
import vivisect.lib.pagelook as v_pagelook

class VivError(Exception):pass
class VivNoSuchFile(VivError):pass

# should probably extend hal.memory
class VivView(v_memory.Memory):
    '''
    A VivView represents files from a VivWorksace mapped at addresses.
    '''
    def __init__(self, vw, pagesize=4096):
        v_memory.Memory.__init__(self)

        self.vw = vw
        #self.maptups = []
        #self.pages = v_pagelook.PageLook(pagesize=pagesize)

    def loadVivFile(self, filehash, baseaddr=None):

        node = self.vw.getFileNode(filehash)
        if node == None:
            raise VivNoSuchFile(filehash)

        if baseaddr == None:
            baseaddr = node[1].get('file:baseaddr',0)

        # FIXME deconflict collisions

        filename = v_bits.b2h(filehash)

        for ra,perms,bytez in self.vw.getFileMaps(filehash):
            self.addMemoryMap( baseaddr + ra, perms, filename, bytez )

        # FIXME apply relocations!

class VivWorkspace(s_evtdist.EventDist):

    def __init__(self, model=None, **config):
        s_evtdist.EventDist.__init__(self)
        if model == None:
            model = v_model.GraphModel()

        self.runinfo = {}   # used for non-persistant runtime info

        # FIXME glue event layers together
        self.model = model

        self.model.initModelNoun('file', ctor=self._ctor_file)
        self.model.initModelNoun('addr', ctor=self._ctor_addr)
        self.model.initModelNoun('memmap', ctor=self._ctor_memmap)

        # setup default indexes
        self.model.initModelProp('file',indexes=['keyval'])
        self.model.initModelProp('memmap:file',indexes=['keyval'])
        self.model.initModelProp('addr:file',indexes=['keyval'])

        self.model.initModelNoun('config')
        self.model.initModelVerb('raddr','flow','raddr')

        node = self.model.formNodeByNoun('config','viv')
        if node[1].get('config:ident') == None:
            ident = s_common.guid()
            node = self.model.setNodeProp(node,'config:ident',ident)

        self.ident = node[1].get('config:ident')

        for key,val in config.items():
            prop = 'config:%s' % key
            if node[1].get(prop) != val:
                node = self.model.setNodeProp(node,prop,val)

    def getRunInfo(self, prop):
        '''
        Retrieve a non-persistant "runtime" variable.

        Example:

            # not useful, but exemplar...
            vw.setRunInfo('pid', os.getpid() )
            ...
            vw.getRunInfo('pid')
        '''
        return self.runinfo.get(prop)

    def setRunInfo(self, prop, valu):
        '''
        Set a non-persistant "runtime" variable.

        Use this API to set/manage configuration info which is
        volatile and should not be saved across instances of the
        VivWorkspace.

        Example:

            # not useful, but exemplar...
            vw.setRunInfo('pid', os.getpid() )
            ...
            vw.getRunInfo('pid')

        '''
        self.runinfo[prop] = valu
        evtinfo = {'prop':prop,'valu':valu}
        self.synFireEvent('viv:run:info', evtinfo)
        self.synFireEvent('viv:run:info:%s' % prop, evtinfo)

    def getVivConfig(self, key, default=None):
        '''
        Retrieve a persistent (stored in workspace) global config value.

        Example:

            ident = vw.getVivConfig('ident')

        '''
        node = self.model.formNodeByNoun('config','viv')
        return node[1].get('config:%s' % key, default)

    def setVivConfig(self, key, val):
        '''
        Set a persistent (stored in workspace) global config value.

        Example:

            vw.setVivConfig('woot',10)

        '''
        node = self.model.formNodeByNoun('config','viv')
        return self.model.setNodeProp(node,'config:%s' % key, val)

    def loadBexFile(self, bex):
        '''
        Load a binary executable file into the vivisect workspace.
        '''
        md5 = bex.info('md5')

        props = {}
        props['file:arch']      = bex.info('arch')
        props['file:path']      = bex.info('path')
        props['file:size']      = bex.info('filesize')
        props['file:format']    = bex.info('format')
        props['file:platform']  = bex.info('platform')
        props['file:baseaddr']  = bex.baseaddr()

        node = self.model.formNodeByNoun('file',md5,**props)

        for ra,perms,bytez in bex.memmaps():
            props = {'memmap:perms':perms,'memmap:bytes':bytez}
            mapnode = self.model.formNodeByNoun('memmap',(md5,ra),**props)

        # FIXME give the bexfile impl a shot at it

        self.synFireEventKw('viv:file:loaded', filehash=md5)

        return md5

    def getFileNode(self, filehash):
        '''
        Retrieve the GraphModel node for the given file hash.

        Example:
            node = vw.getFileNode(md5)
        '''
        return self.model.getNodeByNoun('file',filehash)

    def getVivView(self, **bases):
        '''
        '''
        view = VivView(self)

        if not bases:
            for fnode in self.model.getNodesByProp('file'):
                filehash = fnode[1].get('file')
                view.loadVivFile(filehash)
            return view

    def getFileHashes(self):
        '''
        Return a list of the file hashes loaded in the VivWorkspace.
        '''
        return [ n[1].get('file') for n in self.model.getNodesByProp('file') ]

    def getFileMaps(self, filehash):
        '''
        Return a list of (ra,perms,bytes) tuples for the a file by hash.
        '''
        ret = []
        for node in self.model.getNodesByProp('memmap:file',valu=filehash):
            ra = node[1].get('memmap:ra')
            perms = node[1].get('memmap:perms')
            bytez = node[1].get('memmap:bytes')
            ret.append( (ra,perms,bytez) )
        return ret

    def _ctor_file(self, noun, valu, **props):
        props.setdefault('file:arch','')
        props.setdefault('file:format','')
        props.setdefault('file:platform','')
        props.setdefault('file:basename','')
        props.setdefault('file:origpath','')
        props.setdefault('file:baseaddr',None)
        return self.model._ctor_node(noun, valu, **props)

    def _ctor_memmap(self, noun, valu, **props):
        props['memmap:ra'] = valu[1]
        props['memmap:file'] = valu[0]
        props.setdefault('memmap:perms',0)
        props.setdefault('memmap:bytes',b'')
        return self.model._ctor_node(noun, valu, **props)

    def _ctor_addr(self, noun, valu, **props):
        props['addr:ra'] = valu[1]
        props['addr:file'] = valu[0]
        return self.model._ctor_node(noun, valu, **props)

