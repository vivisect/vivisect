import binascii
import unittest

import envi
import envi.memcanvas as e_memcanvas
import envi.archs.amd64 as e_amd64

import vivisect

instrs = [
    ("41b401", 0x456000, 'mov r12l, 1'),      # ndisasm and oda say "mov r12b, 1" but ia32 manual says "r12l"
    ("bf9fb44900", 0x456000, 'mov edi,0x0049b49f'),
    ("48bf9fb44900aabbccdd", 0x456000, 'mov rdi,0xddccbbaa0049b49f'),
    ("c705b58a270001000000", 0x456005, 'mov dword [rip + 2591413],1'),
    ("48c705e68a270084ef4a00", 0x45600f, 'mov qword [rip + 2591462],0x004aef84'),
    ("48c705b39b2700105f4500", 0x45601a, 'mov qword [rip + 2595763],0x00455f10'),
    ('c4e2f1004141', 0x456000, 'vpshufb xmm0,xmm1,oword [rcx + 65]'),
    ('c4e2f5004141', 0x456000, 'vpshufb ymm0,ymm1,yword [rcx + 65]'),
    ('0f38004141', 0x456000, 'pshufb mm0,qword [rcx + 65]'),
    ("4585f6", 0x456000, 'test r14d,r14d'),
]


class Amd64InstrTest(unittest.TestCase):
    def test_envi_amd64_assorted_instrs(self):
        global instrs

        archmod = envi.getArchModule("amd64")

        for bytez, va, reprOp in instrs:
            op = archmod.archParseOpcode(binascii.unhexlify(bytez), 0, va)
            if repr(op).replace(' ', '') != reprOp.replace(' ', ''):
                raise Exception("FAILED to decode instr:  %.8x %s - should be: %s  - is: %s" %
                                (va, bytez, reprOp, repr(op)))

    # FIXME: test emuluation as well.


# name, bytes, va, repr, txtRender
amd64SingleByteOpcodes = [
    ('add', '0001', 'add byte [rcx],al', 'add byte [rcx],al'),
    ('jg', '7faa', 'jg 0x000003ac', 'jg 0x000003ac'),
    ('rep movsb', 'f3a4', 'rep: movsb ', 'rep: movsb '),
    ('mov al', 'b0aa', 'mov al,170', 'mov al,170'),
    ('mov ebx', 'b8aaaa4040', 'mov eax,0x4040aaaa', 'mov eax,0x4040aaaa'),
    ('mov ah', 'b407', 'mov ah,7', 'mov ah,7'),
    ('call ebx', 'ffd3', 'call rbx', 'call rbx'),
    ('call lit', 'e801010101', 'call 0x01010506', 'call 0x01010506'),
    ('mov dword', '89aa41414141', 'mov dword [rdx + 1094795585],ebp', 'mov dword [rdx + 1094795585],ebp'),
    ('imul 1', 'f6aaaaaaaaaa', 'imul byte [rdx - 1431655766]', 'imul byte [rdx - 1431655766]'),
    ('imul 2', 'f7aaaaaaaaaa', 'imul dword [rdx - 1431655766]', 'imul dword [rdx - 1431655766]'),
    ('imul 3', '69c341410000', 'imul eax,ebx,0x00004141', 'imul eax,ebx,0x00004141'),
    ('imul 4', '4869C341414141', 'imul rax,rbx,0x41414141', 'imul rax,rbx,0x41414141'),
    ('push', 'fff0', 'push rax', 'push rax'),
    ('push 2', '6aff', 'push 0xffffffffffffffff', 'push 0xffffffffffffffff'),
    ('push 3', '68ffffffff', 'push 0xffffffffffffffff', 'push 0xffffffffffffffff'),
    ('pop', '8ff0', 'pop rax', 'pop rax'), # TODO: This isn't a real instr. 8F can only be mem, using r/m to determine encoding
    ('pop', '8ffb', 'pop rbx', 'pop rbx'), # TODO: neither is this
    ('push', '48fff0', 'push rax', 'push rax'),
    ('pop', '488ff0', 'pop rax', 'pop rax'),
    ('pop', '488ffb', 'pop rbx', 'pop rbx'),
    ('nop', '660f1cf8', 'nop ax', 'nop ax'),
    ('nop', '660f1df8', 'nop ax', 'nop ax'),
    ('nop', '660f1ef8', 'nop ax', 'nop ax'),
    ('nop', '660f1ff8', 'nop ax', 'nop ax'),
    ('nop', 'f20f1cfb', 'repnz: nop ebx', 'repnz: nop ebx'),
    ('nop', 'f20f1dfb', 'repnz: nop ebx', 'repnz: nop ebx'),
    ('nop', 'f20f1efb', 'repnz: nop ebx', 'repnz: nop ebx'),
    ('nop', 'f20f1ffb', 'repnz: nop ebx', 'repnz: nop ebx'),
    ('nop', 'f30f1cfa', 'rep: nop edx', 'rep: nop edx'),
    ('nop', 'f30f1dfa', 'rep: nop edx', 'rep: nop edx'),
    ('nop', 'f30f1efa', 'rep: nop edx', 'rep: nop edx'),
    ('nop', 'f30f1ffa', 'rep: nop edx', 'rep: nop edx'),
    ('nop', '0f1cfa', 'nop edx', 'nop edx'),
    ('nop', '0f1dfa', 'nop edx', 'nop edx'),
    ('nop', '0f1efa', 'nop edx', 'nop edx'),
    ('nop', '0f1ffa', 'nop edx', 'nop edx'),
    ('ud2', '0f0b', 'ud2 ', 'ud2 '),
    ('FISTTP', 'db08', 'fisttp dword [rax]', 'fisttp dword [rax]'),
    ('FISTTP 2', 'df08', 'fisttp word [rax]', 'fisttp word [rax]'),
    ('FISTTP 3', 'dd08', 'fisttp qword [rax]', 'fisttp qword [rax]'),
    ('FDIV', 'd8f1', 'fdiv st0,st1', 'fdiv st0,st1'),
    ('FXCH', 'd9ca', 'fxch st0,st2', 'fxch st0,st2'),
    ('FADDP', 'dec1', 'faddp st1,st0', 'faddp st1,st0'),
    ('PREFETCH0', '0f1809', 'prefetch0 byte [rcx]', 'prefetch0 byte [rcx]'),
    ('PREFETCH1', '0f1810', 'prefetch1 byte [rax]', 'prefetch1 byte [rax]'),
    ('PREFETCH2', '0f181b', 'prefetch2 byte [rbx]', 'prefetch2 byte [rbx]'),
    ('PREFETCHNTA', '0f1802', 'prefetchnta byte [rdx]', 'prefetchnta byte [rdx]'),
    ('PREFETCH0', '670f1809', 'prefetch0 byte [ecx]', 'prefetch0 byte [ecx]'),
    ('PREFETCH1', '670f1810', 'prefetch1 byte [eax]', 'prefetch1 byte [eax]'),
    ('PREFETCH2', '670f181b', 'prefetch2 byte [ebx]', 'prefetch2 byte [ebx]'),
    ('PREFETCHNTA', '670f1802', 'prefetchnta byte [edx]', 'prefetchnta byte [edx]'),
    # ('CDQE', '4898', 'cdqe ', 'cdqe '), # It bothers me that this doesn't work
    ('BSWAP (eax)', 'f30fc8', 'rep: bswap eax', 'rep: bswap eax'),
    ('DIV 1', '66f7f2', 'div dx', 'div dx'),
    ('DIV 2', 'f7f1', 'div ecx', 'div ecx'),
    ('DIV 3', '49f7f3', 'div r11', 'div r11'),
    ('ROL', '49d3c3', 'rol r11,cl', 'rol r11,cl'),
]

