from typing import Dict, List, Tuple, Optional, Any, Union

import re

'''
VLE version of mnems.py, parsing VLE Instruction table from VLE PEM.
'''

# Table B-3 VLE Instructions sorted by opcode from VLE PEM
# Order:
#   Form
#   Opcode (hexadecimal) 1
#   Mode Dep.
#   Priv2
#   Cat2
#   Mnemonic
#   Instruction
# Empty lines and lines starting with '#' are ignored
# A series of newlines annotates a page break in the manual

table_contents = '''
C
0000----
VLE
se_illegal
Illegal
C
0001----
VLE
se_isync
Instruction Synchronize
C
0002----
VLE
se_sc
System Call
C
0004----
VLE
se_blr
Branch To Link Register [and Link]
C
0006----
VLE
se_bctr
Branch To Count Register [and Link]
C
0008----
P
VLE
se_rfi
Return from Interrupt
C
0009----
P
VLE
se_rfci
Return From Critical Interrupt
C
000A----
P
VLE
se_rfdi
Return From Debug Interrupt
C
000B----
P
VLE
se_rfmci
Return From Machine Check Interrupt
R
0020----
VLE
se_not
NOT Short Form
R
0030----
VLE
se_neg
Negate Short Form
R
0080----
VLE
se_mflr
Move From Link Register
R
0090----
VLE
se_mtlr
Move To Link Register





R
00A0----
VLE
se_mfctr
Move From Count Register
R
00B0----
VLE
se_mtctr
Move To Count Register
R
00C0----
VLE
se_extzb
Extend Zero Byte
R
00D0----
VLE
se_extsb
Extend Sign Byte Short Form
R
00E0----
VLE
se_extzh
Extend Zero Halfword
R
00F0----
VLE
se_extsh
Extend Sign Halfword Short Form
RR
0100----
VLE
se_mr
Move Register
RR
0200----
VLE
se_mtar
Move To Alternate Register
RR
0300----
VLE
se_mfar
Move from Alternate Register
RR
0400----
VLE
se_add
Add Short Form
RR
0500----
VLE
se_mullw
Multiply Low Word Short Form
RR
0600----
VLE
se_sub
Subtract
RR
0700----
VLE
se_subf
Subtract From Short Form
RR
0C00----
VLE
se_cmp
Compare Word
RR
0D00----
VLE
se_cmpl
Compare Logical Word
RR
0E00----
VLE
se_cmph
Compare Halfword Short Form
RR
0F00----
VLE
se_cmphl
Compare Halfword Logical Short Form
VX
10000000
VEC
vaddubm
Vector Add Unsigned Byte Modulo
VX
10000002
VEC
vmaxub
Vector Maximum Unsigned Byte
VX
10000004
VEC
vrlb
Vector Rotate Left Byte
VX
10000006
VEC
vcmpequb[.]
Vector Compare Equal To Unsigned Byte
VX
10000008
VEC
vmuloub
Vector Multiply Odd Unsigned Byte
VX
1000000A
VEC
vaddfp
Vector Add Floating-Point
VX
1000000C
VEC
vmrghb
Vector Merge High Byte
VX
1000000E
VEC
vpkuhum
Vector Pack Unsigned Halfword Unsigned Modulo
X
10000010
SR
LIM
mulhhwu[o][.]
Multiply High Halfword to Word Unsigned
X
10000018
SR
LIM
machhwu[o][.]
Multiply Accumulate High Halfword to Word Modulo Unsigned
VA
10000020
VEC
vmhaddshs
Vector Multiply-High-Add Signed Halfword Saturate
VA
10000021
VEC
vmhraddshs
Vector Multiply-High-Round-Add Signed Halfword Saturate
VA
10000022
VEC
vmladduhm
Vector Multiply-Low-Add Unsigned Halfword Modulo
VA
10000024
VEC
vmsumubm
Vector Multiply-Sum Unsigned Byte Modulo




VA
10000025
VEC
vmsummbm
Vector Multiply-Sum Mixed Byte Modulo
VA
10000026
VEC
vmsumuhm
Vector Multiply-Sum Unsigned Halfword Modulo
VA
10000027
VEC
vmsumuhs
Vector Multiply-Sum Unsigned Halfword Saturate
VA
10000028
VEC
vmsumshm
Vector Multiply-Sum Signed Halfword Modulo
VA
10000029
VEC
vmsumshs
Vector Multiply-Sum Signed Halfword Saturate
VA
1000002A
VEC
vsel
Vector Select
VA
1000002B
VEC
vperm
Vector Permute
VA
1000002C
VEC
vsldoi
Vector Shift Left Double by Octet Immediate
VA
1000002E
VEC
vmaddfp
Vector Multiply-Add Single-Precision
VA
1000002F
VEC
vnmsubfp
Vector Negative Multiply-Subtract Single-Precision
VX
10000040
VEC
vadduhm
Vector Add Unsigned Halfword Modulo
VX
10000042
VEC
vmaxuh
Vector Maximum Unsigned Halfword
VX
10000044
VEC
vrlh
Vector Rotate Left Halfword
VX
10000046
VEC
vcmpequh[.]
Vector Compare Equal To Unsigned Halfword
VX
10000048
VEC
vmulouh
Vector Multiply Odd Unsigned Halfword
VX
1000004A
VEC
vsubfp
Vector Subtract Single-Precision
VX
1000004C
VEC
vmrghh
Vector Merge High Halfword
VX
1000004E
VEC
vpkuwum
Vector Pack Unsigned Word Unsigned Modulo
X
10000050
SR
LIM
mulhhw[o][.]
Multiply High Halfword to Word Signed
X
10000058
SR
LIM
machhw[o][.]
Multiply Accumulate High Halfword to Word Modulo Signed
X
1000005C
SR
LIM
nmachhw[o][.]
Negative Multiply Accumulate High Halfword to Word Modulo Signed
VX
10000080
VEC
vadduwm
Vector Add Unsigned Word Modulo
VX
10000082
VEC
vmaxuw
Vector Maximum Unsigned Word
VX
10000084
VEC
vrlw
Vector Rotate Left Word
VX
10000086
VEC
vcmpequw[.]
Vector Compare Equal To Unsigned Word
VX
1000008C
VEC
vmrghw
Vector Merge High Word
VX
1000008E
VEC
vpkuhus
Vector Pack Unsigned Halfword Unsigned Saturate
X
10000098
SR
LIM
machhwsu[o][.]
Multiply Accumulate High Halfword to Word Saturate Unsigned
VX
100000C6
VEC
vcmpeqfp[.]
Vector Compare Equal To Single-Precision
VX
100000CE
VEC
vpkuwus
Vector Pack Unsigned Word Unsigned Saturate




X
100000D8
SR
LIM
machhws[o][.]
Multiply Accumulate High Halfword to Word Saturate Signed
X
100000DC
SR
LIM
nmachhws[o][.]
Negative Multiply Accumulate High Halfword to Word Saturate Signed
VX
10000102
VEC
vmaxsb
Vector Maximum Signed Byte
VX
10000104
VEC
vslb
Vector Shift Left Byte
VX
10000108
VEC
vmulosb
Vector Multiply Odd Signed Byte
VX
1000010A
VEC
vrefp
Vector Reciprocal Estimate Single-Precision
VX
1000010C
VEC
vmrglb
Vector Merge Low Byte
VX
1000010E
VEC
vpkshus
Vector Pack Signed Halfword Unsigned Saturate
X
10000110
SR
LIM
mulchwu[o][.]
Multiply Cross Halfword to Word Unsigned
X
10000118
SR
LIM
macchwu[o][.]
Multiply Accumulate Cross Halfword to Word Modulo Unsigned
VX
10000142
VEC
vmaxsh
Vector Maximum Signed Halfword
VX
10000144
VEC
vslh
Vector Shift Left Halfword
VX
10000148
VEC
vmulosh
Vector Multiply Odd Signed Halfword
VX
1000014A
VEC
vrsqrtefp
Vector Reciprocal Square Root Estimate Single-Precision
VX
1000014C
VEC
vmrglh
Vector Merge Low Halfword
VX
1000014E
VEC
vpkswus
Vector Pack Signed Word Unsigned Saturate
X
10000150
SR
LIM
mulchw[o][.]
Multiply Cross Halfword to Word Signed
X
10000158
SR
LIM
macchw[o][.]
Multiply Accumulate Cross Halfword to Word Modulo Signed
X
1000015C
SR
LIM
nmacchw[o][.]
Negative Multiply Accumulate Cross Halfword to Word Modulo Signed
VX
10000180
VEC
vaddcuw
Vector Add Carryout Unsigned Word
VX
10000182
VEC
vmaxsw
Vector Maximum Signed Word
VX
10000184
VEC
vslw
Vector Shift Left Word
VX
1000018A
VEC
vexptefp
Vector 2 Raised to the Exponent Estimate Floating-Point
VX
1000018C
VEC
vmrglw
Vector Merge Low Word
VX
1000018E
VEC
vpkshss
Vector Pack Signed Halfword Signed Saturate
X
10000198
SR
LIM
macchwsu[o][.]
Multiply Accumulate Cross Halfword to Word Saturate Unsigned
VX
100001C4
VEC
vsl
Vector Shift Left




VX
100001C6
VEC
vcmpgefp[.]
Vector Compare Greater Than or Equal To Single-Precision
VX
100001CA
VEC
vlogefp
Vector Log Base 2 Estimate Floating-Point
VX
100001CE
VEC
vpkswss
Vector Pack Signed Word Signed Saturate
X
100001D8
SR
LIM
macchws[o][.]
Multiply Accumulate Cross Halfword to Word Saturate Signed
X
100001DC
SR
LIM
nmacchws[o][.]
Negative Multiply Accumulate Cross Halfword to Word Saturate Signed
EVX
10000200
SP
evaddw
Vector Add Word
VX
10000200
VEC
vaddubs
Vector Add Unsigned Byte Saturate
EVX
10000202
SP
evaddiw
Vector Add Immediate Word
VX
10000202
VEC
vminub
Vector Minimum Unsigned Byte
EVX
10000204
SP
evsubfw
Vector Subtract from Word
VX
10000204
VEC
vsrb
Vector Shift Right Byte
EVX
10000206
SP
evsubifw
Vector Subtract Immediate from Word
VX
10000206
VEC
vcmpgtub[.]
Vector Compare Greater Than Unsigned Byte
EVX
10000208
SP
evabs
Vector Absolute Value
VX
10000208
VEC
vmuleub
Vector Multiply Even Unsigned Byte
EVX
10000209
SP
evneg
Vector Negate
EVX
1000020A
SP
evextsb
Vector Extend Sign Byte
VX
1000020A
VEC
vrfin
Vector Round to Single-Precision Integer Nearest
EVX
1000020B
SP
evextsh
Vector Extend Sign Halfword
EVX
1000020C
SP
evrndw
Vector Round Word
VX
1000020C
VEC
vspltb
Vector Splat Byte
EVX
1000020D
SP
evcntlzw
Vector Count Leading Zeros Bits Word
EVX
1000020E
SP
evcntlsw
Vector Count Leading Sign Bits Word
VX
1000020E
VEC
vupkhsb
Vector Unpack High Signed Byte
EVX
1000020F
SP
brinc
Bit Reverse Increment
EVX
10000211
SP
evand
Vector AND
EVX
10000212
SP
evandc
Vector AND with Complement
EVX
10000216
SP
evxor
Vector XOR
EVX
10000217
SP
evor
Vector OR
EVX
10000218
SP
evnor
Vector NOR




EVX
10000219
SP
eveqv
Vector Equivalent
EVX
1000021B
SP
evorc
Vector OR with Complement
EVX
1000021E
SP
evnand
Vector NAND
EVX
10000220
SP
evsrwu
Vector Shift Right Word Unsigned
EVX
10000221
SP
evsrws
Vector Shift Right Word Signed
EVX
10000222
SP
evsrwiu
Vector Shift Right Word Immediate Unsigned
EVX
10000223
SP
evsrwis
Vector Shift Right Word Immediate Signed
EVX
10000224
SP
evslw
Vector Shift Left Word
EVX
10000226
SP
evslwi
Vector Shift Left Word Immediate
EVX
10000228
SP
evrlw
Vector Rotate Left Word
EVX
10000229
SP
evsplati
Vector Splat Immediate
EVX
1000022A
SP
evrlwi
Vector Rotate Left Word Immediate
EVX
1000022B
SP
evsplatfi
Vector Splat Fractional Immediate
EVX
1000022C
SP
evmergehi
Vector Merge High
EVX
1000022D
SP
evmergelo
Vector Merge Low
EVX
1000022E
SP
evmergehilo
Vector Merge High/Low
EVX
1000022F
SP
evmergelohi
Vector Merge Low/High
EVX
10000230
SP
evcmpgtu
Vector Compare Greater Than Unsigned
EVX
10000231
SP
evcmpgts
Vector Compare Greater Than Signed
EVX
10000232
SP
evcmpltu
Vector Compare Less Than Unsigned
EVX
10000233
SP
evcmplts
Vector Compare Less Than Signed
EVX
10000234
SP
evcmpeq
Vector Compare Equal
VX
10000240
VEC
vadduhs
Vector Add Unsigned Halfword Saturate
VX
10000242
VEC
vminuh
Vector Minimum Unsigned Halfword
VX
10000244
VEC
vsrh
Vector Shift Right Halfword
VX
10000246
VEC
vcmpgtuh[.]
Vector Compare Greater Than Unsigned Halfword
VX
10000248
VEC
vmuleuh
Vector Multiply Even Unsigned Halfword
VX
1000024A
VEC
vrfiz
Vector Round to Single-Precision Integer toward Zero
VX
1000024C
VEC
vsplth
Vector Splat Halfword
VX
1000024E
VEC
vupkhsh
Vector Unpack High Signed Halfword
EVSEL
10000278
SP
evsel
Vector Select
EVX
10000280
SP.FV
evfsadd
Vector Floating-Point Single-Precision Add



VX
10000280
VEC
vadduws
Vector Add Unsigned Word Saturate
EVX
10000281
SP.FV
evfssub
Vector Floating-Point Single-Precision Subtract
VX
10000282
VEC
vminuw
Vector Minimum Unsigned Word
EVX
10000284
SP.FV
evfsabs
Vector Floating-Point Single-Precision Absolute Value
VX
10000284
VEC
vsrw
Vector Shift Right Word
EVX
10000285
SP.FV
evfsnabs
Vector Floating-Point Single-Precision Negative Absolute Value
EVX
10000286
SP.FV
evfsneg
Vector Floating-Point Single-Precision Negate
VX
10000286
VEC
vcmpgtuw[.]
Vector Compare Greater Than Unsigned Word
EVX
10000288
SP.FV
evfsmul
Vector Floating-Point Single-Precision Multiply
EVX
10000289
SP.FV
evfsdiv
Vector Floating-Point Single-Precision Divide
VX
1000028A
VEC
vrfip
Vector Round to Single-Precision Integer toward Positive Infinity
EVX
1000028C
SP.FV
evfscmpgt
Vector Floating-Point Single-Precision Compare Greater Than
VX
1000028C
VEC
vspltw
Vector Splat Word
EVX
1000028D
SP.FV
evfscmplt
Vector Floating-Point Single-Precision Compare Less Than
EVX
1000028E
SP.FV
evfscmpeq
Vector Floating-Point Single-Precision Compare Equal
VX
1000028E
VEC
vupklsb
Vector Unpack Low Signed Byte
EVX
10000290
SP.FV
evfscfui
Vector Convert Floating-Point Single-Precision from Unsigned Integer
EVX
10000291
SP.FV
evfscfsi
Vector Convert Floating-Point Single-Precision from Signed Integer
EVX
10000292
SP.FV
evfscfuf
Vector Convert Floating-Point Single-Precision from Unsigned Fraction
EVX
10000293
SP.FV
evfscfsf
Vector Convert Floating-Point Single-Precision from Signed Fraction
EVX
10000294
SP.FV
evfsctui
Vector Convert Floating-Point Single-Precision to Unsigned Integer
EVX
10000295
SP.FV
evfsctsi
Vector Convert Floating-Point Single-Precision to Signed Integer
EVX
10000296
SP.FV
evfsctuf
Vector Convert Floating-Point Single-Precision to Unsigned Fraction
EVX
10000297
SP.FV
evfsctsf
Vector Convert Floating-Point Single-Precision to Signed Fraction




EVX
10000298
SP.FV
evfsctuiz
Vector Convert Floating-Point Single-Precision to Unsigned Integer with Round Towards Zero
EVX
1000029A
SP.FV
evfsctsiz
Vector Convert Floating-Point Single-Precision to Signed Integer with Round Towards Zero
EVX
1000029C
SP.FV
evfststgt
Vector Floating-Point Single-Precision Test Greater Than
EVX
1000029D
SP.FV
evfststlt
Vector Floating-Point Single-Precision Test Less Than
EVX
1000029E
SP.FV
evfststeq
Vector Floating-Point Single-Precision Test Equal
VX
100002C4
VEC
vsr
Vector Shift Right
VX
100002C6
VEC
vcmpgtfp[.]
Vector Compare Greater Than Single-Precision
VX
100002CA
VEC
vrfim
Vector Round to Single-Precision Integer toward Minus Infinity
VX
100002CE
VEC
vupklsh
Vector Unpack Low Signed Halfword
EVX
100002CF
SP.FD
efscfd
Floating-Point Single-Precision Convert from Double-Precision
EVX
100002E0
SP.FD
efdadd
Floating-Point Double-Precision Add
EVX
100002E0
SP.FS
efsadd
Floating-Point Single-Precision Add
EVX
100002E1
SP.FD
efdsub
Floating-Point Double-Precision Subtract
EVX
100002E1
SP.FS
efssub
Floating-Point Single-Precision Subtract
EVX
100002E2
SP.FD
efdcfuid
Convert Floating-Point Double-Precision from Unsigned Integer Doubleword
EVX
100002E2
SP.FS
efscfuid
Convert Floating-Point Single-Precision from Unsigned Integer Doubleword
EVX
100002E3
SP.FD
efdcfsid
Convert Floating-Point Double-Precision from Signed Integer Doubleword
EVX
100002E3
SP.FS
efscfsid
Convert Floating-Point Single-Precision from Signed Integer Doubleword
EVX
100002E4
SP.FD
efdabs
Floating-Point Double-Precision Absolute Value
EVX
100002E4
SP.FS
efsabs
Floating-Point Single-Precision Absolute Value
EVX
100002E5
SP.FD
efdnabs
Floating-Point Double-Precision Negative Absolute Value
EVX
100002E5
SP.FS
efsnabs
Floating-Point Single-Precision Negative Absolute Value
EVX
100002E6
SP.FD
efdneg
Floating-Point Double-Precision Negate
EVX
100002E6
SP.FS
efsneg
Floating-Point Single-Precision Negate
EVX
100002E8
SP.FD
efdmul
Floating-Point Double-Precision Multiply
EVX
100002E8
SP.FS
efsmul
Floating-Point Single-Precision Multiply
EVX
100002E9
SP.FD
efddiv
Floating-Point Double-Precision Divide




EVX
100002E9
SP.FS
efsdiv
Floating-Point Single-Precision Divide
EVX
100002EA
SP.FD
efdctuidz
Convert Floating-Point Double-Precision to Unsigned Integer Doubleword with Round Towards Zero
EVX
100002EA
SP.FS
efsctuidz
Convert Floating-Point Single-Precision to Unsigned Integer Doubleword with Round Towards Zero
EVX
100002EB
SP.FD
efdctsidz
Convert Floating-Point Double-Precision to Signed Integer Doubleword with Round Towards Zero
EVX
100002EB
SP.FS
efsctsidz
Convert Floating-Point Single-Precision to Signed Integer Doubleword with Round Towards Zero
EVX
100002EC
SP.FD
efdcmpgt
Floating-Point Double-Precision Compare Greater Than
EVX
100002EC
SP.FS
efscmpgt
Floating-Point Single-Precision Compare Greater Than
EVX
100002ED
SP.FD
efdcmplt
Floating-Point Double-Precision Compare Less Than
EVX
100002ED
SP.FS
efscmplt
Floating-Point Single-Precision Compare Less Than
EVX
100002EE
SP.FD
efdcmpeq
Floating-Point Double-Precision Compare Equal
EVX
100002EE
SP.FS
efscmpeq
Floating-Point Single-Precision Compare Equal
EVX
100002EF
SP.FD
efdcfs
Floating-Point Double-Precision Convert from Single-Precision
EVX
100002F0
SP.FD
efdcfui
Convert Floating-Point Double-Precision from Unsigned Integer
EVX
100002F0
SP.FS
efscfui
Convert Floating-Point Single-Precision from Unsigned Integer
EVX
100002F1
SP.FD
efdcfsi
Convert Floating-Point Double-Precision from Signed Integer
EVX
100002F1
SP.FS
efscfsi
Convert Floating-Point Single-Precision from Signed Integer
EVX
100002F2
SP.FD
efdcfuf
Convert Floating-Point Double-Precision from Unsigned Fraction
EVX
100002F2
SP.FS
efscfuf
Convert Floating-Point Single-Precision from Unsigned Fraction
EVX
100002F3
SP.FD
efdcfsf
Convert Floating-Point Double-Precision from Signed Fraction
EVX
100002F3
SP.FS
efscfsf
Convert Floating-Point Single-Precision from Signed Fraction
EVX
100002F4
SP.FD
efdctui
Convert Floating-Point Double-Precision to Unsigned Integer
EVX
100002F4
SP.FS
efsctui
Convert Floating-Point Single-Precision to Unsigned Integer




EVX
100002F5
SP.FD
efdctsi
Convert Floating-Point Double-Precision to Signed Integer
EVX
100002F5
SP.FS
efsctsi
Convert Floating-Point Single-Precision to Signed Integer
EVX
100002F6
SP.FD
efdctuf
Convert Floating-Point Double-Precision to Unsigned Fraction
EVX
100002F6
SP.FS
efsctuf
Convert Floating-Point Single-Precision to Unsigned Fraction
EVX
100002F7
SP.FD
efdctsf
Convert Floating-Point Double-Precision to Signed Fraction
EVX
100002F7
SP.FS
efsctsf
Convert Floating-Point Single-Precision to Signed Fraction
EVX
100002F8
SP.FD
efdctuiz
Convert Floating-Point Double-Precision to Unsigned Integer with Round Towards Zero
EVX
100002F8
SP.FS
efsctuiz
Convert Floating-Point Single-Precision to Unsigned Integer with Round Towards Zero
EVX
100002FA
SP.FD
efdctsiz
Convert Floating-Point Double-Precision to Signed Integer with Round Towards Zero
EVX
100002FA
SP.FS
efsctsiz
Convert Floating-Point Single-Precision to Signed Integer with Round Towards Zero
EVX
100002FC
SP.FD
efdtstgt
Floating-Point Double-Precision Test Greater Than
EVX
100002FC
SP.FS
efststgt
Floating-Point Single-Precision Test Greater Than
EVX
100002FD
SP.FD
efdtstlt
Floating-Point Double-Precision Test Less Than
EVX
100002FD
SP.FS
efststlt
Floating-Point Single-Precision Test Less Than
EVX
100002FE
SP.FD
efdtsteq
Floating-Point Double-Precision Test Equal
EVX
100002FE
SP.FS
efststeq
Floating-Point Single-Precision Test Equal
EVX
10000300
SP
evlddx
Vector Load Doubleword into Doubleword Indexed
VX
10000300
VEC
vaddsbs
Vector Add Signed Byte Saturate
EVX
10000301
SP
evldd
Vector Load Doubleword into Doubleword
EVX
10000302
SP
evldwx
Vector Load Doubleword into 2 Words Indexed
VX
10000302
VEC
vminsb
Vector Minimum Signed Byte
EVX
10000303
SP
evldw
Vector Load Doubleword into 2 Words
EVX
10000304
SP
evldhx
Vector Load Doubleword into 4 Halfwords Indexed
VX
10000304
VEC
vsrab
Vector Shift Right Algebraic Word
EVX
10000305
SP
evldh
Vector Load Doubleword into 4 Halfwords
VX
10000306
VEC
vcmpgtsb[.]
Vector Compare Greater Than Signed Byte




EVX
10000308
SP
evlhhesplatx
Vector Load Halfword into Halfwords Even and Splat Indexed
VX
10000308
VEC
vmulesb
Vector Multiply Even Signed Byte
EVX
10000309
SP
evlhhesplat
Vector Load Halfword into Halfwords Even and Splat
VX
1000030A
VEC
vcuxwfp
Vector Convert from Unsigned Fixed-Point Word to Single-Precision
EVX
1000030C
SP
evlhhousplatx
Vector Load Halfword into Halfwords Odd Unsigned and Splat Indexed
VX
1000030C
VEC
vspltisb
Vector Splat Immediate Signed Byte
EVX
1000030D
SP
evlhhousplat
Vector Load Halfword into Halfwords Odd Unsigned and Splat
EVX
1000030E
SP
evlhhossplatx
Vector Load Halfword into Halfwords Odd Signed and Splat Indexed
VX
1000030E
VEC
vpkpx
Vector Pack Pixel
EVX
1000030F
SP
evlhhossplat
Vector Load Halfword into Halfwords Odd and Splat
EVX
10000310
SP
evlwhex
Vector Load Word into Two Halfwords Even Indexed
EVX
10000311
SP
evlwhe
Vector Load Word into Two Halfwords Even
EVX
10000314
SP
evlwhoux
Vector Load Word into Two Halfwords Odd Unsigned Indexed
EVX
10000315
SP
evlwhou
Vector Load Word into Two Halfwords Odd Unsigned
EVX
10000316
SP
evlwhosx
Vector Load Word into Two Halfwords Odd Signed Indexed
EVX
10000317
SP
evlwhos
Vector Load Word into Two Halfwords Odd Signed
EVX
10000318
SP
evlwwsplatx
Vector Load Word into Word and Splat Indexed
X
10000318
SR
LIM
maclhwu[o][.]
Multiply Accumulate Low Halfword to Word Modulo Unsigned
EVX
10000319
SP
evlwwsplat
Vector Load Word into Word and Splat
EVX
1000031C
SP
evlwhsplatx
Vector Load Word into Two Halfwords and Splat Indexed
EVX
1000031D
SP
evlwhsplat
Vector Load Word into Two Halfwords and Splat
EVX
10000320
SP
evstddx
Vector Store Doubleword of Doubleword Indexed
EVX
10000321
SP
evstdd
Vector Store Doubleword of Doubleword
EVX
10000322
SP
evstdwx
Vector Store Doubleword of Two Words Indexed
EVX
10000323
SP
evstdw
Vector Store Doubleword of Two Words
EVX
10000324
SP
evstdhx
Vector Store Doubleword of Four Halfwords Indexed
EVX
10000325
SP
evstdh
Vector Store Doubleword of Four Halfwords



EVX
10000330
SP
evstwhex
Vector Store Word of Two Halfwords from Even Indexed
EVX
10000331
SP
evstwhe
Vector Store Word of Two Halfwords from Even
EVX
10000334
SP
evstwhox
Vector Store Word of Two Halfwords from Odd Indexed
EVX
10000335
SP
evstwho
Vector Store Word of Two Halfwords from Odd
EVX
10000338
SP
evstwwex
Vector Store Word of Word from Even Indexed
EVX
10000339
SP
evstwwe
Vector Store Word of Word from Even
EVX
1000033C
SP
evstwwox
Vector Store Word of Word from Odd Indexed
EVX
1000033D
SP
evstwwo
Vector Store Word of Word from Odd
VX
10000340
VEC
vaddshs
Vector Add Signed Halfword Saturate
VX
10000342
VEC
vminsh
Vector Minimum Signed Halfword
VX
10000344
VEC
vsrah
Vector Shift Right Algebraic Word
VX
10000346
VEC
vcmpgtsh[.]
Vector Compare Greater Than Signed Halfword
VX
10000348
VEC
vmulesh
Vector Multiply Even Signed Halfword
VX
1000034A
VEC
vcsxwfp
Vector Convert from Signed Fixed-Point Word to Single-Precision
VX
1000034C
VEC
vspltish
Vector Splat Immediate Signed Halfword
VX
1000034E
VEC
vupkhpx
Vector Unpack High Pixel
X
10000358
SR
LIM
maclhw[o][.]
Multiply Accumulate Low Halfword to Word Modulo Signed
X
1000035C
SR
LIM
nmaclhw[o][.]
Negative Multiply Accumulate Low Halfword to Word Modulo Signed
VX
10000380
VEC
vaddsws
Vector Add Signed Word Saturate
VX
10000382
VEC
vminsw
Vector Minimum Signed Word
VX
10000384
VEC
vsraw
Vector Shift Right Algebraic Word
VX
10000386
VEC
vcmpgtsw[.]
Vector Compare Greater Than Signed Word
VX
1000038A
VEC
vcfpuxws
Vector Convert from Single-Precision to Unsigned Fixed-Point Word Saturate
VX
1000038C
VEC
vspltisw
Vector Splat Immediate Signed Word
X
10000398
SR
LIM
maclhwsu[o][.]
Multiply Accumulate Low Halfword to Word Saturate Unsigned
VX
100003C6
VEC
vcmpbfp[.]
Vector Compare Bounds Single-Precision
VX
100003CA
VEC
vcfpsxws
Vector Convert from Single-Precision to Signed Fixed-Point Word Saturate
VX
100003CE
VEC
vupklpx
Vector Unpack Low Pixel




X
100003D8
SR
LIM
maclhws[o][.]
Multiply Accumulate Low Halfword to Word Saturate Signed
X
100003DC
SR
LIM
nmaclhws[o][.]
Negative Multiply Accumulate Low Halfword to Word Saturate Signed
VX
10000400
VEC
vsububm
Vector Subtract Unsigned Byte Modulo
VX
10000402
VEC
vavgub
Vector Average Unsigned Byte
EVX
10000403
SP
evmhessf
Vector Multiply Halfwords, Even, Signed, Saturate, Fractional
VX
10000404
VEC
vand
Vector AND
EVX
10000407
SP
evmhossf
Vector Multiply Halfwords, Odd, Signed, Fractional
EVX
10000408
SP
evmheumi
Vector Multiply Halfwords, Even, Unsigned, Modulo, Integer
EVX
10000409
SP
evmhesmi
Vector Multiply Halfwords, Even, Signed, Modulo, Integer
VX
1000040A
VEC
vmaxfp
Vector Maximum Single-Precision
EVX
1000040B
SP
evmhesmf
Vector Multiply Halfwords, Even, Signed, Modulo, Fractional
EVX
1000040C
SP
evmhoumi
Vector Multiply Halfwords, Odd, Unsigned, Modulo, Integer
VX
1000040C
VEC
vslo
Vector Shift Left by Octet
EVX
1000040D
SP
evmhosmi
Vector Multiply Halfwords, Odd, Signed, Modulo, Integer
EVX
1000040F
SP
evmhosmf
Vector Multiply Halfwords, Odd, Signed, Modulo, Fractional
EVX
10000423
SP
evmhessfa
Vector Multiply Halfwords, Even, Signed, Saturate, Fractional to Accumulator
EVX
10000427
SP
evmhossfa
Vector Multiply Halfwords, Odd, Signed, Fractional to Accumulator
EVX
10000428
SP
evmheumia
Vector Multiply Halfwords, Even, Unsigned, Modulo, Integer to Accumulator
EVX
10000429
SP
evmhesmia
Vector Multiply Halfwords, Even, Signed, Modulo, Integer to Accumulator
EVX
1000042B
SP
evmhesmfa
Vector Multiply Halfwords, Even, Signed, Modulo, Fractional to Accumulate
EVX
1000042C
SP
evmhoumia
Vector Multiply Halfwords, Odd, Unsigned, Modulo, Integer to Accumulator
EVX
1000042D
SP
evmhosmia
Vector Multiply Halfwords, Odd, Signed, Modulo, Integer to Accumulator
EVX
1000042F
SP
evmhosmfa
Vector Multiply Halfwords, Odd, Signed, Modulo, Fractional to Accumulator




VX
10000440
VEC
vsubuhm
Vector Subtract Unsigned Byte Modulo
VX
10000442
VEC
vavguh
Vector Average Unsigned Halfword
VX
10000444
VEC
vandc
Vector AND with Complement
EVX
10000447
SP
evmwhssf
Vector Multiply Word High Signed, Fractional
EVX
10000448
SP
evmwlumi
Vector Multiply Word Low Unsigned, Modulo, Integer
VX
1000044A
VEC
vminfp
Vector Minimum Single-Precision
EVX
1000044C
SP
evmwhumi
Vector Multiply Word High Unsigned, Modulo, Integer
VX
1000044C
VEC
vsro
Vector Shift Right by Octet
EVX
1000044D
SP
evmwhsmi
Vector Multiply Word High Signed, Modulo, Integer
EVX
1000044F
SP
evmwhsmf
Vector Multiply Word High Signed, Modulo, Fractional
EVX
10000453
SP
evmwssf
Vector Multiply Word Signed, Saturate, Fractional
EVX
10000458
SP
evmwumi
Vector Multiply Word Unsigned, Modulo, Integer
EVX
10000459
SP
evmwsmi
Vector Multiply Word Signed, Modulo, Integer
EVX
1000045B
SP
evmwsmf
Vector Multiply Word Signed, Modulo, Fractional
EVX
10000467
SP
evmwhssfa
Vector Multiply Word High Signed, Fractional to Accumulator
EVX
10000468
SP
evmwlumia
Vector Multiply Word Low Unsigned, Modulo, Integer to Accumulator
EVX
1000046C
SP
evmwhumia
Vector Multiply Word High Unsigned, Modulo, Integer to Accumulator
EVX
1000046D
SP
evmwhsmia
Vector Multiply Word High Signed, Modulo, Integer to Accumulator
EVX
1000046F
SP
evmwhsmfa
Vector Multiply Word High Signed, Modulo, Fractional to Accumulator
EVX
10000473
SP
evmwssfa
Vector Multiply Word Signed, Saturate, Fractional to Accumulator
EVX
10000478
SP
evmwumia
Vector Multiply Word Unsigned, Modulo, Integer to Accumulator
EVX
10000479
SP
evmwsmia
Vector Multiply Word Signed, Modulo, Integer to Accumulator
EVX
1000047B
SP
evmwsmfa
Vector Multiply Word Signed, Modulo, Fractional to Accumulator
VX
10000480
VEC
vsubuwm
Vector Subtract Unsigned Word Modulo
VX
10000482
VEC
vavguw
Vector Average Unsigned Word
VX
10000484
VEC
vor
Vector OR




EVX
100004C0
SP
evaddusiaaw
Vector Add Unsigned, Saturate, Integer to Accumulator Word
EVX
100004C1
SP
evaddssiaaw
Vector Add Signed, Saturate, Integer to Accumulator Word
EVX
100004C2
SP
evsubfusiaaw
Vector Subtract Unsigned, Saturate, Integer to Accumulator Word
EVX
100004C3
SP
evsubfssiaaw
Vector Subtract Signed, Saturate, Integer to Accumulator Word
EVX
100004C4
SP
evmra
Initialize Accumulator
VX
100004C4
VEC
vxor
Vector XOR
EVX
100004C6
SP
evdivws
Vector Divide Word Signed
EVX
100004C7
SP
evdivwu
Vector Divide Word Unsigned
EVX
100004C8
SP
evaddumiaaw
Vector Add Unsigned, Modulo, Integer to Accumulator Word
EVX
100004C9
SP
evaddsmiaaw
Vector Add Signed, Modulo, Integer to Accumulator Word
EVX
100004CA
SP
evsubfumiaaw
Vector Subtract Unsigned, Modulo, Integer to Accumulator Word
EVX
100004CB
SP
evsubfsmiaaw
Vector Subtract Signed, Modulo, Integer to Accumulator Word
EVX
10000500
SP
evmheusiaaw
Vector Multiply Halfwords, Even, Unsigned, Saturate Integer and Accumulate into Words
EVX
10000501
SP
evmhessiaaw
Vector Multiply Halfwords, Even, Signed, Saturate, Integer and Accumulate into Words
VX
10000502
VEC
vavgsb
Vector Average Signed Byte
EVX
10000503
SP
evmhessfaaw
Vector Multiply Halfwords, Even, Signed, Saturate, Fractional and Accumulate into Words
EVX
10000504
SP
evmhousiaaw
Vector Multiply Halfwords, Odd, Unsigned, Saturate, Integer and Accumulate into Words
VX
10000504
VEC
vnor
Vector NOR
EVX
10000505
SP
evmhossiaaw
Vector Multiply Halfwords, Odd, Signed, Saturate, Integer and Accumulate into Words
EVX
10000507
SP
evmhossfaaw
Vector Multiply Halfwords, Odd, Signed, Saturate, Fractional and Accumulate into Words
EVX
10000508
SP
evmheumiaaw
Vector Multiply Halfwords, Even, Unsigned, Modulo, Integer and Accumulate into Words
EVX
10000509
SP
evmhesmiaaw
Vector Multiply Halfwords, Even, Signed, Modulo, Integer and Accumulate into Words




EVX
1000050B
SP
evmhesmfaaw
Vector Multiply Halfwords, Even, Signed, Modulo, Fractional and Accumulate into Words
EVX
1000050C
SP
evmhoumiaaw
Vector Multiply Halfwords, Odd, Unsigned, Modulo, Integer and Accumulate into Words
EVX
1000050D
SP
evmhosmiaaw
Vector Multiply Halfwords, Odd, Signed, Modulo, Integer and Accumulate into Words
EVX
1000050F
SP
evmhosmfaaw
Vector Multiply Halfwords, Odd, Signed, Modulo, Fractional and Accumulate into Words
EVX
10000528
SP
evmhegumiaa
Vector Multiply Halfwords, Even, Guarded, Unsigned, Modulo, Integer and Accumulate
EVX
10000529
SP
evmhegsmiaa
Vector Multiply Halfwords, Even, Guarded, Signed, Modulo, Integer and Accumulate
EVX
1000052B
SP
evmhegsmfaa
Vector Multiply Halfwords, Even, Guarded, Signed, Modulo, Fractional and Accumulate
EVX
1000052C
SP
evmhogumiaa
Vector Multiply Halfwords, Odd, Guarded, Unsigned, Modulo, Integer and Accumulate
EVX
1000052D
SP
evmhogsmiaa
Vector Multiply Halfwords, Odd, Guarded, Signed, Modulo, Integer and Accumulate
EVX
1000052F
SP
evmhogsmfaa
Vector Multiply Halfwords, Odd, Guarded, Signed, Modulo, Fractional and Accumulate
EVX
10000540
SP
evmwlusiaaw
Vector Multiply Word Low Unsigned Saturate, Integer and Accumulate into Words
EVX
10000541
SP
evmwlssiaaw
Vector Multiply Word Low Signed, Saturate, Integer and Accumulate into Words
VX
10000542
VEC
vavgsh
Vector Average Signed Halfword
EVX
10000544
SP
evmwhusiaaw
Vector Multiply Word High Unsigned, Integer and Accumulate into Words
EVX
10000547
SP
evmwhssfaaw
Vector Multiply Word High Signed, Fractional and Accumulate into Words
EVX
10000548
SP
evmwlumiaaw
Vector Multiply Word Low Unsigned, Modulo, Integer and Accumulate into Words
EVX
10000549
SP
evmwlsmiaaw
Vector Multiply Word Low Signed, Modulo, Integer and Accumulate into Words
EVX
1000054C
SP
evmwhumiaaw
Vector Multiply Word High Unsigned, Modulo, Integer and Accumulate into Words
EVX
1000054D
SP
evmwhsmiaaw
Vector Multiply Word High Signed, Modulo, Integer and Accumulate into Words
EVX
1000054F
SP
evmwhsmfaaw
Vector Multiply Word High Signed, Modulo, Fractional and Accumulate into Words




EVX
10000553
SP
evmwssfaa
Vector Multiply Word Signed, Saturate, Fractional and Accumulate
EVX
10000558
SP
evmwumiaa
Vector Multiply Word Unsigned, Modulo, Integer and Accumulate
EVX
10000559
SP
evmwsmiaa
Vector Multiply Word Signed, Modulo, Integer and Accumulate
EVX
1000055B
SP
evmwsmfaa
Vector Multiply Word Signed, Modulo, Fractional and Accumulate
EVX
10000580
SP
evmheusianw
Vector Multiply Halfwords, Even, Unsigned, Saturate Integer and Accumulate Negative into Words
VX
10000580
VEC
vsubcuw
Vector Subtract and Write Carry-Out Unsigned Word
EVX
10000581
SP
evmhessianw
Vector Multiply Halfwords, Even, Signed, Saturate, Integer and Accumulate Negative into Words
VX
10000582
VEC
vavgsw
Vector Average Signed Word
EVX
10000583
SP
evmhessfanw
Vector Multiply Halfwords, Even, Signed, Saturate, Fractional and Accumulate Negative into Words
EVX
10000584
SP
evmhousianw
Vector Multiply Halfwords, Odd, Unsigned, Saturate, Integer and Accumulate Negative into Words
EVX
10000585
SP
evmhossianw
Vector Multiply Halfwords, Odd, Signed, Saturate, Integer and Accumulate Negative into Words
EVX
10000587
SP
evmhossfanw
Vector Multiply Halfwords, Odd, Signed, Saturate, Fractional and Accumulate Negative into Words
EVX
10000588
SP
evmheumianw
Vector Multiply Halfwords, Even, Unsigned, Modulo, Integer and Accumulate Negative into Words
EVX
10000589
SP
evmhesmianw
Vector Multiply Halfwords, Even, Signed, Modulo, Integer and Accumulate Negative into Words
EVX
1000058B
SP
evmhesmfanw
Vector Multiply Halfwords, Even, Signed, Modulo, Fractional and Accumulate Negative into Words
EVX
1000058C
SP
evmhoumianw
Vector Multiply Halfwords, Odd, Unsigned, Modulo, Integer and Accumulate Negative into Words
EVX
1000058D
SP
evmhosmianw
Vector Multiply Halfwords, Odd, Signed, Modulo, Integer and Accumulate Negative into Words
EVX
1000058F
SP
evmhosmfanw
Vector Multiply Halfwords, Odd, Signed, Modulo, Fractional and Accumulate Negative into Words
EVX
100005A8
SP
evmhegumian
Vector Multiply Halfwords, Even, Guarded, Unsigned, Modulo, Integer and Accumulate Negative
EVX
100005A9
SP
evmhegsmian
Vector Multiply Halfwords, Even, Guarded, Signed, Modulo, Integer and Accumulate Negative





EVX
100005AB
SP
evmhegsmfan
Vector Multiply Halfwords, Even, Guarded, Signed, Modulo, Fractional and Accumulate Negative
EVX
100005AC
SP
evmhogumian
Vector Multiply Halfwords, Odd, Guarded, Unsigned, Modulo, Integer and Accumulate Negative
EVX
100005AD
SP
evmhogsmian
Vector Multiply Halfwords, Odd, Guarded, Signed, Modulo, Integer and Accumulate Negative
EVX
100005AF
SP
evmhogsmfan
Vector Multiply Halfwords, Odd, Guarded, Signed, Modulo, Fractional and Accumulate Negative
EVX
100005C0
SP
evmwlusianw
Vector Multiply Word Low Unsigned Saturate, Integer and Accumulate Negative into Words
EVX
100005C1
SP
evmwlssianw
Vector Multiply Word Low Signed, Saturate, Integer and Accumulate Negative into Words
EVX
100005C4
SP
evmwhusianw
Vector Multiply Word High Unsigned, Integer and Accumulate Negative into Words
EVX
100005C5
SP
evmwhssianw
Vector Multiply Word High Signed, Integer and Accumulate Negative into Words
EVX
100005C7
SP
evmwhssfanw
Vector Multiply Word High Signed, Fractional and Accumulate Negative into Words
EVX
100005C8
SP
evmwlumianw
Vector Multiply Word Low Unsigned, Modulo, Integer and Accumulate Negative into Words
EVX
100005C9
SP
evmwlsmianw
Vector Multiply Word Low Signed, Modulo, Integer and Accumulate Negative into Words
EVX
100005CC
SP
evmwhumianw
Vector Multiply Word High Unsigned, Modulo, Integer and Accumulate Negative into Words
EVX
100005CD
SP
evmwhsmianw
Vector Multiply Word High Signed, Modulo, Integer and Accumulate Negative into Words
EVX
100005CF
SP
evmwhsmfanw
Vector Multiply Word High Signed, Modulo, Fractional and Accumulate Negative into Words
EVX
100005D3
SP
evmwssfan
Vector Multiply Word Signed, Saturate, Fractional and Accumulate Negative
EVX
100005D8
SP
evmwumian
Vector Multiply Word Unsigned, Modulo, Integer and Accumulate Negative
EVX
100005D9
SP
evmwsmian
Vector Multiply Word Signed, Modulo, Integer and Accumulate Negative
EVX
100005DB
SP
evmwsmfan
Vector Multiply Word Signed, Modulo, Fractional and Accumulate Negative
VX
10000600
VEC
vsububs
Vector Subtract Unsigned Byte Saturate
VX
10000604
VEC
mfvscr
Move from Vector Status and Control Register
VX
10000608
VEC
vsum4ubs
Vector Sum across Quarter Unsigned Byte Saturate




VX
10000640
VEC
vsubuhs
Vector Subtract Unsigned Halfword Saturate
VX
10000644
VEC
mtvscr
Move to Vector Status and Control Register
VX
10000648
VEC
vsum4shs
Vector Sum across Quarter Signed Halfword Saturate
VX
10000680
VEC
vsubuws
Vector Subtract Unsigned Word Saturate
VX
10000688
VEC
vsum2sws
Vector Sum across Half Signed Word Saturate
VX
10000700
VEC
vsubsbs
Vector Subtract Signed Byte Saturate
VX
10000708
VEC
vsum4sbs
Vector Sum across Quarter Signed Byte Saturate
VX
10000740
VEC
vsubshs
Vector Subtract Signed Halfword Saturate
VX
10000780
VEC
vsubsws
Vector Subtract Signed Word Saturate
VX
10000788
VEC
vsumsws
Vector Sum across Signed Word Saturate
D8
18000000
VLE
e_lbzu
Load Byte and Zero with Update
D8
18000100
VLE
e_lhzu
Load Halfword and Zero with Update
D8
18000200
VLE
e_lwzu
Load Word and Zero with Update
D8
18000300
VLE
e_lhau
Load Halfword Algebraic with Update
D8
18000400
VLE
e_stbu
Store Byte with Update
D8
18000500
VLE
e_sthu
Store Halfword with Update
D8
18000600
VLE
e_stwu
Store word with Update
D8
18000800
VLE
e_lmw
Load Multiple Word
D8
18000900
VLE
e_stmw
Store Multiple Word
# Clarify SCI8 form variant
SCI8_1
18008000
SR
VLE
e_addi[.]
Add Scaled Immediate
# Clarify SCI8 form variant
SCI8_1
18009000
SR
VLE
e_addic[.]
Add Scaled Immediate Carrying
# Clarify SCI8 form variant
SCI8_2
1800A000
VLE
e_mulli
Multiply Low Scaled Immediate
# Clarify SCI8 form variant
SCI8_5
1800A800
VLE
e_cmpi
Compare Scaled Immediate Word
# Clarify SCI8 form variant
SCI8_1
1800B000
SR
VLE
e_subfic[.]
Subtract From Scaled Immediate Carrying
# Clarify SCI8 form variant
SCI8_3
1800C000
SR
VLE
e_andi[.]
AND Scaled Immediate
# Clarify SCI8 form variant
SCI8_3
1800D000
SR
VLE
e_ori[.]
OR Scaled Immediate
# Clarify SCI8 form variant
SCI8_3
1800E000
SR
VLE
e_xori[.]
XOR Scaled Immediate
# Clarify SCI8 form variant
SCI8_6
1880A800
VLE
e_cmpli
Compare Logical Scaled Immediate Word
D
1C000000
VLE
e_add16i
Add Immediate
OIM5
2000----
VLE
se_addi
Add Immediate Short Form
OIM5
2200----
VLE
se_cmpli
Compare Logical Immediate Word
OIM5
2400----
SR
VLE
se_subi[.]
Subtract Immediate




IM5
2A00----
VLE
se_cmpi
Compare Immediate Word Short Form
IM5
2C00----
VLE
se_bmaski
Bit Mask Generate Immediate
IM5
2E00----
VLE
se_andi
AND Immediate Short Form
D
30000000
VLE
e_lbz
Load Byte and Zero
D
34000000
VLE
e_stb
Store Byte
D
38000000
VLE
e_lha
Load Halfword Algebraic
RR
4000----
VLE
se_srw
Shift Right Word
RR
4100----
SR
VLE
se_sraw
Shift Right Algebraic Word
RR
4200----
VLE
se_slw
Shift Left Word
RR
4400----
VLE
se_or
OR SHort Form
RR
4500----
VLE
se_andc
AND with Complement Short Form
RR
4600----
SR
VLE
se_and[.]
AND Short Form
IM7
4800----
VLE
se_li
Load Immediate Short Form
D
50000000
VLE
e_lwz
Load Word and Zero
D
54000000
VLE
e_stw
Store Word
D
58000000
VLE
e_lhz
Load Halfword and Zero
D
5C000000
VLE
e_sth
Store Halfword
IM5
6000----
VLE
se_bclri
Bit Clear Immediate
IM5
6200----
VLE
se_bgeni
Bit Generate Immediate
IM5
6400----
VLE
se_bseti
Bit Set Immediate
IM5
6600----
VLE
se_btsti
Bit Test Immediate
IM5
6800----
VLE
se_srwi
Shift Right Word Immediate Short Form
IM5
6A00----
SR
VLE
se_srawi
Shift Right Algebraic Immediate
IM5
6C00----
VLE
se_slwi
Shift Left Word Immediate Short Form
LI20
70000000
VLE
e_li
Load Immediate
I16A
70008800
SR
VLE
e_add2i.
Add (2 operand) Immediate and Record
I16A
70009000
VLE
e_add2is
Add (2 operand) Immediate Shifted
# Fixed typo IA16 -> I16A
I16A
70009800
VLE
e_cmp16i
Compare Immediate Word
I16A
7000A000
VLE
e_mull2i
Multiply (2 operand) Low Immediate
I16A
7000A800
VLE
e_cmpl16i
Compare Logical Immediate Word
# Fixed typo IA16 -> I16A
I16A
7000B000
VLE
e_cmph16i
Compare Halfword Immediate
# Fixed typo IA16 -> I16A
I16A
7000B800
VLE
e_cmphl16i
Compare Halfword Logical Immediate






I16L
7000C000
VLE
e_or2i
OR (2operand) Immediate
I16L
7000C800
SR
VLE
e_and2i.
AND (2 operand) Immediate
I16L
7000D000
VLE
e_or2is
OR (2 operand) Immediate Shifted
I16L
7000E000
VLE
e_lis
Load Immediate Shifted
I16L
7000E800
SR
VLE
e_and2is.
AND (2 operand) Immediate Shifted
M
74000000
VLE
e_rlwimi
Rotate Left Word Immediate then Mask Insert
M
74000001
VLE
e_rlwinm
Rotate Left Word Immediate then AND with Mask
BD24
78000000
VLE
e_b[l]
Branch [and Link]
BD15
7A000000
CT
VLE
e_bc[l]
Branch Conditional [and Link]
X
7C000000
B
cmp
Compare
X
7C000008
B
tw
Trap Word
X
7C00000C
VEC
lvsl
Load Vector for Shift Left Indexed
X
7C00000E
VEC
lvebx
Load Vector Element Byte Indexed
XO
7C000010
SR
B
subfc[o][.]
Subtract From Carrying
XO
7C000012
SR
64
mulhdu[.]
Multiply High Doubleword Unsigned
XO
7C000014
B
addc[o][.]
Add Carrying
XO
7C000016
SR
B
mulhwu[.]
Multiply High Word Unsigned
X
7C00001C
VLE
e_cmph
Compare Halfword
A
7C00001E
B
isel
Integer Select
XL
7C000020
VLE
e_mcrf
Move CR Field
XFX
7C000026
B
mfcr
Move From Condition Register
X
7C000028
B
lwarx
Load Word and Reserve Indexed
X
7C00002A
64
ldx
Load Doubleword Indexed
X
7C00002C
E
icbt
Instruction Cache Block Touch
X
7C00002E
B
lwzx
Load Word and Zero Indexed
X
7C000030
SR
B
slw[.]
Shift Left Word
X
7C000034
SR
B
cntlzw[.]
Count Leading Zeros Word
X
7C000036
SR
64
sld[.]
Shift Left Doubleword
X
7C000038
SR
B
and[.]
AND
X
7C00003A
P
E.PD
ldepx
Load Doubleword by External Process ID Indexed
X
7C00003E
P
E.PD
lwepx
Load Word by External Process ID Indexed
X
7C000040
B
cmpl
Compare Logical





XL
7C000042
VLE
e_crnor
Condition Register NOR
X
7C00004C
VEC
lvsr
Load Vector for Shift Right Indexed
X
7C00004E
VEC
lvehx
Load Vector Element Halfword Indexed
XO
7C000050
SR
B
subf[o][.]
Subtract From
X
7C00005C
VLE
e_cmphl
Compare Halfword Logical
X
7C00006A
64
ldux
Load Doubleword with Update Indexed
X
7C00006C
B
dcbst
Data Cache Block Store
X
7C00006E
B
lwzux
Load Word and Zero with Update Indexed
X
7C000070
SR
VLE
e_slwi[.]
Shift Left Word Immediate
X
7C000074
SR
64
cntlzd[.]
Count Leading Zeros Doubleword
X
7C000078
SR
B
andc[.]
AND with Complement
X
7C00007C
WT
wait
Wait
X
7C000088
64
td
Trap Doubleword
X
7C00008E
VEC
lvewx
Load Vector Element Word Indexed
XO
7C000092
SR
64
mulhd[.]
Multiply High Doubleword
XO
7C000096
SR
B
mulhw[.]
Multiply High Word
X
7C0000A6
P
B
mfmsr
Move From Machine State Register
X
7C0000A8
64
ldarx
Load Doubleword and Reserve Indexed
X
7C0000AC
B
dcbf
Data Cache Block Flush
X
7C0000AE
B
lbzx
Load Byte and Zero Indexed
X
7C0000BE
P
E.PD
lbepx
Load Byte by External Process ID Indexed
X
7C0000CE
VEC
lvx[l]
Load Vector Indexed [Last]
X
7C0000D0
SR
B
neg[o][.]
Negate
X
7C0000EE
B
lbzux
Load Byte and Zero with Update Indexed
X
7C0000F4
B
popcntb
Population Count Bytes
X
7C0000F8
SR
B
nor[.]
NOR
X
7C0000FE
P
E.PD
dcbfep
Data Cache Block Flush by External Process ID
XL
7C000102
VLE
e_crandc
Condition Register AND with Completement
X
7C000106
P
E
wrtee
Write MSR External Enable
X
7C00010C
M
E.CL
dcbtstls
Data Cache Block Touch for Store and Lock Set
VX
7C00010E
VEC
stvebx
Store Vector Element Byte Indexed
XO
7C000110
SR
B
subfe[o][.]
Subtract From Extended



XO
7C000114
SR
B
adde[o][.]
Add Extended
EVX
7C00011D
P
E.PD
evlddepx
Vector Load Doubleword into Doubleword by External Process ID Indexed
XFX
7C000120
B
mtcrf
Move to Condition Register Fields
X
7C000124
P
E
mtmsr
Move To Machine State Register
X
7C00012A
64
stdx
Store Doubleword Indexed
X
7C00012D
B
stwcx.
Store Word Conditional Indexed
X
7C00012E
B
stwx
Store Word Indexed
X
7C00013A
P
E.PD
stdepx
Store Doubleword by External Process ID Indexed
X
7C00013E
P
E.PD
stwepx
Store Word by External Process ID Indexed
X
7C000146
P
E
wrteei
Write MSR External Enable Immediate
X
7C00014C
M
E.CL
dcbtls
Data Cache Block Touch and Lock Set
VX
7C00014E
VEC
stvehx
Store Vector Element Halfword Indexed
X
7C00016A
64
stdux
Store Doubleword with Update Indexed
X
7C00016E
B
stwux
Store Word with Update Indexed
XL
7C000182
VLE
e_crxor
Condition Register XOR
VX
7C00018E
VEC
stvewx
Store Vector Element Word Indexed
XO
7C000190
SR
B
subfze[o][.]
Subtract From Zero Extended
XO
7C000194
SR
B
addze[o][.]
Add to Zero Extended
X
7C00019C
P
E.PC
msgsnd
Message Send
EVX
7C00019D
P
E.PD
evstddepx
Vector Store Doubleword into Doubleword by External Process ID Indexed
X
7C0001AD
64
stdcx.
Store Doubleword Conditional Indexed
X
7C0001AE
B
stbx
Store Bye Indexed
X
7C0001BE
P
E.PD
stbepx
Store Byte by External Process ID Indexed
XL
7C0001C2
VLE
e_crnand
Condition Register NAND
X
7C0001CC
M
E.CL
icblc
Instruction Cache Block Lock Clear
VX
7C0001CE
VEC
stvx[l]
Store Vector Indexed [Last]
XO
7C0001D0
SR
B
subfme[o][.]
Subtract From Minus One Extended
XO
7C0001D2
SR
64
mulld[o][.]
Multiply Low Doubleword
XO
7C0001D4
SR
B
addme[o][.]
Add to Minus One Extended
XO
7C0001D6
SR
B
mullw[o][.]
Multiply Low Word
X
7C0001DC
P
E.PC
msgclr
Message Clear



X
7C0001EC
B
dcbtst
Data Cache Block Touch for Store
X
7C0001EE
B
stbux
Store Byte with Update Indexed
X
7C0001FE
P
E.PD
dcbtstep
Data Cache Block Touch for Store by External Process ID
XL
7C000202
VLE
e_crand
Condition Register AND
XFX
7C000206
P
E
mfdcrx
Move From Device Control Register Indexed
X
7C00020E
P
E.PD
lvepxl
Load Vector by External Process ID Indexed LRU
XO
7C000214
B
add[o][.]
Add
X
7C00022C
B
dcbt
Data Cache Block Touch
X
7C00022E
B
lhzx
Load Halfword and Zero Indexed
X
7C000230
SR
VLE
e_rlw[.]
Rotate Left Word
X
7C000238
SR
B
eqv[.]
Equivalent
X
7C00023E
P
E.PD
lhepx
Load Halfword by External Process ID Indexed
XL
7C000242
VLE
e_creqv
Condition Register Equivalent
XFX
7C000246
P
E
mfdcrux
Move From Device Control Register User Indexed
X
7C00024E
P
E.PD
lvepx
Load Vector by External Process ID Indexed
X
7C00026E
B
lhzux
Load Halfword and Zero with Update Indexed
X
7C000270
SR
VLE
e_rlwi[.]
Rotate Left Word Immediate
D
7C000278
SR
B
xor[.]
XOR
X
7C00027E
P
E.PD
dcbtep
Data Cache Block Touch by External Process ID
XFX
7C000286
P
E
mfdcr
Move From Device Control Register
X
7C00028C
P
E.CD
dcread
Data Cache Read
XFX
7C00029C
O
E.PM
mfpmr
Move From Performance Monitor Register
XFX
7C0002A6
O
B
mfspr
Move From Special Purpose Register
X
7C0002AA
64
lwax
Load Word Algebraic Indexed
X
7C0002AE
B
lhax
Load Halfword Algebraic Indexed
X
7C0002EA
64
lwaux
Load Word Algebraic with Update Indexed
X
7C0002EE
B
lhaux
Load Halfword Algebraic with Update Indexed
X
7C000306
P
E
mtdcrx
Move To Device Control Register Indexed
X
7C00030C
M
E.CL
dcblc
Data Cache Block Lock Clear
X
7C00032E
B
sthx
Store Halfword Indexed
X
7C000338
SR
B
orc[.]
OR with Complement
X
7C00033E
P
E.PD
sthepx
Store Halfword by External Process ID Indexed




XL
7C000342
VLE
e_crorc
Condition Register OR with Complement
X
7C000346
E
mtdcrux
Move To Device Control Register User Indexed
X
7C00036E
B
sthux
Store Halfword with Update Indexed
X
7C000378
SR
B
or[.]
OR
XL
7C000382
VLE
e_cror
Condition Register OR
XFX
7C000386
P
E
mtdcr
Move To Device Control Register
X
7C00038C
P
E.CI
dci
Data Cache Invalidate
XO
7C000392
SR
64
divdu[o][.]
Divide Doubleword Unsigned
XO
7C000396
SR
B
divwu[o][.]
Divide Word Unsigned
XFX
7C00039C
O
E.PM
mtpmr
Move To Performance Monitor Register
XFX
7C0003A6
O
B
mtspr
Move To Special Purpose Register
X
7C0003AC
P
E
dcbi
Data Cache Block Invalidate
X
7C0003B8
SR
B
nand[.]
NAND
X
7C0003CC
M
E.CL
icbtls
Instruction Cache Block Touch and Lock Set
X
7C0003CC
P
E.CD
dcread
Data Cache Read
XO
7C0003D2
SR
64
divd[o][.]
Divide Doubleword
XO
7C0003D6
SR
B
divw[o][.]
Divide Word
X
7C000400
B
mcrxr
Move To Condition Register From XER
X
7C00042A
MA
lswx
Load String Word Indexed
X
7C00042C
B
lwbrx
Load Word Byte-Reversed Indexed
X
7C000430
SR
B
srw[.]
Shift Right Word
X
7C000436
SR
64
srd[.]
Shift Right Doubleword
X
7C00046C
P
E
tlbsync
TLB Synchronize
X
7C000470
SR
VLE
e_srwi[.]
Shift Right Word Immediate
X
7C0004AA
MA
lswi
Load String Word Immediate
X
7C0004AC
B
sync
Synchronize
X
7C0004BE
P
E.PD
lfdepx
Load Floating-Point Double by External Process ID Indexed
X
7C00052A
MA
stswx
Store String Word Indexed
X
7C00052C
B
stwbrx
Store Word Byte-Reversed Indexed
X
7C0005AA
MA
stswi
Store String Word Immediate
X
7C0005BE
P
E.PD
stfdepx
Store Floating-Point Double by External Process ID Indexed




X
7C0005EC
E
dcba
Data Cache Block Allocate
X
7C00060E
P
E.PD
stvepxl
Store Vector by External Process ID Indexed LRU
X
7C000624
P
E
tlbivax
TLB Invalidate Virtual Address Indexed
X
7C00062C
B
lhbrx
Load Halfword Byte-Reversed Indexed
X
7C000630
SR
B
sraw[.]
Shift Right Algebraic Word
X
7C000634
SR
64
srad[.]
Shift Right Algebraic Doubleword
X
7C00064E
P
E.PD
stvepx
Store Vector by External Process ID Indexed
X
7C000670
SR
B
srawi[.]
Shift Right Algebraic Word Immediate
X
7C000674
SR
64
sradi[.]
Shift Right Algebraic Doubleword Immediate
XFX
7C0006AC
E
mbar
Memory Barrier
X
7C000724
P
E
tlbsx
TLB Search Indexed
X
7C00072C
B
sthbrx
Store Halfword Byte-Reversed Indexed
X
7C000734
SR
B
extsh[.]
Extend Sign Halfword
X
7C000764
P
E
tlbre
TLB Read Entry
X
7C000774
SR
B
extsb[.]
Extend Shign Byte
X
7C00078C
P
E.CI
ici
Instruction Cache Invalidate
X
7C0007A4
P
E
tlbwe
TLB Write Entry
X
7C0007AC
B
icbi
Instruction Cache Block Invalidate
X
7C0007B4
SR
64
extsw[.]
Extend Sign Word
X
7C0007BE
P
E.PD
icbiep
Instruction Cache Block Invalidate by External Process ID
X
7C0007CC
P
E.CD
icread
Instruction Cache Read
X
7C0007EC
B
dcbz
Data Cache Block set to Zero
X
7C0007FE
P
E.PD
dcbzep
Data Cache Block set to Zero by External Process ID
XFX
7C100026
B
mfocrf
Move From One Condition Register Field
XFX
7C100120
B
mtocrf
Move To One Condition Register Field
SD4
8000----
VLE
se_lbz
Load Byte and Zero Short Form
SD4
9000----
VLE
se_stb
Store Byte Short Form
SD4
A000----
VLE
se_lhz
Load Halfword and Zero Short Form
SD4
B000----
VLE
se_sth
Store Halfword SHort Form
SD4
C000----
VLE
se_lwz
Load Word and Zero Short Form
SD4
D000----
VLE
se_stw
Store Word Short Form



BD8
E000----
VLE
se_bc
Branch Conditional Short Form
BD8
E800----
VLE
se_b[l]
Branch [and Link]
'''


