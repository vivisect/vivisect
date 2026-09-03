"""
Posix Signals (most common for use with GDBSTUB)
"""
# SIGHUP =      1
# SIGINT =      2
# SIGQUIT =     3
# SIGILL =      4
# SIGTRAP =     5
# SIGABRT =     6
# SIGIOT =      6
# SIGBUS =      7
# SIGFPE =      8
# SIGKILL =     9
# SIGUSR1 =    10
# SIGSEGV =    11
# SIGUSR2 =    12
# SIGPIPE =    13
# SIGALRM =    14
# SIGTERM =    15
# SIGSTKFLT =  16
# SIGCHLD =    17
# SIGCONT =    18
# SIGSTOP =    19
# SIGTSTP =    20
# SIGTTIN =    21
# SIGTTOU =    22
# SIGURG =     23
# SIGXCPU =    24
# SIGXFSZ =    25
# SIGVTALRM =  26
# SIGPROF =    27
# SIGWINCH =   28
# SIGIO =      29
# SIGPOLL =    SIGIO
# SIGLOST =    29
# SIGPWR =     30
# SIGSYS =     31
# SIGUNUSED =  31

SIG_0 =	0	# Signal 0
#define TARGET_SIGNAL_FIRST TARGET_SIGNAL_0
SIGHUP =	1	# Hangup
SIGINT =	2	# Interrupt
SIGQUIT =	3	# Quit
SIGILL =	4	# Illegal instruction
SIGTRAP =	5	# Trace/breakpoint trap
SIGABRT =	6	# Aborted
SIGEMT =	7	# Emulation trap
SIGFPE =	8	# Arithmetic exception
SIGKILL =	9	# Killed
SIGBUS =	10	# Bus error
SIGSEGV =	11	# Segmentation fault
SIGSYS =	12	# Bad system call
SIGPIPE =	13	# Broken pipe
SIGALRM =	14	# Alarm clock
SIGTERM =	15	# Terminated
SIGURG =	16	# Urgent I/O condition
SIGSTOP =	17	# Stopped (signal)
SIGTSTP =	18	# Stopped (user)
SIGCONT =	19	# Continued
SIGCHLD =	20	# Child status changed
SIGTTIN =	21	# Stopped (tty input)
SIGTTOU =	22	# Stopped (tty output)
SIGIO =	23	# I/O possible
SIGXCPU =	24	# CPU time limit exceeded
SIGXFSZ =	25	# File size limit exceeded
SIGVTALRM =	26	# Virtual timer expired
SIGPROF =	27	# Profiling timer expired
SIGWINCH =	28	# Window size changed
SIGLOST =	29	# Resource lost
SIGUSR1 =	30	# User defined signal 1
SIGUSR2 =	31	# User defined signal 2
SIGPWR =	32	# Power fail/restart
#/* Similar to SIGIO.  Perhaps they should have the same number.  */
SIGPOLL =	33	# Pollable event occurred
SIGWIND =	34	# SIGWIND
SIGPHONE =	35	# SIGPHONE
SIGWAITING =	36	# Process's LWPs are blocked
SIGLWP =	37	# Signal LWP
SIGDANGER =	38	# Swap space dangerously low
SIGGRANT =	39	# Monitor mode granted
SIGRETRACT =	40	# Need to relinquish monitor mode
SIGMSG =	41	# Monitor mode data available
SIGSOUND =	42	# Sound completed
SIGSAK =	43	# Secure attention
SIGPRIO =	44	# SIGPRIO
SIG33 =	45	# Real-time event 33
SIG34 =	46	# Real-time event 34
SIG35 =	47	# Real-time event 35
SIG36 =	48	# Real-time event 36
SIG37 =	49	# Real-time event 37
SIG38 =	50	# Real-time event 38
SIG39 =	51	# Real-time event 39
SIG40 =	52	# Real-time event 40
SIG41 =	53	# Real-time event 41
SIG42 =	54	# Real-time event 42
SIG43 =	55	# Real-time event 43
SIG44 =	56	# Real-time event 44
SIG45 =	57	# Real-time event 45
SIG46 =	58	# Real-time event 46
SIG47 =	59	# Real-time event 47
SIG48 =	60	# Real-time event 48
SIG49 =	61	# Real-time event 49
SIG50 =	62	# Real-time event 50
SIG51 =	63	# Real-time event 51
SIG52 =	64	# Real-time event 52
SIG53 =	65	# Real-time event 53
SIG54 =	66	# Real-time event 54
SIG55 =	67	# Real-time event 55
SIG56 =	68	# Real-time event 56
SIG57 =	69	# Real-time event 57
SIG58 =	70	# Real-time event 58
SIG59 =	71	# Real-time event 59
SIG60 =	72	# Real-time event 60
SIG61 =	73	# Real-time event 61
SIG62 =	74	# Real-time event 62
SIG63 =	75	# Real-time event 63

