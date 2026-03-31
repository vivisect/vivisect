"""
ARM64 System Register Definitions - COMPLETE
Based on ARMv8 Architecture Reference Manual and Linux kernel arch/arm64
"""

system_registers = [
    # ================================================================
    # IDENTIFICATION REGISTERS (op0=3, op1=0)
    # ================================================================
    ("MIDR_EL1", 3, 0, 0, 0, 0, "Main ID Register"),
    ("CTR_EL0", 3, 3, 0, 0, 1, "Cache Type Register"),
    ("DCZID_EL0", 3, 3, 0, 0, 7, "Data Cache Zero ID Register"),
    
    # Cache identification registers (op1=1 for read-only cache info)
    ("CCSIDR_EL1", 3, 1, 0, 0, 0, "Cache Size ID Register"),
    ("CLIDR_EL1", 3, 1, 0, 0, 1, "Cache Level ID Register"),
    ("CCSIDR2_EL1", 3, 1, 0, 0, 2, "Cache Size ID Register 2"),
    ("AIDR_EL1", 3, 1, 0, 0, 7, "Auxiliary ID Register"),
    
    # Cache selection register (op1=2 for write to select cache level)
    ("CSSELR_EL1", 3, 2, 0, 0, 0, "Cache Size Selection Register"),
    
    ("VPIDR_EL2", 3, 4, 0, 0, 0, "Virtualization Processor ID Register"),
    ("VMPIDR_EL2", 3, 4, 0, 0, 5, "Virtualization Multiprocessor ID Register"),
    ("MPIDR_EL1", 3, 0, 0, 0, 5, "Multiprocessor Affinity Register"),
    ("REVIDR_EL1", 3, 0, 0, 0, 6, "Revision ID Register"),
    
    # Feature ID Registers (op0=3, op1=0)
    ("ID_AA64PFR0_EL1", 3, 0, 0, 4, 0, "AArch64 Processor Feature Register 0"),
    ("ID_AA64PFR1_EL1", 3, 0, 0, 4, 1, "AArch64 Processor Feature Register 1"),
    ("ID_AA64ZFR0_EL1", 3, 0, 0, 4, 4, "SVE Feature ID Register 0"),
    ("ID_AA64SMFR0_EL1", 3, 0, 0, 4, 5, "SME Feature ID Register 0"),
    ("ID_AA64DFR0_EL1", 3, 0, 0, 5, 0, "AArch64 Debug Feature Register 0"),
    ("ID_AA64DFR1_EL1", 3, 0, 0, 5, 1, "AArch64 Debug Feature Register 1"),
    ("ID_AA64AFR0_EL1", 3, 0, 0, 5, 4, "AArch64 Auxiliary Feature Register 0"),
    ("ID_AA64AFR1_EL1", 3, 0, 0, 5, 5, "AArch64 Auxiliary Feature Register 1"),
    ("ID_AA64ISAR0_EL1", 3, 0, 0, 6, 0, "AArch64 Instruction Set Attribute Register 0"),
    ("ID_AA64ISAR1_EL1", 3, 0, 0, 6, 1, "AArch64 Instruction Set Attribute Register 1"),
    ("ID_AA64ISAR2_EL1", 3, 0, 0, 6, 2, "AArch64 Instruction Set Attribute Register 2"),
    ("ID_AA64MMFR0_EL1", 3, 0, 0, 7, 0, "AArch64 Memory Model Feature Register 0"),
    ("ID_AA64MMFR1_EL1", 3, 0, 0, 7, 1, "AArch64 Memory Model Feature Register 1"),
    ("ID_AA64MMFR2_EL1", 3, 0, 0, 7, 2, "AArch64 Memory Model Feature Register 2"),
    
    # ================================================================
    # SYSTEM CONTROL REGISTERS
    # ================================================================
    ("SCTLR_EL1", 3, 0, 1, 0, 0, "System Control Register (EL1)"),
    ("SCTLR_EL2", 3, 4, 1, 0, 0, "System Control Register (EL2)"),
    ("SCTLR_EL3", 3, 6, 1, 0, 0, "System Control Register (EL3)"),
    ("SCTLR_EL12", 3, 5, 1, 0, 0, "System Control Register (EL1 at EL2)"),
    
    ("ACTLR_EL1", 3, 0, 1, 0, 1, "Auxiliary Control Register (EL1)"),
    ("ACTLR_EL2", 3, 4, 1, 0, 1, "Auxiliary Control Register (EL2)"),
    ("ACTLR_EL3", 3, 6, 1, 0, 1, "Auxiliary Control Register (EL3)"),
    
    ("CPACR_EL1", 3, 0, 1, 0, 2, "Architectural Feature Access Control Register"),
    ("CPACR_EL12", 3, 5, 1, 0, 2, "Architectural Feature Access Control Register (EL1 at EL2)"),
    ("CPTR_EL2", 3, 4, 1, 1, 2, "Architectural Feature Trap Register (EL2)"),
    ("CPTR_EL3", 3, 6, 1, 1, 2, "Architectural Feature Trap Register (EL3)"),
    
    ("HCR_EL2", 3, 4, 1, 1, 0, "Hypervisor Configuration Register"),
    ("SCR_EL3", 3, 6, 1, 1, 0, "Secure Configuration Register"),
    ("MDCR_EL2", 3, 4, 1, 1, 1, "Monitor Debug Configuration Register (EL2)"),
    ("MDCR_EL3", 3, 6, 1, 3, 1, "Monitor Debug Configuration Register (EL3)"),
    ("HSTR_EL2", 3, 4, 1, 1, 3, "Hypervisor System Trap Register"),
    ("HACR_EL2", 3, 4, 1, 1, 7, "Hypervisor Auxiliary Control Register"),
    ("HCRX_EL2", 3, 4, 1, 2, 2, "Extended Hypervisor Configuration Register"),
    ("SDER32_EL2", 3, 4, 1, 3, 1, "AArch32 Secure Debug Enable Register"),
    #("SDER32_EL3", 3, 6, 1, 1, 1, "AArch32 Secure Debug Enable Register (EL3)"),
    
    # ================================================================
    # TRANSLATION TABLE BASE REGISTERS
    # ================================================================
    ("TTBR0_EL1", 3, 0, 2, 0, 0, "Translation Table Base Register 0 (EL1)"),
    ("TTBR1_EL1", 3, 0, 2, 0, 1, "Translation Table Base Register 1 (EL1)"),
    ("TTBR0_EL2", 3, 4, 2, 0, 0, "Translation Table Base Register 0 (EL2)"),
    ("TTBR1_EL2", 3, 4, 2, 0, 1, "Translation Table Base Register 1 (EL2)"),
    ("TTBR0_EL3", 3, 6, 2, 0, 0, "Translation Table Base Register 0 (EL3)"),
    ("TTBR0_EL12", 3, 5, 2, 0, 0, "Translation Table Base Register 0 (EL1 at EL2)"),
    ("TTBR1_EL12", 3, 5, 2, 0, 1, "Translation Table Base Register 1 (EL1 at EL2)"),
    
    ("VTTBR_EL2", 3, 4, 2, 1, 0, "Virtualization Translation Table Base Register"),
    ("VSTTBR_EL2", 3, 4, 2, 6, 0, "Virtualization Secure Translation Table Base Register"),
    ("VNCR_EL2", 3, 4, 2, 2, 0, "Virtual Nested Control Register"),
    
    # Translation Control Registers
    ("TCR_EL1", 3, 0, 2, 0, 2, "Translation Control Register (EL1)"),
    ("TCR_EL2", 3, 4, 2, 0, 2, "Translation Control Register (EL2)"),
    ("TCR_EL3", 3, 6, 2, 0, 2, "Translation Control Register (EL3)"),
    ("TCR_EL12", 3, 5, 2, 0, 2, "Translation Control Register (EL1 at EL2)"),
    ("VTCR_EL2", 3, 4, 2, 1, 2, "Virtualization Translation Control Register"),
    ("VSTCR_EL2", 3, 4, 2, 6, 2, "Virtualization Secure Translation Control Register"),
    
    # ================================================================
    # MEMORY ATTRIBUTE REGISTERS
    # ================================================================
    ("MAIR_EL1", 3, 0, 10, 2, 0, "Memory Attribute Indirection Register (EL1)"),
    ("MAIR_EL2", 3, 4, 10, 2, 0, "Memory Attribute Indirection Register (EL2)"),
    ("MAIR_EL3", 3, 6, 10, 2, 0, "Memory Attribute Indirection Register (EL3)"),
    ("MAIR_EL12", 3, 5, 10, 2, 0, "Memory Attribute Indirection Register (EL1 at EL2)"),
    
    ("AMAIR_EL1", 3, 0, 10, 3, 0, "Auxiliary Memory Attribute Indirection Register (EL1)"),
    ("AMAIR_EL2", 3, 4, 10, 3, 0, "Auxiliary Memory Attribute Indirection Register (EL2)"),
    ("AMAIR_EL3", 3, 6, 10, 3, 0, "Auxiliary Memory Attribute Indirection Register (EL3)"),
    ("AMAIR_EL12", 3, 5, 10, 3, 0, "Auxiliary Memory Attribute Indirection Register (EL1 at EL2)"),
    
    # AArch32 compatibility
    ("DACR32_EL2", 3, 4, 3, 0, 0, "Domain Access Control Register (AArch32)"),
    
    # ================================================================
    # EXCEPTION HANDLING REGISTERS
    # ================================================================
    # Vector Base Address Registers
    ("VBAR_EL1", 3, 0, 12, 0, 0, "Vector Base Address Register (EL1)"),
    ("VBAR_EL2", 3, 4, 12, 0, 0, "Vector Base Address Register (EL2)"),
    ("VBAR_EL3", 3, 6, 12, 0, 0, "Vector Base Address Register (EL3)"),
    ("VBAR_EL12", 3, 5, 12, 0, 0, "Vector Base Address Register (EL1 at EL2)"),
    
    ("RVBAR_EL1", 3, 0, 12, 0, 1, "Reset Vector Base Address Register (EL1)"),
    ("RVBAR_EL2", 3, 4, 12, 0, 1, "Reset Vector Base Address Register (EL2)"),
    ("RVBAR_EL3", 3, 6, 12, 0, 1, "Reset Vector Base Address Register (EL3)"),
    
    ("RMR_EL1", 3, 0, 12, 0, 2, "Reset Management Register (EL1)"),
    ("RMR_EL2", 3, 4, 12, 0, 2, "Reset Management Register (EL2)"),
    ("RMR_EL3", 3, 6, 12, 0, 2, "Reset Management Register (EL3)"),
    
    # Exception Syndrome Registers
    ("ESR_EL1", 3, 0, 5, 2, 0, "Exception Syndrome Register (EL1)"),
    ("ESR_EL2", 3, 4, 5, 2, 0, "Exception Syndrome Register (EL2)"),
    ("ESR_EL3", 3, 6, 5, 2, 0, "Exception Syndrome Register (EL3)"),
    ("ESR_EL12", 3, 5, 5, 2, 0, "Exception Syndrome Register (EL1 at EL2)"),
    
    ("VSESR_EL2", 3, 4, 5, 2, 3, "Virtual SError Exception Syndrome Register"),
    ("DISR_EL1", 3, 0, 12, 1, 1, "Deferred Interrupt Status Register"),
    ("VDISR_EL2", 3, 4, 12, 1, 1, "Virtual Deferred Interrupt Status Register"),
    
    # Fault Address Registers
    ("FAR_EL1", 3, 0, 6, 0, 0, "Fault Address Register (EL1)"),
    ("FAR_EL2", 3, 4, 6, 0, 0, "Fault Address Register (EL2)"),
    ("FAR_EL3", 3, 6, 6, 0, 0, "Fault Address Register (EL3)"),
    ("FAR_EL12", 3, 5, 6, 0, 0, "Fault Address Register (EL1 at EL2)"),
    ("HPFAR_EL2", 3, 4, 6, 0, 4, "Hypervisor IPA Fault Address Register"),
    
    # Auxiliary Fault Status Registers
    ("AFSR0_EL1", 3, 0, 5, 1, 0, "Auxiliary Fault Status Register 0 (EL1)"),
    ("AFSR1_EL1", 3, 0, 5, 1, 1, "Auxiliary Fault Status Register 1 (EL1)"),
    ("AFSR0_EL2", 3, 4, 5, 1, 0, "Auxiliary Fault Status Register 0 (EL2)"),
    ("AFSR1_EL2", 3, 4, 5, 1, 1, "Auxiliary Fault Status Register 1 (EL2)"),
    ("AFSR0_EL3", 3, 6, 5, 1, 0, "Auxiliary Fault Status Register 0 (EL3)"),
    ("AFSR1_EL3", 3, 6, 5, 1, 1, "Auxiliary Fault Status Register 1 (EL3)"),
    ("AFSR0_EL12", 3, 5, 5, 1, 0, "Auxiliary Fault Status Register 0 (EL1 at EL2)"),
    ("AFSR1_EL12", 3, 5, 5, 1, 1, "Auxiliary Fault Status Register 1 (EL1 at EL2)"),
    
    # AArch32 Fault Status
    ("IFSR32_EL2", 3, 4, 5, 0, 1, "Instruction Fault Status Register (AArch32)"),
    
    # Exception Link Registers
    ("ELR_EL1", 3, 0, 4, 0, 1, "Exception Link Register (EL1)"),
    ("ELR_EL2", 3, 4, 4, 0, 1, "Exception Link Register (EL2)"),
    ("ELR_EL3", 3, 6, 4, 0, 1, "Exception Link Register (EL3)"),
    ("ELR_EL12", 3, 5, 4, 0, 1, "Exception Link Register (EL1 at EL2)"),
    
    # Saved Program Status Registers
    ("SPSR_EL1", 3, 0, 4, 0, 0, "Saved Program Status Register (EL1)"),
    ("SPSR_EL2", 3, 4, 4, 0, 0, "Saved Program Status Register (EL2)"),
    ("SPSR_EL3", 3, 6, 4, 0, 0, "Saved Program Status Register (EL3)"),
    ("SPSR_EL12", 3, 5, 4, 0, 0, "Saved Program Status Register (EL1 at EL2)"),
    ("SPSR_irq", 3, 4, 4, 3, 0, "Saved Program Status Register (IRQ)"),
    ("SPSR_abt", 3, 4, 4, 3, 1, "Saved Program Status Register (Abort)"),
    ("SPSR_und", 3, 4, 4, 3, 2, "Saved Program Status Register (Undefined)"),
    ("SPSR_fiq", 3, 4, 4, 3, 3, "Saved Program Status Register (FIQ)"),
    
    # ================================================================
    # PSTATE ACCESS (op0=3, op1=3 or op1=0)
    # ================================================================
    ("CurrentEL", 3, 0, 4, 2, 2, "Current Exception Level"),
    ("SPSel", 3, 0, 4, 2, 0, "Stack Pointer Select"),
    ("NZCV", 3, 3, 4, 2, 0, "Condition Flags"),
    ("DAIF", 3, 3, 4, 2, 1, "Interrupt Mask Bits"),
    ("PAN", 3, 0, 4, 2, 3, "Privileged Access Never"),
    ("UAO", 3, 0, 4, 2, 4, "User Access Override"),
    ("DIT", 3, 3, 4, 2, 5, "Data Independent Timing"),
    ("SSBS", 3, 3, 4, 2, 6, "Speculative Store Bypass Safe"),
    ("TCO", 3, 3, 4, 2, 7, "Tag Check Override"),
    
    # Stack Pointer access
    ("SP_EL0", 3, 0, 4, 1, 0, "Stack Pointer (EL0)"),
    ("SP_EL1", 3, 4, 4, 1, 0, "Stack Pointer (EL1)"),
    ("SP_EL2", 3, 6, 4, 1, 0, "Stack Pointer (EL2)"),
    
    # EL0 debug state
    ("DLR_EL0", 3, 3, 4, 5, 1, "Debug Link Register"),
    ("DSPSR_EL0", 3, 3, 4, 5, 0, "Debug Saved Program Status Register"),

    # ================================================================
    # DEBUG DATA TRANSFER REGISTERS (EL0 access - op0=3, op1=3)
    # ================================================================
    ("DBGDTR_EL0", 3, 3, 0, 4, 0, "Debug Data Transfer Register"),
    ("DBGDTRRX_EL0", 3, 3, 0, 5, 0, "Debug Data Transfer Register, Receive"),
    ("DBGDTRTX_EL0", 3, 3, 0, 5, 0, "Debug Data Transfer Register, Transmit"),
    
    # Floating-point Control/Status
    ("FPCR", 3, 3, 4, 4, 0, "Floating-point Control Register"),
    ("FPSR", 3, 3, 4, 4, 1, "Floating-point Status Register"),
    
    # AArch32 FP compatibility
    ("FPEXC32_EL2", 3, 4, 5, 3, 0, "Floating-Point Exception Control Register (AArch32)"),
    
    # ================================================================
    # CONTEXT AND THREAD ID REGISTERS
    # ================================================================
    ("CONTEXTIDR_EL1", 3, 0, 13, 0, 1, "Context ID Register (EL1)"),
    ("CONTEXTIDR_EL2", 3, 4, 13, 0, 1, "Context ID Register (EL2)"),
    ("CONTEXTIDR_EL12", 3, 5, 13, 0, 1, "Context ID Register (EL1 at EL2)"),
    
    ("TPIDR_EL0", 3, 3, 13, 0, 2, "Thread ID Register (EL0)"),
    ("TPIDRRO_EL0", 3, 3, 13, 0, 3, "Thread ID Register Read-Only (EL0)"),
    ("TPIDR_EL1", 3, 0, 13, 0, 4, "Thread ID Register (EL1)"),
    ("TPIDR_EL2", 3, 4, 13, 0, 2, "Thread ID Register (EL2)"),
    ("TPIDR_EL3", 3, 6, 13, 0, 2, "Thread ID Register (EL3)"),
    ("TPIDR2_EL0", 3, 3, 13, 0, 5, "Thread ID Register 2 (EL0)"),
    
    ("SCXTNUM_EL0", 3, 3, 13, 0, 7, "EL0 Read/Write Software Context Number"),
    ("SCXTNUM_EL1", 3, 0, 13, 0, 7, "EL1 Read/Write Software Context Number"),
    ("SCXTNUM_EL2", 3, 4, 13, 0, 7, "EL2 Read/Write Software Context Number"),
    ("SCXTNUM_EL3", 3, 6, 13, 0, 7, "EL3 Read/Write Software Context Number"),
    ("SCXTNUM_EL12", 3, 5, 13, 0, 7, "EL1 Read/Write Software Context Number (EL2)"),
    
    # ================================================================
    # GENERIC TIMER REGISTERS (op0=3, op1=3 for EL0 access)
    # ================================================================
    ("CNTFRQ_EL0", 3, 3, 14, 0, 0, "Counter-timer Frequency Register"),
    ("CNTPCT_EL0", 3, 3, 14, 0, 1, "Counter-timer Physical Count Register"),
    ("CNTVCT_EL0", 3, 3, 14, 0, 2, "Counter-timer Virtual Count Register"),
    
    ("CNTP_TVAL_EL0", 3, 3, 14, 2, 0, "Counter-timer Physical Timer TimerValue"),
    ("CNTP_CTL_EL0", 3, 3, 14, 2, 1, "Counter-timer Physical Timer Control"),
    ("CNTP_CVAL_EL0", 3, 3, 14, 2, 2, "Counter-timer Physical Timer CompareValue"),
    ("CNTP_TVAL_EL02", 3, 5, 14, 2, 0, "Counter-timer Physical Timer TimerValue (EL02)"),
    ("CNTP_CTL_EL02", 3, 5, 14, 2, 1, "Counter-timer Physical Timer Control (EL02)"),
    ("CNTP_CVAL_EL02", 3, 5, 14, 2, 2, "Counter-timer Physical Timer CompareValue (EL02)"),
    
    ("CNTV_TVAL_EL0", 3, 3, 14, 3, 0, "Counter-timer Virtual Timer TimerValue"),
    ("CNTV_CTL_EL0", 3, 3, 14, 3, 1, "Counter-timer Virtual Timer Control"),
    ("CNTV_CVAL_EL0", 3, 3, 14, 3, 2, "Counter-timer Virtual Timer CompareValue"),
    ("CNTV_TVAL_EL02", 3, 5, 14, 3, 0, "Counter-timer Virtual Timer TimerValue (EL02)"),
    ("CNTV_CTL_EL02", 3, 5, 14, 3, 1, "Counter-timer Virtual Timer Control (EL02)"),
    ("CNTV_CVAL_EL02", 3, 5, 14, 3, 2, "Counter-timer Virtual Timer CompareValue (EL02)"),
    
    ("CNTVOFF_EL2", 3, 4, 14, 0, 3, "Counter-timer Virtual Offset"),
    ("CNTPOFF_EL2", 3, 4, 14, 0, 6, "Counter-timer Physical Offset"),
    
    ("CNTHCTL_EL2", 3, 4, 14, 1, 0, "Counter-timer Hypervisor Control Register"),
    ("CNTKCTL_EL1", 3, 0, 14, 1, 0, "Counter-timer Kernel Control Register"),
    ("CNTKCTL_EL12", 3, 5, 14, 1, 0, "Counter-timer Kernel Control Register (EL12)"),
    
    ("CNTHP_TVAL_EL2", 3, 4, 14, 2, 0, "Counter-timer Hypervisor Physical Timer TimerValue"),
    ("CNTHP_CTL_EL2", 3, 4, 14, 2, 1, "Counter-timer Hypervisor Physical Timer Control"),
    ("CNTHP_CVAL_EL2", 3, 4, 14, 2, 2, "Counter-timer Hypervisor Physical Timer CompareValue"),
    
    ("CNTHV_TVAL_EL2", 3, 4, 14, 3, 0, "Counter-timer Virtual Timer TimerValue (EL2)"),
    ("CNTHV_CTL_EL2", 3, 4, 14, 3, 1, "Counter-timer Virtual Timer Control (EL2)"),
    ("CNTHV_CVAL_EL2", 3, 4, 14, 3, 2, "Counter-timer Virtual Timer CompareValue (EL2)"),
    
    ("CNTHVS_TVAL_EL2", 3, 4, 14, 4, 0, "Counter-timer Secure Virtual Timer TimerValue (EL2)"),
    ("CNTHVS_CTL_EL2", 3, 4, 14, 4, 1, "Counter-timer Secure Virtual Timer Control (EL2)"),
    ("CNTHVS_CVAL_EL2", 3, 4, 14, 4, 2, "Counter-timer Secure Virtual Timer CompareValue (EL2)"),
    
    ("CNTHPS_TVAL_EL2", 3, 4, 14, 5, 0, "Counter-timer Secure Physical Timer TimerValue (EL2)"),
    ("CNTHPS_CTL_EL2", 3, 4, 14, 5, 1, "Counter-timer Secure Physical Timer Control (EL2)"),
    ("CNTHPS_CVAL_EL2", 3, 4, 14, 5, 2, "Counter-timer Secure Physical Timer CompareValue (EL2)"),
    
    ("CNTPS_TVAL_EL1", 3, 7, 14, 2, 0, "Counter-timer Physical Secure Timer TimerValue"),
    ("CNTPS_CTL_EL1", 3, 7, 14, 2, 1, "Counter-timer Physical Secure Timer Control"),
    ("CNTPS_CVAL_EL1", 3, 7, 14, 2, 2, "Counter-timer Physical Secure Timer CompareValue"),
    
    # ================================================================
    # PERFORMANCE MONITORS (op0=3, op1=3 for EL0, op1=0 for EL1)
    # ================================================================
    ("PMCR_EL0", 3, 3, 9, 12, 0, "Performance Monitors Control Register"),
    ("PMCNTENSET_EL0", 3, 3, 9, 12, 1, "Performance Monitors Count Enable Set"),
    ("PMCNTENCLR_EL0", 3, 3, 9, 12, 2, "Performance Monitors Count Enable Clear"),
    ("PMOVSCLR_EL0", 3, 3, 9, 12, 3, "Performance Monitors Overflow Flag Status Clear"),
    ("PMSWINC_EL0", 3, 3, 9, 12, 4, "Performance Monitors Software Increment"),
    ("PMSELR_EL0", 3, 3, 9, 12, 5, "Performance Monitors Event Counter Selection"),
    ("PMCEID0_EL0", 3, 3, 9, 12, 6, "Performance Monitors Common Event ID 0"),
    ("PMCEID1_EL0", 3, 3, 9, 12, 7, "Performance Monitors Common Event ID 1"),
    ("PMCCNTR_EL0", 3, 3, 9, 13, 0, "Performance Monitors Cycle Count Register"),
    ("PMXEVTYPER_EL0", 3, 3, 9, 13, 1, "Performance Monitors Selected Event Type"),
    ("PMXEVCNTR_EL0", 3, 3, 9, 13, 2, "Performance Monitors Selected Event Count"),
    ("PMUSERENR_EL0", 3, 3, 9, 14, 0, "Performance Monitors User Enable Register"),
    ("PMINTENSET_EL1", 3, 0, 9, 14, 1, "Performance Monitors Interrupt Enable Set"),
    ("PMINTENCLR_EL1", 3, 0, 9, 14, 2, "Performance Monitors Interrupt Enable Clear"),
    ("PMOVSSET_EL0", 3, 3, 9, 14, 3, "Performance Monitors Overflow Flag Status Set"),
    ("PMMIR_EL1", 3, 0, 9, 14, 6, "Performance Monitors Machine Identification Register"),
    
    # Performance Monitor Event Counter Registers (0-30)
    ("PMEVCNTR0_EL0", 3, 3, 14, 8, 0, "Performance Monitors Event Counter 0"),
    ("PMEVCNTR1_EL0", 3, 3, 14, 8, 1, "Performance Monitors Event Counter 1"),
    ("PMEVCNTR2_EL0", 3, 3, 14, 8, 2, "Performance Monitors Event Counter 2"),
    ("PMEVCNTR3_EL0", 3, 3, 14, 8, 3, "Performance Monitors Event Counter 3"),
    ("PMEVCNTR4_EL0", 3, 3, 14, 8, 4, "Performance Monitors Event Counter 4"),
    ("PMEVCNTR5_EL0", 3, 3, 14, 8, 5, "Performance Monitors Event Counter 5"),
    ("PMEVCNTR6_EL0", 3, 3, 14, 8, 6, "Performance Monitors Event Counter 6"),
    ("PMEVCNTR7_EL0", 3, 3, 14, 8, 7, "Performance Monitors Event Counter 7"),
    ("PMEVCNTR8_EL0", 3, 3, 14, 9, 0, "Performance Monitors Event Counter 8"),
    ("PMEVCNTR9_EL0", 3, 3, 14, 9, 1, "Performance Monitors Event Counter 9"),
    ("PMEVCNTR10_EL0", 3, 3, 14, 9, 2, "Performance Monitors Event Counter 10"),
    ("PMEVCNTR11_EL0", 3, 3, 14, 9, 3, "Performance Monitors Event Counter 11"),
    ("PMEVCNTR12_EL0", 3, 3, 14, 9, 4, "Performance Monitors Event Counter 12"),
    ("PMEVCNTR13_EL0", 3, 3, 14, 9, 5, "Performance Monitors Event Counter 13"),
    ("PMEVCNTR14_EL0", 3, 3, 14, 9, 6, "Performance Monitors Event Counter 14"),
    ("PMEVCNTR15_EL0", 3, 3, 14, 9, 7, "Performance Monitors Event Counter 15"),
    ("PMEVCNTR16_EL0", 3, 3, 14, 10, 0, "Performance Monitors Event Counter 16"),
    ("PMEVCNTR17_EL0", 3, 3, 14, 10, 1, "Performance Monitors Event Counter 17"),
    ("PMEVCNTR18_EL0", 3, 3, 14, 10, 2, "Performance Monitors Event Counter 18"),
    ("PMEVCNTR19_EL0", 3, 3, 14, 10, 3, "Performance Monitors Event Counter 19"),
    ("PMEVCNTR20_EL0", 3, 3, 14, 10, 4, "Performance Monitors Event Counter 20"),
    ("PMEVCNTR21_EL0", 3, 3, 14, 10, 5, "Performance Monitors Event Counter 21"),
    ("PMEVCNTR22_EL0", 3, 3, 14, 10, 6, "Performance Monitors Event Counter 22"),
    ("PMEVCNTR23_EL0", 3, 3, 14, 10, 7, "Performance Monitors Event Counter 23"),
    ("PMEVCNTR24_EL0", 3, 3, 14, 11, 0, "Performance Monitors Event Counter 24"),
    ("PMEVCNTR25_EL0", 3, 3, 14, 11, 1, "Performance Monitors Event Counter 25"),
    ("PMEVCNTR26_EL0", 3, 3, 14, 11, 2, "Performance Monitors Event Counter 26"),
    ("PMEVCNTR27_EL0", 3, 3, 14, 11, 3, "Performance Monitors Event Counter 27"),
    ("PMEVCNTR28_EL0", 3, 3, 14, 11, 4, "Performance Monitors Event Counter 28"),
    ("PMEVCNTR29_EL0", 3, 3, 14, 11, 5, "Performance Monitors Event Counter 29"),
    ("PMEVCNTR30_EL0", 3, 3, 14, 11, 6, "Performance Monitors Event Counter 30"),
    
    # Performance Monitor Event Type Registers (0-30)
    ("PMEVTYPER0_EL0", 3, 3, 14, 12, 0, "Performance Monitors Event Type 0"),
    ("PMEVTYPER1_EL0", 3, 3, 14, 12, 1, "Performance Monitors Event Type 1"),
    ("PMEVTYPER2_EL0", 3, 3, 14, 12, 2, "Performance Monitors Event Type 2"),
    ("PMEVTYPER3_EL0", 3, 3, 14, 12, 3, "Performance Monitors Event Type 3"),
    ("PMEVTYPER4_EL0", 3, 3, 14, 12, 4, "Performance Monitors Event Type 4"),
    ("PMEVTYPER5_EL0", 3, 3, 14, 12, 5, "Performance Monitors Event Type 5"),
    ("PMEVTYPER6_EL0", 3, 3, 14, 12, 6, "Performance Monitors Event Type 6"),
    ("PMEVTYPER7_EL0", 3, 3, 14, 12, 7, "Performance Monitors Event Type 7"),
    ("PMEVTYPER8_EL0", 3, 3, 14, 13, 0, "Performance Monitors Event Type 8"),
    ("PMEVTYPER9_EL0", 3, 3, 14, 13, 1, "Performance Monitors Event Type 9"),
    ("PMEVTYPER10_EL0", 3, 3, 14, 13, 2, "Performance Monitors Event Type 10"),
    ("PMEVTYPER11_EL0", 3, 3, 14, 13, 3, "Performance Monitors Event Type 11"),
    ("PMEVTYPER12_EL0", 3, 3, 14, 13, 4, "Performance Monitors Event Type 12"),
    ("PMEVTYPER13_EL0", 3, 3, 14, 13, 5, "Performance Monitors Event Type 13"),
    ("PMEVTYPER14_EL0", 3, 3, 14, 13, 6, "Performance Monitors Event Type 14"),
    ("PMEVTYPER15_EL0", 3, 3, 14, 13, 7, "Performance Monitors Event Type 15"),
    ("PMEVTYPER16_EL0", 3, 3, 14, 14, 0, "Performance Monitors Event Type 16"),
    ("PMEVTYPER17_EL0", 3, 3, 14, 14, 1, "Performance Monitors Event Type 17"),
    ("PMEVTYPER18_EL0", 3, 3, 14, 14, 2, "Performance Monitors Event Type 18"),
    ("PMEVTYPER19_EL0", 3, 3, 14, 14, 3, "Performance Monitors Event Type 19"),
    ("PMEVTYPER20_EL0", 3, 3, 14, 14, 4, "Performance Monitors Event Type 20"),
    ("PMEVTYPER21_EL0", 3, 3, 14, 14, 5, "Performance Monitors Event Type 21"),
    ("PMEVTYPER22_EL0", 3, 3, 14, 14, 6, "Performance Monitors Event Type 22"),
    ("PMEVTYPER23_EL0", 3, 3, 14, 14, 7, "Performance Monitors Event Type 23"),
    ("PMEVTYPER24_EL0", 3, 3, 14, 15, 0, "Performance Monitors Event Type 24"),
    ("PMEVTYPER25_EL0", 3, 3, 14, 15, 1, "Performance Monitors Event Type 25"),
    ("PMEVTYPER26_EL0", 3, 3, 14, 15, 2, "Performance Monitors Event Type 26"),
    ("PMEVTYPER27_EL0", 3, 3, 14, 15, 3, "Performance Monitors Event Type 27"),
    ("PMEVTYPER28_EL0", 3, 3, 14, 15, 4, "Performance Monitors Event Type 28"),
    ("PMEVTYPER29_EL0", 3, 3, 14, 15, 5, "Performance Monitors Event Type 29"),
    ("PMEVTYPER30_EL0", 3, 3, 14, 15, 6, "Performance Monitors Event Type 30"),
    
    # Cycle counter filter
    ("PMCCFILTR_EL0", 3, 3, 14, 15, 7, "Performance Monitors Cycle Count Filter"),
    
    # ================================================================
    # ADDRESS TRANSLATION
    # ================================================================
    ("PAR_EL1", 3, 0, 7, 4, 0, "Physical Address Register"),
    
    # ================================================================
    # POINTER AUTHENTICATION KEYS
    # ================================================================
    ("APIAKeyLo_EL1", 3, 0, 2, 1, 0, "Pointer Authentication Key A for Instruction (Lo)"),
    ("APIAKeyHi_EL1", 3, 0, 2, 1, 1, "Pointer Authentication Key A for Instruction (Hi)"),
    ("APIBKeyLo_EL1", 3, 0, 2, 1, 2, "Pointer Authentication Key B for Instruction (Lo)"),
    ("APIBKeyHi_EL1", 3, 0, 2, 1, 3, "Pointer Authentication Key B for Instruction (Hi)"),
    ("APDAKeyLo_EL1", 3, 0, 2, 2, 0, "Pointer Authentication Key A for Data (Lo)"),
    ("APDAKeyHi_EL1", 3, 0, 2, 2, 1, "Pointer Authentication Key A for Data (Hi)"),
    ("APDBKeyLo_EL1", 3, 0, 2, 2, 2, "Pointer Authentication Key B for Data (Lo)"),
    ("APDBKeyHi_EL1", 3, 0, 2, 2, 3, "Pointer Authentication Key B for Data (Hi)"),
    ("APGAKeyLo_EL1", 3, 0, 2, 3, 0, "Pointer Authentication Generic Key (Lo)"),
    ("APGAKeyHi_EL1", 3, 0, 2, 3, 1, "Pointer Authentication Generic Key (Hi)"),
    
    # ================================================================
    # RANDOM NUMBER GENERATION
    # ================================================================
    ("RNDR", 3, 3, 2, 4, 0, "Random Number"),
    ("RNDRRS", 3, 3, 2, 4, 1, "Reseeded Random Number"),
    
    # ================================================================
    # MEMORY TAGGING EXTENSION (MTE)
    # ================================================================
    ("TFSR_EL1", 3, 0, 5, 6, 0, "Tag Fault Status Register (EL1)"),
    ("TFSR_EL2", 3, 4, 5, 6, 0, "Tag Fault Status Register (EL2)"),
    ("TFSR_EL3", 3, 6, 5, 6, 0, "Tag Fault Status Register (EL3)"),
    ("TFSR_EL12", 3, 5, 5, 6, 0, "Tag Fault Status Register (EL12)"),
    ("TFSRE0_EL1", 3, 0, 5, 6, 1, "Tag Fault Status Register (EL0)"),
    ("RGSR_EL1", 3, 0, 1, 0, 5, "Random Allocation Tag Seed Register"),
    ("GCR_EL1", 3, 0, 1, 0, 6, "Tag Control Register"),
    
    # ================================================================
    # SVE CONTROL
    # ================================================================
    ("ZCR_EL1", 3, 0, 1, 2, 0, "SVE Control Register (EL1)"),
    ("ZCR_EL2", 3, 4, 1, 2, 0, "SVE Control Register (EL2)"),
    ("ZCR_EL3", 3, 6, 1, 2, 0, "SVE Control Register (EL3)"),
    ("ZCR_EL12", 3, 5, 1, 2, 0, "SVE Control Register (EL12)"),
    
    # ================================================================
    # SME CONTROL
    # ================================================================
    ("SMCR_EL1", 3, 0, 1, 2, 6, "SME Control Register (EL1)"),
    ("SMCR_EL2", 3, 4, 1, 2, 6, "SME Control Register (EL2)"),
    ("SMCR_EL3", 3, 6, 1, 2, 6, "SME Control Register (EL3)"),
    ("SMCR_EL12", 3, 5, 1, 2, 6, "SME Control Register (EL12)"),
    ("SVCR", 3, 3, 4, 2, 2, "Streaming Vector Control Register"),
    ("SMPRI_EL1", 3, 0, 1, 2, 4, "Streaming Mode Priority Register"),
    ("SMPRIMAP_EL2", 3, 4, 1, 2, 5, "Streaming Mode Priority Mapping Register"),
    
    # ================================================================
    # DEBUG REGISTERS (op0=2) 
    # ================================================================
    ("MDCCINT_EL1", 2, 0, 0, 2, 0, "Monitor Debug Comms Channel Interrupt Enable"),
    ("MDSCR_EL1", 2, 0, 0, 2, 2, "Monitor Debug System Control Register"),
    ("MDRAR_EL1", 2, 0, 1, 0, 0, "Monitor Debug ROM Address Register"),
    
    # OS Lock registers
    ("OSLAR_EL1", 2, 0, 1, 0, 4, "OS Lock Access Register"),
    ("OSLSR_EL1", 2, 0, 1, 1, 4, "OS Lock Status Register"),
    ("OSDLR_EL1", 2, 0, 1, 3, 4, "OS Double Lock Register"),
    
    # Debug data transfer registers
    ("OSDTRRX_EL1", 2, 0, 0, 0, 2, "OS Lock Data Transfer Register, Receive"),
    ("OSDTRTX_EL1", 2, 0, 0, 3, 2, "OS Lock Data Transfer Register, Transmit"),
    ("OSECCR_EL1", 2, 0, 0, 6, 2, "OS Lock Exception Catch Control Register"),
    
    # Debug control
    ("DBGPRCR_EL1", 2, 0, 1, 4, 4, "Debug Power Control Register"),
    ("DBGCLAIMSET_EL1", 2, 0, 7, 8, 6, "Debug Claim Tag Set Register"),
    ("DBGCLAIMCLR_EL1", 2, 0, 7, 9, 6, "Debug Claim Tag Clear Register"),
    ("DBGAUTHSTATUS_EL1", 2, 0, 7, 14, 6, "Debug Authentication Status Register"),
    
    # Debug Breakpoint Value Registers (op0=2)
    ("DBGBVR0_EL1", 2, 0, 0, 0, 4, "Debug Breakpoint Value Register 0"),
    ("DBGBVR1_EL1", 2, 0, 0, 1, 4, "Debug Breakpoint Value Register 1"),
    ("DBGBVR2_EL1", 2, 0, 0, 2, 4, "Debug Breakpoint Value Register 2"),
    ("DBGBVR3_EL1", 2, 0, 0, 3, 4, "Debug Breakpoint Value Register 3"),
    ("DBGBVR4_EL1", 2, 0, 0, 4, 4, "Debug Breakpoint Value Register 4"),
    ("DBGBVR5_EL1", 2, 0, 0, 5, 4, "Debug Breakpoint Value Register 5"),
    ("DBGBVR6_EL1", 2, 0, 0, 6, 4, "Debug Breakpoint Value Register 6"),
    ("DBGBVR7_EL1", 2, 0, 0, 7, 4, "Debug Breakpoint Value Register 7"),
    ("DBGBVR8_EL1", 2, 0, 0, 8, 4, "Debug Breakpoint Value Register 8"),
    ("DBGBVR9_EL1", 2, 0, 0, 9, 4, "Debug Breakpoint Value Register 9"),
    ("DBGBVR10_EL1", 2, 0, 0, 10, 4, "Debug Breakpoint Value Register 10"),
    ("DBGBVR11_EL1", 2, 0, 0, 11, 4, "Debug Breakpoint Value Register 11"),
    ("DBGBVR12_EL1", 2, 0, 0, 12, 4, "Debug Breakpoint Value Register 12"),
    ("DBGBVR13_EL1", 2, 0, 0, 13, 4, "Debug Breakpoint Value Register 13"),
    ("DBGBVR14_EL1", 2, 0, 0, 14, 4, "Debug Breakpoint Value Register 14"),
    ("DBGBVR15_EL1", 2, 0, 0, 15, 4, "Debug Breakpoint Value Register 15"),
    
    # Debug Breakpoint Control Registers (op0=2)
    ("DBGBCR0_EL1", 2, 0, 0, 0, 5, "Debug Breakpoint Control Register 0"),
    ("DBGBCR1_EL1", 2, 0, 0, 1, 5, "Debug Breakpoint Control Register 1"),
    ("DBGBCR2_EL1", 2, 0, 0, 2, 5, "Debug Breakpoint Control Register 2"),
    ("DBGBCR3_EL1", 2, 0, 0, 3, 5, "Debug Breakpoint Control Register 3"),
    ("DBGBCR4_EL1", 2, 0, 0, 4, 5, "Debug Breakpoint Control Register 4"),
    ("DBGBCR5_EL1", 2, 0, 0, 5, 5, "Debug Breakpoint Control Register 5"),
    ("DBGBCR6_EL1", 2, 0, 0, 6, 5, "Debug Breakpoint Control Register 6"),
    ("DBGBCR7_EL1", 2, 0, 0, 7, 5, "Debug Breakpoint Control Register 7"),
    ("DBGBCR8_EL1", 2, 0, 0, 8, 5, "Debug Breakpoint Control Register 8"),
    ("DBGBCR9_EL1", 2, 0, 0, 9, 5, "Debug Breakpoint Control Register 9"),
    ("DBGBCR10_EL1", 2, 0, 0, 10, 5, "Debug Breakpoint Control Register 10"),
    ("DBGBCR11_EL1", 2, 0, 0, 11, 5, "Debug Breakpoint Control Register 11"),
    ("DBGBCR12_EL1", 2, 0, 0, 12, 5, "Debug Breakpoint Control Register 12"),
    ("DBGBCR13_EL1", 2, 0, 0, 13, 5, "Debug Breakpoint Control Register 13"),
    ("DBGBCR14_EL1", 2, 0, 0, 14, 5, "Debug Breakpoint Control Register 14"),
    ("DBGBCR15_EL1", 2, 0, 0, 15, 5, "Debug Breakpoint Control Register 15"),
    
    # Debug Watchpoint Value Registers (op0=2)
    ("DBGWVR0_EL1", 2, 0, 0, 0, 6, "Debug Watchpoint Value Register 0"),
    ("DBGWVR1_EL1", 2, 0, 0, 1, 6, "Debug Watchpoint Value Register 1"),
    ("DBGWVR2_EL1", 2, 0, 0, 2, 6, "Debug Watchpoint Value Register 2"),
    ("DBGWVR3_EL1", 2, 0, 0, 3, 6, "Debug Watchpoint Value Register 3"),
    ("DBGWVR4_EL1", 2, 0, 0, 4, 6, "Debug Watchpoint Value Register 4"),
    ("DBGWVR5_EL1", 2, 0, 0, 5, 6, "Debug Watchpoint Value Register 5"),
    ("DBGWVR6_EL1", 2, 0, 0, 6, 6, "Debug Watchpoint Value Register 6"),
    ("DBGWVR7_EL1", 2, 0, 0, 7, 6, "Debug Watchpoint Value Register 7"),
    ("DBGWVR8_EL1", 2, 0, 0, 8, 6, "Debug Watchpoint Value Register 8"),
    ("DBGWVR9_EL1", 2, 0, 0, 9, 6, "Debug Watchpoint Value Register 9"),
    ("DBGWVR10_EL1", 2, 0, 0, 10, 6, "Debug Watchpoint Value Register 10"),
    ("DBGWVR11_EL1", 2, 0, 0, 11, 6, "Debug Watchpoint Value Register 11"),
    ("DBGWVR12_EL1", 2, 0, 0, 12, 6, "Debug Watchpoint Value Register 12"),
    ("DBGWVR13_EL1", 2, 0, 0, 13, 6, "Debug Watchpoint Value Register 13"),
    ("DBGWVR14_EL1", 2, 0, 0, 14, 6, "Debug Watchpoint Value Register 14"),
    ("DBGWVR15_EL1", 2, 0, 0, 15, 6, "Debug Watchpoint Value Register 15"),
    
    # Debug Watchpoint Control Registers (op0=2)
    ("DBGWCR0_EL1", 2, 0, 0, 0, 7, "Debug Watchpoint Control Register 0"),
    ("DBGWCR1_EL1", 2, 0, 0, 1, 7, "Debug Watchpoint Control Register 1"),
    ("DBGWCR2_EL1", 2, 0, 0, 2, 7, "Debug Watchpoint Control Register 2"),
    ("DBGWCR3_EL1", 2, 0, 0, 3, 7, "Debug Watchpoint Control Register 3"),
    ("DBGWCR4_EL1", 2, 0, 0, 4, 7, "Debug Watchpoint Control Register 4"),
    ("DBGWCR5_EL1", 2, 0, 0, 5, 7, "Debug Watchpoint Control Register 5"),
    ("DBGWCR6_EL1", 2, 0, 0, 6, 7, "Debug Watchpoint Control Register 6"),
    ("DBGWCR7_EL1", 2, 0, 0, 7, 7, "Debug Watchpoint Control Register 7"),
    ("DBGWCR8_EL1", 2, 0, 0, 8, 7, "Debug Watchpoint Control Register 8"),
    ("DBGWCR9_EL1", 2, 0, 0, 9, 7, "Debug Watchpoint Control Register 9"),
    ("DBGWCR10_EL1", 2, 0, 0, 10, 7, "Debug Watchpoint Control Register 10"),
    ("DBGWCR11_EL1", 2, 0, 0, 11, 7, "Debug Watchpoint Control Register 11"),
    ("DBGWCR12_EL1", 2, 0, 0, 12, 7, "Debug Watchpoint Control Register 12"),
    ("DBGWCR13_EL1", 2, 0, 0, 13, 7, "Debug Watchpoint Control Register 13"),
    ("DBGWCR14_EL1", 2, 0, 0, 14, 7, "Debug Watchpoint Control Register 14"),
    ("DBGWCR15_EL1", 2, 0, 0, 15, 7, "Debug Watchpoint Control Register 15"),
    
    # AArch32 debug compatibility
    ("DBGVCR32_EL2", 2, 4, 0, 7, 0, "Debug Vector Catch Register (AArch32)"),
    
    # ================================================================
    # TRACE REGISTERS - ETE/ETM (op0=2, op1=1)
    # Note: These use op0=2, op1=1 for trace unit access
    # ================================================================
    ("TRCTRACEIDR", 2, 1, 0, 0, 1, "Trace ID Register"),
    ("TRCVICTLR", 2, 1, 0, 0, 2, "ViewInst Main Control Register"),
    ("TRCPRGCTLR", 2, 1, 0, 1, 0, "Programming Control Register"),
    ("TRCPROCSELR", 2, 1, 0, 2, 0, "PE Select Control Register"),
    ("TRCSTATR", 2, 1, 0, 3, 0, "Trace Status Register"),
    ("TRCCONFIGR", 2, 1, 0, 4, 0, "Trace Configuration Register"),
    ("TRCAUXCTLR", 2, 1, 0, 6, 0, "Trace Auxiliary Control Register"),
    ("TRCEVENTCTL0R", 2, 1, 0, 8, 0, "Event Control 0 Register"),
    ("TRCEVENTCTL1R", 2, 1, 0, 9, 0, "Event Control 1 Register"),
    ("TRCSTALLCTLR", 2, 1, 0, 11, 0, "Stall Control Register"),
    ("TRCTSCTLR", 2, 1, 0, 12, 0, "Global Timestamp Control Register"),
    ("TRCSYNCPR", 2, 1, 0, 13, 0, "Synchronization Period Register"),
    ("TRCCCCTLR", 2, 1, 0, 14, 0, "Cycle Count Control Register"),
    ("TRCBBCTLR", 2, 1, 0, 15, 0, "Branch Broadcast Control Register"),
    
    # Trace Viewinst
    ("TRCVIIECTLR", 2, 1, 0, 0, 7, "ViewInst Include/Exclude Control Register"),
    ("TRCVISSCTLR", 2, 1, 0, 1, 7, "ViewInst Start/Stop Control Register"),
    ("TRCVIPCSSCTLR", 2, 1, 0, 3, 7, "ViewInst Start/Stop PE Comparator Control"),
    ("TRCVDCTLR", 2, 1, 0, 8, 7, "ViewData Main Control Register"),
    ("TRCVDSACCTLR", 2, 1, 0, 9, 7, "ViewData Include/Exclude Single Address Comparator Control"),
    ("TRCVDARCCTLR", 2, 1, 0, 10, 7, "ViewData Include/Exclude Address Range Comparator Control"),
    
    # Trace Derived Resources
    ("TRCRSCTLR2", 2, 1, 1, 2, 0, "Resource Selection Control Register 2"),
    ("TRCRSCTLR3", 2, 1, 1, 3, 0, "Resource Selection Control Register 3"),
    ("TRCRSCTLR4", 2, 1, 1, 4, 0, "Resource Selection Control Register 4"),
    ("TRCRSCTLR5", 2, 1, 1, 5, 0, "Resource Selection Control Register 5"),
    ("TRCRSCTLR6", 2, 1, 1, 6, 0, "Resource Selection Control Register 6"),
    ("TRCRSCTLR7", 2, 1, 1, 7, 0, "Resource Selection Control Register 7"),
    ("TRCRSCTLR8", 2, 1, 1, 8, 0, "Resource Selection Control Register 8"),
    ("TRCRSCTLR9", 2, 1, 1, 9, 0, "Resource Selection Control Register 9"),
    ("TRCRSCTLR10", 2, 1, 1, 10, 0, "Resource Selection Control Register 10"),
    ("TRCRSCTLR11", 2, 1, 1, 11, 0, "Resource Selection Control Register 11"),
    ("TRCRSCTLR12", 2, 1, 1, 12, 0, "Resource Selection Control Register 12"),
    ("TRCRSCTLR13", 2, 1, 1, 13, 0, "Resource Selection Control Register 13"),
    ("TRCRSCTLR14", 2, 1, 1, 14, 0, "Resource Selection Control Register 14"),
    ("TRCRSCTLR15", 2, 1, 1, 15, 0, "Resource Selection Control Register 15"),
    ("TRCRSCTLR16", 2, 1, 1, 0, 1, "Resource Selection Control Register 16"),
    ("TRCRSCTLR17", 2, 1, 1, 1, 1, "Resource Selection Control Register 17"),
    ("TRCRSCTLR18", 2, 1, 1, 2, 1, "Resource Selection Control Register 18"),
    ("TRCRSCTLR19", 2, 1, 1, 3, 1, "Resource Selection Control Register 19"),
    ("TRCRSCTLR20", 2, 1, 1, 4, 1, "Resource Selection Control Register 20"),
    ("TRCRSCTLR21", 2, 1, 1, 5, 1, "Resource Selection Control Register 21"),
    ("TRCRSCTLR22", 2, 1, 1, 6, 1, "Resource Selection Control Register 22"),
    ("TRCRSCTLR23", 2, 1, 1, 7, 1, "Resource Selection Control Register 23"),
    ("TRCRSCTLR24", 2, 1, 1, 8, 1, "Resource Selection Control Register 24"),
    ("TRCRSCTLR25", 2, 1, 1, 9, 1, "Resource Selection Control Register 25"),
    ("TRCRSCTLR26", 2, 1, 1, 10, 1, "Resource Selection Control Register 26"),
    ("TRCRSCTLR27", 2, 1, 1, 11, 1, "Resource Selection Control Register 27"),
    ("TRCRSCTLR28", 2, 1, 1, 12, 1, "Resource Selection Control Register 28"),
    ("TRCRSCTLR29", 2, 1, 1, 13, 1, "Resource Selection Control Register 29"),
    ("TRCRSCTLR30", 2, 1, 1, 14, 1, "Resource Selection Control Register 30"),
    ("TRCRSCTLR31", 2, 1, 1, 15, 1, "Resource Selection Control Register 31"),
    
    # Trace Single-shot Comparator Control
    ("TRCSSCCR0", 2, 1, 1, 0, 2, "Single-Shot Comparator Control Register 0"),
    ("TRCSSCCR1", 2, 1, 1, 1, 2, "Single-Shot Comparator Control Register 1"),
    ("TRCSSCCR2", 2, 1, 1, 2, 2, "Single-Shot Comparator Control Register 2"),
    ("TRCSSCCR3", 2, 1, 1, 3, 2, "Single-Shot Comparator Control Register 3"),
    ("TRCSSCCR4", 2, 1, 1, 4, 2, "Single-Shot Comparator Control Register 4"),
    ("TRCSSCCR5", 2, 1, 1, 5, 2, "Single-Shot Comparator Control Register 5"),
    ("TRCSSCCR6", 2, 1, 1, 6, 2, "Single-Shot Comparator Control Register 6"),
    ("TRCSSCCR7", 2, 1, 1, 7, 2, "Single-Shot Comparator Control Register 7"),
    
    # Trace Single-shot Status Control
    ("TRCSSCSR0", 2, 1, 1, 8, 2, "Single-Shot Status Control Register 0"),
    ("TRCSSCSR1", 2, 1, 1, 9, 2, "Single-Shot Status Control Register 1"),
    ("TRCSSCSR2", 2, 1, 1, 10, 2, "Single-Shot Status Control Register 2"),
    ("TRCSSCSR3", 2, 1, 1, 11, 2, "Single-Shot Status Control Register 3"),
    ("TRCSSCSR4", 2, 1, 1, 12, 2, "Single-Shot Status Control Register 4"),
    ("TRCSSCSR5", 2, 1, 1, 13, 2, "Single-Shot Status Control Register 5"),
    ("TRCSSCSR6", 2, 1, 1, 14, 2, "Single-Shot Status Control Register 6"),
    ("TRCSSCSR7", 2, 1, 1, 15, 2, "Single-Shot Status Control Register 7"),
    
    # Trace Single-shot PE Comparator Input Control
    ("TRCSSPCICR0", 2, 1, 1, 0, 3, "Single-Shot PE Comparator Input Control Register 0"),
    ("TRCSSPCICR1", 2, 1, 1, 1, 3, "Single-Shot PE Comparator Input Control Register 1"),
    ("TRCSSPCICR2", 2, 1, 1, 2, 3, "Single-Shot PE Comparator Input Control Register 2"),
    ("TRCSSPCICR3", 2, 1, 1, 3, 3, "Single-Shot PE Comparator Input Control Register 3"),
    ("TRCSSPCICR4", 2, 1, 1, 4, 3, "Single-Shot PE Comparator Input Control Register 4"),
    ("TRCSSPCICR5", 2, 1, 1, 5, 3, "Single-Shot PE Comparator Input Control Register 5"),
    ("TRCSSPCICR6", 2, 1, 1, 6, 3, "Single-Shot PE Comparator Input Control Register 6"),
    ("TRCSSPCICR7", 2, 1, 1, 7, 3, "Single-Shot PE Comparator Input Control Register 7"),
    
    # Trace OS Lock
    ("TRCOSLAR", 2, 1, 1, 0, 4, "Trace OS Lock Access Register"),
    ("TRCOSLSR", 2, 1, 1, 1, 4, "Trace OS Lock Status Register"),
    ("TRCPDCR", 2, 1, 1, 4, 4, "Trace Power Down Control Register"),
    ("TRCPDSR", 2, 1, 1, 5, 4, "Trace Power Down Status Register"),
    
    # Trace Sequencer
    ("TRCSEQEVR0", 2, 1, 0, 0, 4, "Trace Sequencer State Transition Event 0"),
    ("TRCSEQEVR1", 2, 1, 0, 1, 4, "Trace Sequencer State Transition Event 1"),
    ("TRCSEQEVR2", 2, 1, 0, 2, 4, "Trace Sequencer State Transition Event 2"),
    ("TRCSEQRSTEVR", 2, 1, 0, 6, 4, "Trace Sequencer Reset Control Event"),
    ("TRCSEQSTR", 2, 1, 0, 7, 4, "Trace Sequencer State Register"),
    
    # Trace External Input Selectors
    ("TRCEXTINSELR", 2, 1, 0, 8, 4, "Trace External Input Select Register 0"),
    ("TRCEXTINSELR1", 2, 1, 0, 9, 4, "Trace External Input Select Register 1"),
    ("TRCEXTINSELR2", 2, 1, 0, 10, 4, "Trace External Input Select Register 2"),
    ("TRCEXTINSELR3", 2, 1, 0, 11, 4, "Trace External Input Select Register 3"),
    
    # Trace Counter Control
    ("TRCCNTCTLR0", 2, 1, 0, 0, 5, "Trace Counter Control Register 0"),
    ("TRCCNTCTLR1", 2, 1, 0, 1, 5, "Trace Counter Control Register 1"),
    ("TRCCNTCTLR2", 2, 1, 0, 2, 5, "Trace Counter Control Register 2"),
    ("TRCCNTCTLR3", 2, 1, 0, 3, 5, "Trace Counter Control Register 3"),
    
    # Trace Counter Reload Value
    ("TRCCNTRLDVR0", 2, 1, 0, 0, 6, "Trace Counter Reload Value Register 0"),
    ("TRCCNTRLDVR1", 2, 1, 0, 1, 6, "Trace Counter Reload Value Register 1"),
    ("TRCCNTRLDVR2", 2, 1, 0, 2, 6, "Trace Counter Reload Value Register 2"),
    ("TRCCNTRLDVR3", 2, 1, 0, 3, 6, "Trace Counter Reload Value Register 3"),
    
    # Trace Counter Value
    ("TRCCNTVR0", 2, 1, 0, 0, 7, "Trace Counter Value Register 0"),
    ("TRCCNTVR1", 2, 1, 0, 1, 7, "Trace Counter Value Register 1"),
    ("TRCCNTVR2", 2, 1, 0, 2, 7, "Trace Counter Value Register 2"),
    ("TRCCNTVR3", 2, 1, 0, 3, 7, "Trace Counter Value Register 3"),
    
    # Trace ID Comparators
    ("TRCIDR8", 2, 1, 0, 0, 6, "Trace ID Register 8"),
    ("TRCIDR9", 2, 1, 0, 1, 6, "Trace ID Register 9"),
    ("TRCIDR10", 2, 1, 0, 2, 6, "Trace ID Register 10"),
    ("TRCIDR11", 2, 1, 0, 3, 6, "Trace ID Register 11"),
    ("TRCIDR12", 2, 1, 0, 4, 6, "Trace ID Register 12"),
    ("TRCIDR13", 2, 1, 0, 5, 6, "Trace ID Register 13"),
    
    # Trace Implementation Defined
    ("TRCIMSPEC0", 2, 1, 0, 0, 7, "Trace Implementation Defined Register 0"),
    ("TRCIMSPEC1", 2, 1, 0, 1, 7, "Trace Implementation Defined Register 1"),
    ("TRCIMSPEC2", 2, 1, 0, 2, 7, "Trace Implementation Defined Register 2"),
    ("TRCIMSPEC3", 2, 1, 0, 3, 7, "Trace Implementation Defined Register 3"),
    ("TRCIMSPEC4", 2, 1, 0, 4, 7, "Trace Implementation Defined Register 4"),
    ("TRCIMSPEC5", 2, 1, 0, 5, 7, "Trace Implementation Defined Register 5"),
    ("TRCIMSPEC6", 2, 1, 0, 6, 7, "Trace Implementation Defined Register 6"),
    ("TRCIMSPEC7", 2, 1, 0, 7, 7, "Trace Implementation Defined Register 7"),
    
    # Trace Address Comparators  
    ("TRCACVR0", 2, 1, 2, 0, 0, "Trace Address Comparator Value Register 0"),
    ("TRCACVR1", 2, 1, 2, 2, 0, "Trace Address Comparator Value Register 1"),
    ("TRCACVR2", 2, 1, 2, 4, 0, "Trace Address Comparator Value Register 2"),
    ("TRCACVR3", 2, 1, 2, 6, 0, "Trace Address Comparator Value Register 3"),
    ("TRCACVR4", 2, 1, 2, 8, 0, "Trace Address Comparator Value Register 4"),
    ("TRCACVR5", 2, 1, 2, 10, 0, "Trace Address Comparator Value Register 5"),
    ("TRCACVR6", 2, 1, 2, 12, 0, "Trace Address Comparator Value Register 6"),
    ("TRCACVR7", 2, 1, 2, 14, 0, "Trace Address Comparator Value Register 7"),
    ("TRCACVR8", 2, 1, 2, 0, 1, "Trace Address Comparator Value Register 8"),
    ("TRCACVR9", 2, 1, 2, 2, 1, "Trace Address Comparator Value Register 9"),
    ("TRCACVR10", 2, 1, 2, 4, 1, "Trace Address Comparator Value Register 10"),
    ("TRCACVR11", 2, 1, 2, 6, 1, "Trace Address Comparator Value Register 11"),
    ("TRCACVR12", 2, 1, 2, 8, 1, "Trace Address Comparator Value Register 12"),
    ("TRCACVR13", 2, 1, 2, 10, 1, "Trace Address Comparator Value Register 13"),
    ("TRCACVR14", 2, 1, 2, 12, 1, "Trace Address Comparator Value Register 14"),
    ("TRCACVR15", 2, 1, 2, 14, 1, "Trace Address Comparator Value Register 15"),
    
    # Trace Address Comparator Access Type
    ("TRCACATR0", 2, 1, 2, 0, 2, "Trace Address Comparator Access Type Register 0"),
    ("TRCACATR1", 2, 1, 2, 2, 2, "Trace Address Comparator Access Type Register 1"),
    ("TRCACATR2", 2, 1, 2, 4, 2, "Trace Address Comparator Access Type Register 2"),
    ("TRCACATR3", 2, 1, 2, 6, 2, "Trace Address Comparator Access Type Register 3"),
    ("TRCACATR4", 2, 1, 2, 8, 2, "Trace Address Comparator Access Type Register 4"),
    ("TRCACATR5", 2, 1, 2, 10, 2, "Trace Address Comparator Access Type Register 5"),
    ("TRCACATR6", 2, 1, 2, 12, 2, "Trace Address Comparator Access Type Register 6"),
    ("TRCACATR7", 2, 1, 2, 14, 2, "Trace Address Comparator Access Type Register 7"),
    ("TRCACATR8", 2, 1, 2, 0, 3, "Trace Address Comparator Access Type Register 8"),
    ("TRCACATR9", 2, 1, 2, 2, 3, "Trace Address Comparator Access Type Register 9"),
    ("TRCACATR10", 2, 1, 2, 4, 3, "Trace Address Comparator Access Type Register 10"),
    ("TRCACATR11", 2, 1, 2, 6, 3, "Trace Address Comparator Access Type Register 11"),
    ("TRCACATR12", 2, 1, 2, 8, 3, "Trace Address Comparator Access Type Register 12"),
    ("TRCACATR13", 2, 1, 2, 10, 3, "Trace Address Comparator Access Type Register 13"),
    ("TRCACATR14", 2, 1, 2, 12, 3, "Trace Address Comparator Access Type Register 14"),
    ("TRCACATR15", 2, 1, 2, 14, 3, "Trace Address Comparator Access Type Register 15"),
    
    # Trace Data Value Comparators
    ("TRCDVCVR0", 2, 1, 2, 0, 4, "Trace Data Value Comparator Value Register 0"),
    ("TRCDVCVR1", 2, 1, 2, 4, 4, "Trace Data Value Comparator Value Register 1"),
    ("TRCDVCVR2", 2, 1, 2, 8, 4, "Trace Data Value Comparator Value Register 2"),
    ("TRCDVCVR3", 2, 1, 2, 12, 4, "Trace Data Value Comparator Value Register 3"),
    ("TRCDVCVR4", 2, 1, 2, 0, 5, "Trace Data Value Comparator Value Register 4"),
    ("TRCDVCVR5", 2, 1, 2, 4, 5, "Trace Data Value Comparator Value Register 5"),
    ("TRCDVCVR6", 2, 1, 2, 8, 5, "Trace Data Value Comparator Value Register 6"),
    ("TRCDVCVR7", 2, 1, 2, 12, 5, "Trace Data Value Comparator Value Register 7"),
    
    # Trace Data Value Comparator Mask
    ("TRCDVCMR0", 2, 1, 2, 0, 6, "Trace Data Value Comparator Mask Register 0"),
    ("TRCDVCMR1", 2, 1, 2, 4, 6, "Trace Data Value Comparator Mask Register 1"),
    ("TRCDVCMR2", 2, 1, 2, 8, 6, "Trace Data Value Comparator Mask Register 2"),
    ("TRCDVCMR3", 2, 1, 2, 12, 6, "Trace Data Value Comparator Mask Register 3"),
    ("TRCDVCMR4", 2, 1, 2, 0, 7, "Trace Data Value Comparator Mask Register 4"),
    ("TRCDVCMR5", 2, 1, 2, 4, 7, "Trace Data Value Comparator Mask Register 5"),
    ("TRCDVCMR6", 2, 1, 2, 8, 7, "Trace Data Value Comparator Mask Register 6"),
    ("TRCDVCMR7", 2, 1, 2, 12, 7, "Trace Data Value Comparator Mask Register 7"),
    
    # Trace Context ID Comparators
    ("TRCCIDCVR0", 2, 1, 3, 0, 0, "Trace Context ID Comparator Value Register 0"),
    ("TRCCIDCVR1", 2, 1, 3, 2, 0, "Trace Context ID Comparator Value Register 1"),
    ("TRCCIDCVR2", 2, 1, 3, 4, 0, "Trace Context ID Comparator Value Register 2"),
    ("TRCCIDCVR3", 2, 1, 3, 6, 0, "Trace Context ID Comparator Value Register 3"),
    ("TRCCIDCVR4", 2, 1, 3, 8, 0, "Trace Context ID Comparator Value Register 4"),
    ("TRCCIDCVR5", 2, 1, 3, 10, 0, "Trace Context ID Comparator Value Register 5"),
    ("TRCCIDCVR6", 2, 1, 3, 12, 0, "Trace Context ID Comparator Value Register 6"),
    ("TRCCIDCVR7", 2, 1, 3, 14, 0, "Trace Context ID Comparator Value Register 7"),
    
    # Trace VMID Comparators
    ("TRCVMIDCVR0", 2, 1, 3, 0, 1, "Trace VMID Comparator Value Register 0"),
    ("TRCVMIDCVR1", 2, 1, 3, 2, 1, "Trace VMID Comparator Value Register 1"),
    ("TRCVMIDCVR2", 2, 1, 3, 4, 1, "Trace VMID Comparator Value Register 2"),
    ("TRCVMIDCVR3", 2, 1, 3, 6, 1, "Trace VMID Comparator Value Register 3"),
    ("TRCVMIDCVR4", 2, 1, 3, 8, 1, "Trace VMID Comparator Value Register 4"),
    ("TRCVMIDCVR5", 2, 1, 3, 10, 1, "Trace VMID Comparator Value Register 5"),
    ("TRCVMIDCVR6", 2, 1, 3, 12, 1, "Trace VMID Comparator Value Register 6"),
    ("TRCVMIDCVR7", 2, 1, 3, 14, 1, "Trace VMID Comparator Value Register 7"),
    
    # Trace Context ID/VMID Comparator Control
    ("TRCCIDCCTLR0", 2, 1, 3, 0, 2, "Trace Context ID Comparator Control Register 0"),
    ("TRCCIDCCTLR1", 2, 1, 3, 1, 2, "Trace Context ID Comparator Control Register 1"),
    ("TRCVMIDCCTLR0", 2, 1, 3, 2, 2, "Trace VMID Comparator Control Register 0"),
    ("TRCVMIDCCTLR1", 2, 1, 3, 3, 2, "Trace VMID Comparator Control Register 1"),
    
    # Trace Integration and Test registers
    ("TRCITCTRL", 2, 1, 7, 0, 4, "Trace Integration Mode Control Register"),
    ("TRCCLAIMSET", 2, 1, 7, 8, 6, "Trace Claim Tag Set Register"),
    ("TRCCLAIMCLR", 2, 1, 7, 9, 6, "Trace Claim Tag Clear Register"),
    ("TRCDEVAFF0", 2, 1, 7, 10, 6, "Trace Device Affinity Register 0"),
    ("TRCDEVAFF1", 2, 1, 7, 11, 6, "Trace Device Affinity Register 1"),
    ("TRCLAR", 2, 1, 7, 12, 6, "Trace Software Lock Access Register"),
    ("TRCLSR", 2, 1, 7, 13, 6, "Trace Software Lock Status Register"),
    ("TRCAUTHSTATUS", 2, 1, 7, 14, 6, "Trace Authentication Status Register"),
    ("TRCDEVARCH", 2, 1, 7, 15, 6, "Trace Device Architecture Register"),
    
    # Additional Trace Status
    ("TRCRSR", 2, 1, 1, 10, 0, "Trace Resources Status Register"),
    ("TRCQCTLR", 2, 1, 0, 1, 1, "Trace Q Element Control Register"),
    
    # ================================================================
    # TRUSTZONE (TrustZone for Cortex-A, ARMv8-A)
    # ================================================================
    ("TEECR32_EL1", 2, 2, 0, 0, 0, "T32EE Configuration Register"),
    ("TEEHBR32_EL1", 2, 2, 1, 0, 0, "T32EE Handler Base Register"),
    
    # ================================================================
    # RAS (Reliability, Availability, Serviceability) - ARMv8.2+
    # ================================================================
    ("ERRSELR_EL1", 3, 0, 5, 3, 1, "Error Record Select Register"),
    ("ERXCTLR_EL1", 3, 0, 5, 4, 1, "Selected Error Record Control Register"),
    ("ERXSTATUS_EL1", 3, 0, 5, 4, 2, "Selected Error Record Primary Status Register"),
    ("ERXADDR_EL1", 3, 0, 5, 4, 3, "Selected Error Record Address Register"),
    ("ERXMISC0_EL1", 3, 0, 5, 5, 0, "Selected Error Record Miscellaneous Register 0"),
    ("ERXMISC1_EL1", 3, 0, 5, 5, 1, "Selected Error Record Miscellaneous Register 1"),
    ("ERXMISC2_EL1", 3, 0, 5, 5, 2, "Selected Error Record Miscellaneous Register 2"),
    ("ERXMISC3_EL1", 3, 0, 5, 5, 3, "Selected Error Record Miscellaneous Register 3"),
    ("ERXPFGCTL_EL1", 3, 0, 5, 4, 4, "Selected Pseudo-fault Generation Control Register"),
    ("ERXPFGCDN_EL1", 3, 0, 5, 4, 6, "Selected Pseudo-fault Generation Countdown Register"),
    ("ERXTS_EL1", 3, 0, 5, 5, 4, "Selected Error Record Timestamp Register"),
    
    # ================================================================
    # STATISTICAL PROFILING EXTENSION (SPE) - ARMv8.2+
    # ================================================================
    ("PMSCR_EL1", 3, 0, 9, 9, 0, "Statistical Profiling Control Register (EL1)"),
    ("PMSCR_EL2", 3, 4, 9, 9, 0, "Statistical Profiling Control Register (EL2)"),
    ("PMSCR_EL12", 3, 5, 9, 9, 0, "Statistical Profiling Control Register (EL12)"),
    
    ("PMSICR_EL1", 3, 0, 9, 9, 2, "Sampling Interval Counter Register"),
    ("PMSIRR_EL1", 3, 0, 9, 9, 3, "Sampling Interval Reload Register"),
    ("PMSFCR_EL1", 3, 0, 9, 9, 4, "Sampling Filter Control Register"),
    ("PMSEVFR_EL1", 3, 0, 9, 9, 5, "Sampling Event Filter Register"),
    ("PMSLATFR_EL1", 3, 0, 9, 9, 6, "Sampling Latency Filter Register"),
    ("PMSIDR_EL1", 3, 0, 9, 9, 7, "Sampling Profiling ID Register"),
    
    ("PMBLIMITR_EL1", 3, 0, 9, 10, 0, "Profiling Buffer Limit Address Register"),
    ("PMBPTR_EL1", 3, 0, 9, 10, 1, "Profiling Buffer Write Pointer Register"),
    ("PMBSR_EL1", 3, 0, 9, 10, 3, "Profiling Buffer Status/syndrome Register"),
    ("PMBIDR_EL1", 3, 0, 9, 10, 7, "Profiling Buffer ID Register"),
    
    # ================================================================
    # TRACE BUFFER EXTENSION (TRBE) - ARMv8.9+/ARMv9.4+
    # ================================================================
    ("TRBLIMITR_EL1", 3, 0, 9, 11, 0, "Trace Buffer Limit Address Register"),
    ("TRBPTR_EL1", 3, 0, 9, 11, 1, "Trace Buffer Write Pointer Register"),
    ("TRBBASER_EL1", 3, 0, 9, 11, 2, "Trace Buffer Base Address Register"),
    ("TRBSR_EL1", 3, 0, 9, 11, 3, "Trace Buffer Status/syndrome Register"),
    ("TRBMAR_EL1", 3, 0, 9, 11, 4, "Trace Buffer Memory Attribute Register"),
    ("TRBTRG_EL1", 3, 0, 9, 11, 6, "Trace Buffer Trigger Counter Register"),
    ("TRBIDR_EL1", 3, 0, 9, 11, 7, "Trace Buffer ID Register"),
    
    # ================================================================
    # TRACE FILTER CONTROL - ARMv8.4+
    # ================================================================
    ("TRFCR_EL1", 3, 0, 1, 2, 1, "Trace Filter Control Register (EL1)"),
    ("TRFCR_EL2", 3, 4, 1, 2, 1, "Trace Filter Control Register (EL2)"),
    ("TRFCR_EL12", 3, 5, 1, 2, 1, "Trace Filter Control Register (EL12)"),
    
    # ================================================================
    # MPAM (Memory System Resource Partitioning and Monitoring)
    # ================================================================
    ("MPAM0_EL1", 3, 0, 10, 5, 1, "MPAM0 Register (EL1)"),
    ("MPAM1_EL1", 3, 0, 10, 5, 0, "MPAM1 Register (EL1)"),
    ("MPAM1_EL12", 3, 5, 10, 5, 0, "MPAM1 Register (EL12)"),
    ("MPAM2_EL2", 3, 4, 10, 5, 0, "MPAM2 Register (EL2)"),
    ("MPAM3_EL3", 3, 6, 10, 5, 0, "MPAM3 Register (EL3)"),
    ("MPAMHCR_EL2", 3, 4, 10, 4, 0, "MPAM Hypervisor Control Register (EL2)"),
    ("MPAMVPMV_EL2", 3, 4, 10, 4, 1, "MPAM Virtual PARTID Mapping Valid Register"),
    ("MPAMVPM0_EL2", 3, 4, 10, 6, 0, "MPAM Virtual PARTID Mapping Register 0"),
    ("MPAMVPM1_EL2", 3, 4, 10, 6, 1, "MPAM Virtual PARTID Mapping Register 1"),
    ("MPAMVPM2_EL2", 3, 4, 10, 6, 2, "MPAM Virtual PARTID Mapping Register 2"),
    ("MPAMVPM3_EL2", 3, 4, 10, 6, 3, "MPAM Virtual PARTID Mapping Register 3"),
    ("MPAMVPM4_EL2", 3, 4, 10, 6, 4, "MPAM Virtual PARTID Mapping Register 4"),
    ("MPAMVPM5_EL2", 3, 4, 10, 6, 5, "MPAM Virtual PARTID Mapping Register 5"),
    ("MPAMVPM6_EL2", 3, 4, 10, 6, 6, "MPAM Virtual PARTID Mapping Register 6"),
    ("MPAMVPM7_EL2", 3, 4, 10, 6, 7, "MPAM Virtual PARTID Mapping Register 7"),
    
    # ================================================================
    # ACTIVITY MONITORS EXTENSION (AMU) - ARMv8.4+
    # ================================================================
    ("AMCR_EL0", 3, 3, 13, 2, 0, "Activity Monitors Control Register"),
    ("AMCFGR_EL0", 3, 3, 13, 2, 1, "Activity Monitors Configuration Register"),
    ("AMCGCR_EL0", 3, 3, 13, 2, 2, "Activity Monitors Counter Group Configuration Register"),
    ("AMUSERENR_EL0", 3, 3, 13, 2, 3, "Activity Monitors User Enable Register"),
    
    ("AMCNTENCLR0_EL0", 3, 3, 13, 2, 4, "Activity Monitors Count Enable Clear Register 0"),
    ("AMCNTENSET0_EL0", 3, 3, 13, 2, 5, "Activity Monitors Count Enable Set Register 0"),
    ("AMCNTENCLR1_EL0", 3, 3, 13, 3, 0, "Activity Monitors Count Enable Clear Register 1"),
    ("AMCNTENSET1_EL0", 3, 3, 13, 3, 1, "Activity Monitors Count Enable Set Register 1"),
    
    # Activity Monitor Event Counter Registers Group 0 (architecture defined, 0-3)
    ("AMEVCNTR00_EL0", 3, 3, 13, 4, 0, "Activity Monitors Event Counter Register 0 (Group 0)"),
    ("AMEVCNTR01_EL0", 3, 3, 13, 4, 1, "Activity Monitors Event Counter Register 1 (Group 0)"),
    ("AMEVCNTR02_EL0", 3, 3, 13, 4, 2, "Activity Monitors Event Counter Register 2 (Group 0)"),
    ("AMEVCNTR03_EL0", 3, 3, 13, 4, 3, "Activity Monitors Event Counter Register 3 (Group 0)"),
    
    # Activity Monitor Event Counter Registers Group 1 (auxiliary, 0-15)
    ("AMEVCNTR10_EL0", 3, 3, 13, 12, 0, "Activity Monitors Event Counter Register 0 (Group 1)"),
    ("AMEVCNTR11_EL0", 3, 3, 13, 12, 1, "Activity Monitors Event Counter Register 1 (Group 1)"),
    ("AMEVCNTR12_EL0", 3, 3, 13, 12, 2, "Activity Monitors Event Counter Register 2 (Group 1)"),
    ("AMEVCNTR13_EL0", 3, 3, 13, 12, 3, "Activity Monitors Event Counter Register 3 (Group 1)"),
    ("AMEVCNTR14_EL0", 3, 3, 13, 12, 4, "Activity Monitors Event Counter Register 4 (Group 1)"),
    ("AMEVCNTR15_EL0", 3, 3, 13, 12, 5, "Activity Monitors Event Counter Register 5 (Group 1)"),
    ("AMEVCNTR16_EL0", 3, 3, 13, 12, 6, "Activity Monitors Event Counter Register 6 (Group 1)"),
    ("AMEVCNTR17_EL0", 3, 3, 13, 12, 7, "Activity Monitors Event Counter Register 7 (Group 1)"),
    ("AMEVCNTR18_EL0", 3, 3, 13, 13, 0, "Activity Monitors Event Counter Register 8 (Group 1)"),
    ("AMEVCNTR19_EL0", 3, 3, 13, 13, 1, "Activity Monitors Event Counter Register 9 (Group 1)"),
    ("AMEVCNTR110_EL0", 3, 3, 13, 13, 2, "Activity Monitors Event Counter Register 10 (Group 1)"),
    ("AMEVCNTR111_EL0", 3, 3, 13, 13, 3, "Activity Monitors Event Counter Register 11 (Group 1)"),
    ("AMEVCNTR112_EL0", 3, 3, 13, 13, 4, "Activity Monitors Event Counter Register 12 (Group 1)"),
    ("AMEVCNTR113_EL0", 3, 3, 13, 13, 5, "Activity Monitors Event Counter Register 13 (Group 1)"),
    ("AMEVCNTR114_EL0", 3, 3, 13, 13, 6, "Activity Monitors Event Counter Register 14 (Group 1)"),
    ("AMEVCNTR115_EL0", 3, 3, 13, 13, 7, "Activity Monitors Event Counter Register 15 (Group 1)"),
    
    # Activity Monitor Event Type Registers Group 1 (0-15)
    ("AMEVTYPER10_EL0", 3, 3, 13, 14, 0, "Activity Monitors Event Type Register 0 (Group 1)"),
    ("AMEVTYPER11_EL0", 3, 3, 13, 14, 1, "Activity Monitors Event Type Register 1 (Group 1)"),
    ("AMEVTYPER12_EL0", 3, 3, 13, 14, 2, "Activity Monitors Event Type Register 2 (Group 1)"),
    ("AMEVTYPER13_EL0", 3, 3, 13, 14, 3, "Activity Monitors Event Type Register 3 (Group 1)"),
    ("AMEVTYPER14_EL0", 3, 3, 13, 14, 4, "Activity Monitors Event Type Register 4 (Group 1)"),
    ("AMEVTYPER15_EL0", 3, 3, 13, 14, 5, "Activity Monitors Event Type Register 5 (Group 1)"),
    ("AMEVTYPER16_EL0", 3, 3, 13, 14, 6, "Activity Monitors Event Type Register 6 (Group 1)"),
    ("AMEVTYPER17_EL0", 3, 3, 13, 14, 7, "Activity Monitors Event Type Register 7 (Group 1)"),
    ("AMEVTYPER18_EL0", 3, 3, 13, 15, 0, "Activity Monitors Event Type Register 8 (Group 1)"),
    ("AMEVTYPER19_EL0", 3, 3, 13, 15, 1, "Activity Monitors Event Type Register 9 (Group 1)"),
    ("AMEVTYPER110_EL0", 3, 3, 13, 15, 2, "Activity Monitors Event Type Register 10 (Group 1)"),
    ("AMEVTYPER111_EL0", 3, 3, 13, 15, 3, "Activity Monitors Event Type Register 11 (Group 1)"),
    ("AMEVTYPER112_EL0", 3, 3, 13, 15, 4, "Activity Monitors Event Type Register 12 (Group 1)"),
    ("AMEVTYPER113_EL0", 3, 3, 13, 15, 5, "Activity Monitors Event Type Register 13 (Group 1)"),
    ("AMEVTYPER114_EL0", 3, 3, 13, 15, 6, "Activity Monitors Event Type Register 14 (Group 1)"),
    ("AMEVTYPER115_EL0", 3, 3, 13, 15, 7, "Activity Monitors Event Type Register 15 (Group 1)"),
    
    # ================================================================
    # LIMITED ORDERING REGIONS (LOR) - ARMv8.1+
    # ================================================================
    ("LORSA_EL1", 3, 0, 10, 4, 0, "LORegion Start Address (EL1)"),
    ("LOREA_EL1", 3, 0, 10, 4, 1, "LORegion End Address (EL1)"),
    ("LORN_EL1", 3, 0, 10, 4, 2, "LORegion Number (EL1)"),
    ("LORC_EL1", 3, 0, 10, 4, 3, "LORegion Control (EL1)"),
    ("LORID_EL1", 3, 0, 10, 4, 7, "LORegion ID (EL1)"),
    
    # ================================================================
    # GIC CPU INTERFACE SYSTEM REGISTERS (v3+)
    # ================================================================
    ("ICC_PMR_EL1", 3, 0, 4, 6, 0, "Interrupt Priority Mask Register"),
    ("ICC_IAR0_EL1", 3, 0, 12, 8, 0, "Interrupt Acknowledge Register 0"),
    ("ICC_EOIR0_EL1", 3, 0, 12, 8, 1, "End Of Interrupt Register 0"),
    ("ICC_HPPIR0_EL1", 3, 0, 12, 8, 2, "Highest Priority Pending Interrupt Register 0"),
    ("ICC_BPR0_EL1", 3, 0, 12, 8, 3, "Binary Point Register 0"),
    ("ICC_AP0R0_EL1", 3, 0, 12, 8, 4, "Active Priorities Register 0 (Group 0)"),
    ("ICC_AP0R1_EL1", 3, 0, 12, 8, 5, "Active Priorities Register 1 (Group 0)"),
    ("ICC_AP0R2_EL1", 3, 0, 12, 8, 6, "Active Priorities Register 2 (Group 0)"),
    ("ICC_AP0R3_EL1", 3, 0, 12, 8, 7, "Active Priorities Register 3 (Group 0)"),
    ("ICC_AP1R0_EL1", 3, 0, 12, 9, 0, "Active Priorities Register 0 (Group 1)"),
    ("ICC_AP1R1_EL1", 3, 0, 12, 9, 1, "Active Priorities Register 1 (Group 1)"),
    ("ICC_AP1R2_EL1", 3, 0, 12, 9, 2, "Active Priorities Register 2 (Group 1)"),
    ("ICC_AP1R3_EL1", 3, 0, 12, 9, 3, "Active Priorities Register 3 (Group 1)"),
    ("ICC_DIR_EL1", 3, 0, 12, 11, 1, "Deactivate Interrupt Register"),
    ("ICC_RPR_EL1", 3, 0, 12, 11, 3, "Running Priority Register"),
    ("ICC_SGI1R_EL1", 3, 0, 12, 11, 5, "Software Generated Interrupt Group 1 Register"),
    ("ICC_ASGI1R_EL1", 3, 0, 12, 11, 6, "Alias Software Generated Interrupt Group 1 Register"),
    ("ICC_SGI0R_EL1", 3, 0, 12, 11, 7, "Software Generated Interrupt Group 0 Register"),
    ("ICC_IAR1_EL1", 3, 0, 12, 12, 0, "Interrupt Acknowledge Register 1"),
    ("ICC_EOIR1_EL1", 3, 0, 12, 12, 1, "End Of Interrupt Register 1"),
    ("ICC_HPPIR1_EL1", 3, 0, 12, 12, 2, "Highest Priority Pending Interrupt Register 1"),
    ("ICC_BPR1_EL1", 3, 0, 12, 12, 3, "Binary Point Register 1"),
    ("ICC_CTLR_EL1", 3, 0, 12, 12, 4, "Interrupt Controller Control Register (EL1)"),
    ("ICC_CTLR_EL3", 3, 6, 12, 12, 4, "Interrupt Controller Control Register (EL3)"),
    ("ICC_SRE_EL1", 3, 0, 12, 12, 5, "Interrupt Controller System Register Enable (EL1)"),
    ("ICC_IGRPEN0_EL1", 3, 0, 12, 12, 6, "Interrupt Controller Interrupt Group 0 Enable (EL1)"),
    ("ICC_IGRPEN1_EL1", 3, 0, 12, 12, 7, "Interrupt Controller Interrupt Group 1 Enable (EL1)"),
    ("ICC_SEIEN_EL1", 3, 0, 12, 13, 0, "Interrupt Controller System Error Interrupt Enable Register"),
    ("ICC_SRE_EL2", 3, 4, 12, 9, 5, "Interrupt Controller System Register Enable (EL2)"),
    ("ICC_SRE_EL3", 3, 6, 12, 12, 5, "Interrupt Controller System Register Enable (EL3)"),
    ("ICC_IGRPEN1_EL3", 3, 6, 12, 12, 7, "Interrupt Controller Interrupt Group 1 Enable (EL3)"),
    
    # Hypervisor ICH registers
    ("ICH_HCR_EL2", 3, 4, 12, 11, 0, "Interrupt Controller Hyp Control Register"),
    ("ICH_VTR_EL2", 3, 4, 12, 11, 1, "Interrupt Controller VGIC Type Register"),
    ("ICH_MISR_EL2", 3, 4, 12, 11, 2, "Interrupt Controller Maintenance Interrupt State Register"),
    ("ICH_EISR_EL2", 3, 4, 12, 11, 3, "Interrupt Controller End of Interrupt Status Register"),
    ("ICH_ELRSR_EL2", 3, 4, 12, 11, 5, "Interrupt Controller Empty List Register Status Register"),
    ("ICH_VMCR_EL2", 3, 4, 12, 11, 7, "Interrupt Controller Virtual Machine Control Register"),
    ("ICH_VSEIR_EL2", 3, 4, 12, 9, 4, "Interrupt Controller Virtual System Error Interrupt Register"),
    ("ICH_AP0R0_EL2", 3, 4, 12, 8, 0, "Interrupt Controller Hyp Active Priorities Register 0"),
    ("ICH_AP0R1_EL2", 3, 4, 12, 8, 1, "Interrupt Controller Hyp Active Priorities Register 1"),
    ("ICH_AP0R2_EL2", 3, 4, 12, 8, 2, "Interrupt Controller Hyp Active Priorities Register 2"),
    ("ICH_AP0R3_EL2", 3, 4, 12, 8, 3, "Interrupt Controller Hyp Active Priorities Register 3"),
    ("ICH_AP1R0_EL2", 3, 4, 12, 9, 0, "Interrupt Controller Hyp Active Priorities Group 1 Register 0"),
    ("ICH_AP1R1_EL2", 3, 4, 12, 9, 1, "Interrupt Controller Hyp Active Priorities Group 1 Register 1"),
    ("ICH_AP1R2_EL2", 3, 4, 12, 9, 2, "Interrupt Controller Hyp Active Priorities Group 1 Register 2"),
    ("ICH_AP1R3_EL2", 3, 4, 12, 9, 3, "Interrupt Controller Hyp Active Priorities Group 1 Register 3"),
    ("ICH_LR0_EL2", 3, 4, 12, 12, 0, "Interrupt Controller List Register 0"),
    ("ICH_LR1_EL2", 3, 4, 12, 12, 1, "Interrupt Controller List Register 1"),
    ("ICH_LR2_EL2", 3, 4, 12, 12, 2, "Interrupt Controller List Register 2"),
    ("ICH_LR3_EL2", 3, 4, 12, 12, 3, "Interrupt Controller List Register 3"),
    ("ICH_LR4_EL2", 3, 4, 12, 12, 4, "Interrupt Controller List Register 4"),
    ("ICH_LR5_EL2", 3, 4, 12, 12, 5, "Interrupt Controller List Register 5"),
    ("ICH_LR6_EL2", 3, 4, 12, 12, 6, "Interrupt Controller List Register 6"),
    ("ICH_LR7_EL2", 3, 4, 12, 12, 7, "Interrupt Controller List Register 7"),
    ("ICH_LR8_EL2", 3, 4, 12, 13, 0, "Interrupt Controller List Register 8"),
    ("ICH_LR9_EL2", 3, 4, 12, 13, 1, "Interrupt Controller List Register 9"),
    ("ICH_LR10_EL2", 3, 4, 12, 13, 2, "Interrupt Controller List Register 10"),
    ("ICH_LR11_EL2", 3, 4, 12, 13, 3, "Interrupt Controller List Register 11"),
    ("ICH_LR12_EL2", 3, 4, 12, 13, 4, "Interrupt Controller List Register 12"),
    ("ICH_LR13_EL2", 3, 4, 12, 13, 5, "Interrupt Controller List Register 13"),
    ("ICH_LR14_EL2", 3, 4, 12, 13, 6, "Interrupt Controller List Register 14"),
    ("ICH_LR15_EL2", 3, 4, 12, 13, 7, "Interrupt Controller List Register 15"),
]

