import sys
import argparse
import traceback

import vstruct.defs.java as v_d_java


def setup():
    ap = argparse.ArgumentParser(description='Java Class File Printer')
    ap.add_argument('file', nargs='+', help='A bunch of java class files to parse')
    return ap


def main(argv):
    opts = setup().parse_args(argv)

    for filename in opts.file:
        with open(filename, 'rb') as f:
            javacls = v_d_java.JavaClass()
            try:
                javacls.vsParse(f.read())
                print(javacls.tree())

                cname = javacls.getClassName()
                sname = javacls.getSuperClassName()
                print('Java Class: %s (inherits: %s)' % (cname, sname))

                for fname, descname, attrs in javacls.getClassFields():
                    print('Field: %s (%s) (attrs: %r)' % (fname, descname, attrs.keys()))

                for methname, attrs in javacls.getClassMethods():
                    print('Method: %s (attrs: %r)' % (methname, attrs.keys()))

                print('Constants:')
                for fname, const in javacls.const_pool:
                    print(const.tag, const.data.tree())

                print(javacls.getClassAttributes().keys())

            except Exception:
                print(javacls.tree())
                traceback.print_exc()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
