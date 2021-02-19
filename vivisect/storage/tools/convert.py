import argparse

import vivisect.storage as v_storage

def setup():
    ap = argparse.ArgumentParser('')

    ap.add_argument('')
    ap.add_argument('')
    ap.add_argument('')

    return ap


def main(argv):
    opts = setup().parse_args(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
