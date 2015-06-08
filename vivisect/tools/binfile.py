import sys
import argparse

import vivisect.lib.bits as v_bits
import vivisect.hal.memory as v_memory
import vivisect.lib.binfile as v_binfile

descr = '''
Simple command line binary executable dumper
'''

def main():
    parser = argparse.ArgumentParser(description=descr)
    #parser.add_argument('--rebase'
    parser.add_argument('--all', default=False, action='store_true')
    parser.add_argument('--mmaps', default=False, action='store_true')
    parser.add_argument('--imports', default=False, action='store_true')
    parser.add_argument('--exports', default=False, action='store_true')
    parser.add_argument('--sections', default=False, action='store_true')
    parser.add_argument('filename')

    args = parser.parse_args()

    print('')
    with open(args.filename,'rb') as fd:
        bif = v_binfile.getBexFile(fd)

        baseaddr = bif.baseaddr()

        print('bin file: %s' % args.filename)
        print('')

        print('  arch: %s' % bif.arch())
        print('  format: %s' % bif.format())
        print('  platform: %s' % bif.platform())
        print('  file md5: %s' % v_bits.b2h(bif.md5()))
        print('  baseaddr: 0x%.8x' % (baseaddr,))
        print('  basename: %s' % bif.basename())
        print('')

        if args.imports or args.all:

            print('imports:')
            for ra,lib,func in bif.imports():
                off = bif.ra2off(ra)
                print('  0x%.8x: (off: %6d) %s %s' % (baseaddr+ra,ra,lib.ljust(20),func))
            print('')

        if args.mmaps or args.all:
            print('memory maps:')
            for mmap in bif.mmaps():
                size = mmap[1].get('size')
                permstr = v_memory.reprPerms(mmap[1].get('perm'))
                print('  0x%.8x %s (%d)' %  (baseaddr+ra, permstr, size))
            print('')

        if args.sections or args.all:
            print('sections:')
            for ra,size,name in bif.sections():
                print('  0x%.8x [%s] (%d)' % (baseaddr+ra,name.ljust(12),size))
            print('')

        if args.exports or args.all:
            print('exports:')
            for ra,name,etype in bif.exports():
                print('  0x%.8x (%s) %s' % (baseaddr+ra,etype.ljust(4),name))
            print('')

if __name__ == '__main__':
    sys.exit(main())
