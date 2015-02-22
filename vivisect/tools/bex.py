import sys
import argparse

import vivisect.lib.bexfile as v_bexfile

descr = '''
Simple command line binary executable dumper
'''

def main():
    parser = argparse.ArgumentParser(description=descr)
    #parser.add_argument('--rebase'
    parser.add_argument('--imports', default=False, action='store_true')
    parser.add_argument('filename')

    args = parser.parse_args()

    with open(args.filename,'rb') as fd:
        bex = v_bexfile.getBexFile(fd)

        baseaddr = bex.baseaddr()
        print('baseaddr: 0x%.8x' % (baseaddr,))

        if args.imports:

            print('imports:')
            for ra,lib,func in bex.imports():
                off = bex.ra2off(ra)
                print('    0x%.8x: (off: %6d) %s %s' % (baseaddr+ra,ra,lib.ljust(20),func))

if __name__ == '__main__':
    sys.exit(main())