def is_opcode_str(s: str) -> bool:
    # opcode is the easiest to fingerprint of the mandatory lines
    opcode_len = 8
    opcode_chars = 'ABCDEF1234567890-'
    if len(s) == opcode_len and all(char in opcode_chars for char in s):
        return True
    else:
        return False


def parse_table_instruction(lines: List[str]) -> Dict[str, Union[str, int]]:
    """Parse lines into columns from Table B-3 with empty optional columns as ''"""
    min_lines = 5
    max_lines = 7
    num_lines = len(lines)
    if num_lines < min_lines or num_lines > max_lines:
        raise Exception(f'ERROR: wrong number of lines for table instruction: {lines}')

    cur_instruction: Dict[str, Union[str, int]] = {}
    # Optional fields are in the middle, eat both ends first
    cur_instruction['form'] = lines.pop(0)
    opcode_str = lines.pop(0)
    opcode_int = int(opcode_str.replace('-', ''), 16)
    cur_instruction['opcode'] = opcode_int
    cur_instruction['instruction'] = lines.pop()
    cur_instruction['mnemonic'] = lines.pop()
    cur_instruction['category'] = lines.pop()
    cur_instruction['mode'] = ''
    cur_instruction['privilege'] = ''

    # Mode Dep and Priv are optional and mutually exclusive
    if len(lines) > 0:
        if len(lines) > 1:
            raise Exception(f'Guess I was wrong about mutex mode dep and priv: {cur_instruction}, {lines}')
        last_line = lines.pop()
        mode_deps = ['SR', 'CT']
        privs = ['M', 'O', 'P']
        if last_line in mode_deps:
            cur_instruction['mode'] = last_line
        elif last_line in privs:
            cur_instruction['privilege'] = last_line
        else:
            raise Exception(f'Unhandled extra line in instruction parsing: {last_line}')

    return cur_instruction


