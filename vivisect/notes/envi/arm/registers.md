# Notes for Register Debugging.

## ARM Banked Registers

ARMv7 (and prior) has banked registers, where each Processor Mode has a set of registers that are constant across all modes, and a set of registers that are unique to that processor mode.
In order to model this in Vivisect/Envi, we've created a multi-tiered accessor model, so that getRegister(REG_R11) goes through a translation/linkage layer to make sure the correct register data storage location is accessed, based on the processor mode.

As you might expect, this approach must be specifically spot-on accurate, or bad things can happen.  And those bad things aren't necessarily obvious.

## SPSRs
We ran into difficulties with SPSR's since SPSRs have the extra complexity of CPSR pointing directly at one of them.
So we fixed the bugs, and got things to line up.  The problem is, it was a real PITA making it all look right.

So we wanted to document some of the sanity-checks we used to troubleshoot in humon-mode.  These may or may not be good unittests, but they are certainly helpful for hands-on testing.

These were originally left in the unittest code, but moved here for clarity.

'''
for posterity:
In [63]: for _,_,_,_,_,PSR,_ in eaar.proc_modes.values(): print(hex(PSR), eaar.reg_table[PSR], eaar.reg_data[eaar.reg_table[PSR]])
    0x13 19 ('r8_fiq', 32)
    0x27 26 ('SPSR_fiq', 32)
    0x3b 29 ('SPSR_irq', 32)
    0x4f 32 ('SPSR_svc', 32)
    0x8b 35 ('SPSR_mon', 32)
    0x9f 38 ('SPSR_abt', 32)
    0xdb 41 ('SPSR_hyp', 32)
    0xef 44 ('SPSR_und', 32)
    0x13f 45 ('SPSR_sys', 32)

this is a humon-repeatable test for future troubleshooting.
this test shows that each outer shell index for the SPSRs reference the inner stored 
SPSRs for each level (ie. what's stored in the RegisterContext).  all but the first 
one, because proc_mode[0] doesn't have an SPSR.
'''

'''
more posterity:
In [107]: for mode in eaar.proc_modes: print(eaar.reg_data[eaar._getRegIdx(eaar.REG_OFFSET_SPSR, mode)])
    _getRegIdx(12, 0) -> (12)
    _getRegIdx(12, 0) -> 12
    ('spsr', 32)
    _getRegIdx(12, 1) -> (25)
    _getRegIdx(12, 1) -> 1a
    ('SPSR_fiq', 32)
    _getRegIdx(12, 2) -> (38)
    _getRegIdx(12, 2) -> 1d
    ('SPSR_irq', 32)
    _getRegIdx(12, 3) -> (4b)
    _getRegIdx(12, 3) -> 20
    ('SPSR_svc', 32)
    _getRegIdx(12, 6) -> (84)
    _getRegIdx(12, 6) -> 23
    ('SPSR_mon', 32)
    _getRegIdx(12, 7) -> (97)
    _getRegIdx(12, 7) -> 26
    ('SPSR_abt', 32)
    _getRegIdx(12, a) -> (d0)
    _getRegIdx(12, a) -> 29
    ('SPSR_hyp', 32)
    _getRegIdx(12, b) -> (e3)
    _getRegIdx(12, b) -> 2c
    ('SPSR_und', 32)
    _getRegIdx(12, f) -> (12f)
    _getRegIdx(12, f) -> 2d
    ('SPSR_sys', 32)

In [108]: for mode in eaar.proc_modes: print(eaar.reg_data[eaar._getRegIdx(eaar.REG_OFFSET_CPSR, mode)])
    _getRegIdx(10, 0) -> (10)
    _getRegIdx(10, 0) -> 10
    ('cpsr', 32)
    _getRegIdx(10, 1) -> (23)
    _getRegIdx(10, 1) -> 10
    ('cpsr', 32)
    _getRegIdx(10, 2) -> (36)
    _getRegIdx(10, 2) -> 10
    ('cpsr', 32)
    _getRegIdx(10, 3) -> (49)
    _getRegIdx(10, 3) -> 10
    ('cpsr', 32)
    _getRegIdx(10, 6) -> (82)
    _getRegIdx(10, 6) -> 10
    ('cpsr', 32)
    _getRegIdx(10, 7) -> (95)
    _getRegIdx(10, 7) -> 10
    ('cpsr', 32)
    _getRegIdx(10, a) -> (ce)
    _getRegIdx(10, a) -> 10
    ('cpsr', 32)
    _getRegIdx(10, b) -> (e1)
    _getRegIdx(10, b) -> 10
    ('cpsr', 32)
    _getRegIdx(10, f) -> (12d)
    _getRegIdx(10, f) -> 10
    ('cpsr', 32)

again, humon-tests which show the SPSR for each level, as well as the CPSR for each level.
obviously, all the CPSRs point to the one and only, RegisterContext register index 0x10
these have the print statement uncommented for _getRegIdx()
'''

