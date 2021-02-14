"""
Unified config object for all vtoys.
"""

import os
import json
import getpass
import logging

import envi.exc as e_exc

logger = logging.getLogger(__name__)

CONFIG_PATH = 0
CONFIG_ENTRY = 1


def gethomedir(*paths, **kwargs):
    makedir = kwargs.get('makedir', True)
    homepath = os.path.expanduser('~')
    path = os.path.join(homepath, *paths)

    if path is not None and not os.path.exists(path) and makedir:
        try:
            os.makedirs(path)
        except Exception as err:
            logger.warning('FIXME - invalid homedir, playing along... (%s)', err)

    return path


def getusername():
    return getpass.getuser()


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

    def __init__(self, filename=None, defaults=None, docs=None, autosave=False):
        self.cfginfo = {}
        self.cfgdocs = {}
        self.autosave = autosave
        self.filename = filename
        self.cfgsubsys = {}

        if defaults is not None:
            self.setConfigPrimitive(defaults)

        if filename is not None and os.path.isfile(filename):
            self.loadConfigFile(filename)

        if docs is not None:
            self.setDocsPrimitive(docs)

    def getOptionDoc(self, optname):
        '''
        Retrieve docs about the given option if present.

        Example:
            doc = config.getOptionDoc('woot')
            if doc is not None:
                print('woot: %s' % doc)
        '''
        return self.cfgdocs.get(optname)

    def getConfigPaths(self):
        '''
        Return a list of tuples including: (type, valid path strings, existing value)

        'type' can be CONFIG_PATH or CONFIG_ENTRY to indicate whether the tuple
        represents a subconfig or an actual key/value pair
        '''
        paths = []
        todo = [([], self)]

        while todo:
            path, config = todo.pop()

            cfgkeys = config.keys()
            if cfgkeys:
                pathstr = '.'.join(path) + "."
                newpaths = [(CONFIG_ENTRY, "%s%s" % (pathstr, key), "%s" % (config[key])) for key in cfgkeys]
                paths.extend(newpaths)

            subnames = config.getSubConfigNames()
            if not len(subnames):
                paths.append((CONFIG_PATH, '.'.join(path), None))
                continue

            for subname in subnames:
                newpath = path[:]
                newpath.append(subname)
                newconfig = config.getSubConfig(subname, add=False)
                todo.append((newpath, newconfig))

        return paths

    def reprConfigPaths(self):
        '''
        Returns a string representation of the configuration paths/options
        and optionally values.  Useful for printing helper data.
        '''
        configpaths = self.getConfigPaths()
        out = ["Valid Config Entries:\n    "]
        reprs = ['%s = %s' % (ckey, cval) for ctype, ckey, cval in configpaths if ctype == CONFIG_ENTRY]
        out.append("\n    ".join(reprs))
        out.append("\n")

        out.append("\nValid Config Paths:\n    ")
        reprs = [ckey for ctype, ckey, cval in configpaths if ctype == CONFIG_PATH]
        out.append("\n    ".join(reprs))
        out.append("\n")
        return ''.join(out)

    def parseConfigOption(self, optstr):
        '''
        Parse a simple foo.bar.baz=<json> syntax string into
        the current config.
        '''
        if '=' not in optstr:
            raise e_exc.ConfigNoAssignment(optstr)

        optpath, valstr = optstr.split('=', 1)

        optparts = optpath.split('.')

        config = self
        for opart in optparts[:-1]:
            config = config.getSubConfig(opart, add=False)
            if config is None:
                raise e_exc.ConfigInvalidName(optpath)

        optname = optparts[-1]
        if optname not in config.cfginfo:
            raise e_exc.ConfigInvalidOption(optname)

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

        config[optname] = json.loads(valstr)

    def getSubConfig(self, name, add=True):
        subcfg = self.cfgsubsys.get(name)
        if subcfg is None and add:
            subcfg = EnviConfig()
            self.cfgsubsys[name] = subcfg
            subcfg.autosave = self.autosave
            # Monkey patch the save method...
            subcfg.saveConfigFile = self.saveConfigFile
        return subcfg

    def getSubConfigNames(self):
        return list(self.cfgsubsys.keys())

    def setDocsPrimitive(self, docsdict):

        for key, val in docsdict.items():

            if isinstance(val, dict):
                subcfg = self.getSubConfig(key)
                subcfg.setDocsPrimitive(val)
                continue

            self.cfgdocs[key] = val

    def setConfigDefault(self, optname, optval, optdoc):
        if optname not in self.cfginfo:
            self.cfginfo[optname] = optval
        self.cfgdocs[optname] = optdoc

    def getConfigPrimitive(self):
        ret = dict(self.cfginfo)
        for subname, subcfg in self.cfgsubsys.items():
            ret[subname] = subcfg.getConfigPrimitive()
        return ret

    def setConfigPrimitive(self, cfgdict):
        for key, val in cfgdict.items():
            if isinstance(val, dict):
                subcfg = self.getSubConfig(key)
                subcfg.setConfigPrimitive(val)
                continue

            self.cfginfo[key] = val

    def saveConfigFile(self, filename=None):
        '''
        Save the config information to file.
        '''
        if filename is None:
            filename = self.filename
        base = os.path.dirname(filename)
        if not os.path.exists(base):
            try:
                os.makedirs(base)
            except Exception as err:
                logger.warning('FIXME - invalid homedir, playing along... (%s)', err)

        cfgdict = self.getConfigPrimitive()
        with open(filename, encoding='utf-8', mode='wt') as fd:
            json.dump(cfgdict, fd, indent=2)

    def loadConfigFile(self, filename=None):
        '''
        Load config info from a file.
        '''
        if filename is None:
            filename = self.filename
        with open(filename, encoding='utf-8', mode='rt') as fd:
            cfgdict = json.load(fd)
        self.setConfigPrimitive(cfgdict)

    def __getattr__(self, name):

        value = self.cfginfo.get(name)
        if value is not None:
            return value

        value = self.cfgsubsys.get(name)
        if value:
            return value

        raise AttributeError('%s has no %s' % (self.__class__.__name__, name))

    #####################################################
    # A few things so it smells kinda like a dictionary
    def __setitem__(self, key, val):
        curval = self.cfginfo.get(key)
        if curval is not None and (type(val) is not type(curval)):
            raise ValueError('%r incompatible with %r' % (val, curval))

        self.cfginfo[key] = val

        if self.autosave:
            self.saveConfigFile()

    def __getitem__(self, key, default=None):
        return self.cfginfo.get(key, default)

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