def parse_vle_table(contents: str) -> List[Dict[str, Union[str, int]]]:
    """Put together columns from newline-separated data to get instruction list.
    
    This is the primary function of this file."""
    vle_instructions: List[Dict[str, Union[str, int]]] = []
    collected_lines: List[str] = []

    first_opcode = True
    for line in contents.split('\n'):
        line = line.strip()
        # Skip empty lines and comments
        if len(line) == 0 or line.startswith('#'):
            continue

        if is_opcode_str(line):
            if first_opcode:
                collected_lines.append(line)
                first_opcode = False
            else:
                # Save off the form for current instruction, process prev
                next_form = collected_lines.pop()
                cur_instruction = parse_table_instruction(collected_lines)
                vle_instructions.append(cur_instruction)
                # Start current instruction with what we have so far
                collected_lines = [next_form, line]
        else:
            collected_lines.append(line)

    # Since we key on opcodes, there'll be one left at the end of the loop
    last_instruction = parse_table_instruction(collected_lines)
    vle_instructions.append(last_instruction)

    return vle_instructions


def sanity_check(vle_table: List[Dict[str, Union[str, int]]]):
    """Assert data in table fits manually-gathered expectations"""
    forms = set()
    modes = set()
    privs = set()
    categories = set()
    for inst in vle_table:
        forms.add(inst['form'])
        modes.add(inst['mode'])
        privs.add(inst['privilege'])
        categories.add(inst['category'])
    print(f'DBG: forms seen: {sorted(forms)}')
    print(f'DBG: modes seen: {sorted(modes)}')
    print(f'DBG: privs seen: {sorted(privs)}')
    print(f'DBG: categories seen: {sorted(categories)}')
    # expected_* derived from manual perusal of VLE PEM Table B-3
    # NOTE: SCI8 is clarified into variants (numbers reflect the order of
    #       listing in VLE PEM)
    expected_forms = ["A", "BD8", "BD15", "BD24", "C", "D", "D8", "EVSEL", "EVX", "IM5", "IM7", "I16A", "I16L", "LI20", "M", "OIM5", "R", "RR", "SCI8_1", "SCI8_2", "SCI8_3", "SCI8_5", "SCI8_6", "SD4", "VA", "VX", "X", "XFX", "XL", "XO"]
    expected_modes = ["", "SR", "CT"]
    expected_privs = ["", "M", "O", "P"]
    expected_categories = ["B", "E", "E.CD", "E.CI", "E.CL", "E.PC", "E.PD", "E.PM", "LIM", "MA", "SP", "SP.FD", "SP.FS", "SP.FV", "VEC", "VLE", "WT", "64"]
    for form in forms:
        if form not in expected_forms:
            raise Exception(f'Unexpected form: {form}')
    for mode in modes:
        if mode not in expected_modes:
            raise Exception(f'Unexpected mode: {mode}')
    for priv in privs:
        if priv not in expected_privs:
            raise Exception(f'Unexpected priv: {priv}')
    for category in categories:
        if category not in expected_categories:
            raise Exception(f'Unexpected category: {category}')
    print('[+] Sanity check passed')


