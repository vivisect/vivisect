import binascii
import unittest

import envi
import envi.memcanvas as e_memcanvas

import vivisect

# name, bytes, va, repr, txtRender
i386SingleByteOpcodes = [
    ('add', '0001', 0x40, 'add byte [ecx],al', 'add byte [ecx],al'),
    ('adc', '83D306', 0x40, 'adc ebx,6', 'adc ebx,6'),
    ('jg', '7faa', 0x400, 'jg 0x000003ac', 'jg 0x000003ac'),
    ('rep movsb', 'f3a4', 0x40, 'rep: movsb ', 'rep: movsb '),
    ('mov al', 'b0aa', 0x40, 'mov al,170', 'mov al,170'),
    ('mov ebx', 'b8aaaa4040', 0x40, 'mov eax,0x4040aaaa', 'mov eax,0x4040aaaa'),
    ('inc ebx', '43', 0x40, 'inc ebx', 'inc ebx'),
    ('call ebx', 'ffd3', 0x40, 'call ebx', 'call ebx'),
    ('call lit', 'e801010101', 0x40, 'call 0x01010146', 'call 0x01010146'),
    ('mov dword', '89aa41414141', 0x40, 'mov dword [edx + 1094795585],ebp', 'mov dword [edx + 1094795585],ebp'),
    ('imul 1', 'f6aaaaaaaaaa', 0x40, 'imul byte [edx - 1431655766]', 'imul byte [edx - 1431655766]'),
    ('imul 2', 'f7aaaaaaaaaa', 0x40, 'imul dword [edx - 1431655766]', 'imul dword [edx - 1431655766]'),
    ('push', 'fff0', 0x40, 'push eax', 'push eax'),
    ('push 2', '6aff', 0x40, 'push 0xffffffff', 'push 0xffffffff'),
    ('push 3', '68ffffffff', 0x40, 'push 0xffffffff', 'push 0xffffffff'),
    ('nop 1', '90', 0x40, 'nop ', 'nop '),
    ('nop 2', '0f1fc0', 0x40, 'nop eax', 'nop eax'),
    ('nop 3', 'f30f1fc0', 0x40, 'rep: nop eax', 'rep: nop eax'),
    ('pop', '8ff0', 0x40, 'pop eax', 'pop eax'),
    ('pop', '8ffb', 0x40, 'pop ebx', 'pop ebx'),
    ('BSWAP (eax)', '0fc8', 0x40, 'bswap eax', 'bswap eax'),
    ('BSWAP (ebx)', '0fcb', 0x40, 'bswap ebx', 'bswap ebx'),
    ('BSWAP (eax)', 'f30fc8', 0x40, 'rep: bswap eax', 'rep: bswap eax'),
    ('BSWAP (ebx)', 'f30fcb', 0x40, 'rep: bswap ebx', 'rep: bswap ebx'),
    ('setg (al)', '0f9fc0', 0x40, 'setg al', 'setg al'),
    ('setg (dl)', '0f9fc2', 0x40, 'setg dl', 'setg dl'),
    ('rep setg (al)', 'f30f9fc0', 0x40, 'rep: setg al', 'rep: setg al'),
    ('rep setg (dl)', 'f30f9fc2', 0x40, 'rep: setg dl', 'rep: setg dl'),
    ('prefix scas', 'f2ae', 0x40, 'repnz: scasb ', 'repnz: scasb '),
    ('jmp', 'E910000000', 0x40, 'jmp 0x00000055', 'jmp 0x00000055'),
    ('TEST', '84db', 0x40, 'test bl,bl', 'test bl,bl'),
    ('POP', '5D', 0x40, 'pop ebp', 'pop ebp'),
    ('POP', '5B', 0x40, 'pop ebx', 'pop ebx'),
    ('nop', '660f1cf8', 0x40, 'nop ax', 'nop ax'),
    ('nop', '660f1df8', 0x40, 'nop ax', 'nop ax'),
    ('nop', '660f1ef8', 0x40, 'nop ax', 'nop ax'),
    ('nop', '660f1ff8', 0x40, 'nop ax', 'nop ax'),
    ('nop', 'f20f1cfb', 0x40, 'repnz: nop ebx', 'repnz: nop ebx'),
    ('nop', 'f20f1dfb', 0x40, 'repnz: nop ebx', 'repnz: nop ebx'),
    ('nop', 'f20f1efb', 0x40, 'repnz: nop ebx', 'repnz: nop ebx'),
    ('nop', 'f20f1ffb', 0x40, 'repnz: nop ebx', 'repnz: nop ebx'),
    ('nop', 'f30f1cfa', 0x40, 'rep: nop edx', 'rep: nop edx'),
    ('nop', 'f30f1dfa', 0x40, 'rep: nop edx', 'rep: nop edx'),
    ('nop', 'f30f1efa', 0x40, 'rep: nop edx', 'rep: nop edx'),
    ('nop', 'f30f1ffa', 0x40, 'rep: nop edx', 'rep: nop edx'),
    ('nop', '0f1cfa', 0x40, 'nop edx', 'nop edx'),
    ('nop', '0f1dfa', 0x40, 'nop edx', 'nop edx'),
    ('nop', '0f1efa', 0x40, 'nop edx', 'nop edx'),
    ('nop', '0f1ffa', 0x40, 'nop edx', 'nop edx'),
    ('DIV 1', '66f7f2', 0x40, 'div dx', 'div dx'),
    ('DIV 2', 'f7f1', 0x40, 'div ecx', 'div ecx'),
    ('RCR 1', '66d1d8', 0x40, 'rcr ax,1', 'rcr ax,1'),
    ('ROL', 'd3c3', 0x40, 'rol ebx,cl', 'rol ebx,cl'),
]

