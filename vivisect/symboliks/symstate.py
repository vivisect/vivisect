def var(r,**info):
    return ('var',r,(),info)

def imm(v,**info):
    return ('imm',v,(),info)

def add(a,b,**info):
    return ('oper','+',[a,b],info)

def sub(a,b,**info):
    return ('oper','-',[a,b],info)

def mul(a,b,**info):
    return ('oper','*',[a,b],info)

def shr(a,b,**info):
    return ('oper','>>',[a,b],info)

def shl(a,b,**info):
    return ('oper','<<',[a,b],info)

def rol(a,b,**info):
    return ('oper','FIXME',[a,b],info)

def ror(a,b,**info):
    return ('oper','FIXME',[a,b],info)

def land(a,b,**info):
    return ('oper','&',[a,b],info)

def lor(a,b,**info):
    return ('oper','|',[a,b],info)

def xor(a,b,**info):
    return ('oper','^',[a,b],info)

def mem(addr,size,**info):
    return ('oper','mem',[addr,size],info)

def eq(a,b,**info):
    return ('cond','eq',[a,b],info)

def gt(a,b,**info):
    return ('cond','gt',[a,b],info)

def lt(a,b,**info):
    return ('cond','lt',[a,b],info)
