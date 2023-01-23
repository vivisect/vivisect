import envi.archs.mips.regs as mips_regs
import envi.archs.mips.opcode as mips_opcode

def _arithLogFormat(op, opers, shamt, mnem):
    '''
    f $d, $s, $t
    '''
    rs, rt, rd = opers

    return mnem + " " + \
           rd.repr() + ", " + \
           rs.repr() + ", " + \
           rt.repr()

def _arithLogIFormat(op, opers, mnem):
    rs, rt, imm = opers

    return mnem + " " + \
           rt.repr() + ", " + \
           rs.repr() + ", " + \
           imm.repr()

def _branchFormat(op, opers, mnem):
    rs, rt, imm = opers

    return mnem + " " + \
           rs.repr() + ", " + \
           rt.repr() + ", " + \
           imm.repr()

def _branchZFormat(op, opers, mnem):
    rs, rt, imm = opers

    return mnem + " " + \
           rs.repr() + ", " + \
           imm.repr()

def _divMultFormat(op, opers, shamt, mnem):
    '''
    f $s, $t
    '''
    rs, rt, rd = opers

    return mnem + " " + \
           rs.repr() + ", " + \
           rt.repr()

def _loadIFormat(op, opers, mnem):
    rs, rt, imm = opers

    return mnem + " " + \
           rt.repr() + ", " + \
           imm.repr()

# JL TODO does this need a different oper type?
def _jumpFormat(op, opers, mnem, pc=0):
    addr, = opers

    addr_shifted = addr << 2
    pc_shifted = pc << 28 # pc-relative addressing

    return mnem + " " + \
           str(hex(pc_shifted + addr_shifted))

def _jumpRFormat(op, opers, shamt, mnem):
    '''
    f $s
    '''
    rs, rt, rd = opers

    return mnem + " " + \
           rs.repr()

# JL TODO does this need a different oper type?
def _loadStoreFormat(op, opers, mnem):
    rs, rt, imm = opers

    return mnem + " " + \
           rt.repr() + ", " + \
           imm.repr() + \
           "(" + rs.repr() + ")"

def _moveFromFormat(op, opers, shamt, mnem):
    '''
    f $d
    '''
    rs, rt, rd = opers

    return mnem + " " + \
           rd.repr()

def _moveToFormat(op, opers, shamt, mnem):
    '''
    f $s
    '''
    rs, rt, rd = opers

    return mnem + " " + \
           rs.repr()

def _shiftFormat(op, opers, shamt, mnem):
    '''
    f $d, $t, a
    '''
    rs, rt, rd = opers

    return mnem + " " + \
           rd.repr() + ", " + \
           rt.repr() + ", " + \
           str(shamt) #JL need to address this

def _shiftVFormat(op, opers, shamt, mnem):
    '''
    f $d, $t, $s
    '''
    rs, rt, rd = opers

    return mnem + " " + \
           rd.repr() + ", " + \
           rt.repr() + ", " + \
           rs.repr()

def _trapFormat(op, opers, shamt, mnem):
    imm, = opers

    return mnem + imm.repr()

def _syscallFormat(op, opers, shamt, mnem):
    return mnem


######################################################################
#  Mcanv parsers
######################################################################
def _RegularOperRender(mcanv, mnem, opers):
    mcanv.addNameText(mnem, typename="mnemonic")
    mcanv.addText(" ")

    imax = len(opers)
    lasti = imax - 1
    for i in range(imax):
        oper = opers[i] # JL will this work with the updated Operand setup?
        oper.render(mcanv, self, i)
        if i != lasti:
            mcanv.addText(",")

def _OneOperRender(mcanv, mnem, oper):
    mcanv.addNameText(mnem, typename="mnemonic")
    mcanv.addText(" ")
    oper.render(mcanv, self, 0)

def _arithLogRender(mcanv, op, opers, shamt, mnem):
    _RegularOperRender(mcanv, mnem, opers)

def _arithLogIRender(mcanv, op, opers, mnem):
    rs, rt, imm = opers
    _RegularOperRender(mcanv, mnem, [rt,rs,str(hex(imm))])

def _branchRender(mcanv, op, opers, mnem):
    rs, rt, imm = opers
    _RegularOperRender(mcanv, mnem, [rs,rt,str(hex(imm))])

def _branchZRender(mcanv, op, opers, mnem):
    rs, rt, imm = opers
    _RegularOperRender(mcanv, mnem, [rs,str(hex(imm))])

def _divMultRender(mcanv, op, opers, shamt, mnem):
    rs, rt, rd = opers
    _RegularOperRender(mcanv, mnem, [rs,rt,str(hex(imm))])

def _loadIRender(mcanv, op, opers, mnem):
    rs, rt, imm = opers
    _RegularOperRender(mcanv, mnem, [rt,str(hex(imm))])

def _jumpRender(mcanv, op, opers, mnem, pc=0):
    addr, = opers

    addr_shifted = addr << 2
    pc_shifted = pc << 28 # pc-relative addressing

    _OneOperRender(mcanv, mnem, str(hex(pc_shifted + addr_shifted)))

def _jumpRRender(mcanv, op, opers, shamt, mnem):
    rs, rt, rd = opers
    _OneOperRender(mcanv, mnem, rs)

def _loadStoreRender(mcanv, op, opers, mnem):
    rs, rt, imm = opers
    indexed = imm.repr() + "(" + rs.repr() + ")" # JL TODO does this need a different oper type?
    _RegularOperRender(mcanv, mnem, [rt, indexed])

def _moveFromRender(mcanv, op, opers, shamt, mnem):
    rs, rt, rd = opers
    _OneOperRender(mcanv, mnem, rd)

def _moveToRender(mcanv, op, opers, shamt, mnem):
    rs, rt, rd = opers
    _OneOperRender(mcanv, mnem, rs)

def _shiftRender(mcanv, op, opers, shamt, mnem):
    rs, rt, rd = opers

    _RegularOperRender(mcanv, mnem, [rd, rt, shamt])

def _shiftVRender(mcanv, op, opers, shamt, mnem):
    _RegularOperRender(mcanv, mnem, opers)

def _trapRender(mcanv, op, opers, shamt, mnem):
    imm, = opers
    _OneOperRender(mcanv, mnem, imm)

def _syscallRender(mcanv, op, opers, shamt, mnem):
    mcanv.addNameText(mnem, typename="mnemonic")

######################################################################
# Create a lookup array of format parsers, which we'll access
# via index in disasm.py
######################################################################

formatParsers = (
    _arithLogFormat,
    _arithLogIFormat,
    _divMultFormat,
    _shiftFormat,
    _shiftVFormat,
    _loadIFormat,
    _branchFormat,
    _branchZFormat,
    _jumpFormat,
    _jumpRFormat,
    _loadStoreFormat,
    _moveFromFormat,
    _moveToFormat,
    _trapFormat,
    _syscallFormat
)

renderParsers = (
    _arithLogRender,
    _arithLogIRender,
    _divMultRender,
    _shiftRender,
    _shiftVRender,
    _loadIRender,
    _branchRender,
    _branchZRender,
    _jumpRender,
    _jumpRRender,
    _loadStoreRender,
    _moveFromRender,
    _moveToRender,
    _trapRender,
    _syscallRender
)
