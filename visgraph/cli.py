'''
A package for a basic command interpreter for the graph.
(and graph db...)
'''

import sys
import cmd

import visgraph.graphcore as vg_gcore


class GraphCli(cmd.Cmd):

    def __init__(self, graph=None):
        cmd.Cmd.__init__(self)
        if graph is None:
            graph = vg_gcore.Graph()
        self.graph = graph

    def do_addnode(self, line):
        '''
        Add a node with the given key=value properties on the CLI.
        (the property nid is special and MUST be an integer)
        '''
        return self.graph.addNode()

    def do_quit(self, line):
        '''
        Exit the visgraph cli....
        '''
        raise SystemExit()


def main():
    cli = GraphCli()
    cli.cmdloop()


if __name__ == '__main__':
    sys.exit(main())
