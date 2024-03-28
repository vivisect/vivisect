import sys
import json
import argparse

import vivisect
import vivisect.const as v_const


def setup():
    ap = argparse.ArgumentParser('Analyze a binary and dump certain features to json')
    ap.add_argument('path', help='Path to binary file to dump features')
    ap.add_argument('--output', default='features.json')
    return ap


def dumpFunctions(vw):
    ret = {}
    for fva in vw.getFunctions():
        # fva: (size, instruction count, code blocks
        size = vw.getFunctionMeta(fva, 'Size')
        inst = vw.getFunctionMeta(fva, 'InstructionCount')
        blks = vw.getFunctionBlocks(fva)

        ret[fva] = (size, inst, blks)

    return ret


def main(argv):
    opts = setup().parse_args(argv)

    vw = vivisect.VivWorkspace()
    vw.loadFromFile(opts.path)
    vw.analyze()

    retn = {}
    retn['functions'] = dumpFunctions(vw)
    retn['entrypoints'] = vw.getEntryPoints()
    retn['pointers'] = vw.getLocations(ltype=v_const.LOC_POINTER)
    retn['strings'] = vw.getLocations(ltype=v_const.LOC_STRING)
    retn['unicode'] = vw.getLocations(ltype=v_const.LOC_UNI)
    retn['imports'] = vw.getLocations(ltype=v_const.LOC_IMPORT)
    retn['exports'] = vw.getExports()
    retn['names'] = vw.getNames()
    retn['xrefs'] = vw.getXrefs()
    retn['relocations'] = vw.getRelocations()

    with open(opts.output, 'w') as fd:
        json.dump(retn, fd, indent=4)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
