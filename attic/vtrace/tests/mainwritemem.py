import sys
import ctypes

import main

if __name__ == '__main__':
    main.waitForTest()

    buf = ctypes.create_string_buffer( 32 )
    sys.stdout.write('0x%.8x\r\n' % ctypes.addressof( buf ))
    sys.stdout.flush()

    main.safeReadline()

    sys.stdout.write('%s\n' % buf.value )
    sys.stdout.flush()

    main.exitTest()