amd64MultiByteOpcodes = [
    # These are all valid tests, but our current impl of prefix 67 is borked
    ('BLSR 2', '67C4E278F30B', 'blsr eax,dword [ebx]', 'blsr eax,dword [ebx]'),
    ('PUSH 2', '67FF37', 'push qword [edi]', 'push qword [edi]'),
    ('MOV w/ size', '67488B16', 'mov rdx,qword [esi]', 'mov rdx,qword [esi]'),
    ('HSUBPS', '67F20F7D9041414141', 'hsubps xmm2,oword [eax + 1094795585]', 'hsubps xmm2,oword [eax + 1094795585]'),
    ('PEXTRD 3', '67660F3A162A11', 'pextrd_q dword [edx],xmm5,17', 'pextrd_q dword [edx],xmm5,17'),
    ('PEXTRQ 3', '6766480F3A16A34141414175', 'pextrd_q qword [ebx + 1094795585],xmm4,117', 'pextrd_q qword [ebx + 1094795585],xmm4,117'),
    ('TEST', '67F70078563412', 'test dword [eax],0x12345678', 'test dword [eax],0x12345678'),
    ('HSUBPS 4', '67F20F7D12', 'hsubps xmm2,oword [edx]', 'hsubps xmm2,oword [edx]'),
    ('CVTSI2SS 3', '67f3440f2a02', 'cvtsi2ss xmm8,dword [edx]', 'cvtsi2ss xmm8,dword [edx]'),
    ('RCPSS 3', '67f3440f531a', 'rcpss xmm11,dword [edx]', 'rcpss xmm11,dword [edx]'),
    ('UNPCKHPD', '67660F158841414141', 'unpckhpd xmm1,oword [eax + 1094795585]', 'unpckhpd xmm1,oword [eax + 1094795585]'),

    ('INSERTPS', '660F3A21CB59', 'insertps xmm1,xmm3,89', 'insertps xmm1,xmm3,89'),
    ('INSERTPS 2', '660F3A21500449', 'insertps xmm2,dword [rax + 4],73', 'insertps xmm2,dword [rax + 4],73'),
    ('INSERTPS 3', '660F3A2114254141414149', 'insertps xmm2,dword [0x41414141],73', 'insertps xmm2,dword [0x41414141],73'),
    ('HSUBPS 2', 'F20F7D9041414141', 'hsubps xmm2,oword [rax + 1094795585]', 'hsubps xmm2,oword [rax + 1094795585]'),
    ('HSUBPS 3', 'F20F7D10', 'hsubps xmm2,oword [rax]', 'hsubps xmm2,oword [rax]'),
    ('MUL 1', 'f6e4', 'mul ah', 'mul ah'),
    # ('MUL 2', '48f6e4', 'mul al,spl', 'mul al,spl'),  # TODO: Valid?
    ('MUL 3', 'f7e2', 'mul edx', 'mul edx'),
    ('MUL 4', '49f7e3', 'mul r11', 'mul r11'),
    ('MUL 5', 'f620', 'mul byte [rax]', 'mul byte [rax]'),
    #('MUL (REX)', '', 'mul ax,al', 'mul '),
    ('NOT', '66F7D0', 'not ax', 'not ax'),
    ('NOT 2', 'F7D0', 'not eax', 'not eax'),
    ('PUSH', '6653', 'push bx', 'push bx'),
    ('CMPPS 0', '440fc2e35a', 'cmpps xmm12,xmm3,90', 'cmpps xmm12,xmm3,90'),
    ('CMPPS 1', '440fc224254a4a4a4a53', 'cmpps xmm12,oword [0x4a4a4a4a],83', 'cmpps xmm12,oword [0x4a4a4a4a],83'),
    ('CMPPS 2', '440fc220ec', 'cmpps xmm12,oword [rax],236', 'cmpps xmm12,oword [rax],236'),
    ('CMPPS 3', '450fc2a2d4000000cf', 'cmpps xmm12,oword [r10 + 212],207', 'cmpps xmm12,oword [r10 + 212],207'),
    ('CMPPS 4', '460fc224f5d400000081', 'cmpps xmm12,oword [0x000000d4 + r14 * 8],129', 'cmpps xmm12,oword [0x000000d4 + r14 * 8],129'),

    ('CVTTPS2PI', '0f2caaaaaaaa41', 'cvttps2pi mm5,oword [rdx + 1101703850]', 'cvttps2pi mm5,oword [rdx + 1101703850]'),
    ('CVTTSS2SI', 'f30f2caaaaaaaa41', 'cvttss2si ebp,dword [rdx + 1101703850]', 'cvttss2si ebp,dword [rdx + 1101703850]'),
    ('CVTTPD2PI', '660f2caaaaaaaa41', 'cvttpd2pi mm5,oword [rdx + 1101703850]', 'cvttpd2pi mm5,oword [rdx + 1101703850]'),
    ('CVTTSD2SI', 'f20f2caaaaaaaa41', 'cvttsd2si ebp,qword [rdx + 1101703850]', 'cvttsd2si ebp,qword [rdx + 1101703850]'),
    ('CVTTSD2SI 2', 'f20f2cc1', 'cvttsd2si eax,xmm1', 'cvttsd2si eax,xmm1'),
    ('CVTTSD2SI 3', 'f2480f2cde', 'cvttsd2si rbx,xmm6', 'cvttsd2si rbx,xmm6'),
    ('CVTTSD2SI 4', 'f2490f2cd9', 'cvttsd2si rbx,xmm9', 'cvttsd2si rbx,xmm9'),
    ('CVTSD2SI', 'f20f2dcb', 'cvtsd2si ecx,xmm3', 'cvtsd2si ecx,xmm3'),
    ('CVTSD2SI 2', 'f24d0f2de1', 'cvtsd2si r12,xmm9', 'cvtsd2si r12,xmm9'),
    ('CVTSD2SI 3', 'f2480f2d142541414141', 'cvtsd2si rdx,qword [0x41414141]', 'cvtsd2si rdx,qword [0x41414141]'),
    ('CVTSD2SI 4', 'f2480f2d09', 'cvtsd2si rcx,qword [rcx]', 'cvtsd2si rcx,qword [rcx]'),
    ('CVTSD2SI 5', 'f2480f2d0cd581000000', 'cvtsd2si rcx,qword [0x00000081 + rdx * 8]', 'cvtsd2si rcx,qword [0x00000081 + rdx * 8]'),
    ('ADDPS', '0f58aa41414141', 'addps xmm5,oword [rdx + 1094795585]', 'addps xmm5,oword [rdx + 1094795585]'),
    ('MOVAPS', '0f28aa41414141', 'movaps xmm5,oword [rdx + 1094795585]', 'movaps xmm5,oword [rdx + 1094795585]'),
    ('MOVAPD', '660f28aa41414141', 'movapd xmm5,oword [rdx + 1094795585]', 'movapd xmm5,oword [rdx + 1094795585]'),
    ('PMULLW (66)', '660faa', 'rsm ', 'rsm '),
    ('CMPXCH8B', '0fc70a', 'cmpxch8b qword [rdx]', 'cmpxch8b qword [rdx]'),
    ('MOVD (66)', '660f7ecb', 'movd ebx,xmm1', 'movd ebx,xmm1'),
    ('MOVD', '66480f7ef8', 'movd rax,xmm7', 'movd rax,xmm7'),  # TODO: REX.W needs to be able to change the opcode name
    ('MOVD', '0F6E0D41414100', 'movd mm1,dword [rip + 4276545]', 'movd mm1,dword [rip + 4276545]'),
    ('MOVQ', '0F6FCB', 'movq mm1,mm3', 'movq mm1,mm3'),
    ('PSRAW',  '0FE1CA', 'psraw mm1,mm2', 'psraw mm1,mm2'),
    ('PSRLQ (66)',  '660FF3CB', 'psllq xmm1,xmm3', 'psllq xmm1,xmm3'),
    ('PALIGNR', '0F3A0FDC03', 'palignr xmm3,xmm4,3', 'palignr xmm3,xmm4,3'),
    ('PALIGNR (66)',  '660F3A0FCA07', 'palignr xmm1,xmm2,7', 'palignr xmm1,xmm2,7'),
    ('PSLLQ (reg)',  '660FF3CA', 'psllq xmm1,xmm2', 'psllq xmm1,xmm2'),
    ('PSLLW (regs)',  '0F71F108', 'psllw mm1,8', 'psllw mm1,8'),
    ('PSLLQ (66)',  '660F73F108', 'psllq xmm1,8', 'psllq xmm1,8'),
    ('RDTSC', '0F31', 'rdtsc ', 'rdtsc '),
    ('RDTSCP', '0F01F9', 'rdtscp ', 'rdtscp '),

    ('PSRLW (66)', '660fd1ce', 'psrlw xmm1,xmm6', 'psrlw xmm1,xmm6'),
    ('PSRLW (66) 2', '660F71D611', 'psrlw xmm6,17', 'psrlw xmm6,17'),
    ('PSRLW (66) 3', '660FD10C253A3A3A3A', 'psrlw xmm1,oword [0x3a3a3a3a]', 'psrlw xmm1,oword [0x3a3a3a3a]'),
    ('PSRAD (66)', '660F72E704', 'psrad xmm7,4', 'psrad xmm7,4'),
    ('PSHUFB', '660F3800EF', 'pshufb xmm5,xmm7', 'pshufb xmm5,xmm7'),
    ('MOVBE', '0F38F0042541414141', 'movbe eax,dword [0x41414141]', 'movbe eax,dword [0x41414141]'),
    ('MOVBE 2', '0F38F10C2541414141', 'movbe dword [0x41414141],ecx', 'movbe dword [0x41414141],ecx'),
    ('PABSB', '0F381CCD', 'pabsb mm1,mm5', 'pabsb mm1,mm5'),
    ('PABSB 2', '0F381C2C2541414141', 'pabsb mm5,qword [0x41414141]', 'pabsb mm5,qword [0x41414141]'),
    ('PABSB 3', '660F381CD4', 'pabsb xmm2,xmm4', 'pabsb xmm2,xmm4'),
    ('PABSB 4', '660F381C1C2541414141', 'pabsb xmm3,oword [0x41414141]', 'pabsb xmm3,oword [0x41414141]'),
    ('POPCNT', '66f30fb8c3', 'popcnt ax,bx', 'popcnt ax,bx'),

    ('PSRLQ (66)',  '660F73D308', 'psrlq xmm3,8', 'psrlq xmm3,8'),
    ('PSRLQ 2',  '660f73d501', 'psrlq xmm5,1', 'psrlq xmm5,1'),
    ('PSRLQ', '660FD3DC', 'psrlq xmm3,xmm4', 'psrlq xmm3,xmm4'),
    ('PSRLQ', '660F73d10f', 'psrlq xmm1,15', 'psrlq xmm1,15'),
    ('PSRLDQ (66)', '660f73d808', 'psrldq xmm0,8', 'psrldq xmm0,8'),
    ('PSRLDQ (66)', '660f73f5aa', 'psllq xmm5,170', 'psllq xmm5,170'),
    ('PSRLDQ (66)', '660f73b9aa', 'pslldq xmm1,170', 'pslldq xmm1,170'),
    ('PCMPISTRI', '660f3a630f0d', 'pcmpistri xmm1,oword [rdi],13', 'pcmpistri xmm1,oword [rdi],13'),

    ('POPCNT', 'f30fb8c4', 'popcnt eax,esp', 'popcnt eax,esp'),
    ('POPCNT 2', 'f3480fb8c4', 'popcnt rax,rsp', 'popcnt rax,rsp'),
    ('POPCNT 3', 'f30fb80541414100', 'popcnt eax,dword [rip + 4276545]', 'popcnt eax,dword [rip + 4276545]'),
    ('LZCNT', 'f30fbdc4', 'lzcnt eax,esp', 'lzcnt eax,esp'),
    ('LZCNT 2', 'f30fbd0541414100', 'lzcnt eax,dword [rip + 4276545]', 'lzcnt eax,dword [rip + 4276545]'),
    ('LZCNT 3', 'f3480fbdc1', 'lzcnt rax,rcx', 'lzcnt rax,rcx'),

    ('MOVDQU', 'F30F6FCA', 'movdqu xmm1,xmm2', 'movdqu xmm1,xmm2'),
    ('MOVDQU (MEM)', 'F30F6F4810', 'movdqu xmm1,oword [rax + 16]', 'movdqu xmm1,oword [rax + 16]'),
    ('MOVDQU (REP)', 'F3F30F6FCA', 'movdqu xmm1,xmm2', 'movdqu xmm1,xmm2'),
    ('MOVSD', 'f20f100d28330608', 'movsd xmm1,qword [rip + 134624040]', 'movsd xmm1,qword [rip + 134624040]'),
    ('MOVSD 2', 'f20f1145f0', 'movsd qword [rbp - 16],xmm0', 'movsd qword [rbp - 16],xmm0'),
    ('MOVSD 3', 'f20f100d70790908', 'movsd xmm1,qword [rip + 134838640]', 'movsd xmm1,qword [rip + 134838640]'),
    ('MOVSS', 'f30f1045f8', 'movss xmm0,dword [rbp - 8]', 'movss xmm0,dword [rbp - 8]'),
    ('MOVSS 2', 'f30f1055d0', 'movss xmm2,dword [rbp - 48]', 'movss xmm2,dword [rbp - 48]'),
    ('MOVSS 3', 'F30F110D41414100', 'movss dword [rip + 4276545],xmm1', 'movss dword [rip + 4276545],xmm1'),
    ('CVTSI2SS', 'f30f2ac8', 'cvtsi2ss xmm1,eax', 'cvtsi2ss xmm1,eax'),
    ('MULSS', 'f30f59ca', 'mulss xmm1,xmm2', 'mulss xmm1,xmm2'),
    ('SUBSS', 'f30f5cc1', 'subss xmm0,xmm1', 'subss xmm0,xmm1'),
    ('CVTSS2SD', 'f30f5ac0', 'cvtss2sd xmm0,xmm0', 'cvtss2sd xmm0,xmm0'),
    ('SQRTSS', 'f30f51d9', 'sqrtss xmm3,xmm1', 'sqrtss xmm3,xmm1'),
    ('VMXON', 'f30fc73541414100', 'vmxon qword [rip + 4276545]', 'vmxon qword [rip + 4276545]'),
    ('VMPTRST', '0FC73C2541414141', 'vmptrst qword [0x41414141]', 'vmptrst qword [0x41414141]'),
    ('VMREAD', '0F78D8', 'vmread rax,rbx', 'vmread rax,rbx'),  # XXX: This will change on 32bit
    ('VMREAD 2', '0F781C2541414141', 'vmread qword [0x41414141],rbx', 'vmread qword [0x41414141],rbx'),
    ('VMWRITE', '0F79CB', 'vmwrite rcx,rbx', 'vmwrite rcx,rbx'),
    ('VMWRITE 2', '0F790C2541414141', 'vmwrite rcx,qword [0x41414141]', 'vmwrite rcx,qword [0x41414141]'),
    ('VMXOFF', '0F01C4', 'vmxoff ', 'vmxoff '),
    ('VMRESUME', '0F01C3', 'vmresume ', 'vmresume '),
    ('VMLAUNCH', '0F01C2', 'vmlaunch ', 'vmlaunch '),
    ('VMFUNC', '0F01D4', 'vmfunc ', 'vmfunc '),  # XXX: Implies eax
    ('VMCALL', '0F01C1', 'vmcall ', 'vmcall '),
    ('VMCLEAR', '660FC7342541414141', 'vmclear qword [0x41414141]', 'vmclear qword [0x41414141]'),
    ('INVVPID', '660F3881042541414141', 'invvpid rax,oword [0x41414141]', 'invvpid rax,oword [0x41414141]'),
    ('INVEPT', '660F3880142541414141', 'invept rdx,oword [0x41414141]', 'invept rdx,oword [0x41414141]'),
    ('MULSD', 'f20f59c1', 'mulsd xmm0,xmm1', 'mulsd xmm0,xmm1'),
    ('VMCLEAR', '660FC73541414100', 'vmclear qword [rip + 4276545]', 'vmclear qword [rip + 4276545]'),
    ('MOVBE',   '0F38F04910', 'movbe ecx,dword [rcx + 16]', 'movbe ecx,dword [rcx + 16]'),
    ('MOVBE 2', '0F38F009', 'movbe ecx,dword [rcx]', 'movbe ecx,dword [rcx]'),
    ('MOVBE 3', '0F38F00C8D41414141', 'movbe ecx,dword [0x41414141 + rcx * 4]', 'movbe ecx,dword [0x41414141 + rcx * 4]'),
    ('MOVBE 4', '0F38F15110', 'movbe dword [rcx + 16],edx', 'movbe dword [rcx + 16],edx'),
    ('MOVBE 5', '0F38F102', 'movbe dword [rdx],eax', 'movbe dword [rdx],eax'),
    ('MOVBE 6', '0F38F10541414141', 'movbe dword [rip + 1094795585],eax', 'movbe dword [rip + 1094795585],eax'),
    # TODO: need to make sure 66 <REX> stuff works
    ('CRC 1', 'f20f38f0e8', 'crc32 ebp,al', 'crc32 ebp,al'),
    ('CRC 2', '66f20f38f1C3', 'crc32 eax,bx', 'crc32 eax,bx'),
    ('CRC 3', 'f20f38f1C3', 'crc32 eax,ebx', 'crc32 eax,ebx'),
    ('CLAC', '0f01ca', 'clac ', 'clac '),
    ('STAC', '0f01cb', 'stac ', 'stac '),
    ('VMFUNC', '0f01d4', 'vmfunc ', 'vmfunc '),
    ('XEND', '0f01d5', 'xend ', 'xend '),
    ('XGETBV', '0f01d0', 'xgetbv ecx', 'xgetbv ecx'),
    ('XSETBV', '0f01d1', 'xsetbv ecx', 'xsetbv ecx'),
    ('XTEST', '0f01d6', 'xtest ', 'xtest '),
    ('MOVUPD', '660f10cc', 'movupd xmm1,xmm4', 'movupd xmm1,xmm4'),
    ('MOVUPD', '660f1018', 'movupd xmm3,oword [rax]', 'movupd xmm3,oword [rax]'),
    ('UNPCKLPD', '660F14A241414100', 'unpcklpd xmm4,oword [rdx + 4276545]', 'unpcklpd xmm4,oword [rdx + 4276545]'),
    ('UNPCKLPD 2', '66410f14cd', 'unpcklpd xmm1,xmm13', 'unpcklpd xmm1,xmm13'),
    ('UNPCKHPD', '660F15CA', 'unpckhpd xmm1,xmm2', 'unpckhpd xmm1,xmm2'),
    ('UNPCKHPD 2', '66410f15cd', 'unpckhpd xmm1,xmm13', 'unpckhpd xmm1,xmm13'),
    ('MOVHPD', '660F162541414141', 'movhpd xmm4,qword [rip + 1094795585]', 'movhpd xmm4,qword [rip + 1094795585]'),
    ('MOVHPD 2', '660F172D41414141', 'movhpd qword [rip + 1094795585],xmm5', 'movhpd qword [rip + 1094795585],xmm5'),
    ('MOVMSKPS', '0F50D6', 'movmskps edx,xmm6', 'movmskps edx,xmm6'),
    ('MOVMSKPD', '660F50D6', 'movmskpd edx,xmm6', 'movmskpd edx,xmm6'),
    ('MOVMSKPD 2', '66490f50c5', 'movmskpd rax,xmm13', 'movmskpd rax,xmm13'),
    ('MOVMSKPD 3', '66410f50c5',  'movmskpd eax,xmm13', 'movmskpd eax,xmm13'),
    ('MOVMSKPD 4', '66410f50c5',  'movmskpd eax,xmm13', 'movmskpd eax,xmm13'),
    ('MOVHLPS', '0F12DF', 'movlps xmm3,xmm7', 'movlps xmm3,xmm7'),
    ('SUBPD', '660F5C6C240E', 'subpd xmm5,oword [rsp + 14]', 'subpd xmm5,oword [rsp + 14]'),
    ('MAXPD', '660F5FAB0F270000', 'maxpd xmm5,oword [rbx + 9999]', 'maxpd xmm5,oword [rbx + 9999]'),
    ('XORPD', '660F57BD15CD5B07', 'xorpd xmm7,oword [rbp + 123456789]', 'xorpd xmm7,oword [rbp + 123456789]'),
    ('SQRTPD', '660f51ca', 'sqrtpd xmm1,xmm2', 'sqrtpd xmm1,xmm2'),
    ('PSHUFD', '660F70CD11', 'pshufd xmm1,xmm5,17', 'pshufd xmm1,xmm5,17'),
    ('PEXTRW', '660FC5C307', 'pextrw rax,xmm3,7', 'pextrw rax,xmm3,7'),
    ('MOVQ', '660FD620', 'movq qword [rax],xmm4', 'movq qword [rax],xmm4'),
    ('MOVQ', 'f3410f7ed8', 'movd_q xmm3,xmm8', 'movd_q xmm3,xmm8'),
    ('PMAXUB', '660FDE2541414141', 'pmaxub xmm4,oword [rip + 1094795585]', 'pmaxub xmm4,oword [rip + 1094795585]'),
    ('MOVNTDQ', '660FE73D78563412', 'movntdq oword [rip + 305419896],xmm7', 'movntdq oword [rip + 305419896],xmm7'),
    ('PADDD', '660FFECE', 'paddd xmm1,xmm6', 'paddd xmm1,xmm6'),
    ('HADDPS', 'F20F7CCE', 'haddps xmm1,xmm6', 'haddps xmm1,xmm6'),
    ('LDDQU', 'F20FF01C2541414141', 'lddqu xmm3,oword [0x41414141]', 'lddqu xmm3,oword [0x41414141]'),

    ('BSF', '480FBCC2', 'bsf rax,rdx', 'bsf rax,rdx'),
    ('BSF 2', '0FBC042541414141', 'bsf eax,dword [0x41414141]', 'bsf eax,dword [0x41414141]'),
    # AES-NI feature set
    ('AESENC', '660F38DCEA', 'aesenc xmm5,xmm2', 'aesenc xmm5,xmm2'),
    ('AESENC (MEM)', '660f38DC3A', 'aesenc xmm7,oword [rdx]', 'aesenc xmm7,oword [rdx]'),
    ('AESENC (MEM 2)', '660f38DC7C2404', 'aesenc xmm7,oword [rsp + 4]', 'aesenc xmm7,oword [rsp + 4]'),
    ('AESENC (MEM 3)', '660F38DC1D41414141', 'aesenc xmm3,oword [rip + 1094795585]', 'aesenc xmm3,oword [rip + 1094795585]'),
    ('AESENCLAST', '660F38DDDC', 'aesenclast xmm3,xmm4', 'aesenclast xmm3,xmm4'),
    ('AESENCLAST (MEM)', '660F38DD18', 'aesenclast xmm3,oword [rax]', 'aesenclast xmm3,oword [rax]'),
    ('AESENCLAST (MEM 2)', '660F38DD5808', 'aesenclast xmm3,oword [rax + 8]', 'aesenclast xmm3,oword [rax + 8]'),
    ('AESENCLAST (MEM 3)', '660F38DD2578563442', 'aesenclast xmm4,oword [rip + 1110726264]', 'aesenclast xmm4,oword [rip + 1110726264]'),
    ('AESDEC', '660f38DECB', 'aesdec xmm1,xmm3', 'aesdec xmm1,xmm3'),
    ('AESDEC (MEM)', '660F38DE0C24', 'aesdec xmm1,oword [rsp]', 'aesdec xmm1,oword [rsp]'),
    ('AESDEC (MEM 2)', '660F38DE5D0C', 'aesdec xmm3,oword [rbp + 12]', 'aesdec xmm3,oword [rbp + 12]'),
    ('AESDEC (MEM 3)', '660F38DE3544434241', 'aesdec xmm6,oword [rip + 1094861636]', 'aesdec xmm6,oword [rip + 1094861636]'),
    ('AESDECLAST', '660F38DFED', 'aesdeclast xmm5,xmm5', 'aesdeclast xmm5,xmm5'),
    ('AESDECLAST (MEM)', '660F38DF2E', 'aesdeclast xmm5,oword [rsi]', 'aesdeclast xmm5,oword [rsi]'),
    ('AESDECLAST (MEM 2)', '660F38DF6740', 'aesdeclast xmm4,oword [rdi + 64]', 'aesdeclast xmm4,oword [rdi + 64]'),
    ('AESDECLAST (MEM 3)', '660F38DF2511213141', 'aesdeclast xmm4,oword [rip + 1093738769]', 'aesdeclast xmm4,oword [rip + 1093738769]'),
    ('AESIMC', '660F38DBF9', 'aesimc xmm7,xmm1', 'aesimc xmm7,xmm1'),
    ('AESIMC (MEM)', '660F38DB13', 'aesimc xmm2,oword [rbx]', 'aesimc xmm2,oword [rbx]'),
    ('AESIMC (MEM 2)', '660F38DB5020', 'aesimc xmm2,oword [rax + 32]', 'aesimc xmm2,oword [rax + 32]'),
    ('AESIMC (MEM 3)', '660F38DB1D00000041', 'aesimc xmm3,oword [rip + 1090519040]', 'aesimc xmm3,oword [rip + 1090519040]'),
    ('AESKEYGENASSIST', '660F3ADFFE08', 'aeskeygenassist xmm7,xmm6,8', 'aeskeygenassist xmm7,xmm6,8'),
    ('AESKEYGENASSIST (MEM)', '660F3ADF1AFE', 'aeskeygenassist xmm3,oword [rdx],254', 'aeskeygenassist xmm3,oword [rdx],254'),
    ('AESKEYGENASSIST (MEM 2)', '660F3ADF998000000039', 'aeskeygenassist xmm3,oword [rcx + 128],57', 'aeskeygenassist xmm3,oword [rcx + 128],57'),
    ('AESKEYGENASSIST (MEM 3)', '660F3ADF2541414141C6', 'aeskeygenassist xmm4,oword [rip + 1094795585],198', 'aeskeygenassist xmm4,oword [rip + 1094795585],198'),
    ('PCLMULQDQ', '660F3A44D307', 'pclmulqdq xmm2,xmm3,7', 'pclmulqdq xmm2,xmm3,7'),
    ('PCLMULQDQ (MEM)', '660F3A441007', 'pclmulqdq xmm2,oword [rax],7', 'pclmulqdq xmm2,oword [rax],7'),
    ('PCLMULQDQ (MEM 2)', '660F3A4478119C', 'pclmulqdq xmm7,oword [rax + 17],156', 'pclmulqdq xmm7,oword [rax + 17],156'),
    ('PCLMULQDQ (MEM 3)', '660F3A443D41414141C6', 'pclmulqdq xmm7,oword [rip + 1094795585],198', 'pclmulqdq xmm7,oword [rip + 1094795585],198'),
    ('BLENDPD', '660F3A0DCA2F', 'blendpd xmm1,xmm2,47', 'blendpd xmm1,xmm2,47'),
    ('BLENDPS', '660F3A0C0C25414141415D', 'blendps xmm1,oword [0x41414141],93', 'blendps xmm1,oword [0x41414141],93'),
    ('BLENDVPS', '660F38140C2541414141', 'blendvps xmm1,oword [0x41414141]', 'blendvps xmm1,oword [0x41414141]'),
    ('BLENDVPS', '660F3814DC', 'blendvps xmm3,xmm4', 'blendvps xmm3,xmm4'),
    ('BLENDVPD', '660F38150C2541414141', 'blendvpd xmm1,oword [0x41414141]', 'blendvpd xmm1,oword [0x41414141]'),
    ('BLENDVPD', '660F3815DC', 'blendvpd xmm3,xmm4', 'blendvpd xmm3,xmm4'),
    ('PEXTRB', '660F3A14D011', 'pextrb eax,xmm2,17', 'pextrb eax,xmm2,17'),
    ('PEXTRB 2', '660F3A141011', 'pextrb byte [rax],xmm2,17', 'pextrb byte [rax],xmm2,17'),
    ('PEXTRB 3', '660F3A14500411', 'pextrb byte [rax + 4],xmm2,17', 'pextrb byte [rax + 4],xmm2,17'),
    # Uck. We need to let the REX bytes modify the opcode name
    ('PEXTRD', '660F3A16EA11', 'pextrd_q edx,xmm5,17', 'pextrd_q edx,xmm5,17'),
    ('PEXTRD 2', '660F3A161011', 'pextrd_q dword [rax],xmm2,17', 'pextrd_q dword [rax],xmm2,17'),
    ('PEXTRQ', '66480F3A16D9FE', 'pextrd_q rcx,xmm3,254', 'pextrd_q rcx,xmm3,254'),
    ('PEXTRQ 2', '66480F3A16A14141414175', 'pextrd_q qword [rcx + 1094795585],xmm4,117', 'pextrd_q qword [rcx + 1094795585],xmm4,117'),
    ('TEST', 'F70078563412', 'test dword [rax],0x12345678', 'test dword [rax],0x12345678'),
    ('MOVSLDUP', 'f30f12ca', 'movsldup xmm1,xmm2', 'movsldup xmm1,xmm2'),
    ('MOVSLDUP 2', 'f30f123c2541414141', 'movsldup xmm7,oword [0x41414141]', 'movsldup xmm7,oword [0x41414141]'),
    ('CVTSI2SS', 'f3440f2ac0', 'cvtsi2ss xmm8,eax', 'cvtsi2ss xmm8,eax'),
    ('CVTSI2SS 2', 'f3440f2a02', 'cvtsi2ss xmm8,dword [rdx]', 'cvtsi2ss xmm8,dword [rdx]'),

    ('CVTTSS2SI', 'f30f2c042541414141', 'cvttss2si eax,dword [0x41414141]', 'cvttss2si eax,dword [0x41414141]'),
    ('CVTTSS2SI 2', 'f3480f2cc3', 'cvttss2si rax,xmm3', 'cvttss2si rax,xmm3'),
    ('CVTTSS2SI 3', 'f3480f2c00', 'cvttss2si rax,dword [rax]', 'cvttss2si rax,dword [rax]'),
    ('CVTSS2SI', 'f30f2dc9', 'cvtss2si ecx,xmm1', 'cvtss2si ecx,xmm1'),
    ('CVTSS2SI 2', 'f3480f2dd2', 'cvtss2si rdx,xmm2', 'cvtss2si rdx,xmm2'),
    ('CVTSS2SI 3', 'f3480f2d10', 'cvtss2si rdx,dword [rax]', 'cvtss2si rdx,dword [rax]'),
    ('CVTSS2SI 4', 'f30f2d4212', 'cvtss2si eax,dword [rdx + 18]', 'cvtss2si eax,dword [rdx + 18]'),
    ('SQRTSS', 'f30f51d7', 'sqrtss xmm2,xmm7', 'sqrtss xmm2,xmm7'),
    ('SQRTSS 2', 'f30f511c2541414141', 'sqrtss xmm3,dword [0x41414141]', 'sqrtss xmm3,dword [0x41414141]'),
    ('SQRTSS 3', 'f30f511cd540000000', 'sqrtss xmm3,dword [0x00000040 + rdx * 8]', 'sqrtss xmm3,dword [0x00000040 + rdx * 8]'),
    ('RSQRTSS', 'f30f52d7', 'rsqrtss xmm2,xmm7', 'rsqrtss xmm2,xmm7'),
    ('RSQRTSS 2', 'f30f521c2541414141', 'rsqrtss xmm3,dword [0x41414141]', 'rsqrtss xmm3,dword [0x41414141]'),
    ('RSQRTSS 3', 'f30f521cd540000000', 'rsqrtss xmm3,dword [0x00000040 + rdx * 8]', 'rsqrtss xmm3,dword [0x00000040 + rdx * 8]'),
    ('RCPSS', 'f3440f53cf', 'rcpss xmm9,xmm7', 'rcpss xmm9,xmm7'),
    ('RCPSS 2', 'f3440f5319', 'rcpss xmm11,dword [rcx]', 'rcpss xmm11,dword [rcx]'),

    ('PINSRB', '660f3a20c811', 'pinsrb xmm1,eax,17', 'pinsrb xmm1,eax,17'),
    ('PINSRB 2', '660f3a200811', 'pinsrb xmm1,byte [rax],17', 'pinsrb xmm1,byte [rax],17'),
    ('PINSRD', '660f3a22c811', 'pinsrd xmm1,eax,17', 'pinsrd xmm1,eax,17'),
    ('PINSRD 2', '660f3a220811', 'pinsrd xmm1,dword [rax],17', 'pinsrd xmm1,dword [rax],17'),
    ('ADDSS', 'f30f58ca', 'addss xmm1,xmm2', 'addss xmm1,xmm2'),
    ('ADDSS 2', 'f30f580a', 'addss xmm1,dword [rdx]', 'addss xmm1,dword [rdx]'),
    ('ADDSS 3', 'f30f585963', 'addss xmm3,dword [rcx + 99]', 'addss xmm3,dword [rcx + 99]'),
    ('ROUNDSS',   '660f3a0adca7', 'roundss xmm3,xmm4,167', 'roundss xmm3,xmm4,167'),
    ('ROUNDSS 2', '660f3a0a1080', 'roundss xmm2,dword [rax],128', 'roundss xmm2,dword [rax],128'),
    ('ROUNDSS 3', '660f3a0a148dff000000ff', 'roundss xmm2,dword [0x000000ff + rcx * 4],255', 'roundss xmm2,dword [0x000000ff + rcx * 4],255'),
    ('CVTPD2PI (NOREX)', '660f2df8', 'cvtpd2pi mm7,xmm0', 'cvtpd2pi mm7,xmm0'),
    # So the only part of REX that should matter for these is: REX.B
    # So anything with the least significant bit set
    ('CVTPD2PI (REX 41)', '66410f2df8', 'cvtpd2pi mm7,xmm8', 'cvtpd2pi mm7,xmm8'),
    ('CVTPD2PI (REX 43)', '66430f2df8', 'cvtpd2pi mm7,xmm8', 'cvtpd2pi mm7,xmm8'),
    ('CVTPD2PI (REX 45)', '66450f2df8', 'cvtpd2pi mm7,xmm8', 'cvtpd2pi mm7,xmm8'),
    ('CVTPD2PI (REX 47)', '66470f2df8', 'cvtpd2pi mm7,xmm8', 'cvtpd2pi mm7,xmm8'),
    ('CVTPD2PI (REX 49)', '66490f2df8', 'cvtpd2pi mm7,xmm8', 'cvtpd2pi mm7,xmm8'),
    ('CVTPD2PI (REX 4b)', '664b0f2df8', 'cvtpd2pi mm7,xmm8', 'cvtpd2pi mm7,xmm8'),
    ('CVTPD2PI (REX 4d)', '664d0f2df8', 'cvtpd2pi mm7,xmm8', 'cvtpd2pi mm7,xmm8'),
    ('CVTPD2PI (REX 4f)', '664f0f2df8', 'cvtpd2pi mm7,xmm8', 'cvtpd2pi mm7,xmm8'),

    ('CVTPD2PI (REX 42)', '66420f2df8', 'cvtpd2pi mm7,xmm0', 'cvtpd2pi mm7,xmm0'),
    ('CVTPD2PI (REX 44)', '66440f2df8', 'cvtpd2pi mm7,xmm0', 'cvtpd2pi mm7,xmm0'),
    ('CVTPD2PI (REX 46)', '66460f2df8', 'cvtpd2pi mm7,xmm0', 'cvtpd2pi mm7,xmm0'),
    ('CVTPD2PI (REX 48)', '66480f2df8', 'cvtpd2pi mm7,xmm0', 'cvtpd2pi mm7,xmm0'),
    ('CVTPD2PI (REX 4a)', '664a0f2df8', 'cvtpd2pi mm7,xmm0', 'cvtpd2pi mm7,xmm0'),
    ('CVTPD2PI (REX 4c)', '664c0f2df8', 'cvtpd2pi mm7,xmm0', 'cvtpd2pi mm7,xmm0'),
    ('CVTPD2PI (REX 4e)', '664e0f2df8', 'cvtpd2pi mm7,xmm0', 'cvtpd2pi mm7,xmm0'),
    ('CVTPD2PI 2 (REX)', '66410f2d38', 'cvtpd2pi mm7,oword [r8]', 'cvtpd2pi mm7,oword [r8]'),
    ('CVTPD2PI 2 (NOREX)', '660f2d38', 'cvtpd2pi mm7,oword [rax]', 'cvtpd2pi mm7,oword [rax]'),
    ('CVTPD2PI 3', '660f2d3c2541414141', 'cvtpd2pi mm7,oword [0x41414141]', 'cvtpd2pi mm7,oword [0x41414141]'),
    ('CVTPD2PI 4', '660f2d3c8561000000', 'cvtpd2pi mm7,oword [0x00000061 + rax * 4]', 'cvtpd2pi mm7,oword [0x00000061 + rax * 4]'),
    ('SQRTSD', 'f20f51cc', 'sqrtsd xmm1,xmm4', 'sqrtsd xmm1,xmm4'),
    ('SQRTSD 2', 'f20f5110', 'sqrtsd xmm2,qword [rax]', 'sqrtsd xmm2,qword [rax]'),
    ('SQRTSD 3', 'f2440f511cd530000000', 'sqrtsd xmm11,qword [0x00000030 + rdx * 8]', 'sqrtsd xmm11,qword [0x00000030 + rdx * 8]'),
    ('MULSD', 'f20f59dc', 'mulsd xmm3,xmm4', 'mulsd xmm3,xmm4'),
    ('MULSD 2', 'f2440f5920', 'mulsd xmm12,qword [rax]', 'mulsd xmm12,qword [rax]'),
    ('MULSD 3', 'f2410f594c2420', 'mulsd xmm1,qword [r12 + 32]', 'mulsd xmm1,qword [r12 + 32]'),
    ('LDDQU', 'f2440ff0142541414141', 'lddqu xmm10,oword [0x41414141]', 'lddqu xmm10,oword [0x41414141]'),
    ('LDDQU 1', 'f20ff0348531000000', 'lddqu xmm6,oword [0x00000031 + rax * 4]', 'lddqu xmm6,oword [0x00000031 + rax * 4]'),
    ('MOVDQ2Q', 'f20fd6d9', 'movdq2q mm3,xmm1', 'movdq2q mm3,xmm1'),
    ('RDRAND', '0fc7f0', 'rdrand eax', 'rdrand eax'),
    ('RDSEED', '0fc7f8', 'rdseed eax', 'rdseed eax'),
    ('VMPTRST', '0fc73d41414141', 'vmptrst qword [rip + 1094795585]', 'vmptrst qword [rip + 1094795585]'),
    ('VMCLEAR', '0fc73541414141', 'vmptrld qword [rip + 1094795585]', 'vmptrld qword [rip + 1094795585]'),
    ('CMPXCHG', '0fb0d0', 'cmpxchg al,dl', 'cmpxchg al,dl'),
    ('PMOVMSKB', '660fd7f8', 'pmovmskb edi,xmm0', 'pmovmskb edi,xmm0'),
    ('PMOVMSBK 2', '660fd7ca', 'pmovmskb ecx,xmm2', 'pmovmskb ecx,xmm2'),
    ('PMOVMSKB 3', '0fd7f8', 'pmovmskb edi,mm0', 'pmovmskb edi,mm0'),
    # XXX: Here's a fun tidbit. In the intel docs for this instruction, it says to use REX.B
    # to index into the higher
    # xmm{8,15} registers. But the only xmm register in this are specifcally indexed by the
    # r/m portion of the ModRM byte.
    ('MOVDQ2Q 2', 'f2410fd6db', 'movdq2q mm3,xmm11', 'movdq2q mm3,xmm11'),
    ('MOVDQ2Q 2', 'f2410fd6fc', 'movdq2q mm7,xmm12', 'movdq2q mm7,xmm12'),
    ('ADDSUBPS', 'f20fd0d3', 'addsubps xmm2,xmm3', 'addsubps xmm2,xmm3'),
    ('ADDSUBPS 2', 'f2450fd0d3', 'addsubps xmm10,xmm11', 'addsubps xmm10,xmm11'),
    ('ADDSUBPS 3', 'f2440fd009', 'addsubps xmm9,oword [rcx]', 'addsubps xmm9,oword [rcx]'),
    ('PSHUFLW', 'f2410f70ca13', 'pshuflw xmm1,xmm10,19', 'pshuflw xmm1,xmm10,19'),
    ('PSHUFLW 2', 'f20f708b282300001b', 'pshuflw xmm1,oword [rbx + 9000],27', 'pshuflw xmm1,oword [rbx + 9000],27'),
    ('CVTPD2DQ', 'f2410fe6d1', 'cvtpd2dq xmm2,xmm9', 'cvtpd2dq xmm2,xmm9'),
    ('CVTPD2DQ 2', 'f2440fe6791d', 'cvtpd2dq xmm15,oword [rcx + 29]', 'cvtpd2dq xmm15,oword [rcx + 29]'),
    ('CVTPD2DQ 3', 'f2440fe6342541414141', 'cvtpd2dq xmm14,oword [0x41414141]', 'cvtpd2dq xmm14,oword [0x41414141]'),
    ('MOVNTPD', '66410f2b12', 'movntpd oword [r10],xmm2', 'movntpd oword [r10],xmm2'),
    ('COMISD', '66410f2fe7', 'comisd xmm4,xmm15', 'comisd xmm4,xmm15'),
    ('UCOMISD', '660f2ef9', 'ucomisd xmm7,xmm1', 'ucomisd xmm7,xmm1'),

    ('ANDPD 0', '66440f54342541414141', 'andpd xmm14,oword [0x41414141]', 'andpd xmm14,oword [0x41414141]'),
    ('ANDPD 1', '66450f5432', 'andpd xmm14,oword [r10]', 'andpd xmm14,oword [r10]'),
    ('ANDPD 2', '66450f5474244b', 'andpd xmm14,oword [r12 + 75]', 'andpd xmm14,oword [r12 + 75]'),
    ('ANDPD 3', '66460f5434fd4b000000', 'andpd xmm14,oword [0x0000004b + r15 * 8]', 'andpd xmm14,oword [0x0000004b + r15 * 8]'),
    ('ANDPD 4', '66450f54f7', 'andpd xmm14,xmm15', 'andpd xmm14,xmm15'),
    ('ANDNPD 0', '660f55142541414141', 'andnpd xmm2,oword [0x41414141]', 'andnpd xmm2,oword [0x41414141]'),
    ('ANDNPD 1', '66410f555500', 'andnpd xmm2,oword [r13]', 'andnpd xmm2,oword [r13]'),
    ('ANDNPD 2', '66410f55515a', 'andnpd xmm2,oword [r9 + 90]', 'andnpd xmm2,oword [r9 + 90]'),
    ('ANDNPD 3', '660f5514d55a000000', 'andnpd xmm2,oword [0x0000005a + rdx * 8]', 'andnpd xmm2,oword [0x0000005a + rdx * 8]'),
    ('ANDNPD 4', '660f55d4', 'andnpd xmm2,xmm4', 'andnpd xmm2,xmm4'),

    ('ADDPD 0', '660f580c2541414141', 'addpd xmm1,oword [0x41414141]', 'addpd xmm1,oword [0x41414141]'),
    ('ADDPD 1', '66410f5808', 'addpd xmm1,oword [r8]', 'addpd xmm1,oword [r8]'),
    ('ADDPD 2', '66410f584c241b', 'addpd xmm1,oword [r12 + 27]', 'addpd xmm1,oword [r12 + 27]'),
    ('ADDPD 3', '66420f580cdd1b000000', 'addpd xmm1,oword [0x0000001b + r11 * 8]', 'addpd xmm1,oword [0x0000001b + r11 * 8]'),
    ('ADDPD 4', '66410f58cb', 'addpd xmm1,xmm11', 'addpd xmm1,xmm11'),
    ('ORPD 0', '660f560c2541414141', 'orpd xmm1,oword [0x41414141]', 'orpd xmm1,oword [0x41414141]'),
    ('ORPD 1', '660f560b', 'orpd xmm1,oword [rbx]', 'orpd xmm1,oword [rbx]'),
    ('ORPD 2', '66410f568ec4000000', 'orpd xmm1,oword [r14 + 196]', 'orpd xmm1,oword [r14 + 196]'),
    ('ORPD 3', '660f560ccdc4000000', 'orpd xmm1,oword [0x000000c4 + rcx * 8]', 'orpd xmm1,oword [0x000000c4 + rcx * 8]'),
    ('ORPD 4', '66410f56cb', 'orpd xmm1,xmm11', 'orpd xmm1,xmm11'),
    ('XORPD 0', '66440f57142541414141', 'xorpd xmm10,oword [0x41414141]', 'xorpd xmm10,oword [0x41414141]'),
    ('XORPD 1', '66450f575500', 'xorpd xmm10,oword [r13]', 'xorpd xmm10,oword [r13]'),
    ('XORPD 2', '66440f5793de000000', 'xorpd xmm10,oword [rbx + 222]', 'xorpd xmm10,oword [rbx + 222]'),
    ('XORPD 3', '66460f5714fdde000000', 'xorpd xmm10,oword [0x000000de + r15 * 8]', 'xorpd xmm10,oword [0x000000de + r15 * 8]'),
    ('XORPD 4', '66440f57d7', 'xorpd xmm10,xmm7', 'xorpd xmm10,xmm7'),
    ('MULPD 0', '660f592c2541414141', 'mulpd xmm5,oword [0x41414141]', 'mulpd xmm5,oword [0x41414141]'),
    ('MULPD 1', '66410f592c24', 'mulpd xmm5,oword [r12]', 'mulpd xmm5,oword [r12]'),
    ('MULPD 2', '66410f596c2445', 'mulpd xmm5,oword [r12 + 69]', 'mulpd xmm5,oword [r12 + 69]'),
    ('MULPD 3', '660f592cdd45000000', 'mulpd xmm5,oword [0x00000045 + rbx * 8]', 'mulpd xmm5,oword [0x00000045 + rbx * 8]'),
    ('MULPD 4', '660f59eb', 'mulpd xmm5,xmm3', 'mulpd xmm5,xmm3'),
    ('SUBPD 0', '660f5c142541414141', 'subpd xmm2,oword [0x41414141]', 'subpd xmm2,oword [0x41414141]'),
    ('SUBPD 1', '66410f5c1424', 'subpd xmm2,oword [r12]', 'subpd xmm2,oword [r12]'),
    ('SUBPD 2', '66410f5c5648', 'subpd xmm2,oword [r14 + 72]', 'subpd xmm2,oword [r14 + 72]'),
    ('SUBPD 3', '66420f5c14c548000000', 'subpd xmm2,oword [0x00000048 + r8 * 8]', 'subpd xmm2,oword [0x00000048 + r8 * 8]'),
    ('SUBPD 4', '66410f5cd5', 'subpd xmm2,xmm13', 'subpd xmm2,xmm13'),
    ('MINPD 0', '660f5d3c2541414141', 'minpd xmm7,oword [0x41414141]', 'minpd xmm7,oword [0x41414141]'),
    ('MINPD 1', '66410f5d39', 'minpd xmm7,oword [r9]', 'minpd xmm7,oword [r9]'),
    ('MINPD 2', '660f5d7922', 'minpd xmm7,oword [rcx + 34]', 'minpd xmm7,oword [rcx + 34]'),
    ('MINPD 3', '66420f5d3cdd22000000', 'minpd xmm7,oword [0x00000022 + r11 * 8]', 'minpd xmm7,oword [0x00000022 + r11 * 8]'),
    ('MINPD 4', '660f5df8', 'minpd xmm7,xmm0', 'minpd xmm7,xmm0'),
    ('MAXPD 0', '66440f5f042541414141', 'maxpd xmm8,oword [0x41414141]', 'maxpd xmm8,oword [0x41414141]'),
    ('MAXPD 1', '66450f5f03', 'maxpd xmm8,oword [r11]', 'maxpd xmm8,oword [r11]'),
    ('MAXPD 2', '66450f5f85c4000000', 'maxpd xmm8,oword [r13 + 196]', 'maxpd xmm8,oword [r13 + 196]'),
    ('MAXPD 3', '66460f5f04cdc4000000', 'maxpd xmm8,oword [0x000000c4 + r9 * 8]', 'maxpd xmm8,oword [0x000000c4 + r9 * 8]'),
    ('MAXPD 4', '66440f5fc1', 'maxpd xmm8,xmm1', 'maxpd xmm8,xmm1'),
    ('MOV AMETH_C', '0f20d0', 'mov rax,ctrl2', 'mov rax,ctrl2'),
    ('MOV AMETH_C 2', '0f20f1', 'mov rcx,ctrl6', 'mov rcx,ctrl6'),
    ('MOV AMETH_C 3', '0f22e2', 'mov ctrl4,rdx', 'mov ctrl4,rdx'),
    ('MOV AMETH_C 4', '0f22f8', 'mov ctrl7,rax', 'mov ctrl7,rax'),
    ('MOV AMETH_C REX', '440f20c2', 'mov rdx,ctrl8', 'mov rdx,ctrl8'),
    ('MOV AMETH_C REX 2', '450f22c1', 'mov ctrl8,r9', 'mov ctrl8,r9'),

    ('MOV AMETH_D', '0f21c0', 'mov rax,debug0', 'mov rax,debug0'), # ADDRMETH_D
    ('MOV AMETH_D 2', '0f21f9', 'mov rcx,debug7', 'mov rcx,debug7'),
    ('MOV AMETH_D 3', '0f23e1', 'mov debug4,rcx', 'mov debug4,rcx'),
    ('MOV AMETH_D REX', '410f23c4', 'mov debug0,r12', 'mov debug0,r12'),
    ('MOV RCX', '48C7C189754200', 'mov rcx,0x00427589', 'mov rcx,0x00427589'),
    ('MOV CX', '66b90202', 'mov cx,514', 'mov cx,514'),
    ('MOV AH', 'b4b3', 'mov ah,179', 'mov ah,179'),

    ('LEA', '8d4a0c', 'lea ecx,dword [rdx + 12]', 'lea ecx,dword [rdx + 12]'),
    ('LEA 2', '488d400c', 'lea rax,qword [rax + 12]', 'lea rax,qword [rax + 12]'),
    ('XOR', '4981F4CE260000', 'xor r12,0x000026ce', 'xor r12,0x000026ce'),
    ('XOR SIGNED', '4881F19B83FFFF', 'xor rcx,0xffffffffffff839b', 'xor rcx,0xffffffffffff839b'),
    ('SIGNED', '83C0F9', 'add eax,0xfffffff9', 'add eax,0xfffffff9'),
    ('UNSIGNED', '05f9000000', 'add eax,249', 'add eax,249'),

    ('MOV SEGREG 2', '8ce0', 'mov eax,fs', 'mov eax,fs'),
    ('MOV SEGREG 3', '8ec6', 'mov es,esi', 'mov es,esi'),
    ('MOV SEGREG 4', '488ce7', 'mov rdi,fs', 'mov rdi,fs'),
    ('MOV SEGREG 5', '488ed6', 'mov ss,rsi', 'mov ss,rsi'),
    ('MOV SEGREG 6', '8E142541414141', 'mov ss,word [0x41414141]', 'mov ss,word [0x41414141]'),
    ('MOV SEGREG 7', '8C042541414141', 'mov word [0x41414141],es', 'mov word [0x41414141],es'),

    ('PMOVSXBW', '660f3820ca', 'pmovsxbw xmm1,xmm2', 'pmovsxbw xmm1,xmm2'),
    ('PMOVSXBD', '660f3821cb', 'pmovsxbd xmm1,xmm3', 'pmovsxbd xmm1,xmm3'),
    ('PMOVSXBQ', '660f3822d3', 'pmovsxbq xmm2,xmm3', 'pmovsxbq xmm2,xmm3'),
    ('PMOVSXWD', '660f3823ff', 'pmovsxwd xmm7,xmm7', 'pmovsxwd xmm7,xmm7'),
    ('PMOVSXWQ', '66440f3824dc', 'pmovsxwq xmm11,xmm4', 'pmovsxwq xmm11,xmm4'),
    ('PMOVSXDQ', '66410f3825df', 'pmovsxdq xmm3,xmm15', 'pmovsxdq xmm3,xmm15'),

    ('PMOVZXBW', '660f3830ca', 'pmovzxbw xmm1,xmm2', 'pmovzxbw xmm1,xmm2'),
    ('PMOVZXBD', '660f3831cb', 'pmovzxbd xmm1,xmm3', 'pmovzxbd xmm1,xmm3'),
    ('PMOVZXBQ', '660f3832d3', 'pmovzxbq xmm2,xmm3', 'pmovzxbq xmm2,xmm3'),
    ('PMOVZXWD', '660f3833ff', 'pmovzxwd xmm7,xmm7', 'pmovzxwd xmm7,xmm7'),
    ('PMOVZXWQ', '66440f3834dc', 'pmovzxwq xmm11,xmm4', 'pmovzxwq xmm11,xmm4'),
    ('PMOVZXDQ', '66410f3835df', 'pmovzxdq xmm3,xmm15', 'pmovzxdq xmm3,xmm15'),

    ('PMOVSXBW (MEM)', '66440f382018', 'pmovsxbw xmm11,qword [rax]', 'pmovsxbw xmm11,qword [rax]'),
    ('PMOVSXBD (MEM)', '660f3821242541414141', 'pmovsxbd xmm4,dword [0x41414141]', 'pmovsxbd xmm4,dword [0x41414141]'),
    ('PMOVSXBQ (MEM)', '66410f38228b29230000', 'pmovsxbq xmm1,word [r11 + 9001]', 'pmovsxbq xmm1,word [r11 + 9001]'),
    ('PMOVSXWD (MEM)', '66440f38230c11', 'pmovsxwd xmm9,qword [rcx + rdx]', 'pmovsxwd xmm9,qword [rcx + rdx]'),
    ('PMOVSXWQ (MEM)', '660f38241cb507000000', 'pmovsxwq xmm3,dword [0x00000007 + rsi * 4]', 'pmovsxwq xmm3,dword [0x00000007 + rsi * 4]'),
    ('PMOVSXDQ (MEM)', '660f382532', 'pmovsxdq xmm6,qword [rdx]', 'pmovsxdq xmm6,qword [rdx]'),

    ('PMOVSXBW (MEM)', '66440f383018', 'pmovzxbw xmm11,qword [rax]', 'pmovzxbw xmm11,qword [rax]'),
    ('PMOVSXBD (MEM)', '660f3831242541414141', 'pmovzxbd xmm4,dword [0x41414141]', 'pmovzxbd xmm4,dword [0x41414141]'),
    ('PMOVSXBQ (MEM)', '66410f38328b29230000', 'pmovzxbq xmm1,word [r11 + 9001]', 'pmovzxbq xmm1,word [r11 + 9001]'),
    ('PMOVSXWD (MEM)', '66440f38330c11', 'pmovzxwd xmm9,qword [rcx + rdx]', 'pmovzxwd xmm9,qword [rcx + rdx]'),
    ('PMOVSXWQ (MEM)', '660f38341cb507000000', 'pmovzxwq xmm3,dword [0x00000007 + rsi * 4]', 'pmovzxwq xmm3,dword [0x00000007 + rsi * 4]'),
    ('PMOVSXDQ (MEM)', '660f383532', 'pmovzxdq xmm6,qword [rdx]', 'pmovzxdq xmm6,qword [rdx]'),
    ('SHA256RNDS2', '0f38cbd3', 'sha256rnds2 xmm2,xmm3,xmm0', 'sha256rnds2 xmm2,xmm3,xmm0'),
    ('SFENCE', '0faef8', 'sfence ', 'sfence '),
    ('LFENCE', '0faee8', 'lfence ', 'lfence '),
    ('MFENCE', '0faef0', 'mfence ', 'mfence '),
    ('XSAVE', '0FAE242541414141', 'xsave dword [0x41414141]', 'xsave dword [0x41414141]'),
    ('WRFSBASE', 'F30FAED0', 'wrfsbase eax', 'wrfsbase eax'),
    ('RDFSBASE', 'F3480FAEC0', 'rdfsbase rax', 'rdfsbase rax'),

    ('WAIT', '9b', 'wait ', 'wait '),  # TODO: this needs to be able to change the opcode too
    ('ADOX 1', 'F30F38f6c2', 'adox eax,edx', 'adox eax,edx'),
    ('ADOX 2', 'f3480f38f6c2', 'adox rax,rdx', 'adox rax,rdx'),
    ('ADOX 3', 'F30F38F6042541414141', 'adox eax,dword [0x41414141]', 'adox eax,dword [0x41414141]'),
    ('ADOX 4', 'F3480F38F6042541414141', 'adox rax,qword [0x41414141]', 'adox rax,qword [0x41414141]'),
    ('ADCX 1', '660f38f6e5', 'adcx esp,ebp', 'adcx esp,ebp'),
    ('ADCX 2', '66480f38f6e5', 'adcx rsp,rbp', 'adcx rsp,rbp'),
    ('ADCX 3', '660f38f6242541414141', 'adcx esp,dword [0x41414141]', 'adcx esp,dword [0x41414141]'),
    ('ADCX 4', '664c0f38f6242541414141', 'adcx r12,qword [0x41414141]', 'adcx r12,qword [0x41414141]'),
]

