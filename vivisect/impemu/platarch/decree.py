import envi.archs.i386 as e_i386
import vivisect.impemu.emulator as v_i_emulator

decree_syscalls = [
    None,
    "_terminate",
    "transmit",
    "receive",
    "fdwait",
    "allocate",
    "deallocate",
    "random",
    ]

for x in range(len(decree_syscalls)):
    callname = decree_syscalls[x]
    if callname == None:
        continue

    varname = "SYS_%s" % (callname.upper())
    globals()[varname] = x


class Decreei386WorkspaceEmulator(v_i_emulator.WorkspaceEmulator, e_i386.IntelEmulator):
    # do we want to inherit from i386WorkspaceEmulator instead?

    taintregs = [ 
        e_i386.REG_EAX, e_i386.REG_ECX, e_i386.REG_EDX,
        e_i386.REG_EBX, e_i386.REG_EBP, e_i386.REG_ESI,
        e_i386.REG_EDI,
    ]

    def __init__(self, vw, logwrite=False, logread=False):
        e_i386.IntelEmulator.__init__(self)
        v_i_emulator.WorkspaceEmulator.__init__(self, vw, logwrite=logwrite, logread=logread)
        self.setEmuOpt('i386:reponce',True)

    def i_int(self, op):
        interrupt = op.getOperValue(0, emu=self)
        if interrupt != 0x80:
            logger.info("0x%x:   INT 0x%" % (op.va, interrupt))
            return

        fva = self.vw.getFunction(op.va)
        syscall = self.getRegister(e_i386.REG_EAX)
        sysname = decree_syscalls[syscall]

        fname = self.vw.getName(fva)
        newfname = "%s_%.8x" % (sysname, fva)

        if fname != None:
            print "renaming %s --> %s" % (fname, newfname)
        self.vw.makeName(fva, newfname)
        self.vw.setComment(op.va, sysname)

        if syscall == SYS__TERMINATE:
            self.vw.addNoReturnCallApi(newfname)
            self.stopEmu()


