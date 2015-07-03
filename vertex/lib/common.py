'''
Common utilities for vertex
'''
def tufo(idx,**info):
    return (idx,info)

class CtorDict:
    '''
    A dict like object that allows declared keys with ctors.
    The CtorDict is similar to a collections.defaultdict except
    each key may have its own declared constructor.  Used for
    caching and on-demand parsers.
 
    '''

    def __init__(self):
        self._info_doc = {}
        self._info_dict = {}
        self._info_ctor = {}

    def get(self, name):
        '''
        Retrieve/Construct a value by key.
        '''
        info = self._info_dict.get(name)
        if info == None:
            ctor = self._info_ctor.get('ctor')
            if ctor != None:
                info = ( ctor(), )
            else:
                info = (None,)

            self._info_dict[name] = info
        return info[0]

    def set(self, name, valu):
        '''
        Set a value by key.
        '''
        self._info_dict[name] = (valu,)

    def init(self, name, ctor=None, doc=None):
        '''
        Initialize the constructor callback for a key.
        '''
        self._info_doc[name] = doc
        self._info_ctor[name] = ctor
