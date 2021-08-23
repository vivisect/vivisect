# calling convention constants
CC_REG              = 1 << 0    # argument is stored in a register
CC_STACK            = 1 << 1    # argument is stored on the stack
CC_STACK_INF        = 1 << 2    # all following args are stored on the stack
CC_CALLEE_CLEANUP   = 1 << 3    # callee cleans up the stack
CC_CALLER_CLEANUP   = 1 << 4    # caller cleans up the stack

# meta-register constants
RMETA_MASK  = 0xffff0000
RMETA_NMASK = 0x0000ffff

ENDIAN_LSB = 0
ENDIAN_MSB = 1

# Memory Map Permission Flags
MM_NONE = 0x0
MM_READ = 0x4
MM_WRITE = 0x2
MM_EXEC = 0x1
MM_SHARED = 0x08

MM_READ_WRITE = MM_READ | MM_WRITE
MM_READ_EXEC = MM_READ | MM_EXEC
MM_RWX = MM_READ | MM_WRITE | MM_EXEC

pnames = [
        'No Access', 
        'Execute', 
        'Write', 
        'Write/Exec', 
        'Read', 
        'Read/Exec', 
        'Read/Write',
        'RWE',
        ]
# create "shared" versions to pnames
for idx in range(8):
    pnames.append('Shared: ' + pnames[idx])


PAGE_SIZE = 1 << 12
PAGE_NMASK = PAGE_SIZE - 1
PAGE_MASK = ~PAGE_NMASK

