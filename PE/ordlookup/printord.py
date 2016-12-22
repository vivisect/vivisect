import sys

'''
Quick utility to generate ord lookups from DLL exports.
'''

import PE

p = PE.PE(open(sys.argv[1], 'rb'))

base = int(p.IMAGE_EXPORT_DIRECTORY.Base)

ords = {}
for fva, ord, name in p.getExports():
    ords[ord+base] = name

keys = list(ords.keys())
keys.sort()
for k in keys:
    print('''    %d:'%s',''' % (k,ords.get(k)))

