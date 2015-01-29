import envi
import envi.memory as e_mem
import envi.memcanvas as e_memcanvas
import envi.memcanvas.renderers as e_rend
import envi.archs.i386 as e_i386
import vivisect
import platform
import unittest

# name, bytes, va, repr, txtRender
i386SingleByteOpcodes = [
        ('add', '0001', 0x40, 'add byte [ecx],al', 'add byte [ecx],al'),
        ('jg', '7faa', 0x400, 'jg 0x000003ac', 'jg 0x000003ac'),
        ('rep movsb', 'f3a4', 0x40, 'rep: movsb ', 'rep: movsb '),
        ('mov al', 'b0aa', 0x40, 'mov al,170', 'mov al,170'),
        ('mov ebx', 'b8aaaa4040', 0x40, 'mov eax,0x4040aaaa', 'mov eax,0x4040aaaa'),
        ('inc ebx', '43', 0x40, 'inc ebx', 'inc ebx'),
        ('call ebx', 'ffd3', 0x40, 'call ebx', 'call ebx'),
        ('call lit', 'e801010101', 0x40, 'call 0x01010146', 'call 0x01010146'),
        ('mov dword', '89aa41414141', 0x40, 'mov dword [edx + 1094795585],ebp', 'mov dword [edx + 1094795585],ebp'),
        ('imul 1', 'f6aaaaaaaaaa', 0x40, 'imul al,byte [edx - 1431655766]', 'imul al,byte [edx - 1431655766]'),
        ('imul 2', 'f7aaaaaaaaaa', 0x40, 'imul eax,dword [edx - 1431655766]', 'imul eax,dword [edx - 1431655766]'),
        ('push', 'fff0', 0x40, 'push eax', 'push eax'),
        ('pop', '8ff0', 0x40, 'pop eax', 'pop eax'),
        ('pop', '8ffb', 0x40, 'pop ebx', 'pop ebx'),
        ]
i386MultiByteOpcodes = [
        ('CVTTPS2PI', '0f2caaaaaaaa41', 0x40, 'cvttps2pi qword [edx + 1101703850],oword [edx + 1101703850]', 'cvttps2pi qword [edx + 1101703850],oword [edx + 1101703850]'),
        ('CVTTSS2SI', 'f30f2caaaaaaaa41', 0x40, 'rep: cvttps2pi qword [edx + 1101703850],oword [edx + 1101703850]', 'rep: cvttps2pi qword [edx + 1101703850],oword [edx + 1101703850]'),
        ('CVTTPD2PI', '660f2caaaaaaaa41', 0x40, 'cvttpd2pi oword [edx + 1101703850],oword [edx + 1101703850]', 'cvttpd2pi oword [edx + 1101703850],oword [edx + 1101703850]'),
        ('CVTTSD2SI', 'f20f2caaaaaaaa41', 0x40, 'repnz: cvttps2pi qword [edx + 1101703850],oword [edx + 1101703850]', 'repnz: cvttps2pi qword [edx + 1101703850],oword [edx + 1101703850]'),
        ('ADDPS', '0f58aa4141414141', 0x40, 'addps xmm5,oword [edx + 1094795585]', 'addps xmm5,oword [edx + 1094795585]'),
        ('MOVAPS', '0f28aa41414141', 0x40, 'movaps xmm5,oword [edx + 1094795585]', 'movaps xmm5,oword [edx + 1094795585]'),
        ('MOVAPD', '660f28aa41414141', 0x40, 'movapd xmm5,oword [edx + 1094795585]', 'movapd xmm5,oword [edx + 1094795585]'),
        ('PMULLW (66)', '660faa41414141', 0x40, 'rsm ', 'rsm '),
        ('CMPXCH8B', '0fc70a', 0x40, 'cmpxch8b qword [edx]', 'cmpxch8b qword [edx]'),
        ('PSRLDQ (66)', '660f73faaa4141', 0x40, 'psldq xmm7,250', 'psldq xmm7,250'),
        ('PSRLDQ (66)', '660f73b5aa4141', 0x40, 'psllq xmm6,181', 'psllq xmm6,181'),
        ('PSRLDQ (66)', '660f73b1aa4141', 0x40, 'psllq xmm6,177', 'psllq xmm6,177'),
        ('PSRLDQ (66)', '660f73b9aa4141', 0x40, 'psldq xmm7,185', 'psldq xmm7,185'),
    ]
