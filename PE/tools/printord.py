'''
Quick utility to generate ord lookups from DLL exports.
'''

import sys
import argparse

import PE


def setup():
    ap = argparse.ArgumentParser('Quick Utility to generate ordlookups from DLLs')
    ap.add_argument('file', help='Path to PE file')
    return ap


def main(argv):
    opts = setup().parse_args(argv)
    with open(opts.file, 'rb') as f:
        p = PE.PE(f)

        base = p.IMAGE_EXPORT_DIRECTORY.Base

        ords = {}
        for fva, ord, name in p.getExports():
            ords[ord+base] = name

        keys = list(ords.keys())
        for k in keys.sort():
            print('    %d:"%s",' % (k, ords.get(k)))


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
