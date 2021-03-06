# -*- coding: latin-1 -*-

import envi.bits as e_bits

# "encodings" is data scraped from the EREF manual
# "EXTRA_OPCODES" is a table added manually in addition to the scraped data

#FIXME: dcbtst (and others, I assume) has different operand ordering between Embedded and Server

encodings = '''tdi 0 0 0 0 1 0
 TO
 rA
 SIMM
 D
 64
twi 0 0 0 0 1 1
 TO
 rA
 SIMM
 D
vaddubm 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 0 0 0
 0
 0 0 0
 0
 0
 VX
 V
vmaxub 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 0 0 0
 0
 0 0 0
 1
 0
 VX
 V
vrlb 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 0 0 0
 0
 0 0 1
 0
 0
 VX
 V
vcmpequb 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 0 0 0
 0
 0 0 1
 1
 0
 VC
 V
vmuloub 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 0 0 0
 0
 0 1 0
 0
 0
 VX
 V
vaddfp 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 0 0 0
 0
 0 1 0
 1
 0
 VX
 V
vmrghb 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 0 0 0
 0
 0 1 1
 0
 0
 VX
 V
vpkuhum 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 0 0 0
 0
 0 1 1
 1
 0
 VX
 V
vmhaddshs 0 0 0 1 0 0
 vD
 vA
 vB
 vC
 1
 0 0 0
 0
 0
 VA
 V
vmhraddshs 0 0 0 1 0 0
 vD
 vA
 vB
 vC
 1
 0 0 0
 0
 1
 VA
 V
vmladduhm 0 0 0 1 0 0
 vD
 vA
 vB
 vC
 1
 0 0 0
 1
 0
 VA
 V
vmsumubm 0 0 0 1 0 0
 vD
 vA
 vB
 vC
 1
 0 0 1
 0
 0
 VA
 V
vmsummbm 0 0 0 1 0 0
 vD
 vA
 vB
 vC
 1
 0 0 1
 0
 1
 VA
 V
vmsumuhm 0 0 0 1 0 0
 vD
 vA
 vB
 vC
 1
 0 0 1
 1
 0
 VA
 V
vmsumuhs 0 0 0 1 0 0
 vD
 vA
 vB
 vC
 1
 0 0 1
 1
 1
 VA
 V
vmsumshm 0 0 0 1 0 0
 vD
 vA
 vB
 vC
 1
 0 1 0
 0
 0
 VA
 V
vmsumshs 0 0 0 1 0 0
 vD
 vA
 vB
 vC
 1
 0 1 0
 0
 1
 VA
 V
vsel 0 0 0 1 0 0
 vD
 vA
 vB
 vC
 1
 0 1 0
 1
 0
 VA
 V
vperm 0 0 0 1 0 0
 vD
 vA
 vB
 vC
 1
 0 1 0
 1
 1
 VA
 V
vsldoi 0 0 0 1 0 0
 vD
 vA
 vB
 /
 SH
 1
 0 1 1
 0
 0
 VX
 V
vmaddfp 0 0 0 1 0 0
 vD
 vA
 vB
 vC
 1
 0 1 1
 1
 0
 VA
 V
vnmsubfp 0 0 0 1 0 0
 vD
 vA
 vB
 vC
 1
 0 1 1
 1
 1
 VA
 V
vadduhm 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 0 0 1
 0
 0 0 0
 0
 0
 VX
 V
vmaxuh 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 0 0 1
 0
 0 0 0
 1
 0
 VX
 V
vrlh 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 0 0 1
 0
 0 0 1
 0
 0
 VX
 V
vcmpequh 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 0 0 1
 0
 0 0 1
 1
 0
 VC
 V
vmulouh 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 0 0 1
 0
 0 1 0
 0
 0
 VX
 V
vsubfp 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 0 0 1
 0
 0 1 0
 1
 0
 VX
 V
vmrghh 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 0 0 1
 0
 0 1 1
 0
 0
 VX
 V
vpkuwum 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 0 0 1
 0
 0 1 1
 1
 0
 VX
 V
EREF: A Programmer’s Reference Manual for Freescale Power Architecture Processors, Rev. 1 (EIS 2.1)
Freescale Semiconductor
A-85
Instruction Set Listings
Table A-4. Instructions Sorted by Opcode (Binary) (continued)
Mnemonic
 0
 1
 2
 3
 4
 5
 6
 7
 8
 9
 10
 11
 12
 13 14 15 16 17
 18 19 20 21 22
 23 24
 25
 26
 27
 28
 29
 30
 31
 Form Category
vadduwm 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 0 1 0
 0
 0 0 0
 0
 0
 VX
 V
vmaxuw 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 0 1 0
 0
 0 0 0
 1
 0
 VX
 V
vrlw 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 0 1 0
 0
 0 0 1
 0
 0
 VX
 V
vcmpequw 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 0 1 0
 0
 0 0 1
 1
 0
 VC
 V
vmrghw 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 0 1 0
 0
 0 1 1
 0
 0
 VX
 V
vpkuhus 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 0 1 0
 0
 0 1 1
 1
 0
 VX
 V
vcmpeqfp 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 0 1 1
 0
 0 0 1
 1
 0
 VC
 V
vpkuwus 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 0 1 1
 0
 0 1 1
 1
 0
 VX
 V
vmaxsb 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 1 0 0
 0
 0 0 0
 1
 0
 VX
 V
vslb 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 1 0 0
 0
 0 0 1
 0
 0
 VX
 V
vmulosb 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 1 0 0
 0
 0 1 0
 0
 0
 VX
 V
vrefp 0 0 0 1 0 0
 vD
 ///
 vB
 0 0 1 0 0
 0
 0 1 0
 1
 0
 VX
 V
vmrglb 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 1 0 0
 0
 0 1 1
 0
 0
 VX
 V
vpkshus 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 1 0 0
 0
 0 1 1
 1
 0
 VX
 V
vmaxsh 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 1 0 1
 0
 0 0 0
 1
 0
 VX
 V
vslh 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 1 0 1
 0
 0 0 1
 0
 0
 VX
 V
vmulosh 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 1 0 1
 0
 0 1 0
 0
 0
 VX
 V
vrsqrtefp 0 0 0 1 0 0
 vD
 ///
 vB
 0 0 1 0 1
 0
 0 1 0
 1
 0
 VX
 V
vmrglh 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 1 0 1
 0
 0 1 1
 0
 0
 VX
 V
vpkswus 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 1 0 1
 0
 0 1 1
 1
 0
 VX
 V
vaddcuw 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 1 1 0
 0
 0 0 0
 0
 0
 VX
 V
vmaxsw 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 1 1 0
 0
 0 0 0
 1
 0
 VX
 V
vslw 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 1 1 0
 0
 0 0 1
 0
 0
 VX
 V
vexptefp 0 0 0 1 0 0
 vD
 ///
 vB
 0 0 1 1 0
 0
 0 1 0
 1
 0
 VX
 V
vmrglw 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 1 1 0
 0
 0 1 1
 0
 0
 VX
 V
vpkshss 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 1 1 0
 0
 0 1 1
 1
 0
 VX
 V
vsl 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 1 1 1
 0
 0 0 1
 0
 0
 VX
 V
vcmpgefp 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 1 1 1
 0
 0 0 1
 1
 0
 VC
 V
vlogefp 0 0 0 1 0 0
 vD
 ///
 vB
 0 0 1 1 1
 0
 0 1 0
 1
 0
 VX
 V
vpkswss 0 0 0 1 0 0
 vD
 vA
 vB
 0 0 1 1 1
 0
 0 1 1
 1
 0
 VX
 V
evaddw 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 0 0 0
 0
 0 0 0
 0
 0
 EVX SP
vaddubs 0 0 0 1 0 0
 vD
 vA
 vB
 0 1 0 0 0
 0
 0 0 0
 0
 0
 VX
 V
evaddiw 0 0 0 1 0 0
 rD
 UIMM
 rB
 0 1 0 0 0
 0
 0 0 0
 1
 0
 EVX SP
vminub 0 0 0 1 0 0
 vD
 vA
 vB
 0 1 0 0 0
 0
 0 0 0
 1
 0
 VX
 V
evsubfw 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 0 0 0
 0
 0 0 1
 0
 0
 EVX SP
A-86
EREF: A Programmer’s Reference Manual for Freescale Power Architecture Processors, Rev. 1 (EIS 2.1)
Freescale Semiconductor
Instruction Set Listings
Table A-4. Instructions Sorted by Opcode (Binary) (continued)
Mnemonic
 0
 1
 2
 3
 4
 5
 6
 7
 8
 9
 10
 11
 12
 13 14 15 16 17
 18 19 20 21 22
 23 24
 25
 26
 27
 28
 29
 30
 31
 Form Category
vsrb 0 0 0 1 0 0
 vD
 vA
 vB
 0 1 0 0 0
 0
 0 0 1
 0
 0
 VX
 V
evsubifw 0 0 0 1 0 0
 rD
 UIMM
 rB
 0 1 0 0 0
 0
 0 0 1
 1
 0
 EVX SP
vcmpgtub 0 0 0 1 0 0
 vD
 vA
 vB
 0 1 0 0 0
 0
 0 0 1
 1
 0
 VC
 V
evabs 0 0 0 1 0 0
 rD
 rA
 ///
 0 1 0 0 0
 0
 0 1 0
 0
 0
 EVX SP
vmuleub 0 0 0 1 0 0
 vD
 vA
 vB
 0 1 0 0 0
 0
 0 1 0
 0
 0
 VX
 V
evneg 0 0 0 1 0 0
 rD
 rA
 ///
 0 1 0 0 0
 0
 0 1 0
 0
 1
 EVX SP
evextsb 0 0 0 1 0 0
 rD
 rA
 ///
 0 1 0 0 0
 0
 0 1 0
 1
 0
 EVX SP
vrfin 0 0 0 1 0 0
 vD
 ///
 vB
 0 1 0 0 0
 0
 0 1 0
 1
 0
 VX
 V
evextsh 0 0 0 1 0 0
 rD
 rA
 ///
 0 1 0 0 0
 0
 0 1 0
 1
 1
 EVX SP
evrndw 0 0 0 1 0 0
 rD
 rA
 0 0 0 0 0
 0 1 0 0 0
 0
 0 1 1
 0
 0
 EVX SP
vspltb 0 0 0 1 0 0
 vD
 UIMM
 vB
 0 1 0 0 0
 0
 0 1 1
 0
 0
 VX
 V
evcntlzw 0 0 0 1 0 0
 rD
 rA
 ///
 0 1 0 0 0
 0
 0 1 1
 0
 1
 EVX SP
evcntlsw 0 0 0 1 0 0
 rD
 rA
 ///
 0 1 0 0 0
 0
 0 1 1
 1
 0
 EVX SP
vupkhsb 0 0 0 1 0 0
 vD
 ///
 vB
 0 1 0 0 0
 0
 0 1 1
 1
 0
 VX
 V
brinc 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 0 0 0
 0
 0 1 1
 1
 1
 EVX SP
evand 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 0 0 0
 0
 1 0 0
 0
 1
 EVX SP
evandc 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 0 0 0
 0
 1 0 0
 1
 0
 EVX SP
evxor 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 0 0 0
 0
 1 0 1
 1
 0
 EVX SP
evor 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 0 0 0
 0
 1 0 1
 1
 1
 EVX SP
evnor 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 0 0 0
 0
 1 1 0
 0
 0
 EVX SP
eveqv 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 0 0 0
 0
 1 1 0
 0
 1
 EVX SP
evorc 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 0 0 0
 0
 1 1 0
 1
 1
 EVX SP
evnand 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 0 0 0
 0
 1 1 1
 1
 0
 EVX SP
evsrwu 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 0 0 0
 1
 0 0 0
 0
 0
 EVX SP
evsrws 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 0 0 0
 1
 0 0 0
 0
 1
 EVX SP
evsrwiu 0 0 0 1 0 0
 rD
 rA
 UIMM
 0 1 0 0 0
 1
 0 0 0
 1
 0
 EVX SP
evsrwis 0 0 0 1 0 0
 rD
 rA
 UIMM
 0 1 0 0 0
 1
 0 0 0
 1
 1
 EVX SP
evslw 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 0 0 0
 1
 0 0 1
 0
 0
 EVX SP
evslwi 0 0 0 1 0 0
 rD
 rA
 UIMM
 0 1 0 0 0
 1
 0 0 1
 1
 0
 EVX SP
evrlw 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 0 0 0
 1
 0 1 0
 0
 0
 EVX SP
evsplati 0 0 0 1 0 0
 rD
 SIMM
 ///
 0 1 0 0 0
 1
 0 1 0
 0
 1
 EVX SP
evrlwi 0 0 0 1 0 0
 rD
 rA
 UIMM
 0 1 0 0 0
 1
 0 1 0
 1
 0
 EVX SP
evsplatfi 0 0 0 1 0 0
 rD
 SIMM
 ///
 0 1 0 0 0
 1
 0 1 0
 1
 1
 EVX SP
evmergehi 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 0 0 0
 1
 0 1 1
 0
 0
 EVX SP
evmergelo 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 0 0 0
 1
 0 1 1
 0
 1
 EVX SP
EREF: A Programmer’s Reference Manual for Freescale Power Architecture Processors, Rev. 1 (EIS 2.1)
Freescale Semiconductor
A-87
Instruction Set Listings
Table A-4. Instructions Sorted by Opcode (Binary) (continued)
Mnemonic
 0
 1
 2
 3
 4
 5
 6
 7
 8
 9
 10
 11
 12
 13 14 15 16 17
 18 19 20 21 22
 23 24
 25
 26
 27
 28
 29
 30
 31
 Form Category
evmergehilo 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 0 0 0
 1
 0 1 1
 1
 0
 EVX SP
evmergelohi 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 0 0 0
 1
 0 1 1
 1
 1
 EVX SP
evcmpgtu 0 0 0 1 0 0
 crD
 /
 /
 rA
 rB
 0 1 0 0 0
 1
 1 0 0
 0
 0
 EVX SP
evcmpgts 0 0 0 1 0 0
 crD
 /
 /
 rA
 rB
 0 1 0 0 0
 1
 1 0 0
 0
 1
 EVX SP
evcmpltu 0 0 0 1 0 0
 crD
 /
 /
 rA
 rB
 0 1 0 0 0
 1
 1 0 0
 1
 0
 EVX SP
evcmplts 0 0 0 1 0 0
 crD
 /
 /
 rA
 rB
 0 1 0 0 0
 1
 1 0 0
 1
 1
 EVX SP
evcmpeq 0 0 0 1 0 0
 crD
 /
 /
 rA
 rB
 0 1 0 0 0
 1
 1 0 1
 0
 0
 EVX SP
vadduhs 0 0 0 1 0 0
 vD
 vA
 vB
 0 1 0 0 1
 0
 0 0 0
 0
 0
 VX
 V
vminuh 0 0 0 1 0 0
 vD
 vA
 vB
 0 1 0 0 1
 0
 0 0 0
 1
 0
 VX
 V
vsrh 0 0 0 1 0 0
 vD
 vA
 vB
 0 1 0 0 1
 0
 0 0 1
 0
 0
 VX
 V
vcmpgtuh 0 0 0 1 0 0
 vD
 vA
 vB
 0 1 0 0 1
 0
 0 0 1
 1
 0
 VC
 V
vmuleuh 0 0 0 1 0 0
 vD
 vA
 vB
 0 1 0 0 1
 0
 0 1 0
 0
 0
 VX
 V
vrfiz 0 0 0 1 0 0
 vD
 ///
 vB
 0 1 0 0 1
 0
 0 1 0
 1
 0
 VX
 V
vsplth 0 0 0 1 0 0
 vD
 UIMM
 vB
 0 1 0 0 1
 0
 0 1 1
 0
 0
 VX
 V
vupkhsh 0 0 0 1 0 0
 vD
 ///
 vB
 0 1 0 0 1
 0
 0 1 1
 1
 0
 VX
 V
evsel 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 0 0 1
 1
 1 1
 crfS
 EVX SP
evfsadd 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 0 1 0
 0
 0 0 0
 0
 0
 EVX SP.FV
vadduws 0 0 0 1 0 0
 vD
 vA
 vB
 0 1 0 1 0
 0
 0 0 0
 0
 0
 VX
 V
evfssub 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 0 1 0
 0
 0 0 0
 0
 1
 EVX SP.FV
vminuw 0 0 0 1 0 0
 vD
 vA
 vB
 0 1 0 1 0
 0
 0 0 0
 1
 0
 VX
 V
evfsabs 0 0 0 1 0 0
 rD
 rA
 ///
 0 1 0 1 0
 0
 0 0 1
 0
 0
 EVX SP.FV
vsrw 0 0 0 1 0 0
 vD
 vA
 vB
 0 1 0 1 0
 0
 0 0 1
 0
 0
 VX
 V
evfsnabs 0 0 0 1 0 0
 rD
 rA
 ///
 0 1 0 1 0
 0
 0 0 1
 0
 1
 EVX SP.FV
evfsneg 0 0 0 1 0 0
 rD
 rA
 ///
 0 1 0 1 0
 0
 0 0 1
 1
 0
 EVX SP.FV
vcmpgtuw 0 0 0 1 0 0
 vD
 vA
 vB
 0 1 0 1 0
 0
 0 0 1
 1
 0
 VC
 V
evfsmul 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 0 1 0
 0
 0 1 0
 0
 0
 EVX SP.FV
evfsdiv 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 0 1 0
 0
 0 1 0
 0
 1
 EVX SP.FV
vrfip 0 0 0 1 0 0
 vD
 ///
 vB
 0 1 0 1 0
 0
 0 1 0
 1
 0
 VX
 V
evfscmpgt 0 0 0 1 0 0
 crD
 /
 /
 rA
 rB
 0 1 0 1 0
 0
 0 1 1
 0
 0
 EVX SP.FV
vspltw 0 0 0 1 0 0
 vD
 UIMM
 vB
 0 1 0 1 0
 0
 0 1 1
 0
 0
 VX
 V
evfscmplt 0 0 0 1 0 0
 crD
 /
 /
 rA
 rB
 0 1 0 1 0
 0
 0 1 1
 0
 1
 EVX SP.FV
evfscmpeq 0 0 0 1 0 0
 crD
 /
 /
 rA
 rB
 0 1 0 1 0
 0
 0 1 1
 1
 0
 EVX SP.FV
vupklsb 0 0 0 1 0 0
 vD
 ///
 vB
 0 1 0 1 0
 0
 0 1 1
 1
 0
 VX
 V
evfscfui 0 0 0 1 0 0
 rD
 ///
 rB
 0 1 0 1 0
 0
 1 0 0
 0
 0
 EVX SP.FV
evfscfsi 0 0 0 1 0 0
 rD
 ///
 rB
 0 1 0 1 0
 0
 1 0 0
 0
 1
 EVX SP.FV
A-88
EREF: A Programmer’s Reference Manual for Freescale Power Architecture Processors, Rev. 1 (EIS 2.1)
Freescale Semiconductor
Instruction Set Listings
Table A-4. Instructions Sorted by Opcode (Binary) (continued)
Mnemonic
 0
 1
 2
 3
 4
 5
 6
 7
 8
 9
 10
 11
 12
 13 14 15 16 17
 18 19 20 21 22
 23 24
 25
 26
 27
 28
 29
 30
 31
 Form Category
evfscfuf 0 0 0 1 0 0
 rD
 ///
 rB
 0 1 0 1 0
 0
 1 0 0
 1
 0
 EVX SP.FV
evfscfsf 0 0 0 1 0 0
 rD
 ///
 rB
 0 1 0 1 0
 0
 1 0 0
 1
 1
 EVX SP.FV
evfsctui 0 0 0 1 0 0
 rD
 ///
 rB
 0 1 0 1 0
 0
 1 0 1
 0
 0
 EVX SP.FV
evfsctsi 0 0 0 1 0 0
 rD
 ///
 rB
 0 1 0 1 0
 0
 1 0 1
 0
 1
 EVX SP.FV
evfsctuf 0 0 0 1 0 0
 rD
 ///
 rB
 0 1 0 1 0
 0
 1 0 1
 1
 0
 EVX SP.FV
evfsctsf 0 0 0 1 0 0
 rD
 ///
 rB
 0 1 0 1 0
 0
 1 0 1
 1
 1
 EVX SP.FV
evfsctuiz 0 0 0 1 0 0
 rD
 ///
 rB
 0 1 0 1 0
 0
 1 1 0
 0
 0
 EVX SP.FV
evfsctsiz 0 0 0 1 0 0
 rD
 ///
 rB
 0 1 0 1 0
 0
 1 1 0
 1
 0
 EVX SP.FV
evfststgt 0 0 0 1 0 0
 crD
 /
 /
 rA
 rB
 0 1 0 1 0
 0
 1 1 1
 0
 0
 EVX SP.FV
evfststlt 0 0 0 1 0 0
 crD
 /
 /
 rA
 rB
 0 1 0 1 0
 0
 1 1 1
 0
 1
 EVX SP.FV
evfststeq 0 0 0 1 0 0
 crD
 /
 /
 rA
 rB
 0 1 0 1 0
 0
 1 1 1
 1
 0
 EVX SP.FV
efsadd 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 0 1 1
 0
 0 0 0
 0
 0
 EVX SP.FS
efssub 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 0 1 1
 0
 0 0 0
 0
 1
 EVX SP.FS
efsabs 0 0 0 1 0 0
 rD
 rA
 ///
 0 1 0 1 1
 0
 0 0 1
 0
 0
 EVX SP.FS
vsr 0 0 0 1 0 0
 vD
 vA
 vB
 0 1 0 1 1
 0
 0 0 1
 0
 0
 VX
 V
efsnabs 0 0 0 1 0 0
 rD
 rA
 ///
 0 1 0 1 1
 0
 0 0 1
 0
 1
 EVX SP.FS
efsneg 0 0 0 1 0 0
 rD
 rA
 ///
 0 1 0 1 1
 0
 0 0 1
 1
 0
 EVX SP.FS
vcmpgtfp 0 0 0 1 0 0
 vD
 vA
 vB
 0 1 0 1 1
 0
 0 0 1
 1
 0
 VC
 V
efsmul 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 0 1 1
 0
 0 1 0
 0
 0
 EVX SP.FS
efsdiv 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 0 1 1
 0
 0 1 0
 0
 1
 EVX SP.FS
vrfim 0 0 0 1 0 0
 vD
 ///
 vB
 0 1 0 1 1
 0
 0 1 0
 1
 0
 VX
 V
efscmpgt 0 0 0 1 0 0
 crD
 /
 /
 rA
 rB
 0 1 0 1 1
 0
 0 1 1
 0
 0
 EVX SP.FS
efscmplt 0 0 0 1 0 0
 crD
 /
 /
 rA
 rB
 0 1 0 1 1
 0
 0 1 1
 0
 1
 EVX SP.FS
efscmpeq 0 0 0 1 0 0
 crD
 /
 /
 rA
 rB
 0 1 0 1 1
 0
 0 1 1
 1
 0
 EVX SP.FS
vupklsh 0 0 0 1 0 0
 vD
 ///
 vB
 0 1 0 1 1
 0
 0 1 1
 1
 0
 VX
 V
efscfd 0 0 0 1 0 0
 rD
 0
 0 0 0 0
 rB
 0 1 0 1 1
 0
 0 1 1
 1
 1
 EVX SP.FS
efscfui 0 0 0 1 0 0
 rD
 ///
 rB
 0 1 0 1 1
 0
 1 0 0
 0
 0
 EVX SP.FS
efscfsi 0 0 0 1 0 0
 rD
 ///
 rB
 0 1 0 1 1
 0
 1 0 0
 0
 1
 EVX SP.FS
efscfuf 0 0 0 1 0 0
 rD
 ///
 rB
 0 1 0 1 1
 0
 1 0 0
 1
 0
 EVX SP.FS
efscfsf 0 0 0 1 0 0
 rD
 ///
 rB
 0 1 0 1 1
 0
 1 0 0
 1
 1
 EVX SP.FS
efsctui 0 0 0 1 0 0
 rD
 ///
 rB
 0 1 0 1 1
 0
 1 0 1
 0
 0
 EVX SP.FS
efsctsi 0 0 0 1 0 0
 rD
 ///
 rB
 0 1 0 1 1
 0
 1 0 1
 0
 1
 EVX SP.FS
efsctuf 0 0 0 1 0 0
 rD
 ///
 rB
 0 1 0 1 1
 0
 1 0 1
 1
 0
 EVX SP.FS
efsctsf 0 0 0 1 0 0
 rD
 ///
 rB
 0 1 0 1 1
 0
 1 0 1
 1
 1
 EVX SP.FS
efsctuiz 0 0 0 1 0 0
 rD
 ///
 rB
 0 1 0 1 1
 0
 1 1 0
 0
 0
 EVX SP.FS
EREF: A Programmer’s Reference Manual for Freescale Power Architecture Processors, Rev. 1 (EIS 2.1)
Freescale Semiconductor
A-89
Instruction Set Listings
Table A-4. Instructions Sorted by Opcode (Binary) (continued)
Mnemonic
 0
 1
 2
 3
 4
 5
 6
 7
 8
 9
 10
 11
 12
 13 14 15 16 17
 18 19 20 21 22
 23 24
 25
 26
 27
 28
 29
 30
 31
 Form Category
efsctsiz 0 0 0 1 0 0
 rD
 ///
 rB
 0 1 0 1 1
 0
 1 1 0
 1
 0
 EVX SP.FS
efststgt 0 0 0 1 0 0
 crD
 /
 /
 rA
 rB
 0 1 0 1 1
 0
 1 1 1
 0
 0
 EVX SP.FS
efststlt 0 0 0 1 0 0
 crD
 /
 /
 rA
 rB
 0 1 0 1 1
 0
 1 1 1
 0
 1
 EVX SP.FS
efststeq 0 0 0 1 0 0
 crD
 /
 /
 rA
 rB
 0 1 0 1 1
 0
 1 1 1
 1
 0
 EVX SP.FS
efdadd 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 0 1 1
 1
 0 0 0
 0
 0
 EVX SP.FD
efdsub 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 0 1 1
 1
 0 0 0
 0
 1
 EVX SP.FD
efdabs 0 0 0 1 0 0
 rD
 rA
 ///
 0 1 0 1 1
 1
 0 0 1
 0
 0
 EVX SP.FD
efdnabs 0 0 0 1 0 0
 rD
 rA
 ///
 0 1 0 1 1
 1
 0 0 1
 0
 1
 EVX SP.FD
efdneg 0 0 0 1 0 0
 rD
 rA
 ///
 0 1 0 1 1
 1
 0 0 1
 1
 0
 EVX SP.FD
efdmul 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 0 1 1
 1
 0 1 0
 0
 0
 EVX SP.FD
efddiv 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 0 1 1
 1
 0 1 0
 0
 1
 EVX SP.FD
efdcmpgt 0 0 0 1 0 0
 crD
 /
 /
 rA
 rB
 0 1 0 1 1
 1
 0 1 1
 0
 0
 EVX SP.FD
efdcmplt 0 0 0 1 0 0
 crD
 /
 /
 rA
 rB
 0 1 0 1 1
 1
 0 1 1
 0
 1
 EVX SP.FD
efdcmpeq 0 0 0 1 0 0
 crD
 /
 /
 rA
 rB
 0 1 0 1 1
 1
 0 1 1
 1
 0
 EVX SP.FD
efdcfs 0 0 0 1 0 0
 rD
 0
 0 0 0 0
 rB
 0 1 0 1 1
 1
 0 1 1
 1
 1
 EVX SP.FD
efdcfui 0 0 0 1 0 0
 rD
 ///
 rB
 0 1 0 1 1
 1
 1 0 0
 0
 0
 EVX SP.FD
efdcfsi 0 0 0 1 0 0
 rD
 ///
 rB
 0 1 0 1 1
 1
 1 0 0
 0
 1
 EVX SP.FD
efdcfuf 0 0 0 1 0 0
 rD
 ///
 rB
 0 1 0 1 1
 1
 1 0 0
 1
 0
 EVX SP.FD
efdcfsf 0 0 0 1 0 0
 rD
 ///
 rB
 0 1 0 1 1
 1
 1 0 0
 1
 1
 EVX SP.FD
efdctui 0 0 0 1 0 0
 rD
 ///
 rB
 0 1 0 1 1
 1
 1 0 1
 0
 0
 EVX SP.FD
efdctsi 0 0 0 1 0 0
 rD
 ///
 rB
 0 1 0 1 1
 1
 1 0 1
 0
 1
 EVX SP.FD
efdctuf 0 0 0 1 0 0
 rD
 ///
 rB
 0 1 0 1 1
 1
 1 0 1
 1
 0
 EVX SP.FD
efdctsf 0 0 0 1 0 0
 rD
 ///
 rB
 0 1 0 1 1
 1
 1 0 1
 1
 1
 EVX SP.FD
efdctuiz 0 0 0 1 0 0
 rD
 ///
 rB
 0 1 0 1 1
 1
 1 1 0
 0
 0
 EVX SP.FD
efdctsiz 0 0 0 1 0 0
 rD
 ///
 rB
 0 1 0 1 1
 1
 1 1 0
 1
 0
 EVX SP.FD
efdtstgt 0 0 0 1 0 0
 crD
 /
 /
 rA
 rB
 0 1 0 1 1
 1
 1 1 1
 0
 0
 EVX SP.FD
efdtstlt 0 0 0 1 0 0
 crD
 /
 /
 rA
 rB
 0 1 0 1 1
 1
 1 1 1
 0
 1
 EVX SP.FD
efdtsteq 0 0 0 1 0 0
 crD
 /
 /
 rA
 rB
 0 1 0 1 1
 1
 1 1 1
 1
 0
 EVX SP.FD
evlddx 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 1 0 0
 0
 0 0 0
 0
 0
 EVX SP
vaddsbs 0 0 0 1 0 0
 vD
 vA
 vB
 0 1 1 0 0
 0
 0 0 0
 0
 0
 VX
 V
1
evldd 0 0 0 1 0 0
 rD
 rA
 UIMM 1
 0 1 1 0 0
 0
 0 0 0
 0
 1
 EVX SP
evldwx 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 1 0 0
 0
 0 0 0
 1
 0
 EVX SP
vminsb 0 0 0 1 0 0
 vD
 vA
 vB
 0 1 1 0 0
 0
 0 0 0
 1
 0
 VX
 V
2
evldw 0 0 0 1 0 0
 rD
 rA
 UIMM 3
 0 1 1 0 0
 0
 0 0 0
 1
 1
 EVX SP
evldhx 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 1 0 0
 0
 0 0 1
 0
 0
 EVX SP
A-90
EREF: A Programmer’s Reference Manual for Freescale Power Architecture Processors, Rev. 1 (EIS 2.1)
Freescale Semiconductor
Instruction Set Listings
Table A-4. Instructions Sorted by Opcode (Binary) (continued)
Mnemonic
 0
 1
 2
 3
 4
 5
 6
 7
 8
 9
 10
 11
 12
 13 14 15 16 17
 18 19 20 21 22
 23 24
 25
 26
 27
 28
 29
 30
 31
 Form Category
vsrab 0 0 0 1 0 0
 vD
 vA
 vB
 0 1 1 0 0
 0
 0 0 1
 0
 0
 VX
 V
3
evldh 0 0 0 1 0 0
 rD
 rA
 UIMM 2
 0 1 1 0 0
 0
 0 0 1
 0
 1
 EVX SP
vcmpgtsb 0 0 0 1 0 0
 vD
 vA
 vB
 0 1 1 0 0
 0
 0 0 1
 1
 0
 VC
 V
evlhhesplatx 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 1 0 0
 0
 0 1 0
 0
 0
 EVX SP
vmulesb 0 0 0 1 0 0
 vD
 vA
 vB
 0 1 1 0 0
 0
 0 1 0
 0
 0
 VX
 V
2
evlhhesplat 0 0 0 1 0 0
 rD
 rA
 UIMM 2
 0 1 1 0 0
 0
 0 1 0
 0
 1
 EVX SP
vcfux 0 0 0 1 0 0
 vD
 UIMM
 vB
 0 1 1 0 0
 0
 0 1 0
 1
 0
 VX
 V
evlhhousplatx 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 1 0 0
 0
 0 1 1
 0
 0
 EVX SP
vspltisb 0 0 0 1 0 0
 vD
 SIMM
 ///
 0 1 1 0 0
 0
 0 1 1
 0
 0
 VX
 V
2
evlhhousplat 0 0 0 1 0 0
 rD
 rA
 UIMM 2
 0 1 1 0 0
 0
 0 1 1
 0
 1
 EVX SP
evlhhossplatx 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 1 0 0
 0
 0 1 1
 1
 0
 EVX SP
vpkpx 0 0 0 1 0 0
 vD
 vA
 vB
 0 1 1 0 0
 0
 0 1 1
 1
 0
 VX
 V
evlhhossplat 0 0 0 1 0 0
 rD
 rA
 UIMM 2
 0 1 1 0 0
 0
 0 1 1
 1
 1
 EVX SP
evlwhex 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 1 0 0
 0
 1 0 0
 0
 0
 EVX SP
2
evlwhe 0 0 0 1 0 0
 rD
 rA
 UIMM 2
 0 1 1 0 0
 0
 1 0 0
 0
 1
 EVX SP
evlwhoux 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 1 0 0
 0
 1 0 1
 0
 0
 EVX SP
evlwhou 0 0 0 1 0 0
 rD
 rA
 UIMM 2
 0 1 1 0 0
 0
 1 0 1
 0
 1
 EVX SP
evlwhosx 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 1 0 0
 0
 1 0 1
 1
 0
 EVX SP
2
evlwhos 0 0 0 1 0 0
 rD
 rA
 UIMM 2
 0 1 1 0 0
 0
 1 0 1
 1
 1
 EVX SP
evlwwsplatx 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 1 0 0
 0
 1 1 0
 0
 0
 EVX SP
3
evlwwsplat 0 0 0 1 0 0
 rD
 rA
 UIMM 3
 0 1 1 0 0
 0
 1 1 0
 0
 1
 EVX SP
evlwhsplatx 0 0 0 1 0 0
 rD
 rA
 rB
 0 1 1 0 0
 0
 1 1 1
 0
 0
 EVX SP
2
evlwhsplat 0 0 0 1 0 0
 rD
 rA
 UIMM 2
 0 1 1 0 0
 0
 1 1 1
 0
 1
 EVX SP
evstddx 0 0 0 1 0 0
 rS
 rA
 rB
 0 1 1 0 0
 1
 0 0 0
 0
 0
 EVX SP
evstdd 0 0 0 1 0 0
 rD
 rA
 UIMM 1
 0 1 1 0 0
 1
 0 0 0
 0
 1
 EVX SP
evstdwx 0 0 0 1 0 0
 rS
 rA
 rB
 0 1 1 0 0
 1
 0 0 0
 1
 0
 EVX SP
3
evstdw 0 0 0 1 0 0
 rS
 rA
 UIMM 3
 0 1 1 0 0
 1
 0 0 0
 1
 1
 EVX SP
evstdhx 0 0 0 1 0 0
 rS
 rA
 rB
 0 1 1 0 0
 1
 0 0 1
 0
 0
 EVX SP
2
evstdh 0 0 0 1 0 0
 rS
 rA
 UIMM 2
 0 1 1 0 0
 1
 0 0 1
 0
 1
 EVX SP
evstwhex 0 0 0 1 0 0
 rS
 rA
 rB
 0 1 1 0 0
 1
 1 0 0
 0
 0
 EVX SP
2
evstwhe 0 0 0 1 0 0
 rS
 rA
 UIMM 2
 0 1 1 0 0
 1
 1 0 0
 0
 1
 EVX SP
evstwhox 0 0 0 1 0 0
 rS
 rA
 rB
 0 1 1 0 0
 1
 1 0 1
 0
 0
 EVX SP
2
evstwho 0 0 0 1 0 0
 rS
 rA
 UIMM 2
 0 1 1 0 0
 1
 1 0 1
 0
 1
 EVX SP
evstwwex 0 0 0 1 0 0
 rS
 rA
 rB
 0 1 1 0 0
 1
 1 1 0
 0
 0
 EVX SP
evstwwe 0 0 0 1 0 0
 rS
 rA
 UIMM 3
 0 1 1 0 0
 1
 1 1 0
 0
 1
 EVX SP
EREF: A Programmer’s Reference Manual for Freescale Power Architecture Processors, Rev. 1 (EIS 2.1)
Freescale Semiconductor
A-91
Instruction Set Listings
Table A-4. Instructions Sorted by Opcode (Binary) (continued)
Mnemonic
 0
 1
 2
 3
 4
 5
 6
 7
 8
 9
 10
 11
 12
 13 14 15 16 17
 18 19 20 21 22
 23 24
 25
 26
 27
 28
 29
 30
 31
 Form Category
evstwwox 0 0 0 1 0 0
 rS
 rA
 rB
 0 1 1 0 0
 1
 1 1 1
 0
 0
 EVX SP
3
evstwwo 0 0 0 1 0 0
 rS
 rA
 UIMM 3
 0 1 1 0 0
 1
 1 1 1
 0
 1
 EVX SP
vaddshs 0 0 0 1 0 0
 vD
 vA
 vB
 0 1 1 0 1
 0
 0 0 0
 0
 0
 VX
 V
vminsh 0 0 0 1 0 0
 vD
 vA
 vB
 0 1 1 0 1
 0
 0 0 0
 1
 0
 VX
 V
vsrah 0 0 0 1 0 0
 vD
 vA
 vB
 0 1 1 0 1
 0
 0 0 1
 0
 0
 VX
 V
vcmpgtsh 0 0 0 1 0 0
 vD
 vA
 vB
 0 1 1 0 1
 0
 0 0 1
 1
 0
 VC
 V
vmulesh 0 0 0 1 0 0
 vD
 vA
 vB
 0 1 1 0 1
 0
 0 1 0
 0
 0
 VX
 V
vcfsx 0 0 0 1 0 0
 vD
 UIMM
 vB
 0 1 1 0 1
 0
 0 1 0
 1
 0
 VX
 V
vspltish 0 0 0 1 0 0
 vD
 SIMM
 ///
 0 1 1 0 1
 0
 0 1 1
 0
 0
 VX
 V
vupkhpx 0 0 0 1 0 0
 vD
 ///
 vB
 0 1 1 0 1
 0
 0 1 1
 1
 0
 VX
 V
vaddsws 0 0 0 1 0 0
 vD
 vA
 vB
 0 1 1 1 0
 0
 0 0 0
 0
 0
 VX
 V
vminsw 0 0 0 1 0 0
 vD
 vA
 vB
 0 1 1 1 0
 0
 0 0 0
 1
 0
 VX
 V
vsraw 0 0 0 1 0 0
 vD
 vA
 vB
 0 1 1 1 0
 0
 0 0 1
 0
 0
 VX
 V
vcmpgtsw 0 0 0 1 0 0
 vD
 vA
 vB
 0 1 1 1 0
 0
 0 0 1
 1
 0
 VC
 V
vctuxs 0 0 0 1 0 0
 vD
 UIMM
 vB
 0 1 1 1 0
 0
 0 1 0
 1
 0
 VX
 V
vspltisw 0 0 0 1 0 0
 vD
 SIMM
 ///
 0 1 1 1 0
 0
 0 1 1
 0
 0
 VX
 V
vcmpbfp 0 0 0 1 0 0
 vD
 vA
 vB
 0 1 1 1 1
 0
 0 0 1
 1
 0
 VC
 V
vctsxs 0 0 0 1 0 0
 vD
 UIMM
 vB
 0 1 1 1 1
 0
 0 1 0
 1
 0
 VX
 V
vupklpx 0 0 0 1 0 0
 vD
 ///
 vB
 0 1 1 1 1
 0
 0 1 1
 1
 0
 VX
 V
vsububm 0 0 0 1 0 0
 vD
 vA
 vB
 1 0 0 0 0
 0
 0 0 0
 0
 0
 VX
 V
vavgub 0 0 0 1 0 0
 vD
 vA
 vB
 1 0 0 0 0
 0
 0 0 0
 1
 0
 VX
 V
evmhessf 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 0
 0
 0 0 0
 1
 1
 EVX SP
vabsdub 0 0 0 1 0 0
 vD
 vA
 vB
 1 0 0 0 0
 0
 0 0 0
 1
 1
 VX
 V
vand 0 0 0 1 0 0
 vD
 vA
 vB
 1 0 0 0 0
 0
 0 0 1
 0
 0
 VX
 V
vcmpequb. 0 0 0 1 0 0
 vD
 vA
 vB
 1 0 0 0 0
 0
 0 0 1
 1
 0
 VC
 V
evmhossf 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 0
 0
 0 0 1
 1
 1
 EVX SP
evmheumi 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 0
 0
 0 1 0
 0
 0
 EVX SP
evmhesmi 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 0
 0
 0 1 0
 0
 1
 EVX SP
vmaxfp 0 0 0 1 0 0
 vD
 vA
 vB
 1 0 0 0 0
 0
 0 1 0
 1
 0
 VX
 V
evmhesmf 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 0
 0
 0 1 0
 1
 1
 EVX SP
evmhoumi 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 0
 0
 0 1 1
 0
 0
 EVX SP
vslo 0 0 0 1 0 0
 vD
 vA
 vB
 1 0 0 0 0
 0
 0 1 1
 0
 0
 VX
 V
evmhosmi 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 0
 0
 0 1 1
 0
 1
 EVX SP
evmhosmf 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 0
 0
 0 1 1
 1
 1
 EVX SP
evmhessfa 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 0
 1
 0 0 0
 1
 1
 EVX SP
A-92
EREF: A Programmer’s Reference Manual for Freescale Power Architecture Processors, Rev. 1 (EIS 2.1)
Freescale Semiconductor
Instruction Set Listings
Table A-4. Instructions Sorted by Opcode (Binary) (continued)
Mnemonic
 0
 1
 2
 3
 4
 5
 6
 7
 8
 9
 10
 11
 12
 13 14 15 16 17
 18 19 20 21 22
 23 24
 25
 26
 27
 28
 29
 30
 31
 Form Category
evmhossfa 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 0
 1
 0 0 1
 1
 1
 EVX SP
evmheumia 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 0
 1
 0 1 0
 0
 0
 EVX SP
evmhesmia 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 0
 1
 0 1 0
 0
 1
 EVX SP
evmhesmfa 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 0
 1
 0 1 0
 1
 1
 EVX SP
evmhoumia 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 0
 1
 0 1 1
 0
 0
 EVX SP
evmhosmia 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 0
 1
 0 1 1
 0
 1
 EVX SP
evmhosmfa 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 0
 1
 0 1 1
 1
 1
 EVX SP
vsubuhm 0 0 0 1 0 0
 vD
 vA
 vB
 1 0 0 0 1
 0
 0 0 0
 0
 0
 VX
 V
vavguh 0 0 0 1 0 0
 vD
 vA
 vB
 1 0 0 0 1
 0
 0 0 0
 1
 0
 VX
 V
vabsduh 0 0 0 1 0 0
 vD
 vA
 vB
 1 0 0 0 1
 0
 0 0 0
 1
 1
 VX
 V
vandc 0 0 0 1 0 0
 vD
 vA
 vB
 1 0 0 0 1
 0
 0 0 1
 0
 0
 VX
 V
vcmpequh. 0 0 0 1 0 0
 vD
 vA
 vB
 1 0 0 0 1
 0
 0 0 1
 1
 0
 VC
 V
evmwhssf 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 1
 0
 0 0 1
 1
 1
 EVX SP
evmwlumi 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 1
 0
 0 1 0
 0
 0
 EVX SP
vminfp 0 0 0 1 0 0
 vD
 vA
 vB
 1 0 0 0 1
 0
 0 1 0
 1
 0
 VX
 V
evmwhumi 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 1
 0
 0 1 1
 0
 0
 EVX SP
vsro 0 0 0 1 0 0
 vD
 vA
 vB
 1 0 0 0 1
 0
 0 1 1
 0
 0
 VX
 V
evmwhsmi 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 1
 0
 0 1 1
 0
 1
 EVX SP
evmwhsmf 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 1
 0
 0 1 1
 1
 1
 EVX SP
evmwssf 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 1
 0
 1 0 0
 1
 1
 EVX SP
evmwumi 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 1
 0
 1 1 0
 0
 0
 EVX SP
evmwsmi 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 1
 0
 1 1 0
 0
 1
 EVX SP
evmwsmf 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 1
 0
 1 1 0
 1
 1
 EVX SP
evmwhssfa 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 1
 1
 0 0 1
 1
 1
 EVX SP
evmwlumia 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 1
 1
 0 1 0
 0
 0
 EVX SP
evmwhumia 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 1
 1
 0 1 1
 0
 0
 EVX SP
evmwhsmia 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 1
 1
 0 1 1
 0
 1
 EVX SP
evmwhsmfa 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 1
 1
 0 1 1
 1
 1
 EVX SP
evmwssfa 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 1
 1
 1 0 0
 1
 1
 EVX SP
evmwumia 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 1
 1
 1 1 0
 0
 0
 EVX SP
evmwsmia 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 1
 1
 1 1 0
 0
 1
 EVX SP
evmwsmfa 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 0 1
 1
 1 1 0
 1
 1
 EVX SP
vsubuwm 0 0 0 1 0 0
 vD
 vA
 vB
 1 0 0 1 0
 0
 0 0 0
 0
 0
 VX
 V
vavguw 0 0 0 1 0 0
 vD
 vA
 vB
 1 0 0 1 0
 0
 0 0 0
 1
 0
 VX
 V
vabsduw 0 0 0 1 0 0
 vD
 vA
 vB
 1 0 0 1 0
 0
 0 0 0
 1
 1
 VX
 V
EREF: A Programmer’s Reference Manual for Freescale Power Architecture Processors, Rev. 1 (EIS 2.1)
Freescale Semiconductor
A-93
Instruction Set Listings
Table A-4. Instructions Sorted by Opcode (Binary) (continued)
Mnemonic
 0
 1
 2
 3
 4
 5
 6
 7
 8
 9
 10
 11
 12
 13 14 15 16 17
 18 19 20 21 22
 23 24
 25
 26
 27
 28
 29
 30
 31
 Form Category
vor 0 0 0 1 0 0
 vD
 vA
 vB
 1 0 0 1 0
 0
 0 0 1
 0
 0
 VX
 V
vcmpequw. 0 0 0 1 0 0
 vD
 vA
 vB
 1 0 0 1 0
 0
 0 0 1
 1
 0
 VC
 V
evaddusiaaw 0 0 0 1 0 0
 rD
 rA
 ///
 1 0 0 1 1
 0
 0 0 0
 0
 0
 EVX SP
evaddssiaaw 0 0 0 1 0 0
 rD
 rA
 ///
 1 0 0 1 1
 0
 0 0 0
 0
 1
 EVX SP
evsubfusiaaw 0 0 0 1 0 0
 rD
 rA
 ///
 1 0 0 1 1
 0
 0 0 0
 1
 0
 EVX SP
evsubfssiaaw 0 0 0 1 0 0
 rD
 rA
 ///
 1 0 0 1 1
 0
 0 0 0
 1
 1
 EVX SP
evmra 0 0 0 1 0 0
 rD
 rA
 ///
 1 0 0 1 1
 0
 0 0 1
 0
 0
 EVX SP
vxor 0 0 0 1 0 0
 vD
 vA
 vB
 1 0 0 1 1
 0
 0 0 1
 0
 0
 VX
 V
evdivws 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 1 1
 0
 0 0 1
 1
 0
 EVX SP
vcmpeqfp. 0 0 0 1 0 0
 vD
 vA
 vB
 1 0 0 1 1
 0
 0 0 1
 1
 0
 VC
 V
evdivwu 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 0 1 1
 0
 0 0 1
 1
 1
 EVX SP
evaddumiaaw 0 0 0 1 0 0
 rD
 rA
 ///
 1 0 0 1 1
 0
 0 1 0
 0
 0
 EVX SP
evaddsmiaaw 0 0 0 1 0 0
 rD
 rA
 ///
 1 0 0 1 1
 0
 0 1 0
 0
 1
 EVX SP
evsubfumiaaw 0 0 0 1 0 0
 rD
 rA
 ///
 1 0 0 1 1
 0
 0 1 0
 1
 0
 EVX SP
evsubfsmiaaw 0 0 0 1 0 0
 rD
 rA
 ///
 1 0 0 1 1
 0
 0 1 0
 1
 1
 EVX SP
evmheusiaaw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 0 0
 0
 0 0 0
 0
 0
 EVX SP
evmhessiaaw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 0 0
 0
 0 0 0
 0
 1
 EVX SP
vavgsb 0 0 0 1 0 0
 vD
 vA
 vB
 1 0 1 0 0
 0
 0 0 0
 1
 0
 VX
 V
evmhessfaaw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 0 0
 0
 0 0 0
 1
 1
 EVX SP
evmhousiaaw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 0 0
 0
 0 0 1
 0
 0
 EVX SP
vnor 0 0 0 1 0 0
 vD
 vA
 vB
 1 0 1 0 0
 0
 0 0 1
 0
 0
 VX
 V
evmhossiaaw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 0 0
 0
 0 0 1
 0
 1
 EVX SP
evmhossfaaw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 0 0
 0
 0 0 1
 1
 1
 EVX SP
evmheumiaaw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 0 0
 0
 0 1 0
 0
 0
 EVX SP
evmhesmiaaw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 0 0
 0
 0 1 0
 0
 1
 EVX SP
evmhesmfaaw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 0 0
 0
 0 1 0
 1
 1
 EVX SP
evmhoumiaaw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 0 0
 0
 0 1 1
 0
 0
 EVX SP
evmhosmiaaw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 0 0
 0
 0 1 1
 0
 1
 EVX SP
evmhosmfaaw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 0 0
 0
 0 1 1
 1
 1
 EVX SP
evmhegumiaa 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 0 0
 1
 0 1 0
 0
 0
 EVX SP
evmhegsmiaa 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 0 0
 1
 0 1 0
 0
 1
 EVX SP
evmhegsmfaa 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 0 0
 1
 0 1 0
 1
 1
 EVX SP
evmhogumiaa 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 0 0
 1
 0 1 1
 0
 0
 EVX SP
evmhogsmiaa 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 0 0
 1
 0 1 1
 0
 1
 EVX SP
evmhogsmfaa 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 0 0
 1
 0 1 1
 1
 1
 EVX SP
A-94
EREF: A Programmer’s Reference Manual for Freescale Power Architecture Processors, Rev. 1 (EIS 2.1)
Freescale Semiconductor
Instruction Set Listings
Table A-4. Instructions Sorted by Opcode (Binary) (continued)
Mnemonic
 0
 1
 2
 3
 4
 5
 6
 7
 8
 9
 10
 11
 12
 13 14 15 16 17
 18 19 20 21 22
 23 24
 25
 26
 27
 28
 29
 30
 31
 Form Category
evmwlusiaaw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 0 1
 0
 0 0 0
 0
 0
 EVX SP
evmwlssiaaw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 0 1
 0
 0 0 0
 0
 1
 EVX SP
vavgsh 0 0 0 1 0 0
 vD
 vA
 vB
 1 0 1 0 1
 0
 0 0 0
 1
 0
 VX
 V
evmwhssmaaw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 0 1
 0
 0 0 1
 0
 1
 EVX SP
evmwlumiaaw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 0 1
 0
 0 1 0
 0
 0
 EVX SP
evmwlsmiaaw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 0 1
 0
 0 1 0
 0
 1
 EVX SP
evmwssfaa 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 0 1
 0
 1 0 0
 1
 1
 EVX SP
evmwumiaa 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 0 1
 0
 1 1 0
 0
 0
 EVX SP
evmwsmiaa 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 0 1
 0
 1 1 0
 0
 1
 EVX SP
evmwsmfaa 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 0 1
 0
 1 1 0
 1
 1
 EVX SP
evmheusianw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 1 0
 0
 0 0 0
 0
 0
 EVX SP
vsubcuw 0 0 0 1 0 0
 vD
 vA
 vB
 1 0 1 1 0
 0
 0 0 0
 0
 0
 VX
 V
evmhessianw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 1 0
 0
 0 0 0
 0
 1
 EVX SP
vavgsw 0 0 0 1 0 0
 vD
 vA
 vB
 1 0 1 1 0
 0
 0 0 0
 1
 0
 VX
 V
evmhessfanw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 1 0
 0
 0 0 0
 1
 1
 EVX SP
evmhousianw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 1 0
 0
 0 0 1
 0
 0
 EVX SP
evmhossianw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 1 0
 0
 0 0 1
 0
 1
 EVX SP
evmhossfanw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 1 0
 0
 0 0 1
 1
 1
 EVX SP
evmheumianw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 1 0
 0
 0 1 0
 0
 0
 EVX SP
evmhesmianw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 1 0
 0
 0 1 0
 0
 1
 EVX SP
evmhesmfanw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 1 0
 0
 0 1 0
 1
 1
 EVX SP
evmhoumianw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 1 0
 0
 0 1 1
 0
 0
 EVX SP
evmhosmianw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 1 0
 0
 0 1 1
 0
 1
 EVX SP
evmhosmfanw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 1 0
 0
 0 1 1
 1
 1
 EVX SP
evmhegumian 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 1 0
 1
 0 1 0
 0
 0
 EVX SP
evmhegsmian 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 1 0
 1
 0 1 0
 0
 1
 EVX SP
evmhegsmfan 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 1 0
 1
 0 1 0
 1
 1
 EVX SP
evmhogumian 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 1 0
 1
 0 1 1
 0
 0
 EVX SP
evmhogsmian 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 1 0
 1
 0 1 1
 0
 1
 EVX SP
evmhogsmfan 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 1 0
 1
 0 1 1
 1
 1
 EVX SP
evmwlusianw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 1 1
 0
 0 0 0
 0
 0
 EVX SP
evmwlssianw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 1 1
 0
 0 0 0
 0
 1
 EVX SP
vcmpgefp. 0 0 0 1 0 0
 vD
 vA
 vB
 1 0 1 1 1
 0
 0 0 1
 1
 0
 VC
 V
evmwlumianw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 1 1
 0
 0 1 0
 0
 0
 EVX SP
evmwlsmianw 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 1 1
 0
 0 1 0
 0
 1
 EVX SP
EREF: A Programmer’s Reference Manual for Freescale Power Architecture Processors, Rev. 1 (EIS 2.1)
Freescale Semiconductor
A-95
Instruction Set Listings
Table A-4. Instructions Sorted by Opcode (Binary) (continued)
Mnemonic
 0
 1
 2
 3
 4
 5
 6
 7
 8
 9
 10
 11
 12
 13 14 15 16 17
 18 19 20 21 22
 23 24
 25
 26
 27
 28
 29
 30
 31
 Form Category
evmwssfan 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 1 1
 0
 1 0 0
 1
 1
 EVX SP
evmwumian 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 1 1
 0
 1 1 0
 0
 0
 EVX SP
evmwsmian 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 1 1
 0
 1 1 0
 0
 1
 EVX SP
evmwsmfan 0 0 0 1 0 0
 rD
 rA
 rB
 1 0 1 1 1
 0
 1 1 0
 1
 1
 EVX SP
vsububs 0 0 0 1 0 0
 vD
 vA
 vB
 1 1 0 0 0
 0
 0 0 0
 0
 0
 VX
 V
mfvscr 0 0 0 1 0 0
 vD
 ///
 ///
 1 1 0 0 0
 0
 0 0 1
 0
 0
 VX
 V
vcmpgtub. 0 0 0 1 0 0
 vD
 vA
 vB
 1 1 0 0 0
 0
 0 0 1
 1
 0
 VC
 V
vsum4ubs 0 0 0 1 0 0
 vD
 vA
 vB
 1 1 0 0 0
 0
 0 1 0
 0
 0
 VX
 V
vsubuhs 0 0 0 1 0 0
 vD
 vA
 vB
 1 1 0 0 1
 0
 0 0 0
 0
 0
 VX
 V
mtvscr 0 0 0 1 0 0
 ///
 ///
 vB
 1 1 0 0 1
 0
 0 0 1
 0
 0
 VX
 V
vcmpgtuh. 0 0 0 1 0 0
 vD
 vA
 vB
 1 1 0 0 1
 0
 0 0 1
 1
 0
 VC
 V
vsum4shs 0 0 0 1 0 0
 vD
 vA
 vB
 1 1 0 0 1
 0
 0 1 0
 0
 0
 VX
 V
vsubuws 0 0 0 1 0 0
 vD
 vA
 vB
 1 1 0 1 0
 0
 0 0 0
 0
 0
 VX
 V
vcmpgtuw. 0 0 0 1 0 0
 vD
 vA
 vB
 1 1 0 1 0
 0
 0 0 1
 1
 0
 VC
 V
vsum2sws 0 0 0 1 0 0
 vD
 vA
 vB
 1 1 0 1 0
 0
 0 1 0
 0
 0
 VX
 V
vcmpgtfp. 0 0 0 1 0 0
 vD
 vA
 vB
 1 1 0 1 1
 0
 0 0 1
 1
 0
 VC
 V
vsubsbs 0 0 0 1 0 0
 vD
 vA
 vB
 1 1 1 0 0
 0
 0 0 0
 0
 0
 VX
 V
vcmpgtsb. 0 0 0 1 0 0
 vD
 vA
 vB
 1 1 1 0 0
 0
 0 0 1
 1
 0
 VC
 V
vsum4sbs 0 0 0 1 0 0
 vD
 vA
 vB
 1 1 1 0 0
 0
 0 1 0
 0
 0
 VX
 V
vsubshs 0 0 0 1 0 0
 vD
 vA
 vB
 1 1 1 0 1
 0
 0 0 0
 0
 0
 VX
 V
vcmpgtsh. 0 0 0 1 0 0
 vD
 vA
 vB
 1 1 1 0 1
 0
 0 0 1
 1
 0
 VC
 V
vsubsws 0 0 0 1 0 0
 vD
 vA
 vB
 1 1 1 1 0
 0
 0 0 0
 0
 0
 VX
 V
vcmpgtsw. 0 0 0 1 0 0
 vD
 vA
 vB
 1 1 1 1 0
 0
 0 0 1
 1
 0
 VC
 V
vsumsws 0 0 0 1 0 0
 vD
 vA
 vB
 1 1 1 1 0
 0
 0 1 0
 0
 0
 VX
 V
vcmpbfp. 0 0 0 1 0 0
 vD
 vA
 vB
 1 1 1 1 1
 0
 0 0 1
 1
 0
 VC
 V
mulli 0 0 0 1 1 1
 rD
 rA
 SIMM
 D
subfic 0 0 1 0 0 0
 rD
 rA
 SIMM
 D
cmpli 0 0 1 0 1 0
 crD
 /
 L
 rA
 UIMM
 D
cmpi 0 0 1 0 1 1
 crD
 /
 L
 rA
 SIMM
 D
addic 0 0 1 1 0 0
 rD
 rA
 SIMM
 D
addic. 0 0 1 1 0 1
 rD
 rA
 SIMM
 D
addi 0 0 1 1 1 0
 rD
 rA
 SIMM
 D
addis 0 0 1 1 1 1
 rD
 rA
 SIMM
 D
bc 0 1 0 0 0 0
 BO
 BI
 BD
 0
 0
 B
bcl 0 1 0 0 0 0
 BO
 BI
 BD
 0
 1
 B
A-96
EREF: A Programmer’s Reference Manual for Freescale Power Architecture Processors, Rev. 1 (EIS 2.1)
Freescale Semiconductor
Instruction Set Listings
Table A-4. Instructions Sorted by Opcode (Binary) (continued)
Mnemonic
 0
 1
 2
 3
 4
 5
 6
 7
 8
 9
 10
 11
 12
 13 14 15 16 17
 18 19 20 21 22
 23 24
 25
 26
 27
 28
 29
 30
 31
 Form Category
bca 0 1 0 0 0 0
 BO
 BI
 BD
 1
 0
 B
bcla 0 1 0 0 0 0
 BO
 BI
 BD
 1
 1
 B
sc 0 1 0 0 0 1
 ///
 LEV
 ///
 1
 /
 SC
b 0 1 0 0 1 0
 LI
 0
 0
 I
bl 0 1 0 0 1 0
 LI
 0
 1
 I
ba 0 1 0 0 1 0
 LI
 1
 0
 I
bla 0 1 0 0 1 0
 LI
 1
 1
 I
mcrf 0 1 0 0 1 1
 crD
 //
 crfS
 ///
 0 0 0 0 0
 0
 0 0 0
 0
 /
 XL
bclr 0 1 0 0 1 1
 BO
 BI
 ///
 BH
 0 0 0 0 0
 1
 0 0 0
 0
 0
 XL
bclrl 0 1 0 0 1 1
 BO
 BI
 ///
 BH
 0 0 0 0 0
 1
 0 0 0
 0
 1
 XL
crnor 0 1 0 0 1 1
 crbD
 crbA
 crbB
 0 0 0 0 1
 0
 0 0 0
 1
 /
 XL
rfmci 0 1 0 0 1 1
 ///
 0 0 0 0 1
 0
 0 1 1
 0
 /
 XL
 Embedded
rfdi 0 1 0 0 1 1
 ///
 0 0 0 0 1
 0
 0 1 1
 1
 /
 X
 E.ED
rfi 0 1 0 0 1 1
 ///
 0 0 0 0 1
 1
 0 0 1
 0
 /
 XL
 Embedded
rfci 0 1 0 0 1 1
 ///
 0 0 0 0 1
 1
 0 0 1
 1
 /
 XL
 Embedded
rfgi 0 1 0 0 1 1
 ///
 0 0 0 1 1
 0
 0 1 1
 0
 /
 X
 E.HV
crandc 0 1 0 0 1 1
 crbD
 crbA
 crbB
 0 0 1 0 0
 0
 0 0 0
 1
 /
 XL
isync 0 1 0 0 1 1
 ///
 0 0 1 0 0
 1
 0 1 1
 0
 /
 XL
crxor 0 1 0 0 1 1
 crbD
 crbA
 crbB
 0 0 1 1 0
 0
 0 0 0
 1
 /
 XL
dnh 0 1 0 0 1 1
 DUI
 DCTL
 0 0 0 0 0 0 0 1 1 0
 0
 0 1 1
 0
 /
 X
 E.ED
crnand 0 1 0 0 1 1
 crbD
 crbA
 crbB
 0 0 1 1 1
 0
 0 0 0
 1
 /
 XL
crand 0 1 0 0 1 1
 crbD
 crbA
 crbB
 0 1 0 0 0
 0
 0 0 0
 1
 /
 XL
creqv 0 1 0 0 1 1
 crbD
 crbA
 crbB
 0 1 0 0 1
 0
 0 0 0
 1
 /
 XL
crorc 0 1 0 0 1 1
 crbD
 crbA
 crbB
 0 1 1 0 1
 0
 0 0 0
 1
 /
 XL
cror 0 1 0 0 1 1
 crbD
 crbA
 crbB
 0 1 1 1 0
 0
 0 0 0
 1
 /
 XL
bcctr 0 1 0 0 1 1
 BO
 BI
 ///
 BH
 1 0 0 0 0
 1
 0 0 0
 0
 0
 XL
bcctrl 0 1 0 0 1 1
 BO
 BI
 ///
 BH
 1 0 0 0 0
 1
 0 0 0
 0
 1
 XL
rlwimi 0 1 0 1 0 0
 rS
 rA
 SH
 MB
 ME
 0
 M
rlwimi. 0 1 0 1 0 0
 rS
 rA
 SH
 MB
 ME
 1
 M
rlwinm 0 1 0 1 0 1
 rS
 rA
 SH
 MB
 ME
 0
 M
rlwinm. 0 1 0 1 0 1
 rS
 rA
 SH
 MB
 ME
 1
 M
rlwnm 0 1 0 1 1 1
 rS
 rA
 rB
 MB
 ME
 0
 M
rlwnm. 0 1 0 1 1 1
 rS
 rA
 rB
 MB
 ME
 1
 M
ori 0 1 1 0 0 0
 rS
 rA
 UIMM
 D
oris 0 1 1 0 0 1
 rS
 rA
 UIMM
 D
EREF: A Programmer’s Reference Manual for Freescale Power Architecture Processors, Rev. 1 (EIS 2.1)
Freescale Semiconductor
A-97
Instruction Set Listings
Table A-4. Instructions Sorted by Opcode (Binary) (continued)
Mnemonic
 0
 1
 2
 3
 4
 5
 6
 7
 8
 9
 10
 11
 12
 13 14 15 16 17
 18 19 20 21 22
 23 24
 25
 26
 27
 28
 29
 30
 31
 Form Category
xori 0 1 1 0 1 0
 rS
 rA
 UIMM
 D
xoris 0 1 1 0 1 1
 rS
 rA
 UIMM
 D
andi. 0 1 1 1 0 0
 rS
 rA
 UIMM
 D
andis. 0 1 1 1 0 1
 rS
 rA
 UIMM
 D
rldicl 0 1 1 1 1 0
 rS
 rA
 sh1-5
 mb1-5
 mb0
 0
 0 0
 sh0
 0
 MD
 64
rldicl. 0 1 1 1 1 0
 rS
 rA
 sh1-5
 mb1-5
 mb0
 0
 0 0
 sh0
 1
 MD
 64
rldicr 0 1 1 1 1 0
 rS
 rA
 sh1-5
 me1-5
 me0
 0
 0 1
 sh0
 0
 MD
 64
rldicr. 0 1 1 1 1 0
 rS
 rA
 sh1-5
 me1-5
 me0
 0
 0 1
 sh0
 1
 MD
 64
rldic 0 1 1 1 1 0
 rS
 rA
 sh1-5
 mb1-5
 mb0
 0
 1 0
 sh0
 0
 MD
 64
rldic. 0 1 1 1 1 0
 rS
 rA
 sh1-5
 mb1-5
 mb0
 0
 1 0
 sh0
 1
 MD
 64
rldimi 0 1 1 1 1 0
 rS
 rA
 sh1-5
 mb1-5
 mb0
 0
 1 1
 sh0
 0
 MD
 64
rldimi. 0 1 1 1 1 0
 rS
 rA
 sh1-5
 mb1-5
 mb0
 0
 1 1
 sh0
 1
 MD
 64
rldcl 0 1 1 1 1 0
 rS
 rA
 rB
 mb1-5
 mb0
 1
 0 0
 0
 0
 MDS 64
rldcl. 0 1 1 1 1 0
 rS
 rA
 rB
 mb1-5
 mb0
 1
 0 0
 0
 1
 MDS 64
rldcr 0 1 1 1 1 0
 rS
 rA
 rB
 me1-5
 me0
 1
 0 0
 1
 0
 MDS 64
rldcr. 0 1 1 1 1 0
 rS
 rA
 rB
 me1-5
 me0
 1
 0 0
 1
 1
 MDS 64
cmp 0 1 1 1 1 1
 crD
 /
 L
 rA
 rB
 0 0 0 0 0
 0
 0 0 0
 0
 /
 X
tw 0 1 1 1 1 1
 TO
 rA
 rB
 0 0 0 0 0
 0
 0 1 0
 0
 /
 X
lvsl 0 1 1 1 1 1
 vD
 rA
 rB
 0 0 0 0 0
 0
 0 1 1
 0
 /
 X
 V
lvebx 0 1 1 1 1 1
 vD
 rA
 rB
 0 0 0 0 0
 0
 0 1 1
 1
 /
 X
 V
subfc 0 1 1 1 1 1
 rD
 rA
 rB
 0 0 0 0 0
 0
 1 0 0
 0
 0
 X
subfc. 0 1 1 1 1 1
 rD
 rA
 rB
 0 0 0 0 0
 0
 1 0 0
 0
 1
 X
mulhdu 0 1 1 1 1 1
 rD
 rA
 rB
 /
 0 0 0 0
 0
 1 0 0
 1
 0
 X
 64
mulhdu. 0 1 1 1 1 1
 rD
 rA
 rB
 /
 0 0 0 0
 0
 1 0 0
 1
 1
 X
 64
addc 0 1 1 1 1 1
 rD
 rA
 rB
 0 0 0 0 0
 0
 1 0 1
 0
 0
 X
addc. 0 1 1 1 1 1
 rD
 rA
 rB
 0 0 0 0 0
 0
 1 0 1
 0
 1
 X
mulhwu 0 1 1 1 1 1
 rD
 rA
 rB
 /
 0 0 0 0
 0
 1 0 1
 1
 0
 X
mulhwu. 0 1 1 1 1 1
 rD
 rA
 rB
 /
 0 0 0 0
 0
 1 0 1
 1
 1
 X
isel 0 1 1 1 1 1
 rD
 rA
 rB
 crb
 0
 1 1 1
 1
 0
 A
tlbilx 0 1 1 1 1 1
 0
 ///
 T
 rA
 rB
 0 0 0 0 0
 1
 0 0 1
 0
 /
 X
 Embedded
mfcr 0 1 1 1 1 1
 rD
 0
 ///
 0 0 0 0 0
 1
 0 0 1
 1
 /
 X
mfocrf 0 1 1 1 1 1
 rD
 1
 CRM
 /
 0 0 0 0 0
 1
 0 0 1
 1
 /
 X
lwarx 0 1 1 1 1 1
 rD
 rA
 rB
 0 0 0 0 0
 1
 0 1 0
 0
 /
 X
ldx 0 1 1 1 1 1
 rD
 rA
 rB
 0 0 0 0 0
 1
 0 1 0
 1
 /
 X
 64
icbt 0 1 1 1 1 1
 CT
 rA
 rB
 0 0 0 0 0
 1
 0 1 1
 0
 /
 X
 Embedded
A-98
EREF: A Programmer’s Reference Manual for Freescale Power Architecture Processors, Rev. 1 (EIS 2.1)
Freescale Semiconductor
Instruction Set Listings
Table A-4. Instructions Sorted by Opcode (Binary) (continued)
Mnemonic
 0
 1
 2
 3
 4
 5
 6
 7
 8
 9
 10
 11
 12
 13 14 15 16 17
 18 19 20 21 22
 23 24
 25
 26
 27
 28
 29
 30
 31
 Form Category
lwzx 0 1 1 1 1 1
 rD
 rA
 rB
 0 0 0 0 0
 1
 0 1 1
 1
 /
 X
slw 0 1 1 1 1 1
 rS
 rA
 rB
 0 0 0 0 0
 1
 1 0 0
 0
 0
 X
slw. 0 1 1 1 1 1
 rS
 rA
 rB
 0 0 0 0 0
 1
 1 0 0
 0
 1
 X
cntlzw 0 1 1 1 1 1
 rS
 rA
 ///
 0 0 0 0 0
 1
 1 0 1
 0
 0
 X
cntlzw. 0 1 1 1 1 1
 rS
 rA
 ///
 0 0 0 0 0
 1
 1 0 1
 0
 1
 X
sld 0 1 1 1 1 1
 rS
 rA
 rB
 0 0 0 0 0
 1
 1 0 1
 1
 0
 X
 64
sld. 0 1 1 1 1 1
 rS
 rA
 rB
 0 0 0 0 0
 1
 1 0 1
 1
 1
 X
 64
and 0 1 1 1 1 1
 rS
 rA
 rB
 0 0 0 0 0
 1
 1 1 0
 0
 0
 X
and. 0 1 1 1 1 1
 rS
 rA
 rB
 0 0 0 0 0
 1
 1 1 0
 0
 1
 X
ldepx 0 1 1 1 1 1
 rD
 rA
 rB
 0 0 0 0 0
 1
 1 1 0
 1
 /
 X
 E.PD, 64
lwepx 0 1 1 1 1 1
 rD
 rA
 rB
 0 0 0 0 0
 1
 1 1 1
 1
 /
 X
 E.PD
cmpl 0 1 1 1 1 1
 crfD
 /
 L
 rA
 rB
 0 0 0 0 1
 0
 0 0 0
 0
 /
 X
lvsr 0 1 1 1 1 1
 vD
 rA
 rB
 0 0 0 0 1
 0
 0 1 1
 0
 /
 X
 V
lvehx 0 1 1 1 1 1
 vD
 rA
 rB
 0 0 0 0 1
 0
 0 1 1
 1
 /
 X
 V
subf 0 1 1 1 1 1
 rD
 rA
 rB
 0 0 0 0 1
 0
 1 0 0
 0
 0
 X
subf. 0 1 1 1 1 1
 rD
 rA
 rB
 0 0 0 0 1
 0
 1 0 0
 0
 1
 X
mviwsplt 0 1 1 1 1 1
 vD
 rA
 rB
 0 0 0 0 1
 0
 1 1 1
 0
 /
 X
 V
lbarx 0 1 1 1 1 1
 rD
 rA
 rB
 0 0 0 0 1
 1
 0 1 0
 0
 /
 X
 ER
ldux 0 1 1 1 1 1
 rD
 rA
 rB
 0 0 0 0 1
 1
 0 1 0
 1
 /
 X
 64
dcbst 0 1 1 1 1 1
 ///
 rA
 rB
 0 0 0 0 1
 1
 0 1 1
 0
 /
 X
lwzux 0 1 1 1 1 1
 rD
 rA
 rB
 0 0 0 0 1
 1
 0 1 1
 1
 /
 X
cntlzd 0 1 1 1 1 1
 rS
 rA
 ///
 0 0 0 0 1
 1
 1 0 1
 0
 0
 X
 64
cntlzd. 0 1 1 1 1 1
 rS
 rA
 ///
 0 0 0 0 1
 1
 1 0 1
 0
 1
 X
 64
andc 0 1 1 1 1 1
 rS
 rA
 rB
 0 0 0 0 1
 1
 1 1 0
 0
 0
 X
andc. 0 1 1 1 1 1
 rS
 rA
 rB
 0 0 0 0 1
 1
 1 1 0
 0
 1
 X
wait 0 1 1 1 1 1
 ///
 WC
 WH
 ///
 0 0 0 0 1
 1
 1 1 1
 0
 /
 X
 WT
dcbstep 0 1 1 1 1 1
 ///
 rA
 rB
 0 0 0 0 1
 1
 1 1 1
 1
 /
 X
 E.PD
td 0 1 1 1 1 1
 TO
 rA
 rB
 0 0 0 1 0
 0
 0 1 0
 0
 /
 X
 64
lvewx 0 1 1 1 1 1
 vD
 rA
 rB
 0 0 0 1 0
 0
 0 1 1
 1
 /
 X
 V
mulhd 0 1 1 1 1 1
 rD
 rA
 rB
 /
 0 0 1 0
 0
 1 0 0
 1
 0
 X
 64
mulhd. 0 1 1 1 1 1
 rD
 rA
 rB
 /
 0 0 1 0
 0
 1 0 0
 1
 1
 X
 64
mulhw 0 1 1 1 1 1
 rD
 rA
 rB
 /
 0 0 1 0
 0
 1 0 1
 1
 0
 X
mulhw. 0 1 1 1 1 1
 rD
 rA
 rB
 /
 0 0 1 0
 0
 1 0 1
 1
 1
 X
mfmsr 0 1 1 1 1 1
 rD
 ///
 0 0 0 1 0
 1
 0 0 1
 1
 /
 X
ldarx 0 1 1 1 1 1
 rD
 rA
 rB
 0 0 0 1 0
 1
 0 1 0
 0
 /
 X
 64
EREF: A Programmer’s Reference Manual for Freescale Power Architecture Processors, Rev. 1 (EIS 2.1)
Freescale Semiconductor
A-99
Instruction Set Listings
Table A-4. Instructions Sorted by Opcode (Binary) (continued)
Mnemonic
 0
 1
 2
 3
 4
 5
 6
 7
 8
 9
 10
 11
 12
 13 14 15 16 17
 18 19 20 21 22
 23 24
 25
 26
 27
 28
 29
 30
 31
 Form Category
dcbf 0 1 1 1 1 1
 ///
 rA
 rB
 0 0 0 1 0
 1
 0 1 1
 0
 /
 X
lbzx 0 1 1 1 1 1
 rD
 rA
 rB
 0 0 0 1 0
 1
 0 1 1
 1
 /
 X
lbepx 0 1 1 1 1 1
 rD
 rA
 rB
 0 0 0 1 0
 1
 1 1 1
 1
 /
 X
 E.PD
dni 0 1 1 1 1 1
 DUI
 DCTL
 0 0 0 0 0 0 0 0 1 1
 0
 0 0 0
 1
 1
 X
 E.ED
lvx 0 1 1 1 1 1
 vD
 rA
 rB
 0 0 0 1 1
 0
 0 1 1
 1
 /
 X
 V
neg 0 1 1 1 1 1
 rD
 rA
 ///
 0 0 0 1 1
 0
 1 0 0
 0
 0
 X
neg. 0 1 1 1 1 1
 rD
 rA
 ///
 0 0 0 1 1
 0
 1 0 0
 0
 1
 X
mvidsplt 0 1 1 1 1 1
 vD
 rA
 rB
 0 0 0 1 1
 0
 1 1 1
 0
 /
 X
 V, 64
lharx 0 1 1 1 1 1
 rD
 rA
 rB
 0 0 0 1 1
 1
 0 1 0
 0
 /
 X
 ER
lbzux 0 1 1 1 1 1
 rD
 rA
 rB
 0 0 0 1 1
 1
 0 1 1
 1
 /
 X
popcntb 0 1 1 1 1 1
 rS
 rA
 ///
 0 0 0 1 1
 1
 1 0 1
 0
 /
 X
nor 0 1 1 1 1 1
 rS
 rA
 rB
 0 0 0 1 1
 1
 1 1 0
 0
 0
 X
nor. 0 1 1 1 1 1
 rS
 rA
 rB
 0 0 0 1 1
 1
 1 1 0
 0
 1
 X
dcbfep 0 1 1 1 1 1
 ///
 rA
 rB
 0 0 0 1 1
 1
 1 1 1
 1
 /
 X
 E.PD
wrtee 0 1 1 1 1 1
 rS
 ///
 0 0 1 0 0
 0
 0 0 1
 1
 /
 X
 Embedded
dcbtstls 0 1 1 1 1 1
 CT
 rA
 rB
 0 0 1 0 0
 0
 0 1 1
 0
 /
 X
 E.CL
stvebx 0 1 1 1 1 1
 vS
 rA
 rB
 0 0 1 0 0
 0
 0 1 1
 1
 /
 X
 V
subfe 0 1 1 1 1 1
 rD
 rA
 rB
 0 0 1 0 0
 0
 1 0 0
 0
 0
 X
subfe. 0 1 1 1 1 1
 rD
 rA
 rB
 0 0 1 0 0
 0
 1 0 0
 0
 1
 X
adde 0 1 1 1 1 1
 rD
 rA
 rB
 0 0 1 0 0
 0
 1 0 1
 0
 0
 X
adde. 0 1 1 1 1 1
 rD
 rA
 rB
 0 0 1 0 0
 0
 1 0 1
 0
 1
 X
mtcrf 0 1 1 1 1 1
 rS
 0
 CRM
 /
 0 0 1 0 0
 1
 0 0 0
 0
 /
 XFX
mtocrf 0 1 1 1 1 1
 rS
 1
 CRM
 /
 0 0 1 0 0
 1
 0 0 0
 0
 /
 XFX
mtmsr 0 1 1 1 1 1
 rS
 ///
 0 0 1 0 0
 1
 0 0 1
 0
 /
 X
stdx 0 1 1 1 1 1
 rS
 rA
 rB
 0 0 1 0 0
 1
 0 1 0
 1
 /
 X
 64
stwcx. 0 1 1 1 1 1
 rS
 rA
 rB
 0 0 1 0 0
 1
 0 1 1
 0
 1
 X
stwx 0 1 1 1 1 1
 rS
 rA
 rB
 0 0 1 0 0
 1
 0 1 1
 1
 /
 D
prtyw 0 1 1 1 1 1
 rS
 rA
 ///
 0 0 1 0 0
 1
 1 0 1
 0
 /
 X
stdepx 0 1 1 1 1 1
 rS
 rA
 rB
 0 0 1 0 0
 1
 1 1 0
 1
 /
 X
 E.PD, 64
stwepx 0 1 1 1 1 1
 rS
 rA
 rB
 0 0 1 0 0
 1
 1 1 1
 1
 /
 X
 E.PD
wrteei 0 1 1 1 1 1
 ///
 E
 ///
 0 0 1 0 1
 0
 0 0 1
 1
 /
 X
 Embedded
dcbtls 0 1 1 1 1 1
 CT
 rA
 rB
 0 0 1 0 1
 0
 0 1 1
 0
 /
 X
 E.CL
stvehx 0 1 1 1 1 1
 vS
 rA
 rB
 0 0 1 0 1
 0
 0 1 1
 1
 /
 X
 V
stdux 0 1 1 1 1 1
 rS
 rA
 rB
 0 0 1 0 1
 1
 0 1 0
 1
 /
 X
 64
stwux 0 1 1 1 1 1
 rS
 rA
 rB
 0 0 1 0 1
 1
 0 1 1
 1
 /
 D
A-100
EREF: A Programmer’s Reference Manual for Freescale Power Architecture Processors, Rev. 1 (EIS 2.1)
Freescale Semiconductor
Instruction Set Listings
Table A-4. Instructions Sorted by Opcode (Binary) (continued)
Mnemonic
 0
 1
 2
 3
 4
 5
 6
 7
 8
 9
 10
 11
 12
 13 14 15 16 17
 18 19 20 21 22
 23 24
 25
 26
 27
 28
 29
 30
 31
 Form Category
prtyd 0 1 1 1 1 1
 rS
 rA
 ///
 0 0 1 0 1
 1
 1 0 1
 0
 /
 X
 64
icblq. 0 1 1 1 1 1
 CT
 rA
 rB
 0 0 1 1 0
 0
 0 1 1
 0
 /
 X
 E.CL
stvewx 0 1 1 1 1 1
 vS
 rA
 rB
 0 0 1 1 0
 0
 0 1 1
 1
 /
 X
 V
subfze 0 1 1 1 1 1
 rD
 rA
 ///
 0 0 1 1 0
 0
 1 0 0
 0
 0
 X
subfze. 0 1 1 1 1 1
 rD
 rA
 ///
 0 0 1 1 0
 0
 1 0 0
 0
 1
 X
addze 0 1 1 1 1 1
 rD
 rA
 ///
 0 0 1 1 0
 0
 1 0 1
 0
 0
 X
addze. 0 1 1 1 1 1
 rD
 rA
 ///
 0 0 1 1 0
 0
 1 0 1
 0
 1
 X
msgsnd 0 1 1 1 1 1
 ///
 ///
 rB
 0 0 1 1 0
 0
 1 1 1
 0
 /
 X
 E.PC
stdcx. 0 1 1 1 1 1
 rS
 rA
 rB
 0 0 1 1 0
 1
 0 1 1
 0
 1
 X
 64
stbx 0 1 1 1 1 1
 rS
 rA
 rB
 0 0 1 1 0
 1
 0 1 1
 1
 /
 X
stbepx 0 1 1 1 1 1
 rS
 rA
 rB
 0 0 1 1 0
 1
 1 1 1
 1
 /
 X
 E.PD
icblc 0 1 1 1 1 1
 CT
 rA
 rB
 0 0 1 1 1
 0
 0 1 1
 0
 /
 X
 E.CL
stvx 0 1 1 1 1 1
 vS
 rA
 rB
 0 0 1 1 1
 0
 0 1 1
 1
 /
 X
 V
subfme 0 1 1 1 1 1
 rD
 rA
 ///
 0 0 1 1 1
 0
 1 0 0
 0
 0
 X
subfme. 0 1 1 1 1 1
 rD
 rA
 ///
 0 0 1 1 1
 0
 1 0 0
 0
 1
 X
mulld 0 1 1 1 1 1
 rD
 rA
 rB
 0 0 1 1 1
 0
 1 0 0
 1
 0
 X
 64
mulld. 0 1 1 1 1 1
 rD
 rA
 rB
 0 0 1 1 1
 0
 1 0 0
 1
 1
 X
 64
addme 0 1 1 1 1 1
 rD
 rA
 ///
 0 0 1 1 1
 0
 1 0 1
 0
 0
 X
addme. 0 1 1 1 1 1
 rD
 rA
 ///
 0 0 1 1 1
 0
 1 0 1
 0
 1
 X
mullw 0 1 1 1 1 1
 rD
 rA
 rB
 0 0 1 1 1
 0
 1 0 1
 1
 0
 X
mullw. 0 1 1 1 1 1
 rD
 rA
 rB
 0 0 1 1 1
 0
 1 0 1
 1
 1
 X
msgclr 0 1 1 1 1 1
 ///
 ///
 rB
 0 0 1 1 1
 0
 1 1 1
 0
 /
 X
 E.PC
dcbtst 0 1 1 1 1 1
 TH
 rA
 rB
 0 0 1 1 1
 1
 0 1 1
 0
 /
 X
stbux 0 1 1 1 1 1
 rS
 rA
 rB
 0 0 1 1 1
 1
 0 1 1
 1
 /
 X
bpermd 0 1 1 1 1 1
 rS
 rA
 rB
 0 0 1 1 1
 1
 1 1 0
 0
 /
 X
 64
dcbtstep 0 1 1 1 1 1
 TH
 rA
 rB
 0 0 1 1 1
 1
 1 1 1
 1
 /
 X
 E.PD
lvexbx 0 1 1 1 1 1
 vD
 rA
 rB
 0 1 0 0 0
 0
 0 1 0
 1
 /
 X
 V
lvepxl 0 1 1 1 1 1
 vD
 rA
 rB
 0 1 0 0 0
 0
 0 1 1
 1
 /
 X
 E.PD, V
sat 0 1 1 1 1 1
 rD
 rA
 SS
 IU
 OU
 SA
 0 1 0 0 0
 0
 1 0 0
 0
 0
 X
 ISAT
sat. 0 1 1 1 1 1
 rD
 rA
 SS
 IU
 OU
 SA
 0 1 0 0 0
 0
 1 0 0
 0
 1
 X
 ISAT
add 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 0 0 0
 0
 1 0 1
 0
 0
 X
add. 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 0 0 0
 0
 1 0 1
 0
 1
 X
ehpriv 0 1 1 1 1 1
 OC
 0 1 0 0 0
 0
 1 1 1
 0
 /
 XL
 E.HV
dcbt 0 1 1 1 1 1
 TH
 rA
 rB
 0 1 0 0 0
 1
 0 1 1
 0
 /
 X
lhzx 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 0 0 0
 1
 0 1 1
 1
 /
 X
EREF: A Programmer’s Reference Manual for Freescale Power Architecture Processors, Rev. 1 (EIS 2.1)
Freescale Semiconductor
A-101
Instruction Set Listings
Table A-4. Instructions Sorted by Opcode (Binary) (continued)
Mnemonic
 0
 1
 2
 3
 4
 5
 6
 7
 8
 9
 10
 11
 12
 13 14 15 16 17
 18 19 20 21 22
 23 24
 25
 26
 27
 28
 29
 30
 31
 Form Category
eqv 0 1 1 1 1 1
 rS
 rA
 rB
 0 1 0 0 0
 1
 1 1 0
 0
 0
 X
eqv. 0 1 1 1 1 1
 rS
 rA
 rB
 0 1 0 0 0
 1
 1 1 0
 0
 1
 X
lhepx 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 0 0 0
 1
 1 1 1
 1
 /
 X
 E.PD
lvexhx 0 1 1 1 1 1
 vD
 rA
 rB
 0 1 0 0 1
 0
 0 1 0
 1
 /
 X
 V
lvepx 0 1 1 1 1 1
 vD
 rA
 rB
 0 1 0 0 1
 0
 0 1 1
 1
 /
 X
 E.PD, V
mulhss 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 0 0 1
 0
 1 0 1
 1
 0
 X
 ISAT
mulhss. 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 0 0 1
 0
 1 0 1
 1
 1
 X
 ISAT
lhzux 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 0 0 1
 1
 0 1 1
 1
 /
 X
xor 0 1 1 1 1 1
 rS
 rA
 rB
 0 1 0 0 1
 1
 1 1 0
 0
 0
 X
xor. 0 1 1 1 1 1
 rS
 rA
 rB
 0 1 0 0 1
 1
 1 1 0
 0
 1
 X
dcbtep 0 1 1 1 1 1
 TH
 rA
 rB
 0 1 0 0 1
 1
 1 1 1
 1
 /
 X
 E.PD
mfdcr 0 1 1 1 1 1
 rD
 DCRN5-9
 DCRN0-4
 0 1 0 1 0
 0
 0 0 1
 1
 /
 XFX E.DC
lvexwx 0 1 1 1 1 1
 vD
 rA
 rB
 0 1 0 1 0
 0
 0 1 0
 1
 /
 X
 V
subfw 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 0 1 0
 0
 1 0 0
 0
 0
 X
 64
subfw. 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 0 1 0
 0
 1 0 0
 0
 1
 X
 64
addw 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 0 1 0
 0
 1 0 1
 0
 0
 X
 64
addw. 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 0 1 0
 0
 1 0 1
 0
 1
 X
 64
mfpmr 0 1 1 1 1 1
 rD
 PMRN5-9
 PMRN0-4
 0 1 0 1 0
 0
 1 1 1
 0
 /
 XFX E.PM
mfspr 0 1 1 1 1 1
 rD
 SPRN5-9
 SPRN0-4
 0 1 0 1 0
 1
 0 0 1
 1
 /
 XFX
lwax 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 0 1 0
 1
 0 1 0
 1
 /
 X
 64
dst 0 1 1 1 1 1
 0
 //
 STRM
 rA
 rB
 0 1 0 1 0
 1
 0 1 1
 0
 /
 X
 V
dstt 0 1 1 1 1 1
 1
 //
 STRM
 rA
 rB
 0 1 0 1 0
 1
 0 1 1
 0
 /
 X
 V
lhax 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 0 1 0
 1
 0 1 1
 1
 /
 X
lvxl 0 1 1 1 1 1
 vD
 rA
 rB
 0 1 0 1 1
 0
 0 1 1
 1
 /
 X
 V
subfwss 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 0 1 1
 0
 1 0 0
 0
 0
 X
 ISAT
subfwss. 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 0 1 1
 0
 1 0 0
 0
 1
 X
 ISAT
addwss 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 0 1 1
 0
 1 0 1
 0
 0
 X
 ISAT
addwss. 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 0 1 1
 0
 1 0 1
 0
 1
 X
 ISAT
mulwss 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 0 1 1
 0
 1 0 1
 1
 0
 X
 ISAT
mulwss. 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 0 1 1
 0
 1 0 1
 1
 1
 X
 ISAT
mftmr 0 1 1 1 1 1
 rD
 TMRN5-9
 TMRN0-4
 0 1 0 1 1
 0
 1 1 1
 0
 /
 XFX EM.TM
mftb 0 1 1 1 1 1
 rD
 TBRN5-9
 TBRN0-4
 0 1 0 1 1
 1
 0 0 1
 1
 0
 XFX
lwaux 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 0 1 1
 1
 0 1 0
 1
 /
 X
 64
dstst 0 1 1 1 1 1
 0
 //
 STRM
 rA
 rB
 0 1 0 1 1
 1
 0 1 1
 0
 /
 X
 V
dststt 0 1 1 1 1 1
 1
 //
 STRM
 rA
 rB
 0 1 0 1 1
 1
 0 1 1
 0
 /
 X
 V
A-102
EREF: A Programmer’s Reference Manual for Freescale Power Architecture Processors, Rev. 1 (EIS 2.1)
Freescale Semiconductor
Instruction Set Listings
Table A-4. Instructions Sorted by Opcode (Binary) (continued)
Mnemonic
 0
 1
 2
 3
 4
 5
 6
 7
 8
 9
 10
 11
 12
 13 14 15 16 17
 18 19 20 21 22
 23 24
 25
 26
 27
 28
 29
 30
 31
 Form Category
lhaux 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 0 1 1
 1
 0 1 1
 1
 /
 X
popcntw 0 1 1 1 1 1
 rS
 rA
 ///
 0 1 0 1 1
 1
 1 0 1
 0
 /
 X
stvexbx 0 1 1 1 1 1
 vS
 rA
 rB
 0 1 1 0 0
 0
 0 1 0
 1
 /
 X
 V
dcblc 0 1 1 1 1 1
 CT
 rA
 rB
 0 1 1 0 0
 0
 0 1 1
 0
 /
 X
 E.CL
subfh 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 1 0 0
 0
 1 0 0
 0
 0
 X
subfh. 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 1 0 0
 0
 1 0 0
 0
 1
 X
addh 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 1 0 0
 0
 1 0 1
 0
 0
 X
addh. 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 1 0 0
 0
 1 0 1
 0
 1
 X
divweu 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 1 0 0
 0
 1 0 1
 1
 0
 XO
divweu. 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 1 0 0
 0
 1 0 1
 1
 1
 XO
sthx 0 1 1 1 1 1
 rS
 rA
 rB
 0 1 1 0 0
 1
 0 1 1
 1
 /
 X
orc 0 1 1 1 1 1
 rS
 rA
 rB
 0 1 1 0 0
 1
 1 1 0
 0
 0
 X
orc. 0 1 1 1 1 1
 rS
 rA
 rB
 0 1 1 0 0
 1
 1 1 0
 0
 1
 X
sthepx 0 1 1 1 1 1
 rS
 rA
 rB
 0 1 1 0 0
 1
 1 1 1
 1
 /
 X
 E.PD
stvexhx 0 1 1 1 1 1
 vS
 rA
 rB
 0 1 1 0 1
 0
 0 1 0
 1
 /
 X
 V
dcblq. 0 1 1 1 1 1
 CT
 rA
 rB
 0 1 1 0 1
 0
 0 1 1
 0
 1
 X
 E.CL
subfhss 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 1 0 1
 0
 1 0 0
 0
 0
 X
 ISAT
subfhss. 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 1 0 1
 0
 1 0 0
 0
 1
 X
 ISAT
addhss 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 1 0 1
 0
 1 0 1
 0
 0
 X
 ISAT
addhss. 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 1 0 1
 0
 1 0 1
 0
 1
 X
 ISAT
divwe 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 1 0 1
 0
 1 0 1
 1
 0
 XO
divwe. 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 1 0 1
 0
 1 0 1
 1
 1
 XO
sthux 0 1 1 1 1 1
 rS
 rA
 rB
 0 1 1 0 1
 1
 0 1 1
 1
 /
 X
miso 0 1 1 1 1 1
 1 1 0 1 0
 1
 1 0 1 0 1 1 0 1 0 0 1 1 0 1
 1
 1 1 0
 0
 0
 X
or 0 1 1 1 1 1
 rS
 rA
 rB
 0 1 1 0 1
 1
 1 1 0
 0
 0
 X
or. 0 1 1 1 1 1
 rS
 rA
 rB
 0 1 1 0 1
 1
 1 1 0
 0
 1
 X
mtdcr 0 1 1 1 1 1
 rS
 DCRN5-9
 DCRN0-4
 0 1 1 1 0
 0
 0 0 1
 1
 /
 XFX E.DC
stvexwx 0 1 1 1 1 1
 vS
 rA
 rB
 0 1 1 1 0
 0
 0 1 0
 1
 /
 X
 V
subfb 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 1 1 0
 0
 1 0 0
 0
 0
 X
subfb. 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 1 1 0
 0
 1 0 0
 0
 1
 X
divdu 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 1 1 0
 0
 1 0 0
 1
 0
 X
 64
divdu. 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 1 1 0
 0
 1 0 0
 1
 1
 X
 64
addb 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 1 1 0
 0
 1 0 1
 0
 0
 X
addb. 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 1 1 0
 0
 1 0 1
 0
 1
 X
divwu 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 1 1 0
 0
 1 0 1
 1
 0
 X
EREF: A Programmer’s Reference Manual for Freescale Power Architecture Processors, Rev. 1 (EIS 2.1)
Freescale Semiconductor
A-103
Instruction Set Listings
Table A-4. Instructions Sorted by Opcode (Binary) (continued)
Mnemonic
 0
 1
 2
 3
 4
 5
 6
 7
 8
 9
 10
 11
 12
 13 14 15 16 17
 18 19 20 21 22
 23 24
 25
 26
 27
 28
 29
 30
 31
 Form Category
divwu. 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 1 1 0
 0
 1 0 1
 1
 1
 X
mtpmr 0 1 1 1 1 1
 rS
 PMRN5-9
 PMRN0-4
 0 1 1 1 0
 0
 1 1 1
 0
 /
 XFX E.PM
mtspr 0 1 1 1 1 1
 rS
 SPRN5-9
 SPRN0-4
 0 1 1 1 0
 1
 0 0 1
 1
 /
 XFX
dcbi 0 1 1 1 1 1
 ///
 rA
 rB
 0 1 1 1 0
 1
 0 1 1
 0
 /
 X
 Embedded
nand 0 1 1 1 1 1
 rS
 rA
 rB
 0 1 1 1 0
 1
 1 1 0
 0
 0
 X
nand. 0 1 1 1 1 1
 rS
 rA
 rB
 0 1 1 1 0
 1
 1 1 0
 0
 1
 X
dsn 0 1 1 1 1 1
 ///
 rA
 rB
 0 1 1 1 1
 0
 0 0 1
 1
 /
 X
 DS
icbtls 0 1 1 1 1 1
 CT
 rA
 rB
 0 1 1 1 1
 0
 0 1 1
 0
 /
 X
 E.CL
stvxl 0 1 1 1 1 1
 vS
 rA
 rB
 0 1 1 1 1
 0
 0 1 1
 1
 /
 X
 V
subfbss 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 1 1 1
 0
 1 0 0
 0
 0
 X
 ISAT
subfbss. 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 1 1 1
 0
 1 0 0
 0
 1
 X
 ISAT
divd 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 1 1 1
 0
 1 0 0
 1
 0
 X
 64
divd. 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 1 1 1
 0
 1 0 0
 1
 1
 X
 64
addbss 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 1 1 1
 0
 1 0 1
 0
 0
 X
 ISAT
addbss. 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 1 1 1
 0
 1 0 1
 0
 1
 X
 ISAT
divw 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 1 1 1
 0
 1 0 1
 1
 0
 X
divw. 0 1 1 1 1 1
 rD
 rA
 rB
 0 1 1 1 1
 0
 1 0 1
 1
 1
 X
mttmr 0 1 1 1 1 1
 rS
 TMRN5-9
 TMRN0-4
 0 1 1 1 1
 0
 1 1 1
 0
 /
 XFX EM.TM
popcntd 0 1 1 1 1 1
 rS
 rA
 ///
 0 1 1 1 1
 1
 1 0 1
 0
 /
 X
 64
cmpb 0 1 1 1 1 1
 rS
 rA
 rB
 0 1 1 1 1
 1
 1 1 0
 0
 /
 X
mcrxr 0 1 1 1 1 1
 crD
 ///
 1 0 0 0 0
 0
 0 0 0
 0
 /
 X
lbdx 0 1 1 1 1 1
 rD
 rA
 rB
 1 0 0 0 0
 0
 0 0 1
 1
 /
 X
 DS
subfco 0 1 1 1 1 1
 rD
 rA
 rB
 1 0 0 0 0
 0
 1 0 0
 0
 0
 X
subfco. 0 1 1 1 1 1
 rD
 rA
 rB
 1 0 0 0 0
 0
 1 0 0
 0
 1
 X
addco 0 1 1 1 1 1
 rD
 rA
 rB
 1 0 0 0 0
 0
 1 0 1
 0
 0
 X
addco. 0 1 1 1 1 1
 rD
 rA
 rB
 1 0 0 0 0
 0
 1 0 1
 0
 1
 X
ldbrx 0 1 1 1 1 1
 rD
 rA
 rB
 1 0 0 0 0
 1
 0 1 0
 0
 /
 X
 64
lwbrx 0 1 1 1 1 1
 rD
 rA
 rB
 1 0 0 0 0
 1
 0 1 1
 0
 /
 X
lfsx 0 1 1 1 1 1
 frD
 rA
 rB
 1 0 0 0 0
 1
 0 1 1
 1
 /
 X
srw 0 1 1 1 1 1
 rS
 rA
 rB
 1 0 0 0 0
 1
 1 0 0
 0
 0
 X
srw. 0 1 1 1 1 1
 rS
 rA
 rB
 1 0 0 0 0
 1
 1 0 0
 0
 1
 X
srd 0 1 1 1 1 1
 rS
 rA
 rB
 1 0 0 0 0
 1
 1 0 1
 1
 0
 X
 64
srd. 0 1 1 1 1 1
 rS
 rA
 rB
 1 0 0 0 0
 1
 1 0 1
 1
 1
 X
 64
lhdx 0 1 1 1 1 1
 rD
 rA
 rB
 1 0 0 0 1
 0
 0 0 1
 0
 /
 X
 DS
lvtrx 0 1 1 1 1 1
 vD
 rA
 rB
 1 0 0 0 1
 0
 0 1 0
 1
 /
 X
 V
A-104
EREF: A Programmer’s Reference Manual for Freescale Power Architecture Processors, Rev. 1 (EIS 2.1)
Freescale Semiconductor
Instruction Set Listings
Table A-4. Instructions Sorted by Opcode (Binary) (continued)
Mnemonic
 0
 1
 2
 3
 4
 5
 6
 7
 8
 9
 10
 11
 12
 13 14 15 16 17
 18 19 20 21 22
 23 24
 25
 26
 27
 28
 29
 30
 31
 Form Category
subfo 0 1 1 1 1 1
 rD
 rA
 rB
 1 0 0 0 1
 0
 1 0 0
 0
 0
 X
subfo. 0 1 1 1 1 1
 rD
 rA
 rB
 1 0 0 0 1
 0
 1 0 0
 0
 1
 X
tlbsync 0 1 1 1 1 1
 0
 ///
 1 0 0 0 1
 1
 0 1 1
 0
 /
 X
 Embedded
lfsux 0 1 1 1 1 1
 frD
 rA
 rB
 1 0 0 0 1
 1
 0 1 1
 1
 /
 X
 FP
lwdx 0 1 1 1 1 1
 rD
 rA
 rB
 1 0 0 1 0
 0
 0 0 1
 1
 /
 X
 DS
lvtlx 0 1 1 1 1 1
 vD
 rA
 rB
 1 0 0 1 0
 0
 0 1 0
 1
 /
 X
 V
sync 0 1 1 1 1 1
 ///
 L
 /
 ///
 E
 ///
 1 0 0 1 0
 1
 0 1 1
 0
 /
 X
lfdx 0 1 1 1 1 1
 frD
 rA
 rB
 1 0 0 1 0
 1
 0 1 1
 1
 /
 X
 FP
lfdepx 0 1 1 1 1 1
 frD
 rA
 rB
 1 0 0 1 0
 1
 1 1 1
 1
 /
 X
 E.PD, FP
lddx 0 1 1 1 1 1
 rD
 rA
 rB
 1 0 0 1 1
 0
 0 0 1
 1
 /
 X
 DS, 64
lvswx 0 1 1 1 1 1
 vD
 rA
 rB
 1 0 0 1 1
 0
 0 1 0
 1
 /
 X
 V
nego 0 1 1 1 1 1
 rD
 rA
 ///
 1 0 0 1 1
 0
 1 0 0
 0
 0
 X
nego. 0 1 1 1 1 1
 rD
 rA
 ///
 1 0 0 1 1
 0
 1 0 0
 0
 1
 X
lfdux 0 1 1 1 1 1
 frD
 rA
 rB
 1 0 0 1 1
 1
 0 1 1
 1
 /
 X
 FP
stbdx 0 1 1 1 1 1
 rS
 rA
 rB
 1 0 1 0 0
 0
 0 0 1
 1
 /
 X
 DS
subfeo 0 1 1 1 1 1
 rD
 rA
 rB
 1 0 1 0 0
 0
 1 0 0
 0
 0
 X
subfeo. 0 1 1 1 1 1
 rD
 rA
 rB
 1 0 1 0 0
 0
 1 0 0
 0
 1
 X
addeo 0 1 1 1 1 1
 rD
 rA
 rB
 1 0 1 0 0
 0
 1 0 1
 0
 0
 X
addeo. 0 1 1 1 1 1
 rD
 rA
 rB
 1 0 1 0 0
 0
 1 0 1
 0
 1
 X
stdbrx 0 1 1 1 1 1
 rS
 rA
 rB
 1 0 1 0 0
 1
 0 1 0
 0
 /
 X
 64
stwbrx 0 1 1 1 1 1
 rS
 rA
 rB
 1 0 1 0 0
 1
 0 1 1
 0
 /
 X
stfsx 0 1 1 1 1 1
 frS
 rA
 rB
 1 0 1 0 0
 1
 0 1 1
 1
 /
 X
 FP
sthdx 0 1 1 1 1 1
 rS
 rA
 rB
 1 0 1 0 1
 0
 0 0 1
 1
 /
 X
 DS
stvfrx 0 1 1 1 1 1
 vS
 rA
 rB
 1 0 1 0 1
 0
 0 1 0
 1
 /
 X
 V
stbcx. 0 1 1 1 1 1
 rS
 rA
 rB
 1 0 1 0 1
 1
 0 1 1
 0
 1
 X
 ER
stfsux 0 1 1 1 1 1
 frS
 rA
 rB
 1 0 1 0 1
 1
 0 1 1
 1
 /
 X
 FP
stwdx 0 1 1 1 1 1
 rS
 rA
 rB
 1 0 1 1 0
 0
 0 0 1
 1
 /
 X
 DS
stvflx 0 1 1 1 1 1
 vS
 rA
 rB
 1 0 1 1 0
 0
 0 1 0
 1
 /
 X
 V
subfzeo 0 1 1 1 1 1
 rD
 rA
 ///
 1 0 1 1 0
 0
 1 0 0
 0
 0
 X
subfzeo. 0 1 1 1 1 1
 rD
 rA
 ///
 1 0 1 1 0
 0
 1 0 0
 0
 1
 X
addzeo 0 1 1 1 1 1
 rD
 rA
 ///
 1 0 1 1 0
 0
 1 0 1
 0
 0
 X
addzeo. 0 1 1 1 1 1
 rD
 rA
 ///
 1 0 1 1 0
 0
 1 0 1
 0
 1
 X
sthcx. 0 1 1 1 1 1
 rS
 rA
 rB
 1 0 1 1 0
 1
 0 1 1
 0
 1
 X
 ER
stfdx 0 1 1 1 1 1
 frS
 rA
 rB
 1 0 1 1 0
 1
 0 1 1
 1
 /
 X
 FP
stfdepx 0 1 1 1 1 1
 frS
 rA
 rB
 1 0 1 1 0
 1
 1 1 1
 1
 /
 X
 E.PD, FP
EREF: A Programmer’s Reference Manual for Freescale Power Architecture Processors, Rev. 1 (EIS 2.1)
Freescale Semiconductor
A-105
Instruction Set Listings
Table A-4. Instructions Sorted by Opcode (Binary) (continued)
Mnemonic
 0
 1
 2
 3
 4
 5
 6
 7
 8
 9
 10
 11
 12
 13 14 15 16 17
 18 19 20 21 22
 23 24
 25
 26
 27
 28
 29
 30
 31
 Form Category
stddx 0 1 1 1 1 1
 rS
 rA
 rB
 1 0 1 1 1
 0
 0 0 1
 1
 /
 X
 DS, 64
stvswx 0 1 1 1 1 1
 vS
 rA
 rB
 1 0 1 1 1
 0
 0 1 0
 1
 /
 X
 V
subfmeo 0 1 1 1 1 1
 rD
 rA
 ///
 1 0 1 1 1
 0
 1 0 0
 0
 0
 X
subfmeo. 0 1 1 1 1 1
 rD
 rA
 ///
 1 0 1 1 1
 0
 1 0 0
 0
 1
 X
mulldo 0 1 1 1 1 1
 rD
 rA
 rB
 1 0 1 1 1
 0
 1 0 0
 1
 0
 X
 64
mulldo. 0 1 1 1 1 1
 rD
 rA
 rB
 1 0 1 1 1
 0
 1 0 0
 1
 1
 X
 64
addmeo 0 1 1 1 1 1
 rD
 rA
 ///
 1 0 1 1 1
 0
 1 0 1
 0
 0
 X
addmeo. 0 1 1 1 1 1
 rD
 rA
 ///
 1 0 1 1 1
 0
 1 0 1
 0
 1
 X
mullwo 0 1 1 1 1 1
 rD
 rA
 rB
 1 0 1 1 1
 0
 1 0 1
 1
 0
 X
mullwo. 0 1 1 1 1 1
 rD
 rA
 rB
 1 0 1 1 1
 0
 1 0 1
 1
 1
 X
dcba 0 1 1 1 1 1
 ///
 0
 rA
 rB
 1 0 1 1 1
 1
 0 1 1
 0
 /
 X
dcbal 0 1 1 1 1 1
 ///
 1
 rA
 rB
 1 0 1 1 1
 1
 0 1 1
 0
 /
 X
 DEO
stfdux 0 1 1 1 1 1
 frS
 rA
 rB
 1 0 1 1 1
 1
 0 1 1
 1
 /
 X
 FP
lvsm 0 1 1 1 1 1
 vD
 rA
 rB
 1 1 0 0 0
 0
 0 1 0
 1
 /
 X
 V
stvepxl 0 1 1 1 1 1
 vS
 rA
 rB
 1 1 0 0 0
 0
 0 1 1
 1
 /
 X
 E.PD, V
addo 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 0 0 0
 0
 1 0 1
 0
 0
 X
addo. 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 0 0 0
 0
 1 0 1
 0
 1
 X
tlbivax 0 1 1 1 1 1
 0
 ///
 rA
 rB
 1 1 0 0 0
 1
 0 0 1
 0
 /
 X
 Embedded
lhbrx 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 0 0 0
 1
 0 1 1
 0
 /
 X
sraw 0 1 1 1 1 1
 rS
 rA
 rB
 1 1 0 0 0
 1
 1 0 0
 0
 0
 X
sraw. 0 1 1 1 1 1
 rS
 rA
 rB
 1 1 0 0 0
 1
 1 0 0
 0
 1
 X
srad 0 1 1 1 1 1
 rS
 rA
 rB
 1 1 0 0 0
 1
 1 0 1
 0
 0
 X
 64
srad. 0 1 1 1 1 1
 rS
 rA
 rB
 1 1 0 0 0
 1
 1 0 1
 0
 1
 X
 64
evlddepx 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 0 0 0
 1
 1 1 1
 1
 /
 X
 E.PD,SP
lfddx 0 1 1 1 1 1
 frD
 rA
 rB
 1 1 0 0 1
 0
 0 0 1
 1
 /
 X
 DS, FP
lvtrxl 0 1 1 1 1 1
 vD
 rA
 rB
 1 1 0 0 1
 0
 0 1 0
 1
 /
 X
 V
stvepx 0 1 1 1 1 1
 vS
 rA
 rB
 1 1 0 0 1
 0
 0 1 1
 1
 /
 X
 E.PD, V
mulhus 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 0 0 1
 0
 1 0 1
 1
 0
 X
 ISAT
mulhus. 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 0 0 1
 0
 1 0 1
 1
 1
 X
 ISAT
dss 0 1 1 1 1 1
 0
 //
 STRM
 ///
 ///
 1 1 0 0 1
 1
 0 1 1
 0
 /
 X
 V
dssall 0 1 1 1 1 1
 1
 //
 ///
 ///
 ///
 1 1 0 0 1
 1
 0 1 1
 0
 /
 X
 V
srawi 0 1 1 1 1 1
 rS
 rA
 SH
 1 1 0 0 1
 1
 1 0 0
 0
 0
 X
srawi. 0 1 1 1 1 1
 rS
 rA
 SH
 1 1 0 0 1
 1
 1 0 0
 0
 1
 X
sradi 0 1 1 1 1 1
 rS
 rA
 sh1-5
 1 1 0 0 1
 1
 1 0 1
 sh0
 0
 XS
 64
sradi. 0 1 1 1 1 1
 rS
 rA
 sh1-5
 1 1 0 0 1
 1
 1 0 1
 sh0
 1
 XS
 64
A-106
EREF: A Programmer’s Reference Manual for Freescale Power Architecture Processors, Rev. 1 (EIS 2.1)
Freescale Semiconductor
Instruction Set Listings
Table A-4. Instructions Sorted by Opcode (Binary) (continued)
Mnemonic
 0
 1
 2
 3
 4
 5
 6
 7
 8
 9
 10
 11
 12
 13 14 15 16 17
 18 19 20 21 22
 23 24
 25
 26
 27
 28
 29
 30
 31
 Form Category
lvtlxl 0 1 1 1 1 1
 vD
 rA
 rB
 1 1 0 1 0
 0
 0 1 0
 1
 /
 X
 V
subfwu 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 0 1 0
 0
 1 0 0
 0
 0
 X
 64
subfwu. 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 0 1 0
 0
 1 0 0
 0
 1
 X
 64
addwu 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 0 1 0
 0
 1 0 1
 0
 0
 X
 64
addwu. 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 0 1 0
 0
 1 0 1
 0
 1
 X
 64
mbar 0 1 1 1 1 1
 MO
 ///
 1 1 0 1 0
 1
 0 1 1
 0
 /
 X
 Embedded
lvswxl 0 1 1 1 1 1
 vD
 rA
 rB
 1 1 0 1 1
 0
 0 1 0
 1
 /
 X
 V
subfwus 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 0 1 1
 0
 1 0 0
 0
 0
 X
 ISAT
subfwus. 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 0 1 1
 0
 1 0 0
 0
 1
 X
 ISAT
addwus 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 0 1 1
 0
 1 0 1
 0
 0
 X
 ISAT
addwus. 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 0 1 1
 0
 1 0 1
 0
 1
 X
 ISAT
mulwus 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 0 1 1
 0
 1 0 1
 1
 0
 X
 ISAT
mulwus. 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 0 1 1
 0
 1 0 1
 1
 1
 X
 ISAT
subfhu 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 1 0 0
 0
 1 0 0
 0
 0
 X
subfhu. 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 1 0 0
 0
 1 0 0
 0
 1
 X
addhu 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 1 0 0
 0
 1 0 1
 0
 0
 X
addhu. 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 1 0 0
 0
 1 0 1
 0
 1
 X
divweuo 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 1 0 0
 0
 1 0 1
 1
 0
 XO
divweuo. 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 1 0 0
 0
 1 0 1
 1
 1
 XO
tlbsx 0 1 1 1 1 1
 0
 ///
 rA
 rB
 1 1 1 0 0
 1
 0 0 1
 0
 /
 X
 Embedded
sthbrx 0 1 1 1 1 1
 rS
 rA
 rB
 1 1 1 0 0
 1
 0 1 1
 0
 /
 X
extsh 0 1 1 1 1 1
 rS
 rA
 ///
 1 1 1 0 0
 1
 1 0 1
 0
 0
 X
extsh. 0 1 1 1 1 1
 rS
 rA
 ///
 1 1 1 0 0
 1
 1 0 1
 0
 1
 X
evstddepx 0 1 1 1 1 1
 rS
 rA
 rB
 1 1 1 0 0
 1
 1 1 1
 1
 /
 X
 E.PD, SP
stfddx 0 1 1 1 1 1
 frS
 rA
 rB
 1 1 1 0 1
 0
 0 0 1
 1
 /
 X
 DS, FP
stvfrxl 0 1 1 1 1 1
 vS
 rA
 rB
 1 1 1 0 1
 0
 0 1 0
 1
 /
 X
 V
subfhus 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 1 0 1
 0
 1 0 0
 0
 0
 X
 ISAT
subfhus. 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 1 0 1
 0
 1 0 0
 0
 1
 X
 ISAT
addhus 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 1 0 1
 0
 1 0 1
 0
 0
 X
 ISAT
addhus. 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 1 0 1
 0
 1 0 1
 0
 1
 X
 ISAT
divweo 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 1 0 1
 0
 1 0 1
 1
 0
 XO
divweo. 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 1 0 1
 0
 1 0 1
 1
 1
 XO
tlbre 0 1 1 1 1 1
 0
 ///
 1 1 1 0 1
 1
 0 0 1
 0
 /
 X
 Embedded
extsb 0 1 1 1 1 1
 rS
 rA
 ///
 1 1 1 0 1
 1
 1 0 1
 0
 0
 X
EREF: A Programmer’s Reference Manual for Freescale Power Architecture Processors, Rev. 1 (EIS 2.1)
Freescale Semiconductor
A-107
Instruction Set Listings
Table A-4. Instructions Sorted by Opcode (Binary) (continued)
Mnemonic
 0
 1
 2
 3
 4
 5
 6
 7
 8
 9
 10
 11
 12
 13 14 15 16 17
 18 19 20 21 22
 23 24
 25
 26
 27
 28
 29
 30
 31
 Form Category
extsb. 0 1 1 1 1 1
 rS
 rA
 ///
 1 1 1 0 1
 1
 1 0 1
 0
 1
 X
stvflxl 0 1 1 1 1 1
 vS
 rA
 rB
 1 1 1 1 0
 0
 0 1 0
 1
 /
 X
 V
subfbu 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 1 1 0
 0
 1 0 0
 0
 0
 X
subfbu. 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 1 1 0
 0
 1 0 0
 0
 1
 X
divduo 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 1 1 0
 0
 1 0 0
 1
 0
 X
 64
divduo. 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 1 1 0
 0
 1 0 0
 1
 1
 X
 64
addbu 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 1 1 0
 0
 1 0 1
 0
 0
 X
addbu. 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 1 1 0
 0
 1 0 1
 0
 1
 X
divwuo 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 1 1 0
 0
 1 0 1
 1
 0
 X
divwuo. 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 1 1 0
 0
 1 0 1
 1
 1
 X
tlbwe 0 1 1 1 1 1
 0
 ///
 1 1 1 1 0
 1
 0 0 1
 0
 /
 X
 Embedded
icbi 0 1 1 1 1 1
 ///
 rA
 rB
 1 1 1 1 0
 1
 0 1 1
 0
 /
 X
stfiwx 0 1 1 1 1 1
 frS
 rA
 rB
 1 1 1 1 0
 1
 0 1 1
 1
 /
 X
 FP
extsw 0 1 1 1 1 1
 rS
 rA
 ///
 1 1 1 1 0
 1
 1 0 1
 0
 0
 X
 64
extsw. 0 1 1 1 1 1
 rS
 rA
 ///
 1 1 1 1 0
 1
 1 0 1
 0
 1
 X
 64
icbiep 0 1 1 1 1 1
 ///
 rA
 rB
 1 1 1 1 0
 1
 1 1 1
 1
 /
 X
 E.PD
stvswxl 0 1 1 1 1 1
 vS
 rA
 rB
 1 1 1 1 1
 0
 0 1 0
 1
 /
 X
 V
subfbus 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 1 1 1
 0
 1 0 0
 0
 0
 X
 ISAT
subfbus. 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 1 1 1
 0
 1 0 0
 0
 1
 X
 ISAT
divdo 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 1 1 1
 0
 1 0 0
 1
 0
 X
 64
divdo. 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 1 1 1
 0
 1 0 0
 1
 1
 X
 64
addbus 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 1 1 1
 0
 1 0 1
 0
 0
 X
 ISAT
addbus. 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 1 1 1
 0
 1 0 1
 0
 1
 X
 ISAT
divwo 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 1 1 1
 0
 1 0 1
 1
 0
 X
divwo. 0 1 1 1 1 1
 rD
 rA
 rB
 1 1 1 1 1
 0
 1 0 1
 1
 1
 X
dcbz 0 1 1 1 1 1
 ///
 0
 rA
 rB
 1 1 1 1 1
 1
 0 1 1
 0
 /
 X
dcbzl 0 1 1 1 1 1
 ///
 1
 rA
 rB
 1 1 1 1 1
 1
 0 1 1
 0
 /
 X
 DEO
dcbzep 0 1 1 1 1 1
 ///
 0
 rA
 rB
 1 1 1 1 1
 1
 1 1 1
 1
 /
 X
 E.PD
dcbzlep 0 1 1 1 1 1
 ///
 1
 rA
 rB
 1 1 1 1 1
 1
 1 1 1
 1
 /
 X
 DEO, E.PD
lwz 1 0 0 0 0 0
 rD
 rA
 D
 D None
lwzu 1 0 0 0 0 1
 rD
 rA
 D
 D None
lbz 1 0 0 0 1 0
 rD
 rA
 D
 D None
lbzu 1 0 0 0 1 1
 rD
 rA
 D
 D None
stw 1 0 0 1 0 0
 rS
 rA
 D
 D None
stwu 1 0 0 1 0 1
 rS
 rA
 D
 D None
A-108
EREF: A Programmer’s Reference Manual for Freescale Power Architecture Processors, Rev. 1 (EIS 2.1)
Freescale Semiconductor
Instruction Set Listings
Table A-4. Instructions Sorted by Opcode (Binary) (continued)
Mnemonic
 0
 1
 2
 3
 4
 5
 6
 7
 8
 9
 10
 11
 12
 13 14 15 16 17
 18 19 20 21 22
 23 24
 25
 26
 27
 28
 29
 30
 31
 Form Category
stb 1 0 0 1 1 0
 rS
 rA
 D
 D None
stbu 1 0 0 1 1 1
 rS
 rA
 D
 D None
lhz 1 0 1 0 0 0
 rD
 rA
 D
 D None
lhzu 1 0 1 0 0 1
 rD
 rA
 D
 D None
lha 1 0 1 0 1 0
 rD
 rA
 D
 D None
lhau 1 0 1 0 1 1
 rD
 rA
 D
 D None
sth 1 0 1 1 0 0
 rS
 rA
 D
 D None
sthu 1 0 1 1 0 1
 rS
 rA
 D
 D None
lmw 1 0 1 1 1 0
 rD
 rA
 D
 D None
stmw 1 0 1 1 1 1
 rS
 rA
 D
 D None
lfs 1 1 0 0 0 0
 frD
 rA
 D
 D
 FP
lfsu 1 1 0 0 0 1
 frD
 rA
 D
 D
 FP
lfd 1 1 0 0 1 0
 frD
 rA
 D
 D
 FP
lfdu 1 1 0 0 1 1
 frD
 rA
 D
 D
 FP
stfs 1 1 0 1 0 0
 frS
 rA
 D
 D
 FP
stfsu 1 1 0 1 0 1
 frS
 rA
 D
 D
 FP
stfd 1 1 0 1 1 0
 frS
 rA
 D
 D
 FP
stfdu 1 1 0 1 1 1
 frS
 rA
 D
 D
 FP
ld 1 1 1 0 1 0
 rD
 rA
 DS
 0
 0
 DS
 64
ldu 1 1 1 0 1 0
 rD
 rA
 DS
 0
 1
 DS
 64
lwa 1 1 1 0 1 0
 rD
 rA
 DS
 1
 0
 DS
 64
fdivs 1 1 1 0 1 1
 frD
 frA
 frB
 ///
 1
 0 0 1
 0
 0
 A
 FP
fdivs. 1 1 1 0 1 1
 frD
 frA
 frB
 ///
 1
 0 0 1
 0
 1
 A
 FP.R
fsubs 1 1 1 0 1 1
 frD
 frA
 frB
 ///
 1
 0 1 0
 0
 0
 A
 FP
fsubs. 1 1 1 0 1 1
 frD
 frA
 frB
 ///
 1
 0 1 0
 0
 1
 A
 FP.R
fadds 1 1 1 0 1 1
 frD
 frA
 frB
 ///
 1
 0 1 0
 1
 0
 A
 FP
fadds. 1 1 1 0 1 1
 frD
 frA
 frB
 ///
 1
 0 1 0
 1
 1
 A
 FP.R
fres 1 1 1 0 1 1
 frD
 ///
 frB
 ///
 1
 1 0 0
 0
 0
 A
 FP
fres. 1 1 1 0 1 1
 frD
 ///
 frB
 ///
 1
 1 0 0
 0
 1
 A
 FP.R
fmuls 1 1 1 0 1 1
 frD
 frA
 ///
 frC
 1
 1 0 0
 1
 0
 A
 FP
fmuls. 1 1 1 0 1 1
 frD
 frA
 ///
 frC
 1
 1 0 0
 1
 1
 A
 FP.R
fmsubs 1 1 1 0 1 1
 frD
 frA
 frB
 frC
 1
 1 1 0
 0
 0
 A
 FP
fmsubs. 1 1 1 0 1 1
 frD
 frA
 frB
 frC
 1
 1 1 0
 0
 1
 A
 FP.R
fmadds 1 1 1 0 1 1
 frD
 frA
 frB
 frC
 1
 1 1 0
 1
 0
 A
 FP
fmadds. 1 1 1 0 1 1
 frD
 frA
 frB
 frC
 1
 1 1 0
 1
 1
 A
 FP.R
EREF: A Programmer’s Reference Manual for Freescale Power Architecture Processors, Rev. 1 (EIS 2.1)
Freescale Semiconductor
A-109
Instruction Set Listings
Table A-4. Instructions Sorted by Opcode (Binary) (continued)
Mnemonic
 0
 1
 2
 3
 4
 5
 6
 7
 8
 9
 10
 11
 12
 13 14 15 16 17
 18 19 20 21 22
 23 24
 25
 26
 27
 28
 29
 30
 31
 Form Category
fnmsubs 1 1 1 0 1 1
 frD
 frA
 frB
 frC
 1
 1 1 1
 0
 0
 A
 FP
fnmsubs. 1 1 1 0 1 1
 frD
 frA
 frB
 frC
 1
 1 1 1
 0
 1
 A
 FP.R
fnmadds 1 1 1 0 1 1
 frD
 frA
 frB
 frC
 1
 1 1 1
 1
 0
 A
 FP
fnmadds. 1 1 1 0 1 1
 frD
 frA
 frB
 frC
 1
 1 1 1
 1
 1
 A
 FP.R
std 1 1 1 1 1 0
 rS
 rA
 DS
 0
 0
 DS
 64
stdu 1 1 1 1 1 0
 rS
 rA
 DS
 0
 1
 DS
 64
fcmpu 1 1 1 1 1 1
 crD
 //
 frA
 frB
 0 0 0 0 0
 0
 0 0 0
 0
 /
 X
 FP
frsp 1 1 1 1 1 1
 frD
 ///
 frB
 0 0 0 0 0
 0
 1 1 0
 0
 0
 X
 FP
frsp. 1 1 1 1 1 1
 frD
 ///
 frB
 0 0 0 0 0
 0
 1 1 0
 0
 1
 X
 FP.R
fctiw 1 1 1 1 1 1
 frD
 ///
 frB
 0 0 0 0 0
 0
 1 1 1
 0
 0
 X
 FP
fctiw. 1 1 1 1 1 1
 frD
 ///
 frB
 0 0 0 0 0
 0
 1 1 1
 0
 1
 X
 FP.R
fctiwz 1 1 1 1 1 1
 frD
 ///
 frB
 0 0 0 0 0
 0
 1 1 1
 1
 0
 X
 FP
fctiwz. 1 1 1 1 1 1
 frD
 ///
 frB
 0 0 0 0 0
 0
 1 1 1
 1
 1
 X
 FP.R
fdiv 1 1 1 1 1 1
 frD
 frA
 frB
 ///
 1
 0 0 1
 0
 0
 A
 FP
fdiv. 1 1 1 1 1 1
 frD
 frA
 frB
 ///
 1
 0 0 1
 0
 1
 A
 FP.R
fadd 1 1 1 1 1 1
 frD
 frA
 frB
 ///
 1
 0 1 0
 1
 0
 A
 FP
fsub 1 1 1 1 1 1
 frD
 frA
 frB
 ///
 1
 0 1 0
 0
 0
 A
 FP
fsub. 1 1 1 1 1 1
 frD
 frA
 frB
 ///
 1
 0 1 0
 0
 1
 A
 FP.R
fadd. 1 1 1 1 1 1
 frD
 frA
 frB
 ///
 1
 0 1 0
 1
 1
 A
 FP.R
fsel 1 1 1 1 1 1
 frD
 frA
 frB
 frC
 1
 0 1 1
 1
 0
 A
 FP
fsel. 1 1 1 1 1 1
 frD
 frA
 frB
 frC
 1
 0 1 1
 1
 1
 A
 FP.R
fmul 1 1 1 1 1 1
 frD
 frA
 ///
 frC
 1
 1 0 0
 1
 0
 A
 FP
fmul. 1 1 1 1 1 1
 frD
 frA
 ///
 frC
 1
 1 0 0
 1
 1
 A
 FP.R
frsqrte 1 1 1 1 1 1
 frD
 ///
 frB
 ///
 1
 1 0 1
 0
 0
 A
 FP
frsqrte. 1 1 1 1 1 1
 frD
 ///
 frB
 ///
 1
 1 0 1
 0
 1
 A
 FP.R
fmsub 1 1 1 1 1 1
 frD
 frA
 frB
 frC
 1
 1 1 0
 0
 0
 A
 FP
fmsub. 1 1 1 1 1 1
 frD
 frA
 frB
 frC
 1
 1 1 0
 0
 1
 A
 FP.R
fmadd 1 1 1 1 1 1
 frD
 frA
 frB
 frC
 1
 1 1 0
 1
 0
 A
 FP
fmadd. 1 1 1 1 1 1
 frD
 frA
 frB
 frC
 1
 1 1 0
 1
 1
 A
 FP.R
fnmsub 1 1 1 1 1 1
 frD
 frA
 frB
 frC
 1
 1 1 1
 0
 0
 A
 FP
fnmsub. 1 1 1 1 1 1
 frD
 frA
 frB
 frC
 1
 1 1 1
 0
 1
 A
 FP.R
fnmadd 1 1 1 1 1 1
 frD
 frA
 frB
 frC
 1
 1 1 1
 1
 0
 A
 FP
fnmadd. 1 1 1 1 1 1
 frD
 frA
 frB
 frC
 1
 1 1 1
 1
 1
 A
 FP.R
fcmpo 1 1 1 1 1 1
 crD
 //
 frA
 frB
 0 0 0 0 1
 0
 0 0 0
 0
 /
 X
 FP
mtfsb1 1 1 1 1 1 1
 crbD
 ///
 0 0 0 0 1
 0
 0 1 1
 0
 0
 X
 FP
A-110
EREF: A Programmer’s Reference Manual for Freescale Power Architecture Processors, Rev. 1 (EIS 2.1)
Freescale Semiconductor
Instruction Set Listings
Table A-4. Instructions Sorted by Opcode (Binary) (continued)
Mnemonic
 0
 1
 2
 3
 4
 5
 6
 7
 8
 9
 10
 11
 12
 13 14 15 16 17
 18 19 20 21 22
 23 24
 25
 26
 27
 28
 29
 30
 31
 Form Category
mtfsb1. 1 1 1 1 1 1
 crbD
 ///
 0 0 0 0 1
 0
 0 1 1
 0
 1
 X
 FP.R
fneg 1 1 1 1 1 1
 frD
 ///
 frB
 0 0 0 0 1
 0
 1 0 0
 0
 0
 X
 FP
fneg. 1 1 1 1 1 1
 frD
 ///
 frB
 0 0 0 0 1
 0
 1 0 0
 0
 1
 X
 FP.R
mcrfs 1 1 1 1 1 1
 crD
 //
 crfS
 ///
 0 0 0 1 0
 0
 0 0 0
 0
 /
 X
 FP
mtfsb0 1 1 1 1 1 1
 crbD
 ///
 0 0 0 1 0
 0
 0 1 1
 0
 0
 X
 FP
mtfsb0. 1 1 1 1 1 1
 crbD
 ///
 0 0 0 1 0
 0
 0 1 1
 0
 1
 X
 FP.R
fmr 1 1 1 1 1 1
 frD
 ///
 frB
 0 0 0 1 0
 0
 1 0 0
 0
 0
 X
 FP
fmr. 1 1 1 1 1 1
 frD
 ///
 frB
 0 0 0 1 0
 0
 1 0 0
 0
 1
 X
 FP.R
mtfsfi 1 1 1 1 1 1
 crD
 ///
 ///
 W
 IMM
 /
 0 0 1 0 0
 0
 0 1 1
 0
 0
 X
 FP
mtfsfi. 1 1 1 1 1 1
 crD
 ///
 ///
 W
 IMM
 /
 0 0 1 0 0
 0
 0 1 1
 0
 1
 X
 FP.R
fnabs 1 1 1 1 1 1
 frD
 ///
 frB
 0 0 1 0 0
 0
 1 0 0
 0
 0
 X
 FP
fnabs. 1 1 1 1 1 1
 frD
 ///
 frB
 0 0 1 0 0
 0
 1 0 0
 0
 1
 X
 FP.R
fabs 1 1 1 1 1 1
 frD
 ///
 frB
 0 1 0 0 0
 0
 1 0 0
 0
 0
 X
 FP
fabs. 1 1 1 1 1 1
 frD
 ///
 frB
 0 1 0 0 0
 0
 1 0 0
 0
 1
 X
 FP.R
mffs 1 1 1 1 1 1
 frD
 ///
 1 0 0 1 0
 0
 0 1 1
 1
 0
 X
 FP
mffs. 1 1 1 1 1 1
 frD
 ///
 1 0 0 1 0
 0
 0 1 1
 1
 1
 X
 FP.R
mtfsf 1 1 1 1 1 1
 L
 FM
 W
 frB
 1 0 1 1 0
 0
 0 1 1
 1
 0
 XFX FP
mtfsf. 1 1 1 1 1 1
 L
 FM
 W
 frB
 1 0 1 1 0
 0
 0 1 1
 1
 1
 XFX FP.R
fctid 1 1 1 1 1 1
 frD
 ///
 frB
 1 1 0 0 1
 0
 1 1 1
 0
 0
 X
 FP
fctid. 1 1 1 1 1 1
 frD
 ///
 frB
 1 1 0 0 1
 0
 1 1 1
 0
 1
 X
 FP.R
fctidz 1 1 1 1 1 1
 frD
 ///
 frB
 1 1 0 0 1
 0
 1 1 1
 1
 0
 X
 FP
fctidz. 1 1 1 1 1 1
 frD
 ///
 frB
 1 1 0 0 1
 0
 1 1 1
 1
 1
 X
 FP.R
fcfid 1 1 1 1 1 1
 frD
 ///
 frB
 1 1 0 1 0
 0
 1 1 1
 0
 0
 X
 FP
fcfid. 1 1 1 1 1 1
 frD
 ///
 frB
 1 1 0 1 0
 0
 1 1 1
 0
 1
 X
 FP.R'''
