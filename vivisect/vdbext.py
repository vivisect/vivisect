
'''
The vdb command / GUI extensions from vivisect!
'''
import logging
import traceback

import vdb
import vtrace
import vdb.qt.main as vdb_qt_main

import envi.cli as e_cli
import vivisect.colormap as viv_color

from envi.threads import firethread
from vqt.main import idlethread, idlethreadsync


logger = logging.getLogger(__name__)


class VivNotif(vtrace.Notifier):

    def __init__(self, vivgui):
        self.vivgui = vivgui

    @idlethreadsync
    def notify(self, event, trace):
        try:

            if event == vtrace.NOTIFY_BREAK and not trace.shouldRunAgain():

                pc = trace.getProgramCounter()
                if self.vivgui.vw.isValidPointer(pc):
                    self.vivgui.vivNavSignal.emit('0x%.8x' % pc)

                # If there are stalker hits, lets make a color map for them...
                shits = trace.getMeta('StalkerHits', None)
                if shits is not None:
                    self.vivgui.vw.vprint('vdb ext found stalker hits!')
                    cmap = viv_color.VivColorMap(self.vivgui.vw)
                    for hit in shits:
                        try:
                            cmap.colorBlock(hit, 'yellow')
                        except Exception as e:
                            self.vivgui.vw.vprint('WARNING: stalker color map: %s' % e)

                    #self.vivgui.setColorMap(cmap.getColorDict())
                    #cmap.saveAs('stalker')
                    cmap.setGuiMap()

        except Exception as e:
            logger.error(traceback.format_exc())


@firethread
def doLoad(db, trace, base):
    db.vw.vprint('Loading from memory 0x%.8x...' % base)
    db.vw.loadFromMemory(trace, base)
    db.vw.vprint('...loaded.')
    db.vw.analyze()


def vivimport(db, line):
    '''
    Import either a library or memory map from the target
    process into the current vivisect workspace.
    '''
    vw = db.vw
    trace = db.getTrace()

    argv = e_cli.splitargs(line)
    if len(argv) != 1:
        return db.do_help("vivimport")

    try:
        base = db.parseExpression(line)
    except Exception:
        db.vprint("Invalid Address Expression: %s" % argv[0])
        return

    # Init Arch/Format if they are not...
    vw.initMeta('Architecture', trace.getMeta('Architecture'))
    vw.initMeta('Format', trace.getMeta('Format'))

    doLoad(db, trace, base)


def extendVdb(db, vivgui):
    db.vw = vivgui.vw  # Store a ref to the workspace...
    db.vivgui = vivgui  # Also a reference to the GUI
    db.registerNotifier(vtrace.NOTIFY_ALL, VivNotif(vivgui))
    db.registerCmdExtension(vivimport)


@firethread
def fireattach(trace, pid):
    trace.attach(pid)


@idlethread
def runVdb(vivgui, pid=None):
    try:
        db = vdb.Vdb()
        extendVdb(db, vivgui)
        vgui = vdb_qt_main.VdbWindow(db)
        vgui.show()
        if pid is not None:
            fireattach(db.trace, pid)
    except Exception as e:
        vivgui.vw.vprint('Error Running VDB: %s' % e)