i386MultiByteOpcodes = [
    ('CMPXCH8B', 'f00fc74d00', 0x40, 'lock: cmpxch8b qword [ebp]', 'lock: cmpxch8b qword [ebp]'),
    ('jmp 2', 'FF248D3A3A3A3A', 0x40, 'jmp dword [0x3a3a3a3a + ecx * 4]', 'jmp dword [0x3a3a3a3a + ecx * 4]'),
    ('MOV', '8B148541414141', 0x40, 'mov edx,dword [0x41414141 + eax * 4]', 'mov edx,dword [0x41414141 + eax * 4]'),
    ('MOV 2r', '678B14', 0x40, 'mov edx,dword [si]', 'mov edx,dword [si]'),
    ('PUSH 2', '67FF37', 0x40, 'push dword [bx]', 'push dword [bx]'),
    ('PUSH 3', '67ff30', 0x40, 'push dword [bx + si]', 'push dword [bx + si]'),
    ('PUSH 4', '67ff7020', 0x40, 'push dword [bx + si + 32]', 'push dword [bx + si + 32]'),
    ('ROR', '66d3c8', 0x40, 'ror ax,cl', 'ror ax,cl'),
    ('PEXTRB', '660F3A14D011', 0x40, 'pextrb eax,xmm2,17', 'pextrb eax,xmm2,17'),
    ('PEXTRB 2', '660F3A141011', 0x40, 'pextrb byte [eax],xmm2,17', 'pextrb byte [eax],xmm2,17'),
    ('MOV 3', '8B16', 0x40, 'mov edx,dword [esi]', 'mov edx,dword [esi]'),
    ('MOV 4', '66b90202', 0x40, 'mov cx,514', 'mov cx,514'),
    ('NOT', '66F7D0', 0x40, 'not ax', 'not ax'),
    ('NOT 2', 'F7D0', 0x40, 'not eax', 'not eax'),
    ('PUSH', '6653', 0x40, 'push bx', 'push bx'),
    ('CVTPD2PI', '660f2Daaaaaaaa41', 0x40, 'cvtpd2pi mm5,oword [edx + 1101703850]', 'cvtpd2pi mm5,oword [edx + 1101703850]'),
    ('CVTTPS2PI', '0f2caaaaaaaa41', 0x40, 'cvttps2pi mm5,qword [edx + 1101703850]', 'cvttps2pi mm5,qword [edx + 1101703850]'),
    ('CVTTSS2SI', 'f30f2caaaaaaaa41', 0x40, 'cvttss2si ebp,dword [edx + 1101703850]', 'cvttss2si ebp,dword [edx + 1101703850]'),
    ('CVTTSS2SI 2', 'f30f2ce9', 0x40, 'cvttss2si ebp,xmm1', 'cvttss2si ebp,xmm1'),
    ('CVTTPD2PI', '660f2caaaaaaaa41', 0x40, 'cvttpd2pi mm5,oword [edx + 1101703850]', 'cvttpd2pi mm5,oword [edx + 1101703850]'),
    ('CVTTSD2SI 2', 'f20f2caaaaaaaa41', 0x40, 'cvttsd2si ebp,qword [edx + 1101703850]', 'cvttsd2si ebp,qword [edx + 1101703850]'),
    ('ADDPS', '0f58aa41414141', 0x40, 'addps xmm5,oword [edx + 1094795585]', 'addps xmm5,oword [edx + 1094795585]'),
    ('MOVAPS', '0f28aa41414141', 0x40, 'movaps xmm5,oword [edx + 1094795585]', 'movaps xmm5,oword [edx + 1094795585]'),
    ('MOVAPD', '660f28aa41414141', 0x40, 'movapd xmm5,oword [edx + 1094795585]', 'movapd xmm5,oword [edx + 1094795585]'),
    ('RSM', '0faa', 0x40, 'rsm ', 'rsm '),
    ('MUL', 'f7e3', 0x40, 'mul ebx', 'mul ebx'),
    ('MUL 2', '66f7e3', 0x40, 'mul bx', 'mul bx'),
    ('PMULLW (66)', '660fd5cd', 0x40, 'pmullw xmm1,xmm5', 'pmullw xmm1,xmm5'),
    ('PMULLW', '0fd5e2', 0x40, 'pmullw mm4,mm2', 'pmullw mm4,mm2'),
    ('CMPXCH8B', '0fc70a', 0x40, 'cmpxch8b qword [edx]', 'cmpxch8b qword [edx]'),
    ('MOVD (66)', '660f7ecb', 0x40, 'movd ebx,xmm1', 'movd ebx,xmm1'),
    ('MOVD', '0F6E0D41414100', 0x40, 'movd mm1,dword [0x00414141]', 'movd mm1,dword [0x00414141]'),
    ('MOVQ', '0F6FCB', 0x40, 'movq mm1,mm3', 'movq mm1,mm3'),
    ('PSRAW',  '0FE1CA', 0x40, 'psraw mm1,mm2', 'psraw mm1,mm2'),
    ('PSLLQ (66)',  '660FF3CB', 0x40, 'psllq xmm1,xmm3', 'psllq xmm1,xmm3'),
    ('PALIGNR', '0F3A0FDC03', 0x40, 'palignr xmm3,xmm4,3', 'palignr xmm3,xmm4,3'),
    ('PALIGNR (66)',  '660F3A0FCA07', 0x40, 'palignr xmm1,xmm2,7', 'palignr xmm1,xmm2,7'),
    ('PSLLQ (reg)',  '660FF3CA', 0x40, 'psllq xmm1,xmm2', 'psllq xmm1,xmm2'),
    ('PSLLW (regs)',  '0F71F108', 0x40, 'psllw mm1,8', 'psllw mm1,8'),
    ('PSLLQ (66) 2',  '660F73F108', 0x40, 'psllq xmm1,8', 'psllq xmm1,8'),
    ('PSRLW (66)',  '660F71D611', 0x40, 'psrlw xmm6,17', 'psrlw xmm6,17'),
    ('PSRAD (66)',  '660F72E704', 0x40, 'psrad xmm7,4', 'psrad xmm7,4'),
    ('PSRLQ (66)',  '660F73D308', 0x40, 'psrlq xmm3,8', 'psrlq xmm3,8'),
    ('PSRAW (66)',  '660F71E108', 0x40, 'psraw xmm1,8', 'psraw xmm1,8'),
    ('PSRLDQ (66)', '660f73faaa', 0x40, 'pslldq xmm2,170', 'pslldq xmm2,170'),
    ('LFENCE', '0faee8', 0x40, 'lfence ', 'lfence '),
    ('LFENCE', '0faeea', 0x40, 'lfence ', 'lfence '),
    ('LFENCE', '0faeec', 0x40, 'lfence ', 'lfence '),
    ('LFENCE', '0faeef', 0x40, 'lfence ', 'lfence '),
    ('MFENCE', '0faef0', 0x40, 'mfence ', 'mfence '),
    ('MFENCE', '0faef2', 0x40, 'mfence ', 'mfence '),
    ('MFENCE', '0faef5', 0x40, 'mfence ', 'mfence '),
    ('MFENCE', '0faef7', 0x40, 'mfence ', 'mfence '),
    ('CVTTSS2SI', 'f30f2cc8', 0x40, 'cvttss2si ecx,xmm0', 'cvttss2si ecx,xmm0'),
    ('PREFIXES', 'f0673e2e65f30f10ca', 0x40, 'lock cs ds gs: movss xmm1,xmm2', 'lock cs ds gs: movss xmm1,xmm2'),
    ('BSR', '0fbdc3', 0x40, 'bsr eax,ebx', 'bsr eax,ebx'),
    ('LZNT', 'f30fbdc3', 0x40, 'lzcnt eax,ebx', 'lzcnt eax,ebx'),
    # Because of how the MODRM Bytes are set, these map to the same instruction
    # TODO: Would these be the same to a real x86 chip?
    ('PSRLDQ (66)', '660f73b5aa', 0x40, 'psllq xmm5,170', 'psllq xmm5,170'),
    ('PSRLDQ (66)', '660f73f5aa', 0x40, 'psllq xmm5,170', 'psllq xmm5,170'),
    # Same for these two
    ('PSRLDQ (66)', '660f73b1aa', 0x40, 'psllq xmm1,170', 'psllq xmm1,170'),
    ('PSRLDQ (66)', '660f73b9aa', 0x40, 'pslldq xmm1,170', 'pslldq xmm1,170'),

    ('ADDSS', 'f30f58ca', 0x40, 'addss xmm1,xmm2', 'addss xmm1,xmm2'),
    ('ADDSS 2', 'f30f580a', 0x40, 'addss xmm1,dword [edx]', 'addss xmm1,dword [edx]'),
    ('ADDSS 3', 'f30f585963', 0x40, 'addss xmm3,dword [ecx + 99]', 'addss xmm3,dword [ecx + 99]'),
    ('SQRTSS', 'f30f51d7', 0x40, 'sqrtss xmm2,xmm7', 'sqrtss xmm2,xmm7'),
    ('SQRTSS 2', 'f30f511c2541414141', 0x40, 'sqrtss xmm3,dword [0x41414141]', 'sqrtss xmm3,dword [0x41414141]'),
    ('SQRTSS 3', 'f30f511cd540000000', 0x40, 'sqrtss xmm3,dword [0x00000040 + edx * 8]', 'sqrtss xmm3,dword [0x00000040 + edx * 8]'),
    ('RSQRTSS', 'f30f52d7', 0x40, 'rsqrtss xmm2,xmm7', 'rsqrtss xmm2,xmm7'),
    ('RSQRTSS 2', 'f30f521c2541414141', 0x40, 'rsqrtss xmm3,dword [0x41414141]', 'rsqrtss xmm3,dword [0x41414141]'),
    ('RSQRTSS 3', 'f30f521cd540000000', 0x40, 'rsqrtss xmm3,dword [0x00000040 + edx * 8]', 'rsqrtss xmm3,dword [0x00000040 + edx * 8]'),
    ('RCPSS', 'f30f53cf', 0x40, 'rcpss xmm1,xmm7', 'rcpss xmm1,xmm7'),
    ('RCPSS 2', 'f30f5319', 0x40, 'rcpss xmm3,dword [ecx]', 'rcpss xmm3,dword [ecx]'),

    ('PCMPISTRI', '660f3a630f0d', 0x40, 'pcmpistri xmm1,oword [edi],13', 'pcmpistri xmm1,oword [edi],13'),
    ('PSHUFB', '660F3800EF', 0x40, 'pshufb xmm5,xmm7', 'pshufb xmm5,xmm7'),
    ('PSHUFB 2', '0F3800CA', 0x40, 'pshufb mm1,mm2', 'pshufb mm1,mm2'),
    ('PABSB', '660F381C08', 0x40, 'pabsb xmm1,oword [eax]', 'pabsb xmm1,oword [eax]'),
    ('PABSB 2', '0F381C1D41414141', 0x40, 'pabsb mm3,qword [0x41414141]', 'pabsb mm3,qword [0x41414141]'),
    ('RDTSC', '0F31', 0x40, 'rdtsc ', 'rdtsc '),
    ('RDTSCP', '0F01F9', 0x40, 'rdtscp ', 'rdtscp '),
    ('CVTDQ2PD', 'f30fe6c0', 0x40, 'cvtdq2pd xmm0,xmm0', 'cvtdq2pd xmm0,xmm0'),
    ('MOVQ', 'F30F7ECB', 0x40, 'movq xmm1,xmm3', 'movq xmm1,xmm3'),
    ('MOVQ (F3)', 'F30F7E0D41414100', 0x40, 'movq xmm1,qword [0x00414141]', 'movq xmm1,qword [0x00414141]'),
    ('MOVSD', 'f20f10ca', 0x40, 'movsd xmm1,xmm2', 'movsd xmm1,xmm2'),
    ('MOVSD (PREFIX)', 'f3f20f10ca', 0x40, 'rep: movsd xmm1,xmm2', 'rep: movsd xmm1,xmm2'),
    ('MOVSS (PREFIX)', 'f2f30f10ca', 0x40, 'repnz: movss xmm1,xmm2', 'repnz: movss xmm1,xmm2'),
    ('POPCNT', '66f30fb8c3', 0x40, 'popcnt ax,bx', 'popcnt ax,bx'),
    ('POPCNT', 'f30fb8c4', 0x40, 'popcnt eax,esp', 'popcnt eax,esp'),
    ('POPCNT', 'f30fb80541414100', 0x40, 'popcnt eax,dword [0x00414141]', 'popcnt eax,dword [0x00414141]'),
    ('LZCNT', 'f30fbdc4', 0x40, 'lzcnt eax,esp', 'lzcnt eax,esp'),
    ('LZCNT', 'f30fbd0541414100', 0x40, 'lzcnt eax,dword [0x00414141]', 'lzcnt eax,dword [0x00414141]'),
    ('MOVDQU', 'F30F6FCA', 0x40, 'movdqu xmm1,xmm2', 'movdqu xmm1,xmm2'),
    ('MOVDQU (MEM)', 'F30F6F4810', 0x40, 'movdqu xmm1,oword [eax + 16]', 'movdqu xmm1,oword [eax + 16]'),
    ('MOVDQU (REP)', 'F3F30F6FCA', 0x40, 'movdqu xmm1,xmm2', 'movdqu xmm1,xmm2'),
    ('MOVSD', 'f20f100d28330608', 0x40, 'movsd xmm1,qword [0x08063328]', 'movsd xmm1,qword [0x08063328]'),
    ('MOVSD 2', 'f20f1145f0', 0x40, 'movsd qword [ebp - 16],xmm0', 'movsd qword [ebp - 16],xmm0'),
    ('MOVSD 3', 'f20f100d70790908', 0x40, 'movsd xmm1,qword [0x08097970]', 'movsd xmm1,qword [0x08097970]'),
    ('MOVSS', 'f30f1045f8', 0x40, 'movss xmm0,dword [ebp - 8]', 'movss xmm0,dword [ebp - 8]'),
    ('MOVSS 2', 'f30f1055d0', 0x40, 'movss xmm2,dword [ebp - 48]', 'movss xmm2,dword [ebp - 48]'),
    ('MOVSS 3', 'F30F110D41414100', 0x40, 'movss dword [0x00414141],xmm1', 'movss dword [0x00414141],xmm1'),
    ('CVTSI2SS', 'f30f2ac8', 0x40, 'cvtsi2ss xmm1,eax', 'cvtsi2ss xmm1,eax'),
    ('MULSS', 'f30f59ca', 0x40, 'mulss xmm1,xmm2', 'mulss xmm1,xmm2'),
    ('SUBSS', 'f30f5cc1', 0x40, 'subss xmm0,xmm1', 'subss xmm0,xmm1'),
    ('CVTSS2SD', 'f30f5ac0', 0x40, 'cvtss2sd xmm0,xmm0', 'cvtss2sd xmm0,xmm0'),
    ('SQRTSS', 'f30f51d9', 0x40, 'sqrtss xmm3,xmm1', 'sqrtss xmm3,xmm1'),
    ('VMXON', 'f30fc73541414100', 0x40, 'vmxon qword [0x00414141]', 'vmxon qword [0x00414141]'),
    ('MULSD', 'f20f59c1', 0x40, 'mulsd xmm0,xmm1', 'mulsd xmm0,xmm1'),
    ('VMCLEAR', '660FC73541414100', 0x40, 'vmclear qword [0x00414141]', 'vmclear qword [0x00414141]'),
    ('CRC 1', 'f20f38f0e8', 0x40, 'crc32 ebp,al', 'crc32 ebp,al'),
    ('CRC 2', '66f20f38f1C3', 0x40, 'crc32 eax,bx', 'crc32 eax,bx'),
    ('CRC 3', 'f20f38f1C3', 0x40, 'crc32 eax,ebx', 'crc32 eax,ebx'),
    ('CLAC', '0f01ca', 0x40, 'clac ', 'clac '),
    ('STAC', '0f01cb', 0x40, 'stac ', 'stac '),
    ('VMFUNC', '0f01d4', 0x40, 'vmfunc ', 'vmfunc '),
    ('XEND', '0f01d5', 0x40, 'xend ', 'xend '),
    ('XGETBV', '0f01d0', 0x40, 'xgetbv ecx', 'xgetbv ecx'),
    ('XSETBV', '0f01d1', 0x40, 'xsetbv ecx', 'xsetbv ecx'),
    ('XADD', '660fc1d8', 0x40, 'xadd ax,bx', 'xadd ax,bx'),
    ('XADD 2', '0fc1d8', 0x40, 'xadd eax,ebx', 'xadd eax,ebx'),
    ('XTEST', '0f01d6', 0x40, 'xtest ', 'xtest '),
    ('MOVUPD', '660f10cc', 0x40, 'movupd xmm1,xmm4', 'movupd xmm1,xmm4'),
    ('MOVUPD', '660f1018', 0x40, 'movupd xmm3,oword [eax]', 'movupd xmm3,oword [eax]'),
    ('UNPCKLPD', '660F14A241414100', 0x40, 'unpcklpd xmm4,oword [edx + 4276545]', 'unpcklpd xmm4,oword [edx + 4276545]'),
    ('MOVHPD', '660F162541414141', 0x40, 'movhpd xmm4,oword [0x41414141]', 'movhpd xmm4,oword [0x41414141]'),
    ('MOVHPD', '660F172D41414141', 0x40, 'movhpd oword [0x41414141],xmm5', 'movhpd oword [0x41414141],xmm5'),
    ('MOVMSKPS', '0F50D6', 0x40, 'movmskps edx,xmm6', 'movmskps edx,xmm6'),
    ('MOVMSKPD', '660F50D6', 0x40, 'movmskpd edx,xmm6', 'movmskpd edx,xmm6'),
    ('PEXTRD', '660F3A16D011', 0x40, 'pextrd eax,xmm2,17', 'pextrd eax,xmm2,17'),
    ('PEXTRD 2', '660F3A161011', 0x40, 'pextrd dword [eax],xmm2,17', 'pextrd dword [eax],xmm2,17'),
    ('PEXTRD', '660F3A16EA11', 0x40, 'pextrd edx,xmm5,17', 'pextrd edx,xmm5,17'),
    ('PEXTRD 2', '660F3A161011', 0x40, 'pextrd dword [eax],xmm2,17', 'pextrd dword [eax],xmm2,17'),
    ('MOVBE',   '0F38F04910', 0x40, 'movbe ecx,dword [ecx + 16]', 'movbe ecx,dword [ecx + 16]'),
    ('MOVBE 2', '0F38F009', 0x40, 'movbe ecx,dword [ecx]', 'movbe ecx,dword [ecx]'),
    ('MOVBE 3', '0F38F00C8D41414141', 0x40, 'movbe ecx,dword [0x41414141 + ecx * 4]', 'movbe ecx,dword [0x41414141 + ecx * 4]'),
    ('MOVBE 4', '0F38F15110', 0x40, 'movbe dword [ecx + 16],edx', 'movbe dword [ecx + 16],edx'),
    ('MOVBE 5', '0F38F102', 0x40, 'movbe dword [edx],eax', 'movbe dword [edx],eax'),
    ('MOVBE 6', '0F38F10541414141', 0x40, 'movbe dword [0x41414141],eax', 'movbe dword [0x41414141],eax'),
    ('MOVBE 7', '660F38F00541414141', 0x40, 'movbe ax,word [0x41414141]', 'movbe ax,word [0x41414141]'),
    # TODO: so technically this is movhlps, but we need to have the operand change the opcode
    ('MOVLPS', '0F12DE', 0x40, 'movlps xmm3,xmm6', 'movlps xmm3,xmm6'),
    ('MOVLPS 2', '0F121D41414141', 0x40, 'movlps xmm3,qword [0x41414141]', 'movlps xmm3,qword [0x41414141]'),
    ('SUBPD', '660F5C6C240E', 0x40, 'subpd xmm5,oword [esp + 14]', 'subpd xmm5,oword [esp + 14]'),
    ('MAXPD', '660F5FAB0F270000', 0x40, 'maxpd xmm5,oword [ebx + 9999]', 'maxpd xmm5,oword [ebx + 9999]'),
    ('XORPD', '660F57BD15CD5B07', 0x40, 'xorpd xmm7,oword [ebp + 123456789]', 'xorpd xmm7,oword [ebp + 123456789]'),
    ('SQRTPD', '660f51ca', 0x40, 'sqrtpd xmm1,xmm2', 'sqrtpd xmm1,xmm2'),
    ('PSHUFD', '660F70CD11', 0x40, 'pshufd xmm1,xmm5,17', 'pshufd xmm1,xmm5,17'),
    ('PEXTRW', '660FC5C307', 0x40, 'pextrw eax,xmm3,7', 'pextrw eax,xmm3,7'),
    ('MOVQ', '660FD620', 0x40, 'movq qword [eax],xmm4', 'movq qword [eax],xmm4'),
    ('PMAXUB', '660FDE2541414141', 0x40, 'pmaxub xmm4,oword [0x41414141]', 'pmaxub xmm4,oword [0x41414141]'),
    ('MOVNTDQ', '660FE73D78563412', 0x40, 'movntdq oword [0x12345678],xmm7', 'movntdq oword [0x12345678],xmm7'),
    ('PADDD', '660FFECE', 0x40, 'paddd xmm1,xmm6', 'paddd xmm1,xmm6'),

    ('MOV AMETH_C', '0f20d0', 0x40, 'mov eax,ctrl2', 'mov eax,ctrl2'),
    ('MOV AMETH_C 2', '0f20f1', 0x40, 'mov ecx,ctrl6', 'mov ecx,ctrl6'),
    ('MOV AMETH_C 3', '0f22e2', 0x40, 'mov ctrl4,edx', 'mov ctrl4,edx'),
    ('MOV AMETH_C 4', '0f22f8', 0x40, 'mov ctrl7,eax', 'mov ctrl7,eax'),

    ('MOV AMETH_D', '0f21c0', 0x40, 'mov eax,debug0', 'mov eax,debug0'),
    ('MOV AMETH_D 2', '0f21f9', 0x40, 'mov ecx,debug7', 'mov ecx,debug7'),
    ('MOV AMETH_D 3', '0f23e1', 0x40, 'mov debug4,ecx', 'mov debug4,ecx'),
    ('PMOVMSKB', '660fd7f8', 0x40, 'pmovmskb edi,xmm0', 'pmovmskb edi,xmm0'),
    ('PMOVMSBK 2', '660fd7ca', 0x40, 'pmovmskb ecx,xmm2', 'pmovmskb ecx,xmm2'),
    ('PMOVMSKB 3', '0fd7f8', 0x40, 'pmovmskb edi,mm0', 'pmovmskb edi,mm0'),
    ('MOV SEGREG', '64a130000000', 0x40, 'fs: mov eax,dword [0x00000030]', 'fs: mov eax,dword [0x00000030]'),
    ('MOV SEGREG 2', '8ce0', 0x40, 'mov eax,fs', 'mov eax,fs'),
    ('MOV SEGREG 3', '8ec6', 0x40, 'mov es,esi', 'mov es,esi'),
    ('MOV SEGREG 4', '668ec6', 0x40, 'mov es,si', 'mov es,si'),
    ('MOV SEGREG 6', '8E142541414141', 0x40, 'mov ss,word [0x41414141]', 'mov ss,word [0x41414141]'),
    ('MOV SEGREG 7', '8C042541414141', 0x40, 'mov word [0x41414141],es', 'mov word [0x41414141],es'),

    ('LEA', '8d5a0c', 0x40, 'lea ebx,dword [edx + 12]', 'lea ebx,dword [edx + 12]'),
    ('SIGNED', '83C0F9', 0x40, 'add eax,0xfffffff9', 'add eax,0xfffffff9'),
    ('MAXPD', '660F5F64C020', 0x40, 'maxpd xmm4,oword [eax + eax * 8 + 32]', 'maxpd xmm4,oword [eax + eax * 8 + 32]'),
    ('MAXPD 2', '660f5fa490d0a80000', 0x40, 'maxpd xmm4,oword [eax + edx * 4 + 43216]', 'maxpd xmm4,oword [eax + edx * 4 + 43216]'),
    # ('rm4mod2', '', 0x40, '', ''),

    ('PMOVSXBW', '660f3820ca', 0x40, 'pmovsxbw xmm1,xmm2', 'pmovsxbw xmm1,xmm2'),
    ('PMOVSXBD', '660f3821cb', 0x40, 'pmovsxbd xmm1,xmm3', 'pmovsxbd xmm1,xmm3'),
    ('PMOVSXBQ', '660f3822d3', 0x40, 'pmovsxbq xmm2,xmm3', 'pmovsxbq xmm2,xmm3'),
    ('PMOVSXWD', '660f3823ff', 0x40, 'pmovsxwd xmm7,xmm7', 'pmovsxwd xmm7,xmm7'),
    ('PMOVSXWQ', '660f3824dc', 0x40, 'pmovsxwq xmm3,xmm4', 'pmovsxwq xmm3,xmm4'),
    ('PMOVSXDQ', '660f3825df', 0x40, 'pmovsxdq xmm3,xmm7', 'pmovsxdq xmm3,xmm7'),

    ('PMOVZXBW', '660f3830ca', 0x40, 'pmovzxbw xmm1,xmm2', 'pmovzxbw xmm1,xmm2'),
    ('PMOVZXBD', '660f3831cb', 0x40, 'pmovzxbd xmm1,xmm3', 'pmovzxbd xmm1,xmm3'),
    ('PMOVZXBQ', '660f3832d3', 0x40, 'pmovzxbq xmm2,xmm3', 'pmovzxbq xmm2,xmm3'),
    ('PMOVZXWD', '660f3833ff', 0x40, 'pmovzxwd xmm7,xmm7', 'pmovzxwd xmm7,xmm7'),
    ('PMOVZXWQ', '660f3834dc', 0x40, 'pmovzxwq xmm3,xmm4', 'pmovzxwq xmm3,xmm4'),
    ('PMOVZXDQ', '660f3835df', 0x40, 'pmovzxdq xmm3,xmm7', 'pmovzxdq xmm3,xmm7'),

    ('PMOVSXBW (MEM)', '660f382018', 0x40, 'pmovsxbw xmm3,qword [eax]', 'pmovsxbw xmm3,qword [eax]'),
    ('PMOVSXBD (MEM)', '660f3821242541414141', 0x40, 'pmovsxbd xmm4,dword [0x41414141]', 'pmovsxbd xmm4,dword [0x41414141]'),
    ('PMOVSXBQ (MEM)', '660f38228b29230000', 0x40, 'pmovsxbq xmm1,word [ebx + 9001]', 'pmovsxbq xmm1,word [ebx + 9001]'),
    ('PMOVSXWD (MEM)', '660f38230c11', 0x40, 'pmovsxwd xmm1,qword [ecx + edx]', 'pmovsxwd xmm1,qword [ecx + edx]'),
    ('PMOVSXWQ (MEM)', '660f38241cb507000000', 0x40, 'pmovsxwq xmm3,dword [0x00000007 + esi * 4]', 'pmovsxwq xmm3,dword [0x00000007 + esi * 4]'),
    ('PMOVSXDQ (MEM)', '660f382532', 0x40, 'pmovsxdq xmm6,qword [edx]', 'pmovsxdq xmm6,qword [edx]'),

    ('PMOVSXBW (MEM)', '660f383018', 0x40, 'pmovzxbw xmm3,qword [eax]', 'pmovzxbw xmm3,qword [eax]'),
    ('PMOVSXBD (MEM)', '660f3831242541414141', 0x40, 'pmovzxbd xmm4,dword [0x41414141]', 'pmovzxbd xmm4,dword [0x41414141]'),
    ('PMOVSXBQ (MEM)', '660f38328b29230000', 0x40, 'pmovzxbq xmm1,word [ebx + 9001]', 'pmovzxbq xmm1,word [ebx + 9001]'),
    ('PMOVSXWD (MEM)', '660f38330c11', 0x40, 'pmovzxwd xmm1,qword [ecx + edx]', 'pmovzxwd xmm1,qword [ecx + edx]'),
    ('PMOVSXWQ (MEM)', '660f38341cb507000000', 0x40, 'pmovzxwq xmm3,dword [0x00000007 + esi * 4]', 'pmovzxwq xmm3,dword [0x00000007 + esi * 4]'),
    ('PMOVSXDQ (MEM)', '660f383532', 0x40, 'pmovzxdq xmm6,qword [edx]', 'pmovzxdq xmm6,qword [edx]'),
    ('SFENCE', '0faef8', 0x40, 'sfence ', 'sfence '),
    ('LFENCE', '0faee8', 0x40, 'lfence ', 'lfence '),
    ('MFENCE', '0faef0', 0x40, 'mfence ', 'mfence '),
    ('XSAVE', '0FAE2541414141', 0x40, 'xsave dword [0x41414141]', 'xsave dword [0x41414141]'),

    ('ptest', '660F3817242541414141', 0x40, 'ptest xmm4,oword [0x41414141]', 'ptest xmm4,oword [0x41414141]'),
    # TODO: Should we add the implicit xmm0 to these? It's only in non-vex mode
    ('blendvps', '660F3814CB', 0x40, 'blendvps xmm1,xmm3', 'blendvps xmm1,xmm3'),
    ('pblendvb', '660F3815CB', 0x40, 'blendvpd xmm1,xmm3', 'blendvpd xmm1,xmm3'),

    # AES-NI feature set
    ('AESENC', '660F38DCEA', 0x40, 'aesenc xmm5,xmm2', 'aesenc xmm5,xmm2'),
    ('AESENC (MEM)', '660f38DC3A', 0x40, 'aesenc xmm7,oword [edx]', 'aesenc xmm7,oword [edx]'),
    ('AESENC (MEM 2)', '660f38DC7C2404', 0x40, 'aesenc xmm7,oword [esp + 4]', 'aesenc xmm7,oword [esp + 4]'),
    ('AESENC (MEM 3)', '660F38DC1D41414141', 0x40, 'aesenc xmm3,oword [0x41414141]', 'aesenc xmm3,oword [0x41414141]'),
    ('AESENCLAST', '660F38DDDC', 0x40, 'aesenclast xmm3,xmm4', 'aesenclast xmm3,xmm4'),
    ('AESENCLAST (MEM)', '660F38DD18', 0x40, 'aesenclast xmm3,oword [eax]', 'aesenclast xmm3,oword [eax]'),
    ('AESENCLAST (MEM 2)', '660F38DD5808', 0x40, 'aesenclast xmm3,oword [eax + 8]', 'aesenclast xmm3,oword [eax + 8]'),
    ('AESENCLAST (MEM 3)', '660F38DD2578563442', 0x40, 'aesenclast xmm4,oword [0x42345678]', 'aesenclast xmm4,oword [0x42345678]'),
    ('AESDEC', '660f38DECB', 0x40, 'aesdec xmm1,xmm3', 'aesdec xmm1,xmm3'),
    ('AESDEC (MEM)', '660F38DE0C24', 0x40, 'aesdec xmm1,oword [esp]', 'aesdec xmm1,oword [esp]'),
    ('AESDEC (MEM 2)', '660F38DE5D0C', 0x40, 'aesdec xmm3,oword [ebp + 12]', 'aesdec xmm3,oword [ebp + 12]'),
    ('AESDEC (MEM 3)', '660F38DE3544434241', 0x40, 'aesdec xmm6,oword [0x41424344]', 'aesdec xmm6,oword [0x41424344]'),
    ('AESDECLAST', '660F38DFED', 0x40, 'aesdeclast xmm5,xmm5', 'aesdeclast xmm5,xmm5'),
    ('AESDECLAST (MEM)', '660F38DF2E', 0x40, 'aesdeclast xmm5,oword [esi]', 'aesdeclast xmm5,oword [esi]'),
    ('AESDECLAST (MEM 2)', '660F38DF6740', 0x40, 'aesdeclast xmm4,oword [edi + 64]', 'aesdeclast xmm4,oword [edi + 64]'),
    ('AESDECLAST (MEM 3)', '660F38DF2511213141', 0x40, 'aesdeclast xmm4,oword [0x41312111]', 'aesdeclast xmm4,oword [0x41312111]'),
    ('AESIMC', '660F38DBF9', 0x40, 'aesimc xmm7,xmm1', 'aesimc xmm7,xmm1'),
    ('AESIMC (MEM)', '660F38DB13', 0x40, 'aesimc xmm2,oword [ebx]', 'aesimc xmm2,oword [ebx]'),
    ('AESIMC (MEM 2)', '660F38DB5020', 0x40, 'aesimc xmm2,oword [eax + 32]', 'aesimc xmm2,oword [eax + 32]'),
    ('AESIMC (MEM 3)', '660F38DB1D00000041', 0x40, 'aesimc xmm3,oword [0x41000000]', 'aesimc xmm3,oword [0x41000000]'),
    ('AESKEYGENASSIST', '660F3ADFFE08', 0x40, 'aeskeygenassist xmm7,xmm6,8', 'aeskeygenassist xmm7,xmm6,8'),
    ('AESKEYGENASSIST (MEM)', '660F3ADF1AFE', 0x40, 'aeskeygenassist xmm3,oword [edx],254', 'aeskeygenassist xmm3,oword [edx],254'),
    ('AESKEYGENASSIST (MEM 2)', '660F3ADF998000000039', 0x40, 'aeskeygenassist xmm3,oword [ecx + 128],57', 'aeskeygenassist xmm3,oword [ecx + 128],57'),
    ('AESKEYGENASSIST (MEM 3)', '660F3ADF2541414141C6', 0x40, 'aeskeygenassist xmm4,oword [0x41414141],198', 'aeskeygenassist xmm4,oword [0x41414141],198'),
    ('PCLMULQDQ', '660F3A44D307', 0x40, 'pclmulqdq xmm2,xmm3,7', 'pclmulqdq xmm2,xmm3,7'),
    ('PCLMULQDQ (MEM)', '660F3A441007', 0x40, 'pclmulqdq xmm2,oword [eax],7', 'pclmulqdq xmm2,oword [eax],7'),
    ('PCLMULQDQ (MEM 2)', '660F3A4478119C', 0x40, 'pclmulqdq xmm7,oword [eax + 17],156', 'pclmulqdq xmm7,oword [eax + 17],156'),
    ('PCLMULQDQ (MEM 3)', '660F3A443D41414141C6', 0x40, 'pclmulqdq xmm7,oword [0x41414141],198', 'pclmulqdq xmm7,oword [0x41414141],198'),
    ('RDRAND', '0fc7f0', 0x40, 'rdrand eax', 'rdrand eax'),
    ('RDSEED', '0fc7f8', 0x40, 'rdseed eax', 'rdseed eax'),
    ('VMPTRST', '0fc73d41414141', 0x40, 'vmptrst qword [0x41414141]', 'vmptrst qword [0x41414141]'),
    ('VMCLEAR', '0fc73541414141', 0x40, 'vmptrld qword [0x41414141]', 'vmptrld qword [0x41414141]'),
    ('CMPXCHG', '0fb0d0', 0x40, 'cmpxchg al,dl', 'cmpxchg al,dl'),
    ('ADOX', 'F30F38f6c2', 0x40, 'adox eax,edx', 'adox eax,edx'),
    ('ADOX MEM', 'F30F38F6042541414141', 0x40, 'adox eax,dword [0x41414141]', 'adox eax,dword [0x41414141]'),
    ('ADCX', '660f38f6e5', 0x40, 'adcx esp,ebp', 'adcx esp,ebp'),
    ('ADCX MEM', '660f38f6242541414141', 0x40, 'adcx esp,dword [0x41414141]', 'adcx esp,dword [0x41414141]'),
]


