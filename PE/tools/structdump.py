import sys
import argparse

import PE
import vtrace.platforms.win32 as vt_win32
import vstruct.builder as vs_builder


def setup():
    ap = argparse.ArgumentParser(help='Dump PE structures')
    ap.add_argument('file')
    return ap


def main(argv):
    opts = setup().parse_args(argv)
    with open(opts.file, 'rb') as f:
        p = PE.PE(f)
        baseaddr = p.IMAGE_NT_HEADERS.OptionalHeader.ImageBase
        osmajor = p.IMAGE_NT_HEADERS.OptionalHeader.MajorOperatingSystemVersion
        osminor = p.IMAGE_NT_HEADERS.OptionalHeader.MinorOperatingSystemVersion
        machine = p.IMAGE_NT_HEADERS.FileHeader.Machine

        vsver = p.getVS_VERSIONINFO()

        archname = PE.machine_names.get(machine)

        parser = vt_win32.Win32SymbolParser(0xffffffff, opts.file, baseaddr)
        parser.parse()

        t = parser._sym_types.values()
        e = parser._sym_enums.values()
        builder = vs_builder.VStructBuilder(defs=t, enums=e)

        print('# Version: %d.%d' % (osmajor, osminor))
        print('# Architecture: %s' % archname)
        if vsver is not None:
            keys = vsver.getVersionKeys()
            keys.sort()
            for k in keys:
                val = vsver.getVersionValue(k)
                print('# %s: %s' % (k, val))
        print(builder.genVStructPyCode())


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
