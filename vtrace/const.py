# Order must match format junk
# NOTIFY_ALL is kinda special, if you registerNotifier
# with it, you get ALL notifications.
NOTIFY_ALL = 0          # Get all notifications
NOTIFY_SIGNAL = 1       # Callback on signal/exception
NOTIFY_BREAK = 2        # Callback on breakpoint / sigtrap
NOTIFY_STEP = 3         # Callback on singlestep complete
NOTIFY_SYSCALL = 4      # Callback on syscall (linux only for now)
NOTIFY_CONTINUE = 5     # Callback on continue (not done for step)
NOTIFY_EXIT = 6         # Callback on process exit
NOTIFY_ATTACH = 7       # Callback on successful attach
NOTIFY_DETACH = 8       # Callback on impending process detach
# The following notifiers are *only* available on some platforms
# (and may be kinda faked out ala library load events on posix)
NOTIFY_LOAD_LIBRARY = 9
NOTIFY_UNLOAD_LIBRARY = 10
NOTIFY_CREATE_THREAD = 11
NOTIFY_EXIT_THREAD = 12
NOTIFY_DEBUG_PRINT = 13 # Some platforms support this (win32).
NOTIFY_MAX = 20

# File Descriptor / Handle Types
FD_UNKNOWN = 0 # Unknown or we don't have a type for it
FD_FILE = 1
FD_SOCKET = 2
FD_PIPE = 3
FD_LOCK = 4   # Win32 Mutant/Lock/Semaphore
FD_EVENT = 5  # Win32 Event/KeyedEvent
FD_THREAD = 6 # Win32 Thread
FD_REGKEY = 7 # Win32 Registry Key

# Vtrace Symbol Types
SYM_MISC = -1
SYM_GLOBAL = 0 # Global (mostly vars)
SYM_LOCAL = 1 # Locals
SYM_FUNCTION = 2 # Functions
SYM_SECTION = 3 # Binary section
SYM_META = 4 # Info that we enumerate

# Vtrace Symbol Offsets
VSYM_NAME = 0
VSYM_ADDR = 1
VSYM_SIZE = 2
VSYM_TYPE = 3
VSYM_FILE = 4
