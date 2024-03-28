import pickle
import vivisect

vivsig_cpickle = b'VIV'.ljust(8, b'\x00')


def writeFileHeader(f):
    f.write(vivsig_cpickle)

def saveWorkspaceChanges(vw, filename):
    elist = vw.exportWorkspaceChanges()
    if len(elist):
        vivEventsAppendFile(filename, elist)

def saveWorkspace(vw, filename):
    events = vw.exportWorkspace()
    vivEventsToFile(filename, events)


def vivEventsAppendFile(filename, events):
    with open(filename, 'ab') as f:
        # if the file is empty, add the header
        if f.tell() == 0:
            writeFileHeader(f)

        pickle.dump(events, f, protocol=2)


def vivEventsToFile(filename, events):
    with open(filename, 'wb') as f:
        # Mime type for the basic workspace
        writeFileHeader(f)
        pickle.dump(events, f, protocol=2)


def vivEventsFromFile(filename):
    with open(filename, 'rb') as f:
        vivsig = f.read(8)

        # check for various viv serial formats
        if vivsig == vivsig_cpickle:
            pass

        else:  # FIXME legacy file format.... ( eventually remove )
            f.seek(0)

        events = []
        # Incremental changes are saved to the file by appending more pickled
        # lists of exported events
        while True:
            try:
                events.extend(pickle.load(f))
            except EOFError:
                break
            except pickle.UnpicklingError:
                raise vivisect.InvalidWorkspace(filename, "invalid workspace file")

    return events


def loadWorkspace(vw, filename):
    events = vivEventsFromFile(filename)
    vw.importWorkspace(events)
    return
