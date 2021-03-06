
import envi.registers as e_reg
import struct
from .const import *

PSW_P = 0
PSW_UD = 1
PSW_OV = 2
PSW_RS0 = 3
PSW_RS1 = 4
PSW_F0 = 5
PSW_AC = 6
PSW_C = 7

def handlerSplitRegisterWrite(index, emu, value):
    """
    use this handler when a register is split into two different areas of memory.  
    for example, on chipcon chips, the dptr register is stored byte-wise at 0xa0 and 0xb0.
    locs is a tuple and fmt is the format string, eg "BB"
    BYTE ORDER MUST BE ?SB! (see DPTR)
    """
    #FIXME: byte order?
    rname, rloc, rmask, rfmt, rsz, rinit, intW, intR = e_reg.reg_table[index]
    for idx in range(len(rloc)-1,-1,-1):
        byte = "%c"%(value & 0xff)
        value >>=8
        emu.writeMemory(rloc[idx], byte)
    return bytes

def handlerSplitRegisterRead(index, emu):
    """
    use this handler when a register is split into two different areas of memory.  
    for example, on chipcon chips, the dptr register is stored byte-wise at 0xa0 and 0xb0.
    locs is a tuple and fmt is the format string, eg "BB"
    BYTE ORDER MUST BE ?SB! (see DPTR)
    """
    #FIXME: byte order?
    rname, rloc, rmask, rfmt, rsz, rinit, intW, intR = e_reg.reg_table[index]
    bytes = []
    for idx in range(len(rloc)):
        bytes.append(emu.readMemory(rloc[idx], 1))
    value, = struct.unpack(rfmt, "".join(bytes))
    return value
        
        
    


