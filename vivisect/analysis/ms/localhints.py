import logging

logger = logging.getLogger(__name__)


def analyze(vw):

    for fname in vw.getFiles():

        h = vw.getFileMeta(fname, 'PELocalHints', None)
        if h is None:
            continue

        for fva, hints in h.items():
            if not vw.isFunction(fva):
                vw.makeFunction(fva)

            for name, offset, size, flags in hints:

                if offset > 0:
                    # Take 2 away for offset from frame....
                    offset = offset - (vw.psize * 2)
                    idx = offset / vw.psize

                    if idx > 100:
                        continue

                    logger.warning('FIXME: %d %s', offset, name)

                    #atype, aname = vw.getFunctionArg(fva, idx)
                    #if atype is None:
                        #atype = viv_magic.Unknown
                    #print 'ARG',idx, name
                    #vw.setFunctionArg(fva, idx, atype, name)

                elif offset < 0:
                    # "offset" is from frame, *we* are from initial esp...
                    offset -= vw.psize
                    vw.setFunctionLocal(fva, offset, None, name)