# Helpers for processing data
def format_instruction(inst_dict: dict) -> str:
    """Format for pretty-printing and inspection"""
    inst_str = f'{inst_dict["form"].ljust(5)}'
    opcode = f'{inst_dict["opcode"]:04x}'.ljust(8)
    inst_str += f'  {opcode}'
    inst_str += f'  {inst_dict["mode"].ljust(2)}'
    inst_str += f'  {inst_dict["privilege"].ljust(1)}'
    inst_str += f'  {inst_dict["category"].ljust(5)}'
    inst_str += f'  {inst_dict["mnemonic"]}'
    return inst_str


def pp_instructions(inst_list: List[dict]):
    for i in inst_list:
        print(format_instruction(i))


def get_instructions_by_form(inst_list: List[dict], form: str) -> List[dict]:
    return [i for i in inst_list if i['form'] == form]


def get_opcode_mappings(inst_list: List[dict]) -> Dict[int, str]:
    return {i['opcode']: i['mnemonic'] for i in inst_list}


def pp_opcode_mappings(opcode_map: Dict[int, str]):
    for opcode, mnemonic in sorted(opcode_map.items()):
        print(f'0x{opcode:08x}: "{mnemonic}"')


# Bitmask helpers for generating bitmasks for forms
def make_bitmask(start: int, stop: int=-1, size: int=32) -> int:
    """Make bitmask for bit position or range (inclusive on start and stop).
    NOTE: this uses the backwards PPC bit ordering where 0 is the highest bit
    e.g. (0, 3) -> 0xf0000000, (4, 7) -> 0x0f000000, 8 -> 0x00800000
    """
    if stop == -1:
        stop = start
    if start > stop:
        start, stop = stop, start
    width = stop - start + 1
    mask = (2 ** width) - 1
    # These last two lines address the weirdo bit ordering
    max_bit_pos = size - 1
    mask = mask << (max_bit_pos - stop)
    return mask


