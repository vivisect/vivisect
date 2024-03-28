import vivisect.impapi.winkern.i386 as v_k_i386

apitypes = dict(v_k_i386.apitypes)

api = {}
for normname, (rtype, rname, cconv, cname, cargs) in v_k_i386.api.items():
    api[normname] = (rtype, rname, 'msx64call', cname, cargs)