#/* Used internally by Solaris threads.  See signal(5) on Solaris.  */
SIGCANCEL =	76	# LWP internal signal

#/* Yes, this pains me, too.  But LynxOS didn't have SIG32, and now
   #GNU/Linux does, and we can't disturb the numbering, since it's
   #part of the remote protocol.  Note that in some GDB's
   #TARGET_SIGNAL_REALTIME_32 is number 76.  */
SIG32 =	77	# Real-time event 32
#/* Yet another pain, IRIX 6 has SIG64. */
SIG64 =	78	# Real-time event 64
#/* Yet another pain, GNU/Linux MIPS might go up to 128. */
SIG65 =	79	# Real-time event 65
SIG66 =	80	# Real-time event 66
SIG67 =	81	# Real-time event 67
SIG68 =	82	# Real-time event 68
SIG69 =	83	# Real-time event 69
SIG70 =	84	# Real-time event 70
SIG71 =	85	# Real-time event 71
SIG72 =	86	# Real-time event 72
SIG73 =	87	# Real-time event 73
SIG74 =	88	# Real-time event 74
SIG75 =	89	# Real-time event 75
SIG76 =	90	# Real-time event 76
SIG77 =	91	# Real-time event 77
SIG78 =	92	# Real-time event 78
SIG79 =	93	# Real-time event 79
SIG80 =	94	# Real-time event 80
SIG81 =	95	# Real-time event 81
SIG82 =	96	# Real-time event 82
SIG83 =	97	# Real-time event 83
SIG84 =	98	# Real-time event 84
SIG85 =	99	# Real-time event 85
SIG86 =	100	# Real-time event 86
SIG87 =	101	# Real-time event 87
SIG88 =	102	# Real-time event 88
SIG89 =	103	# Real-time event 89
SIG90 =	104	# Real-time event 90
SIG91 =	105	# Real-time event 91
SIG92 =	106	# Real-time event 92
SIG93 =	107	# Real-time event 93
SIG94 =	108	# Real-time event 94
SIG95 =	109	# Real-time event 95
SIG96 =	110	# Real-time event 96
SIG97 =	111	# Real-time event 97
SIG98 =	112	# Real-time event 98
SIG99 =	113	# Real-time event 99
SIG100 =	114	# Real-time event 100
SIG101 =	115	# Real-time event 101
SIG102 =	116	# Real-time event 102
SIG103 =	117	# Real-time event 103
SIG104 =	118	# Real-time event 104
SIG105 =	119	# Real-time event 105
SIG106 =	120	# Real-time event 106
SIG107 =	121	# Real-time event 107
SIG108 =	122	# Real-time event 108
SIG109 =	123	# Real-time event 109
SIG110 =	124	# Real-time event 110
SIG111 =	125	# Real-time event 111
SIG112 =	126	# Real-time event 112
SIG113 =	127	# Real-time event 113
SIG114 =	128	# Real-time event 114
SIG115 =	129	# Real-time event 115
SIG116 =	130	# Real-time event 116
SIG117 =	131	# Real-time event 117
SIG118 =	132	# Real-time event 118
SIG119 =	133	# Real-time event 119
SIG120 =	134	# Real-time event 120
SIG121 =	135	# Real-time event 121
SIG122 =	136	# Real-time event 122
SIG123 =	137	# Real-time event 123
SIG124 =	138	# Real-time event 124
SIG125 =	139	# Real-time event 125
SIG126 =	140	# Real-time event 126
SIG127 =	141	# Real-time event 127

SIGINFO =	142	# Information request

#/* Some signal we don't know about.  */
NULL_1 =	143	# Unknown signal

#/* Use whatever signal we use when one is not specifically specified
#   (for passing to proceed and so on).  */
NULL_2 =	144	# Internal error: printing TARGET_SIGNAL_DEFAULT

#/* Mach exceptions.  In versions of GDB before 5.2, these were just before
   #TARGET_SIGNAL_INFO if you were compiling on a Mach host (and missing
   #otherwise).  */
EXC_BAD_ACCESS =	145	# Could not access memory
EXC_BAD_INSTRUCTION =	146	# Illegal instruction/operand
EXC_ARITHMETIC =	147	# Arithmetic exception
EXC_EMULATION =	148	# Emulation instruction
EXC_SOFTWARE =	149	# Software generated exception
EXC_BREAKPOINT =	150	# Breakpoint

#/* If you are adding a new signal, add it just above this comment.  */

#/* Last and unused enum value, for sizing arrays, etc.  */
NULL_3 =	151	# TARGET_SIGNAL_MAGIC

signals = dict({val: key for key, val in locals().items() if key.startswith("SIG")})

