'''
Exceptions for GDBSTUB code
'''

class GdbBreakException(Exception):
    pass

class InvalidGdbPacketException(Exception):
    pass
