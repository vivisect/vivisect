# Regenerating instruction table and constants
To regenerate the `envi/archs/riscv/const_gen.py` and
`envi/archs/riscv/instr_table.py` files from the latest RISC-V follow these
steps:
1. Clone the RISC-V ISA manual git repo
```
$ git clone https://github.com/riscv/riscv-isa-manual
```
2. In the base vivisect directory run the `envi.archs.riscv.gen` script:
```
$ cd vivisect
$ python -m envi.archs.riscv.gen ../riscv-isa-manual
```
3. After the instructions have been generated they can be explored in python
   like this:
```
$ cd vivisect
$ ipython
In [1]: from envi.archs.riscv.instr_table import instructions

In [2]: print(instructions[0])
Out[2]: RiscVIns(name='LUI', opcode=<RISCV_INS.LUI: 1>, form=<RISCV_FORM.U_TYPE: 5>, cat=('R',), mask=63, value=55, fields=(RiscVField(name='rd', type=<RISCV_FIELD.REG: 1>, shift=6, mask=31, flags=0), RiscVField(name='imm[31:12]', type=<RISCV_FIELD.IMM: 3>, shift=11, mask=1048575, flags=0)), flags=0)
```
