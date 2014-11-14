import os
import sys

# Add the contrib directories to our python path
contribdir = os.path.dirname( __file__ )
if os.path.isdir( contribdir ):

    for contrib in os.listdir( contribdir ):

        contpath = os.path.join( contribdir, contrib )

        if not os.path.isdir( contpath ):
            if contrib.endswith('.egg'):
                sys.path.insert(0, contpath)

            continue

        if contrib.startswith('.'):
            continue

        #sys.path.append( contpath )
        sys.path.insert(0, contpath)