class i386InstructionSet(unittest.TestCase):
    _arch = envi.getArchModule("i386")

    def check_opreprs(self, opcodes):
        vw = vivisect.VivWorkspace()
        scanv = e_memcanvas.StringMemoryCanvas(vw)

        for name, bytez, va, reprOp, renderOp in opcodes:
            try:
                op = self._arch.archParseOpcode(binascii.unhexlify(bytez), 0, va)
            except envi.InvalidInstruction:
                self.fail("Failed to parse opcode bytes: %s (case: %s, expected: %s)" % (bytez, name, reprOp))
            except Exception:
                self.fail("Failed to parse opcode bytes: %s (case: %s, expected: %s)" % (bytez, name, reprOp))
            msg = '%s failed length check. Got %d, expected %d' % (name, len(op), int(len(bytez)/2))
            self.assertEqual(len(op), int(len(bytez)/2), msg=msg)
            # print("'%s', 0x%x, '%s' == '%s'" % (bytez, va, repr(op), reprOp))
            try:
                self.assertEqual(repr(op), reprOp)
            except AssertionError:
                self.fail("Failing match for case %s (%s != %s)" % (name, repr(op), reprOp))

            scanv.clearCanvas()
            op.render(scanv)
            self.assertEqual(scanv.strval, renderOp)

    def test_envi_i386_disasm_Specific_SingleByte_Instrs(self):
        self.check_opreprs(i386SingleByteOpcodes)

    def test_envi_i386_disasm_Specific_MultiByte_Instrs(self):
        self.check_opreprs(i386MultiByteOpcodes)

    def checkOpcode(self, hexbytez, va, oprepr, opcheck, opercheck, renderOp):

        op = self._arch.archParseOpcode(binascii.unhexlify(hexbytez), 0, va)
        self.assertEqual(repr(op), oprepr)
        opvars = vars(op)
        for opk, opv in opcheck.items():
            self.assertEqual((opk, opvars.get(opk)), (opk, opv))

        for oidx in range(len(op.opers)):
            oper = op.opers[oidx]
            opervars = vars(oper)
            for opk, opv in opercheck[oidx].items():
                self.assertEqual((opk, opervars.get(opk)), (opk, opv))

        vw = vivisect.VivWorkspace()
        scanv = e_memcanvas.StringMemoryCanvas(vw)
        op.render(scanv)
        self.assertEqual(scanv.strval, renderOp)

    def test_envi_i386_disasm_Reg_Operands(self):
        '''
        test an opcode encoded with an Reg operand
        _0      add al      04
        G       add         02
        C       mov         0f20
        D       mov         0f21
        P       punpcklbw   0f60
        S       mov         8c
        U       movmskps    0f50
        V       sqrtps      0f51

        '''
        opbytez = '0032'
        oprepr = 'add byte [edx],dh'
        opcheck = {'iflags': 65536, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'add', 'opcode': 8193, 'size': 2}
        opercheck = ({'disp': 0, 'tsize': 1, '_is_deref': True, 'reg': 2}, {'tsize': 1, 'reg': 134742018},)
        self.checkOpcode(opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr)

        opbytez = '0440'
        oprepr = 'add al,64'
        opcheck = {'iflags': 65536, 'prefixes': 0, 'mnem': 'add', 'opcode': 8193, 'size': 2}
        opercheck = ({'tsize': 1, 'reg': 524288}, {'tsize': 1, 'imm': 64})
        self.checkOpcode(opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr)

        opbytez = '0218'
        oprepr = 'add bl,byte [eax]'
        opcheck = {'iflags': 65536, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'add', 'opcode': 8193, 'size': 2}
        opercheck = ( {'tsize': 1, 'reg': 524291}, {'disp': 0, 'tsize': 1, '_is_deref': True, 'reg': 0} )
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        opbytez = '0f2018'
        oprepr = 'mov dword [eax],ctrl3'
        opcheck =  {'iflags': 65536, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'mov', 'opcode': 24577, 'size': 3}
        opercheck = ( {'disp': 0, 'tsize': 4, '_is_deref': True, 'reg': 0}, {'tsize': 4, 'reg': 27} )
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

    def test_envi_i386_disasm_Imm_Operands(self):
        '''
        test an opcode encoded with an Imm operand
        _0      rol         d000
        A       callf       9a
        '''
        opbytez = 'd000'
        oprepr = 'rol byte [eax],1'
        opcheck =  {'iflags': 65536, 'va': 16384, 'prefixes': 0, 'mnem': 'rol', 'opcode': 8201, 'size': 2}
        opercheck = ( {'disp': 0, 'tsize': 1, '_is_deref': True, 'reg': 0}, {'tsize': 4, 'imm': 1} )
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        # this is failing legitimately... we decode this opcode wrong
        opbytez = '9aaa11aabbcc33'
        oprepr = 'callf 0x33cc:0xbbaa11aa'
        opcheck =  {'iflags': 65540, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'callf', 'opcode': 4099, 'size': 7}
        opercheck = [{'tsize': 6, 'imm': 56954414829994}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

    def test_envi_i386_disasm_PcRel_Operands(self):
        '''
        test an opcode encoded with an PcRelative operand
        '''
        pass

    def test_envi_i386_disasm_RegMem_Operands(self):
        '''
        test an opcode encoded with an RegMem operand
        X       outsb       6e
        Y       insd        6d
        '''
        opbytez = '6e'
        oprepr = 'outsb edx,byte [esi]'
        opcheck = {'iflags': 65538, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'outsb', 'opcode': 57347, 'size': 1}
        opercheck = [{'tsize': 4, 'reg': 2}, {'disp': 0, 'tsize': 1, '_is_deref': True, 'reg': 6}]
        self.checkOpcode(opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr)

        opbytez = '6d'
        oprepr = 'insd dword [esi],edx'
        opcheck =  {'iflags': 65538, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'insd', 'opcode': 57346, 'size': 1}
        opercheck = [{'disp': 0, 'tsize': 4, '_is_deref': True, 'reg': 6}, {'tsize': 4, 'reg': 2}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

    def test_envi_i386_disasm_ImmMem_Operands(self):
        '''
        test an opcode encoded with an ImmMem operand
        O       mov         a1
        '''
        opbytez = 'a1a2345678'
        oprepr = 'mov eax,dword [0x785634a2]'
        opcheck =  {'iflags': 65536, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'mov', 'opcode': 24577, 'size': 5}
        opercheck = [{'tsize': 4, 'reg': 0}, {'tsize': 4, '_is_deref': True, 'imm': 2018915490}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

    def test_envi_i386_disasm_SIB_Operands(self):
        '''
        exercize the entire SIB operand space
        A       jmp         ea
        E       lar         0f02
        Q       cvttps2pi   0f2c
        W       cvttps2pi   0f2c
        '''
        opbytez = 'eaa123456789ab'          # this wants more bytes, why?
        oprepr = 'jmp 0xab89:0x674523a1'       # this repr's wrong.  it should be ab89:674523a1
        opcheck = {'iflags': 65545, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'jmp', 'opcode': 4097, 'size': 7}
        opercheck = [{'tsize': 6, 'imm': 188606631453601}]
        self.checkOpcode(opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr)

        opbytez = '0f02aabbccddee'
        oprepr = 'lar ebp,word [edx - 287454021]'
        opcheck = {'iflags': 65538, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'lar', 'opcode': 57344, 'size': 7}
        opercheck = [{'tsize': 4, 'reg': 5}, {'disp': -287454021, 'tsize': 2, '_is_deref': True, 'reg': 2}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        opbytez = '0f2caabbccddeeff'
        oprepr = 'cvttps2pi mm5,qword [edx - 287454021]'
        opcheck = {'iflags': 65536, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'cvttps2pi', 'opcode': 61440}
        opercheck = [{'tsize': 8, 'reg': 4194355}, {'disp': -287454021, 'tsize': 8, '_is_deref': True, 'reg': 2}]
        self.checkOpcode(opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr)
