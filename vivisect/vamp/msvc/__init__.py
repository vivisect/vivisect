"""
envi.bytesig signature stuff for Microsoft Visual Studio
"""
import binascii

import envi.bytesig as e_bytesig

sigs = [
    ('680000000064a10000000050', 'ff00000000ffffffffffffff','ntdll.seh3_prolog'),
    ('8b4df064890d00000000595f5e5bc951c3', None, 'ntdll.seh3_epilog'),
    ('8b4df064890d00000000595f5f5e5b8be55d51c3', None, 'ntdll.seh4_epilog'),
    ('680000000064ff35000000008b442410', 'ff00000000ffffffffffffffffffffff', 'ntdll.seh4_prolog'),
    ('a10000000033c58945fc','ff00000000ffffffffff','ntdll.gs_prolog'),
    ('518d4c24042bc81bc0f7d023c88bc42500f0ffff3bc8720a8bc159948b00890424c32d001000008500ebe9', None, 'ntdll.gs_prolog'), # takes only stack delta!
    ('3b0d000000000f85afdc0200c3', 'ffff00000000ffffffffffffff', 'ntdll.security_check_cookie'),
    ('8bff558bec5151a300000000890d00000000891500000000891d00000000893500000000893d000000008c15000000008c0d000000008c1d000000008c05000000008c25000000008c2d000000009c',
     'ffffffffffffffff00000000ffff00000000ffff00000000ffff00000000ffff00000000ffff00000000ffff00000000ffff00000000ffff00000000ffff00000000ffff00000000ffff00000000ff',
     'ntdll.report_gsfailure',
    ),

    ('8bff558bec81ec28030000a300000000890d00000000891500000000891d00000000893500000000893d00000000668c1500000000668c0d00000000668c1d00000000668c0500000000668c2500000000668c2d000000009c',
     'ffffffffffffffffffffffff00000000ffff00000000ffff00000000ffff00000000ffff00000000ffff00000000ffffff00000000ffffff00000000ffffff00000000ffffff00000000ffffff00000000ffffff00000000ff',
     'ntdll.report_gsfailure',
    ),

    ('3b0d000000007502f3c3e9', 'ffff00000000ffffffffff','ntdll.security_check_cookie'),
    ('6aff5064a100000000508b44240c64892500000000896c240c8d6c240c50c3',None, 'ntdll.eh_prolog'),
    ('513d001000008d4c2408721481e9001000002d0010000085013d0010000073ec2bc88bc485018be18b088b400450c3', None, 'ntdll._alloca_probe')

]

class VisualStudioVamp(e_bytesig.SignatureTree):

    def __init__(self):
        e_bytesig.SignatureTree.__init__(self)
        for bytez, masks, fname in sigs:
            bytez = binascii.unhexlify(bytez)
            if masks is not None:
                masks = binascii.unhexlify(masks)
            self.addSignature(bytez, masks=masks, val=fname)

# seh3_prolog
#.text:0x7c8024d6  68c09a837c       push kernel32.seh3_handler
#.text:0x7c8024db  64a100000000     fs: mov eax,dword [0x00000000]
#.text:0x7c8024e1  50               push eax
#.text:0x7c8024e2  8b442410         mov eax,dword [esp + 16]
#.text:0x7c8024e6  896c2410         mov dword [esp + 16],ebp
#.text:0x7c8024ea  8d6c2410         lea ebp,dword [esp + 16]
#.text:0x7c8024ee  2be0             sub esp,eax
#.text:0x7c8024f0  53               push ebx
#.text:0x7c8024f1  56               push esi
#.text:0x7c8024f2  57               push edi
#.text:0x7c8024f3  8b45f8           mov eax,dword [ebp - 8]
#.text:0x7c8024f6  8965e8           mov dword [ebp - 24],esp
#.text:0x7c8024f9  50               push eax
#.text:0x7c8024fa  8b45fc           mov eax,dword [ebp - 4]
#.text:0x7c8024fd  c745fcffffffff   mov dword [ebp - 4],4294967295
#.text:0x7c802504  8945f8           mov dword [ebp - 8],eax
#.text:0x7c802507  8d45f0           lea eax,dword [ebp - 16]
#.text:0x7c80250a  64a300000000     fs: mov dword [0x00000000],eax
#.text:0x7c802510  c3               ret 

