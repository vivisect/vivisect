'''
The cobra "auth" package allows modular authentication
for cobra shared objects
'''

class CobraAuthenticator:

    def __init__(self):
        pass

    def authCobraUser(self, authinfo):
        '''
        Authenticate a user and return their user name.
        Arguments:
            authinfo - a dictionary which can be authmod dependant
                       ( but probably just has user & passwd )
        '''
        # This is *totally* example code... you probably want something
        # from a submodule like cobra.auth.shadowfile
        if authinfo.get('user') != 'invisigoth':
            return None
        if authinfo.get('passwd') != 'secret':
            return None
        return 'invisigoth'

    def checkUserAccess(self, authuser, objname ):
        '''
        Enforce access control on a per shared object basis.
        '''
        return True

