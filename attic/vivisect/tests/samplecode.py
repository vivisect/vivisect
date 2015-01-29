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

