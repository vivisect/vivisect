import platform
# This module needs to be "relocatable"

def getHostId():
    osname = platform.system().lower()
    if osname == 'darwin':
        import darwinhostid
        return darwinhostid.getHostId()

    elif osname in ['microsoft','windows']:
        import windowshostid
        return windowshostid.getHostId()

    return None

