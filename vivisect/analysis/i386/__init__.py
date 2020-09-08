"""
Some utilities related to i386 analysis.  Loaders and analysis
modules may use these as needed...
"""

import binascii

sigs = [
    ("558bec", "ffffff"),  # push ebp; mov ebp,esp; Intel/Microsoft
    ("568bf1", "ffffff"),  # push esi; mov esi,ecx (c++)
    ("5589e5", "ffffff"),  # push ebp; mov ebp,esp; GCC
    ("8bff558bec", "ffffffffff"),  # mov edi,edi; push ebp; mov epb, esp
    # Ok... here's where things get cool...
    # This is push <imm8>, push <imm32>, call <somewhere> # ms seh setup entry
    ("6a006800000000e8", "ff00ff00000000ff")
]


def addEntrySigs(vw):
    for sigstr, maskstr in sigs:
        bytez = binascii.unhexlify(sigstr)
        masks = binascii.unhexlify(maskstr)
        vw.addFunctionSignatureBytes(bytez, masks)
