import envi.archs.h8.const as h8_const
import envi.registers as e_reg

h8_regs = (
    ('er0', 32),
    ('er1', 32),
    ('er2', 32),
    ('er3', 32),
    ('er4', 32),
    ('er5', 32),
    ('er6', 32),
    ('sp', 32),
    ('pc', 24),
    ('ccr', 8),
    ('exr', 8),
)


l = locals()
e_reg.addLocalEnums(l, h8_regs)

REG_CCR_T = 7
REG_CCR_U1 = 6
REG_CCR_H = 5
REG_CCR_U0 = 4
REG_CCR_N = 3
REG_CCR_Z = 2
REG_CCR_V = 1
REG_CCR_C = 0

ccr_fields = [
    REG_CCR_C,
    REG_CCR_V,
    REG_CCR_Z,
    REG_CCR_N,
    REG_CCR_U0,
    REG_CCR_H,
    REG_CCR_U1,
    REG_CCR_T,
]

H8StatMeta = tuple([
    ("N", h8_const.REG_FLAGS, REG_CCR_N, 1, 'Negative'),
    ("Z", h8_const.REG_FLAGS, REG_CCR_Z, 1, 'Zero'),
    ("C", h8_const.REG_FLAGS, REG_CCR_C, 1, 'Carry'),
    ("V", h8_const.REG_FLAGS, REG_CCR_V, 1, 'oVerflow'),
    ("U0", h8_const.REG_FLAGS, REG_CCR_U0, 1, 'User 0'),
    ("U1", h8_const.REG_FLAGS, REG_CCR_U1, 1, 'User 0'),
    ("T", h8_const.REG_FLAGS, REG_CCR_T, 1, 'T'),
    ("H", h8_const.REG_FLAGS, REG_CCR_H, 1, 'Half Carry'),
    ])


H8Meta = [
    ('r0', REG_ER0, 0, 16),
    ('e0', REG_ER0, 16, 16),
    ('r0h', REG_ER0, 8, 8),
    ('r0l', REG_ER0, 0, 8),
    ('r1', REG_ER1, 0, 16),
    ('e1', REG_ER1, 16, 16),
    ('r1h', REG_ER1, 8, 8),
    ('r1l', REG_ER1, 0, 8),
    ('r2', REG_ER2, 0, 16),
    ('e2', REG_ER2, 16, 16),
    ('r2h', REG_ER2, 8, 8),
    ('r2l', REG_ER2, 0, 8),
    ('r3', REG_ER3, 0, 16),
    ('e3', REG_ER3, 16, 16),
    ('r3h', REG_ER3, 8, 8),
    ('r3l', REG_ER3, 0, 8),
    ('r4', REG_ER4, 0, 16),
    ('e4', REG_ER4, 16, 16),
    ('r4h', REG_ER4, 8, 8),
    ('r4l', REG_ER4, 0, 8),
    ('r5', REG_ER5, 0, 16),
    ('e5', REG_ER5, 16, 16),
    ('r5h', REG_ER5, 8, 8),
    ('r5l', REG_ER5, 0, 8),
    ('r6', REG_ER6, 0, 16),
    ('e6', REG_ER6, 16, 16),
    ('r6h', REG_ER6, 8, 8),
    ('r6l', REG_ER6, 0, 8),
    ('r7', REG_SP, 0, 16),
    ('e7', REG_SP, 16, 16),
    ('r7h', REG_SP, 8, 8),
    ('r7l', REG_SP, 0, 8),
    ('er7', REG_SP, 0, 32),
]


def metaFrom8(regidx):
    width = 8
    extended = regidx >> 3
    offset = (width, 0)[extended]

    idx = regidx & 0x7
    idx |= (width << 16)
    idx |= (offset << 24)

    return idx


def metaFrom16(regidx):
    width = 16
    extended = regidx >> 3
    offset = (0, width)[extended]

    idx = regidx & 0x7
    idx |= (width << 16)
    idx |= (offset << 24)

    return idx


converters = (
        None,
        metaFrom8,
        metaFrom16,
        None,
        None,
        )


def convertMeta(regidx, tsize):
    converter = converters[tsize]
    if converter is None:
        return regidx
    return converter(regidx)


e_reg.addLocalStatusMetas(l, H8Meta, H8StatMeta, 'CCR')


class H8RegisterContext(e_reg.RegisterContext):
    def __init__(self):
        e_reg.RegisterContext.__init__(self)
        self.loadRegDef(h8_regs)
        self.loadRegMetas(H8Meta, statmetas=H8StatMeta)
        self.setRegisterIndexes(REG_PC, h8_const.REG_SP, REG_CCR)
