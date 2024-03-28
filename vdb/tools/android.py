'''
Some utilities for debugging on android.
'''
import os
import subprocess

import vdb.release as vdb_release


utildir = os.path.dirname(__file__)
droidtmp = '/data/local/tmp/'


def adbCommand(*argv):
    return subprocess.check_output(argv, stderr=subprocess.PIPE)


message = '''
Due to silly/complicated reasons, you have to issue the
vdb command from within adb yourself (ask visi to rage about
it if youd like to know why...)

Please run this:
cd %s; sh androidpy.sh vdb.pyz
''' % droidtmp


def runVdbOnDroid():
    zfile = os.path.join(utildir, 'vdb.pyz')
    script = os.path.join(utildir, 'androidpy.sh')
    vdb_release.getSourceZip(fname=zfile)

    # copy in the script and the source zip
    print('Pushing vdb.pyz...')
    adbCommand('adb', 'push', zfile, droidtmp + 'vdb.pyz')
    print('Pushing python shell script...')
    adbCommand('adb', 'push', script, droidtmp + 'androidpy.sh')
    print(message)
    # os.system('adb shell sh %s/androidpy.sh %s/vdb.pyz' % ( droidtmp, droidtmp ))
    os.system('adb shell')


if __name__ == '__main__':
    runVdbOnDroid()
