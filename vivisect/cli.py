"""
The vivisect CLI.
"""
import re
import sys
import shlex
import pprint
import socket
import logging
import traceback
from getopt import getopt

import vtrace
import vivisect
import vivisect.vamp as viv_vamp
import vivisect.vector as viv_vector
import vivisect.reports as viv_reports
import vivisect.tools.graphutil as viv_graph

import vivisect.tools.fscope as v_t_fscope
import vivisect.tools.graphutil as v_t_graph

import visgraph.pathcore as vg_path

import vtrace.envitools as vt_envitools

import vdb

import envi.cli as e_cli
import envi.common as e_common
import envi.memory as e_memory
import envi.expression as e_expr
import envi.memcanvas as e_canvas
import envi.memcanvas.renderers as e_render

from vivisect.const import *

logger = logging.getLogger(__name__)


class VivCli(vivisect.VivWorkspace, e_cli.EnviCli):
    '''
    A class that builds upon the VivWorkspace to provide command line capabilities so that
    things like the Vivisect UI can provide a cleaner interface that just a direct python
    shell. It inherits the same parameters as the VivWorkspace (autosave and confdir currently)

    To add a new command, simply add a new function called `do_<cmdname>`.
    '''
    def __init__(self, **kwargs):
        e_cli.EnviCli.__init__(self, self, symobj=self)
        vivisect.VivWorkspace.__init__(self, **kwargs)
        self.canvas.addRenderer("bytes", e_render.ByteRend())
        self.canvas.addRenderer("u_int_16", e_render.ShortRend())
        self.canvas.addRenderer("u_int_32", e_render.LongRend())
        self.canvas.addRenderer("u_int_64", e_render.QuadRend())
        import vivisect.renderers as viv_rend
        self.canvas.addRenderer("viv", viv_rend.WorkspaceRenderer(self))
        self.prompt = "viv> "
        self.addScriptPathEnvVar('VIV_SCRIPT_PATH')

    def getExpressionLocals(self):
        locs = e_cli.EnviCli.getExpressionLocals(self)
        locs['vw'] = self
        locs['vprint'] = self.vprint
        locs['vivisect'] = vivisect
        return locs

    def do_report(self, line):
        """
        Fire a report module by python path name.

        Usage: report <python.path.to.report.module>
        """
        if not line:
            self.vprint("Report Modules")
            for descr, modname in viv_reports.listReportModules():
                self.vprint("Path: %32s (Name: %s)" % (modname, descr))
            return

        cols, results = viv_reports.runReportModule(self, line)
        for va, row in results.items():
            for indx in range(len(cols)):
                valu = row[indx]
                name, typename = cols[indx]
                self.canvas.addVaText(name, va)
                self.canvas.addText(": %s\n" % valu)
            self.canvas.addText("\n")

    def do_pathcount(self, line):
        '''
        Mostly for testing the graph stuff... this will likely be removed.

        (does not count paths with loops currently...)

        Usage: pathcount <func_expr>
        '''
        fva = self.parseExpression(line)
        if not self.isFunction(fva):
            self.vprint('Not a function!')
            return

        g = v_t_graph.buildFunctionGraph(self, fva)
        pathcnt = 0
        for path in v_t_graph.getCodePaths(g):
            self.vprint('Path through 0x%.8x: %s' % (fva, [hex(p[0]) for p in path]))
            pathcnt += 1
        self.vprint('Total Paths: %d' % pathcnt)

    def do_symboliks(self, line):
        '''
        Use the new symboliks subsystem. (NOTE: i386 only for a bit...)

        Usage: symboliks [ options ]

        -A  Run the emu and show the state of the machine for all found paths
            to the given address

        '''

        watchaddr = None

        argv = e_cli.splitargs(line)
        try:
            opts, argv = getopt(argv, 'A:')
        except Exception:
            return self.do_help('symboliks')

        for opt, optarg in opts:
            if opt == '-A':
                # TODO: USE THIS
                watchaddr = self.parseExpression(optarg)

        va = self.parseExpression(argv[0])
        fva = self.getFunction(va)

        import vivisect.symboliks as viv_symboliks
        import vivisect.symboliks.common as sym_common
        import vivisect.symboliks.effects as viv_sym_effects
        import vivisect.symboliks.analysis as vsym_analysis

        symctx = vsym_analysis.getSymbolikAnalysisContext(self)

        for emu, effects in symctx.getSymbolikPaths(fva):

            self.vprint('PATH %s' % ('='*60))

            for eff in effects:

                eff.reduce(emu)
                if eff.efftype in (EFFTYPE_CONSTRAIN, EFFTYPE_CALLFUNC):
                    self.vprint(str(eff))

            for addrsym, valsym in emu._sym_mem.values():
                addrsym = addrsym.reduce(emu=emu)
                valsym = valsym.reduce(emu=emu)
                if emu.isLocalMemory(addrsym):
                    continue
                self.vprint('[ %s ] = %s' % (addrsym, valsym))
            self.vprint('RETURN', emu.getFunctionReturn().reduce())

    def do_names(self, line):
        '''
        Show any names which contain the given argument.

        Usage: names <name_regex>

        FIXME unify do_sym from vdb into symbol context!
        '''
        if not line:
            return self.do_help('names')

        regex = re.compile(line, re.I)
        for va, name in self.getNames():
            if regex.search(name):
                self.vprint('0x%.8x: %s' % (va, name))

    def do_save(self, line):
        """
        Save the current workspace.

        Usage: save
        """
        self.vprint("Saving workspace...")
        self.saveWorkspace()
        self.vprint("...save complete!")

    def do_xrefs(self, line):
        """
        Show xrefs for a particular location.

        Usage: xrefs [options] <va_expr>
        -T Show xrefs *to* the given address
        -F Show xrefs *from* the given address (default)
        """
        parser = e_cli.VOptionParser()
        parser.add_option('-T', action='store_true', dest='xrto')
        parser.add_option('-F', action='store_true', dest='xrfrom')
        argv = shlex.split(line)
        try:
            options, argv = parser.parse_args(argv)
        except Exception as e:
            self.vprint(repr(e))
            return self.do_help('xrefs')

        if len(argv) < 1:
            self.vprint('Supply a va_expr')
            return self.do_help('xrefs')

        va = self.parseExpression(argv[0])

        fptr = []
        if options.xrto:
            fptr.append(self.getXrefsTo)
        if options.xrfrom:
            fptr.append(self.getXrefsFrom)

        for func in fptr:
            for xrfr, xrto, rtype, rflags in func(va):
                tname = ref_type_names.get(rtype, 'Unknown')
                self.vprint('\tFrom: 0x%.8x, To: 0x%.8x, Type: %s, Flags: 0x%.8x' % (xrfr, xrto, tname, rflags))

    def do_searchopcodes(self, line):
        '''
        search opcodes/function for a pattern

        searchopcodes [-f <funcva>] [options] <pattern>
        -f [fva]   - focus on one function
        -c         - search comments
        -o         - search operands
        -t         - search text
        -M <color> - mark opcodes (default = orange)
        -R         - pattern is REGEX (otherwise just text)

        '''
        parser = e_cli.VOptionParser()
        parser.add_option('-f', action='store', dest='funcva', type='int')
        parser.add_option('-c', action='store_true', dest='searchComments')
        parser.add_option('-o', action='store_true', dest='searchOperands')
        parser.add_option('-t', action='store_true', dest='searchText')
        parser.add_option('-M', action='store', dest='markColor', default='orange')
        parser.add_option('-R', action='store_true', dest='is_regex')

        argv = shlex.split(line)
        try:
            options, args = parser.parse_args(argv)
        except Exception as e:
            self.vprint(repr(e))
            return self.do_help('searchopcodes')

        pattern = ' '.join(args)
        if len(pattern) == 0:
            self.vprint('you must specify a pattern')
            return self.do_help('searchopcodes')

        # generate our interesting va list
        valist = []
        if options.funcva:
            # setup valist from function data
            try:
                fva = options.funcva
                graph = viv_graph.buildFunctionGraph(self, fva)
            except Exception as e:
                self.vprint(repr(e))
                return

            for nva, node in graph.getNodes():
                va = nva
                endva = va + node.get('cbsize')
                while va < endva:
                    lva, lsz, ltype, ltinfo = self.getLocation(va)
                    valist.append(va)
                    va += lsz

        else:
            # the whole workspace is our oyster
            valist = [va for va, lvsz, ltype, ltinfo in self.getLocations(LOC_OP)]

        res = []
        canv = e_canvas.StringMemoryCanvas(self)

        defaultSearchAll = True
        for va in valist:
            try:
                addthis = False
                op = self.parseOpcode(va)

                # search comment
                if options.searchComments:
                    defaultSearchAll = False
                    cmt = self.getComment(va)
                    if cmt is not None:

                        if options.is_regex:
                            if len(re.findall(pattern, cmt)):
                                addthis = True

                        else:
                            if pattern in cmt:
                                addthis = True

                # search operands
                if options.searchOperands:
                    defaultSearchAll = False
                    for opidx, oper in enumerate(op.opers):
                        # we're writing to a temp canvas, so clear it before each test
                        canv.clearCanvas()
                        oper = op.opers[opidx]
                        oper.render(canv, op, opidx)
                        operepr = canv.strval

                        if options.is_regex:
                            if len(re.findall(pattern, operepr)):
                                addthis = True

                        else:
                            if pattern in operepr:
                                addthis = True

                            # if we're doing non-regex, let's test against real numbers
                            # (instead of converting to hex and back)
                            numpattrn = pattern
                            try:
                                numpattrn = int(numpattrn, 0)
                            except:
                                pass

                            if numpattrn in vars(oper).values():
                                addthis = True

                # search full text
                if options.searchText or defaultSearchAll:
                    # search through the rendering of the opcode, as well as the comment
                    canv.clearCanvas()
                    op.render(canv)
                    oprepr = canv.strval
                    cmt = self.getComment(va)
                    if cmt is not None:
                        oprepr += "  ; " + cmt

                    if options.is_regex:
                        if len(re.findall(pattern, oprepr)):
                            addthis = True

                    else:
                        if pattern in oprepr:
                            addthis = True
                # only want one listing of each va, no matter how many times it matches
                if addthis:
                    res.append(va)
            except:
                self.vprint(''.join(traceback.format_exception(*sys.exc_info())))

        if len(res) == 0:
            self.vprint('pattern not found: %s (%s)' % (pattern.encode('utf-8').hex(), repr(pattern)))
            return

        # set the color for each finding
        color = options.markColor
        colormap = {va: color for va in res}
        if self._viv_gui is not None:
            from vqt.main import vqtevent
            vqtevent('viv:colormap', colormap)

        self.vprint('matches for: %s (%s)' % (pattern.encode('utf-8').hex(), repr(pattern)))
        for va in res:
            mbase, msize, mperm, mfile = self.memobj.getMemoryMap(va)
            pname = e_memory.reprPerms(mperm)
            sname = self.reprPointer(va)

            op = self.parseOpcode(va)
            self.canvas.renderMemory(va, len(op))
            cmt = self.getComment(va)
            if cmt is not None:
                self.canvas.addText('\t\t; %s (Perms: %s, Smartname: %s)' % (cmt, pname, sname))

            self.canvas.addText('\n')

        self.vprint('done (%d results).' % len(res))

    def do_imports(self, line):
        """
        Show the imports in the workspace (or potentially just one file)

        Usage: imports [fname]
        """
        self.canvas.addText("Imports:\n")
        for va, size, ltype, tinfo in self.getImports():
            # FIXME warn them...
            # (but should we though?)
            if not tinfo.startswith(line):
                continue
            vastr = self.arch.pointerString(va)
            self.canvas.addVaText(vastr, va)
            self.canvas.addText(" ")
            self.canvas.addNameText(tinfo, tinfo)
            self.canvas.addText("\n")

    def do_fscope(self, line):
        '''
        The fscope command can be used to enumerate things from the
        scope of one function and down it's calling graph.

        Usage: fscope [options] <func_addr_expr>

        -I - Show import calls from this function scope
        -S - Show strings from this function scope

        Example: fscope -I kernel32.CreateFileW
                 (Show imports called by CreateFileW and down...)

        '''
        showimp = False
        showstr = False

        argv = e_cli.splitargs(line)
        try:
            opts, args = getopt(argv, 'IS')
        except Exception:
            return self.do_help('fscope')

        if not len(args) or not len(opts):
            return self.do_help('fscope')

        for opt, optarg in opts:
            if opt == '-I':
                showimp = True
            elif opt == '-S':
                showstr = True

        for expr in args:

            va = self.parseExpression(expr)

            if showimp:
                for callva, impname in v_t_fscope.getImportCalls(self, va):
                    pstr = self.arch.pointerString(callva)
                    self.canvas.addVaText(pstr, callva)
                    # FIXME best name symbol etc?
                    self.canvas.addText(' %s\n' % impname)

            if showstr:
                for refva, strva, strbytes in v_t_fscope.getStringRefs(self, va):
                    pstr = self.arch.pointerString(refva)
                    self.canvas.addVaText(pstr, refva)
                    self.canvas.addText(' ')
                    self.canvas.addVaText(strbytes, strva)
                    self.canvas.addText('\n')

    def do_exports(self, line):
        """
        List the exports in the workspace (or in a specific file).

        Usage: exports [fname]
        """
        edict = {}
        for va, etype, name, filename in self.getExports():
            exps = edict.get(filename)
            if exps is None:
                edict[filename] = []
            exps.append((name, va))

        if line:
            x = edict.get(line)
            if x is None:
                self.vprint("Unknown fname: %s" % line)
                return
            edict = {line: x}

        fnames = list(edict.keys())
        fnames.sort()
        for fname in fnames:
            self.canvas.addNameText(fname, fname)
            self.canvas.addText(":\n")
            exports = edict.get(fname)
            exports.sort()
            for ename, eva in exports:
                pstr = self.arch.pointerString(eva)
                self.canvas.addText("    ")
                self.canvas.addVaText(pstr, eva)
                self.canvas.addText("  ")
                self.canvas.addNameText(ename, ename)
                self.canvas.addText("\n")

    def do_filemeta(self, line):

        '''
        Show/List file metadata.

        Usage: filemeta [ fname [ keyname ] ]

        Example: filemeta kernel32
        Example: filemeta kernel32 md5
        '''

        argv = e_cli.splitargs(line)
        if len(argv) == 0:

            self.vprint('Loaded Files:')
            for fname in self.getFiles():
                self.vprint('    %s' % fname)

        elif len(argv) == 1:
            d = self.getFileMetaDict(argv[0])
            self.vprint(pprint.pformat(d))

        elif len(argv) == 2:
            val = self.getFileMeta(argv[0], argv[1])
            self.vprint('%s (%s):' % (argv[1], argv[0]))
            self.vprint(pprint.pformat(val))

        else:
            self.do_help('filemeta')

    def do_funcmeta(self, line):
        """
        Show/Set function metadata.
        Usage: funcmeta <func_expr> [key <value_expr>]

        """
        # FIXME make a search thing here!
        argv = e_cli.splitargs(line)
        if len(argv) == 0:
            return self.do_help("funcmeta")

        if len(argv) == 1:
            va = self.parseExpression(argv[0])
            meta = self.getFunctionMetaDict(va)
            self.vprint(pprint.pformat(meta))

        elif len(argv) == 3:
            va = self.parseExpression(argv[0])
            name = argv[1]
            locs = self.getExpressionLocals()
            val = e_expr.evaluate(argv[2], locs)
            self.setFunctionMeta(va, name, val)

    def do_loc(self, line):
        """
        Display the repr of a single location by va.

        Usage: loc <va_expr>
        """
        if not line:
            return self.do_help("loc")

        addr = self.parseExpression(line)
        loc = self.getLocation(addr)
        if loc is None:
            s = self.arch.pointerString(addr)
            self.vprint("Unknown location: %s" % s)
        r = self.reprLocation(loc)
        self.vprint(r)

    def do_make(self, line):
        """
        Create new instances of locations in the vivisect workspace.

        Usage: make [options] <va_expr>
        -c Make code
        -f Make function
        -s Make a string
        -u Make a unicode string
        -n <size> Make a number
        -p <size> Make a pad
        -S <structname> Make a structure
        """
        argv = e_cli.splitargs(line)
        try:
            opts, args = getopt(argv, "csup:S:")
        except Exception as e:
            logger.warning(str(e))
            return self.do_help("make")

        if len(args) != 1 or len(opts) != 1:
            return self.do_help("make")

        addr = self.parseExpression(args[0])
        opt, optarg = opts[0]

        if opt == "-f":
            logger.debug('new function (manual-cli): 0x%x', addr)
            self.makeFunction(addr)

        elif opt == "-c":
            self.makeCode(addr)

        elif opt == "-s":
            self.makeString(addr)

        elif opt == "-u":
            self.makeUnicode(addr)

        elif opt == "-n":
            size = self.parseExpression(optarg)
            self.makeNumber(addr, size)

        elif opt == "-p":
            size = self.parseExpression(optarg)
            self.makePad(addr, size)

        elif opt == "-S":
            self.makeStructure(addr, optarg)

        else:
            return self.do_help("make")

    def do_emulate(self, line):
        """
        Create an emulator for the given function, and drop into a vdb
        interface to step through the code.

        (vdb CLI will appear in controlling terminal...)

        Usage: emulate <va_expr>
        """
        if not line:
            return self.do_help("emulate")

        emu = self.getEmulator()
        addr = self.parseExpression(line)
        emu.setProgramCounter(addr)

        trace = vt_envitools.TraceEmulator(emu)

        db = vdb.Vdb(trace=trace)
        db.cmdloop()

    def do_argtrack(self, line):
        """
        Track input arguments to the given function by name or address.

        Usage: argtrack <func_addr_expr> <arg_idx>
        """
        if not line:
            return self.do_help("argtrack")

        argv = e_cli.splitargs(line)
        if len(argv) != 2:
            return self.do_help("argtrack")

        try:
            fva = self.parseExpression(argv[0])
        except Exception:
            self.vprint("Invalid Address Expression: %s" % argv[0])
            return

        try:
            idx = self.parseExpression(argv[1])
        except Exception:
            self.vprint("Invalid Index Expression: %s" % argv[1])
            return

        if self.getFunction(fva) != fva:
            self.vprint("Invalid Function Address: (0x%.8x) %s" % (fva, line))

        for pleaf in viv_vector.trackArgOrigin(self, fva, idx):

            self.vprint('='*80)

            path = vg_path.getPathToNode(pleaf)
            path.reverse()

            for pnode in path:
                fva = vg_path.getNodeProp(pnode, 'fva')
                argv = vg_path.getNodeProp(pnode, 'argv')
                callva = vg_path.getNodeProp(pnode, 'cva')
                argidx = vg_path.getNodeProp(pnode, 'argidx')
                if callva is not None:
                    aval, amagic = argv[argidx]
                    arepr = '0x%.8x' % aval
                    if amagic is not None:
                        arepr = repr(amagic)
                    frepr = 'UNKNOWN'
                    if fva is not None:
                        frepr = '0x%.8x' % fva
                    self.vprint('func: %s calls at: 0x%.8x with his own: %s' % (frepr, callva, arepr))
            self.vprint("="*80)

    def do_chat(self, line):
        """
        Echo a message to any other users of a shared workspace.

        Usage: chat oh hai! Checkout 0x7c778030
        """
        if len(line) == 0:
            return self.do_help('chat')

        self.chat(line)

    def do_codepath(self, line):
        """
        Enumerate and show any known code paths from the specified
        from address expression to the to address expression.
        Usage: codepath <from_expr> <to_expr>
        """
        if not line:
            return self.do_help("codepath")

        argv = e_cli.splitargs(line)
        if len(argv) != 2:
            return self.do_help("codepath")

        try:
            frva = self.parseExpression(argv[0])
        except Exception:
            self.vprint("Invalid From Va: %s" % argv[0])
            return

        try:
            tova = self.parseExpression(argv[1])
        except Exception:
            self.vprint("Invalid To Va: %s" % argv[1])
            return

        self.vprint("Tracking Paths From 0x%.8x to 0x%.8x" % (frva, tova))

        paths = viv_vector.getCodePaths(self, frva, tova)
        self.vprint("Function VA\tBlock VA\tSize\tFunction Name")
        count = 0
        for blist in paths:
            count += 1
            self.vprint("="*30)
            for bva, bsize, fva in blist:
                fname = self.getName(fva)
                self.vprint("0x%.8x\t0x%.8x\t%4d\t%s" % (fva, bva, bsize, fname))
        if count == 0:
            self.vprint("None!")
            return

    def do_vampsig(self, line):
        """
        Generate a vamp signature string for the given function's first block.
        """
        if not line:
            return self.do_help("vampsig")

        va = self.parseExpression(line)

        fva = self.getFunction(va)
        if fva is None:
            self.vprint("Invalid Function Address: 0x%.8x (%s)" % (va, line))

        sig, mask = viv_vamp.genSigAndMask(self, fva)
        self.vprint("SIGNATURE: %s" % e_common.hexify(sig))
        self.vprint("MASK: %s" % e_common.hexify(mask))

    def do_vdb(self, line):
        '''
        Execute vdb GUI from within vivisect (allowing special hooks between them...)
        (Optionally, specify a host to use for remote vdb debugging)

        Usage: vdb [<remote_host>]
        '''
        if line:
            try:
                socket.gethostbyname(line)
            except Exception:
                self.vprint('Invalid Remote Host: %s' % line)

            vtrace.remote = line

        import vivisect.vdbext as viv_vdbext
        viv_vdbext.runVdb(self._viv_gui)

    def do_plt(self, line):
        '''
        Parse an entire PLT Section

        Usage: plt <pltva> <pltsize>
        '''
        if not line:
            return self.do_help("plt")

        argv = e_cli.splitargs(line)
        if len(argv) != 2:
            return self.do_help("plt")

        sva = self.parseExpression(argv[0])
        ssize = self.parseExpression(argv[1])

        import vivisect.analysis.elf.elfplt as vaee
        vaee.analyzePLT(self, sva, ssize)

    def do_plt_function(self, line):
        '''
        Make a PLT function at a virtual address

        Usage: plt_function <va>
        '''
        if not line:
            return self.do_help("plt_function")

        fva = self.parseExpression(line)

        import vivisect.analysis.elf.elfplt as vaee
        vaee.analyzeFunction(self, fva)
