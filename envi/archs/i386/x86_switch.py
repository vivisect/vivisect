
def simpleIndirHook(arch, op, vw):
    '''
    we just want to track the indirect jmp/call

    if we do too much here, we won't know when to stop.  there doesn't seem to be any way to get xrefs
    here before we enter into codeblock analysis.  function analysis is where this wants to be.  
    this hook is paired with an analysis module that should be inserted into all Intel architectures 
    directly after CodeBlock analysis.
    '''

    # FIXME: do we want to filter anything out?  
    #  jmp edx
    #  jmp dword [ebx + 68]
    #  call eax
    #  call dword [ebx + eax * 4 - 228]

    # if we have any xrefs from here, we have already been analyzed.  nevermind.
    if len(vw.getXrefsFrom(op.va)):
        return

    if vw.verbose: print "indirect hook at 0x%x    %s" % (op.va, op)
    key = op.mnem + "_indir"
    switches = vw.getMeta(key, None)

    if switches == None:
        switches = []

    if op.va not in switches:
        switches.append(op.va)
        vw.setMeta(key, switches)



