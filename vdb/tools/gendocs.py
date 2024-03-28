'''
Generates HTML documentation for Vdb and related APIs using epydoc.

Command line options (all are optional):

    --dotpath=PATH          To generate class heirarchy graphs as part of
                            documentation, specify the path to the GraphViz
                            dot executable

    -o PATH, --output=PATH  The output directory.  If PATH does not exist,
                            then it will be created.  If it exists and is
                            non-empty, then the current directory will be
                            renamed and a new one created.

    NAMES...                If you have additional files / modules to be
                            included in the documentation, specify them on the
                            command line after other options.

Usage Examples: (from command prompt in directory containing vdb directory)
  python -m vdb.tools.gendocs
  python -m vdb.tools.gendocs --dotpath "D:\\downloads\\Graphviz 2.28\\bin\\dot.exe" ..\\vdb-extensions-git\\*.py
  python -m vdb.tools.gendocs --dotpath "D:\\downloads\\Graphviz 2.28\\bin\\dot.exe" --output mydocs ..\\vdb-extensions-git\\*.py
'''
import os
import sys
import datetime

import epydoc
import epydoc.cli


def vdbEpydoc():
    '''
    Generates HTML documentation for Vdb and related APIs using epydoc.
    '''

    if len(sys.argv) > 1 and (sys.argv[1] == '-h' or sys.argv[1] == '--help'):
        print(__doc__)
        return

    toolsdirname = os.path.dirname(os.path.abspath(__file__))

    outputdir = os.path.join(toolsdirname, os.path.join('..', os.path.join('..', 'apidocs')))
    configfile = os.path.join(toolsdirname, 'vdb.epydoc')
    cssfile = os.path.join(toolsdirname, 'vdb.epydoc.css')

    newargv = ['epydoc', '--config', configfile, '--output', outputdir, '--css', cssfile]

    if sys.argv > 1:
        newargv += sys.argv[1:]

    # Create set the fake command line arguments so they will be parsed
    sys.argv = newargv

    options, names = epydoc.cli.parse_arguments()

    # rename the output directory if it exists to give clean output
    print(options.target)
    if os.path.exists(options.target):
        # path exists, verify it is a directory
        if not os.path.isdir(options.target):
            print('%s exists but is not a directory, exiting', options.target)
            return

        # if dir is not empty, rename it.
        if len(os.listdir(options.target)) > 0:
            now = datetime.datetime.now()
            targetdirname = os.path.join(options.target, '-pre-' + now.strftime('%Y-%m-%d_%H%M%S'))

            print('output dir: %s exists and is not empty. moving old dir to name %s' % (options.target, targetdirname))
            os.rename(options.target, targetdirname)

    epydoc.cli.main(options, names)


if __name__ == '__main__':
    vdbEpydoc()
