import sys
import tempfile
import subprocess

import vivisect.hal.cpu as v_cpu
import vivisect.lib.bits as v_bits

# this is some ghetto code to compare viv dis with ndisasm

def main():
    b = v_bits.h2b(sys.argv[1])

    f = tempfile.NamedTemporaryFile('w+b')
    f.write(b)
    f.flush()

    n = subprocess.check_output(['ndisasm','-b','32',f.name]).decode('utf8')
    print(n.strip().lower())

    cpu = v_cpu.getArchCpu('i386',addmap=(0,7,4096))
    cpu[0:] = b
    inst = cpu.disasm(0)
    print(repr(inst)[2:].lower().strip())

if __name__ == '__main__':
    sys.exit(main())
