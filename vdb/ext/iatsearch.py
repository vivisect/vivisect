import re
import shlex

def iatsearch(db, line):
    '''
    Searches memory maps for fname that matches the regex for pointers
    that we have a symbol for.

    The search is extremely naiive and could look for the chains as we do in
    walkIAT in the pedump script.

    Assumes the tables are aligned with the base of the memory map.

    This could take a long time if you end up scanning a large portion of
    memory.

    Usage: iatsearch calc

    Output format is base, va, sym.  Examine output and then supply what you
    think is the base of the IAT to pedump.(you may be looking at multiple IATs)
    '''
    argv = shlex.split(line)
    if len(argv) < 1:
        return db.do_help('iatsearch')

    trace = db.getTrace()
    for base, size, perms, fname in trace.getMemoryMaps():

        if re.search(argv[0], fname, re.IGNORECASE) == None:
            continue

        db.vprint('searching %s 0x%.8x 0x%.8x' % (fname, base, size))

        entries = []
        # xrange/range makes perf optimizations that doesn't work with 64bit
        # numbers with python 2.x. so...do it the non-pretty way.
        #for va in xrange(base, base + size, trace.getPointerSize()):
        va = base
        while va < base + size:
            ptr = trace.parseExpression('poi(%d)' % (va,))
            sym = trace.getSymByAddr(ptr)
            if sym != None:
                db.vprint('0x%.8x 0x%.8x %s' % (base, va, sym))

            va += trace.getPointerSize()

    db.vprint('done.')

def vdbExtension(db, trace):
    db.registerCmdExtension(iatsearch)
