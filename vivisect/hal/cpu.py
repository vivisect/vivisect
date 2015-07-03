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

        self._cpu_info = self._initCpuInfo()
        self._cpu_info.update(cpuopts)

        self._cpu_mem = self._initCpuMemory()
        self._cpu_regs = None
        self._cpu_decoder = self._initCpuDecoder()


        self._cpu_locals = CpuLocals(self)
        self._cpu_thread = None
        self._cpu_threads = {}

        self._cpu_libs = {}
        self._cpu_libs_byname = {}

        self._initThreads()

        # now that we have everything, mix in the symbolik cpu
        v_symstate.SymbolikCpu.__init__(self)

        # every CPU probably needs a symbolik state builder
        self.symb = v_symstate.StateBuilder(self)

        for mmap in cpuopts.get('mmaps',()):
            self._cpu_mem.addMemoryMap(mmap)

    def print(self, msg, **info):
        '''
        Fire a cpu:print event to display msg on interactive interfaces.

        Example:

            cpu.print('woot!', blah=10)

        '''
        self.fire('cpu:print', msg=str(msg), **info)

    def error(self, msg, **info):
        '''
        Fire a cpu:error event to notify interactive interfaces we have a problem.

        Example:

            try:
                dostuff( cpu )
            except Exception as e:
                cpu.error(e)

        '''
        self.fire('cpu:error', msg=str(msg), **info)

    def libs(self):
        '''
        Returns a list of the loaded libraries in the current Cpu.

        Example:

            for lib in cpu.libs():
                print('lib: %s' % (lib[1].get('path'),))

        Note:

            * "loaded libraries" includes the main executable image.

        '''
        return list(self._cpu_libs.values())

    def getLibByName(self, name):
        '''
        Return a lib tuple by name.

        Example:

            libc = cpu.getLibByName('c')
            print('libc at: 0x%.8x' % ( libc[0], ))
            print('libc path: %s' % ( libc[1].get('path'),))

        '''
        return self._cpu_libs_byname.get(name)


    def eval(self, expr):
        '''
        Evaluate an expression containing  regs/symbols/libs.

        Example:

            addr = cpu.eval('kernel32 + eax')

        Notes:

            * returns None on failure to resolve a symbol

        '''
        try:
            return eval( expr, {}, self._cpu_locals )
        except LocalNotFound as e:
            return None

    def getSymBuilder(self):
        '''
        Retrieve a Symbolik StateBuilder for the CPU.

        See: vivisect.symboliks.symstate.StateBuilder()
        '''
        return v_symstate.StateBuilder(self)

    def _initCpuInfo(self):
        '''
        Initialize a new cpuinfo dict for the CPU.

        This is present to allow individual implementations
        to over-ride and add elements to the cpuinfo() defaults.
        '''
        return cpuinfo()

    def _initCpuDecoder(self):
        return v_disasm.Decoder()

    def _initThreads(self):
        # default impl for spinning up initial threads
        for i in range( self._cpu_info.get('threads',1) ):
            thread = tufo(i)
            self._initCpuThread(thread)

    def _initLib(self, lib):
        # initialize an (addr,info) lib tufo
        lib[1].setdefault('parsed', False)

        self._cpu_libs[ lib[0] ] = lib

        name = lib[1].get('name')
        if name != None:
            self._cpu_libs_byname[name] = lib

        return lib

    def _finiLib(self, lib):
        # tear down an (addr,info) lib tufo
        self._cpu_libs.pop(lib[0], None)

        name = lib[1].get('name')
        if name != None:
            self._cpu_libs_byname.pop(name, None)

        return lib

    def __getattr__(self, name):

        ret = self._cpu_regs.get(name)
        if ret != None:
            return ret

        raise AttributeError(name)

    def __getitem__(self, key):
        if isinstance(key,slice):
            return self._cpu_mem.readMemory(key.start,key.stop-key.start)
        return self._cpu_regs.get(key)

    def __setitem__(self, key, val):
        if isinstance(key,slice):
            return self._cpu_mem.writeMemory(key.start,val)
        return self._cpu_regs.set(key,val)


    def getReg(self, name):
        '''
        Get a register (by name) for the current Cpu thread.

        Example:

            eax = cpu.getReg('eax')

        '''
        return self._cpu_regs.get(name)

    def setReg(self, name, valu):
        '''
        Set a register (by name) for the current Cpu thread.

        Example:

            eax = cpu.getReg('eax')
            cpu.setReg('eax', eax + 20)

        '''
        return self._cpu_regs.set(name,valu)

    def setRegsKw(self, **regs):
        '''
        Syntax sugar for setting several registers as once by kwargs.

        Example:

            cpu.setRegsKw(eax=20,ebx=30)

        '''
        for name,valu in regs.items():
            self.setReg(name,valu)

    def getRegSize(self, name):
        '''
        Return the size (in bits) of a register for the current Cpu.

        Example:

            width = cpu.getRegSize('ebx')

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

    def _readMemory(self, addr, size):
        return self._cpu_mem.readMemory(addr,size)

    def _writeMemory(self, addr, byts):
        return self._cpu_mem.writeMemory(addr,byts)

    def _getMemoryMaps(self):
        return self._cpu_mem.getMemoryMaps()

    def _getMemoryMap(self, addr):
        return self._cpu_mem.getMemoryMap(addr)

    def _allocMemory(self, size, **info):
        return self._cpu_mem.allocMemory(size, **info)

    def _freeMemory(self, addr):
        return self._cpu_mem.freeMemory(addr)

    def _addMemoryMap(self, mmap):
        return self._cpu_mem.addMemoryMap(mmap)

    def _delMemoryMap(self, mmap):
        return self._cpu_mem.delMemoryMap(mmap)

    def _initCpuMemory(self):
        return v_memory.Memory()

    def _initCpuRegs(self):
        regdef = self._cpu_info.get('regdef')
        regs = v_regs.Registers(regdef)
        regs.link( self )
        return regs

    def _initCpuThread(self, thread):
        tid,info = thread

        if info.get('regs') == None:
            info['regs'] = self._initCpuRegs()

        if info.get('mem') == None:
            info['mem'] = self._cpu_mem

        self._cpu_threads[tid] = thread
        self._cpu_setthread(thread)

        return thread

    def _fini_thread(self, thread):
        return self._cpu_threads.pop(thread[0], None)

    def thread(self, tid=None):
        '''
        Retrieve the thread tuple (tid,info) for the current or specified thread.

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

    def switchThread(self, tid):
        '''
        Switch the Cpu context to the specified thread by id.

        Example:

            cpu.switchThread(tid)

            # get eax from thread id "tid"

            eax = cpu.getReg('eax')

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

    def getCpuSnap(self):
        '''
        Return an opaque "snapshot" for the CPU which can later be restored.

        Example:

            cpu.setReg('eax', 10)
            cpu.initMemoryMap(0x41410000, 4096)

            snap = cpu.getCpuSnap()

            cpu.writeMemory( 0x41410000, b'VISI' )
            cpu.setReg('eax', 20)

            cpu.setCpuSnap(snap)

            # eax is back to 10 and bytes at 0x41410000 are reverted

        '''
        regs = self._cpu_regs.save()
        mem = self._cpu_mem.getMemorySnap()
        return {'mem':mem,'regs':regs}

    def setCpuSnap(self, snap):
        '''
        Restore CPU state from a snapshot from getCpuSnap()

        Notes:

            * see Cpu.getCpuSnap() for examples/notes

        '''
        self._cpu_regs.load( snap.get('regs') )
        self._cpu_mem.setMemorySnap( snap.get('mem') )

    def disasm(self, addr, **disinfo):
        '''
        Decode in instruction *tuple* from the given addr.
        ( see cpu.instr() to get an Instr object )

        Example:

            i = cpu.disasm(0x41410000)

        '''
        offset,bytez = self._cpu_mem.getMemBuf(addr)

        inst = self._cpu_decoder.parse(bytez,offset=offset,addr=addr,**disinfo)
        if inst == None:
            return None

        instinfo = inst[2]

        instinfo['addr'] = addr
        instinfo['bytes'] = bytez
        instinfo['offset'] = offset

        return self.instrclass(self,inst)

class LibLocals(int):

    def _set_cpu_lib(self, cpu, lib):
        self.cpu = cpu
        self.lib = lib

    def __getattr__(self, name):
        libname = self.lib[1].get('name')
        sym = self.cpu.libsym(libname, name)
        return sym[1].get('addr')

class CpuLocals:
    '''
    A dictionary like object for use in expression evaluation.
    '''
    def __init__(self, cpu):
        self.cpu = cpu

    def __getitem__(self, name):

        reg = self.cpu.getReg(name)
        if reg != None:
            return reg

        lib = self.cpu.getLibByName(name)
        if lib != None:
            loc = LibLocals(lib[0])
            loc._set_cpu_lib(self.cpu, lib)
            return loc

        meth = getattr(self.cpu, name, None)
        if meth != None:
            return meth

        raise LocalNotFound(name)

class UnknownArch(Exception):pass
class InvalidThread(Exception):pass
class LocalNotFound(Exception):pass

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
          ( ex, addArchCpu('i386.realmode', RealModeCpu ) )

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

def getArchCpu(name, **info):
    '''
    Construct a Cpu class for the given architecture by name.

    Example:

        import vivisect.hal.cpu as v_cpu

        cpu = v_cpu.getArchCpu('i386')

    Notes:

        * extended **info are passed to Cpu constructor.

    '''
    ctor = cpuctors.get(name)
    if ctor == None:
        raise UnknownArch(name)
    return ctor(**info)

