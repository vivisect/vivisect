import os
import platform
# abstract several python 2 vs 3 imports / apis

pyver = tuple([ int(v) for v in platform.python_version().split('.') ])

if pyver >= (3,0,0):
    import queue
    import pickle
    import urllib.parse as urlparse
    import urllib.request as urllib

else: # python 2.x....

    #if os.getenv('VIVPY3'):
        # avoid globally scoped import parser...
        #from __future__ import division
        #from __future__ import print_function
        #from __future__ import absolute_import
        #from __future__ import unicode_literals

    import urlparse
    import Queue as queue
    import cPickle as pickle

    # must go at the end due to "urllib" override
    import urllib2 as urllib
