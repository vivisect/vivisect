import vertex.model as v_model

import synapse.lib.common as s_common
import synapse.event.dist as s_evtdist

import vivisect.lib.bits as v_bits
import vivisect.hal.memory as v_memory
import vivisect.lib.bexfile as v_bexfile
import vivisect.lib.pagelook as v_pagelook

class VivError(Exception):pass
class VivNoSuchFile(VivError):pass

# should probably extend hal.memory
class VivView(v_memory.Memory):
    '''
    A VivView represents files from a VivWorksace mapped at specific
    addresses.

    ( use VivWorkspace.getVivView() to create one )

    A VivWorkspace stores all metadata as relative offsets from the
    base address of the files loaded into the workspace.  In order to
    interpret those offset as memory addresses, the workspace requires
    the creation of a VivView which specified base load addresses for

    Much of the traditional 1.0 VivWorkspace API lives here due to the
    fact that it.. you know... has addresses...

    '''
    def __init__(self, vw, pagesize=4096):
        v_memory.Memory.__init__(self)
        self.vw = vw
        self.pages = v_pagelook.PageLook(pagesize=pagesize)

    def addrToFileAddr(self, addr):
        '''
        Translate a virtual address to a fileaddr (hash,ra) tuple.

        This API is mostly used by the view to map virtual addresses
        back to the fileaddr tuples used by the VivWorkspace.  Using
        it should only be needed if directly calling into workspace.

        Example:

            fa = vv.addToFileAddr(0x41414100)
            # do fileaddr specific stuff...
        '''
        maptup = self.pages.get(addr)
        if maptup == None:
            return None

        fh,ba = maptup
        ra = addr - ba
        return (fh,ra)

    def formFileAddr(self, addr):
        '''
        Create a fileaddr graph node for the translated virtual address.
        '''

    def getFileAddr(self, addr):
        fa = self.addrToFileAddr(addr)
        return self.vw.getFileAddr(fa)

    def formFuncAddr(self, addr, funcdef=None):

        if funcdef == None:
            funcdef = 'void sub_%.8x()' % addr

        fa = self.addrToFileAddr(addr)
        if fa == None:
            raise Exception('Invalid File Addr: 0x%.8x' % (addr,))

        node = self.vw.formFileAddr(*fa)
        self.vw.setNodeProp(node,'fileaddr:func',1)

    def formInstAddr(self, addr, inst):
        '''
        Create/Retrieve an instruction location in the VivWorkspace.
        '''
        todo = [ (addr,inst) ]

        while todo:
            addr,inst = todo.pop()

            fh,ra = self.addrToFileAddr(addr)
            node = self.vw.formFileAddr(fh,ra)

            self.vw.setNodeProp(node,'fileaddr:inst:mnem',inst.mnem())
            self.vw.setNodeProp(node,'fileaddr:inst:size',inst.size())

    #def formPadAddr(self, addr, size):
    #def formDataAddr(self, addr, vtype):

    def loadVivFile(self, filehash, baseaddr=None):

        node = self.vw.getFileNode(filehash)
        if node == None:
            raise VivNoSuchFile(filehash)

        if baseaddr == None:
            baseaddr = node[1].get('file:baseaddr',0)

        # FIXME deconflict collisions

        filename = v_bits.b2h(filehash)

        for ra,perms,bytez in self.vw.getFileMaps(filehash):
            maptup = (filehash,baseaddr)
            self.pages.put( baseaddr + ra, len(bytez), maptup)
            self.addMemoryMap( baseaddr + ra, perms, filename, bytez )

        # FIXME apply relocations!

