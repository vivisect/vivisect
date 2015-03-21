'''
The "hotmess" module allows a single import that clutters your namespace.

Mostly intended to enable scripts/simple code to be terse.

Example:

    from vivisect.debug.hotmess import *

    trace = attach('foo.exe')

'''
import vivisect.debug.asi as v_dbgapi

dbgapi = 
