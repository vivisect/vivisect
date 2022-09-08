'''
A home for the vdb specific memory renderers.
'''
import logging

import envi
import envi.common as e_common
import envi.memcanvas as e_canvas
import envi.memcanvas.renderers as e_canvas_rend

import vivisect.impapi as viv_impapi

import vtrace


logger = logging.getLogger(__name__)

class OpcodeRenderer(e_canvas.MemoryRenderer):

    def __init__(self, trace, arch=envi.ARCH_DEFAULT):
        self.arch = arch
        self.emu_cache = {}  # arch_num: emu instance
        self.pwidth = trace.getPointerSize()
        self.pformat = '0x%%.%dx' % (self.pwidth * 2)

    def _getOpcodePrefix(self, trace, va, op):
        regs = trace.getRegisters()
        regs = {rval: rname for (rname, rval) in regs.items() if rval != 0}

        bp = trace.getBreakpointByAddr(va)
        if bp is not None:
            return ('bp[%d]' % bp.id).ljust(8)

        rname = regs.get(va)
        if rname is not None:
            return rname[:7].ljust(8)

        return '        '

    def _getOpcodeSuffix(self, trace, va, op):
        pc = trace.getProgramCounter()
        if va != pc:
            return ''

        ovals = []
        for o in op.opers:

            if o.isDeref():
                ova = o.getOperAddr(op, trace)
            else:
                ova = o.getOperValue(op, trace)

            sym = None
            if trace.isValidPointer(ova):
                rova = trace.readMemoryFormat(ova, '<P')[0]
                sym = trace.getSymByAddr(rova)

            if sym is None:
                sym = trace.getSymByAddr(ova)

            if sym:
                ovals.append(repr(sym))
            elif o.isDeref():
                ovals.append('[0x%.8x]' % ova)
            else:
                ovals.append('0x%.8x' % ova)

        if [branch for branch, flag in op.getBranches() if flag & envi.BR_COND]:
            emu = self.emu_cache.get(self.arch, vtrace.getEmu(trace))
            emu.setRegisters(trace.getRegisters())
            emu.setProgramCounter(va)
            emu.executeOpcode(op)
            nextpc = emu.getProgramCounter()
            if va + len(op) != nextpc:
                ovals.append('Branch taken: 0x%08x' % nextpc)
            else:
                ovals.append('Branch not taken: 0x%08x' % nextpc)

        return ','.join(ovals)

    def render(self, mcanv, va):
        vastr = self.pformat % va
        # NOTE: we assume the memobj is a trace
        trace = mcanv.mem
        sym = trace.getSymByAddr(va)
        if sym is not None:
            mcanv.addText('\n')
            mcanv.addVaText(str(sym), va=va)
            mcanv.addText(':\n')

        op = trace.parseOpcode(va, arch=self.arch)
        obytes = trace.readMemory(va, op.size)[:8]

        prefix = self._getOpcodePrefix(trace, va, op)
        mcanv.addText(prefix)

        mcanv.addVaText(vastr, va=va)
        mcanv.addText(": %s " % e_common.hexify(obytes).ljust(17))
        op.render(mcanv)

        try:
            suffix = self._getOpcodeSuffix(trace, va, op)
            if suffix:
                mcanv.addText(' ;'+suffix)
        except Exception as e:
            mcanv.addText('; suffix error: %s' % e)

        mcanv.addText("\n")
        return len(op)

class SymbolRenderer(e_canvas.MemoryRenderer):
    def __init__(self, trace):
        a = trace.getMeta("Architecture")
        self.arch = envi.getArchModule(a)
        self.pwidth = self.arch.getPointerSize()

    def render(self, mcanv, va):
        # This is only used with tracer based stuff...
        trace = mcanv.mem
        vastr = self.arch.pointerString(va)
        # NOTE: we assume the memobj is a trace
        trace = mcanv.mem
        p = trace.readMemoryFormat(va, 'P')[0]

        isptr = trace.isValidPointer(p)

        pstr = self.arch.pointerString(p)

        mcanv.addVaText(vastr, va=va)
        mcanv.addText(": ")
        if isptr:
            mcanv.addVaText(pstr, p)
        else:
            mcanv.addText(pstr)

        if isptr:
            sym = trace.getSymByAddr(p, exact=False)
            if sym is not None:
                mcanv.addText(' %s + %d' % (repr(sym), p-int(sym)))

        mcanv.addText('\n')

        return self.pwidth


