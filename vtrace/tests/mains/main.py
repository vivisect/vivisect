import sys
import errno


def waitForTest():
    sys.stdout.write('testwait\n')
    sys.stdout.flush()
    while True:
        line = safeReadline().strip()
        if line == 'testmod':
            break


def safeReadline():
    while True:
        try:  # Crazy loop for freebsd readline failure
            r = sys.stdin.readline()
            break
        except IOError as e:
            if e.errno == errno.EINTR:
                continue
            raise
    return r


def exitTest():
    sys.exit(33)


def main():
    waitForTest()
    return 33


if __name__ == '__main__':
    sys.exit(main())
