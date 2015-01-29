#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/sysctl.h>
#include <errno.h>

#include <mach/mach.h>
#include <mach/mach_vm.h>
#include <mach/vm_prot.h>
//#include <mach/i386/thread_status.h>

#include "exc.h"

#define MACH_MSG_LEN    1024

#if 0

#define MFIELD(WOOT) printf("" #WOOT ": %lu (%ld)\n", (unsigned long)&x.WOOT - (unsigned long)(&x), sizeof(x.WOOT));
int print_sizes() {

    struct extern_proc x = {0};

    printf("void pointer: %lu\n", sizeof(void *));
    printf("x86_thread_state32_t: %lu\n", sizeof(x86_thread_state32_t));
    printf("x86_thread_state64_t: %lu\n", sizeof(x86_thread_state64_t));
    printf("vm_offset_t: %lu\n", sizeof(vm_offset_t));

    printf("kinfo_proc: %lu\n", sizeof(struct kinfo_proc));
    printf("extern_proc: %lu\n", sizeof(struct extern_proc));

    printf("extern_proc.p_pid: %lu\n", (unsigned long)&(x.p_pid) - (unsigned long)&x);

    printf("extern_proc.p_iticks: %lu\n", (unsigned long)&(x.p_iticks) - (unsigned long)&x);

    printf("ipc_space_t: %lu\n", sizeof(ipc_space_t));
    printf("mach_port_name_t: %lu\n", sizeof(mach_port_name_t));
    //printf("mach_port_poly_t: %lu\n", sizeof(mach_port_poly_t));
    printf("mach_msg_type_name_t: %lu\n", sizeof(mach_msg_type_name_t));

    printf("mach_port_t: %.lu\n", sizeof(mach_port_t));
    printf("mach_port_name_t: %.lu\n", sizeof(mach_port_name_t));
    printf("mach_msg_size_t: %.lu\n", sizeof(mach_msg_size_t));
    printf("mach_msg_bits_t: %.lu\n", sizeof(mach_msg_bits_t));
    printf("mach_msg_id_t: %.lu\n", sizeof(mach_msg_id_t));

    printf("kern_return_t: %.lu\n", sizeof(kern_return_t));

        MFIELD(p_un);
        MFIELD(p_vmspace);
        MFIELD(p_sigacts);
        MFIELD(p_flag);
        MFIELD(p_stat);
        MFIELD(p_pid);
        MFIELD(p_oppid);
        MFIELD(p_dupfd);
        MFIELD(user_stack);
        MFIELD(exit_thread);
        MFIELD(p_debugger);
        MFIELD(sigwait);
        MFIELD(p_estcpu);
        MFIELD(p_cpticks);
        MFIELD(p_pctcpu);
        MFIELD(p_wchan);
        MFIELD(p_wmesg);
        MFIELD(p_swtime);
        MFIELD(p_slptime);
        MFIELD(p_realtimer);
        MFIELD(p_rtime);
        MFIELD(p_uticks);
        MFIELD(p_sticks);
        MFIELD(p_iticks);
        MFIELD(p_traceflag);
        MFIELD(p_tracep);
        MFIELD(p_siglist);
        MFIELD(p_textvp);
        MFIELD(p_holdcnt);
        MFIELD(p_sigmask);
        MFIELD(p_sigignore);
        MFIELD(p_sigcatch);
        MFIELD(p_priority);
        MFIELD(p_usrpri);
        MFIELD(p_nice);
        MFIELD(p_comm);
        MFIELD(p_pgrp);
        MFIELD(p_addr);
        MFIELD(p_xstat);
        MFIELD(p_acflag);
        MFIELD(p_ru);

    return(0);
}

int main(int argc, char **argv) {
    return print_sizes();
}

#endif

struct myinfo {
    unsigned int pid;
    char pname[MAXCOMLEN+1];
};

struct myinfo * platformPs(void) {

    int i = 0;
    size_t bsize = 0;
    unsigned int count = 0;
    struct myinfo *myinfos = NULL;
    struct kinfo_proc *kinfos = NULL;
    int sctl[3] = { CTL_KERN, KERN_PROC, KERN_PROC_ALL };

    if (sysctl( sctl, 3, NULL, &bsize, NULL, 0) != 0) {
        perror("sysctl for size failed:");
        return NULL;
    }

