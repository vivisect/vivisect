'''
All the code related to vtrace process snapshots and TraceSnapshot classes.
'''
import copy
import pickle
import logging

import envi
import vtrace
import vtrace.platforms.base as v_base

logger = logging.getLogger(__name__)


class TraceSnapshot(vtrace.Trace, v_base.TracerBase):
    '''
    A trace snapshot is similar to a traditional "core file" except that
    you may also have memory only snapshots that are never written to disk.
    '''
    def __init__(self, snapdict):

        self.s_snapcache = {}
        self.s_snapdict = snapdict

        # a seperate parser for each version...
        if snapdict['version'] == 1:
            self.s_version = snapdict['version']
            self.s_threads = snapdict['threads']
            self.s_regs = snapdict['regs']
            self.s_maps = snapdict['maps']
            self.s_mem = snapdict['mem']
            self.metadata = snapdict['meta']
            self.s_stacktrace = snapdict['stacktrace']
            self.s_exe = snapdict['exe']
            self.s_fds = snapdict['fds']
            self.localvars = snapdict.get('vars', {})
        else:
            raise Exception('ERROR: Unknown snapshot version!')

        # In the ghetto!
        archname = self.metadata.get('Architecture')
        envi.stealArchMethods(self, archname)

        vtrace.Trace.__init__(self)
        v_base.TracerBase.__init__(self)
        # This will re-init meta... *sigh* set it back...
        self.metadata = snapdict['meta']

        # Steal the reg defs of the first thread
        rinfo = list(self.s_regs.items())[0][1]
        self.setRegisterInfo(rinfo)

        #FIXME hard-coded page size!
        self.s_map_lookup = {}
        for mmap in self.s_maps:
            for i in range(mmap[0], mmap[0] + mmap[1], 4096):
                self.s_map_lookup[i] = mmap

        # Lets get some symbol resolvers created for our libraries
        #for fname in self.getNormalizedLibNames():
            #subres = e_resolv.FileSymbol(fname, 

        self.running = False
        self.attached = True
        # So that we pickle
        self.bplock = None
        self.thread = None

    def saveToFd(self, fd):
        '''
        Save this snapshot to the given file like object
        for later reloading...
        '''
        pickle.dump(self.s_snapdict, fd)

    def saveToFile(self, filename):
        '''
        Save a snapshot to file for later reading in...
        '''
        with open(filename, 'wb') as f:
            self.saveToFd(f)

    def getMemoryMap(self, addr):
        if self.getMeta('Architecture') == 'amd64':
            base = addr & 0xfffffffffffff000
        else:
            base = addr & 0xfffff000

        return self.s_map_lookup.get(base, None)

    def platformGetFds(self):
        return self.s_fds

    def getExe(self):
        return self.s_exe

    def getStackTrace(self):
        tid = self.getMeta('ThreadId')
        tr = self.s_stacktrace.get(tid, None)
        if tr is None:
            raise Exception('ERROR: Invalid thread id specified')
        return tr

    def platformGetRegCtx(self, thrid):
        rinfo = self.s_regs.get(thrid)
        ctx = self.archGetRegCtx()
        ctx.setRegisterInfo(rinfo)
        return ctx

    def platformGetMaps(self):
        return self.s_maps

    def platformGetThreads(self):
        return self.s_threads

    def platformReadMemory(self, address, size):
        map = self.getMemoryMap(address)
        if map is None:
            raise Exception("ERROR: platformReadMemory says no map for 0x%.8x" % address)
        offset = address - map[0]  # Base address
        mapbytes = self.s_mem.get(map[0], None)
        if mapbytes is None:
            raise vtrace.PlatformException("ERROR: Memory map at 0x%.8x is not backed!" % map[0])
        if len(mapbytes) == 0:
            raise vtrace.PlatformException("ERROR: Memory Map at 0x%.8x is backed by ''" % map[0])

        ret = mapbytes[offset:offset+size]
        rlen = len(ret)
        # We may have a cross-map read, just recurse for the rest
        if rlen != size:
            ret += self.platformReadMemory(address+rlen, size-rlen)
        return ret

    def platformWriteMemory(self, address, bytes):
        map = self.getMemoryMap(address)
        if map is None:
            raise Exception("ERROR: platformWriteMemory says no map for 0x%.8x" % address)
        offset = address - map[0]
        mapbytes = self.s_mem[map[0]]
        self.s_mem[map[0]] = mapbytes[:offset] + bytes + mapbytes[offset+len(bytes):]

    def platformDetach(self):
        pass

    def platformParseBinary(self, *args):
        logger.warning('FIXME FAKE PLATFORM PARSE BINARY: %s', args)

    # Over-ride register *caching* subsystem to store/retrieve
    # register information in pure dictionaries
    def cacheRegs(self, threadid):
        pass

    # FIXME regs in snapshots are broke...

    def syncRegs(self):
        pass


def loadSnapshot(filename):
    '''
    Load a vtrace process snapshot from a file
    '''
    with open(filename, 'rb') as f:
        return TraceSnapshot(pickle.load(f))


def takeSnapshot(trace):
    '''
    Take a snapshot of the process from the current state and return
    a reference to a tracer which wraps a "snapshot" or "core file".
    '''
    sd = dict()
    orig_thread = trace.getMeta("ThreadId")

    regs = dict()
    stacktrace = dict()

    for thrid, tdata in trace.getThreads().items():
        ctx = trace.getRegisterContext(thrid)
        reginfo = ctx.getRegisterInfo()
        regs[thrid] = reginfo
        try:
            stacktrace[thrid] = trace.getStackTrace()
        except Exception as e:
            logger.warning("Failed to get stack trace for thread 0x%.8x (%s)", thrid, e)

    mem = dict()
    maps = []
    for base, size, perms, fname in trace.getMemoryMaps():
        try:
            mem[base] = trace.readMemory(base, size)
            maps.append((base, size, perms, fname))
        except Exception as msg:
            logger.warning("Can't snapshot memmap at 0x%.8x (%s)", base, msg)

    # If the contents here change, change the version...
    sd['version'] = 1
    sd['threads'] = trace.getThreads()
    sd['regs'] = regs
    sd['maps'] = maps
    sd['mem'] = mem
    sd['meta'] = copy.deepcopy(trace.metadata)
    sd['stacktrace'] = stacktrace
    sd['exe'] = trace.getExe()
    sd['fds'] = trace.getFds()
    sd['vars'] = trace.localvars

    return TraceSnapshot(snapdict=sd)
