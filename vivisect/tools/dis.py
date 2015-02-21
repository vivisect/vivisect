import sys
import argparse

import vivisect.hal.cpu as v_cpu
import vivisect.lib.bits as v_bits

descr = '''
Simple command line byte disassembler.
'''

def main():
    parser = argparse.ArgumentParser(description=descr)
    # FIXME current arch
    parser.add_argument('--arch', dest='arch', default='i386',help='specify a vivisect arch')
    parser.add_argument('--addr', dest='addr', default='0', help='specify a base address')
    parser.add_argument('hexbytes')

    args = parser.parse_args()

    addr = int(args.addr,0)
    instbytes = v_bits.h2b(args.hexbytes)

    cpu = v_cpu.getArchCpu(args.arch,addmap=(addr,7,4096))
    cpu[addr:] = instbytes

    offset = 0
    while offset < len(instbytes):
        inst = cpu.disasm(addr + offset)
        print(repr(inst))
        offset += inst.size()

if __name__ == '__main__':
    sys.exit(main())
