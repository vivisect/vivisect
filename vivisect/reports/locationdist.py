columns = (
    ("Location Type", str),
    ("Instance Count", int),
    ("Size (bytes)", int),
    ("Size (percent)", int),
)


def report(vw):
    return vw.getLocationDistribution()
