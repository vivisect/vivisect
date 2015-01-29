import os
import sys
import getpass
import hashlib

import cobra.auth as c_auth

class ShadowFileAuth(c_auth.CobraAuthenticator):

    '''
    An auth module which uses a simple text file with salted SHA256
    password hashes.  ( this module may be executed as main to produce
    rows for the file )

    File Format:
    # comment
    <username>:<salt>$<saltedhash>
    '''
    def __init__(self, filename):
        c_auth.CobraAuthenticator.__init__(self)
        self.filename = filename
        if not os.path.isfile( filename ):
            raise Exception('No Such File: %s' % filename)

    def authCobraUser(self, authinfo):
        user = authinfo.get('user').lower()
        passwd = authinfo.get('passwd')
        userhdr = '%s:' % user
        for line in open(self.filename,'rb').readlines():
            if not line.startswith(userhdr):
                continue

            line = line.strip()
            # We are on the correct line
            suser,spasswd = line.split(':')
            salt,pwhash = spasswd.split('$')
            if hashlib.sha256( salt + passwd ).hexdigest() == pwhash:
                return user

            break

        return None

if __name__ == '__main__':
    # A helper for making shadow file rows...
    if len(sys.argv) == 1:
        print('Usage: python -m cobra.auth.shadowfile <username> [password]')
        sys.exit(0)

    user = sys.argv[1].lower()
    if len(sys.argv) == 2:
        passwd = getpass.getpass()
    else:
        passwd = sys.argv[2]

    salt = os.urandom(8).encode('hex')
    hash = hashlib.sha256( salt + passwd ).hexdigest()
    print '%s:%s$%s' % (user,salt,hash)
