import itertools

import vivisect.hal.instr as v_instr
import vivisect.hal.memory as v_mem
import vivisect.lib.disasm as v_disasm
import vivisect.hal.registers as v_regs

import vivisect.symboliks.symstate as v_symstate

import synapse.event.dist as s_evtdist
import synapse.lib.apistack as s_apistack

#class TerseApi:

    #def getpc(self,tid=None):
        #return self.regs.getpc()

    #def getsp(self,tid=None):
        #return self.regs.getsp()

    #def getregs(self,tid=None):
        #return self.regs

    #def core(self, idx):
        #return self.getCpuCore(idx)

    #def getreg(self,reg):
        #return self.regs.get(reg)

    #def setreg(self,reg,val):
        #return self.regs.set(reg,val)

    #def getmem(self, va, size):
        #return self.mem.readMemory(va,size)

    #def setmem(self, va, bytez):
        #return self.mem.writeMemory(va,size)

def regdef(**kwargs):
    ret = {
        'docs':{},      # name:descr
        'regs':[],      # (name,width) tuples
        'metas':[],     # (name, realname, rshift, rmask)
        'aliases':[],   # (alias,realname)
    }
    ret.update(kwargs)
    return ret

def cpuinfo(**kwargs):
    a = {
        'nop':None,
        'brk':None,
        'cores':1,
        'mode':None,        # nearly ever CPU is "modal" in some form
        'regdef':regdef(),  # registers etc...
        'ptrsize':4,        # how wide is a pointer ( default to 32 bit )
        'bigend':False,     # set to true for big-endian CPUs/modes
        'aliases':(),       # aliases for the arch name
        'defcalls':{},
    }
    a.update(kwargs)
    return a


