import vivisect.lib.cmdline as v_cmdline

class VdbCmdLine(v_cmdline.CmdLine):

    def __init__(self, dbg):
        v_cmdline.CmdLine.__init__(self)
        self.dbg = dbg
        self.prompt = 'vdb> '

        self.addCmd('ps', self._cli_ps, doc='List processes')
        self.addCmd('attach', self._cli_attach, doc='Attach a trace to a process')
        self.addCmd('status', self._cli_status, doc='Show debugger status')

    def _cli_status(self, cli, argv):

        pid = self.dbg.getDebugInfo('pid')
        host = self.dbg.getDebugInfo('host')
        path = self.dbg.getDebugInfo('path')
        user = self.dbg.getDebugInfo('user')

        arch = self.dbg.getDebugInfo('arch')
        form = self.dbg.getDebugInfo('format')
        plat = self.dbg.getDebugInfo('platform')

        self.print('')
        self.print('Debug Target Info:')
        self.print('')
        self.print('    arch: %s' % (arch,))
        self.print('    plat: %s' % (plat,))
        self.print('    form: %s' % (form,))
        self.print('')
        self.print('    host: %s' % (host,))
        self.print('    path: %s' % (path,))
        self.print('    user: %s' % (user,))
        self.print('')
        #self.print('FIXME PRINT ATTACHED TO')
        self.print('')

    def _cli_ps(self, cli, argv):
        p = self.getCmdArgParser('ps')
        p.add_argument('--glob',default=None,help='Use glob syntax to filter process names')
        opts = p.parse_args(argv)

        for p in self.dbg.getProcessList():
            self.print(p)

    def _cli_attach(self, cli, argv):
        pass

    def _cli_quit(self, cli, argv):
        return v_cmdline.CmdLine._cli_quit(self, cli, argv)

