# XXX(rakuyo): move to a tools directory

import sys
import code
import argparse

import PE


def main(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument('--version', dest='version', default=False, action='store_true')
    parser.add_argument('--resources', dest='resources', default=False, action='store_true')
    parser.add_argument('--files', dest='files', nargs='+')

    opts = parser.parse_args(argv)

    for fname in opts.files:

        print('Parsing: %s' % fname)

        with PE.peFromFileName(fname) as pe:
            if opts.resources:
                print('Type Nameid - rva size sample')
                for rtype, nameid, (rva, size, codepage) in pe.getResources():
                    hexstr = pe.readAtRva(rva, max(size, 8)).encode('hex')
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
    sys.exit(main(sys.argv[1:]))
