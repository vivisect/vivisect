import collections

import vertex.model as v_model

import synapse.lib.common as s_common
import synapse.event.dist as s_evtdist

import vivisect.hal.cpu as v_cpu
import vivisect.lib.bits as v_bits
import vivisect.hal.memory as v_memory
import vivisect.lib.binfile as v_binfile
import vivisect.lib.pagelook as v_pagelook

from vertex.lib.common import tufo

def ldict():
    return collections.defaultdict(list)

class VivError(Exception):pass
class VivNoSuchFile(VivError):pass

class VivFile:
    '''
    A VivFile contains knowledge of a single file.
    '''
    def __init__(self, store, filemd5):
        self.store = store
        self.filemd5 = filemd5

        self.locsbyprop = collections.defaultdict( ldict )
        self.refsbyprop = collections.defaultdict( ldict )

        self.locsbyra = {}          # addr:(addr,info)
        self.refsbydef = {}         # (src,type,dst):((src,type,dst),info)
        self.refsbysrc = ldict()    # src:[ ((src,type,dst),info), ... ]
        self.refsbydst = ldict()    # dst:[ ((src,type,dst),info), ... ]

        self.evtbus = s_evtdist.EventDist()
        self.evtbus.on('loc:add', self._slot_addLoc )
        self.evtbus.on('loc:del', self._slot_delLoc )
        self.evtbus.on('loc:prop:set', self._slot_setLocProp )
        self.evtbus.on('loc:prop:del', self._slot_delLocProp )

        self.evtbus.on('ref:add', self._slot_addRef )
        self.evtbus.on('ref:del', self._slot_delRef )
        self.evtbus.on('ref:prop:set', self._slot_setRefProp )
        self.evtbus.on('ref:prop:del', self._slot_delRefProp )

        #self.evtstor = store.getFileEventStore(filemd5)
        #self.evtstor.synLoadAndStore( self.evtbus )

    def getLocByAddr(self, addr, add=False):
        '''
        Return a location tuple (addr,info) by relative address.
        '''
        loc = self.locsbyra.get(addr)
        if loc == None and add:
            self.evtbus.fire('loc:add', addr=addr)
            loc = self.locsbyra.get(addr)
        return loc

    def getLocsByProp(self, prop, valu=None):
        '''
        Return a list of location tuples (addr,info) by prop[=valu].
        '''
        if valu == None:
            p = self.locsbyprop.get(prop)
            if p == None:
                return ()

            ret = []
            [ ret.extend( locs ) for locs in p.values() ]
            return ret

        p = self.locsbyprop.get(prop)
        if p == None:
            return ()

        return p.get(valu,())

    def getBinFile(self):
        '''
        Return the vivisect.lib.binfile.BinFile object.
        '''
        pass

    def getRefsByProp(self, prop, valu=None):
        if valu == None:
            p = self.refsbyprop.get(prop)
            if p == None:
                return ()

            ret = []
            [ ret.extend( refs ) for refs in p.values() ]
            return ret

        p = self.refsbyprop.get(prop)
        if p == None:
            return ()

        return p.get(valu,())

    def getRefsBySrc(self, addr):
        '''
        Retrieve a list of ( (src,rtype,dst), info ) tuples by src.
        '''
        return self.refsbysrc.get( addr, () )

    def getRefsByDst(self, addr):
        '''
        Retrieve a list of ( (src,rtype,dst), info ) tuples by dst.
        '''
        return self.refsbydst.get( addr, () )

    def getRefByDef(self, src, reftype, dst, add=False):
        '''
        Return a ref tuple ( (src,reftype,dst), info ) by src:type:dst uniqness.

        Example:

            ref = vf.getRefByDef( addr1, 'code', addr2 )
            vf.setRefProp(ref,'woot',30)

        '''
        rdef = (src,reftype,dst)
        ref = self.refsbydef.get(rdef)
        if ref == None and add:
            self.evtbus.fire('ref:add', rdef=rdef)
            ref = self.refsbydef.get(rdef)
        return ref

    def setLocProp(self, loc, prop, valu):
        oldval = loc[1].get(prop)
        self.evtbus.fire('loc:prop:set', addr=loc[0], prop=prop, valu=valu, oldval=oldval)

    def setRefProp(self, ref, prop, valu):
        '''
        Set a property on on a ref to the given value.

        Example:

            vf.setRefProp(ref, prop, valu)

        '''
        oldval = ref[1].get(prop)
        self.evtbus.fire('ref:prop:set', rdef=ref[0], prop=prop, valu=valu, oldval=oldval)

    def delLocProp(self, loc, prop):
        '''
        Delete a property from the given location tuple.

        Example:

            vf.delLocProp(loc, prop)

        '''
        oldval = loc[1].get(prop)
        self.evtbus.fire('loc:prop:del', addr=loc[0], prop=prop, oldval=oldval)

    def delLoc(self, loc):
        '''
        Delete a location.

        Example:

            vf.delLoc(loc)

        '''
        addr = loc[0]
        for prop,valu in loc[1].items():
            self.evtbus.fire('loc:prop:del', addr=addr, prop=prop, oldval=valu)
        self.evtbus.fire('loc:del', addr=addr)

    def delRefProp(self, ref, prop):
        '''
        Delete a property from the given ref tuple.

        Example:

            vf.delRefProp(ref,prop)

        '''
        self.evtbus.fire('ref:prop:del', rdef=ref[0], prop=prop, oldval=oldval)

    def _slot_addLoc(self, event):
        addr = event[1].get('addr')
        self.locsbyra[addr] = (addr,{})

    def _slot_addRef(self, event):
        rdef = event[1].get('rdef')

        ref = ( rdef, {} )
        self.refsbydef[ rdef ] = ref
        self.refsbysrc[ rdef[0] ].append( ref )
        self.refsbydst[ rdef[2] ].append( ref )

    def _slot_setLocProp(self, event):
        evt,evtinfo = event
        addr = evtinfo.get('addr')
        prop = evtinfo.get('prop')
        valu = evtinfo.get('valu')

        loc = self.locsbyra.get(addr)
        self.locsbyprop[prop][valu].append(loc)
        loc[1][prop] = valu

    def _slot_delLoc(self, event):
        addr = event[1].get('addr')
        self.locsbyra.pop(addr,None)

    def _slot_delLocProp(self, event):
        evt,evtinfo = event

        addr = evtinfo.get('addr')
        prop = evtinfo.get('prop')

        loc = self.locbyra.get(addr)

        valu = loc[1].pop(prop,None)
        if valu == None:
            return valu

        vdict = self.locsbyprop[prop]
        locs = vdict[valu]

        locs.remove(loc)
        if not locs:
            vdict.pop(valu,None)

        if not vdict:
            self.locsbyprop.pop(prop,None)

        return valu

    def _slot_setRefProp(self, event):
        evt,evtinfo = event
        rdef = evtinfo.get('rdef')
        prop = evtinfo.get('prop')
        valu = evtinfo.get('valu')
        ref = self.refsbydef.get(rdef)
        self.refsbyprop[prop][valu].append(ref)
        ref[1][prop] = valu

    def delRef(self, ref):
        '''
        Delete a ref from the VivFile.

        Example:

            vf.delRef(ref)

        '''
        rdef = ref[0]
        for prop,valu in ref[1].items():
            self.evtbus.fire('ref:prop:del', rdef=rdef, prop=prop, oldval=valu)
        self.evtbus.fire('ref:del', rdef=rdef)

    def _slot_delRef(self, event):
        rdef = event[1].get('rdef')
        src,rtype,dst = rdef

        ref = self.refsbydef.pop(rdef,None)
        self.refsbysrc[src].remove(ref)
        self.refsbydst[dst].remove(ref)

    def _slot_delRefProp(self, event):
        evt,evtinfo = event
        rdef = evtinfo.get('rdef')
        prop = evtinfo.get('prop')

        ref = self.refsbydef.get(rdef)
        valu = ref[1].get(prop)

        vdict = self.refsbyprop[prop]
        refs = vdict[valu]

        refs.remove( ref )
        if not refs:
            vdict.pop(valu,None)

        if not vdict:
            self.refsbyprop.pop(prop,None)

        ref[1].pop(prop,None)

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
        #self.pages = v_pagelook.PageLook(pagesize=pagesize)

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
        mmap = self.getMemoryMap(addr)
        if mmap == None:
            return None

        maddr,msize,mperm,minfo = mmap

        ra = addr - minfo.get('baseaddr')
        return (minfo.get('filehash'), ra)

    def formFileAddr(self, addr):
        '''
        Create a fileaddr graph node for the translated virtual address.
        '''
        fa = self.addrToFileAddr(addr)
        if fa == None:
            raise Exception('Invalid File Addr: 0x%.8x' % (addr,))
        return self.vw.formNodeByNoun('fileaddr',fa)

    def getFileAddr(self, addr):
        fa = self.addrToFileAddr(addr)
        if fa == None:
            raise Exception('Invalid File Addr: 0x%.8x' % (addr,))
        return self.vw.getNodeByNoun('fileaddr',fa)

    def formFuncAddr(self, addr, funcdef=None):

        if funcdef == None:
            funcdef = 'void sub_%.8x()' % addr

        fa = self.addrToFileAddr(addr)
        return self.vw.formNodeByNoun('filefunc',fa)

    def formFuncCall(self, caller, callee):
        '''
        Form a filefunc --callfunc--> filefunc edge in the VivWorkspace.

        Example:

            func1 = vv.formFuncAddr(0x41414141)
            func2 = vv.formFuncAddr(0x56565656)

            edge = vv.formFuncCall(func1,func2)

        '''
        return self.vw.formEdgeByVerb(caller,'callfunc', callee)

    def formInstAddr(self, addr, inst):
        '''
        Create/Retrieve an instruction location in the VivWorkspace.
        '''
        todo = [ (addr,inst) ]

        while todo:
            addr,inst = todo.pop()

            fa = self.addrToFileAddr(addr)
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

        path = v_bits.b2h(filehash)

        for m in self.vw.getFileMaps(filehash):

            ra = m[0]
            init = m[1].get('init')
            size = m[1].get('size',len(init))
            perm = m[1].get('perm',v_memory.MM_RWX)

            addr = baseaddr + ra

            info = {
                'init':init,
                'path':path,
                'baseaddr':baseaddr,
                'filehash':filehash,
            }
            mmap = self.initMemoryMap(addr, size, perm, **info)

        # FIXME apply relocations!