# NOTE: had to fix this dump for several bugs
# * UIMM[123] didn't copy the footnotes (and turns out they're important for memory derefs...)
# * ">" instead of "." somehow made it in
# * added None to the end of some of the lines to clearly demarc those lines without a Category
# * mtfsf instructions set L and W to 0's...  "The L and W fields of the instruction should always be set to 0."
#   * set back to real values, since PowerISA says something different.  Apparently EREF's talking about the Extended form.
# * mtfsfi instructions set W to 0...  "The W field of the instruction should always be set to 0."
#   * set back to real value, since PowerISA says something different.  Apparently EREF's talking about the Extended form.
# * evrndw, replaced UIMM with 0 0 0 0 0 (appears to be wrong in this table, defined in SPEPEM.
# * cmpl is completely botched:  they left out the crfD field completely, which caused a shift in all the other fields.  eerily, they made up for it with ///
# a few others (should have and will document as i think of them.  see git log.

# TODO:
# * isel   note: isel r15, r15, r16, cr3.eq

cat_names = ('NONE',
        '64',
        'E',
        'V',
        'SP',
        'SP_FV',
        'SP_FS',
        'SP_FD',
        'EMBEDDED',
        'E_ED',
        'E_HV',
        'E_PD',
        'ER',
        'WT',
        'E_CL',
        'E_PC',
        'ISAT',
        'E_DC',
        'E_PM',
        'EM_TM',
        'DS',
        'FP',
        'DEO',
        'FP_R', )
