'''
Convert from one vivisect storage format to another.
'''

import os
import sys
import argparse

import vivisect
import vivisect.parsers as v_parsers

storemap = {
    'viv': 'vivisect.storage.basicfile',
    'mpviv': 'vivisect.storage.mpfile',
}


def setup():
    ap = argparse.ArgumentParser('Convert from one workspace format to another')

    ap.add_argument('old', help='Path to older workspace')
    ap.add_argument('--name', '-n', help='Name for the new workspace')

    return ap


def convert(old, newname):
    oldfmt = v_parsers.guessFormatFilename(old)
    vw = vivisect.VivWorkspace()
    if oldfmt not in storemap:
        print('Refusing to handle format %s, this is for workspace files only!')
        return -1

    newfmt = 'mpviv'
    if oldfmt == 'mpviv':
        newfmt = 'viv'

    if not newname:
        newname = '%s.%s' % (old, newfmt)

    oldstor = storemap[oldfmt]
    newstor = storemap[newfmt]

    vw.setMeta('StorageModule', oldstor)
    vw.loadWorkspace(old)

    vw.setMeta('StorageModule', newstor)
    vw.setMeta('StorageName', newname)
    vw.saveWorkspace()


def main(argv):
    opts = setup().parse_args(argv)

    old = os.path.abspath(opts.old)

    convert(old, opts.name)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
