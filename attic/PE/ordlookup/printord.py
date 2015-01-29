import sys

'''
Quick utility to generate ord lookups from DLL exports.
'''

import PE

p = PE.PE(file(sys.argv[1], 'rb'))

base = long(p.IMAGE_EXPORT_DIRECTORY.Base)

ords = {}
for fva, ord, name in p.getExports():
    ords[ord+base] = name

keys = ords.keys()
keys.sort()
for k in keys:
    print '''    %d:'%s',''' % (k,ords.get(k))

