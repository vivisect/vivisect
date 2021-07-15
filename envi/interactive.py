STYPE_NONE = 0
STYPE_IPYTHON = 1
STYPE_CODE_INTERACT = 2

def dbg_interact(lcls, gbls):
    intro = "Let's interact!"
    shelltype = STYPE_NONE
    try:
        import IPython.Shell
        ipsh = IPython.Shell.IPShell(argv=[''], user_ns=lcls, user_global_ns=gbls)
        print(intro)
        shelltype = STYPE_IPYTHON

    except ImportError as e:
        try:
            from IPython.terminal.interactiveshell import TerminalInteractiveShell
            ipsh = TerminalInteractiveShell()
            ipsh.user_global_ns.update(gbls)
            ipsh.user_global_ns.update(lcls)
            ipsh.autocall = 2       # don't require parenthesis around *everything*.  be smart!
            shelltype = STYPE_IPYTHON
            print(intro)

        except ImportError as e:
            try:
                from IPython.frontend.terminal.interactiveshell import TerminalInteractiveShell
                ipsh = TerminalInteractiveShell()
                ipsh.user_global_ns.update(gbls)
                ipsh.user_global_ns.update(lcls)
                ipsh.autocall = 2       # don't require parenthesis around *everything*.  be smart!
                shelltype = STYPE_IPYTHON

                print(intro)
            except ImportError as e:
                print(e)
                shell = code.InteractiveConsole(gbls)
                shelltype = STYPE_IPYTHON
                print(intro)

    if shelltype == STYPE_IPYTHON:
        ipsh.mainloop()

    elif shelltype == STYPE_CODE_INTERACT:
        shell.interact()

    else:
        print("SORRY, NO INTERACTIVE OPTIONS AVAILABLE!!  wtfo?")