# rname, rloc, rmask, rfmt, rsz, rinit, rhandler
#   rname   - "register" name
#   rloc    - location in IRAM the "register" lives
#   rmask   - bit mask (for 1byte reg's, this is 0xff)
#   rfmt    - struct format
#   rinit   - initialize to this upon reset/startup of the mcu
#   rhandler- index of handler function array (in emulator) called before writing/reading from this "register".  if writeMemory or readMemory impacts this location, the handler is called.  because hardware ports and timers are both set and read, handlers can allow for external components to "exist" in a separate module.  for instance, if we read a port, we want to be able to trigger logic that can set the response to whatever an external component might have set it to.  if we write to a port, we want to be able to save that data off.  if we modify timer control registers (say, to reset a timer), we want to be able to trigger the timer (if implemented) to behave accordingly.
reg_table_chipcon = (
    ('r0', SEG_IRAM_BASE + 0x0, 0xff, "B", 1, 0x0, None, None),
    ('r1', SEG_IRAM_BASE + 0x1, 0xff, "B", 1, 0x0, None, None),
    ('r2', SEG_IRAM_BASE + 0x2, 0xff, "B", 1, 0x0, None, None),
    ('r3', SEG_IRAM_BASE + 0x3, 0xff, "B", 1, 0x0, None, None),
    ('r4', SEG_IRAM_BASE + 0x4, 0xff, "B", 1, 0x0, None, None),
    ('r5', SEG_IRAM_BASE + 0x5, 0xff, "B", 1, 0x0, None, None),
    ('r6', SEG_IRAM_BASE + 0x6, 0xff, "B", 1, 0x0, None, None),
    ('r7', SEG_IRAM_BASE + 0x7, 0xff, "B", 1, 0x0, None, None),
    ('r8', SEG_IRAM_BASE + 0x8, 0xff, "B", 1, 0x0, None, None),
    ('r9', SEG_IRAM_BASE + 0x9, 0xff, "B", 1, 0x0, None, None),
    ('r10', SEG_IRAM_BASE + 0xa, 0xff, "B", 1, 0x0, None, None),
    ('r11', SEG_IRAM_BASE + 0xb, 0xff, "B", 1, 0x0, None, None),
    ('r12', SEG_IRAM_BASE + 0xc, 0xff, "B", 1, 0x0, None, None),
    ('r13', SEG_IRAM_BASE + 0xd, 0xff, "B", 1, 0x0, None, None),
    ('r14', SEG_IRAM_BASE + 0xe, 0xff, "B", 1, 0x0, None, None),
    ('r15', SEG_IRAM_BASE + 0xf, 0xff, "B", 1, 0x0, None, None),
    ('r16', SEG_IRAM_BASE + 0x10, 0xff, "B", 1, 0x0, None, None),
    ('r17', SEG_IRAM_BASE + 0x11, 0xff, "B", 1, 0x0, None, None),
    ('r18', SEG_IRAM_BASE + 0x12, 0xff, "B", 1, 0x0, None, None),
    ('r19', SEG_IRAM_BASE + 0x13, 0xff, "B", 1, 0x0, None, None),
    ('r20', SEG_IRAM_BASE + 0x14, 0xff, "B", 1, 0x0, None, None),
    ('r21', SEG_IRAM_BASE + 0x15, 0xff, "B", 1, 0x0, None, None),
    ('r22', SEG_IRAM_BASE + 0x16, 0xff, "B", 1, 0x0, None, None),
    ('r23', SEG_IRAM_BASE + 0x17, 0xff, "B", 1, 0x0, None, None),
    ('r24', SEG_IRAM_BASE + 0x18, 0xff, "B", 1, 0x0, None, None),
    ('r25', SEG_IRAM_BASE + 0x19, 0xff, "B", 1, 0x0, None, None),
    ('r26', SEG_IRAM_BASE + 0x1a, 0xff, "B", 1, 0x0, None, None),
    ('r27', SEG_IRAM_BASE + 0x1b, 0xff, "B", 1, 0x0, None, None),
    ('r28', SEG_IRAM_BASE + 0x1c, 0xff, "B", 1, 0x0, None, None),
    ('r29', SEG_IRAM_BASE + 0x1d, 0xff, "B", 1, 0x0, None, None),
    ('r30', SEG_IRAM_BASE + 0x1e, 0xff, "B", 1, 0x0, None, None),
    ('r31', SEG_IRAM_BASE + 0x1f, 0xff, "B", 1, 0x0, None, None),
    ('p0', SEG_SFR_BASE + 0x80, 0xff, "B", 1, 0x0, None, None),                                                                               
    ('tcon', SEG_SFR_BASE + 0x81, 0xff, "B", 1, 0x0, None, None),                                                                             
    ('p1', SEG_SFR_BASE + 0x82, 0xff, "B", 1, 0x0, None, None),                                                                               
    ('s0con', SEG_SFR_BASE + 0x83, 0xff, "B", 1, 0x0, None, None),                                                                            
    ('p2', SEG_SFR_BASE + 0x84, 0xff, "B", 1, 0x0, None, None),                                                                               
    ('ien0', SEG_SFR_BASE + 0x85, 0xff, "B", 1, 0x0, None, None),                                                                             
    ('-', SEG_SFR_BASE + 0x86, 0xff, "B", 1, 0x0, None, None),                                                                                
    ('ien1', SEG_SFR_BASE + 0x87, 0xff, "B", 1, 0x0, None, None),                                                                             
    ('ircon', SEG_SFR_BASE + 0x88, 0xff, "B", 1, 0x0, None, None),                                                                            
    ('-', SEG_SFR_BASE + 0x89, 0xff, "B", 1, 0x0, None, None),                                                                                
    ('psw', SEG_SFR_BASE + 0x8a, 0xff, "B", 1, 0x0, None, None),                                                                              
    ('timif', SEG_SFR_BASE + 0x8b, 0xff, "B", 1, 0x0, None, None),                                                                            
    ('acc', SEG_SFR_BASE + 0x8c, 0xff, "B", 1, 0x0, None, None),                                                                              
    ('ircon2', SEG_SFR_BASE + 0x8d, 0xff, "B", 1, 0x0, None, None),                                                                           
    ('b', SEG_SFR_BASE + 0x8e, 0xff, "B", 1, 0x0, None, None),                                                                                
    ('u1csr', SEG_SFR_BASE + 0x8f, 0xff, "B", 1, 0x0, None, None),                                                                            
    ('sp', SEG_SFR_BASE + 0x90, 0xff, "B", 1, 0x0, None, None),                                                                               
    ('p0ifg', SEG_SFR_BASE + 0x91, 0xff, "B", 1, 0x0, None, None),                                                                            
    ('rfim', SEG_SFR_BASE + 0x92, 0xff, "B", 1, 0x0, None, None),                                                                             
    ('-', SEG_SFR_BASE + 0x93, 0xff, "B", 1, 0x0, None, None),                                                                                
    ('t2of0', SEG_SFR_BASE + 0x94, 0xff, "B", 1, 0x0, None, None),                                                                            
    ('ip0', SEG_SFR_BASE + 0x95, 0xff, "B", 1, 0x0, None, None),                                                                              
    ('encdi', SEG_SFR_BASE + 0x96, 0xff, "B", 1, 0x0, None, None),                                                                            
    ('ip1', SEG_SFR_BASE + 0x97, 0xff, "B", 1, 0x0, None, None),                                                                              
    ('u0dbuf', SEG_SFR_BASE + 0x98, 0xff, "B", 1, 0x0, None, None),                                                                           
    ('wdctl', SEG_SFR_BASE + 0x99, 0xff, "B", 1, 0x0, None, None),                                                                            
    ('dmairq', SEG_SFR_BASE + 0x9a, 0xff, "B", 1, 0x0, None, None),                                                                           
    ('rfd', SEG_SFR_BASE + 0x9b, 0xff, "B", 1, 0x0, None, None),                                                                              
    ('rfst', SEG_SFR_BASE + 0x9c, 0xff, "B", 1, 0x0, None, None),                                                                             
    ('rfif', SEG_SFR_BASE + 0x9d, 0xff, "B", 1, 0x0, None, None),                                                                             
    ('percfg', SEG_SFR_BASE + 0x9e, 0xff, "B", 1, 0x0, None, None),                                                                           
    ('u1dbuf', SEG_SFR_BASE + 0x9f, 0xff, "B", 1, 0x0, None, None),                                                                           
    ('dpl0', SEG_SFR_BASE + 0xa0, 0xff, "B", 1, 0x0, None, None),                                                                             
    ('p1ifg', SEG_SFR_BASE + 0xa1, 0xff, "B", 1, 0x0, None, None),                                                                            
    ('dps', SEG_SFR_BASE + 0xa2, 0xff, "B", 1, 0x0, None, None),                                                                              
    ('ien2', SEG_SFR_BASE + 0xa3, 0xff, "B", 1, 0x0, None, None),                                                                             
    ('t2of1', SEG_SFR_BASE + 0xa4, 0xff, "B", 1, 0x0, None, None),                                                                            
    ('-', SEG_SFR_BASE + 0xa5, 0xff, "B", 1, 0x0, None, None),                                                                                
    ('encdo', SEG_SFR_BASE + 0xa6, 0xff, "B", 1, 0x0, None, None),                                                                            
    ('adcl', SEG_SFR_BASE + 0xa7, 0xff, "B", 1, 0x0, None, None),                                                                             
    ('u0baud', SEG_SFR_BASE + 0xa8, 0xff, "B", 1, 0x0, None, None),                                                                           
    ('t3cnt', SEG_SFR_BASE + 0xa9, 0xff, "B", 1, 0x0, None, None),                                                                            
    ('dma1cfgl', SEG_SFR_BASE + 0xaa, 0xff, "B", 1, 0x0, None, None),                                                                         
    ('t1cc0l', SEG_SFR_BASE + 0xab, 0xff, "B", 1, 0x0, None, None),                                                                           
    ('t1cntl', SEG_SFR_BASE + 0xac, 0xff, "B", 1, 0x0, None, None),                                                                           
    ('t4cnt', SEG_SFR_BASE + 0xad, 0xff, "B", 1, 0x0, None, None),                                                                            
    ('adccfg', SEG_SFR_BASE + 0xae, 0xff, "B", 1, 0x0, None, None),                                                                           
    ('u1baud', SEG_SFR_BASE + 0xaf, 0xff, "B", 1, 0x0, None, None),                                                                           
    ('dph0', SEG_SFR_BASE + 0xb0, 0xff, "B", 1, 0x0, None, None),                                                                             
    ('p2ifg', SEG_SFR_BASE + 0xb1, 0xff, "B", 1, 0x0, None, None),                                                                            
    ('mpage', SEG_SFR_BASE + 0xb2, 0xff, "B", 1, 0x0, None, None),                                                                            
    ('s1con', SEG_SFR_BASE + 0xb3, 0xff, "B", 1, 0x0, None, None),                                                                            
    ('t2of2', SEG_SFR_BASE + 0xb4, 0xff, "B", 1, 0x0, None, None),                                                                            
    ('fwt', SEG_SFR_BASE + 0xb5, 0xff, "B", 1, 0x0, None, None),                                                                              
    ('enccs', SEG_SFR_BASE + 0xb6, 0xff, "B", 1, 0x0, None, None),                                                                            
    ('adch', SEG_SFR_BASE + 0xb7, 0xff, "B", 1, 0x0, None, None),                                                                             
    ('t2cnf', SEG_SFR_BASE + 0xb8, 0xff, "B", 1, 0x0, None, None),                                                                            
    ('t3ctl', SEG_SFR_BASE + 0xb9, 0xff, "B", 1, 0x0, None, None),                                                                            
    ('dma1cfgh', SEG_SFR_BASE + 0xba, 0xff, "B", 1, 0x0, None, None),                                                                         
    ('t1cc0h', SEG_SFR_BASE + 0xbb, 0xff, "B", 1, 0x0, None, None),                                                                           
    ('t1cnth', SEG_SFR_BASE + 0xbc, 0xff, "B", 1, 0x0, None, None),                                                                           
    ('t4ctl', SEG_SFR_BASE + 0xbd, 0xff, "B", 1, 0x0, None, None),                                                                            
    ('p0sel', SEG_SFR_BASE + 0xbe, 0xff, "B", 1, 0x0, None, None),                                                                            
    ('u1ucr', SEG_SFR_BASE + 0xbf, 0xff, "B", 1, 0x0, None, None),                                                                            
    ('dpl1', SEG_SFR_BASE + 0xc0, 0xff, "B", 1, 0x0, None, None),                                                                             
    ('pictl', SEG_SFR_BASE + 0xc1, 0xff, "B", 1, 0x0, None, None),                                                                            
    ('t2cmp', SEG_SFR_BASE + 0xc2, 0xff, "B", 1, 0x0, None, None),                                                                            
    ('t2perof0', SEG_SFR_BASE + 0xc3, 0xff, "B", 1, 0x0, None, None),                                                                         
    ('t2caplpl', SEG_SFR_BASE + 0xc4, 0xff, "B", 1, 0x0, None, None),                                                                         
    ('faddrl', SEG_SFR_BASE + 0xc5, 0xff, "B", 1, 0x0, None, None),                                                                           
    ('adccon1', SEG_SFR_BASE + 0xc6, 0xff, "B", 1, 0x0, None, None),                                                                          
    ('rndl', SEG_SFR_BASE + 0xc7, 0xff, "B", 1, 0x0, None, None),                                                                             
    ('u0ucr', SEG_SFR_BASE + 0xc8, 0xff, "B", 1, 0x0, None, None),                                                                            
    ('t3cctl0', SEG_SFR_BASE + 0xc9, 0xff, "B", 1, 0x0, None, None),                                                                          
    ('dma0cfgl', SEG_SFR_BASE + 0xca, 0xff, "B", 1, 0x0, None, None),                                                                         
    ('t1cc1l', SEG_SFR_BASE + 0xcb, 0xff, "B", 1, 0x0, None, None),                                                                           
    ('t1ctl', SEG_SFR_BASE + 0xcc, 0xff, "B", 1, 0x0, None, None),                                                                            
    ('t4cctl0', SEG_SFR_BASE + 0xcd, 0xff, "B", 1, 0x0, None, None),                                                                          
    ('p1sel', SEG_SFR_BASE + 0xce, 0xff, "B", 1, 0x0, None, None),
    ('u1gcr', SEG_SFR_BASE + 0xcf, 0xff, "B", 1, 0x0, None, None),
    ('dph1', SEG_SFR_BASE + 0xd0, 0xff, "B", 1, 0x0, None, None),
    ('p1ien', SEG_SFR_BASE + 0xd1, 0xff, "B", 1, 0x0, None, None),
    ('st0', SEG_SFR_BASE + 0xd2, 0xff, "B", 1, 0x0, None, None),
    ('t2perof1', SEG_SFR_BASE + 0xd3, 0xff, "B", 1, 0x0, None, None),
    ('t2caphph', SEG_SFR_BASE + 0xd4, 0xff, "B", 1, 0x0, None, None),
    ('faddrh', SEG_SFR_BASE + 0xd5, 0xff, "B", 1, 0x0, None, None),
    ('adccon2', SEG_SFR_BASE + 0xd6, 0xff, "B", 1, 0x0, None, None),
    ('rndh', SEG_SFR_BASE + 0xd7, 0xff, "B", 1, 0x0, None, None),
    ('u0gcr', SEG_SFR_BASE + 0xd8, 0xff, "B", 1, 0x0, None, None),
    ('t3cc0', SEG_SFR_BASE + 0xd9, 0xff, "B", 1, 0x0, None, None),
    ('dma0cfgh', SEG_SFR_BASE + 0xda, 0xff, "B", 1, 0x0, None, None),
    ('t1cc1h', SEG_SFR_BASE + 0xdb, 0xff, "B", 1, 0x0, None, None),
    ('t1cctl0', SEG_SFR_BASE + 0xdc, 0xff, "B", 1, 0x0, None, None),
    ('t4cc0', SEG_SFR_BASE + 0xdd, 0xff, "B", 1, 0x0, None, None),
    ('p2sel', SEG_SFR_BASE + 0xde, 0xff, "B", 1, 0x0, None, None),
    ('p0dir', SEG_SFR_BASE + 0xdf, 0xff, "B", 1, 0x0, None, None),
    ('u0csr', SEG_SFR_BASE + 0xe0, 0xff, "B", 1, 0x0, None, None),
    ('-', SEG_SFR_BASE + 0xe1, 0xff, "B", 1, 0x0, None, None),
    ('st1', SEG_SFR_BASE + 0xe2, 0xff, "B", 1, 0x0, None, None),
    ('t2perof2', SEG_SFR_BASE + 0xe3, 0xff, "B", 1, 0x0, None, None),
    ('t2tld', SEG_SFR_BASE + 0xe4, 0xff, "B", 1, 0x0, None, None),
    ('fctl', SEG_SFR_BASE + 0xe5, 0xff, "B", 1, 0x0, None, None),
    ('adccon3', SEG_SFR_BASE + 0xe6, 0xff, "B", 1, 0x0, None, None),
    ('sleep', SEG_SFR_BASE + 0xe7, 0xff, "B", 1, 0x0, None, None),
    ('clkcon', SEG_SFR_BASE + 0xe8, 0xff, "B", 1, 0x0, None, None),
    ('t3cctl1', SEG_SFR_BASE + 0xe9, 0xff, "B", 1, 0x0, None, None),
    ('dmaarm', SEG_SFR_BASE + 0xea, 0xff, "B", 1, 0x0, None, None),
    ('t1cc2l', SEG_SFR_BASE + 0xeb, 0xff, "B", 1, 0x0, None, None),
    ('t1cctl1', SEG_SFR_BASE + 0xec, 0xff, "B", 1, 0x0, None, None),
    ('t4cctl1', SEG_SFR_BASE + 0xed, 0xff, "B", 1, 0x0, None, None),
    ('p1inp', SEG_SFR_BASE + 0xee, 0xff, "B", 1, 0x0, None, None),
    ('p1dir', SEG_SFR_BASE + 0xef, 0xff, "B", 1, 0x0, None, None),
    ('pcon', SEG_SFR_BASE + 0xf0, 0xff, "B", 1, 0x0, None, None),
    ('p0inp', SEG_SFR_BASE + 0xf1, 0xff, "B", 1, 0x0, None, None),
    ('st2', SEG_SFR_BASE + 0xf2, 0xff, "B", 1, 0x0, None, None),
    ('fmap', SEG_SFR_BASE + 0xf3, 0xff, "B", 1, 0x0, None, None),
    ('t2thd', SEG_SFR_BASE + 0xf4, 0xff, "B", 1, 0x0, None, None),
    ('fwdata', SEG_SFR_BASE + 0xf5, 0xff, "B", 1, 0x0, None, None),
    ('-', SEG_SFR_BASE + 0xf6, 0xff, "B", 1, 0x0, None, None),
    ('-', SEG_SFR_BASE + 0xf7, 0xff, "B", 1, 0x0, None, None),
    ('memctr', SEG_SFR_BASE + 0xf8, 0xff, "B", 1, 0x0, None, None),
    ('t3cc1', SEG_SFR_BASE + 0xf9, 0xff, "B", 1, 0x0, None, None),
    ('dmareq', SEG_SFR_BASE + 0xfa, 0xff, "B", 1, 0x0, None, None),
    ('t1cc2h', SEG_SFR_BASE + 0xfb, 0xff, "B", 1, 0x0, None, None),
    ('t1cctl2', SEG_SFR_BASE + 0xfc, 0xff, "B", 1, 0x0, None, None),
    ('t4cc1', SEG_SFR_BASE + 0xfd, 0xff, "B", 1, 0x0, None, None),
    ('p2inp', SEG_SFR_BASE + 0xfe, 0xff, "B", 1, 0x0, None, None),
    ('p2dir', SEG_SFR_BASE + 0xff, 0xff, "B", 1, 0x0, None, None),
    ('pc', SEG_IRAM_BASE + 0x100, 0xffff, ">H", 2, 0x0, None, None),# CHEAT: PC is the only register that doesn't play like this.  FIXME: Make internal!?  That would suck and be inelegant... but possibly faster
    ('dptr', (SEG_SFR_BASE + 0xa0, SEG_SFR_BASE + 0xb0), 0xff, ">H", 1, 0x0, handlerSplitRegisterWrite, handlerSplitRegisterRead),
    ('dptr1', (SEG_SFR_BASE + 0xc0, SEG_SFR_BASE + 0xd0), 0xffff, ">H", 1, 0x0, handlerSplitRegisterWrite, handlerSplitRegisterRead),
    )
    
