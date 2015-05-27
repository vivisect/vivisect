
import envi
import envi.memory as e_mem
import envi.memcanvas as e_memcanvas
import envi.memcanvas.renderers as e_rend
import envi.archs.h8 as e_h8
import vivisect
import platform
import unittest

instrs = [
        ( "8342", 0x4560, 'add.b #42, r3h'),
        ( "7c6075f0", 0x4560, 'bixor #7, @er6'),
        ( "7d707170", 0x4560, 'bnot #7, @er7'),
        ( "0832", 0x4560, 'add.b r3h, r2h'),
        ( "791d4745", 0x4560, 'add.w #4745, e5'),
        ( "0932", 0x4560, 'add.w r3, r2'),
        ( "7a1d00047145", 0x4560, 'add.l #47145, er5'),
        ( "0aa7", 0x4560, 'add.w r3, r2'),
        ( "0b07", 0x4560, 'add.w r3, r2'),
        ( "0b87", 0x4560, 'add.w r3, r2'),
        ( "0b97", 0x4560, 'add.w r3, r2'),
        ( "01406930", 0x4560, 'ldc @er3, ccr'),
        ( "014069b0", 0x4560, 'stc ccr, @er3'),
        ( "01c05023", 0x4560, 'mulxs.b r2h, r3'),
        ( "01c05223", 0x4560, 'mulxs.w r2, er3'),
        ( "01d05123", 0x4560, 'divxs.b r2h, r3'),
        ( "01d05323", 0x4560, 'divxs.w r2, er3'),
        ( "01f06423", 0x4560, 'or.l er2, er3'),
        ( "01f06523", 0x4560, 'xor.l er2, er3'),
        ( "01f06623", 0x4560, 'and.l er2, er3'),
        ( "0a03", 0x4560, 'inc.b r3h'),
        ( "0a83", 0x4560, 'add.l er0, er3'),
        ( "0b83", 0x4560, 'adds.l #2, er3'),
        ( "0b93", 0x4560, 'adds.l #4, er3'),
        ( "0b53", 0x4560, 'inc.w #1, r3'),
        ( "0bf3", 0x4560, 'inc.l #2, er3'),

        ]

class H8InstrTest(unittest.TestCase):
    def test_envi_h8_assorted_instrs(self):
       global instrs

       archmod = envi.getArchModule("h8")

       for bytez, va, reprOp in instrs:
           op = archmod.archParseOpcode(bytez.decode('hex'), 0, va)
           if repr(op).replace(' ','') != reprOp.replace(' ',''):
               raise Exception("FAILED to decode instr:  %.8x %s - should be: %s  - is: %s" % \
                       ( va, bytez, reprOp, repr(op) ) )

    #FIXME: test emuluation as well.


# name, bytes, va, repr, txtRender
h8SingleByteOpcodes = [
        ('add', '0001', 0x40, 'add byte [rcx],al', 'add byte [rcx],al'),
        ('jg', '7faa', 0x400, 'jg 0x000003ac', 'jg 0x000003ac'),
        ('rep movsb', 'f3a4', 0x40, 'rep: movsb ', 'rep: movsb '),
        ('mov al', 'b0aa', 0x40, 'mov al,170', 'mov al,170'),
        ('mov ebx', 'b8aaaa4040', 0x40, 'mov eax,0x4040aaaa', 'mov eax,0x4040aaaa'),
        ('call ebx', 'ffd3', 0x40, 'call rbx', 'call rbx'),
        ('call lit', 'e801010101', 0x40, 'call 0x01010146', 'call 0x01010146'),
        ('mov dword', '89aa41414141', 0x40, 'mov dword [rdx + 1094795585],ebp', 'mov dword [rdx + 1094795585],ebp'),
        ('imul 1', 'f6aaaaaaaaaa', 0x40, 'imul al,byte [rdx - 1431655766]', 'imul al,byte [rdx - 1431655766]'),
        ('imul 2', 'f7aaaaaaaaaa', 0x40, 'imul eax,dword [rdx - 1431655766]', 'imul eax,dword [rdx - 1431655766]'),
        ('push', 'fff0', 0x40, 'push eax', 'push eax'),
        ('pop', '8ff0', 0x40, 'pop eax', 'pop eax'),
        ('pop', '8ffb', 0x40, 'pop ebx', 'pop ebx'),
        ('push', '48fff0', 0x40, 'push rax', 'push rax'),
        ('pop', '488ff0', 0x40, 'pop rax', 'pop rax'),
        ('pop', '488ffb', 0x40, 'pop rbx', 'pop rbx'),
        ]
