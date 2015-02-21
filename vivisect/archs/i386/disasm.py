from vivisect.lib.bits import *
from vivisect.lib.disasm import Decoder,InvalidDecode

i386prefixes = {
    0xf0:'lock',
    0xf2:'repnz',
    0xf3:'rep',
    0x2e:'cs',
    0x36:'ss',
    0x3e:'ds',
    0x26:'es',
    0x64:'fs',
    0x65:'gs',
    0x66:'',    # toggle data size
    0x67:'',    # toggle addr size
}

i386prefix_masks = [ (int2bits(p,8),p) for p in i386prefixes.keys() ]

'''
bitfield conventions for i386:
S   - scale bits from sib
I   - index bits from sib
B   - base bits from sib

d   - modrm direction flag ( 0 == reg->mem, 1 == mem->reg )

M   - mod bits from mod/rm
r   - reg bits from mod/rm
m   - rm bits from mod/rm

w   - 0 == 8 bit oper, 1 == 16/32 oper
s   - 1 sign extend to 16/32 on 8 bit imm

x   - reg1 in an nreg encoding
y   - reg2 in an nreg encoding
z   - reg3 in an nreg encoding

'''

sib = 'SSIIIBBB'
modrm = 'MMrrrmmm'

gpregs32 = (
    ('al','cl','dl','bl','ah','ch','dh','bh'),          # w == 0
    ('eax','ecx','edx','ebx','esp','ebp','esi','edi'),  # w == 1
    ('ax','cx','dx','bx','sp','bp','si','di'),          # 66
)
gpregs16 = (
    ('al','cl','dl','bl','ah','ch','dh','bh'),          # w == 0
    ('ax','cx','dx','bx','sp','bp','si','di'),          # w == 1
    ('eax','ecx','edx','ebx','esp','ebp','esi','edi'),  # 66
)

