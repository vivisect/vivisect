#!/usr/bin/env python
import os
import sys
import time
import logging
import argparse
import cProfile
import importlib.util

import envi.common as e_common
import envi.config as e_config
import envi.threads as e_threads

import vivisect.cli as viv_cli
import vivisect.parsers as viv_parsers


logger = logging.getLogger('vivisect')


def main():
    parser = argparse.ArgumentParser(prog='vivbin', usage='%(prog)s [options] <workspace|binaries...>')
    parser.add_argument('-M', '--module', dest='modname', default=None, action='store',
                        help='run the file listed as an analysis module in non-gui mode and exit')
    parser.add_argument('-A', '--skip-analysis', dest='doanalyze', default=True, action='store_false',
                        help='Do *not* do an initial auto-analysis pass')
    parser.add_argument('-B', '--bulk', dest='bulk', default=False, action='store_true',
                        help='Do *not* start the gui, just load, analyze and save')
    parser.add_argument('-C', '--cprofile', dest='cprof', default=False, action='store_true',
                        help='Output vivisect performace profiling (cProfile) info')
    parser.add_argument('-E', '--entrypoint', dest='entrypoints', default=[], action='append',
                        help='Add Entry Point for bulk analysis (can have multiple "-E <addr>" args')
    parser.add_argument('-O', '--option', dest='option', default=None, action='append',
                        help='<secname>.<optname>=<optval> (optval must be json syntax)')
    parser.add_argument('-p', '--parser', dest='parsemod', default=None, action='store',
                        help='Manually specify the parser module (pe/elf/blob/...)')
    parser.add_argument('-s', '--storage', dest='storage_name', default=None, action='store',
                        help='Specify a storage module by name')
    parser.add_argument('-v', '--verbose', dest='verbose', default=False, action='count',
                        help='Enable verbose mode (multiples matter: -vvvv)')
    parser.add_argument('-V', '--version', dest='version', default=None, action='store',
                        help='Add file version (if available) to save file name')
    parser.add_argument('-c', '--config', dest='config', default=None,
                        help='Path to a directory to use for config data')
    parser.add_argument('-a', '--autosave', dest='autosave', default=False, action='store_true',
                        help='Autosave configuration data')
    parser.add_argument('file', nargs='*')
    args = parser.parse_args()

    vw = viv_cli.VivCli(confdir=args.config, autosave=args.autosave)

    # setup logging
    vw.verbose = min(args.verbose, len(e_common.LOG_LEVELS)-1)
    level = e_common.LOG_LEVELS[vw.verbose]
    e_common.initLogging(logger, level=level)


    # do things
    if args.option is not None:
        for option in args.option:
            if option in ('-h', '?'):
                logger.critical(vw.config.reprConfigPaths())
                sys.exit(-1)

            try:
                vw.config.parseConfigOption(option)
            except e_config.ConfigNoAssignment as e:
                logger.critical(vw.config.reprConfigPaths() + "\n")
                logger.critical(e)
                logger.critical("syntax: \t-O <secname>.<optname>=<optval> (optval must be json syntax)")
                sys.exit(-1)

            except Exception as e:
                logger.critical(vw.config.reprConfigPaths())
                logger.critical("With entry: %s", option)
                logger.critical(e)
                sys.exit(-1)

    if args.storage_name is not None:
        vw.setMeta("StorageModule", args.storage_name)

    # If we're not gonna load files, no analyze
    if args.file is None:
        args.doanalyze = False

    # Load in any additional files...
    needanalyze = False
    if args.file is not None:
        for fname in args.file:
            if args.parsemod is None:
                args.parsemod = viv_parsers.guessFormatFilename(fname)

            start = time.time()
            if args.parsemod == 'viv':
                vw.loadWorkspace(fname)
            else:
                needanalyze = True
                vw.loadFromFile(fname, fmtname=args.parsemod)

            end = time.time()
            logger.info('Loaded (%.4f sec) %s', (end - start), fname)

    if args.bulk:
        for entryva in args.entrypoints:
            try:
                vw.vprint("Adding Entry Point: %s: " % entryva)
                eva = int(entryva, 0)
                vw.setVaSetRow('EntryPoints', (eva,))
            except Exception as e:
                vw.vprint("Failure: %r" % e)

        if args.doanalyze:
            if args.cprof:
                cProfile.run("vw.analyze()")
            else:
                start = time.time()
                vw.analyze()
                end = time.time()
                logger.debug("ANALYSIS TIME: %s", (end-start))

        if args.modname is not None:
            modpath = os.path.abspath(args.modname)
            spec = importlib.util.spec_from_file_location('custom_analysis', modpath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            module.analyze(vw)

        logger.info('stats: %r', vw.getStats())
        logger.info("Saving workspace: %s", vw.getMeta('StorageName'))
        vw.saveWorkspace()

    else:

        import vivisect.qt.main as viv_qt_main

        # If we are interactive, lets turn on extended output...
        if args.doanalyze and needanalyze:
            e_threads.firethread(vw.analyze)()

        viv_qt_main.main(vw)


if __name__ == '__main__':
    main()