forms = (
        'X',
        'D',
        'XFX',
        'XO',
        'XL',
        'A',
        'MD',
        'MDS',
        'M',
        'B',
        'I',
        'SC',
        'VC',
        'VX',
        'EVX',
        'VA',
        'DS',
        'XS',
        )

FORM_CONST = { form : "FORM_" + form for form in forms }

# rS, vS, frS all start at bit 6
# rD, vD, frD, crbD all start at bit 6
# rA, vA, frA, crbA all start at bit 11
# rB, vB, frB, crbB all start at bit 16
# rC, vC, frC, crbC all start at bit 21
# BO starts at bit 6
# BI starts at bit 11
# LI starts at bit 6
# BD starts at bit 16
# UIMM and SIMM start at bit 16 (SOMETIMES) otherwise it's 5 bits
# DUI starts at bit 6
# DCTL starts at bit 11
# STRM starts at bit 9
# crD is 2bits and starts at bit 6
# crfS is 3 bits starting at bit 11
# OC is 15 bits and starts at bit 6
# CT starts at bit 6
# D starts at bit 16 and is 16 bits long
# DS starts at bit 16
# CRM starts at bit 12
# DCRN5-9 starts at 11
# DCRN0-4 starts at 16
# PMRN5-9 starts at 11
# PMRN0-4 starts at 16
# TBRN5-9 starts at 11
# TBRN0-4 starts at 16
# TMRN5-9 starts at 11
# TMRN0-4 starts at 16
# MO starts at bit 6 for 5 bits
# L is 1 bit at bit 6
# W is 1 bit at bit 20
# FM starts at bit 7 for 8 bits
# IMM is 4 bits at 21
# sh1-5
# mb1-5
# me1-5
# MB
# ME