amd64VexOpcodes = [
    ('vpblendvb', 'C4E3694CCB40', 'vpblendvb xmm1,xmm2,xmm3,xmm4', 'vpblendvb xmm1,xmm2,xmm3,xmm4'),
    ('vpblendvb (256)', 'C4E36D4CCB40', 'vpblendvb ymm1,ymm2,ymm3,ymm4', 'vpblendvb ymm1,ymm2,ymm3,ymm4'),
    ('SARX 1', 'c4e272f7c3', 'sarx eax,ebx,ecx', 'sarx eax,ebx,ecx'),
    ('SARX 2', 'c4e2f2f7c3', 'sarx rax,rbx,rcx', 'sarx rax,rbx,rcx'),
    ('SARX 3', 'c4e262f7042541414141', 'sarx eax,dword [0x41414141],ebx', 'sarx eax,dword [0x41414141],ebx'),
    ('SARX 4', 'c4e2f2f7042541414141', 'sarx rax,qword [0x41414141],rcx', 'sarx rax,qword [0x41414141],rcx'),

    ('SHLX 1', 'c4e261f7c3', 'shlx eax,ebx,ebx', 'shlx eax,ebx,ebx'),
    ('SHLX 2', 'c4e2e1f7c4', 'shlx rax,rsp,rbx', 'shlx rax,rsp,rbx'),
    ('SHLX 3', 'c4e261f7042541414141', 'shlx eax,dword [0x41414141],ebx', 'shlx eax,dword [0x41414141],ebx'),
    ('SHLX 4', 'c4e2e1f7042541414141', 'shlx rax,qword [0x41414141],rbx', 'shlx rax,qword [0x41414141],rbx'),

    ('SHRX 1', 'C4E273F7C3', 'shrx eax,ebx,ecx', 'shrx eax,ebx,ecx'),
    ('SHRX 2', 'C4E2F3F7C3', 'shrx rax,rbx,rcx', 'shrx rax,rbx,rcx'),
    ('SHRX 3', 'C4E273F7042541414141', 'shrx eax,dword [0x41414141],ecx', 'shrx eax,dword [0x41414141],ecx'),
    ('SHRX 4', 'C4E2f3F7042541414141', 'shrx rax,qword [0x41414141],rcx', 'shrx rax,qword [0x41414141],rcx'),
    ('MULX 1', 'C4E273f6c3', 'mulx eax,ecx,ebx', 'mulx eax,ecx,ebx'),
    ('MULX 2', 'C4E2f3f6c3', 'mulx rax,rcx,rbx', 'mulx rax,rcx,rbx'),
    ('MULX 3', 'C4E263F60C2541414141', 'mulx ecx,ebx,dword [0x41414141]', 'mulx ecx,ebx,dword [0x41414141]'),
    ('MULX 4', 'C4E2E3F60C2541414141', 'mulx rcx,rbx,qword [0x41414141]', 'mulx rcx,rbx,qword [0x41414141]'),
    ('PDEP 1', 'C4E263F5C1', 'pdep eax,ebx,ecx', 'pdep eax,ebx,ecx'),
    ('PDEP 2', 'C4E2E3F5C1', 'pdep rax,rbx,rcx', 'pdep rax,rbx,rcx'),
    ('PDEP 3', 'C4E263F5042541414141', 'pdep eax,ebx,dword [0x41414141]', 'pdep eax,ebx,dword [0x41414141]'),
    ('PDEP 4', 'C4E2E3F5042541414141', 'pdep rax,rbx,qword [0x41414141]', 'pdep rax,rbx,qword [0x41414141]'),
    ('PEXT 1', 'c4e272f5d3', 'pext edx,ecx,ebx', 'pext edx,ecx,ebx'),
    ('PEXT 2', 'c4e2f2f5d3', 'pext rdx,rcx,rbx', 'pext rdx,rcx,rbx'),
    ('PEXT 3', 'c4e272f5142541414141', 'pext edx,ecx,dword [0x41414141]', 'pext edx,ecx,dword [0x41414141]'),
    ('PEXT 4', 'c4e2f2f5142541414141', 'pext rdx,rcx,qword [0x41414141]', 'pext rdx,rcx,qword [0x41414141]'),

    ('PBLENDW', '660f3a0ef411', 'pblendw xmm6,xmm4,17', 'pblendw xmm6,xmm4,17'),
    ('VBROADCASTI', 'c4627d5a1d8decffff', 'vpbroadcasti128 ymm11,oword [rip + -4979]', 'vpbroadcasti128 ymm11,oword [rip - 4979]'),

    ('PSRLW (VEX)', 'C5E9D1CB', 'vpsrlw xmm1,xmm2,xmm3', 'vpsrlw xmm1,xmm2,xmm3'),
    ('PSRLW (VEX) 1', 'C5F171D208', 'vpsrlw xmm1,xmm2,8', 'vpsrlw xmm1,xmm2,8'),
    ('PSRLW (VEX) 2', 'C5E9D10C2541414141', 'vpsrlw xmm1,xmm2,oword [0x41414141]', 'vpsrlw xmm1,xmm2,oword [0x41414141]'),
    ('PSRLW (VEX) 3', '67C5E9D108', 'vpsrlw xmm1,xmm2,oword [eax]', 'vpsrlw xmm1,xmm2,oword [eax]'),
    ('ANDN', 'C4E260F2C1', 'andn eax,ebx,ecx', 'andn eax,ebx,ecx'),
    ('ANDN 2', 'C4E2E0F2C1', 'andn rax,rbx,rcx', 'andn rax,rbx,rcx'),
    ('BEXTR', 'C4E270F7D3', 'bextr edx,ebx,ecx', 'bextr edx,ebx,ecx'),
    ('BEXTR 2', 'C4E2F0F7D0', 'bextr rdx,rax,rcx', 'bextr rdx,rax,rcx'),
    ('BEXTR 3', 'C4E2F0F71541414100', 'bextr rdx,qword [rip + 4276545],rcx', 'bextr rdx,qword [rip + 4276545],rcx'),
    ('BLSI', 'c4e268f3d8', 'blsi edx,eax', 'blsi edx,eax'),
    ('BLSI 2', 'C4E268F31C2541414141', 'blsi edx,dword [0x41414141]', 'blsi edx,dword [0x41414141]'),
    ('BLSI 3', 'C4E2F0F31C2541414141', 'blsi rcx,qword [0x41414141]', 'blsi rcx,qword [0x41414141]'),
    ('BLSMSK', 'C4E2F0F3142541414141', 'blsmsk rcx,qword [0x41414141]', 'blsmsk rcx,qword [0x41414141]'),
    ('BLSMSK 2', 'C4E278F3D2', 'blsmsk eax,edx', 'blsmsk eax,edx'),
    ('BLSR', 'C4E278F3CB', 'blsr eax,ebx', 'blsr eax,ebx'),
    ('BLSR 3', 'C4E270F30C2541414141', 'blsr ecx,dword [0x41414141]', 'blsr ecx,dword [0x41414141]'),
    ('BLSR 4', 'C4E2F0F30B', 'blsr rcx,qword [rbx]', 'blsr rcx,qword [rbx]'),
    ('BLSR 5', 'C4E2E8F30C2541414141', 'blsr rdx,qword [0x41414141]', 'blsr rdx,qword [0x41414141]'),
    ('VMOVSS',   'C5E210CE', 'vmovss xmm1,xmm3,xmm6', 'vmovss xmm1,xmm3,xmm6'),
    ('VMOVSS 2', 'C5FA1008', 'vmovss xmm1,dword [rax]', 'vmovss xmm1,dword [rax]'),
    ('VMOVSS 3', 'C5FA10CB', 'vmovss xmm1,xmm0,xmm3', 'vmovss xmm1,xmm0,xmm3'),
    ('VMOVSD', 'C5FB1008', 'vmovsd xmm1,qword [rax]', 'vmovsd xmm1,qword [rax]'),
    ('VMOVSD 2', 'C5EB10CB', 'vmovsd xmm1,xmm2,xmm3', 'vmovsd xmm1,xmm2,xmm3'),
    ('VMOVSD 3', 'C5EB11CB', 'vmovsd xmm3,xmm2,xmm1', 'vmovsd xmm3,xmm2,xmm1'),
    ('VMOVSD 4', 'C5FB111C2541414141', 'vmovsd qword [0x41414141],xmm3', 'vmovsd qword [0x41414141],xmm3'),
    ('VMOVSD 5', '67C5FB1118', 'vmovsd qword [eax],xmm3', 'vmovsd qword [eax],xmm3'),

    ('HADDPS 1', 'C5CB7CCB', 'vhaddps xmm1,xmm6,xmm3', 'vhaddps xmm1,xmm6,xmm3'),
    ('HADDPS 2', 'C5E77CD6', 'vhaddps ymm2,ymm3,ymm6', 'vhaddps ymm2,ymm3,ymm6'),
    ('VMOVDQU', 'C5fe6fe3', 'vmovdqu ymm4,ymm3', 'vmovdqu ymm4,ymm3'),
    ('VLDDQU', 'C5FFF01C2541414141', 'vlddqu ymm3,yword [0x41414141]', 'vlddqu ymm3,yword [0x41414141]'),
    ('VLDDQU 2', 'C5FFF034D504000000', 'vlddqu ymm6,yword [0x00000004 + rdx * 8]', 'vlddqu ymm6,yword [0x00000004 + rdx * 8]'),
    ('VLDDQU 3', 'C5FBF00CF504000000', 'vlddqu xmm1,oword [0x00000004 + rsi * 8]', 'vlddqu xmm1,oword [0x00000004 + rsi * 8]'),
    ('VLDDQU 4', '67C5FBF00CF504000000', 'vlddqu xmm1,oword [0x00000004 + esi * 8]', 'vlddqu xmm1,oword [0x00000004 + esi * 8]'),

    ('INSERTPS 4', 'C4E36921D94C', 'vinsertps xmm3,xmm2,xmm1,76', 'vinsertps xmm3,xmm2,xmm1,76'),
    ('INSERTPS 5', 'C4E369211C25414141414C', 'vinsertps xmm3,xmm2,dword [0x41414141],76', 'vinsertps xmm3,xmm2,dword [0x41414141],76'),
    ('INSERTPS 6', 'C4E3692198454141414C', 'vinsertps xmm3,xmm2,dword [rax + 1094795589],76', 'vinsertps xmm3,xmm2,dword [rax + 1094795589],76'),

    ('VPSLLDQ', 'C5F173D208', 'vpsrlq xmm1,xmm2,8', 'vpsrlq xmm1,xmm2,8'),
    ('VPSRLD', 'C5E172D41B', 'vpsrld xmm3,xmm4,27', 'vpsrld xmm3,xmm4,27'),
    ('VPSRLD', 'c5e172d063', 'vpsrld xmm3,xmm0,99', 'vpsrld xmm3,xmm0,99'),
    ('VPSRLD REP', 'f3c5e172d063', 'rep: vpsrld xmm3,xmm0,99', 'rep: vpsrld xmm3,xmm0,99'),
    ('VPSRLD 2', 'C5D9D218', 'vpsrld xmm3,xmm4,oword [rax]', 'vpsrld xmm3,xmm4,oword [rax]'),
    ('VPSRLD 3', 'C5D9D25875', 'vpsrld xmm3,xmm4,oword [rax + 117]', 'vpsrld xmm3,xmm4,oword [rax + 117]'),

    ('VPSRLDQ', 'C5E9D3CB', 'vpsrlq xmm1,xmm2,xmm3', 'vpsrlq xmm1,xmm2,xmm3'),
    ('VPOR', 'C5EDEBCB', 'vpor ymm1,ymm2,ymm3', 'vpor ymm1,ymm2,ymm3'),
    ('VSQRTPD', 'C5F951CA', 'vsqrtpd xmm1,xmm2', 'vsqrtpd xmm1,xmm2'),
    ('VSQRTPD 2', 'C5FD51CA', 'vsqrtpd ymm1,ymm2', 'vsqrtpd ymm1,ymm2'),
    ('VBLENDVPS (128)', 'C4E3694ACB40', 'vblendvps xmm1,xmm2,xmm3,xmm4', 'vblendvps xmm1,xmm2,xmm3,xmm4'),
    ('VBLENDVPS (MEM128)', 'C4E3694A0C254141414140', 'vblendvps xmm1,xmm2,oword [0x41414141],xmm4', 'vblendvps xmm1,xmm2,oword [0x41414141],xmm4'),
    ('VBLENDVPS (256)', 'C4E36D4ACB40', 'vblendvps ymm1,ymm2,ymm3,ymm4', 'vblendvps ymm1,ymm2,ymm3,ymm4'),
    ('VBLENDVPS (MEM256)', 'C4E36D4A0C254141414140', 'vblendvps ymm1,ymm2,yword [0x41414141],ymm4', 'vblendvps ymm1,ymm2,yword [0x41414141],ymm4'),
    ('VMOVUPD', 'C5F910D3', 'vmovupd xmm2,xmm3', 'vmovupd xmm2,xmm3'),
    ('VMOVUPD 2', 'C5FD10D6', 'vmovupd ymm2,ymm6', 'vmovupd ymm2,ymm6'),
    ('VMOVUPD 3', 'C5FD1010', 'vmovupd ymm2,yword [rax]', 'vmovupd ymm2,yword [rax]'),
    ('VMOVUPD 4', 'c5f910c3', 'vmovupd xmm0,xmm3', 'vmovupd xmm0,xmm3'),
    ('VMOVSLDUP', 'c5fa12d4', 'vmovsldup xmm2,xmm4', 'vmovsldup xmm2,xmm4'),
    ('VMOVSLDUP 2', 'c5fe12d4', 'vmovsldup ymm2,ymm4', 'vmovsldup ymm2,ymm4'),
    ('VMOVSLDUP 3', 'c5fe1210', 'vmovsldup ymm2,yword [rax]', 'vmovsldup ymm2,yword [rax]'),
    ('VMOVSLDUP 4', 'c5fe125257', 'vmovsldup ymm2,yword [rdx + 87]', 'vmovsldup ymm2,yword [rdx + 87]'),
    ('VMOVAPD', 'c57928ea', 'vmovapd xmm13,xmm2', 'vmovapd xmm13,xmm2'),
    ('VMOVAPD 2', 'c5792804cd97000000', 'vmovapd xmm8,oword [0x00000097 + rcx * 8]', 'vmovapd xmm8,oword [0x00000097 + rcx * 8]'),
    ('VMOVAPD 3', 'c57d28cc', 'vmovapd ymm9,ymm4', 'vmovapd ymm9,ymm4'),
    ('VMOVAPD 4', 'c5fd297913', 'vmovapd yword [rcx + 19],ymm7', 'vmovapd yword [rcx + 19],ymm7'),
    ('VMOVAPD 5', 'c57d290a', 'vmovapd yword [rdx],ymm9', 'vmovapd yword [rdx],ymm9'),
    ('VMOVLPD', 'c5e91218', 'vmovlpd xmm3,xmm2,qword [rax]', 'vmovlpd xmm3,xmm2,qword [rax]'),
    ('VMOVLPD 2', 'c44111126b62', 'vmovlpd xmm13,xmm13,qword [r11 + 98]', 'vmovlpd xmm13,xmm13,qword [r11 + 98]'),
    ('VMOVDDUP', 'c5fb12fa', 'vmovddup xmm7,xmm2', 'vmovddup xmm7,xmm2'),
    ('VMOVDDUP 2', 'c5fb1221', 'vmovddup xmm4,oword [rcx]', 'vmovddup xmm4,oword [rcx]'),
    ('VMOVNTPD', 'c4c1792b12', 'vmovntpd oword [r10],xmm2', 'vmovntpd oword [r10],xmm2'),
    ('VMOVNTPD 2', 'c4417d2b2a', 'vmovntpd yword [r10],ymm13', 'vmovntpd yword [r10],ymm13'),
    # Are these next three right (all of vmovmskpd)? They're what nasm decodes them to
    ('VMOVMSKPD', 'c4c17950c5', 'vmovmskpd eax,xmm13', 'vmovmskpd eax,xmm13'),
    ('VMOVMSKPD 2', 'c4c17d50c5', 'vmovmskpd rax,ymm13', 'vmovmskpd rax,ymm13'),
    ('VADDSS', 'c5ea580a', 'vaddss xmm1,xmm2,dword [rdx]', 'vaddss xmm1,xmm2,dword [rdx]'),
    ('VADDSS 2', 'c5ea58cc', 'vaddss xmm1,xmm2,xmm4', 'vaddss xmm1,xmm2,xmm4'),
    ('VMULSS', 'c5ea590a', 'vmulss xmm1,xmm2,dword [rdx]', 'vmulss xmm1,xmm2,dword [rdx]'),
    ('VMULSS 2', 'c5ea59cc', 'vmulss xmm1,xmm2,xmm4', 'vmulss xmm1,xmm2,xmm4'),
    ('VUNPCKLPD', 'c5d914d6', 'vunpcklpd xmm2,xmm4,xmm6', 'vunpcklpd xmm2,xmm4,xmm6'),
    ('VUNPCKLPD 2', 'c5dd14d6', 'vunpcklpd ymm2,ymm4,ymm6', 'vunpcklpd ymm2,ymm4,ymm6'),
    ('VUNPCKLPD 3', 'c5d914142541414141', 'vunpcklpd xmm2,xmm4,oword [0x41414141]', 'vunpcklpd xmm2,xmm4,oword [0x41414141]'),
    ('VUNPCKLPD 4', 'c5dd14142541414141', 'vunpcklpd ymm2,ymm4,yword [0x41414141]', 'vunpcklpd ymm2,ymm4,yword [0x41414141]'),
    ('VUNPCKLPD 5', 'c5b514f9', 'vunpcklpd ymm7,ymm9,ymm1', 'vunpcklpd ymm7,ymm9,ymm1'),
    ('VLDDQU', 'c4c17bf01424', 'vlddqu xmm2,oword [r12]', 'vlddqu xmm2,oword [r12]'),
    ('VLDDQU', 'c4c17ff01424', 'vlddqu ymm2,yword [r12]', 'vlddqu ymm2,yword [r12]'),
    ('VPSHUFLW', 'c5fb70ca61', 'vpshuflw xmm1,xmm2,97', 'vpshuflw xmm1,xmm2,97'),
    ('VPSHUFLW 2', 'c5ff70ca11', 'vpshuflw ymm1,ymm2,17', 'vpshuflw ymm1,ymm2,17'),
    ('VPSHUFLW 3', 'c4417f70d411', 'vpshuflw ymm10,ymm12,17', 'vpshuflw ymm10,ymm12,17'),
    ('VPSHUFLW 4', 'c57f701040', 'vpshuflw ymm10,yword [rax],64', 'vpshuflw ymm10,yword [rax],64'),
    ('VCVTPD2DQ', 'c57be6e9', 'vcvtpd2dq xmm13,xmm1', 'vcvtpd2dq xmm13,xmm1'),
    ('VCVTPD2DQ 2', 'c4417be62b', 'vcvtpd2dq xmm13,oword [r11]', 'vcvtpd2dq xmm13,oword [r11]'),
    ('VCVTPD2DQ 3', 'c57fe6e9', 'vcvtpd2dq xmm13,ymm1', 'vcvtpd2dq xmm13,ymm1'),
    ('VCVTPD2DQ 4', 'c4c17fe60a', 'vcvtpd2dq xmm1,yword [r10]', 'vcvtpd2dq xmm1,yword [r10]'),

    ('VANDPD 0', 'c5c1541c254a4a4a4a', 'vandpd xmm3,xmm7,oword [0x4a4a4a4a]', 'vandpd xmm3,xmm7,oword [0x4a4a4a4a]'),
    ('VANDPD 1', 'c4c141541f', 'vandpd xmm3,xmm7,oword [r15]', 'vandpd xmm3,xmm7,oword [r15]'),
    ('VANDPD 2', 'c4c141545960', 'vandpd xmm3,xmm7,oword [r9 + 96]', 'vandpd xmm3,xmm7,oword [r9 + 96]'),
    ('VANDPD 3', 'c4a141541cc560000000', 'vandpd xmm3,xmm7,oword [0x00000060 + r8 * 8]', 'vandpd xmm3,xmm7,oword [0x00000060 + r8 * 8]'),
    ('VANDPD 4', 'c5c154d9', 'vandpd xmm3,xmm7,xmm1', 'vandpd xmm3,xmm7,xmm1'),
    ('VANDPD 5', 'c55d540c254a4a4a4a', 'vandpd ymm9,ymm4,yword [0x4a4a4a4a]', 'vandpd ymm9,ymm4,yword [0x4a4a4a4a]'),
    ('VANDPD 6', 'c4415d540b', 'vandpd ymm9,ymm4,yword [r11]', 'vandpd ymm9,ymm4,yword [r11]'),
    ('VANDPD 7', 'c55d548ab2000000', 'vandpd ymm9,ymm4,yword [rdx + 178]', 'vandpd ymm9,ymm4,yword [rdx + 178]'),
    ('VANDPD 8', 'c55d540ccdb2000000', 'vandpd ymm9,ymm4,yword [0x000000b2 + rcx * 8]', 'vandpd ymm9,ymm4,yword [0x000000b2 + rcx * 8]'),
    ('VANDPD 9', 'c4415d54ce', 'vandpd ymm9,ymm4,ymm14', 'vandpd ymm9,ymm4,ymm14'),
    ('VANDNPD 0', 'c5995524254a4a4a4a', 'vandnpd xmm4,xmm12,oword [0x4a4a4a4a]', 'vandnpd xmm4,xmm12,oword [0x4a4a4a4a]'),
    ('VANDNPD 1', 'c4c1195523', 'vandnpd xmm4,xmm12,oword [r11]', 'vandnpd xmm4,xmm12,oword [r11]'),
    ('VANDNPD 2', 'c4c11955a289000000', 'vandnpd xmm4,xmm12,oword [r10 + 137]', 'vandnpd xmm4,xmm12,oword [r10 + 137]'),
    ('VANDNPD 3', 'c5995524c589000000', 'vandnpd xmm4,xmm12,oword [0x00000089 + rax * 8]', 'vandnpd xmm4,xmm12,oword [0x00000089 + rax * 8]'),
    ('VANDNPD 4', 'c4c11955e1', 'vandnpd xmm4,xmm12,xmm9', 'vandnpd xmm4,xmm12,xmm9'),
    ('VANDNPD 5', 'c5855514254a4a4a4a', 'vandnpd ymm2,ymm15,yword [0x4a4a4a4a]', 'vandnpd ymm2,ymm15,yword [0x4a4a4a4a]'),
    ('VANDNPD 6', 'c5855510', 'vandnpd ymm2,ymm15,yword [rax]', 'vandnpd ymm2,ymm15,yword [rax]'),
    ('VANDNPD 7', 'c4c105559424e8000000', 'vandnpd ymm2,ymm15,yword [r12 + 232]', 'vandnpd ymm2,ymm15,yword [r12 + 232]'),
    ('VANDNPD 8', 'c4a1055514e5e8000000', 'vandnpd ymm2,ymm15,yword [0x000000e8 + r12 * 8]', 'vandnpd ymm2,ymm15,yword [0x000000e8 + r12 * 8]'),
    ('VANDNPD 9', 'c4c10555d7', 'vandnpd ymm2,ymm15,ymm15', 'vandnpd ymm2,ymm15,ymm15'),
    ('VADDPD 0', 'c5d15824254a4a4a4a', 'vaddpd xmm4,xmm5,oword [0x4a4a4a4a]', 'vaddpd xmm4,xmm5,oword [0x4a4a4a4a]'),
    ('VADDPD 1', 'c4c1515823', 'vaddpd xmm4,xmm5,oword [r11]', 'vaddpd xmm4,xmm5,oword [r11]'),
    ('VADDPD 2', 'c4c15158a0de000000', 'vaddpd xmm4,xmm5,oword [r8 + 222]', 'vaddpd xmm4,xmm5,oword [r8 + 222]'),
    ('VADDPD 3', 'c4a1515824c5de000000', 'vaddpd xmm4,xmm5,oword [0x000000de + r8 * 8]', 'vaddpd xmm4,xmm5,oword [0x000000de + r8 * 8]'),
    ('VADDPD 4', 'c4c15158e2', 'vaddpd xmm4,xmm5,xmm10', 'vaddpd xmm4,xmm5,xmm10'),
    ('VADDPD 5', 'c555581c254a4a4a4a', 'vaddpd ymm11,ymm5,yword [0x4a4a4a4a]', 'vaddpd ymm11,ymm5,yword [0x4a4a4a4a]'),
    ('VADDPD 6', 'c44155581e', 'vaddpd ymm11,ymm5,yword [r14]', 'vaddpd ymm11,ymm5,yword [r14]'),
    ('VADDPD 7', 'c44155589fb4000000', 'vaddpd ymm11,ymm5,yword [r15 + 180]', 'vaddpd ymm11,ymm5,yword [r15 + 180]'),
    ('VADDPD 8', 'c42155581cfdb4000000', 'vaddpd ymm11,ymm5,yword [0x000000b4 + r15 * 8]', 'vaddpd ymm11,ymm5,yword [0x000000b4 + r15 * 8]'),
    ('VADDPD 9', 'c4415558df', 'vaddpd ymm11,ymm5,ymm15', 'vaddpd ymm11,ymm5,ymm15'),
    ('VORPD 0', 'c5715614254a4a4a4a', 'vorpd xmm10,xmm1,oword [0x4a4a4a4a]', 'vorpd xmm10,xmm1,oword [0x4a4a4a4a]'),
    ('VORPD 1', 'c441715611', 'vorpd xmm10,xmm1,oword [r9]', 'vorpd xmm10,xmm1,oword [r9]'),
    ('VORPD 2', 'c441715697ff000000', 'vorpd xmm10,xmm1,oword [r15 + 255]', 'vorpd xmm10,xmm1,oword [r15 + 255]'),
    ('VORPD 3', 'c421715614f5ff000000', 'vorpd xmm10,xmm1,oword [0x000000ff + r14 * 8]', 'vorpd xmm10,xmm1,oword [0x000000ff + r14 * 8]'),
    ('VORPD 4', 'c57156d6', 'vorpd xmm10,xmm1,xmm6', 'vorpd xmm10,xmm1,xmm6'),
    ('VORPD 5', 'c5cd563c254a4a4a4a', 'vorpd ymm7,ymm6,yword [0x4a4a4a4a]', 'vorpd ymm7,ymm6,yword [0x4a4a4a4a]'),
    ('VORPD 6', 'c5cd563b', 'vorpd ymm7,ymm6,yword [rbx]', 'vorpd ymm7,ymm6,yword [rbx]'),
    ('VORPD 7', 'c4c14d567d5e', 'vorpd ymm7,ymm6,yword [r13 + 94]', 'vorpd ymm7,ymm6,yword [r13 + 94]'),
    ('VORPD 8', 'c4a14d563ce55e000000', 'vorpd ymm7,ymm6,yword [0x0000005e + r12 * 8]', 'vorpd ymm7,ymm6,yword [0x0000005e + r12 * 8]'),
    ('VORPD 9', 'c4c14d56fe', 'vorpd ymm7,ymm6,ymm14', 'vorpd ymm7,ymm6,ymm14'),
    ('VXORPD 0', 'c579570c254a4a4a4a', 'vxorpd xmm9,xmm0,oword [0x4a4a4a4a]', 'vxorpd xmm9,xmm0,oword [0x4a4a4a4a]'),
    ('VXORPD 1', 'c441795708', 'vxorpd xmm9,xmm0,oword [r8]', 'vxorpd xmm9,xmm0,oword [r8]'),
    ('VXORPD 2', 'c44179574856', 'vxorpd xmm9,xmm0,oword [r8 + 86]', 'vxorpd xmm9,xmm0,oword [r8 + 86]'),
    ('VXORPD 3', 'c579570cc556000000', 'vxorpd xmm9,xmm0,oword [0x00000056 + rax * 8]', 'vxorpd xmm9,xmm0,oword [0x00000056 + rax * 8]'),
    ('VXORPD 4', 'c57957ce', 'vxorpd xmm9,xmm0,xmm6', 'vxorpd xmm9,xmm0,xmm6'),
    ('VXORPD 5', 'c5255724254a4a4a4a', 'vxorpd ymm12,ymm11,yword [0x4a4a4a4a]', 'vxorpd ymm12,ymm11,yword [0x4a4a4a4a]'),
    ('VXORPD 6', 'c441255721', 'vxorpd ymm12,ymm11,yword [r9]', 'vxorpd ymm12,ymm11,yword [r9]'),
    ('VXORPD 7', 'c52557a382000000', 'vxorpd ymm12,ymm11,yword [rbx + 130]', 'vxorpd ymm12,ymm11,yword [rbx + 130]'),
    ('VXORPD 8', 'c5255724dd82000000', 'vxorpd ymm12,ymm11,yword [0x00000082 + rbx * 8]', 'vxorpd ymm12,ymm11,yword [0x00000082 + rbx * 8]'),
    ('VXORPD 9', 'c4412557e0', 'vxorpd ymm12,ymm11,ymm8', 'vxorpd ymm12,ymm11,ymm8'),
    ('VMULPD 0', 'c5795924254a4a4a4a', 'vmulpd xmm12,xmm0,oword [0x4a4a4a4a]', 'vmulpd xmm12,xmm0,oword [0x4a4a4a4a]'),
    ('VMULPD 1', 'c44179596500', 'vmulpd xmm12,xmm0,oword [r13]', 'vmulpd xmm12,xmm0,oword [r13]'),
    ('VMULPD 2', 'c4417959642462', 'vmulpd xmm12,xmm0,oword [r12 + 98]', 'vmulpd xmm12,xmm0,oword [r12 + 98]'),
    ('VMULPD 3', 'c421795924cd62000000', 'vmulpd xmm12,xmm0,oword [0x00000062 + r9 * 8]', 'vmulpd xmm12,xmm0,oword [0x00000062 + r9 * 8]'),
    ('VMULPD 4', 'c4417959e6', 'vmulpd xmm12,xmm0,xmm14', 'vmulpd xmm12,xmm0,xmm14'),
    ('VMULPD 5', 'c575592c254a4a4a4a', 'vmulpd ymm13,ymm1,yword [0x4a4a4a4a]', 'vmulpd ymm13,ymm1,yword [0x4a4a4a4a]'),
    ('VMULPD 6', 'c44175592b', 'vmulpd ymm13,ymm1,yword [r11]', 'vmulpd ymm13,ymm1,yword [r11]'),
    ('VMULPD 7', 'c4417559a9e0000000', 'vmulpd ymm13,ymm1,yword [r9 + 224]', 'vmulpd ymm13,ymm1,yword [r9 + 224]'),
    ('VMULPD 8', 'c42175592cfde0000000', 'vmulpd ymm13,ymm1,yword [0x000000e0 + r15 * 8]', 'vmulpd ymm13,ymm1,yword [0x000000e0 + r15 * 8]'),
    ('VMULPD 9', 'c4417559ee', 'vmulpd ymm13,ymm1,ymm14', 'vmulpd ymm13,ymm1,ymm14'),
    ('VSUBPD 0', 'c5d15c2c254a4a4a4a', 'vsubpd xmm5,xmm5,oword [0x4a4a4a4a]', 'vsubpd xmm5,xmm5,oword [0x4a4a4a4a]'),
    ('VSUBPD 1', 'c4c1515c2f', 'vsubpd xmm5,xmm5,oword [r15]', 'vsubpd xmm5,xmm5,oword [r15]'),
    ('VSUBPD 2', 'c5d15ca88a000000', 'vsubpd xmm5,xmm5,oword [rax + 138]', 'vsubpd xmm5,xmm5,oword [rax + 138]'),
    ('VSUBPD 3', 'c4a1515c2cd58a000000', 'vsubpd xmm5,xmm5,oword [0x0000008a + r10 * 8]', 'vsubpd xmm5,xmm5,oword [0x0000008a + r10 * 8]'),
    ('VSUBPD 4', 'c5d15cef', 'vsubpd xmm5,xmm5,xmm7', 'vsubpd xmm5,xmm5,xmm7'),
    ('VSUBPD 5', 'c55d5c14254a4a4a4a', 'vsubpd ymm10,ymm4,yword [0x4a4a4a4a]', 'vsubpd ymm10,ymm4,yword [0x4a4a4a4a]'),
    ('VSUBPD 6', 'c4415d5c11', 'vsubpd ymm10,ymm4,yword [r9]', 'vsubpd ymm10,ymm4,yword [r9]'),
    ('VSUBPD 7', 'c4415d5c516c', 'vsubpd ymm10,ymm4,yword [r9 + 108]', 'vsubpd ymm10,ymm4,yword [r9 + 108]'),
    ('VSUBPD 8', 'c4215d5c14dd6c000000', 'vsubpd ymm10,ymm4,yword [0x0000006c + r11 * 8]', 'vsubpd ymm10,ymm4,yword [0x0000006c + r11 * 8]'),
    ('VSUBPD 9', 'c4415d5cd4', 'vsubpd ymm10,ymm4,ymm12', 'vsubpd ymm10,ymm4,ymm12'),
    ('VMINPD 0', 'c5b15d14254a4a4a4a', 'vminpd xmm2,xmm9,oword [0x4a4a4a4a]', 'vminpd xmm2,xmm9,oword [0x4a4a4a4a]'),
    ('VMINPD 1', 'c5b15d11', 'vminpd xmm2,xmm9,oword [rcx]', 'vminpd xmm2,xmm9,oword [rcx]'),
    ('VMINPD 2', 'c4c1315d561e', 'vminpd xmm2,xmm9,oword [r14 + 30]', 'vminpd xmm2,xmm9,oword [r14 + 30]'),
    ('VMINPD 3', 'c4a1315d14cd1e000000', 'vminpd xmm2,xmm9,oword [0x0000001e + r9 * 8]', 'vminpd xmm2,xmm9,oword [0x0000001e + r9 * 8]'),
    ('VMINPD 4', 'c4c1315dd4', 'vminpd xmm2,xmm9,xmm12', 'vminpd xmm2,xmm9,xmm12'),
    ('VMINPD 5', 'c57d5d0c254a4a4a4a', 'vminpd ymm9,ymm0,yword [0x4a4a4a4a]', 'vminpd ymm9,ymm0,yword [0x4a4a4a4a]'),
    ('VMINPD 6', 'c57d5d0a', 'vminpd ymm9,ymm0,yword [rdx]', 'vminpd ymm9,ymm0,yword [rdx]'),
    ('VMINPD 7', 'c57d5d8b94000000', 'vminpd ymm9,ymm0,yword [rbx + 148]', 'vminpd ymm9,ymm0,yword [rbx + 148]'),
    ('VMINPD 8', 'c57d5d0ccd94000000', 'vminpd ymm9,ymm0,yword [0x00000094 + rcx * 8]', 'vminpd ymm9,ymm0,yword [0x00000094 + rcx * 8]'),
    ('VMINPD 9', 'c4417d5dcb', 'vminpd ymm9,ymm0,ymm11', 'vminpd ymm9,ymm0,ymm11'),
    ('VMAXPD 0', 'c5395f24254a4a4a4a', 'vmaxpd xmm12,xmm8,oword [0x4a4a4a4a]', 'vmaxpd xmm12,xmm8,oword [0x4a4a4a4a]'),
    ('VMAXPD 1', 'c5395f22', 'vmaxpd xmm12,xmm8,oword [rdx]', 'vmaxpd xmm12,xmm8,oword [rdx]'),
    ('VMAXPD 2', 'c441395f606b', 'vmaxpd xmm12,xmm8,oword [r8 + 107]', 'vmaxpd xmm12,xmm8,oword [r8 + 107]'),
    ('VMAXPD 3', 'c421395f24f56b000000', 'vmaxpd xmm12,xmm8,oword [0x0000006b + r14 * 8]', 'vmaxpd xmm12,xmm8,oword [0x0000006b + r14 * 8]'),
    ('VMAXPD 4', 'c5395fe5', 'vmaxpd xmm12,xmm8,xmm5', 'vmaxpd xmm12,xmm8,xmm5'),
    ('VMAXPD 5', 'c5155f04254a4a4a4a', 'vmaxpd ymm8,ymm13,yword [0x4a4a4a4a]', 'vmaxpd ymm8,ymm13,yword [0x4a4a4a4a]'),
    ('VMAXPD 6', 'c441155f0424', 'vmaxpd ymm8,ymm13,yword [r12]', 'vmaxpd ymm8,ymm13,yword [r12]'),
    ('VMAXPD 7', 'c441155f87f1000000', 'vmaxpd ymm8,ymm13,yword [r15 + 241]', 'vmaxpd ymm8,ymm13,yword [r15 + 241]'),
    ('VMAXPD 8', 'c421155f04fdf1000000', 'vmaxpd ymm8,ymm13,yword [0x000000f1 + r15 * 8]', 'vmaxpd ymm8,ymm13,yword [0x000000f1 + r15 * 8]'),
    ('VMAXPD 9', 'c5155fc3', 'vmaxpd ymm8,ymm13,ymm3', 'vmaxpd ymm8,ymm13,ymm3'),
    ('VPSRLD 0', 'c4c121d2d3', 'vpsrld xmm2,xmm11,xmm11', 'vpsrld xmm2,xmm11,xmm11'),
    ('VPSRLD 1', 'c5a1d214254a4a4a4a', 'vpsrld xmm2,xmm11,oword [0x4a4a4a4a]', 'vpsrld xmm2,xmm11,oword [0x4a4a4a4a]'),
    ('VPSRLD 2', 'c5a1d212', 'vpsrld xmm2,xmm11,oword [rdx]', 'vpsrld xmm2,xmm11,oword [rdx]'),
    ('VPSRLD 3', 'c5a1d25001', 'vpsrld xmm2,xmm11,oword [rax + 1]', 'vpsrld xmm2,xmm11,oword [rax + 1]'),
    ('VPSRLD 4', 'c4a121d214cd01000000', 'vpsrld xmm2,xmm11,oword [0x00000001 + r9 * 8]', 'vpsrld xmm2,xmm11,oword [0x00000001 + r9 * 8]'),
    ('VPSRLD 5', 'c565d2cb', 'vpsrld ymm9,ymm3,xmm3', 'vpsrld ymm9,ymm3,xmm3'),
    ('VPSRLQ 0', 'c44179d3fc', 'vpsrlq xmm15,xmm0,xmm12', 'vpsrlq xmm15,xmm0,xmm12'),
    ('VPSRLQ 1', 'c579d33c254a4a4a4a', 'vpsrlq xmm15,xmm0,oword [0x4a4a4a4a]', 'vpsrlq xmm15,xmm0,oword [0x4a4a4a4a]'),
    ('VPSRLQ 2', 'c44179d339', 'vpsrlq xmm15,xmm0,oword [r9]', 'vpsrlq xmm15,xmm0,oword [r9]'),
    ('VPSRLQ 3', 'c44179d37e3f', 'vpsrlq xmm15,xmm0,oword [r14 + 63]', 'vpsrlq xmm15,xmm0,oword [r14 + 63]'),
    ('VPSRLQ 4', 'c42179d33cf53f000000', 'vpsrlq xmm15,xmm0,oword [0x0000003f + r14 * 8]', 'vpsrlq xmm15,xmm0,oword [0x0000003f + r14 * 8]'),
    ('VPSRLQ 5', 'c515d3ed', 'vpsrlq ymm13,ymm13,xmm5', 'vpsrlq ymm13,ymm13,xmm5'),
    ('VPADDQ 0', 'c571d4c7', 'vpaddq xmm8,xmm1,xmm7', 'vpaddq xmm8,xmm1,xmm7'),
    ('VPADDQ 1', 'c571d404254a4a4a4a', 'vpaddq xmm8,xmm1,oword [0x4a4a4a4a]', 'vpaddq xmm8,xmm1,oword [0x4a4a4a4a]'),
    ('VPADDQ 2', 'c571d402', 'vpaddq xmm8,xmm1,oword [rdx]', 'vpaddq xmm8,xmm1,oword [rdx]'),
    ('VPADDQ 3', 'c44171d44602', 'vpaddq xmm8,xmm1,oword [r14 + 2]', 'vpaddq xmm8,xmm1,oword [r14 + 2]'),
    ('VPADDQ 4', 'c571d404d502000000', 'vpaddq xmm8,xmm1,oword [0x00000002 + rdx * 8]', 'vpaddq xmm8,xmm1,oword [0x00000002 + rdx * 8]'),
    ('VPADDQ 5', 'c5d5d4eb', 'vpaddq ymm5,ymm5,ymm3', 'vpaddq ymm5,ymm5,ymm3'),
    ('VPADDQ 6', 'c5d5d42c254a4a4a4a', 'vpaddq ymm5,ymm5,yword [0x4a4a4a4a]', 'vpaddq ymm5,ymm5,yword [0x4a4a4a4a]'),
    ('VPADDQ 7', 'c4c155d428', 'vpaddq ymm5,ymm5,yword [r8]', 'vpaddq ymm5,ymm5,yword [r8]'),
    ('VPADDQ 8', 'c5d5d4abc3000000', 'vpaddq ymm5,ymm5,yword [rbx + 195]', 'vpaddq ymm5,ymm5,yword [rbx + 195]'),
    ('VPADDQ 9', 'c4a155d42cf5c3000000', 'vpaddq ymm5,ymm5,yword [0x000000c3 + r14 * 8]', 'vpaddq ymm5,ymm5,yword [0x000000c3 + r14 * 8]'),
    ('VPADDD 0', 'c4c131fee6', 'vpaddd xmm4,xmm9,xmm14', 'vpaddd xmm4,xmm9,xmm14'),
    ('VPADDD 1', 'c5b1fe24254a4a4a4a', 'vpaddd xmm4,xmm9,oword [0x4a4a4a4a]', 'vpaddd xmm4,xmm9,oword [0x4a4a4a4a]'),
    ('VPADDD 2', 'c4c131fe21', 'vpaddd xmm4,xmm9,oword [r9]', 'vpaddd xmm4,xmm9,oword [r9]'),
    ('VPADDD 3', 'c5b1fe603a', 'vpaddd xmm4,xmm9,oword [rax + 58]', 'vpaddd xmm4,xmm9,oword [rax + 58]'),
    ('VPADDD 4', 'c4a131fe24c53a000000', 'vpaddd xmm4,xmm9,oword [0x0000003a + r8 * 8]', 'vpaddd xmm4,xmm9,oword [0x0000003a + r8 * 8]'),
    ('VPADDD 5', 'c4415dfef7', 'vpaddd ymm14,ymm4,ymm15', 'vpaddd ymm14,ymm4,ymm15'),
    ('VPADDD 6', 'c55dfe34254a4a4a4a', 'vpaddd ymm14,ymm4,yword [0x4a4a4a4a]', 'vpaddd ymm14,ymm4,yword [0x4a4a4a4a]'),
    ('VPADDD 7', 'c4415dfe30', 'vpaddd ymm14,ymm4,yword [r8]', 'vpaddd ymm14,ymm4,yword [r8]'),
    ('VPADDD 8', 'c4415dfe7124', 'vpaddd ymm14,ymm4,yword [r9 + 36]', 'vpaddd ymm14,ymm4,yword [r9 + 36]'),
    ('VPADDD 9', 'c55dfe34c524000000', 'vpaddd ymm14,ymm4,yword [0x00000024 + rax * 8]', 'vpaddd ymm14,ymm4,yword [0x00000024 + rax * 8]'),
    ('VPADDW 0', 'c571fdeb', 'vpaddw xmm13,xmm1,xmm3', 'vpaddw xmm13,xmm1,xmm3'),
    ('VPADDW 1', 'c571fd2c254a4a4a4a', 'vpaddw xmm13,xmm1,oword [0x4a4a4a4a]', 'vpaddw xmm13,xmm1,oword [0x4a4a4a4a]'),
    ('VPADDW 2', 'c44171fd2a', 'vpaddw xmm13,xmm1,oword [r10]', 'vpaddw xmm13,xmm1,oword [r10]'),
    ('VPADDW 3', 'c44171fdac24fd000000', 'vpaddw xmm13,xmm1,oword [r12 + 253]', 'vpaddw xmm13,xmm1,oword [r12 + 253]'),
    ('VPADDW 4', 'c42171fd2ce5fd000000', 'vpaddw xmm13,xmm1,oword [0x000000fd + r12 * 8]', 'vpaddw xmm13,xmm1,oword [0x000000fd + r12 * 8]'),
    ('VPADDW 5', 'c44175fdf8', 'vpaddw ymm15,ymm1,ymm8', 'vpaddw ymm15,ymm1,ymm8'),
    ('VPADDW 6', 'c575fd3c254a4a4a4a', 'vpaddw ymm15,ymm1,yword [0x4a4a4a4a]', 'vpaddw ymm15,ymm1,yword [0x4a4a4a4a]'),
    ('VPADDW 7', 'c44175fd39', 'vpaddw ymm15,ymm1,yword [r9]', 'vpaddw ymm15,ymm1,yword [r9]'),
    ('VPADDW 8', 'c575fdbae3000000', 'vpaddw ymm15,ymm1,yword [rdx + 227]', 'vpaddw ymm15,ymm1,yword [rdx + 227]'),
    ('VPADDW 9', 'c42175fd3cc5e3000000', 'vpaddw ymm15,ymm1,yword [0x000000e3 + r8 * 8]', 'vpaddw ymm15,ymm1,yword [0x000000e3 + r8 * 8]'),
    ('VPADDB 0', 'c5b1fcc2', 'vpaddb xmm0,xmm9,xmm2', 'vpaddb xmm0,xmm9,xmm2'),
    ('VPADDB 1', 'c5b1fc04254a4a4a4a', 'vpaddb xmm0,xmm9,oword [0x4a4a4a4a]', 'vpaddb xmm0,xmm9,oword [0x4a4a4a4a]'),
    ('VPADDB 2', 'c4c131fc02', 'vpaddb xmm0,xmm9,oword [r10]', 'vpaddb xmm0,xmm9,oword [r10]'),
    ('VPADDB 3', 'c4c131fc869b000000', 'vpaddb xmm0,xmm9,oword [r14 + 155]', 'vpaddb xmm0,xmm9,oword [r14 + 155]'),
    ('VPADDB 4', 'c4a131fc04ed9b000000', 'vpaddb xmm0,xmm9,oword [0x0000009b + r13 * 8]', 'vpaddb xmm0,xmm9,oword [0x0000009b + r13 * 8]'),
    ('VPADDB 5', 'c4c115fce7', 'vpaddb ymm4,ymm13,ymm15', 'vpaddb ymm4,ymm13,ymm15'),
    ('VPADDB 6', 'c595fc24254a4a4a4a', 'vpaddb ymm4,ymm13,yword [0x4a4a4a4a]', 'vpaddb ymm4,ymm13,yword [0x4a4a4a4a]'),
    ('VPADDB 7', 'c595fc21', 'vpaddb ymm4,ymm13,yword [rcx]', 'vpaddb ymm4,ymm13,yword [rcx]'),
    ('VPADDB 8', 'c4c115fc642437', 'vpaddb ymm4,ymm13,yword [r12 + 55]', 'vpaddb ymm4,ymm13,yword [r12 + 55]'),
    ('VPADDB 9', 'c595fc24cd37000000', 'vpaddb ymm4,ymm13,yword [0x00000037 + rcx * 8]', 'vpaddb ymm4,ymm13,yword [0x00000037 + rcx * 8]'),
    ('VPSUBB 0', 'c521f8f3', 'vpsubb xmm14,xmm11,xmm3', 'vpsubb xmm14,xmm11,xmm3'),
    ('VPSUBB 1', 'c521f834254a4a4a4a', 'vpsubb xmm14,xmm11,oword [0x4a4a4a4a]', 'vpsubb xmm14,xmm11,oword [0x4a4a4a4a]'),
    ('VPSUBB 2', 'c44121f836', 'vpsubb xmm14,xmm11,oword [r14]', 'vpsubb xmm14,xmm11,oword [r14]'),
    ('VPSUBB 3', 'c44121f8b0be000000', 'vpsubb xmm14,xmm11,oword [r8 + 190]', 'vpsubb xmm14,xmm11,oword [r8 + 190]'),
    ('VPSUBB 4', 'c521f834ddbe000000', 'vpsubb xmm14,xmm11,oword [0x000000be + rbx * 8]', 'vpsubb xmm14,xmm11,oword [0x000000be + rbx * 8]'),
    ('VPSUBB 5', 'c4411df8e1', 'vpsubb ymm12,ymm12,ymm9', 'vpsubb ymm12,ymm12,ymm9'),
    ('VPSUBB 6', 'c51df824254a4a4a4a', 'vpsubb ymm12,ymm12,yword [0x4a4a4a4a]', 'vpsubb ymm12,ymm12,yword [0x4a4a4a4a]'),
    ('VPSUBB 7', 'c51df823', 'vpsubb ymm12,ymm12,yword [rbx]', 'vpsubb ymm12,ymm12,yword [rbx]'),
    ('VPSUBB 8', 'c4411df86562', 'vpsubb ymm12,ymm12,yword [r13 + 98]', 'vpsubb ymm12,ymm12,yword [r13 + 98]'),
    ('VPSUBB 9', 'c51df824cd62000000', 'vpsubb ymm12,ymm12,yword [0x00000062 + rcx * 8]', 'vpsubb ymm12,ymm12,yword [0x00000062 + rcx * 8]'),
    ('VPSUBW 0', 'c519f9c9', 'vpsubw xmm9,xmm12,xmm1', 'vpsubw xmm9,xmm12,xmm1'),
    ('VPSUBW 1', 'c519f90c254a4a4a4a', 'vpsubw xmm9,xmm12,oword [0x4a4a4a4a]', 'vpsubw xmm9,xmm12,oword [0x4a4a4a4a]'),
    ('VPSUBW 2', 'c44119f94d00', 'vpsubw xmm9,xmm12,oword [r13]', 'vpsubw xmm9,xmm12,oword [r13]'),
    ('VPSUBW 3', 'c44119f94e3b', 'vpsubw xmm9,xmm12,oword [r14 + 59]', 'vpsubw xmm9,xmm12,oword [r14 + 59]'),
    ('VPSUBW 4', 'c42119f90ccd3b000000', 'vpsubw xmm9,xmm12,oword [0x0000003b + r9 * 8]', 'vpsubw xmm9,xmm12,oword [0x0000003b + r9 * 8]'),
    ('VPSUBW 5', 'c5a5f9eb', 'vpsubw ymm5,ymm11,ymm3', 'vpsubw ymm5,ymm11,ymm3'),
    ('VPSUBW 6', 'c5a5f92c254a4a4a4a', 'vpsubw ymm5,ymm11,yword [0x4a4a4a4a]', 'vpsubw ymm5,ymm11,yword [0x4a4a4a4a]'),
    ('VPSUBW 7', 'c4c125f96d00', 'vpsubw ymm5,ymm11,yword [r13]', 'vpsubw ymm5,ymm11,yword [r13]'),
    ('VPSUBW 8', 'c4c125f9afc4000000', 'vpsubw ymm5,ymm11,yword [r15 + 196]', 'vpsubw ymm5,ymm11,yword [r15 + 196]'),
    ('VPSUBW 9', 'c5a5f92cc5c4000000', 'vpsubw ymm5,ymm11,yword [0x000000c4 + rax * 8]', 'vpsubw ymm5,ymm11,yword [0x000000c4 + rax * 8]'),
    ('VPSUBD 0', 'c4c101fafd', 'vpsubd xmm7,xmm15,xmm13', 'vpsubd xmm7,xmm15,xmm13'),
    ('VPSUBD 1', 'c581fa3c254a4a4a4a', 'vpsubd xmm7,xmm15,oword [0x4a4a4a4a]', 'vpsubd xmm7,xmm15,oword [0x4a4a4a4a]'),
    ('VPSUBD 2', 'c4c101fa7d00', 'vpsubd xmm7,xmm15,oword [r13]', 'vpsubd xmm7,xmm15,oword [r13]'),
    ('VPSUBD 3', 'c4c101fabfb2000000', 'vpsubd xmm7,xmm15,oword [r15 + 178]', 'vpsubd xmm7,xmm15,oword [r15 + 178]'),
    ('VPSUBD 5', 'c4415dfae0', 'vpsubd ymm12,ymm4,ymm8', 'vpsubd ymm12,ymm4,ymm8'),
    ('VPSUBD 6', 'c55dfa24254a4a4a4a', 'vpsubd ymm12,ymm4,yword [0x4a4a4a4a]', 'vpsubd ymm12,ymm4,yword [0x4a4a4a4a]'),
    ('VPSUBD 7', 'c4415dfa2424', 'vpsubd ymm12,ymm4,yword [r12]', 'vpsubd ymm12,ymm4,yword [r12]'),
    ('VPSUBD 8', 'c4415dfa655f', 'vpsubd ymm12,ymm4,yword [r13 + 95]', 'vpsubd ymm12,ymm4,yword [r13 + 95]'),
    ('VPSUBQ 0', 'c44151fbd6', 'vpsubq xmm10,xmm5,xmm14', 'vpsubq xmm10,xmm5,xmm14'),
    ('VPSUBQ 1', 'c551fb14254a4a4a4a', 'vpsubq xmm10,xmm5,oword [0x4a4a4a4a]', 'vpsubq xmm10,xmm5,oword [0x4a4a4a4a]'),
    ('VPSUBQ 2', 'c44151fb11', 'vpsubq xmm10,xmm5,oword [r9]', 'vpsubq xmm10,xmm5,oword [r9]'),
    ('VPSUBQ 3', 'c44151fb5623', 'vpsubq xmm10,xmm5,oword [r14 + 35]', 'vpsubq xmm10,xmm5,oword [r14 + 35]'),
    ('VPSUBQ 5', 'c58dfbf4', 'vpsubq ymm6,ymm14,ymm4', 'vpsubq ymm6,ymm14,ymm4'),
    ('VPSUBQ 6', 'c58dfb34254a4a4a4a', 'vpsubq ymm6,ymm14,yword [0x4a4a4a4a]', 'vpsubq ymm6,ymm14,yword [0x4a4a4a4a]'),
    ('VPSUBQ 7', 'c4c10dfb36', 'vpsubq ymm6,ymm14,yword [r14]', 'vpsubq ymm6,ymm14,yword [r14]'),
    ('VPSUBQ 8', 'c4c10dfbb0e3000000', 'vpsubq ymm6,ymm14,yword [r8 + 227]', 'vpsubq ymm6,ymm14,yword [r8 + 227]'),
    ('VPMULLW 0', 'c44131d5d5', 'vpmullw xmm10,xmm9,xmm13', 'vpmullw xmm10,xmm9,xmm13'),
    ('VPMULLW 1', 'c531d514254a4a4a4a', 'vpmullw xmm10,xmm9,oword [0x4a4a4a4a]', 'vpmullw xmm10,xmm9,oword [0x4a4a4a4a]'),
    ('VPMULLW 2', 'c531d511', 'vpmullw xmm10,xmm9,oword [rcx]', 'vpmullw xmm10,xmm9,oword [rcx]'),
    ('VPMULLW 3', 'c44131d591c0000000', 'vpmullw xmm10,xmm9,oword [r9 + 192]', 'vpmullw xmm10,xmm9,oword [r9 + 192]'),
    ('VPMULLW 5', 'c595d5ff', 'vpmullw ymm7,ymm13,ymm7', 'vpmullw ymm7,ymm13,ymm7'),
    ('VPMULLW 6', 'c595d53c254a4a4a4a', 'vpmullw ymm7,ymm13,yword [0x4a4a4a4a]', 'vpmullw ymm7,ymm13,yword [0x4a4a4a4a]'),
    ('VPMULLW 7', 'c4c115d538', 'vpmullw ymm7,ymm13,yword [r8]', 'vpmullw ymm7,ymm13,yword [r8]'),
    ('VPMULLW 8', 'c595d5787f', 'vpmullw ymm7,ymm13,yword [rax + 127]', 'vpmullw ymm7,ymm13,yword [rax + 127]'),
    ('VPMINUB 0', 'c44121daf3', 'vpminub xmm14,xmm11,xmm11', 'vpminub xmm14,xmm11,xmm11'),
    ('VPMINUB 1', 'c521da34254a4a4a4a', 'vpminub xmm14,xmm11,oword [0x4a4a4a4a]', 'vpminub xmm14,xmm11,oword [0x4a4a4a4a]'),
    ('VPMINUB 2', 'c44121da32', 'vpminub xmm14,xmm11,oword [r10]', 'vpminub xmm14,xmm11,oword [r10]'),
    ('VPMINUB 3', 'c44121da742412', 'vpminub xmm14,xmm11,oword [r12 + 18]', 'vpminub xmm14,xmm11,oword [r12 + 18]'),
    ('VPMINUB 4', 'c42121da34ed12000000', 'vpminub xmm14,xmm11,oword [0x00000012 + r13 * 8]', 'vpminub xmm14,xmm11,oword [0x00000012 + r13 * 8]'),
    ('VPMINUB 5', 'c4c15ddaf9', 'vpminub ymm7,ymm4,ymm9', 'vpminub ymm7,ymm4,ymm9'),
    ('VPMINUB 6', 'c5ddda3c254a4a4a4a', 'vpminub ymm7,ymm4,yword [0x4a4a4a4a]', 'vpminub ymm7,ymm4,yword [0x4a4a4a4a]'),
    ('VPMINUB 7', 'c4c15dda3b', 'vpminub ymm7,ymm4,yword [r11]', 'vpminub ymm7,ymm4,yword [r11]'),
    ('VPMINUB 8', 'c4c15dda7d72', 'vpminub ymm7,ymm4,yword [r13 + 114]', 'vpminub ymm7,ymm4,yword [r13 + 114]'),
    ('VPAND 0', 'c44169dbfe', 'vpand xmm15,xmm2,xmm14', 'vpand xmm15,xmm2,xmm14'),
    ('VPAND 1', 'c569db3c254a4a4a4a', 'vpand xmm15,xmm2,oword [0x4a4a4a4a]', 'vpand xmm15,xmm2,oword [0x4a4a4a4a]'),
    ('VPAND 2', 'c44169db3e', 'vpand xmm15,xmm2,oword [r14]', 'vpand xmm15,xmm2,oword [r14]'),
    ('VPAND 3', 'c44169db7c2439', 'vpand xmm15,xmm2,oword [r12 + 57]', 'vpand xmm15,xmm2,oword [r12 + 57]'),
    ('VPAND 5', 'c5bddbe1', 'vpand ymm4,ymm8,ymm1', 'vpand ymm4,ymm8,ymm1'),
    ('VPAND 6', 'c5bddb24254a4a4a4a', 'vpand ymm4,ymm8,yword [0x4a4a4a4a]', 'vpand ymm4,ymm8,yword [0x4a4a4a4a]'),
    ('VPAND 7', 'c4c13ddb27', 'vpand ymm4,ymm8,yword [r15]', 'vpand ymm4,ymm8,yword [r15]'),
    ('VPAND 8', 'c4c13ddb6539', 'vpand ymm4,ymm8,yword [r13 + 57]', 'vpand ymm4,ymm8,yword [r13 + 57]'),
    ('VPSUBUSB 0', 'c44119d8cb', 'vpsubusb xmm9,xmm12,xmm11', 'vpsubusb xmm9,xmm12,xmm11'),
    ('VPSUBUSB 1', 'c519d80c254a4a4a4a', 'vpsubusb xmm9,xmm12,oword [0x4a4a4a4a]', 'vpsubusb xmm9,xmm12,oword [0x4a4a4a4a]'),
    ('VPSUBUSB 2', 'c519d808', 'vpsubusb xmm9,xmm12,oword [rax]', 'vpsubusb xmm9,xmm12,oword [rax]'),
    ('VPSUBUSB 3', 'c44119d888e3000000', 'vpsubusb xmm9,xmm12,oword [r8 + 227]', 'vpsubusb xmm9,xmm12,oword [r8 + 227]'),
    ('VPSUBUSB 5', 'c4414dd8fa', 'vpsubusb ymm15,ymm6,ymm10', 'vpsubusb ymm15,ymm6,ymm10'),
    ('VPSUBUSB 6', 'c54dd83c254a4a4a4a', 'vpsubusb ymm15,ymm6,yword [0x4a4a4a4a]', 'vpsubusb ymm15,ymm6,yword [0x4a4a4a4a]'),
    ('VPSUBUSB 7', 'c4414dd83c24', 'vpsubusb ymm15,ymm6,yword [r12]', 'vpsubusb ymm15,ymm6,yword [r12]'),
    ('VPSUBUSB 8', 'c4414dd8b9d5000000', 'vpsubusb ymm15,ymm6,yword [r9 + 213]', 'vpsubusb ymm15,ymm6,yword [r9 + 213]'),
    ('VPSUBUSW 0', 'c44139d9e0', 'vpsubusw xmm12,xmm8,xmm8', 'vpsubusw xmm12,xmm8,xmm8'),
    ('VPSUBUSW 1', 'c539d924254a4a4a4a', 'vpsubusw xmm12,xmm8,oword [0x4a4a4a4a]', 'vpsubusw xmm12,xmm8,oword [0x4a4a4a4a]'),
    ('VPSUBUSW 2', 'c44139d920', 'vpsubusw xmm12,xmm8,oword [r8]', 'vpsubusw xmm12,xmm8,oword [r8]'),
    ('VPSUBUSW 3', 'c44139d96545', 'vpsubusw xmm12,xmm8,oword [r13 + 69]', 'vpsubusw xmm12,xmm8,oword [r13 + 69]'),
    ('VPSUBUSW 5', 'c44125d9cc', 'vpsubusw ymm9,ymm11,ymm12', 'vpsubusw ymm9,ymm11,ymm12'),
    ('VPSUBUSW 6', 'c525d90c254a4a4a4a', 'vpsubusw ymm9,ymm11,yword [0x4a4a4a4a]', 'vpsubusw ymm9,ymm11,yword [0x4a4a4a4a]'),
    ('VPSUBUSW 7', 'c44125d90c24', 'vpsubusw ymm9,ymm11,yword [r12]', 'vpsubusw ymm9,ymm11,yword [r12]'),
    ('VPSUBUSW 8', 'c44125d94b68', 'vpsubusw ymm9,ymm11,yword [r11 + 104]', 'vpsubusw ymm9,ymm11,yword [r11 + 104]'),
    ('VPADDUSB 0', 'c541dcf7', 'vpaddusb xmm14,xmm7,xmm7', 'vpaddusb xmm14,xmm7,xmm7'),
    ('VPADDUSB 1', 'c541dc34254a4a4a4a', 'vpaddusb xmm14,xmm7,oword [0x4a4a4a4a]', 'vpaddusb xmm14,xmm7,oword [0x4a4a4a4a]'),
    ('VPADDUSB 2', 'c44141dc36', 'vpaddusb xmm14,xmm7,oword [r14]', 'vpaddusb xmm14,xmm7,oword [r14]'),
    ('VPADDUSB 3', 'c44141dc7212', 'vpaddusb xmm14,xmm7,oword [r10 + 18]', 'vpaddusb xmm14,xmm7,oword [r10 + 18]'),
    ('VPADDUSB 5', 'c5c5dcd9', 'vpaddusb ymm3,ymm7,ymm1', 'vpaddusb ymm3,ymm7,ymm1'),
    ('VPADDUSB 6', 'c5c5dc1c254a4a4a4a', 'vpaddusb ymm3,ymm7,yword [0x4a4a4a4a]', 'vpaddusb ymm3,ymm7,yword [0x4a4a4a4a]'),
    ('VPADDUSB 7', 'c4c145dc18', 'vpaddusb ymm3,ymm7,yword [r8]', 'vpaddusb ymm3,ymm7,yword [r8]'),
    ('VPADDUSB 8', 'c5c5dc594b', 'vpaddusb ymm3,ymm7,yword [rcx + 75]', 'vpaddusb ymm3,ymm7,yword [rcx + 75]'),
    ('VPADDUSW 0', 'c44141dde1', 'vpaddusw xmm12,xmm7,xmm9', 'vpaddusw xmm12,xmm7,xmm9'),
    ('VPADDUSW 1', 'c541dd24254a4a4a4a', 'vpaddusw xmm12,xmm7,oword [0x4a4a4a4a]', 'vpaddusw xmm12,xmm7,oword [0x4a4a4a4a]'),
    ('VPADDUSW 2', 'c44141dd26', 'vpaddusw xmm12,xmm7,oword [r14]', 'vpaddusw xmm12,xmm7,oword [r14]'),
    ('VPADDUSW 3', 'c541dd6112', 'vpaddusw xmm12,xmm7,oword [rcx + 18]', 'vpaddusw xmm12,xmm7,oword [rcx + 18]'),
    ('VPADDUSW 5', 'c54ddde1', 'vpaddusw ymm12,ymm6,ymm1', 'vpaddusw ymm12,ymm6,ymm1'),
    ('VPADDUSW 6', 'c54ddd24254a4a4a4a', 'vpaddusw ymm12,ymm6,yword [0x4a4a4a4a]', 'vpaddusw ymm12,ymm6,yword [0x4a4a4a4a]'),
    ('VPADDUSW 7', 'c4414ddd22', 'vpaddusw ymm12,ymm6,yword [r10]', 'vpaddusw ymm12,ymm6,yword [r10]'),
    ('VPADDUSW 8', 'c4414ddda1d8000000', 'vpaddusw ymm12,ymm6,yword [r9 + 216]', 'vpaddusw ymm12,ymm6,yword [r9 + 216]'),
    ('VPADDSB 0', 'c581ecc1', 'vpaddsb xmm0,xmm15,xmm1', 'vpaddsb xmm0,xmm15,xmm1'),
    ('VPADDSB 1', 'c581ec04254a4a4a4a', 'vpaddsb xmm0,xmm15,oword [0x4a4a4a4a]', 'vpaddsb xmm0,xmm15,oword [0x4a4a4a4a]'),
    ('VPADDSB 2', 'c581ec00', 'vpaddsb xmm0,xmm15,oword [rax]', 'vpaddsb xmm0,xmm15,oword [rax]'),
    ('VPADDSB 3', 'c4c101ec80e9000000', 'vpaddsb xmm0,xmm15,oword [r8 + 233]', 'vpaddsb xmm0,xmm15,oword [r8 + 233]'),
    ('VPADDSB 5', 'c4c135ecda', 'vpaddsb ymm3,ymm9,ymm10', 'vpaddsb ymm3,ymm9,ymm10'),
    ('VPADDSB 6', 'c5b5ec1c254a4a4a4a', 'vpaddsb ymm3,ymm9,yword [0x4a4a4a4a]', 'vpaddsb ymm3,ymm9,yword [0x4a4a4a4a]'),
    ('VPADDSB 7', 'c4c135ec1c24', 'vpaddsb ymm3,ymm9,yword [r12]', 'vpaddsb ymm3,ymm9,yword [r12]'),
    ('VPADDSB 8', 'c4c135ec5b7e', 'vpaddsb ymm3,ymm9,yword [r11 + 126]', 'vpaddsb ymm3,ymm9,yword [r11 + 126]'),
    ('VPADDSW 0', 'c44121edd3', 'vpaddsw xmm10,xmm11,xmm11', 'vpaddsw xmm10,xmm11,xmm11'),
    ('VPADDSW 1', 'c521ed14254a4a4a4a', 'vpaddsw xmm10,xmm11,oword [0x4a4a4a4a]', 'vpaddsw xmm10,xmm11,oword [0x4a4a4a4a]'),
    ('VPADDSW 2', 'c44121ed17', 'vpaddsw xmm10,xmm11,oword [r15]', 'vpaddsw xmm10,xmm11,oword [r15]'),
    ('VPADDSW 3', 'c44121ed5138', 'vpaddsw xmm10,xmm11,oword [r9 + 56]', 'vpaddsw xmm10,xmm11,oword [r9 + 56]'),
    ('VPADDSW 5', 'c525edf6', 'vpaddsw ymm14,ymm11,ymm6', 'vpaddsw ymm14,ymm11,ymm6'),
    ('VPADDSW 6', 'c525ed34254a4a4a4a', 'vpaddsw ymm14,ymm11,yword [0x4a4a4a4a]', 'vpaddsw ymm14,ymm11,yword [0x4a4a4a4a]'),
    ('VPADDSW 7', 'c525ed31', 'vpaddsw ymm14,ymm11,yword [rcx]', 'vpaddsw ymm14,ymm11,yword [rcx]'),
    ('VPADDSW 8', 'c44125edb6f2000000', 'vpaddsw ymm14,ymm11,yword [r14 + 242]', 'vpaddsw ymm14,ymm11,yword [r14 + 242]'),
    ('VPMAXUB 0', 'c529def5', 'vpmaxub xmm14,xmm10,xmm5', 'vpmaxub xmm14,xmm10,xmm5'),
    ('VPMAXUB 1', 'c529de34254a4a4a4a', 'vpmaxub xmm14,xmm10,oword [0x4a4a4a4a]', 'vpmaxub xmm14,xmm10,oword [0x4a4a4a4a]'),
    ('VPMAXUB 2', 'c44129de7500', 'vpmaxub xmm14,xmm10,oword [r13]', 'vpmaxub xmm14,xmm10,oword [r13]'),
    ('VPMAXUB 3', 'c44129de722b', 'vpmaxub xmm14,xmm10,oword [r10 + 43]', 'vpmaxub xmm14,xmm10,oword [r10 + 43]'),
    ('VPMAXUB 5', 'c5eddec5', 'vpmaxub ymm0,ymm2,ymm5', 'vpmaxub ymm0,ymm2,ymm5'),
    ('VPMAXUB 6', 'c5edde04254a4a4a4a', 'vpmaxub ymm0,ymm2,yword [0x4a4a4a4a]', 'vpmaxub ymm0,ymm2,yword [0x4a4a4a4a]'),
    ('VPMAXUB 7', 'c4c16dde00', 'vpmaxub ymm0,ymm2,yword [r8]', 'vpmaxub ymm0,ymm2,yword [r8]'),
    ('VPMAXUB 8', 'c4c16dde4337', 'vpmaxub ymm0,ymm2,yword [r11 + 55]', 'vpmaxub ymm0,ymm2,yword [r11 + 55]'),
    ('VPANDN 0', 'c509dffe', 'vpandn xmm15,xmm14,xmm6', 'vpandn xmm15,xmm14,xmm6'),
    ('VPANDN 1', 'c509df3c254a4a4a4a', 'vpandn xmm15,xmm14,oword [0x4a4a4a4a]', 'vpandn xmm15,xmm14,oword [0x4a4a4a4a]'),
    ('VPANDN 2', 'c44109df3a', 'vpandn xmm15,xmm14,oword [r10]', 'vpandn xmm15,xmm14,oword [r10]'),
    ('VPANDN 3', 'c509dfbaf9000000', 'vpandn xmm15,xmm14,oword [rdx + 249]', 'vpandn xmm15,xmm14,oword [rdx + 249]'),
    ('VPANDN 5', 'c4410ddfc7', 'vpandn ymm8,ymm14,ymm15', 'vpandn ymm8,ymm14,ymm15'),
    ('VPANDN 6', 'c50ddf04254a4a4a4a', 'vpandn ymm8,ymm14,yword [0x4a4a4a4a]', 'vpandn ymm8,ymm14,yword [0x4a4a4a4a]'),
    ('VPANDN 7', 'c4410ddf01', 'vpandn ymm8,ymm14,yword [r9]', 'vpandn ymm8,ymm14,yword [r9]'),
    ('VPANDN 8', 'c50ddf4203', 'vpandn ymm8,ymm14,yword [rdx + 3]', 'vpandn ymm8,ymm14,yword [rdx + 3]'),
    ('VPAVGB 0', 'c4c139e0c1', 'vpavgb xmm0,xmm8,xmm9', 'vpavgb xmm0,xmm8,xmm9'),
    ('VPAVGB 1', 'c5b9e004254a4a4a4a', 'vpavgb xmm0,xmm8,oword [0x4a4a4a4a]', 'vpavgb xmm0,xmm8,oword [0x4a4a4a4a]'),
    ('VPAVGB 2', 'c4c139e001', 'vpavgb xmm0,xmm8,oword [r9]', 'vpavgb xmm0,xmm8,oword [r9]'),
    ('VPAVGB 3', 'c4c139e04763', 'vpavgb xmm0,xmm8,oword [r15 + 99]', 'vpavgb xmm0,xmm8,oword [r15 + 99]'),
    ('VPAVGB 5', 'c5e5e0fc', 'vpavgb ymm7,ymm3,ymm4', 'vpavgb ymm7,ymm3,ymm4'),
    ('VPAVGB 6', 'c5e5e03c254a4a4a4a', 'vpavgb ymm7,ymm3,yword [0x4a4a4a4a]', 'vpavgb ymm7,ymm3,yword [0x4a4a4a4a]'),
    ('VPAVGB 7', 'c4c165e03c24', 'vpavgb ymm7,ymm3,yword [r12]', 'vpavgb ymm7,ymm3,yword [r12]'),
    ('VPAVGB 8', 'c4c165e0ba88000000', 'vpavgb ymm7,ymm3,yword [r10 + 136]', 'vpavgb ymm7,ymm3,yword [r10 + 136]'),
    ('VPSRAW 0', 'c501e1f7', 'vpsraw xmm14,xmm15,xmm7', 'vpsraw xmm14,xmm15,xmm7'),
    ('VPSRAW 1', 'c501e134254a4a4a4a', 'vpsraw xmm14,xmm15,oword [0x4a4a4a4a]', 'vpsraw xmm14,xmm15,oword [0x4a4a4a4a]'),
    ('VPSRAW 2', 'c44101e133', 'vpsraw xmm14,xmm15,oword [r11]', 'vpsraw xmm14,xmm15,oword [r11]'),
    ('VPSRAW 3', 'c44101e1734a', 'vpsraw xmm14,xmm15,oword [r11 + 74]', 'vpsraw xmm14,xmm15,oword [r11 + 74]'),
    ('VPSRAW 5', 'c565e1f3', 'vpsraw ymm14,ymm3,xmm3', 'vpsraw ymm14,ymm3,xmm3'),
    ('VPSRAD 0', 'c521e2d4', 'vpsrad xmm10,xmm11,xmm4', 'vpsrad xmm10,xmm11,xmm4'),
    ('VPSRAD 1', 'c521e214254a4a4a4a', 'vpsrad xmm10,xmm11,oword [0x4a4a4a4a]', 'vpsrad xmm10,xmm11,oword [0x4a4a4a4a]'),
    ('VPSRAD 2', 'c44121e216', 'vpsrad xmm10,xmm11,oword [r14]', 'vpsrad xmm10,xmm11,oword [r14]'),
    ('VPSRAD 3', 'c521e25318', 'vpsrad xmm10,xmm11,oword [rbx + 24]', 'vpsrad xmm10,xmm11,oword [rbx + 24]'),
    ('VPSRAD 5', 'c5ade2c2', 'vpsrad ymm0,ymm10,xmm2', 'vpsrad ymm0,ymm10,xmm2'),
    ('VPAVGW 0', 'c579e3cc', 'vpavgw xmm9,xmm0,xmm4', 'vpavgw xmm9,xmm0,xmm4'),
    ('VPAVGW 1', 'c579e30c254a4a4a4a', 'vpavgw xmm9,xmm0,oword [0x4a4a4a4a]', 'vpavgw xmm9,xmm0,oword [0x4a4a4a4a]'),
    ('VPAVGW 2', 'c44179e30f', 'vpavgw xmm9,xmm0,oword [r15]', 'vpavgw xmm9,xmm0,oword [r15]'),
    ('VPAVGW 3', 'c44179e38ed7000000', 'vpavgw xmm9,xmm0,oword [r14 + 215]', 'vpavgw xmm9,xmm0,oword [r14 + 215]'),
    ('VPAVGW 5', 'c4412de3c2', 'vpavgw ymm8,ymm10,ymm10', 'vpavgw ymm8,ymm10,ymm10'),
    ('VPAVGW 6', 'c52de304254a4a4a4a', 'vpavgw ymm8,ymm10,yword [0x4a4a4a4a]', 'vpavgw ymm8,ymm10,yword [0x4a4a4a4a]'),
    ('VPAVGW 7', 'c4412de302', 'vpavgw ymm8,ymm10,yword [r10]', 'vpavgw ymm8,ymm10,yword [r10]'),
    ('VPAVGW 8', 'c4412de3442474', 'vpavgw ymm8,ymm10,yword [r12 + 116]', 'vpavgw ymm8,ymm10,yword [r12 + 116]'),
    ('VPMULHUW 0', 'c44111e4da', 'vpmulhuw xmm11,xmm13,xmm10', 'vpmulhuw xmm11,xmm13,xmm10'),
    ('VPMULHUW 1', 'c511e41c254a4a4a4a', 'vpmulhuw xmm11,xmm13,oword [0x4a4a4a4a]', 'vpmulhuw xmm11,xmm13,oword [0x4a4a4a4a]'),
    ('VPMULHUW 2', 'c44111e41a', 'vpmulhuw xmm11,xmm13,oword [r10]', 'vpmulhuw xmm11,xmm13,oword [r10]'),
    ('VPMULHUW 3', 'c44111e45e61', 'vpmulhuw xmm11,xmm13,oword [r14 + 97]', 'vpmulhuw xmm11,xmm13,oword [r14 + 97]'),
    ('VPMULHUW 5', 'c5a5e4e5', 'vpmulhuw ymm4,ymm11,ymm5', 'vpmulhuw ymm4,ymm11,ymm5'),
    ('VPMULHUW 6', 'c5a5e424254a4a4a4a', 'vpmulhuw ymm4,ymm11,yword [0x4a4a4a4a]', 'vpmulhuw ymm4,ymm11,yword [0x4a4a4a4a]'),
    ('VPMULHUW 7', 'c4c125e46500', 'vpmulhuw ymm4,ymm11,yword [r13]', 'vpmulhuw ymm4,ymm11,yword [r13]'),
    ('VPMULHUW 8', 'c4c125e4a2bb000000', 'vpmulhuw ymm4,ymm11,yword [r10 + 187]', 'vpmulhuw ymm4,ymm11,yword [r10 + 187]'),
    ('VPMULHW 0', 'c4c131e5d4', 'vpmulhw xmm2,xmm9,xmm12', 'vpmulhw xmm2,xmm9,xmm12'),
    ('VPMULHW 1', 'c5b1e514254a4a4a4a', 'vpmulhw xmm2,xmm9,oword [0x4a4a4a4a]', 'vpmulhw xmm2,xmm9,oword [0x4a4a4a4a]'),
    ('VPMULHW 2', 'c5b1e510', 'vpmulhw xmm2,xmm9,oword [rax]', 'vpmulhw xmm2,xmm9,oword [rax]'),
    ('VPMULHW 3', 'c4c131e55729', 'vpmulhw xmm2,xmm9,oword [r15 + 41]', 'vpmulhw xmm2,xmm9,oword [r15 + 41]'),
    ('VPMULHW 5', 'c4c10de5de', 'vpmulhw ymm3,ymm14,ymm14', 'vpmulhw ymm3,ymm14,ymm14'),
    ('VPMULHW 6', 'c58de51c254a4a4a4a', 'vpmulhw ymm3,ymm14,yword [0x4a4a4a4a]', 'vpmulhw ymm3,ymm14,yword [0x4a4a4a4a]'),
    ('VPMULHW 7', 'c4c10de51f', 'vpmulhw ymm3,ymm14,yword [r15]', 'vpmulhw ymm3,ymm14,yword [r15]'),
    ('VPMULHW 8', 'c4c10de55876', 'vpmulhw ymm3,ymm14,yword [r8 + 118]', 'vpmulhw ymm3,ymm14,yword [r8 + 118]'),
    ('VPSUBSB 0', 'c4c151e8de', 'vpsubsb xmm3,xmm5,xmm14', 'vpsubsb xmm3,xmm5,xmm14'),
    ('VPSUBSB 1', 'c5d1e81c254a4a4a4a', 'vpsubsb xmm3,xmm5,oword [0x4a4a4a4a]', 'vpsubsb xmm3,xmm5,oword [0x4a4a4a4a]'),
    ('VPSUBSB 2', 'c5d1e81b', 'vpsubsb xmm3,xmm5,oword [rbx]', 'vpsubsb xmm3,xmm5,oword [rbx]'),
    ('VPSUBSB 3', 'c5d1e81a', 'vpsubsb xmm3,xmm5,oword [rdx]', 'vpsubsb xmm3,xmm5,oword [rdx]'),
    ('VPSUBSB 5', 'c44135e8e4', 'vpsubsb ymm12,ymm9,ymm12', 'vpsubsb ymm12,ymm9,ymm12'),
    ('VPSUBSB 6', 'c535e824254a4a4a4a', 'vpsubsb ymm12,ymm9,yword [0x4a4a4a4a]', 'vpsubsb ymm12,ymm9,yword [0x4a4a4a4a]'),
    ('VPSUBSB 7', 'c44135e820', 'vpsubsb ymm12,ymm9,yword [r8]', 'vpsubsb ymm12,ymm9,yword [r8]'),
    ('VPSUBSB 8', 'c44135e86255', 'vpsubsb ymm12,ymm9,yword [r10 + 85]', 'vpsubsb ymm12,ymm9,yword [r10 + 85]'),
    ('VPSUBSW 0', 'c44121e9d2', 'vpsubsw xmm10,xmm11,xmm10', 'vpsubsw xmm10,xmm11,xmm10'),
    ('VPSUBSW 1', 'c521e914254a4a4a4a', 'vpsubsw xmm10,xmm11,oword [0x4a4a4a4a]', 'vpsubsw xmm10,xmm11,oword [0x4a4a4a4a]'),
    ('VPSUBSW 2', 'c44121e910', 'vpsubsw xmm10,xmm11,oword [r8]', 'vpsubsw xmm10,xmm11,oword [r8]'),
    ('VPSUBSW 3', 'c44121e9513b', 'vpsubsw xmm10,xmm11,oword [r9 + 59]', 'vpsubsw xmm10,xmm11,oword [r9 + 59]'),
    ('VPSUBSW 5', 'c515e9c2', 'vpsubsw ymm8,ymm13,ymm2', 'vpsubsw ymm8,ymm13,ymm2'),
    ('VPSUBSW 6', 'c515e904254a4a4a4a', 'vpsubsw ymm8,ymm13,yword [0x4a4a4a4a]', 'vpsubsw ymm8,ymm13,yword [0x4a4a4a4a]'),
    ('VPSUBSW 7', 'c515e903', 'vpsubsw ymm8,ymm13,yword [rbx]', 'vpsubsw ymm8,ymm13,yword [rbx]'),
    ('VPSUBSW 8', 'c44115e94137', 'vpsubsw ymm8,ymm13,yword [r9 + 55]', 'vpsubsw ymm8,ymm13,yword [r9 + 55]'),
    ('VPMINSW 0', 'c44159eac9', 'vpminsw xmm9,xmm4,xmm9', 'vpminsw xmm9,xmm4,xmm9'),
    ('VPMINSW 1', 'c559ea0c254a4a4a4a', 'vpminsw xmm9,xmm4,oword [0x4a4a4a4a]', 'vpminsw xmm9,xmm4,oword [0x4a4a4a4a]'),
    ('VPMINSW 2', 'c44159ea08', 'vpminsw xmm9,xmm4,oword [r8]', 'vpminsw xmm9,xmm4,oword [r8]'),
    ('VPMINSW 3', 'c44159ea4952', 'vpminsw xmm9,xmm4,oword [r9 + 82]', 'vpminsw xmm9,xmm4,oword [r9 + 82]'),
    ('VPMINSW 5', 'c4c13deae0', 'vpminsw ymm4,ymm8,ymm8', 'vpminsw ymm4,ymm8,ymm8'),
    ('VPMINSW 6', 'c5bdea24254a4a4a4a', 'vpminsw ymm4,ymm8,yword [0x4a4a4a4a]', 'vpminsw ymm4,ymm8,yword [0x4a4a4a4a]'),
    ('VPMINSW 7', 'c4c13dea23', 'vpminsw ymm4,ymm8,yword [r11]', 'vpminsw ymm4,ymm8,yword [r11]'),
    ('VPMINSW 8', 'c4c13dea6153', 'vpminsw ymm4,ymm8,yword [r9 + 83]', 'vpminsw ymm4,ymm8,yword [r9 + 83]'),
    ('VPOR 0', 'c4c141ebeb', 'vpor xmm5,xmm7,xmm11', 'vpor xmm5,xmm7,xmm11'),
    ('VPOR 1', 'c5c1eb2c254a4a4a4a', 'vpor xmm5,xmm7,oword [0x4a4a4a4a]', 'vpor xmm5,xmm7,oword [0x4a4a4a4a]'),
    ('VPOR 2', 'c4c141eb29', 'vpor xmm5,xmm7,oword [r9]', 'vpor xmm5,xmm7,oword [r9]'),
    ('VPOR 3', 'c5c1eba8b3000000', 'vpor xmm5,xmm7,oword [rax + 179]', 'vpor xmm5,xmm7,oword [rax + 179]'),
    ('VPOR 5', 'c525ebcd', 'vpor ymm9,ymm11,ymm5', 'vpor ymm9,ymm11,ymm5'),
    ('VPOR 6', 'c525eb0c254a4a4a4a', 'vpor ymm9,ymm11,yword [0x4a4a4a4a]', 'vpor ymm9,ymm11,yword [0x4a4a4a4a]'),
    ('VPOR 7', 'c44125eb0f', 'vpor ymm9,ymm11,yword [r15]', 'vpor ymm9,ymm11,yword [r15]'),
    ('VPOR 8', 'c44125eb4b0a', 'vpor ymm9,ymm11,yword [r11 + 10]', 'vpor ymm9,ymm11,yword [r11 + 10]'),
    ('VPMAXSW 0', 'c4c161eedb', 'vpmaxsw xmm3,xmm3,xmm11', 'vpmaxsw xmm3,xmm3,xmm11'),
    ('VPMAXSW 1', 'c5e1ee1c254a4a4a4a', 'vpmaxsw xmm3,xmm3,oword [0x4a4a4a4a]', 'vpmaxsw xmm3,xmm3,oword [0x4a4a4a4a]'),
    ('VPMAXSW 2', 'c4c161ee1b', 'vpmaxsw xmm3,xmm3,oword [r11]', 'vpmaxsw xmm3,xmm3,oword [r11]'),
    ('VPMAXSW 3', 'c4c161ee9a9b000000', 'vpmaxsw xmm3,xmm3,oword [r10 + 155]', 'vpmaxsw xmm3,xmm3,oword [r10 + 155]'),
    ('VPMAXSW 5', 'c585eefd', 'vpmaxsw ymm7,ymm15,ymm5', 'vpmaxsw ymm7,ymm15,ymm5'),
    ('VPMAXSW 6', 'c585ee3c254a4a4a4a', 'vpmaxsw ymm7,ymm15,yword [0x4a4a4a4a]', 'vpmaxsw ymm7,ymm15,yword [0x4a4a4a4a]'),
    ('VPMAXSW 7', 'c4c105ee3f', 'vpmaxsw ymm7,ymm15,yword [r15]', 'vpmaxsw ymm7,ymm15,yword [r15]'),
    ('VPMAXSW 8', 'c585eebacf000000', 'vpmaxsw ymm7,ymm15,yword [rdx + 207]', 'vpmaxsw ymm7,ymm15,yword [rdx + 207]'),
    ('VPXOR 0', 'c4c111efe8', 'vpxor xmm5,xmm13,xmm8', 'vpxor xmm5,xmm13,xmm8'),
    ('VPXOR 1', 'c591ef2c254a4a4a4a', 'vpxor xmm5,xmm13,oword [0x4a4a4a4a]', 'vpxor xmm5,xmm13,oword [0x4a4a4a4a]'),
    ('VPXOR 2', 'c4c111ef6d00', 'vpxor xmm5,xmm13,oword [r13]', 'vpxor xmm5,xmm13,oword [r13]'),
    ('VPXOR 5', 'c44165efc2', 'vpxor ymm8,ymm3,ymm10', 'vpxor ymm8,ymm3,ymm10'),
    ('VPXOR 6', 'c565ef04254a4a4a4a', 'vpxor ymm8,ymm3,yword [0x4a4a4a4a]', 'vpxor ymm8,ymm3,yword [0x4a4a4a4a]'),
    ('VPXOR 7', 'c44165ef06', 'vpxor ymm8,ymm3,yword [r14]', 'vpxor ymm8,ymm3,yword [r14]'),
    ('VPXOR 8', 'c44165ef4513', 'vpxor ymm8,ymm3,yword [r13 + 19]', 'vpxor ymm8,ymm3,yword [r13 + 19]'),
    ('VPSLLW 0', 'c4c179f1e1', 'vpsllw xmm4,xmm0,xmm9', 'vpsllw xmm4,xmm0,xmm9'),
    ('VPSLLW 1', 'c5f9f124254a4a4a4a', 'vpsllw xmm4,xmm0,oword [0x4a4a4a4a]', 'vpsllw xmm4,xmm0,oword [0x4a4a4a4a]'),
    ('VPSLLW 2', 'c5f9f122', 'vpsllw xmm4,xmm0,oword [rdx]', 'vpsllw xmm4,xmm0,oword [rdx]'),
    ('VPSLLW 3', 'c4c179f16673', 'vpsllw xmm4,xmm0,oword [r14 + 115]', 'vpsllw xmm4,xmm0,oword [r14 + 115]'),
    ('VPSLLW 5', 'c4c105f1cf', 'vpsllw ymm1,ymm15,xmm15', 'vpsllw ymm1,ymm15,xmm15'),
    ('VPSLLD 0', 'c5a9f2c9', 'vpslld xmm1,xmm10,xmm1', 'vpslld xmm1,xmm10,xmm1'),
    ('VPSLLD 1', 'c5a9f20c254a4a4a4a', 'vpslld xmm1,xmm10,oword [0x4a4a4a4a]', 'vpslld xmm1,xmm10,oword [0x4a4a4a4a]'),
    ('VPSLLD 2', 'c4c129f20b', 'vpslld xmm1,xmm10,oword [r11]', 'vpslld xmm1,xmm10,oword [r11]'),
    ('VPSLLD 3', 'c5a9f24a7f', 'vpslld xmm1,xmm10,oword [rdx + 127]', 'vpslld xmm1,xmm10,oword [rdx + 127]'),
    ('VPSLLD 5', 'c545f2d7', 'vpslld ymm10,ymm7,xmm7', 'vpslld ymm10,ymm7,xmm7'),
    ('VPSLLQ 0', 'c44151f3f2', 'vpsllq xmm14,xmm5,xmm10', 'vpsllq xmm14,xmm5,xmm10'),
    ('VPSLLQ 1', 'c551f334254a4a4a4a', 'vpsllq xmm14,xmm5,oword [0x4a4a4a4a]', 'vpsllq xmm14,xmm5,oword [0x4a4a4a4a]'),
    ('VPSLLQ 2', 'c551f333', 'vpsllq xmm14,xmm5,oword [rbx]', 'vpsllq xmm14,xmm5,oword [rbx]'),
    ('VPSLLQ 3', 'c44151f3b6ba000000', 'vpsllq xmm14,xmm5,oword [r14 + 186]', 'vpsllq xmm14,xmm5,oword [r14 + 186]'),
    ('VPSLLQ 5', 'c55df3fc', 'vpsllq ymm15,ymm4,xmm4', 'vpsllq ymm15,ymm4,xmm4'),
    ('VPMULUDQ 0', 'c4c161f4c1', 'vpmuludq xmm0,xmm3,xmm9', 'vpmuludq xmm0,xmm3,xmm9'),
    ('VPMULUDQ 1', 'c5e1f404254a4a4a4a', 'vpmuludq xmm0,xmm3,oword [0x4a4a4a4a]', 'vpmuludq xmm0,xmm3,oword [0x4a4a4a4a]'),
    ('VPMULUDQ 2', 'c5e1f402', 'vpmuludq xmm0,xmm3,oword [rdx]', 'vpmuludq xmm0,xmm3,oword [rdx]'),
    ('VPMULUDQ 3', 'c4c161f48192000000', 'vpmuludq xmm0,xmm3,oword [r9 + 146]', 'vpmuludq xmm0,xmm3,oword [r9 + 146]'),
    ('VPMULUDQ 5', 'c58df4ce', 'vpmuludq ymm1,ymm14,ymm6', 'vpmuludq ymm1,ymm14,ymm6'),
    ('VPMULUDQ 6', 'c58df40c254a4a4a4a', 'vpmuludq ymm1,ymm14,yword [0x4a4a4a4a]', 'vpmuludq ymm1,ymm14,yword [0x4a4a4a4a]'),
    ('VPMULUDQ 7', 'c58df409', 'vpmuludq ymm1,ymm14,yword [rcx]', 'vpmuludq ymm1,ymm14,yword [rcx]'),
    ('VPMULUDQ 8', 'c58df44852', 'vpmuludq ymm1,ymm14,yword [rax + 82]', 'vpmuludq ymm1,ymm14,yword [rax + 82]'),
    ('VPMADDWD 0', 'c44179f5c4', 'vpmaddwd xmm8,xmm0,xmm12', 'vpmaddwd xmm8,xmm0,xmm12'),
    ('VPMADDWD 1', 'c579f504254a4a4a4a', 'vpmaddwd xmm8,xmm0,oword [0x4a4a4a4a]', 'vpmaddwd xmm8,xmm0,oword [0x4a4a4a4a]'),
    ('VPMADDWD 2', 'c579f501', 'vpmaddwd xmm8,xmm0,oword [rcx]', 'vpmaddwd xmm8,xmm0,oword [rcx]'),
    ('VPMADDWD 3', 'c44179f5442418', 'vpmaddwd xmm8,xmm0,oword [r12 + 24]', 'vpmaddwd xmm8,xmm0,oword [r12 + 24]'),
    ('VPMADDWD 5', 'c44165f5e0', 'vpmaddwd ymm12,ymm3,ymm8', 'vpmaddwd ymm12,ymm3,ymm8'),
    ('VPMADDWD 6', 'c565f524254a4a4a4a', 'vpmaddwd ymm12,ymm3,yword [0x4a4a4a4a]', 'vpmaddwd ymm12,ymm3,yword [0x4a4a4a4a]'),
    ('VPMADDWD 7', 'c565f520', 'vpmaddwd ymm12,ymm3,yword [rax]', 'vpmaddwd ymm12,ymm3,yword [rax]'),
    ('VPMADDWD 8', 'c44165f5a5dd000000', 'vpmaddwd ymm12,ymm3,yword [r13 + 221]', 'vpmaddwd ymm12,ymm3,yword [r13 + 221]'),
    ('VPSADBW 0', 'c531f6c8', 'vpsadbw xmm9,xmm9,xmm0', 'vpsadbw xmm9,xmm9,xmm0'),
    ('VPSADBW 1', 'c531f60c254a4a4a4a', 'vpsadbw xmm9,xmm9,oword [0x4a4a4a4a]', 'vpsadbw xmm9,xmm9,oword [0x4a4a4a4a]'),
    ('VPSADBW 2', 'c44131f60a', 'vpsadbw xmm9,xmm9,oword [r10]', 'vpsadbw xmm9,xmm9,oword [r10]'),
    ('VPSADBW 3', 'c44131f64803', 'vpsadbw xmm9,xmm9,oword [r8 + 3]', 'vpsadbw xmm9,xmm9,oword [r8 + 3]'),
    ('VPSADBW 4', 'c42131f60cd503000000', 'vpsadbw xmm9,xmm9,oword [0x00000003 + r10 * 8]', 'vpsadbw xmm9,xmm9,oword [0x00000003 + r10 * 8]'),
    ('VPSADBW 5', 'c5bdf6c2', 'vpsadbw ymm0,ymm8,ymm2', 'vpsadbw ymm0,ymm8,ymm2'),
    ('VPSADBW 6', 'c5bdf604254a4a4a4a', 'vpsadbw ymm0,ymm8,yword [0x4a4a4a4a]', 'vpsadbw ymm0,ymm8,yword [0x4a4a4a4a]'),
    ('VPSADBW 7', 'c5bdf602', 'vpsadbw ymm0,ymm8,yword [rdx]', 'vpsadbw ymm0,ymm8,yword [rdx]'),
    ('VPSADBW 8', 'c5bdf64002', 'vpsadbw ymm0,ymm8,yword [rax + 2]', 'vpsadbw ymm0,ymm8,yword [rax + 2]'),
    ('VPSADBW 9', 'c4a13df604c502000000', 'vpsadbw ymm0,ymm8,yword [0x00000002 + r8 * 8]', 'vpsadbw ymm0,ymm8,yword [0x00000002 + r8 * 8]'),
    ('VMOVQ 0', 'c4c17a7eec', 'vmovd_q xmm5,xmm12', 'vmovd_q xmm5,xmm12'),
    ('VMOVQ 1', 'c5f9d604254a4a4a4a', 'vmovq qword [0x4a4a4a4a],xmm0', 'vmovq qword [0x4a4a4a4a],xmm0'),
    ('VMOVQ 2', 'c44179d630', 'vmovq qword [r8],xmm14', 'vmovq qword [r8],xmm14'),
    ('VMOVQ 3', 'c44179d68fb4000000', 'vmovq qword [r15 + 180],xmm9', 'vmovq qword [r15 + 180],xmm9'),
    ('VPMOVMSKB 0', 'c44179d7cf', 'vpmovmskb r9d,xmm15', 'vpmovmskb r9d,xmm15'),
    ('VPMOVMSKB 1', 'c57dd7c9', 'vpmovmskb r9d,ymm1', 'vpmovmskb r9d,ymm1'),
    ('VCVTTPD2DQ 0', 'c4c179e6ce', 'vcvttpd2dq xmm1,xmm14', 'vcvttpd2dq xmm1,xmm14'),
    ('VCVTTPD2DQ 1', 'c5fde6cd', 'vcvttpd2dq xmm1,ymm5', 'vcvttpd2dq xmm1,ymm5'),
    ('VCVTTPD2DQ 2', 'c5f9e60c254a4a4a4a', 'vcvttpd2dq xmm1,oword [0x4a4a4a4a]', 'vcvttpd2dq xmm1,oword [0x4a4a4a4a]'),
    ('VCVTTPD2DQ 3', 'c4c179e60f', 'vcvttpd2dq xmm1,oword [r15]', 'vcvttpd2dq xmm1,oword [r15]'),
    ('VCVTTPD2DQ 4', 'c4c179e64871', 'vcvttpd2dq xmm1,oword [r8 + 113]', 'vcvttpd2dq xmm1,oword [r8 + 113]'),
    ('VCVTTPD2DQ 5', 'c4a179e60cf571000000', 'vcvttpd2dq xmm1,oword [0x00000071 + r14 * 8]', 'vcvttpd2dq xmm1,oword [0x00000071 + r14 * 8]'),

    ('VBROADCASTSS 0', 'c4627918ed', 'vbroadcastss xmm13,xmm5', 'vbroadcastss xmm13,xmm5'),
    ('VBROADCASTSS 1', 'c46279182c254a4a4a4a', 'vbroadcastss xmm13,dword [0x4a4a4a4a]', 'vbroadcastss xmm13,dword [0x4a4a4a4a]'),
    ('VBROADCASTSS 2', 'c44279182a', 'vbroadcastss xmm13,dword [r10]', 'vbroadcastss xmm13,dword [r10]'),
    ('VBROADCASTSS 3', 'c44279186c2451', 'vbroadcastss xmm13,dword [r12 + 81]', 'vbroadcastss xmm13,dword [r12 + 81]'),
    ('VBROADCASTSS 4', 'c46279182ccd51000000', 'vbroadcastss xmm13,dword [0x00000051 + rcx * 8]', 'vbroadcastss xmm13,dword [0x00000051 + rcx * 8]'),
    ('VBROADCASTSS 5', 'c4c27d18f0', 'vbroadcastss ymm6,xmm8', 'vbroadcastss ymm6,xmm8'),
    ('VBROADCASTSS 6', 'c4e27d1834254a4a4a4a', 'vbroadcastss ymm6,dword [0x4a4a4a4a]', 'vbroadcastss ymm6,dword [0x4a4a4a4a]'),
    ('VBROADCASTSS 7', 'c4e27d1830', 'vbroadcastss ymm6,dword [rax]', 'vbroadcastss ymm6,dword [rax]'),
    ('VBROADCASTSS 8', 'c4c27d187103', 'vbroadcastss ymm6,dword [r9 + 3]', 'vbroadcastss ymm6,dword [r9 + 3]'),
    ('VBROADCASTSS 9', 'c4a27d1834c503000000', 'vbroadcastss ymm6,dword [0x00000003 + r8 * 8]', 'vbroadcastss ymm6,dword [0x00000003 + r8 * 8]'),
    ('VBROADCASTSD 0', 'c4c27d19c2', 'vbroadcastsd ymm0,xmm10', 'vbroadcastsd ymm0,xmm10'),
    ('VBROADCASTSD 1', 'c4e27d1904254a4a4a4a', 'vbroadcastsd ymm0,qword [0x4a4a4a4a]', 'vbroadcastsd ymm0,qword [0x4a4a4a4a]'),
    ('VBROADCASTSD 2', 'c4c27d1900', 'vbroadcastsd ymm0,qword [r8]', 'vbroadcastsd ymm0,qword [r8]'),
    ('VBROADCASTSD 3', 'c4e27d1980ba000000', 'vbroadcastsd ymm0,qword [rax + 186]', 'vbroadcastsd ymm0,qword [rax + 186]'),
    ('VBROADCASTF128 0', 'c4e27d1a34254a4a4a4a', 'vbroadcastf128 ymm6,oword [0x4a4a4a4a]', 'vbroadcastf128 ymm6,oword [0x4a4a4a4a]'),
    ('VBROADCASTF128 1', 'c4c27d1a37', 'vbroadcastf128 ymm6,oword [r15]', 'vbroadcastf128 ymm6,oword [r15]'),
    ('VBROADCASTF128 2', 'c4c27d1a712b', 'vbroadcastf128 ymm6,oword [r9 + 43]', 'vbroadcastf128 ymm6,oword [r9 + 43]'),

    ('VFMADD132PD 0', 'c4c2c998c4', 'vfmadd132ps_d xmm0,xmm6,xmm12', 'vfmadd132ps_d xmm0,xmm6,xmm12'),
    ('VFMADD132PD 1', 'c4e2c99804254a4a4a4a', 'vfmadd132ps_d xmm0,xmm6,oword [0x4a4a4a4a]', 'vfmadd132ps_d xmm0,xmm6,oword [0x4a4a4a4a]'),
    ('VFMADD132PD 2', 'c4c2c9980424', 'vfmadd132ps_d xmm0,xmm6,oword [r12]', 'vfmadd132ps_d xmm0,xmm6,oword [r12]'),
    ('VFMADD132PD 3', 'c4c2c9984152', 'vfmadd132ps_d xmm0,xmm6,oword [r9 + 82]', 'vfmadd132ps_d xmm0,xmm6,oword [r9 + 82]'),
    ('VFMADD132PD 4', 'c4e2c99804cd52000000', 'vfmadd132ps_d xmm0,xmm6,oword [0x00000052 + rcx * 8]', 'vfmadd132ps_d xmm0,xmm6,oword [0x00000052 + rcx * 8]'),
    ('VFMADD132PD 5', 'c462c598c8', 'vfmadd132ps_d ymm9,ymm7,ymm0', 'vfmadd132ps_d ymm9,ymm7,ymm0'),
    ('VFMADD132PD 6', 'c462c5980c254a4a4a4a', 'vfmadd132ps_d ymm9,ymm7,yword [0x4a4a4a4a]', 'vfmadd132ps_d ymm9,ymm7,yword [0x4a4a4a4a]'),
    ('VFMADD132PD 7', 'c442c5980f', 'vfmadd132ps_d ymm9,ymm7,yword [r15]', 'vfmadd132ps_d ymm9,ymm7,yword [r15]'),
    ('VFMADD132PD 8', 'c462c5984a5b', 'vfmadd132ps_d ymm9,ymm7,yword [rdx + 91]', 'vfmadd132ps_d ymm9,ymm7,yword [rdx + 91]'),
    ('VFMADD132PD 9', 'c422c5980ce55b000000', 'vfmadd132ps_d ymm9,ymm7,yword [0x0000005b + r12 * 8]', 'vfmadd132ps_d ymm9,ymm7,yword [0x0000005b + r12 * 8]'),
    ('VFMADD213PD 0', 'c4e299a8ea', 'vfmadd213ps_d xmm5,xmm12,xmm2', 'vfmadd213ps_d xmm5,xmm12,xmm2'),
    ('VFMADD213PD 1', 'c4e299a82c254a4a4a4a', 'vfmadd213ps_d xmm5,xmm12,oword [0x4a4a4a4a]', 'vfmadd213ps_d xmm5,xmm12,oword [0x4a4a4a4a]'),
    ('VFMADD213PD 2', 'c4c299a82a', 'vfmadd213ps_d xmm5,xmm12,oword [r10]', 'vfmadd213ps_d xmm5,xmm12,oword [r10]'),
    ('VFMADD213PD 3', 'c4c299a8afa9000000', 'vfmadd213ps_d xmm5,xmm12,oword [r15 + 169]', 'vfmadd213ps_d xmm5,xmm12,oword [r15 + 169]'),
    ('VFMADD213PD 4', 'c4e299a82cdda9000000', 'vfmadd213ps_d xmm5,xmm12,oword [0x000000a9 + rbx * 8]', 'vfmadd213ps_d xmm5,xmm12,oword [0x000000a9 + rbx * 8]'),
    ('VFMADD213PD 5', 'c4e2eda8e9', 'vfmadd213ps_d ymm5,ymm2,ymm1', 'vfmadd213ps_d ymm5,ymm2,ymm1'),
    ('VFMADD213PD 6', 'c4e2eda82c254a4a4a4a', 'vfmadd213ps_d ymm5,ymm2,yword [0x4a4a4a4a]', 'vfmadd213ps_d ymm5,ymm2,yword [0x4a4a4a4a]'),
    ('VFMADD213PD 7', 'c4e2eda829', 'vfmadd213ps_d ymm5,ymm2,yword [rcx]', 'vfmadd213ps_d ymm5,ymm2,yword [rcx]'),
    ('VFMADD213PD 8', 'c4e2eda86875', 'vfmadd213ps_d ymm5,ymm2,yword [rax + 117]', 'vfmadd213ps_d ymm5,ymm2,yword [rax + 117]'),
    ('VFMADD213PD 9', 'c4a2eda82cdd75000000', 'vfmadd213ps_d ymm5,ymm2,yword [0x00000075 + r11 * 8]', 'vfmadd213ps_d ymm5,ymm2,yword [0x00000075 + r11 * 8]'),
    ('VFMADD231PD 0', 'c462f9b8cf', 'vfmadd231ps_d xmm9,xmm0,xmm7', 'vfmadd231ps_d xmm9,xmm0,xmm7'),
    ('VFMADD231PD 1', 'c462f9b80c254a4a4a4a', 'vfmadd231ps_d xmm9,xmm0,oword [0x4a4a4a4a]', 'vfmadd231ps_d xmm9,xmm0,oword [0x4a4a4a4a]'),
    ('VFMADD231PD 2', 'c462f9b809', 'vfmadd231ps_d xmm9,xmm0,oword [rcx]', 'vfmadd231ps_d xmm9,xmm0,oword [rcx]'),
    ('VFMADD231PD 3', 'c462f9b84a3c', 'vfmadd231ps_d xmm9,xmm0,oword [rdx + 60]', 'vfmadd231ps_d xmm9,xmm0,oword [rdx + 60]'),
    ('VFMADD231PD 4', 'c462f9b80cdd3c000000', 'vfmadd231ps_d xmm9,xmm0,oword [0x0000003c + rbx * 8]', 'vfmadd231ps_d xmm9,xmm0,oword [0x0000003c + rbx * 8]'),
    ('VFMADD231PD 5', 'c4e2c5b8e0', 'vfmadd231ps_d ymm4,ymm7,ymm0', 'vfmadd231ps_d ymm4,ymm7,ymm0'),
    ('VFMADD231PD 6', 'c4e2c5b824254a4a4a4a', 'vfmadd231ps_d ymm4,ymm7,yword [0x4a4a4a4a]', 'vfmadd231ps_d ymm4,ymm7,yword [0x4a4a4a4a]'),
    ('VFMADD231PD 7', 'c4c2c5b822', 'vfmadd231ps_d ymm4,ymm7,yword [r10]', 'vfmadd231ps_d ymm4,ymm7,yword [r10]'),
    ('VFMADD231PD 8', 'c4c2c5b8a1df000000', 'vfmadd231ps_d ymm4,ymm7,yword [r9 + 223]', 'vfmadd231ps_d ymm4,ymm7,yword [r9 + 223]'),
    ('VFMADD231PD 9', 'c4a2c5b824d5df000000', 'vfmadd231ps_d ymm4,ymm7,yword [0x000000df + r10 * 8]', 'vfmadd231ps_d ymm4,ymm7,yword [0x000000df + r10 * 8]'),
    ('VCMPPS 0', 'c5a8c2d1e8', 'vcmpps xmm2,xmm10,xmm1,232', 'vcmpps xmm2,xmm10,xmm1,232'),
    ('VCMPPS 1', 'c5a8c214254a4a4a4aaa', 'vcmpps xmm2,xmm10,oword [0x4a4a4a4a],170', 'vcmpps xmm2,xmm10,oword [0x4a4a4a4a],170'),
    ('VCMPPS 2', 'c4c128c216e5', 'vcmpps xmm2,xmm10,oword [r14],229', 'vcmpps xmm2,xmm10,oword [r14],229'),
    ('VCMPPS 3', 'c4c128c2514efe', 'vcmpps xmm2,xmm10,oword [r9 + 78],254', 'vcmpps xmm2,xmm10,oword [r9 + 78],254'),
    ('VCMPPS 5', 'c44134c2fd98', 'vcmpps ymm15,ymm9,ymm13,152', 'vcmpps ymm15,ymm9,ymm13,152'),
    ('VCMPPS 6', 'c534c23c254a4a4a4a2b', 'vcmpps ymm15,ymm9,yword [0x4a4a4a4a],43', 'vcmpps ymm15,ymm9,yword [0x4a4a4a4a],43'),
    ('VCMPPS 7', 'c44134c27d00d3', 'vcmpps ymm15,ymm9,yword [r13],211', 'vcmpps ymm15,ymm9,yword [r13],211'),
    ('VCMPPS 8', 'c534c2b8f8000000d1', 'vcmpps ymm15,ymm9,yword [rax + 248],209', 'vcmpps ymm15,ymm9,yword [rax + 248],209'),
    ('VFMADD132pd', 'C4E2E998CB', 'vfmadd132ps_d xmm1,xmm2,xmm3', 'vfmadd132ps_d xmm1,xmm2,xmm3'),
    ('VFMADD213sd', 'c4e2e9a925e32a0600', 'vfmadd213ss_d xmm4,xmm2,qword [rip + 404195]', 'vfmadd213ss_d xmm4,xmm2,qword [rip + 404195]'),
    ('VFMADD213sd 2', 'c4e2f1a91df82a0600', 'vfmadd213ss_d xmm3,xmm1,qword [rip + 404216]', 'vfmadd213ss_d xmm3,xmm1,qword [rip + 404216]'),
    # for the *213ss versions, rex needs to be able to change the mnem :/

    ('VPMOVSXBW', 'C4E27D20CF', 'vpmovsxbw ymm1,xmm7', 'vpmovsxbw ymm1,xmm7'),
    ('VPMOVSXBD', 'C4E27D21CF', 'vpmovsxbd ymm1,xmm7', 'vpmovsxbd ymm1,xmm7'),
    ('VPMOVSXBQ', 'C4E27D22CF', 'vpmovsxbq ymm1,xmm7', 'vpmovsxbq ymm1,xmm7'),
    ('VPMOVSXWD', 'C4E27D23CF', 'vpmovsxwd ymm1,xmm7', 'vpmovsxwd ymm1,xmm7'),
    ('VPMOVSXWQ', 'C4E27D24CF', 'vpmovsxwq ymm1,xmm7', 'vpmovsxwq ymm1,xmm7'),
    ('VPMOVSXDQ', 'C4E27D25CF', 'vpmovsxdq ymm1,xmm7', 'vpmovsxdq ymm1,xmm7'),

    ('VPMOVSXBW (MEM)', 'c4e2792010', 'vpmovsxbw xmm2,qword [rax]', 'vpmovsxbw xmm2,qword [rax]'),
    ('VPMOVSXBD (MEM)', 'c4e2792110', 'vpmovsxbd xmm2,dword [rax]', 'vpmovsxbd xmm2,dword [rax]'),
    ('VPMOVSXBQ (MEM)', 'c4e2792210', 'vpmovsxbq xmm2,word [rax]',  'vpmovsxbq xmm2,word [rax]'),
    ('VPMOVSXWD (MEM)', 'c4e2792310', 'vpmovsxwd xmm2,qword [rax]', 'vpmovsxwd xmm2,qword [rax]'),
    ('VPMOVSXWQ (MEM)', 'c4e2792410', 'vpmovsxwq xmm2,dword [rax]', 'vpmovsxwq xmm2,dword [rax]'),
    ('VPMOVSXDQ (MEM)', 'c4e2792510', 'vpmovsxdq xmm2,qword [rax]', 'vpmovsxdq xmm2,qword [rax]'),

    # The opersize here fails :(
    # ('VPMOVSXBW (MEM256)', 'c4e27d2010', 'vpmovsxbw ymm2,oword [rax]', 'vpmovsxbw ymm2,oword [rax]'),

    ('VPMOVZXBW', 'C4E27D30CF', 'vpmovzxbw ymm1,xmm7', 'vpmovzxbw ymm1,xmm7'),
    ('VPMOVZXBD', 'C4E27D31CF', 'vpmovzxbd ymm1,xmm7', 'vpmovzxbd ymm1,xmm7'),
    ('VPMOVZXBQ', 'C4E27D32CF', 'vpmovzxbq ymm1,xmm7', 'vpmovzxbq ymm1,xmm7'),
    ('VPMOVZXWD', 'C4E27D33CF', 'vpmovzxwd ymm1,xmm7', 'vpmovzxwd ymm1,xmm7'),
    ('VPMOVZXWQ', 'C4E27D34CF', 'vpmovzxwq ymm1,xmm7', 'vpmovzxwq ymm1,xmm7'),
    ('VPMOVZXDQ', 'C4E27D35CF', 'vpmovzxdq ymm1,xmm7', 'vpmovzxdq ymm1,xmm7'),
    ('VPMOVZXBW (MEM)', 'c4e2793010', 'vpmovzxbw xmm2,qword [rax]', 'vpmovzxbw xmm2,qword [rax]'),
    ('VPMOVZXBD (MEM)', 'c4e2793110', 'vpmovzxbd xmm2,dword [rax]', 'vpmovzxbd xmm2,dword [rax]'),
    ('VPMOVZXBQ (MEM)', 'c4e2793210', 'vpmovzxbq xmm2,word [rax]',  'vpmovzxbq xmm2,word [rax]'),
    ('VPMOVZXWD (MEM)', 'c4e2793310', 'vpmovzxwd xmm2,qword [rax]', 'vpmovzxwd xmm2,qword [rax]'),
    ('VPMOVZXWQ (MEM)', 'c4e2793410', 'vpmovzxwq xmm2,dword [rax]', 'vpmovzxwq xmm2,dword [rax]'),
    ('VPMOVZXDQ (MEM)', 'c4e2793510', 'vpmovzxdq xmm2,qword [rax]', 'vpmovzxdq xmm2,qword [rax]'),
]