def make_bitmask_from_str(mask_str: str) -> int:
    """Return a bitmask from a string like '0:3,5,8:11', ranges are inclusive
    NOTE: this uses the backwards PPC bit ordering where 0 is the highest bit"""
    mask = 0
    pieces = mask_str.split(',')
    for cur_piece in pieces:
        if ':' in cur_piece:
            start, stop = (int(i) for i in cur_piece.split(':'))
            piece_mask = make_bitmask(start, stop)
        else:
            bitnum = int(cur_piece)
            piece_mask = make_bitmask(bitnum)
        mask |= piece_mask
    return mask


# NOTE: the equivalent form masks were done manually for 16-bit VLE (se_*) ops,
#       the result of which is in se_ops in vle_ops.py
def generate_form_masks() -> Dict[int, List[str]]:
    # constructed by calculating bitmasks from manual inspection of opcode and
    # XO bits in the VLEPEM table of 32-bit forms (section A.2-A.17)
    # Forms D, X, and XL from EREF Section A.5
    opcode_bits_to_forms = {
        '0:9': ['BD15'],
        '0:5': ['BD24', 'D'],
        '0:5,16:23': ['D8'],
        '0:5,16:20': ['I16A', 'I16L', 'SCI8_2', 'SCI8_4'],
        '0:5,31': ['M'],
        '0:5,16:19': ['SCI8_1', 'SCI8_3'],
        '0:5,6:8,16:20': ['SCI8_5', 'SCI8_6'],
        # NOTE: no opcodes match SCI8_7 in the VLE instructions...
        #'0:5,6:10,16:20': ['SCI8_7'],
        '0:5,16': ['LI20'],
        '0:5,21:30': ['X', 'XL'],
        # NOTE: "Added Instructions" for interrupt handlers (such as e_ldmvgprw)
        #       from Doc #EB696 use an unnamed form, currently added manually
        # '0:10,16:23': ['INTR'] -> mask: 0xffe0ff00
    }

    mask_to_forms = {}
    for mask_str, form_list in opcode_bits_to_forms.items():
        bitmask = make_bitmask_from_str(mask_str)
        mask_to_forms[bitmask] = form_list
    # Sort by bitmask as int for easier manual inspection
    sorted_masks = sorted(mask_to_forms.keys())
    sorted_mask_to_forms = {mask: mask_to_forms[mask] for mask in sorted_masks}
    return sorted_mask_to_forms


