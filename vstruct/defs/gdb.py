import vstruct
from vstruct.primitives import *

class Fstat(vstruct.VStruct):
    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self)
        self.st_dev        = v_uint32(bigend=bigend)
        self.st_ino        = v_uint32(bigend=bigend)
        self.st_mode       = v_uint32(bigend=bigend)
        self.st_nlink      = v_uint32(bigend=bigend)
        self.st_uid        = v_uint32(bigend=bigend)
        self.st_gid        = v_uint32(bigend=bigend)
        self.st_tdev       = v_uint32(bigend=bigend)
        self.st_size       = v_uint64(bigend=bigend)
        self.st_blksize    = v_uint64(bigend=bigend)
        self.st_blocks     = v_uint64(bigend=bigend)
        self.st_atime      = v_uint32(bigend=bigend)
        self.st_mtime      = v_uint32(bigend=bigend)
        self.st_ctime      = v_uint32(bigend=bigend)

'''
struct stat {
    unsigned int  st_dev;      /* device */
    unsigned int  st_ino;      /* inode */
    mode_t        st_mode;     /* protection */
    unsigned int  st_nlink;    /* number of hard links */
    unsigned int  st_uid;      /* user ID of owner */
    unsigned int  st_gid;      /* group ID of owner */
    unsigned int  st_rdev;     /* device type (if inode device) */
    unsigned long st_size;     /* total size, in bytes */
    unsigned long st_blksize;  /* blocksize for filesystem I/O */
    unsigned long st_blocks;   /* number of blocks allocated */
    time_t        st_atime;    /* time of last access */
    time_t        st_mtime;    /* time of last modification */
    time_t        st_ctime;    /* time of last change */
    '''