# fill in the gaps (HACK)
cache = {(t, u, v, w, x):1 for s,t,u,v,w,x,y in system_registers}
for x in range(0x8000, 0x10000):
    op0 = 2 | (x >> 14) & 1
    op1 = (x >> 11) & 7
    crn = (x >> 7) & 0xf
    crm = (x >> 3) & 0xf
    op2 = x & 7
    
    y = (op0, op1, crn, crm, op2)
    if cache.get(y):
        continue

    cache[y] = 1

    system_registers.append(("s%d_%d_c%d_c%d_%d" % (op0, op1, crn, crm, op2), op0, op1, crn, crm, op2, "Undefined / Implementation Specific"))
cache = None    # cleanup, no need for 32k items

# Build lookup dictionaries for fast access
sysreg_by_encoding = {}
sysreg_by_name = {}

for name, op0, op1, crn, crm, op2, desc in system_registers:
    encoding = (op0, op1, crn, crm, op2)
    sysreg_by_encoding[encoding] = (name, desc)
    sysreg_by_name[name.upper()] = (op0, op1, crn, crm, op2, desc)

def get_sysreg_by_encoding(op0, op1, crn, crm, op2):
    """Get system register name and description by encoding."""
    return sysreg_by_encoding.get((op0, op1, crn, crm, op2))

def get_sysreg_by_name(name):
    """Get system register encoding by name."""
    return sysreg_by_name.get(name.upper())

