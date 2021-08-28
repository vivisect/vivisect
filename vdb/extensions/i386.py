import shlex
import envi.archs.i386 as e_i386

def eflags(vdb, line):
    '''
    Shows or flips the status of the eflags register bits.

    Usage: eflags [flag short name]
    '''
    trace = vdb.getTrace()
    argv = shlex.split(line)
    if len(argv) not in (0, 1):
        return vdb.do_help('eflags')

    if len(argv) > 0:
        flag = argv[0].upper()
        valid_flags = trace.getStatusFlags()
        if flag not in valid_flags:
            raise Exception('invalid flag: %s, valid flags %s' % (flag, valid_flags))
        value = trace.getRegisterByName(flag)
        trace.setRegisterByName(flag, not bool(value))
        # TODO: this is not plumbed through to flags gui due to new gui
        # eventing coming soon.
        vdb.vdbUIEvent('vdb:setflags')
        return

    ef = trace.getRegisterByName('eflags')
    vdb.vprint('%16s: %s' % ('Carry', bool(ef & e_i386.EFLAGS_CF)))
    vdb.vprint('%16s: %s' % ('Parity', bool(ef & e_i386.EFLAGS_PF)))
    vdb.vprint('%16s: %s' % ('Adjust', bool(ef & e_i386.EFLAGS_AF)))
    vdb.vprint('%16s: %s' % ('Zero', bool(ef & e_i386.EFLAGS_ZF)))
    vdb.vprint('%16s: %s' % ('Sign', bool(ef & e_i386.EFLAGS_SF)))
    vdb.vprint('%16s: %s' % ('Trap', bool(ef & e_i386.EFLAGS_TF)))
    vdb.vprint('%16s: %s' % ('Interrupt', bool(ef & e_i386.EFLAGS_IF)))
    vdb.vprint('%16s: %s' % ('Direction', bool(ef & e_i386.EFLAGS_DF)))
    vdb.vprint('%16s: %s' % ('Overflow', bool(ef & e_i386.EFLAGS_OF)))


def vdbExtension(vdb, trace):
    vdb.addCmdAlias('db', 'mem -F bytes')
    vdb.addCmdAlias('dw', 'mem -F u_int_16')
    vdb.addCmdAlias('dd', 'mem -F u_int_32')
    vdb.addCmdAlias('dq', 'mem -F u_int_64')
    vdb.addCmdAlias('dr', 'mem -F "Deref View"')
    vdb.addCmdAlias('ds', 'mem -F "Symbols View"')
    vdb.registerCmdExtension(eflags)
