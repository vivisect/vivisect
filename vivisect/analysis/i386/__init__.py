"""
Some utilities related to i386 analysis.  Loaders and analysis
modules may use these as needed...
"""

sigs = [
    (b"558bec", b"ffffff"),  # push ebp; mov ebp,esp; Intel/Microsoft
    (b"568bf1", b"ffffff"),  # push esi; mov esi,ecx (c++)
    (b"5589e5", b"ffffff"),  # push ebp; mov ebp,esp; GCC
    (b"8bff558bec", b"ffffffffff"),  # mov edi,edi; push ebp; mov epb, esp
    # Ok... here's where things get cool...
    # This is push <imm8>, push <imm32>, call <somewhere> # ms seh setup entry
    (b"6a006800000000e8", b"ff00ff00000000ff")
]


def addEntrySigs(vw):
    for bytes, masks in sigs:
        vw.addFunctionSignatureBytes(bytes, masks)
