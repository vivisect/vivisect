
"""
A package of builtin vivisect reports which produce runtime
generated lists of workspace statistics and anomalies.

Each report module must have 2 things. It must have a variable
declared named "columns" which is a list of (colname, coltype)
tuples, and a "report" function which returns a VA Set style
dictionary.
"""

rep_mods = [
    ('Undefined Xrefs/Names', 'vivisect.reports.undeftargets'),
    ('Overlapped Locations', 'vivisect.reports.overlaplocs'),
    ('Function Complexity', 'vivisect.reports.funccomplexity'),
    ('Location Distribution', 'vivisect.reports.locationdist'),
]


def listReportModules():
    '''
    Return a list of (<printname>, <modpath>) tuples for the known
    report types.
    '''
    return list(rep_mods)


def runReportModule(vw, modname):
    mod = vw.loadModule(modname)
    return (mod.columns, mod.report(vw))
