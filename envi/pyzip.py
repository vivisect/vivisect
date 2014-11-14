import os
import sys
import zipfile

'''
A utility package (in a central location) for packaging up
zip files full of source or whatever...
'''

def callback(z, dname, files):
    if dname.find('.svn') != -1:
        return

    for fname in files:
        if fname.endswith('.py'):
            fpath = os.path.join(dname, fname)
            z.write(fpath)

def addSource(z, dname):
    os.path.walk(dname, callback, z)

def main():

    zipname = sys.argv[1]
    pz = zipfile.PyZipFile(zipname, 'w')

    dirnames = sys.argv[2:]
    if not len(dirnames):
        dirnames = [ dname for dname in os.listdir('.') if os.path.isdir(dname) and dname != '.svn' ]

    for dirname in dirnames:
        addSource(pz, dirname)
        pz.writepy(dirname)

    pz.close()

if __name__ == '__main__':
    sys.exit(main())

