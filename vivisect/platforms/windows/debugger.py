
import vivisect.debug.cmdline as v_cmdline
import vivisect.debug.debugger as v_debugger
import vivisect.platforms.windows.trace as v_win_trace

class WinVdbCmdLine(v_cmdline.VdbCmdLine):

    def _cli_status(self, cli, argv):
        v_cmdline.VdbCmdLine._cli_status(self,cli,argv)

        version = self.dbg.getDebugInfo('windows:version')
        seDebugPriv = self.dbg.getDebugInfo('windows:seDebugPrivilege')

        self.print('Windows Target:')
        self.print('')
        self.print('             version: %r' % (version,))
        self.print('    seDebugPrivilege: %s' % (seDebugPriv,))
        self.print('')

class WindowsDebugger(v_debugger.Debugger):

    def _dbg_getDebugCli(self):
        return WinVdbCmdLine(self)

    def _initTrace(self, proc):
        arch = proc[1].get('arch')

        # FIXME syswow64 goes here!

        if arch == 'i386':
            return v_win_trace.I386WinTrace(proc,self)

        if arch == 'amd64':
            return v_win_trace.Amd64WinTrace(proc,self)

        raise Exception('No Trace Class: %s' % (arch,))
