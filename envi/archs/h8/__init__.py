
"""
Renasas H8 module.
MSB
8-bit
16-bit fixed instruction size (except when EA field, then 32-bit)
"""

import envi


class H8Module(envi.ArchitectureModule):

    def __init__(self, name='h8'):
        envi.ArchitectureModule.__init__(self, name, maxinst=4)
        import envi.archs.h8.disasm as h8_disasm
        self._arch_reg = self.archGetRegCtx()
        self._arch_dis = h8_disasm.H8Disasm()
        self._arch_memreg = {}
        self._arch_memreg.update(memreg_h8s)

    def archGetRegCtx(self):
        import envi.archs.h8.regs as h8_regs
        return h8_regs.H8RegisterContext()

    def archGetBreakInstr(self):
        raise Exception("weird... what are you trying to do here?  h8 has a complex breakpoint instruction")

    def archGetNopInstr(self):
        return b'\x00\x00'

    def getPointerSize(self):
        return 4    # 24 bits encoded in the 3 LSB of 32bit.  addresses must be even

    def pointerString(self, va):
        return "0x%.8x" % va

    def archParseOpcode(self, bytes, offset=0, va=0):
        """
        Parse a sequence of bytes out into an envi.Opcode instance.
        """
        return self._arch_dis.disasm(bytes, offset, va)

    def getEmulator(self):
        import envi.archs.h8.emu as h8_emu
        return h8_emu.H8Emulator()

# https://www.renesas.com/us/en/doc/products/mpumcu/001/rej09b0403_h8s2472_2462hm.pdf?key=69aea339d84b503e86d4d19924e46b8c
# see page 1072 onwards for mem -> reg mappings
memreg_h8s = {  # from rej06b0824_h8sap.pdf (h8s/2400).  uncommented entries from IDA H9S/Advanced
        0xffff84: 'SBYCR',     # Standby Control Register
        0xffff86: 'MSTPCRH',
        0xffff87: 'MSTPCRL',
        0xffff89: 'BRR_1',
        0xffff8a: 'SCR_1',
        0xffff8b: 'TDR_1',
        0xffffa0: 'DADRAH',
        0xffffa1: 'BRR_2',
        0xffffa2: 'SCR_2',
        0xffffa3: 'TDR_2',
        0xffffa4: 'SSR_2',
        0xffffa5: 'RDR_2',
        0xffffa8: 'TCNT_0',    # Timer Counter_0(write)  - 16bits
        0xffffa9: 'TCNT_0_byte1',
        0xffffaa: 'PAODR',     # Port A Output Data Register
        0xffffab: 'PA0DDR',    # Port A Data Direction Register
        0xffffb5: 'P4ODDR',    # Port 4 Data Direction Register
        0xffffb7: 'P4ODR',     # Port 4 Data Register
        0xffffbb: 'P6DR',
        0xffffbe: 'P8DDR',
        0xffffbf: 'P8DR',
        0xffffc0: 'P9DDR',
        0xffffc1: 'P9DR',
        0xffffc2: 'IER',
        0xffffc3: 'STCR',
        0xffffc4: 'SYSCR',     # System Control Register
        0xffffc5: 'MDCR',      # Mode Control Register
        0xffffc6: 'BCR',
        0xffffc7: 'WSCR',
        0xffffd8: 'SMR',
        0xffffd9: 'BRR',
        0xffffda: 'SCR',
        0xffffdb: 'TDR',
        0xffffdc: 'SSR',
        0xffffdd: 'RDR',
}


DTC = 0xffec00

DTC_FIELDS = \
        [['External pins',   'IRQ0', '16', "H'0420", ' DTCEA7'],
         ['External pins',   'IRQ1', '17', "H'0422", ' DTCEA6'],
         ['External pins',   'IRQ2', '18', "H'0424", ' DTCEA5'],
         ['External pins',   'IRQ3', '19', "H'0426", ' DTCEA4'],
         ['A D converter',   'ADI',  '28', "H'0438", ' DTCEA3'],
         ['FRT',             'ICIA', '48', "H'0460", ' DTCEA2'],
         ['FRT',             'ICIB', '49', "H'0462", ' DTCEA1'],
         ['FRT',             'OCIA', '52', "H'0468", ' DTCEA0'],
         ['FRT',             'OCIB', '53', "H'046A", ' DTCEB7'],
         ['TMR_0',           'CMIA0', '64', "H'0480", ' DTCEB2'],
         ['TMR_0',           'CMIB0', '65', "H'0482", ' DTCEB1'],
         ['TMR_1',           'CMIA1', '68', "H'0488", ' DTCEB0'],
         ['TMR_1',           'CMIB1', '69', "H'048A", ' DTCEC7'],
         ['TMR_Y',           'CMIAY', '72', "H'0490", ' DTCEC6'],
         ['TMR_Y',           'CMIBY', '73', "H'0492", ' DTCEC5'],
         ['XBS',             'IBF1', '76', "H'0498", ' DTCEC4'],
         ['XBS',             'IBF2', '77', "H'049A", ' DTCEC3'],
         ['SCI_0',           'RXI0', '81', "H'04A2", ' DTCEC2'],
         ['SCI_0',           'TXI0', '82', "H'04A4", ' DTCEC1'],
         ['SCI_1',           'RXI1', '85', "H'04AA", ' DTCEC0'],
         ['SCI_1',           'TXI1', '86', "H'04AC", ' DTCED7'],
         ['SCI_2',           'RXI2', '89', "H'04B2", ' DTCED6'],
         ['SCI_2',           'TXI2', '90', "H'04B4", ' DTCED5'],
         ['IIC_0',           'IICI0', '92', "H'04B8", ' DTCED4'],
         ['IIC_1',           'IICI1', '94', "H'04BC", ' DTCED3'],
         ['LPC',             'ERRI', '108', "H'04D8", ' DTCEE3'],
         ['LPC',             'IBFI1', '109', "H'04DA", ' DTCEE2'],
         ['LPC',             'IBFI2', '110', "H'04DC", ' DTCEE1'],
         ['LPC',             'IBFI3', '111', "H'04DE", ' DTCEE0'],
         ['Software',        'DTVECR_0', '0', "H'0400", ''],
         ['Software',        'DTVECR_1', '1', "H'0402", ''],
         ['Software',        'DTVECR_2', '2', "H'0404", ''],
         ['Software',        'DTVECR_3', '3', "H'0406", ''],
         ['Software',        'DTVECR_4', '4', "H'0408", ''],
         ['Software',        'DTVECR_5', '5', "H'040a", ''],
         ['Software',        'DTVECR_6', '6', "H'040c", ''],
         ['Software',        'DTVECR_7', '7', "H'040e", ''],
         ['Software',        'DTVECR_8', '8', "H'0410", ''],
         ['Software',        'DTVECR_9', '9', "H'0412", '']]

dtc_h8s = {DTC + int(off[2:], 16): "%s_%s" % (n1.replace(" ", "_"), n2) for n1, n2, num, off, ln in DTC_FIELDS}
