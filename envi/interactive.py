
def dbg_interact(lcls, gbls):
    intro = "Let's interact!"
    try:
        import IPython.Shell
        ipsh = IPython.Shell.IPShell(argv=[''], user_ns=lcls, user_global_ns=gbls)
        print(intro)
        ipsh.mainloop()

    except ImportError as e:
        try:
            from IPython.terminal.interactiveshell import TerminalInteractiveShell
            ipsh = TerminalInteractiveShell()
            ipsh.user_global_ns.update(gbls)
            ipsh.user_global_ns.update(lcls)
            ipsh.autocall = 2       # don't require parenthesis around *everything*.  be smart!
            print(intro)
            ipsh.mainloop()
        except ImportError as e:
            try:
                from IPython.frontend.terminal.interactiveshell import TerminalInteractiveShell
                ipsh = TerminalInteractiveShell()
                ipsh.user_global_ns.update(gbls)
                ipsh.user_global_ns.update(lcls)
                ipsh.autocall = 2       # don't require parenthesis around *everything*.  be smart!

                print(intro)
                ipsh.mainloop()
            except ImportError as e:
                print(e)
                shell = code.InteractiveConsole(gbls)
                print(intro)
                shell.interact()