class VivWorkspace(s_evtdist.EventDist):
    '''
    The Vivisect MarkII Workspace.

    The VivWorkspace is implemented using a vertex GraphModel.
    Each file loaded into the workspace creates a "file" node
    (by md5) and all annotations on addresses within the file
    are created as "fileaddr" nodes which are recorded as
    relative addresses within each file.

    '''
    def __init__(self, model=None, **config):
        s_evtdist.EventDist.__init__(self)
        if model == None:
            model = v_model.GraphModel()

        self.runinfo = {}   # used for non-persistant runtime info

        # FIXME glue event layers together
        self.model = model

        self.model.initModelNoun('config')

        self.model.initModelNoun('file', ctor=self._ctor_file)
        self.model.initModelNoun('filemap', ctor=self._ctor_filemap)
        self.model.initModelNoun('fileaddr', ctor=self._ctor_fileaddr)

        # setup default indexes
        self.model.initModelProp('file',indexes=['keyval'])
        self.model.initModelProp('filemap:file',indexes=['keyval'])
        self.model.initModelProp('fileaddr:file',indexes=['keyval'])

        self.model.initModelNoun('config')
        self.model.initModelVerb('fileaddr','flow','fileaddr')

        node = self.model.formNodeByNoun('config','viv')
        if node[1].get('config:ident') == None:
            ident = s_common.guid()
            node = self.model.setNodeProp(node,'config:ident',ident)

        self.ident = node[1].get('config:ident')

        for key,val in config.items():
            prop = 'config:%s' % key
            if node[1].get(prop) != val:
                node = self.model.setNodeProp(node,prop,val)

    def runVivAnalyze(self, filehash=None):
        '''
        Trigger VivWorkspace analysis.
        '''
        self.synFireEvent('viv:analyze:init',{})

        for node in self.model.getNodesByProp('file'):
            filehash = node[1].get('file')
            baseaddr = node[1].get('file:baseaddr', 0x41410000)

            basemaps = {filehash:baseaddr}
            view = self.getVivView(basemaps=basemaps)

            # notify the various strap hangers that it's time
            # for shit to get real.
            evtinfo = dict(vw=self,node=node,view=view,filehash=filehash)
            self.synFireEvent('viv:analyze:file',evtinfo)

        # FIXME put stats in here about new stuff?
        self.synFireEvent('viv:analyze:fini',{})

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
            props = {'filemap:perms':perms,'filemap:bytes':bytez}
            mapnode = self.model.formNodeByNoun('filemap',(md5,ra),**props)

        # FIXME give the bexfile impl a shot at it

        self.synFireEventKw('viv:file:loaded', filehash=md5)

        return md5

    def loadFileFd(self, fd):
        bex = v_bexfile.getBexFile(fd)
        return self.loadBexFile(bex)

    def getFileNode(self, filehash):
        '''
        Retrieve the GraphModel node for the given file hash.

        Example:
            node = vw.getFileNode(md5)
        '''
        return self.model.getNodeByNoun('file',filehash)

    def getFileAddr(self, filehash, ra):
        valu = (filehash,ra)
        return self.model.getNodeByNoun('fileaddr',valu=valu)

    def formFileAddr(self, fileaddr):
        '''
        Create a fileaddr node in the VivWorkspace.

        A fileaddr node is used by the VivWorkspace to represent
        a relative address within a specific file in the workspace.
        '''
        return self.model.formNodeByNoun('fileaddr',fileaddr)

    def getFileAddr(self, fileaddr):
        '''
        Retrieve a fileaddr node from the VivWorkspace.

        See formFileAddr() for details on fileaddr nodes within
        the VivWorkspace graph.

        Example:

            fa = (filehash,reladdr)
            node = vw.getFileAddr(fa)

        '''
        return self.model.getNodeByNoun('fileaddr',fileaddr)

    def formFileInst(self, filehash, ra, inst):
        '''
        Create a node for the given ra and apply the "inst" data model.
        '''
        mnem = inst.mnem()
        size = inst.size()

        node = self.formFileAddr(filehash,ra)

    #def formCodeFlowEdge(self, filehash, fromra, tora):
    #def formLogicFlowEdge(self, filehash, fromra, tora):

    #def formFilePad(self,

    def getVivView(self, basemaps=None):
        '''
        Construct a VivView to represent files mapped at specific addresses.

        The VivView class implements the vivisect.hal.memory.Memory
        interface in order to provide virtual address based access to
        VivWorkspace files.

        The "basemaps" dictionary specifies <filehash>:<baseaddr> mappings
        ( and will also map <basename>:<baseaddr> if the basename is uniq
        amongst the files loaded in the workspace.

        When no basemaps are specified, we attempt to load each file at
        it's preferred base address within the VivView.

        Minimal work is done ( no brute force rebasing ) when constructing
        the VivView which allows them to be dynamically constructed for
        (for example) libraries loaded within an ASLR'd process.

        Example:

            # specify no basemaps to get "all" files mapped as they prefer
            vi = vw.getVivView()

        '''
        view = VivView(self)

        if not basemaps:
            for fnode in self.model.getNodesByProp('file'):
                filehash = fnode[1].get('file')
                view.loadVivFile(filehash)
            return view

        for filehash,baseaddr in basemaps.items():
            node = self.model.getNodeByNoun('file',filehash)
            #if node == None:
                # FIXME try to get the file by basename

            if node == None:
                raise Exception('Unknown File: %s' % (filehash,))

            realhash = node[1].get('file')
            view.loadVivFile(realhash, baseaddr=baseaddr)

        return view

    #def getVivCpu(self, 

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
        for node in self.model.getNodesByProp('filemap:file',valu=filehash):
            ra = node[1].get('filemap:ra')
            perms = node[1].get('filemap:perms')
            bytez = node[1].get('filemap:bytes')
            ret.append( (ra,perms,bytez) )
        return ret

    #def getFileSyms(self, filehash):
    #def getFileRelocs(self, filehash):

    def _ctor_file(self, noun, valu, **props):
        props.setdefault('file:arch','')
        props.setdefault('file:format','')
        props.setdefault('file:platform','')
        props.setdefault('file:basename','')
        props.setdefault('file:origpath','')
        props.setdefault('file:baseaddr',None)
        return self.model._ctor_node(noun, valu, **props)

    def _ctor_filemap(self, noun, valu, **props):
        props['filemap:ra'] = valu[1]
        props['filemap:file'] = valu[0]
        props.setdefault('filemap:perms',0)
        props.setdefault('filemap:bytes',b'')
        return self.model._ctor_node(noun, valu, **props)

    def _ctor_fileaddr(self, noun, valu, **props):
        props['fileaddr:ra'] = valu[1]
        props['fileaddr:file'] = valu[0]
        return self.model._ctor_node(noun, valu, **props)