def build_e_ops(vle_table: List[Dict[str, Union[str, int]]]) -> Dict[int, Dict[int, str]]:
    """Build e_opcode_dict; dict of bitmasks to dicts of opcode: mnemonic"""
    # Forms outside of these should be supported by BookE decoding (VLEPEM A.2)
    '''
    mask_to_e_forms:
        0xfc000000: ['BD24', 'D']
        0xfc000001: ['M']
        0xfc0007fe: ['X', 'XL']
        0xfc008000: ['LI20']
        0xfc00f000: ['SCI8_1', 'SCI8_3']
        0xfc00f800: ['I16A', 'I16L', 'SCI8_2', 'SCI8_4']
        0xfc00ff00: ['D8']
        0xff80f800: ['SCI8_5', 'SCI8_6']
        0xffc00000: ['BD15']
    '''
    mask_to_e_forms = generate_form_masks()
    e_opcode_dict = {}
    # want e_opcode_dict sorted by mask value
    for bitmask, form_list in sorted(mask_to_e_forms.items()):
        # map current mask to opcodes that use it
        mask_dict = {}
        mask_instructions = []
        for form in form_list:
            form_instructions = get_instructions_by_form(vle_table, form)
            form_instructions = [i for i in form_instructions if i['mnemonic'].startswith('e_')]
            mask_instructions.extend(form_instructions)
        # sort instructions by opcode (as of python 3.6 dicts preserve order)
        for instruction in sorted(mask_instructions, key=lambda d: d['opcode']):
            opcode = instruction['opcode']
            mnemonic = instruction['mnemonic']
            mask_dict[opcode] = mnemonic
        e_opcode_dict[bitmask] = mask_dict

    return e_opcode_dict


