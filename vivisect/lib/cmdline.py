import io
import cmd
import sys
import shlex
import argparse
import threading

class CmdQuit(Exception):pass   # raised on cmdline "quit"
class CmdRound(Exception):pass  # raised to hook ArgumentParser exit()
class CmdError(Exception):pass  # raised to hook ArgumentParser error()

class CmdArgParser(argparse.ArgumentParser):

    def error(self,msg):
        raise CmdError(msg)

    def exit(self, status=0, message=None):
        raise CmdRound()

class CmdLine(cmd.Cmd):

    '''
    A utilitized cmd.Cmd object updated for extensibility, programatic use,
    and testability.
    '''

    def __init__(self, stdout=sys.stdout):
        cmd.Cmd.__init__(self)
        self._cmd_cmds = {}
        self._cmd_stdout = stdout
        self._cmd_quit = threading.Event()

        self.addCmd('quit', self._cli_quit )

    def _cli_quit(self, cli, argv):
        '''
        Quit the CmdLine interpreter.


        Usage:

            > quit

        '''
        self.print('l8rz!')
        self._cmd_quit.set()
        raise CmdQuit()

    def print(self, msg):
        '''
        Print cmd output for the given Cmdline interface.

        Example:

            cli.print('woot!')

        '''
        print(msg,file=self._cmd_stdout)

    def addCmd(self, name, meth, subsys='all', **info):
        info['meth'] = meth
        info['subsys'] = subsys
        self._cmd_cmds[name] = info

    def getCmdArgParser(self, name):
        doc = self.getCmdInfo(name,'doc')
        return CmdArgParser(prog=name, description=doc)

    def runTestCmd(self, cmdline):
        '''
        Unit test hook to facilitate running commands and receiving their IO.

        Example:

            txt = self.runTestCmd('woot --blah 10')

        '''
        self._cmd_stdout = io.StringIO()
        try:
            self.onecmd(cmdline)
        except CmdQuit as e:
            pass
        self._cmd_stdout.seek(0)
        return self._cmd_stdout.read()

    def getCmdInfo(self, name, prop, defval=None):
        '''
        Retrieve info for the given command ( from addCmd )

        Example:

            

        '''
        info = self._cmd_cmds.get(name)
        if info == None:
            return defval

        return info.get(prop,defval)

    def cmdloop(self):
        while not self._cmd_quit.isSet():
            try:
                cmd.Cmd.cmdloop(self)
            except CmdQuit as e:
                break
            except CmdRound as e:
                pass
            except KeyboardInterrupt as e:
                self.print('caught ctrl-c')
            except Exception as e:
                self.print('error: %s' % (e,))

    def onecmd(self, line):

        if not line:
            self._run_help(self, [])
            return

        parts = shlex.split(line)

        name = parts[0]
        argv = parts[1:]

        meth = self.getCmdInfo(name,'meth')
        if meth == None:
            # is it an unambiguous partial command?
            names = [ n for n in self._cmd_cmds.keys() if n.startswith(name) ]
            if len(names) > 1:
                names.sort()
                self.print('ambiguous partial command: %s' % (name,))
                self.print( ' '.join(names) )
                return

            if len(names) == 1:
                name = names[0]
                meth = self.getCmdInfo(name,'meth')

        if meth == None:
            self.print('unrecognized command: %s' % (name,))
            return

        meth(self,argv)
        return

