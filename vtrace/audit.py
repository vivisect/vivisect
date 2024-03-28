"""
Test for platform functionality (for internal use).
"""
# Copyright (C) 2007 Invisigoth - See LICENSE file for details
import vtrace
import vtrace.platforms.base as v_base

############################################
#
# FIXME this is dorked for now based on the new platforms/archs design
#
############################################


def auditTracer(trace):
    """
    Print out a list of platform requirements and whether
    a particular tracer meets them.  This is mostly a
    development tool to determine what's left to do on a
    tracer implementation.
    """
    for mname in dir(v_base.BasePlatformMixin):
        if "__" in mname:
            continue
        if getattr(trace.__class__, mname) == getattr(v_base.BasePlatformMixin, mname):
            print("LACKS: %s" % mname)
        else:
            print("HAS: %s" % mname)


if __name__ == "__main__":
    trace = vtrace.getTrace()
    auditTracer(trace)
