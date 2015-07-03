import unittest
import vivisect.lib.cmdline as v_cmdline

class CmdLineTest(unittest.TestCase):

    def test_cmdline_quit(self):

        cli = v_cmdline.CmdLine()
        ret = cli.runTestCmd('quit')
        self.assertEqual(ret.strip(),'l8rz!')

    def test_cmdline_partial_ok(self):
        cli = v_cmdline.CmdLine()
        def foo(cli,argv):
            cli.print('foo!')

        cli.addCmd('foo',foo)
        ret = cli.runTestCmd('fo')
        self.assertEqual(ret.strip(),'foo!')

    def test_cmdline_partial_ambig(self):
        cli = v_cmdline.CmdLine()

        def foo(cli,argv):
            cli.print('foo!')

        def faz(cli,argv):
            cli.print('faz!')

        cli.addCmd('foo',foo)
        cli.addCmd('faz',faz)

        ret = cli.runTestCmd('f').strip()
        self.assertTrue(ret.startswith('ambiguous partial command: f'))