class i386InstructionSet(unittest.TestCase):
    _arch = envi.getArchModule("i386")

    def test_envi_i386_disasm_Specific_SingleByte_Instrs(self):
        '''
        pick 10 arbitrary 1-byte-operands
        '''
        mem = e_mem.IMemory()
        vw = vivisect.VivWorkspace()
        scanv = e_memcanvas.StringMemoryCanvas(vw)

        for name, bytez, va, reprOp, renderOp in i386SingleByteOpcodes:

            op = self._arch.archParseOpcode(bytez.decode('hex'), 0, va)
            #print "'%s', 0x%x, '%s' == '%s'" % (bytez, va, repr(op), reprOp)
            self.assertEqual( repr(op), reprOp )

            scanv.clearCanvas()
            op.render(scanv)
            #print "render:  %s" % repr(scanv.strval)
            self.assertEqual( scanv.strval, renderOp )

    def test_envi_i386_disasm_Specific_MultiByte_Instrs(self):
        '''
        pick 10 arbitrary 2- and 3-byte operands
        '''
        mem = e_mem.IMemory()
        vw = vivisect.VivWorkspace()
        scanv = e_memcanvas.StringMemoryCanvas(vw)

        for name, bytez, va, reprOp, renderOp in i386MultiByteOpcodes:

            op = self._arch.archParseOpcode(bytez.decode('hex'), 0, va)
            #print "'%s', 0x%x, '%s' == '%s'" % (bytez, va, repr(op), reprOp)
            self.assertEqual( repr(op), reprOp )

            scanv.clearCanvas()
            op.render(scanv)
            #print "render:  %s" % repr(scanv.strval)
            self.assertEqual( scanv.strval, renderOp )
    '''
    def test_envi_i386_disasm_A(self):
        pass
    def test_envi_i386_disasm_C(self):
        pass
    def test_envi_i386_disasm_D(self):
        pass
    def test_envi_i386_disasm_E(self):
        pass
    def test_envi_i386_disasm_F(self):
        pass
    def test_envi_i386_disasm_G(self):
        pass
    def test_envi_i386_disasm_I(self):
        pass
    def test_envi_i386_disasm_J(self):
        pass
    def test_envi_i386_disasm_M(self):
        pass
    def test_envi_i386_disasm_N(self):
        pass
    def test_envi_i386_disasm_O(self):
        pass
    def test_envi_i386_disasm_P(self):
        pass
    def test_envi_i386_disasm_Q(self):
        pass
    def test_envi_i386_disasm_R(self):
        pass
    def test_envi_i386_disasm_S(self):
        pass
    def test_envi_i386_disasm_U(self):
        pass
    def test_envi_i386_disasm_V(self):
        pass
    def test_envi_i386_disasm_W(self):
        pass
    def test_envi_i386_disasm_X(self):
        pass
    def test_envi_i386_disasm_Y(self):
        pass
    '''

    def checkOpcode(self, hexbytez, va, oprepr, opcheck, opercheck, renderOp):

        op = self._arch.archParseOpcode(hexbytez.decode('hex'), 0, va)

        self.assertEqual( repr(op), oprepr )
        opvars = vars(op)
        for opk,opv in opcheck.items():
            #print "op: %s %s" % (opk,opv)
            self.assertEqual( (opk, opvars.get(opk)), (opk, opv) )

        for oidx in range(len(op.opers)):
            oper = op.opers[oidx]
            opervars = vars(oper)
            for opk,opv in opercheck[oidx].items():
                #print "oper: %s %s" % (opk,opv)
                self.assertEqual( (opk, opervars.get(opk)), (opk, opv) )

        vw = vivisect.VivWorkspace()
        scanv = e_memcanvas.StringMemoryCanvas(vw)
        op.render(scanv)
        #print "render:  %s" % repr(scanv.strval)
        self.assertEqual( scanv.strval, renderOp )

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
        opcheck =  {'iflags': 65536, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'add', 'opcode': 8193, 'size': 2}
        opercheck = [{'disp': 0, 'tsize': 1, '_is_deref': True, 'reg': 2}, {'tsize': 1, 'reg': 134742018}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        opbytez = '0440'
        oprepr = 'add al,64'
        opcheck = {'iflags': 65536, 'prefixes': 0, 'mnem': 'add', 'opcode': 8193, 'size': 2}
        opercheck = ( {'tsize': 1, 'reg': 524288}, {'tsize': 1, 'imm': 64} )
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        opbytez = '0218'
        oprepr = 'add bl,byte [eax]'
        opcheck = {'iflags': 65536, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'add', 'opcode': 8193, 'size': 2}
        opercheck = ( {'tsize': 1, 'reg': 524291}, {'disp': 0, 'tsize': 1, '_is_deref': True, 'reg': 0} )
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        opbytez = '0f2018'
        oprepr = 'mov dword [eax],ctrl3'
        opcheck =  {'iflags': 65536, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'mov', 'opcode': 24577, 'size': 3}
        opercheck = ( {'disp': 0, 'tsize': 4, '_is_deref': True, 'reg': 0}, {'tsize': 4, 'reg': 35} )
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
        opcheck =  {'iflags': 65538, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'outsb', 'opcode': 57347, 'size': 1}
        opercheck = [{'tsize': 4, 'reg': 2}, {'disp': 0, 'tsize': 1, '_is_deref': True, 'reg': 6}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

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
        A       jmp         fa
        E       lar         0f02
        Q       cvttps2pi   0f2c
        W       cvttps2pi   0f2c
        '''
        opbytez = 'eaa123456789ab'          # this wants more bytes, why?
        oprepr = 'jmp 0xab89:0x674523a1'       # this repr's wrong.  it should be ab89:674523a1
        opcheck =  {'iflags': 65545, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'jmp', 'opcode': 4097, 'size': 7}
        opercheck = [{'tsize': 6, 'imm': 188606631453601}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        opbytez = '0f02aabbccddee'
        oprepr = 'lar ebp,word [edx - 287454021]'
        opcheck =  {'iflags': 65538, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'lar', 'opcode': 57344, 'size': 7}
        opercheck = [{'tsize': 4, 'reg': 5}, {'disp': -287454021, 'tsize': 2, '_is_deref': True, 'reg': 2}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        opbytez = '0f2caabbccddeeff'
        oprepr = 'cvttps2pi qword [edx - 287454021],oword [edx - 287454021]'
        opcheck =  {'iflags': 65536, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'cvttps2pi', 'opcode': 61440}
        opercheck = [{'disp': -287454021, 'tsize': 8, '_is_deref': True, 'reg': 2}, {'disp': -287454021, 'tsize': 16, '_is_deref': True, 'reg': 2}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