# fname : (startbit, size)
# None for either indicates an unknown
FIELD_DATA = {
    '------': (0,6),
    'rS' :      (6,5),
    'vS' :      (6,5),
    'frS' :     (6,5),
    'rS' :      (6,5),

    'rD' :      (6,5),
    'vD' :      (6,5),
    'frD' :     (6,5),
    'crbD' :    (6,5),

    'rA' :      (11,5),
    'vA' :      (11,5),
    'frA' :     (11,5),
    'crbA' :    (11,5),

    'rB' :      (16,5),
    'vB' :      (16,5),
    'frB' :     (16,5),
    'crbB' :    (16,5),

    'rC' :      (21,5),
    'vC' :      (21,5),
    'frC' :     (21,5),
    'crbC' :    (21,5),

    'TO' :      (6,5),
    'BO' :      (6, 5),
    'BI' :      (11, 5),
    'crBI' :    (11, 3),
    'LI' :      (6, 24),
    'BD' :      (16, 14),
    'BH' :      (19, 2),
    'LEV' :     (20, 7),
    'DUI' :     (6, 5),
    'DCTL' :    (11, 5),
    'STRM' :    (9, 2),
    'crD' :     (6, 3),
    'OC' :      (6, 15),
    'CT' :      (6, 5),
    'D' :       (16, 16),
    'DE' :      (16, 12),
    'DS' :      (16, 14),
    'CRM' :     (12, 8),
    'DCRN5-9' : (11, 5),
    'DCRN0-4' : (16, 5),
    'PMRN5-9' : (11, 5),
    'PMRN0-4' : (16, 5),
    'TBRN5-9' : (11, 5),
    'TBRN0-4' : (16, 5),
    'TMRN5-9' : (11, 5),
    'TMRN0-4' : (16, 5),
    'SPRN5-9' : (11, 5),
    'SPRN0-4' : (16, 5),
    'MO' :      (6, 5),
    'W' :       (15, 1),
    'FM' :      (7, 8),
    'sh0' :     (30, 1),
    'sh1-5' :   (16, 5),
    'mb1-5' :   (21, 5),
    'me1-5' :   (21, 5),
    'mb0'   :   (26, 1),
    'me0'   :   (26, 1),
    'MB'    :   (21, 5),
    'ME'    :   (26, 5),
    'TH' :      (6, 5),
    'SS' :      (16, 1),
    'IU' :      (17, 1),
    'OU' :      (18, 1),
    'SA' :      (19, 2),
    'E'  :      (16, 1),
    'WC' :      (9, 2),
    'WH' :      (11, 1),
    'T'  :      (9, 2),
    'crb' :     (21, 5),
    'crfD' :    (6, 3),
    'SIMM5' :   (11, 5),        # only here to be included in the const_gen.  this does not work with parsing the data
    'SIMM16' :  (16, 16),       # only here to be included in the const_gen.  this does not work with parsing the data
    '///' :     (None, None),  # this is a filler field.  could be anywhere and any size.

    }