# seh3_epilog
#.text:0x7c802511  8b4df0           mov ecx,dword [ebp - 16]
#.text:0x7c802514  64890d00000000   fs: mov dword [0x00000000],ecx
#.text:0x7c80251b  59               pop ecx
#.text:0x7c80251c  5f               pop edi
#.text:0x7c80251d  5e               pop esi
#.text:0x7c80251e  5b               pop ebx
#.text:0x7c80251f  c9               leave 
#.text:0x7c802520  51               push ecx
#.text:0x7c802521  c3               ret 


# seh4_prolog
#.text:0x00402390  68f0234000       push hello.seh4_handler
#.text:0x00402395  64ff3500000000   fs: push dword [0x00000000]
#.text:0x0040239c  8b442410         mov eax,dword [esp + 16]
#.text:0x004023a0  896c2410         mov dword [esp + 16],ebp
#.text:0x004023a4  8d6c2410         lea ebp,dword [esp + 16]
#.text:0x004023a8  2be0             sub esp,eax
#.text:0x004023aa  53               push ebx
#.text:0x004023ab  56               push esi
#.text:0x004023ac  57               push edi
#.text:0x004023ad  a110c44000       mov eax,dword [loc_0040c410]
#.text:0x004023b2  3145fc           xor dword [ebp - 4],eax
#.text:0x004023b5  33c5             xor eax,ebp
#.text:0x004023b7  50               push eax
#.text:0x004023b8  8965e8           mov dword [ebp - 24],esp
#.text:0x004023bb  ff75f8           push dword [ebp - 8]
#.text:0x004023be  8b45fc           mov eax,dword [ebp - 4]
#.text:0x004023c1  c745fcfeffffff   mov dword [ebp - 4],4294967294
#.text:0x004023c8  8945f8           mov dword [ebp - 8],eax
#.text:0x004023cb  8d45f0           lea eax,dword [ebp - 16]
#.text:0x004023ce  64a300000000     fs: mov dword [0x00000000],eax
#.text:0x004023d4  c3               ret 

# seh4_epilog
#.text:0x004025e9  8b4df0           mov ecx,dword [ebp - 16]
#.text:0x004025ec  64890d00000000   fs: mov dword [0x00000000],ecx
#.text:0x004025f3  59               pop ecx
#.text:0x004025f4  5f               pop edi
#.text:0x004025f5  5f               pop edi
#.text:0x004025f6  5e               pop esi
#.text:0x004025f7  5b               pop ebx
#.text:0x004025f8  8be5             mov esp,ebp
#.text:0x004025fa  5d               pop ebp
#.text:0x004025fb  51               push ecx
#.text:0x004025fc  c3               ret 

# gs_prolog_chunk
#.text:0x00409362  a11cc04000       mov eax,dword [GS_COOKIE]
#.text:0x00409367  33c5             xor eax,ebp
#.text:0x00409369  8945fc           mov dword [ebp - 4],eax

# GS PROLOG CAN JUST TAKE LOCALS SIZE!

# GS Epilog (is ecx ok chunk)
#.text:0x0040119a  3b0d1cc04000     cmp ecx,dword [GS_COOKIE]
#.text:0x004011a0  7502             jnz loc_004011a4
#.text:0x004011a2  f3c3             rep: ret 
#.text:0x004011a4  loc_004011a4: [1 XREFS]
#.text:0x004011a4  e903160000       jmp loc_004027ac

# Also  __report_gs_failure is loc_004027ac at this point

# EH Prolog:
#6aff             push 255
#50               push eax                          ; Create the new record
#64a100000000     fs: mov eax,dword [0x00000000]
#50               push eax                          ; Grab and save off the next
#8b44240c         mov eax,dword [esp + local_1]     ; Saved EIP -> eax
#64892500000000   fs: mov dword [0x00000000],esp    ; ptr to 3 dword record into FS:0
#896c240c         mov dword [esp + local_1],ebp     ; Put old EBP into saved EIP spot (esp now delta 16 total)
#8d6c240c         lea ebp,dword [esp + local_1]     ; Make ebp point to itself
#50               push eax
#c3               ret 