class DerefRenderer(e_canvas.MemoryRenderer):
    def __init__(self, trace):
        a = trace.getMeta("Architecture")
        self.arch = envi.getArchModule(a)
        self.pwidth = self.arch.getPointerSize()

    def renderData(self, mcanv, va):
        vastr = self.arch.pointerString(va)
        # NOTE: we assume the memobj is a trace
        trace = mcanv.mem
        p = trace.readMemoryFormat(va, 'P')[0]
        isptr = trace.isValidPointer(p)
        pstr = self.arch.pointerString(p)

        vareg = ""
        preg = ""

        regs = trace.getRegisters()
        for name, val in regs.items():
            if val == 0:
                continue
            if val == va:
                vareg = "(%s)" % name
            if val == p:
                preg = "(%s)" % name

        bt = trace.getStackTrace()
        if len(bt) > 1:
            for i in range(1, len(bt)):
                spc, sfc = bt[i]
                if sfc == 0:
                    break
                if spc == 0:
                    break
                if va == spc:
                    vareg = "(savepc)"
                if va == sfc:
                    vareg = "(frame%d)" % i
                if p == spc:
                    preg = "(savepc)"
                if p == sfc:
                    preg = "(frame%d)" % i

        vareg = vareg.ljust(8)
        preg = preg.ljust(8)

        mcanv.addText(" %s: " % str(va - mcanv._canv_beginva).ljust(5))
        mcanv.addVaText(vastr, va=va)
        mcanv.addText(" %s: " % vareg)
        if isptr:
            mcanv.addVaText(pstr, p)
        else:
            mcanv.addText(pstr)

        mcanv.addText(preg)

    def renderMetadata(self, mcanv, va):
        trace = mcanv.mem
        p = trace.readMemoryFormat(va, 'P')[0]
        e_canvas_rend.AutoBytesRenderer().render(mcanv, p)

    def render(self, mcanv, va):
        self.renderData(mcanv, va)
        self.renderMetadata(mcanv, va)
        mcanv.addText('\n')
        return self.arch.getPointerSize()


class StackRenderer(DerefRenderer):
    def __init__(self, trace):
        DerefRenderer.__init__(self, trace)

    def render(self, mcanv, va):
        trace = mcanv.mem
        if va != trace.getStackCounter():
            return DerefRenderer.render(self, mcanv, va)

        pc = trace.getProgramCounter()
        sym, is_thunk = trace.getSymByAddrThunkAware(pc)
        if sym is None:
            return DerefRenderer.render(self, mcanv, va)

        # TODO: this code also exists in win32stealth and in hookbreakpoint
        # we should put this somewhere common
        platform = trace.getMeta('Platform')
        arch = trace.getMeta('Architecture')
        impapi = viv_impapi.getImportApi(platform, arch)
        cc_name = impapi.getImpApiCallConv(sym)
        emu = vtrace.getEmu(trace)
        cc = emu.getCallingConvention(cc_name)
        args_def = impapi.getImpApiArgs(sym)
        if args_def is None:
            # sym did not exist in impapi :(
            logger.warning('sym but no impapi match: {}'.format(sym))
            return DerefRenderer.render(self, mcanv, va)

        argc = len(args_def)

        curop = trace.parseOpcode(trace.getProgramCounter())

        # use the calling convention to retrieve the args
        args = None
        if curop.isCall() or is_thunk:
            args = cc.getPreCallArgs(trace, argc)
        else:
            args = cc.getCallArgs(trace, argc)

        # since we are 'normalizing' the calls by visualizing all calling
        # conventions in a stdcall fashion, some args (like the ones in
        # registers don't have a stack va.
        mcanv.addText('%s :\n' % sym)
        fmt = '  arg%%d (%%s) 0x%%0%dx %%s\n' % (trace.getPointerSize()*2,)
        for index, arg in enumerate(args):
            argtype = args_def[index][0]
            argva = arg
            if trace.isValidPointer(arg):
                argva = trace.readMemoryFormat(arg, 'P')[0]
            smc = e_canvas.StringMemoryCanvas(trace)
            e_canvas_rend.AutoBytesRenderer(maxrend=64).render(smc, argva)
            desc = str(smc)
            mcanv.addText(fmt % (index, argtype, arg, desc))
        mcanv.addText('-' * 5)
        mcanv.addText('\n')

        return DerefRenderer.render(self, mcanv, va)
