import vivisect.impapi.windows.i386 as v_w_i386
apitypes = dict(v_w_i386.apitypes)

api = {
}

i386_omits = set([
    'ntdll.seh3_prolog',
    'ntdll.seh4_prolog',
    'ntdll.seh4_gs_prolog',
    'ntdll.seh3_epilog',
    'ntdll.seh4_epilog',
    'ntdll.eh_prolog',
    'ntdll.gs_prolog',
])

for normname,(rtype,rname,cconv,cname,cargs) in v_w_i386.api.items():
    if normname in i386_omits:
        continue

    api[normname] = (rtype,rname,'msx64call',cname,cargs)