class VivWorkspace(v_model.GraphModel):
    '''
    The Vivisect MarkII Workspace.

    The VivWorkspace is implemented using a vertex GraphModel.
    Each file loaded into the workspace creates a "file" node
    (by md5) and all annotations on addresses within the file
    are created as "fileaddr" nodes which are recorded as
    relative addresses within each file.

    '''
    def __init__(self, **config):
        v_model.GraphModel.__init__(self)


        self.runinfo = {}   # used for non-persistant runtime info
        self.binfiles = {}  # BinFile instances for loaded files
        self.byteblobs = {} # <md5>:<bytes>

        # register an event for binary blobs in the graph storage layer
        self.graph.store.on('viv:savebytes', self._viv_savebytes )

        self.initModelNoun('config')

        # init model node defs
        self.initModelNoun('file', ctor=self._ctor_file)
        self.initModelNoun('filemap', ctor=self._ctor_filemap)
        self.initModelNoun('fileaddr', ctor=self._ctor_fileaddr)
        self.initModelNoun('filefunc', ctor=self._ctor_filefunc, dtor=self._dtor_filefunc)

        self.initModelVerb('filefunc','callfunc','filefunc')

        # init model props and indexes
        self.initModelProp('file',indexes=['keyval'])
        self.initModelProp('file:libname',indexes=['keyval'])

        self.initModelProp('filemap:file',indexes=['keyval'])

        self.initModelProp('fileaddr:file',indexes=['keyval'])
        self.initModelProp('fileaddr:entry',indexes=['keyval'])
        self.initModelProp('fileaddr:reloc',indexes=['keyval'])

        self.initModelProp('filefunc:file',indexes=['keyval'])

        # init model edge defs
        self.initModelVerb('fileaddr','flow','fileaddr')

        node = self.formNodeByNoun('config','viv')
        if node[1].get('config:ident') == None:
            ident = s_common.guid()
            node = self.setNodeProp(node,'config:ident',ident)

        self.ident = node[1].get('config:ident')

        for key,val in config.items():
            prop = 'config:%s' % key
            if node[1].get(prop) != val:
                node = self.setNodeProp(node,prop,val)

    def _viv_savebytes(self, event):
        md5 = event[1].get('md5')
        byts = event[1].get('bytes')
        info = event[1].get('info',{})

        bf = v_binfile.getBinFile(byts, **info)

        self.binfiles[md5] = bf
        self.byteblobs[md5] = byts

    def runVivAnalyze(self, filehash=None):
        '''
        Trigger VivWorkspace analysis.
        '''
        self.fire('viv:analyze:init')

        for node in self.getNodesByProp('file'):
            filehash = node[1].get('file')
            baseaddr = node[1].get('file:baseaddr', 0x41410000)

            basemaps = {filehash:baseaddr}
            view = self.getVivView(basemaps=basemaps)

            # notify the various strap hangers that it's time
            # for shit to get real.
            self.fire('viv:analyze:file', vw=self, node=node, view=view, filehash=filehash)

        # FIXME put stats in here about new stuff?
        self.fire('viv:analyze:fini')

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
        self.fire('viv:run:info', prop=prop, valu=valu)
        self.fire('viv:run:info:%s' % prop, valu=valu)

    def getVivConfig(self, key, default=None):
        '''
        Retrieve a persistent (stored in workspace) global config value.

        Example:

            ident = vw.getVivConfig('ident')

        '''
        node = self.formNodeByNoun('config','viv')
        return node[1].get('config:%s' % key, default)

    def setVivConfig(self, key, val):
        '''
        Set a persistent (stored in workspace) global config value.

        Example:

            vw.setVivConfig('woot',10)

        '''
        node = self.formNodeByNoun('config','viv')
        return self.setNodeProp(node,'config:%s' % key, val)

    #def loadFileBytes(self, byts):

    def loadBinFd(self, fd, **info):
        byts = fd.read()
        bf = v_binfile.getBinFile(byts, **info)
        return self.loadBinFile(bf)

    #def loadBinFilePath(self, path):
        #fd = open(path,'rb')
        #return self.loadBinFd(fd, path=path)

    def loadFileBytes(self, byts, **info):
        '''
        Load a binary file into the workspace from python bytes.

        Example:

            byts = open('foo.exe','rb').read()
            viv.loadFileBytes(byts)

        Notes:

            * **info kwargs are passed to getFile()

        '''
        bf = v_binfile.getFile(byts, **info)
        return self.loadBinFile(bf)

    def loadBinFile(self, bf):
        '''
        Load a BinFile into the vivisect workspace.

        Notes:

            * See vivisect.lib.binfile for creating a BinFile instance.
              ( or use loadBinFd )

        '''
        md5 = bf.getMd5()

        props = {}
        props['file:arch']      = bf.getArch()
        props['file:size']      = bf.getSize()
        props['file:format']    = bf.getFormat()
        props['file:libname']   = bf.getLibName()
        props['file:platform']  = bf.getPlatform()
        props['file:baseaddr']  = bf.getBaseAddr()

        props['file:path']      = bf.getInfo('path')

        node = self.formNodeByNoun('file',md5,**props)

        # do we already have a default arch?
        if self.getVivConfig('arch') == None:
            self.setVivConfig('arch',bf.getArch())

        byts = bf.getBytes()
        self.graph.store.fire('viv:savebytes', md5=md5, bytes=byts)

        for mmap in bf.getMemoryMaps():
            ra = mmap[0]
            perm = mmap[1].get('perm')
            init = mmap[1].get('init')

            props = {'filemap:perm':perm,'filemap:init':init}
            mapnode = self.formNodeByNoun('filemap',(md5,ra),**props)

        for ra,name,etype in bf.getExports():
            self.addFileEntry( (md5,ra), etype=etype )
            if name != None:
                # FIXME MAKE SYMBOLS AND NAMES
                pass

        for ra,rtype,rinfo in bf.getRelocs():
            self.addFileReloc( (md5,ra), rtype, **rinfo )

        # FIXME give the binfile impl a shot at it
        self.fire('viv:file:loaded', filehash=md5)

        return md5

    def getFileNode(self, filehash):
        '''
        Retrieve the GraphModel node for the given file hash.

        Example:
            node = vw.getFileNode(md5)

        '''
        return self.getNodeByNoun('file',filehash)

    def formFileAddr(self, fileaddr):
        '''
        Create a fileaddr node in the VivWorkspace.

        A fileaddr node is used by the VivWorkspace to represent
        a relative address within a specific file in the workspace.

        '''
        return self.formNodeByNoun('fileaddr',fileaddr)

    def addFileEntry(self, fa, etype='unkn'):
        '''
        Annotate a fileaddr node as being an "entry".

        etypes:
        * unkn      - unknown, marks for heuristic analysis
        * func      - function entry point
        * code      - code entry ( but possibly not procedure )
        * data      - data entry ( likely exported variable )

        Example:

            vw.addFileEntry(fa,etype='func')

        '''
        node = self.formNodeByNoun('fileaddr',fa)

        # lets not go backwards in specificity...
        valu = node[1].get('fileaddr:entry')
        if etype == 'unkn' and valu != None:
            return node

        return self.setNodeProp(node,'fileaddr:entry',etype)

    def addFileReloc(self, fa, rtype, **rinfo):
        '''
        Annotate a fileaddr node as being a relocation slot.

        Example:

            vw.addFileReloc(fa,'abs')

        '''
        node = self.formNodeByNoun('fileaddr',fa)
        self.setNodeProp(node,'fileaddr:reloc',rtype)

        for key,val in rinfo.items():
            self.setNodeProp(node,'fileaddr:reloc:%s' % key, val)

    def formFileInst(self, filehash, ra, inst):
        '''
        Create a node for the given ra and apply the "inst" data model.
        '''
        mnem = inst.mnem()
        size = inst.size()

        node = self.formFileAddr(filehash,ra)

    def getVivCpu(self, view=None, arch=None, **opts):
        '''
        Construct a vivisect.hal.Cpu backed by a VivView.

        The VivView is used to map various VivWorkspace files to
        memory locations and is then used as the Memory object for
        a Cpu.

        Example:
            cpu = vw.getVivCpu()

        '''
        if view == None:
            view = self.getVivView()

        if arch == None:
            arch = self.getVivConfig('arch')

        cpu = v_cpu.getArchCpu(arch,**opts)

        for mmap in view.getMemoryMaps():
            cpu.addMemoryMap(mmap)

        return cpu

    def getVivView(self, basemaps=None):
        '''
        Construct a VivView to represent files mapped at specific addresses.

        The VivView class implements the vivisect.hal.memory.Memory
        interface in order to provide virtual address based access to
        VivWorkspace files.

        The "basemaps" dictionary specifies <filehash>:<baseaddr> mappings
        ( and will also map <libname>:<baseaddr> if the libname is uniq
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
            for fnode in self.getNodesByProp('file'):
                filehash = fnode[1].get('file')
                view.loadVivFile(filehash)
            return view

        for filehash,baseaddr in basemaps.items():
            node = self.getNodeByNoun('file',filehash)
            if node == None:
                nodes = self.getNodesByProp('file:libname',filehash)
                if len(nodes) == 1:
                    node = nodes[0]

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
        return [ n[1].get('file') for n in self.getNodesByProp('file') ]

    def getFileMaps(self, filehash):
        '''
        Return a list of (ra,perm,bytes) tuples for the a file by hash.
        '''
        ret = []
        for node in self.getNodesByProp('filemap:file',valu=filehash):
            ra = node[1].get('filemap:ra')
            perm = node[1].get('filemap:perm')
            init = node[1].get('filemap:init')
            ret.append( tufo(ra, perm=perm, init=init) )
        return ret

    #def getFileSyms(self, filehash):
    #def getFileRelocs(self, filehash):

    def _ctor_file(self, noun, valu, **props):
        props.setdefault('file:arch','')
        props.setdefault('file:format','')
        props.setdefault('file:libname','')
        props.setdefault('file:platform','')
        props.setdefault('file:origpath','')
        props.setdefault('file:baseaddr',None)
        return self._ctor_node(noun, valu, **props)

    def _ctor_filemap(self, noun, valu, **props):
        props['filemap:ra'] = valu[1]
        props['filemap:file'] = valu[0]
        props.setdefault('filemap:perm',0)
        props.setdefault('filemap:init',b'')
        return self._ctor_node(noun, valu, **props)

    def _ctor_fileaddr(self, noun, valu, **props):
        props['fileaddr:ra'] = valu[1]
        props['fileaddr:file'] = valu[0]
        return self._ctor_node(noun, valu, **props)

    def _ctor_filefunc(self, noun, valu, **props):
        props['filefunc:ra'] = valu[1]
        props['filefunc:file'] = valu[0]

        # give the fileaddr node a hint about filefunc
        node = self.formNodeByNoun('fileaddr',valu)
        self.setNodeProp(node,'fileaddr:cast:func',1)

        return self._ctor_node(noun, valu, **props)

    def _dtor_filefunc(self, node):
        fa = node[1].get('filefunc')

        fanode = self.getNodeByNoun('fileaddr',fa)
        if fanode != None:
            self.delNodeProp(fanode,'fileaddr:cast:func')

        return self._dtor_node(node)

