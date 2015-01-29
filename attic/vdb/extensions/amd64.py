import vdb.extensions.i386 as v_ext_i386

import vdb.extensions.i386 as vdb_ext_i386

def vdbExtension(vdb, trace):
    vdb.addCmdAlias('db','mem -F bytes')
    vdb.addCmdAlias('dw','mem -F u_int_16')
    vdb.addCmdAlias('dd','mem -F u_int_32')
    vdb.addCmdAlias('dq','mem -F u_int_64')
    vdb.addCmdAlias('dr','mem -F "Deref View"')
    vdb.addCmdAlias('ds','mem -F "Symbols View"')

    vdb.registerCmdExtension(vdb_ext_i386.eflags,'amd64')
