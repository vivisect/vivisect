'''
For now, all this does is rename files to their exportname and version info.
(more to come is likely)
'''

import sys
import code
import optparse
import binascii

import PE

def main():

    parser = optparse.OptionParser()
    parser.add_option('--version', dest='version', default=False, action='store_true')
    parser.add_option('--resources', dest='resources', default=False, action='store_true')

    opts, argv = parser.parse_args()

    for fname in argv:

        print('Parsing: %s' % fname)

        vsver = None
        expname = None

        pe = PE.peFromFileName(fname)

        if opts.resources:
            print('Type Nameid - rva size sample')
            for rtype, nameid, (rva, size, codepage) in pe.getResources():
                hexstr = binascii.hexlify(pe.readAtRva(rva, max(size, 8)))
                print('0x%.4x 0x%.4x - 0x%.8x 0x%.8x %s' % (rtype, nameid, rva, size, hexstr))

        if opts.version:
            vs = pe.getVS_VERSIONINFO()
            if vs is None:
                print('No VS_VERSIONINFO found!')

            else:
                keys = vs.getVersionKeys()
                keys.sort()
                for k in keys:
                    val = vs.getVersionValue(k)
                    print('%s: %r' % (k, val))

        code.interact(local=locals())


if __name__ == "__main__":
    sys.exit(main())
