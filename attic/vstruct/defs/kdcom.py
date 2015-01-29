"""
Initial module with supporting structures for windows
kernel serial debugging.
"""

import vstruct
from vstruct.primitives import *

# Main packet magic bytes and such
BREAKIN_PACKET                      = 0x62626262
BREAKIN_PACKET_BYTE                 = 0x62
PACKET_LEADER                       = 0x30303030
PACKET_LEADER_BYTE                  = 0x30
CONTROL_PACKET_LEADER               = 0x69696969
CONTROL_PACKET_LEADER_BYTE          = 0x69
PACKET_TRAILING_BYTE                = 0xAA

pkt_magic_names = {
    BREAKIN_PACKET:"Break Packet",
    PACKET_LEADER:"Packet",
    CONTROL_PACKET_LEADER:"Control Packet",
} 

# Primary "packet types"
PACKET_TYPE_UNUSED                  = 0
PACKET_TYPE_KD_STATE_CHANGE32       = 1
PACKET_TYPE_KD_STATE_MANIPULATE     = 2
PACKET_TYPE_KD_DEBUG_IO             = 3
PACKET_TYPE_KD_ACKNOWLEDGE          = 4
PACKET_TYPE_KD_RESEND               = 5
PACKET_TYPE_KD_RESET                = 6
PACKET_TYPE_KD_STATE_CHANGE64       = 7
PACKET_TYPE_KD_POLL_BREAKIN         = 8
PACKET_TYPE_KD_TRACE_IO             = 9
PACKET_TYPE_KD_CONTROL_REQUEST      = 10
PACKET_TYPE_KD_FILE_IO              = 11
PACKET_TYPE_MAX                     = 12

pkt_type_names = {
    PACKET_TYPE_UNUSED:"Unused",
    PACKET_TYPE_KD_STATE_CHANGE32:"State Change32",
    PACKET_TYPE_KD_STATE_MANIPULATE:"Manipulate",
    PACKET_TYPE_KD_DEBUG_IO:"Debug IO",
    PACKET_TYPE_KD_ACKNOWLEDGE:"Ack",
    PACKET_TYPE_KD_RESEND:"Resend",
    PACKET_TYPE_KD_RESET:"Reset",
    PACKET_TYPE_KD_STATE_CHANGE64:"State Change64",
    PACKET_TYPE_KD_POLL_BREAKIN:"Breakin",
    PACKET_TYPE_KD_TRACE_IO:"Trace IO",
    PACKET_TYPE_KD_CONTROL_REQUEST:"Control Request",
    PACKET_TYPE_KD_FILE_IO:"File IO",
    PACKET_TYPE_MAX:"Max",
}

# Wait State Change Types
DbgKdMinimumStateChange             = 0x00003030
DbgKdExceptionStateChange           = 0x00003030
DbgKdLoadSymbolsStateChange         = 0x00003031
DbgKdCommandStringStateChange       = 0x00003032
DbgKdMaximumStateChange             = 0x00003033

pkt_sub_wait_state_change = {
    DbgKdMinimumStateChange:"DbgKdMinimumStateChange",
    DbgKdExceptionStateChange:"DbgKdExceptionStateChange",
    DbgKdLoadSymbolsStateChange:"DbgKdLoadSymbolsStateChange",
    DbgKdCommandStringStateChange:"DbgKdCommandStringStateChange",
    DbgKdMaximumStateChange:"DbgKdMaximumStateChange",
}

# Manipulate Types
DbgKdMinimumManipulate              = 0x00003130
DbgKdReadVirtualMemoryApi           = 0x00003130
DbgKdWriteVirtualMemoryApi          = 0x00003131
DbgKdGetContextApi                  = 0x00003132
DbgKdSetContextApi                  = 0x00003133
DbgKdWriteBreakPointApi             = 0x00003134
DbgKdRestoreBreakPointApi           = 0x00003135
DbgKdContinueApi                    = 0x00003136
DbgKdReadControlSpaceApi            = 0x00003137
DbgKdWriteControlSpaceApi           = 0x00003138
DbgKdReadIoSpaceApi                 = 0x00003139
DbgKdWriteIoSpaceApi                = 0x0000313A
DbgKdRebootApi                      = 0x0000313B
DbgKdContinueApi2                   = 0x0000313C
DbgKdReadPhysicalMemoryApi          = 0x0000313D
DbgKdWritePhysicalMemoryApi         = 0x0000313E
DbgKdQuerySpecialCallsApi           = 0x0000313F
DbgKdSetSpecialCallApi              = 0x00003140
DbgKdClearSpecialCallsApi           = 0x00003141
DbgKdSetInternalBreakPointApi       = 0x00003142
DbgKdGetInternalBreakPointApi       = 0x00003143
DbgKdReadIoSpaceExtendedApi         = 0x00003144
DbgKdWriteIoSpaceExtendedApi        = 0x00003145
DbgKdGetVersionApi                  = 0x00003146
DbgKdWriteBreakPointExApi           = 0x00003147
DbgKdRestoreBreakPointExApi         = 0x00003148
DbgKdCauseBugCheckApi               = 0x00003149
DbgKdSwitchProcessor                = 0x00003150
DbgKdPageInApi                      = 0x00003151
DbgKdReadMachineSpecificRegister    = 0x00003152
DbgKdWriteMachineSpecificRegister   = 0x00003153
OldVlm1                             = 0x00003154
OldVlm2                             = 0x00003155
DbgKdSearchMemoryApi                = 0x00003156
DbgKdGetBusDataApi                  = 0x00003157
DbgKdSetBusDataApi                  = 0x00003158
DbgKdCheckLowMemoryApi              = 0x00003159
DbgKdClearAllInternalBreakpointsApi = 0x0000315A
DbgKdFillMemoryApi                  = 0x0000315B
DbgKdQueryMemoryApi                 = 0x0000315C
DbgKdSwitchPartition                = 0x0000315D
DbgKdMaximumManipulate              = 0x0000315E

