from PyQt4 import QtCore, QtGui

QMOD_META   = 0x08000000
QMOD_CTRL   = 0x04000000
QMOD_SHIFT  = 0x02000000

special_keys = {
    0x1000000:'esc',
    0x1000003:'bs',
    0x1000004:'enter',
    0x1000012:'left',
    0x1000013:'up',
    0x1000014:'right',
    0x1000015:'down',
}

fkey_base = 0x100002f
for i in xrange(1,12):
    special_keys[ fkey_base + i ] = 'f%d' % i

def hotkey(targname):
    def hotkeydecor(f):
        f._vq_hotkey = targname
        return f
    return hotkeydecor

class HotKeyMixin(object):

    def __init__(self):
        self._vq_hotkeys = {}
        self._vq_hotkey_targets = {}

        for name in dir(self):
            obj = getattr(self, name, None)
            hktarg = getattr(obj, '_vq_hotkey', None)
            if hktarg:
                self.addHotKeyTarget(hktarg, obj)

    def addHotKeyTarget(self, hkname, callback, *args, **kwargs):
        '''
        Add a new hotkey "target".  This allows applications to specify what
        capabilities they'd like to expose for hotkey binding.

        w.addHotKeyTarget('go', trace.run)
        '''
        self._vq_hotkey_targets[hkname] = (callback,args,kwargs)

    def getHotKeyTargets(self):
        '''
        Retrieve a list of the known hotkey targets for this widget.

        Example:

            for tname in w.getHotKeyTargets():
                print('Found Hotkey Target: %s' % tname)

        '''
        return self._vq_hotkey_targets.keys()

    def isHotKeyTarget(self, targname):
        '''
        Check if the given hotkey target name is valid.
        '''
        return self._vq_hotkey_targets.get(targname) != None

    def getHotKeys(self):
        '''
        Retrieve a list of (hotkey,target) tuples.
        '''
        return self._vq_hotkeys.items()

    def addHotKey(self, keystr, hktarg):
        '''
        Bind a given key sequence (by string) to the given hotkey
        target.
        '''
        self._vq_hotkeys[keystr] = hktarg

    def delHotKey(self, keystr):
        '''
        Remove a configured hotkey string.

        Example:
            w.delHotKey('ctrl+s')
        '''
        self._vq_hotkeys.pop(keystr, None)

    def loadHotKeys(self, settings):
        '''
        Load hotkey keystr/targets from the given QSettings.

        ( hotkey:<target>=<keystr> )
        '''
        for tname in self.getHotKeyTargets():

            keyobj = settings.value('hotkey:%s' % tname)

            if not keyobj.isNull():
                self.addHotKey(keyobj.toString(),tname)

    def getHotKeyFromEvent(self, event):
        '''
        A utility to retrieve the keystr from a QT keystroke event.
        '''
        key = event.key()
        txt = str(event.text())

        mods = int(event.modifiers())

        #print('HOTKEY: %s 0x%.8x' % (key, mods))

        keytxt = None

        if key < 255:
            keytxt = chr(key).lower()

        else:
            keytxt = special_keys.get(key)

        # Check for modifiers...
        if keytxt:

            if mods & QMOD_SHIFT:
                keytxt = keytxt.upper()

            if mods & QMOD_CTRL:
                if mods & QMOD_META:
                    keytxt = 'ctrl+meta+' + keytxt
                else:
                    keytxt = 'ctrl+' + keytxt

        return keytxt

    def eatKeyPressEvent(self, event):
        hotkey = self.getHotKeyFromEvent(event)
        #print 'KEYSTR:',hotkey

        target = self._vq_hotkeys.get( hotkey )
        if target != None:
            callback, args, kwargs = self._vq_hotkey_targets.get( target )
            callback(*args,**kwargs)
            event.accept()
            return True

        return False

    def keyPressEvent(self, event):
        if not self.eatKeyPressEvent(event):
            return super(HotKeyMixin, self).keyPressEvent(event)

import vqt.tree

class HotKeyEditor(vqt.tree.VQTreeView):

    def __init__(self, hotkeyobj, settings=None, parent=None):
        self._hk_settings = settings
        self._hk_hotkeyobj = hotkeyobj
        vqt.tree.VQTreeView.__init__(self, parent=parent, cols=('Hot Target', 'Hot Key'))

        model = self.model()

        lookup = dict([ (targname, keystr) for (keystr,targname) in self.getHotKeys() ])
        targets = self.getHotKeyTargets()
        targets.sort()

        for targname in targets:
            model.append((targname,lookup.get(targname, '')))

        self.setWindowTitle('Hotkey Editor')

