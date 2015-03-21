import os
import msgpack
from binascii import hexlify

if msgpack.version < (0,4,2):
    raise Exception('synapse requires msgpack >= 0.4.2')

def guid():
    return os.urandom(16)