pkt_sub_manipulate = {
    DbgKdMinimumManipulate:"DbgKdMinimumManipulate",
    DbgKdReadVirtualMemoryApi:"DbgKdReadVirtualMemoryApi",
    DbgKdWriteVirtualMemoryApi:"DbgKdWriteVirtualMemoryApi",
    DbgKdGetContextApi:"DbgKdGetContextApi",
    DbgKdSetContextApi:"DbgKdSetContextApi",
    DbgKdWriteBreakPointApi:"DbgKdWriteBreakPointApi",
    DbgKdRestoreBreakPointApi:"DbgKdRestoreBreakPointApi",
    DbgKdContinueApi:"DbgKdContinueApi",
    DbgKdReadControlSpaceApi:"DbgKdReadControlSpaceApi",
    DbgKdWriteControlSpaceApi:"DbgKdWriteControlSpaceApi",
    DbgKdReadIoSpaceApi:"DbgKdReadIoSpaceApi",
    DbgKdWriteIoSpaceApi:"DbgKdWriteIoSpaceApi",
    DbgKdRebootApi:"DbgKdRebootApi",
    DbgKdContinueApi2:"DbgKdContinueApi2",
    DbgKdReadPhysicalMemoryApi:"DbgKdReadPhysicalMemoryApi",
    DbgKdWritePhysicalMemoryApi:"DbgKdWritePhysicalMemoryApi",
    DbgKdQuerySpecialCallsApi:"DbgKdQuerySpecialCallsApi",
    DbgKdSetSpecialCallApi:"DbgKdSetSpecialCallApi",
    DbgKdClearSpecialCallsApi:"DbgKdClearSpecialCallsApi",
    DbgKdSetInternalBreakPointApi:"DbgKdSetInternalBreakPointApi",
    DbgKdGetInternalBreakPointApi:"DbgKdGetInternalBreakPointApi",
    DbgKdReadIoSpaceExtendedApi:"DbgKdReadIoSpaceExtendedApi",
    DbgKdWriteIoSpaceExtendedApi:"DbgKdWriteIoSpaceExtendedApi",
    DbgKdGetVersionApi:"DbgKdGetVersionApi",
    DbgKdWriteBreakPointExApi:"DbgKdWriteBreakPointExApi",
    DbgKdRestoreBreakPointExApi:"DbgKdRestoreBreakPointExApi",
    DbgKdCauseBugCheckApi:"DbgKdCauseBugCheckApi",
    DbgKdSwitchProcessor:"DbgKdSwitchProcessor",
    DbgKdPageInApi:"DbgKdPageInApi",
    DbgKdReadMachineSpecificRegister:"DbgKdReadMachineSpecificRegister",
    DbgKdWriteMachineSpecificRegister:"DbgKdWriteMachineSpecificRegister",
    OldVlm1:"OldVlm1",
    OldVlm2:"OldVlm2",
    DbgKdSearchMemoryApi:"DbgKdSearchMemoryApi",
    DbgKdGetBusDataApi:"DbgKdGetBusDataApi",
    DbgKdSetBusDataApi:"DbgKdSetBusDataApi",
    DbgKdCheckLowMemoryApi:"DbgKdCheckLowMemoryApi",
    DbgKdClearAllInternalBreakpointsApi:"DbgKdClearAllInternalBreakpointsApi",
    DbgKdFillMemoryApi:"DbgKdFillMemoryApi",
    DbgKdQueryMemoryApi:"DbgKdQueryMemoryApi",
    DbgKdSwitchPartition:"DbgKdSwitchPartition",
    DbgKdMaximumManipulate:"DbgKdMaximumManipulate",
}

# Debug I/O Types
DbgKdPrintStringApi                 = 0x00003230
DbgKdGetStringApi                   = 0x00003231

# Control Report Flags
REPORT_INCLUDES_SEGS                = 0x0001
REPORT_INCLUDES_CS                  = 0x0002

# Protocol Versions
DBGKD_64BIT_PROTOCOL_VERSION1       = 5
DBGKD_64BIT_PROTOCOL_VERSION2       = 6

# Query Memory Address Spaces
DBGKD_QUERY_MEMORY_VIRTUAL          = 0
DBGKD_QUERY_MEMORY_PROCESS          = 0
DBGKD_QUERY_MEMORY_SESSION          = 1
DBGKD_QUERY_MEMORY_KERNEL           = 2

# Query Memory Flags
DBGKD_QUERY_MEMORY_READ             = 0x01
DBGKD_QUERY_MEMORY_WRITE            = 0x02
DBGKD_QUERY_MEMORY_EXECUTE          = 0x04
DBGKD_QUERY_MEMORY_FIXED            = 0x08

ULONG = v_uint32
ULONG64 = v_uint64
BOOLEAN = v_uint32

class DBGKD_LOAD_SYMBOLS64(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self._vs_field_align = True
        self.PathNameLength = v_uint32()
        self.BaseOfDll = v_uint64()
        self.ProcessId = v_uint64()
        self.CheckSum = v_uint32()
        self.SizeOfImage = v_uint32()
        #self.UnloadSymbols = v_uint8()
        self.UnloadSymbols = v_uint32() # HACK must be 32 bit aligned

class DBGKD_WAIT_STATE_CHANGE64(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self._vs_field_align = True
        self.NewState = v_uint32()
        self.ProcessorLevel = v_uint16()
        self.Processor = v_uint16()
        self.NumberProcessors = v_uint32()
        self.Thread = v_uint64()
        self.ProgramCounter = v_uint64()