FIELD_M_DATA = {
    'UIMM' :    ( (11, 5), (16, 5), (16,16), ), # form doesn't help.  eg. EVX does multiples
    'UIMM 1' :  ( (11, 5), (16, 5), ), # form doesn't help.  eg. EVX does multiples
    'UIMM 2' :  ( (11, 5), (16, 5), ), # form doesn't help.  eg. EVX does multiples
    'UIMM 3' :  ( (11, 5), (16, 5), ), # form doesn't help.  eg. EVX does multiples
    'SIMM' :    ( (11, 5), (16,16), ),
    'IMM' :     ( (16,4), (21, 4), ),   # X FP: 16, X FP.RL 16
    'crfS' :    ( (11,3), (29, 3), ),
    'L' :       ( (6, 1), (10, 1), ),
    'SH' :      ( (22, 4), (16, 5), ),
    }

THING_FILL = 0
THING_VAR = 1
THING_STATIC = 2

rAnegades = [
    #'addi',        # handled in aliasing, if rA==0, these are really LI and LIS
    #'addis',
    'dcba',
    'dcbal',
    'dcbf',
    'dcbfep',
    'dcbi',
    'dcblc',
    'dcblq.',
    'dcbst',
    'dcbstep',
    'dcbt',
    'dcbtep',
    'dcbtst',
    'dcbtstep',
    'dcbtstls',
    'dcbz',
    'dcbzep',
    'dcbzl',
    'dcbzlep',
    'evlddepx',
    'icblq.',
    'icbtls',
    'isel',
    'icbi',
    'icbiep',
    'icblc',
    'icbt',
    'lbarx',
    'lbepx',
    'lbz',
    'lbzx',
    'ld',
    'ldarx',
    'ldbrx',
    'ldepx',
    'ldx',
    'lfd',
    'lfdepx',
    'lfdx',
    'lfs',
    'lfsx',
    'lha',
    'lhax',
    'lharx',
    'lhbrx',
    'lhepx',
    'lhz',
    'lhzx',
    'lmw',
    'lvepx',
    'lvepxl',
    'lwa',
    'lwarx',
    'lwax',
    'lwbrx',
    'lwepx',
    'lwz',
    'lwzx',
    'stb',
    'stbcx.',
    'stbepx',
    'stbx',
    'std',
    'stdbrx',
    'stdcx.',
    'stdepx',
    'stdx',
    'stfd',
    'stfdepx',
    'stfdx',
    'stfiwx',
    'stfs',
    'stfsx',
    'sth',
    'sthbrx',
    'sthcx.',
    'sthepx',
    'sthx',
    'stmw',
    'stvepx',
    'stvepxl',
    'stw',
    'stwbrx',
    'stwcx.',
    'stwepx',
    'stwx',
    'tlbsx',
    # second time through additions
    'lq',
    'stq',
    'lswi',
    'lswx',
    'stswi',
    'stswx',
    'lfiwax',
    'lfiwzx',
    'stfiwx',
    'lfdp',
    'stfdp',
    'lfdpx',
    'stfdpx',
    'lvebx',
    'lvehx',
    'lvewx',
    'lvx',
    'lvxl',
    'stvebx',
    'stvehx',
    'stvewx',
    'stvx',
    'stvxl',
    'lvsl',
    'lvsr',
    'lqarx',
    'stqcx.',
    'eciwx',
    'ecowx',
    'lbzcix',
    'lhzcix',
    'lwzcix',
    'ldcix',
    'stbcix',
    'sthcix',
    'stwcix',
    'stdcix',
    'tlbilx',
    'tlbsrx.',
    'tlbivax',
    'dcbtls',
]

