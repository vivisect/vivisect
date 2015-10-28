"""
Unified config object for all vtoys.
"""

import os
import sys
import json
import getpass

from ConfigParser import ConfigParser
from cStringIO import StringIO

def gethomedir(*paths):
    homepath = os.path.expanduser('~')
    path = os.path.join(homepath, *paths)

    if path != None and not os.path.exists(path):
        try:
            os.makedirs(path)
        except Exception, err:
            print('FIXME - invalid homedir, playing along...')
            pass

    return path

def getusername():
    return getpass.getuser()

compattypes = {
    int:(int,long),
    str:(str,unicode),
    bool:(bool,),
    long:(int,long),
    unicode:(str,unicode),
    type(None):(int,str,bool,long,unicode),
}

class EnviConfig:
    '''
    EnviConfig basically works like a multi-layer dictionary that 
    loads and stores config data.

    Set a config parameter:     cfg['foo'] = 'bar'
    Get a config parameter:     cfg['foo']
      or access parm using:     cfg.foo  
    Multilevel:                 cfg.baz.bilbo.foo

    Create/get a subconfig:     cfg.getSubConfig('baz', add=True)
    Parse Text Config Options:  cfg.parseConfigOption("string.of.subconfigs=bar")

    Save the configuration:     cfg.saveConfigFile()
    Load the configuration:     cfg.loadConfigFile()
                                # both take optional filenames
    '''

    def __init__(self, filename=None, defaults=None, docs=None):
        self.cfginfo = {}
        self.cfgdocs = {}
        self.autosave = True
        self.filename = filename
        self.cfgsubsys = {}

        if defaults != None:
            self.setConfigPrimitive( defaults )

        if filename != None and os.path.isfile(filename):
            self.loadConfigFile( filename )

        if docs != None:
            self.setDocsPrimitive(docs)

    def getOptionDoc(self, optname):
        '''
        Retrieve docs about the given option if present.

        Example:
            doc = config.getOptionDoc('woot')
            if doc != None:
                print('woot: %s' % doc)
        '''
        return self.cfgdocs.get(optname)

    def parseConfigOption(self, optstr):
        '''
        Parse a simple foo.bar.baz=<json> syntax string into
        the current config.
        '''
        optpath,valstr = optstr.split('=',1)

        optparts = optpath.split('.')

        config = self
        for opart in optparts[:-1]:
            config = config.getSubConfig(opart, add=False)
            if config == None:
                raise Exception('Invalid Config Name: %s' % optpath)

        optname = optparts[-1]
        if not config.cfginfo.has_key(optname):
            raise Exception('Invalid Config Option: %s' % optname)

        # json madness
        if valstr.startswith('0x'):
            valstr = str(int(valstr, 16))

        if not (valstr.startswith('"') and valstr.endswith('"')):
            if valstr.lower() == 'true':
                valstr = 'true'
            elif valstr.lower() == 'false':
                valstr = 'false'

            else:
                try:
                    int(valstr)
                except:
                    valstr = '"' + valstr + '"'

        config[ optname ] = json.loads(valstr)

    def getSubConfig(self, name, add=True):
        subcfg = self.cfgsubsys.get( name )
        if subcfg == None and add:
            subcfg = EnviConfig()
            self.cfgsubsys[ name ] = subcfg
            subcfg.autosave = self.autosave
            # Monkey patch the save method...
            subcfg.saveConfigFile = self.saveConfigFile
        return subcfg

    def getSubConfigNames(self):
        return self.cfgsubsys.keys()

    def setDocsPrimitive(self, docsdict):

        for key,val in docsdict.items():

            if isinstance(val, dict):
                subcfg = self.getSubConfig(key)
                subcfg.setDocsPrimitive( val )
                continue

            self.cfgdocs[ key ] = val

    def setConfigDefault(self, optname, optval, optdoc):
        if not self.cfginfo.has_key(optname):
            self.cfginfo[optname] = optval
        self.cfgdocs[optname] = optdoc

    def getConfigPrimitive(self):
        ret = dict( self.cfginfo )
        for subname,subcfg in self.cfgsubsys.items():
            ret[ subname ] = subcfg.getConfigPrimitive()
        return ret

    def setConfigPrimitive(self, cfgdict):
        for key,val in cfgdict.items():
            if isinstance(val, dict):
                subcfg = self.getSubConfig(key)
                subcfg.setConfigPrimitive( val )
                continue

            self.cfginfo[ key ] = val

    def saveConfigFile(self, filename=None):
        '''
        Save the config information to file.
        '''
        if filename == None:
            filename = self.filename

        cfgdict = self.getConfigPrimitive()
        fd = file(filename,'wb')
        json.dump( cfgdict, fd, indent=2 )

    def loadConfigFile(self, filename=None):
        '''
        Load config info from a file.
        '''
        if filename == None:
            filename = self.filename
        fd = file(filename, 'rb')
        cfgdict = json.load( fd )
        self.setConfigPrimitive( cfgdict )

    def __getattr__(self, name):

        value = self.cfginfo.get(name)
        if value != None:
            return value

        value = self.cfgsubsys.get(name)
        if value:
            return value

        raise AttributeError('%s has no %s' % (self.__class__.__name__, name))

    #####################################################
    # A few things so it smells kinda like a dictionary
    def __setitem__(self, key, val):
        curval = self.cfginfo.get(key)
        if type(val) not in compattypes.get(type(curval)):
            raise ValueError('%r incompatible with %r' % (val,curval))

        self.cfginfo[key] = val

        if self.autosave:
            self.saveConfigFile()

    def __getitem__(self, key, default=None):
        return self.cfginfo.get(key,default)

    def get(self, key, default=None):
        return self.cfginfo.get(key, default)

    def pop(self, key, default=None):
        return self.cfginfo.pop(key, default)
        if self.autosave:
            self.saveConfigFile()

    def keys(self):
        return self.cfginfo.keys()

    def items(self):
        return self.cfginfo.items()

if __name__ == '__main__':
    defaults = {
        'woot':10,
        'foosub': {
            'bar':'qwer',
            'baz':( 'one','two','three'),
         }
    }
    cfg = EnviConfig(defaults=defaults)

    print cfg.woot + 20
    print cfg.foosub.bar
    for thing in cfg.foosub.baz:
        print thing

    cfg.saveConfigFile('cfg.test')

