import platform
# This module needs to be "relocatable"

def getHostId():
    osname = platform.system().lower()
    if osname == 'darwin':
        from . import darwinhostid
        return darwinhostid.getHostId()

    elif osname in ['microsoft','windows']:
        from . import windowshostid
        return windowshostid.getHostId()

    return None