class Amd64InstructionSet(unittest.TestCase):
    _arch = envi.getArchModule("amd64")

    def check_opreprs(self, opers):
        vw = vivisect.VivWorkspace()
        scanv = e_memcanvas.StringMemoryCanvas(vw)

        for name, bytez, reprOp, renderOp in opers:
            try:
                op = self._arch.archParseOpcode(binascii.unhexlify(bytez), 0, 0x400)
            except envi.InvalidInstruction:
                self.fail("Failed to parse opcode bytes: %s (case: %s, expected: %s)" % (bytez, name, reprOp))
            except Exception as e:
                self.fail('Unexpected parse error for case %s: %s' % (name, repr(e)))
            msg = '%s failed length check. Got %d, expected %d' % (name, len(op), int(len(bytez)/2))
            self.assertEqual(len(op), int(len(bytez)/2), msg=msg)
            try:
                self.assertEqual(repr(op), reprOp)
            except AssertionError:
                self.fail("Failing match for case %s (bytes: %s) (Got: '%s', Expected: '%s')" % (name, bytez, repr(op), reprOp))
            except Exception as e:
                self.fail('Unexpected repr error for case %s: %s' % (name, repr(e)))

            scanv.clearCanvas()
            op.render(scanv)
            try:
                self.assertEqual(scanv.strval, renderOp)
            except AssertionError:
                self.fail("Failing canvas case for case %s (bytes: %s) (Got: '%s', Expected: '%s')" % (name, bytez, scanv.strval, renderOp))
            except Exception as e:
                self.fail('Unexpected scanv error for case %s: %s' % (name, repr(e)))

    def test_envi_amd64_disasm_Specific_VEX_Instrs(self):
        self.check_opreprs(amd64VexOpcodes)

    def test_envi_amd64_disasm_Specific_SingleByte_Instrs(self):
        self.check_opreprs(amd64SingleByteOpcodes)

    def test_envi_amd64_disasm_Specific_MultiByte_Instrs(self):
        self.check_opreprs(amd64MultiByteOpcodes)

    def checkOpcode(self, hexbytez, va, oprepr, opcheck, opercheck, renderOp):

        op = self._arch.archParseOpcode(binascii.unhexlify(hexbytez), 0, va)

        self.assertEqual( repr(op), oprepr )
        opvars = vars(op)
        for opk,opv in opcheck.items():
            self.assertEqual((repr(op), opk, opvars.get(opk)), (oprepr, opk, opv))

        for oidx in range(len(op.opers)):
            oper = op.opers[oidx]
            opervars = vars(oper)
            for opk,opv in opercheck[oidx].items():
                self.assertEqual((repr(op), opk, opervars.get(opk)), (oprepr, opk, opv))

        vw = vivisect.VivWorkspace()
        scanv = e_memcanvas.StringMemoryCanvas(vw)
        op.render(scanv)
        self.assertEqual( scanv.strval, renderOp )

    ###############################################
    # only pick the operands special to 64-bit mode
    def test_envi_amd64_disasm_Reg_Operands(self):
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
        _0      mov REX     41b*

        '''
        opbytez = '0032'
        oprepr = 'add byte [rdx],dh'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'add', 'opcode': 8193, 'size': 2}
        opercheck = [{'disp': 0, 'tsize': 1, '_is_deref': True, 'reg': 2}, {'tsize': 1, 'reg': 134742018}]
        self.checkOpcode(opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr)

        opbytez = '480032'
        oprepr = 'add byte [rdx],sil'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 1572864, 'mnem': 'add', 'opcode': 8193, 'size': 3}
        opercheck = [{'disp': 0, 'tsize': 1, '_is_deref': True, 'reg': 2}, {'tsize': 1, 'reg': 524294}]
        self.checkOpcode(opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr)

        opbytez = '480132'
        oprepr = 'add qword [rdx],rsi'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 1572864, 'mnem': 'add', 'opcode': 8193, 'size': 3}
        opercheck = [{'disp': 0, 'tsize': 8, '_is_deref': True, 'reg': 2}, {'tsize': 8, 'reg': 6}]
        self.checkOpcode(opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr)

        opbytez = '0440'
        oprepr = 'add al,64'
        opcheck = {'iflags': 131072, 'prefixes': 0, 'mnem': 'add', 'opcode': 8193, 'size': 2}
        opercheck = ( {'tsize': 1, 'reg': 524288}, {'tsize': 1, 'imm': 64} )
        self.checkOpcode(opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr)

        opbytez = '0218'
        oprepr = 'add bl,byte [rax]'
        opcheck = {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'add', 'opcode': 8193, 'size': 2}
        opercheck = ( {'tsize': 1, 'reg': 524291}, {'disp': 0, 'tsize': 1, '_is_deref': True, 'reg': 0} )
        self.checkOpcode(opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr)

        for x in range(0xb0, 0xb8):
            bytez = '41%.2xAAAAAAAA' % x
            op = self._arch.archParseOpcode(binascii.unhexlify(bytez),0,0x1000)
            self.assertEqual((bytez, hex(op.opers[0].reg)), (bytez, hex( 0x80000 + (x-0xa8))))

        for x in range(0xb8, 0xc0):
            bytez = '41%.2xAAAAAAAA' % x
            op = self._arch.archParseOpcode(binascii.unhexlify(bytez),0,0x1000)
            self.assertEqual((bytez, hex(op.opers[0].reg)), (bytez, hex( 0x200000 + (x-0xb0) )))

    def test_envi_amd64_disasm_Imm_Operands(self):
        '''
        test an opcode encoded with an Imm operand
        _0      rol         d000
        A       callf       9a
        '''
        opbytez = 'd000'
        oprepr = 'rol byte [rax],1'
        opcheck =  {'iflags': 131072, 'va': 16384, 'prefixes': 0, 'mnem': 'rol', 'opcode': 8201, 'size': 2}
        opercheck = ( {'disp': 0, 'tsize': 1, '_is_deref': True, 'reg': 0}, {'tsize': 4, 'imm': 1} )
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        # this is failing legitimately... we decode this opcode wrong
        opbytez = '9aaa11aabbcc33'
        oprepr = 'callf 0x33cc:0xbbaa11aa'
        opcheck =  {'iflags': 131076, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'callf', 'opcode': 4099, 'size': 7}
        opercheck = [{'tsize': 6, 'imm': 56954414829994}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        opbytez = '413ac4'
        oprepr = 'cmp al,r12l'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 1114112, 'mnem': 'cmp', 'opcode': 20482, 'size': 3}
        opercheck = [{'tsize': 1, 'reg': 524288}, {'tsize': 1, 'reg': 524300}]
        self.checkOpcode(opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr)

        opbytez = '453ac4'
        oprepr = 'cmp r8l,r12l'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 1376256, 'mnem': 'cmp', 'opcode': 20482, 'size': 3}
        opercheck = [{'tsize': 1, 'reg': 524296}, {'tsize': 1, 'reg': 524300}]
        self.checkOpcode(opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr)

        opbytez = '473ac4'
        oprepr = 'cmp r8l,r12l'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 1507328, 'mnem': 'cmp', 'opcode': 20482, 'size': 3}
        opercheck = [{'tsize': 1, 'reg': 524296}, {'tsize': 1, 'reg': 524300}]
        self.checkOpcode(opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr)

        opbytez = '3ac4'
        oprepr = 'cmp al,ah'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'cmp', 'opcode': 20482, 'size': 2}
        opercheck = [{'tsize': 1, 'reg': 524288}, {'tsize': 1, 'reg': 134742016}]
        self.checkOpcode(opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr)

        opbytez = '403ac4'
        oprepr = 'cmp al,spl'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 1048576, 'mnem': 'cmp', 'opcode': 20482, 'size': 3}
        opercheck = [{'tsize': 1, 'reg': 524288}, {'tsize': 1, 'reg': 524292}]
        self.checkOpcode(opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr)

        opbytez = '663ac4'
        oprepr = 'cmp al,ah'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 64, 'mnem': 'cmp', 'opcode': 20482, 'size': 3}
        opercheck = [{'tsize': 1, 'reg': 524288}, {'tsize': 1, 'reg': 134742016}]
        self.checkOpcode(opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr)

        opbytez = '673ac4'
        oprepr = 'cmp al,ah'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 128, 'mnem': 'cmp', 'opcode': 20482, 'size': 3}
        opercheck = [{'tsize': 1, 'reg': 524288}, {'tsize': 1, 'reg': 134742016}]
        self.checkOpcode(opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr)

        opbytez = '663ac4'
        oprepr = 'cmp al,ah'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 64, 'mnem': 'cmp', 'opcode': 20482, 'size': 3}
        opercheck = [{'tsize': 1, 'reg': 524288}, {'tsize': 1, 'reg': 134742016}]
        self.checkOpcode(opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr)

        opbytez = '663bc4'
        oprepr = 'cmp ax,sp'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 64, 'mnem': 'cmp', 'opcode': 20482, 'size': 3}
        opercheck = [{'tsize': 2, 'reg': 1048576}, {'tsize': 2, 'reg': 1048580}]
        self.checkOpcode(opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr)

        opbytez = '3bc4'
        oprepr = 'cmp eax,esp'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'cmp', 'opcode': 20482, 'size': 2}
        opercheck = [{'tsize': 4, 'reg': 2097152}, {'tsize': 4, 'reg': 2097156}]
        self.checkOpcode(opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr)

        opbytez = '403bc4'
        oprepr = 'cmp eax,esp'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 1048576, 'mnem': 'cmp', 'opcode': 20482, 'size': 3}
        opercheck = [{'tsize': 4, 'reg': 2097152}, {'tsize': 4, 'reg': 2097156}]
        self.checkOpcode(opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr)

        opbytez = '413bc4'
        oprepr = 'cmp eax,r12d'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 1114112, 'mnem': 'cmp', 'opcode': 20482, 'size': 3}
        opercheck = [{'tsize': 4, 'reg': 2097152}, {'tsize': 4, 'reg': 2097164}]
        self.checkOpcode(opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr)

        opbytez = '66413bc4'
        oprepr = 'cmp ax,r12w'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 1114176, 'mnem': 'cmp', 'opcode': 20482, 'size': 4}
        opercheck = [{'tsize': 2, 'reg': 1048576}, {'tsize': 2, 'reg': 1048588}]
        self.checkOpcode(opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr)

    def test_envi_amd64_disasm_PcRel_Operands(self):
        '''
        test an opcode encoded with an PcRelative operand
        '''
        pass

    def test_envi_amd64_disasm_RegMem_Operands(self):
        '''
        test an opcode encoded with an RegMem operand
        X       outsb       6e
        Y       insd        6d
        '''
        opbytez = '6e'
        oprepr = 'outsb dx,byte [rsi]'
        opcheck =  {'iflags': 131074, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'outsb', 'opcode': 57347, 'size': 1}
        opercheck = [{'tsize': 2, 'reg': 1048578}, {'disp': 0, 'tsize': 1, '_is_deref': True, 'reg': 6}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        opbytez = '6d'
        oprepr = 'insd dword [rsi],dx'
        opcheck =  {'iflags': 131074, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'insd', 'opcode': 57346, 'size': 1}
        opercheck = [{'disp': 0, 'tsize': 4, '_is_deref': True, 'reg': 6}, {'tsize': 2, 'reg': 1048578}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

    def test_envi_amd64_disasm_ImmMem_Operands(self):
        '''
        test an opcode encoded with an ImmMem operand
        O       mov         a1
        '''
        opbytez = 'a1a2345678aabbccdd'
        oprepr = 'mov eax,dword [0xddccbbaa785634a2]'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'mov', 'opcode': 24577, 'size': 9}
        opercheck = [{'tsize': 4, 'reg': 2097152}, {'tsize': 4, '_is_deref': True, 'imm': 15982355518468797602}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

    def test_envi_amd64_disasm_SIB_Operands(self):
        '''
        exercize the entire SIB operand space
        A       jmp         fa
        E       lar         0f02
        Q       cvttps2pi   0f2c
        W       cvttps2pi   0f2c
        with REX:
                mov qword [rsp + r12 * 8 + 32],rdi  4a897ce420
        '''
        opbytez = 'eaa123456789ab'          # this wants more bytes, why?
        oprepr = 'jmp 0xab89:0x674523a1'       # this repr's wrong.  it should be ab89:674523a1
        opcheck =  {'iflags': 131081, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'jmp', 'opcode': 4097, 'size': 7}
        opercheck = [{'tsize': 6, 'imm': 188606631453601}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        opbytez = '0f02aabbccddee'
        oprepr = 'lar ebp,word [rdx - 287454021]'
        opcheck =  {'iflags': 131074, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'lar', 'opcode': 57344, 'size': 7}
        opercheck = [{'tsize': 4, 'reg': 2097157}, {'disp': -287454021, 'tsize': 2, '_is_deref': True, 'reg': 2}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        opbytez = '0f2caabbccddeeff'
        oprepr = 'cvttps2pi mm5,oword [rdx - 287454021]'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'cvttps2pi', 'opcode': 61440, 'size': 7}
        opercheck = [{'tsize': 8, 'reg': 4194387}, {'disp': -287454021, 'tsize': 16, '_is_deref': True, 'reg': 2}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )


        opbytez = '3b80ABCDEF12'
        oprepr = 'cmp eax,dword [rax + 317705643]'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'cmp', 'opcode': 20482, 'size': 6}
        opercheck = [{'tsize': 4, 'reg': 2097152}, {'disp': 317705643, 'tsize': 4, '_is_deref': True, 'reg': 0}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        opbytez = '4a897ce420'
        oprepr = 'mov qword [rsp + r12 * 8 + 32],rdi'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 1703936, 'mnem': 'mov', 'opcode': 24577, 'size': 5}
        opercheck = [{'disp': 32, 'index': 12, 'tsize': 8, 'scale': 8, 'imm': None, '_is_deref': True, 'reg': 4}, {'tsize': 8, 'reg': 7}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )


def generateTestInfo(ophexbytez='6e'):
    a64 = e_amd64.Amd64Module()
    opbytez = ophexbytez
    op = a64.archParseOpcode(binascii.unhexlify(opbytez), 0, 0x4000)
    print("opbytez = '%s'\noprepr = '%s'" % (opbytez, repr(op)))
    opvars = vars(op)
    opers = opvars.pop('opers')
    print("opcheck = %s" % repr(opvars))

    opersvars = []
    for x in range(len(opers)):
        opervars = vars(opers[x])
        opervars.pop('_dis_regctx')
        opersvars.append(opervars)

    print("opercheck = %s" % (repr(opersvars)))
