'''
Analysis plugin for supporting WorkspaceEmulators during analysis pass.
Finds and connects Switch Cases, most specifically from Microsoft.
'''
import envi
import envi.archs.i386 as e_i386

import vivisect
import vivisect.analysis.generic.codeblocks as vagc

def analyzeJmp(amod, emu, op, starteip):
    ''' 
    Top level logic
    '''
    test, ctx = testSwitch(emu.vw, op, starteip, emu)
    if test:
        output = makeSwitch(emu.vw, starteip, ctx['offarraybase'], ctx['indiroffbase'])


def testSwitch(vw, op, vajmp, emu=None):
    '''
    identifies and enumerates microsoft's switch-case methods.
    '''
    if not (op.iflags & envi.IF_BRANCH):
        # vw.verbprint( "indirect branch is not correct type")
        return False,None

    backone = vw.getLocation(vajmp-1)
    if backone == None:
        #vw.verbprint( "previous instruction isn't defined")
        return False,None

    backtwo = vw.getLocation(backone[0]-1)
    if backtwo == None:
        #vw.verbprint( "two previous instruction isn't defined")
        return False,None
    
    filename = vw.getMemoryMap(vajmp)[3]
    imagebase = vw.getFileMeta(filename, 'imagebase')

    op1 = vw.parseOpcode(backone[0])
    if op1.mnem != 'add':
        #vw.verbprint( "previous instruction isn't an 'add'")
        return False,None

    baseoper = op1.opers[1]
    if not isinstance(baseoper, e_i386.i386RegOper):
        #vw.verbprint( "baseoper is not an i386RegOper: %s" % repr(baseoper))
        return False,None

    # this is a weak analysis failure, but a powerful confirmation.
    if emu != None:
        regbase = op1.getOperValue(1, emu)
        if regbase != imagebase:
            vw.verbprint( "reg != imagebase")
            return False,None

    # now check the instruction before that
    op2 = vw.parseOpcode(backtwo[0])
    if op2.mnem != 'mov':
        vw.verbprint( "2nd previous instruction isn't an 'mov'")
        return False,None

    arrayoper = op2.opers[1]
    if not (isinstance(arrayoper, e_i386.i386SibOper) and arrayoper.scale == 4):
        vw.verbprint( "arrayoper is not an i386SibOper of size 4: %s" % repr(baseoper))
        return False,None
    ao_reg = arrayoper.reg & e_i386.RMETA_NMASK
    if  ao_reg != baseoper.reg:
        vw.verbprint( "arrayoper.reg != baseoper.reg: %s != %s" % (ao_reg, baseoper.reg))
        return False,None

    offarraybase = arrayoper.disp
    #initial check of the array.  should point to the next va.  we'll scrape it up later
    offarrayfirst = vw.readMemValue(offarraybase+imagebase, 4)
    if offarrayfirst+imagebase != vajmp+2:
        vw.verbprint( "first ref is not the va after the jmp: %x != %x" % (offarrayfirst+imagebase, vajmp+2))

    indiroffbase = None
    # now check for the byte array before that
    backthree = vw.getLocation(backtwo[0]-1)    # this one is optional. first two are not.
    if backthree != None:
        op = vw.parseOpcode(backthree[0])
        if op.mnem == 'movzx' and isinstance(op.opers[1], e_i386.i386SibOper) and \
                op.opers[1].scale == 1:
            vw.verbprint( "this is a double deref (hitting a byte array offset into the offset-array)")
            indiroffbase = op.opers[1].disp

    return True, {'indiroffbase':indiroffbase, 'offarraybase':offarraybase, }
        
def makeSwitch(vw, vajmp, offarraybase, indiroffbase=None):
    '''
    Makes the changes to the Workspace for the given jmp location.  Handles 
    naming for all cases because naming wants to indicate larger context.

    (future)If indiroffbase is not None, the indirection "database" is analyzed for naming
    '''
    filename = vw.getMemoryMap(vajmp)[3]
    imagebase = vw.getFileMeta(filename, 'imagebase')
    # we have identified this is a switch case
    vw.verbprint( "FOUND MS SWITCH CASE SPRAY at 0x%x" % vajmp)

    # roll through the offset array until imagebase+offset is not a valid pointer, points to non-op locations or splits instructions
    count = 0
    tracker = []
    ptr = offarraybase

    while True:
        off = vw.readMemValue(ptr+imagebase, 4)
        ova = imagebase + off

        tgtva = makeSwitchCase(vw, vajmp, ova)
        if not tgtva:
            break
        
        tracker.append((count, tgtva))
        count += 1
        ptr += 4
       
    # FIXME: this doesn't take into account two-level derefs (indiroffbase)
    naming = {}
    for idx,va in tracker:
        lst = naming.get(va)
        if lst == None:
            lst = []
            naming[va] = lst
        lst.append("%xh" % idx)

    #TODO: analyze indiroffbase to determine case information
    
    for va, opts in naming.items():
        options = "_".join(opts)
        name = "switch_case_%s_%.8x" % (options, va)
        vw.makeName(va, name)

    #TODO: analyze which paths handle which cases, name accordingly
    #TODO: determine good hint for symbolik constraints
    funcva = vw.getFunction(vajmp)
    vw.makeName(vajmp, "jmp_switch_%.8x" % vajmp)
    vagc.analyzeFunction(vw, funcva)
    return tracker

def makeSwitchCase(vw, vaSwitch, vaCase):
    '''
    Handle minutia of each case, specifically, checking for validity and
    making Xref and making code (if necessary)
    '''
    if not vw.isValidPointer(vaCase):
        return False
        
    loc = vw.getLocation(vaCase)
    if loc != None:
        if loc[0] != vaCase:
            return False
        if loc[vivisect.L_LTYPE] != vivisect.LOC_OP:
            return False
    else:
        vw.makeCode(vaCase)
    
    #if we reach here, we're going to assume the location is valid.
    vw.verbprint( "0x%x MS Switch Case Spray: emu.getBranchNode( emu.curpath , 0x%x )" % (vaSwitch, vaCase))
    vw.addXref(vaSwitch, vaCase, vivisect.REF_CODE)

    return vaCase


if globals().get('vw'):
    verbose = vw.verbose
    vw.verbose = True

    vw.vprint("Starting...")
    findSwitchCase(vw)
    vw.vprint("Done")
    
    vw.verbose = verbose
    