def print_vle_interrupt_helpers():
    # Table 2 from Document Number EB696 aka:
    # "New VLE Instructions for Improving Interrupt Handler Efficiency"
    intr_instrs_str = '''e_ldmvgprw
6 (0b0001_10)
0b00000
RA
0b0001_0000
D8
e_stmvgprw
6 (0b0001_10)
0b00000
RA
0b0001_0001
D8
e_ldmvsprw
6 (0b0001_10)
0b00001
RA
0b0001_0000
D8
e_stmvsprw
6 (0b0001_10)
0b00001
RA
0b0001_0001
D8
e_ldmvsrrw
6 (0b0001_10)
0b00100
RA
0b0001_0000
D8
e_stmvsrrw
6 (0b0001_10)
0b00100
RA
0b0001_0001
D8
e_ldmvcsrrw
6 (0b0001_10)
0b00101
RA
0b0001_0000
D8
e_stmvcsrrw
6 (0b0001_10)
0b00101
RA
0b0001_0001
D8
e_ldmvdsrrw
6 (0b0001_10)
0b00110
RA
0b0001_0000
D8
e_stmvdsrrw
6 (0b0001_10)
0b00110
RA
0b0001_0001
D8'''
    lines = intr_instrs_str.split('\n')
    new_instructions = {}
    # mask '0:10,16:23': ['INTR'] -> mask: 0xffe0ff00
    intr_instr_mask = make_bitmask_from_str('0:10,16:23')
    print(f'    0x{intr_instr_mask:08x}: {{')
    for i in range(0, len(lines), 6):
        cur_lineset = lines[i:i+6]
        cur_mnem, zero_to_five, six_to_ten, ra, sixteen_to_twentythree, d8 = cur_lineset
        #print(cur_mnem, zero_to_five, six_to_ten, sixteen_to_twentythree)
        # stitch together the binary string
        match = re.search('(0b[01_]*)', zero_to_five)
        b_0_5 = match.group(1)
        b_6_10 = six_to_ten[2:]  # strip the leading '0b'
        b_11_15 = '0' * ((15-11)+1)  # plus one because inclusive
        b_16_23 = sixteen_to_twentythree[2:]  # strip the leading '0b'
        b_24_31 = '0' * ((31-24)+1)  # plus one because inclusive
        b_opcode = b_0_5 + b_6_10 + b_11_15 + b_16_23 + b_24_31

        opcode_int = int(b_opcode, 2)
        print(f'        0x{opcode_int:08x}: "{cur_mnem}",')
        new_instructions[opcode_int] = cur_mnem
    print('    },')
    #return new_instructions


