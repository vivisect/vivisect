import vivisect.hal.cpu as v_cpu

from vivisect.lib.bits import *
from vivisect.lib.disasm import Decoder

def amd64info():
    return v_cpu.cpuinfo(
        ptrsize=8,

        nop=h2b('90'),
        brk=h2b('cc'),

        regdef=v_cpu.regdef(
            regs=[
                ('rip',64),('rsp',64),('rbp',64),
                ('rax',64), ('rbx',64), ('rcx',64), ('rdx',64), ('rsi',64), ('rdi',64),
            ],
            metas = [
                ('eax','rax',0,32), ('ebx','rbx',0,32), ('ecx','rcx',0,32),
                ('edx','rdx',0,32), ('esi','rsi',0,32), ('edi','rdi',0,32),

                ('ax','rax',0,16), ('bx','rbx',0,16), ('cx','rcx',0,16),
                ('dx','rdx',0,16), ('si','rsi',0,16), ('di','rdi',0,16),
            ],
            aliases = [
                ('_pc','rip'),('_sp','rsp'),
            ],
        )
    )

class Amd64Cpu(v_cpu.Cpu):

    def _init_cpu_info(self):
        return amd64info()

v_cpu.addArchCpu('amd64',Amd64Cpu)
