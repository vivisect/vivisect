import vivisect.hal.cpu as v_cpu

from vivisect.lib.bits import *

from vivisect.archs.i386.disasm import i386Prot32Decoder

def i386info():
    return v_cpu.cpuinfo(
        ptrsize=4,

        nop=h2b('90'),
        brk=h2b('cc'),
        regdef=v_cpu.regdef(
            regs = [
                ('eax',32),('ecx',32),('edx',32),('ebx',32),('esp',32),('ebp',32),('esi',32),('edi',32), # general regs
                ('mm0',64),('mm1',64), ('mm2',64), ('mm3',64), ('mm4',64), ('mm5',64), ('mm6',64), ('mm7',64), # 
                ('xmm0',128),('xmm1',128),('xmm2',128),('xmm3',128),('xmm4',128),('xmm5',128),('xmm6',128),('xmm7',128), # simd regs
                ('debug0',32),('debug1',32),('debug2',32),('debug3',32),('debug4',32),('debug5',32),('debug6',32),('debug7',32), # debug regs
                ('ctrl0',32),('ctrl1',32),('ctrl2',32),('ctrl3',32),('ctrl4',32),('ctrl5',32),('ctrl6',32),('ctrl7',32), # control regs
                ('test0', 32),('test1', 32),('test2', 32),('test3', 32),('test4', 32),('test5', 32),('test6', 32),('test7', 32), # test regs
                ('es', 16),('cs',16),('ss',16),('ds',16),('fs',16),('gs',16), # segment selectors

                # mock up segment selectors
                ('esbase',32),('csbase',32),('ssbase',32),('dsbase',32),('fsbase',32),('gsbase',32),
                ('essize',32),('cssize',32),('sssize',32),('dssize',32),('fssize',32),('gssize',32),

                ('st0', 128),('st1', 128),('st2', 128),('st3', 128),('st4', 128),('st5', 128),('st6', 128),('st7', 128), # fpu regs
                ('eflags', 32), ('eip', 32),
            ],
            metas = [
                ('ax', 'eax', 0, 16), ('bx', 'ebx', 0, 16), ('cx', 'ecx', 0, 16), ('dx', 'edx', 0, 16),
                ('sp', 'esp', 0, 16), ('bp', 'ebp', 0, 16), ('si', 'esi', 0, 16), ('di', 'edi', 0, 16),
                ('al', 'eax', 0, 8), ('bl', 'ebx', 0, 8), ('cl', 'ecx', 0, 8), ('dl', 'edx', 0, 8),
                ('ah', 'eax', 8, 8), ('bh', 'ebx', 8, 8), ('ch', 'ecx', 8, 8), ('dh', 'edx', 8, 8),
            ],
            aliases = [
                ('_pc','eip'),('_sp','esp'),
            ],
        ),
    )

class I386Cpu(v_cpu.Cpu):

    def _init_cpu_info(self):
        return i386info()

    def _init_cpu_decoder(self):
        return i386Prot32Decoder(self)

    #def _slot_setmode(self, evt, evtinfo):
        #pass

        #mode = evtinfo['valu']
        #self.decoder = self.decoders.get(mode)

    #def getSymEffects(self, inst):
        #mnem = inst[2].get('mnem')
        #if mnem == None:
            #mnem = inst[0]

        #symb = self.getSymBuilder()
        #opers = [ symb.wrap(o) for o in inst[1] ]
        #return getattr(self,'_inst_%s' % mnem)(inst,symb,opers)

    #def _inst_inc(self, inst, symb, opers):
        #symb[ opers[0] ] = opers[0] + 1
        #return sym.effects

v_cpu.addArchCpu('i386',I386Cpu)

