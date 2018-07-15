import struct
import envi.archs.ppc.disasm as eapd
d = eapd.PpcDisasm()
out = []
for key,instrlist in eapd.instr_dict.items():
    for instrline in instrlist:
        opcodenum = instrline[1]
        opbin = struct.pack(">I", opcodenum)
        try:
            op = d.disasm(opbin, 0, 0x4000)
            print "0x%.8x:  %s" % (opcodenum, op)
        except Exception, e:
            print "ERROR with opcode 0x%x: %r" % (opcodenum, e)
        out.append(opbin)
file("test_ppc.bin", "wb").write("".join(out))
