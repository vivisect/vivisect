#!/usr/bin/env python
import sys
import argparse
import traceback
import logging

import envi.common as e_common

import vdb
import vtrace
import vtrace.snapshot as vt_snap


logger = logging.getLogger('vdb')


def targetusage():
    print('''
    Alternate vdb "targets" include various embedded/hardware/etc debugging
    capabilities which are not related to your runtime platform....  Some
    targets may require additional foo=bar style options added to the end
    of your vdb command.  See details per-target below.

    ======================================================================

    "vmware32" host=<host> port=<port>
        ( of listening vmware gdb server for 32 bit VM )

        The "vmware32" target enables debugging with a 32bit VMWare Hypervisor
        using their gdb-server stub.  This allows "hardware debugger" like
        kernel debugging.

        Add the following lines to your VMX file to enable debugging:

        debugStub.listen.guest32 = "TRUE"
        debugStub.hideBreakpoints = "FALSE"

        VMWare will be listening on 127.0.0.1 on port 8832 (for the first one...
        8833 for the second... etc... )

        NOTE: Only Windows XP currently supported.
        TODO: Windows 7 / Linux / Windows 8

    ======================================================================

    In development:

    "vmware64"  - Kernel debug 64 bit VMWare Hypervisors
    "openocd"   - Debug embedded targets

    ''')
    sys.exit(0)

loglevels = (logging.CRITICAL,
             logging.ERROR,
             logging.WARN,
             logging.INFO,
             logging.DEBUG)


def main():
    parser = argparse.ArgumentParser(prog='vdbbin', usage='%(prog)s [options] [platformopt=foo, ...]')
    parser.add_argument('-c', '--cmd', dest='command', default=None, help='Debug a fired command')
    parser.add_argument('-p', '--process', dest='process', default=None, help='Attach to process by name or pid')
    parser.add_argument('-Q', '--qt', dest='doqt', default=False, action='store_true', help='Run the QT gui')
    parser.add_argument('-R', '--remote', dest='remotehost', default=None, help='Attach to remote VDB server')
    parser.add_argument('-r', '--run', dest='dorunagain', default=False, action='store_true', help='Do not stop on attach')
    parser.add_argument('-s', '--snapshot', dest='snapshot', default=None, help='Load a vtrace snapshot file')
    parser.add_argument('-S', '--server', dest='doserver', default=False, action='store_true')
    parser.add_argument('-v', '--verbose', dest='verbose', default=False, action='count')
    parser.add_argument('-t', '--target', dest='target', default=None, help='Activate special vdb target ( -t ? for list )')
    parser.add_argument('--android', dest='doandroid', default=False, action='store_true', help='Debug Android with ADB!')
    parser.add_argument('-e', '--eventid', dest='eventid', default=None, type=int, help='Used for Windows JIT')
    parser.add_argument('-w', '--waitfor', dest='waitfor', default=None, help='Wait for process with name')
    parser.add_argument('platargs', nargs='*')

    args = parser.parse_args()

    # setup logging
    verbose = min(args.verbose, 5)
    level = e_common.LOG_LEVELS[verbose]
    e_common.initLogging(logger, level=level)

    # Handle some options before we even create a trace.
    vtrace.remote = args.remotehost  # None by default

    platargs = {}

    for arg in args.platargs:

        if arg.find('=') == -1:
            continue

        k, v = arg.split('=', 1)
        if v.isdigit():
            v = int(v)

        platargs[k.lower()] = v

    if args.doandroid:
        import vdb.tools.android as v_utils_android
        v_utils_android.runVdbOnDroid()
        return

    if args.target == '?':
        targetusage()

    trace = None
    if args.snapshot:
        logger.info('Loading process snapshot...')
        trace = vt_snap.loadSnapshot(args.snapshot)

    if trace is None:
        trace = vtrace.getTrace(target=args.target, **platargs)

    db = vdb.Vdb(trace)
    db.runagain = args.dorunagain
    db.windows_jit_event = args.eventid

    if args.waitfor:
        while True:
            newest_pid = 0
            for pid, pname in trace.ps():
                pname = pname.split(' ')[0]
                if pname.find(args.waitfor) != -1:
                    newest_pid = pid

            if newest_pid != 0:
                trace.attach(newest_pid)
                break

    if args.doqt:
        import vqt.main as vq_main
        import vdb.qt.main as vdb_q_main
        import vqt.colors as vq_colors
        vq_main.startup(css=vq_colors.qt_matrix)
        qgui = vdb_q_main.VdbWindow(db)
        qgui.show()

    if args.doserver:
        db.do_server('')

    if args.process:
        db.do_attach(args.process)

    elif args.command:
        trace.execute(args.command)

    if args.eventid:
        db.trace.setMeta('WindowsJitEvent', args.eventid)

    if args.doqt:
        vq_main.main()

    else:

        while not db.shutdown.isSet():
            try:
                db.cmdloop()
            except KeyboardInterrupt:
                if db.trace.isRunning():
                    db.trace.sendBreak()
            except SystemExit:
                break
            except:
                logger.error(traceback.format_exc())


if __name__ == '__main__':
    main()