class i386Prot32Decoder(Decoder):

    def __init__(self, cpu):
        Decoder.__init__(self)
        self.cpu = cpu
        self.symb = cpu.getSymBuilder()

        self.rmregs = ('eax','ecx','edx','ebx','esp','ebp','esi','edi')

        self._initPrefixes()
        self._initIncRegs32()
        self._initIntelTables()

    def reg(self, reg):
        return self.symb.norm(reg)

    def _get_datasize(self, disinfo):
        datasize = disinfo.get('datasize')
        if datasize != None:
            return datasize

        bits = disinfo.get('bits')
        if bits != None and not bits.get('w',1):
            disinfo['datasize'] = 1
            return 1

        # FIXME optimize
        if 0x66 in disinfo.get('prefixes',()):
            disinfo['datasize'] = 2
            return 2

        disinfo['datasize'] = 4
        return 4

    def _initIntelTables(self):
        self.add('00111111',            self._dis_inst,         mnem='aas')
        self.add('000100dw' + modrm,    self._dis_modrm_reg,    mnem='adc')
        self.add('0001010w',            self._dis_eaximm,       mnem='adc')
        self.add('100000sw:MM010mmm',   self._dis_modrm_imm,    mnem='adc')

        self.add('000000dw' + modrm,    self._dis_modrm_reg,    mnem='add')
        self.add('100000sw:MM000mmm',   self._dis_modrm_imm,    mnem='add')
        self.add('0000010w',            self._dis_eaximm,       mnem='add')

        self.add('001000dw' + modrm,    self._dis_modrm_reg,    mnem='and')
        self.add('100000sw:MM100mmm',   self._dis_modrm_imm,    mnem='and')
        self.add('0010010w',            self._dis_eaximm,       mnem='and')

        self.add('01100011' + modrm,    self._dis_modrm_reg,    mnem='arpl', regs=gpregs16)
        self.add('01100010' + modrm,    self._dis_modrm_reg,    mnem='bound', revoper=True)

        self.add('00001111:10111100' + modrm, self._dis_modrm_reg,mnem='bsf', revoper=True)
        self.add('00001111:10111101' + modrm, self._dis_modrm_reg,mnem='bsr', revoper=True)

        self.add('00001111:11001mmm',   self._dis_reg,          mnem='bswap')

        self.add('00001111:10111010:MM100mmm',  self._dis_modrm_imm,    mnem='bt')
        self.add('00001111:10100011' + modrm,   self._dis_modrm_reg,    mnem='bt')

        self.add('00001111:10111010:MM111mmm',  self._dis_modrm_imm,    mnem='btc')
        self.add('00001111:10111011' + modrm,   self._dis_modrm_reg,    mnem='btc')

        self.add('00001111:10111010:MM110mmm',  self._dis_modrm_imm,    mnem='btr')
        self.add('00001111:10110011' + modrm,   self._dis_modrm_reg,    mnem='btr')

        self.add('00001111:10111010:MM101mmm',  self._dis_modrm_imm,    mnem='bts')
        self.add('00001111:10101011' + modrm,   self._dis_modrm_reg,    mnem='bts')

        self.add('11101000',                    self._dis_reloff,       mnem='call')
        self.add('11111111:MM010mmm',           self._dis_modrm,        mnem='call')

        # FIXME callf

        self.add('10011000',   self._dis_none, mnem='cbw')
        self.add('10011001',   self._dis_none, mnem='cdq')
        self.add('11111000',   self._dis_none, mnem='clc')
        self.add('11111100',   self._dis_none, mnem='cld')
        self.add('11111010',   self._dis_none, mnem='cli')

        self.add('00001111:00000110',   self._dis_none,     mnem='clts')

        self.add('11110101',   self._dis_none, mnem='cmc')

        self.add('001110dw:MMrrrmmm', self._dis_modrm_reg,  mnem='cmp')
        self.add('100000sw:MM111mmm', self._dis_modrm_imm,  mnem='cmp')
        self.add('0011110w',          self._dis_eaximm,     mnem='cmp')

    def _dis_none(self, disinfo):
        return self._dis_inst(**disinfo)

    def _dis_reloff(self, disinfo):
        datasize = self._get_datasize(disinfo)
        imm = self._get_imm(disinfo,datasize)
        destaddr = disinfo.get('addr') + disinfo.get('size') + imm
        return self._dis_inst(opers=(self.symb.norm(destaddr),),**disinfo)

    def _dis_reg(self, disinfo):
        bits = disinfo.get('bits')
        reg = self._get_reg(bits['m'],disinfo)
        return self._dis_inst(opers=(reg.state,),**disinfo)

    def _dis_modrm(self, disinfo):
        datasize = self._get_datasize(disinfo)
        rm = self._get_rm(disinfo,datasize)
        return self._dis_inst(opers=(rm.state,), **disinfo)

    def _dis_modrm_imm(self, disinfo):
        datasize = self._get_datasize(disinfo)
        rm = self._get_rm(disinfo,datasize)
        imm = self._get_simm(disinfo,datasize * 8) # FIXME mode
        return self._dis_inst(opers=(rm.state, self.symb.norm(imm)), **disinfo)

    def _get_eax(self, disinfo):
        bits = disinfo.get('bits')
        if bits != None and bits.get('w') == 0:
            return self.symb.var('al')

        # FIXME optimize
        if 0x66 in disinfo.get('prefixes',()):
            return self.symb.var('ax')

        return self.symb.var('eax')

    def _dis_eaximm(self, disinfo):
        a = self._get_eax(disinfo)
        size = a.bits() // 8
        imm = self._get_imm(disinfo,size)
        return self._dis_inst(opers=(a.state, self.symb.norm(imm)), **disinfo)

    def _get_simm(self, disinfo, destbits):
        # retrieve a possibly signed immediate
        bits = disinfo['bits']

         # s but no w == invalid
        if bits.get('s') and not bits.get('w'):
            raise InvalidDecode('i386: s=1 and w=0')

        if bits.get('s'):
            return signext( self._get_imm8(disinfo), 8, destbits )

        if not bits.get('w'):
            return self._get_imm8(disinfo)

        if 0x66 in disinfo.get('prefixes',()):
            return self._get_imm(disinfo, 2)

        return self._get_imm(disinfo, 4)

    def _dis_regimm(self, disinfo):
        # mnem reg,imm
        bits = disinfo['bits']
        reg = self._get_reg(bits['x'],disinfo)

        imm = self._get_simm(disinfo, reg.bits())
        if imm == None:
            # invalid encoding
            return None

        return self._dis_inst(opers=(reg.state, self.symb.norm(imm)), **disinfo)

    def _get_imm(self, disinfo, size):
        cursize = disinfo['size']
        offset = disinfo['offset']
        curoff = cursize + offset
        imm = int.from_bytes(disinfo['bytes'][curoff:curoff+size],byteorder='little')
        disinfo['size'] += size
        return imm

    def _get_imm8(self, disinfo):
        size = disinfo['size']
        offset = disinfo['offset']
        imm = disinfo['bytes'][offset + size]
        disinfo['size'] += 1
        return imm

    def _get_imm32(self, disinfo):
        size = disinfo['size']
        offset = disinfo['offset']
        byteoff = offset + size
        imm = bytes2int(disinfo['bytes'][ byteoff : byteoff + 4 ])
        disinfo['size'] += 4
        return imm

    def _get_rmreg(self, rm, disinfo):
        return self.symb.var( self.rmregs[rm] )

    def _get_rm(self, disinfo, size):
        bits = disinfo['bits']

        rm = bits.get('m')
        mod = bits.get('M')

        size = self.symb.imm( size )

        # FIXME possibly optimize by array access for mod
        # --funroll-loops ( breakout cases for clarity )
        if mod == 0:
            if rm == 4:
                addr = self._get_sib(disinfo)
                return self.symb.mem( addr, size )

            if rm == 5: # [ imm32 ]
                # how do we know how big the mem is?
                addr = self._get_imm32(disinfo)
                return self.symb.mem( addr, size )

            addr = self._get_rmreg(rm,disinfo)
            return self.symb.mem(addr,size)

        if mod == 1: # imm8
            imm = self._get_imm8(disinfo)

            if rm == 4: # sib encoded
                addr = self._get_sib(disinfo)
                return self.symb.mem( addr + imm, size )

            addr = self._get_rmreg(rm,disinfo)
            return self.symb.mem(addr + imm,size)

        if mod == 2: # imm32
            imm = self._get_imm32(disinfo)

            if rm == 4: # sib encoded
                addr = self._get_sib(disinfo)
                return self.symb.mem( addr + imm, size )

            addr = self._get_rmreg(rm,disinfo)
            return self.symb.mem(addr + imm,size)

        if mod == 3: # reg addressing mode
            return self._get_reg(rm,disinfo)
            #return self.symb.mem(addr + imm,size)

    def _dis_modrm_reg(self, disinfo):
        bits = disinfo['bits']

        #d = bits.get('d')   # mod/rm direction flag

        reg = self._get_reg(bits['r'],disinfo)
        rm = self._get_rm(disinfo, reg.bits() // 8) # FIXME datasize

        if bits.get('d',0) or disinfo.get('revoper'):
        #if disinfo.get('memreg'):
            return self._dis_inst(opers=(reg.state,rm.state),**disinfo)

        return self._dis_inst(opers=(rm.state,reg.state),**disinfo)

    def _initPrefixes(self):
        for m,p in i386prefix_masks:
            self.add( m, self._dis_prefix, prefix=p )

    def _initIncRegs32(self):
        # sliced off to clean up inheritance for amd64 ( these are REX )
        incdec = ('eax','ecx','edx','ebx','esp','ebp','esi','edi')
        for i,b in enumerate( iterbytes( range(0x40,0x48) ) ):
            reg = incdec[i]
            mask = bytes2bits(b)
            self.add(mask, self._dis_hardreg, reg=reg, mnem='inc')

        for i,b in enumerate( iterbytes( range(0x48,0x50) ) ):
            mask = bytes2bits(b)
            self.add(mask, self._dis_hardreg, reg=incdec[i], mnem='dec')

    def _get_reg(self, regid, disinfo):
        bits = disinfo['bits']
        regtable = disinfo.get('regs',gpregs32)
        if not bits.get('w',1):
            return self.symb.var(regtable[0][regid])

        # FIXME optimize prefixes
        if 0x66 in disinfo.get('prefixes',()):
            return self.symb.var(regtable[2][regid])

        return self.symb.var(regtable[1][regid])

    def _get_regtable(self, disinfo):
        return disinfo.get('regs',gpregs32)

    def _dis_hardreg(self, disinfo):
        reg = disinfo['reg']
        opers = ( self.symb.norm(reg), )
        return self._dis_inst(opers=opers, **disinfo)

    def _dis_inst(self, **disinfo):
        info = {}

        size = disinfo.get('size')

        prefixes = disinfo.get('prefixes')
        if prefixes != None:
            info['prefixes'] = prefixes
            size += len(prefixes)

        opers = disinfo.get('opers')
        if opers == None:
            opers = ()

        info['size'] = size

        mnem = disinfo.get('mnem')
        return (mnem,opers,info)

    def _dis_prefix(self, disinfo):
        prefix = disinfo.get('prefix')

        prefixes = disinfo.get('prefixes')
        if prefixes == None:
            prefixes = []
            disinfo['prefixes'] = prefixes

        prefixes.append( prefix )
        disinfo['offset'] += 1

        # we must update any disinfo we want to change
        return self.parse(disinfo['bytes'], **disinfo)

