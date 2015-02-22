import sys
import hashlib
import argparse

import vivisect.vivstor as v_vivstor
import vivisect.workspace as v_workspace

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--vivstor', default=None, help='VivStor compatible URI to locate workspaces (default: ~/.vivstor)')
    #parser.add_argument('--delstor', 
    parser.add_argument('filename')
    args = parser.parse_args()

    vivstor = v_vivstor.getVivStor(uri=args.vivstor)

    filehash = hashlib.md5( open(args.filename,'rb').read() ).digest()

    idents = vivstor.findVivWork(filehash)

    print('FILEHASH: %r' % (filehash,))

if __name__ == '__main__':
    sys.exit(main())