    //printf("got size: %lu\n", bsize);
    count = bsize / sizeof(struct kinfo_proc);

    kinfos = calloc(1, bsize);
    myinfos = calloc(count + 1, sizeof(struct myinfo));

    if (sysctl( sctl, 3, kinfos, &bsize, NULL, 0) != 0) {
        perror("sysctl for kinfo failed:");
        free(kinfos);
        free(myinfos);
        return NULL;
    }

    count = bsize / sizeof(struct kinfo_proc);

    for (i = 0; i < count; i++) {
        myinfos[i].pid = kinfos[i].kp_proc.p_pid;
        memcpy(myinfos[i].pname, kinfos[i].kp_proc.p_comm, MAXCOMLEN);
        //printf("%d %s\n", myinfos[i].pid, myinfos[i].pname);
    }

    myinfos[count].pid = 0xffffffff;

    return myinfos;
}

int is_pid_classic (pid_t pid) {
  int mib[3] = { CTL_KERN, KERN_CLASSIC, pid };
  size_t len = sizeof (int);
  int ret = 0;
  if (sysctl (mib, 3, &ret, &len, NULL, 0) == -1)
    return -1;
  return ret;
}

static int hlpmaskexc = 0;

kern_return_t   vtrace_catch_exception_raise
                (mach_port_t                          exception_port,
                 mach_port_t                                  thread,
                 mach_port_t                                    task,
                 exception_type_t                          exception,
                 exception_data_t                               code,
                 mach_msg_type_number_t                   code_count) {

    printf("catch_exception_raise! (%d) \n", hlpmaskexc);

    if ( hlpmaskexc ) {
        return KERN_SUCCESS;
    }

    return KERN_FAILURE;
}

kern_return_t   vtrace_catch_exception_raise_state
                (mach_port_t                          exception_port,
                 exception_type_t                          exception,
                 exception_data_t                               code,
                 mach_msg_type_number_t                   code_count,
                 int *                                        flavor,
                 thread_state_t                             in_state,
                 mach_msg_type_number_t               in_state_count,
                 thread_state_t                            out_state,
                 mach_msg_type_number_t *            out_state_count) {
    printf("catch_exception_raise_state!\n");
    return KERN_FAILURE;
}

kern_return_t   vtrace_catch_exception_raise_state_identity
                (mach_port_t                          exception_port,
                 mach_port_t                                  thread,
                 mach_port_t                                    task,
                 exception_type_t                          exception,
                 exception_data_t                               code,
                 mach_msg_type_number_t                   code_count,
                 int *                                        flavor,
                 thread_state_t                             in_state,
                 mach_msg_type_number_t               in_state_count,
                 thread_state_t                            out_state,
                 mach_msg_type_number_t *            out_state_count) {
    printf("catch_exception_raise_state_identity!\n");
    return KERN_FAILURE;
}

typedef union mach_msg {
    mach_msg_header_t hdr;
    char data[MACH_MSG_LEN];
} mach_msg_t;

extern boolean_t exc_server( mach_msg_header_t *inmsg, mach_msg_header_t *outmsg);

kern_return_t vtrace_exc_server( mach_msg_header_t *inmsg, mach_msg_header_t *outmsg, int maskexc) {
    hlpmaskexc = maskexc; 
    return exc_server(inmsg, outmsg);
}

#ifdef NEWP


typedef struct darwin_dbgctx {
    mach_port_t dbgtask;
    mach_port_t task;
    mach_port_name_t portset;
    mach_port_name_t excport;
    mach_msg_t *msgin;
    mach_msg_t *msgout;
} darwin_dbgctx_t;

typedef struct darwin_dbgevt {
    mach_port_t thread;
    uint32_t    sigcode;
    uint32_t    exitcode;
} darwin_dbgevt_t;

struct memory_map {
    u_int64_t address;
    u_int64_t size;
    u_int32_t perms;
};

#define VT_READ 4
#define VT_WRIT 2
#define VT_EXEC 1

#define OKORGTFO(status, msg) if (status != KERN_SUCCESS) { printf(msg ": %s\n", mach_error_string(status)); goto statusexit; }

