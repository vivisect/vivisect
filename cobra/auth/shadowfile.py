import os
import sys
import getpass
import hashlib
import argparse
import binascii

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
        if not os.path.isfile(filename):
            raise Exception('No Such File: %s' % filename)

    def authCobraUser(self, authinfo):
        user = authinfo.get('user').lower()
        passwd = authinfo.get('passwd')
        userhdr = '%s:' % user
        with open(self.filename, 'r') as fd:
            for line in fd.readlines():
                if not line.startswith(userhdr):
                    continue

                line = line.strip()
                # We are on the correct line
                suser, spasswd = line.split(':')
                salt, pwhash = spasswd.split('$')
                enc = salt + passwd
                if hashlib.sha256(enc.encode('utf-8')).hexdigest() == pwhash:
                    return user

                break

        return None


def setup():
    desc = 'Helper tool for making shadow file rows'
    ap = argparse.ArgumentParser('cobra.auth.shadowfile', description=desc)
    ap.add_argument('user', help='username to create password for')
    ap.add_argument('--passwd', default=getpass.getpass(), help='optional password to hash')

    return ap


def main(argv):
    opts = setup().parse_args(argv)
    user = opts.user.lower()

    salt = binascii.hexlify(os.urandom(8))
    hash = hashlib.sha256(salt + opts.passwd).hexdigest()
    print('%s:%s$%s' % (user, salt, hash))


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
