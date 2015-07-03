"""
Similar to the vivisect.mach.memory subsystem, this is a unified
way to access information about objects which contain registers
"""
import vivisect.lib.bits as v_bits
import synapse.event.dist as s_dist

class Registers(s_dist.EventDist):

    def __init__(self, regdef):
        s_dist.EventDist.__init__(self)

        self._rctx_regdef = regdef
        self._rctx_cached = True
        self._rctx_cachecb = None

        self._rctx_vals = {}
        self._rctx_dirty = False
        self._rctx_sizes = {}
        self._rctx_setters = {}
        self._rctx_getters = {}

        # this is ( believe it or not ) a speed hack...
        for reg,size in regdef.get('regs'):
            self._init_reg(reg,size)

        for reg,real,shift,size in regdef.get('metas'):
            self._init_metareg(reg,real,shift,size)

        for reg,real in regdef.get('aliases'):
            self._rctx_setters[reg] = self._rctx_setters[real]
            self._rctx_getters[reg] = self._rctx_getters[real]

    def getpc(self):
        '''
        Terse method to return the "program counter" for this architecture.
        '''
        return self.get('_pc')

    def getsp(self):
        '''
        Terse method to return the "stack pointer" for this architecture.
        '''
        return self.get('_sp')

    def sizeof(self, reg):
        '''
        Returns the size (in bits) of the given register
        '''
        return self._rctx_sizes.get(reg)

    def _init_reg(self, reg, size):

        def getreg():
            return self._rctx_vals.get(reg)
        def setreg(v):
            self._rctx_vals[reg] = v & v_bits.bitmasks[size]
            return v
        self._rctx_vals[reg] = 0
        self._rctx_sizes[reg] = size
        self._rctx_getters[reg] = getreg
        self._rctx_setters[reg] = setreg

    def _init_metareg(self, reg, real, shift, size):
        gter = self._rctx_getters.get(real)
        ster = self._rctx_setters.get(real)
        mask = v_bits.bitmasks[size]
        def getmeta():
            return (gter() >> shift) & mask
        def setmeta(valu):
            cur = gter() & ~(mask << shift)
            return ster(cur | ((valu & mask) << shift))
        self._rctx_sizes[reg] = size
        self._rctx_getters[reg] = getmeta
        self._rctx_setters[reg] = setmeta

    def dirty(self):
        return self._rctx_dirty

    def get(self, reg):
        '''
        Get a register value.

        Example:
            a = regs.get('eax')

        NOTE: "reg" may be a meta reg or alias.
        '''
        if not self._rctx_cached:
            self._load_cache()

        gter = self._rctx_getters.get(reg)
        if gter == None:
            return None
        return gter()

    def set(self, reg, valu):
        '''
        Set a register value.

        Example:
            regs.set('ebx',30)

        Returns:
            The new ( unsigned / masked to width ) value.

        '''
        if not self._rctx_cached:
            self._load_cache()

        self._rctx_dirty = True
        ret = self._rctx_setters[reg](valu)
        self.fire('cpu:reg:set', reg=reg, valu=ret)
        return ret

    def __iter__(self):
        for r,v in self._rctx_vals.items():
            yield r,v

    def __getitem__(self, reg):
        return self.get(reg)

    def __setitem__(self, reg, val):
        return self.set(reg,val)

    def __getattr__(self, reg):
        return self.get(reg)

    def _load_cache(self):
        self.load( self._rctx_cachecb() )

    def save(self, clean=True):
        self._rctx_dirty = not clean
        return dict(self._rctx_vals)

    def load(self, regs, dirty=False):
        self._rctx_dirty = dirty
        self._rctx_cached = True
        self._rctx_vals.update(regs)

    def oncache(self, cb):
        self._rctx_cached = False
        self._rctx_cachecb = cb

    def clear(self):
        '''
        Clear the register cache and force a load on the next access.
        '''
        self._rctx_cached = False