TAG_APPEND  = -1
TAG_PREPEND = 0
EXTRA_OPCODES = {
        0x1f:   (
            (TAG_APPEND, 0xfe0007ff, 0x7c0006a5, ( 'tlbsrx.', 'INS_TLBSX', 'FORM_X', 'CAT_EMBEDDED', "(  ( 'rA', FIELD_rA, 16, 0x1f ), ( 'rB', FIELD_rB, 11, 0x1f ),)" , "IF_RC|IF_MEM_EA" ), ),
            ),
        }

def decode(s):
    lines = s.split('\n')
    groups = []
    newgroup = []
    #groups.append(newgroup)

    for line in lines:
        if line.startswith(' '):
            newgroup.append(line)
        elif len(line) == 0:
            newgroup.append(line)
        else:
            newgroup = [ line ]
            groups.append(newgroup)

    return groups

def filterLineGrps(groups):
    dellist = []
    for gidx in range(len(groups)):
        g = groups[gidx]
        if ord(g[0][0]) < 0x60:
            # capital letter, means it's not interesting (headers)
            dellist.append(gidx)

    for x in dellist[::-1]:
        groups.pop(x)


def breakupOpGrps(groups):
    opgroups = {}
    for grp in groups:
        mnem, opgrpidx = grp[0].split(' ', 1)
        grp[0] = opgrpidx
        #grp.insert(0, mnem)

        opgrpidx = int(opgrpidx.replace(' ',''), 2)
        opgrp = opgroups.get(opgrpidx)
        if opgrp == None:
            opgrp = []
            opgroups[opgrpidx] = opgrp

        opgrp.append((mnem, grp))

    return opgroups

def buildTables(opgroups):
    deets = { grp: parseOpgroup(opgroups[grp]) for grp in opgroups.keys() }
    dbyform = {}
    ##
    return deets

badforms = {}
badfields = {}

