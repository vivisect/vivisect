import sys
import argparse

import vivisect.lib.bits as v_bits
import vivisect.hal.memory as v_memory
import vivisect.lib.bexfile as v_bexfile

descr = '''
Simple command line binary executable dumper
'''

def main():
    parser = argparse.ArgumentParser(description=descr)
    #parser.add_argument('--rebase'
    parser.add_argument('--all', default=False, action='store_true')
    parser.add_argument('--imports', default=False, action='store_true')
    parser.add_argument('--exports', default=False, action='store_true')
    parser.add_argument('--memmaps', default=False, action='store_true')
    parser.add_argument('--sections', default=False, action='store_true')
    parser.add_argument('filename')

    args = parser.parse_args()

    print('')
    with open(args.filename,'rb') as fd:
        bex = v_bexfile.getBexFile(fd)

        baseaddr = bex.baseaddr()

        print('bex file: %s' % args.filename)
        print('')

        print('  arch: %s' % bex.arch())
        print('  format: %s' % bex.format())
        print('  platform: %s' % bex.platform())
        print('  file md5: %s' % v_bits.b2h(bex.md5()))
        print('  baseaddr: 0x%.8x' % (baseaddr,))
        print('  basename: %s' % bex.basename())
        print('')

        if args.imports or args.all:

            print('imports:')
            for ra,lib,func in bex.imports():
                off = bex.ra2off(ra)
                print('  0x%.8x: (off: %6d) %s %s' % (baseaddr+ra,ra,lib.ljust(20),func))
            print('')

        if args.memmaps or args.all:
            print('memory maps:')
            for ra,perms,mem in bex.memmaps():
                permstr = v_memory.reprPerms(perms)
                print('  0x%.8x %s (%d)' %  (baseaddr+ra, permstr, len(mem)))
            print('')

        if args.sections or args.all:
            print('sections:')
            for ra,size,name in bex.sections():
                print('  0x%.8x [%s] (%d)' % (baseaddr+ra,name.ljust(12),size))
            print('')

        if args.exports or args.all:
            print('exports:')
            for ra,name,etype in bex.exports():
                print('  0x%.8x (%s) %s' % (baseaddr+ra,etype.ljust(4),name))
            print('')

if __name__ == '__main__':
    sys.exit(main())
