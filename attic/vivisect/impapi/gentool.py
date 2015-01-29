'''
A very simple tool for generating import API definitions from a viv
workspace...
'''
import sys
import vivisect

type_lookup = {
    'Unknown':'int',
    'Pointer':'void *',
    'FUNCPTR':'void *',
    'ObjectRef':'void *',
}

name_lookup = {
    'DWORD':None,
    'Unknown':None,
    'Pointer':'ptr',
    'ObjectRef':'obj',
    'FUNCPTR':'funcptr'
}

def main():

    sys.stdout.write("# ")
    vw = vivisect.VivWorkspace()
    vw.loadWorkspace(sys.argv[1])

    print '# %s' % sys.argv[1]

    fnames = {}

    for fva, etype, ename, fname in vw.getExports():

        enamekey = ename.lower()
        fnamekey = fname.lower()

        fnames[fname] = True

        # Skip past forwarders
        if not vw.isFunction(fva):
            continue

        
        rtype, rname, ccname, funcname, args = vw.getFunctionApi(fva)
        argv = tuple([ (type_lookup.get(t, t), name_lookup.get(t)) for t,name in args ])
        #argv = tuple([ (type_lookup.get(t.__name__, t.__name__), name_lookup.get(t.__name__)) for t,name in vw.getFunctionArgs(fva) ])
        #rtype = vw.getFunctionMeta(fva, 'ReturnType', 'int')
        #ccname = vw.getFunctionMeta(fva, 'CallingConvention')
        print "    '%s.%s':( %r, None, %r, '%s.%s', %r )," % (fnamekey,enamekey,rtype,ccname,fname,ename,argv)

    for fwdfname in fnames.keys():

        for rva, name, fwdname in vw.getFileMeta(fwdfname, 'forwarders', ()):
            fwdapi = vw.getImpApi( fwdname )
            if not fwdapi:
                print('    # FIXME unresolved %s -> %s' % (name, fwdname))
                continue

            print("    '%s.%s':%r," % ( fwdfname.lower(), name.lower(), fwdapi))

if __name__ == '__main__':
    sys.exit(main())

