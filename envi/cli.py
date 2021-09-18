'''
Unified CLI code for things like vivisect and vdb.
'''

import os
import re
import sys
import code
import json
import shlex
import logging
import binascii
import optparse
import traceback
import threading
import collections

import envi.bits as e_bits
import envi.memory as e_mem
import envi.common as e_common
import envi.config as e_config
import envi.memcanvas as e_canvas
import envi.expression as e_expr
import envi.symstore.resolver as e_resolv
import envi.memcanvas.renderers as e_render

from cmd import Cmd
from getopt import getopt


logger = logging.getLogger(__name__)

def splitargs(cmdline):
    cmdline = cmdline.replace('\\\\"', '"').replace('\\"', '')
    patt = re.compile('\".+?\"|\S+')
    for item in cmdline.split('\n'):
        return [s.strip('"') for s in patt.findall(item)]

def formatargs(args):
    ret = []
    subcmds = [args[i:i+5] for i in range(0, len(args), 5)]
    for cmdnames in subcmds:
        fmtstr = '{:15}' * len(cmdnames)
        yield fmtstr.format(*cmdnames)

def columnstr(slist):
    msize = 0
    for s in slist:
        if len(s) > msize:
            msize = len(s)
    return [x.ljust(msize) for x in slist]


class CliExtMeth:
    """
    This is used to work around the difference
    between functions and bound methods for extended
    command modules
    """
    def __init__(self, cli, func):
        self.cli = cli
        self.func = func
        self.__doc__ = func.__doc__

    def __call__(self, line):
        return self.func(self.cli, line)

def isValidScript(scriptpath):
    '''
    Takes in a filepath
    Returns whether the file is valid python (ie. suvives import)
    '''
    if not os.path.isfile(scriptpath):
        return False

    with open(scriptpath, 'rb') as f:
        contents = f.read()

    try:
        cobj = compile(contents, scriptpath, 'exec')
        return True
    except Exception:
        pass

    return False

def getRelScriptsFromPath(scriptpaths):
    '''
    Takes in a list of base paths (eg. ENVI_SCRIPT_PATH list) and recurses the
    directories looking for valid python files (ie. they don't throw errors
    on import).

    Returns a list of scripts usable from the cli in *relative path* format.
    ie.  if my path has "/home/hacker/fooscripts" in it, the script located
    at "/home/hacker/fooscripts/barmazing/bazthis.py" is listed as
    "barmazing/bazthis.py" and the do_script() handler can use that.
    '''
    scripts = []
    for basedir in scriptpaths:
        baselen = len(basedir)

        for dirname,subdirs,subfiles in os.walk(basedir):
            for subfile in subfiles:
                subpath = os.path.join(dirname,subfile)
                if isValidScript(subpath):
                    script = subpath[baselen:]
                    if script.startswith(os.sep):
                        script = script[1:]
                    scripts.append(script)

    return scripts

cfgdefs = {
    'cli':{
        'verbose':False,
        'aliases':{
        }
    }
}

class VOptionParser(optparse.OptionParser):
    '''
    overloads error function that prints to stdout/stderr.

    error is overloaded to raise an exception if an error occurs during the
    parse of arguments.  normally optionparser sends it to stderr.
    '''
    def __init__(self, *args, **kwargs):
        optparse.OptionParser.__init__(self, *args, add_help_option=False, **kwargs)

    def error(self, msg):
        raise Exception(msg)

