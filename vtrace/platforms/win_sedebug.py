#!/usr/bin/env python

import sys

import win32api as wapi
import win32con as wcon
import win32security as wsec

import logging
logger = logging.getLogger(__name__)


PRIV_NAMES = (
    wsec.SE_BACKUP_NAME,
    wsec.SE_DEBUG_NAME,
    wsec.SE_SECURITY_NAME,
)


def enable_privs(remote_server=None, priv_names=PRIV_NAMES):
    priv_ids = sorted(wsec.LookupPrivilegeValue(remote_server, e) for e in priv_names)
    logger.debug("Privileges to be enabled IDs:")
    for privnum in priv_ids:
        logger.debug("\t%s (%d)", wsec.LookupPrivilegeName(None, privnum), privnum)
        
    tok = wsec.OpenProcessToken(wapi.GetCurrentProcess(), wcon.TOKEN_ADJUST_PRIVILEGES | wcon.TOKEN_QUERY)
    proc_privs = wsec.GetTokenInformation(tok, wsec.TokenPrivileges)
    logger.debug("Existing process privileges:")
    prev_privs = {}
    for privnum, privval in proc_privs:
        prev_privs[privnum] = privval
        logger.debug("\t%s (%d): %r", wsec.LookupPrivilegeName(None, privnum), privnum, privval)
        
    new_proc_privs = []
    need_change = False
    for proc_priv in proc_privs:
        if proc_priv[0] in priv_ids:
            logger.debug("Checking privilege %s (%d)", wsec.LookupPrivilegeName(None, proc_priv[0]), proc_priv[0])
            if proc_priv[1] != wcon.SE_PRIVILEGE_ENABLED:
                need_change = True
            new_proc_privs.append((proc_priv[0], wcon.SE_PRIVILEGE_ENABLED))
        else:
            new_proc_privs.append(proc_priv)
    logger.debug("New process privileges:")
    for privnum, privval in new_proc_privs:
        logger.debug("\t%s (%d): %r", wsec.LookupPrivilegeName(None, privnum), privnum, privval)
        
    if need_change:
        modif_privs = wsec.AdjustTokenPrivileges(tok, False, new_proc_privs)
        res = wapi.GetLastError()
        logger.debug("Changed privileges:") # Changed ones
        for privnum, privval in modif_privs:
            prev_priv = prev_privs.get(privnum)
            logger.debug("\t%s (%d): %r -> %r", wsec.LookupPrivilegeName(None, privnum), privnum, privval, prev_priv)
        
        if res != 0:
            logger.warning("Error (partial) setting privileges: %r", res)
    else:
        logger.debug("Already set")
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
