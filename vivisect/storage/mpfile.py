import base64
import logging

import msgpack

logger = logging.getLogger(__name__)

loadargs = {'use_list': False, 'raw': False, 'max_buffer_size': 2**32 -1}
if msgpack.version < (1, 0, 0):
    loadargs['encoding'] = 'utf-8'
else:
    loadargs['strict_map_key'] = False

VSIG = b'MSGVIV'.ljust(8, b'\x00')


def vivEventsAppendFile(filename, events):
    with open(filename, 'ab') as f:
        for event in events:
            if event[0] == 20:
                mape = base64.b64encode(event[1][3])
                event = (event[0], (event[1][0], event[1][1], event[1][2], mape))
            msgpack.pack(event, f, use_bin_type=False)


def saveWorkspaceChanges(vw, filename):
    events = vw.exportWorkspaceChanges()
    vivEventsAppendFile(filename, events)


def vivEventsToFile(filename, events):
    with open(filename, 'wb') as f:
        msgpack.pack(VSIG, f, use_bin_type=False)
        for event in events:
            if event[0] == 20:
                mape = base64.b64encode(event[1][3])
                event = (event[0], (event[1][0], event[1][1], event[1][2], mape))
            msgpack.pack(event, f, use_bin_type=False)


def saveWorkspace(vw, filename):
    events = vw.exportWorkspace()
    vivEventsToFile(filename, events)


def vivEventsFromFile(filename):
    events = []
    with open(filename, 'rb') as f:
        unpacker = msgpack.Unpacker(f, **loadargs)
        siggy = next(unpacker)
        if siggy.encode('utf-8') != VSIG:
            logger.warning('Invalid file signature of %s', str(siggy))
            return
        for event in unpacker:
            if event[0] == 20:
                mape = base64.b64decode(event[1][3])
                event = (event[0], (event[1][0], event[1][1], event[1][2], mape))
            events.append(event)
    return events


def loadWorkspace(vw, filename):
    events = vivEventsFromFile(filename)
    vw.importWorkspace(events)