def parseOpgroup(opgrp):
    global badforms, badfields
    grpdeets = []
    for mnem, data in opgrp:
        grp = data[0]
        cat = data[-1].strip()

        if cat in forms and not data[-2].strip() in forms:
            #print('%r/%r/%r: missing cat' % (mnem, data[-2].strip(), cat))
            form = cat
            fidx = -1
            cat = 'NONE'
        elif cat.find(' ') != -1 and cat.find(', ') == -1:
            #print('%r/%r/%r: merged form/cat' % (mnem, data[-2].strip(), cat))
            form, cat = cat.split(' ')
            fidx = -1
            if form not in forms:
                print("(1)form: %r  not in forms!" % form)
        else:
            # this is really the default, if all goes well.
            form = data[-2].strip()
            fidx = -2
            if form in ('/', '1', '0'):
                form = cat
                fidx = -1
                cat = 'NONE'
            if form not in forms:
                print("(2)form: %r  not in forms!" % form)
                bf = badforms.get(form)
                if bf == None:
                    bf = []
                    badforms[form] = bf
                bf.append((mnem, data))


        fields = data[1:fidx]

        statbits = 6 # include first 6 opcode bits
        varfs = []
        stats = []
        nfields = [(None, grp.replace(' ',''), 0, 6, THING_STATIC)]
        for fidx in range(len(fields)):
            f = fields[fidx]
            go = True

            # check if it's a /// field.
            if '///' in f:
                #print("field has ///.  Breaking: %r" % f)
                thing = [fidx, f, None ,0, THING_FILL]
                varfs.append(thing)
                nfields.append(thing)
                continue

            # otherwise look through for static bits
            for x in range(len(f)):
                if f[x] not in ('0','1',' ','/'):
                    #print("breaking on %s" % f[x])
                    thing = [fidx, f, None, 0, THING_VAR]   # field index, field, size, startbit
                    varfs.append(thing)
                    nfields.append(thing)
                    go = False
                    break

            # if the last bit is a '/' it's considered a 1-bit field, count it.
            if fidx == len(fields)-1 and f.strip() == '/':
                go = True

            # if we haven't only had appropriate 1, 0, and /...  it's a named field, skip
            if not go: continue

            # add this static binary field to the list for counting
            bits = f.replace(' ','')
            thing = [fidx, bits, None, len(bits), THING_STATIC]
            stats.append(thing)
            nfields.append(thing)
            statbits += (len(f)/2)
            #print(f, "  \t",(len(f)/2), statbits)


        # try to determine type and size of operands
        leftover = 32 - statbits
        # mark registers
        for oidx in range(len(varfs)):
            odata = None
            oper = varfs[oidx]
            fidx, f, fstart, fsz, ftype = oper
            field = f.strip()

            #if oper[1].strip().startswith('r'):
            #    print("Register: %r" % oper)
            #    oper[2] = 5
            #    leftover -= 5

            #### COMPLETE HACK! I APOLOGIZE IN ADVANCE. - deprecated.  they screwed up the table.
            #if mnem == 'cmpl':
            #    odata = { 'rA' : (8, 5), 'rB' : (13, 5), 'L' : (7,1), }.get(field)
            #    #print(field, odata)

            # check the simple fields
            if odata == None:
                odata = FIELD_DATA.get(field)

            multi = False

            if odata == None:
                odata = FIELD_M_DATA.get(field)
                multi = True

            if odata == None:
                print("UNKNOWN FIELD: %r  (%s)" % (oper, mnem))
                bf = badfields.get(oper[1])
                if bf == None:
                    bf = []
                    badforms[oper[1]] = bf
                bf.append((mnem, data, oper))
                continue

            if not multi:
                gstart, gsz = odata

                if gstart != None:
                    varfs[oidx][2] = gstart
                if gsz != None:
                    varfs[oidx][3] = gsz
                    leftover -= gsz

        # once we've completed a pass through the simple ones...

        # reduce... find the length of the trailing static bits... and merge fields
        #print(mnem, nfields)
        cleanup = []
        laststart = 32
        lasttype = THING_STATIC
        for tidx in range(len(nfields)-1, 1, -1):
            thing = nfields[tidx]
            prev = nfields[tidx-1]
            #print(thing)


            if thing[4] == THING_FILL and prev[4] == THING_FILL:
                cleanup.append(tidx)

            elif thing[4] == THING_STATIC:
                # if this is the first static, we know the start and length
                if laststart == 32:
                    thing[2] = laststart - thing[3]
                    laststart = thing[2]

                if prev[4] == THING_STATIC:
                    # since we're collapsing, set prev's starting point
                    if prev[2] == None and thing[2] != None:
                        #laststart += thing[3]
                        prev[2] = thing[2] - prev[3]

                    # concat and add size, collapsing into prev
                    #print("prev(1) = ", prev)
                    prev[1] += thing[1]
                    prev[3] += thing[3]
                    cleanup.append(tidx)

                    #print("prev(2) = ", prev)

            laststart = thing[2]
            lasttype = thing[4]

        for x in cleanup:
            #print("popping %d(1)  (%r) " % (x, nfields))
            remove = nfields.pop(x)
            #print("popping %d(2)  (%r) " % (x, nfields))


        # now find what fits...
        for oidx in range(len(nfields)):
            oper = nfields[oidx]
            fidx, f, fstart, fsz, ftype = oper
            if ftype == THING_STATIC:
                continue

            field = f.strip()
            # skip if we have already identified a start bit
            if fstart != None:
                #print("fstart != None:", fstart)
                continue
            if '///' in f:
                continue

            # if we don't have a start bit, check multiple's
            odata = FIELD_M_DATA.get(field)
            if odata == None:
                print("UNKNOWN FIELD: %r  (%s)" % (oper, mnem))
                bf = badfields.get(oper[1])
                if bf == None:
                    bf = []
                    badforms[oper[1]] = bf
                bf.append((mnem, data, oper))
                continue

            # mash all the known ones together and see if each of these can coexist with each...
            for gidx in range(len(odata)-1, -1, -1):
                gstart, gsz = odata[gidx]
                fail = False

                for ofield in nfields:
                    tidx, tf, tstart, tsz, ttype = ofield
                    # skip this field if we haven't figured it out yet.
                    if tstart == None:
                        continue

                    if tstart < gstart:
                        if tstart + tsz > gstart:
                            # overlap
                            fail = True
                    elif gstart + gsz > tstart:
                        # overlap
                        fail = True
                if fail:
                    #print("\tFAIL!  ", gstart, gsz, ofield)
                    continue

                #print("SUCCESS!  ", gstart, gsz, ofield)

                # only continue if we're committed!
                #print(gstart, gsz, ofield)
                if gstart != None:
                    nfields[oidx][2] = gstart
                if gsz != None:
                    nfields[oidx][3] = gsz
                    leftover -= gsz
                break

        # clean up static start/size fields
        for oidx in range(1, len(nfields)-1):
            oper = nfields[oidx]
            fidx, f, fstart, fsz, ftype = oper
            field = f.strip()

            if ftype == THING_STATIC:
                if fstart == None:
                    prevf = nfields[oidx-1]
                    if prevf[2] != None:
                        oper[2] = prevf[2] + prevf[3]
                    else:
                        nextf = nfields[oidx+1]
                        oper[2] = nextf[2] - oper[3]
                    #raw_input("Check to make sure '/' start is correct")


        # finally, for cleanup sake ("///")
        for oidx in range(1, len(nfields)-1):
            oper = nfields[oidx]
            fidx, f, fstart, fsz, ftype = oper
            field = f.strip()

            if ftype == THING_FILL:
                prevf = nfields[oidx-1]
                nextf = nfields[oidx+1]
                gstart = prevf[2] + prevf[3]
                gsz = nextf[2] - gstart

                # now write into the array
                #print("FILLER: ", gstart, gsz)
                nfields[oidx][2] = gstart
                nfields[oidx][3] = gsz
                leftover -= gsz

        nobits = [x for x in varfs if x[3] == 0 and '///' not in x[1]]
        print("%-20s: %s\t%s\t%s \t%r\t%d\t%r" % (mnem, grp, form, cat, nfields, leftover, nobits))

        if checkNfieldSanity(nfields):
            print("ERROR: ", mnem, repr(nfields))
            input()



        grpdeets.append((mnem, grp, form, cat, fields, statbits, varfs, stats, nfields))


        nobits = [x for x in varfs if x[3] == 0 and '///' not in x[1]]

        #for nb in nobits:
            #bf = badfields.get(nb[1])
            #if bf == None:
                #bf = []
                #badforms[form] = bf
            #bf.append((mnem, data))

        if len(nobits):
            print("%-20s: %s\t%s\t%s \t%r\t%r\t%d\t%r" % (mnem, grp, form, cat, fields, varfs, leftover, nobits))

        #print("%s: %s\t%s\t%s \t%r\t%r\t%d" % (mnem, grp, form, cat, fields, varfs, leftover))
    return grpdeets

def checkNfieldSanity(nfields):
    lastidx = 0
    lastsize = 0
    fail = False
    for idx, f, start, sz, typ in nfields:
        if start != (lastidx + lastsize):
            print("FAIL Linkage Test! %r != (%r + %r)   %r " % (start, lastidx, lastsize, nfields))
            fail = True
        lastidx = start
        lastsize = sz

    if start + sz != 32:
        print("FAIL Finishing Test! %r != (%r + %r)   %r " % (32, start, sz, nfields))
        fail = True

    return fail



def parseData():
    lgrps = decode(encodings)
    filterLineGrps(lgrps)
    opgroups = breakupOpGrps(lgrps)

    return opgroups


IGNORE_CONSTS = (
        '------',
        '///',
    )

############

# Table 5-27. BO Operand Encodings
# page 319 of EREF_RM.pdf
#
#   BO    | Description
#   ------+------------
#   0000z | Decrement the CTR, then branch if the decremented CTR ≠ 0 and the condition is FALSE.
#   0001z | Decrement the CTR, then branch if the decremented CTR = 0 and the condition is FALSE.
#   001at | Branch if the condition is FALSE.
#   0100z | Decrement the CTR, then branch if the decremented CTR ≠ 0 and the condition is TRUE.
#   0101z | Decrement the CTR, then branch if the decremented CTR = 0 and the condition is TRUE.
#   011at | Branch if the condition is TRUE.
#   1a00t | Decrement the CTR, then branch if the decremented CTR ≠ 0.
#   1a01t | Decrement the CTR, then branch if the decremented CTR = 0.
#   1z1zz | Branch always.
#
#   z  == don't care
#   at == branch prediction bits
#
# * BO values where BO[2] != 0 are invalid for the bcctr instruction
#   page 415 of EREF_RM.pdf
#

# Some utility functions to make it clear what is being checked
BO_CHECK_CTR_ZERO_MASK = 0b00010
BO_DECREMENT_MASK      = 0b00100
BO_COND_MASK           = 0b01000
BO_CHECK_COND_MASK     = 0b10000

def BO_DECREMENT(bo):
    return (bo & BO_DECREMENT_MASK) == 0

# Table 5-28. at Bit Encodings
# page 319 of EREF_RM.pdf
#
#   at | Hint
#   ---+-----
#   00 | No hint is given
#   01 | Reserved
#   10 | The branch is very likely not to be taken
#   11 | The branch is very likely to be taken
#
#
# This table turns the branch conditional instructions into a mnemonic that
# incorporates the difficult to understand (as a number) BO field using the
# contents of tables 5-27 and 5-28.  Any encoding when z==1 in table 5-27 is
# technically invalid, so don't create a simplified mnemonic and just let the
# default bc/bcctr/bclr instruction form catch it.
bo_simple_stubs = {
    0b00000: (('bdnz', 'f'), ('envi.IF_COND', 'envi.IF_BRANCH'), ('BI',)),
    0b00001: None,
    0b00010: (('bdz', 'f'), ('envi.IF_COND', 'envi.IF_BRANCH'), ('BI',)),
    0b00011: None,
    0b00100: (('b', 'f'), ('envi.IF_COND', 'envi.IF_BRANCH'), ('BI',)),
    0b00101: None,
    0b00110: (('b', 'f'), ('envi.IF_COND', 'envi.IF_BRANCH', 'IF_BRANCH_UNLIKELY'), ('BI',)),
    0b00111: (('b', 'f'), ('envi.IF_COND', 'envi.IF_BRANCH', 'IF_BRANCH_LIKELY'), ('BI',)),
    0b01000: (('bdnz', 't'), ('envi.IF_COND', 'envi.IF_BRANCH'), ('BI',)),
    0b01001: None,
    0b01010: (('bdz', 't'), ('envi.IF_COND', 'envi.IF_BRANCH'), ('BI',)),
    0b01011: None,
    0b01100: (('b', 't'), ('envi.IF_COND', 'envi.IF_BRANCH'), ('BI',)),
    0b01101: None,
    0b01110: (('b', 't'), ('envi.IF_COND', 'envi.IF_BRANCH', 'IF_BRANCH_UNLIKELY'), ('BI',)),
    0b01111: (('b', 't'), ('envi.IF_COND', 'envi.IF_BRANCH', 'IF_BRANCH_LIKELY'), ('BI',)),
    0b10000: (('bdnz',), ('envi.IF_COND', 'envi.IF_BRANCH'), ()),
    0b10001: None,
    0b10010: (('bdz',), ('envi.IF_COND', 'envi.IF_BRANCH'), ()),
    0b10011: None,
    0b10100: (('b',), ('envi.IF_BRANCH', 'envi.IF_NOFALL'), ()),
    0b10101: None,
    0b10110: None,
    0b10111: None,
    0b11000: (('bdnz',), ('envi.IF_COND', 'envi.IF_BRANCH', 'IF_BRANCH_UNLIKELY'), ()),
    0b11001: (('bdnz',), ('envi.IF_COND', 'envi.IF_BRANCH', 'IF_BRANCH_LIKELY'), ()),
    0b11010: None,
    0b11011: None,
    0b11100: None,
    0b11101: None,
    0b11110: None,
    0b11111: None,
}

# Table 5-29. BH Field Encodings
# page 319 of EREF_RM.pdf
#
#   BH | Instruction | Hint
#   ---+-------------+-----
#   00 | bclr[l]     | The instruction is a subroutine return
#      | bcctr[l]    | The instruction is not a subroutine return; the target
#      |             | address is likely to be the same as the target address
#      |             | used the preceding time the branch was taken
#   ---+-------------+-----
#   01 | bclr[l]     | The instruction is not a subroutine return; the target
#      |             | address is likely to be the same as the target address
#      |             | used the preceding time the branch was taken
#      | bcctr[l]    | Reserved
#   ---+-------------+-----
#   10 | *           | Reserved
#   ---+-------------+-----
#   11 | *           | The target address is not predictable
#
# Reserved values are represented as None
bcctr_bh_field_flags = {
    0b00: ('IF_BRANCH_PREV_TARGET',),
    0b01: None,
    0b10: None,
    0b11: (),
}

bclr_bh_field_flags = {
    # Don't add the envi.IF_NOFALL flag here because the b*lrl flags shouldn't
    # have NOFALL set even if the assembly technically says it's a function
    # return.
    0b00: ('envi.IF_RET',),
    0b01: ('IF_BRANCH_PREV_TARGET',),
    0b10: None,
    0b11: (),
}

# Table B-17. Standard Coding for Branch Conditions
# page 1105 of EREF_RM.pdf
#
#   Code | Description                | Equivalent | Bit Tested
#   -----+----------------------------+------------+-----------
#   lt   | Less than                  |            | LT
#   le   | Less than or equal         | ng         | GT
#   eq   | Equal                      |            | EQ
#   ge   | Greater than or equal      | nl         | LT
#   gt   | Greater than               |            | GT
#   nl   | Not less than              | ge         | LT
#   ne   | Not equal                  |            | EQ
#   ng   | Not greater than           | le         | GT
#   so   | Summary overflow           |            | SO
#   ns   | Not summary overflow       |            | SO
#   un   | Unordered (after fcmp)     |            | SO
#   nu   | Not unordered (after fcmp) |            | SO
#
# This table takes the true/false value from the BO-generated mnemonic and the
# lower 2 bits of the BI field and turns that into a more logical operation.
# The floating-point specific flag names from the above table are not used.
#
# Table 6-6. BI Operand Settings for CR Fields
# page 415 of EREF_RM.pdf
#
#   CRn Bits | CR Bits | BI    | Description
#   ---------+---------+-------+------------
#   CR0[0]   | 32      | 00000 | Negative (LT)—Set when the result is negative.
#   CR0[1]   | 33      | 00001 | Positive (GT)—Set when the result is positive
#            |         |       | (and not zero).
#   CR0[2]   | 34      | 00010 | Zero (EQ)—Set when the result is zero.
#   CR0[3]   | 35      | 00011 | Summary overflow (SO). Copy of XER[SO] at the
#            |         |       | instruction’s completion.
#
bi_mnems = {
    't': {
        0b00: 'lt',
        0b01: 'gt',
        0b10: 'eq',
        0b11: 'so',
    },
    'f': {
        0b00: 'ge',
        0b01: 'le',
        0b10: 'ne',
        0b11: 'ns',
    }
}

# Build up the opcode list for the 3 different branch conditional instructions:
# - bc (branch conditional)
# - bcctr (branch conditional to count register)
# - bclr (branch to count register)
# and their "branch conditional & link" counterparts.
#
# The bc instruction has an "absolute" (AA) flag indicating if the BD field is
# a relative or absolute branch.
#
# All three instruction forms have a "link" flag (LK) indicating that the link
# register should be set to the return address.
#
# The BO field indicates the conditions under which the branch should be taken
# including the CR bit specified by the BI field and/or the CTR register being
# 0 or not 0.  In addition the BO field specifies if the CTR should be
# decremented, and any branch prediction hints if they are available.
#
# The BI field is used to indicate the condition that the branch decision is
# based on, the upper 3 bits indicate the CRx field, and the lower 2 bits
# indicate which bit in that CRx field to check. All 5 bits together indicate
# the bit in the CR SPR that the true or false condition is checking for.
#
# The bcctr and bclr instructions do not have a BD field, but instead have a BH
# field which indicates additional instruction hints.
aa = ('','a')
lk = ('','l')

# Some utilities to make the following loops simpler
def make_mnem_str(mnem_parts, bi=None, extra=None):
    base = mnem_parts[:]

    if bi is None:
        assert 't' not in mnem_parts and 'f' not in mnem_parts
    else:
        assert 't' in mnem_parts or 'f' in mnem_parts
        if 't' in base:
            t_index = base.index('t')
            base[t_index] = bi_mnems['t'][bi]
        else:
            f_index = base.index('f')
            base[f_index] = bi_mnems['f'][bi]

    mnem = ''.join(base)
    opcode = "INS_" + mnem.upper()

    # add any additional instruction suffix before adding the likely/unlikely
    # hint
    if extra is not None:
        mnem += extra

    # The text mnemonic in the opcode table can have these branch hint flags
    # because the PpcAbstractEmulator._populateOpMethods() function builds up
    # a table of instructions and uses the INS_* opcode constant rather than the
    # mnem string to find the correct emulation function
    if 'IF_BRANCH_LIKELY' in flags:
        mnem += '+'
    elif 'IF_BRANCH_UNLIKELY' in flags:
        mnem += '-'

    return (mnem, opcode)

def update_flags_for_lk(l, flags_tup):
    flags = list(flags_tup)
    # if we link, then this has a fallthrough. period.
    if lk[l] == 'l':
        try:
            flags.remove('envi.IF_NOFALL')
        except ValueError:
            pass
        try:
            br_flag_index = flags.index('envi.IF_BRANCH')
            flags[br_flag_index] = 'envi.IF_CALL'
        except ValueError:
            pass
    return flags

# The bc instruction has both the AA and LK flags
bcopcodes = []
for a in range(2):
    for l in range(2):
        for bo in range(32):
            if bo_simple_stubs[bo] == None:
                continue

            mnbase_tup, flags_tup, opfields_tup = bo_simple_stubs[bo]
            flags = update_flags_for_lk(l, flags_tup)

            # If this an "absolute address" branch, add IF_ABS to the flags
            if aa[a]:
                flags.append('IF_ABS')
            flag_str = ' | '.join(flags)

            # Don't include the 'a' flag in the "opcode" name, the IF_ABS flag
            # that is added for all absolute branch instructions causes the
            # correct target to be calculated when the FORM_B instructions are
            # decoded.
            mnem_base = list(mnbase_tup) + [lk[l]]

            # By default the bc instructions have BO, BI, BD, LK, and AA
            # operands.  This loop turns the BO, LK, and AA operands into the
            # mnemonic.  Depending on the BO field the BI field may not be
            # needed for this encoding.  The opfields_tup value indicates which
            # non-required fields are needed for this specific mnemonic.
            opfields = list(opfields_tup) + ['BD']

            if 'BI' not in opfields_tup:
                # Do the normal instruction generation
                mnem, opcode = make_mnem_str(mnem_base, extra=aa[a])

                num  = 0x40000000 |   bo<<21 | a<<1 | l
                mask = 0x4C000000 | 0x1F<<21 | 1<<1 | 1
                bcopcodes.append((mnem, opcode, (mask, num), opfields, flag_str))

            else:
                # We need to generate 4 opcode entries for this particular
                # branch instruction given the possible values of the lower
                # 2 bits of the BI field where we turn the 5 bit BI field into
                # a 3 bit crBI field.

                bi_index = opfields.index('BI')
                opfields[bi_index] = 'crBI'
                for bi in range(4):
                    mnem, opcode = make_mnem_str(mnem_base, bi, extra=aa[a])

                    num  = 0x40000000 |   bo<<21 |  bi<<16 | a<<1 | l
                    mask = 0x4C000000 | 0x1F<<21 | 0x3<<16 | 1<<1 | 1
                    bcopcodes.append((mnem, opcode, (mask, num), opfields, flag_str))


# The bcctr only uses the LK flag, but also has the BH field
bcctropcodes = []
for l in range(2):
    for bo in range(32):
        if bo_simple_stubs[bo] is None:
            continue

        # bcctr instructions cannot be encoded with BO values that indicate the
        # CTR register should be decremented.  This is represented when bit 2 of
        # BO is 0.
        if BO_DECREMENT(bo):
            continue

        for bh in range(4):
            if bcctr_bh_field_flags[bh] is None:
                continue

            mnbase_tup, flags_tup, opfields_tup = bo_simple_stubs[bo]
            flags = update_flags_for_lk(l, flags_tup)

            # Special case, ensure that envi.IF_RET is not in the flags list
            # unless it is in bcctr_bh_field_flags[bh]
            flags += list(bcctr_bh_field_flags[bh])
            if 'envi.IF_RET' in flags and 'envi.IF_RET' not in bcctr_bh_field_flags[bh]:
                flags.remove('envi.IF_RET')

            flag_str = ' | '.join(flags)

            mnem_base = list(mnbase_tup) + ['ctr', lk[l]]

            opfields = list(opfields_tup)

            # Do the same BI field checks as done for the bc instruction
            if 'BI' not in opfields_tup:
                mnem, opcode = make_mnem_str(mnem_base)

                num  = 0x4C000420 |   bo<<21 |  bh<<11 | l
                mask = 0x4C0007FE | 0x1F<<21 | 0x3<<11 | 1
                bcctropcodes.append((mnem, opcode, (mask, num), opfields, flag_str))

            else:
                bi_index = opfields.index('BI')
                opfields[bi_index] = 'crBI'

                for bi in range(4):
                    mnem, opcode = make_mnem_str(mnem_base, bi)

                    num  = 0x4C000420 |   bo<<21 |  bi<<16 |  bh<<11 | l
                    mask = 0x4C0007FE | 0x1F<<21 | 0x3<<16 | 0x3<<11 | 1
                    bcctropcodes.append((mnem, opcode, (mask, num), opfields, flag_str))


