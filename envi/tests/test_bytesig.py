import unittest
import envi.bytesig

class SignatureTests(unittest.TestCase):
    def test_signature_subset(self):
        signature_base = b'\x55\xe9\xd8\x01\xfe\xff\x32\x77\x89\x4f\x55'
        sigtree = envi.bytesig.SignatureTree()
        sigtree.addSignature(signature_base)

        sigtree.getSignature(b'\x55\xe9')
        sigtree.addSignature(signature_base[:7], val=signature_base[:7])
        sigtree.addSignature(signature_base[:4], val=signature_base[:4])
        sigtree.addSignature(signature_base + b'\xfe\x38', val=signature_base + b'\xfe\x38')

        self.assertTrue(sigtree.getSignature(b'\x55\xe9\xd8\x01\xfe\xff\x32\x00\x99\x36\x5f\x21\xfd') == signature_base[:7])
        self.assertTrue(sigtree.getSignature(b'\x55\xe9\xd8\x01\xfe\xff\x32') == signature_base[:7])
        self.assertTrue(sigtree.getSignature(b'\x55\xe9\xd8\x01\xfe\x00') == signature_base[:4])
        self.assertTrue(sigtree.getSignature(b'\x55') is None)
