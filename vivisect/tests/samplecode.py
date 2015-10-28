'''
bits 32

foo:
    push ebp
    mov ebp, esp
    mov ecx,[ebp+8]
    xor edx,edx
    cmp ecx,edx
    jz bar

    mov eax, 1

bar:
    mov eax, 2

baz:
    mov esp, ebp
    pop ebp
    ret
'''
func1 = '5589e58b4d0831d239d17405b801000000b80200000089ec5dc3'.decode('hex')


'''
bits 32

foo:
    push ebp
    mov ebp, esp
    mov ecx,[ebp+8]
    xor edx,edx
    cmp ecx,edx
    jz bar
    jnz boo
    jnc baz
boo:

    mov eax, 1

bar:
    mov eax, 2

baz:
    mov esp, ebp
    pop ebp
    ret

for x in testvw.getCodeBlocks():
    va = x[0]
    while va < x[0]+x[1]:
        op = testvw.parseOpcode(va)
        print hex(op.va), op
        va += len(op)
    print

0x41410000 push ebp
0x41410001 mov ebp,esp
0x41410003 mov ecx,dword [ebp + 8]
0x41410006 xor edx,edx
0x41410008 cmp ecx,edx
0x4141000a jz 0x41410015

0x4141000c jnz 0x41410010

0x4141000e jnc 0x4141001a

0x41410010 mov eax,1

0x41410015 mov eax,2

0x4141001a mov esp,ebp
0x4141001c pop ebp
'''

func2 = '5589e58b4d0831d239d174097502730ab801000000b80200000089ec5dc3'.decode('hex')

'''
bits 64

foo:
    push ebp
    mov ebp, esp
    mov ecx,[ebp+8]
    xor edx,edx
    cmp ecx,edx
    jz bar
    jnz boo
    jnc baz
boo:

    mov eax, 1

bar:
    mov eax, 2

baz:
    mov esp, ebp
    pop ebp
    ret

for x in testvw.getCodeBlocks():
    va = x[0]
    while va < x[0]+x[1]:
        op = testvw.parseOpcode(va)
        print hex(op.va), op
        va += len(op)
    print

0x41410000 push ebp
0x41410001 mov ebp,esp
0x41410003 mov ecx,dword [ebp + 8]
0x41410006 xor edx,edx
0x41410008 cmp ecx,edx
0x4141000a jz 0x41410015

0x4141000c jnz 0x41410010

0x4141000e jnc 0x4141001a

0x41410010 mov eax,1

0x41410015 mov eax,2

0x4141001a mov esp,ebp
0x4141001c pop ebp
'''

func2 = '5589e58b4d0831d239d174097502730ab801000000b80200000089ec5dc3'.decode('hex')
