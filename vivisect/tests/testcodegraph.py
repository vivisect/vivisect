import binascii
import unittest

import vivisect
import vivisect.codegraph as codegraph
import vivisect.tests.samplecode as samplecode
'''
bits 32

foo:
    push ebp
    mov ebp, esp
    mov ecx,[ebp+8]
    xor edx,edx
    cmp ecx,edx
    jz bar

    mov eax, 1

bar:
    mov eax, 2

baz:
    mov esp, ebp
    pop ebp
    ret
'''

func1 = binascii.unhexlify('5589e58b4d0831d239d17405b801000000b80200000089ec5dc3')

# TODO: Flesh these out, since this isn't a test of anything right now
class GraphCoreTest(unittest.TestCase):

    def test_vivisect_codegraph_func1(self):
        vw = vivisect.VivWorkspace()
        vw.setMeta('Architecture','i386')
        vw.addMemoryMap(0x41410000, 0xff, 'none', samplecode.func1)
        vw.makeFunction(0x41410000)

