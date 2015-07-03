import sys
def mainwait():
    if 'testwait' in sys.argv:
        sys.stdout.write('testwait\n')
        sys.stdout.close()
        sys.stdin.readline()

