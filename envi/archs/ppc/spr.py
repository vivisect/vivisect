sprs = {
    # The capitalization of these register names are inconsistent to match what 
    # GDB expects.
    1: ("xer", " Integer exception register.", 32),
    8: ("lr", " Link register", 64),
    9: ("ctr", " Count register", 64),

    22: ("DEC", " Decrementer", 32),
    26: ("SRR0", " Save/restore register 0", 64),
    27: ("SRR1", "Save/restore register 1", 32),
    48: ("PID", "Process ID register2 ", 32),
    54: ("DECAR", "Decrementer auto-reload", 32),
    56: ("LPER", "Logical page exception register", 64),
    57: ("LPERU", "Logical page exception register upper", 32),
    58: ("CSRR0", "Critical save/restore register 0", 64),
    59: ("CSRR1", "Critical save/restore register 1", 32),
    61: ("DEAR", "Data exception address register", 64),
    62: ("ESR", " Exception syndrome register", 32),
    63: ("IVPR", "Interrupt vector prefix register", 64),

    # also VRSAVE
    256: ("USPRG0", "SPR general 0", 64),

    # User accessible Read-Only aliases for SPRs 273-279 (except for USPRG0)
    257: ("USPRG1", "SPR general 1", 64),
    258: ("USPRG2", "SPR general 2", 64),
    259: ("USPRG3", "SPR general 3", 64),
    260: ("USPRG4", "SPR general 4", 64),
    261: ("USPRG5", "SPR general 5", 64),
    262: ("USPRG6", "SPR general 6", 64),
    263: ("USPRG7", "SPR general 7", 64),

    # The TB (TBL) and TBU SPRs are "Read Only" metaregisters to read the
    # current tick count of the system.  On 64-bit platforms the TB register can
    # be used to read the full timebase value, on 32-bit systems both the TBL
    # and TBU registers must be read to get the full timebase value.  The TBU
    # always returns just 32 bits.
    #
    # In the PpcAbstractEmulator class the i_mfspr() emulation function just
    # returns the static value in the timebase registers.  For more accurate
    # emulation the addSprReadHandler() function should be used to install a
    # function that accurately emulates time elapsing.
    268: ("TB", "(TBL) Time base (time base lower) - read port to Time", 64),

    # FIXME: meta register for TB
    269: ("TBU", "Time base upper - read port to high-order 32-bits", 32),

    # Supervisor/Hypervisor modifiable general purpose SPRs
    272: ("SPRG0", "SPR general 0", 64),
    273: ("SPRG1", "SPR general 1", 64),
    274: ("SPRG2", "SPR general 2", 64),
    275: ("SPRG3", "SPR general 3", 64),
    276: ("SPRG4", "SPR general 4", 64),
    277: ("SPRG5", "SPR general 5", 64),
    278: ("SPRG6", "SPR general 6", 64),
    279: ("SPRG7", "SPR general 7", 64),

    # FIXME: alias
    283: ("CIR", "Chip identification register (alias to SVR for", 32),

    # SPRs 284/285 are "Write Only" metaregisters to allow modifying the current
    # system timebase (number of ticks that have elapsed since the system
    # started). Note that both of these alias registers are 32-bits (in contrast
    # with the read-only TB register)
    284: ("TBL_WO", "Time base lower - write port to low-order 32 bits", 32),
    285: ("TBU_WO", "Time base upper - write port to high-order 32 bits ", 32),

    286: ("PIR", " Processor ID register ", 32),
    287: ("PVR", " Processor version register ", 32),
    304: ("DBSR", " Debug status register2 ", 32),
    306: ("DBSRWR", " Debug status register write2 ", 32),
    307: ("EPCR", " Embedded processor control  register2 ", 32),
    308: ("DBCR0", " Debug control register 02 ", 32),
    309: ("DBCR1", " Debug control register  12 ", 32),
    310: ("DBCR2", " Debug control register  22 ", 32),
    311: ("MSRP", " MSR  protect2 ", 32),
    312: ("IAC1", " Instruction address compare 1, table3-2 ", 64),
    313: ("IAC2", " Instruction address compare  2", 64),
    314: ("IAC3", " Instruction address compare  3", 64),
    315: ("IAC4", " Instruction address compare  4", 64),
    316: ("DAC1", " Data address compare 12 ", 64),
    317: ("DAC2", " Data address compare  22 ", 64),
    318: ("DVC1", " Data value compare 1 ", 64),
    319: ("DVC2", " Data value compare  22 ", 64),
    336: ("TSR", " Timer status register ", 32),
    338: ("LPIDR", " Logical PID register2 ", 32),

    # Hypervisor register
    339: ("MAS5", " MMU assist register  52  (alias to same physical ", 32),

    340: ("TCR", " Timer control register ", 32),

    # Hypervisor registers
    341: ("MAS8", " MMU assist register  82 ", 32),
    342: ("LRATCFG", " LRAT configuration register ", 32),
    343: ("LRATPS", " LRAT page size register ", 32),
    344: ("TLB0PS", " TLB 0 page size register ", 32),
    345: ("TLB1PS", " TLB 1 page size register ", 32),
    346: ("TLB2PS", " TLB 2 page size register ", 32),
    347: ("TLB3PS", " TLB 3 page size register ", 32),

    # FIXME: These are 64-bit metaregisters for existing MAS registers
    348: ("MAS5_MAS6", " MMU assist register 5 and MMU assist register ", 64),
    349: ("MAS8_MAS1", " MMU assist register 8 and MMU assist register ", 64),

    # MMUv2 register (not implemented)
    350: ("EPTCFG", " Embedded page table configuration register ", 32),

    # (hypervisor) Guest/Supervisor modifiable aliases for SPRs 272-279.
    368: ("GSPRG0", " Guest SPR general 0 ", 64),
    369: ("GSPRG1", " Guest SPR general 1 ", 64),
    370: ("GSPRG2", " Guest SPR general 2 ", 64),
    371: ("GSPRG3", " Guest SPR general 3 ", 64),

    # FIXME: These are 64-bit metaregisters for existing MAS registers
    # MAS7 is a hypervisor-only register
    372: ("MAS7_MAS3", " MMU assist register 7 and MMU assist register ", 64),
    373: ("MAS0_MAS1", " MMU assist register 0 and MMU assist register ", 64),

    # hypervisor registers
    378: ("GSRR0", " Guest save/restore register 0 ", 64),
    379: ("GSRR1", " Guest save/restore register 1 ", 32),
    380: ("GEPR", " Guest external proxy register ", 32),
    381: ("GDEAR", " Guest data exception address register ", 64),
    382: ("GPIR", " Guest processor ID register ", 32),
    383: ("GESR", " Guest exception syndrome register ", 32),

    400: ("IVOR0", " Critical input interrupt offset ", 32),
    401: ("IVOR1", " Machine check interrupt offset ", 32),
    402: ("IVOR2", " Data storage interrupt offset ", 32),
    403: ("IVOR3", " Instruction storage interrupt offset ", 32),
    404: ("IVOR4", " External input interrupt offset ", 32),
    405: ("IVOR5", " Alignment interrupt offset ", 32),
    406: ("IVOR6", " Program interrupt offset ", 32),
    407: ("IVOR7", " Floating-point unavailable interrupt offset. ", 32),
    408: ("IVOR8", " System call interrupt offset ", 32),
    409: ("IVOR9", " APU unavailable interrupt offset ", 32),
    410: ("IVOR10", " Decrementer interrupt offset ", 32),
    411: ("IVOR11", " Fixed-interval timer interrupt offset ", 32),
    412: ("IVOR12", " Watchdog timer interrupt offset ", 32),
    413: ("IVOR13", " Data TLB error interrupt offset ", 32),
    414: ("IVOR14", " Instruction TLB error interrupt offset ", 32),
    415: ("IVOR15", " Debug interrupt offset ", 32),
    432: ("IVOR38", " Guest processor doorbell interrupt offset ", 32),
    433: ("IVOR39", " Guest processor doorbell critical and machine ", 32),
    434: ("IVOR40", " Hypervisor system call interrupt offset ", 32),
    435: ("IVOR41", " Hypervisor privilege interrupt offset ", 32),
    436: ("IVOR42", " LRAT error interrupt offset ", 32),
    437: ("TENSR", " Thread enable status register ", 64),
    438: ("TENS", " Thread enable set ", 64),
    439: ("TENC", " Thread enable clear ", 64),

    # hypervisor registers
    440: ("GIVOR2", " Guest data storage interrupt offset ", 32),
    441: ("GIVOR3", " Guest instruction storage interrupt offset ", 32),
    442: ("GIVOR4", " Guest external input interrupt offset ", 32),
    443: ("GIVOR8", " Guest system call interrupt offset ", 32),
    444: ("GIVOR13", " Guest data TLB error interrupt offset ", 32),
    445: ("GIVOR14", " Guest Instruction TLB error interrupt offset ", 32),

    446: ("TIR", " Thread identification register ", 32),

    # hypervisor registers
    447: ("GIVPR", " Guest interrupt vector prefix ", 64),
    464: ("GIVOR35", " Guest performance monitor interrupt offset ", 32),

    # SPE feature
    512: ("spefscr", " SPE floating point status and control register ", 32),
    515: ("L1CFG0", " L1 cache configuration register 0 ", 32),
    516: ("L1CFG1", " L1 cache configuration register 1 ", 32),
    517: ("NPIDR5", " Nexus processor ID register ", 32),
    519: ("L2CFG0", " L2 cache configuration register 0 ", 32),

    # FIXME: alias
    526: ("ATBL", " Alternate time base register lower (alias to same ", 64),
    527: ("ATBU", " Alternate time base register upper (alias to same ", 32),

    528: ("IVOR32", " SPE/Embedded floating point/AltiVec ", 32),
    529: ("IVOR33", " SPE/Embedded floating point/AltiVec ", 32),
    530: ("IVOR34", " Embedded floating point data exception/AltiVec ", 32),
    531: ("IVOR35", " Performance monitor interrupt offset ", 32),
    532: ("IVOR36", " Processor doorbell interrupt offset ", 32),
    533: ("IVOR37", " Processor doorbell critical interrupt offset ", 32),
    561: ("DBCR3", " Debug control register 3 ", 32),
    562: ("DBCNT", " Debug Counter Register ", 32),
    563: ("DBCR4", " Debug control register 4 ", 32),
    564: ("DBCR5", " Debug control register 5 ", 32),
    569: ("DBERC0", " External Debugger Resource Control 0 (alias to ", 32),
    569: ("MCARU", "Machine check address register upper (alias to", 32),
    570: ("MCSRR0", "Machine-check save/restore register 0", 64),
    571: ("MCSRR1", "Machine-check save/restore register 1", 32),
    572: ("MCSR", "Machine check syndrome register", 32),
    573: ("MCAR", "Machine check address register (upper 32-bits", 64),
    574: ("DSRR0", "Debug save/restore register 0", 64),
    575: ("DSRR1", "Debug save/restore register 1", 32),
    576: ("DDAM", "Debug data acquisition message", 32),

    # FIXME: alias
    601: ("DVC1U", "Alias to high order 32 bits of DVC1 register. (alias", 32),
    602: ("DVC2U", "Alias to high order 32 bits of DVC2 register. (alias", 32),

    603: ("DBCR6", " Debug control register 6 ", 32),

    # Hypervisor
    604: ("SPRG8", "SPRG8", 64),
    605: ("SPRG9", "SPRG9", 64),

    606: ("L1CSR2", "2 L1 cache control and status register 2", 32),
    607: ("L1CSR3", "2 L1 cache control and status register 3", 32),
    624: ("MAS0", "MMU assist register 02 (alias to same physical", 32),
    625: ("MAS1", "MMU assist register 12 (alias to same physical", 32),
    626: ("MAS2", "MMU assist register 22", 64),
    627: ("MAS3", "MMU assist register  32  (alias to same physical", 32),
    628: ("MAS4", "MMU assist register 42", 32),
    630: ("MAS6", "MMU assist register  62  (alias to same physical", 32),
    633: ("PID1", "Process ID Register 1 (phased out)2 ", 32),
    634: ("PID2", "Process ID Register 2 (phased  out)2",  32),

    # FIXME: alias
    637: ("MCARUA", "Machine Check Address Register Upper Alias", 32),

    638: ("EDBRAC0", "External Debug Resource Allocation Control 0", 32),
    688: ("TLB0CFG", " TLB configuration register 0 ", 32),
    689: ("TLB1CFG", " TLB configuration register 1 ", 32),
    690: ("TLB2CFG", " TLB configuration register 2 ", 32),
    691: ("TLB3CFG", " TLB configuration register 3 ", 32),

    # hypervisor
    696: ("CDCSR0", " Core device control and status register2 ", 32),

    700: ("DBRR0", " Debug Resource Request Register 0 ", 32),
    702: ("EPR", " External proxy register ", 32),
    720: ("L2ERRINTEN", " L2 cache error interrupt enable ", 32),
    721: ("L2ERRATTR", " L2 cache error attribute ", 32),
    722: ("L2ERRADDR", " L2 cache error address ", 32),
    723: ("L2ERREADDR", " L2 cache error extended address ", 32),
    724: ("L2ERRCTL", " L2 cache error control ", 32),
    725: ("L2ERRDIS", " L2 cache error disable ", 32),

    # hypervisor
    730: ("EPIDR", " External proxy interrupt data register ", 32),
    731: ("INTLEVEL", " External proxy interrupt priority level register ", 32),
    732: ("GEPIDR", " Guest external proxy interrupt data register ", 32),
    732: ("GINTLEVEL", " Guest external proxy interrupt priority level ", 31),

    # Thread maangement (EM)
    898: ("PPR32", " Processor priority register. PRI field is aliased to ", 32),

    # Hypervisor register (64-bit only)
    944: ("MAS7", " MMU assist register 72 (same physical register ", 32),

    # External PID Registerse (E.PD)
    947: ("EPLC", " External PID load context", 32),
    948: ("EPSC", " External PID store context2 ", 32),

    959: ("L1FINV1", " L1 cache flush and invalidate register 1 ", 32),
    975: ("DEVENT", " Debug event ", 32),
    983: ("NSPD", " Nexus SPR access data ", 32),
    984: ("NSPC", " Nexus SPR access configuration ", 32),
    985: ("L2ERRINJHI", " L2 cache error injection mask high ", 32),
    986: ("L2ERRINJLO", " L2 cache error injection mask low ", 32),
    987: ("L2ERRINJCTL", " L2 cache error injection control ", 32),
    988: ("L2CAPTDATAHI", "L2 cache error capture data high ", 32),
    989: ("L2CAPTDATALO", "L2 cache error capture data low ", 32),
    990: ("L2CAPTECC", " L2 cache error capture ECC syndrome ", 32),
    991: ("L2ERRDET", " L2 cache error detect ", 32),
    1008: ("HID0", " Hardware implementation dependent register 02 ", 32),
    1009: ("HID1", " Hardware implementation dependent register 12 ", 32),
    1010: ("L1CSR0", " L1 cache control and status register 0", 32),
    1011: ("L1CSR1", " L1 cache control and status register 1", 32),
    1012: ("MMUCSR0", " MMU control and status register 02 ", 32),
    1013: ("BUCSR", " Branch unit control and status register 2 ", 32),
    1015: ("MMUCFG", " MMU configuration register ", 32),
    1016: ("L1FINV0", " L1 cache flush and invalidate register 0 ", 32),
    1017: ("L2CSR0", " L2 cache control and status register 0", 32),
    1018: ("L2CSR1", " L2 cache control and status register 1", 32),
    1019: ("PWRMGTCR0", "Power management control register 0", 32),
    1022: ("SCCSRBAR", "Shifted CCSRBAR from SoC", 32),
    1023: ("SVR", " System version register", 32),
}