class EnviCli(Cmd):

    def __init__(self, memobj, config=None, symobj=None):

        self.extcmds = {}
        self.basecmds = []
        self.emptymeth = None
        self.extsubsys = collections.defaultdict(list)
        self.scriptpaths = []
        self.addScriptPathEnvVar('ENVI_SCRIPT_PATH')

        Cmd.__init__(self, stdout=self)

        for name in dir(self):
            if name.startswith('do_'):
                self.basecmds.append(name[3:])

        self.shutdown = threading.Event()

        # If they didn't give us a resolver, make one.
        if symobj is None:
            symobj = e_resolv.SymbolResolver()

        if config is None:
            config = e_config.EnviConfig(defaults=cfgdefs)

        # Force it to be there if its not
        config.getSubConfig('cli')

        self.config = config
        self.memobj = memobj
        self.symobj = symobj
        self.canvas = e_canvas.MemoryCanvas(memobj, syms=symobj)

        self.aliases = {} # For *runtime* aliases only!

    def addCmdAlias(self, alias, cmd, persist=False):
        '''
        Add a command alias and optionally save it.

        Specify persist=True to save the alias.

        Example:
            cli.addRuntimeAlias('woot', 'woot -F -T')
        '''
        if not persist:
            self.aliases[ alias ] = cmd
            return
        self.config.cli.aliases[ alias ] = cmd

    def addScriptPathEnvVar(self, pathenv):
        '''
        Reads a script environment variable in, parses it, and stores the paths
        '''
        scriptdirs = os.getenv( pathenv )
        if scriptdirs is not None:
            for scriptdir in scriptdirs.split(os.pathsep):
                if scriptdir in self.scriptpaths:
                    continue

                self.scriptpaths.append( scriptdir )

    def setCanvas(self, canvas):
        """
        Set a new canvas for the CLI and add all the current renderers
        to the new one.
        """
        for name in self.canvas.getRendererNames():
            canvas.addRenderer(name, self.canvas.getRenderer(name))
        self.canvas = canvas

    def write(self, data):
        # For stdout/stderr
        self.canvas.write(data)

    def get_names(self):
        ret = []
        ret.extend(Cmd.get_names(self))
        ret.extend(self.extcmds.keys())
        return ret

    def getExpressionLocals(self):
        """
        Over-ride this to have things like the eval command
        and the python command use more locals than the sybolic
        defaults.
        """
        return e_expr.MemoryExpressionLocals(self.memobj, symobj=self.symobj)

    def registerCmdExtension(self, func, subsys='extended'):
        self.extcmds["do_%s" % func.__name__] = CliExtMeth(self, func)
        self.extsubsys[ subsys ].append( func.__name__ )

    def vprint(self, msg, addnl=True):
        '''
        Print output to the CLI's output handler.  This allows routines to
        print to the terminal or the GUI depending on which mode we're in.

        Example:
            vprint('hi mom!')
        '''
        if addnl:
            msg = msg + "\n"
        self.canvas.write(msg)

    def __getattr__(self, name):
        func = self.extcmds.get(name, None)
        if func is None:
            raise AttributeError(name)
        return func

    def aliascmd(self, line):
        # Check the "runtime" aliases first
        for alias, cmd in self.aliases.items():
            if line.startswith(alias):
                return line.replace(alias, cmd)

        # Now the "configured" aliases
        for alias, cmd in self.config.cli.aliases.items():
            if line.startswith(alias):
                return line.replace(alias, cmd)

        return line

    def cmdloop(self, intro=None):
        if intro is not None:
            self.vprint(intro)

        while not self.shutdown.isSet():
            try:
                Cmd.cmdloop(self, intro=intro)
            except Exception:
                logger.error(traceback.format_exc())

    def emptyline(self):
        return self.do_help('')

    def setEmptyMethod(self, callback):
        '''
        Set a method to be called back in the event of emptyline().
        NOTE: this method is cleared on every onecmd() call.

        ( the method is called with no args )

        Example:

            def do_foo(self, line):

                x = 10
                def showx():
                    print('X: %d' % x)
                    x += 10

                showx()
                cli.setcrmeth(showx)

        '''
        self.emptymeth = callback

    def onecmd(self, line):

        # check for empty line and emptymeth
        if not line.strip() and self.emptymeth:
            self.emptymeth()
            return

        self.emptymeth = None
        lines = line.split("&&")
        try:
            for line in lines:
                line = self.aliascmd(line)
                Cmd.onecmd(self, line)
        except SystemExit:
            raise
        except Exception as msg:
            if self.config.cli.verbose:
                self.vprint(traceback.format_exc())
            self.vprint("\nERROR: (%s) %s" % (msg.__class__.__name__, msg))

        if self.shutdown.isSet():
            return True

    def do_help(self, line):
        if line:
            return Cmd.do_help(self, line)

        self.basecmds.sort()
        self.vprint('\nbasics:')

        for line in formatargs(self.basecmds):
            self.vprint(line)

        subsys = list(self.extsubsys.keys())
        subsys.sort()

        for sub in subsys:
            self.vprint('\n%s:' % sub)
            cmds = self.extsubsys.get(sub)
            cmds.sort()
            for line in formatargs(cmds):
                self.vprint(line)

        self.vprint('\n')

    def do_clear(self, line):
        '''
        Clears the CLI output. (GUI only)
        '''
        self.canvas.clearCanvas()

    def do_EOF(self, line):
        self.vprint("Use quit")

    def do_quit(self, line):
        """
        Quit

        Usage: quit
        """
        self.shutdown.set()

    def do_config(self, line):
        '''
        Show, edit, or save config options from the command line.

        Usage: config [-s] [config option[=value]]

        no options  display config
        -s          save config to default location AFTER setting any options.
        '''
        parser = VOptionParser()
        parser.add_option('-s', action='store_true', dest='do_save')

        argv = shlex.split(line)
        try:
            options, args = parser.parse_args(argv)
        except Exception as e:
            self.vprint(repr(e))
            return self.do_help('config')

        if len(args) <= 0 and not options.do_save:
            #FIXME for now we will hard code one level of sections
            subnames = self.config.getSubConfigNames()
            subnames.sort()
            for subname in subnames:
                subcfg = self.config.getSubConfig(subname)
                options = list(subcfg.keys())
                options.sort()
                for optname in options:
                    optval = subcfg.get(optname)
                    self.vprint('%s.%s=%s' % (subname, optname, json.dumps(optval)))

            return

        # 1 option per run
        if len(args) > 1:
            return self.do_help('config')

        if len(args) == 1:
            parts = args[0].split('=', 1)
            subname, optname = parts[0].split('.', 1)

            subcfg = self.config.getSubConfig(subname, add=False)
            if subcfg is None:
                self.vprint('No Such Config Section: %s' % subname)
                return

            optval = subcfg.get(optname)
            if optval is None:
                self.vprint('No Such Config Option: %s' % optname)
                return

            if len(parts) == 2:
                newval = json.loads(parts[1])

                if (not isinstance(newval, str)) or not isinstance(optval, str):
                    if type(newval) != type(optval):
                        self.vprint('Invalid Type Mismatch: %r - %r' % (newval, optval))
                        return

                optval = newval
                subcfg[optname] = newval

            self.vprint('%s.%s=%s' % (subname, optname, json.dumps(optval)))

        if options.do_save:
            self.config.saveConfigFile()
            self.vprint('saved configuration file to: %s' % self.config.filename)

    def do_alias(self, line):
        """
        Add an alias to the command line interpreter's aliases dictionary
        Usage: alias <alias_word> rest of the alias command

        To delete an alias:
        Usage: alias <alias_word>
        """
        if len(line):
            row = line.split(None, 1)
            self.config.cli.aliases.pop(row[0])
            if len(row) > 1:
                self.config.cli.aliases[ row[0] ] = row[1]

        self.vprint('')
        self.vprint('Runtime Aliases (not saved):')
        aliases = list(self.aliases.keys())
        aliases.sort()
        for alias in aliases:
            self.vprint('%s -> %s' % (alias,self.aliases.get(alias)))
        self.vprint('')

        self.vprint('Configured Aliases:')
        aliases = list(self.config.cli.aliases.keys())
        aliases.sort()
        for alias in aliases:
            self.vprint('%s -> %s' % (alias, self.config.cli.aliases.get(alias)))
        self.vprint('')
        return

    def do_python(self, line):
        """
        Start an interactive python interpreter. The namespace of the
        interpreter is updated with expression nicities.  You may also
        specify a line of python code as an argument to be exec'd without
        beginning an interactive python interpreter on the controlling
        terminal.

        Usage: python [pycode]
        """
        locals = self.getExpressionLocals()
        if len(line) != 0:
            cobj = compile(line, 'cli_input', 'exec')
            exec(cobj, locals)
        else:
            code.interact(local=locals)

    def parseExpression(self, expr):
        return int(e_expr.evaluate(expr, self.getExpressionLocals()))

    def do_binstr(self, line):
        '''
        Display a binary representation of the given value expression
        (padded to optional width in bits)

        Usage: binstr <val_expr> [<bitwidth_expr>]
        '''
        argv = splitargs(line)
        if len(argv) == 0:
            return self.do_help('binstr')
        bitwidth = None
        value = self.parseExpression(argv[0])
        if len(argv) > 1:
            bitwidth = self.parseExpression(argv[1])
        binstr = e_bits.binrepr(value, bitwidth=bitwidth)
        self.canvas.addText("0x%.8x (%d) %s\n" % (value, value, binstr))

    def do_eval(self, line):
        """
        Evaluate an expression on the CLI to show it's value.

        Usage: eval (ecx+edx)/2
        """
        if not line:
            return self.do_help("eval")

        value = self.parseExpression(line)

        self.canvas.addText("%s = " % line)
        if self.memobj.isValidPointer(value):
            self.canvas.addVaText("0x%.8x" % value, value)
            sym = self.symobj.getSymByAddr(value, exact=False)
            if sym is not None:
                self.canvas.addText(" ")
                self.canvas.addVaText("%s + %d" % (repr(sym),value-int(sym)), value)
        else:
            self.canvas.addText("0x%.8x (%d)" % (value, value))

        self.canvas.addText("\n")

    def do_script(self, line):
        '''
        Execute a python file.

        The script file is arbitrary python code which is run with the
        full complement of expression extensions mapped in as locals.

        The script command sources the env var ENVI_SCRIPT_PATH.

        NOTE: additional command line arguments may be passed in and will
              appear as the list "argv" in the script namespace!  (They will
              all be strings)

        Usage: script <scriptfile> [<argv[0]>, ...]

        or     script ?
        '''
        if len(line) == 0:
            return self.do_help('script')

        argv = splitargs(line)
        locals = self.getExpressionLocals()
        locals['argv'] = argv

        if len(argv) and argv[0] == "?":
            scripts = getRelScriptsFromPath(self.scriptpaths)
            scripts.sort()
            self.vprint('Scripts available in script paths:\n\t' + '\n\t'.join(scripts))
            return


        # TODO: unify vdb.extensions.loadExtensions VDB_EXT_PATH with this
        # TODO: where should env var parsing live?
        scriptpath = None
        if os.path.exists(argv[0]):
            scriptpath = argv[0]
        else:
            for scriptdir in self.scriptpaths:
                # allow scripts to import things from the script dir
                if scriptdir not in sys.path:
                    sys.path.append(scriptdir)

                spath = os.path.join(scriptdir, argv[0])
                if os.path.exists(spath):
                    scriptpath = spath

        if scriptpath is None:
            self.vprint('failed to find script')
            return

        with open(scriptpath, 'rb') as f:
            contents = f.read()

        try:
            cobj = compile(contents, scriptpath, 'exec')
            exec(cobj, locals)
        except Exception as e:
            self.vprint( traceback.format_exc() )
            self.vprint('SCRIPT ERROR: %s' % e)

    def do_maps(self, line):
        """
        Display either a list of all the memory maps or the memory map
        details for the given address expression.

        Usage: maps [addr_expression]
        """
        argv = splitargs(line)
        if len(argv):
            expr = " ".join(argv)
            va = self.parseExpression(expr)
            map = self.memobj.getMemoryMap(va)
            if map is None:
                self.vprint("Memory Map Not Found For: 0x%.8x"%va)

            else:
                addr,size,perm,fname = map
                pname = e_mem.reprPerms(perm)
                self.canvas.addText("Memory Map For: ")
                self.canvas.addVaText("0x%.8x" % va, va)
                self.canvas.addText("\n")
                self.canvas.addVaText("0x%.8x" % addr, addr)
                self.canvas.addText("\t%d\t%s\t%s\n" % (size,pname,fname))
        else:
            totsize = 0
            self.vprint("[ address ] [ size ] [ perms ] [ File ]")
            for addr,size,perm,fname in self.memobj.getMemoryMaps():
                pname = e_mem.reprPerms(perm)
                totsize += size
                self.canvas.addVaText("0x%.8x" % addr, addr)
                sizestr = ("%dK" % (size//1024,)).rjust(8)
                self.canvas.addText("%s\t%s\t%s\n" % (sizestr,pname,fname))
            self.vprint("Total Virtual Memory: %.2f MB" % ((float(totsize)/1024)/1024))

    def do_saveout(self, line):
        '''
        saves output to file for any command.  still outputs to whatever
        canvas the command normally outputs to.

        saveout <output file> <cli command>

        Example:
        saveout out.txt search -c MZ
        '''
        argv = shlex.split(line)
        if len(argv) < 2:
            return self.do_help('saveout')

        fname = argv[0]
        command = ' '.join(argv[1:])

        strcanvas = e_canvas.StringMemoryCanvas(self.canvas.mem)
        with e_canvas.TeeCanvas(self, (self.canvas, strcanvas)) as tc:
            self.onecmd(command)

            with open(fname, 'wb') as f:
                f.write(str(strcanvas))

    def do_search(self, line):
        '''
        search memory for patterns.

        search [options] <pattern>

        -e  <codec> encode the pattern with a codec (hex, utf-16le, etc)
        -X  pattern is in hex (ie. 41414242 is AABB)
        -E  pattern is an envi memory expression (numeric search)
        -r  pattern is a regular expression
        -R  <baseexpr:sizeexpr> search a range of memory (base + size)
        -c  show context (32 bytes) after each hit
        '''
        parser = VOptionParser()
        parser.add_option('-e', action='store', dest='encode_as')
        parser.add_option('-X', action='store_true', dest='is_hex')
        parser.add_option('-E', action='store_true', dest='is_expr')
        parser.add_option('-r', action='store_true', dest='is_regex')
        parser.add_option('-R', action='store', dest='range_search')
        parser.add_option('-c', action='store_const', dest='num_context_bytes',
                const=32)

        argv = shlex.split(line)
        try:
            options, args = parser.parse_args(argv)
        except Exception as e:
            self.vprint(repr(e))
            return self.do_help('search')

        pattern = (' '.join(args)).encode('utf-8')
        if len(pattern) == 0:
            self.vprint('you must specify a pattern')
            return self.do_help('search')

        if options.is_expr:
            sval = self.parseExpression(pattern)
            endian = self.memobj.getEndian()
            size = self.memobj.getPointerSize()
            pattern = e_bits.buildbytes(sval, size, bigend=endian)

        if options.is_hex:
            pattern = binascii.unhexlify(pattern)

        if options.encode_as is not None:
            if options.encode_as == 'hex':
                pattern = e_common.hexify(pattern)
            else:
                import codecs
                patternutf8 = pattern.decode('utf-8')
                pattern = codecs.encode(patternutf8, encoding=options.encode_as)

        if options.range_search:
            try:
                addrexpr, sizeexpr = options.range_search.split(":")
            except Exception as e:
                self.vprint(repr(e))
                return self.do_help('search')
            addr = self.parseExpression(addrexpr)
            size = self.parseExpression(sizeexpr)

            self.canvas.addText('searching from ')
            self.canvas.addVaText('0x%.8x' % addr, addr)
            self.canvas.addText(' for %d bytes\n' % size)
            res = self.memobj.searchMemoryRange(pattern, addr, size, regex=options.is_regex)
        else:
            self.vprint('searching all memory...')
            res = self.memobj.searchMemory(pattern, regex=options.is_regex)

        if len(res) == 0:
            self.vprint('pattern not found: %s (%s)' % (e_common.hexify(pattern), repr(pattern)))
            return

        brend = e_render.ByteRend()
        self.vprint('matches for: %s (%s)' % (e_common.hexify(pattern), repr(pattern)))
        for va in res:
            mbase,msize,mperm,mfile = self.memobj.getMemoryMap(va)
            pname = e_mem.reprPerms(mperm)
            sname = self.reprPointer(va)

            self.canvas.addVaText('0x%.8x' % va, va)
            self.canvas.addText(': ')
            self.canvas.addText('%s ' % pname)
            self.canvas.addText(sname)

            if options.num_context_bytes is not None:
                self.canvas.addText('\n')
                self.canvas.renderMemory(va, options.num_context_bytes, rend=brend)

            self.canvas.addText('\n')

        self.vprint('done (%d results).' % len(res))

    def reprPointer(self, va):
        """
        Do your best to create a humon readable name for the
        value of this pointer.
        """
        if va == 0:
            return "NULL"

        try:
            mbase, msize, mperm, mfile = self.memobj.getMemoryMap(va)
            if va == mbase:
                ret = mfile
            else:
                ret = mfile + " + 0x%x" % (va - mbase)

            sym = self.symobj.getSymByAddr(va, exact=False)
            if sym is not None:
                ret = "%s + 0x%x" % (repr(sym), va-int(sym))

        except Exception:
            ret = hex(va)

        return ret

    def do_memdump(self, line):
        """
        Dump memory to a file.  If no size is given, the entire memory map that
        contains the given va is dumped to disk.

        Usage: memdump <va_expression> <filename> [size_expression]
        """
        argv = shlex.split(line)
        if len(argv) not in (2, 3):
            return self.do_help('memdump')

        va = self.parseExpression(argv[0])
        fname = argv[1]

        if len(argv) == 2:
            va, size, perm, name = self.memobj.getMemoryMap(va)
        elif len(argv) == 3:
            size = self.parseExpression(argv[2])
        else:
            return self.do_help('memdump')

        mem = self.memobj.readMemory(va, size)
        with open(fname, 'wb') as f:
            f.write(mem)

        self.vprint('wrote %d bytes.' % len(mem))

    def do_memcmp(self, line):
        '''
        Compare memory at the given locations.  Outputs a set of
        differences showing bytes at their given offsets....

        Usage: memcmp <addr_expr1> <addr_expr2> <size_expr>
        '''
        if len(line) == 0:
            return self.do_help('memcmp')

        argv = splitargs(line)
        if len(argv) != 3:
            return self.do_help('memcmp')

        addr1 = self.parseExpression(argv[0])
        addr2 = self.parseExpression(argv[1])
        size  = self.parseExpression(argv[2])

        bytes1 = self.memobj.readMemory(addr1, size)
        bytes2 = self.memobj.readMemory(addr2, size)

        res = e_mem.memdiff(bytes1, bytes2)
        if len(res) == 0:
            self.vprint('No Differences!')
            return

        for offset, offsize in res:
            diff1 = addr1+offset
            diff2 = addr2+offset
            self.canvas.addText('==== %d byte difference at offset %d\n' % (offsize,offset))
            self.canvas.addVaText("0x%.8x" % diff1, diff1)
            self.canvas.addText(":")
            self.canvas.addText(e_common.hexify(bytes1[offset:offset+offsize]))
            self.canvas.addText('\n')
            self.canvas.addVaText("0x%.8x" % diff2, diff2)
            self.canvas.addText(":")
            self.canvas.addText(e_common.hexify(bytes2[offset:offset+offsize]))
            self.canvas.addText('\n')

    def do_mem(self, line):
        """
        Show some memory (with optional formatting and size)

        Usage: mem [-F <format>] <addr expression> [size]
        Usage: <enter> ( show next memory chunk after previous mem cmd )

        NOTE: use -F ? for a list of the formats

        """
        fmtname = "bytes"

        if len(line) == 0:
            return self.do_help("mem")

        argv = splitargs(line)
        try:
            opts,args = getopt(argv, "F:")
        except:
            return self.do_help("mem")

        for opt,optarg in opts:
            if opt == "-F":
                fmtname = optarg
                fnames = self.canvas.getRendererNames()

                if fmtname == "?":
                    self.vprint("Registered renderers:")
                    for name in fnames:
                        self.vprint(name)
                    return

                if fmtname not in fnames:
                    self.vprint("Unknown renderer: %s" % fmtname)
                    return

        if len(args) == 0:
            return self.do_help("mem")

        size = 256
        addr = self.parseExpression(args[0])
        if len(args) == 2:
            size = self.parseExpression(args[1])

        scope = {'addr':addr}
        def showmem():
            self.canvas.setRenderer(fmtname)
            self.canvas.renderMemory(scope['addr'], size)
            scope['addr'] += size

        showmem()
        self.setEmptyMethod(showmem)


class EnviMutableCli(EnviCli):
    """
    Cli extensions which require a mutable memory object
    (emulator/trace) rather than a static one (viv workspace)
    """

    def do_memcpy(self, line):
        '''
        Copy memory from one location to another...

        Usage: memcpy <dest_expr> <src_expr> <size_expr>
        '''
        argv = splitargs(line)
        if len(argv) != 3:
            return self.do_help('memcpy')


        dst = self.parseExpression(argv[0])
        src = self.parseExpression(argv[1])
        siz = self.parseExpression(argv[2])

        mem = self.memobj.readMemory(src, siz)
        self.memobj.writeMemory(dst, mem)

    def do_memprotect(self, line):
        """
        Change the memory permissions of a given page/map.

        Usage: memprotect [options] <addr_expr> <perms>
        -S <size> Specify the size of the region to change (default == whole memory map)
        <perms> = "rwx" string "rw", "rx" "rwx" etc...
        """
        if len(line) == 0:
            return self.do_help("memprotect")

        size = None
        argv = splitargs(line)
        try:
            opts, args = getopt(argv, "S:")
        except Exception as e:
            return self.do_help("memprotect")

        for opt,optarg in opts:
            if opt == "-S":
                size = self.parseExpression(optarg)

        if len(args) != 2:
            return self.do_help("memprotect")


        addr = self.parseExpression(args[0])
        perm = e_mem.parsePerms(args[1])

        if size is None:
            map = self.memobj.getMemoryMap(addr)
            if map is None:
                raise Exception("Unknown memory map for 0x%.8x" % addr)
            size = map[1]

        self.memobj.protectMemory(addr, size, perm)

    def do_writemem(self, args):
        """
        Over-write some memory in the target address space.
        Usage: writemem [options] <addr expression> <string>
        -X    The specified string is in hex (ie 414141 = AAA)
        -U    The specified string needs to be unicode in mem (AAA -> 410041004100)
        """
        dohex = False
        douni = False

        try:
            argv = splitargs(args)
            opts,args = getopt(argv, "XU")
        except:
            return self.do_help("writemem")

        if len(args) != 2:
            return self.do_help("writemem")

        for opt,optarg in opts:
            if opt == "-X":
                dohex = True
            elif opt == "-U":
                douni = True

        exprstr, memstr = args
        if dohex:
            memstr = binascii.unhexlify(memstr)
        if douni:
            memstr = ("\x00".join(memstr)) + "\x00"

        addr = self.parseExpression(exprstr)
        self.memobj.writeMemory(addr, memstr)