kern_return_t darwinWait(darwin_dbgctx_t *dbgctx, darwin_dbgevt_t *evt) {

    kern_return_t status = MACH_RCV_INTERRUPTED;
    mach_msg_header_t *hdr = &(dbgctx->msgin->hdr);

    while (status == MACH_RCV_INTERRUPTED) {

        status = mach_msg( dbgctx->msgin, MACH_RCV_MSG | MACH_RCV_INTERRUPT, 0,
                           MACH_MSG_LEN, dbgctx->portset, 0, MACH_PORT_NULL);

    }
    OKORGTFO(status, "mach_msg failed");

    /* Once here, we have a real exception... */
    if (hdr->msgh_local_port == dbgctx->excport) {

        /* Use their crazy exc_server method to formulate a response */
        if (! exc_server(dbgctx->msgin, dbgctx->msgout)) {
            printf("exc_server failed!\n");
            status = -1; //FIXME
            goto statusexit;
        }

    } else {

        printf("got mach_msg from unknown port: %d\n", hdr->msgh_local_port);
        status = -1;
        goto statusexit;

    }


  statusexit:
    if (status != KERN_SUCCESS) {
        //FIXME free failure resources
    }
    return status;

}

kern_return_t darwinContinue(darwin_dbgctx_t *dbgctx, int signal) {
}

kern_return_t initDebugContext(darwin_dbgctx_t *dbgctx, int pid) {

    kern_return_t status = 0;

    dbgctx->dbgtask = mach_task_self();

    /* Find the task from the specified PID */
    status = task_for_pid(dbgctx->dbgtask, pid, &(dbgctx->task));
    OKORGTFO(status, "task_for_pid failed");

    /* Initialize the portset we use for multi-event stuff */
    status = mach_port_allocate(dbgctx->dbgtask, MACH_PORT_RIGHT_PORT_SET, &(dbgctx->portset));
    OKORGTFO(status, "mach_port_allocate (set) failed");

    /* Allocate a new port for read/write (used for exception events) */
    status = mach_port_allocate(dbgctx->dbgtask, MACH_PORT_RIGHT_RECEIVE, &(dbgctx->excport));
    OKORGTFO(status, "mach_port_allocate (recv) failed");

    /* Since it was allocated with RECV, lets add SEND */
    status = mach_port_insert_right(dbgctx->dbgtask, dbgctx->excport,
                                    dbgctx->excport, MACH_MSG_TYPE_MAKE_SEND);
    OKORGTFO(status, "mach_port_insert_right failed");

    /* Now lets add the exception port to our port set */
    status = mach_port_move_member(dbgctx->dbgtask, dbgctx->excport, dbgctx->portset);
    OKORGTFO(status, "mach_port_move_member failed");

    /* Now that we have an exception port, lets set it for the target task */
    status = task_set_exception_ports(dbgctx->task, EXC_MASK_ALL, dbgctx->excport,
                                      EXCEPTION_DEFAULT, THREAD_STATE_NONE);
    OKORGTFO(status, "task_set_exception_ports failed");

    /* Initialize our mach messages */
    dbgctx->msgin = calloc(1, sizeof(mach_msg_t));
    dbgctx->msgout = calloc(1, sizeof(mach_msg_t));

  statusexit:
    if (status != KERN_SUCCESS) {
        // FREE ALL THE PORTS/HANDLES
    }
    return status;
}

kern_return_t finiDebugContext(darwin_dbgctx_t *dbgctx) {
}

struct memory_map *platformGetMaps(vm_map_t task) {

    mach_port_t port = 0;
    unsigned int perms = 0;
    kern_return_t status = 0;
    mach_vm_size_t mapsize = 0;
    mach_vm_address_t mapva = 0;
    mach_msg_type_number_t count = 0;
    struct vm_region_basic_info_64 binfo = {0};

    count = sizeof(struct vm_region_basic_info_64) / sizeof(natural_t);

    status = mach_vm_region(task, &mapva, &mapsize, VM_REGION_BASIC_INFO_64, &binfo, &count, &port);
    while (status == 0) {
        printf("%p %d %d\n", mapva, mapsize, binfo.reserved);
        mapva += mapsize;

        if (binfo.protection & VM_PROT_READ) perms |= VT_READ;
        if (binfo.protection & VM_PROT_WRITE) perms |= VT_WRIT;
        if (binfo.protection & VM_PROT_EXECUTE) perms |= VT_EXEC;

        break;

    }
    mach_error("omg", status);
    printf("status: %d\n", status);
    return NULL;
}

#endif

