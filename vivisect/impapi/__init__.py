'''
Calling convention and API definitions for various APIs/archs.
'''
import sys


class ImportApi:

    def __init__(self):
        self._api_lookup = {}
        self._apitype_lookup = {}

    def getImpApiType(self, tname):
        return self._apitype_lookup.get(tname)

    def updateApiDef(self, apidict):
        self._api_lookup.update(apidict)

    def getImpApi(self, funcname):
        '''
        An API definition consists of the following:
            ( rettype, retname, callconv, funcname, ( (argtype, argname), ...) )
        '''
        return self._api_lookup.get(funcname.lower())

    def getImpApiCallConv(self, funcname):
        ret = self._api_lookup.get(funcname.lower())
        if ret is None:
            return None
        return ret[2]

    def getImpApiArgs(self, funcname):
        ret = self._api_lookup.get(funcname.lower())
        if ret is None:
            return None
        return ret[4]

    def getImpApiRetType(self, funcname):
        ret = self._api_lookup.get(funcname.lower())
        if ret is None:
            return None
        return ret[0]

    def getImpApiRetName(self, funcname):
        ret = self._api_lookup.get(funcname.lower())
        if ret is None:
            return None
        return ret[1]

    def getImpApiArgTypes(self, funcname):
        ret = self._api_lookup.get(funcname.lower())
        if ret is None:
            return None
        return [argt for (argt, argn) in ret[4]]

    def getImpApiArgNames(self, funcname):
        ret = self._api_lookup.get(funcname.lower())
        if ret is None:
            return None
        return [argn for (argt, argn) in ret[4]]

    def addImpApi(self, api, arch):
        api = api.lower()
        arch = arch.lower()

        # First try to look for a specific IMPAPI, if that fails use just the
        # "api" name to get a generic IMPAPI
        try:
            modname = 'vivisect.impapi.%s.%s' % (api, arch)
            __import__(modname)
            mod = sys.modules[modname]
            self._api_lookup.update(mod.api)
        except ModuleNotFoundError:
            modname = 'vivisect.impapi.%s' % api
            __import__(modname)
            mod = sys.modules[modname]
            self._api_lookup.update(mod.getGenericImpApi(arch))

        self._apitype_lookup.update(mod.apitypes)


def getImportApi(api, arch):
    impapi = ImportApi()
    impapi.addImpApi(api, arch)
    return impapi
