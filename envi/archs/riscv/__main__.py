import sys
import struct
import argparse

import envi
import vivisect

import logging


# Force the asnycio and parso modules to not use the standard logging level
logging.getLogger('parso').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def parseBytes(value, size=4):
    if size ==4:
        fmt = ('<I', '>I')[emu.getEndian()]
        data = struct.pack(fmt, value)
    else:
        fmt = ('<H', '>H')[emu.getEndian()]
        data = struct.pack(fmt, value)

    return emu.archParseOpcode(data)


def start(_archname=None, _verbose=0):
    vw = vivisect.VivWorkspace()

    if vw is None:
        print('ERROR: %s is not implemented' % _archname)
        sys.exit(-1)

    # Copied from vivisect/parsers/blob.py
    vw.setMeta('Architecture', _archname)
    vw.setMeta('Platform', 'unknown')
    vw.setMeta('Format', 'blob')
    vw.setMeta('bigend', envi.const.ENDIAN_LSB)
    #vw.setMeta('DefaultCall', vivisect.const.archcalls.get(_archname, 'unknown'))

    # setup logging
    vw.verbose = min(_verbose, len(envi.common.LOG_LEVELS)-1)
    level = envi.common.LOG_LEVELS[vw.verbose]
    envi.common.initLogging(logger, level=level)

    print('workspace arch set to %s' % _archname)
    emu = vw.getEmulator()

    from IPython import embed
    embed(colors='neutral')


def main():
    parser = argparse.ArgumentParser()

    arch_list = [n for n in envi.arch_names.values()]
    parser.add_argument('-a', '--arch', default='rv32', choices=arch_list)
    parser.add_argument('-v', '--verbose', dest='verbose', default=False, action='count',
                        help='Enable verbose mode (multiples matter: -vvvv)')

    args = parser.parse_args()

    start(args.arch, int(args.verbose))


main()
