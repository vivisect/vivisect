
def einfo(db, line):
    db.vprint('EINFO')

def vdbExtension(vdb, trace):
    vdb.registerCmdExtension(einfo)
    