h8MultiByteOpcodes = [
        ('CVTTPS2PI', '0f2caaaaaaaa41', 0x40, 'cvttps2pi mm5,oword [rdx + 1101703850]', 'cvttps2pi mm5,oword [rdx + 1101703850]'),
        ('CVTTSS2SI', 'f30f2caaaaaaaa41', 0x40, 'cvttss2si ebp,oword [rdx + 1101703850]', 'cvttss2si ebp,oword [rdx + 1101703850]'),
        ('CVTTPD2PI', '660f2caaaaaaaa41', 0x40, 'cvttpd2pi mm5,oword [rdx + 1101703850]', 'cvttpd2pi mm5,oword [rdx + 1101703850]'),
        ('CVTTSD2SI', 'f20f2caaaaaaaa41', 0x40, 'cvttsd2si ebp,oword [rdx + 1101703850]', 'cvttsd2si ebp,oword [rdx + 1101703850]'),
        ('ADDPS', '0f58aa4141414141', 0x40, 'addps xmm5,oword [rdx + 1094795585]', 'addps xmm5,oword [rdx + 1094795585]'),
        ('MOVAPS', '0f28aa41414141', 0x40, 'movaps xmm5,oword [rdx + 1094795585]', 'movaps xmm5,oword [rdx + 1094795585]'),
        ('MOVAPD', '660f28aa41414141', 0x40, 'movapd xmm5,oword [rdx + 1094795585]', 'movapd xmm5,oword [rdx + 1094795585]'),
        ('PMULLW (66)', '660faa41414141', 0x40, 'rsm ', 'rsm '),
        ('CMPXCH8B', '0fc70a', 0x40, 'cmpxch8b qword [rdx]', 'cmpxch8b qword [rdx]'),
        ('PSRLDQ (66)', '660f73faaa4141', 0x40, 'psldq xmm7,250', 'psldq xmm7,250'),
        ('PSRLDQ (66)', '660f73b5aa4141', 0x40, 'psllq xmm6,181', 'psllq xmm6,181'),
        ('PSRLDQ (66)', '660f73b1aa4141', 0x40, 'psllq xmm6,177', 'psllq xmm6,177'),
        ('PSRLDQ (66)', '660f73b9aa4141', 0x40, 'psldq xmm7,185', 'psldq xmm7,185'),
    ]
