
import os
import zipfile

pkgnames = ('Elf', 'PE', 'cobra', 'envi', 'vdb', 'visgraph', 'vqt', 'vstruct', 'vtrace')


def addPythonSources( zfile, dirname, filenames ):
    if dirname.find('.svn') != -1:
        return

    for fname in filenames:
        if not fname.endswith('.py'):
            continue

        filepath = os.path.join(dirname, fname)
        zfile.write(filepath, filepath)


def getSourceZip(fname='vdb.pyz'):
    z = zipfile.ZipFile(fname, 'w')
    for pypkg in pkgnames:
        os.path.walk(pypkg, addPythonSources, z)

    z.write('vdbbin', '__main__.py')
    z.close()
    return fname
