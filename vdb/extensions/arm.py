import envi
import envi.cli as e_cli
import envi.common as e_common
import envi.archs.arm.regs as e_arm_regs
import envi.archs.thumb16.disasm as e_thumb

def armdis(db, line):
    '''
    Disassemble arm instructions from the given address.

    Usage: armdis <addr_exp>
    '''
    disasmobj = e_arm.ArmDisasm()
    armthumdis(db, line, disasmobj)

def thumbdis(db, line):
    '''
    Disassemble thumb instructions from the given address.

    Usage: thumbdis <addr_exp>
    '''
    disasmobj = e_thumb.ThumbDisasm()
    armthumdis(db, line, disasmobj)


def armthumbdis(db, line, disasmobj):
    '''
    Core of disassmbly, for code-reuse.  Only difference is the object actually
    doing the disassembly.
    '''
    t = db.getTrace()

    argv = e_cli.splitargs(line)
    size = 20
    argc = len(argv)
    if argc == 0:
        addr = t.getProgramCounter()
    else:
        addr = t.parseExpression(argv[0])

    if argc > 1:
        size = t.parseExpression(argv[1])

    bytez = t.readMemory(addr, size)
    offset = 0

    db.vprint("Dissassembly:")
    while offset < size:
        va = addr + offset
        op = disasmobj.disasm(bytez, offset, va)
        obytez = bytez[offset:offset+len(op)]

        db.canvas.addVaText('0x%.8x' % va, va=va)
        db.canvas.addText(": %s " % e_common.hexify(obytez).ljust(17))
        op.render(db.canvas)
        db.canvas.addText("\n")

        offset += len(op)

def togglethumb(db, line):
    '''
    Toggle Thumb Mode
    '''
    t = db.getTrace()
    cur_t = t.getRegister(e_arm_regs.REG_T)
    new_t = not cur_t
    arch = (envi.ARCH_ARMV7, envi.ARCH_THUMB)[new_t]
    t.setRegister(e_arm_regs.REG_T, new_t)

    db.canvas.addText("Toggled Thumb Mode: %r\n" % new_t)

def vdbExtension(vdb, trace):
    vdb.addCmdAlias('db', 'mem -F bytes')
    vdb.addCmdAlias('dw', 'mem -F u_int_16')
    vdb.addCmdAlias('dd', 'mem -F u_int_32')
    vdb.addCmdAlias('dq', 'mem -F u_int_64')
    vdb.addCmdAlias('dr', 'mem -F "Deref View"')
    vdb.addCmdAlias('ds', 'mem -F "Symbols View"')
    vdb.registerCmdExtension(armdis)
    vdb.registerCmdExtension(thumbdis)
    vdb.registerCmdExtension(togglethumb)