class H8InstructionSet(unittest.TestCase):
    _arch = envi.getArchModule("h8")

    def test_envi_h8_disasm_Specific_SingleByte_Instrs(self):
        '''
        pick 10 arbitrary 1-byte-operands
        '''
        vw = vivisect.VivWorkspace()
        scanv = e_memcanvas.StringMemoryCanvas(vw)

        for name, bytez, va, reprOp, renderOp in h8SingleByteOpcodes:

            op = self._arch.archParseOpcode(bytez.decode('hex'), 0, va)
            #print "'%s', 0x%x, '%s' == '%s'" % (bytez, va, repr(op), reprOp)
            self.assertEqual( repr(op), reprOp )

            scanv.clearCanvas()
            op.render(scanv)
            #print "render:  %s" % repr(scanv.strval)
            self.assertEqual( scanv.strval, renderOp )

    def test_envi_h8_disasm_Specific_MultiByte_Instrs(self):
        '''
        pick 10 arbitrary 2- and 3-byte operands
        '''
        vw = vivisect.VivWorkspace()
        scanv = e_memcanvas.StringMemoryCanvas(vw)

        for name, bytez, va, reprOp, renderOp in h8MultiByteOpcodes:

            op = self._arch.archParseOpcode(bytez.decode('hex'), 0, va)
            #print "'%s', 0x%x, '%s' == '%s'" % (bytez, va, repr(op), reprOp)
            self.assertEqual( repr(op), reprOp )

            scanv.clearCanvas()
            op.render(scanv)
            #print "render:  %s" % repr(scanv.strval)
            self.assertEqual( scanv.strval, renderOp )

    def checkOpcode(self, hexbytez, va, oprepr, opcheck, opercheck, renderOp):

        op = self._arch.archParseOpcode(hexbytez.decode('hex'), 0, va)

        self.assertEqual( repr(op), oprepr )
        opvars = vars(op)
        for opk,opv in opcheck.items():
            #print "op: %s %s" % (opk,opv)
            self.assertEqual( (repr(op), opk, opvars.get(opk)), (oprepr, opk, opv) )

        for oidx in range(len(op.opers)):
            oper = op.opers[oidx]
            opervars = vars(oper)
            for opk,opv in opercheck[oidx].items():
                #print "oper: %s %s" % (opk,opv)
                self.assertEqual( (repr(op), opk, opervars.get(opk)), (oprepr, opk, opv) )

        vw = vivisect.VivWorkspace()
        scanv = e_memcanvas.StringMemoryCanvas(vw)
        op.render(scanv)
        #print "render:  %s" % repr(scanv.strval)
        self.assertEqual( scanv.strval, renderOp )


    
    ###############################################
    # only pick the operands special to 64-bit mode
    def test_envi_h8_disasm_Reg_Operands(self):
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
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        opbytez = '480032'
        oprepr = 'add byte [rdx],sil'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 1572864, 'mnem': 'add', 'opcode': 8193, 'size': 3}
        opercheck = [{'disp': 0, 'tsize': 1, '_is_deref': True, 'reg': 2}, {'tsize': 1, 'reg': 524294}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        opbytez = '480132'
        oprepr = 'add qword [rdx],rsi'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 1572864, 'mnem': 'add', 'opcode': 8193, 'size': 3}
        opercheck = [{'disp': 0, 'tsize': 8, '_is_deref': True, 'reg': 2}, {'tsize': 8, 'reg': 6}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        opbytez = '0440'
        oprepr = 'add al,64'
        opcheck = {'iflags': 131072, 'prefixes': 0, 'mnem': 'add', 'opcode': 8193, 'size': 2}
        opercheck = ( {'tsize': 4, 'reg': 524288}, {'tsize': 4, 'imm': 64} )
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        opbytez = '0218'
        oprepr = 'add bl,byte [rax]'
        opcheck = {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'add', 'opcode': 8193, 'size': 2}
        opercheck = ( {'tsize': 1, 'reg': 524291}, {'disp': 0, 'tsize': 1, '_is_deref': True, 'reg': 0} )
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        opbytez = '0f2018'
        oprepr = 'mov dword [rax],ctrl3'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'mov', 'opcode': 24577, 'size': 3}
        opercheck = ( {'disp': 0, 'tsize': 4, '_is_deref': True, 'reg': 0}, {'tsize': 4, 'reg': 59} )
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        for x in range(0xb0, 0xb8):
            bytez = '41%.2xAAAAAAAA' % x
            op = self._arch.archParseOpcode((bytez).decode('hex'),0,0x1000)
            self.assertEqual( (bytez, hex(op.opers[0].reg)), (bytez, hex( 0x80000 + (x-0xa8) )) )

        for x in range(0xb8, 0xc0):
            bytez = '41%.2xAAAAAAAA' % x
            op = self._arch.archParseOpcode((bytez).decode('hex'),0,0x1000)
            self.assertEqual( (bytez, hex(op.opers[0].reg)), (bytez, hex( 0x200000 + (x-0xb0) )) )




    def test_envi_h8_disasm_Imm_Operands(self):
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

        #In [3]: generateTestInfo('413ac4')
        opbytez = '413ac4'
        oprepr = 'cmp al,r12l'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 1114112, 'mnem': 'cmp', 'opcode': 20482, 'size': 3}
        opercheck = [{'tsize': 1, 'reg': 524288}, {'tsize': 1, 'reg': 524300}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        #In [4]: generateTestInfo('453ac4')
        opbytez = '453ac4'
        oprepr = 'cmp r8l,r12l'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 1376256, 'mnem': 'cmp', 'opcode': 20482, 'size': 3}
        opercheck = [{'tsize': 1, 'reg': 524296}, {'tsize': 1, 'reg': 524300}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        #In [5]: generateTestInfo('473ac4')
        opbytez = '473ac4'
        oprepr = 'cmp r8l,r12l'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 1507328, 'mnem': 'cmp', 'opcode': 20482, 'size': 3}
        opercheck = [{'tsize': 1, 'reg': 524296}, {'tsize': 1, 'reg': 524300}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        #In [3]: generateTestInfo('3ac4')
        opbytez = '3ac4'
        oprepr = 'cmp al,ah'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'cmp', 'opcode': 20482, 'size': 2}
        opercheck = [{'tsize': 1, 'reg': 524288}, {'tsize': 1, 'reg': 134742016}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        #In [4]: generateTestInfo('403ac4')
        opbytez = '403ac4'
        oprepr = 'cmp al,spl'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 1048576, 'mnem': 'cmp', 'opcode': 20482, 'size': 3}
        opercheck = [{'tsize': 1, 'reg': 524288}, {'tsize': 1, 'reg': 524292}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        #In [5]: generateTestInfo('663ac4')
        opbytez = '663ac4'
        oprepr = 'cmp al,ah'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 64, 'mnem': 'cmp', 'opcode': 20482, 'size': 3}
        opercheck = [{'tsize': 1, 'reg': 524288}, {'tsize': 1, 'reg': 134742016}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        #In [6]: generateTestInfo('673ac4')
        opbytez = '673ac4'
        oprepr = 'cmp al,ah'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 128, 'mnem': 'cmp', 'opcode': 20482, 'size': 3}
        opercheck = [{'tsize': 1, 'reg': 524288}, {'tsize': 1, 'reg': 134742016}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        #In [7]: generateTestInfo('663ac4')
        opbytez = '663ac4'
        oprepr = 'cmp al,ah'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 64, 'mnem': 'cmp', 'opcode': 20482, 'size': 3}
        opercheck = [{'tsize': 1, 'reg': 524288}, {'tsize': 1, 'reg': 134742016}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        #In [9]: generateTestInfo('663bc4')
        opbytez = '663bc4'
        oprepr = 'cmp ax,sp'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 64, 'mnem': 'cmp', 'opcode': 20482, 'size': 3}
        opercheck = [{'tsize': 2, 'reg': 1048576}, {'tsize': 2, 'reg': 1048580}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        #In [10]: generateTestInfo('3bc4')
        opbytez = '3bc4'
        oprepr = 'cmp eax,esp'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'cmp', 'opcode': 20482, 'size': 2}
        opercheck = [{'tsize': 4, 'reg': 2097152}, {'tsize': 4, 'reg': 2097156}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        #In [11]: generateTestInfo('403bc4')
        opbytez = '403bc4'
        oprepr = 'cmp eax,esp'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 1048576, 'mnem': 'cmp', 'opcode': 20482, 'size': 3}
        opercheck = [{'tsize': 4, 'reg': 2097152}, {'tsize': 4, 'reg': 2097156}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        #In [12]: generateTestInfo('413bc4')
        opbytez = '413bc4'
        oprepr = 'cmp eax,r12d'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 1114112, 'mnem': 'cmp', 'opcode': 20482, 'size': 3}
        opercheck = [{'tsize': 4, 'reg': 2097152}, {'tsize': 4, 'reg': 2097164}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        #In [13]: generateTestInfo('66413bc4')
        opbytez = '66413bc4'
        oprepr = 'cmp ax,r12w'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 1114176, 'mnem': 'cmp', 'opcode': 20482, 'size': 4}
        opercheck = [{'tsize': 2, 'reg': 1048576}, {'tsize': 2, 'reg': 1048588}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )



    def test_envi_h8_disasm_PcRel_Operands(self):
        '''
        test an opcode encoded with an PcRelative operand
        '''
        pass

    def test_envi_h8_disasm_RegMem_Operands(self):
        '''
        test an opcode encoded with an RegMem operand
        X       outsb       6e
        Y       insd        6d
        '''
        opbytez = '6e'
        oprepr = 'outsb dx,byte [rsi]'
        opcheck =  {'iflags': 131074, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'outsb', 'opcode': 57347, 'size': 1}
        opercheck = [{'tsize': 4, 'reg': 1048578}, {'disp': 0, 'tsize': 1, '_is_deref': True, 'reg': 6}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        opbytez = '6d'
        oprepr = 'insd dword [rsi],dx'
        opcheck =  {'iflags': 131074, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'insd', 'opcode': 57346, 'size': 1}
        opercheck = [{'disp': 0, 'tsize': 4, '_is_deref': True, 'reg': 6}, {'tsize': 4, 'reg': 1048578}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

    def test_envi_h8_disasm_ImmMem_Operands(self):
        '''
        test an opcode encoded with an ImmMem operand
        O       mov         a1
        '''
        opbytez = 'a1a2345678aabbccdd'
        oprepr = 'mov eax,dword [0xddccbbaa785634a2]'
        opcheck =  {'iflags': 131072, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'mov', 'opcode': 24577, 'size': 9}
        opercheck = [{'tsize': 4, 'reg': 2097152}, {'tsize': 4, '_is_deref': True, 'imm': 15982355518468797602L}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

    def test_envi_h8_disasm_SIB_Operands(self):
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
        opercheck = [{'tsize': 8, 'reg': 21}, {'disp': -287454021, 'tsize': 16, '_is_deref': True, 'reg': 2}]
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
    h8 = e_h8.H8Module()
    opbytez = ophexbytez
    op = h8.archParseOpcode(opbytez.decode('hex'), 0, 0x4000)
    print "opbytez = '%s'\noprepr = '%s'"%(opbytez,repr(op))
    opvars=vars(op)
    opers = opvars.pop('opers')
    print "opcheck = ",repr(opvars)

    opersvars = []
    for x in range(len(opers)):
        opervars = vars(opers[x])
        opervars.pop('_dis_regctx')
        opersvars.append(opervars)

    print "opercheck = %s" % (repr(opersvars))