# The bclr only uses the LK flag, but also has the BH field
bclropcodes = []
for l in range(2):
    for bo in range(32):
        if bo_simple_stubs[bo] is None:
            continue

        for bh in range(4):
            if bclr_bh_field_flags[bh] is None:
                continue

            mnbase_tup, flags_tup, opfields_tup = bo_simple_stubs[bo]
            flags = update_flags_for_lk(l, flags_tup)

            # Special case, ensure that envi.IF_RET is not in the flags list
            # unless it is in bclr_bh_field_flags[bh]
            flags += list(bclr_bh_field_flags[bh])
            if 'envi.IF_RET' in flags and 'envi.IF_RET' not in bclr_bh_field_flags[bh]:
                flags.remove('envi.IF_RET')

            flag_str = ' | '.join(flags)

            mnem_base = list(mnbase_tup) + ['lr', lk[l]]

            opfields = list(opfields_tup)

            # Do the same BI field checks as done for the bc and bctr
            # instructions
            if 'BI' not in opfields_tup:
                mnem, opcode = make_mnem_str(mnem_base)

                num  = 0x4C000020 |   bo<<21 |  bh<<11 | l
                mask = 0x4C0007FE | 0x1F<<21 | 0x3<<11 | 1
                bclropcodes.append((mnem, opcode, (mask, num), opfields, flag_str))

            else:
                bi_index = opfields.index('BI')
                opfields[bi_index] = 'crBI'

                for bi in range(4):
                    mnem, opcode = make_mnem_str(mnem_base, bi)

                    num  = 0x4C000020 |   bo<<21 |  bi<<16 |  bh<<11 | l
                    mask = 0x4C0007FE | 0x1F<<21 | 0x3<<16 | 0x3<<11 | 1
                    bclropcodes.append((mnem, opcode, (mask, num), opfields, flag_str))


############
mnems_simplify = [
        'nop',
        'li',
        'lis',
        'la',
        'mr',
        'not',
        'mtcr',
        'lwsync',
        'hwsync',
        'msync',
        'esync',
        'isellt',
        'iselgt',
        'iseleq',
        'waitrsv',
        'cmpw',
        'cmpd',
        'cmpwi',
        'cmpdi',
        'cmplw',
        'cmpld',
        'cmplwi',
        'cmpldi',
        ]

def buildOutput():
    '''
    this is the highest level.
    parses data to get opgrps, builds tables, applies mnems_simplify
    then generates the textual output
    returns three outputs, which are lists of string "lines" to be written to a file
    '''
    out = []
    opgrps = parseData()
    deets = buildTables(opgrps)

    mnems = []
    for grpkey in deets.keys():
        grp = deets.get(grpkey)
        #print(" ==== NEW GROUP ====: ", grpkey)
        for instr in grp:
            #print(instr)
            mnems.append(instr[0])
            #raw_input('waiting...')

    # kick out the constant strings

    # FIELD_* entries
    fieldcounter = 0
    keys = [key for key in FIELD_DATA.keys() if key not in IGNORE_CONSTS]
    keys.sort()
    for field in keys:
        ffield = field.replace(' ','').replace('-','_')
        out.append("FIELD_%s = %d" % (ffield, fieldcounter))
        fieldcounter += 1

    keys = [key for key in FIELD_M_DATA.keys() if key not in IGNORE_CONSTS]
    keys.sort()
    for field in keys:
        ffield = field.replace(' ','').replace('-','_')
        out.append("FIELD_%s = %d" % (ffield, fieldcounter))
        fieldcounter += 1
    out.append('')

    # CATEGORIES
    catcounter = 0
    for cat in cat_names:
        out.append('CAT_%s = 1<<%d' % (cat, catcounter))
        catcounter += 1
    out.append('')
    out.append('CATEGORIES = { y : x  for x,y in globals().items() if x.startswith("CAT_")}')
    out.append('')

    # FORMS
    form_names = []
    formcounter = 0
    keys = [form for form in FORM_CONST.values() ]
    keys.append('FORM_X_2') # used for VLE decoding (per Mitch)
    keys.sort()

    for form in keys:
        out.append("%s = %d" % (form, formcounter))
        form_names.append("    %d : %r," % (formcounter, form))
        formcounter += 1

    out.append('')
    out.append('form_names = {')
    out.extend(form_names)
    out.append('}')


    # MNEMONICS list
    out.append('')
    out.append('mnems = (')

    # Pool all of the mnemonics together in one big list with any trailing '.'
    # stripped so we can ensure that only unique mnemonics are output.

    mnem_array  = [m if m[-1] != '.' else m[:-1] for m in mnems]
    mnem_array += [m if m[-1] != '.' else m[:-1] for m in mnems_simplify]

    # For the branch conditional mnemonics also make sure that the "branch
    # X absolute" mnemonic of 'a' is not included.  The relative/absolute branch
    # target difference is sorted out when the FORM_B instructions are decoded.
    def fix_branch_mnem(mnem):
        if mnem.endswith(('a-', 'a+')):
            return mnem[:-2]
        elif mnem.endswith(('a', '-', '+')):
            return mnem[:-1]
        else:
            return mnem

    mnem_array += [fix_branch_mnem(m) for m, _, _, _, _ in bcopcodes]
    mnem_array += [fix_branch_mnem(m) for m, _, _, _, _ in bcctropcodes]
    mnem_array += [fix_branch_mnem(m) for m, _, _, _, _ in bclropcodes]

    # Turn this list into a set, and then back again so we can sort the list
    # alphabetically before outputting to the const_gen.py output buffer.
    mnem_array = sorted(list(set(mnem_array )))
    mnem_out_list = ['    %r,' % m for m in mnem_array]
    out.extend(mnem_out_list)

    out.append(')')
    out.append('''
inscounter = 0
for _mnem in mnems:
    _name = "INS_" + _mnem.upper()
    if _name in globals():
        msg = 'ERROR: cannot assign %r = %d (currently %r = %d)' % (_name, inscounter, _name, globals()[_name])
        raise Exception(msg)
    globals()[_name] = inscounter
    inscounter += 1

from . import const_gen_vle
VLE_INS_OFFSET = inscounter
for _mnem in const_gen_vle.mnems:
    _name = "INS_" + _mnem.upper()
    if _name in globals():
        if globals()[_name] >= inscounter:
            msg = 'ERROR: cannot assign %r = %d (currently %r = %d)' % (_name, inscounter, _name, globals()[_name])
            raise Exception(msg)
        else:
            # Ignore, no need to add a VLE-specific opcode
            pass
    else:
        globals()[_name] = inscounter
        inscounter += 1
''')

    # additional CONSTs
    out.append('IF_NONE = 0')
    out.append('IF_RC = 1<<8')
    out.append('IF_ABS = 1<<9')
    out.append('IF_BRANCH_LIKELY = 1<<10')
    out.append('IF_BRANCH_UNLIKELY = 1<<11')
    out.append('IF_BRANCH_PREV_TARGET = 1<<12')
    out.append('IF_MEM_EA = 1<<13')
    out.append('')

    # now build the instruction tables.
    out2 = []
    out2.append('import envi')
    out2.append('from .const import *')
    out2.append('instr_dict = {')
    for grpkey in deets.keys():
        grp = deets.get(grpkey)
        out2.append('    %s : (' % grpkey)
        for instr in grp:
            mnem, grptxt, form, cat, fields, statbits, varfs, stats, nfields = instr

            # create mask and value, parse FIELD data (operands).
            mask = 0
            val  = 0
            #overlaps = []
            for n, bits, start, sz, typ in nfields:
                if typ != THING_STATIC:
                    continue
                pmask = e_bits.b_masks[sz]

                # now we have to hunt down any / bytes
                for x in range(sz):
                    if bits[x] == '/':
                        bits = bits[:x] + '0' + bits[x+1:]
                        pmask &= ~(1<<(sz-x-1))

                pval = int(bits, 2)

                # now shift them into place...
                shl = 32 - sz - start
                pval <<= shl
                pmask <<= shl
                #overlaps.append((pval, pmask))
                val |= pval
                mask |= pmask


            fields = [field for field in nfields if field[4] == THING_VAR]
            print("Mask/Val: ", bin(mask), bin(val), hex(mask), hex(val), mnem, fields)

            # generate FIELDS output string
            fout = []
            for field in fields:
                n, fname, start, sz, ftyp = field

                # HACK: if mtfsfi has a field type of IMM change it to UIMM
                if mnem.startswith('mtfsfi') and fname == 'IMM':
                    fname = 'UIMM'

                fname = fname.strip().replace('-','_').replace(' ','')
                shr = 32 - (start + sz)
                fmask = e_bits.b_masks[sz]

                ###### fixup SIMM
                if fname == 'SIMM':
                    fname = 'SIMM%d' % sz

                fout.append(" ( '%s', %s, %s, 0x%x )," % (fname, "FIELD_"+fname, shr, fmask))


            #### fix up the operand ordering where possible.  this is faster and simpler than doing it in the decoder
            if len(fout) > 1 and 'FIELD_rS' in fout[0] and form not in  ('EVX', ):
                if mnem not in ('evstddepx', ) and not mnem.startswith('st'):    # WONKY AS SHIT!
                    temp = fout[0]
                    fout[0] = fout[1]
                    fout[1] = temp

            if len(fout) == 4 and 'FIELD_frC' in fout[3] and form == 'A':
                temp = fout[2]
                fout[2] = fout[3]
                fout[3] = temp

            if len(fout) >2 and 'FIELD_UIMM' in fout[1]:
                temp = fout[1]
                fout[1] = fout[2]
                fout[2] = temp

            ##################### OPERAND ORDERING COMPLETE #####################

            form_const = FORM_CONST[form]

            # calculate flags...
            iflags = []
            if mnem.endswith('.'):
                iflags.append('IF_RC')
            if mnem[0] == 'b':
                if mnem.startswith('bc'):
                    iflags.append('envi.IF_COND')

                if mnem in ('b', 'ba', ):
                    iflags.append('envi.IF_BRANCH | envi.IF_NOFALL')
                elif mnem in ('bc', 'bca', 'bcctr', 'bclr'):
                    iflags.append('envi.IF_BRANCH')
                elif mnem in ('bl', 'bla', 'bcl', 'bcla', 'bcctrl', 'bclrl'):
                    iflags.append('envi.IF_CALL')

                if mnem in ('ba', 'bca', 'bla', 'bcla',):
                    iflags.append('IF_ABS')

            elif mnem.startswith('rf'):
                iflags.append('envi.IF_RET | envi.IF_NOFALL')

            if mnem in rAnegades:
                iflags.append('IF_MEM_EA')

            # last flag check
            if not len(iflags):
                iflags.append("IF_NONE")

            # mask, value, (data)
            # data is ( mnem, opcode, form, cat, operands, iflags)
            #
            ncat = "CAT_" + cat.upper().replace('.', '_').replace(', ', ' | CAT_').replace(',',' | CAT_')

            # Some branch mnemonics remove the need to have to parse out certain
            # operand fields.  The menomic for each branch instruction will
            # specify which fields should be included from this list.  This
            # includes shrinking the standard BI field into a 3-bit field that
            # specify the CR to use for that instruction, rather than the full
            # CR bit mask.
            bc_operands = {
                'BO': "( 'BO', FIELD_BO, 21, 0x1f )",
                'BI': "( 'BI', FIELD_BI, 16, 0x1f )",
                'BD': "( 'BD', FIELD_BD, 2, 0x3fff )",
                'crBI': "( 'crBI', FIELD_crBI, 18, 0x7 )",
                'BH': "( 'BH', FIELD_BH, 10, 0x3 )",
            }

            ###### fixup bc
            if mnem == 'bc':
                for fmnem, bcopcode, (fmask, fval), opfields, fflags in bcopcodes:
                    if len(opfields) == 1:
                        operands = '( %s, )' % bc_operands[opfields[0]]
                    else:
                        operands = '( ' + ', '.join(bc_operands[o] for o in opfields) + ' )'
                    data = "'%s', %s, %s, %s, %s, %s" % (fmnem, bcopcode, form_const, ncat, operands, fflags)
                    out2.append('        (0x%x, 0x%x, ( %s ), ),' % (fmask, fval, data))
                #continue

            if mnem == 'bclr':
                for fmnem, bcopcode, (fmask, fval), opfields, fflags in bclropcodes:
                    if len(opfields) == 1:
                        operands = '( %s, )' % bc_operands[opfields[0]]
                    else:
                        operands = '( ' + ', '.join(bc_operands[o] for o in opfields) + ' )'
                    data = "'%s', %s, %s, %s, %s, %s" % (fmnem, bcopcode, form_const, ncat, operands, fflags)
                    out2.append('        (0x%x, 0x%x, ( %s ), ),' % (fmask, fval, data))
                #continue
            #if mnem == 'bclrl':
            #    continue # this should be covered by the previous generator

            if mnem == 'bcctr':
                for fmnem, bcopcode, (fmask, fval), opfields, fflags in bcctropcodes:
                    if len(opfields) == 1:
                        operands = '( %s, )' % bc_operands[opfields[0]]
                    else:
                        operands = '( ' + ', '.join(bc_operands[o] for o in opfields) + ' )'
                    data = "'%s', %s, %s, %s, %s, %s" % (fmnem, bcopcode, form_const, ncat, operands, fflags)
                    out2.append('        (0x%x, 0x%x, ( %s ), ),' % (fmask, fval, data))
                #continue

            #if mnem == 'bcctrl':
            #    continue # this should be covered by the previous generator

            operands = "( " + ''.join(fout) + ") "
            opcode = "INS_" + mnem.replace('.','').upper()
            data = "'%s', %s, %s, %s, %s, %s" % (mnem, opcode, form_const, ncat, operands, ' | '.join(iflags))

            out2.append('        (0x%x, 0x%x, ( %s ), ),' % (mask, val, data))

        # ADDITIONAL INSTRUCTIONS NOT INCLUDED IN EREF BREAKDOWN (manual)
        for tag, mask, val, data in EXTRA_OPCODES.get(grpkey, []):
            data = "'%s', %s, %s, %s, %s, %s" % data
            if tag == TAG_PREPEND:
                out2.insert(0,  '        (0x%x, 0x%x, ( %s ), ),' % (mask, val, data))
            else:
                out2.append(    '        (0x%x, 0x%x, ( %s ), ),' % (mask, val, data))

        out2.append('    ),')
    out2.append('}',)

    out3 = []
    out3.append('# THIS SHOULD BE COPIED INTO disasm.py FOR DEPENDENCIES SAKE')
    out3.append('OPERCLASSES = {')
    operkeys = [key for key in FIELD_DATA.keys() if key not in IGNORE_CONSTS]
    operkeys.extend([key for key in FIELD_M_DATA.keys() if key not in IGNORE_CONSTS])
    operkeys.sort()
    for key in operkeys:
        nkey = key.replace('-','_').replace(' ','')
        if key[0] == 'r':
            out3.append('    FIELD_%s : PpcRegOper,' % (nkey))
        elif key[0] == 'v':
            out3.append('    FIELD_%s : PpcVRegOper,' % (nkey))
        elif key[0:2] == 'fr':
            out3.append('    FIELD_%s : PpcFRegOper,' % (nkey))
        elif nkey.startswith('crb'):
            out3.append('    FIELD_%s : PpcCBRegOper,' % (nkey))
        elif nkey.startswith('cr'):
            out3.append('    FIELD_%s : PpcCRegOper,' % (nkey))
        elif nkey == 'D':
            out3.append('    FIELD_%s : PpcSImm16Oper,' % (nkey))
        elif nkey == 'DE':
            out3.append('    FIELD_%s : PpcSImm12Oper,' % (nkey))
        elif nkey == 'SIMM5':
            out3.append('    FIELD_%s : PpcSImm5Oper,' % (nkey))
        elif nkey == 'SIMM16':
            out3.append('    FIELD_%s : PpcSImm16Oper,' % (nkey))
        elif nkey == 'UIMM1':
            out3.append('    FIELD_%s : PpcUImm1Oper,' % (nkey))
        elif nkey == 'UIMM2':
            out3.append('    FIELD_%s : PpcUImm2Oper,' % (nkey))
        elif nkey == 'UIMM3':
            out3.append('    FIELD_%s : PpcUImm3Oper,' % (nkey))
        elif key == 'BI':
            out3.append('    FIELD_%s : PpcCBRegOper,' % (nkey))
        elif key == 'BD':
            out3.append('    FIELD_%s : PpcSImm3Oper,' % (nkey))
        elif key == 'DS':
            out3.append('    FIELD_%s : PpcSImm3Oper,' % (nkey))
        else:
            out3.append('    FIELD_%s : PpcImmOper,' % (nkey))

    out3.append('}')

    utest = '''
import sys
import struct
import vivisect
import envi.archs.ppc.disasm as eapd
import envi.memcanvas as e_memcanvas

"""
This module generates unit-test-cases (.py) and binary values to run through other disassmblers (.bin)
"""

def make_unit_tests(outfile='test_ppc_by_cat'):
    vw = vivisect.VivWorkspace()

    out = []
    tests = [test_code, 'instrs_by_category = [']
    scanv = e_memcanvas.StringMemoryCanvas(vw)

    for cat in eapd.CATEGORIES.keys():
        d = eapd.PpcDisasm(options=cat)
        d.__ARCH__ = 0
        catname = eapd.CATEGORIES.get(cat)

        print("\\n====== CAT: %r ======" % catname)
        for key,instrlist in eapd.instr_dict.items():
            for instrline in instrlist:
                opcodenum = instrline[1]
                opcat = instrline[2][3]
                if not opcat & cat:
                    continue

                shifters = [(shl, mask) for nm,tp,shl,mask in instrline[2][-2]]
                shifters.sort()
                for oidx in range(len(shifters)):
                    shl, mask = shifters[oidx]
                    opcodenum |= (len(shifters)-oidx & mask) << shl

                opbin = struct.pack(">I", opcodenum)

                try:
                    op = d.disasm(opbin, 0, 0x4000)
                    print("0x%.8x:  %s" % (opcodenum, op))

                    scanv.clearCanvas()
                    op.render(scanv)
                    # print("render:  %s" % repr(scanv.strval))
                    tests.append("        (%s, '%.8x', '%s', '%s', {})," % (catname, opcodenum, op, scanv.strval))

                except Exception as  e:
                    sys.stderr.write("ERROR: 0x%x: %r\\n" % (opcodenum, e))
                    import traceback
                    traceback.print_exc()

                out.append(opbin)
    with open('%s.bin' % outfile, 'wb') as f:
        f.write(b''.join(out))
    tests.append("]\\n")
    with open('%s.py' % outfile, 'w') as f:
        f.write('\\n'.join(tests))


test_code = """
import envi
import binascii
import unittest
import vivisect
import envi.archs.ppc.disasm as eapd
import envi.memcanvas as e_memcanvas
from envi.const import *
from envi.archs.ppc.const import *

class PpcInstructionSetByCategories(unittest.TestCase):
    def test_instrs_by_cat(self):
        \'\'\'
        test opcode disassembly and emulation by PPC Category
        \'\'\'
        vw = vivisect.VivWorkspace()
        vw.setMeta('Architecture', 'ppc32-embedded')
        vw.setEndian(ENDIAN_MSB)
        emu = vw.getEmulator()
        snap = emu.getEmuSnap()

        scanv = e_memcanvas.StringMemoryCanvas(vw)

        count = 0
        lastcat = None
        for cat, bytez, reprOp, renderOp, emutests in instrs_by_category:
            if cat != lastcat:
                d = eapd.PpcDisasm(options=cat)
                d.__ARCH__ = 0

            count += 1
            opbin = binascii.unhexlify(bytez)
            try:
                op = d.disasm(opbin, 0, 0x4000)

            except envi.InvalidInstruction:
                self.fail("Failed to parse opcode bytes: %s (case: %s, expected: %s)" % (bytez, reprOp, reprOp))
            except Exception as e:
                self.fail("(%r) Failed to parse opcode bytes: %s (case: %s, expected: %s)" % (e, bytez, reprOp, reprOp))
            # print("'%s', 0x%x, '%s' == '%s'" % (bytez, va, repr(op), reprOp))

            try:
                self.assertEqual(repr(op), reprOp)

                scanv.clearCanvas()
                op.render(scanv)
                self.assertEqual(scanv.strval, renderOp)

            except AssertionError:
                self.fail("Failing match for case %s (%s != %s)" % (reprOp, repr(op), reprOp))


            # test emulation
            emu.setEmuSnap(snap)
            self.do_emutsts(emu, bytez, op, emutests)

    def validateEmulation(self, emu, op, setters, tests, tidx=0):
        \'\'\'
        Run emulation tests.  On successful test, returns True
        \'\'\'
        # first set any environment stuff necessary
        emu.setStackCounter(0xbfb07000) # default stack start with top at bfb08000

        # setup flags and registers
        settersrepr = '( %r )' % (', '.join(["%s=%s" % (s, hex(v)) for s,v in setters]))
        testsrepr = '( %r )' % (', '.join(["%s==%s" % (s, hex(v)) for s,v in tests]))

        for tgt, val in setters:
            try:
                # try register first
                emu.setRegisterByName(tgt, val)

            except e_exc.InvalidRegisterName:
                # it's not a register
                if type(tgt) == str:
                    emu.setRegister(eval(tgt), val)

                elif type(tgt) in (long, int):
                    # it's an address
                    emu.writeMemValue(tgt, val, 1) # limited to 1-byte writes currently

                else:
                    raise Exception( "Funkt up Setting: (%r test#%d)  %s = 0x%x" % (op, tidx, tgt, val) )

        emu.executeOpcode(op)

        if not len(tests):
            success = True
        else:
            # start out as failing...
            success = False

        for tgt, val in tests:
            try:
                # try register first
                testval = emu.getRegisterByName(tgt)
                if testval == val:
                    success = True
                else:  # should be an else
                    raise Exception("FAILED(name_reg): (%r test#%d)  %s  !=  0x%x (observed: 0x%x) \\\\n\\\\t(setters: %r)\\\\n\\\\t(test: %r)" % (op, tidx, tgt, val, testval, settersrepr, testsrepr))

            except e_exc.InvalidRegisterName:
                # it's not a register
                if type(tgt) == str:
                    # it's a flag
                    testval = emu.getRegister(eval(tgt))
                    if testval == val:
                        success = True
                    else:
                        raise Exception("FAILED(raw_reg): (%r test#%d)  %s  !=  0x%x (observed: 0x%x) \\\\n\\\\t(setters: %r)\\\\n\\\\t(test: %r)" % (op, tidx, tgt, val, testval, settersrepr, testsrepr))

                elif type(tgt) in (long, int):
                    # it's an address
                    testval = emu.readMemValue(tgt, 1)
                    if testval == val:
                        success = True
                    else:
                        raise Exception("FAILED(mem): (%r test#%d)  0x%x  !=  0x%x (observed: 0x%x) \\\\n\\\\t(setters: %r)\\\\n\\\\t(test: %r)" % (op, tidx, tgt, val, testval, settersrepr, testsrepr))

                elif type(tgt) == tuple:
                    # it's an address:size tuple (size must be 1, 2, 4, or 8)
                    addr, size = tgt
                    testval = emu.readMemValue(addr, size)
                    if testval == val:
                        success = True
                    else:
                        raise Exception("FAILED(mem): (%r test#%d)  0x%x  !=  0x%x (observed: 0x%x) \\\\n\\\\t(setters: %r)\\\\n\\\\t(test: %r)" % (op, tidx, tgt, val, testval, settersrepr, testsrepr))

                else:
                    raise Exception( "Funkt up test (%r test#%d) : %s == %s" % (op, tidx, tgt, val) )

        return success

    def do_emutsts(self, emu, bytez, op, emutests):
        \'\'\'
        Setup and Perform Emulation Tests per architecture variant
        \'\'\'
        bademu = 0
        goodemu = 0
        # if we have a special test lets run it
        for tidx, sCase in enumerate(emutests):
            #allows us to just have a result to check if no setup needed
            if 'tests' in sCase:
                setters = ()
                if 'setup' in sCase:
                    setters = sCase['setup']

                tests = sCase['tests']
                if self.validateEmulation(emu, op, (setters), (tests), tidx):
                    goodemu += 1
                else:
                    bademu += 1
                    raise Exception( "FAILED emulation (special case): %.8x %s - %s" % (op.va, bytez, op) )

            else:
                bademu += 1
                raise Exception( "FAILED special case test format bad:  Instruction test does not have a 'tests' field: %.8x %s - %s" % (op.va, bytez, op))

        return goodemu, bademu


"""
if __name__ == '__main__':
    make_unit_tests()

'''

    return out, out2, out3, utest


# FIXME: unit-tests using the masks for each instruction to generate them.

if __name__ == '__main__':
    out,out2,out3,utest = buildOutput()
    with open('const_gen.py','w') as f:
        f.write( '\n'.join(out))
    with open('ppc_tables.py','w') as f:
        f.write( '\n'.join(out2))
    with open('disasm_gen.py','w') as f:
        f.write( '\n'.join(out3))
    with open('gen_test_ppc.py','w') as f:
        f.write(utest)


'''
1
d = UIMM * 8
2
 d = UIMM * 4
3
d = UIMM * 2
'''


