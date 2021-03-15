'''
A very simple tool for generating import API definitions from a viv
workspace...
'''

import sys
import argparse

import vivisect


type_lookup = {
    'Unknown': 'int',
    'Pointer': 'void *',
    'FUNCPTR': 'void *',
    'ObjectRef': 'void *',
}

name_lookup = {
    'DWORD': None,
    'Unknown': None,
    'Pointer': 'ptr',
    'ObjectRef': 'obj',
    'FUNCPTR': 'funcptr'
}


def setup():
    ap = argparse.ArgumentParser('Generating impapi definitions from a vivisect workspace')
    ap.add_argument('vw', help='Path to vivisect workspace')
    return ap


def main(argv):

    opts = setup().parse_args(argv)
    vw = vivisect.VivWorkspace()
    vw.loadWorkspace(opts.vw)

    print('# %s' % opts.vw)

    fnames = {}

    for fva, etype, ename, fname in vw.getExports():

        enamekey = ename.lower()
        fnamekey = fname.lower()

        fnames[fname] = True

        # Skip past forwarders
        if not vw.isFunction(fva):
            continue

        rtype, rname, ccname, funcname, args = vw.getFunctionApi(fva)
        args = tuple([(type_lookup.get(t, t), name_lookup.get(t)) for t, name in args])
        print("    '%s.%s':( %r, None, %r, '%s.%s', %r )," % (fnamekey, enamekey, rtype, ccname, fname, ename, args))

    for fwdfname in fnames.keys():

        for rva, name, fwdname in vw.getFileMeta(fwdfname, 'forwarders', ()):
            fwdapi = vw.getImpApi(fwdname)
            if not fwdapi:
                print('    # FIXME unresolved %s -> %s' % (name, fwdname))
                continue

            print("    '%s.%s':%r," % (fwdfname.lower(), name.lower(), fwdapi))


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
