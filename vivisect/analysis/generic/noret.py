'''
A function analysis module that determines if any of the leaf nodes in a function
have a clean return

Depends on the codeblock and thunk passes being finished, so typically this will be the last
pass to run.

Generally, idea is to search through the terminal nodes of a function, and if they end in a
noreturn call, or just straight up don't have a return
* And if all the terminal nodes end in that, then there's no way the function returns, and we should
bail
'''
import logging

import envi
import vivisect.const as v_const
import vivisect.tools.graphutil as v_t_graph


logger = logging.getLogger(__name__)


def analyzeFunction(vw, fva):
    if vw.isFunctionThunk(fva):
        # Don't bother with import thunks
        for ref in vw.getXrefsFrom(fva, rtype=v_const.REF_CODE):
            loc = vw.getLocation(ref[v_const.XR_TO])
            if loc and loc[v_const.L_LTYPE] == v_const.LOC_IMPORT:
                return

    g = v_t_graph.buildFunctionGraph(vw, fva)
    _, _, leaves = v_t_graph.getNodeWeightHisto(g)

    hasret = False
    for weight, nodes in leaves.items():
        for node in nodes:
            cbstart, cbsize, cbfunc = vw.getCodeBlock(node[0])
            cbend = cbstart + cbsize - 1

            lva, lsize, ltype, linfo = vw.getLocation(cbend)
            if ltype != v_const.LOC_OP:
                pass
            if vw.isNoReturnVa(lva):
                continue
            if linfo & envi.IF_RET:
                hasret = True
                break
            # be wary of dynamic branches we couldn't resolve
            if linfo & envi.IF_BRANCH:
                hasret = True
                break

    # 0x14006ba90 out of omnetpp.exe at O2, 64bit is a good counter example (that shouldn't be no ret)
    if not hasret:
        logger.info('Marking 0x%.8x as no return' % fva)
        vw.addNoReturnVa(fva)
