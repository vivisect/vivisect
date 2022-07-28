#!/usr/bin/env python

import sys

import win32api as wapi
import win32con as wcon
import win32security as wsec


PRIV_NAMES = (
    wsec.SE_BACKUP_NAME,
    wsec.SE_DEBUG_NAME,
    wsec.SE_SECURITY_NAME,
)


def enable_privs(remote_server=None, priv_names=PRIV_NAMES):
    priv_ids = sorted(wsec.LookupPrivilegeValue(remote_server, e) for e in priv_names)
    print("Privileges to be enabled IDs:", priv_ids)
    tok = wsec.OpenProcessToken(wapi.GetCurrentProcess(), wcon.TOKEN_ADJUST_PRIVILEGES | wcon.TOKEN_QUERY)
    proc_privs = wsec.GetTokenInformation(tok, wsec.TokenPrivileges)
    print("Existing process privileges:", proc_privs)
    new_proc_privs = []
    need_change = False
    for proc_priv in proc_privs:
        if proc_priv[0] in priv_ids:
            print("Checking privilege " + str(proc_priv[0]))
            if proc_priv[1] != wcon.SE_PRIVILEGE_ENABLED:
                need_change = True
            new_proc_privs.append((proc_priv[0], wcon.SE_PRIVILEGE_ENABLED))
        else:
            new_proc_privs.append(proc_priv)
    print("New process privileges:", new_proc_privs)
    if need_change:
        modif_privs = wsec.AdjustTokenPrivileges(tok, False, new_proc_privs)
        res = wapi.GetLastError()
        print("Changed privileges:", modif_privs)  # Changed ones
        if res != 0:
            print("Error (partial) setting privileges:", res)
    else:
        print("Already set")
    #wsec.GetTokenInformation(tok, wsec.TokenPrivileges)  # To compare with proc_privs
    wapi.CloseHandle(tok)


def main(*argv):
    enable_privs()


if __name__ == "__main__":
    print("Python {:s} {:03d}bit on {:s}\n".format(" ".join(elem.strip() for elem in sys.version.split("\n")),
                                                   64 if sys.maxsize > 0x100000000 else 32, sys.platform))
    rc = main(*sys.argv[1:])
    print("\nDone.")
    sys.exit(rc)
