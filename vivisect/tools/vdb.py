import sys
import argparse

import vivisect.lib.cmdline as v_cmdline
import vivisect.debug.debugger as v_debugger

class VdbCmdLine(v_cmdline.CmdLine):

    def __init__(self, dbg):
        self._cmd_dbg = dbg
        v_cmdline.CmdLine.__init__(self)
        self.prompt = 'vdb> '

        self.addCmd('ps', self._run_ps, doc='Display a list of processes and properties' )
        self.addCmd('info', self._run_info, doc='Show basic info about the debug target')

    def _cli_info(self, cli, argv):
        p = self.getCmdArgParser('info')

        pid = self._cmd_dbg.getDebugInfo('pid')
        host = self._cmd_dbg.getDebugInfo('host')
        path = self._cmd_dbg.getDebugInfo('path')
        user = self._cmd_dbg.getDebugInfo('user')

        self.print('')
        self.print('Debug Target Info:')
        self.print('    Pid: %d' % (pid,))
        self.print('   Host: %s' % (host,))
        self.print('   Path: %s' % (path,))
        self.print('   User: %s' % (user,))

        self._cmd_dbg.showDebugInfo(print=self.print)

    def _cli_ps(self, cli, argv):
        p = self.getCmdArgParser('ps')
        p.add_argument('--glob',default=None,help='Use glob syntax to filter process names')
        opts = p.parse_args(argv)

        for p in self._cmd_dbg.getProcessList():
            print(p)

def main(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument('--target',default='this://',help='debug target url')

    opts = parser.parse_args(argv)

    dbg = v_debugger.getDebugger()

    cli = dbg.getDebugCli()
    cli.cmdloop()

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