if __name__ == '__main__':
    vle_table = parse_vle_table(table_contents)
    print(f'[+] VLE mnemonics parsed, {len(vle_table)} found')
    sanity_check(vle_table)

    #for instruction in vle_table:
    #    print(format_instruction(instruction))

    se_insts = [inst for inst in vle_table if inst['mnemonic'].startswith('se_')]
    e_insts = [inst for inst in vle_table if inst['mnemonic'].startswith('e_')]
    ppc_insts = [inst for inst in vle_table if inst not in se_insts and inst not in e_insts]

    print(f'[*] {len(se_insts)} SE_ instructions')
    #print('\n'.join(format_instruction(i) for i in se_insts))

    print(f'[*] {len(e_insts)} E_ instructions')
    #print('\n'.join(format_instruction(i) for i in e_insts))

    print(f'[*] {len(ppc_insts)} Other instructions')
    #print('\n'.join(format_instruction(i) for i in ppc_insts))

    # Sorted by opcode
    # ignoring opcodes by categories to match VLE PEM Table 3-1 "Non-VLE instructions listed by Mnemonic"
    '''
    ignore_categories = [
        '64', 'E.CD', 'E.CI', 'E.CL', 'E.PC', 'E.PD', 'E.PM', 'LIM', 'MA',
        'SP', 'SP.FD', 'SP.FS', 'SP.FV', 'WT', 'VEC'
    ]
    table_3_1_instructions = []
    for instruction in sorted(ppc_insts, key=lambda d: d['mnemonic']):
        if instruction['category'] not in ignore_categories:
            #print(format_instruction(instruction))
            table_3_1_instructions.append(instruction)
    print(f'[*]   {len(table_3_1_instructions)} instructions in Table 3-1')
    '''

    e_opcode_dict = build_e_ops(vle_table)
    print('Starting point for e_opcode_dict = {')
    for bitmask, mask_dict in sorted(e_opcode_dict.items()):
        print(f'    0x{bitmask:08x}: {{')
        for opcode, mnemonic in mask_dict.items():
            print(f'        0x{opcode:08x}: "{mnemonic}",')
        print('    },')
    print('}')

    # Skeleton code for getting the starting point of mask->opcode dicts that
    # integrate the libvle instruction tuples
    '''
    for mask, mask_dict in se_opcode_dict.items():
        print(f'    0x{mask:04x}: {{')
        for opcode, mnemonic in mask_dict.items():
            mnem_str = f'"{mnemonic}"'
            matching_lines = [line for line in se_op_lines if mnem_str in line]
            if len(matching_lines) > 1:
                print(f'multiple matches for {mnemonic}: {matching_lines}')
            inst_tuple = matching_lines[0]
            inst_tuple = inst_tuple.strip()
            print(f'        0x{opcode:04x}: {inst_tuple}')
        print(f'    }},')

    for mask, mask_dict in e_opcode_dict.items():
        print(f'    0x{mask:08x}: {{')
        for opcode, mnemonic in mask_dict.items():
            mnem_str = f'"{mnemonic}"'
            matching_lines = [line for line in e_ops_lines if mnem_str in line]
            if len(matching_lines) > 1:
                print(f'multiple matches for {mnemonic}: {matching_lines}')
            if len(matching_lines) == 0:
                print(f'No matching line for: "{mnemonic}" 0x{opcode:08x}')
                continue
            inst_tuple = matching_lines[0]
            inst_tuple = inst_tuple.strip()
            print(f'        0x{opcode:08x}: {inst_tuple}')
        print(f'    }},')
    '''

    print("New Interrupt helper instructions:")
    print_vle_interrupt_helpers()