reg_table = reg_table_chipcon

REG_PC = len(reg_table_chipcon)-3
REG_SP = 0x10
REG_BP = None
REG_DPTR = len(reg_table_chipcon)-2		# separated! 0xa0 0xb0
REG_DPTR1 = len(reg_table_chipcon)-1		# separated! 0xc0 0xd0
REG_PSW = 0xa
REG_FLAGS = 0xa    #same location, backward-compat name
#REG_PDATA = 0x42		# nonexistent in this platform
REG_A = 0xc
REG_B = 0xe

reg_hash = {}
Mcs51regs = []
Mcs51meta = [  #("dpl", REG_DPTR, 0, 8),
                #("dph", REG_DPTR, 8, 8),
                #("dpl1", REG_DPTR1, 0, 8),
                #("dph1", REG_DPTR1, 8, 8),
                ("CV", REG_FLAGS, 7, 1),
                ("AC", REG_FLAGS, 6, 1),
                ("F0", REG_FLAGS, 5, 1),
                ("RS1", REG_FLAGS, 4, 1),
                ("RS0", REG_FLAGS, 3, 1),
                ("OV", REG_FLAGS, 2, 1),
                ("UserDefFlag", REG_FLAGS, 1, 1),
                ("P", REG_FLAGS, 0, 1),
                ]

for x in range(4):
    for y in range(8):
        row = reg_table_chipcon[(x*8)+y]
        rname,rloc,rmask,rfmt,rsz,rinit,intW,intR = row
        reg = "rb%dr%d"%(x,y)
        reg_hash[rname] = row
        reg_hash[rloc] = (reg, row[1:],)
        #print (reg, row[1:],)
        # Mcs51regs for use with envi's RegisterContext
        Mcs51regs.append((rname,1<<(8*rsz)))

for x in reg_table_chipcon[32:]:
    rname,rloc,rmask,rfmt,rsz,rinit,intW,intR = x
    reg_hash[rname] = x
    reg_hash[rloc] = x
    # Mcs51regs for use with envi's RegisterContext
    Mcs51regs.append((rname,1<<(8*rsz)))


class Mcs51RegisterContext(e_reg.RegisterContext):
    def __init__(self):
        e_reg.RegisterContext.__init__(self)
        self.loadRegDef(Mcs51regs)
        self.loadRegMetas(Mcs51meta)
        self.setRegisterIndexes(REG_PC, REG_SP)

rctx = Mcs51RegisterContext()
