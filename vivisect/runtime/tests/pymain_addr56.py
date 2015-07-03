import ctypes
import dbgmain
dbgmain.mainwait()
try:
    x = ctypes.string_at(0x56565656)
except Exception as e:
    pass
