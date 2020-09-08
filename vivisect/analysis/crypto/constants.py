import logging
import binascii

from vivisect.const import VASET_ADDRESS, VASET_STRING

logger = logging.getLogger(__name__)


"""Locate the basic use of known crypto constants"""

dh_group1 = binascii.unhexlify("FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A63A3620FFFFFFFFFFFFFFFF")

dh_group2 = binascii.unhexlify("FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE65381FFFFFFFFFFFFFFFF")

md5_inits = [0x67452301,0xefcdab89,0x98badcfe,0x10325476]
md5_xform = [
    3614090360, 3905402710, 606105819,  3250441966, 4118548399, 1200080426,
    2821735955, 4249261313, 1770035416, 2336552879, 4294925233, 2304563134,
    1804603682, 4254626195, 2792965006, 1236535329, 4129170786, 3225465664,
     643717713, 3921069994, 3593408605, 38016083,   3634488961, 3889429448,
     568446438, 3275163606, 4107603335, 1163531501, 2850285829, 4243563512,
    1735328473, 2368359562, 4294588738, 2272392833, 1839030562, 4259657740,
    2763975236, 1272893353, 4139469664, 3200236656, 681279174,  3936430074,
    3572445317, 76029189,   3654602809, 3873151461, 530742520,  3299628645,
    4096336452, 1126891415, 2878612391, 4237533241, 1700485571, 2399980690,
    4293915773, 2240044497, 1873313359, 4264355552, 2734768916, 1309151649,
    4149444226, 3174756917, 718787259,  3951481745,
]

vlname = "Crypto Constants"

def analyze(vw):

    rows = []

    for fva in vw.getFunctions():
        md5_init_score = 0
        md5_xform_score = 0
        for va, size, funcva in vw.getFunctionBlocks(fva):
            maxva = va + size
            while va < maxva:
                loctup = vw.getLocation(va)
                if loctup is None:
                    logger.warning("error parsing through function 0x%x at 0x%x", fva, va)
                    va += 1
                    continue
                lva, lsize, ltype, tinfo = loctup

                op = vw.parseOpcode(va, arch=tinfo)
                for o in op.opers:

                    if not o.isImmed():
                        continue

                    imm = o.getOperValue(op)

                    if imm in md5_inits:
                        md5_init_score += 1

                    if imm in md5_xform:
                        md5_xform_score += 1

                va += len(op)

        if md5_init_score == len(md5_inits):
            rows.append((fva, "MD5 Init"))

        if md5_xform_score == len(md5_xform):
            rows.append((fva, "MD5 Transform"))

    for va in vw.searchMemory(dh_group1):
        rows.append((va, "DH Well-Known MODP Group 1"))

    for va in vw.searchMemory(dh_group2):
        rows.append((va, "DH Well-Known MODP Group 2"))

    if len(rows):
        vw.vprint("Adding VA Set: %s" % vlname)
        vw.addVaSet(vlname, (("va", VASET_ADDRESS), ("Match Type", VASET_STRING)), rows)

    else:
        vw.vprint("No known constants found.")
