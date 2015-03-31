import itertools

import vivisect.hal.instr as v_instr
import vivisect.lib.disasm as v_disasm
import vivisect.hal.memory as v_memory
import vivisect.hal.registers as v_regs

import vivisect.symboliks.symstate as v_symstate

import synapse.event.dist as s_evtdist
import synapse.lib.apistack as s_apistack

from vertex.lib.common import tufo

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
        'mode':None,        # nearly ever CPU is "modal" in some form
        'threads':1,        # how many execution contexts to create (threads/cores)
        'regdef':regdef(),  # registers etc...
        'ptrsize':4,        # how wide is a pointer ( default to 32 bit )
        'bigend':False,     # set to true for big-endian CPUs/modes
        'aliases':(),       # aliases for the arch name
        'defcalls':{},
    }
    a.update(kwargs)
    return a


class Cpu(s_apistack.ApiStack,v_symstate.SymbolikCpu,v_memory.Memory):
    '''
    The Cpu class implements the synthesis of the various machine APIs.

    At it's core, the Cpu is the base class from which others such
    as tracers / emulators should extend.  It abstracts the idea of
    threads to manage multiple register contexts as well as memory.
    '''
    instrclass = v_instr.Instr

    def __init__(self, **cpuopts):
        s_apistack.ApiStack.__init__(self)
        v_memory.Memory.__init__(self)

        self._cpu_info = self._init_cpu_info()
        self._cpu_info.update(cpuopts)

        self._cpu_mem = self._init_cpu_mem()
        self._cpu_regs = None
        self._cpu_decoder = self._init_cpu_decoder()


        self._cpu_thread = None
        self._cpu_threads = {}

        self._cpu_libs = {}

        self._init_threads()
        self._initCpuEvents()

        # now that we have everything, mix in the symbolik cpu
        v_symstate.SymbolikCpu.__init__(self)

        # every CPU probably needs a symbolik state builder
        self.symb = v_symstate.StateBuilder(self)

        for mmap in cpuopts.get('mmaps',()):
            self._cpu_mem._init_mmap(mmap)

        # process a few "universal" cpu options
        #addmap = cpuopts.get('addmap')  # (addr,perm,size) to add memory map
        #if addmap != None:
            #mapaddr,mapperm,mapsize = addmap
            #mmap = self.mem().alloc( mapsize, perm=mapperm, addr=mapaddr )
            #self.addMemoryMap(mapaddr,mapperm,'addmap',b'\x00' * mapsize)

        #addbytes = cpuopts.get('addbytes')
        #if addbytes:
            #mapaddr,mapperm,mapbytes = addbytes
            ## FIMXE maybe do some page aligning?
            #self.addMemoryMap(mapaddr,mapperm,'addbytes',mapbytes)

    #def initLib(self, addr, **libinfo):
    #def finiLib(self, lib):

    def getSymBuilder(self):
        '''
        Retrieve a Symbolik StateBuilder for the CPU.

        See: vivisect.symboliks.symstate.StateBuilder()
        '''
        return v_symstate.StateBuilder(self)

    def getCpuInfo(self, prop, default=None):
        '''
        Retrieve a value from the cpuinfo dictionary.
        '''
        return self._cpu_info.get(name,default)

    def setCpuInfo(self, prop, valu):
        '''
        Set a value in the cpuinfo dictionary.
        '''
        self._cpu_info[name] = valu
        self.fire('cpu:info:set', cpu=self, prop=prop, valu=valu)
        self.fire('cpu:info:set:%s' % prop, cpu=self, valu=valu)

    def _init_cpu_info(self):
        '''
        Initialize a new cpuinfo dict for the CPU.

        This is present to allow individual implementations
        to over-ride and add elements to the cpuinfo() defaults.
        '''
        return cpuinfo()

    #def setThreadInfo(self, tid, prop, valu):
        #'''
        #Set a prop:valu key in the info dictionary for the given thread.

        #Example:

            # if we're debugging windows...
            #cpu.setThreadInfo(tid, 'teb', addr)

        #'''
        #thread = self._cpu_threads.get(tid)
        #if thread == None:
            #raise InvalidThread(tid)

        #thread[1][prop] = valu

    def _init_cpu_decoder(self):
        return v_disasm.Decoder()

    def _initCpuEvents(self):
        pass

    def _init_threads(self):
        for i in range( self._cpu_info.get('threads',1) ):
            thread = tufo(i)
            self._init_thread(thread)

    def __getattr__(self, name):

        ret = self._cpu_regs.get(name)

        # act like our regs/mem if requested...
        #ret = getattr(self._cpu_regs,name,None)
        if ret != None:
            return ret

        #ret = getattr(self._cpu_mem,name,None)
        #if ret != None:
            #return ret

        raise AttributeError(name)

    def __getitem__(self, key):
        if isinstance(key,slice):
            return self._cpu_mem.peek(key.start,key.stop-key.start)
        return self._cpu_regs.get(key)

    def __setitem__(self, key, val):
        if isinstance(key,slice):
            return self._cpu_mem.poke(key.start,val)
        return self._cpu_regs.set(key,val)

    #def mem(self):
        #return self._cpu_mem

    def reg(self, name, valu=None):
        '''
        Get/Set a register (by name) for the current Cpu thread.

        Example:

            eax = cpu.reg('eax')
            cpu.reg('eax', eax + 20)

        '''
        if valu != None:
            return self._cpu_regs.set(name,valu)

        return self._cpu_regs.get(name)

    def sizeof(self, name):
        '''
        Return the size of a register for the current Cpu thread.

        Example:

            width = cpu.sizeof('ebx')

        '''
        return self._cpu_regs.sizeof(name)

    def getpc(self):
        '''
        Return the program counter for the current Cpu thread.

        Example:

            pc = cpu.getpc()

        '''
        return self._cpu_regs.getpc()

    def getsp(self):
        '''
        Return the stack counter for the current Cpu thread.

        Example:

            sp = cpu.getsp()

        '''
        return self._cpu_regs.getsp()

    # memory wrapper API

    def _mem_peek(self, addr, size):
        return self._cpu_mem.peek(addr,size)

    def _mem_poke(self, addr, byts):
        return self._cpu_mem.poke(addr,byts)

    def _mem_mmaps(self):
        return self._cpu_mem.mmaps()

    def _mem_mmap(self, addr):
        return self._cpu_mem.mmap(addr)

    def _mem_alloc(self, size, **info):
        return self._cpu_mem.alloc(size, **info)

    def _mem_free(self, addr):
        return self._cpu_mem.free(addr)

    def _init_cpu_mem(self):
        return v_memory.Memory()


    def _init_regs(self):
        regdef = self._cpu_info.get('regdef')
        regs = v_regs.Registers(regdef)
        regs.link( self )
        return regs

    def _init_thread(self, thread):
        tid,info = thread

        if info.get('regs') == None:
            info['regs'] = self._init_regs()

        if info.get('mem') == None:
            info['mem'] = self._cpu_mem

        self._cpu_threads[tid] = thread
        self._cpu_setthread(thread)

        return thread

    def _fini_thread(self, thread):
        return self._cpu_threads.pop(thread[0], None)

    def thread(self, tid=None):
        '''
        Retrieve the thread tuple (tid,tinfo) for the current or specified thread.

        Example:

            thread = cpu.thread(tid)

        '''
        if tid == None:
            return self._cpu_thread
        return self._cpu_threads.get(tid)

    def threads(self):
        '''
        Retrieve a list of (tid,tinfo) tuples for the current threads.

        Example:

            for tid,tinfo in cpu.threads():
                print('thread: %d' % (tid,))

        '''
        return list(self._cpu_threads.values())

    def switch(self, tid):
        '''
        Switch the Cpu context to the specified thread by id.

        Example:

            cpu.switch(tid)

            # get eax from thread id "tid"
            eax = cpu.reg('eax')

        '''
        thread = self._cpu_threads.get(tid)
        if thread == None:
            raise InvalidThread(tid)

        self._cpu_setthread( thread )
        return thread

    def _cpu_setthread(self, thread):
        self._cpu_thread = thread

        self._cpu_mem = thread[1].get('mem')
        self._cpu_regs = thread[1].get('regs')

    def snapshot(self):
        '''
        Return an opaque "snapshot" for the CPU which can later be restored.

        Example:

            cpu.reg('eax', 10)
            cpu.alloc(4096, addr=0x41410000)

            snap = cpu.snapshot()

            cpu.poke( 0x41410000, b'VISI' )
            cpu.reg('eax', 20)

            cpu.restore(snap)

            # eax is back to 10 and bytes at 0x41410000 are reverted

        '''
        regs = self._cpu_regs.save()
        mem = self._cpu_mem.snapshot()
        return {'mem':mem,'regs':regs}

    def restore(self, snap):
        '''
        Restore CPU state from a snapshot from snapshot()

        Notes:

            * see Cpu.snapshot() for examples/notes

        '''
        self._cpu_regs.load( snap.get('regs') )
        self._cpu_mem.restore( snap.get('mem') )

    def disasm(self, addr, **disinfo):
        '''
        Decode in instruction *tuple* from the given addr.
        ( see cpu.instr() to get an Instr object )

        Returns:
            (mnem,opers,info) or None

        Example:
            i = cpu.disasm(0x41410000)
        '''
        offset,bytez = self._cpu_mem.mbuf(addr)

        inst = self._cpu_decoder.parse(bytez,offset=offset,addr=addr,**disinfo)
        if inst == None:
            return None

        instinfo = inst[2]

        instinfo['addr'] = addr
        instinfo['bytes'] = bytez
        instinfo['offset'] = offset

        return self.instrclass(self,inst)

class UnknownArch(Exception):pass
class InvalidThread(Exception):pass

cpuctors = {}
def addArchCpu(name,callback):
    '''
    Register a CPU constructor by an arch name.

    Example:

        import vivisect.hal.cpu as v_cpu

        class MyCpu(v_cpu.Cpu):
            ...

        v_cpu.addArchCpu('myarch',MyCpu)

    Notes:

        * arch "variants" should be named <arch>.<exten>

    '''
    cpuctors[name] = callback

def getArchList():
    '''
    Retrieve a list of (name,ctor) for supported arch Cpus.

    Example:

        import vivisect.hal.cpu as v_cpu

        for name,ctor in v_cpu.getArchList():
            print('arch: %s' % (name,))

    '''
    return cpuctors.items()

def getArchCpu(name, **opts):
    '''
    Construct a Cpu class for the given architecture by name.

    Example:

        import vivisect.hal.cpu as v_cpu

        cpu = v_cpu.getArchCpu('i386')

    Notes:

        * extended **opts are passed to Cpu constructor.

    '''
    ctor = cpuctors.get(name)
    if ctor == None:
        raise UnknownArch(name)
    return ctor(**opts)