class Cpu(s_apistack.ApiStack,s_evtdist.EventDist,v_symstate.SymbolikCpu):
    '''
    The Cpu class implements the synthesis of the various machine APIs.

    At it's core, the Cpu is the base class from which others such
    as tracers / emulators should extend.  It abstracts the idea of
    threads/cores to manage multiple register contexts as well as memory.
    '''
    instrclass = v_instr.Instr

    def __init__(self, **cpuopts):
        s_evtdist.EventDist.__init__(self)
        s_apistack.ApiStack.__init__(self)
        v_symstate.SymbolikCpu.__init__(self)

        self.cpuinfo = self.initCpuInfo()
        self.cpuinfo.update(cpuopts)

        self.mem = None
        self.regs = None
        self.decoder = None

        self.cpucores = {}

        self.initCpuMem()
        self.initCpuCores()
        self.initCpuEvents()
        self.initInstrDecoder()

        # every CPU probably needs a symbolik state builder
        self.symb = v_symstate.StateBuilder(self)

        # process a few "universal" cpu options
        addmap = cpuopts.get('addmap')  # (addr,perm,size) to add memory map
        if addmap != None:
            mapaddr,mapperm,mapsize = addmap
            self.addMemoryMap(mapaddr,mapperm,'addmap',b'\x00' * mapsize)

        addbytes = cpuopts.get('addbytes')
        if addbytes:
            mapaddr,mapperm,mapbytes = addbytes
            # FIMXE maybe do some page aligning?
            self.addMemoryMap(mapaddr,mapperm,'addbytes',mapbytes)

        #self.synAddHandler('cpu:info:set:cores',self._slot_set_cores)
        #self.synAddHandler('cpu:info:set:regdef',self._slot_set_regdef)

    def getCpuInfo(self, prop, default=None):
        '''
        Retrieve a value from the cpuinfo dictionary.
        '''
        return self.cpuinfo.get(name,default)

    def getSymBuilder(self):
        '''
        Retrieve a Symbolik StateBuilder for the CPU.

        See: vivisect.symboliks.symstate.StateBuilder()
        '''
        return v_symstate.StateBuilder(self)

    def setCpuInfo(self, prop, valu):
        '''
        Set a value in the cpuinfo dictionary.
        '''
        self.cpuinfo[name] = valu
        evtinfo = {'cpu':self,'prop':prop,'valu':valu}
        self.synFireEvent('cpu:info:set',cpuinfo)
        self.synFireEvent('cpu:info:set:%s' % prop,cpuinfo)

    def initCpuInfo(self):
        '''
        Initialize a new cpuinfo dict for the CPU.

        This is present to allow individual implementations
        to over-ride and add elements to the cpuinfo() defaults.
        '''
        return cpuinfo()

    def initInstrDecoder(self):
        self.decoder = v_disasm.Decoder()

    def initCpuEvents(self):
        pass

    def initCpuCores(self):
        for i in range( self.cpuinfo.get('cores',1) ):
            self.initCpuCore(i)

    def __getattr__(self, name):
        # act like our regs/mem if requested...
        ret = getattr(self.regs,name,None)
        if ret != None:
            return ret

        ret = getattr(self.mem,name,None)
        if ret != None:
            return ret

        raise AttributeError(name)

    def __getitem__(self, key):
        if isinstance(key,slice):
            return self.mem.readMemory(key.start,key.stop-key.start)
        return self.regs.get(key)

    def __setitem__(self, key, val):
        if isinstance(key,slice):
            return self.mem.writeMemory(key.start,val)
        return self.regs.set(key,val)

    def initCpuMem(self):
        # arch specific CPUs should override here...
        self.mem = v_mem.Memory()

    def initCpuRegs(self):
        regdef = self.cpuinfo.get('regdef')
        return v_regs.Registers(regdef)

    def initCpuCore(self, idx):
        '''
        Create and track an additional register context for the CPU.

        NOTE: this is also used to track threads in user-mode CPUs
        '''
        regs = self.initCpuRegs()
        regs.synAddHandler('*',self.synFireEvent)
        self.cpucores[idx] = regs
        self.setCpuRegs(regs)
        return regs

    def getCpuCore(self, idx):
        '''
        Retrieve the Registers object for a given CPU core by id.
        '''
        return self.cpucores.get(idx)

    def finiCpuCore(self, idx):
        '''
        Pop the Registers object assocated with core idx.

        Example:
            regs = cpu.finiCpuCore(0)

        NOTE: this is mostly used by debugger objects handling
              "threadexit" events.
        '''
        # FIXME switch to another core?
        regs = self.cpucores.pop(idx,None)
        return regs

    def getCpuCores(self):
        '''
        Get a list of (id,regs) tuples for the initialized CPU cores.
        '''
        return self.cpucores.items()

    def setCpuCore(self, idx):
        '''
        Select a CPU core (by id) to be the "current" register context.
        '''
        regs = self.cpucores.get(idx)
        if regs == None:
            raise Exception('Invalid CPU Core: %s' % idx)

        self.setCpuRegs(regs)
        return regs

    def setCpuMem(self, mem):
        '''
        Assign a Memory object to the CPU.
        '''
        self.mem = mem
        #self.synFireEventKw('cpu:mem:set',cpu=self,mem=mem)

    def getCpuMem(self):
        '''
        Return the current Memory object for the Cpu.
        '''
        return self.mem

    def setCpuRegs(self, regs):
        '''
        Assign a "current" Registers object to the CPU.

        FIXME modify current cpu core?
        '''
        self.regs = regs

    def getCpuRegs(self):
        '''
        Return the Registers object for the current Cpu context.
        '''
        return self.regs

    def snapshot(self):
        '''
        Return an opaque "snapshot" for the CPU which can later be restored.

        NOTE: cpu snapshots are *not* serializable/primitives.
        '''
        regs = self.regs.save()
        snap = (regs,self.mem)

        # setup a new "copy on write" memory object
        self.setCpuMem( v_mem.MemoryCache( self.mem ) )

        # FIXME support multiple cores...
        return snap

    def restore(self, snap):
        '''
        Restore CPU state from a snapshot from initCpuSnap.
        '''
        regs,mem = snap
        self.regs.load(regs)
        self.setCpuMem(mem)

    #def decode(self, addr, **disinfo):
    def disasm(self, addr, **disinfo):
        '''
        Decode in instruction *tuple* from the given addr.
        ( see cpu.instr() to get an Instr object )

        Returns:
            (mnem,opers,info) or None

        Example:
            i = cpu.disasm(0x41410000)
        '''
        offset,bytez = self.mem.getBytesDef(addr)

        inst = self.decoder.parse(bytez,offset=offset,addr=addr,**disinfo)
        if inst == None:
            return None

        instinfo = inst[2]

        instinfo['addr'] = addr
        instinfo['bytes'] = bytez
        instinfo['offset'] = offset

        return self.instrclass(self,inst)

class UnknownArch(Exception):pass

cpuctors = {}
def addArchCpu(name,callback):
    '''
    Register a CPU constructor by an arch name.

    NOTE: arch variants are free to register ctors as well.
          Use <name>.<variant> to allow for sorting etc.
          ie. addArchCpu('arm.v7', arm7cpu)
    '''
    cpuctors[name] = callback

def getArchList():
    '''
    Retrieve a list of (name,ctor) tuples.
    '''
    return cpuctors.items()

def getArchCpu(name, **kwargs):
    '''
    Construct a Cpu class for the given architecture by name.
    '''
    ctor = cpuctors.get(name)
    if ctor == None:
        raise UnknownArch(name)
    return ctor(**kwargs)

