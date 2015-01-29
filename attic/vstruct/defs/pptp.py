from vstruct import VStruct
from vstruct.primitives import *

magic = 0x1a2b3c4d

StartCtrlConnReq        = 1
StartCtrlConnRep        = 2
StopCtrlConnReq         = 3
StopCtrlConnRep         = 4

         #Start-Control-Connection-Request            1
         #Start-Control-Connection-Reply              2
         #Stop-Control-Connection-Request             3
         #Stop-Control-Connection-Reply               4
         #Echo-Request                                5
         #Echo-Reply                                  6

         #(Call Management)

         #Outgoing-Call-Request                       7
         #Outgoing-Call-Reply                         8
         #Incoming-Call-Request                       9
         #Incoming-Call-Reply                        10
         #Incoming-Call-Connected                    11
         #Call-Clear-Request                         12
         #Call-Disconnect-Notify                     13

         #(Error Reporting)

         #WAN-Error-Notify                           14

         #(PPP Session Control)

         #Set-Link-Info                              15

'''
    StartCtrlConnReq:

      0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
      |             Length            |       PPTP Message Type       |
      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
      |                         Magic Cookie                          |
      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
      |     Control Message Type      |           Reserved0           |
      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
      |       Protocol Version        |           Reserved1           |
      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
      |                     Framing Capabilities                      |
      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
      |                      Bearer Capabilities                      |
      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
      |       Maximum Channels        |       Firmware Revision       |
      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
      |                                                               |
      +                     Host Name (64 octets)                     +
      |                                                               |
      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
      |                                                               |
      +                   Vendor String (64 octets)                   +
      |                                                               |
      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

    StopCtrlConnReq:

       0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
      |             Length            |       PPTP Message Type       |
      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
      |                         Magic Cookie                          |
      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
      |     Control Message Type      |           Reserved0           |
      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
      |    Reason     |   Reserved1   |           Reserved2           |
      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
'''


class PPTPHeader(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.msgsize    = v_uint16(bigend=True)
        self.msgtype    = v_uint16(bigend=True)
        self.pptpmagic  = v_uint32(bigend=True)
        self.ctrltype   = v_uint16(bigend=True)
        self.res0       = v_uint16(bigend=True)

class PPTP(VStruct):

    def __init__(self):
        VStruct.__init__(self)
        # break it up into fixed header and dyn fields
        self.pptphdr = PPTPHeader()
        self.pptpmsg = VStruct()

    def pcb_pptphdr(self):
        size = self.pptphdr.msgsize - len(self.pptphdr)
        msgtype = self.pptphdr.msgtype

        if msgtype == StartCtrlConnReq:
            self.pptpmsg.protover   = v_uint16(bigend=True)
            self.pptpmsg.res1       = v_uint16(bigend=True)
            self.pptpmsg.framecapa  = v_uint32(bigend=True)
            self.pptpmsg.bearrcapa  = v_uint32(bigend=True)
            self.pptpmsg.maxchan    = v_uint16(bigend=True)
            self.pptpmsg.firmware   = v_uint16(bigend=True)
            self.pptpmsg.hostname   = v_str(size=64)
            self.pptpmsg.vendor   = v_str(size=64)
            return

        if msgtype == StartCtrlConnRep:
            self.pptpmsg.protover   = v_uint16(bigend=True)
            self.pptpmsg.rescode    = v_uint8()
            self.pptpmsg.errcode    = v_uint8()
            self.pptpmsg.framecapa  = v_uint32(bigend=True)
            self.pptpmsg.bearrcapa  = v_uint32(bigend=True)
            self.pptpmsg.maxchan    = v_uint16(bigend=True)
            self.pptpmsg.firmware   = v_uint16(bigend=True)
            self.pptpmsg.hostname   = v_str(size=64)
            self.pptpmsg.vendor   = v_str(size=64)
            return

        if msgtype in (StopCtrlConnReq,StopCtrlConnRep):
            self.pptpmsg.reason     = v_uint8()
            self.pptpmsg.res1       = v_uint8()
            self.pptpmsg.res2       = v_uint16(bigend=True)

        self.pptpmsg.payload = v_bytes(size=size)

