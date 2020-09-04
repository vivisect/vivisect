import logging

import msgpack

logger = logging.getLogger(__name__)

loadargs = {'use_list': False}
if msgpack.version < (1, 0, 0):
    loadargs['encoding'] = 'utf-8'
else:
    loadargs['strict_map_key'] = False

VSIG = b'MSGVIV'.ljust(8, b'\x00')


def vivEventsAppendFile(filename, events):
    with open(filename, 'ab') as f:
        for event in events:
            msgpack.pack(event, f, use_bin_type=True)


def saveWorkspaceChanges(vw, filename):
    events = vw.exportWorkspaceChanges()
    vivEventsAppendFile(filename, events)


def vivEventsToFile(filename, events):
    with open(filename, 'wb') as f:
        msgpack.pack(VSIG, f, use_bin_type=True)
        for event in events:
            msgpack.pack(event, f, use_bin_type=True)


def saveWorkspace(vw, filename):
    events = vw.exportWorkspace()
    vivEventsToFile(filename, events)


def vivEventsFromFile(filename):
    events = []
    with open(filename, 'rb') as f:
        unpacker = msgpack.Unpacker(f, **loadargs)
        siggy = next(unpacker)
        if siggy != VSIG:
            logger.warning('Invalid file signature of %s', str(siggy))
            return
        for upck in unpacker:
            events.append(upck)
    return events


def loadWorkspace(vw, filename):
    events = vivEventsFromFile(filename)
    vw.importWorkspace(events)
