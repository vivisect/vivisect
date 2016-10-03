import traceback
import pickle as pickle

import vivisect

vivsig_cpickle = ('VIV'.ljust(8, '\x00')).encode()


def saveWorkspaceChanges(vw, filename):
    elist = vw.exportWorkspaceChanges()
    if len(elist):
        f = open(filename, 'ab')
        pickle.dump(elist, f, protocol=2)
        f.close()


def saveWorkspace(vw, filename):
    events = vw.exportWorkspace()
    vivEventsToFile(filename, events)


def vivEventsAppendFile(filename, events):
    f = open(filename, 'ab')
    # Mime type for the basic workspace
    pickle.dump(events, f, protocol=2)
    f.close()


def vivEventsToFile(filename, events):
    try:
        with open(filename, 'wb') as f:
            # Mime type for the basic workspace
            f.write(vivsig_cpickle)
            pickle.dump(events, f, protocol=2)
    except Exception as e:
        traceback.print_exc()


def vivEventsFromFile(filename):
    with open(filename, "rb") as f:
        vivsig = f.read(8)

        # check for various viv serial formats
        if vivsig != vivsig_cpickle:
            # FIXME legacy file format.... ( eventually remove )
            f.seek(0)

        events = []
        # Incremental changes are saved to the file by appending more pickled
        # lists of exported events
        while True:
            try:
                events.extend(pickle.load(f))
            except EOFError as e:
                break
            except pickle.UnpicklingError as e:
                raise vivisect.InvalidWorkspace(filename, "invalid workspace file")

    # FIXME - diagnostics to hunt msgpack unsave values
    # for event in events:
    # import msgpack
    # try:
    # msgpack.dumps(event)
    # except Exception, e:
    # print('Unsafe Event: %d %r' % event)

    return events


def loadWorkspace(vw, filename):
    events = vivEventsFromFile(filename)
    vw.importWorkspace(events)
    return
