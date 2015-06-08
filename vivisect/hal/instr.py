import vivisect.lib.bits as v_bits

class Instr:
    '''
    Vivisect HAL Instruction base class.
    '''
    def __init__(self, cpu, inst):
        self.cpu = cpu
        self.inst = inst

    def __str__(self):
        return self.text()

    def __repr__(self):
        addr = self.inst[2].get('addr')
        return '0x%.8x: %s  %s' % (addr,self.hex().ljust(16),str(self))

    def mnem(self):
        '''
        Return the mnemonic for the instruction.

        Example:
            if inst.mnem() == 'foo':
                dostuff()
        '''
        return self.inst[0]

    def size(self):
        '''
        Return the size of the instruction in bytes.

        Example:
            x = inst.size()
        '''
        return self.inst[2].get('size')

    def hex(self):
        '''
        Return a hex string of the instruction bytes.

        Example:
            print( inst.hex() )
        '''
        bytez = self.inst[2].get('bytes')
        offset = self.inst[2].get('offset')
        return v_bits.b2h( bytez[offset:offset+self.size()] )

    def text(self):
        '''
        Return a simple text representation for the instruction.

        Example:
            print( inst.text() )
        '''
        ret = self.mnem()
        symb = self.cpu.symb
        opers = [ str(symb.wrap(o)) for o in self.inst[1] ]
        if opers:
            ret += ' ' + ','.join(opers)
        return ret

    #def html(self):
    #def title(self):

    def getRefs(self):
        '''
        Return a list of (addr,reftype,addr,info) tuples for refs from here.

        Example:

            for ref in inst.getRefs():
                print('ref to: 0x%.8x' % (ref[2],))

        '''
        return self._getRefs()

    #def coderefs(self):
    #def datarefs(self):

