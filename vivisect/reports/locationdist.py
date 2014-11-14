
columns = (
    ("Location Type",str),
    ("Instance Count", int),
    ("Size (bytes)", int),
    ("Size Percent", int),
)

def report(vw):
    return vw.getLocationDistribution()
